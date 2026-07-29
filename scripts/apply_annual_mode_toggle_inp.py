#!/usr/bin/env python3
"""Annual Sci-Fi/Office mode toggle INP: instant label, defer class toggle + DOM moves."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "zh-tw/app/annual/index.html",
]

MARKER = "KPI-MODE-TOGGLE-INP"
JS_MARKER = "/* KPI-MODE-TOGGLE-INP: ラベル即時反映"

CSS_ANCHOR = "    /* KPI-ANNUAL-CLS-FIX */"
CSS_BLOCK = """
    /* KPI-MODE-TOGGLE-INP */
    body.kpi-mode-switching,
    body.kpi-mode-switching * {
      transition: none !important;
      animation: none !important;
    }"""

UPDATE_FN_OLD = """      function updateModeButton() {
        if (!btnModeText || !btnModeToggle) return;
        var isOffice = bodyEl && bodyEl.classList.contains('office-mode');"""

UPDATE_FN_NEW = """      function updateModeButton(isOfficeOpt) {
        if (!btnModeText || !btnModeToggle) return;
        var isOffice =
          typeof isOfficeOpt === 'boolean'
            ? isOfficeOpt
            : !!(bodyEl && bodyEl.classList.contains('office-mode'));"""

CLICK_OLD = """        btnModeToggle.addEventListener('click', function (e) {
          e.preventDefault();
          bodyEl.classList.toggle('office-mode');
          if (bodyEl.classList.contains('office-mode')) {
            sessionStorage.setItem(STORAGE_KEY, '1');
          } else {
            sessionStorage.removeItem(STORAGE_KEY);
          }
          updateModeButton();
          if (window.__ANNUAL_UI && typeof window.__ANNUAL_UI.refreshFocusBarAsset === 'function') {
            window.__ANNUAL_UI.refreshFocusBarAsset();
          }
        });"""

CLICK_NEW = """        /* KPI-MODE-TOGGLE-INP: ラベル即時反映、office-mode 切替は rAF へ */
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

OBSERVER_OLD = """      new MutationObserver(placeToggleForMode).observe(document.body, {
        attributes: true,
        attributeFilter: ['class'],
      });"""

OBSERVER_NEW = """      /* KPI-MODE-TOGGLE-INP: office-mode 変化時の DOM 移動は rAF へ */
      var __placeToggleRaf = 0;
      function schedulePlaceToggleForMode() {
        if (__placeToggleRaf) return;
        __placeToggleRaf = requestAnimationFrame(function () {
          __placeToggleRaf = 0;
          placeToggleForMode();
        });
      }
      new MutationObserver(function (mutations) {
        for (var mi = 0; mi < mutations.length; mi++) {
          var oldVal = mutations[mi].oldValue || '';
          var hadOffice = /\\boffice-mode\\b/.test(oldVal);
          var hasOffice = document.body.classList.contains('office-mode');
          if (hadOffice !== hasOffice) {
            schedulePlaceToggleForMode();
            return;
          }
        }
      }).observe(document.body, {
        attributes: true,
        attributeFilter: ['class'],
        attributeOldValue: true,
      });"""


def patch_css(text: str, rel: str) -> str:
    if MARKER in text and "body.kpi-mode-switching" in text:
        return text
    if CSS_ANCHOR not in text:
        raise SystemExit(f"CLS anchor miss: {rel}")
    if CSS_BLOCK.strip() in text:
        return text
    return text.replace(CSS_ANCHOR, CSS_ANCHOR + CSS_BLOCK, 1)


def patch_js(text: str, rel: str) -> str:
    if JS_MARKER in text:
        print(f"skip JS (already) {rel}")
        return text
    if UPDATE_FN_OLD not in text:
        raise SystemExit(f"updateModeButton miss: {rel}")
    if CLICK_OLD not in text:
        raise SystemExit(f"mode click handler miss: {rel}")
    if OBSERVER_OLD not in text:
        raise SystemExit(f"placeToggle observer miss: {rel}")
    text = text.replace(UPDATE_FN_OLD, UPDATE_FN_NEW, 1)
    text = text.replace(CLICK_OLD, CLICK_NEW, 1)
    text = text.replace(OBSERVER_OLD, OBSERVER_NEW, 1)
    if JS_MARKER not in text:
        raise SystemExit(f"{JS_MARKER} missing after patch: {rel}")
    return text


def patch_page(path: Path) -> None:
    rel = str(path.relative_to(ROOT))
    text = path.read_text(encoding="utf-8")
    before = text
    text = patch_css(text, rel)
    text = patch_js(text, rel)
    if text != before:
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
