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
    // Stripe Sandbox only. Leave secrets empty here.
    // Set STRIPE_SECRET_KEY / STRIPE_WEBHOOK_SECRET in the environment,
    // or put sk_test_ / whsec_ values in gitignored config.local.php.
    // Live keys (sk_live_ / rk_live_) are refused. Do not commit secrets.
    'stripeSecretKey' => '',
    'stripeWebhookSecret' => '',
    'stripePriceBasic' => 'price_1UN9VpKFNH29caO9yLytJKTw',
    'stripePricePro' => 'price_1UN9k2KFNH29caO9pCLbK7xS',
    // Optional absolute origin for Checkout return URLs, no trailing path.
    // Empty = derive from the current request. Production hosts are refused.
    'publicBaseUrl' => '',
];
