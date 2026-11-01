"""Design kit v2: paper-deck structure (nav bar, dividers, links, pager) + refined seminar palette."""
import io
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.oxml.ns import qn
from PIL import Image

# palette (seminar-derived, refined)
BG, INK, BLUE, NAV, NAVACT = 'F6F9FC', '0F2338', '00629B', '0F2338', '18406A'
AMBER, RED, TEAL = 'E3A63B', 'B91C1C', '0E7C86'
PANEL, LINE, MUTED, SOFT = 'EAF2F9', 'D5E1EC', '6B7A90', 'B1BCCC'
WHITE = 'FFFFFF'
HFONT, BFONT = 'Cambria', 'Calibri'
SECTIONS = ['Introduction', 'Literature', 'Methodology', 'Results', 'Conclusion']
SEC_FULL = ['INTRODUCTION', 'LITERATURE REVIEW', 'METHODOLOGY', 'RESULTS', 'CONCLUSION']
DECK_LABEL = 'M.Sc. Thesis'
LOGO = '/tmp/claude-0/-home-user/2f31366c-8266-5d82-b134-0e1ce71114f5/scratchpad/deck/sharif_logo.png'

def rgb(h): return RGBColor.from_string(h)

def shape(slide, kind, x, y, w, h, fill=None, line=None, adj=None, lw=0.75):
    s = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    st = s._element.find(qn('p:style'))
    if st is not None: s._element.remove(st)
    if fill: s.fill.solid(); s.fill.fore_color.rgb = rgb(fill)
    else: s.fill.background()
    if line: s.line.color.rgb = rgb(line); s.line.width = Pt(lw)
    else: s.line.fill.background()
    if adj is not None: s.adjustments[0] = adj
    tf = s.text_frame; tf.margin_left = tf.margin_right = Inches(0.06); tf.margin_top = tf.margin_bottom = Inches(0.03)
    return s

def rect(sl, x, y, w, h, fill, line=None): return shape(sl, MSO_SHAPE.RECTANGLE, x, y, w, h, fill, line)
def rrect(sl, x, y, w, h, fill=WHITE, line=LINE, adj=0.08, lw=0.75): return shape(sl, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill, line, adj, lw)
def oval(sl, x, y, d, fill, line=None):
    o = shape(sl, MSO_SHAPE.OVAL, x, y, d, d, fill, line)
    tf = o.text_frame; tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0; tf.word_wrap = False
    return o

def write(target, paras, size=12, color=INK, bold=False, align='l', anchor=None, italic=False, font=BFONT, space_after=None, line_spacing=None):
    tf = target.text_frame if hasattr(target, 'text_frame') else target
    tf.word_wrap = True
    if anchor: tf.vertical_anchor = {'t': MSO_ANCHOR.TOP, 'm': MSO_ANCHOR.MIDDLE, 'b': MSO_ANCHOR.BOTTOM}[anchor]
    if isinstance(paras, (str, tuple)): paras = [paras]
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        for r in list(p.runs): r._r.getparent().remove(r._r)
        p.alignment = {'l': PP_ALIGN.LEFT, 'c': PP_ALIGN.CENTER, 'r': PP_ALIGN.RIGHT}[align]
        if space_after is not None: p.space_after = Pt(space_after)
        if line_spacing: p.line_spacing = line_spacing
        for r in ([para] if isinstance(para, (str, tuple)) else para):
            text, o = (r, {}) if isinstance(r, str) else r
            run = p.add_run(); run.text = text; f = run.font
            f.name = o.get('font', font); f.size = Pt(o.get('size', size)); f.bold = o.get('bold', bold)
            f.italic = o.get('italic', italic); f.color.rgb = rgb(o.get('color', color))
    return tf

def tb(sl, x, y, w, h, paras, **kw):
    s = sl.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = s.text_frame; tf.margin_left = tf.margin_right = Inches(0.04); tf.margin_top = tf.margin_bottom = Inches(0.02)
    tf.auto_size = MSO_AUTO_SIZE.NONE
    write(s, paras, **kw); return s

def picture(sl, path, x, y, w, h, align='c', valign='m'):
    iw, ih = Image.open(path).size
    r = min(w / iw, h / ih); pw, ph = iw * r, ih * r
    px = x + (w - pw) / 2 if align == 'c' else x
    py = y + (h - ph) / 2 if valign == 'm' else y
    return sl.shapes.add_picture(path, Inches(px), Inches(py), Inches(pw), Inches(ph))

class Deck:
    """Holds link targets so navigation can be wired after all slides exist."""
    def __init__(self, prs):
        self.prs = prs; self.dividers = {}; self.nav = []   # (shape, section)
        self.blank = min(prs.slide_layouts, key=lambda l: len(l.placeholders))
    def new(self): return self.prs.slides.add_slide(self.blank)

    def chrome(self, sl, sec, title, label=None, footer=None):
        rect(sl, 0, 0, 13.333, 7.5, BG)
        rect(sl, 0, 0, 1.08, 7.5, NAV)
        sl.shapes.add_picture(LOGO, Inches(0.22), Inches(0.24), Inches(0.64), Inches(0.64))
        for k, name in enumerate(SECTIONS):
            y = 1.35 + 1.02 * k; act = (k + 1 == sec)
            r = rect(sl, 0, y, 1.08, 0.92, NAVACT if act else NAV)
            write(r, [[(f'0{k+1}', {'size': 17, 'bold': True, 'color': AMBER if act else '7FA7C9', 'font': HFONT})],
                      [(name, {'size': 8.5, 'color': WHITE if act else 'B9C9DA'})]], align='c', anchor='m')
            self.nav.append((r, k + 1))
            if act: rect(sl, 0, y, 0.07, 0.92, AMBER)
        rect(sl, 0.3, 6.78, 0.48, 0.02, '4A6283')
        tb(sl, 0.04, 6.82, 1.0, 0.3, [(DECK_LABEL, {'size': 8, 'color': '8FA6BE'})], align='c')
        hdr = label or (f'0{sec}  ·  {SEC_FULL[sec-1]}' if sec else 'ROADMAP')
        tb(sl, 1.42, 0.27, 9.0, 0.3, [(hdr, {'size': 10, 'bold': True, 'color': BLUE})])
        tb(sl, 1.42, 0.49, 11.5, 0.7, [(title, {'size': 27, 'bold': True, 'color': INK, 'font': HFONT})])
        rect(sl, 1.46, 1.18, 0.7, 0.045, BLUE); rect(sl, 2.2, 1.18, 0.16, 0.045, AMBER)
        if footer: tb(sl, 1.42, 6.74, 10.0, 0.3, [(footer, {'size': 7.5, 'color': MUTED})])
        self.pager(sl, dark=False)

    def pager(self, sl, dark=False):
        a = oval(sl, 11.6, 7.03, 0.3, '1E3A5F' if dark else 'E2ECF5'); write(a, [('‹', {'size': 11, 'bold': True, 'color': WHITE if dark else BLUE})], align='c', anchor='m')
        p = rrect(sl, 11.95, 7.03, 0.68, 0.3, BLUE, None, 0.5)
        p.text_frame.margin_left = p.text_frame.margin_right = 0; p.text_frame.word_wrap = False
        write(p, [('0 / 0', {'size': 9.5, 'bold': True, 'color': WHITE})], align='c', anchor='m'); p.text_frame.word_wrap = False
        b = oval(sl, 12.68, 7.03, 0.3, '1E3A5F' if dark else 'E2ECF5'); write(b, [('›', {'size': 11, 'bold': True, 'color': WHITE if dark else BLUE})], align='c', anchor='m')
        a.name, p.name, b.name = 'PAGER_PREV', 'PAGER_NUM', 'PAGER_NEXT'

    def finalize(self, order):
        n = len(order)
        for r, sec in self.nav:
            if sec in self.dividers: r.click_action.target_slide = self.dividers[sec]
        for i, sl in enumerate(order, 1):
            for s in sl.shapes:
                if s.name == 'PAGER_NUM': write(s, [(f'{i} / {n}', {'size': 9.5, 'bold': True, 'color': WHITE})], align='c', anchor='m'); s.text_frame.word_wrap = False
                elif s.name == 'PAGER_PREV' and i > 1: s.click_action.target_slide = order[i - 2]
                elif s.name == 'PAGER_NEXT' and i < n: s.click_action.target_slide = order[i]
        lst = self.prs.slides._sldIdLst
        ids = {s.slide_id: el for s, el in zip(self.prs.slides, list(lst))}
        want = [s.slide_id for s in order]
        for el in list(lst): lst.remove(el)
        for sid in want: lst.append(ids[sid])

def gradient(shape, c1, c2, angle=35):
    f = shape.fill; f.gradient(); f.gradient_angle = angle
    st = f.gradient_stops
    st[0].color.rgb = rgb(c1); st[0].position = 0.0
    st[1].color.rgb = rgb(c2); st[1].position = 1.0

def divider(D, sl, num, title, img):
    bg = rect(sl, 0, 0, 13.333, 7.5, NAV); gradient(bg, '0F2338', '0B4A75', 30)
    tb(sl, 0.9, 0.95, 4.2, 2.1, [(f'0{num}', {'size': 140, 'bold': True, 'color': AMBER, 'font': HFONT})])
    tb(sl, 0.95, 3.35, 6.25, 1.15, [(title, {'size': 52, 'bold': True, 'color': WHITE, 'font': HFONT})])
    rect(sl, 1.0, 4.75, 1.2, 0.05, AMBER); rect(sl, 2.26, 4.75, 0.2, 0.05, '7FA7C9')
    card = rrect(sl, 7.2, 0.85, 5.5, 5.3, WHITE, None, 0.05)
    picture(sl, img, 7.35, 1.0, 5.2, 5.0)
    for k, name in enumerate(['Introduction', 'Literature Review', 'Methodology', 'Results', 'Conclusion']):
        act = (k + 1 == num)
        p = rrect(sl, 0.95 + 2.35 * k, 6.4, 2.15, 0.42, '18406A' if act else '132E4C', None, 0.5)
        write(p, [(f'0{k+1}  {name}', {'size': 10, 'bold': True, 'color': AMBER if act else '9DB4CB'})], align='c', anchor='m')
        D.nav.append((p, k + 1))
    D.pager(sl, dark=True)
    D.dividers[num] = sl
