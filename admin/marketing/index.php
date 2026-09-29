<?php
/**
 * Founder Admin — Email Updates (marketing subscribers)
 * Raw email is shown on this page only. Token / hash / secret never.
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
  <title>Email Updates | KPN Founder Console</title>
  <link rel="stylesheet" href="../admin.css?v=20260930-m6">
</head>
<body class="admin-page" data-admin-page="marketing">
  <div class="admin-shell">
    <header class="admin-header">
      <h1 class="admin-title">Email Updates</h1>
      <nav class="admin-nav">
        <a href="../">Dashboard</a>
        <a href="../users/">Users</a>
        <a href="../deleted-accounts/">Deleted Accounts</a>
        <a class="active" href="./">Email Updates</a>
      </nav>
    </header>
    <p class="admin-meta">Signed in as <?php echo $email; ?> · raw email is shown here only · no send function · evidence kept 3 years after the last email</p>
    <div id="admin-error" class="err" hidden></div>
    <div id="mkt-cards" class="cards"></div>
    <p id="mkt-status" class="admin-meta"></p>
    <div id="mkt-msg" class="actions-msg" hidden></div>
    <div class="table-wrap">
      <table class="admin-table admin-table-static">
        <thead>
          <tr>
            <th>Email</th>
            <th>Status</th>
            <th>Locale</th>
            <th>Consent Source</th>
            <th>Consent Time</th>
            <th>Last Email Sent</th>
            <th>Has Account</th>
            <th>Unsubscribed</th>
            <th>Retain Until</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody id="mkt-tbody"></tbody>
      </table>
    </div>
  </div>
  <script src="../../js/kpi-auth-client.js?v=20260919-2"></script>
  <script src="../admin.js?v=20260930-m6"></script>
</body>
</html>
