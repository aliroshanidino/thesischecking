# پایگاه دانش H-ASIZH / GLFI / GateScan — فهرست

> ساخته‌شده در 2026-11-01 از چهار فایلی که کاربر بارگذاری کرد، به‌اضافهٔ بررسی دو مخزن GitHub.
> **محل:** مخزن [`aliroshanidino/thesischecking`](https://github.com/aliroshanidino/thesischecking)، شاخهٔ `main`. پایگاه دانش «کنار» دو مخزن [`aliroshanidino/GLFI_fault_campaign`](https://github.com/aliroshanidino/GLFI_fault_campaign) و [`gatescan-dev/gatescanMarkIII`](https://github.com/gatescan-dev/gatescanMarkIII) نگه داشته می‌شود و به آن‌ها ارجاع می‌دهد.
> **مرجع حقیقت:** نتایج مقالهٔ TCAS-I. مخزن عمومی GLFI نسخهٔ قدیمی‌تری از کد است (به گفتهٔ نویسنده، 2026-11-01).
> **زبان:** یادداشت‌های ترکیبی به فارسی‌اند و اصطلاحات فنی به انگلیسی. متن کامل منابع به زبان اصلی در `sources/` است.
> **قرارداد:** هر عدد یا ادعا منبعش را دارد (P = مقاله، S = اسلاید، C1 = فصل ۱، R = کد مخزن). ⚠️ یعنی ناسازگاری؛ همهٔ آن‌ها در `09` جمع شده‌اند.

## ۱. منابع ورودی
| # | فایل اصلی (در `originals/`) | نوع | محتوا | متن استخراج‌شده |
|---|---|---|---|---|
| 1 | `H-ASIZH_TCAS-I_manuscript.pdf` (۱۴ صفحه) | مقالهٔ IEEE TCAS-I (submitted، 2026) | H-ASIZH: هستهٔ نورون ایژیکویچ دیجیتال با کنترل آستانهٔ تطبیقی؛ GLFI؛ PPA در SkyWater 130؛ یادگیری روی تراشه | `sources/paper_H-ASIZH_fulltext.txt` (ترتیب خواندن) و `…_layout.txt` (چیدمان دوستونی)؛ ۱۰ شکل در `sources/figures/paper/` |
| 2 | `seminar_H-ASIZH_Roshani.pptx` (۲۵ اسلاید) | سمینار کارشناسی ارشد، شریف | چالش، شکاف‌ها، اهداف، مرور ادبیات (۲ جدول)، سه مقالهٔ مرجع، روش، نتایج، کار آینده | `sources/slides_seminar_fulltext.txt` (با یادداشت‌های سخنران)؛ تصویر هر اسلاید در `sources/figures/slides/`؛ رندر PDF در `originals/` |
| 3 | `thesis_ch1_Introduction_LitReview_EN.docx` | فصل ۱ پایان‌نامه (انگلیسی) | از پیوستار ابر و لبه تا نورون؛ ۶ شکاف؛ زنجیرهٔ پرسش Q0 تا Q6؛ ۱۶۲ مرجع | `sources/thesis_ch1_EN.md` و ۲ شکل |
| 4 | `thesis_ch1_Introduction_LitReview_FA.docx` | ترجمهٔ فارسی هم‌ساختارِ همان فصل | همان محتوا و همان ۱۶۲ مرجع؛ یک عبارت هایلایت‌شدهٔ ویرایشی | `sources/thesis_ch1_FA.md` و ۲ شکل فارسی |

## ۲. یادداشت‌های دانش (به ترتیب خواندن)
| فایل | موضوع |
|---|---|
| [`01-research-overview.md`](01-research-overview.md) | هویت پژوهش (نویسندگان، آزمایشگاه)، ادعای مرکزی، سه فهرست شکاف کنار هم، دستاوردها، وضعیت و کار باز |
| [`02-thesis-ch1-literature.md`](02-thesis-ch1-literature.md) | فصل ۱ بخش‌به‌بخش: پیوستار، offloading، شش بهای offload، DNN → شتاب‌دهنده → SNN، قابلیت اتکا، جدول ۱.۲، ابزار FI، شکاف‌ها، Q0 تا Q6 |
| [`03-h-asizh-math-model.md`](03-h-asizh-math-model.md) | نگاشت آفین، جدول I (۹ الگو)، کنترل‌گر α/γ/β، DSE (الگوریتم ۱، تابع هزینه)، اثبات لیاپانوف UUB، جاذب سه‌بعدی |
| [`04-h-asizh-microarchitecture.md`](04-h-asizh-microarchitecture.md) | Q7.19، ثابت‌های RTL، PWL، datapathها، clamping، fast-bleed، Light TMR و Restoring Organ، time-multiplexing |
| [`05-glfi-framework.md`](05-glfi-framework.md) | GLFI: پنج مرحله، Shadow Hook، چهارمقداری، FRE/CV، چهار پیامد، مدل خطا، نگاشت به کد، تعداد سایت‌ها، مقایسهٔ ابزارها |
| [`06-results-ppa-reliability-learning.md`](06-results-ppa-reliability-learning.md) | جدول II (PPA)، Fig. 9 (توزیع پیامدها)، جدول III (RFoM)، مقایسه با TMR، مطالعهٔ موردی یادگیری (Fig. 8 و 10) |
| [`07-seminar-slides.md`](07-seminar-slides.md) | اسلاید به اسلاید، با جدول مقایسهٔ FT و خلاصهٔ SPANNER، SoftSNN و Spyrou |
| [`08-repositories-map.md`](08-repositories-map.md) | دو مخزن: ساختار، خط تکامل GLFI به GateScan Mark III، نتایج GateScan، پیوندهای مفهومی |
| [`09-consistency-audit.md`](09-consistency-audit.md) | **ممیزی:** ۳۰+ ناسازگاری بین مقاله، اسلاید، فصل ۱ و کد، با سطح اطمینان و اولویت اصلاح |
| [`10-glossary.md`](10-glossary.md) | واژه‌نامهٔ انگلیسی و فارسی |
| [`11-key-numbers.md`](11-key-numbers.md) | برگهٔ همهٔ اعداد کلیدی با منبع |
| [`12-bibliography-map.md`](12-bibliography-map.md) | نگاشت مراجع کلیدی بین سه شماره‌گذاری |
| [`kb_facts.json`](kb_facts.json) | نسخهٔ ماشین‌خوان اعداد. حاصل‌ضرب‌ها و جمع‌ها در زمان ساخت خودکار کنترل شدند |
| [`tools/rtl_model.py`](tools/rtl_model.py) | مدل پایتون بیت‌دقیق `mark2_homeostatic.vhd` برای بازتولید موارد A1 و B8 ممیزی |

## ۳. نقشهٔ ذهنی یک‌خطی
```
Edge/Cloud offloading (Q0) → دستگاه باید خودش قابل‌اتکا باشد → DNN accel. پرمصرف (Q1) → SNN + DVS (Q2)
→ SA1 = تشنج دیجیتال، TMR گران (Q3) → H-ASIZH: آستانهٔ تطبیقی درون نورون + اثبات UUB + Q7.19 بدون ضرب
→ از کجا بدانیم؟ (Q4) → GLFI سطح گیت چهارمقداری → 4.2٪ خطرناک در برابر 12.0٪ TMR، RFoM 4.76 در برابر 1.13
→ دوام در یادگیری؟ (Q5) → 256-1024-10 TTFS/STDP، 81.8٪، 1020 از 1024 فعال → GateScan Mark III (بازهٔ تضمین‌شده)
→ Q6 باز: BioVision، Homeostasis 2.0، تراشهٔ بینایی مقاوم به خطا
```

## ۴. سه یافتهٔ مهم ممیزی (جزئیات در `09`)
1. **معادلهٔ U در مقاله (Eq. 6 و 8) با RTL و Eq. 23 علامت مخالف دارد.** شبیه‌سازی بیت‌دقیق نشان می‌دهد نورون RTL با I = 0 در کف clamp (V = −0.5 ≈ −97 mV) می‌نشیند، نه در حالت استراحت طبیعی.
2. **مخزن عمومی GLFI از نسخهٔ نهایی عقب است.** به گفتهٔ نویسنده نتایج مقاله درست‌اند و مخزن قدیمی است. در مخزن فعلی این‌ها نیست: netlist و نتایج Restoring Organ، classifier و CSVها. stimulus برای هر معماری فرق دارد و zoning عملاً همه را COMB_CLOUD می‌کند. چون مقاله به این مخزن ارجاع می‌دهد، به‌روزرسانی آن پیش از داوری توصیه می‌شود.
3. **اسلایدها با مقاله نمی‌خوانند:** واحد توان mW در برابر µW، نگاشت `64(v+65)` در برابر `(v+65)/64`، دقت یادگیری 84.3٪ در برابر 81.8٪، و ادعای bridging/stuck-open.

## ۵. نگهداری
- برای افزودن منبع تازه: فایل اصلی را در `originals/` و متن استخراج‌شده را در `sources/` بگذارید، یادداشت مربوط را به‌روز کنید و اعداد تازه را به `11` و `kb_facts.json` اضافه کنید.
- `originals/` (حدود ۴۱ مگابایت؛ PDF مقاله ۳۰ MB) هم در همین مخزن است، به درخواست مالک، تا همه‌چیز یک‌جا باشد.
