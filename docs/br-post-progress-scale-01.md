# BR-POST-PROGRESS-SCALE-01 — Dynamic Progress Bar Scale

Status: **DEFERRED / POST-LAUNCH / REDESIGN**  
Parent: post-launch (do not reopen `TRUNK-06`)  
Registered: 2026-10-02  
Priority: not raised. Do not start.

This is a future redesign candidate. It does not change the current Sales Progress contract.

## Current contract (confirmed)

The Sales Progress bar in production-bound code is:

- Target 100% sits at 66.67% of the track (`width × 2/3`).
- Actual position is that target position times the achievement ratio.
- Visual maximum is 90% of the track (the right 10% stays empty).
- At 135% achievement and above, the fill and triangle share one visual position.
- The printed percent is not clamped. 150 / 200 / 300% still display as those numbers.

Same formula: Daily Floating Window (`setOverlayGraph`), Annual / Monthly Insight and Area1 (`initAllocationWidget`), the Monthly graph popover (`setGraphBarFromAchievementPercent`), and Home (`paintBar`). PL Insight year-comparison bars are a different chart.

## Historical audit

No dynamic scale was found on the Sales Progress achievement bar. `e69ada5` (2026-03-27) already fixed the 100% line at 2/3 and kept a 10% tail. `docs/annual-kpi-strip-memo.md` records that contract, including “150% and above is visually fixed.”

A different chart still uses a dynamic scale: Past Sales Analyze seasonality, `getSeasonalityChartScale` (`9ef8dba`, 2026-07-02). Documented in `docs/past-sales-floating-window-memo.md` §12.5.

- `scaleMax = max(peak, 100)`
- The 100% marker is `(100 / scaleMax) × 100%` of the track.

That seasonality chart is a reference candidate only. It is not the Sales Progress bar, and it is not evidence that the achievement bar once moved its target line left.

## Future redesign (not started)

If Actual exceeds the normal display range, a later redesign may extend the scale so that:

- the target marker moves left relative to the track
- 150 / 200 / 300% stay visually distinct
- Daily, Monthly, Annual, Insight, and Home share one contract

Do not implement from this note. Do not change the current Sales Progress contract.
