// Épisode 1 (3D) — mise en scène des 15 plans
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const lerp = (a, b, t) => a + (b - a) * t;
const eio = (t) => { t = clamp(t); return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };
const eout = (t) => 1 - Math.pow(1 - clamp(t), 3);
const tw = (t, t0, t1, a, b, e = eio) => lerp(a, b, e((t - t0) / (t1 - t0)));
const twv = (t, t0, t1, a, b, e = eio) => a.map((x, i) => tw(t, t0, t1, x, b[i], e));
function blink(t, seed = 0) { const per = 3.2 + (seed % 3) * 0.6; const p = (t + seed * 1.37) % per; return p < 0.13 ? Math.sin((p / 0.13) * Math.PI) : 0; }
const shake = (t, t0, d, a) => (t < t0 || t > t0 + d) ? [0, 0] : [Math.sin(t * 83) * a * (1 - (t - t0) / d), Math.cos(t * 71) * a * (1 - (t - t0) / d)];

export async function construire(THREE, M, init) {
  const { plans, env } = init;
  const wt = (p, txt, n = 0, w = 's') => { const m = p.words.filter((x) => x.w.toLowerCase().includes(txt.toLowerCase())); if (!m[n]) throw new Error('mot ' + txt + ' ' + p.id); return m[n][w]; };
  const vs = (p, id) => p.voices.find((v) => v.id === id).start;
  const ve = (p, id) => { const v = p.voices.find((x) => x.id === id); return v.start + v.dur; };
  const amp = (p, t, qui = 'lana') => { for (const v of p.voices) if (v.voix === qui && t >= v.start && t < v.start + v.dur) { const a = env[v.id]; return a[Math.min(a.length - 1, Math.floor((t - v.start) * 30))] || 0; } return 0; };
  const cam = new THREE.PerspectiveCamera(38, 720 / 1280, 0.05, 60);
  const cam2 = new THREE.PerspectiveCamera(38, 720 / 640, 0.05, 60);
  const look = (c, pos, tgt, fov = 38) => { c.position.set(...pos); c.lookAt(...tgt); c.fov = fov; c.updateProjectionMatrix(); };

  /* ---- lumières ---- */
  function lumieres(scene) {
    const L = {};
    L.hemi = new THREE.HemisphereLight(0xc9b8ff, 0x4a3326, 1.4); scene.add(L.hemi);
    L.key = new THREE.DirectionalLight(0xfff0dd, 2.2); L.key.position.set(2, 5, 4); L.key.castShadow = true;
    L.key.shadow.mapSize.set(2048, 2048); Object.assign(L.key.shadow.camera, { left: -5, right: 5, top: 5, bottom: -5, near: 0.5, far: 20 }); L.key.shadow.bias = -0.0006; L.key.shadow.normalBias = 0.02; L.key.shadow.radius = 4;
    scene.add(L.key); scene.add(L.key.target);
    L.rim = new THREE.DirectionalLight(0x7fa8ff, 1.2); L.rim.position.set(1, 3, -3); scene.add(L.rim);
    L.phone = new THREE.PointLight(0x8fd0ff, 0, 2.2, 1.5); scene.add(L.phone);
    return L;
  }
  const mode = (L, m) => {
    const cfg = {
      jour: [0xc9b8ff, 0x4a3326, 1.4, 0xfff0dd, 2.2, 1.2], nuit: [0x3a3f80, 0x140c1e, 0.55, 0x8fa2ff, 0.55, 1.4],
      matin: [0xffe2c4, 0x5a3a2a, 1.5, 0xffc98a, 2.8, 0.6], sombre: [0x4a3a70, 0x1a1020, 0.8, 0xffe0b0, 1.2, 1.0],
    }[m];
    L.hemi.color.set(cfg[0]); L.hemi.groundColor.set(cfg[1]); L.hemi.intensity = cfg[2]; L.key.color.set(cfg[3]); L.key.intensity = cfg[4]; L.rim.intensity = cfg[5];
  };

  /* ---- décors ---- */
  const sChambre = new THREE.Scene(); sChambre.background = new THREE.Color(0x1b1230);
  const room = M.chambre({}); sChambre.add(room.g); const Lc = lumieres(sChambre);
  const sJean = new THREE.Scene(); sJean.background = new THREE.Color(0x1b1230);
  const sCouloir = new THREE.Scene(); sCouloir.background = new THREE.Color(0x150d24);
  const cou = M.couloir(); sCouloir.add(cou.g); const Lp = lumieres(sCouloir);
  const sLycee = new THREE.Scene(); sLycee.background = new THREE.Color(0x120a24); sLycee.fog = new THREE.Fog(0x120a24, 6, 14);
  const ly = M.lycee(); sLycee.add(ly.g); const Ll = lumieres(sLycee);
  const spot = new THREE.SpotLight(0xfff0d0, 0, 12, 0.35, 0.6, 1); spot.position.set(0, 6, 1); spot.target.position.set(0, 0, 0); spot.castShadow = true; sLycee.add(spot); sLycee.add(spot.target);
  const sSdb = new THREE.Scene(); sSdb.background = new THREE.Color(0x3f8f8c);
  const sdb = M.salleDeBain(); sSdb.add(sdb.g); const Ls = lumieres(sSdb);

  /* ---- personnages et accessoires ---- */
  const lana = M.personnage();
  const ado = M.personnage({ glasses: false, bun: false, longHair: true, pimples: false, unicorn: false, stains: false, top: 0xffffff, sleeves: 0x4f7fc4, jacket: 0x4f7fc4, pants: 0x355e9e, shoes: 'basket', browThick: false });
  sLycee.add(ado.root);
  const livreur = M.personnage({ skin: 0xc68c5a, hair: 0x1a1a1a, shortHair: true, bun: false, glasses: false, pimples: false, unicorn: false, stains: false, top: 0xe23b3b, sleeves: 0xe23b3b, pants: 0x333344, shoes: 'basket', cap: 0xe23b3b, browThick: false });
  sCouloir.add(livreur.root);
  const pates = M.chat(); sChambre.add(pates.root);

  const ecranTex = (draw) => M.canvasTex(280, 540, (c, w, h) => { c.fillStyle = '#10162e'; c.fillRect(0, 0, w, h); draw(c, w, h); });
  const texNathan = ecranTex((c, w, h) => {
    c.fillStyle = '#f4dcae'; c.fillRect(30, 70, 220, 270); c.fillStyle = '#7fb3e6'; c.fillRect(45, 85, 190, 190);
    c.fillStyle = '#2b1a10'; c.beginPath(); c.arc(140, 165, 50, Math.PI, 0); c.fill(); c.fillStyle = '#f0c49a'; c.beginPath(); c.arc(140, 180, 42, 0, 7); c.fill();
    c.fillStyle = '#2d5fa8'; c.fillRect(85, 222, 110, 53); c.fillStyle = '#111'; c.beginPath(); c.arc(125, 178, 5, 0, 7); c.arc(155, 178, 5, 0, 7); c.fill();
    c.strokeStyle = '#111'; c.lineWidth = 4; c.beginPath(); c.arc(140, 192, 14, 0.2, Math.PI - 0.2); c.stroke();
    c.fillStyle = '#333'; c.font = '34px Anton'; c.textAlign = 'center'; c.fillText('NATHAN · 2016', 140, 320);
    c.fillStyle = '#ff4d6d'; c.font = '80px Anton'; c.fillText('♥', 140, 430);
  });
  const texMsg = ecranTex((c, w) => { c.fillStyle = '#fff'; c.fillRect(20, 150, 240, 150); c.fillStyle = '#ef5b93'; c.beginPath(); c.arc(55, 185, 22, 0, 7); c.fill(); c.fillStyle = '#111'; c.font = '30px Anton'; c.fillText('INÈS', 90, 196); c.fillStyle = '#444'; c.font = '22px Anton'; c.fillText('Coucou ma belle !!', 35, 240); c.fillText('Soirée des 10 ans…', 35, 275); });
  const texNoir = ecranTex(() => {});
  const phone = M.telephone(texNoir);
  const setPhone = (tex) => { phone.userData.screen.material.map = tex; phone.userData.screen.material.needsUpdate = true; };
  const pizzaMain = M.pizzas(1);
  const nug = M.nuggets(); const pile = M.linge(2.3);
  const part = new THREE.Mesh(new THREE.ConeGeometry(0.12, 0.3, 3), M.toon(0xf2b84b)); part.rotation.set(Math.PI / 2, 0, 0);
  const bol = new THREE.Group(); bol.add(new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.12, 0.08, 24), M.toon(0x43c3ff)));
  for (let i = 0; i < 9; i++) { const k = new THREE.Mesh(new THREE.SphereGeometry(0.03, 8, 6), M.toon(0x8a5a2b)); k.position.set(Math.cos(i * 2.4) * 0.08, 0.05, Math.sin(i * 2.4) * 0.08); bol.add(k); }
  const mainSeule = new THREE.Group();
  mainSeule.add(new THREE.Mesh(new THREE.CapsuleGeometry(0.07, 0.6, 8, 16), M.toon(0xf6a9c9))).rotation.z = Math.PI / 2;
  const hs = new THREE.Mesh(new THREE.SphereGeometry(0.08, 20, 14), M.toon(0xf4c39c)); hs.position.x = 0.38; mainSeule.add(hs);
  const laptopVentre = new THREE.Group();
  laptopVentre.add(new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.02, 0.3), M.toon(0x2c2c34)));
  const lvs = new THREE.Mesh(new THREE.PlaneGeometry(0.4, 0.26), new THREE.MeshBasicMaterial({ color: 0x9fdcff })); lvs.material.userData.outlineParameters = { visible: false };
  lvs.position.set(0, 0.13, -0.14); lvs.rotation.x = -0.2; laptopVentre.add(lvs);
  const mouches = new THREE.Group(); for (let i = 0; i < 4; i++) mouches.add(new THREE.Mesh(new THREE.SphereGeometry(0.025, 8, 6), M.toon(0x111111))); sChambre.add(mouches);
  [phone, pizzaMain, nug, pile, part, bol, mainSeule, laptopVentre].forEach((o) => o.traverse((c) => { if (c.isMesh) c.castShadow = true; }));

  function reset() {
    for (const o of [lana.root, phone, pizzaMain, nug, pile, part, bol, mainSeule, laptopVentre]) o.removeFromParent();
    room.nuggets.visible = true; room.couette.position.set(0, 0.6, 0.3); room.couette.scale.set(1, 1, 1);
    pates.root.visible = true; mouches.visible = false; Lc.phone.intensity = 0; mode(Lc, 'jour');
    room.lapScreen.color.set(0x7fd0ff); lana.glasses.position.y = 0.03; cou.ombres.visible = false;
  }
  const anime = (t) => {
    room.guirlande.userData.bulbs.forEach((b, i) => { const k = 0.6 + 0.4 * Math.sin(t * 3 + i * 1.7); b.userData.halo.material.opacity = 0.25 + 0.35 * k; });
    room.rideau.rotation.y = Math.sin(t * 0.8) * 0.01;
  };
  const posePhone = (t) => { lana.root.updateMatrixWorld(true); const h = lana.handR; h.add(phone); phone.position.set(0, -0.06, 0.06); phone.rotation.set(-0.2, 0, 0); };
  const assis = (o = {}) => ({ pos: [-1.75, 0.08, -1.75], legs: [-1.45, -1.45], ...o });
  const couche = (o = {}) => ({ pos: [-1.75, 0.82, -0.35], rot: [-Math.PI / 2, 0, 0], ...o });

  const R = {};

  /* 1. ACCROCHE */
  R.hook = (t, p) => {
    reset(); sChambre.add(lana.root); anime(t);
    const tA2 = vs(p, 'a2'), tCa = wt(p, 'ça');
    if (t < tA2) {
      mode(Lc, 'nuit'); Lc.phone.intensity = 2.2;
      lana.set(assis({ armR: M.POSES.phone, armL: [-0.6, 0.3, -1.6], head: [0.28, 0.05, 0.04], look: [0.1, -0.7], lid: 0.45, blink: blink(t, 1), mouth: 'sourire', breathe: Math.sin(t * 2) }));
      posePhone(); setPhone(texNathan);
      phone.getWorldPosition(Lc.phone.position); Lc.phone.position.z += 0.25;
      look(cam, [-1.75 + tw(t, 0, tA2, 0.6, 0.25), tw(t, 0, tA2, 2.0, 1.85), -1.75 + tw(t, 0, tA2, 3.3, 2.5)], [-1.75, 1.55, -1.75], 38);
      return { scene: sChambre, camera: cam };
    }
    // révélation : debout, elle se gratte, figée sur « ça »
    const tf = Math.min(t, tCa);
    mode(Lc, 'jour');
    lana.root.add(part); part.position.set(0, 0, 0); lana.handL.add(part); part.position.set(0, -0.1, 0.08);
    lana.set({ pos: [0, 0, 0.3], armL: [-1.2 + Math.sin(tf * 9) * 0.1, 0.35, -1.5], armR: [-0.5, 0.95, -2.3 + Math.sin(tf * 14) * 0.15], head: [0.05, Math.sin(tf * 2) * 0.1, 0.1], lid: 0.55, mouth: 'ouvert', open: 0.3 + 0.3 * Math.abs(Math.sin(tf * 7)), browLift: -0.2, look: [0.3, 0], breathe: Math.sin(tf * 2) });
    const z = t > tCa ? 1 + 0.08 * eout((t - tCa) / 0.25) : 1;
    const whip = clamp((t - tA2) / 0.25);
    look(cam, [lerp(-2.5, 0, eout(whip)), 1.6, 0.3 + lerp(2.6, 3.7, eout(whip))], [0, 1.45, 0.3], 38 / z);
    return { scene: sChambre, camera: cam };
  };

  /* 2. RECORD : 11 jours sans sortir */
  R.record = (t, p) => {
    reset(); sChambre.add(lana.root); anime(t);
    lana.set(couche({ armL: [-0.3, 0.6, -1.4], armR: [-0.3, 0.6, -1.4], head: [0.25 + Math.sin(t) * 0.03, 0, 0], look: [0, -0.4], lid: 0.55, blink: blink(t, 2), mouth: 'plat' }));
    sChambre.add(laptopVentre); laptopVentre.position.set(-1.75, 1.05, -1.35); laptopVentre.rotation.set(0.6, Math.PI, 0);
    room.couette.position.set(0, 0.62, 0.7); room.couette.scale.set(1, 1, 0.6);
    pates.set({ pos: [-1.3, 0.56, -0.5], rot: [0, -0.6, 0], scale: 0.7, blink: blink(t, 5), tail: Math.sin(t * 2) * 0.3, head: [0, Math.sin(t * 0.7) * 0.3, 0] });
    Lc.phone.intensity = 1.6; Lc.phone.position.set(-1.75, 1.3, -1.6);
    look(cam, [tw(t, 0, p.dur, 0.9, 0.4), tw(t, 0, p.dur, 3.4, 2.7), tw(t, 0, p.dur, 2.2, 1.5)], [-1.6, 0.8, -1.3], 42);
    return { scene: sChambre, camera: cam };
  };

  /* 3. LE LIVREUR */
  R.livreur = (t, p) => {
    reset(); sCouloir.add(lana.root); mode(Lp, 'sombre'); Lp.key.intensity = 1.8; Lp.hemi.intensity = 1.1;
    cou.porte.position.x = 1.25; cou.ombres.visible = false;
    const tD = wt(p, 'demandé'), tB = wt(p, 'bien');
    const taking = clamp((t - (tB + 0.2)) / 0.5);
    lana.set({ pos: [-0.62, 0, 0], rot: [0, 0.55, 0], lid: 0.55, blink: blink(t, 3), look: [0.6, 0], head: [0.05, 0.1, 0], armR: taking > 0 ? twv(taking, 0, 1, M.POSES.bas, [-1.2, 0.1, -0.5]) : M.POSES.bas, mouth: 'plat', breathe: Math.sin(t * 2) });
    const worry = clamp((t - tD) / 0.3);
    livreur.set({ pos: [0.62, 0, 0.05], rot: [0, -0.55, 0], scale: 1.05, armL: [-1.15, 0.15, -0.55], armR: [-1.15, 0.15, -0.55], head: [0.05, -0.1, -0.2 * worry], browLift: 0.5 * worry, browAng: -0.6 * worry, lid: 0.15, blink: blink(t, 7), look: [-0.5, 0], mouth: worry > 0.5 ? 'ouvert' : 'plat', open: 0.1 });
    sCouloir.add(pizzaMain); pizzaMain.position.set(lerp(0.32, -0.25, eio(taking)), 1.12 - 0.06 * taking, 0.35); pizzaMain.rotation.set(0, 0.2, 0);
    look(cam, [tw(t, 0, p.dur, 0.3, 0), 1.65, tw(t, 0, p.dur, 5.0, 4.4)], [0, 1.45, 0], 38);
    return { scene: sCouloir, camera: cam };
  };

  /* 4. PÂTES */
  R.pates = (t, p) => {
    reset(); anime(t);
    const tL = wt(p, 'aime'), tC = wt(p, 'croquettes');
    let headY = Math.sin(t * 0.6) * 0.1, lid = 0.5, meow = 0;
    if (t > tL - 0.2) headY = tw(t, tL - 0.2, tL + 0.2, 0, 1.0);
    if (t > tC - 0.2) { headY = tw(t, tC - 0.2, tC + 0.2, 1.0, -0.5); lid = tw(t, tC - 0.2, tC + 0.1, 0.5, 0.0); meow = Math.sin(clamp((t - tC) / 0.6) * Math.PI) * 0.6; }
    pates.set({ pos: [-1.6, 0.56, -0.7], rot: [0, 0.35, 0], head: [0.05, headY, 0], lid, blink: blink(t, 4), tail: Math.sin(t * 2.5) * 0.4, meow });
    sChambre.add(bol); bol.position.set(-0.95, 0.6, -0.35);
    sChambre.add(mainSeule); const k = clamp(t / 0.8) - clamp((t - tL) / 0.5);
    mainSeule.position.set(lerp(-3.0, -2.25, eout(k)), 1.2 + Math.sin(t * 6) * 0.02 * k, -0.6); mainSeule.rotation.set(0, 0, -0.15);
    look(cam, [tw(t, 0, p.dur, -1.0, -1.25), 1.45, tw(t, 0, p.dur, 1.9, 1.5)], [-1.5, 1.05, -0.65], 38);
    return { scene: sChambre, camera: cam };
  };

  /* 5. LA NUIT : le téléphone vibre */
  R.nuit = (t, p) => {
    reset(); sChambre.add(lana.root); anime(t); mode(Lc, 'nuit');
    room.lapScreen.color.set(0x1a2a44);
    const tV = wt(p, 'vibre');
    lana.set(couche({ pos: [-1.75, 0.82, -0.55], lid: 1, mouth: 'ouvert', open: 0.15 + 0.1 * Math.sin(t * 2), head: [0.15, 0.3, 0], armL: M.POSES.bas, armR: M.POSES.bas }));
    room.couette.position.set(0, 0.68, 0.15); room.couette.scale.set(1.05, 1.3, 1.25);
    pates.set({ pos: [-1.2, 0.56, -0.4], rot: [0, -0.4, 0], scale: 0.7, lid: 1, tail: 0 });
    sChambre.add(phone); setPhone(t > tV ? texMsg : texNoir);
    const v = t > tV ? Math.sin(t * 90) * 0.012 * (Math.sin(t * 6) > 0 ? 1 : 0) : 0;
    phone.position.set(-0.65 + v, 0.52, -2.05); phone.rotation.set(-Math.PI / 2 + 0.02, 0, 0.3 + v * 3);
    Lc.phone.position.set(-0.65, 0.9, -1.9); Lc.phone.intensity = t > tV ? 2.5 : 0;
    look(cam, [tw(t, 0, p.dur, 0.6, 0.0), tw(t, 0, p.dur, 2.4, 1.8), tw(t, 0, p.dur, 1.6, 0.2)], [-1.25, 0.8, -1.9], 40);
    return { scene: sChambre, camera: cam };
  };

  /* 6. LE MESSAGE D'INÈS */
  R.message = (t, p) => {
    reset(); sChambre.add(lana.root); anime(t); mode(Lc, 'nuit'); room.lapScreen.color.set(0x1a2a44);
    const t3 = vs(p, 'e3');
    const froid = clamp((t - t3) / 0.6);
    lana.set(assis({ armR: M.POSES.phone, armL: [-0.4, 0.3, -1.2], head: [0.2, 0, 0.03], look: [0.1, -0.6], lid: lerp(0.62, 0.45, froid), blink: blink(t, 2), browAng: 0.7 * froid, browLift: -0.1, mouth: 'plat', breathe: Math.sin(t * 2) }));
    room.couette.position.set(0, 0.62, 0.55); room.couette.scale.set(1, 1, 0.75);
    pates.set({ pos: [-1.2, 0.56, -0.9], rot: [0, -0.9, 0], scale: 0.7, lid: 0.7, blink: blink(t, 6), head: [0, -0.4 + 0.2 * Math.sin(t), 0], tail: Math.sin(t * 2) * 0.3 });
    posePhone(); setPhone(texMsg);
    phone.getWorldPosition(Lc.phone.position); Lc.phone.position.z += 0.3; Lc.phone.position.y += 0.1; Lc.phone.intensity = 2.6;
    const z = tw(t, 0, p.dur, 0, 1);
    look(cam, [-1.75 + lerp(0.5, 0.15, z), lerp(1.95, 1.85, z), -1.75 + lerp(3.2, 2.1, z)], [-1.75, 1.6, -1.75], 38);
    return { scene: sChambre, camera: cam };
  };

  /* 7. LE REFUS puis le 2e message */
  R.refus = (t, p) => {
    reset(); sChambre.add(lana.root); anime(t); mode(Lc, 'nuit'); room.lapScreen.color.set(0x1a2a44);
    const tF2 = vs(p, 'f2'), tF3 = vs(p, 'f3'), e1 = ve(p, 'f1');
    room.couette.position.set(0, 0.62, 0.55); room.couette.scale.set(1, 1, 0.75);
    pates.set({ pos: [-1.2, 0.56, -0.9], rot: [0, -0.9, 0], scale: 0.7, lid: 0.7, blink: blink(t, 6) });
    const a = amp(p, t);
    let st = assis({ armR: M.POSES.phone, armL: [-0.4, 0.3, -1.2], head: [0.1, 0, 0], look: [0, -0.2], lid: 0.4, blink: blink(t, 3), browAng: 0.8, mouth: 'parle', open: a });
    let ph = 'main';
    if (t > e1 - 0.15) { // jette le téléphone, bras croisés, tête tournée
      const k = clamp((t - (e1 - 0.15)) / 0.35);
      st = { ...st, armR: twv(k, 0, 1, M.POSES.phone, M.POSES.croise), armL: twv(k, 0, 1, [-0.4, 0.3, -1.2], M.POSES.croise), head: [0, lerp(0, -0.9, eout(k)), 0.1], look: [-0.6, 0], lid: 0.5, mouth: 'plat' };
      ph = 'lance';
    }
    if (t > tF2 - 0.2) st.look = [lerp(-0.6, 0.9, clamp((t - tF2) / 0.4)), -0.3], st.lid = tw(t, tF2, tF2 + 0.3, 0.5, 0.1);
    if (t > tF3 + 0.3) { const k = clamp((t - tF3 - 0.3) / 0.5); st.head = [0.2 * k, lerp(-0.9, 0, eout(k)), 0]; st.armR = twv(k, 0, 1, M.POSES.croise, M.POSES.phone); st.armL = twv(k, 0, 1, M.POSES.croise, [-0.4, 0.3, -1.2]); st.look = [0.1, -0.6]; st.lid = 0.15; st.browAng = 0; st.browLift = 0.4; if (k >= 1) ph = 'main'; }
    lana.set(st);
    if (ph === 'main') { posePhone(); setPhone(t > tF3 ? texMsg : texMsg); phone.getWorldPosition(Lc.phone.position); Lc.phone.position.z += 0.3; Lc.phone.intensity = 2.4; }
    else {
      sChambre.add(phone); const k = clamp((t - (e1 - 0.15)) / 0.45);
      const buzz = t > tF2 - 0.2 && t < tF2 + 1.2 ? Math.sin(t * 90) * 0.01 : 0;
      phone.position.set(lerp(-1.6, -1.0, k) + buzz, 0.76 + Math.sin(k * Math.PI) * 0.35, lerp(-1.4, -0.7, k)); phone.rotation.set(-Math.PI / 2, 0, k * 6);
      Lc.phone.position.set(-1.0, 1.1, -0.6); Lc.phone.intensity = t > tF2 - 0.2 ? 2.4 : 0.6; setPhone(texMsg);
    }
    look(cam, [-1.75 + 0.45, 1.95, -1.75 + 2.6], [-1.6, 1.45, -1.5], 40);
    return { scene: sChambre, camera: cam };
  };

  /* 8. LE CRI */
  R.cri = (t, p) => {
    reset(); sChambre.add(lana.root); anime(t); mode(Lc, 'nuit'); room.lapScreen.color.set(0x1a2a44);
    room.couette.position.set(0, 0.62, 0.55); room.couette.scale.set(1, 1, 0.75);
    const a = amp(p, t);
    const k = eout(t / 0.18);
    lana.set(assis({ pos: [-1.75, 0.08 + 0.12 * Math.sin(clamp(t / 0.3) * Math.PI), -1.75], armR: twv(k, 0, 1, M.POSES.phone, M.POSES.haut), armL: twv(k, 0, 1, [-0.4, 0.3, -1.2], M.POSES.haut), eyes: 1.35, lid: 0, look: [0, 0], browLift: 0.9, mouth: 'parle', open: Math.max(0.5, a), head: [-0.15, Math.sin(t * 40) * 0.05, 0] }));
    lana.glasses.position.y = 0.03 + 0.06 * Math.sin(clamp(t / 0.3) * Math.PI);
    pates.set({ pos: [-1.2, 0.56 + 0.5 * Math.sin(clamp(t / 0.6) * Math.PI), -0.9], rot: [0, -0.9, 0], scale: 0.7, lid: 0, tail: 1 });
    Lc.phone.intensity = 1.5; Lc.phone.position.set(-1.6, 2.2, -1.2);
    const [sx, sy] = shake(t, 0, 0.9, 0.04);
    const z = lerp(3.0, 1.9, eout(t / 0.3));
    look(cam, [-1.75 + sx, 1.9 + sy, -1.75 + z], [-1.75, 1.75, -1.75], 40);
    return { scene: sChambre, camera: cam };
  };

  /* 9. LE BAL (flashback) */
  R.bal = (t, p) => {
    const tJ = vs(p, 'g2');
    const sad = clamp((t - tJ) / 1.2);
    mode(Ll, 'sombre'); Ll.hemi.intensity = lerp(0.9, 0.35, sad); Ll.key.intensity = lerp(1.0, 0.15, sad); Ll.rim.intensity = 0.8;
    spot.intensity = lerp(10, 40, sad);
    [ly.g1, ly.g2].forEach((g) => g.userData.bulbs.forEach((b, i) => { b.userData.halo.material.opacity = (0.3 + 0.3 * Math.sin(t * 3 + i)) * (1 - 0.7 * sad); }));
    ly.disco.rotation.y = t * 0.6;
    const lookDoor = Math.sin(t * 0.7) * 0.25 - 0.45;
    ado.set({ pos: [0, 0, 0], rot: [0, 0.15, 0], armL: [-1.0, -0.15, -0.9], armR: [-1.0, -0.15, -0.9], head: [lerp(0, 0.35, sad), lerp(lookDoor, 0, sad), 0], look: [lerp(-0.8, 0, sad), lerp(0, -0.6, sad)], lid: lerp(0.1, 0.55, sad), blink: blink(t, 8), mouth: sad > 0.3 ? 'plat' : 'sourire', browAng: -0.7 * sad, browLift: 0.2 * sad, breathe: Math.sin(t * 2) });
    if (!ado.cadeau) { ado.cadeau = new THREE.Group(); ado.cadeau.add(new THREE.Mesh(new THREE.BoxGeometry(0.22, 0.18, 0.18), M.toon(0xe84f8a))); ado.cadeau.add(new THREE.Mesh(new THREE.BoxGeometry(0.235, 0.04, 0.19), M.toon(0xffd23f))); sLycee.add(ado.cadeau); }
    ado.cadeau.position.set(0.02, 0.98, 0.45);
    const a = t * 0.04 + 0.2;
    const d = lerp(3.4, 5.2, sad);
    look(cam, [Math.sin(a) * d, lerp(1.7, 2.6, sad), Math.cos(a) * d], [0, lerp(1.35, 1.0, sad), 0], 38);
    return { scene: sLycee, camera: cam };
  };

  /* 10. LA DÉCISION */
  R.decision = (t, p) => {
    reset(); sChambre.add(lana.root); anime(t); mode(Lc, 'matin');
    Lc.key.position.set(1.2, 3, -3); room.lapScreen.color.set(0x7fd0ff);
    const a = amp(p, t);
    const k = clamp((t - 0.2) / 0.4);
    lana.set({ pos: [0, 0, 0.2], armL: twv(k, 0, 1, M.POSES.bas, M.POSES.poing), armR: twv(clamp((t - 0.9) / 0.35), 0, 1, M.POSES.bas, M.POSES.poing), lid: 0.25, browAng: 0.9, browLift: -0.2, mouth: a > 0.05 ? 'parle' : 'dents', open: a, head: [-0.08, 0, 0], blink: blink(t, 9), breathe: Math.sin(t * 3) });
    look(cam, [tw(t, 0, p.dur, 0.5, 0.2), tw(t, 0, p.dur, 0.7, 0.9), tw(t, 0, p.dur, 3.0, 2.2)], [0, 1.6, 0.2], 40);
    return { scene: sChambre, camera: cam };
  };

  /* 11. LA CHUTE */
  R.chute = (t, p) => {
    reset(); sChambre.add(lana.root); anime(t); mode(Lc, 'matin'); Lc.key.position.set(1.2, 3, -3);
    room.nuggets.visible = false;
    const tSlip = ve(p, 'h2') + 0.05, tLand = tSlip + 0.55;
    if (t < tLand) {
      const sm = 0.55; const z = lerp(-1.4, 0.55, clamp(t / tSlip));
      const ph = t * 3.2 * sm;
      let st = { pos: [0, Math.abs(Math.sin(ph)) * 0.04, z], legs: [Math.sin(ph) * 0.45, -Math.sin(ph) * 0.45], armL: [-Math.sin(ph) * 0.5, 0.15, -0.4], armR: [Math.sin(ph) * 0.5, 0.15, -0.4], head: [-0.15, 0, 0], lid: 0.2, browAng: 0.6, mouth: 'sourire', look: [0, 0.2], blink: blink(t, 3) };
      if (t > tSlip) {
        const k = clamp((t - tSlip) / 0.55);
        st = { ...st, pos: [0, Math.sin(k * Math.PI) * 0.6, z + k * 0.6], rot: [-k * 1.9, 0, 0], legs: [-1.2 * k, -0.9 * k], armL: M.POSES.haut, armR: M.POSES.haut, eyes: 1.35, lid: 0, mouth: 'ouvert', open: 0.9, browLift: 0.9 };
      }
      lana.set(st);
      sChambre.add(nug); const nk = clamp((t - tSlip) / 0.9);
      nug.position.set(0.05 + nk * 0.8, Math.sin(nk * Math.PI) * 1.4, 0.75 + nk * 0.4); nug.rotation.set(nk * 9, nk * 5, 0);
      look(cam, [0.4, 0.75, 3.3], [0, 1.0, 0.2], 42);
    } else {
      const k = t - tLand;
      sChambre.add(pile); pile.position.set(0, 0, 0.6);
      lana.set({ pos: [0, 1.32 + Math.sin(k * 7) * 0.02 * Math.exp(-k), 0.6], rot: [Math.PI, 0, 0.1 + Math.sin(k * 4) * 0.08 * Math.exp(-k * 0.5)], legs: [Math.sin(k * 9) * 0.25, -Math.sin(k * 9 + 1) * 0.25] });
      sChambre.add(nug); const nk = clamp(k / 0.5);
      nug.position.set(0.15, lerp(2.4, 1.38, eout(nk)), 0.6); nug.rotation.set(0, k * 0.5, 0.2);
      const [sx, sy] = shake(t, tLand, 0.45, 0.06);
      look(cam, [0.3 + sx, 1.3 + sy, 3.2], [0, 0.85, 0.5], 40);
    }
    return { scene: sChambre, camera: cam };
  };

  /* 12. LE MIROIR */
  R.miroir = (t, p) => {
    reset(); sSdb.add(lana.root); mode(Ls, 'jour'); Ls.key.position.set(0, 4, 4);
    const tToi = wt(p, 'toi'), tC = wt(p, 'Chaque');
    let st = { pos: [0, 0, 0], lid: 0.35, blink: blink(t, 4), look: [0, 0.5], head: [0, Math.sin(t * 0.8) * 0.12, 0], torso: [0.12, 0, 0], armL: M.POSES.tete, armR: M.POSES.bas, browLift: 0.3, mouth: 'plat' };
    if (t > 1.6) st = { ...st, armL: M.POSES.bas, look: [0, 0], head: [0, 0, 0], torso: [0, 0, 0] };
    if (t > tToi - 0.15) st = { ...st, armR: M.POSES.pointe, point: true, mouth: 'sourire', lid: 0.15, browLift: 0.5 };
    if (t > tC) st = { ...st, armR: M.POSES.croise, armL: M.POSES.croise, point: false, mouth: 'plat', browAng: 0.5, head: [Math.sin(t * 3) * 0.04, 0, 0] };
    lana.set(st);
    const z = t > tToi ? tw(t, tToi, tToi + 0.3, 1.9, 1.55, eout) : tw(t, 0, tToi, 2.3, 1.9);
    look(cam, [0, 1.65, z], [0, 1.5, 0], 40);
    return { scene: sSdb, camera: cam };
  };

  /* 13. LE VOTE : écran partagé haut/bas */
  R.vote = (t, p) => {
    reset(); sChambre.add(lana.root); anime(t); mode(Lc, 'jour');
    mouches.visible = true;
    mouches.children.forEach((m, i) => m.position.set(-0.85 + Math.cos(t * 6 + i * 2) * 0.35, 0.55 + Math.sin(t * 9 + i) * 0.15, 0.4 + Math.sin(t * 5 + i * 3) * 0.3));
    lana.set({ pos: [1.0, 0, -0.6], lid: 0.45, blink: blink(t, 5), look: [0, 0.6], browLift: Math.sin(t * 7) * 0.25, mouth: 'plat', head: [-0.1, 0, 0] });
    look(cam, [tw(t, 0, p.dur, -0.2, 0.1), 2.0, 2.6], [-0.9, 0.6, -0.2], 42); cam.aspect = 720 / 640; cam.updateProjectionMatrix();
    look(cam2, [1.0, 1.75, -0.6 + tw(t, 0, p.dur, 0.85, 0.7)], [1.0, 1.75, -0.6], 34); cam2.aspect = 720 / 640; cam2.updateProjectionMatrix();
    return { viewports: [{ x: 0, y: 640, w: 720, h: 640, scene: sChambre, camera: cam }, { x: 0, y: 0, w: 720, h: 640, scene: sChambre, camera: cam2 }] };
  };

  /* 14. APPEL AU VOTE */
  R.cta = (t, p) => {
    reset(); sChambre.add(lana.root); anime(t); mode(Lc, 'jour');
    lana.set({ pos: [-0.3, 0, 0.1], rot: [0, 0.15, 0], armR: [M.POSES.coucou[0], M.POSES.coucou[1], -0.9 + Math.sin(t * 9) * 0.35], lid: 0.15, blink: blink(t, 2), mouth: 'sourire', browLift: 0.3, head: [0, 0, Math.sin(t * 3) * 0.06], breathe: Math.sin(t * 2) });
    pates.set({ pos: [-1.35, 0.56, -0.5], rot: [0, 0.5, 0], scale: 0.75, lid: 0.55, blink: blink(t, 7), tail: Math.sin(t * 2.5) * 0.4, head: [0, -0.3, 0] });
    look(cam, [0, 1.55, 3.6], [-0.45, 1.25, -0.2], 40);
    return { scene: sChambre, camera: cam };
  };

  /* 15. QUELQU'UN SONNE À LA PORTE */
  R.porte = (t, p) => {
    reset(); mode(Lp, 'nuit'); Lp.key.intensity = 0.3; Lp.hemi.intensity = 0.45;
    cou.porte.position.x = 0; livreur.root.visible = false;
    const tS = wt(p, 'sonne');
    cou.ombres.visible = t > tS - 0.3;
    cou.ombres.children.forEach((o, i) => { o.position.x = (i ? 0.12 : -0.12) + Math.sin(t * 2) * 0.05; o.scale.x = 1 + 0.2 * Math.sin(t * 5 + i); });
    cou.porte.position.z = -0.95 + (t > tS && t < tS + 0.4 ? Math.sin(t * 60) * 0.006 : 0);
    look(cam, [0, 1.25, tw(t, 0, p.dur, 3.8, 2.2)], [0, 1.0, -0.9], 40);
    const r = { scene: sCouloir, camera: cam };
    return r;
  };

  const plan = (T) => { let p = plans[plans.length - 1]; for (const x of plans) if (T >= x.start && T < x.start + x.dur) { p = x; break; } return p; };
  return {
    update(T) {
      const p = plan(T); const t = T - p.start;
      livreur.root.visible = true;
      cam.aspect = 720 / 1280; cam.updateProjectionMatrix();
      return R[p.id](t, p);
    },
  };
}
