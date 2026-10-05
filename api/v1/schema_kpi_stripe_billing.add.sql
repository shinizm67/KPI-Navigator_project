-- Stripe Sandbox billing (additive). Apply once on a local/sandbox MySQL database.
-- Does not add a second plan column. kpi_users.plan stays the entitlement field.
-- Webhooks update that field only after signature verification.
-- Do not run this against production.

CREATE TABLE IF NOT EXISTS kpi_stripe_subscriptions (
  user_id VARCHAR(64) NOT NULL,
  stripe_customer_id VARCHAR(255) NULL,
  stripe_subscription_id VARCHAR(255) NULL,
  stripe_price_id VARCHAR(255) NULL,
  subscription_status VARCHAR(32) NULL,
  cancel_at_period_end TINYINT(1) NOT NULL DEFAULT 0,
  current_period_end DATETIME NULL,
  entitlement_granted TINYINT(1) NOT NULL DEFAULT 0,
  checkout_session_id VARCHAR(255) NULL,
  last_invoice_status VARCHAR(32) NULL,
  last_event_id VARCHAR(255) NULL,
  updated_at DATETIME NOT NULL,
  PRIMARY KEY (user_id),
  UNIQUE KEY uq_kpi_stripe_customer (stripe_customer_id),
  UNIQUE KEY uq_kpi_stripe_subscription (stripe_subscription_id),
  CONSTRAINT fk_kpi_stripe_sub_user
    FOREIGN KEY (user_id) REFERENCES kpi_users (user_id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS kpi_stripe_events (
  event_id VARCHAR(255) NOT NULL,
  event_type VARCHAR(64) NOT NULL,
  processed_at DATETIME NOT NULL,
  PRIMARY KEY (event_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Rollback (manual, sandbox only):
-- DROP TABLE IF EXISTS kpi_stripe_events;
-- DROP TABLE IF EXISTS kpi_stripe_subscriptions;
