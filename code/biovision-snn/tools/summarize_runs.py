"""Table of Phase-0 style runs: every metrics.json under work/runs (optionally filtered), newest first.
Usage: python tools/summarize_runs.py [substring-filter ...]"""
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1].parent / "work" / "runs"
rows = []
for m in root.rglob("metrics.json"):
    rel = str(m.parent.relative_to(root)).replace("\\", "/")
    if sys.argv[1:] and not all(f in rel for f in sys.argv[1:]):
        continue
    d = json.loads(m.read_text(encoding="utf-8"))
    rows.append((m.stat().st_mtime, rel, d))
rows.sort(reverse=True)
print(f"{'run':62s} {'set':5s} {'svm/acc':>8s} {'knn':>7s} {'train':>6s}  readout / overrides")
for _, rel, d in rows:
    knn = d.get("knn_test_acc")
    ov = " ".join(o.split("=")[0].split(".")[-1] + "=" + o.split("=", 1)[1] for o in (d.get("overrides") or []))
    print(f"{rel[:62]:62s} {d.get('eval_split', 'test')[:5]:5s} {d['test_acc']*100:7.2f}% "
          f"{(f'{knn*100:6.2f}%' if knn is not None else '      -')} {d['train_acc']*100:5.1f}%  {d.get('readout', '')} {ov}")
