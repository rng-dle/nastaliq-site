"""Build the service pages from public/index.html (header, footer, styles) plus the copy below.

Run from the repo root:  python3 scripts/build_pages.py
Writes public/styles.css, public/<slug>.html and public/sitemap.xml. Commit the output;
Cloudflare serves public/ as-is, there is no build step there.
Rule for all copy: never name the ERP platform or framework, and no city or country names.
"""
import datetime, html, json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent / "public"
SITE = "https://nastaliq.co"
ORG = {"@type": "Organization", "@id": f"{SITE}/#org", "name": "Nastaliq", "url": f"{SITE}/"}
E = html.escape

PAGES = [
  dict(slug="erp-data-migration", label="Data migration", service="ERP data migration",
    title="ERP Data Migration from Paper and Old Software | Nastaliq",
    desc="Nastaliq moves receipts, delivery notes, handwritten logs and old-software exports into your ERP, so years of history become searchable.",
    h1="Years of paper records, searchable in your ERP.",
    lede="Receipts, delivery notes, handwritten logs and exports from old software. Nastaliq brings your history into the new system, linked to the right customers, suppliers and items, so it can be searched and reported on instead of sitting in a cupboard.",
    sections=[
      ("What we bring in", "ul", ["Sales and purchase invoices, receipts and delivery notes.", "Handwritten activity logs, registers and ledgers.", "Exports and spreadsheets from your old accounting or inventory software.", "Customers, suppliers, items and opening balances."]),
      ("How a migration runs", "ol", ["A paid sample. We bring in a representative batch of your documents, so you can check the result and we can price the rest accurately.", "A price per 1,000 documents. Printed records cost less than handwritten ones, because they take less work to read and check.", "Batches, checked before import. Records come over in batches, and each batch is checked before it reaches your live system.", "No cut-off day. Your old system stays readable until you are sure everything has come across."]),
      ("Why it is worth doing", "p", ["History in the system means real reports from the first day: what each customer has bought over the years, which items move slowly, and what suppliers have charged. It also means the paper can finally be archived."]),
    ],
    faqs=[
      ("How is ERP data migration priced?", "Per 1,000 documents, after a paid sample. The sample shows what your records look like, so the price reflects how much is printed and how much is handwritten."),
      ("Can you migrate handwritten records?", "Yes. Handwritten logs, registers and receipts can be brought in. They take longer than printed documents to read and check, which is why they are priced separately after the sample."),
      ("Can you migrate from our current accounting software?", "Yes. Exports and spreadsheets from your old software are mapped into the new system, including customers, suppliers, items and opening balances."),
      ("Do we have to stop using the old system during the move?", "No. The old system stays readable until you are sure everything has come across."),
    ]),
  dict(slug="e-invoicing", label="E-invoicing", service="E-invoicing integration",
    title="E-Invoicing Integration for Your ERP | Nastaliq",
    desc="Nastaliq connects your ERP to the tax authority's e-invoicing system, so invoices are reported as they are issued and rejected ones are easy to fix.",
    h1="Invoices reported to the tax authority as you issue them.",
    lede="Where the tax authority requires e-invoicing, Nastaliq connects your ERP to it, so invoices are reported as they are issued and rejected ones are easy to find and fix.",
    sections=[
      ("How it works", "ul", ["Invoices are reported to the tax authority as they are issued, from the same system that runs your stock and accounts.", "Rejected invoices are flagged, so your team can correct them and send them again.", "Once the connection is set up, it is included in your monthly plan."]),
      ("Built country by country", "p", ["Every tax authority's e-invoicing system works differently. We build each country's connection as clients need it, and tell you up front what it takes and what it costs."]),
      ("Pricing", "p", ["A one-time fee per country for the connection, then included in your monthly plan. Every plan from Core at $400 a month includes e-invoicing."]),
    ],
    faqs=[
      ("Which e-invoicing systems do you support?", "We build each country's connection as clients need it. Tell us where you invoice and we will tell you what it takes and what it costs."),
      ("How much does e-invoicing integration cost?", "A one-time fee per country for the connection. After that it is included in your monthly plan."),
      ("What happens when the tax authority rejects an invoice?", "It is flagged in the system, so your team can correct it and send it again."),
      ("Do we need separate software for e-invoicing?", "No. The connection is built into the same ERP that runs your invoicing, stock and accounts."),
    ]),
  dict(slug="restaurant-pos", label="Point of sale", service="Restaurant and bakery point of sale",
    title="Restaurant & Bakery POS with Stock and Accounts | Nastaliq",
    desc="A fast point of sale for restaurants, cafés and bakeries, connected to your stock and accounts, with morning alerts for low stock.",
    h1="A fast till for restaurants and bakeries, tied to your stock and accounts.",
    lede="Nastaliq's point of sale is built for counters that move quickly: restaurants, fast food, cafés and bakeries. Every sale updates stock and the books in the same system, so the numbers at closing match the numbers in your accounts.",
    sections=[
      ("Built for busy counters", "ul", ["A fast, minimal till for counters with queues.", "Layouts the admin can restyle for each brand.", "Several branches on one system."]),
      ("Connected to everything else", "p", ["Sales reduce stock as they happen, so items running low show up in the morning alert before they run out. Takings go straight into your accounts, so nothing is typed in twice at the end of the day."]),
      ("Pricing", "p", ["Point of sale is part of the Scale plan at $900 a month, with unlimited users."]),
    ],
    faqs=[
      ("Does the POS work for bakeries and cafés?", "Yes. It is designed for restaurants, fast food, cafés and bakeries, where speed at the counter matters most."),
      ("Is the POS connected to inventory?", "Yes. Every sale updates stock in the same system, and morning alerts flag items running low."),
      ("Can each brand have its own look?", "Yes. The admin can restyle the till layout for each brand."),
      ("How much does the POS cost?", "Point of sale is included in the Scale plan at $900 a month, with unlimited users."),
    ]),
  dict(slug="erp-for-manufacturers", label="Manufacturing and distribution", service="ERP implementation for manufacturers and distributors",
    title="ERP for Manufacturers and Distributors | Nastaliq",
    desc="Cloud ERP for manufacturers and distributors: buying, production, stock, sales and accounts on one system, across branches and warehouses.",
    h1="One system for what you buy, make, stock and sell.",
    lede="Nastaliq sets up and runs ERP for manufacturers, distributors and retailers with several branches. Purchasing, production, warehouses, sales and accounting sit in one cloud system, configured around how your business already works.",
    sections=[
      ("What it covers", "ul", ["Purchasing and suppliers, from order to payment.", "Manufacturing, with bills of materials and production drawn from stock.", "Stock across several warehouses and branches.", "Sales, invoicing and money owed to you.", "Accounting and tax reports, set up with your accountant."]),
      ("A pilot first, then the move", "p", ["Every project starts with a pilot on one branch, one warehouse or one process, running real work. Then the rest of the business comes across with its old records, and staff learn on their own screens."]),
      ("Pricing", "p", ["The Scale plan, at $900 a month, covers several branches and manufacturing with unlimited users. Launch is a one-time $6,000 to $12,000, with about six weeks to go live."]),
    ],
    faqs=[
      ("Is this ERP suitable for manufacturers?", "Yes. The Scale plan covers manufacturing, several branches and warehouses, alongside stock, sales, purchasing and accounts."),
      ("How long does it take to go live?", "About six weeks for a standard launch, starting with a pilot on one branch, warehouse or process."),
      ("Can you bring our old records in?", "Yes. Paper records and exports from old software are migrated, priced per 1,000 documents after a paid sample."),
      ("Do you charge per user?", "No. Every plan includes unlimited users, so adding staff never changes your bill."),
    ]),
  dict(slug="erp-partner-development", label="Partner firms", service="White-label ERP development for partner firms",
    title="White-Label ERP Development for Partner Firms | Nastaliq",
    desc="White-label ERP development for partner firms: custom apps, integrations, reports and fixes, delivered to your repository. From $45 an hour.",
    h1="More projects than developers? We build under your name.",
    lede="Nastaliq works as a white-label development team for ERP partner firms. Send a scoped task or a whole backlog, and the work arrives as code in your repository, to your standards.",
    sections=[
      ("What we take on", "ul", ["Custom apps.", "Integrations with other systems.", "Print formats and reports.", "Fixes to existing customisations."]),
      ("How it works", "ol", ["You send a scoped task or a whole backlog.", "We agree a fixed price or an hourly rate before starting.", "Code arrives as a pull request you review.", "Our working day overlaps with Europe, the Gulf and Asia."]),
      ("Rates", "p", ["From $45 an hour, or a dedicated developer from $3,000 a month."]),
    ],
    faqs=[
      ("Do you work white-label?", "Yes. The work is delivered under your name, to your repository and your standards."),
      ("How do you price development work?", "A fixed price or an hourly rate, agreed before starting. Hourly work starts at $45, and a dedicated developer starts at $3,000 a month."),
      ("How is code delivered?", "As a pull request to your repository, for you to review before merging."),
      ("Which time zones do you cover?", "Our working day overlaps with Europe, the Gulf and Asia."),
    ],
    cta=("Send us a task", "Tell us what you need built.", "Send the scope, your deadline and how you like code delivered. We reply within one working day.")),
]

# ponytail: theme toggle and background dots copied from the homepage script; if those change there, change them here.
SCRIPT = """<script>
(() => {
  const root = document.documentElement, KEY = 'nq-theme', sysDark = matchMedia('(prefers-color-scheme: dark)');
  const tok = n => getComputedStyle(root).getPropertyValue(n).trim();
  const rng = seed => () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  const isDark = () => root.dataset.theme ? root.dataset.theme === 'dark' : sysDark.matches;
  const modeBtn = document.getElementById('mode'), sky = document.getElementById('sky'); let skyW = 0;
  function drawSky(force) {
    const w = innerWidth, h = innerHeight;
    if (!force && w === skyW && sky.width) return; skyW = w;
    const d = Math.min(devicePixelRatio || 1, 3); sky.width = Math.round(w * d); sky.height = Math.round(h * d);
    const g = sky.getContext('2d'); g.setTransform(d, 0, 0, d, 0, 0); g.clearRect(0, 0, w, h);
    const r = rng(21), cloud = (x, y, cx, cy) => Math.max(0, 1 - Math.hypot(x - cx * w, y - cy * h) / (0.9 * Math.max(w, h))) ** 1.8;
    g.fillStyle = tok('--dot');
    for (let i = 0, n = w * h / 70; i < n; i++) {
      const x = r() * w, y = r() * h;
      if (r() > 0.05 + 0.42 * cloud(x, y, 0.06, 0.04) + 0.42 * cloud(x, y, 0.96, 0.98)) continue;
      g.globalAlpha = 0.35 + 0.65 * r();
      if (r() < 0.04) { g.beginPath(); g.arc(x, y, 1.2 + r() * 1.2, 0, 7); g.fill(); }
      else g.fillRect(Math.round(x), Math.round(y), 1.5, 1.5);
    }
  }
  function sync() { modeBtn.setAttribute('aria-label', isDark() ? 'Switch to light mode' : 'Switch to dark mode'); drawSky(true); }
  modeBtn.addEventListener('click', () => {
    const next = isDark() ? 'light' : 'dark';
    if (next === (sysDark.matches ? 'dark' : 'light')) { delete root.dataset.theme; try { localStorage.removeItem(KEY); } catch (e) {} }
    else { root.dataset.theme = next; try { localStorage.setItem(KEY, next); } catch (e) {} }
  });
  sysDark.addEventListener('change', sync);
  new MutationObserver(sync).observe(root, { attributes: true, attributeFilter: ['data-theme'] });
  addEventListener('resize', () => drawSky()); sync();
})();
</script>"""

EXTRA_CSS = """
/* service pages */
.doc { padding-block: 32px 56px; border-top: 0; }
.doc .wrap { display: flex; flex-direction: column; gap: 20px; }
.doc h1 { font-size: clamp(1.9rem, 4.4vw, 3rem); max-width: 18em; }
.doc .lede { color: var(--muted); max-width: 38em; font-size: 1.1rem; }
.crumb { font-size: 0.9rem; color: var(--muted); }
.crumb a { color: var(--muted); }
.prose { display: flex; flex-direction: column; gap: 14px; max-width: 44em; }
.prose + .prose { margin-top: 36px; }
.prose p, .prose li { color: var(--muted); }
.prose ul, .prose ol { margin: 0; padding-left: 1.2em; display: flex; flex-direction: column; gap: 8px; }
.related ul { list-style: none; margin: 0; padding: 0; display: flex; flex-wrap: wrap; gap: 10px 28px; }
"""

def ld(page, url):
    return {"@context": "https://schema.org", "@graph": [
        {"@type": "Service", "@id": f"{url}#service", "name": page["service"], "serviceType": page["label"],
         "description": page["desc"], "url": url, "provider": ORG},
        {"@type": "FAQPage", "@id": f"{url}#faq", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in page["faqs"]]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Nastaliq", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": page["label"], "item": url}]},
    ]}

def block(kind, items):
    if kind == "p":
        return "".join(f"<p>{E(t)}</p>" for t in items)
    return f"<{kind}>" + "".join(f"<li>{E(t)}</li>" for t in items) + f"</{kind}>"

def build():
    home = (ROOT / "index.html").read_text()
    grab = lambda pat: re.search(pat, home, re.S).group(0)
    (ROOT / "styles.css").write_text(grab(r"(?<=<style>).*?(?=</style>)").strip() + "\n" + EXTRA_CSS)
    aside = grab(r'<aside class="aware".*?</aside>')
    header = re.sub(r'href="#(services|process|pricing|partners|faq)"', r'href="/#\1"', grab(r"<header>.*?</header>")).replace('href="#top"', 'href="/"')
    footer = grab(r"<footer>.*?</footer>")
    head_keep = grab(r'<meta name="theme-color".*?<link rel="apple-touch-icon"[^>]*>')
    theme_init = grab(r"<script>try\{var t=localStorage.*?</script>")
    fonts = grab(r'<link rel="preconnect" href="https://fonts.googleapis.com">.*?display=swap">')

    for p in PAGES:
        url = f"{SITE}/{p['slug']}"
        cta = p.get("cta", ("Book a walkthrough", "Show us how your business runs today.", "Write to us with what you sell, how many branches you have, and what you use now. We reply within one working day."))
        others = "".join(f'<li><a href="/{o["slug"]}">{E(o["service"])}</a></li>' for o in PAGES if o is not p)
        body = "".join(f'<div class="prose"><h2>{E(h)}</h2>{block(k, items)}</div>' for h, k, items in p["sections"])
        faqs = "".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in p["faqs"])
        doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(p['title'])}</title>
<meta name="description" content="{E(p['desc'])}">
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">
<link rel="canonical" href="{url}">
{head_keep}
{theme_init}
<meta property="og:type" content="website">
<meta property="og:site_name" content="Nastaliq">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{E(p['h1'])}">
<meta property="og:description" content="{E(p['desc'])}">
<meta property="og:image" content="{SITE}/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{json.dumps(ld(p, url), ensure_ascii=False, separators=(",", ":"))}</script>
{fonts}
<link rel="stylesheet" href="/styles.css">
</head>
<body>
<canvas id="sky" aria-hidden="true"></canvas>
{aside}
{header}
<main id="top">
  <section class="doc">
    <div class="wrap">
      <p class="crumb"><a href="/">Nastaliq</a> / {E(p['label'])}</p>
      <h1>{E(p['h1'])}</h1>
      <p class="lede">{E(p['lede'])}</p>
      <div class="cta"><a class="btn primary" href="#contact">{E(cta[0])}</a><a class="btn ghost" href="/#pricing">See all pricing</a></div>
    </div>
  </section>
  <section><div class="wrap">{body}</div></section>
  <section id="faq"><div class="wrap"><div class="head"><p class="label">FAQ</p><h2>{E(p['label'])} questions</h2></div>{faqs}</div></section>
  <section class="related"><div class="wrap"><div class="head"><p class="label">More from Nastaliq</p></div><ul>{others}</ul></div></section>
  <section id="contact">
    <div class="wrap contact">
      <p class="label">{E(cta[0])}</p>
      <h2>{E(cta[1])}</h2>
      <p class="note">{E(cta[2])}</p>
      <a class="mail" href="mailto:hello@nastaliq.co">hello@nastaliq.co</a>
    </div>
  </section>
</main>
{footer}
{SCRIPT}
</body>
</html>
"""
        (ROOT / f"{p['slug']}.html").write_text(doc)

    today = datetime.date.today().isoformat()
    urls = [f"{SITE}/"] + [f"{SITE}/{p['slug']}" for p in PAGES]
    (ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>\n" for u in urls) + "</urlset>\n")
    return urls

if __name__ == "__main__":
    for u in build():
        print(u)
