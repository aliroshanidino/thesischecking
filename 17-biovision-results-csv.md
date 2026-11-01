# 17 — تحلیل `results_all.csv` (جدول یکجای نتایج BioVision)

> **منبع:** `sources/biovision/results_all.csv`. این فایل در مخزن پروژه در مسیر `reports/phase0/results_all.csv` قرار دارد.
> **خلاصهٔ گروه‌بندی‌شده:** `sources/biovision/results_all_summary_by_group.csv`، با ۱۶۷ ردیف (میانگین، انحراف معیار، اسپایک، وزن و سرعت برای هر گروه، variant، دیتاست و split).

---

## ۱. ساختار

- **۲۲۹ ردیف** و **۱۵ ستون**:

  ```
  run, group, variant, dataset, split, seed, acc, knn, C, spikes, weights, img_per_s, train_s, rstdp_final, rstdp_best_optimistic
  ```

- **۱۴۴ اجرای یکتا** در **۸۲ گروه**. گزارش فاز ۰ از «۱۴۱ اجرا» نام می‌برد. اختلاف کوچک است، احتمالاً به‌خاطر اجراهای فاز ۱ یا تکرارها.

| بُعد | توزیع |
|---|---|
| دیتاست | ETH-80: ۱۳۸، Caltech: ۷۵، MNIST: ۱۶ |
| split | validation: ۱۵۳، test: ۷۶ |
| خانوادهٔ اجرا | `runs/phase0` (۸۱)، `rl_main` (۳۳)، `eth80_main` (۳۰)، `eth80_screen2` (۲۰)، `eth80_screen3` (۱۶)، `phase0_misc` (۱۵)، **`phase1_main` (۱۲؛ غربال اولیهٔ SVM فاز ۱: s_grey، s_p، s_pk)**، `rl_attention` (۱۰)، `caltech_final` (۶)، `eth80_2016` (۳)، `eth80_final` (۳) |

**نام‌گذاری `variant` (خوانش):**
- `g{N}`: شبکهٔ N×N برای خوانش مکان‌دار. `g1` همان خوانش سراسری مقاله است.
- `l{k}`: لایه (`l0-2` یعنی چند لایه).
- `std`: استانداردسازی.
- `flip`: آینه‌سازی تصویرهای آموزش.
- `Cauto`: انتخاب خودکار C در SVM.
- `ovo`: یک‌به‌یک.
- `svm_grid*` و `rstdp`: نوع خوانش.

`rstdp_best_optimistic` همان «بهترین epoch آزمون» است، یعنی روش مقاله‌ها.

## ۲. ✅ تطبیق اعداد گزارش فاز ۰ با CSV (همه دقیقاً برابر)

| عدد گزارش | گروه در CSV | CSV | گزارش |
|---|---|---|---|
| RL Caltech، ما (کلسیمی)، epoch انتخاب‌شده | `rl_main/caltech_final/cm1_calcium` | 98.65 ± 0.49 (n=3) | 98.65 ± 0.49 |
| همان، بهترین epoch | همان، `rstdp_best_optimistic` | 98.94 ± 0.37 | 98.94 ± 0.37 |
| RL Caltech، تنظیمات Mozafari، epoch انتخاب‌شده | `rl_main/replicate_mozafari/...` | 96.52 ± 0.61 | 96.52 |
| همان، بهترین epoch | همان | 98.51 ± 0.64 | 98.51 ± 0.64 |
| RL ETH-80، leave-one-out، epoch انتخاب‌شده | `rl_main/eth_final_loo/m0_paper` | 81.83 ± 5.58 (n=10 fold) | 81.83 ± 5.58 |
| همان، بهترین epoch | همان | 84.36 ± 5.31 | 84.36 ± 5.31 |
| RL ETH-80 ۵/۵ (مرجع فاز ۰ در گزارش فاز ۱) | `rl_main/eth_final55/m0_paper` | 77.48 ± 1.00 / بهترین 77.87 ± 1.49 | همان |
| SVM Caltech، ما | `caltech_final/final/c5_conv1_8maps` | 98.96 ± 0.25 | 98.96 ± 0.25 |
| SVM Caltech، تنظیمات مقاله | `runs/phase0/..._caltech_3seeds` | 92.80 ± 1.15 | 92.80 ± 1.15 |
| SVM MNIST، ما | `mnist_final/mnist_g5` (`g5_l2`) | 98.52 ± 0.06 | 98.52 ± 0.06 |
| SVM MNIST، تنظیمات مقاله | همان (`g1_l2`) | 91.46 ± 0.36 | 91.46 ± 0.36 |
| SVM ETH-80 ۵/۵، ما (H‑ASIZH) | `eth80_final/final55/h1_hasizh` (`g4_l2_std_flip`) | 84.25 ± 3.49 | 84.25 ± 3.49 |
| SVM ETH-80، تنظیمات مقاله | `replicate/eth80_sdnn_paper` (`g1_l4`) | 44.55 ± 2.60 | 44.55 ± 2.60 |
| ETH-80 H‑ASIZH «85.7 و 91.5» | `eth80_main/confirm/h1_hasizh` (s1) | 85.67 (`g4_l2_std`) / 91.46 (`g4_l2_std_flip_Cauto`) | 85.7 / 91.5 |

## ۳. ملاحظات داده

- در اجراهای `rstdp`، ستون `weights` صفر است، یعنی ثبت نشده. گزارش عدد واقعی را می‌دهد: Caltech حدود ۲۳ هزار و ETH حدود ۳۰۸ هزار.
- ردیف‌های `eth80_final/final55/h1_hasizh` ستون‌های `spikes`، `img_per_s` و `train_s` را صفر یا خالی دارند. این‌ها متادیتای ثبت‌نشده‌اند.
- **بهترین‌های validation:**
  - ETH-80: 91.46٪ (`h1_hasizh`، `g4_l2_std_flip_Cauto`)
  - Caltech: 100٪ (چند پیکربندی؛ validation کوچک است)
  - MNIST: 98.49٪
- **غربال اولیهٔ فاز ۱** (`phase1_main/screen_svm`، ETH-80 validation):
  - خاکستری تا 74.70٪ (`g4_l4-6_std`)
  - P تا 74.09٪
  - P+K تا 75.61٪
  - این اعداد با جدول ۱۱ گزارش فاز ۱ برای «بهترین خوانش» سازگارند.
- نتایج آزمون نهایی فاز ۱ هنوز در این فایل نیستند.
