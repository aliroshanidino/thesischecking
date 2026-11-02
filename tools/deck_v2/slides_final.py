# appended into build_v2.py: Phase 3, Results, Conclusion, References, Thank you
def simple_table(sl, x, y, widths, rows, header, hl_cols=(), hl_rows=(), rh=0.34, fs=11):
    gt = sl.shapes.add_table(len(rows) + 1, len(widths), Inches(x), Inches(y), Inches(sum(widths)), Inches(rh * (len(rows) + 1)))
    t = gt.table; tp = t._tbl.find(_qn('a:tblPr'))
    for at in ('firstRow', 'bandRow'): tp.set(at, '0')
    sid = tp.find(_qn('a:tableStyleId'))
    if sid is not None: sid.text = '{5940675A-B579-460E-94D1-54222C63F5DA}'
    for j, w in enumerate(widths): t.columns[j].width = Inches(w)
    for i in range(len(rows) + 1): t.rows[i].height = Inches(rh)
    for j, h in enumerate(header):
        put(t.cell(0, j), [(h, {'size': fs - 1, 'bold': True, 'color': INK})], fill='DCE6F0', align='l' if j == 0 else 'c')
    for i, row in enumerate(rows, start=1):
        for j, v in enumerate(row):
            hl = (j in hl_cols) or (i - 1 in hl_rows)
            fill = 'FFF7E6' if hl else 'FFFFFF'
            put(t.cell(i, j), [(v, {'size': fs, 'bold': (j == 0) or hl, 'color': INK})], fill=fill, align='l' if j == 0 else 'c')
            _ln(t.cell(i, j), 'lnB', 'E3EAF2', 0.6)
    return t

# ================= Phase 3 · BioVision (methodology)
s23 = D.new(); D.chrome(s23, 3, 'Phase 3 · From One Core to a Brain-Like Vision Network',
    footer='BioVision-SNN architecture (draw.io, 2026) · Kheradpisheh et al. 2018 · Mozafari et al. 2018 · Lamme & Roelfsema 2000 (feed-forward sweep vs recurrent waves)')
rrect(s23, 1.42, 1.3, 11.5, 4.72, WHITE, LINE, 0.02)
picture(s23, f'{FIG}/bio_arch.png', 1.5, 1.36, 11.34, 4.6)
banner(s23, 'The ventral path is built and tested  —  ', 'motion, attention, memory and depth come next')

s24 = D.new(); D.chrome(s24, 3, 'Hardware-Aware by Design',
    footer='BioVision-SNN Phase 1 report (notes 16, 26) · Mitchell logarithm · Brader, Senn & Fusi 2007 · Mozafari et al. 2018')
cards24 = [('Retina emulator', 'P, K and M channels in the log domain; intensity becomes a spike latency — no multipliers.', 'latency', TEAL),
           ('Wave-based TTFS', 'At most one spike per neuron per wave (T = 15 steps); feedback acts in the next wave.', None, BLUE),
           ('Local learning only', 'Flat STDP in S1–S4, exponential STDP for motion, R-STDP for IT and the read-out; no backprop.', None, '9A6A12'),
           ('Two-sided homeostasis', 'Lesson from Phase 1: the θ ≥ θ₀ floor silenced S1, so θ now moves both ways — still shifts only.', 'homeo2', '6B4FA0')]
for k, (h, t, eqn, col) in enumerate(cards24):
    x = 1.42 + (k % 2) * 5.85; y = 1.3 + (k // 2) * 2.4
    rrect(s24, x, y, 5.65, 2.25, WHITE, LINE, 0.06); rect(s24, x, y + 0.2, 0.06, 1.85, col)
    tb(s24, x + 0.2, y + 0.1, 5.3, 0.36, [[(h, {'size': 16, 'bold': True, 'color': col, 'font': HFONT})]])
    tb(s24, x + 0.2, y + 0.5, 5.3, 0.7, [[(t, {'size': 12, 'color': INK})]])
    if eqn: picture(s24, f'{EQ}/{eqn}.png', x + 0.3, y + 1.25, 5.1, 0.88)
    else:
        if k == 1:
            for w in range(4):
                xx = x + 0.4 + w * 1.25
                rrect(s24, xx, y + 1.42, 1.1, 0.5, 'EAF1F9', 'BFD0E2', 0.2)
                tb(s24, xx, y + 1.45, 1.1, 0.44, [[(f'wave {w+1}', {'size': 10.5, 'bold': True, 'color': BLUE})]], align='c', anchor='m')
        else:
            for w, (lay, rule) in enumerate([('S1–S4', 'flat STDP'), ('motion', 'exp. STDP'), ('IT · read-out', 'R-STDP')]):
                xx = x + 0.3 + w * 1.7
                rrect(s24, xx, y + 1.38, 1.55, 0.62, 'FBF2E6', 'E8C27A', 0.15)
                tb(s24, xx, y + 1.4, 1.55, 0.58, [[(lay, {'size': 10.5, 'bold': True, 'color': '9A6A12'})], [(rule, {'size': 10, 'color': INK})]], align='c')
banner(s24, 'Biologically faithful and multiplier-free  —  ', 'every block maps to shifts, adds and compares')

# ================= 04 Results
s25 = D.new(); divider(D, s25, 4, 'Results', f'{FIG}/hero_results.png')

s26 = D.new(); D.chrome(s26, 4, 'Phase 1 · Silicon Cost in SkyWater 130 nm',
    footer='Roshani et al., TCAS-I (submitted), Table II · OpenLane P&R, OpenSTA sign-off at the typical corner (1.8 V, 25 °C) · same 80,146.87 µm² floorplan for all five designs')
rows26 = [('Standard cells', '1,772', '2,469', '3,969', '4,093', '6,025'),
          ('Cell overhead', '1.00×', '1.39×', '2.24×', '2.31×', '3.40×'),
          ('Fmax (MHz)', '83.61', '64.92', '64.18', '62.11', '80.00'),
          ('Total core power (µW)', '30.7', '52.8', '88.5', '91.4', '116.8'),
          ('Energy per update (pJ)', '0.367', '0.813', '1.379', '1.472', '1.460')]
simple_table(s26, 1.42, 1.4, [3.0, 1.7, 1.7, 1.7, 1.7, 1.7], rows26, ['', 'Baseline', 'Homeostasis', '+ Light TMR', '+ Restoring Organ', 'Full TMR'], hl_cols=(2, 4), rh=0.5, fs=13)
pts26 = [('The in-neuron controller is cheap: ', '697 cells (1.39×) for θ, leak, penalty and brake.'),
         ('Triplication multiplies everything: ', '3.40× cells, 3.80× power, 4.12× wire length.'),
         ('Same energy, different safety: ', 'Restoring Organ 1.472 pJ vs full TMR 1.460 pJ per update (next slide).')]
for k, (a, b) in enumerate(pts26):
    rrect(s26, 1.42, 4.55 + k * 0.5, 11.5, 0.42, 'F7FBFB', 'B9DADC', 0.3)
    tb(s26, 1.6, 4.57 + k * 0.5, 11.2, 0.38, [[(a, {'size': 12, 'bold': True, 'color': TEAL}), (b, {'size': 12, 'color': INK})]], anchor='m')
banner(s26, 'A fault-tolerant Izhikevich neuron for  ', 'under a tenth of a milliwatt')

s27 = D.new(); D.chrome(s27, 4, 'Phase 1 · Fault Outcomes on the Netlist',
    footer='Roshani et al., TCAS-I (submitted), Fig. 9 · exhaustive single stuck-at campaign, both polarities · FRE ≤ 20 % and CV ≤ 0.20')
rrect(s27, 1.42, 1.3, 7.3, 4.72, WHITE, LINE, 0.03)
picture(s27, f'{FIG}/fig09_campaign_results.png', 1.5, 1.4, 7.14, 4.5)
tb(s27, 8.9, 1.3, 4.0, 0.34, [[('Dangerous faults (critical + fatal)', {'size': 13, 'bold': True, 'color': INK, 'font': HFONT})]])
bars = [('Baseline', 46.2, 'B8C4D2'), ('Homeostasis', 17.5, TEAL), ('+ Light TMR', 14.9, '7FB0D6'), ('+ Restoring Organ', 4.2, '2E7D4F'), ('Full TMR', 12.0, 'C98A1E')]
for k, (n, v, col) in enumerate(bars):
    y = 1.78 + k * 0.6
    tb(s27, 8.9, y, 1.75, 0.3, [[(n, {'size': 11, 'bold': True, 'color': INK})]])
    rect(s27, 10.6, y + 0.04, max(0.06, v / 46.2 * 1.8), 0.24, col)
    tb(s27, 10.6 + v / 46.2 * 1.8 + 0.06, y, 0.8, 0.3, [[(f'{v} %', {'size': 11, 'bold': True, 'color': INK})]])
rrect(s27, 8.9, 4.86, 4.02, 1.16, 'F7FBFB', 'B9DADC', 0.08)
tb(s27, 9.02, 4.9, 3.8, 1.08, [[('Homeostasis alone cuts critical faults 3× and creates a tolerant class (20.8 %). ', {'size': 10.5, 'color': INK}),
                                 ('Restoring Organ: 4.2 % vs 12.0 % for full TMR, with 32 % fewer cells.', {'size': 10.5, 'bold': True, 'color': TEAL})]], anchor='m')
banner(s27, 'At equal energy per update  —  ', 'the adaptive core is almost 3× safer than full TMR')

s28 = D.new(); D.chrome(s28, 4, 'Phase 1 · Reliability per Unit of Silicon',
    footer='Roshani et al., TCAS-I (submitted), Table III and Eq. (26) · first-order screening ratio under the single-fault model, not a lifetime')
rrect(s28, 1.42, 1.3, 4.2, 1.3, 'FFF7E6', 'F1CD8A', 0.1)
picture(s28, f'{EQ}/rfom.png', 1.55, 1.38, 3.95, 1.15)
tb(s28, 5.85, 1.35, 7.0, 1.2, [[('Vulnerability reduction divided by area growth. ', {'size': 13, 'color': INK}), ('A protection pays for its silicon only when RFoM > 1.', {'size': 13, 'bold': True, 'color': TEAL})]], anchor='m')
rows28 = [('Baseline', '1,772', '0.462', '1.00×', '1.00×', '1.00×'), ('Homeostasis', '2,469', '0.175', '2.64×', '1.39×', '1.89×'),
          ('+ Light TMR', '3,969', '0.149', '3.10×', '2.24×', '1.38×'), ('+ Restoring Organ', '4,093', '0.042', '11.00×', '2.31×', '4.76×'),
          ('Full TMR', '6,025', '0.120', '3.85×', '3.40×', '1.13×')]
simple_table(s28, 1.42, 2.8, [3.0, 1.7, 1.7, 1.7, 1.7, 1.7], rows28, ['Architecture', 'Cells', 'AVF', 'Vuln. reduction', 'Area growth', 'RFoM'], hl_rows=(1, 3), rh=0.5, fs=13)
banner(s28, 'Replication is self-limiting  —  ', 'homeostasis lowers AVF without copying anything')

s29 = D.new(); D.chrome(s29, 4, 'Phase 1 · Learning Survives on the Core',
    footer='Roshani et al., TCAS-I (submitted), Sec. VII-E and Fig. 10 · 25 epochs on 10,000 MNIST images, evaluated on 2,000 · 256 → 1024 → 10, K = 3')
rrect(s29, 1.42, 1.3, 5.3, 4.72, WHITE, LINE, 0.03)
picture(s29, f'{FIG}/fig10_onchip_learning.png', 1.5, 1.38, 5.14, 4.56)
stats29 = [('81.8 %', 'peak test accuracy (K = 3) · 81.2 ± 0.5 % over the last five epochs', BLUE),
           ('81.5 %', 'end-to-end RTL simulation on 600 test images — within one standard error', BLUE),
           ('1020 ± 2 / 1024', 'hidden neurons stay active in all 25 epochs — no death, no dominance', TEAL),
           ('182.8 µW', 'both hardened cores together · 0.177 µW per logical neuron', '9A6A12')]
for k, (h, t, col) in enumerate(stats29):
    y = 1.3 + k * 1.2
    rrect(s29, 6.9, y, 6.02, 1.1, WHITE, LINE, 0.1); rect(s29, 6.9, y + 0.14, 0.06, 0.82, col)
    tb(s29, 7.08, y + 0.06, 5.7, 0.46, [[(h, {'size': 20, 'bold': True, 'color': col, 'font': HFONT})]])
    tb(s29, 7.08, y + 0.55, 5.7, 0.5, [[(t, {'size': 11.5, 'color': INK})]])
banner(s29, 'Fault tolerance did not cost learning  —  ', 'it kept the population alive')

s30 = D.new(); D.chrome(s30, 4, 'Phase 2 · What the Three-Class View Hides',
    footer='Roshani et al., GateScan, IEEE TCAD (draft), Table II, Figs. 3, 4 and 6 · ShadowFI benchmarks (SFUv1, TCU, SFUv2) and twenty ITC’99 circuits')
for (x, y, w, h, img) in [(1.42, 1.3, 5.6, 2.62, 'gs_res10'), (7.2, 1.3, 5.72, 2.62, 'gs_res11'), (1.42, 4.02, 5.6, 2.0, 'gs_res13')]:
    rrect(s30, x, y, w, h, WHITE, LINE, 0.04); picture(s30, f'{FIG}/{img}.png', x + 0.08, y + 0.06, w - 0.16, h - 0.12)
rrect(s30, 7.2, 4.02, 5.72, 2.0, WHITE, LINE, 0.05)
pts30 = [('13–55 %', ' of “masked” faults are proven vulnerable (ESC)'), ('72.5 → 87.5 %', ' TCU lower bound after two trigger rounds'),
         ('[3.2, 99.6]', ' bracket on b18, where the point estimate says 3.2 %'), ('0 disagreements', ' in 1,834 two-engine runs · 165/165 gates')]
for k, (a, b) in enumerate(pts30):
    tb(s30, 7.35, 4.1 + k * 0.46, 5.5, 0.42, [[(a, {'size': 12.5, 'bold': True, 'color': TEAL}), (b, {'size': 11.5, 'color': INK})]], anchor='m')
banner(s30, 'A point estimate hides what the campaign does not know  —  ', 'the bracket shows it')

s31 = D.new(); D.chrome(s31, 4, 'Phase 3 · BioVision Results So Far',
    footer='BioVision-SNN Phase 0 and Phase 1 reports (notes 15, 16, 26) · test accuracy, mean ± std over seeds · paper values are best-epoch, ours are selected on validation unless noted')
rows31 = [('RL, Caltech (Mozafari et al.)', '98.9 ± 0.4', '98.65 ± 0.49'), ('SVM, Caltech (Kheradpisheh et al.)', '99.1 ± 0.2', '98.96 ± 0.25'),
          ('SVM, MNIST', '98.4', '98.52 ± 0.06'), ('SVM, ETH-80, 5/5 split', '82.8', '84.25 ± 3.49')]
tb(s31, 1.42, 1.28, 6.0, 0.3, [[('PHASE 0 · REPRODUCING THE REFERENCE NETWORKS', {'size': 9.5, 'bold': True, 'color': 'C98A1E'})]])
simple_table(s31, 1.42, 1.58, [3.4, 1.25, 1.35], rows31, ['Front, dataset', 'Paper', 'Ours'], hl_cols=(2,), rh=0.42, fs=11.5)
tb(s31, 7.3, 1.28, 5.6, 0.3, [[('PHASE 1 · COLOUR RETINA + VENTRAL PATH, MULTIPLIER-FREE', {'size': 9.5, 'bold': True, 'color': 'C98A1E'})]])
p1 = [('89.42 ± 1.18 %', 'RL, Caltech four classes — above the 85 % target', TEAL), ('72.86 ± 2.22 %', 'RL, ETH-80 5/5 — training still rising at epoch 80', '9A6A12'),
      ('≈ float', 'multiplier-free retina and learning: 73.48 vs 72.56 % (validation)', BLUE), ('4× fewer spikes', 'magno channel alone matches colour on ETH-80 (71.95 vs 71.34 %)', BLUE)]
for k, (a, b, col) in enumerate(p1):
    y = 1.58 + k * 0.6
    rrect(s31, 7.3, y, 5.62, 0.52, WHITE, LINE, 0.15)
    tb(s31, 7.42, y + 0.03, 5.4, 0.46, [[(a + '  ', {'size': 13, 'bold': True, 'color': col, 'font': HFONT}), (b, {'size': 11, 'color': INK})]], anchor='m')
rrect(s31, 1.42, 4.2, 11.5, 1.82, 'F7FBFB', 'B9DADC', 0.05)
tb(s31, 1.6, 4.26, 11.2, 0.32, [[('What Phase 1 taught us', {'size': 14, 'bold': True, 'color': TEAL, 'font': HFONT})]])
less = ['Colour P+K helps on validation (+6.7 %), but the K channel also coded the blue ETH-80 background — found and removed.',
        'Fixed contrast thresholds are fragile under gamma (72 → 11 %); local contrast normalisation removes it at a 3.7 % cost.',
        'The H-ASIZH floor θ ≥ θ₀ silenced S1 after STDP converged — replaced by two-sided rate homeostasis.']
for k, t in enumerate(less):
    tb(s31, 1.75, 4.62 + k * 0.45, 11.0, 0.42, [[('•  ', {'size': 12, 'bold': True, 'color': TEAL}), (t, {'size': 11.5, 'color': INK})]], anchor='m')
banner(s31, 'Local learning, no multipliers  —  ', 'classification works; detection on COCO is next')

# ================= 05 Conclusion
s32 = D.new(); divider(D, s32, 5, 'Conclusion', f'{FIG}/hero_concl.png')

s33 = D.new(); D.chrome(s33, 5, 'Gaps Closed — With Evidence',
    footer='Numbers: TCAS-I (submitted) Tables II–III and Figs. 9–10 · GateScan TCAD (draft) Table II · BioVision Phase 0–1 reports')
rows33 = [('G1', 'No deterministic guarantees', 'C1', 'One-cycle, Lyapunov-bounded core · 52.8 µW and 0.813 pJ per update'),
          ('G2', 'Standards rarely met', 'C2', 'GateScan: certified brackets and exact intervals, not a percentage'),
          ('G3', 'The device is assumed correct', 'C1', 'Dangerous faults 46.2 % → 4.2 % · RFoM 4.76× vs 1.13× for full TMR'),
          ('G4', 'Neuromorphic is not mature', 'C3', 'BioVision, local learning, no multipliers: 98.5 % MNIST · 89.4 % Caltech-4'),
          ('G5', 'No learning in the field', 'C4', 'On-chip STDP on the hardened core: 81.8 % MNIST, 1020 / 1024 neurons alive')]
for k, (g, gt, c, ev) in enumerate(rows33):
    y = 1.3 + k * 0.94
    rrect(s33, 1.42, y, 4.2, 0.84, WHITE, LINE, 0.12); rect(s33, 1.42, y + 0.15, 0.06, 0.54, RED)
    tb(s33, 1.6, y + 0.04, 4.0, 0.76, [[(g + '  ', {'size': 11, 'bold': True, 'color': RED}), (gt, {'size': 14, 'bold': True, 'color': INK, 'font': HFONT})]], anchor='m')
    shape(s33, MSO_SHAPE.RIGHT_ARROW, 5.75, y + 0.27, 0.42, 0.3, '9DB4CB', None)
    name, col, ph = CON[c]
    rrect(s33, 6.32, y, 6.6, 0.84, 'F7FBFB', 'B9DADC', 0.12)
    pill = rrect(s33, 6.45, y + 0.25, 0.32 * 1.0 + 0.95, 0.34, col, None, 0.5); write(pill, [(c, {'size': 11, 'bold': True, 'color': WHITE})], align='c', anchor='m')
    tb(s33, 7.82, y + 0.04, 5.0, 0.76, [[(ev, {'size': 12, 'color': INK})]], anchor='m')
banner(s33, 'Adapt, don’t replicate  —  ', 'dependability built into the neuron itself')

s34 = D.new(); D.chrome(s34, 5, 'The Road Ahead',
    footer='BioVision project brief, phases 2–5 · GateScan lesson, Ch. 10 · TCAS-I (submitted), Sec. VIII')
road34 = [('eye-outline', 'BioVision', '6B4FA0', ['Detection: Penn-Fudan, then COCO', 'Dorsal stream: motion, depth', 'Attention, PFC, object tokens', 'Border ownership and masks', 'Layer-by-layer fault campaign']),
          ('chip', 'Accelerator', TEAL, ['Harden controller, NoC, memory', 'Many hardened cores, one SNN', 'FPGA prototype', 'Tape-out in SkyWater 130 nm']),
          ('magnify-scan', 'GateScan', BLUE, ['Head-to-head with a commercial tool', 'Trigger loop on processors', 'Stronger formal oracle', 'Million-cell scale']),
          ('brain', 'Neuron', '9A6A12', ['Two-sided fault-tolerant LIF / IF', 'Homeostasis 2.0 for learning', 'Transient faults (SEU) in the core'])]
for k, (ic, h, col, items) in enumerate(road34):
    x = 1.42 + k * 2.92
    rrect(s34, x, 1.3, 2.78, 4.72, WHITE, LINE, 0.05); rect(s34, x + 0.2, 1.3, 2.38, 0.06, col)
    oval(s34, x + 0.98, 1.5, 0.8, 'F1F5F9'); picture(s34, f'{IC}/g9_{ic if ic != "eye-outline" else "brain"}.png' if False else f'{IC}/g9_chip.png', x + 1.13, 1.65, 0.5, 0.5) if False else None
    tb(s34, x + 0.1, 1.5, 2.58, 0.8, [[(h, {'size': 17, 'bold': True, 'color': col, 'font': HFONT})]], align='c', anchor='m')
    for i, it in enumerate(items):
        yy = 2.45 + i * 0.68
        rrect(s34, x + 0.15, yy, 2.48, 0.58, 'F7FAFC', 'E1E8F0', 0.15)
        tb(s34, x + 0.22, yy + 0.02, 2.34, 0.54, [[(it, {'size': 11, 'color': INK})]], anchor='m', align='c')
banner(s34, 'Next: from a dependable neuron  —  ', 'to a dependable vision system')

s35 = D.new(); D.chrome(s35, 5, 'Research Outputs',
    footer='Status as of Aban 1405 / November 2026')
outs = [('Journal · submitted', 'H-ASIZH: A Highly Reliable Digital Izhikevich Neuron Core Using Adaptive Threshold Control for Fault Accommodation', 'A. Roshani, M. Ansari, M. T. Manzuri Shalmani — IEEE Transactions on Circuits and Systems I', TEAL),
        ('Journal · draft', 'Masked Is Not Harmless: Certified Gate-Level Fault Vulnerability Analysis with LLM Agents That Propose and Engines That Decide', 'A. Roshani, M. Ansari, M. T. Manzuri Shalmani — IEEE Transactions on Computer-Aided Design', BLUE),
        ('Open source', 'GLFI fault campaign · GateScan Mark III (core, agents, web service) · BioVision-SNN code and run records', 'github.com/aliroshanidino/GLFI_fault_campaign · github.com/gatescan-dev/gatescanMarkIII', '9A6A12'),
        ('Reports', 'BioVision-SNN Phase 0 and Phase 1 technical reports · GateScan lesson (10 chapters) · thesis knowledge base', 'github.com/aliroshanidino/thesischecking', '6B4FA0')]
for k, (tag, t1, t2, col) in enumerate(outs):
    y = 1.3 + k * 1.18
    rrect(s35, 1.42, y, 11.5, 1.06, WHITE, LINE, 0.08); rect(s35, 1.42, y + 0.14, 0.07, 0.78, col)
    pill = rrect(s35, 1.65, y + 0.12, 1.75, 0.32, col, None, 0.5); write(pill, [(tag, {'size': 10, 'bold': True, 'color': WHITE})], align='c', anchor='m')
    tb(s35, 3.55, y + 0.06, 9.25, 0.56, [[(t1, {'size': 13, 'bold': True, 'color': INK, 'font': HFONT})]], anchor='m')
    tb(s35, 3.55, y + 0.62, 9.25, 0.38, [[(t2, {'size': 10.5, 'color': MUTED})]])
banner(s35, 'Two journal papers, open code and open data  —  ', 'every number in this talk is traceable')

s36 = D.new(); D.chrome(s36, 5, 'Selected References',
    footer='Full bibliography: thesis Chapter 1 (162 references) and the two papers')
refs = ['E. M. Izhikevich, “Simple model of spiking neurons,” IEEE TNN, 2003.',
        'C. Frenkel et al., ODIN, IEEE TBioCAS, 2019.',
        'P. U. Diehl and M. Cook, Front. Comput. Neurosci., 2015.',
        'H. K. Khalil, Nonlinear Systems, Prentice Hall, 2002.',
        'J. Arlat et al., “Fault injection for dependability validation,” IEEE TSE, 1990.',
        'R. Leveugle et al., “Statistical fault injection,” DATE, 2009.',
        'C. J. Clopper and E. S. Pearson, Biometrika, 1934.',
        'S. S. Mukherjee et al., AVF methodology, MICRO-36, 2003.',
        'J.-D. Guerrero-Balaguera et al., SHADOWFI, IEEE Access, 2025.',
        'R. C. Baumann, soft errors, IEEE TDMR, 2005.',
        'P. H. Hochschild et al., “Cores that don’t count,” HotOS, 2021.',
        'H. D. Dixit et al., “Silent data corruptions at scale,” 2021.',
        'J. Dean and L. A. Barroso, “The tail at scale,” CACM, 2013.',
        'G. Buttazzo, Hard Real-Time Computing Systems, Springer.',
        'T. Spyrou et al., neuron fault tolerance in SNNs, DATE, 2021.',
        'R. V. W. Putra et al., SoftSNN, DAC, 2022.',
        'R. V. W. Putra et al., RescueSNN, Front. Neurosci., 2023.',
        'Y.-H. Chen et al., Eyeriss, IEEE JSSC, 2017.',
        'P. A. Merolla et al., TrueNorth, Science, 2014.',
        'M. Davies et al., Loihi, IEEE Micro, 2018.',
        'M. Yao et al., Speck, Nat. Commun., 2024.',
        'S. R. Kheradpisheh et al., STDP-based SDNN, Neural Netw., 2018.',
        'M. Mozafari et al., first-spike R-STDP, IEEE TNNLS, 2018.',
        'X. Luo et al., SpikeYOLO, ECCV, 2024.',
        'ISO 26262:2018 · ISO 14708-1:2014.',
        'A. Roshani et al., H-ASIZH, IEEE TCAS-I (submitted).',
        'A. Roshani et al., GateScan, IEEE TCAD (draft).']
half = (len(refs) + 1) // 2
for c in range(2):
    paras = [[(f'[{i+1}]  ', {'size': 9.5, 'bold': True, 'color': BLUE}), (refs[i], {'size': 9.5, 'color': INK})] for i in range(c * half, min(len(refs), (c + 1) * half))]
    tb(s36, 1.42 + c * 5.85, 1.3, 5.65, 5.3, paras, space_after=4)

s37 = D.new()
bg = rect(s37, 0, 0, 13.333, 7.5, NAV); gradient(bg, '0F2338', '0B4A75', 30)
tb(s37, 0.95, 1.6, 11.5, 1.4, [('Thank you', {'size': 72, 'bold': True, 'color': WHITE, 'font': HFONT})])
rect(s37, 1.0, 3.05, 1.2, 0.05, AMBER); rect(s37, 2.26, 3.05, 0.2, 0.05, '7FA7C9')
tb(s37, 0.95, 3.3, 11.5, 0.6, [('Questions and discussion', {'size': 26, 'color': AMBER, 'font': HFONT})])
tb(s37, 0.95, 4.3, 11.5, 1.4, [[('Ali Roshani', {'size': 18, 'bold': True, 'color': WHITE})],
                                [('Supervisors: Dr. Mohsen Ansari · Dr. Mohammad T. Manzuri Shalmani', {'size': 14, 'color': 'C9D6E3'})],
                                [('CPS Lab · Department of Computer Engineering · Sharif University of Technology', {'size': 14, 'color': 'C9D6E3'})],
                                [('github.com/aliroshanidino', {'size': 14, 'color': '9DC3E6'})]])
D.pager(s37, dark=True)
