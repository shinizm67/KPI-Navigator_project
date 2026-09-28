# -*- coding: utf-8 -*-
"""BR-LAUNCH-09 Phase 3 Delete Account contract — static checks (endpoint, protected / child rules, pages, no mock flow)."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAILED = 0
PASSED = 0

LANGS = {
    "ja": ("setting", "../js/kpi-delete-account-page.js", "../images/",
           ["1. 削除される内容", "2. データの扱い", ">3. 本人確認<", "4. 最終確認", "アカウントを削除しました。"]),
    "en": ("en/setting", "../../js/kpi-delete-account-page.js", "../../images/",
           ["1. What Is Deleted", "2. Your Data", ">3. Verify Identity<", "4. Final Confirmation", "Your account has been deleted."]),
    "zh": ("zh-tw/setting", "../../js/kpi-delete-account-page.js", "../../images/",
           ["1. 刪除內容", "2. 資料處理", ">3. 身分驗證<", "4. 最終確認", "您的帳戶已刪除。"]),
}
STEP_PAGES = ["delete_account1.html", "delete_account3.html", "delete_account4-1.html", "delete_account5.html"]
MOCK_WORDS = ["Stripe", "delete-otp", "6桁", "6-digit", "6 位數", "2025年3月28日", "March 28, 2025",
              "delete_account4-2.html", "delete_account2.html", "window.confirm", "delete-accomplished-form"]


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


def in_order(text: str, parts: list[str]) -> bool:
    pos = [text.find(p) for p in parts]
    return all(p >= 0 for p in pos) and pos == sorted(pos)


def main() -> int:
    lib = read("api/v1/_account_delete.php")
    ep = read("api/v1/auth/delete-account.php")
    js = read("js/kpi-delete-account-page.js")

    check("endpoint: POST → session → expected user → user → disabled → action",
          in_order(ep, ["kpi_v1_auth_require_post()", "kpi_v1_auth_current_user_id()", "kpi_v1_require_expected_user(",
                        "kpi_v1_auth_read_user($uid)", "kpi_v1_auth_reject_if_disabled(", "$action ="]))
    check("verify: throttle → password_verify → protected / child → intent",
          in_order(ep, ["$action === 'verify'", "kpi_v1_account_delete_failure_wait(", "password_verify($current",
                        "kpi_v1_account_delete_reject_reason(", "kpi_v1_account_delete_issue_intent("]))
    check("delete: acknowledge === true → lock → locked execute → unlock → clear session on success / gone",
          in_order(ep, ["$body['acknowledge'] !== true", "kpi_v1_email_change_lock()", "kpi_v1_account_delete_execute_locked(",
                        "kpi_v1_email_change_unlock($lock)", "if ($status === 200 || $status === 401)"]))
    check("endpoint never echoes passwords / hashes", "passwordHash" not in ep.split("kpi_v1_auth_read_user($uid);", 1)[1]
          .replace("empty($user['passwordHash'])", "").replace("(string) $user['passwordHash']", ""))
    check("only role user may self-delete", "$role !== 'user'" in lib and "'protected_account'" in lib)
    check("children reject, lookup error fails closed",
          "'has_child_accounts'" in lib and re.search(r"catch \(Throwable \$e\) \{\s*return true;", lib) is not None)
    check("children never cascaded or re-parented", "parent_user_id = NULL" not in lib and "UPDATE kpi_users" not in lib)
    check("execute (locked): fresh user → disabled → role / child → intent → preflight → record → revoke → cleanup",
          in_order(lib[lib.find("function kpi_v1_account_delete_execute_locked"):],
                   ["function kpi_v1_account_delete_execute_locked", "kpi_v1_auth_read_user($userId)",
                         "kpi_v1_auth_user_is_disabled(", "kpi_v1_account_delete_reject_reason(", "kpi_v1_account_delete_intent_valid(",
                         "kpi_v1_account_delete_preflight($cfg)", "kpi_v1_account_delete_user_record(", "kpi_v1_session_revoke_bump(",
                         "kpi_v1_account_delete_cleanup_files("]))
    check("intent bound to user / email / password / revoke epoch / expiry",
          all(k in lib for k in ["'passwordFingerprint'", "'revokeEpoch'", "'expiresAt'", "KPI_ACCOUNT_DELETE_INTENT_TTL"]))
    check("MySQL: row locked, re-checked and deleted in one transaction (consents via existing CASCADE)",
          in_order(lib, ["$pdo->beginTransaction()", "FOR UPDATE", "kpi_v1_account_delete_has_children($cfg, $userId, $pdo)",
                         "DELETE FROM kpi_users WHERE user_id = ?", "$pdo->commit()"])
          and "kpi_user_consents" not in lib)
    check("revoke file kept (bumped, never unlinked)", "session_revoke_path" not in lib and "kpi_v1_session_revoke_bump($userId)" in lib)
    check("feedback anonymized, not deleted",
          "$row['userId'] = null;" in lib and "$row['contactEmail'] = '';" in lib and "$row['userAgent'] = '';" in lib
          and "'/feedback/*.json'" in lib)
    check("file cleanup covers email change / reset tokens / store / profile / consent / backups / plan history",
          all(k in lib for k in ["['pending', 'sends']", "tok_*.json", "'/profiles/'", "'/consents/'", "'/backups/'",
                                 "kpi_v1_admin_plan_history_path()"]))

    check("js: completion only after 200 ok && deleted",
          "r.status === 200 && r.data && r.data.ok === true && r.data.deleted === true" in js
          and js.find("sessionStorage.setItem(DONE_FLAG") > js.find("r.data.deleted === true"))
    check("js: completion page requires the success flag", "sessionStorage.getItem(DONE_FLAG) === '1'" in js)
    check("js: double submit guarded", "if (deleting) return;" in js and "finalBtn.disabled = true" in js)
    check("js: theme kept, account keys cleared",
          "'kpi-office-mode': true" in js and "'kpiNavigator.lastKpiUserId'" in js and "clearUserScopedLocalData" in js)
    check("js: no password written to storage", not re.search(r"setItem\([^)]*pw", js))

    for lang, (folder, js_rel, img, texts) in LANGS.items():
        pages = {p: read(f"{folder}/{p}") for p in STEP_PAGES + ["delete_account_accomplished.html"]}
        allt = "".join(pages.values())
        check(f"{lang}: step headings / completion text", all(t in allt for t in texts),
              str([t for t in texts if t not in allt]))
        main = "".join(re.search(r"<main[\s\S]*?</main>", t).group(0) for t in pages.values())
        scripts = "".join(re.findall(r"<script>[\s\S]*?</script>", allt))
        bad = [w for w in MOCK_WORDS if w in main or w in scripts]
        check(f"{lang}: no mock Stripe / OTP / fake confirm left", not bad, str(bad))
        check(f"{lang}: stepper images use {img}",
              all(f'src="{img}stepper_' in pages[p] for p in STEP_PAGES) and '="../images/' not in "".join(pages.values())
              if img != "../images/" else all(f'src="{img}stepper_' in pages[p] for p in STEP_PAGES))
        for p in ("delete_account4-1.html", "delete_account5.html", "delete_account_accomplished.html"):
            check(f"{lang}: {p} loads the stamped page script",
                  re.search(re.escape(js_rel) + r"\?v=[0-9a-f]{12}\"", pages[p]) is not None)
        check(f"{lang}: completion page does not load the session guard",
              "kpi-auth-client.js" not in pages["delete_account_accomplished.html"]
              and 'id="delete-accomplished-panel"' in pages["delete_account_accomplished.html"]
              and "ACCOUNT DELETED" in pages["delete_account_accomplished.html"])
        check(f"{lang}: final step has acknowledgement + real form",
              all(k in pages["delete_account5.html"] for k in ['id="delete-final-form"', 'id="delete-final-ack"',
                                                               'id="delete-final-error"', 'id="btn-final-delete"']))
        for stub in ("delete_account2.html", "delete_account4-2.html"):
            s = read(f"{folder}/{stub}")
            check(f"{lang}: {stub} redirects to step 1", "location.replace('delete_account1.html')" in s and len(s) < 1200)

    rc = subprocess.call([sys.executable, str(ROOT / "scripts" / "stamp_registration_assets.py"), "--check"],
                         stdout=subprocess.DEVNULL)
    check("asset stamps up to date", rc == 0)

    print(f"\n{PASSED} passed, {FAILED} failed")
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
