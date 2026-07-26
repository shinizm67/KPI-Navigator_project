#!/usr/bin/env python3
"""検証: Analyze Annual Target Revision 4行 KPI（v1）."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]
EXE = Path.home() / (
    "Library/Caches/ms-playwright/chromium-1228/"
    "chrome-mac-arm64/Google Chrome for Testing.app/"
    "Contents/MacOS/Google Chrome for Testing"
)


def seed_store() -> dict:
    # Jul 2026 → Term 3. Sales intentionally below plan pace → negative adj / Watch or Revise.
    return {
        "meta": {
            "schemaVersion": 4,
            "operatingYear": 2026,
            "legacyMigrated": True,
            "selectedDate": "2026-07-14",
        },
        "timeline": {
            "dailySales": {
                "2026-01-15": 20000,
                "2026-07-01": 10000,
                "2026-07-10": 10000,
            },
            "businessDays": {},
        },
        "years": {
            "2026": {
                "year": 2026,
                "status": "open",
                "plan": {"targetSales": 600000, "monthlyHlWeights": [100] * 12},
            }
        },
    }


def verify_page(page, url: str) -> list[str]:
    problems: list[str] = []
    page.add_init_script(
        """
        window.localStorage.setItem('kpiNavigator.kpiYearStore', %s);
        """
        % (json.dumps(json.dumps(seed_store())),)
    )
    page.goto(url, wait_until="load")
    page.wait_for_function(
        "() => typeof window.renderInsightTwDiffs === 'function' && "
        "typeof window.__computeTwMetricsForIso === 'function'",
        timeout=20000,
    )
    result = page.evaluate(
        """() => {
          const iso = '2026-07-14';
          const paneSummary = document.getElementById('insight-pane-summary');
          const paneAnalyze = document.getElementById('insight-pane-analyze');
          const paneGraph = document.getElementById('insight-pane-graph');
          if (paneSummary) paneSummary.hidden = true;
          if (paneAnalyze) paneAnalyze.hidden = false;
          if (paneGraph) paneGraph.hidden = true;
          window.renderInsightTwDiffs(iso);
          const m = window.__computeTwMetricsForIso(iso);
          const block = document.querySelector(
            '#insight-jump-analyze-annual .insight-annual-target-revision-kpi'
          );
          const vals = block
            ? Array.from(
                block.querySelectorAll('.insight-annual-target-revision-kpi__value')
              ).map((el) => el.textContent.trim())
            : [];
          const ja = String(document.documentElement.getAttribute('lang') || '')
            .toLowerCase()
            .indexOf('ja') === 0;
          let expected = null;
          if (m && m.hasPlan && Number(m.ytdT) > 0) {
            let adj = Math.round(((Number(m.ytdA) - Number(m.ytdT)) / Number(m.ytdT)) * 100);
            if (adj > 20) adj = 20;
            if (adj < -20) adj = -20;
            const abs = Math.abs(adj);
            const status = abs < 3
              ? (ja ? '順調' : 'On Track')
              : abs <= 10
                ? (ja ? '要注意' : 'Watch')
                : (ja ? '要改訂' : 'Revise');
            const adjText = (adj > 0 ? '+' : '') + adj + '%';
            let targetText = '—';
            if (m.annualTarget != null && Number.isFinite(Number(m.annualTarget))) {
              const n = Math.round(Number(m.annualTarget) * (1 + adj / 100));
              targetText =
                typeof window.__twFmtMoney === 'function'
                  ? window.__twFmtMoney(n)
                  : String(n);
            }
            expected = {
              term: ja ? '第3四半期' : 'Term 3',
              status,
              adjText,
              targetText,
              ytdA: m.ytdA,
              ytdT: m.ytdT,
              annualTarget: m.annualTarget,
            };
          }
          return { vals, expected, hasPlan: !!(m && m.hasPlan) };
        }"""
    )
    vals = result.get("vals") or []
    expected = result.get("expected")
    rel = url.split("/kpi-navigator/")[-1]
    print(f"  {rel} vals={vals} expected={expected}")

    if len(vals) < 4:
        problems.append(f"{url}: missing ATR KPI rows {vals}")
        return problems
    if vals in (
        ["Term 2", "Watch", "-5%", "$234,567"],
        ["第2四半期", "要注意", "-5%", "$234,567"],
    ):
        problems.append(f"{url}: still mock values")
    want_term = (expected or {}).get("term") or "Term 3"
    if vals[0] != want_term:
        problems.append(f"{url}: term want {want_term} got {vals[0]}")
    if not expected:
        problems.append(f"{url}: could not compute expected (no plan/ytdT)")
        return problems
    if vals[1] != expected["status"]:
        problems.append(f"{url}: status want {expected['status']} got {vals[1]}")
    if vals[2] != expected["adjText"]:
        problems.append(f"{url}: adj want {expected['adjText']} got {vals[2]}")
    # money formatter may be fmtInsightMoney path — accept ¥/$ with same digits
    if expected["targetText"] not in ("—",) and vals[3] in ("$234,567", "—"):
        problems.append(f"{url}: target still mock/empty {vals[3]}")
    if expected["targetText"] != "—" and vals[3] == "$234,567":
        problems.append(f"{url}: target still mock")
    # Prefer exact match when formatter available
    if expected["targetText"] != "—" and vals[3] != expected["targetText"]:
        # tolerate currency symbol difference if digits match
        dig_e = "".join(ch for ch in expected["targetText"] if ch.isdigit() or ch == ",")
        dig_v = "".join(ch for ch in vals[3] if ch.isdigit() or ch == ",")
        if dig_e != dig_v:
            problems.append(
                f"{url}: target want {expected['targetText']} got {vals[3]}"
            )
    return problems


def main() -> int:
    os.environ.pop("PLAYWRIGHT_BROWSERS_PATH", None)
    problems: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=str(EXE), headless=True)
        for path in PAGES:
            page = browser.new_page()
            problems.extend(verify_page(page, path.as_uri()))
            page.close()
        browser.close()
    if problems:
        print("FAIL:")
        for pr in problems:
            print(" ", pr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
