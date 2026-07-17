#!/usr/bin/env python3
"""復旧専用: Annual ページの Graph → Annual を Monthly と同等のデモ描画に戻す.

対象のみ（データ配線・Insight Summary/Analyze は触らない）:
  - CSS 変数（帯高スタブ → 実寸）
  - Graph Annual 用 CSS
  - HTML（準備中プレースホルダ → Monthly 同等）
  - initGraphAnnual* JS + 初期化呼び出し
  - 累計棒の initAllocationWidget

ペア:
  app/monthly → app/annual
  en/app/monthly → en/app/annual
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAIRS = [
    (ROOT / "app/monthly/index.html", ROOT / "app/annual/index.html"),
    (ROOT / "en/app/monthly/index.html", ROOT / "en/app/annual/index.html"),
]

VARS_OLD = """      --insight-graph-annual-content-h: 0px;
      --insight-band-annual-graph: calc(
        var(--insight-annual-analyze-top) + var(--insight-graph-annual-content-h) +
          var(--insight-annual-analyze-strategy-tail-h) + var(--insight-section-bottom-pad)
      );"""

VARS_START = "      --insight-graph-annual-row1-top:"
VARS_END_MARK = "      --insight-band-daily: max("

HELPER_VARS = """      --insight-graph-analyze-link-line-h: calc(13px * 1.2);
      --insight-graph-daily-section-label-stack-h: calc(47px + 40px + 30px);
"""

CSS_START = "    .insight-pane--graph .insight-graph-annual__row-title {"
CSS_END = "    /* Graph tab — Monthly: Cumulative Trend 折れ線"

ANALYZE_LINK_OLD = """    .insight-pane--graph #insight-jump-graph-annual > .insight-graph-analyze-link {
      top: calc(
        var(--insight-annual-analyze-top) + var(--insight-graph-annual-content-h) +
          var(--insight-kpi-graph-gap-box-to-bar)
      );
    }"""

ANALYZE_LINK_NEW = """    .insight-pane--graph #insight-graph-annual-analyze-link {
      top: calc(
        var(--insight-graph-annual-body-h) + var(--insight-graph-annual-gap-after-graph2)
      );
      bottom: auto;
      display: block;
      margin-top: 0;
    }"""

HTML_SECTION_ID = 'id="insight-jump-graph-annual"'

JS_FN_START = "      function initGraphAnnualCumulativeTrendGraph1() {"
JS_FN_END = "      function initGraphDailyHistoricalWeekday() {"

ALLOC_ANNUAL = """      initAllocationWidget({
        graphId: 'insight-graph-annual-cumulative-target-actual',
        percentId: 'insight-graph-annual-cumulative-target-actual-pct',
        dataKey: 'achievementPercent',
        graphWidth: 653,
        editable: false,
        achievementAlertColors: true,
        fallbackPercent: 123
      });
"""

ALLOC_MONTHLY_MARKER = "graphId: 'insight-graph-monthly-cumulative-target-actual'"


def extract_between(text: str, start: str, end: str, label: str) -> str:
    i = text.find(start)
    if i < 0:
        raise SystemExit(f"{label}: start not found")
    j = text.find(end, i + len(start))
    if j < 0:
        raise SystemExit(f"{label}: end not found")
    return text[i:j]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        if new in text or (label == "analyze-link" and "insight-graph-annual-body-h) + var(--insight-graph-annual-gap-after-graph2)" in text):
            return text
        raise SystemExit(f"{label}: old block not found")
    return text.replace(old, new, 1)


def extract_section(text: str, label: str) -> str:
    i = text.find(HTML_SECTION_ID)
    if i < 0:
        raise SystemExit(f"{label}: section id miss")
    sec_start = text.rfind("<section", 0, i)
    j = text.find('id="insight-graph-annual-analyze-link"', i)
    if j < 0:
        raise SystemExit(f"{label}: analyze-link miss")
    end = text.find("</section>", j)
    if end < 0:
        raise SystemExit(f"{label}: section end miss")
    end += len("</section>")
    return text[sec_start:end]


def extract_annual_vars(src: str) -> str:
    i = src.find(VARS_START)
    if i < 0:
        raise SystemExit("src annual vars start miss")
    j = src.find(VARS_END_MARK, i)
    if j < 0:
        raise SystemExit("src annual vars end miss")
    return src[i:j]


def patch_vars(dst: str, src_vars: str) -> str:
    if VARS_START in dst and "--insight-graph-annual-body-h:" in dst:
        # already restored — replace whole annual var block to stay in sync with src
        i = dst.find(VARS_START)
        j = dst.find(VARS_END_MARK, i)
        if j < 0:
            raise SystemExit("dst annual vars end miss")
        out = dst[:i] + src_vars + dst[j:]
    else:
        out = replace_once(dst, VARS_OLD, src_vars, "vars-stub")

    if "--insight-graph-analyze-link-line-h:" not in out:
        # insert helpers just before annual row1-top
        out = out.replace(VARS_START, HELPER_VARS + VARS_START, 1)
    elif "--insight-graph-daily-section-label-stack-h:" not in out:
        out = out.replace(
            "      --insight-graph-analyze-link-line-h: calc(13px * 1.2);\n",
            "      --insight-graph-analyze-link-line-h: calc(13px * 1.2);\n"
            "      --insight-graph-daily-section-label-stack-h: calc(47px + 40px + 30px);\n",
            1,
        )
    return out


def patch_css(dst: str, src: str) -> str:
    css_block = extract_between(src, CSS_START, CSS_END, "annual-css")
    if CSS_START in dst:
        i = dst.find(CSS_START)
        j = dst.find(CSS_END, i)
        if j < 0:
            # annual may have monthly trend without the comment variant
            alt = "    .insight-pane--graph .insight-graph-monthly-trend {"
            j = dst.find(alt, i)
            if j < 0:
                raise SystemExit("dst annual css end miss")
            return dst[:i] + css_block + dst[j:]
        return dst[:i] + css_block + dst[j:]

    # insert before Monthly Cumulative Trend
    anchor = "    /* Graph tab — Monthly: Cumulative Trend 折れ線（docs/insight-graph-cumulative-trend-line-chart.md） */"
    if anchor not in dst:
        anchor = "    .insight-pane--graph .insight-graph-monthly-trend {"
    if anchor not in dst:
        raise SystemExit("css insert anchor miss")
    return dst.replace(anchor, css_block + anchor, 1)


def patch_html(dst: str, src: str) -> str:
    src_sec = extract_section(src, "src")
    dst_sec = extract_section(dst, "dst")
    if dst_sec == src_sec:
        return dst
    return dst.replace(dst_sec, src_sec, 1)


def patch_js(dst: str, src: str) -> str:
    js_block = extract_between(src, JS_FN_START, JS_FN_END, "annual-js")
    inits = (
        "      initGraphAnnualCumulativeTrendGraph1();\n"
        "      initGraphAnnualCumulativeTrendGraph2();\n"
    )

    if JS_FN_START in dst:
        i = dst.find(JS_FN_START)
        j = dst.find(JS_FN_END, i)
        if j < 0:
            raise SystemExit("dst annual js end miss")
        dst = dst[:i] + js_block + dst[j:]
    else:
        # Prefer replace duplicate monthly init; fallback single call.
        dup = (
            "      initGraphMonthlyCumulativeTrend();\n"
            "      initGraphMonthlyCumulativeTrend();\n"
            "      function initGraphDailyHistoricalWeekday() {"
        )
        single = (
            "      initGraphMonthlyCumulativeTrend();\n"
            "      function initGraphDailyHistoricalWeekday() {"
        )
        if dup in dst:
            dst = dst.replace(
                dup,
                "      initGraphMonthlyCumulativeTrend();\n" + js_block + JS_FN_END,
                1,
            )
        elif single in dst:
            dst = dst.replace(
                single,
                "      initGraphMonthlyCumulativeTrend();\n" + js_block + JS_FN_END,
                1,
            )
        else:
            raise SystemExit("js insert anchor miss")

    # Ensure init calls before initGraphDailyHistoricalWeekday()
    call_anchor = "      initGraphDailyHistoricalWeekday();"
    if "initGraphAnnualCumulativeTrendGraph1();" not in dst:
        if call_anchor not in dst:
            raise SystemExit("init call anchor miss")
        dst = dst.replace(call_anchor, inits + call_anchor, 1)
    else:
        # Normalize: Graph1/Graph2 then historical
        dst = re.sub(
            r"(?:      initGraphAnnualCumulativeTrendGraph1\(\);\n)+"
            r"(?:      initGraphAnnualCumulativeTrendGraph2\(\);\n)*",
            inits,
            dst,
            count=1,
        )

    return dst


def patch_alloc(dst: str) -> str:
    if "insight-graph-annual-cumulative-target-actual'" in dst and "initAllocationWidget" in dst:
        # check dedicated widget exists
        if "graphId: 'insight-graph-annual-cumulative-target-actual'" in dst:
            return dst
    if ALLOC_MONTHLY_MARKER not in dst:
        raise SystemExit("monthly alloc widget miss — unexpected")
    # insert after monthly cumulative widget block
    # find the monthly widget and append after its closing });
    idx = dst.find(ALLOC_MONTHLY_MARKER)
    close = dst.find("});", idx)
    if close < 0:
        raise SystemExit("monthly alloc close miss")
    close += len("});")
    return dst[:close] + "\n" + ALLOC_ANNUAL + dst[close:]


def patch_analyze_link(dst: str) -> str:
    return replace_once(dst, ANALYZE_LINK_OLD, ANALYZE_LINK_NEW, "analyze-link")


def verify(dst: str, path: Path) -> None:
    required = [
        'id="insight-graph-annual-graph1"',
        'id="insight-graph-annual-graph2"',
        "function initGraphAnnualCumulativeTrendGraph1",
        "function initGraphAnnualCumulativeTrendGraph2",
        "initGraphAnnualCumulativeTrendGraph1();",
        "initGraphAnnualCumulativeTrendGraph2();",
        "--insight-graph-annual-body-h:",
        "min-height: var(--insight-graph-annual-body-h)",
        "graphId: 'insight-graph-annual-cumulative-target-actual'",
    ]
    missing = [r for r in required if r not in dst]
    if missing:
        raise SystemExit(f"verify fail {path}: missing {missing}")
    if "Annual グラフ（準備中）" in dst:
        raise SystemExit(f"verify fail {path}: placeholder remains")


def patch_pair(src_path: Path, dst_path: Path) -> None:
    src = src_path.read_text(encoding="utf-8")
    dst = dst_path.read_text(encoding="utf-8")

    src_vars = extract_annual_vars(src)
    dst = patch_vars(dst, src_vars)
    dst = patch_css(dst, src)
    dst = patch_analyze_link(dst)
    dst = patch_html(dst, src)
    dst = patch_js(dst, src)
    dst = patch_alloc(dst)

    verify(dst, dst_path)
    dst_path.write_text(dst, encoding="utf-8")
    print(f"OK {dst_path.relative_to(ROOT)} (from {src_path.relative_to(ROOT)})")


def main() -> int:
    for src, dst in PAIRS:
        if not src.is_file() or not dst.is_file():
            print(f"missing {src} or {dst}", file=sys.stderr)
            return 1
        patch_pair(src, dst)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
