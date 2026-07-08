#!/usr/bin/env python3
"""ARP Phase 2d — 年境界のリアルタイムクランプ + 幾何学ベースの Focus Bar スナップ.

問題:
- scheduleSnap の 110ms debounce 後にしか年境界判定しない → 慣性でバッファ突き抜け
- SNAP_ROW_PITCH=42 固定計算と Close 時の scroll スナップ欠如 → Focus Bar とずれる

対策:
- scroll イベントで即時 enforceYearBoundaryScroll（バッファ侵入を即クランプ）
- getNearestFocusRowIndex / getScrollTopForRowIndex を DOM 実測ベースに変更
- Close / Open 共通で snapToNearestRow を実行
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

MARKER = "/* KPI-ARP-PHASE2D */"

FOCUS_INDEX_OLD = """      function getNearestFocusRowIndex() {
        var rows = document.querySelectorAll('#annual-daily-rows .annual-daily-row');
        if (!rows || !rows.length) return 0;
        var rowStart = getRowStartYInContent();
        if (rowStart == null) return 0;
        var anchorOffset = getFocusAnchorOffsetY();
        var anchorYInContent = tableScroll.scrollTop + anchorOffset;
        var idx = Math.round((anchorYInContent - (rowStart + SNAP_ROW_HEIGHT / 2)) / SNAP_ROW_PITCH);
        if (idx < 0) idx = 0;
        if (idx >= rows.length) idx = rows.length - 1;
        return idx;
      }

      function getScrollTopForRowIndex(idx) {
        var rows = document.querySelectorAll('#annual-daily-rows .annual-daily-row');
        if (!rows || !rows.length) return tableScroll.scrollTop;
        var rowStart = getRowStartYInContent();
        if (rowStart == null) return tableScroll.scrollTop;
        var anchorOffset = getFocusAnchorOffsetY();
        var target = rowStart + idx * SNAP_ROW_PITCH + SNAP_ROW_HEIGHT / 2 - anchorOffset;
        var maxTop = tableScroll.scrollHeight - tableScroll.clientHeight;
        if (target < 0) target = 0;
        if (target > maxTop) target = maxTop;
        return target;
      }

      function snapTableToNearestRow() {
        if (!body.classList.contains('annual-focus-bar-expanded')) return;
        var maxTop = tableScroll.scrollHeight - tableScroll.clientHeight;
        if (maxTop <= 0) {
          syncDailyDateFromFocusedRow();
          return;
        }
        var idx = getNearestFocusRowIndex();
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

FOCUS_INDEX_NEW = """      /* KPI-ARP-PHASE2D: Focus Bar アンカーに最も近い行（DOM 実測） */
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
      }

      function snapToNearestRow() {
        if (snapping) return;
        var maxTop = tableScroll.scrollHeight - tableScroll.clientHeight;
        if (maxTop <= 0) {
          syncDailyDateFromFocusedRow();
          return;
        }
        var idx = getNearestFocusRowIndex();
        var target = getScrollTopForRowIndex(idx);
        if (Math.abs(target - tableScroll.scrollTop) < 1) {
          syncDailyDateFromFocusedRowForIndex(idx);
          if (typeof window.__refreshAnnualFocusBarLower === 'function') {
            window.__refreshAnnualFocusBarLower();
          }
          return;
        }
        snapping = true;
        tableScroll.scrollTo({ top: target, behavior: 'smooth' });
        waitForVerticalScrollSettle(target, function () {
          snapping = false;
          syncDailyDateFromFocusedRowForIndex(idx);
          if (typeof window.__refreshAnnualFocusBarLower === 'function') {
            window.__refreshAnnualFocusBarLower();
          }
        });
      }

      function snapTableToNearestRow() {
        snapToNearestRow();
      }"""

ENFORCE_BLOCK = """      function snapToRowIndexHard(idx) {
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

ENFORCE_BLOCK_NEW = """      /* KPI-ARP-PHASE2D */
      var lastScrollTop = tableScroll.scrollTop;
      var lastScrollDir = 0;
      function enforceYearBoundaryScroll() {
        if (snapping) return false;
        var range = anchorYearRowRange();
        if (range.first < 0 || range.last < 0) return false;
        var focusIdx = getNearestFocusRowIndex();
        if (focusIdx < range.first || focusIdx > range.last) {
          var clampIdx = focusIdx < range.first ? range.first : range.last;
          var clampTarget = getScrollTopForRowIndex(clampIdx);
          if (Math.abs(tableScroll.scrollTop - clampTarget) > 1) {
            snapping = true;
            tableScroll.scrollTop = clampTarget;
            snapping = false;
            syncDailyDateFromFocusedRowForIndex(clampIdx);
          }
          return true;
        }
        if (focusIdx === range.first && lastScrollDir < 0) {
          if (edgeArmedDir === -1) {
            edgeArmedDir = 0;
            crossYearByEdge(-1);
            return true;
          }
          edgeArmedDir = -1;
          var topTarget = getScrollTopForRowIndex(range.first);
          if (Math.abs(tableScroll.scrollTop - topTarget) > 1) {
            snapping = true;
            tableScroll.scrollTop = topTarget;
            snapping = false;
          }
          syncDailyDateFromFocusedRowForIndex(range.first);
          return true;
        }
        if (focusIdx === range.last && lastScrollDir > 0) {
          if (edgeArmedDir === 1) {
            edgeArmedDir = 0;
            crossYearByEdge(1);
            return true;
          }
          edgeArmedDir = 1;
          var botTarget = getScrollTopForRowIndex(range.last);
          if (Math.abs(tableScroll.scrollTop - botTarget) > 1) {
            snapping = true;
            tableScroll.scrollTop = botTarget;
            snapping = false;
          }
          syncDailyDateFromFocusedRowForIndex(range.last);
          return true;
        }
        if (focusIdx > range.first && focusIdx < range.last) {
          edgeArmedDir = 0;
        }
        return false;
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

SCHEDULE_SNAP_NEW = """      function scheduleSnap() {
        if (snapping) return;
        if (snapTimer) clearTimeout(snapTimer);
        snapTimer = setTimeout(function () {
          snapTimer = 0;
          if (snapping) return;
          /* KPI-ARP-PHASE2D: 年境界は enforceYearBoundaryScroll が即時処理。ここは行スナップ */
          snapToNearestRow();
        }, SNAP_DELAY_MS);
      }"""

SCROLL_LISTENER_OLD = """      tableScroll.addEventListener('scroll', function () {
        syncScrollLeft(tableScroll);
        scheduleSnap();
      }, { passive: true });"""

SCROLL_LISTENER_NEW = """      window.__annualTwFocusRowIndex = getNearestFocusRowIndex;
      tableScroll.addEventListener('scroll', function () {
        var st = tableScroll.scrollTop;
        if (st > lastScrollTop) lastScrollDir = 1;
        else if (st < lastScrollTop) lastScrollDir = -1;
        lastScrollTop = st;
        if (!snapping) enforceYearBoundaryScroll();
        syncScrollLeft(tableScroll);
        scheduleSnap();
      }, { passive: true });"""

FOCUS_BAR_STATE_OLD = """      function getFocusedRowState() {
        var rows = rowsRoot.children;
        if (!rows || !rows.length) return { row: null, offset: 0, idx: 0 };
        var rowPitch = 42;
        var rowHeight = 40;
        var tableRect = tableScroll.getBoundingClientRect();
        var anchorRect = lowerScroll ? lowerScroll.getBoundingClientRect() : tableRect;
        var anchorOffset = (anchorRect.top + anchorRect.height / 2) - tableRect.top;
        var firstRect = rows[0].getBoundingClientRect();
        var rowStart = tableScroll.scrollTop + (firstRect.top - tableRect.top);
        var anchorYInContent = tableScroll.scrollTop + anchorOffset;
        var idx = Math.round((anchorYInContent - (rowStart + rowHeight / 2)) / rowPitch);
        if (idx < 0) idx = 0;
        if (idx >= rows.length) idx = rows.length - 1;
        var idealTop = rowStart + idx * rowPitch + rowHeight / 2 - anchorOffset;
        var offset = tableScroll.scrollTop - idealTop;
        return { row: rows[idx], offset: offset, idx: idx };
      }"""

FOCUS_BAR_STATE_NEW = """      function getFocusedRowState() {
        var rows = rowsRoot.children;
        if (!rows || !rows.length) return { row: null, offset: 0, idx: 0 };
        var tableRect = tableScroll.getBoundingClientRect();
        var anchorRect = lowerScroll ? lowerScroll.getBoundingClientRect() : tableRect;
        var anchorOffset = (anchorRect.top + anchorRect.height / 2) - tableRect.top;
        var idx = 0;
        if (typeof window.__annualTwFocusRowIndex === 'function') {
          idx = window.__annualTwFocusRowIndex();
        } else {
          var bestDist = Infinity;
          for (var i = 0; i < rows.length; i++) {
            var rowRect = rows[i].getBoundingClientRect();
            var center = rowRect.top - tableRect.top + rowRect.height / 2;
            var dist = Math.abs(center - anchorOffset);
            if (dist < bestDist) {
              bestDist = dist;
              idx = i;
            }
          }
        }
        if (idx < 0) idx = 0;
        if (idx >= rows.length) idx = rows.length - 1;
        var rowRect = rows[idx].getBoundingClientRect();
        var rowCenterViewport = rowRect.top - tableRect.top + rowRect.height / 2;
        var offset = rowCenterViewport - anchorOffset;
        return { row: rows[idx], offset: offset, idx: idx };
      }"""


def _apply(text: str, old: str, new: str, label: str) -> str:
    if old in text:
        return text.replace(old, new, 1)
    if MARKER in text and label in ("focus index", "enforce", "schedule", "scroll", "focus state"):
        return text
    raise ValueError(f"{label}: anchor not found")


def main() -> int:
    for path in PAGES:
        text = path.read_text(encoding="utf-8")
        if MARKER in text:
            print(f"skip (already applied): {path.relative_to(ROOT)}")
            continue
        text = _apply(text, FOCUS_INDEX_OLD, FOCUS_INDEX_NEW, "focus index")
        text = _apply(text, ENFORCE_BLOCK, ENFORCE_BLOCK_NEW, "enforce")
        text = _apply(text, SCHEDULE_SNAP_OLD, SCHEDULE_SNAP_NEW, "schedule")
        text = _apply(text, SCROLL_LISTENER_OLD, SCROLL_LISTENER_NEW, "scroll")
        text = _apply(text, FOCUS_BAR_STATE_OLD, FOCUS_BAR_STATE_NEW, "focus state")
        path.write_text(text, encoding="utf-8")
        print(f"applied: {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
