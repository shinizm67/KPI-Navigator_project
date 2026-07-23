#!/usr/bin/env python3
"""Insight date ◀︎▶︎ hold: mark holding, defer settle / dateChanged until release."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from insight_diff_client import (  # noqa: E402
    INSIGHT_DIFF_JS_END,
    INSIGHT_DIFF_JS_MARKER,
    INSIGHT_FILL_NEW,
    INSIGHT_OVERLAY_IIFE,
    insight_diff_js,
)

PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

HOLD_OLD = """      function bindInsightDateHoldRepeat(btn, delta) {
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
      }"""

HOLD_NEW = """      function bindInsightDateHoldRepeat(btn, delta) {
        if (!btn) return;
        var delayId = null;
        var repeatId = null;
        function clearHoldTimers() {
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
          clearHoldTimers();
          if (typeof window.__insightDateHoldStart === 'function') {
            window.__insightDateHoldStart();
          } else {
            window.__INSIGHT_DATE_HOLDING = true;
          }
          stepOnce();
          delayId = setTimeout(function () {
            repeatId = setInterval(stepOnce, 75);
          }, 400);
        }
        function onPointerUp() {
          clearHoldTimers();
          if (typeof window.__insightDateHoldEnd === 'function') {
            window.__insightDateHoldEnd();
          } else {
            window.__INSIGHT_DATE_HOLDING = false;
          }
        }
        btn.addEventListener('pointerdown', onPointerDown);
        btn.addEventListener('pointerup', onPointerUp);
        btn.addEventListener('pointercancel', onPointerUp);
        btn.addEventListener('lostpointercapture', onPointerUp);
        btn.addEventListener('keydown', function (ev) {
          if (ev.key !== 'Enter' && ev.key !== ' ') return;
          ev.preventDefault();
          stepOnce();
        });
      }"""


def inject_insight_diff_js(text: str) -> str:
    block = insight_diff_js().rstrip() + "\n"
    if INSIGHT_DIFF_JS_MARKER not in text:
        pos = text.find(INSIGHT_OVERLAY_IIFE)
        if pos < 0:
            raise SystemExit("insight-overlay IIFE anchor miss")
        return text[:pos] + block + text[pos:]
    pattern = (
        re.escape(INSIGHT_DIFF_JS_MARKER)
        + r"[\s\S]*?"
        + re.escape(INSIGHT_DIFF_JS_END)
        + r"\n?"
    )
    return re.sub(pattern, lambda _m: block.rstrip() + "\n", text, count=1)


def patch_fill(text: str) -> str:
    fill_pat = re.compile(
        r"      function fill\(iso\) \{\n"
        r"        iso = iso \|\| resolveIso\(\);\n"
        r"        if \(dateBtnEl\) dateBtnEl\.textContent = fmtDate\(iso\);\n"
        r"[\s\S]*?"
        r"            runInsightFillHeavy\(\);\n"
        r"          \}\);\n"
        r"        \}\);\n"
        r"      \}"
    )
    m = fill_pat.search(text)
    if not m:
        raise SystemExit("coalesced fill(iso) miss")
    return text[: m.start()] + INSIGHT_FILL_NEW + text[m.end() :]


def patch_hold(text: str) -> str:
    if "__insightDateHoldStart" in text and "clearHoldTimers" in text:
        return text
    if HOLD_OLD not in text:
        raise SystemExit("bindInsightDateHoldRepeat miss")
    return text.replace(HOLD_OLD, HOLD_NEW, 1)


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = inject_insight_diff_js(text)
    text = patch_fill(text)
    text = patch_hold(text)
    for needle in (
        "__insightDateHoldStart",
        "__insightDateHoldEnd",
        "__INSIGHT_DATE_HOLDING",
        "var holding = !!window.__INSIGHT_DATE_HOLDING",
        "__INSIGHT_YEAR_EXPENSE_CACHE",
    ):
        if needle not in text:
            raise SystemExit(f"missing {needle}: {path}")
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
