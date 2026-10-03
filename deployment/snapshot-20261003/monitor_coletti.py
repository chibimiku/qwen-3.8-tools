#!/usr/bin/env python3
# coletti llama-server 实时看板：页面一次性加载，前端 fetch 局部刷新（不整页重载）
import http.server, json, urllib.request, os, re

LOG = "/root/autodl-tmp/server_coletti.log"
M = "http://127.0.0.1:8081/metrics"

def get(path):
    try:
        with urllib.request.urlopen(path, timeout=3) as r:
            return r.read().decode("utf-8", "replace"), None
    except Exception as e:
        return None, str(e)

def parse_metrics(txt):
    d = {}
    for line in txt.splitlines():
        if line.startswith("#") or not line.strip():
            continue
        m = re.match(r'^([a-zA-Z_:][a-zA-Z0-9_:]*)(\{[^}]*\})?\s+(\S+)\s*(?:$|#)', line)
        if m:
            try:
                val = float(m.group(3))
            except ValueError:
                continue
            d.setdefault(m.group(1), []).append(val)
    return d

def val(d, name, agg="sum"):
    if name not in d or not d[name]:
        return None
    v = d[name]
    return sum(v) if agg == "sum" else (max(v) if agg == "max" else v[0])

def read_tail(maxchars=9000):
    try:
        with open(LOG, "rb") as f:
            f.seek(0, os.SEEK_END)
            sz = f.tell()
            f.seek(max(0, sz - maxchars))
            return f.read().decode("utf-8", "replace")[-maxchars:]
    except Exception as e:
        return "log err: %s" % e

def data():
    met, me = get(M)
    if me is not None:
        return {"err": me}
    d = parse_metrics(met)
    draft = val(d, "llamacpp:spec_decode_num_draft_tokens_total", "sum")
    accept = val(d, "llamacpp:spec_decode_num_accepted_tokens_total", "sum")
    def f(v, nd=1):
        return "%.*f" % (nd, v) if v is not None else "—"
    return {
        "gen_ts": f(val(d, "llamacpp:predicted_tokens_seconds", "first")),
        "prompt_ts": f(val(d, "llamacpp:prompt_tokens_seconds", "first")),
        "gen_total": f(val(d, "llamacpp:tokens_predicted_total", "sum"), 0),
        "prompt_total": f(val(d, "llamacpp:prompt_tokens_total", "sum"), 0),
        "processing": "yes" if (val(d, "llamacpp:requests_processing", "max") or 0) > 0 else "no",
        "deferred": f(val(d, "llamacpp:requests_deferred", "max"), 0),
        "max_tokens": f(val(d, "llamacpp:n_tokens_max", "max"), 0),
        "acc_rate": ("%.1f%%" % (100.0 * accept / draft)) if (draft and accept and draft > 0) else "—",
        "log": read_tail(),
    }

PAGE = r'''<!doctype html><html><head><meta charset="utf-8"><title>llama-server 监控</title>
<style>
body{font-family:system-ui,Arial,sans-serif;background:#0f1215;color:#e6e6e6;margin:0;padding:14px}
h2{margin:0 0 10px;color:#fff;font-size:18px}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:14px}
.card{background:#171b20;border:1px solid #2a2f37;border-radius:8px;padding:10px}
.card .v{font-size:24px;font-weight:700;color:#4cc9f0}
.card .t{font-size:12px;color:#adb5bd;margin-top:2px}
.card .s{font-size:10px;color:#6c757d;margin-top:2px}
pre{white-space:pre-wrap;background:#000;color:#8fffa1;padding:10px;border-radius:6px;max-height:430px;overflow:auto;font:12px/1.5 monospace}
.lab{color:#999;font-size:12px;margin:4px 0}
</style></head><body>
<h2>llama-server (Coletti) 实时监控（3s 自动刷新）</h2>
<div class="grid">
  <div class="card"><div class="v" id="gen_ts">—</div><div class="t">生成 t/s</div><div class="s">predicted_tokens_seconds</div></div>
  <div class="card"><div class="v" id="prompt_ts">—</div><div class="t">Prompt t/s</div><div class="s">prompt_tokens_seconds</div></div>
  <div class="card"><div class="v" id="gen_total">—</div><div class="t">生成 tokens(累计)</div><div class="s">tokens_predicted_total</div></div>
  <div class="card"><div class="v" id="prompt_total">—</div><div class="t">Prompt tokens(累计)</div><div class="s">prompt_tokens_total</div></div>
  <div class="card"><div class="v" id="processing">—</div><div class="t">处理中</div><div class="s">requests_processing</div></div>
  <div class="card"><div class="v" id="deferred">—</div><div class="t">排队/deferred</div><div class="s">requests_deferred</div></div>
  <div class="card"><div class="v" id="max_tokens">—</div><div class="t">max tokens</div><div class="s">n_tokens_max</div></div>
  <div class="card"><div class="v" id="acc_rate">—</div><div class="t">Spec-dec 接受率</div><div class="s">accepted/draft</div></div>
</div>
<div class="lab">server_coletti.log 尾部</div>
<pre id="log">加载中…</pre>
<script>
function set(id, v){ var e=document.getElementById(id); if(e) e.textContent = (v===null||v===undefined)?'—':v; }
function refresh(){
  fetch('./data').then(function(r){return r.json();}).then(function(d){
    if(d.err){ set('gen_ts', 'err: '+d.err); return; }
    set('gen_ts', d.gen_ts); set('prompt_ts', d.prompt_ts); set('gen_total', d.gen_total);
    set('prompt_total', d.prompt_total); set('processing', d.processing); set('deferred', d.deferred);
    set('max_tokens', d.max_tokens); set('acc_rate', d.acc_rate);
    var log=document.getElementById('log'); log.textContent=d.log; log.scrollTop=log.scrollHeight;
  }).catch(function(){});
}
refresh(); setInterval(refresh, 3000);
</script>
</body></html>'''

class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.rstrip('/').endswith('data') or self.path.endswith('/data'):
            d = data()
            body = json.dumps(d, ensure_ascii=False).encode("utf-8")
            self.send_response(200); self.send_header("Content-Type", "application/json; charset=utf-8"); self.end_headers()
            self.wfile.write(body)
        else:
            body = PAGE.encode("utf-8")
            self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.end_headers()
            self.wfile.write(body)
    def log_message(self, *a):
        pass

print("MONITOR_UP http://0.0.0.0:8090")
http.server.ThreadingHTTPServer(("0.0.0.0", 8090), H).serve_forever()
