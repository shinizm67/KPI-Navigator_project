#!/usr/bin/env python3
"""Monthly Cockpit date/year nav — reduce redundant rebuilds on day change."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]

DAILY_DATE_OLD = """      document.addEventListener('annual:dailyDateChanged', function (ev) {
        var iso = ev && ev.detail && ev.detail.isoDate;
        var source = ev && ev.detail && ev.detail.source;
        if (!iso) return;
        if (source === 'focus-sync') return;
        var d = parseISODateLocal(iso);
        if (!d) return;
        if (!isDateWithinBounds(d)) return;
        setStateYearMonth(d.getFullYear(), d.getMonth());
        persistMonthlyLast();
        renderPickerMenu();
        rebuildColumns();
        var scrollOpts = source === 'today' ? { behavior: 'smooth' } : undefined;
        scheduleScroll(iso, scrollOpts);
      });"""

DAILY_DATE_NEW = """      document.addEventListener('annual:dailyDateChanged', function (ev) {
        var iso = ev && ev.detail && ev.detail.isoDate;
        var source = ev && ev.detail && ev.detail.source;
        if (!iso) return;
        if (source === 'focus-sync') return;
        var d = parseISODateLocal(iso);
        if (!d) return;
        if (!isDateWithinBounds(d)) return;
        var prevYear = state.year;
        var prevMonth0 = state.month0;
        setStateYearMonth(d.getFullYear(), d.getMonth());
        persistMonthlyLast();
        renderPickerMenu();
        if (prevYear !== state.year || prevMonth0 !== state.month0) {
          rebuildColumns();
        }
        var scrollOpts = source === 'today' ? { behavior: 'smooth' } : undefined;
        scheduleScroll(iso, scrollOpts);
      });"""

COCKPIT_REFRESH_OLD = """      function onArea1CockpitRefresh() {
        refreshArea1Cockpit(resolveArea1Iso());
      }"""

COCKPIT_REFRESH_NEW = """      var __area1CockpitRefreshTimer = null;
      function onArea1CockpitRefresh() {
        if (__area1CockpitRefreshTimer != null) window.clearTimeout(__area1CockpitRefreshTimer);
        __area1CockpitRefreshTimer = window.setTimeout(function () {
          __area1CockpitRefreshTimer = null;
          refreshArea1Cockpit(resolveArea1Iso());
        }, 0);
      }"""

SNAPSHOT_OLD = """        if (typeof window.__computeTwMetricsForIso === 'function') {
          if (window.KpiYearStore && typeof KpiYearStore.syncToAnnualDaily === 'function') {
            KpiYearStore.syncToAnnualDaily();
          }
          var m = window.__computeTwMetricsForIso(iso);
          if (m) {
            sales = Number(m.dailySales) || 0;
            if (m.dailyTarget != null && Number.isFinite(Number(m.dailyTarget))) {
              diffTarget = Number(m.dailyTarget);
              targetText = fmtTwMoney(diffTarget);
              diffActual = sales;
              diffText =
                typeof window.__twFmtDiff === 'function'
                  ? window.__twFmtDiff(diffActual, diffTarget)
                  : fmtTwMoney(diffActual - diffTarget);
              achText =
                typeof window.__twFmtAchPct === 'function'
                  ? window.__twFmtAchPct(diffActual, diffTarget)
                  : '—';
            }
          }
        }"""

SNAPSHOT_NEW = """        var dailyTarget = null;
        if (window.KpiYearStore && typeof KpiYearStore.resolveDailyTargetByIso === 'function') {
          var rowYear = Number(String(iso).slice(0, 4));
          if (Number.isFinite(rowYear)) {
            var resolved = KpiYearStore.resolveDailyTargetByIso(rowYear, iso);
            if (resolved && Number.isFinite(Number(resolved.value))) {
              dailyTarget = Number(resolved.value);
            }
          }
        } else if (typeof window.__computeTwMetricsForIso === 'function') {
          var m = window.__computeTwMetricsForIso(iso);
          if (m && m.dailyTarget != null && Number.isFinite(Number(m.dailyTarget))) {
            dailyTarget = Number(m.dailyTarget);
            sales = Number(m.dailySales) || sales;
          }
        }
        if (dailyTarget != null && Number.isFinite(dailyTarget)) {
          diffTarget = dailyTarget;
          targetText = fmtTwMoney(diffTarget);
          diffActual = sales;
          diffText =
            typeof window.__twFmtDiff === 'function'
              ? window.__twFmtDiff(diffActual, diffTarget)
              : fmtTwMoney(diffActual - diffTarget);
          achText =
            typeof window.__twFmtAchPct === 'function'
              ? window.__twFmtAchPct(diffActual, diffTarget)
              : '—';
        }"""


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    changed = False
    for old, new, label in (
        (DAILY_DATE_OLD, DAILY_DATE_NEW, "dailyDateChanged"),
        (COCKPIT_REFRESH_OLD, COCKPIT_REFRESH_NEW, "cockpit debounce"),
        (SNAPSHOT_OLD, SNAPSHOT_NEW, "group1 snapshot"),
    ):
        if old in text:
            text = text.replace(old, new, 1)
            changed = True
        elif new.split("\n", 1)[0].strip() in text and label == "dailyDateChanged":
            pass
        elif "__area1CockpitRefreshTimer" in text and label == "cockpit debounce":
            pass
        elif "resolveDailyTargetByIso(rowYear, iso)" in text and label == "group1 snapshot":
            pass
        else:
            raise SystemExit(f"{label} patch miss in {path}")
    if changed:
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")
    else:
        print(f"skip (already patched) {path.relative_to(ROOT)}")


def main() -> int:
    for path in PAGES:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_page(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
