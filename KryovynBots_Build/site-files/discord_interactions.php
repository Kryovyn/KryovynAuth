<?php
header('Content-Type: application/json; charset=utf-8');

$cfg = json_decode(@file_get_contents(__DIR__ . '/../data/auth_config.json'), true) ?: [];
$PUBLIC_KEY = $cfg['discord_public_key'] ?? '';
$API_URL = $cfg['api_url'] ?? '';
$API_TOKEN = $cfg['api_token'] ?? '';

if (!$PUBLIC_KEY) {
    http_response_code(500);
    exit(json_encode(['error'=>'discord_public_key not set']));
}

$sig = $_SERVER['HTTP_X_SIGNATURE_ED25519'] ?? '';
$ts  = $_SERVER['HTTP_X_SIGNATURE_TIMESTAMP'] ?? '';
$body = file_get_contents('php://input');

if (!$sig || !$ts) {
    http_response_code(401);
    exit(json_encode(['error'=>'missing signature']));
}

$ok = @sodium_crypto_sign_verify_detached(
    hex2bin($sig),
    $ts . $body,
    hex2bin($PUBLIC_KEY)
);
if (!$ok) {
    http_response_code(401);
    exit(json_encode(['error'=>'invalid signature']));
}

$in = json_decode($body, true) ?: [];
$type = $in['type'] ?? 0;

if ($type === 1) {
    echo json_encode(['type'=>1]);
    exit;
}

if ($type !== 2) {
    echo json_encode(['type'=>4, 'data'=>['content'=>'Unknown','flags'=>64]]);
    exit;
}

$command = $in['data']['name'] ?? '';
$options = $in['data']['options'] ?? [];
$userId = $in['member']['user']['id'] ?? ($in['user']['id'] ?? '');
$userTag = $in['member']['user']['username'] ?? 'user';

$opt = [];
foreach ($options as $o) {
    $opt[$o['name']] = $o['value'] ?? null;
}

function call_api($action, $payload, $url, $token) {
    $ch = curl_init($url . '?action=' . urlencode($action));
    curl_setopt_array($ch, [
        CURLOPT_POST => true,
        CURLOPT_POSTFIELDS => json_encode($payload, JSON_UNESCAPED_UNICODE),
        CURLOPT_HTTPHEADER => ['Content-Type: application/json', 'X-Auth-Token: ' . $token],
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => 8,
    ]);
    $r = curl_exec($ch);
    curl_close($ch);
    $d = json_decode((string)$r, true);
    return is_array($d) ? $d : ['ok'=>false, 'error'=>'api error'];
}

function reply($content, $ephemeral = true) {
    echo json_encode([
        'type'=>4,
        'data'=>[
            'content'=>$content,
            'flags'=>$ephemeral ? 64 : 0,
        ],
    ]);
    exit;
}

function embed_reply($embed, $ephemeral = true) {
    echo json_encode([
        'type'=>4,
        'data'=>[
            'embeds'=>[$embed],
            'flags'=>$ephemeral ? 64 : 0,
        ],
    ]);
    exit;
}

switch ($command) {
    case 'link':
        $code = strtoupper(trim($opt['code'] ?? ''));
        if (!$code) reply('❌ Не указан код.');
        $r = call_api('link_confirm', [
            'code' => $code,
            'platform' => 'ds',
            'platform_id' => (string)$userId,
            'tag' => $userTag,
        ], $API_URL, $API_TOKEN);

        if (!empty($r['ok'])) {
            embed_reply([
                'title' => '✅ Аккаунт привязан',
                'description' => 'Minecraft: **' . ($r['mc_name'] ?? '?') . '**',
                'color' => 0xA855F7,
            ]);
        }
        $msgs = [
            'code_not_found' => '❌ Код не найден.',
            'wrong_platform' => '❌ Код для другой платформы.',
            'expired' => '❌ Код истёк.',
            'conflict' => '❌ Этот Discord уже привязан.',
        ];
        reply($msgs[$r['reason'] ?? ''] ?? '❌ Ошибка');

    case 'profile':
        $r = call_api('profile', [
            'platform' => 'ds',
            'platform_id' => (string)$userId,
        ], $API_URL, $API_TOKEN);

        if (empty($r['ok'])) reply('Аккаунт не привязан. /link');
        $a = $r['account'];

        embed_reply([
            'title' => '🛡 Профиль',
            'color' => 0xA855F7,
            'fields' => [
                ['name'=>'Ник', 'value'=>$a['mc_name'] ?? '?', 'inline'=>true],
                ['name'=>'2FA', 'value'=>!empty($a['tfa_enabled']) ? '🟢 вкл' : '🔴 выкл', 'inline'=>true],
                ['name'=>'Устройств', 'value'=>(string)($a['device_count'] ?? 0), 'inline'=>true],
                ['name'=>'Сессий', 'value'=>(string)($a['active_sessions'] ?? 0), 'inline'=>true],
            ],
        ]);

    case 'devices':
        $r = call_api('devices_list', [
            'platform' => 'ds',
            'platform_id' => (string)$userId,
        ], $API_URL, $API_TOKEN);

        $devs = $r['devices'] ?? [];
        if (!$devs) reply('📱 Нет устройств.');

        $fields = [];
        foreach (array_slice($devs, 0, 10) as $d) {
            $fields[] = [
                'name' => '#' . $d['id'] . ' ' . mb_substr($d['name'] ?? '?', 0, 50),
                'value' => 'IP: `' . ($d['ip'] ?? '?') . '`',
                'inline' => false,
            ];
        }
        embed_reply(['title'=>'📱 Устройства','color'=>0xA855F7,'fields'=>$fields]);

    case '2fa':
        $enable = ($opt['action'] ?? '') === 'on';
        $r = call_api('toggle_2fa', [
            'platform' => 'ds',
            'platform_id' => (string)$userId,
            'enabled' => $enable,
        ], $API_URL, $API_TOKEN);

        reply(!empty($r['ok']) ? ('🔐 2FA ' . ($enable ? 'включена' : 'выключена') . '.') : '❌ Ошибка.');

    case 'unlink':
        $r = call_api('unlink', [
            'platform' => 'ds',
            'platform_id' => (string)$userId,
        ], $API_URL, $API_TOKEN);
        reply(!empty($r['ok']) ? '✅ Отвязано.' : '❌ Ошибка.');

    case 'help':
        embed_reply([
            'title' => '❓ Помощь',
            'description' => 'Привязка: в игре `/knlink ds` → код → сюда `/link КОД`',
            'color' => 0xA855F7,
        ]);

    default:
        reply('❌ Неизвестная команда.');
}
