# -*- coding: utf-8 -*-
"""BR-LAUNCH-09 Phase 3A Extension L3 — Founder lifecycle UI contract (static checks).

Founder-only endpoints, no raw email / HMAC in responses or logs, frozen churn definition (JST, role user, child and
exclude_from_metrics excluded, same-month early churn), Deleted Accounts page, Users Origin / exclude column."""
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


ENDPOINTS = {
    "api/v1/admin/deleted-accounts.php": "GET",
    "api/v1/admin/lifecycle-lookup.php": "POST",
    "api/v1/admin/lifecycle-erase.php": "POST",
    "api/v1/admin/set-metrics-exclusion.php": "POST",
    "api/v1/admin/dashboard.php": "GET",
    "api/v1/admin/users.php": "GET",
}
PAGES = ["admin/index.php", "admin/users/index.php", "admin/users/detail/index.php", "admin/deleted-accounts/index.php"]


def main() -> int:
    la = read("api/v1/_lifecycle_admin.php")
    js = read("admin/admin.js")

    for rel, method in ENDPOINTS.items():
        src = read(rel)
        gate = src.find("kpi_v1_auth_require_founder_superadmin($cfg)")
        body = src.find("kpi_v1_auth_read_json_body()")
        work = min(i for i in (src.find("kpi_v1_lifecycle_", gate + 1), src.find("kpi_v1_admin_", gate + 1)) if i > 0)
        check(f"{rel}: founder gate before any work", gate > 0 and (body < 0 or gate < body) and gate < work)
        if method == "POST":
            check(f"{rel}: POST only", "kpi_v1_auth_require_post()" in src)
        else:
            check(f"{rel}: GET only", "!== 'GET'" in src)
    lookup = read("api/v1/admin/lifecycle-lookup.php")
    check("lookup: never logs / stores the email", "error_log" not in lookup and "file_put_contents" not in lookup
          and "INSERT" not in lookup and "UPDATE" not in lookup)
    check("lookup: response does not echo the email", not re.search(r"json_out\([^;]*\$email", lookup))
    check("lookup: fail closed without key", "lifecycle_key_missing" in lookup and "kpi_v1_lifecycle_all_keys($cfg) === []" in lookup)
    check("lookup: matches under every configured key", "kpi_v1_lifecycle_email_hmacs($cfg, $email)" in fn(la, "kpi_v1_lifecycle_lookup"))
    pub = fn(la, "kpi_v1_lifecycle_public_row")
    check("public row: no HMAC / key id / email", "emailHmac" not in pub and "hmacKeyId" not in pub and "email'" not in pub)
    for rel in ("api/v1/admin/deleted-accounts.php", "api/v1/admin/lifecycle-lookup.php"):
        check(f"{rel}: rows mapped through public_row", "array_map('kpi_v1_lifecycle_public_row'" in read(rel))
    check("list + dashboard run the 3-year purge", all("kpi_v1_lifecycle_purge($cfg)" in read(r)
                                                       for r in ("api/v1/admin/deleted-accounts.php", "api/v1/admin/dashboard.php")))
    erase = fn(la, "kpi_v1_lifecycle_erase")
    check("erase: one row by lifecycle id, clears returned links, never touches kpi_users",
          "DELETE FROM kpi_account_deletions WHERE id = ?" in erase and "matched_deletion_id = NULL" in erase
          and "kpi_users" not in erase and "matchedLifecycleId'] = null" in erase)
    check("erase endpoint validates lc_ id", "/^lc_[a-f0-9]{24}$/" in read("api/v1/admin/lifecycle-erase.php"))
    acc = fn(la, "kpi_v1_lifecycle_set_account_exclusion")
    check("account exclusion: upsert origin row, legacy when absent",
          "ON DUPLICATE KEY UPDATE exclude_from_metrics" in acc and "'legacy'" in acc and "'origin' => 'legacy'" in acc)
    check("exclusion endpoint requires boolean + exactly one target",
          "is_bool($body['exclude'])" in read("api/v1/admin/set-metrics-exclusion.php") and "invalid_target" in read("api/v1/admin/set-metrics-exclusion.php"))

    mc = fn(la, "kpi_v1_lifecycle_metrics_compute")
    check("churn: JST month boundaries", "kpi_v1_lifecycle_jst()" in mc and "'Asia/Tokyo'" in fn(la, "kpi_v1_lifecycle_jst"))
    check("churn: role user only, child excluded", "!== 'user' || !empty($u['parentUserId'])" in mc and "=== 'child'" in mc)
    check("churn: exclude_from_metrics removed on both sides", mc.count("excludeFromMetrics") >= 2)
    check("churn: disabled kept in the denominator (counted, not skipped)",
          "$activeDisabled++" in mc and not re.search(r"disabled'\]\)\)\s*\{\s*continue", mc))
    check("churn: denominator = existing at month start", "$c < $s && $d >= $s" in mc and "if ($c < $s) {\n            $denominator++" in mc)
    check("churn: numerator = deleted in month, created before start; else early churn",
          "$inMonth = $d >= $s && $d < $e" in mc and "$numerator++" in mc and "$early++" in mc)
    check("churn: rate = numerator / denominator x 100, null when 0", "$numerator / $denominator * 100" in mc and "$denominator > 0" in mc)
    check("metrics: config-listed founders excluded", "kpi_v1_auth_is_founder_superadmin($u, $cfg)" in fn(la, "kpi_v1_lifecycle_metrics"))
    check("users.php: origin + exclude flag", "'signupOrigin' => $origin['origin']" in read("api/v1/admin/users.php")
          and "'excludeFromMetrics' => $origin['excludeFromMetrics']" in read("api/v1/admin/users.php"))

    for rel in PAGES:
        src = read(rel)
        check(f"{rel}: founder page gate", "kpi_v1_admin_require_founder_page($cfg)" in src)
        check(f"{rel}: nav has Deleted Accounts", "Deleted Accounts</a>" in src)
        check(f"{rel}: admin.js / admin.css versioned", "admin.js?v=" in src and "admin.css?v=" in src)
    dp = read("admin/deleted-accounts/index.php")
    for col in ("Previous User ID", "Created", "Deleted", "Lifetime", "Plan at Deletion", "Origin", "Cleanup Status", "Returned",
                "Return Count", "Exclude from Metrics", "Actions"):
        check(f"deleted page column {col}", f"<th>{col}</th>" in dp)
    check("deleted page: lookup input not autocompleted", 'autocomplete="off"' in dp)
    check("deleted page: data-admin-page=deleted", 'data-admin-page="deleted"' in dp)
    up = read("admin/users/index.php")
    check("users page: Origin + Exclude columns", "<th>Origin</th>" in up and "<th>Exclude from Metrics</th>" in up)
    for label in ("'Active'", "'New'", "'Deleted'", "'Monthly Churn'", "'Returned'", "'Early Churn'", "'Child Deletions'", "'Disabled'"):
        check(f"dashboard card {label}", "card(" + label in js)
    check("admin.js: history delete confirms", "window.confirm('Permanently delete the history row" in js)
    check("admin.js: lookup clears the input", "input.value = '';" in js)
    check("admin.js: no email written to storage", "localStorage" not in js and "sessionStorage" not in js)
    check("admin.js: origin labels NEW / RETURNED / UNKNOWN", all(x in js for x in ("'NEW'", "RETURNED</span>", "UNKNOWN</span>")))

    print(f"\n{PASSED} passed, {FAILED} failed")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
