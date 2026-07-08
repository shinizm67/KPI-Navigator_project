#!/usr/bin/env python3
"""ARP Phase 2e — 年跨ぎスクロールの hot path 軽量化（カクつき低減）.

ARP-2d で入れた「毎スクロール 393 行 getBoundingClientRect」を廃し:
- getNearestFocusRowIndex / getScrollTopForRowIndex を実測ピッチ基準の O(1) 算術に
- anchorYearRowRange をキャッシュ（描画時に無効化）
- enforceYearBoundaryScroll を rAF で間引き
精度（実測ピッチ）は維持。
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

MARKER = "/* KPI-ARP-PHASE2E */"

FOCUS_INDEX_OLD = """      /* KPI-ARP-PHASE2D: Focus Bar アンカーに最も近い行（DOM 実測） */
      function getNearestFocusRowIndex() {
        var rows = document.querySelectorAll('#annual-daily-rows .annual-daily-row');
        if (!rows || !rows.length) return 0;
        var tableRect = tableScroll.getBoundingClientRect();
        var anchorOffset = getFocusAnchorOffsetY();
        var bestIdx = 0;
        var bestDist = Infinity;
        for (var i = 0; i < rows.length; i++) {
          var rowRect = rows[i].getBoundingClientRect();
          var center = rowRect.top - tableRect.top + rowRect.height / 2;
          var dist = Math.abs(center - anchorOffset);
          if (dist < bestDist) {
            bestDist = dist;
            bestIdx = i;
          }
        }
        return bestIdx;
      }

      /* KPI-ARP-PHASE2D: 行中心を Focus Bar アンカーに一致させる scrollTop */
      function getScrollTopForRowIndex(idx) {
        var rows = document.querySelectorAll('#annual-daily-rows .annual-daily-row');
        if (!rows || !rows.length || idx < 0 || idx >= rows.length) return tableScroll.scrollTop;
        var row = rows[idx];
        var tableRect = tableScroll.getBoundingClientRect();
        var rowRect = row.getBoundingClientRect();
        var anchorOffset = getFocusAnchorOffsetY();
        var rowCenterViewport = rowRect.top - tableRect.top + rowRect.height / 2;
        var target = tableScroll.scrollTop + (rowCenterViewport - anchorOffset);
        var maxTop = tableScroll.scrollHeight - tableScroll.clientHeight;
        if (target < 0) target = 0;
        if (target > maxTop) target = maxTop;
        return target;
      }"""

FOCUS_INDEX_NEW = """      /* KPI-ARP-PHASE2E: 実測ピッチ（行0/行1から算出）。O(1) */
      function getRowPitch() {
        var rows = document.querySelectorAll('#annual-daily-rows .annual-daily-row');
        if (!rows || rows.length < 2) return SNAP_ROW_PITCH;
        var r0 = rows[0].getBoundingClientRect();
        var r1 = rows[1].getBoundingClientRect();
        var p = r1.top - r0.top;
        return p > 0 ? p : SNAP_ROW_PITCH;
      }

      /* KPI-ARP-PHASE2E: Focus Bar アンカー最寄り行（算術・O(1)） */
      function getNearestFocusRowIndex() {
        var rows = document.querySelectorAll('#annual-daily-rows .annual-daily-row');
        if (!rows || !rows.length) return 0;
        var rowStart = getRowStartYInContent();
        if (rowStart == null) return 0;
        var pitch = getRowPitch();
        var anchorOffset = getFocusAnchorOffsetY();
        var anchorYInContent = tableScroll.scrollTop + anchorOffset;
        var idx = Math.round((anchorYInContent - (rowStart + SNAP_ROW_HEIGHT / 2)) / pitch);
        if (idx < 0) idx = 0;
        if (idx >= rows.length) idx = rows.length - 1;
        return idx;
      }

      /* KPI-ARP-PHASE2E: 行中心をアンカーに一致させる scrollTop（算術・O(1)） */
      function getScrollTopForRowIndex(idx) {
        var rows = document.querySelectorAll('#annual-daily-rows .annual-daily-row');
        if (!rows || !rows.length) return tableScroll.scrollTop;
        if (idx < 0) idx = 0;
        if (idx >= rows.length) idx = rows.length - 1;
        var rowStart = getRowStartYInContent();
        if (rowStart == null) return tableScroll.scrollTop;
        var pitch = getRowPitch();
        var anchorOffset = getFocusAnchorOffsetY();
        var target = rowStart + idx * pitch + SNAP_ROW_HEIGHT / 2 - anchorOffset;
        var maxTop = tableScroll.scrollHeight - tableScroll.clientHeight;
        if (target < 0) target = 0;
        if (target > maxTop) target = maxTop;
        return target;
      }"""

RANGE_OLD = """      function anchorYearRowRange() {
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
      }"""

RANGE_NEW = """      /* KPI-ARP-PHASE2E: 描画毎に無効化するキャッシュ */
      var __anchorRangeCache = null;
      function anchorYearRowRange() {
        if (__anchorRangeCache) return __anchorRangeCache;
        var rows = document.querySelectorAll('#annual-daily-rows .annual-daily-row');
        var first = -1;
        var last = -1;
        for (var i = 0; i < rows.length; i++) {
          if (rows[i].getAttribute('data-active-year') === '1') {
            if (first < 0) first = i;
            last = i;
          }
        }
        __anchorRangeCache = { first: first, last: last, count: rows.length };
        return __anchorRangeCache;
      }
      document.addEventListener('annual:timelineRowsRendered', function () {
        __anchorRangeCache = null;
      });"""

SCROLL_OLD = """      window.__annualTwFocusRowIndex = getNearestFocusRowIndex;
      tableScroll.addEventListener('scroll', function () {
        var st = tableScroll.scrollTop;
        if (st > lastScrollTop) lastScrollDir = 1;
        else if (st < lastScrollTop) lastScrollDir = -1;
        lastScrollTop = st;
        if (!snapping) enforceYearBoundaryScroll();
        syncScrollLeft(tableScroll);
        scheduleSnap();
      }, { passive: true });"""

SCROLL_NEW = """      window.__annualTwFocusRowIndex = getNearestFocusRowIndex;
      /* KPI-ARP-PHASE2E: enforce を rAF で間引き（毎イベント実行しない） */
      var __enforceRafPending = false;
      function scheduleEnforceYearBoundary() {
        if (__enforceRafPending) return;
        __enforceRafPending = true;
        requestAnimationFrame(function () {
          __enforceRafPending = false;
          if (!snapping) enforceYearBoundaryScroll();
        });
      }
      tableScroll.addEventListener('scroll', function () {
        var st = tableScroll.scrollTop;
        if (st > lastScrollTop) lastScrollDir = 1;
        else if (st < lastScrollTop) lastScrollDir = -1;
        lastScrollTop = st;
        scheduleEnforceYearBoundary();
        syncScrollLeft(tableScroll);
        scheduleSnap();
      }, { passive: true });"""


def main() -> int:
    for path in PAGES:
        text = path.read_text(encoding="utf-8")
        if MARKER in text:
            print(f"skip (already applied): {path.relative_to(ROOT)}")
            continue
        for old, new, label in [
            (FOCUS_INDEX_OLD, FOCUS_INDEX_NEW, "focus index"),
            (RANGE_OLD, RANGE_NEW, "range cache"),
            (SCROLL_OLD, SCROLL_NEW, "scroll throttle"),
        ]:
            if old not in text:
                raise ValueError(f"{label}: anchor not found in {path.relative_to(ROOT)}")
            text = text.replace(old, new, 1)
        # マーカーを先頭付近に一度だけ残す
        text = text.replace(
            "      /* KPI-ARP-PHASE2E: 実測ピッチ（行0/行1から算出）。O(1) */",
            "      " + MARKER + "\n      /* KPI-ARP-PHASE2E: 実測ピッチ（行0/行1から算出）。O(1) */",
            1,
        )
        path.write_text(text, encoding="utf-8")
        print(f"applied: {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
