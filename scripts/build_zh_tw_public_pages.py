#!/usr/bin/env python3
"""Build zh-tw public periphery pages from EN (login / plan / legal / register / account_protection).

Also:
- expands html[lang=\"ja\"] font overrides → zh-TW in shared CSS
- wires JA/EN language switchers with data-url-zh-tw
- refreshes public chrome via build_site_chrome.py
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPT_TW = "TW - Traditional Chinese"

LOCALE_STYLE = """  <style id="kpi-lang-switcher-locale">
    /* KPI-LANG-SWITCHER-LOCALE: footer shortcut = native + EN only (see docs/lang-switcher-locale-policy.md) */
    html[lang='ja'] .lang-option-zh-tw {
      display: none !important;
    }
    html[lang='zh-TW'] .lang-option-ja,
    html[lang^='zh'] .lang-option-ja {
      display: none !important;
    }
  </style>"""


def _patch_lang_switcher(text: str, *, active: str, url_ja: str, url_en: str, url_zh_tw: str) -> str:
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
    return _patch_lang_js(text)


def _patch_lang_js(text: str) -> str:
    """Ensure click handler resolves zh-tw (login/plan style and register style)."""
    if "urlZhTw" in text and "data-url-zh-tw" in text:
        # Still may need href ternary update
        pass

    # Pattern A: login/plan/legal — lang === 'ja' ? urlJa : lang === 'en' ? urlEn
    text = re.sub(
        r"var urlEn = langWrap(?: && langWrap)?\.getAttribute\('data-url-en'\);\s*"
        r"var urlJa = langWrap(?: && langWrap)?\.getAttribute\('data-url-ja'\);",
        "var urlEn = langWrap && langWrap.getAttribute('data-url-en');\n"
        "        var urlJa = langWrap && langWrap.getAttribute('data-url-ja');\n"
        "        var urlZhTw = langWrap && langWrap.getAttribute('data-url-zh-tw');",
        text,
        count=1,
    )
    # When langWrap is known non-null (plan/legal)
    text = re.sub(
        r"var urlEn = langWrap\.getAttribute\('data-url-en'\);\s*"
        r"var urlJa = langWrap\.getAttribute\('data-url-ja'\);",
        "var urlEn = langWrap.getAttribute('data-url-en');\n"
        "      var urlJa = langWrap.getAttribute('data-url-ja');\n"
        "      var urlZhTw = langWrap.getAttribute('data-url-zh-tw');",
        text,
        count=1,
    )

    # href assignment variants
    text = text.replace(
        "var href = (lang === 'ja' && urlJa) ? urlJa : (lang === 'en' && urlEn) ? urlEn : null;",
        "var href =\n"
        "              lang === 'ja' && urlJa\n"
        "                ? urlJa\n"
        "                : lang === 'en' && urlEn\n"
        "                  ? urlEn\n"
        "                  : lang === 'zh-tw' && urlZhTw\n"
        "                    ? urlZhTw\n"
        "                    : null;",
    )
    # register script.js style
    text = text.replace(
        "var baseUrl = (lang === 'ja' && urlJa) ? urlJa : (lang === 'en' && urlEn) ? urlEn : null;",
        "var baseUrl =\n"
        "          lang === 'ja' && urlJa\n"
        "            ? urlJa\n"
        "            : lang === 'en' && urlEn\n"
        "              ? urlEn\n"
        "              : lang === 'zh-tw' && urlZhTw\n"
        "                ? urlZhTw\n"
        "                : null;",
    )
    # ensure urlZhTw var in register script if only urlEn/urlJa
    if "data-url-zh-tw" in text and "urlZhTw" not in text:
        text = text.replace(
            "var urlEn = wrap && wrap.getAttribute('data-url-en');\n"
            "    var urlJa = wrap && wrap.getAttribute('data-url-ja');",
            "var urlEn = wrap && wrap.getAttribute('data-url-en');\n"
            "    var urlJa = wrap && wrap.getAttribute('data-url-ja');\n"
            "    var urlZhTw = wrap && wrap.getAttribute('data-url-zh-tw');",
            1,
        )
    return text


def expand_ja_font_selectors_in_css(css: str) -> tuple[str, int]:
    """Expand html[lang=\"ja\"] / html[lang='ja'] selectors to also include zh-TW / zh."""
    out: list[str] = []
    pos = 0
    changed = 0
    for rm in re.finditer(r"([^{}@][^{]*)\{([^{}]*)\}", css):
        out.append(css[pos : rm.start()])
        selector, body = rm.group(1), rm.group(2)
        pos = rm.end()
        sel_has_ja = ('html[lang="ja"]' in selector) or ("html[lang='ja']" in selector)
        if not sel_has_ja:
            out.append(rm.group(0))
            continue
        if "zh-TW" in selector or 'lang^="zh"' in selector or "lang^='zh'" in selector:
            out.append(rm.group(0))
            continue
        parts = [p.strip() for p in selector.split(",") if p.strip()]
        extra: list[str] = []
        for p in parts:
            if 'html[lang="ja"]' in p:
                extra.append(p.replace('html[lang="ja"]', 'html[lang="zh-TW"]', 1))
                extra.append(p.replace('html[lang="ja"]', 'html[lang^="zh"]', 1))
            elif "html[lang='ja']" in p:
                extra.append(p.replace("html[lang='ja']", "html[lang='zh-TW']", 1))
                extra.append(p.replace("html[lang='ja']", "html[lang^='zh']", 1))
        if not extra:
            out.append(rm.group(0))
            continue
        lead = re.match(r"^\s*", selector).group(0)
        new_sel = ",\n".join(parts + extra)
        out.append(f"{lead}{new_sel} {{{body}}}")
        changed += 1
    out.append(css[pos:])
    return "".join(out), changed


def patch_shared_css() -> None:
    paths = [
        ROOT / "register" / "style.css",
        ROOT / "en" / "login" / "style.css",
        ROOT / "plan" / "style.css",
        ROOT / "legal" / "terms" / "style.css",
        ROOT / "en" / "legal" / "terms" / "style.css",
    ]
    for path in paths:
        if not path.is_file():
            print(f"skip missing CSS: {path}")
            continue
        src = path.read_text(encoding="utf-8")
        patched, n = expand_ja_font_selectors_in_css(src)
        if n:
            path.write_text(patched, encoding="utf-8")
        print(f"CSS {path.relative_to(ROOT)}: expanded {n} ja→zh font rules")


def apply_common_zh(text: str) -> str:
    reps = [
        ("<html lang=\"en\">", "<html lang=\"zh-TW\">"),
        ("https://forge-laboratory.com/en", "https://forge-laboratory.com"),
        ("FORGE LABORATORY - Top page", "FORGE LABORATORY - 首頁"),
        ("Switch to Office Mode", "切換至 Office Mode"),
        ("Switch to Sci-Fi Mode", "切換至 Sci-Fi Mode"),
        ("Select language", "選擇語言"),
        ("Language options", "語言選項"),
        ("Back to top", "回到頁首"),
        (
            "family=BIZ+UDP+Gothic:wght@400;500;700&family=Orbitron:wght@400;500;600;700&display=swap",
            "family=BIZ+UDP+Gothic:wght@400;500;700&display=swap",
        ),
    ]
    for a, b in reps:
        text = text.replace(a, b)
    return text


def build_login() -> None:
    src = ROOT / "en" / "login" / "index.html"
    dst = ROOT / "zh-tw" / "login" / "index.html"
    text = apply_common_zh(src.read_text(encoding="utf-8"))
    text = text.replace(
        "<title>Log IN | KPI Navigator | FORGE LABORATORY</title>",
        "<title>登入 | KPI Navigator | FORGE LABORATORY</title>",
    )
    text = text.replace('href="../../register/style.css"', 'href="../../register/style.css"')
    text = text.replace('href="style.css"', 'href="../../en/login/style.css"')
    text = text.replace(">Log IN</h2>", ">登入</h2>")
    text = text.replace(
        "<label for=\"user-id\">USER ID / Mail Address :</label>",
        "<label for=\"user-id\">使用者 ID / 電子郵件地址 :</label>",
    )
    text = text.replace(
        "<label for=\"password\">Pass Word :</label>",
        "<label for=\"password\">密碼 :</label>",
    )
    text = text.replace(">Log IN</button>", ">登入</button>")
    text = text.replace(
        "btnModeToggle.setAttribute('aria-label', isOffice ? '切換至 Sci-Fi Mode' : '切換至 Office Mode');",
        "btnModeToggle.setAttribute('aria-label', isOffice ? '切換至 Sci-Fi Mode' : '切換至 Office Mode');",
    )
    text = _patch_lang_switcher(
        text,
        active="zh-tw",
        url_ja="../../login/index.html",
        url_en="../../en/login/index.html",
        url_zh_tw="index.html",
    )
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text, encoding="utf-8")
    print(f"wrote {dst.relative_to(ROOT)}")


def build_plan() -> None:
    src = ROOT / "en" / "plan" / "index.html"
    dst = ROOT / "zh-tw" / "plan" / "index.html"
    text = apply_common_zh(src.read_text(encoding="utf-8"))
    text = text.replace(
        "<title>Plan | KPI Navigator | FORGE LABORATORY</title>",
        "<title>方案 | KPI Navigator | FORGE LABORATORY</title>",
    )
    text = text.replace('href="style.css"', 'href="../../plan/style.css"')
    text = text.replace(">Plan</h2>", ">方案</h2>")
    reps = [
        (">List</th>", ">項目</th>"),
        (">Basic $5/month</th>", ">基本 $5/月</th>"),
        (">Pro $29/month</th>", ">專業 $29/月</th>"),
        ("1. Annual KPI Dashboard", "1. 年度 KPI 儀表板"),
        ("2. Monthly KPI Analysis", "2. 月次 KPI 分析"),
        ("3. Daily Target Tracking", "3. 日次目標追蹤"),
        ("4. Automatic Achievement Calculation", "4. 達成率自動計算"),
        ("5. Seasonality Detection", "5. 季節性偵測"),
        ("6. Business Day Management", "6. 營業日管理"),
        ("7. CSV Data Import (Previous Year)", "7. CSV 資料匯入（前一年）"),
        ("8. Automated Sales Target Engine", "8. 自動銷售目標引擎"),
        ("9. Cost Input (Food & Beverage)", "9. 成本輸入（餐飲）"),
        ("10. Cost Ratio Visualization", "10. 成本比率視覺化"),
        ("11. Profit Structure Visualization", "11. 利潤結構視覺化"),
        ("12. Monthly Profit Analysis Dashboard", "12. 月次利潤分析儀表板"),
        ('aria-label="Included"', 'aria-label="包含"'),
        ('aria-label="Not included"', 'aria-label="不包含"'),
        (
            'href="../register/registration_si-fi_en.html?plan=basic"',
            'href="../register/registration_si-fi_zh-tw.html?plan=basic"',
        ),
        (
            'href="../register/registration_si-fi_en.html?plan=pro"',
            'href="../register/registration_si-fi_zh-tw.html?plan=pro"',
        ),
        (">Register Basic</a>", ">註冊基本方案</a>"),
        (">Register Pro</a>", ">註冊專業方案</a>"),
    ]
    for a, b in reps:
        text = text.replace(a, b)
    text = _patch_lang_switcher(
        text,
        active="zh-tw",
        url_ja="../../plan/index.html",
        url_en="../../en/plan/index.html",
        url_zh_tw="index.html",
    )
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text, encoding="utf-8")
    print(f"wrote {dst.relative_to(ROOT)}")


def build_account_protection() -> None:
    # account_protection.html
    src = ROOT / "en" / "account_protection" / "account_protection.html"
    dst = ROOT / "zh-tw" / "account_protection" / "account_protection.html"
    text = apply_common_zh(src.read_text(encoding="utf-8"))
    text = text.replace(
        "<title>Account Protection | KPI Navigator | FORGE LABORATORY</title>",
        "<title>帳戶保護 | KPI Navigator | FORGE LABORATORY</title>",
    )
    text = text.replace('href="../../register/style.css"', 'href="../../register/style.css"')
    text = text.replace('href="../setting/style.css"', 'href="../../en/setting/style.css"')
    text = text.replace(">Security protection flow</h3>", ">帳戶保護流程</h3>")
    text = text.replace(
        ">This page is reserved for account recovery actions.</p>",
        ">此頁面保留供帳戶復原相關操作使用。</p>",
    )
    text = text.replace(
        ">Implementation will include password reset, session revocation, and support escalation.</p>",
        ">未來將實作密碼重設、工作階段撤銷，以及支援升級流程。</p>",
    )
    text = text.replace(">Back</a>", ">返回</a>")
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text, encoding="utf-8")
    print(f"wrote {dst.relative_to(ROOT)}")

    # defensive_protocol.html
    src2 = ROOT / "en" / "account_protection" / "defensive_protocol.html"
    dst2 = ROOT / "zh-tw" / "account_protection" / "defensive_protocol.html"
    text = apply_common_zh(src2.read_text(encoding="utf-8"))
    text = text.replace(
        "<title>Defensive Protocol | KPI Navigator | FORGE LABORATORY</title>",
        "<title>防護通訊協定 | KPI Navigator | FORGE LABORATORY</title>",
    )
    text = text.replace('href="../setting/style.css"', 'href="../../en/setting/style.css"')
    reps = [
        (">Another device is currently signed in</h3>", ">目前已有其他裝置登入</h3>"),
        (
            ">This account is currently in use on another device.</p>",
            ">此帳戶目前正在其他裝置上使用中。</p>",
        ),
        (
            ">To continue on this device, please verify your identity via email.</p>",
            ">若要在此裝置繼續使用，請透過電子郵件驗證身分。</p>",
        ),
        (">Verify via Email</button>", ">以電子郵件驗證</button>"),
        (
            ">If this wasn't you, please contact support.</a>",
            ">若這不是您本人的操作，請聯絡支援。</a>",
        ),
        (">This wasn't me</a>", ">這不是我</a>"),
        (
            "Verification email has been sent. Please check your inbox.",
            "驗證郵件已寄出。請檢查您的收件匣。",
        ),
    ]
    for a, b in reps:
        text = text.replace(a, b)
    dst2.write_text(text, encoding="utf-8")
    print(f"wrote {dst2.relative_to(ROOT)}")


def build_legal_terms() -> None:
    src = ROOT / "en" / "legal" / "terms" / "index.html"
    dst = ROOT / "zh-tw" / "legal" / "terms" / "index.html"
    text = apply_common_zh(src.read_text(encoding="utf-8"))
    text = text.replace(
        "<title>Terms of Service | KPI Navigator | FORGE LABORATORY</title>",
        "<title>服務條款 | KPI Navigator | FORGE LABORATORY</title>",
    )
    text = text.replace('href="style.css"', 'href="../../../legal/terms/style.css"')
    text = text.replace('href="../../../register/style.css"', 'href="../../../register/style.css"')

    # Replace main content block
    main_zh = """    <main class="terms-content">
      <h1 class="terms-title">服務條款（KPI Navigator）</h1>
      <p class="terms-meta">最後更新：2026年2月16日<br>營運者：Forge-Lab（由松下真一郎營運）（下稱「本公司」）</p>

      <section class="terms-section">
        <h2>1. 適用範圍</h2>
        <p>本條款規範您對 KPI Navigator（下稱「本服務」）的存取與使用。一旦建立帳戶、存取或使用本服務，即表示您同意受本條款與隱私權政策拘束。</p>
      </section>

      <section class="terms-section">
        <h2>2. 商業用途</h2>
        <p>本服務旨在供商業用途使用（包括公司與以商業身分行事的個人事業主）。</p>
      </section>

      <section class="terms-section">
        <h2>3. 帳戶註冊</h2>
        <p>註冊時您必須提供正確資訊。若有詐欺、濫用或重大違反本條款之情事，本公司得拒絕或暫停帳戶。</p>
      </section>

      <section class="terms-section">
        <h2>4. 帳戶安全</h2>
        <p>您有責任保管登入憑證，並對帳戶下之一切活動負責。</p>
      </section>

      <section class="terms-section">
        <h2>5. 費用與帳單</h2>
        <p>費用、帳單週期與取消條件會顯示於價格與結帳頁面。付款可能經由第三方處理業者（例如 Stripe）處理。</p>
      </section>

      <section class="terms-section">
        <h2>6. 取消</h2>
        <p>您可依本服務提供的方式取消訂閱。除強制性法律另有規定外，費用不予退還且不按比例計算。</p>
      </section>

      <section class="terms-section">
        <h2>7. 禁止行為</h2>
        <p>您不得：</p>
        <ul>
          <li>嘗試未經授權存取、利用漏洞或以其他方式干擾本服務</li>
          <li>侵害智慧財產權或違反法令</li>
          <li>將本服務用於不法或有害活動</li>
          <li>逆向工程、複製或轉售本服務（法律允許者除外）</li>
        </ul>
      </section>

      <section class="terms-section">
        <h2>8. 智慧財產權</h2>
        <p>本公司保留本服務及相關智慧財產之一切權利、所有權與利益。</p>
      </section>

      <section class="terms-section">
        <h2>9. 您的資料</h2>
        <p>您保留所輸入業務資料的所有權。您授予本公司有限授權，僅為提供與改善本服務、防止詐欺與提供支援之目的，依隱私權政策所述託管、處理與顯示您的資料。</p>
      </section>

      <section class="terms-section">
        <h2>10. 非顧問意見；無保證</h2>
        <p>本服務依輸入與設定邏輯提供工具與輸出結果。其並非財務、法律、稅務、投資或商業顧問意見。您須自行對依本服務所做決策負責。本服務按「現況」與「現有」提供，不附任何種類之保證。</p>
      </section>

      <section class="terms-section">
        <h2>11. 責任限制</h2>
        <p>在法律允許的最大範圍內：</p>
        <ul>
          <li>本公司不對任何間接、附帶、特殊、衍生性或懲罰性損害，或任何利潤、營收或資料損失負責。</li>
          <li>本公司因本服務所生或相關之總責任，不得超過引起索賠事件發生前十二個月內您向本公司支付之費用總額。（此「前十二個月已付費用」上限為常見 SaaS 結構。）</li>
        </ul>
      </section>

      <section class="terms-section">
        <h2>12. 暫停；終止</h2>
        <p>基於安全、法令遵循或重大違約等合理必要情形，本公司得暫停或終止存取。</p>
      </section>

      <section class="terms-section">
        <h2>13. 服務或條款變更</h2>
        <p>本公司得修改本服務或本條款。於合理情形下將提供通知。繼續使用即視為接受更新後之條款。</p>
      </section>

      <section class="terms-section">
        <h2>14. 準據法；管轄</h2>
        <p>本條款受日本法律管轄。東京地方裁判所為第一審專屬管轄法院。惟若您居住國之強制法規另有要求，則在其不得排除之範圍內適用該強制規定。</p>
      </section>
    </main>"""

    text = re.sub(
        r"<main class=\"terms-content\">[\s\S]*?</main>",
        main_zh,
        text,
        count=1,
    )
    text = text.replace(
        'href="../../register/registration_si-fi_en.html"',
        'href="../../register/registration_si-fi_zh-tw.html"',
    )
    text = text.replace(
        "→ Go back Registration",
        "→ 返回註冊頁面",
    )
    text = _patch_lang_switcher(
        text,
        active="zh-tw",
        url_ja="../../../legal/terms/index.html",
        url_en="../../../en/legal/terms/index.html",
        url_zh_tw="index.html",
    )
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text, encoding="utf-8")
    print(f"wrote {dst.relative_to(ROOT)}")


def build_legal_privacy() -> None:
    src = ROOT / "en" / "legal" / "privacy" / "index.html"
    dst = ROOT / "zh-tw" / "legal" / "privacy" / "index.html"
    text = apply_common_zh(src.read_text(encoding="utf-8"))
    text = text.replace(
        "<title>Privacy Policy | KPI Navigator | FORGE LABORATORY</title>",
        "<title>隱私權政策 | KPI Navigator | FORGE LABORATORY</title>",
    )
    text = text.replace(
        'href="../terms/style.css"',
        'href="../../../legal/terms/style.css"',
    )

    main_zh = """    <main class="terms-content">
      <h1 class="terms-title">隱私權政策</h1>
      <p class="terms-meta">最後更新：2026年2月16日<br>控管者／營運者：Forge-Lab（由松下真一郎營運）<br>聯絡方式：<a href="mailto:support@forge-laboratory.com">support@forge-laboratory.com</a></p>

      <section class="terms-section">
        <h2>1. 我們蒐集的資料</h2>
        <p>我們可能蒐集：</p>
        <ul>
          <li><strong>帳戶資料：</strong>姓名（或商業名稱）、電子郵件、密碼雜湊、國家／地區、語言偏好</li>
          <li><strong>業務輸入資料：</strong>銷售數字、營業日、KPI 設定，以及相關分析輸出</li>
          <li><strong>付款資料：</strong>我們不儲存完整卡片資訊；付款由第三方處理業者（例如 Stripe）處理</li>
          <li><strong>使用資料：</strong>日誌（IP 位址、裝置／瀏覽器、頁面／操作、時間戳）、安全事件</li>
          <li><strong>Cookie：</strong>必要 Cookie，以及（若啟用）分析 Cookie</li>
        </ul>
      </section>

      <section class="terms-section">
        <h2>2. 使用目的</h2>
        <ul>
          <li>提供與營運本服務（建立帳戶、登入、功能交付）</li>
          <li>客戶支援與通訊</li>
          <li>安全性、詐欺防範、濫用偵測</li>
          <li>服務改善與分析（若啟用）</li>
          <li>法令遵循與條款執行</li>
        </ul>
      </section>

      <section class="terms-section">
        <h2>3. 法律依據（EEA／英國用戶）</h2>
        <p>在適用 GDPR／UK GDPR 時，我們基於下列依據處理個人資料：</p>
        <ul>
          <li>契約必要性（為提供本服務）</li>
          <li>正當利益（安全、詐欺防範、提升可靠性）</li>
          <li>同意（可選分析／行銷 Cookie，若使用時）</li>
        </ul>
        <p>（本通知反映透明度要求。）</p>
      </section>

      <section class="terms-section">
        <h2>4. 分享與處理者</h2>
        <p>我們可能與下列對象分享資料：</p>
        <ul>
          <li>基礎設施與託管供應商</li>
          <li>付款處理業者（例如 Stripe）</li>
          <li>分析供應商（若啟用）</li>
          <li>依法要求時之主管機關</li>
        </ul>
      </section>

      <section class="terms-section">
        <h2>5. 國際資料傳輸</h2>
        <p>我們可能在您所在國家以外處理資料。對於 EEA／英國資料傳輸，我們於必要時採用充分性認定或標準契約條款等適當保護措施。</p>
        <p>與日本相關之要求，我們遵循個資法（APPI）關於跨境傳輸之規定。</p>
      </section>

      <section class="terms-section">
        <h2>6. 保存期間</h2>
        <p>我們會在提供本服務、遵守法律義務、解決爭議與執行協議所需期間內保存個人資料。部分日誌可能因安全／稽核目的而保留。</p>
      </section>

      <section class="terms-section">
        <h2>7. 您的權利</h2>
        <p>依您所在地，您可能享有下列權利：</p>
        <ul>
          <li>存取、更正、刪除或匯出您的個人資料</li>
          <li>反對或限制特定處理</li>
          <li>撤回同意（處理基於同意時）</li>
          <li>向監管機關提出申訴（EEA／英國）</li>
        </ul>
      </section>

      <section class="terms-section">
        <h2>8. Cookie</h2>
        <p>我們使用必要 Cookie 以進行驗證與安全防護。可選分析 Cookie（若使用）將於需要時透過 Cookie 橫幅或設定控制。</p>
      </section>

      <section class="terms-section">
        <h2>9. 安全性</h2>
        <p>我們採取合理之技術與組織措施保護資料。惟任何傳輸或儲存方式皆無法保證百分之百安全。</p>
      </section>

      <section class="terms-section">
        <h2>10. 兒童</h2>
        <p>本服務非針對兒童，而以商業用戶為對象。</p>
      </section>

      <section class="terms-section">
        <h2>11. 政策更新</h2>
        <p>我們可能不時更新本政策。「最後更新」日期將反映變更。</p>
      </section>

      <section class="terms-section">
        <h2>12. 聯絡方式</h2>
        <p>隱私相關詢問請聯絡：<a href="mailto:support@forge-laboratory.com">support@forge-laboratory.com</a></p>
      </section>
    </main>"""

    text = re.sub(
        r"<main class=\"terms-content\">[\s\S]*?</main>",
        main_zh,
        text,
        count=1,
    )
    text = text.replace(
        'href="../../register/registration_si-fi_en.html"',
        'href="../../register/registration_si-fi_zh-tw.html"',
    )
    text = text.replace("→ Go back Registration", "→ 返回註冊頁面")
    text = _patch_lang_switcher(
        text,
        active="zh-tw",
        url_ja="../../../legal/privacy/index.html",
        url_en="../../../en/legal/privacy/index.html",
        url_zh_tw="index.html",
    )
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text, encoding="utf-8")
    print(f"wrote {dst.relative_to(ROOT)}")


def build_register() -> None:
    src = ROOT / "en" / "register" / "registration_si-fi_en.html"
    dst = ROOT / "zh-tw" / "register" / "registration_si-fi_zh-tw.html"
    text = apply_common_zh(src.read_text(encoding="utf-8"))
    text = text.replace(
        "<title>KPI Navigator - Registration | FORGE LABORATORY WEB SERVICE</title>",
        "<title>KPI Navigator - 註冊 | FORGE LABORATORY WEB SERVICE</title>",
    )
    text = text.replace('href="style.css"', 'href="../../register/style.css"')
    text = text.replace('src="script.js"', 'src="script.js"')
    reps = [
        (">Cancel anytime</p>", ">可隨時取消</p>"),
        ('id="plan-price">$5 / Month</p>', 'id="plan-price">$5 / 月</p>'),
        (">Registration</span>", ">註冊</span>"),
        ("<label for=\"name\">Name :</label>", "<label for=\"name\">姓名 :</label>"),
        (
            "<label for=\"company\">Company Name / Store Name :</label>",
            "<label for=\"company\">公司名稱 / 店名 :</label>",
        ),
        (
            "<label for=\"email\">Email Address :</label>",
            "<label for=\"email\">電子郵件地址 :</label>",
        ),
        ("<label for=\"password\">Password :</label>", "<label for=\"password\">密碼 :</label>"),
        (
            "<label for=\"password-confirm\">Confirm Password :</label>",
            "<label for=\"password-confirm\">確認密碼 :</label>",
        ),
        ('aria-label="Show password"', 'aria-label="顯示密碼"'),
        ('title="Show password"', 'title="顯示密碼"'),
        (
            ">*At least 8 characters, including letters, numbers, and symbols</p>",
            ">*至少 8 個字元，需包含字母、數字與符號</p>",
        ),
        (
            ">I agree to the Terms of Service and Privacy Policy</span>",
            ">我同意服務條款與隱私權政策</span>",
        ),
        ('href="../legal/terms/"', 'href="../legal/terms/"'),
        ('href="../legal/privacy/"', 'href="../legal/privacy/"'),
        (">View Terms</a>", ">查看服務條款</a>"),
        (">View Privacy</a>", ">查看隱私權政策</a>"),
        (">Register</button>", ">註冊</button>"),
    ]
    for a, b in reps:
        text = text.replace(a, b)
    text = _patch_lang_switcher(
        text,
        active="zh-tw",
        url_ja="../../register/registration_si-fi_jp/registration_si-fi_jp.html",
        url_en="../../en/register/registration_si-fi_en.html",
        url_zh_tw="registration_si-fi_zh-tw.html",
    )
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text, encoding="utf-8")
    print(f"wrote {dst.relative_to(ROOT)}")

    # script.js for zh-tw register
    js_src = (ROOT / "en" / "register" / "script.js").read_text(encoding="utf-8")
    js = js_src
    js = js.replace(
        "btnModeToggle.setAttribute('aria-label', isOffice ? 'Switch to Sci-Fi Mode' : 'Switch to Office Mode');",
        "btnModeToggle.setAttribute('aria-label', isOffice ? '切換至 Sci-Fi Mode' : '切換至 Office Mode');",
    )
    js = js.replace(
        "var urlEn = wrap && wrap.getAttribute('data-url-en');\n"
        "    var urlJa = wrap && wrap.getAttribute('data-url-ja');",
        "var urlEn = wrap && wrap.getAttribute('data-url-en');\n"
        "    var urlJa = wrap && wrap.getAttribute('data-url-ja');\n"
        "    var urlZhTw = wrap && wrap.getAttribute('data-url-zh-tw');",
    )
    js = js.replace(
        "var baseUrl = (lang === 'ja' && urlJa) ? urlJa : (lang === 'en' && urlEn) ? urlEn : null;",
        "var baseUrl =\n"
        "          lang === 'ja' && urlJa\n"
        "            ? urlJa\n"
        "            : lang === 'en' && urlEn\n"
        "              ? urlEn\n"
        "              : lang === 'zh-tw' && urlZhTw\n"
        "                ? urlZhTw\n"
        "                : null;",
    )
    js = js.replace(
        "  var messages = {\n"
        "    en: {\n"
        "      required: 'Please enter this field.',\n"
        "      passwordLength: 'Password must be at least 8 characters, including letters, numbers, and symbols.'\n"
        "    },\n"
        "    ja: {\n"
        "      required: 'このフィールドを入力してください。',\n"
        "      passwordLength: 'パスワードは8文字以上で、英数字と記号を含めてください。'\n"
        "    }\n"
        "  };",
        "  var messages = {\n"
        "    en: {\n"
        "      required: 'Please enter this field.',\n"
        "      passwordLength: 'Password must be at least 8 characters, including letters, numbers, and symbols.'\n"
        "    },\n"
        "    ja: {\n"
        "      required: 'このフィールドを入力してください。',\n"
        "      passwordLength: 'パスワードは8文字以上で、英数字と記号を含めてください。'\n"
        "    },\n"
        "    zh: {\n"
        "      required: '請填寫此欄位。',\n"
        "      passwordLength: '密碼至少需 8 個字元，並包含字母、數字與符號。'\n"
        "    }\n"
        "  };",
    )
    js = js.replace(
        "alert(pageLang === 'ja' ? 'パスワードが一致しません。' : 'Passwords do not match.');",
        "alert(pageLang === 'ja' ? 'パスワードが一致しません。' : pageLang === 'zh' ? '密碼不一致。' : 'Passwords do not match.');",
    )
    js = js.replace(
        "btn.setAttribute('aria-label', isPassword ? 'Hide password' : 'Show password');\n"
        "      btn.setAttribute('title', isPassword ? 'Hide password' : 'Show password');",
        "btn.setAttribute('aria-label', isPassword ? '隱藏密碼' : '顯示密碼');\n"
        "      btn.setAttribute('title', isPassword ? '隱藏密碼' : '顯示密碼');",
    )
    # Also keep $ prices (same as EN / zh-tw setting); localize / Month → / 月
    js = js.replace("planPrice.textContent = '$29 / Month';", "planPrice.textContent = '$29 / 月';")
    js = js.replace("planPrice.textContent = '$5 / Month';", "planPrice.textContent = '$5 / 月';")
    (ROOT / "zh-tw" / "register" / "script.js").write_text(js, encoding="utf-8")
    print("wrote zh-tw/register/script.js")


def wire_ja_en_switchers() -> None:
    mapping = {
        ("login/index.html", "ja"): (
            "index.html",
            "../en/login/index.html",
            "../zh-tw/login/index.html",
        ),
        ("en/login/index.html", "en"): (
            "../../login/index.html",
            "index.html",
            "../../zh-tw/login/index.html",
        ),
        ("plan/index.html", "ja"): (
            "index.html",
            "../en/plan/index.html",
            "../zh-tw/plan/index.html",
        ),
        ("en/plan/index.html", "en"): (
            "../../plan/index.html",
            "index.html",
            "../../zh-tw/plan/index.html",
        ),
        ("legal/terms/index.html", "ja"): (
            "index.html",
            "../../en/legal/terms/index.html",
            "../../zh-tw/legal/terms/index.html",
        ),
        ("en/legal/terms/index.html", "en"): (
            "../../../legal/terms/index.html",
            "index.html",
            "../../../zh-tw/legal/terms/index.html",
        ),
        ("legal/privacy/index.html", "ja"): (
            "index.html",
            "../../en/legal/privacy/index.html",
            "../../zh-tw/legal/privacy/index.html",
        ),
        ("en/legal/privacy/index.html", "en"): (
            "../../../legal/privacy/index.html",
            "index.html",
            "../../../zh-tw/legal/privacy/index.html",
        ),
        ("register/registration_si-fi_jp/registration_si-fi_jp.html", "ja"): (
            "registration_si-fi_jp.html",
            "../../en/register/registration_si-fi_en.html",
            "../../zh-tw/register/registration_si-fi_zh-tw.html",
        ),
        ("en/register/registration_si-fi_en.html", "en"): (
            "../../register/registration_si-fi_jp/registration_si-fi_jp.html",
            "registration_si-fi_en.html",
            "../../zh-tw/register/registration_si-fi_zh-tw.html",
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

    # Patch EN + JA register script.js for zh-tw URL resolution
    for rel in ("en/register/script.js", "register/script.js"):
        path = ROOT / rel
        if not path.is_file():
            continue
        js = path.read_text(encoding="utf-8")
        if "urlZhTw" not in js:
            js = js.replace(
                "var urlEn = wrap && wrap.getAttribute('data-url-en');\n"
                "    var urlJa = wrap && wrap.getAttribute('data-url-ja');",
                "var urlEn = wrap && wrap.getAttribute('data-url-en');\n"
                "    var urlJa = wrap && wrap.getAttribute('data-url-ja');\n"
                "    var urlZhTw = wrap && wrap.getAttribute('data-url-zh-tw');",
            )
            js = js.replace(
                "var baseUrl = (lang === 'ja' && urlJa) ? urlJa : (lang === 'en' && urlEn) ? urlEn : null;",
                "var baseUrl =\n"
                "          lang === 'ja' && urlJa\n"
                "            ? urlJa\n"
                "            : lang === 'en' && urlEn\n"
                "              ? urlEn\n"
                "              : lang === 'zh-tw' && urlZhTw\n"
                "                ? urlZhTw\n"
                "                : null;",
            )
            path.write_text(js, encoding="utf-8")
            print(f"patched register JS: {rel}")


def refresh_public_chrome() -> None:
    rc = subprocess.call(
        [sys.executable, str(ROOT / "scripts" / "build_site_chrome.py"), "public"],
        cwd=str(ROOT / "scripts"),
    )
    if rc != 0:
        raise SystemExit(f"build_site_chrome public failed: {rc}")


def main() -> None:
    patch_shared_css()
    build_login()
    build_account_protection()
    build_plan()
    build_legal_terms()
    build_legal_privacy()
    build_register()
    wire_ja_en_switchers()
    refresh_public_chrome()
    print("build_zh_tw_public_pages: OK")


if __name__ == "__main__":
    main()
