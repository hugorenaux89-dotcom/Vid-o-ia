// Épisode 1 — version 2D du nouveau script (voix locale), habillage partagé avec ep3d.js
const A = require('./art');
const B = require('./art2');
const E3 = require('./ep3d');
const E1 = require('./ep01');
const { tw, easeOut, easeBack, blinkAt, popS, clamp, POSES, lerp } = A;
const { TL, wt, vstart: vs, vend: ve } = E3;
const env = E3.init().env;

const amp = (p, t, qui = 'lana') => { for (const v of p.voices) if (v.voix === qui && t >= v.start && t < v.start + v.dur) { const a = env[v.id]; return a[Math.min(a.length - 1, Math.floor((t - v.start) * 30))] || 0; } return 0; };
const VIG = `<rect width="720" height="1280" fill="url(#vig)"/>`;
const assise = (P, t) => A.lana({ ...P, t, y: (P.y || 0) + 70, s: P.s || 0.95 });
const couchee = (P, cx = 380, cy = 870, s = 0.62) => `<g transform="translate(${cx} ${cy}) rotate(-90) scale(${s}) translate(-360 -800)">${A.lana(P)}</g>`;
function litCote(t) {
  return `<g filter="url(#sh)"><rect x="30" y="690" width="50" height="330" rx="10" fill="#5b3b2c" ${A.O(6)}/>
   <rect x="30" y="905" width="660" height="90" rx="16" fill="#f1eefa" ${A.O(7)}/><rect x="30" y="990" width="660" height="60" rx="10" fill="#5b3b2c" ${A.O(6)}/>
   <path d="M90 905 q20 -50 110 -40 q70 0 70 40z" fill="#efe9ff" ${A.O(6)}/></g>`;
}
const draps = (x0 = 470, y0 = 850) => `<g filter="url(#sh)"><path d="M${x0} ${y0 + 60} q20 -70 110 -60 q90 0 110 70 v70 h-220z" fill="#9b7fd6" ${A.O(7)}/><path d="M${x0 + 30} ${y0 + 40} q60 -30 120 0" fill="none" stroke="#7d62bd" stroke-width="6"/></g>`;
const lueur = (x, y, r = 160, o = 0.7) => `<circle cx="${x}" cy="${y}" r="${r}" fill="url(#glow)" opacity="${o}"/>`;

const R = {};

/* 1. ACCROCHE */
R.hook = (t, p) => {
  const tA2 = vs(p, 'a2'), tCa = wt(p, 'ça');
  if (t < tA2) {
    const P = { blink: blinkAt(t, 1), lid: 0.45, look: [8, 10], phone: true, armR: POSES.phone, mouth: 'sourire', eyes: 'normal', headRot: 4, blush: 1.6 };
    const scene = A.chambre(t, { lit: 'lump', linge: false, nuggets: false }) + B.litFond(t) + assise(P, t) + B.couette(t) + B.nuit(0.55) + lueur(540, 700, 200, 0.8) + VIG;
    return A.camera(scene, 360, 700, tw(t, 0, tA2, 1.0, 1.15));
  }
  const tf = Math.min(t, tCa);
  const P = { t: tf, blink: 0, lid: 0.55, look: [4, 0], mouth: 'o', armR: [-30 + Math.sin(tf * 14) * 4, -150 + Math.sin(tf * 14) * 8], armL: POSES.bas, headRot: 6 + Math.sin(tf * 2) * 2, browLift: 2 };
  const scene = A.chambre(tf) + A.odeurs(tf) + A.lana(P) + VIG;
  const z = t > tCa ? 1 + 0.06 * easeOut((t - tCa) / 0.2) : tw(t, tA2, tA2 + 0.3, 1.12, 1.0, easeOut);
  const gris = t > tCa ? `<rect width="720" height="1280" fill="#000" opacity=".12"/>` : '';
  return A.camera(scene, 360, 660, z) + gris;
};

/* 2. RECORD */
R.record = (t, p) => {
  const P = { t, blink: blinkAt(t, 2), lid: 0.55, look: [0, 8], mouth: 'plat', armL: [100, -60], armR: [100, -60] };
  const laptop = `<g transform="translate(445 830) rotate(-90)" filter="url(#sh)"><rect x="-70" y="-6" width="140" height="14" rx="4" fill="#2c2c34" ${A.O(5)}/><path d="M-66 -6 l10 -90 h112 l10 90z" fill="#2c2c34" ${A.O(5)}/><path d="M-56 -12 l8 -76 h96 l8 76z" fill="#9fdcff"/></g>`;
  const scene = A.chambre(t, { lit: 'lump', linge: false, nuggets: false }) + litCote(t) + couchee(P) + draps(500, 830) + laptop + lueur(330, 860, 140, 0.6) +
    A.chat(620, 1110, 0.55, { t, blink: blinkAt(t, 5), lid: 0.6 }) + A.odeurs(t, [[200, 760], [520, 760], [600, 960]]) + VIG;
  return A.camera(scene, 380, 820, tw(t, 0, p.dur, 1.05, 1.18));
};

/* 3. LE LIVREUR */
R.livreur = (t, p) => {
  const tD = wt(p, 'demandé'), tB = wt(p, 'bien');
  const worry = clamp((t - tD) / 0.3);
  const take = clamp((t - (tB + 0.15)) / 0.5);
  const PL = { t, blink: blinkAt(t, 3), lid: 0.55, look: [8, 0], mouth: 'plat', armR: take > 0 ? POSES.phone : POSES.bas, x: -175, s: 0.78 };
  const box = `<g transform="translate(${lerp(530, 250, easeOut(take))} ${lerp(992, 1005, take)})" filter="url(#sh)"><rect x="-150" y="-20" width="300" height="40" rx="5" fill="#e8c08b" ${A.O(5)}/><text x="0" y="10" font-family="Anton" font-size="22" fill="#b5462b" text-anchor="middle">PIZZA</text></g>`;
  const scene = B.couloir(t, { ouverte: 1 }) + A.lana(PL) + B.livreur({ t, x: 175, s: 0.8, worry, blink: blinkAt(t, 7), boite: false }) + box + VIG;
  return A.camera(scene, 360, 800, tw(t, 0, p.dur, 1.02, 1.12));
};

/* 4. PÂTES */
R.pates = (t, p) => {
  const tL = wt(p, 'aime'), tC = wt(p, 'croquettes');
  const o = { t, blink: blinkAt(t, 4), lid: 0.5, headRot: Math.sin(t * 0.8) * 3, lookX: 0, meow: 0 };
  if (t > tL - 0.2) { o.headRot = tw(t, tL - 0.2, tL + 0.2, 0, -22); o.lookX = -6; }
  if (t > tC - 0.15) { o.headRot = tw(t, tC - 0.15, tC + 0.2, -22, 14); o.lookX = 6; o.lid = tw(t, tC - 0.15, tC + 0.1, 0.5, 0); o.meow = Math.sin(clamp((t - tC) / 0.6) * Math.PI); }
  const k = clamp(t / 0.7) - clamp((t - tL) / 0.4);
  const main = `<g transform="translate(${lerp(-220, 60, easeOut(k))} ${560 + Math.sin(t * 8) * 6 * k})"><path d="M-200 0 H130" stroke="${A.K}" stroke-width="66" stroke-linecap="round"/><path d="M-200 0 H130" stroke="${A.C.pink}" stroke-width="52" stroke-linecap="round"/><circle cx="150" cy="0" r="32" fill="${A.C.skin}" ${A.O(6)}/></g>`;
  const bol = `<g transform="translate(570 1035)" filter="url(#sh)"><path d="M-80 -20 h160 l-20 50 h-120z" fill="#43c3ff" ${A.O(6)}/>${[-50, -25, 0, 25, 50, -35, 12, 38].map((x, i) => `<circle cx="${x}" cy="${-24 - (i > 4 ? 12 : 0)}" r="11" fill="#8a5a2b" ${A.O(3)}/>`).join('')}</g>`;
  const scene = A.chambre(t, { lit: 'lump', linge: false, nuggets: false }) + B.litFond(t) + B.couette(t, 1060) + A.chat(360, 860, 1.9, o) + bol + main + VIG;
  return A.camera(scene, 360, 760, tw(t, 0, p.dur, 1.0, 1.1));
};

/* 5. LA NUIT */
R.nuit = (t, p) => {
  const tV = wt(p, 'vibre');
  const P = { t, blink: 0, lid: 1, mouth: 'soupir', look: [0, 0], armL: POSES.bas, armR: POSES.bas };
  const draps2 = `<g filter="url(#sh)"><path d="M230 820 q40 -30 120 -20 q180 -10 340 20 v120 h-460z" fill="#9b7fd6" ${A.O(7)}/></g>`;
  const scene = A.chambre(t, { lit: 'lump', linge: false, nuggets: false }) + litCote(t) + couchee(P) + draps2 +
    B.tableDeNuit(t, { x: 540, y: 1010, ecran: t > tV, vibre: t > tV && Math.sin(t * 6) > 0 }) + B.nuit(1) + (t > tV ? lueur(625, 990, 200, 0.9) : '') + B.zzz(t, 230, 760) + VIG;
  return A.camera(scene, tw(t, 0, p.dur, 380, 420), tw(t, 0, p.dur, 860, 900), tw(t, 0, p.dur, 1.0, 1.15));
};

/* 6. LE MESSAGE D'INÈS */
R.message = (t, p) => {
  const t3 = vs(p, 'e3');
  const froid = clamp((t - t3) / 0.6);
  const P = { blink: blinkAt(t, 2), lid: lerp(0.6, 0.4, froid), look: [8, 10], phone: true, armR: POSES.phone, mouth: froid > 0.5 ? 'tordu' : 'plat', browAng: 10 * froid, headRot: 3 };
  const scene = A.chambre(t, { lit: 'lump', linge: false, nuggets: false }) + B.litFond(t) + assise(P, t) + B.couette(t) + B.nuit(0.6) + lueur(540, 720, 220, 0.85) + VIG;
  return A.camera(scene, 380, tw(t, 0, p.dur, 800, 700), tw(t, 0, p.dur, 1.05, 1.35));
};

/* 7. LE REFUS + 2E MESSAGE */
R.refus = (t, p) => {
  const e1 = ve(p, 'f1'), tF2 = vs(p, 'f2'), tF3 = vs(p, 'f3');
  const a = amp(p, t);
  let P = { blink: blinkAt(t, 3), lid: 0.4, look: [0, 4], phone: true, armR: POSES.phone, mouth: 'parle', open: a, browAng: 14, headRot: 0 };
  let phone = '';
  const thrown = t > e1 - 0.1 && t < tF3 + 0.5;
  if (thrown) {
    const k = clamp((t - (e1 - 0.1)) / 0.45);
    P = { ...P, phone: false, armR: POSES.croise, armL: POSES.croise, headRot: lerp(0, -12, easeOut(k)), look: [-10, 0], lid: 0.5, mouth: 'tordu' };
    const buzz = t > tF2 - 0.2 && t < tF2 + 1.2 ? Math.sin(t * 90) * 4 : 0;
    phone = A.telephone(lerp(540, 590, k) + buzz, lerp(760, 1060, easeOut(k)) - Math.sin(k * Math.PI) * 160, k * 300, 0.5, t) + (t > tF2 - 0.2 ? lueur(590, 1050, 150, 0.8) : '');
    if (t > tF2) P = { ...P, look: [lerp(-10, 10, clamp((t - tF2) / 0.4)), 8], lid: tw(t, tF2, tF2 + 0.3, 0.5, 0.1), browAng: 0, browLift: -6 };
  }
  if (t >= tF3 + 0.5) P = { ...P, phone: true, armR: POSES.phone, armL: POSES.bas, look: [8, 10], lid: 0.1, browLift: -10, browAng: 0, mouth: 'o', headRot: 2 };
  const scene = A.chambre(t, { lit: 'lump', linge: false, nuggets: false }) + B.litFond(t) + assise(P, t) + B.couette(t) + phone + B.nuit(0.6) + (P.phone ? lueur(540, 720, 220, 0.85) : '') + VIG;
  return A.camera(scene, 370, 760, 1.18);
};

/* 8. LE CRI */
R.cri = (t, p) => {
  const a = amp(p, t);
  const k = easeOut(t / 0.15);
  const P = { blink: 0, lid: 0, eyes: 'grand', look: [0, 0], armL: [lerp(78, -48, k), lerp(92, -84, k)], armR: [lerp(58, -48, k), lerp(-98, -84, k)], mouth: 'parle', open: Math.max(0.55, a), browLift: -24, sweat: true, headRot: Math.sin(t * 40) * 2, y: -30 * Math.sin(clamp(t / 0.3) * Math.PI) };
  const scene = A.chambre(t, { lit: 'lump', linge: false, nuggets: false }) + B.litFond(t) + assise(P, t) + B.couette(t) + B.nuit(0.4) + VIG;
  const [sx, sy] = A.shake(t, 0, 0.9, 18);
  return A.camera(scene, 360, 640, lerp(1.0, 1.35, easeOut(t / 0.25)), sx, sy);
};

/* 9. LE BAL */
R.bal = (t, p) => {
  const tJ = vs(p, 'g2');
  const sad = clamp((t - tJ) / 1.2);
  const P = { t, teen: true, blink: blinkAt(t, 8), lid: lerp(0.05, 0.5, sad), look: [lerp(-10, 0, sad), lerp(0, 10, sad)], mouth: sad > 0.3 ? 'plat' : 'sourire', eyes: 'normal', armL: POSES.cadeau, armR: POSES.cadeau, headRot: lerp(-6 + Math.sin(t * 0.7) * 4, 6, sad), browAng: -10 * sad, s: 0.82, y: 0 };
  const hands = A.handPos('R', ...POSES.cadeau);
  const scene = B.bal(t, sad) + A.lana(P) + B.cadeau(360, 1230 + (hands[1] - 1230) * 0.82 + 10) + VIG;
  return A.camera(scene, 360, lerp(700, 760, sad), lerp(tw(t, 0, tJ, 1.0, 1.12), 0.92, easeOut(sad)));
};

/* 10. LA DÉCISION */
R.decision = (t, p) => {
  const a = amp(p, t);
  const k = clamp((t - 0.15) / 0.3), k2 = clamp((t - 0.9) / 0.3);
  const P = { t, blink: blinkAt(t, 9), lid: 0.22, browAng: 14, mouth: a > 0.05 ? 'parle' : 'dents', open: a, armL: [lerp(78, 100, k), lerp(92, -80, k)], armR: [lerp(78, 100, k2), lerp(92, -80, k2)], armLopt: { fist: true }, armRopt: { fist: true } };
  const scene = A.chambre(t, { linge: true }) + A.lana(P) + B.matin(1) + VIG;
  return A.camera(scene, 360, tw(t, 0, p.dur, 760, 640), tw(t, 0, p.dur, 1.0, 1.25));
};

/* 11. LA CHUTE */
R.chute = (t, p) => {
  const tSlip = ve(p, 'h2') + 0.05, tLand = tSlip + 0.55;
  let inner;
  if (t < tLand) {
    const walk = clamp(t / tSlip);
    const P = { t, blink: blinkAt(t, 5), lid: 0.2, browAng: 10, mouth: 'sourire', eyes: 'normal', armL: [78 + Math.sin(t * 3) * 14, 92], armR: [78 - Math.sin(t * 3) * 14, 92], headRot: Math.sin(t * 1.7) * 2, s: lerp(0.8, 0.98, walk), y: -Math.abs(Math.sin(t * 3)) * 8, rot: Math.sin(t * 3) * 2 };
    let x = 0, rot = P.rot, y = P.y;
    if (t > tSlip) {
      const k = clamp((t - tSlip) / 0.55);
      rot = 95 * easeOut(k) * 0.9; x = 140 * k; y = -60 * Math.sin(k * Math.PI);
      Object.assign(P, { eyes: 'grand', mouth: 'cri', lid: 0, browLift: -20, armL: POSES.haut, armR: POSES.salut });
    }
    P.x = x; P.y = y; P.rot = rot;
    const nug = t > tSlip ? A.nuggets(330 + (t - tSlip) * 300, 1235 - Math.sin(clamp((t - tSlip) / 0.7) * Math.PI) * 400, (t - tSlip) * 720, 1.2) : A.nuggets(360, 1250, -8);
    inner = A.chambre(t, { nuggets: false }) + A.odeurs(t) + A.lana(P) + nug + B.matin(1);
  } else {
    const k = t - tLand;
    const sway = Math.sin(k * 5) * 6 * Math.exp(-k * 0.8);
    const legs = `<g transform="rotate(${sway.toFixed(2)} 520 1080)">${[[470, -18], [570, 16]].map(([x, r]) => `<g transform="rotate(${r} ${x} 1060)"><rect x="${x - 40}" y="880" width="80" height="190" rx="20" fill="${A.C.pink}" ${A.O(7)}/>
        <ellipse cx="${x}" cy="880" rx="62" ry="32" fill="#fff" ${A.O(7)}/><path d="M${x - 8} 852 l10 -32 l10 32z" fill="#ffd23f" ${A.O(4)}/><circle cx="${x - 18}" cy="874" r="5" fill="${A.K}"/><circle cx="${x + 18}" cy="874" r="5" fill="${A.K}"/></g>`).join('')}</g>`;
    const stars = A.etoiles(t, [0, 2.1, 4.2].map((ph) => [520 + Math.cos(t * 5 + ph) * 90, 840 + Math.sin(t * 5 + ph) * 25, 0.9]));
    inner = A.chambre(t, { linge: false, nuggets: false }) + A.odeurs(t) + legs + A.linge(1.8, -90, 40) + stars + A.nuggets(470, Math.min(870, 500 + k * 1400), 12, 1.1) + B.matin(1);
  }
  const [sx, sy] = A.shake(t, tLand, 0.45, 20);
  return A.camera(`<rect width="720" height="1280" fill="#2a1b45"/>` + inner + VIG, 360, t < tLand ? 700 : 720, t < tLand ? tw(t, 0, tSlip, 1.0, 1.08) : 1.15, sx, sy);
};

/* 12. LE MIROIR */
R.miroir = (t, p) => {
  const tToi = wt(p, 'toi'), tC = wt(p, 'Chaque');
  let P = { t, blink: blinkAt(t, 6), lid: 0.35, look: [0, -10], mouth: 'tordu', armL: POSES.tete, armR: POSES.bas, headRot: Math.sin(t) * 3, browLift: -6 };
  if (t > 1.6) P = { ...P, armL: POSES.bas, look: [0, 0], mouth: 'soupir' };
  if (t > tToi - 0.15) P = { ...P, armR: POSES.pointe, armRopt: { point: true }, mouth: 'sourire', eyes: 'normal', lid: 0.1, browLift: -12 };
  if (t > tC) P = { ...P, armR: POSES.croise, armL: POSES.croise, armRopt: {}, mouth: 'plat', browAng: 8, eyes: undefined, lid: 0.3, headRot: Math.sin(t * 3) * 1.5 };
  const z = t > tToi ? 1.08 + 0.12 * easeOut((t - tToi) / 0.3) : tw(t, 0, tToi, 1.0, 1.08);
  return A.camera(A.salleDeBain(t) + A.lana(P) + VIG, 360, 700, z);
};

/* 13. LE VOTE — scène de l'épisode d'origine */
R.vote = (t, p) => E1.R.vote(t, p);

/* 14. APPEL AU VOTE */
R.cta = (t, p) => {
  const wave = Math.sin(t * 7) * 18;
  const P = { t, blink: blinkAt(t, 8), lid: 0.2, mouth: 'sourire', eyes: 'normal', armL: POSES.bas, armR: [-30 + wave * 0.3, -100 + wave], headRot: Math.sin(t * 1.5) * 3, browLift: -6, s: 0.9, y: 30 };
  const scene = A.chambre(t) + A.odeurs(t) + A.lana(P) + A.chat(205, 735, 0.62, { t, blink: blinkAt(t, 9), lid: 0.5, headRot: -6 + Math.sin(t) * 3 }) + VIG;
  return A.camera(scene, 360, 660, tw(t, 0, p.dur, 1.0, 1.06));
};

/* 15. QUELQU'UN SONNE */
R.porte = (t, p) => {
  const tS = wt(p, 'sonne');
  const scene = B.couloir(t, { fente: true, pieds: t > tS - 0.3, sonnette: t > tS && t < tS + 1 }) + B.nuit(0.7) + `<path d="M150 1072 L120 1280 H600 L570 1072 Z" fill="#fff1b8" opacity=".15"/>` + VIG;
  const [sx, sy] = A.shake(t, tS, 0.35, 6);
  return A.camera(scene, 360, 760, tw(t, 0, p.dur, 1.0, 1.35), sx, sy);
};

/* habillage : reprend celui de ep3d, avec quelques ajustements 2D */
const Over = { ...E3.O };
Over.hook = (t, p) => {
  const tA2 = vs(p, 'a2'), tCa = wt(p, 'ça'), end = ve(p, 'a2');
  let s = E3.O.hook(Math.min(t, tCa - 0.001), p);
  if (t > tCa) {
    s = '';
    const k = t - tCa;
    s += `<rect width="720" height="1280" fill="#fff" opacity="${(0.6 * (1 - clamp(k / 0.15))).toFixed(2)}"/>`;
    s += A.pop(360, 1190, popS(t, tCa, 0.25), A.titre0(0, [['ÇA. 👆', '#ff4d5e']], 120), -3);
    s += E3.fleche(160, 330, 330, 400, 'CHIGNON NID D\'OISEAU', popS(t, tCa + 0.3, 0.3), A.C.yellow);
    s += E3.fleche(560, 440, 440, 520, 'SOURCILS SAUVAGES', popS(t, tCa + 0.55, 0.3), '#ff8fc8');
    s += E3.fleche(560, 1010, 430, 920, 'PYJAMA DEPUIS 2023', popS(t, tCa + 0.8, 0.3), '#7fe0ff');
    s += A.hud(30, 0);
  }
  return s;
};
Over.vote = (t, p) => E3.sousTitres(t, p, 900);

const frameAt = (T) => {
  const p = E3.plan(T); const t = T - p.start;
  return A.DEFS + `<rect width="720" height="1280" fill="#1b1230"/>` + R[p.id](t, p) + E3.habillage(T, Over);
};
module.exports = { TL, frameAt };
