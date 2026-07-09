#!/usr/bin/env python3
"""MRP Phase 1 — Monthly only: stop full multi-year vertical TW background render."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]

MRP_PHASE1_MARKER = "/* KPI-MRP-PHASE1 */"

DUPLICATE_IIFE_CLOSE = """      })();
      })();
    })();
    (function () {
      var rowsRoot = document.getElementById('annual-daily-rows');"""

FIXED_IIFE_CLOSE = """      })();
    })();
    (function () {
      var rowsRoot = document.getElementById('annual-daily-rows');"""

TW_BOOTSTRAP_V2_ANCHOR = """      /* KPI-MONTHLY-LOAD-PERF */
      /* KPI-MONTHLY-LOAD-PERF-2 */
      function scheduleMonthlyFullTwRender(cy) {"""

TW_BOOTSTRAP_MRP1 = f"""      /* KPI-MONTHLY-LOAD-PERF */
      /* KPI-MONTHLY-LOAD-PERF-2 */
      {MRP_PHASE1_MARKER}
      /* Monthly: 全年度バックグラウンド描画を廃止。表示年のみ（anchor-year-only）。 */
      window.__ensureMonthlyVerticalTwRendered = function () {{
        if (window.__monthlyVerticalTwPartialRendered) return;
        window.__monthlyVerticalTwPartialRendered = true;
        window.__monthlyVerticalTwBootstrapPending = false;
        var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        if (!Number.isFinite(cy)) cy = new Date().getFullYear();
        renderAnnualDailyTimeline(cy, {{ boundsHint: 'anchor-year-only', preserveScroll: true }});
      }};
      document.addEventListener('annual:focusBarStateChanged', function (ev) {{
        if (ev && ev.detail && ev.detail.expanded) {{
          window.__ensureMonthlyVerticalTwRendered();
        }}
      }});
      (function bootstrapMonthlyVerticalTw() {{
        var kick = function () {{
          if (window.__monthlyVerticalTwPartialRendered) return;
          window.__ensureMonthlyVerticalTwRendered();
        }};
        if (document.body.classList.contains('annual-focus-bar-expanded')) {{
          window.requestAnimationFrame(function () {{
            window.requestAnimationFrame(kick);
          }});
          return;
        }}
        window.__monthlyVerticalTwBootstrapPending = true;
        document.addEventListener('monthly:pageReady', function () {{
          window.requestAnimationFrame(kick);
        }}, {{ once: true }});
        if (typeof window.requestIdleCallback === 'function') {{
          window.requestIdleCallback(kick, {{ timeout: 900 }});
        }} else {{
          window.setTimeout(kick, 400);
        }}
      }})();"""

RENDER_GUARD_ANCHOR = """      function renderAnnualDailyTimeline(anchorYear, opts) {
        opts = opts || {};
        anchorYear = Number(anchorYear);"""

RENDER_GUARD_BLOCK = f"""      function renderAnnualDailyTimeline(anchorYear, opts) {{
        opts = opts || {{}};
        {MRP_PHASE1_MARKER}
        if (document.body.classList.contains('monthly-page') && !opts.boundsHint) {{
          opts.boundsHint = 'anchor-year-only';
        }}
        anchorYear = Number(anchorYear);"""


def repair_duplicate_iife_close(text: str) -> str:
    if DUPLICATE_IIFE_CLOSE in text:
        return text.replace(DUPLICATE_IIFE_CLOSE, FIXED_IIFE_CLOSE, 1)
    return text


def patch_page(path: Path) -> None:
    original = path.read_text(encoding="utf-8")
    text = repair_duplicate_iife_close(original)
    if MRP_PHASE1_MARKER in text:
        if text != original:
            path.write_text(text, encoding="utf-8")
            print(f"repaired duplicate IIFE close {path.relative_to(ROOT)}")
        else:
            print(f"skip (already applied) {path.relative_to(ROOT)}")
        return
    if TW_BOOTSTRAP_V2_ANCHOR not in text:
        raise SystemExit(f"MRP phase1 bootstrap anchor miss: {path}")
    if RENDER_GUARD_ANCHOR not in text:
        raise SystemExit(f"MRP phase1 render guard anchor miss: {path}")
    # Replace from anchor through end of bootstrap IIFE (before closing })(); of outer block)
    start = text.index(TW_BOOTSTRAP_V2_ANCHOR)
    end_marker = "    })();\n    (function () {\n      var rowsRoot = document.getElementById('annual-daily-rows');"
    if end_marker not in text[start:]:
        raise SystemExit(f"MRP phase1 bootstrap end anchor miss: {path}")
    end = text.index(end_marker, start)
    text = text[:start] + TW_BOOTSTRAP_MRP1 + "\n" + text[end:]
    text = text.replace(RENDER_GUARD_ANCHOR, RENDER_GUARD_BLOCK, 1)
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
