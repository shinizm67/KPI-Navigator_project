#!/usr/bin/env python3
"""P0 remainder: Focus Bar / Table Window multi-year timeline scroll."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from focus_bar_timeline_scroll_client import TIMELINE_CSS, render_timeline_js  # noqa: E402

TARGETS = [
    (ROOT / "app/annual/index.html", True),
    (ROOT / "en/app/annual/index.html", True),
    (ROOT / "app/monthly/index.html", False),
    (ROOT / "en/app/monthly/index.html", False),
]

RENDER_BLOCK_RE = re.compile(
    r"      function renderAnnualDailyTable\(year\) \{.*?"
    r"      renderAnnualDailyTable\(window\.__ANNUAL_DATA\.calendarYear\);\n",
    re.DOTALL,
)

# Monthly pages had an extra salesMapChanged listener whose body also called
# renderAnnualDailyTable; the non-greedy RENDER_BLOCK_RE stopped there and left
# a broken `});` plus duplicate tail after timeline injection.
MONTHLY_RENDER_TAIL_RE = re.compile(
    r"      renderAnnualDailyTimeline\(window\.__ANNUAL_DATA\.calendarYear\);\n"
    r"      \}\);\n"
    r"      document\.addEventListener\('annual:salesMapChanged', function \(ev\) \{.*?"
    r"      renderAnnualDailyTable\(window\.__ANNUAL_DATA\.calendarYear\);\n"
    r"    \}\)\(\);\n",
    re.DOTALL,
)

MONTHLY_RENDER_BLOCK_RE = re.compile(
    r"      function renderAnnualDailyTable\(year\) \{.*?"
    r"      renderAnnualDailyTable\(window\.__ANNUAL_DATA\.calendarYear\);\n"
    r"    \}\)\(\);\n",
    re.DOTALL,
)

SYNC_FOCUS_OLD = """      function syncDailyDateFromFocusedRowForIndex(idx) {
        var rows = document.querySelectorAll('#annual-daily-rows .annual-daily-row');
        if (!rows || !rows.length) return;
        if (idx < 0 || idx >= rows.length) return;
        var iso = rows[idx].getAttribute('data-iso-date');
        if (!iso) return;
        if (window.__ANNUAL_UI && typeof window.__ANNUAL_UI.setDailyDateByISO === 'function') {
          window.__ANNUAL_UI.setDailyDateByISO(iso, 'focus-sync');
        }
      }"""

SYNC_FOCUS_NEW = """      function syncCalendarYearFromIso(iso) {
        if (!iso || iso.length < 4) return;
        var y = Number(iso.slice(0, 4));
        if (!Number.isFinite(y)) return;
        if (
          window.__ANNUAL_UI &&
          typeof window.__ANNUAL_UI.setCalendarYearSilent === 'function'
        ) {
          window.__ANNUAL_UI.setCalendarYearSilent(y);
        }
      }
      function syncDailyDateFromFocusedRowForIndex(idx) {
        var rows = document.querySelectorAll('#annual-daily-rows .annual-daily-row');
        if (!rows || !rows.length) return;
        if (idx < 0 || idx >= rows.length) return;
        var iso = rows[idx].getAttribute('data-iso-date');
        if (!iso) return;
        syncCalendarYearFromIso(iso);
        if (window.__ANNUAL_UI && typeof window.__ANNUAL_UI.setDailyDateByISO === 'function') {
          window.__ANNUAL_UI.setDailyDateByISO(iso, 'focus-sync');
        }
      }"""

RENDER_YEAR_OLD = """        document.dispatchEvent(
          new CustomEvent('annual:calendarYearChanged', { detail: { year: currentYear } })
        );"""

RENDER_YEAR_NEW = """        document.dispatchEvent(
          new CustomEvent('annual:calendarYearChanged', {
            detail: { year: currentYear, skipTableRender: true },
          })
        );"""

SET_CAL_YEAR_OLD = """      window.__ANNUAL_UI.setCalendarYear = function (y) {
        y = Number(y);
        if (!Number.isFinite(y)) return;
        y = Math.max(minYear, Math.min(maxYear, Math.round(y)));
        if (currentYear === y) return;
        currentYear = y;
        renderYear();
      };
      renderYear();"""

SET_CAL_YEAR_NEW = """      window.__ANNUAL_UI.setCalendarYear = function (y) {
        y = Number(y);
        if (!Number.isFinite(y)) return;
        y = Math.max(minYear, Math.min(maxYear, Math.round(y)));
        if (currentYear === y) return;
        currentYear = y;
        renderYear();
      };
      window.__ANNUAL_UI.setCalendarYearSilent = function (y) {
        y = Number(y);
        if (!Number.isFinite(y)) return;
        y = Math.max(minYear, Math.min(maxYear, Math.round(y)));
        if (currentYear === y) return;
        currentYear = y;
        yearBtn.textContent = String(currentYear);
        window.__ANNUAL_DATA = window.__ANNUAL_DATA || {};
        window.__ANNUAL_DATA.calendarYear = currentYear;
        buildYearMenu();
        document.dispatchEvent(
          new CustomEvent('annual:calendarYearChanged', {
            detail: { year: currentYear, skipTableRender: true, source: 'focus-sync' },
          })
        );
        syncAnnualNavToStorage();
      };
      renderYear();"""

SHIFT_YEAR_OLD = """      document.addEventListener('annual:calendarYearChanged', function (ev) {
        var y = ev.detail && ev.detail.year;
        if (y == null) return;
        shiftDailyDateToCalendarYear(Number(y));
      });"""

SHIFT_YEAR_NEW = """      document.addEventListener('annual:calendarYearChanged', function (ev) {
        var y = ev.detail && ev.detail.year;
        if (y == null) return;
        if (ev.detail && ev.detail.source === 'focus-sync') return;
        shiftDailyDateToCalendarYear(Number(y));
      });"""

GET_BOUNDS_OLD = """      function getJumpYearBounds() {
        var data = window.__ANNUAL_DATA || {};
        var daily = data.daily || {};
        var map = daily.targetSalesByDate || {};
        var minYear = null;
        Object.keys(map).forEach(function (k) {
          var m = /^(\\d{4})-\\d{2}-\\d{2}$/.exec(String(k));
          if (!m) return;
          var y = Number(m[1]);
          if (!Number.isFinite(y)) return;
          if (minYear == null || y < minYear) minYear = y;
        });
        if (minYear == null) {
          var cur = parseISODateLocal(daily.selectedDate);
          minYear = cur ? cur.getFullYear() : new Date().getFullYear();
        }
        var maxYear = new Date().getFullYear() + 5;
        if (minYear > maxYear) minYear = maxYear;
        return { minYear: minYear, maxYear: maxYear };
      }"""

GET_BOUNDS_NEW = """      function getJumpYearBounds() {
        var data = window.__ANNUAL_DATA || {};
        var daily = data.daily || {};
        var map = daily.targetSalesByDate || {};
        var minYear = null;
        var maxYear = null;
        function considerYear(y) {
          y = Number(y);
          if (!Number.isFinite(y)) return;
          if (minYear == null || y < minYear) minYear = y;
          if (maxYear == null || y > maxYear) maxYear = y;
        }
        if (window.KpiYearStore) {
          KpiYearStore.listYearsWithData().forEach(considerYear);
          considerYear(KpiYearStore.getOperatingYear());
        }
        Object.keys(map).forEach(function (k) {
          var m = /^(\\d{4})-\\d{2}-\\d{2}$/.exec(String(k));
          if (!m) return;
          considerYear(Number(m[1]));
        });
        if (minYear == null) {
          var cur = parseISODateLocal(daily.selectedDate);
          minYear = cur ? cur.getFullYear() : new Date().getFullYear();
        }
        if (maxYear == null) maxYear = new Date().getFullYear();
        maxYear = Math.max(maxYear, new Date().getFullYear() + 5);
        if (minYear > maxYear) minYear = maxYear;
        return { minYear: minYear, maxYear: maxYear };
      }"""

APPLY_SEL_OLD = """        if (window.__ANNUAL_UI && typeof window.__ANNUAL_UI.syncAnnualNavToStorage === 'function') {
          window.__ANNUAL_UI.syncAnnualNavToStorage();
        }
        return true;
      }"""

APPLY_SEL_NEW = """        if (window.KpiYearStore && typeof KpiYearStore.setSelectedDate === 'function') {
          KpiYearStore.setSelectedDate(iso, source || 'annual-ui');
        }
        if (window.__ANNUAL_UI && typeof window.__ANNUAL_UI.syncAnnualNavToStorage === 'function') {
          window.__ANNUAL_UI.syncAnnualNavToStorage();
        }
        return true;
      }"""

INIT_SEL_OLD = """      var nowInit = new Date();
      var initialDate = new Date(nowInit.getFullYear(), nowInit.getMonth(), nowInit.getDate());
      applyDailySelection(initialDate, 'initial', { skipJumpGuard: true });"""

INIT_SEL_NEW = """      var nowInit = new Date();
      var initialDate = new Date(nowInit.getFullYear(), nowInit.getMonth(), nowInit.getDate());
      if (window.KpiYearStore && typeof KpiYearStore.getSelectedDate === 'function') {
        var storeIso = KpiYearStore.getSelectedDate();
        var storeDate = storeIso ? parseISODateLocal(storeIso) : null;
        if (storeDate) initialDate = storeDate;
      }
      applyDailySelection(initialDate, 'initial', { skipJumpGuard: true });"""

APPLY_SEL_NEW_MONTHLY = """        if (window.KpiYearStore && typeof KpiYearStore.setSelectedDate === 'function') {
          KpiYearStore.setSelectedDate(iso, source || 'annual-ui');
        }
        return true;
      }"""

APPLY_SEL_OLD_MONTHLY = """        document.dispatchEvent(
          new CustomEvent('annual:dailyDateChanged', {
            detail: { isoDate: iso, date: d, targetSales: target, source: source || 'selection' }
          })
        );
        return true;
      }"""

SET_CAL_YEAR_NEW_MONTHLY = """      window.__ANNUAL_UI.setCalendarYear = function (y) {
        y = Number(y);
        if (!Number.isFinite(y)) return;
        y = Math.max(minYear, Math.min(maxYear, Math.round(y)));
        if (currentYear === y) return;
        currentYear = y;
        renderYear();
      };
      window.__ANNUAL_UI.setCalendarYearSilent = function (y) {
        y = Number(y);
        if (!Number.isFinite(y)) return;
        y = Math.max(minYear, Math.min(maxYear, Math.round(y)));
        if (currentYear === y) return;
        currentYear = y;
        yearBtn.textContent = String(currentYear);
        window.__ANNUAL_DATA = window.__ANNUAL_DATA || {};
        window.__ANNUAL_DATA.calendarYear = currentYear;
        buildYearMenu();
        document.dispatchEvent(
          new CustomEvent('annual:calendarYearChanged', {
            detail: { year: currentYear, skipTableRender: true, source: 'focus-sync' },
          })
        );
      };
      renderYear();"""


def apply_optional(text: str, old: str, new: str, path: Path, label: str) -> str:
    if old in text:
        return text.replace(old, new, 1)
    if "monthly" in str(path):
        if label == "applyDailySelection" and APPLY_SEL_OLD_MONTHLY in text:
            return text.replace(APPLY_SEL_OLD_MONTHLY, APPLY_SEL_NEW_MONTHLY, 1)
        if label == "setCalendarYear" and SET_CAL_YEAR_OLD in text:
            return text.replace(SET_CAL_YEAR_OLD, SET_CAL_YEAR_NEW_MONTHLY, 1)
    raise SystemExit(f"patch block missing in {path}: {label}")


def patch_file(path: Path, with_fill_state: bool) -> None:
    text = path.read_text(encoding="utf-8")

    timeline_block = (
        render_timeline_js(with_fill_state=with_fill_state)
        + "      renderAnnualDailyTimeline(window.__ANNUAL_DATA.calendarYear);\n"
    )
    is_monthly = "monthly" in str(path)
    if MONTHLY_RENDER_TAIL_RE.search(text):
        text = (
            MONTHLY_RENDER_TAIL_RE.sub(
                "      renderAnnualDailyTimeline(window.__ANNUAL_DATA.calendarYear);\n"
                "    })();\n",
                text,
                count=1,
            )
        )
    if "function renderAnnualDailyTimeline" not in text:
        block_re = MONTHLY_RENDER_BLOCK_RE if is_monthly else RENDER_BLOCK_RE
        m = block_re.search(text)
        if not m:
            raise SystemExit(f"renderAnnualDailyTable block not found in {path}")
        text = text[: m.start()] + timeline_block + "    })();\n" + text[m.end() :]

    if ".annual-daily-row--year-boundary" not in text:
        anchor = ".annual-daily-row--outside-year {"
        if anchor not in text:
            raise SystemExit(f"CSS anchor not found in {path}")
        text = text.replace(anchor, TIMELINE_CSS + "\n    " + anchor, 1)

    replacements = [
        (SYNC_FOCUS_OLD, SYNC_FOCUS_NEW, "syncFocus"),
        (RENDER_YEAR_OLD, RENDER_YEAR_NEW, "renderYear"),
        (SHIFT_YEAR_OLD, SHIFT_YEAR_NEW, "shiftYear"),
        (GET_BOUNDS_OLD, GET_BOUNDS_NEW, "getJumpYearBounds"),
        (INIT_SEL_OLD, INIT_SEL_NEW, "initSel"),
    ]
    for old, new, label in replacements:
        if new in text and label != "renderYear":
            continue
        if old not in text:
            if label == "renderYear" and "skipTableRender: true" in text:
                continue
            raise SystemExit(f"patch block missing in {path}: {label}")
        text = text.replace(old, new, 1)

    if SET_CAL_YEAR_NEW not in text and "setCalendarYearSilent" not in text:
        text = apply_optional(text, SET_CAL_YEAR_OLD, SET_CAL_YEAR_NEW, path, "setCalendarYear")
    if "KpiYearStore.setSelectedDate" not in text:
        text = apply_optional(text, APPLY_SEL_OLD, APPLY_SEL_NEW, path, "applyDailySelection")

    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> int:
    for path, with_fill in TARGETS:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_file(path, with_fill)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
