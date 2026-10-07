<?php
/**
 * Stripe subscription Checkout, webhook, and Customer Portal.
 * stripeMode is test or live. The host name does not select the mode.
 * Entitlement changes happen only inside the verified webhook path.
 */

require_once __DIR__ . '/_auth.php';
require_once __DIR__ . '/_billing_store.php';

function kpi_v1_stripe_env_or_config($envName, $cfg, $cfgKey)
{
    $env = getenv($envName);
    if (is_string($env) && trim($env) !== '') {
        return trim($env);
    }
    if (isset($cfg[$cfgKey]) && trim((string) $cfg[$cfgKey]) !== '') {
        return trim((string) $cfg[$cfgKey]);
    }
    return '';
}

function kpi_v1_stripe_sandbox_price_ids()
{
    return [
        'price_1UN9VpKFNH29caO9yLytJKTw',
        'price_1UN9k2KFNH29caO9pCLbK7xS',
        'price_1UNWRgKFNH29caO9kzKcLf3x',
        'price_1UNWRhKFNH29caO9NXixShH5',
    ];
}

function kpi_v1_stripe_is_sandbox_price($priceId)
{
    return in_array((string) $priceId, kpi_v1_stripe_sandbox_price_ids(), true);
}

/**
 * Empty STRIPE_MODE and stripeMode means test.
 * Any other non-empty value is invalid. The host is not consulted.
 * @return 'test'|'live'|''
 */
function kpi_v1_stripe_mode($cfg)
{
    $raw = strtolower(kpi_v1_stripe_env_or_config('STRIPE_MODE', $cfg, 'stripeMode'));
    if ($raw === '') {
        return 'test';
    }
    if ($raw === 'test' || $raw === 'live') {
        return $raw;
    }
    return '';
}

function kpi_v1_stripe_price_value($cfg, $envName, $cfgKey, $fallback, $mode)
{
    $value = kpi_v1_stripe_env_or_config($envName, $cfg, $cfgKey);
    if ($value === '' && $mode === 'test') {
        $value = $fallback;
    }
    if ($mode === 'live' && kpi_v1_stripe_is_sandbox_price($value)) {
        return '';
    }
    if ($value !== '' && preg_match('/^price_[A-Za-z0-9_]+$/', $value) !== 1) {
        return '';
    }
    return $value;
}

/**
 * Regional Price map. Profile currency does not select a Price.
 * GLOBAL is the USD list. JP is the Japan list. Other countries use GLOBAL.
 */
function kpi_v1_stripe_prices($cfg)
{
    $mode = kpi_v1_stripe_mode($cfg);
    return [
        'GLOBAL' => [
            'basic' => kpi_v1_stripe_price_value($cfg, 'STRIPE_PRICE_BASIC', 'stripePriceBasic', 'price_1UN9VpKFNH29caO9yLytJKTw', $mode),
            'pro' => kpi_v1_stripe_price_value($cfg, 'STRIPE_PRICE_PRO', 'stripePricePro', 'price_1UN9k2KFNH29caO9pCLbK7xS', $mode),
        ],
        'JP' => [
            'basic' => kpi_v1_stripe_price_value($cfg, 'STRIPE_PRICE_BASIC_JP', 'stripePriceBasicJp', 'price_1UNWRgKFNH29caO9kzKcLf3x', $mode),
            'pro' => kpi_v1_stripe_price_value($cfg, 'STRIPE_PRICE_PRO_JP', 'stripePriceProJp', 'price_1UNWRhKFNH29caO9NXixShH5', $mode),
        ],
    ];
}

function kpi_v1_stripe_normalize_country($country)
{
    $code = strtoupper(trim((string) $country));
    if ($code === 'JP') {
        return 'JP';
    }
    return '';
}

function kpi_v1_stripe_region_for_country($country)
{
    return kpi_v1_stripe_normalize_country($country) === 'JP' ? 'JP' : 'GLOBAL';
}

/**
 * Billing region comes only from the saved business country.
 * Request body, currency, locale, and client address are ignored.
 */
function kpi_v1_stripe_region_for_user($cfg, $userId)
{
    require_once __DIR__ . '/_admin_store.php';
    $profile = kpi_v1_profile_read($cfg, $userId);
    $country = (is_array($profile) && isset($profile['country'])) ? $profile['country'] : '';
    return kpi_v1_stripe_region_for_country($country);
}

function kpi_v1_stripe_price_for_plan(array $prices, $region, $plan)
{
    $region = ($region === 'JP') ? 'JP' : 'GLOBAL';
    $plan = ($plan === 'pro') ? 'pro' : 'basic';
    $selected = '';
    if (isset($prices[$region]) && is_array($prices[$region]) && isset($prices[$region][$plan]) && is_string($prices[$region][$plan])) {
        $selected = $prices[$region][$plan];
    }
    if ($selected === '' && isset($prices['GLOBAL'][$plan]) && is_string($prices['GLOBAL'][$plan])) {
        $selected = $prices['GLOBAL'][$plan];
    }
    return $selected;
}

function kpi_v1_stripe_prices_configured(array $prices)
{
    foreach (['GLOBAL', 'JP'] as $region) {
        if (!isset($prices[$region]) || !is_array($prices[$region])) {
            return false;
        }
        $basic = isset($prices[$region]['basic']) ? $prices[$region]['basic'] : '';
        $pro = isset($prices[$region]['pro']) ? $prices[$region]['pro'] : '';
        if (!is_string($basic) || $basic === '' || !is_string($pro) || $pro === '') {
            return false;
        }
        if (kpi_v1_stripe_same($basic, $pro)) {
            return false;
        }
    }
    return kpi_v1_stripe_plan_for_price($prices, $prices['GLOBAL']['basic']) === 'basic'
        && kpi_v1_stripe_plan_for_price($prices, $prices['GLOBAL']['pro']) === 'pro'
        && kpi_v1_stripe_plan_for_price($prices, $prices['JP']['basic']) === 'basic'
        && kpi_v1_stripe_plan_for_price($prices, $prices['JP']['pro']) === 'pro';
}

function kpi_v1_stripe_same($left, $right)
{
    if (!is_string($left) || !is_string($right) || strlen($left) !== strlen($right)) {
        return false;
    }
    return hash_equals($left, $right);
}

function kpi_v1_stripe_plan_for_price(array $prices, $priceId)
{
    $priceId = (string) $priceId;
    $found = null;
    foreach ($prices as $regionPrices) {
        if (!is_array($regionPrices)) {
            continue;
        }
        foreach (['basic', 'pro'] as $plan) {
            if (!isset($regionPrices[$plan]) || !is_string($regionPrices[$plan])) {
                continue;
            }
            if (!kpi_v1_stripe_same($regionPrices[$plan], $priceId)) {
                continue;
            }
            if ($found !== null && $found !== $plan) {
                return null;
            }
            $found = $plan;
        }
    }
    return $found;
}

function kpi_v1_stripe_secret($cfg)
{
    return kpi_v1_stripe_env_or_config('STRIPE_SECRET_KEY', $cfg, 'stripeSecretKey');
}

function kpi_v1_stripe_webhook_secret($cfg)
{
    $mode = kpi_v1_stripe_mode($cfg);
    $testSecret = kpi_v1_stripe_env_or_config('STRIPE_WEBHOOK_SECRET', $cfg, 'stripeWebhookSecret');
    if ($mode === 'live') {
        $liveSecret = kpi_v1_stripe_env_or_config('STRIPE_WEBHOOK_SECRET_LIVE', $cfg, 'stripeWebhookSecretLive');
        if ($liveSecret === '' || strpos($liveSecret, 'sk_') === 0 || strpos($liveSecret, 'rk_') === 0) {
            return '';
        }
        if ($testSecret !== '' && hash_equals($liveSecret, $testSecret)) {
            return '';
        }
        return $liveSecret;
    }
    if ($mode !== 'test') {
        return '';
    }
    return $testSecret;
}

function kpi_v1_stripe_secret_matches_mode($secret, $mode)
{
    $isTest = strpos($secret, 'sk_test_') === 0 || strpos($secret, 'rk_test_') === 0;
    $isLive = strpos($secret, 'sk_live_') === 0 || strpos($secret, 'rk_live_') === 0;
    if ($mode === 'test') {
        return $isTest;
    }
    if ($mode === 'live') {
        return $isLive;
    }
    return false;
}

/**
 * @return array{ok:bool, status?:int, error?:string, mode?:string, secret?:string}
 */
function kpi_v1_stripe_require_mode_key($cfg)
{
    $mode = kpi_v1_stripe_mode($cfg);
    if ($mode !== 'test' && $mode !== 'live') {
        return ['ok' => false, 'status' => 503, 'error' => 'stripe_mode_invalid'];
    }
    $secret = kpi_v1_stripe_secret($cfg);
    if ($secret === '') {
        return ['ok' => false, 'status' => 503, 'error' => 'not_configured'];
    }
    if (!kpi_v1_stripe_secret_matches_mode($secret, $mode)) {
        return ['ok' => false, 'status' => 403, 'error' => 'stripe_key_mismatch'];
    }
    return ['ok' => true, 'mode' => $mode, 'secret' => $secret];
}

function kpi_v1_stripe_livemode_matches($value, $mode)
{
    if (!is_bool($value) || ($mode !== 'test' && $mode !== 'live')) {
        return false;
    }
    return $value === ($mode === 'live');
}

function kpi_v1_stripe_request_host($server)
{
    $host = isset($server['HTTP_HOST']) ? (string) $server['HTTP_HOST'] : '';
    return strtolower(preg_replace('/:\d+$/', '', trim($host)));
}

function kpi_v1_stripe_meta_user($object)
{
    if (!is_array($object) || !isset($object['metadata']) || !is_array($object['metadata'])) {
        return '';
    }
    $id = isset($object['metadata']['kpn_user_id']) ? trim((string) $object['metadata']['kpn_user_id']) : '';
    if (!preg_match('/^[A-Za-z0-9_-]{1,64}$/', $id)) {
        return '';
    }
    return $id;
}

function kpi_v1_stripe_form_encode($params, $prefix = '')
{
    $pairs = [];
    foreach ($params as $key => $value) {
        $name = $prefix === '' ? (string) $key : $prefix . '[' . $key . ']';
        if (is_array($value)) {
            $nested = kpi_v1_stripe_form_encode($value, $name);
            if ($nested !== '') {
                $pairs[] = $nested;
            }
            continue;
        }
        $pairs[] = rawurlencode($name) . '=' . rawurlencode((string) $value);
    }
    return implode('&', $pairs);
}

function kpi_v1_stripe_return_urls($base, $locale)
{
    $locale = strtolower(trim((string) $locale));
    if ($locale === 'zh-tw' || $locale === 'zh') {
        $dir = '/zh-tw/setting/';
    } elseif ($locale === 'en') {
        $dir = '/en/setting/';
    } else {
        $dir = '/setting/';
    }
    return [
        'success_url' => $base . $dir . 'checkout_success.html?checkout=return&session_id={CHECKOUT_SESSION_ID}',
        'cancel_url' => $base . $dir . 'checkout_cancel.html',
    ];
}

function kpi_v1_stripe_loopback_host($host)
{
    $host = strtolower(trim((string) $host));
    return $host === 'localhost' || $host === '127.0.0.1' || $host === '::1';
}

function kpi_v1_stripe_base_allowed($base, $mode)
{
    $parts = parse_url((string) $base);
    if (!is_array($parts) || empty($parts['scheme']) || empty($parts['host']) || !empty($parts['user'])) {
        return false;
    }
    $scheme = strtolower((string) $parts['scheme']);
    $host = strtolower((string) $parts['host']);
    $loop = kpi_v1_stripe_loopback_host($host);
    if ($mode === 'test') {
        return ($scheme === 'http' || $scheme === 'https') && $loop;
    }
    if ($mode !== 'live' || $scheme !== 'https' || $loop) {
        return false;
    }
    $suffix = 'forge-laboratory.com';
    return $host === $suffix || substr($host, -strlen('.' . $suffix)) === '.' . $suffix;
}

function kpi_v1_stripe_resolve_base($cfg, $server)
{
    $mode = kpi_v1_stripe_mode($cfg);
    if ($mode !== 'test' && $mode !== 'live') {
        return ['ok' => false, 'status' => 503, 'error' => 'stripe_mode_invalid'];
    }
    $configured = kpi_v1_stripe_env_or_config('KPN_PUBLIC_BASE_URL', $cfg, 'publicBaseUrl');
    if ($configured !== '') {
        $base = rtrim($configured, '/');
    } else {
        $host = kpi_v1_stripe_request_host($server);
        if ($host === '') {
            return ['ok' => false, 'status' => 403, 'error' => 'return_url_rejected'];
        }
        $https = !empty($server['HTTPS']) && $server['HTTPS'] !== 'off';
        $script = isset($server['SCRIPT_NAME']) ? str_replace('\\', '/', (string) $server['SCRIPT_NAME']) : '';
        $marker = '/api/v1/billing/';
        $pos = strpos($script, $marker);
        $prefix = $pos === false ? '' : substr($script, 0, $pos);
        $base = ($https ? 'https' : 'http') . '://' . $host . $prefix;
    }
    if (!kpi_v1_stripe_base_allowed($base, $mode)) {
        return ['ok' => false, 'status' => 403, 'error' => 'return_url_rejected'];
    }
    return ['ok' => true, 'base' => $base];
}

function kpi_v1_stripe_checkout_params($userId, $plan, $priceId, $successUrl, $cancelUrl, $customerId)
{
    $params = [
        'mode' => 'subscription',
        'line_items' => [
            [
                'price' => $priceId,
                'quantity' => '1',
            ],
        ],
        'success_url' => $successUrl,
        'cancel_url' => $cancelUrl,
        'client_reference_id' => (string) $userId,
        'metadata' => [
            'kpn_user_id' => (string) $userId,
            'kpn_plan' => (string) $plan,
        ],
        'subscription_data' => [
            'metadata' => [
                'kpn_user_id' => (string) $userId,
                'kpn_plan' => (string) $plan,
            ],
        ],
        'adaptive_pricing' => [
            'enabled' => 'false',
        ],
    ];
    if (is_string($customerId) && $customerId !== '') {
        $params['customer'] = $customerId;
    }
    return $params;
}

function kpi_v1_stripe_checkout_blocks(array $billing)
{
    $status = isset($billing['subscriptionStatus']) ? (string) $billing['subscriptionStatus'] : '';
    if (in_array($status, ['active', 'trialing', 'past_due', 'unpaid', 'incomplete'], true)) {
        return true;
    }
    if ($status === '' && !empty($billing['stripeSubscriptionId'])) {
        return true;
    }
    return false;
}

function &kpi_v1_stripe_transport_slot()
{
    static $transport = null;
    return $transport;
}

function kpi_v1_stripe_set_transport($transport)
{
    $slot = &kpi_v1_stripe_transport_slot();
    $slot = $transport;
}

function kpi_v1_stripe_http($secret, $body, $idempotencyKey, $path = '/v1/checkout/sessions')
{
    if (!is_string($path) || strpos($path, '/v1/') !== 0) {
        $path = '/v1/checkout/sessions';
    }
    $slot = &kpi_v1_stripe_transport_slot();
    if (is_callable($slot)) {
        return $slot($secret, $path, $body, $idempotencyKey);
    }
    if (!function_exists('curl_init')) {
        return ['status' => 0, 'json' => null];
    }
    $ch = curl_init('https://api.stripe.com' . $path);
    if ($ch === false) {
        return ['status' => 0, 'json' => null];
    }
    $headers = [
        'Authorization: Bearer ' . $secret,
        'Content-Type: application/x-www-form-urlencoded',
        'User-Agent: KPN-Stripe-Sandbox/1',
    ];
    if ($idempotencyKey !== '') {
        $headers[] = 'Idempotency-Key: ' . $idempotencyKey;
    }
    curl_setopt_array($ch, [
        CURLOPT_POST => true,
        CURLOPT_POSTFIELDS => $body,
        CURLOPT_HTTPHEADER => $headers,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => 20,
    ]);
    $raw = curl_exec($ch);
    $status = (int) curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    $json = is_string($raw) ? json_decode($raw, true) : null;
    return ['status' => $status, 'json' => is_array($json) ? $json : null];
}

function kpi_v1_stripe_url_is_hosted_checkout($url)
{
    $parts = parse_url((string) $url);
    return is_array($parts)
        && isset($parts['scheme'], $parts['host'])
        && $parts['scheme'] === 'https'
        && strtolower((string) $parts['host']) === 'checkout.stripe.com';
}

function kpi_v1_stripe_portal_return_url($base, $locale)
{
    $locale = strtolower(trim((string) $locale));
    if ($locale === 'zh-tw' || $locale === 'zh') {
        $dir = '/zh-tw/setting/';
    } elseif ($locale === 'en') {
        $dir = '/en/setting/';
    } else {
        $dir = '/setting/';
    }
    return $base . $dir . 'change_plan.html';
}

function kpi_v1_stripe_customer_id_ok($customerId)
{
    return is_string($customerId) && preg_match('/^cus_[A-Za-z0-9]{1,250}$/', $customerId) === 1;
}

function kpi_v1_stripe_url_is_hosted_portal($url)
{
    $parts = parse_url((string) $url);
    return is_array($parts)
        && isset($parts['scheme'], $parts['host'])
        && $parts['scheme'] === 'https'
        && strtolower((string) $parts['host']) === 'billing.stripe.com'
        && empty($parts['user']);
}

/**
 * Billing Portal Session for the signed-in user's stored Stripe customer.
 * The browser cannot choose the customer, subscription, or return URL.
 * Does not cancel or change the subscription. Dashboard portal settings do.
 */
function kpi_v1_stripe_start_portal($cfg, $user, $body, $server, $now = null)
{
    if (!is_array($user) || empty($user['userId'])) {
        return ['ok' => false, 'status' => 401, 'error' => 'unauthorized'];
    }
    if (!empty($user['disabled'])) {
        return ['ok' => false, 'status' => 403, 'error' => 'account_disabled'];
    }
    if (!is_array($body)) {
        return ['ok' => false, 'status' => 400, 'error' => 'invalid_json'];
    }
    foreach ([
        'customer', 'customerId', 'customer_id', 'subscription', 'subscriptionId', 'subscription_id',
        'return_url', 'returnUrl', 'mode', 'price', 'priceId', 'price_id',
    ] as $forbidden) {
        if (array_key_exists($forbidden, $body)) {
            return ['ok' => false, 'status' => 400, 'error' => 'client_billing_forbidden'];
        }
    }
    $key = kpi_v1_stripe_require_mode_key($cfg);
    if (empty($key['ok'])) {
        return $key;
    }
    $secret = $key['secret'];
    $mode = $key['mode'];
    $base = kpi_v1_stripe_resolve_base($cfg, is_array($server) ? $server : []);
    if (empty($base['ok'])) {
        return $base;
    }
    $locale = isset($body['locale']) ? (string) $body['locale'] : 'ja';
    $returnUrl = kpi_v1_stripe_portal_return_url($base['base'], $locale);
    $userId = (string) $user['userId'];
    $look = kpi_v1_billing_transaction($cfg, function ($store) use ($userId) {
        return ['ok' => true, 'billing' => $store->get($userId), 'rollback' => true];
    });
    if (empty($look['ok'])) {
        return $look;
    }
    $billing = (isset($look['billing']) && is_array($look['billing'])) ? $look['billing'] : null;
    $customerId = is_array($billing) && isset($billing['stripeCustomerId']) ? (string) $billing['stripeCustomerId'] : '';
    if (!kpi_v1_stripe_customer_id_ok($customerId)) {
        return ['ok' => false, 'status' => 409, 'error' => 'no_stripe_customer'];
    }
    $params = [
        'customer' => $customerId,
        'return_url' => $returnUrl,
    ];
    $encoded = kpi_v1_stripe_form_encode($params);
    $now = $now === null ? time() : (int) $now;
    $idempotency = 'kpn_portal_' . hash('sha256', $userId . '|' . (string) (int) floor($now / 60));
    $response = kpi_v1_stripe_http($secret, $encoded, $idempotency, '/v1/billing_portal/sessions');
    $status = isset($response['status']) ? (int) $response['status'] : 0;
    $json = isset($response['json']) && is_array($response['json']) ? $response['json'] : null;
    $stripeCode = '';
    if (is_array($json) && isset($json['error']) && is_array($json['error']) && isset($json['error']['code'])) {
        $stripeCode = (string) $json['error']['code'];
    }
    if ($stripeCode === 'resource_missing') {
        return ['ok' => false, 'status' => 409, 'error' => 'customer_mode_mismatch'];
    }
    if ($status < 200 || $status >= 300 || $json === null || empty($json['url']) || empty($json['id'])) {
        return ['ok' => false, 'status' => 502, 'error' => 'stripe_error'];
    }
    if (!kpi_v1_stripe_url_is_hosted_portal($json['url'])) {
        return ['ok' => false, 'status' => 502, 'error' => 'stripe_error'];
    }
    if (!isset($json['livemode']) || !kpi_v1_stripe_livemode_matches($json['livemode'], $mode)) {
        return ['ok' => false, 'status' => 502, 'error' => 'stripe_livemode_mismatch'];
    }
    return [
        'ok' => true,
        'status' => 200,
        'url' => (string) $json['url'],
        'id' => (string) $json['id'],
        'params' => $params,
        'body' => $encoded,
    ];
}

/**
 * Create a hosted Checkout Session. $user null means unauthenticated.
 * Does not change kpi_users.plan.
 */
function kpi_v1_stripe_start_checkout($cfg, $user, $body, $server, $now = null)
{
    if (!is_array($user) || empty($user['userId'])) {
        return ['ok' => false, 'status' => 401, 'error' => 'unauthorized'];
    }
    if (!empty($user['disabled'])) {
        return ['ok' => false, 'status' => 403, 'error' => 'account_disabled'];
    }
    if (!is_array($body)) {
        return ['ok' => false, 'status' => 400, 'error' => 'invalid_json'];
    }
    foreach (['price', 'priceId', 'price_id', 'country', 'currency', 'region', 'mode', 'success_url', 'cancel_url'] as $forbidden) {
        if (array_key_exists($forbidden, $body)) {
            return ['ok' => false, 'status' => 400, 'error' => 'client_price_forbidden'];
        }
    }
    $plan = isset($body['plan']) ? strtolower(trim((string) $body['plan'])) : '';
    if ($plan !== 'basic' && $plan !== 'pro') {
        return ['ok' => false, 'status' => 400, 'error' => 'invalid_plan'];
    }
    $key = kpi_v1_stripe_require_mode_key($cfg);
    if (empty($key['ok'])) {
        return $key;
    }
    $secret = $key['secret'];
    $mode = $key['mode'];
    $prices = kpi_v1_stripe_prices($cfg);
    if (!kpi_v1_stripe_prices_configured($prices)) {
        return ['ok' => false, 'status' => 503, 'error' => 'not_configured'];
    }
    $base = kpi_v1_stripe_resolve_base($cfg, is_array($server) ? $server : []);
    if (empty($base['ok'])) {
        return $base;
    }
    $locale = isset($body['locale']) ? (string) $body['locale'] : 'ja';
    $urls = kpi_v1_stripe_return_urls($base['base'], $locale);
    $userId = (string) $user['userId'];
    $region = kpi_v1_stripe_region_for_user($cfg, $userId);
    $priceId = kpi_v1_stripe_price_for_plan($prices, $region, $plan);
    if ($priceId === '') {
        return ['ok' => false, 'status' => 503, 'error' => 'not_configured'];
    }
    $existing = null;
    $look = kpi_v1_billing_transaction($cfg, function ($store) use ($userId) {
        return ['ok' => true, 'billing' => $store->get($userId), 'rollback' => true];
    });
    if (empty($look['ok'])) {
        return $look;
    }
    if (isset($look['billing']) && is_array($look['billing'])) {
        $existing = $look['billing'];
        if (kpi_v1_stripe_checkout_blocks($existing)) {
            return ['ok' => false, 'status' => 409, 'error' => 'already_subscribed'];
        }
    }
    $customerId = is_array($existing) ? $existing['stripeCustomerId'] : '';
    $params = kpi_v1_stripe_checkout_params(
        $userId,
        $plan,
        $priceId,
        $urls['success_url'],
        $urls['cancel_url'],
        is_string($customerId) ? $customerId : ''
    );
    $encoded = kpi_v1_stripe_form_encode($params);
    $encoded = str_replace(rawurlencode('{CHECKOUT_SESSION_ID}'), '{CHECKOUT_SESSION_ID}', $encoded);
    $now = $now === null ? time() : (int) $now;
    $idempotency = 'kpn_' . hash('sha256', $userId . '|' . $plan . '|' . $region . '|' . (string) (int) floor($now / 600));
    $response = kpi_v1_stripe_http($secret, $encoded, $idempotency);
    $status = isset($response['status']) ? (int) $response['status'] : 0;
    $json = isset($response['json']) && is_array($response['json']) ? $response['json'] : null;
    if ($status < 200 || $status >= 300 || $json === null || empty($json['url']) || empty($json['id'])) {
        return ['ok' => false, 'status' => 502, 'error' => 'stripe_error'];
    }
    if (!kpi_v1_stripe_url_is_hosted_checkout($json['url'])) {
        return ['ok' => false, 'status' => 502, 'error' => 'stripe_error'];
    }
    if (!isset($json['livemode']) || !kpi_v1_stripe_livemode_matches($json['livemode'], $mode)) {
        return ['ok' => false, 'status' => 502, 'error' => 'stripe_livemode_mismatch'];
    }
    return [
        'ok' => true,
        'status' => 200,
        'url' => (string) $json['url'],
        'id' => (string) $json['id'],
        'params' => $params,
        'body' => $encoded,
    ];
}

function kpi_v1_stripe_verify_signature($payload, $header, $secret, $now, $tolerance = 300)
{
    if (!is_string($payload) || $payload === '' || !is_string($header) || $header === '' || !is_string($secret) || $secret === '') {
        return false;
    }
    $timestamp = '';
    $signatures = [];
    foreach (explode(',', $header) as $part) {
        $part = trim($part);
        if (strpos($part, 't=') === 0) {
            $timestamp = substr($part, 2);
        } elseif (strpos($part, 'v1=') === 0) {
            $signatures[] = substr($part, 3);
        }
    }
    if ($timestamp === '' || !ctype_digit($timestamp) || !$signatures) {
        return false;
    }
    if (abs((int) $now - (int) $timestamp) > (int) $tolerance) {
        return false;
    }
    $expected = hash_hmac('sha256', $timestamp . '.' . $payload, $secret);
    foreach ($signatures as $signature) {
        if (hash_equals($expected, $signature)) {
            return true;
        }
    }
    return false;
}

function kpi_v1_stripe_subscription_price($subscription)
{
    if (!is_array($subscription) || !isset($subscription['items']['data']) || !is_array($subscription['items']['data'])) {
        return ['error' => 'unmapped_price'];
    }
    if (count($subscription['items']['data']) !== 1) {
        return ['error' => 'unmapped_price'];
    }
    $item = $subscription['items']['data'][0];
    if (!is_array($item)) {
        return ['error' => 'unmapped_price'];
    }
    $qty = isset($item['quantity']) ? (int) $item['quantity'] : 1;
    if ($qty !== 1) {
        return ['error' => 'unexpected_quantity'];
    }
    $price = isset($item['price']) ? $item['price'] : null;
    $priceId = '';
    if (is_string($price)) {
        $priceId = $price;
    } elseif (is_array($price) && isset($price['id'])) {
        $priceId = (string) $price['id'];
    }
    if ($priceId === '') {
        return ['error' => 'unmapped_price'];
    }
    return ['priceId' => $priceId];
}

function kpi_v1_stripe_apply_subscription(array $prices, array $billing, array $object, $deleted)
{
    $status = $deleted ? 'canceled' : strtolower(trim((string) (isset($object['status']) ? $object['status'] : '')));
    $billing['subscriptionStatus'] = $status;
    $billing['cancelAtPeriodEnd'] = !empty($object['cancel_at_period_end']);
    if (!empty($object['customer']) && is_string($object['customer'])) {
        $billing['stripeCustomerId'] = $object['customer'];
    }
    if (!empty($object['id']) && is_string($object['id'])) {
        $billing['stripeSubscriptionId'] = $object['id'];
    }
    if (isset($object['current_period_end']) && is_numeric($object['current_period_end'])) {
        $billing['currentPeriodEnd'] = gmdate('c', (int) $object['current_period_end']);
    }
    $priceInfo = kpi_v1_stripe_subscription_price($object);
    $mapped = null;
    if (isset($priceInfo['priceId'])) {
        $billing['stripePriceId'] = $priceInfo['priceId'];
        $mapped = kpi_v1_stripe_plan_for_price($prices, $priceInfo['priceId']);
    }
    $plan = null;
    $grant = ($status === 'active' && $mapped !== null && empty($priceInfo['error']));
    if ($grant) {
        $billing['entitlementGranted'] = true;
        $plan = $mapped;
    } else {
        if (!empty($billing['entitlementGranted'])) {
            $plan = 'basic';
        }
        $billing['entitlementGranted'] = false;
    }
    return ['billing' => $billing, 'plan' => $plan];
}

function kpi_v1_stripe_apply_event(array $prices, array $billing, array $event)
{
    $type = isset($event['type']) ? (string) $event['type'] : '';
    $object = (isset($event['data']['object']) && is_array($event['data']['object'])) ? $event['data']['object'] : [];
    $billing['lastEventId'] = isset($event['id']) ? (string) $event['id'] : $billing['lastEventId'];
    $billing['updatedAt'] = gmdate('c');

    if ($type === 'checkout.session.completed') {
        if (isset($object['mode']) && (string) $object['mode'] !== 'subscription') {
            return ['billing' => $billing, 'plan' => null];
        }
        if (!empty($object['customer']) && is_string($object['customer'])) {
            $billing['stripeCustomerId'] = $object['customer'];
        }
        if (!empty($object['subscription']) && is_string($object['subscription'])) {
            $billing['stripeSubscriptionId'] = $object['subscription'];
        }
        if (!empty($object['id']) && is_string($object['id'])) {
            $billing['checkoutSessionId'] = $object['id'];
        }
        return ['billing' => $billing, 'plan' => null];
    }

    if ($type === 'customer.subscription.created' || $type === 'customer.subscription.updated' || $type === 'customer.subscription.deleted') {
        return kpi_v1_stripe_apply_subscription($prices, $billing, $object, $type === 'customer.subscription.deleted');
    }

    if ($type === 'invoice.payment_succeeded' || $type === 'invoice.payment_failed') {
        $billing['lastInvoiceStatus'] = $type === 'invoice.payment_succeeded' ? 'succeeded' : 'failed';
        if (!empty($object['customer']) && is_string($object['customer']) && empty($billing['stripeCustomerId'])) {
            $billing['stripeCustomerId'] = $object['customer'];
        }
        if (!empty($object['subscription']) && is_string($object['subscription']) && empty($billing['stripeSubscriptionId'])) {
            $billing['stripeSubscriptionId'] = $object['subscription'];
        }
        return ['billing' => $billing, 'plan' => null];
    }

    return ['billing' => $billing, 'plan' => null, 'ignored' => true];
}

function kpi_v1_stripe_event_ids(array $event)
{
    $object = (isset($event['data']['object']) && is_array($event['data']['object'])) ? $event['data']['object'] : [];
    $type = isset($event['type']) ? (string) $event['type'] : '';
    $meta = kpi_v1_stripe_meta_user($object);
    $reference = '';
    if ($type === 'checkout.session.completed' && !empty($object['client_reference_id'])) {
        $reference = trim((string) $object['client_reference_id']);
        if (!preg_match('/^[A-Za-z0-9_-]{1,64}$/', $reference)) {
            $reference = '';
        }
    }
    $customer = '';
    $subscription = '';
    if (!empty($object['customer']) && is_string($object['customer'])) {
        $customer = $object['customer'];
    }
    if ($type === 'checkout.session.completed' || strpos($type, 'invoice.') === 0) {
        if (!empty($object['subscription']) && is_string($object['subscription'])) {
            $subscription = $object['subscription'];
        }
    } elseif (strpos($type, 'customer.subscription.') === 0 && !empty($object['id'])) {
        $subscription = (string) $object['id'];
    }
    return [
        'metaUser' => $meta,
        'reference' => $reference,
        'customer' => $customer,
        'subscription' => $subscription,
    ];
}

function kpi_v1_stripe_set_user_plan($cfg, array $user, $newPlan)
{
    $newPlan = (string) $newPlan;
    $old = isset($user['plan']) ? strtolower(trim((string) $user['plan'])) : 'basic';
    if ($old !== 'basic' && $old !== 'pro') {
        $old = 'basic';
    }
    if ($old === $newPlan) {
        return;
    }
    if (!empty($user['disabled'])) {
        return;
    }
    $user['plan'] = $newPlan;
    $user['planUpdatedAt'] = gmdate('c');
    kpi_v1_auth_write_user($user);
    require_once __DIR__ . '/_admin_store.php';
    kpi_v1_plan_history_append($cfg, $user['userId'], $old, $newPlan, 'stripe', 'stripe');
}

/**
 * Verify and apply one Stripe event. Idempotent on event id.
 * Browser success URLs never call this.
 */
function kpi_v1_stripe_handle_webhook($cfg, $payload, $header, $server, $now = null)
{
    $now = $now === null ? time() : (int) $now;
    $mode = kpi_v1_stripe_mode($cfg);
    if ($mode !== 'test' && $mode !== 'live') {
        return ['ok' => false, 'status' => 503, 'error' => 'stripe_mode_invalid'];
    }
    $secret = kpi_v1_stripe_webhook_secret($cfg);
    if ($secret === '' || strpos($secret, 'sk_') === 0 || strpos($secret, 'rk_') === 0) {
        return ['ok' => false, 'status' => 503, 'error' => 'not_configured'];
    }
    if (!kpi_v1_stripe_verify_signature((string) $payload, (string) $header, $secret, $now)) {
        return ['ok' => false, 'status' => 400, 'error' => 'invalid_signature'];
    }
    $event = json_decode((string) $payload, true);
    if (!is_array($event) || empty($event['id']) || empty($event['type']) || !isset($event['data']['object'])) {
        return ['ok' => false, 'status' => 400, 'error' => 'invalid_event'];
    }
    if (!isset($event['livemode']) || !kpi_v1_stripe_livemode_matches($event['livemode'], $mode)) {
        return ['ok' => false, 'status' => 400, 'error' => 'stripe_livemode_mismatch'];
    }
    $eventId = (string) $event['id'];
    if (!preg_match('/^[A-Za-z0-9_]{1,64}$/', $eventId)) {
        return ['ok' => false, 'status' => 400, 'error' => 'invalid_event'];
    }
    $prices = kpi_v1_stripe_prices($cfg);
    $ids = kpi_v1_stripe_event_ids($event);

    return kpi_v1_billing_transaction($cfg, function ($store) use ($cfg, $event, $eventId, $prices, $ids) {
        if ($store->eventSeen($eventId)) {
            return [
                'ok' => true,
                'status' => 200,
                'duplicate' => true,
                'rollback' => true,
            ];
        }
        if ($ids['metaUser'] !== '' && $ids['reference'] !== '' && $ids['metaUser'] !== $ids['reference']) {
            $store->putEvent($eventId, (string) $event['type']);
            return ['ok' => true, 'status' => 200, 'ignored' => 'identity_conflict'];
        }
        $bound = $ids['metaUser'] !== '' ? $ids['metaUser'] : $ids['reference'];
        $bySub = $ids['subscription'] !== '' ? $store->findBySubscription($ids['subscription']) : null;
        $byCus = $ids['customer'] !== '' ? $store->findByCustomer($ids['customer']) : null;
        if ($bound !== '' && $bySub !== null && $bound !== $bySub) {
            $store->putEvent($eventId, (string) $event['type']);
            return ['ok' => true, 'status' => 200, 'ignored' => 'identity_conflict'];
        }
        if ($bound !== '' && $byCus !== null && $bound !== $byCus) {
            $store->putEvent($eventId, (string) $event['type']);
            return ['ok' => true, 'status' => 200, 'ignored' => 'identity_conflict'];
        }
        if ($bound === '') {
            $bound = $bySub !== null ? $bySub : ($byCus !== null ? $byCus : '');
        }
        if ($bound === '') {
            $store->putEvent($eventId, (string) $event['type']);
            return ['ok' => true, 'status' => 200, 'ignored' => 'unbound'];
        }
        $user = kpi_v1_auth_read_user($bound);
        if (!is_array($user)) {
            $store->putEvent($eventId, (string) $event['type']);
            return ['ok' => true, 'status' => 200, 'ignored' => 'unknown_user'];
        }
        $billing = $store->get($bound);
        if (!is_array($billing)) {
            $billing = kpi_v1_billing_blank($bound);
        }
        $applied = kpi_v1_stripe_apply_event($prices, $billing, $event);
        if (!empty($user['disabled'])) {
            $applied['plan'] = null;
            $applied['billing']['entitlementGranted'] = false;
        }
        $store->put($applied['billing']);
        if (isset($applied['plan']) && ($applied['plan'] === 'basic' || $applied['plan'] === 'pro')) {
            kpi_v1_stripe_set_user_plan($cfg, $user, $applied['plan']);
        }
        $store->putEvent($eventId, (string) $event['type']);
        return [
            'ok' => true,
            'status' => 200,
            'duplicate' => false,
            'userId' => $bound,
            'plan' => isset($applied['plan']) ? $applied['plan'] : null,
            'billing' => $applied['billing'],
        ];
    });
}

/**
 * Display amounts for the allowlisted Sandbox Prices.
 * Keyed by Price ID so a country change cannot relabel an existing subscription.
 */
function kpi_v1_stripe_known_price_displays()
{
    return [
        'price_1UN9VpKFNH29caO9yLytJKTw' => ['plan' => 'basic', 'currency' => 'USD', 'amount' => 10],
        'price_1UN9k2KFNH29caO9pCLbK7xS' => ['plan' => 'pro', 'currency' => 'USD', 'amount' => 30],
        'price_1UNWRgKFNH29caO9kzKcLf3x' => ['plan' => 'basic', 'currency' => 'JPY', 'amount' => 1000],
        'price_1UNWRhKFNH29caO9NXixShH5' => ['plan' => 'pro', 'currency' => 'JPY', 'amount' => 3000],
    ];
}

function kpi_v1_stripe_format_amount($currency, $amount)
{
    if ($currency === 'JPY') {
        return '¥' . number_format((int) $amount);
    }
    if ($currency === 'USD') {
        return '$' . number_format((int) $amount);
    }
    return '';
}

function kpi_v1_stripe_public_amount($row)
{
    if (!is_array($row) || !isset($row['currency'], $row['amount'])) {
        return ['amount' => null, 'formattedAmount' => ''];
    }
    return [
        'amount' => (int) $row['amount'],
        'formattedAmount' => kpi_v1_stripe_format_amount($row['currency'], $row['amount']),
    ];
}

/**
 * Regional offer for a new Checkout. Uses the saved business country only.
 * Does not describe an existing subscription.
 */
function kpi_v1_stripe_offer_for_user($cfg, $userId)
{
    $prices = kpi_v1_stripe_prices($cfg);
    $region = kpi_v1_stripe_region_for_user($cfg, $userId);
    $catalog = kpi_v1_stripe_known_price_displays();
    $basicId = kpi_v1_stripe_price_for_plan($prices, $region, 'basic');
    $proId = kpi_v1_stripe_price_for_plan($prices, $region, 'pro');
    $basic = isset($catalog[$basicId]) ? $catalog[$basicId] : null;
    $pro = isset($catalog[$proId]) ? $catalog[$proId] : null;
    $currency = '';
    if (is_array($basic) && is_array($pro) && $basic['currency'] === $pro['currency']) {
        $currency = $basic['currency'];
    }
    return [
        'pricingRegion' => $region,
        'currency' => $currency,
        'basic' => kpi_v1_stripe_public_amount($basic),
        'pro' => kpi_v1_stripe_public_amount($pro),
    ];
}

function kpi_v1_stripe_subscription_price_display($priceId)
{
    $catalog = kpi_v1_stripe_known_price_displays();
    $priceId = (string) $priceId;
    if ($priceId === '' || !isset($catalog[$priceId])) {
        return ['known' => false];
    }
    $row = $catalog[$priceId];
    $public = kpi_v1_stripe_public_amount($row);
    return [
        'known' => true,
        'plan' => $row['plan'],
        'currency' => $row['currency'],
        'amount' => $public['amount'],
        'formattedAmount' => $public['formattedAmount'],
    ];
}

function kpi_v1_billing_status_payload($cfg, array $user)
{
    $userId = (string) $user['userId'];
    $look = kpi_v1_billing_transaction($cfg, function ($store) use ($userId) {
        return ['ok' => true, 'billing' => $store->get($userId), 'rollback' => true];
    });
    $billing = (isset($look['billing']) && is_array($look['billing'])) ? $look['billing'] : null;
    $prices = kpi_v1_stripe_prices($cfg);
    $mapped = null;
    if ($billing !== null && !empty($billing['stripePriceId'])) {
        $mapped = kpi_v1_stripe_plan_for_price($prices, $billing['stripePriceId']);
    }
    $status = $billing !== null && isset($billing['subscriptionStatus']) ? $billing['subscriptionStatus'] : null;
    $confirmed = $billing !== null
        && !empty($billing['entitlementGranted'])
        && $status === 'active'
        && $mapped !== null;
    $public = kpi_v1_auth_public_user($user, $cfg);
    $subscriptionPrice = null;
    if ($billing !== null && !empty($billing['stripePriceId'])) {
        $subscriptionPrice = kpi_v1_stripe_subscription_price_display($billing['stripePriceId']);
    }
    return [
        'ok' => true,
        'plan' => $public['plan'],
        'offer' => kpi_v1_stripe_offer_for_user($cfg, $userId),
        'billing' => [
            'status' => $status,
            'plan' => $mapped,
            'cancelAtPeriodEnd' => $billing !== null && !empty($billing['cancelAtPeriodEnd']),
            'currentPeriodEnd' => $billing !== null ? $billing['currentPeriodEnd'] : null,
            'confirmed' => $confirmed,
            'invoiceStatus' => $billing !== null ? $billing['lastInvoiceStatus'] : null,
            'subscriptionPrice' => $subscriptionPrice,
            'portalAvailable' => $billing !== null && kpi_v1_stripe_customer_id_ok(isset($billing['stripeCustomerId']) ? (string) $billing['stripeCustomerId'] : ''),
        ],
    ];
}
