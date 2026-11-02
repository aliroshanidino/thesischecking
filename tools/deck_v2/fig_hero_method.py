"""Divider 03 hero: three phases converge on one dependable edge device."""
import sys, math; sys.path.insert(0, '.')
from figkit import render_html, FONT_CSS
from art import *
W, H = 760, 700
cx, cy, R = 380, 296, 196
phases = [(-150, 'chip', '#0E7C86', '#E0F1F2', 'Phase 1', 'H-ASIZH neuron core', 'done', '#0E7C86'),
          (-30, 'magnify-scan', '#00629B', '#E3EEF7', 'Phase 2', 'GateScan', 'done', '#0E7C86'),
          (90, 'eye-outline', '#6B4FA0', '#EEE9F6', 'Phase 3', 'BioVision', 'in progress', '#C98A1E')]
p = [DEFS, f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>',
     '<defs><marker id="ah" markerUnits="userSpaceOnUse" markerWidth="22" markerHeight="22" refX="12" refY="11" orient="auto"><path d="M0,0 L22,11 L0,22 z" fill="#E3A63B"/></marker></defs>',
     f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="#E6EEF5" stroke-width="1.5"/>']
P = lambda a, r=R: (cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
# flow arcs 1 -> 2 -> 3
for a1, a2 in [(-150, -30), (-30, 90)]:
    s, e = P(a1 + 21), P(a2 - 21)
    p.append(f'<path d="M {s[0]:.1f} {s[1]:.1f} A {R} {R} 0 0 1 {e[0]:.1f} {e[1]:.1f}" fill="none" stroke="#E3A63B" stroke-width="4" '
             f'stroke-linecap="round" marker-end="url(#ah)"/>')
for a, ic, col, tint, ph, name, st, stc in phases:
    x, y = P(a); ix, iy = P(a, 112); ox, oy = P(a, R - 66)
    p.append(f'<line x1="{ix:.1f}" y1="{iy:.1f}" x2="{ox:.1f}" y2="{oy:.1f}" stroke="#B8C9DA" stroke-width="2.4" stroke-dasharray="2 7" stroke-linecap="round"/>')
    p.append(f'<g filter="url(#sh)"><circle cx="{x:.1f}" cy="{y:.1f}" r="64" fill="#FFFFFF" stroke="#D5E1EC" stroke-width="2"/></g>')
    p.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="51" fill="{tint}"/>' + mdi(ic, x - 31, y - 31, 62, col))
    ly = y - 128 if a < 0 else y + 90
    w = 11 * len(st) + 26
    p.append(f'<text x="{x:.1f}" y="{ly:.1f}" text-anchor="middle" class="ss" font-weight="700" font-size="15" letter-spacing="2" fill="#E3A63B">{ph.upper()}</text>'
             f'<text x="{x:.1f}" y="{ly+26:.1f}" text-anchor="middle" class="sf" font-weight="600" font-size="22" fill="#0F2338">{name}</text>'
             f'<rect x="{x-w/2:.1f}" y="{ly+38:.1f}" width="{w}" height="24" rx="12" fill="{stc}" fill-opacity=".14"/>'
             f'<text x="{x:.1f}" y="{ly+55:.1f}" text-anchor="middle" class="ss" font-weight="700" font-size="14" fill="{stc}">{st}</text>')
p.append(f'<g filter="url(#sh)"><circle cx="{cx}" cy="{cy}" r="100" fill="#0F2338"/></g>')
p.append(f'<circle cx="{cx}" cy="{cy}" r="88" fill="none" stroke="#E3A63B" stroke-width="3" stroke-dasharray="10 7"/>')
p.append(mdi('chip', cx - 28, cy - 62, 56, '#E3A63B'))
p.append(f'<text x="{cx}" y="{cy+18}" text-anchor="middle" class="sf" font-weight="600" font-size="19" fill="#FFFFFF">one dependable</text>'
         f'<text x="{cx}" y="{cy+42}" text-anchor="middle" class="sf" font-weight="600" font-size="19" fill="#FFFFFF">edge device</text>')
p.append(f'<text x="{cx}" y="{H-16}" text-anchor="middle" class="ss" font-size="20" fill="#6B7A90">core → <tspan font-weight="700" fill="#00629B">trusted measurement</tspan> → vision system</text>')
svg = f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">{"".join(p)}</svg>'
html = f'<!doctype html><html><head><meta charset="utf-8"><style>{FONT_CSS}*{{margin:0}}body{{width:{W}px;height:{H}px}}</style></head><body>{svg}</body></html>'
render_html(html, '/tmp/claude-0/-home-user/2f31366c-8266-5d82-b134-0e1ce71114f5/scratchpad/deck/figs/hero_method.png', W, H, 2.5)
print('ok')
