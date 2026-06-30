#!/usr/bin/env python3
"""Graph tab Annual section: bar + graph1 + graph2 (clone Monthly, annual axis 365/366)."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

FILES = [
    (ROOT / "app/monthly/index.html", ROOT / "scripts/_annual_graphs_ja.html", "ja"),
    (ROOT / "en/app/monthly/index.html", ROOT / "scripts/_annual_graphs_en.html", "en"),
    (ROOT / "app/annual/index.html", ROOT / "scripts/_annual_graphs_ja.html", "ja"),
    (ROOT / "en/app/annual/index.html", ROOT / "scripts/_annual_graphs_en.html", "en"),
]

ANNUAL_YEAR_HELPERS = """
        function getFocusYearContext() {
          var data = window.__ANNUAL_DATA || {};
          var iso = data.daily && data.daily.selectedDate;
          var year;
          var month;
          var day;
          if (iso) {
            var parts = String(iso).split('-');
            year = Number(parts[0]);
            month = Number(parts[1]);
            day = Number(parts[2]);
          } else {
            var now = new Date();
            year = now.getFullYear();
            month = now.getMonth() + 1;
            day = now.getDate();
          }
          if (!Number.isFinite(year)) year = new Date().getFullYear();
          if (!Number.isFinite(month)) month = 1;
          if (!Number.isFinite(day)) day = 1;
          var dim = daysInYear(year);
          var start = new Date(year, 0, 1);
          var dt = new Date(year, month - 1, day);
          var dayOfYear = Math.floor((dt - start) / 86400000) + 1;
          if (!Number.isFinite(dayOfYear) || dayOfYear < 1) dayOfYear = 1;
          if (dayOfYear > dim) dayOfYear = dim;
          return { year: year, month: month, day: day, dayOfYear: dayOfYear, dim: dim };
        }

        function daysInYear(year) {
          return (year % 4 === 0 && year % 100 !== 0) || year % 400 === 0 ? 366 : 365;
        }

        function calendarFromDayOfYear(year, dayOfYear) {
          var dt = new Date(year, 0, dayOfYear);
          return { year: dt.getFullYear(), month: dt.getMonth() + 1, day: dt.getDate() };
        }

        function formatTooltipDateFromDayOfYear(year, dayOfYear) {
          var cal = calendarFromDayOfYear(year, dayOfYear);
          var dt = new Date(cal.year, cal.month - 1, cal.day);
          var wd = isEn ? weekdayEn[dt.getDay()] : weekdayJa[dt.getDay()];
          if (isEn) return cal.year + '.' + cal.month + '.' + cal.day + ' ' + wd;
          return cal.year + '.' + cal.month + '.' + cal.day + ' (' + wd + ')';
        }

        function buildXTickMonths(year, dim) {
          var ticks = [];
          for (var m = 1; m <= 12; m++) {
            var start = new Date(year, m - 1, 1);
            var dayOfYear = Math.floor((start - new Date(year, 0, 1)) / 86400000) + 1;
            if (dayOfYear < 1) dayOfYear = 1;
            if (dayOfYear > dim) dayOfYear = dim;
            ticks.push({ day: dayOfYear, label: String(m) });
          }
          return ticks;
        }
"""

OLD_FOCUS_BLOCK = """        function getFocusYearMonth() {
          var data = window.__ANNUAL_DATA || {};
          var iso = data.daily && data.daily.selectedDate;
          if (iso) {
            var parts = String(iso).split('-');
            var y = Number(parts[0]);
            var m = Number(parts[1]);
            if (Number.isFinite(y) && Number.isFinite(m)) return { year: y, month: m };
          }
          var now = new Date();
          return { year: now.getFullYear(), month: now.getMonth() + 1 };
        }

        function daysInMonth(year, month) {
          return new Date(year, month, 0).getDate();
        }

        function formatAxisMoney(v) {"""

NEW_FOCUS_BLOCK = ANNUAL_YEAR_HELPERS + """
        function formatAxisMoney(v) {"""

OLD_TOOLTIP_FN = """        function formatTooltipDate(year, month, day) {
          var dt = new Date(year, month - 1, day);
          var wd = isEn ? weekdayEn[dt.getDay()] : weekdayJa[dt.getDay()];
          if (isEn) return year + '.' + month + '.' + day + ' ' + wd;
          return year + '.' + month + '.' + day + ' (' + wd + ')';
        }

        function niceYMax"""

NEW_TOOLTIP_FN = """        function niceYMax"""

OLD_XTICK = """        function buildXTickDays(dim) {
          if (dim <= 1) return [1];
          var slots = CFG.xTickSlots;
          var days = [];
          for (var i = 0; i < slots; i++) {
            var d = Math.round(1 + ((dim - 1) * i) / (slots - 1));
            if (days.indexOf(d) === -1) days.push(d);
          }
          if (days[days.length - 1] !== dim) days[days.length - 1] = dim;
          return days;
        }

        function buildDemoPayload(dim) {
          var baseDaily = isEn ? 4000 : 400000;"""

NEW_XTICK = """        function buildDemoPayload(dim, todayDay) {
          var baseDaily = isEn ? 12000 : 1200000;"""

OLD_PAYLOAD_TAIL = """          var todayDay = Math.min(dim, 18);
          return {"""

NEW_PAYLOAD_TAIL = """          var endDay = Math.min(dim, todayDay || Math.min(dim, 132));
          return {"""

OLD_PAYLOAD_TODAY = """            todayDay: todayDay"""
NEW_PAYLOAD_TODAY_FIELD = """            todayDay: endDay"""

# graph1 render block
OLD_RENDER_G1 = """        function render() {
          var ym = getFocusYearMonth();
          var dim = daysInMonth(ym.year, ym.month);
          if (periodEl) periodEl.textContent = ym.year + '.' + ym.month;

          var payload = buildDemoPayload(dim);
          var yMax = niceYMax(
            Math.max.apply(null, payload.target.concat(payload.actual)),
            CFG.yTicks
          );

          frame.__trendChartState = { dim: dim, ym: ym, payload: payload, yMax: yMax };"""

NEW_RENDER_G1 = """        function render() {
          var ctx = getFocusYearContext();
          var dim = ctx.dim;
          if (periodEl) periodEl.textContent = String(ctx.year);

          var payload = buildDemoPayload(dim, ctx.dayOfYear);
          var yMax = niceYMax(
            Math.max.apply(null, payload.target.concat(payload.actual)),
            CFG.yTicks
          );

          frame.__trendChartState = { dim: dim, ctx: ctx, payload: payload, yMax: yMax };"""

OLD_XLOOP_G1 = """          buildXTickDays(dim).forEach(function (day) {
            var xx = xForDay(day, dim);
            axesG.appendChild(svgText(xx, CFG.plotBottom + 18, 'middle', String(day)));
          });"""

NEW_XLOOP_G1 = """          buildXTickMonths(ctx.year, dim).forEach(function (tick) {
            var xx = xForDay(tick.day, dim);
            axesG.appendChild(svgText(xx, CFG.plotBottom + 18, 'middle', tick.label));
          });"""

OLD_TIP_G1 = """          if (dateEl) dateEl.textContent = formatTooltipDate(state.ym.year, state.ym.month, hit.day);"""

NEW_TIP_G1 = """          if (dateEl) dateEl.textContent = formatTooltipDateFromDayOfYear(state.ctx.year, hit.day);"""

# graph2 render
OLD_RENDER_G2 = """        function render() {
          var ym = getFocusYearMonth();
          var dim = daysInMonth(ym.year, ym.month);
          var payload = buildComparePayload(dim);
          var allVals = payload.best.concat(payload.lastYear).concat(payload.current);
          var yMax = niceYMax(Math.max.apply(null, allVals), CFG.yTicks);

          frame.__trendChartState = { dim: dim, ym: ym, payload: payload, yMax: yMax };"""

NEW_RENDER_G2 = """        function render() {
          var ctx = getFocusYearContext();
          var dim = ctx.dim;
          var payload = buildComparePayload(dim, ctx.dayOfYear);
          var allVals = payload.best.concat(payload.lastYear).concat(payload.current);
          var yMax = niceYMax(Math.max.apply(null, allVals), CFG.yTicks);

          frame.__trendChartState = { dim: dim, ctx: ctx, payload: payload, yMax: yMax };"""

OLD_XLOOP_G2 = OLD_XLOOP_G1
NEW_XLOOP_G2 = NEW_XLOOP_G1

OLD_TIP_G2 = """          if (dateEl) dateEl.textContent = formatTooltipDate(state.ym.year, state.ym.month, hit.day);"""

NEW_TIP_G2 = NEW_TIP_G1

OLD_COMPARE = """        function buildComparePayload(dim) {
          var baseDaily = isEn ? 650 : 65000;"""

NEW_COMPARE = """        function buildComparePayload(dim, todayDay) {
          var baseDaily = isEn ? 12000 : 1200000;"""

OLD_COMPARE_TODAY = """          var todayDay = Math.min(dim, 22);"""

NEW_COMPARE_TODAY = """          var endDay = Math.min(dim, todayDay || Math.min(dim, 132));"""

VARS_OLD = """      --insight-graph-annual-content-h: 0px;
      --insight-band-annual-graph: calc(
        var(--insight-annual-analyze-top) + var(--insight-graph-annual-content-h) +
          var(--insight-annual-analyze-strategy-tail-h) + var(--insight-section-bottom-pad)
      );"""

VARS_NEW = """      --insight-graph-annual-row1-top: var(--insight-graph-daily-row1-top);
      --insight-graph-annual-trend-gap-after-bar: 98px;
      --insight-graph-annual-trend-heading-gap: 39px;
      --insight-graph-annual-trend-frame-w: 965px;
      --insight-graph-annual-trend-frame-h: 618px;
      --insight-graph-annual-trend-block-h: calc(
        var(--insight-graph-annual-trend-heading-gap) + 16px * 1.2 +
          var(--insight-graph-annual-trend-frame-h)
      );
      --insight-graph-annual-trend-top: calc(
        var(--insight-graph-annual-row1-top) + var(--insight-graph-daily-chart-h) +
          var(--insight-graph-annual-trend-gap-after-bar)
      );
      --insight-graph-annual-trend-gap-between-graphs: 48px;
      --insight-graph-annual-trend2-top: calc(
        var(--insight-graph-annual-trend-top) + var(--insight-graph-annual-trend-block-h) +
          var(--insight-graph-annual-trend-gap-between-graphs)
      );
      --insight-graph-annual-body-h: calc(
        var(--insight-graph-annual-row1-top) + var(--insight-graph-daily-chart-h) +
          var(--insight-graph-annual-trend-gap-after-bar) + var(--insight-graph-annual-trend-block-h) * 2 +
          var(--insight-graph-annual-trend-gap-between-graphs)
      );
      --insight-graph-annual-section-bottom-pad: 46px;
      --insight-graph-annual-gap-graph2-to-section-bottom: 168px;
      --insight-graph-annual-gap-after-graph2: calc(
        var(--insight-graph-annual-gap-graph2-to-section-bottom) -
          var(--insight-graph-annual-section-bottom-pad) - var(--insight-graph-analyze-link-line-h)
      );
      --insight-graph-annual-analyze-link-tail-h: var(--insight-graph-annual-gap-graph2-to-section-bottom);
      --insight-graph-annual-content-h: var(--insight-graph-annual-body-h);
      --insight-band-annual-graph: calc(
        var(--insight-graph-daily-section-label-stack-h) + var(--insight-graph-annual-body-h) +
          var(--insight-graph-annual-analyze-link-tail-h) + var(--insight-atr-back-to-top-h) +
          var(--insight-section-bottom-pad)
      );"""

ANNUAL_ANALYZE_CSS_OLD = """    .insight-pane--graph #insight-jump-graph-annual > .insight-graph-analyze-link {
      top: calc(
        var(--insight-annual-analyze-top) + var(--insight-graph-annual-content-h) +
          var(--insight-kpi-graph-gap-box-to-bar)
      );
    }"""

ANNUAL_ANALYZE_CSS_NEW = """    .insight-pane--graph #insight-graph-annual-analyze-link {
      top: calc(
        var(--insight-graph-annual-body-h) + var(--insight-graph-annual-gap-after-graph2)
      );
      bottom: auto;
      display: block;
      margin-top: 0;
    }"""

ANNUAL_MONTHLY_CSS = Path(ROOT / "app/monthly/index.html").read_text(encoding="utf-8")
m = re.search(
    r"/\* Graph tab — Monthly: Cumulative Trend.*?\n    \.office-mode \.insight-pane--graph \.insight-graph-monthly-trend__tooltip \{\n      background: #fff;\n      border-color: #2a2a2a;\n    \}\n",
    ANNUAL_MONTHLY_CSS,
    re.S,
)
if not m:
    raise SystemExit("monthly trend css block not found")
monthly_css = m.group(0)
annual_css = monthly_css.replace("Monthly", "Annual").replace("monthly", "annual")
# best line blue for annual compare
annual_css = annual_css.replace("#e6ff00", "#5b7cff")
ANNUAL_CSS_INSERT = (
    annual_css
    + "\n    .insight-pane--graph .insight-graph-annual {\n"
    + "      min-height: var(--insight-graph-annual-body-h);\n"
    + "      padding-bottom: var(--insight-graph-annual-analyze-link-tail-h);\n"
    + "      box-sizing: content-box;\n"
    + "    }\n"
    + "    .insight-pane--graph .insight-graph-annual-trend--graph1 {\n"
    + "      top: var(--insight-graph-annual-trend-top);\n"
    + "    }\n"
    + "    .insight-pane--graph .insight-graph-annual-trend--graph2 {\n"
    + "      top: var(--insight-graph-annual-trend2-top);\n"
    + "    }\n"
)

# cumulative row css from monthly
m2 = re.search(
    r"\.insight-pane--graph \.insight-graph-monthly__row-title \{.*?\n    /\* Graph tab — Monthly: Cumulative Trend",
    ANNUAL_MONTHLY_CSS,
    re.S,
)
if not m2:
    raise SystemExit("monthly row css not found")
annual_row_css = m2.group(0).replace("/* Graph tab — Monthly: Cumulative Trend", "/* Graph tab — Annual: cumulative bar + trends")
annual_row_css = annual_row_css.replace("monthly", "annual")


def patch_annual_js(src: Path, graph_num: int) -> str:
    t = src.read_text(encoding="utf-8")
    t = t.replace(OLD_FOCUS_BLOCK, NEW_FOCUS_BLOCK)
    t = t.replace(OLD_TOOLTIP_FN, NEW_TOOLTIP_FN)
    t = t.replace(OLD_XTICK, NEW_XTICK)
    t = t.replace(OLD_PAYLOAD_TAIL, NEW_PAYLOAD_TAIL)
    t = t.replace(OLD_PAYLOAD_TODAY, NEW_PAYLOAD_TODAY_FIELD)
    if graph_num == 1:
        t = t.replace(OLD_RENDER_G1, NEW_RENDER_G1)
        t = t.replace(OLD_XLOOP_G1, NEW_XLOOP_G1)
        t = t.replace(OLD_TIP_G1, NEW_TIP_G1)
    else:
        t = t.replace(OLD_COMPARE, NEW_COMPARE)
        t = t.replace(OLD_COMPARE_TODAY, NEW_COMPARE_TODAY)
        t = t.replace(OLD_RENDER_G2, NEW_RENDER_G2)
        t = t.replace(OLD_XLOOP_G2, NEW_XLOOP_G2)
        t = t.replace(OLD_TIP_G2, NEW_TIP_G2)
    return t


def build_html_snippets():
    for lang, suffix in [("ja", "_ja"), ("en", "_en")]:
        monthly_bar = (ROOT / f"scripts/_monthly_graphs{suffix}.html").read_text(encoding="utf-8")
        # bar only: up to first graph1
        bar_end = monthly_bar.find('<div class="insight-graph-monthly-trend')
        bar = monthly_bar[:bar_end]
        bar = bar.replace("monthly", "annual").replace("Monthly", "Annual")
        if lang == "ja":
            bar = bar.replace("累計目標", "累計目標").replace("本日（売上）", "本日（売上）")
        graphs = monthly_bar[bar_end:]
        graphs = graphs.replace("monthly", "annual").replace("Monthly", "Annual")
        graphs = graphs.replace("月次累計推移比較", "年次累計推移比較")
        graphs = graphs.replace("Monthly Cumulative Trend Compare", "Annual Cumulative Trend Compare")
        graphs = graphs.replace("当月累計（今年）", "当年累計（今年）")
        graphs = graphs.replace("前年同月累計", "前年累計")
        graphs = graphs.replace("過去同月ベスト累計", "過去最高年累計")
        graphs = graphs.replace("Current Month (This Year)", "Current Year Line")
        graphs = graphs.replace("Same Month (Last Year)", "Last Year Line")
        graphs = graphs.replace("Best Historical (Same Month)", "Best Historical Year Line")
        # graph1: year only in period
        graphs = graphs.replace('id="insight-graph-annual-graph1-period">2026.5', 'id="insight-graph-annual-graph1-period">2026')
        # graph2: no period line (like monthly graph2)
        graphs = re.sub(
            r'\n                    <p class="insight-graph-annual-trend__period" id="insight-graph-annual-graph2-period">[^<]*</p>',
            "",
            graphs,
        )
        # remove achievement from graph2 if present - monthly graph2 has no achievement
        # analyze link inside wrapper
        graphs = graphs.replace(
            'id="insight-graph-monthly-analyze-link"',
            'id="insight-graph-annual-analyze-link"',
        )
        graphs = graphs.replace("insight-graph-monthly-analyze-link", "insight-graph-annual-analyze-link")
        # hover width
        graphs = graphs.replace('width="800"', 'width="817"')
        out = bar + graphs
        (ROOT / f"scripts/_annual_graphs{suffix}.html").write_text(out, encoding="utf-8")


def patch_file(path: Path, html_snippet: Path, g1: str, g2: str):
    text = path.read_text(encoding="utf-8")

    if VARS_OLD in text:
        text = text.replace(VARS_OLD, VARS_NEW, 1)

    if ANNUAL_ANALYZE_CSS_OLD in text:
        text = text.replace(ANNUAL_ANALYZE_CSS_OLD, ANNUAL_ANALYZE_CSS_NEW, 1)

    anchor_css = "    /* Graph tab — Monthly: Cumulative Trend"
    if "insight-graph-annual-trend--graph1" not in text and anchor_css in text:
        text = text.replace(anchor_css, annual_row_css + "\n" + ANNUAL_CSS_INSERT + anchor_css, 1)

    old_annual = re.search(
        r'              <div class="insight-graph-annual"[^>]*>.*?</div>\s*<a\s*\n\s*class="insight-graph-analyze-link"\s*\n\s*id="insight-graph-annual-analyze-link"[^>]*>.*?</a>\s*<div class="insight-pane--graph__foot">',
        text,
        re.S,
    )
    snippet = html_snippet.read_text(encoding="utf-8").strip()
    if "en/" in str(path):
        snippet = snippet.replace("▶ 分析", "▶ Analyze").replace("年次累計", "Annual Cumulative")
    new_block = (
        '              <div class="insight-graph-annual" aria-label="Annual グラフ比較">\n'
        + snippet
        + "\n              </div>\n              <div class=\"insight-pane--graph__foot\">"
    )
    if old_annual:
        text = text[: old_annual.start()] + new_block + text[old_annual.end() :]
    else:
        raise SystemExit(f"annual placeholder not found in {path}")

    if "function initGraphAnnualCumulativeTrendGraph1" not in text:
        marker2 = "      initGraphMonthlyCumulativeTrendGraph2();\n"
        idx = text.find(marker2)
        if idx < 0:
            raise SystemExit("js insert point not found")
        text = text[: idx + len(marker2)] + g1 + "\n" + g2 + text[idx + len(marker2) :]
        text = text.replace(
            marker2,
            marker2
            + "      initGraphAnnualCumulativeTrendGraph1();\n"
            + "      initGraphAnnualCumulativeTrendGraph2();\n",
            1,
        )

    if "insight-graph-annual-cumulative-target-actual" not in text:
        text = text.replace(
            "        fallbackPercent: 123\n      });",
            "        fallbackPercent: 123\n      });\n      initAllocationWidget({\n        graphId: 'insight-graph-annual-cumulative-target-actual',\n        percentId: 'insight-graph-annual-cumulative-target-actual-pct',\n        dataKey: 'achievementPercent',\n        graphWidth: 653,\n        editable: false,\n        achievementAlertColors: true,\n        fallbackPercent: 123\n      });",
            1,
        )

    path.write_text(text, encoding="utf-8")
    print(f"patched {path}")


def main():
    build_html_snippets()
    g1 = patch_annual_js(ROOT / "scripts/_trend_chart_annual_graph1_base.js", 1)
    g2 = patch_annual_js(ROOT / "scripts/_trend_chart_annual_graph2_base.js", 2)
    (ROOT / "scripts/_trend_chart_annual_graph1.js").write_text(g1, encoding="utf-8")
    (ROOT / "scripts/_trend_chart_annual_graph2.js").write_text(g2, encoding="utf-8")

    for path, snippet, _ in FILES:
        patch_file(path, snippet, g1, g2)


if __name__ == "__main__":
    main()
