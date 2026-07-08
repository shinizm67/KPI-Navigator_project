#!/usr/bin/env python3
"""ARP Phase 2c — 2段階年跨ぎ: 年始/年末で一旦停止→再スクロールで跨ぐ.

現状は物理スクロール端（±14 日バッファの端）で crossYearByEdge が発火するため
「1/1 や 12/31 を通り越してバッファまで行ってからジャンプ」して見える。
判定をアンカー年の 1/1 / 12/31 行基準に変更し、
  1回目: 境界行にスナップして停止（アーム）
  2回目（同方向に再スクロール）: 年跨ぎ
とする。
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

MARKER = "/* KPI-ARP-PHASE2C */"

EDGE_DECL_OLD = """      /* KPI-ARP-PHASE2 */
      var ARP_EDGE_EPS = 6;"""

EDGE_DECL_NEW = """      /* KPI-ARP-PHASE2 */
      /* KPI-ARP-PHASE2C */
      var ARP_EDGE_EPS = 6;
      /* KPI-ARP-PHASE2C: 2段階年跨ぎ用アーム状態（-1=年始で待機, 1=年末で待機） */
      var edgeArmedDir = 0;
      function anchorYearRowRange() {
        var rows = document.querySelectorAll('#annual-daily-rows .annual-daily-row');
        var first = -1;
        var last = -1;
        for (var i = 0; i < rows.length; i++) {
          if (rows[i].getAttribute('data-active-year') === '1') {
            if (first < 0) first = i;
            last = i;
          }
        }
        return { first: first, last: last, count: rows.length };
      }
      function snapToRowIndexHard(idx) {
        if (snapTimer) clearTimeout(snapTimer);
        var target = getScrollTopForRowIndex(idx);
        if (Math.abs(target - tableScroll.scrollTop) < 1) {
          syncDailyDateFromFocusedRowForIndex(idx);
          return;
        }
        snapping = true;
        tableScroll.scrollTo({ top: target, behavior: 'smooth' });
        waitForVerticalScrollSettle(target, function () {
          snapping = false;
          syncDailyDateFromFocusedRowForIndex(idx);
        });
      }"""

SCHEDULE_SNAP_OLD = """      function scheduleSnap() {
        if (snapping) return;
        if (snapTimer) clearTimeout(snapTimer);
        snapTimer = setTimeout(function () {
          snapTimer = 0;
          /* KPI-ARP-PHASE4: Close / Open 共通 — 縦スクロール端で年跨ぎ */
          var maxTop = Math.max(0, tableScroll.scrollHeight - tableScroll.clientHeight);
          if (maxTop > 0) {
            if (tableScroll.scrollTop <= ARP_EDGE_EPS && crossYearByEdge(-1)) return;
            if (tableScroll.scrollTop >= maxTop - ARP_EDGE_EPS && crossYearByEdge(1)) return;
          }
          if (body.classList.contains('annual-focus-bar-expanded')) {
            snapTableToNearestRow();
          } else {
            syncDailyDateFromFocusedRow();
          }
        }, SNAP_DELAY_MS);
      }"""

SCHEDULE_SNAP_NEW = """      function scheduleSnap() {
        if (snapping) return;
        if (snapTimer) clearTimeout(snapTimer);
        snapTimer = setTimeout(function () {
          snapTimer = 0;
          /* KPI-ARP-PHASE2C: 年始/年末で一旦停止→再スクロールで年跨ぎ（Close / Open 共通） */
          var maxTop = Math.max(0, tableScroll.scrollHeight - tableScroll.clientHeight);
          if (maxTop > 0) {
            var range = anchorYearRowRange();
            if (range.first >= 0 && range.last >= 0) {
              var focusIdx = getNearestFocusRowIndex();
              if (focusIdx <= range.first) {
                if (edgeArmedDir === -1) {
                  edgeArmedDir = 0;
                  if (crossYearByEdge(-1)) return;
                } else {
                  edgeArmedDir = -1;
                  snapToRowIndexHard(range.first);
                  return;
                }
              } else if (focusIdx >= range.last) {
                if (edgeArmedDir === 1) {
                  edgeArmedDir = 0;
                  if (crossYearByEdge(1)) return;
                } else {
                  edgeArmedDir = 1;
                  snapToRowIndexHard(range.last);
                  return;
                }
              } else {
                edgeArmedDir = 0;
              }
            }
          }
          if (body.classList.contains('annual-focus-bar-expanded')) {
            snapTableToNearestRow();
          } else {
            syncDailyDateFromFocusedRow();
          }
        }, SNAP_DELAY_MS);
      }"""

CROSS_RESET_OLD = """        var nextYear = cy + dir;
        var b = annualRenderableYearBounds();
        if (nextYear < b.minYear || nextYear > b.maxYear) return false;
        snapping = true;"""

CROSS_RESET_NEW = """        var nextYear = cy + dir;
        var b = annualRenderableYearBounds();
        if (nextYear < b.minYear || nextYear > b.maxYear) return false;
        /* KPI-ARP-PHASE2C: 跨ぎ後に着地側で即再跨ぎしないようアーム解除 */
        edgeArmedDir = 0;
        snapping = true;"""


def main() -> int:
    for path in PAGES:
        text = path.read_text(encoding="utf-8")
        if MARKER in text:
            print(f"skip (already applied): {path.relative_to(ROOT)}")
            continue
        if EDGE_DECL_OLD not in text:
            raise ValueError(f"edge decl anchor not found: {path.relative_to(ROOT)}")
        if SCHEDULE_SNAP_OLD not in text:
            raise ValueError(f"scheduleSnap anchor not found: {path.relative_to(ROOT)}")
        if CROSS_RESET_OLD not in text:
            raise ValueError(f"cross reset anchor not found: {path.relative_to(ROOT)}")
        text = text.replace(EDGE_DECL_OLD, EDGE_DECL_NEW, 1)
        text = text.replace(SCHEDULE_SNAP_OLD, SCHEDULE_SNAP_NEW, 1)
        text = text.replace(CROSS_RESET_OLD, CROSS_RESET_NEW, 1)
        path.write_text(text, encoding="utf-8")
        print(f"applied: {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
