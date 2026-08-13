-- KPI Pilot Phase B4-T2 schema (MySQL / MariaDB)
-- Apply once on local or Lolipop DB, then set storageDriver=mysql in config.local.php

CREATE TABLE IF NOT EXISTS kpi_users (
  user_id VARCHAR(64) NOT NULL,
  email VARCHAR(255) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  plan VARCHAR(16) NOT NULL DEFAULT 'basic',
  disabled TINYINT(1) NOT NULL DEFAULT 0,
  plan_updated_at DATETIME NULL,
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL,
  PRIMARY KEY (user_id),
  UNIQUE KEY uq_kpi_users_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Existing DBs created before disabled existed:
-- ALTER TABLE kpi_users ADD COLUMN disabled TINYINT(1) NOT NULL DEFAULT 0 AFTER plan;

CREATE TABLE IF NOT EXISTS kpi_store (
  user_id VARCHAR(64) NOT NULL,
  store_json LONGTEXT NULL,
  annual_nav_json LONGTEXT NULL,
  pl_json LONGTEXT NULL,
  updated_at DATETIME NULL,
  PRIMARY KEY (user_id),
  CONSTRAINT fk_kpi_store_user
    FOREIGN KEY (user_id) REFERENCES kpi_users (user_id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
