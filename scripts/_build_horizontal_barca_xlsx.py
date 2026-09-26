# -*- coding: utf-8 -*-
"""Build a multi-sheet horizontal XLSX from the copied Barca CSV fixture.

Does not read or write excel/. Column letters support AA+ (the daily report is wide).
"""
from __future__ import annotations

import csv
import io
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "fixtures" / "import" / "horizontal" / "barca_2025_11_data.csv"
OUT_PATH = ROOT / "fixtures" / "import" / "horizontal" / "barca_2025_11_data.xlsx"


def col_ref(col0: int) -> str:
    n = col0 + 1
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def cell_xml(ref: str, value) -> str:
    if value is None or value == "":
        return ""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return f'<c r="{ref}"><v>{value}</v></c>'
    return f'<c r="{ref}" t="inlineStr"><is><t>{escape(str(value))}</t></is></c>'


def sheet_xml(rows: list[list]) -> str:
    out = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>',
    ]
    for r, row in enumerate(rows, 1):
        cells = []
        for c, val in enumerate(row):
            xml = cell_xml(f"{col_ref(c)}{r}", val)
            if xml:
                cells.append(xml)
        if cells:
            out.append(f'<row r="{r}">{"".join(cells)}</row>')
    out.append("</sheetData></worksheet>")
    return "\n".join(out)


def write_xlsx(path: Path, sheets: list[tuple[str, list[list]]]) -> None:
    names = [s[0] for s in sheets]
    wb = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>',
    ]
    rels = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
    ]
    for i, name in enumerate(names, 1):
        wb.append(f'<sheet name="{escape(name)}" sheetId="{i}" r:id="rId{i}"/>')
        rels.append(
            f'<Relationship Id="rId{i}" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
            f'Target="worksheets/sheet{i}.xml"/>'
        )
    wb.append("</sheets></workbook>")
    rels.append("</Relationships>")
    ctypes = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
        '<Default Extension="xml" ContentType="application/xml"/>',
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>',
    ]
    for i in range(1, len(names) + 1):
        ctypes.append(
            f'<Override PartName="/xl/worksheets/sheet{i}.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        )
    ctypes.append("</Types>")
    root_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>
"""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", "\n".join(ctypes))
        z.writestr("xl/workbook.xml", "\n".join(wb))
        z.writestr("xl/_rels/workbook.xml.rels", "\n".join(rels))
        z.writestr("_rels/.rels", root_rels)
        for i, (_n, rows) in enumerate(sheets, 1):
            z.writestr(f"xl/worksheets/sheet{i}.xml", sheet_xml(rows))
    path.write_bytes(buf.getvalue())


def load_csv_rows(path: Path) -> list[list[str]]:
    text = path.read_text(encoding="utf-8-sig")
    return list(csv.reader(io.StringIO(text)))


def main() -> int:
    if not CSV_PATH.is_file():
        raise SystemExit(f"missing copied fixture: {CSV_PATH}")
    rows = load_csv_rows(CSV_PATH)
    dummy = [["メモ"], ["picker-only sheet — do not treat as the daily report"]]
    write_xlsx(OUT_PATH, [("メモ", dummy), ("日次レポート", rows)])
    print(f"wrote {OUT_PATH} rows={len(rows)} bytes={OUT_PATH.stat().st_size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
