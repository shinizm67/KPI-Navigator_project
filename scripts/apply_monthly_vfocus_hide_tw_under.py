#!/usr/bin/env python3
"""Hide TW columns under Monthly vFocus so overlay and table cannot double-draw."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "zh-tw/app/monthly/index.html",
]

FILL_OLD = """      pointer-events: none;
      background: #000;
      isolation: isolate;
    }
    .office-mode .monthly-vfocus-fill {
      background: #2a2a2a;
    }"""

FILL_NEW = """      pointer-events: none;
      background: #000;
      isolation: isolate;
      contain: paint;
    }
    .office-mode .monthly-vfocus-fill {
      background: #2a2a2a;
    }"""

BAR_OLD = """      z-index: 5;
      pointer-events: none;
      isolation: isolate;
      transform: translateZ(0);
    }"""

BAR_NEW = """      z-index: 30;
      pointer-events: none;
      isolation: isolate;
      transform: translate3d(0, 0, 1px);
    }"""

LANE_BG_OLD = """    .monthly-vfocus-lane {
      flex: 0 0 33.333333%;
      min-width: 0;
      display: flex;
      flex-direction: column;
      align-items: stretch;
      box-sizing: border-box;
    }"""

LANE_BG_NEW = """    .monthly-vfocus-lane {
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

SIDE_OLD = """    body:not(.office-mode) .monthly-vfocus-lane--side {
      opacity: 0.42;
    }"""

SIDE_NEW = """    body:not(.office-mode) .monthly-vfocus-lane--side {
      opacity: 1;
    }"""

RAF_OLD = """      var vFocusRaf = null;
      var __vfocusLastIdx = null;"""

RAF_NEW = """      var vFocusRaf = null;
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

EMPTY_OLD = """        if (n === 0) {
          __vfocusLastIdx = null;
          syncMonthlyVfocusYearBadge(NaN);"""

EMPTY_NEW = """        if (n === 0) {
          __vfocusLastIdx = null;
          setTwColsUnderVfocus([]);
          syncMonthlyVfocusYearBadge(NaN);"""

TRANSFORM_OLD = """        if (vFocusLanesEl && vFocusStackEl) {
          var laneW = vFocusStackEl.clientWidth;
          var shift = -laneW * (1 + frac);
          vFocusLanesEl.style.transform = 'translateX(' + shift + 'px)';
        }
        if (__vfocusLastIdx === idx) return;"""

TRANSFORM_NEW = """        if (vFocusLanesEl && vFocusStackEl) {
          var laneW = vFocusStackEl.clientWidth;
          var shift = -laneW * (1 + frac);
          vFocusLanesEl.style.transform = 'translateX(' + shift + 'px)';
        }
        hideTwColsUnderVfocusBar(idx, n);
        if (__vfocusLastIdx === idx) return;"""

BUSY_OLD = """        window.__monthlyTwColumnsBusy = true;
        __vfocusLastIdx = null;"""

BUSY_NEW = """        window.__monthlyTwColumnsBusy = true;
        __vfocusLastIdx = null;
        __vfocusHiddenCols = [];"""


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


def main() -> int:
    for path in TARGETS:
        text = path.read_text(encoding="utf-8")
        text = replace_once(text, FILL_OLD, FILL_NEW, "fill-hide", path)
        text = replace_once(text, BAR_OLD, BAR_NEW, "bar-z", path)
        text = replace_once(text, LANE_BG_OLD, LANE_BG_NEW, "lane-bg", path)
        text = replace_once(text, SIDE_OLD, SIDE_NEW, "side-opacity", path)
        text = replace_once(text, RAF_OLD, RAF_NEW, "hide-helpers", path)
        text = replace_once(text, EMPTY_OLD, EMPTY_NEW, "empty-clear", path)
        text = replace_once(text, TRANSFORM_OLD, TRANSFORM_NEW, "hide-on-scroll", path)
        text = replace_once(text, BUSY_OLD, BUSY_NEW, "rebuild-reset", path)
        path.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
