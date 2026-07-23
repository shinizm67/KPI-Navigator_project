#!/usr/bin/env python3
"""Insight Summary Annual: 幽霊空白の根絶（Analyze 帯 max 汚染 + ATR 尾の過大予約）.

- Annual ページに Monthly と同型の Summary タブ override を移植（必須）
- Summary 帯高だけ ATR 尾を実レイアウト（relative foot）に合わせる（Analyze 共有変数は触らない）
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
]

# Summary 専用: Analyze の --insight-atr-tail-inner-h（絶対配置 150px 前提）を使わない
SUMMARY_TAIL_VARS = """      --insight-atr-summary-foot-margin-h: calc(
        var(--insight-kpi-graph-gap-box-to-visual) + 50px + 25px + 50px + (13px * 1.2) + 12px
      );
      --insight-atr-summary-tail-h: calc(
        var(--insight-kpi-graph-gap-box-to-visual) + 96px +
          var(--insight-atr-summary-foot-margin-h) + 40px
      );
"""

SUMMARY_OVERRIDE_BLOCK = """    /* Summary タブ: 親 .insight-overlay__content / .insight-pane の Analyze 用 min-height を無効化 */
    .insight-overlay__content:has(> #insight-pane-summary:not([hidden])) {
      min-height: auto;
      height: auto;
    }
    #insight-pane-summary.insight-pane {
      min-height: auto;
      height: auto;
    }
    /* Summary タブのみ: 帯高は Summary 実寸（Analyze の max 採用で下に空きが出ない） */
    #insight-pane-summary .insight-overlay__section--daily {
      min-height: var(--insight-band-daily-summary);
    }
    #insight-pane-summary .insight-overlay__hline--monthly {
      top: var(--insight-band-daily-summary);
    }
    #insight-pane-summary .insight-overlay__hline--annual {
      top: calc(var(--insight-band-daily-summary) + var(--insight-band-monthly-summary));
    }
    #insight-pane-summary .insight-overlay__section--monthly {
      min-height: var(--insight-band-monthly-summary);
    }
    /* Summary Annual: Summary 帯高（下端余白は --insight-band-annual-summary に含む） */
    #insight-pane-summary #insight-jump-summary-annual {
      min-height: var(--insight-band-annual-summary);
      height: auto;
      padding-bottom: 0;
      box-sizing: border-box;
    }
    #insight-pane-summary .insight-annual-target-revision-tail {
      min-height: 0;
    }
    #insight-pane-summary .insight-annual-target-revision-tail .insight-annual-target-revision-foot {
      position: relative;
      top: auto;
      right: auto;
      margin-top: calc(
        var(--insight-kpi-graph-gap-box-to-visual) + 50px + 25px + 50px + (13px * 1.2) + 12px
      );
      display: flex;
      justify-content: flex-end;
      width: 100%;
      box-sizing: border-box;
    }
"""


def ensure_summary_tail_vars(text: str) -> str:
    if "--insight-atr-summary-tail-h" in text:
        return text
    # Insert before --insight-annual-summary-target-revision-zone-h if present
    anchor = "      --insight-annual-summary-target-revision-zone-h:"
    if anchor in text:
        return text.replace(anchor, SUMMARY_TAIL_VARS + anchor, 1)
    # Annual older formula: inject before --insight-band-annual-summary
    anchor2 = "      --insight-band-annual-summary:"
    if anchor2 not in text:
        raise SystemExit("band-annual-summary anchor miss")
    return text.replace(anchor2, SUMMARY_TAIL_VARS + anchor2, 1)


def fix_summary_band_formula(text: str) -> str:
    """Point Summary annual band at summary-tail (not Analyze absolute atr-tail)."""
    # Monthly-style zone
    old_zone = (
        "      --insight-annual-summary-target-revision-zone-h: calc(\n"
        "        48px + var(--insight-annual-revision-rows-h) + var(--insight-atr-tail-inner-h)\n"
        "      );"
    )
    new_zone = (
        "      --insight-annual-summary-target-revision-zone-h: calc(\n"
        "        48px + var(--insight-annual-revision-rows-h) + var(--insight-atr-summary-tail-h)\n"
        "      );"
    )
    if old_zone in text:
        text = text.replace(old_zone, new_zone, 1)
    elif (
        "--insight-annual-summary-target-revision-zone-h: calc(\n"
        "        48px + var(--insight-annual-revision-rows-h) + var(--insight-atr-summary-tail-h)"
    ) in text:
        pass
    elif "--insight-annual-summary-target-revision-zone-h:" in text:
        pass

    # Annual older band formula (no zone var)
    old_band_annual = (
        "      --insight-band-annual-summary: calc(\n"
        "        var(--insight-through-comparison-tail-end) + var(--insight-atr-zone-through-graph-h) +\n"
        "          var(--insight-atr-back-to-top-h) + var(--insight-section-bottom-pad)\n"
        "      );"
    )
    new_band_annual = (
        "      --insight-band-annual-summary: calc(\n"
        "        var(--insight-through-comparison-tail-end) + 48px + var(--insight-annual-revision-rows-h) +\n"
        "          var(--insight-atr-summary-tail-h) + var(--insight-section-bottom-pad)\n"
        "      );"
    )
    if old_band_annual in text:
        text = text.replace(old_band_annual, new_band_annual, 1)

    # Monthly band that still references atr-tail via zone — zone already fixed above
    return text


def ensure_summary_overrides(text: str) -> str:
    if "#insight-pane-summary #insight-jump-summary-annual" in text:
        return text
    # Insert after Graph pane auto block if present, else after section--annual
    graph_anchor = """    #insight-pane-graph.insight-pane {
      min-height: auto;
      height: auto;
    }
"""
    if graph_anchor in text:
        return text.replace(graph_anchor, graph_anchor + SUMMARY_OVERRIDE_BLOCK, 1)

    section_anchor = """    .insight-overlay__section--annual {
      min-height: var(--insight-band-annual);
    }
"""
    if section_anchor not in text:
        raise SystemExit("section--annual anchor miss for Summary overrides")
    return text.replace(section_anchor, section_anchor + SUMMARY_OVERRIDE_BLOCK, 1)


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = ensure_summary_tail_vars(text)
    text = fix_summary_band_formula(text)
    text = ensure_summary_overrides(text)
    checks = [
        "#insight-pane-summary #insight-jump-summary-annual",
        "--insight-atr-summary-tail-h",
        "insight-pane-summary:not([hidden])",
    ]
    for needle in checks:
        if needle not in text:
            raise SystemExit(f"missing {needle}: {path}")
    # must not leave Summary zone on Analyze atr-tail
    if re.search(
        r"--insight-annual-summary-target-revision-zone-h:\s*calc\(\s*"
        r"48px \+ var\(--insight-annual-revision-rows-h\) \+ var\(--insight-atr-tail-inner-h\)",
        text,
    ):
        raise SystemExit(f"Summary zone still uses atr-tail-inner-h: {path}")
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> int:
    for path in PAGES:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_page(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
