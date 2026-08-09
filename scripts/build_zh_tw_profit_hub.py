#!/usr/bin/env python3
"""zh-tw Profit hub: scaffold + chrome + body copy (MEP entry page).

Easiest-first MEP rollout:
  1) this hub (small)
  2) profit/pl (larger; separate waves)
  3) Annual waves 4–6 (remaining Annual i18n)
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

SRC = ROOT / "en" / "app" / "profit" / "index.html"
DST = ROOT / "zh-tw" / "app" / "profit" / "index.html"

REPLACEMENTS = [
    ('<html lang="en">', '<html lang="zh-TW">'),
    (
        "Profit | KPI Pilot | FORGE LABORATORY",
        "利潤 | KPI Pilot | FORGE LABORATORY",
    ),
    (
        'href="../../setting/style.css"',
        'href="../../../en/setting/style.css"',
    ),
    ("https://forge-laboratory.com/en", "https://forge-laboratory.com"),
    # Hub body
    (">Profit summary (Pro)</h1>", ">利潤摘要（專業方案）</h1>"),
    (
        "Read-only P&amp;L-oriented hub. Daily focuses on target vs. actual revenue; this area is for detailed income, expenses, and profit.",
        "以損益（P&amp;L）觀點整理收支與利潤的<strong>唯讀</strong>總覽。Daily 著重目標與實績對照；此區則供 PL 參照。",
    ),
    (
        "Open the <strong>Daily</strong> floating window from the <strong>Annual</strong> or <strong>Monthly</strong> page.",
        "每日利潤浮動視窗請從<strong>年度</strong>或<strong>月度</strong>頁面的選單「Daily」開啟。",
    ),
    (
        ">P&amp;L statement<span class=\"profit-hub-card-note\">Mock PL table · 12 months + annual total</span>",
        ">損益表（PL）<span class=\"profit-hub-card-note\">月次輸入雛形・12 個月＋年度合計</span>",
    ),
    (
        ">Daily profit<span class=\"profit-hub-card-note\">Coming soon (read-only)</span>",
        ">每日利潤<span class=\"profit-hub-card-note\">即將推出（唯讀）</span>",
    ),
    (
        ">Monthly profit<span class=\"profit-hub-card-note\">Coming soon (read-only)</span>",
        ">月度利潤<span class=\"profit-hub-card-note\">即將推出（唯讀）</span>",
    ),
    (
        ">Annual profit<span class=\"profit-hub-card-note\">Coming soon (read-only)</span>",
        ">年度利潤<span class=\"profit-hub-card-note\">即將推出（唯讀）</span>",
    ),
    ('aria-label="Current workspace"', 'aria-label="目前工作區"'),
    ('aria-label="Workspaces"', 'aria-label="工作區清單"'),
]


def ensure_pages_app_entry() -> None:
    path = ROOT / "scripts" / "build_site_chrome.py"
    text = path.read_text(encoding="utf-8")
    needle = '{"path": "zh-tw/app/profit/index.html"'
    if needle in text:
        print("PAGES_APP already has zh-tw profit")
        return
    anchor = (
        '    {"path": "en/app/profit/index.html", "lang": "en", '
        '"base": "../../", "img": "../../../", "active": "profit", "daily": "link"},\n'
    )
    insert = (
        anchor
        + '    {"path": "zh-tw/app/profit/index.html", "lang": "zh-tw", '
        '"base": "../../", "img": "../../../", "active": "profit", "daily": "link"},\n'
    )
    if anchor not in text:
        raise SystemExit("could not find EN profit PAGES_APP entry")
    path.write_text(text.replace(anchor, insert, 1), encoding="utf-8")
    print("registered zh-tw profit in PAGES_APP")


def ensure_export_target() -> None:
    path = ROOT / "scripts" / "apply_kpi_pl_mep_export.py"
    text = path.read_text(encoding="utf-8")
    line = '    "zh-tw/app/profit/index.html",\n'
    if line in text:
        print("export TARGET already has zh-tw profit hub")
        return
    anchor = '    "en/app/profit/index.html",\n'
    if anchor not in text:
        raise SystemExit("could not find en profit export target")
    path.write_text(text.replace(anchor, anchor + line, 1), encoding="utf-8")
    print("registered zh-tw profit hub in export TARGET")


def scaffold_from_en() -> None:
    DST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SRC, DST)
    text = _strip_export_script(DST.read_text(encoding="utf-8"))
    missing = []
    for a, b in REPLACEMENTS:
        if a not in text:
            missing.append(a[:80])
            continue
        text = text.replace(a, b)
    text = _patch_lang_switcher(
        text,
        active="zh-tw",
        url_ja="../../../app/profit/index.html",
        url_en="../../../en/app/profit/index.html",
        url_zh_tw="index.html",
    )
    DST.write_text(text, encoding="utf-8")
    if missing:
        print("WARN missing replacements:")
        for m in missing:
            print(" ", repr(m))
    print(f"wrote {DST.relative_to(ROOT)} ({DST.stat().st_size} bytes)")


def wire_ja_en_lang_switchers() -> None:
    mapping = {
        ("app/profit/index.html", "ja"): (
            "index.html",
            "../../en/app/profit/index.html",
            "../../zh-tw/app/profit/index.html",
        ),
        ("en/app/profit/index.html", "en"): (
            "../../../app/profit/index.html",
            "index.html",
            "../../../zh-tw/app/profit/index.html",
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
        ("title 利潤", "利潤 | KPI Pilot" in t),
        ("hub title", "利潤摘要（專業方案）" in t),
        ("PL card", "損益表（PL）" in t),
        ("chrome 洞察", "洞察" in t or ">洞察<" in t),
        ("style path", "en/setting/style.css" in t),
        ("lang TW active", "lang-option-zh-tw lang-option-active" in t),
        ("export", "KPI-PL-MEP-EXPORT" in t),
    ]
    for name, ok in checks:
        print(("OK" if ok else "FAIL"), name)
        if not ok:
            raise SystemExit(1)
    ja = (ROOT / "app/profit/index.html").read_text(encoding="utf-8")
    en = (ROOT / "en/app/profit/index.html").read_text(encoding="utf-8")
    assert 'data-url-zh-tw="../../zh-tw/app/profit/index.html"' in ja
    assert 'data-url-zh-tw="../../../zh-tw/app/profit/index.html"' in en
    print("verify: ALL OK")


def main() -> None:
    ensure_pages_app_entry()
    ensure_export_target()
    scaffold_from_en()
    wire_ja_en_lang_switchers()
    refresh_chrome_and_export()
    text = _patch_lang_switcher(
        DST.read_text(encoding="utf-8"),
        active="zh-tw",
        url_ja="../../../app/profit/index.html",
        url_en="../../../en/app/profit/index.html",
        url_zh_tw="index.html",
    )
    DST.write_text(text, encoding="utf-8")
    verify()
    print("build_zh_tw_profit_hub: OK")


if __name__ == "__main__":
    main()
