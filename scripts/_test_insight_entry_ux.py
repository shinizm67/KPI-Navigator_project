# -*- coding: utf-8 -*-
"""Insight Global Menu entry: Pro opens FW directly, Basic goes to Change Plan."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
JS = ROOT / "js" / "kpi-auth-client.js"
CHROME = SCRIPTS / "site_chrome.py"

FAILED = 0
PASSED = 0

INSIGHT_PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "zh-tw/app/monthly/index.html",
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "zh-tw/app/annual/index.html",
]
LINK_PAGES = [
    ROOT / "app/booking/index.html",
    ROOT / "en/app/booking/index.html",
    ROOT / "zh-tw/app/booking/index.html",
    ROOT / "setting/change_plan.html",
    ROOT / "en/setting/change_plan.html",
    ROOT / "zh-tw/setting/change_plan.html",
    ROOT / "setting/profile.html",
    ROOT / "en/setting/profile.html",
    ROOT / "zh-tw/setting/profile.html",
    ROOT / "app/profit/index.html",
    ROOT / "en/app/profit/index.html",
    ROOT / "zh-tw/app/profit/index.html",
]
DEEP_LINK_PAGES = [
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
    ROOT / "zh-tw/app/monthly/edit/index.html",
    ROOT / "app/profit/pl/index.html",
    ROOT / "en/app/profit/pl/index.html",
    ROOT / "zh-tw/app/profit/pl/index.html",
]
HUB_PAGES = [
    ROOT / "app/profit/index.html",
    ROOT / "en/app/profit/index.html",
    ROOT / "zh-tw/app/profit/index.html",
]

INSIGHT_BTN_RE = re.compile(
    r'<a\s[^>]*id="global-nav-index-btn"[^>]*>',
    re.I | re.S,
)


def assert_true(cond: bool, msg: str) -> None:
    global PASSED, FAILED
    if cond:
        PASSED += 1
        return
    FAILED += 1
    print("FAIL:", msg)


def insight_anchor(html: str) -> str:
    m = INSIGHT_BTN_RE.search(html)
    return m.group(0) if m else ""


def test_auth_client_gate() -> None:
    js = JS.read_text(encoding="utf-8")
    assert_true("function bindInsightMenuGate" in js, "dedicated Insight menu gate")
    assert_true("function openInsightFloatingWindow" in js, "direct FW open helper")
    assert_true("openInsight()" in js, "calls existing openInsight")
    assert_true("function resolveInsightOpenHref" in js, "non-overlay href resolver")
    assert_true("open=insight" in js, "deep-link open=insight")
    assert_true("app/profit/index.html" not in js.split("function bindInsightMenuGate")[-1][:2500], "gate does not target hub")
    assert_true("isBasicPlan()" in js.split("function bindInsightMenuGate", 1)[-1][:900], "Basic uses existing plan gate")
    assert_true("resolveChangePlanHref" in js.split("function bindInsightMenuGate", 1)[-1][:900], "Basic uses Change Plan")
    assert_true("bindInsightMenuGate(doc.getElementById" in js, "Insight btn uses menu gate not generic href gate")
    assert_true("bindProHrefGate(doc.getElementById ? doc.getElementById('header-booking-btn')" in js, "Booking still uses Pro href gate")
    assert_true("readInsightNavContext" in js, "keeps year/month/iso context")
    assert_true("searchParams.set('year'" in js, "year query preserved")
    assert_true("searchParams.set('month'" in js, "month query preserved")
    assert_true("searchParams.set('iso'" in js, "iso query preserved")
    chrome = CHROME.read_text(encoding="utf-8")
    assert_true("app/monthly/index.html?open=insight" in chrome, "chrome default Insight href is Monthly FW")
    assert_true(
        'href = profit_href or f"{base}app/profit/index.html"' not in chrome,
        "chrome default is no longer profit hub",
    )


def test_overlay_pages_direct_open() -> None:
    for path in INSIGHT_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        a = insight_anchor(html)
        assert_true("id=\"global-nav-index-btn\"" in a, f"{rel} Insight menu id")
        assert_true("data-href-basic=" in a and "change_plan.html" in a, f"{rel} Basic → Change Plan")
        assert_true("app/profit/index.html" not in a, f"{rel} Insight href bypasses hub")
        assert_true("open=insight" in a or 'href="#"' in a, f"{rel} Pro href is FW deep link or overlay")
        assert_true("__KPI_MONTHLY_OVERLAYS__.openInsight = open" in html, f"{rel} exports openInsight")
        assert_true("function bindInsightNavGate" in html or "bindInsightNavGate(document)" in html, f"{rel} gate bound")


def test_link_pages_go_to_monthly_fw() -> None:
    for path in LINK_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        a = insight_anchor(html)
        if not a:
            assert_true(False, f"{rel} missing Insight menu")
            continue
        assert_true("change_plan.html" in a, f"{rel} Basic Change Plan")
        assert_true("open=insight" in a, f"{rel} Pro → Monthly ?open=insight")
        assert_true("app/profit/index.html" not in a, f"{rel} not hub")
        assert_true("id=\"header-booking-btn\"" in html, f"{rel} Booking item kept")
        assert_true("id=\"global-nav-daily-btn\"" in html or "日次" in html or "Daily" in html or "每日" in html, f"{rel} Daily item kept")


def test_deep_links_already_fw() -> None:
    for path in DEEP_LINK_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        a = insight_anchor(html)
        assert_true("open=insight" in a, f"{rel} already deep-links FW")
        assert_true("change_plan.html" in a, f"{rel} Basic Change Plan")
        assert_true("app/profit/index.html" not in a, f"{rel} not hub")


def test_hub_kept_but_not_entry() -> None:
    for path in HUB_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        assert_true("profit-hub" in html or "利益サマリー" in html or "Profit" in html or "利潤" in html, f"{rel} hub page kept")
        a = insight_anchor(html)
        assert_true("open=insight" in a, f"{rel} Global Menu Insight leaves hub")
        assert_true('aria-current="page"' not in a, f"{rel} Insight is no longer hub-current")


def test_other_nav_untouched() -> None:
    html = (ROOT / "app/monthly/index.html").read_text(encoding="utf-8")
    assert_true('href="../../app/annual/index.html"' in html, "Annual nav kept")
    assert_true('href="../../app/monthly/index.html"' in html, "Monthly nav kept")
    assert_true('id="global-nav-daily-btn"' in html, "Daily overlay opener kept")
    assert_true('id="header-booking-btn"' in html, "Booking kept")
    assert_true("data-href-pro=\"../../app/booking/index.html\"" in html, "Booking Pro target kept")


def test_no_new_billing_ui() -> None:
    js = JS.read_text(encoding="utf-8")
    assert_true("Stripe" not in js.split("function bindInsightMenuGate")[-1][:2000], "no Stripe in Insight gate")
    assert_true("store.php" not in js, "no store.php in auth client gate")


def main() -> int:
    test_auth_client_gate()
    test_overlay_pages_direct_open()
    test_link_pages_go_to_monthly_fw()
    test_deep_links_already_fw()
    test_hub_kept_but_not_entry()
    test_other_nav_untouched()
    test_no_new_billing_ui()
    print(f"passed={PASSED} failed={FAILED}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
