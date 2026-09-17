#!/usr/bin/env python3
"""Unit 6C: patch PL / MEP expense import to lineId-first mapping without regenerating pages."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PL_PAGES = [
    (ROOT / "app/profit/pl/index.html", "../../../js/"),
    (ROOT / "en/app/profit/pl/index.html", "../../../../js/"),
    (ROOT / "zh-tw/app/profit/pl/index.html", "../../../../js/"),
]
MEP_PAGES = [
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
    ROOT / "zh-tw/app/monthly/edit/index.html",
]

SCRIPT_NEEDLE = "kpi-csv-templates.js"

LOAD_OLD = """        function loadCatalogLines() {
          if (typeof window.__plGetCatalogLines === 'function') {
            try {
              var viaApi = window.__plGetCatalogLines();
              if (Array.isArray(viaApi)) {
                return viaApi.filter(function (l) { return l && l.lineId && l.active !== false; });
              }
            } catch (_e0) {}
          }
          try {
            var raw = localStorage.getItem(CATALOG_KEY);
            if (!raw) return [];
            var parsed = JSON.parse(raw);
            var lines = parsed && Array.isArray(parsed.lines) ? parsed.lines : [];
            return lines.filter(function (l) { return l && l.lineId && l.active !== false; });
          } catch (_e) {
            return [];
          }
        }"""

LOAD_NEW = """        function isImportableLine(l) {
          if (window.KpiExpenseCsvImport && typeof window.KpiExpenseCsvImport.isImportableLine === 'function') {
            return window.KpiExpenseCsvImport.isImportableLine(l);
          }
          return !!(l && l.lineId && l.active !== false && !l.presetOrphan);
        }
        function looksLikeLineId(raw) {
          if (window.KpiExpenseCsvImport && typeof window.KpiExpenseCsvImport.looksLikeLineId === 'function') {
            return window.KpiExpenseCsvImport.looksLikeLineId(raw);
          }
          return /^exp_[a-z0-9_]+$/i.test(String(raw || '').trim());
        }
        function loadCatalogLines() {
          if (typeof window.__plGetCatalogLines === 'function') {
            try {
              var viaApi = window.__plGetCatalogLines();
              if (Array.isArray(viaApi)) {
                return viaApi.filter(isImportableLine);
              }
            } catch (_e0) {}
          }
          try {
            var raw = localStorage.getItem(CATALOG_KEY);
            if (!raw) return [];
            var parsed = JSON.parse(raw);
            var lines = parsed && Array.isArray(parsed.lines) ? parsed.lines : [];
            return lines.filter(isImportableLine);
          } catch (_e) {
            return [];
          }
        }"""

RESOLVER_OLD = """        function buildLabelIndex(lines) {
          var idx = {};
          lines.forEach(function (l) {
            [l.labelJa, l.labelEn, l.lineId].forEach(function (label) {
              var k = normText(label);
              if (k && !idx[k]) idx[k] = l;
            });
          });
          return idx;
        }
        /** resolver(displayName) -> line | null (catalog label first, then alias). */
        function makeResolver(lines, aliases) {
          var idx = buildLabelIndex(lines);
          var byId = {};
          lines.forEach(function (l) { byId[String(l.lineId)] = l; });
          return function (display) {
            var k = normText(display);
            if (idx[k]) return idx[k];
            var aid = aliases && aliases[k];
            if (aid && byId[String(aid)]) return byId[String(aid)];
            return null;
          };
        }"""

RESOLVER_NEW = """        function buildLabelIndex(lines) {
          var idx = {};
          (lines || []).forEach(function (l) {
            if (!isImportableLine(l)) return;
            [l.labelJa, l.labelEn, l.labelZh, l.labelZhTw].forEach(function (label) {
              var k = normText(label);
              if (k && !idx[k]) idx[k] = l;
            });
          });
          return idx;
        }
        /** resolver: lineId first, then current catalog label, then alias. */
        function makeResolver(lines, aliases) {
          if (window.KpiExpenseCsvImport && typeof window.KpiExpenseCsvImport.makeResolver === 'function') {
            return window.KpiExpenseCsvImport.makeResolver(lines, aliases);
          }
          var importable = (lines || []).filter(isImportableLine);
          var idx = buildLabelIndex(importable);
          var byId = {};
          var byIdNorm = {};
          importable.forEach(function (l) {
            var id = String(l.lineId);
            byId[id] = l;
            byIdNorm[normText(id)] = l;
          });
          return function (display) {
            var raw = String(display == null ? '' : display).trim();
            if (!raw) return null;
            if (window.KpiExpenseCsvImport && window.KpiExpenseCsvImport.isHeaderItemToken &&
                window.KpiExpenseCsvImport.isHeaderItemToken(raw)) return null;
            if (byId[raw]) return byId[raw];
            var k = normText(raw);
            if (byIdNorm[k]) return byIdNorm[k];
            if (idx[k] && !byIdNorm[k]) return idx[k];
            var aid = aliases && aliases[k];
            if (aid && byId[String(aid)]) return byId[String(aid)];
            return null;
          };
        }"""

PLAN_SKIP_OLD = """            var date = normDate(row[dateCol]);
            var item = String(row[itemCol] == null ? '' : row[itemCol]).trim();
            var amount = parseAmount(row[amtCol]);
            if (!date || !item) { skippedNoData++; continue; }"""

PLAN_SKIP_NEW = """            var date = normDate(row[dateCol]);
            var item = String(row[itemCol] == null ? '' : row[itemCol]).trim();
            var amount = parseAmount(row[amtCol]);
            if (!date || !item) { skippedNoData++; continue; }
            if (window.KpiExpenseCsvImport && window.KpiExpenseCsvImport.isHeaderItemToken &&
                window.KpiExpenseCsvImport.isHeaderItemToken(item)) {
              skippedNoData++;
              continue;
            }"""

FUZZY_OLD = """            // 名寄せ候補: pre-select the closest catalog line (user can override).
            var suggest = bestCatalogMatch(info.display, lines);"""

FUZZY_NEW = """            // 名寄せ候補: labels only. Never auto-assign unknown machine keys.
            var suggest = looksLikeLineId(info.display) ? null : bestCatalogMatch(info.display, lines);"""

EXPORT_OLD = """          makeResolver: makeResolver,"""

EXPORT_NEW = """          makeResolver: makeResolver,
          looksLikeLineId: looksLikeLineId,
          isImportableLine: isImportableLine,"""

MEP_DETECT_OLD = """            if (dateCol < 0 && (h === '日付' || h === 'date' || h === '年月日' || h === '年月')) dateCol = i;
            else if (itemCol < 0 && (h === '費目' || h === '項目' || h === '科目' || h === 'item' || h === 'category' || h === 'name')) itemCol = i;
            else if (amtCol < 0 && (h === '金額' || h === 'amount' || h === 'value' || h === 'cost' || h === 'price')) amtCol = i;
          }
          if (dateCol >= 0 && itemCol >= 0 && amtCol >= 0) return { dateCol: dateCol, itemCol: itemCol, amtCol: amtCol, start: 1 };
          return { dateCol: 0, itemCol: 1, amtCol: 2, start: 1 };"""

MEP_DETECT_NEW = """            if (dateCol < 0 && (h === '日付' || h === 'date' || h === '年月日' || h === '年月' || h === 'month' || h === 'day' || h === 'ym' || h === 'ymd')) dateCol = i;
            else if (itemCol < 0 && (h === '費目' || h === '項目' || h === '科目' || h === 'item' || h === 'category' || h === 'name' || h === 'lineid')) itemCol = i;
            else if (amtCol < 0 && (h === '金額' || h === 'amount' || h === 'value' || h === 'cost' || h === 'price')) amtCol = i;
          }
          if (dateCol >= 0 && itemCol >= 0 && amtCol >= 0) return { dateCol: dateCol, itemCol: itemCol, amtCol: amtCol, start: 1 };
          var fallbackAmt = ((rows[0] || []).length >= 4) ? 3 : 2;
          return { dateCol: dateCol === -1 ? 0 : dateCol, itemCol: itemCol === -1 ? 1 : itemCol, amtCol: amtCol === -1 ? fallbackAmt : amtCol, start: 1 };"""

MEP_MAP_OLD = """        function catalogLineMap() {
          var map = {};
          var all = []
            .concat(state.fixedItems || [])
            .concat(state.variableItems || []);
          all.forEach(function (row) {
            if (!row || !row.lineId) return;
            map[normText(row.labelJa)] = row;
            map[normText(row.labelEn)] = row;
            map[normText(row.lineId)] = row;
          });
          return map;
        }"""

MEP_MAP_NEW = """        function catalogLineMap() {
          var all = []
            .concat(state.fixedItems || [])
            .concat(state.variableItems || []);
          if (window.KpiExpenseCsvImport && typeof window.KpiExpenseCsvImport.makeResolver === 'function') {
            var resolve = window.KpiExpenseCsvImport.makeResolver(all, {});
            return { resolve: resolve };
          }
          var map = {};
          var byId = {};
          all.forEach(function (row) {
            if (!row || !row.lineId || row.active === false || row.presetOrphan) return;
            byId[String(row.lineId)] = row;
            byId[normText(row.lineId)] = row;
            [row.labelJa, row.labelEn, row.labelZh, row.labelZhTw].forEach(function (label) {
              var k = normText(label);
              if (k && !map[k] && !byId[k]) map[k] = row;
            });
          });
          return {
            resolve: function (item) {
              var raw = String(item == null ? '' : item).trim();
              if (!raw) return null;
              if (byId[raw]) return byId[raw];
              var k = normText(raw);
              if (byId[k]) return byId[k];
              return map[k] || null;
            }
          };
        }"""

MEP_RESOLVE_OLD = """            var line = labelMap[normText(item)];
            if (!line) { skipped++; continue; }
            var year = Number(date.slice(0, 4));
            if (!Number.isFinite(year)) { skipped++; continue; }
            var amt = parseAmount(row[cols.amtCol]);
            var style = line.resolvedInputStyle || line.inputStyle || 'monthly';
            if (style === 'daily' && date.length === 10) {"""

MEP_RESOLVE_NEW = """            var line = labelMap.resolve ? labelMap.resolve(item) : labelMap[normText(item)];
            if (!line) { skipped++; continue; }
            var year = Number(date.slice(0, 4));
            if (!Number.isFinite(year)) { skipped++; continue; }
            var amt = parseAmount(row[cols.amtCol]);
            var style = line.resolvedInputStyle || line.inputStyle || 'monthly';
            if (style === 'daily' && date.length !== 10) { skipped++; continue; }
            if (style === 'daily' && date.length === 10) {"""


def inject_script(text: str, prefix: str) -> str:
    tag = f'<script src="{prefix}kpi-expense-csv-import.js"></script>'
    if "kpi-expense-csv-import.js" in text:
        return text
    needle = f'<script src="{prefix}kpi-csv-templates.js"></script>'
    if needle not in text:
        raise ValueError(f"csv-templates script missing for prefix {prefix}")
    return text.replace(needle, needle + "\n    " + tag, 1)


def replace_once(text: str, old: str, new: str, label: str, path: Path) -> str:
    if old not in text:
        if new in text:
            return text
        raise ValueError(f"{label} missing in {path}")
    if new in text:
        return text
    return text.replace(old, new, 1)


def patch_pl(path: Path, js_prefix: str) -> bool:
    original = path.read_text(encoding="utf-8")
    text = inject_script(original, js_prefix)
    text = replace_once(text, LOAD_OLD, LOAD_NEW, "PL loadCatalogLines", path)
    text = replace_once(text, RESOLVER_OLD, RESOLVER_NEW, "PL makeResolver", path)
    text = replace_once(text, PLAN_SKIP_OLD, PLAN_SKIP_NEW, "PL buildPlan skip", path)
    text = replace_once(text, FUZZY_OLD, FUZZY_NEW, "PL unmatched fuzzy", path)
    text = replace_once(text, EXPORT_OLD, EXPORT_NEW, "PL export", path)
    if text == original:
        return False
    path.write_text(text, encoding="utf-8")
    return True


def patch_mep(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    m = re.search(r'<script src="([^"]*/)kpi-csv-templates\.js"></script>', original)
    if not m:
        raise ValueError(f"csv-templates missing in {path}")
    text = inject_script(original, m.group(1))
    text = replace_once(text, MEP_DETECT_OLD, MEP_DETECT_NEW, "MEP detectCols", path)
    text = replace_once(text, MEP_MAP_OLD, MEP_MAP_NEW, "MEP catalogLineMap", path)
    text = replace_once(text, MEP_RESOLVE_OLD, MEP_RESOLVE_NEW, "MEP applyExpenseRows", path)
    if text == original:
        return False
    path.write_text(text, encoding="utf-8")
    return True


def main() -> int:
    changed = 0
    for path, prefix in PL_PAGES:
        if patch_pl(path, prefix):
            print(f"patched {path.relative_to(ROOT).as_posix()}")
            changed += 1
        else:
            print(f"unchanged {path.relative_to(ROOT).as_posix()}")
    for path in MEP_PAGES:
        if patch_mep(path):
            print(f"patched {path.relative_to(ROOT).as_posix()}")
            changed += 1
        else:
            print(f"unchanged {path.relative_to(ROOT).as_posix()}")
    print(f"pages patched={changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
