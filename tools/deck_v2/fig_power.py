import sys, math; sys.path.insert(0, '.')
from figkit import icon, render_html, FONT_CSS
W, H = 780, 540
INK, BLUE, AMBER, RED, TEAL, MUTED, LINE = '#0F2338', '#00629B', '#E3A63B', '#B91C1C', '#0E7C86', '#6B7A90', '#D5E1EC'
X0, X1 = 215, 760                       # plot x-range (px)
lo, hi = -4, 2                          # log10 W: 100 µW .. 100 W  (right = low power)
def xp(w): return X1 - (math.log10(w) - lo) / (hi - lo) * (X1 - X0)
rows = [  # label, sub, (wmin, wmax) or point, colour, icon, source
 ('CPU', 'embedded / server', (10, 100), '#7E91A6', 'cpu-64-bit', 'Capra 2020'),
 ('GPU', 'edge / server', 100, '#7E91A6', 'expansion-card', 'Capra 2020'),
 ('FPGA', 'reconfigurable', (1, 10), BLUE, 'developer-board', 'Capra 2020'),
 ('Dense DNN ASIC', 'NPU · systolic', (0.1, 1), BLUE, 'chip', 'Capra 2020'),
 ('Eyeriss', 'CNN ASIC, AlexNet conv', 0.278, BLUE, 'chip', 'Chen 2017'),
 ('TrueNorth', 'SNN · 1 M neurons', 0.065, TEAL, 'brain', 'Akopyan 2015'),
 ('Speck', 'SNN + DVS camera', 0.0007, TEAL, 'eye', 'Yao 2024'),
]
y0, dy = 52, 58
g = []
# envelope zone (≤ tens of mW)
g.append(f'<rect x="{xp(0.035)}" y="40" width="{X1+10-xp(0.035)}" height="{y0+dy*len(rows)-40}" rx="14" fill="#B91C1C" opacity=".07"/>')
g.append(f'<line x1="{xp(0.035)}" y1="40" x2="{xp(0.035)}" y2="{y0+dy*len(rows)}" stroke="{RED}" stroke-width="2" stroke-dasharray="6 5"/>')
g.append(f'<text x="{xp(0.035)-8}" y="28" text-anchor="middle" class="ss" font-size="16" font-weight="700" fill="{RED}">extreme-edge envelope  ≲ tens of mW</text>')
for i, (lab, sub, val, col, ic, src) in enumerate(rows):
    y = y0 + i * dy
    g.append(f'<line x1="{X0}" y1="{y+20}" x2="{X1}" y2="{y+20}" stroke="#EEF3F8" stroke-width="1"/>')
    g.append(icon(ic, 32, col, x=10, y=y+4))
    g.append(f'<text x="54" y="{y+19}" class="sf" font-size="19" font-weight="600" fill="{INK}">{lab}</text>')
    g.append(f'<text x="54" y="{y+38}" class="ss" font-size="14.5" fill="{MUTED}">{sub}</text>')
    if isinstance(val, tuple):
        xa, xb = xp(val[1]), xp(val[0])
        g.append(f'<rect x="{xa}" y="{y+8}" width="{xb-xa}" height="24" rx="12" fill="{col}" opacity=".88"/>')
        txt = f'{val[0]:g}–{val[1]:g} W' if val[1] >= 1 else f'{val[0]*1000:g}–{val[1]*1000:g} mW'
        g.append(f'<text x="{xb+10}" y="{y+26}" class="ss" font-size="16" font-weight="700" fill="{col}">{txt}</text>')
    else:
        x = xp(val)
        g.append(f'<circle cx="{x}" cy="{y+20}" r="11" fill="{col}" stroke="#fff" stroke-width="3"/>')
        txt = f'≈ {val:g} W' if val >= 1 else f'{val*1000:g} mW'
        g.append(f'<text x="{x+18}" y="{y+26}" class="ss" font-size="16" font-weight="700" fill="{col}">{txt}</text>')
# axis
ay = y0 + dy * len(rows) + 6
g.append(f'<line x1="{X0}" y1="{ay}" x2="{X1}" y2="{ay}" stroke="{INK}" stroke-width="1.5"/>')
for e, lab in [(2, '100 W'), (1, '10 W'), (0, '1 W'), (-1, '100 mW'), (-2, '10 mW'), (-3, '1 mW'), (-4, '100 µW')]:
    x = xp(10 ** e)
    g.append(f'<line x1="{x}" y1="{ay}" x2="{x}" y2="{ay+7}" stroke="{INK}" stroke-width="1.5"/><text x="{x}" y="{ay+26}" text-anchor="middle" class="ss" font-size="15" fill="{MUTED}">{lab}</text>')
g.append(f'<text x="{(X0+X1)/2}" y="{ay+50}" text-anchor="middle" class="ss" font-size="16" font-weight="700" fill="{INK}">power (log scale)  →  towards the extreme edge</text>')
svg = f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">{"".join(g)}</svg>'
html = f'<!doctype html><html><head><meta charset="utf-8"><style>{FONT_CSS}*{{margin:0}}body{{width:{W}px;height:{H}px;background:transparent}}</style></head><body>{svg}</body></html>'
render_html(html, '/tmp/claude-0/-home-user/2f31366c-8266-5d82-b134-0e1ce71114f5/scratchpad/deck/figs/power.png', W, H, 2.6)
print('ok')
