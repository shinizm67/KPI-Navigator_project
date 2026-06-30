#!/usr/bin/env python3
"""Daily FW — sticky date header (scroll body keeps Monthly/Annual reachable)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from daily_overlay_sticky_head_client import (  # noqa: E402
    HTML_PANEL_OPEN_NEW_EN,
    HTML_PANEL_OPEN_NEW_JA,
    HTML_PANEL_OPEN_OLD,
    HTML_SCROLL_CLOSE_NEW,
    HTML_SCROLL_CLOSE_OLD,
    HTML_SCROLL_OPEN_NEW,
    HTML_SCROLL_OPEN_OLD,
    OPEN_ANNUAL_NEW,
    OPEN_ANNUAL_OLD,
    OPEN_MONTHLY_NEW,
    OPEN_MONTHLY_OLD,
    PANEL_CSS_ANNUAL_NEW,
    PANEL_CSS_ANNUAL_OLD,
    PANEL_CSS_MONTHLY_NEW,
    PANEL_CSS_MONTHLY_OLD,
    RESET_FN_MONTHLY,
    RESET_FN_MONTHLY_OLD,
    STICKY_CSS_BLOCK,
    STICKY_HEAD_END,
    STICKY_HEAD_MARKER,
)

PAGES = [
    (ROOT / "app/annual/index.html", "ja", "annual"),
    (ROOT / "en/app/annual/index.html", "en", "annual"),
    (ROOT / "app/monthly/index.html", "ja", "monthly"),
    (ROOT / "en/app/monthly/index.html", "en", "monthly"),
]


def patch_html(text: str, lang: str) -> str:
    if "daily-overlay__sticky-head" in text:
        return text
    panel_new = HTML_PANEL_OPEN_NEW_JA if lang == "ja" else HTML_PANEL_OPEN_NEW_EN
    if HTML_PANEL_OPEN_OLD not in text:
        raise SystemExit("daily overlay panel open HTML miss")
    text = text.replace(HTML_PANEL_OPEN_OLD, panel_new, 1)
    if HTML_SCROLL_OPEN_OLD not in text:
        raise SystemExit("daily overlay scroll open HTML miss")
    text = text.replace(HTML_SCROLL_OPEN_OLD, HTML_SCROLL_OPEN_NEW, 1)
    if HTML_SCROLL_CLOSE_OLD not in text:
        raise SystemExit("daily overlay scroll close HTML miss")
    return text.replace(HTML_SCROLL_CLOSE_OLD, HTML_SCROLL_CLOSE_NEW, 1)


def patch_panel_css(text: str, page_kind: str) -> str:
    pattern = re.compile(
        re.escape(STICKY_HEAD_MARKER) + r"[\s\S]*?" + re.escape(STICKY_HEAD_END) + r"\n?"
    )
    if STICKY_HEAD_MARKER in text:
        text = pattern.sub(STICKY_CSS_BLOCK.rstrip() + "\n", text, count=1)
        while text.count(STICKY_HEAD_MARKER) > 1:
            text = pattern.sub("", text, count=1)
    elif page_kind == "monthly":
        if PANEL_CSS_MONTHLY_OLD not in text:
            raise SystemExit("monthly daily overlay panel CSS miss")
        text = text.replace(PANEL_CSS_MONTHLY_OLD, PANEL_CSS_MONTHLY_NEW, 1)
    else:
        if PANEL_CSS_ANNUAL_OLD not in text:
            raise SystemExit("annual daily overlay panel CSS miss")
        text = text.replace(PANEL_CSS_ANNUAL_OLD, PANEL_CSS_ANNUAL_NEW, 1)
    anchor = "    .daily-overlay__head {"
    if anchor not in text:
        raise SystemExit("daily overlay head CSS anchor miss")
    if STICKY_HEAD_MARKER not in text:
        text = text.replace(anchor, STICKY_CSS_BLOCK + "\n    .daily-overlay__head {", 1)
    return text


def patch_open_js(text: str, page_kind: str) -> str:
    if "resetDailyOverlayScroll" in text:
        return text
    if page_kind == "monthly":
        if RESET_FN_MONTHLY_OLD not in text:
            raise SystemExit("monthly daily overlay open() miss")
        text = text.replace(RESET_FN_MONTHLY_OLD, RESET_FN_MONTHLY, 1)
        if OPEN_MONTHLY_OLD not in text:
            raise SystemExit("monthly daily overlay fill/open tail miss")
        return text.replace(OPEN_MONTHLY_OLD, OPEN_MONTHLY_NEW, 1)
    if OPEN_ANNUAL_OLD not in text:
        raise SystemExit("annual daily overlay open() miss")
    return text.replace(OPEN_ANNUAL_OLD, OPEN_ANNUAL_NEW, 1)


def patch_panel_vars(text: str) -> str:
    text = text.replace(
        "--daily-overlay-sticky-h: 104px;",
        "--daily-overlay-sticky-h: 74px;\n      --daily-overlay-daily-kpi-top: 32px;",
    )
    text = text.replace(
        "--daily-overlay-sticky-h: 84px;",
        "--daily-overlay-sticky-h: 74px;",
    )
    text = text.replace(
        "--daily-overlay-sticky-h: 64px;",
        "--daily-overlay-sticky-h: 74px;",
    )
    text = text.replace(
        "--daily-overlay-daily-kpi-top: 22px;",
        "--daily-overlay-daily-kpi-top: 32px;",
    )
    text = text.replace(
        "--daily-overlay-daily-kpi-top: 42px;",
        "--daily-overlay-daily-kpi-top: 32px;",
    )
    if "--daily-overlay-daily-kpi-top:" not in text:
        text = text.replace(
            "--daily-overlay-sticky-h: 74px;",
            "--daily-overlay-sticky-h: 74px;\n      --daily-overlay-daily-kpi-top: 32px;",
            1,
        )
    return text


def patch_page(path: Path, lang: str, page_kind: str) -> None:
    text = path.read_text(encoding="utf-8")
    text = patch_html(text, lang)
    text = patch_panel_css(text, page_kind)
    text = patch_panel_vars(text)
    text = patch_open_js(text, page_kind)
    if STICKY_HEAD_MARKER not in text:
        raise SystemExit(f"sticky head CSS not applied: {path}")
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> int:
    for path, lang, kind in PAGES:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_page(path, lang, kind)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
