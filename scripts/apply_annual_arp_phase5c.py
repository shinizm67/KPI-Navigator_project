#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARP-5c: 年跨ぎ着地の「粘り」を短縮（トン→ん→パッ化）

対象:
  - app/annual/index.html
  - en/app/annual/index.html

変更:
  - crossYearByEdge の idx>=0 ブロックを、固定 160ms 待機から
    「着地検知(waitForVerticalScrollSettle) + 短い保持(48ms)」へ変更。
  - finalize を one-shot 化して二重実行を防止。

狙い:
  - 境界で止まった後の「んん〜」を短縮し、跨ぎを機敏にする。

冪等:
  - KPI-ARP-PHASE5C が含まれていれば再適用しない。
"""

from pathlib import Path

FILES = [
    "app/annual/index.html",
    "en/app/annual/index.html",
]

MARKER = "KPI-ARP-PHASE5C"

OLD_BLOCK = """        if (idx >= 0) {
          var target = getScrollTopForRowIndex(idx);
          /* KPI-ARP-PHASE2B: 慣性スクロールを打ち消して境界日に確実に着地 */
          tableScroll.scrollTop = target;
          requestAnimationFrame(function () {
            tableScroll.scrollTop = target;
            requestAnimationFrame(function () {
              tableScroll.scrollTop = target;
            });
          });
          setTimeout(function () {
            snapping = false;
            syncDailyDateFromFocusedRowForIndex(idx);
            __arpDeferredYearSync();
            /* KPI-ARP-PHASE3: 年跨ぎ後に Focus Bar 行を確実に同期 */
            if (typeof window.__refreshAnnualFocusBarLower === 'function') {
              window.__refreshAnnualFocusBarLower();
            }
          }, 160);
        } else {"""

NEW_BLOCK = """        if (idx >= 0) {
          var target = getScrollTopForRowIndex(idx);
          /* KPI-ARP-PHASE2B: 慣性スクロールを打ち消して境界日に確実に着地 */
          tableScroll.scrollTop = target;
          var __crossFinalized = false;
          function __finalizeCrossLanding() {
            if (__crossFinalized) return;
            __crossFinalized = true;
            snapping = false;
            syncDailyDateFromFocusedRowForIndex(idx);
            __arpDeferredYearSync();
            /* KPI-ARP-PHASE3: 年跨ぎ後に Focus Bar 行を確実に同期 */
            if (typeof window.__refreshAnnualFocusBarLower === 'function') {
              window.__refreshAnnualFocusBarLower();
            }
          }
          requestAnimationFrame(function () {
            tableScroll.scrollTop = target;
            requestAnimationFrame(function () {
              tableScroll.scrollTop = target;
              /* KPI-ARP-PHASE5C: 着地検知後に短い保持のみで解除（固定160msを廃止） */
              waitForVerticalScrollSettle(target, function () {
                setTimeout(__finalizeCrossLanding, 48);
              });
            });
          });
        } else {"""


def apply_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        print(f"  SKIP (already applied): {path}")
        return False
    cnt = text.count(OLD_BLOCK)
    if cnt != 1:
        raise SystemExit(f"  ERROR in {path}: crossYearByEdge block expected 1, found {cnt}")
    text = text.replace(OLD_BLOCK, NEW_BLOCK, 1)
    path.write_text(text, encoding="utf-8")
    print(f"  OK: {path}")
    return True


def main():
    root = Path(__file__).resolve().parent.parent
    changed = 0
    for rel in FILES:
        p = root / rel
        if apply_file(p):
            changed += 1
    print(f"Done. {changed} file(s) changed.")


if __name__ == "__main__":
    main()
