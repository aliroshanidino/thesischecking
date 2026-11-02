# thesischecking — پایگاه دانش پایان‌نامه و مقالهٔ H-ASIZH

**Knowledge base** for Ali Roshani's M.Sc. thesis (Sharif University of Technology, CPS Lab). It covers the H-ASIZH fault-tolerant Izhikevich neuron core, the GLFI gate-level fault-injection framework, and GateScan. The notes are in Persian and keep technical terms in English.

پایگاه دانش پایان‌نامهٔ کارشناسی ارشد علی روشنی (دانشگاه صنعتی شریف، آزمایشگاه CPS):

- **H-ASIZH:** هستهٔ نورون ایژیکویچ دیجیتال مقاوم به خطا با کنترل آستانهٔ تطبیقی.
- **GLFI:** چارچوب تزریق خطای سطح گیت.
- **GateScan:** جانشین GLFI.

**شروع از:** [`00-INDEX.md`](00-INDEX.md)

## محتوا

| مسیر | چیست |
|---|---|
| `00-INDEX.md` … `12-bibliography-map.md` | ۱۳ یادداشت دانش H‑ASIZH/GLFI: نمای کلی، فصل ۱، مدل ریاضی، ریزمعماری، GLFI، نتایج، اسلایدها، نقشهٔ مخزن‌ها، ممیزی سازگاری، واژه‌نامه، اعداد کلیدی، مراجع |
| `13-…` تا `18-…` | پروژهٔ **BioVision‑SNN** (Q6): دستورالعمل، سند معماری، گزارش فاز ۰ و ۱، تحلیل CSV نتایج، و قرارداد کاری |
| `26-biovision-complete-technical-report.md` | **گزارش فنی کامل BioVision‑SNN:** معماری، کد، روش آزمایش و همهٔ آزمایش‌های فاز ۰ و ۱ |
| `code/biovision-snn/` | کد کامل پروژهٔ BioVision‑SNN (پایتون، پیکربندی‌ها، کمپین‌ها، آزمون‌ها، گزارش‌ها) |
| `code/biovision-snn-runs/` | سوابق خام همهٔ اجراهای آزمایش (لاگ و metrics) |
| `kb_facts.json` | همهٔ اعداد کلیدی به شکل ماشین‌خوان |
| `sources/` | متن کامل استخراج‌شدهٔ همهٔ سندها: مقاله، اسلایدها، فصل ۱ (EN و FA) و در `sources/biovision/` سندهای BioVision، `results_all.csv` و شکل‌هایشان |
| `originals/` | فایل‌های اصلی: PDF مقالهٔ TCAS-I، PPTX سمینار و PDF رندرشدهٔ آن، DOCX فصل ۱ (EN و FA) و سه DOCX پروژهٔ BioVision |
| `tools/rtl_model.py` | مدل پایتونی بیت‌به‌بیت از `rtl/mark2_homeostatic.vhd` در مخزن GLFI، برای ممیزی |

## مخزن‌های مرتبط

- [`aliroshanidino/GLFI_fault_campaign`](https://github.com/aliroshanidino/GLFI_fault_campaign): چارچوب GLFI. snapshot عمومی آن قدیمی‌تر از نتایج نهایی مقاله است.
- [`gatescan-dev/gatescanMarkIII`](https://github.com/gatescan-dev/gatescanMarkIII): GateScan Mark III.1.

**مرجع حقیقت:** نتایج مقالهٔ TCAS-I. هر جا منابع با هم نمی‌خوانند، در [`09-consistency-audit.md`](09-consistency-audit.md) آمده است.
