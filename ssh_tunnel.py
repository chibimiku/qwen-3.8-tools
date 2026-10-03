"""Local-only SSH tunnel. Password is prompted and never saved."""
import argparse, getpass, hashlib, base64, socketserver, select, paramiko
p=argparse.ArgumentParser()
p.add_argument('--host',default='connect.westd.seetacloud.com')
p.add_argument('--port',type=int,default=32204)
p.add_argument('--user',default='root')
p.add_argument('--local-port',type=int,default=18081)
p.add_argument('--remote-port',type=int,default=8081)
p.add_argument('--fingerprint',default='y2DhrdHAWfTCoY9uLz0ve3EzTKYtWNBBWm80QUTOkXg')
a=p.parse_args()
s=paramiko.SSHClient()
class PinnedHostKey(paramiko.MissingHostKeyPolicy):
    def missing_host_key(self,client,hostname,key):
        actual=base64.b64encode(hashlib.sha256(key.asbytes()).digest()).decode().rstrip('=')
        if actual!=a.fingerprint.removeprefix('SHA256:'):
            raise paramiko.SSHException('Host key differs from expected fingerprint: SHA256:'+actual)
s.set_missing_host_key_policy(PinnedHostKey())
s.connect(a.host,port=a.port,username=a.user,password=getpass.getpass('SSH password: '),timeout=25)
t=s.get_transport(); t.set_keepalive(30)
key=t.get_remote_server_key()
print('Host key SHA256:'+base64.b64encode(hashlib.sha256(key.asbytes()).digest()).decode().rstrip('='),flush=True)
class Forward(socketserver.BaseRequestHandler):
    def handle(self):
        ch=t.open_channel('direct-tcpip',('127.0.0.1',a.remote_port),self.request.getpeername())
        try:
            while True:
                ready,_,_=select.select([self.request,ch],[],[],30)
                for source in ready:
                    data=source.recv(65536)
                    if not data: return
                    (ch if source is self.request else self.request).sendall(data)
        finally: ch.close()
class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address=True
    daemon_threads=True
print(f'TUNNEL READY 127.0.0.1:{a.local_port} -> 127.0.0.1:{a.remote_port}',flush=True)
try:
    with Server(('127.0.0.1',a.local_port),Forward) as server: server.serve_forever()
finally: s.close()
