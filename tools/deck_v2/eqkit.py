"""Render LaTeX equations to transparent high-DPI PNGs with KaTeX (local npm package) + Chromium."""
import json, subprocess, os
KDIR = '/tmp/claude-0/-home-user/2f31366c-8266-5d82-b134-0e1ce71114f5/scratchpad/katex_dl/package'
def eq_png(tex, out, size=40, color='#0F2338', scale=3):
    out = os.path.abspath(out); tmp = out.replace('.png', '.html')
    js = f"""
const katex=require('{KDIR}/dist/katex.js');const fs=require('fs');const {{chromium}}=require('playwright');
(async()=>{{
 const html=katex.renderToString({json.dumps(tex)},{{displayMode:true,throwOnError:true,strict:false,trust:true}});
 fs.writeFileSync('{tmp}',`<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="file://{KDIR}/dist/katex.min.css">
 <style>body{{margin:0;background:transparent}} #eq{{display:inline-block;padding:6px 10px;color:{color}}} .katex{{font-size:{size}px}} .katex-display{{margin:0}}</style></head>
 <body><div id="eq">${{html}}</div></body></html>`);
 const b=await chromium.launch();const p=await b.newPage({{deviceScaleFactor:{scale},viewport:{{width:2400,height:1200}}}});
 await p.goto('file://{tmp}');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(400);
 const el=await p.$('#eq');await el.screenshot({{path:'{out}',omitBackground:true}});await b.close();}})();"""
    r = subprocess.run(['node', '-e', js], capture_output=True, text=True, cwd='/tmp/claude-0/-home-user/2f31366c-8266-5d82-b134-0e1ce71114f5/scratchpad')
    if r.returncode: raise RuntimeError(r.stderr[-2000:])
    return out
