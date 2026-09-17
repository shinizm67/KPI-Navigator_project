"""Unit 6E — Business Type smoke fixture generator.

Writes import-only sample CSVs under ``tests/generated-fixtures/``.
Never writes ``excel/``, reset files, or production catalog.

Reuses:
- csv_sales_schema.py
- csv_template_generator.py
- pl_line_catalog.py (preset tuples / catalog)
"""

from __future__ import annotations

import json
from calendar import monthrange
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Iterable

from csv_sales_schema import (
    COMMON_KEYS,
    CSV_PERSISTED_MEAL_KEYS,
    LUNCH_VALIDATION_FIELDS,
    RESTAURANT_ONLY_KEYS,
)
from csv_template_generator import (
    EXPENSE_DAILY_MACHINE_HEADER,
    EXPENSE_MONTHLY_MACHINE_HEADER,
    csv_dumps,
    default_catalog_lines,
    expense_machine_header,
    is_restaurant_like,
    line_input_style,
    line_label,
    sales_field_keys,
    select_active_expense_lines,
)
from pl_line_catalog import BUSINESS_TYPE_CANONICAL

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "tests" / "generated-fixtures"
EXCEL_DIR = ROOT / "excel"

RESTAURANT_YEARS = (2024, 2025, 2026)
MINIMAL_YEAR = 2026
MINIMAL_MONTH = 3
MINIMAL_DAY_COUNT = 7
NON_RESTAURANT = tuple(code for code in BUSINESS_TYPE_CANONICAL if code != "restaurant")

# Shared occupancy/utility ids — skip when picking a distinctive monthly sample.
GENERIC_MONTHLY_IDS = frozenset(
    {
        "exp_rent",
        "exp_electric",
        "exp_water",
        "exp_gas",
        "exp_telecom",
        "exp_non_life_insurance",
    }
)

# Mock catalog only. Never written to kpiNavigator.plLineCatalog by this generator.
CUSTOM_SMOKE_LINE: dict[str, Any] = {
    "lineId": "exp_custom_variable_smoke",
    "labelJa": "Smoke custom fee",
    "labelEn": "Smoke custom fee",
    "labelZh": "Smoke custom fee",
    "bucket": "variable",
    "inputStyle": "monthly",
    "resolvedInputStyle": "monthly",
    "isDefault": False,
    "active": True,
    "presetOrphan": False,
    "sortOrder": 900,
}

CUSTOM_SMOKE_AMOUNT = 7777
CUSTOM_HOST_TYPE = "retail"


class FixturePathError(ValueError):
    pass


def assert_safe_dest(dest: Path) -> Path:
    dest = dest.resolve()
    tests_root = (ROOT / "tests").resolve()
    excel = EXCEL_DIR.resolve()
    try:
        dest.relative_to(tests_root)
    except ValueError as exc:
        raise FixturePathError(f"fixtures must live under tests/: {dest}") from exc
    try:
        dest.relative_to(excel)
        raise FixturePathError(f"excel/ is forbidden: {dest}")
    except ValueError:
        pass
    if "excel" in dest.parts:
        raise FixturePathError(f"excel/ is forbidden: {dest}")
    return dest


def iter_year_dates(year: int) -> list[date]:
    start = date(year, 1, 1)
    end = date(year, 12, 31)
    out: list[date] = []
    cur = start
    while cur <= end:
        out.append(cur)
        cur += timedelta(days=1)
    return out


def iter_minimal_dates(year: int = MINIMAL_YEAR, month: int = MINIMAL_MONTH) -> list[date]:
    last = min(MINIMAL_DAY_COUNT, monthrange(year, month)[1])
    return [date(year, month, day) for day in range(1, last + 1)]


def is_closed_day(d: date) -> bool:
    return d.weekday() == 6


def restaurant_sales_values(d: date) -> dict[str, Any]:
    iso = d.isoformat()
    if is_closed_day(d):
        zeros = {
            "date": iso,
            "business_day": 0,
            "daily_sales": 0,
            "lunch_sales": 0,
            "dinner_sales": 0,
            "total_customers": 0,
            "lunch_customers": 0,
            "dinner_customers": 0,
            "total_groups": 0,
            "lunch_groups": 0,
            "dinner_groups": 0,
            "food_sales": 0,
            "drink_sales": 0,
        }
        return zeros
    yday = d.timetuple().tm_yday
    sales = (d.year - 2023) * 100000 + yday * 100 + d.month
    dinner = (sales * 6) // 10
    lunch = sales - dinner
    food = (sales * 7) // 10
    drink = sales - food
    total_c = 10 + (yday % 17)
    dinner_c = (total_c * 6) // 10
    lunch_c = total_c - dinner_c
    total_g = 4 + (yday % 7)
    dinner_g = max(1, (total_g * 6) // 10)
    lunch_g = max(0, total_g - dinner_g)
    return {
        "date": iso,
        "business_day": 1,
        "daily_sales": sales,
        "lunch_sales": lunch,
        "dinner_sales": dinner,
        "total_customers": total_c,
        "lunch_customers": lunch_c,
        "dinner_customers": dinner_c,
        "total_groups": total_g,
        "lunch_groups": lunch_g,
        "dinner_groups": dinner_g,
        "food_sales": food,
        "drink_sales": drink,
    }


def non_restaurant_sales_values(d: date, business_type: str) -> dict[str, Any]:
    bt_index = list(BUSINESS_TYPE_CANONICAL).index(business_type)
    sales = 4000 + bt_index * 100000 + d.month * 100 + d.day
    return {
        "date": d.isoformat(),
        "business_day": 0 if is_closed_day(d) else 1,
        "daily_sales": 0 if is_closed_day(d) else sales,
    }


def sales_rows(business_type: str, dates: Iterable[date]) -> list[list[Any]]:
    keys = sales_field_keys(business_type)
    rows: list[list[Any]] = [list(keys)]
    for d in dates:
        values = (
            restaurant_sales_values(d)
            if is_restaurant_like(business_type)
            else non_restaurant_sales_values(d, business_type)
        )
        rows.append([values.get(key, "") for key in keys])
    return rows


def catalog_lines(business_type: str) -> list[dict[str, Any]]:
    return select_active_expense_lines(default_catalog_lines(business_type))


def lines_for_style(lines: Iterable[dict[str, Any]], style: str) -> list[dict[str, Any]]:
    want = "daily" if style == "daily" else "monthly"
    return [line for line in lines if line_input_style(line) == want]


def pick_representative(lines: list[dict[str, Any]], style: str) -> dict[str, Any] | None:
    styled = lines_for_style(lines, style)
    if not styled:
        return None
    if style == "monthly":
        unique = [line for line in styled if str(line.get("lineId")) not in GENERIC_MONTHLY_IDS]
        if unique:
            return unique[0]
    return styled[0]


def daily_expense_amount(line_index: int, d: date) -> int:
    return 1100 + line_index * 100 + d.month * 10 + d.day


def monthly_expense_amount(line_index: int, year: int, month: int) -> int:
    return 21000 + line_index * 1000 + (year - 2024) * 100 + month


def expense_rows(
    lines: list[dict[str, Any]],
    *,
    style: str,
    dates: Iterable[date] | None = None,
    months: Iterable[tuple[int, int]] | None = None,
) -> list[list[Any]]:
    want = "daily" if style == "daily" else "monthly"
    header = list(expense_machine_header(want))
    rows: list[list[Any]] = [header]
    if want == "daily":
        day_list = list(dates or [])
        for line_index, line in enumerate(lines):
            line_id = str(line.get("lineId") or "")
            label = line_label(line, "en")
            for d in day_list:
                rows.append(
                    [d.isoformat(), line_id, label, daily_expense_amount(line_index, d)]
                )
        return rows
    month_list = list(months or [])
    for line_index, line in enumerate(lines):
        line_id = str(line.get("lineId") or "")
        label = line_label(line, "en")
        for year, month in month_list:
            rows.append(
                [
                    f"{year:04d}-{month:02d}",
                    line_id,
                    label,
                    monthly_expense_amount(line_index, year, month),
                ]
            )
    return rows


def restaurant_bundle(year: int) -> dict[str, Any]:
    dates = iter_year_dates(year)
    lines = catalog_lines("restaurant")
    daily_lines = lines_for_style(lines, "daily")
    monthly_lines = lines_for_style(lines, "monthly")
    months = [(year, month) for month in range(1, 13)]
    return {
        "year": year,
        "sales": {
            "filename": f"restaurant_{year}_sales.csv",
            "text": csv_dumps(sales_rows("restaurant", dates)),
            "keys": sales_field_keys("restaurant"),
            "days": len(dates),
        },
        "expenses_daily": {
            "filename": f"restaurant_{year}_expenses_daily.csv",
            "text": csv_dumps(expense_rows(daily_lines, style="daily", dates=dates)),
            "lineIds": tuple(str(line["lineId"]) for line in daily_lines),
        },
        "expenses_monthly": {
            "filename": f"restaurant_{year}_expenses_monthly.csv",
            "text": csv_dumps(
                expense_rows(monthly_lines, style="monthly", months=months)
            ),
            "lineIds": tuple(str(line["lineId"]) for line in monthly_lines),
        },
    }


def custom_catalog_entry() -> dict[str, Any]:
    line = dict(CUSTOM_SMOKE_LINE)
    return {
        "lineId": line["lineId"],
        "inputStyle": line_input_style(line),
        "active": True,
        "hostBusinessType": CUSTOM_HOST_TYPE,
        "labels": {
            "ja": line_label(line, "ja"),
            "en": line_label(line, "en"),
            "zh-tw": line_label(line, "zh-tw"),
        },
        "mockCatalog": True,
        "productionCatalog": False,
    }


def minimal_bundle(business_type: str) -> dict[str, Any]:
    dates = iter_minimal_dates()
    lines = catalog_lines(business_type)
    daily_line = pick_representative(lines, "daily")
    monthly_line = pick_representative(lines, "monthly")
    if daily_line is None or monthly_line is None:
        raise RuntimeError(f"{business_type} preset missing daily or monthly line")
    year, month = MINIMAL_YEAR, MINIMAL_MONTH
    daily_rows = expense_rows([daily_line], style="daily", dates=dates)
    monthly_rows = expense_rows(
        [monthly_line], style="monthly", months=[(year, month)]
    )
    if business_type == CUSTOM_HOST_TYPE:
        custom = dict(CUSTOM_SMOKE_LINE)
        monthly_rows.append(
            [
                f"{year:04d}-{month:02d}",
                custom["lineId"],
                line_label(custom, "en"),
                CUSTOM_SMOKE_AMOUNT,
            ]
        )
    return {
        "businessType": business_type,
        "sales": {
            "filename": f"{business_type}_minimal_sales.csv",
            "text": csv_dumps(sales_rows(business_type, dates)),
            "keys": sales_field_keys(business_type),
            "days": len(dates),
        },
        "expenses_daily": {
            "filename": f"{business_type}_minimal_expenses_daily.csv",
            "text": csv_dumps(daily_rows),
            "lineIds": (str(daily_line["lineId"]),),
        },
        "expenses_monthly": {
            "filename": f"{business_type}_minimal_expenses_monthly.csv",
            "text": csv_dumps(monthly_rows),
            "lineIds": tuple(
                [str(monthly_line["lineId"])]
                + ([CUSTOM_SMOKE_LINE["lineId"]] if business_type == CUSTOM_HOST_TYPE else [])
            ),
        },
        "dailyLine": {
            "lineId": daily_line["lineId"],
            "labels": {
                "ja": line_label(daily_line, "ja"),
                "en": line_label(daily_line, "en"),
                "zh-tw": line_label(daily_line, "zh-tw"),
            },
        },
        "monthlyLine": {
            "lineId": monthly_line["lineId"],
            "labels": {
                "ja": line_label(monthly_line, "ja"),
                "en": line_label(monthly_line, "en"),
                "zh-tw": line_label(monthly_line, "zh-tw"),
            },
        },
    }


def build_manifest(restaurant: list[dict[str, Any]], minimal: list[dict[str, Any]]) -> dict[str, Any]:
    files: list[str] = []
    for bundle in restaurant:
        files.extend(
            [
                bundle["sales"]["filename"],
                bundle["expenses_daily"]["filename"],
                bundle["expenses_monthly"]["filename"],
            ]
        )
    for bundle in minimal:
        files.extend(
            [
                bundle["sales"]["filename"],
                bundle["expenses_daily"]["filename"],
                bundle["expenses_monthly"]["filename"],
            ]
        )
    return {
        "schema": "kpn-6e-smoke-fixtures-v1",
        "generatedBy": "csv_smoke_fixture_generator.py",
        "locale": "machine-key",
        "reset": False,
        "deletionSemantics": False,
        "excel": "untouched",
        "productionCatalog": False,
        "restaurantYears": list(RESTAURANT_YEARS),
        "minimalYear": MINIMAL_YEAR,
        "minimalMonth": MINIMAL_MONTH,
        "salesCommonKeys": list(COMMON_KEYS),
        "salesRestaurantOnlyKeys": list(RESTAURANT_ONLY_KEYS),
        "unit4PersistedMealKeys": list(CSV_PERSISTED_MEAL_KEYS),
        "unit4LunchValidationKeys": list(LUNCH_VALIDATION_FIELDS),
        "expenseDailyHeader": list(EXPENSE_DAILY_MACHINE_HEADER),
        "expenseMonthlyHeader": list(EXPENSE_MONTHLY_MACHINE_HEADER),
        "custom": custom_catalog_entry(),
        "files": files,
        "restaurant": [
            {
                "year": bundle["year"],
                "sales": bundle["sales"]["filename"],
                "expensesDaily": bundle["expenses_daily"]["filename"],
                "expensesMonthly": bundle["expenses_monthly"]["filename"],
                "dailyLineIds": list(bundle["expenses_daily"]["lineIds"]),
                "monthlyLineIds": list(bundle["expenses_monthly"]["lineIds"]),
            }
            for bundle in restaurant
        ],
        "minimal": [
            {
                "businessType": bundle["businessType"],
                "sales": bundle["sales"]["filename"],
                "expensesDaily": bundle["expenses_daily"]["filename"],
                "expensesMonthly": bundle["expenses_monthly"]["filename"],
                "dailyLine": bundle["dailyLine"],
                "monthlyLine": bundle["monthlyLine"],
            }
            for bundle in minimal
        ],
    }


def build_all() -> dict[str, Any]:
    restaurant = [restaurant_bundle(year) for year in RESTAURANT_YEARS]
    minimal = [minimal_bundle(code) for code in NON_RESTAURANT]
    files: dict[str, str] = {}
    for bundle in restaurant:
        files[bundle["sales"]["filename"]] = bundle["sales"]["text"]
        files[bundle["expenses_daily"]["filename"]] = bundle["expenses_daily"]["text"]
        files[bundle["expenses_monthly"]["filename"]] = bundle["expenses_monthly"]["text"]
    for bundle in minimal:
        files[bundle["sales"]["filename"]] = bundle["sales"]["text"]
        files[bundle["expenses_daily"]["filename"]] = bundle["expenses_daily"]["text"]
        files[bundle["expenses_monthly"]["filename"]] = bundle["expenses_monthly"]["text"]
    manifest = build_manifest(restaurant, minimal)
    files["manifest.json"] = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    return {
        "restaurant": restaurant,
        "minimal": minimal,
        "manifest": manifest,
        "files": files,
    }


def write_fixtures(dest: Path | None = None) -> dict[str, Path]:
    dest = assert_safe_dest(dest or FIXTURE_ROOT)
    dest.mkdir(parents=True, exist_ok=True)
    payload = build_all()
    written: dict[str, Path] = {}
    for name, text in payload["files"].items():
        if "reset" in name.lower() or "delete" in name.lower():
            raise FixturePathError(f"reset/deletion fixture names are forbidden: {name}")
        path = dest / name
        if "excel" in path.parts:
            raise FixturePathError(f"excel/ is forbidden: {path}")
        path.write_text(text, encoding="utf-8", newline="\n")
        written[name] = path
    return written


def main() -> int:
    written = write_fixtures(FIXTURE_ROOT)
    print(f"wrote {len(written)} files under {FIXTURE_ROOT.relative_to(ROOT).as_posix()}")
    for name in sorted(written):
        print(f"  {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
