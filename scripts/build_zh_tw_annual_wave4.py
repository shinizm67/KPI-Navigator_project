#!/usr/bin/env python3
"""Annual zh-tw Wave 4: Past Sales Data / Sales Data / Annual Edit modals."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DST = ROOT / "zh-tw" / "app" / "annual" / "index.html"

# Longest-first within modal region
MODAL_REPLACEMENTS = [
    # --- Past Sales ---
    (">Past Sales Data</h2>", ">過去銷售資料</h2>"),
    ('aria-label="Import CSV"', 'aria-label="匯入 CSV"'),
    (">Import CSV\n      </button>", ">匯入 CSV\n      </button>"),
    ('aria-label="Save"', 'aria-label="儲存"'),
    (">Save\n      </button>", ">儲存\n      </button>"),
    ('aria-label="Past data edit mode"', 'aria-label="過去資料編輯模式"'),
    (">Past Data Edit</p>", ">過去資料編輯</p>"),
    (
        'data-ps-edit-side="view">View</span>',
        'data-ps-edit-side="view">瀏覽</span>',
    ),
    (
        'aria-label="Switch past data between view and edit"',
        'aria-label="在瀏覽與編輯之間切換過去資料"',
    ),
    (
        'title="View: read-only. Edit: change past sales and business days (affects Analyze and seasonality)."',
        'title="瀏覽：唯讀。編輯：可變更過去銷售與營業日（會影響 Analyze 與旺淡）。"',
    ),
    ('aria-label="Collapse summary"', 'aria-label="收合摘要"'),
    ('title="Collapse summary"', 'title="收合摘要"'),
    ('aria-label="Past sales views"', 'aria-label="過去銷售檢視"'),
    (
        'data-psm-tab="input"\n          >\n            Input\n          </button>',
        'data-psm-tab="input"\n          >\n            輸入\n          </button>',
    ),
    (
        'data-psm-tab="analyze"\n          >\n            Analyze\n          </button>',
        'data-psm-tab="analyze"\n          >\n            分析\n          </button>',
    ),
    ('aria-label="Past sales summary"', 'aria-label="過去銷售摘要"'),
    (">Cumulative Input Sales</span>", ">累計輸入銷售</span>"),
    (
        'data-tooltip="Please set your annual target sales"',
        'data-tooltip="請設定年度目標銷售"',
    ),
    ('aria-label="Annual Target Sales"', 'aria-label="年度目標銷售"'),
    (">Remaining / Input Progress</span>", ">剩餘／輸入進度</span>"),
    (">Total B. Days</span>", ">總營業日數</span>"),
    ('aria-label="Year"', 'aria-label="年"'),
    ('aria-label="Month"', 'aria-label="月"'),
    ('aria-label="Previous year"', 'aria-label="上一年"'),
    ('aria-label="Next year"', 'aria-label="下一年"'),
    ('aria-label="Previous month"', 'aria-label="上個月"'),
    ('aria-label="Next month"', 'aria-label="下個月"'),
    (
        'id="past-sales-date-header-btn">Date</button>',
        'id="past-sales-date-header-btn">日期</button>',
    ),
    ('aria-label="Filter by weekday or holiday"', 'aria-label="依星期或假日篩選"'),
    ('aria-label="Weekdays and holidays to show"', 'aria-label="要顯示的星期與假日"'),
    ("/> Sunday</label>", "/> 星期日</label>"),
    ("/> Monday</label>", "/> 星期一</label>"),
    ("/> Tuesday</label>", "/> 星期二</label>"),
    ("/> Wednesday</label>", "/> 星期三</label>"),
    ("/> Thursday</label>", "/> 星期四</label>"),
    ("/> Friday</label>", "/> 星期五</label>"),
    ("/> Saturday</label>", "/> 星期六</label>"),
    (
        "/> National holidays (when calendar linked)",
        "/> 國定假日（連結假日日曆時）",
    ),
    (">\n                Clear filter\n              </button>", ">\n                清除篩選\n              </button>"),
    ('aria-label="Pick a date to scroll the list"', 'aria-label="選擇日期並捲動清單"'),
    (
        'past-sales-modal__colhead-dayoff-title">B. DAY</span>',
        'past-sales-modal__colhead-dayoff-title">營業日</span>',
    ),
    (
        'id="past-sales-select-all">\n              Select all\n            </button>',
        'id="past-sales-select-all">\n              全選\n            </button>',
    ),
    (
        '<span>Sales</span>\n            <div class="past-sales-modal__sales-sort"',
        '<span>銷售</span>\n            <div class="past-sales-modal__sales-sort"',
    ),
    ('aria-label="Sort by sales"', 'aria-label="依銷售排序"'),
    ('aria-label="Sales sort options"', 'aria-label="銷售排序選項"'),
    (">\n                    Descending (high → low)\n                  </button>", ">\n                    降冪（高 → 低）\n                  </button>"),
    (">\n                    Ascending (low → high)\n                  </button>", ">\n                    升冪（低 → 高）\n                  </button>"),
    (
        'past-sales-modal__sales-sort-section-label">Numeric rank</div>',
        'past-sales-modal__sales-sort-section-label">數值排名</div>',
    ),
    (
        'id="past-sales-sales-sort-reset">\n                  Back to date order\n                </button>',
        'id="past-sales-sales-sort-reset">\n                  回到日期順序\n                </button>',
    ),
    (
        'past-sales-modal__colhead-monthly">Monthly Total</div>',
        'past-sales-modal__colhead-monthly">月次合計</div>',
    ),
    (
        'past-sales-modal__colhead-annual">Annual Total</div>',
        'past-sales-modal__colhead-annual">年度合計</div>',
    ),
    ('aria-label="Past sales daily list"', 'aria-label="過去銷售每日清單"'),
    (
        'past-sales-modal__analyze-kpi-label">Annual Input Sales</p>',
        'past-sales-modal__analyze-kpi-label">年度輸入銷售</p>',
    ),
    (
        'past-sales-modal__analyze-kpi-label">Total Business Days</p>',
        'past-sales-modal__analyze-kpi-label">總營業日數</p>',
    ),
    (
        'past-sales-modal__analyze-kpi-label">Average Daily Sales</p>',
        'past-sales-modal__analyze-kpi-label">平均日次銷售</p>',
    ),
    (">Monthly Sales</th>", ">月次銷售</th>"),
    (">Baseline Monthly Sales</th>", ">基準月次銷售</th>"),
    (">Seasonality %</th>", ">旺淡期%</th>"),
    (">Monthly Seasonality %</h3>", ">月次旺淡期%</h3>"),
    (">Close Past Sales Data</p>", ">關閉過去銷售資料</p>"),
    (
        ">Choose whether to save your changes before closing.</p>",
        ">關閉前請選擇是否儲存變更。</p>",
    ),
    (">Save and close\n        </button>", ">儲存並關閉\n        </button>"),
    (">Close without saving\n        </button>", ">不儲存並關閉\n        </button>"),
    (">Cancel\n        </button>", ">取消\n        </button>"),
    # --- Sales Data ---
    (">Sales Data</h2>", ">銷售資料</h2>"),
    (
        'aria-label="Daily target allocation method"',
        'aria-label="每日目標分配方式"',
    ),
    (
        'data-tooltip="Choose how daily targets are allocated. [Flat] Divide each month evenly across business days—every day gets the same target. [Weekday] Apply past weekday patterns (recommended). Months with insufficient data fall back to flat. Pick the option that fits your situation."',
        'data-tooltip="選擇每日目標的分配方式。[月內均等] 將各月依營業日平均分配，每日相同目標。[曜日加重] 套用過去同星期模式（建議）。資料不足的月份會退回均等。請依現況選擇。"',
    ),
    (
        'sdm-daily-target-mode__label">Weekday</span>',
        'sdm-daily-target-mode__label">曜日加重</span>',
    ),
    (
        'data-dtm-mode="monthly-flat"\n            data-kpi-guard-ignore\n          >Flat</button>',
        'data-dtm-mode="monthly-flat"\n            data-kpi-guard-ignore\n          >月內均等</button>',
    ),
    (
        'data-dtm-mode="weekday-weighted"\n            data-kpi-guard-ignore\n          >Weekday</button>',
        'data-dtm-mode="weekday-weighted"\n            data-kpi-guard-ignore\n          >曜日加重</button>',
    ),
    ('aria-label="Daily sales input path"', 'aria-label="每日銷售輸入路徑"'),
    (
        'kpi-daily-input-path__title">Edit</p>',
        'kpi-daily-input-path__title">編輯</p>',
    ),
    (
        'data-kpi-path-side="annual">Annual</span>',
        'data-kpi-path-side="annual">年度</span>',
    ),
    (
        'aria-label="Switch daily sales between Annual and Monthly"',
        'aria-label="在年度與月度之間切換每日銷售"',
    ),
    (
        'data-kpi-path-side="mep">Monthly</span>',
        'data-kpi-path-side="mep">月度</span>',
    ),
    ('aria-label="Sales data views"', 'aria-label="銷售資料檢視"'),
    (
        'data-sdm-tab="input"\n          >\n            Input\n          </button>',
        'data-sdm-tab="input"\n          >\n            輸入\n          </button>',
    ),
    (
        'data-sdm-tab="analyze"\n          >\n            Analyze\n          </button>',
        'data-sdm-tab="analyze"\n          >\n            分析\n          </button>',
    ),
    (
        'data-sdm-tab="input"\n          >\n            Target Sales\n          </button>',
        'data-sdm-tab="input"\n          >\n            目標銷售\n          </button>',
    ),
    ('aria-label="Sales data summary"', 'aria-label="銷售資料摘要"'),
    (
        'id="sales-data-date-header-btn">Date</button>',
        'id="sales-data-date-header-btn">日期</button>',
    ),
    (
        'sales-data-modal__colhead-dayoff-title">B. DAY</span>',
        'sales-data-modal__colhead-dayoff-title">營業日</span>',
    ),
    (
        'id="sales-data-select-all">\n              Select all\n            </button>',
        'id="sales-data-select-all">\n              全選\n            </button>',
    ),
    (
        '<span>Sales</span>\n            <div class="sales-data-modal__sales-sort"',
        '<span>銷售</span>\n            <div class="sales-data-modal__sales-sort"',
    ),
    (
        'sales-data-modal__sales-sort-section-label">Numeric rank</div>',
        'sales-data-modal__sales-sort-section-label">數值排名</div>',
    ),
    (
        'id="sales-data-sales-sort-reset">\n                  Back to date order\n                </button>',
        'id="sales-data-sales-sort-reset">\n                  回到日期順序\n                </button>',
    ),
    (
        'sales-data-modal__colhead-monthly">Monthly Total</div>',
        'sales-data-modal__colhead-monthly">月次合計</div>',
    ),
    (
        'sales-data-modal__colhead-annual">Annual Total</div>',
        'sales-data-modal__colhead-annual">年度合計</div>',
    ),
    (
        'sales-data-modal__analyze-kpi-label">Annual Target Sales</p>',
        'sales-data-modal__analyze-kpi-label">年度目標銷售</p>',
    ),
    (
        'sales-data-modal__analyze-kpi-label">Total Business Days</p>',
        'sales-data-modal__analyze-kpi-label">總營業日數</p>',
    ),
    (
        'sales-data-modal__analyze-kpi-label">Average Daily Sales</p>',
        'sales-data-modal__analyze-kpi-label">平均日次銷售</p>',
    ),
    (">Baseline Monthly Sales</th>", ">基準月次銷售</th>"),
    (">Monthly Target Sales</th>", ">月次目標銷售</th>"),
    (">Reference Seasonality %</th>", ">參考旺淡季%</th>"),
    (">H/L Season% Setting</th>", ">旺淡期%設定</th>"),
    (
        'data-hl-tip="12-month average → 100%"',
        'data-hl-tip="12 個月平均 → 100%"',
    ),
    (">Monthly Allocated Total</td>", ">月次分配率合計</td>"),
    (">Notice</p>", ">通知</p>"),
    ('aria-label="Weekday baseline years"', 'aria-label="曜日分配基準年"'),
    (">Reset to last 2 years</button>", ">還原為最近 2 年</button>"),
    (">Monthly Seasonality %</h3>", ">月次旺淡期%</h3>"),
    (">Close Sales Data</p>", ">關閉銷售資料</p>"),
    # --- Annual Edit ---
    (">Bulk daily edit</h2>", ">每日批次編輯</h2>"),
    ('aria-label="Confirm"', 'aria-label="確認"'),
    (">Confirm\n      </button>", ">確認\n      </button>"),
    ('aria-label="Undo last change"', 'aria-label="復原上一步"'),
    (">Undo\n      </button>", ">復原\n      </button>"),
    (
        'title="Import daily sales from CSV or Excel (.xlsx). Optional Food/Drink columns (either side OK)."',
        'title="從 CSV 或 Excel（.xlsx）匯入每日銷售。可選餐點／飲料欄（左右皆可）。"',
    ),
    (
        'data-tooltip="Import daily sales from CSV or Excel (.xlsx). Optional Food/Drink columns (either side OK)."',
        'data-tooltip="從 CSV 或 Excel（.xlsx）匯入每日銷售。可選餐點／飲料欄（左右皆可）。"',
    ),
    (
        'for="annual-edit-year-select">Year</label>',
        'for="annual-edit-year-select">年</label>',
    ),
    (
        'for="annual-edit-month-select">Month</label>',
        'for="annual-edit-month-select">月</label>',
    ),
    ('aria-label="Choose year from list"', 'aria-label="從清單選擇年份"'),
    ('aria-label="Choose month from list"', 'aria-label="從清單選擇月份"'),
    (
        'id="annual-edit-date-header-btn">Date</button>',
        'id="annual-edit-date-header-btn">日期</button>',
    ),
    (
        'aria-label="Filter rows by weekday or national holiday"',
        'aria-label="依星期或國定假日篩選列"',
    ),
    ('aria-label="Weekdays and holidays"', 'aria-label="星期與假日"'),
    (
        'id="annual-edit-filter-holiday" /> National holiday</label',
        'id="annual-edit-filter-holiday" /> 國定假日</label',
    ),
    (
        'aria-label="Pick a date to jump to top of list"',
        'aria-label="選擇日期並跳至清單頂端"',
    ),
    (
        'annual-edit-modal__colhead-dayoff-title">Business Day</span>',
        'annual-edit-modal__colhead-dayoff-title">營業日</span>',
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
    (
        'annual-edit-modal__sales-sort-section-label">Numeric rank</div>',
        'annual-edit-modal__sales-sort-section-label">數值排名</div>',
    ),
    (
        'id="annual-edit-sales-sort-reset">\n                Back to date order\n              </button>',
        'id="annual-edit-sales-sort-reset">\n                回到日期順序\n              </button>',
    ),
    ('aria-label="Daily rows"', 'aria-label="每日列"'),
    ('aria-label="Close"', 'aria-label="關閉"'),
]

JS_PATCHES = [
    (
        "if (!window.__KPI_EDIT_LEASE.tryAcquire(isJa ? '売上データ' : 'Sales Data')) {",
        "if (!window.__KPI_EDIT_LEASE.tryAcquire(isJa ? '売上データ' : (String(document.documentElement.getAttribute('lang')||'').indexOf('zh')===0 ? '銷售資料' : 'Sales Data'))) {",
    ),
    (
        "if (!window.__KPI_EDIT_LEASE.tryAcquire(isJa ? '過去売上' : 'Past Sales')) {",
        "if (!window.__KPI_EDIT_LEASE.tryAcquire(isJa ? '過去売上' : (String(document.documentElement.getAttribute('lang')||'').indexOf('zh')===0 ? '過去銷售' : 'Past Sales'))) {",
    ),
    (
        "if (!window.__KPI_EDIT_LEASE.tryAcquire(isJa ? '年次編集' : 'Annual Edit')) {",
        "if (!window.__KPI_EDIT_LEASE.tryAcquire(isJa ? '年次編集' : (String(document.documentElement.getAttribute('lang')||'').indexOf('zh')===0 ? '每日批次編輯' : 'Annual Edit'))) {",
    ),
]


def main() -> None:
    if not DST.is_file():
        raise SystemExit(f"missing {DST}")
    text = DST.read_text(encoding="utf-8")
    i = text.find('id="past-sales-modal"')
    j = text.find('id="insight-overlay"')
    if i < 0:
        raise SystemExit("past-sales-modal not found")
    if j < 0:
        j = text.find("KPI-SITE-FOOTER")
    root = text.rfind("<div", 0, i)
    head, mid, tail = text[:root], text[root:j], text[j:]

    missing = []
    for a, b in sorted(MODAL_REPLACEMENTS, key=lambda ab: -len(ab[0])):
        if a not in mid:
            missing.append(a[:90])
            continue
        mid = mid.replace(a, b)

    text2 = head + mid + tail
    for a, b in JS_PATCHES:
        if a not in text2:
            missing.append("js:" + a[:80])
        else:
            text2 = text2.replace(a, b, 1)

    # Fallback: Edit side may already be 編輯 from earlier waves
    mid_check = text2[root:j] if False else None  # noqa: keep simple
    DST.write_text(text2, encoding="utf-8")

    if missing:
        print(f"WARN missing {len(missing)} (showing 20):")
        for m in missing[:20]:
            print(" ", repr(m))

    t = DST.read_text(encoding="utf-8")
    must = [
        "過去銷售資料",
        "銷售資料",
        "過去資料編輯",
        "累計輸入銷售",
        "剩餘／輸入進度",
        "總營業日數",
        "關閉過去銷售資料",
        "關閉銷售資料",
        "儲存並關閉",
        "曜日加重",
        "月內均等",
        "每日批次編輯",
        "旺淡期%設定",
    ]
    for s in must:
        if s not in t:
            raise SystemExit(f"missing after wave4: {s}")
    print("wave4 applied:", DST.relative_to(ROOT))
    print("build_zh_tw_annual_wave4: OK")


if __name__ == "__main__":
    main()
