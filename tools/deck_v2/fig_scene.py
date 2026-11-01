import sys; sys.path.insert(0, '.')
from figkit import render_html, FONT_CSS
from art import *
W, H = 1600, 640
GY = 468                                   # ground line (pavement top)
def leader(x1, y1, x2, y2, col): return f'<path d="M{x1},{y1} L{x2},{y2}" stroke="{col}" stroke-width="1.6" stroke-opacity=".6"/><circle cx="{x2}" cy="{y2}" r="4" fill="{col}"/>'
parts = [DEFS,
 f'<rect x="0" y="0" width="{W}" height="{GY}" fill="url(#sky)"/>',
 f'<rect x="0" y="{GY}" width="{W}" height="{H-GY}" fill="url(#ground)"/>',
 mdi('city-variant', 420, GY-200, 200, '#CBD9E6', .75), mdi('city', 1300, GY-150, 160, '#CBD9E6', .6),
 mdi('pine-tree', 728, GY-66, 66, '#A8C3B1'), mdi('pine-tree', 766, GY-50, 50, '#B8D0BF'), mdi('tree', 1520, GY-78, 78, '#A8C3B1'),
 f'<rect x="0" y="{GY+20}" width="{W}" height="78" fill="#3A4A5A"/>',
 ''.join(f'<rect x="{x}" y="{GY+56}" width="46" height="6" rx="3" fill="#F6F9FC" opacity=".85"/>' for x in range(20, W, 92)),
 f'<rect x="0" y="{GY+16}" width="{W}" height="6" fill="#B9C6D2"/>',
 cloud(290, 130, 1.15), rack(198, 102, 44, 88), rack(252, 102, 44, 88), rack(306, 102, 44, 88), rack(360, 102, 44, 88),
 building(575, GY-225, 140, 225, 7, 4), mdi('router-wireless', 619, GY-282, 52, BLUE),
 tower(880, GY, 235),
 street_lamp(1045, GY+16, 170),
 mdi('walk', 945, GY-84, 84, '#1D3B5E'), mdi('glasses', 970, GY-75, 28, AMBER),
 car(1095, GY+62, 0.74),
 drone(1215, 118, 0.85),
]
for (x1, y1), (x2, y2), lift in [((1200, GY+8), (905, GY-215), 80), ((1215, 132), (900, GY-238), 60), ((985, GY-60), (888, GY-205), 30),
                                  ((852, GY-240), (690, GY-280), 70), ((620, GY-285), (420, 210), 80)]:
    parts.append(f'<path d="M{x1},{y1} Q{(x1+x2)/2},{min(y1,y2)-lift} {x2},{y2}" stroke="{BLUE}" stroke-width="2.6" fill="none" stroke-dasharray="3 9" stroke-linecap="round" opacity=".8"/>')
parts.append(f'<text x="560" y="128" class="ss" font-style="italic" font-size="16" fill="{BLUE}">offloading ↑  wireless · shared · best-effort</text>')
# implant inset
parts.append(f'<g filter="url(#sh)"><circle cx="1470" cy="190" r="118" fill="#FFFFFF" stroke="{RED}" stroke-opacity=".35" stroke-width="3"/></g>')
parts.append(eye_implant(1485, 190, 74))
# labels (title + one line)
def tag(x, y, title, line, col, w):
    return (f'<g filter="url(#shs)"><rect x="{x}" y="{y}" width="{w}" height="54" rx="11" fill="#FFFFFF"/></g><rect x="{x}" y="{y}" width="6" height="54" rx="3" fill="{col}"/>'
            f'<text x="{x+16}" y="{y+23}" class="sf" font-weight="600" font-size="17" fill="{col}">{title}</text>'
            f'<text x="{x+16}" y="{y+43}" class="ss" font-size="14" fill="{INK}">{line}</text>')
parts += [tag(60, 236, 'Cloud', 'kW per rack · hot swap', BLUE, 205), leader(165, 236, 210, 195, BLUE),
          tag(360, 330, 'Fog', '10–100 W · technician', BLUE, 190), leader(550, 357, 590, 340, BLUE),
          tag(770, 40, 'Edge', 'MEC at the base station', TEAL, 205), leader(875, 94, 880, 230, TEAL),
          tag(870, GY+110, 'Wearable', 'mW · replace the device', RED, 205), leader(975, GY+110, 975, GY+2, RED),
          tag(1105, GY+110, 'Vehicle · UAV · robot', 'tens–hundreds W · workshop', TEAL, 240), leader(1225, GY+110, 1225, GY+92, TEAL),
          tag(1350, 330, 'Retinal implant', '≈ +1 °C · µW–mW · surgery', RED, 240), leader(1470, 330, 1470, 308, RED)]
svg = f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">{"".join(parts)}</svg>'
bar = '''<div class="bar"><span>CLOUD</span><div class="g"></div><span>EXTREME EDGE</span></div>
<div class="cap"><span>← more compute · more redundancy · easy repair</span><span>closer to the physical world · power, heat headroom and repairability vanish →</span></div>'''
html = f'''<!doctype html><html><head><meta charset="utf-8"><style>{FONT_CSS}
*{{margin:0;box-sizing:border-box}} body{{width:{W}px;font-family:'Source Sans 3',sans-serif;background:#F6F9FC}}
.wrap{{border-radius:22px;overflow:hidden;border:1.5px solid #D5E1EC;box-shadow:0 10px 30px rgba(15,35,56,.10)}}
.bar{{display:flex;align-items:center;gap:14px;margin:16px 6px 4px;font-weight:700;font-size:15px;color:#0F2338;letter-spacing:1px}}
.g{{flex:1;height:12px;border-radius:6px;background:linear-gradient(90deg,#00629B,#0E7C86 55%,#B91C1C)}}
.cap{{display:flex;justify-content:space-between;font-size:15px;color:#6B7A90;margin:0 6px}}
</style></head><body><div class="wrap">{svg}</div>{bar}</body></html>'''
render_html(html, '/tmp/claude-0/-home-user/2f31366c-8266-5d82-b134-0e1ce71114f5/scratchpad/deck/figs/scene.png', W, H + 72, scale=2.4)
print('ok')
