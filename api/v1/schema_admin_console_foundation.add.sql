-- Admin Console Foundation (additive migration)
-- Apply once on MySQL/MariaDB (phpMyAdmin). Existing users kept.
-- Does NOT invent historical plan rows.

-- 1) kpi_users: role / last_login / parent
ALTER TABLE kpi_users
  ADD COLUMN role VARCHAR(32) NOT NULL DEFAULT 'user' AFTER disabled,
  ADD COLUMN last_login_at DATETIME NULL DEFAULT NULL AFTER updated_at,
  ADD COLUMN parent_user_id VARCHAR(64) NULL DEFAULT NULL AFTER last_login_at;

ALTER TABLE kpi_users ADD INDEX idx_kpi_users_role (role);
ALTER TABLE kpi_users ADD INDEX idx_kpi_users_parent (parent_user_id);
ALTER TABLE kpi_users ADD INDEX idx_kpi_users_created (created_at);
ALTER TABLE kpi_users ADD INDEX idx_kpi_users_last_login (last_login_at);

-- 2) Plan history (append-only)
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

-- 3) Server-side profile
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

-- Bootstrap Founder (EDIT then run once; never auto-promotes trial accounts):
-- UPDATE kpi_users SET role = 'founder_superadmin' WHERE email = 'your-founder@example.com' LIMIT 1;

-- Rollback (manual):
-- DROP TABLE IF EXISTS kpi_user_profiles;
-- DROP TABLE IF EXISTS kpi_plan_history;
-- ALTER TABLE kpi_users DROP COLUMN parent_user_id, DROP COLUMN last_login_at, DROP COLUMN role;
