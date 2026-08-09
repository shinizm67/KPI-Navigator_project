#!/usr/bin/env python3
"""Build setting/preferences.html (JA + EN + zh-TW)."""

from __future__ import annotations

from pathlib import Path

from site_chrome import (
    FOOTER_MARK_END,
    FOOTER_MARK_START,
    HEADER_MARK_END,
    HEADER_MARK_START,
    build_footer,
    build_header,
)

ROOT = Path(__file__).resolve().parents[1]

CURRENCY_OPTS = """              <option value="">— Select —</option>
              <option value="JPY">¥ - Yen</option>
              <option value="USD">$ - US Dollar</option>
              <option value="EUR">€ - Euro</option>
              <option value="GBP">£ - Pound</option>
              <option value="TWD">NT$ - New Taiwan Dollar</option>"""

# Locale roots: JA at repo root, EN under en/, Traditional Chinese (TW) under zh-tw/
# Language is NOT CSS-class switching — parallel page trees (same as en/).
LANG_META = {
    "ja": {
        "html_lang": "ja",
        "out": "setting/preferences.html",
        "img": "../",
        "base": "../",
        "currency_js": "../js/kpi-currency.js",
        "register_css": "../register/style.css",
        "setting_css": "../en/setting/style.css",
        "url_ja": "preferences.html",
        "url_en": "../en/setting/preferences.html",
        "url_zh_tw": "../zh-tw/setting/preferences.html",
        "title": "環境設定 | KPI Pilot | FORGE LABORATORY",
        "page_sub": "設定",
        "hint": "変更は KPI Pilot 全体に反映されます。表示モードはヘッダーのトグルとも同期します。",
        "label_lang": "言語を選択 :",
        "label_currency": "通貨を選択 :",
        "label_mode": "表示モード :",
        "label_tutorial": "チュートリアル / ツールチップ :",
        "aria_lang": "言語を選択",
        "aria_currency": "通貨を選択",
        "aria_mode": "表示モードを選択",
        "aria_tutorial": "チュートリアル表示を切替",
        "save_label": "設定を保存",
        "workspace_aria": "現在のワークスペース",
        "workspace_list_aria": "ワークスペース一覧",
        "switch_to_scifi": "Sci-Fi Mode に切り替え",
        "switch_to_office": "Office Mode に切り替え",
        "saved_msg": "設定を保存しました。",
        "lang_btn_aria": "言語を選択",
        "lang_list_aria": "言語オプション",
        "lang_code": "JP",
        "lang_name": "Japanese",
    },
    "en": {
        "html_lang": "en",
        "out": "en/setting/preferences.html",
        "img": "../../",
        "base": "../",
        "currency_js": "../../js/kpi-currency.js",
        "register_css": "../../register/style.css",
        "setting_css": "style.css",
        "url_ja": "../../setting/preferences.html",
        "url_en": "preferences.html",
        "url_zh_tw": "../../zh-tw/setting/preferences.html",
        "title": "Preferences | KPI Pilot | FORGE LABORATORY",
        "page_sub": "Preferences",
        "hint": "Changes apply across KPI Pilot. Display Mode also syncs with the header toggle.",
        "label_lang": "Choose Language :",
        "label_currency": "Choose Currency :",
        "label_mode": "Display Mode :",
        "label_tutorial": "Tutorial / Tooltips :",
        "aria_lang": "Select language",
        "aria_currency": "Select currency",
        "aria_mode": "Select display mode",
        "aria_tutorial": "Toggle tutorial tooltips",
        "save_label": "Save Preferences",
        "workspace_aria": "Current workspace",
        "workspace_list_aria": "Workspace list",
        "switch_to_scifi": "Switch to Sci-Fi Mode",
        "switch_to_office": "Switch to Office Mode",
        "saved_msg": "Preferences saved.",
        "lang_btn_aria": "Select language",
        "lang_list_aria": "Language options",
        "lang_code": "EN",
        "lang_name": "English",
    },
    "zh-tw": {
        "html_lang": "zh-TW",
        "out": "zh-tw/setting/preferences.html",
        "img": "../../",
        "base": "../",
        "currency_js": "../../js/kpi-currency.js",
        "register_css": "../../register/style.css",
        "setting_css": "../../en/setting/style.css",
        "url_ja": "../../setting/preferences.html",
        "url_en": "../../en/setting/preferences.html",
        "url_zh_tw": "preferences.html",
        "title": "設定 | KPI Pilot | FORGE LABORATORY",
        "page_sub": "設定",
        "hint": "變更會套用至整個 KPI Pilot。顯示模式也會與頁首切換同步。",
        "label_lang": "選擇語言 :",
        "label_currency": "選擇貨幣 :",
        "label_mode": "顯示模式 :",
        "label_tutorial": "教學 / 提示 :",
        "aria_lang": "選擇語言",
        "aria_currency": "選擇貨幣",
        "aria_mode": "選擇顯示模式",
        "aria_tutorial": "切換教學提示",
        "save_label": "儲存設定",
        "workspace_aria": "目前工作區",
        "workspace_list_aria": "工作區清單",
        "switch_to_scifi": "切換至 Sci-Fi Mode",
        "switch_to_office": "切換至 Office Mode",
        "saved_msg": "設定已儲存。",
        "lang_btn_aria": "選擇語言",
        "lang_list_aria": "語言選項",
        "lang_code": "TW",
        "lang_name": "Traditional Chinese",
    },
}

OPT_JA = "JP - Japanese"
OPT_EN = "EN - English"
OPT_TW = "TW - Traditional Chinese"


def build(lang: str) -> str:
    m = LANG_META[lang]
    header = build_header(
        lang=lang,
        base=m["base"],
        img=m["img"],
        active=None,
        daily_mode="link",
        account_current="preferences",
    )
    footer = build_footer(lang=lang, img=m["img"])
    sel_ja = " selected" if lang == "ja" else ""
    sel_en = " selected" if lang == "en" else ""
    sel_tw = " selected" if lang == "zh-tw" else ""
    act_ja = " lang-option-active" if lang == "ja" else ""
    act_en = " lang-option-active" if lang == "en" else ""
    act_tw = " lang-option-active" if lang == "zh-tw" else ""

    return f"""<!DOCTYPE html>
<html lang="{m['html_lang']}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{m['title']}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=BIZ+UDP+Gothic:wght@400;500;700&family=Orbitron:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{m['register_css']}">
  <link rel="stylesheet" href="{m['setting_css']}">
  <style>
    .profile-preferences-hint {{
      margin: 0 0 28px;
      max-width: 520px;
      color: #58e1f3;
      font-size: 13px;
      line-height: 1.45;
      opacity: 0.9;
    }}
    body.office-mode .profile-preferences-hint {{
      color: #333;
      opacity: 1;
    }}
  </style>
</head>
<body class="si-fi profile-page" id="body-el">
  <!-- KPI-CURRENCY-JS:START -->
  <script src="{m['currency_js']}"></script>
  <!-- KPI-CURRENCY-JS:END -->
{HEADER_MARK_START}
{header}
{HEADER_MARK_END}

  <div class="page-wrap profile-wrap">
    <main class="profile-main">
      <div class="workspace-selector-wrap">
        <button type="button" class="profile-workspace-indicator" id="workspace-trigger" aria-label="{m['workspace_aria']}" aria-expanded="false" aria-haspopup="true">
          <span class="profile-workspace-icon" aria-hidden="true">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" focusable="false"><path d="M8 5v14l11-7z"/></svg>
          </span>
          <span class="profile-workspace-label">Workspace : Personal</span>
        </button>
        <div class="workspace-popup" id="workspace-popup" role="dialog" aria-label="{m['workspace_list_aria']}" hidden>
          <div class="workspace-popup-inner">
            <div class="workspace-popup-item is-current">Workspace : Personal</div>
          </div>
        </div>
      </div>
      <h1 class="profile-title-main">KPI Pilot</h1>
      <h2 class="profile-title-sub">{m['page_sub']}</h2>
      <p class="profile-preferences-hint">{m['hint']}</p>

      <form class="registration-form profile-form" action="#" method="post" id="preferences-form">
        <div class="profile-editable-group">
          <div class="form-group">
            <label for="pref-lang">{m['label_lang']}</label>
            <select id="pref-lang" name="lang" class="profile-select" aria-label="{m['aria_lang']}" data-url-ja="{m['url_ja']}" data-url-en="{m['url_en']}" data-url-zh-tw="{m['url_zh_tw']}">
              <option value="ja"{sel_ja}>{OPT_JA}</option>
              <option value="en"{sel_en}>{OPT_EN}</option>
              <option value="zh-tw"{sel_tw}>{OPT_TW}</option>
            </select>
          </div>

          <div class="form-group">
            <label for="pref-currency">{m['label_currency']}</label>
            <select id="pref-currency" name="currency" class="profile-select" aria-label="{m['aria_currency']}">
{CURRENCY_OPTS}
            </select>
          </div>

          <div class="form-group">
            <label for="pref-mode">{m['label_mode']}</label>
            <select id="pref-mode" name="mode" class="profile-select" aria-label="{m['aria_mode']}">
              <option value="scifi">Sci-Fi Mode</option>
              <option value="office">Office Mode</option>
            </select>
          </div>

          <div class="form-group">
            <label for="pref-tutorial">{m['label_tutorial']}</label>
            <select id="pref-tutorial" name="tutorial" class="profile-select" aria-label="{m['aria_tutorial']}">
              <option value="1">ON</option>
              <option value="0">OFF</option>
            </select>
          </div>
        </div>

        <div class="form-actions profile-actions">
          <button type="submit" class="btn-submit btn-register profile-save-button">{m['save_label']}</button>
        </div>
      </form>
    </main>
  </div>

{FOOTER_MARK_START}
{footer}
{FOOTER_MARK_END}

  <div class="lang-select-wrap" id="lang-select-wrap" data-url-en="{m['url_en']}" data-url-ja="{m['url_ja']}" data-url-zh-tw="{m['url_zh_tw']}">
    <button type="button" class="lang-select-btn" id="lang-select-btn" aria-expanded="false" aria-haspopup="listbox" aria-label="{m['lang_btn_aria']}">
      <span class="lang-code" aria-hidden="true">{m['lang_code']}</span>
      <span class="lang-name">{m['lang_name']}</span>
      <span class="lang-chevron" aria-hidden="true"></span>
    </button>
    <div class="lang-select-dropdown" id="lang-select-dropdown" role="listbox" aria-label="{m['lang_list_aria']}" hidden>
      <button type="button" class="lang-option lang-option-ja{act_ja}" role="option" data-lang="ja">{OPT_JA}</button>
      <button type="button" class="lang-option lang-option-en{act_en}" role="option" data-lang="en">{OPT_EN}</button>
      <button type="button" class="lang-option lang-option-zh-tw{act_tw}" role="option" data-lang="zh-tw">{OPT_TW}</button>
    </div>
  </div>

  <script>
    (function () {{
      var STORAGE_KEY = 'kpi-office-mode';
      var bodyEl = document.getElementById('body-el');
      var btnModeToggle = document.getElementById('btn-mode-toggle');
      var btnModeText = document.getElementById('btn-mode-text');
      var settingsOfficeLabel = document.getElementById('settings-office-label');
      var prefMode = document.getElementById('pref-mode');

      function isOffice() {{
        return !!(bodyEl && bodyEl.classList.contains('office-mode'));
      }}

      function updateModeButton() {{
        if (!btnModeText || !btnModeToggle) return;
        var office = isOffice();
        btnModeText.textContent = office ? 'SCI-FI MODE' : 'OFFICE MODE';
        btnModeToggle.setAttribute('aria-label', office ? '{m['switch_to_scifi']}' : '{m['switch_to_office']}');
        if (settingsOfficeLabel) settingsOfficeLabel.textContent = office ? 'Sci-Fi Mode' : 'Office Mode';
        if (prefMode) prefMode.value = office ? 'office' : 'scifi';
      }}

      function setOffice(on) {{
        if (!bodyEl) return;
        bodyEl.classList.toggle('office-mode', !!on);
        try {{
          if (on) sessionStorage.setItem(STORAGE_KEY, '1');
          else sessionStorage.removeItem(STORAGE_KEY);
        }} catch (_e) {{}}
        updateModeButton();
      }}

      if (bodyEl && btnModeToggle) {{
        try {{
          if (sessionStorage.getItem(STORAGE_KEY) === '1') bodyEl.classList.add('office-mode');
        }} catch (_e) {{}}
        btnModeToggle.addEventListener('click', function (e) {{
          e.preventDefault();
          setOffice(!isOffice());
        }});
        updateModeButton();
      }}

      if (prefMode) {{
        prefMode.addEventListener('change', function () {{
          setOffice(prefMode.value === 'office');
        }});
      }}
    }})();

    (function () {{
      var menuBtn = document.querySelector('.icon-button-menu');
      var dropdown = document.getElementById('settings-dropdown');
      var officeToggle = document.getElementById('settings-office-toggle');
      if (!menuBtn || !dropdown) return;
      menuBtn.addEventListener('click', function (e) {{
        e.stopPropagation();
        dropdown.hidden = !dropdown.hidden;
      }});
      if (officeToggle) {{
        officeToggle.addEventListener('click', function (e) {{
          e.preventDefault();
          e.stopPropagation();
          var modeBtn = document.getElementById('btn-mode-toggle');
          if (modeBtn) modeBtn.click();
        }});
      }}
      dropdown.addEventListener('click', function (e) {{ e.stopPropagation(); }});
      document.addEventListener('click', function () {{ dropdown.hidden = true; }});
    }})();

    (function () {{
      var gearBtn = document.getElementById('btn-account-settings');
      var accountPopup = document.getElementById('account-settings-popup');
      var menuDropdown = document.getElementById('settings-dropdown');
      if (!gearBtn || !accountPopup) return;
      gearBtn.addEventListener('click', function (e) {{
        e.stopPropagation();
        var isOpen = !accountPopup.hidden;
        accountPopup.hidden = isOpen;
        gearBtn.setAttribute('aria-expanded', (!isOpen).toString());
        if (!isOpen && menuDropdown) menuDropdown.hidden = true;
      }});
      accountPopup.addEventListener('click', function (e) {{ e.stopPropagation(); }});
      document.addEventListener('click', function () {{
        accountPopup.hidden = true;
        gearBtn.setAttribute('aria-expanded', 'false');
      }});
    }})();

    (function () {{
      var trigger = document.getElementById('workspace-trigger');
      var popup = document.getElementById('workspace-popup');
      if (!trigger || !popup) return;
      trigger.addEventListener('click', function (e) {{
        e.stopPropagation();
        var isOpen = !popup.hidden;
        popup.hidden = isOpen;
        trigger.setAttribute('aria-expanded', (!isOpen).toString());
      }});
      popup.addEventListener('click', function (e) {{ e.stopPropagation(); }});
      document.addEventListener('click', function () {{
        popup.hidden = true;
        trigger.setAttribute('aria-expanded', 'false');
      }});
    }})();

    (function () {{
      var CURRENCY_KEY = 'kpi-currency';
      var TUTORIAL_KEY = 'kpi-tutorial-advanced';
      var currencyEl = document.getElementById('pref-currency');
      var tutorialEl = document.getElementById('pref-tutorial');
      var langEl = document.getElementById('pref-lang');
      var form = document.getElementById('preferences-form');
      var bodyEl = document.getElementById('body-el');

      function hrefForLang(lang) {{
        if (!langEl) return null;
        if (lang === 'ja') return langEl.getAttribute('data-url-ja');
        if (lang === 'en') return langEl.getAttribute('data-url-en');
        if (lang === 'zh-tw') return langEl.getAttribute('data-url-zh-tw');
        return null;
      }}

      function navigateLang(lang) {{
        var href = hrefForLang(lang);
        if (!href) return;
        try {{
          if (bodyEl && bodyEl.classList.contains('office-mode')) {{
            sessionStorage.setItem('kpi-office-mode', '1');
          }}
        }} catch (_e) {{}}
        window.location.href = href;
      }}

      function saveCurrency(code) {{
        try {{
          if (code) localStorage.setItem(CURRENCY_KEY, code);
          else localStorage.removeItem(CURRENCY_KEY);
          var raw = localStorage.getItem('kpi-profile-last');
          if (raw) {{
            var data = JSON.parse(raw);
            var labels = {{
              JPY: '¥ - Yen',
              USD: '$ - US Dollar',
              EUR: '€ - Euro',
              GBP: '£ - Pound',
              TWD: 'NT$ - New Taiwan Dollar'
            }};
            if (window.KpiCurrency && KpiCurrency.label) {{
              data.currency = KpiCurrency.label(code) || code || '';
            }} else {{
              data.currency = labels[code] || code || '';
            }}
            localStorage.setItem('kpi-profile-last', JSON.stringify(data));
          }}
        }} catch (_e) {{}}
      }}

      function saveTutorial(on) {{
        try {{
          sessionStorage.setItem(TUTORIAL_KEY, on ? '1' : '0');
        }} catch (_e) {{}}
        document.body.classList.toggle('tutorial-advanced-off', !on);
      }}

      try {{
        if (currencyEl && window.KpiCurrency && typeof KpiCurrency.arrangeSelect === 'function') {{
          KpiCurrency.arrangeSelect(currencyEl);
        }}
        var cur = localStorage.getItem(CURRENCY_KEY) || '';
        if (currencyEl && cur) currencyEl.value = cur;
        var tut = sessionStorage.getItem(TUTORIAL_KEY);
        if (tutorialEl) tutorialEl.value = tut === '0' ? '0' : '1';
      }} catch (_e) {{}}

      if (langEl) {{
        langEl.addEventListener('change', function () {{
          navigateLang(langEl.value);
        }});
      }}
      if (currencyEl) {{
        currencyEl.addEventListener('change', function () {{
          saveCurrency(currencyEl.value);
        }});
      }}
      if (tutorialEl) {{
        saveTutorial(tutorialEl.value !== '0');
        tutorialEl.addEventListener('change', function () {{
          saveTutorial(tutorialEl.value !== '0');
        }});
      }}

      if (form) {{
        form.addEventListener('submit', function (e) {{
          e.preventDefault();
          if (currencyEl) saveCurrency(currencyEl.value);
          if (tutorialEl) saveTutorial(tutorialEl.value !== '0');
          var modeEl = document.getElementById('pref-mode');
          if (modeEl && bodyEl) {{
            var on = modeEl.value === 'office';
            bodyEl.classList.toggle('office-mode', on);
            try {{
              if (on) sessionStorage.setItem('kpi-office-mode', '1');
              else sessionStorage.removeItem('kpi-office-mode');
            }} catch (_e) {{}}
          }}
          if (langEl && langEl.value !== '{lang}') {{
            navigateLang(langEl.value);
            return;
          }}
          window.alert('{m['saved_msg']}');
        }});
      }}
    }})();

    (function () {{
      var langBtn = document.getElementById('lang-select-btn');
      var langDropdown = document.getElementById('lang-select-dropdown');
      var langOptions = document.querySelectorAll('.lang-option');
      var langWrap = document.getElementById('lang-select-wrap');
      if (!langBtn || !langDropdown || !langWrap) return;
      langBtn.addEventListener('click', function (e) {{
        e.stopPropagation();
        var isOpen = !langDropdown.hidden;
        langDropdown.hidden = isOpen;
        langBtn.setAttribute('aria-expanded', (!isOpen).toString());
      }});
      document.addEventListener('click', function () {{
        langDropdown.hidden = true;
        langBtn.setAttribute('aria-expanded', 'false');
      }});
      var urlEn = langWrap.getAttribute('data-url-en');
      var urlJa = langWrap.getAttribute('data-url-ja');
      var urlZhTw = langWrap.getAttribute('data-url-zh-tw');
      var bodyElForLang = document.getElementById('body-el');
      langOptions.forEach(function (opt) {{
        opt.addEventListener('click', function (e) {{
          e.stopPropagation();
          try {{
            if (bodyElForLang && bodyElForLang.classList.contains('office-mode')) {{
              sessionStorage.setItem('kpi-office-mode', '1');
            }}
          }} catch (_e) {{}}
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
        }});
      }});
    }})();

    (function () {{
      var back = document.getElementById('footerBackToTop');
      if (!back) return;
      back.addEventListener('click', function () {{
        window.scrollTo({{ top: 0, behavior: 'smooth' }});
      }});
    }})();
  </script>
</body>
</html>
"""


def main() -> None:
    for lang, meta in LANG_META.items():
        path = ROOT / meta["out"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(build(lang), encoding="utf-8")
        print("wrote", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
