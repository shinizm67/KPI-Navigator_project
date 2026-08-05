<?php
/**
 * POST /api/v1/auth/logout.php
 */

require __DIR__ . '/../_auth.php';

$cfg = kpi_v1_load_config();
kpi_v1_auth_boot($cfg);
kpi_v1_auth_require_post();

kpi_v1_auth_clear_session();
kpi_v1_json_out(200, ['ok' => true]);
