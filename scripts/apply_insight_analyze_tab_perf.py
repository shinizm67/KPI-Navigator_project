#!/usr/bin/env python3
"""Insight Analyze/Graph タブ切替: 先にタブ表示、重い patch は遅延・分割."""

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
    INSIGHT_OVERLAY_IIFE,
    INSIGHT_SET_TAB_NEW,
    insight_diff_js,
)

PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

# Current sync tab-render block (from date-nav perf)
SET_TAB_SYNC_TAIL = """        if (which === 'analyze' || which === 'graph') {
          try {
            if (window.__INSIGHT_SELECTED_ISO && typeof window.renderInsightTwDiffs === 'function') {
              window.renderInsightTwDiffs(window.__INSIGHT_SELECTED_ISO);
            }
          } catch (_insightTabErr) {}
        }
        try {
          document.dispatchEvent(new CustomEvent('insight:tabChanged', { detail: { tab: which } }));
        } catch (_insightTabEvErr) {}
      }"""

SET_TAB_HEAD = """      function setInsightTab(which) {
        which = which || 'summary';
        if (paneSummary) paneSummary.hidden = which !== 'summary';
        if (paneAnalyze) paneAnalyze.hidden = which !== 'analyze';
        if (paneGraph) paneGraph.hidden = which !== 'graph';
        if (tabSummary) tabSummary.classList.toggle('is-active', which === 'summary');
        if (tabAnalyze) tabAnalyze.classList.toggle('is-active', which === 'analyze');
        if (tabGraph) tabGraph.classList.toggle('is-active', which === 'graph');
        if (titleEl) titleEl.textContent = insightTabTitles[which] || insightTabTitles.summary;
        if (insightScroll) insightScroll.scrollTop = 0;
        updateInsightJumpHrefs();
"""


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


def patch_set_insight_tab(text: str) -> str:
    if "__INSIGHT_TAB_PENDING" in text and "mode: pendingTab" in text:
        return text
    old = SET_TAB_HEAD + SET_TAB_SYNC_TAIL
    if old not in text:
        raise SystemExit("setInsightTab sync block miss")
    return text.replace(old, INSIGHT_SET_TAB_NEW, 1)


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = inject_insight_diff_js(text)
    text = patch_set_insight_tab(text)
    for needle in (
        "runInsightAnalyzePatches",
        "__INSIGHT_TAB_PENDING",
        "__INSIGHT_PANE_CACHE",
        "mode: pendingTab",
        "mode === 'analyze'",
    ):
        if needle not in text:
            raise SystemExit(f"missing {needle}: {path}")
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
