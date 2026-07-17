"""Graph Monthly レイアウト — 折れ線1本構成に合わせた帯高・▶分析リンク位置."""

from __future__ import annotations

MONTHLY_BODY_H_OLD = """      --insight-graph-monthly-body-h: calc(
        var(--insight-graph-monthly-row1-top) + var(--insight-graph-daily-chart-h) +
          var(--insight-graph-monthly-trend-gap-after-bar) + var(--insight-graph-monthly-trend-block-h) * 2 +
          var(--insight-graph-monthly-trend-gap-between-graphs)
      );"""

MONTHLY_BODY_H_NEW = """      --insight-graph-monthly-body-h: calc(
        var(--insight-graph-monthly-row1-top) + var(--insight-graph-daily-chart-h) +
          var(--insight-graph-monthly-trend-gap-after-bar) + var(--insight-graph-monthly-trend-block-h)
      );"""

MONTHLY_BODY_H_COMMENT_OLD = "      /* Graph Monthly: Graph2下端→0.5px横線 168px（▶分析の下→横線 46px） */"
MONTHLY_BODY_H_COMMENT_NEW = "      /* Graph Monthly: 折れ線下端→0.5px横線 168px（▶分析の下→横線 46px） */"

MONTHLY_ANALYZE_LINK_OLD = """    .insight-pane--graph #insight-jump-graph-monthly > .insight-graph-analyze-link {
      top: calc(
        var(--insight-monthly-analyze-top) + var(--insight-graph-monthly-content-h) +
          var(--insight-kpi-graph-gap-box-to-bar)
      );
    }"""

MONTHLY_ANALYZE_LINK_NEW = """    .insight-pane--graph #insight-jump-graph-monthly > .insight-graph-analyze-link {
      top: calc(
        var(--insight-graph-monthly-body-h) + var(--insight-graph-monthly-gap-after-graph2)
      );
    }"""

MARKER_BODY_H = "var(--insight-graph-monthly-trend-block-h) * 2"
MARKER_ANALYZE_LINK = "var(--insight-graph-monthly-body-h) + var(--insight-graph-monthly-gap-after-graph2)"
