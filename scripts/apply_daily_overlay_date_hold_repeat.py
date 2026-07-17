#!/usr/bin/env python3
"""Daily Floating Window — 日付 ◀︎▶︎ の押しっぱなし連打."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

MARKER = "bindDailyOverlayDateHoldRepeat"

CLICK_OLD = """      if (prevDayBtn) {
        prevDayBtn.addEventListener('click', function () {
          selectedIso = shiftIso(selectedIso || resolveIso(), -1);
          fill(selectedIso);
        });
      }
      if (nextDayBtn) {
        nextDayBtn.addEventListener('click', function () {
          selectedIso = shiftIso(selectedIso || resolveIso(), 1);
          fill(selectedIso);
        });
      }"""

HOLD_NEW = """      function bindDailyOverlayDateHoldRepeat(btn, delta) {
        if (!btn) return;
        var delayId = null;
        var repeatId = null;
        function clearHold() {
          if (delayId != null) { clearTimeout(delayId); delayId = null; }
          if (repeatId != null) { clearInterval(repeatId); repeatId = null; }
        }
        function stepOnce() {
          selectedIso = shiftIso(selectedIso || resolveIso(), delta);
          fill(selectedIso);
        }
        function onPointerDown(ev) {
          if (ev.pointerType === 'mouse' && ev.button !== 0) return;
          ev.preventDefault();
          try { btn.setPointerCapture(ev.pointerId); } catch (_capErr) {}
          clearHold();
          stepOnce();
          delayId = setTimeout(function () {
            repeatId = setInterval(stepOnce, 75);
          }, 400);
        }
        function onPointerUp() { clearHold(); }
        btn.addEventListener('pointerdown', onPointerDown);
        btn.addEventListener('pointerup', onPointerUp);
        btn.addEventListener('pointercancel', onPointerUp);
        btn.addEventListener('lostpointercapture', onPointerUp);
        btn.addEventListener('keydown', function (ev) {
          if (ev.key !== 'Enter' && ev.key !== ' ') return;
          ev.preventDefault();
          stepOnce();
        });
      }
      bindDailyOverlayDateHoldRepeat(prevDayBtn, -1);
      bindDailyOverlayDateHoldRepeat(nextDayBtn, 1);"""


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        print(f"skip (already) {path.relative_to(ROOT)}")
        return
    if CLICK_OLD not in text:
        raise SystemExit(f"daily overlay click handlers miss: {path}")
    text = text.replace(CLICK_OLD, HOLD_NEW, 1)
    if MARKER not in text:
        raise SystemExit(f"{MARKER} missing after patch: {path}")
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> int:
    for path in PAGES:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_page(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
