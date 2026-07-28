#!/usr/bin/env python3
"""zh-tw Profit PL Wave 1: scaffold from EN + chrome/toolbar/table chrome i18n.

Full LABELS_ZH in build_pl_table_page.py is a follow-up; this wave gets a
usable zh-tw PL page linked from the profit hub.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_zh_tw_profile_pages import _patch_lang_switcher, _strip_export_script  # noqa: E402

SRC = ROOT / "en" / "app" / "profit" / "pl" / "index.html"
DST = ROOT / "zh-tw" / "app" / "profit" / "pl" / "index.html"

# Visible chrome / toolbar / table shell (longest-first applied)
REPLACEMENTS = [
    ('<html lang="en">', '<html lang="zh-TW">'),
    (
        "Profit &amp; Loss (PL) | KPI Navigator",
        "損益表（PL） | KPI Navigator",
    ),
    (
        "Profit & Loss (PL) | KPI Navigator",
        "損益表（PL） | KPI Navigator",
    ),
    ("https://forge-laboratory.com/en", "https://forge-laboratory.com"),
    # Global nav (EN chrome baked into PL page)
    (">Annual</span>", ">年度</span>"),
    (">Monthly</span>", ">月度</span>"),
    (">Daily</span>", ">每日</span>"),
    (">Insight</span>", ">洞察</span>"),
    ('aria-label="Go to Annual view"', 'aria-label="前往年度檢視"'),
    ('aria-label="Go to Monthly view"', 'aria-label="前往月度檢視"'),
    ('aria-label="Open Daily on Monthly"', 'aria-label="在月度頁開啟每日"'),
    ('aria-label="Open Insight on Monthly"', 'aria-label="在月度頁開啟洞察"'),
    ('aria-label="Basic plan: go to Change Plan"', 'aria-label="基本方案請前往變更方案"'),
    # Toolbar
    (">← Monthly Edit</", ">← 月度編輯</"),
    (">Line items</", ">科目管理</"),
    (">PL Insight</", ">PL 洞察</"),
    (">Download Excel</", ">下載 Excel</"),
    (">Upload Expenses</", ">匯入支出</"),
    (">Undo</", ">復原</"),
    (">Save</", ">儲存</"),
    (">Zoom</", ">縮放</"),
    (">Year</", ">年度</"),
    (">Edit</", ">編輯</"),
    (">Today</", ">今天</"),
    ('aria-label="Back to Monthly Edit page"', 'aria-label="返回月度編輯頁"'),
    ('aria-label="Select fiscal year to display"', 'aria-label="選擇顯示的會計年度"'),
    ('aria-label="Open PL Insight"', 'aria-label="開啟 PL 洞察"'),
    ('aria-label="Download PL table as CSV for Excel"', 'aria-label="下載 PL 表為 Excel 用 CSV"'),
    ('aria-label="Zoom out"', 'aria-label="縮小"'),
    ('aria-label="Zoom in"', 'aria-label="放大"'),
    ('aria-label="Close"', 'aria-label="關閉"'),
    ('aria-label="Previous day"', 'aria-label="前一天"'),
    ('aria-label="Next day"', 'aria-label="後一天"'),
    ('aria-label="Select date"', 'aria-label="選擇日期"'),
    # Table corner / months / head
    (">Profit &amp; Loss</", ">損益表</"),
    (">Profit & Loss</", ">損益表</"),
    (">Business Days</", ">營業日數</"),
    (">January</", ">1月</"),
    (">February</", ">2月</"),
    (">March</", ">3月</"),
    (">April</", ">4月</"),
    (">May</", ">5月</"),
    (">June</", ">6月</"),
    (">July</", ">7月</"),
    (">August</", ">8月</"),
    (">September</", ">9月</"),
    (">October</", ">10月</"),
    (">November</", ">11月</"),
    (">December</", ">12月</"),
    (">Annual total</", ">年度合計</"),
    (">Amount</", ">金額</"),
    (">Ratio</", ">比率</"),
    # Section labels (common)
    (">Income</", ">收入</"),
    (">Store sales</", ">店鋪銷售</"),
    (">Total sales</", ">銷售合計</"),
    (">Fixed</", ">固定費</"),
    (">Variable</", ">變動費</"),
    (">Expenses</", ">支出</"),
    (">Subtotal</", ">小計</"),
    (">Profit ①</", ">利潤①</"),
    (">Profit</", ">利潤</"),
    (">Analysis</", ">分析</"),
    (">Graph</", ">圖表</"),
    (">Attributes</", ">屬性</"),
    # Insight overlay areas
    (">Area 1. Current FL Snapshot</", ">Area 1. 當日 FL 快照</"),
    (">Area 2. Last Year Same Month FL Snapshot</", ">Area 2. 去年同月 FL 快照</"),
    (">Area 3. Year-to-Date FL Snapshot</", ">Area 3. 年初至今 FL 快照</"),
    (">Daily Performance</", ">每日表現</"),
    (">Monthly Performance</", ">月度表現</"),
    (">Expense breakdown</", ">支出明細</"),
    (">Total Expenses</", ">支出合計</"),
    (">This Year</", ">今年</"),
    (">Last Year</", ">去年</"),
    (">Best Year</", ">最佳年度</"),
    (">No Data</", ">無資料</"),
    (">Back to profit hub</", ">返回利潤摘要</"),
    # Modals (high traffic)
    (">Where will you enter amounts for this item?</", ">此科目要在何處輸入金額？</"),
    (">Edit line item</", ">編輯科目</"),
    (">Monthly adjustment</", ">月次調整額</"),
    (">Hide this line?</", ">要隱藏此科目嗎？</"),
    (">Hidden expense lines</", ">已隱藏的支出科目</"),
    (">Confirm</", ">決定</"),
    (">Cancel</", ">取消</"),
    (">Restore</", ">還原</"),
    (">Close</", ">關閉</"),
    (">Hide</", ">隱藏</"),
    (">Delete</", ">刪除</"),
    (">Label</", ">科目名</"),
    (">Daily total</", ">日次合計</"),
    (">Adjustment</", ">調整額</"),
    ("Coming soon", "即將推出"),
]


def ensure_export_target() -> None:
    path = ROOT / "scripts" / "apply_kpi_pl_mep_export.py"
    text = path.read_text(encoding="utf-8")
    line = '    "zh-tw/app/profit/pl/index.html",\n'
    if line in text:
        print("export TARGET already has zh-tw PL")
        return
    anchor = '    "en/app/profit/pl/index.html",\n'
    if anchor not in text:
        raise SystemExit("could not find en PL export target")
    path.write_text(text.replace(anchor, anchor + line, 1), encoding="utf-8")
    print("registered zh-tw PL in export TARGET")


def scaffold() -> None:
    DST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SRC, DST)
    text = _strip_export_script(DST.read_text(encoding="utf-8"))
    # Prefer EN setting stylesheet already used by EN PL (../../../../en/setting/)
    # Fix forge + lang switcher paths for zh-tw tree (same depth as EN).
    missing = []
    # Apply longest first
    pairs = sorted(REPLACEMENTS, key=lambda ab: -len(ab[0]))
    for a, b in pairs:
        if a not in text:
            missing.append(a[:70])
            continue
        text = text.replace(a, b)
    text = _patch_lang_switcher(
        text,
        active="zh-tw",
        url_ja="../../../../app/profit/pl/index.html",
        url_en="../../../../en/app/profit/pl/index.html",
        url_zh_tw="index.html",
    )
    DST.write_text(text, encoding="utf-8")
    print(f"wrote {DST.relative_to(ROOT)} ({DST.stat().st_size} bytes)")
    if missing:
        print(f"WARN missing {len(missing)} (showing 15):")
        for m in missing[:15]:
            print(" ", repr(m))


def wire_ja_en_lang_switchers() -> None:
    mapping = {
        ("app/profit/pl/index.html", "ja"): (
            "index.html",
            "../../../en/app/profit/pl/index.html",
            "../../../zh-tw/app/profit/pl/index.html",
        ),
        ("en/app/profit/pl/index.html", "en"): (
            "../../../../app/profit/pl/index.html",
            "index.html",
            "../../../../zh-tw/app/profit/pl/index.html",
        ),
    }
    for (rel, active), (url_ja, url_en, url_zh) in mapping.items():
        path = ROOT / rel
        if not path.is_file():
            print("skip missing", rel)
            continue
        text = _patch_lang_switcher(
            path.read_text(encoding="utf-8"),
            active=active,
            url_ja=url_ja,
            url_en=url_en,
            url_zh_tw=url_zh,
        )
        path.write_text(text, encoding="utf-8")
        print(f"wired lang switcher: {rel}")


def refresh_export() -> None:
    rc = subprocess.call(
        [sys.executable, str(ROOT / "scripts" / "apply_kpi_pl_mep_export.py")],
        cwd=str(ROOT),
    )
    if rc != 0:
        raise SystemExit(f"apply_kpi_pl_mep_export failed: {rc}")


def verify() -> None:
    t = DST.read_text(encoding="utf-8")
    must = [
        'lang="zh-TW"',
        "損益表（PL）",
        "科目管理",
        "PL 洞察",
        "營業日數",
        "1月",
        "12月",
        "lang-option-zh-tw lang-option-active",
        "KPI-PL-MEP-EXPORT",
    ]
    for s in must:
        if s not in t:
            raise SystemExit(f"missing: {s}")
    # setting links should resolve under zh-tw or en setting
    assert "setting/" in t
    print("verify: ALL OK")


def main() -> None:
    ensure_export_target()
    scaffold()
    wire_ja_en_lang_switchers()
    refresh_export()
    # re-assert lang switcher after export inject
    text = _patch_lang_switcher(
        DST.read_text(encoding="utf-8"),
        active="zh-tw",
        url_ja="../../../../app/profit/pl/index.html",
        url_en="../../../../en/app/profit/pl/index.html",
        url_zh_tw="index.html",
    )
    DST.write_text(text, encoding="utf-8")
    verify()
    print("build_zh_tw_profit_pl_wave1: OK")


if __name__ == "__main__":
    main()
