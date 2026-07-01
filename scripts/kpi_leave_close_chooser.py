"""KPI leave / close chooser — shared HTML/CSS/JS for MEP, PL, Past Sales, and Sales Data."""

from __future__ import annotations

# Same tokens as app/annual/index.html (--sdm-* on sales-data-modal)
CLOSE_CHOOSER_CSS = """
    :root {
      --sdm-panel-bg: #000000;
      --sdm-cyan: #58e1f3;
      --sdm-fs-body: 14px;
      --sdm-bg-active-editable: rgba(88, 225, 243, 0.5);
      --sdm-bg-active-focus: rgba(88, 225, 243, 0.567);
      --sdm-bg-active-55: var(--sdm-bg-active-editable);
      --sdm-bg-active-70: var(--sdm-bg-active-focus);
    }
    .sales-data-modal__close-chooser {
      position: fixed;
      inset: 0;
      z-index: 20150;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 24px;
      box-sizing: border-box;
    }
    .sales-data-modal__close-chooser[hidden] {
      display: none !important;
    }
    .sales-data-modal__close-chooser-scrim {
      position: absolute;
      inset: 0;
      background: rgba(0, 0, 0, 0.55);
    }
    .sales-data-modal__close-chooser-panel {
      position: relative;
      z-index: 1;
      width: min(420px, 100%);
      padding: 24px 22px 20px;
      border: 2px solid var(--sdm-cyan);
      border-radius: 8px;
      background: var(--sdm-panel-bg);
      color: var(--sdm-cyan);
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.45);
      box-sizing: border-box;
    }
    .sales-data-modal__close-chooser-title {
      margin: 0 0 10px;
      font-size: 18px;
      font-weight: 700;
      line-height: 1.35;
    }
    .sales-data-modal__close-chooser-msg {
      margin: 0 0 20px;
      font-size: var(--sdm-fs-body);
      line-height: 1.5;
      opacity: 0.92;
    }
    .sales-data-modal__close-chooser-actions {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .sales-data-modal__close-chooser-btn {
      width: 100%;
      min-height: 40px;
      padding: 8px 14px;
      border: 1px solid var(--sdm-cyan);
      border-radius: 6px;
      background: transparent;
      color: var(--sdm-cyan);
      font: inherit;
      font-size: 15px;
      cursor: pointer;
      box-sizing: border-box;
    }
    .sales-data-modal__close-chooser-btn--save {
      background: var(--sdm-bg-active-55);
      font-weight: 700;
    }
    .sales-data-modal__close-chooser-btn:hover,
    .sales-data-modal__close-chooser-btn:focus-visible {
      background: var(--sdm-bg-active-70);
      outline: 2px solid var(--sdm-cyan);
      outline-offset: 2px;
    }
"""

CLOSE_CHOOSER_HTML = {
    "ja": """
  <div
    class="sales-data-modal__close-chooser"
    id="sales-data-close-chooser"
    role="dialog"
    aria-modal="true"
    aria-labelledby="sales-data-close-chooser-title"
    hidden
  >
    <div class="sales-data-modal__close-chooser-scrim" id="sales-data-close-chooser-scrim" aria-hidden="true"></div>
    <div class="sales-data-modal__close-chooser-panel">
      <p id="sales-data-close-chooser-title" class="sales-data-modal__close-chooser-title">売上データを閉じます</p>
      <p class="sales-data-modal__close-chooser-msg">保存するか、保存せずに閉じるかを選んでください。</p>
      <div class="sales-data-modal__close-chooser-actions">
        <button type="button" class="sales-data-modal__close-chooser-btn sales-data-modal__close-chooser-btn--save" id="sales-data-close-save">
          保存して閉じる
        </button>
        <button type="button" class="sales-data-modal__close-chooser-btn" id="sales-data-close-discard">
          保存せずに閉じる
        </button>
        <button type="button" class="sales-data-modal__close-chooser-btn" id="sales-data-close-cancel">
          キャンセル
        </button>
      </div>
    </div>
  </div>
""",
    "en": """
  <div
    class="sales-data-modal__close-chooser"
    id="sales-data-close-chooser"
    role="dialog"
    aria-modal="true"
    aria-labelledby="sales-data-close-chooser-title"
    hidden
  >
    <div class="sales-data-modal__close-chooser-scrim" id="sales-data-close-chooser-scrim" aria-hidden="true"></div>
    <div class="sales-data-modal__close-chooser-panel">
      <p id="sales-data-close-chooser-title" class="sales-data-modal__close-chooser-title">Close Sales Data</p>
      <p class="sales-data-modal__close-chooser-msg">Choose whether to save your changes before closing.</p>
      <div class="sales-data-modal__close-chooser-actions">
        <button type="button" class="sales-data-modal__close-chooser-btn sales-data-modal__close-chooser-btn--save" id="sales-data-close-save">
          Save and close
        </button>
        <button type="button" class="sales-data-modal__close-chooser-btn" id="sales-data-close-discard">
          Close without saving
        </button>
        <button type="button" class="sales-data-modal__close-chooser-btn" id="sales-data-close-cancel">
          Cancel
        </button>
      </div>
    </div>
  </div>
""",
}

PAST_SALES_CLOSE_CHOOSER_HTML = {
    "ja": """
  <div
    class="sales-data-modal__close-chooser"
    id="past-sales-close-chooser"
    role="dialog"
    aria-modal="true"
    aria-labelledby="past-sales-close-chooser-title"
    hidden
  >
    <div class="sales-data-modal__close-chooser-scrim" id="past-sales-close-chooser-scrim" aria-hidden="true"></div>
    <div class="sales-data-modal__close-chooser-panel">
      <p id="past-sales-close-chooser-title" class="sales-data-modal__close-chooser-title">過去売上データを閉じます</p>
      <p class="sales-data-modal__close-chooser-msg">保存するか、保存せずに閉じるかを選んでください。</p>
      <div class="sales-data-modal__close-chooser-actions">
        <button type="button" class="sales-data-modal__close-chooser-btn sales-data-modal__close-chooser-btn--save" id="past-sales-close-save">
          保存して閉じる
        </button>
        <button type="button" class="sales-data-modal__close-chooser-btn" id="past-sales-close-discard">
          保存せずに閉じる
        </button>
        <button type="button" class="sales-data-modal__close-chooser-btn" id="past-sales-close-cancel">
          キャンセル
        </button>
      </div>
    </div>
  </div>
""",
    "en": """
  <div
    class="sales-data-modal__close-chooser"
    id="past-sales-close-chooser"
    role="dialog"
    aria-modal="true"
    aria-labelledby="past-sales-close-chooser-title"
    hidden
  >
    <div class="sales-data-modal__close-chooser-scrim" id="past-sales-close-chooser-scrim" aria-hidden="true"></div>
    <div class="sales-data-modal__close-chooser-panel">
      <p id="past-sales-close-chooser-title" class="sales-data-modal__close-chooser-title">Close Past Sales Data</p>
      <p class="sales-data-modal__close-chooser-msg">Choose whether to save your changes before closing.</p>
      <div class="sales-data-modal__close-chooser-actions">
        <button type="button" class="sales-data-modal__close-chooser-btn sales-data-modal__close-chooser-btn--save" id="past-sales-close-save">
          Save and close
        </button>
        <button type="button" class="sales-data-modal__close-chooser-btn" id="past-sales-close-discard">
          Close without saving
        </button>
        <button type="button" class="sales-data-modal__close-chooser-btn" id="past-sales-close-cancel">
          Cancel
        </button>
      </div>
    </div>
  </div>
""",
}


def close_chooser_js(
    save_on_leave: str,
    *,
    can_leave_without_chooser: str = "editSessionCommitted && !hasUnsavedChanges()",
) -> str:
    """Inject after hasUnsavedChanges() exists. save_on_leave: JS statements before resolving true."""
    return f"""
      var closeChooser = document.getElementById('sales-data-close-chooser');
      var closeChooserScrim = document.getElementById('sales-data-close-chooser-scrim');
      var closeChooserSave = document.getElementById('sales-data-close-save');
      var closeChooserDiscard = document.getElementById('sales-data-close-discard');
      var closeChooserCancel = document.getElementById('sales-data-close-cancel');
      var closeChooserReturnFocus = null;
      var leaveNavigateResolve = null;

      function isCloseChooserOpen() {{
        return closeChooser && !closeChooser.hasAttribute('hidden');
      }}
      function showCloseChooser() {{
        if (!closeChooser) return;
        closeChooserReturnFocus = document.activeElement;
        closeChooser.removeAttribute('hidden');
        if (closeChooserCancel) closeChooserCancel.focus();
      }}
      function hideCloseChooser() {{
        if (!closeChooser || closeChooser.hasAttribute('hidden')) return;
        closeChooser.setAttribute('hidden', '');
        var el = closeChooserReturnFocus;
        closeChooserReturnFocus = null;
        if (el && typeof el.focus === 'function') el.focus();
      }}
      function finishLeaveNavigate(ok) {{
        var fn = leaveNavigateResolve;
        leaveNavigateResolve = null;
        hideCloseChooser();
        if (fn) fn(!!ok);
      }}
      if (closeChooserSave) {{
        closeChooserSave.addEventListener('click', function () {{
          {save_on_leave}
          finishLeaveNavigate(true);
        }});
      }}
      if (closeChooserDiscard) {{
        closeChooserDiscard.addEventListener('click', function () {{
          finishLeaveNavigate(true);
        }});
      }}
      if (closeChooserCancel) {{
        closeChooserCancel.addEventListener('click', function () {{
          finishLeaveNavigate(false);
        }});
      }}
      if (closeChooserScrim) {{
        closeChooserScrim.addEventListener('click', function () {{
          finishLeaveNavigate(false);
        }});
      }}
      function canLeaveWithoutChooser() {{
        return {can_leave_without_chooser};
      }}
      function requestLeaveNavigation() {{
        return new Promise(function (resolve) {{
          if (canLeaveWithoutChooser()) {{
            resolve(true);
            return;
          }}
          if (isCloseChooserOpen()) {{
            resolve(false);
            return;
          }}
          leaveNavigateResolve = resolve;
          showCloseChooser();
        }});
      }}
      window.requestLeaveNavigation = requestLeaveNavigation;
"""


def past_sales_close_chooser_js(*, save_on_leave: str = "savePastSalesModal();") -> str:
    """Inject inside Past Sales modal IIFE after savePastSalesModal() exists."""
    return f"""
      var pastSalesCloseChooser = document.getElementById('past-sales-close-chooser');
      var pastSalesCloseChooserScrim = document.getElementById('past-sales-close-chooser-scrim');
      var pastSalesCloseChooserSave = document.getElementById('past-sales-close-save');
      var pastSalesCloseChooserDiscard = document.getElementById('past-sales-close-discard');
      var pastSalesCloseChooserCancel = document.getElementById('past-sales-close-cancel');
      var pastSalesCloseChooserReturnFocus = null;
      var pastSalesLeaveResolve = null;

      function hasPastSalesUnsavedChanges() {{
        return !!state.modalDirty || Object.keys(state.rowStateByIso || {{}}).length > 0;
      }}
      function isPastSalesCloseChooserOpen() {{
        return pastSalesCloseChooser && !pastSalesCloseChooser.hasAttribute('hidden');
      }}
      function showPastSalesCloseChooser() {{
        if (!pastSalesCloseChooser) return;
        pastSalesCloseChooserReturnFocus = document.activeElement;
        pastSalesCloseChooser.removeAttribute('hidden');
        if (pastSalesCloseChooserCancel) pastSalesCloseChooserCancel.focus();
      }}
      function hidePastSalesCloseChooser() {{
        if (!pastSalesCloseChooser || pastSalesCloseChooser.hasAttribute('hidden')) return;
        pastSalesCloseChooser.setAttribute('hidden', '');
        var el = pastSalesCloseChooserReturnFocus;
        pastSalesCloseChooserReturnFocus = null;
        if (el && typeof el.focus === 'function') el.focus();
      }}
      function finishPastSalesLeaveNavigate(ok) {{
        var fn = pastSalesLeaveResolve;
        pastSalesLeaveResolve = null;
        hidePastSalesCloseChooser();
        if (fn) fn(!!ok);
      }}
      if (pastSalesCloseChooserSave) {{
        pastSalesCloseChooserSave.addEventListener('click', function () {{
          {save_on_leave}
          finishPastSalesLeaveNavigate(true);
        }});
      }}
      if (pastSalesCloseChooserDiscard) {{
        pastSalesCloseChooserDiscard.addEventListener('click', function () {{
          finishPastSalesLeaveNavigate(true);
        }});
      }}
      if (pastSalesCloseChooserCancel) {{
        pastSalesCloseChooserCancel.addEventListener('click', function () {{
          finishPastSalesLeaveNavigate(false);
        }});
      }}
      if (pastSalesCloseChooserScrim) {{
        pastSalesCloseChooserScrim.addEventListener('click', function () {{
          finishPastSalesLeaveNavigate(false);
        }});
      }}
      function requestPastSalesLeaveNavigation() {{
        return new Promise(function (resolve) {{
          if (!hasPastSalesUnsavedChanges()) {{
            resolve(true);
            return;
          }}
          if (isPastSalesCloseChooserOpen()) {{
            resolve(false);
            return;
          }}
          pastSalesLeaveResolve = resolve;
          showPastSalesCloseChooser();
        }});
      }}
      function requestCloseModal() {{
        requestPastSalesLeaveNavigation().then(function (ok) {{
          if (ok) closeModal();
        }});
      }}
"""
