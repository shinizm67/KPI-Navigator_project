#!/usr/bin/env python3
"""Create zh-tw Change Password (+ success) from EN, and wire JA/EN language switchers."""

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

PW_REPLACEMENTS = [
    (
        "Change Password (Edit) | KPI Pilot | FORGE LABORATORY",
        "變更密碼（編輯） | KPI Pilot | FORGE LABORATORY",
    ),
    (
        "Change Password | KPI Pilot | FORGE LABORATORY",
        "變更密碼 | KPI Pilot | FORGE LABORATORY",
    ),
    ("<html lang=\"en\">", "<html lang=\"zh-TW\">"),
    ('href="style.css"', 'href="../../en/setting/style.css"'),
    ("https://forge-laboratory.com/en", "https://forge-laboratory.com"),
    (">Change Password</h2>", ">變更密碼</h2>"),
    # Longer phrase first so "New Password" does not leave "Confirm 新密碼"
    ("Confirm New Password :", "確認新密碼 :"),
    ("New Password :", "新密碼 :"),
    (">Update Password</button>", ">更新密碼</button>"),
    ("Password successfully changed.", "密碼已成功變更。"),
    (">Back to Profile</a>", ">返回個人資料</a>"),
    (
        "*At least 8 characters, including letters, numbers, and symbols",
        "*至少 8 個字元，並包含英文字母、數字與符號",
    ),
    ('aria-label="Show password"', 'aria-label="顯示密碼"'),
    ('title="Show password"', 'title="顯示密碼"'),
    ("Hide password", "隱藏密碼"),
    ("Show password", "顯示密碼"),
    ("Please enter a new password.", "請輸入新密碼。"),
    (
        "Password must be at least 8 characters and include letters, numbers, and symbols.",
        "密碼須至少 8 個字元，並包含英文字母、數字與符號。",
    ),
    ("Please confirm your new password.", "請確認新密碼。"),
    ("Passwords do not match.", "密碼不一致。"),
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
    for a, b in PW_REPLACEMENTS:
        text = text.replace(a, b)
    text = text.replace(
        "btnModeToggle.setAttribute('aria-label', isOffice ? 'Switch to Sci-Fi Mode' : 'Switch to Office Mode');",
        "btnModeToggle.setAttribute('aria-label', isOffice ? '切換至 Sci-Fi Mode' : '切換至 Office Mode');",
    )
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
        ("setting/change_password.html", "ja"): (
            "change_password.html",
            "../en/setting/change_password.html",
            "../zh-tw/setting/change_password.html",
        ),
        ("en/setting/change_password.html", "en"): (
            "../../setting/change_password.html",
            "change_password.html",
            "../../zh-tw/setting/change_password.html",
        ),
        ("setting/change_password_success.html", "ja"): (
            "change_password_success.html",
            "../en/setting/change_password_success.html",
            "../zh-tw/setting/change_password_success.html",
        ),
        ("en/setting/change_password_success.html", "en"): (
            "../../setting/change_password_success.html",
            "change_password_success.html",
            "../../zh-tw/setting/change_password_success.html",
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
        "setting/change_password.html",
        "setting/change_password_success.html",
        "en/setting/change_password.html",
        "en/setting/change_password_success.html",
        "zh-tw/setting/change_password.html",
        "zh-tw/setting/change_password_success.html",
        "zh-tw/setting/profile.html",
        "zh-tw/setting/preferences.html",
        "zh-tw/setting/change_email.html",
    ):
        path = ROOT / rel
        if not path.is_file():
            continue
        path.write_text(inject_script(path.read_text(encoding="utf-8")), encoding="utf-8")
        print(f"export inject: {rel}")


def main() -> None:
    build_zh_tw_from_en("change_password.html")
    build_zh_tw_from_en("change_password_success.html")
    wire_ja_en_lang_switchers()
    refresh_chrome_and_export()
    print("build_zh_tw_change_password_pages: OK")


if __name__ == "__main__":
    main()
