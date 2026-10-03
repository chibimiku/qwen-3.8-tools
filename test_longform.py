import urllib.request,json,time,re,pathlib,collections,sys
base='http://127.0.0.1:18081'
model=json.load(urllib.request.urlopen(base+'/v1/models'))['data'][0]['id']
out=pathlib.Path('audit');out.mkdir(exist_ok=True)
prompt='写一章4500至5500汉字的中文悬疑小说，只输出正文，不要提纲、分析、创作说明或总结。故事设定：1998年秋天，山城的旧钟表铺，女修表师林岚收到十年前失踪的父亲寄来的包裹，包裹中有一只停在凌晨两点十七分的怀表。邮戳却是明天的日期。人物只有林岚、邮递员陈默、老警察赵启。林岚始终不知道父亲是否活着。第一人称限知视角，全章一夜内发生。展开至少五个有因果联系的完整场景，细节与对话服务于调查。赵启在中段揭示一条可验证但不完整的线索。结尾怀表重新走动，并出现一个具体的新证据，悬念保持。人物姓名、视角、时间保持一致。语言自然，避免反复抒情、同义改写和整段重复。写足篇幅。'
summary=[]
cases=[('original',{'repeat_penalty':1.3,'presence_penalty':1.0}),('neutral_penalties',{'repeat_penalty':1.0,'presence_penalty':0.0}),('official_non_thinking',{'repeat_penalty':1.0,'presence_penalty':1.5,'temperature':0.7,'top_p':0.8})]
cases.append(('repeat_only_fix',{'repeat_penalty':1.0,'presence_penalty':1.0}))
if len(sys.argv)>1:
    cases=[x for x in cases if x[0]==sys.argv[1]]
    if (out/'summary.json').exists(): summary=json.loads((out/'summary.json').read_text(encoding='utf-8'))
for label,penalties in cases:
    body={'model':model,'messages':[{'role':'system','content':'你是中文小说作者。严格遵循故事约束，直接写小说正文。'},{'role':'user','content':prompt}], 'temperature':0.5,'top_p':0.9,'top_k':20,'min_p':0,'seed':42,'max_tokens':7000,'stream':False,**penalties}
    (out/(label+'-request.json')).write_text(json.dumps(body,ensure_ascii=False,indent=2),encoding='utf-8')
    print('START',label,flush=True); start=time.monotonic()
    req=urllib.request.Request(base+'/v1/chat/completions',data=json.dumps(body,ensure_ascii=False).encode(),headers={'Content-Type':'application/json'})
    result=json.load(urllib.request.urlopen(req,timeout=600))
    (out/(label+'-response.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    text=result['choices'][0]['message'].get('content') or ''
    (out/(label+'.txt')).write_text(text,encoding='utf-8')
    chunks=[text[i:i+1000] for i in range(0,len(text),1000)]
    windows=[]
    for c in chunks:
        grams=[c[i:i+10] for i in range(max(0,len(c)-9))]; counts=collections.Counter(grams)
        windows.append({'chars':len(c),'repeated_10gram_fraction':round(sum(n-1 for n in counts.values())/max(1,len(grams)),4)})
    stats={'label':label,'seconds':round(time.monotonic()-start,2),'characters':len(text),'hanzi':len(re.findall('[\u4e00-\u9fff]',text)),'finish_reason':result['choices'][0]['finish_reason'],'usage':result.get('usage'),'windows':windows,'reasoning_chars':len(result['choices'][0]['message'].get('reasoning_content') or '')}
    summary.append(stats);(out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(stats,ensure_ascii=False),flush=True)
