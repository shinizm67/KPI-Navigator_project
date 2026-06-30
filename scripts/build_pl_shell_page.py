#!/usr/bin/env python3
"""Generate PL table shell (layout only) — JA/EN. Cell values filled at runtime later."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Row order: top summary → KPI → profit → expense detail (PL表例4.pdf / build_pl_table_page.py)
INCOME_ROWS = [
    ("bizdays", "営業日数", "Business Days", "meta"),
    ("store_sales", "店舗売上", "Store Sales", "summary"),
    ("sales_a", "売上A", "Sales A", "detail"),
    ("sales_b", "売上B", "Sales B", "detail"),
    ("sales_total", "売上合計", "Total Sales", "total"),
]

EXPENSE_SUMMARY_ROWS = [
    ("fixed_sum", "固定費", "Fixed", "summary"),
    ("variable_sum", "変動費", "Expected", "summary"),
    ("expense_sum", "合計", "Total Expenses", "total"),
]

KPI_ROWS = [
    ("food_cost_rate", "食材原価率", "Food cost Ratio"),
    ("labor_rate", "労働分配率", "Labor Share"),
    ("fl_rate", "FL率", "Food & Labor Ratio"),
    ("gross_margin", "粗利益率", "Gross Margin"),
]

# PL表例4.pdf 科目順（build_pl_table_page.EXPENSE_ROWS）— bucket で固定/変動に分割
EXPENSE_DETAIL = [
    ("rent", "家賃◉", "Rent◉", "fixed", "rent"),
    ("labor_fixed", "人件費(社員)", "Labor (staff)", "fixed"),
    ("music", "音楽費（バンド）◉", "Music (band)◉", "fixed"),
    ("plants", "植木◉", "Plants◉", "fixed"),
    ("town", "町会費◉", "Town fee◉", "fixed"),
    ("pest", "害虫駆除費用◉", "Pest control◉", "fixed"),
    ("repair", "修繕費◉", "Repairs◉", "fixed"),
    ("lease", "リース料（厨房・レジ）◉", "Lease (kitchen/POS)◉", "fixed"),
    ("bgm", "有線放送（ＢＧＭ）◉", "BGM◉", "fixed"),
    ("tablecheck", "Table Check◉", "Table Check◉", "fixed"),
    ("alsok", "アルソック◉", "ALSOK◉", "fixed"),
    ("asset_tax", "償却資産税", "Fixed asset tax", "fixed", "owned"),
    ("depr", "減価償却費（想定）", "Depreciation (est.)", "fixed"),
    ("insurance", "店舗用損害賠償保険", "Shop liability ins.", "fixed"),
    ("social", "社会保険料", "Social insurance", "fixed"),
    ("food_purchase", "★仕入（食材）◉", "★Food purchase◉", "variable"),
    ("labor_pt", "★人件費(アルバイト)", "★Part-time labor", "variable"),
    ("supplies", "★仕入（備品・消耗品）◉", "★Supplies◉", "variable"),
    ("petty", "★雑費（小口精算等）◉", "★Petty cash◉", "variable"),
    ("maint", "★メンテナンス料◉", "★Maintenance◉", "variable"),
    ("electric", "★電気◉", "★Electricity◉", "variable"),
    ("gas", "★ガス◉", "★Gas◉", "variable"),
    ("water", "★水道◉", "★Water◉", "variable"),
    ("waste", "★産廃処理費◉", "★Waste disposal◉", "variable"),
    ("card_fee", "★クレジットカード手数料◉", "★Card fees◉", "variable"),
    ("ad", "広告宣伝費◉", "Advertising◉", "variable"),
    ("telecom", "通信費◉", "Telecom◉", "variable"),
    ("uniform", "被服費◉", "Uniforms◉", "variable"),
    ("hq", "本部費用", "Head office", "variable"),
    ("emp_ins", "雇用保険料", "Employment ins.", "variable"),
    ("workers_comp", "労災保険料", "Workers' comp.", "variable"),
    ("consumption_tax", "消費税（想定）", "Consumption tax (est.)", "variable"),
]

MONTHS_JA = [f"{m}月" for m in range(1, 13)]
MONTHS_EN = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def data_cells(row_id: str, editable: bool = False) -> str:
    parts = []
    for mi in range(13):
        key = "annual" if mi == 12 else str(mi)
        edit = ""
        if editable and mi < 12:
            edit = (
                f' contenteditable="true" data-pl-editable="1" data-pl-field="amount"'
                f' data-row="{row_id}" data-month="{mi}"'
            )
        parts.append(f'<td class="pl-num"{edit} data-pl-cell="amount" data-row="{row_id}" data-period="{key}"></td>')
        parts.append(f'<td class="pl-pct" data-pl-cell="ratio" data-row="{row_id}" data-period="{key}"></td>')
    return "".join(parts)


def v_label(text: str, cls: str = "pl-v-label") -> str:
    return f'<span class="{cls}">{text}</span>'


def render_tbody(lang: str) -> str:
    is_ja = lang == "ja"
    major_income = "収入" if is_ja else "Income"
    major_exp_sum = "総支出" if is_ja else "Total Expenses"
    major_expense = "支出" if is_ja else "Expenses"
    mid_fix = "Fix" if not is_ja else "固定費"
    mid_var = "Expected" if not is_ja else "変動費"
    profit_l = "利益" if is_ja else "Profit"
    kpi_toggle = "KPI" if not is_ja else "KPI"
    add_fix = "＋ 固定費の行を追加" if is_ja else "+ Add fixed row"
    add_var = "＋ 変動費の行を追加" if is_ja else "+ Add variable row"

    rows: list[str] = []

    # — Income block —
    n_income = len(INCOME_ROWS)
    for i, (rid, ja, en, kind) in enumerate(INCOME_ROWS):
        label = ja if is_ja else en
        bold = " pl-row-bold" if kind == "total" else ""
        major = ""
        if i == 0:
            major = (
                f'<td class="pl-v-cell pl-v-cell--major" rowspan="{n_income}">'
                f'{v_label(major_income, "pl-v-label pl-v-label--major")}</td>'
            )
        rows.append(
            f'<tr class="pl-data-row{ bold}" data-row="{rid}" data-pl-section="income">'
            f"{major}"
            f'<td class="pl-v-cell pl-v-cell--mid pl-v-cell--empty"></td>'
            f'<th scope="row" class="pl-h-label">{label}</th>'
            f"{data_cells(rid)}"
            f"</tr>"
        )

    # — Expense summary block —
    n_sum = len(EXPENSE_SUMMARY_ROWS)
    for i, (rid, ja, en, kind) in enumerate(EXPENSE_SUMMARY_ROWS):
        label = ja if is_ja else en
        bold = " pl-row-bold" if kind == "total" else ""
        major = ""
        if i == 0:
            major = (
                f'<td class="pl-v-cell pl-v-cell--major" rowspan="{n_sum}">'
                f'{v_label(major_exp_sum, "pl-v-label pl-v-label--major")}</td>'
            )
        rows.append(
            f'<tr class="pl-data-row{ bold}" data-row="{rid}" data-pl-section="expense-summary">'
            f"{major}"
            f'<td class="pl-v-cell pl-v-cell--mid pl-v-cell--empty"></td>'
            f'<th scope="row" class="pl-h-label">{label}</th>'
            f"{data_cells(rid)}"
            f"</tr>"
        )

    # — KPI toggle + rows —
    rows.append(
        f'<tr class="pl-kpi-head" data-pl-section="kpi">'
        f'<td class="pl-v-cell pl-v-cell--major pl-v-cell--empty"></td>'
        f'<td class="pl-v-cell pl-v-cell--mid pl-v-cell--empty"></td>'
        f'<th scope="row" class="pl-h-label pl-kpi-head__label">'
        f'<button type="button" class="pl-kpi-toggle" id="pl-kpi-toggle" aria-expanded="true" aria-controls="pl-kpi-group">'
        f'<span class="pl-kpi-toggle__icon" aria-hidden="true">▼</span> {kpi_toggle}'
        f"</button></th>"
        f'<td colspan="26" class="pl-kpi-head__hint"></td></tr>'
    )
    for rid, ja, en in KPI_ROWS:
        label = ja if is_ja else en
        rows.append(
            f'<tr class="pl-kpi-row pl-kpi-group" id="pl-kpi-group" data-row="{rid}" data-pl-section="kpi">'
            f'<td class="pl-v-cell pl-v-cell--major pl-v-cell--empty"></td>'
            f'<td class="pl-v-cell pl-v-cell--mid pl-v-cell--empty"></td>'
            f'<th scope="row" class="pl-h-label pl-h-label--kpi">{label}</th>'
            f"{data_cells(rid)}"
            f"</tr>"
        )

    # — Profit —
    rows.append(
        f'<tr class="pl-data-row pl-row-bold pl-profit-row" data-row="profit" data-pl-section="profit">'
        f'<td class="pl-v-cell pl-v-cell--major pl-v-cell--empty"></td>'
        f'<td class="pl-v-cell pl-v-cell--mid pl-v-cell--empty"></td>'
        f'<th scope="row" class="pl-h-label pl-h-label--profit">{profit_l}</th>'
        f'{data_cells("profit")}'
        f"</tr>"
    )

    # — Expense detail (fixed / variable) —
    fixed_rows = [r for r in EXPENSE_DETAIL if r[3] == "fixed"]
    var_rows = [r for r in EXPENSE_DETAIL if r[3] == "variable"]
    total_detail = len(fixed_rows) + 1 + len(var_rows) + 1
    detail_i = 0

    def detail_tr(rid: str, label: str, bucket: str, occ: str | None) -> str:
        nonlocal detail_i
        occ_attr = f' data-pl-occupancy="{occ}"' if occ else ""
        occ_cls = " pl-expense-row--occupancy" if occ else ""
        major = ""
        if detail_i == 0:
            major = (
                f'<td class="pl-v-cell pl-v-cell--major" rowspan="{total_detail}">'
                f'{v_label(major_expense, "pl-v-label pl-v-label--major")}</td>'
            )
        mid = ""
        if bucket == "fixed" and detail_i == 0:
            mid = (
                f'<td class="pl-v-cell pl-v-cell--mid" rowspan="{len(fixed_rows) + 1}">'
                f'{v_label(mid_fix, "pl-v-label pl-v-label--mid")}</td>'
            )
        elif bucket == "variable" and rid == var_rows[0][0]:
            mid = (
                f'<td class="pl-v-cell pl-v-cell--mid" rowspan="{len(var_rows) + 1}">'
                f'{v_label(mid_var, "pl-v-label pl-v-label--mid")}</td>'
            )
        edit_icon = "✎" if bucket == "variable" or rid not in ("rent", "asset_tax") else "✎"
        label_cell = (
            f'<th scope="row" class="pl-h-label pl-h-label--detail">'
            f'<span class="pl-edit-icon" aria-hidden="true">{edit_icon}</span>'
            f"<span>{label}</span></th>"
        )
        detail_i += 1
        return (
            f'<tr class="pl-data-row pl-expense-row{ occ_cls}" data-row="{rid}" '
            f'data-pl-section="expense-detail" data-pl-bucket="{bucket}"{ occ_attr}>'
            f"{major}{mid}{label_cell}"
            f'{data_cells(rid, editable=True)}'
            f"</tr>"
        )

    for item in fixed_rows:
        rid, ja, en, bucket = item[0], item[1], item[2], item[3]
        occ = item[4] if len(item) > 4 else None
        rows.append(detail_tr(rid, ja if is_ja else en, bucket, occ))

    rows.append(
        f'<tr class="pl-add-row" data-pl-section="expense-detail" data-pl-bucket="fixed">'
        f'<th scope="row" class="pl-h-label pl-h-label--detail"></th>'
        f'<td colspan="26" class="pl-add-row__cell">'
        f'<button type="button" class="pl-add-btn" disabled>{add_fix}</button></td></tr>'
    )
    detail_i += 1

    for item in var_rows:
        rid, ja, en, bucket = item[0], item[1], item[2], item[3]
        rows.append(detail_tr(rid, ja if is_ja else en, bucket, None))

    rows.append(
        f'<tr class="pl-add-row" data-pl-section="expense-detail" data-pl-bucket="variable">'
        f'<th scope="row" class="pl-h-label pl-h-label--detail"></th>'
        f'<td colspan="26" class="pl-add-row__cell">'
        f'<button type="button" class="pl-add-btn" disabled>{add_var}</button></td></tr>'
    )

    return "\n".join(rows)


def thead_html(lang: str, year: str = "2026") -> str:
    months = MONTHS_JA if lang == "ja" else MONTHS_EN
    corner = "損益表" if lang == "ja" else "Profit & Loss"
    amt = "金額" if lang == "ja" else "Amount"
    ratio = "比率" if lang == "ja" else "Ratio"
    total = "合計" if lang == "ja" else "Total"
    h1 = (
        f'<tr><th class="pl-corner" rowspan="2" scope="col">{corner}<br><span class="pl-corner-year">{year}</span></th>'
        f'<th class="pl-corner-mid" rowspan="2" scope="col"></th>'
        f'<th class="pl-corner-label" rowspan="2" scope="col"></th>'
    )
    for m in months:
        h1 += f'<th colspan="2" scope="colgroup">{m}</th>'
    h1 += f'<th colspan="2" scope="colgroup">{total}</th></tr>'
    h2 = "<tr>"
    for _ in range(13):
        h2 += f'<th scope="col">{amt}</th><th scope="col">{ratio}</th>'
    h2 += "</tr>"
    return h1 + h2


def page_paths(lang: str) -> dict[str, str]:
    if lang == "en":
        return {
            "asset": "../../../../",
            "annual": "../../annual/index.html",
            "monthly": "../../monthly/index.html",
            "pl_index": "index.html",
            "shell_other": "../../../../app/profit/pl/shell.html",
            "monthly_edit": "../../monthly/edit/index.html",
            "setting": "../../../../en/setting/",
            "forge_url": "https://forge-laboratory.com/en",
        }
    return {
        "asset": "../../../",
        "annual": "../../annual/index.html",
        "monthly": "../../monthly/index.html",
        "pl_index": "index.html",
        "shell_other": "../../../en/app/profit/pl/shell.html",
        "monthly_edit": "../../monthly/edit/index.html",
        "setting": "../../../en/setting/",
        "forge_url": "https://forge-laboratory.com",
    }


def render_page(lang: str) -> str:
    p = page_paths(lang)
    is_ja = lang == "ja"
    html_lang = "ja" if is_ja else "en"
    title = "損益表（PL）シェル" if is_ja else "Profit & Loss (PL) Shell"
    badge = "SHELL — セルは描画時に投入" if is_ja else "SHELL — cells filled at render time"
    year_l = "年度" if is_ja else "Year"
    back_edit = "← 月次編集へ" if is_ja else "← Monthly Edit"
    back_prod = "← 現行 PL 表" if is_ja else "← Current PL table"
    csv_l = "CSV取込" if is_ja else "Upload CSV"
    undo_l = "戻る" if is_ja else "Undo"
    nav = (
        ("年次", "Annual", p["annual"]),
        ("月次", "Monthly", p["monthly"]),
        ("日次", "Daily", "#"),
        ("考察", "Insight", "../../monthly/index.html?open=insight"),
    )
    nav_html = ""
    for ja, en, href in nav:
        nav_html += f"""
          <li class="global-nav-item">
            <a href="{href}" class="nav-frame-btn" aria-label="{en if not is_ja else ja}">
              <span class="btn-mode-frame">
                <img src="{p['asset']}images/button_frame.svg" alt="" class="btn-mode-frame-img" aria-hidden="true">
                <span class="btn-mode-text nav-btn-text">{ja if is_ja else en}</span>
              </span>
            </a>
          </li>"""

    tbody = render_tbody(lang)
    thead = thead_html(lang)

    return f"""<!DOCTYPE html>
<html lang="{html_lang}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} | KPI Navigator</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{p['asset']}register/style.css">
  <style>
    body.pl-shell-page .profile-main {{
      padding: 16px 0 48px;
      align-items: stretch;
      width: 100%;
    }}
    .pl-shell-wrap {{
      --pl-cyan: #58e1f3;
      --pl-green: #0f9403;
      --pl-major-w: 36px;
      --pl-mid-w: 32px;
      --pl-label-w: 200px;
      width: min(100%, 100%);
      margin: 0 auto;
      padding: 0 12px 32px;
      box-sizing: border-box;
    }}
    .pl-shell-badge {{
      display: inline-block;
      margin-left: 10px;
      padding: 2px 8px;
      font-size: 10px;
      border: 1px solid var(--pl-green);
      color: #b8ffb0;
      vertical-align: middle;
    }}
    .pl-toolbar {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 10px 14px;
      margin-bottom: 10px;
      min-height: 40px;
    }}
    .pl-toolbar__left {{ display: flex; flex-wrap: wrap; align-items: center; gap: 10px 14px; flex: 1; }}
    .pl-toolbar__actions {{ display: flex; gap: 8px; margin-left: auto; }}
    .pl-year-label {{ font-size: 12px; color: var(--pl-cyan); font-weight: 600; }}
    .pl-year-select, .pl-toolbar__select {{
      height: 32px; min-width: 100px; padding: 0 8px;
      border: 1px solid rgba(88, 225, 243, 0.45); border-radius: 3px;
      background: rgba(8, 18, 22, 0.95); color: var(--pl-cyan);
      font-family: 'Orbitron', sans-serif; font-size: 12px;
    }}
    .pl-toolbar__back {{ color: var(--pl-cyan); font-size: 0.88rem; font-weight: 600; text-decoration: none; }}
    .pl-toolbar__btn {{
      height: 32px; padding: 0 14px; border: 1px solid rgba(88, 225, 243, 0.45);
      background: rgba(88, 225, 243, 0.12); color: var(--pl-cyan);
      font-family: 'Orbitron', sans-serif; font-size: 11px; cursor: pointer;
    }}
    .pl-toolbar__btn--save {{ border-color: rgba(15, 148, 3, 0.8); background: rgba(15, 148, 3, 0.2); }}
    .pl-toolbar__btn:disabled {{ opacity: 0.45; cursor: not-allowed; }}
    .pl-head-bar {{ margin-bottom: 8px; }}
    .pl-title {{ margin: 0; font-size: 1.05rem; color: var(--pl-cyan); font-weight: 600; }}
    .pl-meta {{ margin: 4px 0 0; font-size: 0.78rem; color: rgba(255,255,255,0.75); font-family: system-ui, sans-serif; }}
    .pl-scroll {{
      overflow: auto;
      max-height: calc(100vh - 200px);
      border: 2px solid var(--pl-green);
      background: rgba(8, 18, 22, 0.92);
    }}
    .pl-table {{
      border-collapse: separate;
      border-spacing: 0;
      font-size: 12px;
      font-family: 'Orbitron', sans-serif;
      min-width: 2200px;
    }}
    .pl-table th, .pl-table td {{
      border: 0.5px solid rgba(88, 225, 243, 0.35);
      padding: 5px 8px;
      vertical-align: middle;
      background: #0a1418;
      color: #58e1f3;
    }}
    .pl-table thead th {{
      background: #12252b;
      text-align: center;
      font-weight: 600;
      position: sticky;
      top: 0;
      z-index: 5;
    }}
    .pl-corner {{ position: sticky; left: 0; z-index: 8; min-width: var(--pl-major-w); text-align: center !important; }}
    .pl-corner-mid {{ position: sticky; left: var(--pl-major-w); z-index: 7; min-width: var(--pl-mid-w); }}
    .pl-corner-label {{ position: sticky; left: calc(var(--pl-major-w) + var(--pl-mid-w)); z-index: 7; min-width: var(--pl-label-w); }}
    .pl-corner-year {{ font-size: 10px; font-weight: 400; opacity: 0.85; }}
    .pl-num, .pl-pct {{ text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; min-width: 72px; }}
    .pl-v-cell {{ padding: 4px 2px; text-align: center; background: rgba(88, 225, 243, 0.06); }}
    .pl-v-cell--major {{ position: sticky; left: 0; z-index: 4; background: rgba(88, 225, 243, 0.1); min-width: var(--pl-major-w); }}
    .pl-v-cell--mid {{ position: sticky; left: var(--pl-major-w); z-index: 3; background: rgba(88, 225, 243, 0.07); min-width: var(--pl-mid-w); }}
    .pl-v-cell--empty {{ background: #0a1418; }}
    .pl-h-label {{
      position: sticky;
      left: calc(var(--pl-major-w) + var(--pl-mid-w));
      z-index: 2;
      min-width: var(--pl-label-w);
      max-width: var(--pl-label-w);
      text-align: left !important;
      font-weight: 500;
      background: #0f1a1e;
      box-shadow: 1px 0 0 rgba(88, 225, 243, 0.35);
    }}
    .pl-h-label--profit {{ font-weight: 700; font-size: 13px; }}
    .pl-h-label--kpi {{ font-weight: 400; font-size: 11px; color: rgba(88, 225, 243, 0.9); }}
    .pl-h-label--detail {{ display: flex; align-items: center; gap: 6px; font-size: 11px; }}
    .pl-row-bold .pl-h-label {{ font-weight: 700; }}
    .pl-v-label {{
      writing-mode: vertical-rl;
      text-orientation: mixed;
      transform: rotate(180deg);
      white-space: nowrap;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      color: var(--pl-cyan);
      letter-spacing: 0.04em;
    }}
    .pl-v-label--major {{ font-weight: 700; font-size: 14px; min-height: 48px; }}
    .pl-v-label--mid {{ font-weight: 600; font-size: 12px; min-height: 40px; }}
    .pl-kpi-head__label {{ padding: 0 !important; }}
    .pl-kpi-toggle {{
      width: 100%; margin: 0; padding: 6px 8px; border: 0; background: transparent;
      color: var(--pl-cyan); font-family: inherit; font-size: 11px; text-align: left; cursor: pointer;
    }}
    .pl-kpi-head__hint {{ font-size: 10px; color: rgba(88, 225, 243, 0.5); }}
    body.pl-kpi-collapsed .pl-kpi-group {{ display: none; }}
    .pl-profit-row .pl-num, .pl-profit-row .pl-pct {{ font-weight: 700; }}
    .pl-edit-icon {{
      flex: 0 0 16px; width: 16px; height: 16px;
      border: 1px solid rgba(88, 225, 243, 0.45); border-radius: 2px;
      background: rgba(88, 225, 243, 0.1); font-size: 9px; line-height: 14px; text-align: center;
    }}
    .pl-add-row__cell {{ text-align: center; background: rgba(88, 225, 243, 0.03); }}
    .pl-add-btn {{
      border: 1px dashed rgba(88, 225, 243, 0.4); background: transparent;
      color: rgba(88, 225, 243, 0.7); font-family: inherit; font-size: 10px; padding: 3px 10px;
    }}
    .pl-expense-row--occupancy[data-pl-occupancy="owned"] {{ display: none; }}
    .pl-shell-page[data-occupancy="owned"] .pl-expense-row--occupancy[data-pl-occupancy="rent"] {{ display: none; }}
    .pl-shell-page[data-occupancy="owned"] .pl-expense-row--occupancy[data-pl-occupancy="owned"] {{ display: table-row; }}
  </style>
</head>
<body class="si-fi profile-page pl-shell-page pl-page" id="body-el">
  <header class="site-header">
    <div class="header-inner">
      <div class="header-logo">
        <a href="{p['forge_url']}" class="logo-link" target="_blank" rel="noopener noreferrer">
          <img src="{p['asset']}images/forge_lab_logo.png" alt="FORGE LABORATORY" class="logo-img">
        </a>
      </div>
      <nav class="global-nav" aria-label="Main">
        <ul class="global-nav-list">{nav_html}
        </ul>
      </nav>
    </div>
  </header>
  <div class="profile-page">
    <main class="profile-main">
      <div class="pl-shell-wrap">
        <div class="pl-toolbar">
          <div class="pl-toolbar__left">
            <label class="pl-year-label" for="pl-year-select">{year_l}</label>
            <select id="pl-year-select" class="pl-year-select" aria-label="{year_l}"><option selected>2026</option></select>
            <a class="pl-toolbar__back" href="{p['monthly_edit']}">{back_edit}</a>
          </div>
          <div class="pl-toolbar__actions">
            <button type="button" class="pl-toolbar__btn" disabled>{csv_l}</button>
            <button type="button" class="pl-toolbar__btn" disabled>{undo_l}</button>
            <button type="button" class="pl-toolbar__btn pl-toolbar__btn--save" disabled>Save</button>
          </div>
        </div>
        <div class="pl-head-bar">
          <h1 class="pl-title">{title}<span class="pl-shell-badge">{badge}</span></h1>
          <p class="pl-meta">Figma 1枚表レイアウト · 行順 <code>excel/PL表例4.pdf</code> · <a href="{p['pl_index']}" style="color:#58e1f3">{back_prod}</a> · <a href="{p['shell_other']}" style="color:#58e1f3">{"EN" if is_ja else "JA"}</a></p>
        </div>
        <div class="pl-scroll" role="region" aria-label="{title}">
          <table class="pl-table" id="pl-shell-table">
            <thead>{thead}</thead>
            <tbody id="pl-shell-tbody">
{tbody}
            </tbody>
          </table>
        </div>
      </div>
    </main>
  </div>
  <script>
    /* シェル — 数値投入は window.plShell.renderRow(rowId, periodIndex, amount, ratioPct) 等で後付け */
    (function () {{
      var kpiBtn = document.getElementById('pl-kpi-toggle');
      if (kpiBtn) {{
        kpiBtn.addEventListener('click', function () {{
          var collapsed = body.classList.toggle('pl-kpi-collapsed');
          kpiBtn.setAttribute('aria-expanded', collapsed ? 'false' : 'true');
          var icon = kpiBtn.querySelector('.pl-kpi-toggle__icon');
          if (icon) icon.textContent = collapsed ? '▶' : '▼';
        }});
      }}
      window.plShell = {{
        /** 1行×1期間のセルに値を入れる（period: 0-11 月次, 'annual'） */
        setCell: function (rowId, period, amountText, ratioText) {{
          var key = period === 'annual' || period === 12 ? 'annual' : String(period);
          document.querySelectorAll('[data-row="' + rowId + '"][data-period="' + key + '"]').forEach(function (el) {{
            if (el.getAttribute('data-pl-cell') === 'amount') el.textContent = amountText != null ? amountText : '';
            if (el.getAttribute('data-pl-cell') === 'ratio') el.textContent = ratioText != null ? ratioText : '';
          }});
        }},
        clearAll: function () {{
          document.querySelectorAll('[data-pl-cell]').forEach(function (el) {{ el.textContent = ''; }});
        }}
      }};
    }})();
  </script>
</body>
</html>
"""


def main() -> None:
    ja = ROOT / "app/profit/pl/shell.html"
    en = ROOT / "en/app/profit/pl/shell.html"
    ja.parent.mkdir(parents=True, exist_ok=True)
    en.parent.mkdir(parents=True, exist_ok=True)
    ja.write_text(render_page("ja"), encoding="utf-8")
    en.write_text(render_page("en"), encoding="utf-8")
    print("Wrote", ja, en)


if __name__ == "__main__":
    main()
