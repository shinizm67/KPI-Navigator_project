#!/usr/bin/env python3
"""Annual ページ Graph タブ: Analyze 帯の巨大 min-height が消えたことを検証."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]


def main() -> int:
    problems: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for path in PAGES:
            page = browser.new_page(viewport={"width": 1400, "height": 900})
            page.goto(path.as_uri(), wait_until="load")
            page.wait_for_timeout(400)
            r = page.evaluate(
                """() => {
                  const root = document.getElementById('insight-overlay');
                  if (root) { root.hidden = false; root.removeAttribute('hidden'); }
                  ['insight-pane-summary','insight-pane-analyze','insight-pane-graph'].forEach(id => {
                    const el = document.getElementById(id); if (!el) return;
                    el.hidden = id !== 'insight-pane-graph';
                  });
                  const host = document.querySelector('.insight-overlay__content');
                  const pane = document.getElementById('insight-pane-graph');
                  const section = document.getElementById('insight-jump-graph-annual');
                  const g2 = document.getElementById('insight-graph-annual-graph2');
                  const link = document.getElementById('insight-graph-annual-analyze-link');
                  section.scrollIntoView();
                  return {
                    contentMin: getComputedStyle(host).minHeight,
                    paneBottomExtra: pane.getBoundingClientRect().bottom - section.getBoundingClientRect().bottom,
                    gapG2Link: link.getBoundingClientRect().top - g2.getBoundingClientRect().bottom,
                    annualH: section.getBoundingClientRect().height,
                    series2: (g2.querySelector('.insight-graph-annual-trend__series')||{}).childElementCount || 0,
                  };
                }"""
            )
            print(f"  {path.relative_to(ROOT)} {json.dumps(r)}")
            if r["contentMin"] not in ("0px", "auto") and "9431" in str(r["contentMin"]):
                problems.append(f"{path}: contentMin={r['contentMin']}")
            if float(r["paneBottomExtra"]) > 5:
                problems.append(f"{path}: paneBottomExtra={r['paneBottomExtra']}")
            if float(r["gapG2Link"]) > 160:
                problems.append(f"{path}: gapG2Link={r['gapG2Link']}")
            if int(r["series2"]) < 1:
                problems.append(f"{path}: graph2 empty")
            page.close()
        browser.close()

    print("\n=== RESULT ===")
    if problems:
        for pr in problems:
            print("NG:", pr)
        return 1
    print("OK: Annual Graph タブ下の Analyze 帯残骸スペースなし")
    return 0


if __name__ == "__main__":
    sys.exit(main())
