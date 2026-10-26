#!/usr/bin/env python3
"""Builds Nastaliq's static pages into public/. Run: python3 tools/build_site.py
- Generates products, company, contact, articles index and article pages.
- Rewrites the <head> (SEO/AEO metadata, JSON-LD), header, footer and FAQ block of the hand-kept public/index.html.
- Writes sitemap.xml, robots.txt, llms.txt.
Pricing never appears on the site: prices go out by email only."""
import html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB = os.path.join(ROOT, 'public')
SITE = 'https://nastaliq.co'
TODAY = '2026-10-26'
EMAIL = 'hello@nastaliq.co'
FONT = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=Figtree:wght@400;500;600;700&display=swap">')

def x(s): return html.escape(s, quote=True)
def B(en, fr, tag='span'):
    """bilingual inline text"""
    return '<span class="en">%s</span><span class="fr">%s</span>' % (en, fr)

# ---------------------------------------------------------------- shared data
ORG = {
    '@type': 'Organization', '@id': SITE + '/#org', 'name': 'Nastaliq', 'legalName': 'Nastaliq LLP', 'url': SITE + '/',
    'logo': SITE + '/img/mark.svg', 'email': EMAIL,
    'description': 'Nastaliq builds and hosts cloud business software for small and mid-sized businesses in North America: point of sale, inventory, purchasing, accounting and sales in one system, in English and French.',
    'address': {'@type': 'PostalAddress', 'addressLocality': 'Lahore', 'addressCountry': 'PK'},
    'areaServed': ['CA', 'US'], 'knowsLanguage': ['en', 'fr'],
    'contactPoint': {'@type': 'ContactPoint', 'contactType': 'sales', 'email': EMAIL, 'availableLanguage': ['English', 'French']},
}
WEBSITE = {'@type': 'WebSite', '@id': SITE + '/#website', 'url': SITE + '/', 'name': 'Nastaliq', 'inLanguage': ['en', 'fr'], 'publisher': {'@id': SITE + '/#org'}}

PRODUCTS = [
    ('suite', 'ok', 'Available', 'Disponible', 'Business suite', "Suite d'affaires",
     'Inventory, purchasing, accounting and sales in one cloud system, set up for your business and hosted by us.',
     "Inventaire, achats, comptabilité et ventes dans un seul système infonuagique, configuré pour votre entreprise et hébergé par nous.", []),
    ('pos', 'warn', 'In development', 'En développement', 'Point of sale', 'Point de vente',
     'A clean, fast till for restaurants, fast food and bakeries.',
     'Une caisse rapide et épurée pour restaurants, restauration rapide et boulangeries.',
     [('Admin-editable colour themes', "Thèmes de couleurs modifiables par l'administrateur"), ('Built for counter speed', 'Pensé pour la vitesse au comptoir')]),
    ('janitorial', 'warn', 'Early access', 'Accès anticipé', 'Janitorial operations', "Gestion des services d'entretien",
     'Run a commercial cleaning company from one app, for cleaners, supervisors and clients.',
     "Gérez une entreprise d'entretien commercial depuis une seule application, pour les employés, les superviseurs et les clients.",
     [('Time clock with GPS geofencing', 'Pointage avec géorepérage GPS'), ('Inspections and checklists with photo proof', 'Inspections et listes de vérification avec preuve photo'),
      ('Client portal and messaging', 'Portail client et messagerie'), ('Supplies and job profitability', 'Fournitures et rentabilité par contrat')]),
    ('owner', 'warn', 'Early access', 'Accès anticipé', 'Owner dashboard and alerts', 'Tableau de bord et alertes',
     'A home screen by role, phone-friendly stock screens, and a morning email digest of what needs attention.',
     "Un écran d'accueil selon le rôle, des écrans de stock adaptés au téléphone et un courriel matinal sur ce qui demande votre attention.", []),
    ('bilingual', 'ok', 'Available', 'Disponible', 'English and French', 'Anglais et français',
     'One switch on every screen, with Canadian French terms such as courriel and téléverser.',
     'Un seul bouton sur chaque écran, avec la terminologie du français canadien, comme courriel et téléverser.', []),
    ('claude', 'warn', 'Pilot', 'Projet pilote', 'Claude-powered assistance', 'Assistance propulsée par Claude',
     'Plain-language questions about your data and in-screen guidance. Discrepancy auditing is planned.',
     "Questions en langage courant sur vos données et aide dans l'écran. L'audit des écarts est prévu.", []),
]

# FAQ shown on the home page AND emitted as FAQPage JSON-LD (text must match what is visible)
FAQ = [
    ('What is Nastaliq?', "Qu'est-ce que Nastaliq?",
     'Nastaliq is cloud business software for small and mid-sized businesses in North America. It puts point of sale, inventory, purchasing, accounting and sales in one system, in English and French. We set it up for your business and host it.',
     "Nastaliq est un logiciel d'affaires infonuagique pour les petites et moyennes entreprises d'Amérique du Nord. Il réunit caisse, stocks, achats, comptabilité et ventes dans un seul système, en français et en anglais. Nous l'installons pour votre entreprise et l'hébergeons."),
    ('How much does Nastaliq cost?', 'Combien coûte Nastaliq?',
     'Pricing is a flat monthly subscription with unlimited users, plus a one-time setup fee. We send the exact plan and price by email after you tell us what you run.',
     "Le tarif est un abonnement mensuel fixe avec utilisateurs illimités, plus des frais d'installation uniques. Nous envoyons le plan et le prix exacts par courriel après que vous nous avez décrit votre entreprise."),
    ('How long does it take to go live?', 'Combien de temps avant la mise en service?',
     'Most businesses go live in about six weeks, with setup and hosting handled by us.',
     "La plupart des entreprises démarrent en environ six semaines, installation et hébergement assurés par nous."),
    ('Do I need to install anything?', 'Dois-je installer quelque chose?',
     'No. Nastaliq runs in the cloud. You sign in from a browser or your phone.',
     'Non. Nastaliq fonctionne dans le nuage. Vous vous connectez depuis un navigateur ou votre téléphone.'),
    ('Is Nastaliq available in French?', 'Nastaliq est-il offert en français?',
     'Yes. Every screen has an English and French switch, with Canadian French terms such as courriel and téléverser.',
     "Oui. Chaque écran offre un bouton anglais et français, avec la terminologie du français canadien, comme courriel et téléverser."),
    ('Can you bring my existing records in?', 'Pouvez-vous importer mes données existantes?',
     'Yes. We help bring your existing customers, products and records in during setup. Tell us what you use today and we will say what is possible.',
     "Oui. Nous vous aidons à importer vos clients, produits et dossiers existants pendant l'installation. Dites-nous ce que vous utilisez aujourd'hui et nous vous dirons ce qui est possible."),
    ('What does the Claude-powered assistance do?', "Que fait l'assistance propulsée par Claude?",
     'Plain-language questions about your own data and guidance inside the screen. Both are in Pilot. Automatic discrepancy auditing is only planned. Every AI feature on this site shows its real status.',
     "Des questions en langage courant sur vos propres données et de l'aide dans l'écran. Les deux sont en projet pilote. L'audit automatique des écarts est seulement prévu. Chaque fonction d'IA du site affiche son état réel."),
    ('Who builds and supports Nastaliq?', 'Qui conçoit et soutient Nastaliq?',
     'Nastaliq LLP, a small team in Lahore, Pakistan, serving clients in North America.',
     'Nastaliq LLP, une petite équipe à Lahore, au Pakistan, au service de clients nord-américains.'),
]

ARTS = [
 dict(slug='choosing-pos-and-inventory-software-small-business', tag='Buying guide',
      title='How to choose POS and inventory software for a small business',
      desc='A practical checklist for owners comparing point of sale and inventory systems: what to test, what to ask and what to ignore.',
      short='Pick the system that passes your own ten must-have tasks live, keeps sales, stock and books in one place, works on a phone and has pricing you can predict. Ignore everything else in the demo.',
      faq=[('What should a small business look for in POS software?', 'Look for sales that update stock and the books automatically, a screen that works on a phone, easy export of your own data, and a pricing model that does not grow with every new user.'),
           ('How do I compare POS and inventory systems fairly?', 'Write down your ten most common tasks, ask each vendor to do them live with your sample data and score each task pass or fail.'),
           ('Should POS and inventory be one system?', 'Usually yes. When one system records the sale, the stock change and the accounting entry, you avoid re-typing and your numbers agree.')],
      body='''
<p>Most small businesses pick point of sale and inventory software the same way: a quick demo, a monthly price, a gut feeling. Six months later the stock numbers are wrong, the books are done by hand and nobody wants to switch again. This checklist helps you avoid that.</p>
<h2>Start with how you actually sell</h2>
<p>Write down the three or four things your team does every day. A bakery rings sales at a counter and tracks flour and boxes. A distributor takes orders by phone and receives pallets. A shop does both. The software has to fit those moves, not the other way round. If a demo spends ten minutes on features you will never use, that tells you who the product was built for.</p>
<h2>Check that sales, stock and books are one system</h2>
<p>The most common failure is three tools that don't talk to each other. A sale rings up in one place, stock is edited in a spreadsheet and the accountant gets a monthly export. Ask a simple question during the demo: <strong>when I sell one item, what changes, and where?</strong> A good answer is that stock drops, the sale posts to the books and the customer record updates, all by itself.</p>
<h2>Test it on a phone</h2>
<p>Receiving stock, counting shelves and checking a price happen on the floor, not at a desk. Open the product on a phone and try to receive a delivery. If you need to pinch and zoom to press a button, your staff will stop using it.</p>
<h2>Ask what happens to your data</h2>
<ul><li>Can you export all your records, in a normal format, at any time?</li><li>Who handles backups, and how often?</li><li>What does it cost, in time and money, to bring your existing customers and products in?</li></ul>
<h2>Look at the pricing model, not only the price</h2>
<p>A low price per user gets expensive when you add cashiers, warehouse staff and a bookkeeper. Ask whether users are unlimited, whether setup is a one-time fee and whether hosting and updates are included. A flat monthly subscription is easier to plan around than a bill that changes whenever you hire.</p>
<h2>Check language and location</h2>
<p>If you serve customers in English and French, check that invoices, receipts and staff screens can switch language, not just the website. Check tax handling for your province as well.</p>
<h2>Be honest about what is finished</h2>
<p>Ask the vendor which features are available today and which are still being built. Reputable vendors will tell you plainly. Anything labelled "coming soon" should not be part of your buying decision.</p>
<h2>A simple scoring method</h2>
<ol><li>List your must-have tasks, no more than ten.</li><li>Have each vendor show you each task live, with your own sample data.</li><li>Score each one pass or fail. Ignore everything else.</li></ol>
<p>The system that passes the most real tasks, with a pricing model you can predict, is usually the right one.</p>'''),
 dict(slug='why-inventory-counts-drift', tag='Inventory',
      title='Why inventory counts drift, and how barcode scanning fixes it',
      desc='The usual reasons your stock numbers stop matching the shelf, and the small habits and tools that close the gap.',
      short='Inventory counts drift because stock moves or arrives without being recorded at the moment it happens. Scanning barcodes at receiving, transfer and sale, plus small weekly counts, keeps the system and the shelf in step.',
      faq=[('Why does my inventory never match the shelf?', 'Usually because receiving, transfers, returns or damage were recorded late, wrongly or not at all. The longer the gap between the event and the entry, the bigger the drift.'),
           ('Does barcode scanning really improve stock accuracy?', 'Yes. Scanning identifies the exact item and records it at the moment it moves, which removes most typing mistakes and forgotten entries.'),
           ('How often should a small business count stock?', 'Count a small group of fast-moving items every week instead of the whole warehouse once a year. Problems show up sooner and are easier to trace.')],
      body='''
<p>You count the shelf on Monday and the system agrees. By Friday it doesn't. Inventory drift is normal, and it almost always comes from the same handful of causes.</p>
<h2>Where the numbers go wrong</h2>
<ul><li><strong>Receiving errors.</strong> A delivery is checked against the packing slip, but the slip is wrong, or the count is entered later from memory.</li><li><strong>Unrecorded movement.</strong> Stock moves between rooms, trucks or locations without a transfer being entered.</li><li><strong>Typing mistakes.</strong> One extra zero on a quantity is enough to hide a shortage for weeks.</li><li><strong>Returns and damage.</strong> Items are thrown away or returned to suppliers with no adjustment.</li><li><strong>Substitutions at the counter.</strong> A customer gets a different size than the one rung up.</li></ul>
<h2>Why delay makes it worse</h2>
<p>The longer the gap between an event and recording it, the more likely it is to be forgotten or entered wrong. Paper notes that get typed in at the end of the day are the biggest source of drift in small warehouses and shops.</p>
<h2>What barcode scanning changes</h2>
<p>Scanning replaces typing with a camera or scanner. The item is identified by its code, so you can't mistype a name or pick the wrong variant. When scanning happens at the moment of receiving, transferring or selling, the system is updated while the stock is still in your hands.</p>
<h2>Habits that keep counts honest</h2>
<ol><li><strong>Receive against the purchase order,</strong> not against memory.</li><li><strong>Record every transfer</strong> between locations, even short trips.</li><li><strong>Count a little every week.</strong> Cycle counts of a few fast-moving items catch problems sooner than one big count a year.</li><li><strong>Investigate differences</strong> once, then fix the cause, not just the number.</li><li><strong>Give staff phone-sized screens</strong> so recording takes seconds.</li></ol>
<h2>Set a reorder level for important items</h2>
<p>When stock is accurate you can trust a reorder alert. A system that tells you six items are below their minimum each morning removes the need to walk the shelves just to find out what to buy.</p>
<h2>Start small</h2>
<p>You don't need to fix everything at once. Pick your twenty fastest-moving items, scan them in and out for a month and compare against a physical count. Most owners see the difference quickly.</p>'''),
 dict(slug='bilingual-business-software-canada', tag='Canada',
      title='Bilingual business software for Canadian small businesses',
      desc='Why English and French support matters for invoices, receipts and staff screens, and what to check before you buy.',
      short='Good bilingual software lets each user pick a language and prints invoices and receipts in the customer\'s language, with Canadian French terms. Test it with your own documents before you buy, and check provincial rules with an adviser.',
      faq=[('Does business software need to support French in Canada?', 'It depends on your province, customers and business type. Many Canadian businesses serve both languages, so a system that switches cleanly saves retyping. Confirm your own obligations with an accountant or adviser.'),
           ('What should I check in bilingual business software?', 'Check that each user can choose a language, that invoices and receipts can print in either language, and that emails, reports and error messages are translated, not only the menu.'),
           ('Is Canadian French different from European French in software?', 'Yes. Some business terms differ, for example courriel for email and téléverser for upload. Ask whether the translation was written for Canadian users.')],
      body='''
<p>If you sell in Canada, some of your customers will prefer French, and some of your staff will too. Software that only works well in English creates friction on both sides of the counter.</p>
<h2>Where language shows up</h2>
<ul><li><strong>Customer documents:</strong> invoices, quotes, receipts and statements.</li><li><strong>Staff screens:</strong> menus, buttons, error messages and reports.</li><li><strong>Emails and notifications</strong> that your system sends on your behalf.</li><li><strong>Product names and descriptions</strong> you enter yourself.</li></ul>
<h2>Translation is not the same as Canadian French</h2>
<p>Business vocabulary differs between France and Canada. Terms for receipts, taxes and payment methods are not always the same, and staff notice when a screen sounds foreign. Ask the vendor whether the French is written for Canadian users, and have a French-speaking colleague click through a real invoice.</p>
<h2>Questions to ask a vendor</h2>
<ol><li>Can each user choose their own language, or is it one setting for the whole company?</li><li>Can one customer receive French documents while another receives English?</li><li>Are reports, emails and error messages translated, or only the main menu?</li><li>Who maintains the translations when new features are added?</li></ol>
<h2>Check your own obligations</h2>
<p>Language requirements for commercial documents and signage differ by province and by business type. Speak to your accountant or a qualified adviser about what applies to you, rather than relying on a software vendor's summary.</p>
<h2>The practical benefit</h2>
<p>A bilingual system lets you hire from a wider pool, serve more customers and hand documents to either side without retyping. For a growing business that sells across provincial lines, that matters more each year.</p>
<h2>What to do next</h2>
<p>Before you buy, ask for a demo in French and in English using your own product names. If the system handles both cleanly, you have one less thing to worry about later.</p>'''),
 dict(slug='cloud-vs-on-premise-for-small-business', tag='Buying guide',
      title='Cloud or on-premise software: which fits a small business',
      desc='A plain comparison of costs, upkeep, backups and risk for owners deciding where their business system should live.',
      short='For most small businesses, cloud software costs less to run because the vendor handles hosting, updates and backups. On-premise only makes sense when you have IT staff, unreliable internet or a rule that data must stay on site.',
      faq=[('Is cloud software better than on-premise for a small business?', 'For most small businesses, yes. The vendor handles servers, updates and backups, and staff can use it from a phone or any location. On-premise suits businesses with IT staff or a requirement to keep data on site.'),
           ('What are the hidden costs of on-premise software?', 'Servers and replacement hardware, time spent on patches and backups, downtime when something fails, and the cost of adding a second location or remote staff.'),
           ('What should I ask a cloud software vendor?', 'Ask whether you can export all your data, how often backups run and where they are kept, whether updates and hosting are included in the fee, and what happens if you lose internet for a few hours.')],
      body='''
<p>Older business software ran on a server in the back office. Newer software runs in the cloud and you reach it through a browser or a phone. For most small businesses the difference comes down to who carries the upkeep.</p>
<h2>What on-premise means</h2>
<p>You buy or rent a server, install the software, keep it patched and back it up. If it fails, someone on your side fixes it. It can work well for businesses with an IT person and a reason to keep data inside the building.</p>
<h2>What cloud means</h2>
<p>The vendor hosts the software, applies updates and handles backups. You sign in from anywhere. You pay a subscription instead of buying equipment up front.</p>
<h2>Compare the real costs</h2>
<ul><li><strong>Hardware:</strong> servers, networking and replacement after failures.</li><li><strong>Time:</strong> updates, security patches and restoring from backups.</li><li><strong>Downtime:</strong> who gets called when it stops working on a Saturday.</li><li><strong>Growth:</strong> adding a second location or remote staff.</li></ul>
<h2>Where cloud fits well</h2>
<p>Cloud software suits businesses with several people on phones and tablets, more than one location or no dedicated IT staff. Updates arrive without a visit, and everyone sees the same live numbers.</p>
<h2>What to check with a cloud vendor</h2>
<ol><li>Can you export all of your data whenever you want?</li><li>How often are backups taken and where are they kept?</li><li>Are updates and hosting included in the monthly fee?</li><li>What is the plan if you lose internet access for a few hours?</li></ol>
<h2>When on-premise still makes sense</h2>
<p>If your internet connection is unreliable, or a rule or customer contract requires data to stay on site, an on-premise system may be the safer choice. Be honest about whether that is a real requirement or a habit.</p>
<h2>Our view</h2>
<p>Nastaliq is cloud-only. Setup and hosting are handled by us, so a small team spends time selling and receiving stock instead of maintaining a server.</p>'''),
]

# ---------------------------------------------------------------- fragments
def header(pre='', cur='', home=False):
    def l(href, en, fr, k=''):
        c = ' aria-current="page"' if cur == k and k else ''
        return '<a class="l" href="%s"%s>%s</a>' % (href, c, B(en, fr))
    extra = (l('#sectors', 'Industries', 'Secteurs') + l('#pricing', 'Pricing', 'Tarifs')) if home else ''
    lang = ('<div class="lang" role="group" aria-label="Language"><button id="b-en" type="button" aria-pressed="true">EN</button>'
            '<button id="b-fr" type="button" aria-pressed="false">FR</button></div>')
    cta = '<a class="btn pri sm" href="%s">%s</a>' % ('#contact' if home else pre + 'contact.html', B('Request a demo', 'Demander une démo'))
    return ('<a class="skip" href="#main">Skip to content</a><header><div class="in bar"><a class="logo" href="%sindex.html" aria-label="Nastaliq, home">'
            '<img class="mk" src="%simg/mark.svg" width="30" height="28" alt=""><img class="wd" src="%simg/wordmark.svg" width="55" height="15" alt="Nastaliq"></a>'
            '<nav id="nav" aria-label="Main">%s%s%s%s%s%s%s</nav>'
            '<button class="menu-btn" type="button" aria-expanded="false" aria-controls="nav" aria-label="Menu"><i></i><i></i></button></div></header>'
            % (pre, pre, pre, extra, l(pre + 'products.html', 'Products', 'Produits', 'products'), l(pre + 'company.html', 'Company', 'Entreprise', 'company'),
               l(pre + 'articles.html', 'Articles', 'Articles', 'art'), l(pre + 'contact.html', 'Contact', 'Contact', 'contact'), lang, cta))

def footer(pre=''):
    return ('<div class="in"><footer class="foot2"><div class="fl"><a href="%sproducts.html">%s</a><a href="%scompany.html">%s</a><a href="%sarticles.html">Articles</a>'
            '<a href="%scontact.html">Contact</a><a href="mailto:%s">%s</a></div>'
            '<p>%s</p><span>&copy; 2026 Nastaliq LLP. %s</span></footer></div>'
            % (pre, B('Products', 'Produits'), pre, B('Company', 'Entreprise'), pre, pre, EMAIL, EMAIL,
               B('Every feature carries its real status. Available means clients can use it today. Early access, In development, Pilot and Planned are labelled as such. Claude is a product of Anthropic. Trademarks belong to their owners.',
                 "Chaque fonction affiche son état réel. Disponible signifie que des clients peuvent l'utiliser aujourd'hui. Accès anticipé, En développement, Projet pilote et Prévu sont indiqués tels quels. Claude est un produit d'Anthropic. Les marques citées appartiennent à leurs propriétaires."),
               B('Lahore, Pakistan, serving North America.', "Lahore, Pakistan, au service de l'Amérique du Nord.")))

def head(path, title, desc, schema, pre='', og_type='website', extra='', en_only=False):
    url = SITE + '/' + path
    graph = {'@context': 'https://schema.org', '@graph': [ORG, WEBSITE] + schema}
    return ('<!doctype html>\n<html lang="en"%s><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
            '<title>%s</title><meta name="description" content="%s"><link rel="canonical" href="%s">'
            '<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1"><meta name="theme-color" content="#000000">'
            '<link rel="icon" href="%sfavicon.svg" type="image/svg+xml">'
            '<meta property="og:site_name" content="Nastaliq"><meta property="og:locale" content="en_CA"><meta property="og:locale:alternate" content="fr_CA">'
            '<meta property="og:type" content="%s"><meta property="og:title" content="%s"><meta property="og:description" content="%s"><meta property="og:url" content="%s">'
            '<meta property="og:image" content="%s/img/og.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="Nastaliq: cloud business software for small businesses">'
            '<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="%s"><meta name="twitter:description" content="%s"><meta name="twitter:image" content="%s/img/og.png">'
            '%s%s<link rel="stylesheet" href="%scss/home.css">'
            '<script type="application/ld+json">%s</script></head>'
            % (' data-en-only' if en_only else '', x(title), x(desc), url, pre, og_type, x(title), x(desc), url, SITE, x(title), x(desc), SITE, extra, FONT, pre, json.dumps(graph, ensure_ascii=False, separators=(',', ':'))))

SPRITE = open(os.path.join(ROOT, 'tools', 'sprite.svg')).read() if os.path.exists(os.path.join(ROOT, 'tools', 'sprite.svg')) else ''

def page(path, title, desc, schema, body, pre='', cur='', og_type='website', extra='', en_only=False):
    return (head(path, title, desc, schema, pre, og_type, extra, en_only) + '<body>' + header(pre, cur) + '<main id="main">' + body + '</main>'
            + footer(pre) + '<script src="%sjs/home.js" defer></script></body></html>\n' % pre)

def crumbs(items):
    return {'@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': SITE + '/' + u} for i, (n, u) in enumerate(items)]}

def faq_ld(pairs):
    return {'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in pairs]}

def write(path, s):
    p = os.path.join(PUB, path); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8').write(s)

def hero(h1en, h1fr, lede_en, lede_fr):
    return ('<section class="pagehead"><div class="in"><h1 style="max-width:18ch">%s</h1><p class="lede" style="margin-top:20px">%s</p></div></section>'
            % (B(h1en, h1fr), B(lede_en, lede_fr)))

def badge(cls, en, fr):
    return '<span class="tag%s">%s</span>' % (' w' if cls == 'warn' else '', B(en, fr))

# ---------------------------------------------------------------- products
def products():
    cards = ''
    for pid, cls, sen, sfr, ten, tfr, den, dfr, ul in PRODUCTS:
        li = ('<ul>' + ''.join('<li>%s</li>' % B(e, f) for e, f in ul) + '</ul>') if ul else ''
        cards += '<article class="pcard" id="%s">%s<h2>%s</h2><p>%s</p>%s</article>' % (pid, badge(cls, sen, sfr), B(ten, tfr), B(den, dfr), li)
    body = (hero('What we build and where it stands.', 'Ce que nous construisons et où nous en sommes.',
                 'Every product carries a status. Available means clients can use it today. Anything else says so.',
                 "Chaque produit affiche son état. Disponible signifie que des clients peuvent l'utiliser aujourd'hui. Tout le reste est indiqué.")
            + '<section class="band paper"><div class="in"><div class="pgrid">' + cards + '</div></div></section>'
            + '<section class="band"><div class="in"><div class="cta2"><h2>%s</h2><p>%s</p><a class="btn" href="contact.html">%s</a></div></div></section>'
            % (B('Tell us what you run', 'Dites-nous ce que vous exploitez'),
               B('We reply by email with a plan and a price.', 'Nous répondons par courriel avec un plan et un prix.'),
               B('Get in touch', 'Nous joindre')))
    items = [{'@type': 'ListItem', 'position': i + 1, 'item': {'@type': 'SoftwareApplication', 'name': p[4], 'description': p[6], 'applicationCategory': 'BusinessApplication',
              'operatingSystem': 'Web', 'url': SITE + '/products.html#' + p[0], 'provider': {'@id': SITE + '/#org'}}} for i, p in enumerate(PRODUCTS)]
    schema = [{'@type': 'CollectionPage', 'name': 'Nastaliq products', 'url': SITE + '/products.html', 'isPartOf': {'@id': SITE + '/#website'}},
              {'@type': 'ItemList', 'name': 'Nastaliq products', 'itemListElement': items}, crumbs([('Home', ''), ('Products', 'products.html')])]
    write('products.html', page('products.html', 'Nastaliq Products | POS, inventory, accounting and more',
          'What Nastaliq builds and where each product stands: business suite, point of sale, janitorial operations, owner dashboard and Claude-powered assistance.',
          schema, body, cur='products'))

# ---------------------------------------------------------------- company
def company():
    facts = [('Legal name', 'Raison sociale', 'Nastaliq LLP', 'Nastaliq LLP'),
             ('Registered', 'Immatriculation', 'Incorporated with the Securities and Exchange Commission of Pakistan (SECP).', 'Constituée auprès de la Securities and Exchange Commission of Pakistan (SECP).'),
             ('Delivery base', 'Base de livraison', 'Lahore, Pakistan', 'Lahore, Pakistan'),
             ('Serving', 'Clientèle', 'North America', 'Amérique du Nord'),
             ('Team', 'Équipe', 'A small team: software engineering, accounting, and marketing and operations.', 'Une petite équipe : génie logiciel, comptabilité, ainsi que marketing et opérations.'),
             ('Hosting model', "Modèle d'hébergement", 'Cloud only. We do not sell on-premise installs.', "Infonuagique seulement. Nous ne vendons pas d'installations sur place.")]
    dl = ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % (B(a, b), B(c, d)) for a, b, c, d in facts)
    pr = [('Say what is real', 'Dire ce qui est réel', 'Every feature is labelled with its actual status, from Available to Planned.', 'Chaque fonction est étiquetée selon son état réel, de Disponible à Prévu.'),
          ('Accounting first', "La comptabilité d'abord", 'Accounting expertise is part of the team, so the books are set up properly from day one.', "L'expertise comptable fait partie de l'équipe, ce qui garantit des livres bien configurés dès le premier jour."),
          ('Your language', 'Votre langue', 'English and French throughout, because Canadian businesses work in both.', 'Anglais et français partout, parce que les entreprises canadiennes travaillent dans les deux langues.')]
    cards = ''.join('<div><h3>%s</h3><p>%s</p></div>' % (B(a, b), B(c, d)) for a, b, c, d in pr)
    body = (hero('A small team that sets up your system and keeps it running.', 'Une petite équipe qui installe votre système et le maintient en marche.',
                 'Nastaliq builds and hosts cloud business software for small and mid-sized businesses in North America.',
                 "Nastaliq conçoit et héberge des logiciels d'affaires infonuagiques pour les petites et moyennes entreprises d'Amérique du Nord.")
            + '<section class="band paper"><div class="in"><h2>%s</h2><dl class="facts">%s</dl></div></section>' % (B('Who we are', 'Qui nous sommes'), dl)
            + '<section class="band yel"><div class="in"><h2>%s</h2><div class="f4" style="grid-template-columns:repeat(auto-fit,minmax(240px,1fr))">%s</div></div></section>' % (B('How we work with clients', 'Notre façon de travailler avec nos clients'), cards))
    schema = [{'@type': 'AboutPage', 'name': 'About Nastaliq', 'url': SITE + '/company.html', 'about': {'@id': SITE + '/#org'}, 'isPartOf': {'@id': SITE + '/#website'}},
              crumbs([('Home', ''), ('Company', 'company.html')])]
    write('company.html', page('company.html', 'About Nastaliq LLP | Cloud business software team',
          'Nastaliq LLP builds and hosts cloud business software for small and mid-sized businesses in North America. Registered with SECP, based in Lahore, Pakistan.',
          schema, body, cur='company'))

# ---------------------------------------------------------------- contact
def contact():
    steps = [('What you sell', 'Ce que vous vendez', 'Products, services, or both.', 'Produits, services, ou les deux.'),
             ('Your locations', 'Vos emplacements', 'How many, and where.', 'Combien, et où.'),
             ('What you use today', "Ce que vous utilisez aujourd'hui", 'Tills, spreadsheets, another system.', 'Caisses, tableurs, un autre système.')]
    li = ''.join('<li><b>%s</b><span>%s</span></li>' % (B(a, b), B(c, d)) for a, b, c, d in steps)
    body = (hero('Tell us about your business.', 'Parlez-nous de votre entreprise.',
                 'Write to us with what you sell, how many locations you run, and what you use today. We reply by email with a plan and a price.',
                 "Écrivez-nous ce que vous vendez, combien d'emplacements vous exploitez et ce que vous utilisez aujourd'hui. Nous répondons par courriel avec un plan et un prix.")
            + '<section class="band"><div class="in"><div class="ct" id="contact"><div><h2>%s</h2><p class="lede" style="margin-top:14px">%s</p>'
              '<p style="margin-top:22px;font-weight:700;font-size:1.2rem">%s<button type="button" class="copy" id="cp">Copy</button></p></div>'
              '<div style="display:grid;gap:14px;align-content:center"><a class="btn" href="mailto:%s?subject=Nastaliq%%20demo%%20request">%s</a>'
              '<ol class="steps">%s</ol></div></div></div></section>'
            % (B('Email us', 'Écrivez-nous'), B('Pricing is sent by email: a flat monthly subscription with unlimited users plus a one-time setup fee.',
                 "Le tarif est envoyé par courriel : un abonnement mensuel fixe avec utilisateurs illimités, plus des frais d'installation uniques."),
               EMAIL, EMAIL, B('Email us', 'Écrivez-nous'), li))
    schema = [{'@type': 'ContactPage', 'name': 'Contact Nastaliq', 'url': SITE + '/contact.html', 'about': {'@id': SITE + '/#org'}, 'isPartOf': {'@id': SITE + '/#website'}},
              crumbs([('Home', ''), ('Contact', 'contact.html')])]
    write('contact.html', page('contact.html', 'Contact Nastaliq | Get a plan and a price by email',
          'Tell Nastaliq what you sell, how many locations you run and what you use today. We reply by email with a plan and a price.', schema, body, cur='contact'))

# ---------------------------------------------------------------- articles
def art_cards(items, base='articles/'):
    return ''.join('<a href="%s%s.html"><small>%s</small><h3>%s</h3><p>%s</p></a>' % (base, a['slug'], a['tag'], html.escape(a['title']), html.escape(a['desc'])) for a in items)

def articles():
    for a in ARTS:
        rel = [b for b in ARTS if b['slug'] != a['slug']]
        faq = ''.join('<details><summary>%s</summary><p>%s</p></details>' % (html.escape(q), html.escape(ans)) for q, ans in a['faq'])
        body = ('<article class="in art"><div class="crumb"><a href="../index.html">Home</a> / <a href="../articles.html">Articles</a></div>'
                '<h1>%s</h1><p class="meta">%s &middot; Published <time datetime="%s">October 26, 2026</time> &middot; By the Nastaliq team</p>'
                '<div class="short"><b>The short answer</b><p>%s</p></div>'
                '<div class="prose">%s</div>'
                '<section class="prose faq-s"><h2>Common questions</h2>%s</section>'
                '<div class="cta"><h3>See Nastaliq with your business loaded</h3><p>Tell us what you sell and how you run today. We reply by email with a plan and a price.</p>'
                '<a class="btn" href="../contact.html">Request a demo</a> <a class="btn" href="../products.html" style="background:none;color:var(--on-y)">See products</a></div>'
                '<div class="rel"><h2>More guides</h2><div class="ac" style="background:none">%s</div></div></article>'
                % (html.escape(a['title']), a['tag'], TODAY, html.escape(a['short']), a['body'], faq, art_cards(rel, '')))
        url = 'articles/%s.html' % a['slug']
        schema = [{'@type': 'Article', 'headline': a['title'], 'description': a['desc'], 'datePublished': TODAY, 'dateModified': TODAY, 'inLanguage': 'en',
                   'author': {'@id': SITE + '/#org'}, 'publisher': {'@id': SITE + '/#org'}, 'mainEntityOfPage': SITE + '/' + url,
                   'image': SITE + '/img/og.png', 'isPartOf': {'@id': SITE + '/#website'}},
                  faq_ld(a['faq']), crumbs([('Home', ''), ('Articles', 'articles.html'), (a['title'], url)])]
        write(url, page(url, (a['title'] + ' | Nastaliq') if len(a['title']) <= 49 else a['title'], a['desc'], schema, body, pre='../', cur='art', og_type='article', en_only=True))
    cards = art_cards(ARTS)
    body = ('<section class="pagehead"><div class="in"><h1 style="max-width:16ch">Guides for small business owners</h1>'
            '<p class="lede" style="margin-top:20px">Plain advice on software, stock and running your shop. No jargon.</p></div></section>'
            '<section class="band"><div class="in"><div class="ac" style="margin-top:0">%s</div></div></section>' % cards)
    schema = [{'@type': 'CollectionPage', 'name': 'Articles', 'url': SITE + '/articles.html', 'isPartOf': {'@id': SITE + '/#website'}},
              {'@type': 'ItemList', 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': SITE + '/articles/%s.html' % a['slug'], 'name': a['title']} for i, a in enumerate(ARTS)]},
              crumbs([('Home', ''), ('Articles', 'articles.html')])]
    write('articles.html', page('articles.html', 'Articles for small business owners | Nastaliq',
          'Guides on choosing POS and inventory software, keeping stock accurate, bilingual systems in Canada and cloud versus on-premise software.', schema, body, cur='art', en_only=True))

# ---------------------------------------------------------------- home (hand-kept body; head, header, footer, FAQ regenerated)
def home():
    p = os.path.join(PUB, 'index.html')
    s = open(p, encoding='utf-8').read()
    m = re.search(r'<body>(.*?)</body>', s, re.S)
    inner = m.group(1)
    sprite = re.search(r'<svg width="0".*?</svg>', inner, re.S)
    sprite = sprite.group(0) if sprite else ''
    inner = re.sub(r'<svg width="0".*?</svg>', '', inner, count=1, flags=re.S)
    inner = re.sub(r'<a class="skip".*?</a>', '', inner, count=1, flags=re.S)
    inner = re.sub(r'<header>.*?</header>', '', inner, count=1, flags=re.S)
    inner = re.sub(r'<div class="in"><footer.*?</footer></div>', '', inner, flags=re.S)
    inner = re.sub(r'<script src="js/home.js"[^>]*></script>', '', inner)
    # wrap hero etc in <main>
    if '<main' not in inner:
        inner = '<main id="main">' + inner.strip() + '</main>'
    # FAQ block
    faq_html = ''.join('<details><summary>%s</summary><p>%s</p></details>' % (B(q, qf), B(a, af)) for q, qf, a, af in FAQ)
    inner = re.sub(r'(<section class="band" id="faq">.*?<div style="margin-top:30px;max-width:820px">).*?(</div>\s*</div>\s*</section>)',
                   lambda m2: m2.group(1) + faq_html + m2.group(2), inner, count=1, flags=re.S)
    app = {'@type': 'SoftwareApplication', 'name': 'Nastaliq', 'applicationCategory': 'BusinessApplication', 'operatingSystem': 'Web',
           'description': 'Cloud point of sale, inventory, purchasing, accounting and sales for small and mid-sized businesses, in English and French.',
           'url': SITE + '/', 'provider': {'@id': SITE + '/#org'}, 'inLanguage': ['en', 'fr'], 'featureList': ['Point of sale', 'Inventory with barcode scanning', 'Purchasing', 'Accounting', 'Sales', 'English and French']}
    schema = [{'@type': 'WebPage', '@id': SITE + '/#webpage', 'url': SITE + '/', 'name': 'Nastaliq', 'isPartOf': {'@id': SITE + '/#website'}, 'about': {'@id': SITE + '/#org'}},
              app, faq_ld([(q, a) for q, qf, a, af in FAQ])]
    h = head('', 'Nastaliq | Cloud POS, inventory and accounting',
             'Cloud business software for North American small businesses: POS, inventory, purchasing, accounting and sales in one system, in English and French.',
             schema)
    out = h + '<body>' + sprite + header('', '', True) + inner + footer('') + '<script src="js/home.js" defer></script></body></html>\n'
    write('index.html', out)

def seo_files():
    urls = [('', '1.0'), ('products.html', '0.8'), ('company.html', '0.6'), ('contact.html', '0.7'), ('articles.html', '0.8')] + [('articles/%s.html' % a['slug'], '0.7') for a in ARTS]
    write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + ''.join('<url><loc>%s/%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>\n' % (SITE, u, TODAY, pr) for u, pr in urls) + '</urlset>\n')
    bots = ['GPTBot', 'OAI-SearchBot', 'ChatGPT-User', 'ClaudeBot', 'Claude-SearchBot', 'Claude-User', 'PerplexityBot', 'Google-Extended', 'Applebot-Extended']
    write('robots.txt', 'User-agent: *\nAllow: /\n\n' + ''.join('User-agent: %s\nAllow: /\n\n' % b for b in bots) + 'Sitemap: %s/sitemap.xml\n' % SITE)
    prod = '\n'.join('- [%s](%s/products.html#%s): %s (%s)' % (p[4], SITE, p[0], p[6], p[2]) for p in PRODUCTS)
    art = '\n'.join('- [%s](%s/articles/%s.html): %s' % (a['title'], SITE, a['slug'], a['desc']) for a in ARTS)
    faq = '\n'.join('**%s** %s\n' % (q, a) for q, qf, a, af in FAQ)
    write('llms.txt', '# Nastaliq\n\n> Nastaliq LLP builds and hosts cloud business software for small and mid-sized businesses in North America: point of sale, inventory, purchasing, accounting and sales in one system, in English and French. Cloud only. Pricing is a flat monthly subscription with unlimited users plus a one-time setup fee, sent by email.\n\n'
          'Nastaliq LLP is incorporated with the Securities and Exchange Commission of Pakistan (SECP) and based in Lahore, Pakistan. Contact: %s\n\n## Pages\n- [Home](%s/): overview\n- [Products](%s/products.html): every product with its real status\n- [Company](%s/company.html): who we are\n- [Contact](%s/contact.html): how to reach us\n- [Articles](%s/articles.html): guides for small business owners\n\n## Products and status\n%s\n\n## Guides\n%s\n\n## Frequently asked questions\n%s\n'
          % (EMAIL, SITE, SITE, SITE, SITE, SITE, prod, art, faq))

if __name__ == '__main__':
    products(); company(); contact(); articles(); home(); seo_files()
    print('built')
