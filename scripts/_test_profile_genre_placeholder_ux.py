# -*- coding: utf-8 -*-
"""Profile genre placeholder UX: prompts never become input.value."""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
FAILED = 0
PASSED = 0

EDIT = {
    "jp": ROOT / "setting/profile_edit.html",
    "en": ROOT / "en/setting/profile_edit.html",
    "zh": ROOT / "zh-tw/setting/profile_edit.html",
}
BT_JS = ROOT / "js" / "kpi-business-type.js"
CANONICAL = ("restaurant", "retail", "hair_salon", "fitness", "hotel", "other")
SENTINEL = "— Select Industry first —"

PLACEHOLDERS = {
    "jp": {
        "need": "先に業種を選択してください",
        "ready": "候補から選択するか、ご自身の業態・ジャンルを自由に入力してください",
    },
    "en": {
        "need": "Select a business type first",
        "ready": "Choose a suggestion, or type your own category / genre.",
    },
    "zh": {
        "need": "請先選擇業態",
        "ready": "可從候選項目選擇，或自行輸入您的業態／類型。",
    },
}


def assert_true(cond: bool, msg: str) -> None:
    global PASSED, FAILED
    if cond:
        PASSED += 1
        return
    FAILED += 1
    print("FAIL:", msg)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def is_genre_prompt(v: str) -> bool:
    s = str(v or "").strip()
    if not s:
        return True
    n = re.sub(r"^[—–-]\s*|\s*[—–-]$", "", s).strip().lower()
    return n in (
        "select industry first",
        "select a business type first",
        "select",
    ) or s in (
        "先に業種を選択してください",
        "請先選擇業態",
    )


def sync_state(industry: str, current_value: str, suggestions_by_type: dict[str, list[str]], ph: dict) -> dict:
    raw = (industry or "").strip()
    typ = raw
    rec = suggestions_by_type.get(typ) if typ else None
    value = "" if is_genre_prompt(current_value) else str(current_value or "")
    placeholder = ph["ready"] if typ else ph["need"]
    suggestions = list(rec or []) if typ else []
    return {"value": value, "placeholder": placeholder, "suggestions": suggestions}


def genre_map(html: str) -> str:
    return html.split("var GENRE_BY_TYPE = {", 1)[1].split("};", 1)[0]


def suggestions(html: str, key: str) -> list[str]:
    block = genre_map(html)
    parts = block.split(f"{key}:", 1)[1]
    nxt = min(
        [parts.find(f"{k}:") for k in CANONICAL if f"{k}:" in parts[1:]],
        default=len(parts),
    )
    chunk = parts[: nxt if nxt > 0 else len(parts)]
    found = re.search(r"suggestions:\s*\[(.*?)\]", chunk, re.S)
    if not found:
        return []
    return re.findall(r"'([^']+)'", found.group(1))


def test_placeholders_and_sentinels() -> None:
    for loc, path in EDIT.items():
        html = path.read_text(encoding="utf-8")
        ph = PLACEHOLDERS[loc]
        assert_true("KPI-PROFILE-GENRE-PLACEHOLDER" in html, f"{loc} marker")
        assert_true(f'placeholder="{ph["ready"]}"' in html, f"{loc} html placeholder ready")
        assert_true(f"GENRE_PLACEHOLDER_NEED_TYPE = '{ph['need']}'" in html, f"{loc} unselected placeholder")
        assert_true(f"GENRE_PLACEHOLDER_READY = '{ph['ready']}'" in html, f"{loc} selected placeholder")
        assert_true("genreInput.placeholder" in html, f"{loc} sets placeholder not value for prompt")
        assert_true("isGenrePrompt(g) ? '' : g" in html, f"{loc} save strips prompt")
        assert_true("if (isGenrePrompt(savedGenre)) savedGenre = ''" in html, f"{loc} hydrate strips prompt")
        assert_true("if (type && rec)" in html, f"{loc} no suggestions until type chosen")
        assert_true("wear_shop" not in html, f"{loc} Wear Shop not a BT option")
        assert_true("value=\"cafe\"" not in html, f"{loc} Cafe not a BT option")
        assert_true("office-mode" in html, f"{loc} Office/Sci-Fi share same page")
        assert_true(html.count("function syncGenreField") == 1, f"{loc} single genre sync (no mode fork)")

    jp = EDIT["jp"].read_text(encoding="utf-8")
    assert_true("先に業種を選択してください" in jp, "JP unselected copy")
    jp_input = jp.split('id="profile-genre"', 1)[1].split(">", 1)[0]
    assert_true("Select Industry first" not in jp_input, "JP input tag is not English prompt")
    assert_true("Select a business type first" not in jp_input, "JP input tag not EN placeholder")


def test_runtime_contract() -> None:
    jp = EDIT["jp"].read_text(encoding="utf-8")
    by_type = {k: suggestions(jp, k) for k in ("restaurant", "retail", "hair_salon")}
    ph = PLACEHOLDERS["jp"]

    empty = sync_state("", "", by_type, ph)
    assert_true(empty["value"] == "", "1 JP unselected value empty")
    assert_true(empty["placeholder"] == ph["need"], "1 JP unselected placeholder JA")
    assert_true(empty["suggestions"] == [], "1 JP unselected no suggestions")

    rest = sync_state("restaurant", SENTINEL, by_type, ph)
    assert_true(rest["value"] == "", "2 sentinel not kept as value")
    assert_true(rest["placeholder"] == ph["ready"], "2 JP restaurant placeholder ready")
    assert_true("イタリアン" in rest["suggestions"] and "寿司" in rest["suggestions"], "2 JP restaurant suggestions")

    retail = sync_state("retail", "", by_type, ph)
    assert_true(retail["value"] == "", "3 JP retail value empty")
    assert_true("アパレル" in retail["suggestions"] and "生活用品" in retail["suggestions"], "3 JP retail suggestions")
    assert_true("イタリアン" not in retail["suggestions"], "3 retail list is not restaurant")

    saved = sync_state("retail", "アパレル", by_type, ph)
    assert_true(saved["value"] == "アパレル", "4 saved genre stays in value")
    assert_true(saved["placeholder"] == ph["ready"], "4 placeholder is not the saved genre")

    changed = sync_state("hair_salon", "アパレル", by_type, ph)
    assert_true(changed["value"] == "アパレル", "5 BT change does not delete saved genre")
    assert_true("美容室" in changed["suggestions"], "5 hair salon suggestions after change")

    free = sync_state("other", "オリジナル業態", by_type, ph)
    assert_true(free["value"] == "オリジナル業態", "6 free text kept")

    en = sync_state("restaurant", "", {k: suggestions(EDIT["en"].read_text(encoding="utf-8"), k) for k in ("restaurant",)}, PLACEHOLDERS["en"])
    assert_true(en["placeholder"] == PLACEHOLDERS["en"]["ready"], "7 EN placeholder")
    assert_true("Italian" in en["suggestions"], "7 EN restaurant suggestions")

    zh_html = EDIT["zh"].read_text(encoding="utf-8")
    zh = sync_state("", SENTINEL, {k: suggestions(zh_html, k) for k in ("restaurant",)}, PLACEHOLDERS["zh"])
    assert_true(zh["placeholder"] == PLACEHOLDERS["zh"]["need"], "8 ZH-TW unselected placeholder")
    assert_true(zh["value"] == "", "8 ZH-TW sentinel stripped")

    assert_true(is_genre_prompt(SENTINEL), "9 English industry-first sentinel detected")
    assert_true(not is_genre_prompt("イタリアン"), "9 real genre is not a prompt")


def test_canonical_and_modes() -> None:
    bt = BT_JS.read_text(encoding="utf-8")
    for code in CANONICAL:
        assert_true(f"'{code}'" in bt, f"12 canonical {code}")
    assert_true("wear_shop: 'retail'" in bt, "13 legacy wear_shop maps")
    canon_block = bt.split("var CANONICAL = [", 1)[1].split("];", 1)[0]
    assert_true("'wear_shop'" not in canon_block, "13 Wear Shop not a canonical option")
    assert_true("'cafe'" not in canon_block, "13 Cafe not a canonical option")
    jp = EDIT["jp"].read_text(encoding="utf-8")
    assert_true("kpi-office-mode" in jp, "10/11 Office toggle on same Profile source")
    assert_true("bodyEl.classList.toggle('office-mode')" in jp or 'classList.toggle("office-mode")' in jp or "classList.toggle('office-mode')" in jp, "10/11 Sci-Fi/Office class toggle")
    assert_true(jp.count("var GENRE_BY_TYPE") == 1, "10/11 one genre map for both modes")


def test_unit5_genre_and_foundation() -> None:
    u5g = load_module("u5_profile_genre", SCRIPTS / "_test_profile_genre_ux.py")
    rc = u5g.main()
    assert_true(rc == 0, "Unit 5 profile genre still green")
    u5a = load_module("u5a_bt_foundation", SCRIPTS / "_test_business_type_foundation.py")
    rc2 = u5a.main()
    assert_true(rc2 == 0, "Unit 5A business type foundation still green")


def main() -> int:
    test_placeholders_and_sentinels()
    test_runtime_contract()
    test_canonical_and_modes()
    test_unit5_genre_and_foundation()
    print(f"passed={PASSED} failed={FAILED}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
