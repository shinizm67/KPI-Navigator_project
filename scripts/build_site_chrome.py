#!/usr/bin/env python3
"""Inject canonical Global Menu header + footer into pages (single source).

First run replaces the existing `<header class="site-header">…</header>` and
`<footer class="site-footer">…</footer>` blocks with marker-wrapped generated
markup. Subsequent runs replace only the content between markers.

Page-specific `<script src>` tags that live inside the header marker are kept.
A shared chrome script is replaced only when the page tag matches the generated
file and query. A different query, or a script the template does not emit, stays
on the page. The header download/auth inline script is always the generated one.

Rollout is staged via PAGES groups: app (annual/monthly/profit), settings, and
public (login/register/plan/legal). Generated pages (monthly/edit, PL) are still
integrated into their own build scripts in a later increment.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from site_chrome import (
    FOOTER_MARK_END,
    FOOTER_MARK_START,
    HEADER_MARK_END,
    HEADER_MARK_START,
    build_footer,
    build_header,
    build_public_footer,
    build_public_header,
)

ROOT = Path(__file__).resolve().parents[1]

# Pilot group: hand-authored app body pages (annual / monthly / profit, JA+EN).
# base = path to language root; img = path to repo-root images/.
# daily: "overlay" = page hosts the Daily floating window (annual/monthly);
#        "link"    = page navigates to Annual for Daily (profit).
# Profit-nav label is canonical (考察 / Insight) for every page — no per-page
# override (the old en/profit "Profit" drift was retired 2026-07-17).
PAGES_APP = [
    {"path": "app/home/index.html", "lang": "ja", "base": "../../", "img": "../../", "active": "home", "daily": "link"},
    {"path": "app/annual/index.html", "lang": "ja", "base": "../../", "img": "../../", "active": "annual", "daily": "overlay"},
    {"path": "app/monthly/index.html", "lang": "ja", "base": "../../", "img": "../../", "active": "monthly", "daily": "overlay"},
    {"path": "app/profit/index.html", "lang": "ja", "base": "../../", "img": "../../", "active": None, "daily": "link"},
    {"path": "app/booking/index.html", "lang": "ja", "base": "../../", "img": "../../", "active": None, "daily": "link"},
    {"path": "en/app/home/index.html", "lang": "en", "base": "../../", "img": "../../../", "active": "home", "daily": "link"},
    {"path": "en/app/annual/index.html", "lang": "en", "base": "../../", "img": "../../../", "active": "annual", "daily": "overlay"},
    {"path": "zh-tw/app/home/index.html", "lang": "zh-tw", "base": "../../", "img": "../../../", "active": "home", "daily": "link"},
    {"path": "zh-tw/app/annual/index.html", "lang": "zh-tw", "base": "../../", "img": "../../../", "active": "annual", "daily": "overlay"},
    {"path": "en/app/monthly/index.html", "lang": "en", "base": "../../", "img": "../../../", "active": "monthly", "daily": "overlay"},
    {"path": "zh-tw/app/monthly/index.html", "lang": "zh-tw", "base": "../../", "img": "../../../", "active": "monthly", "daily": "overlay"},
    {"path": "en/app/profit/index.html", "lang": "en", "base": "../../", "img": "../../../", "active": None, "daily": "link"},
    {"path": "en/app/booking/index.html", "lang": "en", "base": "../../", "img": "../../../", "active": None, "daily": "link"},
    {"path": "zh-tw/app/profit/index.html", "lang": "zh-tw", "base": "../../", "img": "../../../", "active": None, "daily": "link"},
    {"path": "zh-tw/app/booking/index.html", "lang": "zh-tw", "base": "../../", "img": "../../../", "active": None, "daily": "link"},
]

# Settings pages share ONE canonical chrome (unified with the app header).
# Each maps to the account-popup item it should mark as current. Settings pages
# host no Daily overlay, so daily = "link" (navigate to Annual).
_SETTINGS_CURRENT = [
    ("profile.html", "profile"),
    ("profile_edit.html", "profile"),
    ("preferences.html", "preferences"),
    ("change_email.html", "change_email"),
    ("change_email_edit.html", "change_email"),
    ("change_password.html", "change_password"),
    ("change_password_success.html", "change_password"),
    ("session_management.html", "session"),
    ("plan_details.html", "plan_details"),
    ("change_plan.html", "change_plan"),
    ("delete_account1.html", "delete"),
    ("delete_account2.html", "delete"),
    ("delete_account3.html", "delete"),
    ("delete_account4-1.html", "delete"),
    ("delete_account4-2.html", "delete"),
    ("delete_account5.html", "delete"),
    ("delete_account_accomplished.html", "delete"),
]


def _settings_pages() -> list[dict]:
    pages = []
    for fname, current in _SETTINGS_CURRENT:
        pages.append({
            "path": f"setting/{fname}", "lang": "ja", "base": "../", "img": "../",
            "active": None, "daily": "link", "account_current": current,
        })
        pages.append({
            "path": f"en/setting/{fname}", "lang": "en", "base": "../", "img": "../../",
            "active": None, "daily": "link", "account_current": current,
        })
        zh_rel = f"zh-tw/setting/{fname}"
        if (ROOT / zh_rel).is_file():
            pages.append({
                "path": zh_rel, "lang": "zh-tw", "base": "../", "img": "../../",
                "active": None, "daily": "link", "account_current": current,
            })
    return pages


PAGES_SETTINGS = _settings_pages()

# Public (pre-login) pages share the minimal `variant="public"` chrome (logo +
# mode toggle, no nav, no account popup). base is unused for these; img is the
# path to the repo-root images/ dir. The orphan root-level
# `registration_si-fi_en.html` is intentionally excluded (not linked anywhere;
# lacks the mode-toggle JS ids) — flagged as a deletion candidate instead.
PAGES_PUBLIC = [
    {"path": "login/index.html", "lang": "ja", "img": "../", "variant": "public"},
    {"path": "en/login/index.html", "lang": "en", "img": "../../", "variant": "public"},
    {"path": "zh-tw/login/index.html", "lang": "zh-tw", "img": "../../", "variant": "public"},
    {"path": "plan/index.html", "lang": "ja", "img": "../", "variant": "public"},
    {"path": "en/plan/index.html", "lang": "en", "img": "../../", "variant": "public"},
    {"path": "zh-tw/plan/index.html", "lang": "zh-tw", "img": "../../", "variant": "public"},
    {"path": "legal/terms/index.html", "lang": "ja", "img": "../../", "variant": "public"},
    {"path": "legal/privacy/index.html", "lang": "ja", "img": "../../", "variant": "public"},
    {"path": "en/legal/terms/index.html", "lang": "en", "img": "../../../", "variant": "public"},
    {"path": "en/legal/privacy/index.html", "lang": "en", "img": "../../../", "variant": "public"},
    {"path": "zh-tw/legal/terms/index.html", "lang": "zh-tw", "img": "../../../", "variant": "public"},
    {"path": "zh-tw/legal/privacy/index.html", "lang": "zh-tw", "img": "../../../", "variant": "public"},
    {"path": "register/registration_si-fi_jp/registration_si-fi_jp.html", "lang": "ja", "img": "../../", "variant": "public"},
    {"path": "en/register/registration_si-fi_en.html", "lang": "en", "img": "../../", "variant": "public"},
    {"path": "zh-tw/register/registration_si-fi_zh-tw.html", "lang": "zh-tw", "img": "../../", "variant": "public"},
]

# Generated pages that are updated in place here (their own generators are not
# re-runnable / already stripped their source). Header-only (no footer). PL
# `index.html` (JA / EN / ZH-TW header) is owned by build_pl_table_page.py
# and scripts/pl_chrome.py (`pl_header` / `--sync-zh-tw-header`). The PL `shell.html` prototype is
# intentionally left alone, so neither is listed here.
# monthly-edit is a Monthly page (active=monthly) whose Daily/Insight nav are
# deep links back to the Monthly page.
PAGES_GENERATED = [
    {
        "path": "app/monthly/edit/index.html", "lang": "ja",
        "base": "../../../", "img": "../../../", "active": "monthly",
        "daily": "overlay", "daily_href": "../index.html?open=daily",
        "profit_href": "../index.html?open=insight", "footer": False,
    },
    {
        "path": "en/app/monthly/edit/index.html", "lang": "en",
        "base": "../../../", "img": "../../../../", "active": "monthly",
        "daily": "overlay", "daily_href": "../index.html?open=daily",
        "profit_href": "../index.html?open=insight", "footer": False,
    },
    {
        "path": "zh-tw/app/monthly/edit/index.html", "lang": "zh-tw",
        "base": "../../../", "img": "../../../../", "active": "monthly",
        "daily": "overlay", "daily_href": "../index.html?open=daily",
        "profit_href": "../index.html?open=insight", "footer": False,
    },
]

GROUPS = {
    "app": PAGES_APP,
    "settings": PAGES_SETTINGS,
    "public": PAGES_PUBLIC,
    "generated": PAGES_GENERATED,
}


_SCRIPT_RE = re.compile(r"[ \t]*<script\b[^>]*>[\s\S]*?</script>", re.IGNORECASE)
_SRC_RE = re.compile(r"""\bsrc\s*=\s*["']([^"']+)["']""", re.IGNORECASE)


def _script_src(tag: str) -> str | None:
    match = _SRC_RE.search(tag)
    return match.group(1) if match else None


def _script_name_query(src: str) -> tuple[str, str]:
    path, _, query = src.partition("?")
    return path.rsplit("/", 1)[-1], query


def _indent_script(tag: str) -> str:
    lines = tag.strip().split("\n")
    return "\n".join(("    " + line) if line else line for line in lines)


def merge_preserved_header_scripts(old_block: str, new_header: str) -> str:
    """Keep page script tags when replacing a generated header.

    Chrome-owned external scripts (same filename and query as `new_header`)
    follow the template. Anything else already in `old_block` is copied back
    in its previous order: extra files, and shared files pinned to another query.
    """
    old_matches = list(_SCRIPT_RE.finditer(old_block))
    if not old_matches:
        return new_header
    new_matches = list(_SCRIPT_RE.finditer(new_header))
    if not new_matches:
        return new_header

    generated_src = []
    generated_inline = []
    for match in new_matches:
        tag = match.group(0).strip()
        if _script_src(tag):
            generated_src.append(tag)
        else:
            generated_inline.append(match.group(0).strip("\n"))
    generated_by_name = {}
    for tag in generated_src:
        name, _query = _script_name_query(_script_src(tag) or "")
        generated_by_name[name] = tag

    merged = []
    seen = set()
    page_inline = []
    for index, match in enumerate(old_matches):
        raw = match.group(0).strip()
        gap = "" if index == 0 else old_block[old_matches[index - 1].end():match.start()]
        blank = "\n\n" in gap
        src = _script_src(raw)
        if not src:
            if "__headerDlBound" not in raw:
                page_inline.append(raw)
            continue
        name, query = _script_name_query(src)
        seen.add(name)
        generated = generated_by_name.get(name)
        if generated is None:
            chosen = raw
        else:
            _gname, generated_query = _script_name_query(_script_src(generated) or "")
            chosen = generated if query == generated_query else raw
        merged.append({"tag": chosen, "blank": blank, "name": name})

    for index, tag in enumerate(generated_src):
        name, _query = _script_name_query(_script_src(tag) or "")
        if name in seen:
            continue
        item = {"tag": tag, "blank": False, "name": name}
        later_name = None
        for later in generated_src[index + 1:]:
            candidate, _query = _script_name_query(_script_src(later) or "")
            if candidate in seen:
                later_name = candidate
                break
        if later_name is None:
            merged.append(item)
        else:
            insert_at = next(i for i, entry in enumerate(merged) if entry["name"] == later_name)
            merged.insert(insert_at, item)
        seen.add(name)

    parts = []
    for entry in merged:
        if entry["blank"] and parts:
            parts.append("")
        parts.append(_indent_script(entry["tag"]))
    parts.extend(generated_inline)
    parts.extend(_indent_script(tag) for tag in page_inline)
    start = new_matches[0].start()
    end = new_matches[-1].end()
    return new_header[:start] + "\n".join(parts) + new_header[end:]


def _replace_block(text: str, start: str, end: str, raw_re: str, replacement: str, label: str, path: Path) -> str:
    marked = re.compile(r"[ \t]*" + re.escape(start) + r"[\s\S]*?" + re.escape(end))
    if marked.search(text):
        return marked.sub(lambda _m: replacement, text, count=1)
    raw = re.compile(raw_re)
    if not raw.search(text):
        raise SystemExit(f"{path}: {label} block not found (neither markers nor raw)")
    return raw.sub(lambda _m: replacement, text, count=1)


def _marked_span(text: str, start: str, end: str) -> str | None:
    marked = re.compile(r"[ \t]*" + re.escape(start) + r"[\s\S]*?" + re.escape(end))
    match = marked.search(text)
    return match.group(0) if match else None


def render_page(cfg: dict, text: str, path: Path) -> str:
    if cfg.get("variant") == "public":
        header = build_public_header(cfg["lang"], cfg["img"])
    else:
        header = build_header(
            cfg["lang"], cfg["base"], cfg["img"], cfg["active"],
            daily_mode=cfg.get("daily", "overlay"),
            profit_label=cfg.get("profit_label"),
            account_current=cfg.get("account_current"),
            header_class=cfg.get("header_class", ""),
            nav_class=cfg.get("nav_class", ""),
            nav_attr=cfg.get("nav_attr", ""),
            daily_href=cfg.get("daily_href"),
            profit_href=cfg.get("profit_href"),
        )
    old_header = _marked_span(text, HEADER_MARK_START, HEADER_MARK_END)
    if old_header:
        header = merge_preserved_header_scripts(old_header, header)
    header_repl = f"  {HEADER_MARK_START}\n{header}\n  {HEADER_MARK_END}"

    text = _replace_block(
        text, HEADER_MARK_START, HEADER_MARK_END,
        r'[ \t]*<header class="site-header[^"]*">[\s\S]*?</header>',
        header_repl, "header", path,
    )
    # Some pages (generated monthly-edit / PL shells) have no footer.
    if cfg.get("footer", True):
        footer = (
            build_public_footer(cfg["lang"], cfg["img"])
            if cfg.get("variant") == "public"
            else build_footer(cfg["lang"], cfg["img"])
        )
        footer_repl = f"  {FOOTER_MARK_START}\n{footer}\n  {FOOTER_MARK_END}"
        text = _replace_block(
            text, FOOTER_MARK_START, FOOTER_MARK_END,
            r'[ \t]*<footer class="site-footer">[\s\S]*?</footer>',
            footer_repl, "footer", path,
        )
    return text


def _write_if_changed(path: Path, original: bytes, text: str) -> bool:
    newline = b"\r\n" if b"\r\n" in original else b"\n"
    payload = text.replace("\r\n", "\n").replace("\n", newline.decode("ascii")).encode("utf-8")
    if payload == original:
        return False
    path.write_bytes(payload)
    return True


def patch_page(cfg: dict) -> None:
    path = ROOT / cfg["path"]
    if not path.is_file():
        raise SystemExit(f"missing page: {path}")
    original = path.read_bytes()
    text = original.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
    updated = render_page(cfg, text, path)
    changed = _write_if_changed(path, original, updated)
    print(f"{'patched' if changed else 'unchanged'} {cfg['path']}")


def main(argv: list[str]) -> int:
    groups = argv[1:] or ["app"]
    for g in groups:
        if g not in GROUPS:
            print(f"unknown group: {g} (available: {', '.join(GROUPS)})", file=sys.stderr)
            return 2
    for g in groups:
        for cfg in GROUPS[g]:
            patch_page(cfg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
