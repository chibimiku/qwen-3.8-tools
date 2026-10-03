import os,pathlib,json,urllib.request,sys
sys.stdout.reconfigure(encoding='utf-8')
path=pathlib.Path(os.environ['APPDATA'])/'xyz.chatboxapp.app'/'config.json'
settings=json.loads(path.read_text(encoding='utf-8'))['settings']
p=settings['providers']['custom-provider-qwen-seetacloud-local']
model=settings['defaultChatModel']['model']
body={'model':model,'messages':[{'role':'user','content':'请只回复：连接成功'}],'max_tokens':32,'stream':True}
req=urllib.request.Request(p['apiHost'].rstrip('/')+p['apiPath'],data=json.dumps(body,ensure_ascii=False).encode(),headers={'Content-Type':'application/json','Authorization':'Bearer '+p['apiKey']})
content=''
with urllib.request.urlopen(req,timeout=120) as response:
    for line in response:
        line=line.decode('utf-8').strip()
        if not line.startswith('data: ') or line=='data: [DONE]': continue
        obj=json.loads(line[6:])
        for choice in obj.get('choices',[]): content+=choice.get('delta',{}).get('content') or ''
assert '连接成功' in content,content
print('CONFIGURED ENDPOINT:',p['apiHost']+p['apiPath'])
print('MODEL:',model)
print('STREAM REPLY:',content)
