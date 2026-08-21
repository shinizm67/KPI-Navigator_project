#!/usr/bin/env python3
"""Annual TW spacer virtualization: keep year+14 logical list, DOM is Focus ±28 only."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "zh-tw/app/annual/index.html",
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "zh-tw/app/monthly/index.html",
]


def replace_once(text: str, old: str, new: str, label: str, path: Path) -> str:
    cnt = text.count(old)
    if cnt == 0:
        if new in text:
            print(f"  skip {label} (already) {path.relative_to(ROOT)}")
            return text
        raise SystemExit(f"  ERROR {label} not found: {path.relative_to(ROOT)}")
    if cnt != 1:
        raise SystemExit(f"  ERROR {label} found {cnt}: {path.relative_to(ROOT)}")
    print(f"  patch {label} {path.relative_to(ROOT)}")
    return text.replace(old, new, 1)


CSS_OLD = """    .annual-daily-rows {
      display: flex;
      flex-direction: column;
      gap: 2px;
      width: 600px;
      max-width: none;
      margin: 0;
      padding: 0;
    }"""

CSS_NEW = """    .annual-daily-rows {
      display: flex;
      flex-direction: column;
      gap: 2px;
      width: 600px;
      max-width: none;
      margin: 0;
      padding: 0;
    }
    /* KPI-TW-SPACER: 年+14日の高さは残し、実DOM行は Focus 前後だけ */
    .annual-daily-rows-spacer {
      flex: 0 0 auto;
      width: 100%;
      pointer-events: none;
      visibility: hidden;
    }"""

LOOP_HEAD_OLD = """        var prevYearMarker = null;
        for (var d = new Date(bounds.rangeStart); d <= bounds.rangeEnd; d.setDate(d.getDate() + 1)) {
          var iso =
            d.getFullYear() +
            '-' +
            pad2(d.getMonth() + 1) +
            '-' +
            pad2(d.getDate());"""

LOOP_HEAD_NEW = """        var logicalDays = [];
        for (
          var dScan = new Date(bounds.rangeStart);
          dScan <= bounds.rangeEnd;
          dScan.setDate(dScan.getDate() + 1)
        ) {
          logicalDays.push(new Date(dScan.getFullYear(), dScan.getMonth(), dScan.getDate()));
        }
        var nLog = logicalDays.length;
        var activeFirst = -1;
        var activeLast = -1;
        for (var ai = 0; ai < nLog; ai++) {
          if (logicalDays[ai].getFullYear() === anchorYear) {
            if (activeFirst < 0) activeFirst = ai;
            activeLast = ai;
          }
        }
        rowsRoot.setAttribute('data-tw-logical-count', String(nLog));
        rowsRoot.setAttribute('data-tw-active-first', String(activeFirst));
        rowsRoot.setAttribute('data-tw-active-last', String(activeLast));
        var focusIdxPaint = 0;
        var focusIsoPaint = String(bounds.focusIso || '');
        for (var fi = 0; fi < nLog; fi++) {
          if (twLocalIso(logicalDays[fi]) === focusIsoPaint) {
            focusIdxPaint = fi;
            break;
          }
        }
        var halfPaint = typeof TW_DRAW_HALF_DAYS === 'number' ? TW_DRAW_HALF_DAYS : 28;
        function paintTwVisibleRows(centerIdx) {
          centerIdx = Number(centerIdx);
          if (!Number.isFinite(centerIdx)) centerIdx = 0;
          if (centerIdx < 0) centerIdx = 0;
          if (centerIdx >= nLog) centerIdx = nLog - 1;
          var visLo = Math.max(0, centerIdx - halfPaint);
          var visHi = Math.min(nLog - 1, centerIdx + halfPaint);
          rowsRoot.setAttribute('data-tw-vis-lo', String(visLo));
          rowsRoot.setAttribute('data-tw-vis-hi', String(visHi));
          if (logicalDays[visLo]) seedTwCumUpTo(logicalDays[visLo]);
          var frag = document.createDocumentFragment();
          var spB = document.createElement('div');
          spB.className = 'annual-daily-rows-spacer annual-daily-rows-spacer--before';
          spB.setAttribute('aria-hidden', 'true');
          spB.style.height = visLo * 42 + 'px';
          frag.appendChild(spB);
        var prevYearMarker = null;
        for (var pi = visLo; pi <= visHi; pi++) {
          var d = logicalDays[pi];
          var iso =
            d.getFullYear() +
            '-' +
            pad2(d.getMonth() + 1) +
            '-' +
            pad2(d.getDate());"""

LOOP_TAIL_OLD = """          row.appendChild(groupBase);
          row.appendChild(groupMonthly);
          row.appendChild(groupAnnual);
          rowsRoot.appendChild(row);
        }"""

LOOP_TAIL_NEW = """          row.appendChild(groupBase);
          row.appendChild(groupMonthly);
          row.appendChild(groupAnnual);
          row.setAttribute('data-tw-logical-idx', String(pi));
          frag.appendChild(row);
        }
          var spA = document.createElement('div');
          spA.className = 'annual-daily-rows-spacer annual-daily-rows-spacer--after';
          spA.setAttribute('aria-hidden', 'true');
          spA.style.height = Math.max(0, nLog - visHi - 1) * 42 + 'px';
          frag.appendChild(spA);
          rowsRoot.replaceChildren(frag);
          if (typeof __geomCache !== 'undefined') __geomCache = null;
          if (typeof __anchorRangeCache !== 'undefined') __anchorRangeCache = null;
        }
        window.__paintTwVisibleWindow = function (iso) {
          if (!iso || !nLog) return false;
          var idx = -1;
          for (var qi = 0; qi < nLog; qi++) {
            if (twLocalIso(logicalDays[qi]) === String(iso)) {
              idx = qi;
              break;
            }
          }
          if (idx < 0) return false;
          var lo = Number(rowsRoot.getAttribute('data-tw-vis-lo'));
          var hi = Number(rowsRoot.getAttribute('data-tw-vis-hi'));
          var edge = typeof TW_DRAW_EDGE_DAYS === 'number' ? TW_DRAW_EDGE_DAYS : 7;
          if (!Number.isFinite(lo) || idx < lo || idx > hi || idx <= lo + edge || idx >= hi - edge) {
            paintTwVisibleRows(idx);
          }
          return true;
        };
        window.__ensureTwDrawWindow = function (iso) {
          if (!window.__paintTwVisibleWindow(iso)) return false;
          if (window.__ANNUAL_UI && typeof window.__ANNUAL_UI.scrollTableToIso === 'function') {
            return !!window.__ANNUAL_UI.scrollTableToIso(String(iso), { lockMs: 400 });
          }
          return alignTwFocusIso(iso);
        };
        window.__twMaybeShiftVisibleWindow = function () {
          var n = Number(rowsRoot.getAttribute('data-tw-logical-count') || 0);
          var lo = Number(rowsRoot.getAttribute('data-tw-vis-lo'));
          var hi = Number(rowsRoot.getAttribute('data-tw-vis-hi'));
          if (!n || !Number.isFinite(lo) || !Number.isFinite(hi)) return;
          var idx = 0;
          if (typeof window.__annualTwFocusRowIndex === 'function') {
            idx = window.__annualTwFocusRowIndex();
          }
          if (idx < 0) idx = 0;
          if (idx >= n) idx = n - 1;
          var edge = typeof TW_DRAW_EDGE_DAYS === 'number' ? TW_DRAW_EDGE_DAYS : 7;
          if (idx > lo + edge && idx < hi - edge) return;
          var nextLo = Math.max(0, idx - halfPaint);
          var nextHi = Math.min(n - 1, idx + halfPaint);
          if (nextLo === lo && nextHi === hi) return;
          paintTwVisibleRows(idx);
        };
        paintTwVisibleRows(focusIdxPaint);"""

GEOM_OLD = """      function getAnnualGeom() {
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
      }"""

GEOM_NEW = """      function getAnnualGeom() {
        if (__geomCache) return __geomCache;
        var rowsRootEl = document.getElementById('annual-daily-rows');
        var rows = document.querySelectorAll('#annual-daily-rows .annual-daily-row');
        var visLo = Number(rowsRootEl && rowsRootEl.getAttribute('data-tw-vis-lo')) || 0;
        var logicalCount = Number(rowsRootEl && rowsRootEl.getAttribute('data-tw-logical-count')) || 0;
        var domCount = rows ? rows.length : 0;
        var count = logicalCount > 0 ? logicalCount : domCount;
        var centerHalf = SNAP_ROW_HEIGHT / 2;
        if (!rows || domCount < 1) {
          return { ok: false, rowStart: null, pitch: SNAP_ROW_PITCH, anchorOffset: 0, count: 0, maxTop: 0, centerHalf: centerHalf };
        }
        var tableRect = tableScroll.getBoundingClientRect();
        var r0 = rows[0].getBoundingClientRect();
        var pitch = SNAP_ROW_PITCH;
        if (domCount >= 2) {
          var p = rows[1].getBoundingClientRect().top - r0.top;
          if (p > 0) pitch = p;
        }
        var rowStart = tableScroll.scrollTop + (r0.top - tableRect.top) - visLo * pitch;
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
      }"""

ANCHOR_OLD = """      function anchorYearRowRange() {
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
      }"""

ANCHOR_NEW = """      function anchorYearRowRange() {
        if (__anchorRangeCache) return __anchorRangeCache;
        var root = document.getElementById('annual-daily-rows');
        var first = Number(root && root.getAttribute('data-tw-active-first'));
        var last = Number(root && root.getAttribute('data-tw-active-last'));
        var count = Number(root && root.getAttribute('data-tw-logical-count'));
        if (!Number.isFinite(first) || !Number.isFinite(last) || first < 0) {
          var rows = document.querySelectorAll('#annual-daily-rows .annual-daily-row');
          first = -1;
          last = -1;
          for (var i = 0; i < rows.length; i++) {
            if (rows[i].getAttribute('data-active-year') === '1') {
              if (first < 0) first = Number(rows[i].getAttribute('data-tw-logical-idx'));
              last = Number(rows[i].getAttribute('data-tw-logical-idx'));
            }
          }
          count = rows.length;
        }
        __anchorRangeCache = { first: first, last: last, count: count };
        return __anchorRangeCache;
      }"""

SYNC_ANNUAL_OLD = """      function syncDailyDateFromFocusedRowForIndex(idx) {
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

SYNC_ANNUAL_NEW = """      function syncDailyDateFromFocusedRowForIndex(idx) {
        var root = document.getElementById('annual-daily-rows');
        var row = root
          ? root.querySelector('.annual-daily-row[data-tw-logical-idx="' + idx + '"]')
          : null;
        if (!row) {
          if (window.__twMaybeShiftVisibleWindow) window.__twMaybeShiftVisibleWindow();
          row = root
            ? root.querySelector('.annual-daily-row[data-tw-logical-idx="' + idx + '"]')
            : null;
        }
        if (!row) return;
        var iso = row.getAttribute('data-iso-date');
        if (!iso) return;
        if (__focusDateLockIso && iso !== __focusDateLockIso) return;
        if (window.__ANNUAL_UI && typeof window.__ANNUAL_UI.setDailyDateByISO === 'function') {
          window.__ANNUAL_UI.setDailyDateByISO(iso, 'focus-sync');
        }
      }"""

SYNC_MONTHLY_OLD = """      function syncDailyDateFromFocusedRowForIndex(idx) {
        var rows = document.querySelectorAll('#annual-daily-rows .annual-daily-row');
        if (!rows || !rows.length) return;
        if (idx < 0 || idx >= rows.length) return;
        var iso = rows[idx].getAttribute('data-iso-date');
        if (!iso) return;
        syncCalendarYearFromIso(iso);
        if (window.__ANNUAL_UI && typeof window.__ANNUAL_UI.setDailyDateByISO === 'function') {
          window.__ANNUAL_UI.setDailyDateByISO(iso, 'focus-sync');
        }
      }"""

SYNC_MONTHLY_NEW = """      function syncDailyDateFromFocusedRowForIndex(idx) {
        var root = document.getElementById('annual-daily-rows');
        var row = root
          ? root.querySelector('.annual-daily-row[data-tw-logical-idx="' + idx + '"]')
          : null;
        if (!row) {
          if (window.__twMaybeShiftVisibleWindow) window.__twMaybeShiftVisibleWindow();
          row = root
            ? root.querySelector('.annual-daily-row[data-tw-logical-idx="' + idx + '"]')
            : null;
        }
        if (!row) return;
        var iso = row.getAttribute('data-iso-date');
        if (!iso) return;
        syncCalendarYearFromIso(iso);
        if (window.__ANNUAL_UI && typeof window.__ANNUAL_UI.setDailyDateByISO === 'function') {
          window.__ANNUAL_UI.setDailyDateByISO(iso, 'focus-sync');
        }
      }"""

MONTHLY_FOCUS_IDX_OLD = """      function getNearestFocusRowIndex() {
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
        var target = rowStart + idx * SNAP_ROW_PITCH + SNAP_ROW_HEIGHT / 2 - anchorOffset;"""

MONTHLY_FOCUS_IDX_NEW = """      function getNearestFocusRowIndex() {
        var root = document.getElementById('annual-daily-rows');
        var rows = document.querySelectorAll('#annual-daily-rows .annual-daily-row');
        if (!rows || !rows.length) return 0;
        var visLo = Number(root && root.getAttribute('data-tw-vis-lo')) || 0;
        var logicalCount = Number(root && root.getAttribute('data-tw-logical-count')) || rows.length;
        var rowStart = getRowStartYInContent();
        if (rowStart == null) return 0;
        rowStart -= visLo * SNAP_ROW_PITCH;
        var anchorOffset = getFocusAnchorOffsetY();
        var anchorYInContent = tableScroll.scrollTop + anchorOffset;
        var idx = Math.round((anchorYInContent - (rowStart + SNAP_ROW_HEIGHT / 2)) / SNAP_ROW_PITCH);
        if (idx < 0) idx = 0;
        if (idx >= logicalCount) idx = logicalCount - 1;
        return idx;
      }

      function getScrollTopForRowIndex(idx) {
        var root = document.getElementById('annual-daily-rows');
        var rows = document.querySelectorAll('#annual-daily-rows .annual-daily-row');
        if (!rows || !rows.length) return tableScroll.scrollTop;
        var visLo = Number(root && root.getAttribute('data-tw-vis-lo')) || 0;
        var logicalCount = Number(root && root.getAttribute('data-tw-logical-count')) || rows.length;
        var rowStart = getRowStartYInContent();
        if (rowStart == null) return tableScroll.scrollTop;
        rowStart -= visLo * SNAP_ROW_PITCH;
        if (idx < 0) idx = 0;
        if (idx >= logicalCount) idx = logicalCount - 1;
        var anchorOffset = getFocusAnchorOffsetY();
        var target = rowStart + idx * SNAP_ROW_PITCH + SNAP_ROW_HEIGHT / 2 - anchorOffset;"""

FOCUS_STATE_ANNUAL_OLD = """      function getFocusedRowState() {
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
        }"""

FOCUS_STATE_ANNUAL_NEW = """      function twDomRowByLogicalIdx(idx) {
        return rowsRoot.querySelector('.annual-daily-row[data-tw-logical-idx="' + idx + '"]');
      }
      function getFocusedRowState() {
        var rows = rowsRoot.querySelectorAll('.annual-daily-row');
        if (!rows || !rows.length) return { row: null, offset: 0, idx: 0 };
        var logicalCount = Number(rowsRoot.getAttribute('data-tw-logical-count')) || rows.length;
        /* KPI-ARP-PHASE5A: geom キャッシュがあれば reflow なしで算出 */
        if (typeof window.__annualGeom === 'function' && typeof window.__annualTwFocusRowIndex === 'function') {
          var g5a = window.__annualGeom();
          if (g5a && g5a.ok && g5a.rowStart != null) {
            var idx5a = window.__annualTwFocusRowIndex();
            if (idx5a < 0) idx5a = 0;
            if (idx5a >= logicalCount) idx5a = logicalCount - 1;
            var center5a = (g5a.rowStart + idx5a * g5a.pitch + g5a.centerHalf) - tableScroll.scrollTop;
            return { row: twDomRowByLogicalIdx(idx5a), offset: center5a - g5a.anchorOffset, idx: idx5a };
          }
        }"""

FOCUS_STATE_MONTHLY_OLD = """      function getFocusedRowState() {
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

FOCUS_STATE_MONTHLY_NEW = """      function getFocusedRowState() {
        var rows = rowsRoot.querySelectorAll('.annual-daily-row');
        if (!rows || !rows.length) return { row: null, offset: 0, idx: 0 };
        var rowPitch = 42;
        var rowHeight = 40;
        var visLo = Number(rowsRoot.getAttribute('data-tw-vis-lo')) || 0;
        var logicalCount = Number(rowsRoot.getAttribute('data-tw-logical-count')) || rows.length;
        var tableRect = tableScroll.getBoundingClientRect();
        var anchorRect = lowerScroll ? lowerScroll.getBoundingClientRect() : tableRect;
        var anchorOffset = (anchorRect.top + anchorRect.height / 2) - tableRect.top;
        var firstRect = rows[0].getBoundingClientRect();
        var rowStart = tableScroll.scrollTop + (firstRect.top - tableRect.top) - visLo * rowPitch;
        var anchorYInContent = tableScroll.scrollTop + anchorOffset;
        var idx = Math.round((anchorYInContent - (rowStart + rowHeight / 2)) / rowPitch);
        if (idx < 0) idx = 0;
        if (idx >= logicalCount) idx = logicalCount - 1;
        var idealTop = rowStart + idx * rowPitch + rowHeight / 2 - anchorOffset;
        var offset = tableScroll.scrollTop - idealTop;
        var row = rowsRoot.querySelector('.annual-daily-row[data-tw-logical-idx="' + idx + '"]');
        return { row: row, offset: offset, idx: idx };
      }"""

SCROLL_ISO_OLD = """      function scrollTableToIso(iso, opts) {
        opts = opts || {};
        if (!iso || !/^\\d{4}-\\d{2}-\\d{2}$/.test(String(iso))) return false;
        var rows = document.querySelectorAll('#annual-daily-rows .annual-daily-row');
        if (!rows || !rows.length) return false;
        var idx = -1;
        for (var i = 0; i < rows.length; i++) {
          if (
            rows[i].getAttribute('data-iso-date') === String(iso) &&
            rows[i].getAttribute('data-active-year') === '1'
          ) {
            idx = i;
            break;
          }
        }
        if (idx < 0) {
          for (var j = 0; j < rows.length; j++) {
            if (rows[j].getAttribute('data-iso-date') === String(iso)) {
              idx = j;
              break;
            }
          }
        }
        if (idx < 0) return false;"""

SCROLL_ISO_NEW = """      function scrollTableToIso(iso, opts) {
        opts = opts || {};
        if (!iso || !/^\\d{4}-\\d{2}-\\d{2}$/.test(String(iso))) return false;
        if (window.__paintTwVisibleWindow) window.__paintTwVisibleWindow(String(iso));
        var row = document.querySelector(
          '#annual-daily-rows .annual-daily-row[data-iso-date="' + String(iso) + '"]'
        );
        if (!row) return false;
        var idx = Number(row.getAttribute('data-tw-logical-idx'));
        if (!Number.isFinite(idx)) return false;"""

ANNUAL_SCROLL_OLD = """      tableScroll.addEventListener('scroll', function () {
        var st = tableScroll.scrollTop;
        if (st > lastScrollTop) lastScrollDir = 1;
        else if (st < lastScrollTop) lastScrollDir = -1;
        lastScrollTop = st;
        scheduleEnforceYearBoundary();
        syncScrollLeft(tableScroll);
        scheduleSnap();
      }, { passive: true });"""

ANNUAL_SCROLL_NEW = """      tableScroll.addEventListener('scroll', function () {
        var st = tableScroll.scrollTop;
        if (st > lastScrollTop) lastScrollDir = 1;
        else if (st < lastScrollTop) lastScrollDir = -1;
        lastScrollTop = st;
        if (window.__twMaybeShiftVisibleWindow) window.__twMaybeShiftVisibleWindow();
        scheduleEnforceYearBoundary();
        syncScrollLeft(tableScroll);
        scheduleSnap();
      }, { passive: true });"""

MONTHLY_SCROLL_OLD = """      tableScroll.addEventListener('scroll', function () {
        syncScrollLeft(tableScroll);
        scheduleSnap();
      }, { passive: true });"""

MONTHLY_SCROLL_NEW = """      tableScroll.addEventListener('scroll', function () {
        if (window.__twMaybeShiftVisibleWindow) window.__twMaybeShiftVisibleWindow();
        syncScrollLeft(tableScroll);
        scheduleSnap();
      }, { passive: true });"""

FOCUS_FALLBACK_OLD = """        if (idx < 0) idx = 0;
        if (idx >= rows.length) idx = rows.length - 1;
        var rowRect = rows[idx].getBoundingClientRect();
        var rowCenterViewport = rowRect.top - tableRect.top + rowRect.height / 2;
        var offset = rowCenterViewport - anchorOffset;
        return { row: rows[idx], offset: offset, idx: idx };
      }"""

FOCUS_FALLBACK_NEW = """        if (idx < 0) idx = 0;
        if (idx >= logicalCount) idx = logicalCount - 1;
        var rowEl = twDomRowByLogicalIdx(idx) || rows[0];
        var rowRect = rowEl.getBoundingClientRect();
        var rowCenterViewport = rowRect.top - tableRect.top + rowRect.height / 2;
        var offset = rowCenterViewport - anchorOffset;
        return { row: rowEl, offset: offset, idx: idx };
      }"""

ENSURE_OLD = """      window.__ensureTwDrawWindow = function (iso) {
        if (!iso || !/^\\d{4}-\\d{2}-\\d{2}$/.test(String(iso))) return false;
        var row = document.querySelector(
          '#annual-daily-rows .annual-daily-row[data-iso-date="' + iso + '"]'
        );
        if (!row) return false;
        if (window.__ANNUAL_UI && typeof window.__ANNUAL_UI.scrollTableToIso === 'function') {
          return !!window.__ANNUAL_UI.scrollTableToIso(String(iso), { lockMs: 400 });
        }
        return alignTwFocusIso(iso);
      };"""

# render now assigns __ensureTwDrawWindow; remove the later stale definition if present
ENSURE_NEW = """      /* KPI-TW-SPACER: __ensureTwDrawWindow は renderAnnualDailyTimeline 内で定義 */"""


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    rel = str(path.relative_to(ROOT))
    is_annual = "/annual/" in rel.replace("\\", "/")
    text = replace_once(text, CSS_OLD, CSS_NEW, "css", path)
    text = replace_once(text, LOOP_HEAD_OLD, LOOP_HEAD_NEW, "loop-head", path)
    text = replace_once(text, LOOP_TAIL_OLD, LOOP_TAIL_NEW, "loop-tail", path)
    if is_annual:
        text = replace_once(text, GEOM_OLD, GEOM_NEW, "geom", path)
        text = replace_once(text, ANCHOR_OLD, ANCHOR_NEW, "anchor-range", path)
        text = replace_once(text, SYNC_ANNUAL_OLD, SYNC_ANNUAL_NEW, "sync-idx", path)
        text = replace_once(text, FOCUS_STATE_ANNUAL_OLD, FOCUS_STATE_ANNUAL_NEW, "focus-state", path)
        text = replace_once(text, FOCUS_FALLBACK_OLD, FOCUS_FALLBACK_NEW, "focus-fallback", path)
        text = replace_once(text, SCROLL_ISO_OLD, SCROLL_ISO_NEW, "scroll-iso", path)
        text = replace_once(text, ANNUAL_SCROLL_OLD, ANNUAL_SCROLL_NEW, "scroll-shift", path)
        if ENSURE_OLD in text:
            text = replace_once(text, ENSURE_OLD, ENSURE_NEW, "ensure-stub", path)
        else:
            print(f"  skip ensure-stub (missing) {path.relative_to(ROOT)}")
    else:
        text = replace_once(text, MONTHLY_FOCUS_IDX_OLD, MONTHLY_FOCUS_IDX_NEW, "monthly-idx", path)
        text = replace_once(text, SYNC_MONTHLY_OLD, SYNC_MONTHLY_NEW, "sync-idx", path)
        text = replace_once(text, FOCUS_STATE_MONTHLY_OLD, FOCUS_STATE_MONTHLY_NEW, "focus-state", path)
        text = replace_once(text, MONTHLY_SCROLL_OLD, MONTHLY_SCROLL_NEW, "scroll-shift", path)
        if ENSURE_OLD in text:
            text = replace_once(text, ENSURE_OLD, ENSURE_NEW, "ensure-stub", path)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    for path in PAGES:
        print("==", path.relative_to(ROOT))
        patch_page(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
