# -*- coding: utf-8 -*-
"""BR-LOCAL-VERIFY-01 Phase 4A-1 — JP core / gate smoke on local MySQL.

The frozen user-facing contract is 122 cases. This step runs the runner
foundation, the 20 JP core, Pro, embedded, and gate cases, plus JP Settings
and JP Public startup cases. EN and ZH-TW stay out of this step.

A fresh browser that opens setting/profile.html lands on profile_edit.html
when kpi-profile-last is absent. That is existing product behavior. The ready
fixture must still show its canonical business name. The profile-required
fixture must stay empty.

After each fixture group the runner compares MySQL with the manifest. A
changed fixture is reseeded from that same manifest before the next group.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import socket
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

from kpn_local_php import php_bin, php_command

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "fixtures" / "local" / "canonical" / "manifest.json"
MYSQL_SEED = ROOT / "scripts" / "kpn_local_mysql_seed.php"
OUT = ROOT / "tests" / "results" / "local-full-page-smoke.json"
READY_MS = 20000

# Contract cases fill the frozen 122. coverage=supplemental repeats a route and does not take a slot.
CONTRACT_TARGET = 122
CASES = [
    {"id": "core-home-jp", "fixture": "fx-basic-restaurant-ready", "path": "/app/home/index.html", "kind": "app", "expect": "normal Basic Home"},
    {"id": "core-annual-jp", "fixture": "fx-basic-restaurant-ready", "path": "/app/annual/index.html", "kind": "app", "expect": "normal Basic Annual"},
    {"id": "core-monthly-jp", "fixture": "fx-basic-restaurant-ready", "path": "/app/monthly/index.html", "kind": "app", "expect": "normal Basic Monthly"},
    {"id": "core-profit-jp", "fixture": "fx-basic-restaurant-ready", "path": "/app/profit/index.html", "kind": "profit", "expect": "Profit hub stays open for Basic"},
    {"id": "core-profile-jp", "fixture": "fx-basic-restaurant-ready", "path": "/setting/profile.html", "kind": "profile", "coverage": "supplemental", "expect": "Ready profile opens the edit form with the canonical business name"},
    {"id": "core-pl-jp", "fixture": "fx-pro-hotel-ready", "path": "/app/profit/pl/index.html", "kind": "app", "expect": "Pro Hotel PL stays open"},
    {"id": "core-mep-jp", "fixture": "fx-pro-hotel-ready", "path": "/app/monthly/edit/index.html", "kind": "app", "expect": "Pro Hotel MEP stays open"},
    {"id": "core-booking-jp", "fixture": "fx-pro-hotel-ready", "path": "/app/booking/index.html", "kind": "booking", "expect": "Booking shows the intentional COMING SOON state"},
    {"id": "surf-daily-monthly", "fixture": "fx-basic-restaurant-ready", "path": "/app/monthly/index.html?open=daily", "kind": "daily", "expect": "Monthly Daily surface opens"},
    {"id": "surf-daily-annual", "fixture": "fx-basic-restaurant-ready", "path": "/app/annual/index.html", "kind": "daily-annual", "expect": "Annual Daily surface opens from its own host"},
    {"id": "surf-insight", "fixture": "fx-pro-hotel-ready", "path": "/app/monthly/index.html?open=insight", "kind": "insight", "expect": "Insight surface opens for Pro"},
    {"id": "surf-setup-annual", "fixture": "fx-basic-setup-required", "path": "/app/annual/index.html", "kind": "setup", "expect": "Annual keeps setup-required and is not complete"},
    {"id": "surf-setup-monthly", "fixture": "fx-basic-setup-required", "path": "/app/monthly/index.html", "kind": "setup", "expect": "Monthly keeps setup-required and is not complete"},
    {"id": "gate-profile-annual", "fixture": "fx-basic-profile-required", "path": "/app/annual/index.html", "kind": "profile-gate", "expect": "Annual hard gate is active and the account is not ready"},
    {"id": "gate-profile-route", "fixture": "fx-basic-profile-required", "path": "/setting/profile.html", "kind": "profile-fallback", "expect": "Incomplete profile falls through to profile edit"},
    {"id": "gate-pl", "fixture": "fx-basic-restaurant-ready", "path": "/app/profit/pl/index.html", "kind": "pro-gate", "expect": "Basic PL lands on Change Plan"},
    {"id": "gate-mep", "fixture": "fx-basic-restaurant-ready", "path": "/app/monthly/edit/index.html", "kind": "pro-gate", "expect": "Basic MEP lands on Change Plan"},
    {"id": "gate-booking", "fixture": "fx-basic-restaurant-ready", "path": "/app/booking/index.html", "kind": "pro-gate", "expect": "Basic Booking lands on Change Plan"},
    {"id": "gate-insight", "fixture": "fx-basic-restaurant-ready", "path": "/app/monthly/index.html", "kind": "insight-gate", "expect": "Basic Insight action lands on Change Plan"},
    {"id": "biz-pro-rest", "fixture": "fx-pro-restaurant-ready", "path": "/app/monthly/index.html", "kind": "restaurant", "expect": "Pro Restaurant Monthly keeps food sales that Hotel does not have"},
    {"id": "set-jp-index", "fixture": "fx-basic-restaurant-ready", "path": "/setting/index.html", "kind": "profile", "expect": "Settings index replaces to profile edit and the ready name hydrates"},
    {"id": "set-jp-profile", "fixture": "fx-basic-restaurant-ready", "path": "/setting/profile.html", "kind": "profile", "expect": "Ready profile opens the edit form with the canonical business name"},
    {"id": "set-jp-profile-edit", "fixture": "fx-basic-restaurant-ready", "path": "/setting/profile_edit.html", "kind": "profile", "expect": "Profile edit shows the canonical business name"},
    {"id": "set-jp-preferences", "fixture": "fx-basic-restaurant-ready", "path": "/setting/preferences.html", "kind": "settings", "finalPath": "/setting/preferences.html", "selector": "#preferences-form", "expect": "Preferences form stays on Basic"},
    {"id": "set-jp-change-email", "fixture": "fx-basic-restaurant-ready", "path": "/setting/change_email.html", "kind": "settings", "finalPath": "/setting/change_email.html", "selector": "h2.profile-title-sub", "expect": "Change Email confirmation boots without sending mail"},
    {"id": "set-jp-change-email-edit", "fixture": "fx-basic-restaurant-ready", "path": "/setting/change_email_edit.html", "kind": "settings", "finalPath": "/setting/change_email_edit.html", "selector": "#change-email-form", "expect": "Change Email edit form boots without sending mail"},
    {"id": "set-jp-change-password", "fixture": "fx-basic-restaurant-ready", "path": "/setting/change_password.html", "kind": "settings", "finalPath": "/setting/change_password.html", "selector": "#current-password", "expect": "Change Password form boots without changing the password"},
    {"id": "set-jp-change-password-success", "fixture": "fx-basic-restaurant-ready", "path": "/setting/change_password_success.html", "kind": "settings", "finalPath": "/setting/change_password_success.html", "selector": "h2.profile-title-sub", "expect": "Password completion screen boots without a password change"},
    {"id": "set-jp-change-plan", "fixture": "fx-basic-restaurant-ready", "path": "/setting/change_plan.html", "kind": "settings", "finalPath": "/setting/change_plan.html", "selector": "#change-plan-h1", "expect": "Change Plan stays on Basic"},
    {"id": "set-jp-plan-details", "fixture": "fx-basic-restaurant-ready", "path": "/setting/plan_details.html", "kind": "settings", "finalPath": "/setting/plan_details.html", "selector": "#plan-details-h1", "expect": "Plan details stays a static Basic page"},
    {"id": "set-jp-session", "fixture": "fx-basic-restaurant-ready", "path": "/setting/session_management.html", "kind": "settings", "finalPath": "/setting/session_management.html", "selector": "#coming-soon-text", "text": "Coming soon", "expect": "Session Management shows the intentional construction state"},
    {"id": "set-jp-feedback", "fixture": "fx-basic-restaurant-ready", "path": "/setting/feedback.html", "kind": "settings", "finalPath": "/setting/feedback.html", "selector": "#feedback-message", "expect": "Feedback form boots without sending mail"},
    {"id": "set-jp-delete-1", "fixture": "fx-basic-restaurant-ready", "path": "/setting/delete_account1.html", "kind": "settings", "finalPath": "/setting/delete_account1.html", "selector": "#delete-step1-heading", "expect": "Delete step 1 boots without deleting the account"},
    {"id": "set-jp-delete-2", "fixture": "fx-basic-restaurant-ready", "path": "/setting/delete_account2.html", "kind": "settings", "finalPath": "/setting/delete_account1.html", "selector": "#delete-step1-heading", "expect": "Delete step 2 replaces to delete step 1"},
    {"id": "set-jp-delete-3", "fixture": "fx-basic-restaurant-ready", "path": "/setting/delete_account3.html", "kind": "settings", "finalPath": "/setting/delete_account3.html", "selector": "h3.delete-account-step-heading", "expect": "Delete step 2 screen boots without deleting the account"},
    {"id": "set-jp-delete-4-1", "fixture": "fx-basic-restaurant-ready", "path": "/setting/delete_account4-1.html", "kind": "settings", "finalPath": "/setting/delete_account4-1.html", "selector": "h3.delete-account-step-heading", "expect": "Delete step 3 screen boots without deleting the account"},
    {"id": "set-jp-delete-4-2", "fixture": "fx-basic-restaurant-ready", "path": "/setting/delete_account4-2.html", "kind": "settings", "finalPath": "/setting/delete_account1.html", "selector": "#delete-step1-heading", "expect": "Delete step 4-2 replaces to delete step 1"},
    {"id": "set-jp-delete-5", "fixture": "fx-basic-restaurant-ready", "path": "/setting/delete_account5.html", "kind": "settings", "finalPath": "/setting/delete_account5.html", "selector": "h2.delete-account-page-title", "expect": "Delete final confirmation boots without deleting the account"},
    {"id": "set-jp-delete-done", "fixture": "fx-basic-restaurant-ready", "path": "/setting/delete_account_accomplished.html", "kind": "settings", "finalPath": "/index.html", "selector": "#lp-brand", "expect": "Delete completion without the in-tab success flag returns to the JP top page and keeps Basic"},
    {"id": "pub-jp-top", "fixture": "public", "path": "/index.html", "kind": "public", "finalPath": "/index.html", "selector": "#lp-brand", "expect": "JP top page loads signed out"},
    {"id": "pub-jp-login", "fixture": "public", "path": "/login/index.html", "kind": "public", "finalPath": "/login/index.html", "selector": "#btn-login", "expect": "JP login loads signed out"},
    {"id": "pub-jp-register", "fixture": "public", "path": "/register/registration_si-fi_jp/registration_si-fi_jp.html", "kind": "public", "finalPath": "/register/registration_si-fi_jp/registration_si-fi_jp.html", "selector": "#plan-title", "expect": "JP registration loads without submitting"},
    {"id": "pub-jp-forgot", "fixture": "public", "path": "/forgot-password/index.html", "kind": "public", "finalPath": "/forgot-password/index.html", "selector": "#forgot-form", "expect": "Forgot password loads without sending mail"},
    {"id": "pub-jp-reset", "fixture": "public", "path": "/reset-password/index.html", "kind": "public", "finalPath": "/reset-password/index.html", "selector": "#reset-form", "expect": "Reset password loads without changing a password"},
    {"id": "pub-jp-plan", "fixture": "public", "path": "/plan/index.html", "kind": "public", "finalPath": "/plan/index.html", "selector": "#plan-basic-cta", "expect": "JP plan page loads as the current static page"},
    {"id": "pub-jp-terms", "fixture": "public", "path": "/legal/terms/index.html", "kind": "public", "finalPath": "/legal/terms/index.html", "selector": "h1.terms-title", "expect": "JP terms load"},
    {"id": "pub-jp-privacy", "fixture": "public", "path": "/legal/privacy/index.html", "kind": "public", "finalPath": "/legal/privacy/index.html", "selector": "h1.terms-title", "expect": "JP privacy policy loads"},
    {"id": "pub-jp-unsubscribe", "fixture": "public", "path": "/unsubscribe/index.html", "kind": "public", "finalPath": "/unsubscribe/index.html", "selector": "#unsubscribe-form", "expect": "Unsubscribe loads without submitting"},
    {"id": "pub-jp-account-protection", "fixture": "public", "path": "/account_protection/account_protection.html", "kind": "public", "finalPath": "/account_protection/account_protection.html", "selector": ".defense-text", "expect": "Account protection shows the reserved-page wording"},
    {"id": "pub-jp-defensive-protocol", "fixture": "public", "path": "/account_protection/defensive_protocol.html", "kind": "public", "finalPath": "/account_protection/defensive_protocol.html", "selector": "#defense-title", "expect": "Defensive protocol boots without sending mail"},
]


def locale_cases(group: str, prefix: str, lang: str, rows: list[dict]) -> list[dict]:
    out = []
    for row in rows:
        item = dict(row)
        item["group"] = group
        item["prefix"] = prefix
        item["lang"] = lang
        out.append(item)
    return out


EN_ROWS = [
    {"id": "core-home-en", "fixture": "fx-basic-restaurant-ready", "path": "/en/app/home/index.html", "kind": "app", "expect": "EN Basic Home boots in English"},
    {"id": "core-annual-en", "fixture": "fx-basic-restaurant-ready", "path": "/en/app/annual/index.html", "kind": "app", "expect": "EN Basic Annual boots in English"},
    {"id": "core-monthly-en", "fixture": "fx-basic-restaurant-ready", "path": "/en/app/monthly/index.html", "kind": "app", "expect": "EN Basic Monthly boots in English"},
    {"id": "core-profit-en", "fixture": "fx-basic-restaurant-ready", "path": "/en/app/profit/index.html", "kind": "profit", "expect": "EN Profit hub boots for Basic in English"},
    {"id": "core-pl-en", "fixture": "fx-pro-hotel-ready", "path": "/en/app/profit/pl/index.html", "kind": "app", "expect": "EN Pro Hotel PL boots in English"},
    {"id": "core-mep-en", "fixture": "fx-pro-hotel-ready", "path": "/en/app/monthly/edit/index.html", "kind": "app", "expect": "EN Pro Hotel MEP boots in English"},
    {"id": "core-booking-en", "fixture": "fx-pro-hotel-ready", "path": "/en/app/booking/index.html", "kind": "booking", "expect": "EN Booking shows Coming Soon in English"},
    {"id": "set-en-index", "fixture": "fx-basic-restaurant-ready", "path": "/en/setting/index.html", "kind": "profile", "expect": "EN settings index reaches profile edit in English and hydrates the ready name"},
    {"id": "set-en-profile", "fixture": "fx-basic-restaurant-ready", "path": "/en/setting/profile.html", "kind": "profile", "expect": "EN profile reaches profile edit in English and hydrates the ready name"},
    {"id": "set-en-profile-edit", "fixture": "fx-basic-restaurant-ready", "path": "/en/setting/profile_edit.html", "kind": "profile", "expect": "EN profile edit shows the canonical name in English"},
    {"id": "set-en-preferences", "fixture": "fx-basic-restaurant-ready", "path": "/en/setting/preferences.html", "kind": "settings", "finalPath": "/en/setting/preferences.html", "selector": "#preferences-form", "expect": "EN preferences stay in English on Basic"},
    {"id": "set-en-change-email", "fixture": "fx-basic-restaurant-ready", "path": "/en/setting/change_email.html", "kind": "settings", "finalPath": "/en/setting/change_email.html", "selector": "h2.profile-title-sub", "expect": "EN change email boots in English without sending mail"},
    {"id": "set-en-change-email-edit", "fixture": "fx-basic-restaurant-ready", "path": "/en/setting/change_email_edit.html", "kind": "settings", "finalPath": "/en/setting/change_email_edit.html", "selector": "#change-email-form", "expect": "EN change email edit boots in English without sending mail"},
    {"id": "set-en-change-password", "fixture": "fx-basic-restaurant-ready", "path": "/en/setting/change_password.html", "kind": "settings", "finalPath": "/en/setting/change_password.html", "selector": "#current-password", "expect": "EN change password boots in English without changing the password"},
    {"id": "set-en-change-password-success", "fixture": "fx-basic-restaurant-ready", "path": "/en/setting/change_password_success.html", "kind": "settings", "finalPath": "/en/setting/change_password_success.html", "selector": "h2.profile-title-sub", "expect": "EN password completion boots in English"},
    {"id": "set-en-change-plan", "fixture": "fx-basic-restaurant-ready", "path": "/en/setting/change_plan.html", "kind": "settings", "finalPath": "/en/setting/change_plan.html", "selector": "#change-plan-h1", "expect": "EN change plan stays Basic and English"},
    {"id": "set-en-plan-details", "fixture": "fx-basic-restaurant-ready", "path": "/en/setting/plan_details.html", "kind": "settings", "finalPath": "/en/setting/plan_details.html", "selector": "#plan-details-h1", "expect": "EN plan details stay static and English"},
    {"id": "set-en-session", "fixture": "fx-basic-restaurant-ready", "path": "/en/setting/session_management.html", "kind": "settings", "finalPath": "/en/setting/session_management.html", "selector": "#coming-soon-text", "text": "Coming soon", "expect": "EN session management shows Coming soon"},
    {"id": "set-en-feedback", "fixture": "fx-basic-restaurant-ready", "path": "/en/setting/feedback.html", "kind": "settings", "finalPath": "/en/setting/feedback.html", "selector": "#feedback-message", "expect": "EN feedback boots in English without sending mail"},
    {"id": "set-en-delete-1", "fixture": "fx-basic-restaurant-ready", "path": "/en/setting/delete_account1.html", "kind": "settings", "finalPath": "/en/setting/delete_account1.html", "selector": "#delete-step1-heading", "expect": "EN delete step 1 boots in English"},
    {"id": "set-en-delete-2", "fixture": "fx-basic-restaurant-ready", "path": "/en/setting/delete_account2.html", "kind": "settings", "finalPath": "/en/setting/delete_account1.html", "selector": "#delete-step1-heading", "expect": "EN delete step 2 replaces to EN delete step 1"},
    {"id": "set-en-delete-3", "fixture": "fx-basic-restaurant-ready", "path": "/en/setting/delete_account3.html", "kind": "settings", "finalPath": "/en/setting/delete_account3.html", "selector": "h3.delete-account-step-heading", "expect": "EN delete step 2 screen boots in English"},
    {"id": "set-en-delete-4-1", "fixture": "fx-basic-restaurant-ready", "path": "/en/setting/delete_account4-1.html", "kind": "settings", "finalPath": "/en/setting/delete_account4-1.html", "selector": "h3.delete-account-step-heading", "expect": "EN delete step 3 screen boots in English"},
    {"id": "set-en-delete-4-2", "fixture": "fx-basic-restaurant-ready", "path": "/en/setting/delete_account4-2.html", "kind": "settings", "finalPath": "/en/setting/delete_account1.html", "selector": "#delete-step1-heading", "expect": "EN delete step 4-2 replaces to EN delete step 1"},
    {"id": "set-en-delete-5", "fixture": "fx-basic-restaurant-ready", "path": "/en/setting/delete_account5.html", "kind": "settings", "finalPath": "/en/setting/delete_account5.html", "selector": "h2.delete-account-page-title", "expect": "EN delete final confirmation boots in English"},
    {"id": "set-en-delete-done", "fixture": "fx-basic-restaurant-ready", "path": "/en/setting/delete_account_accomplished.html", "kind": "settings", "finalPath": "/en/index.html", "selector": "#lp-brand", "expect": "EN delete completion without the success flag returns to the EN top and stays Basic"},
    {"id": "pub-en-top", "fixture": "public", "path": "/en/index.html", "kind": "public", "finalPath": "/en/index.html", "selector": "#lp-brand", "expect": "EN top loads signed out in English"},
    {"id": "pub-en-login", "fixture": "public", "path": "/en/login/index.html", "kind": "public", "finalPath": "/en/login/index.html", "selector": "#btn-login", "expect": "EN login loads signed out in English"},
    {"id": "pub-en-register", "fixture": "public", "path": "/en/register/registration_si-fi_en.html", "kind": "public", "finalPath": "/en/register/registration_si-fi_en.html", "selector": "#plan-title", "expect": "EN registration loads in English without submitting"},
    {"id": "pub-en-forgot", "fixture": "public", "path": "/en/forgot-password/index.html", "kind": "public", "finalPath": "/en/forgot-password/index.html", "selector": "#forgot-form", "expect": "EN forgot password loads in English without sending mail"},
    {"id": "pub-en-reset", "fixture": "public", "path": "/en/reset-password/index.html", "kind": "public", "finalPath": "/en/reset-password/index.html", "selector": "#reset-form", "expect": "EN reset password loads in English without changing a password"},
    {"id": "pub-en-plan", "fixture": "public", "path": "/en/plan/index.html", "kind": "public", "finalPath": "/en/plan/index.html", "selector": "#plan-basic-cta", "expect": "EN plan page loads in English"},
    {"id": "pub-en-terms", "fixture": "public", "path": "/en/legal/terms/index.html", "kind": "public", "finalPath": "/en/legal/terms/index.html", "selector": "h1.terms-title", "expect": "EN terms load in English"},
    {"id": "pub-en-privacy", "fixture": "public", "path": "/en/legal/privacy/index.html", "kind": "public", "finalPath": "/en/legal/privacy/index.html", "selector": "h1.terms-title", "expect": "EN privacy policy loads in English"},
    {"id": "pub-en-unsubscribe", "fixture": "public", "path": "/en/unsubscribe/index.html", "kind": "public", "finalPath": "/en/unsubscribe/index.html", "selector": "#unsubscribe-form", "expect": "EN unsubscribe loads in English without submitting"},
    {"id": "pub-en-account-protection", "fixture": "public", "path": "/en/account_protection/account_protection.html", "kind": "public", "finalPath": "/en/account_protection/account_protection.html", "selector": ".defense-text", "expect": "EN account protection shows the reserved-page wording"},
    {"id": "pub-en-defensive-protocol", "fixture": "public", "path": "/en/account_protection/defensive_protocol.html", "kind": "public", "finalPath": "/en/account_protection/defensive_protocol.html", "selector": "#defense-title", "expect": "EN defensive protocol boots in English without sending mail"},
]
ZH_ROWS = [
    {"id": "core-home-zh-tw", "fixture": "fx-basic-restaurant-ready", "path": "/zh-tw/app/home/index.html", "kind": "app", "expect": "ZH-TW Basic Home boots in Traditional Chinese"},
    {"id": "core-annual-zh-tw", "fixture": "fx-basic-restaurant-ready", "path": "/zh-tw/app/annual/index.html", "kind": "app", "expect": "ZH-TW Basic Annual boots in Traditional Chinese"},
    {"id": "core-monthly-zh-tw", "fixture": "fx-basic-restaurant-ready", "path": "/zh-tw/app/monthly/index.html", "kind": "app", "expect": "ZH-TW Basic Monthly boots in Traditional Chinese"},
    {"id": "core-profit-zh-tw", "fixture": "fx-basic-restaurant-ready", "path": "/zh-tw/app/profit/index.html", "kind": "profit", "expect": "ZH-TW Profit hub boots for Basic in Traditional Chinese"},
    {"id": "core-pl-zh-tw", "fixture": "fx-pro-hotel-ready", "path": "/zh-tw/app/profit/pl/index.html", "kind": "app", "expect": "ZH-TW Pro Hotel PL boots in Traditional Chinese"},
    {"id": "core-mep-zh-tw", "fixture": "fx-pro-hotel-ready", "path": "/zh-tw/app/monthly/edit/index.html", "kind": "app", "expect": "ZH-TW Pro Hotel MEP boots in Traditional Chinese"},
    {"id": "core-booking-zh-tw", "fixture": "fx-pro-hotel-ready", "path": "/zh-tw/app/booking/index.html", "kind": "booking", "expect": "ZH-TW Booking shows Coming Soon in Traditional Chinese"},
    {"id": "set-zh-tw-index", "fixture": "fx-basic-restaurant-ready", "path": "/zh-tw/setting/index.html", "kind": "profile", "expect": "ZH-TW settings index reaches profile edit in Traditional Chinese and hydrates the ready name"},
    {"id": "set-zh-tw-profile", "fixture": "fx-basic-restaurant-ready", "path": "/zh-tw/setting/profile.html", "kind": "profile", "expect": "ZH-TW profile reaches profile edit in Traditional Chinese and hydrates the ready name"},
    {"id": "set-zh-tw-profile-edit", "fixture": "fx-basic-restaurant-ready", "path": "/zh-tw/setting/profile_edit.html", "kind": "profile", "expect": "ZH-TW profile edit shows the canonical name in Traditional Chinese"},
    {"id": "set-zh-tw-preferences", "fixture": "fx-basic-restaurant-ready", "path": "/zh-tw/setting/preferences.html", "kind": "settings", "finalPath": "/zh-tw/setting/preferences.html", "selector": "#preferences-form", "expect": "ZH-TW preferences stay in Traditional Chinese on Basic"},
    {"id": "set-zh-tw-change-email", "fixture": "fx-basic-restaurant-ready", "path": "/zh-tw/setting/change_email.html", "kind": "settings", "finalPath": "/zh-tw/setting/change_email.html", "selector": "h2.profile-title-sub", "expect": "ZH-TW change email boots in Traditional Chinese without sending mail"},
    {"id": "set-zh-tw-change-email-edit", "fixture": "fx-basic-restaurant-ready", "path": "/zh-tw/setting/change_email_edit.html", "kind": "settings", "finalPath": "/zh-tw/setting/change_email_edit.html", "selector": "#change-email-form", "expect": "ZH-TW change email edit boots in Traditional Chinese without sending mail"},
    {"id": "set-zh-tw-change-password", "fixture": "fx-basic-restaurant-ready", "path": "/zh-tw/setting/change_password.html", "kind": "settings", "finalPath": "/zh-tw/setting/change_password.html", "selector": "#current-password", "expect": "ZH-TW change password boots in Traditional Chinese without changing the password"},
    {"id": "set-zh-tw-change-password-success", "fixture": "fx-basic-restaurant-ready", "path": "/zh-tw/setting/change_password_success.html", "kind": "settings", "finalPath": "/zh-tw/setting/change_password_success.html", "selector": "h2.profile-title-sub", "expect": "ZH-TW password completion boots in Traditional Chinese"},
    {"id": "set-zh-tw-change-plan", "fixture": "fx-basic-restaurant-ready", "path": "/zh-tw/setting/change_plan.html", "kind": "settings", "finalPath": "/zh-tw/setting/change_plan.html", "selector": "#change-plan-h1", "expect": "ZH-TW change plan stays Basic and Traditional Chinese"},
    {"id": "set-zh-tw-plan-details", "fixture": "fx-basic-restaurant-ready", "path": "/zh-tw/setting/plan_details.html", "kind": "settings", "finalPath": "/zh-tw/setting/plan_details.html", "selector": "#plan-details-h1", "expect": "ZH-TW plan details stay static and Traditional Chinese"},
    {"id": "set-zh-tw-session", "fixture": "fx-basic-restaurant-ready", "path": "/zh-tw/setting/session_management.html", "kind": "settings", "finalPath": "/zh-tw/setting/session_management.html", "selector": "#coming-soon-text", "text": "即將推出", "expect": "ZH-TW session management shows the construction state"},
    {"id": "set-zh-tw-feedback", "fixture": "fx-basic-restaurant-ready", "path": "/zh-tw/setting/feedback.html", "kind": "settings", "finalPath": "/zh-tw/setting/feedback.html", "selector": "#feedback-message", "expect": "ZH-TW feedback boots in Traditional Chinese without sending mail"},
    {"id": "set-zh-tw-delete-1", "fixture": "fx-basic-restaurant-ready", "path": "/zh-tw/setting/delete_account1.html", "kind": "settings", "finalPath": "/zh-tw/setting/delete_account1.html", "selector": "#delete-step1-heading", "expect": "ZH-TW delete step 1 boots in Traditional Chinese"},
    {"id": "set-zh-tw-delete-2", "fixture": "fx-basic-restaurant-ready", "path": "/zh-tw/setting/delete_account2.html", "kind": "settings", "finalPath": "/zh-tw/setting/delete_account1.html", "selector": "#delete-step1-heading", "expect": "ZH-TW delete step 2 replaces to ZH-TW delete step 1"},
    {"id": "set-zh-tw-delete-3", "fixture": "fx-basic-restaurant-ready", "path": "/zh-tw/setting/delete_account3.html", "kind": "settings", "finalPath": "/zh-tw/setting/delete_account3.html", "selector": "h3.delete-account-step-heading", "expect": "ZH-TW delete step 2 screen boots in Traditional Chinese"},
    {"id": "set-zh-tw-delete-4-1", "fixture": "fx-basic-restaurant-ready", "path": "/zh-tw/setting/delete_account4-1.html", "kind": "settings", "finalPath": "/zh-tw/setting/delete_account4-1.html", "selector": "h3.delete-account-step-heading", "expect": "ZH-TW delete step 3 screen boots in Traditional Chinese"},
    {"id": "set-zh-tw-delete-4-2", "fixture": "fx-basic-restaurant-ready", "path": "/zh-tw/setting/delete_account4-2.html", "kind": "settings", "finalPath": "/zh-tw/setting/delete_account1.html", "selector": "#delete-step1-heading", "expect": "ZH-TW delete step 4-2 replaces to ZH-TW delete step 1"},
    {"id": "set-zh-tw-delete-5", "fixture": "fx-basic-restaurant-ready", "path": "/zh-tw/setting/delete_account5.html", "kind": "settings", "finalPath": "/zh-tw/setting/delete_account5.html", "selector": "h2.delete-account-page-title", "expect": "ZH-TW delete final confirmation boots in Traditional Chinese"},
    {"id": "set-zh-tw-delete-done", "fixture": "fx-basic-restaurant-ready", "path": "/zh-tw/setting/delete_account_accomplished.html", "kind": "settings", "finalPath": "/zh-tw/login/index.html", "selector": "#btn-login", "expect": "ZH-TW delete completion without the success flag returns to the ZH-TW login and stays Basic"},
    {"id": "pub-zh-tw-login", "fixture": "public", "path": "/zh-tw/login/index.html", "kind": "public", "finalPath": "/zh-tw/login/index.html", "selector": "#btn-login", "expect": "ZH-TW login loads signed out in Traditional Chinese"},
    {"id": "pub-zh-tw-register", "fixture": "public", "path": "/zh-tw/register/registration_si-fi_zh-tw.html", "kind": "public", "finalPath": "/zh-tw/register/registration_si-fi_zh-tw.html", "selector": "#plan-title", "expect": "ZH-TW registration loads in Traditional Chinese without submitting"},
    {"id": "pub-zh-tw-forgot", "fixture": "public", "path": "/zh-tw/forgot-password/index.html", "kind": "public", "finalPath": "/zh-tw/forgot-password/index.html", "selector": "#forgot-form", "expect": "ZH-TW forgot password loads in Traditional Chinese without sending mail"},
    {"id": "pub-zh-tw-reset", "fixture": "public", "path": "/zh-tw/reset-password/index.html", "kind": "public", "finalPath": "/zh-tw/reset-password/index.html", "selector": "#reset-form", "expect": "ZH-TW reset password loads in Traditional Chinese without changing a password"},
    {"id": "pub-zh-tw-plan", "fixture": "public", "path": "/zh-tw/plan/index.html", "kind": "public", "finalPath": "/zh-tw/plan/index.html", "selector": "#plan-basic-cta", "expect": "ZH-TW plan page loads in Traditional Chinese"},
    {"id": "pub-zh-tw-terms", "fixture": "public", "path": "/zh-tw/legal/terms/index.html", "kind": "public", "finalPath": "/zh-tw/legal/terms/index.html", "selector": "h1.terms-title", "expect": "ZH-TW terms load in Traditional Chinese"},
    {"id": "pub-zh-tw-privacy", "fixture": "public", "path": "/zh-tw/legal/privacy/index.html", "kind": "public", "finalPath": "/zh-tw/legal/privacy/index.html", "selector": "h1.terms-title", "expect": "ZH-TW privacy policy loads in Traditional Chinese"},
    {"id": "pub-zh-tw-unsubscribe", "fixture": "public", "path": "/zh-tw/unsubscribe/index.html", "kind": "public", "finalPath": "/zh-tw/unsubscribe/index.html", "selector": "#unsubscribe-form", "expect": "ZH-TW unsubscribe loads in Traditional Chinese without submitting"},
    {"id": "pub-zh-tw-account-protection", "fixture": "public", "path": "/zh-tw/account_protection/account_protection.html", "kind": "public", "finalPath": "/zh-tw/account_protection/account_protection.html", "selector": ".defense-text", "expect": "ZH-TW account protection shows the reserved-page wording"},
    {"id": "pub-zh-tw-defensive-protocol", "fixture": "public", "path": "/zh-tw/account_protection/defensive_protocol.html", "kind": "public", "finalPath": "/zh-tw/account_protection/defensive_protocol.html", "selector": "#defense-title", "expect": "ZH-TW defensive protocol boots in Traditional Chinese without sending mail"},
]
CASES.extend(locale_cases("en", "/en/", "en", EN_ROWS))
CASES.extend(locale_cases("zh-tw", "/zh-tw/", "zh-TW", ZH_ROWS))


def runtime_identity_path() -> Path:
    override = os.environ.get("KPN_LOCAL_MYSQL_RUNTIME_CONFIG", "")
    if override:
        return Path(override)
    return Path(os.environ.get("LOCALAPPDATA", "")) / "kpn-tools" / "kpn-local-mysql-runtime.php"


def read_runtime_identity() -> tuple[str, str]:
    text = runtime_identity_path().read_text(encoding="utf-8")
    user = re.search(r"'dbUser'\s*=>\s*'([A-Za-z0-9_]+)'", text)
    password = re.search(r"'dbPass'\s*=>\s*'([A-Za-z0-9]+)'", text)
    if not user or not password or user.group(1) != "kpn_local_runtime":
        raise SystemExit("runtime identity is not kpn_local_runtime")
    return user.group(1), password.group(1)


def write_config(path: Path, root: Path, **overrides) -> None:
    data = {
        "localTestMode": True,
        "localDataRoot": root.as_posix(),
        "storageDriver": "mysql",
        "dbHost": "127.0.0.1",
        "dbPort": 3306,
        "dbName": "kpn_local_test",
        "dbUser": "kpn_local_runtime",
        "dbPass": "",
        "dbCharset": "utf8mb4",
        "registrationEnabled": False,
        "allowSelfPlanChange": False,
        "passwordResetBaseUrl": "http://127.0.0.1:9",
        "supportEmail": "local-sink@localhost.test",
        "supportFrom": "local-sink@localhost.test",
        "token": "local-test-token",
        "planAdminToken": "local-test-plan-token",
    }
    data.update(overrides)
    lines = ["<?php", "return ["]
    for key, value in data.items():
        if isinstance(value, bool):
            rendered = "true" if value else "false"
        elif isinstance(value, int):
            rendered = str(value)
        else:
            rendered = "'" + str(value).replace("\\", "\\\\").replace("'", "\\'") + "'"
        lines.append(f"    '{key}' => {rendered},")
    lines.append("];")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_php(php: list[str], args: list[str], config: Path) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["KPI_V1_CONFIG"] = str(config)
    return subprocess.run(php + args, cwd=str(ROOT), env=env, capture_output=True, text=True, timeout=90)


def free_port() -> int:
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return int(port)


def wait_http(port: int) -> None:
    url = f"http://127.0.0.1:{port}/api/v1/auth/registration-status.php"
    last = ""
    for _ in range(40):
        try:
            with urllib.request.urlopen(url, timeout=2) as res:
                if res.status == 200:
                    return
        except Exception as exc:
            last = str(exc)
        time.sleep(0.25)
    raise SystemExit(f"php server did not answer: {last}")


PROFILE_COLUMNS = {
    "businessName": "business_name",
    "companyName": "company_name",
    "businessType": "business_type",
    "genre": "genre",
    "locale": "locale",
    "country": "country",
    "stateRegion": "state_region",
    "city": "city",
    "currency": "currency",
}


def norm(value):
    if isinstance(value, dict):
        return {str(key): norm(item) for key, item in value.items()}
    if isinstance(value, list):
        return [norm(item) for item in value]
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


def parse_json(raw):
    if raw in (None, ""):
        return None
    return norm(json.loads(raw))


def expected_inputs(account: dict) -> list:
    store = (account.get("blob") or {}).get("store") or {}
    timeline = store.get("timeline") or {}
    sales = timeline.get("dailySales") or {}
    days = timeline.get("businessDays") or {}
    rows = []
    for iso in sorted(set(sales) | set(days)):
        amount = int(sales[iso]) if iso in sales else 0
        flag = bool(days[iso]) if iso in days else None
        rows.append([iso, amount, flag])
    return rows


def actual_inputs(dump: dict, user_id: str) -> list:
    rows = []
    for row in dump.get("inputs") or []:
        if row["user_id"] != user_id:
            continue
        raw = row["business_day"]
        flag = None if raw is None else bool(int(raw))
        rows.append([row["iso"], int(float(row["sales"])), flag])
    rows.sort(key=lambda item: item[0])
    return rows


def profile_expected(account: dict):
    profile = account.get("profile") or {}
    if not any(profile.get(key) not in (None, "") for key in PROFILE_COLUMNS):
        return None
    return {key: profile.get(key) or None for key in PROFILE_COLUMNS}


def profile_actual(dump: dict, user_id: str):
    row = next((item for item in dump.get("profiles") or [] if item["user_id"] == user_id), None)
    if row is None:
        return None
    return {key: row.get(column) or None for key, column in PROFILE_COLUMNS.items()}


def changed_paths(expected, observed, prefix=""):
    paths = []
    if type(expected) != type(observed) and not (expected is None or observed is None):
        if not isinstance(expected, (dict, list)) or not isinstance(observed, (dict, list)):
            return [prefix or "$"]
    if isinstance(expected, dict) or isinstance(observed, dict):
        left = expected if isinstance(expected, dict) else {}
        right = observed if isinstance(observed, dict) else {}
        for key in sorted(set(left) | set(right)):
            child = f"{prefix}.{key}" if prefix else str(key)
            if key not in left or key not in right or left.get(key) != right.get(key):
                if isinstance(left.get(key), dict) and isinstance(right.get(key), dict):
                    paths.extend(changed_paths(left.get(key), right.get(key), child))
                else:
                    paths.append(child)
        return paths
    if expected != observed:
        paths.append(prefix or "$")
    return paths


def fixture_delta(account: dict, dump: dict) -> dict:
    user_id = account["userId"]
    user = next(item for item in dump["users"] if item["user_id"] == user_id)
    store = next(item for item in dump["stores"] if item["user_id"] == user_id)
    blob = account["blob"]
    changed = {}
    if user.get("plan") != account.get("plan"):
        changed["user"] = {"canonical": account.get("plan"), "observed": user.get("plan")}
    canonical_revision = int(blob.get("revision") or 1)
    observed_revision = int(store.get("revision"))
    if observed_revision != canonical_revision:
        changed["revision"] = {"canonical": canonical_revision, "observed": observed_revision}
    store_paths = []
    for label, raw, expected in (
        ("store", store.get("store_json"), blob.get("store")),
        ("annualNav", store.get("annual_nav_json"), blob.get("annualNav")),
        ("pl", store.get("pl_json"), blob.get("pl")),
    ):
        actual = parse_json(raw)
        wanted = norm(expected)
        if actual != wanted:
            store_paths.extend(f"{label}.{path}" for path in changed_paths(wanted, actual))
    if store_paths:
        changed["store"] = store_paths[:40]
    if profile_actual(dump, user_id) != profile_expected(account):
        changed["profile"] = True
    if actual_inputs(dump, user_id) != expected_inputs(account):
        changed["dailyInput"] = True
    return changed


def dump_db(php: list[str], cfg: Path) -> dict:
    result = run_php(php, [str(MYSQL_SEED), "dump"], cfg)
    if result.returncode != 0:
        raise SystemExit(f"dump failed: {result.stderr or result.stdout}")
    return json.loads(result.stdout)


def reseed_fixture(php: list[str], cfg: Path, fixture_id: str) -> None:
    result = run_php(php, [str(MYSQL_SEED), "seed", fixture_id], cfg)
    marker = f"seeded kpn_local_test 1 {fixture_id}"
    if result.returncode != 0 or marker not in (result.stdout or ""):
        raise SystemExit(f"fixture reseed failed: {result.stderr or result.stdout}")


APP_READY = """(spec) => {
  const tier = sessionStorage.getItem('kpiNavigator.subscriptionTier')
    || localStorage.getItem('kpiNavigator.subscriptionTier');
  const uid = localStorage.getItem('kpiNavigator.lastKpiUserId');
  let store = null;
  try { store = JSON.parse(localStorage.getItem('kpiNavigator.kpiYearStore') || 'null'); }
  catch (e) { store = null; }
  const meta = store && store.meta ? store.meta : {};
  const sales = store && store.timeline && store.timeline.dailySales ? store.timeline.dailySales : {};
  const setup = meta.setup || {};
  const amount = sales[spec.iso] == null ? null : Number(sales[spec.iso]);
  return uid === spec.userId
    && tier === spec.plan
    && meta.businessType === spec.businessType
    && !!setup.complete === !!spec.setupComplete
    && amount === spec.sales
    && location.pathname.indexOf(spec.path) >= 0
    && (!spec.prefix || location.pathname.indexOf(spec.prefix) === 0)
    && (!spec.lang || document.documentElement.lang === spec.lang);
}"""


def watch(page, bag: dict) -> None:
    def on_request(req) -> None:
        host = (urlparse(req.url).hostname or "").lower()
        path = (urlparse(req.url).path or "").lower()
        if req.url.lower().startswith("ftp:") or host.startswith("ftp."):
            bag["ftp"].append(req.url)
        if any(token in path for token in ("/api/v1/feedback", "/auth/request-email-change", "/auth/forgot", "mail")):
            if req.method != "GET":
                bag["mail"].append(req.method + " " + path)
        if host in ("127.0.0.1", "localhost", ""):
            return
        if "forge-laboratory.com" in host or "lolipop" in host:
            bag["production"].append(req.url)

    def on_error(err) -> None:
        bag["pageerrors"].append(str(err))

    page.on("request", on_request)
    page.on("pageerror", on_error)


def login(page, base: str, account: dict) -> None:
    page.goto(base + "/login/index.html", wait_until="domcontentloaded", timeout=60000)
    page.fill("#user-id", account["email"])
    page.fill("#password", account["password"])
    page.click("#btn-login")
    page.wait_for_function(
        """(userId) => localStorage.getItem('kpiNavigator.lastKpiUserId') === userId
          && location.pathname.indexOf('/app/') >= 0
          && document.readyState !== 'loading'""",
        arg=account["userId"],
        timeout=60000,
    )
    page.wait_for_load_state("load", timeout=60000)


def fatal_text(page) -> str:
    try:
        text = page.locator("body").inner_text(timeout=3000)
    except Exception:
        return ""
    if "Fatal error" in text or "Uncaught" in text:
        return text[:240]
    return ""


def open_case(page, base: str, case: dict, account: dict, bag: dict) -> dict:
    before = len(bag["pageerrors"])
    row = {
        "id": case["id"],
        "fixture": case["fixture"],
        "route": case["path"],
        "locale": case.get("lang") or "",
        "coverage": case.get("coverage") or "contract",
        "expected": case["expect"],
        "result": "FAIL",
        "detail": "",
        "finalUrl": "",
    }
    try:
        target = base + case["path"]
        try:
            page.goto(target, wait_until="domcontentloaded", timeout=90000)
        except Exception as exc:
            if "interrupted by another navigation" not in str(exc):
                raise
            page.goto(target, wait_until="domcontentloaded", timeout=90000)
        kind = case["kind"]
        if kind == "app":
            page.wait_for_function(
                APP_READY,
                arg={
                    "userId": account["userId"],
                    "plan": account["plan"],
                    "businessType": account["businessType"],
                    "setupComplete": True,
                    "iso": "2026-10-03",
                    "sales": account["blob"]["store"]["timeline"]["dailySales"]["2026-10-03"],
                    "path": case["path"].split("?")[0],
                    "prefix": case.get("prefix") or "",
                    "lang": case.get("lang") or "",
                },
                timeout=READY_MS,
            )
        elif kind == "profit":
            page.wait_for_function(
                """(spec) => {
                  const tier = sessionStorage.getItem('kpiNavigator.subscriptionTier')
                    || localStorage.getItem('kpiNavigator.subscriptionTier');
                  const uid = localStorage.getItem('kpiNavigator.lastKpiUserId');
                  return uid === spec.userId && tier === 'basic'
                    && !!document.querySelector('.profit-hub-title')
                    && location.pathname.indexOf('/app/profit/index.html') >= 0
                    && location.pathname.indexOf('/pl/') < 0
                    && (!spec.prefix || location.pathname.indexOf(spec.prefix) === 0)
                    && (!spec.lang || document.documentElement.lang === spec.lang);
                }""",
                arg={"userId": account["userId"], "prefix": case.get("prefix") or "", "lang": case.get("lang") or ""},
                timeout=READY_MS,
            )
        elif kind == "profile":
            page.wait_for_function(
                """async (spec) => {
                  if (spec.prefix && location.pathname.indexOf(spec.prefix) !== 0) return false;
                  if (spec.lang && document.documentElement.lang !== spec.lang) return false;
                  if (location.pathname.indexOf('/setting/profile_edit.html') < 0) return false;
                  const tier = sessionStorage.getItem('kpiNavigator.subscriptionTier')
                    || localStorage.getItem('kpiNavigator.subscriptionTier');
                  if (localStorage.getItem('kpiNavigator.lastKpiUserId') !== spec.userId || tier !== 'basic') return false;
                  const input = document.getElementById('profile-business-name');
                  const res = await fetch('/api/v1/profile.php', {credentials:'include'});
                  const body = await res.json();
                  const profile = body.profile || {};
                  return res.status === 200
                    && profile.businessName === spec.name
                    && profile.businessType === 'restaurant'
                    && !!input && input.value === spec.name;
                }""",
                arg={
                    "userId": account["userId"],
                    "name": account["profile"]["businessName"],
                    "prefix": case.get("prefix") or "",
                    "lang": case.get("lang") or "",
                },
                timeout=READY_MS,
            )
        elif kind == "booking":
            page.wait_for_function(
                """(spec) => {
                  const tier = sessionStorage.getItem('kpiNavigator.subscriptionTier')
                    || localStorage.getItem('kpiNavigator.subscriptionTier');
                  const el = document.getElementById('coming-soon-text');
                  return localStorage.getItem('kpiNavigator.lastKpiUserId') === spec.userId
                    && tier === 'pro'
                    && location.pathname.indexOf('/app/booking/') >= 0
                    && (!spec.prefix || location.pathname.indexOf(spec.prefix) === 0)
                    && (!spec.lang || document.documentElement.lang === spec.lang)
                    && !!el && /COMING SOON/i.test(el.textContent || '');
                }""",
                arg={"userId": account["userId"], "prefix": case.get("prefix") or "", "lang": case.get("lang") or ""},
                timeout=READY_MS,
            )
        elif kind == "daily":
            page.wait_for_function(
                """(spec) => {
                  const el = document.getElementById('daily-overlay');
                  const tier = sessionStorage.getItem('kpiNavigator.subscriptionTier')
                    || localStorage.getItem('kpiNavigator.subscriptionTier');
                  return localStorage.getItem('kpiNavigator.lastKpiUserId') === spec.userId
                    && tier === 'basic' && !!el && el.hidden === false
                    && location.pathname.indexOf('/app/monthly/') >= 0;
                }""",
                arg={"userId": account["userId"]},
                timeout=READY_MS,
            )
        elif kind == "daily-annual":
            page.wait_for_function(
                APP_READY,
                arg={
                    "userId": account["userId"],
                    "plan": "basic",
                    "businessType": "restaurant",
                    "setupComplete": True,
                    "iso": "2026-10-03",
                    "sales": 31000,
                    "path": "/app/annual/",
                },
                timeout=READY_MS,
            )
            page.click("#global-nav-daily-btn")
            page.wait_for_function(
                """() => {
                  const el = document.getElementById('daily-overlay');
                  return !!el && el.hidden === false && location.pathname.indexOf('/app/annual/') >= 0;
                }""",
                timeout=READY_MS,
            )
        elif kind == "insight":
            page.wait_for_function(
                """(spec) => {
                  const el = document.getElementById('insight-overlay');
                  const tier = sessionStorage.getItem('kpiNavigator.subscriptionTier')
                    || localStorage.getItem('kpiNavigator.subscriptionTier');
                  return localStorage.getItem('kpiNavigator.lastKpiUserId') === spec.userId
                    && tier === 'pro' && !!el && el.hidden === false
                    && location.pathname.indexOf('/app/monthly/') >= 0;
                }""",
                arg={"userId": account["userId"]},
                timeout=READY_MS,
            )
        elif kind == "setup":
            page.wait_for_function(
                """async (spec) => {
                  let store = null;
                  try { store = JSON.parse(localStorage.getItem('kpiNavigator.kpiYearStore') || 'null'); }
                  catch (e) { store = null; }
                  const meta = store && store.meta ? store.meta : {};
                  const setup = meta.setup || {};
                  const uid = localStorage.getItem('kpiNavigator.lastKpiUserId');
                  const tier = sessionStorage.getItem('kpiNavigator.subscriptionTier')
                    || localStorage.getItem('kpiNavigator.subscriptionTier');
                  if (uid !== spec.userId || tier !== 'basic' || meta.businessType !== 'restaurant') return false;
                  if (setup.complete === true) return false;
                  if (location.pathname.indexOf(spec.path) < 0) return false;
                  const nr = window.KpiNavigationReadiness;
                  if (!nr || typeof nr.settle !== 'function') return false;
                  const result = await nr.settle('basic');
                  if (!result || result.status !== 'SETUP_INITIAL_REQUIRED' || result.setupComplete) return false;
                  const resume = document.getElementById('kpi-nr-resume');
                  const dialog = document.getElementById('kpi-s0');
                  const visible = (!!resume && resume.hidden === false) || (!!dialog && dialog.hidden === false);
                  return spec.requireVisible ? visible : true;
                }""",
                arg={
                    "userId": account["userId"],
                    "path": case["path"].split("?")[0],
                    "requireVisible": "/app/annual/" in case["path"],
                },
                timeout=READY_MS,
            )
        elif kind == "profile-gate":
            page.wait_for_function(
                """(spec) => {
                  const guard = document.getElementById('kpi-nr-guard');
                  const uid = localStorage.getItem('kpiNavigator.lastKpiUserId');
                  const tier = sessionStorage.getItem('kpiNavigator.subscriptionTier')
                    || localStorage.getItem('kpiNavigator.subscriptionTier');
                  let store = null;
                  try { store = JSON.parse(localStorage.getItem('kpiNavigator.kpiYearStore') || 'null'); }
                  catch (e) { store = null; }
                  const setup = store && store.meta && store.meta.setup ? store.meta.setup : {};
                  return uid === spec.userId && tier === 'basic'
                    && !!guard && guard.hidden === false
                    && setup.complete !== true
                    && location.pathname.indexOf('/app/annual/') >= 0;
                }""",
                arg={"userId": account["userId"]},
                timeout=READY_MS,
            )
        elif kind == "profile-fallback":
            page.wait_for_function(
                """async (spec) => {
                  if (location.pathname.indexOf('/setting/profile_edit.html') < 0) return false;
                  const tier = sessionStorage.getItem('kpiNavigator.subscriptionTier')
                    || localStorage.getItem('kpiNavigator.subscriptionTier');
                  if (localStorage.getItem('kpiNavigator.lastKpiUserId') !== spec.userId || tier !== 'basic') return false;
                  const input = document.getElementById('profile-business-name');
                  const res = await fetch('/api/v1/profile.php', {credentials:'include'});
                  const body = await res.json();
                  const profile = body.profile || {};
                  const name = profile.businessName || '';
                  return res.status === 200 && name === '' && !!input && input.value === '';
                }""",
                arg={"userId": account["userId"]},
                timeout=READY_MS,
            )
            row["finalRoute"] = "/setting/profile_edit.html"
        elif kind == "pro-gate":
            page.wait_for_url("**/setting/change_plan.html", timeout=READY_MS)
            page.wait_for_function(
                """(spec) => {
                  const tier = sessionStorage.getItem('kpiNavigator.subscriptionTier')
                    || localStorage.getItem('kpiNavigator.subscriptionTier');
                  return localStorage.getItem('kpiNavigator.lastKpiUserId') === spec.userId
                    && tier === 'basic'
                    && location.pathname.indexOf('/setting/change_plan.html') >= 0;
                }""",
                arg={"userId": account["userId"]},
                timeout=READY_MS,
            )
        elif kind == "insight-gate":
            page.wait_for_function(
                """(spec) => localStorage.getItem('kpiNavigator.lastKpiUserId') === spec.userId
                  && !!document.getElementById('global-nav-index-btn')""",
                arg={"userId": account["userId"]},
                timeout=READY_MS,
            )
            page.click("#global-nav-index-btn")
            page.wait_for_url("**/setting/change_plan.html", timeout=READY_MS)
        elif kind == "restaurant":
            page.wait_for_function(
                """(spec) => {
                  const tier = sessionStorage.getItem('kpiNavigator.subscriptionTier')
                    || localStorage.getItem('kpiNavigator.subscriptionTier');
                  let store = null;
                  try { store = JSON.parse(localStorage.getItem('kpiNavigator.kpiYearStore') || 'null'); }
                  catch (e) { store = null; }
                  const year = store && store.years && store.years['2026'] ? store.years['2026'] : {};
                  const food = year.dailyIncome && year.dailyIncome.food_sales
                    ? Number(year.dailyIncome.food_sales['2026-10-03']) : null;
                  const lunch = year.dailyMeal && year.dailyMeal.lunch_sales
                    ? Number(year.dailyMeal.lunch_sales['2026-10-03']) : null;
                  return localStorage.getItem('kpiNavigator.lastKpiUserId') === spec.userId
                    && tier === 'pro'
                    && store && store.meta && store.meta.businessType === 'restaurant'
                    && food === 32000 && lunch === 18000
                    && location.pathname.indexOf('/app/monthly/') >= 0;
                }""",
                arg={"userId": account["userId"]},
                timeout=READY_MS,
            )
        elif kind == "settings":
            page.wait_for_function(
                """(spec) => {
                  const tier = sessionStorage.getItem('kpiNavigator.subscriptionTier')
                    || localStorage.getItem('kpiNavigator.subscriptionTier');
                  if (localStorage.getItem('kpiNavigator.lastKpiUserId') !== spec.userId) return false;
                  if (tier !== 'basic') return false;
                  if (location.pathname.indexOf(spec.finalPath) < 0) return false;
                  const el = spec.selector ? document.querySelector(spec.selector) : document.body;
                  if (!el) return false;
                  if (spec.text && (el.textContent || '').indexOf(spec.text) < 0) return false;
                  if (spec.prefix && location.pathname.indexOf(spec.prefix) !== 0) return false;
                  if (spec.lang && document.documentElement.lang !== spec.lang) return false;
                  return true;
                }""",
                arg={
                    "userId": account["userId"],
                    "finalPath": case.get("finalPath") or case["path"].split("?")[0],
                    "selector": case.get("selector") or "",
                    "text": case.get("text") or "",
                    "prefix": case.get("prefix") or "",
                    "lang": case.get("lang") or "",
                },
                timeout=READY_MS,
            )
        elif kind == "public":
            page.wait_for_function(
                """(spec) => {
                  if (location.pathname.indexOf(spec.finalPath) < 0) return false;
                  if (localStorage.getItem('kpiNavigator.lastKpiUserId')) return false;
                  if (spec.prefix && location.pathname.indexOf(spec.prefix) !== 0) return false;
                  if (spec.lang && document.documentElement.lang !== spec.lang) return false;
                  const el = spec.selector ? document.querySelector(spec.selector) : document.body;
                  return !!el;
                }""",
                arg={
                    "finalPath": case.get("finalPath") or case["path"].split("?")[0],
                    "selector": case.get("selector") or "",
                    "prefix": case.get("prefix") or "",
                    "lang": case.get("lang") or "",
                },
                timeout=READY_MS,
            )
        else:
            raise SystemExit(f"unknown kind {kind}")
        fatal = fatal_text(page)
        row["finalUrl"] = page.url
        if fatal:
            row["detail"] = fatal
        elif len(bag["pageerrors"]) != before:
            row["detail"] = bag["pageerrors"][before]
        else:
            row["result"] = "PASS"
    except Exception as exc:
        row["finalUrl"] = page.url
        row["detail"] = str(exc).splitlines()[0][:400]
    return row


def main() -> None:
    php_path = php_bin()
    if not php_path:
        raise SystemExit("php not found")
    php = php_command(php_path)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    accounts = {row["id"]: row for row in manifest["accounts"]}
    work = Path(tempfile.mkdtemp(prefix="kpn-p4a-"))
    data_root = work / "data"
    data_root.mkdir()
    try:
        user, password = read_runtime_identity()
        cfg = work / "mysql.php"
        port = free_port()
        write_config(
            cfg,
            data_root,
            dbUser=user,
            dbPass=password,
            passwordResetBaseUrl=f"http://127.0.0.1:{port}",
        )
        seeded = run_php(php, [str(MYSQL_SEED)], cfg)
        if seeded.returncode != 0 or "seeded kpn_local_test 5" not in (seeded.stdout or ""):
            raise SystemExit(f"mysql seed failed: {seeded.stderr or seeded.stdout}")
        before = json.loads(run_php(php, [str(MYSQL_SEED), "dump"], cfg).stdout)
        if not str(before.get("runtimeUser", "")).startswith("kpn_local_runtime@"):
            raise SystemExit(f"runtime user mismatch: {before.get('runtimeUser')}")
        if before.get("database") != "kpn_local_test" or before.get("legacyRows") or before.get("factRows") != 0:
            raise SystemExit("seed safety check failed")
        if len(before.get("users") or []) != 5:
            raise SystemExit("expected five canonical users")

        env = os.environ.copy()
        env["KPI_V1_CONFIG"] = str(cfg)
        server = subprocess.Popen(
            php + ["-S", f"127.0.0.1:{port}", "-t", str(ROOT)],
            cwd=str(ROOT),
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        bag = {"pageerrors": [], "production": [], "ftp": [], "mail": []}
        results = []
        try:
            wait_http(port)
            from playwright.sync_api import sync_playwright

            base = f"http://127.0.0.1:{port}"
            order = [
                "fx-basic-restaurant-ready",
                "fx-pro-hotel-ready",
                "fx-pro-restaurant-ready",
                "fx-basic-profile-required",
                "fx-basic-setup-required",
            ]
            groups = []
            for case in CASES:
                key = (case.get("group") or "jp", case["fixture"])
                if key not in groups:
                    groups.append(key)
            mutations = []
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(channel="chrome", headless=True)
                for group, fixture_id in groups:
                    context = browser.new_context()
                    page = context.new_page()
                    watch(page, bag)
                    if fixture_id != "public":
                        login(page, base, accounts[fixture_id])
                    for case in CASES:
                        if (case.get("group") or "jp", case["fixture"]) != (group, fixture_id):
                            continue
                        account = {} if fixture_id == "public" else accounts[fixture_id]
                        results.append(open_case(page, base, case, account, bag))
                    context.close()
                    if fixture_id == "public":
                        continue
                    observed = dump_db(php, cfg)
                    categories = fixture_delta(accounts[fixture_id], observed)
                    if categories:
                        mutations.append({
                            "group": group,
                            "fixture": fixture_id,
                            "fixtureMutated": True,
                            "categories": list(categories),
                            "detail": categories,
                            "reseed": "single-fixture",
                        })
                        reseed_fixture(php, cfg, fixture_id)
                        restored = dump_db(php, cfg)
                        if fixture_delta(accounts[fixture_id], restored):
                            raise SystemExit(f"reseed did not restore {fixture_id}")
                browser.close()
        finally:
            server.terminate()
        final = dump_db(php, cfg)
        final_dirty = {
            fixture_id: fixture_delta(accounts[fixture_id], final)
            for fixture_id in order
            if fixture_delta(accounts[fixture_id], final)
        }
        failed = [row for row in results if row["result"] != "PASS"]
        supplemental = [row["id"] for row in results if row.get("coverage") == "supplemental"]
        contract_completed = sum(
            1 for row in results if row.get("coverage") != "supplemental" and row["result"] == "PASS"
        )
        report = {
            "phase": "BR-LOCAL-VERIFY-01 Phase 4A-3",
            "executedCases": len(results),
            "passedCases": len(results) - len(failed),
            "failedCases": len(failed),
            "contractCoverageCompleted": contract_completed,
            "contractCoverageTarget": CONTRACT_TARGET,
            "supplementalCases": supplemental,
            "remainingContractCoverage": CONTRACT_TARGET - contract_completed,
            "pageerrors": bag["pageerrors"],
            "productionRequests": bag["production"],
            "productionDbAccess": 0 if before.get("database") == "kpn_local_test" else 1,
            "ftp": bag["ftp"],
            "realMail": bag["mail"],
            "runtimeUser": before.get("runtimeUser"),
            "database": before.get("database"),
            "fixtureMutations": mutations,
            "finalCanonical": not final_dirty,
            "finalDirty": final_dirty,
            "profileRouteNote": "Fresh profile.html falls through to profile_edit.html when kpi-profile-last is absent. Ready data still hydrates. Profile-required stays empty.",
            "results": results,
        }
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({
            "ok": not failed and not bag["pageerrors"] and not bag["production"] and not bag["ftp"] and not bag["mail"] and not final_dirty,
            "executedCases": report["executedCases"],
            "passedCases": report["passedCases"],
            "failedCases": report["failedCases"],
            "contractCoverageCompleted": report["contractCoverageCompleted"],
            "contractCoverageTarget": report["contractCoverageTarget"],
            "supplementalCases": report["supplementalCases"],
            "remainingContractCoverage": report["remainingContractCoverage"],
            "pageerrors": len(bag["pageerrors"]),
            "productionRequests": len(bag["production"]),
            "fixtureMutations": mutations,
            "finalCanonical": not final_dirty,
            "failed": [row["id"] + ": " + row["detail"] for row in failed],
        }, ensure_ascii=False))
        if failed or bag["pageerrors"] or bag["production"] or bag["ftp"] or bag["mail"] or final_dirty:
            raise SystemExit("phase 4 smoke failed")
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
