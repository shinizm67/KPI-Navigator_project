#!/usr/bin/env python3
"""Fix Annual↔Monthly selectedDate sync via kpiNavigator.annualNav."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ANNUAL_TARGETS = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

STORE_TARGETS = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]

SYNC_OLD = """      function syncAnnualNavToStorage() {
        var data = window.__ANNUAL_DATA || {};
        var cy = data.calendarYear;
        var iso = data.daily && data.daily.selectedDate;
        if (cy == null) return;"""

SYNC_NEW = """      function readAnnualNav() {
        var gwNav = window.__KPI_DATA_GATEWAY;
        try {
          if (gwNav && typeof gwNav.getJson === 'function') return gwNav.getJson('kpiNavigator.annualNav');
          var raw = localStorage.getItem('kpiNavigator.annualNav');
          return raw ? JSON.parse(raw) : null;
        } catch (_eNav) {
          return null;
        }
      }
      function syncAnnualNavToStorage() {
        var data = window.__ANNUAL_DATA || {};
        var cy = data.calendarYear;
        var iso = data.daily && data.daily.selectedDate;
        if ((!iso || !/^\\d{4}-\\d{2}-\\d{2}$/.test(String(iso))) && typeof readAnnualNav === 'function') {
          var existingNav = readAnnualNav();
          if (
            existingNav &&
            existingNav.selectedIso &&
            /^\\d{4}-\\d{2}-\\d{2}$/.test(String(existingNav.selectedIso))
          ) {
            iso = String(existingNav.selectedIso);
          }
        }
        if (cy == null) return;"""

RENDER_YEAR_OLD = """        window.__ANNUAL_DATA.calendarYear = currentYear;
        buildYearMenu();
      };
      renderYear();
    })();
    (function () {
      var bdEl = document.getElementById('annual-total-bd-value');"""

RENDER_YEAR_NEW = """        window.__ANNUAL_DATA.calendarYear = currentYear;
        buildYearMenu();
      };
      (function hydrateYearControlFromNav() {
        var nav = readAnnualNav();
        if (!nav || typeof nav !== 'object') return;
        if (nav.calendarYear != null && Number.isFinite(Number(nav.calendarYear))) {
          currentYear = Number(nav.calendarYear);
          window.__ANNUAL_DATA.calendarYear = currentYear;
        }
        if (nav.selectedIso && /^\\d{4}-\\d{2}-\\d{2}$/.test(String(nav.selectedIso))) {
          window.__ANNUAL_DATA.daily = window.__ANNUAL_DATA.daily || {};
          window.__ANNUAL_DATA.daily.selectedDate = String(nav.selectedIso);
        }
      })();
      renderYear();
    })();
    (function () {
      var bdEl = document.getElementById('annual-total-bd-value');"""

SET_SELECTED_OLD = """        function setSelectedDate(iso, source) {
          if (!validIso(iso)) return;
          store.meta.selectedDate = iso;"""

SET_SELECTED_NEW = """        function hydrateNavFromStorage() {
          var nav = gw().getJson(SELECTED_DATE_KEY);
          if (!nav || typeof nav !== 'object') return;
          if (nav.selectedIso && validIso(nav.selectedIso)) {
            store.meta.selectedDate = nav.selectedIso;
          }
        }

        function setSelectedDate(iso, source) {
          if (!validIso(iso)) return;
          store.meta.selectedDate = iso;"""

GET_SELECTED_OLD = """        function getSelectedDate() {
          if (store.meta.selectedDate) return store.meta.selectedDate;
          if (window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily && window.__ANNUAL_DATA.daily.selectedDate) {
            return window.__ANNUAL_DATA.daily.selectedDate;
          }
          return null;
        }"""

GET_SELECTED_NEW = """        function getSelectedDate() {
          var nav = gw().getJson(SELECTED_DATE_KEY);
          if (nav && nav.selectedIso && validIso(nav.selectedIso)) {
            store.meta.selectedDate = nav.selectedIso;
            return nav.selectedIso;
          }
          if (store.meta.selectedDate) return store.meta.selectedDate;
          if (window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily && window.__ANNUAL_DATA.daily.selectedDate) {
            return window.__ANNUAL_DATA.daily.selectedDate;
          }
          return null;
        }"""

INIT_CAL_OLD = """          if (window.__ANNUAL_DATA) {
            window.__ANNUAL_DATA.calendarYear = getOperatingYear();
          }
          ensureOperatingYearPlanDefaults();
          syncToAnnualDaily();"""

INIT_CAL_NEW = """          hydrateNavFromStorage();
          if (window.__ANNUAL_DATA) {
            var navCy = gw().getJson(SELECTED_DATE_KEY);
            if (navCy && navCy.calendarYear != null && Number.isFinite(Number(navCy.calendarYear))) {
              window.__ANNUAL_DATA.calendarYear = Number(navCy.calendarYear);
            } else if (store.meta.selectedDate && validIso(store.meta.selectedDate)) {
              window.__ANNUAL_DATA.calendarYear = isoYear(store.meta.selectedDate);
            } else {
              window.__ANNUAL_DATA.calendarYear = getOperatingYear();
            }
          }
          ensureOperatingYearPlanDefaults();
          syncToAnnualDaily();"""

RELOAD_OLD = """          reload: function () {
            loadStore();
            reconcileTimelineFromLegacy();"""

RELOAD_NEW = """          reload: function () {
            loadStore();
            hydrateNavFromStorage();
            reconcileTimelineFromLegacy();"""


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old in text:
        return text.replace(old, new, 1)
    if new.split("\n", 1)[0].strip() in text:
        return text
    raise SystemExit(f"patch miss ({label})")


def patch_annual(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = replace_once(text, SYNC_OLD, SYNC_NEW, "syncAnnualNavToStorage")
    text = replace_once(text, RENDER_YEAR_OLD, RENDER_YEAR_NEW, "hydrateYearControlFromNav")
    path.write_text(text, encoding="utf-8")
    print(f"patched annual year control: {path.relative_to(ROOT)}")


def patch_store(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = replace_once(text, SET_SELECTED_OLD, SET_SELECTED_NEW, "hydrateNavFromStorage")
    text = replace_once(text, GET_SELECTED_OLD, GET_SELECTED_NEW, "getSelectedDate")
    text = replace_once(text, INIT_CAL_OLD, INIT_CAL_NEW, "init calendarYear")
    text = replace_once(text, RELOAD_OLD, RELOAD_NEW, "reload hydrate")
    path.write_text(text, encoding="utf-8")
    print(f"patched store: {path.relative_to(ROOT)}")


def main() -> None:
    for path in ANNUAL_TARGETS:
        patch_annual(path)
    for path in STORE_TARGETS:
        patch_store(path)


if __name__ == "__main__":
    main()
