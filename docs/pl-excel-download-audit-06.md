# BR-LAUNCH-06 PL Excel Download Repair — Phase 1 Audit

Date: 2026-09-24  
Status: ACTIVE (audit only; no product change)  
Production: `https://forge-laboratory.com/kpi-navigator`  
Button: `#pl-excel-download` (JA「Excelダウンロード」/ EN「Download Excel」/ ZH-TW「下載 Excel」)  
excel/: untouched

Playwright: `scripts/_tmp_c6_pl_excel_audit.json`, `_tmp_c6_pl_excel_audit2.json`, `_tmp_c6_pl_excel_bytes.json`

This is repair of an existing user-visible control. Not a new exporter. Not MEP Excel / Raw Data / template redesign.

---

## Root cause

`downloadPlExcel()` builds a **CSV** (UTF-8 BOM), wraps it in a `Blob`, does `URL.createObjectURL`, clicks a temporary `<a download="PL_{year}.csv">`, then **immediately** `URL.revokeObjectURL(url)`.

Chrome then **navigates** to that `blob:` URL. The blob is already revoked → `chrome-error://chromewebdata/` with **ERR_FILE_NOT_FOUND**. Playwright records **zero** `download` events.

Valid CSV bytes already exist before the click (JA 8612 B, EN 8572 B, ZH-TW 8602 B). Generation is not the failure.

A vs B: **A (payload exists; download trigger + blob lifecycle broken)**, with the payload being **CSV not XLSX**.

---

## Failure layer

**Blob Lifecycle** (immediate revoke) + **Browser Navigation** (blob: treated as document load).

| Layer | Result |
|-------|--------|
| 1 Workbook generation | PASS — DOM snapshot CSV of the current PL table |
| 2 Serialization | PASS as CSV; **not** XLSX (`PK` signature absent; BOM `EF BB BF`) |
| 3 Blob creation | PASS — `text/csv;charset=utf-8`, size > 0 |
| 4 Blob URL | PASS — `blob:https://forge-laboratory.com/...` |
| 5 Download trigger | FAIL — no `download` event; `<a download>` does not keep the user on PL |
| 6 Revoke timing | FAIL — revoke in the same turn as `link.click()` |
| 7 Browser navigation | FAIL — `chrome-error://chromewebdata/` / ERR_FILE_NOT_FOUND |
| 8 Other | Separate DL-menu XLSX path (`KPI-PL-MEP-EXPORT` / `#kpi-export-pl-mep` / `XLSX.writeFile`) is **not** this button. Out of this launch repair. |

---

## Handler (all 3 langs)

```javascript
function downloadPlExcel() {
  var csv = '\uFEFF' + buildPlExportCsv();
  var blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
  var url = URL.createObjectURL(blob);
  var link = document.createElement('a');
  link.href = url;
  link.download = 'PL_' + plYear + '.csv';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
```

No `window.open`, no `location.href` assignment, no `target=_blank`. Filename: `PL_{operating/display year}.csv` (observed `PL_2026.csv`).

---

## Current workbook content (intended)

Not a multi-sheet XLSX. It is **one CSV** of the on-screen PL tables, in page language (row labels from DOM).

| Piece | Present |
|-------|---------|
| Sheet names | None (CSV) |
| Year | Filename `PL_2026.csv`; year selector is current PL year |
| Month columns | 12 × (Amount + Ratio) |
| Income rows | Yes (frozen table: store sales, streams, totals) |
| Expense rows | Summary + expense-detail body |
| Fixed / variable | Via labeled rows in the DOM dump |
| Totals | Yes |
| Ratios | Yes (paired columns) |
| Profit | Yes (frozen block) |
| Analysis | Yes (`pl-analyze-*`) |
| Custom expense lines | Included if visible in expense-detail tbody |
| Language labels | JA: `1月 金額`. EN: `Jan Amount`. ZH-TW header uses English month tokens (`Jan 金額`) + ZH row labels — existing, not this bug |

Office vs Sci-Fi: **same byte size** (JA 8612 both). Mode does not change content.

Do **not** redesign this workbook in Phase 2. Restore download of this CSV.

---

## Automated evidence

Click `#pl-excel-download` (no intercept):

- URL after click: `chrome-error://chromewebdata/`
- Body: `ERR_FILE_NOT_FOUND`
- Downloads: `[]`

Intercept `<a>.click` + skip revoke, then `fetch(blobUrl)`:

| Lang | ok | filename | size | XLSX PK | CSV BOM |
|------|----|----------|------|---------|---------|
| JA | true | PL_2026.csv | 8612 | no | yes |
| EN | true | PL_2026.csv | 8572 | no | yes |
| ZH-TW | true | PL_2026.csv | 8602 | no | yes |
| JA Office | true | PL_2026.csv | 8612 | no | yes |

CSV reopens as UTF-8 text (header + 営業日 / Business Days / 營業日數 + 店舗売上 / Store Sales / 店面營業額).

---

## Phase 2 repair (do not implement now)

SMALL CSS-free JS: stop navigating; keep blob alive until the download finishes (delay/omit `revokeObjectURL`; keep `download` on a same-document `<a>`; do not `location.assign` the blob). Do not switch this button to the MEP+PL XLSX redesign.

ZH-TW English month tokens in the CSV header are existing; leave unless they block the download fix.

---

## Verdict

| Field | Value |
|-------|--------|
| Workbook Generation | PASS |
| Serialized XLSX | FAIL (current button emits CSV) |
| Blob Creation | PASS |
| Download Trigger | FAIL |
| JP | FAIL (same bug; CSV payload PASS) |
| EN | FAIL (same) |
| ZH-TW | FAIL (same) |
| Sci-Fi | FAIL (same) |
| Office | FAIL (same; bytes identical to Sci-Fi) |
| Estimated Fix Size | **SMALL** |
| Launch Blocker | **YES** |
| Human Review Required | **NO** |
| BR-LAUNCH-06 | **ACTIVE** |
| Next Task | **BR-LAUNCH-06 Phase 2 Repair** |
| BR-LAUNCH-07 | PAUSED / REGISTER ONLY |
| excel untouched | **YES** |
