# 21 — پایگاه مرور ادبیات برای اسلایدها و فصل ۳: طبقه‌بندی، ماتریس جایگاه و منابع

> **ساخته‌شده:** 2026-11-01. منابع: مراجع فصل ۱ (۱۶۲)، مراجع مقاله (۴۵)، اسلایدهای سمینار (۲۵)، سند معماری BioVision (۱۷ کار)، و **جست‌وجوی وب تازه** (پیوندها در بخش ۹).
> **علامت‌ها:**
> - ✔ = مشخصات در همین پایگاه دانش یا در جست‌وجوی این جلسه تأیید شده.
> - † = از دانش عمومی آمده و پیش از استناد باید مشخصات دقیق کتاب‌شناختی‌اش بررسی شود.
> - ⚠️ = اختلاف بین منابع (← `09`).

---

## ۱. نقشهٔ دسته‌ها

کار پیشین روی چهار محور سنجیده می‌شود:
1. **کاربرد:** بینایی (تصویر یا ویدیو)
2. **بستر:** شتاب‌دهندهٔ سخت‌افزاری
3. **محاسبه:** اسپایکی یا نورومورفیک
4. **قابلیت اتکا:** تحمل خطا

| دسته | بینایی | شتاب‌دهندهٔ سخت‌افزاری | اسپایکی | تحمل خطا | §  |
|---|---|---|---|---|---|
| A. شتاب‌دهنده‌های DNN برای بینایی لبه | ✓ | ✓ | ✗ | ✗ | ۲ |
| B. شتاب‌دهنده‌های DNN مقاوم به خطا | ✓ (اغلب CNN) | ✓ | ✗ | ✓ | ۳ |
| C. پردازنده‌ها و هسته‌های نورومورفیک | گاهی | ✓ | ✓ | ✗ | ۴ |
| D. تحمل خطای SNN و سخت‌افزار نورومورفیک | گاهی | گاهی | ✓ | ✓ | ۵ |
| E. ابزار تزریق و ارزیابی خطا | — | ابزار | گاهی | ارزیابی | ۶ |
| F. سیستم‌های بینایی اسپایکی و زیست‌الهام (جایگاه BioVision) | ✓ | به‌ندرت | ✓ | ✗ | ۷ |
| **این تز** | ✓ | ✓ (Sky130، P&R) | ✓ | ✓ (درون نورون و اثبات‌شده) | ۸ |

## ۲. دستهٔ A: شتاب‌دهنده‌های DNN برای بینایی لبه (بدون تحمل خطا)

| کار | سال و محل | نکتهٔ کلیدی | ارقام |
|---|---|---|---|
| DianNao ✔ | ASPLOS 2014 | طراحی حول دسترسی به حافظه | — |
| ShiDianNao † | ISCA 2015 | شتاب‌دهندهٔ CNN کنار حسگر برای بینایی | — |
| **Eyeriss** ✔ | JSSC 2017 | dataflow از نوع row-stationary | لایه‌های conv شبکهٔ AlexNet با 34.7 fps در 278 mW |
| **TPU** ✔ | ISCA 2017 | آرایهٔ systolic در مرکز داده | 15 تا 30 برابر سریع‌تر و 30 تا 80 برابر TOPS/W بهتر از CPU و GPU |
| NVDLA ✔ (به‌عنوان بستر FIdelity) | منبع باز | شتاب‌دهندهٔ استنتاج انویدیا | — |
| MCUNet ✔ (فصل ۱ [75]) | — | استنتاج در مقیاس ImageNet روی MCU | — |
| SSD کوانتیزه روی FPGA برای پهپاد (Suh و همکاران) ✔ | ACM TRETS 2023 | co-design برای ZU3EG | 2.54 W؛ 1.1 تا 8.7 برابر کاراتر از کارهای قبلی |
| YOLOv3-Tiny روی FPGA ارزان برای پهپاد ✔ | Electronics 2025 | بینایی بی‌درنگ پهپاد | — |
| IPU پیش‌پردازش و پس‌پردازش روی MPSoC برای پهپاد (Cittadini و همکاران) ✔ | Control Eng. Practice 2025 | — | — |
| LPODC (چالش DAC) ✔ | — | امتیازدهی هم‌زمان throughput، توان و دقت آشکارسازهای پهپاد | — |
| Capra و همکاران (مرور) ✔ | IEEE Access 2020 | توان پلتفرم‌ها | CPU: 10 تا 100 W؛ GPU: حدود 100 W؛ FPGA: 1 تا 10 W؛ ASIC: 0.1 تا 1 W |

**جمع‌بندی دستهٔ A:**
- کارایی و throughput بالاست.
- فرض ضمنی این است که سخت‌افزار درست کار می‌کند.
- در لبهٔ دور توان هنوز چند مرتبه بالاتر از بودجهٔ ایمپلنت و پوشیدنی است.

## ۳. دستهٔ B: شتاب‌دهنده‌های DNN مقاوم به خطا (غیراسپایکی)

| کار | سطح | سازوکار | مدل خطا | نکته |
|---|---|---|---|---|
| Li و همکاران ✔ | تحلیل | انتشار خطا وابسته به نوع داده، موقعیت بیت و لایه | گذرا | SC 2017 |
| Ares (Reagen و همکاران) ✔ | تحلیل | کمّی‌سازی تاب‌آوری DNN | — | DAC 2018 |
| Zhang و همکاران ✔ | systolic (شبه-TPU) | هرس آگاه از خطا و بازآموزی | **دائمی** | VTS 2018؛ «چند خطای دائمی دقت را شدیداً کم می‌کند» |
| SalvageDNN (Hanif و Shafique) ✔ | نگاشت | نگاشت آگاه از خطا بر اساس saliency | دائمی | Phil. Trans. A 2020 |
| Libano و همکاران ✔ | FPGA | سخت‌سازی انتخابی | SEU | IEEE TNS 2019 |
| ABFT برای ضرب ماتریس systolic روی FPGA ✔ | الگوریتمی | ABFT | — | IEEE TC 2021 (UFRGS، POLITO و ASU)؛ سربار کمتر از ۱٪ |
| FORTALESA ✔ | systolic بازپیکربندی‌پذیر | حفاظت رجیستر و MAC | گذرا و دائمی | arXiv 2025 |
| Ait Alam و همکاران ✔ | الگوریتمی | استفادهٔ دوباره از شتاب‌دهندهٔ معیوب بدون تغییر سخت‌افزار؛ شبیه‌ساز S3A | stuck-at در link و رجیستر وزن | arXiv 2024 |
| Sterpone و همکاران ✔ | FPGA مقاوم به تابش | جایابی برای کاهش حساسیت SET هستهٔ نورون CNN | SET | IEEE TCAD 2023؛ روی RTG4 |
| SR-YOLOv5s روی PolarFire SoC (پایان‌نامهٔ Capuano) ✔ | فضایی | آشکارساز مقاوم برای فضا | تابش | mAP50 برابر 0.927 |
| YOLO روی AMD Versal با آزمون پروتون (پایان‌نامهٔ BYU) ✔ | فضایی | تزریق در حافظهٔ پیکربندی و آزمون پروتون | SEU | 2026 |
| Antunes و Podobas (مرور) ✔ | — | NMR، DMR و TMR برای شتاب‌دهنده‌های NN فضایی | — | arXiv 2025 |
| Mittal؛ Ruospo و همکاران (مرورها) ✔ | — | مدل‌سازی، ارزیابی و کاهش | — | — |

**جمع‌بندی دستهٔ B:**
- حفاظت روی، اطراف یا بالای PE و حافظه اعمال می‌شود (نگاشت، هرس، ABFT، TMR).
- **اسپایکی نیست.**
- بیشتر برای SEU یا گذرا طراحی شده است.
- **TMR و NMR در پهپاد و فضا رایج است، اما هزینه‌اش سه برابر است.**

## ۴. دستهٔ C: پردازنده‌ها و هسته‌های نورومورفیک (بدون تحمل خطا)

| تراشه یا هسته | سال | فناوری | نورون | نکته |
|---|---|---|---|---|
| TrueNorth ✔ | Science 2014، TCAD 2015 | 28 nm | ۱ میلیون نورون، ۲۵۶ میلیون سیناپس | حدود 65 mW |
| SpiNNaker ✔ / SpiNNaker2 ✔ | 2014 / 2021 تا 2024 | 22 nm (SpiNNaker2) | چندهسته‌ای ARM | SpiNNaker2 حدود 0.72 W و 6.4 TOPS/W (طبق یک جدول مرور) |
| Loihi ✔ / Loihi 2 ✔ | 2018 / 2021 | 14 nm / Intel 4 | یادگیری روی تراشه | Loihi 2 حدود 15 TOPS/W (طبق یک جدول مرور) |
| Tianjic † | Nature 2019 | 28 nm | هیبرید ANN و SNN | — |
| **ODIN** ✔ (Frenkel) | TBioCAS 2019 | 28 nm | ۲۵۶ نورون، ۶۴ هزار سیناپس؛ **LIF یا مدل پدیدارشناختی ۲۰ رفتار ایژیکویچ**؛ time-multiplexed (کنترلر و scheduler روی AER) | 0.086 mm²، 12.7 pJ/SOP؛ **نقطهٔ شروع این تز** |
| **MorphIC** ✔ (Frenkel) | 2019 | 65 nm | چهارهسته‌ای، ۵۱۲ LIF در هر هسته، وزن دودویی، یادگیری تصادفی؛ time-multiplexing به سبک ODIN | حرکت به سمت شبکه روی تراشه |
| ReckOn † (Frenkel و Indiveri) | ISSCC 2022 | — | تک‌هسته‌ای، یادگیری آنلاین | — |
| **Speck** ✔ (SynSense و CASIA) | Nat. Commun. 2024 / ASYNC 2023 | — | SoC ناهمگام حسگر و محاسبه، خط لولهٔ CNN با ۳۲۷ هزار نورون، بدون کلاک | توان استراحت 0.42 mW؛ سیستم کامل 0.70 mW |
| **QUANTISENC** ✔ (Drexel، گروه Das) | arXiv 2024 / MWSCAS 2024؛ نسخهٔ ++ در Asilomar 2025 | دیجیتال، software-defined | LIF و CUBA، ممیز ثابت با کوانتش متغیر | چندهسته‌ای با interconnect مشترک و جمع‌کنندهٔ تقریبی |
| SNE † | DATE 2022 | — | کانولوشن رویدادمحور تنک | — |
| ایژیکویچ بی‌ضرب: Haghiri 2018 ✔، Sruthi و Bindiya 2025 ✔، PWL و comb-exp ✔ | TBioCAS / TCAS-I | — | Izhikevich | **هیچ‌کدام تحمل خطا ندارند** (جست‌وجوی این جلسه هم کار مقاوم به خطا روی ایژیکویچ دیجیتال پیدا نکرد) |

**جمع‌بندی دستهٔ C:** کارایی انرژی بالا، اما **قابلیت اطمینان بخشی از طراحی نیست**. هستهٔ time-multiplexed یک نقطهٔ شکست تکی برای صدها نورون است.

## ۵. دستهٔ D: تحمل خطای SNN و سخت‌افزار نورومورفیک (لایه‌به‌لایه)

| لایه | کار | سازوکار | مدل خطا | ضعف (از دید این تز) |
|---|---|---|---|---|
| **سیستم و حافظه** | SparkXD ✔، EnforceSNN ✔ (Putra) | DRAM تقریبی | خطای حافظه | فقط حافظه |
| | SoftSNN ✔ (DAC 2022) | Bound-and-Protect: clip وزن و غیرفعال‌سازی reset | **فقط گذرا** | ۱۴ تا ۱۸٪ مساحت؛ فقط اعداد نسبی |
| | ReSpawn ✔ (ICCAD 2021) | نگاشت و آموزش آگاه از خطا | حافظهٔ نامطمئن | نقشهٔ خطای آفلاین |
| | RescueSNN ✔ (Front. Neurosci. 2023 ⚠️) | FAM و bit-shuffling؛ مدل stuck-at در رجیستر وزن و گام‌های غشا | **دائمی** | ۳۶.۵٪ مساحت؛ نقشهٔ خطای آفلاین؛ بدون یادگیری روی تراشه |
| | FalVolt ✔ (Siddique 2023) | مقیاس‌دهی ولتاژ مقاوم به خطا | — | — |
| **نگاشت و NoC** | MigSpike ✔، Yerima 2023 ✔، R-NASH ✔، Big-Little µBrains ✔، eSpine ✔ (Titirsha) | مهاجرت، نگاشت روی 3D-NoC، چیدمان آگاه از طول عمر | دائمی | منابع یدکی، نقشهٔ خطا و از دست رفتن قطعیت زمانی |
| **زیست‌الهام (ناظر بیرونی)** | SPANNER ✔ (TNNLS 2018 ⚠️) | آستروسیت با e-SP روی FPGA | خطای سیناپس | ۴۵ DSP (سربار ۱۲۵٪)؛ ناظر بی‌حفاظت |
| | Naeem 2015 ✔، Rastogi ✔، Isik 2022 ✔، Varshika 2023 ✔ (آستروسیت تنظیم‌پذیر، ۹۴٪ با ۱۵٪ هستهٔ معیوب) | شبکهٔ آستروسیتی | — | همان |
| | **NeuFT** ✔ (Drexel، DFT 2024) | شبکه به «جزیره‌های سیناپسی» تقسیم می‌شود و هر جزیره یک آستروسیت آموزش‌دیده دارد | **SEU روی FPGA** (فضا) | ناظر جدا؛ گذرا |
| | Johnson 2018 ✔ (TCAS-I) | هموستاز از شبکهٔ آستروسیتی | — | **نزدیک‌ترین کار**؛ تنظیم‌کننده از نورون جداست |
| **سطح نورون و ساختار** | Spyrou 2021 ✔ (DATE) | dropout، self-test با شمارندهٔ ۳ بیتی، **TMR فقط در لایهٔ خروجی** | dead، saturated، timing | رفتاری؛ بدون PPA |
| | Spyrou 2022 ✔ (DATE) | تحلیل BER شتاب‌دهندهٔ FPGA | SEU حافظه | تحلیل، بدون راه‌حل |
| | El-Sayed 2019 تا 2023 ✔ | مدل‌های خطای نورون از سطح ترانزیستور؛ self-test | — | — |
| | Das و Varshika 2025 ✔ (DATE) | محاسبهٔ دندریتی و مهار ساختاری | — | حدود ۶۰٪ سربار برای هر نورون |
| | Cheng 2025 ✔ (VLSI Symp.) | تصویربردار نورومورفیک مقاوم به تابش با پیکسل‌های خودترمیم | تابش | سطح پیکسل |
| | Gleyo و Girau ✔ (DATE 2026) | **population coding** برای تحمل خطای دائمی بدون آشکارساز | dead و saturated در LIF | افزونگی جمعیتی |
| | Schuman 2020 ✔ (IJCNN) | آموزش برای تاب‌آوری | — | — |
| **مرورها** | Stratigopoulos و همکاران ✔ (DFT 2023، مرور آزمون و قابلیت اطمینان SNN)؛ special session 2023 ✔ (یادگیری روی سخت‌افزار معیوب اثر خطا را حدود ۱۵٪ کم می‌کند)؛ مرور قابلیت اطمینان SNN روی ReRAM-CIM ✔ (2024)؛ Vatajelu 2019 ✔ | — | — | — |

⚠️ **«TMR انتخابی روی LIF از گروه Drexel»** که در طرح فصل ۳ آمده، در جست‌وجو پیدا نشد. نزدیک‌ترین‌ها:
- TMR فقط در لایهٔ آخر: Spyrou (DATE 2021/2022)
- کار دندریتی Das و Varshika
- NeuFT و QUANTISENC از Drexel
- population coding از Gleyo و Girau

**عنوان دقیق مرجع مورد نظر لازم است.**

## ۶. دستهٔ E: ابزار تزریق و ارزیابی خطا

| ابزار | سطح | متن‌باز | ۴مقداری (X/Z) | زبان یا بستر | نکته |
|---|---|---|---|---|---|
| Synopsys fault simulator / TestMAX FuSa ✔ | گیت | ✗ | ✓ | تجاری | ISO 26262 و IEC 61508؛ گران و بسته |
| **SHADOWFI** ✔ (IEEE Access 2025 ⚠️) | netlist (ASIC) | ✓ | ✗ | Verilog | hyperscale؛ تزریق از بیرون طرح |
| **RADSAFiE** ✔ (IEEE Access 2025) | netlist (FPGA) | ✗ | ✗ | Vivado | قفل روی vendor |
| **FIdelity** ✔ (He، Balaprakash و Li، MICRO 2020) | مدل نرم‌افزاری از RTL شتاب‌دهندهٔ DL | — | — | NVDLA | ۴۶ میلیون آزمایش؛ خطای گذرای منطق؛ اعتبارسنجی با RTL |
| PyTorchFI †، TensorFI †، NVBitFI † | نرم‌افزار و GPU | ✓ | ✗ | PyTorch، TF، CUDA | DNN |
| **enpheeph** ✔ (Colucci، Steininger و Shafique، IROS 2022) | نرم‌افزار | ✓ | ✗ | GPU | SNN و DNN فشرده؛ سربار کمتر از ۲۰٪ |
| **SpikingJET** ✔ (Gogebakan و Di Carlo، IOLTS 2024) | نرم‌افزار (snnTorch) | ✓ | ✗ | SNN conv، FF و FC | وزن، پارامتر نورون و حالت |
| **SpikeFI** ✔ (Spyrou 2024) | نرم‌افزار (SLAYER) | ✓ | ✗ | PyTorch | — |
| El-Sayed ✔ | netlist و ترانزیستور | ✓ | ✗ | — | بدون معماری کمپین خودکار |
| **GLFI → GateScan (این تز)** | **گیت، تزریق درون مدار** | ✓ | **✓** | VHDL و Verilog، Icarus و Verilator | Shadow Hook؛ رده‌بندی نورومتریک؛ GateScan: بازهٔ گواهی‌شده و قطعیت دوموتوره |

## ۷. دستهٔ F: سیستم‌های بینایی اسپایکی و زیست‌الهام (جایگاه BioVision)

- **۱۷ کار جدول مرور سند معماری** (← `14` §۱): Kheradpisheh 2018، Mozafari 2018، Masquelier و Thorpe 2007، Zhou و Li 2022، Spike-VisNet 2024، Paredes-Vallés 2019، BioMotion-SNN 2025، Chelian و Srinivasa 2013، Hu 2017، WWN-2 2010، WW-Nets 2020، Han و Sereno 2022، Choi 2023، VeDo-Net 2024، StereoSpike 2022، Kiran و Tripathi 2025، VOneNet 2020.
- **آشکارسازی اسپایکی با backprop (مرجع عددی برای هدف COCO):**
  - **SpikeYOLO** ✔ (Luo و همکاران، ECCV 2024): COCO **66.2٪ mAP@50 و 48.9٪ mAP@50:95**؛ Gen1 **67.2٪ mAP@50**. نورون I-LIF با آموزش صحیح و استنتاج spike-driven، بر پایهٔ ساده‌شدهٔ YOLOv8. **با backprop آموزش دیده است، نه یادگیری محلی.**
  - Spiking-YOLO † (Kim و همکاران، AAAI 2020)؛ EMS-YOLO † (ICCV 2023).
- **مرز مالکیت (border ownership):**
  - Zhou، Friedman و von der Heydt 2000 ✔ (زیستی)
  - مدل‌های Hu، von der Heydt و Niebur ✔ (eNeuro 2019، ناسپایکی با سلول‌های grouping)
  - مدل اسپایکی پیش‌خور Supèr و همکاران ✔ (PLoS ONE 2010)
  - مدل اسپایکی disinhibitory Wagatsuma و همکاران ✔ (2015)
  - **هیچ مدل مرز مالکیت با STDP یا یادگیری محلی پیدا نشد**، و این یک شکاف است.
- **شاهد زیستی توجه:** Debes و Dragoi ✔ (Science 2023): خاموش کردن بازخورد V4 به V1 اثر توجه را از بین می‌برد.

## ۸. ماتریس جایگاه (برای اسلاید مقایسه)

| کار | بینایی | HW (RTL/ASIC) | اسپایکی | FT | سطح FT | خطای دائمی | تضمین صوری | ارزیابی سطح گیت با ۴ مقدار | یادگیری محلی |
|---|---|---|---|---|---|---|---|---|---|
| Eyeriss، TPU (A) | ✓ | ✓ | ✗ | ✗ | — | — | — | — | ✗ |
| Zhang 2018، SalvageDNN (B) | ✓ | ✓ | ✗ | ✓ | نگاشت و هرس | ✓ | ✗ | ✗ | ✗ |
| YOLO فضایی با TMR (B) | ✓ | FPGA | ✗ | ✓ | سیستم (NMR) | SEU | ✗ | ✗ | ✗ |
| ODIN، MorphIC، Speck (C) | گاهی | ✓ | ✓ | ✗ | — | — | — | — | ✓ (ODIN و MorphIC) |
| QUANTISENC (C) | ✗ | ✓ | ✓ (LIF) | ✗ | — | — | — | — | ✗ |
| SoftSNN، RescueSNN (D) | MNIST | ✓ (65 nm) | ✓ (LIF) | ✓ | سیستم و حافظه | فقط RescueSNN | ✗ | ✗ | ✗ |
| SPANNER، NeuFT (D) | — | FPGA | ✓ (LIF) | ✓ | ناظر بیرونی | گذرا یا سیناپس | ✗ | ✗ | — |
| Johnson 2018 (D) | — | ✓ | ✓ | ✓ | هموستاز بیرونی | ✓ | ✗ | ✗ | — |
| Spyrou 2021 (D) | N-MNIST | ✗ (رفتاری) | ✓ (I&F) | ✓ | نورون و لایهٔ خروجی | dead و saturated | ✗ | ✗ | ✗ |
| Das و Varshika 2025 (D) | — | ✓ | ✓ | ✓ | ساختاری درون نورون | ✓ | ✗ | ✗ | — |
| Gleyo و Girau 2026 (D) | ✗ (رگرسیون) | ✗ | ✓ (LIF) | ✓ | population coding | ✓ | ✗ | ✗ | ✗ |
| SpikeYOLO (F) | ✓ COCO | ✗ | ✓ | ✗ | — | — | — | — | ✗ (backprop) |
| Kheradpisheh و Mozafari 2018 (F) | ✓ | ✗ | ✓ | ✗ | — | — | — | — | ✓ |
| **این تز: H‑ASIZH + GLFI/GateScan + BioVision** | **✓** (MNIST روی تراشه؛ Caltech و ETH در BioVision) | **✓ (Sky130، P&R)** | **✓ (Izhikevich؛ LIF و IF)** | **✓** | **درون دینامیک نورون** و Restoring Organ برای صفحهٔ کنترل | **✓ (stuck-at روی همهٔ گره‌ها)** | **✓ (UUB لیاپانوف)** | **✓** | **✓ (STDP، R-STDP، روی تراشه)** |

## ۹. پیوندهای جست‌وجوی این جلسه

- QUANTISENC: [arXiv 2404.02248](https://arxiv.org/html/2404.02248v1) · [Drexel، QUANTISENC++](https://researchdiscovery.drexel.edu/esploro/outputs/conferenceProceeding/QUANTISENC-A-Fully-Configurable-Many-Core-Neuromorphic-Hardware/991022047146604721)
- NeuFT: [Drexel، DFT 2024](https://researchdiscovery.drexel.edu/esploro/outputs/conferenceProceeding/Towards-Biology-Inspired-Fault-Tolerance-of-Neuromorphic/991021965371304721)
- Population coding: [DATE 2026](https://past.date-conference.com/proceedings-archive/2026/DATA/293.pdf) · [HAL](https://hal-sfo.ccsd.cnrs.fr/LORIA-AIS/hal-05450820v1)
- SpikeYOLO: [arXiv 2407.20708](https://arxiv.org/pdf/2407.20708) · [ECCV 2024](https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/04704.pdf)
- FIdelity: [MICRO-53](https://www.microarch.org/micro53/papers/738300a270.pdf) · [IEEE](https://ieeexplore.ieee.org/document/9251852/authors)
- مرورهای قابلیت اطمینان SNN: [Stratigopoulos et al., DFT 2023](https://hal.sorbonne-universite.fr/LIP6-CIAN/hal-04176109v1) · [special session 2023](https://arxiv.org/pdf/2305.01818) · [ReRAM-CIM survey 2024](https://arxiv.org/pdf/2412.10389)
- شتاب‌دهنده‌های معیوب: [Ait Alam 2024](https://arxiv.org/pdf/2412.16208) · [FORTALESA 2025](https://arxiv.org/html/2503.04426v1) · [ABFT systolic TC 2021](https://iris.unitn.it/bitstream/11572/376659/2/TC_2021_ASU_UFRGS_POLITO__Rev1_.pdf) · [Zhang 2018](https://arxiv.org/pdf/1802.04657v2.pdf)
- شتاب‌دهندهٔ NN فضایی: [Antunes & Podobas survey](https://arxiv.org/html/2504.16173v1) · [Capuano thesis](https://www.fedoa.unina.it/15958/) · [BYU Versal YOLO](https://scholarsarchive.byu.edu/etd/11283) · [Sterpone TCAD 2023](https://iris.polito.it/handle/11583/2983793)
- Speck: [Nat. Commun. 2024](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11127998/) · [ASYNC 2023](https://arxiv.org/abs/2304.06793)
- ابزارهای FI برای SNN: [enpheeph](https://arxiv.org/abs/2208.00328v1) · [SpikingJET](https://arxiv.org/abs/2404.00383v1) · [SpikeFI](https://ar5iv.labs.arxiv.org/html/2412.06795)
- ODIN و MorphIC: [ODIN arXiv 1804.07858](https://www.arxiv.org/pdf/1804.07858) · [MorphIC arXiv 1904.08513](https://arxiv.org/pdf/1904.08513)
- RescueSNN و SoftSNN: [arXiv 2304.04041](https://arxiv.org/pdf/2304.04041) · [arXiv 2203.05523](https://arxiv.org/pdf/2203.05523)
- Loihi 2 و SpiNNaker2: [مرور 2026](https://arxiv.org/pdf/2604.04727) · [Yan et al.](https://arxiv.org/pdf/2009.08921)
- پهپاد و FPGA: [Suh TRETS 2023](https://unpaywall.org/10.1145%2F3583074) · [YOLOv3-Tiny 2025](https://iris.univpm.it/retrieve/488c6f4b-75a6-4d1a-baf7-d6fd52290b4f/Cal%c3%ac_Optimized-Implementation-YOLOv3-Tiny_2025.pdf) · [Cittadini 2025](https://iris.sssup.it/retrieve/ffad627c-0615-4873-be25-c5ffddba8a74/1-s2.0-S0952197625001599-main.pdf) · [مرور 2025](https://arxiv.org/pdf/2509.04173)
- مرز مالکیت: [Hu et al. 2019 (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC6635809) · [Supèr et al. 2010](https://diposit.ub.edu/items/814e1300-8666-4d92-a356-3ba531803c63/full)
