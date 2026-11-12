/* Nastaliq mark as a 3D object: three solid cards crossing on the three axes.
   Drag to turn it any way; pinch or Ctrl + scroll to zoom. Needs three.js r149 (vendor/three.min.js). */
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
  scene.add(new T.AmbientLight(0xffffff, 0.7));
  var key = new T.DirectionalLight(0xffffff, 1); key.position.set(3, 5, 6); scene.add(key);
  var fill = new T.DirectionalLight(0xfff0c8, 0.4); fill.position.set(-5, -3, -4); scene.add(fill);

  /* three solid cards, one per axis, all the same pale yellow */
  var L = 2.4, W = 1.2, TH = 0.12;
  var geo = new T.BoxGeometry(L, W, TH);
  var edges = new T.EdgesGeometry(geo);
  var mat = new T.MeshStandardMaterial({ color: new T.Color(0xFFE9A8).convertSRGBToLinear(), roughness: 0.55, metalness: 0.05 });
  var line = new T.LineBasicMaterial({ color: 0x000000 });
  var rig = new T.Group(); scene.add(rig);
  [new T.Matrix4(),
   new T.Matrix4().set(0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1),
   new T.Matrix4().set(0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1)].forEach(function (r) {
    var m = new T.Mesh(geo, mat);
    m.quaternion.setFromRotationMatrix(r);
    m.add(new T.LineSegments(edges, line));
    rig.add(m);
  });

  /* looking down the diagonal, like the logo */
  var HOME = new T.Quaternion().setFromUnitVectors(new T.Vector3(1, 1, 1).normalize(), new T.Vector3(0, 0, 1));
  var up = new T.Vector3(0, 1, 0).applyQuaternion(HOME);
  HOME.premultiply(new T.Quaternion().setFromAxisAngle(new T.Vector3(0, 0, 1), Math.atan2(up.x, up.y)));
  rig.quaternion.copy(HOME);
  var BASE = 7, zoom = 1, dist = BASE;
  function size() {
    var w = Math.max(1, stage.clientWidth), h = Math.max(1, stage.clientHeight);
    renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix();
  }
  size();
  if (window.ResizeObserver) new ResizeObserver(size).observe(stage); else window.addEventListener('resize', size);

  var dragging = false, lastX = 0, lastY = 0, idleAt = 0, homing = false;
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  function turn(dx, dy) { rig.quaternion.premultiply(new T.Quaternion().setFromEuler(new T.Euler(dy, dx, 0))).normalize(); }
  canvas.addEventListener('pointerdown', function (ev) {
    if (ev.button > 0) return;
    canvas.setPointerCapture(ev.pointerId); dragging = true; homing = false; lastX = ev.clientX; lastY = ev.clientY; canvas.style.cursor = 'grabbing';
  });
  canvas.addEventListener('pointermove', function (ev) {
    if (!dragging) return;
    turn((ev.clientX - lastX) * 0.008, (ev.clientY - lastY) * 0.008); lastX = ev.clientX; lastY = ev.clientY;
  });
  function end() { dragging = false; canvas.style.cursor = 'grab'; idleAt = performance.now() + 2500; }
  canvas.addEventListener('pointerup', end); canvas.addEventListener('pointercancel', end);
  canvas.addEventListener('wheel', function (ev) {
    if (!ev.ctrlKey) return;
    ev.preventDefault(); zoom = Math.max(0.6, Math.min(1.8, zoom * Math.exp(ev.deltaY * 0.002)));
  }, { passive: false });
  function zoomBy(f) { zoom = Math.max(0.6, Math.min(1.8, zoom * f)); }
  function reset() { zoom = 1; homing = true; }
  var zin = document.getElementById('cube-in'), zout = document.getElementById('cube-out'), rst = document.getElementById('cube-reset');
  if (zin) zin.addEventListener('click', function () { zoomBy(1 / 1.2); });
  if (zout) zout.addEventListener('click', function () { zoomBy(1.2); });
  if (rst) rst.addEventListener('click', reset);
  canvas.addEventListener('keydown', function (ev) {
    var k = ev.key, s = 0.12;
    if (k === 'ArrowLeft') turn(-s, 0); else if (k === 'ArrowRight') turn(s, 0); else if (k === 'ArrowUp') turn(0, -s); else if (k === 'ArrowDown') turn(0, s);
    else if (k === '+' || k === '=') zoomBy(1 / 1.2); else if (k === '-') zoomBy(1.2); else if (k === 'r' || k === 'R') reset(); else return;
    ev.preventDefault();
  });

  var visible = true, first = true, spin = new T.Quaternion().setFromAxisAngle(new T.Vector3(0, 1, 0), 0.004);
  if (window.IntersectionObserver) new IntersectionObserver(function (en) { visible = en[0].isIntersecting; }).observe(stage);
  function frame(now) {
    requestAnimationFrame(frame);
    if (!visible) return;
    if (homing) { rig.quaternion.slerp(HOME, 0.12); if (rig.quaternion.angleTo(HOME) < 0.002) homing = false; }
    else if (!dragging && !reduce && now > idleAt) rig.quaternion.premultiply(spin).normalize();
    var want = BASE * zoom * (camera.aspect < 1 ? 1 / Math.max(camera.aspect, 0.6) : 1);
    dist += (want - dist) * 0.1;
    camera.position.set(0, 0, dist);
    renderer.render(scene, camera);
    if (first) { first = false; stage.classList.remove('loading'); }
  }
  canvas.style.cursor = 'grab';
  requestAnimationFrame(frame);
})();
