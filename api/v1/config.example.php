<?php
/**
 * Phase A Store API — copy to config.local.php and set token.
 * config.local.php is gitignored.
 */
return [
    // Shared secret for X-KPI-Store-Token (legacy Phase A; storeAuthMode=token|dual only)
    'token' => 'dev-change-me',
    // Legacy single-user id when storeAuthMode=token|dual without session
    'userId' => 'default',
    // session (default) | token (Phase A only) | dual (session first, else token)
    'storeAuthMode' => 'session',
    // Allow browser calls from same site / local tools
    'corsOrigin' => '*',
    // B3 Entitlement
    'defaultPlan' => 'basic',       // new registrations
    'legacyPlan' => 'pro',          // users created before plan field
    'allowSelfPlanChange' => true,  // set false on production
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
];
