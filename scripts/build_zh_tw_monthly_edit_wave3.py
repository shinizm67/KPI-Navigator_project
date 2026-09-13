#!/usr/bin/env python3
"""zh-tw Monthly Edit Wave 3: View/Edit sides, UNDO, Daily Notes float labels.

Focus Bar / KPI strip English product labels stay English (docs/font-locale-policy.md).
This wave localizes remaining MEP chrome and the memo float panel.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DST = ROOT / "zh-tw" / "app" / "monthly" / "edit" / "index.html"
MARKER = "/* KPI-MEP-ZH-TW-WAVE3 */"

STATIC: list[tuple[str, str]] = [
    (
        '<span class="kpi-daily-input-path__side is-active" data-kpi-edit-side="view">View</span>',
        '<span class="kpi-daily-input-path__side is-active" data-kpi-edit-side="view">檢視</span>',
    ),
    (
        '<span class="kpi-daily-input-path__side is-inactive" data-kpi-edit-side="edit">Edit</span>',
        '<span class="kpi-daily-input-path__side is-inactive" data-kpi-edit-side="edit">編輯</span>',
    ),
    (
        'data-kpi-edit-side="view">View</span>',
        'data-kpi-edit-side="view">檢視</span>',
    ),
    (
        'data-kpi-edit-side="edit">Edit</span>',
        'data-kpi-edit-side="edit">編輯</span>',
    ),
    (
        'id="memo-float-undo" disabled>UNDO</button>',
        'id="memo-float-undo" disabled>復原</button>',
    ),
]

OLD_MEMO_LABELS = """      function memoFloatLabels() {
        return useJa
          ? {
              windowTitle: '日次メモ',
              todaySales: "Today's Sales",
              targetSales: "Today's Target Sales",
              diff: 'Difference',
              achievement: 'Achievement',
              weather: 'Weather',
              freeMemoSection: 'Memo（自由記述）',
              addFreeMemo: '自由メモを追加',
              today: 'Today',
              prevMonth: '先月',
              nextMonth: '翌月'
            }
          : {
              windowTitle: 'Daily Notes',
              todaySales: "Today's Sales",
              targetSales: "Today's Target Sales",
              diff: 'Difference',
              achievement: 'Achievement',
              weather: 'Weather',
              freeMemoSection: 'Memo',
              addFreeMemo: 'Add free memo',
              today: 'Today',
              prevMonth: 'Prev',
              nextMonth: 'Next'
            };
      }"""

NEW_MEMO_LABELS = """      function memoFloatLabels() {
        if (useZh) {
          return {
            windowTitle: '每日備註',
            todaySales: '今日銷售',
            targetSales: '今日目標銷售',
            diff: '差額',
            achievement: '達成率',
            weather: '天氣',
            freeMemoSection: '備註（自由記述）',
            addFreeMemo: '新增自由備註',
            today: '今天',
            prevMonth: '上月',
            nextMonth: '下月'
          };
        }
        return useJa
          ? {
              windowTitle: '日次メモ',
              todaySales: "Today's Sales",
              targetSales: "Today's Target Sales",
              diff: 'Difference',
              achievement: 'Achievement',
              weather: 'Weather',
              freeMemoSection: 'Memo（自由記述）',
              addFreeMemo: '自由メモを追加',
              today: 'Today',
              prevMonth: '先月',
              nextMonth: '翌月'
            }
          : {
              windowTitle: 'Daily Notes',
              todaySales: "Today's Sales",
              targetSales: "Today's Target Sales",
              diff: 'Difference',
              achievement: 'Achievement',
              weather: 'Weather',
              freeMemoSection: 'Memo',
              addFreeMemo: 'Add free memo',
              today: 'Today',
              prevMonth: 'Prev',
              nextMonth: 'Next'
            };
      }"""


def main() -> None:
    if not DST.is_file():
        raise SystemExit(f"missing {DST}")
    text = DST.read_text(encoding="utf-8")

    for a, b in STATIC:
        if a not in text:
            if b in text:
                print("skip static:", repr(a[:50]))
                continue
            print("WARN missing:", repr(a[:70]))
            continue
        text = text.replace(a, b)

    if "windowTitle: '每日備註'" in text:
        print("memoFloatLabels already zh")
    elif OLD_MEMO_LABELS in text:
        text = text.replace(OLD_MEMO_LABELS, NEW_MEMO_LABELS, 1)
        print("patched memoFloatLabels")
    else:
        raise SystemExit("memoFloatLabels block not found")

    if MARKER not in text:
        text = text.replace(
            "/* KPI-MEP-ZH-TW-WAVE2 */",
            "/* KPI-MEP-ZH-TW-WAVE2 */\n      " + MARKER,
            1,
        )

    original = DST.read_text(encoding="utf-8")
    if text == original:
        print("unchanged:", DST.relative_to(ROOT))
    else:
        DST.write_text(text, encoding="utf-8")

    t = DST.read_text(encoding="utf-8")
    checks = [
        ("wave3 marker", MARKER in t),
        ("path 檢視", 'data-kpi-edit-side="view">檢視</span>' in t),
        ("path 編輯", 'data-kpi-edit-side="edit">編輯</span>' in t),
        ("UNDO→復原", 'id="memo-float-undo" disabled>復原</button>' in t),
        ("memo zh", "windowTitle: '每日備註'" in t),
        ("no Annual path", 'data-kpi-path-side="annual">' not in t),
        ("no Monthly path", 'data-kpi-path-side="mep">' not in t),
        ("Focus Bar EN kept", "annualProgress: 'Annual Progress'" in t),
    ]
    for name, ok in checks:
        print(("OK" if ok else "FAIL"), name)
        if not ok:
            raise SystemExit(1)
    print("build_zh_tw_monthly_edit_wave3: OK")


if __name__ == "__main__":
    main()
