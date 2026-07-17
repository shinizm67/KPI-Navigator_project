#!/usr/bin/env python3
"""Graph Annual 復旧検証: Annual ページでグラフ DOM / 系列が描画されること."""

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


def verify_page(page, url: str) -> list[str]:
    problems: list[str] = []
    page.goto(url, wait_until="load")
    page.wait_for_timeout(500)

    result = page.evaluate(
        """() => {
          const root = document.getElementById('insight-overlay');
          if (root) {
            root.hidden = false;
            root.removeAttribute('hidden');
            root.classList.add('is-open');
          }
          ['insight-pane-summary','insight-pane-analyze','insight-pane-graph'].forEach(id => {
            const el = document.getElementById(id);
            if (!el) return;
            if (id === 'insight-pane-graph') {
              el.hidden = false;
              el.removeAttribute('hidden');
            } else {
              el.hidden = true;
              el.setAttribute('hidden', '');
            }
          });
          const section = document.getElementById('insight-jump-graph-annual');
          if (section) section.scrollIntoView();
          const g1 = document.getElementById('insight-graph-annual-graph1');
          const g2 = document.getElementById('insight-graph-annual-graph2');
          const bar = document.getElementById('insight-graph-annual-cumulative-target-actual');
          const series1 = g1 && g1.querySelector('.insight-graph-annual-trend__series');
          const series2 = g2 && g2.querySelector('.insight-graph-annual-trend__series');
          const placeholder = section && /準備中/.test(section.getAttribute('aria-label')||'')
            || !!(section && section.querySelector('[aria-label*=\"準備中\"]'));
          function box(el) {
            if (!el) return null;
            const r = el.getBoundingClientRect();
            return { w: r.width, h: r.height, visible: r.width > 0 && r.height > 0 };
          }
          return {
            placeholder,
            sectionH: box(section),
            g1: box(g1),
            g2: box(g2),
            bar: box(bar),
            series1: series1 ? series1.childElementCount : null,
            series2: series2 ? series2.childElementCount : null,
            textSample: section ? (section.innerText || '').slice(0, 180) : null,
          };
        }"""
    )

    if result.get("placeholder"):
        problems.append(f"{url}: placeholder remains")
    if not result.get("g1") or not result["g1"]["visible"]:
        problems.append(f"{url}: graph1 not visible {result.get('g1')}")
    if not result.get("g2") or not result["g2"]["visible"]:
        problems.append(f"{url}: graph2 not visible {result.get('g2')}")
    if not result.get("bar") or not result["bar"]["visible"]:
        problems.append(f"{url}: cumulative bar not visible {result.get('bar')}")
    if not result.get("series1") or result["series1"] < 1:
        problems.append(f"{url}: graph1 series empty {result.get('series1')}")
    if not result.get("series2") or result["series2"] < 1:
        problems.append(f"{url}: graph2 series empty {result.get('series2')}")

    print(f"  {url.split('/kpi-navigator/')[-1]}")
    print(f"    {json.dumps(result, ensure_ascii=False)}")
    return problems


def main() -> int:
    all_problems: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for page_path in PAGES:
            context = browser.new_context()
            page = context.new_page()
            try:
                all_problems += verify_page(page, page_path.as_uri())
            except Exception as e:  # noqa: BLE001
                all_problems.append(f"{page_path}: EXCEPTION {e}")
            finally:
                context.close()
        browser.close()

    print("\n=== RESULT ===")
    if all_problems:
        for pr in all_problems:
            print("NG:", pr)
        return 1
    print("OK: Annual ページ Graph → Annual が描画される（2ファイル）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
