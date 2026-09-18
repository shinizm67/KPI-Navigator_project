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
