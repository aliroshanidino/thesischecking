"""Persian (right-to-left) Word report from a light text source, with native Word equations.

    python tools/docx_report.py <source.txt> <out.docx>

Source format (one block per paragraph, blank lines between blocks):

* ``# ``, ``## ``, ``### `` headings; ``- `` bullet items; ``1. `` numbered items; ``> `` a shaded note;
* ``$$ <LaTeX> $$`` on its own line: a numbered display equation (native Word/OMML math);
* inline ``$<LaTeX>$`` math, ``**bold**`` and ```code``` (Latin font, left-to-right) inside any paragraph;
* Markdown tables (``| a | b |`` lines, the second line ``|---|``) followed by an optional ``Table: caption`` line;
* ``![caption](path/to/image.png)`` a centred figure with its caption;
* ``[[TOC]]`` a table of contents field, ``[[PAGEBREAK]]`` a page break, ``[[TITLE]] title | subtitle | line``.

Persian runs are right-to-left with the B Nazanin complex-script font; Latin runs (terms, code, numbers inside
Latin words) keep Times New Roman and their own direction; Western digits in Persian runs become Persian digits.
LaTeX goes LaTeX -> MathML (latex2mathml) -> OMML with Office's own ``MML2OMML.XSL``.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import latex2mathml.converter
from docx import Document
from docx.enum.section import WD_ORIENT  # noqa: F401
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from lxml import etree

XSL_PATHS = [r"C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL",
             r"C:\Program Files (x86)\Microsoft Office\root\Office16\MML2OMML.XSL"]
FA_FONT, TITLE_FONT, LATIN_FONT = "B Nazanin", "B Titr", "Times New Roman"
FA_DIGITS = str.maketrans("0123456789%", "۰۱۲۳۴۵۶۷۸۹٪")
BLUE = RGBColor(0x1F, 0x3A, 0x68)
_xslt = None


def omml(latex: str, display: bool = False):
    global _xslt
    if _xslt is None:
        _xslt = etree.XSLT(etree.parse(next(p for p in XSL_PATHS if Path(p).exists())))
    mml = etree.fromstring(latex2mathml.converter.convert(latex, display="block" if display else "inline"))
    tidy_mathml(mml)
    root = _xslt(mml).getroot()
    m = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
    for nary in root.iter(m + "nary"):  # an n-ary operator (sum) whose argument follows it: move it inside
        e = nary.find(m + "e")
        if e is not None and len(e) == 0:
            for sib in list(nary.itersiblings()):
                e.append(sib)
    return root


MML = "{http://www.w3.org/1998/Math/MathML}"
FUNCS = {"max", "min", "argmin", "argmax", "exp", "cos", "sin", "log", "ln", "sup", "inf", "lim"}


def tidy_mathml(mml) -> None:
    """Upright function names (max, min, cos ...) and visible spaces: MML2OMML drops ``mspace`` and sets
    ``mo`` words in italics."""
    for el in list(mml.iter(MML + "mo", MML + "mi")):
        if (el.text or "").strip() in FUNCS:
            name = el.text.strip()
            el.tag = MML + "mi"
            el.set("mathvariant", "normal")
            for k in ("stretchy", "fence", "form", "movablelimits"):
                el.attrib.pop(k, None)
            parent = el.getparent()
            if name in {"cos", "sin", "exp", "log", "ln"} and el.getnext() is not None and parent is not None \
                    and etree.QName(parent).localname in {"mrow", "math", "mtd", "mstyle"}:
                sp = etree.Element(MML + "mtext")
                sp.text = "\u2009"
                el.addnext(sp)
    for el in list(mml.iter(MML + "mspace")):
        w = el.get("width", "0.278em")
        n = 2 if w.startswith("1em") or w.startswith("2em") else 1
        txt = etree.Element(MML + "mtext")
        txt.text = "\u00a0" * n if n > 1 or not w.startswith("0.1") else "\u2009"
        txt.tail = el.tail
        el.getparent().replace(el, txt)


def fa_digits(text: str) -> str:
    text = re.sub(r"(?<=\d)\.(?=\d)", "٫", text)
    text = text.replace("هٔ", "ه‌ی")  # "هٔ" -> "ه‌ی" (B Nazanin has no U+0654 mark)
    return text.translate(FA_DIGITS)


def set_rtl_paragraph(p, align: str = "both") -> None:
    ppr = p._p.get_or_add_pPr()
    if ppr.find(qn("w:bidi")) is None:
        ppr.insert(0, OxmlElement("w:bidi"))
    p.alignment = {"both": WD_ALIGN_PARAGRAPH.JUSTIFY, "center": WD_ALIGN_PARAGRAPH.CENTER,
                   "start": WD_ALIGN_PARAGRAPH.LEFT}[align]  # LEFT in a bidi paragraph = start (right side)


def style_run(run, latin: bool, size: float | None = None, bold: bool = False, font: str | None = None,
              color: RGBColor | None = None) -> None:
    rpr = run._r.get_or_add_rPr()
    fonts = rpr.find(qn("w:rFonts"))
    if fonts is None:
        fonts = OxmlElement("w:rFonts")
        rpr.insert(0, fonts)
    for k in ("w:ascii", "w:hAnsi"):
        fonts.set(qn(k), LATIN_FONT)
    fonts.set(qn("w:cs"), font or FA_FONT)
    if not latin:
        rpr.append(OxmlElement("w:rtl"))
        lang = OxmlElement("w:lang")
        lang.set(qn("w:bidi"), "fa-IR")
        rpr.append(lang)
    if size:
        run.font.size = Pt(size)
        szcs = OxmlElement("w:szCs")
        szcs.set(qn("w:val"), str(int(size * 2)))
        rpr.append(szcs)
    if bold:
        run.bold = True
        rpr.append(OxmlElement("w:bCs"))
    if color is not None:
        run.font.color.rgb = color


LATIN = re.compile(r"[A-Za-z][A-Za-z0-9_]*(?:[\-+/.:'’=×·][A-Za-z0-9_]+)*(?:,? [A-Za-z0-9][A-Za-z0-9_]*(?:[\-+/.:'’=×·][A-Za-z0-9_]+)*)*")
TOKEN = re.compile(r"(\$[^$]+\$|\*\*[^*]+\*\*|`[^`]+`)")


def add_text(p, text: str, size: float | None = None, bold: bool = False, font: str | None = None,
             color: RGBColor | None = None) -> None:
    """Inline markup -> runs: math, bold, code, then Persian / Latin segments."""
    for tok in TOKEN.split(text):
        if not tok:
            continue
        if tok.startswith("$") and tok.endswith("$"):
            p._p.append(omml(tok[1:-1]))
        elif tok.startswith("**"):
            add_text(p, tok[2:-2], size, True, font, color)
        elif tok.startswith("`"):
            r = p.add_run(tok[1:-1])
            style_run(r, True, (size or 12) - 1, bold, font, color)
            r.font.name = "Consolas"
        else:
            pos = 0
            for m in LATIN.finditer(tok):
                if m.start() > pos:
                    r = p.add_run(fa_digits(tok[pos:m.start()]))
                    style_run(r, False, size, bold, font, color)
                r = p.add_run(m.group(0).replace("-", "\u2011"))  # non-breaking hyphen: H-ASIZH stays whole
                style_run(r, True, size, bold, font, color)
                pos = m.end()
            if pos < len(tok):
                r = p.add_run(fa_digits(tok[pos:]))
                style_run(r, False, size, bold, font, color)


def shade(el, fill: str) -> None:
    pr = el.get_or_add_tcPr() if hasattr(el, "get_or_add_tcPr") else el.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    pr.append(shd)


class Report:
    def __init__(self):
        self.doc = Document()
        self.eq = 0
        self.fig = 0
        self.tab = 0
        sec = self.doc.sections[0]
        sec.page_width, sec.page_height = Cm(21), Cm(29.7)
        sec.left_margin = sec.right_margin = Cm(2.3)
        sec.top_margin, sec.bottom_margin = Cm(2.2), Cm(2.2)
        st = self.doc.styles["Normal"]
        st.font.name = LATIN_FONT
        st.font.size = Pt(12)
        st.element.rPr.rFonts.set(qn("w:cs"), FA_FONT)
        szcs = OxmlElement("w:szCs")
        szcs.set(qn("w:val"), "26")
        st.element.rPr.append(szcs)
        pf = st.paragraph_format
        pf.space_after = Pt(4)
        pf.line_spacing = 1.2
        sectpr = sec._sectPr
        sectpr.append(OxmlElement("w:bidi"))
        self._footer()
        settings = self.doc.settings.element
        upd = OxmlElement("w:updateFields")
        upd.set(qn("w:val"), "true")
        settings.append(upd)

    def _footer(self) -> None:
        p = self.doc.sections[0].footer.paragraphs[0]
        set_rtl_paragraph(p, "center")
        r = p.add_run()
        for kind, text in (("begin", None), (None, "PAGE"), ("end", None)):
            if kind:
                fc = OxmlElement("w:fldChar")
                fc.set(qn("w:fldCharType"), kind)
                r._r.append(fc)
            else:
                it = OxmlElement("w:instrText")
                it.set(qn("xml:space"), "preserve")
                it.text = text
                r._r.append(it)
        style_run(r, False, 11)

    # ---- blocks -------------------------------------------------------------------------------------------
    def heading(self, text: str, level: int) -> None:
        p = self.doc.add_heading("", level=level)
        set_rtl_paragraph(p, "start")
        p.paragraph_format.space_before = Pt(14 if level == 1 else 10)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        add_text(p, text, {1: 17, 2: 14.5, 3: 13}[level], False, TITLE_FONT, BLUE)

    def paragraph(self, text: str, size: float = 12) -> None:
        p = self.doc.add_paragraph()
        set_rtl_paragraph(p)
        add_text(p, text, size)

    def note(self, text: str) -> None:
        p = self.doc.add_paragraph()
        set_rtl_paragraph(p)
        shade(p._p, "EAF1FB")
        p.paragraph_format.left_indent = p.paragraph_format.right_indent = Cm(0.4)
        add_text(p, text, 11.5)

    def bullet(self, text: str, numbered: bool = False, restart: bool = False) -> None:
        p = self.doc.add_paragraph(style="List Number" if numbered else "List Bullet")
        if numbered:  # every numbered list starts at 1: its own w:num on the style's abstract numbering
            numbering = self.doc.part.numbering_part.numbering_definitions._numbering
            if restart or getattr(self, "_num_id", None) is None:
                base = self.doc.styles["List Number"].element.pPr.numPr.numId.val
                num = numbering.add_num(numbering.num_having_numId(base).abstractNumId.val)
                num.add_lvlOverride(ilvl=0).add_startOverride(1)
                self._num_id = num.numId
            numpr = p._p.get_or_add_pPr().get_or_add_numPr()
            numpr.get_or_add_ilvl().val = 0
            numpr.get_or_add_numId().val = self._num_id
        set_rtl_paragraph(p)
        add_text(p, text)

    def equation(self, latex: str) -> None:
        """Numbered display equation: a borderless two-cell row (equation | number), right-to-left."""
        self.eq += 1
        t = self.doc.add_table(rows=1, cols=2)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        tblpr = t._tbl.tblPr
        tblpr.append(OxmlElement("w:bidiVisual"))
        widths = (Cm(1.6), Cm(14.8))
        num, eq = t.rows[0].cells[1], t.rows[0].cells[0]  # bidiVisual: first cell is on the right
        for c, w in zip((num, eq), widths):
            c.width = w
        eq.width, num.width = Cm(14.8), Cm(1.6)
        pe = eq.paragraphs[0]
        pe.alignment = WD_ALIGN_PARAGRAPH.CENTER
        para = etree.SubElement(pe._p, qn("m:oMathPara"))
        para.append(omml(latex, display=True))
        pn = num.paragraphs[0]
        set_rtl_paragraph(pn, "center")
        add_text(pn, f"({self.eq})", 12)
        # first cell (right) holds the equation, second (left) the number
        row = t.rows[0]._tr
        row.remove(num._tc)
        row.append(num._tc)

    def table(self, rows: list[list[str]], caption: str | None) -> None:
        self.tab += 1
        if caption:
            p = self.doc.add_paragraph()
            set_rtl_paragraph(p, "center")
            p.paragraph_format.keep_with_next = True
            add_text(p, f"جدول {self.tab}: {caption}", 11, True)
        t = self.doc.add_table(rows=len(rows), cols=len(rows[0]))
        t.style = "Table Grid"
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t._tbl.tblPr.append(OxmlElement("w:bidiVisual"))
        for i, row in enumerate(rows):
            for j, cell in enumerate(row):
                c = t.rows[i].cells[j]
                p = c.paragraphs[0]
                set_rtl_paragraph(p, "center")
                p.paragraph_format.space_after = Pt(1)
                add_text(p, cell.strip(), 10.5 if len(row) <= 4 else 9.5, i == 0)
                if i == 0:
                    shade(c._tc, "D9E2F3")
        self.doc.add_paragraph().paragraph_format.space_after = Pt(2)

    def figure(self, path: str, caption: str, width_cm: float = 15.5) -> None:
        self.fig += 1
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.keep_with_next = True
        p.add_run().add_picture(path, width=Cm(width_cm))
        c = self.doc.add_paragraph()
        set_rtl_paragraph(c, "center")
        add_text(c, f"شکل {self.fig}: {caption}", 11, True)

    def toc(self) -> None:
        p = self.doc.add_paragraph()
        set_rtl_paragraph(p, "start")
        r = p.add_run()
        for kind, text in (("begin", None), (None, 'TOC \\o "1-2" \\h \\z \\u'), ("separate", None),
                           ("end", None)):
            if kind:
                fc = OxmlElement("w:fldChar")
                fc.set(qn("w:fldCharType"), kind)
                r._r.append(fc)
                if kind == "separate":
                    t = OxmlElement("w:t")
                    t.text = "برای ساختن فهرست، کلید F9 را روی این بخش بزنید."
                    r._r.append(t)
            else:
                it = OxmlElement("w:instrText")
                it.set(qn("xml:space"), "preserve")
                it.text = text
                r._r.append(it)
        style_run(r, False, 12)

    def title(self, title: str, subtitle: str, line: str) -> None:
        for _ in range(6):
            self.doc.add_paragraph()
        for text, size, font, col in ((title, 26, TITLE_FONT, BLUE), (subtitle, 16, TITLE_FONT, BLUE),
                                      (line, 13, FA_FONT, None)):
            p = self.doc.add_paragraph()
            set_rtl_paragraph(p, "center")
            p.paragraph_format.space_after = Pt(18)
            add_text(p, text, size, font == FA_FONT and False, font, col)

    def page_break(self) -> None:
        self.doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    # ---- source -------------------------------------------------------------------------------------------
    def build(self, source: str, base: Path) -> None:
        blocks = re.split(r"\n\s*\n", source.strip())
        for block in blocks:
            lines = [ln.rstrip() for ln in block.strip().splitlines()]
            first = lines[0]
            k = next((n for n, ln in enumerate(lines) if n and re.match(r"^(- |\d+\. )", ln)), None)
            if k and not re.match(r"^(- |\d+\. |\|)", first):  # paragraph, then a list
                self.build("\n".join(lines[:k]) + "\n\n" + "\n".join(lines[k:]), base)
                continue
            if first.startswith("<!--"):
                continue
            if first == "[[TOC]]":
                self.toc()
            elif first == "[[PAGEBREAK]]":
                self.page_break()
            elif first.startswith("[[TITLE]]"):
                self.title(*[s.strip() for s in first[len("[[TITLE]]"):].split("|")])
            elif first.startswith("#"):
                level = len(first) - len(first.lstrip("#"))
                self.heading(first.lstrip("#").strip(), level)
                if len(lines) > 1:
                    self.build("\n".join(lines[1:]), base)
            elif first.startswith("$$"):
                self.equation(" ".join(lines).strip().strip("$").strip())
            elif first.startswith("|"):
                rows = [ln for ln in lines if ln.startswith("|")]
                cap = next((ln[len("Table:"):].strip() for ln in lines if ln.startswith("Table:")), None)
                cells = [[c for c in r.strip().strip("|").split("|")] for r in rows if not re.match(r"^\|[\s:|-]+\|$", r)]
                self.table(cells, cap)
            elif first.startswith("!["):
                m = re.match(r"!\[(.*)\]\((.*?)\)(?:\{width=([\d.]+)\})?", first)
                self.figure(str((base / m.group(2)).resolve()), m.group(1), float(m.group(3) or 15.5))
            elif first.startswith(("- ", "1. ")) or re.match(r"^\d+\. ", first):
                for ln in lines:
                    if ln.startswith("- "):
                        self.bullet(ln[2:])
                    elif re.match(r"^\d+\. ", ln):
                        self.bullet(re.sub(r"^\d+\. ", "", ln), numbered=True, restart=ln.startswith("1. "))
                    else:  # continuation of the previous item
                        self.paragraph(ln)
            elif first.startswith("> "):
                self.note(" ".join(ln[2:] if ln.startswith("> ") else ln for ln in lines))
            else:
                self.paragraph(" ".join(lines))


def main() -> None:
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    rep = Report()
    rep.build(src.read_text(encoding="utf-8"), src.parent)
    rep.doc.save(out)
    print(f"wrote {out} ({rep.eq} equations, {rep.tab} tables, {rep.fig} figures)")


if __name__ == "__main__":
    main()
