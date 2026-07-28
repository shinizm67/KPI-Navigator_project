#!/usr/bin/env python3
"""zh-tw P2 leftover English: Insight aria + annual t(ja,en) + monthly alerts."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MONTHLY = ROOT / "zh-tw" / "app" / "monthly" / "index.html"
ANNUAL = ROOT / "zh-tw" / "app" / "annual" / "index.html"

ARIA = [
    ("This month vs historical average", "本月與歷史平均比較"),
    ("This year vs historical average", "本年與歷史平均比較"),
    ("This year sales vs historical average", "本年銷售與歷史平均比較"),
    ("Annual target revision", "年度目標修訂"),
    ("Daily sales status", "每日銷售狀態"),
    ("Today vs same weekday last year insight", "今日與去年同星期洞察"),
    ("Weekly insight", "週次洞察"),
    ("Week date", "週日期"),
    ("Monthly sales summary", "月次銷售摘要"),
    ("Same month historical compare", "同月歷史比較"),
    ("Monthly expense and profit", "月次支出與利益"),
    ("View reason for best same month", "查看最佳同月理由"),
    ("View reason for worst same month", "查看最差同月理由"),
    ("Annual sales summary", "年次銷售摘要"),
    ("Current progress", "累積進度"),
    ("Historical annual compare", "年度歷史比較"),
    ("Annual expense and profit", "年度支出與利益"),
    ("Year expense and profit charts", "年度支出與利益圖表"),
    ("View reason for best comparable year", "查看最佳可比年度理由"),
    ("View reason for weakest comparable year", "查看最弱可比年度理由"),
    ("Daily graph comparisons", "每日圖表比較"),
    ("Monthly graph comparisons", "月次圖表比較"),
    ("Cumulative target vs actual trend", "累計目標與累計實績走勢"),
    ("Annual graph compare", "年度圖表比較"),
    ("Annual cumulative trend compare", "年度累計走勢比較"),
    ("Monthly seasonality analysis", "月次旺淡分析"),
    ("Monthly seasonality chart", "月次旺淡圖表"),
    ("Sales summary", "銷售摘要"),
    ("Monthly target sales allocation", "月次目標銷售配分"),
    ("Baseline year selection", "基準年選擇"),
]

STATIC = [
    (
        "Uncheck years with abnormal sales (closures, renovations, etc.). Select at least one year.",
        "請取消勾選異常銷售的年份（休業、裝修等）。請至少選擇一年。",
    ),
    ('aria-label="UNDO"', 'aria-label="復原"'),
    (">UNDO</", ">復原</"),
    (
        "請在 Sales Data 的 Analyze 編輯",
        "請在銷售資料的「分析」編輯",
    ),
    (
        "會影響 Analyze 與旺淡",
        "會影響「分析」與旺淡",
    ),
]

T_OLD = """        function t(ja, en) {
          return isJa() ? ja : en;
        }"""

T_NEW = """        function t(ja, en, zh) {
          var lang = String(document.documentElement.getAttribute('lang') || '')
            .toLowerCase();
          if (lang.indexOf('ja') === 0) return ja;
          if (lang.indexOf('zh') === 0) return zh != null && zh !== '' ? zh : ja;
          return en;
        }"""

MONTHLY_JS = [
    (
        "lockLink.setAttribute('aria-label', 'Plan status: Unlocked');",
        "lockLink.setAttribute('aria-label', '方案狀態：已解鎖');",
    ),
    (
        "lockLink.setAttribute('aria-label', 'Change Plan');",
        "lockLink.setAttribute('aria-label', '變更方案');",
    ),
    (
        """        function leaseConflictMessage(holder) {
          var label = (holder && holder.label) || (isJa() ? '別タブ' : 'another tab');
          return isJa()
            ? '「' + label + '」が別タブで編集中です。閲覧のみ可能です。'
            : '"' + label + '" is being edited in another tab. This view is read-only.';
        }""",
        """        function leaseConflictMessage(holder) {
          var lang = String(document.documentElement.getAttribute('lang') || '').toLowerCase();
          var isZh = lang.indexOf('zh') === 0;
          var label = (holder && holder.label) || (isJa() ? '別タブ' : isZh ? '其他分頁' : 'another tab');
          if (isJa()) return '「' + label + '」が別タブで編集中です。閲覧のみ可能です。';
          if (isZh) return '「' + label + '」正在其他分頁編輯中。此畫面僅供瀏覽。';
          return '"' + label + '" is being edited in another tab. This view is read-only.';
        }""",
    ),
    (
        """          window.alert(
            document.documentElement.getAttribute('lang') === 'ja'
              ? '確定済みの年は繁閑%を編集できません。'
              : 'Cannot edit H/L % for a locked year.'
          );""",
        """          window.alert(
            (function () {
              var lang = String(document.documentElement.getAttribute('lang') || '').toLowerCase();
              if (lang.indexOf('ja') === 0) return '確定済みの年は繁閑%を編集できません。';
              if (lang.indexOf('zh') === 0) return '已鎖定的年份無法編輯旺淡%。';
              return 'Cannot edit H/L % for a locked year.';
            })()
          );""",
    ),
    (
        """          var monthNames =
          document.documentElement.getAttribute('lang') === 'ja'
            ? ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
            : ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        for (var i = 0; i < 12; i++) {
          var input = window.prompt(
            (document.documentElement.getAttribute('lang') === 'ja' ? '繁閑期% ' : 'H/L % ') +
              monthNames[i] +
              ' (5% steps)',
            String(weights[i])
          );
          if (input == null) return;
          var next = normalizeWeightInput(input);
          if (next == null) {
            window.alert(
              document.documentElement.getAttribute('lang') === 'ja'
                ? '5%刻みの整数（60〜200）で入力してください。'
                : 'Please enter an integer in 5% steps (60 to 200).'
            );
            return;
          }""",
        """          var _hlLang = String(document.documentElement.getAttribute('lang') || '').toLowerCase();
          var _hlJa = _hlLang.indexOf('ja') === 0;
          var _hlZh = _hlLang.indexOf('zh') === 0;
          var monthNames = (_hlJa || _hlZh)
            ? ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
            : ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        for (var i = 0; i < 12; i++) {
          var input = window.prompt(
            (_hlJa ? '繁閑期% ' : _hlZh ? '旺淡期% ' : 'H/L % ') +
              monthNames[i] +
              (_hlJa ? '（5%刻み）' : _hlZh ? '（5%刻度）' : ' (5% steps)'),
            String(weights[i])
          );
          if (input == null) return;
          var next = normalizeWeightInput(input);
          if (next == null) {
            window.alert(
              _hlJa
                ? '5%刻みの整数（60〜200）で入力してください。'
                : _hlZh
                  ? '請輸入 5% 刻度的整數（60–200）。'
                  : 'Please enter an integer in 5% steps (60 to 200).'
            );
            return;
          }""",
    ),
    (
        "window.alert('Jump is allowed only from ' + b.minYear + ' to ' + b.maxYear + '. Selected year ' + y + ' is out of range.');",
        """window.alert((function () {
          var lang = String(document.documentElement.getAttribute('lang') || '').toLowerCase();
          if (lang.indexOf('ja') === 0) return 'ジャンプできるのは ' + b.minYear + '〜' + b.maxYear + ' 年です。選択年 ' + y + ' は範囲外です。';
          if (lang.indexOf('zh') === 0) return '可跳轉年份僅限 ' + b.minYear + '–' + b.maxYear + '。所選年份 ' + y + ' 超出範圍。';
          return 'Jump is allowed only from ' + b.minYear + ' to ' + b.maxYear + '. Selected year ' + y + ' is out of range.';
        })());""",
    ),
]

# annual summary collapse labels near end of file
ANNUAL_SUMMARY = [
    (
        """      function isJa() {
        return document.documentElement.getAttribute('lang') === 'ja';
      }
      function label(collapsed) {
        if (collapsed) {
          return isJa() ? 'サマリーを表示' : 'Show summary';
        }
        return isJa() ? 'サマリーを折りたたむ' : 'Collapse summary';
      }""",
        """      function isJa() {
        return document.documentElement.getAttribute('lang') === 'ja';
      }
      function isZh() {
        return String(document.documentElement.getAttribute('lang') || '')
          .toLowerCase()
          .indexOf('zh') === 0;
      }
      function label(collapsed) {
        if (collapsed) {
          return isJa() ? 'サマリーを表示' : isZh() ? '顯示摘要' : 'Show summary';
        }
        return isJa() ? 'サマリーを折りたたむ' : isZh() ? '收合摘要' : 'Collapse summary';
      }""",
    ),
]


def apply_aria(text: str) -> tuple[str, int]:
    n = 0
    for en, zh in ARIA:
        a = f'aria-label="{en}"'
        b = f'aria-label="{zh}"'
        c = text.count(a)
        if c:
            text = text.replace(a, b)
            n += c
    return text, n


def apply_pairs(text: str, pairs: list[tuple[str, str]]) -> tuple[str, int]:
    n = 0
    for a, b in pairs:
        c = text.count(a)
        if c:
            text = text.replace(a, b)
            n += c
    return text, n


def main() -> None:
    for path, name in ((MONTHLY, "monthly"), (ANNUAL, "annual")):
        text = path.read_text(encoding="utf-8")
        text, n_aria = apply_aria(text)
        text, n_static = apply_pairs(text, STATIC)
        # visible demo None inside strong blocks already handled partially; ensure leftover
        text2 = text.replace("<strong>店內活動</strong> None", "<strong>店內活動</strong> 無")
        text2 = text2.replace("<strong>店內活動</strong>\n                None", "<strong>店內活動</strong>\n                無")
        if text2 != text:
            n_static += 1
            text = text2
        print(f"{name}: aria={n_aria} static={n_static}")

        if path == ANNUAL:
            c = text.count(T_OLD)
            if c:
                text = text.replace(T_OLD, T_NEW)
                print(f"  annual: upgraded t(ja,en) x{c}")
            else:
                print("  annual: t(ja,en) already upgraded or missing")
            text, n_sum = apply_pairs(text, ANNUAL_SUMMARY)
            print(f"  annual summary labels: {n_sum}")

        if path == MONTHLY:
            text, n_js = apply_pairs(text, MONTHLY_JS)
            print(f"  monthly js: {n_js}")
            # same lease/jump may also exist on annual — apply there too below

        path.write_text(text, encoding="utf-8")

    # apply monthly-style alerts to annual if present
    text = ANNUAL.read_text(encoding="utf-8")
    text, n_js = apply_pairs(text, MONTHLY_JS)
    print(f"annual js (shared patterns): {n_js}")
    ANNUAL.write_text(text, encoding="utf-8")

    # verify
    for path in (MONTHLY, ANNUAL):
        t = path.read_text(encoding="utf-8")
        assert 'aria-label="Weekly insight"' not in t
        assert "Uncheck years with abnormal" not in t
    assert "function t(ja, en, zh)" in ANNUAL.read_text(encoding="utf-8")
    print("verify: OK")
    print("patch_zh_tw_p2_remaining_en: OK")


if __name__ == "__main__":
    main()
