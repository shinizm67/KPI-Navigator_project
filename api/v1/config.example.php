<?php
/**
 * Phase A Store API — copy to config.local.php and set token.
 * config.local.php is gitignored.
 */
return [
    // Shared secret for X-KPI-Store-Token (change before any real deploy)
    'token' => 'dev-change-me',
    // Single-user id for now
    'userId' => 'default',
    // Allow browser calls from same site / local tools
    'corsOrigin' => '*',
];
