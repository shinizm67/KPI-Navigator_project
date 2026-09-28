-- Account Lifecycle History (BR-LAUNCH-09 Phase 3A Extension; additive migration)
-- Apply once on MySQL / MariaDB (phpMyAdmin) BEFORE deploying the code that uses it.
-- Existing tables and rows are not changed. No backfill (no self-service deletion happened before this).
--
-- kpi_account_deletions: one minimal row per account deletion. No FK (the account no longer exists).
--   Never stores raw email, password hash, profile, business data, consent contents, IP or UA.
--   Rows are purged automatically 3 years after deleted_at (api/v1/_lifecycle.php).
-- kpi_account_origins: NEW / RETURNED marker (+ exclude_from_metrics) of live accounts; deleted with the account.

CREATE TABLE IF NOT EXISTS kpi_account_deletions (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  lifecycle_id VARCHAR(40) NOT NULL,
  previous_user_id VARCHAR(64) NOT NULL,
  email_hmac CHAR(64) NOT NULL,
  hmac_key_id VARCHAR(16) NOT NULL,
  account_created_at DATETIME NOT NULL,
  deleted_at DATETIME NOT NULL,
  lifetime_days INT UNSIGNED NOT NULL,
  plan_at_deletion VARCHAR(16) NOT NULL,
  role_at_deletion VARCHAR(32) NOT NULL,
  account_kind VARCHAR(16) NOT NULL,
  signup_origin VARCHAR(16) NOT NULL,
  deletion_source VARCHAR(32) NOT NULL DEFAULT 'self_service',
  cleanup_status VARCHAR(16) NOT NULL DEFAULT 'pending',
  cleanup_detail VARCHAR(255) NULL DEFAULT NULL,
  exclude_from_metrics TINYINT(1) NOT NULL DEFAULT 0,
  returned_at DATETIME NULL DEFAULT NULL,
  return_count INT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (id),
  UNIQUE KEY uq_kpi_account_deletions_lifecycle (lifecycle_id),
  UNIQUE KEY uq_kpi_account_deletions_prev_user (previous_user_id),
  KEY idx_kpi_account_deletions_hmac (email_hmac),
  KEY idx_kpi_account_deletions_deleted (deleted_at),
  KEY idx_kpi_account_deletions_created (account_created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS kpi_account_origins (
  user_id VARCHAR(64) NOT NULL,
  origin VARCHAR(16) NOT NULL,
  matched_deletion_id BIGINT UNSIGNED NULL DEFAULT NULL,
  exclude_from_metrics TINYINT(1) NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL,
  PRIMARY KEY (user_id),
  CONSTRAINT fk_kpi_account_origins_user
    FOREIGN KEY (user_id) REFERENCES kpi_users (user_id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Rollback (manual; erases all lifecycle history):
-- DROP TABLE IF EXISTS kpi_account_origins;
-- DROP TABLE IF EXISTS kpi_account_deletions;
