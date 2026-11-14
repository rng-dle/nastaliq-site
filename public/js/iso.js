/* Hero module map: one module lit at a time. Cycles on its own until the visitor touches it. */
(function () {
  'use strict';
  var st = document.getElementById('iso-stage');
  if (!st) return;
  var mods = st.querySelectorAll('.mod'), lines = st.querySelectorAll('.cn'), btns = st.querySelectorAll('.iso-lb');
  var title = document.getElementById('iso-t'), desc = document.getElementById('iso-d');
  var n = btns.length, cur = 0, hold = false, done = false;
  function on(list, i) { for (var k = 0; k < list.length; k++) list[k].classList.toggle('on', +list[k].dataset.i === i); }
  function show(i) {
    cur = i; on(mods, i); on(lines, i);
    for (var k = 0; k < n; k++) btns[k].setAttribute('aria-pressed', +btns[k].dataset.i === i);
    title.textContent = btns[i].dataset.t; desc.textContent = btns[i].dataset.d;
  }
  function pick(i, stop) { if (stop) done = true; show(i); }
  for (var k = 0; k < n; k++) {
    btns[k].addEventListener('click', function () { pick(+this.dataset.i, true); });
    btns[k].addEventListener('mouseenter', function () { pick(+this.dataset.i, false); });
  }
  for (k = 0; k < mods.length; k++) mods[k].addEventListener('click', function () { pick(+this.dataset.i, true); });
  st.addEventListener('mouseenter', function () { hold = true; });
  st.addEventListener('mouseleave', function () { hold = false; });
  st.addEventListener('focusin', function () { hold = true; });
  st.addEventListener('focusout', function () { hold = false; });
  if (window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  setInterval(function () { if (!hold && !done && !document.hidden) show((cur + 1) % n); }, 4200);
})();
