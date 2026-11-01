import sys, math; sys.path.insert(0, '.')
from figkit import render_html, FONT_CSS
from art import *
W, H = 760, 650
cx, cy = 380, 345
sat = [('quadcopter', 'UAV', -90), ('car-side', 'Autonomous car', 150), ('eye', 'Retinal implant', 30)]
p = [DEFS, f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>',
     ''.join(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#D5E1EC" stroke-width="1.5" stroke-dasharray="{d}"/>' for r, d in ((150, '0'), (235, '4 8'))),
     f'<g filter="url(#sh)"><circle cx="{cx}" cy="{cy}" r="112" fill="#0F2338"/></g>',
     f'<circle cx="{cx}" cy="{cy}" r="78" fill="url(#iris)"/><circle cx="{cx}" cy="{cy}" r="30" fill="#061522"/>',
     f'<circle cx="{cx-26}" cy="{cy-28}" r="14" fill="#FFFFFF" opacity=".75"/><circle cx="{cx+22}" cy="{cy+20}" r="6" fill="#FFFFFF" opacity=".4"/>',
     f'<circle cx="{cx}" cy="{cy}" r="96" fill="none" stroke="#E3A63B" stroke-width="3" stroke-dasharray="10 7"/>']
for name, lab, ang in sat:
    a = math.radians(ang); x = cx + 235 * math.cos(a); y = cy + 235 * math.sin(a)
    # spike train along the spoke
    ux, uy = (cx - x) / 235, (cy - y) / 235
    for k in range(5):
        px, py = x + ux * (70 + k * 18), y + uy * (70 + k * 18)
        nx, ny = -uy, ux
        p.append(f'<line x1="{px-nx*9}" y1="{py-ny*9}" x2="{px+nx*9}" y2="{py+ny*9}" stroke="#E3A63B" stroke-width="3.5" stroke-linecap="round"/>')
    p.append(f'<g filter="url(#sh)"><circle cx="{x}" cy="{y}" r="62" fill="#FFFFFF" stroke="#D5E1EC" stroke-width="2"/></g>')
    p.append(mdi(name, x - 34, y - 34, 68, RED if name == 'eye' else BLUE))
    ly = y + 92 if ang != -90 else y - 78
    p.append(f'<text x="{x}" y="{ly}" text-anchor="middle" class="sf" font-weight="600" font-size="22" fill="#0F2338">{lab}</text>')
p.append(f'<text x="{cx}" y="{H-36}" text-anchor="middle" class="ss" font-size="21" fill="#6B7A90">an image must become a <tspan font-weight="700" fill="#00629B">decision</tspan> — on the device itself</text>')
svg = f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">{"".join(p)}</svg>'
html = f'<!doctype html><html><head><meta charset="utf-8"><style>{FONT_CSS}*{{margin:0}}body{{width:{W}px;height:{H}px}}</style></head><body>{svg}</body></html>'
render_html(html, '/tmp/claude-0/-home-user/2f31366c-8266-5d82-b134-0e1ce71114f5/scratchpad/deck/figs/hero_intro.png', W, H, 2.5)
print('ok')
