"""Build the Persian Word report of Phase 1 from the text sources and the campaign results.

    python tools/build_phase1_report.py

1. ``tools/phase1_figures.py``: figures + ``reports/phase1/numbers.json`` from the metrics of every run;
2. the sources (summary, methods, results, architecture) are joined, ``{{key}}`` placeholders are replaced by
   "mean ± std" (a single run: the value; a plain number: rounded; missing: "در حال اجرا");
3. ``tools/docx_report.py`` writes ``reports/phase1/گزارش_فاز_۱.docx`` (right-to-left, native Word equations).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import docx_report  # noqa: E402
import phase1_figures  # noqa: E402

REP = ROOT / "reports" / "phase1"


def fmt(v) -> str:
    if isinstance(v, (int, float)):
        return f"{v:.1f}" if abs(v) < 100 else f"{v:,.0f}"
    if not isinstance(v, (list, tuple)) or v[0] is None:
        return "در حال اجرا"
    mean, sd = v
    return f"{mean:.2f} ± {sd:.2f}" if sd else f"{mean:.2f}"


def main() -> None:
    phase1_figures.main()
    numbers = phase1_figures.numbers()
    parts = [
        "[[TITLE]] گزارش فاز ۱ پروژهٔ BioVision-SNN | مسیر شکمی رنگی تا IT روی شبکیهٔ لگاریتمی | "
        "طراحی سخت‌افزارآگاه بی‌ضرب، تحلیل ریاضی و آزمون‌های ناوردایی",
        "[[PAGEBREAK]]",
        "**فهرست مطالب**",
        "[[TOC]]",
        "[[PAGEBREAK]]",
    ] + [(REP / f"report_fa_{p}.txt").read_text(encoding="utf-8") for p in ("summary", "methods", "results", "architecture")]
    text = "\n\n".join(parts)
    missing = set()

    def sub(m):
        key = m.group(1)
        if key not in numbers:
            missing.add(key)
            return "؟"
        return fmt(numbers[key])
    text = re.sub(r"\{\{(\w+)\}\}", sub, text)
    if missing:
        print("unknown placeholders:", sorted(missing))
    (REP / "report_fa_full.txt").write_text(text, encoding="utf-8")
    rep = docx_report.Report()
    rep.build(text, REP)
    out = REP / "گزارش_فاز_۱.docx"
    rep.doc.save(out)
    print(f"wrote {out}: {rep.eq} equations, {rep.tab} tables, {rep.fig} figures")


if __name__ == "__main__":
    main()
