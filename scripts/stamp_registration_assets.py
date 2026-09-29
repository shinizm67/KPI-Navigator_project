#!/usr/bin/env python3
"""Stamp Registration / Plan / Change Password / Change Email / Preferences / Unsubscribe page script URLs with a content hash (?v=<sha256[:12]>).

JS is served with a 7-day cache, so every page listed here must request a URL that
changes whenever the script content changes. Run after editing any Registration script,
js/kpi-auth-client.js, js/kpi-plan-cta.js, js/kpi-change-password-page.js, js/kpi-change-email-page.js,
js/kpi-marketing-preference.js or js/kpi-unsubscribe-page.js
(build_zh_tw_public_pages.py runs it for zh-tw register).

  python scripts/stamp_registration_assets.py          # rewrite
  python scripts/stamp_registration_assets.py --check  # exit 1 if any page is stale
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# page -> {src attribute value without query: repo file}
PAGES = {
    "register/registration_si-fi_jp/registration_si-fi_jp.html": {
        "../../js/kpi-auth-client.js": "js/kpi-auth-client.js",
        "../script.js": "register/script.js",
    },
    "en/register/registration_si-fi_en.html": {
        "../../js/kpi-auth-client.js": "js/kpi-auth-client.js",
        "script.js": "en/register/script.js",
    },
    "zh-tw/register/registration_si-fi_zh-tw.html": {
        "../../js/kpi-auth-client.js": "js/kpi-auth-client.js",
        "script.js": "zh-tw/register/script.js",
    },
    "plan/index.html": {"../js/kpi-plan-cta.js": "js/kpi-plan-cta.js"},
    "en/plan/index.html": {"../../js/kpi-plan-cta.js": "js/kpi-plan-cta.js"},
    "zh-tw/plan/index.html": {"../../js/kpi-plan-cta.js": "js/kpi-plan-cta.js"},
    "setting/change_password.html": {"../js/kpi-change-password-page.js": "js/kpi-change-password-page.js"},
    "setting/change_password_success.html": {"../js/kpi-change-password-page.js": "js/kpi-change-password-page.js"},
    "en/setting/change_password.html": {"../../js/kpi-change-password-page.js": "js/kpi-change-password-page.js"},
    "en/setting/change_password_success.html": {"../../js/kpi-change-password-page.js": "js/kpi-change-password-page.js"},
    "zh-tw/setting/change_password.html": {"../../js/kpi-change-password-page.js": "js/kpi-change-password-page.js"},
    "zh-tw/setting/change_password_success.html": {"../../js/kpi-change-password-page.js": "js/kpi-change-password-page.js"},
    "setting/change_email_edit.html": {"../js/kpi-change-email-page.js": "js/kpi-change-email-page.js"},
    "en/setting/change_email_edit.html": {"../../js/kpi-change-email-page.js": "js/kpi-change-email-page.js"},
    "zh-tw/setting/change_email_edit.html": {"../../js/kpi-change-email-page.js": "js/kpi-change-email-page.js"},
    **{
        f"{prefix}setting/{page}": {f"{up}js/kpi-delete-account-page.js": "js/kpi-delete-account-page.js"}
        for prefix, up in (("", "../"), ("en/", "../../"), ("zh-tw/", "../../"))
        for page in ("delete_account4-1.html", "delete_account5.html", "delete_account_accomplished.html")
    },
    **{
        f"{prefix}setting/preferences.html": {f"{up}js/kpi-marketing-preference.js": "js/kpi-marketing-preference.js"}
        for prefix, up in (("", "../"), ("en/", "../../"), ("zh-tw/", "../../"))
    },
    **{
        f"{prefix}unsubscribe/index.html": {f"{up}js/kpi-unsubscribe-page.js": "js/kpi-unsubscribe-page.js"}
        for prefix, up in (("", "../"), ("en/", "../../"), ("zh-tw/", "../../"))
    },
}


def asset_version(rel: str) -> str:
    data = (ROOT / rel).read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()[:12]


def stamp_text(text: str, refs: dict[str, str]) -> str:
    for src, rel in refs.items():
        pattern = re.compile(r'(<script src=")' + re.escape(src) + r'(?:\?v=[^"]*)?(")')
        if len(pattern.findall(text)) != 1:
            raise SystemExit(f"expected exactly one <script src=\"{src}\">")
        text = pattern.sub(lambda m: m.group(1) + src + "?v=" + asset_version(rel) + m.group(2), text)
    return text


def stamp_page(page: str, check: bool = False) -> bool:
    """Returns True when the page is (or was) out of date."""
    path = ROOT / page
    raw = path.read_bytes()
    crlf = b"\r\n" in raw
    text = raw.decode("utf-8").replace("\r\n", "\n")
    new = stamp_text(text, PAGES[page])
    stale = new != text
    if stale and not check:
        out = new.replace("\n", "\r\n") if crlf else new
        path.write_bytes(out.encode("utf-8"))
    return stale


def main() -> int:
    check = "--check" in sys.argv
    stale = [p for p in PAGES if stamp_page(p, check=check)]
    for p in stale:
        print(("STALE " if check else "stamped ") + p)
    if check and stale:
        return 1
    print("registration assets: " + ("up to date" if not stale or not check else "stale"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
