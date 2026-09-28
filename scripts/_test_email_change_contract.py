# -*- coding: utf-8 -*-
"""BR-LAUNCH-09 Phase 2 Email Change contract — static checks (endpoints, confirmation, pages, no local-only change)."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAILED = 0
PASSED = 0

LANGS = {
    "ja": ("setting", "../js/kpi-change-email-page.js",
           ["現在のメールアドレス :", "新しいメールアドレス :", "新しいメールアドレス（確認） :", "現在のパスワード :", "確認コード :"]),
    "en": ("en/setting", "../../js/kpi-change-email-page.js",
           ["Current Email Address :", "New Email Address :", "Confirm New Email Address :", "Current Password :", "Confirmation Code :"]),
    "zh": ("zh-tw/setting", "../../js/kpi-change-email-page.js",
           ["目前的電子信箱 :", "新的電子信箱 :", "確認新的電子信箱 :", "目前密碼 :", "確認碼 :"]),
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


def in_order(text: str, parts: list[str]) -> bool:
    pos = [text.find(p) for p in parts]
    return all(p >= 0 for p in pos) and pos == sorted(pos)


def main() -> int:
    lib = read("api/v1/_email_change.php")
    rq = read("api/v1/auth/request-email-change.php")
    cf = read("api/v1/auth/confirm-email-change.php")

    check("request: POST → session → expected user → disabled → email rules → current password → same email",
          in_order(rq, ["kpi_v1_auth_require_post()", "kpi_v1_auth_current_user_id()", "kpi_v1_require_expected_user(",
                        "kpi_v1_auth_reject_if_disabled(", "'invalid_email'", "'email_mismatch'", "password_verify($current",
                        "'email_unchanged'", "$lock = kpi_v1_email_change_lock()",
                        "$result = kpi_v1_email_change_request_locked("]))
    check("request (locked): duplicate → throttle → record send → pending → mail",
          in_order(rq, ["function kpi_v1_email_change_request_locked", "'email_unavailable'", "'too_many_requests'",
                        "kpi_v1_email_change_record_send(", "kpi_v1_email_change_write_pending(", "kpi_v1_mail_send("]))
    check("request: never writes the user record or bumps sessions",
          "kpi_v1_auth_write_user" not in rq and "revoke_bump" not in rq and "UPDATE kpi_users" not in rq)
    check("request: 6-digit random code, stored only as password_hash",
          "random_int(0, 999999)" in rq and "password_hash($code, PASSWORD_DEFAULT)" in rq and "'codeHash' => $codeHash" in rq)
    check("request: pending bound to old email, password fingerprint and revoke epoch",
          all(k in rq for k in ("'oldEmail' => $oldEmail", "'passwordFingerprint' =>", "'revokeEpoch' =>")))
    check("request: TTL reuses Password Reset TTL", "kpi_v1_password_reset_ttl_minutes($cfg)" in rq)
    check("request: mail failure removes the pending request and reports mail_failed",
          in_order(rq[rq.find("kpi_v1_mail_send("):], ["kpi_v1_mail_send(", "kpi_v1_email_change_delete_pending($uid)", "'mail_failed'"]))
    check("request: success body never carries the code", "'code'" not in rq.split("return [200", 1)[-1].split("]]", 1)[0])

    check("throttle: Password Reset cooldown + hourly cap",
          "kpi_v1_password_reset_cooldown_seconds($cfg)" in lib and "KPI_EMAIL_CHANGE_MAX_SENDS_PER_HOUR = 5" in lib)
    check("storage: file-backed under data/email_change (no schema)", "/data/email_change" in lib
          and "CREATE TABLE" not in lib and "kpi_email_change" not in read("api/v1/schema.sql"))
    check("lock: shares the registration lock (file email index)", "register.lock" in lib)

    check("confirm: session → expected user → disabled (voids pending) → lock",
          in_order(cf, ["kpi_v1_auth_current_user_id()", "kpi_v1_require_expected_user(", "kpi_v1_auth_user_is_disabled($user)",
                        "kpi_v1_email_change_delete_pending($uid);", "kpi_v1_email_change_lock()"]))
    check("confirm: expiry → attempts → code verify → state re-check → duplicate re-check → apply",
          in_order(cf, ["'expiresAt'", "KPI_EMAIL_CHANGE_MAX_ATTEMPTS", "password_verify($code", "passwordFingerprint",
                        "revokeEpoch", "kpi_v1_auth_find_user_by_email($newEmail)", "kpi_v1_email_change_apply("]))
    check("confirm: attempts capped at 5", "KPI_EMAIL_CHANGE_MAX_ATTEMPTS = 5" in lib and "'code_locked'" in cf)
    for code in ("code_expired", "code_invalid", "code_locked", "email_change_stale", "email_unavailable", "change_failed"):
        check(f"confirm: error code {code}", f"'error' => '{code}'" in cf)
    check("confirm: success regenerates this session and re-stamps it",
          in_order(cf, ["session_regenerate_id(true)", "kpi_v1_auth_set_session_user($uid)"]))
    check("confirm: old address notice after commit, masked new email",
          in_order(cf, ["kpi_v1_auth_set_session_user($uid)", "kpi_v1_email_change_notice_mail(", "kpi_v1_mail_send($cfg, $done['oldEmail']"])
          and "kpi_v1_email_change_mask(" in cf)

    check("apply (MySQL): conditional UPDATE on old email + password hash in a transaction",
          "WHERE user_id = ? AND email = ? AND password_hash = ?" in lib and "beginTransaction()" in lib and "commit()" in lib)
    check("apply (MySQL): UNIQUE violation (23000) → email_unavailable", "'23000') ? 'email_unavailable'" in lib)
    check("apply: other sessions revoked (revoke epoch bump) before commit",
          lib.find("kpi_v1_session_revoke_bump($userId) === null") < lib.find("$pdo->commit()"))
    check("apply (file): index swap removes old, adds new, rolls back on failure",
          "unset($nextIndex[$oldEmail])" in lib and "$nextIndex[$newEmail] = (string) $userId" in lib
          and "kpi_v1_registration_write_json_atomic($userPath, $fresh)" in lib)
    for loc, frag in (("ja", "確認コード: {$code}"), ("zh", "確認碼：{$code}"), ("en", "Confirmation code: {$code}"),
                      ("ja notice", "メールアドレスが変更されました"), ("zh notice", "電子信箱已變更"), ("en notice", "Email Address Changed")):
        check(f"mail copy: {loc}", frag in lib)
    for rel, text in (("request", rq), ("confirm", cf)):
        outs = re.findall(r"(?:kpi_v1_json_out\(|return \[)(.*?)\);?\n", text)
        check(f"{rel}: responses never include password / code / hashes",
              outs and not any(re.search(r"\$(current|code|codeHash|passwordHash)\b|password_hash", o) for o in outs), str(outs))

    page_js = strip_js_comments(read("js/kpi-change-email-page.js"))
    check("page JS: request + confirm endpoints with credentials",
          "'/auth/request-email-change.php'" in page_js and "'/auth/confirm-email-change.php'" in page_js
          and "credentials: 'include'" in page_js)
    check("page JS: success flag only after confirm status 200 and ok === true",
          in_order(page_js[page_js.find("'/auth/confirm-email-change.php'"):],
                   ["'/auth/confirm-email-change.php'", "r.status === 200 && r.data && r.data.ok === true",
                             "sessionStorage.setItem('kpi-email-change-success', '1')", "'change_email.html'"]))
    sets = re.findall(r"(localStorage|sessionStorage)\.setItem\(([^)]*)\)", page_js)
    check("page JS: the only storage write is the success flag (no email / password / code, no local profile)",
          sets == [("sessionStorage", "'kpi-email-change-success', '1'")] and "kpi-profile-last" not in page_js, str(sets))
    check("page JS: double submit guard", "if (inFlight) return;" in page_js and "requestBtn.disabled = on" in page_js)
    check("page JS: relies only on pre-existing __KPI_AUTH members",
          set(re.findall(r"auth\.(\w+)", page_js)) <= {"attachExpectedUser", "resolveAuthBase", "handleUnauthorizedSession",
                                                       "staleAccountMessage", "ensureUserScopeBound"},
          str(set(re.findall(r"auth\.(\w+)", page_js))))
    check("page JS: 3 languages", "此電子信箱無法使用。" in page_js and "This email address cannot be used." in page_js
          and "このメールアドレスは使用できません。" in page_js)

    for lang, (folder, src, labels) in LANGS.items():
        page = read(f"{folder}/change_email_edit.html")
        view = read(f"{folder}/change_email.html")
        check(f"{lang}: labels in page language", all(l in page for l in labels), str([l for l in labels if l not in page]))
        check(f"{lang}: step A fields in order, step B hidden",
              in_order(page, ['id="change-email-form"', 'id="new-email"', 'id="confirm-email"', 'id="current-password"',
                              'id="err-change-email"', 'id="confirm-email-form" novalidate hidden', 'id="email-code"',
                              'id="err-confirm-email-form"', 'id="email-change-back"']))
        check(f"{lang}: no prefilled password value", not re.search(r'type="password"[^>]*value=', page) and "Forgelab" not in page)
        check(f"{lang}: fake local-only handler removed",
              "kpi-profile-last" not in page and "kpi-email-change-success" not in page)
        check(f"{lang}: page JS once with ?v=", len(re.findall(re.escape(src) + r"\?v=[0-9a-f]{12}\"", page)) == 1)
        check(f"{lang}: success banner hidden until flagged", 'id="email-change-success" role="status" aria-live="polite" hidden' in view)

    stamp = subprocess.run([sys.executable, str(ROOT / "scripts" / "stamp_registration_assets.py"), "--check"],
                           capture_output=True, text=True)
    check("all stamped pages carry the current content hash", stamp.returncode == 0, stamp.stdout.strip())

    print(f"\n{PASSED} passed, {FAILED} failed")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
