<?php
/**
 * Phase A Store API — copy to config.local.php and set token.
 * config.local.php is gitignored.
 */
return [
    // Local verification only. Production stays false. When true, the API refuses
    // non-loopback DB / FTP / URL hosts and does not call mail().
    'localTestMode' => false,
    'localDataRoot' => '',
    // Shared secret for X-KPI-Store-Token (legacy Phase A; storeAuthMode=token|dual only)
    'token' => 'dev-change-me',
    // Legacy single-user id when storeAuthMode=token|dual without session
    'userId' => 'default',
    // session (default) | token (Phase A only) | dual (session first, else token)
    'storeAuthMode' => 'session',
    // Allow browser calls from same site / local tools
    'corsOrigin' => '*',
    // B3 Entitlement
    'defaultPlan' => 'basic',       // new registrations (when registrationEnabled)
    'legacyPlan' => 'pro',          // users created before plan field
    'allowSelfPlanChange' => true,  // set false on production
    // Public self-serve signup (POST /auth/register.php). Keep false until billing is ready.
    // Production: false. Admin create-user is independent and ignores this flag.
    'registrationEnabled' => false,
    // Founder Super Admin bootstrap emails (optional). Prefer DB role=founder_superadmin.
    // Never list full_authorized / trial accounts here unless intentional.
    'founderSuperAdminEmails' => [],
    'planAdminToken' => 'dev-plan-admin-change-me',
    'tokenModePlan' => 'pro',
    // B4-T1 store backups
    'backupEnabled' => true,
    'backupKeep' => 10,
    // B4-T2: keep 'file' until MySQL is ready; then 'mysql'
    'storageDriver' => 'file',
    'dbHost' => '127.0.0.1',
    'dbPort' => 3306,
    'dbName' => '',
    'dbUser' => '',
    'dbPass' => '',
    'dbCharset' => 'utf8mb4',
    // Feedback / survey mail (gear → ご意見・リクエスト)
    'supportEmail' => 'support@forge-laboratory.com',
    'supportFrom' => 'support@forge-laboratory.com',
    // Password reset (Forgot Password). Empty baseUrl → production default.
    'passwordResetTtlMinutes' => 30,
    'passwordResetCooldownSeconds' => 120,
    'passwordResetBaseUrl' => 'https://forge-laboratory.com/kpi-navigator',
    // Account Lifecycle History: HMAC key for the email matching value (random, >= 32 chars; never commit it; keep a
    // copy outside the server — losing it only breaks return detection). Empty = account deletion refuses to run.
    // Rotation: move the old key to lifecycleHmacPreviousKeys [id => key] so earlier rows still match.
    'lifecycleHmacKeyId' => 'k1',
    'lifecycleHmacKey' => '',
    'lifecycleHmacPreviousKeys' => [],
    // Marketing unsubscribe token only (link HMAC). Random, >= 32 chars. Never commit the value.
    // Production: set in config.local.php before deploy. Empty here. Do not auto-generate on production.
    'marketingTokenSecret' => '',
    // Marketing evidence match_key only. Separate from marketingTokenSecret and from lifecycleHmacKey.
    // First key id is k1. Rotation: keep the old secret in marketingEvidencePreviousSecrets [id => secret].
    'marketingEvidenceKeyId' => 'k1',
    'marketingEvidenceSecret' => '',
    'marketingEvidencePreviousSecrets' => [],
    // Stripe mode. test or live. Omitted means test. Do not infer live from the host.
    // Production sets STRIPE_MODE=live only after live Prices, a live webhook, and an HTTPS base exist.
    // A live key in test mode, or a test key in live mode, is rejected. Missing key fails closed.
    'stripeMode' => 'test',
    // Secrets stay empty in this file. Test: STRIPE_SECRET_KEY or stripeSecretKey (sk_test_ or rk_test_).
    // Live: the same key name, with sk_live_ or rk_live_, and only while stripeMode is live.
    'stripeSecretKey' => '',
    // Test webhook signing secret. Live mode ignores this and requires stripeWebhookSecretLive.
    // STRIPE_WEBHOOK_SECRET / STRIPE_WEBHOOK_SECRET_LIVE. The two values must differ.
    'stripeWebhookSecret' => '',
    'stripeWebhookSecretLive' => '',
    // Price IDs. Saved business country selects the region. Profile currency does not.
    // JP uses the Japan Prices. Any other, missing, or free-text country uses GLOBAL USD.
    // The four values below are Sandbox defaults and apply only while stripeMode is test.
    // Live mode ignores them. Set live Price IDs with the same keys or
    // STRIPE_PRICE_BASIC / STRIPE_PRICE_PRO / STRIPE_PRICE_BASIC_JP / STRIPE_PRICE_PRO_JP.
    'stripePriceBasic' => 'price_1UN9VpKFNH29caO9yLytJKTw',
    'stripePricePro' => 'price_1UN9k2KFNH29caO9pCLbK7xS',
    'stripePriceBasicJp' => 'price_1UNWRgKFNH29caO9kzKcLf3x',
    'stripePriceProJp' => 'price_1UNWRhKFNH29caO9NXixShH5',
    // Checkout and portal return origin. Test mode allows only localhost / 127.0.0.1.
    // Live mode requires https and a forge-laboratory.com host. Empty derives from the request,
    // then the same rule rejects it. The browser cannot supply this URL.
    'publicBaseUrl' => '',
];
