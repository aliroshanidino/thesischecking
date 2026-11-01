import sys; sys.path.insert(0, '.')
from figkit import icon, render_html, FONT_CSS
W, H = 1320, 430
INK, BLUE, AMBER, RED, TEAL, MUTED, LINE = '#0F2338', '#00629B', '#E3A63B', '#B91C1C', '#0E7C86', '#6B7A90', '#D5E1EC'
st = [
 ('01', 'Introduction', 'Mission-critical vision, the edge device, and why its neuron must not fail', 'Ch. 1–2', 'quadcopter', BLUE),
 ('02', 'Literature Review', 'Six families of prior work and where this thesis stands', 'Ch. 3', 'book-open-page-variant', BLUE),
 ('03', 'Methodology', 'Hardened neuron → trustworthy fault analysis → BioVision', 'Ch. 4–7', 'chip', TEAL),
 ('04', 'Results', 'PPA, fault campaign, RFoM, on-chip learning, BioVision', 'Ch. 8', 'chart-box-outline', TEAL),
 ('05', 'Conclusion', 'Takeaways, publications and the road ahead', 'Ch. 9', 'flag-checkered', AMBER),
]
xs = [132 + i * 264 for i in range(5)]
cy = 138
nodes = ''
for i, (num, name, desc, ch, ic, col) in enumerate(st):
    x = xs[i]
    nodes += f'''<div class="st" style="left:{x-120}px;--c:{col}">
      <div class="num">{num}</div>
      <div class="ring"><div class="disc">{icon(ic, 52, col)}</div></div>
      <div class="name">{name}</div><div class="desc">{desc}</div><div class="chip">{ch}</div></div>'''
path_d = f'M {xs[0]} {cy} ' + ' '.join(f'C {xs[i]+90} {cy-26 if i%2==0 else cy+26}, {xs[i+1]-90} {cy+26 if i%2==0 else cy-26}, {xs[i+1]} {cy}' for i in range(4))
html = f'''<!doctype html><html><head><meta charset="utf-8"><style>{FONT_CSS}
*{{box-sizing:border-box;margin:0}} body{{width:{W}px;height:{H}px;font-family:'Source Sans 3',sans-serif;color:{INK};position:relative;background:transparent}}
svg.path{{position:absolute;left:0;top:0}}
.st{{position:absolute;top:28px;width:240px;text-align:center}}
.num{{font-family:'Source Serif 4',serif;font-weight:600;font-size:30px;color:var(--c);letter-spacing:1px;height:44px}}
.ring{{margin:0 auto;width:132px;height:132px;border-radius:50%;background:conic-gradient(var(--c) 0 100%);padding:5px;box-shadow:0 10px 24px rgba(15,35,56,.14)}}
.disc{{width:100%;height:100%;border-radius:50%;background:#fff;display:flex;align-items:center;justify-content:center;border:6px solid #F6F9FC}}
.name{{font-family:'Source Serif 4',serif;font-weight:600;font-size:25px;margin-top:20px}}
.desc{{font-size:16.5px;color:{MUTED};line-height:1.32;margin:8px 10px 12px;min-height:66px}}
.chip{{display:inline-block;font-weight:700;font-size:14px;color:var(--c);background:#fff;border:1.5px solid var(--c);border-radius:20px;padding:3px 14px}}
</style></head><body>
<svg class="path" width="{W}" height="{H}"><defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="{BLUE}"/><stop offset=".55" stop-color="{TEAL}"/><stop offset="1" stop-color="{AMBER}"/></linearGradient></defs>
<path d="{path_d}" stroke="url(#g)" stroke-width="5" fill="none" stroke-dasharray="2 12" stroke-linecap="round"/></svg>
{nodes}</body></html>'''
render_html(html, '/tmp/claude-0/-home-user/2f31366c-8266-5d82-b134-0e1ce71114f5/scratchpad/deck/figs/outline.png', W, H)
print('ok')
