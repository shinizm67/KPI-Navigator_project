# -*- coding: utf-8 -*-
"""Annual hydrates explicit server BT via the same session-sync path as MEP."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "zh-tw/app/annual/index.html",
]
MEP = ROOT / "app/monthly/edit/index.html"
BT_JS = ROOT / "js/kpi-business-type.js"
GW = ROOT / "js/kpi-data-gateway.js"

FAILED = 0
PASSED = 0


def check(cond: bool, msg: str) -> None:
    global PASSED, FAILED
    if cond:
        PASSED += 1
        return
    FAILED += 1
    print("FAIL:", msg)


def main() -> int:
    mep = MEP.read_text(encoding="utf-8")
    check("function enableSessionStoreSyncIfAuthed" in mep, "MEP still has session sync helper")
    for path in PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        check("function enableSessionStoreSyncIfAuthed" in html, f"{rel} session sync helper")
        check("function resolveStoreSyncBaseUrl" in html, f"{rel} store sync URL")
        check("enableSessionStoreSyncIfAuthed(meResult)" in html, f"{rel} sync before init")
        check(".then(function (r) {\n                run(r);" in html or "run(r)" in html, f"{rel} passes me() result")
        check("resetForUserScope();\n            init();" not in html, f"{rel} user-scope reuses startInit")
        check("isBusinessTypeSet()" in html, f"{rel} import gate still uses isBusinessTypeSet")
        check("promptIndustryRequiredForImport" in html, f"{rel} import gate offers Profile edit")
    bt = BT_JS.read_text(encoding="utf-8")
    check("function isBusinessTypeSet()" in bt, "isBusinessTypeSet exists")
    check("function hydrateFromServerProfile()" in bt, "BT hydrates from server profile")
    check("normalizeBusinessType(serverProfileType)" in bt, "isSet also honors fetched profile.php type")
    check("readPersistedBusinessType() || DEFAULT_TYPE" in bt, "getBusinessType fallback kept")
    gw = GW.read_text(encoding="utf-8")
    check("fullStore.meta.businessType" in gw, "gateway still applies server BT")
    check("hydrateFromServerProfile" in gw, "gateway bridges profile.php BT after store hydrate")
    check("Do not invent a default" in gw, "gateway does not invent restaurant")
    print("PASS" if FAILED == 0 else "FAIL", PASSED, "ok", FAILED, "fail")
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
