#!/usr/bin/env python3
"""Annual Sci-Fi/Office toggle INP v2: drop universal *, skip painting daily rows during switch."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "zh-tw/app/annual/index.html",
]

MARKER = "KPI-MODE-TOGGLE-INP-V2"

CSS_OLD = """    /* KPI-MODE-TOGGLE-INP */
    body.kpi-mode-switching,
    body.kpi-mode-switching * {
      transition: none !important;
      animation: none !important;
    }"""

CSS_NEW = """    /* KPI-MODE-TOGGLE-INP */
    /* KPI-MODE-TOGGLE-INP-V2: * 全称をやめ、日次一覧の描画だけ一時スキップ */
    body.kpi-mode-switching {
      transition: none !important;
      animation: none !important;
    }
    body.kpi-mode-switching #annual-daily-rows,
    body.kpi-mode-switching .annual-daily-focus-scroll,
    body.kpi-mode-switching .annual-daily-focus-global-scroll {
      content-visibility: hidden;
      contain: strict;
    }"""

CLICK_OLD = """        /* KPI-MODE-TOGGLE-INP: ラベル即時反映、office-mode 切替は rAF へ */
        var __modeToggleRaf = 0;
        btnModeToggle.addEventListener('click', function (e) {
          e.preventDefault();
          if (__modeToggleRaf) return;
          var willBeOffice = !bodyEl.classList.contains('office-mode');
          if (willBeOffice) {
            sessionStorage.setItem(STORAGE_KEY, '1');
          } else {
            sessionStorage.removeItem(STORAGE_KEY);
          }
          updateModeButton(willBeOffice);
          bodyEl.classList.add('kpi-mode-switching');
          __modeToggleRaf = requestAnimationFrame(function () {
            __modeToggleRaf = 0;
            bodyEl.classList.toggle('office-mode', willBeOffice);
            if (window.__ANNUAL_UI && typeof window.__ANNUAL_UI.refreshFocusBarAsset === 'function') {
              window.__ANNUAL_UI.refreshFocusBarAsset();
            }
            requestAnimationFrame(function () {
              bodyEl.classList.remove('kpi-mode-switching');
            });
          });
        });"""

CLICK_NEW = """        /* KPI-MODE-TOGGLE-INP: ラベル即時反映、office-mode 切替は rAF へ */
        /* KPI-MODE-TOGGLE-INP-V2: 先に日次一覧を描画スキップ → 切替 → 再表示 */
        var __modeToggleBusy = false;
        btnModeToggle.addEventListener('click', function (e) {
          e.preventDefault();
          if (__modeToggleBusy || !bodyEl) return;
          __modeToggleBusy = true;
          var willBeOffice = !bodyEl.classList.contains('office-mode');
          if (willBeOffice) {
            sessionStorage.setItem(STORAGE_KEY, '1');
          } else {
            sessionStorage.removeItem(STORAGE_KEY);
          }
          updateModeButton(willBeOffice);
          bodyEl.classList.add('kpi-mode-switching');
          requestAnimationFrame(function () {
            bodyEl.classList.toggle('office-mode', willBeOffice);
            if (window.__ANNUAL_UI && typeof window.__ANNUAL_UI.refreshFocusBarAsset === 'function') {
              window.__ANNUAL_UI.refreshFocusBarAsset();
            }
            requestAnimationFrame(function () {
              bodyEl.classList.remove('kpi-mode-switching');
              __modeToggleBusy = false;
            });
          });
        });"""


def patch_page(path: Path) -> None:
    rel = str(path.relative_to(ROOT))
    text = path.read_text(encoding="utf-8")
    if MARKER in text and "content-visibility: hidden" in text:
        print(f"skip (already) {rel}")
        return
    if CSS_OLD not in text:
        raise SystemExit(f"CSS block miss: {rel}")
    if CLICK_OLD not in text:
        raise SystemExit(f"click handler miss: {rel}")
    text = text.replace(CSS_OLD, CSS_NEW, 1)
    text = text.replace(CLICK_OLD, CLICK_NEW, 1)
    if MARKER not in text:
        raise SystemExit(f"{MARKER} missing after patch: {rel}")
    path.write_text(text, encoding="utf-8")
    print(f"wrote {rel}")


def main() -> int:
    for path in PAGES:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_page(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
