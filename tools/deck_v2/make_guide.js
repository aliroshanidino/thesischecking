// Persian (RTL) slide-by-slide guide for the thesis deck, with a thumbnail of every slide.
const fs = require('fs');
const path = require('path');
const { Document, Packer, Paragraph, TextRun, ImageRun, HeadingLevel, AlignmentType, PageBreak,
        Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle, Footer, PageNumber, TableOfContents } = require('docx');
const DIR = '/tmp/claude-0/-home-user/2f31366c-8266-5d82-b134-0e1ce71114f5/scratchpad/deck';
const N = JSON.parse(fs.readFileSync(path.join(DIR, 'notes_fa.json'), 'utf8'));
const FONT = 'Tahoma';
const r = (text, o = {}) => new TextRun({ text, rightToLeft: true, font: FONT, size: o.size || 22, sizeComplexScript: o.size || 22,
                                         bold: !!o.bold, boldComplexScript: !!o.bold, color: o.color || '0F2338' });
const P = (runs, o = {}) => new Paragraph({ bidirectional: true, alignment: AlignmentType.RIGHT, spacing: { after: o.after ?? 120, line: 300 },
                                            heading: o.heading, children: Array.isArray(runs) ? runs : [runs] });
const label = (lab, txt, col) => P([r(lab + ': ', { bold: true, color: col || '00629B' }), r(txt)]);
function thumb(i) {
  const f = path.join(DIR, `all-${String(i).padStart(2, '0')}.png`);
  return new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 160 },
    children: [new ImageRun({ type: 'png', data: fs.readFileSync(f), transformation: { width: 560, height: 315 },
      altText: { title: `Slide ${i}`, description: `Slide ${i}`, name: `slide${i}` } })] });
}
const kids = [];
// cover
kids.push(P([r('راهنمای کامل اسلایدهای ارائهٔ پایان‌نامه', { size: 40, bold: true })], { after: 200 }));
kids.push(P([r('دستگاه لبهٔ دور قابل‌اتکا برای پردازش تصویر با شبکه‌های عصبی اسپایکی و هستهٔ نورونی مقاوم به خطا', { size: 26, color: '00629B' })], { after: 200 }));
kids.push(P([r('علی روشنی · استادان راهنما: دکتر محسن انصاری و دکتر محمدتقی منظوری شلمانی · CPS Lab، دانشکدهٔ مهندسی کامپیوتر، دانشگاه صنعتی شریف · آبان ۱۴۰۵', { size: 22, color: '6B7A90' })], { after: 300 }));
kids.push(P([r('این سند برای هر اسلاید این بخش‌ها را دارد:', { bold: true })]));
['هدف اسلاید', 'آنچه روی اسلاید است (متن، شکل و ترتیب)', 'شکل‌ها و منبعشان', 'متن پیشنهادی برای ارائه (همین متن در بخش Notes پاورپوینت هم هست)', 'اعداد و منبع دقیق هر عدد', 'پرسش احتمالی داوران و پاسخ پیشنهادی']
  .forEach((t, j) => kids.push(P([r(`${'۱۲۳۴۵۶'[j]}. ` + t)], { after: 60 })));
kids.push(P([r('قواعد کلی دک: ', { bold: true }), r('قانون ۵×۵×۵ (حداکثر ۵ جمله در هر اسلاید، یا ۵ مورد با یک زیرجمله)؛ هیچ عدد ساختگی ندارد و هر عدد منبع دارد؛ نتایج فقط در بخش Results آمده‌اند؛ همهٔ شکل‌ها با اسکریپت ساخته شده‌اند و دوباره‌سازی می‌شوند (tools/deck_v2 در مخزن).')], { after: 120 }));
kids.push(P([r('ساختار: ', { bold: true }), r('۳۷ اسلاید در پنج بخش. ۰۱ مقدمه (اسلاید ۳ تا ۹)، ۰۲ مرور ادبیات (۱۰ و ۱۱)، ۰۳ روش (۱۲ تا ۲۴: فاز ۱ از ۱۴ تا ۱۸، فاز ۲ از ۱۹ تا ۲۲، فاز ۳ از ۲۳ و ۲۴)، ۰۴ نتایج (۲۵ تا ۳۱)، ۰۵ جمع‌بندی (۳۲ تا ۳۷). در حالت نمایش، نوار ناوبری چپ، کارت‌های Outline و دکمه‌های قبلی و بعدی لینک دارند.')]));
kids.push(P([r('زمان پیشنهادی: ', { bold: true }), r('حدود ۴۰ دقیقه. مقدمه ۸ دقیقه، مرور ادبیات ۳، روش ۱۴، نتایج ۱۰ و جمع‌بندی ۵.')]));
kids.push(new Paragraph({ children: [new PageBreak()] }));
N.forEach((n, k) => {
  const i = k + 1;
  kids.push(P([r(`اسلاید ${i} — `, { size: 30, bold: true, color: '00629B' }), new TextRun({ text: n.t, font: 'Calibri', size: 30, bold: true, color: '0F2338' })], { heading: HeadingLevel.HEADING_1, after: 120 }));
  kids.push(thumb(i));
  kids.push(label('هدف اسلاید', n.goal, '0E7C86'));
  kids.push(label('روی اسلاید', n.on));
  kids.push(label('شکل‌ها و منبع', n.fig, '6B4FA0'));
  kids.push(label('متن پیشنهادی ارائه', n.say, '9A6A12'));
  if (n.num !== '—') kids.push(label('اعداد و منبع', n.num, 'B91C1C'));
  if (n.q !== '—') kids.push(label('پرسش احتمالی و پاسخ', n.q, '3D5A78'));
  if (i < N.length) kids.push(new Paragraph({ children: [new PageBreak()] }));
});
const doc = new Document({
  creator: 'Ali Roshani', title: 'Thesis deck — slide guide (FA)',
  styles: { default: { document: { run: { font: FONT, size: 22 } } } },
  sections: [{ properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } },
               footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 18, color: '6B7A90' })] })] }) },
               children: kids }] });
Packer.toBuffer(doc).then(b => { fs.writeFileSync(path.join(DIR, 'thesis_deck_guide_FA.docx'), b); console.log('docx ok', b.length); });
