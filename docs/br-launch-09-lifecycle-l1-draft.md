# BR-LAUNCH-09 Phase 3A Extension — Account Lifecycle L1 Draft

**Status: FINAL DRAFT (L1) — waiting for Shin final approval. Not live.** Created 2026-09-29; retention decided 2026-09-29.

- Production Privacy Policy (`legal/privacy/`, `en/legal/privacy/`, `zh-tw/legal/privacy/`) is **unchanged**.
- `KPI_PRIVACY_VERSION` stays `2026-02-16` (no production update).
- Delete Account STEP 2 (`delete_account3.html` × 3 languages) is **unchanged** in production.
- No Lifecycle server implementation until Shin's final approval.

Order: Shin final approval → final Privacy version / date → L2 implementation.

Contract background: `docs/development-path.md` rows `phase3a_lifecycle_2026-09-29`, `phase3a_lifecycle_decisions_2026-09-29`, `phase3a_churn_freeze_2026-09-29`, `phase3a_retention_2026-09-29`.

---

## 0. Retention contract (decided by Shin, 2026-09-29)

- **Retention period: 3 years after account deletion.** Same contract in JP / EN / ZH-TW.
- This is **not** a statutory retention period. It is the period KPN needs for: churn analysis, account lifetime analysis, return / re-registration analysis, cohort analysis.
- A lifecycle history row is **deleted automatically** once 3 years have passed since its deletion date (`deleted_at + 3 years`).
- Kept as before: no raw email (HMAC matching value only); no business data; no consent history; no IP / UA; the Founder side provides a procedure to erase a history row on the person's request.

---

## 1. Privacy Policy final draft (changes only)

Unchanged sections are not repeated. "Add" = new text; existing text stays unless marked "Replace".

Header: Last updated = `TBD (set at final approval)`; `KPI_PRIVACY_VERSION` = `TBD (set at final approval)`.

### 1-1. 日本語（`legal/privacy/index.html`）

**§1 取得する情報 — Add (list item, after 利用情報):**

> **退会履歴** アカウント削除時に作成する最小限の記録（削除前の内部ユーザーID、メールアドレスから生成した照合用の値、アカウント作成日・削除日・利用期間、削除時のプランおよび権限）。メールアドレスそのものは保存しません。照合用の値は当方が管理する秘密鍵を用いて生成するもので、その値だけからメールアドレスを復元することはできません。

**§2 利用目的 — Add (list items):**

> - 退会数・利用継続期間・再登録の状況など、事業運営のための統計分析（退会履歴を利用します）
> - 同じメールアドレスで再度アカウントが作成された場合に、過去に利用があったことを判別すること（過去のデータを復元することはありません）

**§3 法的根拠（EEA／英国ユーザー向け） — Replace the 正当な利益 item:**

> 正当な利益（セキュリティ確保、不正防止、信頼性向上、ならびに退会履歴を用いた事業運営のための統計分析のため）

**§6 保存期間 — Add (paragraph, after the existing list):**

> アカウントが削除された場合、アカウント情報、事業入力データ、プロフィール、同意記録などは削除します。ただし、1.に記載した退会履歴に限り、統計分析および再登録の判別のため、**削除日から3年間**保持し、3年を経過した記録は自動的に消去します。この期間は法令上の保存期間ではなく、上記の目的に必要な期間として当方が定めたものです。退会履歴には、メールアドレス、パスワード、事業入力データ、同意記録、IPアドレス、ブラウザ情報は含まれません。

**§7 ユーザーの権利 — Add (paragraph, after the existing list):**

> アカウント削除後に退会履歴の消去を希望される場合は、12.のお問い合わせ先までご連絡ください。ご連絡いただいたメールアドレスをもとに該当する記録を特定し、消去します。

### 1-2. English (`en/legal/privacy/index.html`)

**§1 What we collect — Add (list item, after Usage data):**

> **Account deletion record:** a minimal record created when an account is deleted (the previous internal user ID, a matching value derived from the email address, the account creation date, deletion date and lifetime, and the plan and role at deletion). We do not store the email address itself. The matching value is generated with a secret key we control, and the email address cannot be recovered from that value alone.

**§2 Why we use it (Purposes) — Add (list items):**

> - Statistical analysis for running the business, such as the number of account deletions, how long accounts are used, and re-registrations (using account deletion records)
> - Recognizing that an account newly created with the same email address was used before (past data is never restored)

**§3 Legal bases (EEA/UK users) — Replace the Legitimate interests item:**

> Legitimate interests (security, fraud prevention, improving reliability, and statistical analysis for running the business using account deletion records)

**§6 Retention — Add (paragraph):**

> When an account is deleted, we delete the account data, business input data, profile, consent records and related data. Only the account deletion record described in section 1 is kept, for statistical analysis and recognizing re-registrations, **for 3 years from the deletion date**; records older than 3 years are erased automatically. This is not a statutory retention period; it is the period we set as necessary for these purposes. The account deletion record does not include the email address, password, business input data, consent records, IP address or browser information.

**§7 Your rights — Add (paragraph):**

> If you would like your account deletion record erased after your account has been deleted, contact us at the address in section 12. We will identify the matching record from the email address you provide and erase it.

### 1-3. 繁體中文（`zh-tw/legal/privacy/index.html`）

**§1 我們蒐集的資料 — Add (list item, after 使用資料):**

> **帳戶刪除紀錄：**刪除帳戶時建立的最小紀錄（刪除前的內部使用者 ID、由電子信箱產生的比對值、帳戶建立日、刪除日與使用期間，以及刪除時的方案與權限）。我們不會儲存電子信箱本身。比對值係使用我們管理的秘密金鑰產生，無法僅憑該值還原電子信箱。

**§2 使用目的 — Add (list items):**

> - 為經營本服務所進行的統計分析，例如帳戶刪除數、使用期間及重新註冊情形（使用帳戶刪除紀錄）
> - 以相同電子信箱重新建立帳戶時，判別該使用者曾經使用過本服務（不會還原過去的資料）

**§3 法律依據（EEA／英國用戶） — Replace the 正當利益 item:**

> 正當利益（安全、詐欺防範、提升可靠性，以及使用帳戶刪除紀錄進行經營本服務所需之統計分析）

**§6 保存期間 — Add (paragraph):**

> 帳戶刪除時，我們會刪除帳戶資料、業務輸入資料、個人資料設定、同意紀錄等。僅第 1 節所述之帳戶刪除紀錄，為統計分析及判別重新註冊之目的，**自刪除日起保存 3 年**，超過 3 年之紀錄將自動清除。此期間並非法定保存期間，而是我們依上述目的所訂定之必要期間。帳戶刪除紀錄不包含電子信箱、密碼、業務輸入資料、同意紀錄、IP 位址或瀏覽器資訊。

**§7 您的權利 — Add (paragraph):**

> 帳戶刪除後，如希望清除帳戶刪除紀錄，請透過第 12 節之聯絡方式與我們聯繫。我們將依您提供的電子信箱找出對應紀錄並予以清除。

---

## 2. Delete Account STEP 2 final draft copy (`delete_account3.html`)

Only the 「削除後も残るもの」 column changes: **one item is added at the top.** The 「削除されるデータ」 column is unchanged (the plan setting itself is deleted; only the plan at deletion stays in the minimal record).

| Language | Added item (first line of the "remains" column) |
|---|---|
| JP | 退会履歴（メールアドレスを含まない最小限の記録：作成日・削除日・削除時のプランなど。削除日から3年後に自動で消去されます） |
| EN | Account deletion record (a minimal record without your email address: creation date, deletion date, plan at deletion, etc. Erased automatically 3 years after the deletion date) |
| ZH-TW | 帳戶刪除紀錄（不含電子信箱的最小紀錄：建立日、刪除日、刪除時的方案等。自刪除日起 3 年後自動清除） |

---

## 3. L2 requirements added by the retention contract

1. **Automatic purge:** rows with `deleted_at` older than 3 years are deleted. A 3-year window is only reached in 2029, so no row can be affected before then; the purge still ships in L2 and is covered by tests (time-shifted rows). Trigger: to be fixed at L2 (candidate: run the purge opportunistically inside Founder lifecycle / dashboard requests and inside each account deletion — no cron dependency on ConoHa WING).
2. **Churn over the window:** metrics can only look back up to 3 years; cohorts older than that lose their deleted members. Founder UI states the window.
3. **Erasure on request:** Founder email lookup (server-side HMAC, input not stored or logged) + "erase this history row" action, Founder only.
4. **Fail closed** (decided): missing HMAC key or history table → the account deletion does not run (500, retry allowed).

---

## 4. Remaining review notes (not blocking the approval of this draft)

1. **Classification:** a keyed HMAC of the email can be re-matched by us, so the record is treated as pseudonymized personal data (GDPR) / personal information (APPI), not anonymous data — the draft is written on that basis.
2. **Legal basis:** legitimate interests for EEA / UK (minimal fields, no email, 3-year limit, erasure on request).
3. **Notice to existing users:** registration is still closed; current production users were admin-created and have no consent rows. Updating "Last updated" + version is the planned notice.
4. **Existing gap (not changed by this draft):** the Policy does not mention that anonymized feedback text, emails already sent to support, and server logs / backups for a limited period remain after deletion (STEP 2 already says so). Separate decision.

---

## 5. Not in this draft

- Lifecycle schema, HMAC key provisioning, delete / registration integration, Founder UI (L2 / L3).
- Stripe / paid deletion wording (Phase 3B BLOCKED).
- Exact plan timeline (separate task).
