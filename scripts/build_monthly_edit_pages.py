#!/usr/bin/env python3
"""Extract monthly-edit-float into app/monthly/edit and en/app/monthly/edit pages."""

from __future__ import annotations

import re
from pathlib import Path

from kpi_leave_close_chooser import (
    CLOSE_CHOOSER_CSS,
    CLOSE_CHOOSER_HTML,
    close_chooser_js,
)

ROOT = Path(__file__).resolve().parents[1]

CONFIGS = [
    {
        "src": ROOT / "en/app/monthly/index.html",
        "out": ROOT / "en/app/monthly/edit/index.html",
        "lang": "en",
        "title": "Monthly Edit | KPI Navigator | FORGE LABORATORY",
        "content_lang_meta": '  <meta http-equiv="content-language" content="en">\n',
        "translate_no": ' translate="no"',
        "register_css": "../../../../register/style.css",
        "setting_css": "../../../setting/style.css",
        "images_prefix": "../../../../images/",
        "setting_prefix": "../../../setting/",
        "forge_href": "https://forge-laboratory.com/en",
        "forge_aria": "FORGE LABORATORY - Top page",
        "nav_aria": "Main navigation",
        "annual_label": "Annual",
        "monthly_label": "Monthly",
        "daily_label": "Daily",
        "insight_label": "Insight",
        "office_toggle_aria": "Switch to Office Mode",
        "menu_aria": "Open navigation menu",
        "gear_aria": "Account settings",
        "account_popup_aria": "Account Settings",
        "monthly_nav_href": "../index.html",
        "annual_href": "../../annual/index.html",
        "daily_href": "../index.html?open=daily",
        "profit_href": "../index.html?open=insight",
        "profit_basic_href": "../../../setting/change_plan.html",
        "lang_switch_en": "edit/index.html",
        "lang_switch_ja": "../../../app/monthly/edit/index.html",
        "close_aria": "Back to Monthly",
        "close_char": "←",
        "page_h1": "Monthly bulk edit",
        "body_extra_class": "",
    },
    {
        "src": ROOT / "app/monthly/index.html",
        "out": ROOT / "app/monthly/edit/index.html",
        "lang": "ja",
        "title": "月次編集 | KPI Navigator | FORGE LABORATORY",
        "content_lang_meta": "",
        "translate_no": "",
        "register_css": "../../../register/style.css",
        "setting_css": "../../../en/setting/style.css",
        "images_prefix": "../../../images/",
        "setting_prefix": "../../../en/setting/",
        "forge_href": "https://forge-laboratory.com/",
        "forge_aria": "FORGE LABORATORY - トップページ",
        "nav_aria": "メインナビゲーション",
        "annual_label": "年次",
        "monthly_label": "月次",
        "daily_label": "日次",
        "insight_label": "考察",
        "office_toggle_aria": "Office Mode に切り替え",
        "menu_aria": "ナビゲーションメニューを開く",
        "gear_aria": "アカウント設定",
        "account_popup_aria": "アカウント設定",
        "monthly_nav_href": "../index.html",
        "annual_href": "../../annual/index.html",
        "daily_href": "../index.html?open=daily",
        "profit_href": "../index.html?open=insight",
        "profit_basic_href": "../../../setting/change_plan.html",
        "lang_switch_en": "../../../en/app/monthly/edit/index.html",
        "lang_switch_ja": "index.html",
        "close_aria": "月次ページに戻る",
        "close_char": "←",
        "page_h1": "月次一括編集",
        "body_extra_class": "",
    },
]

CSS_START = "/* Monthly Edit Floating Window"
CSS_END = "/* Monthly page: replace Annual daily table window"

JS_START = "    (function () {\n      var root = document.getElementById('monthly-edit-float');"
JS_END_MARKER = "    })();\n    (function () {\n      var win = document.querySelector('.monthly-table-window');"

HTML_START = '<div\n    class="monthly-edit-float"\n    id="monthly-edit-float"'
HTML_END = "\n\n  <footer"

CSS_PAGE_PATCH = """
    body.monthly-edit-page {
      margin: 0;
      min-height: 100vh;
      background: #1a1a1a;
    }
    body.monthly-edit-page.office-mode {
      background: #f4f4f4;
    }
    /* Full-page edit: panel fills viewport below site header */
    body.monthly-edit-page .monthly-edit-float {
      padding: 0;
      min-height: calc(100vh - 72px);
    }
    body.monthly-edit-page .monthly-edit-float__panel {
      width: 100%;
      max-width: none;
      height: calc(100vh - 72px);
      margin: 0;
      border: none;
      border-radius: 0;
      box-shadow: none;
      background: transparent;
      display: flex;
      flex-direction: column;
    }
    body.monthly-edit-page:not(.office-mode) .monthly-edit-float__panel {
      background: #1a1a1a;
    }
    body.monthly-edit-page.office-mode .monthly-edit-float__panel {
      background: #f4f4f4;
    }
    /* Toolbar inset: move control groups inward; background stays full-bleed */
    body.monthly-edit-page {
      --mef-page-inset: 50px;
    }
    body.monthly-edit-page .monthly-edit-float__close {
      left: calc(12px + var(--mef-page-inset));
    }
    body.monthly-edit-page .monthly-edit-float__today {
      left: calc(56px + var(--mef-page-inset));
    }
    body.monthly-edit-page .monthly-edit-float__confirm {
      right: calc(12px + var(--mef-page-inset));
    }
    body.monthly-edit-page .monthly-edit-float__undo {
      right: calc(108px + var(--mef-page-inset));
    }
    body.monthly-edit-page .monthly-edit-float__csv-upload {
      right: calc(214px + var(--mef-page-inset));
    }
    /* KPI-CSV-UPLOAD-TOOLTIP */
    .monthly-edit-float__csv-upload[data-tooltip] {
      z-index: 2;
    }
    .monthly-edit-float__csv-upload[data-tooltip]:hover::after,
    .monthly-edit-float__csv-upload[data-tooltip]:focus-visible::after {
      content: attr(data-tooltip);
      position: absolute;
      left: 50%;
      top: calc(100% + 8px);
      transform: translateX(-50%);
      padding: 8px 10px;
      border: 1px solid var(--mef-line);
      border-radius: 3px;
      background: #102932;
      color: var(--mef-cyan);
      font-size: 12px;
      font-weight: 400;
      line-height: 1.45;
      text-align: left;
      white-space: normal;
      width: max-content;
      max-width: min(300px, 85vw);
      z-index: 200;
      pointer-events: none;
      box-shadow: 0 4px 14px rgba(16, 0, 82, 0.35);
    }
    /* END KPI-CSV-UPLOAD-TOOLTIP */
    body.monthly-edit-page .monthly-edit-float__top {
      padding-left: calc(14px + var(--mef-page-inset));
      padding-right: calc(14px + var(--mef-page-inset));
    }
    /* Global nav (same as Monthly index) */
    .nav-frame-btn[aria-current="page"] .btn-mode-frame {
      background: rgba(88, 225, 243, 0.18);
      border-radius: 2px;
    }
    .nav-btn-text {
      font-size: 10px;
      line-height: 1;
      letter-spacing: 0.05em;
    }
    .nav-frame-btn[aria-current="page"] .nav-btn-text {
      font-size: 11px;
      font-weight: 700;
    }
    html[lang="ja"] .si-fi:not(.office-mode) .global-nav-list {
      gap: 24px;
    }
    html[lang="ja"] .si-fi:not(.office-mode) .nav-frame-btn .btn-mode-frame {
      max-width: 120px;
    }
    html[lang="ja"] .si-fi:not(.office-mode) .nav-btn-text {
      font-size: 10px !important;
      line-height: 1 !important;
      letter-spacing: 0.05em;
      font-weight: 400;
    }
    html[lang="ja"] .si-fi:not(.office-mode) .nav-frame-btn[aria-current="page"] .nav-btn-text {
      font-size: 11px !important;
      font-weight: 700;
    }
    body.monthly-page.office-mode .nav-frame-btn[aria-current="page"] .btn-mode-frame,
    body.monthly-edit-page.office-mode .nav-frame-btn[aria-current="page"] .btn-mode-frame {
      background: #4a4a4a;
      border-color: rgba(255, 255, 255, 0.28);
    }
    body.monthly-page.office-mode .nav-frame-btn[aria-current="page"] .nav-btn-text,
    body.monthly-edit-page.office-mode .nav-frame-btn[aria-current="page"] .nav-btn-text {
      color: #ffffff;
      font-weight: 700;
      font-size: 12px;
      letter-spacing: 0.1em;
    }
    html[lang='en'] .office-mode .global-nav-list {
      gap: 50px;
    }
    html[lang='ja'] .office-mode .global-nav-list {
      gap: 80px;
    }
    html[lang='ja'] .office-mode .nav-frame-btn[aria-current='page'] .nav-btn-text {
      font-family: 'BIZ UDPGothic', sans-serif;
      letter-spacing: 0.06em;
    }
""" + CLOSE_CHOOSER_CSS

MEP_MEMO_FLAG_CSS = """
    .monthly-edit-float__memo-flag-cell {
      padding: 0;
      text-align: center;
      vertical-align: middle;
    }
    .monthly-edit-float__memo-flag-btn {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 100%;
      min-height: var(--mef-row-h);
      margin: 0;
      padding: 0;
      border: none;
      background: transparent;
      color: #1a1a1a;
      cursor: pointer;
      box-sizing: border-box;
    }
    .monthly-edit-float__memo-flag-btn[data-tooltip] {
      position: relative;
      z-index: 2;
    }
    .monthly-edit-float__memo-flag-btn[data-tooltip]:hover::after,
    .monthly-edit-float__memo-flag-btn[data-tooltip]:focus-visible::after {
      content: attr(data-tooltip);
      position: absolute;
      left: 50%;
      bottom: calc(100% + 8px);
      transform: translateX(-50%);
      padding: 8px 10px;
      border: 1px solid var(--mef-line);
      border-radius: 3px;
      background: #102932;
      color: var(--mef-cyan);
      font-size: 12px;
      font-weight: 400;
      line-height: 1.45;
      text-align: center;
      white-space: nowrap;
      width: max-content;
      max-width: min(280px, 85vw);
      z-index: 200;
      pointer-events: none;
      box-shadow: 0 4px 14px rgba(16, 0, 82, 0.35);
    }
    body.kpi-tutorial-hints-off .monthly-edit-float__memo-flag-btn[data-tooltip]:hover::after,
    body.kpi-tutorial-hints-off .monthly-edit-float__memo-flag-btn[data-tooltip]:focus-visible::after {
      content: none;
    }
    .monthly-edit-float__memo-flag-btn:hover,
    .monthly-edit-float__memo-flag-btn:focus-visible {
      outline: none;
      box-shadow: inset 0 0 0 1px rgba(242, 133, 0, 0.55);
    }
    .monthly-edit-float__memo-flag-icon {
      width: 22px;
      height: 22px;
      display: block;
      pointer-events: none;
    }
    body.office-mode .monthly-edit-float__memo-flag-btn {
      color: #5a5a5a;
    }
"""

MEP_BOTTOM_SPACER_CSS = """
    .monthly-edit-float__bottom-spacer {
      display: block;
      height: 100px;
      min-height: 100px;
      flex-shrink: 0;
      pointer-events: none;
    }
    .monthly-edit-float__table tr.monthly-edit-float__bottom-spacer td {
      height: 100px;
      min-height: 100px;
      padding: 0;
      border: none !important;
      background: transparent !important;
      pointer-events: none;
    }
"""

JS_PATCHES = [
    (
        "if (!root || !backdrop || !btnClose || !tbl || !elLabels || !scroller) return;",
        "if (!root || !btnClose || !tbl || !elLabels || !scroller) return;",
    ),
    (
        """      function syncFromPage() {
        var ui = window.__MONTHLY_UI;
        if (ui && typeof ui.getState === 'function') {
          var st = ui.getState();
          if (st && Number.isFinite(st.year) && Number.isFinite(st.month0)) {
            mefYear = st.year;
            mefMonth0 = st.month0;
          }
        }
      }""",
        """      var MEF_STORAGE_MONTHLY_LAST = 'kpiNavigator.monthlyLast';
      var mefPreferredIso = null;
      function syncFromPage() {
        var params = new URLSearchParams(window.location.search);
        var y = Number(params.get('year'));
        var m = Number(params.get('month'));
        var iso = String(params.get('iso') || '').trim();
        if (iso && /^\\d{4}-\\d{2}-\\d{2}$/.test(iso)) mefPreferredIso = iso;
        if (Number.isFinite(y) && m >= 1 && m <= 12) {
          mefYear = y;
          mefMonth0 = m - 1;
          return;
        }
        try {
          var raw = sessionStorage.getItem(MEF_STORAGE_MONTHLY_LAST);
          if (raw) {
            var o = JSON.parse(raw);
            if (o && Number.isFinite(o.year) && Number.isFinite(o.month0)) {
              mefYear = o.year;
              mefMonth0 = o.month0;
              return;
            }
          }
        } catch (_e) {}
        var ui = window.__MONTHLY_UI;
        if (ui && typeof ui.getState === 'function') {
          var st = ui.getState();
          if (st && Number.isFinite(st.year) && Number.isFinite(st.month0)) {
            mefYear = st.year;
            mefMonth0 = st.month0;
          }
        }
      }
      function persistMefMonth() {
        try {
          sessionStorage.setItem(
            MEF_STORAGE_MONTHLY_LAST,
            JSON.stringify({ year: mefYear, month0: mefMonth0 })
          );
        } catch (_e) {}
      }""",
    ),
    (
        """      function openFloat() {
        syncFromPage();
        undoStack = [];
        syncUndoButton();
        clearDirty();
        editSessionCommitted = false;
        buildGrid();
        confirmedSnapshot = buildConfirmedSnapshot();
        root.hidden = false;
        document.body.style.overflow = 'hidden';
        scroller.scrollTop = 0;
        applyZoom();
        scrollToPreferredDayLeft();
        syncLabelScroll();
        btnClose.focus();
      }""",
        """      function scrollToIsoColumn(iso) {
        if (!scroller || !tbl || !iso) return;
        var ths = tbl.querySelectorAll('thead th');
        if (!ths || !ths.length) return;
        var parts = iso.split('-');
        if (parts.length < 3) return;
        var d = Number(parts[2]);
        if (!Number.isFinite(d) || d < 1) return;
        var dayIdx = Math.max(0, Math.min(ths.length - 1, d - 1));
        var target = ths[dayIdx];
        var left = (target ? target.offsetLeft : 0) * currentScale;
        scroller.scrollLeft = left;
      }
      function initEditPage() {
        syncFromPage();
        undoStack = [];
        syncUndoButton();
        clearDirty();
        editSessionCommitted = false;
        buildGrid();
        confirmedSnapshot = buildConfirmedSnapshot();
        persistMefMonth();
        scroller.scrollTop = 0;
        applyZoom();
        if (mefPreferredIso) scrollToIsoColumn(mefPreferredIso);
        else scrollToPreferredDayLeft();
        syncLabelScroll();
        if (btnClose) btnClose.focus();
      }""",
    ),
    (
        """      function closeFloat() {
        closeMonthPicker();
        root.hidden = true;
        document.body.style.overflow = '';
      }""",
        """      function navigateBackToMonthly() {
        closeMonthPicker();
        window.location.href = '../index.html';
      }""",
    ),
    (
        "      document.addEventListener('monthly:vfocusEditRequested', openFloat);",
        "",
    ),
    (
        "      backdrop.addEventListener('click', requestCloseFloat);",
        "",
    ),
    (
        """      function allowEditNavigation() {
        if (!editTouched) {
          return window.confirm(t('本当に離れますか？', 'Leave this page?'));
        }
        if (!hasUnsavedChanges()) return true;
        if (window.confirm(t('未保存の入力があります。保存しますか？', 'You have unsaved changes. Save them?'))) {
          if (btnConfirm) btnConfirm.click();
          return true;
        }
        return window.confirm(t('保存せずに離れますか？', 'Leave without saving?'));
      }
      function confirmDiscardEdits() {
        return allowEditNavigation();
      }""",
        close_chooser_js(
            "if (btnConfirm) btnConfirm.click();"
        )
        + """
      function confirmDiscardEdits() {
        return requestLeaveNavigation();
      }""",
    ),
    (
        """      function requestCloseFloat() {
        if (!confirmDiscardEdits()) return;
        clearDirty();
        navigateBackToMonthly();
      }""",
        """      function requestCloseFloat() {
        requestLeaveNavigation().then(function (ok) {
          if (!ok) return;
          clearDirty();
          navigateBackToMonthly();
        });
      }""",
    ),
    (
        """      function goToProfitLossPage() {
        if (!allowEditNavigation()) return;
        var editReturn =""",
        """      function goToProfitLossPage() {
        requestLeaveNavigation().then(function (ok) {
          if (!ok) return;
        var editReturn =""",
    ),
    (
        """        window.location.href = href;
      }
      if (btnProfitLoss) {""",
        """        window.location.href = href;
        });
      }
      if (btnProfitLoss) {""",
    ),
    (
        """      document.querySelectorAll('.global-nav a.nav-frame-btn[href]').forEach(function (el) {
        el.addEventListener('click', function (e) {
          if (!allowEditNavigation()) e.preventDefault();
        });
      });""",
        """      function isInternalLeaveLink(a) {
        if (!a || !a.getAttribute) return false;
        var href = (a.getAttribute('href') || '').trim();
        if (!href || href === '#') return false;
        if (/^javascript:/i.test(href)) return false;
        if (a.target === '_blank') return false;
        if (/^https?:\\/\\//i.test(href)) return false;
        if (href.charAt(0) === '#') return false;
        return true;
      }
      function resolveLeaveHref(a) {
        if (a.id === 'global-nav-index-btn') {
          var tierKey = 'kpiNavigator.subscriptionTier';
          try {
            if ((sessionStorage.getItem(tierKey) || localStorage.getItem(tierKey)) === 'basic') {
              var hrefBasic = a.getAttribute('data-href-basic');
              if (hrefBasic) return new URL(hrefBasic, window.location.href).href;
            }
          } catch (_e) {}
          var hrefPro = a.getAttribute('data-href-pro') || a.getAttribute('href') || '';
          if (hrefPro) return new URL(hrefPro, window.location.href).href;
        }
        var href = monthlyOverlayHref(a);
        if (!href || href === '#') href = a.getAttribute('href') || '';
        try {
          return new URL(href, window.location.href).href;
        } catch (_e) {
          return href;
        }
      }
      document.addEventListener(
        'click',
        function (e) {
          if (root.hidden) return;
          var a = e.target && e.target.closest ? e.target.closest('a[href]') : null;
          if (!isInternalLeaveLink(a)) return;
          e.preventDefault();
          e.stopPropagation();
          var targetHref = resolveLeaveHref(a);
          requestLeaveNavigation().then(function (ok) {
            if (ok) window.location.href = targetHref;
          });
        },
        true
      );""",
    ),
    (
        """        rows.push({ type: 'bizday', id: 'bizday', labelJa: '営業日', labelEn: 'Business Day' });
        rows.push({
          type: 'aggregate',
          id: 'totalSales',""",
        """        rows.push({ type: 'bizday', id: 'bizday', labelJa: '営業日', labelEn: 'Business Day' });
        rows.push({ type: 'aggregate', id: 'profit', labelJa: 'Profit', labelEn: 'Profit', section: 'profit' });
        rows.push({
          type: 'aggregate',
          id: 'totalSales',""",
    ),
    (
        """        rows.push({ type: 'weatherRow', id: 'weather' });
        rows.push({ type: 'aggregate', id: 'profit', labelJa: 'Profit', labelEn: 'Profit', section: 'profit' });
        return rows;""",
        """        rows.push({ type: 'weatherRow', id: 'weather' });
        return rows;""",
    ),
    (
        """        rows.push({ type: 'group', id: 'g-memo', labelJa: '日次メモ', labelEn: 'Daily Notes' });
        rows.push({
          type: 'aggregate',
          id: 'memoHead',
          labelJa: 'メモ',
          labelEn: 'Memo',
          section: 'memo',
          plusminus: 'memo'
        });
        if (!state.collapsed.memo) {
          state.memoItems.forEach(function (r) {
            rows.push({ type: 'memoRow', row: r, section: 'memo' });
          });
        }
        rows.push({ type: 'group', id: 'g-weather', labelJa: 'WEATHER', labelEn: 'WEATHER' });
        rows.push({ type: 'weatherRow', id: 'weather' });""",
        """        rows.push({ type: 'group', id: 'g-weather', labelJa: 'WEATHER', labelEn: 'WEATHER' });
        rows.push({ type: 'weatherRow', id: 'weather' });
        rows.push({ type: 'group', id: 'g-memo', labelJa: '日次メモ', labelEn: 'Daily Notes' });
        rows.push({
          type: 'aggregate',
          id: 'memoHead',
          labelJa: 'メモ',
          labelEn: 'Memo',
          section: 'memo',
          plusminus: 'memo'
        });
        if (!state.collapsed.memo) {
          syncWeeklyMemoItems();
          state.memoItems.forEach(function (r) {
            rows.push({ type: 'memoRow', row: r, section: 'memo' });
          });
        }""",
    ),
    (
        """        });

        tbl.innerHTML = '';""",
        """        });

        var spacerLabel = document.createElement('div');
        spacerLabel.className = 'monthly-edit-float__bottom-spacer';
        spacerLabel.setAttribute('aria-hidden', 'true');
        elLabels.appendChild(spacerLabel);
        var trSpacer = document.createElement('tr');
        trSpacer.className = 'monthly-edit-float__bottom-spacer';
        trSpacer.setAttribute('aria-hidden', 'true');
        var tdSpacer = document.createElement('td');
        tdSpacer.colSpan = isoList.length;
        trSpacer.appendChild(tdSpacer);
        tbody.appendChild(trSpacer);

        tbl.innerHTML = '';""",
    ),
]

JS_APPEND = """
      initEditPage();
"""

NAV_HELPER = """
    (function () {
      var STORAGE_MONTHLY_LAST = 'kpiNavigator.monthlyLast';
      window.__MONTHLY_EDIT_NAV__ = {
        go: function (isoDate) {
          var href = 'edit/index.html';
          var q = [];
          try {
            if (window.__MONTHLY_UI && typeof window.__MONTHLY_UI.getState === 'function') {
              var st = window.__MONTHLY_UI.getState();
              if (st && Number.isFinite(st.year)) q.push('year=' + encodeURIComponent(String(st.year)));
              if (st && Number.isFinite(st.month0)) q.push('month=' + encodeURIComponent(String(st.month0 + 1)));
            } else {
              var raw = sessionStorage.getItem(STORAGE_MONTHLY_LAST);
              if (raw) {
                var o = JSON.parse(raw);
                if (o && Number.isFinite(o.year)) q.push('year=' + encodeURIComponent(String(o.year)));
                if (o && Number.isFinite(o.month0)) q.push('month=' + encodeURIComponent(String(o.month0 + 1)));
              }
            }
          } catch (_e) {}
          if (isoDate) q.push('iso=' + encodeURIComponent(String(isoDate)));
          if (q.length) href += '?' + q.join('&');
          window.location.href = href;
        }
      };
    })();
"""

OFFICE_SCRIPTS = """
  <script>
    (function () {
      var STORAGE_KEY = 'kpi-office-mode';
      var bodyEl = document.getElementById('body-el');
      var btnModeToggle = document.getElementById('btn-mode-toggle');
      var btnModeText = document.getElementById('btn-mode-text');
      var settingsOfficeLabel = document.getElementById('settings-office-label');
      function updateModeButton() {
        if (!btnModeText || !btnModeToggle) return;
        var isOffice = bodyEl && bodyEl.classList.contains('office-mode');
        btnModeText.textContent = isOffice ? 'SCI-FI MODE' : 'OFFICE MODE';
        btnModeToggle.setAttribute('aria-label', isOffice ? 'Switch to Sci-Fi Mode' : 'Switch to Office Mode');
        if (settingsOfficeLabel) {
          settingsOfficeLabel.textContent = isOffice ? 'Sci-Fi Mode' : 'Office Mode';
        }
      }
      if (bodyEl && btnModeToggle) {
        if (sessionStorage.getItem(STORAGE_KEY) === '1') {
          bodyEl.classList.add('office-mode');
        }
        btnModeToggle.addEventListener('click', function (e) {
          e.preventDefault();
          bodyEl.classList.toggle('office-mode');
          if (bodyEl.classList.contains('office-mode')) {
            sessionStorage.setItem(STORAGE_KEY, '1');
          } else {
            sessionStorage.removeItem(STORAGE_KEY);
          }
          updateModeButton();
        });
        updateModeButton();
      }
    })();
    (function () {
      var STORAGE_KEY = 'kpi-office-mode';
      document.addEventListener('click', function (ev) {
        var t = ev.target;
        if (!t || !t.closest) return;
        var a = t.closest('a[href]');
        if (!a) return;
        var href = String(a.getAttribute('href') || '').trim();
        if (!href || href === '#' || href.indexOf('javascript:') === 0) return;
        if (href.indexOf('mailto:') === 0 || href.indexOf('tel:') === 0) return;
        if (a.getAttribute('target') === '_blank') return;
        var isOffice = document.body.classList.contains('office-mode');
        try {
          if (isOffice) sessionStorage.setItem(STORAGE_KEY, '1');
          else sessionStorage.removeItem(STORAGE_KEY);
        } catch (_err) {}
      });
    })();
    (function () {
      var menuBtn = document.querySelector('.icon-button-menu');
      var dropdown = document.getElementById('settings-dropdown');
      var officeToggle = document.getElementById('settings-office-toggle');
      if (!menuBtn || !dropdown) return;
      menuBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        dropdown.hidden = !dropdown.hidden;
      });
      if (officeToggle) {
        officeToggle.addEventListener('click', function (e) {
          e.preventDefault();
          e.stopPropagation();
          var modeBtn = document.getElementById('btn-mode-toggle');
          if (modeBtn) modeBtn.click();
        });
      }
      dropdown.addEventListener('click', function (e) {
        e.stopPropagation();
      });
      document.addEventListener('click', function () {
        dropdown.hidden = true;
      });
    })();
    (function () {
      var gearBtn = document.getElementById('btn-account-settings');
      var accountPopup = document.getElementById('account-settings-popup');
      var menuDropdown = document.getElementById('settings-dropdown');
      if (!gearBtn || !accountPopup) return;
      gearBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        var isOpen = !accountPopup.hidden;
        accountPopup.hidden = isOpen;
        gearBtn.setAttribute('aria-expanded', !isOpen);
        if (!isOpen && menuDropdown) menuDropdown.hidden = true;
      });
      accountPopup.addEventListener('click', function (e) {
        e.stopPropagation();
      });
      document.addEventListener('click', function () {
        accountPopup.hidden = true;
        gearBtn.setAttribute('aria-expanded', 'false');
      });
    })();
    (function () {
      var btn = document.getElementById('global-nav-index-btn');
      if (!btn) return;
      var KEY = 'kpiNavigator.subscriptionTier';
      function isBasicPlan() {
        try {
          return (sessionStorage.getItem(KEY) || localStorage.getItem(KEY)) === 'basic';
        } catch (e) {
          return false;
        }
      }
      var hrefPro = btn.getAttribute('data-href-pro');
      var hrefBasic = btn.getAttribute('data-href-basic');
      if (hrefPro) btn.setAttribute('href', hrefPro);
      btn.addEventListener('click', function (ev) {
        if (!isBasicPlan()) return;
        ev.preventDefault();
        if (hrefBasic) window.location.href = hrefBasic;
      });
    })();
  </script>
"""


def extract_between(text: str, start: str, end: str) -> str:
    i = text.find(start)
    if i < 0:
        raise ValueError(f"start marker not found: {start[:60]!r}")
    j = text.find(end, i + len(start))
    if j < 0:
        raise ValueError(f"end marker not found after start: {end[:60]!r}")
    return text[i:j]


def patch_css(css: str) -> str:
    css = css.replace(
        "/* Monthly Edit Floating Window",
        "/* Monthly Edit page (extracted from monthly index)",
        1,
    )
    css = css.replace(
        ".monthly-edit-float[hidden] {\n      display: none !important;\n    }\n    .monthly-edit-float {",
        ".monthly-edit-float {",
        1,
    )
    old_shell = """    .monthly-edit-float {
      --mef-cyan: #58e1f3;
      --mef-line: #58e1f3;
      --mef-panel: #2c2c2c;
      --mef-fixed: #252525;
      --mef-th-h: 36px;
      --mef-row-h: 36px;
      --mef-group-h: 28px;
      --mef-profit-h: 44px;
      --mef-label-w: 320px;
      --mef-col-min: 88px;
      position: fixed;
      inset: 0;
      z-index: 20100;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 16px;
      box-sizing: border-box;
      font-family: 'BIZ UDPGothic', sans-serif;
    }"""
    new_shell = """    .monthly-edit-float {
      --mef-cyan: #58e1f3;
      --mef-line: #58e1f3;
      --mef-panel: #2c2c2c;
      --mef-fixed: #252525;
      --mef-th-h: 36px;
      --mef-row-h: 36px;
      --mef-group-h: 28px;
      --mef-profit-h: 44px;
      --mef-label-w: 320px;
      --mef-col-min: 88px;
      position: relative;
      z-index: 1;
      display: flex;
      flex-direction: column;
      flex: 1;
      width: 100%;
      max-width: 100%;
      min-height: 0;
      padding: 12px 16px 16px;
      box-sizing: border-box;
      font-family: 'BIZ UDPGothic', sans-serif;
    }"""
    css = css.replace(old_shell, new_shell, 1)
    css = css.replace(
        """    .monthly-edit-float__backdrop {
      position: absolute;
      inset: 0;
      background: rgba(0, 0, 0, 0.55);
      cursor: pointer;
    }""",
        """    .monthly-edit-float__backdrop {
      display: none !important;
    }""",
        1,
    )
    panel_old = re.search(
        r"    \.monthly-edit-float__panel \{[^}]+\}",
        css,
        re.DOTALL,
    )
    if panel_old:
        css = css.replace(
            panel_old.group(0),
            """    .monthly-edit-float__panel {
      position: relative;
      z-index: 1;
      width: min(1400px, 100%);
      height: auto;
      max-height: none;
      margin: 0 auto;
      box-sizing: border-box;
      background: var(--mef-panel);
      border: 1px solid var(--mef-line);
      border-radius: 6px;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
      display: flex;
      flex-direction: column;
      color: var(--mef-cyan);
      overflow: hidden;
      flex: 1;
    }""",
            1,
        )
    profit_label_old = """    .monthly-edit-float__label-row--profit {
      height: var(--mef-profit-h);
      min-height: var(--mef-profit-h);
      border-top: 1px solid rgba(88, 225, 243, 0.5);
      font-size: 13px;
      font-weight: 800;
      color: #58e1f3;
      background: rgba(88, 225, 243, 0.08);
    }"""
    profit_label_new = """    .monthly-edit-float__label-row--profit {
      height: var(--mef-profit-h);
      min-height: var(--mef-profit-h);
      border-bottom: 1px solid rgba(88, 225, 243, 0.65);
      font-size: 15px;
      font-weight: 800;
      letter-spacing: 0.04em;
      color: #58e1f3;
      background: rgba(88, 225, 243, 0.14);
    }"""
    if profit_label_old in css:
        css = css.replace(profit_label_old, profit_label_new, 1)
    profit_row_old = """    .monthly-edit-float__table tr.monthly-edit-float__profit-row td {
      border-top: 1px solid rgba(88, 225, 243, 0.6);
      background: rgba(88, 225, 243, 0.08);
      height: var(--mef-profit-h);
      font-size: 13px;
      font-weight: 700;
    }"""
    profit_row_new = """    .monthly-edit-float__table tr.monthly-edit-float__profit-row td {
      border-bottom: 1px solid rgba(88, 225, 243, 0.65);
      background: rgba(88, 225, 243, 0.14);
      height: var(--mef-profit-h);
      font-size: 15px;
      font-weight: 700;
      letter-spacing: 0.02em;
    }"""
    if profit_row_old in css:
        css = css.replace(profit_row_old, profit_row_new, 1)
    office_profit_label_old = """    body.office-mode .monthly-edit-float__label-row--profit {
      border-top-color: #444;
      color: #111;
      background: #e7e7e7;
    }"""
    office_profit_label_new = """    body.office-mode .monthly-edit-float__label-row--profit {
      border-bottom-color: #444;
      color: #111;
      background: #dcdcdc;
    }"""
    if office_profit_label_old in css:
        css = css.replace(office_profit_label_old, office_profit_label_new, 1)
    office_profit_row_old = """    body.office-mode .monthly-edit-float__table tr.monthly-edit-float__profit-row td {
      border-top-color: #444;
      background: #e7e7e7;
      color: #111;
    }"""
    office_profit_row_new = """    body.office-mode .monthly-edit-float__table tr.monthly-edit-float__profit-row td {
      border-bottom-color: #444;
      background: #dcdcdc;
      color: #111;
    }"""
    if office_profit_row_old in css:
        css = css.replace(office_profit_row_old, office_profit_row_new, 1)
    return CSS_PAGE_PATCH + css + MEP_BOTTOM_SPACER_CSS + MEP_MEMO_FLAG_CSS


def patch_js(js: str) -> str:
    for old, new in JS_PATCHES:
        if old not in js:
            raise ValueError(f"JS patch miss:\\n{old[:120]}")
        js = js.replace(old, new, 1)
    if "buildGrid();" in js and "persistMefMonth();" not in js:
        js = js.replace("        buildGrid();\n      }", "        buildGrid();\n        persistMefMonth();\n      }", 2)
    if not js.rstrip().endswith("initEditPage();"):
        js = js.rstrip() + "\n" + JS_APPEND
    return js


def patch_html(html: str, cfg: dict) -> str:
    html = re.sub(r"\n    hidden\n", "\n", html, count=1)
    html = html.replace('role="dialog"', 'role="region"')
    html = html.replace('aria-modal="true"', '')
    html = re.sub(
        r'aria-label="(?:Close|閉じる)"',
        f'aria-label="{cfg["close_aria"]}"',
        html,
        count=1,
    )
    html = re.sub(
        r'(id="monthly-edit-float-close"[^>]*>)\s*[×x]\s*(</button>)',
        rf"\1{cfg['close_char']}\2",
        html,
        count=1,
        flags=re.IGNORECASE,
    )
    html = re.sub(
        r'<div class="monthly-edit-float__backdrop[^>]*></div>\s*',
        "",
        html,
        count=1,
    )
    html = re.sub(
        r'\s*<div class="monthly-edit-float__labels-footer-spacer"[^>]*></div>',
        "",
        html,
        count=1,
    )
    return html


def extract_header_tail(src: str, setting_prefix: str) -> str:
    m = re.search(
        r'(<div class="account-settings-popup" id="account-settings-popup".*?</div>\s*</div>\s*</header>)',
        src,
        re.DOTALL,
    )
    if not m:
        raise ValueError("header tail (account popup + settings dropdown) not found")
    block = m.group(1)
    block = block.replace("../../setting/", setting_prefix)
    block = block.replace('../../../en/setting/', setting_prefix)
    return block


def build_page(cfg: dict) -> str:
    src_text = cfg["src"].read_text(encoding="utf-8")
    css = patch_css(extract_between(src_text, CSS_START, CSS_END))
    html_block = patch_html(
        extract_between(src_text, HTML_START, HTML_END).strip(),
        cfg,
    )
    js_body = patch_js(
        extract_between(src_text, JS_START, JS_END_MARKER).rstrip()
    )
    header_tail = extract_header_tail(src_text, cfg["setting_prefix"])

    lang_attr = cfg["lang"]
    if cfg["lang"] == "en":
        font_rule = "html[lang='en'] body.si-fi:not(.office-mode) .monthly-edit-float"
    else:
        font_rule = "html[lang='ja'] body.si-fi:not(.office-mode) .monthly-edit-float"

    return f"""<!DOCTYPE html>
<html lang="{lang_attr}"{cfg["translate_no"]}>
<head>
  <meta charset="UTF-8">
{cfg["content_lang_meta"]}  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{cfg["title"]}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=BIZ+UDP+Gothic:wght@400;500;700&family=Orbitron:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{cfg["register_css"]}">
  <link rel="stylesheet" href="{cfg["setting_css"]}">
  <style>
{css}
  </style>
</head>
<body class="si-fi profile-page monthly-page monthly-edit-page{cfg["body_extra_class"]}" id="body-el">
  <header class="site-header">
    <div class="header-inner">
      <div class="header-logo">
        <a href="{cfg["forge_href"]}" class="logo-link" aria-label="{cfg["forge_aria"]}" target="_blank" rel="noopener noreferrer">
          <img src="{cfg["images_prefix"]}forge_lab_logo.png" alt="FORGE LABORATORY" class="logo-img">
        </a>
      </div>
      <nav class="global-nav" aria-label="{cfg["nav_aria"]}">
        <ul class="global-nav-list">
          <li class="global-nav-item">
            <a href="{cfg["annual_href"]}" class="nav-frame-btn" aria-label="{cfg["annual_label"]}">
              <span class="btn-mode-frame">
                <img src="{cfg["images_prefix"]}button_frame.svg" alt="" class="btn-mode-frame-img" aria-hidden="true">
                <span class="btn-mode-text nav-btn-text">{cfg["annual_label"]}</span>
              </span>
            </a>
          </li>
          <li class="global-nav-item">
            <a href="{cfg["monthly_nav_href"]}" class="nav-frame-btn" aria-label="{cfg["monthly_label"]}" aria-current="page">
              <span class="btn-mode-frame">
                <img src="{cfg["images_prefix"]}button_frame.svg" alt="" class="btn-mode-frame-img" aria-hidden="true">
                <span class="btn-mode-text nav-btn-text">{cfg["monthly_label"]}</span>
              </span>
            </a>
          </li>
          <li class="global-nav-item">
            <a href="{cfg["daily_href"]}" class="nav-frame-btn" id="global-nav-daily-btn" aria-label="{cfg["daily_label"]}">
              <span class="btn-mode-frame">
                <img src="{cfg["images_prefix"]}button_frame.svg" alt="" class="btn-mode-frame-img" aria-hidden="true">
                <span class="btn-mode-text nav-btn-text">{cfg["daily_label"]}</span>
              </span>
            </a>
          </li>
          <li class="global-nav-item">
            <a
              href="{cfg["profit_href"]}"
              class="nav-frame-btn"
              id="global-nav-index-btn"
              data-href-pro="{cfg["profit_href"]}"
              data-href-basic="{cfg["profit_basic_href"]}"
              aria-label="{cfg["insight_label"]}"
            >
              <span class="btn-mode-frame">
                <img src="{cfg["images_prefix"]}button_frame.svg" alt="" class="btn-mode-frame-img" aria-hidden="true">
                <span class="btn-mode-text nav-btn-text">{cfg["insight_label"]}</span>
              </span>
            </a>
          </li>
        </ul>
      </nav>
      <div class="header-actions">
        <a href="#" class="btn-mode" id="btn-mode-toggle" role="button" aria-label="{cfg["office_toggle_aria"]}">
          <span class="btn-mode-frame">
            <img src="{cfg["images_prefix"]}button_frame.svg" alt="" class="btn-mode-frame-img" aria-hidden="true">
            <span class="btn-mode-text" id="btn-mode-text">OFFICE MODE</span>
          </span>
        </a>
        <button type="button" class="icon-button icon-button-menu" aria-label="{cfg["menu_aria"]}">
          <img src="{cfg["images_prefix"]}dropdown_menu.svg" alt="" class="icon-img" aria-hidden="true">
        </button>
        <button type="button" class="icon-button icon-button-settings" id="btn-account-settings" aria-label="{cfg["gear_aria"]}" aria-expanded="false" aria-haspopup="true">
          <img src="{cfg["images_prefix"]}setting_gear.svg" alt="" class="icon-img" aria-hidden="true">
        </button>
      </div>
      {header_tail}

  {html_block}

{CLOSE_CHOOSER_HTML[cfg["lang"]]}
  <div class="lang-select-wrap" id="lang-select-wrap" data-url-en="{cfg["lang_switch_en"]}" data-url-ja="{cfg["lang_switch_ja"]}">
    <button type="button" class="lang-select-btn" id="lang-select-btn" aria-expanded="false" aria-haspopup="listbox" aria-label="Select language">
      <span class="lang-code" aria-hidden="true">{'JP' if cfg['lang'] == 'ja' else 'EN'}</span>
      <span class="lang-name">{'日本語' if cfg['lang'] == 'ja' else 'English'}</span>
      <span class="lang-chevron" aria-hidden="true"></span>
    </button>
    <div class="lang-select-dropdown" id="lang-select-dropdown" role="listbox" aria-label="Language options" hidden>
      <button type="button" class="lang-option lang-option-ja{' lang-option-active' if cfg['lang'] == 'ja' else ''}" role="option" data-lang="ja">JP - Japanese</button>
      <button type="button" class="lang-option lang-option-en{' lang-option-active' if cfg['lang'] == 'en' else ''}" role="option" data-lang="en">EN - English</button>
    </div>
  </div>
{OFFICE_SCRIPTS}
  <script>
    (function () {{
      var langBtn = document.getElementById('lang-select-btn');
      var langDropdown = document.getElementById('lang-select-dropdown');
      var langOptions = document.querySelectorAll('.lang-option');
      var langWrap = document.getElementById('lang-select-wrap');
      if (!langBtn || !langDropdown || !langWrap) return;
      langBtn.addEventListener('click', function (e) {{
        e.stopPropagation();
        langDropdown.hidden = !langDropdown.hidden;
        langBtn.setAttribute('aria-expanded', langDropdown.hidden ? 'false' : 'true');
      }});
      langOptions.forEach(function (opt) {{
        opt.addEventListener('click', function () {{
          var lang = opt.getAttribute('data-lang');
          var url = lang === 'ja' ? langWrap.getAttribute('data-url-ja') : langWrap.getAttribute('data-url-en');
          if (!url) return;
          var go = function () {{ window.location.href = url; }};
          if (typeof requestLeaveNavigation === 'function') {{
            requestLeaveNavigation().then(function (ok) {{ if (ok) go(); }});
          }} else {{
            go();
          }}
        }});
      }});
      document.addEventListener('click', function () {{
        langDropdown.hidden = true;
        langBtn.setAttribute('aria-expanded', 'false');
      }});
    }})();
  </script>
  <script>
    (function () {{
{js_body}
    }})();
  </script>
</body>
</html>
"""


def strip_from_monthly(src_path: Path) -> None:
    text = src_path.read_text(encoding="utf-8")
    css_block = extract_between(text, CSS_START, CSS_END)
    html_block = extract_between(text, HTML_START, HTML_END)
    js_block = extract_between(text, JS_START, JS_END_MARKER)

    if css_block not in text or html_block not in text or js_block not in text:
        raise ValueError(f"blocks missing in {src_path}")

    text = text.replace(css_block, "", 1)
    text = text.replace(html_block, "", 1)
    text = text.replace(js_block, "", 1)

    text = text.replace(
        """      topEditBtn.addEventListener('click', function () {
        document.dispatchEvent(new CustomEvent('monthly:vfocusEditRequested', {
          detail: {
            isoDate: null
          }
        }));
      });""",
        """      topEditBtn.addEventListener('click', function () {
        if (window.__MONTHLY_EDIT_NAV__) window.__MONTHLY_EDIT_NAV__.go(null);
      });""",
        1,
    )

    text = text.replace(
        """        vEditBtn.addEventListener('click', function () {
          document.dispatchEvent(new CustomEvent('monthly:vfocusEditRequested', {
            detail: {
              isoDate: currentFocusIso || readDailySelectedIso() || null
            }
          }));
        });""",
        """        vEditBtn.addEventListener('click', function () {
          if (window.__MONTHLY_EDIT_NAV__) {
            window.__MONTHLY_EDIT_NAV__.go(currentFocusIso || readDailySelectedIso() || null);
          }
        });""",
        1,
    )

    if "window.__MONTHLY_EDIT_NAV__ = {" not in text:
        text = text.replace("</body>", NAV_HELPER + "\n</body>", 1)

    src_path.write_text(text, encoding="utf-8")


def main() -> None:
    for cfg in CONFIGS:
        out = cfg["out"]
        out.parent.mkdir(parents=True, exist_ok=True)
        page = build_page(cfg)
        out.write_text(page, encoding="utf-8")
        print(f"wrote {out.relative_to(ROOT)} ({len(page)} bytes)")
        strip_from_monthly(cfg["src"])
        print(f"patched {cfg['src'].relative_to(ROOT)}")


if __name__ == "__main__":
    main()
    import subprocess
    import sys

    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "apply_daily_sales_import.py")],
        cwd=str(ROOT),
        check=False,
    )
    subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; from pathlib import Path; "
            "sys.path.insert(0, 'scripts'); "
            "from apply_kpi_year_store import patch_mep, MEP_TARGETS; "
            "[patch_mep(t) for t in MEP_TARGETS]",
        ],
        cwd=str(ROOT),
        check=False,
    )
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "apply_mep_store.py")],
        cwd=str(ROOT),
        check=False,
    )
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "apply_kpi_phase5.py")],
        cwd=str(ROOT),
        check=False,
    )
