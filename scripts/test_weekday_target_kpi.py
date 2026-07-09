#!/usr/bin/env python3
"""Smoke-test Phase 11 weekday KPI store APIs (Node, no browser)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from kpi_year_store_client import kpi_year_store_js  # noqa: E402


def main() -> int:
    store_js = kpi_year_store_js()
    script = f"""
{store_js}
var store = KpiYearStore.getStore();
store.timeline.dailySales['2024-01-01'] = 700;
store.timeline.dailySales['2024-01-08'] = 700;
store.timeline.dailySales['2024-01-02'] = 300;
store.timeline.dailySales['2024-01-09'] = 300;
store.timeline.businessDays['2024-01-01'] = true;
store.timeline.businessDays['2024-01-08'] = true;
store.timeline.businessDays['2024-01-02'] = true;
store.timeline.businessDays['2024-01-09'] = true;
store.years[2026] = {{
  plan: {{
    targetSales: 365000,
    monthlyHlWeights: [100,100,100,100,100,100,100,100,100,100,100,100]
  }}
}};
store.meta.operatingYear = 2026;
var baseline = KpiYearStore.getDefaultWeekdayBaselineYears(2026);
var shareMon = KpiYearStore.computeWeekdayShareAvg(2026, 0, 1, [2024]);
var kpiMon = KpiYearStore.computeDailyKpiByMonthDow(2026, 0, 1, [2024]);
console.log(JSON.stringify({{
  baseline: baseline,
  shareMon: shareMon,
  kpiMon: kpiMon,
  hasApi: typeof KpiYearStore.computeDailyTargetByIso === 'function'
}}));
"""
    proc = subprocess.run(
        ["node", "-e", script],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        print(proc.stderr or proc.stdout, file=sys.stderr)
        return 1
    data = json.loads(proc.stdout.strip().splitlines()[-1])
    assert data["hasApi"] is True
    assert data["baseline"] == [2024]
    assert isinstance(data["shareMon"], (int, float)) and data["shareMon"] > 0
    assert isinstance(data["kpiMon"], (int, float)) and data["kpiMon"] > 0
    print("ok", data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
