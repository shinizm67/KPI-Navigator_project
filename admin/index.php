<?php
/**
 * Founder Admin — Dashboard
 * Server-side founder gate (not client-only).
 */
require __DIR__ . '/../api/v1/_admin.php';
require_once __DIR__ . '/../api/v1/_admin_store.php';

$cfg = kpi_v1_load_config();
kpi_v1_auth_boot($cfg);
$adminUser = kpi_v1_admin_require_founder_page($cfg);
$email = htmlspecialchars((string) ($adminUser['email'] ?? ''), ENT_QUOTES, 'UTF-8');
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Admin Dashboard | KPN Founder Console</title>
  <link rel="stylesheet" href="admin.css">
</head>
<body class="admin-page" data-admin-page="dashboard">
  <div class="admin-shell">
    <header class="admin-header">
      <h1 class="admin-title">KPN Founder Console</h1>
      <nav class="admin-nav">
        <a class="active" href="./">Dashboard</a>
        <a href="users/">Users</a>
      </nav>
    </header>
    <p class="admin-meta">Signed in as <?php echo $email; ?> · Sci-Fi Mode</p>
    <div id="admin-error" class="err" hidden></div>
    <div id="dash-cards" class="cards"></div>
  </div>
  <script src="../js/kpi-auth-client.js"></script>
  <script src="admin.js"></script>
</body>
</html>
