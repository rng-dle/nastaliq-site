(function () {
  'use strict';
  var d = document, root = d.documentElement;
  function $(s, c) { return (c || d).querySelector(s); }
  function $$(s, c) { return [].slice.call((c || d).querySelectorAll(s)); }

  /* ---------- language: EN / FR, remembered ---------- */
  var L = 'en';
  try { L = localStorage.getItem('nq-lang') || ''; } catch (e) {}
  if (L !== 'en' && L !== 'fr') L = /^fr/i.test(navigator.language || '') ? 'fr' : 'en';
  var els = $$('[data-fr]');
  els.forEach(function (e) { e.setAttribute('data-en', e.innerHTML); });
  var titleEn = d.title, titleFr = root.getAttribute('data-title-fr') || d.title;
  function setLang(l) {
    els.forEach(function (e) { e.innerHTML = e.getAttribute(l === 'fr' ? 'data-fr' : 'data-en'); });
    root.lang = l; d.title = l === 'fr' ? titleFr : titleEn;
    $$('.lang button').forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.l === l)); });
    $$('[data-aria-fr]').forEach(function (e) {
      if (!e.hasAttribute('data-aria-en')) e.setAttribute('data-aria-en', e.getAttribute('aria-label') || '');
      e.setAttribute('aria-label', e.getAttribute(l === 'fr' ? 'data-aria-fr' : 'data-aria-en'));
    });
    try { localStorage.setItem('nq-lang', l); } catch (e) {}
    L = l;
  }
  $$('.lang button').forEach(function (b) { b.addEventListener('click', function () { setLang(b.dataset.l); }); });
  setLang(L);

  /* ---------- nav: mega panel and mobile menu ---------- */
  var nav = $('.gnav'), scrim = $('.scrim'), mb = $('.menu-btn'), pb = $('#nl-products');
  function megaOpen(on) {
    if (!nav || !pb) return;
    nav.classList.toggle('mega-open', on); pb.setAttribute('aria-expanded', String(on));
    if (scrim) scrim.classList.toggle('on', on);
  }
  function menuOpen(on) {
    if (!nav) return;
    nav.classList.toggle('open', on); if (mb) mb.setAttribute('aria-expanded', String(on));
    root.style.overflow = on ? 'hidden' : '';
  }
  var narrow = function () { return window.matchMedia('(max-width: 860px)').matches; };
  if (pb) {
    pb.addEventListener('click', function (e) {
      e.stopPropagation(); if (narrow()) return;
      var hov = matchMedia('(hover:hover)').matches;
      megaOpen(hov ? true : pb.getAttribute('aria-expanded') !== 'true');
    });
    var hoverT;
    var host = pb;
    var panel = $('.mega');
    [host, panel].forEach(function (n) {
      if (!n) return;
      n.addEventListener('mouseenter', function () { if (!narrow() && matchMedia('(hover:hover)').matches) { clearTimeout(hoverT); megaOpen(true); } });
      n.addEventListener('mouseleave', function () { if (!narrow()) { hoverT = setTimeout(function () { megaOpen(false); }, 140); } });
    });
  }
  if (mb) mb.addEventListener('click', function () { menuOpen(!nav.classList.contains('open')); });
  if (scrim) scrim.addEventListener('click', function () { megaOpen(false); });
  d.addEventListener('keydown', function (e) { if (e.key === 'Escape') { megaOpen(false); menuOpen(false); } });
  d.addEventListener('click', function (e) { if (nav && !nav.contains(e.target)) megaOpen(false); });
  $$('.nav-links a').forEach(function (a) { a.addEventListener('click', function () { megaOpen(false); menuOpen(false); }); });
  window.addEventListener('resize', function () { if (!narrow()) menuOpen(false); });

  /* ---------- reveal on scroll ---------- */
  var rv = $$('.rv');
  if ('IntersectionObserver' in window && rv.length) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
    rv.forEach(function (n) { io.observe(n); });
    setTimeout(function () { rv.forEach(function (n) { n.classList.add('in'); }); }, 4000);   // never leave content hidden
  } else rv.forEach(function (n) { n.classList.add('in'); });

  /* ---------- products: highlight the category being read ---------- */
  var cats = $$('.cats a'), secs = cats.map(function (a) { return $(a.getAttribute('href')); }).filter(Boolean);
  if (cats.length && 'IntersectionObserver' in window) {
    var co = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting) cats.forEach(function (a) { a.classList.toggle('on', a.getAttribute('href') === '#' + e.target.id); });
      });
    }, { rootMargin: '-30% 0px -60% 0px' });
    secs.forEach(function (s) { co.observe(s); });
  }

  /* ---------- contact: copy address ---------- */
  var cb = $('#copy'), mail = $('#mail');
  if (cb && mail) cb.addEventListener('click', function () {
    function sel() { var r = d.createRange(); r.selectNodeContents(mail); var s = getSelection(); s.removeAllRanges(); s.addRange(r); }
    function ok() { cb.innerHTML = L === 'fr' ? 'Copié' : 'Copied'; setTimeout(function () { cb.innerHTML = cb.getAttribute(L === 'fr' ? 'data-fr' : 'data-en'); }, 1800); }
    try { navigator.clipboard.writeText(mail.textContent.trim()).then(ok, sel); } catch (e) { sel(); }
  });

  var y = $('#yr'); if (y) y.textContent = new Date().getFullYear();
})();
