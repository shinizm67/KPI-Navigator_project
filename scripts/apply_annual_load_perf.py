#!/usr/bin/env python3
"""Annual page load — dedupe cockpit sync, fix Target Sales layout flash, defer TW."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

MARKER = "/* KPI-ANNUAL-LOAD-PERF */"

CSS_GROUP_OLD = """    .annual-target-sales-group {
      position: absolute;
      left: 0;
      transform: none;
      top: 21px;
      z-index: 2;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 6px;
    }"""

CSS_GROUP_NEW = """    .annual-target-sales-group {
      position: absolute;
      left: 0;
      transform: none;
      top: 21px;
      z-index: 2;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 6px;
      opacity: 0;
    }
    .annual-target-sales-group.annual-target-sales-group--positioned {
      opacity: 1;
    }"""

PLACE_FN_OLD = """        targetGroup.style.left = left + 'px';
      }

      var langJa = document.documentElement.lang === 'ja';"""

PLACE_FN_NEW = """        targetGroup.style.left = left + 'px';
        targetGroup.classList.add('annual-target-sales-group--positioned');
      }

      var langJa = document.documentElement.lang === 'ja';"""

PLACE_LISTENERS_SINGLE_OLD = """      placeTargetSalesGroup();
      window.addEventListener('resize', placeTargetSalesGroup);
      requestAnimationFrame(placeTargetSalesGroup);
      document.addEventListener('annual:timelineRowsRendered', placeTargetSalesGroup);
      document.addEventListener('kpi:readSurfacesRefresh', function () {
        requestAnimationFrame(placeTargetSalesGroup);
      });
      setTimeout(placeTargetSalesGroup, 150);"""

PLACE_LISTENERS_DUP_OLD = """      placeTargetSalesGroup();
      window.addEventListener('resize', placeTargetSalesGroup);
      requestAnimationFrame(placeTargetSalesGroup);
      document.addEventListener('annual:timelineRowsRendered', placeTargetSalesGroup);
      document.addEventListener('kpi:readSurfacesRefresh', function () {
        requestAnimationFrame(placeTargetSalesGroup);
      });
      setTimeout(placeTargetSalesGroup, 150);
      document.addEventListener('annual:timelineRowsRendered', placeTargetSalesGroup);
      document.addEventListener('kpi:readSurfacesRefresh', function () {
        requestAnimationFrame(placeTargetSalesGroup);
      });
      setTimeout(placeTargetSalesGroup, 150);"""

PLACE_LISTENERS_NEW = f"""      {MARKER}
      var __placeTargetSalesTimer = null;
      function schedulePlaceTargetSalesGroup() {{
        if (__placeTargetSalesTimer != null) window.clearTimeout(__placeTargetSalesTimer);
        __placeTargetSalesTimer = window.setTimeout(function () {{
          __placeTargetSalesTimer = null;
          window.requestAnimationFrame(placeTargetSalesGroup);
        }}, 0);
      }}
      schedulePlaceTargetSalesGroup();
      window.addEventListener('resize', schedulePlaceTargetSalesGroup);
      document.addEventListener('annual:timelineRowsRendered', schedulePlaceTargetSalesGroup);
      document.addEventListener('kpi:readSurfacesRefresh', schedulePlaceTargetSalesGroup);
      document.addEventListener('annual:calendarYearChanged', schedulePlaceTargetSalesGroup);
      setTimeout(schedulePlaceTargetSalesGroup, 150);"""

EARLY_SYNC_OLD = """    (function () {
      if (window.__ANNUAL_UI && typeof window.__ANNUAL_UI.syncCockpitForCalendarYear === 'function') {
        window.__ANNUAL_UI.syncCockpitForCalendarYear();
      }
    })();
    (function () {
      /** 達成率のみ: 100%以上は黄、50〜100%は10%刻みでアンバー→赤、50%未満は濃い赤 */"""

EARLY_SYNC_NEW = """    (function () {
      /** 達成率のみ: 100%以上は黄、50〜100%は10%刻みでアンバー→赤、50%未満は濃い赤 */"""

EARLY_SYNC_EN_OLD = """    (function () {
      if (window.__ANNUAL_UI && typeof window.__ANNUAL_UI.syncCockpitForCalendarYear === 'function') {
        window.__ANNUAL_UI.syncCockpitForCalendarYear();
      }
    })();
    (function () {
      /** Achievement markers only: yellow at 100%+, amber→red in 10% steps to 50%, deep red below */"""

SYNC_COCKPIT_FN_OLD = """        function syncCockpitForCalendarYear(explicitYear) {
          var year = resolveCalendarYear(explicitYear);"""

SYNC_COCKPIT_FN_NEW = """        function syncCockpitForCalendarYearCore(explicitYear) {
          var year = resolveCalendarYear(explicitYear);"""

SYNC_COCKPIT_WRAP_OLD = """          if (typeof window.refreshArea1Cockpit === 'function') {
            window.refreshArea1Cockpit();
          }
        }

        window.__ANNUAL_UI = window.__ANNUAL_UI || {};
        window.__ANNUAL_UI.syncCockpitForCalendarYear = syncCockpitForCalendarYear;"""

SYNC_COCKPIT_WRAP_NEW = """          if (typeof window.refreshArea1Cockpit === 'function') {
            window.refreshArea1Cockpit();
          }
        }

        var __syncCockpitTimer = null;
        var __syncCockpitPendingYear;
        function syncCockpitForCalendarYear(explicitYear) {
          if (arguments.length > 0) __syncCockpitPendingYear = explicitYear;
          if (__syncCockpitTimer != null) window.clearTimeout(__syncCockpitTimer);
          __syncCockpitTimer = window.setTimeout(function () {
            __syncCockpitTimer = null;
            var pending = __syncCockpitPendingYear;
            __syncCockpitPendingYear = undefined;
            syncCockpitForCalendarYearCore(pending);
          }, 0);
        }

        window.__ANNUAL_UI = window.__ANNUAL_UI || {};
        window.__ANNUAL_UI.syncCockpitForCalendarYear = syncCockpitForCalendarYear;"""

COCKPIT_YEAR_LISTENER_OLD = """        document.addEventListener('annual:calendarYearChanged', function () {
          syncCockpitForCalendarYear();
        });"""

COCKPIT_YEAR_LISTENER_NEW = """        document.addEventListener('annual:calendarYearChanged', function () {
          window.requestAnimationFrame(function () {
            syncCockpitForCalendarYear();
          });
        });"""

COCKPIT_REFRESH_OLD = """      function onArea1CockpitRefresh() {
        refreshArea1Cockpit(resolveArea1Iso());
      }
      onArea1CockpitRefresh();
      document.addEventListener('annual:dailyDateChanged', onArea1CockpitRefresh);"""

COCKPIT_REFRESH_NEW = """      var __area1CockpitRefreshTimer = null;
      function onArea1CockpitRefresh() {
        if (__area1CockpitRefreshTimer != null) window.clearTimeout(__area1CockpitRefreshTimer);
        __area1CockpitRefreshTimer = window.setTimeout(function () {
          __area1CockpitRefreshTimer = null;
          refreshArea1Cockpit(resolveArea1Iso());
        }, 0);
      }
      /* Initial refresh: scheduleInitialCockpitSync after refreshArea1Cockpit exists. */
      document.addEventListener('annual:dailyDateChanged', onArea1CockpitRefresh);"""

INITIAL_TW_OLD = """      renderAnnualDailyTimeline(window.__ANNUAL_DATA.calendarYear);
    })();"""

INITIAL_TW_NEW = """      window.requestAnimationFrame(function () {
        window.requestAnimationFrame(function () {
          renderAnnualDailyTimeline(window.__ANNUAL_DATA.calendarYear);
        });
      });
    })();"""


def _apply(text: str, old: str, new: str, label: str) -> str:
    if old in text:
        return text.replace(old, new, 1)
    if MARKER in text and label in (
        "place listeners",
        "initial tw",
        "cockpit refresh",
    ):
        return text
    if "syncCockpitForCalendarYearCore" in text and label in (
        "sync cockpit fn",
        "sync cockpit wrap",
    ):
        return text
    if "annual-target-sales-group--positioned" in text and label == "css group":
        return text
    if "annual-target-sales-group--positioned" in text and label == "place fn":
        return text
    if "schedulePlaceTargetSalesGroup" in text and label == "place listeners":
        return text
    if "Initial refresh: scheduleInitialCockpitSync" in text and label == "cockpit refresh":
        return text
    if label == "early sync" and EARLY_SYNC_OLD not in text and EARLY_SYNC_EN_OLD not in text:
        return text
    raise SystemExit(f"{label} patch miss")


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = _apply(text, CSS_GROUP_OLD, CSS_GROUP_NEW, "css group")
    text = _apply(text, PLACE_FN_OLD, PLACE_FN_NEW, "place fn")
    if PLACE_LISTENERS_DUP_OLD in text:
        text = text.replace(PLACE_LISTENERS_DUP_OLD, PLACE_LISTENERS_NEW, 1)
    else:
        text = _apply(text, PLACE_LISTENERS_SINGLE_OLD, PLACE_LISTENERS_NEW, "place listeners")
    if EARLY_SYNC_OLD in text:
        text = text.replace(EARLY_SYNC_OLD, EARLY_SYNC_NEW, 1)
    elif EARLY_SYNC_EN_OLD in text:
        text = text.replace(EARLY_SYNC_EN_OLD, EARLY_SYNC_NEW.replace(
            "達成率のみ: 100%以上は黄、50〜100%は10%刻みでアンバー→赤、50%未満は濃い赤",
            "Achievement markers only: yellow at 100%+, amber→red in 10% steps to 50%, deep red below",
        ), 1)
    text = _apply(text, SYNC_COCKPIT_FN_OLD, SYNC_COCKPIT_FN_NEW, "sync cockpit fn")
    text = _apply(text, SYNC_COCKPIT_WRAP_OLD, SYNC_COCKPIT_WRAP_NEW, "sync cockpit wrap")
    if COCKPIT_YEAR_LISTENER_OLD in text:
        text = text.replace(COCKPIT_YEAR_LISTENER_OLD, COCKPIT_YEAR_LISTENER_NEW, 1)
    text = _apply(text, COCKPIT_REFRESH_OLD, COCKPIT_REFRESH_NEW, "cockpit refresh")
    text = _apply(text, INITIAL_TW_OLD, INITIAL_TW_NEW, "initial tw")
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
