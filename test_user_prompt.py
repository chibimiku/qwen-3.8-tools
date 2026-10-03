import pathlib,json,urllib.request,time,re,sys
sys.stdout.reconfigure(encoding='utf-8')
base='http://127.0.0.1:18081';out=pathlib.Path('audit');out.mkdir(exist_ok=True)
prompt='要求：请写一段关于一名大二女生在后山行走，着凉感冒后非常难受坚持回来的小说，先写章节目录结构再填充内容，5000字左右。'
system='你是中文小说作者。目录、章节标题和正文全部使用简体中文，不使用英文标题或英文段落。先给出简短中文目录，再按顺序完成约5000汉字的正文。紧扣用户指定的主角、身体感受、行动过程和回程，保持姓名、地点、时间及人物关系一致。使用自然连贯的段落与正常标点；避免反复概括、机械对白、无关支线和重复结尾。'
summary=[]
for name,params,messages in [('user_original',{'temperature':0.5,'top_p':0.9,'repeat_penalty':1.3,'presence_penalty':1.0},[{'role':'user','content':prompt}]),('user_fixed',{'temperature':0.7,'top_p':0.8,'repeat_penalty':1.0,'presence_penalty':1.5},[{'role':'system','content':system},{'role':'user','content':prompt}])]:
    body={'model':'qwen-novel','messages':messages,'top_k':20,'min_p':0,'seed':42,'max_tokens':7000,'stream':False,**params}
    (out/(name+'-request.json')).write_text(json.dumps(body,ensure_ascii=False,indent=2),encoding='utf-8')
    print('START',name,flush=True);start=time.monotonic()
    req=urllib.request.Request(base+'/v1/chat/completions',data=json.dumps(body,ensure_ascii=False).encode(),headers={'Content-Type':'application/json'})
    result=json.load(urllib.request.urlopen(req,timeout=600)); text=result['choices'][0]['message'].get('content') or ''
    (out/(name+'-response.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/(name+'.txt')).write_text(text,encoding='utf-8')
    record={'name':name,'seconds':round(time.monotonic()-start,2),'characters':len(text),'hanzi':len(re.findall('[\u4e00-\u9fff]',text)),'latin_words':re.findall('[A-Za-z]{2,}',text),'finish_reason':result['choices'][0]['finish_reason'],'usage':result.get('usage'),'reasoning_chars':len(result['choices'][0]['message'].get('reasoning_content') or '')}
    summary.append(record); (out/'user-prompt-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(record,ensure_ascii=False),flush=True)
