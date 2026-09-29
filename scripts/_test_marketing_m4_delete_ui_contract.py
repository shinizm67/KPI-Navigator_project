"""BR-LAUNCH-09 Extension M4 — Delete UI newsletter contract (static checks).

STEP 4 asks keep / stop only while subscribed (no preselection, Delete disabled until chosen), shows a notice
otherwise, and blocks while the state is unknown. STEP 2 explains the newsletter data separately from the
account deletion record. The server keeps the required choice.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
results = []


def check(name, ok, detail=""):
    results.append(bool(ok))
    print(("PASS  " if ok else "FAIL  ") + name + ("" if ok else "  :: " + str(detail)[:300]))


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


STEP4 = {"ja": "setting/delete_account5.html", "en": "en/setting/delete_account5.html", "zh": "zh-tw/setting/delete_account5.html"}
STEP2 = {"ja": "setting/delete_account3.html", "en": "en/setting/delete_account3.html", "zh": "zh-tw/setting/delete_account3.html"}
KEEP = {"ja": "退会後もお知らせメールを受け取る", "en": "Keep receiving email updates after deletion", "zh": "刪除帳戶後仍接收通知郵件"}
STOP = {"ja": "お知らせメールの配信を停止する", "en": "Stop email updates", "zh": "停止寄送通知郵件"}
NONE = {"ja": "現在、お知らせメールは配信されていません。退会後にメールアドレスを配信用として保持することはありません。",
        "en": "You are not currently receiving email updates. We will not keep your email address for sending them after deletion.",
        "zh": "目前未寄送通知郵件給您。刪除帳戶後，不會保留您的電子郵件地址用於寄送。"}
S2 = {"ja": ("<li>お知らせメールの配信先（STEP 4 で「退会後もお知らせメールを受け取る」を選んだ場合のみ。", "<li>お知らせメールの同意記録（"),
      "en": ("<li>Email updates recipient (only if you choose \"Keep receiving email updates after deletion\" in Step 4", "<li>Email updates consent record ("),
      "zh": ("<li>通知郵件收件地址（僅限您於步驟 4 選擇「刪除帳戶後仍接收通知郵件」時", "<li>通知郵件同意紀錄（")}


def tag(html, el_id):
    m = re.search(r"<[a-z]+[^>]*\bid=\"%s\"[^>]*>" % re.escape(el_id), html)
    return m.group(0) if m else ""


def main():
    for lang, rel in STEP4.items():
        s = read(rel)
        form = s[s.find('id="delete-final-form"'):s.find("</form>", s.find('id="delete-final-form"'))]
        check(f"[{lang}] STEP 4 newsletter block inside the delete form", 'id="delete-marketing"' in form)
        check(f"[{lang}] loading shown first; choice / notice / unknown hidden until the server answers",
              " hidden" not in tag(s, "delete-marketing-loading")
              and all(" hidden" in tag(s, i) for i in ("delete-marketing-choice", "delete-marketing-none", "delete-marketing-unknown")))
        radios = re.findall(r"<input[^>]*name=\"marketing_after_delete\"[^>]*>", s)
        check(f"[{lang}] exactly keep + stop radios, no preselection",
              len(radios) == 2 and 'value="keep"' in radios[0] and 'value="stop"' in radios[1]
              and not any("checked" in r for r in radios), radios)
        check(f"[{lang}] keep / stop wording", KEEP[lang] in s and STOP[lang] in s)
        check(f"[{lang}] not-subscribed notice (no new opt-in offered)", NONE[lang] in s
              and s.count('name="marketing_after_delete"') == 2 and "marketing-optin" not in s)
        check(f"[{lang}] Sci-Fi + Office styles for the block",
              ".si-fi.office-mode.delete-account-page .delete-marketing-fieldset" in s and ".delete-marketing-fieldset {" in s)
        check(f"[{lang}] delete script cache-bust = content hash",
              re.search(r"js/kpi-delete-account-page\.js\?v=[0-9a-f]{12}\"", s) is not None)
        s2 = read(STEP2[lang])
        keep_line, evid_line = S2[lang]
        remains = s2[s2.rfind('<div class="delete-retention-column">'):]
        check(f"[{lang}] STEP 2 lists newsletter recipient + consent record under 'remains', after the deletion record",
              keep_line in remains and evid_line in remains and remains.find(keep_line) > remains.find("<li>")
              and remains.find(evid_line) > remains.find(keep_line))

    js = read("js/kpi-delete-account-page.js")
    check("js: state read from the session user's preference API", "'/marketing/preference.php'" in js and "method: 'GET'" in js)
    check("js: Delete blocked while loading / unknown / subscribed without a choice",
          "mktState === 'loading' || mktState === 'unknown' || (mktState === 'subscribed' && !mktSelected())" in js)
    check("js: only a boolean server answer unlocks (anything else = unknown)",
          "typeof r.data.subscribed === 'boolean'" in js and js.count("showMarketing('unknown')") >= 3)
    check("js: radios reset (no preselection, also after back / forward cache)",
          "mktRadios[ri].checked = false" in js and "ev.persisted" in js and "checked = true" not in js)
    check("js: marketingAfterDelete sent only for a subscribed choice",
          "if (mktChoiceValue) body.marketingAfterDelete = mktChoiceValue;" in js
          and "var mktChoiceValue = mktState === 'subscribed' ? mktSelected() : '';" in js)
    check("js: submit refused client-side while loading / unknown / no choice",
          "if (mktState === 'loading' || mktState === 'unknown') return;" in js
          and "if (mktState === 'subscribed' && !mktChoiceValue) return;" in js)
    check("js: marketing_choice_required -> message + state reloaded (nothing deleted)",
          "code === 'marketing_choice_required'" in js and "MSG.marketingChanged()" in js)
    check("js: completion still only after 200 ok && deleted",
          "r.status === 200 && r.data && r.data.ok === true && r.data.deleted === true" in js)

    api = read("api/v1/auth/delete-account.php")
    core = read("api/v1/_account_delete.php")
    mkt = read("api/v1/_marketing.php")
    check("server: only keep | stop accepted", "in_array($body['marketingAfterDelete'], ['keep', 'stop'], true)" in api)
    check("server: subscribed without a choice -> 400 marketing_choice_required, rolled back",
          "'error' => 'marketing_choice_required'" in core and "return 'marketing_choice_required';" in core)
    op = mkt[mkt.find("function kpi_v1_marketing_op_account_deleted"):]
    op = op[:op.find("\n}\n")]
    check("server: delete never subscribes (not subscribed -> nothing created)",
          "return 'done';" in op and "subscribe" not in op.replace("'subscribed'", "").replace("choice_required", ""))

    passed = sum(results)
    print("\n%d passed, %d failed" % (passed, len(results) - passed))
    sys.exit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
