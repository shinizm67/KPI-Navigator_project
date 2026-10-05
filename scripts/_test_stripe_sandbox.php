<?php
/**
 * Stripe Sandbox subscription checks. No live card. No network unless a transport is injected.
 * Fixture keys below are not Stripe credentials.
 */

$root = sys_get_temp_dir() . DIRECTORY_SEPARATOR . 'kpn-stripe-sbx-' . getmypid();
if (!is_dir($root) && !mkdir($root, 0700, true)) {
    fwrite(STDERR, "cannot create temp root\n");
    exit(1);
}

$basicPrice = 'price_1UN9VpKFNH29caO9yLytJKTw';
$proPrice = 'price_1UN9k2KFNH29caO9pCLbK7xS';
$fixtureSecret = 'sk_test_fixture_only_not_real';
$fixtureWebhook = 'whsec_fixture_only_not_real';

$configPath = $root . DIRECTORY_SEPARATOR . 'config.php';
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
    'stripeWebhookSecret' => $fixtureWebhook,
    'stripePriceBasic' => $basicPrice,
    'stripePricePro' => $proPrice,
    'token' => 'test-token',
    'planAdminToken' => 'test-plan-token',
    'allowSelfPlanChange' => false,
    'registrationEnabled' => false,
];
file_put_contents($configPath, "<?php\nreturn " . var_export($config, true) . ";\n");
putenv('KPI_V1_CONFIG=' . $configPath);

require dirname(__DIR__) . '/api/v1/_stripe.php';

$failures = [];

function check($name, $ok, $detail = '')
{
    global $failures;
    if ($ok) {
        echo "PASS\t{$name}\n";
        return;
    }
    $failures[] = $name;
    echo "FAIL\t{$name}\t{$detail}\n";
}

function make_user($id, $plan)
{
    $user = [
        'userId' => $id,
        'email' => $id . '@example.com',
        'passwordHash' => 'not-a-login-hash',
        'plan' => $plan,
        'disabled' => false,
        'role' => 'user',
        'createdAt' => gmdate('c'),
    ];
    kpi_v1_auth_write_user($user);
    return kpi_v1_auth_read_user($id);
}

function history_count($userId)
{
    $path = kpi_v1_file_data_root() . '/plan_history.json';
    if (!is_file($path)) {
        return 0;
    }
    $rows = json_decode((string) file_get_contents($path), true);
    if (!is_array($rows)) {
        return 0;
    }
    $n = 0;
    foreach ($rows as $row) {
        if (is_array($row) && isset($row['userId']) && $row['userId'] === $userId && isset($row['source']) && $row['source'] === 'stripe') {
            $n++;
        }
    }
    return $n;
}

function sign_payload($payload, $secret, $timestamp)
{
    $sig = hash_hmac('sha256', $timestamp . '.' . $payload, $secret);
    return 't=' . $timestamp . ',v1=' . $sig;
}

function event_payload($id, $type, array $object)
{
    return json_encode([
        'id' => $id,
        'type' => $type,
        'data' => ['object' => $object],
    ], JSON_UNESCAPED_SLASHES);
}

function local_server()
{
    return ['HTTP_HOST' => '127.0.0.1', 'HTTPS' => '', 'SCRIPT_NAME' => '/kpi-navigator/api/v1/billing/checkout-session.php'];
}

function subscription_object($id, $customer, $status, $priceId, $userId, $cancelAtPeriodEnd, $now)
{
    return [
        'id' => $id,
        'object' => 'subscription',
        'customer' => $customer,
        'status' => $status,
        'cancel_at_period_end' => $cancelAtPeriodEnd,
        'current_period_end' => $now + 2592000,
        'metadata' => ['kpn_user_id' => $userId],
        'items' => [
            'data' => [
                ['quantity' => 1, 'price' => ['id' => $priceId]],
            ],
        ],
    ];
}

$calls = [];
kpi_v1_stripe_set_transport(function ($secret, $path, $body, $idempotency) use (&$calls, $fixtureSecret) {
    if (!is_string($secret) || strpos($secret, 'sk_live_') === 0 || strpos($secret, 'rk_live_') === 0) {
        throw new RuntimeException('refusing non-test transport');
    }
    if ($secret !== $fixtureSecret) {
        throw new RuntimeException('unexpected secret');
    }
    $calls[] = ['path' => $path, 'body' => $body, 'idempotency' => $idempotency];
    return [
        'status' => 200,
        'json' => [
            'id' => 'cs_test_fixture',
            'url' => 'https://checkout.stripe.com/c/pay/cs_test_fixture',
        ],
    ];
});

$cfg = kpi_v1_load_config();
$now = 1760000000;
$server = local_server();
$user = make_user('u_stripesbx01', 'basic');

$beforePlan = kpi_v1_auth_read_user($user['userId'])['plan'];
$basic = kpi_v1_stripe_start_checkout($cfg, $user, ['plan' => 'basic', 'locale' => 'ja'], $server, $now);
check(
    '1 basic checkout session',
    !empty($basic['ok'])
        && $basic['params']['mode'] === 'subscription'
        && $basic['params']['line_items'][0]['price'] === $basicPrice
        && $basic['params']['line_items'][0]['quantity'] === '1'
        && $basic['params']['adaptive_pricing']['enabled'] === 'false'
        && strpos($basic['body'], 'mode=subscription') !== false
        && strpos($basic['body'], 'line_items%5B0%5D%5Bprice%5D=' . $basicPrice) !== false
        && strpos($basic['body'], 'line_items%5B0%5D%5Bquantity%5D=1') !== false
        && strpos($basic['body'], 'adaptive_pricing%5Benabled%5D=false') !== false
        && strpos($basic['body'], '{CHECKOUT_SESSION_ID}') !== false
        && strpos($basic['body'], '%7BCHECKOUT_SESSION_ID%7D') === false
        && strpos($basic['params']['success_url'], 'http://127.0.0.1/kpi-navigator/setting/checkout_success.html?checkout=return&session_id={CHECKOUT_SESSION_ID}') === 0
        && $basic['params']['cancel_url'] === 'http://127.0.0.1/kpi-navigator/setting/checkout_cancel.html'
        && kpi_v1_auth_read_user($user['userId'])['plan'] === $beforePlan
        && count($calls) === 1,
    json_encode(isset($basic['error']) ? $basic['error'] : $basic['params'])
);

$pro = kpi_v1_stripe_start_checkout($cfg, $user, ['plan' => 'pro', 'locale' => 'en'], $server, $now);
check(
    '2 pro checkout session',
    !empty($pro['ok'])
        && $pro['params']['mode'] === 'subscription'
        && $pro['params']['line_items'][0]['price'] === $proPrice
        && $pro['params']['line_items'][0]['quantity'] === '1'
        && strpos($pro['params']['success_url'], '/en/setting/checkout_success.html?checkout=return&session_id={CHECKOUT_SESSION_ID}') !== false
        && $pro['params']['cancel_url'] === 'http://127.0.0.1/kpi-navigator/en/setting/checkout_cancel.html'
        && count($calls) === 2
        && kpi_v1_auth_read_user($user['userId'])['plan'] === 'basic',
    isset($pro['error']) ? $pro['error'] : ''
);

$callCount = count($calls);
$invalid = kpi_v1_stripe_start_checkout($cfg, $user, ['plan' => 'enterprise'], $server, $now);
check(
    '3 invalid plan rejected',
    empty($invalid['ok']) && $invalid['status'] === 400 && $invalid['error'] === 'invalid_plan' && count($calls) === $callCount,
    isset($invalid['error']) ? $invalid['error'] : ''
);

$priced = kpi_v1_stripe_start_checkout($cfg, $user, ['plan' => 'pro', 'priceId' => $basicPrice], $server, $now);
check(
    '3b client price rejected',
    empty($priced['ok']) && $priced['status'] === 400 && $priced['error'] === 'client_price_forbidden' && count($calls) === $callCount,
    isset($priced['error']) ? $priced['error'] : ''
);

$anon = kpi_v1_stripe_start_checkout($cfg, null, ['plan' => 'pro'], $server, $now);
check(
    '4 unauthenticated rejected',
    empty($anon['ok']) && $anon['status'] === 401 && $anon['error'] === 'unauthorized' && count($calls) === $callCount,
    isset($anon['error']) ? $anon['error'] : ''
);

$endpoint = (string) file_get_contents(dirname(__DIR__) . '/api/v1/billing/checkout-session.php');
$unauthPos = strpos($endpoint, "error' => 'unauthorized'");
$startPos = strpos($endpoint, 'kpi_v1_stripe_start_checkout');
check('4b endpoint rejects missing session before Stripe', $unauthPos !== false && $startPos !== false && $unauthPos < $startPos);

$liveCfg = $cfg;
$liveCfg['stripeSecretKey'] = 'sk_live_fixture_forbidden';
$live = kpi_v1_stripe_start_checkout($liveCfg, $user, ['plan' => 'pro'], $server, $now);
check('live key refused', empty($live['ok']) && $live['error'] === 'live_key_forbidden' && count($calls) === $callCount);

$returnJs = (string) file_get_contents(dirname(__DIR__) . '/js/kpi-checkout-return.js');
check(
    'success page does not grant from the browser',
    strpos($returnJs, 'set-plan') === false
        && strpos($returnJs, 'setPlan') === false
        && strpos($returnJs, 'session_id') === false
        && strpos($returnJs, 'billing.confirmed') !== false
);

$whServer = ['HTTP_HOST' => '127.0.0.1'];
$paidSession = event_payload('evt_checkout_paid', 'checkout.session.completed', [
    'id' => 'cs_test_paid',
    'object' => 'checkout.session',
    'mode' => 'subscription',
    'payment_status' => 'paid',
    'customer' => 'cus_test_1',
    'subscription' => 'sub_test_pro',
    'client_reference_id' => $user['userId'],
    'metadata' => ['kpn_user_id' => $user['userId']],
]);
$paid = kpi_v1_stripe_handle_webhook($cfg, $paidSession, sign_payload($paidSession, $fixtureWebhook, $now), $whServer, $now);
$statusAfterPaid = kpi_v1_billing_status_payload($cfg, kpi_v1_auth_read_user($user['userId']));
check(
    '5a paid checkout event does not grant by itself',
    !empty($paid['ok'])
        && kpi_v1_auth_read_user($user['userId'])['plan'] === 'basic'
        && empty($statusAfterPaid['billing']['confirmed'])
        && $statusAfterPaid['billing']['status'] === null,
    json_encode($statusAfterPaid)
);

$created = event_payload(
    'evt_sub_created',
    'customer.subscription.created',
    subscription_object('sub_test_pro', 'cus_test_1', 'active', $proPrice, $user['userId'], false, $now)
);
$createdResult = kpi_v1_stripe_handle_webhook($cfg, $created, sign_payload($created, $fixtureWebhook, $now), $whServer, $now);
$afterCreate = kpi_v1_billing_status_payload($cfg, kpi_v1_auth_read_user($user['userId']));
$stored = kpi_v1_billing_transaction($cfg, function ($store) use ($user) {
    return ['ok' => true, 'billing' => $store->get($user['userId']), 'rollback' => true];
});
check(
    '5 successful subscription webhook',
    !empty($createdResult['ok'])
        && empty($createdResult['duplicate'])
        && kpi_v1_auth_read_user($user['userId'])['plan'] === 'pro'
        && $afterCreate['billing']['confirmed'] === true
        && $afterCreate['billing']['plan'] === 'pro'
        && $afterCreate['billing']['status'] === 'active'
        && is_array($stored['billing'])
        && $stored['billing']['stripeCustomerId'] === 'cus_test_1'
        && $stored['billing']['stripeSubscriptionId'] === 'sub_test_pro'
        && $stored['billing']['stripePriceId'] === $proPrice
        && history_count($user['userId']) === 1,
    json_encode($afterCreate)
);

$againCalls = count($calls);
$second = kpi_v1_stripe_start_checkout($cfg, kpi_v1_auth_read_user($user['userId']), ['plan' => 'basic'], $server, $now);
check(
    '5b second checkout blocked while active',
    empty($second['ok']) && $second['error'] === 'already_subscribed' && count($calls) === $againCalls,
    isset($second['error']) ? $second['error'] : ''
);

$failUser = make_user('u_stripesbx02', 'basic');
$incomplete = event_payload(
    'evt_incomplete',
    'customer.subscription.created',
    subscription_object('sub_test_fail', 'cus_test_fail', 'incomplete', $proPrice, $failUser['userId'], false, $now)
);
$incompleteResult = kpi_v1_stripe_handle_webhook($cfg, $incomplete, sign_payload($incomplete, $fixtureWebhook, $now), $whServer, $now);
$invoice = event_payload('evt_invoice_fail', 'invoice.payment_failed', [
    'id' => 'in_test_fail',
    'object' => 'invoice',
    'customer' => 'cus_test_fail',
    'subscription' => 'sub_test_fail',
    'metadata' => ['kpn_user_id' => $failUser['userId']],
]);
$invoiceResult = kpi_v1_stripe_handle_webhook($cfg, $invoice, sign_payload($invoice, $fixtureWebhook, $now), $whServer, $now);
$failStatus = kpi_v1_billing_status_payload($cfg, kpi_v1_auth_read_user($failUser['userId']));
check(
    '6 payment failure grants nothing',
    !empty($incompleteResult['ok'])
        && !empty($invoiceResult['ok'])
        && kpi_v1_auth_read_user($failUser['userId'])['plan'] === 'basic'
        && empty($failStatus['billing']['confirmed'])
        && $failStatus['billing']['status'] === 'incomplete'
        && $failStatus['billing']['invoiceStatus'] === 'failed'
        && history_count($failUser['userId']) === 0,
    json_encode($failStatus)
);

$unknown = event_payload(
    'evt_unknown_price',
    'customer.subscription.updated',
    subscription_object('sub_test_fail', 'cus_test_fail', 'active', 'price_unknown_not_in_catalog', $failUser['userId'], false, $now)
);
$unknownResult = kpi_v1_stripe_handle_webhook($cfg, $unknown, sign_payload($unknown, $fixtureWebhook, $now), $whServer, $now);
$unknownStatus = kpi_v1_billing_status_payload($cfg, kpi_v1_auth_read_user($failUser['userId']));
check(
    '6b unknown price does not grant',
    !empty($unknownResult['ok'])
        && kpi_v1_auth_read_user($failUser['userId'])['plan'] === 'basic'
        && empty($unknownStatus['billing']['confirmed']),
    json_encode($unknownStatus)
);

$pendingCancel = event_payload(
    'evt_cancel_scheduled',
    'customer.subscription.updated',
    subscription_object('sub_test_pro', 'cus_test_1', 'active', $proPrice, $user['userId'], true, $now)
);
$pendingResult = kpi_v1_stripe_handle_webhook($cfg, $pendingCancel, sign_payload($pendingCancel, $fixtureWebhook, $now), $whServer, $now);
$pendingStatus = kpi_v1_billing_status_payload($cfg, kpi_v1_auth_read_user($user['userId']));
check(
    '7a cancel_at_period_end stays active until Stripe ends it',
    !empty($pendingResult['ok'])
        && kpi_v1_auth_read_user($user['userId'])['plan'] === 'pro'
        && $pendingStatus['billing']['status'] === 'active'
        && $pendingStatus['billing']['cancelAtPeriodEnd'] === true
        && $pendingStatus['billing']['confirmed'] === true,
    json_encode($pendingStatus)
);

$deletedObject = subscription_object('sub_test_pro', 'cus_test_1', 'canceled', $proPrice, $user['userId'], false, $now);
$deleted = event_payload('evt_sub_deleted', 'customer.subscription.deleted', $deletedObject);
$deletedResult = kpi_v1_stripe_handle_webhook($cfg, $deleted, sign_payload($deleted, $fixtureWebhook, $now), $whServer, $now);
$deletedStatus = kpi_v1_billing_status_payload($cfg, kpi_v1_auth_read_user($user['userId']));
check(
    '7 cancellation webhook',
    !empty($deletedResult['ok'])
        && kpi_v1_auth_read_user($user['userId'])['plan'] === 'basic'
        && $deletedStatus['billing']['status'] === 'canceled'
        && empty($deletedStatus['billing']['confirmed']),
    json_encode($deletedStatus)
);

$historyBefore = history_count($user['userId']);
$planBefore = kpi_v1_auth_read_user($user['userId'])['plan'];
$dup = kpi_v1_stripe_handle_webhook($cfg, $deleted, sign_payload($deleted, $fixtureWebhook, $now), $whServer, $now);
$dupStatus = kpi_v1_billing_status_payload($cfg, kpi_v1_auth_read_user($user['userId']));
check(
    '8 duplicate webhook is idempotent',
    !empty($dup['ok'])
        && !empty($dup['duplicate'])
        && kpi_v1_auth_read_user($user['userId'])['plan'] === $planBefore
        && $dupStatus['billing']['status'] === 'canceled'
        && history_count($user['userId']) === $historyBefore,
    json_encode($dup)
);

$bad = kpi_v1_stripe_handle_webhook($cfg, $created, sign_payload($created, 'whsec_wrong', $now), $whServer, $now);
check('bad signature rejected', empty($bad['ok']) && $bad['error'] === 'invalid_signature');

$prod = kpi_v1_stripe_handle_webhook(
    $cfg,
    $created,
    sign_payload($created, $fixtureWebhook, $now),
    ['HTTP_HOST' => 'forge-laboratory.com'],
    $now
);
check(
    'production host refused',
    empty($prod['ok']) && $prod['error'] === 'production_forbidden' && kpi_v1_auth_read_user($user['userId'])['plan'] === 'basic'
);

$zh = kpi_v1_stripe_return_urls('http://127.0.0.1/kpi-navigator', 'zh-tw');
check(
    'zh-tw return urls',
    strpos($zh['success_url'], '/zh-tw/setting/checkout_success.html?checkout=return&session_id={CHECKOUT_SESSION_ID}') !== false
        && strpos($zh['cancel_url'], '/zh-tw/setting/checkout_cancel.html') !== false
);

$longSessionId = 'cs_test_' . str_repeat('A1', 29);
$longUser = make_user('u_stripesbx_longcs', 'basic');
$longPayload = event_payload('evt_long_checkout', 'checkout.session.completed', [
    'id' => $longSessionId,
    'object' => 'checkout.session',
    'mode' => 'subscription',
    'payment_status' => 'paid',
    'customer' => 'cus_test_long',
    'subscription' => 'sub_test_long',
    'client_reference_id' => $longUser['userId'],
    'metadata' => ['kpn_user_id' => $longUser['userId']],
]);
$longResult = kpi_v1_stripe_handle_webhook($cfg, $longPayload, sign_payload($longPayload, $fixtureWebhook, $now), $whServer, $now);
$longStored = kpi_v1_billing_transaction($cfg, function ($store) use ($longUser) {
    return ['ok' => true, 'billing' => $store->get($longUser['userId']), 'rollback' => true];
});
$schemaBlob = (string) file_get_contents(dirname(__DIR__) . '/api/v1/schema.sql')
    . (string) file_get_contents(dirname(__DIR__) . '/api/v1/schema_kpi_stripe_billing.add.sql')
    . (string) file_get_contents(dirname(__DIR__) . '/api/v1/schema_kpi_stripe_id_width.add.sql');
check(
    'long checkout session id stored without truncation',
    strlen($longSessionId) === 66
        && !empty($longResult['ok'])
        && empty($longResult['duplicate'])
        && kpi_v1_auth_read_user($longUser['userId'])['plan'] === 'basic'
        && is_array($longStored['billing'])
        && $longStored['billing']['checkoutSessionId'] === $longSessionId
        && strlen($longStored['billing']['checkoutSessionId']) === 66
        && strpos($schemaBlob, 'checkout_session_id VARCHAR(255)') !== false
        && strpos($schemaBlob, 'checkout_session_id VARCHAR(64)') === false,
    isset($longResult['error']) ? $longResult['error'] : ''
);

$srcBlob = '';
foreach ([
    'api/v1/_stripe.php',
    'api/v1/_billing_store.php',
    'api/v1/billing/checkout-session.php',
    'api/v1/billing/webhook.php',
    'api/v1/billing/status.php',
    'api/v1/config.example.php',
    'js/kpi-change-plan-page.js',
    'js/kpi-checkout-return.js',
] as $rel) {
    $srcBlob .= (string) file_get_contents(dirname(__DIR__) . '/' . $rel);
}
check(
    'no live key or webhook secret in source',
    preg_match('/sk_live_[A-Za-z0-9]{8,}/', $srcBlob) !== 1
        && preg_match('/sk_test_[A-Za-z0-9]{8,}/', $srcBlob) !== 1
        && preg_match('/whsec_[A-Za-z0-9]{8,}/', $srcBlob) !== 1
        && strpos($srcBlob, $fixtureSecret) === false
);

$authJs = (string) file_get_contents(dirname(__DIR__) . '/js/kpi-auth-client.js');
$returnNow = (string) file_get_contents(dirname(__DIR__) . '/js/kpi-checkout-return.js');
$successFnStart = strpos($authJs, 'function isCheckoutSuccessPage()');
$successFn = $successFnStart === false ? '' : substr($authJs, $successFnStart, 280);
$guardStart = strpos($authJs, 'function handleUnauthorizedSession');
$guardFn = $guardStart === false ? '' : substr($authJs, $guardStart, 220);
$confirmedPos = strpos($returnNow, 'billing.confirmed === true');
$continuePos = strpos($returnNow, 'show(continueEl, true)');
$unauthPos = strpos($returnNow, 'r.status === 401 || r.status === 403');
$loginShowPos = $unauthPos === false ? false : strpos($returnNow, 'show(loginEl, true)', $unauthPos);
$processingPos = strpos($returnNow, '決済結果を確認しています。画面の移動だけでは契約は確定しません。');
check(
    'success return states',
    strpos($successFn, 'checkout_success\\.html') !== false
        && strpos($successFn, 'change_plan.html') === false
        && strpos($guardFn, 'isCheckoutSuccessPage()') !== false
        && strpos($guardFn, 'redirectToLogin()') !== false
        && strpos($returnNow, 'location.replace') === false
        && strpos($returnNow, 'location.href') === false
        && strpos($returnNow, 'set-plan') === false
        && strpos($returnNow, 'setPlan') === false
        && strpos($returnNow, 'お申し込みを受け付けました。') !== false
        && strpos($returnNow, 'Your subscription request was received.') !== false
        && strpos($returnNow, '已收到您的訂閱申請。') !== false
        && $processingPos !== false
        && $unauthPos !== false
        && $loginShowPos !== false
        && $loginShowPos > $unauthPos
        && $confirmedPos !== false
        && $continuePos !== false
        && $continuePos > $confirmedPos
        && strpos($returnNow, 'サブスクリプションを確認しました') !== false
);

$successPages = [
    'setting/checkout_success.html' => 'ログインして続行',
    'en/setting/checkout_success.html' => 'Sign in to continue',
    'zh-tw/setting/checkout_success.html' => '登入以繼續',
];
$successMarkupOk = true;
foreach ($successPages as $rel => $label) {
    $html = (string) file_get_contents(dirname(__DIR__) . '/' . $rel);
    if (strpos($html, 'id="checkout-return-login" hidden') === false
        || strpos($html, 'href="../login/index.html">' . $label) === false
        || strpos($html, 'id="checkout-return-continue" hidden') === false
        || strpos($html, 'href="../app/annual/index.html"') === false) {
        $successMarkupOk = false;
    }
}
check('success pages offer login without claiming confirmation', $successMarkupOk);

$cancelOk = true;
foreach ([
    'setting/checkout_cancel.html' => 'アカウントのプランは変更されていません。',
    'en/setting/checkout_cancel.html' => 'Your account plan was not changed.',
    'zh-tw/setting/checkout_cancel.html' => '帳戶方案沒有變更。',
] as $rel => $sentence) {
    $html = (string) file_get_contents(dirname(__DIR__) . '/' . $rel);
    if (strpos($html, $sentence) === false
        || strpos($html, 'kpi-auth-client.js') !== false
        || strpos($html, 'set-plan') !== false) {
        $cancelOk = false;
    }
}
check('cancel return does not grant or force login', $cancelOk);

echo count($failures) === 0 ? "OK\n" : ("FAILED " . count($failures) . "\n");
exit(count($failures) === 0 ? 0 : 1);
