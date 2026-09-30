"""BR-LAUNCH-09 Extension M6 — Founder Email Updates UI + segment labels (static checks)."""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
results = []


def check(name, ok, detail=""):
    results.append(bool(ok))
    print(("PASS  " if ok else "FAIL  ") + name + ("" if ok else "  :: " + str(detail)[:300]))


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def main():
    mkt = read("admin/marketing/index.php")
    js = read("admin/admin.js")
    dash = read("admin/index.php")
    deleted = read("admin/deleted-accounts/index.php")
    list_api = read("api/v1/admin/marketing-subscribers.php")
    act_api = read("api/v1/admin/marketing-action.php")
    lookup = read("api/v1/admin/lifecycle-lookup.php")
    pub = read("api/v1/_marketing.php")

    check("marketing page: founder page gate", "kpi_v1_admin_require_founder_page($cfg)" in mkt)
    check("marketing page: Email Updates nav + table columns",
          'data-admin-page="marketing"' in mkt and "<th>Email</th>" in mkt and "<th>Status</th>" in mkt
          and "<th>Last Email Sent</th>" in mkt and "<th>Actions</th>" in mkt)
    check("marketing page: no token / hash / secret columns",
          all(x not in mkt[mkt.find("<thead>"):] for x in ("Token", "Hash", "Secret", "Nonce")))
    check("subscribers API: founder gate, GET, purge then list",
          "kpi_v1_auth_require_founder_superadmin($cfg)" in list_api and "!== 'GET'" in list_api
          and list_api.find("kpi_v1_auth_require_founder_superadmin") < list_api.find("kpi_v1_marketing_founder_list"))
    check("action API: founder + POST; unsubscribe | erase only",
          "kpi_v1_auth_require_founder_superadmin($cfg)" in act_api and "kpi_v1_auth_require_post()" in act_api
          and "['unsubscribe', 'erase']" in act_api)
    check("public row: raw email only while subscribed; token / match key no",
          "== 'subscribed') ? (string) $r['email']" in pub
          and "token" not in pub[pub.find("function kpi_v1_marketing_public_row"):pub.find("function kpi_v1_marketing_founder_list")]
          and "matchKey" not in pub[pub.find("function kpi_v1_marketing_public_row"):pub.find("function kpi_v1_marketing_founder_list")])
    check("admin.js: marketing confirms unsubscribe + erase",
          "Unsubscribe " in js and "from email updates" in js and "Permanently erase " in js and "legal hold" in js)
    check("admin.js: marketing actions POST id + action (no token)",
          "'/admin/marketing-action.php'" in js and "action: action" in js)
    check("admin.js: no storage of emails", "localStorage" not in js and "sessionStorage" not in js)
    check("dashboard: Deletions by Segment is a separate section",
          'id="lifecycle-segments-section"' in dash and "Deletions by Segment" in dash
          and dash.find("lifecycle-section") < dash.find("lifecycle-segments-section"))
    check("admin.js: This month vs Retained history not mixed",
          "This month (JST " in js and "Retained history (last 3 years)" in js
          and "segmentTable('country'" in js)
    check("admin.js: Unknown vs Other distinct labels",
          'seg-unknown">Unknown</span>' in js and 'seg-other">Other</span>' in js
          and "pre-M2 history or unavailable" in js and "Value outside the current catalog" in js)
    check("deleted accounts: Country / Business Type / Currency columns",
          "<th>Country</th>" in deleted and "<th>Business Type</th>" in deleted and "<th>Currency</th>" in deleted)
    check("lookup Option B: POST body email, not echoed, not logged",
          "kpi_v1_auth_require_post()" in lookup and "body: { email: entered }" in js
          and "error_log" not in lookup and not re.search(r"json_out\([^;]*\$email", lookup))
    check("lookup: input cleared; Matched lookup in page memory only",
          "input.value = '';" in js and "Matched lookup: " in js)
    check("EN Preferences heading = Email updates", "Email updates :" in read("en/setting/preferences.html"))
    check("EN subscribed copy", "You will now receive email updates from Forge Laboratory." in read("js/kpi-marketing-preference.js"))
    check("JP / ZH-TW headings unchanged (お知らせメール / 通知郵件)",
          "お知らせメール :" in read("setting/preferences.html") and "通知郵件 :" in read("zh-tw/setting/preferences.html"))

    passed = sum(results)
    print("\n%d passed, %d failed" % (passed, len(results) - passed))
    sys.exit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
