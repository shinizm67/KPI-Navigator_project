# -*- coding: utf-8 -*-
"""Auth failure Founder placeholder fix — static contract tests."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOUNDER = "s.matsushita@forge-laboratory.com"
DEFAULT_UID = "KPI-000000"

PROFILE_PAGES = [
    "setting/profile.html",
    "setting/profile_edit.html",
    "en/setting/profile.html",
    "en/setting/profile_edit.html",
    "zh-tw/setting/profile.html",
    "zh-tw/setting/profile_edit.html",
]
CHANGE_EMAIL_PAGES = [
    "setting/change_email.html",
    "setting/change_email_edit.html",
    "en/setting/change_email.html",
    "en/setting/change_email_edit.html",
    "zh-tw/setting/change_email.html",
    "zh-tw/setting/change_email_edit.html",
]
SESSION_JS = "js/kpi-profile-session-account.js"

failures: list[str] = []


def check(name: str, cond: bool) -> None:
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {name}")
    if not cond:
        failures.append(name)


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def main() -> int:
    js = read(SESSION_JS)

    check("session-account clears identity", "clearIdentity" in js)
    check("session-account redirects login", "redirectLogin" in js)
    check("session-account requires status 200", "r.status === 200" in js or "status !== 200" in js)
    check("session-account uses resolveLoginHref", "resolveLoginHref" in js)
    check("session-account no Founder fallback", FOUNDER not in js)
    check("session-account no KPI-000000 fallback", DEFAULT_UID not in js)
    check("session-account supports change-email mode", "change-email" in js)
    check("session-account paints only when authorized", "isAuthorized" in js and "applySessionAccount" in js)
    check(
        "unauthorized path clears then redirects",
        "clearIdentity(ids)" in js and "redirectLogin()" in js,
    )

    for rel in PROFILE_PAGES:
        html = read(rel)
        check(f"{rel}: no Founder email", FOUNDER not in html)
        check(f"{rel}: no KPI-000000 identity", DEFAULT_UID not in html)
        check(f"{rel}: includes session-account", "kpi-profile-session-account.js" in html)
        if "profile_edit" in rel:
            check(f"{rel}: edit mode", 'data-kpi-profile-account-mode="edit"' in html)
            check(f"{rel}: placeholder userId", 'id="profile-user-id"' in html and ">—" in html)
            check(f"{rel}: placeholder email", 'id="profile-email-display"' in html)
        else:
            check(f"{rel}: view mode", 'data-kpi-profile-account-mode="view"' in html)
            check(f"{rel}: placeholder userId", 'id="fixed-user-id"' in html and ">—" in html)
            check(f"{rel}: placeholder email", 'id="fixed-email"' in html)
            check(
                f"{rel}: no LS identity hydrate",
                "setText('fixed-user-id'" not in html and "setText('fixed-email'" not in html,
            )

    for rel in CHANGE_EMAIL_PAGES:
        html = read(rel)
        check(f"{rel}: no Founder email", FOUNDER not in html)
        check(f"{rel}: includes session-account", "kpi-profile-session-account.js" in html)
        check(
            f"{rel}: change-email mode",
            'data-kpi-profile-account-mode="change-email"' in html,
        )
        check(f"{rel}: no LS Founder fallback", "kpi-profile-last" not in html or FOUNDER not in html)
        # identity must not be filled from localStorage founder fallback anymore
        check(
            f"{rel}: no founder trim fallback",
            "|| 's.matsushita@forge-laboratory.com'" not in html,
        )

    # Regression: admin / password / profile sync contracts untouched by this fix
    admin = read("scripts/_test_admin_actions_foundation.py")
    check("admin actions test still present", "force-logout" in admin and "set-disabled" in admin)
    pw = read("api/v1/_password_reset.php")
    check("password reset admin_send intact", "admin_send" in pw)
    sync = read("scripts/_test_profile_server_sync.py")
    check("profile sync test intact", "profile ignores client userId" in sync)
    forgot = read("api/v1/auth/forgot-password.php")
    check("forgot-password endpoint present", "forgot" in forgot.lower() or "password" in forgot.lower())

    # Cross-locale identity contract parity (same script + modes)
    for lang_prefix, pages in [
        ("jp", ["setting/profile.html", "setting/profile_edit.html", "setting/change_email.html"]),
        ("en", ["en/setting/profile.html", "en/setting/profile_edit.html", "en/setting/change_email.html"]),
        ("zh-tw", ["zh-tw/setting/profile.html", "zh-tw/setting/profile_edit.html", "zh-tw/setting/change_email.html"]),
    ]:
        for rel in pages:
            html = read(rel)
            check(f"{lang_prefix} {rel}: session-account wired", "kpi-profile-session-account.js" in html)

    if failures:
        print(f"\nFAILED ({len(failures)}):")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("\nAll auth-failure placeholder checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
