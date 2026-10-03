import pathlib,struct,json,re
import sys
sys.stdout.reconfigure(encoding='utf-8')
p=pathlib.Path(r'C:\Program Files\Chatbox\resources\app.asar')
with p.open('rb') as f:
    h=struct.unpack('<4I',f.read(16)); tree=json.loads(f.read(h[3])); base=8+h[1]
    def walk(d,pre=''):
        for k,v in d.items():
            name=pre+k
            if 'files' in v: yield from walk(v['files'],name+'/')
            elif name.startswith('dist/') and name.endswith('.js'): yield name,v
    for name,v in walk(tree['files']):
        if v.get('unpacked') or 'offset' not in v: continue
        f.seek(base+int(v['offset'])); content=f.read(v['size']).decode('utf-8','replace')
        for term in ['const SettingsSchema=','),SettingsSchema=','SettingsSchema=GlobalSessionSettingsSchema','GlobalSessionSettingsSchema.merge','GlobalSessionSettingsSchema.extend','globalSettings','defaultSessionSettings']:
            matches=list(re.finditer(re.escape(term),content))
            if matches and 'apiPath' in content:
                print(name,term)
                for m in matches[:2]: print(content[max(0,m.start()-100):m.end()+1000])
