"""Figures and numbers of the Phase 1 report from the Phase 1 campaigns (main, extra, extra_rl, bal, adapt, final).

    python tools/phase1_figures.py      # writes reports/phase1/figs/*.png and reports/phase1/numbers.json
"""

from __future__ import annotations

import glob
import json
import statistics as st
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["axes.unicode_minus"] = False
import matplotlib.pyplot as plt  # noqa: E402

import phase0_figures as p0  # noqa: E402  (same style, palette and helpers)

ROOT = Path(__file__).resolve().parents[1]
CAMPS = ROOT.parent / "work" / "campaigns"
OUT = ROOT / "reports" / "phase1" / "figs"


# tag -> (campaign, stage, group) of the 3-seed test runs (DECISIONS D27, D28)
FINALS = {
    "svm_eth_fixed": ("phase1_main", "final_svm", "s_pk_fixed"),
    "svm_eth": ("phase1_bal", "final_svm_bal", "*"),
    "rl_eth": ("phase1_main", "final_rl", "*"),
    "svm_eth_grey": ("phase1_bal", "controls_bal", "f_eth_grey46"),
    "svm_eth_grey_flip": ("phase1_main", "final_controls", "f_eth_grey"),
    "svm_cal": ("phase1_bal", "controls_bal", "f_cal_pkm"),
    "svm_cal_grey": ("phase1_bal", "controls_bal", "f_cal_grey46"),
    "rl_cal": ("phase1_bal", "controls_bal", "f_cal_rl_c1_bal"),
    "rl_cal_fixed": ("phase1_main", "final_controls", "f_cal_rl_c1"),
    "rl_cal_grey": ("phase1_main", "final_controls", "f_cal_rl_c1_grey"),
    "svm_eth_adapt": ("phase1_final", "final_svm_adapt", "*"),
    "rl_eth_adapt": ("phase1_final", "final_rl_adapt", "*"),
    "svm_cal_adapt": ("phase1_final", "controls_adapt", "f_cal_svm_adapt"),
    "rl_cal_adapt": ("phase1_final", "controls_adapt", "f_cal_rl_adapt"),
}
# validation screens: (campaign, stage)
SCREENS = [("phase1_main", "screen_svm"), ("phase1_main", "screen_rl"), ("phase1_extra", "screen_x"),
           ("phase1_extra_rl", "screen_x"), ("phase1_bal", "screen_rl_bal"), ("phase1_adapt", "screen_inv"),
           ("phase1_adapt2", "screen_inv"), ("phase1_v2", "screen"), ("phase1_v2b", "screen"), ("phase1_v2c", "screen"),
           ("phase1_mag", "screen")]


def runs(camp: str, stage: str, group: str = "*") -> list[dict]:
    return [json.loads(Path(m).read_text(encoding="utf-8"))
            for m in sorted(glob.glob(str(CAMPS / camp / stage / group / "s*/metrics.json")))]


def ms(v):
    return (st.mean(v), st.stdev(v) if len(v) > 1 else 0.0) if v else (None, 0.0)


def best_variant(d: dict) -> float:
    vs = d.get("variants") or {}
    return 100 * max([v["svm"] for v in vs.values()] or [d["test_acc"]])


def inv_of(r: list[dict]) -> dict | None:
    invs = [m.get("invariance_rstdp") or m.get("invariance_svm") for m in r]
    invs = [i for i in invs if i]
    return {k: ms([100 * i[k] for i in invs]) for k in invs[0]} if invs else None


def numbers() -> dict:
    n = {}
    for tag, (camp, stage, grp) in FINALS.items():
        r = runs(camp, stage, grp)
        n[tag] = ms([100 * m["test_acc"] for m in r])
        if r:
            n[tag + "_group"] = Path(glob.glob(str(CAMPS / camp / stage / grp))[0]).name
            n[tag + "_spikes"] = st.mean(m["spikes_per_image_input_plus_conv"] for m in r)
            n[tag + "_input_spikes"] = st.mean(m["spikes_per_image"]["input"] for m in r)
            n[tag + "_weights"] = r[0]["weights"]
            n[tag + "_seeds"] = [round(100 * m["test_acc"], 2) for m in r]
            if "rstdp_best_test_acc_optimistic" in r[0]:
                n[tag + "_best_epoch"] = ms([100 * m["rstdp_best_test_acc_optimistic"] for m in r])
                n[tag + "_silent"] = ms([100 * m.get("rstdp_test_silent", 0) for m in r])
        inv = inv_of(r)
        if inv:
            n[tag + "_invariance"] = inv
            for k, v in inv.items():
                n[f"{tag}_inv_{k.replace(' ', '_').replace('.', 'p')}"] = v
    n["screens"] = {}
    for camp, stage in SCREENS:
        for m in sorted(glob.glob(str(CAMPS / camp / stage / "*" / "s0/metrics.json"))):
            d = json.loads(Path(m).read_text(encoding="utf-8"))
            name = Path(m).parts[-3]
            n["screens"][name] = 100 * d["test_acc"]
            n["v_" + name] = (100 * d["test_acc"], 0.0)
            n["vb_" + name] = (best_variant(d), 0.0)
            n["c1_" + name] = (d["final_C_l"].get("conv1", float("nan")), 0.0)
            inv = inv_of([d])
            if inv:
                n[name + "_invariance"] = inv
                for k, v in inv.items():
                    n[f"{name}_inv_{k.replace(' ', '_').replace('.', 'p')}"] = v
    n.update(cost())
    return n


CONV = [(5, 12), (5, 32), (5, 64), (3, 128)]  # (kernel, maps) of S1..S4; input channels: retina, then previous maps


def cost() -> dict:
    """Event-driven synaptic operations (one addition each) vs the MACs of the same dense convolutional network, per
    image over the three pyramid levels (128, 64, 32), for the classifier-front networks of the finals."""
    out = {}
    for tag in ("svm_eth", "svm_eth_fixed", "svm_eth_adapt", "svm_cal"):
        r = runs(*FINALS[tag])
        if not r:
            continue
        sp = r[0]["spikes_per_image"]
        ov = " ".join(r[0].get("overrides", []))
        ch = 8 if "pkm" in ov else 2 if "grey" in ov else 6
        feeds = ["input", "1_pool", "3_pool", "5_pool"]
        sop = sum(sp[f] * k * k * m for f, (k, m) in zip(feeds, CONV))
        mac, cin = 0.0, ch
        for i, (k, m) in enumerate(CONV):
            for size in (128, 64, 32):
                mac += (size >> i) ** 2 * k * k * cin * m
            cin = m
        out.update({f"cost_{tag}_sop": sop / 1e6, f"cost_{tag}_mac": mac / 1e6, f"cost_{tag}_ratio": mac / sop})
    return out


NAMES = {
    "s_pk": "P+K، آستانهٔ ثابت هر کانال", "s_grey": "خاکستری", "s_p": "فقط P", "s_pkm": "P+K+M",
    "s_pk_rank": "P+K، کد ترتیب رتبه", "s_pk_float": "P+K، ممیز شناور و لگاریتم دقیق",
    "s_pk_1level": "P+K، بدون هرم", "s_pk_fixed": "P+K، آستانهٔ ثابت سراسری (پس‌زمینه)",
    "x_svm_slope": "آستانهٔ سراسری، ضریب هم‌شیب", "x_svm_s1long": "آستانهٔ سراسری، S1 با 8000 تکرار",
    "a_svm_base": "P+K+M، آستانهٔ ثابت هر کانال (با ناوردایی)", "a_svm_adapt": "P+K+M، تطبیق تضاد",
    "a_svm_adapt_rank": "P+K+M، تطبیق تضاد و کد رتبه",
    "r_c1_pk": "C1، P+K", "r_c1_pk_calcium": "C1، P+K، نرخ کلسیمی", "r_c1_grey": "C1، خاکستری",
    "r_c4_pk": "C4، P+K", "r_c1_pk_fixed": "C1، آستانهٔ سراسری", "r_c1_pk_fixed_calcium": "C1، آستانهٔ سراسری، کلسیمی",
    "r_c4_pk_fixed": "C4، آستانهٔ سراسری", "x_rl_c1_slope": "C1، آستانهٔ سراسری، ضریب هم‌شیب",
    "x_rl_c1p2_fixed": "C1 با پنجرهٔ 32، آستانهٔ سراسری", "x_rl_c1p2_fixed_calcium": "C1 با پنجرهٔ 32، آستانهٔ سراسری، کلسیمی",
    "x_rl_c1p2": "C1 با پنجرهٔ 32، P+K", "x_rl_c1p2_calcium": "C1 با پنجرهٔ 32، P+K، کلسیمی",
    "a_rl_base": "C1، کلسیمی، آستانهٔ ثابت هر کانال (با ناوردایی)", "a_rl_adapt": "C1، کلسیمی، تطبیق تضاد",
    "a_rl_adapt_rank": "C1، کلسیمی، تطبیق تضاد و کد رتبه",
    "a_rl_adapt_f2": "C1، کلسیمی، تطبیق تضاد با کف 2 اکتاو",
    "r2_lcn7": "C1، کلسیمی، نرمال‌سازی محلی تضاد", "r2_lcn5": "C1، کلسیمی، نرمال‌سازی محلی (κ=2^-5)",
    "r2_lcn7_flip150": "C1، نرمال‌سازی محلی، آینه‌سازی، 150 epoch", "m_eth_rl": "C1، کلسیمی، فقط magno",
    "s2_lcn7": "P+K+M، نرمال‌سازی محلی تضاد",
}
SVM_SCREENS = ["s_pk", "s_grey", "s_p", "s_pkm", "s_pk_rank", "s_pk_float", "s_pk_1level", "s_pk_fixed", "x_svm_slope",
               "x_svm_s1long", "a_svm_base", "a_svm_adapt", "a_svm_adapt_rank", "s2_lcn7", "m_eth_svm"]


def invariance_figure(n: dict, keys: list[tuple[str, str]], path: Path, title: str) -> None:
    keys = [(k, lab) for k, lab in keys if k + "_invariance" in n]
    if not keys:
        return
    groups = [("brightness", "ضریب روشنایی"), ("gamma", "گاما"), ("scale", "ضریب مقیاس"), ("shift", "جابه‌جایی (پیکسل)")]
    fig, axes = plt.subplots(1, 4, figsize=(15, 4.6), sharey=True)
    cols = (p0.BLUE, p0.ORANGE, p0.AQUA, "#6250d6", "#b04a8f", "#5a8f29")
    for ax, (g, gt) in zip(axes, groups):
        for (k, lab), col in zip(keys, cols):
            inv = n[k + "_invariance"]
            pts = [(float(name.split()[-1].replace("px", "").replace("x", "")), v[0])
                   for name, v in inv.items() if name.startswith(g)]
            pts = sorted(pts + [(0.0 if g == "shift" else 1.0, inv["none"][0])])
            ax.plot([x for x, _ in pts], [y for _, y in pts], "-o", color=col, lw=2, ms=5, label=lab)
        ax.set_title(gt, color=p0.INK)
        ax.yaxis.grid(True, color=p0.GRID)
        ax.set_axisbelow(True)
        ax.set_ylim(0, 100)
        if g in ("brightness", "gamma"):
            ax.set_xscale("log", base=2)
            xs = [0.25, 0.5, 1, 2, 4] if g == "brightness" else [0.5, 1, 2]
            ax.set_xticks(xs, [f"{x:g}" for x in xs])
            ax.minorticks_off()
    axes[0].set_ylabel("دقت (درصد)")
    fig.legend(*axes[0].get_legend_handles_labels(), frameon=False, fontsize=10, loc="lower center",
               ncol=min(3, len(keys)), bbox_to_anchor=(0.5, -0.02))
    fig.suptitle(title, color=p0.INK)
    fig.tight_layout(rect=(0, 0.08 + 0.05 * (len(keys) > 3), 1, 1))
    fig.savefig(path)
    plt.close(fig)


def retina_figure() -> None:
    """Spike-time maps of one ETH-80 image under the three contrast-threshold modes, and under gamma 0.5."""
    import sys

    import numpy as np
    import torch
    from PIL import Image
    sys.path.insert(0, str(ROOT))
    from biovision.engine.spikes import NO_SPIKE
    from biovision.eval.invariance import gamma
    from biovision.retina.hw_retina import calibrate_l_min, encode_bio3
    eth = CAMPS.parent / "proc" / "eth80" / "cropped256"
    path = eth / "tomato1" / "tomato1-022-090.png"
    if not path.exists():
        return

    def load(p):
        a = np.asarray(Image.open(p).convert("RGB").resize((128, 128)), dtype=np.float32)
        return torch.from_numpy(a).permute(2, 0, 1)
    sample = [load(p) / 255 for p in sorted(glob.glob(str(eth / "*" / "*-022-*.png")))[::12][:40]]
    lm = calibrate_l_min(sample, "pk", 0.07)
    img = load(path)
    rows = [("آستانهٔ ثابت سراسری", img, dict(l_min=-0.5, per_channel=False)),
            ("آستانهٔ ثابت هر کانال", img, dict(l_min=lm, per_channel=True)),
            ("تطبیق تضاد", img, dict(l_min="adaptive", per_channel=True)),
            ("آستانهٔ ثابت هر کانال، گامای 0.5", gamma(img, 0.5), dict(l_min=lm, per_channel=True)),
            ("تطبیق تضاد، گامای 0.5", gamma(img, 0.5), dict(l_min="adaptive", per_channel=True))]
    cols = [("L+M− ON", 0), ("L+M− OFF", 1), ("M+L− ON", 2), ("M+L− OFF", 3), ("K (S−Y) ON", 4), ("K (S−Y) OFF", 5)]
    fig, axes = plt.subplots(len(rows), len(cols) + 1, figsize=(2.1 * (len(cols) + 1), 2.25 * len(rows)))
    for r, (lab, im, kw) in enumerate(rows):
        code = encode_bio3(im / 255, 15, "pk", delta=0.25, **kw)[0]
        axes[r, 0].imshow((im / 255).permute(1, 2, 0).numpy())
        axes[r, 0].set_ylabel(lab, fontsize=9, color=p0.INK)
        for c, (title, ch) in enumerate(cols, start=1):
            t = code[ch].float()
            v = torch.where(t == NO_SPIKE, torch.full_like(t, float("nan")), 15 - t).numpy()
            axes[r, c].imshow(np.zeros_like(v), cmap="gray", vmin=0, vmax=1)
            axes[r, c].imshow(v, cmap="magma", vmin=0, vmax=15)
            axes[r, c].set_xlabel(f"{int((t != NO_SPIKE).sum())} اسپایک", fontsize=8, color=p0.INK2)
            if r == 0:
                axes[r, c].set_title(title, fontsize=9, color=p0.INK)
        for ax in axes[r]:
            ax.set_xticks([])
            ax.set_yticks([])
    fig.suptitle("زمان اولین اسپایک کانال‌های P و K در سه حالت آستانهٔ تضاد (روشن‌تر = زودتر؛ سیاه = بدون اسپایک)",
                 color=p0.INK)
    fig.tight_layout()
    fig.savefig(OUT / "retina_modes.png")
    plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    p0.OUT = OUT
    retina_figure()
    n = numbers()
    (OUT.parent / "numbers.json").write_text(json.dumps(n, indent=1, ensure_ascii=False), encoding="utf-8")
    sc = n["screens"]
    svm = {k: n["vb_" + k][0] for k in SVM_SCREENS if k in sc}
    rl = {k: v for k, v in sc.items() if k not in SVM_SCREENS and "_cal_" not in k}  # ETH-80 RL screens
    if svm:
        p0.hbars(OUT / "screen_svm.png", svm, NAMES, None, "", "جبههٔ طبقه‌بند: غربال ETH-80 روی validation", xlim=(60, 88))
    if rl:
        p0.hbars(OUT / "screen_rl.png", rl, NAMES, None, "", "جبههٔ RL: غربال ETH-80 روی validation", xlim=(40, 85))
    # channel comparison of the RL front on validation (same network): colour P+K, grey, magno only (event code)
    import csv
    runs_csv = {(r["group"]): r for r in csv.DictReader(open(ROOT / "results" / "all_runs.csv", encoding="utf-8"))}

    def val(name):
        r = runs_csv.get(name)
        return (float(r["acc"]), 0.0) if r and r["acc"] else (None, 0.0)
    series = [[val("r_c1_pk_calcium"), val("pk_cal_rl")], [val("r_c1_grey"), val("g_cal_rl")], [val("m_eth_rl"), val("m_cal_rl")]]
    if any(v[0] is not None for s_ in series for v in s_):
        fig, ax = plt.subplots(figsize=(9, 5))
        p0.bars(ax, ["ETH-80", "Caltech چهاردسته‌ای"], series, [p0.BLUE, p0.ORANGE, p0.AQUA],
                ["رنگی P+K", "خاکستری", "فقط magno"], (0, 105), "جبههٔ RL: کانال‌های شبکیه (validation، یک seed)")
        fig.tight_layout()
        fig.savefig(OUT / "channels_rl.png")
        plt.close(fig)
    invariance_figure(n, [("rl_eth", "RL، ETH-80"), ("svm_eth_fixed", "طبقه‌بند، ETH-80، آستانهٔ سراسری"),
                          ("svm_eth", "طبقه‌بند، ETH-80"), ("svm_cal", "طبقه‌بند، Caltech"), ("rl_cal", "RL، Caltech")],
                      OUT / "invariance_finals.png", "ناوردایی آزمون‌های نهایی با آستانه‌های ثابت (test، میانگین سه seed)")
    for front, lab in (("rl", "RL"), ("svm", "طبقه‌بند")):
        invariance_figure(n, [(f"a_{front}_base", "آستانهٔ ثابت هر کانال"), (f"a_{front}_adapt", "تطبیق تضاد"),
                              (f"a_{front}_adapt_f2", "تطبیق تضاد با کف 2 اکتاو"),
                              (f"a_{front}_adapt_rank", "تطبیق تضاد و کد رتبه")],
                          OUT / f"invariance_adapt_{front}.png", f"جبههٔ {lab}: اثر تطبیق تضاد بر ناوردایی (ETH-80، validation)")
    invariance_figure(n, [("a_rl_base", "آستانهٔ ثابت هر کانال"), ("a_rl_adapt_f2", "تطبیق تضاد سراسری با کف"),
                          ("r2_lcn7", "نرمال‌سازی محلی تضاد"), ("r2_lcn7_flip150", "نرمال‌سازی محلی، آینه‌سازی، 150 epoch")],
                      OUT / "invariance_lcn_rl.png", "جبههٔ RL: سه روش کنترل تضاد (ETH-80، validation)")
    invariance_figure(n, [("rl_eth_adapt", "RL، ETH-80"), ("svm_eth_adapt", "طبقه‌بند، ETH-80"),
                          ("rl_cal_adapt", "RL، Caltech"), ("svm_cal_adapt", "طبقه‌بند، Caltech")],
                      OUT / "invariance_adapt_finals.png", "ناوردایی معماری نهایی با تطبیق تضاد (test، سه seed)")
    print(json.dumps({k: v for k, v in n.items() if not k.endswith("_invariance") and "_inv_" not in k},
                     indent=0, ensure_ascii=False)[:4000])


if __name__ == "__main__":
    main()
