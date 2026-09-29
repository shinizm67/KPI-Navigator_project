<?php
/**
 * Founder Admin — Deleted Accounts (account lifecycle history)
 * No raw email is stored or shown; lookup matches by HMAC on the server.
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
  <title>Deleted Accounts | KPN Founder Console</title>
  <link rel="stylesheet" href="../admin.css?v=20260929-l3">
</head>
<body class="admin-page" data-admin-page="deleted">
  <div class="admin-shell">
    <header class="admin-header">
      <h1 class="admin-title">Deleted Accounts</h1>
      <nav class="admin-nav">
        <a href="../">Dashboard</a>
        <a href="../users/">Users</a>
        <a class="active" href="./">Deleted Accounts</a>
      </nav>
    </header>
    <p class="admin-meta">Signed in as <?php echo $email; ?> · raw email is never stored · rows are purged automatically 3 years after deletion</p>
    <div id="admin-error" class="err" hidden></div>
    <form id="lc-lookup-form" class="lookup-box" autocomplete="off">
      <label class="rel-label" for="lc-lookup-email">Email lookup (erasure request)</label>
      <div class="lookup-row">
        <input id="lc-lookup-email" class="admin-input" type="email" name="lc-lookup" autocomplete="off" spellcheck="false" placeholder="name@example.com">
        <button type="submit" class="btn-admin">Lookup</button>
        <button type="button" class="btn-admin btn-muted" id="lc-lookup-clear" hidden>Show All</button>
      </div>
      <p class="actions-note">The email is matched on the server and is not saved. It is cleared from this field after lookup.</p>
      <div id="lc-lookup-msg" class="actions-msg" hidden></div>
    </form>
    <div id="lc-status" class="admin-meta"></div>
    <div class="table-wrap">
      <table class="admin-table admin-table-static">
        <thead>
          <tr>
            <th>Previous User ID</th>
            <th>Created</th>
            <th>Deleted</th>
            <th>Lifetime</th>
            <th>Plan at Deletion</th>
            <th>Kind</th>
            <th>Origin</th>
            <th>Cleanup Status</th>
            <th>Returned</th>
            <th>Return Count</th>
            <th>Exclude from Metrics</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody id="lc-tbody"></tbody>
      </table>
    </div>
  </div>
  <script src="../../js/kpi-auth-client.js?v=20260919-2"></script>
  <script src="../admin.js?v=20260929-l3"></script>
</body>
</html>
