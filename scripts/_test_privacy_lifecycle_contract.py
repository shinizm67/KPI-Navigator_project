# -*- coding: utf-8 -*-
"""BR-LAUNCH-09 Lifecycle L4 — Privacy Policy lifecycle wording (L1-approved) in JP / EN / ZH-TW, dated like KPI_PRIVACY_VERSION."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAILED = 0
PASSED = 0
MONTHS = {m: i for i, m in enumerate(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}


def check(name: str, cond: bool, detail: str = "") -> None:
    global FAILED, PASSED
    if cond:
        PASSED += 1
        print(f"PASS  {name}")
    else:
        FAILED += 1
        print(f"FAIL  {name}" + (f" — {detail}" if detail else ""))


PAGES = {
    "legal/privacy/index.html": [
        "<strong>退会履歴</strong>", "メールアドレスそのものは保存しません", "<strong>削除日から3年間</strong>", "自動的に消去します",
        "法令上の保存期間ではなく", "本文・送信日時・種別", "ユーザーID、ログイン用メールアドレス、連絡先メールアドレス、ブラウザ情報、プラン、送信元ページを削除",
        "自動的に削除されません", "同意記録などは削除します", "退会履歴の消去を希望される場合", "過去のデータを復元することはありません",
        "退会履歴を用いた事業運営のための統計分析"],
    "en/legal/privacy/index.html": [
        "<strong>Account deletion record:</strong>", "We do not store the email address itself",
        "<strong>for 3 years from the deletion date</strong>", "erased automatically", "This is not a statutory retention period",
        "the message text, the date and time it was sent, and its category",
        "remove the user ID, login email address, contact email address, browser information, plan and the page it was sent from",
        "are not deleted automatically", "consent records and related data", "erased after your account has been deleted",
        "past data is never restored", "statistical analysis for running the business using account deletion records"],
    "zh-tw/legal/privacy/index.html": [
        "<strong>帳戶刪除紀錄：</strong>", "我們不會儲存電子信箱本身", "<strong>自刪除日起保存 3 年</strong>", "將自動清除",
        "此期間並非法定保存期間", "內文、送出日期時間及類別", "刪除使用者 ID、登入用電子信箱、聯絡用電子信箱、瀏覽器資訊、方案及送出頁面",
        "不會因本服務之帳戶刪除處理而自動刪除", "同意紀錄等", "如希望清除帳戶刪除紀錄", "不會還原過去的資料",
        "使用帳戶刪除紀錄進行經營本服務所需之統計分析"],
}
FORBIDDEN = ["Stripe ID", "stripe_customer", "HMAC", "SHA-256"]


def page_date(t: str) -> str | None:
    m = re.search(r'class="terms-meta">(?:最終更新日|最後更新)：(\d{4})年(\d{1,2})月(\d{1,2})日', t)
    if m:
        return "%s-%02d-%02d" % (m.group(1), int(m.group(2)), int(m.group(3)))
    m = re.search(r'class="terms-meta">Last updated: (\d{1,2}) ([A-Z][a-z]{2}) (\d{4})', t)
    return "%s-%02d-%02d" % (m.group(3), MONTHS[m.group(2)], int(m.group(1))) if m else None


def main() -> int:
    pv = re.search(r"const KPI_PRIVACY_VERSION = '([^']+)';", (ROOT / "api/v1/_registration.php").read_text(encoding="utf-8"))
    check("KPI_PRIVACY_VERSION moved past 2026-02-16", pv is not None and pv.group(1) > "2026-02-16", pv and pv.group(1))
    for rel, needles in PAGES.items():
        t = (ROOT / rel).read_text(encoding="utf-8")
        check(f"{rel}: Last updated == KPI_PRIVACY_VERSION", pv is not None and page_date(t) == pv.group(1), page_date(t))
        for n in needles:
            check(f"{rel}: has {n[:40]}", t.count(n) == 1, str(t.count(n)))
        check(f"{rel}: no implementation terms", not [f for f in FORBIDDEN if f in t])
    for rel in ("setting/delete_account3.html", "en/setting/delete_account3.html", "zh-tw/setting/delete_account3.html"):
        t = (ROOT / rel).read_text(encoding="utf-8")
        check(f"{rel}: STEP 2 mentions the 3-year deletion record", ("3年" in t) or ("3 years" in t) or ("3 年" in t))
    print(f"\n{PASSED} passed, {FAILED} failed")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
