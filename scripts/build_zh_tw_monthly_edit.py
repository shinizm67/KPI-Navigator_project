#!/usr/bin/env python3
"""zh-tw Monthly Edit: scaffold from EN + chrome/toolbar/modals i18n.

zh-tw/app/monthly already deep-links to ../monthly/edit/index.html; this page
was the missing tree node (easiest Tars-friendly follow-up after Annual/Monthly
waves and Insight vertical-label fix).
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_zh_tw_profile_pages import (  # noqa: E402
    _patch_lang_switcher,
    _strip_export_script,
)

SRC = ROOT / "en" / "app" / "monthly" / "edit" / "index.html"
DST = ROOT / "zh-tw" / "app" / "monthly" / "edit" / "index.html"

# Longest-first where overlaps matter
REPLACEMENTS = [
    ('<html lang="en" translate="no">', '<html lang="zh-TW">'),
    ('<html lang="en">', '<html lang="zh-TW">'),
    ('<meta http-equiv="content-language" content="en">\n', ""),
    (
        "Monthly Edit | KPI Navigator | FORGE LABORATORY",
        "月度編輯 | KPI Navigator | FORGE LABORATORY",
    ),
    (
        'href="../../../setting/style.css"',
        'href="../../../../en/setting/style.css"',
    ),
    ("https://forge-laboratory.com/en", "https://forge-laboratory.com"),
    # Page / toolbar
    (">Monthly bulk edit</h2>", ">月度批次編輯</h2>"),
    ('aria-label="Jump to today"', 'aria-label="跳至今天"'),
    (">\n        Today\n      </button>", ">\n        今天\n      </button>"),
    (
        'aria-label="Sales input path (Annual / Monthly)"',
        'aria-label="銷售輸入路徑（年度 / 月度）"',
    ),
    (">Sales Input</p>", ">銷售輸入</p>"),
    (
        'aria-label="Switch sales input between Annual and Monthly"',
        'aria-label="在年度與月度之間切換銷售輸入"',
    ),
    ('aria-label="Undo last change"', 'aria-label="復原上一步"'),
    (">\n        Undo\n      </button>", ">\n        復原\n      </button>"),
    ('aria-label="Import sales CSV"', 'aria-label="匯入銷售 CSV"'),
    (
        'title="Import daily sales from CSV/Excel (.xlsx). For expenses, use \'Upload Expenses\' on the PL page."',
        'title="以 CSV/Excel（.xlsx）匯入每日銷售。支出請使用 PL 頁的「匯入支出」。"',
    ),
    (
        'data-tooltip="Import daily sales from CSV/Excel (.xlsx). For expenses, use \'Upload Expenses\' on the PL page."',
        'data-tooltip="以 CSV/Excel（.xlsx）匯入每日銷售。支出請使用 PL 頁的「匯入支出」。"',
    ),
    (">\n        Upload Sales\n      </button>", ">\n        匯入銷售\n      </button>"),
    (">Save</button>", ">儲存</button>"),
    (
        'aria-label="Open Profit and Loss (P&amp;L) table"',
        'aria-label="開啟損益表（PL）"',
    ),
    (
        'title="Open Profit and Loss (P&amp;L) table"',
        'title="開啟損益表（PL）"',
    ),
    (">\n          View Profit &amp; Loss\n        </button>", ">\n          檢視損益表\n        </button>"),
    ('aria-label="Hide summary panel"', 'aria-label="隱藏摘要面板"'),
    ('title="Close below Analyze area"', 'title="關閉下方分析區"'),
    ('aria-label="Previous month"', 'aria-label="上個月"'),
    (">◀ Prev</button>", ">◀ 上月</button>"),
    ('aria-label="Choose year and month"', 'aria-label="選擇年月"'),
    ('aria-label="Next month"', 'aria-label="下個月"'),
    (">Next ▶</button>", ">下月 ▶</button>"),
    (">Year</span>", ">年</span>"),
    ('aria-label="Open daily notes"', 'aria-label="開啟每日備註"'),
    ('title="Open daily notes"', 'title="開啟每日備註"'),
    (">\n          Daily Notes\n        </button>", ">\n          每日備註\n        </button>"),
    ('aria-label="Open Strategy Note"', 'aria-label="開啟策略備註"'),
    ('title="Open Strategy Note"', 'title="開啟策略備註"'),
    (">\n          Strategy Note\n        </button>", ">\n          策略備註\n        </button>"),
    (">Zoom</label>", ">縮放</label>"),
    ('aria-label="Zoom out"', 'aria-label="縮小"'),
    ('aria-label="Zoom in"', 'aria-label="放大"'),
    (">Date</div>", ">日期</div>"),
    ('aria-label="Month daily grid"', 'aria-label="月度每日網格"'),
    # Memo modal
    ('aria-label="Close"', 'aria-label="關閉"'),
    (">Daily Notes</h2>", ">每日備註</h2>"),
    (">Prev</button>", ">上月</button>"),
    (">Next</button>", ">下月</button>"),
    (">Today</button>", ">今天</button>"),
    (">Close daily notes</p>", ">關閉每日備註</p>"),
    (
        ">Choose whether to save or discard your changes.</p>",
        ">請選擇儲存或捨棄變更後關閉。</p>",
    ),
    (">\n          Save and close\n        </button>", ">\n          儲存並關閉\n        </button>"),
    (
        ">\n          Close without saving\n        </button>",
        ">\n          不儲存並關閉\n        </button>",
    ),
    (">\n          Cancel\n        </button>", ">\n          取消\n        </button>"),
    # Strategy note modal
    (">Strategy Note</h2>", ">策略備註</h2>"),
    (">User Note</label>", ">使用者備註</label>"),
    (
        ">Saved via Monthly Edit Save to appear on Insight.</p>",
        ">於月度編輯按儲存後，會顯示在洞察中。</p>",
    ),
    # Path / sales-data choosers
    (">Switch input surface</p>", ">切換輸入畫面</p>"),
    (
        ">You have unsaved changes. Save before switching, or discard and switch.</p>",
        ">尚有未儲存的變更。請先儲存再切換，或捨棄後切換。</p>",
    ),
    (">\n          Save and switch\n        </button>", ">\n          儲存並切換\n        </button>"),
    (
        ">\n          Switch without saving\n        </button>",
        ">\n          不儲存並切換\n        </button>",
    ),
    (">Close Sales Data</p>", ">關閉銷售資料</p>"),
    (
        ">Choose whether to save your changes before closing.</p>",
        ">關閉前請選擇是否儲存變更。</p>",
    ),
    # Tutorial
    ('aria-label="Tutorial visibility"', 'aria-label="教學顯示設定"'),
    (">Tutorial</h2>", ">教學</h2>"),
    ('aria-label="Toggle tutorial visibility"', 'aria-label="切換教學顯示"'),
]


def ensure_pages_generated_entry() -> None:
    path = ROOT / "scripts" / "build_site_chrome.py"
    text = path.read_text(encoding="utf-8")
    needle = '{"path": "zh-tw/app/monthly/edit/index.html"'
    if needle in text:
        print("PAGES_GENERATED already has zh-tw monthly/edit")
        return
    anchor = (
        '    {\n'
        '        "path": "en/app/monthly/edit/index.html", "lang": "en",\n'
        '        "base": "../../../", "img": "../../../../", "active": "monthly",\n'
        '        "daily": "overlay", "daily_href": "../index.html?open=daily",\n'
        '        "profit_href": "../index.html?open=insight", "footer": False,\n'
        '    },\n'
    )
    insert = (
        anchor
        + '    {\n'
        '        "path": "zh-tw/app/monthly/edit/index.html", "lang": "zh-tw",\n'
        '        "base": "../../../", "img": "../../../../", "active": "monthly",\n'
        '        "daily": "overlay", "daily_href": "../index.html?open=daily",\n'
        '        "profit_href": "../index.html?open=insight", "footer": False,\n'
        '    },\n'
    )
    if anchor not in text:
        raise SystemExit("could not find EN monthly/edit PAGES_GENERATED entry")
    path.write_text(text.replace(anchor, insert, 1), encoding="utf-8")
    print("registered zh-tw monthly/edit in PAGES_GENERATED")


def ensure_export_target() -> None:
    path = ROOT / "scripts" / "apply_kpi_pl_mep_export.py"
    text = path.read_text(encoding="utf-8")
    line = '    "zh-tw/app/monthly/edit/index.html",\n'
    if line in text:
        print("export TARGET already has zh-tw monthly/edit")
        return
    anchor = '    "en/app/monthly/edit/index.html",\n'
    if anchor not in text:
        raise SystemExit("could not find en monthly/edit export target")
    path.write_text(text.replace(anchor, anchor + line, 1), encoding="utf-8")
    print("registered zh-tw monthly/edit in export TARGET")


def scaffold_from_en() -> None:
    DST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SRC, DST)
    text = _strip_export_script(DST.read_text(encoding="utf-8"))
    missing = []
    for a, b in REPLACEMENTS:
        if a not in text:
            missing.append(a[:90])
            continue
        text = text.replace(a, b)
    text = text.replace("<head>\n\n  <meta", "<head>\n  <meta")
    text = _patch_lang_switcher(
        text,
        active="zh-tw",
        url_ja="../../../../app/monthly/edit/index.html",
        url_en="../../../../en/app/monthly/edit/index.html",
        url_zh_tw="index.html",
    )
    DST.write_text(text, encoding="utf-8")
    if missing:
        print("WARN missing replacements:")
        for m in missing:
            print(" ", repr(m))
    print(f"wrote {DST.relative_to(ROOT)} ({DST.stat().st_size} bytes)")


def wire_ja_en_lang_switchers() -> None:
    mapping = {
        ("app/monthly/edit/index.html", "ja"): (
            "index.html",
            "../../../en/app/monthly/edit/index.html",
            "../../../zh-tw/app/monthly/edit/index.html",
        ),
        ("en/app/monthly/edit/index.html", "en"): (
            "../../../../app/monthly/edit/index.html",
            "index.html",
            "../../../../zh-tw/app/monthly/edit/index.html",
        ),
    }
    for (rel, active), (url_ja, url_en, url_zh) in mapping.items():
        path = ROOT / rel
        text = _patch_lang_switcher(
            path.read_text(encoding="utf-8"),
            active=active,
            url_ja=url_ja,
            url_en=url_en,
            url_zh_tw=url_zh,
        )
        path.write_text(text, encoding="utf-8")
        print(f"wired lang switcher: {rel}")


def refresh_chrome_and_export() -> None:
    rc = subprocess.call(
        [sys.executable, str(ROOT / "scripts" / "build_site_chrome.py"), "generated"],
        cwd=str(ROOT / "scripts"),
    )
    if rc != 0:
        raise SystemExit(f"build_site_chrome generated failed: {rc}")
    rc = subprocess.call(
        [sys.executable, str(ROOT / "scripts" / "apply_kpi_pl_mep_export.py")],
        cwd=str(ROOT),
    )
    if rc != 0:
        raise SystemExit(f"apply_kpi_pl_mep_export failed: {rc}")


def verify() -> None:
    t = DST.read_text(encoding="utf-8")
    checks = [
        ('lang="zh-TW"', 'lang="zh-TW"' in t),
        ("title 月度編輯", "月度編輯 | KPI Navigator" in t),
        ("儲存", ">儲存<" in t or ">儲存</button>" in t),
        ("復原", "復原" in t),
        ("每日備註", "每日備註" in t),
        ("策略備註", "策略備註" in t),
        ("chrome 月度", ">月度<" in t or "月度" in t),
        ("style path", "en/setting/style.css" in t),
        ("lang TW active", "lang-option-zh-tw lang-option-active" in t),
        ("link monthly", 'href="../index.html"' in t or "monthly" in t),
        ("export", "KPI-PL-MEP-EXPORT" in t),
        ("no EN bulk title", "Monthly bulk edit" not in t),
    ]
    for name, ok in checks:
        print(("OK" if ok else "FAIL"), name)
        if not ok:
            raise SystemExit(1)
    ja = (ROOT / "app/monthly/edit/index.html").read_text(encoding="utf-8")
    en = (ROOT / "en/app/monthly/edit/index.html").read_text(encoding="utf-8")
    assert 'data-url-zh-tw="../../../zh-tw/app/monthly/edit/index.html"' in ja
    assert 'data-url-zh-tw="../../../../zh-tw/app/monthly/edit/index.html"' in en
    print("verify: ALL OK")


def main() -> None:
    ensure_pages_generated_entry()
    ensure_export_target()
    scaffold_from_en()
    wire_ja_en_lang_switchers()
    refresh_chrome_and_export()
    text = _patch_lang_switcher(
        DST.read_text(encoding="utf-8"),
        active="zh-tw",
        url_ja="../../../../app/monthly/edit/index.html",
        url_en="../../../../en/app/monthly/edit/index.html",
        url_zh_tw="index.html",
    )
    DST.write_text(text, encoding="utf-8")
    verify()
    print("build_zh_tw_monthly_edit: OK")


if __name__ == "__main__":
    main()
