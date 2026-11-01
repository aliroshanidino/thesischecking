"""Build the thesis progress deck in the visual style of the H-ASIZH paper deck.

Base file: the paper deck (reused slides keep their exact design); new slides are drawn
with the same design system. Output: thesis_deck.pptx
"""
import copy, re, sys
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from PIL import Image

BASE = '/home/user/knowledge_base/originals/H-ASIZH_paper_slides.pptx'  # paper deck (design + reused slides)
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/kb_work5/thesis_deck.pptx'
KB = '/home/user/knowledge_base'
FONT = 'Palatino Linotype'
NAVY, ACT, GOLD, RED, TEAL = '17262D', '21414B', 'E09F3E', 'C8553D', '0F5C6E'
BG, LINE, GREY, LIGHT, MUTED = 'FBFAF7', 'D7E0E2', '8FA6AD', 'E4EFF0', '6B7B83'
PALE = 'F2F6F7'; PEACH = 'FCEBD9'
DECK_LABEL = 'M.Sc. Thesis'
SECTIONS = ['Introduction', 'Literature', 'Methodology', 'Results', 'Conclusion']
SEC_FULL = ['INTRODUCTION', 'LITERATURE REVIEW', 'METHODOLOGY', 'RESULTS', 'CONCLUSION']

prs = Presentation(BASE)
orig = list(prs.slides)               # 0-based index = paper slide number - 1
BLANK = prs.slide_layouts[6]
LOGO = None
for sh in orig[3].shapes:
    if sh.shape_type == 13 and sh.name == 'Picture 3':
        LOGO = sh.image.blob
import io

def rgb(h): return RGBColor.from_string(h)

def _shape(slide, kind, x, y, w, h, fill=None, line=None, adj=None, lw=0.75):
    s = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill: s.fill.solid(); s.fill.fore_color.rgb = rgb(fill)
    else: s.fill.background()
    if line: s.line.color.rgb = rgb(line); s.line.width = Pt(lw)
    else: s.line.fill.background()
    if adj is not None and kind == MSO_SHAPE.ROUNDED_RECTANGLE: s.adjustments[0] = adj
    s.shadow.inherit = False
    st = s._element.find(qn('p:style'))
    if st is not None: s._element.remove(st)
    tf = s.text_frame; tf.margin_left = tf.margin_right = Inches(0.06); tf.margin_top = tf.margin_bottom = Inches(0.03)
    return s

def rect(slide, x, y, w, h, fill, line=None): return _shape(slide, MSO_SHAPE.RECTANGLE, x, y, w, h, fill, line)
def rrect(slide, x, y, w, h, fill='FFFFFF', line=LINE, adj=0.06): return _shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill, line, adj)
def oval(slide, x, y, d, fill):
    o = _shape(slide, MSO_SHAPE.OVAL, x, y, d, d, fill)
    tf = o.text_frame; tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0; tf.word_wrap = False
    return o

def write(shape_or_tf, paras, size=12, color=NAVY, bold=False, align='l', anchor=None, italic=False, spacing=None, space_after=None):
    """paras: list of paragraphs; paragraph = str or list of runs; run = str or (text, {opts})."""
    tf = shape_or_tf.text_frame if hasattr(shape_or_tf, 'text_frame') else shape_or_tf
    tf.word_wrap = True
    if anchor: tf.vertical_anchor = {'t': MSO_ANCHOR.TOP, 'm': MSO_ANCHOR.MIDDLE, 'b': MSO_ANCHOR.BOTTOM}[anchor]
    if isinstance(paras, str): paras = [paras]
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        for r in list(p.runs): r._r.getparent().remove(r._r)
        p.alignment = {'l': PP_ALIGN.LEFT, 'c': PP_ALIGN.CENTER, 'r': PP_ALIGN.RIGHT}[align]
        if spacing: p.line_spacing = spacing
        if space_after is not None: p.space_after = Pt(space_after)
        runs = [para] if isinstance(para, (str, tuple)) else para
        for r in runs:
            text, o = (r, {}) if isinstance(r, str) else r
            run = p.add_run(); run.text = text
            f = run.font; f.name = FONT; f.size = Pt(o.get('size', size)); f.bold = o.get('bold', bold)
            f.italic = o.get('italic', italic); f.color.rgb = rgb(o.get('color', color))
    return tf

def tb(slide, x, y, w, h, paras, **kw):
    s = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = s.text_frame; tf.margin_left = tf.margin_right = Inches(0.04); tf.margin_top = tf.margin_bottom = Inches(0.02)
    write(s, paras, **kw); return s

def picture(slide, path_or_blob, x, y, w, h, align='c'):
    src = io.BytesIO(path_or_blob) if isinstance(path_or_blob, bytes) else path_or_blob
    im = Image.open(src); iw, ih = im.size
    if isinstance(src, io.BytesIO): src.seek(0)
    r = min(w / iw, h / ih); pw, ph = iw * r, ih * r
    px = x + (w - pw) / 2 if align == 'c' else x
    return slide.shapes.add_picture(src, Inches(px), Inches(y + (h - ph) / 2), Inches(pw), Inches(ph))

DIVIDERS = {}

def link(shape, target):
    if target is not None: shape.click_action.target_slide = target

def chrome(slide, sec, title, footer=None):
    """Content-slide frame identical to the paper deck."""
    rect(slide, 0, 0, 13.333, 7.5, BG)
    rect(slide, 0, 0, 1.08, 7.5, NAVY)
    slide.shapes.add_picture(io.BytesIO(LOGO), Inches(0.24), Inches(0.26), Inches(0.6), Inches(0.6))
    for k, name in enumerate(SECTIONS):
        y = 1.35 + 1.02 * k
        r = rect(slide, 0, y, 1.08, 0.92, ACT if k + 1 == sec else NAVY)
        write(r, [[(f'0{k+1}', {'size': 17, 'bold': True, 'color': GOLD})], [(name, {'size': 8.5, 'color': 'FFFFFF'})]], align='c', anchor='m')
        link(r, DIVIDERS.get(k + 1))
        if k + 1 == sec: rect(slide, 0, y, 0.07, 0.92, GOLD)
    rect(slide, 0.3, 6.78, 0.48, 0.02, GREY)
    tb(slide, 0.06, 6.82, 0.96, 0.3, [(DECK_LABEL, {'size': 8, 'color': GREY})], align='c')
    tb(slide, 1.42, 0.28, 9.0, 0.3, [(f'0{sec}  ·  {SEC_FULL[sec-1]}', {'size': 10, 'bold': True, 'color': GOLD})])
    tb(slide, 1.42, 0.5, 11.5, 0.68, [(title, {'size': 26, 'color': NAVY})])
    rect(slide, 1.46, 1.17, 0.85, 0.04, GOLD)
    if footer: tb(slide, 1.42, 6.72, 10.0, 0.3, [(footer, {'size': 7, 'color': MUTED})])
    pager(slide, light=True)

def pager(slide, light=True):
    a = oval(slide, 11.6, 7.03, 0.3, LIGHT if light else ACT); write(a, [('‹', {'size': 10, 'bold': True, 'color': TEAL if light else 'FFFFFF'})], align='c', anchor='m')
    p = rrect(slide, 11.95, 7.03, 0.68, 0.3, TEAL if light else ACT, None, 0.5); write(p, [('0 / 0', {'size': 9.5, 'bold': True, 'color': 'FFFFFF'})], align='c', anchor='m')
    p.text_frame.margin_left = p.text_frame.margin_right = 0; p.text_frame.word_wrap = False
    b = oval(slide, 12.68, 7.03, 0.3, LIGHT if light else ACT); write(b, [('›', {'size': 10, 'bold': True, 'color': TEAL if light else 'FFFFFF'})], align='c', anchor='m')

def banner(slide, y, runs, h=0.55, fill=NAVY, x=1.42, w=11.5):
    b = rrect(slide, x, y, w, h, fill, None, 0.12)
    write(b, [runs], size=14, color='FFFFFF', align='c', anchor='m'); return b

def card(slide, x, y, w, h, head=None, body=None, num=None, numfill=RED, headsize=14, bodysize=11, fill='FFFFFF', tag=None):
    rrect(slide, x, y, w, h, fill)
    tx = x + 0.18
    if num is not None:
        o = oval(slide, x + 0.16, y + 0.15, 0.4, numfill); write(o, [(str(num), {'size': 11 if len(str(num)) == 1 else 9.5, 'bold': True, 'color': 'FFFFFF'})], align='c', anchor='m'); o.text_frame.word_wrap = False; tx = x + 0.66
    if head: tb(slide, tx, y + 0.1, w - (tx - x) - 0.12, 0.5, [(head, {'size': headsize, 'bold': True})], anchor='m')
    if tag:
        t = rrect(slide, x + w - 1.25, y - 0.17, 1.15, 0.32, GOLD, None, 0.5); write(t, [(tag, {'size': 9, 'bold': True, 'color': 'FFFFFF'})], align='c', anchor='m')
    if body:
        tb(slide, x + 0.18, y + (0.62 if head else 0.12), w - 0.34, h - (0.7 if head else 0.2), body, size=bodysize)

def table(slide, x, y, w, colw, rows, size=10, hsize=10.5, rowh=0.36, ours_last=True, first_bold=True, hfill=TEAL):
    nr, nc = len(rows), len(rows[0])
    gs = slide.shapes.add_table(nr, nc, Inches(x), Inches(y), Inches(w), Inches(rowh * nr))
    t = gs.table
    tot = sum(colw)
    for j, cw in enumerate(colw): t.columns[j].width = Inches(w * cw / tot)
    for i in range(nr):
        t.rows[i].height = Inches(rowh)
        for j in range(nc):
            c = t.cell(i, j); c.margin_left = c.margin_right = Inches(0.06); c.margin_top = c.margin_bottom = Inches(0.025)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            ours = ours_last and i == nr - 1
            if i == 0: fill, col, b, sz = hfill, 'FFFFFF', True, hsize
            elif ours: fill, col, b, sz = PEACH, RED, (j == 0 or True), size
            else: fill, col, b, sz = ('FFFFFF' if i % 2 else PALE), NAVY, (first_bold and j == 0), size
            c.fill.solid(); c.fill.fore_color.rgb = rgb(fill)
            val = rows[i][j]
            write(c, [(str(val), {'size': sz, 'bold': b, 'color': col})] if not isinstance(val, list) else val, size=sz, color=col, bold=b)
    return gs

def divider(slide, num, title, img, img_bg='FFFFFF'):
    rect(slide, 0, 0, 13.333, 7.5, NAVY)
    tb(slide, 0.9, 1.0, 3.6, 2.0, [(f'0{num}', {'size': 140, 'bold': True, 'color': GOLD})])
    tb(slide, 0.95, 3.35, 6.25, 1.15, [(title, {'size': 52, 'color': 'FFFFFF'})])
    rect(slide, 1.0, 4.8, 1.4, 0.05, GOLD)
    rrect(slide, 7.25, 0.95, 5.4, 5.15, img_bg, None, 0.04)
    picture(slide, img, 7.45, 1.15, 5.0, 4.75)
    for k, name in enumerate(['Introduction', 'Literature Review', 'Methodology', 'Results', 'Conclusion']):
        p = rrect(slide, 0.95 + 2.35 * k, 6.4, 2.15, 0.42, ACT if k + 1 == num else NAVY, None, 0.5)
        write(p, [(f'0{k+1}  {name}', {'size': 10, 'bold': True, 'color': GOLD if k + 1 == num else GREY})], align='c', anchor='m')
        link(p, DIVIDERS.get(k + 1))
    pager(slide, light=False)

def set_runs(shape, paras):
    """Replace text of an existing shape, keeping the first run's formatting of each paragraph."""
    tf = shape.text_frame; ps = list(tf.paragraphs)
    for i, text in enumerate(paras):
        p = ps[min(i, len(ps) - 1)] if i < len(ps) else None
        if p is None:
            newp = copy.deepcopy(ps[-1]._p); tf._txBody.append(newp); p = tf.paragraphs[-1]
        runs = p.runs
        if runs:
            runs[0].text = text
            for r in runs[1:]: r._r.getparent().remove(r._r)
        else:
            p.text = text
    for p in list(tf.paragraphs)[len(paras):]: p._p.getparent().remove(p._p)

def find(slide, sid): return next(s for s in slide.shapes if s.shape_id == sid)

# ---------------------------------------------------------------- reused slides
TITLE, OUTLINE, D1, D2, D3, D4 = orig[0], orig[1], orig[2], orig[12], orig[16], orig[26]
CTRL, LYAP, UARCH, HARD = orig[18], orig[19], orig[21], orig[23]
PPA, OUTC, RFOM, LEARN = orig[27], orig[28], orig[29], orig[30]
FUTURE, REF1, THANKS = orig[32], orig[33], orig[34]
DIVIDERS.update({1: D1, 2: D2, 3: D3, 4: D4})
SEIZURE_PIC = next(s for s in orig[7].shapes if s.shape_type == 13 and s.name == 'Picture 30').image.blob

set_runs(find(TITLE, 6), ['M.Sc. Thesis'])
set_runs(find(TITLE, 8), ['Design of a Fault-Tolerant Deep Neural Network Hardware Accelerator for Image and Video Processing Applications'])
find(TITLE, 8).text_frame.paragraphs[0].runs[0].font.size = Pt(21)
for para in find(TITLE, 9).text_frame.paragraphs:
    for r in para.runs:
        if 'Mohsen Ansari' in r.text: r.text = r.text.replace('Dr. Mohsen Ansari', 'Dr. M. Ansari  &  Dr. M. T. Manzuri Shalmani')
set_runs(find(OUTLINE, 21), ['Mission-critical vision, the edge device, and why its neuron must not fail'])
set_runs(find(OUTLINE, 28), ['Six families of prior work and where this thesis stands'])
set_runs(find(OUTLINE, 35), ['Hardened core → trustworthy fault analysis → BioVision'])
set_runs(find(OUTLINE, 42), ['PPA, fault campaign, RFoM, learning, BioVision'])
set_runs(find(OUTLINE, 49), ['Takeaways, publications and the road ahead'])
for (sid, a, b) in [(14, 'Hardened neuron', 'H-ASIZH + Lyapunov bound'), (17, 'Silicon core', '1-cycle Q7.19 on SkyWater 130 nm'),
                    (20, 'Control-plane hardening', 'light TMR + restoring organ'), (23, 'Fault analysis', 'GLFI → GateScan'),
                    (26, 'Vision system', 'BioVision-SNN')]:
    set_runs(find(D3, sid), [a, b])
set_runs(find(CTRL, 14), ['Phase 1 · The Intrinsic Homeostatic Controller'])
set_runs(find(LYAP, 14), ['Phase 1 · It Cannot Run Away: Lyapunov Bound'])
set_runs(find(UARCH, 14), ['Phase 1 · A One-Cycle Micro-Architecture'])
set_runs(find(HARD, 14), ['Phase 1 · Hardening the Control Plane'])
set_runs(find(LEARN, 14), ['Phase 1 · On-Chip Learning Case Study'])
set_runs(find(REF1, 14), ['References (I)'])
set_runs(find(FUTURE, 14), ['Future Work: Where This Goes Next'])
set_runs(find(FUTURE, 37), ['▸  Phases 0–1 done: retina emulator and colour ventral stream; next: location-wise readout, dorsal stream, attention, depth, border ownership',
                            '▸  Cross-layer campaign: gate-level fault outcomes injected per layer of the vision system'])
set_runs(find(FUTURE, 35), ['BioVision-SNN on fault-tolerant cores'])
for s in orig:
    for sh in s.shapes:
        if sh.has_text_frame and sh.text_frame.text.strip() == 'H-ASIZH' and sh.top > Inches(6.5):
            set_runs(sh, [DECK_LABEL])
# ---------------------------------------------------------------- new slides
R = {}  # reference keys -> numbers (paper deck uses 1..53; new ones from 54)
NEW_REFS = [
 ('sat09', 'M. Satyanarayanan et al., “The case for VM-based cloudlets in mobile computing,” IEEE Pervasive Comput., 2009.'),
 ('bon12', 'F. Bonomi et al., “Fog computing and its role in the Internet of Things,” in Proc. MCC Workshop, 2012.'),
 ('shi16', 'W. Shi et al., “Edge computing: Vision and challenges,” IEEE Internet Things J., 2016.'),
 ('kang17', 'Y. Kang et al., “Neurosurgeon: Collaborative intelligence between the cloud and mobile edge,” in Proc. ASPLOS, 2017.'),
 ('zhou19', 'Z. Zhou et al., “Edge intelligence: Paving the last mile of AI with edge computing,” Proc. IEEE, 2019.'),
 ('kai21', 'P. Kairouz et al., “Advances and open problems in federated learning,” Found. Trends Mach. Learn., 2021.'),
 ('pas21', 'D. Pasquini et al., “Unleashing the tiger: Inference attacks on split learning,” in Proc. ACM CCS, 2021.'),
 ('dean13', 'J. Dean and L. A. Barroso, “The tail at scale,” Commun. ACM, 2013.'),
 ('pot00', 'G. J. Pottie and W. J. Kaiser, “Wireless integrated network sensors,” Commun. ACM, 2000.'),
 ('koop16', 'P. Koopman and M. Wagner, “Challenges in autonomous vehicle testing and validation,” SAE Int. J. Transp. Safety, 2016.'),
 ('hoch21', 'P. H. Hochschild et al., “Cores that don’t count,” in Proc. HotOS, 2021.'),
 ('avi04', 'A. Avizienis et al., “Basic concepts and taxonomy of dependable and secure computing,” IEEE Trans. Dependable Secure Comput., 2004.'),
 ('eyer17', 'Y.-H. Chen et al., “Eyeriss: An energy-efficient reconfigurable accelerator for deep CNNs,” IEEE J. Solid-State Circuits, 2017.'),
 ('tpu17', 'N. P. Jouppi et al., “In-datacenter performance analysis of a tensor processing unit,” in Proc. ISCA, 2017.'),
 ('capra20', 'M. Capra et al., “Hardware and software optimizations for accelerating deep neural networks: Survey,” IEEE Access, 2020.'),
 ('suh23', 'D. Suh et al., low-precision SSD co-design for drone detection on a resource-constrained FPGA, ACM Trans. Reconfig. Technol. Syst., 2023, doi:10.1145/3583074.'),
 ('zhang18', 'J. J. Zhang et al., “Analyzing and mitigating the impact of permanent faults on a systolic array based neural network accelerator,” in Proc. IEEE VTS, 2018.'),
 ('li17', 'G. Li et al., “Understanding error propagation in deep learning neural network accelerators and applications,” in Proc. SC, 2017.'),
 ('ares18', 'B. Reagen et al., “Ares: A framework for quantifying the resilience of deep neural networks,” in Proc. DAC, 2018.'),
 ('fid20', 'Y. He, P. Balaprakash and Y. Li, “FIdelity: Efficient resilience analysis framework for deep learning accelerators,” in Proc. MICRO, 2020.'),
 ('fort25', '“FORTALESA: Fault-tolerant reconfigurable systolic array for DNN inference,” arXiv:2503.04426, 2025.'),
 ('ait24', 'Ait Alam et al., “Algorithmic strategies for sustainable reuse of neural network accelerators with permanent faults,” arXiv:2412.16208, 2024.'),
 ('ster23', 'L. Sterpone et al., SET-aware placement of CNN neuron cores on radiation-hardened FPGAs (RTG4), IEEE Trans. Comput.-Aided Design, 2023.'),
 ('ant25', 'Antunes and Podobas, “FPGA-based neural network accelerators for space applications: A survey,” arXiv:2504.16173, 2025.'),
 ('mero14', 'P. A. Merolla et al., “A million spiking-neuron integrated circuit with a scalable communication network and interface,” Science, 2014.'),
 ('furb14', 'S. B. Furber et al., “The SpiNNaker project,” Proc. IEEE, 2014.'),
 ('orch21', 'G. Orchard et al., “Efficient neuromorphic signal processing with Loihi 2,” in Proc. IEEE SiPS, 2021.'),
 ('morph19', 'C. Frenkel et al., “MorphIC: A 65-nm 738k-synapse/mm² quad-core binary-weight digital neuromorphic processor with stochastic spike-driven online learning,” IEEE Trans. Biomed. Circuits Syst., 2019.'),
 ('speck24', 'M. Yao et al., “Spike-based dynamic computing with asynchronous sensing-computing neuromorphic chip,” Nat. Commun., 2024.'),
 ('quant24', 'S. Matinizadeh et al., “QUANTISENC: A fully-configurable software-defined digital quantized spiking neural core architecture,” arXiv:2404.02248, 2024.'),
 ('sruthi25', 'P. V. Sruthi and T. S. Bindiya, “Modeling of Izhikevich spiking neurons with high matching accuracy using comb-exp functions and its multiplier-free realization,” IEEE Trans. Circuits Syst. I, 2025.'),
 ('falvolt', 'A. Siddique et al., “FalVolt: Fault-tolerant voltage scaling for neuromorphic architectures,” IEEE Trans. VLSI Syst., 2023.'),
 ('neuft24', 'NeuFT: astrocyte-inspired fault tolerance of FPGA-based neuromorphic hardware against SEUs, in Proc. IEEE DFT, 2024 (Drexel University).'),
 ('spy22', 'T. Spyrou et al., “Reliability analysis of a spiking neural network hardware accelerator,” in Proc. DATE, 2022.'),
 ('gleyo26', 'A. Gleyo and B. Girau, “Population coding to improve fault tolerance of neuromorphic networks in regression tasks,” in Proc. DATE, 2026.'),
 ('elsayed20', 'S. A. El-Sayed et al., “Spiking neuron hardware-level fault modeling,” in Proc. IEEE IOLTS, 2020.'),
 ('strat23', 'H.-G. Stratigopoulos et al., “Testing and reliability of spiking neural networks: A review of the state-of-the-art,” in Proc. IEEE DFT, 2023.'),
 ('radsafie', 'M. Monopoli et al., “RADSAFiE: A netlist-level fault injection user interface application for FPGA-based digital systems,” IEEE Access, 2025.'),
 ('enph22', 'A. Colucci, A. Steininger and M. Shafique, “enpheeph: A fault injection framework for spiking and compressed deep neural networks,” in Proc. IEEE/RSJ IROS, 2022.'),
 ('sjet24', 'A. B. Gogebakan et al., “SpikingJET: Enhancing fault injection for fully and convolutional spiking neural networks,” in Proc. IEEE IOLTS, 2024.'),
 ('spikefi', 'T. Spyrou et al., “SpikeFI: A fault injection framework for spiking neural networks,” arXiv:2412.06795, 2024.'),
 ('kher18', 'S. R. Kheradpisheh et al., “STDP-based spiking deep convolutional neural networks for object recognition,” Neural Netw., 2018.'),
 ('moz18', 'M. Mozafari et al., “First-spike-based visual categorization using reward-modulated STDP,” IEEE Trans. Neural Netw. Learn. Syst., 2018.'),
 ('syolo24', 'X. Luo et al., “Integer-valued training and spike-driven inference spiking neural network for high-performance and energy-efficient object detection,” in Proc. ECCV, 2024.'),
 ('pv19', 'F. Paredes-Vallés et al., “Unsupervised learning of a hierarchical spiking neural network for optical flow estimation,” IEEE Trans. Pattern Anal. Mach. Intell., 2019.'),
 ('stereo22', 'U. Rançon et al., “StereoSpike: Depth learning with a spiking neural network,” IEEE Access, 2022.'),
 ('wwn10', 'Z. Ji and J. Weng, “WWN-2: A biologically inspired neural network for concurrent visual attention and recognition,” in Proc. IJCNN, 2010.'),
 ('zhou00', 'H. Zhou, H. S. Friedman and R. von der Heydt, “Coding of border ownership in monkey visual cortex,” J. Neurosci., 2000.'),
 ('debes23', 'S. R. Debes and V. Dragoi, “Suppressing feedback signals to visual cortex abolishes attentional modulation,” Science, 2023.'),
 ('dvs08', 'P. Lichtsteiner, C. Posch and T. Delbruck, “A 128×128 120 dB 15 µs latency asynchronous temporal contrast vision sensor,” IEEE J. Solid-State Circuits, 2008.'),
 ('kher16', 'S. R. Kheradpisheh, M. Ganjtabesh and T. Masquelier, “Bio-inspired unsupervised learning of visual features leads to robust invariant object recognition,” Neurocomputing, 2016.'),
 ('brader07', 'J. M. Brader, W. Senn and S. Fusi, “Learning real-world stimuli in a neural network with spike-driven synaptic dynamics,” Neural Comput., 2007.'),
 ('agrel05', 'P. R. Roelfsema and A. van Ooyen, “Attention-gated reinforcement learning of internal representations for classification,” Neural Comput., 2005.'),
 ('spyke19', 'M. Mozafari et al., “SpykeTorch: Efficient simulation of convolutional spiking neural networks with at most one spike per neuron,” Front. Neurosci., 2019.'),
]
for k, (key, _) in enumerate(NEW_REFS): R[key] = 54 + k
def c(*keys): return '[' + ', '.join(str(R[k]) if isinstance(k, str) else str(k) for k in keys) + ']'

def S(): return prs.slides.add_slide(BLANK)

# 4 — Where should intelligence live?
s4 = S(); chrome(s4, 1, 'Where Should Intelligence Live?',
    f'[54] Satyanarayanan 2009   [55] Bonomi 2012   [56] Shi 2016   [57] Kang 2017   [58] Zhou 2019   [59] Kairouz 2021   [15] Kim 2007')
rrect(s4, 1.42, 1.42, 6.35, 4.05); picture(s4, f'{KB}/sources/figures/thesis_ch1_en/fig1-1_continuum_ladder.png', 1.52, 1.5, 6.15, 3.9)
card(s4, 7.95, 1.42, 4.98, 1.25, 'Mission-critical vision', [['UAVs, autonomous cars, robots and retinal implants: the camera is the ', ('first stage of a decision', {'bold': True}), ' that must be made in real time.']], num=1, headsize=13, bodysize=10.5)
card(s4, 7.95, 2.8, 4.98, 1.25, 'The systems answer: offloading', [f'Cloudlets, fog and MEC move servers closer {c("sat09","bon12","shi16")}; DNNs are split by layer {c("kang17")}; split & federated learning {c("zhou19","kai21")}.'], num=2, headsize=13, bodysize=10.5)
card(s4, 7.95, 4.18, 4.98, 1.29, 'Its hidden assumption', [['The end device is a ', ('black box that always computes correctly', {'bold': True}), '; only its speed matters.']], num=3, headsize=13, bodysize=10.5)
banner(s4, 5.68, [('Down the ladder, power, heat headroom and repairability vanish — ', {}), ('an implant must stay within ≈ +1 °C', {'bold': True, 'color': GOLD})])

# 5 — Why offloading fails safety-critical vision
s5 = S(); chrome(s5, 1, 'Why Offloading Fails Safety-Critical Vision',
    f'[61] Dean & Barroso 2013   [62] Pottie & Kaiser 2000   [60] Pasquini 2021   [63] Koopman & Wagner 2016   [64] Hochschild 2021')
groups = [
 ('Time & determinism', f'Tail latency: 1 % slow × 100 servers → 63 % slow {c("dean13")}; no worst-case bound; handover outages; model/state skew'),
 ('Connectivity', 'Coverage gaps, jamming, radio loss in tissue and under water, cascading infrastructure failure'),
 ('Energy & heat', f'1 kbit over 100 m ≈ 3 M instructions {c("pot00")}; video saturates the uplink; radio heat and retransmissions'),
 ('Security & privacy', f'Every hop is an attack surface; split learning leaks raw data {c("pas21")}; trust in the operator'),
 ('Certification', f'IEC 61508 / ISO 26262 need a bounded system {c("koop16")}; unknown fault-containment boundary; liability'),
 ('Silent corruption', f'Even cloud cores corrupt data silently {c("hoch21")}; the remote node is not a safe harbour'),
 ('Scale & cost', 'Spectrum capacity, deployment and upkeep of the infrastructure'),
 ('Environment & modelling', 'Radiation, heat and vibration hit the device anyway; offloading optimisers assume a fixed network model'),
]
for k, (h, b) in enumerate(groups):
    x = 1.42 + (k % 4) * 2.92; y = 1.42 + (k // 4) * 2.05
    card(s5, x, y, 2.78, 1.92, h, [b], num=k + 1, headsize=12, bodysize=9.5)
banner(s5, 5.68, [('24 weaknesses in 8 groups → ', {}), ('the critical perception–decision loop must close on the device itself', {'bold': True, 'color': GOLD})])

# 6 — Two anchors + why spikes
s6 = S(); chrome(s6, 1, 'Our Anchor: Build the Extreme-Edge Device',
    f'[68] Capra 2020   [15] Kim 2007   [7] Roy 2019   [10] Akopyan 2015   [11] Davies 2018   [67] Jouppi 2017')
card(s6, 1.42, 1.42, 3.7, 1.85, 'A1 · Extreme edge', [['The safety-critical loop closes ', ('on the device', {'bold': True}), '; offloading stays for training, maps and analytics.']], num='A1', numfill=TEAL, headsize=13, bodysize=10.5)
card(s6, 1.42, 3.42, 3.7, 1.85, 'A2 · Purpose-built device', [['A device ', ('designed for this task', {'bold': True}), ' — image and video — under size, weight, power, heat and cost limits.']], num='A2', numfill=TEAL, headsize=13, bodysize=10.5)
rrect(s6, 5.3, 1.42, 3.75, 3.85)
tb(s6, 5.45, 1.5, 3.5, 0.4, [('Power envelope down the ladder', {'size': 13, 'bold': True})])
table(s6, 5.45, 1.95, 3.45, [1.4, 1.2], [['Platform', 'Typical power'], ['CPU', '10–100 W'], ['GPU', '≈ 100 W'], ['FPGA', '1–10 W'], ['ASIC accelerator', '0.1–1 W'], ['Brain implant', 'tens of mW (≈ +1 °C)']], size=10, rowh=0.5, ours_last=True)
card(s6, 9.23, 1.42, 3.7, 3.85, 'Why spikes', [
    ['▸  Brain: 10¹¹ neurons at ≈ 20 W ', (c(7), {})],
    '▸  Event-driven, sparse, memory beside compute',
    ['▸  ', ('Dense NPU', {'bold': True}), ' (TPU, phone NPU) ≠ ', ('neuromorphic processor', {'bold': True}), ': lower throughput, far lower power and heat'],
    ['▸  Chips exist: TrueNorth, Loihi ', (c(10, 11), {})]], num=3, headsize=13, bodysize=10.5)
banner(s6, 5.68, [('Device + spikes: ', {}), ('a spiking accelerator for vision that must also be dependable', {'bold': True, 'color': GOLD})])

# 7 — Inside a time-multiplexed SNN accelerator
s7 = S(); chrome(s7, 1, 'Inside a Time-Multiplexed SNN Accelerator: Who Can Fail?',
    f'[52] Frenkel 2019 (ODIN)   [17] Vatajelu 2019   [24] Spyrou 2021   [16] Hill 2022')
rrect(s7, 1.42, 1.42, 5.6, 4.0)
tb(s7, 1.58, 1.5, 5.3, 0.4, [('ODIN-style accelerator ', {'size': 13, 'bold': True}), (c(52), {'size': 11, 'color': MUTED})])
blocks = [('Central controller / FSM', 1.62, 2.05, 2.5, 0.75, NAVY), ('Network-on-chip / AER router', 4.32, 2.05, 2.5, 0.75, NAVY),
          ('Neuron-state & weight memory', 1.62, 3.05, 2.5, 0.75, NAVY), ('Neuron core ×1…5 (time-multiplexed)', 4.32, 3.05, 2.5, 0.75, RED)]
for (t, x, y, w, h, f) in blocks:
    b = rrect(s7, x, y, w, h, f, None, 0.1); write(b, [(t, {'size': 11, 'bold': True, 'color': 'FFFFFF'})], align='c', anchor='m')
tb(s7, 1.62, 4.0, 5.2, 1.35, [['One core serves ', ('hundreds of virtual neurons', {'bold': True}), ': a single permanent defect in it reaches every neuron mapped onto it.'],
                               ['Four vulnerable parts — ', ('this thesis hardens the neuron core first', {'bold': True, 'color': RED}), '.']], size=11)
rrect(s7, 7.2, 1.42, 5.73, 4.0); picture(s7, SEIZURE_PIC, 7.35, 1.5, 5.45, 3.4)
tb(s7, 7.35, 4.95, 5.45, 0.4, [('SA1 → parasitic current → digital seizure;  SA0 → silence  ' + c(17, 24), {'size': 10, 'italic': True, 'color': MUTED})], align='c')
banner(s7, 5.68, [('TMR masks it at ', {}), ('3.40× the cells', {'bold': True, 'color': GOLD}), (' — the extreme edge cannot pay for triplication', {})])

# 8 — Research gaps
s8 = S(); chrome(s8, 1, 'Research Gaps',
    '[57] Kang 2017  [58] Zhou 2019  [17] Vatajelu 2019  [18] Schuman 2020  [19] Lyons 1962  [22] ReSpawn  [34] RescueSNN  [21] SPANNER  [46] Johnson 2018  [47] Das 2025  [25] Leveugle 2009  [26] SHADOWFI')
gaps = [('The device is an ideal black box', f'Edge-intelligence research optimises placement and assumes a correct device {c("kang17","zhou19")}.'),
        ('No dependable path for vision at the extreme edge', f'Neuromorphic + event vision is efficient, but its behaviour under permanent faults is little studied {c(17, 18)}.'),
        ('Fault tolerance does not scale down', f'TMR ≈ 3× {c(19)}; SNN schemes need spares, fault maps, re-mapping {c(22, 34)}; supervisors are unprotected {c(21, 46)}.'),
        ('The neuron is a primitive, not a design object', f'Protection acts on, around or above the neuron; no proven bound on its behaviour {c(24, 47)}.'),
        ('Evaluation is not physically faithful', f'Software or two-valued campaigns; faithful gate-level tools are closed and costly {c(25, 26)}.'),
        ('Dependability and learning are studied apart', 'Fault tolerance is tested on frozen networks; compatibility with on-chip learning is rarely shown.')]
for k, (h, b) in enumerate(gaps):
    y = 1.38 + k * 0.86
    rrect(s8, 1.42, y, 11.5, 0.76)
    o = oval(s8, 1.6, y + 0.16, 0.44, RED); write(o, [(f'G{k+1}', {'size': 11, 'bold': True, 'color': 'FFFFFF'})], align='c', anchor='m')
    tb(s8, 2.22, y + 0.04, 3.9, 0.68, [(h, {'size': 12.5, 'bold': True})], anchor='m')
    tb(s8, 6.2, y + 0.04, 6.6, 0.68, [(b, {'size': 10.5})], anchor='m')

# 9 — Research questions & contributions
s9 = S(); chrome(s9, 1, 'Research Questions and Contributions')
rrect(s9, 1.42, 1.42, 4.75, 5.1); picture(s9, f'{KB}/sources/figures/thesis_ch1_en/fig1-2_research_journey.png', 1.5, 1.48, 4.6, 4.98)
contrib = [('System argument', 'Safety-critical vision must close its loop on the device; fault tolerance moves down the stack.', 'Ch. 1–3'),
           ('H-ASIZH neuron', 'Exact affine map + homeostatic threshold; Lyapunov proof of a uniformly ultimately bounded rate.', 'Ch. 4'),
           ('Hardware-ready core', 'Powers-of-two DSE, 1-cycle Q7.19 datapath, restoring-organ control plane, P&R on Sky130.', 'Ch. 5'),
           ('Trustworthy fault analysis', 'GLFI: four-valued, in-circuit saboteurs → GateScan: certified vulnerability bracket.', 'Ch. 6'),
           ('Neuron → vision system', 'On-chip STDP learning; BioVision-SNN: retina, ventral & dorsal streams, local learning.', 'Ch. 7–8')]
for k, (h, b, ch) in enumerate(contrib):
    y = 1.42 + k * 1.03
    rrect(s9, 6.35, y, 6.58, 0.93)
    o = oval(s9, 6.5, y + 0.22, 0.48, TEAL); write(o, [(f'C{k+1}', {'size': 11, 'bold': True, 'color': 'FFFFFF'})], align='c', anchor='m')
    tb(s9, 7.1, y + 0.06, 4.6, 0.36, [(h, {'size': 12.5, 'bold': True})])
    tb(s9, 7.1, y + 0.4, 5.7, 0.5, [(b, {'size': 10})])
    t = rrect(s9, 11.75, y + 0.08, 1.05, 0.28, LIGHT, None, 0.5); write(t, [(ch, {'size': 8.5, 'bold': True, 'color': TEAL})], align='c', anchor='m')

# 11 — A & B accelerators
s11 = S(); chrome(s11, 2, 'Accelerators for Vision: Fast, but Assumed Correct',
    '[66] Eyeriss  [67] TPU  [69] Suh 2023  [70] Zhang 2018  [71] Li 2017  [72] Ares  [42] SalvageDNN  [29] Libano 2019  [74] FORTALESA  [75] Ait Alam 2024  [76] Sterpone 2023  [77] Antunes 2025')
table(s11, 1.42, 1.4, 11.5, [2.0, 1.05, 2.7, 1.35, 3.0], [
 ['Work', 'Class', 'Mechanism', 'Fault model', 'Limitation at the extreme edge'],
 [f'Eyeriss {c("eyer17")}', 'A · ASIC', 'Row-stationary dataflow; AlexNet conv 34.7 fps @ 278 mW', '—', 'Assumes correct hardware'],
 [f'TPU {c("tpu17")}', 'A · ASIC', 'Systolic array; 15–30× faster than CPU/GPU', '—', 'Data-centre power'],
 [f'UAV detector on FPGA {c("suh23")}', 'A · FPGA', 'Low-precision SSD co-design', '—', '2.54 W; no protection'],
 [f'Zhang et al. {c("zhang18")}', 'B · systolic', 'Fault-aware pruning + retraining', 'Permanent', 'Needs fault map and retraining'],
 [f'Li / Ares {c("li17","ares18")}', 'B · analysis', 'Error propagation, resilience quantification', 'Transient', 'Analysis only'],
 [f'SalvageDNN {c(42)}', 'B · mapping', 'Saliency-driven fault-aware mapping', 'Permanent', 'Diagnosis + re-mapping'],
 [f'FORTALESA / reuse {c("fort25","ait24")}', 'B · systolic', 'Reconfigurable PE protection; algorithmic reuse', 'Trans. + perm.', 'Redundancy inside the PE'],
 [f'Space CNN / YOLO {c("ster23","ant25")}', 'B · FPGA', 'TMR / NMR, scrubbing, SET-aware placement', 'SEU', '≈ 3× area and power'],
 ['None of the above', '—', 'Spiking computation', '—', 'Not event-driven, not µW-scale']], size=9.5, hsize=10, rowh=0.44)
banner(s11, 5.95, [('Protection sits ', {}), ('on, around or above', {'bold': True, 'color': GOLD}), (' the processing element — and none of it is spiking', {})], h=0.5)

# 12 — C neuromorphic processors
s12 = S(); chrome(s12, 2, 'Neuromorphic Processors and Neuron Cores',
    '[10] Akopyan 2015  [78] Merolla 2014  [79] Furber 2014  [11] Davies 2018  [80] Orchard 2021  [52] Frenkel 2019  [81] MorphIC  [82] Speck  [83] QUANTISENC  [13] Haghiri 2018  [84] Sruthi 2025')
table(s12, 1.42, 1.4, 11.5, [2.2, 1.35, 2.6, 3.3, 1.3], [
 ['Chip / core', 'Year · node', 'Neurons', 'Highlight', 'Fault tolerance'],
 [f'TrueNorth {c(10, "mero14")}', '2014 · 28 nm', '1 M, 256 M synapses', '≈ 65 mW real time', 'Not a target'],
 [f'SpiNNaker {c("furb14")}', '2014', 'ARM many-core', 'Large-scale real-time simulation', 'Not a target'],
 [f'Loihi / Loihi 2 {c(11, "orch21")}', '2018 / 2021', 'Programmable', 'On-chip learning', 'Not a target'],
 [f'ODIN {c(52)}', '2019 · 28 nm', '256 · LIF or 20 Izhikevich behaviours', '0.086 mm², 12.7 pJ/SOP, time-multiplexed', 'Not a target'],
 [f'MorphIC {c("morph19")}', '2019 · 65 nm', '4 × 512 LIF', 'Binary weights, hierarchical routing', 'Not a target'],
 [f'Speck {c("speck24")}', '2024', '327k-neuron CNN + DVS', 'Clockless; 0.70 mW system', 'Not a target'],
 [f'QUANTISENC {c("quant24")}', '2024', 'Configurable LIF', 'Software-defined fixed-point cores', 'Not a target'],
 [f'Multiplier-free Izhikevich {c(13, "sruthi25")}', '2018–2025', 'Izhikevich', 'Shift-add, PWL / comb-exp', 'Not a target']], size=9.5, hsize=10, rowh=0.44, ours_last=False)
banner(s12, 5.68, [('A time-multiplexed core is a single point of failure for hundreds of neurons — ', {}), ('yet no core protects itself', {'bold': True, 'color': GOLD})])

# 13 — D FT in SNN hardware
s13 = S(); chrome(s13, 2, 'Fault Tolerance in SNN Hardware, Layer by Layer',
    '[37] SoftSNN [35] SparkXD [36] EnforceSNN [22] ReSpawn [34] RescueSNN [23] MigSpike [38,40] 3D-NoC [21] SPANNER [43–45] astrocytes [86] NeuFT [46] Johnson [24,87] Spyrou [47] Das [88] Gleyo [90] Stratigopoulos')
table(s13, 1.42, 1.38, 11.5, [1.55, 2.45, 2.75, 1.45, 3.0], [
 ['Layer', 'Representative work', 'Mechanism', 'Fault model', 'Cost / weakness'],
 ['System & memory', f'SoftSNN, SparkXD, EnforceSNN {c(37, 35, 36)}', 'Bound-and-protect; approximate DRAM', 'Soft / memory', 'Transient only; relative PPA'],
 ['Mapping & NoC', f'ReSpawn, RescueSNN, MigSpike, 3D-NoC {c(22, 34, 23, 38)}', 'Fault-aware mapping, migration', 'Permanent', 'Spares + fault map; timing tied to one die'],
 ['Bio-inspired supervisor', f'SPANNER, astrocyte nets, NeuFT {c(21, 44, "neuft24")}', 'Astrocyte-like monitor beside the neurons', 'Synapse / SEU', 'Supervisor on the same die is unprotected'],
 ['External homeostasis', f'Johnson et al. {c(46)}', 'Astrocyte-driven regulation', 'Permanent', 'Regulator ≠ neuron'],
 ['Neuron & structure', f'Spyrou, dendritic, population coding {c(24, 47, "gleyo26")}', 'Self-test + output TMR; structural; redundant populations', 'Dead / saturated', 'Behavioural only; ≈ 60 % overhead; extra neurons'],
 ['Neuron-intrinsic (this thesis)', 'H-ASIZH', 'Adaptive threshold as a state variable + restoring organ', 'Stuck-at, every node', '1.39× cells (2.31× hardened); proven bound']], size=9.5, hsize=10, rowh=0.6)
banner(s13, 5.85, [('Every branch acts on, around or above the neuron — ', {}), ('none acts inside it', {'bold': True, 'color': GOLD})], h=0.5)

# 14 — E FI tools
s14 = S(); chrome(s14, 2, 'Fault-Injection and Reliability Tools',
    '[26] SHADOWFI  [91] RADSAFiE  [73] FIdelity  [92] enpheeph  [93] SpikingJET  [94] SpikeFI  [89] El-Sayed  [25] Leveugle 2009')
table(s14, 1.42, 1.4, 11.5, [2.6, 2.3, 0.8, 1.0, 4.0], [
 ['Tool', 'Injection level', 'Open', '4-valued', 'Note'],
 ['Synopsys FuSa / fault simulator', 'Gate', '✗', '✓', 'Licensed, ISO 26262; hard to reproduce outside'],
 [f'SHADOWFI {c(26)}', 'Netlist (ASIC)', '✓', '✗', 'Hyperscale; injection outside the design; Verilog only'],
 [f'RADSAFiE {c("radsafie")}', 'Netlist (FPGA)', '✗', '✗', 'Vendor-locked to Vivado'],
 [f'FIdelity {c("fid20")}', 'SW model of accelerator RTL', '—', '—', '46 M injections on NVDLA; transient logic faults'],
 [f'enpheeph / SpikingJET / SpikeFI {c("enph22", "sjet24", "spikefi")}', 'Software (SNN)', '✓', '✗', 'No hardware fidelity'],
 [f'El-Sayed et al. {c("elsayed20")}', 'Netlist / transistor', '✓', '✗', 'Neuron fault models; no automated campaign'],
 ['GLFI → GateScan (this thesis)', 'Gate, in-circuit saboteurs', '✓', '✓', 'Dual-engine, formal oracle, certified bracket']], size=10, hsize=10.5, rowh=0.5)
banner(s14, 5.68, [('Without X/Z and cross-checks, robustness describes ', {}), ('the model, not the circuit', {'bold': True, 'color': GOLD}), (' ' + c(25), {'size': 11})])

# 15 — F bio-inspired spiking vision
s15 = S(); chrome(s15, 2, 'Bio-Inspired Spiking Vision Systems',
    '[95] Kheradpisheh 2018 [96] Mozafari 2018 [98] Paredes-Vallés 2019 [99] StereoSpike [100] WWN-2 [97] SpikeYOLO [82] Speck [101] Zhou 2000 [102] Debes & Dragoi 2023')
table(s15, 1.42, 1.38, 11.5, [2.35, 1.35, 1.5, 1.6, 1.75, 2.95], [
 ['Work', 'Spiking', 'Local learning', 'Streams', 'Attention', 'Output'],
 [f'Kheradpisheh 2018 {c("kher18")}', '✓ TTFS', 'STDP', 'Ventral', '—', 'Class'],
 [f'Mozafari 2018 {c("moz18")}', '✓ TTFS', 'R-STDP', 'Ventral', '—', 'Class'],
 [f'Paredes-Vallés 2019 {c("pv19")}', '✓ events', 'STDP', 'Motion', '—', 'Optical flow'],
 [f'StereoSpike 2022 {c("stereo22")}', '✓', '✗ surrogate', '—', '—', 'Dense depth'],
 [f'WWN-2 2010 {c("wwn10")}', '✗', 'Hebbian', 'What + where', 'Top-down', 'Location + identity'],
 [f'SpikeYOLO 2024 {c("syolo24")}', '✓ I-LIF', '✗ backprop', '—', '—', 'Boxes: COCO 66.2 mAP@50'],
 [f'Speck 2024 {c("speck24")}', '✓ + DVS', '✗', '—', 'Dynamic', 'Class at 0.70 mW'],
 ['BioVision-SNN (this thesis)', '✓ TTFS waves', 'STDP / R-STDP', 'Ventral + dorsal', 'Feedback to LGN', 'What-where, depth, motion, identity']], size=9.5, hsize=10, rowh=0.47)
banner(s15, 5.85, [('No spiking model learns ', {}), ('border ownership', {'bold': True, 'color': GOLD}), (f' locally; feedback attention is shown in biology {c("debes23")}', {})], h=0.5)

# 16 — Positioning matrix
s16 = S(); chrome(s16, 2, 'Where This Thesis Stands')
Y, N, P = '✓', '✗', '◐'
table(s16, 1.42, 1.35, 11.5, [2.9, 0.9, 1.05, 0.9, 1.1, 1.05, 1.0, 1.1, 1.1], [
 ['Work', 'Vision', 'HW (RTL/ASIC)', 'Spiking', 'Fault-tolerant', 'Permanent faults', 'Formal bound', 'Gate-level 4-valued', 'Local learning'],
 ['Eyeriss, TPU', Y, Y, N, N, N, N, N, N],
 ['Zhang 2018, SalvageDNN', Y, Y, N, Y, Y, N, N, N],
 ['Space CNN / YOLO + TMR', Y, P, N, Y, P, N, N, N],
 ['ODIN, MorphIC, Speck', P, Y, Y, N, N, N, N, P],
 ['SoftSNN, RescueSNN', P, Y, Y, Y, P, N, N, N],
 ['SPANNER, NeuFT, Johnson', N, P, Y, Y, P, N, N, N],
 ['Spyrou 2021, population coding', P, N, Y, Y, Y, N, N, N],
 ['SpikeYOLO', Y, N, Y, N, N, N, N, N],
 ['Kheradpisheh / Mozafari', Y, N, Y, N, N, N, N, Y],
 ['This thesis', Y, Y, Y, Y, Y, Y, Y, Y]], size=10.5, hsize=9.5, rowh=0.43)
tb(s16, 1.42, 6.2, 11.5, 0.35, [('✓ yes   ◐ partly   ✗ no — references on the previous five slides', {'size': 9.5, 'italic': True, 'color': MUTED})])

# 18 — Methodology overview
s18 = S(); chrome(s18, 3, 'Methodology: Three Phases, One Device')
phases = [('Phase 1', 'Harden the neuron core', ['Exact affine map of Izhikevich', 'Homeostatic threshold controller', 'Lyapunov UUB proof; powers-of-two DSE', '1-cycle Q7.19 RTL; restoring organ', 'P&R on SkyWater 130 nm', 'Extended to LIF / IF cores'], 'done'),
          ('Phase 2', 'Trust the measurement', ['GLFI: in-circuit saboteurs, 4-valued', 'Neuro-metric fault classes', 'GateScan: dual-engine (Verilator + Icarus)', 'Formal oracle, exact statistics', 'Certified vulnerability bracket', 'LLM agents propose; the core decides'], 'done'),
          ('Phase 3', 'Build the vision system', ['BioVision-SNN: retina outside the network', 'Ventral + dorsal streams, attention', 'TTFS waves, STDP / R-STDP only', 'Multiplier-free (shift-add) learning', 'Phase 0–1 done; 2–5 to go', 'Then: cross-layer fault campaign'], 'in progress')]
for k, (ph, h, items, tag) in enumerate(phases):
    x = 1.42 + k * 3.9
    card(s18, x, 1.5, 3.65, 3.95, f'{ph} · {h}', [f'▸  {t}' for t in items], headsize=13, bodysize=11, tag=tag)
    if k < 2: tb(s18, x + 3.6, 3.15, 0.35, 0.5, [('→', {'size': 22, 'bold': True, 'color': GOLD})], align='c')
banner(s18, 5.68, [('Time-multiplexing makes the core the single point of failure → ', {}), ('harden it, prove it, measure it, deploy it', {'bold': True, 'color': GOLD})])

# 24 — Phase 2 GLFI → GateScan
s24 = S(); chrome(s24, 3, 'Phase 2 · From GLFI to GateScan',
    '[25] Leveugle 2009   [26] SHADOWFI   GateScan Mark III.1 (github.com/gatescan-dev/gatescanMarkIII)')
rrect(s24, 1.42, 1.42, 6.2, 2.85); picture(s24, f'{KB}/sources/figures/paper/fig07_glfi_framework.png', 1.5, 1.5, 6.05, 2.7)
card(s24, 1.42, 4.4, 6.2, 1.2, None, [[('Shadow hook, compiled into the netlist: ', {'bold': True}), ('assign net = (fi_enable && fi_target_id==ID) ? fi_value : hook_net;', {'size': 10, 'color': TEAL})],
                                      'One instrumented netlist for the whole campaign; fi_value can force 0, 1, X or Z.'], bodysize=10.5)
card(s24, 7.8, 1.42, 5.13, 4.18, 'GateScan Mark III', [
    '▸  A certified bracket instead of one SDC %: lower = proven detections, upper = all but proven-harmless',
    '▸  Exact intervals: Clopper–Pearson, hypergeometric, census',
    '▸  Escape certificate and an 11-class taxonomy beside SDC/DUE/Masked',
    '▸  Two engines (Verilator + Icarus/cocotb) and a formal oracle',
    '▸  LLM agents only propose workloads; a wrong agent can widen the bracket, never falsify it',
    [('▸  1,834 two-engine runs, 0 disagreements; 13–55 % of “masked” faults proven vulnerable', {'bold': True})]], headsize=13, bodysize=10.5, num=2, numfill=TEAL)
banner(s24, 5.78, [('GLFI asked “is the neuron robust?” — GateScan asks ', {}), ('“can we trust the answer?”', {'bold': True, 'color': GOLD})], h=0.5)

# 25 — Phase 3 BioVision architecture
s25 = S(); chrome(s25, 3, 'Phase 3 · BioVision-SNN Architecture',
    '[95] Kheradpisheh 2018  [96] Mozafari 2018  [101] Zhou 2000  [102] Debes & Dragoi 2023  [103] Lichtsteiner 2008  [107] SpykeTorch')
rrect(s25, 1.42, 1.38, 4.2, 5.12); picture(s25, f'{KB}/sources/biovision/media_architecture/image1.png', 1.5, 1.45, 4.05, 4.98)
rows = [('Retina (fixed)', 'P / K / M channels, DoG, divisive normalisation, intensity→latency; microsaccade events (no DVS camera)'),
        ('LGN', 'Relay + attention gate: attended spikes fire earlier (δ = 3 steps); virtual fovea'),
        ('V1 · V2', 'S1 12 maps (1,800 weights), C1 = earliest spike; thin / pale / thick stripes; direction-selective cells'),
        ('Ventral', 'V4 (64) → IT (128); location-wise R-STDP readout: silence = background'),
        ('Dorsal', 'MT (aperture problem), V3 motion contrast, MST heading and time-to-contact'),
        ('Depth · select', '5 monocular cues; priority map with k-WTA replaces NMS; PFC object files keep identity'),
        ('Output', 'Token o = (position, mask, class, depth, velocity, TTC, id); border ownership B±')]
for k, (h, b) in enumerate(rows):
    y = 1.38 + k * 0.6
    rrect(s25, 5.8, y, 7.13, 0.53)
    tb(s25, 5.92, y + 0.03, 1.45, 0.47, [(h, {'size': 11, 'bold': True, 'color': TEAL})], anchor='m')
    tb(s25, 7.4, y + 0.03, 5.45, 0.47, [(b, {'size': 9.5})], anchor='m')
banner(s25, 5.68, [('TTFS waves: one spike per neuron per wave; worst-case ', {}), ('≈ 46 ms', {'bold': True, 'color': GOLD}), (' (wave 1), ', {}), ('≈ 91 ms', {'bold': True, 'color': GOLD}), (' (wave 2); ≈ 156k weights', {})], x=5.8, w=7.13, h=0.82)

# 26 — Phase 3 hardware-aware learning
s26 = S(); chrome(s26, 3, 'Phase 3 · Hardware-Aware Retina and Learning',
    '[104] Kheradpisheh 2016  [105] Brader 2007  [106] Roelfsema & van Ooyen 2005  [96] Mozafari 2018')
cards26 = [('Log-domain retina', ['Binomial filters instead of Gaussians', 'Mitchell log: error ≤ 0.0861 octave', 'Divisive normalisation = one subtraction', 'Brightness invariance ≤ 0.172 octave'], TEAL),
           ('Multiplier-free learning', ['s(w) = ½·min(w, 1−w) replaces w(1−w)', 'Rates = sums of two powers of two', '16-bit weights; 24–29-bit accumulators', 'Accuracy cost ≈ 0 vs. floating point'], TEAL),
           ('H-ASIZH inside TTFS', ['θ ← θ + α(θ₀ − θ) + γ·z per image', 'Calcium C = (α/γ)(θ − θ₀) ∈ [0, 1]', 'β-brake moved into plasticity', 'Floor θ ≥ θ₀ silenced S1 → two-sided rate homeostasis (Homeostasis 2.0)'], RED),
           ('Reward learning', ['First-spike R-STDP decision layer', 'Per-neuron calcium adaptive rate', f'AGREL attention rule for hidden layers {c("agrel05")}: +15 % on ETH-80', f'SDSP / R-SDSP tested {c("brader07")}'], TEAL)]
for k, (h, items, col) in enumerate(cards26):
    x = 1.42 + k * 2.92
    card(s26, x, 1.42, 2.78, 3.4, h, [f'▸  {t}' for t in items], num=k + 1, numfill=col, headsize=12, bodysize=11)
plan = ['0 · Reproduce', '1 · Colour ventral', '2 · Where (readout)', '3 · Dorsal & waves', '4 · Attention, depth', '5 · Borders, faults']
for k, t in enumerate(plan):
    p = rrect(s26, 1.42 + k * 1.93, 5.0, 1.83, 0.45, TEAL if k == 0 else (GOLD if k == 1 else LIGHT), None, 0.5)
    write(p, [(t, {'size': 9.5, 'bold': True, 'color': 'FFFFFF' if k < 2 else TEAL})], align='c', anchor='m')
banner(s26, 5.68, [('Two design rules for every block: ', {}), ('a biological counterpart', {'bold': True, 'color': GOLD}), (' and ', {}), ('shift-add-compare hardware', {'bold': True, 'color': GOLD})])

# 32 — BioVision results
s32 = S(); chrome(s32, 4, 'BioVision-SNN: Results So Far (Phases 0–1)',
    '[95] Kheradpisheh 2018 (SDNN)  [96] Mozafari 2018  — all numbers: test accuracy, mean ± std over seeds / folds; Phase 0 gate closed 2026-10-20')
table(s32, 1.42, 1.4, 6.6, [2.6, 1.6, 1.9], [
 ['Phase 0 (test %)', 'Paper', 'Ours'],
 ['RL · Caltech (Mozafari)', '98.9 ± 0.4', '98.65 ± 0.49'],
 ['RL · ETH-80 leave-one-out', '89.5 ± 1.9', '81.83 ± 5.58'],
 ['Probe · Caltech (SDNN)', '99.1 ± 0.2', '98.96 ± 0.25'],
 ['Probe · MNIST (SDNN)', '98.4', '98.52 ± 0.06'],
 ['Probe · ETH-80 5/5 (SDNN)', '82.8', '84.25 ± 3.49'],
 ['Multiplier-free mode', '—', '−0.9 / +1.7 pp']], size=10.5, hsize=11, rowh=0.48, ours_last=False)
tb(s32, 1.42, 4.85, 6.6, 0.75, [[('H-ASIZH threshold', {'bold': True, 'color': RED}), ' gave the best ETH-80 features (84.25 %); per-neuron calcium rate matched Mozafari on Caltech; decisions with < 1,000 input spikes.']], size=10.5)
card(s32, 8.2, 1.4, 4.73, 4.15, 'Phase 1 (draft, 128 px)', [
    '▸  Colour helps: P+K +6.7 pp over grey (RL, ETH-80 val.)',
    '▸  RL ETH-80 test: 72.87 ± 2.22 (decision still rising at epoch 80)',
    '▸  Caltech-4, grey retina: 89.42 ± 1.18',
    '▸  Darker images: invariant (log-domain theorem)',
    '▸  Gamma 0.5 collapsed accuracy → contrast adaptation (running)',
    '▸  Found and fixed: K-channel background artefact, power-of-two rate collapse, 3 errors in the design maths (107 unit tests)'], num=1, numfill=GOLD, headsize=13, bodysize=11.5)
banner(s32, 5.68, [('Local learning reproduces — and on MNIST and ETH-80 exceeds — the SDNN baseline, ', {}), ('multiplier-free', {'bold': True, 'color': GOLD})])

# 33 — Conclusion divider
D5 = S(); DIVIDERS[5] = D5
divider(D5, 5, 'Conclusion', f'{KB}/sources/figures/thesis_ch1_en/fig1-2_research_journey.png')

# 34 — Conclusion
s34 = S(); chrome(s34, 5, 'Conclusion')
takes = [('Dependability is a device requirement', 'For safety-critical vision the loop must close on the device; fault tolerance has to move down the stack with the computation.', 'A'),
         ('Fault tolerance can live inside the neuron', 'H-ASIZH: proven bounded rate; 4.2 % vs 12.0 % dangerous faults, RFoM 4.76× vs 1.13×, at the same 1.47 pJ per update.', 'B'),
         ('The measurement itself must be trusted', 'GLFI → GateScan: four-valued, in-circuit, cross-checked; a certified bracket instead of an optimistic point estimate.', 'C'),
         ('From a neuron to a vision system', 'On-chip learning keeps 1020/1024 neurons alive; BioVision reproduces the SDNN baselines with local, multiplier-free learning.', 'D')]
for k, (h, b, n) in enumerate(takes):
    x = 1.42 + (k % 2) * 5.85; y = 1.42 + (k // 2) * 2.0
    card(s34, x, y, 5.65, 1.85, h, [b], num=n, numfill=TEAL, headsize=13.5, bodysize=11)
banner(s34, 5.68, [('Triplication buys nothing that ', {}), ('accommodation', {'bold': True, 'color': GOLD}), (' does not buy more cheaply', {})])

# 36 — Research articles
s36 = S(); chrome(s36, 5, 'Research Articles and Artefacts')
arts = [('H-ASIZH: A Highly Reliable Digital Izhikevich Neuron Core Using Adaptive Threshold Control for Fault Accommodation', 'A. Roshani, M. Ansari, M. T. Manzuri Shalmani', 'IEEE TCAS-I · submitted'),
        ('GateScan: certified gate-level vulnerability analysis (working title “Masked Is Not Harmless…”)', 'GateScan Mark III.1', 'IEEE TCAD · in preparation'),
        ('BioVision-SNN: a hardware-aware bio-inspired spiking vision system with local learning', 'Phase reports 0–1', 'in preparation')]
for k, (t, a, st) in enumerate(arts):
    y = 1.42 + k * 1.1
    rrect(s36, 1.42, y, 11.5, 0.98)
    o = oval(s36, 1.6, y + 0.27, 0.44, TEAL); write(o, [(str(k + 1), {'size': 12, 'bold': True, 'color': 'FFFFFF'})], align='c', anchor='m')
    tb(s36, 2.2, y + 0.06, 8.2, 0.55, [(t, {'size': 12.5, 'bold': True})])
    tb(s36, 2.2, y + 0.6, 8.2, 0.32, [(a, {'size': 10, 'italic': True, 'color': MUTED})])
    p = rrect(s36, 10.6, y + 0.3, 2.15, 0.36, GOLD if 'submitted' in st else LIGHT, None, 0.5)
    write(p, [(st, {'size': 9.5, 'bold': True, 'color': 'FFFFFF' if 'submitted' in st else TEAL})], align='c', anchor='m')
card(s36, 1.42, 4.8, 11.5, 0.8, None, [[('Open source: ', {'bold': True}), 'github.com/aliroshanidino/GLFI_fault_campaign  ·  github.com/gatescan-dev/gatescanMarkIII (MIT)']], bodysize=11)

# 38 — References (II)
s38 = S(); chrome(s38, 5, 'References (II)')
half = (len(NEW_REFS) + 1) // 2
for col, chunk in enumerate([NEW_REFS[:half], NEW_REFS[half:]]):
    paras = [[(f'[{R[k]}] ', {'bold': True}), t] for k, t in chunk]
    tb(s38, 1.42 + col * 5.85, 1.32, 5.65, 5.4, paras, size=6.1, color='3B4A52', space_after=0.6)

# ---------------------------------------------------------------- order, delete, renumber
order = [TITLE, OUTLINE, D1, s4, s5, s6, s7, s8, s9,
         D2, s11, s12, s13, s14, s15, s16,
         D3, s18, CTRL, LYAP, UARCH, HARD, s24, s25, s26,
         D4, PPA, OUTC, RFOM, LEARN, s32,
         D5, s34, FUTURE, s36, REF1, s38, THANKS]
kept_parts = {s.part for s in order}
for s in order:
    for sh in s.shapes:
        try: t = sh.click_action.target_slide
        except Exception: continue
        if t is not None and t.part not in kept_parts:
            sh.click_action.target_slide = D5
sldIdLst = prs.slides._sldIdLst
ids = {s.slide_id: el for s, el in zip(prs.slides, list(sldIdLst))}
order_ids = [s.slide_id for s in order]
keep = set(order_ids)
for s in list(prs.slides):
    sid = s.slide_id
    if sid not in keep:
        el = ids[sid]; rId = el.get(qn('r:id'))
        sldIdLst.remove(el); prs.part.drop_rel(rId)
for el in list(sldIdLst): sldIdLst.remove(el)
for sid in order_ids: sldIdLst.append(ids[sid])
N = len(order)
for i, s in enumerate(order, 1):
    for sh in s.shapes:
        if not sh.has_text_frame or sh.top < Inches(6.9): continue
        t = sh.text_frame.text.strip()
        if re.fullmatch(r'\d+ / \d+', t):
            set_runs(sh, [f'{i} / {N}'])
        elif t == '‹':
            sh.click_action.target_slide = order[i - 2] if i > 1 else None
        elif t == '›':
            sh.click_action.target_slide = order[i] if i < N else None
# re-point nav links of reused slides: the paper deck had no conclusion divider
for s in order:
    for sh in s.shapes:
        if sh.has_text_frame and sh.text_frame.text.replace('\n', '/').strip() in ('05/Conclusion', '05  Conclusion'):
            link(sh, D5)
prs.save(OUT)
print('saved', OUT, N, 'slides')
