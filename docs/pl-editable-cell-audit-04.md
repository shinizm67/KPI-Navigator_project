# BR-LAUNCH-04 PL Editable Cell Visual Finish — Phase 1 Audit

Date: 2026-09-24  
Status: ACTIVE (audit only; no CSS / calc / save / classifier / entitlement / importer change)  
Production: `https://forge-laboratory.com/kpi-navigator`  
Viewport: 1440×900  
Plans: Demo Pro (grid), Demo Basic (redirect)  
Languages: JA / EN / ZH-TW  
Modes: Sci-Fi / Office  

Playwright + computedStyle: `scripts/_tmp_c4_pl_cell_audit.json`  
Screenshots: `scripts/_tmp_c4_shots/`  
Spec: `docs/pl-table-v1-implementation-spec.md` — **B の必須 UX「入力可能セルだけ色付き」= 未着手**  
excel/: untouched

This is not a redesign. Findings are Launch visual-contract gaps.

---

## Verdict

| Field | Value |
|-------|--------|
| Editable Cell Contract | **PARTIAL** |
| Sci-Fi | issues |
| Office | issues |
| JP | issues (CSS same as EN/ZH-TW) |
| EN | issues (CSS same as JA/ZH-TW) |
| ZH-TW | issues (live 132 monthly + 36 daily cells measured) |
| P0 | **0** |
| P1 | **5** |
| P2 | **3** |
| Human Visual Review Needed | **YES** |
| Estimated Fix Size | **SMALL** |
| BR-LAUNCH-04 | **ACTIVE** |
| Next Task | **BR-LAUNCH-04 Phase 2 Repair** (CSS visual contract only) |
| excel untouched | **YES** |

PARTIAL, not UNCLEAR: focus fill + `cursor:text` exist on monthly amount cells. Resting look does **not** tell editable from income / total / ratio / empty `—`. Spec required fill-on-editable-only is not implemented.

---

## Who can edit

| Surface | Editable? | Marker | Rest look |
|---------|-----------|--------|-----------|
| Monthly expense amount (preset + custom) | **Yes** | `contenteditable` + `data-pl-editable="1"` + class `pl-amt-cell--pl-monthly-editable` | Same cyan / `#111` as all amount text. No rest fill. Class has **no CSS**. |
| Daily expense amount | No (F2 / dblclick adjustment) | `pl-amt-cell--pl-daily-readonly` | Sci-Fi: dim cyan `rgba(88,225,243,0.45)`. Office: **same `#111` as editable**. |
| Ratio | No | `.pl-ratio-cell__text` | Same color as amounts; `cursor:default` |
| Income amounts | No | `.pl-amt-cell--income-*` | Same color; `cursor:default`; `—` or money |
| Summary Fixed / Variable / Total Expenses | No | summary rows / `--total` | Same color; totals **15px / 700** only |
| Year total | No | `--year-total` | Same color |
| Profit | No | `.pl-month-cell--profit` | Size/weight + loss color ramp |
| Row labels (non-total) | Label only (dblclick / F2) | `data-pl-label-editable="1"` | Dashed underline **hover** (amount cells have none) |
| Basic PL | Page blocked | `guardProPage` → `change_plan.html` | Intentional |

Live ZH-TW Pro after catalog hydrate: **132** monthly editable cells, **36** daily readonly, catalog **23** lines. Custom and preset share `dataRow()`.

---

## Check grid (1–15)

| # | Check | Result |
|---|--------|--------|
| 1 | Which cells editable | Monthly expense amounts only (`data-pl-editable="1"`). Labels separately. |
| 2 | Which not | Income, ratio, totals, profit, year total, daily expense, inactive catalog. |
| 3 | Distinguishable by look alone | **No at rest.** Cursor `text` vs `default` only on pointer. Totals differ by font size/weight only. |
| 4 | Border | None on rest. Focus = inset cyan 1px (Sci-Fi recipe in both modes). |
| 5 | Background | Rest transparent. Focus `#152a32` even in Office. |
| 6 | Hover | **None** on amount editable. Labels get dashed underline. |
| 7 | Focus | Exists. Sci-Fi OK-ish. Office uses Sci-Fi dark teal. No layout shift (159.5×40 rest=hover=focus). |
| 8 | Cursor | Editable `text`; daily/income/total `default`. |
| 9 | Alignment | Amounts center 13px; labels right. Shared. |
| 10 | Placeholder / zero | Empty monthly often `—` (same glyph as readonly empty). Summary can show `¥0`. Daily shows money or `—`. |
| 11 | Locked | Pro grid unlocked. Insight compare-lock is overlay, not cell chrome. |
| 12 | Disabled | N/A on Pro amounts. Daily is readonly, not disabled styling beyond dim (Sci-Fi only). |
| 13 | Basic/Pro | Basic PL redirects. No Basic editable-cell variant. |
| 14 | Sci-Fi / Office | Shared rest gap. Office additionally: daily=editable color; focus is Sci-Fi fill. |
| 15 | JP / EN / ZH-TW | Editable CSS copy-identical. No lang-specific rest/hover/focus. ZH-TW live measured; JA/EN CSS matches. |

---

## Findings

| ID | Sev | Summary |
|----|-----|---------|
| C4-01 | **P1** | Resting monthly editable amounts share color + transparent bg + no border with income, totals, ratios. Spec B UX 未着手. |
| C4-02 | **P1** | Hook class `pl-amt-cell--pl-monthly-editable` is painted by JS but has **zero CSS**. |
| C4-03 | **P1** | No `:hover` paint on `[data-pl-editable="1"]`. Labels already have hover. |
| C4-04 | **P1** | Office `:focus` uses Sci-Fi `#152a32` + cyan inset. Screenshot: dark teal cell on gray Office grid. |
| C4-05 | **P1** | Office daily-readonly loses dim: `body.office-mode .pl-amt-cell__text { color:#111 }` wins (same specificity, later). Daily looks like monthly editable. |
| C4-06 | **P2** | Empty editable and empty readonly both use `—`. Zero vs blank vs dash is not a contract. |
| C4-07 | **P2** | Label hover (dashed) vs amount hover (none) — two affordance languages. |
| C4-08 | **P2** | Cold PL before catalog hydrate: expense `tbody` empty. JA/EN have no `kpi:storeHydratedFromServer` re-render of rows (ZH-TW has amount hydrate only). Out of visual-finish repair; do not expand 04. |
| I-01 | intentional | Income / ratio / profit / year total not amount-editable (MEP rollup / computed). |
| I-02 | intentional | Daily expense readonly + F2 adjustment. |
| I-03 | intentional | Basic → `change_plan.html`. |
| I-04 | intentional | Totals not `contenteditable`. |

No P0: users can still type in monthly cells; totals are not writable. This is Launch polish of the missing “only type here” fill.

---

## Automated (Playwright)

- Pro ZH-TW Sci-Fi: 132 editable, 36 daily. Rest color `rgb(88,225,243)` identical to income/total. Daily `a=0.45`. Hover bg unchanged. Focus `rgb(21,42,50)` + inset cyan. Size 159.5×40 no shift. `overflowX=0`.
- Pro ZH-TW Office: same counts. Editable/daily/income/total all `rgb(17,17,17)`. Focus still `rgb(21,42,50)`.
- Pro JA/EN in cookie-only cold profile: expense detail not in DOM until catalog+BT (C4-08). CSS rules match ZH-TW.
- Basic JA PL: redirected to `setting/change_plan.html`.
- Static scan 3 langs: `has_monthly_editable_css=false`, `has_editable_hover=false`, `has_editable_focus=true`, `has_office_editable_rest=false`, `has_office_editable_focus=false`, `office_amt_after_daily=true`.

---

## Shared root causes

1. Spec B 「入力可能セルだけ色付き」 never implemented — editable rest inherits generic `.pl-amt-cell__text`.
2. Office `color:#111` on all amount text, with no editable rest/hover/focus override and with later-win over daily dim.
3. Amount editable contract is cursor + Sci-Fi focus only; hover/rest fill never defined (labels already have a different hover).

---

## Repair scope (Phase 2 — do not start extra branches)

CSS only on PL (JA / EN / ZH-TW):

- Rest fill/border on `[data-pl-editable="1"]` (and/or `.pl-amt-cell--pl-monthly-editable`) so monthly cells read as input.
- Hover on those cells.
- Office focus that is Office, not `#152a32`.
- Restore Office daily-readonly dim vs monthly editable.

Do **not** change: PL calculation, save, expense classification, fixed/variable, data model, entitlement, importer, Monthly (spec mentions Monthly; this branch is PL only).

Do **not** start `BR-LAUNCH-05`.

---

## Human visual review

**YES.** Rest vs total vs daily is a contrast/affordance call. Screenshots: Sci-Fi focus is the only obvious paint; Office focus looks like a Sci-Fi leftover; empty `—` matches readonly.
