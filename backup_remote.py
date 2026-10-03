"""Save deployment code and a pinned llama.cpp source archive; never save password."""
import argparse,base64,getpass,hashlib,json,pathlib,posixpath,sys,time,paramiko
sys.stdout.reconfigure(encoding='utf-8')
p=argparse.ArgumentParser()
p.add_argument('--host',default='connect.westd.seetacloud.com')
p.add_argument('--port',type=int,default=32204)
p.add_argument('--user',default='root')
p.add_argument('--fingerprint',default='y2DhrdHAWfTCoY9uLz0ve3EzTKYtWNBBWm80QUTOkXg')
p.add_argument('--output',default='deployment/snapshot-20261003')
a=p.parse_args();root=pathlib.Path(a.output);root.mkdir(parents=True,exist_ok=True)
class Pin(paramiko.MissingHostKeyPolicy):
    def missing_host_key(self,client,hostname,key):
        actual=base64.b64encode(hashlib.sha256(key.asbytes()).digest()).decode().rstrip('=')
        if actual!=a.fingerprint.removeprefix('SHA256:'): raise paramiko.SSHException('Unexpected host key: SHA256:'+actual)
s=paramiko.SSHClient();s.set_missing_host_key_policy(Pin())
s.connect(a.host,port=a.port,username=a.user,password=getpass.getpass('SSH password: '),timeout=25)
s.get_transport().set_keepalive(30)
def command(cmd):
    _,o,e=s.exec_command(cmd,timeout=600);data=o.read();err=e.read().decode('utf-8','replace');code=o.channel.recv_exit_status()
    if code: raise RuntimeError(f'Command failed ({code}): {err}')
    return data
metadata={'host':a.host,'port':a.port,'fingerprint':'SHA256:'+a.fingerprint,'captured_at':time.strftime('%Y-%m-%dT%H:%M:%S%z'),'files':[]}
try:
    rev=command('git -C /root/autodl-tmp/llama.cpp rev-parse HEAD').decode().strip();metadata['llama_cpp_commit']=rev
    status=command('git -C /root/autodl-tmp/llama.cpp status --porcelain').decode()
    if status.strip(): raise RuntimeError('llama.cpp has uncommitted changes; save them before archiving')
    command('git -C /root/autodl-tmp/llama.cpp archive --format=tar.gz -o /root/autodl-tmp/llama-source-audit.tar.gz HEAD')
    client=s.open_sftp()
    names=['run_server_coletti.sh','run_server_novel.sh','run_server_coletti.sh.before-20261003','start-qwen-service.sh','build_coletti.sh','setup_coletti.sh','dl_coletti.sh','llm-idle-shutdown.sh','llm-idle-start.sh','llm-idle-watchdog.sh','monitor_coletti.py','run_monitor_coletti.sh','setup_nginx_monitor.sh','nginx_coletti.conf','info2.sh','server-audit-20261003.log','server-novel.log','server_coletti.log','idle_shutdown.log','build_coletti.log','llama-source-audit.tar.gz']
    for name in names:
        src=posixpath.join('/root/autodl-tmp',name);dest=root/name
        try: client.get(src,str(dest))
        except FileNotFoundError: metadata.setdefault('missing_files',[]).append(name);continue
        metadata['files'].append({'path':name,'size':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
        print('SAVED',name,dest.stat().st_size,flush=True)
    commands={
      'environment.txt':"uname -a; cat /etc/os-release; nvidia-smi --query-gpu=name,memory.total,memory.used --format=csv; cmake --version; gcc --version; /usr/local/cuda-12.1/bin/nvcc --version; cat /sys/fs/cgroup/memory.max 2>/dev/null; cat /sys/fs/cgroup/memory/memory.limit_in_bytes 2>/dev/null; df -h /root/autodl-tmp; ps -eo pid,args | grep '[l]lama-server'; true",
      'cmake-options.txt':"grep -E '^(CMAKE_BUILD_TYPE|CMAKE_CUDA_ARCHITECTURES|GGML_CUDA|CMAKE_CUDA_COMPILER|CMAKE_CXX_COMPILER|LLAMA_)' /root/autodl-tmp/llama.cpp/build/CMakeCache.txt",
      'model-sha256.txt':"sha256sum /root/autodl-tmp/models/Qwen3.8-27B-Uncensored-Q8_0.gguf /root/autodl-tmp/models/mmproj-Qwen3.8-27B-Uncensored-F16.gguf",
      'models.json':"curl -fsS http://127.0.0.1:8081/v1/models",
      'props.json':"curl -fsS http://127.0.0.1:8081/props"
    }
    for name,cmd in commands.items():
        print('CAPTURING',name,flush=True);dest=root/name;dest.write_bytes(command(cmd));metadata['files'].append({'path':name,'size':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
    (root/'manifest.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
    print('BACKUP COMPLETE',root.resolve(),flush=True)
finally: s.close()
