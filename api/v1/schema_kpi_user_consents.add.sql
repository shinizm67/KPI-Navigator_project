-- Legal consent record (additive migration, BR-LAUNCH-05)
-- Apply once on MySQL/MariaDB (phpMyAdmin) before public registration is reopened.
-- Existing users and tables are unchanged.
-- Append-only: one row per acceptance; re-consent adds a new row, existing rows are never updated.

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

-- Rollback (manual):
-- DROP TABLE IF EXISTS kpi_user_consents;
