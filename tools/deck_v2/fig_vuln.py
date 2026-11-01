import sys; sys.path.insert(0, '.')
from figkit import icon, render_html, FONT_CSS
from art import DEFS
W, H = 1560, 620
INK, BLUE, AMBER, RED, TEAL, MUTED, LINE = '#0F2338', '#00629B', '#E3A63B', '#B91C1C', '#0E7C86', '#6B7A90', '#D5E1EC'
# ---------- Izhikevich simulation (regular spiking), fault applied at t = 100 ms
def izh(mode, T=300, dt=0.25):
    a, b, c, d = 0.02, 0.2, -65, 8
    v, u = -65.0, b * -65.0; out = []
    for k in range(int(T / dt)):
        t = k * dt; I = 10.0
        if t >= 100:
            if mode == 'sa1': I = 10.0 + 60.0          # persistent parasitic current
            if mode == 'sa0': I = 0.0                  # drive removed
        v += dt * (0.04 * v * v + 5 * v + 140 - u + I); u += dt * a * (b * v - u)
        if v >= 30: out.append((t, 30)); v, u = c, u + d
        else: out.append((t, v))
    return out
def trace(data, x0, y0, w, h, col):
    pts = ' '.join(f'{x0 + t / 300 * w:.1f},{y0 + (30 - min(v, 30)) / 110 * h:.1f}' for t, v in data[::2])
    return f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="2" stroke-linejoin="round"/>'
g = [DEFS]
# ---------- left: accelerator architecture
g.append(f'<rect x="0" y="0" width="930" height="{H}" rx="22" fill="#FFFFFF" stroke="{LINE}" stroke-width="1.5"/>')
g.append(f'<text x="34" y="46" class="sf" font-size="22" font-weight="600" fill="{INK}">Time-multiplexed SNN accelerator (ODIN-style)</text>')
g.append(f'<defs><marker id="arr" markerWidth="10" markerHeight="10" refX="6" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{RED}"/></marker>'
         f'<marker id="arrT" markerWidth="10" markerHeight="10" refX="6" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{TEAL}"/></marker></defs>')
def block(x, y, w, h, ic, title, sub, col, fill='#F3F7FB'):
    return (f'<g filter="url(#shs)"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{fill}" stroke="{col}" stroke-opacity=".45" stroke-width="2"/></g>'
            + icon(ic, 40, col, x=x + 20, y=y + h / 2 - 20) +
            f'<text x="{x+74}" y="{y+h/2-4}" class="sf" font-size="20" font-weight="600" fill="{INK}">{title}</text>'
            f'<text x="{x+74}" y="{y+h/2+20}" class="ss" font-size="15.5" fill="{MUTED}">{sub}</text>')
CX, CY, R = 690, 250, 128
# bus: three blocks -> vertical bus -> core
for yy in (132, 242, 352):
    g.append(f'<line x1="400" y1="{yy}" x2="470" y2="{yy}" stroke="#9DB4CB" stroke-width="3" stroke-linecap="round"/>')
g.append(f'<line x1="470" y1="132" x2="470" y2="352" stroke="#9DB4CB" stroke-width="3" stroke-linecap="round"/>')
g.append(f'<line x1="470" y1="{CY}" x2="{CX-100}" y2="{CY}" stroke="#9DB4CB" stroke-width="3" stroke-linecap="round"/>')
g.append(block(40, 86, 360, 92, 'cog', 'Central controller', 'FSM · scheduler', BLUE))
g.append(block(40, 196, 360, 92, 'lan', 'Network-on-chip', 'AER spike routing', BLUE))
g.append(block(40, 306, 360, 92, 'memory', 'State & weight memory', 'neuron states · synaptic weights', BLUE))
# fault arrow (drawn before the ring so the ring sits on top)
g.append(f'<path d="M 470 488 C 545 488 590 430 622 {CY+66}" stroke="{RED}" stroke-width="3.2" fill="none" marker-end="url(#arr)"/>')
# neuron core (highlighted)
g.append(f'<circle cx="{CX}" cy="{CY}" r="104" fill="{RED}" opacity=".07"/>')
g.append(f'<g filter="url(#sh)"><rect x="{CX-100}" y="{CY-62}" width="200" height="124" rx="20" fill="#FFFFFF" stroke="{RED}" stroke-width="3"/></g>')
g.append(icon('chip', 50, RED, x=CX-25, y=CY-54))
g.append(f'<text x="{CX}" y="{CY+22}" text-anchor="middle" class="sf" font-size="20" font-weight="600" fill="{RED}">Neuron core</text>')
g.append(f'<text x="{CX}" y="{CY+45}" text-anchor="middle" class="ss" font-size="15" fill="{INK}">one datapath · 1-cycle update</text>')
# ring of virtual neurons served in turn by the single core
import math
for k in range(16):
    an = math.radians(11.25 + k * 22.5); x = CX + R * math.cos(an); y = CY + R * math.sin(an)
    g.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="9" fill="#FFFFFF" stroke="{TEAL}" stroke-width="2.5"/>')
a0, a1, RA = math.radians(-150), math.radians(-40), R + 24
g.append(f'<path d="M {CX+RA*math.cos(a0):.1f} {CY+RA*math.sin(a0):.1f} A {RA} {RA} 0 0 1 {CX+RA*math.cos(a1):.1f} {CY+RA*math.sin(a1):.1f}" '
         f'stroke="{TEAL}" stroke-width="2.6" fill="none" marker-end="url(#arrT)"/>')
g.append(f'<text x="912" y="{CY+R+56}" text-anchor="end" class="ss" font-size="16" font-weight="700" fill="{TEAL}">time-multiplexed: one core serves</text>')
g.append(f'<text x="912" y="{CY+R+78}" text-anchor="end" class="ss" font-size="16" font-weight="700" fill="{TEAL}">hundreds of virtual neurons</text>')
# fault sources
src = [('factory', 'defects'), ('timer-sand', 'ageing'), ('radioactive', 'radiation'), ('thermometer-alert', 'V / T')]
for k, (ic, lab) in enumerate(src):
    x = 62 + k * 98; y = 462
    g.append(f'<circle cx="{x+22}" cy="{y+22}" r="30" fill="#FBEAEA"/>' + icon(ic, 44, RED, x=x, y=y))
    g.append(f'<text x="{x+22}" y="{y+78}" text-anchor="middle" class="ss" font-size="15" fill="{INK}">{lab}</text>')
g.append(f'<text x="40" y="590" class="ss" font-size="17" fill="{MUTED}">permanent faults → a node stuck-at-0 / stuck-at-1 inside the shared core</text>')
# ---------- right: neuron behaviour under faults
X = 960
g.append(f'<rect x="{X}" y="0" width="{W-X}" height="{H}" rx="22" fill="#FFFFFF" stroke="{LINE}" stroke-width="1.5"/>')
g.append(f'<text x="{X+30}" y="46" class="sf" font-size="22" font-weight="600" fill="{INK}">What one stuck-at does to a neuron</text>')
rows = [('healthy', 'regular, bounded firing', BLUE, None), ('sa1', 'SA1 → digital seizure', RED, None), ('sa0', 'SA0 → silence', '#7E91A6', None)]
for i, (mode, lab, col, _) in enumerate(rows):
    y0 = 76 + i * 165; bx, bw, bh = X + 30, W - X - 60, 112
    g.append(f'<text x="{bx}" y="{y0+16}" class="ss" font-size="16.5" font-weight="700" fill="{col}">{lab}</text>')
    g.append(f'<rect x="{bx}" y="{y0+26}" width="{bw}" height="{bh}" rx="10" fill="#F6F9FC"/>')
    if mode != 'healthy':
        fx = X + 40 + 100 / 300 * (W - X - 80)
        g.append(f'<rect x="{fx}" y="{y0+26}" width="{bx+bw-fx}" height="{bh}" fill="{col}" opacity=".07"/>')
        g.append(f'<line x1="{fx}" y1="{y0+26}" x2="{fx}" y2="{y0+26+bh}" stroke="{col}" stroke-width="2" stroke-dasharray="5 4"/>')
        g.append(f'<text x="{bx+bw}" y="{y0+16}" text-anchor="end" class="ss" font-size="15.5" font-weight="700" fill="{col}">fault injected ⤓</text>')
    g.append(trace(izh(mode), X + 40, y0 + 31, W - X - 80, bh - 10, col))
# time axis under the last row
ax_y = 76 + 2 * 165 + 26 + 112 + 8
for tms in (0, 100, 200, 300):
    tx = X + 40 + tms / 300 * (W - X - 80)
    g.append(f'<line x1="{tx:.1f}" y1="{ax_y}" x2="{tx:.1f}" y2="{ax_y+6}" stroke="{MUTED}" stroke-width="1.5"/>')
    g.append(f'<text x="{tx:.1f}" y="{ax_y+22}" text-anchor="middle" class="ss" font-size="15" fill="{MUTED}">{tms}{" ms" if tms == 300 else ""}</text>')
g.append(f'<text x="{X+30}" y="{H-16}" class="ss" font-size="15.5" fill="{MUTED}">Izhikevich RS neuron (behavioural model): SA1 ≈ drive stuck high, SA0 ≈ drive lost</text>')
svg = f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">{"".join(g)}</svg>'
html = f'<!doctype html><html><head><meta charset="utf-8"><style>{FONT_CSS}*{{margin:0}}body{{width:{W}px;height:{H}px;background:transparent}}</style></head><body>{svg}</body></html>'
render_html(html, '/tmp/claude-0/-home-user/2f31366c-8266-5d82-b134-0e1ce71114f5/scratchpad/deck/figs/vuln.png', W, H, 2.4)
print('ok')
