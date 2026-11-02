"""Collect every Phase 0 result (campaigns + earlier runs) into one table for the report.

    python tools/phase0_tables.py [--out reports/phase0/results_all.csv]

For each run directory with a ``metrics.json`` it records the dataset, the evaluation split (validation / test),
every readout variant's accuracy, spikes per image, weights and timing; then prints mean +- std per
(campaign, stage, group, variant) so that the report tables can be written from it.
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics as st
from collections import defaultdict
from pathlib import Path

WORK = Path(__file__).resolve().parents[2] / "work"


def runs():
    for m in sorted(list((WORK / "campaigns").glob("*/*/*/*/metrics.json")) +
                    list((WORK / "runs" / "phase0").glob("*/*/metrics.json")) +
                    list((WORK / "runs" / "phase0").glob("*/*/*/metrics.json"))):
        try:
            yield m, json.loads(m.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path(__file__).resolve().parents[1] / "reports" / "phase0" / "results_all.csv"))
    ap.add_argument("--filter", default="")
    a = ap.parse_args()
    rows, groups = [], defaultdict(list)
    for m, met in runs():
        rel = m.parent.relative_to(WORK).as_posix()
        if a.filter and a.filter not in rel:
            continue
        parts = rel.split("/")
        key = "/".join(parts[:-1])  # everything but the seed / fold directory
        variants = met.get("variants") or {"": {"svm": met["test_acc"]}}
        for vn, v in variants.items():
            row = {"run": rel, "group": key, "variant": vn or met.get("readout", ""), "dataset": met["dataset"],
                   "split": met.get("eval_split", "test"), "seed": met["seed"], "acc": v["svm"], "knn": v.get("knn", ""),
                   "C": v.get("C", ""), "spikes": round(met.get("spikes_per_image_input_plus_conv", 0), 1),
                   "weights": met.get("weights", ""), "img_per_s": round(met.get("feature_images_per_s", 0), 2),
                   "train_s": round(sum(met.get("train_time_s", {}).values()), 1),
                   "rstdp_final": met.get("rstdp_final_test_acc", ""),
                   "rstdp_best_optimistic": met.get("rstdp_best_test_acc_optimistic", "")}
            rows.append(row)
            groups[(key, row["variant"], row["split"], met["dataset"])].append(v["svm"])
    if rows:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        with open(a.out, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    for (key, vn, split, ds), accs in sorted(groups.items()):
        sd = st.stdev(accs) if len(accs) > 1 else 0.0
        print(f"{ds:8s} {split:10s} {100 * st.mean(accs):6.2f} +- {100 * sd:4.2f} (n={len(accs)})  {key} [{vn}]")


if __name__ == "__main__":
    main()
