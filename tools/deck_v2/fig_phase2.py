"""Phase 2 figures: FARM campaign design, GateScan architecture (neuron-core figure style), certified bracket."""
import sys; sys.path.insert(0, '.')
from figkit import render_html, FONT_CSS
from art import mdi
from eqkit import eq_png
INK, BLUE, AMBER, RED, TEAL, MUTED, LINE = '#0F2338', '#00629B', '#E3A63B', '#B91C1C', '#0E7C86', '#6B7A90', '#D5E1EC'
OUT = '/tmp/claude-0/-home-user/2f31366c-8266-5d82-b134-0e1ce71114f5/scratchpad/deck/figs'
SH = ('<filter id="sh" x="-5%" y="-10%" width="110%" height="130%"><feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#0F2338" flood-opacity=".12"/></filter>'
      '<marker id="ar" markerUnits="userSpaceOnUse" markerWidth="18" markerHeight="18" refX="14" refY="9" orient="auto"><path d="M0,0 L18,9 L0,18 z" fill="#0F2338"/></marker>'
      '<marker id="arb" markerUnits="userSpaceOnUse" markerWidth="18" markerHeight="18" refX="14" refY="9" orient="auto"><path d="M0,0 L18,9 L0,18 z" fill="#2A7AB8"/></marker>'
      '<marker id="arp" markerUnits="userSpaceOnUse" markerWidth="18" markerHeight="18" refX="14" refY="9" orient="auto"><path d="M0,0 L18,9 L0,18 z" fill="#C05A8A"/></marker>')
def T(x, y, s, size=22, w=400, col=INK, anchor='start', cls='ss', extra=''):
    return f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" font-weight="{w}" fill="{col}" text-anchor="{anchor}" {extra}>{s}</text>'
def page(W, H, body, name, scale=2.2):
    svg = f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg"><defs>{SH}</defs>{body}</svg>'
    html = f'<!doctype html><html><head><meta charset="utf-8"><style>{FONT_CSS}*{{margin:0}}body{{width:{W}px;height:{H}px;background:transparent}}</style></head><body>{svg}</body></html>'
    render_html(html, f'{OUT}/{name}.png', W, H, scale)

# ------------------------------------------------------------------ FARM
def farm():
    W, H = 1500, 820; g = []
    cards = [(30, 30, 'F', 'Faults', 'where and what', 'target', BLUE, '#EAF1F9',
              [('site', 'every extracted net of the netlist'), ('value', 'stuck-at-0 / stuck-at-1, permanent, single')]),
             (770, 30, 'A', 'Activation', 'under what and when', 'play-circle-outline', '#9A6A12', '#FBF2E6',
              [('workload', 'short, steady tonic-firing stimulus'), ('time τ', 'inject after 2,000 fault-free cycles, hold to 10,000')]),
             (30, 430, 'R', 'Readouts', 'what we observe', 'pulse', TEAL, '#EAF5F3',
              [('output', 'spike timestamps — the only observation point'), ('golden', 'the same run without the fault')]),
             (770, 430, 'M', 'Measures', 'how we judge', 'scale-balance', '#6B4FA0', '#F1EEF8',
              [('band', 'firing-rate error ≤ 20 % and ISI CV ≤ 0.20'), ('classes', 'masked · tolerant · critical · fatal')])]
    for x, y, L, name, sub, ic, col, tint, rows in cards:
        g.append(f'<g filter="url(#sh)"><rect x="{x}" y="{y}" width="700" height="360" rx="22" fill="{tint}" stroke="{col}" stroke-opacity=".35" stroke-width="2"/></g>')
        g.append(f'<circle cx="{x+62}" cy="{y+64}" r="38" fill="{col}"/>' + T(x + 62, y + 77, L, 38, 700, '#FFFFFF', 'middle', 'sf'))
        g.append(T(x + 120, y + 62, name, 34, 700, INK, cls='sf') + T(x + 120, y + 94, sub, 22, 400, MUTED, extra='font-style="italic"'))
        g.append(mdi(ic, x + 620, y + 30, 54, col))
        for i, (tag, txt) in enumerate(rows):
            yy = y + 140 + i * 92
            g.append(f'<rect x="{x+30}" y="{yy}" width="640" height="76" rx="14" fill="#FFFFFF" stroke="#DCE4ED" stroke-width="1.5"/>')
            tw = 15 * len(tag) + 28
            g.append(f'<rect x="{x+46}" y="{yy+22}" width="{tw}" height="32" rx="16" fill="{col}" fill-opacity=".14"/>' + T(x + 46 + tw / 2, yy + 45, tag, 20, 700, col, 'middle'))
            g.append(T(x + 46 + tw + 18, yy + 46, txt, 22.5, 400, INK))
        if L == 'A':   # injection timeline
            ty = y + 328; x0, x1 = x + 130, x + 660; xi = x0 + (x1 - x0) * 0.2
            g.append(f'<rect x="{x0}" y="{ty-10}" width="{xi-x0}" height="14" rx="4" fill="#5E9E4F"/><rect x="{xi}" y="{ty-10}" width="{x1-xi}" height="14" rx="4" fill="{RED}" fill-opacity=".75"/>')
            g.append(T(x0, ty - 18, 'fault-free', 16, 600, '#5E9E4F') + T(xi + 8, ty - 18, 'fault held on', 16, 600, RED) + T(xi, ty + 24, 'τ = 2,000', 16, 700, INK, 'middle') + T(x1, ty + 24, '10,000 cycles', 16, 400, MUTED, 'end'))
    # centre: the netlist under test (a compact badge in the empty corner gap)
    cx, cy = 750, 410
    g.append(f'<g filter="url(#sh)"><circle cx="{cx}" cy="{cy}" r="74" fill="{INK}"/></g>')
    g.append(f'<circle cx="{cx}" cy="{cy}" r="64" fill="none" stroke="{AMBER}" stroke-width="2.5" stroke-dasharray="7 5"/>')
    g.append(mdi('chip', cx - 22, cy - 46, 44, AMBER))
    g.append(T(cx, cy + 18, 'synthesized', 15, 700, '#FFFFFF', 'middle') + T(cx, cy + 36, 'netlist', 15, 700, '#FFFFFF', 'middle'))
    page(W, H, ''.join(g), 'farm')

# ------------------------------------------------------------------ GateScan architecture (style of the neuron-core figure)
def gs_arch():
    W, H = 2000, 1000; g = []
    def panel(x, y, w, h, fill, title, col='#7F93A8'):
        left = w > 400
        return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="{col}" stroke-width="2" stroke-dasharray="9 6"/>'
                + T(x + 26 if left else x + w / 2, y + 36, title, 27, 600, INK, 'start' if left else 'middle', 'sf', 'font-style="italic"'))
    def blk(x, y, w, h, ic, t1, t2, fill, stroke, icc):
        return (f'<g filter="url(#sh)"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{fill}" stroke="{stroke}" stroke-width="2"/></g>'
                + mdi(ic, x + 14, y + h / 2 - 22, 44, icc) + T(x + 70, y + h / 2 - 4, t1, 22, 700, INK) + T(x + 70, y + h / 2 + 22, t2, 17.5, 400, '#4A5A6E'))
    def arr(x1, y1, x2, y2, m='ar', col=INK, wd=2.6, dash=''):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="{wd}"{d} marker-end="url(#{m})"/>'
    # left: inputs (like the REGISTERS column)
    g.append(panel(20, 70, 230, 900, '#FFF6D6', 'INPUTS', '#C9A44A'))
    for i, (ic, a, b) in enumerate([('file-code-outline', 'RTL', 'any circuit'), ('format-list-checks', 'Fault set', 'SA0 · SA1 · SEU'), ('play-circle-outline', 'Workloads', 'given or random')]):
        y = 160 + i * 270
        g.append(f'<g filter="url(#sh)"><rect x="45" y="{y}" width="180" height="170" rx="12" fill="#FFE9A8" stroke="#C9A44A" stroke-width="2"/></g>')
        g.append(mdi(ic, 105, y + 18, 60, '#7A5A10') + T(135, y + 112, a, 24, 700, INK, 'middle') + T(135, y + 142, b, 17, 400, '#5C4A1E', 'middle'))
    # agent layer
    g.append(panel(290, 70, 1450, 250, '#E7F3FB', 'LLM agent layer: proposes', '#2A7AB8'))
    agents = [('magnify', 'Analyzer', 'ports · modes'), ('script-text-outline', 'Scenario', 'writes workloads'), ('comment-check-outline', 'Critic', 'requests revisions'),
              ('lightbulb-on-outline', 'Interpreter', 'metric · tolerance'), ('target', 'Trigger', 'per-fault stimuli')]
    for i, (ic, a, b) in enumerate(agents):
        x = 320 + i * 284
        fill, st = ('#FCE9F1', '#C05A8A') if a == 'Trigger' else ('#FFFFFF', '#7FB0D6')
        g.append(blk(x, 128, 262, 96, ic, a, b, fill, st, '#2A7AB8' if a != 'Trigger' else '#C05A8A'))
    g.append(T(1015, 296, 'workloads, triggers and metrics — as data only', 19, 600, '#2A7AB8', 'middle', extra='font-style="italic"'))
    # validation gates
    g.append(panel(290, 350, 1450, 120, '#FFF7E6', 'Validation gates', '#C9A44A'))
    for i, s in enumerate(['workload compiles', 'metric checked', 'explanation checked', 'hashes logged']):
        x = 345 + i * 350
        g.append(f'<rect x="{x}" y="{402}" width="300" height="48" rx="24" fill="#FFFFFF" stroke="#E2C27A" stroke-width="1.8"/>' + mdi('shield-check-outline', x + 14, 410, 32, '#9A6A12') + T(x + 56, 434, s, 20, 600, INK))
    g.append(arr(1015, 320, 1015, 398, 'arb', '#2A7AB8', 3))
    # deterministic core
    g.append(panel(290, 500, 1450, 470, '#EAF6EC', 'Deterministic core: decides', '#4E9F6A'))
    row1 = [('cog-outline', 'Synthesis', 'Yosys · GHDL'), ('sitemap-outline', 'Fault universe', 'collapse · cone'), ('needle', 'Instrument', 'hooks · T0 gate'),
            ('square-wave', 'Simulate', 'Verilator ‖ Icarus'), ('history', 'Follow-up', 'latent fate')]
    for i, (ic, a, b) in enumerate(row1):
        x = 315 + i * 284
        g.append(blk(x, 568, 256, 104, ic, a, b, '#FFFFFF', '#8CC59C', '#2E7D4F'))
        if i < 4: g.append(arr(x + 258, 620, x + 282, 620))
    row2 = [('function-variant', 'Formal oracle', 'ABC · witness replay'), ('chart-bell-curve', 'Exact statistics', 'Clopper–Pearson · hypergeometric'),
            ('certificate-outline', 'Certified report', 'bracket · 11 classes · AVF')]
    xs2 = [1190, 760, 315]; ws2 = [520, 400, 410]
    for (ic, a, b), x, w in zip(row2, xs2, ws2):
        fill, st = ('#E2F3E6', '#4E9F6A') if a == 'Certified report' else ('#FFFFFF', '#8CC59C')
        g.append(blk(x, 760, w, 104, ic, a, b, fill, st, '#2E7D4F'))
    g.append(f'<path d="M 1450 674 L 1450 758" stroke="{INK}" stroke-width="2.6" fill="none" marker-end="url(#ar)"/>')
    g.append(arr(1188, 812, 1164, 812)); g.append(arr(758, 812, 729, 812))
    g.append(arr(1015, 470, 1015, 560, 'ar', INK, 3))
    g.append(T(1030, 492, 'admitted proposals', 17, 600, '#4A5A6E'))
    # outputs + feedback
    g.append(panel(1780, 70, 200, 900, '#F1EEF8', 'OUTPUTS', '#8A73B8'))
    for i, (ic, a, b) in enumerate([('file-certificate-outline', 'Report', 'md · html · json'), ('chart-box-outline', 'Bracket', '[lower, upper]'), ('tag-multiple-outline', 'Classes', '11 + 3-class view')]):
        y = 160 + i * 270
        g.append(f'<g filter="url(#sh)"><rect x="1800" y="{y}" width="160" height="170" rx="12" fill="#E4DCF2" stroke="#8A73B8" stroke-width="2"/></g>')
        g.append(mdi(ic, 1850, y + 18, 60, '#5B3F92') + T(1880, y + 112, a, 23, 700, INK, 'middle') + T(1880, y + 142, b, 16.5, 400, '#4B3A6E', 'middle'))
    g.append(f'<path d="M 250 620 L 312 620" stroke="{INK}" stroke-width="2.6" marker-end="url(#ar)"/>')
    g.append(f'<path d="M 726 862 L 726 905 L 1760 905 L 1760 330 L 1798 330" stroke="{INK}" stroke-width="2.6" fill="none" marker-end="url(#ar)"/>')
    g.append(f'<path d="M 1742 640 L 1765 640 L 1765 176 L 1638 176" stroke="#C05A8A" stroke-width="2.6" fill="none" stroke-dasharray="8 6" marker-end="url(#arp)"/>')
    g.append(T(1610, 950, 'undecided faults + activation / propagation diagnosis → Trigger', 18, 600, '#C05A8A', 'end', extra='font-style="italic"'))
    page(W, H, ''.join(g), 'gs_arch', 1.8)

# ------------------------------------------------------------------ certified bracket
def bracket():
    W, H = 1000, 380; g = []
    x0, x1, y = 40, 960, 140
    xd, xu = x0 + (x1 - x0) * 0.55, x0 + (x1 - x0) * 0.80
    g.append(f'<rect x="{x0}" y="{y}" width="{xd-x0}" height="80" rx="10" fill="#E9B3A8"/>' + T((x0 + xd) / 2, y + 38, 'D · proven vulnerable', 26, 700, '#7A1F12', 'middle') + T((x0 + xd) / 2, y + 66, 'replayed witness in both simulators', 18, 400, '#7A1F12', 'middle'))
    g.append(f'<rect x="{xd}" y="{y}" width="{xu-xd}" height="80" fill="#D7DEE6"/>' + T((xd + xu) / 2, y + 38, 'U · undecided', 24, 700, '#3D4B5C', 'middle') + T((xd + xu) / 2, y + 66, 'said to be so', 18, 400, '#3D4B5C', 'middle'))
    g.append(f'<rect x="{xu}" y="{y}" width="{x1-xu}" height="80" rx="10" fill="#B9E0C8"/>' + T((xu + x1) / 2, y + 38, 'R · harmless', 24, 700, '#1E5E36', 'middle') + T((xu + x1) / 2, y + 66, 'proof', 18, 400, '#1E5E36', 'middle'))
    for xx, lab, col, yy in [(xd, 'lower bound  |D| / |F|', RED, y - 40), (xu, 'upper bound  (|D| + |U|) / |F|', '#1E5E36', y + 128)]:
        g.append(f'<line x1="{xx}" y1="{y-18}" x2="{xx}" y2="{y+98}" stroke="{col}" stroke-width="3.5"/>' + T(xx, yy, lab, 22, 700, col, 'middle'))
    g.append(f'<path d="M {xd} {y+150} L {xu} {y+150}" stroke="{INK}" stroke-width="2.5"/><path d="M {xd} {y+140} L {xd} {y+160} M {xu} {y+140} L {xu} {y+160}" stroke="{INK}" stroke-width="2.5"/>')
    g.append(T((xd + xu) / 2, y + 186, 'width = what the evidence still lacks', 20, 600, MUTED, 'middle', extra='font-style="italic"'))
    g.append(T(x0, 50, 'All faults F of the circuit', 22, 700, INK) + T(x0, 78, 'the true vulnerability V always lies inside the bracket', 19, 400, MUTED))
    page(W, H, ''.join(g), 'bracket', 2.2)

if __name__ == '__main__':
    farm(); gs_arch(); bracket()
    eq_png(r'n=\dfrac{N}{1+e^{2}\,\dfrac{N-1}{t^{2}\,p\,(1-p)}}', f'{OUT}/eq/leveugle.png', 40)
    eq_png(r'\frac{|D|}{|F|}\ \le\ V\ \le\ \frac{|D|+|U|}{|F|}', f'{OUT}/eq/bracket.png', 40)
    print('ok')
