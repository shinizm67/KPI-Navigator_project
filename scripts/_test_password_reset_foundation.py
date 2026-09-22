# -*- coding: utf-8 -*-
"""Forgot Password Foundation — static contract tests."""
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
        print(f"FAIL  {name}" + (f" — {detail}" if detail else ""))


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def main() -> None:
    mig = read("api/v1/schema_password_reset.add.sql")
    check("migration creates token table", "CREATE TABLE IF NOT EXISTS kpi_password_reset_tokens" in mig)
    check("migration token_hash column", "token_hash CHAR(64)" in mig)
    check("migration used_at nullable", "used_at DATETIME NULL" in mig)
    check("migration no plaintext token column", "token_plain" not in mig.lower() and "plaintext_token" not in mig.lower())
    check("migration additive only", "DROP TABLE" not in mig.split("Rollback")[0])

    helper = read("api/v1/_password_reset.php")
    check("sha256 token hash", "hash('sha256'" in helper)
    check("random_bytes token", "random_bytes(32)" in helper)
    check("ttl default 30", "passwordResetTtlMinutes" in helper)
    check("cooldown throttle", "kpi_v1_password_reset_throttle_allow" in helper)
    check("invalidate old tokens", "kpi_v1_password_reset_invalidate_user_tokens" in helper)
    check("PASSWORD_DEFAULT on reset", "PASSWORD_DEFAULT" in helper)
    check("no plaintext in DB insert comment path", "token_hash" in helper and "INSERT INTO kpi_password_reset_tokens" in helper)

    forgot = read("api/v1/auth/forgot-password.php")
    check("forgot always ok true", "['ok' => true]" in forgot or '["ok" => true]' in forgot)
    check("forgot no user_not_found", "user_not_found" not in forgot and "email_not_found" not in forgot)
    check("forgot uses request helper", "kpi_v1_password_reset_request" in forgot)

    reset = read("api/v1/auth/reset-password.php")
    check("reset consume helper", "kpi_v1_password_reset_consume" in reset)
    check("reset generic invalid error", "invalid_or_expired_token" in reset)
    check("reset password_too_short", "password_too_short" in reset)

    mail = read("api/v1/_mail.php")
    check("mail uses PHP mail()", "@mail(" in mail or "mail(" in mail)
    check("no PHPMailer dependency", "require PHPMailer" not in mail and "new PHPMailer" not in mail and "\\\\PHPMailer" not in mail)

    # Request path must not leak existence via distinct errors
    check(
        "request returns generic for missing user",
        "'ok' => true" in helper and "mailed" in helper,
    )

    cfg = read("api/v1/config.example.php")
    check("config ttl", "passwordResetTtlMinutes" in cfg)
    check("config cooldown", "passwordResetCooldownSeconds" in cfg)
    check("registration still disabled", "'registrationEnabled' => false" in cfg)

    boot = read("api/v1/_bootstrap.php")
    check("bootstrap reset defaults", "passwordResetTtlMinutes" in boot)

    client = read("js/kpi-auth-client.js")
    check("client forgotPassword", "forgotPassword:" in client or "forgotPassword =" in client or "function forgotPassword" in client)
    check("client resetPassword", "function resetPassword" in client)
    check("client generic message", "forgotPasswordGenericMessage" in client)
    check("client invalid token message", "invalid_or_expired_token" in client)
    check("client password_mismatch", "password_mismatch" in client)

    for rel, needle in [
        ("login/index.html", "forgot-password"),
        ("en/login/index.html", "forgot-password"),
        ("zh-tw/login/index.html", "forgot-password"),
        ("forgot-password/index.html", "kpi-forgot-password-page.js"),
        ("en/forgot-password/index.html", "kpi-forgot-password-page.js"),
        ("zh-tw/forgot-password/index.html", "kpi-forgot-password-page.js"),
        ("reset-password/index.html", "kpi-reset-password-page.js"),
        ("en/reset-password/index.html", "kpi-reset-password-page.js"),
        ("zh-tw/reset-password/index.html", "kpi-reset-password-page.js"),
    ]:
        t = read(rel)
        check(f"{rel} wiring", needle in t)

    reset_js = read("js/kpi-reset-password-page.js")
    check("reset JS success hides form", "form.hidden = true" in reset_js)
    check("reset JS shows success container", "okEl.hidden = false" in reset_js)
    check("reset JS auto redirect", "setTimeout" in reset_js and ("location.assign" in reset_js or "location.href" in reset_js))
    check("reset JS redirect delay 2500", "2500" in reset_js)
    check("reset JS uses resolveLoginHref", "resolveLoginHref" in reset_js)
    check("reset JS goLogin helper", "function goLogin" in reset_js)
    check(
        "reset JS invalid token does not hide form",
        "form.hidden = true" not in reset_js.split("if (!token)")[1].split("form.addEventListener")[0],
    )
    check(
        "reset JS invalid token does not redirect",
        "goLogin" not in reset_js.split("if (!token)")[1].split("form.addEventListener")[0]
        and "location.assign" not in reset_js.split("if (!token)")[1].split("form.addEventListener")[0],
    )
    check("reset JS uses success msg element", "reset-success-msg" in reset_js)
    check("reset JS reads login link href", "reset-login-link" in reset_js)
    check(
        "reset JS never wipes success via textContent on container",
        "okEl.textContent" not in reset_js,
    )

    check(
        "success message JP redirect wording",
        "パスワードを再設定しました。ログイン画面へ移動します。" in client,
    )
    check(
        "success message EN redirect wording",
        "Your password has been reset. Redirecting to login" in client,
    )
    check(
        "success message ZH-TW redirect wording",
        "密碼已重設。正在前往登入畫面" in client,
    )

    for rel, login_href, login_label in [
        ("reset-password/index.html", "/kpi-navigator/login/index.html", "ログイン画面へ"),
        ("en/reset-password/index.html", "/kpi-navigator/en/login/index.html", "Go to Login"),
        ("zh-tw/reset-password/index.html", "/kpi-navigator/zh-tw/login/index.html", "前往登入畫面"),
    ]:
        t = read(rel)
        form_m = re.search(r'<form[^>]*id="reset-form"[^>]*>(.*?)</form>', t, re.S)
        check(f"{rel} has reset-form", bool(form_m))
        if form_m:
            check(f"{rel} success not inside form", 'id="reset-success"' not in form_m.group(1))
            check(f"{rel} form kept on invalid path", 'id="reset-error"' in form_m.group(1))
        check(f"{rel} success outside form", 'id="reset-success"' in t)
        check(f"{rel} success msg element", 'id="reset-success-msg"' in t)
        check(f"{rel} login link in success", 'id="reset-login-link"' in t)
        check(f"{rel} login href locale", f'id="reset-login-link" href="{login_href}"' in t)
        check(f"{rel} login button label", login_label in t)
        check(f"{rel} login button class", 'id="reset-login-link"' in t and "btn-login" in t)
        check(f"{rel} versioned auth-client", "kpi-auth-client.js?v=20260922-c2l5a" in t)
        check(f"{rel} versioned reset-page js", "kpi-reset-password-page.js?v=20260918-2" in t)
        # static href must remain a real anchor (not JS-only)
        check(
            f"{rel} static login anchor",
            re.search(
                r'<a[^>]*id="reset-login-link"[^>]*href="' + re.escape(login_href) + r'"',
                t,
            )
            is not None,
        )
        # success block after form
        fi = t.find('id="reset-form"')
        si = t.find('id="reset-success"')
        check(f"{rel} success after form marker", fi >= 0 and si > fi)

    # client resolveLoginHref still locale-correct
    check("client resolveLoginHref JP path", "'/login/index.html'" in client or '"/login/index.html"' in client)
    check("client resolveLoginHref EN path", "'/en/login/index.html'" in client)
    check("client resolveLoginHref ZH path", "'/zh-tw/login/index.html'" in client)

    # Email subjects in helper
    check("JP email subject", "KPN パスワード再設定" in helper)
    check("EN email subject", "KPN Password Reset" in helper)
    check("ZH-TW email subject", "KPN 密碼重設" in helper)

    # Session: consume bumps per-user revoke epoch + clears current browser session
    check(
        "session revoke on consume uses epoch bump",
        "kpi_v1_session_revoke_bump" in helper and "kpi_v1_auth_clear_session" in helper,
    )

    # Login / register contracts untouched
    login = read("api/v1/auth/login.php")
    check("login still password_verify", "password_verify" in login)
    reg = read("api/v1/auth/register.php")
    check("register still gated", "registrationEnabled" in reg)
    check("register still PASSWORD_DEFAULT", "PASSWORD_DEFAULT" in reg)

    admin = read("api/v1/_admin.php")
    check("admin founder gate intact", "kpi_v1_auth_require_founder_superadmin" in admin)

    # Ensure APIs never echo password/token in response construction
    for rel in ["api/v1/auth/forgot-password.php", "api/v1/auth/reset-password.php"]:
        t = read(rel)
        check(f"{rel} no token in json_out", "token" not in t.split("kpi_v1_json_out")[-1] or "invalid_or_expired_token" in t)

    schema = read("api/v1/schema.sql")
    check("schema.sql includes reset table", "kpi_password_reset_tokens" in schema)

    print(f"\n{PASSED} passed, {FAILED} failed")
    raise SystemExit(1 if FAILED else 0)


if __name__ == "__main__":
    main()
