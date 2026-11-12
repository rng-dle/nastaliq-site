/* Nastaliq mark in 3D: the three interlocking planes of the logo, extruded and lit like a polished object.
   Drag to turn it any way, right-drag or shift-drag (two fingers on touch) to move it,
   pinch or Ctrl + scroll to zoom. Needs three.js r149 (vendor/three.min.js). */
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
  try {
    renderer = new T.WebGLRenderer({ canvas: canvas, antialias: true, alpha: false, powerPreference: 'high-performance' });
  } catch (e) { fail(); return; }
  var BG = 0x0a0a0b;
  renderer.setClearColor(BG, 1);          // transmission samples the clear colour
  renderer.outputEncoding = T.sRGBEncoding;
  renderer.toneMapping = T.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.15;
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

  var scene = new T.Scene();
  scene.background = new T.Color(BG);
  var camera = new T.PerspectiveCamera(28, 1, 0.1, 100);
  var TARGET = new T.Vector3(0, 1.45, 0);

  /* ---------- studio lighting baked into an environment map ---------- */
  function panel(root, w, h, x, y, z, k, col) {
    var c = new T.Color(col || 0xffffff).multiplyScalar(k);
    var m = new T.Mesh(new T.PlaneGeometry(w, h), new T.MeshBasicMaterial({ color: c, side: T.DoubleSide }));
    m.position.set(x, y, z); m.lookAt(0, 0, 0); root.add(m);
  }
  var envScene = new T.Scene();
  envScene.add(new T.Mesh(new T.SphereGeometry(60, 32, 16), new T.MeshBasicMaterial({ color: 0x15161a, side: T.BackSide })));
  panel(envScene, 34, 14, 0, 28, 6, 3.2);                 // overhead softbox
  panel(envScene, 5, 30, -24, 6, 7, 5);                 // left strip
  panel(envScene, 5, 30, 24, 5, 5, 3.5);                  // right strip
  panel(envScene, 28, 5, 0, 7, -28, 5, 0xffe2a8);       // warm rim behind
  panel(envScene, 22, 4, 0, -10, 22, 1.4);              // low front fill
  panel(envScene, 8, 8, 14, 12, 20, 2.4, 0xfff1d0);       // key accent
  var pmrem = new T.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(envScene, 0.02).texture;
  pmrem.dispose();

  /* ---------- materials: one per plane of the mark ---------- */
  function amber(hex) {
    return new T.MeshPhysicalMaterial({ color: hex, metalness: 0.45, roughness: 0.3, clearcoat: 1, clearcoatRoughness: 0.08, envMapIntensity: 1.1 });
  }
  var PLANES = [   // [colour, z layer, path from the logo]
    [0xD9800B, -1, 'M1.03 -2.50L1.81 -2.05L1.81 -1.05L2.52 -0.64L2.52 -3.36ZM-0.08 -1.86L-2.52 -0.45L-2.52 3.36L-0.16 2.00L-1.89 1.00L-0.08 -0.05Z'],
    [0xF3A21C,  0, 'M-1.65 -1.14L0.08 -2.14L0.08 -0.05L1.65 0.86L1.65 -1.95L-1.65 -3.86ZM1.65 3.86L1.65 2.14L0.87 2.59L0.00 2.09L-0.71 2.50Z'],
    [0xFFC23A,  1, 'M1.81 -0.86L1.81 1.14L0.00 0.09L-1.57 1.00L0.87 2.41L2.56 1.43L4.17 0.50ZM-2.56 -1.43L-4.17 -0.50L-2.68 0.36L-2.68 -0.55L-1.81 -1.05L-1.81 -1.86Z']
  ];

  /* ---------- geometry: logo polygons pulled out into solid shapes ---------- */
  var K = 0.44, DEPTH = 0.3, LIFT = 1.8;
  var rig = new T.Group(); scene.add(rig);
  var cube = new T.Group();                         // the mark; named cube in the controls below
  PLANES.forEach(function (pl) {
    var mat = amber(pl[0]);
    pl[2].split('Z').forEach(function (sub) {
      var pts = [], re = /(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)/g, m;
      while ((m = re.exec(sub))) pts.push(new T.Vector2(parseFloat(m[1]) * K, -parseFloat(m[2]) * K));
      if (pts.length < 3) return;
      var geo = new T.ExtrudeGeometry(new T.Shape(pts), {
        depth: DEPTH, bevelEnabled: true, bevelThickness: 0.035, bevelSize: 0.03, bevelSegments: 4, curveSegments: 1
      });
      geo.translate(0, 0, pl[1] * DEPTH - DEPTH / 2);
      cube.add(new T.Mesh(geo, mat));
    });
  });
  rig.add(cube);

  /* studio backdrop and floor: opaque, so the glass has something to refract */
  var bc = document.createElement('canvas'); bc.width = 4; bc.height = 256;
  var bx = bc.getContext('2d'), bgr = bx.createLinearGradient(0, 0, 0, 256);
  bgr.addColorStop(0, '#202024'); bgr.addColorStop(0.48, '#2e2a24'); bgr.addColorStop(0.56, '#17161a'); bgr.addColorStop(1, '#09090a');
  bx.fillStyle = bgr; bx.fillRect(0, 0, 4, 256);
  var bgTex = new T.CanvasTexture(bc); bgTex.encoding = T.sRGBEncoding;
  var dome = new T.Mesh(new T.SphereGeometry(40, 32, 24), new T.MeshBasicMaterial({ map: bgTex, side: T.BackSide, toneMapped: false, depthWrite: false }));
  dome.position.y = 1.2; dome.renderOrder = -2; scene.add(dome);
  var floor = new T.Mesh(new T.CircleGeometry(40, 64), new T.MeshStandardMaterial({ color: 0x060607, roughness: 0.5, metalness: 0.3, envMapIntensity: 0.22 }));
  floor.rotation.x = -Math.PI / 2; floor.position.y = -0.215; scene.add(floor);

  /* soft contact shadow */
  var sh = document.createElement('canvas'); sh.width = sh.height = 128;
  var sg = sh.getContext('2d'), gr = sg.createRadialGradient(64, 64, 4, 64, 64, 64);
  gr.addColorStop(0, 'rgba(0,0,0,.75)'); gr.addColorStop(1, 'rgba(0,0,0,0)');
  sg.fillStyle = gr; sg.fillRect(0, 0, 128, 128);
  var shadow = new T.Mesh(new T.PlaneGeometry(5.2, 5.2), new T.MeshBasicMaterial({ map: new T.CanvasTexture(sh), transparent: true, opacity: 0.7, depthWrite: false }));
  shadow.rotation.x = -Math.PI / 2; shadow.position.y = -0.21; rig.add(shadow);

  /* ---------- resting pose: floating, turned a little toward the viewer ---------- */
  var q0 = new T.Quaternion().setFromEuler(new T.Euler(-0.16, 0.5, 0.03));
  var pos0 = new T.Vector3(0, LIFT, 0);
  cube.quaternion.copy(q0); cube.position.copy(pos0);

  /* ---------- view, sizing ---------- */
  var zoom = 1, zoomT = 1, rigT = new T.Vector3(), W = 1, H = 1;
  function size() {
    W = Math.max(1, stage.clientWidth); H = Math.max(1, stage.clientHeight);
    renderer.setSize(W, H, false);
    camera.aspect = W / H; camera.updateProjectionMatrix();
  }
  function placeCamera() {
    var halfTan = Math.tan(camera.fov * Math.PI / 360);
    var need = 4.8 / (2 * halfTan * camera.aspect);        // keep the base inside the frame width
    var need2 = 6.2 / (2 * halfTan);                       // and the whole cube inside the frame height
    var dist = Math.max(need, need2, 8.5) / zoom;
    camera.position.set(0, TARGET.y + dist * 0.16, dist);
    camera.lookAt(TARGET);
  }
  size(); placeCamera();
  if (window.ResizeObserver) new ResizeObserver(function () { size(); placeCamera(); }).observe(stage);
  else window.addEventListener('resize', function () { size(); placeCamera(); });

  /* ---------- interaction ---------- */
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var coarse = window.matchMedia && matchMedia('(pointer: coarse)').matches;
  if (coarse) stage.classList.add('coarse');
  var resting = true, lastTouch = 0, vel = new T.Vector2(), dragging = false;
  var ptrs = {}, nptr = 0, mode = null, pinch0 = 0, zoom0 = 1, cen0 = null;
  var AX = new T.Vector3(1, 0, 0), AY = new T.Vector3(0, 1, 0), tq = new T.Quaternion();
  var anim = null;

  function turn(dx, dy) {                       // world-space turn, any axis, no limits
    tq.setFromAxisAngle(AY, dx); cube.quaternion.premultiply(tq);
    tq.setFromAxisAngle(AX, dy); cube.quaternion.premultiply(tq);
    cube.quaternion.normalize();
  }
  function touched() { resting = false; anim = null; lastTouch = performance.now(); }
  function pts() { var a = []; for (var k in ptrs) a.push(ptrs[k]); return a; }

  canvas.addEventListener('contextmenu', function (e) { e.preventDefault(); });
  canvas.addEventListener('pointerdown', function (e) {
    try { canvas.setPointerCapture(e.pointerId); } catch (x) {}
    ptrs[e.pointerId] = { x: e.clientX, y: e.clientY }; nptr++;
    touched(); vel.set(0, 0);
    if (nptr === 1) { mode = (e.button === 2 || e.shiftKey || e.ctrlKey) ? 'pan' : 'rot'; dragging = true; }
    else if (nptr === 2) {
      var p = pts(); mode = 'pinch'; pinch0 = Math.hypot(p[0].x - p[1].x, p[0].y - p[1].y) || 1; zoom0 = zoomT;
      cen0 = { x: (p[0].x + p[1].x) / 2, y: (p[0].y + p[1].y) / 2 };
    }
  });
  canvas.addEventListener('pointermove', function (e) {
    var p = ptrs[e.pointerId]; if (!p) return;
    var dx = e.clientX - p.x, dy = e.clientY - p.y; p.x = e.clientX; p.y = e.clientY;
    if (mode === 'rot') {
      var k = 0.0085; turn(dx * k, dy * k); vel.set(dx * k, dy * k);
    } else if (mode === 'pan') {
      movePan(dx, dy);
    } else if (mode === 'pinch' && nptr >= 2) {
      var a = pts(), d = Math.hypot(a[0].x - a[1].x, a[0].y - a[1].y) || 1;
      zoomT = clamp(zoom0 * d / pinch0, 0.55, 2.2); zoom = zoomT; placeCamera();
      var c = { x: (a[0].x + a[1].x) / 2, y: (a[0].y + a[1].y) / 2 };
      movePan(c.x - cen0.x, c.y - cen0.y); cen0 = c;
    }
  });
  function end(e) {
    if (!ptrs[e.pointerId]) return;
    delete ptrs[e.pointerId]; nptr = Math.max(0, nptr - 1);
    try { canvas.releasePointerCapture(e.pointerId); } catch (x) {}
    if (nptr === 0) { dragging = false; mode = null; }
    else if (nptr === 1) { mode = 'rot'; vel.set(0, 0); }
    lastTouch = performance.now();
  }
  canvas.addEventListener('pointerup', end);
  canvas.addEventListener('pointercancel', end);
  canvas.addEventListener('lostpointercapture', end);
  canvas.addEventListener('wheel', function (e) {
    if (!(e.ctrlKey || e.metaKey)) return;       // plain scroll still scrolls the page
    e.preventDefault(); zoomT = clamp(zoomT * Math.exp(-e.deltaY * 0.0022), 0.55, 2.2);
  }, { passive: false });
  canvas.addEventListener('dblclick', reset);
  function movePan(dx, dy) {
    var u = (2 * camera.position.distanceTo(TARGET) * Math.tan(camera.fov * Math.PI / 360)) / H;
    rigT.x = clamp(rigT.x + dx * u, -3.2, 3.2); rigT.y = clamp(rigT.y - dy * u, -2.2, 2.2);
  }
  function clamp(v, a, b) { return Math.min(b, Math.max(a, v)); }

  function reset() {
    anim = { t: 0, q: cube.quaternion.clone(), p: cube.position.clone(), r: rig.position.clone(), z: zoomT };
    vel.set(0, 0);
  }
  var bReset = document.getElementById('cube-reset'), bIn = document.getElementById('cube-in'),
      bOut = document.getElementById('cube-out'), bTurn = document.getElementById('cube-turn');
  if (bReset) bReset.addEventListener('click', reset);
  if (bIn) bIn.addEventListener('click', function () { zoomT = clamp(zoomT * 1.18, 0.55, 2.2); });
  if (bOut) bOut.addEventListener('click', function () { zoomT = clamp(zoomT / 1.18, 0.55, 2.2); });
  if (bTurn) bTurn.addEventListener('click', function () {
    var on = !stage.classList.contains('free'); stage.classList.toggle('free', on); bTurn.setAttribute('aria-pressed', String(on));
  });
  canvas.addEventListener('keydown', function (e) {
    var k = 0.12, used = true;
    if (e.key === 'ArrowLeft') turn(-k, 0); else if (e.key === 'ArrowRight') turn(k, 0);
    else if (e.key === 'ArrowUp') turn(0, -k); else if (e.key === 'ArrowDown') turn(0, k);
    else if (e.key === '+' || e.key === '=') zoomT = clamp(zoomT * 1.12, 0.55, 2.2);
    else if (e.key === '-') zoomT = clamp(zoomT / 1.12, 0.55, 2.2);
    else if (e.key === 'r' || e.key === 'R' || e.key === '0') reset();
    else used = false;
    if (used) { e.preventDefault(); touched(); }
  });

  /* ---------- loop ---------- */
  var visible = true, last = performance.now(), raf = 0, first = true;
  if (window.IntersectionObserver) new IntersectionObserver(function (es) {
    visible = es[0].isIntersecting; if (visible && !raf) { last = performance.now(); raf = requestAnimationFrame(frame); }
  }, { rootMargin: '120px' }).observe(stage);
  function ease(t) { return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }
  var q1 = new T.Quaternion(), pv = new T.Vector3(), swayT = 0;

  function frame(now) {
    raf = 0;
    if (!visible) return;
    var dt = Math.min(0.05, (now - last) / 1000); last = now;

    if (anim) {                                  // glide back to the corner pose
      anim.t = Math.min(1, anim.t + dt / 0.95); var e = ease(anim.t);
      cube.quaternion.copy(anim.q).slerp(q0, e); cube.position.copy(anim.p).lerp(pos0, e);
      rig.position.copy(anim.r).lerp(pv.set(0, 0, 0), e); rigT.copy(rig.position);
      zoomT = anim.z + (1 - anim.z) * e;
      if (anim.t >= 1) { anim = null; resting = true; swayT = 0; }
    } else {
      if (!dragging && (Math.abs(vel.x) > 0.0002 || Math.abs(vel.y) > 0.0002)) {   // momentum
        turn(vel.x, vel.y); var f = Math.pow(0.0035, dt); vel.multiplyScalar(f);
      }
      if (resting && !dragging && !reduce) {      // gentle sway and float, always facing the viewer
        swayT += dt;
        q1.setFromAxisAngle(AY, Math.sin(swayT * 0.6) * 0.62); cube.quaternion.copy(q1).multiply(q0);
        cube.position.set(0, LIFT + Math.sin(swayT * 0.9) * 0.07, 0);
      } else if (!resting && !dragging && now - lastTouch > 9000 && !reduce && Math.abs(vel.x) + Math.abs(vel.y) < 0.0002) {
        reset();                                  // let go for nine seconds: drift home
      }
      rig.position.x += (rigT.x - rig.position.x) * Math.min(1, dt * 10);
      rig.position.y += (rigT.y - rig.position.y) * Math.min(1, dt * 10);
    }
    if (Math.abs(zoom - zoomT) > 0.0005) { zoom += (zoomT - zoom) * Math.min(1, dt * 10); placeCamera(); }

    renderer.render(scene, camera);
    if (first) { first = false; stage.classList.remove('loading'); }
    raf = requestAnimationFrame(frame);
  }
  raf = requestAnimationFrame(frame);

  canvas.addEventListener('webglcontextlost', function (e) { e.preventDefault(); fail(); });
})();
