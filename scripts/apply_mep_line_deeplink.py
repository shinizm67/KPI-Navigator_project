#!/usr/bin/env python3
"""MEP: ?line=<rowId> deep-link → scroll / focus / flash that expense row."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TARGETS = [
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
]

CSS_MARKER = "/* MEP-LINE-DEEPLINK-CSS */"
CSS_BLOCK = """    /* MEP-LINE-DEEPLINK-CSS */
    tr.mef-row--line-flash > th,
    tr.mef-row--line-flash > td {
      animation: mefLineFlash 1.6s ease-out;
    }
    @keyframes mefLineFlash {
      0% {
        box-shadow: inset 0 0 0 2px #58e1f3;
        background: rgba(88, 225, 243, 0.18);
      }
      100% {
        box-shadow: inset 0 0 0 0 rgba(88, 225, 243, 0);
        background: transparent;
      }
    }
    body.office-mode tr.mef-row--line-flash > th,
    body.office-mode tr.mef-row--line-flash > td {
      animation: mefLineFlashOffice 1.6s ease-out;
    }
    @keyframes mefLineFlashOffice {
      0% {
        box-shadow: inset 0 0 0 2px #0f9403;
        background: rgba(15, 148, 3, 0.14);
      }
      100% {
        box-shadow: inset 0 0 0 0 rgba(15, 148, 3, 0);
        background: transparent;
      }
    }
    @media (prefers-reduced-motion: reduce) {
      tr.mef-row--line-flash > th,
      tr.mef-row--line-flash > td,
      body.office-mode tr.mef-row--line-flash > th,
      body.office-mode tr.mef-row--line-flash > td {
        animation: none;
        box-shadow: inset 0 0 0 2px #58e1f3;
      }
    }
"""

SYNC_NEEDLE = """        var params = new URLSearchParams(window.location.search);
        var y = Number(params.get('year'));
        var m = Number(params.get('month'));
        var iso = String(params.get('iso') || '').trim();
"""

SYNC_REPL = """        var params = new URLSearchParams(window.location.search);
        var y = Number(params.get('year'));
        var m = Number(params.get('month'));
        var iso = String(params.get('iso') || '').trim();
        var line = String(params.get('line') || '').trim();
        mefPreferredLineId = line || null;
"""

INIT_NEEDLE = """        if (mefPreferredIso) scrollToIsoColumn(mefPreferredIso);
        else scrollToPreferredDayLeft();
        syncLabelScroll();
"""

INIT_REPL = """        if (mefPreferredIso) scrollToIsoColumn(mefPreferredIso);
        else scrollToPreferredDayLeft();
        syncLabelScroll();
        focusPreferredLine();
"""

FOCUS_FN = """
      var mefPreferredLineId = null;
      function focusPreferredLine() {
        if (!mefPreferredLineId || !root) return;
        var lineId = mefPreferredLineId;
        mefPreferredLineId = null;
        var iso = mefPreferredIso;
        var sel = iso
          ? 'input[data-action="money-input"][data-row-id="' +
            lineId +
            '"][data-iso="' +
            iso +
            '"]'
          : 'input[data-action="money-input"][data-row-id="' + lineId + '"]';
        var inp = root.querySelector(sel);
        if (!inp) {
          inp = root.querySelector(
            'input[data-action="money-input"][data-row-id="' + lineId + '"]'
          );
        }
        var tr = inp
          ? inp.closest('tr')
          : root.querySelector('tr[data-row-id="' + lineId + '"]');
        if (!tr && elLabels) {
          tr = elLabels.querySelector('tr[data-row-id="' + lineId + '"]');
        }
        if (tr) {
          try {
            tr.scrollIntoView({ behavior: 'smooth', block: 'center' });
          } catch (_e) {
            tr.scrollIntoView();
          }
          tr.classList.remove('mef-row--line-flash');
          void tr.offsetWidth;
          tr.classList.add('mef-row--line-flash');
          window.setTimeout(function () {
            tr.classList.remove('mef-row--line-flash');
          }, 1600);
        }
        if (inp && !inp.disabled && typeof inp.focus === 'function') {
          try {
            inp.focus({ preventScroll: true });
          } catch (_f) {
            inp.focus();
          }
        }
      }
"""


def inject_css(text: str) -> str:
    if CSS_MARKER in text:
        return text
    anchor = "</style>"
    idx = text.find(anchor)
    if idx < 0:
        raise ValueError("</style> not found")
    return text[:idx] + CSS_BLOCK + text[idx:]


def inject_focus_fn(text: str) -> str:
    if "function focusPreferredLine()" in text:
        return text
    anchor = "      function syncFromPage() {"
    if anchor not in text:
        raise ValueError("syncFromPage anchor missing")
    return text.replace(anchor, FOCUS_FN + "\n" + anchor, 1)


def patch_file(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = inject_css(text)
    text = inject_focus_fn(text)
    if "mefPreferredLineId = line || null" not in text:
        if SYNC_NEEDLE not in text:
            raise ValueError(f"syncFromPage params block missing: {path}")
        text = text.replace(SYNC_NEEDLE, SYNC_REPL, 1)
    if "focusPreferredLine();" not in text:
        if INIT_NEEDLE not in text:
            raise ValueError(f"initEditPage scroll block missing: {path}")
        text = text.replace(INIT_NEEDLE, INIT_REPL, 1)
    path.write_text(text, encoding="utf-8")
    print(f"patched {path.relative_to(ROOT)}")


def main() -> int:
    for t in TARGETS:
        if not t.is_file():
            print(f"missing: {t}")
            return 1
        patch_file(t)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
