// Sample data for the home-page dashboard preview. One real public company per industry, figures from its latest annual/quarterly filings,
// all dollar values in $ millions as reported, shown on the site divided by 1,000 so they look like a mid-size business.
// mix: [label, current, prior|null, growth%|null]   trend: [label, value]   fin: [label, current, prior|null]
// kpis: [label, value, sub, up(1/0), view to open]   hl: [title, detail]   Entries marked "derived" are arithmetic on reported numbers.
window.NQ_DATA = {
  Distribution: {
    co: 'Sysco', per: 'fiscal 2025', unit: '$', mixLabel: 'Division', trendLabel: 'Quarterly sales',
    src: 'https://investors.sysco.com/~/media/Files/S/Sysco-IR/documents/annual-reports/Sysco_2025-Annual-Report_Web.pdf',
    mix: [['US Foodservice', 56965, 55339], ['International', 14905, 14561], ['SYGMA', 8410, 7768], ['Other', 1090, 1176]],
    trend: [['Q1', 20500], ['Q2', 20200], ['Q3', 19600], ['Q4', 21100]],
    kpis: [['Annual sales', '$81.4M', '+3.2% vs last year', 1, 'sales'], ['Gross profit', '$14.9M', '18.4% margin', 1, 'accounting'], ['Product cost inflation', '2.5%', 'dairy and poultry', 0, 'reports'], ['Q4 sales', '$21.1M', '+2.8% vs last year', 1, 'reports']],
    fin: [['Sales', 81370, 78844], ['Cost of sales', 66458, 64265], ['Gross profit (derived)', 14912, 14579], ['Net income', 1828, 1955]],
    hl: [['Product cost inflation', 'Running at 2.5% for the year, mostly in dairy and poultry.'], ['US local case volume', 'Down 1.4% for the year, improving through Q4.'], ['Mexico joint venture', 'Divested in the second quarter, so International growth is lower as reported.']]
  },
  Retail: {
    co: 'Target', per: 'fiscal 2024', unit: '$', mixLabel: 'Category', trendLabel: 'Net sales by year',
    src: 'https://app.edgar.tools/companies/TGT/disclosures/revenue',
    mix: [['Food and beverage', 23828, 23899], ['Household essentials', 18614, 18746], ['Home furnishings and decor', 16699, 17760], ['Apparel and accessories', 16505, 16485], ['Hardlines', 15784, 16162], ['Beauty', 13173, 12538]],
    trend: [['FY22', 109120], ['FY23', 107412], ['FY24', 106566]],
    kpis: [['Net sales', '$106.6M', '-0.8% vs last year', 0, 'sales'], ['Food and beverage', '$23.8M', 'largest category', 1, 'sales'], ['Digital sales', '$20.5M', '+5.7% vs last year', 1, 'reports'], ['Stores fulfil', '97.6%', 'of merchandise sales', 1, 'inventory']],
    fin: [['Net sales', 106566, 107412], ['Merchandise sales', 104820, 105803], ['Advertising revenue', 649, 522], ['Credit card profit sharing', 576, 667]],
    hl: [['Home furnishings', 'Down 6% on last year, the weakest category.'], ['Beauty', 'Up 5% on last year, the fastest-growing category.'], ['Shop-in-shop partner', 'The Ulta Beauty agreement ends in August 2026.']]
  },
  Janitorial: {
    co: 'ABM Industries', per: 'fiscal 2025', unit: '$', mixLabel: 'Segment', trendLabel: 'Revenue by year',
    src: 'https://www.sec.gov/Archives/edgar/data/771497/000077149725000031/abm-20251031.htm',
    mix: [['Business and Industry', 4126, 4059.1], ['Manufacturing and Distribution', 1618.6, 1554.3], ['Aviation', 1118.7, 1032.6], ['Technical Solutions', 960.6, 809.3], ['Education', 922, 904]],
    trend: [['FY23', 8096.4], ['FY24', 8359.4], ['FY25', 8745.9]],
    kpis: [['Annual revenue', '$8.75M', '+4.6% vs last year', 1, 'sales'], ['New bookings', '$1.9M', 'a record year', 1, 'reports'], ['Technical Solutions', '$0.96M', '+18.7% vs last year', 1, 'sales'], ['Q4 revenue', '$2.30M', '+5.4% vs last year', 1, 'reports']],
    fin: [['Revenue', 8745.9, 8359.4], ['Business and Industry operating profit', 316.9, 307], ['Manufacturing and Distribution operating profit', 151.4, 166.3], ['Aviation operating profit', 65.2, 59.1], ['Education operating profit', 67.7, 55.3]],
    hl: [['Record new bookings', 'Full-year new sales bookings reached $1.9M, the highest on record.'], ['Aviation margin', 'Q4 operating margin was 5.7%, held back by upfront costs on new programs.'], ['Acquisition', 'WGNSTAR, a technical workforce provider, was announced at year end.']]
  },
  Manufacturing: {
    co: 'Lincoln Electric', per: 'fiscal 2025', unit: '$', mixLabel: 'Segment', trendLabel: 'Net sales by year',
    src: 'https://www.sec.gov/Archives/edgar/data/59527/000005952726000003/leco-20260212xex99d1.htm',
    mix: [['Americas Welding', 2723.6, 2564.8], ['International Welding', 930.9, 933.7], ['Harris Products Group', 578.6, 510.1]],
    trend: [['FY24', 4008.7], ['FY25', 4233]],
    kpis: [['Net sales', '$4.23M', '+5.6% vs last year', 1, 'sales'], ['Net income', '$0.52M', '+11.7% vs last year', 1, 'accounting'], ['Americas Welding', '$2.72M', '+6.2% vs last year', 1, 'sales'], ['Harris Products', '$0.58M', '+13.4% vs last year', 1, 'sales']],
    fin: [['Net sales', 4233, 4008.7], ['Net income', 520.5, 466.1]],
    hl: [['Equipment demand', 'Welding equipment in the Americas grew for the first time since late 2023.'], ['Europe', 'International Welding volumes fell 4% in Q3 on weak European demand.'], ['Price and volume', 'Q3 price was up 7.8% while volumes were down 2.2%.']]
  },
  'Food and beverage': {
    co: 'Starbucks', per: 'fiscal 2025', unit: '$', mixLabel: 'Segment, Q4', trendLabel: 'Quarterly revenue',
    src: 'https://s203.q4cdn.com/326826266/files/doc_financials/2025/q4/SBUX-09-28-2025-Exhibit-99-1.pdf',
    mix: [['North America', 6901.5, 6691.9], ['International', 2070.9, 1893.2], ['Channel Development', 542.6, 465.4]],
    trend: [['Q1', 9400], ['Q2', 8800], ['Q3', 9500], ['Q4', 9600]],
    kpis: [['Annual revenue', '$37.2M', '+3% vs last year', 1, 'sales'], ['Q4 revenue', '$9.6M', '+5% vs last year', 1, 'reports'], ['International Q4', '$2.07M', '+9% vs last year', 1, 'sales'], ['Channel Development Q4', '$0.54M', '+17% vs last year', 1, 'sales']],
    fin: [['Net revenues', 37200, 36200], ['North America Q4 operating income', 308.5, 1253.5], ['Channel Development Q4 operating income', 265.2, 264.7]],
    hl: [['North America margin', 'Q4 operating margin fell to 4.5% from 18.7% a year earlier.'], ['Store closures', '627 stores closed under the restructuring plan announced in September.'], ['Channel growth', 'Channel Development revenue rose 17% in Q4.']]
  },
  Construction: {
    co: 'Quanta Services', per: 'fiscal 2025', unit: '$', mixLabel: 'Segment, Q3', trendLabel: 'Quarterly revenue',
    src: 'https://www.barchart.com/story/news/35787665/quanta-services-reports-third-quarter-2025-results',
    mix: [['Electric Infrastructure', 6170, 5230], ['Underground and Infrastructure', 1460, 1260]],
    trend: [['Q1', 6230], ['Q2', 6770], ['Q3', 7630], ['Q4', 7842]],
    kpis: [['Annual revenue', '$28.5M', '+20.3% vs last year', 1, 'sales'], ['Backlog', '$44.0M', 'a record', 1, 'reports'], ['Operating income', '$1.61M', '+19.7% vs last year', 1, 'accounting'], ['Q4 revenue', '$7.84M', '+19.7% vs last year', 1, 'reports']],
    fin: [['Revenue', 28479.7, 23672.8], ['Operating income', 1611.5, 1346.5], ['Net income to common stock', 1028.4, 904.8]],
    hl: [['Record backlog', 'Total backlog ended the year at $44.0M, up from $39.2M at Q3.'], ['Large power project', 'Selected for a roughly 3 gigawatt generation and grid project.'], ['Electric margin', 'Q3 operating margin was 11.4%, up from 11.0%.']]
  },
  'Professional services': {
    co: 'Accenture', per: 'fiscal 2025', unit: '$', mixLabel: 'Industry group', trendLabel: 'Revenue by year',
    src: 'https://newsroom.accenture.com/content/4q-full-fy25-earnings/q4-and-full-fy25-fact-sheet.pdf',
    mix: [['Products', 21200, null, 8], ['Financial Services', 14760, null, 6], ['Resources', 9480, null, 5], ['Communications, Media, Tech and Health, Public Service (derived)', 24230, null, null]],
    trend: [['FY24 (derived)', 64870], ['FY25', 69670]],
    kpis: [['Annual revenue', '$69.7M', '+7% vs last year', 1, 'sales'], ['New bookings', '$80.6M', 'for the year', 1, 'reports'], ['Operating margin', '14.7%', 'GAAP basis', 1, 'accounting'], ['Q4 revenue', '$17.6M', '+7% vs last year', 1, 'reports']],
    fin: [['Revenue', 69670, 64870], ['New bookings', 80600, null], ['Free cash flow', 10900, null]],
    hl: [['Generative AI bookings', 'New bookings reached $5.9M for the year, $1.8M of it in Q4.'], ['US federal work', 'Expected to take 1 to 1.5 points off next year growth.'], ['Q4 margin', 'Adjusted operating margin was 15.1%, up slightly.']]
  },
  Ecommerce: {
    co: 'Etsy', per: 'fiscal 2025', unit: '%', mixLabel: 'Share of marketplace sales, Q2', trendLabel: 'Gross merchandise sales',
    src: 'https://investors.etsy.com/_assets/_fea57334fe81a735b34cf3bf4bdcb553/etsy/db/938/10062/earnings_release/Exhibit+99.1+12.31.2025.pdf',
    mix: [['Home and Living', 33], ['Jewelry and Accessories', 19], ['Apparel', 13], ['Craft Supplies', 9], ['Paper and Party Supplies', 8], ['Toys and Games', 4], ['Other', 14]],
    trend: [['FY24', 12587], ['FY25', 11917]],
    kpis: [['Gross merchandise sales', '$11.9M', '-5.3% vs last year', 0, 'sales'], ['Revenue', '$2.88M', '+2.7% vs last year', 1, 'accounting'], ['Take rate', '24.2%', '+190 bps', 1, 'reports'], ['Q4 revenue', '$0.88M', '+3.5% vs last year', 1, 'reports']],
    fin: [['Gross merchandise sales', 11916.9, 12587], ['Revenue', 2883.5, 2808.3], ['Marketplace revenue', 2007.2, 2020.7], ['Services revenue', 876.3, 787.6], ['Gross profit', 2065.7, 2033.8]],
    hl: [['Active buyers', 'Down 3.4% to 86.5 million, with the decline easing.'], ['Take rate', 'Reached 24.5% in Q4, driven by on-site ads.'], ['Reverb sale', 'Reverb was sold in June 2025, so prior-year comparisons shift.']]
  }
};
