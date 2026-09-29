# BR-LAUNCH-09 Extension — Lifecycle Segmentation + Marketing Opt-in (M1 draft)

Status: **M1 DRAFT — waiting for Shin decisions (section 15).** Nothing implemented, nothing deployed.
Public Registration is live (`registrationEnabled` true); this work must not break it.

Two separate data areas, never joined:

| | Lifecycle History (`kpi_account_deletions`) | Marketing Subscribers (`kpi_marketing_subscribers`) |
|---|---|---|
| Purpose | churn / retention / return / segment analysis | news about KPN / Forge Laboratory services, only with opt-in |
| Email | HMAC only (never raw) | raw normalized email (needed to send) |
| Created | on account delete | only on explicit opt-in |
| Retention | 3 years after deletion (unchanged contract) | while subscribed; evidence 3 years after the last marketing mail (section 8) |
| Link between them | none (no lifecycle id / HMAC in subscribers; no subscriber id in history) | |

---

## 1. Legal / privacy audit

Sources checked 2026-09-29:

- 特定商取引法（通信販売電子メール広告）— 消費者庁 特定商取引法ガイド「通信販売」, 施行規則: opt-in required; the record of the request / consent must be kept **for 3 years from the day the last e-mail advertisement was sent**, also when the recipient later refuses. For consent collected through a fixed web form, keeping the fixed text shown + when it was shown + the per-address record is sufficient. KPN sells an online subscription service → mails promoting KPN / new services are treated as 通信販売電子メール広告 (conservative).
- 特定電子メール法 — 総務省「特定電子メールの送信の適正化等に関する法律のポイント」/ ガイドライン: opt-in; consent record kept until 1 month after the last send (1 year after a measure order); once a refusal is received, no further sends. **Every ad mail must show**: sender name, that the recipient can refuse + the refusal address / URL (right before or after it), sender postal address, and a contact for complaints / questions (phone, email or URL). Address / contact may be on a linked page if the mail says where.
- Longest period wins → **3 years from the last marketing send** (Shin's first candidate is consistent).
- Other regions (EN / ZH-TW users): GDPR / ePrivacy (consent, withdrawal as easy as giving it), Taiwan PDPA (stop on objection; first marketing contact must offer refusal), US CAN-SPAM (postal address, opt-out honored promptly). The same opt-in + one-link unsubscribe + sender block covers them.

Current state (code):

- Privacy (JP / EN / ZH-TW, 2026-09-29): no marketing purpose; §3 mentions "consent for marketing cookies" only; §1 退会履歴 lists user id / HMAC / dates / plan / role — no segment fields.
- Terms (2026-02-16): no marketing / notification clause; 第9条 defers data handling to the Privacy Policy → **no conflict**, Terms need no change.
- Registration: one checkbox 「利用規約およびプライバシーポリシーに同意します」 (`agree_terms`), consent row in `kpi_user_consents` (terms / privacy version, accepted_at, source). No marketing field.
- Delete Account: STEP 1 (`delete_account1`) → STEP 2 data (`delete_account3`) → STEP 3 password (`delete_account4-1`) → STEP 4 final confirm (`delete_account5`) → completion. Server `_account_delete.php` writes the lifecycle row in the delete transaction.
- Mail: `api/v1/_mail.php` = PHP `mail()`, plain text, From "Key Performance Navigator <supportFrom>". Used for email-change codes / notices, password reset, feedback. **No marketing send exists; none is added in this Phase.**
- Settings: no notification / newsletter preference anywhere.
- Published operator info: name (Forge-Lab, 運営責任者) + support@forge-laboratory.com. **No postal address / phone published** → needed before the first marketing mail (not before consent collection).

## 2. Proposed schema

```sql
-- M2: new (CREATE only)
CREATE TABLE IF NOT EXISTS kpi_marketing_subscribers (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  normalized_email VARCHAR(255) NOT NULL,
  status VARCHAR(16) NOT NULL,                 -- subscribed | unsubscribed
  locale VARCHAR(8) NOT NULL,                  -- ja | en | zh-TW
  account_user_id VARCHAR(64) NULL,            -- set while a KPN account with this email exists; NULL after delete
  consent_at DATETIME NULL,                    -- latest opt-in
  consent_source VARCHAR(32) NULL,             -- registration | settings | delete_keep
  consent_text_version VARCHAR(32) NULL,       -- e.g. mkt-2026-10-xx (fixed text kept in code + docs)
  privacy_version_at_consent VARCHAR(32) NULL,
  unsubscribed_at DATETIME NULL,
  unsubscribe_source VARCHAR(32) NULL,         -- link | settings | delete_stop | founder
  last_marketing_sent_at DATETIME NULL,
  unsub_token_hash CHAR(64) NULL,              -- sha256 of the random token; plain token never stored
  retain_until DATETIME NULL,                  -- evidence purge date (section 8)
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_kpi_marketing_email (normalized_email),
  UNIQUE KEY uq_kpi_marketing_token (unsub_token_hash),
  KEY idx_kpi_marketing_status (status),
  KEY idx_kpi_marketing_account (account_user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Consent evidence, append-only (who / when / how / which text); no FK so it survives account delete
CREATE TABLE IF NOT EXISTS kpi_marketing_consent_events (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  subscriber_id BIGINT UNSIGNED NOT NULL,
  event VARCHAR(24) NOT NULL,                  -- subscribe | unsubscribe | keep_after_delete | email_changed | erase_request
  source VARCHAR(32) NOT NULL,
  consent_text_version VARCHAR(32) NULL,
  privacy_version VARCHAR(32) NULL,
  locale VARCHAR(8) NULL,
  occurred_at DATETIME NOT NULL,
  PRIMARY KEY (id),
  KEY idx_kpi_marketing_events_sub (subscriber_id, occurred_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- M5: lifecycle segment snapshot (additive nullable columns; existing rows stay NULL)
ALTER TABLE kpi_account_deletions
  ADD COLUMN seg_country VARCHAR(8) NULL,
  ADD COLUMN seg_business_type VARCHAR(32) NULL,
  ADD COLUMN seg_currency VARCHAR(8) NULL;
```

- No FK from `account_user_id` to `kpi_users` (the row must be able to outlive the account); the delete flow sets it explicitly.
- Never stored in marketing tables: password / hash, business / sales data, profile, IP, UA, lifecycle id, HMAC.
- File-storage mode (local / dev) gets the same contract in JSON files under `api/v1/data/marketing/` (flock), like lifecycle.
- Rollback: M2 tables can be dropped (no other table references them); the M5 columns can be dropped (nothing else reads them). Idempotent: `IF NOT EXISTS`; ALTER guarded by an information_schema check in the runner.

## 3. Lifecycle segment contract

Added to the history row at delete time, read from the account's profile / store in the same transaction, **normalized to coded values only**:

| Field | Source | Stored value |
|---|---|---|
| `seg_country` | profile `country` | ISO 3166-1 alpha-2 if it maps (e.g. `JP`, `TW`, `US`); anything else → `other`; empty → NULL |
| `seg_business_type` | profile `business_type` (fallback `store.meta.businessType`) | the fixed Business Type code (e.g. `restaurant`); not in the list → `other`; empty → NULL |
| `seg_currency` | profile `currency` | ISO 4217 code if valid (e.g. `JPY`); else `other`; empty → NULL |
| plan / kind / created / deleted / lifetime | existing | unchanged |

- Existing columns unchanged (lifecycle id, previous user id, HMAC, origin, returned, cleanup, exclude).
- Never stored: raw email, business / company name, city, state / region, genre / free text, sales, customer counts, daily data, password, consent contents, IP, UA.
- Existing history rows (incl. the current one): **left NULL**, shown as "Unknown". No backfill / guessing.
- Metrics: Founder Dashboard gets churn breakdown by country / business type / currency / plan (same frozen churn rules; NULL = Unknown bucket). Retention stays 3 years (same purge).

## 4. Marketing consent contract

- Opt-in only; default unchecked everywhere; never bundled with Terms / Privacy consent.
- Existing users: **no row** = not subscribed. No bulk opt-in, no "consented" flag set for anyone.
- Subscribe sources: Registration checkbox, Settings preference (M3), keep-after-delete choice (M4, only for already-subscribed users).
- One row per normalized email. Subscribing again with an existing row → status subscribed + new consent event (evidence history kept).
- Registration with the box checked:
  - 201 → subscriber row (or reactivated row) + event, in the same transaction as the account + consent rows (MySQL). If the marketing write fails the registration still fails closed (503) — no half state.
  - 409 `email_taken` / any 4xx → nothing written.
- Unchecked → no marketing row.
- Email change (existing verified flow): the subscription follows the account → email updated + `email_changed` event (recommended; see decision D4).
- No marketing mail is sent in this Phase.

## 5. Registration UX

Below the Terms / Privacy checkbox, a separate unchecked checkbox + helper text (JP / EN / ZH-TW, Sci-Fi / Office):

- JP: 「Forge Laboratoryから、KPNの新機能・新サービス・キャンペーン等のお知らせをメールで受け取る（任意）」
  helper: 「配信はいつでも停止できます。退会後も受け取るかは、退会時に選べます。」
- EN: "Receive emails from Forge Laboratory about new KPN features, new services and campaigns (optional)"
  helper: "You can unsubscribe at any time. When you delete your account, you can choose whether to keep receiving them."
- ZH-TW: 「接收 Forge Laboratory 以電子郵件寄送的 KPN 新功能、新服務及活動等通知（選填）」
  helper: 「您可隨時取消訂閱。刪除帳戶時，可選擇是否繼續接收。」

Register button condition unchanged (Terms / Privacy only). Payload gains `marketingOptIn: true|false` (+ the consent text version the page showed); server validates the version. `registration-status` also returns `marketingConsentVersion`.

Settings (M3): a "お知らせメール" row on the existing Preferences page: current status + subscribe / unsubscribe (session user only, current email).

## 6. Delete UX

STEP 4 (final confirm, `delete_account5`) gets a Marketing block driven by the server (session user):

- Subscribed → required choice, **no preselection**: 「退会後もForge Laboratoryからのお知らせを受け取る」 / 「配信を停止する」. Delete button stays disabled until one is chosen (recommended, D2).
- Not subscribed → text only: 「お知らせメールは配信されていません。退会後にメールアドレスを保持することはありません。」 No new opt-in offered at delete (recommended, D3).
- Server: `delete` action takes `marketingAfterDelete: "keep" | "stop"` (required only if subscribed).
  - keep → subscriber row stays subscribed, `account_user_id` NULL, event `keep_after_delete`.
  - stop / not subscribed → status unsubscribed (+ event) and the raw email is removed per section 8.
  - Done inside the delete transaction; failure → rollback (fail closed, same as lifecycle).
- STEP 2 copy (`delete_account3`) gains one line: 「お知らせメールを退会後も受け取ることを選んだ場合に限り、メールアドレスを配信用に保持します（事業データとは別に管理し、KPNのデータは復元されません）。」
- KPN business data is deleted in both cases; lifecycle keeps HMAC only.

## 7. Unsubscribe contract

- Every future marketing mail carries a personal link `…/kpi-navigator/unsubscribe/?t=<subscriberId>.<secret>` + `List-Unsubscribe` / `List-Unsubscribe-Post: List-Unsubscribe=One-Click` headers + reply-to-support fallback.
- Token: 32 random bytes, only `sha256` stored; rotated on every re-subscribe; revoked (hash NULL) on erase. Not time-expiring while the row exists (a legal opt-out must keep working), revocable instead.
- No login. GET shows a confirm page (no state change, safe for mail scanners); POST (button, or One-Click POST) unsubscribes. Optional reason (fixed choices + short text, stored without the email, like anonymized feedback).
- Same neutral response for unknown / already unsubscribed / valid tokens (no enumeration); double unsubscribe = success page.
- After unsubscribe: never sent again. Re-subscribe only by the person's explicit action (Settings while logged in, or a new registration opt-in).
- Rate limit: unsubscribe POST per token + global bucket (existing file limiter); Settings / Founder endpoints are session / Founder gated.

## 8. Consent evidence retention (separate from Lifecycle's 3 years)

- Subscribed: kept while subscribed.
- Unsubscribed / delete-stop / Founder erase:
  - no marketing mail ever sent → email + events deleted immediately (nothing to prove);
  - at least one mail sent → **evidence-only** row (status unsubscribed, never mailed) until `last_marketing_sent_at + 3 years`, then purged automatically (特商法; covers 特電法 1 month). Recommended, D1.
- `retain_until` computed on each state change; purge runs with the existing lifecycle purge hook.
- Founder "erase" of an evidence-only row before its date is blocked with a notice (legal hold); a full erase is possible when nothing was sent.

## 9. Privacy revisions (JP / EN / ZH-TW; version / Last updated = production deploy date)

§1 退会履歴 (replace):
- JP: 「退会履歴　アカウント削除時に作成する最小限の記録（削除前の内部ユーザーID、メールアドレスから生成した照合用の値、アカウント作成日・削除日・利用期間、削除時のプラン・権限・アカウント種別、ならびに国、業種、通貨）。メールアドレス、屋号・会社名、市区町村・州／都道府県、売上などの事業入力データは含みません。照合用の値は当方が管理する秘密鍵を用いて生成するもので、その値だけからメールアドレスを復元することはできません。」
- EN: "Account deletion record: a minimal record created when an account is deleted (the former internal user ID, a matching value derived from the email address, account creation date, deletion date and period of use, plan, role and account type at deletion, and country, business type and currency). It does not include the email address, business or company name, city, state / region, or business data such as sales. The matching value is generated with a secret key managed by us and the email address cannot be recovered from that value alone."
- ZH-TW: 「帳戶刪除紀錄：刪除帳戶時建立的最低限度紀錄（刪除前的內部使用者 ID、由電子郵件地址產生的比對用值、帳戶建立日、刪除日及使用期間、刪除時的方案、權限及帳戶類型，以及國家、業種及幣別）。不包含電子郵件地址、商號／公司名稱、市區町村、州／都道府縣，以及營業額等事業輸入資料。比對用值係以本方管理之秘密金鑰產生，僅憑該值無法還原電子郵件地址。」

§1 new item:
- JP: 「お知らせメールの配信情報　お知らせメールの受信を希望された場合に限り、メールアドレス、表示言語、同意日時・同意した画面と文言の版、配信停止日時、最終配信日時」
- EN: "Newsletter information: only if you choose to receive our emails — email address, display language, date and time of consent, the screen and wording version you agreed to, unsubscribe date and time, and the date of the last email sent"
- ZH-TW: 「通知郵件寄送資訊：僅限您選擇接收通知郵件時——電子郵件地址、顯示語言、同意日期時間、同意時之畫面及文字版本、取消訂閱日期時間，以及最後寄送日期時間」

§2 purposes (replace the statistics line + add one):
- JP: 「退会数・利用継続期間・再登録の状況、ならびに国・業種・通貨・プラン別の傾向など、事業運営のための統計分析（退会履歴を利用します）」／「ご本人が受信を希望された場合に限り、KPNの新機能、Forge Laboratoryの新サービス、キャンペーン等のお知らせをメールで送ること」
- EN: "Statistical analysis for running our business, such as the number of deletions, period of use, re-registration, and trends by country, business type, currency and plan (using account deletion records)" / "Only if you have asked to receive them, sending emails about new KPN features, new Forge Laboratory services, campaigns and similar news"
- ZH-TW: 「為事業經營所需之統計分析，例如刪除數量、使用期間、重新註冊狀況，以及依國家、業種、幣別及方案之趨勢（使用帳戶刪除紀錄）」／「僅限您希望接收時，以電子郵件寄送 KPN 新功能、Forge Laboratory 新服務及活動等通知」

§3 consent line (replace): JP 「同意（任意の分析Cookie、およびお知らせメールの配信）」 / EN "Consent (optional analytics cookies and our newsletter emails)" / ZH-TW 「同意（選用之分析 Cookie 及通知郵件之寄送）」

§6 new paragraph after the 退会履歴 paragraph:
- JP: 「お知らせメールの配信情報は、事業入力データとは別に管理し、受信を希望されている間保持します。配信はメール内のリンクまたは設定画面からいつでも停止できます。アカウント削除時に受信の継続を選んだ場合に限り、アカウント削除後もメールアドレスを配信用に保持します（KPNのデータは保持・復元しません）。継続を選ばなかった場合や配信を停止した場合は、配信用のメールアドレスを削除します。ただし、すでにお知らせメールを送信していた場合は、法令に基づき、同意の記録（メールアドレス、同意・停止の日時および方法）を最後の送信日から3年間保持し、その間メールを送ることはありません。」
- EN: "Newsletter information is kept separately from business data for as long as you want to receive our emails. You can unsubscribe at any time from the link in each email or in Settings. Only if you choose to keep receiving them when deleting your account do we keep your email address for this purpose after deletion (KPN data is neither kept nor restored). If you do not choose this, or you unsubscribe, we delete the email address used for sending. However, if we have already sent you such emails, we keep the record of your consent (email address, date, time and method of consent and unsubscription) for 3 years from the last email as required by law, and we do not email you during that time."
- ZH-TW: 「通知郵件寄送資訊與事業輸入資料分開管理，於您希望接收期間保存。您可隨時透過郵件中的連結或設定畫面取消訂閱。僅限您於刪除帳戶時選擇繼續接收，我們才會於帳戶刪除後保留您的電子郵件地址以供寄送（不保存亦不還原 KPN 資料）。未選擇繼續或取消訂閱時，我們將刪除寄送用之電子郵件地址。惟若我們已寄送過通知郵件，將依法令自最後寄送日起保存同意紀錄（電子郵件地址、同意及取消之日期時間與方式）3 年，期間內不會再寄送郵件。」

§7 add: JP 「お知らせメールは、各メールのリンク、設定画面、または12.のお問い合わせ先への連絡により、いつでも配信を停止できます。」 (EN / ZH-TW same meaning).

## 10. Founder UI

- New page `admin/marketing/` (Founder Super Admin only, English like the rest): counts (subscribed / unsubscribed / evidence-only / total), table email (Founder only) / status / locale / consent date / source / consent text version / last sent / unsubscribed at / has account (yes / no), actions: manual unsubscribe, erase (blocked while under legal hold). No send button.
- Deleted Accounts: **no email / marketing column.** Segment columns Country / Business Type / Currency added (compact; "Unknown" for NULL).
- Email Lookup Option B: the email stays only in the POST body and page memory; after a lookup the page shows `Matched lookup: <entered email>` above the result, the input is cleared; the text lives in a JS variable only (no URL, no storage), so reload / navigation removes it. API responses keep no raw email; the server does not log it (unchanged).

## 11. DB / schema impact

- Two new tables (CREATE only) + three nullable columns on `kpi_account_deletions` (ALTER ADD COLUMN, MySQL 8 instant, no data rewrite) — D5.
- Existing tables otherwise unchanged; no change to `kpi_users` / `kpi_user_consents`.
- Rollout order (M7): backup → migration (tables + columns) → schema verify → deploy server (register / delete / lifecycle / marketing APIs, all tolerant of the feature being off) → deploy Founder UI → deploy Privacy + Registration + Delete + Settings pages together on the same day (Privacy date = that day) → production-safe verify → controlled smoke with the kept test account only after Shin GO.
- Registration stays live throughout: the server accepts old payloads (no `marketingOptIn` = not subscribed) so cached pages keep working.

## 12. Security

- Unsubscribe token: `random_bytes(32)`, sha256 stored, rotated / revoked, constant-time compare, neutral responses.
- No secret in repo / logs; token only inside the mail.
- Marketing APIs: Settings = session + expected-user guard; Founder = Founder Super Admin; unsubscribe = token + rate limit. Registration marketing flag passes the existing layers first (header reject, global / IP / email limiters).
- Enumeration: registration keeps the existing 409 behavior (frozen); marketing endpoints never reveal whether an email is subscribed.
- Raw email only in the marketing table and the Founder marketing page; never in lifecycle rows / responses.

## 13. Implementation phases

- M1 Audit / contract / Privacy final draft (this document) → Shin decisions
- M2 DB + server marketing infrastructure (schema, helpers, file mode, unsubscribe endpoint + page, purge)
- M3 Registration checkbox + Settings preference
- M4 Delete Account integration (STEP 4 choice, STEP 2 copy, server)
- M5 Lifecycle segment snapshot + segment metrics
- M6 Founder UI (Marketing page, Deleted Accounts segment columns, Lookup Option B)
- M7 Production migration / deploy / smoke (Privacy date = deploy day)
- Later, separate Phase: marketing sender (provider, sender block with address / contact, List-Unsubscribe headers, send log → `last_marketing_sent_at`)

## 14. Smoke plan

Local (PHP + MariaDB + Chrome, file + MySQL):

1. registration unchecked → 201, no subscriber
2. checked → subscriber + event
3. consent metadata (time, source, text version, privacy version, locale)
4. independent of the Terms consent row
5. duplicate email → 409, no subscriber change; re-registration after delete with opt-in reactivates the row
6. existing users have no row
7. delete subscribed → keep → row kept, account link NULL
8. delete subscribed → stop → email removed (never sent) / evidence-only (sent)
9. delete unsubscribed → no raw email anywhere
10. lifecycle row has no raw email
11-17. segment snapshot: country / business type / currency normalization, plan, kind, retention fields, NULL for missing
18-20. unsubscribe, double unsubscribe, re-subscribe (Settings only)
21-22. JP / EN / ZH-TW × Sci-Fi / Office pages
23-26. registration, delete, lifecycle metrics regressions, Founder access control

Production (after deploy, Shin GO): read-only + the kept test account only; no new accounts.

## 15. Decisions needed

- D1 Evidence after opt-out when mails were sent: evidence-only row for 3 years after the last send (legal) — recommended.
- D2 Delete STEP 4 for subscribed users: required choice with no preselection — recommended.
- D3 Offer a new opt-in inside Delete for unsubscribed users: no — recommended.
- D4 Email change: the subscription follows the account (email updated + event) — recommended.
- D5 Segment storage: nullable columns on `kpi_account_deletions` (ALTER ADD COLUMN) — recommended; alternative: a separate segment table (CREATE only).
- D6 Sender postal address / phone for marketing mails: decide in the sender Phase (not needed to collect consent) — recommended.
