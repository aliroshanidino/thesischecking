"""Remaining figures: BioVision architecture (built vs planned), result/conclusion divider heroes, equations."""
import sys; sys.path.insert(0, '.')
from fig_phase2 import T, page, INK, BLUE, AMBER, RED, TEAL, MUTED
from art import mdi
from eqkit import eq_png
OUT = '/tmp/claude-0/-home-user/2f31366c-8266-5d82-b134-0e1ce71114f5/scratchpad/deck/figs'

def bio_arch():
    W, H = 2200, 1000; g = []
    def panel(x, y, w, h, fill, title, col):
        return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{fill}" stroke="{col}" stroke-width="2" stroke-dasharray="9 6"/>'
                + T(x + 18, y + 32, title, 22, 600, INK, 'start', 'sf', 'font-style="italic"'))
    def blk(x, y, w, h, t1, t2, built, col):
        st = f'stroke="{col}" stroke-width="2.4"' if built else f'stroke="{col}" stroke-width="2.2" stroke-dasharray="7 5"'
        fill = '#FFFFFF' if built else '#FFFFFF" fill-opacity="0.55'
        return (f'<g filter="url(#sh)"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="11" fill="{fill}" {st}/></g>'
                + T(x + w / 2, y + h / 2 - 2, t1, 21, 700, INK if built else '#56657A', 'middle') + T(x + w / 2, y + h / 2 + 22, t2, 16, 400, MUTED, 'middle'))
    def arr(x1, y1, x2, y2, col=INK, dash=''):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        return f'<path d="M {x1} {y1} L {x2} {y2}" stroke="{col}" stroke-width="2.4"{d} fill="none" marker-end="url(#ar)"/>'
    G, B, O, P = '#5E9E4F', '#2A7AB8', '#C98A1E', '#7A5AA8'
    g.append(panel(20, 60, 300, 900, '#F5F5F5', 'Retina emulator', '#9AA6B2'))
    g.append(panel(340, 60, 230, 900, '#EEF7EC', 'LGN (relay)', G))
    g.append(panel(590, 60, 520, 900, '#F7F9FC', 'V1 · V2 (shared)', '#8EA4BB'))
    g.append(panel(1130, 60, 560, 440, '#EAF2FB', 'Ventral stream · what', B))
    g.append(panel(1130, 520, 560, 440, '#FDF3E6', 'Dorsal stream · where / how', O))
    g.append(panel(1710, 60, 470, 900, '#F3EEF9', 'Selection · goal · memory', P))
    rows = [(150, 'P', 'L/M opponent'), (440, 'K', 'S − Y'), (760, 'M', 'events (Δ log Y)')]
    for y, ch, sub in rows:
        g.append(blk(45, y, 250, 96, f'{ch} channel', sub, True, '#7E8B98'))
        g.append(blk(360, y, 190, 96, f'LGN · {ch}', 'w = 1, gated', True, G))
        g.append(arr(297, y + 48, 357, y + 48))
    g.append(blk(610, 150, 230, 96, 'V1 · S1 / C1', 'P ⊕ K · STDP', True, B))
    g.append(blk(860, 110, 230, 84, 'V2 thin', 'surface colour', True, B))
    g.append(blk(860, 214, 230, 84, 'V2 pale', 'corners · junctions', True, B))
    g.append(blk(610, 760, 230, 96, 'V1 · motion', '8 dirs × 3 speeds', False, O))
    g.append(blk(860, 760, 230, 96, 'V2 thick', 'pooled motion', False, O))
    for y in (198, 488): g.append(arr(552, y if y == 198 else 488, 607, 198))
    g.append(arr(552, 808, 607, 808)); g.append(arr(842, 190, 857, 152)); g.append(arr(842, 206, 857, 256)); g.append(arr(842, 808, 857, 808))
    g.append(blk(1150, 110, 250, 96, 'V4 · S3 / C3', 'shape × colour', True, B))
    g.append(blk(1150, 240, 250, 96, 'IT · S4 / C4', 'location kept', True, B))
    g.append(blk(1420, 110, 250, 96, 'Readout (image)', 'first spike · R-STDP', True, B))
    g.append(blk(1420, 240, 250, 96, 'Readout D_c(u)', 'location-wise', False, B))
    g.append(blk(1420, 370, 250, 96, 'Gist (wave 1)', 'is there a car?', False, B))
    g.append(arr(1092, 160, 1147, 158)); g.append(arr(1275, 208, 1275, 237)); g.append(arr(1402, 270, 1418, 160)); g.append(arr(1402, 288, 1417, 288)); g.append(arr(1545, 338, 1545, 367))
    g.append(blk(1150, 570, 250, 96, 'MT', 'velocity v(u)', False, O))
    g.append(blk(1150, 700, 250, 96, 'V3 · MST', 'salience · heading', False, O))
    g.append(blk(1420, 640, 250, 120, 'Depth fusion', 'five monocular cues', False, O))
    g.append(arr(1092, 808, 1147, 620)); g.append(arr(1275, 668, 1275, 697)); g.append(arr(1402, 748, 1417, 710))
    g.append(blk(1730, 110, 430, 110, 'Priority map (LIP)', 'k-WTA replaces NMS', False, P))
    g.append(blk(1730, 260, 430, 110, 'Attention a(x)', 'fed back to LGN, wave n+1', False, P))
    g.append(blk(1730, 410, 430, 130, 'PFC', 'goal · object files · reward', False, P))
    g.append(blk(1730, 600, 430, 150, 'Object tokens', 'position · mask · class · depth · velocity · id', False, P))
    g.append(arr(1672, 158, 1727, 160)); g.append(arr(1945, 222, 1945, 257)); g.append(arr(1945, 542, 1945, 597)); g.append(arr(1672, 700, 1727, 680))
    g.append(f'<path d="M 1730 315 L 1700 315 L 1700 40 L 530 40 L 530 148" stroke="{RED}" stroke-width="2.4" stroke-dasharray="8 6" fill="none" marker-end="url(#ar)"/>')
    g.append(T(1080, 32, 'attention feedback → all LGN sheets (next wave)', 18, 600, RED, 'middle', extra='font-style="italic"'))
    # legend
    g.append(f'<rect x="40" y="972" width="38" height="20" rx="5" fill="#FFFFFF" stroke="{INK}" stroke-width="2.4"/>' + T(88, 989, 'built and tested (Phase 0 – 1)', 18, 600, INK))
    g.append(f'<rect x="400" y="972" width="38" height="20" rx="5" fill="#FFFFFF" stroke="#56657A" stroke-width="2.2" stroke-dasharray="6 4"/>' + T(448, 989, 'planned (Phase 2 – 5)', 18, 600, '#56657A'))
    g.append(T(2160, 989, 'wave-based TTFS · ≤ 1 spike per neuron per wave · local learning only · no multipliers', 18, 400, MUTED, 'end', extra='font-style="italic"'))
    page(W, H, ''.join(g), 'bio_arch', 1.7)

def hero(name, items, caption):
    W, H = 760, 700; g = [f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>']
    for k, (ic, col, tint, t1, t2) in enumerate(items):
        rows = (len(items) + 1) // 2; y0 = (H - 40 - rows * 205) / 2
        x = 40 + (k % 2) * 350; y = y0 + (k // 2) * 205
        g.append(f'<g filter="url(#sh)"><rect x="{x}" y="{y}" width="330" height="185" rx="22" fill="#FFFFFF" stroke="#D5E1EC" stroke-width="2"/></g>')
        g.append(f'<circle cx="{x+62}" cy="{y+66}" r="38" fill="{tint}"/>' + mdi(ic, x + 38, y + 42, 48, col))
        g.append(T(x + 116, y + 62, t1, 23, 700, INK, cls='sf') + T(x + 116, y + 90, t2, 17, 400, MUTED))
    g.append(T(W / 2, H - 22, caption, 20, 400, MUTED, 'middle'))
    page(W, H, ''.join(g), name, 2.5)

if __name__ == '__main__':
    bio_arch()
    hero('hero_results', [('chip', '#0E7C86', '#E0F1F2', 'Silicon cost', 'Sky130 PPA'), ('shield-check-outline', '#B91C1C', '#F9E5E5', 'Reliability', 'fault outcomes · RFoM'),
                          ('school-outline', '#9A6A12', '#FBF1DE', 'Learning', 'on-chip case study'), ('magnify-scan', '#00629B', '#E3EEF7', 'Assessment', 'GateScan brackets'),
                          ('eye-outline', '#6B4FA0', '#EEE9F6', 'Vision', 'BioVision so far'), ('check-decagram-outline', '#2E7D4F', '#E2F3E6', 'Every number', 'traced to its source')],
         'measured on the netlist, in silicon flow, and on data')
    hero('hero_concl', [('flag-checkered', '#0E7C86', '#E0F1F2', 'What we built', 'core · campaign · vision'), ('lightbulb-on-outline', '#9A6A12', '#FBF1DE', 'What we learned', 'adapt, don’t replicate'),
                        ('map-marker-path', '#00629B', '#E3EEF7', 'Road ahead', 'detection · system FT'), ('file-document-multiple-outline', '#6B4FA0', '#EEE9F6', 'Outputs', 'papers · open code')],
         'one dependable extreme-edge vision device')
    eq_png(r'\theta_i\;\leftarrow\;\theta_i+\eta\,\theta_0\,\frac{z_i-\rho}{\rho},\qquad \eta=\rho=2^{-5}', f'{OUT}/eq/homeo2.png', 40)
    eq_png(r't=T\Big(1-\frac{r}{r_{max}}\Big),\qquad r=\frac{\lfloor D\rfloor_{+}}{\varepsilon+G*Y}', f'{OUT}/eq/latency.png', 40)
    eq_png(r'\mathrm{RFoM}_i=\frac{\mathrm{AVF}_{base}/\mathrm{AVF}_i}{N_i/N_{base}}', f'{OUT}/eq/rfom.png', 40)
    print('ok')
