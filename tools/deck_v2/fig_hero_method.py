"""Divider 03 hero (v2): three phases as three simple steps."""
import sys; sys.path.insert(0, '.')
from figkit import render_html, FONT_CSS
from art import *
W, H = 760, 700
steps = [('chip', '#0E7C86', '#E0F1F2', 'Fault-tolerant neuron core', 'homeostasis inside the neuron', 'done', '#0E7C86'),
         ('magnify-scan', '#00629B', '#E3EEF7', 'Fault-assessment campaign', 'GLFI → GateScan', 'done', '#0E7C86'),
         ('eye-outline', '#6B4FA0', '#EEE9F6', 'Bio-inspired edge-vision network', 'BioVision', 'in progress', '#C98A1E')]
p = [DEFS, f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>',
     '<defs><marker id="ah" markerUnits="userSpaceOnUse" markerWidth="22" markerHeight="22" refX="11" refY="11" orient="auto"><path d="M0,0 L22,11 L0,22 z" fill="#E3A63B"/></marker></defs>']
x0, cw, chh, y0, pitch = 40, 680, 158, 52, 214
for i, (ic, col, tint, t1, t2, st, stc) in enumerate(steps):
    y = y0 + i * pitch
    p.append(f'<g filter="url(#sh)"><rect x="{x0}" y="{y}" width="{cw}" height="{chh}" rx="22" fill="#FFFFFF" stroke="#D5E1EC" stroke-width="2"/></g>')
    p.append(f'<rect x="{x0}" y="{y+26}" width="7" height="{chh-52}" rx="3.5" fill="{col}"/>')
    p.append(f'<circle cx="{x0+92}" cy="{y+chh/2}" r="50" fill="{tint}"/>' + mdi(ic, x0 + 62, y + chh / 2 - 30, 60, col))
    p.append(f'<text x="{x0+170}" y="{y+52}" class="ss" font-size="16" font-weight="700" letter-spacing="2.4" fill="#E3A63B">PHASE {i+1}</text>')
    p.append(f'<text x="{x0+170}" y="{y+90}" class="sf" font-size="27" font-weight="600" fill="#0F2338">{t1}</text>')
    p.append(f'<text x="{x0+170}" y="{y+122}" class="ss" font-size="20" fill="#6B7A90">{t2}</text>')
    w = 11 * len(st) + 28
    p.append(f'<rect x="{x0+cw-w-22}" y="{y+30}" width="{w}" height="26" rx="13" fill="{stc}" fill-opacity=".13"/>'
             f'<text x="{x0+cw-w/2-22}" y="{y+48}" text-anchor="middle" class="ss" font-size="14.5" font-weight="700" fill="{stc}">{st}</text>')
    if i < 2:
        ya = y + chh + 8
        p.append(f'<line x1="{x0+92}" y1="{ya}" x2="{x0+92}" y2="{ya+pitch-chh-26}" stroke="#E3A63B" stroke-width="4" stroke-linecap="round" marker-end="url(#ah)"/>')
svg = f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">{"".join(p)}</svg>'
html = f'<!doctype html><html><head><meta charset="utf-8"><style>{FONT_CSS}*{{margin:0}}body{{width:{W}px;height:{H}px}}</style></head><body>{svg}</body></html>'
render_html(html, '/tmp/claude-0/-home-user/2f31366c-8266-5d82-b134-0e1ce71114f5/scratchpad/deck/figs/hero_method.png', W, H, 2.5)
print('ok')
