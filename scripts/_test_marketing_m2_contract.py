# -*- coding: utf-8 -*-
"""BR-LAUNCH-09 Extension M2 — Marketing opt-in + Lifecycle segment contract (static checks).

Opt-in only / separate from the Terms consent, evidence retention (never mailed → delete, mailed → 3 years),
delete keep / stop choice, email change follows the account, token never stored, lifecycle segments coded only,
schema additive, registration limits unchanged, no sender."""
from __future__ import annotations

import re
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


def fn(text: str, name: str) -> str:
    start = text.find("function " + name + "(")
    nxt = text.find("\nfunction ", start + 1)
    return text[start:nxt if nxt > 0 else len(text)] if start >= 0 else ""


def in_order(text: str, parts: list[str]) -> bool:
    pos = [text.find(p) for p in parts]
    return all(p >= 0 for p in pos) and pos == sorted(pos)


def table(sql: str, name: str) -> str:
    m = re.search(r"CREATE TABLE IF NOT EXISTS " + name + r" \(([\s\S]*?)\) ENGINE", sql)
    return m.group(1) if m else ""


def main() -> int:
    mk = read("api/v1/_marketing.php")
    lc = read("api/v1/_lifecycle.php")
    ad = read("api/v1/_account_delete.php")
    ec = read("api/v1/_email_change.php")
    rg = read("api/v1/_registration.php")
    reg = read("api/v1/auth/register.php")
    dele = read("api/v1/auth/delete-account.php")
    unsub = read("api/v1/marketing/unsubscribe.php")
    pref = read("api/v1/marketing/preference.php")
    fl = read("api/v1/admin/marketing-subscribers.php")
    fa = read("api/v1/admin/marketing-action.php")
    lookup = read("api/v1/admin/lifecycle-lookup.php")
    schema = read("api/v1/schema.sql")
    mig = read("api/v1/schema_kpi_marketing.add.sql")

    # Consent
    c = fn(mk, "kpi_v1_marketing_consent_from_registration")
    check("registration: only marketingOptIn === true creates consent; else nothing",
          "$body['marketingOptIn'] !== true" in c and "return null;" in c)
    check("registration: wording version must match (400 marketing_consent_outdated)",
          "!== KPI_MARKETING_CONSENT_VERSION" in c and "marketing_consent_outdated" in c)
    check("consent evidence: source / text version / privacy version / locale",
          all(k in c for k in ["'registration'", "KPI_MARKETING_CONSENT_VERSION", "KPI_PRIVACY_VERSION", "kpi_v1_marketing_locale("]))
    check("fixed wording kept per version (ja / en / zh-TW)",
          "'mkt-2026-09-29' => [" in mk and all(k in mk for k in ["'ja' =>", "'en' =>", "'zh-TW' =>"]))
    check("register.php: consent before duplicate check; marketing written inside the account + consent unit",
          in_order(reg, ["kpi_v1_registration_consent_from_body(", "kpi_v1_marketing_consent_from_registration(",
                         "isset($index[$email])", "kpi_v1_registration_create_user_with_consent($cfg, $user, $consent['record'], $alsoWrite)"])
          and "$marketing === null ? null" in reg)
    cr = fn(rg, "kpi_v1_registration_create_user_with_consent")
    check("MySQL: marketing hook before commit, rollback on false",
          in_order(cr, ["kpi_v1_consent_db_insert(", "$alsoWrite($pdo) !== true", "$pdo->rollBack();", "$pdo->commit();"]))
    fc = fn(rg, "kpi_v1_registration_file_create")
    check("file: marketing hook failure undoes index, consent and user",
          in_order(fc[fc.find("$alsoWrite(null) !== true"):], ["$alsoWrite(null) !== true", "kpi_v1_auth_email_index_path(), $prevIndex)",
                                                              "@unlink($consentPath);", "@unlink($userPath);"]))
    check("registration limits unchanged (no marketing bucket in the registration map)",
          "marketing" not in fn(rg, "kpi_v1_registration_rate_limits"))

    # Retention
    stop = fn(mk, "kpi_v1_marketing_plan_stop")
    check("stop: never mailed → row deleted (null)", "if (empty($old['lastMarketingSentAt'])) {\n        return [null, []];" in stop)
    check("stop: mailed → evidence-only, token revoked, retain = last send + 3 years",
          all(k in stop for k in ["'unsubscribed'", "$row['tokenNonce'] = null;", "$row['tokenHash'] = null;",
                                  "KPI_MARKETING_EVIDENCE_RETENTION"]) and "const KPI_MARKETING_EVIDENCE_RETENTION = '+3 years';" in mk)
    check("purge: unsubscribed rows past retain_until deleted with their evidence",
          "(string) $r['retainUntil'] < $now" in fn(mk, "kpi_v1_marketing_purge_in")
          and "DELETE FROM kpi_marketing_consent_events WHERE subscriber_id = ?" in mk)
    check("purge runs after each account delete and before the Founder list",
          "kpi_v1_marketing_purge($cfg)" in ad and "kpi_v1_marketing_purge($cfg);" in fn(mk, "kpi_v1_marketing_founder_list"))
    fa_fn = fn(mk, "kpi_v1_marketing_founder_action")
    check("Founder erase: legal hold for mailed evidence", "'legal_hold'" in fa_fn and "'evidence_only'" in fa_fn and "409" in fa)

    # Delete
    dl = fn(mk, "kpi_v1_marketing_op_account_deleted")
    check("delete: subscribed needs keep / stop, else choice_required",
          in_order(dl, ["$choice === 'keep'", "$choice !== 'stop'", "return 'choice_required';", "'delete_stop'"]))
    check("delete keep: only the account link is removed + keep_after_delete evidence",
          "$new['accountUserId'] = null;" in dl and "'keep_after_delete'" in dl and "'subscribed'" in dl)
    check("delete never creates / turns on a subscription (no subscribe call)", "op_subscribe" not in dl)
    rec = fn(ad, "kpi_v1_account_delete_user_record")
    check("MySQL: marketing settled inside the delete transaction, before the history row",
          in_order(rec, ["$pdo->beginTransaction()", "kpi_v1_marketing_op_account_deleted(", "'marketing_choice_required'",
                         "kpi_v1_lifecycle_db_insert($pdo, $record)", "$pdo->commit()"]))
    check("file: marketing snapshot restored on every later failure", rec.count("kpi_v1_marketing_file_restore($marketingSnap);") == 3)
    check("delete API: marketingAfterDelete keep|stop only; 400 marketing_choice_required; verify answers subscribed",
          "['keep', 'stop']" in dele and "'marketing' => ['subscribed' =>" in dele
          and "[400, ['ok' => false, 'error' => 'marketing_choice_required']]" in ad)

    # Email change
    ch = fn(mk, "kpi_v1_marketing_op_email_changed")
    check("email change: never mailed → same row moves (token rotated); mailed → old evidence-only + new subscribed with carried consent",
          all(k in ch for k in ["$new['email'] = (string) $newEmail;", "kpi_v1_marketing_new_token(", "'email_changed'",
                                "'source' => 'email_change'", "'consentAt' => $a['consentAt']"]))
    ap = fn(ec, "kpi_v1_email_change_apply")
    check("email change: marketing moved in the same transaction (MySQL) / undone with the user files (file)",
          in_order(ap, ["UPDATE kpi_users SET email", "kpi_v1_marketing_op_email_changed(", "kpi_v1_session_revoke_bump(", "$pdo->commit();"])
          and "kpi_v1_marketing_file_restore($marketingSnap);" in ap)

    # Missing tables
    run = fn(mk, "kpi_v1_marketing_run")
    check("missing tables = absent (nothing subscribed); other DB errors propagate / fail",
          "'42S02'" in mk and "return ['absent'];" in run and "return ['failed'];" in run)
    check("opt-in with absent storage fails the registration", "return $res[0] === 'ok';" in fn(mk, "kpi_v1_marketing_on_registration"))

    # Token
    check("token = HMAC(secret, nonce); only nonce + sha256(token) stored",
          "hash_hmac('sha256', 'kpn-marketing-unsub|' . $nonce" in mk and "hash('sha256', 'kpn-marketing-unsub-token|'" in mk
          and "random_bytes(16)" in mk and "unsub_token_nonce CHAR(32)" in mig and "unsub_token_hash CHAR(64)" in mig)
    check("secret: config marketingTokenSecret (>= 32) or generated 0600 file under data/marketing",
          "marketingTokenSecret" in mk and "KPI_MARKETING_MIN_SECRET_LENGTH = 32" in mk and "@chmod($tmp, 0600);" in mk)
    check("no error_log with an email / token in marketing code",
          not re.search(r"error_log\([^;]*(\$email|\$token|\$row)", mk + unsub + pref))

    # Unsubscribe endpoint
    check("unsubscribe: POST only, no session, no-store",
          "!== 'POST'" in unsub and "kpi_v1_auth_boot" not in unsub and "no-store" in unsub)
    check("unsubscribe: identical answer whatever the token", unsub.count("kpi_v1_json_out(200, ['ok' => true]);") == 1
          and "matched" not in unsub.split("kpi_v1_json_out(200")[1])
    check("unsubscribe: One-Click form + rate limits (global + per token)",
          "List-Unsubscribe" in unsub and "One-Click" in unsub
          and "kpi_v1_marketing_rate_gate($cfg, 'marketing_unsub_global'" in unsub
          and "kpi_v1_marketing_rate_gate($cfg, 'marketing_unsub_token'" in unsub)
    check("unsubscribe reason stored without email / token / IP", "'reason' => $reason, 'note' => $note" in mk
          and "REMOTE_ADDR" not in fn(mk, "kpi_v1_marketing_record_reason"))

    # Settings / Founder
    check("preference: session user only, expected-user guard, current wording version for subscribe",
          "kpi_v1_auth_current_user_id()" in pref and "kpi_v1_require_expected_user($uid, $body);" in pref
          and "!== KPI_MARKETING_CONSENT_VERSION" in pref)
    check("Founder APIs gated", "kpi_v1_auth_require_founder_superadmin($cfg);" in fl and "kpi_v1_auth_require_founder_superadmin($cfg);" in fa)
    pub = fn(mk, "kpi_v1_marketing_public_row")
    check("Founder rows never carry token material", "token" not in pub.lower())
    check("no send function / mail() in marketing code",
          not re.search(r"(?<![\w])mail\(", mk + unsub + pref + fl + fa) and "kpi_v1_mail_send" not in mk + unsub + pref + fl + fa)

    # Lookup Option B (server side unchanged)
    check("lifecycle lookup: POST body only, never echoed / stored",
          "kpi_v1_auth_require_post();" in lookup and "$_GET" not in lookup and "unset($email, $body);" in lookup
          and "'email'" not in lookup.split("kpi_v1_json_out(200")[1])

    # Segments
    check("segments coded only (listed ISO country / currency, fixed business types, other / null)",
          all(k in lc for k in ["KPI_LIFECYCLE_COUNTRIES", "KPI_LIFECYCLE_CURRENCIES", "KPI_LIFECYCLE_BUSINESS_TYPES", "'other'"]))
    seg = fn(lc, "kpi_v1_lifecycle_segment")
    check("segment reads only country / business type / currency (+ store.meta.businessType)",
          all(k not in seg for k in ["businessName", "companyName", "city", "stateRegion", "genre"]) and "['meta']['businessType']" in seg)
    ins = fn(lc, "kpi_v1_lifecycle_db_insert")
    check("history INSERT carries the three segment columns", all(k in ins for k in ["seg_country", "seg_business_type", "seg_currency"]))
    check("lifecycle readiness requires the segment columns (fail closed)", "seg_country, seg_business_type, seg_currency" in fn(lc, "kpi_v1_lifecycle_ready"))

    # Schema
    for label, sql in (("schema.sql", schema), ("migration", mig)):
        s = table(sql, "kpi_marketing_subscribers")
        e = table(sql, "kpi_marketing_consent_events")
        check(f"{label}: subscribers table unique email + token hash, no FK, no password / ip / ua / hmac / business columns",
              "UNIQUE KEY uq_kpi_marketing_email (normalized_email)" in s and "UNIQUE KEY uq_kpi_marketing_token (unsub_token_hash)" in s
              and "FOREIGN KEY" not in s and not re.search(r"^\s*(password\w*|ip\w*|user_agent|email_hmac|business\w*)\s", s, re.M))
        check(f"{label}: events table append-only shape, no email column, no FK",
              "subscriber_id BIGINT UNSIGNED NOT NULL" in e and "email" not in e and "FOREIGN KEY" not in e)
    check("migration: additive only (CREATE IF NOT EXISTS + ADD COLUMN), no UPDATE / DELETE / DROP outside comments",
          not re.search(r"^\s*(UPDATE|DELETE|DROP|TRUNCATE)\b", mig, re.M | re.I)
          and len(re.findall(r"^\s+ADD COLUMN seg_", mig, re.M)) == 3)
    check("schema.sql: segment columns on kpi_account_deletions",
          all(k in table(schema, "kpi_account_deletions") for k in ["seg_country VARCHAR(8) NULL", "seg_business_type VARCHAR(32) NULL",
                                                                    "seg_currency VARCHAR(8) NULL"]))

    print(f"\n{PASSED} passed, {FAILED} failed")
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
