import { EmailMessage } from 'cloudflare:email';
import { MAX_BODY, parseLead, buildMime } from './lead.js';

const SITE = 'https://nastaliq.co';
const json = (o, status = 200) => new Response(JSON.stringify(o), { status, headers: { 'content-type': 'application/json', 'cache-control': 'no-store' } });
const allowed = (origin) => { try { const h = new URL(origin).hostname; return h === 'nastaliq.co' || h === 'www.nastaliq.co' || h.endsWith('.workers.dev') || h === 'localhost'; } catch (e) { return false; } };

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    if (url.pathname !== '/api/lead') return env.ASSETS.fetch(req);
    if (req.method !== 'POST') return json({ error: 'method not allowed' }, 405);
    if (!allowed(req.headers.get('origin') || '')) return json({ error: 'forbidden' }, 403);
    if (!(req.headers.get('content-type') || '').includes('application/json')) return json({ error: 'bad request' }, 415);
    const text = await req.text();
    if (text.length > MAX_BODY) return json({ error: 'Logo too large.' }, 413);
    let raw; try { raw = JSON.parse(text); } catch (e) { return json({ error: 'bad request' }, 400); }
    const r = parseLead(raw);
    if (!r.ok) return json({ error: r.error }, 400);
    if (r.spam) return json({ ok: true });
    if (!env.LEAD_TO) return json({ error: 'Not configured.' }, 500);
    const from = env.LEAD_FROM || 'leads@nastaliq.co';
    try {
      await env.MAIL.send(new EmailMessage(from, env.LEAD_TO, buildMime({ from, to: env.LEAD_TO, site: SITE, lead: r.lead })));
    } catch (e) {
      console.error('lead email failed', String(e));
      return json({ error: 'Could not send. Please email hello@nastaliq.co.' }, 502);
    }
    const { logo, ...rest } = r.lead;
    console.log('lead', JSON.stringify({ ...rest, logo: !!logo }));   // structured log, ready to feed Frappe later
    return json({ ok: true });
  },
};
