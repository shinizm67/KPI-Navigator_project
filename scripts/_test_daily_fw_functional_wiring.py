# -*- coding: utf-8 -*-
"""Daily Floating Window (#daily-overlay) functional wiring contract."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAILED = 0
PASSED = 0

HOST_PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "zh-tw/app/monthly/index.html",
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "zh-tw/app/annual/index.html",
]
CLIENT = ROOT / "scripts/daily_overlay_kpi_client.py"


def check(cond: bool, msg: str) -> None:
    global PASSED, FAILED
    if cond:
        PASSED += 1
        return
    FAILED += 1
    print("FAIL:", msg)


def main() -> int:
    client = CLIENT.read_text(encoding="utf-8")

    # --- source client formulas ---
    check("window.renderDailyOverlayKpis" in client, "client exposes renderDailyOverlayKpis")
    check("__computeTwMetricsForIso" in client, "KPIs from TW metrics")
    check("m.isBusinessToday ? fmtOverlayMoney(m.dailySales)" in client, "closed day sales → dash")
    check("hasDailyPlan ? fmtOverlayMoney(m.dailyTarget)" in client, "target gated on biz+plan")
    check("hasDailyPlan ? fmtOverlayDiff(m.dailySales, m.dailyTarget)" in client, "diff gated")
    check("hasDailyPlan ? fmtOverlayAchPct(m.dailySales, m.dailyTarget)" in client, "ach gated")
    check("m.hasPlan ? fmtOverlayCount(m.monthRemainingBD) : dash" in client, "month BD gated by hasPlan")
    check("m.hasPlan ? fmtOverlayCount(m.yearRemainingBD) : dash" in client, "year BD gated by hasPlan")
    check("setOverlayGraph(dailyGraph, m.dailySales, m.dailyTarget, hasDailyPlan)" in client, "daily graph wired")
    check("Math.round((actual / target) * 100) + '%'" in client, "ach rounding contract")
    # no meal/customer/group in Daily FW metrics client
    check("dailyMeal" not in client and "lunch" not in client.lower(), "no restaurant meal invent")
    check("businessType" not in client and "getAnalysisMetrics" not in client, "no BT invent in Daily FW KPI")

    # numerical helpers (151960 / 40059)
    sales, target = 151960, 40059
    diff = sales - target
    ach = round((sales / target) * 100)
    check(diff == 111901, "diff formula 151960-40059=111901")
    check(ach == 379, "ach round 379%")

    for path in HOST_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        check('id="daily-overlay"' in html, f"{rel} has daily-overlay root")
        check('id="global-nav-daily-btn"' in html, f"{rel} Daily nav entry")
        check("window.renderDailyOverlayKpis" in html, f"{rel} KPI renderer")
        check("__computeTwMetricsForIso" in html, f"{rel} TW metrics available")
        check("function open()" in html and "fill(selectedIso)" in html, f"{rel} open→fill")
        check("bindDailyOverlayDateHoldRepeat" in html or "daily-overlay-prev-day" in html, f"{rel} prev/next")
        check('id="daily-overlay-today"' in html, f"{rel} today button")
        check('id="daily-overlay-close"' in html, f"{rel} close")
        check("selectedIso = shiftIso" in html, f"{rel} date nav updates selectedIso")
        check("renderDailyOverlayKpis(iso)" in html, f"{rel} fill calls renderer with iso")
        check("m.hasPlan ? fmtOverlayCount(m.monthRemainingBD) : dash" in html, f"{rel} month BD hasPlan gate")
        check("m.hasPlan ? fmtOverlayCount(m.yearRemainingBD) : dash" in html, f"{rel} year BD hasPlan gate")
        check("m.isBusinessToday ? fmtOverlayMoney(m.dailySales) : dash" in html, f"{rel} closed→dash")
        # Monthly hosts: ?open=daily deep link + openDaily export
        # Annual hosts: #global-nav-daily-btn only (no deep-link contract)
        if "/monthly/" in rel:
            check("open === 'daily'" in html, f"{rel} ?open=daily deep link")
            check(
                "__KPI_MONTHLY_OVERLAYS__" in html and "openDaily" in html,
                f"{rel} openDaily export",
            )
        else:
            check(
                "btnDaily.addEventListener('click'" in html
                or 'btnDaily.addEventListener("click"' in html,
                f"{rel} Daily nav click open",
            )
            check("open === 'daily'" not in html, f"{rel} annual has no ?open=daily invent")
        # static shell placeholders exist but must be overwritten by renderer
        check("daily-overlay__daily-value-box" in html, f"{rel} daily value boxes")
        check("daily-overlay__monthly-value-box" in html, f"{rel} monthly value boxes")
        check("daily-overlay__annual-value-box" in html, f"{rel} annual value boxes")
        # no Basic hard-block on Daily entry (sales surface)
        open_idx = html.find("btnDaily.addEventListener('click'")
        if open_idx < 0:
            open_idx = html.find('btnDaily.addEventListener("click"')
        snippet = html[open_idx : open_idx + 250] if open_idx >= 0 else ""
        check("isBasicTier" not in snippet and "change_plan" not in snippet.lower(), f"{rel} Daily open not Pro-gated")

    # session / auth scripts still on hosts (monthly + annual JP)
    for path in (HOST_PAGES[0], HOST_PAGES[3]):
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        check("kpi-auth-client.js" in html, f"{rel} auth client")

    print(f"passed={PASSED} failed={FAILED}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
