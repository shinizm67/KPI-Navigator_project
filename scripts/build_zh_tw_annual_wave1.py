#!/usr/bin/env python3
"""Annual zh-tw Wave 1: scaffold page + chrome + language switcher wiring.

Wave 1 does NOT translate cockpit / modals / insight body copy (later waves).
Creates zh-tw/app/annual/index.html from EN, injects zh-tw Global Menu chrome,
and wires JA/EN/TW language switchers on all three Annual trees.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_zh_tw_profile_pages import (  # noqa: E402
    _patch_lang_switcher,
    _strip_export_script,
)

SRC = ROOT / "en" / "app" / "annual" / "index.html"
DST = ROOT / "zh-tw" / "app" / "annual" / "index.html"

WAVE1_REPLACEMENTS = [
    ("<html lang=\"en\">", "<html lang=\"zh-TW\">"),
    (
        "Annual | KPI Navigator | FORGE LABORATORY",
        "年度 | KPI Navigator | FORGE LABORATORY",
    ),
    # zh-tw/setting has no style.css — use shared EN setting stylesheet.
    (
        'href="../../setting/style.css"',
        'href="../../../en/setting/style.css"',
    ),
    ("https://forge-laboratory.com/en", "https://forge-laboratory.com"),
]


def ensure_pages_app_entry() -> None:
    """Register zh-tw Annual in build_site_chrome.PAGES_APP if missing."""
    path = ROOT / "scripts" / "build_site_chrome.py"
    text = path.read_text(encoding="utf-8")
    needle = '{"path": "zh-tw/app/annual/index.html"'
    if needle in text:
        print("PAGES_APP already has zh-tw annual")
        return
    # Insert after EN annual entry.
    anchor = (
        '    {"path": "en/app/annual/index.html", "lang": "en", '
        '"base": "../../", "img": "../../../", "active": "annual", "daily": "overlay"},\n'
    )
    insert = (
        anchor
        + '    {"path": "zh-tw/app/annual/index.html", "lang": "zh-tw", '
        '"base": "../../", "img": "../../../", "active": "annual", "daily": "overlay"},\n'
    )
    if anchor not in text:
        raise SystemExit("could not find EN annual PAGES_APP entry to extend")
    path.write_text(text.replace(anchor, insert, 1), encoding="utf-8")
    print("registered zh-tw annual in PAGES_APP")


def ensure_export_target() -> None:
    path = ROOT / "scripts" / "apply_kpi_pl_mep_export.py"
    text = path.read_text(encoding="utf-8")
    line = '    "zh-tw/app/annual/index.html",\n'
    if line in text:
        print("export TARGET already has zh-tw annual")
        return
    anchor = '    "en/app/annual/index.html",\n'
    if anchor not in text:
        raise SystemExit("could not find en annual export target")
    path.write_text(text.replace(anchor, anchor + line, 1), encoding="utf-8")
    print("registered zh-tw annual in export TARGET_GLOBS")


def scaffold_from_en() -> None:
    DST.parent.mkdir(parents=True, exist_ok=True)
    # Copy then patch (file ~1.5MB).
    shutil.copyfile(SRC, DST)
    text = _strip_export_script(DST.read_text(encoding="utf-8"))
    for a, b in WAVE1_REPLACEMENTS:
        text = text.replace(a, b)
    text = _patch_lang_switcher(
        text,
        active="zh-tw",
        url_ja="../../../app/annual/index.html",
        url_en="../../../en/app/annual/index.html",
        url_zh_tw="index.html",
    )
    DST.write_text(text, encoding="utf-8")
    print(f"wrote {DST.relative_to(ROOT)} ({DST.stat().st_size} bytes)")


def wire_ja_en_lang_switchers() -> None:
    mapping = {
        ("app/annual/index.html", "ja"): (
            "index.html",
            "../../en/app/annual/index.html",
            "../../zh-tw/app/annual/index.html",
        ),
        ("en/app/annual/index.html", "en"): (
            "../../../app/annual/index.html",
            "index.html",
            "../../../zh-tw/app/annual/index.html",
        ),
    }
    for (rel, active), (url_ja, url_en, url_zh) in mapping.items():
        path = ROOT / rel
        text = _patch_lang_switcher(
            path.read_text(encoding="utf-8"),
            active=active,
            url_ja=url_ja,
            url_en=url_en,
            url_zh_tw=url_zh,
        )
        path.write_text(text, encoding="utf-8")
        print(f"wired lang switcher: {rel}")


def refresh_chrome_and_export() -> None:
    rc = subprocess.call(
        [sys.executable, str(ROOT / "scripts" / "build_site_chrome.py"), "app"],
        cwd=str(ROOT / "scripts"),
    )
    if rc != 0:
        raise SystemExit(f"build_site_chrome app failed: {rc}")
    rc = subprocess.call(
        [sys.executable, str(ROOT / "scripts" / "apply_kpi_pl_mep_export.py")],
        cwd=str(ROOT),
    )
    if rc != 0:
        raise SystemExit(f"apply_kpi_pl_mep_export failed: {rc}")


def verify() -> None:
    t = DST.read_text(encoding="utf-8")
    checks = [
        ('lang="zh-TW"', 'lang="zh-TW"' in t),
        ("title 年度", "年度 | KPI Navigator" in t),
        ("chrome 年度 nav", ">年度</span>" in t),
        ("chrome 帳戶", "帳戶設定" in t or ">帳戶<" in t),
        ("setting href", "../../setting/profile.html" in t),
        ("style path", "en/setting/style.css" in t),
        ("lang TW active", "lang-option-zh-tw lang-option-active" in t),
        ("export", "KPI-PL-MEP-EXPORT" in t),
        ("images path", "../../../images/" in t),
    ]
    for name, ok in checks:
        print(("OK" if ok else "FAIL"), name)
        if not ok:
            raise SystemExit(1)
    ja = (ROOT / "app/annual/index.html").read_text(encoding="utf-8")
    en = (ROOT / "en/app/annual/index.html").read_text(encoding="utf-8")
    assert 'data-url-zh-tw="../../zh-tw/app/annual/index.html"' in ja
    assert 'data-url-zh-tw="../../../zh-tw/app/annual/index.html"' in en
    print("verify: ALL OK")


def main() -> None:
    ensure_pages_app_entry()
    ensure_export_target()
    scaffold_from_en()
    wire_ja_en_lang_switchers()
    refresh_chrome_and_export()
    # Lang switcher on zh-tw may be overwritten only if chrome touched it — re-apply.
    text = _patch_lang_switcher(
        DST.read_text(encoding="utf-8"),
        active="zh-tw",
        url_ja="../../../app/annual/index.html",
        url_en="../../../en/app/annual/index.html",
        url_zh_tw="index.html",
    )
    DST.write_text(text, encoding="utf-8")
    verify()
    print("build_zh_tw_annual_wave1: OK")
    print(
        "Note: Wave 1 = chrome/scaffold only. Cockpit/modals/insight body "
        "remain English until later waves."
    )


if __name__ == "__main__":
    main()
