#!/usr/bin/env python3
"""Shared PL Global Menu header (JA / EN / ZH-TW).

`build_pl_table_page.render_page` and `--sync-zh-tw-header` both use
`pl_header()` → `site_chrome.build_header()`. ZH-TW PL has no full page
generator; only the header is synced so the table body is preserved.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
from site_chrome import build_header  # noqa: E402
from build_site_chrome import merge_preserved_header_scripts  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

_PL_HEADER_RE = re.compile(
    r'[ \t]*<header class="site-header[^"]*">[\s\S]*?</header>',
)

PL_PAGE_PATHS = {
    "ja": "app/profit/pl/index.html",
    "en": "en/app/profit/pl/index.html",
    "zh-tw": "zh-tw/app/profit/pl/index.html",
}


def page_paths(lang: str) -> dict[str, str]:
    """Asset root + app URLs from profit/pl/index.html."""
    if lang == "en":
        return {
            "asset": "../../../../",
            "annual": "../../annual/index.html",
            "monthly": "../../monthly/index.html",
            "daily": "#",
            "insight": "../../monthly/index.html?open=insight",
            "insight_basic": "../../../setting/change_plan.html",
            "profit_hub": "../index.html",
            "pl_self": "index.html",
            "monthly_edit": "../../monthly/edit/index.html",
            "lang_en": "index.html",
            "lang_ja": "../../../../app/profit/pl/index.html",
            "setting": "../../../../en/setting/",
            "forge_url": "https://forge-laboratory.com/en",
        }
    if lang == "zh-tw":
        return {
            "asset": "../../../../",
            "annual": "../../annual/index.html",
            "monthly": "../../monthly/index.html",
            "daily": "#",
            "insight": "../../monthly/index.html?open=insight",
            "insight_basic": "../../../setting/change_plan.html",
            "profit_hub": "../index.html",
            "pl_self": "index.html",
            "monthly_edit": "../../monthly/edit/index.html",
            "lang_en": "../../../../en/app/profit/pl/index.html",
            "lang_ja": "../../../../app/profit/pl/index.html",
            "setting": "../../../../zh-tw/setting/",
            "forge_url": "https://forge-laboratory.com/",
        }
    return {
        "asset": "../../../",
        "annual": "../../annual/index.html",
        "monthly": "../../monthly/index.html",
        "daily": "#",
        "insight": "../../monthly/index.html?open=insight",
        "insight_basic": "../../../setting/change_plan.html",
        "profit_hub": "../index.html",
        "pl_self": "index.html",
        "monthly_edit": "../../monthly/edit/index.html",
        "lang_en": "../../../en/app/profit/pl/index.html",
        "lang_ja": "index.html",
        "setting": "../../../en/setting/",
        "forge_url": "https://forge-laboratory.com",
    }


def pl_header(lang: str) -> str:
    """Shared PL Global Menu. Same `build_header()` call for JA / EN / ZH-TW."""
    p = page_paths(lang)
    return build_header(
        lang, "../../../", p["asset"], None,
        daily_mode="overlay",
        header_class="pl-site-header",
        nav_class="pl-header-global-nav",
        nav_attr=' data-pl-nav="1"',
        profit_href=p["insight"],
    )


def apply_pl_header(path: Path, lang: str) -> None:
    """Replace the existing PL `<header>` with `pl_header(lang)`. Body unchanged."""
    original = path.read_bytes()
    text = original.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
    header = pl_header(lang)
    if 'id="header-booking-btn"' not in header:
        raise SystemExit(f"{path}: generated header missing #header-booking-btn")
    match = _PL_HEADER_RE.search(text)
    if not match:
        raise SystemExit(f"{path}: expected 1 PL header, found 0")
    header = merge_preserved_header_scripts(match.group(0), header)
    updated = text[:match.start()] + header + text[match.end():]
    if _PL_HEADER_RE.search(updated) is None:
        raise SystemExit(f"{path}: PL header missing after merge")
    newline = b"\r\n" if b"\r\n" in original else b"\n"
    payload = updated.replace("\n", newline.decode("ascii")).encode("utf-8")
    if payload != original:
        path.write_bytes(payload)
    print("synced PL header", lang, "->", path)


def main(argv: list[str] | None = None) -> None:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv == ["--sync-zh-tw-header"]:
        apply_pl_header(ROOT / PL_PAGE_PATHS["zh-tw"], "zh-tw")
        return
    if argv == ["--sync-headers"]:
        for lang, rel in PL_PAGE_PATHS.items():
            apply_pl_header(ROOT / rel, lang)
        return
    raise SystemExit("usage: pl_chrome.py --sync-zh-tw-header | --sync-headers")


if __name__ == "__main__":
    main()
