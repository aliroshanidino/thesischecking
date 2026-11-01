"""Helpers for the v2 thesis deck: slide cloning across presentations + rendering."""
import copy, subprocess, os
from pptx import Presentation
from pptx.oxml.ns import qn

RT_SLIDE = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide'

def clone_slide(src_slide, dst_prs, layout_idx=6):
    """Copy a slide (background, shapes, images, external links) into another presentation."""
    new = dst_prs.slides.add_slide(dst_prs.slide_layouts[layout_idx])
    tree = new.shapes._spTree
    for el in list(tree):
        if el.tag not in (qn('p:nvGrpSpPr'), qn('p:grpSpPr')): tree.remove(el)
    src_csld = src_slide._element.find(qn('p:cSld'))
    bg = src_csld.find(qn('p:bg'))
    if bg is not None:
        new._element.find(qn('p:cSld')).insert(0, copy.deepcopy(bg))
    rid_map = {}
    for rId, rel in src_slide.part.rels.items():
        if rel.reltype == RT_SLIDE or rel.reltype.endswith('/notesSlide') or rel.reltype.endswith('/slideLayout'):
            continue
        if rel.is_external:
            rid_map[rId] = new.part.relate_to(rel.target_ref, rel.reltype, is_external=True)
        else:
            rid_map[rId] = new.part.relate_to(rel.target_part, rel.reltype)
    for el in src_slide.shapes._spTree:
        if el.tag in (qn('p:nvGrpSpPr'), qn('p:grpSpPr')): continue
        e = copy.deepcopy(el)
        for node in e.iter():
            for attr in (qn('r:embed'), qn('r:link'), qn('r:id')):
                v = node.get(attr)
                if v is not None:
                    if v in rid_map: node.set(attr, rid_map[v])
                    else:  # link to a slide that is not copied: drop the hyperlink element
                        if node.tag in (qn('a:hlinkClick'),): node.getparent().remove(node)
        tree.append(e)
    return new

def empty_deck(base):
    prs = Presentation(base)
    lst = prs.slides._sldIdLst
    for el in list(lst):
        prs.part.drop_rel(el.get(qn('r:id'))); lst.remove(el)
    return prs

def render(pptx, outdir, first=None, last=None, dpi=110, prefix='s'):
    subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', '--outdir', outdir, pptx], capture_output=True)
    pdf = os.path.join(outdir, os.path.splitext(os.path.basename(pptx))[0] + '.pdf')
    args = ['pdftoppm', '-png', '-r', str(dpi)]
    if first: args += ['-f', str(first)]
    if last: args += ['-l', str(last)]
    subprocess.run(args + [pdf, os.path.join(outdir, prefix)], capture_output=True)
    return pdf
