"""Phase 0: Kheradpisheh et al. 2018 SDNN with our modules (CLAUDE.md Section 8, Phase 0).

    python -m biovision.experiments.phase0 --config configs/phase0_caltech.yaml --seed 0 [--limit 40]

Writes into ``$RUN_DIR`` (or ``work/runs/adhoc/<name>``): config.yaml, metrics.json, convergence.csv, figs/.
"""

from __future__ import annotations

import argparse
import inspect
import math
import json
import os
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
import yaml

from ..config import config_hash, load_config
from ..data import caltech, eth80, mnist
from ..engine.device import describe, resolve_device, set_deterministic
from ..engine.sdnn import SDNN, ConvLayer
from ..engine.spikes import NO_SPIKE
from ..eval.probes import select_C, svm_probe
from ..eval.visualize import confusion_plot, convergence_plot, feature_grid, reconstruct_features
from ..paths import Paths
from ..retina.dog import sdnn_dog_input, sdnn_dog_kernel
from ..retina.latency import rank_order

LOADERS = {"caltech": (caltech, "proc/caltech101"), "eth80": (eth80, "proc/eth80/cropped256"), "mnist": (mnist, "raw:mnist")}


def views(x) -> list:
    """The spike-time maps of one image: a list (multi-scale input) or a single tensor."""
    return x if isinstance(x, list) else [x]


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def split_validation(tr_x, tr_y, fraction: float, seed: int):
    """Stratified hold-out of ``fraction`` of the training images (hyper-parameter search, D17)."""
    rng = np.random.default_rng(seed + 1000)
    y = np.asarray(tr_y)
    val = np.zeros(len(y), dtype=bool)
    for c in np.unique(y):
        idx = np.flatnonzero(y == c)
        val[rng.choice(idx, int(round(fraction * len(idx))), replace=False)] = True
    keep = lambda m: ([tr_x[i] for i in np.flatnonzero(m)], [int(y[i]) for i in np.flatnonzero(m)])  # noqa: E731
    return (*keep(~val), *keep(val))


def load_data(cfg: dict, paths: Paths, seed: int, limit: int | None):
    """Train / evaluation data and the groups of the training images (object instances for ETH-80, else None).
    With ``validation`` in the config the evaluation set is a held-out part of the TRAINING data (by object
    instance for ETH-80) and the real test set is never loaded or scored."""
    module, where = LOADERS[cfg["dataset"]]
    root = paths.raw / where[4:] if where.startswith("raw:") else paths.work / where
    kw = dict(cfg.get("data", {}))
    variant = kw.pop("variant", None)  # ETH-80 image set: cropped256 (default) or cropped-close128
    if variant:
        root = paths.work / "proc" / "eth80" / variant
    val = cfg.get("validation")
    groups = None
    if cfg["dataset"] == "mnist":
        tr_x, tr_y, te_x, te_y = module.load(root, seed, train_limit=limit)
        tr_x = list(tr_x)
        if val:
            return (*split_validation(tr_x, tr_y, val["fraction"], seed), None)
        if limit:
            te_x, te_y = te_x[: limit // 2], te_y[: limit // 2]
        return tr_x, tr_y, list(te_x), te_y, None
    if cfg["dataset"] == "eth80":
        if val:
            kw["val_instances"] = val["instances"]
        tr_x, tr_y, te_x, te_y, groups = module.load(root, seed, with_groups=True, **kw)
    else:  # keys inherited from an ETH-80 base config (train_instances, size) are not this loader's
        accepted = inspect.signature(module.load).parameters
        tr_x, tr_y, te_x, te_y = module.load(root, seed, **{k: v for k, v in kw.items() if k in accepted})
        if val:
            tr_x, tr_y, te_x, te_y = split_validation(tr_x, tr_y, val["fraction"], seed)
    if limit:  # smoke run: a few images per class
        def take(y, n):
            keep, seen = [], {}
            for i, lab in enumerate(y):
                if seen.get(lab, 0) < n:
                    keep.append(i)
                    seen[lab] = seen.get(lab, 0) + 1
            return keep
        n_cls = len(set(tr_y))
        k_tr, k_te = take(tr_y, max(2, limit // n_cls)), take(te_y, max(2, limit // (2 * n_cls)))
        groups = [groups[i] for i in k_tr] if groups is not None else None
        tr_x, tr_y = [tr_x[i] for i in k_tr], [tr_y[i] for i in k_tr]
        te_x, te_y = [te_x[i] for i in k_te], [te_y[i] for i in k_te]
    return tr_x, tr_y, te_x, te_y, groups


def knn_probe(train_x, train_y, test_x, test_y, k: int) -> float:
    from sklearn.neighbors import KNeighborsClassifier
    clf = KNeighborsClassifier(n_neighbors=k).fit(train_x, train_y)
    return float((clf.predict(test_x) == np.asarray(test_y)).mean())


def rstdp_readout(cfg, model, tr_in, tr_y, te_in, te_y, gen, device, log, encode=None, te_raw=None, tr_raw=None):
    """Mozafari et al. 2018 readout on top of the STDP-trained layers: class-assigned maps, first-spike decision,
    R-STDP with adaptive rates and dropout. Reports the final epoch, the epoch with the best TRAIN accuracy
    (honest model selection) and, separately, the best test epoch (how the paper reports; optimistic)."""
    from sklearn.metrics import confusion_matrix
    from ..learning.rstdp import RSTDPRates
    from ..ventral.rstdp_global import RSTDPReadout

    rs = cfg["rstdp"]
    inp = rs.get("input") or {}
    if inp:  # denser spike code of the last STDP layer for the decision layer: lower threshold and/or no WTA
        last = model.layers[model.conv_ids[-1]]
        last.threshold = torch.as_tensor(last.threshold, dtype=torch.float32, device=device) * inp.get("threshold_scale", 1.0)
        last.wta = inp.get("wta", True)
    view = rs.get("view", 0)  # multi-scale input: the decision layer reads one pyramid level
    x_tr = [model.forward(views(x)[view]) for x in tr_in]
    x_te = [model.forward(views(x)[view]) for x in te_in]
    n_spk = float(np.mean([int((x != NO_SPIKE).sum()) for x in x_tr[:: max(1, len(x_tr) // 200)]]))
    log(f"decision-layer input: {n_spk:.0f} spikes per image")
    if rs.get("threshold") == "auto":  # a fraction of the expected final potential (w ~ w_mean on every input spike)
        frac = rs.get("threshold_frac", 0.2) * (rs["kernel"] ** 2 / max(1, x_tr[0].shape[-1] * x_tr[0].shape[-2]))
        rs["threshold"] = max(1.0, frac * n_spk * cfg.get("init", {}).get("w_mean", 0.8))
        log(f"decision threshold calibrated to {rs['threshold']:.1f}")
    if rs.get("flip") and encode is not None and tr_raw is not None:  # mirrored training images (new views, D28)
        x_tr = x_tr + [model.forward(views(encode(img.flip(-1)))[view]) for img in tr_raw]
        tr_y = list(tr_y) + list(tr_y)
        log(f"R-STDP training set with mirrored images: {len(x_tr)}")
    n_cls = len(cfg["classes"])
    kw = dict(calcium=rs.get("calcium"), margin=rs.get("margin"), teacher=rs.get("teacher", 0.0),
              rule=rs.get("rule", "stdp"), sdsp=rs.get("sdsp"))
    if rs.get("hidden"):  # hidden layer: STDP pre-training, then attention-gated R-STDP (AGREL, D24)
        from ..ventral.rstdp_attention import AttentionRSTDP
        hid = rs["hidden"]
        readout = AttentionRSTDP(x_tr[0].shape[1], n_cls, hid, rs, RSTDPRates(**rs.get("rates", {})),
                                 rs.get("dropout", 0.0), model.T, device, gen, rs.get("attention"),
                                 **cfg.get("init", {}), **kw)
        t_pre = time.time()
        readout.pretrain(x_tr, hid.get("a_plus", 0.004), hid.get("a_minus", 0.003), hid.get("pretrain_iter", 5000),
                         log=log)
        log(f"hidden layer: STDP pre-training {time.time() - t_pre:.0f} s; decision-layer input "
            f"{np.mean([int((readout.features(x) != NO_SPIKE).sum()) for x in x_te[:200]]):.0f} spikes per image")
    else:
        readout = RSTDPReadout(x_tr[0].shape[1], n_cls, rs["maps_per_class"], rs["kernel"], rs["threshold"],
                               RSTDPRates(**rs.get("rates", {})), rs.get("dropout", 0.0), model.T, device, gen,
                               **cfg.get("init", {}), **kw)
    history, best_train, best = [], -1.0, None
    for epoch in range(1, rs["epochs"] + 1):
        tr = readout.train_epoch(x_tr, tr_y)
        row = {"epoch": epoch, "train_hit": tr["hit"], "train_silent": tr["silent"]}
        if epoch % rs.get("eval_every", 5) == 0 or epoch == rs["epochs"]:
            ev_tr = readout.evaluate(x_tr, tr_y)
            ev_te = readout.evaluate(x_te, te_y)
            row |= {"train_acc": ev_tr["acc"], "test_acc": ev_te["acc"], "test_silent": ev_te["silent"]}
            if ev_tr["acc"] >= best_train:
                best_train, best = ev_tr["acc"], (epoch, ev_tr, ev_te)
            att = f", attention updates {readout.updates}" if hasattr(readout, "updates") else ""
            log(f"R-STDP epoch {epoch}: train {ev_tr['acc']:.4f} test {ev_te['acc']:.4f} (silent {ev_te['silent']:.3f}){att}")
        history.append(row)
    epoch_sel, ev_tr, ev_te = best
    pred = [p if p >= 0 else n_cls for p in ev_te["pred"]]  # silence counted as its own (wrong) column
    evals = [h for h in history if "test_acc" in h]
    probe = {"train_acc": ev_tr["acc"], "test_acc": ev_te["acc"],
             "confusion": confusion_matrix(te_y, pred, labels=list(range(n_cls)) + [n_cls])[:n_cls, :n_cls].tolist()}
    extra = {"rstdp_selected_epoch": epoch_sel, "rstdp_final_test_acc": evals[-1]["test_acc"],
             "rstdp_best_test_acc_optimistic": max(h["test_acc"] for h in evals), "rstdp_history": history,
             "rstdp_test_silent": ev_te["silent"]}
    log(f"R-STDP selected epoch {epoch_sel} (best train): test {ev_te['acc']:.4f}; final {extra['rstdp_final_test_acc']:.4f}; "
        f"best-test (optimistic) {extra['rstdp_best_test_acc_optimistic']:.4f}")
    if cfg.get("invariance") and encode is not None:  # the final (trained) decision layer on perturbed test images
        from ..eval.invariance import perturbations
        idx = list(range(0, len(te_raw), max(1, len(te_raw) // cfg["invariance"].get("n_test", 400))))
        ys = [te_y[i] for i in idx]
        inv = {"none": readout.evaluate([model.forward(views(encode(te_raw[i]))[view]) for i in idx], ys)["acc"]}
        for name, f in perturbations(cfg["invariance"]):
            inv[name] = readout.evaluate([model.forward(views(encode(f(te_raw[i])))[view]) for i in idx], ys)["acc"]
            log(f"invariance (R-STDP) {name}: {inv[name]:.4f} (unperturbed {inv['none']:.4f})")
        extra["invariance_rstdp"] = inv
    return probe, extra


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--limit", type=int, default=None, help="smoke run: number of training images")
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE",
                    help="override a config entry, e.g. --set layers.2.radius=4 (dotted path, list indices allowed)")
    ap.add_argument("--load-weights", default=None,
                    help="weights.pt of an earlier run with the same layers: skip STDP training, evaluate readouts only")
    args = ap.parse_args()

    cfg = load_config(args.config)
    for item in args.set:
        key, value = item.split("=", 1)
        *parents, last = key.split(".")
        node = cfg
        for p in parents:
            node = node[int(p)] if isinstance(node, list) else node.setdefault(p, {})
        node[int(last) if isinstance(node, list) else last] = yaml.safe_load(value)
    cfg["overrides"] = args.set
    from ..learning import hw
    hw.configure(cfg.get("hardware"))  # shift-and-add learning arithmetic (D22)
    if cfg.get("n_layers"):  # keep only the first n layers (e.g. read out conv2 without training conv3)
        cfg["layers"] = cfg["layers"][: cfg["n_layers"]]
    cfg["seed"] = args.seed
    name = Path(args.config).stem
    paths = Paths.from_config(cfg)
    out = Path(os.environ.get("RUN_DIR", paths.runs / "adhoc" / f"{name}_s{args.seed}"))
    (out / "figs").mkdir(parents=True, exist_ok=True)
    device = resolve_device(cfg.get("device", "auto"))
    set_deterministic(cfg.get("deterministic", True))
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    gen = torch.Generator().manual_seed(args.seed)
    (out / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")
    log(f"{name} seed {args.seed} on {describe(device)} -> {out}")

    # ---- data and retina (DoG + rank-order code, Section 4.3 / paper) -----------------------------------
    t0 = time.time()
    tr_x, tr_y, te_x, te_y, tr_groups = load_data(cfg, paths, args.seed, args.limit)
    log(f"data: {len(tr_x)} train / {len(te_x)} test images ({time.time() - t0:.0f} s)")
    r = cfg["retina"]
    T = cfg["time"]["T"]
    kernels = [sdnn_dog_kernel(*k) for k in r.get("dog_kernels", [])]

    if r.get("mode") == "gabor_c1":  # Mozafari 2018 front end (fixed Gabor S1 + C1), D18
        from ..retina.gabor import gabor_c1, gabor_kernel
        gk = [gabor_kernel(r.get("gabor_size", 5), o) for o in r["orientations"]]
        kernels = gk

        def encode(img: torch.Tensor) -> torch.Tensor:
            return gabor_c1(img.to(device) / 255.0, gk, tuple(r["pool"]), r.get("lateral_inhibition"), T).unsqueeze(0)
    elif r.get("mode") == "bio3":  # Phase 1: hardware-aware log-domain retina, factor-2 pyramid (D26)
        from ..retina.hw_retina import CHANNELS, calibrate_l_min, encode_bio3, pyramid_pow2
        ch = r.get("channels", "pk")
        filt = r.get("filters") or {}
        n_extra = CHANNELS["pk" if ch == "pkm" else ch] if filt.get("lcn") and filt.get("dual") else 0
        kernels = [None] * (CHANNELS[ch] + n_extra)  # dual retina: luminance- and contrast-normalised channels
        l_min = r.get("l_min", -0.5)
        l_floor = None
        if ch != "m" and (l_min == "auto" or (l_min == "adaptive" and r.get("adapt_floor") is not None)):
            # per-channel contrast thresholds for equal input density (offline constants); with contrast adaptation
            # they set the floor: the threshold may adapt down by at most `adapt_floor` octaves
            sample = [(x if x.dim() == 3 else x.unsqueeze(0).expand(3, -1, -1)).to(device)
                      for x in tr_x[:: max(1, len(tr_x) // 40)][:40]]
            lm = calibrate_l_min(sample, ch, r.get("input_rate", 0.07), r.get("log", "mitchell"), r.get("filters"))
            log(f"retina contrast thresholds per channel: {[round(float(v), 2) for v in lm.flatten()]}")
            if l_min == "auto":
                l_min = lm
            else:
                l_floor = lm - r["adapt_floor"]

        mg = r.get("magno") or {}  # CLAUDE.md 4.3 keys -> magno_times(): C in natural-log units -> octaves
        magno_kw = {"contrast": mg.get("contrast_threshold", 0.2) / math.log(2),
                    "shifts": tuple(tuple(m) for m in mg.get("microsaccades", [[1, 0, 0], [0, -1, 3], [-1, 0, 6], [0, 1, 9]]))}

        def encode(img: torch.Tensor):
            x = img.to(device) / 255.0
            if x.dim() == 2:
                x = x.unsqueeze(0).expand(3, -1, -1)
            lv = pyramid_pow2(x, r.get("levels", 3))
            v = [encode_bio3(lev, T, ch, r.get("coding", "log"), r.get("delta", 0.25), r.get("log", "mitchell"),
                             r.get("per_channel", False), magno_kw, r.get("filters"), l_min, r.get("input_rate", 0.07),
                             l_floor)
                 for lev in lv]
            return v if len(v) > 1 else v[0]
    else:
        encode = None

    def encode_dog(img: torch.Tensor) -> torch.Tensor:
        resp = sdnn_dog_input(img.to(device), kernels, r["threshold"])
        top = r.get("top_fraction")
        if top:  # equal spike budget per image: only the strongest `top` fraction of DoG cells fire (D17)
            k = max(1, int(top * resp.numel()))
            thr = resp.flatten().kthvalue(resp.numel() - k + 1).values
            resp = torch.where(resp >= thr, resp, torch.zeros_like(resp))
        return rank_order(resp, T, theta_in=1e-9, per_channel=r.get("rank_per_channel", False)).unsqueeze(0)

    encode = encode or encode_dog
    scales = r.get("scales")
    if scales:  # multi-scale input with shared weights (Kheradpisheh 2016): one spike-time map per scale
        if "rstdp" in cfg:
            raise ValueError("retina.scales is not supported with the R-STDP readout")
        single = encode

        def encode(img: torch.Tensor) -> list[torch.Tensor]:
            return [single(img if s == 1 else F.interpolate(img[None, None], scale_factor=s, mode="bilinear",
                                                            align_corners=False)[0, 0]) for s in scales]
    tr_in = [encode(x) for x in tr_x]
    te_in = [encode(x) for x in te_x]
    in_spikes = float(np.mean([sum(int((t != NO_SPIKE).sum()) for t in views(x)) for x in te_in]))
    log(f"encoded ({time.time() - t0:.0f} s); input spikes per test image {in_spikes:.0f}")

    # ---- layer-wise STDP ----------------------------------------------------------------------------------
    model = SDNN(len(kernels), cfg["layers"], T, device, gen, **cfg.get("init", {}))
    lr = cfg["learning"]
    curves, train_time = {}, {}
    if args.load_weights:
        saved = torch.load(args.load_weights)
        th_path = Path(args.load_weights).with_name("thresholds.pt")
        saved_th = torch.load(th_path) if th_path.exists() else {}
        for li in model.conv_ids:
            model.layers[li].weight = saved[li].to(device)
            if li in saved_th:  # learned (homeostatic) thresholds
                th = saved_th[li]
                model.layers[li].threshold = th.to(device) if th.dim() else float(th)
        log(f"loaded STDP weights from {args.load_weights} (no STDP training)")
        cfg["loaded_weights"] = args.load_weights
    for n, li in enumerate(model.conv_ids if not args.load_weights else [], start=1):
        t1 = time.time()
        inputs = [model.forward(v, upto=li) for x in tr_in for v in views(x)]  # every scale is a training view
        if model.layers[li].threshold == "auto":  # CLAUDE.md 5.4: ~fire_rate of the positions fire initially
            log(f"conv{n}: threshold calibrated to {model.calibrate(li, inputs):.2f}")
        curve = model.train_layer(li, inputs, lr["a_plus"], lr["a_minus"], gen, lr["freeze_below"],
                                  max_iter=lr["max_iter"][n - 1], log=log)
        curves[f"conv{n}"] = curve
        train_time[f"conv{n}"] = time.time() - t1
        log(f"conv{n}: {curve[-1][0]} iterations, C_l = {curve[-1][1]:.4f}, {train_time[f'conv{n}']:.0f} s")

    # ---- readout: R-STDP first-spike decision (Mozafari 2018) or probe on final potentials ---------------
    t2 = time.time()
    extra = {}
    if "rstdp" in cfg:
        probe, extra = rstdp_readout(cfg, model, tr_in, tr_y, te_in, te_y, gen, device, log, encode, te_x, tr_x)
        ips = (len(tr_in) + len(te_in)) / (time.time() - t2)
    else:
        ro = cfg.get("readout", {})
        # readout.variants: several readouts scored from ONE pass over the data (each overrides the base keys)
        variants = [{**{k: v for k, v in ro.items() if k != "variants"}, **v} for v in ro.get("variants") or [{}]]
        for v in variants:
            v.setdefault("layers", [model.conv_ids[-1]])
            v.setdefault("grid", 1)
            g = "-".join(map(str, v["grid"])) if isinstance(v["grid"], list) else v["grid"]
            v.setdefault("name", f"g{g}_l{'-'.join(map(str, v['layers']))}" + ("_std" if v.get("standardize") else "")
                         + ("_flip" if v.get("flip") else "") + (f"_C{v['C']}" if "C" in v else "")
                         + (f"_{v['svm']}" if "svm" in v else ""))
        need = sorted({li for v in variants for li in v["layers"]})
        store = torch.float16 if len(variants) > 1 else torch.float32  # RAM: many variants x 60k MNIST images

        def feats(x) -> list[torch.Tensor]:  # one pass per view; max over scales of each (map, cell) feature
            per_view = [model.readout_maps(view, need) for view in views(x)]
            return [torch.stack([model.pool_features(m, v["grid"], v["layers"]) for m in per_view]).amax(0)
                    .cpu().to(store) for v in variants]
        f_tr = list(zip(*[feats(x) for x in tr_in]))
        f_te = list(zip(*[feats(x) for x in te_in]))
        if any(v.get("flip") for v in variants):  # mirrored TRAINING images as extra classifier samples
            f_trf = list(zip(*[feats(encode(torch.flip(x, dims=[-1]))) for x in tr_x]))
        ips = (len(tr_in) + len(te_in)) / (time.time() - t2)
        results = {}
        for j, v in enumerate(variants):
            a_tr, a_te = torch.cat(f_tr[j]).float().numpy(), torch.cat(f_te[j]).float().numpy()
            y_tr, g_tr = tr_y, tr_groups
            if v.get("flip"):
                a_tr = np.concatenate([a_tr, torch.cat(f_trf[j]).float().numpy()])
                y_tr = list(tr_y) * 2
                g_tr = list(tr_groups) * 2 if tr_groups is not None else None
            if v.get("standardize"):
                mu, sd = a_tr.mean(0), a_tr.std(0) + 1e-6
                a_tr, a_te = (a_tr - mu) / sd, (a_te - mu) / sd
            tag = f" [{v['name']}]" if len(variants) > 1 else ""
            C, kind, cv = v.get("C", cfg["svm_C"]), v.get("svm", "ovr"), None
            if C == "auto":  # C chosen by (grouped) cross-validation inside the training set
                C, cv = select_C(a_tr, y_tr, g_tr, seed=args.seed, kind=kind)
                log(f"C by cross-validation on the training set: {C} (cv acc {cv[C]:.4f}){tag}")
            p = svm_probe(a_tr, y_tr, a_te, te_y, C=C, seed=args.seed, kind=kind)
            log(f"SVM: train {p['train_acc']:.4f}, test {p['test_acc']:.4f}{tag}")
            res = {"svm": p["test_acc"], "train": p["train_acc"], "C": C, "cv": cv,
                   "spec": {k: x for k, x in v.items() if k != "name"}}
            if v.get("knn"):
                res["knn"] = knn_probe(a_tr, y_tr, a_te, te_y, k=v["knn"])
                log(f"KNN (k={v['knn']}): test {res['knn']:.4f}{tag}")
            results[v["name"]] = res
            if j == 0 and cfg.get("invariance"):  # first readout on perturbed test images (same classifier)
                from ..eval.invariance import perturbations
                from ..eval.probes import make_svm
                clf = make_svm(C, args.seed, kind).fit(a_tr, y_tr)
                idx = list(range(0, len(te_x), max(1, len(te_x) // cfg["invariance"].get("n_test", 400))))
                ys = np.asarray([te_y[i] for i in idx])

                def score(f):
                    a = torch.cat([feats(encode(f(te_x[i])))[0] for i in idx]).float().numpy()
                    if v.get("standardize"):
                        a = (a - mu) / sd
                    return float((clf.predict(a) == ys).mean())
                inv = {"none": score(lambda im: im)}
                for name, f in perturbations(cfg["invariance"]):
                    inv[name] = score(f)
                    log(f"invariance (SVM) {name}: {inv[name]:.4f} (unperturbed {inv['none']:.4f})")
                extra["invariance_svm"] = inv
            if j == 0:
                probe = p
                if "knn" in res:
                    extra["knn_test_acc"] = res["knn"]
            del a_tr, a_te
        extra["variants"] = results

    sparsity, spikes = {}, {"input": in_spikes}
    step = max(1, len(te_in) // 200)  # evenly spread over the test set (it is ordered by class)
    sample = te_in[::step][:200]
    per_layer = None
    for x in sample:
        counts = None
        for v in views(x):  # spikes of all scales count for this image
            rec = []
            model.forward(v, record=rec)
            c = [(int((t != NO_SPIKE).sum()), t.numel()) for t in rec]
            counts = c if counts is None else [(a + e, b + d) for (a, b), (e, d) in zip(counts, c)]
        per_layer = counts if per_layer is None else [(a + c, b + d) for (a, b), (c, d) in zip(per_layer, counts)]
    for i, (fired, total) in enumerate(per_layer or []):
        kind = "conv" if isinstance(model.layers[i], ConvLayer) else "pool"
        key = f"{i}_{kind}"
        sparsity[key] = fired / total
        spikes[key] = fired / len(sample)
    conv_spikes = sum(v for k, v in spikes.items() if k.endswith("conv"))

    metrics = {
        "dataset": cfg["dataset"], "seed": args.seed, "config_hash": config_hash(cfg), "device": describe(device),
        "n_train": len(tr_x), "n_test": len(te_x), "test_acc": probe["test_acc"], "train_acc": probe["train_acc"],
        "confusion": probe["confusion"], "final_C_l": {k: c[-1][1] for k, c in curves.items()},
        "iterations": {k: c[-1][0] for k, c in curves.items()}, "train_time_s": train_time,
        "feature_images_per_s": ips, "sparsity_per_layer": sparsity, "spikes_per_image": spikes,
        "spikes_per_image_input_plus_conv": in_spikes + conv_spikes, "paper_test_acc": cfg.get("paper_test_acc"),
        "weights": int(sum(l.weight.numel() for l in model.layers if isinstance(l, ConvLayer))), "limit": args.limit,
        "readout": "rstdp" if "rstdp" in cfg else f"svm_grid{cfg.get('readout', {}).get('grid', 1)}",
        "loaded_weights": args.load_weights, "eval_split": "validation" if cfg.get("validation") else "test",
        "overrides": args.set, **extra,
    }
    (out / "metrics.json").write_text(json.dumps(metrics, indent=1), encoding="utf-8")
    with open(out / "convergence.csv", "w", encoding="utf-8") as f:
        f.write("layer,iteration,C_l\n")
        for k, c in curves.items():
            f.writelines(f"{k},{i},{v:.6f}\n" for i, v in c)

    # ---- figures --------------------------------------------------------------------------------------------
    convergence_plot(curves, out / "figs" / "convergence.png", lr["freeze_below"])
    for n, li in enumerate(model.conv_ids, start=1):
        try:
            feature_grid(reconstruct_features(model.layers, kernels, li), out / "figs" / f"features_conv{n}.png",
                         f"{name} seed {args.seed}: conv{n} preferred features")
        except Exception as e:  # noqa: BLE001  (no fixed input kernels to back-project through, e.g. bio3)
            log(f"feature figure conv{n} skipped: {type(e).__name__}")
    confusion_plot(probe["confusion"], cfg["classes"], out / "figs" / "confusion.png",
                   f"{name} seed {args.seed}: test acc {probe['test_acc']:.3f}")
    torch.save({i: l.weight.cpu() for i, l in enumerate(model.layers) if isinstance(l, ConvLayer)}, out / "weights.pt")
    torch.save({i: torch.as_tensor(l.threshold).cpu() for i, l in enumerate(model.layers) if isinstance(l, ConvLayer)},
               out / "thresholds.pt")
    log(f"done: test accuracy {probe['test_acc']:.4f} (paper {cfg.get('paper_test_acc')})")


if __name__ == "__main__":
    main()
