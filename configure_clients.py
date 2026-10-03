"""Back up and add only the user's Qwen connection and tunnel."""
import pathlib,json,datetime,shutil,re,os
stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
app=pathlib.Path(os.environ['APPDATA'])
config=app/'xyz.chatboxapp.app'/'config.json'
backup=config.with_name('config-before-qwen-'+stamp+'.json')
shutil.copy2(config,backup)
data=json.loads(config.read_text(encoding='utf-8-sig'))
settings=data['settings']; pid='custom-provider-qwen-seetacloud-local'
model=json.loads(pathlib.Path('remote-models.json').read_text(encoding='utf-8'))['data'][0]['id']
models=json.loads(pathlib.Path('remote-models.json').read_text(encoding='utf-8'))['data']
if 'qwen-novel' in models[0].get('aliases',[]): model='qwen-novel'
entries=settings.setdefault('customProviders',[])
if not any(x['id']==pid for x in entries): entries.append({'id':pid,'name':'Qwen3.8 27B · SSH 本地隧道','type':'openai','isCustom':True})
settings.setdefault('providers',{})[pid]={'apiKey':'local-ssh','apiHost':'http://127.0.0.1:18081/v1','apiPath':'/chat/completions','useProxy':False,'models':[{'modelId':model,'type':'chat','apiStyle':'openai','nickname':'Qwen3.8-27B-Uncensored Q8','contextWindow':131072,'maxOutput':16384,'capabilities':[]}]}
favorite={'provider':pid,'model':model}
settings['favoritedModels']=[x for x in settings.get('favoritedModels',[]) if x.get('provider')!=pid]
if favorite not in settings.setdefault('favoritedModels',[]): settings['favoritedModels'].append(favorite)
settings['defaultChatModel']=favorite
settings['maxTokens']=16384
settings['stream']=True
settings['temperature']=0.7
settings['topP']=0.8
settings['defaultPrompt']='你是中文小说作者。目录、章节标题和正文全部使用简体中文，不使用英文标题或英文段落。先给出简短中文目录，再按顺序完成用户要求的正文。紧扣用户指定的主角、主题、身体感受和行动过程，保持姓名、地点、时间及人物关系一致。使用自然连贯的段落与正常标点；避免反复概括、机械对白、无关支线和重复结尾。'
tmp=config.with_suffix('.qwen.tmp'); tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8'); os.replace(tmp,config)
print('Chatbox configured. Backup:',backup)
moba=app/'MobaXterm'/'MobaXterm.ini'
if moba.exists():
    mbackup=moba.with_name('MobaXterm-before-qwen-'+stamp+'.ini'); shutil.copy2(moba,mbackup)
    raw=moba.read_bytes()
    encoding='utf-8' if raw.startswith(b'\xef\xbb\xbf') else 'cp1252'
    try: text=raw.decode(encoding)
    except UnicodeDecodeError: encoding='utf-8';text=raw.decode(encoding)
    name='qwen-current-32204'
    if not re.search(r'^\d+\.'+re.escape(name)+r'=',text,re.M):
        indexes=[int(x) for x in re.findall(r'^(\d+)\.[^=]+=Local;',text,re.M)]
        entry=f'{max(indexes,default=0)+1:04d}.{name}=Local;root@connect.westd.seetacloud.com:32204;127.0.0.1:8081;18081;0;No SSH key selected;127.0.0.1;No proxy selected;0'
        if '[PortForwarding]' in text: text=text.replace('[PortForwarding]','[PortForwarding]\r\n'+entry,1)
        else: text+='\r\n[PortForwarding]\r\n'+entry+'\r\n'
        mt=moba.with_suffix('.qwen.tmp');mt.write_bytes(text.encode(encoding));os.replace(mt,moba)
    print('MobaXterm tunnel saved. Backup:',mbackup)
verify=json.loads(config.read_text(encoding='utf-8'))
assert verify['settings']['providers'][pid]['apiHost']=='http://127.0.0.1:18081/v1'
print('Verified model:',model)
