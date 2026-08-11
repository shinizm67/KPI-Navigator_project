<?php
/**
 * POST /api/v1/feedback.php
 * Gear → ご意見・リクエスト. Mail to supportEmail (default support@forge-laboratory.com).
 */

require __DIR__ . '/_auth.php';

$cfg = kpi_v1_load_config();
kpi_v1_auth_boot($cfg);
kpi_v1_auth_require_post();

$body = kpi_v1_auth_read_json_body();

$category = isset($body['category']) ? strtolower(trim((string) $body['category'])) : '';
$allowed = ['bug' => true, 'ux' => true, 'feature' => true, 'other' => true];
if ($category === '' || !isset($allowed[$category])) {
    kpi_v1_json_out(400, ['ok' => false, 'error' => 'invalid_category']);
}

$message = isset($body['message']) ? trim((string) $body['message']) : '';
if ($message === '' || mb_strlen($message) > 2000) {
    kpi_v1_json_out(400, ['ok' => false, 'error' => 'invalid_message']);
}

$contact = '';
if (isset($body['contactEmail']) && (string) $body['contactEmail'] !== '') {
    $contact = kpi_v1_auth_normalize_email($body['contactEmail']);
    if ($contact === null) {
        kpi_v1_json_out(400, ['ok' => false, 'error' => 'invalid_contact_email']);
    }
}

$pageUrl = isset($body['pageUrl']) ? trim((string) $body['pageUrl']) : '';
if (mb_strlen($pageUrl) > 500) {
    $pageUrl = mb_substr($pageUrl, 0, 500);
}
$userAgent = isset($body['userAgent']) ? trim((string) $body['userAgent']) : '';
if (mb_strlen($userAgent) > 400) {
    $userAgent = mb_substr($userAgent, 0, 400);
}

$now = time();
$last = isset($_SESSION['kpi_feedback_at']) ? (int) $_SESSION['kpi_feedback_at'] : 0;
if ($last > 0 && ($now - $last) < 45) {
    kpi_v1_json_out(429, ['ok' => false, 'error' => 'rate_limited']);
}

$userId = kpi_v1_auth_current_user_id();
$plan = '';
$sessionEmail = '';
if ($userId !== null) {
    $user = kpi_v1_auth_read_user($userId);
    if (is_array($user)) {
        $pub = kpi_v1_auth_public_user($user, $cfg);
        $plan = isset($pub['plan']) ? (string) $pub['plan'] : '';
        $sessionEmail = isset($pub['email']) ? (string) $pub['email'] : '';
        if ($contact === '' && $sessionEmail !== '') {
            $contact = $sessionEmail;
        }
    }
}

$to = isset($cfg['supportEmail']) ? trim((string) $cfg['supportEmail']) : '';
if ($to === '' || !filter_var($to, FILTER_VALIDATE_EMAIL)) {
    $to = 'support@forge-laboratory.com';
}
$from = isset($cfg['supportFrom']) ? trim((string) $cfg['supportFrom']) : '';
if ($from === '' || !filter_var($from, FILTER_VALIDATE_EMAIL)) {
    $from = $to;
}

$labels = [
    'bug' => '不具合',
    'ux' => '使いにくい',
    'feature' => '機能要望',
    'other' => 'その他',
];
$label = $labels[$category];
$stamp = gmdate('Y-m-d\TH:i:s\Z');
$subject = '[Key Performance Navigator] ' . $label . ' / ' . ($userId !== null ? $userId : 'guest');

$lines = [
    'Key Performance Navigator feedback',
    '---',
    'At: ' . $stamp,
    'Category: ' . $category . ' (' . $label . ')',
    'UserId: ' . ($userId !== null ? $userId : '(not logged in)'),
    'Plan: ' . ($plan !== '' ? $plan : '(unknown)'),
    'Session email: ' . ($sessionEmail !== '' ? $sessionEmail : '(none)'),
    'Contact: ' . ($contact !== '' ? $contact : '(none)'),
    'Page: ' . ($pageUrl !== '' ? $pageUrl : '(none)'),
    'UA: ' . ($userAgent !== '' ? $userAgent : '(none)'),
    '---',
    $message,
];
$text = implode("\n", $lines);

$dir = __DIR__ . '/data/feedback';
if (!is_dir($dir)) {
    @mkdir($dir, 0750, true);
}
$logName = $dir . '/' . gmdate('Ymd-His') . '_' . bin2hex(random_bytes(4)) . '.json';
@file_put_contents(
    $logName,
    json_encode(
        [
            'at' => $stamp,
            'category' => $category,
            'userId' => $userId,
            'plan' => $plan,
            'sessionEmail' => $sessionEmail,
            'contactEmail' => $contact,
            'pageUrl' => $pageUrl,
            'userAgent' => $userAgent,
            'message' => $message,
        ],
        JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT
    ),
    LOCK_EX
);

$headers = [
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: 8bit',
    'From: Key Performance Navigator <' . $from . '>',
];
if ($contact !== '') {
    $headers[] = 'Reply-To: ' . $contact;
}
$ok = @mail($to, '=?UTF-8?B?' . base64_encode($subject) . '?=', $text, implode("\r\n", $headers));
if (!$ok) {
    kpi_v1_json_out(502, ['ok' => false, 'error' => 'mail_failed']);
}

$_SESSION['kpi_feedback_at'] = $now;
kpi_v1_json_out(200, ['ok' => true]);
