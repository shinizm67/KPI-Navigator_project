#!/usr/bin/env python3
"""Create zh-tw Delete Account flow from EN, and wire JA/EN language switchers."""

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

PAGES = [
    "delete_account1.html",
    "delete_account2.html",
    "delete_account3.html",
    "delete_account4-1.html",
    "delete_account4-2.html",
    "delete_account5.html",
    "delete_account_accomplished.html",
]

# Longer / more specific phrases first.
DELETE_REPLACEMENTS = [
    ("<html lang=\"en\">", "<html lang=\"zh-TW\">"),
    ('href="style.css"', 'href="../../en/setting/style.css"'),
    ("https://forge-laboratory.com/en", "https://forge-laboratory.com"),
    # Titles
    (
        "Delete Account (Step 4-1) | KPI Pilot | FORGE LABORATORY",
        "刪除帳戶（步驟 4-1） | KPI Pilot | FORGE LABORATORY",
    ),
    (
        "Delete Account (Step 4-2) | KPI Pilot | FORGE LABORATORY",
        "刪除帳戶（步驟 4-2） | KPI Pilot | FORGE LABORATORY",
    ),
    (
        "Delete Account (Step 2) | KPI Pilot | FORGE LABORATORY",
        "刪除帳戶（步驟 2） | KPI Pilot | FORGE LABORATORY",
    ),
    (
        "Delete Account (Step 3) | KPI Pilot | FORGE LABORATORY",
        "刪除帳戶（步驟 3） | KPI Pilot | FORGE LABORATORY",
    ),
    (
        "Delete Account (Step 5) | KPI Pilot | FORGE LABORATORY",
        "刪除帳戶（步驟 5） | KPI Pilot | FORGE LABORATORY",
    ),
    (
        "Delete Account | KPI Pilot | FORGE LABORATORY",
        "刪除帳戶 | KPI Pilot | FORGE LABORATORY",
    ),
    (
        "Account Deleted | KPI Pilot | FORGE LABORATORY",
        "帳戶已刪除 | KPI Pilot | FORGE LABORATORY",
    ),
    # Page headings
    (">DELETE ACCOUNT</h2>", ">刪除帳戶</h2>"),
    (">Delete Account</h2>", ">刪除帳戶</h2>"),
    (">Final Confirmation</h2>", ">最終確認</h2>"),
    (">Account Deleted</h2>", ">帳戶已刪除</h2>"),
    # Shared chrome bits for content area
    ("Current workspace", "目前工作區"),
    ("Workspace list", "工作區清單"),
    ("Switch to Office Mode", "切換至 Office Mode"),
    ("Switch to Sci-Fi Mode", "切換至 Sci-Fi Mode"),
    ("Select language", "選擇語言"),
    ("Language options", "語言選項"),
    ("Back to top", "回到頁首"),
    ('aria-label="Account deletion steps"', 'aria-label="刪除帳戶步驟"'),
    ('aria-label="Subscription options"', 'aria-label="訂閱選項"'),
    ('aria-label="One-time code verification"', 'aria-label="一次性驗證碼"'),
    # Stepper labels (shared across steps)
    ("<li>5. Final Confirmation</li>", "<li>5. 最終確認</li>"),
    ("<li>4. Security Verification</li>", "<li>4. 安全驗證</li>"),
    ("<li>3. Data Retention</li>", "<li>3. 資料保留</li>"),
    ("<li>2. Manage Subscription</li>", "<li>2. 管理訂閱</li>"),
    ("<li>1. Account Status</li>", "<li>1. 帳戶狀態</li>"),
    (
        "alt=\"Step 1 of 5: Account Status, Manage Subscription, Data Retention, Security Verification, Final Confirmation\"",
        "alt=\"第 1 / 5 步：帳戶狀態、管理訂閱、資料保留、安全驗證、最終確認\"",
    ),
    ('alt="Step 2 of 5: Manage Subscription"', 'alt="第 2 / 5 步：管理訂閱"'),
    ('alt="Step 3 of 5: Data Retention"', 'alt="第 3 / 5 步：資料保留"'),
    ('alt="Step 4 of 5: Security Verification"', 'alt="第 4 / 5 步：安全驗證"'),
    ('alt="Step 5 of 5: Final Confirmation"', 'alt="第 5 / 5 步：最終確認"'),
    # Step headings
    (">5. Final Confirmation</h3>", ">5. 最終確認</h3>"),
    (">4. Security Verification</h3>", ">4. 安全驗證</h3>"),
    (">3. Data Retention</h3>", ">3. 資料保留</h3>"),
    (">2. Manage Subscription</h3>", ">2. 管理訂閱</h3>"),
    (">1. Account Status</h3>", ">1. 帳戶狀態</h3>"),
    # Step 1
    (
        "This will deactivate your account. Personal data will be removed. Anonymized data may be retained.",
        "此操作將停用您的帳戶。個人資料將被移除，匿名化資料可能會被保留。",
    ),
    ("<dt>Subscription</dt>", "<dt>訂閱</dt>"),
    ("<dd>Active</dd>", "<dd>使用中</dd>"),
    ("<dt>Plan</dt>", "<dt>方案</dt>"),
    ("<dd>Pro</dd>", "<dd>專業</dd>"),
    ("<dt>Next Billing Date</dt>", "<dt>下次帳單日</dt>"),
    ("March 28, 2025", "2025年3月28日"),
    (
        "Manage Subscription (Stripe) →",
        "管理訂閱（Stripe）→",
    ),
    (
        "Cancel or change billing in Stripe before completing account deletion.",
        "完成刪除帳戶前，請先在 Stripe 取消或變更帳單。",
    ),
    # Step 2
    (
        "Before deleting your account, please review your subscription status.",
        "刪除帳戶前，請先確認您的訂閱狀態。",
    ),
    ("<dt>Current Plan</dt>", "<dt>目前方案</dt>"),
    ("<dd>Pro (Active)</dd>", "<dd>專業（使用中）</dd>"),
    ("<dt>Next Billing</dt>", "<dt>下次帳單</dt>"),
    (">Option A</p>", ">選項 A</p>"),
    (">Option B</p>", ">選項 B</p>"),
    (">Option C</p>", ">選項 C</p>"),
    (">Keep Plan</h4>", ">維持方案</h4>"),
    (">Change Plan</h4>", ">變更方案</h4>"),
    (">Cancel Subscription</h4>", ">取消訂閱</h4>"),
    (">Back to KPI Pilot →</a>", ">返回 KPI Pilot →</a>"),
    (">Manage Plan →</a>", ">管理方案 →</a>"),
    (">Go to Stripe →</a>", ">前往 Stripe →</a>"),
    # Step 3
    (
        "Please review how your data will be handled after account deletion.",
        "請確認帳戶刪除後的資料處理方式。",
    ),
    (">Retention Summary</h4>", ">保留摘要</h4>"),
    (
        "Personal data: deleted with account (email, business profile)",
        "個人資料：隨帳戶刪除（電子郵件、事業資料）",
    ),
    (
        "Financial records: retained in accounting logs",
        "財務紀錄：保留於會計日誌",
    ),
    (
        "KPI logs: retained where required by legal policies",
        "KPI 日誌：依法規或政策必要範圍內保留",
    ),
    (
        "Events and payment records: retained for analytics and support",
        "事件與付款紀錄：保留供分析與支援使用",
    ),
    (">Deleted / Removed</h5>", ">將刪除 / 移除</h5>"),
    (
        "Profile data (email, password, profile, workspace settings)",
        "個人資料（電子郵件、密碼、個人資料、工作區設定）",
    ),
    ("App user settings", "應用程式使用者設定"),
    (
        ">May be retained (anonymized / aggregated)</h5>",
        ">可能保留（匿名化 / 彙總）</h5>",
    ),
    (
        "KPI performance metrics (anonymized)",
        "KPI 績效指標（匿名化）",
    ),
    (
        "System logs for security &amp; fraud prevention",
        "安全與防詐騙用的系統日誌",
    ),
    (
        "Billing records where legally required",
        "法律要求時的帳單紀錄",
    ),
    (">Need a break instead?</p>", ">想先暫停嗎？</p>"),
    (">Cancel subscription only →</a>", ">僅取消訂閱 →</a>"),
    (">Downgrade plan →</a>", ">降級方案 →</a>"),
    (">← Back</a>", ">← 返回</a>"),
    (">CONTINUE →</a>", ">繼續 →</a>"),
    # Step 4
    (
        "To protect your account, please verify your identity before proceeding.",
        "為保護您的帳戶，請先完成身分驗證再繼續。",
    ),
    (
        "Account deletion is not completed yet.",
        "此刻尚未完成帳戶刪除。",
    ),
    (">Enter Password</label>", ">輸入密碼</label>"),
    (">Please enter your password.</p>", ">請輸入密碼。</p>"),
    (">Confirm</button>", ">確認</button>"),
    ('aria-label="Show password"', 'aria-label="顯示密碼"'),
    ('title="Show password"', 'title="顯示密碼"'),
    ("Hide password", "隱藏密碼"),
    ("Show password", "顯示密碼"),
    (
        "We&apos;ve sent a 6-digit code to your email.",
        "我們已將 6 位數驗證碼傳送至您的電子郵件。",
    ),
    (">Code expires in 5 minutes.</p>", ">驗證碼將於 5 分鐘後失效。</p>"),
    (">Resend code (60s)</button>", ">重新傳送驗證碼（60 秒）</button>"),
    (">Please enter the 6-digit code.</p>", ">請輸入 6 位數驗證碼。</p>"),
    ('aria-label="Digit 1"', 'aria-label="第 1 碼"'),
    ('aria-label="Digit 2"', 'aria-label="第 2 碼"'),
    ('aria-label="Digit 3"', 'aria-label="第 3 碼"'),
    ('aria-label="Digit 4"', 'aria-label="第 4 碼"'),
    ('aria-label="Digit 5"', 'aria-label="第 5 碼"'),
    ('aria-label="Digit 6"', 'aria-label="第 6 碼"'),
    ("Resend code (", "重新傳送驗證碼（"),
    ("'+sec+'s)'", "'+sec+' 秒）'"),
    ("'Resend code'", "'重新傳送驗證碼'"),
    # Step 5
    (
        "This action is permanent and cannot be undone.",
        "此操作無法復原，執行後無法復原。",
    ),
    (
        "The following data will be permanently deleted:",
        "以下資料將被永久刪除：",
    ),
    (">All KPI records</li>", ">所有 KPI 紀錄</li>"),
    (">All financial data</li>", ">所有財務資料</li>"),
    (">Workspace settings</li>", ">工作區設定</li>"),
    (">Subscription history</li>", ">訂閱紀錄</li>"),
    (">Cancel</a>", ">取消</a>"),
    (">Delete Account</button>", ">刪除帳戶</button>"),
    (
        "Delete this account permanently?",
        "確定要永久刪除此帳戶嗎？",
    ),
    # Accomplished
    (
        ">Your account has been deleted.</h3>",
        ">您的帳戶已刪除。</h3>",
    ),
    (
        ">Thank you for using KPI Pilot.</p>",
        ">感謝您使用 KPI Pilot。</p>",
    ),
    (
        ">We would appreciate your feedback.</p>",
        ">若方便，請留下您的意見回饋。</p>",
    ),
    (
        ">Why are you leaving? (optional)</legend>",
        ">您為什麼要離開？（選填）</legend>",
    ),
    ("> Too expensive</label>", "> 費用太高</label>"),
    ("> Missing features</label>", "> 缺少需要的功能</label>"),
    ("> Difficult to use</label>", "> 不好用</label>"),
    ("> Switching to another tool</label>", "> 改用其他工具</label>"),
    ("> Other</label>", "> 其他</label>"),
    (
        ">Additional comments (optional)</label>",
        ">其他意見（選填）</label>",
    ),
    (
        'placeholder="Tell us how we can improve."',
        'placeholder="請告訴我們可以如何改進。"',
    ),
    (">Submit Feedback</button>", ">送出回饋</button>"),
    (">Close</a>", ">關閉</a>"),
]


def build_zh_tw_from_en(src_name: str) -> Path:
    src = ROOT / "en" / "setting" / src_name
    dst = ROOT / "zh-tw" / "setting" / src_name
    text = _strip_export_script(src.read_text(encoding="utf-8"))
    for a, b in DELETE_REPLACEMENTS:
        text = text.replace(a, b)
    # Mode toggle (pretty + minified)
    text = text.replace(
        "btnModeToggle.setAttribute('aria-label', isOffice ? 'Switch to Sci-Fi Mode' : 'Switch to Office Mode');",
        "btnModeToggle.setAttribute('aria-label', isOffice ? '切換至 Sci-Fi Mode' : '切換至 Office Mode');",
    )
    text = text.replace(
        "btnModeToggle.setAttribute('aria-label',isOffice?'Switch to Sci-Fi Mode':'Switch to Office Mode');",
        "btnModeToggle.setAttribute('aria-label',isOffice?'切換至 Sci-Fi Mode':'切換至 Office Mode');",
    )
    text = text.replace(
        "btn.setAttribute('aria-label',isPassword?'Hide password':'Show password');"
        "btn.setAttribute('title',isPassword?'Hide password':'Show password');",
        "btn.setAttribute('aria-label',isPassword?'隱藏密碼':'顯示密碼');"
        "btn.setAttribute('title',isPassword?'隱藏密碼':'顯示密碼');",
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
    for name in PAGES:
        mapping = {
            (f"setting/{name}", "ja"): (
                name,
                f"../en/setting/{name}",
                f"../zh-tw/setting/{name}",
            ),
            (f"en/setting/{name}", "en"): (
                f"../../setting/{name}",
                name,
                f"../../zh-tw/setting/{name}",
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

    for name in PAGES:
        for prefix in ("setting", "en/setting", "zh-tw/setting"):
            path = ROOT / prefix / name
            if not path.is_file():
                continue
            path.write_text(inject_script(path.read_text(encoding="utf-8")), encoding="utf-8")
            print(f"export inject: {prefix}/{name}")


def main() -> None:
    for name in PAGES:
        build_zh_tw_from_en(name)
    wire_ja_en_lang_switchers()
    refresh_chrome_and_export()
    # Re-apply step navigation (JA/EN/zh-tw; Sci-Fi & Office share HTML).
    rc = subprocess.call(
        [sys.executable, str(ROOT / "scripts" / "apply_delete_account_nav.py")],
        cwd=str(ROOT),
    )
    if rc != 0:
        raise SystemExit(f"apply_delete_account_nav failed: {rc}")
    print("build_zh_tw_delete_account_pages: OK")


if __name__ == "__main__":
    main()
