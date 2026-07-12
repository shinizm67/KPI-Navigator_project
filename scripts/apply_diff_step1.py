#!/usr/bin/env python3
"""Difference Step 1 — TW diff severity CSS + Focus Bar lower class sync."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from apply_focus_tw_metrics import patch_page as patch_focus_tw  # noqa: E402

PAGES = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]

ANNUAL_PAGES = {
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
}

DIFF_CSS_MARKER = "/* KPI-TW-DIFF-SEVERITY */"

DIFF_CSS_OLD = """    .annual-daily-row__cell--neg {
      color: #ff6b6b;
    }
    .annual-daily-row__cell.kpi-fill-empty {"""

DIFF_CSS_OLD_MONTHLY = """    .annual-daily-row__cell--neg {
      color: #ff6b6b;
    }
    /* Focus Bar: SVGのみ（レイアウト検証）。Window 725 / SVG 757。 */
    .annual-daily-focus-bar-layer {"""

DIFF_CSS_NEW_MONTHLY = f"""    .annual-daily-row__cell--neg {{
      color: #ff6b6b;
    }}
    {DIFF_CSS_MARKER}
    body:not(.office-mode) .annual-daily-row__cell.tw-diff--win,
    body:not(.office-mode) .annual-daily-focus-bar-lower__cell.tw-diff--win {{
      color: #58e1f3;
    }}
    body:not(.office-mode) .annual-daily-row__cell.tw-diff--neutral,
    body:not(.office-mode) .annual-daily-focus-bar-lower__cell.tw-diff--neutral {{
      color: #58e1f3;
    }}
    .annual-daily-row__cell.tw-diff--sev-90,
    .annual-daily-focus-bar-lower__cell.tw-diff--sev-90 {{
      color: #f9a825;
    }}
    .annual-daily-row__cell.tw-diff--sev-80,
    .annual-daily-focus-bar-lower__cell.tw-diff--sev-80 {{
      color: #ef6c00;
    }}
    .annual-daily-row__cell.tw-diff--sev-70,
    .annual-daily-focus-bar-lower__cell.tw-diff--sev-70 {{
      color: #e65100;
    }}
    .annual-daily-row__cell.tw-diff--sev-60,
    .annual-daily-focus-bar-lower__cell.tw-diff--sev-60 {{
      color: #e53935;
    }}
    .annual-daily-row__cell.tw-diff--sev-50,
    .annual-daily-focus-bar-lower__cell.tw-diff--sev-50 {{
      color: #c62828;
    }}
    .annual-daily-row__cell.tw-diff--sev-below,
    .annual-daily-focus-bar-lower__cell.tw-diff--sev-below {{
      color: #b71c1c;
    }}
    /* Focus Bar: SVGのみ（レイアウト検証）。Window 725 / SVG 757。 */
    .annual-daily-focus-bar-layer {{"""

DIFF_CSS_NEW = f"""    .annual-daily-row__cell--neg {{
      color: #ff6b6b;
    }}
    {DIFF_CSS_MARKER}
    body:not(.office-mode) .annual-daily-row__cell.tw-diff--win,
    body:not(.office-mode) .annual-daily-focus-bar-lower__cell.tw-diff--win {{
      color: #58e1f3;
    }}
    body:not(.office-mode) .annual-daily-row__cell.tw-diff--neutral,
    body:not(.office-mode) .annual-daily-focus-bar-lower__cell.tw-diff--neutral {{
      color: #58e1f3;
    }}
    .annual-daily-row__cell.tw-diff--sev-90,
    .annual-daily-focus-bar-lower__cell.tw-diff--sev-90 {{
      color: #f9a825;
    }}
    .annual-daily-row__cell.tw-diff--sev-80,
    .annual-daily-focus-bar-lower__cell.tw-diff--sev-80 {{
      color: #ef6c00;
    }}
    .annual-daily-row__cell.tw-diff--sev-70,
    .annual-daily-focus-bar-lower__cell.tw-diff--sev-70 {{
      color: #e65100;
    }}
    .annual-daily-row__cell.tw-diff--sev-60,
    .annual-daily-focus-bar-lower__cell.tw-diff--sev-60 {{
      color: #e53935;
    }}
    .annual-daily-row__cell.tw-diff--sev-50,
    .annual-daily-focus-bar-lower__cell.tw-diff--sev-50 {{
      color: #c62828;
    }}
    .annual-daily-row__cell.tw-diff--sev-below,
    .annual-daily-focus-bar-lower__cell.tw-diff--sev-below {{
      color: #b71c1c;
    }}
    .annual-daily-row__cell.kpi-fill-empty {{"""

OFFICE_DIFF_CSS_OLD = """    .office-mode .annual-daily-row__cell--neg {
      color: #b00020;
    }
    /* Office: Table Window 上端から Sci-Fi と同じ top:235px。閉じ SVG = focus_bar_office_mode.svg */"""

OFFICE_DIFF_CSS_NEW = f"""    .office-mode .annual-daily-row__cell--neg {{
      color: #b00020;
    }}
    .office-mode .annual-daily-row__cell.tw-diff--win,
    .office-mode .annual-daily-focus-bar-lower__cell.tw-diff--win {{
      color: #111;
    }}
    .office-mode .annual-daily-row__cell.tw-diff--neutral,
    .office-mode .annual-daily-focus-bar-lower__cell.tw-diff--neutral {{
      color: #111;
    }}
    /* KPI-ANNUAL-TW-OFFICE-DIFF-WIN */
    body.office-mode .annual-daily-row .annual-daily-row__cell.tw-diff--win,
    body.office-mode .annual-daily-row .annual-daily-row__cell.tw-diff--neutral,
    body.office-mode .annual-daily-focus-bar-lower .annual-daily-focus-bar-lower__cell.tw-diff--win,
    body.office-mode .annual-daily-focus-bar-lower .annual-daily-focus-bar-lower__cell.tw-diff--neutral {{
      color: #111;
    }}
    .office-mode .annual-daily-row__cell.tw-diff--sev-90,
    .office-mode .annual-daily-focus-bar-lower__cell.tw-diff--sev-90 {{
      color: #e65100;
    }}
    .office-mode .annual-daily-row__cell.tw-diff--sev-80,
    .office-mode .annual-daily-focus-bar-lower__cell.tw-diff--sev-80 {{
      color: #d84315;
    }}
    .office-mode .annual-daily-row__cell.tw-diff--sev-70,
    .office-mode .annual-daily-focus-bar-lower__cell.tw-diff--sev-70 {{
      color: #c62828;
    }}
    .office-mode .annual-daily-row__cell.tw-diff--sev-60,
    .office-mode .annual-daily-focus-bar-lower__cell.tw-diff--sev-60 {{
      color: #b71c1c;
    }}
    .office-mode .annual-daily-row__cell.tw-diff--sev-50,
    .office-mode .annual-daily-focus-bar-lower__cell.tw-diff--sev-50 {{
      color: #9a0007;
    }}
    .office-mode .annual-daily-row__cell.tw-diff--sev-below,
    .office-mode .annual-daily-focus-bar-lower__cell.tw-diff--sev-below {{
      color: #7f0000;
    }}
    /* Office: Table Window 上端から Sci-Fi と同じ top:235px。閉じ SVG = focus_bar_office_mode.svg */"""

ANNUAL_FB_DIFF_LANE_MARKER = "/* KPI-ANNUAL-FB-OFFICE-TW-DIFF-LANE */"

ANNUAL_FB_DIFF_LANE_ANCHOR = """    .office-mode .annual-daily-focus-bar-lower.annual-daily-focus-bar-lower--off .annual-daily-focus-bar-lower__cell {
      color: #6a6a6a;
      border-right-color: #bdbdbd;
    }
    .office-mode .annual-daily-focus-wing-hit::before {"""

ANNUAL_FB_DIFF_LANE_BLOCK = """    .office-mode .annual-daily-focus-bar-lower.annual-daily-focus-bar-lower--off .annual-daily-focus-bar-lower__cell {
      color: #6a6a6a;
      border-right-color: #bdbdbd;
    }
    /* KPI-ANNUAL-FB-OFFICE-TW-DIFF-LANE */
    /* Focus Bar 下段: ベース色（#111 / OFF #6a6a6a）より TW diff severity を優先 */
    .office-mode .annual-daily-focus-bar-lower .annual-daily-focus-bar-lower__cell.tw-diff--sev-90,
    .office-mode .annual-daily-focus-bar-lower.annual-daily-focus-bar-lower--off .annual-daily-focus-bar-lower__cell.tw-diff--sev-90,
    body.annual-focus-bar-expanded.office-mode .annual-daily-focus-bar-lower .annual-daily-focus-bar-lower__cell.tw-diff--sev-90 {
      color: #e65100;
    }
    .office-mode .annual-daily-focus-bar-lower .annual-daily-focus-bar-lower__cell.tw-diff--sev-80,
    .office-mode .annual-daily-focus-bar-lower.annual-daily-focus-bar-lower--off .annual-daily-focus-bar-lower__cell.tw-diff--sev-80,
    body.annual-focus-bar-expanded.office-mode .annual-daily-focus-bar-lower .annual-daily-focus-bar-lower__cell.tw-diff--sev-80 {
      color: #d84315;
    }
    .office-mode .annual-daily-focus-bar-lower .annual-daily-focus-bar-lower__cell.tw-diff--sev-70,
    .office-mode .annual-daily-focus-bar-lower.annual-daily-focus-bar-lower--off .annual-daily-focus-bar-lower__cell.tw-diff--sev-70,
    body.annual-focus-bar-expanded.office-mode .annual-daily-focus-bar-lower .annual-daily-focus-bar-lower__cell.tw-diff--sev-70 {
      color: #c62828;
    }
    .office-mode .annual-daily-focus-bar-lower .annual-daily-focus-bar-lower__cell.tw-diff--sev-60,
    .office-mode .annual-daily-focus-bar-lower.annual-daily-focus-bar-lower--off .annual-daily-focus-bar-lower__cell.tw-diff--sev-60,
    body.annual-focus-bar-expanded.office-mode .annual-daily-focus-bar-lower .annual-daily-focus-bar-lower__cell.tw-diff--sev-60 {
      color: #b71c1c;
    }
    .office-mode .annual-daily-focus-bar-lower .annual-daily-focus-bar-lower__cell.tw-diff--sev-50,
    .office-mode .annual-daily-focus-bar-lower.annual-daily-focus-bar-lower--off .annual-daily-focus-bar-lower__cell.tw-diff--sev-50,
    body.annual-focus-bar-expanded.office-mode .annual-daily-focus-bar-lower .annual-daily-focus-bar-lower__cell.tw-diff--sev-50 {
      color: #9a0007;
    }
    .office-mode .annual-daily-focus-bar-lower .annual-daily-focus-bar-lower__cell.tw-diff--sev-below,
    .office-mode .annual-daily-focus-bar-lower.annual-daily-focus-bar-lower--off .annual-daily-focus-bar-lower__cell.tw-diff--sev-below,
    body.annual-focus-bar-expanded.office-mode .annual-daily-focus-bar-lower .annual-daily-focus-bar-lower__cell.tw-diff--sev-below {
      color: #7f0000;
    }
    /* Sci-Fi: 下段ベース #58e1f3 / OFF 薄シアンより TW diff severity を優先 */
    body:not(.office-mode) .annual-daily-focus-bar-lower .annual-daily-focus-bar-lower__cell.tw-diff--sev-90,
    body:not(.office-mode) .annual-daily-focus-bar-lower.annual-daily-focus-bar-lower--off .annual-daily-focus-bar-lower__cell.tw-diff--sev-90 {
      color: #f9a825;
    }
    body:not(.office-mode) .annual-daily-focus-bar-lower .annual-daily-focus-bar-lower__cell.tw-diff--sev-80,
    body:not(.office-mode) .annual-daily-focus-bar-lower.annual-daily-focus-bar-lower--off .annual-daily-focus-bar-lower__cell.tw-diff--sev-80 {
      color: #ef6c00;
    }
    body:not(.office-mode) .annual-daily-focus-bar-lower .annual-daily-focus-bar-lower__cell.tw-diff--sev-70,
    body:not(.office-mode) .annual-daily-focus-bar-lower.annual-daily-focus-bar-lower--off .annual-daily-focus-bar-lower__cell.tw-diff--sev-70 {
      color: #e65100;
    }
    body:not(.office-mode) .annual-daily-focus-bar-lower .annual-daily-focus-bar-lower__cell.tw-diff--sev-60,
    body:not(.office-mode) .annual-daily-focus-bar-lower.annual-daily-focus-bar-lower--off .annual-daily-focus-bar-lower__cell.tw-diff--sev-60 {
      color: #e53935;
    }
    body:not(.office-mode) .annual-daily-focus-bar-lower .annual-daily-focus-bar-lower__cell.tw-diff--sev-50,
    body:not(.office-mode) .annual-daily-focus-bar-lower.annual-daily-focus-bar-lower--off .annual-daily-focus-bar-lower__cell.tw-diff--sev-50 {
      color: #c62828;
    }
    body:not(.office-mode) .annual-daily-focus-bar-lower .annual-daily-focus-bar-lower__cell.tw-diff--sev-below,
    body:not(.office-mode) .annual-daily-focus-bar-lower.annual-daily-focus-bar-lower--off .annual-daily-focus-bar-lower__cell.tw-diff--sev-below {
      color: #b71c1c;
    }
    .office-mode .annual-daily-focus-wing-hit::before {"""

SCI_FI_DIFF_WIN_OLD = """    .annual-daily-row__cell.tw-diff--win,
    .annual-daily-focus-bar-lower__cell.tw-diff--win {
      color: #58e1f3;
    }
    .annual-daily-row__cell.tw-diff--neutral,
    .annual-daily-focus-bar-lower__cell.tw-diff--neutral {
      color: #58e1f3;
    }"""

SCI_FI_DIFF_WIN_NEW = """    body:not(.office-mode) .annual-daily-row__cell.tw-diff--win,
    body:not(.office-mode) .annual-daily-focus-bar-lower__cell.tw-diff--win {
      color: #58e1f3;
    }
    body:not(.office-mode) .annual-daily-row__cell.tw-diff--neutral,
    body:not(.office-mode) .annual-daily-focus-bar-lower__cell.tw-diff--neutral {
      color: #58e1f3;
    }"""

ANNUAL_TW_OFFICE_DIFF_WIN_MARKER = "/* KPI-ANNUAL-TW-OFFICE-DIFF-WIN */"

ANNUAL_TW_OFFICE_DIFF_WIN_ANCHOR = """    .office-mode .annual-daily-row__cell.tw-diff--neutral,
    .office-mode .annual-daily-focus-bar-lower__cell.tw-diff--neutral {
      color: #111;
    }
    .office-mode .annual-daily-row__cell.tw-diff--sev-90,"""

ANNUAL_TW_OFFICE_DIFF_WIN_BLOCK = """    .office-mode .annual-daily-row__cell.tw-diff--neutral,
    .office-mode .annual-daily-focus-bar-lower__cell.tw-diff--neutral {
      color: #111;
    }
    /* KPI-ANNUAL-TW-OFFICE-DIFF-WIN */
    body.office-mode .annual-daily-row .annual-daily-row__cell.tw-diff--win,
    body.office-mode .annual-daily-row .annual-daily-row__cell.tw-diff--neutral,
    body.office-mode .annual-daily-focus-bar-lower .annual-daily-focus-bar-lower__cell.tw-diff--win,
    body.office-mode .annual-daily-focus-bar-lower .annual-daily-focus-bar-lower__cell.tw-diff--neutral {
      color: #111;
    }
    .office-mode .annual-daily-row__cell.tw-diff--sev-90,"""

FOCUS_BAR_SYNC_OLD = """      function copyGroupText(row, groupClass) {
        var group = row.querySelector(groupClass);
        if (!group) return [];
        var cells = group.querySelectorAll('.annual-daily-row__cell');
        return Array.prototype.map.call(cells, function (cell) {
          return cell.textContent || '—';
        });
      }

      function writeLowerFromRowTo(target, row) {
        if (!target || !row) return;
        target.classList.toggle('annual-daily-focus-bar-lower--off', row.classList.contains('annual-daily-row--off'));
        var targetCells = target.querySelectorAll('.annual-daily-focus-bar-lower__cell');
        if (!targetCells || !targetCells.length) return;
        var base = copyGroupText(row, '.annual-daily-row__group--base');
        var monthly = copyGroupText(row, '.annual-daily-row__group--monthly');
        var annual = copyGroupText(row, '.annual-daily-row__group--annual');
        var merged = base.concat(monthly, annual);
        for (var i = 0; i < targetCells.length; i += 1) {
          targetCells[i].textContent = merged[i] != null ? merged[i] : '—';
        }
      }"""

FOCUS_BAR_SYNC_NEW = """      var TW_DIFF_FB_INDICES = { 3: true, 7: true, 11: true };
      function twDiffLevelsList() {
        if (window.__twDiffLevels && window.__twDiffLevels.length) return window.__twDiffLevels;
        return [
          'tw-diff--win',
          'tw-diff--neutral',
          'tw-diff--sev-90',
          'tw-diff--sev-80',
          'tw-diff--sev-70',
          'tw-diff--sev-60',
          'tw-diff--sev-50',
          'tw-diff--sev-below',
        ];
      }
      function syncTwDiffClasses(targetCell, sourceCell) {
        if (!targetCell || !sourceCell) return;
        var levels = twDiffLevelsList();
        for (var i = 0; i < levels.length; i++) {
          targetCell.classList.remove(levels[i]);
        }
        for (var j = 0; j < levels.length; j++) {
          if (sourceCell.classList.contains(levels[j])) {
            targetCell.classList.add(levels[j]);
          }
        }
      }
      function copyGroupCells(row, groupClass) {
        var group = row.querySelector(groupClass);
        if (!group) return [];
        var cells = group.querySelectorAll('.annual-daily-row__cell');
        return Array.prototype.map.call(cells, function (cell) {
          return { text: cell.textContent || '—', el: cell };
        });
      }

      function writeLowerFromRowTo(target, row) {
        if (!target || !row) return;
        target.classList.toggle('annual-daily-focus-bar-lower--off', row.classList.contains('annual-daily-row--off'));
        var targetCells = target.querySelectorAll('.annual-daily-focus-bar-lower__cell');
        if (!targetCells || !targetCells.length) return;
        var base = copyGroupCells(row, '.annual-daily-row__group--base');
        var monthly = copyGroupCells(row, '.annual-daily-row__group--monthly');
        var annual = copyGroupCells(row, '.annual-daily-row__group--annual');
        var merged = base.concat(monthly, annual);
        for (var i = 0; i < targetCells.length; i += 1) {
          var item = merged[i];
          if (!item) {
            targetCells[i].textContent = '—';
            continue;
          }
          targetCells[i].textContent = item.text != null ? item.text : '—';
          if (TW_DIFF_FB_INDICES[i]) syncTwDiffClasses(targetCells[i], item.el);
        }
      }"""


def patch_sci_fi_diff_scoping(text: str) -> str:
    if "body:not(.office-mode) .annual-daily-row__cell.tw-diff--win" in text:
        return text
    if SCI_FI_DIFF_WIN_OLD not in text:
        return text
    return text.replace(SCI_FI_DIFF_WIN_OLD, SCI_FI_DIFF_WIN_NEW, 1)


def patch_annual_tw_office_diff_win(text: str) -> str:
    if ANNUAL_TW_OFFICE_DIFF_WIN_MARKER in text:
        return text
    if ANNUAL_TW_OFFICE_DIFF_WIN_ANCHOR not in text:
        return text
    return text.replace(ANNUAL_TW_OFFICE_DIFF_WIN_ANCHOR, ANNUAL_TW_OFFICE_DIFF_WIN_BLOCK, 1)


def patch_css(text: str, *, annual_only: bool = False) -> str:
    if DIFF_CSS_MARKER in text:
        text = text
    elif DIFF_CSS_OLD in text:
        text = text.replace(DIFF_CSS_OLD, DIFF_CSS_NEW, 1)
    elif DIFF_CSS_OLD_MONTHLY in text:
        text = text.replace(DIFF_CSS_OLD_MONTHLY, DIFF_CSS_NEW_MONTHLY, 1)
    else:
        raise SystemExit("TW diff severity CSS patch miss")
    if not annual_only:
        return patch_sci_fi_diff_scoping(text)
    if OFFICE_DIFF_CSS_NEW.split("office-mode .annual-daily-row__cell.tw-diff--win")[0] in text:
        text = patch_annual_fb_diff_lane(text)
        text = patch_sci_fi_diff_scoping(text)
        return patch_annual_tw_office_diff_win(text)
    if OFFICE_DIFF_CSS_OLD not in text:
        raise SystemExit("office TW diff severity CSS patch miss")
    text = text.replace(OFFICE_DIFF_CSS_OLD, OFFICE_DIFF_CSS_NEW, 1)
    text = patch_annual_fb_diff_lane(text)
    text = patch_sci_fi_diff_scoping(text)
    return patch_annual_tw_office_diff_win(text)


def patch_annual_fb_diff_lane(text: str) -> str:
    if ANNUAL_FB_DIFF_LANE_MARKER in text:
        return text
    if ANNUAL_FB_DIFF_LANE_ANCHOR not in text:
        raise SystemExit("annual FB diff lane CSS anchor miss")
    return text.replace(ANNUAL_FB_DIFF_LANE_ANCHOR, ANNUAL_FB_DIFF_LANE_BLOCK, 1)


def patch_focus_bar_sync(text: str) -> str:
    if "TW_DIFF_FB_INDICES" in text:
        return text
    if FOCUS_BAR_SYNC_OLD not in text:
        raise SystemExit("Focus Bar diff sync patch miss")
    return text.replace(FOCUS_BAR_SYNC_OLD, FOCUS_BAR_SYNC_NEW, 1)


def patch_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = patch_css(text, annual_only=path in ANNUAL_PAGES)
    text = patch_focus_bar_sync(text)
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> int:
    for path in PAGES:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_focus_tw(path)
    for path in PAGES:
        patch_page(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
