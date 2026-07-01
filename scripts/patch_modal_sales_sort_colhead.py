#!/usr/bin/env python3
"""Inject Sales column sort/filter UI into Past Sales and Sales Data modals (JA/EN)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = {
    ROOT / "app/annual/index.html": {
        "past_old": '          <div class="past-sales-modal__colhead-sales">売上</div>',
        "past_new": """          <div class="past-sales-modal__colhead-sales">
            <span>売上</span>
            <div class="past-sales-modal__sales-sort" id="past-sales-sales-sort-wrap">
              <button
                type="button"
                class="past-sales-modal__date-filter-toggle past-sales-modal__sales-sort-toggle"
                id="past-sales-sales-sort-toggle"
                aria-expanded="false"
                aria-haspopup="true"
                aria-controls="past-sales-sales-sort-panel"
                aria-label="売上で並べ替え"
              >
                <span class="past-sales-modal__sort-icon" aria-hidden="true">▼</span>
              </button>
              <div
                id="past-sales-sales-sort-panel"
                class="past-sales-modal__date-filter-panel past-sales-modal__sales-sort-panel"
                role="group"
                aria-label="売上の並べ替え"
                hidden
              >
                <div class="past-sales-modal__sales-sort-orders">
                  <button type="button" class="past-sales-modal__sales-sort-btn" data-psm-sales-order="desc">
                    降り順（売上 高→低）
                  </button>
                  <button type="button" class="past-sales-modal__sales-sort-btn" data-psm-sales-order="asc">
                    登り順（売上 低→高）
                  </button>
                </div>
                <div class="past-sales-modal__sales-sort-section-label">数値順位</div>
                <div class="past-sales-modal__sales-sort-amounts" id="past-sales-sales-sort-amounts"></div>
                <button type="button" class="past-sales-modal__filter-clear" id="past-sales-sales-sort-reset">
                  日付順に戻す
                </button>
              </div>
            </div>
          </div>""",
        "sdm_old": '          <div class="sales-data-modal__colhead-sales">売上</div>',
        "sdm_new": """          <div class="sales-data-modal__colhead-sales">
            <span>売上</span>
            <div class="sales-data-modal__sales-sort" id="sales-data-sales-sort-wrap">
              <button
                type="button"
                class="sales-data-modal__date-filter-toggle sales-data-modal__sales-sort-toggle"
                id="sales-data-sales-sort-toggle"
                aria-expanded="false"
                aria-haspopup="true"
                aria-controls="sales-data-sales-sort-panel"
                aria-label="売上で並べ替え"
              >
                <span class="sales-data-modal__sort-icon" aria-hidden="true">▼</span>
              </button>
              <div
                id="sales-data-sales-sort-panel"
                class="sales-data-modal__date-filter-panel sales-data-modal__sales-sort-panel"
                role="group"
                aria-label="売上の並べ替え"
                hidden
              >
                <div class="sales-data-modal__sales-sort-orders">
                  <button type="button" class="sales-data-modal__sales-sort-btn" data-sdm-sales-order="desc">
                    降り順（売上 高→低）
                  </button>
                  <button type="button" class="sales-data-modal__sales-sort-btn" data-sdm-sales-order="asc">
                    登り順（売上 低→高）
                  </button>
                </div>
                <div class="sales-data-modal__sales-sort-section-label">数値順位</div>
                <div class="sales-data-modal__sales-sort-amounts" id="sales-data-sales-sort-amounts"></div>
                <button type="button" class="sales-data-modal__filter-clear" id="sales-data-sales-sort-reset">
                  日付順に戻す
                </button>
              </div>
            </div>
          </div>""",
    },
    ROOT / "en/app/annual/index.html": {
        "past_old": '          <div class="past-sales-modal__colhead-sales">Sales</div>',
        "past_new": """          <div class="past-sales-modal__colhead-sales">
            <span>Sales</span>
            <div class="past-sales-modal__sales-sort" id="past-sales-sales-sort-wrap">
              <button
                type="button"
                class="past-sales-modal__date-filter-toggle past-sales-modal__sales-sort-toggle"
                id="past-sales-sales-sort-toggle"
                aria-expanded="false"
                aria-haspopup="true"
                aria-controls="past-sales-sales-sort-panel"
                aria-label="Sort by sales"
              >
                <span class="past-sales-modal__sort-icon" aria-hidden="true">▼</span>
              </button>
              <div
                id="past-sales-sales-sort-panel"
                class="past-sales-modal__date-filter-panel past-sales-modal__sales-sort-panel"
                role="group"
                aria-label="Sales sort options"
                hidden
              >
                <div class="past-sales-modal__sales-sort-orders">
                  <button type="button" class="past-sales-modal__sales-sort-btn" data-psm-sales-order="desc">
                    Descending (high → low)
                  </button>
                  <button type="button" class="past-sales-modal__sales-sort-btn" data-psm-sales-order="asc">
                    Ascending (low → high)
                  </button>
                </div>
                <div class="past-sales-modal__sales-sort-section-label">Numeric rank</div>
                <div class="past-sales-modal__sales-sort-amounts" id="past-sales-sales-sort-amounts"></div>
                <button type="button" class="past-sales-modal__filter-clear" id="past-sales-sales-sort-reset">
                  Back to date order
                </button>
              </div>
            </div>
          </div>""",
        "sdm_old": '          <div class="sales-data-modal__colhead-sales">Sales</div>',
        "sdm_new": """          <div class="sales-data-modal__colhead-sales">
            <span>Sales</span>
            <div class="sales-data-modal__sales-sort" id="sales-data-sales-sort-wrap">
              <button
                type="button"
                class="sales-data-modal__date-filter-toggle sales-data-modal__sales-sort-toggle"
                id="sales-data-sales-sort-toggle"
                aria-expanded="false"
                aria-haspopup="true"
                aria-controls="sales-data-sales-sort-panel"
                aria-label="Sort by sales"
              >
                <span class="sales-data-modal__sort-icon" aria-hidden="true">▼</span>
              </button>
              <div
                id="sales-data-sales-sort-panel"
                class="sales-data-modal__date-filter-panel sales-data-modal__sales-sort-panel"
                role="group"
                aria-label="Sales sort options"
                hidden
              >
                <div class="sales-data-modal__sales-sort-orders">
                  <button type="button" class="sales-data-modal__sales-sort-btn" data-sdm-sales-order="desc">
                    Descending (high → low)
                  </button>
                  <button type="button" class="sales-data-modal__sales-sort-btn" data-sdm-sales-order="asc">
                    Ascending (low → high)
                  </button>
                </div>
                <div class="sales-data-modal__sales-sort-section-label">Numeric rank</div>
                <div class="sales-data-modal__sales-sort-amounts" id="sales-data-sales-sort-amounts"></div>
                <button type="button" class="sales-data-modal__filter-clear" id="sales-data-sales-sort-reset">
                  Back to date order
                </button>
              </div>
            </div>
          </div>""",
    },
}


def patch_file(path: Path, spec: dict[str, str]) -> bool:
    text = path.read_text(encoding="utf-8")
    if "past-sales-sales-sort-wrap" in text:
        return False
    if spec["past_old"] not in text or spec["sdm_old"] not in text:
        raise SystemExit(f"anchor missing in {path}")
    text = text.replace(spec["past_old"], spec["past_new"], 1)
    text = text.replace(spec["sdm_old"], spec["sdm_new"], 1)
    path.write_text(text, encoding="utf-8")
    return True


def main() -> None:
    for path, spec in TARGETS.items():
        if patch_file(path, spec):
            print(f"patched {path.relative_to(ROOT)}")
        else:
            print(f"skip {path.relative_to(ROOT)} (already patched)")


if __name__ == "__main__":
    main()
