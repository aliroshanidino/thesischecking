# 08 — نقشهٔ دو مخزن GitHub و پیوند آن‌ها با اسناد

> این پایگاه دانش «کنار» دو مخزن زیر نگه داشته می‌شود:
> - `aliroshanidino/GLFI_fault_campaign` (عمومی) — مسیر محلی: `/home/user/GLFI_fault_campaign`
> - `gatescan-dev/gatescanMarkIII` (عمومی) — مسیر محلی: `/home/user/gatescanMarkIII`
> خود پایگاه دانش در مخزن جداگانهٔ `aliroshanidino/thesischecking` است.

---

## ۱. خط تکامل ابزار

```
H-ASIZH (پایان‌نامه / مقالهٔ TCAS-I)
   │  «Q4: How do we know?»
   ▼
GLFI (Mark I) ── aliroshanidino/GLFI_fault_campaign      ← ابزار کمپین مقالهٔ H-ASIZH (پانویس مقاله)
   │
   ▼
GateScan Mark I ── gatescan-dev/gatescan                  (بردارهای تصادفی کور + cocotb/Icarus)
   ▼
GateScan Mark II ── gatescan-dev/gatescanMarkII (b45eccd)  (FastAPI + React + ۳ عامل DeepSeek: Analyzer/Actor/Critic؛ سایت faass.viracoai.net)
   ▼
GateScan Mark III / III.1 (v3.1.0) ── gatescan-dev/gatescanMarkIII   (هستهٔ قطعی اثبات‌پذیر؛ LLM فقط پیشنهاد می‌دهد)
```

- فصل ۱ پایان‌نامه (Q4): «پاسخ ساختن یک چارچوب باز، سطح گیت و چهارمقداری GLFI بود و سپس رشد آن به **GateScan**، موتور تحلیل خطای معتبر و تکرارپذیر.»
- اسلاید ۱۸: «GLFI Engine **Mark I**» · اسلاید ۹: «Online **FAASS** service: faass.viracoai.net» (= سایت Mark II طبق HANDOFF).
- HANDOFF Mark III: ممیزی Mark II نشان داد testbench عامل هرگز به کمپین نمی‌رسید، نقص‌های هستهٔ E1–E12 باعث می‌شد **۱۰۰٪ خطاها Vulnerable** گزارش شوند (حتی خطای بدون hook)، و دو حفرهٔ امنیتی تأییدشده (S1 path traversal در آپلود، S2 تزریق اسکریپت Yosys از نام top). ← این یعنی ادعاهای «LLM testbench» اسلایدها مربوط به نسلی است که بعداً معیوب تشخیص داده شد.

## ۲. مخزن `GLFI_fault_campaign` (ساختار و نگاشت به مقاله)

| مسیر | محتوا | بخش مقاله |
|---|---|---|
| `rtl/mark2_{baseline,homeostatic,light_tmr,restoringorgan,ultimate_tmr}.vhd` | پنج واریانت VHDL نورون (Q7.19) | IV، VII |
| `synth/run_synth_all.sh` + `snn_core_*.v` | سنتز GHDL+Yosys به primitive generic (۴ مدل، بدون restoring organ) | V-A مرحله ۱ |
| `netlists/raw/*_generic.{v,json}` | netlistهای flatten | V-A |
| `code/target_extractor.py` | استخراج سایت‌ها + zoning هیوریستیک | V-A مرحله ۲ |
| `code/instrumentor.py` | Saboteur weaving (Logic Shadow Hook، گذرگاه fi_enable/fi_target_id/fi_value) | V-B |
| `netlists/instrumented/` | netlistهای ابزارگذاری‌شده + `targets_*.json` | V-B |
| `code/cocotb_orchestrator.py` | reset/warmup، چک قطعیت ۳ اجرا، حلقهٔ کمپین با checkpoint، CSV | V-C |
| `code/manifest_builder.py`، `tech_profile.py`، `utils.py` | ساخت manifest، پروفایل تکنولوژی، logger/config | — |
| `scripts/run_campaign.py` | داشبورد موازی («11 CORES»)، تقسیم به part | V |
| `sim/tb_top.v`، `sim/Makefile`، `sim/workspaces/*` | مدل‌های primitive Yosys، workspaceهای هر part (progress.txt، results.xml) | V-C |
| `config/project.yaml`، `manifests/*.json` | پیکربندی کمپین، runtime، golden، targets | V-C |

- تاریخچه: ۱۳ commit؛ اولین «Initial commit for GLFI fault campaign» (2026-06-23)؛ آخرین «new2» (2026-09-06). README ندارد.
- **وضعیت (به گفتهٔ نویسنده، 2026-11-01):** این مخزن نسخهٔ قدیمی‌تری از کد است. نتایج نهایی و درست همان‌هایی‌اند که در مقاله آمده‌اند. هر جا این پایگاه دانش «کد مخزن» را توصیف می‌کند، منظور همین snapshot قدیمی است.
- پایگاه دانش در این مخزن نیست. جایش مخزن جداگانهٔ `aliroshanidino/thesischecking` است.
- ثابت‌های RTL و جزئیات کد: ← `04` و `05`. ناسازگاری‌ها: ← `09` بخش الف و ب.

## ۳. مخزن `gatescanMarkIII` (خلاصه — برای جزئیات خود مخزن را ببینید)

- **مأموریت:** تحلیل آسیب‌پذیری خطا در سطح گیت: RTL (Verilog/VHDL) → سنتز → تزریق stuck-at و SEU → به‌جای یک درصد SDC، **بازهٔ تضمین‌شدهٔ آسیب‌پذیری** (certified bracket) با بازه‌های اطمینان دقیق (Clopper-Pearson، hypergeometric، Hoeffding-Serfling، census) + **escape certificate** + **رده‌بندی ۱۱‌گانه** (DUE, SDC, DLY, ESC, TOL, LAT, UNK, MSK, HEAL, BEN, INE) کنار دید کلاسیک SDC/DUE/Masked.
- **اصل طراحی:** «LLM پیشنهاد می‌دهد، هسته تصمیم می‌گیرد» (چارچوب FARM، Arlat 1990: Faults/Activation/Readouts/Measures؛ LLM فقط Activation). قضیهٔ **T3** در `docs/TRUST_PROOF.md`: عامل اشتباه فقط بازه را گشادتر می‌کند، هرگز غلط نمی‌کند.
- **ساختار:** `gatescan/core/` (synth، IR، fault universe، instrumentation، gates، workload DSL، موتورهای Verilator و Icarus/cocotb، campaign، latent follow-up، cone reduction، formal oracle، certify، stats، taxonomy، trigger، reports) · `gatescan/agents/` (analyzer، scenario، critic، interpreter، trigger؛ providers: manual exchange، Anthropic، OpenAI-compatible) · `gatescan/cli.py` · `backend/` (FastAPI) · `frontend/` (فارسی، RTL، بدون build) · `deploy/` (Docker، Caddy HTTPS، systemd، نصاب Ubuntu، لانچر Windows) · `benchmarks/shadowfi/` · `docs/` (TRUST_PROOF، design/01–03، HANDOFF_SITE_REBUILD، results/paper_data.json، shadowfi_comparison.md).
- **نتایج Mark III.1 (ShadowFI، stuck-at، scoped):**

| طرح | سلول | SDC [95% CI] | ShadowFI SDC | بازه، workload داده‌شده | بازه با عامل‌ها | ESC |
|---|---|---|---|---|---|---|
| SFUv1 | 22,344 | 94.3 [93.9, 94.7] | 92 | [96.6, 99.8] | [98.8, 99.5] | 70 از 171 masked |
| TCU | 103,280 | 72.3 [71.7, 72.9] | 72 | [72.5, 100] | [87.5, 100] | 457 از 831 |
| SFUv2 | 44,782 | 86.4 (census) | 80 | [88.2, 100] | [94.7, 100] | 48 از 369 |

  - ۱۳ تا ۵۵٪ آنچه دید سه‌رده‌ای «Masked» می‌نامد با شاهد بازپخش‌شده آسیب‌پذیر ثابت شد. SEU روی TCU: AVF = 74.65٪ [72.9، 76.4] (فقط FFهای scope). SVC کامپایل نشد (OOM، ۴۸۶ هزار سلول).
  - ITC'99: ۲۰ مدار (۳۹ تا ۱۰۴٬۸۷۳ سلول)؛ اوراکل فرمال در b09 تشخیص را از ۸۱.۵٪ به ۹۸.۰٪ دقیق رساند.
  - اعتبارسنجی: ۱۶۵/۱۶۵ دروازه؛ ۱۸۳۴ آزمایش دوموتوره، صفر اختلاف (۱۰۴ مورد وابسته به X)؛ آزمون جهش ۲۲/۲۳؛ ۳۶۰+ تست.
  - ابزارها: Yosys 0.33، Verilator 5.020، Icarus 12.0، cocotb 2.1.0.
  - مقالهٔ GateScan: پیش‌نویس **IEEE TCAD** با عنوان کاری «Masked Is Not Harmless…».

## ۴. پیوندهای مفهومی بین H-ASIZH و GateScan
| مفهوم در H-ASIZH/GLFI | معادل در GateScan Mark III |
|---|---|
| Masked / Tolerant / Critical / Fatal (FRE ≤ 20٪، CV ≤ 0.2) | MSK/TOL/SDC/DUE + DLY/LAT/ESC/UNK/HEAL/BEN/INE؛ «Masked» تفکیک می‌شود به «فقط زیر workload» در برابر «اثبات‌شده بی‌خطر» |
| AVF = (Critical + Fatal)/Total | کران پایین/بالای AVF با گواهی |
| «داده‌ها پوشش زیر workload مشخص‌اند، نه ATPG» (V-D) | دقیقاً همان مسئله‌ای که GateScan با bracket و escape certificate حل می‌کند |
| شبیه‌سازی Icarus چهارمقداری | دوموتوره Verilator + Icarus/cocotb، با X-dependence |
| تزریق داخلی Shadow Hook | `gatescan/core/instrument.py` |
| مقایسه با SHADOWFI | `benchmarks/shadowfi/` و مقایسهٔ خطابه‌خطا (`shadowfi_view`) |

**پیشنهاد:** بازاجرای کمپین پنج‌معماری H-ASIZH با GateScan Mark III.1 هم مشکلات B1–B4 مخزن GLFI را حل می‌کند و هم به‌جای درصد نقطه‌ای، بازهٔ تضمین‌شده برای Fig. 9/جدول III می‌دهد.

## ۵. نکتهٔ انتشار
پایگاه دانش، با متن کامل مقالهٔ submitted و فصل پایان‌نامه و فایل‌های اصلی، به تصمیم مالک در مخزن **عمومی** `aliroshanidino/thesischecking` قرار گرفته است (2026-11-01).
