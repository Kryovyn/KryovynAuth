<?php
header('Content-Type: application/json; charset=utf-8');

$dataDir = __DIR__ . '/../data';
$cfgFile = $dataDir . '/auth_config.json';
$dbFile  = $dataDir . '/accounts.db';

if (!is_dir($dataDir)) { mkdir($dataDir, 0775, true); }
$cfg = json_decode(@file_get_contents($cfgFile), true) ?: [];
$TOKEN = $cfg['api_token'] ?? '';

if (!hash_equals($TOKEN, $_SERVER['HTTP_X_AUTH_TOKEN'] ?? '')) {
    http_response_code(403);
    exit(json_encode(['error'=>'forbidden']));
}

$db = new PDO('sqlite:' . $dbFile, null, null, [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
]);
$db->exec('PRAGMA journal_mode = WAL');
init_schema($db);

$action = $_GET['action'] ?? '';
$in = json_decode(file_get_contents('php://input'), true) ?: [];

$TTL = (int)($cfg['session_ttl'] ?? 120);
$LEN = (int)($cfg['code_length'] ?? 6);
$TRUST = (int)($cfg['trust_days'] ?? 30);
$LINK_TTL = (int)($cfg['link_code_ttl'] ?? 900);

try {
    switch ($action) {
        case 'ping':             out(['ok'=>true,'time'=>time()]);
        case 'session_start':    act_session_start($db,$in,$TTL,$LEN,$cfg);
        case 'session_verify':   act_session_verify($db,$in,$TRUST);
        case 'session_approve':  act_session_approve($db,$in);
        case 'session_deny':     act_session_deny($db,$in);
        case 'sessions_list':    act_sessions_list($db,$in);
        case 'link_start':       act_link_start($db,$in,$LINK_TTL,$cfg);
        case 'link_confirm':     act_link_confirm($db,$in);
        case 'unlink':           act_unlink($db,$in);
        case 'profile':          act_profile($db,$in,'platform');
        case 'profile_by_uuid':  act_profile($db,$in,'uuid');
        case 'devices_list':     act_devices_list($db,$in);
        case 'devices_by_uuid':  act_devices_by_uuid($db,$in);
        case 'device_revoke':    act_device_revoke($db,$in);
        case 'devices_revoke_all': act_devices_revoke_all($db,$in);
        case 'device_trust':     act_device_trust($db,$in,$TRUST);
        case 'toggle_2fa':       act_toggle_2fa($db,$in);
        case 'tfa_poll':         act_tfa_poll($db);
        case 'tfa_ack':          act_tfa_ack($db,$in);
        default:
            http_response_code(404); out(['error'=>'unknown action']);
    }
} catch (Throwable $e) {
    http_response_code(500); out(['error'=>$e->getMessage()]);
}

function out($d){ echo json_encode($d, JSON_UNESCAPED_UNICODE); exit; }

function init_schema($db) {
    $db->exec("CREATE TABLE IF NOT EXISTS accounts (id INTEGER PRIMARY KEY AUTOINCREMENT, mc_uuid TEXT UNIQUE, mc_name TEXT, tfa_enabled INT DEFAULT 0, created_at DATETIME DEFAULT CURRENT_TIMESTAMP, last_login DATETIME)");
    $db->exec("CREATE TABLE IF NOT EXISTS links (id INTEGER PRIMARY KEY AUTOINCREMENT, mc_uuid TEXT, platform TEXT, platform_id TEXT, platform_tag TEXT, linked_at DATETIME DEFAULT CURRENT_TIMESTAMP, UNIQUE(platform, platform_id), UNIQUE(mc_uuid, platform))");
    $db->exec("CREATE TABLE IF NOT EXISTS sessions (id INTEGER PRIMARY KEY AUTOINCREMENT, mc_uuid TEXT, mc_name TEXT, ip TEXT, fingerprint TEXT, code TEXT, platform TEXT, status TEXT DEFAULT 'pending', created_at DATETIME DEFAULT CURRENT_TIMESTAMP, expires_at DATETIME)");
    $db->exec("CREATE TABLE IF NOT EXISTS devices (id INTEGER PRIMARY KEY AUTOINCREMENT, mc_uuid TEXT, fingerprint TEXT, name TEXT, ip TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP, expires_at DATETIME, UNIQUE(mc_uuid, fingerprint))");
    $db->exec("CREATE TABLE IF NOT EXISTS link_codes (code TEXT PRIMARY KEY, mc_uuid TEXT, mc_name TEXT, platform TEXT, expires_at DATETIME, used INT DEFAULT 0)");
    $db->exec("CREATE TABLE IF NOT EXISTS tfa_pending (id INTEGER PRIMARY KEY AUTOINCREMENT, mc_uuid TEXT, mc_name TEXT, platform TEXT, chat_id TEXT, code TEXT, sent INT DEFAULT 0, expires_at DATETIME)");
}

function act_session_start($db, $in, $ttl, $len, $cfg) {
    $uuid = $in['uuid'] ?? ''; $name = $in['name'] ?? '';
    $fp = $in['fingerprint'] ?? ''; $requested = $in['platform'] ?? 'auto';
    if (!$uuid || !$name) out(['error'=>'uuid, name required']);

    if ($fp) {
        $d = $db->prepare('SELECT id, expires_at FROM devices WHERE mc_uuid=? AND fingerprint=?');
        $d->execute([$uuid, $fp]);
        if ($dev = $d->fetch()) {
            if (!$dev['expires_at'] || strtotime($dev['expires_at']) > time()) {
                out(['ok'=>true, 'trusted'=>true]);
            } else {
                $db->prepare('DELETE FROM devices WHERE id=?')->execute([$dev['id']]);
            }
        }
    }

    $acc = $db->prepare('SELECT tfa_enabled FROM accounts WHERE mc_uuid=?');
    $acc->execute([$uuid]);
    if (!(int)($acc->fetchColumn() ?: 0)) {
        out(['ok'=>true, 'trusted'=>true]);
    }

    $lnk = $db->prepare('SELECT platform, platform_id, platform_tag FROM links WHERE mc_uuid=?');
    $lnk->execute([$uuid]);
    $links = $lnk->fetchAll();
    if (!$links) out(['ok'=>false, 'reason'=>'not_linked']);

    if ($requested === 'select') {
        out(['ok'=>true, 'need_platform'=>true, 'platforms'=>array_map(fn($l)=>[
            'platform'=>$l['platform'],
            'tag'=>$l['platform_tag'] ?: $l['platform_id']
        ], $links)]);
    }

    if ($requested === 'all') {
        $targets = $links;
    } elseif ($requested !== 'auto') {
        $targets = array_values(array_filter($links, fn($l)=>$l['platform']===$requested));
    } else {
        $targets = [$links[0]];
    }

    $db->prepare("UPDATE sessions SET status='expired' WHERE mc_uuid=? AND status='pending'")->execute([$uuid]);

    $code = str_pad((string)random_int(0, (10 ** $len) - 1), $len, '0', STR_PAD_LEFT);
    $exp = date('Y-m-d H:i:s', time() + $ttl);
    $csv = implode(',', array_map(fn($t)=>$t['platform'], $targets));

    $db->prepare('INSERT INTO sessions (mc_uuid, mc_name, ip, fingerprint, code, platform, expires_at) VALUES (?,?,?,?,?,?,?)')
       ->execute([$uuid, $name, $in['ip'] ?? '', $fp, $code, $csv, $exp]);
    $sid = (int)$db->lastInsertId();

    $sent = false;
    $sent_to = [];
    foreach ($targets as $t) {
        $db->prepare('INSERT INTO tfa_pending (mc_uuid, mc_name, platform, chat_id, code, expires_at) VALUES (?,?,?,?,?,?)')
           ->execute([$uuid, $name, $t['platform'], $t['platform_id'], $code, $exp]);

        $r = send_code_via_bot($t['platform'], $t['platform_id'], $code, $name, $ttl, $in['device_name'] ?? '', $cfg);
        if ($r) {
            $sent = true;
            $sent_to[] = $t['platform'];
        }
    }

    out(['ok'=>true, 'session'=>$sid, 'platform'=>$targets[0]['platform'], 'platforms_sent'=>$sent_to, 'ttl'=>$ttl, 'sent'=>$sent]);
}

function act_session_verify($db, $in, $trust) {
    $sid = (int)($in['session'] ?? 0);
    $code = (string)($in['code'] ?? '');
    $fp = $in['fingerprint'] ?? '';
    $dname = $in['device_name'] ?? '';
    if (!$sid || !$code) out(['error'=>'session, code required']);

    $s = $db->prepare('SELECT * FROM sessions WHERE id=?');
    $s->execute([$sid]);
    $sess = $s->fetch();
    if (!$sess) out(['ok'=>false, 'reason'=>'not_found']);
    if ($sess['status'] !== 'pending') out(['ok'=>false, 'reason'=>$sess['status']]);
    if (strtotime($sess['expires_at']) < time()) {
        $db->prepare("UPDATE sessions SET status='expired' WHERE id=?")->execute([$sid]);
        out(['ok'=>false, 'reason'=>'expired']);
    }
    if (!hash_equals($sess['code'], $code)) out(['ok'=>false, 'reason'=>'wrong_code']);

    $db->prepare("UPDATE sessions SET status='confirmed' WHERE id=?")->execute([$sid]);

    if (!empty($in['trust']) && $fp && $trust > 0) {
        $exp = date('Y-m-d H:i:s', time() + $trust * 86400);
        $db->prepare('INSERT OR REPLACE INTO devices (mc_uuid, fingerprint, name, ip, expires_at) VALUES (?,?,?,?,?)')
           ->execute([$sess['mc_uuid'], $fp, $dname, $sess['ip'], $exp]);
    }

    out(['ok'=>true]);
}

function act_session_approve($db, $in) {
    $sid = (int)($in['session_id'] ?? 0);
    $p = $in['platform'] ?? '';
    $pid = (string)($in['platform_id'] ?? '');
    if (!$sid || !$p || !$pid) out(['error'=>'bad_params']);

    $s = $db->prepare('SELECT s.*, l.platform_id FROM sessions s LEFT JOIN links l ON l.mc_uuid=s.mc_uuid WHERE s.id=?');
    $s->execute([$sid]);
    $sess = $s->fetch();
    if (!$sess) out(['ok'=>false, 'reason'=>'not_found']);
    if (strtotime($sess['expires_at']) < time()) out(['ok'=>false, 'reason'=>'expired']);

    $chk = $db->prepare('SELECT 1 FROM links WHERE mc_uuid=? AND platform=? AND platform_id=?');
    $chk->execute([$sess['mc_uuid'], $p, $pid]);
    if (!$chk->fetchColumn()) out(['ok'=>false, 'reason'=>'not_owner']);

    $db->prepare("UPDATE sessions SET status='confirmed' WHERE id=?")->execute([$sid]);
    out(['ok'=>true]);
}

function act_session_deny($db, $in) {
    $db->prepare("UPDATE sessions SET status='denied' WHERE id=?")->execute([(int)($in['session_id'] ?? 0)]);
    out(['ok'=>true]);
}

function act_sessions_list($db, $in) {
    $p = $in['platform'] ?? '';
    $pid = (string)($in['platform_id'] ?? '');
    $s = $db->prepare("SELECT s.id, s.mc_name, s.ip, s.device_name, s.created_at FROM sessions s JOIN links l ON l.mc_uuid=s.mc_uuid WHERE l.platform=? AND l.platform_id=? AND s.status='pending' AND s.expires_at > CURRENT_TIMESTAMP ORDER BY s.created_at DESC");
    $s->execute([$p, $pid]);
    out(['ok'=>true, 'sessions'=>$s->fetchAll()]);
}

function act_link_start($db, $in, $ttl, $cfg) {
    $uuid = $in['uuid'] ?? '';
    $name = $in['name'] ?? '';
    $p = $in['platform'] ?? 'tg';
    if (!in_array($p, ['tg','max','ds'])) out(['error'=>'bad platform']);

    $ex = $db->prepare('SELECT 1 FROM links WHERE mc_uuid=? AND platform=?');
    $ex->execute([$uuid, $p]);
    if ($ex->fetchColumn()) out(['ok'=>false, 'reason'=>'already_linked']);

    $code = strtoupper(bin2hex(random_bytes(4)));
    $exp = date('Y-m-d H:i:s', time() + $ttl);
    $db->prepare('INSERT INTO link_codes (code, mc_uuid, mc_name, platform, expires_at) VALUES (?,?,?,?,?)')
       ->execute([$code, $uuid, $name, $p, $exp]);

    out(['ok'=>true, 'code'=>$code, 'bot_url'=>$cfg["bot_{$p}_url"] ?? '', 'command'=>"/link {$code}"]);
}

function act_link_confirm($db, $in) {
    $code = strtoupper($in['code'] ?? '');
    $p = $in['platform'] ?? '';
    $pid = (string)($in['platform_id'] ?? '');
    if (!$code || !$p || !$pid) out(['error'=>'bad params']);

    $s = $db->prepare('SELECT * FROM link_codes WHERE code=? AND used=0');
    $s->execute([$code]);
    $row = $s->fetch();
    if (!$row) out(['ok'=>false, 'reason'=>'code_not_found']);
    if ($row['platform'] !== $p) out(['ok'=>false, 'reason'=>'wrong_platform']);
    if (strtotime($row['expires_at']) < time()) out(['ok'=>false, 'reason'=>'expired']);

    $ex = $db->prepare('SELECT mc_uuid FROM links WHERE platform=? AND platform_id=?');
    $ex->execute([$p, $pid]);
    $other = $ex->fetchColumn();
    if ($other && $other !== $row['mc_uuid']) out(['ok'=>false, 'reason'=>'conflict']);

    $db->prepare('DELETE FROM links WHERE mc_uuid=? AND platform=?')->execute([$row['mc_uuid'], $p]);
    $db->prepare('INSERT INTO links (mc_uuid, platform, platform_id, platform_tag) VALUES (?,?,?,?)')
       ->execute([$row['mc_uuid'], $p, $pid, $in['tag'] ?? null]);
    $db->prepare('UPDATE link_codes SET used=1 WHERE code=?')->execute([$code]);

    $acc = $db->prepare('SELECT 1 FROM accounts WHERE mc_uuid=?');
    $acc->execute([$row['mc_uuid']]);
    if (!$acc->fetchColumn()) {
        $db->prepare('INSERT INTO accounts (mc_uuid, mc_name) VALUES (?,?)')
           ->execute([$row['mc_uuid'], $row['mc_name']]);
    }

    out(['ok'=>true, 'mc_name'=>$row['mc_name']]);
}

function act_unlink($db, $in) {
    $db->prepare('DELETE FROM links WHERE platform=? AND platform_id=?')->execute([$in['platform'] ?? '', (string)($in['platform_id'] ?? '')]);
    out(['ok'=>true]);
}

function act_profile($db, $in, $by) {
    if ($by === 'platform') {
        $s = $db->prepare('SELECT mc_uuid FROM links WHERE platform=? AND platform_id=?');
        $s->execute([$in['platform'] ?? '', (string)($in['platform_id'] ?? '')]);
        $uuid = $s->fetchColumn();
    } else {
        $uuid = $in['uuid'] ?? '';
    }
    if (!$uuid) out(['ok'=>false, 'reason'=>'not_linked']);

    $a = $db->prepare('SELECT * FROM accounts WHERE mc_uuid=?');
    $a->execute([$uuid]);
    $acc = $a->fetch() ?: ['mc_uuid'=>$uuid, 'mc_name'=>'?', 'tfa_enabled'=>0];

    $dev = $db->prepare('SELECT COUNT(*) FROM devices WHERE mc_uuid=?');
    $dev->execute([$uuid]);
    $ses = $db->prepare("SELECT COUNT(*) FROM sessions WHERE mc_uuid=? AND status='pending'");
    $ses->execute([$uuid]);

    out(['ok'=>true, 'account'=>[
        'mc_uuid'=>$uuid,
        'mc_name'=>$acc['mc_name'],
        'tfa_enabled'=>(bool)$acc['tfa_enabled'],
        'linked_at'=>$acc['created_at'] ?? '—',
        'device_count'=>(int)$dev->fetchColumn(),
        'active_sessions'=>(int)$ses->fetchColumn(),
    ]]);
}

function act_devices_list($db, $in) {
    $s = $db->prepare('SELECT mc_uuid FROM links WHERE platform=? AND platform_id=?');
    $s->execute([$in['platform'] ?? '', (string)($in['platform_id'] ?? '')]);
    $uuid = $s->fetchColumn();
    if (!$uuid) out(['ok'=>false, 'reason'=>'not_linked']);
    devices_dump($db, $uuid);
}

function act_devices_by_uuid($db, $in) {
    devices_dump($db, $in['uuid'] ?? '');
}

function devices_dump($db, $uuid) {
    $s = $db->prepare('SELECT id, name, ip, created_at FROM devices WHERE mc_uuid=? ORDER BY created_at DESC');
    $s->execute([$uuid]);
    out(['ok'=>true, 'devices'=>$s->fetchAll()]);
}

function act_device_revoke($db, $in) {
    $s = $db->prepare('SELECT mc_uuid FROM links WHERE platform=? AND platform_id=?');
    $s->execute([$in['platform'] ?? '', (string)($in['platform_id'] ?? '')]);
    $uuid = $s->fetchColumn();
    if (!$uuid) out(['ok'=>false, 'reason'=>'not_linked']);
    $db->prepare('DELETE FROM devices WHERE id=? AND mc_uuid=?')->execute([(int)($in['device_id'] ?? 0), $uuid]);
    out(['ok'=>true]);
}

function act_devices_revoke_all($db, $in) {
    $db->prepare('DELETE FROM devices WHERE mc_uuid=?')->execute([$in['uuid'] ?? '']);
    out(['ok'=>true]);
}

function act_device_trust($db, $in, $def) {
    $uuid = $in['uuid'] ?? '';
    $fp = $in['fingerprint'] ?? '';
    $days = (int)($in['days'] ?? $def);
    if (!$uuid || !$fp) out(['ok'=>false, 'reason'=>'bad_params']);
    if ($days <= 0 || $days > 365) $days = $def;
    $exp = date('Y-m-d H:i:s', time() + $days * 86400);
    $db->prepare('INSERT OR REPLACE INTO devices (mc_uuid, fingerprint, name, ip, expires_at) VALUES (?,?,?,?,?)')
       ->execute([$uuid, $fp, $in['device_name'] ?? '', $_SERVER['REMOTE_ADDR'] ?? '', $exp]);
    out(['ok'=>true, 'days'=>$days]);
}

function act_toggle_2fa($db, $in) {
    $s = $db->prepare('SELECT mc_uuid FROM links WHERE platform=? AND platform_id=?');
    $s->execute([$in['platform'] ?? '', (string)($in['platform_id'] ?? '')]);
    $uuid = $s->fetchColumn();
    if (!$uuid) out(['ok'=>false, 'reason'=>'not_linked']);
    $db->prepare('UPDATE accounts SET tfa_enabled=? WHERE mc_uuid=?')->execute([!empty($in['enabled']) ? 1 : 0, $uuid]);
    out(['ok'=>true]);
}

function act_tfa_poll($db) {
    $s = $db->query("SELECT id, mc_name, platform, chat_id, code FROM tfa_pending WHERE sent=0 AND expires_at > datetime('now') ORDER BY id LIMIT 20");
    out(['ok'=>true, 'items'=>$s->fetchAll()]);
}

function act_tfa_ack($db, $in) {
    $db->prepare('UPDATE tfa_pending SET sent=1 WHERE id=?')->execute([(int)($in['id'] ?? 0)]);
    out(['ok'=>true]);
}

function send_code_via_bot($platform, $chatId, $code, $name, $ttl, $device, $cfg) {
    $proxy = $cfg['bot_api_proxy'][$platform] ?? '';
    $tok = $cfg['bot_tokens'][$platform] ?? '';
    if (!$proxy || !$tok) return false;

    if ($platform === 'tg') {
        $text = "🔐 <b>Kryovyn Auth</b>\n\nНик: <b>" . htmlspecialchars($name, ENT_QUOTES, 'UTF-8') . "</b>\n"
              . ($device ? "Устройство: <code>" . htmlspecialchars($device, ENT_QUOTES, 'UTF-8') . "</code>\n" : '')
              . "Код: <code>{$code}</code>\n\nВведи: <code>/knlogin {$code}</code>";
        $url = rtrim($proxy, '/') . "/bot{$tok}/sendMessage";
        $payload = ['chat_id'=>$chatId, 'text'=>$text, 'parse_mode'=>'HTML'];
    } elseif ($platform === 'ds') {
        $text = "**🔐 Kryovyn Auth**\n\nНик: **{$name}**\n"
              . ($device ? "Устройство: `{$device}`\n" : '')
              . "Код: `{$code}`\n\nВведи: `/knlogin {$code}`";
        $url = rtrim($proxy, '/') . "/dm";
        $payload = ['user_id'=>$chatId, 'content'=>$text];
    } else {
        return false;
    }

    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_POST => true,
        CURLOPT_POSTFIELDS => json_encode($payload, JSON_UNESCAPED_UNICODE),
        CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => 8,
    ]);
    $r = curl_exec($ch);
    curl_close($ch);
    $d = json_decode((string)$r, true);
    return !empty($d['ok']);
}
