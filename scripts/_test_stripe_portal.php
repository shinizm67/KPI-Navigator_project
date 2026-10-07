<?php
/**
 * Customer Portal session and the account-delete subscription gate.
 * Fixture keys are not Stripe credentials. No network.
 */

$root = sys_get_temp_dir() . DIRECTORY_SEPARATOR . 'kpn-stripe-portal-' . getmypid() . '-' . bin2hex(random_bytes(4));
if (!mkdir($root, 0700, true)) {
    fwrite(STDERR, "cannot create temp root\n");
    exit(1);
}
$fixtureSecret = 'sk_test_fixture_only_not_real';
$config = [
    'localTestMode' => true,
    'localDataRoot' => $root,
    'storageDriver' => 'file',
    'dbHost' => '127.0.0.1',
    'dbPort' => 3306,
    'dbName' => '',
    'dbUser' => '',
    'dbPass' => '',
    'passwordResetBaseUrl' => 'http://127.0.0.1/kpi-navigator',
    'supportEmail' => 'sandbox@example.com',
    'supportFrom' => 'sandbox@example.com',
    'publicBaseUrl' => 'http://127.0.0.1/kpi-navigator',
    'stripeSecretKey' => $fixtureSecret,
    'stripeWebhookSecret' => 'whsec_fixture_only_not_real',
    'corsOrigin' => 'http://127.0.0.1',
    'registrationEnabled' => false,
    'lifecycleHmacKey' => 'fixture-lifecycle-hmac-key-32chars',
    'lifecycleHmacKeyId' => 'fixture',
];
$configPath = $root . DIRECTORY_SEPARATOR . 'config.php';
file_put_contents($configPath, "<?php\nreturn " . var_export($config, true) . ";\n");
putenv('KPI_V1_CONFIG=' . $configPath);
putenv('STRIPE_SECRET_KEY');
$_ENV['KPI_V1_CONFIG'] = $configPath;

require dirname(__DIR__) . '/api/v1/_stripe.php';
require_once dirname(__DIR__) . '/api/v1/_account_delete.php';

$failed = 0;
function check($name, $ok, $detail = '')
{
    global $failed;
    if ($ok) {
        echo "PASS\t$name\n";
        return;
    }
    $failed++;
    echo "FAIL\t$name" . ($detail !== '' ? "\t$detail" : '') . "\n";
}

$cfg = kpi_v1_load_config();
$_SERVER['REQUEST_METHOD'] = 'POST';
$_SERVER['HTTPS'] = '';
$_SERVER['HTTP_HOST'] = '127.0.0.1';
$_SERVER['SCRIPT_NAME'] = '/kpi-navigator/api/v1/billing/portal-session.php';
kpi_v1_auth_boot($cfg);

function make_user($id, $email)
{
    kpi_v1_auth_write_user([
        'userId' => $id,
        'email' => $email,
        'passwordHash' => password_hash('Abcd123!', PASSWORD_DEFAULT),
        'plan' => 'basic',
        'role' => 'user',
        'disabled' => false,
        'createdAt' => gmdate('c'),
    ]);
    $index = kpi_v1_auth_read_email_index();
    $index[$email] = $id;
    kpi_v1_auth_write_email_index($index);
}

function put_billing($userId, $customer, $subscription, $status, $cancel)
{
    $row = kpi_v1_billing_blank($userId);
    $row['stripeCustomerId'] = $customer;
    $row['stripeSubscriptionId'] = $subscription;
    $row['subscriptionStatus'] = $status;
    $row['cancelAtPeriodEnd'] = $cancel;
    $saved = kpi_v1_billing_transaction(kpi_v1_load_config(), function ($store) use ($row) {
        $store->put($row);
        return ['ok' => true];
    });
    if (empty($saved['ok'])) {
        fwrite(STDERR, "billing put failed\n");
        exit(1);
    }
}

$calls = [];
kpi_v1_stripe_set_transport(function ($secret, $path, $body, $idempotency) use (&$calls, $fixtureSecret) {
    $calls[] = [
        'secret' => $secret,
        'path' => $path,
        'body' => $body,
        'idempotency' => $idempotency,
    ];
    if (strpos($body, 'cus_livemodeother') !== false) {
        return ['status' => 404, 'json' => ['error' => ['code' => 'resource_missing', 'message' => 'hidden']]];
    }
    return [
        'status' => 200,
        'json' => [
            'id' => 'bps_fixture',
            'url' => 'https://billing.stripe.com/p/session/test_fixture',
        ],
    ];
});

$server = [
    'HTTP_HOST' => '127.0.0.1',
    'HTTPS' => '',
    'SCRIPT_NAME' => '/kpi-navigator/api/v1/billing/portal-session.php',
];

make_user('u_portal_a', 'portal-a@example.com');
make_user('u_portal_b', 'portal-b@example.com');
put_billing('u_portal_a', 'cus_serverstored01', 'sub_serverstored01', 'active', false);

$none = kpi_v1_stripe_start_portal($cfg, null, [], $server);
check('1 unauthenticated portal request rejected', $none['status'] === 401 && $none['error'] === 'unauthorized' && $calls === []);

$missing = kpi_v1_stripe_start_portal($cfg, kpi_v1_auth_read_user('u_portal_b'), [], $server);
check('2 user without Stripe customer rejected', $missing['status'] === 409 && $missing['error'] === 'no_stripe_customer' && $calls === []);

$opened = kpi_v1_stripe_start_portal($cfg, kpi_v1_auth_read_user('u_portal_a'), ['locale' => 'ja'], $server);
check(
    '3 portal uses the server-stored customer',
    $opened['ok'] === true
        && isset($calls[0]['body'])
        && strpos($calls[0]['body'], 'customer=' . rawurlencode('cus_serverstored01')) !== false
        && strpos($calls[0]['body'], 'cus_client') === false
);
check(
    '6 portal request is the billing portal with the server return URL',
    isset($calls[0]['path'], $calls[0]['secret'], $opened['url'])
        && $calls[0]['path'] === '/v1/billing_portal/sessions'
        && $calls[0]['secret'] === $fixtureSecret
        && strpos($calls[0]['body'], rawurlencode('http://127.0.0.1/kpi-navigator/setting/change_plan.html')) !== false
        && $opened['url'] === 'https://billing.stripe.com/p/session/test_fixture'
        && strpos(json_encode($opened['url']), 'cus_') === false
);

$beforeClient = count($calls);
$clientCustomer = kpi_v1_stripe_start_portal($cfg, kpi_v1_auth_read_user('u_portal_a'), [
    'customer' => 'cus_clientinjected',
    'locale' => 'ja',
], $server);
check('4 client customer ID rejected', $clientCustomer['status'] === 400 && $clientCustomer['error'] === 'client_billing_forbidden' && count($calls) === $beforeClient);

$clientReturn = kpi_v1_stripe_start_portal($cfg, kpi_v1_auth_read_user('u_portal_a'), [
    'return_url' => 'https://evil.example/steal',
], $server);
check('5 arbitrary return URL rejected', $clientReturn['status'] === 400 && $clientReturn['error'] === 'client_billing_forbidden' && count($calls) === $beforeClient);

$liveCfg = $cfg;
$liveCfg['stripeSecretKey'] = 'sk_live_fixture_only_not_real';
$live = kpi_v1_stripe_start_portal($liveCfg, kpi_v1_auth_read_user('u_portal_a'), [], $server);
check('test customer is not sent with a live key', $live['status'] === 403 && $live['error'] === 'live_key_forbidden' && count($calls) === $beforeClient);

put_billing('u_portal_b', 'cus_livemodeother', null, null, false);
$mode = kpi_v1_stripe_start_portal($cfg, kpi_v1_auth_read_user('u_portal_b'), [], $server);
$modeJson = json_encode($mode);
check(
    'live customer is not opened with the test key',
    $mode['status'] === 409
        && $mode['error'] === 'customer_mode_mismatch'
        && strpos((string) $modeJson, 'cus_livemodeother') === false
        && strpos((string) $modeJson, 'https://billing.stripe.com/') === false
);

$prodCfg = $cfg;
$prodCfg['publicBaseUrl'] = 'https://forge-laboratory.com/kpi-navigator';
$prod = kpi_v1_stripe_start_portal($prodCfg, kpi_v1_auth_read_user('u_portal_a'), [], $server);
check('production host stays forbidden', $prod['status'] === 403 && $prod['error'] === 'production_forbidden');

$status = kpi_v1_billing_status_payload($cfg, kpi_v1_auth_read_user('u_portal_a'));
$statusJson = json_encode($status);
check(
    'status offers the portal without the customer id',
    !empty($status['billing']['portalAvailable'])
        && strpos((string) $statusJson, 'cus_') === false
        && strpos((string) $statusJson, 'stripeCustomerId') === false
);

$prices = kpi_v1_stripe_prices($cfg);
$proPrice = $prices['GLOBAL']['pro'];
$kept = kpi_v1_stripe_apply_subscription($prices, kpi_v1_billing_blank('u_portal_a'), [
    'id' => 'sub_serverstored01',
    'customer' => 'cus_serverstored01',
    'status' => 'active',
    'cancel_at_period_end' => true,
    'items' => ['data' => [['quantity' => 1, 'price' => ['id' => $proPrice]]]],
], false);
$ended = kpi_v1_stripe_apply_subscription($prices, $kept['billing'], [
    'id' => 'sub_serverstored01',
    'customer' => 'cus_serverstored01',
    'status' => 'canceled',
    'cancel_at_period_end' => true,
    'items' => ['data' => [['quantity' => 1, 'price' => ['id' => $proPrice]]]],
], true);
check(
    'cancel at period end keeps Pro until the subscription ends',
    $kept['plan'] === 'pro'
        && !empty($kept['billing']['entitlementGranted'])
        && !empty($kept['billing']['cancelAtPeriodEnd'])
        && $ended['billing']['subscriptionStatus'] === 'canceled'
        && empty($ended['billing']['entitlementGranted'])
        && $ended['plan'] === 'basic'
);

function block_code($userId)
{
    $user = kpi_v1_auth_read_user($userId);
    return kpi_v1_account_delete_reject_reason(kpi_v1_load_config(), $user);
}

$cases = [
    '7 active blocks deletion' => ['active', false],
    '8 trialing blocks deletion' => ['trialing', false],
    '9 past_due blocks deletion' => ['past_due', false],
    '10 unpaid blocks deletion' => ['unpaid', false],
    '11 incomplete blocks deletion' => ['incomplete', false],
    '12 cancel_at_period_end plus active still blocks' => ['active', true],
];
foreach ($cases as $name => $spec) {
    put_billing('u_portal_a', 'cus_serverstored01', 'sub_serverstored01', $spec[0], $spec[1]);
    $code = block_code('u_portal_a');
    $record = kpi_v1_account_delete_user_record(kpi_v1_load_config(), kpi_v1_auth_read_user('u_portal_a'));
    $still = kpi_v1_auth_read_user('u_portal_a');
    check($name, $code === 'active_subscription_exists' && $record === 'active_subscription_exists' && is_array($still), (string) $code . '/' . (string) $record);
}

put_billing('u_portal_a', 'cus_serverstored01', 'sub_serverstored01', 'canceled', true);
$endedCode = block_code('u_portal_a');
$endedExec = kpi_v1_account_delete_execute_locked(kpi_v1_load_config(), 'u_portal_a', null);
check(
    '13 ended subscription does not block deletion',
    $endedCode === null && $endedExec[0] === 403 && $endedExec[1]['error'] === 'delete_intent_required' && is_array(kpi_v1_auth_read_user('u_portal_a'))
);

put_billing('u_portal_b', null, null, null, false);
$clear = kpi_v1_billing_transaction($cfg, function ($store) {
    $blank = kpi_v1_billing_blank('u_portal_clear');
    $store->put($blank);
    return ['ok' => true];
});
make_user('u_portal_clear', 'portal-clear@example.com');
$clearCode = block_code('u_portal_clear');
$clearExec = kpi_v1_account_delete_execute_locked($cfg, 'u_portal_clear', null);
check(
    '14 user without a subscription reaches the existing delete rules',
    $clear['ok'] === true && $clearCode === null && $clearExec[0] === 403 && $clearExec[1]['error'] === 'delete_intent_required'
);

put_billing('u_portal_a', 'cus_serverstored01', 'sub_serverstored01', 'active', true);
put_billing('u_portal_b', null, null, null, false);
$callsBeforeOther = count($calls);
$otherPortal = kpi_v1_stripe_start_portal($cfg, kpi_v1_auth_read_user('u_portal_b'), [], $server);
check(
    '15 another user is not blocked and does not receive the first customer',
    block_code('u_portal_b') === null
        && block_code('u_portal_a') === 'active_subscription_exists'
        && $otherPortal['error'] === 'no_stripe_customer'
        && count($calls) === $callsBeforeOther
);

$founder = kpi_v1_auth_read_user('u_portal_clear');
$founder['role'] = 'founder';
kpi_v1_auth_write_user($founder);
$protected = kpi_v1_account_delete_reject_reason($cfg, kpi_v1_auth_read_user('u_portal_clear'));
check('16 protected role is still rejected', $protected === 'protected_account' && kpi_v1_account_delete_reject_http($protected) === 403);

$portalPhp = file_get_contents(dirname(__DIR__) . '/api/v1/billing/portal-session.php');
check(
    'portal HTTP response returns only the hosted URL',
    strpos($portalPhp, "'url' => \$result['url']") !== false
        && strpos($portalPhp, "\$result['id']") === false
        && strpos($portalPhp, "\$result['params']") === false
);

if ($failed > 0) {
    echo "FAILED $failed\n";
    exit(1);
}
echo "OK\n";
exit(0);
