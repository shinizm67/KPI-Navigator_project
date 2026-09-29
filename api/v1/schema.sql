-- KPI Pilot Phase B4-T2 schema (MySQL / MariaDB)
-- Apply once on local or Lolipop DB, then set storageDriver=mysql in config.local.php

CREATE TABLE IF NOT EXISTS kpi_users (
  user_id VARCHAR(64) NOT NULL,
  email VARCHAR(255) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  plan VARCHAR(16) NOT NULL DEFAULT 'basic',
  disabled TINYINT(1) NOT NULL DEFAULT 0,
  role VARCHAR(32) NOT NULL DEFAULT 'user',
  plan_updated_at DATETIME NULL,
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL,
  last_login_at DATETIME NULL,
  parent_user_id VARCHAR(64) NULL,
  PRIMARY KEY (user_id),
  UNIQUE KEY uq_kpi_users_email (email),
  KEY idx_kpi_users_role (role),
  KEY idx_kpi_users_parent (parent_user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Existing DBs created before disabled existed:
-- ALTER TABLE kpi_users ADD COLUMN disabled TINYINT(1) NOT NULL DEFAULT 0 AFTER plan;
-- Admin Console Foundation: see schema_admin_console_foundation.add.sql

CREATE TABLE IF NOT EXISTS kpi_store (
  user_id VARCHAR(64) NOT NULL,
  store_json LONGTEXT NULL,
  annual_nav_json LONGTEXT NULL,
  pl_json LONGTEXT NULL,
  updated_at DATETIME NULL,
  revision BIGINT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (user_id),
  CONSTRAINT fk_kpi_store_user
    FOREIGN KEY (user_id) REFERENCES kpi_users (user_id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 段階2: 日ファクト行。既存 DB は schema_kpi_daily_facts.add.sql を phpMyAdmin で1回。
-- kpi_store.store_json は残す（切戻し）。
CREATE TABLE IF NOT EXISTS kpi_daily_facts (
  user_id VARCHAR(64) NOT NULL,
  iso DATE NOT NULL,
  sales DECIMAL(15,2) NOT NULL DEFAULT 0,
  business_day TINYINT(1) NOT NULL DEFAULT 0,
  daily_target DECIMAL(15,2) NULL,
  mtd_actual DECIMAL(15,2) NOT NULL DEFAULT 0,
  mtd_target DECIMAL(15,2) NULL,
  ytd_actual DECIMAL(15,2) NOT NULL DEFAULT 0,
  ytd_target DECIMAL(15,2) NULL,
  updated_at DATETIME NOT NULL,
  PRIMARY KEY (user_id, iso),
  CONSTRAINT fk_kpi_daily_facts_user
    FOREIGN KEY (user_id) REFERENCES kpi_users (user_id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- snapshot-store 入力正本化: Daily Sales / Business Day の行正本。
-- 既存 DB は schema_kpi_daily_inputs.add.sql を phpMyAdmin で1回。
CREATE TABLE IF NOT EXISTS kpi_daily_inputs (
  user_id VARCHAR(64) NOT NULL,
  iso DATE NOT NULL,
  sales DECIMAL(15,2) NOT NULL DEFAULT 0,
  business_day TINYINT(1) NULL DEFAULT NULL,
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL,
  PRIMARY KEY (user_id, iso),
  KEY idx_kpi_daily_inputs_user_updated (user_id, updated_at),
  CONSTRAINT fk_kpi_daily_inputs_user
    FOREIGN KEY (user_id) REFERENCES kpi_users (user_id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS kpi_plan_history (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id VARCHAR(64) NOT NULL,
  old_plan VARCHAR(16) NULL,
  new_plan VARCHAR(16) NOT NULL,
  changed_at DATETIME NOT NULL,
  changed_by VARCHAR(64) NULL,
  source VARCHAR(32) NOT NULL DEFAULT 'system',
  PRIMARY KEY (id),
  KEY idx_kpi_plan_history_user_changed (user_id, changed_at),
  CONSTRAINT fk_kpi_plan_history_user
    FOREIGN KEY (user_id) REFERENCES kpi_users (user_id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS kpi_user_profiles (
  user_id VARCHAR(64) NOT NULL,
  business_name VARCHAR(255) NULL,
  company_name VARCHAR(255) NULL,
  business_type VARCHAR(64) NULL,
  genre VARCHAR(255) NULL,
  locale VARCHAR(32) NULL,
  country VARCHAR(128) NULL,
  state_region VARCHAR(128) NULL,
  city VARCHAR(128) NULL,
  currency VARCHAR(16) NULL,
  updated_at DATETIME NOT NULL,
  PRIMARY KEY (user_id),
  CONSTRAINT fk_kpi_user_profiles_user
    FOREIGN KEY (user_id) REFERENCES kpi_users (user_id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Password reset: existing DBs use schema_password_reset.add.sql once.
CREATE TABLE IF NOT EXISTS kpi_password_reset_tokens (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id VARCHAR(64) NOT NULL,
  token_hash CHAR(64) NOT NULL,
  expires_at DATETIME NOT NULL,
  used_at DATETIME NULL DEFAULT NULL,
  created_at DATETIME NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_kpi_password_reset_token_hash (token_hash),
  KEY idx_kpi_password_reset_user (user_id),
  KEY idx_kpi_password_reset_expires (expires_at),
  CONSTRAINT fk_kpi_password_reset_user
    FOREIGN KEY (user_id) REFERENCES kpi_users (user_id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Account Lifecycle History: existing DBs use schema_kpi_account_lifecycle.add.sql once.
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
  seg_country VARCHAR(8) NULL DEFAULT NULL,
  seg_business_type VARCHAR(32) NULL DEFAULT NULL,
  seg_currency VARCHAR(8) NULL DEFAULT NULL,
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

-- Marketing opt-in (no FK; rows can outlive the account): existing DBs use schema_kpi_marketing.add.sql once.
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

-- Legal consent (append-only): existing DBs use schema_kpi_user_consents.add.sql once.
CREATE TABLE IF NOT EXISTS kpi_user_consents (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id VARCHAR(64) NOT NULL,
  terms_version VARCHAR(32) NOT NULL,
  privacy_version VARCHAR(32) NOT NULL,
  accepted_at DATETIME NOT NULL,
  source VARCHAR(32) NOT NULL,
  PRIMARY KEY (id),
  KEY idx_kpi_user_consents_user_accepted (user_id, accepted_at),
  CONSTRAINT fk_kpi_user_consents_user
    FOREIGN KEY (user_id) REFERENCES kpi_users (user_id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
