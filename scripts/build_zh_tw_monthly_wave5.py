#!/usr/bin/env python3
"""Monthly zh-tw Wave 5: Insight overlay + Daily overlay (chrome, section labels, JS hooks)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DST = ROOT / "zh-tw" / "app" / "monthly" / "index.html"

# Longest-first within insight/daily HTML regions
REGION_REPLACEMENTS = [
    # --- section / block titles ---
    ("Cumulative Target Trend vs Cumulative Actual Trend", "累計目標趨勢 vs 累計實際趨勢"),
    ("Annual Cumulative Trend Compare", "年度累計趨勢比較"),
    ("Historical Same Month &amp;\n                  Day of Week Average", "過去同月・同星期平均"),
    ("Historical Same Month &amp; Day of Week Average", "過去同月・同星期平均"),
    ("Same Month Historical Compare", "過去同月比較"),
    ("Historical Annual Compare", "過去年度比較"),
    ("Last Year Same Month Sales", "去年同月銷售"),
    ("Difference vs Last Year", "與去年差額"),
    ("2 Years Ago Same Month", "兩年前同月"),
    ("3 Years Ago Same Month", "三年前同月"),
    ("2 Years Ago Same Period", "兩年前同期"),
    ("3 Years Ago Same Period", "三年前同期"),
    ("Last Year Same Period Sales", "去年同期銷售"),
    ("Gap vs Last Year", "與去年差距"),
    ("Monthly Expense &amp; Profit", "月度支出與利潤"),
    ("Annual Expense &amp; Profit", "年度支出與利潤"),
    ("Year Expense &amp; Profit", "年度支出與利潤"),
    ("Current Month Expenses", "本月支出"),
    ("Last Year Same Month", "去年同月"),
    ("Last Year Same Period", "去年同期"),
    ("Current Year Expenses", "今年支出"),
    ("Historical Insight Access", "過去洞察存取"),
    ("Best Comparable Year", "最佳可比較年度"),
    ("Weakest Comparable Year", "最弱可比較年度"),
    ("Best Same Month", "最佳同月"),
    ("Worst Same Month", "最弱同月"),
    ("Monthly Sales Summary", "月度銷售摘要"),
    ("Annual Sales Summary", "年度銷售摘要"),
    ("Actual vs Last Year Weekday", "實際 vs 去年同星期"),
    ("Last Year same weekday Sales", "去年同星期銷售"),
    ("Historical Same Weekday", "過去同星期"),
    ("Target vs Actual", "目標 vs 實際"),
    ("Today's Target Sales", "今日目標銷售"),
    ("Today's Insight", "今日洞察"),
    ("Last Year Day of Week Insight", "去年同星期洞察"),
    ("Weekly Insight", "每週洞察"),
    ("Strategy Note", "策略備註"),
    ("User Note", "使用者備註"),
    ("Today (Sales)", "今日（銷售）"),
    ("Cumulative Actual Trend (KGI)", "累計實際趨勢 (KGI)"),
    ("Cumulative Target Trend (KPI)", "累計目標趨勢 (KPI)"),
    ("Current Achievement Rate", "目前達成率"),
    ("Annual Achievement Rate", "年度達成率"),
    ("Cumulative Annual Actual Sales", "年度累計實際銷售"),
    ("Cumulative Annual Target Sales", "年度累計目標銷售"),
    ("Cumulative Target Annual Sales", "年度累計目標銷售"),
    ("Cumulative Annual Sales", "年度累計銷售"),
    ("Cumulative Monthly Target Sales", "月度累計目標銷售"),
    ("Cumulative Monthly Sales", "月度累計銷售"),
    ("Cumulative Target Sales", "累計目標銷售"),
    ("Cumulative Fixed Cost", "累計固定成本"),
    ("Cumulative Variable Cost", "累計變動成本"),
    ("Cumulative Profit", "累計利潤"),
    ("Cumulative Sales", "累計銷售"),
    ("Cumulative Target", "累計目標"),
    ("Cumulative Actual", "累計實際"),
    ("Remaining Amount to Target", "距離目標剩餘金額"),
    ("Remaining Annual Business Days", "年度剩餘營業日"),
    ("Remaining Business Days", "剩餘營業日"),
    ("Remaining Business day", "剩餘營業日"),
    ("Daily Sales Needed to Hit Target", "達成目標所需日銷售"),
    ("Daily Required Sales", "每日所需銷售"),
    ("Required Daily Sales", "每日所需銷售"),
    ("Required Revenue", "所需營收"),
    ("Total Cumulative Total Expenses", "累計支出合計"),
    ("Total Expenses", "支出合計"),
    ("Estimated Profit", "預估利潤"),
    ("Annual Profit Margin", "年度利潤率"),
    ("Annual Target Revision", "年度目標修訂"),
    ("Annual Target Sales", "年度目標銷售"),
    ("Current Progress", "目前進度"),
    ("Current Gap", "目前差距"),
    ("Gap Rate", "差距率"),
    ("YoY Rate", "年增率"),
    ("Margin Change", "利潤率變化"),
    ("Cost Structure", "成本結構"),
    ("Cost Margin", "成本利潤率"),
    ("Cost Rate", "成本率"),
    ("FL Rate", "FL 率"),
    ("Food Cost", "餐點成本"),
    ("Drink Cost", "飲料成本"),
    ("Misc Cost", "雜費成本"),
    ("Variable Cost", "變動成本"),
    ("Fixed Cost", "固定成本"),
    ("Expected Cost", "預計成本"),
    ("Expenses(Optional)", "支出（選填）"),
    ("Sales Status", "銷售狀態"),
    ("Same Day of Week", "同星期"),
    ("Same Weekday", "同星期"),
    ("(Daily Allocation)", "（日次分配）"),
    ("(If available)", "（若有）"),
    ("Historical Avg", "過去平均"),
    ("Day of Week Average", "星期平均"),
    ("This Month", "本月"),
    ("Last Year Month", "去年同月"),
    ("This Year", "今年"),
    ("Last Year", "去年"),
    ("Current Term", "本期"),
    ("Term 2", "第2季"),
    ("Revision Status", "修訂狀態"),
    ("Suggested Adjustment", "建議調整"),
    ("Suggested Target", "建議目標"),
    ("View Reason", "查看原因"),
    ("^ Back to Top", "^ 回到頂端"),
    ("▶ Analyze", "▶ 分析"),
    ("▶ Graph", "▶ 圖表"),
    ("Profit Margin", "利潤率"),
    ("Target Sales", "目標銷售"),
    ("Achievement Rate", "達成率"),
    ("Achievement", "達成率"),
    ("Difference", "差額"),
    ("Variance", "差額"),
    ("Reference", "參考"),
    ("Progress", "進度"),
    ("Comparison", "比較"),
    ("Expenses", "支出"),
    ("Expected", "預計"),
    ("Variable", "變動"),
    ("Fixed", "固定"),
    ("Profit", "利潤"),
    ("Watch", "注意"),
    ("OFF", "公休"),
    # chrome / tabs (after longer phrases)
    ('aria-label="Insight"', 'aria-label="洞察"'),
    ('aria-label="Close"', 'aria-label="關閉"'),
    ('aria-label="Daily section"', 'aria-label="每日區塊"'),
    ('aria-label="Monthly section"', 'aria-label="月度區塊"'),
    ('aria-label="Annual section"', 'aria-label="年度區塊"'),
    ('id="insight-overlay-title">Summary</h2>', 'id="insight-overlay-title">摘要</h2>'),
    ('data-insight-tab="summary">Summary</button>', 'data-insight-tab="summary">摘要</button>'),
    ('data-insight-tab="analyze">Analyze</button>', 'data-insight-tab="analyze">分析</button>'),
    ('data-insight-tab="graph">Graph</button>', 'data-insight-tab="graph">圖表</button>'),
    ('href="#insight-jump-summary-daily">Daily</a>', 'href="#insight-jump-summary-daily">每日</a>'),
    ('href="#insight-jump-summary-monthly">Monthly</a>', 'href="#insight-jump-summary-monthly">月度</a>'),
    ('href="#insight-jump-summary-annual">Annual</a>', 'href="#insight-jump-summary-annual">年度</a>'),
    ('insight-overlay__section-label">Daily</h3>', 'insight-overlay__section-label">每日</h3>'),
    ('insight-overlay__section-label">Monthly</h3>', 'insight-overlay__section-label">月度</h3>'),
    ('insight-overlay__section-label">Annual</h3>', 'insight-overlay__section-label">年度</h3>'),
    # field labels often as <p>…</p> or <dt>
    (">Weather :</", ">天氣 :"),
    (">Store Event :</", ">店內活動 :"),
    (">Area Event :</", ">地區活動 :"),
    (">Social Media :</", ">社群媒體 :"),
    (">Marketing :</", ">行銷 :"),
    (">Promo Conversion :</", ">促銷轉換 :"),
    (">Reservation :</", ">預約 :"),
    (">Weather:</", ">天氣:"),
    (">Store Event:</", ">店內活動:"),
    (">Area Event:</", ">地區活動:"),
    (">Social Media:</", ">社群媒體:"),
    (">Marketing:</", ">行銷:"),
    (">Promo Conversion:</", ">促銷轉換:"),
    (">Reservation:</", ">預約:"),
    (">Weather</", ">天氣</"),
    (">Store Event</", ">店內活動</"),
    (">Area Event</", ">地區活動</"),
    (">Social Media</", ">社群媒體</"),
    (">Marketing</", ">行銷</"),
    (">Promo Conversion</", ">促銷轉換</"),
    (">Reservation</", ">預約</"),
    (">Date</", ">日期</"),
    (">None</", ">無</"),
    (">Fine</", ">晴</"),
    (">Cloudy</", ">多雲</"),
    (">Sales</", ">銷售</"),
    ("Today's Sales :", "今日銷售 :"),
    ("Today's Target Sales :", "今日目標銷售 :"),
    ("Current Year Cumulative :", "今年累計 :"),
    ("Last Year Cumulative :", "去年累計 :"),
    ("Best Historical Year :", "歷史最佳年度 :"),
    ("vs Last Year :", "與去年比 :"),
    ("Current Year Line", "今年線"),
    ("Last Year Line", "去年線"),
    ("Best Historical Year Line", "歷史最佳年度線"),
    ("Difference :", "差額 :"),
    ("Achievement :", "達成率 :"),
]

# Daily overlay extras (also applied in daily region; overlaps OK)
DAILY_EXTRA = [
    ('aria-label="Daily floating window"', 'aria-label="每日浮動視窗"'),
    ('id="daily-overlay-today">Today</button>', 'id="daily-overlay-today">今天</button>'),
    (">Daily</h3>", ">每日</h3>"),
    (">Monthly</h3>", ">月度</h3>"),
    (">Annual</h3>", ">年度</h3>"),
]

JS_PATCHES = [
    (
        "if (todayTitle) todayTitle.textContent = ja ? '本日の考察' : \"Today's Insight\";",
        "if (todayTitle) todayTitle.textContent = ja ? '本日の考察' : zh ? '今日洞察' : \"Today's Insight\";",
    ),
    (
        "if (lyTitle) lyTitle.textContent = ja ? '前年同曜日の考察' : 'Last Year Day of Week Insight';",
        "if (lyTitle) lyTitle.textContent = ja ? '前年同曜日の考察' : zh ? '去年同星期洞察' : 'Last Year Day of Week Insight';",
    ),
    (
        "var weatherDt = ja ? '天気 :' : 'Weather :';",
        "var weatherDt = ja ? '天気 :' : zh ? '天氣 :' : 'Weather :';",
    ),
    (
        "var insightTabTitles = { summary: 'Summary', analyze: 'Analyze', graph: 'Graph' };",
        "var insightTabTitles = zh\n"
        "        ? { summary: '摘要', analyze: '分析', graph: '圖表' }\n"
        "        : ja\n"
        "          ? { summary: 'サマリー', analyze: '分析', graph: 'グラフ' }\n"
        "          : { summary: 'Summary', analyze: 'Analyze', graph: 'Graph' };",
    ),
]


def _apply_list(text: str, pairs: list[tuple[str, str]], missing: list[str], label: str) -> str:
    for a, b in pairs:
        if a not in text:
            missing.append(f"{label}:{a[:70]}")
            continue
        text = text.replace(a, b)
    return text


def main() -> None:
    if not DST.is_file():
        raise SystemExit(f"missing {DST}")
    text = DST.read_text(encoding="utf-8")
    i_insight = text.find('id="insight-overlay"')
    i_daily = text.find('id="daily-overlay"')
    if i_insight < 0 or i_daily < 0:
        raise SystemExit("insight/daily overlay markers missing")
    # daily overlay ends before first large script after it, or </body>
    i_body_end = text.find("</body>", i_daily)
    # Prefer cut at first <script after daily starts that is app logic — keep HTML only
    # Use: from insight start back to opening <div, through daily HTML until next sibling script block after daily close.
    # Simpler: insight HTML = insight..daily, daily HTML = daily..(kpi export or script with insight init)
    marker_after_daily = text.find('id="kpi-pl-mep-export-modal"', i_daily)
    if marker_after_daily < 0:
        marker_after_daily = text.find("<script", i_daily + 500)
    if marker_after_daily < 0:
        marker_after_daily = i_body_end

    head = text[:i_insight]
    # include a bit before id for opening tag — find preceding '<' of the overlay root
    root_start = text.rfind("<div", 0, i_insight)
    if root_start < 0 or root_start < i_insight - 200:
        root_start = i_insight
    head = text[:root_start]
    insight = text[root_start:i_daily]
    daily_root = text.rfind("<div", i_insight, i_daily + 1)
    # i_daily is inside daily opening; find daily root
    daily_root = text.rfind("<div", 0, i_daily)
    # Re-slice properly
    insight = text[root_start:daily_root]
    daily = text[daily_root:marker_after_daily]
    tail = text[marker_after_daily:]

    missing: list[str] = []
    insight = _apply_list(insight, REGION_REPLACEMENTS, missing, "insight")
    daily = _apply_list(daily, REGION_REPLACEMENTS + DAILY_EXTRA, missing, "daily")

    # Ensure zh variable near insight title updates (find ja var in dual-insight block)
    # Patch common `var ja =` patterns used by insight fill
    if "var zh =" not in tail and "var zh =" not in insight:
        # Patch JS in whole file for insight helpers
        pass

    text2 = head + insight + daily + tail

    # Inject zh beside existing `var ja =` in insight dual insight updater if present
    old_ja = "var ja = (document.documentElement.lang || '').indexOf('ja') === 0;"
    # Several variants:
    ja_variants = [
        "var ja = (document.documentElement.lang || '').indexOf('ja') === 0;",
        "var ja = document.documentElement.getAttribute('lang') === 'ja';",
        "var ja = (document.documentElement.getAttribute('lang') || '').indexOf('ja') === 0;",
    ]
    # Broader: in the specific todayTitle block, ensure zh exists
    needle = "if (todayTitle) todayTitle.textContent = ja ? '本日の考察'"
    idx = text2.find(needle)
    if idx > 0:
        # look backward for function start / ja declaration within 800 chars
        window = text2[max(0, idx - 1200) : idx]
        if "var zh" not in window and "zh ?" not in text2[idx : idx + 200]:
            # find nearest ja decl
            for v in ja_variants:
                j = text2.rfind(v, max(0, idx - 2000), idx)
                if j >= 0:
                    insert = (
                        v
                        + "\n        var zh = (document.documentElement.lang || '').indexOf('zh') === 0;"
                    )
                    text2 = text2[:j] + insert + text2[j + len(v) :]
                    break
            else:
                # insert zh just before todayTitle line
                text2 = text2[:idx] + (
                    "var zh = (document.documentElement.lang || '').indexOf('zh') === 0;\n        "
                ) + text2[idx:]

    for a, b in JS_PATCHES:
        if a not in text2:
            missing.append("js:" + a[:70])
        else:
            text2 = text2.replace(a, b, 1)

    # insightTabTitles may need ja/zh in scope — ensure nearby
    tab_idx = text2.find("var insightTabTitles = zh")
    if tab_idx > 0:
        win = text2[max(0, tab_idx - 800) : tab_idx]
        if "var zh" not in win and "zh =" not in win:
            # find ja near titleEl handler
            j = text2.rfind("var ja", max(0, tab_idx - 1500), tab_idx)
            if j < 0:
                text2 = (
                    text2[:tab_idx]
                    + "var _il = String(document.documentElement.getAttribute('lang') || '').toLowerCase();\n"
                    "      var ja = _il.indexOf('ja') === 0;\n"
                    "      var zh = _il.indexOf('zh') === 0;\n      "
                    + text2[tab_idx:]
                )
            else:
                # after ja line insert zh
                line_end = text2.find("\n", j)
                if line_end > 0 and "var zh" not in text2[j:line_end + 80]:
                    text2 = (
                        text2[:line_end]
                        + "\n      var zh = String(document.documentElement.getAttribute('lang') || '').toLowerCase().indexOf('zh') === 0;"
                        + text2[line_end:]
                    )

    DST.write_text(text2, encoding="utf-8")
    if missing:
        # Only warn for insight misses that look critical
        crit = [m for m in missing if m.startswith("js:") or "Sales Summary" in m or "insight-overlay-title" in m]
        print(f"WARN missing {len(missing)} (showing up to 25):")
        for m in missing[:25]:
            print(" ", repr(m))
        if len(missing) > 25:
            print(f"  ... +{len(missing) - 25} more")

    t = DST.read_text(encoding="utf-8")
    must = [
        "摘要",
        "分析",
        "圖表",
        "月度銷售摘要",
        "年度銷售摘要",
        "今日洞察",
        "累計目標趨勢",
        "insightTabTitles = zh",
    ]
    for s in must:
        if s not in t:
            raise SystemExit(f"missing after wave5: {s}")
    print("wave5 applied:", DST.relative_to(ROOT))
    print("build_zh_tw_monthly_wave5: OK")


if __name__ == "__main__":
    main()
