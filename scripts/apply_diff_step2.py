#!/usr/bin/env python3
"""Difference Step 2 — Daily FW + Graph popover diff severity."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from apply_daily_overlay_kpi import inject_overlay_kpi_block  # noqa: E402
from diff_step2_client import (  # noqa: E402
    DIFF_STEP2_MARKER,
    GRAPH_DIFF_CSS_ANCHOR,
    GRAPH_DIFF_CSS_BLOCK,
    GRAPH_OFFICE_DIFF_CSS_ANCHOR,
    GRAPH_OFFICE_DIFF_CSS_BLOCK,
    OVERLAY_DIFF_CSS_ANCHOR,
    OVERLAY_DIFF_CSS_BLOCK,
)
from focus_bar_graph_client import REFRESH_GRAPH_NEW  # noqa: E402

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]

REFRESH_GRAPH_PRE_STEP2 = """      function refreshGraphContent() {
        var row = getFocusedRow();
        var iso = resolveGraphFocusedIso(row);
        panel.classList.remove('annual-graph-popover--win', 'annual-graph-popover--lose', 'annual-graph-popover--neutral');

        if (!iso) {
          panel.classList.add('annual-graph-popover--neutral');
          valDate.textContent = '—';
          valAch.textContent = '—';
          valTarget.textContent = '—';
          valActual.textContent = '—';
          valDiff.textContent = '—';
          setGraphBarFromAchievementPercent(NaN);
          return;
        }

        var compute =
          typeof window.__computeTwMetricsForIso === 'function'
            ? window.__computeTwMetricsForIso
            : null;
        var m = compute ? compute(iso) : null;
        var g = graphMetricsForMode(m, mode);

        valDate.textContent = row ? getFocusedDateText(row) : iso;

        if (!g || !g.hasData) {
          panel.classList.add('annual-graph-popover--neutral');
          valAch.textContent = '—';
          valTarget.textContent =
            g && Number.isFinite(g.target) ? fmtMoney(g.target) : '—';
          valActual.textContent =
            g && Number.isFinite(g.sales) ? fmtMoney(g.sales) : '—';
          valDiff.textContent = '—';
          setGraphBarFromAchievementPercent(NaN);
          return;
        }

        var target = g.target;
        var sales = g.sales;
        var diff = sales - target;
        var achValue = target > 0 ? (sales / target) * 100 : 0;
        setGraphBarFromAchievementPercent(achValue);
        panel.classList.add(diff >= 0 ? 'annual-graph-popover--win' : 'annual-graph-popover--lose');
        valAch.textContent = formatAchPercent(achValue);
        valTarget.textContent = fmtMoney(target);
        valActual.textContent = fmtMoney(sales);
        valDiff.textContent = formatSignedDiff(diff);
      }"""


def patch_overlay_css(text: str) -> str:
    if DIFF_STEP2_MARKER in text and "daily-overlay__daily-value-box.tw-diff--win" in text:
        return text
    if OVERLAY_DIFF_CSS_ANCHOR not in text:
        if OVERLAY_DIFF_CSS_BLOCK.split(DIFF_STEP2_MARKER)[0].strip() in text:
            return text
        raise SystemExit("daily overlay diff CSS anchor miss")
    return text.replace(OVERLAY_DIFF_CSS_ANCHOR, OVERLAY_DIFF_CSS_BLOCK, 1)


def patch_graph_css(text: str) -> str:
    if "annual-graph-popover__val-diff.tw-diff--win" in text:
        text = text
    elif GRAPH_DIFF_CSS_ANCHOR in text:
        text = text.replace(GRAPH_DIFF_CSS_ANCHOR, GRAPH_DIFF_CSS_BLOCK, 1)
    else:
        raise SystemExit("graph popover diff CSS anchor miss")
    if ".office-mode .annual-graph-popover__val-diff.tw-diff--win" in text:
        return text
    if GRAPH_OFFICE_DIFF_CSS_ANCHOR not in text:
        raise SystemExit("graph popover office diff CSS anchor miss")
    return text.replace(GRAPH_OFFICE_DIFF_CSS_ANCHOR, GRAPH_OFFICE_DIFF_CSS_BLOCK, 1)


def patch_graph_refresh(text: str) -> str:
    if "applyGraphTwDiffClass(valDiff" in text:
        return text
    if REFRESH_GRAPH_PRE_STEP2 in text:
        return text.replace(REFRESH_GRAPH_PRE_STEP2, REFRESH_GRAPH_NEW, 1)
    if REFRESH_GRAPH_NEW in text:
        return text
    raise SystemExit("refreshGraphContent step2 patch miss")


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = patch_overlay_css(text)
    text = patch_graph_css(text)
    text = inject_overlay_kpi_block(text)
    text = patch_graph_refresh(text)
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
