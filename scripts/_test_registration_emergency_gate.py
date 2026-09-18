# -*- coding: utf-8 -*-
"""Public Registration Emergency Gate — static + control-flow checks."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAILED = 0
PASSED = 0


def check(name: str, cond: bool, detail: str = "") -> None:
    global FAILED, PASSED
    if cond:
        PASSED += 1
        print(f"PASS  {name}")
    else:
        FAILED += 1
        extra = f" — {detail}" if detail else ""
        print(f"FAIL  {name}{extra}")


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def main() -> None:
    reg = read("api/v1/auth/register.php")
    boot = read("api/v1/_bootstrap.php")
    example = read("api/v1/config.example.php")
    admin = read("api/v1/auth/admin-create-user.php")
    auth_js = read("js/kpi-auth-client.js")
    login_php = read("api/v1/auth/login.php")

    # 1) Config default false
    check(
        "config.example registrationEnabled=false",
        re.search(r"'registrationEnabled'\s*=>\s*false", example) is not None,
    )
    check(
        "bootstrap default registrationEnabled=false",
        re.search(r"'registrationEnabled'\s*=>\s*false", boot) is not None,
    )

    # 2) Server gate before create/session
    gate_pos = reg.find("registration_disabled")
    write_pos = reg.find("kpi_v1_auth_write_user")
    session_pos = reg.find("kpi_v1_auth_set_session_user")
    check("register.php emits registration_disabled", "registration_disabled" in reg)
    check("register.php returns 403 on gate", "kpi_v1_json_out(403" in reg and "registration_disabled" in reg)
    check("gate before user write", gate_pos >= 0 and write_pos > gate_pos)
    check("gate before session", gate_pos >= 0 and session_pos > gate_pos)
    check(
        "gate uses empty(registrationEnabled)",
        "empty($cfg['registrationEnabled'])" in reg or 'empty($cfg["registrationEnabled"])' in reg,
    )

    # 3) admin-create-user isolated
    check("admin-create-user has no registrationEnabled gate", "registrationEnabled" not in admin)
    check("admin-create-user still writes user", "kpi_v1_auth_write_user" in admin)
    check("admin-create-user does not set session", "kpi_v1_auth_set_session_user" not in admin)

    # 4) login untouched by registration gate
    check("login.php has no registrationEnabled", "registrationEnabled" not in login_php)

    # 5) Frontend error UX (before generic 403)
    pos_rd = auth_js.find("registration_disabled")
    pos_403 = auth_js.find("entitlement_required")
    check(
        "errorMessage handles registration_disabled before generic 403",
        pos_rd >= 0 and pos_403 > pos_rd,
    )
    check("JP registration_disabled message", "現在、新規登録の受付を一時停止しています。" in auth_js)
    check("EN registration_disabled message", "New registrations are temporarily unavailable." in auth_js)
    check("ZH-TW registration_disabled message", "目前暫停接受新註冊。" in auth_js)

    # 6) Plan CTAs no longer point at public register
    for rel, bad in [
        ("plan/index.html", "registration_si-fi_jp"),
        ("en/plan/index.html", "registration_si-fi_en"),
        ("zh-tw/plan/index.html", "registration_si-fi_zh-tw"),
    ]:
        t = read(rel)
        row = re.search(r'class="row-buttons".*?</tr>', t, re.S)
        check(f"{rel} has row-buttons", row is not None)
        if row:
            chunk = row.group(0)
            check(f"{rel} CTA not linking to register", bad not in chunk)
            check(f"{rel} CTA uses mailto/contact", "mailto:support@forge-laboratory.com" in chunk)

    # 7) Registration pages show unavailable + hide form
    pages = {
        "register/registration_si-fi_jp/registration_si-fi_jp.html": "現在、新規登録の受付を一時停止しています。",
        "en/register/registration_si-fi_en.html": "New registrations are temporarily unavailable.",
        "zh-tw/register/registration_si-fi_zh-tw.html": "目前暫停接受新註冊。",
    }
    for rel, msg in pages.items():
        t = read(rel)
        check(f"{rel} has disabled notice", "registration-disabled-notice" in t)
        check(f"{rel} has locale message", msg in t)
        check(f"{rel} form hidden", 'hidden aria-hidden="true"' in t)
        check(f"{rel} keeps login link", "login" in t.lower())

    # 8) Scripts gate submit
    for rel in ["register/script.js", "en/register/script.js", "zh-tw/register/script.js"]:
        t = read(rel)
        check(f"{rel} respects disabled notice", "registration-disabled-notice" in t)

    # 9) zh-tw uses zh for errorMessage
    zh_script = read("zh-tw/register/script.js")
    check("zh-tw script errorMessage uses zh", "errorMessage('zh'," in zh_script)

    print(f"\n{PASSED} passed, {FAILED} failed")
    raise SystemExit(1 if FAILED else 0)


if __name__ == "__main__":
    main()
