"""Divider 02 hero: six families of prior work around this thesis."""
import sys, math; sys.path.insert(0, '.')
from figkit import render_html, FONT_CSS
from art import *
W, H = 760, 680
cx, cy = 380, 322
fams = [('chip', 'Edge-vision', 'accelerators', '#00629B', '#E3EEF7'),
        ('shield-check-outline', 'Fault-tolerant', 'accelerators', '#00629B', '#E3EEF7'),
        ('brain', 'Neuromorphic', 'processors', '#0E7C86', '#E0F1F2'),
        ('shield-sync-outline', 'SNN fault', 'tolerance', '#0E7C86', '#E0F1F2'),
        ('magnify-scan', 'Fault-injection', 'tools', '#9A6A12', '#FBF1DE'),
        ('eye-outline', 'Spiking vision', 'systems', '#9A6A12', '#FBF1DE')]
R = 205
p = [DEFS, f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>',
     f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="#D5E1EC" stroke-width="1.6" stroke-dasharray="4 8"/>',
     f'<circle cx="{cx}" cy="{cy}" r="150" fill="none" stroke="#E6EEF5" stroke-width="1.4"/>']
for k, (ic, l1, l2, col, tint) in enumerate(fams):
    a = math.radians(-90 + k * 60); x = cx + R * math.cos(a); y = cy + R * math.sin(a)
    p.append(f'<line x1="{cx + 100*math.cos(a):.1f}" y1="{cy + 100*math.sin(a):.1f}" x2="{x - 58*math.cos(a):.1f}" y2="{y - 58*math.sin(a):.1f}" '
             f'stroke="#B8C9DA" stroke-width="2.4" stroke-dasharray="2 7" stroke-linecap="round"/>')
    p.append(f'<g filter="url(#sh)"><circle cx="{x:.1f}" cy="{y:.1f}" r="54" fill="#FFFFFF" stroke="#D5E1EC" stroke-width="2"/></g>')
    p.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="42" fill="{tint}"/>' + mdi(ic, x - 26, y - 26, 52, col))
    p.append(f'<circle cx="{x-40:.1f}" cy="{y-40:.1f}" r="14" fill="#E3A63B"/><text x="{x-40:.1f}" y="{y-34:.1f}" text-anchor="middle" class="sf" font-weight="600" font-size="16" fill="#FFFFFF">{"ABCDEF"[k]}</text>')
    c, sn = math.cos(a), math.sin(a)
    if abs(c) < 0.1:      # top / bottom: label above or below
        tx, anc = x, 'middle'; ty = y - 84 if sn < 0 else y + 82
    else:                 # sides: label outward
        tx, anc = (x + 64, 'start') if c > 0 else (x - 64, 'end'); ty = y - 4
    p.append(f'<text x="{tx:.1f}" y="{ty:.1f}" text-anchor="{anc}" class="ss" font-weight="700" font-size="19" fill="#0F2338">{l1}</text>'
             f'<text x="{tx:.1f}" y="{ty+22:.1f}" text-anchor="{anc}" class="ss" font-size="18" fill="#6B7A90">{l2}</text>')
# centre: this thesis
p.append(f'<g filter="url(#sh)"><circle cx="{cx}" cy="{cy}" r="96" fill="#0F2338"/></g>')
p.append(f'<circle cx="{cx}" cy="{cy}" r="84" fill="none" stroke="#E3A63B" stroke-width="3" stroke-dasharray="10 7"/>')
p.append(mdi('chip', cx - 30, cy - 52, 60, '#E3A63B'))
p.append(f'<text x="{cx}" y="{cy+34}" text-anchor="middle" class="sf" font-weight="600" font-size="21" fill="#FFFFFF">This thesis</text>')
p.append(f'<text x="{cx}" y="{H-22}" text-anchor="middle" class="ss" font-size="20" fill="#6B7A90">six families of prior work — <tspan font-weight="700" fill="#00629B">none covers all</tspan> of our needs</text>')
svg = f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">{"".join(p)}</svg>'
html = f'<!doctype html><html><head><meta charset="utf-8"><style>{FONT_CSS}*{{margin:0}}body{{width:{W}px;height:{H}px}}</style></head><body>{svg}</body></html>'
render_html(html, '/tmp/claude-0/-home-user/2f31366c-8266-5d82-b134-0e1ce71114f5/scratchpad/deck/figs/hero_lit.png', W, H, 2.5)
print('ok')
