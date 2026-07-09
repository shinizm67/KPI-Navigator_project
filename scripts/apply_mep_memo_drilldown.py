#!/usr/bin/env python3
"""MEP memo grid → Daily Notes drill-down (preview cell + row focus)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
]

DRILLDOWN_JS = (ROOT / "scripts/_mep_memo_drilldown.js").read_text(encoding="utf-8")
MARKER = "/* MEP-MEMO-DRILLDOWN */"

CSS_ANCHOR = """    .monthly-edit-float__memo-flag-btn[data-tooltip]:hover::after,
    .monthly-edit-float__memo-flag-btn[data-tooltip]:focus-visible::after {"""

CSS_NEW = """    .monthly-edit-float__memo-flag-btn[data-tooltip]:hover::after,
    .monthly-edit-float__memo-flag-btn[data-tooltip]:focus-visible::after {"""

CSS_INSERT = """
    /* MEP-MEMO-DRILLDOWN-CSS */
    .monthly-edit-float__memo-preview-btn {
      display: block;
      width: 100%;
      max-width: 100%;
      min-height: var(--mef-row-h);
      margin: 0;
      padding: 4px 6px;
      border: 0;
      background: transparent;
      color: var(--mef-cyan);
      font: inherit;
      font-size: 11px;
      line-height: 1.25;
      text-align: center;
      cursor: pointer;
      box-sizing: border-box;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .monthly-edit-float__memo-preview-btn:hover,
    .monthly-edit-float__memo-preview-btn:focus-visible {
      outline: 1px solid rgba(88, 225, 243, 0.55);
      outline-offset: -1px;
      color: #9ef6ff;
    }
    .monthly-edit-float__memo-preview-btn--empty {
      color: rgba(88, 225, 243, 0.35);
    }
    body.office-mode .monthly-edit-float__memo-preview-btn {
      color: #1565c0;
    }
    body.office-mode .monthly-edit-float__memo-preview-btn--empty {
      color: rgba(21, 101, 192, 0.35);
    }
"""

MEMO_ROW_OLD = """          } else if (r.type === 'memoRow') {
            labelInfo.label = rowLabel(r.row);
            labelInfo.rowRef = r.row;
            labelInfo.manualInput = true;
            isoList.forEach(function (iso) {
              var td = document.createElement('td');
              td.className = cellInactiveClass(iso).trim();
              var inp = document.createElement('input');
              inp.type = 'text';
              inp.className = 'monthly-edit-float__input';
              inp.disabled = !bizDayByIso[iso];
              inp.value = readMemo(r.row.id, iso);
              inp.setAttribute('data-action', 'memo-input');
              inp.setAttribute('data-row-id', r.row.id);
              inp.setAttribute('data-iso', iso);
              td.appendChild(inp);
              if (bizDayByIso[iso]) syncMemoInputTdFill(inp);
              tr.appendChild(td);
            });"""

MEMO_ROW_NEW = """          } else if (r.type === 'memoRow') {
            labelInfo.label = rowLabel(r.row);
            labelInfo.rowRef = r.row;
            labelInfo.manualInput = false;
            isoList.forEach(function (iso) {
              var td = document.createElement('td');
              td.className = cellInactiveClass(iso).trim();
              if (bizDayByIso[iso]) {
                var rawMemo = readMemo(r.row.id, iso);
                var btnMemo = document.createElement('button');
                btnMemo.type = 'button';
                btnMemo.className = 'monthly-edit-float__memo-preview-btn';
                if (!String(rawMemo || '').trim()) {
                  btnMemo.classList.add('monthly-edit-float__memo-preview-btn--empty');
                }
                btnMemo.textContent = formatMemoCellPreview(rawMemo);
                btnMemo.setAttribute('data-memo-full', rawMemo);
                btnMemo.setAttribute('data-action', 'memo-open-row');
                btnMemo.setAttribute('data-row-id', r.row.id);
                btnMemo.setAttribute('data-iso', iso);
                btnMemo.setAttribute(
                  'aria-label',
                  t(
                    rowLabel(r.row) + 'のメモを開く（' + iso + '）',
                    'Open ' + rowLabel(r.row) + ' memo (' + iso + ')'
                  )
                );
                btnMemo.setAttribute(
                  'title',
                  t(
                    'クリックで日次メモを開く',
                    'Click to open Daily Notes'
                  )
                );
                td.appendChild(btnMemo);
                syncMemoPreviewTdFill(btnMemo);
              }
              tr.appendChild(td);
            });"""

CLICK_OLD = """        } else if (action === 'memo-open') {
          openMemoForIso(btn.getAttribute('data-iso'));
        } else if (action === 'add-row') {"""

CLICK_NEW = """        } else if (action === 'memo-open') {
          openMemoForIso(btn.getAttribute('data-iso'));
        } else if (action === 'memo-open-row') {
          openMemoForIso(
            btn.getAttribute('data-iso'),
            false,
            btn.getAttribute('data-row-id')
          );
        } else if (action === 'add-row') {"""

BUILD_GRID_ANCHOR = """      function buildGrid() {
        flushPendingMemoEditsFromDom();"""


def patch_file(path: Path) -> None:
    text = path.read_text(encoding="utf-8")

    if "MEP-MEMO-DRILLDOWN-CSS" not in text:
        if CSS_ANCHOR not in text:
            raise SystemExit(f"CSS anchor missing in {path}")
        # Insert drilldown CSS before memo-flag tooltip block
        idx = text.find(CSS_ANCHOR)
        text = text[:idx] + CSS_INSERT + "\n" + text[idx:]

    if MARKER not in text:
        if BUILD_GRID_ANCHOR not in text:
            raise SystemExit(f"buildGrid anchor missing in {path}")
        text = text.replace(
            BUILD_GRID_ANCHOR,
            DRILLDOWN_JS.rstrip() + "\n" + BUILD_GRID_ANCHOR,
            1,
        )

    if "data-action', 'memo-open-row'" not in text and 'data-action", "memo-open-row"' not in text:
        if MEMO_ROW_OLD not in text:
            if "memo-open-row" in text:
                pass  # already patched
            else:
                raise SystemExit(f"memoRow block missing in {path}")
        else:
            text = text.replace(MEMO_ROW_OLD, MEMO_ROW_NEW, 1)

    if "action === 'memo-open-row'" not in text:
        if CLICK_OLD not in text:
            if "memo-open-row" in text:
                pass
            else:
                raise SystemExit(f"click handler anchor missing in {path}")
        else:
            text = text.replace(CLICK_OLD, CLICK_NEW, 1)

    path.write_text(text, encoding="utf-8")
    print(f"patched {path.relative_to(ROOT)}")


def main() -> int:
    for path in TARGETS:
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 1
        patch_file(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
