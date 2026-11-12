/* Nastaliq mark as a real 3D object: three interlocking cards, one per axis.
   Drag the background to turn it any way; drag a card to pull it out along its own axis.
   Needs three.js r149 (vendor/three.min.js). */
(function () {
  'use strict';
  var stage = document.getElementById('cube-stage');
  if (!stage) return;
  var canvas = document.getElementById('cube-canvas');
  function fail() { stage.classList.remove('loading'); stage.classList.add('nogl'); }
  if (!window.THREE || !canvas) { fail(); return; }
  var T = THREE;
  stage.classList.add('loading');

  var renderer;
  try { renderer = new T.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true }); } catch (e) { fail(); return; }
  renderer.outputEncoding = T.sRGBEncoding;
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

  var scene = new T.Scene();
  var camera = new T.PerspectiveCamera(30, 1, 0.1, 100);
  scene.add(new T.AmbientLight(0xffffff, 0.75));
  var key = new T.DirectionalLight(0xffffff, 0.9); key.position.set(3, 5, 6); scene.add(key);
  var fill = new T.DirectionalLight(0xffe2b0, 0.35); fill.position.set(-5, -3, -4); scene.add(fill);

  /* ---------- the three cards ----------
     Each card is a plate with a slot open at its back end. Card k+1 sits in the slot of card k, so the
     set interlocks, and each card slides out along its own long axis (its +x) without touching the others. */
  var L = 2.2, W = 1.1, TH = 0.12, CL = 0.02;            // length, width, thickness, clearance
  var s = TH / 2 + CL, e = W / 2 + CL;
  var outline = [[-L / 2, -W / 2], [L / 2, -W / 2], [L / 2, W / 2], [-L / 2, W / 2], [-L / 2, s], [e, s], [e, -s], [-L / 2, -s]];
  var shape = new T.Shape(outline.map(function (p) { return new T.Vector2(p[0], p[1]); }));
  var cardGeo = new T.ExtrudeGeometry(shape, { depth: TH, bevelEnabled: false });
  cardGeo.translate(0, 0, -TH / 2);
  var edgeGeo = new T.EdgesGeometry(cardGeo, 20);

  var rig = new T.Group(); scene.add(rig);
  var cardDefs = [   // colour as in the logo; rotation maps the local frame onto world axes
    { color: 0xF3A21C, rot: new T.Matrix4(), axis: new T.Vector3(1, 0, 0) },
    { color: 0xD9800B, rot: new T.Matrix4().set(0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1), axis: new T.Vector3(0, 1, 0) },
    { color: 0xFFC23A, rot: new T.Matrix4().set(0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1), axis: new T.Vector3(0, 0, 1) }
  ];
  var cards = cardDefs.map(function (d) {
    var mat = new T.MeshStandardMaterial({ color: new T.Color(d.color).convertSRGBToLinear(), roughness: 0.5, metalness: 0.1 });
    var m = new T.Mesh(cardGeo, mat);
    m.quaternion.setFromRotationMatrix(d.rot);
    m.add(new T.LineSegments(edgeGeo, new T.LineBasicMaterial({ color: 0x000000 })));
    m.userData = { axis: d.axis, off: 0, tgt: 0 };
    rig.add(m);
    return m;
  });
  var PULL = 1.9;

  /* ---------- pose, view ---------- */
  var HOME = new T.Quaternion().setFromUnitVectors(new T.Vector3(1, 1, 1).normalize(), new T.Vector3(0, 0, 1));
  var up = new T.Vector3(0, 1, 0).applyQuaternion(HOME);           // roll so the model's up edge points up the screen
  var roll = Math.atan2(up.x, up.y);
  HOME.premultiply(new T.Quaternion().setFromAxisAngle(new T.Vector3(0, 0, 1), roll));
  rig.quaternion.copy(HOME);
  var BASE = 7.2, zoom = 1, dist = BASE, W_PX = 1, H_PX = 1;
  function size() {
    W_PX = Math.max(1, stage.clientWidth); H_PX = Math.max(1, stage.clientHeight);
    renderer.setSize(W_PX, H_PX, false); camera.aspect = W_PX / H_PX; camera.updateProjectionMatrix();
  }
  size();
  if (window.ResizeObserver) new ResizeObserver(size).observe(stage); else window.addEventListener('resize', size);

  /* ---------- interaction ---------- */
  var ray = new T.Raycaster(), ndc = new T.Vector2();
  var mode = null, active = null, lastX = 0, lastY = 0, pxPerUnit = 1, dirX = 1, dirY = 0, idleAt = 0;
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  function pick(ev) {
    var r = canvas.getBoundingClientRect();
    ndc.set(((ev.clientX - r.left) / r.width) * 2 - 1, -((ev.clientY - r.top) / r.height) * 2 + 1);
    ray.setFromCamera(ndc, camera);
    var hit = ray.intersectObjects(cards, false)[0];
    return hit ? hit.object : null;
  }
  function screenAxis(card) {      // where the card's pull axis points on screen
    var a = card.userData.axis.clone().transformDirection(rig.matrixWorld);
    var p0 = card.getWorldPosition(new T.Vector3()), p1 = p0.clone().add(a);
    p0.project(camera); p1.project(camera);
    var dx = (p1.x - p0.x) * W_PX / 2, dy = -(p1.y - p0.y) * H_PX / 2, len = Math.hypot(dx, dy) || 1;
    dirX = dx / len; dirY = dy / len; pxPerUnit = Math.max(len, 8);
  }
  canvas.addEventListener('pointerdown', function (ev) {
    if (ev.button > 0) return;
    canvas.setPointerCapture(ev.pointerId);
    lastX = ev.clientX; lastY = ev.clientY;
    active = pick(ev);
    mode = active ? 'pull' : 'turn';
    if (active) screenAxis(active);
    canvas.style.cursor = 'grabbing';
  });
  canvas.addEventListener('pointermove', function (ev) {
    if (!mode) { canvas.style.cursor = pick(ev) ? 'pointer' : 'grab'; return; }
    var dx = ev.clientX - lastX, dy = ev.clientY - lastY; lastX = ev.clientX; lastY = ev.clientY;
    if (mode === 'pull') {
      var u = active.userData;
      u.tgt = Math.max(0, Math.min(PULL, u.tgt + (dx * dirX + dy * dirY) / pxPerUnit));
      u.off = u.tgt;
    } else {
      var q = new T.Quaternion().setFromEuler(new T.Euler(dy * 0.008, dx * 0.008, 0, 'XYZ'));
      rig.quaternion.premultiply(q).normalize();
    }
  });
  function end() { mode = null; active = null; canvas.style.cursor = 'grab'; idleAt = performance.now() + 2500; }
  canvas.addEventListener('pointerup', end); canvas.addEventListener('pointercancel', end);
  canvas.addEventListener('wheel', function (ev) {
    if (!ev.ctrlKey) return;
    ev.preventDefault(); zoom = Math.max(0.6, Math.min(1.8, zoom * Math.exp(ev.deltaY * 0.002)));
  }, { passive: false });

  var pullBtn = document.getElementById('cube-pull'), zin = document.getElementById('cube-in'), zout = document.getElementById('cube-out'), rst = document.getElementById('cube-reset');
  function setAll(v) { cards.forEach(function (c) { c.userData.tgt = v; }); }
  function allOut() { return cards.every(function (c) { return c.userData.tgt > PULL * 0.5; }); }
  function sync() { if (pullBtn) pullBtn.setAttribute('aria-pressed', allOut()); }
  if (pullBtn) pullBtn.addEventListener('click', function () { setAll(allOut() ? 0 : PULL); sync(); });
  if (zin) zin.addEventListener('click', function () { zoom = Math.max(0.6, zoom / 1.2); });
  if (zout) zout.addEventListener('click', function () { zoom = Math.min(1.8, zoom * 1.2); });
  var homing = false;
  if (rst) rst.addEventListener('click', function () { setAll(0); zoom = 1; homing = true; sync(); });
  canvas.addEventListener('keydown', function (ev) {
    var k = ev.key, step = 0.12, q = null;
    if (k === 'ArrowLeft') q = new T.Euler(0, -step, 0); else if (k === 'ArrowRight') q = new T.Euler(0, step, 0);
    else if (k === 'ArrowUp') q = new T.Euler(-step, 0, 0); else if (k === 'ArrowDown') q = new T.Euler(step, 0, 0);
    else if (k === '+' || k === '=') zoom = Math.max(0.6, zoom / 1.2); else if (k === '-') zoom = Math.min(1.8, zoom * 1.2);
    else if (k === 'p' || k === 'P') { setAll(allOut() ? 0 : PULL); sync(); } else if (k === 'r' || k === 'R') { setAll(0); zoom = 1; homing = true; sync(); }
    else return;
    ev.preventDefault();
    if (q) rig.quaternion.premultiply(new T.Quaternion().setFromEuler(q)).normalize();
  });

  /* ---------- loop ---------- */
  var visible = true, first = true, spin = new T.Quaternion();
  if (window.IntersectionObserver) new IntersectionObserver(function (en) { visible = en[0].isIntersecting; }).observe(stage);
  function frame(now) {
    requestAnimationFrame(frame);
    if (!visible) return;
    var far = 0;
    cards.forEach(function (c) {
      var u = c.userData;
      if (mode !== 'pull' || c !== active) u.off += (u.tgt - u.off) * 0.14;
      c.position.copy(u.axis).multiplyScalar(u.off);
      far = Math.max(far, u.off);
    });
    if (homing) { rig.quaternion.slerp(HOME, 0.12); if (rig.quaternion.angleTo(HOME) < 0.002) homing = false; }
    else if (!mode && !reduce && now > idleAt) { spin.setFromAxisAngle(new T.Vector3(0, 1, 0), 0.004); rig.quaternion.premultiply(spin).normalize(); }
    var want = (BASE + far * 1.9) * zoom * (camera.aspect < 1 ? 1 / Math.max(camera.aspect, 0.6) : 1);
    dist += (want - dist) * 0.1;
    camera.position.set(0, 0, dist);
    renderer.render(scene, camera);
    if (first) { first = false; stage.classList.remove('loading'); }
  }
  canvas.style.cursor = 'grab';
  requestAnimationFrame(frame);
})();
