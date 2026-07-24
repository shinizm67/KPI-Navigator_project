#!/usr/bin/env python3
"""Build setting/preferences.html (JA + EN)."""

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
              <option value="GBP">£ - Pound</option>"""


def build(lang: str) -> str:
    is_ja = lang == "ja"
    img = "../" if is_ja else "../../"
    header = build_header(
        lang=lang,
        base="../",
        img=img,
        active=None,
        daily_mode="link",
        account_current="preferences",
    )
    footer = build_footer(lang=lang, img=img)

    if is_ja:
        title = "環境設定 | KPI Navigator | FORGE LABORATORY"
        register_css = "../register/style.css"
        setting_css = "../en/setting/style.css"
        page_sub = "設定"
        hint = "変更は KPI Navigator 全体に反映されます。表示モードはヘッダーのトグルとも同期します。"
        label_lang = "言語を選択 :"
        label_currency = "通貨を選択 :"
        label_mode = "表示モード :"
        label_tutorial = "チュートリアル / ツールチップ :"
        aria_lang = "言語を選択"
        aria_currency = "通貨を選択"
        aria_mode = "表示モードを選択"
        aria_tutorial = "チュートリアル表示を切替"
        opt_ja = "JP - Japanese"
        opt_en = "EN - English"
        save_label = "設定を保存"
        workspace_aria = "現在のワークスペース"
        workspace_list_aria = "ワークスペース一覧"
        switch_to_scifi = "Sci-Fi Mode に切り替え"
        switch_to_office = "Office Mode に切り替え"
        saved_msg = "設定を保存しました。"
        lang_btn_aria = "言語を選択"
        lang_list_aria = "言語オプション"
        url_ja = "preferences.html"
        url_en = "../en/setting/preferences.html"
        lang_code = "JP"
        lang_name = "Japanese"
    else:
        title = "Preferences | KPI Navigator | FORGE LABORATORY"
        register_css = "../../register/style.css"
        setting_css = "style.css"
        page_sub = "Preferences"
        hint = "Changes apply across KPI Navigator. Display Mode also syncs with the header toggle."
        label_lang = "Choose Language :"
        label_currency = "Choose Currency :"
        label_mode = "Display Mode :"
        label_tutorial = "Tutorial / Tooltips :"
        aria_lang = "Select language"
        aria_currency = "Select currency"
        aria_mode = "Select display mode"
        aria_tutorial = "Toggle tutorial tooltips"
        opt_ja = "JP - Japanese"
        opt_en = "EN - English"
        save_label = "Save Preferences"
        workspace_aria = "Current workspace"
        workspace_list_aria = "Workspace list"
        switch_to_scifi = "Switch to Sci-Fi Mode"
        switch_to_office = "Switch to Office Mode"
        saved_msg = "Preferences saved."
        lang_btn_aria = "Select language"
        lang_list_aria = "Language options"
        url_ja = "../../setting/preferences.html"
        url_en = "preferences.html"
        lang_code = "EN"
        lang_name = "English"

    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=BIZ+UDP+Gothic:wght@400;500;700&family=Orbitron:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{register_css}">
  <link rel="stylesheet" href="{setting_css}">
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
{HEADER_MARK_START}
{header}
{HEADER_MARK_END}

  <div class="page-wrap profile-wrap">
    <main class="profile-main">
      <div class="workspace-selector-wrap">
        <button type="button" class="profile-workspace-indicator" id="workspace-trigger" aria-label="{workspace_aria}" aria-expanded="false" aria-haspopup="true">
          <span class="profile-workspace-icon" aria-hidden="true">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" focusable="false"><path d="M8 5v14l11-7z"/></svg>
          </span>
          <span class="profile-workspace-label">Workspace : Personal</span>
        </button>
        <div class="workspace-popup" id="workspace-popup" role="dialog" aria-label="{workspace_list_aria}" hidden>
          <div class="workspace-popup-inner">
            <div class="workspace-popup-item is-current">Workspace : Personal</div>
          </div>
        </div>
      </div>
      <h1 class="profile-title-main">KPI Navigator</h1>
      <h2 class="profile-title-sub">{page_sub}</h2>
      <p class="profile-preferences-hint">{hint}</p>

      <form class="registration-form profile-form" action="#" method="post" id="preferences-form">
        <div class="profile-editable-group">
          <div class="form-group">
            <label for="pref-lang">{label_lang}</label>
            <select id="pref-lang" name="lang" class="profile-select" aria-label="{aria_lang}" data-url-ja="{url_ja}" data-url-en="{url_en}">
              <option value="ja"{' selected' if is_ja else ''}>{opt_ja}</option>
              <option value="en"{'' if is_ja else ' selected'}>{opt_en}</option>
            </select>
          </div>

          <div class="form-group">
            <label for="pref-currency">{label_currency}</label>
            <select id="pref-currency" name="currency" class="profile-select" aria-label="{aria_currency}">
{CURRENCY_OPTS}
            </select>
          </div>

          <div class="form-group">
            <label for="pref-mode">{label_mode}</label>
            <select id="pref-mode" name="mode" class="profile-select" aria-label="{aria_mode}">
              <option value="scifi">Sci-Fi Mode</option>
              <option value="office">Office Mode</option>
            </select>
          </div>

          <div class="form-group">
            <label for="pref-tutorial">{label_tutorial}</label>
            <select id="pref-tutorial" name="tutorial" class="profile-select" aria-label="{aria_tutorial}">
              <option value="1">ON</option>
              <option value="0">OFF</option>
            </select>
          </div>
        </div>

        <div class="form-actions profile-actions">
          <button type="submit" class="btn-submit btn-register profile-save-button">{save_label}</button>
        </div>
      </form>
    </main>
  </div>

{FOOTER_MARK_START}
{footer}
{FOOTER_MARK_END}

  <div class="lang-select-wrap" id="lang-select-wrap" data-url-en="{url_en}" data-url-ja="{url_ja}">
    <button type="button" class="lang-select-btn" id="lang-select-btn" aria-expanded="false" aria-haspopup="listbox" aria-label="{lang_btn_aria}">
      <span class="lang-code" aria-hidden="true">{lang_code}</span>
      <span class="lang-name">{lang_name}</span>
      <span class="lang-chevron" aria-hidden="true"></span>
    </button>
    <div class="lang-select-dropdown" id="lang-select-dropdown" role="listbox" aria-label="{lang_list_aria}" hidden>
      <button type="button" class="lang-option lang-option-ja{' lang-option-active' if is_ja else ''}" role="option" data-lang="ja">{opt_ja}</button>
      <button type="button" class="lang-option lang-option-en{'' if is_ja else ' lang-option-active'}" role="option" data-lang="en">{opt_en}</button>
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
        btnModeToggle.setAttribute('aria-label', office ? '{switch_to_scifi}' : '{switch_to_office}');
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

      function navigateLang(lang) {{
        if (!langEl) return;
        var href =
          lang === 'ja'
            ? langEl.getAttribute('data-url-ja')
            : lang === 'en'
              ? langEl.getAttribute('data-url-en')
              : null;
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
              GBP: '£ - Pound'
            }};
            data.currency = labels[code] || code || '';
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
          window.alert('{saved_msg}');
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
          var href = next === 'ja' && urlJa ? urlJa : next === 'en' && urlEn ? urlEn : null;
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
    targets = {
        "ja": ROOT / "setting/preferences.html",
        "en": ROOT / "en/setting/preferences.html",
    }
    for lang, path in targets.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(build(lang), encoding="utf-8")
        print("wrote", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
