#!/usr/bin/env python3
"""Monthly zh-tw Wave 3: annual-style table/Focus Bar, Monthly Table Window, graph popover."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DST = ROOT / "zh-tw" / "app" / "monthly" / "index.html"

WAVE3_REPLACEMENTS = [
    # --- Shared with Annual Wave 3 (monthly summary table + Daily TW + graph shell) ---
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
    (
        'id="annual-monthly-toggle" aria-expanded="false" aria-controls="annual-frame-open">\n          Open\n        </button>',
        'id="annual-monthly-toggle" aria-expanded="false" aria-controls="annual-frame-open">\n          開啟\n        </button>',
    ),
    ("btn.textContent = isOpen ? 'Close' : 'Open';", "btn.textContent = isOpen ? '關閉' : '開啟';"),
    ('aria-label="Daily sales list"', 'aria-label="每日銷售清單"'),
    ('aria-label="Global menu"', 'aria-label="全域選單"'),
    ('aria-label="Display year"', 'aria-label="顯示年份"'),
    ('aria-label="Edit day row"', 'aria-label="編輯日次列"'),
    (
        'class="annual-daily-focus-edit-btn" id="annual-daily-focus-edit-btn" aria-label="編輯日次列">\n              <img src="../../../images/button.svg" alt="" decoding="async">\n              <span>Edit</span>',
        'class="annual-daily-focus-edit-btn" id="annual-daily-focus-edit-btn" aria-label="編輯日次列">\n              <img src="../../../images/button.svg" alt="" decoding="async">\n              <span>編輯</span>',
    ),
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
    ('aria-label="Back to Area1 Cockpit"', 'aria-label="返回 Area1 主控台"'),
    (
        'focus-bar-back-to-cockpit__line">Back to</span>',
        'focus-bar-back-to-cockpit__line">返回</span>',
    ),
    (
        'focus-bar-back-to-cockpit__line">Cockpit</span>',
        'focus-bar-back-to-cockpit__line">主控台</span>',
    ),
    (">Daily Graph</h2>", ">每日圖表</h2>"),
    (
        ">\n              ▼ Daily\n            </button>",
        ">\n              ▼ 每日\n            </button>",
    ),
    (
        'id="annual-graph-popover-close" aria-label="Close"',
        'id="annual-graph-popover-close" aria-label="關閉"',
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
    # JA-sourced wing aria (monthly scaffold often copies JA)
    (
        "expanded ? '日次テーブルを縮小' : '日次テーブルを展開'",
        "expanded ? '收合每日表格' : '展開每日表格'",
    ),
    (
        "initialExpanded ? '日次テーブルを縮小' : '日次テーブルを展開'",
        "initialExpanded ? '收合每日表格' : '展開每日表格'",
    ),
    (
        "expanded ? 'Collapse daily table' : 'Expand daily table'",
        "expanded ? '收合每日表格' : '展開每日表格'",
    ),
    (
        "initialExpanded ? 'Collapse daily table' : 'Expand daily table'",
        "initialExpanded ? '收合每日表格' : '展開每日表格'",
    ),
    # --- Monthly Table Window (unique to Monthly) ---
    ('aria-label="Monthly Table Window"', 'aria-label="月度表格視窗"'),
    ('aria-label="Previous month"', 'aria-label="上個月"'),
    ('aria-label="Next month"', 'aria-label="下個月"'),
    ('aria-label="Select month"', 'aria-label="選擇月份"'),
    ('aria-label="Months"', 'aria-label="月份清單"'),
    (
        'aria-controls="monthly-month-menu"\n            >January</button>',
        'aria-controls="monthly-month-menu"\n            >1月</button>',
    ),
    (
        'monthly-table-window__vlabel-inner">Income</span>',
        'monthly-table-window__vlabel-inner">收入</span>',
    ),
    (
        'monthly-table-window__vlabel-inner">Customer</span>',
        'monthly-table-window__vlabel-inner">來客數</span>',
    ),
    (
        'monthly-table-window__vlabel-inner">Expenses</span>',
        'monthly-table-window__vlabel-inner">支出</span>',
    ),
    (
        'aria-label="Date and three daily-cell groups (horizontal scroll)"',
        'aria-label="日期與三組日次儲存格（橫向捲動）"',
    ),
    (
        'monthly-table-window__col-text--date">Date</p>',
        'monthly-table-window__col-text--date">日期</p>',
    ),
    ('aria-label="Daily metric labels"', 'aria-label="日次指標標籤"'),
    (
        'monthly-table-window__metric-line">Sales</p>',
        'monthly-table-window__metric-line">銷售</p>',
    ),
    (
        'monthly-table-window__metric-line">Lunch</p>',
        'monthly-table-window__metric-line">午餐</p>',
    ),
    (
        'monthly-table-window__metric-line">Dinner</p>',
        'monthly-table-window__metric-line">晚餐</p>',
    ),
    (
        'monthly-table-window__metric-line">Target Sales</p>',
        'monthly-table-window__metric-line">目標銷售</p>',
    ),
    (
        'monthly-table-window__metric-line">Difference</p>',
        'monthly-table-window__metric-line">差額</p>',
    ),
    (
        'monthly-table-window__metric-line">Achievement</p>',
        'monthly-table-window__metric-line">達成率</p>',
    ),
    (
        'monthly-table-window__metric-line">Customer</p>',
        'monthly-table-window__metric-line">來客數</p>',
    ),
    (
        'monthly-table-window__metric-line">P/C</p>',
        'monthly-table-window__metric-line">組數</p>',
    ),
    (
        'monthly-table-window__metric-line">Food</p>',
        'monthly-table-window__metric-line">餐點</p>',
    ),
    (
        'monthly-table-window__metric-line">Beverage</p>',
        'monthly-table-window__metric-line">飲料</p>',
    ),
    (
        'monthly-table-window__metric-line">Misc</p>',
        'monthly-table-window__metric-line">雜費</p>',
    ),
    (
        'monthly-table-window__metric-line">Fixed</p>',
        'monthly-table-window__metric-line">確定支出</p>',
    ),
    (
        'monthly-table-window__metric-line">Expected</p>',
        'monthly-table-window__metric-line">預計支出</p>',
    ),
    (
        'monthly-table-window__metric-line">Total</p>',
        'monthly-table-window__metric-line">合計</p>',
    ),
    (
        'monthly-table-window__col-text--profit">Profit</p>',
        'monthly-table-window__col-text--profit">利潤</p>',
    ),
    ('aria-label="Focus Bar controls"', 'aria-label="Focus Bar 操作"'),
    (
        'id="monthly-vfocus-edit" aria-label="編輯">Edit</button>',
        'id="monthly-vfocus-edit" aria-label="編輯">編輯</button>',
    ),
    ('aria-label="Go to today’s column"', 'aria-label="移至今天欄位"'),
    (
        'monthly-vfocus-graph-btn__inner">Today</span>',
        'monthly-vfocus-graph-btn__inner">今天</span>',
    ),
    (
        'monthly-vfocus-graph-btn__inner">Graph</span>',
        'monthly-vfocus-graph-btn__inner">圖表</span>',
    ),
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

MONTH_PICKER_LANG_OLD = """      var useJa =
        String(document.documentElement.getAttribute('lang') || '')
          .toLowerCase()
          .indexOf('ja') === 0;
      var MONTHS_JA = [
        '1月', '2月', '3月', '4月', '5月', '6月',
        '7月', '8月', '9月', '10月', '11月', '12月'
      ];
      var MONTHS_EN = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
      ];
      var months = useJa ? MONTHS_JA : MONTHS_EN;"""

MONTH_PICKER_LANG_NEW = """      var _monthLang = String(document.documentElement.getAttribute('lang') || '').toLowerCase();
      var useJa = _monthLang.indexOf('ja') === 0 || _monthLang.indexOf('zh') === 0;
      var MONTHS_JA = [
        '1月', '2月', '3月', '4月', '5月', '6月',
        '7月', '8月', '9月', '10月', '11月', '12月'
      ];
      var MONTHS_EN = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
      ];
      var months = useJa ? MONTHS_JA : MONTHS_EN;"""


def main() -> None:
    if not DST.is_file():
        raise SystemExit(f"missing {DST} — run wave1/wave2 first")
    text = DST.read_text(encoding="utf-8")
    missing = []
    for a, b in WAVE3_REPLACEMENTS:
        if a == b:
            continue
        if a not in text:
            missing.append(a[:100])
            continue
        text = text.replace(a, b)

    if GRAPH_STR_OLD not in text:
        if "isZh = _lang.indexOf('zh')" in text and "每日圖表" in text:
            print("graph STR already patched")
        else:
            missing.append("GRAPH_STR_OLD block")
    else:
        text = text.replace(GRAPH_STR_OLD, GRAPH_STR_NEW, 1)

    if MONTH_PICKER_LANG_OLD not in text:
        if "_monthLang" in text and "indexOf('zh')" in text:
            print("month picker lang already patched")
        else:
            missing.append("MONTH_PICKER_LANG_OLD block")
    else:
        text = text.replace(MONTH_PICKER_LANG_OLD, MONTH_PICKER_LANG_NEW, 1)

    # Fallback: plain Edit span if path-specific replace missed
    text = text.replace(
        '<span>Edit</span>\n            </button>\n            <div class="annual-daily-focus-global-scroll"',
        '<span>編輯</span>\n            </button>\n            <div class="annual-daily-focus-global-scroll"',
    )

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
        "收入",
        "來客數",
        "支出",
        "利潤",
        "餐點",
        "確定支出",
        "isZh",
        "_monthLang",
    ]
    for s in must:
        if s not in t:
            raise SystemExit(f"missing after wave3: {s}")
    print("wave3 applied:", DST.relative_to(ROOT))
    print("build_zh_tw_monthly_wave3: OK")


if __name__ == "__main__":
    main()
