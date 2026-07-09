"""Annual CLS + placeTargetSalesGroup layout perf — reserve space, coalesce layout reads."""

from __future__ import annotations

ANNUAL_CLS_MARKER = "/* KPI-ANNUAL-CLS-FIX */"
ANNUAL_PLACE_MARKER = "/* KPI-ANNUAL-PLACE-PERF */"

HEAD_PRELOAD_OLD = """  <link rel="stylesheet" href="../../register/style.css">"""
HEAD_PRELOAD_NEW = """  <link rel="preload" as="image" href="../../images/area_close.svg" fetchpriority="high">
  <link rel="stylesheet" href="../../register/style.css">"""

HEAD_PRELOAD_EN_OLD = """  <link rel="stylesheet" href="../../../register/style.css">"""
HEAD_PRELOAD_EN_NEW = """  <link rel="preload" as="image" href="../../../images/area_close.svg" fetchpriority="high">
  <link rel="stylesheet" href="../../../register/style.css">"""

BODY_BOOT_OLD = '<body class="si-fi profile-page" id="body-el">'
BODY_BOOT_SCRIPT = """  <script>/* KPI-ANNUAL-CLS-BOOT */(function(){try{if(localStorage.getItem('kpi-annual-focus-bar-expanded')!=='1')return;document.body.classList.add('annual-focus-bar-expanded');var prep=function(){var img=document.getElementById('annual-daily-focus-bar-img');if(!img)return;var office=document.body.classList.contains('office-mode');var src=img.getAttribute('src')||'';var dir=src.indexOf('/')>=0?src.slice(0,src.lastIndexOf('/')+1):'../../images/';img.setAttribute('src',dir+(office?'focus_bar_office_mode_open.svg':'focus_bar_open.svg'));img.setAttribute('width','1132');};if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',prep,{once:true});else prep();}catch(e){}})();</script>"""
BODY_BOOT_SCRIPT_EN = BODY_BOOT_SCRIPT.replace(
    ":'../../images/';", ":'../../../images/';"
)
BODY_BOOT_NEW = BODY_BOOT_OLD + "\n" + BODY_BOOT_SCRIPT
BODY_BOOT_NEW_EN = BODY_BOOT_OLD + "\n" + BODY_BOOT_SCRIPT_EN

FRAME_IMG_CSS_OLD = """    .annual-frame-img {
      width: 100%;
      display: block;
      height: auto;
    }
    .annual-area-top-svg {
      position: relative;
      display: block;
      width: 100%;
    }"""

FRAME_IMG_CSS_NEW = f"""    {ANNUAL_CLS_MARKER}
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
    }}
    .annual-total-bd-value,
    .annual-target-sales-value,
    .annual-target-sales-amount,
    .annual-kpi-value,
    .annual-daily-row__cell,
    .annual-daily-focus-bar-lower__cell,
    .annual-daily-focus-bar-upper__cell,
    .annual-open-table td {{
      font-variant-numeric: tabular-nums;
    }}
    .annual-daily-focus-bar-img {{
      aspect-ratio: 757 / 91;
      height: auto;
    }}
    body.annual-focus-bar-expanded .annual-daily-focus-bar-img {{
      aspect-ratio: 1132 / 91;
    }}"""

AREA_CLOSE_IMG_OLD = """            <img src="../../images/area_close.svg" alt="" class="annual-frame-img" aria-hidden="true">"""
AREA_CLOSE_IMG_NEW = """            <img src="../../images/area_close.svg" alt="" class="annual-frame-img" width="1017" height="362" decoding="async" fetchpriority="high" aria-hidden="true">"""
AREA_CLOSE_IMG_EN_OLD = """            <img src="../../../images/area_close.svg" alt="" class="annual-frame-img" aria-hidden="true">"""
AREA_CLOSE_IMG_EN_NEW = """            <img src="../../../images/area_close.svg" alt="" class="annual-frame-img" width="1017" height="362" decoding="async" fetchpriority="high" aria-hidden="true">"""

FOCUS_BAR_IMG_OLD = """              <img src="../../images/focus_bar.svg" alt="" class="annual-daily-focus-bar-img" id="annual-daily-focus-bar-img" width="757" height="91" decoding="async" aria-hidden="true">"""
FOCUS_BAR_IMG_EN_OLD = """              <img src="../../../images/focus_bar.svg" alt="" class="annual-daily-focus-bar-img" id="annual-daily-focus-bar-img" width="757" height="91" decoding="async" aria-hidden="true">"""

PLACE_FN_OLD = """      function placeTargetSalesGroup() {
        if (!targetGroup) return;
        var root = document.getElementById('annual-monthly-data');
        if (!root) return;
        var rootRect = root.getBoundingClientRect();
        var todayRect = todayBtn.getBoundingClientRect();
        var left = Math.round(todayRect.right - rootRect.left + 45);
        targetGroup.style.left = left + 'px';
        targetGroup.classList.add('annual-target-sales-group--positioned');
      }"""

PLACE_FN_NEW = f"""      {ANNUAL_PLACE_MARKER}
      var __placeTargetSalesLeft = null;
      function placeTargetSalesGroup() {{
        if (!targetGroup) return;
        var root = document.getElementById('annual-monthly-data');
        if (!root) return;
        var rootRect = root.getBoundingClientRect();
        var todayRect = todayBtn.getBoundingClientRect();
        var left = Math.round(todayRect.right - rootRect.left + 45);
        if (__placeTargetSalesLeft === left) {{
          if (!targetGroup.classList.contains('annual-target-sales-group--positioned')) {{
            targetGroup.classList.add('annual-target-sales-group--positioned');
          }}
          return;
        }}
        __placeTargetSalesLeft = left;
        targetGroup.style.left = left + 'px';
        targetGroup.classList.add('annual-target-sales-group--positioned');
      }}"""

PLACE_LISTENERS_OLD = """      /* KPI-ANNUAL-LOAD-PERF */
      var __placeTargetSalesTimer = null;
      function schedulePlaceTargetSalesGroup() {
        if (__placeTargetSalesTimer != null) window.clearTimeout(__placeTargetSalesTimer);
        __placeTargetSalesTimer = window.setTimeout(function () {
          __placeTargetSalesTimer = null;
          window.requestAnimationFrame(placeTargetSalesGroup);
        }, 0);
      }
      schedulePlaceTargetSalesGroup();
      window.addEventListener('resize', schedulePlaceTargetSalesGroup);
      document.addEventListener('annual:timelineRowsRendered', schedulePlaceTargetSalesGroup);
      document.addEventListener('kpi:readSurfacesRefresh', schedulePlaceTargetSalesGroup);
      document.addEventListener('annual:calendarYearChanged', schedulePlaceTargetSalesGroup);
      setTimeout(schedulePlaceTargetSalesGroup, 150);"""

PLACE_LISTENERS_NEW = """      /* KPI-ANNUAL-LOAD-PERF */
      var __placeTargetSalesRaf = null;
      function schedulePlaceTargetSalesGroup() {
        if (__placeTargetSalesRaf != null) return;
        __placeTargetSalesRaf = window.requestAnimationFrame(function () {
          __placeTargetSalesRaf = null;
          placeTargetSalesGroup();
        });
      }
      schedulePlaceTargetSalesGroup();
      window.addEventListener('resize', schedulePlaceTargetSalesGroup);
      document.addEventListener('annual:timelineRowsRendered', schedulePlaceTargetSalesGroup);
      document.addEventListener('kpi:readSurfacesRefresh', schedulePlaceTargetSalesGroup);
      document.addEventListener('annual:calendarYearChanged', schedulePlaceTargetSalesGroup);
      if (typeof ResizeObserver !== 'undefined') {
        var __placeTargetSalesRo = new ResizeObserver(schedulePlaceTargetSalesGroup);
        var __placeRoot = document.getElementById('annual-monthly-data');
        if (__placeRoot) __placeTargetSalesRo.observe(__placeRoot);
        if (todayBtn) __placeTargetSalesRo.observe(todayBtn);
      }
      window.addEventListener('load', schedulePlaceTargetSalesGroup);"""

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
        if (twToggleBtn) {
          twToggleBtn.setAttribute('aria-checked', initialExpanded ? 'true' : 'false');
        }
      } else {
        setFocusBarExpanded(initialExpanded);
      }"""

FOCUS_BAR_INIT_EN_NEW = FOCUS_BAR_INIT_NEW.replace(
    "日次テーブルを縮小' : '日次テーブルを展開'",
    "Collapse daily table' : 'Expand daily table'",
)
