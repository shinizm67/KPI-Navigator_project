"""Daily Floating Window — sticky date header + internal scroll body."""

from __future__ import annotations

STICKY_HEAD_MARKER = "/* KPI-DAILY-OVERLAY-STICKY-HEAD */"
STICKY_HEAD_END = "/* END KPI-DAILY-OVERLAY-STICKY-HEAD */"

HTML_PANEL_OPEN_OLD = """    <section class="daily-overlay__panel" role="dialog" aria-modal="true" aria-label="Daily">
      <button type="button" class="daily-overlay__close" id="daily-overlay-close\""""

HTML_PANEL_OPEN_NEW_JA = """    <section class="daily-overlay__panel" role="dialog" aria-modal="true" aria-label="Daily">
      <div class="daily-overlay__sticky-head" aria-label="日付操作">
      <button type="button" class="daily-overlay__close" id="daily-overlay-close\""""

HTML_PANEL_OPEN_NEW_EN = """    <section class="daily-overlay__panel" role="dialog" aria-modal="true" aria-label="Daily">
      <div class="daily-overlay__sticky-head" aria-label="Date navigation">
      <button type="button" class="daily-overlay__close" id="daily-overlay-close\""""

HTML_SCROLL_OPEN_OLD = """        <input type="date" class="daily-overlay__date-input" id="daily-overlay-date-input" aria-hidden="true" tabindex="-1">
      </div>
      <span class="daily-overlay__vline" aria-hidden="true"></span>"""

HTML_SCROLL_OPEN_NEW = """        <input type="date" class="daily-overlay__date-input" id="daily-overlay-date-input" aria-hidden="true" tabindex="-1">
      </div>
      </div>
      <div class="daily-overlay__scroll" tabindex="-1">
      <span class="daily-overlay__vline" aria-hidden="true"></span>"""

HTML_SCROLL_CLOSE_OLD = """        <p class="daily-overlay__daily-graph-rate">120%</p>
      </div>
    </section>
  </div>"""

HTML_SCROLL_CLOSE_NEW = """        <p class="daily-overlay__daily-graph-rate">120%</p>
      </div>
      </div>
    </section>
  </div>"""

PANEL_CSS_ANNUAL_OLD = """    .daily-overlay__panel {
      position: relative;
      width: 1100px;
      height: 1350px;
      overflow: hidden;
      border: 3px solid rgba(13, 177, 58, 0.85);"""

PANEL_CSS_ANNUAL_NEW = """    .daily-overlay__panel {
      position: relative;
      display: flex;
      flex-direction: column;
      width: 1100px;
      height: 1350px;
      max-height: calc(100vh - 32px);
      overflow: hidden;
      --daily-overlay-sticky-h: 74px;
      --daily-overlay-daily-kpi-top: 32px;
      border: 3px solid rgba(13, 177, 58, 0.85);"""

PANEL_CSS_MONTHLY_OLD = """    .daily-overlay__panel {
      position: relative;
      z-index: 1;
      flex: 0 0 auto;
      flex-shrink: 0;
      width: 1100px;
      max-width: calc(100vw - 32px);
      min-width: min(1100px, calc(100vw - 32px));
      height: 1350px;
      overflow: hidden;
      border: 3px solid rgba(13, 177, 58, 0.85);"""

PANEL_CSS_MONTHLY_NEW = """    .daily-overlay__panel {
      position: relative;
      z-index: 1;
      flex: 0 0 auto;
      flex-shrink: 0;
      display: flex;
      flex-direction: column;
      width: 1100px;
      max-width: calc(100vw - 32px);
      min-width: min(1100px, calc(100vw - 32px));
      height: 1350px;
      max-height: calc(100vh - 32px);
      overflow: hidden;
      --daily-overlay-sticky-h: 74px;
      --daily-overlay-daily-kpi-top: 32px;
      border: 3px solid rgba(13, 177, 58, 0.85);"""

STICKY_CSS_BLOCK = f"""    {STICKY_HEAD_MARKER}
    .daily-overlay__sticky-head {{
      position: relative;
      flex: 0 0 var(--daily-overlay-sticky-h);
      height: var(--daily-overlay-sticky-h);
      z-index: 12;
      background: rgba(9, 12, 17, 0.98);
      box-sizing: border-box;
    }}
    .daily-overlay__sticky-head .daily-overlay__head {{
      top: 8px;
      min-height: 28px;
      align-items: center;
    }}
    .daily-overlay__sticky-head::after {{
      content: '';
      position: absolute;
      left: 79px;
      right: 66px;
      bottom: 0;
      border-top: 0.5px solid rgba(88, 225, 243, 0.72);
      pointer-events: none;
    }}
    .daily-overlay__scroll {{
      position: relative;
      flex: 1 1 auto;
      min-height: 0;
      overflow-x: hidden;
      overflow-y: auto;
      -webkit-overflow-scrolling: touch;
    }}
    .daily-overlay__scroll::after {{
      content: '';
      display: block;
      height: calc(1350px - var(--daily-overlay-sticky-h));
      width: 1px;
      pointer-events: none;
    }}
    .daily-overlay__scroll .daily-overlay__vline {{
      top: 0;
      bottom: auto;
      height: calc(1350px - 34px - var(--daily-overlay-sticky-h));
    }}
    .daily-overlay__scroll .daily-overlay__hline--1 {{
      top: calc(383px - var(--daily-overlay-sticky-h));
    }}
    .daily-overlay__scroll .daily-overlay__hline--2 {{
      top: calc(792px - var(--daily-overlay-sticky-h));
    }}
    .daily-overlay__scroll .daily-overlay__segment--daily {{
      top: calc(104px - var(--daily-overlay-sticky-h));
      height: 279px;
    }}
    .daily-overlay__scroll .daily-overlay__segment--monthly {{
      top: calc(383px - var(--daily-overlay-sticky-h));
      height: 409px;
    }}
    .daily-overlay__scroll .daily-overlay__segment--annual {{
      top: calc(792px - var(--daily-overlay-sticky-h));
      bottom: auto;
      height: calc(1350px - 34px - 792px);
    }}
    .daily-overlay__scroll .daily-overlay__daily-kpi {{
      top: var(--daily-overlay-daily-kpi-top);
    }}
    .daily-overlay__scroll .daily-overlay__monthly-kpi {{
      top: calc(422px - var(--daily-overlay-sticky-h));
    }}
    .daily-overlay__scroll .daily-overlay__annual-kpi-wrap {{
      top: calc(848px - var(--daily-overlay-sticky-h));
    }}
    .daily-overlay__scroll .daily-overlay__daily-graph {{
      top: calc(314.5px - var(--daily-overlay-sticky-h));
    }}
    .daily-overlay__scroll .daily-overlay__monthly-graph {{
      top: calc(718.5px - var(--daily-overlay-sticky-h));
    }}
    .daily-overlay__scroll .daily-overlay__annual-graph {{
      top: calc(1248.5px - var(--daily-overlay-sticky-h));
    }}
    .office-mode .daily-overlay__sticky-head {{
      background: rgba(9, 12, 17, 0.98);
    }}
    {STICKY_HEAD_END}"""

OPEN_ANNUAL_OLD = """      function open() {
        lastFocused = document.activeElement;
        selectedIso = resolveIso();
        root.hidden = false;
        root.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
        fill(selectedIso);
        btnClose.focus();
      }"""

OPEN_ANNUAL_NEW = """      function resetDailyOverlayScroll() {
        var scrollEl = root.querySelector('.daily-overlay__scroll');
        if (scrollEl) scrollEl.scrollTop = 0;
      }
      function open() {
        lastFocused = document.activeElement;
        selectedIso = resolveIso();
        root.hidden = false;
        root.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
        fill(selectedIso);
        resetDailyOverlayScroll();
        btnClose.focus();
      }"""

OPEN_MONTHLY_OLD = """        fill(selectedIso);
        btnClose.focus();
      }
      function close() {
        root.hidden = true;
        root.setAttribute('aria-hidden', 'true');"""

OPEN_MONTHLY_NEW = """        fill(selectedIso);
        resetDailyOverlayScroll();
        btnClose.focus();
      }
      function close() {
        root.hidden = true;
        root.setAttribute('aria-hidden', 'true');"""

RESET_FN_MONTHLY = """      function resetDailyOverlayScroll() {
        var scrollEl = root.querySelector('.daily-overlay__scroll');
        if (scrollEl) scrollEl.scrollTop = 0;
      }
      function open() {
        lastFocused = document.activeElement;
        selectedIso = resolveIso();
        root.hidden = false;
        root.removeAttribute('hidden');
        root.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
        var panel = root.querySelector('.daily-overlay__panel');
        if (panel) {
          panel.style.flex = '0 0 auto';
          panel.style.width = '1100px';
          panel.style.maxWidth = 'calc(100vw - 32px)';
          void panel.offsetWidth;
        }"""

RESET_FN_MONTHLY_OLD = """      function open() {
        lastFocused = document.activeElement;
        selectedIso = resolveIso();
        root.hidden = false;
        root.removeAttribute('hidden');
        root.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
        var panel = root.querySelector('.daily-overlay__panel');
        if (panel) {
          panel.style.flex = '0 0 auto';
          panel.style.width = '1100px';
          panel.style.maxWidth = 'calc(100vw - 32px)';
          void panel.offsetWidth;
        }"""
