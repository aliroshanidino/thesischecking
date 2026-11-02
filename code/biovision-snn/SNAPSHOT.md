# کد BioVision-SNN: snapshot مخزن کاری

> **منبع:** مخزن کاری پروژه روی لپ‌تاپ کاربر (`B:\projects\image recognition accelerator\biovision-snn`)، شاخهٔ `phase-1`، commit `739ff3e` (2026-11-02). این commit همهٔ تغییرهای آخرین جلسهٔ کاری فاز ۱ (2026-10-20) را دارد.
> **گزارش کامل:** [`../../26-biovision-complete-technical-report.md`](../../26-biovision-complete-technical-report.md).
> **سوابق خام اجراها:** [`../biovision-snn-runs/`](../biovision-snn-runs/).

## آنچه اینجاست

همهٔ فایل‌هایی که git در مخزن کاری دنبال می‌کند، به‌اضافهٔ گزارش Word نهایی فاز ۰. فهرست:
- **کد:** بستهٔ `biovision/`، پیکربندی‌ها، کمپین‌ها، ابزارها و آزمون‌ها؛
- **سندها:** گزارش‌ها، شکل‌ها، `DECISIONS.md` و `STATUS.md`؛
- **نتیجه‌ها:** `results/all_runs.csv` (136 اجرا) و `results/invariance.csv`.

## تفاوت‌ها با مخزن کاری

| مورد | در مخزن کاری | اینجا | چرا |
|---|---|---|---|
| دستورالعمل پروژه | `CLAUDE.md` | `CLAUDE_BioVision.md` | طبق یادداشت 18 این مخزن، این فایل نباید دستورالعمل جلسه‌های کاری روی پایگاه دانش شود |
| کتابخانه‌های بیرونی | `third_party/SpykeTorch` (upstream commit `aa302c7`) و `third_party/psee_loader` (از [prophesee-automotive-dataset-toolbox](https://github.com/prophesee-ai/prophesee-automotive-dataset-toolbox)، commit `c09d34a`، مجوز Apache-2.0) | حذف شده | کد ما نیستند و کد ما آن‌ها را import نمی‌کند. SpykeTorch فقط برای مقایسهٔ پیاده‌سازی خوانده شد: [miladmozafari/SpykeTorch](https://github.com/miladmozafari/SpykeTorch) |
| فهرست سرور HPC | `docs/hpc_inventory.txt` | حذف شده | این مخزن عمومی است و آن فایل سرویس‌ها و درگاه‌های باز سرور دانشگاه را فهرست می‌کند |
| نشانی سرور | نشانی IP داخلی در `DECISIONS.md` و `tools/hpc.env` | `<HPC-IP>` | همان دلیل |

هیچ رمز، کلید یا توکنی در کد نبود. دیتاست‌ها، وزن‌های آموزش‌دیده و شکل‌های تک‌تک اجراها منتشر نشده‌اند.

## اجرا

بخش ۵-۲ گزارش ۲۶ را ببینید. خلاصه:
```
python -m pytest -q                                  # 108 آزمون
python tools/campaign.py campaigns/phase1_main.yaml  # یک کمپین
python tools/collect_all_runs.py                     # جدول همهٔ اجراها
```
مسیر داده و پوشهٔ کار در `tools/local.env` و `biovision/paths.py` تعریف شده است. پوشهٔ کار (`../work`) کنار مخزن قرار می‌گیرد.
