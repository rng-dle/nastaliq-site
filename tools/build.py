#!/usr/bin/env python3
"""Generates the four static pages in public/. Run: python3 tools/build.py"""
import html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB = os.path.join(ROOT, 'public')

MARK = ('<path fill="#F3A21C" d="M-1.65 -1.14L0.08 -2.14L0.08 -0.05L1.65 0.86L1.65 -1.95L-1.65 -3.86ZM1.65 3.86L1.65 2.14L0.87 2.59L0.00 2.09L-0.71 2.50Z"/>'
        '<path fill="#D9800B" d="M1.03 -2.50L1.81 -2.05L1.81 -1.05L2.52 -0.64L2.52 -3.36ZM-0.08 -1.86L-2.52 -0.45L-2.52 3.36L-0.16 2.00L-1.89 1.00L-0.08 -0.05Z"/>'
        '<path fill="#FFC23A" d="M1.81 -0.86L1.81 1.14L0.00 0.09L-1.57 1.00L0.87 2.41L2.56 1.43L4.17 0.50ZM-2.56 -1.43L-4.17 -0.50L-2.68 0.36L-2.68 -0.55L-1.81 -1.05L-1.81 -1.86Z"/>')
WORD = json.load(open(os.path.join(ROOT, 'tools', 'wordmark.json')))['d']

def x(s):
    return html.escape(s, quote=True)

def T(en, fr):
    """text with a French twin, as attributes + English content"""
    return 'data-fr="%s"' % x(fr), en

def E(tag, en, fr, cls='', extra=''):
    c = ' class="%s"' % cls if cls else ''
    return '<%s%s %s%s>%s</%s>' % (tag, c, 'data-fr="%s"' % x(fr), (' ' + extra) if extra else '', en, tag)

PRODUCTS = [
    ('suite', 'ok', 'Available', 'Disponible', 'Business suite', 'Suite d\'affaires',
     'Inventory, purchasing, accounting and sales in one cloud system, set up for your business and hosted by us.',
     'Inventaire, achats, comptabilité et ventes dans un seul système infonuagique, configuré pour votre entreprise et hébergé par nous.',
     'Inventory, purchasing, accounting and sales in one system.', 'Inventaire, achats, comptabilité et ventes dans un seul système.', []),
    ('pos', 'warn', 'In development', 'En développement', 'Point of sale', 'Point de vente',
     'A clean, fast till for restaurants, fast food and bakeries.',
     'Une caisse rapide et épurée pour restaurants, restauration rapide et boulangeries.',
     'A fast counter till for restaurants, fast food and bakeries.', 'Une caisse rapide pour restaurants, restauration rapide et boulangeries.',
     [('Admin-editable colour themes', 'Thèmes de couleurs modifiables par l\'administrateur'), ('Built for counter speed', 'Pensé pour la vitesse au comptoir')]),
    ('janitorial', 'warn', 'Early access', 'Accès anticipé', 'Janitorial operations', 'Gestion des services d\'entretien',
     'Run a commercial cleaning company from one app, for cleaners, supervisors and clients.',
     'Gérez une entreprise d\'entretien commercial depuis une seule application, pour les employés, les superviseurs et les clients.',
     'Run a commercial cleaning company from one app.', 'Gérez une entreprise d\'entretien commercial depuis une seule application.',
     [('Time clock with GPS geofencing', 'Pointage avec géorepérage GPS'), ('Inspections and checklists with photo proof', 'Inspections et listes de vérification avec preuve photo'),
      ('Client portal and messaging', 'Portail client et messagerie'), ('Supplies and job profitability', 'Fournitures et rentabilité par contrat')]),
    ('owner', 'warn', 'Early access', 'Accès anticipé', 'Owner dashboard and alerts', 'Tableau de bord et alertes',
     'A home screen by role, phone-friendly stock screens, and a morning email digest of what needs attention.',
     'Un écran d\'accueil selon le rôle, des écrans de stock adaptés au téléphone et un courriel matinal sur ce qui demande votre attention.',
     'A home screen by role and a morning email digest.', 'Un écran d\'accueil selon le rôle et un courriel matinal.', []),
    ('bilingual', 'ok', 'Available', 'Disponible', 'English and French', 'Anglais et français',
     'One switch on every screen, with Canadian French terms such as courriel and téléverser.',
     'Un seul bouton sur chaque écran, avec la terminologie du français canadien, comme courriel et téléverser.',
     'One switch on every screen.', 'Un seul bouton sur chaque écran.', []),
    ('claude', 'warn', 'Pilot', 'Projet pilote', 'Claude-powered assistance', 'Assistance propulsée par Claude',
     'Plain-language questions about your data and in-screen guidance. Discrepancy auditing is planned.',
     'Questions en langage courant sur vos données et aide dans l\'écran. L\'audit des écarts est prévu.',
     'Questions and help on your own data.', 'Des réponses et de l\'aide sur vos propres données.', []),
]

PAGES = {
    'index': ('Nastaliq', 'Nastaliq', 'Cloud business software for North American small and mid-sized businesses. Sales, stock, purchasing and accounting in one system, in English and French.'),
    'products': ('Nastaliq Products', 'Produits Nastaliq', 'What Nastaliq builds and where each product stands.'),
    'company': ('Nastaliq Company', 'Entreprise Nastaliq', 'Nastaliq LLP builds and hosts cloud business software for small and mid-sized businesses in North America.'),
    'contact': ('Nastaliq Contact', 'Contact Nastaliq', 'Tell Nastaliq about your business and get a plan and a price.'),
}

def head(key):
    ten, tfr, desc = PAGES[key]
    return ('<!doctype html><html lang="en" data-title-fr="%s"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
            '<meta name="theme-color" content="#000000"><meta name="color-scheme" content="dark">'
            '<title>%s</title><meta name="description" content="%s">'
            '<meta property="og:title" content="%s"><meta property="og:description" content="%s"><meta property="og:type" content="website">'
            '<link rel="icon" href="favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="css/site.css">'
            '<script>document.documentElement.className+=" js"</script></head>' % (x(tfr), x(ten), x(desc), x(ten), x(desc)))

def header(cur):
    items = ''.join(
        '<a href="products.html#%s"><b %s>%s</b><span %s>%s</span></a>' % (p[0], 'data-fr="%s"' % x(p[5]), p[4], 'data-fr="%s"' % x(p[9]), p[8])
        for p in PRODUCTS)
    def link(href, en, fr, k):
        cur_attr = ' aria-current="page"' if cur == k else ''
        return '<a href="%s"%s data-fr="%s">%s</a>' % (href, cur_attr, x(fr), en)
    return (
        '<a class="skip" href="#main" data-fr="Aller au contenu">Skip to content</a>'
        '<header class="gnav" id="gnav"><div class="gnav-in">'
        '<a class="brand" href="index.html" aria-label="Nastaliq, home" data-aria-fr="Nastaliq, accueil">'
        '<svg class="m" role="img" aria-hidden="true" viewBox="-4.27 -3.96 8.54 7.92">' + MARK + '</svg>'
        '<svg class="w" role="img" aria-hidden="true" viewBox="33 -782 3785 1024"><path fill="#F5F0E8" d="' + WORD + '"/></svg></a>'
        '<nav class="nav-links" id="nav-links" aria-label="Main" data-aria-fr="Principale">'
        + link('index.html', 'Home', 'Accueil', 'index') +
        '<button class="nl" id="nl-products" type="button" aria-expanded="false" aria-controls="mega"><span data-fr="Produits">Products</span><i class="chev"></i></button>'
        + '<div class="mega" id="mega"><div class="mega-in"><span class="mega-lab" data-fr="Ce que nous construisons">What we build</span>' + items + '</div></div>'
        + link('company.html', 'Company', 'Entreprise', 'company')
        + link('contact.html', 'Contact', 'Contact', 'contact') +
        '<span class="lang" role="group" aria-label="Language" data-aria-fr="Langue"><button type="button" data-l="en" aria-pressed="true">EN</button><button type="button" data-l="fr" aria-pressed="false">FR</button></span>'
        '</nav>'
        '<button class="menu-btn" type="button" aria-label="Menu" data-aria-fr="Menu" aria-expanded="false" aria-controls="nav-links"><i></i><i></i></button>'
        '</div>'
        '</header><div class="scrim"></div>')

def footer():
    plinks = ''.join('<a href="products.html#%s" data-fr="%s">%s</a>' % (p[0], x(p[5]), p[4]) for p in PRODUCTS[:4])
    return (
        '<footer class="foot"><div class="foot-in"><div class="foot-cols">'
        '<div><h4 data-fr="Produits">Products</h4>' + plinks + '</div>'
        '<div><h4 data-fr="Entreprise">Company</h4><a href="company.html" data-fr="À propos">About</a><a href="contact.html" data-fr="Nous joindre">Get in touch</a></div>'
        '<div><h4 data-fr="Courriel">Email</h4><a href="contact.html">hello@nastaliq.co</a></div>'
        '</div>'
        '<p class="foot-note" data-fr="Chaque fonction affiche son état réel. Disponible signifie que des clients peuvent l\'utiliser aujourd\'hui. Accès anticipé, En développement, Projet pilote et Prévu sont indiqués tels quels. Claude est un produit d\'Anthropic. Les marques citées appartiennent à leurs propriétaires.">'
        'Every feature carries its real status. Available means clients can use it today. Early access, In development, Pilot and Planned are labelled as such. Claude is a product of Anthropic. Trademarks belong to their owners.</p>'
        '<div class="foot-base"><span>&copy; <span id="yr">2026</span> Nastaliq LLP</span>'
        '<span data-fr="Lahore, Pakistan · au service de l\'Amérique du Nord">Lahore, Pakistan · serving North America</span></div>'
        '</div></footer>'
        '<script src="js/site.js"></script>')

def status(cls, en, fr):
    return '<span class="badge b-%s" data-fr="%s">%s</span>' % (cls, x(fr), en)

def tile(pid, cls, sen, sfr, ten, tfr, den, dfr, ul=(), cta=('Explore', 'Découvrir'), delay=''):
    li = ''
    if ul:
        li = '<ul>' + ''.join('<li data-fr="%s">%s</li>' % (x(f), e) for e, f in ul) + '</ul>'
    return ('<article class="tile rv%s">%s<h3 class="h3" data-fr="%s">%s</h3><p data-fr="%s">%s</p>%s'
            '<a class="more" href="products.html#%s" data-fr="%s">%s</a></article>'
            % (delay, status(cls, sen, sfr), x(tfr), ten, x(dfr), den, li, pid, x(cta[1]), cta[0]))

def band(inner, cls='', wide=False):
    return '<section class="band %s"><div class="%s">%s</div></section>' % (cls, 'wide' if wide else 'inner', inner)

# ------------------------------------------------------------------ home
def home():
    hero = ('<section class="band hero center"><div class="inner">'
            + E('span', 'Cloud business software', 'Logiciel d\'affaires infonuagique', 'eyebrow')
            + E('h1', 'One system for the counter and the back office.', 'Un seul système pour le comptoir et l\'arrière-boutique.', 'display')
            + E('p', 'Point of sale, inventory, purchasing, accounting and sales in one cloud system, with an English and French switch on every screen. Built for North American small and mid-sized businesses.',
                'Point de vente, inventaire, achats, comptabilité et ventes dans un seul système infonuagique, avec un bouton anglais/français sur chaque écran. Conçu pour les petites et moyennes entreprises nord-américaines.', 'lede')
            + '<div class="cta">' + E('a', 'Get in touch', 'Nous joindre', 'btn', 'href="contact.html"') + E('a', 'See the products', 'Voir les produits', 'btn alt', 'href="products.html"') + '</div>'
            '</div></section>')

    what = band(
        '<div class="rv">' + E('span', 'What is Nastaliq?', 'Qu\'est-ce que Nastaliq?', 'eyebrow')
        + E('h2', 'Everything you sell, stock, buy and book, working together.', 'Tout ce que vous vendez, stockez, achetez et comptabilisez, qui fonctionne ensemble.', 'h2')
        + E('p', 'Nastaliq is cloud business software for small and mid-sized businesses. A sale at the counter updates your stock and your books without anyone re-typing it, so the numbers are current when you look.',
            'Nastaliq est un logiciel d\'affaires infonuagique pour les petites et moyennes entreprises. Une vente au comptoir met à jour vos stocks et votre comptabilité sans que personne ne ressaisisse quoi que ce soit, donc vos chiffres sont à jour quand vous les consultez.', 'lede') + '</div>'
        '<div class="vals">'
        + '<div class="val rv">' + E('b', 'Run it from one place', 'Tout gérer au même endroit') + E('p', 'Sell, stock, buy and book in the same system.', 'Vendez, stockez, achetez et comptabilisez dans le même système.') + '</div>'
        + '<div class="val rv d1">' + E('b', 'Work from a phone', 'Travailler depuis un téléphone') + E('p', 'Receive, transfer and count stock on the warehouse floor, with barcode scanning.', 'Recevez, transférez et comptez les stocks à l\'entrepôt, avec lecture de codes à barres.') + '</div>'
        + '<div class="val rv d2">' + E('b', 'Switch language in a tap', 'Changer de langue d\'un geste') + E('p', 'English and French on every screen, with Canadian French terms.', 'Anglais et français sur chaque écran, avec la terminologie du français canadien.') + '</div>'
        + '<div class="val rv d3">' + E('b', 'Go live with confidence', 'Démarrer en toute confiance') + E('p', 'We set it up for your business and host it. Typically about six weeks from kickoff to your first live day.', 'Nous le configurons pour votre entreprise et l\'hébergeons. Habituellement environ six semaines entre le lancement et le premier jour en production.') + '</div>'
        '</div>', 'alt')

    cube = (
        '<section class="cube-band" id="cube"><div class="cube-head">'
        + E('span', 'Nastaliq', 'Nastaliq', 'eyebrow rv')
        + E('h2', 'Everything you run, in one piece.', 'Tout ce que vous gérez, d\'un seul bloc.', 'h2 rv')
        + E('p', 'Sales, stock, purchasing and books share one system. Pick up the mark and turn it any way you like.', 'Les ventes, les stocks, les achats et la comptabilité partagent un seul système. Prenez la marque et tournez-la comme vous voulez.', 'lede rv')
        + '</div>'
        '<div id="cube-stage" class="rv" role="group" aria-label="Interactive 3D Nastaliq mark" data-aria-fr="Marque Nastaliq interactive en 3D">'
        '<canvas id="cube-canvas" tabindex="0" aria-label="The Nastaliq mark in 3D. Drag or use the arrow keys to turn it, plus and minus to zoom, R to reset." data-aria-fr="La marque Nastaliq en 3D. Glissez ou utilisez les flèches pour la tourner, plus et moins pour zoomer, R pour réinitialiser."></canvas>'
        + E('div', 'Drag to turn · Right-drag to move · Pinch or Ctrl + scroll to zoom', 'Glissez pour tourner · Clic droit pour déplacer · Pincez ou Ctrl + molette pour zoomer', 'cube-hint')
        + '<div class="cube-ui">'
        + E('button', 'Turn freely', 'Tourner librement', '', 'id="cube-turn" type="button" aria-pressed="false"')
        + '<button id="cube-out" type="button" aria-label="Zoom out" data-aria-fr="Dézoomer">&minus;</button>'
        '<button id="cube-in" type="button" aria-label="Zoom in" data-aria-fr="Zoomer">+</button>'
        + E('button', 'Reset', 'Réinitialiser', '', 'id="cube-reset" type="button"')
        + '</div>'
        '<div id="cube-fallback" aria-hidden="true"><svg viewBox="-4.27 -3.96 8.54 7.92">' + MARK + '</svg></div>'
        '</div></section>')

    explore = band(
        '<div class="rv">' + E('span', 'Explore the products', 'Explorer les produits', 'eyebrow')
        + E('h2', 'Six things Nastaliq does, each with its real status.', 'Six choses que fait Nastaliq, chacune avec son état réel.', 'h2') + '</div>'
        '<div class="tiles">'
        + tile('suite', 'ok', 'Available', 'Disponible', 'Sell', 'Vendre',
               'Invoicing and customer records today. A counter point of sale is in development.',
               'Facturation et dossiers clients dès aujourd\'hui. Un point de vente au comptoir est en développement.', cta=('Explore selling', 'Découvrir la vente'))
        + tile('suite', 'ok', 'Available', 'Disponible', 'Stock', 'Stocker',
               'Inventory is available today. Phone-friendly receiving, transfer and counting screens with barcode scanning are in early access.',
               'L\'inventaire est disponible aujourd\'hui. Les écrans de réception, de transfert et de comptage adaptés au téléphone, avec lecture de codes à barres, sont en accès anticipé.', delay=' d1', cta=('Explore stock', 'Découvrir les stocks'))
        + tile('suite', 'ok', 'Available', 'Disponible', 'Buy', 'Acheter',
               'Purchase orders and supplier records tied to what is actually on the shelf.',
               'Bons de commande et fiches fournisseurs liés à ce qui est réellement en rayon.', delay=' d2', cta=('Explore buying', 'Découvrir les achats'))
        + tile('suite', 'ok', 'Available', 'Disponible', 'Books', 'Comptabilité',
               'Accounting that updates as sales and purchases happen, so the numbers are current.',
               'Une comptabilité qui se met à jour à chaque vente et achat, pour des chiffres toujours à jour.', cta=('Explore the books', 'Découvrir la comptabilité'))
        + tile('pos', 'warn', 'In development', 'En développement', 'Point of sale', 'Point de vente',
               'A clean, fast till for restaurants, fast food and bakeries.',
               'Une caisse rapide et épurée pour restaurants, restauration rapide et boulangeries.', delay=' d1', cta=('Explore point of sale', 'Découvrir le point de vente'))
        + tile('janitorial', 'warn', 'Early access', 'Accès anticipé', 'Janitorial operations', 'Gestion des services d\'entretien',
               'Run a commercial cleaning company from one app, for cleaners, supervisors and clients.',
               'Gérez une entreprise d\'entretien commercial depuis une seule application, pour les employés, les superviseurs et les clients.', delay=' d2', cta=('Explore janitorial', 'Découvrir l\'entretien'))
        + '</div>', '', True)

    claude = band(
        '<div class="rv">' + E('span', 'Claude-powered assistance', 'Assistance propulsée par Claude', 'eyebrow')
        + E('h2', 'AI that works on your own business data.', 'Une IA qui travaille sur les données de votre entreprise.', 'h2')
        + E('p', 'We connect the system to the Anthropic Claude API to answer questions and help with routine work. Each feature carries its real status.',
            'Nous relions le système à l\'API Claude d\'Anthropic pour répondre aux questions et aider dans les tâches courantes. Chaque fonction affiche son état réel.', 'lede') + '</div>'
        '<div class="tiles">'
        + '<article class="tile rv">' + status('warn', 'Pilot', 'Projet pilote') + E('h3', 'Ask in plain language', 'Posez vos questions en langage courant', 'h3')
        + E('p', 'Ask for last week\'s sales by item or what is running low. The system finds the answer in your records.', 'Demandez les ventes de la semaine par article ou ce qui s\'épuise. Le système trouve la réponse dans vos dossiers.') + '</article>'
        + '<article class="tile rv d1">' + status('warn', 'Pilot', 'Projet pilote') + E('h3', 'Help inside the screen', 'De l\'aide dans l\'écran', 'h3')
        + E('p', 'Step-by-step guidance for the form you are filling in.', 'Un accompagnement pas à pas pour le formulaire que vous remplissez.') + '</article>'
        + '<article class="tile rv d2">' + status('plan', 'Planned', 'Prévu') + E('h3', 'Discrepancy auditing', 'Audit des écarts', 'h3')
        + E('p', 'Automatic checks that flag mismatches between stock, purchases and the books.', 'Des vérifications automatiques qui signalent les écarts entre stocks, achats et comptabilité.') + '</article>'
        '</div>', 'alt', True)

    switching = band(
        '<div class="rv">' + E('span', 'Already running something else?', 'Vous utilisez déjà autre chose?', 'eyebrow')
        + E('h2', 'Tell us what you use today.', 'Dites-nous ce que vous utilisez aujourd\'hui.', 'h2')
        + E('p', 'Write to us with what you sell, how many locations you run, and what your tills and spreadsheets look like now. We reply with a plan and a price.',
            'Écrivez-nous ce que vous vendez, combien d\'emplacements vous exploitez et à quoi ressemblent vos caisses et vos tableurs aujourd\'hui. Nous répondons avec un plan et un prix.', 'lede')
        + '<div class="cta">' + E('a', 'Tell us about your business', 'Parlez-nous de votre entreprise', 'btn', 'href="contact.html"') + '</div></div>', 'center')

    how = band(
        '<div class="rv">' + E('span', 'How we work', 'Notre façon de travailler', 'eyebrow')
        + E('h2', 'We run it so you do not have to.', 'Nous l\'exploitons pour que vous n\'ayez pas à le faire.', 'h2') + '</div>'
        '<dl class="facts rv">'
        + '<div class="fact"><dt data-fr="Hébergement">Hosting</dt>' + E('dd', 'Cloud only. We run it for you and keep it updated. No on-premise installs.', 'Infonuagique seulement. Nous l\'exploitons et le tenons à jour. Aucune installation sur place.') + '</div>'
        + '<div class="fact"><dt data-fr="Tarification">Pricing</dt>' + E('dd', 'A flat monthly subscription with unlimited users, plus a one-time setup fee.', 'Un abonnement mensuel fixe, utilisateurs illimités, plus des frais d\'installation uniques.') + '</div>'
        + '<div class="fact"><dt data-fr="Mise en service">Go-live</dt>' + E('dd', 'Typically about six weeks from kickoff to your first live day.', 'Habituellement environ six semaines entre le lancement et le premier jour en production.') + '</div>'
        + '<div class="fact"><dt data-fr="Livraison">Delivery</dt>' + E('dd', 'Built and supported by a small team based in Lahore, Pakistan, for clients in North America.', 'Conçu et soutenu par une petite équipe basée à Lahore, au Pakistan, pour des clients en Amérique du Nord.') + '</div>'
        '</dl>', 'alt')

    faqs = [
        ('What does it cost?', 'Combien ça coûte?',
         'A flat monthly subscription with unlimited users, plus a one-time setup fee. We send an exact price once we know your locations and what you sell.',
         'Un abonnement mensuel fixe, utilisateurs illimités, plus des frais d\'installation uniques. Nous vous envoyons un prix précis dès que nous connaissons vos emplacements et ce que vous vendez.'),
        ('How long does it take to go live?', 'Combien de temps faut-il pour démarrer?',
         'Typically about six weeks from kickoff to your first live day.',
         'Habituellement environ six semaines entre le lancement et votre premier jour en production.'),
        ('Do I have to install anything?', 'Dois-je installer quelque chose?',
         'No. Nastaliq is cloud only. We run it, update it and keep it available. There is nothing to install on a server.',
         'Non. Nastaliq est offert seulement dans le nuage. Nous l\'exploitons, le mettons à jour et le gardons disponible. Il n\'y a rien à installer sur un serveur.'),
        ('Is it available in French?', 'Est-ce offert en français?',
         'Yes. English and French on every screen with one switch, using Canadian French terms such as courriel and téléverser.',
         'Oui. Anglais et français sur chaque écran avec un seul bouton, avec la terminologie du français canadien, comme courriel et téléverser.'),
        ('Which features are ready today?', 'Quelles fonctions sont prêtes aujourd\'hui?',
         'Each feature carries a status: Available, Early access, In development, Pilot or Planned. Available means clients can use it today. The Products page lists every status.',
         'Chaque fonction porte un état : Disponible, Accès anticipé, En développement, Projet pilote ou Prévu. Disponible signifie que des clients peuvent l\'utiliser aujourd\'hui. La page Produits liste chaque état.'),
        ('Who builds and supports it?', 'Qui le conçoit et le soutient?',
         'A small team based in Lahore, Pakistan, serving clients in North America.',
         'Une petite équipe basée à Lahore, au Pakistan, au service de clients en Amérique du Nord.'),
    ]
    faq = band(
        '<div class="rv">' + E('span', 'Frequently asked questions', 'Questions fréquentes', 'eyebrow')
        + E('h2', 'Questions we get before anyone signs.', 'Les questions qu\'on nous pose avant de signer.', 'h2') + '</div>'
        '<div class="faq rv">' + ''.join(
            '<details><summary data-fr="%s">%s</summary><p data-fr="%s">%s</p></details>' % (x(qf), qe, x(af), ae) for qe, qf, ae, af in faqs)
        + '</div>')

    close = band(
        '<div class="rv">' + E('h2', 'Tell us about your business.', 'Parlez-nous de votre entreprise.', 'display')
        + '<div class="cta">' + E('a', 'Get in touch', 'Nous joindre', 'btn', 'href="contact.html"') + E('a', 'See the products', 'Voir les produits', 'btn alt', 'href="products.html"') + '</div></div>',
        'center alt')

    ld = ('<script type="application/ld+json">' + json.dumps({
        '@context': 'https://schema.org', '@type': 'Organization', 'name': 'Nastaliq LLP', 'url': 'https://nastaliq.co/',
        'email': 'hello@nastaliq.co', 'description': PAGES['index'][2]}) + '</script>')
    return head('index') + '<body>' + header('index') + '<main id="main">' + hero + what + cube + explore + claude + switching + how + faq + close + '</main>' + footer() + \
        '<script src="vendor/three.min.js" defer></script><script src="js/cube.js" defer></script>' + ld + '</body></html>'

# ------------------------------------------------------------------ products
def products():
    cats = ''.join('<a href="#%s"><b data-fr="%s">%s</b><span data-fr="%s">%s</span></a>' % (p[0], x(p[5]), p[4], x(p[9]), p[8]) for p in PRODUCTS)
    cards = ''
    for p in PRODUCTS:
        ul = ''
        if p[10]:
            ul = '<ul>' + ''.join('<li data-fr="%s">%s</li>' % (x(f), e) for e, f in p[10]) + '</ul>'
        cards += ('<article class="prod rv" id="%s">%s<h2 class="h3" data-fr="%s">%s</h2><p data-fr="%s">%s</p>%s</article>'
                  % (p[0], status(p[1], p[2], p[3]), x(p[5]), p[4], x(p[7]), p[6], ul))
    hero = ('<section class="band hero"><div class="inner">'
            + E('span', 'Products', 'Produits', 'eyebrow')
            + E('h1', 'What we build and where it stands.', 'Ce que nous construisons et où nous en sommes.', 'display')
            + E('p', 'Every product carries a status. Available means clients can use it today. Anything else says so.', 'Chaque produit affiche son état. Disponible signifie que des clients peuvent l\'utiliser aujourd\'hui. Tout le reste est indiqué.', 'lede')
            + '<div class="legend">' + status('ok', 'Available', 'Disponible') + status('warn', 'Early access, In development, Pilot', 'Accès anticipé, En développement, Projet pilote') + status('plan', 'Planned', 'Prévu') + '</div>'
            '</div></section>')
    body = ('<section class="band alt" style="padding-top:clamp(40px,6vw,72px)"><div class="wide"><div class="split">'
            '<aside class="cats" aria-label="Product categories" data-aria-fr="Catégories de produits"><h2 data-fr="Catégories">Categories</h2>' + cats + '</aside>'
            '<div>' + cards + '</div></div></div></section>')
    close = band('<div class="rv">' + E('h2', 'Ready to talk?', 'On en discute?', 'h2') + '<div class="cta">' + E('a', 'Get in touch', 'Nous joindre', 'btn', 'href="contact.html"') + '</div></div>', 'center')
    return head('products') + '<body>' + header('products') + '<main id="main">' + hero + body + close + '</main>' + footer() + '</body></html>'

# ------------------------------------------------------------------ company
def company():
    hero = ('<section class="band hero"><div class="inner">'
            + E('span', 'Company', 'Entreprise', 'eyebrow')
            + E('h1', 'A small team that sets up your system and keeps it running.', 'Une petite équipe qui installe votre système et le maintient en marche.', 'display')
            + E('p', 'Nastaliq builds and hosts cloud business software for small and mid-sized businesses in North America.', 'Nastaliq conçoit et héberge des logiciels d\'affaires infonuagiques pour les petites et moyennes entreprises d\'Amérique du Nord.', 'lede')
            + '</div></section>')
    facts = band(
        '<div class="rv">' + E('span', 'Facts', 'Faits', 'eyebrow') + E('h2', 'Who we are.', 'Qui nous sommes.', 'h2') + '</div>'
        '<dl class="facts rv">'
        '<div class="fact"><dt data-fr="Raison sociale">Legal name</dt><dd>Nastaliq LLP</dd></div>'
        '<div class="fact"><dt data-fr="Immatriculation">Registered</dt>' + E('dd', 'Incorporated with the Securities and Exchange Commission of Pakistan (SECP).', 'Constituée auprès de la Securities and Exchange Commission of Pakistan (SECP).') + '</div>'
        '<div class="fact"><dt data-fr="Base de livraison">Delivery base</dt>' + E('dd', 'Lahore, Pakistan', 'Lahore, Pakistan') + '</div>'
        '<div class="fact"><dt data-fr="Clientèle">Serving</dt>' + E('dd', 'North America', 'Amérique du Nord') + '</div>'
        '<div class="fact"><dt data-fr="Équipe">Team</dt>' + E('dd', 'A small team: software engineering, accounting, and marketing and operations.', 'Une petite équipe : génie logiciel, comptabilité, ainsi que marketing et opérations.') + '</div>'
        '<div class="fact"><dt data-fr="Modèle d\'hébergement">Hosting model</dt>' + E('dd', 'Cloud only. We do not sell on-premise installs.', 'Infonuagique seulement. Nous ne vendons pas d\'installations sur place.') + '</div>'
        '</dl>', 'alt')
    princ = band(
        '<div class="rv">' + E('span', 'Principles', 'Principes', 'eyebrow') + E('h2', 'How we work with clients.', 'Notre façon de travailler avec nos clients.', 'h2') + '</div>'
        '<div class="tiles">'
        '<article class="tile rv">' + E('h3', 'Say what is real', 'Dire ce qui est réel', 'h3') + E('p', 'Every feature is labelled with its actual status, from Available to Planned.', 'Chaque fonction est étiquetée selon son état réel, de Disponible à Prévu.') + '</article>'
        '<article class="tile rv d1">' + E('h3', 'Accounting first', 'La comptabilité d\'abord', 'h3') + E('p', 'Accounting expertise is part of the team, so the books are set up properly from day one.', 'L\'expertise comptable fait partie de l\'équipe, ce qui garantit des livres bien configurés dès le premier jour.') + '</article>'
        '<article class="tile rv d2">' + E('h3', 'Your language', 'Votre langue', 'h3') + E('p', 'English and French throughout, because Canadian businesses work in both.', 'Anglais et français partout, parce que les entreprises canadiennes travaillent dans les deux langues.') + '</article>'
        '</div>', '', True)
    return head('company') + '<body>' + header('company') + '<main id="main">' + hero + facts + princ + '</main>' + footer() + '</body></html>'

# ------------------------------------------------------------------ contact
def contact():
    hero = ('<section class="band hero"><div class="inner">'
            + E('span', 'Contact', 'Contact', 'eyebrow')
            + E('h1', 'Tell us about your business.', 'Parlez-nous de votre entreprise.', 'display')
            + E('p', 'Write to us with what you sell, how many locations you run, and what you use today. We reply with a plan and a price.', 'Écrivez-nous ce que vous vendez, combien d\'emplacements vous exploitez et ce que vous utilisez aujourd\'hui. Nous répondons avec un plan et un prix.', 'lede')
            + '</div></section>')
    mail = band(
        '<div class="rv">' + E('span', 'Email', 'Courriel', 'eyebrow') + '<div class="mail" id="mail">hello@nastaliq.co</div>'
        '<div class="cta">' + E('button', 'Copy address', 'Copier l\'adresse', 'btn', 'id="copy" type="button"') + '</div></div>'
        '<ol class="steps">'
        '<li class="rv"><b data-fr="Ce que vous vendez">What you sell</b>' + E('span', 'Products, services, or both.', 'Produits, services, ou les deux.', '') + '</li>'
        '<li class="rv d1"><b data-fr="Vos emplacements">Your locations</b>' + E('span', 'How many, and where.', 'Combien, et où.', '') + '</li>'
        '<li class="rv d2"><b data-fr="Ce que vous utilisez">What you use today</b>' + E('span', 'Tills, spreadsheets, another system.', 'Caisses, tableurs, un autre système.', '') + '</li>'
        '</ol>', 'alt')
    return head('contact') + '<body>' + header('contact') + '<main id="main">' + hero + mail + '</main>' + footer() + '</body></html>'

if __name__ == '__main__':
    for name, fn in (('index', home), ('products', products), ('company', company), ('contact', contact)):
        open(os.path.join(PUB, name + '.html'), 'w', encoding='utf-8').write(fn())
        print('wrote', name + '.html')
