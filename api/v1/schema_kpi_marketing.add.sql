-- Lifecycle Segmentation + Marketing Opt-in (BR-LAUNCH-09 Extension M2; additive migration)
-- Contract: docs/br-launch-09-marketing-m1-draft.md (D1–D6 frozen 2026-09-29).
-- Apply once on MySQL / MariaDB BEFORE deploying the code that uses it. Existing rows are not changed; no backfill.
--
-- kpi_marketing_subscribers: one row per normalized email, created only on explicit opt-in.
--   No FK (a "keep after delete" row outlives the account). Never stores password / business data / IP / UA /
--   lifecycle id / HMAC. The unsubscribe token itself is never stored: nonce + sha256(token) only
--   (token = HMAC(server secret, nonce)).
--   Unsubscribed rows are deleted at once when no marketing mail was ever sent; otherwise kept as evidence only
--   until last_marketing_sent_at + 3 years (retain_until), never mailed again (api/v1/_marketing.php).
-- kpi_marketing_consent_events: append-only consent evidence of a subscriber row; deleted together with it.
-- kpi_account_deletions: segment snapshot at deletion (coded values only). Existing rows stay NULL (= Unknown).

CREATE TABLE IF NOT EXISTS kpi_marketing_subscribers (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  normalized_email VARCHAR(255) NOT NULL,
  status VARCHAR(16) NOT NULL,
  locale VARCHAR(8) NOT NULL,
  account_user_id VARCHAR(64) NULL DEFAULT NULL,
  consent_at DATETIME NULL DEFAULT NULL,
  consent_source VARCHAR(32) NULL DEFAULT NULL,
  consent_text_version VARCHAR(32) NULL DEFAULT NULL,
  privacy_version_at_consent VARCHAR(32) NULL DEFAULT NULL,
  unsubscribed_at DATETIME NULL DEFAULT NULL,
  unsubscribe_source VARCHAR(32) NULL DEFAULT NULL,
  last_marketing_sent_at DATETIME NULL DEFAULT NULL,
  unsub_token_nonce CHAR(32) NULL DEFAULT NULL,
  unsub_token_hash CHAR(64) NULL DEFAULT NULL,
  retain_until DATETIME NULL DEFAULT NULL,
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_kpi_marketing_email (normalized_email),
  UNIQUE KEY uq_kpi_marketing_token (unsub_token_hash),
  KEY idx_kpi_marketing_status (status),
  KEY idx_kpi_marketing_account (account_user_id),
  KEY idx_kpi_marketing_retain (retain_until)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS kpi_marketing_consent_events (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  subscriber_id BIGINT UNSIGNED NOT NULL,
  event VARCHAR(24) NOT NULL,
  source VARCHAR(32) NOT NULL,
  consent_text_version VARCHAR(32) NULL DEFAULT NULL,
  privacy_version VARCHAR(32) NULL DEFAULT NULL,
  locale VARCHAR(8) NULL DEFAULT NULL,
  occurred_at DATETIME NOT NULL,
  PRIMARY KEY (id),
  KEY idx_kpi_marketing_events_sub (subscriber_id, occurred_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Run once. MySQL 8 has no ADD COLUMN IF NOT EXISTS: the rollout runner checks information_schema first.
ALTER TABLE kpi_account_deletions
  ADD COLUMN seg_country VARCHAR(8) NULL DEFAULT NULL,
  ADD COLUMN seg_business_type VARCHAR(32) NULL DEFAULT NULL,
  ADD COLUMN seg_currency VARCHAR(8) NULL DEFAULT NULL;

-- Rollback (manual; erases all marketing subscribers / evidence and the segment snapshots):
-- DROP TABLE IF EXISTS kpi_marketing_consent_events;
-- DROP TABLE IF EXISTS kpi_marketing_subscribers;
-- ALTER TABLE kpi_account_deletions DROP COLUMN seg_country, DROP COLUMN seg_business_type, DROP COLUMN seg_currency;
