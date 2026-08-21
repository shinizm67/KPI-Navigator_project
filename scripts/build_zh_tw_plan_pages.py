#!/usr/bin/env python3
"""Create zh-tw Plan Details + Change Plan from EN, and wire JA/EN language switchers."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_zh_tw_profile_pages import (  # noqa: E402
    _patch_lang_switcher,
    _strip_export_script,
)

# Longer / more specific phrases first to avoid partial clobbering.
SHARED_REPLACEMENTS = [
    ("<html lang=\"en\">", "<html lang=\"zh-TW\">"),
    ('href="style.css"', 'href="../../en/setting/style.css"'),
    ('href="../plan/style.css"', 'href="../../en/plan/style.css"'),
    ("https://forge-laboratory.com/en", "https://forge-laboratory.com"),
    ("Current workspace", "目前工作區"),
    ("Workspace list", "工作區清單"),
    ("Switch to Office Mode", "切換至 Office Mode"),
    ("Switch to Sci-Fi Mode", "切換至 Sci-Fi Mode"),
    ("Select language", "選擇語言"),
    ("Language options", "語言選項"),
    ("Back to top", "回到頁首"),
]

PLAN_DETAILS_REPLACEMENTS = [
    (
        "Plan Details | KPI Pilot | FORGE LABORATORY",
        "方案詳情 | KPI Pilot | FORGE LABORATORY",
    ),
    (">Plan Details</h2>", ">方案詳情</h2>"),
    ("]</span> Current Plan</h3>", "]</span> 目前方案</h3>"),
    ("<dt>Plan Name</dt>", "<dt>方案名稱</dt>"),
    ("<dt>Status</dt>", "<dt>狀態</dt>"),
    ("<dd>Active</dd>", "<dd>使用中</dd>"),
    ("<dt>Price</dt>", "<dt>價格</dt>"),
    ("$29 / Month", "$29 / 月"),
    ("<dt>Billing Cycle</dt>", "<dt>帳單週期</dt>"),
    ("<dd>Monthly</dd>", "<dd>每月</dd>"),
    ("<dt>Next Billing Date</dt>", "<dt>下次帳單日</dt>"),
    ("March 15th, 2025", "2025年3月15日"),
    ("<dt>Payment Method</dt>", "<dt>付款方式</dt>"),
    ("<dt>Subscription ID</dt>", "<dt>訂閱 ID</dt>"),
    ("<dd>Pro</dd>", "<dd>專業</dd>"),
    ("]</span> Included in Your Plan</h3>", "]</span> 方案包含內容</h3>"),
    ("Advanced KPI Analytics", "進階 KPI 分析"),
    ("Daily / Monthly / Yearly KPI Hub Access", "日次 / 月次 / 年次 KPI 中心存取"),
    ("Multi-Year Data Comparison", "多年資料比較"),
    ("Custom KPI dashboards", "自訂 KPI 儀表板"),
    ("Data Management", "資料管理"),
    ("Unlimited CSV Upload", "CSV 上傳無限制"),
    ("Full Historical Data Retention", "完整歷史資料保留"),
    ("Export to CSV / PDF", "匯出為 CSV / PDF"),
    ("Data Backup &amp; Recovery", "資料備份與復原"),
    ("Financial Insight", "財務洞察"),
    ("P&amp;L (Profit &amp; Loss) Visualization", "P&amp;L（損益）視覺化"),
    ("Cost Ratio Monitoring", "成本比率監控"),
    ("Revenue Gap Action Suggestions", "營收落差行動建議"),
    ("AI Assistance", "AI 協助"),
    ("AI Business Advisory Chat", "AI 商業顧問聊天"),
    ("Seasonal Forecast Suggestions", "季節預測建議"),
    ("Risk Detection Alerts", "風險偵測警示"),
    ("Account &amp; Usage", "帳戶與使用額度"),
    ("Multi-Store Management (up to 3 locations)", "多門市管理（最多 3 個據點）"),
    ("Multi-User Access (up to 5 users)", "多使用者存取（最多 5 位）"),
    ("Priority Support", "優先支援"),
    ("]</span> Usage Limits</h3>", "]</span> 使用上限</h3>"),
    ("<dt>CSV Upload</dt>", "<dt>CSV 上傳</dt>"),
    ("<dd>Unlimited</dd>", "<dd>無限制</dd>"),
    ("<dt>KPI Advisory calls</dt>", "<dt>KPI 顧問使用次數</dt>"),
    ("500 / month", "500 / 月"),
    ("<dt>Stores</dt>", "<dt>門市數</dt>"),
    ("<dt>Users</dt>", "<dt>使用者數</dt>"),
    ("]</span> Billing</h3>", "]</span> 帳單</h3>"),
    (">Manage Billing</a>", ">管理帳單</a>"),
    ("]</span> Manage Subscription</h3>", "]</span> 訂閱管理</h3>"),
    (">Change Plan</a>", ">變更方案</a>"),
    (
        "Switch to Yearly Billing (Save 15%)",
        "改為年繳（省 15%）",
    ),
    ("Update Payment Method", "更新付款方式"),
    ("Cancel Subscription", "取消訂閱"),
    (
        "Cancellation becomes effective at the end of the current billing period. Data is retained for 30 days after cancellation.",
        "取消將於目前帳單週期結束時生效。取消後資料將保留 30 天。",
    ),
    (
        "]</span> Data &amp; Cancellation Policy</h3>",
        "]</span> 資料與取消政策</h3>",
    ),
    (
        "Downgrading to Basic restricts access to P&amp;L and AI modules.",
        "降級至基本方案後，P&amp;L 與 AI 模組的存取將受限制。",
    ),
    (
        "No data is deleted immediately upon downgrade.",
        "降級時不會立即刪除資料。",
    ),
    (
        "Account access remains active until the period ends.",
        "帳戶存取權限會持續至週期結束。",
    ),
    (
        "All data is permanently deleted after 30 days.",
        "所有資料將於 30 天後永久刪除。",
    ),
    ("]</span> Support</h3>", "]</span> 支援</h3>"),
    ("Priority Email Support", "優先電子郵件支援"),
    (
        "Response within 24 hours (Business Days)",
        "24 小時內回覆（營業日）",
    ),
    (">Contact Support &gt;</a>", ">聯絡支援 &gt;</a>"),
]

CHANGE_PLAN_REPLACEMENTS = [
    (
        "Change Plan | KPI Pilot | FORGE LABORATORY",
        "變更方案 | KPI Pilot | FORGE LABORATORY",
    ),
    (">Change Plan</h2>", ">變更方案</h2>"),
    ("]</span> Current Plan</h3>", "]</span> 目前方案</h3>"),
    (
        "Upgrade or downgrade your subscription plan.",
        "可升級或降級您的訂閱方案。",
    ),
    ("]</span> Current Plan Summary</h3>", "]</span> 目前方案摘要</h3>"),
    ("<strong>Current Plan:</strong> Pro", "<strong>目前方案：</strong> 專業"),
    ("<strong>Billing Cycle:</strong> Monthly", "<strong>帳單週期：</strong> 每月"),
    (
        "<strong>Next Billing Date:</strong> March 14, 2025",
        "<strong>下次帳單日：</strong> 2025年3月14日",
    ),
    ("]</span> Available Plans</h3>", "]</span> 可用方案</h3>"),
    (
        'Feature list matches the public <a href="../plan/index.html">Plan</a> page.',
        '功能列表與公開的 <a href="../../en/plan/index.html">方案</a> 頁面相同。',
    ),
    (">List</th>", ">項目</th>"),
    (">Basic $5</th>", ">基本 $5</th>"),
    (">Pro $29</th>", ">專業 $29</th>"),
    ("1. Annual KPI Dashboard", "1. 年度 KPI 儀表板"),
    ("2. Monthly KPI Analysis", "2. 月次 KPI 分析"),
    ("3. Daily Target Tracking", "3. 日次目標追蹤"),
    ("4. Automatic Achievement Calculation", "4. 達成率自動計算"),
    ("5. Seasonality Detection", "5. 季節性偵測"),
    ("6. Business Day Management", "6. 營業日管理"),
    ("7. CSV Data Import (Previous Year)", "7. CSV 資料匯入（前一年）"),
    ("8. Automated Sales Target Engine", "8. 自動銷售目標引擎"),
    ("9. Cost Input (Food &amp; Beverage)", "9. 成本輸入（餐飲）"),
    ("10. Cost Ratio Visualization", "10. 成本比率視覺化"),
    ("11. Profit Structure Visualization", "11. 利潤結構視覺化"),
    ("12. Monthly Profit Analysis Dashboard", "12. 月次利潤分析儀表板"),
    ('aria-label="Included"', 'aria-label="包含"'),
    ('aria-label="Not included"', 'aria-label="不包含"'),
    (">Down Grade Plan</a>", ">降級方案</a>"),
    (
        'role="status" aria-label="Your current plan">Current Plan</span>',
        'role="status" aria-label="您目前的方案">目前方案</span>',
    ),
    ("]</span> Billing Impact Notice</h3>", "]</span> 帳單影響說明</h3>"),
    (
        "<strong>When upgrading:</strong> You get immediate access to new features. A prorated charge may be applied to your payment method today.",
        "<strong>升級時：</strong>可立即使用新功能。可能會於今日依比例向您的付款方式收費。",
    ),
    (
        "<strong>When downgrading:</strong> Changes take effect at the end of your current billing period. No immediate refund for the remaining time on the current plan.",
        "<strong>降級時：</strong>變更於目前帳單週期結束後生效。目前方案剩餘期間不予即時退款。",
    ),
]


def build_zh_tw_from_en(src_name: str, extra: list[tuple[str, str]]) -> Path:
    src = ROOT / "en" / "setting" / src_name
    dst = ROOT / "zh-tw" / "setting" / src_name
    text = _strip_export_script(src.read_text(encoding="utf-8"))
    for a, b in SHARED_REPLACEMENTS + extra:
        text = text.replace(a, b)
    text = text.replace(
        "btnModeToggle.setAttribute('aria-label', isOffice ? 'Switch to Sci-Fi Mode' : 'Switch to Office Mode');",
        "btnModeToggle.setAttribute('aria-label', isOffice ? '切換至 Sci-Fi Mode' : '切換至 Office Mode');",
    )
    text = _patch_lang_switcher(
        text,
        active="zh-tw",
        url_ja=f"../../setting/{src_name}",
        url_en=f"../../en/setting/{src_name}",
        url_zh_tw=src_name,
    )
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text, encoding="utf-8")
    print(f"wrote {dst.relative_to(ROOT)}")
    return dst


def wire_ja_en_lang_switchers() -> None:
    mapping = {
        ("setting/plan_details.html", "ja"): (
            "plan_details.html",
            "../en/setting/plan_details.html",
            "../zh-tw/setting/plan_details.html",
        ),
        ("en/setting/plan_details.html", "en"): (
            "../../setting/plan_details.html",
            "plan_details.html",
            "../../zh-tw/setting/plan_details.html",
        ),
        ("setting/change_plan.html", "ja"): (
            "change_plan.html",
            "../en/setting/change_plan.html",
            "../zh-tw/setting/change_plan.html",
        ),
        ("en/setting/change_plan.html", "en"): (
            "../../setting/change_plan.html",
            "change_plan.html",
            "../../zh-tw/setting/change_plan.html",
        ),
    }
    for (rel, active), (url_ja, url_en, url_zh) in mapping.items():
        path = ROOT / rel
        text = _patch_lang_switcher(
            path.read_text(encoding="utf-8"),
            active=active,
            url_ja=url_ja,
            url_en=url_en,
            url_zh_tw=url_zh,
        )
        path.write_text(text, encoding="utf-8")
        print(f"wired lang switcher: {rel}")


def refresh_chrome_and_export() -> None:
    rc = subprocess.call(
        [sys.executable, str(ROOT / "scripts" / "build_site_chrome.py"), "settings"],
        cwd=str(ROOT / "scripts"),
    )
    if rc != 0:
        raise SystemExit(f"build_site_chrome failed: {rc}")
    from apply_kpi_pl_mep_export import inject_script  # noqa: WPS433

    for rel in (
        "setting/plan_details.html",
        "setting/change_plan.html",
        "en/setting/plan_details.html",
        "en/setting/change_plan.html",
        "zh-tw/setting/plan_details.html",
        "zh-tw/setting/change_plan.html",
    ):
        path = ROOT / rel
        if not path.is_file():
            continue
        path.write_text(inject_script(path.read_text(encoding="utf-8")), encoding="utf-8")
        print(f"export inject: {rel}")


def main() -> None:
    build_zh_tw_from_en("plan_details.html", PLAN_DETAILS_REPLACEMENTS)
    build_zh_tw_from_en("change_plan.html", CHANGE_PLAN_REPLACEMENTS)
    wire_ja_en_lang_switchers()
    refresh_chrome_and_export()
    print("build_zh_tw_plan_pages: OK")


if __name__ == "__main__":
    main()
