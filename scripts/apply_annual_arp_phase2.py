#!/usr/bin/env python3
"""ARP Phase 2 — Annual TW: crossYearByEdge (vertical scroll, Close mode).

Close 時に縦スクロールが上端/下端に達したら年を跨ぐ。
- 上端 → 前年（12/31 着地） / 下端 → 翌年（1/1 着地）
- annual:calendarYearChanged は飛ばさず、窓リビルド・年バッジ・selectedDate を個別同期
- Open (annual-focus-bar-expanded) は対象外（ARP-4）
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

MARKER = "/* KPI-ARP-PHASE2 */"

SCHEDULE_SNAP_OLD = """      function scheduleSnap() {
        if (snapping) return;
        if (snapTimer) clearTimeout(snapTimer);
        snapTimer = setTimeout(function () {
          snapTimer = 0;
          if (body.classList.contains('annual-focus-bar-expanded')) {
            snapTableToNearestRow();
          } else {
            syncDailyDateFromFocusedRow();
          }
        }, SNAP_DELAY_MS);
      }"""

SCHEDULE_SNAP_NEW = """      /* KPI-ARP-PHASE2 */
      var ARP_EDGE_EPS = 6;
      function annualRenderableYearBounds() {
        var systemYear = new Date().getFullYear();
        var minY = systemYear;
        var maxY = systemYear;
        if (window.KpiYearStore) {
          try {
            if (typeof KpiYearStore.listYearsWithData === 'function') {
              KpiYearStore.listYearsWithData().forEach(function (y) {
                y = Number(y);
                if (!Number.isFinite(y)) return;
                if (y < minY) minY = y;
                if (y > maxY) maxY = y;
              });
            }
            if (typeof KpiYearStore.getOperatingYear === 'function') {
              var oy = Number(KpiYearStore.getOperatingYear());
              if (Number.isFinite(oy)) {
                if (oy < minY) minY = oy;
                if (oy > maxY) maxY = oy;
              }
            }
          } catch (e) {}
        }
        maxY = Math.max(maxY, systemYear + 1);
        return { minYear: minY, maxYear: maxY };
      }
      function crossYearByEdge(dir) {
        if (dir !== 1 && dir !== -1) return false;
        /* ARP-2: Close モードのみ。Open は ARP-4 で対応 */
        if (body.classList.contains('annual-focus-bar-expanded')) return false;
        if (typeof window.__renderAnnualDailyTimeline !== 'function') return false;
        var cy = Number(window.__ANNUAL_DATA && window.__ANNUAL_DATA.calendarYear);
        if (!Number.isFinite(cy)) return false;
        var nextYear = cy + dir;
        var b = annualRenderableYearBounds();
        if (nextYear < b.minYear || nextYear > b.maxYear) return false;
        snapping = true;
        window.__renderAnnualDailyTimeline(nextYear, {
          boundsHint: 'anchor-year-only',
          preserveScroll: false,
        });
        var yearBadge = document.getElementById('annual-daily-focus-tw-year');
        if (yearBadge) yearBadge.textContent = String(nextYear);
        var iso = dir > 0 ? nextYear + '-01-01' : nextYear + '-12-31';
        if (window.__ANNUAL_UI && typeof window.__ANNUAL_UI.setDailyDateByISO === 'function') {
          window.__ANNUAL_UI.setDailyDateByISO(iso, 'focus-sync');
        }
        var rows = document.querySelectorAll('#annual-daily-rows .annual-daily-row');
        var idx = -1;
        for (var i = 0; i < rows.length; i++) {
          if (rows[i].getAttribute('data-iso-date') === iso) {
            idx = i;
            break;
          }
        }
        if (idx >= 0) {
          var target = getScrollTopForRowIndex(idx);
          tableScroll.scrollTop = target;
          setTimeout(function () {
            snapping = false;
            syncDailyDateFromFocusedRowForIndex(idx);
          }, 60);
        } else {
          snapping = false;
        }
        return true;
      }
      function scheduleSnap() {
        if (snapping) return;
        if (snapTimer) clearTimeout(snapTimer);
        snapTimer = setTimeout(function () {
          snapTimer = 0;
          if (body.classList.contains('annual-focus-bar-expanded')) {
            snapTableToNearestRow();
          } else {
            /* KPI-ARP-PHASE2: Close時、縦スクロール端で年跨ぎ */
            var maxTop = Math.max(0, tableScroll.scrollHeight - tableScroll.clientHeight);
            if (maxTop > 0) {
              if (tableScroll.scrollTop <= ARP_EDGE_EPS && crossYearByEdge(-1)) return;
              if (tableScroll.scrollTop >= maxTop - ARP_EDGE_EPS && crossYearByEdge(1)) return;
            }
            syncDailyDateFromFocusedRow();
          }
        }, SNAP_DELAY_MS);
      }"""


def main() -> int:
    for path in PAGES:
        text = path.read_text(encoding="utf-8")
        if MARKER in text:
            print(f"skip (already applied): {path.relative_to(ROOT)}")
            continue
        if SCHEDULE_SNAP_OLD not in text:
            raise ValueError(f"scheduleSnap anchor not found: {path.relative_to(ROOT)}")
        text = text.replace(SCHEDULE_SNAP_OLD, SCHEDULE_SNAP_NEW, 1)
        path.write_text(text, encoding="utf-8")
        print(f"applied: {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
