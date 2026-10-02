# BR-POST-PACE-ALERT-01 — Business-day vs Sales Pace Alert Visual Contract

Status: **DEFERRED / POST-LAUNCH / REDESIGN**  
Parent: post-launch (do not reopen `TRUNK-06`)  
Registered: 2026-10-02  
Priority: not raised. Do not start.

This reviews the current Home pace warning. It is not a restore. No pre-Home Business-day vs Sales pace contract was found.

## Current Home contract

Introduced in `5e7dd63` (2026-10-01), `js/kpi-home-kpi.js` `paceWarning`. Home paint of the bar itself started in `a6503ed` (2026-10-01).

gap = raw Business-day Progress − raw Sales Progress.

| gap | result |
|-----|--------|
| gap < 10 | normal |
| 10 <= gap < 20 | orange |
| gap >= 20 | red |

Sales Progress >= Business-day Progress is normal. A negative Sales Progress is clamped to 0 for this warning calculation only.

On Home, that warning overwrites the Sales Progress triangle color and the percentage color. Daily Floating Window and Insight do not. Their triangle color still follows achievement severity (`getAchievementMarkerColor`, present since `e69ada5`, 2026-03-27).

## Historical audit

evidence not found: a Business-day vs Sales pace warning before Home. The Home rule is a new specification, so a later change is a redesign of that specification, not a restore.

## Future review (not started)

- warning thresholds
- normal / orange / red
- whether the triangle color changes
- whether the percentage color changes
- a separate warning indicator
- a tooltip
- alignment with the rest of the KPN Progress UI

Do not change the current Home implementation from this note.
