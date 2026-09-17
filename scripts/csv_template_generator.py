"""Business Type + active catalog CSV templates (Unit 6D).

Runtime twin: ``js/kpi-csv-templates.js``. 6F can reuse these row builders
for Excel. Does not write ``excel/`` and does not change parsers.
"""

from __future__ import annotations

from typing import Any, Iterable, Sequence

from csv_sales_schema import COMMON_KEYS, RESTAURANT_ONLY_KEYS
from pl_line_catalog import (
    catalog_from_expense_tuples,
    get_default_expense_lines,
    normalize_business_type_for_preset,
)

CATALOG_KEY = "kpiNavigator.plLineCatalog"

SALES_LABELS = {
    "ja": {
        "date": "日付",
        "business_day": "営業日",
        "daily_sales": "日次売上",
        "lunch_sales": "ランチ売上",
        "dinner_sales": "ディナー売上",
        "total_customers": "トータル客数",
        "lunch_customers": "ランチ客数",
        "dinner_customers": "ディナー客数",
        "total_groups": "トータル組数",
        "lunch_groups": "ランチ組数",
        "dinner_groups": "ディナー組数",
        "food_sales": "フード売上",
        "drink_sales": "ドリンク売上",
    },
    "en": {
        "date": "date",
        "business_day": "business day",
        "daily_sales": "daily sales",
        "lunch_sales": "lunch sales",
        "dinner_sales": "dinner sales",
        "total_customers": "total customers",
        "lunch_customers": "lunch customers",
        "dinner_customers": "dinner customers",
        "total_groups": "total groups",
        "lunch_groups": "lunch groups",
        "dinner_groups": "dinner groups",
        "food_sales": "food sales",
        "drink_sales": "drink sales",
    },
    "zh-tw": {
        "date": "日期",
        "business_day": "營業日",
        "daily_sales": "日次銷售",
        "lunch_sales": "午餐銷售",
        "dinner_sales": "晚餐銷售",
        "total_customers": "總客數",
        "lunch_customers": "午餐客數",
        "dinner_customers": "晚餐客數",
        "total_groups": "總組數",
        "lunch_groups": "午餐組數",
        "dinner_groups": "晚餐組數",
        "food_sales": "餐點銷售",
        "drink_sales": "飲料銷售",
    },
}

EXPENSE_HEADER_LABELS = {
    "ja": {
        "date": "日付",
        "month": "年月",
        "item": "lineId",
        "label": "費目",
        "amount": "金額",
    },
    "en": {
        "date": "date",
        "month": "month",
        "item": "lineId",
        "label": "item",
        "amount": "amount",
    },
    "zh-tw": {
        "date": "日期",
        "month": "年月",
        "item": "lineId",
        "label": "費目",
        "amount": "金額",
    },
}

EXPENSE_DAILY_MACHINE_HEADER = ("date", "item", "label", "amount")
EXPENSE_MONTHLY_MACHINE_HEADER = ("month", "item", "label", "amount")
# Parser DATE_KEYS already accepts both date and month.


def normalize_lang(lang: str | None) -> str:
    raw = str(lang or "").lower()
    if raw.startswith("ja"):
        return "ja"
    if raw.startswith("zh"):
        return "zh-tw"
    return "en"


def is_restaurant_like(business_type: str | None) -> bool:
    return normalize_business_type_for_preset(business_type) == "restaurant"


def sales_field_keys(business_type: str | None) -> tuple[str, ...]:
    keys = list(COMMON_KEYS)
    if is_restaurant_like(business_type):
        keys.extend(RESTAURANT_ONLY_KEYS)
    return tuple(keys)


def sales_label_for(key: str, lang: str | None) -> str:
    loc = SALES_LABELS[normalize_lang(lang)]
    return loc.get(key, key)


def csv_cell(value: Any) -> str:
    s = "" if value is None else str(value)
    if any(ch in s for ch in (",", '"', "\n", "\r")):
        return '"' + s.replace('"', '""') + '"'
    return s


def csv_dumps(rows: Sequence[Sequence[Any]]) -> str:
    return "\n".join(",".join(csv_cell(c) for c in row) for row in rows) + "\n"


def parse_csv_text(text: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in str(text or "").replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        if line == "":
            continue
        rows.append(next(iter(_split_csv_line(line)), [line]))
    return rows


def _split_csv_line(line: str) -> Iterable[list[str]]:
    out: list[str] = []
    cur = ""
    in_q = False
    i = 0
    while i < len(line):
        ch = line[i]
        if in_q:
            if ch == '"':
                if i + 1 < len(line) and line[i + 1] == '"':
                    cur += '"'
                    i += 1
                else:
                    in_q = False
            else:
                cur += ch
        elif ch == '"':
            in_q = True
        elif ch == ",":
            out.append(cur)
            cur = ""
        else:
            cur += ch
        i += 1
    out.append(cur)
    yield out


def expense_machine_header(style: str) -> tuple[str, ...]:
    return EXPENSE_DAILY_MACHINE_HEADER if style == "daily" else EXPENSE_MONTHLY_MACHINE_HEADER


def build_sales_template(
    business_type: str | None,
    lang: str | None = "ja",
) -> dict[str, Any]:
    keys = sales_field_keys(business_type)
    loc = normalize_lang(lang)
    labels = [sales_label_for(k, loc) for k in keys]
    text = csv_dumps([list(keys), labels])
    return {
        "kind": "sales",
        "businessType": normalize_business_type_for_preset(business_type),
        "lang": loc,
        "keys": keys,
        "labels": tuple(labels),
        "filename": "sales_template.csv",
        "text": text,
    }


def is_custom_line_id(line_id: str | None) -> bool:
    return str(line_id or "").startswith("exp_custom_")


def line_input_style(line: dict[str, Any]) -> str:
    style = line.get("resolvedInputStyle") or line.get("inputStyle") or "monthly"
    return "daily" if style == "daily" else "monthly"


def line_label(line: dict[str, Any], lang: str | None) -> str:
    loc = normalize_lang(lang)
    if loc == "ja":
        return str(line.get("labelJa") or line.get("labelEn") or line.get("lineId") or "")
    if loc == "zh-tw":
        return str(
            line.get("labelZh")
            or line.get("labelJa")
            or line.get("labelEn")
            or line.get("lineId")
            or ""
        )
    return str(line.get("labelEn") or line.get("labelJa") or line.get("lineId") or "")


def select_active_expense_lines(catalog_lines: Iterable[dict[str, Any]] | None) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for line in catalog_lines or []:
        if not isinstance(line, dict):
            continue
        line_id = str(line.get("lineId") or "").strip()
        if not line_id or line_id in seen:
            continue
        if line.get("active") is False:
            continue
        if line.get("presetOrphan"):
            continue
        seen.add(line_id)
        out.append(line)
    out.sort(
        key=lambda row: (
            0 if line_input_style(row) == "daily" else 1,
            str(row.get("bucket") or ""),
            int(row.get("sortOrder") or 0),
            str(row.get("lineId") or ""),
        )
    )
    return out


def default_catalog_lines(business_type: str | None) -> list[dict[str, Any]]:
    return catalog_from_expense_tuples(get_default_expense_lines(business_type))


def resolve_catalog_lines(
    catalog_lines: Iterable[dict[str, Any]] | None,
    business_type: str | None,
) -> list[dict[str, Any]]:
    rows = [dict(line) for line in (catalog_lines or []) if isinstance(line, dict)]
    if not rows:
        return default_catalog_lines(business_type)
    return rows


def build_expense_template(
    catalog_lines: Iterable[dict[str, Any]] | None,
    *,
    style: str,
    lang: str | None = "ja",
    business_type: str | None = None,
) -> dict[str, Any]:
    want = "daily" if style == "daily" else "monthly"
    loc = normalize_lang(lang)
    active = select_active_expense_lines(resolve_catalog_lines(catalog_lines, business_type))
    picked = [line for line in active if line_input_style(line) == want]
    header_labels = EXPENSE_HEADER_LABELS[loc]
    machine = expense_machine_header(want)
    date_label_key = "date" if want == "daily" else "month"
    rows: list[list[str]] = [
        list(machine),
        [
            header_labels[date_label_key],
            header_labels["item"],
            header_labels["label"],
            header_labels["amount"],
        ],
    ]
    for line in picked:
        line_id = str(line.get("lineId") or "")
        rows.append(["", line_id, line_label(line, loc), ""])
    filename = "expense_daily_template.csv" if want == "daily" else "expense_monthly_template.csv"
    return {
        "kind": "expense-" + want,
        "businessType": normalize_business_type_for_preset(business_type),
        "lang": loc,
        "style": want,
        "lineIds": tuple(str(line.get("lineId") or "") for line in picked),
        "filename": filename,
        "text": csv_dumps(rows),
        "lines": picked,
    }
