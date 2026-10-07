<?php
/**
 * Stripe test/live mode contract. Fixture keys only. No network.
 */

$root = sys_get_temp_dir() . DIRECTORY_SEPARATOR . 'kpn-stripe-mode-' . getmypid() . '-' . bin2hex(random_bytes(4));
if (!mkdir($root, 0700, true)) {
    fwrite(STDERR, "cannot create temp root\n");
    exit(1);
}

$sandboxBasic = 'price_1UN9VpKFNH29caO9yLytJKTw';
$sandboxPro = 'price_1UN9k2KFNH29caO9pCLbK7xS';
$sandboxBasicJp = 'price_1UNWRgKFNH29caO9kzKcLf3x';
$sandboxProJp = 'price_1UNWRhKFNH29caO9NXixShH5';
$liveBasic = 'price_livebasicusd0001';
$livePro = 'price_liveprousd000001';
$liveBasicJp = 'price_livebasicjpy0001';
$liveProJp = 'price_liveprojpy000001';
$testKey = 'sk_test_fixture_only_not_real';
$liveKey = 'sk_live_fixture_only_not_real';
$testWhsec = 'whsec_fixture_test_only';
$liveWhsec = 'whsec_fixture_live_only';

foreach ([
    'STRIPE_MODE', 'STRIPE_SECRET_KEY', 'STRIPE_WEBHOOK_SECRET', 'STRIPE_WEBHOOK_SECRET_LIVE',
    'STRIPE_PRICE_BASIC', 'STRIPE_PRICE_PRO', 'STRIPE_PRICE_BASIC_JP', 'STRIPE_PRICE_PRO_JP',
    'KPN_PUBLIC_BASE_URL',
] as $envName) {
    putenv($envName);
}

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
    'stripeMode' => 'test',
    'publicBaseUrl' => 'http://127.0.0.1/kpi-navigator',
    'stripeSecretKey' => $testKey,
    'stripeWebhookSecret' => $testWhsec,
    'stripeWebhookSecretLive' => '',
    'token' => 'test-token',
    'planAdminToken' => 'test-plan-token',
    'allowSelfPlanChange' => false,
    'registrationEnabled' => false,
];
$configPath = $root . DIRECTORY_SEPARATOR . 'config.php';
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

function make_user($id)
{
    kpi_v1_auth_write_user([
        'userId' => $id,
        'email' => $id . '@example.com',
        'passwordHash' => 'not-a-login-hash',
        'plan' => 'basic',
        'disabled' => false,
        'role' => 'user',
        'createdAt' => gmdate('c'),
    ]);
    return kpi_v1_auth_read_user($id);
}

function sign_payload($payload, $secret, $timestamp)
{
    $sig = hash_hmac('sha256', $timestamp . '.' . $payload, $secret);
    return 't=' . $timestamp . ',v1=' . $sig;
}

function event_body($id, $livemode)
{
    return json_encode([
        'id' => $id,
        'type' => 'checkout.session.completed',
        'livemode' => $livemode,
        'data' => ['object' => [
            'id' => 'cs_mode_fixture',
            'mode' => 'subscription',
            'client_reference_id' => 'u_modehook',
            'metadata' => ['kpn_user_id' => 'u_modehook'],
        ]],
    ], JSON_UNESCAPED_SLASHES);
}

$script = ['livemode' => false, 'kind' => 'checkout'];
$calls = [];
kpi_v1_stripe_set_transport(function ($secret, $path, $body, $idempotency) use (&$calls, &$script) {
    $calls[] = ['secret' => $secret, 'path' => $path, 'body' => $body];
    if ($script['kind'] === 'missing') {
        return ['status' => 404, 'json' => ['error' => ['code' => 'resource_missing']]];
    }
    $url = $script['kind'] === 'portal'
        ? 'https://billing.stripe.com/p/session/mode_fixture'
        : 'https://checkout.stripe.com/c/pay/cs_mode_fixture';
    return [
        'status' => 200,
        'json' => [
            'id' => $script['kind'] === 'portal' ? 'bps_mode_fixture' : 'cs_mode_fixture',
            'url' => $url,
            'livemode' => $script['livemode'],
        ],
    ];
});

$cfg = kpi_v1_load_config();
$now = 1760000000;
$server = ['HTTP_HOST' => '127.0.0.1', 'HTTPS' => '', 'SCRIPT_NAME' => '/kpi-navigator/api/v1/billing/checkout-session.php'];
$user = make_user('u_modecheckout');
make_user('u_modehook');
make_user('u_modeportal');

$testCheckout = kpi_v1_stripe_start_checkout($cfg, $user, ['plan' => 'basic'], $server, $now);
check(
    '1 test mode accepts a test key',
    !empty($testCheckout['ok']) && $testCheckout['params']['line_items'][0]['price'] === $sandboxBasic && count($calls) === 1
);

$before = count($calls);
$liveKeyCfg = $cfg;
$liveKeyCfg['stripeSecretKey'] = $liveKey;
$rejectedLiveKey = kpi_v1_stripe_start_checkout($liveKeyCfg, $user, ['plan' => 'basic'], $server, $now);
check(
    '2 test mode rejects a live key',
    empty($rejectedLiveKey['ok']) && $rejectedLiveKey['error'] === 'stripe_key_mismatch' && count($calls) === $before
);

$liveCfg = $cfg;
$liveCfg['stripeMode'] = 'live';
$liveCfg['stripeSecretKey'] = $liveKey;
$liveCfg['stripeWebhookSecretLive'] = $liveWhsec;
$liveCfg['stripePriceBasic'] = $liveBasic;
$liveCfg['stripePricePro'] = $livePro;
$liveCfg['stripePriceBasicJp'] = $liveBasicJp;
$liveCfg['stripePriceProJp'] = $liveProJp;
$liveCfg['publicBaseUrl'] = 'https://forge-laboratory.com';
$script['livemode'] = true;
$liveCheckout = kpi_v1_stripe_start_checkout($liveCfg, $user, ['plan' => 'pro'], $server, $now);
check(
    '3 live mode accepts a live key fixture',
    !empty($liveCheckout['ok']) && $liveCheckout['params']['line_items'][0]['price'] === $livePro
);

$script['livemode'] = false;
$before = count($calls);
$liveCfgTestKey = $liveCfg;
$liveCfgTestKey['stripeSecretKey'] = $testKey;
$rejectedTestKey = kpi_v1_stripe_start_checkout($liveCfgTestKey, $user, ['plan' => 'pro'], $server, $now);
check(
    '4 live mode rejects a test key',
    empty($rejectedTestKey['ok']) && $rejectedTestKey['error'] === 'stripe_key_mismatch' && count($calls) === $before
);

$before = count($calls);
$missingPrice = $liveCfg;
$missingPrice['stripePricePro'] = '';
$missing = kpi_v1_stripe_start_checkout($missingPrice, $user, ['plan' => 'pro'], $server, $now);
check(
    '5 live mode with a missing live Price fails closed',
    empty($missing['ok']) && $missing['error'] === 'not_configured' && count($calls) === $before
);

$defaultCfg = $cfg;
unset($defaultCfg['stripePriceBasic'], $defaultCfg['stripePricePro'], $defaultCfg['stripePriceBasicJp'], $defaultCfg['stripePriceProJp']);
$defaults = kpi_v1_stripe_prices($defaultCfg);
check(
    '6 test mode uses the Sandbox Price defaults',
    $defaults['GLOBAL']['basic'] === $sandboxBasic
        && $defaults['GLOBAL']['pro'] === $sandboxPro
        && $defaults['JP']['basic'] === $sandboxBasicJp
        && $defaults['JP']['pro'] === $sandboxProJp
);

$sandboxLive = $liveCfg;
$sandboxLive['stripePriceBasic'] = $sandboxBasic;
$sandboxLive['stripePricePro'] = $sandboxPro;
$sandboxLive['stripePriceBasicJp'] = $sandboxBasicJp;
$sandboxLive['stripePriceProJp'] = $sandboxProJp;
$sandboxPrices = kpi_v1_stripe_prices($sandboxLive);
$before = count($calls);
$sandboxCheckout = kpi_v1_stripe_start_checkout($sandboxLive, $user, ['plan' => 'basic'], $server, $now);
check(
    '7 live mode never uses a Sandbox Price',
    $sandboxPrices['GLOBAL']['basic'] === ''
        && $sandboxPrices['JP']['pro'] === ''
        && empty($sandboxCheckout['ok'])
        && $sandboxCheckout['error'] === 'not_configured'
        && count($calls) === $before
);

$whServer = ['HTTP_HOST' => '127.0.0.1'];
$testEvent = event_body('evt_mode_test_ok', false);
$testHook = kpi_v1_stripe_handle_webhook($cfg, $testEvent, sign_payload($testEvent, $testWhsec, $now), $whServer, $now);
check('8 webhook test event accepted in test mode', !empty($testHook['ok']) && empty($testHook['error']));

$liveEvent = event_body('evt_mode_live_reject', true);
$liveRejected = kpi_v1_stripe_handle_webhook($cfg, $liveEvent, sign_payload($liveEvent, $testWhsec, $now), $whServer, $now);
check(
    '9 webhook live event rejected in test mode',
    empty($liveRejected['ok']) && $liveRejected['error'] === 'stripe_livemode_mismatch'
);

$liveOkEvent = event_body('evt_mode_live_ok', true);
$liveHook = kpi_v1_stripe_handle_webhook($liveCfg, $liveOkEvent, sign_payload($liveOkEvent, $liveWhsec, $now), $whServer, $now);
check('10 webhook live event accepted in live mode', !empty($liveHook['ok']) && empty($liveHook['error']));

$testOnLive = event_body('evt_mode_test_on_live', false);
$testOnLiveResult = kpi_v1_stripe_handle_webhook($liveCfg, $testOnLive, sign_payload($testOnLive, $liveWhsec, $now), $whServer, $now);
$sameSecret = $liveCfg;
$sameSecret['stripeWebhookSecretLive'] = $testWhsec;
$sameSecretEvent = event_body('evt_mode_same_secret', true);
$sameSecretResult = kpi_v1_stripe_handle_webhook($sameSecret, $sameSecretEvent, sign_payload($sameSecretEvent, $testWhsec, $now), $whServer, $now);
check(
    '11 webhook test event rejected in live mode',
    empty($testOnLiveResult['ok']) && $testOnLiveResult['error'] === 'stripe_livemode_mismatch'
        && empty($sameSecretResult['ok']) && $sameSecretResult['error'] === 'not_configured'
);

$localLive = $liveCfg;
$localLive['publicBaseUrl'] = 'http://127.0.0.1/kpi-navigator';
$before = count($calls);
$script['livemode'] = true;
$localRejected = kpi_v1_stripe_start_checkout($localLive, $user, ['plan' => 'basic'], $server, $now);
check(
    '12 live mode rejects a localhost base',
    empty($localRejected['ok']) && $localRejected['error'] === 'return_url_rejected' && count($calls) === $before
);

$httpLive = $liveCfg;
$httpLive['publicBaseUrl'] = 'http://forge-laboratory.com';
$httpRejected = kpi_v1_stripe_start_checkout($httpLive, $user, ['plan' => 'basic'], $server, $now);
check(
    '13 live mode rejects an http URL',
    empty($httpRejected['ok']) && $httpRejected['error'] === 'return_url_rejected' && count($calls) === $before
);

$httpsLive = kpi_v1_stripe_start_checkout($liveCfg, $user, ['plan' => 'basic', 'locale' => 'zh-tw'], $server, $now);
check(
    '14 live mode accepts the HTTPS Forge Laboratory base',
    !empty($httpsLive['ok'])
        && strpos($httpsLive['params']['success_url'], 'https://forge-laboratory.com/zh-tw/setting/checkout_success.html') === 0
);

$loop = kpi_v1_stripe_resolve_base($cfg, $server);
check('15 test mode accepts localhost', !empty($loop['ok']) && strpos($loop['base'], 'http://127.0.0.1') === 0);

$row = kpi_v1_billing_blank('u_modeportal');
$row['stripeCustomerId'] = 'cus_modeportal';
kpi_v1_billing_transaction($cfg, function ($store) use ($row) {
    $store->put($row);
    return ['ok' => true];
});
$script['kind'] = 'portal';
$script['livemode'] = true;
$portalUser = kpi_v1_auth_read_user('u_modeportal');
$portalMismatch = kpi_v1_stripe_start_portal($cfg, $portalUser, ['locale' => 'en'], $server, $now);
$portalBody = $calls ? (string) $calls[count($calls) - 1]['body'] : '';
check(
    '16 portal mode mismatch rejected',
    empty($portalMismatch['ok']) && $portalMismatch['error'] === 'stripe_livemode_mismatch'
        && strpos($portalBody, rawurlencode('http://127.0.0.1/kpi-navigator/en/setting/change_plan.html')) !== false
);

$script['kind'] = 'checkout';
$script['livemode'] = true;
$checkoutMismatch = kpi_v1_stripe_start_checkout($cfg, $user, ['plan' => 'basic'], $server, $now);
check(
    '17 checkout mode mismatch rejected',
    empty($checkoutMismatch['ok']) && $checkoutMismatch['error'] === 'stripe_livemode_mismatch'
);

if ($failures) {
    fwrite(STDERR, count($failures) . " failed\n");
    exit(1);
}
echo "OK\n";
