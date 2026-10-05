-- Widen Stripe external identifiers. Additive only.
-- Does not recreate tables, drop rows, or change kpi_users.plan.
-- Stripe object IDs are not capped at 64 characters. A sandbox
-- Checkout Session ID is already 66 characters.
-- Do not run this against production.

ALTER TABLE kpi_stripe_subscriptions
  MODIFY stripe_customer_id VARCHAR(255) NULL,
  MODIFY stripe_subscription_id VARCHAR(255) NULL,
  MODIFY stripe_price_id VARCHAR(255) NULL,
  MODIFY checkout_session_id VARCHAR(255) NULL,
  MODIFY last_event_id VARCHAR(255) NULL;

ALTER TABLE kpi_stripe_events
  MODIFY event_id VARCHAR(255) NOT NULL;
