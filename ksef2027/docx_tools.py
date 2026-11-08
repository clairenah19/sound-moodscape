"""Shared helpers for filling the official KSEF paper template (붙임3 논문양식.docx) with python-docx.

The template is the competition's own file; this module only fills it. Fonts: the template names HWP
fonts (한양신명조, 돋움, 바탕) that macOS does not have, so 명조 text uses AppleMyungjo and 돋움 text uses
Apple SD Gothic Neo, which keeps the template's 명조/돋움 distinction when the PDF is exported on a Mac.
"""
import subprocess
from pathlib import Path

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

MYEONGJO = ('Times New Roman', 'AppleMyungjo')
DOTUM = ('Apple SD Gothic Neo', 'Apple SD Gothic Neo')
LINK_BLUE = RGBColor(0x1F, 0x4E, 0x9A)


def set_font(run, font=MYEONGJO, size=None, bold=None, italic=None, sup=False, color=None):
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn('w:rFonts'))
    if rfonts is None:
        rfonts = OxmlElement('w:rFonts')
        rpr.insert(0, rfonts)
    for k in ('w:ascii', 'w:hAnsi', 'w:cs'):
        rfonts.set(qn(k), font[0])
    rfonts.set(qn('w:eastAsia'), font[1])
    for k in ('w:asciiTheme', 'w:hAnsiTheme', 'w:eastAsiaTheme', 'w:cstheme'):
        if rfonts.get(qn(k)) is not None:
            del rfonts.attrib[qn(k)]
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.font.bold = bold
    if italic is not None:
        run.font.italic = italic
    run.font.superscript = bool(sup) or None
    if color is not None:
        run.font.color.rgb = color
    return run


def clear(paragraph):
    for child in list(paragraph._element):
        if child.tag != qn('w:pPr'):
            paragraph._element.remove(child)


def remove(paragraph):
    paragraph._element.getparent().remove(paragraph._element)


def add_runs(paragraph, parts, font=MYEONGJO, size=11):
    """parts: list of str or (text, dict(bold/italic/sup/link/font)) tuples."""
    for part in parts:
        if isinstance(part, str):
            set_font(paragraph.add_run(part), font, size)
            continue
        text, opt = part
        if opt.get('link'):
            add_hyperlink(paragraph, opt['link'], text, opt.get('font', font), opt.get('size', size))
        else:
            set_font(paragraph.add_run(text), opt.get('font', font), opt.get('size', size), opt.get('bold'),
                     opt.get('italic'), opt.get('sup', False))


def add_hyperlink(paragraph, url, text, font=MYEONGJO, size=11):
    r_id = paragraph.part.relate_to(url, RT.HYPERLINK, is_external=True)
    link = OxmlElement('w:hyperlink')
    link.set(qn('r:id'), r_id)
    run = OxmlElement('w:r')
    link.append(run)
    paragraph._element.append(link)
    from docx.text.run import Run
    r = Run(run, paragraph)
    r.text = text
    set_font(r, font, size, color=LINK_BLUE)
    r.font.underline = True
    return r


def fmt(paragraph, align='justify', before=0, after=4, line=1.2, first_indent=None, keep_next=False):
    pf = paragraph.paragraph_format
    paragraph.alignment = {'justify': WD_ALIGN_PARAGRAPH.JUSTIFY, 'center': WD_ALIGN_PARAGRAPH.CENTER,
                           'left': WD_ALIGN_PARAGRAPH.LEFT}[align]
    pf.space_before, pf.space_after, pf.line_spacing = Pt(before), Pt(after), line
    if first_indent is not None:
        pf.first_line_indent = Pt(first_indent)
    pf.keep_with_next = keep_next
    return paragraph


def _border(tag, val='single', sz=6):
    el = OxmlElement(f'w:{tag}')
    el.set(qn('w:val'), val)
    el.set(qn('w:sz'), str(sz))
    el.set(qn('w:space'), '0')
    el.set(qn('w:color'), '000000')
    return el


def academic_table(doc, header, rows, widths_cm, font=MYEONGJO, size=8.5, align=None):
    """Three-rule table: thick top and bottom rules, thin rule under the header, no vertical lines."""
    t = doc.add_table(rows=1 + len(rows), cols=len(header))
    t.autofit = False
    tblpr = t._tbl.tblPr
    borders = OxmlElement('w:tblBorders')
    for tag in ('top', 'bottom'):
        borders.append(_border(tag, sz=10))
    for tag in ('left', 'right', 'insideV', 'insideH'):
        borders.append(_border(tag, 'nil'))
    tblpr.append(borders)
    jc = OxmlElement('w:jc'); jc.set(qn('w:val'), 'center'); tblpr.append(jc)
    # Pages ignores per-cell widths unless the grid, total width and a fixed layout are all set.
    layout = OxmlElement('w:tblLayout'); layout.set(qn('w:type'), 'fixed'); tblpr.append(layout)
    tblw = tblpr.find(qn('w:tblW'))
    if tblw is None:
        tblw = OxmlElement('w:tblW'); tblpr.append(tblw)
    tblw.set(qn('w:type'), 'dxa'); tblw.set(qn('w:w'), str(int(sum(widths_cm) * 567)))
    for i, col in enumerate(t.columns):
        col.width = Cm(widths_cm[i])
    align = align or ['left'] + ['center'] * (len(header) - 1)
    for ri, row in enumerate([header] + rows):
        for ci, val in enumerate(row):
            cell = t.rows[ri].cells[ci]
            cell.width = Cm(widths_cm[ci])
            p = cell.paragraphs[0]
            clear(p)
            add_runs(p, val if isinstance(val, list) else [(str(val), {'bold': ri == 0})], font, size)
            fmt(p, align[ci] if ri else 'center', 1, 1, 1.0)
            if ri == 0:
                tcpr = cell._tc.get_or_add_tcPr()
                b = OxmlElement('w:tcBorders'); b.append(_border('bottom', sz=6)); tcpr.append(b)
    return t


def export_pdf_with_pages(docx_path, pdf_path):
    """Export through Apple Pages so the PDF matches the .docx layout (the competition wants a PDF)."""
    docx_path, pdf_path = Path(docx_path).resolve(), Path(pdf_path).resolve()
    script = f'''with timeout of 180 seconds
tell application "Pages"
set d to open (POSIX file "{docx_path}")
delay 3
export d to (POSIX file "{pdf_path}") as PDF
close d saving no
end tell
end timeout'''
    subprocess.run(['osascript', '-e', script], check=True)
