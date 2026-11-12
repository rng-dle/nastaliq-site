#!/usr/bin/env python3
"""Builds Nastaliq's static pages into public/. Run: python3 tools/build_site.py
- Generates products, company, contact, articles index and article pages, industry pages and legal pages.
- Rewrites the <head> (SEO/AEO metadata, JSON-LD), header, footer and FAQ block of the hand-kept tools/home.tpl.html into public/index.html.
- Writes sitemap.xml, robots.txt, llms.txt and _redirects.
Pricing never appears on the site: prices go out by email only. The site is English only."""
import datetime, html, json, os, posixpath, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content_en import ARTS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB = os.path.join(ROOT, 'public')
SITE = 'https://nastaliq.co'
TODAY = '2026-10-26'
EMAIL = 'hello@nastaliq.co'
REG_NO = '0361484'   # SECP LLP incorporation number (certificate dated 16 October 2026)
REG_URL = 'https://leap.secp.gov.pk/#/verify-company-info/' + REG_NO
LEGAL_DATE = '2026-11-12'
UPDATED = '2026-11-12'   # sitemap lastmod; bump when pages change
# Article author. None = "the Nastaliq team". To name a person:
# AUTHOR = dict(name='Full Name', role='Partner, Nastaliq LLP', url='https://www.linkedin.com/in/...')
AUTHOR = None
PUBLISHED = {'outgrowing-spreadsheets-and-accounting-software': '2026-11-11', 'how-to-choose-an-erp': '2026-11-11', 'private-cloud-erp-vs-saas-vs-on-premise': '2026-11-11',
             'multilingual-erp-software': '2026-11-12', 'erp-implementation-checklist': '2026-11-12', 'erp-cost-what-drives-the-price': '2026-11-12',
             'inventory-management-software-buyers-guide': '2026-11-12', 'erp-data-migration-guide': '2026-11-12'}   # any other article uses TODAY
# Company social profiles, shown in the footer and emitted as schema sameAs. A blank URL hides that link.
SOCIAL = [('LinkedIn', ''), ('Instagram', '')]
SAME_AS = [u for _, u in SOCIAL if u]
FONT = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=Figtree:wght@400;500;600;700&display=swap">')

def x(s): return html.escape(s, quote=True)
def nice_date(iso): d = datetime.date.fromisoformat(iso); return '%s %d, %d' % (d.strftime('%B'), d.day, d.year)

# ---------------------------------------------------------------- shared data
ORG = {
    '@type': 'Organization', '@id': SITE + '/#org', 'name': 'Nastaliq', 'legalName': 'Nastaliq LLP', 'alternateName': ['Nastaliq LLP', 'Nastaliq ERP'], 'url': SITE + '/',
    'disambiguatingDescription': 'Software company that builds and hosts a cloud ERP for businesses in North America.',
    'logo': SITE + '/img/mark.svg', 'email': EMAIL, 'foundingDate': '2026-10-16',
    'identifier': {'@type': 'PropertyValue', 'propertyID': 'SECP LLP Incorporation No.', 'value': REG_NO},
    'description': 'Nastaliq builds and hosts private cloud ERP for growing businesses in North America: inventory, purchasing, sales and accounting in one system, with each client on its own dedicated server, in the language your team works in.',
    'address': {'@type': 'PostalAddress', 'addressLocality': 'Lahore', 'addressCountry': 'PK'},
    'areaServed': ['CA', 'US'],
    'contactPoint': {'@type': 'ContactPoint', 'contactType': 'sales', 'email': EMAIL, 'availableLanguage': 'English'},
}
if SAME_AS: ORG['sameAs'] = SAME_AS
WEBSITE = {'@type': 'WebSite', '@id': SITE + '/#website', 'url': SITE + '/', 'name': 'Nastaliq', 'inLanguage': 'en', 'publisher': {'@id': SITE + '/#org'}}

PRODUCTS = [
    ('suite', 'Business suite',
     'Inventory, purchasing, accounting and sales in one cloud system, implemented for your business and hosted by us.',
     ['Inventory: receive, transfer and count stock, with barcode scanning from a phone',
      'Purchasing: purchase orders, receiving and supplier bills in one flow',
      'Sales: sales orders, invoices and customer-specific prices',
      'Accounting: books that follow every sale and purchase',
      'Your own dedicated server, with your name and logo on the login']),
    ('janitorial', 'Janitorial operations',
     'Run a commercial cleaning company from one app, for cleaners, supervisors and clients.',
     ['Time clock with GPS geofencing', 'Inspections and checklists with photo proof', 'Client portal and messaging', 'Supplies and job profitability']),
    ('owner', 'Owner dashboard and alerts',
     'A home screen by role, phone-friendly stock screens, and a morning email digest of what needs attention.',
     ['Owner, sales, warehouse and accountant each land on their own tasks', 'Morning email: sales, low stock and overdue bills', 'Owner metrics, down to each sale']),
    ('languages', 'Every language',
     'Each user picks their own language on every screen, and documents print in the language your customer reads.',
     ['Each user picks their own language', 'Documents in your customer\'s language']),
    ('pos', 'Point of sale',
     'A clean, fast till for restaurants, fast food and bakeries.',
     ['Admin-editable colour themes', 'Built for counter speed']),
]

# FAQ shown on the home page AND emitted as FAQPage JSON-LD (text must match what is visible)
FAQ = [
    ('What is Nastaliq?',
     'Nastaliq is a private cloud ERP for growing businesses in North America, typically companies with $1M or more in annual revenue. It puts inventory, purchasing, sales and accounting in one system, on your own dedicated server, in the language your team works in. We implement it for your business and host it.'),
    ('Is our data shared with other clients?',
     'No. Every client, whatever its size, runs on its own dedicated server with its own site. Your system and data are not shared with any other company.'),
    ('How much does Nastaliq cost?',
     'Pricing is a flat monthly subscription with unlimited users, plus a one-time implementation fee. Data migration is charged separately. We send the exact plan and price by email after you tell us what you run.'),
    ('Do I need to install anything?',
     'No. Nastaliq runs in the cloud. You sign in from a browser or your phone.'),
    ('Does Nastaliq support my language?',
     'Yes. Every screen can be switched to the language your team works in, each user picks their own, and documents print in the language your customer reads.'),
    ('Can you bring my existing records in?',
     'Yes, as a paid add-on. Data migration is not part of the implementation fee. Tell us what you use today and we will say what is possible and what it costs.'),
]

# ---------------------------------------------------------------- helpers
def levels(path):
    up = '../' * path.count('/')
    return up, up   # (up to the site root, prefix for assets); kept as a pair for callers

def url_for(path):
    return SITE + '/' + ('' if path == 'index.html' else path[:-5] if path.endswith('.html') else path)

def art_cards(items, base='articles/', h='h3'):
    return ''.join('<a href="%s%s.html"><small>%s</small><%s>%s</%s><p>%s</p></a>' % (base, a['slug'], a['tag'], h, html.escape(a['title']), h, html.escape(a['desc'])) for a in items)

# ---------------------------------------------------------------- fragments
def header(path, cur='', home=False):
    up, pre = levels(path)
    def l(href, label, k=''):
        c = ' aria-current="page"' if cur == k and k else ''
        return '<a class="l" href="%s"%s>%s</a>' % (href, c, label)
    extra = (l('#sectors', 'Industries') + l('#pricing', 'Pricing')) if home else ''
    cta = '<a class="btn sm" href="%s">Book a free demo</a>' % ('#contact' if home else up + 'contact.html')
    return ('<a class="skip" href="#main">Skip to content</a><header><div class="in bar"><a class="logo" href="%sindex.html" aria-label="Nastaliq, home">'
            '<img class="mk" src="%simg/mark.svg" width="30" height="28" alt=""><img class="wd" src="%simg/wordmark.svg" width="55" height="15" alt="Nastaliq"></a>'
            '<nav id="nav" aria-label="Main">%s%s%s%s%s%s</nav>'
            '<button class="menu-btn" type="button" aria-expanded="false" aria-controls="nav" aria-label="Menu"><i></i><i></i></button></div></header>'
            % (up, pre, pre, extra, l(up + 'products.html', 'Products', 'products'), l(up + 'company.html', 'Company', 'company'),
               l(up + 'articles.html', 'Articles', 'art'), l(up + 'contact.html', 'Contact', 'contact'), cta))

def footer(path):
    up, pre = levels(path)
    home = up + 'index.html'
    def col(title, links):
        return '<div><h3>%s</h3>%s</div>' % (title, ''.join('<a href="%s">%s</a>' % l for l in links))
    social = [(u, n) for n, u in SOCIAL if u]
    company = [(up + 'company.html', 'About'), (up + 'articles.html', 'Articles'), (up + 'contact.html', 'Contact')]
    return ('<footer class="foot"><div class="in"><div class="fg"><div><a class="logo" href="%s" aria-label="Nastaliq"><img class="mk" src="%simg/mark.svg" width="32" height="30" alt=""><img class="wd" src="%simg/wordmark.svg" width="59" height="16" alt="Nastaliq"></a>'
            '<p>Private cloud ERP for growing businesses: inventory, purchasing, sales and accounting on your own dedicated server, in your language.</p>'
            '<p>Lahore, Pakistan, serving North America.</p><a href="mailto:%s">%s</a></div>%s%s%s</div>'
            '<div class="legal"><p>&copy; 2026 Nastaliq LLP. Registration No. %s. All rights reserved.</p>'
            '<p><a href="%sprivacy.html">Privacy Policy</a><i>|</i><a href="%sterms.html">Terms of Service</a></p></div></div></footer>'
            % (home, pre, pre, EMAIL, EMAIL,
               col('Product', [(up + 'products.html', 'Products'), (home + '#pricing', 'Pricing'), (home + '#faq', 'FAQ')]),
               col('Industries', [(up + 'industries/%s.html' % i['slug'], i['name']) for i in INDUSTRIES]),
               col('Company', company + social),
               REG_NO, up, up))

def head(path, title, desc, schema, og_type='website', robots='index,follow,max-image-preview:large,max-snippet:-1'):
    up, pre = levels(path)
    url = url_for(path)
    graph = {'@context': 'https://schema.org', '@graph': [ORG, WEBSITE] + schema}
    return ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
            '<title>%s</title><meta name="description" content="%s"><link rel="canonical" href="%s">'
            '<meta name="robots" content="%s"><meta name="theme-color" content="#000000">'
            '<link rel="icon" href="%sfavicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="%simg/apple-touch-icon.png">'
            '<meta property="og:site_name" content="Nastaliq"><meta property="og:locale" content="en_CA">'
            '<meta property="og:type" content="%s"><meta property="og:title" content="%s"><meta property="og:description" content="%s"><meta property="og:url" content="%s">'
            '<meta property="og:image" content="%s/img/og.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="Nastaliq: private cloud ERP for growing businesses">'
            '<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="%s"><meta name="twitter:description" content="%s"><meta name="twitter:image" content="%s/img/og.png">'
            '%s<link rel="stylesheet" href="%scss/home.css">'
            '<script type="application/ld+json">%s</script></head>'
            % (x(title), x(desc), url, robots, pre, pre, og_type, x(title), x(desc), url, SITE,
               x(title), x(desc), SITE, FONT, pre, json.dumps(graph, ensure_ascii=False, separators=(',', ':'))))

def page(path, title, desc, schema, body, cur='', og_type='website', **kw):
    up, pre = levels(path)
    return (head(path, title, desc, schema, og_type, **kw) + '<body>' + header(path, cur) + '<main id="main">' + body + '</main>'
            + footer(path) + '<script src="%sjs/home.js" defer></script></body></html>\n' % pre)

def crumbs(items):
    return {'@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': u} for i, (n, u) in enumerate(items)]}

def faq_ld(pairs):
    return {'@type': 'FAQPage', 'inLanguage': 'en', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in pairs]}

def clean(href, base):
    """relative link -> root-absolute, extensionless (Cloudflare serves foo.html at /foo and redirects /foo.html there)"""
    if not href or href.startswith(('http', 'mailto:', 'tel:', 'data:', '#', '/')): return href
    p, sep, frag = href.partition('#')
    n = posixpath.normpath(posixpath.join(base, p))
    if n == '.': n = ''
    if n == 'index.html' or n.endswith('/index.html'): n = n[:-10]
    elif n.endswith('.html'): n = n[:-5]
    return '/' + n + sep + frag

def write(path, s):
    base = posixpath.dirname(path)
    s = re.sub(r'\b(href|src)="([^"]*)"', lambda m: '%s="%s"' % (m.group(1), clean(m.group(2), base)), s)
    p = os.path.join(PUB, path); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8').write(s)

def hero(h1, lede):
    return '<section class="pagehead"><div class="in"><h1 style="max-width:20ch">%s</h1><p class="lede">%s</p></div></section>' % (h1, lede)

def pg(path, name): return (name, url_for(path))

# ---------------------------------------------------------------- shared steps
FLOW = [('Tell us what you run', 'What you sell, how many locations you have and what you use today.'),
        ('See your demo', 'We reply by email with a demo prepared for your industry, plus a plan and a price.'),
        ('We implement it', 'We configure the system for your business. Migrating your existing customers, products and records is available as a paid add-on.'),
        ('Go live', 'Your team starts working in the system. Hosting, updates and support stay with us.')]

def flow_section(title='From the first email to go-live'):
    li = ''.join('<li><h3>%s</h3><p>%s</p></li>' % step for step in FLOW)
    return '<section class="band dark"><div class="in"><div class="sh"><h2>%s</h2></div><ol class="flow">%s</ol></div></section>' % (title, li)

# ---------------------------------------------------------------- industries
MIGRATE = 'Yes, as a paid add-on. Data migration is quoted separately from the implementation fee. Tell us what you use today and we will say what is possible.'
INDUSTRIES = [
 dict(slug='distribution', name='Distribution',
      title='ERP for distribution and wholesale companies | Nastaliq',
      h1='ERP for distribution and wholesale companies',
      lede='Purchasing, receiving, stock and customer pricing in one private cloud system, implemented for distribution and hosted by us.',
      who='Built for distributors and trading companies with one or more warehouses that have outgrown spreadsheets and stand-alone accounting software.',
      feats=[('Purchase order to supplier bill', 'Raise a purchase order, receive against it and match the supplier bill, in one flow with no re-typing.'),
             ('Warehouse work on a phone', 'Receive, transfer and count stock from the floor, scanning barcodes with the phone camera.'),
             ('Customer-specific prices', 'Each customer gets the agreed price on every sales order, whoever enters it.'),
             ('Stock you can trust', 'See what is on hand and what has fallen below its reorder level, without walking the shelves.'),
             ('Books that keep up', 'Every receipt, sale and bill posts to the accounts as it happens, with unpaid and overdue bills in view.'),
             ('Morning email', "Yesterday's sales, low stock and overdue bills in the owner's inbox before the day starts.")],
      faq=[('Does it handle more than one warehouse?', 'Yes. Stock is kept by location, and transfers between locations are recorded from a phone.'),
           ('Can our existing items, customers and suppliers be migrated?', MIGRATE)]),
 dict(slug='retail', name='Retail',
      title='ERP for retail businesses | Nastaliq',
      h1='ERP for retail businesses',
      lede='Stock, purchasing, sales records and accounting in one private cloud system, implemented for retail and hosted by us.',
      who='Built for retailers with real stock to manage, across one store or several, who want the back office in one place.',
      feats=[('Sales tied to live stock', 'Each sales order reduces stock the moment it is entered, so the shelf and the system agree.'),
             ('Barcode receiving and counts', 'Receive deliveries and run cycle counts from a phone instead of a clipboard.'),
             ('Purchasing in one flow', 'Purchase orders, receiving and supplier bills connected from start to finish.'),
             ('Accounting that follows every sale', 'Sales and purchases post to the books by themselves, ready for your accountant.'),
             ('Your language', 'Each user picks a language, and documents print in the language your customer reads.'),
             ('Owner metrics', 'A home screen with the numbers that matter, down to each sale.')],
      faq=[('Is this a point-of-sale system?', 'No. Nastaliq is the system behind the counter: stock, purchasing, sales records and accounting. A dedicated point of sale is in development.'),
           ('Can it cover more than one store?', 'Yes. Stock is kept by location, and transfers between locations are recorded.'),
           ('Can our existing products and customers be migrated?', MIGRATE)]),
 dict(slug='manufacturing', name='Manufacturing',
      title='ERP for manufacturing companies | Nastaliq',
      h1='ERP for manufacturing companies',
      lede='Bills of materials, work orders, purchasing and stock in one private cloud system, with the books following every job.',
      who='Built for makers and assemblers that buy materials, turn them into finished goods and need to know what each job really costs.',
      feats=[('Bills of materials', 'Define what goes into each product, so a work order knows what to draw from stock.'),
             ('Work orders', 'Plan production, issue materials and record finished goods against each order.'),
             ('Purchasing from the plan', 'Raise purchase orders for shortfalls, receive against them and match supplier bills.'),
             ('Stock by location', 'Track raw materials, work in progress and finished goods across rooms or sites.'),
             ('True job cost', 'Material and production cost flows to the accounts, so margin is a number and not a guess.'),
             ('Floor screens on a phone', 'Receive and move stock from the shop floor by scanning barcodes.')],
      faq=[('Does it handle bills of materials?', 'Yes. Products can have a bill of materials, and work orders draw from stock against it.'),
           ('Can it track more than one location?', 'Yes. Stock is kept by location, and transfers are recorded.'),
           ('Can our existing items and orders be migrated?', MIGRATE)]),
 dict(slug='food-and-beverage', name='Food and beverage',
      title='ERP for food and beverage companies | Nastaliq',
      h1='ERP for food and beverage companies',
      lede='Stock, purchasing, sales and accounting for food and drink producers and wholesalers, with batch and expiry tracking.',
      who='Built for producers, importers and wholesalers of food and drink that need to know what came in, what went out and what is about to expire.',
      feats=[('Batch tracking', 'Record the batch on every receipt and shipment, so you can see where a lot went.'),
             ('Expiry dates', 'Keep expiry dates on stock and see what needs to move first.'),
             ('Recipes and production', 'Keep a bill of materials for each product and draw ingredients from stock when you produce.'),
             ('Purchasing and receiving', 'Purchase orders, receiving and supplier bills in one flow.'),
             ('Customer-specific prices', 'Each customer gets the agreed price on every order.'),
             ('Books that keep up', 'Sales, purchases and stock movements post to the accounts as they happen.')],
      faq=[('Can it track expiry dates?', 'Yes. Stock can carry batch numbers and expiry dates.'),
           ('Can we trace a batch?', 'Yes. Because the batch is recorded on receipts and shipments, you can follow it through the system.'),
           ('Can our existing products and customers be migrated?', MIGRATE)]),
 dict(slug='construction', name='Construction and trades',
      title='ERP for construction and trades businesses | Nastaliq',
      h1='ERP for construction and trades businesses',
      lede='Projects, purchasing, timesheets and invoicing in one private cloud system for contractors and trades businesses.',
      who='Built for contractors and trades companies that run several jobs at once and need to see what each one costs and earns.',
      feats=[('Projects and tasks', 'Keep each job, its tasks and its costs in one place.'),
             ('Timesheets', 'Record hours against jobs, so labour cost lands where it belongs.'),
             ('Purchasing per job', 'Buy materials against a job and see the cost as soon as the bill is entered.'),
             ('Job profitability', 'Compare what a job has cost with what it has earned while it is still running.'),
             ('Stock for materials', 'Track materials in the yard, the shop and the truck.'),
             ('Invoicing from the job', 'Bill customers from the job record, with the books updated as you go.')],
      faq=[('Can we see the profit on each job?', 'Yes. Costs from timesheets, purchases and stock are tied to the job, so you can compare them with what you have billed.'),
           ('Can crews use it from a phone?', 'Yes. Nastaliq runs in a browser on a phone, so crews can record time and stock movements on site.'),
           ('Can our existing customers and records be migrated?', MIGRATE)]),
 dict(slug='professional-services', name='Professional services',
      title='ERP for professional services firms | Nastaliq',
      h1='ERP for professional services firms',
      lede='Timesheets, projects, billing and accounting in one private cloud system for agencies, consultancies and firms that sell time.',
      who='Built for firms that sell expertise by the hour or by the project and want billing, time and the books to agree.',
      feats=[('Timesheets', 'Record time against clients and projects, from a desktop or a phone.'),
             ('Projects and budgets', 'Set a budget for each project and watch hours and cost against it.'),
             ('Invoicing from time', 'Turn approved time into an invoice without re-typing it.'),
             ('Expenses', 'Record expenses against the client or project they belong to.'),
             ('Accounting that follows billing', 'Invoices, payments and expenses post to the books as they happen.'),
             ('Reporting by client', 'See revenue, cost and margin for each client and project.')],
      faq=[('Do we need the inventory side?', 'No. We implement the system around projects, time and billing, and stock features can stay off.'),
           ('Can we bill by the hour and by the project?', 'Yes. You can invoice from recorded time or bill a project amount.'),
           ('Can our existing clients and projects be migrated?', MIGRATE)]),
 dict(slug='ecommerce', name='E-commerce',
      title='ERP for e-commerce businesses | Nastaliq',
      h1='ERP for e-commerce businesses',
      lede='Stock, purchasing, orders and accounting behind your online store, in one private cloud system.',
      who='Built for online sellers that have outgrown spreadsheets and need one stock number, one set of orders and books that agree.',
      feats=[('One stock number', 'Keep a single record of what you hold, across warehouses and suppliers.'),
             ('Purchasing and receiving', 'Order from suppliers, receive against the order and match the bill.'),
             ('Orders in, books out', 'Sales orders, invoices and payments post to the accounts as they happen.'),
             ('Multiple locations', 'Track stock across your own warehouse, a fulfilment partner or a shop.'),
             ('Customer pricing', 'Hold wholesale and customer-specific prices next to your retail price.'),
             ('Returns and credit notes', 'Record a return, put the stock back and issue the credit in one flow.')],
      faq=[('Does it connect to our online store?', 'Store connections are scoped during implementation. Tell us which platform you use and we will say what is possible.'),
           ('Can it handle wholesale and retail prices?', 'Yes. Customers can have their own prices alongside your standard price list.'),
           ('Can our existing products and customers be migrated?', MIGRATE)]),
 dict(slug='janitorial', name='Janitorial',
      title='Operations software for commercial cleaning | Nastaliq',
      h1='Operations software for commercial cleaning companies',
      lede='Crews, inspections, clients and supplies in one app, for cleaners, supervisors and the companies you serve.',
      who='Built for commercial cleaning companies that schedule crews across client sites and need proof that the work was done.',
      feats=[('Time clock and scheduling', 'Schedule crews by site and record hours with a time clock that uses GPS geofencing.'),
             ('Inspections and checklists', 'Checklists per site, with photo proof of the finished work.'),
             ('Client portal and messaging', 'Give each client one place to see their site and reach you.'),
             ('Supplies and job profitability', 'Track what each job uses and what it earns.')],
      faq=[('Who uses it?', 'Cleaners clock in and complete checklists, supervisors schedule and inspect, and clients follow their site through the portal.'),
           ('Can it be used from a phone?', 'Yes. Cleaners and supervisors work from a phone, including the time clock and photo checklists.')]),
]
# Industries without their own tab on the home page
OTHER_INDUSTRIES = [i['slug'] for i in INDUSTRIES if i['slug'] not in ('distribution', 'retail', 'janitorial')]
# Extra category suggestions for the "Other" box in the demo form
EXTRA_CATEGORIES = ['Agriculture', 'Automotive parts', 'Education', 'Energy', 'Furniture', 'Healthcare supplies', 'Hospitality', 'Nonprofit', 'Pharmacy', 'Printing', 'Real estate', 'Textiles', 'Wholesale']


def industries():
    for I in INDUSTRIES:
        path = 'industries/%s.html' % I['slug']
        cards = ''.join('<div class="card"><h2>%s</h2><p>%s</p></div>' % f for f in I['feats'])
        faq = ''.join('<details><summary>%s</summary><p>%s</p></details>' % (html.escape(q), html.escape(a)) for q, a in I['faq'])
        body = ('<section class="pagehead"><div class="in"><h1 style="max-width:20ch">%s</h1><p class="lede">%s</p><p><a class="btn" href="../contact.html">Book a free demo</a></p></div></section>'
                '<section class="band"><div class="in"><div class="sh"><h2>What\'s included</h2><p class="lede">%s</p></div><div class="g3 feat">%s</div></div></section>'
                % (I['h1'], I['lede'], I['who'], cards)
                + flow_section('How implementation works')
                + '<section class="band"><div class="in"><div class="sh"><h2>Common questions</h2></div><div class="faq">%s</div></div></section>' % faq
                + '<section class="band" style="padding-top:0"><div class="in"><div class="cta2"><h2>See it with your industry loaded</h2><p>Tell us what you run. We reply by email with a demo, a plan and a price.</p><a class="btn" href="../contact.html">Get in touch</a></div></div></section>')
        schema = [{'@type': 'WebPage', 'name': I['h1'], 'url': url_for(path), 'inLanguage': 'en', 'isPartOf': {'@id': SITE + '/#website'}, 'about': {'@id': SITE + '/#org'}},
                  {'@type': 'Service', 'name': I['h1'], 'serviceType': 'Cloud ERP implementation and hosting', 'description': I['lede'],
                   'provider': {'@id': SITE + '/#org'}, 'areaServed': ['CA', 'US'], 'url': url_for(path)},
                  faq_ld(I['faq']), crumbs([pg('index.html', 'Home'), (I['name'], url_for(path))])]
        write(path, page(path, I['title'], I['lede'], schema, body))

def notfound():
    body = (hero('Page not found.', 'The page may have moved. These will get you back on track.')
            + '<section class="band"><div class="in"><p class="ctas"><a class="btn dk" href="index.html">Home</a><a class="btn ol" href="products.html">Products</a><a class="btn ol" href="articles.html">Articles</a><a class="btn ol" href="contact.html">Contact</a></p></div></section>')
    write('404.html', page('404.html', 'Page not found | Nastaliq', 'This page could not be found on nastaliq.co.', [], body, robots='noindex,follow'))

# ---------------------------------------------------------------- products
def products():
    cards = ''
    for pid, title, desc, ul in PRODUCTS:
        cards += '<article class="pcard" id="%s"><h2>%s</h2><p>%s</p><ul>%s</ul></article>' % (pid, title, desc, ''.join('<li>%s</li>' % e for e in ul))
    body = (hero('What we build.', 'Inventory, purchasing, sales and accounting, plus the apps around them, all hosted by us.')
            + '<section class="band"><div class="in"><div class="pgrid">' + cards + '</div></div></section>'
            + '<section class="band" style="padding-top:0"><div class="in"><div class="cta2"><h2>Tell us what you run</h2><p>We reply by email with a plan and a price.</p><a class="btn" href="contact.html">Get in touch</a></div></div></section>')
    items = [{'@type': 'ListItem', 'position': i + 1, 'item': {'@type': 'SoftwareApplication', 'name': p[1], 'description': p[2], 'applicationCategory': 'BusinessApplication',
              'operatingSystem': 'Web', 'url': url_for('products.html') + '#' + p[0], 'provider': {'@id': SITE + '/#org'}}} for i, p in enumerate(PRODUCTS)]
    schema = [{'@type': 'CollectionPage', 'name': 'Nastaliq products', 'url': url_for('products.html'), 'inLanguage': 'en', 'isPartOf': {'@id': SITE + '/#website'}},
              {'@type': 'ItemList', 'name': 'Nastaliq products', 'itemListElement': items},
              crumbs([pg('index.html', 'Home'), pg('products.html', 'Products')])]
    write('products.html', page('products.html', 'Nastaliq Products | Inventory, purchasing, sales, accounting',
          'What Nastaliq builds: business suite, janitorial operations, owner dashboard, every language, and point of sale.', schema, body, cur='products'))

# ---------------------------------------------------------------- company
def company():
    facts = [('Legal name', 'Nastaliq LLP'),
             ('Registered', 'Incorporated on 16 October 2026 with the Securities and Exchange Commission of Pakistan (SECP) under the Limited Liability Partnership Act, 2017.'),
             ('Registration No.', '%s (<a href="%s" rel="noopener">verify with SECP</a>)' % (REG_NO, REG_URL))]
    dl = ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % f for f in facts)
    body = (hero('A committed team that implements your system and keeps it running.', 'Nastaliq builds and hosts a private cloud ERP for growing businesses in North America.')
            + '<section class="band paper"><div class="in"><h2>What we do</h2><div class="prose" style="margin-top:22px"><p>Nastaliq implements and hosts a private cloud ERP for growing businesses: inventory, purchasing, sales and accounting in one system. Each client runs on its own dedicated server, with its own name and logo, and its data is never shared with another company.</p></div></div></section>'
            + '<section class="band"><div class="in"><h2>Who we are</h2><dl class="facts">%s</dl></div></section>' % dl)
    schema = [{'@type': 'AboutPage', 'name': 'About Nastaliq', 'url': url_for('company.html'), 'inLanguage': 'en', 'about': {'@id': SITE + '/#org'}, 'isPartOf': {'@id': SITE + '/#website'}},
              crumbs([pg('index.html', 'Home'), pg('company.html', 'Company')])]
    write('company.html', page('company.html', 'About Nastaliq LLP | Cloud business software team',
          'Nastaliq LLP builds and hosts a private cloud ERP for growing businesses in North America. Registered with SECP, based in Lahore, Pakistan.', schema, body, cur='company'))

# ---------------------------------------------------------------- contact
MAIL_ICON = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10 13a5 5 0 0 0 7.5.5l3-3a5 5 0 0 0-7-7l-1.7 1.7"/><path d="M14 11a5 5 0 0 0-7.5-.5l-3 3a5 5 0 0 0 7 7l1.7-1.7"/></svg>'

def contact():
    steps = [('What you sell', 'Products, services, or both.'), ('Your locations', 'How many, and where.'),
             ('What you use today', 'Spreadsheets, accounting software, another system.')]
    li = ''.join('<li><b>%s</b><span>%s</span></li>' % s for s in steps)
    body = (hero('Tell us about your business.', 'Write to us with what you sell, how many locations you run, and what you use today. We reply by email with a plan and a price.')
            + '<section class="band"><div class="in"><div class="cbox" id="contact"><div><h2>Email us</h2><p class="lede">Pricing is sent by email: a flat monthly subscription with unlimited users plus a one-time implementation fee.</p>'
              '<p class="mail">%s<a class="copy" href="mailto:%s?subject=Nastaliq%%20demo%%20request" aria-label="Send an email to %s">%sEmail</a></p></div>'
              '<div><a class="btn dk" href="mailto:%s?subject=Nastaliq%%20demo%%20request">Email us</a>'
              '<ol class="steps">%s</ol></div></div></div></section>'
            % (EMAIL, EMAIL, EMAIL, MAIL_ICON, EMAIL, li) + flow_section())
    schema = [{'@type': 'ContactPage', 'name': 'Contact Nastaliq', 'url': url_for('contact.html'), 'inLanguage': 'en', 'about': {'@id': SITE + '/#org'}, 'isPartOf': {'@id': SITE + '/#website'}},
              crumbs([pg('index.html', 'Home'), pg('contact.html', 'Contact')])]
    write('contact.html', page('contact.html', 'Contact Nastaliq | Get a plan and a price by email',
          'Tell Nastaliq what you sell, how many locations you run and what you use today. We reply by email with a plan and a price.', schema, body, cur='contact'))

# ---------------------------------------------------------------- articles
def articles():
    for i, a in enumerate(ARTS):
        rel = [ARTS[(i + k) % len(ARTS)] for k in (1, 2, 3)]   # three neighbours keep the related row symmetrical
        faq = ''.join('<details><summary>%s</summary><p>%s</p></details>' % (html.escape(q), html.escape(ans)) for q, ans in a['faq'])
        pub = PUBLISHED.get(a['slug'], TODAY)
        byline = ('By %s, %s' % (html.escape(AUTHOR['name']), AUTHOR['role'])) if AUTHOR else 'By the Nastaliq team'
        body = ('<article class="in art"><div class="crumb"><a href="../index.html">Home</a> / <a href="../articles.html">Articles</a></div>'
                '<h1>%s</h1><p class="meta">%s &middot; Published <time datetime="%s">%s</time> &middot; %s</p>'
                '<div class="short"><b>The short answer</b><p>%s</p></div>'
                '<div class="prose">%s</div>'
                '<section class="prose faq-s"><h2>Common questions</h2>%s</section>'
                '<div class="cta"><h3>See Nastaliq with your business loaded</h3><p>Tell us what you sell and how you run today. We reply by email with a plan and a price.</p>'
                '<a class="btn" href="../contact.html">Book a free demo</a> <a class="btn" href="../products.html">See products</a></div>'
                '<div class="rel"><h2>More guides</h2><div class="ac">%s</div></div></article>'
                % (html.escape(a['title']), a['tag'], pub, nice_date(pub), byline, html.escape(a['short']), a['body'], faq, art_cards(rel, '')))
        path = 'articles/%s.html' % a['slug']
        schema = [{'@type': 'Article', 'headline': a['title'], 'description': a['desc'], 'datePublished': pub, 'dateModified': UPDATED, 'inLanguage': 'en',
                   'author': ({'@type': 'Person', 'name': AUTHOR['name'], 'jobTitle': AUTHOR['role'], 'url': AUTHOR.get('url') or url_for('company.html'), 'worksFor': {'@id': SITE + '/#org'}} if AUTHOR else {'@id': SITE + '/#org'}),
                   'publisher': {'@id': SITE + '/#org'}, 'mainEntityOfPage': url_for(path),
                   'image': SITE + '/img/og.png', 'isPartOf': {'@id': SITE + '/#website'}},
                  faq_ld(a['faq']), crumbs([pg('index.html', 'Home'), pg('articles.html', 'Articles'), (a['title'], url_for(path))])]
        seo = a['seo']
        write(path, page(path, (seo + ' | Nastaliq') if len(seo) <= 49 else seo, a['desc'], schema, body, cur='art', og_type='article'))
    body = ('<section class="pagehead"><div class="in"><h1 style="max-width:18ch">Guides for business owners</h1>'
            '<p class="lede">Plain advice on software, stock and running your operations. No jargon.</p></div></section>'
            '<section class="band paper"><div class="in"><div class="ac">%s</div></div></section>' % art_cards(ARTS, h='h2'))
    schema = [{'@type': 'CollectionPage', 'name': 'Articles', 'url': url_for('articles.html'), 'inLanguage': 'en', 'isPartOf': {'@id': SITE + '/#website'}},
              {'@type': 'ItemList', 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': url_for('articles/%s.html' % a['slug']), 'name': a['title']} for i, a in enumerate(ARTS)]},
              crumbs([pg('index.html', 'Home'), pg('articles.html', 'Articles')])]
    write('articles.html', page('articles.html', 'ERP guides for business owners | Nastaliq',
          'Guides on choosing an ERP, ERP cost, implementation and data migration, inventory software, moving off spreadsheets and multilingual systems.', schema, body, cur='art'))

# ---------------------------------------------------------------- legal
LEGAL = {
 'privacy.html': dict(
   t='Privacy Policy',
   d='How Nastaliq LLP handles personal information on nastaliq.co and when you contact us.',
   s=[
      ('Who we are',
       'Nastaliq LLP is a limited liability partnership incorporated with the Securities and Exchange Commission of Pakistan (Registration No. %s), based in Lahore, Pakistan. This policy covers the website nastaliq.co and the messages you send us. You can reach us at <a href="mailto:%s">%s</a>.' % (REG_NO, EMAIL, EMAIL)),
      ('What this website collects',
       'The website has no accounts, no advertising trackers and no analytics scripts, and we set no cookies of our own. The demo form on the home page does not send anything to our servers: it opens your own email app with your answers filled in, and nothing reaches us unless you send that email.'),
      ('Service providers',
       'The site is delivered through a content delivery network and loads its fonts from Google Fonts. Like any web host, these providers process technical data such as your IP address and browser type in order to deliver pages and keep the service secure.'),
      ('When you email us',
       'If you write to us, we keep your name, email address, business details and the content of your message. We use them to reply, prepare a demo and send you a plan and a price. We do not sell personal information, and we do not share it except with the email providers that carry and store our mail.'),
      ('Client systems',
       'Data that clients keep inside the business software we host for them is handled under the agreement with that client, not under this website policy.'),
      ('Your choices',
       'You can ask us to show you, correct or delete the personal information we hold about you by writing to <a href="mailto:%s">%s</a>. We answer within a reasonable time.' % (EMAIL, EMAIL)),
      ('Changes',
       'If this policy changes, the new version is posted on this page with a new date.'),
   ]),
 'terms.html': dict(
   t='Terms of Service',
   d='The terms that apply when you use the nastaliq.co website.',
   s=[
      ('About these terms',
       'These terms apply to the website nastaliq.co, operated by Nastaliq LLP (Registration No. %s). By using the site you agree to them. The business software we provide to clients is covered by a separate written agreement with each client.' % REG_NO),
      ('Information on the site',
       'The site describes our products for general information. Features and availability can change, and some features described may still be in development, so what you receive is set by your written agreement. Screens shown on the site use sample data. Guides and articles are general information and are not legal, tax or accounting advice.'),
      ('Pricing and offers',
       'Nothing on the site is a binding offer. Plans and prices are sent by email and take effect only in a written agreement.'),
      ('Our content',
       'The Nastaliq name, logo, text and designs on the site belong to Nastaliq LLP. You may link to the site and quote short passages with credit. Please do not copy the site or pass it off as your own.'),
      ('Acceptable use',
       'Do not use the site in a way that breaks the law, disrupts the service or attempts to gain unauthorised access to it.'),
      ('Liability',
       'The site is provided as is. To the extent the law allows, Nastaliq LLP is not liable for loss arising from use of the site or reliance on its content. Links to other websites are provided for convenience and we are not responsible for their content.'),
      ('Governing law and contact',
       'These terms are governed by the laws of Pakistan. Questions about them can be sent to <a href="mailto:%s">%s</a>.' % (EMAIL, EMAIL)),
   ]),
}

def legal():
    for path, L in LEGAL.items():
        title = L['t']
        secs = ''.join('<h2>%s</h2><p>%s</p>' % hp for hp in L['s'])
        body = ('<article class="in art"><div class="crumb"><a href="index.html">%s</a> / %s</div><h1>%s</h1>'
                '<p class="meta">%s <time datetime="%s">%s</time></p><div class="prose">%s</div></article>'
                % ('Home', title, title, 'Last updated', LEGAL_DATE, nice_date(LEGAL_DATE), secs))
        schema = [{'@type': 'WebPage', 'name': title, 'url': url_for(path), 'inLanguage': 'en', 'isPartOf': {'@id': SITE + '/#website'}},
                  crumbs([pg('index.html', 'Home'), (title, url_for(path))])]
        write(path, page(path, title + ' | Nastaliq', L['d'], schema, body))

# ---------------------------------------------------------------- home (template in tools/home.tpl.html)
def home():
    tpl = open(os.path.join(ROOT, 'tools', 'home.tpl.html'), encoding='utf-8').read()
    sprite = re.search(r'<svg width="0".*?</svg>', tpl, re.S).group(0)
    main = re.search(r'<main id="main">.*?</main>', tpl, re.S).group(0)
    by_slug = {i['slug']: i for i in INDUSTRIES}
    opts = ''.join('<option>%s</option>' % html.escape(i['name']) for i in INDUSTRIES) + '<option>Other</option>'
    cats = ''.join('<option value="%s">' % html.escape(c) for c in sorted(set([i['name'] for i in INDUSTRIES] + EXTRA_CATEGORIES)))
    chips = ''.join('<a href="industries/%s.html">%s</a>' % (s, by_slug[s]['name']) for s in OTHER_INDUSTRIES)
    faq_html = ''.join('<details><summary>%s</summary><p>%s</p></details>' % (q, a) for q, a in FAQ)
    main = (main.replace('<!--FAQ-->', faq_html).replace('<!--ARTS-->', art_cards(ARTS[:6]))
            .replace('<!--IND-OPTS-->', opts).replace('<!--IND-LIST-->', cats).replace('<!--IND-CHIPS-->', chips))
    assert '@@' not in main and '<!--' not in main
    app = {'@type': 'SoftwareApplication', 'name': 'Nastaliq ERP', 'applicationCategory': 'BusinessApplication', 'operatingSystem': 'Web',
           'description': 'Private cloud ERP for growing businesses: inventory, purchasing, sales and accounting on a dedicated server, in the language your team works in.',
           'url': url_for('index.html'), 'provider': {'@id': SITE + '/#org'},
           'featureList': ['Inventory with barcode scanning', 'Purchasing', 'Accounting', 'Sales', 'Every language']}
    schema = [{'@type': 'WebPage', '@id': url_for('index.html') + '#webpage', 'url': url_for('index.html'), 'name': 'Nastaliq', 'inLanguage': 'en',
               'isPartOf': {'@id': SITE + '/#website'}, 'about': {'@id': SITE + '/#org'}}, app, faq_ld(FAQ)]
    title = 'Nastaliq | Private cloud ERP for inventory and accounting'
    desc = 'Private cloud ERP for growing North American businesses: inventory, purchasing, sales and accounting on your own dedicated server, in your language.'
    out = head('index.html', title, desc, schema) + '<body>' + sprite + header('index.html', '', True) + main + footer('index.html') + '<script src="js/home.js" defer></script></body></html>\n'
    write('index.html', out)

def seo_files():
    pages = [('index.html', '1.0'), ('products.html', '0.8'), ('company.html', '0.6'), ('contact.html', '0.7'), ('articles.html', '0.8')] + [('articles/%s.html' % a['slug'], '0.7') for a in ARTS] + [('industries/%s.html' % i['slug'], '0.8') for i in INDUSTRIES] + [('privacy.html', '0.3'), ('terms.html', '0.3')]
    rows = ''.join('<url><loc>%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>\n' % (url_for(p), UPDATED, pr) for p, pr in pages)
    open(os.path.join(PUB, 'sitemap.xml'), 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + rows + '</urlset>\n')
    bots = ['GPTBot', 'OAI-SearchBot', 'ChatGPT-User', 'ClaudeBot', 'Claude-SearchBot', 'Claude-User', 'PerplexityBot', 'Google-Extended', 'Applebot-Extended']
    open(os.path.join(PUB, 'robots.txt'), 'w').write('User-agent: *\nAllow: /\n\n' + ''.join('User-agent: %s\nAllow: /\n\n' % b for b in bots) + 'Sitemap: %s/sitemap.xml\n' % SITE)
    moved = [('choosing-pos-and-inventory-software-small-business', 'how-to-choose-an-erp'), ('cloud-vs-on-premise-for-small-business', 'private-cloud-erp-vs-saas-vs-on-premise'),
             ('bilingual-business-software-canada', 'multilingual-erp-software')]
    redirects = ''.join('/articles/%s%s /articles/%s 301\n' % (a, ext, b) for a, b in moved for ext in ('', '.html'))
    # the French site was retired: send old /fr URLs to their English equivalents
    redirects += '/fr/articles/bilingual-business-software-canada /articles/multilingual-erp-software 301\n/fr/articles/:slug /articles/:slug 301\n'
    redirects += '/fr/industries/:slug /industries/:slug 301\n/fr / 301\n/fr/* /:splat 301\n'
    open(os.path.join(PUB, '_redirects'), 'w').write(redirects)
    ind = '\n'.join('- [%s](%s): %s' % (i['h1'], url_for('industries/%s.html' % i['slug']), i['lede']) for i in INDUSTRIES)
    prod = '\n'.join('- [%s](%s#%s): %s' % (p[1], url_for('products.html'), p[0], p[2]) for p in PRODUCTS)
    art = '\n'.join('- [%s](%s): %s' % (a['title'], url_for('articles/%s.html' % a['slug']), a['desc']) for a in ARTS)
    faq = '\n'.join('**%s** %s\n' % qa for qa in FAQ)
    txt = ('# Nastaliq\n\n> Nastaliq LLP builds and hosts private cloud ERP for growing businesses in North America: inventory, purchasing, sales and accounting in one system, with each client on its own dedicated server, in the language your team works in. Cloud only. Pricing is a flat monthly subscription with unlimited users plus a one-time implementation fee, sent by email. Data migration is charged separately.\n\n'
           'Nastaliq LLP is incorporated with the Securities and Exchange Commission of Pakistan (SECP) and based in Lahore, Pakistan. Contact: %s\n\n## Pages\n- [Home](%s)\n- [Products](%s)\n- [Company](%s)\n- [Contact](%s)\n- [Articles](%s)\n\n## Products\n%s\n\n## Industries\n%s\n\n## Guides\n%s\n\n## Frequently asked questions\n%s\n'
           % (EMAIL, url_for('index.html'), url_for('products.html'), url_for('company.html'), url_for('contact.html'), url_for('articles.html'), prod, ind, art, faq))
    open(os.path.join(PUB, 'llms.txt'), 'w').write(txt)

if __name__ == '__main__':
    products(); company(); contact(); articles(); industries(); legal(); notfound(); home()
    seo_files()
    print('built')
