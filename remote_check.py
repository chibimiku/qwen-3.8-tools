import paramiko, getpass, sys, json
s=paramiko.SSHClient()
s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
s.connect('connect.westd.seetacloud.com',port=32204,username='root',password=getpass.getpass('SSH password: '),timeout=25)
print('CONNECTED hostkey SHA256 available',s.get_transport().get_remote_server_key().get_name(),flush=True)
for line in sys.stdin:
    try:
        cmd=json.loads(line)
        i,o,e=s.exec_command(cmd,timeout=600)
        print(o.read().decode('utf-8','replace'),flush=True)
        print(e.read().decode('utf-8','replace'),flush=True)
        print('END_COMMAND',flush=True)
    except Exception as ex: print(type(ex).__name__,str(ex),flush=True)
