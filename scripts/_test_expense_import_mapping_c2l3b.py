# -*- coding: utf-8 -*-
"""C2-L3-B: persistent expense mapping record + user-scoped aliases.

Twin of js/kpi-expense-import-mapping.js. Amount hold stays L3-A.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from pl_line_catalog import expense_detail_default_catalog  # noqa: E402

import _test_expense_csv_import_6c as u6c  # noqa: E402
import _test_expense_unknown_hold_c2l3a as l3a  # noqa: E402
import _test_csv_import_safety_ux_6h as u6h  # noqa: E402

FAILED = 0
PASSED = 0

MAP_JS = (ROOT / "js" / "kpi-expense-import-mapping.js").read_text(encoding="utf-8")
GATEWAY_JS = (ROOT / "js" / "kpi-data-gateway.js").read_text(encoding="utf-8")
AUTH_JS = (ROOT / "js" / "kpi-auth-client.js").read_text(encoding="utf-8")
PL_PY = (SCRIPTS / "pl_expense_import_client.py").read_text(encoding="utf-8")
RESET_PHP = (ROOT / "api" / "v1" / "_admin_reset_kpi.php").read_text(encoding="utf-8")
SALES_PARSER = (SCRIPTS / "daily_sales_import_client.py").read_text(encoding="utf-8")
HOLD_JS = (ROOT / "js" / "kpi-expense-unknown-hold.js").read_text(encoding="utf-8")

MAP_KEY = "kpiNavigator.plExpenseImportMapping"
LEGACY_ALIAS_KEY = "kpiNavigator.plExpenseImportAliases"
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


def empty_blob():
    return {"schemaVersion": 1, "aliases": {}, "records": {}}


def norm_text(v) -> str:
    return u6c.norm_text(v)


def classify_via(raw, line, aliases) -> str:
    if not line:
        return "none"
    line_id = str(line.get("lineId") or "")
    trimmed = str(raw or "").strip()
    if trimmed == line_id:
        return "lineId"
    k = norm_text(trimmed)
    if k and norm_text(line_id) == k:
        return "lineId"
    for label in (line.get("labelJa"), line.get("labelEn"), line.get("labelZh"), line.get("labelZhTw")):
        if label and norm_text(label) == k:
            return "label"
    if aliases and aliases.get(k) and str(aliases[k]) == line_id:
        return "alias"
    return "synonym"


def status_for(via, resolved_line_id, skipped) -> str:
    if skipped:
        return "skipped"
    if not resolved_line_id:
        return "unknown"
    if via in ("alias", "user-assigned"):
        return "user-assigned"
    return "auto"


def merge_date_range(prev, incoming):
    incoming = incoming or {}
    prev = prev or {}
    from_v = str(incoming.get("from") or "") or str(prev.get("from") or "")
    to_v = str(incoming.get("to") or "") or str(prev.get("to") or "")
    if prev.get("from") and from_v and str(prev["from"]) < from_v:
        from_v = str(prev["from"])
    if prev.get("to") and to_v and str(prev["to"]) > to_v:
        to_v = str(prev["to"])
    if not from_v and not to_v:
        return None
    return {"from": from_v or to_v, "to": to_v or from_v}


def upsert_entries(blob, entries, meta=None):
    blob = copy.deepcopy(blob or empty_blob())
    blob.setdefault("aliases", {})
    blob.setdefault("records", {})
    meta = meta or {}
    imported_at = meta.get("importedAt")
    if not isinstance(imported_at, (int, float)):
        imported_at = 1
    batch_id = str(meta.get("importBatchId") or "imp_test")
    filename = str(meta.get("sourceFilename") or "")
    for raw in entries or []:
        original = str(raw.get("originalLabel") or "").strip()
        normalized = norm_text(raw.get("normalizedLabel") or original)
        if not normalized:
            continue
        resolved = str(raw.get("resolvedLineId") or "")
        via = str(raw.get("via") or ("auto" if resolved else "none"))
        skipped = bool(raw.get("skipped"))
        status = raw.get("status") or status_for(via, resolved, skipped)
        if status not in ("auto", "user-assigned", "unknown", "skipped"):
            status = status_for(via, resolved, skipped)
        rec = blob["records"].get(normalized) or {}
        rec["originalLabel"] = rec.get("originalLabel") or original or normalized
        rec["normalizedLabel"] = normalized
        rec["resolvedLineId"] = resolved
        rec["status"] = status
        rec["via"] = via
        rec["sourceType"] = "expense"
        rec["importBatchId"] = batch_id
        rec["importedAt"] = imported_at
        if filename:
            rec["sourceFilename"] = filename
        rec["dateRange"] = merge_date_range(rec.get("dateRange"), raw.get("dateRange"))
        if status in ("unknown", "skipped"):
            rec["unknownId"] = raw.get("unknownId") or rec.get("unknownId") or l3a.unknown_id_for(normalized)
            if not resolved:
                rec["resolvedLineId"] = ""
        else:
            rec["unknownId"] = raw.get("unknownId") or ""
        blob["records"][normalized] = rec
    blob["schemaVersion"] = 1
    return blob


def migrate_legacy_aliases(blob, legacy):
    blob = copy.deepcopy(blob or empty_blob())
    blob.setdefault("aliases", {})
    if not isinstance(legacy, dict):
        return blob
    for k, v in legacy.items():
        if not blob["aliases"].get(k) and v:
            blob["aliases"][k] = str(v)
    return blob


def catalog(bt="restaurant"):
    return [dict(row) for row in expense_detail_default_catalog(bt)]


def plan_mapping(rows, lines, aliases=None, business_type="restaurant", skipped_norms=None):
    aliases = aliases or {}
    skipped_norms = skipped_norms or {}
    cols = u6c.detect_columns(rows)
    resolve = u6c.make_resolver(lines, aliases, business_type=business_type)
    draft = {}
    start = cols["start"]
    for row in rows[start:]:
        date = u6c.norm_date(row[cols["dateCol"]] if cols["dateCol"] < len(row) else "")
        item = str(row[cols["itemCol"]] if cols["itemCol"] < len(row) else "").strip()
        if not date or not item or u6c.is_header_item(item):
            continue
        line = resolve(item)
        k = norm_text(item)
        via = classify_via(item, line, aliases)
        if k not in draft:
            draft[k] = {
                "originalLabel": item,
                "resolvedLineId": str(line["lineId"]) if line else "",
                "via": via,
                "periods": {},
            }
        draft[k]["periods"][date] = True
        if line:
            draft[k]["resolvedLineId"] = str(line["lineId"])
            draft[k]["via"] = via
    entries = []
    for k, d in draft.items():
        periods = sorted(d["periods"])
        resolved = "" if skipped_norms.get(k) else d["resolvedLineId"]
        via = d["via"]
        status = status_for(via, resolved, bool(skipped_norms.get(k)))
        entries.append({
            "originalLabel": d["originalLabel"],
            "normalizedLabel": k,
            "resolvedLineId": resolved,
            "via": via,
            "status": status,
            "skipped": bool(skipped_norms.get(k)),
            "unknownId": l3a.unknown_id_for(k) if status in ("unknown", "skipped") else "",
            "dateRange": {"from": periods[0], "to": periods[-1]} if periods else None,
        })
    return entries


META = {
    "importBatchId": "imp_l3btest_abc123",
    "importedAt": 1727000000000,
    "sourceFilename": "expenses_2026.csv",
}


def test_auto_synonym_record() -> None:
    lines = catalog()
    entries = plan_mapping(
        [["日付", "費目", "金額"], ["2026-01", "店舗家賃", "100"]],
        lines,
        business_type="restaurant",
    )
    blob = upsert_entries(empty_blob(), entries, META)
    rec = blob["records"][norm_text("店舗家賃")]
    assert_true(rec["status"] == "auto", "1 synonym mapping status auto")
    assert_true(rec["via"] == "synonym", "1 synonym via")
    assert_true(rec["resolvedLineId"] == "exp_rent", "1 synonym target rent")
    assert_true(rec["sourceType"] == "expense", "1 expense sourceType")


def test_exact_label_record() -> None:
    lines = catalog()
    rent = next(row for row in lines if row["lineId"] == "exp_rent")
    entries = plan_mapping(
        [["日付", "費目", "金額"], ["2026-01", rent["labelJa"], "80"]],
        lines,
        business_type="restaurant",
    )
    rec = upsert_entries(empty_blob(), entries, META)["records"][norm_text(rent["labelJa"])]
    assert_true(rec["status"] == "auto", "2 exact label status auto")
    assert_true(rec["via"] == "label", "2 exact label via")
    assert_true(rec["resolvedLineId"] == "exp_rent", "2 exact label target")


def test_user_alias_record() -> None:
    lines = catalog()
    aliases = {norm_text("オーナー給与"): "exp_rent"}
    entries = plan_mapping(
        [["日付", "費目", "金額"], ["2026-02", "オーナー給与", "50"]],
        lines,
        aliases=aliases,
        business_type="restaurant",
    )
    rec = upsert_entries(empty_blob(), entries, META)["records"][norm_text("オーナー給与")]
    assert_true(rec["status"] == "user-assigned", "3 alias status user-assigned")
    assert_true(rec["via"] == "alias", "3 alias via")
    assert_true(rec["resolvedLineId"] == "exp_rent", "3 alias target")


def test_unknown_record() -> None:
    lines = catalog()
    entries = plan_mapping(
        [["日付", "費目", "金額"], ["2026-03", "予約サイト利用料", "12"]],
        lines,
        business_type="restaurant",
    )
    rec = upsert_entries(empty_blob(), entries, META)["records"][norm_text("予約サイト利用料")]
    assert_true(rec["status"] == "unknown", "4 unknown status")
    assert_true(rec["resolvedLineId"] == "", "4 unknown has no lineId")
    assert_true(str(rec["unknownId"]).startswith("unk_"), "4 unknownId unk_")
    assert_true("exp_custom_" not in rec["unknownId"], "4 no custom id")


def test_skipped_record() -> None:
    lines = catalog()
    entries = plan_mapping(
        [["日付", "費目", "金額"], ["2026-04", "予約サイト利用料", "9"]],
        lines,
        business_type="restaurant",
        skipped_norms={norm_text("予約サイト利用料"): True},
    )
    rec = upsert_entries(empty_blob(), entries, META)["records"][norm_text("予約サイト利用料")]
    assert_true(rec["status"] == "skipped", "5 skipped status")
    assert_true(rec["resolvedLineId"] == "", "5 skipped has no lineId")


def test_filename_imported_at_batch() -> None:
    lines = catalog()
    entries = plan_mapping(
        [["日付", "費目", "金額"], ["2026-01", "店舗家賃", "1"]],
        lines,
        business_type="restaurant",
    )
    rec = upsert_entries(empty_blob(), entries, META)["records"][norm_text("店舗家賃")]
    assert_true(rec["sourceFilename"] == "expenses_2026.csv", "6 sourceFilename saved")
    assert_true(rec["importedAt"] == 1727000000000, "7 importedAt saved")
    assert_true(rec["importBatchId"] == "imp_l3btest_abc123", "8 importBatchId saved")
    assert_true(rec["importBatchId"].startswith("imp_"), "8 batch prefix")


def test_upsert_not_infinite_history() -> None:
    lines = catalog()
    first = plan_mapping(
        [["日付", "費目", "金額"], ["2026-01", "店舗家賃", "1"]],
        lines,
        business_type="restaurant",
    )
    blob = upsert_entries(empty_blob(), first, META)
    second_meta = dict(META)
    second_meta["importBatchId"] = "imp_second"
    second_meta["sourceFilename"] = "expenses_2026_again.csv"
    second_meta["importedAt"] = 1727000000999
    second = plan_mapping(
        [["日付", "費目", "金額"], ["2026-06", "店舗家賃", "2"]],
        lines,
        business_type="restaurant",
    )
    blob = upsert_entries(blob, second, second_meta)
    recs = [k for k in blob["records"] if blob["records"][k]["normalizedLabel"] == norm_text("店舗家賃")]
    assert_true(len(recs) == 1, "reimport upserts one mapping record")
    rec = blob["records"][norm_text("店舗家賃")]
    assert_true(rec["importBatchId"] == "imp_second", "latest batch wins")
    assert_true(rec["dateRange"]["from"] == "2026-01", "dateRange keeps earlier from")
    assert_true(rec["dateRange"]["to"] == "2026-06", "dateRange widens to")


def test_logout_login_round_trip() -> None:
    blob = upsert_entries(
        empty_blob(),
        [{
            "originalLabel": "店舗家賃",
            "normalizedLabel": norm_text("店舗家賃"),
            "resolvedLineId": "exp_rent",
            "via": "synonym",
            "status": "auto",
        }],
        META,
    )
    blob["aliases"][norm_text("オーナー給与")] = "exp_rent"
    pl = {"expenseImportMapping": blob, "unknownHold": {"schemaVersion": 1, "records": {}}}
    assert_true("expenseImportMapping: localGet(PL_IMPORT_MAPPING_KEY)" in GATEWAY_JS, "9 collect includes mapping")
    assert_true("hasOwnProperty.call(pl, 'expenseImportMapping')" in GATEWAY_JS, "9 apply round-trips mapping")
    restored = json.loads(json.dumps(pl["expenseImportMapping"]))
    assert_true(restored["records"][norm_text("店舗家賃")]["status"] == "auto", "9 record survives json round-trip")
    assert_true(restored["aliases"][norm_text("オーナー給与")] == "exp_rent", "9 aliases survive json round-trip")
    assert_true("PL_IMPORT_MAPPING_KEY" in GATEWAY_JS, "9 gateway mapping key")
    assert_true("key === PL_IMPORT_MAPPING_KEY" in GATEWAY_JS, "9 isPlSyncKey includes mapping")


def test_user_switch_and_reset() -> None:
    exact = AUTH_JS.split("USER_SCOPE_CLEAR_EXACT = [", 1)[1].split("];", 1)[0]
    assert_true("plExpenseImportMapping" in exact, "10 mapping wiped on user switch")
    assert_true("plExpenseImportAliases" in exact, "10 legacy aliases wiped on user switch")
    assert_true("localRemoveRaw(PL_IMPORT_MAPPING_KEY)" in GATEWAY_JS, "10 beginLocalUserScopeReset clears mapping")
    assert_true("kpiNavigator.plExpenseImportAliases" in GATEWAY_JS, "10 reset also drops legacy alias key")
    assert_true("kpi:localUserScopeChanged" in MAP_JS, "10 helper listens for scope change")
    assert_true("pl_json = NULL" in RESET_PHP, "11 reset-user-kpi nulls pl_json")
    assert_true("Not a PL catalog sibling" in MAP_JS, "mapping is not catalog sibling")


def test_alias_server_persistence_and_priority() -> None:
    blob = empty_blob()
    blob = migrate_legacy_aliases(blob, {norm_text("食材費"): "exp_custom_variable_foodalias"})
    assert_true(blob["aliases"][norm_text("食材費")] == "exp_custom_variable_foodalias", "12 legacy aliases migrate")
    restaurant = catalog()
    custom = {
        "lineId": "exp_custom_variable_foodalias",
        "labelJa": "独自食材",
        "labelEn": "Custom food",
        "labelZh": "",
        "labelZhTw": "",
        "active": True,
        "inputStyle": "monthly",
        "resolvedInputStyle": "monthly",
    }
    resolve = u6c.make_resolver(
        restaurant + [custom],
        aliases=blob["aliases"],
        business_type="restaurant",
    )
    assert_true(resolve("食材費")["lineId"] == "exp_custom_variable_foodalias", "13 alias beats synonym")
    orphan_aliases = {norm_text("食材費"): "exp_missing_zzzz"}
    orphan_r = u6c.make_resolver(restaurant, aliases=orphan_aliases, business_type="restaurant")
    hit = orphan_r("食材費")
    assert_true(hit is not None and hit["lineId"] == "exp_food_cost", "14 orphan alias falls through to synonym")
    missing_r = u6c.make_resolver(restaurant, aliases={norm_text("謎費目"): "exp_missing_zzzz"}, business_type="restaurant")
    assert_true(missing_r("謎費目") is None, "14 missing alias target with no synonym stays unmatched")
    assert_true("LEGACY_ALIAS_KEY" in MAP_JS, "12 helper migrates legacy LS aliases")
    assert_true("removeItem(LEGACY_ALIAS_KEY)" in MAP_JS, "12 legacy key removed after migrate")
    assert_true("loadAliases" in MAP_JS and "saveAliases" in MAP_JS, "12 helper owns aliases")
    assert_true("KpiExpenseImportMapping.loadAliases" in PL_PY, "12 PL prefers mapping helper aliases")
    js = (ROOT / "js" / "kpi-expense-csv-import.js").read_text(encoding="utf-8")
    alias_at = js.find("var aid = aliases && aliases[k];")
    syn_at = js.find("return resolveSynonym(k, byId, opts)")
    assert_true(0 <= alias_at < syn_at, "13 JS alias before synonym")


def test_pages_and_shape() -> None:
    assert_true("persistMappingFromPlan" in PL_PY, "PL python persists mapping")
    assert_true("skippedNorms" in PL_PY, "PL skipped status wired")
    assert_true("nextImportBatchId" in PL_PY, "PL uses mapping batch ids")
    assert_true("kpi-expense-import-mapping.js" in (SCRIPTS / "build_pl_table_page.py").read_text(encoding="utf-8"), "builder loads mapping helper")
    for path in PL_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        assert_true("kpi-expense-import-mapping.js" in html, f"{rel} loads mapping helper")
        assert_true("persistMappingFromPlan" in html, f"{rel} persists mapping records")
        assert_true("KpiExpenseImportMapping.loadAliases" in html, f"{rel} aliases via helper")
        assert_true("Mapping History" not in html, f"{rel} no Mapping History UI")
    for path in MEP_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        assert_true("kpi-expense-import-mapping.js" in html, f"{rel} MEP loads mapping helper")
        assert_true("KpiExpenseImportMapping.upsertEntries" in html, f"{rel} MEP upserts mapping")
        assert_true("KpiExpenseImportMapping.loadAliases" in html, f"{rel} MEP loads persisted aliases")
        assert_true("skipped++;" in html, f"{rel} MEP skipped count kept")
    assert_true("kpi-expense-import-mapping" not in SALES_PARSER, "Sales importer untouched")
    assert_true("imp_' + Date.now().toString(36) + '_' + Math.random()" in MAP_JS, "batch is time+random")
    assert_true("records keyed by normalizedLabel" in MAP_JS, "upsert by normalizedLabel")


def test_existing_suites() -> None:
    before6c = u6c.FAILED
    u6c.test_lineid_priority_and_rename()
    u6c.test_inactive_orphan_unknown()
    u6c.test_c2_l2_high_confidence_synonyms()
    u6c.test_pages_load_shared_resolver()
    assert_true(u6c.FAILED == before6c, "15 existing C2-L2 / 6C tests green")

    before_l3a = l3a.FAILED
    l3a.test_pl_unknown_preserves_label_amount_date()
    l3a.test_pl_skip_still_preserves_hold()
    l3a.test_mep_unknown_hold_not_table()
    l3a.test_stable_id_and_merge()
    l3a.test_known_and_synonym_not_held()
    l3a.test_orphan_inactive_rules()
    l3a.test_gateway_auth_reset_wiring()
    l3a.test_pages_wire_helper()
    l3a.test_helper_shape_in_js()
    assert_true(l3a.FAILED == before_l3a, "16 existing C2-L3-A tests green")

    before6h = u6h.FAILED
    u6h.test_mep_expense_confirm()
    u6h.test_pl_policy_unchanged()
    u6h.test_parsers_and_templates_untouched()
    assert_true(u6h.FAILED == before6h, "17 existing 6H regression green")


def main() -> int:
    print("--- C2-L3-B mapping records ---")
    test_auto_synonym_record()
    test_exact_label_record()
    test_user_alias_record()
    test_unknown_record()
    test_skipped_record()
    test_filename_imported_at_batch()
    test_upsert_not_infinite_history()
    print("--- C2-L3-B persistence ---")
    test_logout_login_round_trip()
    test_user_switch_and_reset()
    test_alias_server_persistence_and_priority()
    test_pages_and_shape()
    print("--- existing suites ---")
    test_existing_suites()
    print(f"passed={PASSED} failed={FAILED}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
