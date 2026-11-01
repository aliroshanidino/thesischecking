# 22 — دک اسلاید تز: طرح نهایی (۳۸ اسلاید) و پیش‌نویس اولیه

> **وضعیت:** پیش‌نویس. ترتیب نهایی پس از رسیدن **دک تز مبنا** با آن تطبیق داده می‌شود. ظاهر اسلایدها از **دک سمینار** (`originals/seminar_H-ASIZH_Roshani.pptx`) و **دک مقاله** (هنوز نرسیده) گرفته می‌شود.
> **زبان دک:** انگلیسی، مثل سمینار.
> **منابع محتوا:** یادداشت‌های `01` تا `21`.


## نسخهٔ ساخته‌شده (2026-11-01): `deliverables/thesis_progress_deck.pptx` و `.pdf`

**مبنای ساخت:**
- **روند:** از دک تز مبنا (پایان‌نامهٔ GAP، Younesi، شریف، ۳۳ اسلاید). ترتیب: مقدمه (پیش‌زمینه، اهمیت، اهداف) ← مرور ادبیات با جدول مقایسه ← روش ← نتایج ← جمع‌بندی ← مراجع ← مقالات پژوهشی ← تشکر. این دک متعلق به شخص دیگری است و در مخزن گذاشته **نشده**.
- **ظاهر:** از دک مقالهٔ H‑ASIZH (`originals/H-ASIZH_paper_slides.pptx`). همان نوار ناوبری، رنگ‌ها و فونت Palatino. اسلایدهای روش و نتایج H‑ASIZH مستقیماً از همان دک بازاستفاده شدند.
- **اسکریپت تولید:** `tools/build_thesis_deck.py`.

| # | اسلاید | منشأ |
|---|---|---|
| 1 | عنوان (M.Sc. Thesis، عنوان رسمی، دو استاد راهنما) | دک مقاله، ویرایش‌شده |
| 2 | Outline | دک مقاله، ویرایش‌شده |
| 3 | جداکنندهٔ 01 Introduction | دک مقاله |
| 4 | Where Should Intelligence Live? (نردبان پیوستار و فرض پنهان) | جدید |
| 5 | Why Offloading Fails Safety-Critical Vision (۸ گروه) | جدید |
| 6 | Our Anchor: Build the Extreme-Edge Device (دو دست‌آویز، جدول توان، چرا اسپایک) | جدید |
| 7 | Inside a Time-Multiplexed SNN Accelerator: Who Can Fail? | جدید، با شکل SA1/SA0 دک مقاله |
| 8 | Research Gaps (G1 تا G6) | جدید |
| 9 | Research Questions and Contributions (Q0 تا Q6؛ C1 تا C5) | جدید |
| 10 | جداکنندهٔ 02 | دک مقاله |
| 11 | Accelerators for Vision (دسته‌های A و B) | جدید |
| 12 | Neuromorphic Processors and Neuron Cores (دستهٔ C) | جدید |
| 13 | Fault Tolerance in SNN Hardware, Layer by Layer (دستهٔ D) | جدید |
| 14 | Fault-Injection and Reliability Tools (دستهٔ E) | جدید |
| 15 | Bio-Inspired Spiking Vision Systems (دستهٔ F) | جدید |
| 16 | Where This Thesis Stands (ماتریس جایگاه) | جدید |
| 17 | جداکنندهٔ 03 (پنج گام) | دک مقاله، ویرایش‌شده |
| 18 | Methodology: Three Phases, One Device | جدید |
| 19 تا 22 | Phase 1: کنترل‌گر، لیاپانوف، ریزمعماری، سخت‌سازی صفحهٔ کنترل | دک مقاله |
| 23 | Phase 2 · From GLFI to GateScan | جدید |
| 24 | Phase 3 · BioVision-SNN Architecture | جدید |
| 25 | Phase 3 · Hardware-Aware Retina and Learning | جدید |
| 26 | جداکنندهٔ 04 | دک مقاله |
| 27 تا 30 | PPA، توزیع پیامد خطا، RFoM، یادگیری روی تراشه | دک مقاله |
| 31 | BioVision-SNN: Results So Far (فاز ۰ و ۱) | جدید |
| 32 | جداکنندهٔ 05 | جدید |
| 33 | Conclusion | جدید |
| 34 | Future Work | دک مقاله، ویرایش‌شده |
| 35 | Research Articles and Artefacts | جدید |
| 36 | References (I) [1–53] | دک مقاله |
| 37 | References (II) [54–107] | جدید |
| 38 | Thank you | دک مقاله |

**قرارداد مراجع:**
- شماره‌های ۱ تا ۵۳ همان فهرست دک مقاله‌اند، تا ارجاع اسلایدهای بازاستفاده‌شده درست بماند.
- مراجع تازه از ۵۴ شروع می‌شوند.
- مشخصات کامل چند مرجع بررسی‌نشده است (NeuFT، Suh 2023، Sterpone 2023، FORTALESA). در متن مرجع با توصیف یا DOI آمده‌اند و پیش از ارائه باید کامل شوند.

## پیش‌نویس اولیه

| # | بخش | عنوان اسلاید (EN) | محتوا و منبع |
|---|---|---|---|
| 1 | — | Title | عنوان رسمی (EN)، نام، اساتید، CPS Lab، شریف |
| 2 | Intro | Where should intelligence live? | مأموریت‌های حیاتی (پهپاد، خودرو، ربات، ایمپلنت) و پیوستار ابر، مه، لبه و لبهٔ دور، با تصویر نردبان قیود (`02` §۱.۲، Fig. 1.1) |
| 3 | Intro | The offloading paradigm and its hidden assumption | Neurosurgeon، split و federated؛ «دستگاه جعبه‌سیاهی که درست کار می‌کند» (`02` §۱.۳) |
| 4 | Intro | Why offloading fails safety-critical vision | ۲۴ ضعف در ۸ گروه، به‌صورت آیکون‌دار (`19` §۳) |
| 5 | Intro | Two anchors: extreme edge + a purpose-built device | دو دست‌آویز و موضع متوازن (`19`، `20`) |
| 6 | Intro | Edge-device constraints → from DNN accelerators to SNN | SWaP-C؛ ۱۱ خانوادهٔ شتاب‌دهی؛ NPU متراکم در برابر نورومورفیک؛ ODIN و time-multiplexing (`19` §۴، `20` §۴) |
| 7 | Intro | The new bottleneck: a device that is alone | چهار جزء آسیب‌پذیر شتاب‌دهندهٔ time-multiplexed؛ SA1 یعنی تشنج دیجیتال؛ TMR = 3.40× سلول (`20`، `06`) |
| 8 | Intro | Research gaps | شش شکاف (`02` §۱.۸، `01` §۴) |
| 9 | Intro | Research questions Q0 → Q6 | نقشهٔ سفر پژوهشی (Fig. 1.2) |
| 10 | Intro | Objectives & contributions | پنج دستاورد و سه فاز (`01` §۵، `20` §۵) |
| 11 | Lit. review | Literature map (top-down) | شش دسته A تا F (`21` §۱) |
| 12 | Lit. review | A · Edge vision DNN accelerators | Eyeriss، TPU، UAV FPGA و حد توان (`21` §۲) |
| 13 | Lit. review | B · Fault-tolerant DNN accelerators | Zhang، SalvageDNN، ABFT، FORTALESA، TMR فضایی (`21` §۳) |
| 14 | Lit. review | C · Neuromorphic processors & neuron cores | TrueNorth، Loihi 2، SpiNNaker2، ODIN، MorphIC، Speck، QUANTISENC، ایژیکویچ بی‌ضرب (`21` §۴) |
| 15 | Lit. review | D · Fault tolerance in SNN hardware (layer by layer) | سیستم و حافظه / زیست‌الهام / سطح نورون، با جدول نقد (`21` §۵) |
| 16 | Lit. review | E · Fault-injection & reliability tools | جدول ابزارها (`21` §۶) |
| 17 | Lit. review | F · Bio-inspired spiking vision systems | جایگاه BioVision و SpikeYOLO به‌عنوان مرجع (`21` §۷، `14`) |
| 18 | Lit. review | Positioning matrix: where this thesis stands | ماتریس ۱۰ ستونه (`21` §۸) |
| 19 | Method | Methodology overview: three phases | هستهٔ مقاوم → شبیه‌ساز قابل اعتماد → BioVision (`20`) |
| 20 | Method | Phase 1a · H-ASIZH model | نگاشت آفین، کنترل‌گر α/γ/β، DSE (`03`) |
| 21 | Method | Phase 1b · Lyapunov UUB & 3-D homeostatic attractor | (`03` §۵ و §۶) |
| 22 | Method | Phase 1c · Micro-architecture & control-plane hardening | Q7.19، PWL، clamp و fast-bleed، Light TMR و Restoring Organ، Sky130 (`04`) |
| 23 | Method | Phase 2 · GLFI → GateScan | پنج مرحله، Shadow Hook، چهارمقداری، رده‌بندی نورومتریک، بازهٔ گواهی‌شده (`05`، `08`) |
| 24 | Method | Phase 3 · BioVision-SNN architecture | شبیه‌ساز شبکیه P/K/M، LGN، V1 و V2، مسیر شکمی و پشتی، عمق، نقشهٔ اولویت و PFC، مرز مالکیت (`13`، `14`) |
| 25 | Results | Core PPA (Sky130) & fault campaign | جدول II و Fig. 9 (`06`) |
| 26 | Results | Reliability figure of merit + on-chip learning | جدول III؛ 81.8٪ و 1020 از 1024 فعال (`06`) |
| 27 | Results | BioVision Phase 0 & 1 results | جدول نتایج فاز ۰؛ فاز ۱ (رنگ +6.7٪، ناوردایی)؛ کف H‑ASIZH و Homeostasis 2.0 (`15`، `16`) |
| 28 | Conclusion | Current conclusions & road ahead | آنچه به دست آمد؛ کار باز: فاز ۲ تا ۵ BioVision، کمپین آسیب‌پذیری میان‌لایه‌ای، LIF و IF مقاوم دوطرفه، پهپاد |
| 29–30 | References | References (2 slides) | منابع کلیدی از `12` و `21` |

**نکته‌هایی که پیش از ساخت باید تأیید شوند:**
- اعداد ممیزی: دقت 81.8٪ (نه 84.3٪)، واحد µW (نه mW)، نگاشت `(v+65)/64`.
- عنوان دقیق مرجع «TMR انتخابی روی LIF از Drexel».
- آیا نتایج نورون LIF یا IF دوطرفه هم در دک بیاید؟ کاربر گفت «زیاد توجه نکن»، پس فعلاً فقط یک خط در «کار باز».
