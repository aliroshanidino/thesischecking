"""Build the Persian Word report of Phase 0 from the text sources and the campaign results.

    python tools/build_phase0_report.py

1. ``tools/phase0_figures.py``: figures + ``reports/phase0/numbers.json`` from the metrics of every run;
2. the sources (summary, methods, learning-rule survey, results) are joined, ``{{key}}`` placeholders are replaced by
   "mean ± std" of the numbers (a single run: the value; missing: "در حال اجرا");
3. ``tools/docx_report.py`` writes ``reports/phase0/گزارش_فاز_۰.docx`` (right-to-left, native Word equations).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import docx_report  # noqa: E402
import phase0_figures  # noqa: E402

REP = ROOT / "reports" / "phase0"


def fmt(v) -> str:
    if not isinstance(v, (list, tuple)) or v[0] is None:
        return "در حال اجرا"
    mean, sd = v
    return f"{mean:.2f} ± {sd:.2f}" if sd else f"{mean:.2f}"


def survey_section() -> str:
    s = (ROOT / "docs" / "learning_rules_survey_fa.md").read_text(encoding="utf-8")
    s = re.sub(r"^# .*$", "# ۷. مرور قاعده‌های یادگیری زیستی", s, count=1, flags=re.M)
    s = re.sub(r"^## (\d)\. ", lambda m: f"## ۷-{'۰۱۲۳۴۵۶۷۸۹'[int(m.group(1))]} ", s, flags=re.M)
    s = s.replace("| قاعده | پایهٔ زیستی |", "| قاعده | پایهٔ زیستی |")
    return s


def main() -> None:
    phase0_figures.main()
    numbers = phase0_figures.numbers()
    parts = [
        "[[TITLE]] گزارش فاز ۰ پروژهٔ BioVision-SNN | بازتولید و بهبود شبکه‌های اسپایکی تیم خردپیشه و گنج‌تابش | "
        "یادگیری تقویتی سخت‌افزارپذیر، قاعده‌های کلسیمی و قاعدهٔ توجه",
        "[[PAGEBREAK]]",
        "**فهرست مطالب**",
        "[[TOC]]",
        "[[PAGEBREAK]]",
        (REP / "report_fa_summary.txt").read_text(encoding="utf-8"),
        (REP / "report_fa_methods.txt").read_text(encoding="utf-8"),
        survey_section(),
        (REP / "report_fa_results.txt").read_text(encoding="utf-8"),
    ]
    arch = (REP / "report_fa_architecture.txt").read_text(encoding="utf-8")
    parts[-1] = parts[-1].replace("# ۱۲. جمع‌بندی", arch + "\n\n# ۱۲. جمع‌بندی", 1)
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
    out = REP / "گزارش_نهایی_فاز_۰.docx"
    rep.doc.save(out)
    print(f"wrote {out}: {rep.eq} equations, {rep.tab} tables, {rep.fig} figures")


if __name__ == "__main__":
    main()
