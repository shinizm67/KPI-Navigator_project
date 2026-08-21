#!/usr/bin/env python3
"""Create zh-tw Change Email (+ Edit) from EN, and wire JA/EN language switchers."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_zh_tw_profile_pages import (  # noqa: E402
    _patch_lang_switcher,
    _strip_export_script,
)

EMAIL_REPLACEMENTS = [
    (
        "Change Email Address (Edit) | KPI Pilot | FORGE LABORATORY",
        "變更電子郵件地址（編輯） | KPI Pilot | FORGE LABORATORY",
    ),
    (
        "Change Email Address | KPI Pilot | FORGE LABORATORY",
        "變更電子郵件地址 | KPI Pilot | FORGE LABORATORY",
    ),
    ("<html lang=\"en\">", "<html lang=\"zh-TW\">"),
    ('href="style.css"', 'href="../../en/setting/style.css"'),
    ("https://forge-laboratory.com/en", "https://forge-laboratory.com"),
    (">Change Email Address</h2>", ">變更電子郵件地址</h2>"),
    ("Updated successfully.", "已成功更新。"),
    ("Current Email Address :", "目前的電子郵件地址 :"),
    # Longer phrase first so "New Email Address" does not leave "Confirm 新的…"
    ("Confirm New Email Address :", "確認新的電子郵件地址 :"),
    ("New Email Address :", "新的電子郵件地址 :"),
    ("Password :", "密碼 :"),
    (">Edit</a>", ">編輯</a>"),
    (">Update Email Address</button>", ">更新電子郵件地址</button>"),
    ('aria-label="Show password"', 'aria-label="顯示密碼"'),
    ('title="Show password"', 'title="顯示密碼"'),
    ("Hide password", "隱藏密碼"),
    ("Show password", "顯示密碼"),
    ("Please enter a new email address.", "請輸入新的電子郵件地址。"),
    ("Please enter a valid email address.", "請輸入有效的電子郵件地址。"),
    ("Please confirm your new email address.", "請確認新的電子郵件地址。"),
    ("Email addresses do not match.", "電子郵件地址不一致。"),
    ("Please enter your password.", "請輸入密碼。"),
    ("Current workspace", "目前工作區"),
    ("Workspace list", "工作區清單"),
    ("Switch to Office Mode", "切換至 Office Mode"),
    ("Switch to Sci-Fi Mode", "切換至 Sci-Fi Mode"),
    ("Select language", "選擇語言"),
    ("Language options", "語言選項"),
    ("Back to top", "回到頁首"),
]


def build_zh_tw_from_en(src_name: str) -> Path:
    src = ROOT / "en" / "setting" / src_name
    dst = ROOT / "zh-tw" / "setting" / src_name
    text = _strip_export_script(src.read_text(encoding="utf-8"))
    for a, b in EMAIL_REPLACEMENTS:
        text = text.replace(a, b)
    text = text.replace(
        "btnModeToggle.setAttribute('aria-label', isOffice ? 'Switch to Sci-Fi Mode' : 'Switch to Office Mode');",
        "btnModeToggle.setAttribute('aria-label', isOffice ? '切換至 Sci-Fi Mode' : '切換至 Office Mode');",
    )
    # Password toggle labels in edit page JS
    text = text.replace(
        "btn.setAttribute('aria-label', isPassword ? 'Hide password' : 'Show password');",
        "btn.setAttribute('aria-label', isPassword ? '隱藏密碼' : '顯示密碼');",
    )
    text = text.replace(
        "btn.setAttribute('title', isPassword ? 'Hide password' : 'Show password');",
        "btn.setAttribute('title', isPassword ? '隱藏密碼' : '顯示密碼');",
    )

    text = _patch_lang_switcher(
        text,
        active="zh-tw",
        url_ja=f"../../setting/{src_name}",
        url_en=f"../../en/setting/{src_name}",
        url_zh_tw=src_name,
    )
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text, encoding="utf-8")
    print(f"wrote {dst.relative_to(ROOT)}")
    return dst


def wire_ja_en_lang_switchers() -> None:
    mapping = {
        ("setting/change_email.html", "ja"): (
            "change_email.html",
            "../en/setting/change_email.html",
            "../zh-tw/setting/change_email.html",
        ),
        ("en/setting/change_email.html", "en"): (
            "../../setting/change_email.html",
            "change_email.html",
            "../../zh-tw/setting/change_email.html",
        ),
        ("setting/change_email_edit.html", "ja"): (
            "change_email_edit.html",
            "../en/setting/change_email_edit.html",
            "../zh-tw/setting/change_email_edit.html",
        ),
        ("en/setting/change_email_edit.html", "en"): (
            "../../setting/change_email_edit.html",
            "change_email_edit.html",
            "../../zh-tw/setting/change_email_edit.html",
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
        [sys.executable, str(ROOT / "scripts" / "build_site_chrome.py"), "settings"],
        cwd=str(ROOT / "scripts"),
    )
    if rc != 0:
        raise SystemExit(f"build_site_chrome failed: {rc}")
    from apply_kpi_pl_mep_export import inject_script  # noqa: WPS433

    for rel in (
        "setting/change_email.html",
        "setting/change_email_edit.html",
        "en/setting/change_email.html",
        "en/setting/change_email_edit.html",
        "zh-tw/setting/change_email.html",
        "zh-tw/setting/change_email_edit.html",
        "zh-tw/setting/profile.html",
        "zh-tw/setting/preferences.html",
    ):
        path = ROOT / rel
        if not path.is_file():
            continue
        path.write_text(inject_script(path.read_text(encoding="utf-8")), encoding="utf-8")
        print(f"export inject: {rel}")


def main() -> None:
    build_zh_tw_from_en("change_email.html")
    build_zh_tw_from_en("change_email_edit.html")
    wire_ja_en_lang_switchers()
    refresh_chrome_and_export()
    print("build_zh_tw_change_email_pages: OK")


if __name__ == "__main__":
    main()
