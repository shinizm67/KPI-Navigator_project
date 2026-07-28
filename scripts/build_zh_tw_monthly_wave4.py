#!/usr/bin/env python3
"""Monthly zh-tw Wave 4: Bulk daily edit modal (HTML + JS i18n hooks)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DST = ROOT / "zh-tw" / "app" / "monthly" / "index.html"

WAVE4_REPLACEMENTS = [
    (">Bulk daily edit</h2>", ">每日批次編輯</h2>"),
    (
        'id="annual-edit-modal-close" aria-label="Close"',
        'id="annual-edit-modal-close" aria-label="關閉"',
    ),
    (
        'id="annual-edit-modal-save" aria-label="Save">\n        Save\n      </button>',
        'id="annual-edit-modal-save" aria-label="儲存">\n        儲存\n      </button>',
    ),
    (
        'for="annual-edit-year-select">Year</label>',
        'for="annual-edit-year-select">年</label>',
    ),
    (
        'for="annual-edit-month-select">Month</label>',
        'for="annual-edit-month-select">月</label>',
    ),
    (
        'aria-label="Choose year from list"',
        'aria-label="從清單選擇年份"',
    ),
    (
        'aria-label="Choose month from list"',
        'aria-label="從清單選擇月份"',
    ),
    (
        'id="annual-edit-date-header-btn">Date</button>',
        'id="annual-edit-date-header-btn">日期</button>',
    ),
    (
        'aria-label="Filter rows by weekday or national holiday"',
        'aria-label="依星期或國定假日篩選列"',
    ),
    (
        'aria-label="Weekdays and holidays"',
        'aria-label="星期與假日"',
    ),
    ("/> Monday</label", "/> 星期一</label"),
    ("/> Tuesday</label", "/> 星期二</label"),
    ("/> Wednesday</label", "/> 星期三</label"),
    ("/> Thursday</label", "/> 星期四</label"),
    ("/> Friday</label", "/> 星期五</label"),
    ("/> Saturday</label", "/> 星期六</label"),
    ("/> Sunday</label", "/> 星期日</label"),
    (
        'id="annual-edit-filter-holiday" /> National holiday</label',
        'id="annual-edit-filter-holiday" /> 國定假日</label',
    ),
    (
        'id="annual-edit-filter-clear">\n                Clear filter\n              </button>',
        'id="annual-edit-filter-clear">\n                清除篩選\n              </button>',
    ),
    (
        'aria-label="Pick a date to jump to top of list"',
        'aria-label="選擇日期並跳至清單頂端"',
    ),
    (
        'annual-edit-modal__colhead-dayoff-title">Day Off</span>',
        'annual-edit-modal__colhead-dayoff-title">公休</span>',
    ),
    (
        'id="annual-edit-select-all">Select All</button>',
        'id="annual-edit-select-all">全選</button>',
    ),
    (
        '<span>Sales</span>\n          <div class="annual-edit-modal__sales-sort"',
        '<span>銷售</span>\n          <div class="annual-edit-modal__sales-sort"',
    ),
    ('aria-label="Sort by sales"', 'aria-label="依銷售排序"'),
    ('aria-label="Sales sort options"', 'aria-label="銷售排序選項"'),
    (
        ">\n                  Descending (high → low)\n                </button>",
        ">\n                  降冪（高 → 低）\n                </button>",
    ),
    (
        ">\n                  Ascending (low → high)\n                </button>",
        ">\n                  升冪（低 → 高）\n                </button>",
    ),
    (
        'annual-edit-modal__sales-sort-section-label">Numeric rank</div>',
        'annual-edit-modal__sales-sort-section-label">數值排名</div>',
    ),
    (
        'id="annual-edit-sales-sort-reset">\n                Back to date order\n              </button>',
        'id="annual-edit-sales-sort-reset">\n                回到日期順序\n              </button>',
    ),
    (
        'id="annual-edit-modal-table" aria-label="Daily rows"',
        'id="annual-edit-modal-table" aria-label="每日列"',
    ),
]

EDIT_LANG_OLD = """      var isJa = document.documentElement.getAttribute('lang') === 'ja';
      var MONTHS_JA = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'];
      var MONTHS_EN = [
        'January',
        'February',
        'March',
        'April',
        'May',
        'June',
        'July',
        'August',
        'September',
        'October',
        'November',
        'December'
      ];
      var WEEKDAYS_EN = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'];
      var WEEKDAYS_JA = ['日', '月', '火', '水', '木', '金', '土'];

      var state = {
        year: 2026,
        viewMonth: 0,
        rowStateByIso: {},
        salesPinnedAmount: null,
        salesAmountSort: null,
        modalDirty: false
      };
      var lastFocusEl = null;
      var MSG_UNSAVED_CLOSE = isJa
        ? '変更が保存されていません。保存せずに閉じますか？'
        : 'You have unsaved changes. Close without saving?';"""

EDIT_LANG_NEW = """      var _editLang = String(document.documentElement.getAttribute('lang') || '').toLowerCase();
      var isJa = _editLang === 'ja' || _editLang.indexOf('ja') === 0;
      var isZh = _editLang.indexOf('zh') === 0;
      var MONTHS_JA = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'];
      var MONTHS_EN = [
        'January',
        'February',
        'March',
        'April',
        'May',
        'June',
        'July',
        'August',
        'September',
        'October',
        'November',
        'December'
      ];
      var WEEKDAYS_EN = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'];
      var WEEKDAYS_JA = ['日', '月', '火', '水', '木', '金', '土'];

      var state = {
        year: 2026,
        viewMonth: 0,
        rowStateByIso: {},
        salesPinnedAmount: null,
        salesAmountSort: null,
        modalDirty: false
      };
      var lastFocusEl = null;
      var MSG_UNSAVED_CLOSE = isJa
        ? '変更が保存されていません。保存せずに閉じますか？'
        : isZh
          ? '尚有未儲存的變更。要在不儲存的情況下關閉嗎？'
          : 'You have unsaved changes. Close without saving?';"""

EDIT_ARIA_DAYOFF_OLD = "cb.setAttribute('aria-label', isJa ? '店休日' : 'Day off');"
EDIT_ARIA_DAYOFF_NEW = "cb.setAttribute('aria-label', isJa ? '店休日' : isZh ? '公休日' : 'Day off');"

EDIT_LEASE_OLD = "if (!window.__KPI_EDIT_LEASE.tryAcquire(isJa ? '年次編集' : 'Annual Edit')) {"
EDIT_LEASE_NEW = "if (!window.__KPI_EDIT_LEASE.tryAcquire(isJa ? '年次編集' : isZh ? '每日批次編輯' : 'Annual Edit')) {"

EDIT_MONTH_LABEL_OLD = "var labels = isJa ? MONTHS_JA : MONTHS_EN;"
EDIT_MONTH_LABEL_NEW = "var labels = (isJa || isZh) ? MONTHS_JA : MONTHS_EN;"

EDIT_MONTH_LAB_OLD = "monthLab.textContent = isJa ? MONTHS_JA[item.m0] : MONTHS_EN[item.m0];"
EDIT_MONTH_LAB_NEW = "monthLab.textContent = (isJa || isZh) ? MONTHS_JA[item.m0] : MONTHS_EN[item.m0];"


def main() -> None:
    if not DST.is_file():
        raise SystemExit(f"missing {DST}")
    text = DST.read_text(encoding="utf-8")
    missing = []
    for a, b in WAVE4_REPLACEMENTS:
        if a not in text:
            missing.append(a[:90])
            continue
        text = text.replace(a, b)

    for old, new, label in [
        (EDIT_LANG_OLD, EDIT_LANG_NEW, "EDIT_LANG"),
        (EDIT_ARIA_DAYOFF_OLD, EDIT_ARIA_DAYOFF_NEW, "DAYOFF"),
        (EDIT_LEASE_OLD, EDIT_LEASE_NEW, "LEASE"),
        (EDIT_MONTH_LABEL_OLD, EDIT_MONTH_LABEL_NEW, "MONTH_LABEL"),
        (EDIT_MONTH_LAB_OLD, EDIT_MONTH_LAB_NEW, "MONTH_LAB"),
    ]:
        if old not in text:
            if "isZh" in text and label == "EDIT_LANG" and "尚有未儲存" in text:
                print(label, "already patched")
            elif label != "EDIT_LANG" and "isZh ?" in text:
                print(label, "maybe already")
                missing.append(label)
            else:
                missing.append(label)
        else:
            text = text.replace(old, new, 1)

    DST.write_text(text, encoding="utf-8")
    if missing:
        print("WARN missing:")
        for m in missing:
            print(" ", repr(m))

    t = DST.read_text(encoding="utf-8")
    for s in [
        "每日批次編輯",
        "儲存",
        "國定假日",
        "公休",
        "全選",
        "降冪（高 → 低）",
        "回到日期順序",
        "尚有未儲存的變更",
        "isZh",
    ]:
        if s not in t:
            raise SystemExit(f"missing after wave4: {s}")
    print("wave4 applied:", DST.relative_to(ROOT))
    print("build_zh_tw_monthly_wave4: OK")


if __name__ == "__main__":
    main()
