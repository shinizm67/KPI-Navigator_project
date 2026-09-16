# -*- coding: utf-8 -*-
"""Unit 5B — Profile subcategory (genre) by Business Type."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAILED = 0
PASSED = 0

EDIT_PAGES = [
    ROOT / "setting/profile_edit.html",
    ROOT / "en/setting/profile_edit.html",
    ROOT / "zh-tw/setting/profile_edit.html",
]
VIEW_PAGES = [
    ROOT / "setting/profile.html",
    ROOT / "en/setting/profile.html",
    ROOT / "zh-tw/setting/profile.html",
]
CANONICAL = (
    "restaurant",
    "retail",
    "hair_salon",
    "fitness",
    "hotel",
    "other",
)
JP_EDIT = ROOT / "setting/profile_edit.html"
EN_EDIT = ROOT / "en/setting/profile_edit.html"
ZH_EDIT = ROOT / "zh-tw/setting/profile_edit.html"


def assert_true(cond: bool, msg: str) -> None:
    global FAILED, PASSED
    if cond:
        PASSED += 1
        return
    FAILED += 1
    print("FAIL:", msg)


def genre_map(html: str) -> str:
    return html.split("var GENRE_BY_TYPE = {", 1)[1].split("};", 1)[0]


def test_a_restaurant_jp() -> None:
    html = JP_EDIT.read_text(encoding="utf-8")
    block = genre_map(html)
    rest = block.split("restaurant:", 1)[1].split("retail:", 1)[0]
    assert_true("料理ジャンル（任意）" in rest, "A JP restaurant label")
    for s in ("イタリアン", "和食", "カフェ", "バー", "居酒屋", "焼肉", "寿司"):
        assert_true(s in rest, f"A JP restaurant suggestion {s}")
    assert_true("Italian" not in rest, "A JP restaurant suggestions are Japanese")
    assert_true('<input type="text" id="profile-genre"' in html, "A still free text")
    assert_true("<select id=\"profile-genre\"" not in html, "A not a fixed select")


def test_b_to_f_type_labels() -> None:
    jp = genre_map(JP_EDIT.read_text(encoding="utf-8"))
    assert_true("小売ジャンル（任意）" in jp.split("retail:", 1)[1].split("hair_salon:", 1)[0], "B retail label")
    for s in ("アパレル", "食品", "楽器", "雑貨", "お土産", "書店", "生活用品"):
        assert_true(s in jp, f"B retail JP {s}")
    salon = jp.split("hair_salon:", 1)[1].split("fitness:", 1)[0]
    assert_true("サロンタイプ（任意）" in salon, "C salon label")
    for s in ("美容室", "理容室", "カラー専門", "ヘッドスパ", "ネイル併設"):
        assert_true(s in salon, f"C salon {s}")
    fit = jp.split("fitness:", 1)[1].split("hotel:", 1)[0]
    assert_true("フィットネスタイプ（任意）" in fit, "D fitness label")
    for s in ("ジム", "パーソナルトレーニング", "ヨガ", "ピラティス", "スタジオ"):
        assert_true(s in fit, f"D fitness {s}")
    hotel = jp.split("hotel:", 1)[1].split("other:", 1)[0]
    assert_true("宿泊施設タイプ（任意）" in hotel, "E hotel label")
    for s in ("ホテル", "旅館", "ゲストハウス", "ビジネスホテル", "リゾート"):
        assert_true(s in hotel, f"E hotel {s}")
    other = jp.split("other:", 1)[1]
    assert_true("業種詳細（任意）" in other, "F other label")


def test_g_j_save_hydrate_preserve() -> None:
    for path in EDIT_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        save = html.split("var data = {", 1)[1].split("};", 1)[0]
        assert_true("genreEl.value" in save, f"G {rel} saves free-text")
        assert_true("getSelectText(genreEl)" not in html, f"G {rel} not select-only")
        genre_input = html.split('id="profile-genre" name="genre"', 1)[-1].split(">", 1)[0]
        assert_true("required" not in genre_input, f"G {rel} optional")
        assert_true("genreInput.value = savedGenre" in html, f"G {rel} hydrates any saved string")
        sync = html.split("function syncGenreField", 1)[1].split("if (industrySelect)", 1)[0]
        assert_true("genreInput.value" not in sync, f"J {rel} type change does not clear genre")
        assert_true("industrySelect.addEventListener('change', syncGenreField)" in html, f"I {rel} switches suggestions")
        assert_true("GENRE_BY_TYPE[type]" in html, f"I {rel} uses type map")


def test_h_tooltip() -> None:
    jp = JP_EDIT.read_text(encoding="utf-8")
    en = EN_EDIT.read_text(encoding="utf-8")
    zh = ZH_EDIT.read_text(encoding="utf-8")
    assert_true("profile-genre-tip-btn" in jp, "H JP tip button")
    assert_true("候補から選択するか、ご自身の業態・ジャンルを自由に入力してください。" in jp, "H JP tooltip")
    assert_true("Choose a suggestion, or type your own category / genre." in en, "H EN tooltip")
    assert_true("可從候選項目選擇，或自行輸入您的業態／類型。" in zh, "H ZH tooltip")
    css = (ROOT / "en" / "setting" / "style.css").read_text(encoding="utf-8")
    assert_true(".profile-genre-tip-panel" in css, "H tip panel CSS")
    assert_true("is-tip-open" in css, "H click/open state")


def test_k_localized_suggestions() -> None:
    en = genre_map(EN_EDIT.read_text(encoding="utf-8"))
    zh = genre_map(ZH_EDIT.read_text(encoding="utf-8"))
    assert_true("Italian" in en and "Yakiniku" in en, "K EN restaurant suggestions")
    assert_true("Apparel" in en and "Musical instruments" in en, "K EN retail suggestions")
    assert_true("義式料理" in zh and "燒肉" in zh, "K ZH restaurant suggestions")
    assert_true("服飾" in zh and "樂器" in zh, "K ZH retail suggestions")
    assert_true("イタリアン" not in en, "K EN page is not JP suggestions")
    assert_true("Italian" not in zh.split("restaurant:", 1)[1].split("retail:", 1)[0], "K ZH restaurant is not EN")
    jp_view = (ROOT / "setting/profile.html").read_text(encoding="utf-8")
    en_view = (ROOT / "en/setting/profile.html").read_text(encoding="utf-8")
    zh_view = (ROOT / "zh-tw/setting/profile.html").read_text(encoding="utf-8")
    assert_true("小売ジャンル（任意）" in jp_view, "K JP view has retail label")
    assert_true("Retail Genre (Optional)" in en_view, "K EN view has retail label")
    assert_true("零售類型（選填）" in zh_view, "K ZH view has retail label")
    assert_true("genreGroup.hidden = false" in jp_view, "K view always shows subcategory")
    assert_true('id="profile-genre-group" hidden' not in jp_view, "K view not restaurant-only hidden")


def test_always_visible_on_edit() -> None:
    for path in EDIT_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        assert_true('id="profile-genre-group"' in html, f"{rel} has genre group")
        assert_true('id="profile-genre-group" hidden' not in html, f"{rel} shown for all types")
        assert_true("genreGroup.hidden = false" in html, f"{rel} keeps field visible")


def test_l_canonical_and_forbidden() -> None:
    bt = (ROOT / "js" / "kpi-business-type.js").read_text(encoding="utf-8")
    for code in CANONICAL:
        assert_true(f"'{code}'" in bt, f"L helper still lists {code}")
    jp_reg = (ROOT / "register" / "registration_si-fi_jp" / "registration_si-fi_jp.html").read_text(encoding="utf-8")
    assert_true("profile-genre" not in jp_reg, "Registration unchanged")
    schema = (ROOT / "api" / "v1" / "schema.sql").read_text(encoding="utf-8")
    assert_true("business_type" not in schema.lower(), "no new schema column")
    store = (ROOT / "api" / "v1" / "store.php").read_text(encoding="utf-8")
    assert_true("profile-genre" not in store, "store.php untouched")
    catalog = (ROOT / "scripts" / "pl_line_catalog.py").read_text(encoding="utf-8")
    assert_true("RETAIL_EXPENSE_DETAIL_LINES" in catalog, "PL presets untouched")


def main() -> int:
    test_a_restaurant_jp()
    test_b_to_f_type_labels()
    test_g_j_save_hydrate_preserve()
    test_h_tooltip()
    test_k_localized_suggestions()
    test_always_visible_on_edit()
    test_l_canonical_and_forbidden()
    print(f"passed={PASSED} failed={FAILED}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
