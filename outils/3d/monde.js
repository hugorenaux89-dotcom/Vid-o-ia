// Lana 30 jours — monde 3D (Three.js) : matériaux toon, personnages articulés, décors
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

/* ---------- matériaux ---------- */
const grad = (() => {
  const d = new Uint8Array([90, 90, 90, 255, 175, 175, 175, 255, 255, 255, 255, 255]);
  const t = new THREE.DataTexture(d, 3, 1, THREE.RGBAFormat);
  t.minFilter = t.magFilter = THREE.NearestFilter; t.needsUpdate = true; return t;
})();
const cache = {};
export function toon(color, o = {}) {
  const k = color + JSON.stringify(o);
  if (!o.unique && cache[k]) return cache[k];
  const m = new THREE.MeshToonMaterial({ color, gradientMap: grad, ...o.mat });
  if (o.emissive) { m.emissive = new THREE.Color(o.emissive); m.emissiveIntensity = o.ei ?? 1; }
  if (o.map) m.map = o.map;
  if (o.transparent) { m.transparent = true; m.opacity = o.opacity ?? 1; }
  m.userData.outlineParameters = { thickness: o.outline ?? 0.0045, color: [0.05, 0.03, 0.06], visible: o.noOutline ? false : true };
  if (!o.unique) cache[k] = m;
  return m;
}
export const flat = (color, o = {}) => {
  const m = new THREE.MeshBasicMaterial({ color, transparent: !!o.transparent, opacity: o.opacity ?? 1, side: o.side ?? THREE.FrontSide, depthWrite: o.depthWrite ?? true });
  if (o.map) m.map = o.map;
  m.userData.outlineParameters = { visible: false };
  return m;
};
const noOutline = (mesh) => { mesh.traverse((c) => { if (c.material) c.material.userData.outlineParameters = { visible: false }; }); return mesh; };

export function mesh(geo, mat, pos = [0, 0, 0], rot = [0, 0, 0], scale = [1, 1, 1], o = {}) {
  const m = new THREE.Mesh(geo, mat);
  m.position.set(...pos); m.rotation.set(...rot); m.scale.set(...scale);
  m.castShadow = o.cast ?? true; m.receiveShadow = o.receive ?? true;
  return m;
}
const S = (r, ws = 32, hs = 24) => new THREE.SphereGeometry(r, ws, hs);
const CAP = (r, l) => new THREE.CapsuleGeometry(r, l, 8, 20);
const BOX = (w, h, d, r = 0.03) => new RoundedBoxGeometry(w, h, d, 3, Math.min(r, w / 2.1, h / 2.1, d / 2.1));
const CYL = (rt, rb, h, s = 28) => new THREE.CylinderGeometry(rt, rb, h, s);

/* ---------- textures dessinées ---------- */
export function canvasTex(w, h, draw) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  const g = c.getContext('2d'); draw(g, w, h);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4;
  return t;
}
const stripes = (a, b, n = 12) => canvasTex(512, 512, (g, w, h) => { g.fillStyle = a; g.fillRect(0, 0, w, h); g.fillStyle = b; for (let i = 0; i < n; i++) g.fillRect(i * w / n, 0, w / n / 2, h); });

/* ---------- PERSONNAGE ---------- */
const SKIN = 0xf4c39c, HAIR = 0x7a4526, PINK = 0xf6a9c9;
export function personnage(o = {}) {
  const P = {
    skin: SKIN, hair: HAIR, top: PINK, pants: PINK, sleeves: PINK, shoes: 'licorne', glasses: true, bun: true, longHair: false,
    pimples: true, unicorn: true, stains: true, cap: null, shortHair: false, browThick: true, ...o,
  };
  const root = new THREE.Group();
  const body = new THREE.Group(); root.add(body);
  const R = { root, body, P };
  // jambes
  const legMat = toon(P.pants);
  for (const s of [-1, 1]) {
    const leg = new THREE.Group(); leg.position.set(s * 0.13, 0.62, 0); body.add(leg);
    leg.add(mesh(CAP(0.115, 0.36), legMat, [0, -0.27, 0]));
    // pieds
    if (P.shoes === 'licorne') {
      const f = new THREE.Group(); f.position.set(0, -0.53, 0.07); leg.add(f);
      f.add(mesh(S(0.14), toon(0xffffff), [0, 0, 0], [0, 0, 0], [0.95, 0.6, 1.35]));
      f.add(mesh(new THREE.ConeGeometry(0.035, 0.13, 16), toon(0xffd23f), [0, 0.1, 0.11], [0.5, 0, 0]));
      for (const e of [-1, 1]) f.add(mesh(S(0.02, 12, 8), toon(0x151515), [e * 0.05, 0.05, 0.17]));
    } else {
      leg.add(mesh(BOX(0.2, 0.12, 0.32, 0.05), toon(0xffffff), [0, -0.55, 0.05]));
      leg.add(mesh(BOX(0.205, 0.03, 0.325, 0.01), toon(0xe23b3b), [0, -0.6, 0.05]));
    }
    R['leg' + (s < 0 ? 'L' : 'R')] = leg;
  }
  // torse
  const torso = new THREE.Group(); torso.position.y = 0.62; body.add(torso); R.torso = torso;
  torso.add(mesh(CAP(0.29, 0.34), toon(P.top), [0, 0.33, 0], [0, 0, 0], [1, 1, 0.82]));
  if (P.jacket) {
    for (const s of [-1, 1]) torso.add(mesh(CAP(0.17, 0.32), toon(P.jacket), [s * 0.17, 0.36, 0.02], [0, 0, 0], [1, 1, 1.15]));
    torso.add(mesh(new THREE.CircleGeometry(0.07, 5), toon(0xffd23f), [0, 0.38, 0.245], [0, 0, 0.3]));
  }
  if (P.unicorn) {
    const u = new THREE.Group(); u.position.set(0, 0.32, 0.235); torso.add(u);
    u.add(mesh(new THREE.CircleGeometry(0.11, 32), toon(0xffffff, { noOutline: true }), [0, 0, 0.005]));
    u.add(mesh(new THREE.ConeGeometry(0.025, 0.08, 12), toon(0xffd23f), [0, 0.12, 0.01]));
    for (const e of [-1, 1]) u.add(mesh(new THREE.CircleGeometry(0.014, 12), flat(0x151515), [e * 0.04, 0.01, 0.012]));
    u.add(mesh(new THREE.TorusGeometry(0.03, 0.006, 6, 16, Math.PI), flat(0x151515), [0, -0.03, 0.012], [0, 0, Math.PI]));
  }
  if (P.stains) {
    for (const [x, y, r, c] of [[-0.15, 0.5, 0.035, 0xc9783f], [0.17, 0.15, 0.045, 0xc9783f], [-0.12, 0.12, 0.022, 0xe23b3b], [0.14, 0.48, 0.018, 0xffd23f]])
      torso.add(mesh(new THREE.CircleGeometry(r, 16), flat(c), [x, y, 0.24 - Math.abs(x) * 0.18], [0, x * 1.2, 0]));
  }
  // bras
  for (const s of [-1, 1]) {
    const sh = new THREE.Group(); sh.position.set(s * 0.3, 0.55, 0); torso.add(sh);
    sh.add(mesh(CAP(0.075, 0.18), toon(P.sleeves), [0, -0.13, 0]));
    const el = new THREE.Group(); el.position.y = -0.27; sh.add(el);
    el.add(mesh(CAP(0.07, 0.16), toon(P.sleeves), [0, -0.11, 0]));
    const hand = new THREE.Group(); hand.position.y = -0.25; el.add(hand);
    hand.add(mesh(S(0.075), toon(P.skin), [0, 0, 0], [0, 0, 0], [1, 1.05, 0.85]));
    const finger = mesh(CAP(0.022, 0.08), toon(P.skin), [0, -0.09, 0.03], [0.3, 0, 0]); finger.visible = false; hand.add(finger);
    R['sh' + (s < 0 ? 'L' : 'R')] = sh; R['el' + (s < 0 ? 'L' : 'R')] = el; R['hand' + (s < 0 ? 'L' : 'R')] = hand; R['finger' + (s < 0 ? 'L' : 'R')] = finger;
  }
  // tête
  const neck = new THREE.Group(); neck.position.y = 1.2; body.add(neck); R.neck = neck;
  neck.add(mesh(CYL(0.08, 0.09, 0.14), toon(P.skin), [0, 0.02, 0]));
  const head = new THREE.Group(); head.position.y = 0.4; neck.add(head); R.head = head;
  head.add(mesh(S(0.42, 48, 36), toon(P.skin), [0, 0, 0], [0, 0, 0], [1, 0.97, 0.94]));
  for (const s of [-1, 1]) head.add(mesh(S(0.08), toon(P.skin), [s * 0.41, -0.02, -0.02], [0, 0, 0], [0.6, 1, 0.8]));
  // cheveux
  const hm = toon(P.hair);
  if (P.shortHair) {
    head.add(mesh(new THREE.SphereGeometry(0.445, 40, 30, 0, Math.PI * 2, 0, Math.PI * 0.42), hm, [0, 0.02, -0.02], [-0.25, 0, 0]));
  } else {
    head.add(mesh(new THREE.SphereGeometry(0.455, 40, 30, 0, Math.PI * 2, 0, Math.PI * 0.62), hm, [0, 0.03, -0.04], [-0.55, 0, 0]));
    // frange
    for (const [x, y, rz, sx] of [[-0.24, 0.22, 0.55, 1.1], [-0.08, 0.28, 0.25, 1], [0.09, 0.28, -0.2, 1], [0.25, 0.21, -0.55, 1.1]])
      head.add(mesh(S(0.16), hm, [x, y + 0.04, 0.26], [0.45, 0, rz], [sx, 0.55, 0.5]));
    // mèches sur les côtés
    for (const s of [-1, 1]) head.add(mesh(CAP(0.07, P.longHair ? 0.75 : 0.3), hm, [s * 0.37, P.longHair ? -0.38 : -0.12, 0.05], [0, 0, s * -0.12]));
    if (P.longHair) head.add(mesh(CAP(0.38, 0.55), hm, [0, -0.38, -0.2], [0.1, 0, 0], [1.05, 1, 0.55]));
  }
  if (P.bun) {
    const bun = new THREE.Group(); bun.position.set(0, 0.43, -0.08); head.add(bun); R.bun = bun;
    bun.add(mesh(S(0.2), hm, [0, 0.1, 0], [0, 0, 0], [1, 0.85, 1]));
    bun.add(mesh(new THREE.TorusGeometry(0.15, 0.04, 12, 28), toon(0x43c3ff), [0, -0.02, 0], [Math.PI / 2, 0, 0]));
    const pen = new THREE.Group(); pen.position.set(0.05, 0.12, 0); pen.rotation.set(0.2, 0, -0.65); bun.add(pen);
    pen.add(mesh(CYL(0.022, 0.022, 0.42, 6), toon(0xffd23f), [0, 0.1, 0]));
    pen.add(mesh(CYL(0.023, 0.023, 0.05, 6), toon(0xff6b9a), [0, 0.33, 0]));
    for (const [rx, rz] of [[0.6, 0.9], [-0.5, -1.0], [0.1, 1.6], [-0.9, 0.2]]) bun.add(mesh(CAP(0.025, 0.14), hm, [Math.sin(rz) * 0.17, 0.2, Math.sin(rx) * 0.1], [rx, 0, rz]));
  }
  if (P.cap) {
    head.add(mesh(new THREE.SphereGeometry(0.46, 32, 20, 0, Math.PI * 2, 0, Math.PI * 0.38), toon(P.cap), [0, 0.08, 0], [-0.15, 0, 0]));
    head.add(mesh(BOX(0.42, 0.04, 0.3, 0.02), toon(P.cap), [0, 0.18, 0.42], [0.25, 0, 0]));
  }
  // visage
  const face = new THREE.Group(); face.position.set(0, -0.02, 0.35); head.add(face); R.face = face;
  for (const s of [-1, 1]) {
    const eye = new THREE.Group(); eye.position.set(s * 0.15, 0.03, 0.0); face.add(eye);
    eye.add(mesh(S(0.085), toon(0xffffff), [0, 0, 0], [0, 0, 0], [1, 1.1, 0.6]));
    const pup = new THREE.Group(); pup.position.z = 0.045; eye.add(pup);
    pup.add(mesh(S(0.046, 20, 14), toon(0x5a3420, { noOutline: true }), [0, 0, 0], [0, 0, 0], [1, 1, 0.5]));
    pup.add(mesh(S(0.028, 16, 12), flat(0x111111), [0, 0, 0.012], [0, 0, 0], [1, 1, 0.5]));
    pup.add(mesh(S(0.011, 10, 8), flat(0xffffff), [0.014, 0.016, 0.025]));
    // paupière (haut)
    const lid = mesh(new THREE.SphereGeometry(0.092, 28, 16, 0, Math.PI * 2, 0, Math.PI / 2), toon(P.skin), [0, 0, 0], [0, 0, 0], [1, 1.1, 0.68]);
    eye.add(lid);
    R['eye' + (s < 0 ? 'L' : 'R')] = eye; R['pup' + (s < 0 ? 'L' : 'R')] = pup; R['lid' + (s < 0 ? 'L' : 'R')] = lid;
    // sourcils
    const brow = new THREE.Group(); brow.position.set(s * 0.15, 0.15, 0.075); face.add(brow);
    brow.add(mesh(CAP(P.browThick ? 0.03 : 0.013, P.browThick ? 0.12 : 0.1), toon(0x3b2213), [0, 0, 0], [0, 0, Math.PI / 2 + s * 0.12], [1, 1, 0.7]));
    if (P.browThick) for (let i = 0; i < 4; i++) brow.add(mesh(CAP(0.009, 0.03), toon(0x3b2213, { noOutline: true }), [-0.06 + i * 0.04, 0.035, 0], [0, 0, (i - 1.5) * 0.3]));
    R['brow' + (s < 0 ? 'L' : 'R')] = brow;
    // joues
    face.add(mesh(new THREE.CircleGeometry(0.06, 20), flat(0xff7d8e, { transparent: true, opacity: 0.45, depthWrite: false }), [s * 0.24, -0.11, -0.02], [0, s * 0.5, 0]));
    if (!P.glasses && !P.pimples) { /* rien */ }
  }
  // cernes / boutons
  if (P.pimples) {
    for (const [x, y, z] of [[-0.29, -0.15, -0.06], [0.19, 0.26, -0.02], [0.1, -0.27, -0.03]]) face.add(mesh(S(0.018, 10, 8), toon(0xe8434a), [x, y, z]));
    for (const s of [-1, 1]) face.add(mesh(new THREE.TorusGeometry(0.06, 0.008, 6, 18, Math.PI * 0.8), flat(0xb9786b), [s * 0.15, -0.035, 0.02], [0, 0, Math.PI * 1.1]));
  }
  // nez
  face.add(mesh(S(0.035), toon(0xeeb38a), [0, -0.06, 0.06], [0, 0, 0], [1, 0.9, 0.9]));
  // bouches
  const mouth = new THREE.Group(); mouth.position.set(0, -0.18, 0.02); face.add(mouth); R.mouth = mouth;
  const dark = toon(0x7a1f2b);
  R.mouths = {
    plat: mesh(new THREE.TorusGeometry(0.06, 0.012, 8, 20, Math.PI * 0.7), flat(0x2a1010), [0, -0.03, 0], [0, 0, Math.PI * 0.15]),
    ouvert: (() => { const g = new THREE.Group(); g.add(mesh(S(0.07, 24, 16), dark, [0, 0, 0], [0, 0, 0], [1, 1, 0.35])); g.add(mesh(S(0.04, 16, 12), toon(0xff8a95), [0, -0.035, 0.012], [0, 0, 0], [1, 0.6, 0.3])); return g; })(),
    sourire: (() => { const g = new THREE.Group(); g.add(mesh(new THREE.SphereGeometry(0.08, 24, 16, 0, Math.PI * 2, Math.PI / 2, Math.PI / 2), dark, [0, 0.02, 0], [0, 0, 0], [1, 0.75, 0.35])); g.add(mesh(BOX(0.12, 0.025, 0.02, 0.008), toon(0xffffff), [0, 0.01, 0.02])); return g; })(),
    dents: mesh(BOX(0.15, 0.06, 0.04, 0.02), toon(0xffffff), [0, 0, 0]),
  };
  for (const k in R.mouths) { mouth.add(R.mouths[k]); R.mouths[k].visible = false; }
  // lunettes
  if (P.glasses) {
    const gl = new THREE.Group(); gl.position.set(0, 0.03, 0.06); gl.rotation.z = -0.07; face.add(gl); R.glasses = gl;
    const gm = toon(0x141414);
    for (const s of [-1, 1]) {
      gl.add(mesh(new THREE.TorusGeometry(0.115, 0.016, 10, 40), gm, [s * 0.15, 0, 0]));
      gl.add(mesh(new THREE.CircleGeometry(0.11, 32), flat(0xbfe6ff, { transparent: true, opacity: 0.12, depthWrite: false }), [s * 0.15, 0, -0.005]));
      gl.add(mesh(CYL(0.012, 0.012, 0.3, 6), gm, [s * 0.27, 0, -0.17], [Math.PI / 2, 0, 0]));
    }
    gl.add(mesh(CYL(0.014, 0.014, 0.07, 6), gm, [0, 0.01, 0], [0, 0, Math.PI / 2]));
    gl.add(mesh(BOX(0.06, 0.045, 0.02, 0.005), toon(0xffffff), [0, 0.01, 0.01]));
  }
  root.traverse((c) => { if (c.isMesh) c.receiveShadow = false; });
  // état
  R.set = (st) => poser(R, st);
  R.set({});
  return R;
}

const lerp = (a, b, t) => a + (b - a) * t;
// Pose : angles en radians. bras = [avant/arrière (x), écart (z), coude (x)]
export const POSES = {
  bas: [0.05, 0.12, -0.15], hanche: [0.2, 0.65, -1.9], haut: [0.1, 2.7, -0.35], phone: [-1.05, 0.25, -1.35],
  pointe: [-1.45, 0.1, -0.1], coucou: [0.0, 2.3, -0.9], hausse: [-0.4, 0.95, -1.6], poing: [-0.3, 2.5, -1.4], tete: [-0.5, 0.9, -2.3], croise: [-1.2, -0.35, -1.6],
};
function poser(R, st) {
  const s = { lid: 0.25, blink: 0, look: [0, 0], browLift: 0, browAng: 0, mouth: 'plat', open: 0, head: [0, 0, 0], torso: [0, 0, 0], armL: POSES.bas, armR: POSES.bas, legs: [0, 0], pos: [0, 0, 0], rot: [0, 0, 0], scale: 1, breathe: 0, squash: 0, point: false, eyes: 1, ...st };
  R.root.position.set(...s.pos); R.root.rotation.set(...s.rot); R.root.scale.setScalar(s.scale);
  R.body.scale.set(1 + s.squash * 0.15, 1 - s.squash * 0.2 + s.breathe * 0.012, 1 + s.squash * 0.15);
  R.torso.rotation.set(...s.torso);
  R.head.rotation.set(...s.head);
  const lid = Math.max(s.lid, s.blink);
  for (const k of ['L', 'R']) {
    R['lid' + k].rotation.x = lerp(-1.75, -0.05, lid) ; // ouvert -> fermé
    R['lid' + k].visible = lid > 0.02;
    R['pup' + k].position.x = s.look[0] * 0.03; R['pup' + k].position.y = s.look[1] * 0.03;
    R['eye' + k].scale.setScalar(s.eyes);
    R['pup' + k].scale.setScalar(s.eyes > 1.1 ? 0.7 : 1);
    const sg = k === 'L' ? -1 : 1;
    R['brow' + k].position.y = 0.155 + s.browLift * 0.06;
    R['brow' + k].rotation.z = sg * s.browAng * 0.4;
    const a = k === 'L' ? s.armL : s.armR;
    R['sh' + k].rotation.set(a[0], 0, sg * a[1]);
    R['el' + k].rotation.set(a[2], 0, 0);
    R['finger' + k].visible = !!(s.point && k === 'R');
  }
  R.legL.rotation.x = s.legs[0]; R.legR.rotation.x = s.legs[1];
  for (const k in R.mouths) R.mouths[k].visible = false;
  let m = s.mouth;
  if (m === 'parle') m = s.open > 0.12 ? 'ouvert' : 'plat';
  const mm = R.mouths[m] || R.mouths.plat; mm.visible = true;
  if (m === 'ouvert') mm.scale.set(0.8 + s.open * 0.4, 0.35 + s.open * 1.1, 1); else mm.scale.set(1, 1, 1);
}

/* ---------- PÂTES ---------- */
export function chat() {
  const root = new THREE.Group(); const R = { root };
  const o = toon(0xef8a2e), cr = toon(0xfbe3c4), d = toon(0xc4651c);
  root.add(mesh(S(0.34), o, [0, 0.3, 0], [0, 0, 0], [1.15, 0.9, 1]));
  root.add(mesh(S(0.22), cr, [0, 0.27, 0.2], [0, 0, 0], [1, 1, 0.6]));
  for (const s of [-1, 1]) root.add(mesh(S(0.1), o, [s * 0.16, 0.06, 0.22], [0, 0, 0], [1, 0.6, 1.3]));
  const tail = new THREE.Group(); tail.position.set(0.3, 0.2, -0.15); root.add(tail); R.tail = tail;
  for (let i = 0; i < 6; i++) tail.add(mesh(S(0.06 - i * 0.004), i === 5 ? d : o, [i * 0.07, i * 0.06, -i * 0.02]));
  const head = new THREE.Group(); head.position.set(0, 0.68, 0.06); root.add(head); R.head = head;
  head.add(mesh(S(0.28), o, [0, 0, 0], [0, 0, 0], [1.1, 0.95, 0.95]));
  for (const s of [-1, 1]) {
    head.add(mesh(new THREE.ConeGeometry(0.1, 0.18, 4), o, [s * 0.17, 0.24, 0], [0, Math.PI / 4, s * -0.3]));
    const eye = new THREE.Group(); eye.position.set(s * 0.11, 0.03, 0.23); head.add(eye);
    eye.add(mesh(S(0.065), toon(0xd6f27a), [0, 0, 0], [0, 0, 0], [1, 0.9, 0.5]));
    eye.add(mesh(BOX(0.018, 0.09, 0.02, 0.008), flat(0x111111), [0, 0, 0.03]));
    const lid = mesh(new THREE.SphereGeometry(0.07, 20, 12, 0, Math.PI * 2, 0, Math.PI / 2), o, [0, 0, 0], [0, 0, 0], [1, 1, 0.6]); eye.add(lid);
    R['lid' + (s < 0 ? 'L' : 'R')] = lid;
    for (const w of [-0.02, 0.02]) head.add(mesh(CYL(0.004, 0.004, 0.26, 4), flat(0x222222), [s * 0.24, -0.06 + w, 0.2], [0, 0, Math.PI / 2 + s * w * 4]));
  }
  head.add(mesh(S(0.12), cr, [0, -0.09, 0.2], [0, 0, 0], [1.1, 0.75, 0.6]));
  head.add(mesh(new THREE.ConeGeometry(0.03, 0.03, 3), toon(0xe8708f), [0, -0.04, 0.27], [Math.PI, 0, 0]));
  for (const x of [-0.06, 0, 0.06]) head.add(mesh(BOX(0.025, 0.08, 0.02, 0.008), d, [x, 0.2, 0.18], [0.4, 0, 0]));
  const mouth = mesh(S(0.045, 16, 12), toon(0x7a1f2b), [0, -0.12, 0.26], [0, 0, 0], [1, 0.1, 0.3]); head.add(mouth); R.mouth = mouth;
  root.traverse((c) => { if (c.isMesh) c.receiveShadow = false; });
  R.set = (st) => {
    const s = { lid: 0.5, blink: 0, head: [0, 0, 0], tail: 0, meow: 0, pos: [0, 0, 0], rot: [0, 0, 0], scale: 1, ...st };
    root.position.set(...s.pos); root.rotation.set(...s.rot); root.scale.setScalar(s.scale);
    head.rotation.set(...s.head);
    tail.rotation.set(0, 0, s.tail);
    const l = Math.max(s.lid, s.blink);
    R.lidL.rotation.x = R.lidR.rotation.x = lerp(-1.75, -0.05, l);
    mouth.scale.set(1, 0.1 + s.meow * 0.9, 0.3);
  };
  R.set({});
  return R;
}

/* ---------- ACCESSOIRES ---------- */
export function telephone(screenTex) {
  const g = new THREE.Group();
  g.add(mesh(BOX(0.16, 0.3, 0.025, 0.02), toon(0x1b1b1b), [0, 0, 0]));
  const scr = mesh(new THREE.PlaneGeometry(0.14, 0.27), flat(0x111111), [0, 0, 0.014]);
  if (screenTex) { scr.material.map = screenTex; scr.material.color.set(0xffffff); }
  g.add(scr); g.userData.screen = scr;
  return g;
}
export function nuggets() {
  const g = new THREE.Group();
  g.add(mesh(BOX(0.22, 0.14, 0.14, 0.02), toon(0xe23b3b), [0, 0.07, 0]));
  g.add(mesh(BOX(0.24, 0.03, 0.16, 0.01), toon(0xffd23f), [0, 0.15, 0]));
  for (const [x, z] of [[-0.05, 0], [0.04, 0.02], [0, -0.03]]) g.add(mesh(S(0.04, 12, 10), toon(0xd99a45), [x, 0.18, z], [0, 0, 0], [1.2, 0.7, 1]));
  return g;
}
export function linge(scale = 1) {
  const g = new THREE.Group();
  const cols = [0x5aa6d6, 0xf2d24a, 0xef5b93, 0x7bd389, 0xffffff, 0x9b7fd6];
  const pts = [[0, 0.12, 0, 0.35], [-0.3, 0.1, 0.1, 0.28], [0.3, 0.1, -0.05, 0.3], [0.05, 0.3, 0.05, 0.25], [-0.15, 0.25, -0.15, 0.22], [0.25, 0.25, 0.15, 0.2], [-0.35, 0.05, -0.2, 0.2]];
  pts.forEach(([x, y, z, r], i) => g.add(mesh(S(r, 20, 14), toon(cols[i % cols.length]), [x, y, z], [i, i * 2, 0], [1.3, 0.6, 1])));
  g.scale.setScalar(scale);
  return g;
}
export function pizzas(n = 3) {
  const g = new THREE.Group();
  const top = canvasTex(256, 256, (c, w, h) => { c.fillStyle = '#e8c08b'; c.fillRect(0, 0, w, h); c.fillStyle = '#b5462b'; c.font = '64px Anton'; c.textAlign = 'center'; c.fillText('PIZZA', w / 2, h / 2 + 22); c.strokeStyle = '#c99a63'; c.lineWidth = 8; c.strokeRect(14, 14, w - 28, h - 28); });
  for (let i = 0; i < n; i++) {
    const b = mesh(BOX(0.5, 0.07, 0.5, 0.01), toon(0xe0b47f), [i * 0.03, 0.035 + i * 0.075, i * 0.02], [0, i * 0.2, 0]);
    g.add(b);
    if (i === n - 1) g.add(mesh(new THREE.PlaneGeometry(0.46, 0.46), toon(0xffffff, { map: top, noOutline: true, unique: true }), [i * 0.03, 0.072 + i * 0.075, i * 0.02], [-Math.PI / 2, 0, i * 0.2]));
  }
  return g;
}
export function plante() {
  const g = new THREE.Group();
  g.add(mesh(CYL(0.16, 0.12, 0.28), toon(0xc9653c), [0, 0.14, 0]));
  for (const [rx, rz, l] of [[0.2, 0.3, 0.5], [-0.2, -0.4, 0.45], [0.1, -0.1, 0.6], [-0.3, 0.6, 0.35]]) {
    const st = mesh(CYL(0.012, 0.016, l, 5), toon(0x86622f), [Math.sin(rz) * l / 2, 0.28 + l / 2 * Math.cos(rz), Math.sin(rx) * l / 2], [rx, 0, rz]);
    g.add(st);
  }
  g.add(mesh(S(0.05, 8, 6), toon(0xa07b3a), [0.12, 0.62, 0], [0, 0, 0], [1, 0.3, 0.6]));
  return g;
}
export function guirlande(from, to, n = 10, sag = 0.25) {
  const g = new THREE.Group(); g.userData.bulbs = [];
  const cols = [0xffd23f, 0xff7aa8, 0x7fe0ff];
  const a = new THREE.Vector3(...from), b = new THREE.Vector3(...to);
  const pts = [];
  for (let i = 0; i <= 40; i++) { const t = i / 40; const p = a.clone().lerp(b, t); p.y -= Math.sin(t * Math.PI) * sag; pts.push(p); }
  g.add(new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 60, 0.006, 4), flat(0x222222)));
  for (let i = 1; i < n; i++) {
    const t = i / n; const p = a.clone().lerp(b, t); p.y -= Math.sin(t * Math.PI) * sag + 0.04;
    const m = new THREE.Mesh(S(0.035, 12, 10), new THREE.MeshBasicMaterial({ color: cols[i % 3] }));
    m.material.userData.outlineParameters = { visible: false };
    m.position.copy(p); g.add(m); g.userData.bulbs.push(m);
    const halo = new THREE.Sprite(new THREE.SpriteMaterial({ map: haloTex(), color: cols[i % 3], transparent: true, opacity: 0.5, depthWrite: false, blending: THREE.AdditiveBlending }));
    halo.scale.setScalar(0.3); halo.position.copy(p); g.add(halo); m.userData.halo = halo;
  }
  return g;
}
let _halo;
export function haloTex() {
  if (_halo) return _halo;
  _halo = canvasTex(128, 128, (g, w) => { const r = g.createRadialGradient(w / 2, w / 2, 0, w / 2, w / 2, w / 2); r.addColorStop(0, 'rgba(255,255,255,1)'); r.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = r; g.fillRect(0, 0, w, w); });
  return _halo;
}

/* ---------- DÉCORS ---------- */
export function chambre(opts = {}) {
  const g = new THREE.Group(); const R = { g };
  const wallTex = stripes('#3a2660', '#432d70', 14); wallTex.wrapS = wallTex.wrapT = THREE.RepeatWrapping; wallTex.repeat.set(2, 1);
  const wall = toon(0xffffff, { map: wallTex, noOutline: true, unique: true });
  const floorTex = canvasTex(512, 512, (c, w, h) => { c.fillStyle = '#6a4a3a'; c.fillRect(0, 0, w, h); c.strokeStyle = '#4e3428'; c.lineWidth = 6; for (let y = 0; y < h; y += 64) { c.beginPath(); c.moveTo(0, y); c.lineTo(w, y); c.stroke(); for (let x = (y / 64 % 2) * 120; x < w; x += 240) { c.beginPath(); c.moveTo(x, y); c.lineTo(x, y + 64); c.stroke(); } } });
  floorTex.wrapS = floorTex.wrapT = THREE.RepeatWrapping; floorTex.repeat.set(3, 3);
  g.add(mesh(new THREE.PlaneGeometry(8, 8), toon(0xffffff, { map: floorTex, noOutline: true, unique: true }), [0, 0, 0.5], [-Math.PI / 2, 0, 0], [1, 1, 1], { cast: false }));
  g.add(mesh(new THREE.PlaneGeometry(8, 4), wall, [0, 2, -2.5], [0, 0, 0], [1, 1, 1], { cast: false }));
  g.add(mesh(new THREE.PlaneGeometry(8, 4), wall, [-3.2, 2, 1.5], [0, Math.PI / 2, 0], [1, 1, 1], { cast: false }));
  g.add(mesh(new THREE.PlaneGeometry(8, 4), wall, [3.2, 2, 1.5], [0, -Math.PI / 2, 0], [1, 1, 1], { cast: false }));
  g.add(mesh(BOX(6.4, 0.12, 0.05, 0.01), toon(0x2a1b45), [0, 0.06, -2.47]));
  // fenêtre
  const sky = canvasTex(512, 640, (c, w, h) => {
    const gr = c.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#0d1433'); gr.addColorStop(1, '#2b3a78'); c.fillStyle = gr; c.fillRect(0, 0, w, h);
    c.fillStyle = '#fff'; for (let i = 0; i < 60; i++) { c.globalAlpha = Math.random() * 0.8 + 0.2; c.beginPath(); c.arc(Math.random() * w, Math.random() * h * 0.8, Math.random() * 2.5 + 0.5, 0, 7); c.fill(); }
    c.globalAlpha = 1; const m = c.createRadialGradient(360, 150, 20, 360, 150, 110); m.addColorStop(0, 'rgba(255,246,200,1)'); m.addColorStop(0.45, 'rgba(255,246,200,0.9)'); m.addColorStop(0.5, 'rgba(255,246,200,0.25)'); m.addColorStop(1, 'rgba(255,246,200,0)'); c.fillStyle = m; c.fillRect(200, 0, 320, 320);
    c.fillStyle = '#1b1f3f'; for (let x = 0; x < w; x += 70) { const hh = 90 + (x * 37 % 120); c.fillRect(x, h - hh, 60, hh); c.fillStyle = '#ffd86b'; for (let k = 0; k < 4; k++) if ((x + k) % 3) c.fillRect(x + 10 + (k % 2) * 25, h - hh + 15 + Math.floor(k / 2) * 30, 12, 14); c.fillStyle = '#1b1f3f'; }
  });
  R.skyMat = toon(0xffffff, { map: sky, emissive: 0xffffff, ei: 0.0, noOutline: true, unique: true });
  R.skyMat.emissiveMap = sky; R.skyMat.emissiveIntensity = 0.9;
  g.add(mesh(new THREE.PlaneGeometry(1.5, 1.8), R.skyMat, [1.2, 1.95, -2.48], [0, 0, 0], [1, 1, 1], { cast: false }));
  const fr = toon(0xe9e3d6);
  for (const [x, y, w, h] of [[1.2, 2.88, 1.62, 0.08], [1.2, 1.02, 1.62, 0.08], [0.43, 1.95, 0.08, 1.9], [1.97, 1.95, 0.08, 1.9], [1.2, 1.95, 0.05, 1.8], [1.2, 1.95, 1.5, 0.05]])
    g.add(mesh(BOX(w, h, 0.08, 0.02), fr, [x, y, -2.44]));
  g.add(mesh(BOX(1.7, 0.06, 0.25, 0.02), fr, [1.2, 0.98, -2.36]));
  // rideau ou jean
  R.rideau = new THREE.Group(); g.add(R.rideau);
  if (opts.rideau === 'jean') {
    const jm = toon(0x4f7fc4);
    R.rideau.add(mesh(BOX(0.55, 0.32, 0.08, 0.04), jm, [0.75, 2.62, -2.3]));
    for (const s of [-1, 1]) R.rideau.add(mesh(CAP(0.13, 1.0), jm, [0.75 + s * 0.14, 1.85, -2.3], [0, 0, s * 0.05]));
    R.rideau.add(mesh(BOX(0.56, 0.05, 0.09, 0.01), toon(0x355e9e), [0.75, 2.76, -2.3]));
    for (const s of [-1, 1]) R.rideau.add(mesh(BOX(0.05, 0.12, 0.05, 0.01), toon(0xffd23f), [0.75 + s * 0.22, 2.84, -2.28]));
  } else {
    const cm = toon(0x8c3a6a);
    for (let i = 0; i < 4; i++) R.rideau.add(mesh(CAP(0.09, 1.9), cm, [0.55 + i * 0.13, 1.85, -2.32]));
    R.rideau.add(mesh(CYL(0.025, 0.025, 1.9, 8), toon(0x3a2a2a), [1.2, 2.95, -2.3], [0, 0, Math.PI / 2]));
  }
  // lit
  const lit = new THREE.Group(); lit.position.set(-1.75, 0, -1.3); g.add(lit); R.lit = lit;
  lit.add(mesh(BOX(1.5, 0.35, 2.3, 0.05), toon(0x5b3b2c), [0, 0.18, 0]));
  lit.add(mesh(BOX(1.45, 0.22, 2.2, 0.1), toon(0xf1eefa), [0, 0.45, 0]));
  lit.add(mesh(BOX(1.5, 0.9, 0.12, 0.05), toon(0x5b3b2c), [0, 0.6, -1.15]));
  lit.add(mesh(BOX(0.6, 0.18, 0.4, 0.09), toon(0xefe9ff), [-0.3, 0.63, -0.85], [0.2, 0.2, 0]));
  R.couette = mesh(BOX(1.55, 0.25, 1.6, 0.12), toon(0x9b7fd6), [0, 0.6, 0.3], [0, 0, 0.02]);
  lit.add(R.couette);
  // table de nuit + bureau
  g.add(mesh(BOX(0.5, 0.5, 0.45, 0.03), toon(0x5b3b2c), [-0.65, 0.25, -2.15]));
  R.bureau = new THREE.Group(); R.bureau.position.set(2.3, 0, -1.9); g.add(R.bureau);
  R.bureau.add(mesh(BOX(1.3, 0.06, 0.7, 0.02), toon(0x6b4632), [0, 0.78, 0]));
  for (const [x, z] of [[-0.6, -0.3], [0.6, -0.3], [-0.6, 0.3], [0.6, 0.3]]) R.bureau.add(mesh(CYL(0.03, 0.03, 0.78, 8), toon(0x4a2f22), [x, 0.39, z]));
  const lap = new THREE.Group(); lap.position.set(-0.1, 0.81, 0.05); R.bureau.add(lap);
  lap.add(mesh(BOX(0.5, 0.025, 0.34, 0.01), toon(0x2c2c34), [0, 0.012, 0]));
  const scr = new THREE.Group(); scr.position.set(0, 0.02, -0.16); scr.rotation.x = -0.25; lap.add(scr);
  scr.add(mesh(BOX(0.5, 0.33, 0.02, 0.01), toon(0x2c2c34), [0, 0.165, 0]));
  R.lapScreen = new THREE.MeshBasicMaterial({ color: 0x7fd0ff }); R.lapScreen.userData.outlineParameters = { visible: false };
  scr.add(new THREE.Mesh(new THREE.PlaneGeometry(0.46, 0.29), R.lapScreen)).position.set(0, 0.165, 0.012);
  R.bureau.add(mesh(CYL(0.05, 0.045, 0.1, 16), toon(0xf1f1f1), [0.4, 0.86, 0.1]));
  // chaise gamer
  // poster K-drama + calendrier
  const poster = canvasTex(400, 520, (c, w, h) => { c.fillStyle = '#ef5b93'; c.fillRect(0, 0, w, h); c.fillStyle = '#ffd23f'; c.beginPath(); c.arc(w / 2, 190, 120, 0, 7); c.fill(); c.strokeStyle = '#151515'; c.lineWidth = 10; c.stroke(); c.beginPath(); c.moveTo(130, 210); c.lineTo(170, 150); c.lineTo(210, 210); c.lineTo(250, 150); c.stroke(); c.fillStyle = '#fff'; c.font = '86px Anton'; c.textAlign = 'center'; c.fillText('K-DRAMA', w / 2, 440); });
  g.add(mesh(new THREE.PlaneGeometry(0.85, 1.1), toon(0xffffff, { map: poster, unique: true }), [-3.18, 2.0, -0.5], [0, Math.PI / 2, 0.06]));
  const cal = canvasTex(300, 300, (c, w, h) => { c.fillStyle = '#fff'; c.fillRect(0, 0, w, h); c.fillStyle = '#e23b3b'; c.fillRect(0, 0, w, 70); c.fillStyle = '#fff'; c.font = '46px Anton'; c.textAlign = 'center'; c.fillText('NOVEMBRE', w / 2, 52); c.fillStyle = '#ddd'; for (let r = 0; r < 4; r++) for (let k = 0; k < 6; k++) c.fillRect(18 + k * 46, 90 + r * 50, 34, 34); c.fillStyle = '#e23b3b'; c.font = '90px Anton'; c.fillText('30', 210, 280); });
  g.add(mesh(new THREE.PlaneGeometry(0.55, 0.55), toon(0xffffff, { map: cal, unique: true }), [-0.4, 1.9, -2.47]));
  // guirlande
  R.guirlande = guirlande([-3.1, 2.75, -2.4], [0.3, 2.75, -2.4], 12, 0.3); g.add(R.guirlande);
  // désordre
  R.pizzas = pizzas(3); R.pizzas.position.set(-0.9, 0, 0.4); g.add(R.pizzas);
  R.linge = linge(1); R.linge.position.set(1.6, 0, 0.3); g.add(R.linge);
  R.plante = plante(); R.plante.position.set(2.75, 0, -0.9); g.add(R.plante);
  R.nuggets = nuggets(); R.nuggets.position.set(0.35, 0, 0.95); R.nuggets.rotation.y = 0.4; g.add(R.nuggets);
  for (const [x, z, r] of [[-0.3, 1.4, 0.3], [0.9, -0.6, 1.2]]) { const c = mesh(CYL(0.04, 0.04, 0.12, 12), toon(0xe23b3b), [x, 0.04, z], [Math.PI / 2, 0, r]); g.add(c); }
  return R;
}

export function salleDeBain() {
  const g = new THREE.Group(); const R = { g };
  const tiles = canvasTex(512, 512, (c, w, h) => { c.fillStyle = '#4fa6a0'; c.fillRect(0, 0, w, h); c.fillStyle = '#5fb7b0'; for (let y = 0; y < 8; y++) for (let x = 0; x < 8; x++) c.fillRect(x * 64 + 3, y * 64 + 3, 58, 58); });
  tiles.wrapS = tiles.wrapT = THREE.RepeatWrapping; tiles.repeat.set(4, 2);
  const tm = toon(0xffffff, { map: tiles, noOutline: true, unique: true });
  g.add(mesh(new THREE.PlaneGeometry(8, 4), tm, [0, 2, -1.6], [0, 0, 0], [1, 1, 1], { cast: false }));
  g.add(mesh(new THREE.PlaneGeometry(8, 8), toon(0xd9cfc2, { noOutline: true }), [0, 0, 2], [-Math.PI / 2, 0, 0], [1, 1, 1], { cast: false }));
  g.add(mesh(BOX(0.8, 0.06, 0.25, 0.02), toon(0xece9e4), [-1.5, 2.3, -1.45]));
  g.add(mesh(CYL(0.06, 0.06, 0.25, 12), toon(0xff8fb7), [-1.65, 2.45, -1.45]));
  g.add(mesh(CYL(0.05, 0.05, 0.3, 12), toon(0x9be07a), [-1.4, 2.48, -1.45]));
  const rid = toon(0xf6d1e3);
  for (let i = 0; i < 5; i++) g.add(mesh(CAP(0.1, 2.2), rid, [1.4 + i * 0.17, 1.6, -1.3]));
  return R;
}

export function lycee() {
  const g = new THREE.Group(); const R = { g };
  g.add(mesh(new THREE.PlaneGeometry(14, 14), toon(0x8a6a4a, { noOutline: true }), [0, 0, 0], [-Math.PI / 2, 0, 0], [1, 1, 1], { cast: false }));
  g.add(mesh(new THREE.PlaneGeometry(14, 6), toon(0x2b2050, { noOutline: true }), [0, 3, -4], [0, 0, 0], [1, 1, 1], { cast: false }));
  const ban = canvasTex(1024, 220, (c, w, h) => { c.fillStyle = '#e84f8a'; c.fillRect(0, 0, w, h); c.fillStyle = '#fff'; c.font = '140px Anton'; c.textAlign = 'center'; c.fillText('BAL DE FIN D\'ANNÉE 2016', w / 2, 168); });
  g.add(mesh(new THREE.PlaneGeometry(4.4, 0.95), toon(0xffffff, { map: ban, unique: true, emissive: 0x330011, ei: 0.4 }), [0, 3.6, -3.95]));
  R.g1 = guirlande([-5, 4.4, -3.9], [0, 3.2, -1], 14, 0.4); g.add(R.g1);
  R.g2 = guirlande([5, 4.4, -3.9], [0, 3.2, -1], 14, 0.4); g.add(R.g2);
  R.disco = new THREE.Group(); R.disco.position.set(0, 4.1, -1.6); g.add(R.disco);
  R.disco.add(mesh(new THREE.IcosahedronGeometry(0.35, 2), toon(0xcfd6e6, { emissive: 0x334455, ei: 0.6 })));
  for (let i = 0; i < 4; i++) g.add(mesh(CYL(0.25, 0.25, 0.9, 20), toon([0xffd23f, 0xff7aa8, 0x7fe0ff, 0x9be07a][i]), [-3 + i * 2, 0.45, -3.2]));
  // table avec punch
  g.add(mesh(BOX(1.6, 0.08, 0.7, 0.02), toon(0xffffff), [3, 0.8, -2.5]));
  g.add(mesh(CYL(0.25, 0.2, 0.3, 20), toon(0xff5c8a, { transparent: true, opacity: 0.85 }), [3, 1.0, -2.5]));
  return R;
}

export function couloir() {
  const g = new THREE.Group(); const R = { g };
  g.add(mesh(new THREE.PlaneGeometry(8, 8), toon(0x3e2c3a, { noOutline: true }), [0, 0, 0], [-Math.PI / 2, 0, 0], [1, 1, 1], { cast: false }));
  g.add(mesh(new THREE.PlaneGeometry(8, 4), toon(0x352450, { noOutline: true }), [0, 2, -1], [0, 0, 0], [1, 1, 1], { cast: false }));
  R.porte = mesh(BOX(1.1, 2.2, 0.08, 0.02), toon(0x7b4a2e), [0, 1.1, -0.95]);
  g.add(R.porte);
  for (const [y] of [[0.6], [1.6]]) g.add(mesh(BOX(0.8, 0.6, 0.02, 0.02), toon(0x6a3f27), [0, y, -0.9]));
  g.add(mesh(S(0.05, 12, 10), toon(0xd9b14a), [0.42, 1.05, -0.88]));
  g.add(mesh(CYL(0.03, 0.03, 0.03, 12), toon(0x222222), [0, 1.62, -0.9], [Math.PI / 2, 0, 0]));
  R.fente = new THREE.Mesh(new THREE.PlaneGeometry(1.1, 0.05), new THREE.MeshBasicMaterial({ color: 0xfff1b8 }));
  R.fente.material.userData.outlineParameters = { visible: false }; R.fente.position.set(0, 0.012, -0.9); R.fente.rotation.x = -Math.PI / 2; g.add(R.fente);
  R.ombres = new THREE.Group(); g.add(R.ombres);
  for (const s of [-1, 1]) { const o = new THREE.Mesh(new THREE.PlaneGeometry(0.16, 0.06), new THREE.MeshBasicMaterial({ color: 0x000000 })); o.material.userData.outlineParameters = { visible: false }; o.position.set(s * 0.12, 0.013, -0.9); o.rotation.x = -Math.PI / 2; R.ombres.add(o); }
  // tapis
  g.add(mesh(BOX(1.3, 0.02, 0.7, 0.01), toon(0xe23b3b), [0, 0.01, -0.3]));
  return R;
}
