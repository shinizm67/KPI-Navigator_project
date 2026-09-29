# -*- coding: utf-8 -*-
"""BR-LAUNCH-09 Extension M3 — Marketing opt-in UI contract (static checks).

Registration checkbox (optional, default OFF, separate from Terms, shown only for the matching wording version),
Preferences row (server state first, explicit ON / OFF, immediate), unsubscribe confirmation page (no state change on
open, POST with the token in the body, no login, no referrer). JP / EN / ZH-TW share one contract."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAILED = 0
PASSED = 0


def check(name: str, cond: bool, detail: str = "") -> None:
    global FAILED, PASSED
    if cond:
        PASSED += 1
        print(f"PASS  {name}")
    else:
        FAILED += 1
        print(f"FAIL  {name}" + (f" — {detail}" if detail else ""))


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def tag(html: str, id_: str) -> str:
    m = re.search(r"<[a-z]+[^>]*\bid=\"%s\"[^>]*>" % re.escape(id_), html)
    return m.group(0) if m else ""


def main() -> int:
    mk = read("api/v1/_marketing.php")
    version = re.search(r"const KPI_MARKETING_CONSENT_VERSION = '([^']+)';", mk).group(1)
    block = re.search(r"'%s' => \[(.*?)\]," % re.escape(version), mk, re.S).group(1)
    texts = dict(re.findall(r"'(ja|en|zh-TW)' => '([^']+)'", block))
    check("server keeps one fixed sentence per locale for the current version", sorted(texts) == ["en", "ja", "zh-TW"], str(texts))

    langs = {
        "ja": ("register/registration_si-fi_jp/registration_si-fi_jp.html", "register/script.js", "setting/preferences.html",
               "unsubscribe/index.html", "（任意）", "'ja'"),
        "en": ("en/register/registration_si-fi_en.html", "en/register/script.js", "en/setting/preferences.html",
               "en/unsubscribe/index.html", " (optional)", "'en'"),
        "zh-TW": ("zh-tw/register/registration_si-fi_zh-tw.html", "zh-tw/register/script.js", "zh-tw/setting/preferences.html",
                  "zh-tw/unsubscribe/index.html", "（選填）", "'zh-TW'"),
    }
    for loc, (reg, js, pref, unsub, mark, jsloc) in langs.items():
        rh, rj, ph, uh = read(reg), read(js), read(pref), read(unsub)
        wrap, box = tag(rh, "marketing-optin-wrap"), tag(rh, "marketing-optin")
        check(f"[{loc}] registration: opt-in block hidden until the server version matches; version = {version}",
              " hidden" in wrap and f'data-marketing-version="{version}"' in wrap)
        check(f"[{loc}] registration: checkbox default OFF, not required, not the Terms checkbox",
              box and "checked" not in box and "required" not in box and 'name="marketing_opt_in"' in box)
        check(f"[{loc}] registration: wording = server sentence + optional marker",
              f'{texts[loc]}<span class="form-marketing-optional">{mark}</span>' in rh)
        check(f"[{loc}] registration script: shown only if status.marketingConsentVersion === page version; reset to OFF",
              "d.marketingConsentVersion === pageVersion" in rj and "marketingBox.checked = false;" in rj)
        check(f"[{loc}] registration script: marketing fields only when offered + checked; Register gate unchanged",
              "var marketingOptIn = marketingOffered() && marketingBox.checked;" in rj and "extra.marketingOptIn = true;" in rj
              and f"extra.marketingLocale = {jsloc};" in rj and "marketingOptIn: marketingOptIn" not in rj
              and "btnRegister.disabled = !(registrationOpen && emailOk && passwordOk && confirmOk && agreed);" in rj)
        check(f"[{loc}] registration script: marketing_consent_outdated handled (reload message)", "'marketing_consent_outdated'" in rj)
        check(f"[{loc}] registration script cache-bust = content hash", re.search(r'script\.js\?v=[0-9a-f]{12}"', rh) is not None)

        row, pbox = tag(ph, "pref-marketing-row"), tag(ph, "pref-marketing")
        check(f"[{loc}] preferences: newsletter row hidden until the server state is known; version = {version}",
              " hidden" in row and f'data-marketing-version="{version}"' in row)
        check(f"[{loc}] preferences: checkbox has no default state; wording = server sentence",
              pbox and "checked" not in pbox and f'<span class="form-agreement-text">{texts[loc]}</span>' in ph)
        check(f"[{loc}] preferences: row inside the existing Preferences form group (no new page); script loaded",
              ph.find('id="pref-marketing-row"') > ph.find('id="pref-tutorial"') > 0
              and re.search(r"js/kpi-marketing-preference\.js\?v=[0-9a-f]{12}", ph) is not None)

        check(f"[{loc}] unsubscribe page: no referrer, noindex, no auth client (public, no login redirect)",
              '<meta name="referrer" content="no-referrer">' in uh and 'name="robots" content="noindex, nofollow"' in uh
              and "kpi-auth-client" not in uh and re.search(r"js/kpi-unsubscribe-page\.js\?v=[0-9a-f]{12}", uh) is not None)
        check(f"[{loc}] unsubscribe page: button disabled until a well-formed token; optional reason codes = server list",
              "disabled>" in tag(uh, "btn-unsubscribe") + ">" and all(f'value="{v}"' in uh for v in ["too_many", "not_relevant", "not_requested", "other"])
              and 'maxlength="200"' in uh)

    pj = read("js/kpi-marketing-preference.js")
    check("preferences JS: row shown only after GET ok with a boolean state", "typeof r.data.subscribed !== 'boolean'" in pj and "row.hidden = false;" in pj)
    check("preferences JS: subscribe sends the page's wording version; stale page cannot subscribe",
          "consentTextVersion: pageVersion" in pj and "box.disabled = !subscribed && !versionOk;" in pj)
    check("preferences JS: expected-user guard + stale-tab block; no browser storage",
          "attachExpectedUser" in pj and "assertCanMutateUserData" in pj and "localStorage" not in pj and "sessionStorage" not in pj)
    uj = read("js/kpi-unsubscribe-page.js")
    check("unsubscribe JS: nothing sent on open (only the submit handler posts)",
          uj.count("fetch(") == 1 and uj.find("fetch(") > uj.find("form.addEventListener('submit'"))
    check("unsubscribe JS: token in the POST body, no cookies, no referrer, same answer shown for every 200",
          "var body = { token: token };" in uj and "credentials: 'omit'" in uj and "referrerPolicy: 'no-referrer'" in uj
          and "/^[A-Za-z0-9_-]{43}$/" in uj)
    check("unsubscribe JS: no storage, no console output of the token",
          "localStorage" not in uj and "sessionStorage" not in uj and "console." not in uj)

    print(f"\n{PASSED} passed, {FAILED} failed")
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
