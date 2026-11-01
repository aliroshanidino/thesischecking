import sys; sys.path.insert(0, '.')
from figkit import render_html, FONT_CSS
from art import *
OUT = '/tmp/claude-0/-home-user/2f31366c-8266-5d82-b134-0e1ce71114f5/scratchpad/deck/figs'
W, H = 640, 360
def bbox(x, y, w, h, lab, col=AMBER):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="none" stroke="{col}" stroke-width="3"/>'
            f'<rect x="{x-1.5}" y="{y-22}" width="{len(lab)*8.2+14}" height="22" rx="4" fill="{col}"/>'
            f'<text x="{x+6}" y="{y-6}" class="ss" font-weight="700" font-size="14" fill="#0F2338">{lab}</text>')
def chip(x, y, text, col):
    return (f'<g filter="url(#shs)"><rect x="{x}" y="{y}" width="{len(text)*8.6+30}" height="30" rx="15" fill="{col}"/></g>'
            f'<text x="{x+15}" y="{y+20}" class="ss" font-weight="700" font-size="15" fill="#FFFFFF">{text}</text>')
def frame(body, bg='url(#sky)'):
    return f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">{DEFS}<rect width="{W}" height="{H}" fill="{bg}"/>{body}</svg>'
def page(svg):
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>{FONT_CSS}*{{margin:0}}body{{width:{W}px;height:{H}px;background:transparent}}
    .w{{border-radius:18px;overflow:hidden;width:{W}px;height:{H}px}}</style></head><body><div class="w">{svg}</div></body></html>'''
# 1 — autonomous vehicle
GY = 250
v = [f'<rect x="0" y="{GY}" width="{W}" height="{H-GY}" fill="url(#ground)"/>',
     mdi('city-variant', 330, 70, 190, '#CBD9E6', .8), mdi('pine-tree', 560, 175, 70, '#A8C3B1'),
     f'<rect x="0" y="{GY+14}" width="{W}" height="70" fill="#3A4A5A"/>',
     ''.join(f'<rect x="{x}" y="{GY+46}" width="40" height="6" rx="3" fill="#F6F9FC" opacity=".85"/>' for x in range(10, W, 80)),
     car(30, GY+62, 0.62),
     mdi('walk', 430, GY-38, 78, '#1D3B5E'),
     f'<g transform="translate(612,{GY+12}) scale(-1,1)">' + car(0, 0, 0.33, cam=False) + '</g>',
     bbox(420, GY-46, 74, 96, 'person 0.97'), bbox(388 + 0, GY-32, 0, 0, '') if False else '',
     bbox(500, GY-24, 118, 44, 'car 0.94', '#4FD1C5'),
     chip(28, 22, 'decide in < 100 ms → brake', RED)]
render_html(page(frame(''.join(v))), f'{OUT}/app_car.png', W, H, 2.5)
# 2 — UAV over terrain, beyond coverage
t = [f'<path d="M0,250 C120,200 220,240 320,215 C430,188 520,230 640,205 L640,360 L0,360 Z" fill="#CFE0D3"/>',
     f'<path d="M0,290 C140,255 260,300 380,270 C480,248 560,280 640,262 L640,360 L0,360 Z" fill="#B7CFBD"/>',
     ''.join(mdi('pine-tree', x, y, 46, '#7FA58B') for x, y in [(40, 235), (90, 250), (520, 215), (575, 228), (300, 262)]),
     drone(300, 82, 0.8),
     bbox(232, 238, 40, 58, 'person', AMBER), mdi('walk', 230, 240, 52, '#1D3B5E'),
     bbox(330, 250, 74, 36, 'vehicle', '#4FD1C5'), f'<g transform="translate(332,282) scale(0.24)">' + car(0, 0, 1, cam=False) + '</g>',
     mdi('signal-off', 560, 24, 46, RED), f'<text x="474" y="92" class="ss" font-weight="700" font-size="15" fill="{RED}">beyond coverage</text>',
     chip(26, 22, 'detect on board, in flight', BLUE)]
render_html(page(frame(''.join(t))), f'{OUT}/app_uav.png', W, H, 2.5)
# 3 — retinal prosthesis: camera glasses -> processor -> epiretinal implant
r = [eye_implant(420, 190, 108),
     f'<g filter="url(#shs)"><rect x="40" y="132" width="150" height="58" rx="14" fill="#0F2338"/></g>',
     f'<circle cx="166" cy="161" r="16" fill="#2F86C4"/><circle cx="166" cy="161" r="7" fill="#0B2236"/>',
     f'<text x="58" y="166" class="ss" font-weight="700" font-size="15" fill="#FFFFFF">camera</text>',
     f'<path d="M190,161 C230,161 240,190 280,190" stroke="{AMBER}" stroke-width="3" fill="none" stroke-dasharray="6 5"/>',
     f'<text x="58" y="222" class="ss" font-size="14" fill="{MUTED}">glasses camera + processor</text>',
     f'<text x="500" y="72" class="ss" font-weight="700" font-size="15" fill="{RED}">epiretinal implant</text>',
     f'<path d="M560,80 L540,150" stroke="{RED}" stroke-width="1.6"/>',
     f'<text x="540" y="340" class="ss" font-size="14" fill="{MUTED}">optic nerve</text>',
     chip(26, 22, 'restore sight: ≈ +1 °C budget', RED)]
render_html(page(frame(''.join(r), bg='#FBF3F0')), f'{OUT}/app_implant.png', W, H, 2.5)
print('ok')
