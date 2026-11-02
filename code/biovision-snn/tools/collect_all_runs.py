"""Every run of every campaign (Phase 0 and Phase 1) in one table, finished or interrupted.

    python tools/collect_all_runs.py      # writes results/all_runs.csv and results/invariance.csv

A finished run has ``metrics.json``; an interrupted one (stopped campaign) only ``log.txt``: its last R-STDP
evaluation or SVM line is reported with ``status = interrupted``.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAMPS = ROOT.parent / "work" / "campaigns"
OUT = ROOT / "results"


def best_variant(met: dict) -> tuple[str, float]:
    vs = met.get("variants") or {}
    if not vs:
        return "", met["test_acc"]
    name, v = max(vs.items(), key=lambda kv: kv[1]["svm"])
    return name, v["svm"]


def last_log_value(log: Path) -> tuple[str, str]:
    """Last evaluation found in an interrupted run's log."""
    text = log.read_text(encoding="utf-8", errors="replace")
    ep = re.findall(r"R-STDP epoch (\d+): train ([\d.]+) test ([\d.]+)", text)
    if ep:
        e, tr, te = ep[-1]
        return f"epoch {e}", te
    sv = re.findall(r"SVM: train [\d.]+, test ([\d.]+) \[(.+?)\]", text)
    if sv:
        return f"svm {sv[-1][1]}", sv[-1][0]
    stage = re.findall(r"(conv\d): (\d+) iterations", text)
    return (f"{stage[-1][0]} trained" if stage else "started"), ""


def main() -> None:
    OUT.mkdir(exist_ok=True)
    rows, inv_rows = [], []
    for log in sorted(CAMPS.glob("*/*/*/*/log.txt")):
        run = log.parent
        camp, stage, group, tag = run.parts[-4:]
        cmd = json.loads((run / "cmd.json").read_text(encoding="utf-8")) if (run / "cmd.json").exists() else []
        sets = [cmd[i + 1] for i, c in enumerate(cmd) if c == "--set"]
        config = cmd[cmd.index("--config") + 1] if "--config" in cmd else ""
        row = {"campaign": camp, "stage": stage, "group": group, "run": tag, "config": config,
               "overrides": " | ".join(sets)}
        m = run / "metrics.json"
        if m.exists():
            met = json.loads(m.read_text(encoding="utf-8"))
            vn, vacc = best_variant(met)
            row |= {"status": "finished", "dataset": met.get("dataset", ""), "split": met.get("eval_split", "test"),
                    "acc": round(100 * met["test_acc"], 2), "best_variant": vn, "best_variant_acc": round(100 * vacc, 2),
                    "rstdp_best_epoch_acc": round(100 * met["rstdp_best_test_acc_optimistic"], 2)
                    if "rstdp_best_test_acc_optimistic" in met else "",
                    "rstdp_selected_epoch": met.get("rstdp_selected_epoch", ""),
                    "input_spikes": round((met.get("spikes_per_image") or {}).get("input", 0)),
                    "spikes_input_plus_conv": round(met.get("spikes_per_image_input_plus_conv", 0)),
                    "weights": met.get("weights", ""), "n_train": met.get("n_train", ""), "n_eval": met.get("n_test", ""),
                    "C_l": " ".join(f"{k}={v:.3f}" for k, v in met.get("final_C_l", {}).items()),
                    "train_time_s": round(sum(met.get("train_time_s", {}).values())), "last_seen": ""}
            inv = met.get("invariance_rstdp") or met.get("invariance_svm")
            if inv:
                inv_rows.append({"campaign": camp, "stage": stage, "group": group, "run": tag,
                                 "readout": "rstdp" if "invariance_rstdp" in met else "svm",
                                 **{k: round(100 * v, 2) for k, v in inv.items()}})
        else:
            where, acc = last_log_value(log)
            failed = "Traceback" in log.read_text(encoding="utf-8", errors="replace")
            row |= {"status": "failed" if failed else "interrupted", "acc": round(100 * float(acc), 2) if acc else "",
                    "last_seen": where}
        rows.append(row)
    keys = ["campaign", "stage", "group", "run", "status", "dataset", "split", "acc", "best_variant", "best_variant_acc",
            "rstdp_best_epoch_acc", "rstdp_selected_epoch", "input_spikes", "spikes_input_plus_conv", "weights",
            "n_train", "n_eval", "C_l", "train_time_s", "last_seen", "config", "overrides"]
    with open(OUT / "all_runs.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    inv_keys = ["campaign", "stage", "group", "run", "readout"] + sorted({k for r in inv_rows for k in r} -
                                                                          {"campaign", "stage", "group", "run", "readout"})
    with open(OUT / "invariance.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=inv_keys)
        w.writeheader()
        w.writerows(inv_rows)
    n = {s: sum(r["status"] == s for r in rows) for s in ("finished", "interrupted", "failed")}
    print(f"{len(rows)} runs: {n}; invariance rows {len(inv_rows)}")


if __name__ == "__main__":
    main()
