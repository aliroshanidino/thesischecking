# 05 — چارچوب GLFI (Gate-Level Fault Injection): روش، طبقه‌بندی و نگاشت به کد

> منابع: مقاله بخش V و Fig. 7، اسلایدهای ۹ و ۱۸، فصل ۱ بخش 1.7، و کد `GLFI_fault_campaign/`.
> مسیر تکامل: **GLFI (Mark I) → GateScan Mark II → GateScan Mark III** (← `08-repositories-map.md`).
> ⚠️ هر جا «کد مخزن» آمده، منظور snapshot عمومی و **قدیمی‌تر** مخزن GLFI است. به گفتهٔ نویسنده، نتایج نهایی همان‌هایی‌اند که در مقاله آمده‌اند.

---

## ۱. چرا تزریق سطح گیت؟

- **قضیهٔ لیاپانوف** برای اغتشاش پیوسته روی حالت ایدئال درست است. اما سیلیکون این‌طور خراب نمی‌شود: یک خطای دائمی یک net از netlist سنتزشده را خراب می‌کند. اینکه خطا به خروجی اسپایک برسد یا نه به سه چیز بستگی دارد: ساختار بولی، حالت نورون و تعداد سیکل‌هایی که تا انتشار می‌گذرد.
- **دو روش رد شده:**
  1. **تزریق رفتاری در متغیر RTL:** سطحش غلط است. سنتز حساب را شدیداً بازسازی می‌کند (یک adder ۲۶ بیتی به یک carry chain بدون معادل در کد منبع تبدیل می‌شود) و masking سطح گیت، که بقا را تعیین می‌کند، بالای netlist دیده نمی‌شود.
  2. **FORCE/RELEASE داخل شبیه‌ساز:** سطح درستی دارد اما خوب مقیاس نمی‌شود و وابسته به vendor است.
- **چارچوب‌های باز** (SHADOWFI [44]) گلوگاه را با محاسبات hyperscale حل می‌کنند، اما تزریق‌شان بیرون از طرح است. GLFI تزریق را **داخلی** انجام می‌دهد و خطا را در خود مدار کامپایل می‌کند، پس در زمان اجرا هیچ مداخله‌ای لازم نیست.
- **ابزارهای تجاری** (Synopsys fault simulator [158] و ATPG/FuSa [159]) طبق فصل ۱ برای ISO 26262 و IEC 61508 ساخته شده‌اند. اما licensed، گران و بسته‌اند و نتایجشان بیرون از محیط دارای مجوز تکرارپذیر نیست.

## ۲. پنج مرحلهٔ GLFI (Fig. 7)

| مرحله | مقاله | کد مخزن |
|---|---|---|
| **1. Synthesis Toolchain** | GHDL (VHDL frontend plugin) و Yosys، مدار کاملاً flatten می‌شود تا همهٔ netها آدرس‌پذیر باشند، و به **primitiveهای generic** نگاشت می‌شود، نه کتابخانهٔ vendor. در نتیجه توزیع گزارش‌شده ویژگی معماری است. | `synth/run_synth_all.sh`. مسیر plugin سخت‌کد شده: `/home/libftizh/ghdl-yosys-plugin/ghdl.so`. خروجی: `netlists/raw/*_generic.v` و `.json` |
| **2. Target Extracting & Zoning** | parser خروجی هر primitive را به یکی از ۴ ناحیهٔ معنایی نگاشت می‌کند: `STATE_MEMORY`، `CONTROL_PLANE` (netهای ناشی از مقایسهٔ آستانه یا سیگنال اسپایک)، `DATAPATH` (حساب پهن) و `COMB_CLOUD` (بقیه). خروجی: Target Manifest (JSON). | `code/target_extractor.py` (regex پایتون). zoning **هیوریستیک بر اساس نام net** است (← بخش ۷) |
| **3. Saboteur Weaving (Logic Shadow Hook)** | instrumentor فقط **یک بار** netlist را تغییر می‌دهد، نه یک بار برای هر خطا. | `code/instrumentor.py` → `netlists/instrumented/*_instrumented.v` |
| **4. Simulation & Orchestration** | Icarus Verilog و cocotb (از راه VPI bridge). اول **۳ بار اجرای golden netlist** برای بررسی قطعیت، بعد اجرای همهٔ حالت‌های instrumented. | `code/cocotb_orchestrator.py`، `sim/tb_top.v`، `sim/Makefile` و `scripts/run_campaign.py` (داشبورد چندریسمانی «11 CORES») |
| **5. Physiology / Neuro-metric Analysis** | طبقه‌بندی timestampهای اسپایک (Raw Fault Signatures، CSV) | در مخزن **نیست**: `classifier.py` و `reporter.py` حذف شده‌اند (commitهای 2026-06-23) و فایل‌های CSV نتایج هم commit نشده‌اند |

## ۳. Logic Shadow Hook (هستهٔ نوآوری)

در هر هدف، instrumentor یک bypass کنترل‌پذیر از راه یک **گذرگاه خطای سه‌پورتی** درج می‌کند: `fi_enable`، `fi_target_id[31:0]` و `fi_value`. net هدف از driver اولیه‌اش جدا می‌شود، خروجی driver به یک shadow net می‌رود و خود net دوباره به‌صورت یک continuous assignment تعریف می‌شود:

```verilog
assign net = (fi_enable && fi_target_id == ID) ? fi_value : hook_net;
```

(در کد: `hook_{safe_net}_{t_id}`.)

**سه ویژگی:**
1. اگر `fi_enable = 0` باشد، عبارت همان driver اصلی است. netlist ابزارگذاری‌شده از نظر عملکرد با golden یکی است و **یک طرح کل کمپین را پوشش می‌دهد**.
2. `fi_target_id` یک ورودی top-level است، نه ثابت. پس بهینه‌سازی نمی‌تواند MUX را حذف کند. این حالتِ «شکست خاموش» جهش سادهٔ netlist است.
3. `fi_value` چهارحالته است، پس hook می‌تواند `x` یا `z` را به همان راحتی یک سطح منطقی تحمیل کند. در کد یک ورودی Verilog یک‌بیتی است که ذاتاً چهارحالته است، اما پیکربندی کمپین فقط مقدارهای `[0, 1]` را به کار می‌برد.

## ۴. شبیه‌سازی

- **منطق چهارمقداری IEEE 1364 (0، 1، X، Z):** انتشار حالت نامعلوم صریحاً شبیه‌سازی می‌شود. این وقتی مهم است که خطا یک comparator یا select line را تغذیه کند. شبیه‌ساز دومقداری بی‌صدا یک شاخه را انتخاب می‌کند و نتیجه‌ای خوش‌بینانه‌تر از سخت‌افزار واقعی می‌دهد.
- **زمان‌بندی:** هر اجرا **۲۰۰۰ سیکل** بدون خطا اجرا می‌شود تا حالت به چرخهٔ حدی برسد. بعد خطا دائماً اعمال می‌شود و اجرا تا **سیکل ۱۰٬۰۰۰** ادامه می‌یابد. این طول به‌خاطر ثابت leak برابر ۶۴ سیکل لازم است.
- **پیکربندی کد** (`config/project.yaml` و `manifests/runtime_config.json`):

```yaml
fault_model: { type: Stuck-At, values: [0, 1], mechanism: "Shadow-Hook (Mux-based)" }
simulation:  { simulator: icarus, clock_period_ns: 10, warmup_cycles: 20,
               injection_delay: 2000, observation_cycles: 10000, determinism_runs: 3 }
top_module: homeostatic_neuron2, technology: Yosys_Generic, total_targets: 2944
```

- **stimulus در کد** (`cocotb_orchestrator.py`): `I_syn` ثابت است و برای هر معماری **متفاوت**:
  - baseline: 650000 (≈ 1.240)
  - homeostatic و light TMR: 820000 (≈ 1.564)
  - بقیه (ultimate TMR و restoring organ): 850000 (≈ 1.621)
  - مقاله این مقادیر را گزارش نمی‌کند (← `09-consistency-audit.md`).
- **golden spikes** (`manifests/baseline_summary.json`، ۱۰ اسپایک): 105, 259, 512, 1512, 2805, 4054, 5309, 6563, 7817, 9071. ISI پایدار حدود 1254 سیکل است.

## ۵. طبقه‌بندی نورومتریک

یک نورون اسپایکی را نمی‌شود فقط pass/fail کرد. قطاری که چند سیکل جابه‌جا شده هنوز اطلاعاتش را حمل می‌کند. قطاری که تعداد را حفظ کند اما به burstهای نامنظم تبدیل شود این‌طور نیست.

```
FRE = |N_faulty − N_golden| / N_golden          (Firing-Rate Error)
CV  = σ_ISI / μ_ISI                              (ISI Coefficient of Variation)      (24)
باند تحمل: FRE ≤ 20%  و  CV ≤ 0.20
```

- **کران مطلق روی CV** اینجا مجاز است چون نمونهٔ سنتزشده tonic است (`c_hw = 0`، `d_hw = 0.094`) و CV بدون خطایش داخل باند است. برای پیکربندی bursting مثل IB یا CH، معیار باید نسبت به آمارهٔ golden خودش بیان شود.

| رده | تعریف |
|---|---|
| **Masked** | timestampها با مرجع یکسان‌اند |
| **Tolerant** | تغییر کرده اما داخل باند است |
| **Critical** | بیرون باند است اما هنوز شلیک می‌کند (سهم نورون را تخریب می‌کند) |
| **Fatal** | دائماً خاموش یا اشباع است (نورون را حذف می‌کند یا آن را منبع نویز منتشرشونده می‌کند) |

- **dangerous = Critical + Fatal** و **AVF = (N_critical + N_fatal) / N_total**.
- **survival = Masked + Tolerant.** «95.8% survival» در اسلایدها برابر 100 − 4.2 است.

## ۶. مدل خطا و محدوده (Section V-D)

- **مدل:** stuck-at تکی دائمی، روی **همهٔ** سایت‌های استخراج‌شده، در **هر دو قطب**، **بدون fault collapsing**.
- **چرا دائمی؟** برای یک طرح تطبیقی سخت‌تر است، چون گره stuck روی همهٔ ارزیابی‌های بعدی اثر می‌گذارد، نه فقط یک به‌روزرسانی ([37] SoftSNN).
- **سه محدودیت اعلام‌شده:**
  1. داده‌ها پوشش زیر یک workload مشخص‌اند، **نه** کارایی خطای ATPG [28]. تنها نقطهٔ مشاهده خروجی اسپایک است، پس خطایی که قطار خروجی را تغییر ندهد masked شمرده می‌شود.
  2. باقی‌ماندهٔ 10⁻¹³ مربوط به نگاشت آفین است، نه datapath پیاده‌شده که PWL هم دارد.
  3. قضیهٔ پایداری خطا را جریانی روی معادلهٔ غشا مدل می‌کند و DATAPATH و COMB_CLOUD را می‌پوشاند، نه منطق تصمیم.
- **تعداد سایت‌ها در مخزن** (Yosys generic، از `targets_*.json`؛ تعداد اجرا = سایت × ۲ قطب):

| ماژول | سایت‌ها | STATE_MEMORY | CONTROL_PLANE | DATAPATH | COMB_CLOUD | اجرا (SA0+SA1) |
|---|---|---|---|---|---|---|
| baseline_neuron2 | 2047 | 53 | 0 | 0 | 1994 | 4094 |
| homeostatic_neuron2 | 2944 | 79 | 0 | 0 | 2865 | 5888 |
| light_tmr_neuron2 | 4365 | 131 | 47 | 0 | 4187 | 8730 |
| ultimate_tmr_neuron2 | 4934 | 235 | 47 | 52 | 4600 | 9868 |
| restoringorgan_neuron2 | — | — | — | — | — | در مخزن نیست |

  workspaceهای `sim/` نشان می‌دهند کمپین‌ها در چند part اجرا شده‌اند: homeostatic در ۲ بخش ×2944، light TMR در ۳×2184 + 2178 و ultimate در ۳×2468 + 2464. همه با «DONE» تمام شده‌اند. workspaceهای تک‌بخشی قدیمی ناتمام مانده‌اند (69.4٪، 33.2٪ و 23.3٪).

## ۷. نکات مهم کد (برای توسعهٔ بعدی)

- **zoning:**
  - `dff` در نوع سلول → `STATE_MEMORY`.
  - نام net یا instance شامل `theta, beta, f_, vmax, vmin, umax, umin, fb, spk, voted` → `CONTROL_PLANE`.
  - شامل `v_, u_, pwl, sum, diff, dv, du, term` → `DATAPATH`.
  - بقیه → `COMB_CLOUD`.
  - چون Yosys بعد از flatten نام‌ها را به `_NNNN_` تبدیل می‌کند، در baseline و homeostatic **همهٔ** سایت‌های غیر DFF در `COMB_CLOUD` می‌افتند. تحلیل ناحیه‌ای مقاله با این پیاده‌سازی عملاً ممکن نیست.
- `tb_top.v` primitiveهای Yosys را تعریف می‌کند: `$_AND_`، `$_OR_`، `$_XOR_`، `$_NAND_`، `$_NOR_`، `$_XNOR_`، `$_NOT_`، `$_MUX_` و DFFهای PP0 و PP1.
- **ستون‌های CSV خروجی** (`CSV_RESULTS_PATH`، پیش‌فرض `results.csv`): `target_id, net_name, domain(SEQ/COMB), zone, fault_val, gld_spikes, flt_spikes, gld_times, flt_times`. checkpointing دارد، یعنی کار از ردیف‌های قبلی ادامه می‌یابد.
- مخزن **README ندارد** و پیام commitها توصیفی نیستند («new2»، «true»، «1111»).

## ۸. ادعاهای GLFI در اسلایدها در برابر مقاله

| ادعای اسلاید (۹ و ۱۸) | وضعیت در مقاله و کد |
|---|---|
| «Multi-agent LLM testbench generation» (cocotb) | در مقاله TCAS-I نیامده. در GateScan Mark II عامل‌های DeepSeek بودند و ممیزی Mark III نشان داد testbench عامل هرگز به کمپین نمی‌رسید |
| «4-valued logic for **bridging** and **stuck-open**» | مقاله و کد فقط stuck-at (SA0 و SA1) دارند |
| «VHDL + Verilog + Cocotb» | کد فعلی ورودی VHDL را با GHDL می‌خواند |
| «Online FAASS service: faass.viracoai.net» | همان سایت GateScan Mark II (طبق HANDOFF) |
| «Exhaustive campaign … 100% fault coverage» | exhaustive روی سایت‌های استخراج‌شده، بدون collapsing |

## ۹. مقایسهٔ ابزارها (اسلاید ۹، جدول ۲)

| ابزار | سطح تزریق | متن‌باز | ۴مقداری | VHDL و Verilog | محدودیت کلیدی |
|---|---|---|---|---|---|
| SpikeFI (Spyrou 2024) | نرم‌افزار (PyTorch) | ● | ○ | ○ | وفاداری فیزیکی ندارد |
| RADSAFiE (Monopoli 2025) | netlist (FPGA) | ○ | ○ | ○ | قفل روی Vivado، خطای bridging را مدل نمی‌کند |
| SHADOWFI (Guerrero 2025) | netlist (ASIC) | ● | ○ | ○ | فقط Verilog، حالت‌های X و Z را نمی‌گیرد |
| El-Sayed (2019–2023) | netlist یا ترانزیستور | ● | ○ | ○ | معماری خودکار کمپین GLFI ندارد |
| Spyrou (2022) | حافظه (FPGA) | ○ | ○ | ○ | فقط SEU حافظه، تزریق ترکیبی ندارد |
| **GLFI (این کار)** | شبیه‌سازی سطح گیت | ● | ● | ● | Shadow-Hook و LLM testbench و FAASS |
