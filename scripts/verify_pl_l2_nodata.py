#!/usr/bin/env python3
"""検証: 過去データが皆無のとき、L2 トグル ON でも行高を上げない（可読性維持）。

- localStorage を空にして「過去も今年も実績なし」を再現
- コーナー +/- を ON にしても:
    * pl-guide-has-data は付かない
    * 明細行の高さは OFF 時とほぼ同じ（行高を上げない）
    * 目安セル（has-l2）は 0
    * 案内ツールチップに「データが貯まると表示」系の文言が出る
- 業界目安テンプレは出さない（＝勝手な数字を出さない）
"""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "app/profit/pl/index.html",
    ROOT / "en/app/profit/pl/index.html",
]
EXE = Path.home() / (
    "Library/Caches/ms-playwright/chromium-1228/"
    "chrome-mac-arm64/Google Chrome for Testing.app/"
    "Contents/MacOS/Google Chrome for Testing"
)


def row_h(page) -> float:
    return page.evaluate(
        """() => {
          const tr = document.querySelector('#pl-expense-detail-data-body tr[data-line-id]');
          return tr ? tr.getBoundingClientRect().height : 0;
        }"""
    )


def verify_page(page, url: str, lang: str) -> list[str]:
    errs: list[str] = []
    page.goto(url, wait_until="domcontentloaded")
    page.evaluate("() => localStorage.clear()")
    page.reload(wait_until="domcontentloaded")
    page.wait_for_timeout(900)
    page.evaluate(
        """() => {
          if (window.__plRefreshExpenseAmounts) __plRefreshExpenseAmounts();
          if (window.__plRefreshRatios) __plRefreshRatios();
          if (window.__plRefreshReferenceBudget) __plRefreshReferenceBudget();
        }"""
    )
    page.wait_for_timeout(300)
    off_h = row_h(page)

    page.click("#pl-guide-toggle")
    page.wait_for_timeout(400)
    state = page.evaluate(
        """() => ({
          on: document.body.classList.contains('pl-guide-on'),
          hasData: document.body.classList.contains('pl-guide-has-data'),
          has: document.querySelectorAll('#pl-expense-detail-data-body .pl-amt-cell--has-l2').length,
          tip: (document.querySelector('.pl-guide-tip-pop') || {}).textContent || '',
          tipVisible: !!(document.querySelector('.pl-guide-tip-pop.is-visible')),
        })"""
    )
    on_h = row_h(page)

    if not state["on"]:
        errs.append(f"{lang}: トグルが ON にならない")
    if state["hasData"]:
        errs.append(f"{lang}: データ皆無なのに pl-guide-has-data が付いている")
    if state["has"] != 0:
        errs.append(f"{lang}: データ皆無なのに目安セルがある {state['has']}")
    if abs(on_h - off_h) > 2:
        errs.append(f"{lang}: データ皆無で行高が変化した off={off_h} on={on_h}")
    # 案内文言（JA/EN いずれか特徴語）
    tip = state["tip"]
    if lang == "ja":
        if "貯まる" not in tip and "データ" not in tip:
            errs.append(f"{lang}: 案内文言が出ていない {tip!r}")
    else:
        if "past" not in tip.lower() and "data" not in tip.lower():
            errs.append(f"{lang}: no-data notice missing {tip!r}")
    if not state["tipVisible"]:
        errs.append(f"{lang}: 案内ツールチップが表示されていない")

    return errs


def main() -> int:
    if not EXE.exists():
        print(f"FAIL: chromium missing {EXE}", file=sys.stderr)
        return 2
    all_errs: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=str(EXE), headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        for path in PAGES:
            lang = "en" if "/en/" in str(path) else "ja"
            all_errs.extend(verify_page(page, path.resolve().as_uri(), lang))
        browser.close()
    if all_errs:
        print("FAIL")
        for e in all_errs:
            print(" -", e)
        return 1
    print("OK: PL L2 no-data（行高を上げず案内のみ・業界目安は出さない）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
