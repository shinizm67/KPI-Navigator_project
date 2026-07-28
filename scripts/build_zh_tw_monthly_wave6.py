#!/usr/bin/env python3
"""Monthly zh-tw Wave 6: remaining JS i18n polish (date OFF, aria, tutorial chrome)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DST = ROOT / "zh-tw" / "app" / "monthly" / "index.html"

REPLACEMENTS = [
    (
        "return isBusinessDayByIso(iso, d) ? base : base + ' OFF';",
        "return isBusinessDayByIso(iso, d) ? base : base + (useJa ? ' 公休' : ' OFF');",
    ),
    (
        "(off ? ' 店休' : '');",
        "(off ? ' 公休' : '');",
    ),
    (
        "el.setAttribute('title', isJa ? 'メモがあります' : 'Memo saved');",
        "el.setAttribute('title', isJa ? 'メモがあります' : (String(document.documentElement.getAttribute('lang')||'').indexOf('zh')===0 ? '已儲存備註' : 'Memo saved'));",
    ),
    (
        "isJa ? 'メモがあります' : 'Memo saved'",
        "isJa ? 'メモがあります' : (String(document.documentElement.getAttribute('lang')||'').indexOf('zh')===0 ? '已儲存備註' : 'Memo saved')",
    ),
    (
        "isJa ? dateLabel + '（メモあり）' : dateLabel + ' (memo saved)'",
        "isJa ? dateLabel + '（メモあり）' : (String(document.documentElement.getAttribute('lang')||'').indexOf('zh')===0 ? dateLabel + '（有備註）' : dateLabel + ' (memo saved)')",
    ),
    ('aria-label="Tutorial visibility"', 'aria-label="教學顯示設定"'),
    ('tutorial-toggle-float__title">Tutorial</h2>', 'tutorial-toggle-float__title">教學</h2>'),
    ('aria-label="Toggle tutorial visibility"', 'aria-label="切換教學顯示"'),
    # leftover mangled aria from wave5 partial replaces
    ('aria-label="支出 metrics"', 'aria-label="支出指標"'),
    ('aria-label="利潤 metrics"', 'aria-label="利潤指標"'),
    ('aria-label="參考 metrics"', 'aria-label="參考指標"'),
    (
        '<span class="insight-daily-reference__label-line">Historical Same Month &amp;</span><br><span class="insight-daily-reference__label-line">星期平均</span>',
        '<span class="insight-daily-reference__label-line">過去同月・</span><br><span class="insight-daily-reference__label-line">同星期平均</span>',
    ),
    (
        'daily-overlay__vlabel">Daily</p>',
        'daily-overlay__vlabel">每日</p>',
    ),
    (
        'daily-overlay__vlabel">Monthly</p>',
        'daily-overlay__vlabel">月度</p>',
    ),
    (
        'daily-overlay__vlabel">Annual</p>',
        'daily-overlay__vlabel">年度</p>',
    ),
]


def main() -> None:
    if not DST.is_file():
        raise SystemExit(f"missing {DST}")
    text = DST.read_text(encoding="utf-8")
    missing = []
    for a, b in REPLACEMENTS:
        if a not in text:
            missing.append(a[:80])
            continue
        text = text.replace(a, b)
    DST.write_text(text, encoding="utf-8")
    if missing:
        print("WARN missing (already applied?):")
        for m in missing:
            print(" ", repr(m))

    t = DST.read_text(encoding="utf-8")
    for s in ["公休", "教學", "已儲存備註", "同星期平均"]:
        if s not in t:
            raise SystemExit(f"missing after wave6: {s}")
    # ensure no mangled metrics aria left in HTML attrs
    if ' metrics"' in t:
        print("WARN still has ' metrics\"' somewhere")
    print("wave6 applied:", DST.relative_to(ROOT))
    print("build_zh_tw_monthly_wave6: OK")


if __name__ == "__main__":
    main()
