#!/usr/bin/env python3
"""Insight date-nav perf: coalesce fill, skip hidden panes, SVG guard, expense cache."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from insight_diff_client import (  # noqa: E402
    INSIGHT_DIFF_JS_END,
    INSIGHT_DIFF_JS_MARKER,
    INSIGHT_FILL_NEW,
    INSIGHT_OVERLAY_IIFE,
    INSIGHT_SET_TAB_NEW,
    INSIGHT_SET_TAB_OLD,
    insight_diff_js,
)
from insight_expense_read_client import (  # noqa: E402
    INSIGHT_EXPENSE_READ_END,
    INSIGHT_EXPENSE_READ_MARKER,
    insight_expense_read_js,
)
from insight_trend_annual_graph1_client import (  # noqa: E402
    TREND_LISTENERS_NEW as G1_LISTENERS_NEW,
)
from insight_trend_annual_graph2_client import (  # noqa: E402
    TREND_LISTENERS_NEW as G2_LISTENERS_NEW,
)
from insight_trend_monthly_client import (  # noqa: E402
    TREND_LISTENERS_NEW as MONTHLY_LISTENERS_NEW,
)

PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

# Currently shipped listeners (pre-guard)
LISTENERS_BEFORE_GUARD = """        render();
        [
          'annual:calendarDateChanged',
          'annual:dailyDateChanged',
          'kpi:dailyTargetModeChanged',
          'kpi:weekdayBaselineChanged',
          'kpi:annualPlanChanged',
          'insight:dateChanged',
        ].forEach(function (evName) {
          document.addEventListener(evName, render);
        });
      }"""

FILL_SYNC_RE = re.compile(
    r"      function fill\(iso\) \{\n"
    r"        iso = iso \|\| resolveIso\(\);\n"
    r"        if \(dateBtnEl\) dateBtnEl\.textContent = fmtDate\(iso\);\n"
    r"        if \(todayBtnEl\) todayBtnEl\.hidden = iso === getTodayIso\(\);\n"
    r"        if \(dateInputEl\) dateInputEl\.value = iso;\n"
    r"        window\.__INSIGHT_SELECTED_ISO = iso;\n"
    r"        try \{\n"
    r"          if \(typeof window\.renderInsightTwDiffs === 'function'\) \{\n"
    r"            window\.renderInsightTwDiffs\(iso\);\n"
    r"          \}\n"
    r"        \} catch \(_insightDiffErr\) \{\}\n"
    r"        try \{\n"
    r"          document\.dispatchEvent\(new CustomEvent\('insight:dateChanged', \{ detail: \{ iso: iso \} \}\)\);\n"
    r"        \} catch \(_insightDateErr\) \{\}\n"
    r"      \}"
)


def inject_insight_diff_js(text: str) -> str:
    block = insight_diff_js().rstrip() + "\n"
    if INSIGHT_DIFF_JS_MARKER not in text:
        pos = text.find(INSIGHT_OVERLAY_IIFE)
        if pos < 0:
            raise SystemExit("insight-overlay IIFE anchor miss")
        return text[:pos] + block + text[pos:]
    pattern = (
        re.escape(INSIGHT_DIFF_JS_MARKER)
        + r"[\s\S]*?"
        + re.escape(INSIGHT_DIFF_JS_END)
        + r"\n?"
    )
    return re.sub(pattern, lambda _m: block.rstrip() + "\n", text, count=1)


def inject_expense_read(text: str) -> str:
    pattern = (
        re.escape(INSIGHT_EXPENSE_READ_MARKER)
        + r"[\s\S]*?"
        + re.escape(INSIGHT_EXPENSE_READ_END)
        + r"\n?"
    )
    text = re.sub(pattern, "", text)
    block = insight_expense_read_js().rstrip() + "\n"
    anchor = "    /* KPI-INSIGHT-TW-DIFF */"
    if anchor not in text:
        raise SystemExit("KPI-INSIGHT-TW-DIFF anchor miss")
    return text.replace(anchor, block + anchor, 1)


def patch_insight_fill(text: str) -> str:
    # Upgrade coalesce fill to skipAnalyze + settle when on Analyze
    if "__INSIGHT_FILL_SCHED" in text and "runInsightFillHeavy" in text:
        if "skipAnalyze: onAnalyze" in text and "__scheduleInsightAnalyzeSettle" in text:
            return text
        # Replace entire fill() that has coalesce but older heavy body
        import re

        pattern = re.compile(
            r"      function fill\(iso\) \{\n"
            r"        iso = iso \|\| resolveIso\(\);\n"
            r"        if \(dateBtnEl\) dateBtnEl\.textContent = fmtDate\(iso\);\n"
            r"        if \(todayBtnEl\) todayBtnEl\.hidden = iso === getTodayIso\(\);\n"
            r"        if \(dateInputEl\) dateInputEl\.value = iso;\n"
            r"        window\.__INSIGHT_SELECTED_ISO = iso;\n"
            r"        window\.__INSIGHT_PENDING_ISO = iso;\n"
            r"        if \(window\.__INSIGHT_FILL_SCHED\) return;\n"
            r"        window\.__INSIGHT_FILL_SCHED = true;\n"
            r"        requestAnimationFrame\(function \(\) \{\n"
            r"          requestAnimationFrame\(function \(\) \{\n"
            r"[\s\S]*?"
            r"            runInsightFillHeavy\(\);\n"
            r"          \}\);\n"
            r"        \}\);\n"
            r"      \}"
        )
        if not pattern.search(text):
            raise SystemExit("fill coalesce block miss for skipAnalyze upgrade")
        return pattern.sub(INSIGHT_FILL_NEW, text, count=1)
    if FILL_SYNC_RE.search(text):
        return FILL_SYNC_RE.sub(INSIGHT_FILL_NEW, text, count=1)
    if INSIGHT_FILL_NEW in text:
        return text
    raise SystemExit("insight overlay fill() patch miss")


def patch_set_insight_tab(text: str) -> str:
    if "__INSIGHT_TAB_PENDING" in text and "mode: pendingTab" in text:
        return text
    if "insight:tabChanged" in text and "which === 'analyze' || which === 'graph'" in text:
        return text
    if INSIGHT_SET_TAB_OLD not in text:
        raise SystemExit("setInsightTab patch miss")
    return text.replace(INSIGHT_SET_TAB_OLD, INSIGHT_SET_TAB_NEW, 1)


def patch_trend_listeners(text: str) -> str:
    if "insightTrendDirty" in text and "insightTrendRender" in text:
        # already guarded; ensure all three charts have it
        count = text.count("insightTrendDirty")
        if count >= 3:
            return text

    # Monthly chart ends before initGraphAnnualCumulativeTrendGraph1 / initGraphMonthlyCumulativeTrend call
    monthly_before = LISTENERS_BEFORE_GUARD
    monthly_after = MONTHLY_LISTENERS_NEW
    if monthly_before not in text and "insightTrendDirty" not in text:
        raise SystemExit("monthly trend listeners patch miss")

    # Replace each occurrence carefully with chart-specific NEW (suffix differs)
    # 1) monthly: ...listeners...}\n      initGraphMonthlyCumulativeTrend();
    #    OR on annual pages might still have same monthly chart
    # Graph1: ...}\n\n\n      function initGraphAnnualCumulativeTrendGraph2
    # Graph2: ...}\n      function initGraphDailyHistoricalWeekday

    g1_before = LISTENERS_BEFORE_GUARD + "\n\n\n      function initGraphAnnualCumulativeTrendGraph2() {"
    g1_after = G1_LISTENERS_NEW  # already includes trailing initGraphAnnual...

    g2_before = LISTENERS_BEFORE_GUARD + "\n      function initGraphDailyHistoricalWeekday() {"
    g2_after = G2_LISTENERS_NEW  # already includes trailing initGraphDaily...

    if g1_before in text:
        text = text.replace(g1_before, g1_after, 1)
    elif "function initGraphAnnualCumulativeTrendGraph2" in text and "insightTrendDirty" not in text:
        # try without extra blank lines
        alt = LISTENERS_BEFORE_GUARD + "\n\n      function initGraphAnnualCumulativeTrendGraph2() {"
        alt_new = G1_LISTENERS_NEW.replace("\n\n\n      function", "\n\n      function", 1)
        if alt in text:
            text = text.replace(alt, alt_new, 1)
        else:
            raise SystemExit("graph1 trend listeners patch miss")

    if g2_before in text:
        text = text.replace(g2_before, g2_after, 1)
    elif "insightTrendDirty" in text and text.count("insightTrendDirty") >= 2:
        pass
    else:
        raise SystemExit("graph2 trend listeners patch miss")

    # Monthly: remaining LISTENERS_BEFORE_GUARD (first / only leftover)
    if monthly_before in text:
        text = text.replace(monthly_before, monthly_after, 1)
    elif text.count("insightTrendDirty") < 3:
        raise SystemExit("monthly trend listeners still missing guard")

    if text.count("insightTrendDirty") < 3:
        raise SystemExit(
            f"expected 3 insightTrendDirty blocks, found {text.count('insightTrendDirty')}"
        )
    return text


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = inject_insight_diff_js(text)
    text = inject_expense_read(text)
    text = patch_insight_fill(text)
    text = patch_set_insight_tab(text)
    text = patch_trend_listeners(text)

    checks = [
        ("__INSIGHT_FILL_SCHED", "fill coalesce"),
        ("wantAnalyze", "pane skip"),
        ("insight:tabChanged", "tab event"),
        ("insightTrendDirty", "svg guard"),
        ("expenseSnapshotCache", "expense cache"),
        ("sumThroughMonthCache", "sumThroughMonth cache"),
    ]
    for needle, label in checks:
        if needle not in text:
            raise SystemExit(f"{label} missing after patch: {path} ({needle})")

    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> int:
    for path in PAGES:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_page(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
