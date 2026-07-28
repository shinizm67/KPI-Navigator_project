#!/usr/bin/env python3
"""Annual zh-tw Wave 2: Area1 cockpit copy (buttons, year/date, history, KPI strip).

Does not translate Focus Bar / Daily TW table body / modals / Insight (later waves).
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DST = ROOT / "zh-tw" / "app" / "annual" / "index.html"

# Longer / more specific phrases first.
WAVE2_REPLACEMENTS = [
    # Workspace chrome (cockpit area)
    ("Current workspace", "目前工作區"),
    ("Workspace list", "工作區清單"),
    # Access buttons
    (
        "Past Sales — Enter historical daily sales",
        "過去銷售 — 輸入歷史每日銷售",
    ),
    (
        "Historical daily sales only. Current year is not edited here.",
        "僅限歷史每日銷售。今年資料不在此編輯。",
    ),
    (
        "Sales — Enter this year's daily sales",
        "銷售 — 輸入今年的每日銷售",
    ),
    (
        'title="Enter this year\'s daily sales"',
        'title="輸入今年的每日銷售"',
    ),
    (">Past Sales</span>", ">過去銷售</span>"),
    ('aria-label="Annual sales controls"', 'aria-label="年度銷售控制"'),
    # Year / date
    ('aria-label="Previous year"', 'aria-label="上一年"'),
    ('aria-label="Next year"', 'aria-label="下一年"'),
    ('aria-label="Select year"', 'aria-label="選擇年份"'),
    ('aria-label="Previous day"', 'aria-label="前一天"'),
    ('aria-label="Next day"', 'aria-label="後一天"'),
    ('aria-label="Select date"', 'aria-label="選擇日期"'),
    ('aria-label="Move to today"', 'aria-label="移至今天"'),
    (">Today</button>", ">今天</button>"),
    # Core labels
    (">Total Business day</p>", ">年度營業日數</p>"),
    (">Annual Target Sales</p>", ">年度目標銷售</p>"),
    (">History</button>", ">紀錄</button>"),
    ('aria-label="Annual history"', 'aria-label="年度紀錄"'),
    ('aria-label="Annual history records"', 'aria-label="年度紀錄清單"'),
    (">History</h3>", ">紀錄</h3>"),
    (">Close</button>", ">關閉</button>"),
    (">Date/Time</th>", ">日期／時間</th>"),
    (">By</th>", ">操作者</th>"),
    (">Target Sales</th>", ">目標銷售</th>"),
    (">Summary</th>", ">摘要</th>"),
    (">Actions</th>", ">操作</th>"),
    (">Owner</td>", ">擁有者</td>"),
    (
        "Adjusted annual target and monthly seasonal weights.",
        "已調整年度目標銷售與月次旺淡權重。",
    ),
    (
        "Initial yearly setup with default monthly weights.",
        "以預設月次權重完成年度初始設定。",
    ),
    (
        "First imported snapshot from legacy spreadsheet.",
        "已匯入舊試算表的第一份快照。",
    ),
    (">Compare</button>", ">比較</button>"),
    (">Restore</button>", ">還原</button>"),
    # Allocation + table window toggle (still Area1)
    (">Monthly Allocation Total</p>", ">月次分配率合計</p>"),
    ("promptLabel: 'Monthly Allocation Total'", "promptLabel: '月次分配率合計'"),
    (">Annual Table Window</p>", ">年度表格視窗</p>"),
    (
        'aria-label="Open Annual Table Window"',
        'aria-label="開啟年度表格視窗"',
    ),
    (
        "expanded ? 'Close Annual Table Window' : 'Open Annual Table Window'",
        "expanded ? '關閉年度表格視窗' : '開啟年度表格視窗'",
    ),
    (
        ">Open</span>\n            <button\n              type=\"button\"\n              class=\"annual-tw-toggle\"",
        ">開啟</span>\n            <button\n              type=\"button\"\n              class=\"annual-tw-toggle\"",
    ),
    (
        'annual-tw-toggle-label--close">Close</span>',
        'annual-tw-toggle-label--close">關閉</span>',
    ),
    ('aria-label="Move to Focus Bar"', 'aria-label="移至 Focus Bar"'),
    (">▼ Focus Bar</button>", ">▼ Focus Bar</button>"),  # keep product term; label already TW via aria
    # KPI strip — longer first
    (">Cumulative Target Sales</p>", ">累積目標銷售</p>"),
    (">Cumulative Sales</p>", ">累積實際銷售</p>"),
    (
        'annual-kpi-strip-label--cyan">Target Sales</p>',
        'annual-kpi-strip-label--cyan">目標銷售</p>',
    ),
    (
        'annual-kpi-strip-label--cyan">Difference</p>',
        'annual-kpi-strip-label--cyan">差額</p>',
    ),
    (
        'annual-kpi-strip-label--cyan">Achievement</p>',
        'annual-kpi-strip-label--cyan">達成率</p>',
    ),
    (
        'annual-kpi-strip-label--sales">Sales</p>',
        'annual-kpi-strip-label--sales">銷售</p>',
    ),
    # Access Sales button label (after Past Sales / aria already done)
    (
        'monthly-access-btn__label">Sales</span>',
        'monthly-access-btn__label">銷售</span>',
    ),
    # Period row labels in cockpit KPI group
    (
        'annual-kpi-strip-period-label">Daily</span>',
        'annual-kpi-strip-period-label">每日</span>',
    ),
    (
        'annual-kpi-strip-period-label">Monthly</span>',
        'annual-kpi-strip-period-label">月度</span>',
    ),
    (
        'annual-kpi-strip-period-label">Annual</span>',
        'annual-kpi-strip-period-label">年度</span>',
    ),
]


def main() -> None:
    if not DST.is_file():
        raise SystemExit(f"missing {DST} — run build_zh_tw_annual_wave1.py first")
    text = DST.read_text(encoding="utf-8")
    missing = []
    for a, b in WAVE2_REPLACEMENTS:
        if a == b:
            continue
        if a not in text:
            missing.append(a[:80])
            continue
        text = text.replace(a, b)
    DST.write_text(text, encoding="utf-8")
    if missing:
        print("WARN missing sources:")
        for m in missing:
            print(" ", repr(m))

    # Verify key visible strings
    t = DST.read_text(encoding="utf-8")
    must = [
        "過去銷售",
        "銷售",
        "今天",
        "年度營業日數",
        "年度目標銷售",
        "紀錄",
        "月次分配率合計",
        "年度表格視窗",
        "累積實際銷售",
        "累積目標銷售",
        "目標銷售",
        "差額",
        "達成率",
        "開啟年度表格視窗",
        "擁有者",
    ]
    for s in must:
        if s not in t:
            raise SystemExit(f"missing after wave2: {s}")
    # Should still be English (wave 3+)
    leftovers_ok = ["Focus Bar", "▼ Focus Bar"]
    print("wave2 applied:", DST.relative_to(ROOT))
    print("build_zh_tw_annual_wave2: OK")


if __name__ == "__main__":
    main()
