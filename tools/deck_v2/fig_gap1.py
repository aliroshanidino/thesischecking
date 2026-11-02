"""Slide 9 figure (gap 1): statistical vs deterministic compliance with four hard limits. Schematic, no data."""
import sys, math; sys.path.insert(0, '.')
from figkit import icon, render_html, FONT_CSS
W, H = 760, 716
INK, BLUE, AMBER, RED, TEAL, MUTED, LINE = '#0F2338', '#00629B', '#E3A63B', '#B91C1C', '#0E7C86', '#6B7A90', '#D5E1EC'
AX0, AX1 = 210, 728                       # x-range of each row's axis
rows = [('Deadline', 'timer-outline', 'hard deadline', 'cap'),
        ('Power', 'flash-outline', 'power cap', 'cap'),
        ('Energy', 'battery-outline', 'energy budget', 'cap'),
        ('Accuracy', 'bullseye-arrow', 'accuracy floor', 'floor')]
def lognorm(u, mu, s):                     # u in (0, 1]
    return 0 if u <= 0 else math.exp(-(math.log(u) - mu) ** 2 / (2 * s * s)) / u
def gauss(u, m, s): return math.exp(-(u - m) ** 2 / (2 * s * s))
g = ['<defs><linearGradient id="off" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8A9AB0" stop-opacity=".55"/>'
     '<stop offset="1" stop-color="#8A9AB0" stop-opacity=".08"/></linearGradient>'
     '<linearGradient id="on" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0E7C86" stop-opacity=".9"/>'
     '<stop offset="1" stop-color="#0E7C86" stop-opacity=".25"/></linearGradient></defs>']
g.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="20" fill="#FFFFFF" stroke="{LINE}" stroke-width="1.5"/>')
g.append(f'<text x="28" y="44" class="sf" font-size="25" font-weight="600" fill="{INK}">Gap 1 · met on average, not guaranteed</text>')
# legend
lx = 28
for sw, lab in [('<rect width="26" height="14" rx="3" fill="url(#off)" stroke="#8A9AB0"/>', 'offloaded · best effort'),
                ('<rect width="26" height="14" rx="3" fill="url(#on)"/>', 'on-device · deterministic'),
                (f'<rect width="26" height="14" rx="3" fill="{RED}" fill-opacity=".45"/>', 'limit violated')]:
    g.append(f'<g transform="translate({lx},64)">{sw}</g><text x="{lx+34}" y="76" class="ss" font-size="18" fill="{INK}">{lab}</text>')
    lx += 34 + 9.2 * len(lab) + 22
RH, RY0 = 146, 104
for i, (name, ic, limlab, kind) in enumerate(rows):
    y0 = RY0 + i * RH; base = y0 + RH - 30; top = y0 + 18
    if i: g.append(f'<line x1="24" y1="{y0}" x2="{W-24}" y2="{y0}" stroke="{LINE}" stroke-width="1"/>')
    g.append(f'<circle cx="54" cy="{(top+base)/2}" r="26" fill="#E3EEF7"/>' + icon(ic, 30, BLUE, x=39, y=(top + base) / 2 - 15))
    g.append(f'<text x="92" y="{(top+base)/2+8}" class="ss" font-size="22" font-weight="700" fill="{INK}">{name}</text>')
    g.append(f'<line x1="{AX0}" y1="{base}" x2="{AX1}" y2="{base}" stroke="#9DB4CB" stroke-width="2"/>')
    # curves on u in [0,1] mapped to the axis
    N = 220; us = [k / N for k in range(1, N + 1)]
    if kind == 'cap':
        lim = 0.74
        mode, sig, onm = [(0.33, 0.58, 0.44), (0.40, 0.48, 0.50), (0.36, 0.53, 0.47)][i]
        off = [lognorm(u, math.log(mode), sig) for u in us]; on = [gauss(u, onm, 0.022) for u in us]
    else:  # floor: violation on the left
        lim = 0.30
        off = [lognorm(1.02 - u, math.log(0.34), 0.56) for u in us]; on = [gauss(u, 0.62, 0.022) for u in us]
    mo, mn = max(off), max(on); hh = base - top
    X = lambda u: AX0 + u * (AX1 - AX0)
    pts_off = [(X(u), base - f / mo * hh * 0.72) for u, f in zip(us, off)]
    pts_on = [(X(u), base - f / mn * hh * 0.98) for u, f in zip(us, on)]
    poly = lambda pts: f'M {pts[0][0]:.1f} {base} ' + ' '.join(f'L {x:.1f} {y:.1f}' for x, y in pts) + f' L {pts[-1][0]:.1f} {base} Z'
    g.append(f'<path d="{poly(pts_off)}" fill="url(#off)" stroke="#8A9AB0" stroke-width="1.8"/>')
    viol = [(x, y) for (x, y), u in zip(pts_off, us) if (u >= lim if kind == 'cap' else u <= lim)]
    if viol: g.append(f'<path d="{poly(viol)}" fill="{RED}" fill-opacity=".45" stroke="none"/>')
    g.append(f'<path d="{poly(pts_on)}" fill="url(#on)" stroke="{TEAL}" stroke-width="1.6"/>')
    xl = X(lim)
    g.append(f'<line x1="{xl:.1f}" y1="{top-6}" x2="{xl:.1f}" y2="{base+4}" stroke="{RED}" stroke-width="2.4" stroke-dasharray="6 4"/>')
    anchor, dx = ('start', 8) if kind == 'cap' else ('end', -8)
    g.append(f'<text x="{xl+dx:.1f}" y="{top+10}" text-anchor="{anchor}" class="ss" font-size="17" font-weight="700" fill="{RED}">{limlab}</text>')
g.append(f'<text x="{W-26}" y="{H-14}" text-anchor="end" class="ss" font-size="16" font-style="italic" fill="{MUTED}">schematic · illustrative shapes, no measured data</text>')
svg = f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">{"".join(g)}</svg>'
html = f'<!doctype html><html><head><meta charset="utf-8"><style>{FONT_CSS}*{{margin:0}}body{{width:{W}px;height:{H}px;background:transparent}}</style></head><body>{svg}</body></html>'
render_html(html, '/tmp/claude-0/-home-user/2f31366c-8266-5d82-b134-0e1ce71114f5/scratchpad/deck/figs/gap1.png', W, H, 3)
print('ok')
