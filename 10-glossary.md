# 10 — واژه‌نامه (انگلیسی ↔ فارسی ↔ معنا در این پژوهش)

| اصطلاح | معادل فارسی (طبق نسخهٔ FA فصل ۱ در صورت وجود) | معنا / کاربرد |
|---|---|---|
| H-ASIZH | — | Homeostatic Affine Scaled Izhikevich (مقاله) / Homeostatic-Adaptive Spiking Izhikevich Hardware (اسلاید) |
| GLFI | تزریق خطای سطح گیت | Gate-Level Fault Injection؛ چارچوب پنج‌مرحله‌ای؛ نسل اول ابزار پیش از GateScan |
| GateScan (Mark I/II/III) | — | جانشین GLFI؛ بازهٔ تضمین‌شدهٔ آسیب‌پذیری |
| FAASS | — | سرویس آنلاین (faass.viracoai.net) = GateScan Mark II |
| Digital seizure | تشنج دیجیتال | شلیک پایدار ناشی از SA1 که فابریک اسپایک را اشباع و باتری ایمپلنت را خالی می‌کند |
| Stuck-at (SA0/SA1) | گیر در صفر/یک | مدل کلاسیک خطای دائمی گره |
| Fault accommodation vs. masking | سازگاری با خطا در برابر پوشاندن | تنظیم مجدد set-point کند در برابر پنهان‌سازی با تکثیر |
| Homeostasis / homeostatic plasticity | هموستاز / شکل‌پذیری هموستاتیک | پایدارسازی شلیک با بازخورد |
| Adaptive threshold θ | آستانهٔ تطبیقی | متغیر حالت سوم و کند نورون |
| α leak / γ penalty / β brake | نشت / جریمه / ترمز | 2⁻⁶ / 2⁻³ / 2³ |
| Fast-bleed valve | شیر تخلیهٔ سریع | برگرداندن U نیمه‌راه به استراحت در یک سیکل |
| Clamping network (anti-windup) | شبکهٔ گیره | جلوگیری از wrap-around در Q7.19 |
| Restoring organ | اندام بازیاب | ساختار von Neumann: سه‌تایی کردن خود voterها |
| Light TMR | TMR سبک | سه‌تایی کردن فقط منطق تصمیم و THETA-REG |
| UUB | کران‌داری نهایی یکنواخت | Uniformly Ultimately Bounded |
| Lie derivative | مشتق لی | مشتق تابع لیاپانوف در امتداد مسیر |
| Averaging theorem (hybrid) | قضیهٔ میانگین‌گیری | نگاشت قطار Dirac به نرخ r(t) |
| Homeostatic attractor | جاذب هموستاتیک | چرخهٔ حدی سه‌بعدی کران‌دار (V,U,θ) |
| Affine map | نگاشت آفین | V_hw = (v+65)/64 |
| Q7.19 | — | ۲۶ بیت علامت‌دار: 1 علامت + 6 صحیح + 19 کسری |
| PWL estimator | تخمین‌گر خطی تکه‌ای | جایگزین 2.56V² با چهار قطعهٔ توان دو |
| Logic Shadow Hook / saboteur weaving | قلاب سایه / بافتن خرابکار | درج MUX کنترل‌پذیر در netlist |
| Semantic zoning | ناحیه‌بندی معنایی | STATE_MEMORY / CONTROL_PLANE / DATAPATH / COMB_CLOUD |
| FRE / CV | خطای نرخ شلیک / ضریب تغییرات ISI | معیارهای نورومتریک (≤ 20٪، ≤ 0.20) |
| Masked / Tolerant / Critical / Fatal | پوشیده / قابل‌تحمل / بحرانی / مرگبار | چهار پیامد خطا |
| AVF | ضریب آسیب‌پذیری معماری | (Critical + Fatal)/Total |
| RFoM | شاخص قابلیت اطمینان | (AVF_base/AVF_i)/(N_i/N_base) |
| SWaP-C | — | Size, Weight, Power and Cost |
| TTFS | زمان تا نخستین اسپایک | کدگذاری زمانی ورودی |
| k-WTA (first-K) | برنده‌ها همه‌چیز را می‌برند | رقابت جانبی، K = 3 |
| STDP / R-STDP / SDSP | — | قواعد یادگیری اسپایکی (spike-timing / reward-modulated / spike-driven synaptic plasticity) |
| Teacher annealing | — | کاهش تدریجی سیگنال معلم در قاعدهٔ delta |
| Time multiplexing | چندتایی‌سازی زمانی | یک هستهٔ فیزیکی برای نورون‌های مجازی زیاد |
| Edge-to-cloud continuum | پیوستار لبه تا ابر | — |
| Extreme edge | لبهٔ دور | حسگر، پوشیدنی، ایمپلنت |
| Cloudlet / Fog / MEC | کلادلت / مه / محاسبات لبهٔ چنددسترسی | — |
| Offloading / partitioning / split learning / federated | برون‌سپاری / تقسیم / یادگیری تقسیم‌شده / فدرال | — |
| Smashed data | دادهٔ خردشده | فعال‌سازی‌های میانی در split learning |
| Dark silicon | سیلیکون تاریک | بخش خاموش تراشه پس از پایان Dennard |
| Dataflow (row-stationary) | جریان داده | تصمیم مرکزی طراحی شتاب‌دهنده |
| DVS / event camera | حسگر بینایی دینامیک / دوربین رویدادی | 120 dB، 15 µs |
| Mercurial cores / SDC | هسته‌های دمدمی / خرابی خاموش داده | — |
| Dependability (Avizienis) | قابلیت اتکا | fault → error → failure |
| ego-only system | سیستم خودبسنده | همهٔ عملیات خودران روی یک خودرو |
| Certified bracket / ESC | بازهٔ گواهی‌شده / فرار | مفاهیم GateScan |
