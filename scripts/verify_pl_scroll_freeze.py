#!/usr/bin/env python3
"""検証: PL 縦スクロール固定ペイン + 横スクロール同期 + 行追加後の行高同期."""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "app/profit/pl/index.html"
EXE = Path.home() / (
    "Library/Caches/ms-playwright/chromium-1228/"
    "chrome-mac-arm64/Google Chrome for Testing.app/"
    "Contents/MacOS/Google Chrome for Testing"
)


def main() -> int:
    if not EXE.exists():
        print(f"FAIL: chromium missing {EXE}", file=sys.stderr)
        return 2
    errs: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=str(EXE), headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 720})
        page.goto(PAGE.resolve().as_uri(), wait_until="domcontentloaded")
        page.evaluate("() => localStorage.clear()")
        page.reload(wait_until="domcontentloaded")
        page.wait_for_timeout(700)

        struct = page.evaluate(
            """() => {
              const frozen = document.getElementById('pl-table-frozen');
              const scrollY = document.getElementById('pl-table-scroll-y');
              const biz = document.querySelector('#pl-table-frozen-body .pl-data-row--bizdays');
              const income = document.querySelector('#pl-table-scroll-y .pl-data-row--income');
              const frozenPane = document.getElementById('pl-data-pane-frozen');
              const bodyPane = document.getElementById('pl-data-pane');
              const expPane = document.getElementById('pl-data-pane-expense-detail');
              return {
                frozen: !!frozen,
                scrollY: !!scrollY,
                bizInFrozen: !!biz,
                incomeInScroll: !!income,
                frozenOverflowY: frozen ? getComputedStyle(frozen).overflowY : '',
                scrollOverflowY: scrollY ? getComputedStyle(scrollY).overflowY : '',
                canScrollY: scrollY ? scrollY.scrollHeight > scrollY.clientHeight + 2 : false,
                panes: !!(frozenPane && bodyPane && expPane),
              };
            }"""
        )
        for key in ("frozen", "scrollY", "bizInFrozen", "incomeInScroll", "panes"):
            if not struct[key]:
                errs.append(f"structure {key}=False")
        if struct["scrollOverflowY"] not in ("scroll", "auto", "overlay"):
            errs.append(f"scroll-y overflow-y={struct['scrollOverflowY']!r}")

        # Force short scroll area so vertical scroll is exercised
        page.evaluate(
            """() => {
              const el = document.getElementById('pl-table-scroll-y');
              if (el) el.style.maxHeight = '220px';
            }"""
        )
        page.wait_for_timeout(100)
        can = page.evaluate(
            """() => {
              const el = document.getElementById('pl-table-scroll-y');
              if (!el) return false;
              el.scrollTop = 80;
              return el.scrollTop >= 40 && el.scrollHeight > el.clientHeight;
            }"""
        )
        if not can:
            errs.append("vertical scroll did not move under constrained height")

        # Horizontal sync: frozen → expense detail
        sync = page.evaluate(
            """() => {
              const frozenPane = document.getElementById('pl-data-pane-frozen');
              const bodyPane = document.getElementById('pl-data-pane');
              const expPane = document.getElementById('pl-data-pane-expense-detail');
              if (!frozenPane || !bodyPane || !expPane) return { ok: false, reason: 'missing pane' };
              frozenPane.scrollLeft = 240;
              frozenPane.dispatchEvent(new Event('scroll'));
              return {
                ok:
                  Math.abs(bodyPane.scrollLeft - 240) < 2 &&
                  Math.abs(expPane.scrollLeft - 240) < 2,
                body: bodyPane.scrollLeft,
                exp: expPane.scrollLeft,
              };
            }"""
        )
        if not sync.get("ok"):
            errs.append(f"horizontal sync failed {sync}")

        # After occupancy/render, label/data row counts match
        page.evaluate(
            """() => {
              if (window.__plSetOccupancy) __plSetOccupancy('owned');
              if (window.__plSetOccupancy) __plSetOccupancy('rent');
            }"""
        )
        page.wait_for_timeout(400)
        pairs = page.evaluate(
            """() => {
              function count(sel) {
                const t = document.querySelector(sel);
                return t ? t.querySelectorAll('tr').length : -1;
              }
              const labelN = count('.pl-table--labels-expense-detail');
              const dataN = count('.pl-table--data-expense-detail');
              const labelRows = Array.from(
                document.querySelectorAll('.pl-table--labels-expense-detail tr')
              );
              const dataRows = Array.from(
                document.querySelectorAll('.pl-table--data-expense-detail tr')
              );
              const n = Math.min(labelRows.length, dataRows.length);
              let maxDiff = 0;
              for (let i = 0; i < n; i++) {
                maxDiff = Math.max(
                  maxDiff,
                  Math.abs(labelRows[i].offsetHeight - dataRows[i].offsetHeight)
                );
              }
              return { labelN, dataN, maxDiff };
            }"""
        )
        if pairs["labelN"] != pairs["dataN"] or pairs["labelN"] < 2:
            errs.append(f"expense label/data row mismatch {pairs}")
        if pairs["maxDiff"] > 2:
            errs.append(f"expense row height drift {pairs['maxDiff']}px")

        browser.close()

    if errs:
        print("FAIL")
        for e in errs:
            print(" -", e)
        return 1
    print("OK: PL scroll freeze")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
