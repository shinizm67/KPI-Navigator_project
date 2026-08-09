#!/usr/bin/env python3
"""Create zh-tw Profile (+ Edit) from EN, and wire JA/EN language switchers."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

OPT_TW = "TW - Traditional Chinese"

# Visible EN → zh-TW (Taiwan) replacements for Profile surfaces.
PROFILE_REPLACEMENTS = [
    ("Profile (Fixed) | KPI Pilot | FORGE LABORATORY", "個人資料（檢視） | KPI Pilot | FORGE LABORATORY"),
    ("Profile (Edit) | KPI Pilot | FORGE LABORATORY", "個人資料（編輯） | KPI Pilot | FORGE LABORATORY"),
    ("Profile | KPI Pilot | FORGE LABORATORY", "個人資料 | KPI Pilot | FORGE LABORATORY"),
    ("<html lang=\"en\">", "<html lang=\"zh-TW\">"),
    ('href="style.css"', 'href="../../en/setting/style.css"'),
    ("https://forge-laboratory.com/en", "https://forge-laboratory.com"),
    (">Profile</h2>", ">個人資料</h2>"),
    ("Current workspace", "目前工作區"),
    ("Workspace list", "工作區清單"),
    ("Email Address :", "電子郵件地址 :"),
    ("User ID :", "使用者 ID :"),
    ("Business Name :", "店名 / 服務名稱 :"),
    ("Company Name :", "公司名稱 :"),
    ("Industry :", "產業 :"),
    ("Genre :", "類型 :"),
    ("Country :", "國家 :"),
    ("State / Prefecture :", "縣市 / 州 :"),
    ("City :", "城市 :"),
    ("Currency :", "貨幣 :"),
    ("Time Zone :", "時區 :"),
    ("Main KPIs / Goals :", "主要 KPI / 目標 :"),
    (">Edit</a>", ">編輯</a>"),
    (">Save Profile</button>", ">儲存個人資料</button>"),
    ('aria-label="Select industry"', 'aria-label="選擇產業"'),
    ('aria-label="Select genre"', 'aria-label="選擇類型"'),
    ('aria-label="Select country"', 'aria-label="選擇國家"'),
    ('aria-label="Select state or prefecture"', 'aria-label="選擇縣市或州"'),
    ('aria-label="Select city"', 'aria-label="選擇城市"'),
    ('aria-label="Select currency"', 'aria-label="選擇貨幣"'),
    ('aria-label="Time zone (auto-filled)"', 'aria-label="時區（自動填入）"'),
    ('placeholder="Auto-filled from State / City"', 'placeholder="依縣市 / 城市自動填入"'),
    ('placeholder="Describe the KPIs you want to focus on."', 'placeholder="請描述您想聚焦的 KPI 或目標。"'),
    (">— Select —</option>", ">— 請選擇 —</option>"),
    (">— Select Industry first —</option>", ">— 請先選擇產業 —</option>"),
    (">— Select Country first —</option>", ">— 請先選擇國家 —</option>"),
    (">— Select State first —</option>", ">— 請先選擇縣市 / 州 —</option>"),
    (">Restaurant</option>", ">餐廳</option>"),
    (">Wear Shop</option>", ">服飾店</option>"),
    (">Retail</option>", ">零售</option>"),
    (">Cafe</option>", ">咖啡廳</option>"),
    ("Switch to Office Mode", "切換至 Office Mode"),
    ("Switch to Sci-Fi Mode", "切換至 Sci-Fi Mode"),
    ("Select language", "選擇語言"),
    ("Language options", "語言選項"),
    ("Back to top", "回到頁首"),
]


def _patch_lang_switcher(text: str, *, active: str, url_ja: str, url_en: str, url_zh_tw: str) -> str:
    """Replace footer language control with JA/EN/zh-TW options."""
    act_ja = " lang-option-active" if active == "ja" else ""
    act_en = " lang-option-active" if active == "en" else ""
    act_tw = " lang-option-active" if active == "zh-tw" else ""
    if active == "ja":
        code, name, aria, list_aria = "JP", "Japanese", "言語を選択", "言語オプション"
    elif active == "en":
        code, name, aria, list_aria = "EN", "English", "Select language", "Language options"
    else:
        code, name, aria, list_aria = "TW", "Traditional Chinese", "選擇語言", "語言選項"

    block = f"""  <div class="lang-select-wrap" id="lang-select-wrap" data-url-en="{url_en}" data-url-ja="{url_ja}" data-url-zh-tw="{url_zh_tw}">
    <button type="button" class="lang-select-btn" id="lang-select-btn" aria-expanded="false" aria-haspopup="listbox" aria-label="{aria}">
      <span class="lang-code" aria-hidden="true">{code}</span>
      <span class="lang-name">{name}</span>
      <span class="lang-chevron" aria-hidden="true"></span>
    </button>
    <div class="lang-select-dropdown" id="lang-select-dropdown" role="listbox" aria-label="{list_aria}" hidden>
      <button type="button" class="lang-option lang-option-ja{act_ja}" role="option" data-lang="ja">JP - Japanese</button>
      <button type="button" class="lang-option lang-option-en{act_en}" role="option" data-lang="en">EN - English</button>
      <button type="button" class="lang-option lang-option-zh-tw{act_tw}" role="option" data-lang="zh-tw">{OPT_TW}</button>
    </div>
  </div>"""

    text = re.sub(
        r'[ \t]*<div class="lang-select-wrap" id="lang-select-wrap"[\s\S]*?</div>\s*</div>',
        block,
        text,
        count=1,
    )

    # Ensure click handler resolves zh-tw URLs (preferences-style).
    old = (
        "var urlEn = langWrap.getAttribute('data-url-en');\n"
        "      var urlJa = langWrap.getAttribute('data-url-ja');\n"
        "      var bodyElForLang = document.getElementById('body-el');\n"
        "\n"
        "      langOptions.forEach(function (opt) {\n"
        "        opt.addEventListener('click', function (e) {\n"
        "          e.stopPropagation();\n"
        "          if (bodyElForLang && bodyElForLang.classList.contains('office-mode')) {\n"
        "            sessionStorage.setItem('kpi-office-mode', '1');\n"
        "          }\n"
        "          var lang = this.getAttribute('data-lang');\n"
        "          var href = (lang === 'ja' && urlJa) ? urlJa : (lang === 'en' && urlEn) ? urlEn : null;\n"
        "          if (href) window.location.href = href;\n"
        "        });\n"
        "      });"
    )
    new = (
        "var urlEn = langWrap.getAttribute('data-url-en');\n"
        "      var urlJa = langWrap.getAttribute('data-url-ja');\n"
        "      var urlZhTw = langWrap.getAttribute('data-url-zh-tw');\n"
        "      var bodyElForLang = document.getElementById('body-el');\n"
        "\n"
        "      langOptions.forEach(function (opt) {\n"
        "        opt.addEventListener('click', function (e) {\n"
        "          e.stopPropagation();\n"
        "          try {\n"
        "            if (bodyElForLang && bodyElForLang.classList.contains('office-mode')) {\n"
        "              sessionStorage.setItem('kpi-office-mode', '1');\n"
        "            }\n"
        "          } catch (_e) {}\n"
        "          var next = this.getAttribute('data-lang');\n"
        "          var href =\n"
        "            next === 'ja' && urlJa\n"
        "              ? urlJa\n"
        "              : next === 'en' && urlEn\n"
        "                ? urlEn\n"
        "                : next === 'zh-tw' && urlZhTw\n"
        "                  ? urlZhTw\n"
        "                  : null;\n"
        "          if (href) window.location.href = href;\n"
        "        });\n"
        "      });"
    )
    if old in text:
        text = text.replace(old, new, 1)
    elif "data-url-zh-tw" not in text or "urlZhTw" not in text:
        # Compact variant without blank line / try
        text = re.sub(
            r"var urlEn = langWrap\.getAttribute\('data-url-en'\);\s*"
            r"var urlJa = langWrap\.getAttribute\('data-url-ja'\);",
            "var urlEn = langWrap.getAttribute('data-url-en');\n"
            "      var urlJa = langWrap.getAttribute('data-url-ja');\n"
            "      var urlZhTw = langWrap.getAttribute('data-url-zh-tw');",
            text,
            count=1,
        )
        text = re.sub(
            r"var href = \(lang === 'ja' && urlJa\) \? urlJa : \(lang === 'en' && urlEn\) \? urlEn : null;",
            "var href =\n"
            "            lang === 'ja' && urlJa\n"
            "              ? urlJa\n"
            "              : lang === 'en' && urlEn\n"
            "                ? urlEn\n"
            "                : lang === 'zh-tw' && urlZhTw\n"
            "                  ? urlZhTw\n"
            "                  : null;",
            text,
            count=1,
        )
    return text


def _strip_export_script(text: str) -> str:
    return re.sub(
        r"\n?[ \t]*<script>\s*/\* KPI-PL-MEP-EXPORT \*/[\s\S]*?</script>\s*",
        "\n",
        text,
        count=1,
    )


def build_zh_tw_from_en(src_name: str, title_hint: str) -> Path:
    src = ROOT / "en" / "setting" / src_name
    dst = ROOT / "zh-tw" / "setting" / src_name
    text = src.read_text(encoding="utf-8")
    text = _strip_export_script(text)
    for a, b in PROFILE_REPLACEMENTS:
        text = text.replace(a, b)

    # Mode-toggle aria strings in inline JS (EN page).
    text = text.replace(
        "btnModeToggle.setAttribute('aria-label', isOffice ? 'Switch to Sci-Fi Mode' : 'Switch to Office Mode');",
        "btnModeToggle.setAttribute('aria-label', isOffice ? '切換至 Sci-Fi Mode' : '切換至 Office Mode');",
    )

    url_ja = f"../../setting/{src_name}"
    url_en = f"../../en/setting/{src_name}"
    url_zh = src_name
    text = _patch_lang_switcher(
        text, active="zh-tw", url_ja=url_ja, url_en=url_en, url_zh_tw=url_zh
    )

    # Title safety if edit title pattern differs
    if "個人資料" not in text.split("<title>", 1)[-1][:80]:
        text = re.sub(
            r"<title>.*?</title>",
            f"<title>{title_hint}</title>",
            text,
            count=1,
        )

    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text, encoding="utf-8")
    print(f"wrote {dst.relative_to(ROOT)}")
    return dst


def wire_ja_en_lang_switchers() -> None:
    mapping = {
        ("setting/profile.html", "ja"): (
            "profile.html",
            "../en/setting/profile.html",
            "../zh-tw/setting/profile.html",
        ),
        ("en/setting/profile.html", "en"): (
            "../../setting/profile.html",
            "profile.html",
            "../../zh-tw/setting/profile.html",
        ),
        ("setting/profile_edit.html", "ja"): (
            "profile_edit.html",
            "../en/setting/profile_edit.html",
            "../zh-tw/setting/profile_edit.html",
        ),
        ("en/setting/profile_edit.html", "en"): (
            "../../setting/profile_edit.html",
            "profile_edit.html",
            "../../zh-tw/setting/profile_edit.html",
        ),
    }
    for (rel, active), (url_ja, url_en, url_zh) in mapping.items():
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")
        text = _patch_lang_switcher(
            text, active=active, url_ja=url_ja, url_en=url_en, url_zh_tw=url_zh
        )
        path.write_text(text, encoding="utf-8")
        print(f"wired lang switcher: {rel}")


def write_zh_tw_index() -> None:
    path = ROOT / "zh-tw" / "setting" / "index.html"
    path.write_text(
        """<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="0; url=profile.html">
  <title>個人資料 | KPI Pilot</title>
  <script>
    (function () {
      try {
        window.location.replace('profile.html');
      } catch (e) {
        window.location.href = 'profile.html';
      }
    })();
  </script>
</head>
<body>
  <p>若未自動導向，請<a href="profile.html">點此前往個人資料</a>。</p>
</body>
</html>
""",
        encoding="utf-8",
    )
    print(f"wrote {path.relative_to(ROOT)}")


def refresh_chrome_and_export() -> None:
    rc = subprocess.call(
        [sys.executable, str(ROOT / "scripts" / "build_site_chrome.py"), "settings"],
        cwd=str(ROOT / "scripts"),
    )
    if rc != 0:
        raise SystemExit(f"build_site_chrome failed: {rc}")
    # Re-inject export client on profile pages (JA/EN/zh-tw).
    from apply_kpi_pl_mep_export import inject_script  # noqa: WPS433

    for rel in (
        "setting/profile.html",
        "setting/profile_edit.html",
        "en/setting/profile.html",
        "en/setting/profile_edit.html",
        "zh-tw/setting/profile.html",
        "zh-tw/setting/profile_edit.html",
        "zh-tw/setting/preferences.html",
    ):
        path = ROOT / rel
        if not path.is_file():
            continue
        text = inject_script(path.read_text(encoding="utf-8"))
        path.write_text(text, encoding="utf-8")
        print(f"export inject: {rel}")


def main() -> None:
    build_zh_tw_from_en("profile.html", "個人資料（檢視） | KPI Pilot | FORGE LABORATORY")
    build_zh_tw_from_en("profile_edit.html", "個人資料（編輯） | KPI Pilot | FORGE LABORATORY")
    write_zh_tw_index()
    wire_ja_en_lang_switchers()
    refresh_chrome_and_export()
    print("build_zh_tw_profile_pages: OK")


if __name__ == "__main__":
    main()
