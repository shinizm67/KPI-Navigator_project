#!/usr/bin/env python3
"""Phase 2: persist monthly H/L plan weights + Cockpit read-only display."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TARGETS = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
]

HL_PLAN_OLD = """      var hlSeasonCells = document.querySelectorAll('.annual-open-table tbody td:nth-child(4)');
      function normalizeWeightInput(raw) {
        var value = parsePercentText(raw);
        if (!Number.isFinite(value)) return null;
        if (!Number.isInteger(value)) return null;
        if (value % 5 !== 0) return null;
        if (value < 60 || value > 200) return null;
        return value;
      }

      function recalcMonthlyAllocationTotal() {
        if (!monthlyAllocationWidget || !hlSeasonCells.length) return;
        var sum = 0;
        hlSeasonCells.forEach(function (cell) {
          var parsed = parsePercentText(cell.textContent);
          sum += Number.isFinite(parsed) ? parsed : 100;
        });
        var totalPercent = sum / 12;
        monthlyAllocationWidget.setPercent(totalPercent);
      }

      hlSeasonCells.forEach(function (cell) {
        cell.setAttribute('title', 'Input in 5% steps only (60% to 200%)');
        cell.addEventListener('click', function () {
          var current = parsePercentText(cell.textContent);
          var input = window.prompt('H/L Sea (%) - 5% steps only', String(Number.isFinite(current) ? current : 100));
          if (input == null) return;
          var next = normalizeWeightInput(input);
          if (next == null) {
            window.alert('Please enter an integer in 5% steps (60 to 200).');
            return;
          }
          cell.textContent = next + '%';
          recalcMonthlyAllocationTotal();
        });
      });

      recalcMonthlyAllocationTotal();"""

HL_PLAN_NEW = """      var hlSeasonCells = document.querySelectorAll('.annual-open-table tbody td:nth-child(4)');
      var hlSeasonHeader = document.querySelector('.annual-open-table thead th:nth-child(4)');
      var hlPlanReadOnlyTitle = document.documentElement.getAttribute('lang') === 'ja'
        ? '計画繁閑%（閲覧のみ。列見出しをクリックして編集）'
        : 'Plan H/L % (read-only). Click the column header to edit.';
      var hlPlanHeaderTitle = document.documentElement.getAttribute('lang') === 'ja'
        ? 'クリックで月次繁閑%を編集（5%刻み・60〜200%）'
        : 'Click to edit monthly H/L % (5% steps, 60–200%)';
      function normalizeWeightInput(raw) {
        var value = parsePercentText(raw);
        if (!Number.isFinite(value)) return null;
        if (!Number.isInteger(value)) return null;
        if (value % 5 !== 0) return null;
        if (value < 60 || value > 200) return null;
        return value;
      }
      function parseHlCellsToWeights() {
        var weights = [];
        hlSeasonCells.forEach(function (cell) {
          var parsed = parsePercentText(cell.textContent);
          weights.push(Number.isFinite(parsed) ? parsed : 100);
        });
        while (weights.length < 12) weights.push(100);
        return weights.slice(0, 12);
      }
      function applyHlWeightsToCells(weights) {
        if (!weights || weights.length !== 12) return;
        hlSeasonCells.forEach(function (cell, idx) {
          var n = Number(weights[idx]);
          cell.textContent = (Number.isFinite(n) ? n : 100) + '%';
        });
      }
      function recalcMonthlyAllocationTotal() {
        if (!monthlyAllocationWidget || !hlSeasonCells.length) return;
        var sum = 0;
        hlSeasonCells.forEach(function (cell) {
          var parsed = parsePercentText(cell.textContent);
          sum += Number.isFinite(parsed) ? parsed : 100;
        });
        var totalPercent = sum / 12;
        monthlyAllocationWidget.setPercent(totalPercent);
      }
      function refreshHlPlanFromStore() {
        if (!window.KpiYearStore || !hlSeasonCells.length) return;
        var oy = KpiYearStore.getOperatingYear();
        var weights = KpiYearStore.readMonthlyHlWeights(oy);
        if (weights) applyHlWeightsToCells(weights);
        recalcMonthlyAllocationTotal();
      }
      function saveHlWeightsToStore(weights, source) {
        if (!window.KpiYearStore) return false;
        var oy = KpiYearStore.getOperatingYear();
        return KpiYearStore.writeMonthlyHlWeights(oy, weights, { source: source || 'cockpit-plan-edit' });
      }
      function openHlWeightsEditor() {
        if (!window.KpiYearStore) return;
        var oy = KpiYearStore.getOperatingYear();
        if (KpiYearStore.isYearLocked(oy)) {
          window.alert(
            document.documentElement.getAttribute('lang') === 'ja'
              ? '確定済みの年は繁閑%を編集できません。'
              : 'Cannot edit H/L % for a locked year.'
          );
          return;
        }
        var weights = KpiYearStore.readMonthlyHlWeights(oy) || parseHlCellsToWeights();
        var monthNames =
          document.documentElement.getAttribute('lang') === 'ja'
            ? ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
            : ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        for (var i = 0; i < 12; i++) {
          var input = window.prompt(
            (document.documentElement.getAttribute('lang') === 'ja' ? '繁閑期% ' : 'H/L % ') +
              monthNames[i] +
              ' (5% steps)',
            String(weights[i])
          );
          if (input == null) return;
          var next = normalizeWeightInput(input);
          if (next == null) {
            window.alert(
              document.documentElement.getAttribute('lang') === 'ja'
                ? '5%刻みの整数（60〜200）で入力してください。'
                : 'Please enter an integer in 5% steps (60 to 200).'
            );
            return;
          }
          weights[i] = next;
        }
        if (!saveHlWeightsToStore(weights, 'cockpit-plan-edit')) return;
        applyHlWeightsToCells(weights);
        recalcMonthlyAllocationTotal();
      }
      if (window.KpiYearStore && hlSeasonCells.length) {
        var hlOy = KpiYearStore.getOperatingYear();
        var hlWeights = KpiYearStore.readMonthlyHlWeights(hlOy);
        if (!hlWeights) {
          hlWeights = parseHlCellsToWeights();
          KpiYearStore.writeMonthlyHlWeights(hlOy, hlWeights, { source: 'dom-seed' });
        }
        applyHlWeightsToCells(hlWeights);
      }
      hlSeasonCells.forEach(function (cell) {
        cell.setAttribute('title', hlPlanReadOnlyTitle);
        cell.classList.add('kpi-hl-plan-readonly');
      });
      if (hlSeasonHeader) {
        hlSeasonHeader.setAttribute('title', hlPlanHeaderTitle);
        hlSeasonHeader.classList.add('kpi-hl-plan-editable-header');
        hlSeasonHeader.style.cursor = 'pointer';
        hlSeasonHeader.addEventListener('click', openHlWeightsEditor);
      }
      document.addEventListener('kpi:annualPlanChanged', function () {
        refreshHlPlanFromStore();
      });
      window.__ANNUAL_UI = window.__ANNUAL_UI || {};
      window.__ANNUAL_UI.refreshHlPlanFromStore = refreshHlPlanFromStore;
      window.__ANNUAL_UI.openHlWeightsEditor = openHlWeightsEditor;
      recalcMonthlyAllocationTotal();"""

HL_PLAN_PATCHED_MARKER = "kpi-hl-plan-readonly"


def patch_file(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if HL_PLAN_PATCHED_MARKER in text:
        print(f"skip (already patched) {path.relative_to(ROOT)}")
        return
    if HL_PLAN_OLD not in text:
        raise ValueError(f"hl plan block not found in {path}")
    path.write_text(text.replace(HL_PLAN_OLD, HL_PLAN_NEW, 1), encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> None:
    for target in TARGETS:
        patch_file(target)


if __name__ == "__main__":
    main()
