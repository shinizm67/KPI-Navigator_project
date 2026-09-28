# -*- coding: utf-8 -*-
"""BR-LAUNCH-09 Phase 3A Extension — Account Lifecycle History contract (static checks).

HMAC only (no raw email), same-transaction history row, fail closed, 3-year purge, NEW / RETURNED on account creation,
feedback plan / page blanked, STEP 2 copy, no key in the repo."""
from __future__ import annotations

import re
import subprocess
import sys
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


def in_order(text: str, parts: list[str]) -> bool:
    pos = [text.find(p) for p in parts]
    return all(p >= 0 for p in pos) and pos == sorted(pos)


def fn(text: str, name: str) -> str:
    start = text.find("function " + name + "(")
    nxt = text.find("\nfunction ", start + 1)
    return text[start:nxt if nxt > 0 else len(text)] if start >= 0 else ""


def table(sql: str, name: str) -> str:
    m = re.search(r"CREATE TABLE IF NOT EXISTS " + name + r" \(([\s\S]*?)\) ENGINE", sql)
    return m.group(1) if m else ""


def main() -> int:
    lc = read("api/v1/_lifecycle.php")
    ad = read("api/v1/_account_delete.php")
    reg = read("api/v1/auth/register.php")
    adm = read("api/v1/auth/admin-create-user.php")
    schema = read("api/v1/schema.sql")
    mig = read("api/v1/schema_kpi_account_lifecycle.add.sql")
    example = read("api/v1/config.example.php")

    check("HMAC-SHA256 with the server key over the normalized email",
          "hash_hmac('sha256', 'kpn-lifecycle-email:' . kpi_v1_lifecycle_normalize_email($email), (string) $key)" in lc
          and "strtolower(trim((string) $email))" in fn(lc, "kpi_v1_lifecycle_normalize_email"))
    check("no plain SHA-256 of the email", not re.search(r"hash\('sha256',[^)]*email", lc))
    check("key >= 32 chars and a safe key id, else not ready",
          "KPI_LIFECYCLE_MIN_KEY_LENGTH = 32" in lc and "^[A-Za-z0-9_-]{1,16}$" in lc)
    check("retired keys still match (rotation)", "lifecycleHmacPreviousKeys" in lc and "kpi_v1_lifecycle_email_hmacs(" in lc)
    ins = fn(lc, "kpi_v1_lifecycle_db_insert")
    check("history INSERT stores the HMAC, never the email / hash / UA / IP",
          "email_hmac" in ins and not re.search(r"\(\s*[^)]*\bemail\s*,", ins.replace("email_hmac", ""))
          and not any(k in ins for k in ("password", "user_agent", "ip_address", "stripe")))
    rec = fn(lc, "kpi_v1_lifecycle_build_record")
    check("record fields per contract",
          all(k in rec for k in ["'previousUserId'", "'emailHmac'", "'hmacKeyId'", "'accountCreatedAt'", "'deletedAt'",
                                  "'lifetimeDays'", "'planAtDeletion'", "'roleAtDeletion'", "'accountKind'", "'signupOrigin'",
                                  "'cleanupStatus'", "'excludeFromMetrics'", "'returnedAt'", "'returnCount'"])
          and "'email' =>" not in rec and "passwordHash" not in rec)
    check("retention: purge rows older than deleted_at + 3 years",
          "KPI_LIFECYCLE_RETENTION = '-3 years'" in lc and "DELETE FROM kpi_account_deletions WHERE deleted_at < ?" in lc)
    check("readiness checks key + both tables (MySQL) / readable files (file)",
          all(k in fn(lc, "kpi_v1_lifecycle_ready") for k in ["kpi_v1_lifecycle_active_key($cfg) === null",
                                                              "FROM kpi_account_deletions", "FROM kpi_account_origins",
                                                              "kpi_v1_lifecycle_file_read('deletions') !== null"]))
    created = fn(lc, "kpi_v1_lifecycle_on_account_created")
    check("account creation: match -> returned (+1 on every matching row, first returned_at kept), else new",
          "return_count = return_count + 1, returned_at = COALESCE(returned_at, ?)" in created
          and "'returned' : 'new'" in created)
    check("account creation never blocked: failures -> origin unknown + log",
          "kpi_v1_lifecycle_mark_unknown(" in created and "error_log('kpn lifecycle: origin lookup failed" in created
          and "json_out" not in lc)

    check("delete preflight fails closed without lifecycle readiness",
          in_order(fn(ad, "kpi_v1_account_delete_preflight"), ["if (!kpi_v1_lifecycle_ready($cfg))", "return false;"]))
    rec_fn = fn(ad, "kpi_v1_account_delete_user_record")
    check("MySQL: lock row → child re-check → history INSERT → DELETE kpi_users → commit (one transaction)",
          in_order(rec_fn, ["$pdo->beginTransaction()", "FOR UPDATE", "kpi_v1_account_delete_has_children($cfg, $userId, $pdo)",
                            "kpi_v1_lifecycle_db_insert($pdo, $record)", "DELETE FROM kpi_users WHERE user_id = ?",
                            "$pdo->commit()"]))
    check("MySQL: history record built from the locked row", "kpi_v1_lifecycle_db_origin($pdo, $userId)" in rec_fn
          and "'email' => (string) $row['email']" in rec_fn)
    check("file: history row written before the user file is removed and undone on failure",
          in_order(rec_fn[rec_fn.find("$userPath = "):], ["kpi_v1_lifecycle_file_insert($record)", "@unlink($userPath)"])
          and rec_fn.count("kpi_v1_lifecycle_file_remove($record['lifecycleId'])") == 2)
    ex = fn(ad, "kpi_v1_account_delete_execute_locked")
    check("after delete: revoke → cleanup → cleanup status → purge",
          in_order(ex, ["kpi_v1_session_revoke_bump(", "kpi_v1_account_delete_cleanup_files(", "kpi_v1_lifecycle_set_cleanup(",
                        "kpi_v1_lifecycle_purge($cfg)"]))
    check("feedback anonymization also blanks plan and page",
          "$row['plan'] = '';" in ad and "$row['pageUrl'] = '';" in ad and "$row['message']" not in ad
          and "$row['category']" not in ad and "$row['at']" not in ad)
    check("consents still deleted with the account (no lifecycle copy)", "consent" not in lc.lower().replace("consent contents", ""))

    check("register.php records origin after the account + consent exist",
          in_order(reg, ["kpi_v1_registration_create_user_with_consent(", "kpi_v1_lifecycle_on_account_created(",
                         "kpi_v1_auth_set_session_user("]))
    check("admin-create-user.php records origin after the account exists",
          in_order(adm, ["kpi_v1_auth_write_user($user)", "kpi_v1_auth_write_email_index($index)", "kpi_v1_lifecycle_on_account_created("]))

    for label, sql in (("schema.sql", schema), ("migration", mig)):
        d = table(sql, "kpi_account_deletions")
        o = table(sql, "kpi_account_origins")
        check(f"{label}: history table without email / password / ip / ua / stripe columns and without FK",
              d != "" and "email_hmac CHAR(64)" in d and not re.search(r"^\s*(email|password_hash|ip|user_agent)\s", d, re.M)
              and "stripe" not in d.lower() and "FOREIGN KEY" not in d)
        check(f"{label}: origins table cascades with the account", "REFERENCES kpi_users (user_id)" in o and "ON DELETE CASCADE" in o)
    check("schema.sql: lifecycle tables load with or without the consent section",
          schema.find("kpi_account_deletions") < schema.find("-- Legal consent (append-only)"))

    check("config.example: key documented and empty", "'lifecycleHmacKey' => ''," in example)
    tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout.split()
    leaks = []
    for rel in tracked:
        if rel.endswith((".php", ".js", ".html", ".md", ".json", ".py")) and not rel.startswith("scripts/_tmp_"):
            try:
                txt = (ROOT / rel).read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if re.search(r"['\"]lifecycleHmacKey['\"]\s*=>\s*['\"][^'\"]+['\"]", txt):
                leaks.append(rel)
    check("no lifecycle HMAC key committed", not leaks, str(leaks))

    step2 = {
        "setting/delete_account3.html": ["退会履歴（メールアドレスを含まない最小限の記録", "削除日から3年後に自動で消去されます",
                                         "フィードバックの本文・送信日時・種別", "サポート宛てに送信済みのメール（アカウント削除では自動削除されません）"],
        "en/setting/delete_account3.html": ["Account deletion record (a minimal record without your email address",
                                            "Erased automatically 3 years after the deletion date",
                                            "The text, date and category of feedback you sent",
                                            "Emails already sent to support (not deleted automatically by account deletion)"],
        "zh-tw/setting/delete_account3.html": ["帳戶刪除紀錄（不含電子信箱的最小紀錄", "自刪除日起 3 年後自動清除",
                                               "您送出的意見回饋內文、送出日期時間與類別", "已寄送給客服的電子郵件（不會因帳戶刪除而自動刪除）"],
    }
    for rel, texts in step2.items():
        t = read(rel)
        check(f"STEP 2 copy: {rel}", all(x in t for x in texts), str([x for x in texts if x not in t]))

    print(f"\n{PASSED} passed, {FAILED} failed")
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
