# -*- coding: utf-8 -*-
"""BR-LAUNCH-05 Registration launch contract — static checks (consent, status, abuse, cache, zh-tw generator)."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAILED = 0
PASSED = 0

MONTHS = {m: i for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}
REG_PAGES = [
    "register/registration_si-fi_jp/registration_si-fi_jp.html",
    "en/register/registration_si-fi_en.html",
    "zh-tw/register/registration_si-fi_zh-tw.html",
]
REG_SCRIPTS = ["register/script.js", "en/register/script.js", "zh-tw/register/script.js"]


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


def legal_date(rel: str) -> str | None:
    t = read(rel)
    m = re.search(r'class="terms-meta">(?:最終更新日|最後更新)：(\d{4})年(\d{1,2})月(\d{1,2})日', t)
    if m:
        return "%s-%02d-%02d" % (m.group(1), int(m.group(2)), int(m.group(3)))
    m = re.search(r'class="terms-meta">Last updated: (\d{1,2}) ([A-Z][a-z]{2}) (\d{4})', t)
    if m:
        return "%s-%02d-%02d" % (m.group(3), MONTHS[m.group(2)], int(m.group(1)))
    return None


def main() -> None:
    helper = read("api/v1/_registration.php")
    reg = read("api/v1/auth/register.php")
    status = read("api/v1/auth/registration-status.php")
    admin = read("api/v1/auth/admin-create-user.php")
    login = read("api/v1/auth/login.php")

    # Consent versions = legal "Last updated" (all languages)
    tv = re.search(r"const KPI_TERMS_VERSION = '([^']+)';", helper)
    pv = re.search(r"const KPI_PRIVACY_VERSION = '([^']+)';", helper)
    check("canonical TERMS / PRIVACY version constants", tv is not None and pv is not None)
    for rel in ["legal/terms/index.html", "en/legal/terms/index.html", "zh-tw/legal/terms/index.html"]:
        d = legal_date(rel)
        check(f"{rel} Last updated == KPI_TERMS_VERSION", tv is not None and d == tv.group(1), f"{d} vs {tv and tv.group(1)}")
    for rel in ["legal/privacy/index.html", "en/legal/privacy/index.html", "zh-tw/legal/privacy/index.html"]:
        d = legal_date(rel)
        check(f"{rel} Last updated == KPI_PRIVACY_VERSION", pv is not None and d == pv.group(1), f"{d} vs {pv and pv.group(1)}")

    # Consent storage: append-only, created with the user
    mig = read("api/v1/schema_kpi_user_consents.add.sql")
    schema = read("api/v1/schema.sql")
    for col in ["id BIGINT", "user_id", "terms_version", "privacy_version", "accepted_at", "source"]:
        check(f"consent migration has {col}", col in mig)
    check("schema.sql includes kpi_user_consents", "CREATE TABLE IF NOT EXISTS kpi_user_consents" in schema)
    mig_sql = "\n".join(l for l in mig.splitlines() if not l.strip().startswith("--"))
    stmts = [s.strip() for s in mig_sql.split(";") if s.strip()]
    check("consent migration: exactly one statement, CREATE TABLE IF NOT EXISTS kpi_user_consents",
          len(stmts) == 1 and stmts[0].startswith("CREATE TABLE IF NOT EXISTS kpi_user_consents ("), stmts[:2])
    check("consent migration: no DROP / ALTER / DELETE / UPDATE / TRUNCATE / INSERT / RENAME / GRANT outside comments",
          re.search(r"\b(DROP|ALTER|DELETE|UPDATE|TRUNCATE|INSERT|RENAME|GRANT|REPLACE)\b",
                    re.sub(r"ON\s+DELETE\s+CASCADE", "", mig_sql, flags=re.I), re.I) is None)
    check("consent migration: only references kpi_users (FK), never modifies it",
          re.findall(r"\bkpi_\w+", mig_sql) == ["kpi_user_consents", "kpi_users"])
    api_php = "\n".join(p.read_text(encoding="utf-8") for p in (ROOT / "api").rglob("*.php"))
    check("no UPDATE / DELETE on kpi_user_consents anywhere in api/",
          re.search(r"(UPDATE|DELETE\s+FROM)\s+kpi_user_consents", api_php, re.I) is None)
    check("MySQL: user + consent (+ optional marketing opt-in) in one transaction",
          re.search(r"beginTransaction\(\);\s*kpi_v1_registration_db_insert_user\(\$pdo, \$user\);\s*"
                    r"kpi_v1_consent_db_insert\(\$pdo, \$user\['userId'\], \$consent\);\s*"
                    r"if \(\$alsoWrite !== null && \$alsoWrite\(\$pdo\) !== true\) \{\s*\$pdo->rollBack\(\);\s*return 'failed';\s*\}\s*"
                    r"\$pdo->commit\(\);", helper) is not None)
    check("MySQL: rollBack on failure", helper.count("$pdo->rollBack();") >= 2)
    check("file: compensating delete when consent / index write fails", helper.count("@unlink($userPath);") >= 2)
    check("register creates via create_user_with_consent (not a bare write_user)",
          "kpi_v1_registration_create_user_with_consent(" in reg and "kpi_v1_auth_write_user(" not in reg)

    # Server-side checks and order
    order = [reg.find(s) for s in [
        "kpi_v1_registration_enabled($cfg)", "kpi_v1_registration_has_forwarded_ip_header()",
        "kpi_v1_registration_rate_gate($cfg, 'global_attempt'", "kpi_v1_registration_rate_gate($cfg, 'ip'",
        "kpi_v1_registration_bot_reason(", "kpi_v1_registration_rate_gate($cfg, 'email'", "kpi_v1_registration_password_ok(",
        "kpi_v1_registration_consent_from_body(", "isset($index[$email])", "kpi_v1_registration_rate_gate($cfg, 'global_create_day'",
        "kpi_v1_registration_rate_gate($cfg, 'global_create_hour'", "kpi_v1_registration_create_user_with_consent(",
        "kpi_v1_auth_set_session_user("]]
    check("register order: gate -> forwarded header reject -> global attempt -> IP (auxiliary) -> bot -> email limit -> "
          "password -> consent -> duplicate -> global create day / hour -> create -> session",
          all(x >= 0 for x in order) and order == sorted(order), str(order))
    check("forwarded header reject = CF-Connecting-IP / X-Real-IP only, answered as generic registration_rejected",
          "isset($_SERVER['HTTP_CF_CONNECTING_IP']) || isset($_SERVER['HTTP_X_REAL_IP'])" in helper
          and re.search(r"has_forwarded_ip_header\(\)\) \{\s*kpi_v1_json_out\(400, \['ok' => false, 'error' => 'registration_rejected'\]\);", reg)
          is not None)
    check("global limiter defaults: attempts 30 / 10 min, creations 10 / h and 40 / 24 h",
          "'registrationGlobalAttemptMax', 30," in helper and "'registrationGlobalAttemptWindowSeconds', 600," in helper
          and re.search(r"'registrationGlobalCreateHourMax', 10, 1, 10000\),\s*3600,", helper) is not None
          and re.search(r"'registrationGlobalCreateDayMax', 40, 1, 10000\),\s*86400,", helper) is not None)
    check("rate gate fails closed: storage unavailable -> 503, full -> 429 rate_limited",
          re.search(r"if \(\$allowed === null\) \{\s*kpi_v1_json_out\(503, \['ok' => false, 'error' => 'registration_unavailable'\]\);",
                    helper) is not None and "kpi_v1_json_out(429, ['ok' => false, 'error' => 'rate_limited']);" in helper)
    check("no forwarded header is trusted as the client IP",
          not re.search(r"HTTP_(X_FORWARDED_FOR|CF_CONNECTING_IP|X_REAL_IP|TRUE_CLIENT_IP|CLIENT_IP|FORWARDED)'\]\)\s*\?", helper))
    check("consentAccepted must be boolean true", "$body['consentAccepted'] !== true" in helper)
    check("stale version -> consent_outdated", "'consent_outdated'" in helper)
    check("public registration plan fixed to basic", "'plan' => 'basic'," in reg and "default_plan" not in reg)
    check("rate limit counters live under data/ (no new infra)", "/data/registration" in helper and "redis" not in helper.lower())
    check("rate limit keys: REMOTE_ADDR only (no spoofable forwarded headers)",
          "REMOTE_ADDR" in helper and "HTTP_X_FORWARDED_FOR" not in helper)
    check("no CAPTCHA", "captcha" not in (helper + reg).lower())
    check("error codes only; no exception text returned",
          "getMessage()" not in helper + reg and "errorInfo[2]" not in helper + reg)
    check("login / admin-create untouched by public password rule",
          "kpi_v1_registration_password_ok" not in login + admin and "_registration.php" not in login + admin)

    # Status endpoint
    check("status: GET only, no-store, no session",
          "'GET'" in status and "no-store" in status and "session_start" not in status and "kpi_v1_auth_boot" not in status)
    check("status: formToken only when enabled; fail closed if token cannot be issued",
          "if ($enabled)" in helper and "$out['registrationEnabled'] = false;" in helper)

    # Pages / scripts
    for rel in REG_PAGES:
        t = read(rel)
        check(f"{rel}: static notice + hidden form by default (fail closed without JS / status)",
              "registration-disabled-notice" in t and 'hidden aria-hidden="true"' in t)
        check(f"{rel}: honeypot off-screen, tabindex -1, autocomplete off, aria-hidden",
              re.search(r'aria-hidden="true" style="position:absolute;left:-10000px;[^"]*">\s*<label for="reg-extra-note">', t) is not None
              and 'id="reg-extra-note" name="extra_note" value="" tabindex="-1" autocomplete="off"' in t)
        check(f"{rel}: no Name / Company / Business Type", 'id="name"' not in t and 'id="company"' not in t and 'id="business-type"' not in t)
    for rel in REG_SCRIPTS:
        t = read(rel)
        check(f"{rel}: opens only on status GET === true with versions + token",
              "d.registrationEnabled === true" in t and "d.formToken" in t and "registrationStatus()" in t)
        check(f"{rel}: button also requires registrationOpen", "!(registrationOpen && emailOk" in t)
        check(f"{rel}: sends consent + versions + token + honeypot",
              all(k in t for k in ["consentAccepted:", "termsVersion: registrationStatus.termsVersion",
                                   "privacyVersion: registrationStatus.privacyVersion", "formToken: registrationStatus.formToken", "extraNote:"]))
        check(f"{rel}: no plan in payload / no ?plan= use", "plan:" not in t and "get('plan')" not in t)

    # Cache safety
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "stamp_registration_assets.py"), "--check"],
                       capture_output=True, text=True)
    check("Registration script URLs carry the current content hash (?v=)", r.returncode == 0, r.stdout + r.stderr)

    # zh-tw generator keeps Registration contract
    gen = read("scripts/build_zh_tw_public_pages.py")
    for s in ["目前暫停接受新註冊", "前往登入", "搶先體驗／聯絡我們", "請勿填寫此欄位",
              "errorMessage('zh',", 'newline="\\n"', "stamp_registration_assets.stamp_page(zh_page)"]:
        check(f"zh-tw generator keeps: {s}", s in gen)
    check("zh-tw generator fails loudly when EN source drifts", "EN source changed, missing" in gen)
    for rel, reg in [("plan/index.html", "../register/registration_si-fi_jp/registration_si-fi_jp.html"),
                     ("en/plan/index.html", "../register/registration_si-fi_en.html"),
                     ("zh-tw/plan/index.html", "../register/registration_si-fi_zh-tw.html")]:
        t = read(rel)
        m = re.search(r'<a href="([^"]+)" class="btn-register" id="plan-basic-cta" data-register-href="([^"]+)"', t)
        check(f"{rel}: Basic CTA defaults to Early Access mailto, switches only to same-language Registration",
              m is not None and m.group(1).startswith("mailto:") and m.group(2) == reg and "kpi-plan-cta.js?v=" in t)
    cta = read("js/kpi-plan-cta.js")
    check("kpi-plan-cta.js opens only on registrationEnabled === true + versions + formToken (same as Registration)",
          "d.registrationEnabled !== true" in cta and "typeof d.formToken !== 'string'" in cta and ".catch(function () {})" in cta)
    zh_js = read("zh-tw/register/script.js")
    check("zh-tw register: success message in Traditional Chinese", "alert('註冊完成，將前往登入頁面。');" in zh_js
          and "Registration complete. Proceeding to login." not in zh_js)
    check("zh-tw register: urlZhTw declared once", zh_js.count("var urlZhTw =") == 1)

    print(f"\n{PASSED} passed, {FAILED} failed")
    raise SystemExit(1 if FAILED else 0)


if __name__ == "__main__":
    main()
