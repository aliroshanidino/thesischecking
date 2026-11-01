"""Hand-drawn SVG illustration library (gradients, soft shadows) for the thesis deck."""
import re
from figkit import ICON_DIR
INK, BLUE, AMBER, RED, TEAL, MUTED = '#0F2338', '#00629B', '#E3A63B', '#B91C1C', '#0E7C86', '#6B7A90'

def mdi(name, x, y, s, fill, op=1.0):
    d = re.search(r' d="([^"]+)"', open(f'{ICON_DIR}/{name}.svg').read()).group(1)
    return f'<g transform="translate({x},{y}) scale({s/24})" opacity="{op}"><path d="{d}" fill="{fill}"/></g>'

DEFS = f'''<defs>
 <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#DDEBF7"/><stop offset="1" stop-color="#F7FAFD"/></linearGradient>
 <linearGradient id="ground" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E6EDF3"/><stop offset="1" stop-color="#D3DEE7"/></linearGradient>
 <linearGradient id="cloudG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#CFE3F4"/></linearGradient>
 <linearGradient id="rack" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#1D3B5E"/><stop offset="1" stop-color="#0F2338"/></linearGradient>
 <linearGradient id="carBody" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2F86C4"/><stop offset="1" stop-color="#00507E"/></linearGradient>
 <linearGradient id="glass" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#E8F4FC"/><stop offset="1" stop-color="#9CC6E6"/></linearGradient>
 <linearGradient id="bldg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#C9D8E6"/><stop offset="1" stop-color="#A9BDD0"/></linearGradient>
 <linearGradient id="steel" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#7E91A6"/><stop offset="1" stop-color="#4E6278"/></linearGradient>
 <linearGradient id="fov" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#E3A63B" stop-opacity=".55"/><stop offset="1" stop-color="#E3A63B" stop-opacity="0"/></linearGradient>
 <linearGradient id="fovDown" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E3A63B" stop-opacity=".5"/><stop offset="1" stop-color="#E3A63B" stop-opacity="0"/></linearGradient>
 <linearGradient id="scale" x1="0" x2="1"><stop offset="0" stop-color="#00629B"/><stop offset=".55" stop-color="#0E7C86"/><stop offset="1" stop-color="#B91C1C"/></linearGradient>
 <radialGradient id="iris" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#0B2236"/><stop offset=".35" stop-color="#0B2236"/><stop offset=".36" stop-color="#2F86C4"/><stop offset="1" stop-color="#0E4F7E"/></radialGradient>
 <radialGradient id="eyeball" cx=".45" cy=".4" r=".6"><stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#F1D9D2"/></radialGradient>
 <filter id="sh" x="-20%" y="-20%" width="140%" height="160%"><feDropShadow dx="0" dy="6" stdDeviation="7" flood-color="#0F2338" flood-opacity=".18"/></filter>
 <filter id="shs" x="-20%" y="-20%" width="140%" height="160%"><feDropShadow dx="0" dy="2" stdDeviation="2.5" flood-color="#0F2338" flood-opacity=".22"/></filter>
</defs>'''

def cloud(cx, cy, s=1.0):
    c = [(-120, 20, 62), (-55, -30, 80), (35, -48, 92), (118, 0, 70), (60, 38, 60), (-40, 40, 62), (160, 38, 44), (-160, 45, 40)]
    circles = ''.join(f'<circle cx="{cx+dx*s}" cy="{cy+dy*s}" r="{r*s}"/>' for dx, dy, r in c)
    base = f'<rect x="{cx-170*s}" y="{cy+20*s}" width="{340*s}" height="{66*s}" rx="{33*s}"/>'
    return f'<g filter="url(#sh)"><g fill="url(#cloudG)" stroke="#A9CBE6" stroke-width="2">{circles}{base}</g><g fill="url(#cloudG)">{circles}{base}</g></g>'

def rack(x, y, w=46, h=92):
    leds = ''.join(f'<rect x="{x+6}" y="{y+8+i*16}" width="{w-12}" height="9" rx="2" fill="#24496F"/><circle cx="{x+w-11}" cy="{y+12.5+i*16}" r="2.2" fill="{"#4FD1C5" if i%2==0 else "#E3A63B"}"/>' for i in range(5))
    return f'<g filter="url(#shs)"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="url(#rack)"/>{leds}</g>'

def building(x, y, w, h, floors=6, cols=4):
    win = ''.join(f'<rect x="{x+10+c*((w-20)/cols)}" y="{y+14+f*((h-26)/floors)}" width="{(w-20)/cols-8}" height="{(h-26)/floors-8}" rx="2" fill="{"#EAF4FC" if (f+c)%3 else "#FFE7B3"}" opacity=".95"/>' for f in range(floors) for c in range(cols))
    return f'<g filter="url(#sh)"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="url(#bldg)"/><rect x="{x}" y="{y}" width="{w}" height="8" rx="3" fill="#8DA4BA"/>{win}</g>'

def tower(x, base_y, h=230):
    top = base_y - h
    lines = f'<path d="M{x-34},{base_y} L{x-6},{top} M{x+34},{base_y} L{x+6},{top}" stroke="url(#steel)" stroke-width="6" stroke-linecap="round"/>'
    for i in range(1, 7):
        y1 = base_y - h * i / 7; y0 = base_y - h * (i - 1) / 7
        wl = 34 - 28 * (i - 1) / 7; wh = 34 - 28 * i / 7
        lines += f'<path d="M{x-wl},{y0} L{x+wh},{y1} M{x+wl},{y0} L{x-wh},{y1} M{x-wh},{y1} L{x+wh},{y1}" stroke="#7E91A6" stroke-width="2.4"/>'
    ants = f'<rect x="{x-20}" y="{top+10}" width="9" height="34" rx="3" fill="#5A6E84"/><rect x="{x+11}" y="{top+10}" width="9" height="34" rx="3" fill="#5A6E84"/><rect x="{x-4}" y="{top-6}" width="8" height="30" rx="3" fill="#5A6E84"/>'
    waves = ''.join(f'<path d="M{x-28-r},{top+20-r*0.6} A{r+28},{r+28} 0 0 0 {x-28-r},{top+20+r*0.6}" stroke="#00629B" stroke-opacity="{0.75-k*0.2}" stroke-width="3" fill="none"/>'
                    f'<path d="M{x+28+r},{top+20-r*0.6} A{r+28},{r+28} 0 0 1 {x+28+r},{top+20+r*0.6}" stroke="#00629B" stroke-opacity="{0.75-k*0.2}" stroke-width="3" fill="none"/>' for k, r in enumerate((10, 26, 42)))
    cab = f'<g filter="url(#shs)"><rect x="{x-96}" y="{base_y-62}" width="54" height="62" rx="5" fill="url(#rack)"/>' + ''.join(f'<rect x="{x-90}" y="{base_y-54+i*13}" width="42" height="7" rx="2" fill="#24496F"/><circle cx="{x-52}" cy="{base_y-50.5+i*13}" r="2" fill="#4FD1C5"/>' for i in range(4)) + '</g>'
    return f'<g>{lines}{ants}{waves}{cab}</g>'

def street_lamp(x, base_y, h=170):
    return (f'<g><rect x="{x-4}" y="{base_y-h}" width="8" height="{h}" rx="3" fill="url(#steel)"/>'
            f'<path d="M{x},{base_y-h+6} q30,-26 64,-10" stroke="#5A6E84" stroke-width="7" fill="none" stroke-linecap="round"/>'
            f'<path d="M{x+50},{base_y-h+3} h34 l-6,12 h-22 z" fill="#4E6278"/><ellipse cx="{x+67}" cy="{base_y-h+17}" rx="16" ry="5" fill="#FFE7B3"/>'
            f'<path d="M{x+51},{base_y-h+17} L{x+33},{base_y-h+80} L{x+101},{base_y-h+80} L{x+83},{base_y-h+17} z" fill="#FFE7B3" opacity=".35"/>'
            f'<g filter="url(#shs)"><rect x="{x-17}" y="{base_y-h+58}" width="34" height="40" rx="4" fill="url(#rack)"/><circle cx="{x}" cy="{base_y-h+70}" r="3" fill="#4FD1C5"/><rect x="{x-10}" y="{base_y-h+80}" width="20" height="5" rx="2" fill="#24496F"/></g>'
            f'<rect x="{x-14}" y="{base_y-6}" width="28" height="8" rx="3" fill="#5A6E84"/></g>')

def car(x, y, s=1.0, cam=True):
    """side-view car, x,y = rear-bottom of body."""
    S = lambda v: v * s
    body = f'M{x},{y} L{x},{y-S(34)} Q{x+S(4)},{y-S(46)} {x+S(26)},{y-S(48)} L{x+S(70)},{y-S(50)} Q{x+S(96)},{y-S(80)} {x+S(128)},{y-S(82)} L{x+S(186)},{y-S(82)} Q{x+S(214)},{y-S(80)} {x+S(238)},{y-S(52)} L{x+S(282)},{y-S(46)} Q{x+S(300)},{y-S(42)} {x+S(302)},{y-S(26)} L{x+S(302)},{y} Z'
    win = f'M{x+S(84)},{y-S(52)} Q{x+S(104)},{y-S(74)} {x+S(130)},{y-S(75)} L{x+S(152)},{y-S(75)} L{x+S(152)},{y-S(52)} Z M{x+S(160)},{y-S(52)} L{x+S(160)},{y-S(75)} L{x+S(184)},{y-S(75)} Q{x+S(204)},{y-S(73)} {x+S(222)},{y-S(52)} Z'
    wheel = lambda cx: f'<circle cx="{cx}" cy="{y}" r="{S(26)}" fill="#1B2733"/><circle cx="{cx}" cy="{y}" r="{S(13)}" fill="#C8D3DD"/><circle cx="{cx}" cy="{y}" r="{S(4)}" fill="#5A6E84"/>'
    camg = (f'<path d="M{x+S(196)},{y-S(86)} L{x+S(470)},{y-S(150)} L{x+S(470)},{y+S(20)} Z" fill="url(#fov)"/>'
            f'<rect x="{x+S(182)}" y="{y-S(94)}" width="{S(22)}" height="{S(12)}" rx="3" fill="#0F2338"/><circle cx="{x+S(202)}" cy="{y-S(88)}" r="{S(4)}" fill="#E3A63B"/>') if cam else ''
    return (f'<g>{camg}<ellipse cx="{x+S(151)}" cy="{y+S(26)}" rx="{S(160)}" ry="{S(9)}" fill="#0F2338" opacity=".18"/>'
            f'<g filter="url(#sh)"><path d="{body}" fill="url(#carBody)"/></g><path d="{win}" fill="url(#glass)"/>'
            f'<rect x="{x+S(290)}" y="{y-S(38)}" width="{S(12)}" height="{S(9)}" rx="2" fill="#FFE7B3"/><rect x="{x-S(2)}" y="{y-S(34)}" width="{S(8)}" height="{S(9)}" rx="2" fill="#E05A47"/>'
            f'{wheel(x+S(62))}{wheel(x+S(238))}</g>')

def drone(cx, cy, s=1.0, cam=True):
    S = lambda v: v * s
    arms = f'<path d="M{cx-S(70)},{cy-S(8)} L{cx+S(70)},{cy-S(8)}" stroke="#1D3B5E" stroke-width="{S(8)}" stroke-linecap="round"/>'
    rotors = ''.join(f'<rect x="{cx+dx-S(4)}" y="{cy-S(22)}" width="{S(8)}" height="{S(16)}" rx="2" fill="#1D3B5E"/>'
                     f'<ellipse cx="{cx+dx}" cy="{cy-S(24)}" rx="{S(44)}" ry="{S(6)}" fill="#9CC6E6" opacity=".55"/>'
                     f'<ellipse cx="{cx+dx}" cy="{cy-S(24)}" rx="{S(44)}" ry="{S(6)}" fill="none" stroke="#00629B" stroke-opacity=".5" stroke-width="1.5"/>' for dx in (-S(70), S(70)))
    body = f'<g filter="url(#sh)"><rect x="{cx-S(40)}" y="{cy-S(18)}" width="{S(80)}" height="{S(26)}" rx="{S(12)}" fill="url(#carBody)"/></g><rect x="{cx-S(20)}" y="{cy-S(13)}" width="{S(40)}" height="{S(7)}" rx="3" fill="url(#glass)"/>'
    gimbal = f'<rect x="{cx-S(9)}" y="{cy+S(8)}" width="{S(18)}" height="{S(14)}" rx="3" fill="#0F2338"/><circle cx="{cx}" cy="{cy+S(18)}" r="{S(4)}" fill="#E3A63B"/>'
    fovg = f'<path d="M{cx},{cy+S(22)} L{cx-S(95)},{cy+S(190)} L{cx+S(95)},{cy+S(190)} Z" fill="url(#fovDown)"/>' if cam else ''
    return f'<g>{fovg}{arms}{rotors}{body}{gimbal}</g>'

def eye_implant(cx, cy, r=92):
    """eye cross-section with an epiretinal implant chip and a glasses camera."""
    return (f'<g><circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#eyeball)" stroke="#E3B7AA" stroke-width="3"/>'
            f'<path d="M{cx+r*0.15},{cy-r*0.98} A{r},{r} 0 0 1 {cx+r*0.15},{cy+r*0.98}" fill="none" stroke="#C0392B" stroke-width="7" stroke-opacity=".55"/>'
            f'<ellipse cx="{cx-r*0.93}" cy="{cy}" rx="{r*0.16}" ry="{r*0.42}" fill="url(#iris)"/>'
            f'<path d="M{cx-r*1.02},{cy-r*0.45} Q{cx-r*1.25},{cy} {cx-r*1.02},{cy+r*0.45}" fill="#DCEEF9" stroke="#9CC6E6" stroke-width="2"/>'
            f'<g filter="url(#shs)"><rect x="{cx+r*0.62}" y="{cy-r*0.24}" width="{r*0.26}" height="{r*0.48}" rx="4" fill="#0F2338" transform="rotate(-6 {cx+r*0.75} {cy})"/></g>'
            + ''.join(f'<circle cx="{cx+r*0.71}" cy="{cy-r*0.16+i*r*0.1}" r="2.2" fill="#E3A63B"/>' for i in range(4)) +
            f'<path d="M{cx+r*0.88},{cy+r*0.05} C{cx+r*1.2},{cy+r*0.2} {cx+r*1.3},{cy+r*0.6} {cx+r*1.5},{cy+r*0.75}" stroke="#E3A63B" stroke-width="3" fill="none" stroke-dasharray="6 5"/>'
            f'<path d="M{cx-r*1.9},{cy} L{cx-r*1.2},{cy-r*0.25} L{cx-r*1.2},{cy+r*0.25} Z" fill="#FFE7B3" opacity=".7"/></g>')

def label(x, y, title, lines, col, anchor='start', w=230):
    tx = x if anchor == 'start' else x - w
    body = ''.join(f'<tspan x="{tx+16}" dy="{19 if i else 0}">{l}</tspan>' for i, l in enumerate(lines))
    h = 40 + 19 * len(lines)
    return (f'<g filter="url(#shs)"><rect x="{tx}" y="{y}" width="{w}" height="{h}" rx="12" fill="#FFFFFF" stroke="{col}" stroke-opacity=".35"/>'
            f'<rect x="{tx}" y="{y}" width="6" height="{h}" rx="3" fill="{col}"/></g>'
            f'<text x="{tx+16}" y="{y+24}" class="sf" font-weight="600" font-size="17" fill="{col}">{title}</text>'
            f'<text x="{tx+16}" y="{y+46}" class="ss" font-size="14.5" fill="{INK}">{body}</text>')
