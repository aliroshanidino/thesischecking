import sys; sys.path.insert(0, '.')
from figkit import icon, render_html, FONT_CSS
W, H = 1320, 470
NAVY, BLUE, GOLD, RED, TEAL, MUTE, LINE = '#203864', '#2F5597', '#E09F3E', '#C8553D', '#0F5C6E', '#6B7B83', '#D7E0E2'
tiers = [
 ('Cloud', 'data centre', ['cloud', 'server'], 'kW per rack', 'hot swap', 'large', BLUE),
 ('Fog / Edge', 'gateway · MEC server', ['router-wireless', 'access-point-network'], '10–100 W', 'technician visit', 'moderate', BLUE),
 ('Vehicle / Robot', 'on-board computer', ['car-side', 'quadcopter', 'robot-industrial'], 'tens–hundreds W', 'workshop', 'limited', TEAL),
 ('Wearable', 'skin contact', ['watch', 'glasses'], 'mW', 'replace device', 'small', RED),
 ('Implant', 'living tissue, ≈ +1 °C', ['brain', 'eye'], 'µW – mW', 'surgery / none', 'very small', RED),
]
cols = ''
for i, (name, sub, icons, power, repair, lat, col) in enumerate(tiers):
    ic = ''.join(f'<div class="ic">{icon(n, 40 if len(icons) > 2 else 48, col)}</div>' for n in icons)
    hl = ' hl' if i >= 3 else ''
    cols += f'''<div class="tier{hl}" style="--c:{col}">
      <div class="icons">{ic}</div>
      <div class="name">{name}</div><div class="sub">{sub}</div>
      <div class="kv"><span>Power</span><b>{power}</b></div>
      <div class="kv"><span>Repair</span><b>{repair}</b></div>
      <div class="kv"><span>Redundancy</span><b>{lat}</b></div></div>'''
    if i < 4: cols += f'<div class="arrow">{icon("chevron-right", 34, "#9AAAB2")}</div>'
html = f'''<!doctype html><html><head><meta charset="utf-8"><style>{FONT_CSS}
*{{box-sizing:border-box;margin:0}} body{{width:{W}px;height:{H}px;font-family:'Source Sans 3',sans-serif;color:{NAVY};background:transparent}}
.row{{display:flex;align-items:stretch;gap:6px;padding:18px 18px 0}}
.tier{{flex:1;background:#fff;border:1.5px solid {LINE};border-top:6px solid var(--c);border-radius:14px;padding:16px 15px 12px;display:flex;flex-direction:column}}
.tier.hl{{background:#FFF8F4;border-color:#F0C9BC;border-top-color:var(--c);box-shadow:0 6px 18px rgba(200,85,61,.16)}}
.icons{{display:flex;gap:6px;align-items:flex-end;height:54px;margin-bottom:8px}}
.name{{font-family:'Source Serif 4',serif;font-weight:600;font-size:24px;color:var(--c);white-space:nowrap}}
.sub{{font-size:16px;color:{MUTE};margin:2px 0 14px;font-style:italic}}
.kv{{display:flex;justify-content:space-between;border-top:1px dashed {LINE};padding:6px 0;font-size:15px}}
.kv span{{color:{MUTE}}} .kv b{{font-weight:700;color:{NAVY}}}
.arrow{{display:flex;align-items:center}}
.axes{{margin:18px 18px 0;position:relative;height:120px}}
.bar{{height:30px;border-radius:15px;display:flex;align-items:center;justify-content:space-between;padding:0 18px;font-weight:600;font-size:16px;color:#fff;margin-bottom:12px}}
.b1{{background:linear-gradient(90deg,{BLUE},{TEAL} 60%,{RED})}}
.b2{{background:linear-gradient(90deg,{RED},{TEAL} 40%,{BLUE});}}
.note{{font-size:15px;color:{MUTE};text-align:center;margin-top:4px}}
</style></head><body>
<div class="row">{cols}</div>
<div class="axes">
 <div class="bar b1"><span>more compute, more redundancy</span><span>closer to the physical world</span></div>
 <div class="bar b2"><span>power · heat headroom · repairability shrink</span><span>latency · privacy · autonomy improve</span></div>
 <div class="note">Indicative orders of magnitude — thesis Table 1.1 (Capra et al., 2020; implant limit ≈ +1 °C: Kim et al., 2007)</div>
</div></body></html>'''
render_html(html, '/tmp/claude-0/-home-user/2f31366c-8266-5d82-b134-0e1ce71114f5/scratchpad/deck/figs/continuum.png', W, H)
print('ok')
