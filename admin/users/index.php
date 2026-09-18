<?php
/**
 * Founder Admin — Users Table
 */
require __DIR__ . '/../../api/v1/_admin.php';
require_once __DIR__ . '/../../api/v1/_admin_store.php';

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
  <title>Users | KPN Founder Console</title>
  <link rel="stylesheet" href="../admin.css">
</head>
<body class="admin-page" data-admin-page="users">
  <div class="admin-shell">
    <header class="admin-header">
      <h1 class="admin-title">Users</h1>
      <nav class="admin-nav">
        <a href="../">Dashboard</a>
        <a class="active" href="./">Users</a>
      </nav>
    </header>
    <p class="admin-meta">Signed in as <?php echo $email; ?> · row click opens detail</p>
    <div id="admin-error" class="err" hidden></div>
    <div class="table-wrap">
      <table class="admin-table">
        <thead>
          <tr>
            <th>User ID</th>
            <th>Email</th>
            <th>Plan</th>
            <th>Plan Changed At</th>
            <th>Created At</th>
            <th>Last Login</th>
            <th>Related</th>
            <th>Business Name</th>
            <th>Company Name</th>
            <th>Business Type</th>
            <th>Genre</th>
            <th>Language</th>
            <th>Country</th>
            <th>State / Region</th>
            <th>City</th>
            <th>Currency</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody id="users-tbody"></tbody>
      </table>
    </div>
  </div>
  <script src="../../js/kpi-auth-client.js?v=20260919-2"></script>
  <script src="../admin.js"></script>
</body>
</html>
