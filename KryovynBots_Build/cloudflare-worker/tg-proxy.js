export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const target = 'https://api.telegram.org' + url.pathname + url.search;
    try {
      const resp = await fetch(new Request(target, {
        method: request.method,
        headers: request.headers,
        body: request.body,
      }));
      return new Response(resp.body, { status: resp.status, headers: resp.headers });
    } catch (e) {
      return new Response(JSON.stringify({ ok: false, error: 'proxy_failed' }), {
        status: 502,
        headers: { 'Content-Type': 'application/json' },
      });
    }
  }
};
