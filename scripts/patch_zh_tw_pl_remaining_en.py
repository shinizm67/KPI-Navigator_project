#!/usr/bin/env python3
"""Patch remaining English chrome strings on zh-tw PL (+ profit hub BIZ font)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PL = ROOT / "zh-tw" / "app" / "profit" / "pl" / "index.html"
HUB = ROOT / "zh-tw" / "app" / "profit" / "index.html"

PL_REPLACEMENTS = [
    ('aria-label="FORGE LABORATORY - Top page"', 'aria-label="FORGE LABORATORY - 首頁"'),
    ('aria-label="Main navigation"', 'aria-label="主要導覽"'),
    ('aria-label="Open Daily view"', 'aria-label="開啟每日檢視"'),
    (
        'aria-label="Profit summary (Pro). Basic plan goes to Change Plan"',
        'aria-label="利潤摘要（專業方案）。基本方案請前往變更方案"',
    ),
    ('aria-label="Switch to Office Mode"', 'aria-label="切換至 Office Mode"'),
    (
        'aria-label="Download templates and P&amp;L data"',
        'aria-label="下載範本與收支資料"',
    ),
    ('aria-label="Download menu"', 'aria-label="下載選單"'),
    ('aria-label="Open Expense (coming soon)"', 'aria-label="開啟支出設定（準備中）"'),
    ('aria-label="Toggle Office Mode"', 'aria-label="切換 Office Mode"'),
    (
        'aria-label="Daily sales input path (read-only)"',
        'aria-label="日次銷售輸入路徑（唯讀）"',
    ),
    (
        'data-tooltip="Daily sales input path (read-only). Switch in MEP or Sales Data."',
        'data-tooltip="日次銷售輸入路徑（唯讀）。請在 MEP 或 Sales Data 切換。"',
    ),
    (
        'title="Daily sales input path (read-only). Switch in MEP or Sales Data."',
        'title="日次銷售輸入路徑（唯讀）。請在 MEP 或 Sales Data 切換。"',
    ),
    ('aria-label="Hidden expense lines"', 'aria-label="隱藏的支出科目"'),
    ('aria-label="Toggle analysis section"', 'aria-label="切換分析區塊顯示"'),
    ('aria-label="Back to top"', 'aria-label="回到頁首"'),
    ('aria-label="Compare areas"', 'aria-label="比較區域"'),
    (
        "btnModeToggle.setAttribute('aria-label', isOffice ? 'Switch to Sci-Fi Mode' : 'Switch to Office Mode');",
        "btnModeToggle.setAttribute('aria-label', isOffice ? '切換至 Sci-Fi Mode' : '切換至 Office Mode');",
    ),
    (
        'var plGuideTipShow = "+ Show per-line reference budget (guideline). Median of your past ratios × this month\'s sales flags likely overspending per cell (not a prescribed ideal).";',
        'var plGuideTipShow = "＋ 顯示各科目參考預算（尺規）。以過去比率中位數 × 本月營業額標示可能超支（非強制標準值）。";',
    ),
    (
        'var plGuideTipHide = "− Hide the per-line reference budget (guideline).";',
        'var plGuideTipHide = "− 隱藏各科目參考預算（尺規）。";',
    ),
    (
        'var plGuideTipNoData = "Reference budget appears automatically once you have past sales & expense data (computed from your own store\'s records).";',
        'var plGuideTipNoData = "參考預算會在累積過去的營業額與支出資料後自動顯示（依您店家的實績計算）。";',
    ),
]


def patch_pl() -> None:
    text = PL.read_text(encoding="utf-8")
    n = 0
    for a, b in PL_REPLACEMENTS:
        c = text.count(a)
        if c:
            text = text.replace(a, b)
            n += c
            print(f"  {c}x {a[:60]}...")
    PL.write_text(text, encoding="utf-8")
    print(f"patched PL replacements: {n}")


def patch_hub() -> None:
    text = HUB.read_text(encoding="utf-8")
    text2 = text.replace(
        "family=BIZ+UDP+Gothic:wght@400;500;700&family=Orbitron:wght@400;500;600;700&display=swap",
        "family=BIZ+UDP+Gothic:wght@400;500;700&display=swap",
    )
    text2 = text2.replace(
        ".profit-hub-title {\n      font-family: 'Orbitron', sans-serif;",
        ".profit-hub-title {\n      font-family: 'BIZ UDPGothic', sans-serif;",
    )
    # catch-all for hub body
    if "KPI-PROFIT-HUB-ZH-TW-BIZ" not in text2:
        marker = "  <style id=\"kpi-lang-switcher-locale\">"
        block = """  <style id="kpi-profit-hub-zh-tw-biz">
    /* KPI-PROFIT-HUB-ZH-TW-BIZ */
    html[lang='zh-TW'] body,
    html[lang='zh-TW'] body *:not(script):not(style),
    html[lang^='zh'] body,
    html[lang^='zh'] body *:not(script):not(style) {
      font-family: 'BIZ UDPGothic', 'BIZ UDP Gothic', sans-serif;
    }
  </style>
"""
        if marker in text2:
            text2 = text2.replace(marker, block + marker, 1)
        else:
            text2 = text2.replace("</head>", block + "</head>", 1)
    if text2 != text:
        HUB.write_text(text2, encoding="utf-8")
        print("patched profit hub BIZ font")
    else:
        print("profit hub: no font changes needed")


def verify() -> None:
    pl = PL.read_text(encoding="utf-8")
    leftovers = [
        'aria-label="Open Daily view"',
        'aria-label="Main navigation"',
        'aria-label="Switch to Office Mode"',
        'aria-label="Hidden expense lines"',
        'aria-label="Toggle analysis section"',
        'aria-label="Back to top"',
        "Switch to Sci-Fi Mode",
        "Daily sales input path (read-only)",
        "Show per-line reference budget",
        "Hide the per-line reference budget",
        "Reference budget appears automatically",
    ]
    bad = [s for s in leftovers if s in pl]
    for s in leftovers:
        print(("FAIL" if s in pl else "OK"), s[:50])
    if bad:
        raise SystemExit(1)
    print("verify: ALL OK")


def main() -> None:
    patch_pl()
    patch_hub()
    verify()
    print("patch_zh_tw_pl_remaining_en: OK")


if __name__ == "__main__":
    main()
