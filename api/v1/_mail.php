<?php
/**
 * Lightweight mail helper — PHP mail() only (no PHPMailer).
 * Reuses supportFrom / supportEmail from config (same as feedback.php).
 */

require_once __DIR__ . '/_bootstrap.php';

/**
 * @return array{from:string,to:string}
 */
function kpi_v1_mail_addresses($cfg)
{
    $to = isset($cfg['supportEmail']) ? trim((string) $cfg['supportEmail']) : '';
    if ($to === '' || !filter_var($to, FILTER_VALIDATE_EMAIL)) {
        $to = 'support@forge-laboratory.com';
    }
    $from = isset($cfg['supportFrom']) ? trim((string) $cfg['supportFrom']) : '';
    if ($from === '' || !filter_var($from, FILTER_VALIDATE_EMAIL)) {
        $from = $to;
    }
    return ['from' => $from, 'to' => $to];
}

/**
 * Send UTF-8 plain text mail. Does not log body secrets.
 * @return bool
 */
function kpi_v1_mail_send($cfg, $toEmail, $subject, $bodyText)
{
    $toEmail = trim((string) $toEmail);
    if ($toEmail === '' || !filter_var($toEmail, FILTER_VALIDATE_EMAIL)) {
        return false;
    }
    $addrs = kpi_v1_mail_addresses($cfg);
    $from = $addrs['from'];
    $headers = [
        'MIME-Version: 1.0',
        'Content-Type: text/plain; charset=UTF-8',
        'Content-Transfer-Encoding: 8bit',
        'From: Key Performance Navigator <' . $from . '>',
    ];
    $encodedSubject = '=?UTF-8?B?' . base64_encode((string) $subject) . '?=';
    return (bool) @mail($toEmail, $encodedSubject, (string) $bodyText, implode("\r\n", $headers));
}
