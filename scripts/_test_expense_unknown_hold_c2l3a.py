# -*- coding: utf-8 -*-
"""C2-L3-A: unknown expense hold (catalog-outside). Twin of js/kpi-expense-unknown-hold.js."""

from __future__ import annotations

import copy
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from pl_line_catalog import expense_detail_default_catalog  # noqa: E402

import _test_expense_csv_import_6c as u6c  # noqa: E402

FAILED = 0
PASSED = 0

HOLD_JS = (ROOT / "js" / "kpi-expense-unknown-hold.js").read_text(encoding="utf-8")
GATEWAY_JS = (ROOT / "js" / "kpi-data-gateway.js").read_text(encoding="utf-8")
AUTH_JS = (ROOT / "js" / "kpi-auth-client.js").read_text(encoding="utf-8")
PL_PY = (SCRIPTS / "pl_expense_import_client.py").read_text(encoding="utf-8")
RESET_PHP = (ROOT / "api" / "v1" / "_admin_reset_kpi.php").read_text(encoding="utf-8")
SALES_PARSER = (SCRIPTS / "daily_sales_import_client.py").read_text(encoding="utf-8")
HOLD_KEY = "kpiNavigator.plExpenseUnknownHold"

PL_PAGES = u6c.PL_PAGES
MEP_PAGES = u6c.MEP_PAGES


def assert_true(cond: bool, msg: str) -> None:
    global PASSED, FAILED
    if cond:
        PASSED += 1
        return
    FAILED += 1
    print("FAIL:", msg)


def fnv1a32_hex(text: str) -> str:
    h = 2166136261
    for ch in text:
        h ^= ord(ch)
        h = (h * 16777619) & 0xFFFFFFFF
    return f"{h:08x}"


def unknown_id_for(normalized: str) -> str:
    return "unk_" + fnv1a32_hex(normalized)


def merge_value(existing_has, existing, incoming, policy):
    if policy == "add":
        return int(round((existing or 0) + incoming))
    if policy == "skip":
        return existing if existing_has else int(round(incoming))
    return int(round(incoming))


def ingest_unmatched(blob, unmatched, policy="replace", meta=None):
    records = copy.deepcopy(blob.get("records") or {})
    meta = meta or {}
    for norm_key, info in (unmatched or {}).items():
        normalized = u6c.norm_text(info.get("display") or info.get("originalLabel") or norm_key)
        if not normalized:
            continue
        uid = unknown_id_for(normalized)
        n = 2
        while uid in records and str(records[uid].get("normalizedLabel") or "") != normalized:
            uid = f"{unknown_id_for(normalized)}_{n}"
            n += 1
        rec = records.get(uid) or {
            "unknownId": uid,
            "originalLabel": str(info.get("display") or info.get("originalLabel") or norm_key),
            "normalizedLabel": normalized,
            "status": "unknown",
            "rows": [],
        }
        existing = {row["period"]: row["amount"] for row in rec.get("rows") or []}
        incoming_map = dict(info.get("rowsByPeriod") or {})
        for period, amount in incoming_map.items():
            has = period in existing
            existing[period] = merge_value(has, existing.get(period), amount, policy)
        rec["rows"] = [{"period": k, "amount": existing[k]} for k in sorted(existing)]
        rec["status"] = "unknown"
        rec["normalizedLabel"] = normalized
        if meta.get("importBatchId"):
            rec["lastImportBatchId"] = meta["importBatchId"]
        if meta.get("importedAt") is not None:
            rec["lastImportedAt"] = meta["importedAt"]
        if meta.get("sourceFilename"):
            rec["sourceFilename"] = meta["sourceFilename"]
        records[uid] = rec
    return {"schemaVersion": 1, "records": records}


def pl_unmatched_from_rows(rows, lines, aliases=None, business_type=None):
    cols = u6c.detect_columns(rows)
    resolve = u6c.make_resolver(lines, aliases, business_type=business_type)
    unmatched = {}
    known_monthly = {}
    start = cols["start"]
    for row in rows[start:]:
        date = u6c.norm_date(row[cols["dateCol"]] if cols["dateCol"] < len(row) else "")
        item = str(row[cols["itemCol"]] if cols["itemCol"] < len(row) else "").strip()
        amount = u6c.parse_amount(row[cols["amtCol"]] if cols["amtCol"] < len(row) else "")
        if not date or not item or u6c.is_header_item(item):
            continue
        line = resolve(item)
        if not line:
            k = u6c.norm_text(item)
            if k not in unmatched:
                unmatched[k] = {
                    "display": item,
                    "count": 0,
                    "hasDaily": False,
                    "hasMonthly": False,
                    "rowsByPeriod": {},
                }
            unmatched[k]["count"] += 1
            if len(date) == 10:
                unmatched[k]["hasDaily"] = True
            else:
                unmatched[k]["hasMonthly"] = True
            unmatched[k]["rowsByPeriod"][date] = unmatched[k]["rowsByPeriod"].get(date, 0) + amount
            continue
        style = line.get("resolvedInputStyle") or line.get("inputStyle") or "monthly"
        if style != "daily":
            year = int(date[:4])
            month0 = int(date[5:7]) - 1
            known_monthly.setdefault(year, {})
            key = f"{line['lineId']}:{month0}"
            known_monthly[year][key] = known_monthly[year].get(key, 0) + amount
    return unmatched, known_monthly


def restaurant_catalog():
    return expense_detail_default_catalog("restaurant")


def test_pl_unknown_preserves_label_amount_date() -> None:
    catalog = restaurant_catalog()
    rows = [
        ["日付", "費目", "金額"],
        ["2026-04", "予約サイト利用料", "32000"],
        ["2026-04-10", "BGM使用料", "5000"],
        ["2026-05", "害虫駆除費", "12000"],
    ]
    unmatched, known = pl_unmatched_from_rows(rows, catalog, business_type="restaurant")
    assert_true("予約サイト利用料" in unmatched, "PL unknown originalLabel key")
    assert_true(unmatched["予約サイト利用料"]["display"] == "予約サイト利用料", "PL originalLabel preserved")
    assert_true(unmatched["予約サイト利用料"]["rowsByPeriod"]["2026-04"] == 32000, "PL amount preserved")
    assert_true(unmatched["bgm使用料"]["rowsByPeriod"]["2026-04-10"] == 5000, "PL daily date preserved")
    assert_true(unmatched["害虫駆除費"]["rowsByPeriod"]["2026-05"] == 12000, "PL month/year preserved")
    blob = ingest_unmatched({"schemaVersion": 1, "records": {}}, unmatched, meta={"sourceFilename": "x.csv", "importBatchId": "imp_1", "importedAt": 1})
    rec = next(iter(blob["records"].values()))
    assert_true(rec["originalLabel"] == "予約サイト利用料" or "予約サイト利用料" in [r["originalLabel"] for r in blob["records"].values()], "hold originalLabel")
    bgm_id = unknown_id_for("bgm使用料")
    assert_true(blob["records"][bgm_id]["rows"][0]["period"] == "2026-04-10", "hold keeps date")
    assert_true(not known, "unknowns do not write canonical amounts")
    assert_true("bucket" not in blob["records"][bgm_id], "hold has no bucket")
    assert_true("inputStyle" not in blob["records"][bgm_id], "hold has no inputStyle")


def test_pl_skip_still_preserves_hold() -> None:
    catalog = restaurant_catalog()
    rows = [["日付", "費目", "金額"], ["2026-04", "予約サイト利用料", "32000"]]
    unmatched, known = pl_unmatched_from_rows(rows, catalog, business_type="restaurant")
    blob = ingest_unmatched({"schemaVersion": 1, "records": {}}, unmatched, policy="replace")
    assert_true(len(blob["records"]) == 1, "skip-all still creates hold")
    assert_true(not known, "canonical skip writes nothing")
    assert_true("persistUnmatchedFromPlan(plan, policy, meta || {});" in PL_PY, "PL persist helper exists")
    no_write_block = PL_PY.split("if (!hasWrites)", 1)[1].split("var conflicts", 1)[0]
    assert_true("persistUnmatchedFromPlan" in no_write_block, "PL skip/no-writes still persist hold")


def test_mep_unknown_hold_not_table() -> None:
    catalog = restaurant_catalog()
    rows = [["日付", "費目", "金額"], ["2026-04", "予約サイト利用料", "32000"], ["2026-04", "exp_rent", "100000"]]
    unmatched, known = pl_unmatched_from_rows(rows, catalog, business_type="restaurant")
    hold_rows = []
    for info in unmatched.values():
        for period, amount in info["rowsByPeriod"].items():
            hold_rows.append({"originalLabel": info["display"], "period": period, "amount": amount})
    blob = ingest_unmatched({"schemaVersion": 1, "records": {}}, unmatched, policy="replace")
    assert_true(len(hold_rows) == 1, "MEP unknown collected")
    assert_true("exp_rent:3" in known.get(2026, {}), "known rent still canonical")
    assert_true(all(not lid.startswith("unk_") for lid in known.get(2026, {})), "hold ids not in MEP amounts")
    rec = blob["records"][unknown_id_for("予約サイト利用料")]
    assert_true(rec["rows"][0]["amount"] == 32000, "MEP unknown amount in hold")
    for path in MEP_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        assert_true("unknownHoldRows.push" in html, f"{rel} MEP sends unknown to hold")
        skip_block = html.split("unknownHoldRows.push", 1)[1].split("continue;", 1)[0]
        assert_true("rowValueById" not in skip_block, f"{rel} unknown not written to MEP cells")
        assert_true("ingestRawRows" in html, f"{rel} MEP ingestRawRows")
        assert_true("state.fixedItems" in html and "state.variableItems" in html, f"{rel} MEP sections unchanged")


def test_stable_id_and_merge() -> None:
    unmatched = {
        "予約サイト利用料": {
            "display": "予約サイト利用料",
            "rowsByPeriod": {"2026-04": 32000},
        }
    }
    blob = ingest_unmatched({"schemaVersion": 1, "records": {}}, unmatched)
    uid = unknown_id_for("予約サイト利用料")
    assert_true(uid == "unk_" + fnv1a32_hex("予約サイト利用料"), "deterministic unknownId")
    assert_true(not uid.startswith("exp_"), "unknownId is not exp_*")
    assert_true("exp_custom_" not in uid, "unknownId is not exp_custom_*")
    blob2 = ingest_unmatched(blob, unmatched, policy="replace")
    assert_true(len(blob2["records"]) == 1, "reimport does not duplicate unknownId")
    assert_true(blob2["records"][uid]["rows"][0]["amount"] == 32000, "replace overwrites same period")
    added = ingest_unmatched(
        {"schemaVersion": 1, "records": {uid: {"unknownId": uid, "originalLabel": "予約サイト利用料", "normalizedLabel": "予約サイト利用料", "status": "unknown", "rows": [{"period": "2026-04", "amount": 32000}]}}},
        unmatched,
        policy="add",
    )
    assert_true(added["records"][uid]["rows"][0]["amount"] == 64000, "add policy matches expense import")
    skipped = ingest_unmatched(
        {"schemaVersion": 1, "records": {uid: {"unknownId": uid, "originalLabel": "予約サイト利用料", "normalizedLabel": "予約サイト利用料", "status": "unknown", "rows": [{"period": "2026-04", "amount": 32000}]}}},
        unmatched,
        policy="skip",
    )
    assert_true(skipped["records"][uid]["rows"][0]["amount"] == 32000, "skip policy keeps existing")
    spaced = {
        "予約サイト利用料": {
            "display": "予約サイト 利用料",
            "rowsByPeriod": {"2026-05": 1},
        }
    }
    # display normalizes to same key only if caller uses norm_text of display
    spaced_norm = {u6c.norm_text("予約サイト 利用料"): spaced["予約サイト利用料"]}
    blob5 = ingest_unmatched(skipped, spaced_norm, policy="replace")
    assert_true(len(blob5["records"]) == 1, "whitespace-normalized label shares unknownId")


def test_known_and_synonym_not_held() -> None:
    catalog = restaurant_catalog()
    rows = [
        ["日付", "費目", "金額"],
        ["2026-01", "店舗家賃", "100"],
        ["2026-01", "食材費", "200"],
        ["2026-01", "exp_rent", "300"],
        ["2026-01", "予約サイト利用料", "9"],
    ]
    unmatched, known = pl_unmatched_from_rows(rows, catalog, business_type="restaurant")
    assert_true("予約サイト利用料" in unmatched, "true unknown is held")
    assert_true("店舗家賃" not in unmatched and "食材費" not in unmatched, "C2-L2 synonyms not held")
    assert_true("exp_rent:0" in known[2026], "known/synonym write canonical")
    machine = [
        ["日付", "費目", "金額"],
        ["2026-03", "exp_unknown_zzzz", "謎", "100"],
    ]
    # 3-col detect: item is 費目
    machine = [["日付", "費目", "金額"], ["2026-03", "exp_unknown_zzzz", "100"]]
    unmatched_m, known_m = pl_unmatched_from_rows(machine, catalog, business_type="restaurant")
    assert_true("exp_unknown_zzzz" in unmatched_m, "machine exp_* unknown stays unmatched")
    assert_true(not known_m, "unknown machine key does not write canonical")
    assert_true(u6c.looks_like_line_id("exp_unknown_zzzz"), "machine key contract kept")


def test_orphan_inactive_rules() -> None:
    catalog = restaurant_catalog()
    catalog = [dict(row) for row in catalog]
    for row in catalog:
        if row.get("lineId") == "exp_advertising":
            row["active"] = False
        if row.get("lineId") == "exp_utilities":
            row["presetOrphan"] = True
    rows = [
        ["日付", "費目", "金額"],
        ["2026-01", "exp_advertising", "10"],
        ["2026-01", "exp_utilities", "20"],
        ["2026-01", "exp_rent", "30"],
    ]
    unmatched, known = pl_unmatched_from_rows(rows, catalog, business_type="restaurant")
    assert_true("exp_advertising" in unmatched, "inactive stays unmatched")
    assert_true("exp_utilities" in unmatched, "presetOrphan stays unmatched")
    assert_true(known[2026]["exp_rent:0"] == 30, "active canonical still imports")


def test_gateway_auth_reset_wiring() -> None:
    assert_true("PL_UNKNOWN_HOLD_KEY" in GATEWAY_JS, "gateway has hold key")
    assert_true("unknownHold: localGet(PL_UNKNOWN_HOLD_KEY)" in GATEWAY_JS, "collectPlFromLocal includes hold")
    assert_true("hasOwnProperty.call(pl, 'unknownHold')" in GATEWAY_JS, "applyPlToLocal round-trips hold")
    assert_true("key === PL_UNKNOWN_HOLD_KEY" in GATEWAY_JS, "isPlSyncKey includes hold")
    assert_true("localRemoveRaw(PL_UNKNOWN_HOLD_KEY)" in GATEWAY_JS, "user-scope reset clears hold")
    assert_true("'kpiNavigator.plExpenseUnknownHold'" in AUTH_JS, "auth wipe list includes hold")
    exact = AUTH_JS.split("USER_SCOPE_CLEAR_EXACT = [", 1)[1].split("];", 1)[0]
    assert_true("plExpenseUnknownHold" in exact, "hold is exact user-scope key")
    assert_true("pl_json = NULL" in RESET_PHP, "reset-user-kpi nulls pl_json (hold lives there)")
    assert_true("kpi-expense-unknown-hold" not in SALES_PARSER, "Sales importer untouched")
    assert_true("KpiExpenseUnknownHold" in HOLD_JS, "helper export")
    assert_true("exp_custom_" in HOLD_JS and "Never exp_custom" in HOLD_JS, "helper forbids custom-line ids")
    assert_true("STORAGE_KEY = 'kpiNavigator.plExpenseUnknownHold'" in HOLD_JS, "single storage key")


def test_pages_wire_helper() -> None:
    for path in PL_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        assert_true("kpi-expense-unknown-hold.js" in html, f"{rel} loads hold helper")
        assert_true("persistUnmatchedFromPlan" in html, f"{rel} persists unmatched")
        assert_true("rowsByPeriod" in html, f"{rel} keeps unmatched amounts")
        assert_true("__plAddCatalogLineWithLabel" in html, f"{rel} existing create path kept")
        assert_true("bestScore >= 0.6" in html, f"{rel} fuzzy threshold kept")
    for path in MEP_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        assert_true("kpi-expense-unknown-hold.js" in html, f"{rel} loads hold helper")
        assert_true("skipped++;" in html, f"{rel} skipped count contract kept")
        assert_true("日次反映" in html or "Daily applied" in html, f"{rel} existing alert kept")
    assert_true("KpiExpenseUnknownHold.ingestUnmatched" in PL_PY, "PL python source wired")
    builder = (SCRIPTS / "build_pl_table_page.py").read_text(encoding="utf-8")
    assert_true("kpi-expense-unknown-hold.js" in builder, "PL builder loads hold helper")


def test_helper_shape_in_js() -> None:
    assert_true("status = 'unknown'" in HOLD_JS or 'STATUS_UNKNOWN = \'unknown\'' in HOLD_JS, "status unknown")
    assert_true("importBatchId" in HOLD_JS and "sourceFilename" in HOLD_JS, "batch/filename fields")
    assert_true("Math.imul(h, 16777619)" in HOLD_JS, "fnv1a in JS")
    sample = unknown_id_for("予約サイト利用料")
    assert_true(re.fullmatch(r"unk_[0-9a-f]{8}", sample), "unknownId shape")


def test_6c_regression() -> None:
    before = u6c.FAILED
    u6c.test_lineid_priority_and_rename()
    u6c.test_inactive_orphan_unknown()
    u6c.test_c2_l2_high_confidence_synonyms()
    u6c.test_pages_load_shared_resolver()
    assert_true(u6c.FAILED == before, "6C regression stays green")


def main() -> int:
    print("--- C2-L3-A PL preserve ---")
    test_pl_unknown_preserves_label_amount_date()
    test_pl_skip_still_preserves_hold()
    print("--- C2-L3-A MEP ---")
    test_mep_unknown_hold_not_table()
    print("--- C2-L3-A identity / known ---")
    test_stable_id_and_merge()
    test_known_and_synonym_not_held()
    test_orphan_inactive_rules()
    print("--- C2-L3-A persistence wiring ---")
    test_gateway_auth_reset_wiring()
    test_pages_wire_helper()
    test_helper_shape_in_js()
    print("--- 6C regression ---")
    test_6c_regression()
    print(f"passed={PASSED} failed={FAILED}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
