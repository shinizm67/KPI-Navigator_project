#!/usr/bin/env python3
"""P0 remainder: selectedDate sharing between Monthly Focus Bar and MEP."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MEP_TARGETS = [
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
]

MONTHLY_TARGETS = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]

SYNC_FROM_OLD = """      function syncFromPage() {
        var params = new URLSearchParams(window.location.search);
        var y = Number(params.get('year'));
        var m = Number(params.get('month'));
        var iso = String(params.get('iso') || '').trim();
        if (iso && /^\\d{4}-\\d{2}-\\d{2}$/.test(iso)) mefPreferredIso = iso;
        if (Number.isFinite(y) && m >= 1 && m <= 12) {
          mefYear = y;
          mefMonth0 = m - 1;
          return;
        }
        try {
          var raw = sessionStorage.getItem(MEF_STORAGE_MONTHLY_LAST);
          if (raw) {
            var o = JSON.parse(raw);
            if (o && Number.isFinite(o.year) && Number.isFinite(o.month0)) {
              mefYear = o.year;
              mefMonth0 = o.month0;
              return;
            }
          }
        } catch (_e) {}
        var ui = window.__MONTHLY_UI;
        if (ui && typeof ui.getState === 'function') {
          var st = ui.getState();
          if (st && Number.isFinite(st.year) && Number.isFinite(st.month0)) {
            mefYear = st.year;
            mefMonth0 = st.month0;
          }
        }
      }"""

SYNC_FROM_NEW = """      function mepIsoFromParts(y, m0, d) {
        return y + '-' + String(m0 + 1).padStart(2, '0') + '-' + String(d).padStart(2, '0');
      }
      function applyMepSelectedIso(iso) {
        if (!iso || !/^\\d{4}-\\d{2}-\\d{2}$/.test(iso)) return;
        mefPreferredIso = iso;
        var parts = iso.split('-');
        mefYear = Number(parts[0]);
        mefMonth0 = Number(parts[1]) - 1;
      }
      function pushMepSelectedDateToStore(iso) {
        if (
          window.KpiYearStore &&
          typeof KpiYearStore.setSelectedDate === 'function' &&
          iso &&
          /^\\d{4}-\\d{2}-\\d{2}$/.test(iso)
        ) {
          KpiYearStore.setSelectedDate(iso, 'monthly-edit-float');
        }
      }
      function syncFromPage() {
        var params = new URLSearchParams(window.location.search);
        var y = Number(params.get('year'));
        var m = Number(params.get('month'));
        var iso = String(params.get('iso') || '').trim();
        if (iso && /^\\d{4}-\\d{2}-\\d{2}$/.test(iso)) {
          applyMepSelectedIso(iso);
          return;
        }
        if (Number.isFinite(y) && m >= 1 && m <= 12) {
          mefYear = y;
          mefMonth0 = m - 1;
          return;
        }
        try {
          var raw = sessionStorage.getItem(MEF_STORAGE_MONTHLY_LAST);
          if (raw) {
            var o = JSON.parse(raw);
            if (o && Number.isFinite(o.year) && Number.isFinite(o.month0)) {
              mefYear = o.year;
              mefMonth0 = o.month0;
              return;
            }
          }
        } catch (_e) {}
        var ui = window.__MONTHLY_UI;
        if (ui && typeof ui.getState === 'function') {
          var st = ui.getState();
          if (st && Number.isFinite(st.year) && Number.isFinite(st.month0)) {
            mefYear = st.year;
            mefMonth0 = st.month0;
          }
        }
        if (
          !mefPreferredIso &&
          window.KpiYearStore &&
          typeof KpiYearStore.getSelectedDate === 'function'
        ) {
          var storeIso = String(KpiYearStore.getSelectedDate() || '').trim();
          if (/^\\d{4}-\\d{2}-\\d{2}$/.test(storeIso)) applyMepSelectedIso(storeIso);
        }
      }"""

SCROLL_OLD = """      function scrollToPreferredDayLeft() {
        if (!scroller || !tbl) return;
        var ths = dateRailScale.querySelectorAll('.monthly-edit-float__date-rail-th');
        if (!ths || !ths.length) return;
        var now = new Date();
        var dayIdx = 0;
        if (now.getFullYear() === mefYear && now.getMonth() === mefMonth0) {
          dayIdx = Math.max(0, Math.min(ths.length - 1, now.getDate() - 1));
        }
        var target = ths[dayIdx];
        var left = target ? target.offsetLeft : 0;
        scroller.scrollLeft = left;
      }"""

SCROLL_NEW = """      function scrollToPreferredDayLeft() {
        if (!scroller || !tbl) return;
        var ths = dateRailScale.querySelectorAll('.monthly-edit-float__date-rail-th');
        if (!ths || !ths.length) return;
        var dayIdx = 0;
        if (mefPreferredIso) {
          var prefParts = mefPreferredIso.split('-');
          if (
            Number(prefParts[0]) === mefYear &&
            Number(prefParts[1]) - 1 === mefMonth0
          ) {
            dayIdx = Math.max(0, Math.min(ths.length - 1, Number(prefParts[2]) - 1));
          }
        } else {
          var now = new Date();
          if (now.getFullYear() === mefYear && now.getMonth() === mefMonth0) {
            dayIdx = Math.max(0, Math.min(ths.length - 1, now.getDate() - 1));
          }
        }
        var target = ths[dayIdx];
        var left = target ? target.offsetLeft : 0;
        scroller.scrollLeft = left;
        if (target) {
          var isoAttr = target.getAttribute('data-iso');
          if (isoAttr) pushMepSelectedDateToStore(isoAttr);
        }
      }"""

INIT_OLD = """        if (mefPreferredIso) scrollToIsoColumn(mefPreferredIso);
        else scrollToPreferredDayLeft();
        syncLabelScroll();
        pinLabelsToRight();
      }"""

INIT_NEW = """        if (mefPreferredIso) {
          scrollToIsoColumn(mefPreferredIso);
          pushMepSelectedDateToStore(mefPreferredIso);
        } else {
          scrollToPreferredDayLeft();
        }
        syncLabelScroll();
        pinLabelsToRight();
      }"""

READ_DAILY_OLD = """      function readDailySelectedIso() {
        var daily = window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily;
        if (!daily || !daily.selectedDate) return null;
        var d = parseISODateLocal(daily.selectedDate);
        if (!d) return null;
        return toISODateLocal(d);
      }"""

READ_DAILY_NEW = """      function readDailySelectedIso() {
        if (window.KpiYearStore && typeof KpiYearStore.getSelectedDate === 'function') {
          var storeIso = String(KpiYearStore.getSelectedDate() || '').trim();
          var storeDate = storeIso ? parseISODateLocal(storeIso) : null;
          if (storeDate) return toISODateLocal(storeDate);
        }
        var daily = window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily;
        if (!daily || !daily.selectedDate) return null;
        var d = parseISODateLocal(daily.selectedDate);
        if (!d) return null;
        return toISODateLocal(d);
      }"""


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old in text:
        return text.replace(old, new, 1)
    if new.split("\n", 1)[0].strip() in text:
        return text
    raise SystemExit(f"patch miss ({label})")


def patch_mep(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = replace_once(text, SYNC_FROM_OLD, SYNC_FROM_NEW, "syncFromPage")
    text = replace_once(text, SCROLL_OLD, SCROLL_NEW, "scrollToPreferredDayLeft")
    text = replace_once(text, INIT_OLD, INIT_NEW, "initEditPage")
    path.write_text(text, encoding="utf-8")
    print(f"patched MEP: {path}")


def patch_monthly(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = replace_once(text, READ_DAILY_OLD, READ_DAILY_NEW, "readDailySelectedIso")
    path.write_text(text, encoding="utf-8")
    print(f"patched monthly: {path}")


def main() -> None:
    for path in MEP_TARGETS:
        patch_mep(path)
    for path in MONTHLY_TARGETS:
        patch_monthly(path)


if __name__ == "__main__":
    main()
