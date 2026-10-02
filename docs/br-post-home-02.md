# BR-POST-HOME-02 — Home / Simple Mode Redesign

Status: **DEFERRED / POST-LAUNCH / P1 / REGISTER ONLY**  
Parent: post-launch (do not reopen `TRUNK-06`)  
Registered: 2026-10-02  
First Action: H2-1 — Home v2 Pre-Implementation Audit (**NOT STARTED**)

`BR-POST-HOME-01` stays **PRODUCTION VERIFIED / CLOSED**. This task does not reopen it. CURRENT PATH is unchanged. H2-1 has not started. No implementation.

## Product role

- Initial Setup = do not get lost the first time.
- Home = do not get lost in daily operation.
- Full KPN = detail analysis.

Home v2 is not an edit screen. It is the entry that shows the current Daily, Monthly, and Annual state on one screen.

## Language

Global Menu:

| Locale | Label |
|--------|-------|
| JP | ホーム |
| EN | Home |
| ZH-TW | 首頁 |

The JP Global Menu does not use the word "Home".

## Design source

Shin’s latest PNG is the Home v2 UI source. Card width, Close / Open heights, and the placement of KPI rows, progress, and the detail link come from that PNG.

The red dimension lines, red px numbers, and red guide marks in the PNG are design annotation. They are not part of the UI. Implementation uses only the size, gap, alignment, typography, and position those notes indicate.

## Dimensions

| Window | Close | Open |
|--------|-------|------|
| Daily | 360px | 650px |
| Monthly | 360px | 985px |
| Annual | same structure as Monthly | same structure as Monthly |

Width: 1000px.

## Structure

Three windows share one reference date: Daily, Monthly, Annual. Each window has Close and Open.

- Close shows the primary KPIs only.
- Open adds the supporting KPIs, progress, and the detail link.

## Close

Daily:

- Daily Actual Sales
- Daily Target Sales
- Difference
- Achievement %

Monthly and Annual:

- Cumulative Actual Sales
- Cumulative Target Sales
- Difference
- Achievement %

## Open

Daily Open follows the PNG.

Monthly and Annual Open candidates:

- Final Target
- Required Revenue
- Remaining Business Days
- Daily Required Sales
- Business-day Progress
- Sales Progress
- Detail navigation

## Sales Progress

Use the existing KPN Sales Progress contract. Home v2 does not redesign the scale.

- Green fill = Actual.
- Yellow vertical marker = Target 100%.
- Triangle = Actual position.
- The existing fixed-scale contract stays.

Only the values change by period:

| Window | Values |
|--------|--------|
| Daily | Daily Actual / Daily Target |
| Monthly | Cumulative Actual / Cumulative Target |
| Annual | Cumulative Actual / Cumulative Target |

Dynamic scale work stays in `BR-POST-PROGRESS-SCALE-01`. Do not mix it into this task.

## Business-day Progress

Home v1 reuses the Sales `paintBar`, so a yellow 100% marker appears on the business-day bar. Home v2’s working proposal is:

- Bright green = elapsed business-day progress.
- Dark track = remaining business-day portion.
- Triangle = current / selected business-day position.
- Yellow target marker on this bar = remove candidate.

The Sales Progress yellow marker stays.

## Pace alert

Home v1 already warns from the gap between Business-day Progress and Sales Progress. Home v2 does not do a large visual redesign of that warning. The visual contract stays in `BR-POST-PACE-ALERT-01`.

## Color

Sci-Fi primary colors:

- Cyan `#58E1F3`
- Green `#0F9403`

Do not add another primary color. The existing yellow target marker is the existing Progress contract, not a new primary color. Office mode keeps the existing Office contract.

## Global Menu

Home stays in the Global Menu, with the labels above. At the 1200px minimum viewport it must not overflow or overlap. Before shrinking the Forge Laboratory logo, adjust left padding, margin, and the logo-to-menu gap.

## Detail navigation

The lower-right of each window links to that window’s detail page. The label and the destination are not decided. Do not fix them as "Go to Annual" or any other wording.

## Implementation principle

- Do not build a Home-only KPI engine.
- Reuse the existing Daily, Monthly, and Annual calculations.
- Do not copy the data source.
- Home is a presentation layer.
- Home does not edit, as a rule.
- Send detail work to the existing pages.
- Sci-Fi / Office parity.
- JP / EN / ZH-TW parity.

## Task separation

| Task | Relation |
|------|----------|
| `BR-POST-HOME-01` | PRODUCTION VERIFIED / CLOSED. Do not change. |
| `BR-POST-PROGRESS-SCALE-01` | Dynamic Progress Scale redesign. Not part of Home v2. |
| `BR-POST-PACE-ALERT-01` | Pace Alert visual redesign. Not part of Home v2. |
| Annual Target Revision / Reforecast | Separate task. Not part of Home v2. |

## H2-1 — Home v2 Pre-Implementation Audit

Status: **NOT STARTED**.

When started, the audit covers the current Home v1 DOM / JS / CSS, Global Menu, 1200px viewport, JP / EN / ZH-TW, Sci-Fi / Office, the shared reference date, existing KPI data sources, Close / Open implementation options, how far Monthly and Annual can share one structure, geometry differences from the PNG, and the candidate files.
