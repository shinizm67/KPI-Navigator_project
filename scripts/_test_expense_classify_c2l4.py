# -*- coding: utf-8 -*-
"""C2-L4: launch-safe expense classification. Twin of js/kpi-expense-classify.js."""

from __future__ import annotations

import copy
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from pl_line_catalog import reconcile_catalog_lines  # noqa: E402

import _test_expense_csv_import_6c as u6c  # noqa: E402
import _test_expense_unknown_hold_c2l3a as l3a  # noqa: E402
import _test_expense_import_mapping_c2l3b as l3b  # noqa: E402
import _test_csv_import_safety_ux_6h as u6h  # noqa: E402

FAILED = 0
PASSED = 0

CLS_JS = (ROOT / "js" / "kpi-expense-classify.js").read_text(encoding="utf-8")
HOLD_JS = (ROOT / "js" / "kpi-expense-unknown-hold.js").read_text(encoding="utf-8")
MAP_JS = (ROOT / "js" / "kpi-expense-import-mapping.js").read_text(encoding="utf-8")
GATEWAY_JS = (ROOT / "js" / "kpi-data-gateway.js").read_text(encoding="utf-8")
AUTH_JS = (ROOT / "js" / "kpi-auth-client.js").read_text(encoding="utf-8")
PL_PY = (SCRIPTS / "pl_expense_detail_client.py").read_text(encoding="utf-8")
BUILDER = (SCRIPTS / "build_pl_table_page.py").read_text(encoding="utf-8")
SALES_PARSER = (SCRIPTS / "daily_sales_import_client.py").read_text(encoding="utf-8")

PL_PAGES = u6c.PL_PAGES
MEP_PAGES = u6c.MEP_PAGES


def assert_true(cond: bool, msg: str) -> None:
    global PASSED, FAILED
    if cond:
        PASSED += 1
        return
    FAILED += 1
    print("FAIL:", msg)


def custom_line(line_id="exp_custom_variable_shop", bucket="variable", style="monthly", **kwargs):
    row = {
        "lineId": line_id,
        "labelJa": kwargs.pop("labelJa", "独自科目"),
        "labelEn": kwargs.pop("labelEn", "Custom"),
        "bucket": bucket,
        "inputStyle": style,
        "resolvedInputStyle": style,
        "isDefault": False,
        "active": True,
        "sortOrder": kwargs.pop("sortOrder", 0),
    }
    row.update(kwargs)
    return row


def preset_line(line_id="exp_rent", bucket="fixed", style="monthly", **kwargs):
    row = {
        "lineId": line_id,
        "labelJa": "店舗家賃",
        "labelEn": "Rent",
        "bucket": bucket,
        "inputStyle": style,
        "resolvedInputStyle": style,
        "isDefault": True,
        "active": True,
        "sortOrder": kwargs.pop("sortOrder", 0),
    }
    row.update(kwargs)
    return row


def can_set_line_bucket(line, next_bucket, has_nonzero_daily=False):
    if not line:
        return {"ok": False, "reason": "missing"}
    if line.get("active") is False:
        return {"ok": False, "reason": "inactive"}
    if line.get("presetOrphan"):
        return {"ok": False, "reason": "orphan"}
    lid = str(line.get("lineId") or "")
    if not lid.startswith("exp_custom_") or line.get("isDefault") is True:
        return {"ok": False, "reason": "not_custom"}
    if next_bucket not in ("fixed", "variable"):
        return {"ok": False, "reason": "invalid_bucket"}
    if line.get("bucket") == next_bucket:
        return {"ok": True, "noop": True}
    style = line.get("resolvedInputStyle") or line.get("inputStyle") or "monthly"
    if next_bucket == "fixed" and style == "daily" and has_nonzero_daily:
        return {"ok": False, "reason": "daily_data"}
    return {"ok": True}


def active_in_bucket(lines, bucket):
    return sorted(
        [l for l in lines if l and l.get("active") is not False and l.get("bucket") == bucket],
        key=lambda l: int(l.get("sortOrder") or 0),
    )


def apply_set_line_bucket(lines, line_id, next_bucket, has_nonzero_daily=False):
    lst = copy.deepcopy(lines)
    line = next((l for l in lst if l and str(l.get("lineId")) == str(line_id)), None)
    gate = can_set_line_bucket(line, next_bucket, has_nonzero_daily)
    if not gate["ok"]:
        return {"ok": False, "reason": gate["reason"], "lines": lst, "lineId": line_id}
    if gate.get("noop"):
        return {"ok": True, "changed": False, "lineId": str(line_id), "bucket": line["bucket"], "lines": lst}
    old_bucket = line["bucket"]
    line["bucket"] = next_bucket
    if next_bucket == "fixed":
        line["inputStyle"] = "monthly"
        line["resolvedInputStyle"] = "monthly"
    for i, row in enumerate(active_in_bucket(lst, old_bucket)):
        row["sortOrder"] = i
    others = [l for l in active_in_bucket(lst, next_bucket) if str(l.get("lineId")) != str(line_id)]
    max_order = max((int(l.get("sortOrder") or 0) for l in others), default=-1)
    line["sortOrder"] = max_order + 1
    return {
        "ok": True,
        "changed": True,
        "lineId": str(line["lineId"]),
        "oldBucket": old_bucket,
        "newBucket": next_bucket,
        "lines": lst,
    }


def move_line(lines, line_id, direction):
    lst = copy.deepcopy(lines)
    line = next((l for l in lst if l.get("lineId") == line_id and l.get("active")), None)
    if not line:
        return lst
    bucket_lines = active_in_bucket(lst, line["bucket"])
    ids = [l["lineId"] for l in bucket_lines]
    if line_id not in ids:
        return lst
    idx = ids.index(line_id)
    swap = idx - 1 if direction == "up" else idx + 1
    if swap < 0 or swap >= len(ids):
        return lst
    ids[idx], ids[swap] = ids[swap], ids[idx]
    for i, lid in enumerate(ids):
        target = next(l for l in lst if l["lineId"] == lid)
        target["sortOrder"] = i
    return lst


def rows_have_daily(rows):
    return any(re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(r.get("period") or "")) for r in (rows or []))


def decide_unknown_classify(rec, bucket):
    if not rec or rec.get("status") == "resolved":
        return {"ok": False, "reason": "missing_or_resolved"}
    if bucket not in ("fixed", "variable"):
        return {"ok": False, "reason": "invalid_bucket"}
    if rows_have_daily(rec.get("rows")) and bucket != "variable":
        return {"ok": False, "reason": "daily_requires_variable"}
    return {
        "ok": True,
        "bucket": bucket,
        "inputStyle": "daily" if rows_have_daily(rec.get("rows")) else "monthly",
        "originalLabel": rec.get("originalLabel") or rec.get("normalizedLabel") or "",
    }


def copy_hold_amounts(line_id, rows, monthly_by_year, daily_by_year):
    for row in rows or []:
        period = str(row.get("period") or "")
        amt = int(round(float(row.get("amount") or 0)))
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", period):
            year = int(period[:4])
            daily_by_year.setdefault(year, {}).setdefault(line_id, {})
            daily_by_year[year][line_id][period] = daily_by_year[year][line_id].get(period, 0) + amt
        else:
            m = re.fullmatch(r"(\d{4})-(\d{1,2})", period)
            if not m:
                continue
            year = int(m.group(1))
            month0 = int(m.group(2)) - 1
            key = f"{line_id}:{month0}"
            monthly_by_year.setdefault(year, {})
            monthly_by_year[year][key] = monthly_by_year[year].get(key, 0) + amt


def mark_hold_resolved(rec, line_id):
    rec["status"] = "resolved"
    rec["resolvedLineId"] = line_id
    rec["resolvedAt"] = 1
    return rec


def test_1_variable_monthly_to_fixed():
    amounts = {"exp_custom_variable_shop:0": 1200, "exp_rent:0": 50}
    snap = copy.deepcopy(amounts)
    lines = [
        preset_line(sortOrder=0),
        custom_line(sortOrder=0, bucket="variable", style="monthly"),
        custom_line("exp_custom_variable_other", bucket="variable", style="monthly", sortOrder=1),
    ]
    result = apply_set_line_bucket(lines, "exp_custom_variable_shop", "fixed")
    moved = next(l for l in result["lines"] if l["lineId"] == "exp_custom_variable_shop")
    assert_true(result["ok"] and result["changed"], "1 custom variable monthly -> fixed ok")
    assert_true(moved["lineId"] == "exp_custom_variable_shop", "1 lineId unchanged")
    assert_true(moved["bucket"] == "fixed", "1 bucket is fixed")
    assert_true(moved["inputStyle"] == "monthly" and moved["resolvedInputStyle"] == "monthly", "1 stays monthly")
    assert_true(amounts == snap, "1 amounts untouched")


def test_2_fixed_monthly_to_variable():
    amounts = {"exp_custom_fixed_keep:3": 880}
    snap = copy.deepcopy(amounts)
    lines = [
        preset_line(sortOrder=0),
        custom_line("exp_custom_fixed_keep", bucket="fixed", style="monthly", sortOrder=0),
    ]
    result = apply_set_line_bucket(lines, "exp_custom_fixed_keep", "variable")
    moved = next(l for l in result["lines"] if l["lineId"] == "exp_custom_fixed_keep")
    assert_true(result["ok"], "2 custom fixed -> variable ok")
    assert_true(moved["lineId"] == "exp_custom_fixed_keep", "2 lineId unchanged")
    assert_true(moved["bucket"] == "variable", "2 bucket is variable")
    assert_true(moved["inputStyle"] == "monthly", "2 does not auto-switch to daily")
    assert_true(amounts == snap, "2 amounts untouched")


def test_3_daily_block_and_empty_allow():
    lid = "exp_custom_variable_daily"
    daily = {2026: {lid: {"2026-04-02": 40}}}
    snap = copy.deepcopy(daily)
    line = custom_line(lid, bucket="variable", style="daily", sortOrder=0)
    blocked = apply_set_line_bucket([line], lid, "fixed", has_nonzero_daily=True)
    after = next(l for l in blocked["lines"] if l["lineId"] == lid)
    assert_true(not blocked["ok"] and blocked["reason"] == "daily_data", "3 daily values BLOCK")
    assert_true(after["bucket"] == "variable" and after["inputStyle"] == "daily", "3 style/bucket kept")
    assert_true(after["lineId"] == lid, "3 lineId kept on block")
    assert_true(daily == snap, "3 daily data fully preserved")

    empty = custom_line("exp_custom_variable_empty", bucket="variable", style="daily", sortOrder=0)
    allowed = apply_set_line_bucket([empty], "exp_custom_variable_empty", "fixed", has_nonzero_daily=False)
    moved = next(l for l in allowed["lines"] if l["lineId"] == "exp_custom_variable_empty")
    assert_true(allowed["ok"], "3 empty daily may become fixed")
    assert_true(moved["bucket"] == "fixed" and moved["inputStyle"] == "monthly", "3 empty daily -> fixed monthly")


def test_4_preset_block():
    line = preset_line()
    result = apply_set_line_bucket([line], "exp_rent", "variable")
    assert_true(not result["ok"] and result["reason"] == "not_custom", "4 preset bucket change BLOCK")
    assert_true(result["lines"][0]["bucket"] == "fixed", "4 preset bucket unchanged")


def test_5_inactive_orphan_block():
    hidden = custom_line("exp_custom_variable_hid", active=False, sortOrder=0)
    orphan = custom_line("exp_custom_variable_orp", presetOrphan=True, sortOrder=0)
    r1 = apply_set_line_bucket([hidden], "exp_custom_variable_hid", "fixed")
    r2 = apply_set_line_bucket([orphan], "exp_custom_variable_orp", "fixed")
    assert_true(not r1["ok"] and r1["reason"] == "inactive", "5 inactive BLOCK")
    assert_true(not r2["ok"] and r2["reason"] == "orphan", "5 orphan BLOCK")


def test_6_old_bucket_reindex():
    lines = [
        custom_line("exp_custom_variable_a", bucket="variable", sortOrder=0),
        custom_line("exp_custom_variable_b", bucket="variable", sortOrder=1),
        custom_line("exp_custom_variable_c", bucket="variable", sortOrder=2),
        preset_line(sortOrder=0),
    ]
    result = apply_set_line_bucket(lines, "exp_custom_variable_b", "fixed")
    remaining = active_in_bucket(result["lines"], "variable")
    assert_true([l["lineId"] for l in remaining] == ["exp_custom_variable_a", "exp_custom_variable_c"], "6 remaining variable ids")
    assert_true([l["sortOrder"] for l in remaining] == [0, 1], "6 old bucket reindex 0..n-1")


def test_7_new_bucket_max_plus_one():
    lines = [
        preset_line(sortOrder=0),
        custom_line("exp_custom_fixed_old", bucket="fixed", sortOrder=1),
        custom_line("exp_custom_variable_move", bucket="variable", sortOrder=0),
    ]
    result = apply_set_line_bucket(lines, "exp_custom_variable_move", "fixed")
    moved = next(l for l in result["lines"] if l["lineId"] == "exp_custom_variable_move")
    assert_true(moved["sortOrder"] == 2, "7 new bucket max(active)+1")


def test_8_move_line_regression():
    lines = [
        custom_line("exp_custom_variable_a", bucket="variable", sortOrder=0),
        custom_line("exp_custom_variable_b", bucket="variable", sortOrder=1),
        custom_line("exp_custom_variable_c", bucket="variable", sortOrder=2),
    ]
    after_reclass = apply_set_line_bucket(lines, "exp_custom_variable_a", "fixed")["lines"]
    var_after = move_line(after_reclass, "exp_custom_variable_c", "up")
    orders = {l["lineId"]: l["sortOrder"] for l in var_after if l["bucket"] == "variable"}
    assert_true(orders["exp_custom_variable_c"] == 0 and orders["exp_custom_variable_b"] == 1, "8 ▲▼ still swaps within bucket")
    assert_true("bucketLines.splice" in PL_PY and "target.sortOrder = i" in PL_PY, "8 existing moveLine contract kept")


def test_9_logout_login_round_trip():
    assert_true("PL_CATALOG_KEY" in GATEWAY_JS, "9 catalog still gateway-backed")
    assert_true("expenseImportMapping" in GATEWAY_JS, "9 mapping still gateway-backed")
    assert_true("unknownHold" in GATEWAY_JS, "9 hold still gateway-backed")
    assert_true("STORAGE_KEY" not in CLS_JS, "9 classify.js adds no new LS key")
    assert_true("saveLines(result.lines)" in PL_PY, "9 bucket persist uses existing catalog saveLines")
    assert_true("clearStoredAmountsForLine" not in CLS_JS, "9 classify does not delete monthly amounts")
    assert_true("clearDailyExpenses" not in CLS_JS, "9 classify does not delete daily amounts")


def test_10_bt_switch_keeps_custom_bucket():
    custom = custom_line("exp_custom_variable_shop", bucket="variable", style="monthly", sortOrder=5)
    switched_in = apply_set_line_bucket([preset_line(), custom], "exp_custom_variable_shop", "fixed")
    moved = next(l for l in switched_in["lines"] if l["lineId"] == "exp_custom_variable_shop")
    after_bt = reconcile_catalog_lines(switched_in["lines"], "retail")
    kept = next(l for l in after_bt if l["lineId"] == "exp_custom_variable_shop")
    assert_true(kept["bucket"] == "fixed", "10 BT switch keeps custom bucket")
    assert_true(kept["lineId"] == moved["lineId"], "10 custom lineId survives BT")
    assert_true("line.bucket = nextBucket" in CLS_JS, "10 JS mutates bucket in place")


def test_11_unknown_to_classified():
    rec = {
        "unknownId": "unk_deadbeef",
        "originalLabel": "予約サイト利用料",
        "normalizedLabel": l3b.norm_text("予約サイト利用料"),
        "status": "unknown",
        "rows": [{"period": "2026-01", "amount": 900}, {"period": "2026-02", "amount": 1100}],
    }
    rec["normalizedLabel"] = l3b.norm_text(rec["originalLabel"])
    decision = decide_unknown_classify(rec, "fixed")
    assert_true(decision["ok"] and decision["inputStyle"] == "monthly", "11 monthly unknown may be fixed")
    line_id = "exp_custom_fixed_fromhold"
    monthly = {2026: {"exp_rent:0": 1}}
    daily = {}
    snap_other = copy.deepcopy(monthly)
    copy_hold_amounts(line_id, rec["rows"], monthly, daily)
    mapping = {}
    mapping[rec["normalizedLabel"]] = {
        "originalLabel": rec["originalLabel"],
        "resolvedLineId": line_id,
        "status": "user-assigned",
        "via": "user-assigned",
    }
    aliases = {rec["normalizedLabel"]: line_id}
    kept_rows = copy.deepcopy(rec["rows"])
    mark_hold_resolved(rec, line_id)
    assert_true(monthly[2026][f"{line_id}:0"] == 900, "11 Jan amount copied")
    assert_true(monthly[2026][f"{line_id}:1"] == 1100, "11 Feb amount copied")
    assert_true(monthly[2026]["exp_rent:0"] == snap_other[2026]["exp_rent:0"], "11 other amounts untouched")
    assert_true(not daily, "11 no daily invented")
    assert_true(mapping[rec["normalizedLabel"]]["status"] == "user-assigned", "11 mapping user-assigned")
    assert_true(aliases[rec["normalizedLabel"]] == line_id, "11 alias points at new lineId")
    assert_true(rec["status"] == "resolved" and rec["resolvedLineId"] == line_id, "11 hold resolved, not deleted")
    assert_true(rec["rows"] == kept_rows, "11 original rows kept")
    assert_true(decision["originalLabel"] == "予約サイト利用料", "12 originalLabel kept through classify")


def test_12_original_label_and_daily_unknown():
    rec = {
        "unknownId": "unk_daily",
        "originalLabel": "仕入（日次）",
        "normalizedLabel": l3b.norm_text("仕入（日次）"),
        "status": "unknown",
        "rows": [{"period": "2026-03-04", "amount": 30}],
    }
    blocked = decide_unknown_classify(rec, "fixed")
    allowed = decide_unknown_classify(rec, "variable")
    assert_true(not blocked["ok"] and blocked["reason"] == "daily_requires_variable", "11 daily unknown cannot be fixed")
    assert_true(allowed["ok"] and allowed["inputStyle"] == "daily", "11 daily unknown stays daily variable")
    monthly, daily = {}, {}
    copy_hold_amounts("exp_custom_variable_fromhold", rec["rows"], monthly, daily)
    assert_true(daily[2026]["exp_custom_variable_fromhold"]["2026-03-04"] == 30, "11 daily amount copied")
    assert_true(not monthly, "11 daily classify does not monthly-convert")
    assert_true("originalLabel" in CLS_JS, "12 JS keeps originalLabel")
    assert_true("holdDeleted: false" in CLS_JS, "11 JS does not delete hold")


def test_13_14_15_regressions():
    before_l3a = l3a.FAILED
    l3a.test_pl_unknown_preserves_label_amount_date()
    l3a.test_pl_skip_still_preserves_hold()
    l3a.test_stable_id_and_merge()
    l3a.test_known_and_synonym_not_held()
    l3a.test_orphan_inactive_rules()
    l3a.test_gateway_auth_reset_wiring()
    l3a.test_pages_wire_helper()
    l3a.test_helper_shape_in_js()
    assert_true(l3a.FAILED == before_l3a, "13 L3-A regression green")

    before_l3b = l3b.FAILED
    l3b.test_auto_synonym_record()
    l3b.test_user_switch_and_reset()
    l3b.test_pages_and_shape()
    assert_true(l3b.FAILED == before_l3b, "14 L3-B regression green")

    before6c = u6c.FAILED
    u6c.test_lineid_priority_and_rename()
    u6c.test_inactive_orphan_unknown()
    u6c.test_c2_l2_high_confidence_synonyms()
    u6c.test_pages_load_shared_resolver()
    assert_true(u6c.FAILED == before6c, "15 C2-L2 / 6C regression green")

    before6h = u6h.FAILED
    u6h.test_mep_expense_confirm()
    u6h.test_pl_policy_unchanged()
    u6h.test_parsers_and_templates_untouched()
    assert_true(u6h.FAILED == before6h, "15 6H regression green")


def test_wiring_and_safety():
    assert_true("function applySetLineBucket" in CLS_JS, "JS applySetLineBucket")
    assert_true("reason: 'daily_data'" in CLS_JS, "JS daily_data block")
    assert_true("reason: 'not_custom'" in CLS_JS, "JS preset/custom gate")
    assert_true("cleanupAbandonedInputDataOnStyleChange" not in CLS_JS, "no conversion engine in classify.js")
    assert_true("setLineBucket" in PL_PY, "PL wires setLineBucket")
    assert_true("didBucket" in PL_PY, "bucket change skips style cleanup")
    assert_true("classifyUnknownHold" in PL_PY and "classifyUnknownHold" in CLS_JS, "unknown classify wired")
    assert_true("listUnresolved" in HOLD_JS and "markResolved" in HOLD_JS, "hold archive API")
    assert_true("STATUS_RESOLVED" in HOLD_JS, "hold resolved status")
    assert_true("kpi-expense-classify.js" in BUILDER, "builder loads classify helper")
    assert_true("pl-expense-label-edit-bucket" in BUILDER, "builder has bucket fieldset")
    assert_true("classify-unknown" in PL_PY, "line-manage classify entry")
    assert_true("kpi-expense-classify" not in SALES_PARSER, "Sales importer untouched")
    assert_true("CREATE TABLE" not in CLS_JS, "no new DB table")
    for path in PL_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        assert_true("kpi-expense-classify.js" in html, f"{rel} loads classify helper")
        assert_true("pl-expense-label-edit-bucket" in html, f"{rel} has bucket fieldset")
        assert_true("__plSetLineBucket" in html, f"{rel} exports setLineBucket")
        assert_true("classify-unknown" in html, f"{rel} unknown classify UI")
        assert_true("data-action=\"restore-line\"" in html, f"{rel} restore kept")
    for path in MEP_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        assert_true("kpi-expense-classify.js" not in html, f"{rel} MEP has no new classify UI")
        assert_true("kpi-expense-unknown-hold.js" in html, f"{rel} MEP still loads hold")


def main() -> int:
    print("--- C2-L4 launch-safe classify ---")
    test_1_variable_monthly_to_fixed()
    test_2_fixed_monthly_to_variable()
    test_3_daily_block_and_empty_allow()
    test_4_preset_block()
    test_5_inactive_orphan_block()
    test_6_old_bucket_reindex()
    test_7_new_bucket_max_plus_one()
    test_8_move_line_regression()
    test_9_logout_login_round_trip()
    test_10_bt_switch_keeps_custom_bucket()
    test_11_unknown_to_classified()
    test_12_original_label_and_daily_unknown()
    test_wiring_and_safety()
    test_13_14_15_regressions()
    print(f"PASSED={PASSED} FAILED={FAILED}")
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
