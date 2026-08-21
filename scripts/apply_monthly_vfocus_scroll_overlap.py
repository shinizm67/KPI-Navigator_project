#!/usr/bin/env python3
"""Stop Monthly vFocus overlay from ghosting TW during horizontal scroll."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "zh-tw/app/monthly/index.html",
]

FILL_OLD = """    .monthly-vfocus-fill {
      position: absolute;
      left: 1px;
      right: 1px;
      top: var(--monthly-vfocus-fill-top);
      bottom: 18px;
      z-index: 1;
      display: flex;
      align-items: flex-start;
      justify-content: center;
      box-sizing: border-box;
      overflow: hidden;
      pointer-events: none;
    }"""

FILL_NEW = """    .monthly-vfocus-fill {
      position: absolute;
      left: 1px;
      right: 1px;
      top: var(--monthly-vfocus-fill-top);
      bottom: 18px;
      z-index: 1;
      display: flex;
      align-items: flex-start;
      justify-content: center;
      box-sizing: border-box;
      overflow: hidden;
      pointer-events: none;
      background: #000;
      isolation: isolate;
    }
    .office-mode .monthly-vfocus-fill {
      background: #2a2a2a;
    }"""

BAR_OLD = """    .monthly-vertical-focus-bar {
      position: absolute;
      left: 498px;
      top: var(--monthly-vfocus-bar-top);
      width: 135px;
      height: var(--monthly-vfocus-frame-h);
      z-index: 5;
      pointer-events: none;
    }"""

BAR_NEW = """    .monthly-vertical-focus-bar {
      position: absolute;
      left: 498px;
      top: var(--monthly-vfocus-bar-top);
      width: 135px;
      height: var(--monthly-vfocus-frame-h);
      z-index: 5;
      pointer-events: none;
      isolation: isolate;
      transform: translateZ(0);
    }"""

WILL_OLD = """      transform: translateX(-33.333333%);
      will-change: transform;
    }"""

WILL_NEW = """      transform: translateX(-33.333333%);
    }"""

RAF_OLD = """      var vFocusRaf = null;"""

RAF_NEW = """      var vFocusRaf = null;
      var __vfocusLastIdx = null;"""

EMPTY_OLD = """        if (n === 0) {
          syncMonthlyVfocusYearBadge(NaN);"""

EMPTY_NEW = """        if (n === 0) {
          __vfocusLastIdx = null;
          syncMonthlyVfocusYearBadge(NaN);"""

LANE_OLD = """        fillLane(0, idx - 1);
        fillLane(1, idx);
        fillLane(2, idx + 1);
        function syncVFocusLaneTwState(laneEl, colIdx) {
          if (!laneEl) return;
          laneEl.classList.remove('monthly-vfocus-lane--tw-off', 'monthly-vfocus-lane--tw-buffer');
          if (colIdx < 0 || colIdx >= n) return;
          var h = trackDate.children[colIdx];
          if (!h) return;
          if (h.classList.contains('monthly-date-header-cell--buffer')) {
            laneEl.classList.add('monthly-vfocus-lane--tw-buffer');
          } else if (h.classList.contains('monthly-date-header-cell--off')) {
            laneEl.classList.add('monthly-vfocus-lane--tw-off');
          }
        }
        syncVFocusLaneTwState(vLanePrev, idx - 1);
        syncVFocusLaneTwState(vLaneCenter, idx);
        syncVFocusLaneTwState(vLaneNext, idx + 1);
        if (vFocusLanesEl && vFocusStackEl) {
          var laneW = vFocusStackEl.clientWidth;
          var shift = -laneW * (1 + frac);
          vFocusLanesEl.style.transform = 'translateX(' + shift + 'px)';
        }

        var hdr = trackDate.children[idx];
        if (hdr) {
          currentFocusIso = hdr.getAttribute('data-iso') || currentFocusIso;
          var isoNow = hdr.getAttribute('data-iso');
          if (isoNow) {
            syncArea2ByIso(isoNow);
            syncMonthlyVfocusYearBadge(isoNow);
          }
        }"""

LANE_NEW = """        if (vFocusLanesEl && vFocusStackEl) {
          var laneW = vFocusStackEl.clientWidth;
          var shift = -laneW * (1 + frac);
          vFocusLanesEl.style.transform = 'translateX(' + shift + 'px)';
        }
        if (__vfocusLastIdx === idx) return;
        __vfocusLastIdx = idx;
        fillLane(0, idx - 1);
        fillLane(1, idx);
        fillLane(2, idx + 1);
        function syncVFocusLaneTwState(laneEl, colIdx) {
          if (!laneEl) return;
          laneEl.classList.remove('monthly-vfocus-lane--tw-off', 'monthly-vfocus-lane--tw-buffer');
          if (colIdx < 0 || colIdx >= n) return;
          var h = trackDate.children[colIdx];
          if (!h) return;
          if (h.classList.contains('monthly-date-header-cell--buffer')) {
            laneEl.classList.add('monthly-vfocus-lane--tw-buffer');
          } else if (h.classList.contains('monthly-date-header-cell--off')) {
            laneEl.classList.add('monthly-vfocus-lane--tw-off');
          }
        }
        syncVFocusLaneTwState(vLanePrev, idx - 1);
        syncVFocusLaneTwState(vLaneCenter, idx);
        syncVFocusLaneTwState(vLaneNext, idx + 1);

        var hdr = trackDate.children[idx];
        if (hdr) {
          currentFocusIso = hdr.getAttribute('data-iso') || currentFocusIso;
          var isoNow = hdr.getAttribute('data-iso');
          if (isoNow) {
            syncArea2ByIso(isoNow);
            syncMonthlyVfocusYearBadge(isoNow);
          }
        }"""

BUSY_OLD = """        window.__monthlyTwColumnsBusy = true;
        var alreadyShown =
          document.documentElement.getAttribute('data-monthly-tw-hydrated') === '1';"""

BUSY_NEW = """        window.__monthlyTwColumnsBusy = true;
        __vfocusLastIdx = null;
        var alreadyShown =
          document.documentElement.getAttribute('data-monthly-tw-hydrated') === '1';"""


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
        text = replace_once(text, FILL_OLD, FILL_NEW, "fill", path)
        text = replace_once(text, BAR_OLD, BAR_NEW, "bar", path)
        text = replace_once(text, WILL_OLD, WILL_NEW, "will-change", path)
        text = replace_once(text, RAF_OLD, RAF_NEW, "raf", path)
        text = replace_once(text, EMPTY_OLD, EMPTY_NEW, "empty", path)
        text = replace_once(text, LANE_OLD, LANE_NEW, "lanes", path)
        text = replace_once(text, BUSY_OLD, BUSY_NEW, "rebuild-reset", path)
        path.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
