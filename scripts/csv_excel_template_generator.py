"""Unit 6F — Excel (.xlsx) thin wrapper around Unit 6D CSV templates.

Does not define Business Type or expense labels. Sheet AOA comes from
``csv_template_generator``. Never writes ``excel/``.
"""

from __future__ import annotations

import re
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Any, Iterable
from xml.etree import ElementTree as ET

from csv_template_generator import (
    EXPENSE_DAILY_MACHINE_HEADER,
    EXPENSE_MONTHLY_MACHINE_HEADER,
    build_expense_template,
    build_sales_template,
    normalize_lang,
    parse_csv_text,
)
from pl_line_catalog import normalize_business_type_for_preset

ROOT = Path(__file__).resolve().parents[1]
EXCEL_DIR = ROOT / "excel"
SALES_BLANK_ROWS = 8

SHEET_NAMES = {
    "ja": {
        "sales": "売上",
        "expense-daily": "支出_日次",
        "expense-monthly": "支出_月次",
    },
    "en": {
        "sales": "Sales",
        "expense-daily": "Daily Expenses",
        "expense-monthly": "Monthly Expenses",
    },
    "zh-tw": {
        "sales": "銷售",
        "expense-daily": "支出_每日",
        "expense-monthly": "支出_月度",
    },
}

NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_PKG_REL = "http://schemas.openxmlformats.org/package/2006/relationships"
NS_CT = "http://schemas.openxmlformats.org/package/2006/content-types"


class FixturePathError(ValueError):
    pass


def sheet_name(kind: str, lang: str | None) -> str:
    loc = normalize_lang(lang)
    pack = SHEET_NAMES.get(loc) or SHEET_NAMES["en"]
    return pack[kind]


def sales_aoa(business_type: str | None, lang: str | None = "ja") -> list[list[str]]:
    rec = build_sales_template(business_type, lang)
    rows = parse_csv_text(rec["text"])
    width = len(rec["keys"])
    for _ in range(SALES_BLANK_ROWS):
        rows.append([""] * width)
    return rows


def expense_aoa(
    catalog_lines: Iterable[dict[str, Any]] | None,
    *,
    style: str,
    lang: str | None = "ja",
    business_type: str | None = None,
) -> list[list[str]]:
    rec = build_expense_template(
        catalog_lines,
        style=style,
        lang=lang,
        business_type=business_type,
    )
    return parse_csv_text(rec["text"])


def build_excel_spec(
    business_type: str | None,
    lang: str | None = "ja",
    catalog_lines: Iterable[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    loc = normalize_lang(lang)
    bt = normalize_business_type_for_preset(business_type)
    sales = build_sales_template(bt, loc)
    daily = build_expense_template(catalog_lines, style="daily", lang=loc, business_type=bt)
    monthly = build_expense_template(
        catalog_lines, style="monthly", lang=loc, business_type=bt
    )
    sheets = [
        {
            "kind": "sales",
            "name": sheet_name("sales", loc),
            "rows": sales_aoa(bt, loc),
            "keys": tuple(sales["keys"]),
            "lineIds": (),
        },
        {
            "kind": "expense-daily",
            "name": sheet_name("expense-daily", loc),
            "rows": expense_aoa(catalog_lines, style="daily", lang=loc, business_type=bt),
            "keys": tuple(EXPENSE_DAILY_MACHINE_HEADER),
            "lineIds": tuple(daily["lineIds"]),
        },
        {
            "kind": "expense-monthly",
            "name": sheet_name("expense-monthly", loc),
            "rows": expense_aoa(
                catalog_lines, style="monthly", lang=loc, business_type=bt
            ),
            "keys": tuple(EXPENSE_MONTHLY_MACHINE_HEADER),
            "lineIds": tuple(monthly["lineIds"]),
        },
    ]
    return {
        "businessType": bt,
        "lang": loc,
        "filename": f"kpi_template_{bt}.xlsx",
        "sheets": sheets,
    }


def _xml_escape(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _col_letter(index: int) -> str:
    n = index + 1
    out = ""
    while n:
        n, rem = divmod(n - 1, 26)
        out = chr(65 + rem) + out
    return out


def _sheet_xml(rows: list[list[str]]) -> str:
    max_r = max(len(rows), 1)
    max_c = max((len(row) for row in rows), default=1)
    dim = f"A1:{_col_letter(max_c - 1)}{max_r}"
    parts = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        f'<worksheet xmlns="{NS_MAIN}"><dimension ref="{dim}"/><sheetData>',
    ]
    for r, row in enumerate(rows, start=1):
        cells = []
        for c, value in enumerate(row):
            addr = f"{_col_letter(c)}{r}"
            cells.append(
                f'<c r="{addr}" t="inlineStr"><is><t>{_xml_escape(value)}</t></is></c>'
            )
        parts.append(f'<row r="{r}">{"".join(cells)}</row>')
    parts.append("</sheetData></worksheet>")
    return "".join(parts)


def workbook_bytes(spec: dict[str, Any]) -> bytes:
    sheets = spec["sheets"]
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "[Content_Types].xml",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f'<Types xmlns="{NS_CT}">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
            '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
            + "".join(
                f'<Override PartName="/xl/worksheets/sheet{i}.xml" '
                'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
                for i in range(1, len(sheets) + 1)
            )
            + "</Types>",
        )
        zf.writestr(
            "_rels/.rels",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f'<Relationships xmlns="{NS_PKG_REL}">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
            "</Relationships>",
        )
        sheet_tags = []
        rels = []
        for i, sheet in enumerate(sheets, start=1):
            name = _xml_escape(sheet["name"])
            sheet_tags.append(
                f'<sheet name="{name}" sheetId="{i}" r:id="rId{i}"/>'
            )
            rels.append(
                f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i}.xml"/>'
            )
            zf.writestr(f"xl/worksheets/sheet{i}.xml", _sheet_xml(sheet["rows"]))
        rels.append(
            f'<Relationship Id="rId{len(sheets) + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
        )
        zf.writestr(
            "xl/workbook.xml",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f'<workbook xmlns="{NS_MAIN}" xmlns:r="{NS_REL}">'
            f'<sheets>{"".join(sheet_tags)}</sheets></workbook>',
        )
        zf.writestr(
            "xl/_rels/workbook.xml.rels",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f'<Relationships xmlns="{NS_PKG_REL}">{"".join(rels)}</Relationships>',
        )
        zf.writestr(
            "xl/styles.xml",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f'<styleSheet xmlns="{NS_MAIN}">'
            '<fonts count="1"><font><sz val="11"/><color theme="1"/><name val="Calibri"/><family val="2"/></font></fonts>'
            '<fills count="2">'
            '<fill><patternFill patternType="none"/></fill>'
            '<fill><patternFill patternType="gray125"/></fill>'
            "</fills>"
            "<borders count=\"1\"><border><left/><right/><top/><bottom/><diagonal/></border></borders>"
            '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
            '<cellXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/></cellXfs>'
            "</styleSheet>",
        )
    return buf.getvalue()


def read_workbook(data: bytes) -> dict[str, list[list[str]]]:
    with zipfile.ZipFile(BytesIO(data)) as zf:
        names = _workbook_sheet_names(zf)
        out: dict[str, list[list[str]]] = {}
        for i, name in enumerate(names, start=1):
            xml = zf.read(f"xl/worksheets/sheet{i}.xml")
            out[name] = _parse_sheet_xml(xml)
        return out


def _workbook_sheet_names(zf: zipfile.ZipFile) -> list[str]:
    root = ET.fromstring(zf.read("xl/workbook.xml"))
    ns = {"m": NS_MAIN}
    return [el.get("name") or "" for el in root.findall("m:sheets/m:sheet", ns)]


def _parse_sheet_xml(xml: bytes) -> list[list[str]]:
    root = ET.fromstring(xml)
    ns = {"m": NS_MAIN}
    rows: list[list[str]] = []
    for row_el in root.findall("m:sheetData/m:row", ns):
        cells: dict[int, str] = {}
        max_c = -1
        for cell in row_el.findall("m:c", ns):
            addr = cell.get("r") or "A1"
            col = _col_index(re.sub(r"\d+", "", addr))
            text_el = cell.find("m:is/m:t", ns)
            value = "" if text_el is None or text_el.text is None else text_el.text
            cells[col] = value
            if col > max_c:
                max_c = col
        row = [cells.get(i, "") for i in range(max_c + 1)] if max_c >= 0 else []
        rows.append(row)
    return rows


def _col_index(letters: str) -> int:
    n = 0
    for ch in letters:
        n = n * 26 + (ord(ch.upper()) - 64)
    return n - 1


def assert_safe_dest(dest: Path) -> Path:
    dest = dest.resolve()
    tests_root = (ROOT / "tests").resolve()
    excel = EXCEL_DIR.resolve()
    try:
        dest.relative_to(tests_root)
    except ValueError as exc:
        raise FixturePathError(f"xlsx output must live under tests/: {dest}") from exc
    try:
        dest.relative_to(excel)
        raise FixturePathError(f"excel/ is forbidden: {dest}")
    except ValueError:
        pass
    if "excel" in dest.parts:
        raise FixturePathError(f"excel/ is forbidden: {dest}")
    return dest


def write_xlsx(spec: dict[str, Any], dest: Path) -> Path:
    dest = assert_safe_dest(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(workbook_bytes(spec))
    return dest
