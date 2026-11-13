// Pure helpers for the demo-request endpoint: validation and MIME building. No Cloudflare imports, so Node can test it.
export const MAX_BODY = 450000;          // bytes of JSON accepted
export const MAX_LOGO = 300000;          // chars of logo data URL accepted
const INDUSTRIES = ['Distribution', 'Retail', 'Janitorial', 'Manufacturing', 'Food and beverage', 'Construction', 'Professional services', 'Ecommerce', 'Other'];
const HEX = /^#[0-9a-f]{6}$/i;
const LOGO = /^data:image\/(png|jpeg|webp);base64,([A-Za-z0-9+/=]+)$/;

const s = (v, n) => (typeof v === 'string' ? v.replace(/[\u0000-\u0008\u000b\u000c\u000e-\u001f]/g, '').trim().slice(0, n) : '');
const line = (v) => v.replace(/[\r\n]+/g, ' ');                     // header-safe
const esc = (v) => v.replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const b64 = (bytes) => { let o = ''; for (let i = 0; i < bytes.length; i += 0x8000) o += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000)); return btoa(o); };
const utf8b64 = (str) => b64(new TextEncoder().encode(str));
const wrap = (x) => x.replace(/.{1,76}/g, '$&\r\n').trimEnd();
const encWord = (str) => (/^[\x20-\x7e]*$/.test(str) ? str : '=?UTF-8?B?' + utf8b64(str) + '?=');

// Returns {ok:true, lead} or {ok:false, error}. Honeypot hits return {ok:true, spam:true} so bots see success.
export function parseLead(raw) {
  if (!raw || typeof raw !== 'object') return { ok: false, error: 'bad request' };
  if (s(raw.hp, 50)) return { ok: true, spam: true };
  if (typeof raw.t === 'number' && raw.t < 2500) return { ok: true, spam: true };   // filled in under 2.5s: a bot
  const lead = {
    name: s(raw.name, 80), email: s(raw.email, 120), business: s(raw.business, 100),
    industry: INDUSTRIES.includes(s(raw.industry, 40)) ? s(raw.industry, 40) : 'Other',
    other: s(raw.other, 60), today: s(raw.today, 1500), preview: null, logo: null,
  };
  if (!lead.name || !lead.business) return { ok: false, error: 'Name and business are required.' };
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(lead.email)) return { ok: false, error: 'Enter a valid email address.' };
  const p = raw.preview;
  if (p && typeof p === 'object') {
    lead.preview = { name: s(p.name, 40), industry: s(p.industry, 40), accent: HEX.test(s(p.accent, 7)) ? s(p.accent, 7) : '#ffc23a', hasLogo: !!p.hasLogo };
    if (typeof raw.logo === 'string' && raw.logo.length <= MAX_LOGO) {
      const m = LOGO.exec(raw.logo);
      if (m) {
        try { const bin = atob(m[2]); const bytes = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i); lead.logo = { mime: 'image/' + m[1], ext: m[1] === 'jpeg' ? 'jpg' : m[1], bytes }; } catch (e) { /* drop bad logo */ }
      }
    }
  }
  return { ok: true, lead };
}

export function previewLink(site, p) {
  const json = JSON.stringify({ n: p.name, i: p.industry, a: p.accent });
  return site + '/?pv=' + utf8b64(json).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '') + '#preview';
}

export function buildMime({ from, to, site, lead, now = new Date(), id = crypto.randomUUID() }) {
  const rows = [['Name', lead.name], ['Email', lead.email], ['Business', lead.business], ['Industry', lead.industry + (lead.other ? ' / ' + lead.other : '')], ['Using today', lead.today || '(not given)']];
  let link = '';
  if (lead.preview) {
    const p = lead.preview; link = previewLink(site, p);
    rows.push(['Preview name', p.name || '(left blank)'], ['Preview industry', p.industry || '(default)'], ['Preview colour', p.accent], ['Preview logo', lead.logo ? 'attached' : 'none'], ['Reopen preview', link]);
  } else rows.push(['Preview', 'visitor did not use the dashboard preview']);
  const text = rows.map(([k, v]) => k + ': ' + v).join('\n') + '\n';
  const html = '<table style="font:14px/1.5 Arial,sans-serif;border-collapse:collapse">' + rows.map(([k, v]) =>
    '<tr><td style="padding:4px 14px 4px 0;color:#666;vertical-align:top">' + esc(k) + '</td><td style="padding:4px 0;white-space:pre-wrap">' + (k === 'Reopen preview' ? '<a href="' + esc(v) + '">' + esc(v) + '</a>' : esc(v)) + '</td></tr>').join('') + '</table>'
    + (lead.logo ? '<p style="margin-top:16px"><img src="cid:logo@nastaliq" alt="Visitor logo" style="max-width:160px;max-height:160px;background:#eee;padding:8px;border-radius:8px"></p>' : '');
  const bA = 'alt_' + id, bR = 'rel_' + id, CRLF = '\r\n';
  const subject = 'Demo request: ' + line(lead.business) + ' (' + line(lead.industry) + ')';
  const h = [
    'From: Nastaliq site <' + from + '>', 'To: ' + to, 'Reply-To: ' + (/^[\x20-\x7e]*$/.test(lead.name) ? '"' + line(lead.name).replace(/["\\]/g, '') + '"' : encWord(line(lead.name))) + ' <' + line(lead.email) + '>',
    'Subject: ' + encWord(subject), 'Date: ' + now.toUTCString(), 'Message-ID: <' + id + '@nastaliq.co>', 'MIME-Version: 1.0',
    'Content-Type: multipart/related; boundary="' + bR + '"',
  ];
  const parts = [
    '--' + bR, 'Content-Type: multipart/alternative; boundary="' + bA + '"', '',
    '--' + bA, 'Content-Type: text/plain; charset=utf-8', 'Content-Transfer-Encoding: base64', '', wrap(utf8b64(text)),
    '--' + bA, 'Content-Type: text/html; charset=utf-8', 'Content-Transfer-Encoding: base64', '', wrap(utf8b64(html)),
    '--' + bA + '--',
  ];
  if (lead.logo) parts.push('--' + bR, 'Content-Type: ' + lead.logo.mime + '; name="logo.' + lead.logo.ext + '"', 'Content-Transfer-Encoding: base64',
    'Content-ID: <logo@nastaliq>', 'Content-Disposition: inline; filename="logo.' + lead.logo.ext + '"', '', wrap(b64(lead.logo.bytes)));
  parts.push('--' + bR + '--', '');
  return h.join(CRLF) + CRLF + CRLF + parts.join(CRLF);
}
