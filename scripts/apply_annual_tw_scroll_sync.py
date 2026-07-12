#!/usr/bin/env python3
"""Hard-scroll Annual TW to selectedDate so Focus Bar matches Cockpit."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

TARGETS = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

LOCK_EXPORT_OLD = """      window.__ANNUAL_UI = window.__ANNUAL_UI || {};
      window.__ANNUAL_UI.lockFocusDateSync = lockFocusDateSync;

      function syncDailyDateFromFocusedRowForIndex(idx) {"""

LOCK_EXPORT_NEW = """      window.__ANNUAL_UI = window.__ANNUAL_UI || {};
      window.__ANNUAL_UI.lockFocusDateSync = lockFocusDateSync;
      window.__ANNUAL_UI.getFocusDateLockIso = function () {
        return __focusDateLockIso;
      };

      function scrollTableToIso(iso, opts) {
        opts = opts || {};
        if (!iso || !/^\\d{4}-\\d{2}-\\d{2}$/.test(String(iso))) return false;
        var rows = document.querySelectorAll('#annual-daily-rows .annual-daily-row');
        if (!rows || !rows.length) return false;
        var idx = -1;
        for (var i = 0; i < rows.length; i++) {
          if (rows[i].getAttribute('data-iso-date') === String(iso)) {
            idx = i;
            break;
          }
        }
        if (idx < 0) return false;
        if (snapTimer) clearTimeout(snapTimer);
        snapping = true;
        __geomCache = null;
        __anchorRangeCache = null;
        if (opts.lockMs) lockFocusDateSync(String(iso), opts.lockMs);
        var target = getScrollTopForRowIndex(idx);
        tableScroll.scrollTop = target;
        requestAnimationFrame(function () {
          __geomCache = null;
          var t2 = getScrollTopForRowIndex(idx);
          tableScroll.scrollTop = t2;
          snapping = false;
          if (typeof window.__refreshAnnualFocusBarLower === 'function') {
            window.__refreshAnnualFocusBarLower();
          }
        });
        return true;
      }
      window.__ANNUAL_UI.scrollTableToIso = scrollTableToIso;

      function syncDailyDateFromFocusedRowForIndex(idx) {"""

TRY_SCROLL_OLD = """        // Year変更やテーブル再描画直後に飛んだ場合に備えて短いリトライを入れる
        var tries = 0;
        var maxTries = 6;
        function tryScrollToISO() {
          tries += 1;
          var row = document.querySelector('#annual-daily-rows .annual-daily-row[data-iso-date="' + iso + '"]');
          if (!row) {
            if (tries < maxTries) {
              setTimeout(tryScrollToISO, 50);
            }
            return;
          }
          var rows = document.querySelectorAll('#annual-daily-rows .annual-daily-row');
          var idx = -1;
          for (var i = 0; i < rows.length; i += 1) {
            if (rows[i] === row) {
              idx = i;
              break;
            }
          }
          if (idx < 0) return;

          if (snapTimer) clearTimeout(snapTimer);
          snapping = true;
          var target = getScrollTopForRowIndex(idx);
          tableScroll.scrollTo({ top: target, behavior: 'smooth' });
          setTimeout(function () {
            snapping = false;
          }, 220);
        }
        tryScrollToISO();"""

TRY_SCROLL_NEW = """        var hardBootstrap =
          source === 'timeline-bootstrap' ||
          source === 'initial-sync' ||
          source === 'initial';
        // Year変更やテーブル再描画直後に飛んだ場合に備えて短いリトライを入れる
        var tries = 0;
        var maxTries = hardBootstrap ? 20 : 6;
        function tryScrollToISO() {
          tries += 1;
          if (
            hardBootstrap &&
            window.__ANNUAL_UI &&
            typeof window.__ANNUAL_UI.scrollTableToIso === 'function' &&
            window.__ANNUAL_UI.scrollTableToIso(iso, { lockMs: 1800 })
          ) {
            return;
          }
          var row = document.querySelector('#annual-daily-rows .annual-daily-row[data-iso-date="' + iso + '"]');
          if (!row) {
            if (tries < maxTries) {
              setTimeout(tryScrollToISO, 50);
            }
            return;
          }
          var rows = document.querySelectorAll('#annual-daily-rows .annual-daily-row');
          var idx = -1;
          for (var i = 0; i < rows.length; i += 1) {
            if (rows[i] === row) {
              idx = i;
              break;
            }
          }
          if (idx < 0) return;

          if (snapTimer) clearTimeout(snapTimer);
          snapping = true;
          var target = getScrollTopForRowIndex(idx);
          tableScroll.scrollTo({ top: target, behavior: 'smooth' });
          setTimeout(function () {
            snapping = false;
          }, 220);
        }
        tryScrollToISO();"""

TIMELINE_BOOT_OLD = """        if (prevScroll != null && scrollEl) {
          scrollEl.scrollTop = prevScroll;
        } else if (scrollEl) {
          var bootIso = null;
          try {
            if (window.KpiYearStore && typeof KpiYearStore.getSelectedDate === 'function') {
              bootIso = KpiYearStore.getSelectedDate();
            }
          } catch (_bootE) {}
          if (!bootIso && daily && daily.selectedDate) bootIso = daily.selectedDate;
          if (bootIso && /^\\d{4}-\\d{2}-\\d{2}$/.test(String(bootIso))) {
            window.__ANNUAL_DATA.daily = window.__ANNUAL_DATA.daily || {};
            window.__ANNUAL_DATA.daily.selectedDate = String(bootIso);
            if (window.__ANNUAL_UI && typeof window.__ANNUAL_UI.lockFocusDateSync === 'function') {
              window.__ANNUAL_UI.lockFocusDateSync(String(bootIso), 1800);
            }
            requestAnimationFrame(function () {
              document.dispatchEvent(
                new CustomEvent('annual:dailyDateChanged', {
                  detail: { isoDate: String(bootIso), source: 'timeline-bootstrap' },
                })
              );
            });
          }
        }
        if (document.body.classList.contains('monthly-page')) {"""

TIMELINE_BOOT_NEW = """        var bootIsoForScroll = null;
        if (prevScroll != null && scrollEl) {
          scrollEl.scrollTop = prevScroll;
        } else if (scrollEl) {
          try {
            if (window.KpiYearStore && typeof KpiYearStore.getSelectedDate === 'function') {
              bootIsoForScroll = KpiYearStore.getSelectedDate();
            }
          } catch (_bootE) {}
          if (!bootIsoForScroll && daily && daily.selectedDate) bootIsoForScroll = daily.selectedDate;
          if (bootIsoForScroll && /^\\d{4}-\\d{2}-\\d{2}$/.test(String(bootIsoForScroll))) {
            window.__ANNUAL_DATA.daily = window.__ANNUAL_DATA.daily || {};
            window.__ANNUAL_DATA.daily.selectedDate = String(bootIsoForScroll);
          }
        }
        if (
          bootIsoForScroll &&
          window.__ANNUAL_UI &&
          typeof window.__ANNUAL_UI.scrollTableToIso === 'function'
        ) {
          window.__ANNUAL_UI.scrollTableToIso(String(bootIsoForScroll), { lockMs: 1800 });
        } else if (bootIsoForScroll) {
          document.dispatchEvent(
            new CustomEvent('annual:dailyDateChanged', {
              detail: { isoDate: String(bootIsoForScroll), source: 'timeline-bootstrap' },
            })
          );
        }
        if (document.body.classList.contains('monthly-page')) {"""

REFRESH_LOWER_OLD = """      function refreshLower() {
        if (raf) cancelAnimationFrame(raf);
        raf = requestAnimationFrame(function () {
          var state = getFocusedRowState();
          var idx = state.idx;"""

REFRESH_LOWER_NEW = """      function refreshLower() {
        if (raf) cancelAnimationFrame(raf);
        raf = requestAnimationFrame(function () {
          var state = getFocusedRowState();
          var lockIso =
            window.__ANNUAL_UI && typeof window.__ANNUAL_UI.getFocusDateLockIso === 'function'
              ? window.__ANNUAL_UI.getFocusDateLockIso()
              : null;
          if (lockIso) {
            var lockRow = rowsRoot.querySelector(
              '.annual-daily-row[data-iso-date="' + lockIso + '"]'
            );
            if (lockRow) {
              var lockRows = rowsRoot.children;
              var lockIdx = -1;
              for (var li = 0; li < lockRows.length; li++) {
                if (lockRows[li] === lockRow) {
                  lockIdx = li;
                  break;
                }
              }
              if (lockIdx >= 0) {
                state = { row: lockRow, offset: state.offset, idx: lockIdx };
              }
            }
          }
          var idx = state.idx;"""


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old in text:
        return text.replace(old, new, 1)
    if new.split("\n", 1)[0].strip() in text:
        return text
    raise SystemExit(f"patch miss ({label})")


def patch(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = replace_once(text, LOCK_EXPORT_OLD, LOCK_EXPORT_NEW, "scrollTableToIso")
    text = replace_once(text, TRY_SCROLL_OLD, TRY_SCROLL_NEW, "tryScrollToISO hard")
    text = replace_once(text, TIMELINE_BOOT_OLD, TIMELINE_BOOT_NEW, "timeline boot scroll")
    text = replace_once(text, REFRESH_LOWER_OLD, REFRESH_LOWER_NEW, "refreshLower lock")
    path.write_text(text, encoding="utf-8")
    print(f"patched {path.relative_to(ROOT)}")


def main() -> None:
    for path in TARGETS:
        patch(path)


if __name__ == "__main__":
    main()
