"""Slide 9 figure: the abstraction stack with one research gap per layer (Ch. 1 §1.8, gaps 1+2 merged)."""
import sys; sys.path.insert(0, '.')
from figkit import icon, render_html, FONT_CSS
W, H = 1560, 640
INK, BLUE, AMBER, RED, TEAL, MUTED, LINE = '#0F2338', '#00629B', '#E3A63B', '#B91C1C', '#0E7C86', '#6B7A90', '#D5E1EC'
X0, FW, SK, TOPD, FRONT, PITCH, Y0 = 34, 590, 40, 22, 70, 116, 40     # stack geometry
layers = [  # (name, icon, prior-work chips, top tint, front gradient, edge, gap tag, sentence)
    ('SYSTEM · EDGE–CLOUD CONTINUUM', 'cloud-outline', ['Neurosurgeon', 'split / federated learning', 'MEC offloading'],
     '#E6F0F8', ('#F4F8FC', '#DCE8F3'), '#9DB8D2', 'G1', 'SYSTEM',
     [('Offloading assumes a ', 0), ('correct end device', 1), (' — no dependable path exists for safety-critical vision at the extreme edge.', 0)]),
    ('ACCELERATOR ARCHITECTURE', 'developer-board', ['TMR / NMR', 'spares + re-mapping', 'astrocyte monitors'],
     '#E1ECF6', ('#F1F6FB', '#D4E3F1'), '#93B1CE', 'G2', 'ARCHITECTURE',
     [('Fault tolerance ', 0), ('does not scale down', 1), (': redundancy costs area and power, and the monitor is built from the same faulty gates.', 0)]),
    ('NEURON CORE', 'brain', ['LIF / IF taken as given', 'dead / saturated fault models'],
     '#FBF1DE', ('#FFF9EE', '#F7E6C4'), AMBER, 'G3', 'NEURON CORE',
     [('The neuron is a fixed primitive, ', 0), ('not a design object', 1), (' — its own dynamics are rarely made, or proven, to stay bounded.', 0)]),
    ('GATE-LEVEL ASSESSMENT', 'magnify-scan', ['two-valued simulation', 'closed FuSa tools', 'SDC · DUE · masked'],
     '#E1ECF6', ('#F1F6FB', '#D4E3F1'), '#93B1CE', 'G4', 'ASSESSMENT',
     [('Assessment is ', 0), ('not physically faithful', 1), (': two-valued or above the netlist, closed tools, and “masked” is never proven harmless.', 0)]),
    ('ON-CHIP LEARNING · CROSSES EVERY LAYER', 'school-outline', ['FT on frozen networks', 'offline fault maps'],
     '#DDF0F1', ('#EEF8F8', '#CFE8EA'), '#7CC3C8', 'G5', 'LEARNING',
     [('Dependability and on-chip learning are ', 0), ('studied apart', 1), (' — fault tolerance is tested on frozen, pre-trained networks.', 0)]),
]
g = ['<defs>'
     '<filter id="sh" x="-10%" y="-20%" width="120%" height="150%"><feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#0F2338" flood-opacity=".14"/></filter>'
     '<filter id="shs" x="-10%" y="-20%" width="120%" height="150%"><feDropShadow dx="0" dy="2" stdDeviation="2.5" flood-color="#0F2338" flood-opacity=".10"/></filter>']
for i, L in enumerate(layers):
    g.append(f'<linearGradient id="fr{i}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{L[4][0]}"/><stop offset="1" stop-color="{L[4][1]}"/></linearGradient>')
g.append('</defs>')

def text_runs(x, y, runs, size, width_chars):
    """Wrap (text, bold) runs; a word may span runs (e.g. bold phrase + ':'), spaces separate words."""
    import re
    words, cur = [], []
    for t, b in runs:
        for tok in re.findall(r'\S+|\s+', t):
            if tok.isspace():
                if cur: words.append(cur); cur = []
            else:
                cur.append((tok, b))
    if cur: words.append(cur)
    lines, line, n = [], [], 0
    for w in words:
        ln = sum(len(t) for t, _ in w)
        if line and n + 1 + ln > width_chars: lines.append(line); line, n = [], 0
        n += ln + (1 if line else 0); line.append(w)
    lines.append(line)
    out = []
    for li, line in enumerate(lines):
        spans = ''
        for j, w in enumerate(line):
            for k, (t, b) in enumerate(w):
                lead = ' ' if (j > 0 and k == 0) else ''
                spans += f'<tspan font-weight="{700 if b else 400}" fill="{RED if b else INK}">{lead}{t}</tspan>'
        out.append(f'<text x="{x}" y="{y + li * size * 1.28:.1f}" class="ss" font-size="{size}" xml:space="preserve">{spans}</text>')
    return ''.join(out), len(lines)

for i, (name, ic, chips, top, fr, edge, tag, short, sent) in enumerate(layers):
    yt = Y0 + i * PITCH; yf = yt + TOPD; cy = yf + FRONT / 2
    learn = i == 4
    dash = ' stroke-dasharray="7 5"' if learn else ''
    # slab: top face, right side face, front face
    g.append(f'<g filter="url(#sh)">'
             f'<polygon points="{X0},{yf} {X0+SK},{yt} {X0+FW+SK},{yt} {X0+FW},{yf}" fill="{top}" stroke="{edge}" stroke-width="1.6"{dash}/>'
             f'<polygon points="{X0+FW},{yf} {X0+FW+SK},{yt} {X0+FW+SK},{yt+FRONT} {X0+FW},{yf+FRONT}" fill="{fr[1]}" stroke="{edge}" stroke-width="1.6"{dash}/>'
             f'<rect x="{X0}" y="{yf}" width="{FW}" height="{FRONT}" fill="url(#fr{i})" stroke="{edge}" stroke-width="1.6"{dash}/></g>')
    col = TEAL if learn else ('#9A6A12' if i == 2 else BLUE)
    g.append(icon(ic, 30, col, x=X0 + 14, y=yf + 9))
    g.append(f'<text x="{X0+54}" y="{yf+29}" class="ss" font-size="17" font-weight="700" letter-spacing="1.2" fill="{INK}">{name}</text>')
    cx = X0 + 54
    for c in chips:
        w = 8.0 * len(c) + 22
        g.append(f'<rect x="{cx}" y="{yf+38}" width="{w:.0f}" height="26" rx="13" fill="#FFFFFF" fill-opacity=".85" stroke="#B8C4D2"/>'
                 f'<text x="{cx+w/2:.0f}" y="{yf+56.5}" text-anchor="middle" class="ss" font-size="16" fill="{MUTED}">{c}</text>')
        cx += w + 8
    # crack across the top face and down the side face
    kx = X0 + FW - 70
    g.append(f'<path d="M {kx-2} {yf} l 9 -6 l -5 -4 l 10 -5 l -4 -3 l 9 -4" fill="none" stroke="{RED}" stroke-width="2.6" stroke-linejoin="round"/>')
    g.append(f'<path d="M {X0+FW+20} {yt+11} l -6 14 l 8 6 l -7 16 l 6 9 l -6 18" fill="none" stroke="{RED}" stroke-width="2.4" stroke-linejoin="round"/>')
    # connector + gap badge
    bx = X0 + FW + SK + 52
    g.append(f'<line x1="{X0+FW+SK+4}" y1="{cy}" x2="{bx-24}" y2="{cy}" stroke="{RED}" stroke-width="2" stroke-dasharray="4 4"/>')
    g.append(f'<circle cx="{bx}" cy="{cy}" r="23" fill="{RED}" filter="url(#shs)"/>'
             f'<text x="{bx}" y="{cy+7}" text-anchor="middle" class="sf" font-size="19" font-weight="600" fill="#FFFFFF">{tag}</text>')
    # statement card
    cx0, cw, ch = bx + 40, W - (bx + 40) - 8, 100
    g.append(f'<g filter="url(#shs)"><rect x="{cx0}" y="{cy-ch/2}" width="{cw}" height="{ch}" rx="14" fill="#FFFFFF" stroke="{LINE}" stroke-width="1.4"/></g>')
    g.append(f'<rect x="{cx0}" y="{cy-ch/2+14}" width="4" height="{ch-28}" rx="2" fill="{RED}"/>')
    g.append(f'<text x="{cx0+22}" y="{cy-ch/2+27}" class="ss" font-size="14" font-weight="700" letter-spacing="1.6" fill="{MUTED}">{short}</text>')
    t, _ = text_runs(cx0 + 22, cy - ch / 2 + 55, sent, 20.5, 64)
    g.append(t)
g.append(f'<text x="{X0}" y="{H-6}" class="ss" font-size="16" fill="{MUTED}">grey chips = what prior work does at each layer  ·  red = what is still missing  (Ch. 1 §1.8)</text>')
svg = f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">{"".join(g)}</svg>'
html = f'<!doctype html><html><head><meta charset="utf-8"><style>{FONT_CSS}*{{margin:0}}body{{width:{W}px;height:{H}px;background:transparent}}</style></head><body>{svg}</body></html>'
render_html(html, '/tmp/claude-0/-home-user/2f31366c-8266-5d82-b134-0e1ce71114f5/scratchpad/deck/figs/gaps.png', W, H, 2.4)
print('ok')
