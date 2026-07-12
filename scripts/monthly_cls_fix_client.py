"""Monthly CLS fixes — reserve layout before paint / hydrate."""

from __future__ import annotations

MONTHLY_CLS_MARKER = "/* KPI-MONTHLY-CLS-FIX */"

HTML_ROOT_OLD = '<html lang="ja">'
HTML_ROOT_NEW = '<html lang="ja" data-monthly-tw-hydrated="0">'

HTML_ROOT_EN_OLD = '<html lang="en">'
HTML_ROOT_EN_NEW = '<html lang="en" data-monthly-tw-hydrated="0">'

BODY_BOOT_OLD = '<body class="si-fi profile-page monthly-page" id="body-el">'
BODY_BOOT_SCRIPT_OLD = """  <script>/* KPI-MONTHLY-CLS-BOOT */(function(){try{if(localStorage.getItem('kpi-annual-focus-bar-expanded')==='1'){document.body.classList.add('annual-focus-bar-expanded');}}catch(e){}})();</script>"""

BODY_BOOT_SCRIPT_NEW = """  <script>/* KPI-MONTHLY-CLS-BOOT */(function(){try{if(localStorage.getItem('kpi-annual-focus-bar-expanded')!=='1')return;document.body.classList.add('annual-focus-bar-expanded');var prep=function(){var img=document.getElementById('annual-daily-focus-bar-img');if(!img)return;var office=document.body.classList.contains('office-mode');var src=img.getAttribute('src')||'';var dir=src.indexOf('/')>=0?src.slice(0,src.lastIndexOf('/')+1):'../../images/';img.setAttribute('src',dir+(office?'focus_bar_office_mode_open.svg':'focus_bar_open.svg'));img.setAttribute('width','1132');};if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',prep,{once:true});else prep();}catch(e){}})();</script>"""

BODY_BOOT_NEW = BODY_BOOT_OLD + "\n" + BODY_BOOT_SCRIPT_NEW

FRAME_IMG_CSS_OLD = """    .annual-frame-img {
      width: 100%;
      display: block;
      height: auto;
    }"""

FRAME_IMG_CSS_NEW = f"""    {MONTHLY_CLS_MARKER}
    .annual-frame-img {{
      width: 100%;
      display: block;
      height: auto;
    }}
    .annual-frame-close .annual-frame-img,
    .annual-area-top-svg .annual-frame-img[src*="area_close"] {{
      aspect-ratio: 1017 / 362;
    }}
    .annual-frame-open .annual-area-top-svg .annual-frame-img {{
      aspect-ratio: 1017 / 358;
    }}
    .annual-frame-img[src*="area_open_bottom"] {{
      aspect-ratio: 1017 / 20;
    }}
    .annual-area-top-svg {{
      position: relative;
      display: block;
      width: 100%;
    }}
    .annual-frame-close .annual-area-top-svg {{
      aspect-ratio: 1017 / 362;
    }}
    .annual-frame-open .annual-area-top-svg {{
      aspect-ratio: 1017 / 358;
    }}"""

MONTHLY_CELL_CSS_OLD = """    .monthly-data-column__cell {
      box-sizing: border-box;
      border-bottom: 1px solid #58e1f3;
      min-height: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 0 4px;
      color: #58e1f3;
      font-family: 'Orbitron', sans-serif;
      font-size: 13px;
      line-height: 1;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }"""

MONTHLY_CELL_CSS_NEW = f"""    .monthly-data-column__cell {{
      box-sizing: border-box;
      border-bottom: 1px solid #58e1f3;
      min-height: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 0 4px;
      color: #58e1f3;
      font-family: 'Orbitron', sans-serif;
      font-size: 13px;
      line-height: 1;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      font-variant-numeric: tabular-nums;
      min-width: 5.5em;
    }}
    .annual-daily-row__cell,
    .annual-daily-focus-bar-lower__cell,
    .annual-daily-focus-bar-upper__cell,
    .annual-open-table td,
    .annual-total-bd-value,
    .annual-target-sales-value,
    .annual-kpi-value {{
      font-variant-numeric: tabular-nums;
    }}
    .annual-daily-focus-bar-img {{
      aspect-ratio: 757 / 91;
      height: auto;
    }}
    body.annual-focus-bar-expanded .annual-daily-focus-bar-img {{
      aspect-ratio: 1132 / 91;
    }}"""

DASH_ROW6_OLD = """      var OFF_CELL_DASH = '-';
      function dashRow6() {
        return [OFF_CELL_DASH, OFF_CELL_DASH, OFF_CELL_DASH, OFF_CELL_DASH, OFF_CELL_DASH, OFF_CELL_DASH];
      }"""

DASH_ROW6_NEW = """      var OFF_CELL_DASH = '-';
      var TW_SKELETON_MONEY = '\\u00a50,000,000';
      var TW_SKELETON_PCT = '000%';
      function dashRow6() {
        return [
          TW_SKELETON_MONEY,
          TW_SKELETON_MONEY,
          TW_SKELETON_MONEY,
          TW_SKELETON_MONEY,
          TW_SKELETON_MONEY,
          TW_SKELETON_PCT,
        ];
      }"""

FOCUS_BAR_INIT_OLD = """      var initialExpanded = false;
      try {
        initialExpanded = localStorage.getItem(STORAGE_FOCUS_BAR) === '1';
      } catch (e1) {}
      setFocusBarExpanded(initialExpanded);"""

FOCUS_BAR_INIT_NEW = """      var initialExpanded = false;
      try {
        initialExpanded = localStorage.getItem(STORAGE_FOCUS_BAR) === '1';
      } catch (e1) {}
      var alreadyExpanded = document.body.classList.contains('annual-focus-bar-expanded');
      if (initialExpanded === alreadyExpanded) {
        updateFocusBarImage(initialExpanded);
        if (moreBtn) moreBtn.setAttribute('aria-expanded', initialExpanded ? 'true' : 'false');
        wingHitBtn.setAttribute('aria-label', initialExpanded ? '日次テーブルを縮小' : '日次テーブルを展開');
        window.__ANNUAL_UI = window.__ANNUAL_UI || {};
        window.__ANNUAL_UI.focusBarExpanded = initialExpanded;
        window.__ANNUAL_UI.refreshFocusBarAsset = function () {
          updateFocusBarImage(document.body.classList.contains('annual-focus-bar-expanded'));
        };
      } else {
        setFocusBarExpanded(initialExpanded);
      }"""

AREA_CLOSE_IMG_OLD = """            <img src="../../images/area_close.svg" alt="" class="annual-frame-img" aria-hidden="true">"""
AREA_CLOSE_IMG_NEW = """            <img src="../../images/area_close.svg" alt="" class="annual-frame-img" width="1017" height="362" decoding="async" aria-hidden="true">"""
AREA_CLOSE_IMG_EN_OLD = """            <img src="../../../images/area_close.svg" alt="" class="annual-frame-img" aria-hidden="true">"""
AREA_CLOSE_IMG_EN_NEW = """            <img src="../../../images/area_close.svg" alt="" class="annual-frame-img" width="1017" height="362" decoding="async" aria-hidden="true">"""

FOCUS_BAR_IMG_HTML_OLD = """              <img src="../../images/focus_bar.svg" alt="" class="annual-daily-focus-bar-img" id="annual-daily-focus-bar-img" width="757" height="91" decoding="async" aria-hidden="true">"""

FOCUS_BAR_IMG_HTML_NEW = """              <img src="../../images/focus_bar.svg" alt="" class="annual-daily-focus-bar-img" id="annual-daily-focus-bar-img" width="757" height="91" decoding="async" fetchpriority="high" aria-hidden="true">"""

FOCUS_BAR_IMG_HTML_EN_OLD = """              <img src="../../../images/focus_bar.svg" alt="" class="annual-daily-focus-bar-img" id="annual-daily-focus-bar-img" width="757" height="91" decoding="async" aria-hidden="true">"""

FOCUS_BAR_IMG_HTML_EN_NEW = """              <img src="../../../images/focus_bar.svg" alt="" class="annual-daily-focus-bar-img" id="annual-daily-focus-bar-img" width="757" height="91" decoding="async" fetchpriority="high" aria-hidden="true">"""

HYDRATE_VISIBILITY_OLD = """    html[data-monthly-tw-hydrated="0"] .monthly-scroll-data__track--group .monthly-data-column__cell,
    html[data-monthly-tw-hydrated="0"] .monthly-scroll-data__track--profit .monthly-data-column__cell {
      opacity: 1;
      color: rgba(88, 225, 243, 0.38);
    }"""

HYDRATE_VISIBILITY_NEW = """    html[data-monthly-tw-hydrated="0"] .monthly-scroll-data__track--group .monthly-data-column__cell,
    html[data-monthly-tw-hydrated="0"] .monthly-scroll-data__track--profit .monthly-data-column__cell {
      visibility: hidden;
    }"""
