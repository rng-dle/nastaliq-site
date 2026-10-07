"""Build the service pages from public/index.html (header, footer, styles) plus the copy below.

Run from the repo root:  python3 scripts/build_pages.py
Writes public/styles.css, public/<slug>.html and public/sitemap.xml. Commit the output;
Cloudflare serves public/ as-is, there is no build step there.
Rule for all copy: never name the ERP platform or framework, and no city or country names.
Approved exception: the unlisted FBR page may name FBR and Pakistan. Unlisted pages are in the sitemap
but not in the footer or related links, so those names stay on that page.
No exception for the platform or framework names, on any page, ever.
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
  dict(slug="fbr-e-invoicing", label="FBR e-invoicing", service="FBR digital invoicing integration", unlisted=True,
    title="FBR Digital Invoicing Integration for Your ERP | Nastaliq",
    desc="Nastaliq connects your ERP to FBR's Digital Invoicing system: invoices reported in real time, FBR invoice number and QR code printed, rejections easy to fix.",
    h1="FBR digital invoicing, built into your ERP.",
    lede="FBR requires sales tax registered businesses in Pakistan to report invoices to its Digital Invoicing system as they are issued. Nastaliq connects your ERP to FBR, so each invoice goes out in real time and comes back with its FBR invoice number and QR code, ready to print.",
    sections=[
      ("What the connection does", "ul", ["Sends each sales tax invoice to FBR as it is issued, from the same ERP that runs your stock and accounts.", "Prints the FBR invoice number and QR code on every invoice.", "Keeps the FBR invoice number with each invoice in the system.", "Flags rejected invoices, so your team can correct them and send them again."]),
      ("How we set it up", "ol", ["You get your security token from FBR's IRIS portal, and we connect it to your ERP.", "We run FBR's sandbox test scenarios for the kinds of invoices you issue.", "Once the tests pass, we switch the connection on for live invoices.", "Your team keeps invoicing as before, and we keep the connection up to date when FBR changes the system."]),
      ("Check your deadline", "p", ["FBR has phased digital invoicing in by business size and sector, and has moved the deadlines more than once. Check the current date for your category on FBR's website or with your tax adviser."]),
      ("Pricing", "p", ["A one-time fee for the FBR connection, then included in your monthly plan, from $400 a month. Tell us which sales tax scenarios apply to your invoices and we will tell you the fee."]),
    ],
    faqs=[
      ("What is FBR digital invoicing?", "FBR's system for sales tax registered businesses to report each invoice to FBR in real time. Each accepted invoice gets an FBR invoice number and a QR code, which go on the printed invoice."),
      ("Who has to use FBR digital invoicing?", "Sales tax registered persons, phased in by business size and sector. FBR has changed the deadlines more than once, so check the current date for your category."),
      ("Do we need separate software for FBR invoicing?", "No. Nastaliq builds the FBR connection into the same ERP that runs your invoicing, stock and accounts."),
      ("What happens if FBR rejects an invoice?", "It is flagged in the ERP, so your team can correct it and send it again."),
      ("How much does FBR integration cost?", "A one-time fee for the connection, then included in your monthly plan."),
    ]),
  dict(slug="erp-pricing", label="Pricing", service="Managed cloud ERP", link="ERP pricing",
    title="ERP Pricing: Flat Monthly Plans, Unlimited Users | Nastaliq",
    desc="Nastaliq ERP pricing: Core $400, Scale $900 and Enterprise from $2,000 a month, all with unlimited users. Hosting, updates and support included.",
    h1="Flat monthly pricing, with no per-user fees.",
    lede="Every Nastaliq plan includes hosting, updates and support, with unlimited users. You pay a one-time launch fee to go live, then one monthly fee that does not change when you add staff.",
    sections=[
      ("Monthly plans", "ul", ["Core, $400 a month: accounting, stock, sales, purchasing and e-invoicing for one company, with support in business hours.", "Scale, $900 a month: everything in Core, plus several branches, manufacturing, point of sale, alerts and priority support.", "Enterprise, from $2,000 a month: a dedicated server, a named engineer and agreed response times."]),
      ("One-time fees", "ul", ["Launch, $6,000 to $12,000: the system configured, tested and live in about six weeks, with your team trained.", "Data migration: priced per 1,000 documents after a paid sample, because handwritten records take longer than printed ones.", "E-invoicing: a one-time fee per country for the connection, then included in your monthly plan."]),
      ("Included in every plan", "ul", ["Unlimited users.", "Cloud hosting with offsite backups.", "Updates.", "Support from the people who built your system.", "Your data, exportable whenever you want it."]),
    ],
    faqs=[
      ("How much does an ERP system cost?", "With Nastaliq, $400 or $900 a month for most companies, or from $2,000 a month for Enterprise, plus a one-time launch fee of $6,000 to $12,000. Every plan has unlimited users."),
      ("Do you charge per user?", "No. Every plan includes unlimited users, so adding staff never changes your bill."),
      ("Is there a software licence fee?", "No. You pay for setup, hosting, updates and support. There is no licence fee on top."),
      ("What does the launch fee cover?", "Configuring the system around how you work, testing it, a pilot on one branch, warehouse or process, and training your team. Most launches go live in about six weeks."),
    ],
    offers=[("Core plan", 400, "MONTH"), ("Scale plan", 900, "MONTH"), ("Enterprise plan", 2000, "MONTH", "min"), ("Launch", 6000, None, "min", 12000)]),
  dict(slug="erp-implementation", label="Implementation", service="ERP implementation",
    title="ERP Implementation in About Six Weeks | Nastaliq",
    desc="Nastaliq ERP implementation: a walkthrough, a pilot on real work, then the move with your records, staff training and hosting. Live in about six weeks.",
    h1="ERP implementation that starts with a pilot, not a big bang.",
    lede="Nastaliq configures accounting, stock, buying, selling and manufacturing around how your business already works. Each stage gives you something working before the next one starts, and most companies are live in about six weeks.",
    sections=[
      ("Four stages", "ol", ["A walkthrough. You show us how orders, stock and money move today, and we tell you plainly whether we are a fit.", "A pilot. We set up one branch, one warehouse or one process first, and your team runs real work on it.", "The move. Records come over, staff learn on their own screens, and the old system stays readable until you are sure.", "Day to day. Hosting, updates and support from the people who built it. Your data exports whenever you want it."]),
      ("What gets set up", "ul", ["Chart of accounts and tax reports, with your accountant.", "Items, warehouses and branches.", "Customers, suppliers and price lists.", "Buying, selling and, if you make things, manufacturing.", "Users, and what each role can see."]),
      ("Cost", "p", ["Launch is a one-time $6,000 to $12,000, depending on the size of the setup. After that, one monthly plan from $400, with unlimited users."]),
    ],
    faqs=[
      ("How long does ERP implementation take?", "About six weeks for a standard launch, from walkthrough to go-live."),
      ("Why start with a pilot?", "Running real work on one branch, warehouse or process shows problems early, while they are cheap to fix, and gives your team confidence before everything moves."),
      ("Do you train our staff?", "Yes. Staff learn on their own screens, and training is part of the launch fee."),
      ("What happens after go-live?", "We host the system, keep it updated and support your team. Your data can be exported whenever you want it."),
    ]),
  dict(slug="erp-for-retail", label="Retail", service="ERP for retailers with several branches",
    title="ERP for Retailers with Several Branches | Nastaliq",
    desc="Cloud ERP for retailers with several branches: stock in every shop and warehouse, point of sale, transfers between branches and one set of accounts.",
    h1="Every branch's stock and sales in one system.",
    lede="Nastaliq sets up and runs ERP for retailers with more than one shop. Every branch sells from the same system, so stock, sales and accounts are up to date across the business, not just at month end.",
    sections=[
      ("What it covers", "ul", ["Stock in every shop and warehouse, visible from head office.", "Transfers between branches and warehouses.", "Point of sale at each counter, connected to stock and accounts.", "Buying from suppliers, centrally or per branch.", "Morning alerts for low stock and late payments.", "One set of accounts for the whole business."]),
      ("Good fit", "p", ["Bookshops, pharmacies, food and drink chains, and any retailer whose spreadsheets can no longer keep up with several branches."]),
      ("Pricing", "p", ["Several branches and point of sale are part of the Scale plan at $900 a month, with unlimited users. Launch is a one-time $6,000 to $12,000."]),
    ],
    faqs=[
      ("Can head office see every branch's stock?", "Yes. Stock is tracked per shop and warehouse, and head office sees all of it in one place."),
      ("Can we move stock between branches?", "Yes. Transfers between branches and warehouses are recorded in the system, so both sides stay accurate."),
      ("Does it include point of sale?", "Yes. The Scale plan includes point of sale, connected to stock and accounts."),
      ("How much does it cost for several branches?", "Several branches are covered by the Scale plan at $900 a month, with unlimited users."),
    ]),
  dict(slug="custom-erp-apps", label="Custom apps", service="Custom ERP apps",
    title="Custom ERP Apps, Alerts and Dashboards | Nastaliq",
    desc="Nastaliq builds custom apps on top of your ERP: morning alerts for low stock and late payments, owner dashboards, point of sale and your own branding.",
    h1="The apps your team needs, built on top of your ERP.",
    lede="Standard modules cover most of a business. For the rest, Nastaliq builds custom apps that sit on top of your ERP, so updates to the core system don't break them.",
    sections=[
      ("What we build", "ul", ["Morning alerts for low stock and late payments, sent before the day starts.", "Owner dashboards: sales, money owed, cash and stock at a glance.", "Point of sale for restaurants, cafés and bakeries.", "Your own branding on the admin: name, logo and colours.", "Custom reports and print formats."]),
      ("Built to survive updates", "p", ["Each app is built separately from the core system, so it keeps working when the core is updated."]),
      ("Pricing", "p", ["Alerts and point of sale are part of the Scale plan at $900 a month. For anything else, tell us what you need and we will quote it."]),
    ],
    faqs=[
      ("Can you build a custom app for our ERP?", "Yes. Tell us what your team needs and we will tell you what it takes and what it costs."),
      ("Will custom apps break when the system is updated?", "They are built not to. Each app sits separately from the core system, so core updates don't overwrite it."),
      ("What do the morning alerts cover?", "Items running low on stock and payments that are late, sent each morning so they can be dealt with before the day starts."),
      ("Can the admin carry our branding?", "Yes. The admin can show your company's name, logo and colours."),
    ]),
  dict(slug="how-much-does-erp-cost", kind="guide", date="2026-10-07", label="Guides", faqhead="Common questions",
    link="How much does an ERP system cost?", service="How much does an ERP system cost?",
    title="How Much Does an ERP System Cost? | Nastaliq",
    desc="What an ERP system really costs: licences, implementation, data migration, hosting and support, per-user versus flat pricing, and what to ask before you sign.",
    h1="How much does an ERP system cost?",
    lede="The price of an ERP is rarely one number. It is usually five: the software licence, getting it set up, moving your records in, hosting it, and supporting your team once it is live. Here is what each one covers, and what to ask about each before you sign.",
    sections=[
      ("1. The software licence", "p", ["Many ERP vendors charge per user, per month. That looks cheap for a small team and grows with every person you add. Others charge a flat fee for the whole company, or no licence fee at all and charge for the service around the software instead. Ask what happens to the bill when you hire ten more people."]),
      ("2. Implementation", "p", ["Implementation is the work of setting the system up around how you run: your chart of accounts, items, warehouses, branches, prices, approvals and reports. It is usually a one-time fee, and it is where most projects go over budget. Ask what is included, how long it takes, and whether a pilot comes before the full switch."]),
      ("3. Data migration", "p", ["Bringing your history in is often priced separately. Clean exports from old software are quick. Paper records and handwritten logs take far longer, because every document has to be read and checked. Ask for a paid sample before agreeing a price for the whole archive."]),
      ("4. Hosting", "p", ["A cloud ERP needs servers, backups and updates. Some vendors include hosting in the monthly fee, others bill it separately or leave it to you. Ask where your data is hosted, how often it is backed up, and whether you can export it."]),
      ("5. Support and changes", "p", ["After go-live your team will have questions, and the business will keep changing. Ask whether support is included, how fast it responds, and how new reports or changes are priced."]),
      ("What Nastaliq charges", "ul", ["Monthly plans of $400 (Core), $900 (Scale) and from $2,000 (Enterprise), all with unlimited users.", "A one-time launch fee of $6,000 to $12,000, with about six weeks to go live.", "Hosting, updates and support included in every plan.", "Data migration priced per 1,000 documents after a paid sample."]),
    ],
    faqs=[
      ("Is per-user ERP pricing cheaper?", "For a very small team it can be. Because the bill grows with every user, a flat fee usually works out cheaper as the team grows, and it never discourages you from giving more staff access."),
      ("What is the biggest hidden cost in an ERP project?", "Usually implementation and data migration, because both depend on how your business works and how messy your records are. Agree what is included, and ask for a pilot or sample before committing to the full price."),
      ("How much does a cloud ERP cost per month?", "It depends on the vendor and the pricing model. Nastaliq's plans are $400, $900 or from $2,000 a month, with unlimited users and hosting included."),
      ("Should hosting be included in the ERP price?", "It is simpler when it is. If hosting, backups and updates come from the same team that set the system up, there is one place to go when something breaks."),
    ]),
  dict(slug="paper-records-to-erp", kind="guide", date="2026-10-07", label="Guides", faqhead="Common questions",
    link="How to move paper records into an ERP", service="How to move paper records into an ERP",
    title="How to Move Paper Records into an ERP | Nastaliq",
    desc="A step-by-step guide to moving receipts, delivery notes and handwritten logs into an ERP: what to bring in, how to sample, check and import, and what it costs.",
    h1="How to move paper records into an ERP",
    lede="Many growing companies still keep years of history on paper: receipts, delivery notes, handwritten registers. Moving it into an ERP makes it searchable and gives you real reports from the first day. Here is how to do it without stopping the business.",
    sections=[
      ("1. Decide what history you need", "p", ["Not every piece of paper needs to come across. Start with what you will actually use: customer and supplier balances, sales history for reporting, and stock movements. Older or rarely used records can be archived instead."]),
      ("2. Sort the documents by type", "p", ["Group the paper into types, such as sales invoices, purchase receipts, delivery notes and handwritten logs. Each type has its own layout and its own fields, and each is handled as its own batch."]),
      ("3. Run a sample first", "p", ["Bring in a small, representative batch of each type before committing to the whole archive. The sample shows how readable the records are, how long they take, and what the full migration will cost."]),
      ("4. Read, check and link", "p", ["Each document is read into the system's fields and checked, then linked to the right customer, supplier and item. Linking is what turns a pile of scans into history you can report on."]),
      ("5. Import in batches, then switch over", "p", ["Bring records in batch by batch, checking each one before it reaches the live system. Keep the old records accessible until you are sure everything has come across."]),
    ],
    faqs=[
      ("Can handwritten records be moved into an ERP?", "Yes. They take longer than printed documents, because each one has to be read and checked, so they usually cost more per document."),
      ("How much does it cost to move paper records into an ERP?", "It depends on volume and how readable the records are, which is why a paid sample comes first. Nastaliq prices migration per 1,000 documents after the sample."),
      ("Do we have to stop working while records are migrated?", "No. Records come over in batches while the business keeps running, and the old records stay accessible until the move is complete."),
      ("What should we migrate first?", "Balances and the history you will report on: customers, suppliers, items, opening balances, and recent sales and purchases."),
    ]),
  dict(slug="what-is-e-invoicing", kind="guide", date="2026-10-07", label="Guides", faqhead="Common questions",
    link="What is e-invoicing, and how does it work?", service="What is e-invoicing, and how does it work?",
    title="What Is E-Invoicing and How Does It Work? | Nastaliq",
    desc="E-invoicing explained: how invoices reach the tax authority in real time, what comes back on each one, what happens on rejection, and how an ERP connects.",
    h1="What is e-invoicing, and how does it work?",
    lede="E-invoicing means sending each invoice to the tax authority electronically, usually as it is issued, instead of only reporting totals in a periodic return. More tax authorities require it every year. Here is how it works and what it means for your invoicing.",
    sections=[
      ("How it works", "ol", ["Your system creates the invoice as usual.", "The invoice data is sent to the tax authority's system, usually in real time.", "The authority checks it, and either accepts it or rejects it with a reason.", "An accepted invoice comes back with a reference from the authority, often a unique number and a QR code, which go on the invoice you send."]),
      ("Clearance and reporting", "p", ["Some tax authorities clear each invoice before it is valid, so the customer only ever receives an invoice the authority has accepted. Others accept a report of each invoice shortly after it is issued. Either way, the invoice data has to leave your system in the authority's format."]),
      ("Why connect it to your ERP", "p", ["Typing invoices into a government portal by hand does not scale. When the connection is built into the ERP that already creates your invoices, reporting happens automatically, rejections show up where your team works, and your stock and accounts stay in step with what the authority sees."]),
      ("What to ask before you connect", "ul", ["Which of your invoice types and tax scenarios the connection covers.", "How rejected invoices are flagged and corrected.", "Whether the connection is tested in the authority's sandbox before it goes live.", "Who keeps it working when the authority changes its system."]),
    ],
    faqs=[
      ("What is the difference between an e-invoice and a PDF invoice?", "A PDF is a picture of an invoice for people to read. An e-invoice is structured data in the tax authority's format, sent to its system so it can be checked automatically."),
      ("Is e-invoicing mandatory?", "In a growing number of countries, yes, usually phased in by business size or sector. Check the current rules and deadlines with your tax authority or adviser."),
      ("What happens when an e-invoice is rejected?", "The authority returns it with a reason. The invoice has to be corrected and sent again before it counts."),
      ("Can e-invoicing be added to an existing ERP?", "Usually, if the ERP can send invoice data in the authority's format. Nastaliq builds the connection into the ERP it runs for each client."),
    ]),
]
ORDER = ["erp-implementation", "erp-pricing", "erp-for-manufacturers", "erp-for-retail", "erp-data-migration",
         "e-invoicing", "restaurant-pos", "custom-erp-apps", "erp-partner-development", "fbr-e-invoicing",
         "how-much-does-erp-cost", "paper-records-to-erp", "what-is-e-invoicing"]
PAGES.sort(key=lambda p: ORDER.index(p["slug"]))
SHORT = {"erp-implementation": "Implementation", "erp-pricing": "Pricing", "erp-for-manufacturers": "Manufacturers",
         "erp-for-retail": "Retail", "erp-data-migration": "Data migration", "e-invoicing": "E-invoicing",
         "restaurant-pos": "Restaurant POS", "custom-erp-apps": "Custom apps", "erp-partner-development": "Partner firms",
         "how-much-does-erp-cost": "What ERP costs", "paper-records-to-erp": "Paper to ERP", "what-is-e-invoicing": "E-invoicing explained"}

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

def offer(t):  # (name, price, unit) or (name, min price, unit, "min"[, max price])
    name, price, unit, *rest = t
    spec = {"@type": "UnitPriceSpecification", "priceCurrency": "USD", ("minPrice" if rest else "price"): price}
    if len(rest) > 1: spec["maxPrice"] = rest[1]
    if unit: spec["unitText"] = unit
    return {"@type": "Offer", "name": name, "priceSpecification": spec}

def ld(page, url):
    if page.get("kind") == "guide":
        service = {"@type": "Article", "@id": f"{url}#article", "headline": page["h1"], "description": page["desc"],
                   "url": url, "mainEntityOfPage": url, "datePublished": page["date"], "dateModified": page["date"],
                   "author": ORG, "publisher": {**ORG, "logo": f"{SITE}/apple-touch-icon.png"}, "image": f"{SITE}/og-image.png"}
    else:
        service = {"@type": "Service", "@id": f"{url}#service", "name": page["service"], "serviceType": page["label"],
                   "description": page["desc"], "url": url, "provider": ORG}
    if page.get("offers"): service["offers"] = [offer(t) for t in page["offers"]]
    return {"@context": "https://schema.org", "@graph": [
        service,
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
    listed = [p for p in PAGES if not p.get("unlisted")]
    nav = "".join(f'<nav class="links" aria-label="{label}">' + "".join(f'<a href="/{p["slug"]}">{SHORT[p["slug"]]}</a>' for p in listed if (p.get("kind") == "guide") == g) + "</nav>"
                  for label, g in (("Services", False), ("Guides", True)))
    home, n = re.subn(r'<nav class="links" aria-label="Services">.*?</nav>(?:<nav class="links" aria-label="Guides">.*?</nav>)?', nav, home, flags=re.S)
    assert n == 1, "footer nav not found in index.html"
    (ROOT / "index.html").write_text(home)
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
        second = ('<a class="btn ghost" href="/erp-implementation">How implementation works</a>' if p["slug"] == "erp-pricing"
                  else '<a class="btn ghost" href="/erp-pricing">See all pricing</a>')
        others = "".join(f'<li><a href="/{o["slug"]}">{E(o.get("link", o["service"]))}</a></li>' for o in PAGES if o is not p and not o.get("unlisted") and o.get("kind") != "guide")
        body = "".join(f'<div class="prose"><h2>{E(h)}</h2>{block(k, items)}</div>' for h, k, items in p["sections"])
        if p.get("note"): body += f'<div class="prose"><p class="note">{E(p["note"])}</p></div>'
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
      <div class="cta"><a class="btn primary" href="#contact">{E(cta[0])}</a>{second}</div>
    </div>
  </section>
  <section><div class="wrap">{body}</div></section>
  <section id="faq"><div class="wrap"><div class="head"><p class="label">FAQ</p><h2>{E(p.get('faqhead', p['label'] + ' questions'))}</h2></div>{faqs}</div></section>
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

    full = ["# Nastaliq: full text of nastaliq.co", "", "Nastaliq is an ERP company for growing businesses. Website: https://nastaliq.co. Email: hello@nastaliq.co.", ""]
    for p in listed:
        full += [f"## {p['h1']}", f"URL: {SITE}/{p['slug']}", "", p["lede"], ""]
        for h, k, items in p["sections"]:
            full += [f"### {h}"] + (items if k == "p" else [f"- {t}" for t in items]) + [""]
        full += ["### Questions"] + [f"Q: {q}\nA: {a}\n" for q, a in p["faqs"]] + [""]
    (ROOT / "llms-full.txt").write_text("\n".join(full))
    today = datetime.date.today().isoformat()
    urls = [f"{SITE}/"] + [f"{SITE}/{p['slug']}" for p in PAGES]
    (ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>\n" for u in urls) + "</urlset>\n")
    return urls

if __name__ == "__main__":
    for u in build():
        print(u)
