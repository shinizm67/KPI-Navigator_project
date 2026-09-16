# -*- coding: utf-8 -*-
"""Unit 5B — Profile Genre UX: restaurant free text, hidden for other types."""
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
NON_RESTAURANT = ("retail", "hair_salon", "fitness", "hotel", "other")


def assert_true(cond: bool, msg: str) -> None:
    global FAILED, PASSED
    if cond:
        PASSED += 1
        return
    FAILED += 1
    print("FAIL:", msg)


def test_a_restaurant_shows_input() -> None:
    for path in EDIT_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        assert_true('id="profile-genre"' in html, f"A {rel} has genre field")
        assert_true('<input type="text" id="profile-genre"' in html, f"A {rel} uses text input")
        assert_true("<select id=\"profile-genre\"" not in html, f"A {rel} is not a fixed select")
        assert_true('list="profile-genre-suggestions"' in html, f"A {rel} has datalist")
        assert_true('value="Italian"' in html, f"A {rel} suggests Italian")
        assert_true('id="profile-genre-group" hidden' in html, f"A {rel} group can collapse")


def test_b_c_d_save_and_hydrate() -> None:
    for path in EDIT_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        save = html.split("var data = {", 1)[1].split("};", 1)[0]
        assert_true("genreEl.value" in save, f"B {rel} saves free-text value")
        assert_true("getSelectText(genreEl)" not in html, f"B {rel} no longer saves select label")
        assert_true(".trim()" in save, f"B {rel} trims genre")
        genre_input = html.split('id="profile-genre"', 1)[1].split(">", 1)[0]
        assert_true("required" not in genre_input, f"D {rel} genre is optional")
        assert_true("genreInput.value = savedGenre" in html, f"C {rel} hydrates saved genre as-is")
        assert_true("genreSelect.options" not in html, f"C {rel} does not require option match")
        vis = html.split("function syncGenreVisibility", 1)[1].split("function ", 1)[0]
        assert_true("genreInput.value" not in vis, f"K {rel} hide does not clear genre value")


def test_e_to_j_non_restaurant_hidden() -> None:
    css = (ROOT / "en" / "setting" / "style.css").read_text(encoding="utf-8")
    assert_true(".form-group-genre[hidden]" in css, "J hidden rule exists")
    assert_true("display: none !important" in css.split(".form-group-genre[hidden]", 1)[1][:200], "J no leftover gap")
    assert_true("visibility:hidden" not in css.split(".form-group-genre[hidden]", 1)[1][:200], "J not visibility-hidden")
    for path in EDIT_PAGES + VIEW_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        assert_true('id="profile-genre-group" hidden' in html, f"J {rel} starts collapsed")
        if path in EDIT_PAGES:
            assert_true("genreGroup.hidden = !isRestaurantIndustry(raw)" in html, f"E-I {rel} only restaurant shows")
            assert_true("=== 'restaurant'" in html, f"E-I {rel} restaurant-only gate")
            for code in NON_RESTAURANT:
                assert_true(code in CANONICAL, f"L {code} still canonical")
        else:
            assert_true("genreGroup.hidden = viewType !== 'restaurant'" in html, f"E-I {rel} view hides non-restaurant")


def test_k_preserve_across_type_change() -> None:
    for path in EDIT_PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        assert_true("genre: genreEl ? String(genreEl.value || '').trim() : ''" in html, f"K {rel} always persists genre")
        assert_true("genreInput.value = ''" not in html, f"K {rel} does not wipe on type change")


def test_l_canonical_and_forbidden_surfaces() -> None:
    bt = (ROOT / "js" / "kpi-business-type.js").read_text(encoding="utf-8")
    for code in CANONICAL:
        assert_true(f"'{code}'" in bt, f"L helper still lists {code}")
    jp_reg = (ROOT / "register" / "registration_si-fi_jp" / "registration_si-fi_jp.html").read_text(encoding="utf-8")
    assert_true("profile-genre" not in jp_reg, "Registration has no genre field")
    schema = (ROOT / "api" / "v1" / "schema.sql").read_text(encoding="utf-8")
    assert_true("business_type" not in schema.lower(), "no new schema column")
    store = (ROOT / "api" / "v1" / "store.php").read_text(encoding="utf-8")
    assert_true("profile-genre" not in store, "store.php untouched")
    catalog = (ROOT / "scripts" / "pl_line_catalog.py").read_text(encoding="utf-8")
    assert_true("RETAIL_EXPENSE_DETAIL_LINES" in catalog, "PL presets untouched by this unit")


def test_i18n_labels() -> None:
    jp_edit = (ROOT / "setting" / "profile_edit.html").read_text(encoding="utf-8")
    en_edit = (ROOT / "en" / "setting" / "profile_edit.html").read_text(encoding="utf-8")
    zh_edit = (ROOT / "zh-tw" / "setting" / "profile_edit.html").read_text(encoding="utf-8")
    assert_true("料理ジャンル（任意）" in jp_edit, "JP edit label")
    assert_true("Cuisine / Genre (Optional)" in en_edit, "EN edit label")
    assert_true("料理類型（選填）" in zh_edit, "ZH-TW edit label")
    jp_view = (ROOT / "setting" / "profile.html").read_text(encoding="utf-8")
    en_view = (ROOT / "en" / "setting" / "profile.html").read_text(encoding="utf-8")
    zh_view = (ROOT / "zh-tw" / "setting" / "profile.html").read_text(encoding="utf-8")
    assert_true("料理ジャンル（任意）" in jp_view, "JP view label")
    assert_true("Cuisine / Genre (Optional)" in en_view, "EN view label")
    assert_true("料理類型（選填）" in zh_view, "ZH-TW view label")


def main() -> int:
    test_a_restaurant_shows_input()
    test_b_c_d_save_and_hydrate()
    test_e_to_j_non_restaurant_hidden()
    test_k_preserve_across_type_change()
    test_l_canonical_and_forbidden_surfaces()
    test_i18n_labels()
    print(f"passed={PASSED} failed={FAILED}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
