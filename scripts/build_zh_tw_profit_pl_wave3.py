#!/usr/bin/env python3
"""zh-tw Profit PL Wave 3: remaining modal / attribute / chrome English strings.

Wave 1–2 covered toolbar, grid labels, catalog, and expense-detail JS.
This wave localizes leftover static HTML: download menu, account settings,
input-source / attribute / sales-close / adjustment modals.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DST = ROOT / "zh-tw" / "app" / "profit" / "pl" / "index.html"

MARKER = "/* KPI-PL-ZH-TW-WAVE3 */"

# Exact string replacements (longest / most specific first where needed)
STATIC: list[tuple[str, str]] = [
    # —— Download menu ——
    ('class="template-dl-heading">Templates</p>', 'class="template-dl-heading">範本</p>'),
    (
        ">Download Expense Template (Daily)</a>",
        ">下載支出範本（每日）</a>",
    ),
    (
        ">Download Expense Template (Monthly)</a>",
        ">下載支出範本（月次）</a>",
    ),
    ('class="template-dl-heading">Data export</p>', 'class="template-dl-heading">資料匯出</p>'),
    (
        'aria-label="Download MEP and PL workbook as Excel (Pro)">P&L data (MEP + PL)</button>',
        'aria-label="下載 MEP 與 PL 活頁簿為 Excel（專業方案）">損益資料（MEP＋PL）</button>',
    ),
    # —— Account settings chrome ——
    ('aria-label="Open navigation menu"', 'aria-label="開啟導覽選單"'),
    ('aria-label="Account settings"', 'aria-label="帳戶設定"'),
    ('aria-label="Account Settings"', 'aria-label="帳戶設定"'),
    (
        'class="account-settings-popup-title">Account Settings</h3>',
        'class="account-settings-popup-title">帳戶設定</h3>',
    ),
    (
        'class="account-settings-heading">Account</h4>',
        'class="account-settings-heading">帳戶</h4>',
    ),
    (
        'class="account-settings-heading">Subscription</h4>',
        'class="account-settings-heading">訂閱</h4>',
    ),
    (">Profile</a>", ">個人資料</a>"),
    (">Preferences</a>", ">設定</a>"),
    (">Change Email</a>", ">變更電子郵件</a>"),
    (">Change Password</a>", ">變更密碼</a>"),
    (">Session Management</a>", ">工作階段管理</a>"),
    (">Plan Details</a>", ">方案詳情</a>"),
    (">Change Plan</a>", ">變更方案</a>"),
    (">Delete Account</a>", ">刪除帳戶</a>"),
    # —— Sales data close chooser ——
    (
        'class="sales-data-modal__close-chooser-title">Close Sales Data</p>',
        'class="sales-data-modal__close-chooser-title">關閉銷售資料</p>',
    ),
    (
        'class="sales-data-modal__close-chooser-msg">Choose whether to save your changes before closing.</p>',
        'class="sales-data-modal__close-chooser-msg">關閉前請選擇是否儲存變更。</p>',
    ),
    (
        "id=\"sales-data-close-save\">\n          Save and close\n        </button>",
        "id=\"sales-data-close-save\">\n          儲存並關閉\n        </button>",
    ),
    (
        "id=\"sales-data-close-discard\">\n          Close without saving\n        </button>",
        "id=\"sales-data-close-discard\">\n          不儲存關閉\n        </button>",
    ),
    (
        "id=\"sales-data-close-cancel\">\n          Cancel\n        </button>",
        "id=\"sales-data-close-cancel\">\n          取消\n        </button>",
    ),
    # —— Input source / label-edit source ——
    (
        'class="pl-input-source-modal__legend">Where to enter amounts</legend>',
        'class="pl-input-source-modal__legend">金額輸入位置</legend>',
    ),
    (
        "<span>Monthly Edit Page（日次輸入）</span>",
        "<span>月度編輯頁（每日輸入）</span>",
    ),
    (
        "<span>Monthly Edit Page (daily entries)</span>",
        "<span>月度編輯頁（每日輸入）</span>",
    ),
    (
        "<span>Profit & Loss table (monthly)</span>",
        "<span>損益表（月次輸入）</span>",
    ),
    (
        "<span>Profit &amp; Loss table (monthly)</span>",
        "<span>損益表（月次輸入）</span>",
    ),
    # —— Adjustment modal ——
    (
        'class="pl-expense-adj-modal__hint">Adjust gaps vs invoice totals. Daily entries are kept.</p>',
        'class="pl-expense-adj-modal__hint">調整與發票總額的差額。每日輸入不會消失。</p>',
    ),
    (
        'class="pl-expense-adj-modal__label">PL amount</span>',
        'class="pl-expense-adj-modal__label">PL 顯示額</span>',
    ),
    (
        'class="pl-expense-adj-modal__label">Daily total</span>',
        'class="pl-expense-adj-modal__label">每日合計</span>',
    ),
    (
        'class="pl-expense-adj-modal__label">Adjustment</span>',
        'class="pl-expense-adj-modal__label">調整額</span>',
    ),
    (
        'id="pl-expense-adj-modal-title">Monthly adjustment</h2>',
        'id="pl-expense-adj-modal-title">月次調整額</h2>',
    ),
    # —— Attribute modal titles / legends ——
    (
        'id="pl-expense-attribute-modal-title">Select an expense attribute for this line</h2>',
        'id="pl-expense-attribute-modal-title">請選擇此科目的屬性</h2>',
    ),
    (
        'class="pl-input-source-modal__legend">Select an expense attribute for this line</legend>',
        'class="pl-input-source-modal__legend">請選擇此科目的屬性</legend>',
    ),
    (
        'class="pl-input-source-modal__legend">Select a variable expense attribute for this line</legend>',
        'class="pl-input-source-modal__legend">請選擇此變動費科目的屬性</legend>',
    ),
    # —— Global nav (align with zh-tw monthly) ——
    (
        '<span class="btn-mode-text nav-btn-text">Expense</span>',
        '<span class="btn-mode-text nav-btn-text">支出</span>',
    ),
    # —— leftover aria / tooltip ——
    (
        'aria-label="Edit label (double-click or F2)"',
        'aria-label="編輯科目名稱（雙擊或 F2）"',
    ),
    (
        'var labelEditAria = "Edit label (double-click or F2)";',
        'var labelEditAria = "編輯科目名稱（雙擊或 F2）";',
    ),
    (
        'var editAria = "Edit label (double-click or F2)";',
        'var editAria = "編輯科目名稱（雙擊或 F2）";',
    ),
]

# Attribute radio visible labels (value → zh-TW)
ATTR_LABELS: dict[str, str] = {
    "occupancy": "店面物件費",
    "property_tax": "資產稅",
    "salaries_wages": "薪資／工資",
    "lease": "租賃費",
    "depreciation": "折舊費用",
    "insurance": "保險費",
    "labor_related": "人事相關費用",
    "food_cost": "餐點進貨成本",
    "drink_cost": "飲料進貨成本",
    "supplies": "備品／消耗品",
    "miscellaneous": "雜費",
    "utilities": "水電瓦斯費",
    "variable_labor": "工讀／臨時人事費用",
    "communication": "通訊費",
    "advertising": "廣告宣傳費",
    "uniforms": "制服／工作服",
    "payment_fees": "信用卡手續費",
    "taxes": "稅金",
    "subscription": "訂閱費",
}


def patch_attr_spans(text: str) -> str:
    for value, zh in ATTR_LABELS.items():
        pat = re.compile(
            rf'(name="pl-expense-attribute" value="{re.escape(value)}"><span>)([^<]+)(</span>)'
        )
        text, n = pat.subn(rf"\g<1>{zh}\g<3>", text)
        if n == 0:
            # some pages may omit optional attrs
            print(f"WARN no attribute span for {value}")
    return text


def verify(text: str) -> None:
    checks = [
        ("wave3 marker", MARKER in text),
        ("範本 heading", ">範本<" in text),
        ("下載支出範本（每日）", "下載支出範本（每日）" in text),
        ("帳戶設定 title", ">帳戶設定<" in text),
        ("個人資料 menu", ">個人資料<" in text),
        ("關閉銷售資料", "關閉銷售資料" in text),
        ("儲存並關閉", "儲存並關閉" in text),
        ("金額輸入位置", "金額輸入位置" in text),
        ("月度編輯頁（每日輸入）", "月度編輯頁（每日輸入）" in text),
        ("發票 hint", "調整與發票總額的差額" in text),
        ("PL 顯示額", "PL 顯示額" in text),
        ("attr Occupancy→店面物件費", ">店面物件費<" in text),
        ("attr Food→餐點進貨成本", ">餐點進貨成本<" in text),
        ("attr Advertising→廣告宣傳費", ">廣告宣傳費<" in text),
        ("no Templates EN", ">Templates<" not in text),
        ("no Close Sales Data EN", ">Close Sales Data<" not in text),
        ("no Food Cost EN attr", 'value="food_cost"><span>Food Cost</span>' not in text),
        ("no Advertising EN attr", 'value="advertising"><span>Advertising</span>' not in text),
        ("nav 支出", 'nav-btn-text">支出</span>' in text),
        ("no nav Expense EN", 'nav-btn-text">Expense</span>' not in text),
    ]
    for name, ok in checks:
        print(("OK" if ok else "FAIL"), name)
        if not ok:
            raise SystemExit(1)
    print("verify: ALL OK")


def main() -> None:
    if not DST.is_file():
        raise SystemExit(f"missing {DST}")
    text = DST.read_text(encoding="utf-8")

    if MARKER not in text:
        # Insert marker near wave2 marker if present, else at top of first script after DOCTYPE comment
        if "KPI-PL-ZH-TW-WAVE2" in text:
            text = text.replace(
                "/* KPI-PL-ZH-TW-WAVE2 */",
                "/* KPI-PL-ZH-TW-WAVE2 */\n      " + MARKER,
                1,
            )
        else:
            text = text.replace("<head>", f"<head>\n  <!-- {MARKER} -->", 1)

    for a, b in STATIC:
        if a not in text:
            if b in text:
                print("skip (already):", repr(a[:60]))
                continue
            print("WARN missing:", repr(a[:90]))
            continue
        text = text.replace(a, b)

    text = patch_attr_spans(text)

    DST.write_text(text, encoding="utf-8")
    verify(DST.read_text(encoding="utf-8"))
    print("build_zh_tw_profit_pl_wave3: OK")


if __name__ == "__main__":
    main()
