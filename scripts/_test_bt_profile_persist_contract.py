# -*- coding: utf-8 -*-
"""Profile industry persistence: profile.php is source of truth; store.meta is bridged."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BT = (ROOT / "js" / "kpi-business-type.js").read_text(encoding="utf-8")
GW = (ROOT / "js" / "kpi-data-gateway.js").read_text(encoding="utf-8")
CACHE = "20260927-bt1"

HOSTS = [
    ROOT / "setting/profile.html",
    ROOT / "setting/profile_edit.html",
    ROOT / "en/setting/profile.html",
    ROOT / "en/setting/profile_edit.html",
    ROOT / "zh-tw/setting/profile.html",
    ROOT / "zh-tw/setting/profile_edit.html",
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "zh-tw/app/annual/index.html",
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "zh-tw/app/monthly/index.html",
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
    ROOT / "zh-tw/app/monthly/edit/index.html",
    ROOT / "app/profit/pl/index.html",
    ROOT / "en/app/profit/pl/index.html",
    ROOT / "zh-tw/app/profit/pl/index.html",
]


def main() -> int:
    fails = []

    def check(cond: bool, msg: str) -> None:
        if not cond:
            fails.append(msg)

    check("function hydrateFromServerProfile()" in BT, "hydrateFromServerProfile exists")
    check("p.synced ? normalizeBusinessType" in BT, "only synced server profile counts as set")
    check("setBusinessType(type)" in BT, "hydrate writes store.meta via setBusinessType")
    check("normalizeBusinessType(serverProfileType)" in BT, "isSet reads profile cache")
    check("DEFAULT_TYPE" not in BT.split("function hydrateFromServerProfile()")[1].split("function isRestaurantLike")[0], "hydrate does not invent restaurant")
    check("hydrateFromServerProfile" in GW, "gateway calls profile hydrate after store GET")
    check("promptIndustryRequiredForImport" in BT, "unset gate still exists")

    for path in HOSTS:
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        check(f"kpi-business-type.js?v={CACHE}" in text, f"{rel} BT cache-bust")
        if path.name == "profile_edit.html":
            check("fromServer" in text and "setBusinessType(fromServer)" in text, f"{rel} edit applies server BT before meta re-sync")
        if path.name == "profile.html":
            check("hydrateFromServerProfile" in text, f"{rel} view hydrates industry from server")
            check("paintIndustry" in text, f"{rel} view can repaint after hydrate")

    if fails:
        for f in fails:
            print("FAIL", f)
        return 1
    print("ok", len(HOSTS), "hosts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
