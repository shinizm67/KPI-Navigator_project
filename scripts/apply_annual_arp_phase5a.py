#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARP-5a: Annual 年跨ぎスクロールの性能改善（第1弾）

対象: app/annual/index.html, en/app/annual/index.html

目的:
  #1 カクつき  -> スクロール hot path から getBoundingClientRect（強制 reflow）を排除
  #3 タイムラグ -> 年跨ぎ描画を DocumentFragment 一括挿入 + 重い表示同期を着地後に遅延

変更点:
  1) ジオメトリを描画後1回だけ実測しキャッシュ（getAnnualGeom）。
     getNearestFocusRowIndex / getScrollTopForRowIndex / getRowPitch をキャッシュ算術に置換。
  2) キャッシュ無効化を timelineRowsRendered / focusBarStateChanged / resize に接続。
  3) renderAnnualDailyTimeline: 行を DocumentFragment に構築して1回で挿入。
  4) crossYearByEdge: Cockpit 表示同期・営業日数同期を着地後の setTimeout に遅延。
  5) getFocusedRowState: geom キャッシュがあれば reflow なしで算出（fallback 温存）。

冪等: 'KPI-ARP-PHASE5A' が既に含まれていればスキップ。
"""

import sys
from pathlib import Path

FILES = [
    "app/annual/index.html",
    "en/app/annual/index.html",
]

MARKER = "KPI-ARP-PHASE5A"

# ---- 1) geometry block ------------------------------------------------------
OLD_GEOM = """      /* KPI-ARP-PHASE2E */
      /* KPI-ARP-PHASE2E: 実測ピッチ（行0/行1から算出）。O(1) */
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

NEW_GEOM = """      /* KPI-ARP-PHASE5A: ジオメトリは描画後1回だけ実測しキャッシュ（スクロール hot path から reflow を排除） */
      var __geomCache = null;
      function getAnnualGeom() {
        if (__geomCache) return __geomCache;
        var rows = document.querySelectorAll('#annual-daily-rows .annual-daily-row');
        var count = rows ? rows.length : 0;
        var centerHalf = SNAP_ROW_HEIGHT / 2;
        if (!rows || count < 1) {
          return { ok: false, rowStart: null, pitch: SNAP_ROW_PITCH, anchorOffset: 0, count: 0, maxTop: 0, centerHalf: centerHalf };
        }
        var tableRect = tableScroll.getBoundingClientRect();
        var r0 = rows[0].getBoundingClientRect();
        var pitch = SNAP_ROW_PITCH;
        if (count >= 2) {
          var p = rows[1].getBoundingClientRect().top - r0.top;
          if (p > 0) pitch = p;
        }
        var rowStart = tableScroll.scrollTop + (r0.top - tableRect.top);
        var anchorRect = lowerScroll ? lowerScroll.getBoundingClientRect() : tableRect;
        var anchorOffset = (anchorRect.top + anchorRect.height / 2) - tableRect.top;
        __geomCache = {
          ok: true,
          rowStart: rowStart,
          pitch: pitch,
          anchorOffset: anchorOffset,
          count: count,
          maxTop: tableScroll.scrollHeight - tableScroll.clientHeight,
          centerHalf: centerHalf
        };
        return __geomCache;
      }
      window.__annualGeom = getAnnualGeom;
      window.addEventListener('resize', function () { __geomCache = null; }, { passive: true });

      /* KPI-ARP-PHASE5A: 実測ピッチ（キャッシュ） */
      function getRowPitch() { return getAnnualGeom().pitch; }

      /* KPI-ARP-PHASE5A: Focus Bar アンカー最寄り行（キャッシュ算術・reflow なし） */
      function getNearestFocusRowIndex() {
        var g = getAnnualGeom();
        if (!g.ok || g.rowStart == null) return 0;
        var anchorYInContent = tableScroll.scrollTop + g.anchorOffset;
        var idx = Math.round((anchorYInContent - (g.rowStart + g.centerHalf)) / g.pitch);
        if (idx < 0) idx = 0;
        if (idx >= g.count) idx = g.count - 1;
        return idx;
      }

      /* KPI-ARP-PHASE5A: 行中心をアンカーに一致させる scrollTop（キャッシュ算術・reflow なし） */
      function getScrollTopForRowIndex(idx) {
        var g = getAnnualGeom();
        if (!g.ok || g.rowStart == null) return tableScroll.scrollTop;
        if (idx < 0) idx = 0;
        if (idx >= g.count) idx = g.count - 1;
        var target = g.rowStart + idx * g.pitch + g.centerHalf - g.anchorOffset;
        var maxTop = g.maxTop;
        if (maxTop <= 0) maxTop = tableScroll.scrollHeight - tableScroll.clientHeight;
        if (target < 0) target = 0;
        if (target > maxTop) target = maxTop;
        return target;
      }"""

# ---- 2) invalidation on timelineRowsRendered --------------------------------
OLD_TRR = """      document.addEventListener('annual:timelineRowsRendered', function () {
        __anchorRangeCache = null;
      });"""
NEW_TRR = """      document.addEventListener('annual:timelineRowsRendered', function () {
        __anchorRangeCache = null;
        __geomCache = null;
      });"""

# ---- 2b) invalidation on focusBarStateChanged -------------------------------
OLD_FBS = """      document.addEventListener('annual:focusBarStateChanged', function () {
        if (snapTimer) clearTimeout(snapTimer);
        snapping = false;
        syncScrollLeft(tableScroll);
      });"""
NEW_FBS = """      document.addEventListener('annual:focusBarStateChanged', function () {
        if (snapTimer) clearTimeout(snapTimer);
        snapping = false;
        __geomCache = null;
        __anchorRangeCache = null;
        syncScrollLeft(tableScroll);
      });"""

# ---- 3) DocumentFragment in render ------------------------------------------
OLD_FRAG_A = """        rowsRoot.innerHTML = '';
        rowsRoot.setAttribute('data-year', String(anchorYear));"""
NEW_FRAG_A = """        rowsRoot.innerHTML = '';
        /* KPI-ARP-PHASE5A: 行は DocumentFragment に構築し1回で挿入（reflow削減） */
        var __rowsFrag = document.createDocumentFragment();
        rowsRoot.setAttribute('data-year', String(anchorYear));"""

OLD_FRAG_B = """          row.appendChild(groupBase);
          row.appendChild(groupMonthly);
          row.appendChild(groupAnnual);
          rowsRoot.appendChild(row);
        }"""
NEW_FRAG_B = """          row.appendChild(groupBase);
          row.appendChild(groupMonthly);
          row.appendChild(groupAnnual);
          __rowsFrag.appendChild(row);
        }
        rowsRoot.appendChild(__rowsFrag);"""

# ---- 4) crossYearByEdge deferred syncs --------------------------------------
OLD_CROSS = """        snapping = true;
        window.__renderAnnualDailyTimeline(nextYear, {
          boundsHint: 'anchor-year-only',
          preserveScroll: false,
        });
        var yearBadge = document.getElementById('annual-daily-focus-tw-year');
        if (yearBadge) yearBadge.textContent = String(nextYear);
        /* KPI-ARP-PHASE4: Open 時の横スクロール位置をリセットして3グループを先頭に */
        if (body.classList.contains('annual-focus-bar-expanded')) {
          tableScroll.scrollLeft = 0;
          syncScrollLeft(tableScroll);
        }
        /* KPI-ARP-PHASE2B: Cockpit 年ナビ表示・営業日数を追従（表示のみ・副作用なし） */
        if (window.__ANNUAL_UI && typeof window.__ANNUAL_UI.setCalendarYearDisplayOnly === 'function') {
          window.__ANNUAL_UI.setCalendarYearDisplayOnly(nextYear);
        }
        if (
          window.__ANNUAL_UI &&
          typeof window.__ANNUAL_UI.syncBusinessDayDisplayFromDailyMap === 'function'
        ) {
          window.__ANNUAL_UI.syncBusinessDayDisplayFromDailyMap();
        }
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
          /* KPI-ARP-PHASE2B: 慣性スクロールを打ち消して境界日に確実に着地 */
          tableScroll.scrollTop = target;
          requestAnimationFrame(function () {
            tableScroll.scrollTop = target;
            requestAnimationFrame(function () {
              tableScroll.scrollTop = target;
            });
          });
          setTimeout(function () {
            snapping = false;
            syncDailyDateFromFocusedRowForIndex(idx);
            /* KPI-ARP-PHASE3: 年跨ぎ後に Focus Bar 行を確実に同期 */
            if (typeof window.__refreshAnnualFocusBarLower === 'function') {
              window.__refreshAnnualFocusBarLower();
            }
          }, 160);
        } else {
          snapping = false;
        }
        return true;"""

NEW_CROSS = """        snapping = true;
        window.__renderAnnualDailyTimeline(nextYear, {
          boundsHint: 'anchor-year-only',
          preserveScroll: false,
        });
        var yearBadge = document.getElementById('annual-daily-focus-tw-year');
        if (yearBadge) yearBadge.textContent = String(nextYear);
        /* KPI-ARP-PHASE4: Open 時の横スクロール位置をリセットして3グループを先頭に */
        if (body.classList.contains('annual-focus-bar-expanded')) {
          tableScroll.scrollLeft = 0;
          syncScrollLeft(tableScroll);
        }
        var iso = dir > 0 ? nextYear + '-01-01' : nextYear + '-12-31';
        /* KPI-ARP-PHASE5A: 重い表示同期（Cockpit 年ナビ・営業日数）は着地後に遅延実行 */
        function __arpDeferredYearSync() {
          if (window.__ANNUAL_UI && typeof window.__ANNUAL_UI.setCalendarYearDisplayOnly === 'function') {
            window.__ANNUAL_UI.setCalendarYearDisplayOnly(nextYear);
          }
          if (
            window.__ANNUAL_UI &&
            typeof window.__ANNUAL_UI.syncBusinessDayDisplayFromDailyMap === 'function'
          ) {
            window.__ANNUAL_UI.syncBusinessDayDisplayFromDailyMap();
          }
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
          /* KPI-ARP-PHASE2B: 慣性スクロールを打ち消して境界日に確実に着地 */
          tableScroll.scrollTop = target;
          requestAnimationFrame(function () {
            tableScroll.scrollTop = target;
            requestAnimationFrame(function () {
              tableScroll.scrollTop = target;
            });
          });
          setTimeout(function () {
            snapping = false;
            syncDailyDateFromFocusedRowForIndex(idx);
            __arpDeferredYearSync();
            /* KPI-ARP-PHASE3: 年跨ぎ後に Focus Bar 行を確実に同期 */
            if (typeof window.__refreshAnnualFocusBarLower === 'function') {
              window.__refreshAnnualFocusBarLower();
            }
          }, 160);
        } else {
          __arpDeferredYearSync();
          if (window.__ANNUAL_UI && typeof window.__ANNUAL_UI.setDailyDateByISO === 'function') {
            window.__ANNUAL_UI.setDailyDateByISO(iso, 'focus-sync');
          }
          snapping = false;
        }
        return true;"""

# ---- 5) getFocusedRowState fast path ----------------------------------------
OLD_FRS = """      function getFocusedRowState() {
        var rows = rowsRoot.children;
        if (!rows || !rows.length) return { row: null, offset: 0, idx: 0 };
        var tableRect = tableScroll.getBoundingClientRect();"""
NEW_FRS = """      function getFocusedRowState() {
        var rows = rowsRoot.children;
        if (!rows || !rows.length) return { row: null, offset: 0, idx: 0 };
        /* KPI-ARP-PHASE5A: geom キャッシュがあれば reflow なしで算出 */
        if (typeof window.__annualGeom === 'function' && typeof window.__annualTwFocusRowIndex === 'function') {
          var g5a = window.__annualGeom();
          if (g5a && g5a.ok && g5a.rowStart != null) {
            var idx5a = window.__annualTwFocusRowIndex();
            if (idx5a < 0) idx5a = 0;
            if (idx5a >= rows.length) idx5a = rows.length - 1;
            var center5a = (g5a.rowStart + idx5a * g5a.pitch + g5a.centerHalf) - tableScroll.scrollTop;
            return { row: rows[idx5a], offset: center5a - g5a.anchorOffset, idx: idx5a };
          }
        }
        var tableRect = tableScroll.getBoundingClientRect();"""

EDITS = [
    ("geometry block", OLD_GEOM, NEW_GEOM),
    ("timelineRowsRendered invalidation", OLD_TRR, NEW_TRR),
    ("focusBarStateChanged invalidation", OLD_FBS, NEW_FBS),
    ("render fragment decl", OLD_FRAG_A, NEW_FRAG_A),
    ("render fragment append", OLD_FRAG_B, NEW_FRAG_B),
    ("crossYearByEdge deferred sync", OLD_CROSS, NEW_CROSS),
    ("getFocusedRowState fast path", OLD_FRS, NEW_FRS),
]


def apply_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        print(f"  SKIP (already applied): {path}")
        return False
    for name, old, new in EDITS:
        cnt = text.count(old)
        if cnt != 1:
            raise SystemExit(
                f"  ERROR in {path}: expected exactly 1 occurrence of "
                f"[{name}], found {cnt}"
            )
        text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")
    print(f"  OK: {path}")
    return True


def main():
    root = Path(__file__).resolve().parent.parent
    changed = 0
    for rel in FILES:
        p = root / rel
        if not p.exists():
            print(f"  MISSING: {p}")
            continue
        if apply_file(p):
            changed += 1
    print(f"Done. {changed} file(s) changed.")


if __name__ == "__main__":
    main()
