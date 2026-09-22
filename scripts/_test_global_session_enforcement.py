# -*- coding: utf-8 -*-
"""Global session enforcement — shared auth gate contract tests."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
failures: list[str] = []


def check(name: str, cond: bool) -> None:
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")
    if not cond:
        failures.append(name)


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


APP_PAGES = [
    "app/annual/index.html",
    "app/monthly/index.html",
    "app/monthly/edit/index.html",
    "app/profit/index.html",
    "app/profit/pl/index.html",
    "app/booking/index.html",
    "en/app/annual/index.html",
    "en/app/monthly/index.html",
    "en/app/monthly/edit/index.html",
    "en/app/profit/index.html",
    "en/app/profit/pl/index.html",
    "en/app/booking/index.html",
    "zh-tw/app/annual/index.html",
    "zh-tw/app/monthly/index.html",
    "zh-tw/app/monthly/edit/index.html",
    "zh-tw/app/profit/index.html",
    "zh-tw/app/profit/pl/index.html",
    "zh-tw/app/booking/index.html",
]

SETTING_PAGES = [
    "setting/profile.html",
    "setting/profile_edit.html",
    "setting/change_email.html",
    "setting/change_password.html",
    "setting/change_plan.html",
    "setting/session_management.html",
    "en/setting/profile.html",
    "en/setting/change_password.html",
    "en/setting/session_management.html",
    "zh-tw/setting/profile.html",
    "zh-tw/setting/change_password.html",
    "zh-tw/setting/session_management.html",
]

PUBLIC_PAGES = [
    "login/index.html",
    "en/login/index.html",
    "zh-tw/login/index.html",
    "forgot-password/index.html",
    "reset-password/index.html",
]


def main() -> int:
    js = read("js/kpi-auth-client.js")
    gw = read("js/kpi-data-gateway.js")
    admin = read("api/v1/_admin.php")

    check("enforceSession exported", "enforceSession:" in js or "enforceSession =" in js)
    check("handleUnauthorizedSession exported", "handleUnauthorizedSession" in js)
    check("isPublicAuthPage", "isPublicAuthPage" in js)
    check("isSessionUnauthorized", "isSessionUnauthorized" in js)
    check("boot calls enforceSession", "enforceSession()" in js)
    check("boot no longer silent-only sync", "enforceSession().catch" in js)
    check("detects 401", "status === 401" in js)
    check("detects 403", "status === 403" in js)
    check("detects account_disabled", "account_disabled" in js)
    check("redirect uses resolveLoginHref", "resolveLoginHref" in js and "location.replace" in js)
    check("clears display tier only", "clearSessionDisplayState" in js and "TIER_KEY" in js)
    start = js.find("function handleUnauthorizedSession")
    end = js.find("function enforceSession", start)
    body = js[start:end] if start >= 0 and end > start else ""
    check("unauthorized handler skips business wipe", "clearUserScopedLocalData" not in body)
    check("syncPlanFromServer triggers unauthorized handle", "handleUnauthorizedSession(r)" in js)
    check("guardProPage unauthorized path", "reason: 'unauthorized'" in js)
    check("public pages skip login/register/forgot/reset", "/login/" in js and "/forgot-password/" in js and "/reset-password/" in js and "/register/" in js)

    check("gateway redirects on store 401/403", "handleUnauthorizedSession" in gw and "res.status === 401" in gw)

    check("admin page unauth redirects login", "Location: /kpi-navigator/login/index.html" in admin)

    for rel in APP_PAGES + SETTING_PAGES:
        html = read(rel)
        check(f"{rel}: auth-client present", "kpi-auth-client.js" in html)
        check(f"{rel}: auth-client cache-bust", "kpi-auth-client.js?v=20260923-c2l5b" in html)

    for rel in PUBLIC_PAGES:
        html = read(rel)
        check(f"{rel}: auth-client cache-bust", "kpi-auth-client.js?v=20260923-c2l5b" in html)

    # Profile identity contract still wired
    check(
        "profile session-account retained",
        "kpi-profile-session-account.js" in read("setting/profile.html"),
    )

    # Admin actions / unit6 / password reset regression surface
    check("admin actions test file present", (ROOT / "scripts/_test_admin_actions_foundation.py").is_file())
    check("password reset test file present", (ROOT / "scripts/_test_password_reset_foundation.py").is_file())

    if failures:
        print(f"\nFAILED ({len(failures)}):")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("\nAll global session enforcement checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
