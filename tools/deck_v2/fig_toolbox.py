"""Methodology slide: redrawn hardware toolbox (RTL-to-GDSII, verification/FI frontend, environment)."""
import sys; sys.path.insert(0, '.')
from figkit import render_html, FONT_CSS
from art import mdi
W, H = 2400, 836
INK, BLUE, AMBER, RED, TEAL, MUTED, LINE = '#0F2338', '#00629B', '#E3A63B', '#B91C1C', '#0E7C86', '#6B7A90', '#D5E1EC'
g = ['<defs><filter id="sh" x="-5%" y="-10%" width="110%" height="130%"><feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#0F2338" flood-opacity=".10"/></filter>'
     '<marker id="ar" markerUnits="userSpaceOnUse" markerWidth="26" markerHeight="26" refX="20" refY="13" orient="auto"><path d="M0,0 L26,13 L0,26 z" fill="#0F2338"/></marker>'
     '<marker id="arg" markerUnits="userSpaceOnUse" markerWidth="20" markerHeight="20" refX="15" refY="10" orient="auto"><path d="M0,0 L20,10 L0,20 z" fill="#7F93A8"/></marker></defs>']
def T(x, y, s, size=22, w=400, col=INK, anchor='start', cls='ss', extra=''):
    return f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" font-weight="{w}" fill="{col}" text-anchor="{anchor}" {extra}>{s}</text>'
def card(x, y, w, h, fill, stroke='#CFDAE6', rx=18, dash=''):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<g filter="url(#sh)"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="2"{d}/></g>'
def pill(x, y, w, s, size=21):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="27" rx="7" fill="#FFFFFF" stroke="#D9E2EC" stroke-width="1.4"/>'
            + T(x + w / 2, y + 20, s, size, 400, INK, 'middle'))
def arrow(x1, y1, x2, y2, col='#0F2338', wdt=5, m='ar'):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="{wdt}" stroke-linecap="round" marker-end="url(#{m})"/>'
def band(y, h, title):
    return (f'<rect x="8" y="{y}" width="{W-16}" height="{h}" rx="22" fill="#FBFCFE" stroke="#C9D6E3" stroke-width="2" stroke-dasharray="8 7"/>'
            + T(32, y + 34, title, 21, 700, '#3D5A78', extra='letter-spacing="2.4"'))
# ---------------- band A: RTL -> GDSII
g.append(band(6, 452, 'RTL → GDSII  ·  FULLY OPEN-SOURCE, ASIC-TARGETED FLOW'))
cy0, ch = 56, 384
cols = [(24, 300, '#EEF6EE'), (374, 470, '#EAF1F9'), (894, 500, '#EAF5F3'), (1444, 500, '#FBF2E6'), (1994, 382, '#EEF2F6')]
for x, w, f in cols: g.append(card(x, cy0, w, ch, f))
for k in range(4):
    xa = cols[k][0] + cols[k][1] + 6; xb = cols[k + 1][0] - 8
    g.append(arrow(xa, cy0 + ch / 2, xb, cy0 + ch / 2))
# RTL design
x, w = cols[0][0], cols[0][1]
g.append(mdi('file-code-outline', x + w / 2 - 48, cy0 + 26, 96, '#2E7D4F'))
g.append(T(x + w / 2, cy0 + 160, 'RTL design', 30, 700, INK, 'middle', 'sf'))
g.append(T(x + w / 2, cy0 + 192, '(VHDL / Verilog)', 21, 400, MUTED, 'middle'))
for i, s in enumerate(['Fault-tolerant', 'neuromorphic processor', 'Homeostatic feedback loops', 'Error detection & recovery']):
    bullet = i in (0, 2, 3)
    yy = cy0 + 238 + i * 32 + (6 if i >= 2 else 0)
    if bullet: g.append(f'<circle cx="{x+26}" cy="{yy-7}" r="5" fill="#2E7D4F"/>')
    g.append(T(x + 40, yy, s, 21, 400, INK))
# stages
stages = [(1, 'LOGIC SYNTHESIS', ('Yosys', '#7B3FA0', None), 'open-source synthesis',
           ['RTL parsing & elaboration', 'Boolean optimization', 'Redundancy extraction', 'Technology mapping', 'Timing & area optimization'],
           ['SkyWater 130 nm', 'standard-cell library'], '#E1EAF4'),
          (2, 'PHYSICAL IMPLEMENTATION (P&R)', ('Open', INK, ('ROAD', '#E8772E')), None,
           ['Floorplanning', 'Power grid generation (PDN)', 'Placement (global + detailed)', 'Clock tree synthesis (CTS)', 'Routing (global + detailed)', 'Filler, tap cells & DRC fixing'],
           ['Handles the routing density of the', 'homeostatic feedback loops'], '#FFF3DC'),
          (3, 'SIGN-OFF & ANALYSIS', ('Open', INK, ('STA', BLUE)), None,
           ['Post-synthesis STA', 'Multi-corner timing analysis', 'Critical path & slack analysis', 'Power analysis (PPA)', 'DRC / LVS (via Magic)', 'GDSII stream-out'],
           ['Power: leakage · internal · switching', 'Area: cell + routing · Fmax · worst slack'], '#FFF3DC')]
for k, (n, title, wm, sub, items, note, notefill) in enumerate(stages):
    x, w, _ = cols[k + 1]
    g.append(T(x + 22, cy0 + 36, f'STAGE {n}', 19, 700, '#C98A1E', extra='letter-spacing="2"'))
    g.append(T(x + 22 + 104, cy0 + 36, title, 19, 700, INK, extra='letter-spacing="1"'))
    g.append(f'<rect x="{x+22}" y="{cy0+50}" width="{w-44}" height="62" rx="12" fill="#FFFFFF" stroke="#D9E2EC" stroke-width="1.5"/>')
    if wm[2] is None:
        g.append(T(x + w / 2 - (60 if sub else 0), cy0 + 95, wm[0], 40, 700, wm[1], 'middle', 'sf'))
        if sub: g.append(T(x + w / 2 + 10, cy0 + 90, sub, 19, 400, MUTED, 'start', 'ss', 'font-style="italic"'))
    else:
        g.append(f'<text x="{x+w/2}" y="{cy0+97}" text-anchor="middle" class="ss" font-size="42" font-weight="700">'
                 f'<tspan fill="{wm[1]}">{wm[0]}</tspan><tspan fill="{wm[2][1]}">{wm[2][0]}</tspan></text>')
    for i, s in enumerate(items):
        g.append(pill(x + 22, cy0 + 124 + i * 32, w - 44, s))
    ny = cy0 + ch - 70
    g.append(f'<rect x="{x+22}" y="{ny}" width="{w-44}" height="56" rx="10" fill="{notefill}" stroke="{"#E8C27A" if notefill != "#E1EAF4" else "#BFD0E2"}" stroke-width="1.4" stroke-dasharray="5 4"/>')
    for j, s in enumerate(note): g.append(T(x + w / 2, ny + 24 + j * 22, s, 19, 400, '#3D4B5C', 'middle'))
# output
x, w = cols[4][0], cols[4][1]
g.append(T(x + w / 2, cy0 + 36, 'OUTPUT · TAPE-OUT READY', 19, 700, '#C98A1E', 'middle', extra='letter-spacing="1.6"'))
outs = [('file-outline', 'GDSII', 'layout'), ('chip', 'Sign-off reports', 'STA · PPA · DRC'), ('code-braces', 'Netlist', 'post-route')]
for i, (ic, a, b) in enumerate(outs):
    yy = cy0 + 60 + i * 104
    g.append(f'<rect x="{x+22}" y="{yy}" width="{w-44}" height="92" rx="12" fill="#FFFFFF" stroke="#D9E2EC" stroke-width="1.5"/>')
    g.append(mdi(ic, x + 40, yy + 16, 60, INK))
    g.append(T(x + 118, yy + 42, a, 25, 700, INK)); g.append(T(x + 118, yy + 70, b, 20, 400, MUTED))
# ---------------- band B: verification & fault-injection frontend
yB, hB = 472, 212
g.append(band(yB, hB, 'VERIFICATION & FAULT-INJECTION FRONTEND  ·  PRE-SYNTHESIS'))
nodes = [('file-code-outline', '#2E7D4F', 'RTL source code', 'VHDL / Verilog', '#EEF6EE', None),
         (None, None, 'GHDL', 'VHDL compiler & simulator', '#EAF1F9', '#1E5BB8'),
         ('language-python', '#3776AB', 'cocotb', 'Python testbenches · VPI / VHPI', '#F1EEF8', None),
         ('square-wave', '#9A6A12', 'Cycle-accurate simulation', '4-valued logic (0 · 1 · X · Z)', '#FBF2E6', None),
         ('needle', RED, 'Gate-level fault injection', 'GLFI campaigns → GateScan', '#FBEAEA', None),
         ('clipboard-check-outline', INK, 'Coverage & metrics', 'outcome classes · debug', '#FFF7E6', None)]
nw, gap = 336, 52; x0 = (W - (6 * nw + 5 * gap)) / 2; ny0 = yB + 52
for i, (ic, icc, a, b, f, wmc) in enumerate(nodes):
    x = x0 + i * (nw + gap)
    stroke = '#E3A0A0' if ic == 'needle' else '#CFDAE6'
    g.append(card(x, ny0, nw, 104, f, stroke, 14))
    if ic: g.append(mdi(ic, x + 18, ny0 + 24, 56, icc)); tx = x + 88
    else: g.append(T(x + 24, ny0 + 66, '', 10)); tx = x + 22
    if wmc: g.append(T(tx, ny0 + 56, a, 34, 700, wmc, 'start', 'sf'))
    else: g.append(T(tx, ny0 + 46, a, 21.5, 700, INK))
    g.append(T(tx, ny0 + (86 if wmc else 76), b, 18.5, 400, MUTED))
    if i < 5: g.append(arrow(x + nw + 4, ny0 + 52, x + nw + gap - 6, ny0 + 52, INK, 4))
# feedback loop: metrics -> testbenches
xa = x0 + 5 * (nw + gap) + nw / 2; xb = x0 + 2 * (nw + gap) + nw / 2; yl = ny0 + 104 + 22
g.append(f'<path d="M {xa} {ny0+106} L {xa} {yl} L {xb} {yl} L {xb} {ny0+112}" fill="none" stroke="#7F93A8" stroke-width="3" stroke-dasharray="9 6" marker-end="url(#arg)"/>')
g.append(f'<rect x="{(xa+xb)/2-130}" y="{yl-14}" width="260" height="28" fill="#FBFCFE"/>' + T((xa + xb) / 2, yl + 7, 'new workloads / triggers', 18, 600, '#7F93A8', 'middle'))
# ---------------- band C: environment
yC, hC = 696, 134
g.append(band(yC, hC, 'DEVELOPMENT ENVIRONMENT & TOOLING'))
env = [('linux', INK, 'Linux on WSL 2', 'Yosys & netlist tools on Windows'),
       ('microsoft-visual-studio-code', '#007ACC', 'Visual Studio Code', 'RTL development & debugging'),
       ('docker', '#2496ED', 'Docker', 'reproducible EDA environment'),
       ('cube-outline', '#2E5E8C', 'Open-source EDA stack', 'Yosys · OpenROAD · OpenSTA · Magic · GHDL · cocotb · Icarus'),
       (None, None, 'SkyWater 130 nm PDK', 'open, commercial-grade CMOS')]
ew = (W - 64) / 5
for i, (ic, icc, a, b) in enumerate(env):
    x = 32 + i * ew
    if i: g.append(f'<line x1="{x-6}" y1="{yC+48}" x2="{x-6}" y2="{yC+hC-14}" stroke="#C9D6E3" stroke-width="2" stroke-dasharray="4 6"/>')
    if ic: g.append(mdi(ic, x + 10, yC + 50, 64, icc))
    else:   # stylised wafer
        cxw, cyw = x + 42, yC + 82
        g.append(f'<circle cx="{cxw}" cy="{cyw}" r="31" fill="#EAF3E6" stroke="#5E9E4F" stroke-width="3"/>')
        for dx in (-14, 0, 14):
            for dy in (-14, 0, 14):
                if dx * dx + dy * dy <= 300: g.append(f'<rect x="{cxw+dx-5.5}" y="{cyw+dy-5.5}" width="11" height="11" rx="2" fill="#5E9E4F"/>')
        g.append(f'<path d="M {cxw-12} {cyw+29} L {cxw+12} {cyw+29}" stroke="#FFFFFF" stroke-width="4"/>')
    g.append(T(x + 92, yC + 76, a, 23, 700, INK))
    words = b.split(' '); l1, l2 = [], []
    for wd in words:
        (l1 if len(' '.join(l1 + [wd])) <= 34 and not l2 else l2).append(wd)
    g.append(T(x + 92, yC + 102, ' '.join(l1), 18.5, 400, MUTED))
    if l2: g.append(T(x + 92, yC + 124, ' '.join(l2), 18.5, 400, MUTED))
svg = f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">{"".join(g)}</svg>'
html = f'<!doctype html><html><head><meta charset="utf-8"><style>{FONT_CSS}*{{margin:0}}body{{width:{W}px;height:{H}px;background:transparent}}</style></head><body>{svg}</body></html>'
render_html(html, '/tmp/claude-0/-home-user/2f31366c-8266-5d82-b134-0e1ce71114f5/scratchpad/deck/figs/toolbox.png', W, H, 1.6)
print('ok')
