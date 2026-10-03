# BR-POST-HOME-02 — Home / Simple Mode Redesign

Status: **LOCAL HUMAN VISUAL REVIEW COMPLETE / NOT DEPLOYED / P1**  
Parent: post-launch (do not reopen `TRUNK-06`)  
Registered: 2026-10-02  
Local visual review: 2026-10-03

`BR-POST-HOME-01` stays **PRODUCTION VERIFIED / CLOSED**. This task does not reopen it. CURRENT PATH is unchanged. Home v2 is implemented locally and the human visual review is complete. Production deploy has not been done. This status is not PRODUCTION VERIFIED.

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

Width: 900px.

## Local visual contract

Recorded from the local implementation after the 2026-10-03 human visual review. Production has not been checked.

- Top control zone: the existing Global Menu, then the existing Workspace selector, then Daily / Monthly / Annual.
- Workspace bottom to Daily top is about 60px. Daily to Monthly, and Monthly to Annual, are 50px between the card borders.
- Primary KPI row 1 is 24px. Rows 2–4 are 20px. Labels are right-aligned. Values are left-aligned. The three cards share those edges. The visual gap from the label’s right edge to the value’s left edge is 100px.
- The date text is 20px. The previous and next controls stay 16px. Today stays 12px.
- The header has no separator. The 0.5px disclosure boundary appears only while Open, under the chevron. On Monthly and Annual Open, the gap above that line and the gap below it match.
- Supporting KPI rows use the same visual rhythm as the primary KPI rows.
- Sales Progress and Business-day Progress keep their existing calculation and rendering.

## Structure

Three windows share one reference date: Daily, Monthly, Annual. Each window has Close and Open.

- Close shows the primary KPIs only.
- Open adds the supporting KPIs, progress, and the detail link.

## Disclosure Boundary / Expanded Content Separator

Candidate for a future shared KPN Expand / Collapse rule.

An expand/collapse surface should show where the always-visible default content ends and the expanded content begins. Do not leave that boundary to the user’s guess.

Home v2 draws that boundary as a 0.5px horizontal separator:

- Above the line: the primary KPIs, which stay visible when the window is closed.
- The chevron sits with that default content.
- Below the line: supporting KPIs, progress, and the other expanded content.

The separator is shown in the Open state, directly under the chevron. It is not shown in the Close state, because there is no expanded content.

Thickness is 0.5px on purpose. 1px is too visually loud for this boundary. 0.5px still marks the information break and stays quiet in the Sci-Fi UI. Sci-Fi uses the existing cyan contract. Office uses a separator tone that fits the existing Office contract. This line is an information boundary, not decoration. The header under the title and date navigation does not use this line.

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

The lower-right of each window links to that window’s detail page. Home v2 keeps the existing v1 label and destination.

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

Status: **SUPERSEDED**.

The separate pre-implementation audit was not recorded. Home v2 was implemented locally and closed by human visual review on 2026-10-03. Production deploy is still outstanding.
