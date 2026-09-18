<?php
/**
 * Founder Admin — User Detail
 */
require __DIR__ . '/../../../api/v1/_admin.php';
require_once __DIR__ . '/../../../api/v1/_admin_store.php';

$cfg = kpi_v1_load_config();
kpi_v1_auth_boot($cfg);
$adminUser = kpi_v1_admin_require_founder_page($cfg);
$email = htmlspecialchars((string) ($adminUser['email'] ?? ''), ENT_QUOTES, 'UTF-8');
$id = isset($_GET['id']) ? htmlspecialchars((string) $_GET['id'], ENT_QUOTES, 'UTF-8') : '';
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>User Detail | KPN Founder Console</title>
  <link rel="stylesheet" href="../../admin.css">
</head>
<body class="admin-page" data-admin-page="detail">
  <div class="admin-shell">
    <header class="admin-header">
      <h1 class="admin-title">User Detail</h1>
      <nav class="admin-nav">
        <a href="../../">Dashboard</a>
        <a href="../">Users</a>
        <a class="active" href="./?id=<?php echo rawurlencode($id); ?>">Detail</a>
      </nav>
    </header>
    <p class="admin-meta">Signed in as <?php echo $email; ?></p>
    <div id="admin-error" class="err" hidden></div>
    <div id="detail-root"></div>
  </div>
  <script src="../../../js/kpi-auth-client.js"></script>
  <script src="../../admin.js"></script>
</body>
</html>
