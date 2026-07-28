#!/usr/bin/env python3
"""Create zh-tw Session Management from EN, and wire JA/EN language switchers."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_zh_tw_profile_pages import (  # noqa: E402
    _patch_lang_switcher,
    _strip_export_script,
)

SRC_NAME = "session_management.html"

SESSION_REPLACEMENTS = [
    (
        "Session Management | KPI Navigator | FORGE LABORATORY",
        "工作階段管理 | KPI Navigator | FORGE LABORATORY",
    ),
    ("<html lang=\"en\">", "<html lang=\"zh-TW\">"),
    ('href="style.css"', 'href="../../en/setting/style.css"'),
    ("https://forge-laboratory.com/en", "https://forge-laboratory.com"),
    (">Session Management</h2>", ">工作階段管理</h2>"),
    # Coming-soon panel (visible + animation phrases)
    (">Coming soon</p>", ">即將推出</p>"),
    (
        "var phrases = ['Coming soon', 'Work in Progress', 'Under Construction'];",
        "var phrases = ['即將推出', '進行中', '建置中'];",
    ),
    ("textEl.textContent = 'Coming soon';", "textEl.textContent = '即將推出';"),
    ("Current workspace", "目前工作區"),
    ("Workspace list", "工作區清單"),
    ("Switch to Office Mode", "切換至 Office Mode"),
    ("Switch to Sci-Fi Mode", "切換至 Sci-Fi Mode"),
    ("Select language", "選擇語言"),
    ("Language options", "語言選項"),
    ("Back to top", "回到頁首"),
]

LANG_JS = """    (function () {
      var langBtn = document.getElementById('lang-select-btn');
      var langDropdown = document.getElementById('lang-select-dropdown');
      var langOptions = document.querySelectorAll('.lang-option');
      var langWrap = document.getElementById('lang-select-wrap');
      if (!langBtn || !langDropdown || !langWrap) return;
      langBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        var isOpen = !langDropdown.hidden;
        langDropdown.hidden = isOpen;
        langBtn.setAttribute('aria-expanded', !isOpen);
      });
      document.addEventListener('click', function () {
        langDropdown.hidden = true;
        langBtn.setAttribute('aria-expanded', 'false');
      });
      var urlEn = langWrap.getAttribute('data-url-en');
      var urlJa = langWrap.getAttribute('data-url-ja');
      var urlZhTw = langWrap.getAttribute('data-url-zh-tw');
      var bodyElForLang = document.getElementById('body-el');
      langOptions.forEach(function (opt) {
        opt.addEventListener('click', function (e) {
          e.stopPropagation();
          try {
            if (bodyElForLang && bodyElForLang.classList.contains('office-mode')) {
              sessionStorage.setItem('kpi-office-mode', '1');
            }
          } catch (_e) {}
          var next = this.getAttribute('data-lang');
          var href =
            next === 'ja' && urlJa
              ? urlJa
              : next === 'en' && urlEn
                ? urlEn
                : next === 'zh-tw' && urlZhTw
                  ? urlZhTw
                  : null;
          if (href) window.location.href = href;
        });
      });
    })();
"""


def _ensure_lang_ui(text: str, *, active: str, url_ja: str, url_en: str, url_zh_tw: str) -> str:
    """Insert lang switcher + click handler when missing (EN session page)."""
    if 'id="lang-select-wrap"' not in text:
        # Placeholder block; _patch_lang_switcher rewrites attributes/active.
        stub = """  <div class="lang-select-wrap" id="lang-select-wrap" data-url-en="x" data-url-ja="x">
    <button type="button" class="lang-select-btn" id="lang-select-btn" aria-expanded="false" aria-haspopup="listbox" aria-label="Select language">
      <span class="lang-code" aria-hidden="true">EN</span>
      <span class="lang-name">English</span>
      <span class="lang-chevron" aria-hidden="true"></span>
    </button>
    <div class="lang-select-dropdown" id="lang-select-dropdown" role="listbox" aria-label="Language options" hidden>
      <button type="button" class="lang-option lang-option-ja" role="option" data-lang="ja">JP - Japanese</button>
      <button type="button" class="lang-option lang-option-en" role="option" data-lang="en">EN - English</button>
    </div>
  </div>
"""
        if "<!-- KPI-SITE-FOOTER:END -->" in text:
            text = text.replace(
                "<!-- KPI-SITE-FOOTER:END -->",
                "<!-- KPI-SITE-FOOTER:END -->\n\n" + stub,
                1,
            )
        else:
            text = text.replace("</footer>", "</footer>\n\n" + stub, 1)

    text = _patch_lang_switcher(
        text, active=active, url_ja=url_ja, url_en=url_en, url_zh_tw=url_zh_tw
    )

    if "lang-select-btn" in text and "getElementById('lang-select-btn')" not in text:
        # Insert handler before the coming-soon IIFE (or first page script after footer).
        m = re.search(
            r"(<script>\s*\(function \(\) \{\s*var textEl = document\.getElementById\('coming-soon-text'\);)",
            text,
        )
        if m:
            text = text[: m.start()] + "<script>\n" + LANG_JS + "  </script>\n  " + text[m.start() :]
        else:
            # Fallback: before first script after footer end
            idx = text.find("<!-- KPI-SITE-FOOTER:END -->")
            script_idx = text.find("<script>", idx if idx >= 0 else 0)
            if script_idx >= 0:
                text = text[:script_idx] + "<script>\n" + LANG_JS + "  </script>\n  " + text[script_idx:]

    # Upgrade compact JA/EN-only href resolver if still present.
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
    if "urlZhTw" not in text and "data-url-zh-tw" in text:
        text = re.sub(
            r"var urlEn = langWrap\.getAttribute\('data-url-en'\);\s*"
            r"var urlJa = langWrap\.getAttribute\('data-url-ja'\);",
            "var urlEn = langWrap.getAttribute('data-url-en');\n"
            "      var urlJa = langWrap.getAttribute('data-url-ja');\n"
            "      var urlZhTw = langWrap.getAttribute('data-url-zh-tw');",
            text,
            count=1,
        )
    return text


def build_zh_tw_from_en() -> Path:
    src = ROOT / "en" / "setting" / SRC_NAME
    dst = ROOT / "zh-tw" / "setting" / SRC_NAME
    text = _strip_export_script(src.read_text(encoding="utf-8"))
    for a, b in SESSION_REPLACEMENTS:
        text = text.replace(a, b)
    text = text.replace(
        "btnModeToggle.setAttribute('aria-label', isOffice ? 'Switch to Sci-Fi Mode' : 'Switch to Office Mode');",
        "btnModeToggle.setAttribute('aria-label', isOffice ? '切換至 Sci-Fi Mode' : '切換至 Office Mode');",
    )
    text = _ensure_lang_ui(
        text,
        active="zh-tw",
        url_ja=f"../../setting/{SRC_NAME}",
        url_en=f"../../en/setting/{SRC_NAME}",
        url_zh_tw=SRC_NAME,
    )
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text, encoding="utf-8")
    print(f"wrote {dst.relative_to(ROOT)}")
    return dst


def wire_ja_en_lang_switchers() -> None:
    mapping = {
        ("setting/session_management.html", "ja"): (
            SRC_NAME,
            f"../en/setting/{SRC_NAME}",
            f"../zh-tw/setting/{SRC_NAME}",
        ),
        ("en/setting/session_management.html", "en"): (
            f"../../setting/{SRC_NAME}",
            SRC_NAME,
            f"../../zh-tw/setting/{SRC_NAME}",
        ),
    }
    for (rel, active), (url_ja, url_en, url_zh) in mapping.items():
        path = ROOT / rel
        text = _ensure_lang_ui(
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
        f"setting/{SRC_NAME}",
        f"en/setting/{SRC_NAME}",
        f"zh-tw/setting/{SRC_NAME}",
    ):
        path = ROOT / rel
        if not path.is_file():
            continue
        path.write_text(inject_script(path.read_text(encoding="utf-8")), encoding="utf-8")
        print(f"export inject: {rel}")


def main() -> None:
    build_zh_tw_from_en()
    wire_ja_en_lang_switchers()
    refresh_chrome_and_export()
    print("build_zh_tw_session_management_pages: OK")


if __name__ == "__main__":
    main()
