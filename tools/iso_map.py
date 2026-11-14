"""Isometric module map for the home hero (replaces the old three.js mark).
build_site.py calls block() and injects it where tools/home.tpl.html has <!--ISO-->.
Pure SVG + HTML buttons: no WebGL, no library. Colours live in css/home.css, behaviour in js/iso.js."""
import html

VW, VH = 1000, 790
C = (500, 395)              # centre of the core
A, B, T = 120, 60, 14       # tile half-width, half-height, thickness
MODS = [  # key, label, caption, cx, cy  (clockwise from the top)
    ('inventory', 'Inventory', 'Live stock by location. Receive, transfer and count with barcode scanning on a phone.', 500, 180),
    ('purchasing', 'Purchasing', 'Purchase orders and supplier bills, tied to the stock they bring in.', 790, 288),
    ('sales', 'Sales', 'Quotes, orders and invoices that draw stock down as you sell.', 790, 502),
    ('accounting', 'Accounting', 'Receivables, payables and statements, updated as every sale and purchase is posted.', 500, 610),
    ('reports', 'Reports & Digest', 'Owner metrics, drill-downs and a morning email digest of what needs attention.', 210, 502),
    ('server', 'Dedicated Server', 'Your own server, never shared with another client. We host it and support it.', 210, 288),
]
MARK = ('<path class="m1" d="M-1.65 -1.14L0.08 -2.14L0.08 -0.05L1.65 0.86L1.65 -1.95L-1.65 -3.86ZM1.65 3.86L1.65 2.14L0.87 2.59L0.00 2.09L-0.71 2.50Z"/>'
        '<path class="m2" d="M1.03 -2.50L1.81 -2.05L1.81 -1.05L2.52 -0.64L2.52 -3.36ZM-0.08 -1.86L-2.52 -0.45L-2.52 3.36L-0.16 2.00L-1.89 1.00L-0.08 -0.05Z"/>'
        '<path class="m3" d="M1.81 -0.86L1.81 1.14L0.00 0.09L-1.57 1.00L0.87 2.41L2.56 1.43L4.17 0.50ZM-2.56 -1.43L-4.17 -0.50L-2.68 0.36L-2.68 -0.55L-1.81 -1.05L-1.81 -1.86Z"/>')


def pts(p): return ' '.join('%g,%g' % q for q in p)
def poly(p, c): return '<polygon class="%s" points="%s"/>' % (c, pts(p))
def rhomb(x, y, a, b): return [(x, y - b), (x + a, y), (x, y + b), (x - a, y)]


def box(x, y, s, h):
    """Iso box, base centre (x,y), footprint half-width s, height h."""
    return (poly([(x - s, y - h), (x, y - h + s / 2), (x, y + s / 2), (x - s, y)], 'l') +
            poly([(x, y - h + s / 2), (x + s, y - h), (x + s, y), (x, y + s / 2)], 'r') +
            poly([(x, y - h - s / 2), (x + s, y - h), (x, y - h + s / 2), (x - s, y - h)], 't'))


def coin(x, y, r, n, h=8):
    o = ''
    for i in range(n):
        yy = y - i * h
        o += ('<path class="l" d="M%g,%g V%g A%g,%g 0 0 0 %g,%g V%g Z"/>' % (x - r, yy - h, yy, r, r / 2, x + r, yy, yy - h) +
              '<ellipse class="t" cx="%g" cy="%g" rx="%g" ry="%g"/>' % (x, yy - h, r, r / 2))
    return o


def card(bx, by, w, h, face='L', rows=(), bars=(), line=None):
    """Standing card, bottom-middle (bx,by). face L slopes down-right, R slopes up-right."""
    k = 0.5 if face == 'L' else -0.5
    x0, y0 = bx - w / 2, by - k * w / 2
    P = lambda u, v: (x0 + u * w, y0 + k * u * w - v * h)
    dx = 6 if face == 'L' else -6
    back = [(px + dx, py - 3) for px, py in (P(0, 0), P(1, 0), P(1, 1), P(0, 1))]
    o = poly(back, 'r') + poly([P(0, 0), P(1, 0), P(1, 1), P(0, 1)], 't')
    for v in rows:
        o += '<path class="k" d="M%g,%g L%g,%g"/>' % (*P(.14, v), *P(.86, v))
    for u0, u1, vh in bars:
        o += poly([P(u0, .14), P(u1, .14), P(u1, .14 + vh), P(u0, .14 + vh)], 'kb')
    if line:
        o += '<path class="k" d="M%s"/>' % ' L'.join('%g,%g' % P(u, v) for u, v in line)
    return o


def icon(key, cx, cy):
    if key == 'inventory':
        return box(cx, cy - 14, 24, 24) + box(cx, cy - 38, 22, 20) + box(cx - 34, cy + 8, 24, 24) + box(cx + 34, cy + 8, 24, 24)
    if key == 'purchasing':
        return card(cx - 14, cy + 10, 64, 82, 'L', rows=(.72, .56, .40)) + box(cx + 40, cy + 18, 20, 24)
    if key == 'sales':
        return coin(cx - 30, cy + 8, 26, 4) + coin(cx + 30, cy + 20, 26, 2) + coin(cx + 6, cy + 36, 24, 3)
    if key == 'accounting':
        return (card(cx - 22, cy + 6, 70, 92, 'L', rows=(.78, .64, .50, .36, .22)) +
                card(cx + 32, cy + 36, 56, 54, 'R', bars=((.14, .30, .28), (.38, .54, .46), (.62, .78, .64))))
    if key == 'reports':
        return (box(cx, cy + 24, 40, 6) +
                card(cx, cy + 14, 100, 78, 'L', bars=((.12, .26, .26), (.34, .48, .42), (.56, .70, .56)), line=((.1, .62), (.4, .78), (.62, .70), (.9, .92))))
    if key == 'server':
        o = ''
        for i, y in enumerate((cy + 16, cy - 6, cy - 28)):
            o += box(cx, y, 52, 18)
            for j in range(3):  # LEDs on the left face
                u = .12 + j * .09
                o += '<circle class="led" cx="%g" cy="%g" r="2.2"/>' % (cx - 52 + u * 52, y + u * 26 - 9)
        return o
    raise KeyError(key)


def block():
    s = '<svg class="iso" viewBox="0 0 %d %d" aria-hidden="true" focusable="false">' % (VW, VH)
    s += '<defs><radialGradient id="iso-glow"><stop offset="0" stop-color="#ffc23a" stop-opacity=".55"/><stop offset="1" stop-color="#ffc23a" stop-opacity="0"/></radialGradient></defs>'
    s += poly(rhomb(C[0], C[1] + 28, 500, 290), 'pl2') + poly(rhomb(C[0], C[1] + 14, 500, 290), 'pl2') + poly(rhomb(C[0], C[1], 500, 290), 'pl')
    for i, (key, _l, _c, cx, cy) in enumerate(MODS):
        s += '<line class="cn%s" data-i="%d" x1="%d" y1="%d" x2="%d" y2="%d"/>' % (' on' if i == 0 else '', i, C[0], C[1], cx, cy)
    for i, (key, _l, _c, cx, cy) in sorted(enumerate(MODS), key=lambda m: m[1][4]):
        top = rhomb(cx, cy, A, B)
        s += '<g class="mod%s" data-i="%d">' % (' on' if i == 0 else '', i)
        s += poly([(cx - A, cy), (cx, cy + B), (cx, cy + B + T), (cx - A, cy + T)], 'tl') + poly([(cx, cy + B), (cx + A, cy), (cx + A, cy + T), (cx, cy + B + T)], 'tr') + poly(top, 'tt')
        s += icon(key, cx, cy) + '</g>'
    # core: pedestal, glow and the Nastaliq mark
    s += '<ellipse cx="500" cy="410" rx="98" ry="34" class="ped2"/><ellipse cx="500" cy="402" rx="80" ry="27" class="ped"/>'
    s += '<ellipse cx="500" cy="345" rx="150" ry="110" fill="url(#iso-glow)" class="glow"/>'
    s += '<g class="core"><g transform="translate(500 336) scale(14.5)">%s</g></g></svg>' % MARK
    btns = ''
    for i, (key, label, cap, cx, cy) in enumerate(MODS):
        btns += ('<button type="button" class="iso-lb" data-i="%d" aria-pressed="%s" data-t="%s" data-d="%s" style="left:%.2f%%;top:%.2f%%">%s</button>'
                 % (i, 'true' if i == 0 else 'false', html.escape(label, True), html.escape(cap, True), cx / VW * 100, (cy - B - T - 74 if i == 0 else cy + B + T + 20) / VH * 100, html.escape(label)))
    k0 = MODS[0]
    return ('<div id="iso-stage" role="group" aria-label="The Nastaliq modules around one core"><div class="iso-wrap">%s%s</div>'
            '<div class="iso-cap"><b id="iso-t">%s</b><span id="iso-d">%s</span></div></div>') % (s, btns, html.escape(k0[1]), html.escape(k0[2]))
