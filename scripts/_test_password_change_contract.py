# -*- coding: utf-8 -*-
"""BR-LAUNCH-09 Phase 1 Password Change contract — static checks (endpoint, pages, no plaintext storage)."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAILED = 0
PASSED = 0

LANGS = {
    "ja": ("setting", "../js/kpi-change-password-page.js", "現在のパスワード :"),
    "en": ("en/setting", "../../js/kpi-change-password-page.js", "Current Password :"),
    "zh": ("zh-tw/setting", "../../js/kpi-change-password-page.js", "目前密碼 :"),
}


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


def strip_js_comments(src: str) -> str:
    return re.sub(r"/\*.*?\*/", "", src, flags=re.S)


def main() -> int:
    api = read("api/v1/auth/change-password.php")
    order = [
        "kpi_v1_auth_require_post()",
        "kpi_v1_auth_current_user_id()",
        "kpi_v1_require_expected_user(",
        "kpi_v1_auth_reject_if_disabled(",
        "kpi_v1_registration_password_ok(",
        "password_verify($current",
        "password_verify($next",
        "password_hash($next, PASSWORD_DEFAULT)",
        "kpi_v1_session_revoke_bump(",
        "session_regenerate_id(true)",
        "kpi_v1_auth_set_session_user(",
    ]
    pos = [api.find(s) for s in order]
    check("endpoint: POST → session → expected user → disabled → policy → current verify → reuse → hash → revoke → regenerate → restamp",
          all(p >= 0 for p in pos) and pos == sorted(pos), str(list(zip(order, pos))))
    check("endpoint: no session → 401 unauthorized", "kpi_v1_json_out(401, ['ok' => false, 'error' => 'unauthorized'])" in api)
    for code in ("password_mismatch", "password_weak", "current_password_incorrect", "password_unchanged",
                 "password_conflict", "change_failed"):
        check(f"endpoint: error code {code}", f"'error' => '{code}'" in api)
    check("endpoint: MySQL update only replaces the verified hash (AND password_hash = ?) inside a transaction",
          "WHERE user_id = ? AND password_hash = ?" in api and "beginTransaction()" in api
          and api.count("rollBack()") >= 3 and "commit()" in api)
    check("endpoint: revoke failure rolls back before commit",
          api.find("kpi_v1_session_revoke_bump($uid) === null") < api.find("$pdo->commit()"))
    check("endpoint: file mode checks the hash is unchanged before writing",
          "hash_equals($oldHash" in api and api.find("hash_equals($oldHash") < api.find("kpi_v1_auth_write_user($fresh)"))
    outs = re.findall(r"kpi_v1_json_out\((.*?)\);", api, flags=re.S)
    check("endpoint: responses never include passwords or hashes",
          outs and not any(re.search(r"\$(current|next|confirm|hash|oldHash)\b|password_hash", o) for o in outs), str(outs))
    check("endpoint: success body is only {ok:true}", "kpi_v1_json_out(200, ['ok' => true]);" in api)

    reset = read("api/v1/_password_reset.php")
    check("password reset contract unchanged: min 8, revoke bump, clears current session",
          "strlen($newPassword) < 8" in reset and "kpi_v1_session_revoke_bump($user['userId'])" in reset
          and "kpi_v1_auth_clear_session();" in reset)
    admin_pw = read("api/v1/auth/admin-set-password.php")
    check("admin set password contract unchanged (admin token, min 8)",
          "kpi_v1_auth_require_admin($cfg, $body);" in admin_pw and "strlen($password) < 8" in admin_pw)
    reg = read("api/v1/_registration.php")
    check("password rule shared with registration (8+, letter, digit, symbol)",
          "function kpi_v1_registration_password_ok" in reg and "[^a-zA-Z0-9]" in reg)

    page_js = read("js/kpi-change-password-page.js")
    code_js = strip_js_comments(page_js)
    check("page JS: posts to /auth/change-password.php with credentials",
          "'/auth/change-password.php'" in code_js and "credentials: 'include'" in code_js)
    check("page JS: success screen only after status 200 and ok === true",
          "r.status === 200 && r.data && r.data.ok === true" in code_js
          and code_js.find("r.data.ok === true") < code_js.find("change_password_success.html"))
    sets = re.findall(r"(localStorage|sessionStorage)\.setItem\(([^)]*)\)", code_js)
    check("page JS: the only storage write is the success flag (never a password)",
          sets == [("sessionStorage", "'kpi-password-change-success', '1'")], str(sets))
    check("page JS: removes legacy kpi-auth-password and reads the success flag once",
          "localStorage.removeItem('kpi-auth-password')" in code_js
          and "sessionStorage.removeItem('kpi-password-change-success')" in code_js)
    check("page JS: double submit guard (inFlight + disabled button)",
          "if (inFlight) return;" in code_js and "submitBtn.disabled = on" in code_js)
    check("page JS: relies only on pre-existing __KPI_AUTH members",
          set(re.findall(r"auth\.(\w+)", code_js)) <= {"attachExpectedUser", "resolveAuthBase", "handleUnauthorizedSession",
                                                        "staleAccountMessage", "ensureUserScopeBound"},
          str(set(re.findall(r"auth\.(\w+)", code_js))))
    check("page JS: 3 languages for every message", code_js.count("t(") >= 10 and "目前的密碼不正確" in code_js
          and "Current password is incorrect." in code_js and "現在のパスワードが正しくありません。" in code_js)

    client = strip_js_comments(read("js/kpi-auth-client.js"))
    boot = client.find("enforceSession().catch")
    check("auth client: legacy plaintext password removed on every page load",
          0 <= client.find("localStorage.removeItem('kpi-auth-password')") < boot)

    for lang, (folder, src, label) in LANGS.items():
        page = read(f"{folder}/change_password.html")
        ok = read(f"{folder}/change_password_success.html")
        check(f"{lang}: current / new / confirm fields in order",
              0 <= page.find('id="current-password"') < page.find('id="new-password"') < page.find('id="confirm-password"'))
        check(f"{lang}: current password label + autocomplete", label in page and 'autocomplete="current-password"' in page)
        check(f"{lang}: inline errors for each field + form error",
              all(f'id="{e}"' in page for e in ("err-current-password", "err-new-password", "err-confirm-password", "err-change-password")))
        check(f"{lang}: no password written to browser storage",
              "kpi-auth-password" not in page and not re.search(r"(localStorage|sessionStorage)\.setItem\([^)]*[Pp]w", page))
        check(f"{lang}: no fake success redirect left inline", "change_password_success.html';" not in page)
        for rel, text in ((f"{folder}/change_password.html", page), (f"{folder}/change_password_success.html", ok)):
            check(f"{lang}: {rel.split('/')[-1]} loads page JS once with ?v=",
                  len(re.findall(re.escape(src) + r"\?v=[0-9a-f]{12}\"", text)) == 1)
        check(f"{lang}: success message hidden until server-confirmed",
              'id="password-success" hidden' in ok and "kpi-password-change-success" not in ok)

    zh_build = read("scripts/build_zh_tw_change_password_pages.py")
    check("zh-tw generator knows the Current Password label", '("Current Password :", "目前密碼 :")' in zh_build)

    stamp = subprocess.run([sys.executable, str(ROOT / "scripts" / "stamp_registration_assets.py"), "--check"],
                           capture_output=True, text=True)
    check("all stamped pages carry the current content hash", stamp.returncode == 0, stamp.stdout.strip())

    print(f"\n{PASSED} passed, {FAILED} failed")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
