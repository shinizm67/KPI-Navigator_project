# Monthly Table Window — layout implementation notes

Last updated: 2026-04-10

Product-level notes remain in `docs/monthly-page-memo.md`. This file records **pixel-level layout** implemented in `app/monthly/index.html` and `en/app/monthly/index.html`.

## Files

- JP: `app/monthly/index.html`
- EN: `en/app/monthly/index.html` (asset paths use one extra `../` vs JP)
- Annual daily table / graph / edit modal are **hidden** on Monthly (`display: none !important`) until the Monthly grid is built.
- Global nav: Annual pages link `Monthly` to `../monthly/index.html`.
- Language switch: JP Monthly `data-url-en="../../en/app/monthly/index.html"`; EN Monthly `data-url-ja="../../../app/monthly/index.html"`.

## Container `.monthly-table-window`

- Width: `1100px`
- Min height: `913px`
- Margin top: `80px` (space for vertical focus bar protruding upward)
- Horizontal centering: `margin-left/right: calc((100% - 1100px) / 2)` because parent `.annual-monthly-data` caps at ~1020px.
- No outer border (`border: 0`).
- Background: `#1F1E1E`

## Vertical focus bar (SVG)

- Assets: `images/vertical_focus_bar.svg` (Sci-Fi), `images/vertical_focus_bar_office.svg` (Office). Native SVG size `123×916`.
- Class: `.monthly-vertical-focus-bar`
- Position (relative to `.monthly-table-window`): `left: 504px`, `top: -39px`
- Rendered size: `123px × 916px` (match SVG)
- Office mode toggles SVG via existing `.office-mode` rules on `.monthly-focusbar-img-*`

### Naming (conversation)

- **Section1**: top tab area of the bar
- **Section2**: long middle
- **Section3**: bottom cap

## Month picker `.monthly-month-picker`

- Size: `113.5px × 41px`
- Position: `left: 44px`, `top: -41px` so the **bottom-left corner** meets the top of the left guide vertical at `x = 44px`.
- Style: bg `#1F1E1E`, border `0.5px solid #58E1F3`, label `13px`
- Prev/next arrows cycle months; label opens dropdown (January–December).

## Tab right vertical line (sub-pixel)

- Do **not** position with a separate element using `left: 44 + 113.5`; rounding misaligns with the tab border.
- Use `.monthly-month-picker::after`: `left: calc(100% - 0.5px)`, `top: 100%`, `width: 0.5px`, `height: 913px`, `#58E1F3` (Office: `#727575` on `::after`).

## Guide lines (`#58E1F3`, `0.5px` unless noted)

| Purpose | Class | Placement |
|--------|--------|-----------|
| Left vertical | `.monthly-table-window__guide-line` | `left: 44px`, `top: 0`, `height: 775px` |
| Horizontal left segment | `.monthly-table-window__h-line-775` | `left: 0`, `top: 775px`, `width: 505px` (stops at focus bar left) |
| Horizontal right segment | `.monthly-table-window__h-line-775-right` | `left: 627px` (= `504 + 123`), `top: 775px`, `width: calc(100% - 627px)` (to window right edge) |

## Operational hazards

- **Never** global-replace `width: 100%` → `505px` in the whole file: it breaks unrelated layout (e.g. flex children). Only set `505px` on `.monthly-table-window__h-line-775`.
- Broken CSS selectors (e.g. stray `h5px;`) can invalidate following rules; keep diffs small and verify.
