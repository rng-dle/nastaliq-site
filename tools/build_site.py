#!/usr/bin/env python3
"""Builds Nastaliq's static pages into public/. Run: python3 tools/build_site.py
- Generates products, company, contact, articles index and article pages.
- Rewrites the <head> (SEO/AEO metadata, JSON-LD), header, footer and FAQ block of the hand-kept public/index.html.
- Writes sitemap.xml, robots.txt, llms.txt.
Pricing never appears on the site: prices go out by email only."""
import html, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content_fr import FR as ARTS_FR

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB = os.path.join(ROOT, 'public')
SITE = 'https://nastaliq.co'
TODAY = '2026-10-26'
EMAIL = 'hello@nastaliq.co'
REG_NO = '0361484'   # SECP LLP incorporation number (certificate dated 16 October 2026)
REG_URL = 'https://leap.secp.gov.pk/#/verify-company-info/' + REG_NO
LEGAL_DATE = '2026-11-11'
UPDATED = '2026-11-11'   # sitemap lastmod; bump when pages change
FONT = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=Figtree:wght@400;500;600;700&display=swap">')

def x(s): return html.escape(s, quote=True)
LANG = 'en'
def B(en, fr, tag='span'):
    """pick the text for the language being built"""
    return fr if LANG == 'fr' else en

# ---------------------------------------------------------------- shared data
ORG = {
    '@type': 'Organization', '@id': SITE + '/#org', 'name': 'Nastaliq', 'legalName': 'Nastaliq LLP', 'url': SITE + '/',
    'logo': SITE + '/img/mark.svg', 'email': EMAIL, 'foundingDate': '2026-10-16',
    'identifier': {'@type': 'PropertyValue', 'propertyID': 'SECP LLP Incorporation No.', 'value': REG_NO},
    'description': 'Nastaliq builds and hosts cloud ERP for growing businesses in North America: inventory, purchasing, sales and accounting in one private system, in English and French.',
    'address': {'@type': 'PostalAddress', 'addressLocality': 'Lahore', 'addressCountry': 'PK'},
    'areaServed': ['CA', 'US'], 'knowsLanguage': ['en', 'fr'],
    'contactPoint': {'@type': 'ContactPoint', 'contactType': 'sales', 'email': EMAIL, 'availableLanguage': ['English', 'French']},
}
WEBSITE = {'@type': 'WebSite', '@id': SITE + '/#website', 'url': SITE + '/', 'name': 'Nastaliq', 'inLanguage': ['en', 'fr'], 'publisher': {'@id': SITE + '/#org'}}

PRODUCTS = [
    ('suite', 'ok', 'Available', 'Disponible', 'Business suite', "Suite d'affaires",
     'Inventory, purchasing, accounting and sales in one cloud system, set up for your business and hosted by us.',
     "Inventaire, achats, comptabilité et ventes dans un seul système infonuagique, configuré pour votre entreprise et hébergé par nous.", []),
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
    ('pos', 'warn', 'In development', 'En développement', 'Point of sale', 'Point de vente',
     'A clean, fast till for restaurants, fast food and bakeries.',
     'Une caisse rapide et épurée pour restaurants, restauration rapide et boulangeries.',
     [('Admin-editable colour themes', "Thèmes de couleurs modifiables par l'administrateur"), ('Built for counter speed', 'Pensé pour la vitesse au comptoir')]),
]

# FAQ shown on the home page AND emitted as FAQPage JSON-LD (text must match what is visible)
FAQ = [
    ('What is Nastaliq?', "Qu'est-ce que Nastaliq?",
     'Nastaliq is a cloud ERP for growing businesses in North America, typically companies with $1M or more in annual revenue. It puts inventory, purchasing, sales and accounting in one system, on your own private instance, in English and French. We set it up for your business and host it.',
     "Nastaliq est un ERP infonuagique pour les entreprises en croissance d'Amérique du Nord, généralement celles dont les revenus annuels atteignent 1 M$ ou plus. Il réunit stocks, achats, ventes et comptabilité dans un seul système, sur votre propre instance privée, en français et en anglais. Nous l'installons pour votre entreprise et l'hébergeons."),
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

# ---------------------------------------------------------------- language helpers
def lp(): return 'fr/' if LANG == 'fr' else ''
def art_t(a, k): return ARTS_FR[a['slug']][k] if LANG == 'fr' else a[k]

def levels(path):
    d = path.count('/')
    return '../' * d, '../' * (d + (1 if LANG == 'fr' else 0))   # (up within language folder, up to site root)

def alt_href(path):
    up, pre = levels(path)
    return (pre + path) if LANG == 'fr' else (up + 'fr/' + path)

# ---------------------------------------------------------------- fragments
def header(path, cur='', home=False):
    up, pre = levels(path)
    def l(href, en, fr, k=''):
        c = ' aria-current="page"' if cur == k and k else ''
        return '<a class="l" href="%s"%s>%s</a>' % (href, c, B(en, fr))
    extra = (l('#sectors', 'Industries', 'Secteurs') + l('#pricing', 'Pricing', 'Tarifs')) if home else ''
    en_h = (pre + path) if LANG == 'fr' else ''
    fr_h = alt_href(path) if LANG == 'en' else ''
    lang = ('<div class="lang" role="group" aria-label="%s"><a %s lang="en" hreflang="en">EN</a><a %s lang="fr" hreflang="fr">FR</a></div>'
            % (B('Language', 'Langue'),
               'aria-current="true"' if LANG == 'en' else 'href="%s"' % (pre + path),
               'aria-current="true"' if LANG == 'fr' else 'href="%s"' % fr_h))
    cta = '<a class="btn sm" href="%s">%s</a>' % ('#contact' if home else up + 'contact.html', B('Book a free demo', 'Réserver une démo gratuite'))
    top = ('<div class="top"><div class="in"><span>%s</span><div><a href="%scontact.html">Contact</a><a href="mailto:%s">%s</a></div></div></div>'
           % (B('Cloud ERP for growing businesses in North America', "ERP infonuagique pour les entreprises en croissance d'Amérique du Nord"), up, EMAIL, EMAIL))
    return ('<a class="skip" href="#main">%s</a>@@TOP@@<header><div class="in bar"><a class="logo" href="%sindex.html" aria-label="%s">'
            '<img class="mk" src="%simg/mark.svg" width="30" height="28" alt=""><img class="wd" src="%simg/wordmark.svg" width="55" height="15" alt="Nastaliq"></a>'
            '<nav id="nav" aria-label="%s">%s%s%s%s%s%s%s</nav>'
            '<button class="menu-btn" type="button" aria-expanded="false" aria-controls="nav" aria-label="Menu"><i></i><i></i></button></div></header>'
            % (B('Skip to content', 'Aller au contenu'), up, B('Nastaliq, home', 'Nastaliq, accueil'), pre, pre, B('Main', 'Principale'), extra,
               l(up + 'products.html', 'Products', 'Produits', 'products'), l(up + 'company.html', 'Company', 'Entreprise', 'company'),
               l(up + 'articles.html', 'Articles', 'Articles', 'art'), l(up + 'contact.html', 'Contact', 'Contact', 'contact'), lang, cta)).replace('@@TOP@@', top)

def footer(path):
    up, pre = levels(path)
    home = up + 'index.html'
    def col(title, links):
        return '<div><h3>%s</h3>%s</div>' % (title, ''.join('<a href="%s">%s</a>' % l for l in links))
    return ('<footer class="foot"><div class="in"><div class="fg"><div><a class="logo" href="%s" aria-label="Nastaliq"><img class="mk" src="%simg/mark.svg" width="32" height="30" alt=""><img class="wd" src="%simg/wordmark.svg" width="59" height="16" alt="Nastaliq"></a>'
            '<p>%s</p><p>%s</p><a href="mailto:%s">%s</a></div>%s%s%s</div>'
            '<p class="legal">&copy; 2026 Nastaliq LLP. %s %s. %s <i>|</i> <a href="%sprivacy.html">%s</a> <i>|</i> <a href="%sterms.html">%s</a></p></div></footer>'
            % (home, pre, pre,
               B('Cloud ERP for growing businesses: inventory, purchasing, sales and accounting in one private system, in English and French.',
                 "ERP infonuagique pour entreprises en croissance : stocks, achats, ventes et comptabilité dans un seul système privé, en français et en anglais."),
               B('Lahore, Pakistan, serving North America.', "Lahore, Pakistan, au service de l'Amérique du Nord."), EMAIL, EMAIL,
               col(B('Product', 'Produit'), [(up + 'products.html', B('Products', 'Produits')), (home + '#sectors', B('Industries', 'Secteurs')), (home + '#pricing', B('Pricing', 'Tarifs')), (home + '#faq', 'FAQ')]),
               col(B('Company', 'Entreprise'), [(up + 'company.html', B('About', 'À propos')), (up + 'articles.html', 'Articles'), (up + 'contact.html', 'Contact')]),
               col(B('Legal', 'Mentions légales'), [(up + 'privacy.html', B('Privacy Policy', 'Politique de confidentialité')), (up + 'terms.html', B('Terms of Service', "Conditions d'utilisation"))]),
               B('Registration No.', "N° d'immatriculation"), REG_NO, B('All rights reserved.', 'Tous droits réservés.'),
               up, B('Privacy Policy', 'Politique de confidentialité'), up, B('Terms of Service', "Conditions d'utilisation")))

def url_for(path, lang=None):
    lang = lang or LANG
    return SITE + '/' + ('fr/' if lang == 'fr' else '') + ('' if path == 'index.html' else path)

def head(path, title, desc, schema, og_type='website'):
    up, pre = levels(path)
    url = url_for(path)
    org = dict(ORG)
    if LANG == 'fr':
        org['description'] = "Nastaliq conçoit et héberge des un ERP infonuagique pour les entreprises en croissance d'Amérique du Nord : stocks, achats, ventes et comptabilité dans un seul système privé, en français et en anglais."
    web = dict(WEBSITE)
    graph = {'@context': 'https://schema.org', '@graph': [org, web] + schema}
    en, fr = url_for(path, 'en'), url_for(path, 'fr')
    oloc, oalt = ('fr_CA', 'en_CA') if LANG == 'fr' else ('en_CA', 'fr_CA')
    return ('<!doctype html>\n<html lang="%s"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
            '<title>%s</title><meta name="description" content="%s"><link rel="canonical" href="%s">'
            '<link rel="alternate" hreflang="en" href="%s"><link rel="alternate" hreflang="fr" href="%s"><link rel="alternate" hreflang="x-default" href="%s">'
            '<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1"><meta name="theme-color" content="#000000">'
            '<link rel="icon" href="%sfavicon.svg" type="image/svg+xml">'
            '<meta property="og:site_name" content="Nastaliq"><meta property="og:locale" content="%s"><meta property="og:locale:alternate" content="%s">'
            '<meta property="og:type" content="%s"><meta property="og:title" content="%s"><meta property="og:description" content="%s"><meta property="og:url" content="%s">'
            '<meta property="og:image" content="%s/img/og.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="%s">'
            '<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="%s"><meta name="twitter:description" content="%s"><meta name="twitter:image" content="%s/img/og.png">'
            '%s<link rel="stylesheet" href="%scss/home.css">'
            '<script type="application/ld+json">%s</script></head>'
            % (LANG, x(title), x(desc), url, en, fr, en, pre, oloc, oalt, og_type, x(title), x(desc), url, SITE,
               B('Nastaliq: cloud ERP for growing businesses', "Nastaliq : ERP infonuagique pour entreprises en croissance"),
               x(title), x(desc), SITE, FONT, pre, json.dumps(graph, ensure_ascii=False, separators=(',', ':'))))

def page(path, title, desc, schema, body, cur='', og_type='website'):
    up, pre = levels(path)
    return (head(path, title, desc, schema, og_type) + '<body>' + header(path, cur) + '<main id="main">' + body + '</main>'
            + footer(path) + '<script src="%sjs/home.js" defer></script></body></html>\n' % pre)

def crumbs(items):
    return {'@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': u} for i, (n, u) in enumerate(items)]}

def faq_ld(pairs):
    return {'@type': 'FAQPage', 'inLanguage': LANG, 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in pairs]}

def write(path, s):
    p = os.path.join(PUB, lp() + path); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8').write(s)

def hero(h1en, h1fr, lede_en, lede_fr):
    return ('<section class="pagehead"><div class="in"><h1 style="max-width:20ch">%s</h1><p class="lede">%s</p></div></section>'
            % (B(h1en, h1fr), B(lede_en, lede_fr)))

def badge(cls, en, fr):
    return '<span class="tag%s">%s</span>' % (' w' if cls == 'warn' else '', B(en, fr))

def pg(path, name_en, name_fr):
    return (name_fr if LANG == 'fr' else name_en, url_for(path))

# ---------------------------------------------------------------- products
def products():
    cards = ''
    for pid, cls, sen, sfr, ten, tfr, den, dfr, ul in PRODUCTS:
        li = ('<ul>' + ''.join('<li>%s</li>' % B(e, f) for e, f in ul) + '</ul>') if ul else ''
        cards += '<article class="pcard" id="%s">%s<h2>%s</h2><p>%s</p>%s</article>' % (pid, badge(cls, sen, sfr), B(ten, tfr), B(den, dfr), li)
    body = (hero('What we build and where it stands.', 'Ce que nous construisons et où nous en sommes.',
                 'Every product carries a status. Available means clients can use it today. Anything else says so.',
                 "Chaque produit affiche son état. Disponible signifie que des clients peuvent l'utiliser aujourd'hui. Tout le reste est indiqué.")
            + '<section class="band"><div class="in"><div class="pgrid">' + cards + '</div></div></section>'
            + '<section class="band" style="padding-top:0"><div class="in"><div class="cta2"><h2>%s</h2><p>%s</p><a class="btn" href="contact.html">%s</a></div></div></section>'
            % (B('Tell us what you run', 'Dites-nous ce que vous exploitez'),
               B('We reply by email with a plan and a price.', 'Nous répondons par courriel avec un plan et un prix.'),
               B('Get in touch', 'Nous joindre')))
    items = [{'@type': 'ListItem', 'position': i + 1, 'item': {'@type': 'SoftwareApplication', 'name': B(p[4], p[5]), 'description': B(p[6], p[7]), 'applicationCategory': 'BusinessApplication',
              'operatingSystem': 'Web', 'url': url_for('products.html') + '#' + p[0], 'provider': {'@id': SITE + '/#org'}}} for i, p in enumerate(PRODUCTS)]
    schema = [{'@type': 'CollectionPage', 'name': B('Nastaliq products', 'Produits Nastaliq'), 'url': url_for('products.html'), 'inLanguage': LANG, 'isPartOf': {'@id': SITE + '/#website'}},
              {'@type': 'ItemList', 'name': B('Nastaliq products', 'Produits Nastaliq'), 'itemListElement': items},
              crumbs([pg('index.html', 'Home', 'Accueil'), pg('products.html', 'Products', 'Produits')])]
    write('products.html', page('products.html',
          B('Nastaliq Products | Inventory, purchasing, sales, accounting', 'Produits Nastaliq | Stocks, achats, ventes, comptabilité'),
          B('What Nastaliq builds and where each product stands: business suite, janitorial operations, owner dashboard, English and French, and point of sale.',
            "Ce que Nastaliq conçoit et où en est chaque produit : suite d'affaires, point de vente, entretien ménager et tableau de bord."),
          schema, body, cur='products'))

# ---------------------------------------------------------------- company
def company():
    facts = [('Legal name', 'Raison sociale', 'Nastaliq LLP', 'Nastaliq LLP'),
             ('Registered', 'Immatriculation', 'Incorporated on 16 October 2026 with the Securities and Exchange Commission of Pakistan (SECP) under the Limited Liability Partnership Act, 2017.', 'Constituée le 16 octobre 2026 auprès de la Securities and Exchange Commission of Pakistan (SECP), en vertu de la Limited Liability Partnership Act, 2017.'),
             ('Registration No.', "N° d'immatriculation", '%s (<a href="%s" rel="noopener">verify with SECP</a>)' % (REG_NO, REG_URL), '%s (<a href="%s" rel="noopener">vérifier auprès de la SECP</a>)' % (REG_NO, REG_URL)),
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
                 'Nastaliq builds and hosts a cloud ERP for growing businesses in North America.',
                 "Nastaliq conçoit et héberge un ERP infonuagique pour les entreprises en croissance d'Amérique du Nord.")
            + '<section class="band"><div class="in"><h2>%s</h2><dl class="facts">%s</dl></div></section>' % (B('Who we are', 'Qui nous sommes'), dl)
            + '<section class="band paper"><div class="in"><h2>%s</h2><div class="f4">%s</div></div></section>' % (B('How we work with clients', 'Notre façon de travailler avec nos clients'), cards))
    schema = [{'@type': 'AboutPage', 'name': B('About Nastaliq', 'À propos de Nastaliq'), 'url': url_for('company.html'), 'inLanguage': LANG, 'about': {'@id': SITE + '/#org'}, 'isPartOf': {'@id': SITE + '/#website'}},
              crumbs([pg('index.html', 'Home', 'Accueil'), pg('company.html', 'Company', 'Entreprise')])]
    write('company.html', page('company.html', B('About Nastaliq LLP | Cloud business software team', 'À propos de Nastaliq LLP | Équipe de logiciels infonuagiques'),
          B('Nastaliq LLP builds and hosts a cloud ERP for growing businesses in North America. Registered with SECP, based in Lahore, Pakistan.',
            "Nastaliq LLP conçoit et héberge des logiciels d'affaires infonuagiques pour les PME d'Amérique du Nord. Établie à Lahore, au Pakistan."),
          schema, body, cur='company'))

# ---------------------------------------------------------------- contact
def contact():
    steps = [('What you sell', 'Ce que vous vendez', 'Products, services, or both.', 'Produits, services, ou les deux.'),
             ('Your locations', 'Vos emplacements', 'How many, and where.', 'Combien, et où.'),
             ('What you use today', "Ce que vous utilisez aujourd'hui", 'Spreadsheets, accounting software, another system.', 'Tableurs, logiciel comptable, un autre système.')]
    li = ''.join('<li><b>%s</b><span>%s</span></li>' % (B(a, b), B(c, d)) for a, b, c, d in steps)
    subj = B('Nastaliq%20demo%20request', 'Demande%20de%20d%C3%A9mo%20Nastaliq')
    body = (hero('Tell us about your business.', 'Parlez-nous de votre entreprise.',
                 'Write to us with what you sell, how many locations you run, and what you use today. We reply by email with a plan and a price.',
                 "Écrivez-nous ce que vous vendez, combien d'emplacements vous exploitez et ce que vous utilisez aujourd'hui. Nous répondons par courriel avec un plan et un prix.")
            + '<section class="band"><div class="in"><div class="cbox" id="contact"><div><h2>%s</h2><p class="lede">%s</p>'
              '<p class="mail">%s<button type="button" class="copy" id="cp" data-done="%s">%s</button></p></div>'
              '<div><a class="btn dk" href="mailto:%s?subject=%s">%s</a>'
              '<ol class="steps">%s</ol></div></div></div></section>'
            % (B('Email us', 'Écrivez-nous'), B('Pricing is sent by email: a flat monthly subscription with unlimited users plus a one-time setup fee.',
                 "Le tarif est envoyé par courriel : un abonnement mensuel fixe avec utilisateurs illimités, plus des frais d'installation uniques."),
               EMAIL, B('Copied', 'Copié'), B('Copy', 'Copier'), EMAIL, subj, B('Email us', 'Écrivez-nous'), li))
    schema = [{'@type': 'ContactPage', 'name': B('Contact Nastaliq', 'Joindre Nastaliq'), 'url': url_for('contact.html'), 'inLanguage': LANG, 'about': {'@id': SITE + '/#org'}, 'isPartOf': {'@id': SITE + '/#website'}},
              crumbs([pg('index.html', 'Home', 'Accueil'), pg('contact.html', 'Contact', 'Contact')])]
    write('contact.html', page('contact.html', B('Contact Nastaliq | Get a plan and a price by email', 'Joindre Nastaliq | Un plan et un prix par courriel'),
          B('Tell Nastaliq what you sell, how many locations you run and what you use today. We reply by email with a plan and a price.',
            "Dites-nous ce que vous vendez et ce que vous utilisez aujourd'hui. Nous répondons par courriel avec un plan et un prix."),
          schema, body, cur='contact'))

# ---------------------------------------------------------------- articles
def art_cards(items, base='articles/', h='h3'):
    return ''.join('<a href="%s%s.html"><small>%s</small><%s>%s</%s><p>%s</p></a>' % (base, a['slug'], art_t(a, 'tag'), h, html.escape(art_t(a, 'title')), h, html.escape(art_t(a, 'desc'))) for a in items)

def articles():
    for a in ARTS:
        rel = [b for b in ARTS if b['slug'] != a['slug']]
        faqs = art_t(a, 'faq')
        faq = ''.join('<details><summary>%s</summary><p>%s</p></details>' % (html.escape(q), html.escape(ans)) for q, ans in faqs)
        date_h = B('October 26, 2026', '26 octobre 2026')
        body = ('<article class="in art"><div class="crumb"><a href="../index.html">%s</a> / <a href="../articles.html">Articles</a></div>'
                '<h1>%s</h1><p class="meta">%s &middot; %s <time datetime="%s">%s</time> &middot; %s</p>'
                '<div class="short"><b>%s</b><p>%s</p></div>'
                '<div class="prose">%s</div>'
                '<section class="prose faq-s"><h2>%s</h2>%s</section>'
                '<div class="cta"><h3>%s</h3><p>%s</p>'
                '<a class="btn" href="../contact.html">%s</a> <a class="btn" href="../products.html">%s</a></div>'
                '<div class="rel"><h2>%s</h2><div class="ac">%s</div></div></article>'
                % (B('Home', 'Accueil'), html.escape(art_t(a, 'title')), art_t(a, 'tag'), B('Published', 'Publié le'), TODAY, date_h, B('By the Nastaliq team', "Par l'équipe Nastaliq"),
                   B('The short answer', 'La réponse courte'), html.escape(art_t(a, 'short')), art_t(a, 'body'),
                   B('Common questions', 'Questions fréquentes'), faq,
                   B('See Nastaliq with your business loaded', 'Voyez Nastaliq avec votre entreprise'),
                   B('Tell us what you sell and how you run today. We reply by email with a plan and a price.', "Dites-nous ce que vous vendez et comment vous fonctionnez aujourd'hui. Nous répondons par courriel avec un plan et un prix."),
                   B('Book a free demo', 'Réserver une démo gratuite'), B('See products', 'Voir les produits'),
                   B('More guides', "D'autres guides"), art_cards(rel, '')))
        path = 'articles/%s.html' % a['slug']
        title = art_t(a, 'title')
        suffix = ' | Nastaliq'
        schema = [{'@type': 'Article', 'headline': title, 'description': art_t(a, 'desc'), 'datePublished': TODAY, 'dateModified': TODAY, 'inLanguage': LANG,
                   'author': {'@id': SITE + '/#org'}, 'publisher': {'@id': SITE + '/#org'}, 'mainEntityOfPage': url_for(path),
                   'image': SITE + '/img/og.png', 'isPartOf': {'@id': SITE + '/#website'}},
                  faq_ld(faqs), crumbs([pg('index.html', 'Home', 'Accueil'), pg('articles.html', 'Articles', 'Articles'), (title, url_for(path))])]
        write(path, page(path, (title + suffix) if len(title) <= 49 else title, art_t(a, 'desc'), schema, body, cur='art', og_type='article'))
    body = ('<section class="pagehead"><div class="in"><h1 style="max-width:18ch">%s</h1>'
            '<p class="lede">%s</p></div></section>'
            '<section class="band paper"><div class="in"><div class="ac">%s</div></div></section>'
            % (B('Guides for business owners', "Des guides pour les propriétaires d'entreprise"),
               B('Plain advice on software, stock and running your operations. No jargon.', 'Des conseils clairs sur les logiciels, les stocks et la gestion de vos opérations. Sans jargon.'),
               art_cards(ARTS, h='h2')))
    schema = [{'@type': 'CollectionPage', 'name': 'Articles', 'url': url_for('articles.html'), 'inLanguage': LANG, 'isPartOf': {'@id': SITE + '/#website'}},
              {'@type': 'ItemList', 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': url_for('articles/%s.html' % a['slug']), 'name': art_t(a, 'title')} for i, a in enumerate(ARTS)]},
              crumbs([pg('index.html', 'Home', 'Accueil'), pg('articles.html', 'Articles', 'Articles')])]
    write('articles.html', page('articles.html', B('Articles for small business owners | Nastaliq', 'Articles pour propriétaires de petites entreprises | Nastaliq'),
          B('Guides on choosing POS and inventory software, keeping stock accurate, bilingual systems in Canada and cloud versus on-premise software.',
            "Guides pour choisir un logiciel de caisse, garder des stocks exacts, adopter un système bilingue et comparer infonuagique et sur place."),
          schema, body, cur='art'))

# ---------------------------------------------------------------- legal
LEGAL = {
 'privacy.html': dict(
   t=('Privacy Policy', 'Politique de confidentialité'),
   d=('How Nastaliq LLP handles personal information on nastaliq.co and when you contact us.', "Comment Nastaliq LLP traite les renseignements personnels sur nastaliq.co et lorsque vous nous écrivez."),
   s=[(('Who we are', 'Qui nous sommes'),
       ('Nastaliq LLP is a limited liability partnership incorporated with the Securities and Exchange Commission of Pakistan (Registration No. %s), based in Lahore, Pakistan. This policy covers the website nastaliq.co and the messages you send us. You can reach us at <a href="mailto:%s">%s</a>.' % (REG_NO, EMAIL, EMAIL),
        "Nastaliq LLP est une société à responsabilité limitée constituée auprès de la Securities and Exchange Commission of Pakistan (n° d'immatriculation %s), établie à Lahore, au Pakistan. La présente politique couvre le site nastaliq.co et les messages que vous nous envoyez. Vous pouvez nous joindre à <a href=\"mailto:%s\">%s</a>." % (REG_NO, EMAIL, EMAIL))),
      (('What this website collects', 'Ce que ce site recueille'),
       ('The website has no accounts, no advertising trackers and no analytics scripts, and we set no cookies of our own. The demo form on the home page does not send anything to our servers: it opens your own email app with your answers filled in, and nothing reaches us unless you send that email.',
        "Le site n'a ni comptes, ni traceurs publicitaires, ni scripts d'analyse, et nous ne déposons aucun témoin. Le formulaire de démo de la page d'accueil n'envoie rien à nos serveurs : il ouvre votre application de courriel avec vos réponses, et rien ne nous parvient tant que vous n'envoyez pas ce courriel.")),
      (('Service providers', 'Fournisseurs de services'),
       ('The site is delivered through a content delivery network and loads its fonts from Google Fonts. Like any web host, these providers process technical data such as your IP address and browser type in order to deliver pages and keep the service secure.',
        "Le site est diffusé par un réseau de diffusion de contenu et charge ses polices depuis Google Fonts. Comme tout hébergeur, ces fournisseurs traitent des données techniques, comme votre adresse IP et votre type de navigateur, pour livrer les pages et protéger le service.")),
      (('When you email us', 'Lorsque vous nous écrivez'),
       ('If you write to us, we keep your name, email address, business details and the content of your message. We use them to reply, prepare a demo and send you a plan and a price. We do not sell personal information, and we do not share it except with the email providers that carry and store our mail.',
        "Si vous nous écrivez, nous conservons votre nom, votre adresse courriel, les renseignements sur votre entreprise et le contenu de votre message. Nous les utilisons pour vous répondre, préparer une démo et vous envoyer un plan et un prix. Nous ne vendons pas de renseignements personnels et ne les partageons qu'avec les fournisseurs de courriel qui acheminent et conservent nos messages.")),
      (('Client systems', 'Systèmes des clients'),
       ('Data that clients keep inside the business software we host for them is handled under the agreement with that client, not under this website policy.',
        "Les données que les clients conservent dans le logiciel que nous hébergeons pour eux sont traitées selon l'entente conclue avec ce client, et non selon la présente politique.")),
      (('Your choices', 'Vos choix'),
       ('You can ask us to show you, correct or delete the personal information we hold about you by writing to <a href="mailto:%s">%s</a>. We answer within a reasonable time.' % (EMAIL, EMAIL),
        "Vous pouvez nous demander de consulter, de corriger ou de supprimer les renseignements personnels que nous détenons à votre sujet en écrivant à <a href=\"mailto:%s\">%s</a>. Nous répondons dans un délai raisonnable." % (EMAIL, EMAIL))),
      (('Changes', 'Modifications'),
       ('If this policy changes, the new version is posted on this page with a new date.', "Si la présente politique change, la nouvelle version est publiée sur cette page avec une nouvelle date."))]),
 'terms.html': dict(
   t=('Terms of Service', "Conditions d'utilisation"),
   d=('The terms that apply when you use the nastaliq.co website.', "Les conditions qui s'appliquent lorsque vous utilisez le site nastaliq.co."),
   s=[(('About these terms', 'À propos de ces conditions'),
       ('These terms apply to the website nastaliq.co, operated by Nastaliq LLP (Registration No. %s). By using the site you agree to them. The business software we provide to clients is covered by a separate written agreement with each client.' % REG_NO,
        "Les présentes conditions s'appliquent au site nastaliq.co, exploité par Nastaliq LLP (n° d'immatriculation %s). En utilisant le site, vous les acceptez. Le logiciel d'affaires que nous fournissons aux clients fait l'objet d'une entente écrite distincte avec chaque client." % REG_NO)),
      (('Information on the site', 'Information sur le site'),
       ('The site describes our products for general information. Each feature shows its status: Available, Early access, In development or Planned. Screens shown on the site use sample data. Guides and articles are general information and are not legal, tax or accounting advice.',
        "Le site décrit nos produits à titre d'information générale. Chaque fonction affiche son état : Offert, Accès anticipé, En développement ou Prévu. Les écrans présentés utilisent des données d'exemple. Les guides et articles sont de l'information générale et ne constituent pas des conseils juridiques, fiscaux ou comptables.")),
      (('Pricing and offers', 'Tarifs et offres'),
       ('Nothing on the site is a binding offer. Plans and prices are sent by email and take effect only in a written agreement.',
        "Rien sur le site ne constitue une offre ferme. Les plans et les prix sont envoyés par courriel et ne prennent effet que dans une entente écrite.")),
      (('Our content', 'Notre contenu'),
       ('The Nastaliq name, logo, text and designs on the site belong to Nastaliq LLP. You may link to the site and quote short passages with credit. Please do not copy the site or pass it off as your own.',
        "Le nom Nastaliq, le logo, les textes et les éléments graphiques du site appartiennent à Nastaliq LLP. Vous pouvez créer des liens vers le site et en citer de courts passages en mentionnant la source. Veuillez ne pas copier le site ni le présenter comme le vôtre.")),
      (('Acceptable use', 'Utilisation acceptable'),
       ('Do not use the site in a way that breaks the law, disrupts the service or attempts to gain unauthorised access to it.',
        "N'utilisez pas le site d'une manière qui enfreint la loi, perturbe le service ou tente d'y accéder sans autorisation.")),
      (('Liability', 'Responsabilité'),
       ('The site is provided as is. To the extent the law allows, Nastaliq LLP is not liable for loss arising from use of the site or reliance on its content. Links to other websites are provided for convenience and we are not responsible for their content.',
        "Le site est fourni tel quel. Dans la mesure permise par la loi, Nastaliq LLP n'est pas responsable des pertes découlant de l'utilisation du site ou de la confiance accordée à son contenu. Les liens vers d'autres sites sont fournis par commodité et nous ne sommes pas responsables de leur contenu.")),
      (('Governing law and contact', 'Droit applicable et contact'),
       ('These terms are governed by the laws of Pakistan. Questions about them can be sent to <a href="mailto:%s">%s</a>.' % (EMAIL, EMAIL),
        "Les présentes conditions sont régies par les lois du Pakistan. Vos questions peuvent être envoyées à <a href=\"mailto:%s\">%s</a>." % (EMAIL, EMAIL)))]),
}

def legal():
    for path, L in LEGAL.items():
        title = B(*L['t'])
        secs = ''.join('<h2>%s</h2><p>%s</p>' % (B(*h), B(*p)) for h, p in L['s'])
        body = ('<article class="in art"><div class="crumb"><a href="index.html">%s</a> / %s</div><h1>%s</h1>'
                '<p class="meta">%s <time datetime="%s">%s</time></p><div class="prose">%s</div></article>'
                % (B('Home', 'Accueil'), title, title, B('Last updated', 'Dernière mise à jour :'), LEGAL_DATE, B('November 11, 2026', '11 novembre 2026'), secs))
        schema = [{'@type': 'WebPage', 'name': title, 'url': url_for(path), 'inLanguage': LANG, 'isPartOf': {'@id': SITE + '/#website'}},
                  crumbs([pg('index.html', 'Home', 'Accueil'), (title, url_for(path))])]
        write(path, page(path, title + ' | Nastaliq', B(*L['d']), schema, body))

# ---------------------------------------------------------------- home (template in tools/home.tpl.html)
MOCK_FR = {
 'Home': 'Accueil', 'Sales': 'Ventes', 'Stock': 'Stocks', 'Purchasing': 'Achats', 'Accounts': 'Comptabilité', 'Reports': 'Rapports',
 'Good morning, Sam': 'Bonjour, Sam', 'Sample data': "Données d'exemple", 'Sales today': "Ventes aujourd'hui", '$4,280': '4 280 $', 'Open orders': 'Commandes ouvertes',
 '3 due today': "3 à livrer aujourd'hui", 'Below reorder': 'Sous le seuil', 'Act today': "À traiter aujourd'hui", 'Unpaid bills': 'Factures impayées', '$9,115': '9 115 $',
 '5 suppliers': '5 fournisseurs', 'Sales this week, CAD thousands': 'Ventes de la semaine, en milliers de $ CA',
 'Mon': 'Lun', 'Tue': 'Mar', 'Wed': 'Mer', 'Thu': 'Jeu', 'Fri': 'Ven', 'Sat': 'Sam', 'Sun': 'Dim',
 'Order #1042': 'Commande 1042', 'Order #1041': 'Commande 1041', '$612.00': '612,00 $', '$1,480.00': '1 480,00 $', 'Paid': 'Payée', 'Due Fri': 'Échéance ven.',
 'Receive stock': 'Réception de stock', 'Warehouse A': 'Entrepôt A', 'Floor cleaner 5L': 'Nettoyant à plancher 5 L', 'Nitrile gloves M': 'Gants de nitrile M',
 'Mop heads': 'Têtes de vadrouille', '3 left': '3 restantes', 'Trash bags 55gal': 'Sacs à ordures 55 gal', 'Scan barcode': 'Numériser un code-barres',
 'Mop heads: 3 left': 'Têtes de vadrouille : 3 restantes', 'Reorder suggested': 'Réapprovisionnement suggéré', 'Order #1042 paid': 'Commande 1042 payée',
 '$612.00 from Maple Café': '612,00 $ de Maple Café', 'Purchase orders': "Bons de commande", 'Received': 'Reçu', 'In transit': 'En transit', 'Overdue': 'En retard', 'Draft': 'Brouillon',
 '$2,140': '2 140 $', '$860': '860 $', '$3,975': '3 975 $', '$1,210': '1 210 $', 'Checkout': 'Caisse', 'Stock count': 'Inventaire', 'Matches': 'Conforme', 'Short 2': 'Manque 2', 'Over 1': 'Surplus 1',
 'Tote bag': 'Sac fourre-tout', 'Candle': 'Bougie', 'Mug': 'Tasse', 'Notebook': 'Carnet', 'Cap': 'Casquette', 'Tee': 'T-shirt', 'Total': 'Total',
 '$18': '18 $', '$24': '24 $', '$14': '14 $', '$12': '12 $', '$22': '22 $', '$30': '30 $', '$18.00': '18,00 $', '$14.00': '14,00 $',
 'Order 27': 'Commande 27', 'Croissant': 'Croissant', 'Latte': 'Latte', 'Sourdough': 'Pain au levain', 'Cookie': 'Biscuit', 'Quiche': 'Quiche', 'Tea': 'Thé',
 '$4': '4 $', '$5': '5 $', '$9': '9 $', '$3': '3 $', '$8': '8 $',
 'Lobby inspection': "Inspection du hall d'entrée", 'Floors mopped': 'Planchers lavés', 'Restrooms restocked': 'Toilettes réapprovisionnées',
 'Windows wiped': 'Fenêtres nettoyées', 'Photo of finished lobby': 'Photo du hall terminé', 'Pilot': 'Pilote', 'Copy': 'Copier',
 '$3,100': '3 100 $', '$2,020': '2 020 $', '$1,300': '1 300 $',
}

def home():
    tpl = open(os.path.join(ROOT, 'tools', 'home.tpl.html'), encoding='utf-8').read()
    sprite = re.search(r'<svg width="0".*?</svg>', tpl, re.S).group(0)
    main = re.search(r'<main id="main">.*?</main>', tpl, re.S).group(0)
    idx = 1 if LANG == 'fr' else 0
    main = re.sub(r'<span class="en">(.*?)</span><span class="fr">(.*?)</span>', lambda m: m.group(1 + idx), main, flags=re.S)
    if LANG == 'fr':
        for k in sorted(MOCK_FR, key=len, reverse=True):
            main = main.replace('>' + k + '<', '>' + MOCK_FR[k] + '<')
        main = main.replace('acme-supply.nastaliq.co', 'acme-fournitures.nastaliq.co').replace('ACME SUPPLY', 'ACME FOURNITURES').replace('>Elm Dental<', '>Clinique Elm<').replace('>North Gym<', '>Gym du Nord<')
    faq_html = ''.join('<details><summary>%s</summary><p>%s</p></details>' % (B(q, qf), B(a, af)) for q, qf, a, af in FAQ)
    main = main.replace('<!--FAQ-->', faq_html).replace('<!--ARTS-->', art_cards(ARTS))
    for k, v in (('@@COPIED@@', B('Copied', 'Copié')), ('@@SUBJECT@@', B('Nastaliq demo request', 'Demande de démo Nastaliq')), ('@@L_NAME@@', B('Name', 'Nom')),
                 ('@@L_BIZ@@', B('Business', 'Entreprise')), ('@@L_IND@@', B('Industry', 'Secteur')), ('@@L_TODAY@@', B('Using today', "Utilise aujourd'hui"))):
        main = main.replace(k, v)
    assert '@@' not in main and '<!--' not in main
    app = {'@type': 'SoftwareApplication', 'name': 'Nastaliq', 'applicationCategory': 'BusinessApplication', 'operatingSystem': 'Web',
           'description': B('Cloud ERP for growing businesses: inventory, purchasing, sales and accounting on a private instance, in English and French.',
                            'ERP infonuagique pour entreprises en croissance : stocks, achats, ventes et comptabilité sur une instance privée, en français et en anglais.'),
           'url': url_for('index.html'), 'provider': {'@id': SITE + '/#org'}, 'inLanguage': ['en', 'fr'],
           'featureList': B(['Inventory with barcode scanning', 'Purchasing', 'Accounting', 'Sales', 'English and French'],
                            ['Inventaire avec codes-barres', 'Achats', 'Comptabilité', 'Ventes', 'Français et anglais'])}
    schema = [{'@type': 'WebPage', '@id': url_for('index.html') + '#webpage', 'url': url_for('index.html'), 'name': 'Nastaliq', 'inLanguage': LANG,
               'isPartOf': {'@id': SITE + '/#website'}, 'about': {'@id': SITE + '/#org'}}, app, faq_ld([(B(q, qf), B(a, af)) for q, qf, a, af in FAQ])]
    title = B('Nastaliq | Cloud ERP for inventory, sales and accounting', 'Nastaliq | ERP infonuagique : stocks, ventes, comptabilité')
    desc = B('Cloud ERP for growing North American businesses: inventory, purchasing, sales and accounting in one private system, in English and French.',
             "ERP infonuagique pour entreprises en croissance : stocks, achats, ventes et comptabilité dans un seul système privé, bilingue.")
    out = head('index.html', title, desc, schema) + '<body>' + sprite + header('index.html', '', True) + main + footer('index.html') + '<script src="js/home.js" defer></script></body></html>\n'
    out = out.replace('src="js/home.js"', 'src="%sjs/home.js"' % levels('index.html')[1])
    write('index.html', out)

def seo_files():
    pages = [('index.html', '1.0'), ('products.html', '0.8'), ('company.html', '0.6'), ('contact.html', '0.7'), ('articles.html', '0.8')] + [('articles/%s.html' % a['slug'], '0.7') for a in ARTS] + [('privacy.html', '0.3'), ('terms.html', '0.3')]
    rows = ''
    for p, pr in pages:
        for lg in ('en', 'fr'):
            alts = ''.join('<xhtml:link rel="alternate" hreflang="%s" href="%s"/>' % (l2, url_for(p, l2)) for l2 in ('en', 'fr')) + '<xhtml:link rel="alternate" hreflang="x-default" href="%s"/>' % url_for(p, 'en')
            rows += '<url><loc>%s</loc><lastmod>%s</lastmod><priority>%s</priority>%s</url>\n' % (url_for(p, lg), UPDATED, pr, alts)
    open(os.path.join(PUB, 'sitemap.xml'), 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + rows + '</urlset>\n')
    bots = ['GPTBot', 'OAI-SearchBot', 'ChatGPT-User', 'ClaudeBot', 'Claude-SearchBot', 'Claude-User', 'PerplexityBot', 'Google-Extended', 'Applebot-Extended']
    open(os.path.join(PUB, 'robots.txt'), 'w').write('User-agent: *\nAllow: /\n\n' + ''.join('User-agent: %s\nAllow: /\n\n' % b for b in bots) + 'Sitemap: %s/sitemap.xml\n' % SITE)
    for lg in ('en', 'fr'):
        fr = lg == 'fr'
        prod = '\n'.join('- [%s](%s#%s): %s (%s)' % (p[5] if fr else p[4], url_for('products.html', lg), p[0], p[7] if fr else p[6], p[3] if fr else p[2]) for p in PRODUCTS)
        art = '\n'.join('- [%s](%s): %s' % (ARTS_FR[a['slug']]['title'] if fr else a['title'], url_for('articles/%s.html' % a['slug'], lg), ARTS_FR[a['slug']]['desc'] if fr else a['desc']) for a in ARTS)
        faq = '\n'.join('**%s** %s\n' % ((qf, af) if fr else (q, a)) for q, qf, a, af in FAQ)
        if fr:
            txt = ('# Nastaliq\n\n> Nastaliq LLP conçoit et héberge des un ERP infonuagique pour les entreprises en croissance d\'Amérique du Nord : stocks, achats, ventes et comptabilité dans un seul système privé, en français et en anglais. Infonuagique seulement. Le tarif est un abonnement mensuel fixe avec utilisateurs illimités, plus des frais d\'installation uniques, envoyé par courriel.\n\n'
                   'Nastaliq LLP est constituée auprès de la Securities and Exchange Commission of Pakistan (SECP) et établie à Lahore, au Pakistan. Courriel : %s\n\n## Pages\n- [Accueil](%s)\n- [Produits](%s)\n- [Entreprise](%s)\n- [Contact](%s)\n- [Articles](%s)\n\n## Produits et état\n%s\n\n## Guides\n%s\n\n## Questions fréquentes\n%s\n'
                   % (EMAIL, url_for('index.html', lg), url_for('products.html', lg), url_for('company.html', lg), url_for('contact.html', lg), url_for('articles.html', lg), prod, art, faq))
            os.makedirs(os.path.join(PUB, 'fr'), exist_ok=True)
            open(os.path.join(PUB, 'fr', 'llms.txt'), 'w').write(txt)
        else:
            txt = ('# Nastaliq\n\n> Nastaliq LLP builds and hosts cloud ERP for growing businesses in North America: inventory, purchasing, sales and accounting in one private system, in English and French. Cloud only. Pricing is a flat monthly subscription with unlimited users plus a one-time setup fee, sent by email.\n\n'
                   'Nastaliq LLP is incorporated with the Securities and Exchange Commission of Pakistan (SECP) and based in Lahore, Pakistan. Contact: %s\n\nFrench version: %s/fr/llms.txt\n\n## Pages\n- [Home](%s)\n- [Products](%s)\n- [Company](%s)\n- [Contact](%s)\n- [Articles](%s)\n\n## Products and status\n%s\n\n## Guides\n%s\n\n## Frequently asked questions\n%s\n'
                   % (EMAIL, SITE, url_for('index.html', lg), url_for('products.html', lg), url_for('company.html', lg), url_for('contact.html', lg), url_for('articles.html', lg), prod, art, faq))
            open(os.path.join(PUB, 'llms.txt'), 'w').write(txt)

if __name__ == '__main__':
    for LANG in ('en', 'fr'):
        products(); company(); contact(); articles(); legal(); home()
    seo_files()
    print('built')
