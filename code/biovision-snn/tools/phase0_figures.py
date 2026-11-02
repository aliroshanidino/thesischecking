"""Figures and numbers of the Phase 0 report, computed from the campaign results.

    python tools/phase0_figures.py            # writes reports/phase0/figs/*.png and reports/phase0/numbers.json

Static PNGs for a printed Word report (light mode). Colours: the first three categorical slots of the dataviz
reference palette (validated together: CVD dE 9.2, normal-vision dE 27.6; the aqua slot is below 3:1 contrast, so
every bar carries its value as a direct label). Matplotlib >= 3.11 shapes and orders Persian text itself (complex
text layout), so labels are passed as they are.
"""

from __future__ import annotations

import glob
import json
import statistics as st
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT.parent / "work"
CAMP = WORK / "campaigns"
OUT = ROOT / "reports" / "phase0" / "figs"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#ffffff"

for f in (Path.home() / "AppData/Local/Microsoft/Windows/Fonts/BNazanin.ttf",):
    if f.exists():
        font_manager.fontManager.addfont(str(f))
plt.rcParams.update({"font.family": ["B Nazanin", "Tahoma", "DejaVu Sans"], "font.size": 13,
                     "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": SURFACE,
                     "axes.facecolor": SURFACE, "savefig.dpi": 200})


def fa(text: str) -> str:
    return text


def metrics(pattern: str) -> list[dict]:
    return [json.loads(Path(m).read_text(encoding="utf-8")) for m in sorted(glob.glob(str(pattern)))]


def acc(ms: list[dict], variant: str | None = None, key: str = "test_acc") -> list[float]:
    out = []
    for m in ms:
        if variant:
            v = (m.get("variants") or {}).get(variant)
            if v:
                out.append(100 * v["svm"])
        elif m.get(key) is not None:
            out.append(100 * m[key])
    return out


def ms(v: list[float]) -> tuple[float | None, float]:
    if not v:
        return None, 0.0
    return st.mean(v), (st.stdev(v) if len(v) > 1 else 0.0)


def numbers() -> dict:
    n = {}
    # classifier front -------------------------------------------------------------------------------------------
    n["caltech_paper_settings"] = ms(acc(metrics(WORK / "runs/phase0/20261019-0216_caltech_3seeds/seed*/metrics.json")))
    n["caltech_ours"] = ms(acc(metrics(CAMP / "caltech_final/final/c5_conv1_8maps/s*/metrics.json")))
    mn = metrics(CAMP / "phase0_misc/mnist_final/mnist_g5/s*/metrics.json")
    n["mnist_paper_settings"], n["mnist_ours"] = ms(acc(mn, "g1_l2")), ms(acc(mn, "g5_l2"))
    eth = metrics(CAMP / "phase0_misc/replicate/eth80_sdnn_paper/s*/metrics.json")
    n["eth_sdnn_paper_settings"], n["eth_sdnn_paper_settings_our_readout"] = ms(acc(eth, "g1_l4")), ms(acc(eth, "g4_l2_std"))
    e16 = metrics(CAMP / "eth80_2016/replicate/s2_1250/s*/metrics.json")
    n["eth_2016_paper_settings"] = ms(acc(e16, "g1_l0_ovo"))
    n["eth_2016_our_readout"] = ms(acc(e16, "g3_l0_std"))
    fin = metrics(CAMP / "eth80_final/final55/*/s*/metrics.json")
    n["eth_classifier_ours"] = ms(acc(fin))
    # RL front -----------------------------------------------------------------------------------------------------
    for tag, pat in (("rl_eth55", "rl_main/eth_final55/*/s*/metrics.json"),
                     ("rl_eth_loo", "rl_main/eth_final_loo/*/s*_f*/metrics.json"),
                     ("rl_caltech", "rl_main/caltech_final/*/s*/metrics.json"),
                     ("rl_caltech_paper", "rl_main/replicate_mozafari/caltech_mozafari_paper/s*/metrics.json")):
        m = metrics(CAMP / pat)
        n[tag + "_selected"] = ms(acc(m))
        n[tag + "_final"] = ms(acc(m, key="rstdp_final_test_acc"))
        n[tag + "_best_epoch"] = ms(acc(m, key="rstdp_best_test_acc_optimistic"))
        n[tag + "_runs"] = len(m)
    return n


def screen(pattern: str, best_variant: bool) -> dict[str, float]:
    out = {}
    for m in sorted(glob.glob(str(CAMP / pattern))):
        name = Path(m).parts[-3]
        d = json.loads(Path(m).read_text(encoding="utf-8"))
        v = d.get("variants") or {}
        out[name] = 100 * (max(x["svm"] for x in v.values()) if best_variant and v else d["test_acc"])
    return out


def bars(ax, groups, series, colors, labels, ylim, title):
    """Grouped vertical bars with value labels (direct labels relieve the low-contrast slot)."""
    w = 0.8 / len(series)
    for i, (vals, col, lab) in enumerate(zip(series, colors, labels)):
        for g, (mean, sd) in enumerate(vals):
            if mean is None:
                continue
            x = g + (i - (len(series) - 1) / 2) * w
            ax.bar(x, mean, w * 0.9, color=col, yerr=sd if sd else None, capsize=3, ecolor=INK2,
                   label=fa(lab) if g == 0 or not any(v[0] is not None for v in vals[:g]) else None, zorder=2)
            ax.text(x, mean + (sd or 0) + 0.6, f"{mean:.1f}", ha="center", va="bottom", fontsize=10, color=INK)
    ax.set_xticks(range(len(groups)), [fa(g) for g in groups])
    ax.set_ylim(*ylim)
    ax.set_ylabel(fa("دقت آزمون (درصد)"))
    ax.yaxis.grid(True, color=GRID, zorder=0)
    ax.set_axisbelow(True)
    ax.set_title(fa(title), color=INK)
    handles, labs = ax.get_legend_handles_labels()
    uniq = dict(zip(labs, handles))
    ax.legend(uniq.values(), uniq.keys(), frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.12),
              ncol=len(uniq), fontsize=11)


def hbars(path, data: dict[str, float], names: dict[str, str], ref: float | None, ref_label: str, title: str,
          xlim=(0, 100)):
    items = sorted(((v, names.get(k, k)) for k, v in data.items()), reverse=True)
    fig, ax = plt.subplots(figsize=(8, 0.45 * len(items) + 1.4))
    y = range(len(items))
    ax.barh(list(y), [v for v, _ in items], 0.6, color=BLUE, zorder=2)
    for i, (v, _) in enumerate(items):
        ax.text(v + 0.4, i, f"{v:.1f}", va="center", fontsize=10, color=INK)
    ax.set_yticks(list(y), [fa(n) for _, n in items])
    ax.invert_yaxis()
    if ref is not None:
        ax.axvline(ref, color=ORANGE, lw=2, ls="--", zorder=3)
        ax.text(ref, -0.8, fa(ref_label), color=INK2, ha="center", fontsize=10)
    ax.set_xlim(*xlim)
    ax.set_xlabel(fa("دقت validation (درصد)"))
    ax.xaxis.grid(True, color=GRID, zorder=0)
    ax.set_axisbelow(True)
    ax.set_title(fa(title), color=INK, pad=18)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    n = numbers()
    (OUT.parent / "numbers.json").write_text(json.dumps(n, indent=1, ensure_ascii=False), encoding="utf-8")

    # F1: classifier front ---------------------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 5))
    bars(ax, ["Caltech", "ETH-80 (۵/۵)", "MNIST"],
         [[(99.1, 0.2), (82.8, 0), (98.4, 0)],
          [n["caltech_paper_settings"], n["eth_sdnn_paper_settings"], n["mnist_paper_settings"]],
          [n["caltech_ours"], n["eth_classifier_ours"], n["mnist_ours"]]],
         [BLUE, ORANGE, AQUA], ["مقالهٔ SDNN", "بازتولید با تنظیمات مقاله", "روش بهبودیافتهٔ ما"], (0, 110),
         "جبههٔ طبقه‌بند: مقاله، بازتولید و روش ما")
    fig.tight_layout()
    fig.savefig(OUT / "classifier_compare.png")
    plt.close(fig)

    # F2: RL front -----------------------------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 5))
    bars(ax, ["Caltech", "ETH-80 (۵/۵)", "ETH-80 (leave-one-out)"],
         [[(98.9, 0.4), (None, 0), (89.5, 1.9)],
          [n["rl_caltech_selected"], n["rl_eth55_selected"], n["rl_eth_loo_selected"]],
          [n["rl_caltech_best_epoch"], n["rl_eth55_best_epoch"], n["rl_eth_loo_best_epoch"]]],
         [BLUE, ORANGE, AQUA],
         ["مقالهٔ Mozafari (بهترین epoch)", "ما: epoch انتخاب‌شده با دقت آموزش", "ما: بهترین epoch آزمون"], (0, 110),
         "جبههٔ یادگیری تقویتی (R-STDP، بدون طبقه‌بند بیرونی)")
    fig.tight_layout()
    fig.savefig(OUT / "rl_compare.png")
    plt.close(fig)

    # F3: RL rules on ETH-80 validation --------------------------------------------------------------------------
    names = {"m0_paper": "تنظیمات مقاله", "m1_calcium": "نرخ کلسیمی", "m2_calcium_teacher": "کلسیم + معلم",
             "m3_calcium_margin": "کلسیم + حاشیه", "m4_mpc20": "۲۰ نقشه برای هر دسته", "m5_rsdsp": "R-SDSP",
             "m6_rsdsp_k03": "R-SDSP با κ = 0.3", "m7_hw": "حالت بی‌ضرب (shift و add)",
             "f1_conv2_dense": "R-STDP روی conv2 پرتراکم"}
    sc = screen("rl_main/eth_screen/*/s0/metrics.json", False)
    hbars(OUT / "rl_rules_eth.png", sc, names, sc.get("m0_paper"), "مقاله", "قاعده‌های تصمیم RL روی ETH-80")
    sc = screen("rl_main/caltech_screen/*/s0/metrics.json", False)
    names_c = {"cm0_paper": "تنظیمات مقاله", "cm1_calcium": "نرخ کلسیمی", "cm2_calcium_teacher": "کلسیم + معلم",
               "cm5_rsdsp": "R-SDSP", "cm7_hw": "حالت بی‌ضرب (shift و add)"}
    if sc:
        hbars(OUT / "rl_rules_caltech.png", sc, names_c, sc.get("cm0_paper"), "مقاله",
              "قاعده‌های تصمیم RL روی Caltech", xlim=(50, 102))

    # F4: attention ----------------------------------------------------------------------------------------------
    at = screen("rl_attention/*/*/s0/metrics.json", False)
    fig, ax = plt.subplots(figsize=(8, 4.6))
    bars(ax, ["ETH-80", "Caltech"],
         [[(at.get("a0h_control"), 0), (at.get("ca2h_control_k7_th10"), 0)],
          [(at.get("a1_rpe"), 0), (at.get("ca2_rpe_k7_th10"), 0)]],
         [ORANGE, AQUA], ["کنترل: لایهٔ پنهان منجمد", "یادگیری با توجه (AGREL)"], (0, 105),
         "اثر قاعدهٔ توجه بر شبکهٔ دولایه (validation)")
    ax.set_ylabel(fa("دقت validation (درصد)"))
    fig.tight_layout()
    fig.savefig(OUT / "attention.png")
    plt.close(fig)

    # F5: classifier screens on ETH-80 ---------------------------------------------------------------------------
    names_e = {"e0_ref": "مرجع (DoG، هموستازی)", "e1_maps800": "۸۰۰ نقشه", "e2_hasizh": "H-ASIZH با θ0 = 60",
               "e3_hasizh_brake": "H-ASIZH + ترمز با θ0 = 60", "e4_sdsp": "SDSP کلسیمی", "e5_sdsp_k03": "SDSP با κ = 0.3",
               "e6_size300": "تصویر ۳۰۰ پیکسلی", "s1_on_off": "DoG مرکز-روشن و مرکز-تاریک",
               "s2_scales3": "ورودی سه‌مقیاسی", "s3_maps1200": "۱۲۰۰ نقشه", "s4_on_off_scales3": "ON/OFF + سه‌مقیاسی",
               "h1_hasizh": "H-ASIZH با θ0 = 40", "h2_hasizh_brake": "H-ASIZH + ترمز با θ0 = 40",
               "h3_hasizh_sdsp": "H-ASIZH + SDSP", "h4_calcium_homeo": "هموستازی کلسیمی"}
    sc = {}
    for camp in ("eth80_main", "eth80_screen2", "eth80_screen3"):
        sc |= screen(f"{camp}/screen/*/s0/metrics.json", True)
    hbars(OUT / "eth_classifier_screen.png", sc, names_e, None, "", "جبههٔ طبقه‌بند روی ETH-80: بهترین خوانش هر پیکربندی",
          xlim=(70, 90))

    # F6: leave-one-out folds ------------------------------------------------------------------------------------
    loo = sorted(glob.glob(str(CAMP / "rl_main/eth_final_loo/*/s0_f*/metrics.json")),
                 key=lambda p: int(Path(p).parent.name.split("_f")[1]))
    if loo:
        d = [json.loads(Path(p).read_text(encoding="utf-8")) for p in loo]
        folds = [int(Path(p).parent.name.split("_f")[1]) for p in loo]
        fig, ax = plt.subplots(figsize=(9, 4.6))
        w = 0.38
        ax.bar([f - w / 2 for f in folds], [100 * m["test_acc"] for m in d], w, color=ORANGE,
               label=fa("epoch انتخاب‌شده با دقت آموزش"), zorder=2)
        ax.bar([f + w / 2 for f in folds], [100 * m["rstdp_best_test_acc_optimistic"] for m in d], w, color=AQUA,
               label=fa("بهترین epoch آزمون"), zorder=2)
        ax.axhspan(89.5 - 1.9, 89.5 + 1.9, color=BLUE, alpha=0.15, zorder=1)
        ax.axhline(89.5, color=BLUE, lw=2, zorder=3, label=fa("Mozafari: 89.5 ± 1.9"))
        ax.set_xticks(folds, [str(f) for f in folds])
        ax.set_xlabel(fa("دور leave-one-out (شیء آزمون)"))
        ax.set_ylabel(fa("دقت آزمون (درصد)"))
        ax.set_ylim(50, 100)
        ax.yaxis.grid(True, color=GRID, zorder=0)
        ax.set_axisbelow(True)
        ax.legend(frameon=False, loc="lower right", fontsize=11)
        ax.set_title(fa("ETH-80 با پروتکل Mozafari: دقت هر دور"), color=INK)
        fig.tight_layout()
        fig.savefig(OUT / "rl_loo_folds.png")
        plt.close(fig)
    arch_figures()
    print(json.dumps(n, indent=1, ensure_ascii=False))



def arch_diagram(path: Path, title: str, blocks: list[tuple[str, str, str]]) -> None:
    """Top-to-bottom block diagram (readable at page width); each block = (title, detail, colour)."""
    from matplotlib.patches import FancyBboxPatch
    n = len(blocks)
    fig, ax = plt.subplots(figsize=(7.2, 1.15 * n + 0.6))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, n)
    ax.axis("off")
    for i, (head, detail, col) in enumerate(blocks):
        y = n - 1 - i
        for fc, alpha in ((col, 0.16), ("none", 1.0)):
            ax.add_patch(FancyBboxPatch((0.04, y + 0.12), 0.92, 0.72, boxstyle="round,pad=0.01,rounding_size=0.04",
                                        fc=fc, ec=col if fc == "none" else INK2, lw=2 if fc == "none" else 0,
                                        alpha=alpha))
        ax.text(0.93, y + 0.48, head, ha="right", va="center", fontsize=13, color=INK, weight="bold")
        ax.text(0.07, y + 0.48, detail.replace(chr(10), "  ·  "), ha="left", va="center", fontsize=11, color=INK2)
        if i < n - 1:
            ax.annotate("", xy=(0.5, y + 0.02), xytext=(0.5, y + 0.12),
                        arrowprops=dict(arrowstyle="-|>", color=INK2, lw=1.6))
    ax.set_title(title, color=INK, fontsize=14)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def arch_figures() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    arch_diagram(OUT / "arch_rl.png", "معماری A: یادگیری تقویتی با اولین اسپایک (اصلی، سخت‌افزارپذیر)", [
        ("تصویر خاکستری", "Caltech: ضریب 0.5\nETH-80: 128×128", BLUE),
        ("S1: Gabor ثابت", "4 جهت، 5×5\nقدر مطلق پاسخ", BLUE),
        ("C1: بیشینهٔ محلی", "7×7 گام 6 (Caltech)\n5×5 گام 4 (ETH-80)\nبازداری جانبی شدت", BLUE),
        ("کد TTFS", "ترتیب رتبه، T = 15\nیک جهت در هر مکان", BLUE),
        ("S2: تصمیم R-STDP", "10 نقشه برای هر دسته\nIF، آستانه 42 / 160\nپنجره 17 / 31", ORANGE),
        ("خروجی", "دستهٔ اولین اسپایک\nبدون طبقه‌بند", AQUA),
    ])
    arch_diagram(OUT / "arch_svm.png", "معماری B: ویژگی‌های STDP با سنجهٔ SVM (فرعی)", [
        ("تصویر خاکستری", "ETH-80: 200×200\nCaltech: ارتفاع 160", BLUE),
        ("DoG ثابت", "7×7، σ = 1 و 2\nآستانه 15 / 25", BLUE),
        ("conv1: STDP", "4 / 8 نقشهٔ 5×5\nآستانه 10", ORANGE),
        ("pool1", "7×7 گام 6", BLUE),
        ("conv2: STDP", "800 / 20 نقشهٔ 16×16\nآستانهٔ H-ASIZH\nیا هموستازی", ORANGE),
        ("خوانش", "پتانسیل نهایی\nشبکهٔ 4×4 / 3×3\nSVM خطی", AQUA),
    ])


if __name__ == "__main__":
    main()
