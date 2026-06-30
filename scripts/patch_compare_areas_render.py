#!/usr/bin/env python3
"""Patch build_pl_table_page.py for Area 2/3 compare rendering."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts" / "build_pl_table_page.py"
RENDER_SNIPPET = Path(__file__).resolve().parent / "_compare_areas_render.js"


def brace_js(js: str) -> str:
    return js.replace("{", "{{").replace("}", "}}")


def main() -> None:
    text = TARGET.read_text(encoding="utf-8")
    render_block = brace_js(RENDER_SNIPPET.read_text(encoding="utf-8"))

    # 1. Tooltip: add axisMode support
    old_tooltip = """      function area1FillChartTooltip(tooltip, cfg, day) {{
        var parts = cfg.isoParts;
        if (!parts || !tooltip) return null;
        var idx = day - 1;
        var rows = [];
        rows.push({{
          label: L.compare_this_year,
          date: fmtDateYmd(parts.year, parts.month, day),
          value: cfg.values.thisYear[idx] || 0,
          color: '#66e7ff',
        }});
        if (cfg.showLast) {{
          rows.push({{
            label: L.compare_last_year,
            date: fmtDateYmd(parts.year - 1, parts.month, day),
            value: cfg.values.lastYear[idx] || 0,
            color: '#e8e54b',
          }});
        }}
        if (cfg.showBest && cfg.canShowBest) {{
          rows.push({{
            label: L.compare_best_year,
            date: fmtDateYmd(cfg.bestYear, parts.month, day),
            value: cfg.values.bestYear[idx] || 0,
            color: '#16d33a',
          }});
        }}
        var snapEl = tooltip.querySelector('[data-field="snap"]');
        if (snapEl) {{
          snapEl.textContent = fmtDateYmd(parts.year, parts.month, day);
        }}"""

    new_tooltip = """      function fmtComparePeriodDate(year, month, period, axisMode) {{
        if (axisMode === 'month') return year + '/' + period;
        return fmtDateYmd(year, month, period);
      }}

      function area1FillChartTooltip(tooltip, cfg, day) {{
        var parts = cfg.isoParts;
        if (!parts || !tooltip) return null;
        var axisMode = cfg.axisMode || 'day';
        var idx = day - 1;
        var rows = [];
        rows.push({{
          label: L.compare_this_year,
          date: fmtComparePeriodDate(parts.year, parts.month, day, axisMode),
          value: cfg.values.thisYear[idx] || 0,
          color: '#66e7ff',
        }});
        if (cfg.showLast) {{
          rows.push({{
            label: L.compare_last_year,
            date: fmtComparePeriodDate(parts.year - 1, parts.month, day, axisMode),
            value: cfg.values.lastYear[idx] || 0,
            color: '#e8e54b',
          }});
        }}
        if (cfg.showBest && cfg.canShowBest) {{
          rows.push({{
            label: L.compare_best_year,
            date: fmtComparePeriodDate(cfg.bestYear, parts.month, day, axisMode),
            value: cfg.values.bestYear[idx] || 0,
            color: '#16d33a',
          }});
        }}
        var snapEl = tooltip.querySelector('[data-field="snap"]');
        if (snapEl) {{
          snapEl.textContent = fmtComparePeriodDate(parts.year, parts.month, day, axisMode);
        }}"""

    if old_tooltip not in text:
        raise SystemExit("tooltip block not found")
    text = text.replace(old_tooltip, new_tooltip, 1)

    # 2. Slim buildArea1ChartData
    start = text.index("      function buildArea1ChartData(iso) {{")
    end = text.index("      function buildArea2ChartData(iso) {{")
    text = (
        text[:start]
        + """      function buildArea1ChartData(iso) {{
        var d = new Date(String(iso || '').trim() + 'T00:00:00');
        if (!isFinite(d.getTime())) return null;
        var dim = d.getDate();
        var year = d.getFullYear();
        var month = d.getMonth() + 1;
        var periodCount = new Date(year, month, 0).getDate();
        var daySeed = (year * 37 + month * 97 + dim * 13) % 1000;
        return buildCompareDayChartData(dim, periodCount, daySeed);
      }}

"""
        + text[end:]
    )

    # 3. Remove buildArea1ChartDataRefactored
    ref_start = text.index("      function buildArea1ChartDataRefactored(iso) {{")
    ref_end = text.index("      function buildArea1Series(iso) {{")
    text = text[:ref_start] + text[ref_end:]

    # 4. area1XTickSvgHtml delegates to compareXTickSvgHtml
    old_xtick = """      function area1XTickSvgHtml(daysInMonth, padL, plotW, padT, plotH) {{
        var y = padT + plotH + 16;
        return area1XTickDays(daysInMonth)
          .map(function (t) {{
            var x = comparePeriodCenterX(t, daysInMonth, padL, plotW);
            return (
              '<text x="' +
              x.toFixed(1) +
              '" y="' +
              y.toFixed(1) +
              '" text-anchor="middle" class="pl-compare-line__axis-label">' +
              t +
              '</text>'
            );
          }})
          .join('');
      }}"""
    new_xtick = """      function compareXTickSvgHtml(periodCount, ticks, padL, plotW, padT, plotH) {{
        var y = padT + plotH + 16;
        return ticks
          .map(function (t) {{
            var x = comparePeriodCenterX(t, periodCount, padL, plotW);
            return (
              '<text x="' +
              x.toFixed(1) +
              '" y="' +
              y.toFixed(1) +
              '" text-anchor="middle" class="pl-compare-line__axis-label">' +
              t +
              '</text>'
            );
          }})
          .join('');
      }}

      function area1XTickSvgHtml(daysInMonth, padL, plotW, padT, plotH) {{
        return compareXTickSvgHtml(daysInMonth, area1XTickDays(daysInMonth), padL, plotW, padT, plotH);
      }}"""
    if old_xtick not in text:
        raise SystemExit("area1XTickSvgHtml block not found")
    text = text.replace(old_xtick, new_xtick, 1)

    # 5. Replace renderArea1Line .. renderArea1FlSnapshot with generic renderers
    r_start = text.index("      function renderArea1Line(iso) {{")
    r_end = text.index("      function fillDate(iso) {{")
    # Remove duplicate fmtComparePeriodDate from render snippet (already in tooltip section)
    render_lines = render_block.splitlines()
    filtered = []
    skip = False
    for line in render_lines:
        if line.strip().startswith("function fmtComparePeriodDate"):
            skip = True
            continue
        if skip:
            if line.strip() == "}":
                skip = False
            continue
        filtered.append(line)
    render_block_clean = "\n".join(filtered).replace(
        "'ol-compare-line pl-compare-daily'",
        "'pl-compare-line pl-compare-daily'",
    )
    text = text[:r_start] + render_block_clean + "\n" + text[r_end:]

    # 6. fillDate calls renderAllCompareAreas
    text = text.replace(
        "        renderArea1FlSnapshot(iso);",
        "        renderAllCompareAreas(iso);",
        1,
    )

    TARGET.write_text(text, encoding="utf-8")
    print("Patched", TARGET)


if __name__ == "__main__":
    main()
