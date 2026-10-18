export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const botToken = env.DISCORD_BOT_TOKEN;

    if (!botToken) {
      return json({ ok: false, error: 'no_bot_token' }, 500);
    }

    if (url.pathname === '/dm') {
      try {
        const body = await request.json();
        const userId = String(body.user_id || '');
        const content = String(body.content || '');
        if (!userId || !content) return json({ ok: false, error: 'bad_params' });

        const dmResp = await fetch('https://discord.com/api/v10/users/@me/channels', {
          method: 'POST',
          headers: {
            'Authorization': `Bot ${botToken}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ recipient_id: userId }),
        });
        if (!dmResp.ok) return json({ ok: false, error: 'dm_open_failed', status: dmResp.status }, 400);

        const dm = await dmResp.json();
        const msgResp = await fetch(`https://discord.com/api/v10/channels/${dm.id}/messages`, {
          method: 'POST',
          headers: {
            'Authorization': `Bot ${botToken}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ content }),
        });
        const txt = await msgResp.text();
        return json({ ok: msgResp.ok, status: msgResp.status, body: txt }, 200);
      } catch (e) {
        return json({ ok: false, error: String(e) }, 500);
      }
    }

    if (url.pathname === '/register') {
      const appId = env.DISCORD_APP_ID;
      if (!appId) return json({ ok: false, error: 'no_app_id' }, 500);

      const commands = [
        { name: 'link', description: 'Link MC account', options: [
          { name: 'code', description: 'Code', type: 3, required: true }
        ]},
        { name: 'profile', description: 'Profile' },
        { name: 'devices', description: 'Devices' },
        { name: '2fa', description: '2FA', options: [
          { name: 'action', description: 'on/off', type: 3, required: true, choices: [
            { name: 'On', value: 'on' }, { name: 'Off', value: 'off' }
          ]}
        ]},
        { name: 'unlink', description: 'Unlink' },
        { name: 'help', description: 'Help' },
      ];

      const resp = await fetch(`https://discord.com/api/v10/applications/${appId}/commands`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bot ${botToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(commands),
      });
      const txt = await resp.text();
      return json({ ok: resp.ok, status: resp.status, body: txt }, 200);
    }

    return json({ ok: false, error: 'not_found' }, 404);
  }
};

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}
