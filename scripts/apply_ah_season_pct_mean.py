#!/usr/bin/env python3
"""Step AH: reference seasonality = equal-weight mean of each year's monthlyPct.

H/L initial values snap that same mean to 5%. Does not change user-edited H/L.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STORE_HTML = [
    ROOT / "app/annual/index.html",
    ROOT / "en/app/annual/index.html",
    ROOT / "zh-tw/app/annual/index.html",
    ROOT / "app/monthly/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "zh-tw/app/monthly/index.html",
    ROOT / "app/monthly/edit/index.html",
    ROOT / "en/app/monthly/edit/index.html",
    ROOT / "zh-tw/app/monthly/edit/index.html",
]

AVG_OLD = """        function computeAverageSeasonalityPct(operatingYear, maxYears) {
          var eligible = listEligiblePastYearsForBaseline(operatingYear, maxYears);
          if (!eligible.length) return null;
          var nYears = eligible.length;
          var sumBaseline = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
          var sumActual = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
          var hasComponents = true;
          eligible.forEach(function (item) {
            var obs = item.observed;
            if (
              !obs ||
              !obs.monthlySales ||
              obs.monthlySales.length !== 12 ||
              !obs.monthlyBizDays ||
              obs.monthlyBizDays.length !== 12
            ) {
              hasComponents = false;
              return;
            }
            var dailyAvg =
              obs.totalBusinessDays > 0 && obs.annualSales != null
                ? Number(obs.annualSales) / obs.totalBusinessDays
                : 0;
            for (var m = 0; m < 12; m++) {
              var baseline = dailyAvg * Number(obs.monthlyBizDays[m] || 0);
              sumBaseline[m] += baseline;
              sumActual[m] += Number(obs.monthlySales[m] || 0);
            }
          });
          var months = [];
          if (hasComponents) {
            for (var mi = 0; mi < 12; mi++) {
              var avgBaseline = sumBaseline[mi] / nYears;
              var avgActual = sumActual[mi] / nYears;
              months.push(
                avgBaseline > 0
                  ? Math.round((avgActual / avgBaseline) * 10000) / 100
                  : null
              );
            }
          } else {
            for (var mj = 0; mj < 12; mj++) {
              var sum = 0;
              var n = 0;
              eligible.forEach(function (item) {
                var v = item.observed.monthlyPct[mj];
                if (v != null && Number.isFinite(Number(v))) {
                  sum += Number(v);
                  n++;
                }
              });
              months.push(n ? Math.round((sum / n) * 100) / 100 : null);
            }
          }
          return {
            months: months,
            yearsUsed: eligible.map(function (item) { return item.year; }),
          };
        }"""

AVG_NEW = """        function computeAverageSeasonalityPct(operatingYear, maxYears) {
          /* KPI-SEASON-PCT-MEAN-AH: equal-weight mean of each year's monthlyPct */
          var eligible = listEligiblePastYearsForBaseline(operatingYear, maxYears);
          if (!eligible.length) return null;
          var months = [];
          for (var mj = 0; mj < 12; mj++) {
            var sum = 0;
            var n = 0;
            eligible.forEach(function (item) {
              var v =
                item.observed && item.observed.monthlyPct
                  ? item.observed.monthlyPct[mj]
                  : null;
              if (v != null && Number.isFinite(Number(v))) {
                sum += Number(v);
                n++;
              }
            });
            months.push(n ? Math.round((sum / n) * 100) / 100 : null);
          }
          return {
            months: months,
            yearsUsed: eligible.map(function (item) { return item.year; }),
          };
        }"""

HL_OLD = """        function computeBaselineHlWeights(operatingYear, maxYears) {
          var oy = Number(operatingYear);
          if (!Number.isFinite(oy)) return null;
          var cap = maxYears == null ? 2 : Math.max(1, Math.min(5, Number(maxYears) || 2));
          var eligible = listEligiblePastYearsForBaseline(oy, cap);
          if (!eligible.length) return null;
          var months = [];
          for (var m = 0; m < 12; m++) {
            var sum = 0;
            var n = 0;
            eligible.forEach(function (item) {
              var v = item.observed.monthlyPct[m];
              if (v != null && Number.isFinite(Number(v))) {
                sum += Number(v);
                n++;
              }
            });
            months.push(n ? snapHlWeightFromObserved(sum / n) : 100);
          }
          return months;
        }"""

HL_NEW = """        function computeBaselineHlWeights(operatingYear, maxYears) {
          var pack = computeAverageSeasonalityPct(operatingYear, maxYears);
          if (!pack || !pack.months || pack.months.length !== 12) return null;
          var months = [];
          for (var m = 0; m < 12; m++) {
            months.push(snapHlWeightFromObserved(pack.months[m]));
          }
          return months;
        }"""

UI_REPLACES = [
    (">前年繁閑期%</th>", ">参考繁閑期%</th>"),
    (">Last Year of Seasonality %</th>", ">Reference Seasonality %</th>"),
    (">前年旺淡季%</th>", ">參考旺淡季%</th>"),
    (
        "月次実質％（前年繁閑％から算出した目標売上KPIに対して、実績売上が何％か）。",
        "月次実質％（参考繁閑％から算出した目標売上KPIに対して、実績売上が何％か）。",
    ),
    (
        "左の繁閑期%を参考に ▲▼ で各月を調整し、合計を 100% に近づけてください。",
        "左の参考繁閑期%を参考に ▲▼ で各月を調整し、合計を 100% に近づけてください。",
    ),
    (
        "refer to Seasonality % on the left",
        "refer to Reference Seasonality % on the left",
    ),
]


def py_escape(js: str) -> str:
    return js.replace("{", "{{").replace("}", "}}")


def patch_text(text: str, path: Path) -> str:
    if AVG_OLD not in text:
        raise SystemExit(f"missing computeAverageSeasonalityPct in {path}")
    text = text.replace(AVG_OLD, AVG_NEW, 1)
    if HL_OLD not in text:
        raise SystemExit(f"missing computeBaselineHlWeights in {path}")
    text = text.replace(HL_OLD, HL_NEW, 1)
    for old, new in UI_REPLACES:
        text = text.replace(old, new)
    return text


def main() -> int:
    store_py = ROOT / "scripts/kpi_year_store_client.py"
    py_text = store_py.read_text(encoding="utf-8")
    py_avg_old = py_escape(AVG_OLD)
    py_avg_new = py_escape(AVG_NEW)
    py_hl_old = py_escape(HL_OLD)
    py_hl_new = py_escape(HL_NEW)
    if py_avg_old not in py_text:
        raise SystemExit("missing computeAverageSeasonalityPct in kpi_year_store_client.py")
    py_text = py_text.replace(py_avg_old, py_avg_new, 1)
    if py_hl_old not in py_text:
        raise SystemExit("missing computeBaselineHlWeights in kpi_year_store_client.py")
    py_text = py_text.replace(py_hl_old, py_hl_new, 1)
    store_py.write_text(py_text, encoding="utf-8")
    print("patched scripts/kpi_year_store_client.py")

    for path in STORE_HTML:
        text = path.read_text(encoding="utf-8")
        path.write_text(patch_text(text, path.relative_to(ROOT)), encoding="utf-8")
        print(f"patched {path.relative_to(ROOT)}")

    extras = [
        ROOT / "scripts/apply_sdm_target_sales_tab.py",
        ROOT / "scripts/build_zh_tw_annual_wave4.py",
        ROOT / "scripts/sdm_hl_stepper_client.py",
    ]
    extra_replaces = [
        ('"col_season": "前年繁閑期%"', '"col_season": "参考繁閑期%"'),
        (
            '"col_season": "Last Year of Seasonality %"',
            '"col_season": "Reference Seasonality %"',
        ),
        (
            '">Last Year of Seasonality %</th>", ">前年旺淡期%</th>"',
            '">Reference Seasonality %</th>", ">參考旺淡季%</th>"',
        ),
        (
            "refer to Seasonality % on the left",
            "refer to Reference Seasonality % on the left",
        ),
    ]
    for path in extras:
        text = path.read_text(encoding="utf-8")
        orig = text
        for old, new in extra_replaces:
            text = text.replace(old, new)
        if text != orig:
            path.write_text(text, encoding="utf-8")
            print(f"patched {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
