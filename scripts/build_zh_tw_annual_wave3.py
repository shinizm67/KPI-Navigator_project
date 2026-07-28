#!/usr/bin/env python3
"""Annual zh-tw Wave 3: monthly table frame, Focus Bar / Daily TW, graph popover shell."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DST = ROOT / "zh-tw" / "app" / "annual" / "index.html"

WAVE3_REPLACEMENTS = [
    # Monthly open table
    ('aria-label="Annual monthly summary table"', 'aria-label="年度月次摘要表"'),
    (">Month</th>", ">月</th>"),
    (
        '<th data-tooltip="Business Day">Bussi D</th>',
        '<th data-tooltip="營業日數">營業日</th>',
    ),
    (
        '<th data-tooltip="Monthly Average Target Sales">M A Target</th>',
        '<th data-tooltip="月平均目標銷售">平均銷售額</th>',
    ),
    (
        '<th data-tooltip="Plan H/L % (read-only). Edit in Sales Data Analyze.">H/L Sea</th>',
        '<th data-tooltip="計畫旺淡%（唯讀）。請在 Sales Data 的 Analyze 編輯。">旺淡期%</th>',
    ),
    (
        '<th data-tooltip="Monthly Target Sales">Monthly Target</th>',
        '<th data-tooltip="月次目標銷售">月次目標</th>',
    ),
    (
        '<th data-tooltip="Daily Target Sales">Daily Target</th>',
        '<th data-tooltip="日次目標銷售">日次目標</th>',
    ),
    (">Monthly Profit</th>", ">月次銷售實績</th>"),
    (">Monthly KGI</th>", ">月間 KGI</th>"),
    (
        '<th data-tooltip="Monthly Seasonal Average Percentage">H/L Sea</th>',
        '<th data-tooltip="月次平均%（相對平均銷售額的實績%）">月次平均%</th>',
    ),
    (
        '<th data-tooltip="Monthly KPI Achievement Percentage (KGI vs KPI)">H/L %</th>',
        '<th data-tooltip="月次實質%（相對目標 KPI 的達成%）">月次實質%</th>',
    ),
    ("<td>Jan</td>", "<td>1月</td>"),
    ("<td>Feb</td>", "<td>2月</td>"),
    ("<td>Mar</td>", "<td>3月</td>"),
    ("<td>Apr</td>", "<td>4月</td>"),
    ("<td>May</td>", "<td>5月</td>"),
    ("<td>Jun</td>", "<td>6月</td>"),
    ("<td>Jul</td>", "<td>7月</td>"),
    ("<td>Aug</td>", "<td>8月</td>"),
    ("<td>Sep</td>", "<td>9月</td>"),
    ("<td>Oct</td>", "<td>10月</td>"),
    ("<td>Nov</td>", "<td>11月</td>"),
    ("<td>Dec</td>", "<td>12月</td>"),
    # Monthly frame toggle button + JS
    (
        'id="annual-monthly-toggle" aria-expanded="false" aria-controls="annual-frame-open">\n          Open\n        </button>',
        'id="annual-monthly-toggle" aria-expanded="false" aria-controls="annual-frame-open">\n          開啟\n        </button>',
    ),
    ("btn.textContent = isOpen ? 'Close' : 'Open';", "btn.textContent = isOpen ? '關閉' : '開啟';"),
    # Daily focus window
    ('aria-label="Daily sales list"', 'aria-label="每日銷售清單"'),
    ('aria-label="Global menu"', 'aria-label="全域選單"'),
    ('aria-label="Display year"', 'aria-label="顯示年份"'),
    ('aria-label="Edit day row"', 'aria-label="編輯日次列"'),
    (">Edit</span>", ">編輯</span>"),
    ('aria-label="Daily rows for year"', 'aria-label="該年每日列"'),
    ('aria-label="Scroll to today"', 'aria-label="捲動至今天"'),
    ('aria-label="Open graph"', 'aria-label="開啟圖表"'),
    ('aria-label="Expand daily table"', 'aria-label="展開每日表格"'),
    (
        "expanded ? 'Collapse daily table' : 'Expand daily table'",
        "expanded ? '收合每日表格' : '展開每日表格'",
    ),
    (
        "initialExpanded ? 'Collapse daily table' : 'Expand daily table'",
        "initialExpanded ? '收合每日表格' : '展開每日表格'",
    ),
    (">Focus row up and down</span>", ">焦點列 上下</span>"),
    (">Toggle</span>", ">切換</span>"),
    # Column headers (longer first)
    (">Monthly Target Sales</span>", ">月次目標銷售</span>"),
    (">Monthly Sales</span>", ">月次銷售</span>"),
    (">Annual Target Sales</span>", ">年度目標銷售</span>"),
    (">Annual Sales</span>", ">年度銷售</span>"),
    (">Today&rsquo;s Sales</span>", ">今日銷售</span>"),
    (
        'annual-daily-hdr__cell--date">Date</span>',
        'annual-daily-hdr__cell--date">日期</span>',
    ),
    (
        'annual-daily-focus-bar-upper__cell--date">Date</span>',
        'annual-daily-focus-bar-upper__cell--date">日期</span>',
    ),
    (
        'annual-daily-hdr__cell">Target Sales</span>',
        'annual-daily-hdr__cell">目標銷售</span>',
    ),
    (
        'annual-daily-focus-bar-upper__cell">Target Sales</span>',
        'annual-daily-focus-bar-upper__cell">目標銷售</span>',
    ),
    (
        'annual-daily-hdr__cell">Difference</span>',
        'annual-daily-hdr__cell">差額</span>',
    ),
    (
        'annual-daily-focus-bar-upper__cell">Difference</span>',
        'annual-daily-focus-bar-upper__cell">差額</span>',
    ),
    (
        'annual-daily-hdr__cell">Achievement</span>',
        'annual-daily-hdr__cell">達成率</span>',
    ),
    (
        'annual-daily-focus-bar-upper__cell">Achievement</span>',
        'annual-daily-focus-bar-upper__cell">達成率</span>',
    ),
    (
        'annual-daily-focus-bar-graph-btn__inner">Today</span>',
        'annual-daily-focus-bar-graph-btn__inner">今天</span>',
    ),
    (
        'annual-daily-focus-bar-graph-btn__inner">Graph</span>',
        'annual-daily-focus-bar-graph-btn__inner">圖表</span>',
    ),
    # Back to cockpit
    ('aria-label="Back to Area1 Cockpit"', 'aria-label="返回 Area1 主控台"'),
    (
        'focus-bar-back-to-cockpit__line">Back</span>',
        'focus-bar-back-to-cockpit__line">返回</span>',
    ),
    (
        'focus-bar-back-to-cockpit__line">to</span>',
        'focus-bar-back-to-cockpit__line">至</span>',
    ),
    (
        'focus-bar-back-to-cockpit__line">Cockpit</span>',
        'focus-bar-back-to-cockpit__line">主控台</span>',
    ),
    # Focus jump (keep Focus Bar product term in label)
    (">▼ Focus Bar</button>", ">▼ Focus Bar</button>"),
    # Graph popover static HTML
    (">Daily Graph</h2>", ">每日圖表</h2>"),
    (">▼ Daily\n            </button>", ">▼ 每日\n            </button>"),
    (
        ">\n              ▼ Daily\n            </button>",
        ">\n              ▼ 每日\n            </button>",
    ),
    (
        'data-graph-mode="daily">Daily</button>',
        'data-graph-mode="daily">每日</button>',
    ),
    (
        'data-graph-mode="monthly">Monthly</button>',
        'data-graph-mode="monthly">月度</button>',
    ),
    (
        'data-graph-mode="annual">Annual</button>',
        'data-graph-mode="annual">年度</button>',
    ),
    (">Date :</span>", ">日期 :</span>"),
    (">Achievement :</span>", ">達成率 :</span>"),
    (">Target Sales :</span>", ">目標銷售 :</span>"),
    (">Actual Sales :</span>", ">實際銷售 :</span>"),
    (">Difference :</span>", ">差額 :</span>"),
]

GRAPH_STR_OLD = """      var isJa = document.documentElement.getAttribute('lang') === 'ja';
      var STR = isJa
        ? {
            titles: { daily: '日次グラフ', monthly: '月次グラフ', annual: '年次グラフ' },
            drop: { daily: '▼ 日次', monthly: '▼ 月次', annual: '▼ 年次' },
            labels: {
              daily: { target: '本日目標売上 :', actual: '本日売上 :' },
              monthly: { target: '月次累計目標売上 :', actual: '月次累計実績売上 :' },
              annual: { target: '年次累計目標売上 :', actual: '年次累計実績売上 :' },
            },
            date: '日付 :',
            ach: '達成率 :',
            diff: '差額 :',
            close: '閉じる',
          }
        : {
            titles: { daily: 'Daily Graph', monthly: 'Monthly Graph', annual: 'Annual Graph' },
            drop: { daily: '▼ Daily', monthly: '▼ Monthly', annual: '▼ Annual' },
            labels: {
              daily: { target: "Today's Target Sales :", actual: "Today's Sales :" },
              monthly: { target: 'Cumulative Target Sales :', actual: 'Cumulative Actual Sales :' },
              annual: { target: 'Cumulative Target Sales :', actual: 'Cumulative Actual Sales :' },
            },
            date: 'Date :',
            ach: 'Achievement :',
            diff: 'Difference :',
            close: 'Close',
          };"""

GRAPH_STR_NEW = """      var _lang = String(document.documentElement.getAttribute('lang') || '').toLowerCase();
      var isJa = _lang === 'ja' || _lang.indexOf('ja') === 0;
      var isZh = _lang.indexOf('zh') === 0;
      var STR = isJa
        ? {
            titles: { daily: '日次グラフ', monthly: '月次グラフ', annual: '年次グラフ' },
            drop: { daily: '▼ 日次', monthly: '▼ 月次', annual: '▼ 年次' },
            labels: {
              daily: { target: '本日目標売上 :', actual: '本日売上 :' },
              monthly: { target: '月次累計目標売上 :', actual: '月次累計実績売上 :' },
              annual: { target: '年次累計目標売上 :', actual: '年次累計実績売上 :' },
            },
            date: '日付 :',
            ach: '達成率 :',
            diff: '差額 :',
            close: '閉じる',
          }
        : isZh
          ? {
              titles: { daily: '每日圖表', monthly: '月度圖表', annual: '年度圖表' },
              drop: { daily: '▼ 每日', monthly: '▼ 月度', annual: '▼ 年度' },
              labels: {
                daily: { target: '今日目標銷售 :', actual: '今日銷售 :' },
                monthly: { target: '月次累計目標銷售 :', actual: '月次累計實際銷售 :' },
                annual: { target: '年度累計目標銷售 :', actual: '年度累計實際銷售 :' },
              },
              date: '日期 :',
              ach: '達成率 :',
              diff: '差額 :',
              close: '關閉',
            }
          : {
              titles: { daily: 'Daily Graph', monthly: 'Monthly Graph', annual: 'Annual Graph' },
              drop: { daily: '▼ Daily', monthly: '▼ Monthly', annual: '▼ Annual' },
              labels: {
                daily: { target: "Today's Target Sales :", actual: "Today's Sales :" },
                monthly: { target: 'Cumulative Target Sales :', actual: 'Cumulative Actual Sales :' },
                annual: { target: 'Cumulative Target Sales :', actual: 'Cumulative Actual Sales :' },
              },
              date: 'Date :',
              ach: 'Achievement :',
              diff: 'Difference :',
              close: 'Close',
            };"""


def main() -> None:
    if not DST.is_file():
        raise SystemExit(f"missing {DST} — run wave1/wave2 first")
    text = DST.read_text(encoding="utf-8")
    missing = []
    for a, b in WAVE3_REPLACEMENTS:
        if a == b:
            continue
        if a not in text:
            missing.append(a[:90])
            continue
        text = text.replace(a, b)

    if GRAPH_STR_OLD not in text:
        if "isZh = _lang.indexOf('zh')" in text or "每日圖表" in text and "var isZh" in text:
            print("graph STR already patched")
        else:
            missing.append("GRAPH_STR_OLD block")
    else:
        text = text.replace(GRAPH_STR_OLD, GRAPH_STR_NEW, 1)

    DST.write_text(text, encoding="utf-8")
    if missing:
        print("WARN missing sources:")
        for m in missing:
            print(" ", repr(m))

    t = DST.read_text(encoding="utf-8")
    must = [
        "營業日",
        "平均銷售額",
        "旺淡期%",
        "月次目標",
        "日次目標",
        "1月",
        "12月",
        "今日銷售",
        "月次目標銷售",
        "焦點列 上下",
        "返回",
        "主控台",
        "每日圖表",
        "實際銷售",
        "展開每日表格",
        "isZh",
    ]
    for s in must:
        if s not in t:
            raise SystemExit(f"missing after wave3: {s}")
    print("wave3 applied:", DST.relative_to(ROOT))
    print("build_zh_tw_annual_wave3: OK")


if __name__ == "__main__":
    main()
