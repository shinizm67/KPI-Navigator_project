"""Sales Data Analyze — weekday target data-quality banner (Phase 11-7)."""

from __future__ import annotations

CSS = """
    /* SDM-WEEKDAY-QUALITY-CSS */
    .sdm-weekday-quality {
      margin-top: var(--sdm-analyze-table-chart-gap, 48px);
      margin-bottom: 16px;
      padding: 12px 14px;
      border: 2px solid rgba(255, 179, 71, 0.75);
      background: rgba(255, 179, 71, 0.1);
      box-sizing: border-box;
      width: 100%;
      display: flex;
      align-items: flex-start;
      gap: 10px;
    }
    .sdm-weekday-quality[hidden] {
      display: none !important;
    }
    .sdm-weekday-quality--info {
      border-color: rgba(88, 225, 243, 0.55);
      background: rgba(88, 225, 243, 0.08);
    }
    .sdm-weekday-quality--ok {
      border-color: rgba(15, 148, 3, 0.45);
      background: rgba(15, 148, 3, 0.08);
    }
    .sdm-weekday-quality__badge {
      flex: 0 0 auto;
      margin: 0;
      padding: 2px 8px;
      border-radius: 3px;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.04em;
      line-height: 1.4;
      color: #1a1200;
      background: #ffb347;
    }
    .sdm-weekday-quality--info .sdm-weekday-quality__badge {
      color: #0a2a30;
      background: rgba(88, 225, 243, 0.85);
    }
    .sdm-weekday-quality--ok .sdm-weekday-quality__badge {
      color: #0a3010;
      background: rgba(120, 220, 140, 0.9);
    }
    .sdm-weekday-quality__msg {
      margin: 0;
      font-size: 12px;
      line-height: 1.5;
      color: rgba(255, 220, 170, 0.95);
      flex: 1 1 auto;
    }
    .sdm-weekday-quality--info .sdm-weekday-quality__msg {
      color: rgba(168, 232, 245, 0.95);
    }
    .sdm-weekday-quality--ok .sdm-weekday-quality__msg {
      color: rgba(180, 240, 190, 0.95);
    }
    body.office-mode .sdm-weekday-quality {
      border-color: rgba(180, 83, 9, 0.45);
      background: rgba(180, 83, 9, 0.06);
    }
    body.office-mode .sdm-weekday-quality--info {
      border-color: rgba(10, 74, 138, 0.35);
      background: rgba(10, 74, 138, 0.04);
    }
    body.office-mode .sdm-weekday-quality--ok {
      border-color: rgba(15, 148, 3, 0.35);
      background: rgba(15, 148, 3, 0.05);
    }
    body.office-mode .sdm-weekday-quality__msg {
      color: #7c2d12;
    }
    body.office-mode .sdm-weekday-quality--info .sdm-weekday-quality__msg {
      color: #0a4a8a;
    }
    body.office-mode .sdm-weekday-quality--ok .sdm-weekday-quality__msg {
      color: #14532d;
    }
    /* /SDM-WEEKDAY-QUALITY-CSS */
"""

HTML_JA = """            <section
              class="sdm-weekday-quality sdm-weekday-quality--info"
              id="sdm-weekday-quality"
              aria-live="polite"
              hidden
              data-kpi-guard-ignore
            >
              <p class="sdm-weekday-quality__badge" id="sdm-weekday-quality-badge">お知らせ</p>
              <p class="sdm-weekday-quality__msg" id="sdm-weekday-quality-msg"></p>
            </section>"""

HTML_EN = """            <section
              class="sdm-weekday-quality sdm-weekday-quality--info"
              id="sdm-weekday-quality"
              aria-live="polite"
              hidden
              data-kpi-guard-ignore
            >
              <p class="sdm-weekday-quality__badge" id="sdm-weekday-quality-badge">Notice</p>
              <p class="sdm-weekday-quality__msg" id="sdm-weekday-quality-msg"></p>
            </section>"""
