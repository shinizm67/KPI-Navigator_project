#!/usr/bin/env python3
"""Insight 4/4 — Graph → Monthly 累計折れ線の実データ化 + Insight 内日付追従."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from apply_focus_tw_metrics import patch_page as patch_focus_tw  # noqa: E402
from insight_diff_client import (  # noqa: E402
    INSIGHT_DIFF_JS_END,
    INSIGHT_DIFF_JS_MARKER,
    INSIGHT_FILL_NEW,
    INSIGHT_FILL_OLD,
    INSIGHT_OVERLAY_IIFE,
    insight_diff_js,
)
from insight_trend_monthly_client import (  # noqa: E402
    MARKER_BUILD_STORE,
    MARKER_RESOLVE_ISO,
    TREND_BUILD_STORE_NEW,
    TREND_BUILD_STORE_OLD,
    TREND_GET_FOCUS_NEW,
    TREND_GET_FOCUS_OLD,
    TREND_LISTENERS_NEW,
    TREND_LISTENERS_OLD,
    TREND_RENDER_PAYLOAD_NEW,
    TREND_RENDER_PAYLOAD_OLD,
)

PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]


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


def patch_insight_fill(text: str) -> str:
    if "__INSIGHT_SELECTED_ISO" in text and "insight:dateChanged" in text:
        return text
    if INSIGHT_FILL_OLD not in text and INSIGHT_FILL_NEW.split("window.__INSIGHT_SELECTED_ISO")[0] not in text:
        # already patched via INSIGHT_FILL_NEW from prior apply
        if "window.__INSIGHT_SELECTED_ISO = iso" in text:
            return text
        raise SystemExit("insight overlay fill() patch miss")
    if INSIGHT_FILL_OLD in text:
        return text.replace(INSIGHT_FILL_OLD, INSIGHT_FILL_NEW, 1)
    # re-apply fill block when insight_diff was re-injected but fill still old
    old = """      function fill(iso) {
        iso = iso || resolveIso();
        if (dateBtnEl) dateBtnEl.textContent = fmtDate(iso);
        if (todayBtnEl) todayBtnEl.hidden = iso === getTodayIso();
        if (dateInputEl) dateInputEl.value = iso;
        try {
          if (typeof window.renderInsightTwDiffs === 'function') {
            window.renderInsightTwDiffs(iso);
          }
        } catch (_insightDiffErr) {}
      }"""
    if old in text:
        return text.replace(old, INSIGHT_FILL_NEW, 1)
    return text


def patch_monthly_trend(text: str) -> str:
    if MARKER_RESOLVE_ISO in text and MARKER_BUILD_STORE in text:
        if TREND_RENDER_PAYLOAD_NEW in text and "insight:dateChanged" in text:
            return text
    if TREND_GET_FOCUS_OLD not in text:
        if MARKER_RESOLVE_ISO in text:
            pass
        else:
            raise SystemExit("monthly trend getFocusYearMonth patch miss")
    else:
        text = text.replace(TREND_GET_FOCUS_OLD, TREND_GET_FOCUS_NEW, 1)
    if TREND_BUILD_STORE_OLD in text:
        text = text.replace(TREND_BUILD_STORE_OLD, TREND_BUILD_STORE_NEW, 1)
    elif MARKER_BUILD_STORE not in text:
        raise SystemExit("monthly trend buildStorePayload patch miss")
    if TREND_RENDER_PAYLOAD_OLD in text:
        text = text.replace(TREND_RENDER_PAYLOAD_OLD, TREND_RENDER_PAYLOAD_NEW, 1)
    elif TREND_RENDER_PAYLOAD_NEW not in text:
        raise SystemExit("monthly trend render payload patch miss")
    if TREND_LISTENERS_OLD in text:
        text = text.replace(TREND_LISTENERS_OLD, TREND_LISTENERS_NEW, 1)
    elif "insight:dateChanged" not in text:
        raise SystemExit("monthly trend listeners patch miss")
    return text


def patch_page(path: Path) -> None:
    patch_focus_tw(path)
    text = path.read_text(encoding="utf-8")
    text = inject_insight_diff_js(text)
    text = patch_insight_fill(text)
    text = patch_monthly_trend(text)
    if "__buildMonthlyCumulativeTrendPayload" not in text:
        raise SystemExit(f"buildMonthlyCumulativeTrendPayload missing: {path}")
    if MARKER_BUILD_STORE not in text:
        raise SystemExit(f"trend buildStorePayload missing: {path}")
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
