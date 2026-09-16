#!/usr/bin/env python3
"""Unit 5B-1: inject preset engine into PL / MEP pages only.

Does not regenerate whole pages or run site_chrome.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PL_PAGES = [
    (ROOT / "app/profit/pl/index.html", "../../../js/"),
    (ROOT / "en/app/profit/pl/index.html", "../../../../js/"),
    (ROOT / "zh-tw/app/profit/pl/index.html", "../../../../js/"),
]
MEP_PAGES = [
    (ROOT / "app/monthly/edit/index.html", "../../../js/"),
    (ROOT / "en/app/monthly/edit/index.html", "../../../../js/"),
    (ROOT / "zh-tw/app/monthly/edit/index.html", "../../../../js/"),
]

CURRENT_PRESET_FN = """      function currentPresetLines() {
        if (window.KpiPlExpensePresets && typeof window.KpiPlExpensePresets.hasDefinedPreset === 'function') {
          if (!window.KpiPlExpensePresets.hasDefinedPreset()) {
            return [];
          }
          var bt = window.KpiPlExpensePresets.resolveBusinessType();
          if (bt === 'restaurant') {
            return DEFAULT_LINES;
          }
          return window.KpiPlExpensePresets.getDefaultExpenseLines(bt);
        }
        return DEFAULT_LINES;
      }

"""

DEFAULT_BY_ID_OLD = """      function defaultById() {
        var map = {};
        DEFAULT_LINES.forEach(function (line) {
          map[line.lineId] = line;
        });
        return map;
      }"""

DEFAULT_BY_ID_NEW = """      function defaultById() {
        var map = {};
        currentPresetLines().forEach(function (line) {
          map[line.lineId] = line;
        });
        return map;
      }"""

RECONCILE_GUARD = """      function reconcileCatalogLines(oldLines) {
        if (window.KpiPlExpensePresets && typeof window.KpiPlExpensePresets.reconcileCatalogLines === 'function') {
          return window.KpiPlExpensePresets.reconcileCatalogLines(oldLines, null, currentPresetLines());
        }
"""

LOAD_LINES_OLD = """      function loadLines() {
        try {
          var raw = localStorage.getItem(CATALOG_KEY);
          if (raw) {
            var parsed = JSON.parse(raw);
            if (parsed && Array.isArray(parsed.lines) && parsed.lines.length) {
              if (parsed.schemaVersion !== CATALOG_SCHEMA_VERSION) {
                return mergeCatalogFromDefaults(parsed.lines);
              }
              return migrateLines(parsed.lines);
            }
          }
        } catch (_e) {}
        var fresh = JSON.parse(JSON.stringify(DEFAULT_LINES));
        syncOccupancyActiveFlags(fresh);
        saveLines(fresh);
        return fresh;
      }"""

LOAD_LINES_NEW = """      function loadLines() {
        try {
          var raw = localStorage.getItem(CATALOG_KEY);
          if (raw) {
            var parsed = JSON.parse(raw);
            if (parsed && Array.isArray(parsed.lines)) {
              if (parsed.lines.length) {
                if (parsed.schemaVersion !== CATALOG_SCHEMA_VERSION) {
                  return mergeCatalogFromDefaults(parsed.lines);
                }
                return migrateLines(parsed.lines);
              }
              if (window.KpiPlExpensePresets && !window.KpiPlExpensePresets.hasDefinedPreset()) {
                return parsed.lines;
              }
            }
          }
        } catch (_e) {}
        var fresh = JSON.parse(JSON.stringify(currentPresetLines()));
        syncOccupancyActiveFlags(fresh);
        saveLines(fresh);
        return fresh;
      }"""

MEP_LOAD_OLD = """      function loadPlCatalogLines() {
        try {
          var raw = localStorage.getItem(PL_CATALOG_STORAGE_KEY);
          if (!raw) return null;
          var parsed = JSON.parse(raw);
          if (!parsed || !Array.isArray(parsed.lines) || !parsed.lines.length) return null;
          return parsed.lines.filter(function (line) {
            return line && line.active !== false;
          });
        } catch (_e) {
          return null;
        }
      }"""

MEP_LOAD_NEW = """      function loadPlCatalogLines() {
        try {
          var raw = localStorage.getItem(PL_CATALOG_STORAGE_KEY);
          if (!raw) return null;
          var parsed = JSON.parse(raw);
          if (!parsed || !Array.isArray(parsed.lines)) return null;
          if (!parsed.lines.length) {
            if (window.KpiPlExpensePresets && !window.KpiPlExpensePresets.hasDefinedPreset()) {
              return parsed.lines;
            }
            return null;
          }
          return parsed.lines.filter(function (line) {
            return line && line.active !== false;
          });
        } catch (_e) {
          return null;
        }
      }"""

MEP_EMBED_OLD = """      function catalogExpenseDefsFromEmbedded(bucket) {
        return PL_LINE_CATALOG.filter(function (e) {
          return e.bucket === bucket && e.active !== false;
        });
      }"""

MEP_EMBED_NEW = """      function catalogExpenseDefsFromEmbedded(bucket) {
        if (window.KpiPlExpensePresets && !window.KpiPlExpensePresets.hasDefinedPreset()) {
          return [];
        }
        return PL_LINE_CATALOG.filter(function (e) {
          return e.bucket === bucket && e.active !== false;
        });
      }"""


def inject_scripts(text: str, js_prefix: str) -> str:
    bt = f'  <script src="{js_prefix}kpi-business-type.js"></script>\n'
    presets = f'  <script src="{js_prefix}kpi-pl-expense-presets.js"></script>\n'
    if "kpi-pl-expense-presets.js" in text:
        return text
    needle = "  <!-- KPI-CURRENCY-JS:END -->"
    if needle not in text:
        raise ValueError("KPI-CURRENCY-JS:END missing")
    insert = ""
    if "kpi-business-type.js" not in text:
        insert += bt
    insert += presets
    return text.replace(needle, insert + needle, 1)


def patch_pl(path: Path, js_prefix: str) -> None:
    text = path.read_text(encoding="utf-8")
    text = inject_scripts(text, js_prefix)
    if "function currentPresetLines()" not in text:
        if DEFAULT_BY_ID_OLD not in text:
            raise ValueError(f"defaultById missing in {path}")
        text = text.replace(DEFAULT_BY_ID_OLD, CURRENT_PRESET_FN + DEFAULT_BY_ID_NEW, 1)
    elif DEFAULT_BY_ID_OLD in text:
        text = text.replace(DEFAULT_BY_ID_OLD, DEFAULT_BY_ID_NEW, 1)
    if "KpiPlExpensePresets.reconcileCatalogLines" not in text:
        old = "      function reconcileCatalogLines(oldLines) {\n"
        if old not in text:
            raise ValueError(f"reconcileCatalogLines missing in {path}")
        text = text.replace(old, RECONCILE_GUARD, 1)
    if LOAD_LINES_OLD not in text:
        if "JSON.parse(JSON.stringify(currentPresetLines()))" not in text:
            raise ValueError(f"loadLines pattern missing in {path}")
    else:
        text = text.replace(LOAD_LINES_OLD, LOAD_LINES_NEW, 1)
    path.write_text(text, encoding="utf-8")
    print(f"patched PL {path.relative_to(ROOT)}")


def patch_mep(path: Path, js_prefix: str) -> None:
    text = path.read_text(encoding="utf-8")
    text = inject_scripts(text, js_prefix)
    if MEP_LOAD_OLD not in text:
        if "hasDefinedPreset()) {\n              return parsed.lines;" not in text:
            raise ValueError(f"MEP loadPlCatalogLines pattern missing in {path}")
    else:
        text = text.replace(MEP_LOAD_OLD, MEP_LOAD_NEW, 1)
    if MEP_EMBED_OLD not in text:
        if "hasDefinedPreset()) {\n          return [];" not in text:
            raise ValueError(f"MEP catalogExpenseDefsFromEmbedded pattern missing in {path}")
    else:
        text = text.replace(MEP_EMBED_OLD, MEP_EMBED_NEW, 1)
    path.write_text(text, encoding="utf-8")
    print(f"patched MEP {path.relative_to(ROOT)}")


def main() -> None:
    for path, prefix in PL_PAGES:
        patch_pl(path, prefix)
    for path, prefix in MEP_PAGES:
        patch_mep(path, prefix)


if __name__ == "__main__":
    main()
