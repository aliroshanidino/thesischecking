# مرور قاعده‌های یادگیری زیستی برای BioVision-SNN

> نوشته‌شده در 2026-10-19 به درخواست کاربر. معیار انتخاب سه چیز است: واقعاً زیستی باشد (محلی، بدون پس‌انتشار خطا)، با کدگذاری TTFS (یک اسپایک برای هر نورون در هر موج) سازگار باشد، و روی تراشه فقط با shift، add و مقایسه پیاده شود (تصمیم D22).

## ۱. جدول مقایسه

| قاعده | پایهٔ زیستی | عامل سوم (پاداش یا آموزش) | سازگاری با TTFS | هزینهٔ سخت‌افزاری | وضعیت در پروژه |
|---|---|---|---|---|---|
| STDP مسطح (Kheradpisheh 2018) | ترتیب اسپایک پیش و پس | ندارد | کامل؛ برای همین طراحی شده | ضریب ‏$w(1-w)$؛ در حالت بی‌ضرب ‏$\tfrac12\min(w,1-w)$ | پیاده و پایهٔ همهٔ لایه‌های ویژگی |
| STDP نمایی (Bi و Poo) | پنجرهٔ زمانی ‏$e^{-\Delta t/\tau}$ | ندارد | نیمه؛ فاصلهٔ زمانی در موج فشرده تقریباً بی‌معناست | جدول ثابت (LUT) برای ‏$\Delta t$ صحیح | در سند طرح برای حرکت (فاز ۳) |
| R-STDP (Florian 2007؛ Mozafari 2018) | دوپامین تعدیل‌کنندهٔ STDP | پاداش و تنبیه سراسری | کامل (Mozafari) | مثل STDP؛ نرخ‌های توان دو | پیاده؛ **جبههٔ اصلی** |
| R-STDP با ردِ شایستگی (Izhikevich 2007) | ردِ سیناپسی که دوپامین دیررس آن را تثبیت می‌کند | پاداش با تأخیر | در تصویر ثابت با پاداش فوری همان R-STDP است | یک شمارندهٔ نزولی برای هر سیناپس | برای ویدیو و حرکت (فاز ۳) |
| SDSP (Brader, Senn, Fusi 2007) | پرش وزن در اسپایک پیش، بسته به پتانسیل و کلسیم پس‌سیناپسی | جریان معلم | با بازنویسی ما کامل | مقایسه با آستانه‌ها؛ بی‌ضرب | پیاده (D20) |
| R-SDSP (پیشنهاد سند طرح) | SDSP با علامت پاداش | پاداش و تنبیه | کامل | بی‌ضرب | پیاده (D23)؛ در حال آزمون |
| قاعدهٔ کلسیمی Graupner و Brunel (2012) | کلسیم سیناپسی و دو آستانهٔ ‏$\theta_p$ و ‏$\theta_d$ | ندارد | با بازنویسی؛ هم‌ارز STDP با پنجرهٔ زمانی محدود | جدول ثابت و مقایسه | نامزد آزمون |
| BCM | آستانهٔ لغزان وابسته به فعالیت میانگین | ندارد | با بازنویسی (کلسیم = احتمال اسپایک) | ضرب در ‏$(1-C)$؛ با کلسیم کوانتیده بی‌ضرب | نزدیک به ترمز H-ASIZH ما |
| هموستازی آستانه و H-ASIZH (Roshani و همکاران) | کلسیم درون‌سلولی و آستانهٔ متغیر | ندارد | کامل | ‏$\alpha=2^{-6}$: shift و add | پیاده (D21) |
| Tempotron و ReSuMe | ردِ شایستگی و سیگنال آموزش | برچسب | کامل (تصمیم با اسپایک یا سکوت) | مثل STDP | گزینهٔ «معلم» ما (D20) |
| AGREL، Q-AGREL و BrainProp (Roelfsema 2005؛ Pozzi 2020) | پاداش سراسری + بازخورد توجه از واحد انتخاب‌شده به لایه‌های پایین | پاداش و توجه | نیمه؛ نیاز به مسیر بازخورد | ضرب در وزن بازخورد؛ با وزن دودویی بی‌ضرب | **نامزد مهم** برای یادگیری تقویتی لایه‌های عمیق |
| BTSP (Bittner 2017) | پتانسیل plateau و پنجرهٔ چندثانیه‌ای، یادگیری یک‌باره | ورودی آموزنده | برای حافظهٔ اپیزودی، نه دسته‌بندی | ساده | برای حافظهٔ کاری (فاز ۴) |
| e-prop (Bellec 2020) | ردِ شایستگی × سیگنال یادگیری | خطای پخش‌شده | برای شبکهٔ بازگشتی | ضرب | خارج از معیار |
| پس‌انتشار زمانی (S4NN، BS4NN، STiDi-BP) | زیستی نیست | گرادیان خطا | کامل | ضرب و تقسیم | فقط برای مقایسه؛ خارج از معیار |

## ۲. نتیجه‌گیری برای پروژه

- **قاعدهٔ یادگیری ویژگی‌ها:** STDP مسطح با هموستازی همچنان بهترین نتیجه را داده است. SDSP و H-ASIZH در حال آزمون‌اند. در این آزمون‌ها H-ASIZH با ‏$\theta_0$ پایین‌تر تنظیم شده، چون آستانه‌ای که هرگز پایین نمی‌آید نقشه‌های خاموش را زنده نمی‌کند.
- **لایهٔ تصمیم (جبههٔ اصلی):** چهار نامزد در کمپین `rl_main` مقایسه می‌شوند:
  - R-STDP با نرخ تطبیقی و dropout؛
  - R-STDP با نرخ کلسیمی نورون‌به‌نورون؛
  - R-STDP با سیگنال معلم (شبیه ReSuMe)؛
  - R-SDSP با توقف یادگیری کلسیمی.
- **ردِ شایستگی (Izhikevich و Florian):** در دسته‌بندی تصویر ثابت با پاداش فوری چیزی اضافه نمی‌کند، چون ردِ شایستگی همان STDP همین تصویر است. جای آن در فاز ۳ است، وقتی پاداش با تأخیر می‌آید.
- **قدم بعدی پیشنهادی:** یادگیری تقویتی لایه‌های عمیق با بازخورد توجه (AGREL و BrainProp). Mozafari 2019 نشان داده است که R-STDP در لایه‌های بالاتر ویژگی‌هایی یاد می‌گیرد که برای تکلیف تشخیصی‌اند، و روی MNIST بدون طبقه‌بند بیرونی به 97.2% رسیده است. BrainProp نشان داده است که یادگیری تقویتی با بازخورد توجه می‌تواند به دقت پس‌انتشار برسد.

## ۳. منابع

- Florian (2007), *Reinforcement Learning Through Modulation of Spike-Timing-Dependent Synaptic Plasticity*, Neural Computation.
- Izhikevich (2007), *Solving the distal reward problem through linkage of STDP and dopamine signaling*, Cerebral Cortex.
- Brader, Senn, Fusi (2007), *Learning real-world stimuli in a neural network with spike-driven synaptic dynamics*, Neural Computation.
- Graupner, Brunel (2012), *Calcium-based plasticity model explains sensitivity of synaptic changes to spike pattern, rate, and dendritic location*, PNAS.
- Roelfsema, van Ooyen (2005), *Attention-Gated Reinforcement Learning of Internal Representations for Classification*, Neural Computation.
- Pozzi, Bohté, Roelfsema (2020), *Attention-Gated Brain Propagation*.
- Mozafari et al. (2018), *First-Spike-Based Visual Categorization Using Reward-Modulated STDP*, IEEE TNNLS.
- Mozafari et al. (2019), *Bio-inspired digit recognition using reward-modulated STDP in deep convolutional networks*, Pattern Recognition.
- Bittner et al. (2017), *Behavioral time scale synaptic plasticity underlies CA1 place fields*, Science.
- Gütig, Sompolinsky (2006), *The tempotron*, Nature Neuroscience.
- Khacef et al. (2022), *Spike-based local synaptic plasticity: a survey of computational models and neuromorphic circuits*, Neuromorphic Computing and Engineering.
- Quintana et al. (2022), *Bio-plausible digital implementation of a reward modulated STDP synapse*, Neural Computing and Applications.
- Roshani, Ansari, Manzuri Shalmani (2026), *H-ASIZH*, submitted to IEEE TCAS-I.
