<?php
/**
 * Stripe Sandbox subscription state.
 * File driver: one JSON document under the data root.
 * MySQL driver: kpi_stripe_subscriptions + kpi_stripe_events.
 * Neither store is the entitlement source. kpi_users.plan remains that field.
 */

require_once __DIR__ . '/_bootstrap.php';

function kpi_v1_billing_blank($userId)
{
    return [
        'userId' => (string) $userId,
        'stripeCustomerId' => null,
        'stripeSubscriptionId' => null,
        'stripePriceId' => null,
        'subscriptionStatus' => null,
        'cancelAtPeriodEnd' => false,
        'currentPeriodEnd' => null,
        'entitlementGranted' => false,
        'checkoutSessionId' => null,
        'lastInvoiceStatus' => null,
        'lastEventId' => null,
        'updatedAt' => gmdate('c'),
    ];
}

function kpi_v1_billing_dir()
{
    $dir = kpi_v1_file_data_root() . '/billing';
    if (!is_dir($dir)) {
        mkdir($dir, 0750, true);
    }
    return $dir;
}

function kpi_v1_billing_empty_state()
{
    return [
        'subscriptions' => [],
        'byCustomer' => [],
        'bySubscription' => [],
        'events' => [],
    ];
}

/**
 * Run $fn with an exclusive billing store. The callback receives a store object
 * and returns an array. File mode saves when the store is dirty. MySQL commits
 * the same PDO transaction used for the user plan update.
 *
 * @return array
 */
function kpi_v1_billing_transaction($cfg, $fn)
{
    if (kpi_v1_storage_is_mysql($cfg)) {
        require_once __DIR__ . '/_db.php';
        $pdo = kpi_v1_db($cfg);
        if (!$pdo instanceof PDO) {
            return ['ok' => false, 'status' => 500, 'error' => 'db_unavailable'];
        }
        try {
            $pdo->beginTransaction();
            $store = new KpiV1BillingMysqlStore($pdo);
            $result = $fn($store);
            if (!is_array($result)) {
                $result = ['ok' => false, 'status' => 500, 'error' => 'billing_write_failed'];
            }
            if ($pdo->inTransaction()) {
                if (!empty($result['rollback'])) {
                    $pdo->rollBack();
                } else {
                    $pdo->commit();
                }
            }
            return $result;
        } catch (Throwable $e) {
            if ($pdo instanceof PDO && $pdo->inTransaction()) {
                $pdo->rollBack();
            }
            $sqlState = ($e instanceof PDOException && isset($e->errorInfo[0])) ? (string) $e->errorInfo[0] : '';
            if ($sqlState === '42S02') {
                return ['ok' => false, 'status' => 500, 'error' => 'billing_schema_missing'];
            }
            return ['ok' => false, 'status' => 500, 'error' => 'billing_write_failed'];
        }
    }

    $dir = kpi_v1_billing_dir();
    $lock = fopen($dir . '/state.lock', 'c');
    if ($lock === false) {
        return ['ok' => false, 'status' => 500, 'error' => 'billing_lock_failed'];
    }
    if (!flock($lock, LOCK_EX)) {
        fclose($lock);
        return ['ok' => false, 'status' => 500, 'error' => 'billing_lock_failed'];
    }
    try {
        $path = $dir . '/state.json';
        $state = kpi_v1_billing_empty_state();
        if (is_file($path)) {
            $decoded = json_decode((string) file_get_contents($path), true);
            if (is_array($decoded)) {
                foreach (['subscriptions', 'byCustomer', 'bySubscription', 'events'] as $key) {
                    if (isset($decoded[$key]) && is_array($decoded[$key])) {
                        $state[$key] = $decoded[$key];
                    }
                }
            }
        }
        $store = new KpiV1BillingFileStore($state);
        $result = $fn($store);
        if (!is_array($result)) {
            $result = ['ok' => false, 'status' => 500, 'error' => 'billing_write_failed'];
        }
        if (empty($result['rollback']) && $store->isDirty()) {
            $json = json_encode($store->state(), JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT);
            $tmp = $path . '.tmp';
            if ($json === false || file_put_contents($tmp, $json, LOCK_EX) === false) {
                @unlink($tmp);
                return ['ok' => false, 'status' => 500, 'error' => 'billing_write_failed'];
            }
            if (is_file($path)) {
                @unlink($path);
            }
            if (!rename($tmp, $path)) {
                @unlink($tmp);
                return ['ok' => false, 'status' => 500, 'error' => 'billing_write_failed'];
            }
        }
        return $result;
    } finally {
        flock($lock, LOCK_UN);
        fclose($lock);
    }
}

class KpiV1BillingFileStore
{
    private $state;
    private $dirty = false;

    public function __construct(array $state)
    {
        $this->state = $state;
    }

    public function isDirty()
    {
        return $this->dirty;
    }

    public function state()
    {
        return $this->state;
    }

    public function get($userId)
    {
        $userId = (string) $userId;
        if (!isset($this->state['subscriptions'][$userId]) || !is_array($this->state['subscriptions'][$userId])) {
            return null;
        }
        return $this->state['subscriptions'][$userId];
    }

    public function findByCustomer($customerId)
    {
        $customerId = (string) $customerId;
        if ($customerId === '' || !isset($this->state['byCustomer'][$customerId])) {
            return null;
        }
        return (string) $this->state['byCustomer'][$customerId];
    }

    public function findBySubscription($subscriptionId)
    {
        $subscriptionId = (string) $subscriptionId;
        if ($subscriptionId === '' || !isset($this->state['bySubscription'][$subscriptionId])) {
            return null;
        }
        return (string) $this->state['bySubscription'][$subscriptionId];
    }

    public function eventSeen($eventId)
    {
        return isset($this->state['events'][(string) $eventId]);
    }

    public function putEvent($eventId, $type)
    {
        $this->state['events'][(string) $eventId] = [
            'eventId' => (string) $eventId,
            'type' => (string) $type,
            'processedAt' => gmdate('c'),
        ];
        $this->dirty = true;
    }

    public function put(array $record)
    {
        $userId = (string) $record['userId'];
        $prev = isset($this->state['subscriptions'][$userId]) ? $this->state['subscriptions'][$userId] : null;
        if (is_array($prev)) {
            if (!empty($prev['stripeCustomerId'])) {
                unset($this->state['byCustomer'][$prev['stripeCustomerId']]);
            }
            if (!empty($prev['stripeSubscriptionId'])) {
                unset($this->state['bySubscription'][$prev['stripeSubscriptionId']]);
            }
        }
        $this->state['subscriptions'][$userId] = $record;
        if (!empty($record['stripeCustomerId'])) {
            $this->state['byCustomer'][(string) $record['stripeCustomerId']] = $userId;
        }
        if (!empty($record['stripeSubscriptionId'])) {
            $this->state['bySubscription'][(string) $record['stripeSubscriptionId']] = $userId;
        }
        $this->dirty = true;
    }
}

class KpiV1BillingMysqlStore
{
    private $pdo;

    public function __construct(PDO $pdo)
    {
        $this->pdo = $pdo;
    }

    public function get($userId)
    {
        $stmt = $this->pdo->prepare(
            'SELECT user_id, stripe_customer_id, stripe_subscription_id, stripe_price_id, subscription_status,
                    cancel_at_period_end, current_period_end, entitlement_granted, checkout_session_id,
                    last_invoice_status, last_event_id, updated_at
             FROM kpi_stripe_subscriptions WHERE user_id = ? LIMIT 1 FOR UPDATE'
        );
        $stmt->execute([(string) $userId]);
        $row = $stmt->fetch(PDO::FETCH_ASSOC);
        if (!$row) {
            return null;
        }
        return $this->rowToRecord($row);
    }

    public function findByCustomer($customerId)
    {
        $customerId = (string) $customerId;
        if ($customerId === '') {
            return null;
        }
        $stmt = $this->pdo->prepare(
            'SELECT user_id FROM kpi_stripe_subscriptions WHERE stripe_customer_id = ? LIMIT 1'
        );
        $stmt->execute([$customerId]);
        $row = $stmt->fetch(PDO::FETCH_ASSOC);
        return $row ? (string) $row['user_id'] : null;
    }

    public function findBySubscription($subscriptionId)
    {
        $subscriptionId = (string) $subscriptionId;
        if ($subscriptionId === '') {
            return null;
        }
        $stmt = $this->pdo->prepare(
            'SELECT user_id FROM kpi_stripe_subscriptions WHERE stripe_subscription_id = ? LIMIT 1'
        );
        $stmt->execute([$subscriptionId]);
        $row = $stmt->fetch(PDO::FETCH_ASSOC);
        return $row ? (string) $row['user_id'] : null;
    }

    public function eventSeen($eventId)
    {
        $stmt = $this->pdo->prepare('SELECT event_id FROM kpi_stripe_events WHERE event_id = ? LIMIT 1 FOR UPDATE');
        $stmt->execute([(string) $eventId]);
        return (bool) $stmt->fetch(PDO::FETCH_ASSOC);
    }

    public function putEvent($eventId, $type)
    {
        $stmt = $this->pdo->prepare(
            'INSERT INTO kpi_stripe_events (event_id, event_type, processed_at) VALUES (?, ?, ?)'
        );
        $stmt->execute([(string) $eventId, (string) $type, gmdate('Y-m-d H:i:s')]);
    }

    public function put(array $record)
    {
        $period = null;
        if (!empty($record['currentPeriodEnd'])) {
            $period = gmdate('Y-m-d H:i:s', strtotime((string) $record['currentPeriodEnd']) ?: time());
        }
        $stmt = $this->pdo->prepare(
            'INSERT INTO kpi_stripe_subscriptions (
                user_id, stripe_customer_id, stripe_subscription_id, stripe_price_id, subscription_status,
                cancel_at_period_end, current_period_end, entitlement_granted, checkout_session_id,
                last_invoice_status, last_event_id, updated_at
             ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
             ON DUPLICATE KEY UPDATE
                stripe_customer_id = VALUES(stripe_customer_id),
                stripe_subscription_id = VALUES(stripe_subscription_id),
                stripe_price_id = VALUES(stripe_price_id),
                subscription_status = VALUES(subscription_status),
                cancel_at_period_end = VALUES(cancel_at_period_end),
                current_period_end = VALUES(current_period_end),
                entitlement_granted = VALUES(entitlement_granted),
                checkout_session_id = VALUES(checkout_session_id),
                last_invoice_status = VALUES(last_invoice_status),
                last_event_id = VALUES(last_event_id),
                updated_at = VALUES(updated_at)'
        );
        $stmt->execute([
            (string) $record['userId'],
            $record['stripeCustomerId'] !== null && $record['stripeCustomerId'] !== '' ? (string) $record['stripeCustomerId'] : null,
            $record['stripeSubscriptionId'] !== null && $record['stripeSubscriptionId'] !== '' ? (string) $record['stripeSubscriptionId'] : null,
            $record['stripePriceId'] !== null && $record['stripePriceId'] !== '' ? (string) $record['stripePriceId'] : null,
            $record['subscriptionStatus'] !== null && $record['subscriptionStatus'] !== '' ? (string) $record['subscriptionStatus'] : null,
            !empty($record['cancelAtPeriodEnd']) ? 1 : 0,
            $period,
            !empty($record['entitlementGranted']) ? 1 : 0,
            $record['checkoutSessionId'] !== null && $record['checkoutSessionId'] !== '' ? (string) $record['checkoutSessionId'] : null,
            $record['lastInvoiceStatus'] !== null && $record['lastInvoiceStatus'] !== '' ? (string) $record['lastInvoiceStatus'] : null,
            $record['lastEventId'] !== null && $record['lastEventId'] !== '' ? (string) $record['lastEventId'] : null,
            gmdate('Y-m-d H:i:s'),
        ]);
    }

    private function rowToRecord(array $row)
    {
        $period = null;
        if (!empty($row['current_period_end'])) {
            $period = gmdate('c', strtotime($row['current_period_end'] . ' UTC') ?: time());
        }
        return [
            'userId' => (string) $row['user_id'],
            'stripeCustomerId' => $row['stripe_customer_id'] !== null ? (string) $row['stripe_customer_id'] : null,
            'stripeSubscriptionId' => $row['stripe_subscription_id'] !== null ? (string) $row['stripe_subscription_id'] : null,
            'stripePriceId' => $row['stripe_price_id'] !== null ? (string) $row['stripe_price_id'] : null,
            'subscriptionStatus' => $row['subscription_status'] !== null ? (string) $row['subscription_status'] : null,
            'cancelAtPeriodEnd' => !empty($row['cancel_at_period_end']),
            'currentPeriodEnd' => $period,
            'entitlementGranted' => !empty($row['entitlement_granted']),
            'checkoutSessionId' => $row['checkout_session_id'] !== null ? (string) $row['checkout_session_id'] : null,
            'lastInvoiceStatus' => $row['last_invoice_status'] !== null ? (string) $row['last_invoice_status'] : null,
            'lastEventId' => $row['last_event_id'] !== null ? (string) $row['last_event_id'] : null,
            'updatedAt' => !empty($row['updated_at']) ? gmdate('c', strtotime($row['updated_at'] . ' UTC') ?: time()) : null,
        ];
    }
}
