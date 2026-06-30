#!/usr/bin/env python3
"""Add collapsible summary (▼/▶) to Annual sales-data + past-sales modals (JA/EN)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CSS_BLOCK = """
    .sales-data-modal__summary-wrap,
    .past-sales-modal__summary-wrap {
      width: 100%;
      margin: 0;
      flex-shrink: 0;
    }
    .sales-data-modal__summary-wrap.is-collapsed,
    .past-sales-modal__summary-wrap.is-collapsed {
      display: none;
    }
    .sales-data-modal__summary-toggle {
      flex: 0 0 32px;
      width: 32px;
      min-width: 32px;
      height: var(--sdm-tab-input-h);
      margin: 0;
      padding: 0;
      border: 1px solid var(--sdm-line);
      background: var(--sdm-bg-inactive);
      color: var(--sdm-cyan);
      font-size: 14px;
      font-weight: 600;
      line-height: 1;
      font-family: inherit;
      cursor: pointer;
      box-sizing: border-box;
    }
    .past-sales-modal__summary-toggle {
      flex: 0 0 32px;
      width: 32px;
      min-width: 32px;
      height: var(--psm-tab-input-h);
      margin: 0;
      padding: 0;
      border: 1px solid var(--psm-line);
      background: var(--psm-bg-inactive);
      color: var(--psm-cyan);
      font-size: 14px;
      font-weight: 600;
      line-height: 1;
      font-family: inherit;
      cursor: pointer;
      box-sizing: border-box;
    }
    .sales-data-modal__summary-toggle:hover,
    .sales-data-modal__summary-toggle:focus-visible {
      background: var(--sdm-bg-active-55);
      outline: 2px solid var(--sdm-cyan);
      outline-offset: 1px;
    }
    .past-sales-modal__summary-toggle:hover,
    .past-sales-modal__summary-toggle:focus-visible {
      background: var(--psm-bg-active-55);
      outline: 2px solid var(--psm-cyan);
      outline-offset: 1px;
    }
    .sales-data-modal__panel[data-sdm-tab='analyze'] .sales-data-modal__summary-toggle {
      display: none !important;
    }
    .past-sales-modal__panel[data-psm-tab='analyze'] .past-sales-modal__summary-toggle {
      display: none !important;
    }
"""

JS_BLOCK = """
  <script>
    (function () {
      var STORAGE_SALES = 'kpiNavigator.salesDataSummaryCollapsed';
      var STORAGE_PAST = 'kpiNavigator.pastSalesSummaryCollapsed';
      function isJa() {
        return document.documentElement.getAttribute('lang') === 'ja';
      }
      function label(collapsed) {
        if (collapsed) {
          return isJa() ? 'サマリーを表示' : 'Show summary';
        }
        return isJa() ? 'サマリーを折りたたむ' : 'Collapse summary';
      }
      function initWrap(wrap, btn, storageKey) {
        if (!wrap || !btn) return;
        var panel = wrap.querySelector('[data-sdm-summary-panel]');
        if (!panel) return;
        function setCollapsed(collapsed) {
          wrap.classList.toggle('is-collapsed', collapsed);
          btn.setAttribute('aria-expanded', collapsed ? 'false' : 'true');
          btn.textContent = collapsed ? '▶︎' : '▼';
          var text = label(collapsed);
          btn.setAttribute('aria-label', text);
          btn.setAttribute('title', text);
          try {
            sessionStorage.setItem(storageKey, collapsed ? '1' : '0');
          } catch (_e) {}
        }
        var initialCollapsed = false;
        try {
          initialCollapsed = sessionStorage.getItem(storageKey) === '1';
        } catch (_e) {}
        setCollapsed(initialCollapsed);
        btn.addEventListener('click', function () {
          setCollapsed(wrap.classList.contains('is-collapsed') ? false : true);
        });
      }
      initWrap(
        document.getElementById('sales-data-summary-wrap'),
        document.getElementById('sales-data-summary-toggle'),
        STORAGE_SALES
      );
      initWrap(
        document.getElementById('past-sales-summary-wrap'),
        document.getElementById('past-sales-summary-toggle'),
        STORAGE_PAST
      );
    })();
  </script>
"""

SALES_WRAP = {
    "en": """      <div
        class="sales-data-modal__summary-wrap sales-data-modal__input-only"
        id="sales-data-summary-wrap"
        data-sdm-summary-collapsible
      >
        <div
          class="sales-data-modal__summary"
          id="sales-data-summary-panel"
          data-sdm-summary-panel
          aria-label="Sales summary"
        >""",
    "ja": """      <div
        class="sales-data-modal__summary-wrap sales-data-modal__input-only"
        id="sales-data-summary-wrap"
        data-sdm-summary-collapsible
      >
        <div
          class="sales-data-modal__summary"
          id="sales-data-summary-panel"
          data-sdm-summary-panel
          aria-label="売上サマリー"
        >""",
}

PAST_WRAP = {
    "en": """      <div
        class="past-sales-modal__summary-wrap past-sales-modal__input-only"
        id="past-sales-summary-wrap"
        data-sdm-summary-collapsible
      >
        <div
          class="past-sales-modal__summary"
          id="past-sales-summary-panel"
          data-sdm-summary-panel
          aria-label="Past sales summary"
        >""",
    "ja": """      <div
        class="past-sales-modal__summary-wrap past-sales-modal__input-only"
        id="past-sales-summary-wrap"
        data-sdm-summary-collapsible
      >
        <div
          class="past-sales-modal__summary"
          id="past-sales-summary-panel"
          data-sdm-summary-panel
          aria-label="過去売上サマリー"
        >""",
}

SALES_OPEN = {
    "en": '      <div class="sales-data-modal__summary sales-data-modal__input-only" aria-label="Sales summary">',
    "ja": '      <div class="sales-data-modal__summary sales-data-modal__input-only" aria-label="売上サマリー">',
}

PAST_OPEN = {
    "en": '      <div class="past-sales-modal__summary past-sales-modal__input-only" aria-label="Past sales summary">',
    "ja": '      <div class="past-sales-modal__summary past-sales-modal__input-only" aria-label="過去売上サマリー">',
}

SALES_CLOSE = """        </div>
      </div>"""

PAST_CLOSE = """        </div>
      </div>"""


def patch_file(path: Path, lang: str) -> None:
    text = path.read_text(encoding="utf-8")
    if "sales-data-modal__summary-wrap" in text:
        print(f"skip (already patched): {path}")
        return

    if ".sales-data-modal__summary-wrap," not in text:
        anchor = "    .sales-data-modal__summary {"
        if anchor not in text:
            raise SystemExit(f"CSS anchor missing in {path}")
        text = text.replace(anchor, CSS_BLOCK + anchor, 1)

    text = text.replace(SALES_OPEN[lang], SALES_WRAP[lang], 1)
    text = text.replace(PAST_OPEN[lang], PAST_WRAP[lang], 1)

    # Close summary panel + wrap before year/month row (sales) — unique 3-row ending
    sales_end = "          <p class=\"sales-data-modal__summary-pct\" id=\"sales-data-summary-progress-pct\">—</p>\n        </div>\n      </div>\n      <div class=\"sales-data-modal__ym\">"
    sales_end_new = (
        "          <p class=\"sales-data-modal__summary-pct\" id=\"sales-data-summary-progress-pct\">—</p>\n"
        "        </div>\n"
        + SALES_CLOSE
        + "\n      <div class=\"sales-data-modal__ym\">"
    )
    if sales_end not in text:
        raise SystemExit(f"sales summary end anchor missing in {path}")
    text = text.replace(sales_end, sales_end_new, 1)

    past_end = "          <p class=\"past-sales-modal__summary-pct\" id=\"past-sales-summary-progress-pct\">—</p>\n        </div>\n      </div>\n      <div class=\"past-sales-modal__ym\">"
    past_end_new = (
        "          <p class=\"past-sales-modal__summary-pct\" id=\"past-sales-summary-progress-pct\">—</p>\n"
        "        </div>\n"
        + PAST_CLOSE
        + "\n      <div class=\"past-sales-modal__ym\">"
    )
    if past_end not in text:
        raise SystemExit(f"past summary end anchor missing in {path}")
    text = text.replace(past_end, past_end_new, 1)

    if "kpiNavigator.salesDataSummaryCollapsed" not in text:
        text = text.replace("</body>", JS_BLOCK + "\n</body>", 1)

    path.write_text(text, encoding="utf-8")
    print(f"patched {path}")


def main() -> None:
    patch_file(ROOT / "en/app/annual/index.html", "en")
    patch_file(ROOT / "app/annual/index.html", "ja")


if __name__ == "__main__":
    main()
