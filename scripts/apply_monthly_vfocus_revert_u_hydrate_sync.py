#!/usr/bin/env python3
"""Revert Step U clip-path (it punched holes). Keep overlay copy in sync after DB hydrate."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
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


FILL_OLD = """      pointer-events: none;
      background: #000;
      isolation: isolate;
      contain: paint;
    }"""

FILL_NEW = """      pointer-events: none;
      background: #000;
      isolation: isolate;
    }"""

BAR_OLD = """      z-index: 30;
      pointer-events: none;
      isolation: isolate;
      transform: translate3d(0, 0, 1px);
    }"""

BAR_NEW = """      z-index: 5;
      pointer-events: none;
      isolation: isolate;
      transform: translateZ(0);
    }"""

LANE_BG_OLD = """    .monthly-vfocus-lane {
      flex: 0 0 33.333333%;
      min-width: 0;
      display: flex;
      flex-direction: column;
      align-items: stretch;
      box-sizing: border-box;
      background: #000;
    }
    .office-mode .monthly-vfocus-lane {
      background: #2a2a2a;
    }"""

LANE_BG_NEW = """    .monthly-vfocus-lane {
      flex: 0 0 33.333333%;
      min-width: 0;
      display: flex;
      flex-direction: column;
      align-items: stretch;
      box-sizing: border-box;
    }"""

SIDE_OLD_JA = """    /* 左右レーンは帯内の窓送り。表と二重に見えないよう薄くしない */
    body:not(.office-mode) .monthly-vfocus-lane--side {
      opacity: 1;
    }"""

SIDE_NEW_JA = """    /* 左右レーン: Annual の ghost（opacity 0.42）に近い薄さ */
    body:not(.office-mode) .monthly-vfocus-lane--side {
      opacity: 0.42;
    }"""

SIDE_OLD = """    body:not(.office-mode) .monthly-vfocus-lane--side {
      opacity: 1;
    }"""

SIDE_NEW = """    body:not(.office-mode) .monthly-vfocus-lane--side {
      opacity: 0.42;
    }"""

HELPERS_OLD = """      var vFocusRaf = null;
      var __vfocusLastIdx = null;
      var __vfocusHiddenCols = [];
      var vFocusFillEl = document.querySelector('.monthly-vfocus-fill');
      function setTwColsUnderVfocus(clipItems) {
        var tracks = [trackDate, trackGroup1, trackGroup2, trackGroup3, trackProfit];
        function applyClip(i, clip) {
          for (var t = 0; t < tracks.length; t++) {
            var el = tracks[t] && tracks[t].children ? tracks[t].children[i] : null;
            if (!el) continue;
            if (clip) el.style.clipPath = clip;
            else el.style.removeProperty('clip-path');
          }
        }
        var keep = Object.create(null);
        for (var n1 = 0; n1 < clipItems.length; n1++) keep[clipItems[n1].i] = true;
        for (var o = 0; o < __vfocusHiddenCols.length; o++) {
          if (!keep[__vfocusHiddenCols[o]]) applyClip(__vfocusHiddenCols[o], '');
        }
        var next = [];
        for (var n2 = 0; n2 < clipItems.length; n2++) {
          applyClip(clipItems[n2].i, clipItems[n2].clip);
          next.push(clipItems[n2].i);
        }
        __vfocusHiddenCols = next;
      }
      function hideTwColsUnderVfocusBar(centerIdx, colCount) {
        var items = [];
        var box = vFocusFillEl || vFocusStackEl;
        if (!box || !trackGroup1 || !colCount) {
          setTwColsUnderVfocus(items);
          return;
        }
        var fr = box.getBoundingClientRect();
        var left = fr.left;
        var right = fr.right;
        var lo = Math.max(0, centerIdx - 2);
        var hi = Math.min(colCount - 1, centerIdx + 2);
        for (var i = lo; i <= hi; i++) {
          var col = trackGroup1.children[i];
          if (!col) continue;
          var r = col.getBoundingClientRect();
          if (r.right <= left || r.left >= right) continue;
          var clip;
          if (r.left >= left && r.right <= right) {
            clip = 'inset(0 100% 0 0)';
          } else if (r.left < left && r.right <= right) {
            clip = 'inset(0 ' + (r.right - left) + 'px 0 0)';
          } else if (r.left >= left && r.right > right) {
            clip = 'inset(0 0 0 ' + (right - r.left) + 'px)';
          } else {
            clip = 'inset(0 100% 0 0)';
          }
          items.push({ i: i, clip: clip });
        }
        setTwColsUnderVfocus(items);
      }"""

HELPERS_NEW = """      var vFocusRaf = null;
      var __vfocusLastIdx = null;"""

EMPTY_OLD = """        if (n === 0) {
          __vfocusLastIdx = null;
          setTwColsUnderVfocus([]);
          syncMonthlyVfocusYearBadge(NaN);"""

EMPTY_NEW = """        if (n === 0) {
          __vfocusLastIdx = null;
          syncMonthlyVfocusYearBadge(NaN);"""

TRANSFORM_OLD = """        if (vFocusLanesEl && vFocusStackEl) {
          var laneW = vFocusStackEl.clientWidth;
          var shift = -laneW * (1 + frac);
          vFocusLanesEl.style.transform = 'translateX(' + shift + 'px)';
        }
        hideTwColsUnderVfocusBar(idx, n);
        if (__vfocusLastIdx === idx) return;"""

TRANSFORM_NEW = """        if (vFocusLanesEl && vFocusStackEl) {
          var laneW = vFocusStackEl.clientWidth;
          var shift = -laneW * (1 + frac);
          vFocusLanesEl.style.transform = 'translateX(' + shift + 'px)';
        }
        if (__vfocusLastIdx === idx) return;"""

BUSY_OLD = """        window.__monthlyTwColumnsBusy = true;
        __vfocusLastIdx = null;
        __vfocusHiddenCols = [];"""

BUSY_NEW = """        window.__monthlyTwColumnsBusy = true;
        __vfocusLastIdx = null;"""

REFRESH_OLD = """        if (typeof scheduleVFocusUpdate === 'function') scheduleVFocusUpdate();
        return true;
      }
      window.__MONTHLY_UI = window.__MONTHLY_UI || {};
      window.__MONTHLY_UI.refreshMonthlyTwCellsInPlace = refreshMonthlyTwCellsInPlace;"""

REFRESH_NEW = """        __vfocusLastIdx = null;
        if (typeof scheduleVFocusUpdate === 'function') scheduleVFocusUpdate();
        return true;
      }
      window.__MONTHLY_UI = window.__MONTHLY_UI || {};
      window.__MONTHLY_UI.refreshMonthlyTwCellsInPlace = refreshMonthlyTwCellsInPlace;"""

LAZY_OLD = """          if (touched) scheduleVFocusUpdate();"""

LAZY_NEW = """          if (touched) {
            __vfocusLastIdx = null;
            scheduleVFocusUpdate();
          }"""

PHASE1_OLD = """          document.documentElement.setAttribute('data-monthly-tw-hydrated', '1');
          document.documentElement.setAttribute('data-monthly-tw-interactive', '1');
          scheduleVFocusUpdate();"""

PHASE1_NEW = """          document.documentElement.setAttribute('data-monthly-tw-hydrated', '1');
          document.documentElement.setAttribute('data-monthly-tw-interactive', '1');
          __vfocusLastIdx = null;
          scheduleVFocusUpdate();"""


def main() -> int:
    for path in TARGETS:
        text = path.read_text(encoding="utf-8")
        text = replace_once(text, FILL_OLD, FILL_NEW, "fill", path)
        text = replace_once(text, BAR_OLD, BAR_NEW, "bar", path)
        text = replace_once(text, LANE_BG_OLD, LANE_BG_NEW, "lane-bg", path)
        if SIDE_OLD_JA in text:
            text = replace_once(text, SIDE_OLD_JA, SIDE_NEW_JA, "side-ja", path)
        else:
            text = replace_once(text, SIDE_OLD, SIDE_NEW, "side", path)
        text = replace_once(text, HELPERS_OLD, HELPERS_NEW, "helpers", path)
        text = replace_once(text, EMPTY_OLD, EMPTY_NEW, "empty", path)
        text = replace_once(text, TRANSFORM_OLD, TRANSFORM_NEW, "transform", path)
        text = replace_once(text, BUSY_OLD, BUSY_NEW, "rebuild", path)
        text = replace_once(text, REFRESH_OLD, REFRESH_NEW, "refresh-sync", path)
        text = replace_once(text, LAZY_OLD, LAZY_NEW, "lazy-sync", path)
        text = replace_once(text, PHASE1_OLD, PHASE1_NEW, "phase1-sync", path)
        path.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
