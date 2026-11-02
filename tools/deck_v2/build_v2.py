"""Thesis deck v2 — built slide by slide with the user. Base: seminar deck (theme, title slide)."""
import sys, copy
sys.path.insert(0, '/tmp/claude-0/-home-user/2f31366c-8266-5d82-b134-0e1ce71114f5/scratchpad/deck')
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn

SEM = '/home/user/knowledge_base/originals/seminar_H-ASIZH_Roshani.pptx'
OUT = '/tmp/claude-0/-home-user/2f31366c-8266-5d82-b134-0e1ce71114f5/scratchpad/deck/thesis_v2.pptx'
BLUE, NAVYB, INK, MUTEB = '2F5597', '203864', '222A35', '7B93A8'

prs = Presentation(SEM)
# keep only slide 1 of the seminar (title); later slides are added by this script
lst = prs.slides._sldIdLst
for el in list(lst)[1:]:
    prs.part.drop_rel(el.get(qn('r:id'))); lst.remove(el)
s1 = prs.slides[0]
def sh(slide, sid): return next(x for x in slide.shapes if x.shape_id == sid)

# ---- Slide 1: title (seminar style)
tf9 = sh(s1, 9).text_frame
for para in list(tf9.paragraphs)[1:]: para._p.getparent().remove(para._p)
first = tf9.paragraphs[0]
for r in list(first.runs): r._r.getparent().remove(r._r)
for br in first._p.findall(qn('a:br')): first._p.remove(br)
lines = [[('Presented by   ', False, 14), ('Ali Roshani', True, 16)],
         [('Supervisors   ', False, 14), ('Dr. Mohsen Ansari', True, 14), ('  &  ', False, 14), ('Dr. Mohammad T. Manzuri Shalmani', True, 14)],
         [('Date   ', False, 14), ('Aban 1405  ·  November 2026', True, 14)]]
for i, line in enumerate(lines):
    para = first if i == 0 else tf9.add_paragraph()
    para.alignment = PP_ALIGN.LEFT; para.space_after = Pt(5)
    for t, b, sz in line:
        r = para.add_run(); r.text = t; r.font.name = 'Calibri'; r.font.size = Pt(sz); r.font.bold = b
        r.font.color.rgb = RGBColor.from_string(NAVYB)
sh(s1, 9).top = Inches(4.62); sh(s1, 9).height = Inches(1.3)
# small "M.Sc. thesis" tag under the subtitle, with an accent rule
tag = s1.shapes.add_textbox(Inches(0.55), Inches(4.12), Inches(7.9), Inches(0.32))
tf = tag.text_frame; tf.margin_left = Inches(0.05); tf.word_wrap = True; from pptx.enum.text import MSO_AUTO_SIZE; tf.auto_size = MSO_AUTO_SIZE.NONE
tf.paragraphs[0].alignment = PP_ALIGN.LEFT
r = tf.paragraphs[0].add_run(); r.text = 'M.Sc. THESIS  ·  RESEARCH PROGRESS REPORT'
r.font.name = 'Calibri'; r.font.size = Pt(11); r.font.bold = True; r.font.color.rgb = RGBColor.from_string(MUTEB)
rule = s1.shapes.add_shape(1, Inches(0.56), Inches(4.04), Inches(0.9), Inches(0.035))
rule.fill.solid(); rule.fill.fore_color.rgb = RGBColor.from_string(BLUE); rule.line.fill.background()
st = rule._element.find(qn('p:style'))
if st is not None: rule._element.remove(st)
sh(s1, 15).text_frame.paragraphs[0].runs[0].text = '1 / 30'


from dk2 import *
D = Deck(prs)
FIG = '/tmp/claude-0/-home-user/2f31366c-8266-5d82-b134-0e1ce71114f5/scratchpad/deck/figs'

# ---- Slide 2: Outline
s2 = D.new(); D.chrome(s2, None, 'Outline')
pic = picture(s2, f'{FIG}/outline.png', 1.42, 1.45, 11.5, 3.9)
for k in range(5):                       # clickable hotspots over the five stations -> section dividers
    hs = rect(s2, 1.42 + k * 2.3, 1.45, 2.3, 3.75, None); hs.name = f'HOTSPOT_{k+1}'; D.nav.append((hs, k + 1))
box = rrect(s2, 1.42, 5.55, 11.5, 0.95, PANEL, '9DBFDA', 0.12)
tb(s2, 1.62, 5.6, 1.9, 0.85, [[('THESIS STATEMENT', {'size': 9.5, 'bold': True, 'color': BLUE})]], anchor='m')
tb(s2, 3.35, 5.6, 9.45, 0.85, [[('The system can share the load, but not the responsibility: ', {'size': 14, 'color': INK, 'font': HFONT}),
     ('fault tolerance must move down the stack — from the system to the accelerator, and into the neuron.', {'size': 14, 'bold': True, 'color': BLUE, 'font': HFONT})]], anchor='m')

# ---- Slide 3: divider 01
s3 = D.new(); divider(D, s3, 1, 'Introduction', f'{FIG}/hero_intro.png')

# ---- Slide 4: thesis scope & applications  (5 sentences)
s4 = D.new(); D.chrome(s4, 1, 'Our Thesis and Where It Matters',
    footer='Safety: ISO 26262 (road vehicles)  ·  Implant thermal limit ≈ +1 °C: Kim et al., IEEE TNSRE 2007  ·  Retinal prostheses: refs. [62, 63] of Ch. 1')
th = rrect(s4, 1.42, 1.42, 11.5, 0.78, PANEL, '9DBFDA', 0.14)
tb(s4, 1.62, 1.46, 1.4, 0.7, [[('THIS THESIS', {'size': 10, 'bold': True, 'color': BLUE})]], anchor='m')
tb(s4, 2.95, 1.46, 9.85, 0.7, [[('A fault-tolerant hardware accelerator for image and video processing — ', {'size': 15, 'font': HFONT}),
                                 ('dependable vision on the device itself.', {'size': 15, 'bold': True, 'color': BLUE, 'font': HFONT})]], anchor='m')
apps = [('app_car.png', 'Autonomous vehicles', 'On-board perception must decide within milliseconds.', 'A missed obstacle is a safety failure.', BLUE),
        ('app_uav.png', 'UAVs and robots', 'Detection must keep working in flight, beyond coverage.', 'No repair until the mission ends.', TEAL),
        ('app_implant.png', 'Retinal implants', 'Artificial sight for the blind runs inside the body.', '≈ +1 °C budget; repair means surgery.', RED)]
for k, (img, h, a, b, col) in enumerate(apps):
    x = 1.42 + k * 3.9
    rrect(s4, x, 2.38, 3.7, 3.42, WHITE, LINE, 0.06)
    picture(s4, f'{FIG}/{img}', x + 0.1, 2.48, 3.5, 1.97)
    rect(s4, x + 0.18, 4.6, 0.06, 1.05, col)
    tb(s4, x + 0.32, 4.55, 3.3, 0.38, [[(h, {'size': 15, 'bold': True, 'color': col, 'font': HFONT})]])
    tb(s4, x + 0.32, 4.92, 3.3, 0.5, [[(a, {'size': 12, 'color': INK})]])
    tb(s4, x + 0.32, 5.36, 3.3, 0.35, [[(b, {'size': 11, 'italic': True, 'color': MUTED})]])
bn = rrect(s4, 1.42, 5.98, 11.5, 0.55, INK, None, 0.2)
write(bn, [[('Common need:  ', {'size': 14, 'color': WHITE, 'font': HFONT}), ('real-time · low-power · dependable', {'size': 14, 'bold': True, 'color': AMBER, 'font': HFONT}),
            ('  image processing at the extreme edge', {'size': 14, 'color': WHITE, 'font': HFONT})]], align='c', anchor='m')

# ---- Slide 5: where should the computation live?  (2 sentences + figure)
s5 = D.new(); D.chrome(s5, 1, 'Where Should the Computation Live?',
    footer='Cloudlets: Satyanarayanan 2009 · Fog: Bonomi 2012 · Edge: Shi 2016 · Platform power: Capra et al. 2020 · Implant limit: Kim et al. 2007 (thesis Table 1.1)')
picture(s5, f'{FIG}/scene.png', 1.42, 1.38, 11.5, 4.72)
bn = rrect(s5, 1.42, 6.14, 11.5, 0.52, INK, None, 0.2)
write(bn, [[('The systems answer was offloading — it quietly assumes ', {'size': 14, 'color': WHITE, 'font': HFONT}),
            ('the end device is a correct black box', {'size': 14, 'bold': True, 'color': AMBER, 'font': HFONT})]], align='c', anchor='m')

# ---- Slide 6: why offloading fails (8 groups, one short sentence each)
s6 = D.new(); D.chrome(s6, 1, 'Why Offloading Fails Safety-Critical Vision',
    footer='Dean & Barroso 2013 · Pottie & Kaiser 2000 · Pasquini et al. 2021 · Koopman & Wagner 2016 · Hochschild et al. 2021 · Dixit et al. 2021 · Baumann 2005')
IC = f'{FIG}/icons'
items = [('timer-alert-outline', 'Time & determinism', 'Latency becomes a distribution: 1 % slow servers make 63 % of requests slow.', BLUE, 'E3EEF7'),
         ('signal-off', 'Connectivity', 'Coverage gaps, jamming and tissue attenuation cut the link when it is needed most.', BLUE, 'E3EEF7'),
         ('lightning-bolt', 'Energy & heat', 'Sending 1 kbit over 100 m costs as much energy as 3 M instructions.', 'C98A1E', 'FBF1DE'),
         ('lock-open-alert-outline', 'Security & privacy', 'Every hop is an attack surface; split learning leaks private data.', RED, 'F9E5E5'),
         ('certificate-outline', 'Dependability & certification', 'An open, shared chain cannot be certified to IEC 61508 / ISO 26262.', RED, 'F9E5E5'),
         ('database-alert-outline', 'Silent data corruption', 'Even cloud cores corrupt data silently — a few per several thousand machines.', RED, 'F9E5E5'),
         ('cash-multiple', 'Scale & economics', 'Spectrum and fog / MEC infrastructure are finite and costly to run.', TEAL, 'E0F1F2'),
         ('radioactive', 'Environment & modelling', 'Radiation, heat and vibration hit the device anyway; offloading models assume it is correct.', TEAL, 'E0F1F2')]
for k, (ic, h, t, col, tint) in enumerate(items):
    cx = 1.42 + (k % 2) * 5.85; cy = 1.42 + (k // 2) * 1.16
    rrect(s6, cx, cy, 5.65, 1.04, WHITE, LINE, 0.14)
    o = oval(s6, cx + 0.18, cy + 0.2, 0.64, tint)
    picture(s6, f'{IC}/{ic}.png', cx + 0.29, cy + 0.31, 0.42, 0.42)
    tb(s6, cx + 0.98, cy + 0.08, 4.55, 0.38, [[(f'{k+1:02d}  ', {'size': 11, 'bold': True, 'color': MUTED}), (h, {'size': 15, 'bold': True, 'color': col, 'font': HFONT})]])
    tb(s6, cx + 0.98, cy + 0.44, 4.55, 0.56, [[(t, {'size': 12, 'color': INK})]])
bn = rrect(s6, 1.42, 6.12, 11.5, 0.5, INK, None, 0.2)
write(bn, [[('8 weakness groups  →  ', {'size': 14, 'color': WHITE, 'font': HFONT}),
            ('the critical perception–decision loop must close on the device itself', {'size': 14, 'bold': True, 'color': AMBER, 'font': HFONT})]], align='c', anchor='m')

# ---- Slide 7: which accelerator for the extreme edge?  (4 sentences + chart)
s7 = D.new(); D.chrome(s7, 1, 'Which Accelerator for the Extreme Edge?',
    footer='Capra et al. 2020 (platform power) · Chen et al. 2017 (Eyeriss) · Akopyan et al. 2015 (TrueNorth) · Yao et al. 2024 (Speck) · implant envelope: Kim et al. 2007')
rrect(s7, 1.42, 1.38, 6.95, 4.55, WHITE, LINE, 0.05)
picture(s7, f'{FIG}/power.png', 1.55, 1.45, 6.7, 4.42)
cands = [('chip_blue', 'Dense NPU / systolic ASIC', 'Efficient for CNNs — but computes every pixel, every frame.', BLUE, 'E3EEF7', False),
         ('grid_amber', 'QNN · TinyML', 'Quantisation and pruning shrink the model, not the dense computation.', 'C98A1E', 'FBF1DE', False),
         ('brain_teal', 'SNN · neuromorphic', 'Computes only on spikes — event-driven, sparse, mW-scale.', TEAL, 'E0F1F2', True)]
for k, (ic, h, t, col, tint, chosen) in enumerate(cands):
    y = 1.38 + k * 1.55
    rrect(s7, 8.55, y, 4.38, 1.4, 'F2FAFA' if chosen else WHITE, '7CC3C8' if chosen else LINE, 0.1, 1.5 if chosen else 0.75)
    oval(s7, 8.72, y + 0.2, 0.62, tint); picture(s7, f'{IC}/{ic}.png', 8.83, y + 0.31, 0.4, 0.4)
    tb(s7, 9.48, y + 0.14, 3.3, 0.4, [[(h, {'size': 15, 'bold': True, 'color': col, 'font': HFONT})]])
    tb(s7, 9.48, y + 0.55, 3.35, 0.8, [[(t, {'size': 12, 'color': INK})]])
    if chosen:
        bdg = rrect(s7, 11.55, y - 0.16, 1.25, 0.32, TEAL, None, 0.5)
        write(bdg, [('✓  OUR CHOICE', {'size': 9.5, 'bold': True, 'color': WHITE})], align='c', anchor='m')
bn = rrect(s7, 1.42, 6.1, 11.5, 0.52, INK, None, 0.2)
write(bn, [[('So we build our own extreme-edge device on SNN  —  ', {'size': 14, 'color': WHITE, 'font': HFONT}),
            ('local · real-time · within power and heat · accurate', {'size': 14, 'bold': True, 'color': AMBER, 'font': HFONT})]], align='c', anchor='m')

# ---- Slide 8: why dependability must be built in (figure + one banner sentence)
s8 = D.new(); D.chrome(s8, 1, 'Why Dependability Must Be Built In',
    footer='Frenkel et al. 2019 (ODIN) · Izhikevich 2003 · Baumann 2005 · Vatajelu et al. 2019 · Spyrou et al. 2021 · Hochschild et al. 2021')
picture(s8, f'{FIG}/vuln.png', 1.42, 1.36, 11.5, 4.57)
bn = rrect(s8, 1.42, 6.08, 11.5, 0.54, INK, None, 0.2)
write(bn, [[('Alone at the edge, nothing can outvote a faulty core  →  ', {'size': 14, 'color': WHITE, 'font': HFONT}),
            ('harden the shared neuron core first', {'size': 14, 'bold': True, 'color': AMBER, 'font': HFONT})]], align='c', anchor='m')

# ---- Slide 9: research gaps -> contributions (one row per gap; one sentence per answer)
s9 = D.new(); D.chrome(s9, 1, 'Research Gaps and Contributions',
    footer='Buttazzo, Hard Real-Time Computing Systems · ISO 14708-1:2014 · ISO 26262:2018 · Roshani et al., TCAS-I (submitted) · Roshani et al., GateScan, TCAD (draft)')
CON = {'C1': ('C1 · H-ASIZH neuron core', TEAL, 'Phase 1'), 'C2': ('C2 · GateScan', BLUE, 'Phase 2'),
       'C3': ('C3 · BioVision', '6B4FA0', 'Phase 3'), 'C4': ('C4 · On-chip learning', 'B7791A', 'Phase 1')}
rows9 = [('timer-alert-outline', 'No deterministic guarantees', 'deadline · power · energy · accuracy met only statistically',
          'C1', 'Deterministic by design: one-cycle update, Lyapunov-bounded, 182.8 µW for two cores.'),
         ('clipboard-alert-outline', 'Standards rarely met', 'e.g. ISO 14708: ≤ 2 °C implant heating',
          'C2', 'Certified fault brackets instead of percentages — evidence a standard can accept.'),
         ('chip', 'The device is assumed correct', 'reliability, availability, security barely studied',
          'C1', 'A self-protecting core: more than 4× better than full TMR, with one-third less silicon.'),
         ('brain', 'Neuromorphic is not mature', 'still below YOLO-class accuracy on COCO',
          'C3', 'Brain-like spiking vision with local learning: classification done, COCO detection next.'),
         ('school-outline', 'No learning in the field', 'devices drift and wear; learning stops',
          'C4', 'STDP learning on the hardened core: 1020 / 1024 neurons stay active, 81.8 % on MNIST.')]
tb(s9, 1.42, 1.3, 4.35, 0.3, [[('THE GAP', {'size': 10.5, 'bold': True, 'color': RED})]])
tb(s9, 6.42, 1.3, 6.5, 0.3, [[('OUR ANSWER', {'size': 10.5, 'bold': True, 'color': TEAL})]])
for k, (ic, h, sub, c, ans) in enumerate(rows9):
    y = 1.6 + k * 0.94
    # gap card
    rrect(s9, 1.42, y, 4.35, 0.84, WHITE, LINE, 0.12, 0.75)
    rect(s9, 1.42, y + 0.15, 0.06, 0.54, RED)
    oval(s9, 1.6, y + 0.15, 0.54, 'F9E5E5'); picture(s9, f'{IC}/g9r_{ic}.png', 1.69, y + 0.24, 0.36, 0.36)
    tb(s9, 2.25, y + 0.07, 3.48, 0.38, [[(f'G{k+1}  ', {'size': 11, 'bold': True, 'color': RED}), (h, {'size': 14, 'bold': True, 'color': INK, 'font': HFONT})]])
    tb(s9, 2.25, y + 0.45, 3.48, 0.34, [[(sub, {'size': 10.5, 'color': MUTED})]])
    # arrow
    shape(s9, MSO_SHAPE.RIGHT_ARROW, 5.88, y + 0.27, 0.42, 0.3, '9DB4CB', None)
    # answer card
    name, col, ph = CON[c]
    rrect(s9, 6.42, y, 6.5, 0.84, 'F7FBFB', 'B9DADC', 0.12, 0.75)
    pill = rrect(s9, 6.58, y + 0.1, 0.105 * len(name) * 0.68 + 0.4, 0.3, col, None, 0.5)
    write(pill, [(name, {'size': 10.5, 'bold': True, 'color': WHITE})], align='c', anchor='m')
    tb(s9, 11.6, y + 0.08, 1.2, 0.3, [[(ph, {'size': 10, 'italic': True, 'color': MUTED})]], align='r')
    tb(s9, 6.58, y + 0.43, 6.25, 0.38, [[(ans, {'size': 12.5, 'color': INK})]])
tb(s9, 1.42, 6.34, 11.5, 0.26, [[('Out of scope: security attacks and rare long-tail events.', {'size': 10.5, 'italic': True, 'color': MUTED})]])

# ---- Slide 10: divider 02 Literature Review
s10 = D.new(); divider(D, s10, 2, 'Literature Review', f'{FIG}/hero_lit.png')

# ---- Slide 11: one positioning table (2-3 works per family)
from pptx.oxml.ns import qn as _qn
from lxml import etree as _et
s11 = D.new(); D.chrome(s11, 2, 'Where This Thesis Stands',
    footer='Chen 2017 · Suh 2023 · Zhang 2018 · BYU 2026 · Frenkel 2019 · Yao 2024 · Davies 2021 · Spyrou 2021 · Putra 2022, 2023 · Guerrero-Balaguera 2025 · Spyrou 2024 · Kheradpisheh 2018 · Luo 2024')
Y, N_, P_ = '✓', '✗', '◐'
fam = {'A': ('Edge-vision\naccelerators', 'E3EEF7', BLUE), 'B': ('Fault-tolerant\naccelerators', 'E3EEF7', BLUE),
       'C': ('Neuromorphic\nprocessors', 'E0F1F2', TEAL), 'D': ('SNN fault\ntolerance', 'E0F1F2', TEAL),
       'E': ('Fault-injection\ntools', 'FBF1DE', '9A6A12'), 'F': ('Spiking vision\nsystems', 'FBF1DE', '9A6A12')}
# columns: work, edge vision, ASIC, FPGA, compute, permanent, transient, campaign, learning
data = [('A', 'Eyeriss · JSSC 2017', Y, (Y, '65 nm'), N_, 'CNN PE array', N_, N_, N_, N_),
        ('A', 'Suh et al. (UAV) · TRETS 2023', Y, N_, Y, 'CNN engine', N_, N_, N_, N_),
        ('B', 'Zhang et al. · VTS 2018', N_, (P_, 'model'), N_, 'Systolic array', (Y, 'stuck-at'), N_, 'behavioural simulation', N_),
        ('B', 'YOLO on Versal (BYU) · 2026', (P_, 'space'), N_, Y, 'CNN engine', N_, (Y, 'SEU'), 'config-memory injection + proton beam', N_),
        ('C', 'ODIN · TBioCAS 2019', (P_, 'MNIST'), (Y, '28 nm'), N_, 'Neuromorphic NPU', N_, N_, N_, Y),
        ('C', 'Speck · Nat. Commun. 2024', (Y, 'DVS'), Y, N_, 'Neuromorphic NPU', N_, N_, N_, N_),
        ('C', 'Loihi 2 · 2021', N_, (Y, 'Intel 4'), N_, 'Neuromorphic NPU', N_, N_, N_, Y),
        ('D', 'Spyrou et al. · DATE 2021', (P_, 'N-MNIST'), N_, N_, 'SW model', (Y, 'dead / sat.'), N_, 'behavioural', N_),
        ('D', 'SoftSNN · DAC 2022', (P_, 'MNIST'), (Y, '65 nm'), N_, 'Neuromorphic NPU', N_, (Y, 'soft err.'), 'behavioural', N_),
        ('D', 'RescueSNN · Front. Neuro. 2023', (P_, 'MNIST'), (Y, '65 nm'), N_, 'Neuromorphic NPU', (Y, 'stuck-at'), N_, 'behavioural', N_),
        ('E', 'ShadowFI · IEEE Access 2025', N_, (Y, 'netlists'), (Y, 'emul.'), 'GPU units', '—', '—', 'gate-level · 2-valued · SDC / DUE / masked', N_),
        ('E', 'SpikeFI · 2024', N_, N_, N_, 'GPU (SW)', '—', '—', 'software (PyTorch)', N_),
        ('F', 'Kheradpisheh et al. · 2018', N_, N_, N_, 'CPU / GPU (SW)', N_, N_, N_, (P_, 'STDP, SW')),
        ('F', 'SpikeYOLO · ECCV 2024', N_, N_, N_, 'GPU (SW)', N_, N_, N_, N_)]
thesis = ('★', 'This thesis', (Y, 'µW cores'), (Y, 'Sky130'), N_, 'Neuromorphic NPU', (Y, 'all nodes'), (P_, 'assessed'), 'gate-level · 4-valued · certified bracket', (Y, 'STDP'))
widths = [1.19, 2.12, 0.8, 0.62, 0.62, 1.22, 0.86, 0.86, 2.31, 0.9]
nrows = 2 + len(data) + 1
gt = s11.shapes.add_table(nrows, len(widths), Inches(1.42), Inches(1.32), Inches(sum(widths)), Inches(4.7))
tbl = gt.table
tp = tbl._tbl.find(_qn('a:tblPr'))
for at in ('firstRow', 'bandRow'): tp.set(at, '0')
sid = tp.find(_qn('a:tableStyleId'))
if sid is not None: sid.text = '{5940675A-B579-460E-94D1-54222C63F5DA}'   # "No Style, Table Grid"
for j, w in enumerate(widths): tbl.columns[j].width = Inches(w)
tbl.rows[0].height = Inches(0.3); tbl.rows[1].height = Inches(0.3)
for i in range(2, nrows): tbl.rows[i].height = Inches(0.268)
def _ln(cell, side, color, w):
    tcPr = cell._tc.get_or_add_tcPr()
    for old in tcPr.findall(_qn(f'a:{side}')): tcPr.remove(old)
    ln = _et.SubElement(tcPr, _qn(f'a:{side}'), w=str(int(w * 12700)))
    if color is None: _et.SubElement(ln, _qn('a:noFill'))
    else:
        sf = _et.SubElement(ln, _qn('a:solidFill')); _et.SubElement(sf, _qn('a:srgbClr'), val=color)
def cell_fmt(c, fill=None):
    c.margin_left = c.margin_right = Inches(0.05); c.margin_top = c.margin_bottom = Inches(0.01)
    c.vertical_anchor = MSO_ANCHOR.MIDDLE
    if fill: c.fill.solid(); c.fill.fore_color.rgb = RGBColor.from_string(fill)
    else: c.fill.background()
    for side in ('lnL', 'lnR', 'lnT', 'lnB'): _ln(c, side, None, 0)
def put(c, runs, align='c', fill=None):
    cell_fmt(c, fill); write(c.text_frame, [runs], align=align)
SYMC = {Y: '4E9F8C', N_: 'C8D0DA', P_: 'DDA445'}
def sym(v, bold_row=False):
    if isinstance(v, tuple):
        return [(v[0], {'size': 11, 'bold': True, 'color': SYMC[v[0]]}), (f' {v[1]}', {'size': 8, 'color': MUTED})]
    if v in SYMC: return [(v, {'size': 11, 'bold': True, 'color': SYMC[v]})]
    return [(v, {'size': 9, 'bold': bold_row, 'color': INK})]
# header
H1 = [('Family', 0), ('Work', 0), ('Edge vision', 0), ('Hardware', 1), (None, 2), ('Accelerator type', 0), ('Fault tolerance', 1), (None, 2), ('Fault-assessment campaign', 0), ('On-chip learning', 0)]
H2 = [None, None, None, 'ASIC', 'FPGA', None, 'Permanent', 'Transient', None, None]
hdr = {'size': 9.5, 'bold': True, 'color': INK}
for j, (t, kind) in enumerate(H1):
    if t is not None: put(tbl.cell(0, j), [(t, hdr)], fill='DCE6F0', align='l' if j < 2 else 'c')
    else: cell_fmt(tbl.cell(0, j), 'DCE6F0')
    sub = H2[j]
    if sub: put(tbl.cell(1, j), [(sub, {'size': 9, 'bold': True, 'color': '3D5A78'})], fill='EBF1F7')
    else: cell_fmt(tbl.cell(1, j), 'DCE6F0')
for j, (t, kind) in enumerate(H1):
    if kind == 0: tbl.cell(0, j).merge(tbl.cell(1, j))
    if kind == 1: tbl.cell(0, j).merge(tbl.cell(0, j + 1))
# body
r = 2; start = {}
for row in data:
    f = row[0]; start.setdefault(f, r)
    tint = fam[f][1]
    put(tbl.cell(r, 1), [(row[1], {'size': 9.5, 'color': INK})], align='l', fill='FFFFFF')
    for j, v in enumerate(row[2:], start=2):
        put(tbl.cell(r, j), sym(v), fill='FFFFFF', align='l' if (j == 8 and v not in SYMC) else 'c')
    for j in range(len(widths)): _ln(tbl.cell(r, j), 'lnB', 'ECF0F5', 0.6)
    r += 1
# family cells (merged)
order = list(dict.fromkeys(x[0] for x in data))
for f in order:
    r0 = start[f]; r1 = r0 + sum(1 for x in data if x[0] == f) - 1
    c = tbl.cell(r0, 0)
    for rr in range(r0, r1 + 1): cell_fmt(tbl.cell(rr, 0), fam[f][1])
    if r1 > r0: c.merge(tbl.cell(r1, 0))
    name, tint, col = fam[f]
    cell_fmt(c, tint); write(c.text_frame, [[(f'{f}  ', {'size': 10, 'bold': True, 'color': col, 'font': HFONT}), (name.split('\n')[0], {'size': 8.5, 'bold': True, 'color': INK})],
                                            [(name.split('\n')[1], {'size': 8.5, 'color': MUTED})]], align='l')
    for j in range(len(widths)): _ln(tbl.cell(r1, j), 'lnB', 'D3DEE9', 1.0)
# thesis row
put(tbl.cell(r, 0), [('★', {'size': 12, 'bold': True, 'color': AMBER})], fill='FFF7E6', align='c')
put(tbl.cell(r, 1), [('This thesis', {'size': 10.5, 'bold': True, 'color': INK, 'font': HFONT})], fill='FFF7E6', align='l')
for j, v in enumerate(thesis[2:], start=2):
    runs = sym(v, True)
    put(tbl.cell(r, j), runs, fill='FFF7E6', align='c' if j != 8 else 'l')
for j in range(len(widths)):
    _ln(tbl.cell(r, j), 'lnT', 'F1CD8A', 1.25); _ln(tbl.cell(r, j), 'lnB', 'F1CD8A', 1.25)
tb(s11, 1.42, 6.08, 11.5, 0.24, [[('✓ ', {'size': 10, 'bold': True, 'color': '4E9F8C'}), ('yes    ', {'size': 9.5, 'color': MUTED}),
                                   ('◐ ', {'size': 10, 'bold': True, 'color': 'DDA445'}), ('partial / model / assessed only    ', {'size': 9.5, 'color': MUTED}),
                                   ('✗ ', {'size': 10, 'bold': True, 'color': 'C8D0DA'}), ('no    ', {'size': 9.5, 'color': MUTED}),
                                   ('Edge vision = on a low-power edge device, not a GPU / PC  ·  NPU = neural processing unit (neuromorphic)  ·  systolic / PE array = dense DNN accelerator', {'size': 9, 'color': MUTED})]])
bn = rrect(s11, 1.42, 6.33, 11.5, 0.38, INK, None, 0.25)
write(bn, [[('Only this thesis combines ', {'size': 12.5, 'color': WHITE, 'font': HFONT}),
            ('edge vision · permanent-fault tolerance · a faithful campaign · on-chip learning', {'size': 12.5, 'bold': True, 'color': AMBER, 'font': HFONT})]], align='c', anchor='m')

# ---- Slide 12: divider 03 Methodology
s12 = D.new(); divider(D, s12, 3, 'Methodology', f'{FIG}/hero_method.png')

# ---- Slide 13: methodology roadmap (3 phases) + redrawn toolbox
s13 = D.new(); D.chrome(s13, 3, 'Our Path and Our Toolbox',
    footer='Toolbox: Yosys · OpenROAD · OpenSTA · Magic · GHDL · cocotb · Icarus Verilog · SkyWater 130 nm PDK · WSL 2 · Docker · VS Code')
road = [('PHASE 1', 'Fault-tolerant neuron core', TEAL,
         [[('Of the four vulnerable parts of an ODIN-style accelerator, we harden the Izhikevich / LIF neuron first — with Lyapunov-guided homeostasis, not redundancy.', {'size': 10, 'color': INK})],
          [('Bonus: the adaptive threshold is also a learning rule — overhead ≈ only α, β, γ.', {'size': 10, 'bold': True, 'color': '9A6A12'})]]),
        ('PHASE 2', 'Fault-assessment campaign', BLUE,
         [[('We build GLFI, grow it into GateScan, and test every node of the core with it.', {'size': 10.5, 'color': INK})]]),
        ('PHASE 3', 'Bio-inspired edge-vision network', '6B4FA0',
         [[('We scale the hardened core into a network and build BioVision on it.', {'size': 10.5, 'color': INK})]])]
cws = [4.3, 3.28, 3.28]; xs = [1.42, 1.42 + 4.3 + 0.32, 1.42 + 4.3 + 0.32 + 3.28 + 0.32]
for k, (ph, name, col, paras) in enumerate(road):
    x, cw13 = xs[k], cws[k]
    rrect(s13, x, 1.3, cw13, 1.36, WHITE, LINE, 0.1, 0.75)
    rect(s13, x, 1.42, 0.06, 1.12, col)
    tb(s13, x + 0.14, 1.32, cw13 - 0.2, 0.22, [[(ph, {'size': 9, 'bold': True, 'color': 'C98A1E'})]])
    tb(s13, x + 0.14, 1.5, cw13 - 0.2, 0.3, [[(name, {'size': 13, 'bold': True, 'color': INK, 'font': HFONT})]])
    tb(s13, x + 0.14, 1.8, cw13 - 0.22, 0.86, paras, space_after=1)
    if k < 2: shape(s13, MSO_SHAPE.RIGHT_ARROW, x + cw13 + 0.05, 1.87, 0.22, 0.22, AMBER, None)
picture(s13, f'{FIG}/toolbox.png', 1.42, 2.76, 11.5, 3.9)

# ================= Phase 1 · fault-tolerant neuron core (slides 14–18)
EQ = f'{FIG}/eq'
def lab(sl, x, y, w, t, col='C98A1E'):
    tb(sl, x, y, w, 0.24, [[(t, {'size': 9, 'bold': True, 'color': col})]])
def banner(sl, a, b):
    bn = rrect(sl, 1.42, 6.12, 11.5, 0.5, INK, None, 0.2)
    write(bn, [[(a, {'size': 14, 'color': WHITE, 'font': HFONT}), (b, {'size': 14, 'bold': True, 'color': AMBER, 'font': HFONT})]], align='c', anchor='m')

# ---- Slide 14: starting point
s14 = D.new(); D.chrome(s14, 3, 'Phase 1 · Starting Point: the Izhikevich Neuron',
    footer='Izhikevich, IEEE TNN 2003 · Roshani et al., H-ASIZH, IEEE TCAS-I (submitted), Sec. II')
rrect(s14, 1.42, 1.32, 5.75, 1.78, WHITE, LINE, 0.06); lab(s14, 1.6, 1.38, 5, 'IZHIKEVICH MODEL (2003) · RICH FIRING FROM FOUR PARAMETERS a, b, c, d')
picture(s14, f'{EQ}/izh.png', 1.6, 1.62, 5.4, 1.42)
rrect(s14, 1.42, 3.2, 5.75, 0.86, 'FFF7E6', 'F1CD8A', 0.12); lab(s14, 1.6, 3.24, 5.4, 'EXACT AFFINE MAP · ÷64 IS A FREE RIGHT-SHIFT', '9A6A12')
picture(s14, f'{EQ}/map.png', 1.6, 3.46, 5.4, 0.56)
rrect(s14, 1.42, 4.16, 5.75, 1.3, WHITE, LINE, 0.08); lab(s14, 1.6, 4.22, 5.4, 'HARDWARE FORM · SAME NULLCLINES, SAME PHASE PORTRAIT')
picture(s14, f'{EQ}/hw.png', 1.6, 4.46, 5.4, 0.94)
tb(s14, 1.42, 5.52, 5.75, 0.55, [[('Contraction keeps the state near [−0.5, 1.5]: ', {'size': 11.5, 'color': INK}), ('free guard bits ', {'size': 11.5, 'bold': True, 'color': TEAL}), ('in the Q7.19 word.', {'size': 11.5, 'color': INK})]])
rrect(s14, 7.35, 1.32, 5.57, 4.74, WHITE, LINE, 0.04)
picture(s14, f'{FIG}/fig02_nine_patterns.png', 7.45, 1.4, 5.37, 4.3)
tb(s14, 7.45, 5.72, 5.37, 0.3, [[('Bio vs hardware model: nine patterns overlap, RMSE < 10⁻¹³', {'size': 10.5, 'italic': True, 'color': MUTED})]], align='c')
banner(s14, 'Exact and shift-friendly  —  ', 'yet one stuck-at still drives it into a digital seizure')

# ---- Slide 15: homeostasis guided by Lyapunov
s15 = D.new(); D.chrome(s15, 3, 'Adding Homeostasis, Guided by Lyapunov',
    footer='Khalil, Nonlinear Systems · Slotine & Li, Applied Nonlinear Control · Roshani et al., TCAS-I (submitted), Sec. III')
rrect(s15, 1.42, 1.32, 5.9, 2.36, WHITE, LINE, 0.05); lab(s15, 1.6, 1.38, 5.6, 'H-ASIZH · THE THRESHOLD θ BECOMES A SLOW STATE VARIABLE')
picture(s15, f'{EQ}/hasizh.png', 1.6, 1.62, 5.55, 2.0)
chips = [('α = 2⁻⁶', 'leak · ≫ 6', 'θ returns to θ₀ when healthy'), ('γ = 2⁻³', 'penalty · ≫ 3', 'every spike raises θ'), ('β = 2³', 'brake · ≪ 3', 'deeper reset after a burst')]
for k, (a, b, c) in enumerate(chips):
    x = 1.42 + k * 2.0
    rrect(s15, x, 3.78, 1.9, 0.86, 'FFF7E6', 'F1CD8A', 0.14)
    tb(s15, x + 0.08, 3.8, 1.75, 0.3, [[(a, {'size': 14, 'bold': True, 'color': '9A6A12', 'font': HFONT}), ('  ' + b, {'size': 9, 'color': MUTED})]])
    tb(s15, x + 0.08, 4.18, 1.78, 0.42, [[(c, {'size': 10.5, 'color': INK})]])
rrect(s15, 1.42, 4.74, 5.9, 1.3, 'EEF6F6', 'B9DADC', 0.06); lab(s15, 1.6, 4.8, 5.6, 'LYAPUNOV ARGUMENT', TEAL)
picture(s15, f'{EQ}/lyap.png', 1.6, 5.02, 5.55, 0.98)
rrect(s15, 7.5, 1.32, 5.42, 3.62, WHITE, LINE, 0.04)
picture(s15, f'{FIG}/fig04_phase_space.png', 7.58, 1.4, 5.26, 3.1)
tb(s15, 7.58, 4.52, 5.26, 0.36, [[('Normal: 2-D cycle  ·  Fault: collapse  ·  H-ASIZH: bounded 3-D attractor', {'size': 10.5, 'italic': True, 'color': MUTED})]], align='c')
rrect(s15, 7.5, 5.04, 5.42, 1.0, 'EEF6F6', 'B9DADC', 0.1)
tb(s15, 7.68, 5.1, 5.1, 0.9, [[('The firing rate is ', {'size': 13, 'color': INK}), ('uniformly ultimately bounded', {'size': 13, 'bold': True, 'color': TEAL}),
                               (' — the band is set by γ, not by the size of the fault.', {'size': 13, 'color': INK})]], anchor='m')
banner(s15, 'θ makes the neuron its own controller  —  ', 'no external monitor, no redundancy')

# ---- Slide 16: the controller is a learning rule
s16 = D.new(); D.chrome(s16, 3, 'The Same Equation Is a Learning Rule',
    footer='Diehl & Cook, Front. Comput. Neurosci. 2015 (adaptive threshold for STDP learning) · Johnson et al., TCAS-I 2018 · Roshani et al., TCAS-I (submitted)')
rrect(s16, 1.42, 1.32, 11.5, 1.32, WHITE, LINE, 0.08); lab(s16, 1.62, 1.38, 9, 'OUR FAULT-TOLERANCE CONTROLLER (H-ASIZH)', TEAL)
picture(s16, f'{EQ}/ours.png', 1.62, 1.6, 11.1, 0.98)
eqv = oval(s16, 6.93, 2.6, 0.48, AMBER); write(eqv, [('≡', {'size': 20, 'bold': True, 'color': WHITE})], align='c', anchor='m')
rrect(s16, 1.42, 3.0, 11.5, 1.32, WHITE, LINE, 0.08); lab(s16, 1.62, 3.06, 9, 'ADAPTIVE-THRESHOLD HOMEOSTASIS USED FOR UNSUPERVISED STDP LEARNING (DIEHL & COOK 2015)', BLUE)
picture(s16, f'{EQ}/dc.png', 1.62, 3.28, 11.1, 0.98)
rrect(s16, 3.4, 4.4, 7.55, 0.52, 'FFF7E6', 'F1CD8A', 0.3)
picture(s16, f'{EQ}/map2.png', 3.5, 4.43, 7.35, 0.46)
cards16 = [('Biology', 'α ↔ Ca²⁺ clearance · γ ↔ Ca²⁺ influx per spike · β ↔ Ca²⁺-dependent hyperpolarization', TEAL),
           ('Hardware', 'Controller = three shifters, two adders, one comparator — no multiplier.', BLUE),
           ('Learning', 'The same θ prevents neuron death and dominance in competitive learning.', '9A6A12')]
for k, (h, t, col) in enumerate(cards16):
    x = 1.42 + k * 3.9
    rrect(s16, x, 5.04, 3.7, 0.98, WHITE, LINE, 0.1); rect(s16, x, 5.16, 0.06, 0.74, col)
    tb(s16, x + 0.16, 5.07, 3.45, 0.3, [[(h, {'size': 12.5, 'bold': True, 'color': col, 'font': HFONT})]])
    tb(s16, x + 0.16, 5.37, 3.45, 0.62, [[(t, {'size': 10.5, 'color': INK})]])
banner(s16, 'Silicon bought for fault tolerance also buys on-chip learning  —  ', 'overhead ≈ α, β, γ')

# ---- Slide 17: micro-architecture
s17 = D.new(); D.chrome(s17, 3, 'A One-Cycle, Multiplier-Free Micro-Architecture',
    footer='Roshani et al., TCAS-I (submitted), Sec. IV, Figs. 5–6 · RTL: GLFI_fault_campaign/rtl/mark2_homeostatic.vhd')
rrect(s17, 1.42, 1.32, 7.35, 4.36, WHITE, LINE, 0.03)
picture(s17, f'{FIG}/fig06_microarchitecture.png', 1.5, 1.4, 7.19, 4.04)
tb(s17, 1.5, 5.4, 7.19, 0.26, [[('EX: PWL estimator · V and U datapaths · homeostatic engine     WB: clamping · fast-bleed valve · spike generator', {'size': 9.5, 'italic': True, 'color': MUTED})]], align='c')
rrect(s17, 8.95, 1.32, 3.97, 1.98, WHITE, LINE, 0.06)
picture(s17, f'{FIG}/fig05_q719_word.png', 9.03, 1.38, 3.81, 1.86)
rrect(s17, 8.95, 3.4, 3.97, 2.28, WHITE, LINE, 0.06); lab(s17, 9.1, 3.45, 3.7, 'V² WITHOUT A MULTIPLIER · 4-SEGMENT PWL')
picture(s17, f'{EQ}/pwl.png', 9.05, 3.7, 3.77, 1.9)
chips17 = [('1 update / cycle', 'no latency jitter in a timing code'), ('shifts & adds only', 'no multiplier on the critical path'), ('safety inside the core', 'clamping · fast-bleed · β-brake')]
for k, (a, b) in enumerate(chips17):
    x = 1.42 + k * 3.9
    rrect(s17, x, 5.78, 3.7, 0.28, 'EEF6F6', 'B9DADC', 0.4)
    tb(s17, x + 0.1, 5.79, 3.5, 0.26, [[(a + '  ', {'size': 10.5, 'bold': True, 'color': TEAL}), (b, {'size': 10, 'color': INK})]], align='c')
banner(s17, 'Placed and routed in SkyWater 130 nm  —  ', 'the controller adds only shifters, adders and a comparator')

# ---- Slide 18: case study
s18 = D.new(); D.chrome(s18, 3, 'Case Study: Does Learning Survive on the Core?',
    footer='Roshani et al., TCAS-I (submitted), Sec. VI and VII-E, Figs. 8 and 10 · MNIST downsampled to 16 × 16, TTFS in 15 time steps')
rrect(s18, 1.42, 1.32, 6.25, 4.72, WHITE, LINE, 0.03)
picture(s18, f'{FIG}/fig08_case_study_system.png', 1.5, 1.4, 6.09, 4.56)
stats = [('256 → 1024 → 10', 'TTFS SNN built only from our cores · STDP + first-K WTA (K = 3) · delta-rule readout', BLUE, WHITE),
         ('2 cores · 1,034 logical neurons', 'time-multiplexed · 4-bit weights · 2.26 Mib of state and weight memory', BLUE, WHITE),
         ('182.8 µW', 'both hardened cores together — 0.177 µW per logical neuron', BLUE, WHITE),
         ('81.8 % on MNIST · 1020 / 1024 active', 'the adaptive threshold keeps the whole population alive while it learns', WHITE, TEAL)]
for k, (h, t, hc, fill) in enumerate(stats):
    y = 1.32 + k * 1.2
    rrect(s18, 7.85, y, 5.07, 1.1, fill, LINE if fill == WHITE else None, 0.1)
    tb(s18, 8.02, y + 0.08, 4.8, 0.4, [[(h, {'size': 17 if k < 3 else 15.5, 'bold': True, 'color': hc, 'font': HFONT})]])
    tb(s18, 8.02, y + 0.5, 4.8, 0.58, [[(t, {'size': 10.5, 'color': INK if fill == WHITE else 'E6F4F4'})]])
banner(s18, 'Fault tolerance did not cost learning  —  ', 'it kept the population alive')

D.finalize([s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14, s15, s16, s17, s18])
prs.save(OUT); print('saved', OUT, len(prs.slides))
