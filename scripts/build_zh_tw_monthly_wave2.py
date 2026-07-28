#!/usr/bin/env python3
"""Monthly zh-tw Wave 2: Area1 cockpit (lock/edit, year/date, history, KPI strip)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DST = ROOT / "zh-tw" / "app" / "monthly" / "index.html"

WAVE2_REPLACEMENTS = [
    ("Current workspace", "目前工作區"),
    ("Workspace list", "工作區清單"),
    ('aria-label="Monthly plan controls"', 'aria-label="月度方案控制"'),
    ('aria-label="Change Plan"', 'aria-label="變更方案"'),
    ('aria-label="Edit"', 'aria-label="編輯"'),
    (">LOCKED</span>", ">鎖定</span>"),
    (">EDIT</span>", ">編輯</span>"),
    ("lockLabel.textContent = 'UNLOCKED';", "lockLabel.textContent = '已解鎖';"),
    ("lockLabel.textContent = 'LOCKED';", "lockLabel.textContent = '鎖定';"),
    (
        "lockLink.setAttribute('aria-label', 'プラン状態: アンロック');",
        "lockLink.setAttribute('aria-label', '方案狀態：已解鎖');",
    ),
    # EN pro-path aria (if present)
    (
        "lockLink.setAttribute('aria-label', 'Plan status: unlocked');",
        "lockLink.setAttribute('aria-label', '方案狀態：已解鎖');",
    ),
    # Year / date
    ('aria-label="Previous year"', 'aria-label="上一年"'),
    ('aria-label="Next year"', 'aria-label="下一年"'),
    ('aria-label="Select year"', 'aria-label="選擇年份"'),
    ('aria-label="Previous day"', 'aria-label="前一天"'),
    ('aria-label="Next day"', 'aria-label="後一天"'),
    ('aria-label="Select date"', 'aria-label="選擇日期"'),
    ('aria-label="Move to today"', 'aria-label="移至今天"'),
    (">Today</button>", ">今天</button>"),
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
    (">Monthly Allocation Total</p>", ">月次分配率合計</p>"),
    ("promptLabel: 'Monthly Allocation Total'", "promptLabel: '月次分配率合計'"),
    ('aria-label="Move to Focus Bar"', 'aria-label="移至 Focus Bar"'),
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
        raise SystemExit(f"missing {DST} — run build_zh_tw_monthly_wave1.py first")
    text = DST.read_text(encoding="utf-8")
    missing = []
    for a, b in WAVE2_REPLACEMENTS:
        if a not in text:
            missing.append(a[:80])
            continue
        text = text.replace(a, b)
    # EN pro unlock path uses English aria if present in copied file
    text = text.replace(
        "lockLink.setAttribute('aria-label', 'Plan unlocked');",
        "lockLink.setAttribute('aria-label', '方案狀態：已解鎖');",
    )
    # Common EN pattern from en monthly
    if "lockLabel.textContent = 'UNLOCKED'" in text:
        text = text.replace("lockLabel.textContent = 'UNLOCKED'", "lockLabel.textContent = '已解鎖'")
    DST.write_text(text, encoding="utf-8")
    if missing:
        print("WARN missing:")
        for m in missing:
            print(" ", repr(m))

    t = DST.read_text(encoding="utf-8")
    for s in ["鎖定", "編輯", "今天", "年度營業日數", "年度目標銷售", "紀錄", "月次分配率合計", "累積實際銷售", "已解鎖"]:
        if s not in t:
            raise SystemExit(f"missing: {s}")
    print("wave2 applied:", DST.relative_to(ROOT))
    print("build_zh_tw_monthly_wave2: OK")


if __name__ == "__main__":
    main()
