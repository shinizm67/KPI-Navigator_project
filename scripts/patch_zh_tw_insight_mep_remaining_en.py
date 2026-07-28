#!/usr/bin/env python3
"""zh-tw Insight/MEP leftover English (P1 wave).

Fixes:
1. insightIsJaLang() binary → insightUiLang() + insightPick(ja,en,zh)
2. Key Insight JS labels (None / weather / status / weekly / memos)
3. Annual static: Tutorial, path-change chooser, business-days titles
4. MEP zoom alert English
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MONTHLY = ROOT / "zh-tw" / "app" / "monthly" / "index.html"
ANNUAL = ROOT / "zh-tw" / "app" / "annual" / "index.html"
MEP = ROOT / "zh-tw" / "app" / "monthly" / "edit" / "index.html"

HELPER_OLD = """      function insightIsJaLang() {
        return (
          String(document.documentElement.getAttribute('lang') || '')
            .toLowerCase()
            .indexOf('ja') === 0
        );
      }

      function dualInsightNoneLabel() {
        return insightIsJaLang() ? 'なし' : 'None';
      }"""

HELPER_NEW = """      function insightUiLang() {
        var lang = String(document.documentElement.getAttribute('lang') || '')
          .toLowerCase();
        if (lang.indexOf('ja') === 0) return 'ja';
        if (lang.indexOf('zh') === 0) return 'zh';
        return 'en';
      }
      function insightIsJaLang() {
        return insightUiLang() === 'ja';
      }
      function insightIsZhLang() {
        return insightUiLang() === 'zh';
      }
      function insightPick(ja, en, zh) {
        var l = insightUiLang();
        if (l === 'ja') return ja;
        if (l === 'zh') return zh != null ? zh : en;
        return en;
      }

      function dualInsightNoneLabel() {
        return insightPick('なし', 'None', '無');
      }"""

WEATHER_OLD = """      function dualInsightWeatherLabel(code) {
        var presets = [
          { code: '', ja: '—', en: '—' },
          { code: 'sunny', ja: '晴れ', en: 'Sunny' },
          { code: 'cloudy', ja: '曇り', en: 'Cloudy' },
          { code: 'rain', ja: '雨', en: 'Rain' },
          { code: 'snow', ja: '雪', en: 'Snow' },
          { code: 'thunder', ja: '雷', en: 'Thunder' },
          { code: 'storm', ja: '嵐', en: 'Storm' },
          { code: 'gale', ja: '暴風', en: 'Gale' },
        ];
        var s = String(code == null ? '' : code).trim();
        var low = s.toLowerCase();
        if (low === 'fine') s = 'sunny';
        var ja = insightIsJaLang();
        for (var i = 0; i < presets.length; i++) {
          if (presets[i].code === s) return ja ? presets[i].ja : presets[i].en;
        }
        return s ? s : DASH;
      }"""

WEATHER_NEW = """      function dualInsightWeatherLabel(code) {
        var presets = [
          { code: '', ja: '—', en: '—', zh: '—' },
          { code: 'sunny', ja: '晴れ', en: 'Sunny', zh: '晴' },
          { code: 'cloudy', ja: '曇り', en: 'Cloudy', zh: '陰' },
          { code: 'rain', ja: '雨', en: 'Rain', zh: '雨' },
          { code: 'snow', ja: '雪', en: 'Snow', zh: '雪' },
          { code: 'thunder', ja: '雷', en: 'Thunder', zh: '雷' },
          { code: 'storm', ja: '嵐', en: 'Storm', zh: '暴風雨' },
          { code: 'gale', ja: '暴風', en: 'Gale', zh: '強風' },
        ];
        var s = String(code == null ? '' : code).trim();
        var low = s.toLowerCase();
        if (low === 'fine') s = 'sunny';
        for (var i = 0; i < presets.length; i++) {
          if (presets[i].code === s) {
            return insightPick(presets[i].ja, presets[i].en, presets[i].zh);
          }
        }
        return s ? s : DASH;
      }"""


def patch_insight_js(text: str, label: str) -> str:
    n = 0
    if HELPER_OLD in text:
        text = text.replace(HELPER_OLD, HELPER_NEW, 1)
        n += 1
        print(f"  {label}: injected insightUiLang/insightPick")
    elif "function insightPick(" in text:
        print(f"  {label}: insightPick already present")
    else:
        print(f"  {label}: WARN helper block not found")

    if WEATHER_OLD in text:
        text = text.replace(WEATHER_OLD, WEATHER_NEW, 1)
        n += 1
        print(f"  {label}: weather zh labels")
    elif "zh: '晴'" in text:
        print(f"  {label}: weather zh already present")
    else:
        print(f"  {label}: WARN weather block not found")

    reps = [
        (
            "term = ja ? '第' + termNum + '四半期' : 'Term ' + termNum;",
            "term = insightPick('第' + termNum + '四半期', 'Term ' + termNum, '第' + termNum + '季');",
        ),
        (
            """        var status = abs < 3
          ? ja ? '順調' : 'On Track'
          : abs <= 10
            ? ja ? '要注意' : 'Watch'
            : ja ? '要改訂' : 'Revise';""",
            """        var status = abs < 3
          ? insightPick('順調', 'On Track', '順利')
          : abs <= 10
            ? insightPick('要注意', 'Watch', '需注意')
            : insightPick('要改訂', 'Revise', '需修正');""",
        ),
        (
            """      function historicalReasonEmptyLabel(kind) {
        if (insightIsJaLang()) {
          return kind === 'year' ? 'この期間のメモはありません' : 'この月のメモはありません';
        }
        return kind === 'year' ? 'No memo for this period' : 'No memo for this month';
      }""",
            """      function historicalReasonEmptyLabel(kind) {
        if (kind === 'year') {
          return insightPick('この期間のメモはありません', 'No memo for this period', '此期間沒有備註');
        }
        return insightPick('この月のメモはありません', 'No memo for this month', '本月沒有備註');
      }""",
        ),
        (
            """      function historicalReasonMemoLabels(year) {
        var ja = insightIsJaLang();
        var defaults = ja
          ? ['店舗イベント', 'エリアイベント', 'SNS', 'マーケ', 'プロモ', '予約']
          : [
              'Store Event',
              'Area Event',
              'Social Media',
              'Marketing',
              'Promo Conversion',
              'Reservation',
            ];
        var payload = dualInsightLoadYearPayload(year);
        var labels = defaults.slice();
        if (payload && payload.mepMemoRows && payload.mepMemoRows.length) {
          for (var i = 0; i < 6 && i < payload.mepMemoRows.length; i++) {
            var row = payload.mepMemoRows[i];
            var lab = ja
              ? row.labelJa || row.labelEn || defaults[i]
              : row.labelEn || row.labelJa || defaults[i];
            if (lab) labels[i] = String(lab);
          }
        }
        return labels;
      }""",
            """      function historicalReasonMemoLabels(year) {
        var defaults = insightPick(
          ['店舗イベント', 'エリアイベント', 'SNS', 'マーケ', 'プロモ', '予約'],
          [
            'Store Event',
            'Area Event',
            'Social Media',
            'Marketing',
            'Promo Conversion',
            'Reservation',
          ],
          ['店家活動', '地區活動', '社群媒體', '行銷', '促銷轉換', '預約']
        );
        var payload = dualInsightLoadYearPayload(year);
        var labels = defaults.slice();
        var lang = insightUiLang();
        if (payload && payload.mepMemoRows && payload.mepMemoRows.length) {
          for (var i = 0; i < 6 && i < payload.mepMemoRows.length; i++) {
            var row = payload.mepMemoRows[i];
            var lab =
              lang === 'ja'
                ? row.labelJa || row.labelEn || defaults[i]
                : lang === 'zh'
                  ? row.labelZh || row.labelJa || row.labelEn || defaults[i]
                  : row.labelEn || row.labelJa || defaults[i];
            if (lab) labels[i] = String(lab);
          }
        }
        return labels;
      }""",
        ),
        (
            "label: insightIsJaLang() ? '天気' : 'Weather',",
            "label: insightPick('天気', 'Weather', '天氣'),",
        ),
        (
            "label: insightIsJaLang() ? '戦略メモ' : 'User Note',",
            "label: insightPick('戦略メモ', 'User Note', '策略備註'),",
        ),
        # Weekly Insight block
        (
            """      var useJa =
        String(document.documentElement.getAttribute('lang') || '')
          .toLowerCase()
          .indexOf('ja') === 0;
      var memoTooltipMax = useJa ? 300 : 500;
      var noneLabel = useJa ? 'なし' : 'None';
      var offSuffix = useJa ? ' OFF' : ' OFF';
      var todayNavLabel = useJa ? '本日' : 'Today';
      var weeklyTitleLabel = useJa ? '週間考察' : 'Weekly Insight';
      var dateColLabel = useJa ? '日付' : 'Date';
      var weatherColLabel = useJa ? '天気' : 'Weather';
      var memoColDefaults = useJa
        ? ['店舗イベント', 'エリアイベント', 'SNS', 'マーケ', 'プロモ', '予約']
        : [
            'Store Event',
            'Area Event',
            'Social Media',
            'Marketing',
            'Promo Conversion',
            'Reservation'
          ];""",
            """      var useJa = typeof insightIsJaLang === 'function' ? insightIsJaLang() : false;
      var useZh = typeof insightIsZhLang === 'function' ? insightIsZhLang() : false;
      var memoTooltipMax = useJa ? 300 : 500;
      var noneLabel = typeof insightPick === 'function' ? insightPick('なし', 'None', '無') : (useJa ? 'なし' : 'None');
      var offSuffix = typeof insightPick === 'function' ? insightPick(' 公休', ' OFF', ' 公休') : (useJa ? ' 公休' : ' OFF');
      var todayNavLabel = typeof insightPick === 'function' ? insightPick('本日', 'Today', '今天') : (useJa ? '本日' : 'Today');
      var weeklyTitleLabel = typeof insightPick === 'function' ? insightPick('週間考察', 'Weekly Insight', '週間洞察') : (useJa ? '週間考察' : 'Weekly Insight');
      var dateColLabel = typeof insightPick === 'function' ? insightPick('日付', 'Date', '日期') : (useJa ? '日付' : 'Date');
      var weatherColLabel = typeof insightPick === 'function' ? insightPick('天気', 'Weather', '天氣') : (useJa ? '天気' : 'Weather');
      var memoColDefaults = typeof insightPick === 'function'
        ? insightPick(
            ['店舗イベント', 'エリアイベント', 'SNS', 'マーケ', 'プロモ', '予約'],
            ['Store Event', 'Area Event', 'Social Media', 'Marketing', 'Promo Conversion', 'Reservation'],
            ['店家活動', '地區活動', '社群媒體', '行銷', '促銷轉換', '預約']
          )
        : (useJa
            ? ['店舗イベント', 'エリアイベント', 'SNS', 'マーケ', 'プロモ', '予約']
            : ['Store Event', 'Area Event', 'Social Media', 'Marketing', 'Promo Conversion', 'Reservation']);""",
        ),
        # OFF day suffix in monthly table date labels
        (
            "return isBusinessDayByIso(iso, d) ? base : base + (useJa ? ' 公休' : ' OFF');",
            "return isBusinessDayByIso(iso, d) ? base : base + (useJa || (String(document.documentElement.getAttribute('lang')||'').toLowerCase().indexOf('zh')===0) ? ' 公休' : ' OFF');",
        ),
    ]
    for a, b in reps:
        if a in text:
            text = text.replace(a, b)
            n += 1
        else:
            # allow already-patched
            if b[:40] in text:
                continue
            print(f"  {label}: miss fragment: {a[:60]!r}")
    print(f"  {label}: applied {n} insight fragments")
    return text


ANNUAL_STATIC = [
    (
        'title="Total business days in the selected year"',
        'title="所選年份的營業日合計"',
    ),
    (
        'title="Total business days this year"',
        'title="本年營業日合計"',
    ),
    (
        'aria-label="Tutorial visibility"',
        'aria-label="教學顯示設定"',
    ),
    (
        '<h2 class="tutorial-toggle-float__title">Tutorial</h2>',
        '<h2 class="tutorial-toggle-float__title">教學</h2>',
    ),
    (
        'aria-label="Toggle tutorial visibility"',
        'aria-label="切換教學顯示"',
    ),
    (
        'id="tutorial-toggle-on">on</p>',
        'id="tutorial-toggle-on">開</p>',
    ),
    (
        'id="tutorial-toggle-off">off</p>',
        'id="tutorial-toggle-off">關</p>',
    ),
    (
        'aria-label="Close"',
        'aria-label="關閉"',
    ),
    (
        '>Switch input surface</p>',
        '>切換輸入介面</p>',
    ),
    (
        ">You have unsaved changes. Save before switching, or discard and switch.</p>",
        ">尚有未儲存的變更。請先儲存再切換，或不儲存直接切換。</p>",
    ),
    (
        ">Save and switch\n        </button>",
        ">儲存後切換\n        </button>",
    ),
    (
        ">Switch without saving\n        </button>",
        ">不儲存並切換\n        </button>",
    ),
    (
        'id="kpi-path-change-cancel">\n          Cancel\n        </button>',
        'id="kpi-path-change-cancel">\n          取消\n        </button>',
    ),
]

# Insight high-visibility aria (same on monthly/annual)
ARIA_REPS = [
    ('aria-label="Today sales vs historical weekday average"', 'aria-label="今日銷售與過去同星期平均比較"'),
    ('aria-label="Monthly sales status"', 'aria-label="月度銷售狀態"'),
    ('aria-label="Annual sales status"', 'aria-label="年度銷售狀態"'),
    ('aria-label="Cost structure"', 'aria-label="成本結構"'),
    ('aria-label="Back to top"', 'aria-label="回到頁首"'),
    ('aria-label="Daily"', 'aria-label="每日"'),
    ('aria-label="Date navigation"', 'aria-label="日期導覽"'),
    ('aria-label="Daily (Analyze)"', 'aria-label="每日（分析）"'),
    ('aria-label="Monthly (Analyze)"', 'aria-label="月度（分析）"'),
    ('aria-label="Annual (Analyze)"', 'aria-label="年度（分析）"'),
    ('aria-label="Daily (Graph)"', 'aria-label="每日（圖表）"'),
    ('aria-label="Monthly (Graph)"', 'aria-label="月度（圖表）"'),
    ('aria-label="Annual (Graph)"', 'aria-label="年度（圖表）"'),
]


def apply_list(text: str, pairs: list[tuple[str, str]], label: str) -> str:
    n = 0
    for a, b in pairs:
        c = text.count(a)
        if c:
            text = text.replace(a, b)
            n += c
    print(f"  {label}: {n} replacements")
    return text


def patch_mep() -> None:
    text = MEP.read_text(encoding="utf-8")
    old1 = "window.alert('Zoom must be between ' + min + '% and ' + max + '%.');"
    new1 = "window.alert('縮放必須介於 ' + min + '% 到 ' + max + '%。');"
    old2 = "window.alert('Only half-width numeric input is allowed.');"
    new2 = "window.alert('僅可輸入半形數字。');"
    n = 0
    if old1 in text:
        text = text.replace(old1, new1)
        n += 1
    if old2 in text:
        text = text.replace(old2, new2)
        n += 1
    MEP.write_text(text, encoding="utf-8")
    print(f"MEP zoom alerts: {n}")


def main() -> None:
    for path, name in ((MONTHLY, "monthly"), (ANNUAL, "annual")):
        text = path.read_text(encoding="utf-8")
        text = patch_insight_js(text, name)
        text = apply_list(text, ARIA_REPS, f"{name} aria")
        if path == ANNUAL:
            text = apply_list(text, ANNUAL_STATIC, "annual static")
        # sample visible None → 無 (keep data-memo="None")
        text2 = text.replace(">None</", ">無</")
        if text2 != text:
            print(f"  {name}: visible None→無 applied")
            text = text2
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")

    patch_mep()

    # verify helpers
    for path in (MONTHLY, ANNUAL):
        t = path.read_text(encoding="utf-8")
        assert "function insightPick(" in t, path
        assert "insightPick('なし', 'None', '無')" in t, path
        assert "zh: '晴'" in t, path
    print("verify: OK")
    print("patch_zh_tw_insight_mep_remaining_en: OK")


if __name__ == "__main__":
    main()
