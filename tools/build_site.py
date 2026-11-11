#!/usr/bin/env python3
"""Builds Nastaliq's static pages into public/. Run: python3 tools/build_site.py
- Generates products, company, contact, articles index and article pages.
- Rewrites the <head> (SEO/AEO metadata, JSON-LD), header, footer and FAQ block of the hand-kept public/index.html.
- Writes sitemap.xml, robots.txt, llms.txt.
Pricing never appears on the site: prices go out by email only."""
import html, json, os, posixpath, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content_en import ARTS
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
# Article author. None = "the Nastaliq team". To name a person:
# AUTHOR = dict(name='Full Name', role=('Partner, Nastaliq LLP', 'Associé, Nastaliq LLP'), url='https://www.linkedin.com/in/...')
AUTHOR = None
NEW_ARTS = {'outgrowing-spreadsheets-and-accounting-software', 'how-to-choose-an-erp', 'private-cloud-erp-vs-saas-vs-on-premise'}   # published 2026-11-11; the rest on TODAY
SAME_AS = []   # public profiles of the company (LinkedIn page, directory listings); emitted as schema sameAs
FONT = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=Figtree:wght@400;500;600;700&display=swap">')

def x(s): return html.escape(s, quote=True)
LANG = 'en'
def B(en, fr, tag='span'):
    """pick the text for the language being built"""
    return fr if LANG == 'fr' else en

# ---------------------------------------------------------------- shared data
ORG = {
    '@type': 'Organization', '@id': SITE + '/#org', 'name': 'Nastaliq', 'legalName': 'Nastaliq LLP', 'alternateName': ['Nastaliq LLP', 'Nastaliq ERP'], 'url': SITE + '/',
    'disambiguatingDescription': 'Software company that builds and hosts a cloud ERP for businesses in North America.',
    'logo': SITE + '/img/mark.svg', 'email': EMAIL, 'foundingDate': '2026-10-16',
    'identifier': {'@type': 'PropertyValue', 'propertyID': 'SECP LLP Incorporation No.', 'value': REG_NO},
    'description': 'Nastaliq builds and hosts private cloud ERP for growing businesses in North America: inventory, purchasing, sales and accounting in one system, with each client on its own dedicated server, in English and French.',
    'address': {'@type': 'PostalAddress', 'addressLocality': 'Lahore', 'addressCountry': 'PK'},
    'areaServed': ['CA', 'US'], 'knowsLanguage': ['en', 'fr'],
    'contactPoint': {'@type': 'ContactPoint', 'contactType': 'sales', 'email': EMAIL, 'availableLanguage': ['English', 'French']},
}
if SAME_AS: ORG['sameAs'] = SAME_AS
WEBSITE = {'@type': 'WebSite', '@id': SITE + '/#website', 'url': SITE + '/', 'name': 'Nastaliq', 'inLanguage': ['en', 'fr'], 'publisher': {'@id': SITE + '/#org'}}

PRODUCTS = [
    ('suite', 'ok', 'Available', 'Disponible', 'Business suite', "Suite d'affaires",
     'Inventory, purchasing, accounting and sales in one cloud system, set up for your business and hosted by us.',
     "Inventaire, achats, comptabilité et ventes dans un seul système infonuagique, configuré pour votre entreprise et hébergé par nous.",
     [('Inventory: receive, transfer and count stock, with barcode scanning from a phone', "Stocks : réception, transfert et inventaire, avec codes-barres depuis un téléphone"),
      ('Purchasing: purchase orders, receiving and supplier bills in one flow', 'Achats : bons de commande, réception et factures fournisseurs en un seul flux'),
      ('Sales: sales orders, invoices and customer-specific prices', 'Ventes : commandes, factures et prix par client'),
      ('Accounting: books that follow every sale and purchase', 'Comptabilité : des livres alimentés par chaque vente et achat'),
      ('Your own dedicated server, with your name and logo on the login', 'Votre propre serveur dédié, avec votre nom et votre logo à la connexion')]),
    ('janitorial', 'warn', 'Early access', 'Accès anticipé', 'Janitorial operations', "Gestion des services d'entretien",
     'Run a commercial cleaning company from one app, for cleaners, supervisors and clients.',
     "Gérez une entreprise d'entretien commercial depuis une seule application, pour les employés, les superviseurs et les clients.",
     [('Time clock with GPS geofencing', 'Pointage avec géorepérage GPS'), ('Inspections and checklists with photo proof', 'Inspections et listes de vérification avec preuve photo'),
      ('Client portal and messaging', 'Portail client et messagerie'), ('Supplies and job profitability', 'Fournitures et rentabilité par contrat')]),
    ('owner', 'warn', 'Early access', 'Accès anticipé', 'Owner dashboard and alerts', 'Tableau de bord et alertes',
     'A home screen by role, phone-friendly stock screens, and a morning email digest of what needs attention.',
     "Un écran d'accueil selon le rôle, des écrans de stock adaptés au téléphone et un courriel matinal sur ce qui demande votre attention.",
     [('Owner, sales, warehouse and accountant each land on their own tasks', 'Propriétaire, ventes, entrepôt et comptable arrivent chacun sur leurs tâches'),
      ('Morning email: sales, low stock and overdue bills', 'Courriel du matin : ventes, stocks bas et factures en retard'),
      ('Owner metrics, down to each sale', "Indicateurs du propriétaire, jusqu'à chaque vente")]),
    ('bilingual', 'ok', 'Available', 'Disponible', 'English and French', 'Anglais et français',
     'One switch on every screen, with Canadian French terms such as courriel and téléverser.',
     'Un seul bouton sur chaque écran, avec la terminologie du français canadien, comme courriel et téléverser.',
     [('Each user picks their own language', 'Chaque utilisateur choisit sa langue'),
      ('Documents in English or French', 'Documents en français ou en anglais')]),
    ('pos', 'warn', 'In development', 'En développement', 'Point of sale', 'Point de vente',
     'A clean, fast till for restaurants, fast food and bakeries.',
     'Une caisse rapide et épurée pour restaurants, restauration rapide et boulangeries.',
     [('Admin-editable colour themes', "Thèmes de couleurs modifiables par l'administrateur"), ('Built for counter speed', 'Pensé pour la vitesse au comptoir')]),
]

# FAQ shown on the home page AND emitted as FAQPage JSON-LD (text must match what is visible)
FAQ = [
    ('What is Nastaliq?', "Qu'est-ce que Nastaliq?",
     'Nastaliq is a private cloud ERP for growing businesses in North America, typically companies with $1M or more in annual revenue. It puts inventory, purchasing, sales and accounting in one system, on your own dedicated server, in English and French. We set it up for your business and host it.',
     "Nastaliq est un ERP en nuage privé pour les entreprises en croissance d'Amérique du Nord, généralement celles dont les revenus annuels atteignent 1 M$ ou plus. Il réunit stocks, achats, ventes et comptabilité dans un seul système, sur votre propre serveur dédié, en français et en anglais. Nous l'installons pour votre entreprise et l'hébergeons."),
    ('Is our data shared with other clients?', "Nos données sont-elles partagées avec d'autres clients?",
     'No. Every client, whatever its size, runs on its own dedicated server with its own site. Your system and data are not shared with any other company.',
     "Non. Chaque client, peu importe sa taille, fonctionne sur son propre serveur dédié, avec son propre site. Votre système et vos données ne sont partagés avec aucune autre entreprise."),
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
           % (B('Private cloud ERP for growing businesses in North America', "ERP en nuage privé pour les entreprises en croissance d'Amérique du Nord"), up, EMAIL, EMAIL))
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
               B('Private cloud ERP for growing businesses: inventory, purchasing, sales and accounting on your own dedicated server, in English and French.',
                 "ERP en nuage privé pour entreprises en croissance : stocks, achats, ventes et comptabilité sur votre propre serveur dédié, en français et en anglais."),
               B('Lahore, Pakistan, serving North America.', "Lahore, Pakistan, au service de l'Amérique du Nord."), EMAIL, EMAIL,
               col(B('Product', 'Produit'), [(up + 'products.html', B('Products', 'Produits')), (home + '#pricing', B('Pricing', 'Tarifs')), (home + '#faq', 'FAQ')])
               + col(B('Industries', 'Secteurs'), [(up + 'industries/%s.html' % i['slug'], B(*i['name'])) for i in INDUSTRIES]),
               col(B('Company', 'Entreprise'), [(up + 'company.html', B('About', 'À propos')), (up + 'articles.html', 'Articles'), (up + 'contact.html', 'Contact')]),
               col(B('Legal', 'Mentions légales'), [(up + 'privacy.html', B('Privacy Policy', 'Politique de confidentialité')), (up + 'terms.html', B('Terms of Service', "Conditions d'utilisation"))]),
               B('Registration No.', "N° d'immatriculation"), REG_NO, B('All rights reserved.', 'Tous droits réservés.'),
               up, B('Privacy Policy', 'Politique de confidentialité'), up, B('Terms of Service', "Conditions d'utilisation")))

def url_for(path, lang=None):
    lang = lang or LANG
    return SITE + '/' + ('fr/' if lang == 'fr' else '') + ('' if path == 'index.html' else path[:-5] if path.endswith('.html') else path)

def head(path, title, desc, schema, og_type='website', robots='index,follow,max-image-preview:large,max-snippet:-1'):
    up, pre = levels(path)
    url = url_for(path)
    org = dict(ORG)
    if LANG == 'fr':
        org['description'] = "Nastaliq conçoit et héberge des un ERP en nuage privé pour les entreprises en croissance d'Amérique du Nord : stocks, achats, ventes et comptabilité dans un seul système, chaque client ayant son propre serveur dédié, en français et en anglais."
    web = dict(WEBSITE)
    graph = {'@context': 'https://schema.org', '@graph': [org, web] + schema}
    en, fr = url_for(path, 'en'), url_for(path, 'fr')
    oloc, oalt = ('fr_CA', 'en_CA') if LANG == 'fr' else ('en_CA', 'fr_CA')
    return ('<!doctype html>\n<html lang="%s"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
            '<title>%s</title><meta name="description" content="%s"><link rel="canonical" href="%s">'
            '<link rel="alternate" hreflang="en" href="%s"><link rel="alternate" hreflang="fr" href="%s"><link rel="alternate" hreflang="x-default" href="%s">'
            '<meta name="robots" content="%s"><meta name="theme-color" content="#000000">'
            '<link rel="icon" href="%sfavicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="%simg/apple-touch-icon.png">'
            '<meta property="og:site_name" content="Nastaliq"><meta property="og:locale" content="%s"><meta property="og:locale:alternate" content="%s">'
            '<meta property="og:type" content="%s"><meta property="og:title" content="%s"><meta property="og:description" content="%s"><meta property="og:url" content="%s">'
            '<meta property="og:image" content="%s/img/og.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="%s">'
            '<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="%s"><meta name="twitter:description" content="%s"><meta name="twitter:image" content="%s/img/og.png">'
            '%s<link rel="stylesheet" href="%scss/home.css">'
            '<script type="application/ld+json">%s</script></head>'
            % (LANG, x(title), x(desc), url, en, fr, en, robots, pre, pre, oloc, oalt, og_type, x(title), x(desc), url, SITE,
               B('Nastaliq: private cloud ERP for growing businesses', "Nastaliq : ERP en nuage privé pour entreprises en croissance"),
               x(title), x(desc), SITE, FONT, pre, json.dumps(graph, ensure_ascii=False, separators=(',', ':'))))

def page(path, title, desc, schema, body, cur='', og_type='website', **kw):
    up, pre = levels(path)
    return (head(path, title, desc, schema, og_type, **kw) + '<body>' + header(path, cur) + '<main id="main">' + body + '</main>'
            + footer(path) + '<script src="%sjs/home.js" defer></script></body></html>\n' % pre)

def crumbs(items):
    return {'@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': u} for i, (n, u) in enumerate(items)]}

def faq_ld(pairs):
    return {'@type': 'FAQPage', 'inLanguage': LANG, 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in pairs]}

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
    base = posixpath.dirname(lp() + path)
    s = re.sub(r'\b(href|src)="([^"]*)"', lambda m: '%s="%s"' % (m.group(1), clean(m.group(2), base)), s)
    p = os.path.join(PUB, lp() + path); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8').write(s)

def hero(h1en, h1fr, lede_en, lede_fr):
    return ('<section class="pagehead"><div class="in"><h1 style="max-width:20ch">%s</h1><p class="lede">%s</p></div></section>'
            % (B(h1en, h1fr), B(lede_en, lede_fr)))

def badge(cls, en, fr):
    return '<span class="tag%s">%s</span>' % (' w' if cls == 'warn' else '', B(en, fr))

def pg(path, name_en, name_fr):
    return (name_fr if LANG == 'fr' else name_en, url_for(path))

# ---------------------------------------------------------------- shared steps
FLOW = [('Tell us what you run', 'Dites-nous ce que vous exploitez', 'What you sell, how many locations you have and what you use today.', "Ce que vous vendez, combien d'emplacements vous avez et ce que vous utilisez aujourd'hui."),
        ('See your demo', 'Voyez votre démo', 'We reply by email with a demo set up for your industry, plus a plan and a price.', 'Nous répondons par courriel avec une démo préparée pour votre secteur, un plan et un prix.'),
        ('We set it up', "Nous l'installons", 'We configure your preset and bring in your customers, products and records.', 'Nous configurons votre préréglage et importons vos clients, produits et dossiers.'),
        ('Go live', 'Mise en service', 'Most businesses go live in about six weeks. Hosting, updates and support stay with us.', 'La plupart des entreprises démarrent en environ six semaines. Hébergement, mises à jour et soutien restent chez nous.')]

def flow_section(en='What happens next', fr='La suite des choses'):
    li = ''.join('<li><h3>%s</h3><p>%s</p></li>' % (B(a, b), B(c, d)) for a, b, c, d in FLOW)
    return '<section class="band dark"><div class="in"><div class="sh"><h2>%s</h2></div><ol class="flow">%s</ol></div></section>' % (B(en, fr), li)

# ---------------------------------------------------------------- industries
AV, EA = ('ok', 'Available', 'Offert'), ('warn', 'Early access', 'Accès anticipé')
INDUSTRIES = [
 dict(slug='distribution', status=AV, name=('Distribution', 'Distribution'),
      title=('ERP for distribution and wholesale companies | Nastaliq', 'ERP pour la distribution et le commerce de gros | Nastaliq'),
      h1=('ERP for distribution and wholesale companies', 'ERP pour les entreprises de distribution et de gros'),
      lede=('Purchasing, receiving, stock and customer pricing in one private cloud system, set up from a distribution preset and hosted by us.',
            "Achats, réception, stocks et prix par client dans un seul système infonuagique privé, configuré à partir d'un préréglage pour la distribution et hébergé par nous."),
      who=('Built for distributors and trading companies with one or more warehouses that have outgrown spreadsheets and stand-alone accounting software.',
           "Conçu pour les distributeurs et les sociétés de négoce ayant un ou plusieurs entrepôts, pour qui les tableurs et un logiciel comptable isolé ne suffisent plus."),
      feats=[(AV, 'Purchase order to supplier bill', 'Du bon de commande à la facture', 'Raise a purchase order, receive against it and match the supplier bill, in one flow with no re-typing.', 'Créez un bon de commande, recevez la marchandise et rapprochez la facture du fournisseur, en un seul flux et sans ressaisie.'),
             (AV, 'Warehouse work on a phone', "Le travail d'entrepôt au téléphone", 'Receive, transfer and count stock from the floor, scanning barcodes with the phone camera.', 'Réception, transfert et inventaire depuis le plancher, en numérisant les codes-barres avec la caméra du téléphone.'),
             (AV, 'Customer-specific prices', 'Prix par client', 'Each customer gets the agreed price on every sales order, whoever enters it.', 'Chaque client obtient le prix convenu sur chaque commande, peu importe qui la saisit.'),
             (AV, 'Stock you can trust', 'Des stocks fiables', 'See what is on hand and what has fallen below its reorder level, without walking the shelves.', 'Voyez ce qui est en main et ce qui est passé sous le seuil de réapprovisionnement, sans parcourir les tablettes.'),
             (AV, 'Books that keep up', 'Des livres à jour', 'Every receipt, sale and bill posts to the accounts as it happens, with unpaid and overdue bills in view.', "Chaque réception, vente et facture s'inscrit dans les comptes au fur et à mesure, avec les factures impayées et en retard bien visibles."),
             (EA, 'Morning email', 'Courriel du matin', "Yesterday's sales, low stock and overdue bills in the owner's inbox before the day starts.", 'Les ventes de la veille, les stocks bas et les factures en retard dans la boîte du propriétaire avant le début de la journée.')],
      faq=[('Does it handle more than one warehouse?', "Gère-t-il plus d'un entrepôt?", 'Yes. Stock is kept by location, and transfers between locations are recorded from a phone.', 'Oui. Les stocks sont tenus par emplacement, et les transferts entre emplacements sont consignés depuis un téléphone.'),
           ('Can our existing items, customers and suppliers be imported?', 'Peut-on importer nos articles, clients et fournisseurs existants?', 'Yes. We bring your existing records in during setup. Tell us what you use today and we will say what is possible.', "Oui. Nous importons vos dossiers existants pendant l'installation. Dites-nous ce que vous utilisez aujourd'hui et nous vous dirons ce qui est possible."),
           ('How long until we are live?', 'Combien de temps avant la mise en service?', 'Most businesses go live in about six weeks, with setup and hosting handled by us.', "La plupart des entreprises démarrent en environ six semaines, installation et hébergement assurés par nous.")]),
 dict(slug='retail', status=AV, name=('Retail', 'Détail'),
      title=('ERP for retail businesses | Nastaliq', 'ERP pour les commerces de détail | Nastaliq'),
      h1=('ERP for retail businesses', 'ERP pour les commerces de détail'),
      lede=('Stock, purchasing, sales records and accounting in one private cloud system, set up from a retail preset and hosted by us.',
            "Stocks, achats, ventes et comptabilité dans un seul système infonuagique privé, configuré à partir d'un préréglage pour le détail et hébergé par nous."),
      who=('Built for retailers with real stock to manage, across one store or several, who want the back office in one place.',
           'Conçu pour les détaillants qui ont de vrais stocks à gérer, dans un ou plusieurs magasins, et qui veulent tout le travail de bureau au même endroit.'),
      feats=[(AV, 'Sales tied to live stock', 'Des ventes reliées aux stocks', 'Each sales order reduces stock the moment it is entered, so the shelf and the system agree.', 'Chaque commande réduit les stocks dès sa saisie : la tablette et le système concordent.'),
             (AV, 'Barcode receiving and counts', 'Réception et inventaire par code-barres', 'Receive deliveries and run cycle counts from a phone instead of a clipboard.', 'Recevez les livraisons et faites des inventaires tournants avec un téléphone plutôt qu’une planchette.'),
             (AV, 'Purchasing in one flow', 'Les achats en un seul flux', 'Purchase orders, receiving and supplier bills connected from start to finish.', 'Bons de commande, réception et factures fournisseurs reliés du début à la fin.'),
             (AV, 'Accounting that follows every sale', 'Une comptabilité alimentée par chaque vente', 'Sales and purchases post to the books by themselves, ready for your accountant.', "Les ventes et les achats s'inscrivent d'eux-mêmes dans les livres, prêts pour votre comptable."),
             (AV, 'English and French', 'Français et anglais', 'Each user picks a language, and documents print in either one.', "Chaque utilisateur choisit sa langue, et les documents s'impriment dans l'une ou l'autre."),
             (EA, 'Owner metrics', 'Indicateurs du propriétaire', 'A home screen with the numbers that matter, down to each sale.', "Un écran d'accueil avec les chiffres qui comptent, jusqu'à chaque vente.")],
      faq=[('Is this a point-of-sale system?', 'Est-ce un système de point de vente?', 'No. Nastaliq is the system behind the counter: stock, purchasing, sales records and accounting. A dedicated point of sale is in development.', "Non. Nastaliq est le système derrière le comptoir : stocks, achats, ventes et comptabilité. Un point de vente dédié est en développement."),
           ('Can it cover more than one store?', "Peut-il couvrir plus d'un magasin?", 'Yes. Stock is kept by location, and transfers between locations are recorded.', 'Oui. Les stocks sont tenus par emplacement, et les transferts entre emplacements sont consignés.'),
           ('Can our existing products and customers be imported?', 'Peut-on importer nos produits et clients existants?', 'Yes. We bring your existing records in during setup.', "Oui. Nous importons vos dossiers existants pendant l'installation.")]),
 dict(slug='janitorial', status=EA, name=('Janitorial', 'Entretien'),
      title=('Operations software for commercial cleaning | Nastaliq', "Logiciel de gestion pour l'entretien commercial | Nastaliq"),
      h1=('Operations software for commercial cleaning companies', "Logiciel de gestion pour les entreprises d'entretien commercial"),
      lede=('Crews, inspections, clients and supplies in one app, for cleaners, supervisors and the companies you serve. Now in early access.',
            'Équipes, inspections, clients et fournitures dans une seule application, pour les employés, les superviseurs et vos clients. Maintenant en accès anticipé.'),
      who=('Built for commercial cleaning companies that schedule crews across client sites and need proof that the work was done.',
           "Conçu pour les entreprises d'entretien commercial qui répartissent des équipes chez leurs clients et doivent prouver que le travail a été fait."),
      feats=[(EA, 'Time clock and scheduling', 'Pointage et horaires', 'Schedule crews by site and record hours with a time clock that uses GPS geofencing.', 'Planifiez les équipes par site et consignez les heures avec un pointage par géorepérage GPS.'),
             (EA, 'Inspections and checklists', 'Inspections et listes de vérification', 'Checklists per site, with photo proof of the finished work.', 'Des listes par site, avec preuve photo du travail terminé.'),
             (EA, 'Client portal and messaging', 'Portail client et messagerie', 'Give each client one place to see their site and reach you.', 'Offrez à chaque client un seul endroit pour suivre son site et vous joindre.'),
             (EA, 'Supplies and job profitability', 'Fournitures et rentabilité par contrat', 'Track what each job uses and what it earns.', "Suivez ce que chaque contrat consomme et ce qu'il rapporte.")],
      faq=[('Is it available today?', 'Est-il offert aujourd’hui?', 'It is in early access. Write to us and we will tell you plainly what is ready and what is still being built.', "Il est en accès anticipé. Écrivez-nous et nous vous dirons franchement ce qui est prêt et ce qui est encore en développement."),
           ('Who uses it?', "Qui l'utilise?", 'Cleaners clock in and complete checklists, supervisors schedule and inspect, and clients follow their site through the portal.', 'Les employés pointent et remplissent les listes, les superviseurs planifient et inspectent, et les clients suivent leur site par le portail.')]),
]

def industries():
    for I in INDUSTRIES:
        path = 'industries/%s.html' % I['slug']
        cards = ''.join('<div class="card">%s<h2>%s</h2><p>%s</p></div>' % (badge(st[0], st[1], st[2]), B(a, b), B(c, d)) for st, a, b, c, d in I['feats'])
        faqs = [(B(q, qf), B(a, af)) for q, qf, a, af in I['faq']]
        faq = ''.join('<details><summary>%s</summary><p>%s</p></details>' % (html.escape(q), html.escape(a)) for q, a in faqs)
        body = ('<section class="pagehead"><div class="in">%s<h1 style="max-width:20ch">%s</h1><p class="lede">%s</p><p><a class="btn" href="../contact.html">%s</a></p></div></section>'
                '<section class="band"><div class="in"><div class="sh"><h2>%s</h2><p class="lede">%s</p></div><div class="g3 feat">%s</div></div></section>'
                % (badge(*I['status']), B(*I['h1']), B(*I['lede']), B('Book a free demo', 'Réserver une démo gratuite'),
                   B("What's included", 'Ce qui est inclus'), B(*I['who']), cards)
                + flow_section('How setup works', "Comment se déroule l'installation")
                + '<section class="band"><div class="in"><div class="sh"><h2>%s</h2></div><div class="faq">%s</div></div></section>' % (B('Common questions', 'Questions fréquentes'), faq)
                + '<section class="band" style="padding-top:0"><div class="in"><div class="cta2"><h2>%s</h2><p>%s</p><a class="btn" href="../contact.html">%s</a></div></div></section>'
                % (B('See it with your industry loaded', 'Voyez-le avec votre secteur'), B('Tell us what you run. We reply by email with a demo, a plan and a price.', 'Dites-nous ce que vous exploitez. Nous répondons par courriel avec une démo, un plan et un prix.'), B('Get in touch', 'Nous joindre')))
        schema = [{'@type': 'WebPage', 'name': B(*I['h1']), 'url': url_for(path), 'inLanguage': LANG, 'isPartOf': {'@id': SITE + '/#website'}, 'about': {'@id': SITE + '/#org'}},
                  {'@type': 'Service', 'name': B(*I['h1']), 'serviceType': B('Cloud ERP implementation and hosting', "Implantation et hébergement d'ERP infonuagique"), 'description': B(*I['lede']),
                   'provider': {'@id': SITE + '/#org'}, 'areaServed': ['CA', 'US'], 'url': url_for(path)},
                  faq_ld(faqs), crumbs([pg('index.html', 'Home', 'Accueil'), (B(*I['name']), url_for(path))])]
        write(path, page(path, B(*I['title']), B(*I['lede']), schema, body))

def notfound():
    body = (hero('Page not found.', 'Page introuvable.', 'The page may have moved. These will get you back on track.', 'La page a peut-être été déplacée. Ces liens vous remettront sur la bonne voie.')
            + '<section class="band"><div class="in"><p class="ctas"><a class="btn dk" href="index.html">%s</a><a class="btn ol" href="products.html">%s</a><a class="btn ol" href="articles.html">%s</a><a class="btn ol" href="contact.html">Contact</a></p></div></section>'
            % (B('Home', 'Accueil'), B('Products', 'Produits'), 'Articles'))
    write('404.html', page('404.html', B('Page not found | Nastaliq', 'Page introuvable | Nastaliq'), B('This page could not be found on nastaliq.co.', 'Cette page est introuvable sur nastaliq.co.'), [], body, robots='noindex,follow'))

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
             ('Hosting model', "Modèle d'hébergement", 'Private cloud only: each client on its own dedicated server. We do not sell on-premise installs.', "Nuage privé seulement : chaque client sur son propre serveur dédié. Nous ne vendons pas d'installations sur place.")]
    dl = ''.join('<div><dt>%s</dt><dd>%s</dd></div>' % (B(a, b), B(c, d)) for a, b, c, d in facts)
    pr = [('Say what is real', 'Dire ce qui est réel', 'Every feature is labelled with its actual status, from Available to Planned.', 'Chaque fonction est étiquetée selon son état réel, de Disponible à Prévu.'),
          ('Accounting first', "La comptabilité d'abord", 'Accounting expertise is part of the team, so the books are set up properly from day one.', "L'expertise comptable fait partie de l'équipe, ce qui garantit des livres bien configurés dès le premier jour."),
          ('Your language', 'Votre langue', 'English and French throughout, because Canadian businesses work in both.', 'Anglais et français partout, parce que les entreprises canadiennes travaillent dans les deux langues.')]
    cards = ''.join('<div><h3>%s</h3><p>%s</p></div>' % (B(a, b), B(c, d)) for a, b, c, d in pr)
    body = (hero('A small team that sets up your system and keeps it running.', 'Une petite équipe qui installe votre système et le maintient en marche.',
                 'Nastaliq builds and hosts a private cloud ERP for growing businesses in North America.',
                 "Nastaliq conçoit et héberge un ERP en nuage privé pour les entreprises en croissance d'Amérique du Nord.")
            + '<section class="band paper"><div class="in"><h2>%s</h2><div class="prose" style="margin-top:22px"><p>%s</p><p>%s</p></div></div></section>'
            % (B('What we do', 'Ce que nous faisons'),
               B('Nastaliq sets up and hosts a private cloud ERP for growing businesses: inventory, purchasing, sales and accounting in one system. Each client runs on its own dedicated server, with its own name and logo, and its data is never shared with another company.',
                 "Nastaliq installe et héberge un ERP en nuage privé pour les entreprises en croissance : stocks, achats, ventes et comptabilité dans un seul système. Chaque client fonctionne sur son propre serveur dédié, à son nom et avec son logo, et ses données ne sont jamais partagées avec une autre entreprise."),
               B('We start from a preset for your industry, bring in your existing records and stay responsible for hosting, updates and support after go-live. Pricing is a flat monthly subscription with unlimited users plus a one-time setup fee.',
                 "Nous partons d'un préréglage pour votre secteur, importons vos dossiers existants et demeurons responsables de l'hébergement, des mises à jour et du soutien après la mise en service. Le tarif est un abonnement mensuel fixe avec utilisateurs illimités, plus des frais d'installation uniques."))
            + '<section class="band"><div class="in"><h2>%s</h2><dl class="facts">%s</dl></div></section>' % (B('Who we are', 'Qui nous sommes'), dl)
            + '<section class="band paper"><div class="in"><h2>%s</h2><div class="f4">%s</div></div></section>' % (B('How we work with clients', 'Notre façon de travailler avec nos clients'), cards)
            + flow_section('From first email to go-live', 'Du premier courriel à la mise en service'))
    schema = [{'@type': 'AboutPage', 'name': B('About Nastaliq', 'À propos de Nastaliq'), 'url': url_for('company.html'), 'inLanguage': LANG, 'about': {'@id': SITE + '/#org'}, 'isPartOf': {'@id': SITE + '/#website'}},
              crumbs([pg('index.html', 'Home', 'Accueil'), pg('company.html', 'Company', 'Entreprise')])]
    write('company.html', page('company.html', B('About Nastaliq LLP | Cloud business software team', 'À propos de Nastaliq LLP | Équipe de logiciels infonuagiques'),
          B('Nastaliq LLP builds and hosts a private cloud ERP for growing businesses in North America. Registered with SECP, based in Lahore, Pakistan.',
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
               EMAIL, B('Copied', 'Copié'), B('Copy', 'Copier'), EMAIL, subj, B('Email us', 'Écrivez-nous'), li) + flow_section())
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
        pub = '2026-11-11' if a['slug'] in NEW_ARTS else TODAY
        date_h = B('November 11, 2026', '11 novembre 2026') if a['slug'] in NEW_ARTS else B('October 26, 2026', '26 octobre 2026')
        body = ('<article class="in art"><div class="crumb"><a href="../index.html">%s</a> / <a href="../articles.html">Articles</a></div>'
                '<h1>%s</h1><p class="meta">%s &middot; %s <time datetime="%s">%s</time> &middot; %s</p>'
                '<div class="short"><b>%s</b><p>%s</p></div>'
                '<div class="prose">%s</div>'
                '<section class="prose faq-s"><h2>%s</h2>%s</section>'
                '<div class="cta"><h3>%s</h3><p>%s</p>'
                '<a class="btn" href="../contact.html">%s</a> <a class="btn" href="../products.html">%s</a></div>'
                '<div class="rel"><h2>%s</h2><div class="ac">%s</div></div></article>'
                % (B('Home', 'Accueil'), html.escape(art_t(a, 'title')), art_t(a, 'tag'), B('Published', 'Publié le'), pub, date_h, (B('By ', 'Par ') + html.escape(AUTHOR['name']) + ', ' + B(*AUTHOR['role'])) if AUTHOR else B('By the Nastaliq team', "Par l'équipe Nastaliq"),
                   B('The short answer', 'La réponse courte'), html.escape(art_t(a, 'short')), art_t(a, 'body'),
                   B('Common questions', 'Questions fréquentes'), faq,
                   B('See Nastaliq with your business loaded', 'Voyez Nastaliq avec votre entreprise'),
                   B('Tell us what you sell and how you run today. We reply by email with a plan and a price.', "Dites-nous ce que vous vendez et comment vous fonctionnez aujourd'hui. Nous répondons par courriel avec un plan et un prix."),
                   B('Book a free demo', 'Réserver une démo gratuite'), B('See products', 'Voir les produits'),
                   B('More guides', "D'autres guides"), art_cards(rel, '')))
        path = 'articles/%s.html' % a['slug']
        title = art_t(a, 'title')
        suffix = ' | Nastaliq'
        schema = [{'@type': 'Article', 'headline': title, 'description': art_t(a, 'desc'), 'datePublished': pub, 'dateModified': UPDATED, 'inLanguage': LANG,
                   'author': ({'@type': 'Person', 'name': AUTHOR['name'], 'jobTitle': B(*AUTHOR['role']), 'url': AUTHOR.get('url') or url_for('company.html'), 'worksFor': {'@id': SITE + '/#org'}} if AUTHOR else {'@id': SITE + '/#org'}),
                   'publisher': {'@id': SITE + '/#org'}, 'mainEntityOfPage': url_for(path),
                   'image': SITE + '/img/og.png', 'isPartOf': {'@id': SITE + '/#website'}},
                  faq_ld(faqs), crumbs([pg('index.html', 'Home', 'Accueil'), pg('articles.html', 'Articles', 'Articles'), (title, url_for(path))])]
        seo = art_t(a, 'seo')
        write(path, page(path, (seo + suffix) if len(seo) <= 49 else seo, art_t(a, 'desc'), schema, body, cur='art', og_type='article'))
    body = ('<section class="pagehead"><div class="in"><h1 style="max-width:18ch">%s</h1>'
            '<p class="lede">%s</p></div></section>'
            '<section class="band paper"><div class="in"><div class="ac">%s</div></div></section>'
            % (B('Guides for business owners', "Des guides pour les propriétaires d'entreprise"),
               B('Plain advice on software, stock and running your operations. No jargon.', 'Des conseils clairs sur les logiciels, les stocks et la gestion de vos opérations. Sans jargon.'),
               art_cards(ARTS, h='h2')))
    schema = [{'@type': 'CollectionPage', 'name': 'Articles', 'url': url_for('articles.html'), 'inLanguage': LANG, 'isPartOf': {'@id': SITE + '/#website'}},
              {'@type': 'ItemList', 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': url_for('articles/%s.html' % a['slug']), 'name': art_t(a, 'title')} for i, a in enumerate(ARTS)]},
              crumbs([pg('index.html', 'Home', 'Accueil'), pg('articles.html', 'Articles', 'Articles')])]
    write('articles.html', page('articles.html', B('ERP guides for business owners | Nastaliq', "Guides ERP pour propriétaires d'entreprise | Nastaliq"),
          B('Guides on choosing an ERP, moving off spreadsheets, keeping stock accurate, bilingual systems in Canada and where to host your operations data.',
            "Guides pour choisir un ERP, quitter les tableurs, garder des stocks exacts, adopter un système bilingue et décider où héberger vos données."),
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
    app = {'@type': 'SoftwareApplication', 'name': 'Nastaliq ERP', 'applicationCategory': 'BusinessApplication', 'operatingSystem': 'Web',
           'description': B('Private cloud ERP for growing businesses: inventory, purchasing, sales and accounting on a dedicated server, in English and French.',
                            'ERP en nuage privé pour entreprises en croissance : stocks, achats, ventes et comptabilité sur un serveur dédié, en français et en anglais.'),
           'url': url_for('index.html'), 'provider': {'@id': SITE + '/#org'}, 'inLanguage': ['en', 'fr'],
           'featureList': B(['Inventory with barcode scanning', 'Purchasing', 'Accounting', 'Sales', 'English and French'],
                            ['Inventaire avec codes-barres', 'Achats', 'Comptabilité', 'Ventes', 'Français et anglais'])}
    schema = [{'@type': 'WebPage', '@id': url_for('index.html') + '#webpage', 'url': url_for('index.html'), 'name': 'Nastaliq', 'inLanguage': LANG,
               'isPartOf': {'@id': SITE + '/#website'}, 'about': {'@id': SITE + '/#org'}}, app, faq_ld([(B(q, qf), B(a, af)) for q, qf, a, af in FAQ])]
    title = B('Nastaliq | Private cloud ERP for inventory and accounting', 'Nastaliq | ERP en nuage privé : stocks, ventes, comptabilité')
    desc = B('Private cloud ERP for growing North American businesses: inventory, purchasing, sales and accounting on your own dedicated server, in English and French.',
             "ERP en nuage privé pour entreprises en croissance : stocks, achats, ventes et comptabilité sur votre propre serveur dédié, bilingue.")
    out = head('index.html', title, desc, schema) + '<body>' + sprite + header('index.html', '', True) + main + footer('index.html') + '<script src="js/home.js" defer></script></body></html>\n'
    out = out.replace('src="js/home.js"', 'src="%sjs/home.js"' % levels('index.html')[1])
    write('index.html', out)

def seo_files():
    pages = [('index.html', '1.0'), ('products.html', '0.8'), ('company.html', '0.6'), ('contact.html', '0.7'), ('articles.html', '0.8')] + [('articles/%s.html' % a['slug'], '0.7') for a in ARTS] + [('industries/%s.html' % i['slug'], '0.8') for i in INDUSTRIES] + [('privacy.html', '0.3'), ('terms.html', '0.3')]
    rows = ''
    for p, pr in pages:
        for lg in ('en', 'fr'):
            alts = ''.join('<xhtml:link rel="alternate" hreflang="%s" href="%s"/>' % (l2, url_for(p, l2)) for l2 in ('en', 'fr')) + '<xhtml:link rel="alternate" hreflang="x-default" href="%s"/>' % url_for(p, 'en')
            rows += '<url><loc>%s</loc><lastmod>%s</lastmod><priority>%s</priority>%s</url>\n' % (url_for(p, lg), UPDATED, pr, alts)
    open(os.path.join(PUB, 'sitemap.xml'), 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + rows + '</urlset>\n')
    bots = ['GPTBot', 'OAI-SearchBot', 'ChatGPT-User', 'ClaudeBot', 'Claude-SearchBot', 'Claude-User', 'PerplexityBot', 'Google-Extended', 'Applebot-Extended']
    open(os.path.join(PUB, 'robots.txt'), 'w').write('User-agent: *\nAllow: /\n\n' + ''.join('User-agent: %s\nAllow: /\n\n' % b for b in bots) + 'Sitemap: %s/sitemap.xml\n' % SITE)
    moved = [('choosing-pos-and-inventory-software-small-business', 'how-to-choose-an-erp'), ('cloud-vs-on-premise-for-small-business', 'private-cloud-erp-vs-saas-vs-on-premise')]
    open(os.path.join(PUB, '_redirects'), 'w').write(''.join('%s/articles/%s%s %s/articles/%s 301\n' % (pre, a, ext, pre, b) for a, b in moved for pre in ('', '/fr') for ext in ('', '.html')))
    for lg in ('en', 'fr'):
        fr = lg == 'fr'
        ind = '\n'.join('- [%s](%s): %s (%s)' % (i['h1'][fr], url_for('industries/%s.html' % i['slug'], lg), i['lede'][fr], i['status'][2 if fr else 1]) for i in INDUSTRIES)
        prod = '\n'.join('- [%s](%s#%s): %s (%s)' % (p[5] if fr else p[4], url_for('products.html', lg), p[0], p[7] if fr else p[6], p[3] if fr else p[2]) for p in PRODUCTS)
        art = '\n'.join('- [%s](%s): %s' % (ARTS_FR[a['slug']]['title'] if fr else a['title'], url_for('articles/%s.html' % a['slug'], lg), ARTS_FR[a['slug']]['desc'] if fr else a['desc']) for a in ARTS)
        faq = '\n'.join('**%s** %s\n' % ((qf, af) if fr else (q, a)) for q, qf, a, af in FAQ)
        if fr:
            txt = ('# Nastaliq\n\n> Nastaliq LLP conçoit et héberge des un ERP en nuage privé pour les entreprises en croissance d\'Amérique du Nord : stocks, achats, ventes et comptabilité dans un seul système, chaque client ayant son propre serveur dédié, en français et en anglais. Infonuagique seulement. Le tarif est un abonnement mensuel fixe avec utilisateurs illimités, plus des frais d\'installation uniques, envoyé par courriel.\n\n'
                   'Nastaliq LLP est constituée auprès de la Securities and Exchange Commission of Pakistan (SECP) et établie à Lahore, au Pakistan. Courriel : %s\n\n## Pages\n- [Accueil](%s)\n- [Produits](%s)\n- [Entreprise](%s)\n- [Contact](%s)\n- [Articles](%s)\n\n## Produits et état\n%s\n\n## Secteurs\n%s\n\n## Guides\n%s\n\n## Questions fréquentes\n%s\n'
                   % (EMAIL, url_for('index.html', lg), url_for('products.html', lg), url_for('company.html', lg), url_for('contact.html', lg), url_for('articles.html', lg), prod, ind, art, faq))
            os.makedirs(os.path.join(PUB, 'fr'), exist_ok=True)
            open(os.path.join(PUB, 'fr', 'llms.txt'), 'w').write(txt)
        else:
            txt = ('# Nastaliq\n\n> Nastaliq LLP builds and hosts private cloud ERP for growing businesses in North America: inventory, purchasing, sales and accounting in one system, with each client on its own dedicated server, in English and French. Cloud only. Pricing is a flat monthly subscription with unlimited users plus a one-time setup fee, sent by email.\n\n'
                   'Nastaliq LLP is incorporated with the Securities and Exchange Commission of Pakistan (SECP) and based in Lahore, Pakistan. Contact: %s\n\nFrench version: %s/fr/llms.txt\n\n## Pages\n- [Home](%s)\n- [Products](%s)\n- [Company](%s)\n- [Contact](%s)\n- [Articles](%s)\n\n## Products and status\n%s\n\n## Industries\n%s\n\n## Guides\n%s\n\n## Frequently asked questions\n%s\n'
                   % (EMAIL, SITE, url_for('index.html', lg), url_for('products.html', lg), url_for('company.html', lg), url_for('contact.html', lg), url_for('articles.html', lg), prod, ind, art, faq))
            open(os.path.join(PUB, 'llms.txt'), 'w').write(txt)

if __name__ == '__main__':
    for LANG in ('en', 'fr'):
        products(); company(); contact(); articles(); industries(); legal(); notfound(); home()
    seo_files()
    print('built')
