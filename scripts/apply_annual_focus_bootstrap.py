#!/usr/bin/env python3
"""Prevent Annual Focus Bar from resetting selectedDate to Jan 1 on load."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

TARGETS = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

SYNC_FN_OLD = """      function syncDailyDateFromFocusedRowForIndex(idx) {
        var rows = document.querySelectorAll('#annual-daily-rows .annual-daily-row');
        if (!rows || !rows.length) return;
        if (idx < 0 || idx >= rows.length) return;
        var iso = rows[idx].getAttribute('data-iso-date');
        if (!iso) return;
        if (window.__ANNUAL_UI && typeof window.__ANNUAL_UI.setDailyDateByISO === 'function') {
          window.__ANNUAL_UI.setDailyDateByISO(iso, 'focus-sync');
        }
      }"""

SYNC_FN_NEW = """      var __focusDateLockIso = null;
      var __focusDateLockTimer = null;
      function lockFocusDateSync(iso, ms) {
        if (!iso || !/^\\d{4}-\\d{2}-\\d{2}$/.test(String(iso))) return;
        __focusDateLockIso = String(iso);
        if (__focusDateLockTimer != null) window.clearTimeout(__focusDateLockTimer);
        __focusDateLockTimer = window.setTimeout(function () {
          __focusDateLockIso = null;
          __focusDateLockTimer = null;
        }, Number(ms) > 0 ? Number(ms) : 1500);
      }
      window.__ANNUAL_UI = window.__ANNUAL_UI || {};
      window.__ANNUAL_UI.lockFocusDateSync = lockFocusDateSync;

      function syncDailyDateFromFocusedRowForIndex(idx) {
        var rows = document.querySelectorAll('#annual-daily-rows .annual-daily-row');
        if (!rows || !rows.length) return;
        if (idx < 0 || idx >= rows.length) return;
        var iso = rows[idx].getAttribute('data-iso-date');
        if (!iso) return;
        if (__focusDateLockIso && iso !== __focusDateLockIso) return;
        if (window.__ANNUAL_UI && typeof window.__ANNUAL_UI.setDailyDateByISO === 'function') {
          window.__ANNUAL_UI.setDailyDateByISO(iso, 'focus-sync');
        }
      }"""

DATE_CHANGED_OLD = """      document.addEventListener('annual:dailyDateChanged', function (ev) {
        var iso = ev && ev.detail && ev.detail.isoDate;
        var source = ev && ev.detail && ev.detail.source;
        if (!iso) return;
        if (source === 'focus-sync') return;

        // Year変更やテーブル再描画直後に飛んだ場合に備えて短いリトライを入れる"""

DATE_CHANGED_NEW = """      document.addEventListener('annual:dailyDateChanged', function (ev) {
        var iso = ev && ev.detail && ev.detail.isoDate;
        var source = ev && ev.detail && ev.detail.source;
        if (!iso) return;
        if (source === 'focus-sync') return;
        if (
          source === 'timeline-bootstrap' ||
          source === 'initial-sync' ||
          source === 'initial'
        ) {
          lockFocusDateSync(iso, 1800);
        }

        // Year変更やテーブル再描画直後に飛んだ場合に備えて短いリトライを入れる"""

TIMELINE_END_OLD = """        if (prevScroll != null && scrollEl) {
          scrollEl.scrollTop = prevScroll;
        }
        if (document.body.classList.contains('monthly-page')) {
          if (opts.boundsHint === 'anchor-year-only') {
            window.__monthlyVerticalTwPartialRendered = true;
          } else {
            window.__monthlyVerticalTwPartialRendered = true;
            window.__monthlyVerticalTwFullRendered = true;
          }
        }
        document.dispatchEvent(new CustomEvent('annual:timelineRowsRendered'));
      }"""

TIMELINE_END_NEW = """        if (prevScroll != null && scrollEl) {
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
        if (document.body.classList.contains('monthly-page')) {
          if (opts.boundsHint === 'anchor-year-only') {
            window.__monthlyVerticalTwPartialRendered = true;
          } else {
            window.__monthlyVerticalTwPartialRendered = true;
            window.__monthlyVerticalTwFullRendered = true;
          }
        }
        document.dispatchEvent(new CustomEvent('annual:timelineRowsRendered'));
      }"""

APPLY_INITIAL_OLD = None



def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old in text:
        return text.replace(old, new, 1)
    if new.split("\n", 1)[0].strip() in text:
        return text
    raise SystemExit(f"patch miss ({label})")


def patch(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = replace_once(text, SYNC_FN_OLD, SYNC_FN_NEW, "syncDailyDateFromFocusedRowForIndex")
    text = replace_once(text, DATE_CHANGED_OLD, DATE_CHANGED_NEW, "dailyDateChanged lock")
    text = replace_once(text, TIMELINE_END_OLD, TIMELINE_END_NEW, "timeline bootstrap scroll")
    path.write_text(text, encoding="utf-8")
    print(f"patched {path.relative_to(ROOT)}")


def main() -> None:
    for path in TARGETS:
        patch(path)


if __name__ == "__main__":
    main()
