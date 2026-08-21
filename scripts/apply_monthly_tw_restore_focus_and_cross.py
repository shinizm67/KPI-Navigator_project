#!/usr/bin/env python3
"""Step Z: restore Focus Bar copy, allow month-cross, stop annualNav PUT on scroll."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "zh-tw/app/monthly/index.html",
]


def replace_once(text: str, old: str, new: str, label: str, path: Path) -> str:
    cnt = text.count(old)
    if cnt == 0:
        if new in text:
            print(f"  skip {label} (already) {path.relative_to(ROOT)}")
            return text
        raise SystemExit(f"  ERROR {label} not found: {path.relative_to(ROOT)}")
    if cnt != 1:
        raise SystemExit(f"  ERROR {label} found {cnt}: {path.relative_to(ROOT)}")
    print(f"  patch {label} {path.relative_to(ROOT)}")
    return text.replace(old, new, 1)


FILL_OLD = """      pointer-events: none;
      background: transparent;
    }
    .office-mode .monthly-vfocus-fill {
      background: transparent;
    }"""

FILL_NEW = """      pointer-events: none;
      background: #000;
      isolation: isolate;
    }
    .office-mode .monthly-vfocus-fill {
      background: #2a2a2a;
    }"""

LANES_OLD = """    .monthly-vfocus-lanes {
      display: flex;
      flex-direction: row;
      align-items: flex-start;
      justify-content: flex-start;
      gap: 0;
      width: 300%;
      box-sizing: border-box;
      transform: translateX(-33.333333%);
      visibility: hidden;
    }"""

LANES_NEW = """    .monthly-vfocus-lanes {
      display: flex;
      flex-direction: row;
      align-items: flex-start;
      justify-content: flex-start;
      gap: 0;
      width: 300%;
      box-sizing: border-box;
      transform: translateX(-33.333333%);
    }"""

NAV_OLD = """          if (src !== 'focus-sync' && src !== 'monthly-vfocus-nav') persistStore();
          if (window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily) {
            window.__ANNUAL_DATA.daily.selectedDate = iso;
          }
          try {
            gw().setJson(SELECTED_DATE_KEY, {
              calendarYear: isoYear(iso),
              selectedIso: iso,
            });
          } catch (_e) {}"""

NAV_NEW = """          if (src !== 'focus-sync' && src !== 'monthly-vfocus-nav') persistStore();
          if (window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily) {
            window.__ANNUAL_DATA.daily.selectedDate = iso;
          }
          /* 横スクロール中に annualNav を書くと store.php へ全ストアPUTが走る */
          if (src !== 'focus-sync' && src !== 'monthly-vfocus-nav') {
            try {
              gw().setJson(SELECTED_DATE_KEY, {
                calendarYear: isoYear(iso),
                selectedIso: iso,
              });
            } catch (_e) {}
          }"""

SETTLE_OLD = """      function settleMonthlyScroll() {
        snapTimer = 0;
        if (settleSkip > 0) return;
        if (window.__monthlyTwColumnsBusy) return;

        var maxScroll = Math.max(0, scrollEl.scrollWidth - scrollEl.clientWidth);
        var edgeLocked = __monthlyEdgeLockUntil && Date.now() < __monthlyEdgeLockUntil;"""

SETTLE_NEW = """      function settleMonthlyScroll() {
        snapTimer = 0;
        if (settleSkip > 0) return;

        var maxScroll = Math.max(0, scrollEl.scrollWidth - scrollEl.clientWidth);
        var edgeLocked = __monthlyEdgeLockUntil && Date.now() < __monthlyEdgeLockUntil;"""

REBUILD_OLD = """        window.__monthlyTwColumnsBusy = true;
        __monthlyEdgeLockUntil = Date.now() + 700;
        __vfocusLastIdx = null;"""

REBUILD_NEW = """        window.__monthlyTwColumnsBusy = true;
        __vfocusLastIdx = null;"""

CROSS_OLD = """      function crossMonthByEdge(dir) {
        var next = clampYearMonth(state.year, state.month0 + dir);
        if (next.year === state.year && next.month0 === state.month0) return false;
        state.year = next.year;
        state.month0 = next.month0;"""

CROSS_NEW = """      function crossMonthByEdge(dir) {
        var next = clampYearMonth(state.year, state.month0 + dir);
        if (next.year === state.year && next.month0 === state.month0) return false;
        state.year = next.year;
        state.month0 = next.month0;
        __monthlyEdgeLockUntil = Date.now() + 900;"""


def main() -> int:
    for path in TARGETS:
        text = path.read_text(encoding="utf-8")
        text = replace_once(text, FILL_OLD, FILL_NEW, "fill", path)
        text = replace_once(text, LANES_OLD, LANES_NEW, "lanes", path)
        text = replace_once(text, NAV_OLD, NAV_NEW, "nav-skip", path)
        text = replace_once(text, SETTLE_OLD, SETTLE_NEW, "settle", path)
        text = replace_once(text, REBUILD_OLD, REBUILD_NEW, "rebuild-lock", path)
        text = replace_once(text, CROSS_OLD, CROSS_NEW, "cross-lock", path)
        path.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
