# -*- coding: utf-8 -*-
"""BR-LOCAL-VERIFY-01 Phase 2 — canonical fixture contract.

Seeds a temporary localTestMode file root. Does not open production,
MySQL, FTP, or mail.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "fixtures" / "local" / "canonical" / "manifest.json"
SEED = ROOT / "scripts" / "kpn_local_test_seed.php"
PRESETS = ROOT / "js" / "kpi-pl-expense-presets.js"
BUSINESS_TYPE = ROOT / "js" / "kpi-business-type.js"
LIVE_DATA = ROOT / "api" / "v1" / "data"
OUT = ROOT / "tests" / "results" / "local-canonical-fixtures.json"

EXPECTED_IDS = [
    "fx-basic-restaurant-ready",
    "fx-pro-restaurant-ready",
    "fx-pro-hotel-ready",
    "fx-basic-profile-required",
    "fx-basic-setup-required",
    "fx-legacy-pro",
]
CANONICAL_TYPES = ["restaurant", "retail", "hair_salon", "fitness", "hotel", "other"]
MEAL_FIELDS = [
    "lunch_sales",
    "dinner_sales",
    "total_customers",
    "lunch_customers",
    "dinner_customers",
    "total_groups",
    "lunch_groups",
    "dinner_groups",
]
CHECKS: list[tuple[str, bool]] = []


def check(name: str, ok: bool) -> None:
    CHECKS.append((name, bool(ok)))
    if not ok:
        raise SystemExit(f"FAIL {name}")


def php_bin() -> str:
    for name in ("php", "php.exe"):
        found = shutil.which(name)
        if found:
            return found
    local = Path(os.environ.get("LOCALAPPDATA", "")) / "kpn-tools" / "php" / "php.exe"
    if local.is_file():
        return str(local)
    return ""


def write_config(path: Path, root: Path, **overrides) -> None:
    data = {
        "localTestMode": True,
        "localDataRoot": root.resolve().as_posix(),
        "storageDriver": "file",
        "dbHost": "127.0.0.1",
        "dbName": "",
        "dbUser": "",
        "dbPass": "",
        "registrationEnabled": False,
        "allowSelfPlanChange": False,
        "passwordResetBaseUrl": "http://127.0.0.1:9",
        "supportEmail": "local-sink@localhost.test",
        "supportFrom": "local-sink@localhost.test",
        "token": "local-test-token",
        "planAdminToken": "local-test-plan-token",
    }
    data.update(overrides)
    lines = ["<?php", "return ["]
    for key, value in data.items():
        if isinstance(value, bool):
            rendered = "true" if value else "false"
        else:
            rendered = "'" + str(value).replace("\\", "\\\\").replace("'", "\\'") + "'"
        lines.append(f"    '{key}' => {rendered},")
    lines.append("];")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_seed(php: str, config: Path) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["KPI_V1_CONFIG"] = str(config)
    return subprocess.run(
        [php, str(SEED)],
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )


def load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def account_map(manifest: dict) -> dict:
    return {row["id"]: row for row in manifest["accounts"]}


def blob_file(root: Path, user_id: str) -> dict:
    return json.loads((root / f"{user_id}.json").read_text(encoding="utf-8"))


def user_file(root: Path, user_id: str) -> dict:
    return json.loads((root / "users" / f"{user_id}.json").read_text(encoding="utf-8"))


def profile_file(root: Path, user_id: str) -> dict:
    return json.loads((root / "profiles" / f"{user_id}.json").read_text(encoding="utf-8"))


def extract_assigned_json(text: str, name: str):
    marker = f"var {name} = "
    start = text.find(marker)
    if start < 0:
        raise SystemExit(f"missing {name}")
    value, _end = json.JSONDecoder().raw_decode(text[start + len(marker):])
    return value


def legacy_map(text: str) -> dict:
    match = re.search(r"var LEGACY_TO_CANONICAL = \{(.*?)\};", text, re.S)
    if not match:
        raise SystemExit("missing LEGACY_TO_CANONICAL")
    out = {}
    for key, value in re.findall(r"([A-Za-z0-9_]+)\s*:\s*'([^']+)'", match.group(1)):
        out[key] = value
    return out


def canonical_list(text: str) -> list[str]:
    match = re.search(r"var CANONICAL = \[(.*?)\];", text, re.S)
    if not match:
        raise SystemExit("missing CANONICAL")
    return re.findall(r"'([^']+)'", match.group(1))


def grandfathered(store: dict | None) -> bool:
    if not isinstance(store, dict):
        return False
    meta = store.get("meta") if isinstance(store.get("meta"), dict) else {}
    bag = meta.get("setup") if isinstance(meta.get("setup"), dict) else None
    complete = bool(bag and bag.get("complete") is True)
    active = bool(bag and bag.get("complete") is not True)
    sales = (store.get("timeline") or {}).get("dailySales") or {}
    has_sales = False
    for iso, value in sales.items():
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            has_sales = True
            break
    year = (store.get("years") or {}).get("2026") or {}
    plan = year.get("plan") if isinstance(year, dict) else {}
    target = isinstance(plan, dict) and plan.get("source") != "rollover-snapshot" and isinstance(plan.get("targetSales"), (int, float)) and plan.get("targetSales", 0) > 0
    return complete or ((not active) and (has_sales or target))


def assert_structure(manifest: dict) -> None:
    raw = MANIFEST_PATH.read_text(encoding="utf-8")
    check("clock frozen", manifest["clock"]["fixtureClock"] == "2026-10-03T12:00:00+09:00")
    check("timezone frozen", manifest["clock"]["fixtureTimezone"] == "Asia/Tokyo")
    check("canonical date frozen", manifest["clock"]["canonicalDate"] == "2026-10-03")
    check("no production host in manifest", "forge-laboratory" not in raw and "lolipop" not in raw)
    check("no ftp secret in manifest", "ftpPass" not in raw and "ftpPassword" not in raw)
    ids = [row["id"] for row in manifest["accounts"]]
    users = [row["userId"] for row in manifest["accounts"]]
    emails = [row["email"] for row in manifest["accounts"]]
    check("six accounts", ids == EXPECTED_IDS)
    check("unique ids", len(set(ids)) == len(ids))
    check("unique user ids", len(set(users)) == len(users) and all(not uid.startswith("_") for uid in users))
    check("unique emails", len(set(emails)) == len(emails) and all(email.endswith("@localhost.test") for email in emails))
    by_id = account_map(manifest)
    check("basic plan", by_id["fx-basic-restaurant-ready"]["plan"] == "basic")
    check("pro restaurant plan", by_id["fx-pro-restaurant-ready"]["plan"] == "pro")
    check("pro hotel plan", by_id["fx-pro-hotel-ready"]["plan"] == "pro")
    check("profile required plan", by_id["fx-basic-profile-required"]["plan"] == "basic")
    check("setup required plan", by_id["fx-basic-setup-required"]["plan"] == "basic")
    check("legacy omits plan", "plan" not in by_id["fx-legacy-pro"] and by_id["fx-legacy-pro"]["planSource"] == "legacy")
    check("profile required unset type", by_id["fx-basic-profile-required"]["businessType"] is None)
    check("setup required incomplete", by_id["fx-basic-setup-required"]["blob"]["store"]["meta"]["setup"]["complete"] is False)
    check("profile required empty store", by_id["fx-basic-profile-required"]["blob"]["store"] is None)
    check("setup required has no sales", by_id["fx-basic-setup-required"]["blob"]["store"]["timeline"]["dailySales"] == {})
    check("not grandfather profile", grandfathered(by_id["fx-basic-profile-required"]["blob"]["store"]) is False)
    check("not grandfather setup", grandfathered(by_id["fx-basic-setup-required"]["blob"]["store"]) is False)
    basic = by_id["fx-basic-restaurant-ready"]["blob"]["store"]
    check("basic cursor day", basic["timeline"]["dailySales"]["2026-10-03"] == 31000)
    check("basic closed day", basic["timeline"]["businessDays"]["2026-10-04"] is False and "2026-10-04" not in basic["timeline"]["dailySales"])
    meal = basic["years"]["2026"]["dailyMeal"]
    check("basic meal fields", all(meal[field]["2026-10-03"] > 0 for field in MEAL_FIELDS))
    check("basic food drink", basic["years"]["2026"]["dailyIncome"]["food_sales"]["2026-10-03"] == 20000)
    check("basic has no expenses", "dailyExpenses" not in basic["years"]["2026"] and "pl" not in by_id["fx-basic-restaurant-ready"]["blob"])
    pro = by_id["fx-pro-restaurant-ready"]["blob"]
    check("pro historical day", pro["store"]["timeline"]["dailySales"]["2025-04-02"] == 21000)
    check("pro historical not skipped", pro["store"]["meta"]["setup"]["historicalSkipped"] is False)
    check("pro target", pro["store"]["years"]["2026"]["plan"]["targetSales"] == 36000000)
    check("pro daily expense", pro["store"]["years"]["2026"]["dailyExpenses"]["exp_food_cost"]["2026-10-03"] == 9000)
    check("pro monthly expense", pro["pl"]["expensesByYear"]["2026"]["exp_rent:9"] == 150000)
    hotel = by_id["fx-pro-hotel-ready"]["blob"]
    hotel_year = hotel["store"]["years"]["2026"]
    check("hotel common sales", hotel["store"]["timeline"]["dailySales"]["2026-10-03"] == 64000)
    check("hotel has no meal structure", "dailyMeal" not in hotel_year and "dailyIncome" not in hotel_year)
    check("hotel linen and ota", hotel["pl"]["expensesByYear"]["2026"]["exp_linen_cleaning:9"] == 12000 and hotel["pl"]["expensesByYear"]["2026"]["exp_ota_fees:9"] == 7000)
    check("hotel daily labor", hotel_year["dailyExpenses"]["exp_variable_labor"]["2026-10-03"] == 8000)
    check("aliases", manifest["phase1Aliases"]["LOCAL_BASIC"] == "fx-basic-restaurant-ready" and manifest["phase1Aliases"]["LOCAL_PRO"] == "fx-pro-hotel-ready")
    check("account types supported", all(row["businessType"] in (None, "restaurant", "hotel") for row in manifest["accounts"]))
    cases = manifest["businessTypeCases"]
    check("four business type cases", [row["id"] for row in cases] == ["bt-retail", "bt-hair-salon", "bt-fitness", "bt-other"])
    bt_text = BUSINESS_TYPE.read_text(encoding="utf-8")
    preset_text = PRESETS.read_text(encoding="utf-8")
    canon = canonical_list(bt_text)
    legacy = legacy_map(bt_text)
    presets = extract_assigned_json(preset_text, "PRESETS")
    analysis = extract_assigned_json(preset_text, "ANALYSIS")
    check("product canonical types", canon == CANONICAL_TYPES)
    for row in cases:
        code = row["businessType"]
        check(f"{code} canonical", code in canon and row["presetFamily"] == code)
        check(f"{code} analysis", analysis[code]["mode"] == row["analysisMode"] == "key_expenses")
        line_ids = {line["lineId"] for line in presets[code]["lines"] if line.get("active") or line.get("isDefault")}
        check(f"{code} preset lines", set(row["representativeLineIds"]).issubset(line_ids))
        for raw in row["normalizeFrom"]:
            resolved = raw if raw in canon else legacy.get(raw)
            check(f"{code} normalize {raw}", resolved == code)


def assert_seeded(root: Path, manifest: dict) -> None:
    for row in manifest["accounts"]:
        blob = blob_file(root, row["userId"])
        check(f"seed blob {row['id']}", blob["store"] == row["blob"]["store"] and blob.get("pl") == row["blob"].get("pl"))
        check(f"seed nav {row['id']}", blob.get("annualNav") == row["blob"].get("annualNav"))
        user = user_file(root, row["userId"])
        check(f"seed email {row['id']}", user["email"] == row["email"] and user["createdAt"] == row["createdAt"])
        if row["planSource"] == "legacy":
            check("legacy file omits plan", "plan" not in user)
        else:
            check(f"seed plan {row['id']}", user.get("plan") == row["plan"])
        profile = profile_file(root, row["userId"])
        for key, value in row["profile"].items():
            check(f"profile {row['id']} {key}", profile.get(key) == value)
        check(
            f"profile {row['id']} updatedAt",
            profile.get("updatedAt") == manifest["clock"]["fixtureClock"],
        )


def canonical_state(root: Path, manifest: dict) -> dict:
    state = {}
    for row in manifest["accounts"]:
        user = user_file(root, row["userId"])
        user.pop("passwordHash", None)
        state[row["id"]] = {
            "user": user,
            "profile": profile_file(root, row["userId"]),
            "blob": blob_file(root, row["userId"]),
        }
    return state


def main() -> None:
    php = php_bin()
    if not php:
        raise SystemExit("php not found")
    manifest = load_manifest()
    assert_structure(manifest)
    work = Path(tempfile.mkdtemp(prefix="kpn-fx-"))
    data_root = work / "data"
    data_root.mkdir()
    config = work / "config.php"
    write_config(config, data_root)
    live_before = (LIVE_DATA / ".htaccess").read_bytes() if (LIVE_DATA / ".htaccess").is_file() else b""
    try:
        unsafe = work / "unsafe"
        unsafe.mkdir()
        (unsafe / "foreign.txt").write_text("keep", encoding="utf-8")
        unsafe_config = work / "unsafe.php"
        write_config(unsafe_config, unsafe)
        refused = run_seed(php, unsafe_config)
        check("unsafe root refused", refused.returncode != 0 and "local_test_refused:sentinel" in (refused.stderr or ""))
        check("foreign file kept", (unsafe / "foreign.txt").read_text(encoding="utf-8") == "keep")
        check("unsafe sentinel absent", not (unsafe / ".kpn-local-fixture-root").exists())

        prod_config = work / "prod.php"
        write_config(prod_config, LIVE_DATA)
        prod = run_seed(php, prod_config)
        check("production data path refused", prod.returncode != 0 and "local_test_refused:" in (prod.stderr or ""))
        live_after = (LIVE_DATA / ".htaccess").read_bytes() if (LIVE_DATA / ".htaccess").is_file() else b""
        check("production data unchanged", live_before == live_after)

        first = run_seed(php, config)
        check("seed succeeds", first.returncode == 0 and "seeded" in (first.stdout or ""))
        check("sentinel created", (data_root / ".kpn-local-fixture-root").is_file())
        assert_seeded(data_root, manifest)
        before_state = canonical_state(data_root, manifest)
        clock = manifest["clock"]["fixtureClock"]
        check(
            "captured profile updatedAt",
            all(item["profile"]["updatedAt"] == clock for item in before_state.values()),
        )

        marker = data_root / "keep.txt"
        marker.write_text("stay", encoding="utf-8")
        basic_id = account_map(manifest)["fx-basic-restaurant-ready"]["userId"]
        blob_path = data_root / f"{basic_id}.json"
        mutated = json.loads(blob_path.read_text(encoding="utf-8"))
        mutated["store"]["timeline"]["dailySales"]["2026-10-03"] = 1
        blob_path.write_text(json.dumps(mutated), encoding="utf-8")
        profile_path = data_root / "profiles" / f"{basic_id}.json"
        mutated_profile = json.loads(profile_path.read_text(encoding="utf-8"))
        mutated_profile["updatedAt"] = "1999-01-01T00:00:00+00:00"
        profile_path.write_text(json.dumps(mutated_profile), encoding="utf-8")
        sentinel = (data_root / ".kpn-local-fixture-root").read_text(encoding="utf-8")
        broken = sentinel.replace(sentinel.splitlines()[1], sentinel.splitlines()[1] + "-other")
        (data_root / ".kpn-local-fixture-root").write_text(broken, encoding="utf-8")
        blocked = run_seed(php, config)
        check("mismatched sentinel refused", blocked.returncode != 0 and "local_test_refused:sentinel" in (blocked.stderr or ""))
        check("mismatch did not restore", blob_file(data_root, basic_id)["store"]["timeline"]["dailySales"]["2026-10-03"] == 1)
        check(
            "mismatch kept profile timestamp",
            profile_file(data_root, basic_id)["updatedAt"] == "1999-01-01T00:00:00+00:00",
        )
        (data_root / ".kpn-local-fixture-root").write_text(sentinel, encoding="utf-8")

        again = run_seed(php, config)
        check("reseed succeeds", again.returncode == 0 and "seeded" in (again.stdout or ""))
        assert_seeded(data_root, manifest)
        after_state = canonical_state(data_root, manifest)
        check("reseed profile updatedAt", after_state["fx-basic-restaurant-ready"]["profile"]["updatedAt"] == clock)
        check("reseed canonical state", before_state == after_state)
        check("keep file survived", marker.read_text(encoding="utf-8") == "stay")

        env = os.environ.copy()
        env["KPI_V1_CONFIG"] = str(config)
        legacy_id = account_map(manifest)["fx-legacy-pro"]["userId"]
        legacy_path = (data_root / "users" / f"{legacy_id}.json").as_posix()
        shown = subprocess.run(
            [php, "-r", "require 'api/v1/_auth.php'; $u = json_decode(file_get_contents($argv[1]), true); $p = kpi_v1_auth_public_user($u, kpi_v1_load_config()); echo $p['plan'];", legacy_path],
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )
        check("legacy resolves pro", shown.returncode == 0 and (shown.stdout or "").strip() == "pro")
    finally:
        shutil.rmtree(work, ignore_errors=True)
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps({"ok": all(ok for _name, ok in CHECKS), "passed": sum(1 for _n, ok in CHECKS if ok), "total": len(CHECKS), "checks": [{"name": n, "ok": ok} for n, ok in CHECKS]}, ensure_ascii=False, indent=2), encoding="utf-8")
    passed = sum(1 for _name, ok in CHECKS if ok)
    print(f"passed {passed}/{len(CHECKS)}")


if __name__ == "__main__":
    main()
