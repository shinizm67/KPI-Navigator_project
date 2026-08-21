#!/usr/bin/env python3
"""MEP path toggle tooltips + CSV disable when Annual; Past Sales view/edit tooltips."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MEP_EDIT = [
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
    ROOT / "zh-tw/app/monthly/edit/index.html",
]

ANNUAL = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "zh-tw/app/annual/index.html",
]

GUARDS_JS = (ROOT / "scripts/_kpi_edit_guards.js").read_text(encoding="utf-8")

CSV_DISABLED_CSS = """    .monthly-edit-float__csv-upload:disabled {
      opacity: 0.35;
      cursor: not-allowed;
    }
"""

MEP_PATH_SWITCH_OLD = """      function mepPathSwitchHint() {
        return t(
          '編集するには入力経路を Monthly（MEP）に切替してください',
          'To edit, switch the input path to Monthly (MEP)'
        );
      }
"""

MEP_PATH_SWITCH_NEW = """      function isMepDailySalesPathBlocked() {
        return !!(
          window.KpiYearStore &&
          typeof KpiYearStore.getDailySalesInputPath === 'function' &&
          KpiYearStore.getDailySalesInputPath() !== 'mep'
        );
      }
      function mepPathSwitchHint() {
        return t(
          '日次売上の入力経路が年次（Annual / Sales Data）側です。上部の売上入力トグルを月次（Monthly / MEP）に切り替えてください。',
          'Daily sales input is on Annual / Sales Data. Switch the sales input toggle above to Monthly (MEP).',
          '每日營業額輸入路徑在年度（Annual / Sales Data）。請將上方賣上輸入切換鈕切到月度（Monthly / MEP）。'
        );
      }
"""

MEP_PATH_SWITCH_ZH_OLD = """      function mepPathSwitchHint() {
        return t(
          '編集するには入力経路を Monthly（MEP）に切替してください',
          'To edit, switch the input path to Monthly (MEP)',
          '如要編輯，請將輸入路徑切換到 Monthly（MEP）'
        );
      }
"""

MANUAL_HINT_OLD = """      function manualInputHint() {
        if (
          window.KpiYearStore &&
          typeof KpiYearStore.getDailySalesInputPath === 'function' &&
          KpiYearStore.getDailySalesInputPath() !== 'mep'
        ) {
          return mepPathSwitchHint();
        }
        return t('手入力が必要です（セルに直接入力）', 'Manual entry — type values in the cells');
      }
"""

MANUAL_HINT_NEW = """      function manualInputHint() {
        if (isMepDailySalesPathBlocked()) {
          return mepPathSwitchHint();
        }
        return t(
          '手入力が必要です（営業日のセルに直接入力）',
          'Manual entry — type values in the business-day cells',
          '需手動輸入（請在營業日的儲存格輸入）'
        );
      }
"""

MANUAL_HINT_ZH_OLD = """      function manualInputHint() {
        if (
          window.KpiYearStore &&
          typeof KpiYearStore.getDailySalesInputPath === 'function' &&
          KpiYearStore.getDailySalesInputPath() !== 'mep'
        ) {
          return mepPathSwitchHint();
        }
        return t('手入力が必要です（セルに直接入力）', 'Manual entry — type values in the cells', '需手動輸入（請直接在儲存格輸入）');
      }
"""

STATIC_INPUT_OLD = """              } else {
                var kind = r.valueKind || 'money';
                if (kind === 'count') {
                  inp.value = fmtCount(readValue(r.id, iso));
                  inp.setAttribute('data-action', 'count-input');
                } else {
                  inp.value = fmtMoney(readValue(r.id, iso));
                  inp.setAttribute('data-action', 'money-input');
                }
                inp.setAttribute('data-row-id', r.id);
                inp.setAttribute('data-iso', iso);
                inp.setAttribute('title', manualInputHint());
              }
"""

STATIC_INPUT_NEW = """              } else {
                var kind = r.valueKind || 'money';
                var pathBlockedStatic = isMepDailySalesPathBlocked();
                if (kind === 'count') {
                  inp.value = fmtCount(readValue(r.id, iso));
                  inp.setAttribute('data-action', 'count-input');
                } else {
                  inp.value = fmtMoney(readValue(r.id, iso));
                  inp.setAttribute('data-action', 'money-input');
                }
                inp.setAttribute('data-row-id', r.id);
                inp.setAttribute('data-iso', iso);
                inp.setAttribute('data-mep-daily-input', '1');
                if (pathBlockedStatic) {
                  inp.disabled = true;
                  inp.readOnly = true;
                  inp.setAttribute('title', mepPathSwitchHint());
                } else {
                  inp.setAttribute('title', manualInputHint());
                }
              }
"""

MEP_PATH_BLOCKED_OLD = """                    var mepPathBlocked =
                      window.KpiYearStore &&
                      typeof KpiYearStore.getDailySalesInputPath === 'function' &&
                      KpiYearStore.getDailySalesInputPath() !== 'mep';
"""

MEP_PATH_BLOCKED_NEW = """                    var mepPathBlocked = isMepDailySalesPathBlocked();
"""

BIZ_BLOCKED_OLD = """              var mepPathBlockedForBiz =
                window.KpiYearStore &&
                typeof KpiYearStore.getDailySalesInputPath === 'function' &&
                KpiYearStore.getDailySalesInputPath() !== 'mep';
"""

BIZ_BLOCKED_NEW = """              var mepPathBlockedForBiz = isMepDailySalesPathBlocked();
"""

CSV_BLOCK_OLD = re.compile(
    r"        btnCsvUpload\.addEventListener\(\n"
    r"          'click',\n"
    r"          function \(ev\) \{[\s\S]*?\n"
    r"          true\n"
    r"        \);\n\n",
    re.MULTILINE,
)

SYNC_CSV_OLD = """        function syncCsvUploadTooltip() {
          var msg = isMepSalesPathActive()
            ? mepCsvText(
                '日次売上をCSV/Excel（.xlsx）で取り込みます。支出はPLの「支出CSV取込」をご利用ください。',
                'Import daily sales from CSV/Excel (.xlsx). For expenses, use PL "Expense CSV Import".',
                '可用 CSV/Excel（.xlsx）匯入每日營業額。支出請使用 PL 的「支出CSV匯入」。'
              )
            : mepCsvText(
                '現在、日次売上の入力経路が Annual / Sales Data 側です。CSV取込を使うには Monthly（MEP）へ切替してください。クリックで切替できます。',
                'Daily sales input path is currently Annual / Sales Data. Switch to Monthly (MEP) to use CSV import. Click to switch.',
                '目前每日營業額輸入路徑在 Annual / Sales Data。若要使用 CSV 匯入，請切換到 Monthly（MEP）。點擊即可切換。'
              );
          btnCsvUpload.setAttribute('title', msg);
          btnCsvUpload.setAttribute('data-tooltip', msg);
          btnCsvUpload.setAttribute('aria-label', msg);
        }
"""

SYNC_CSV_NEW = """        function syncCsvUploadTooltip() {
          var active = isMepSalesPathActive();
          var msg = active
            ? mepCsvText(
                '日次売上をCSV/Excel（.xlsx）で取り込みます。支出はPLの「支出CSV取込」をご利用ください。',
                'Import daily sales from CSV/Excel (.xlsx). For expenses, use PL "Expense CSV Import".',
                '可用 CSV/Excel（.xlsx）匯入每日營業額。支出請使用 PL 的「支出CSV匯入」。'
              )
            : mepCsvText(
                '日次売上の入力経路が年次側のため、CSV取込は利用できません。上部の売上入力トグルを月次（MEP）に切り替えてください。',
                'CSV import is unavailable while daily sales input is on Annual / Sales Data. Switch the sales input toggle above to Monthly (MEP).',
                '每日營業額輸入路徑在年度側，無法使用 CSV 匯入。請將上方賣上輸入切換鈕切到月度（MEP）。'
              );
          btnCsvUpload.disabled = !active;
          btnCsvUpload.setAttribute('title', msg);
          btnCsvUpload.setAttribute('data-tooltip', msg);
          btnCsvUpload.setAttribute('aria-label', msg);
        }
"""

COUNT_GUARD_OLD = """        } else if (action === 'count-input') {
          var rowIdC = target.getAttribute('data-row-id');
          var isoC = target.getAttribute('data-iso');
          pushUndo();
"""

COUNT_GUARD_NEW = """        } else if (action === 'count-input') {
          if (isMepDailySalesPathBlocked()) {
            buildGrid();
            return;
          }
          var rowIdC = target.getAttribute('data-row-id');
          var isoC = target.getAttribute('data-iso');
          pushUndo();
"""

MONEY_GUARD_OLD = """        } else if (action === 'money-input') {
          var rowId = target.getAttribute('data-row-id');
          var iso2 = target.getAttribute('data-iso');
          var salesPathOnly =
"""

MONEY_GUARD_NEW = """        } else if (action === 'money-input') {
          var rowId = target.getAttribute('data-row-id');
          var iso2 = target.getAttribute('data-iso');
          if (
            isMepDailySalesPathBlocked() &&
            (target.getAttribute('data-mep-daily-input') === '1' ||
              target.getAttribute('data-mep-editable') === '1')
          ) {
            buildGrid();
            return;
          }
          var salesPathOnly =
"""


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old in text:
        return text.replace(old, new, 1)
    if new.split("\n")[1].strip() in text:
        return text
    raise SystemExit(f"patch miss ({label})")


def patch_mep_edit(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    is_zh = "/zh-tw/" in str(path)

    if "function isMepDailySalesPathBlocked()" not in text:
        if is_zh:
            text = replace_once(text, MEP_PATH_SWITCH_ZH_OLD, MEP_PATH_SWITCH_NEW, "mep path switch zh")
            text = replace_once(text, MANUAL_HINT_ZH_OLD, MANUAL_HINT_NEW, "manual hint zh")
        else:
            text = replace_once(text, MEP_PATH_SWITCH_OLD, MEP_PATH_SWITCH_NEW, "mep path switch")
            text = replace_once(text, MANUAL_HINT_OLD, MANUAL_HINT_NEW, "manual hint")

    if CSV_DISABLED_CSS.strip() not in text:
        anchor = "    .monthly-edit-float__undo:disabled {"
        if anchor not in text:
            raise SystemExit("csv disabled css anchor missing")
        text = text.replace(anchor, CSV_DISABLED_CSS + anchor, 1)

    text = replace_once(text, MEP_PATH_BLOCKED_OLD, MEP_PATH_BLOCKED_NEW, "mep path blocked inline")
    text = replace_once(text, BIZ_BLOCKED_OLD, BIZ_BLOCKED_NEW, "biz path blocked")
    text = replace_once(text, STATIC_INPUT_OLD, STATIC_INPUT_NEW, "static input guard")
    text = replace_once(text, SYNC_CSV_OLD, SYNC_CSV_NEW, "sync csv tooltip")
    text = CSV_BLOCK_OLD.sub("", text, count=1)
    text = replace_once(text, MONEY_GUARD_OLD, MONEY_GUARD_NEW, "money guard")
    text = replace_once(text, COUNT_GUARD_OLD, COUNT_GUARD_NEW, "count guard")

    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def patch_annual_guards(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(r"      /\* KPI-EDIT-GUARDS \*/[\s\S]*?\}\)\(\);\n", re.MULTILINE)
    if not pattern.search(text):
        raise SystemExit(f"KPI-EDIT-GUARDS block missing: {path}")
    text = pattern.sub(GUARDS_JS.rstrip() + "\n", text, count=1)
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)} guards")


def main() -> int:
    for p in MEP_EDIT + ANNUAL:
        if not p.is_file():
            print(f"missing {p}", file=sys.stderr)
            return 1
    for p in MEP_EDIT:
        patch_mep_edit(p)
    for p in ANNUAL:
        patch_annual_guards(p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
