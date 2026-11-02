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

D.finalize([s1, s2, s3, s4, s5, s6, s7, s8, s9])
prs.save(OUT); print('saved', OUT, len(prs.slides))
