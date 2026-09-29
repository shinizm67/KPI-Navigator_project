"""BR-LAUNCH-09 Extension M5 — lifecycle segment breakdown contract (static checks).

Deletions by country / business type / currency from history rows only, next to (not inside) the lifecycle
metrics; NULL = unknown (never inferred), unlisted = other; same population as `deleted`; 3-year window.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
results = []


def check(name, ok, detail=""):
    results.append(bool(ok))
    print(("PASS  " if ok else "FAIL  ") + name + ("" if ok else "  :: " + str(detail)[:300]))


def body_of(src, fn):
    i = src.find("function " + fn + "(")
    if i < 0:
        return ""
    j = src.find("\n}\n", i)
    return src[i:j]


def main():
    adm = (ROOT / "api/v1/_lifecycle_admin.php").read_text(encoding="utf-8")
    dash = (ROOT / "api/v1/admin/dashboard.php").read_text(encoding="utf-8")
    bucket = body_of(adm, "kpi_v1_lifecycle_segment_bucket")
    comp = body_of(adm, "kpi_v1_lifecycle_segments_compute")
    metrics = body_of(adm, "kpi_v1_lifecycle_metrics_compute")

    check("bucket: null / empty -> unknown", "if ($value === null) {\n        return 'unknown';" in bucket
          and "if ($s === '') {\n        return 'unknown';" in bucket)
    check("bucket: listed code kept, anything else -> other (no inference)",
          "in_array($s, $catalog, true) ? $s : 'other'" in bucket and "LEGACY" not in bucket and "strto" not in bucket)
    check("dimensions use the snapshot catalogs",
          "['segCountry', KPI_LIFECYCLE_COUNTRIES]" in comp and "['segBusinessType', KPI_LIFECYCLE_BUSINESS_TYPES]" in comp
          and "['segCurrency', KPI_LIFECYCLE_CURRENCIES]" in comp)
    check("population = metrics `deleted`: excluded + child skipped, invalid dates skipped",
          "!empty($r['excludeFromMetrics'])" in comp and "=== 'child'" in comp and "$c === null || $d === null" in comp)
    check("month scope in JST, churned vs earlyChurn split like the metrics",
          "kpi_v1_lifecycle_jst()" in comp and "$kind = $c < $s ? 'churned' : 'earlyChurn';" in comp)
    check("retained scope limited to the 3-year retention window",
          "strtotime(KPI_LIFECYCLE_RETENTION, $now)" in comp and "$d >= $windowStart && $d <= $now" in comp)
    check("history rows only: no users / origins / profile / email read",
          all(x not in comp for x in ("kpi_v1_admin_list_users", "origins", "profile", "email", "Hmac", "previousUserId", "lifecycleId")))
    check("metrics compute untouched by segments", "seg" not in metrics.lower())
    check("dashboard: separate key next to lifecycle", "$stats['lifecycle'] = kpi_v1_lifecycle_metrics($cfg, $month);" in dash
          and "$stats['lifecycleSegments'] = kpi_v1_lifecycle_segments($cfg, $month);" in dash)
    check("dashboard: Founder Super Admin gate + purge before reading",
          "kpi_v1_auth_require_founder_superadmin($cfg);" in dash and dash.find("kpi_v1_lifecycle_purge") < dash.find("lifecycleSegments'] ="))
    check("storage unavailable -> null", "return $rows === null ? null : kpi_v1_lifecycle_segments_compute($rows, $month);" in adm)

    passed = sum(results)
    print("\n%d passed, %d failed" % (passed, len(results) - passed))
    sys.exit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
