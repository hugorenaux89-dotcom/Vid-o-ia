// Épisode 1 — scènes animées, synchronisées sur la voix off
const fs = require('fs');
const path = require('path');
const A = require('./art');
const { tw, easeOut, easeBack, blinkAt, popS, clamp, POSES } = A;

const VOIX = path.join(__dirname, '../build/ep01/voix');
const voix = (id) => JSON.parse(fs.readFileSync(path.join(VOIX, id + '.json'), 'utf8'));

// Scènes : segments de voix (id, début local), durée totale
const SCENES = [
  { id: 'telephone', segs: [['s1', 0.7]], tail: 0.5 },
  { id: 'couette', segs: [['s2', 0.35]], tail: 0.45 },
  { id: 'presentation', segs: [['s3', 0.3]], tail: 0.55 },
  { id: 'pates', segs: [['s4', 0.3]], tail: 0.8 },
  { id: 'message', segs: [['s5', 0.3]], tail: 1.2 },
  { id: 'lycee', segs: [['s5b', 0.6]], tail: 0.3 },
  { id: 'jean', segs: [['s5c', 0.25]], tail: 0.6 },
  { id: 'chute', segs: [['s6a', 0.25], ['s6b', 0]], gap: 1.7, tail: 0.7 },
  { id: 'miroir', segs: [['s7', 0.4]], tail: 0.6 },
  { id: 'vote', segs: [['s8', 0.3]], tail: 0.8 },
  { id: 'fin', segs: [['s9', 0.3]], tail: 1.6 },
];

function construireTimeline() {
  let T = 0;
  const out = [];
  for (const sc of SCENES) {
    const words = [];
    const voices = [];
    let local = 0;
    sc.segs.forEach(([id, lead], i) => {
      const v = voix(id);
      local += i === 0 ? lead : sc.gap || 0;
      voices.push({ id, start: local });
      v.words.forEach((w) => words.push({ w: w.w, s: w.s + local, e: w.e + local, seg: id }));
      local += v.dur;
    });
    const dur = local + sc.tail;
    out.push({ ...sc, start: T, dur, words, voices });
    T += dur;
  }
  return { scenes: out, total: T };
}
const TL = construireTimeline();
const S = Object.fromEntries(TL.scenes.map((s) => [s.id, s]));
// temps (local) du mot contenant `txt` (n-ième occurrence)
function wt(sc, txt, n = 0, which = 's') {
  const m = sc.words.filter((w) => w.w.toLowerCase().includes(txt.toLowerCase()));
  if (!m[n]) throw new Error(`mot introuvable: ${txt} dans ${sc.id}`);
  return m[n][which];
}

// Transition d'entrée : petit zoom-punch + flash
function entree(t, inner) {
  const z = 1 + 0.06 * (1 - easeOut(t / 0.35));
  return `<g transform="translate(360 640) scale(${z.toFixed(4)}) translate(-360 -640)">${inner}</g>` +
    (t < 0.12 ? `<rect width="720" height="1280" fill="#fff" opacity="${(0.35 * (1 - t / 0.12)).toFixed(2)}"/>` : '');
}

const R = {};

/* 1. Le téléphone qui vibre */
R.telephone = (t, sc) => {
  const vib = (t > 0.05 && t < 1.6) ? Math.sin(t * 95) * 5 : 0;
  const notif = popS(t, 0.9, 0.4);
  const z = tw(t, 0, sc.dur, 1.0, 1.12);
  const bg = `<g filter="url(#blur)" opacity=".85">${A.chambre(t, { linge: false })}</g><rect width="720" height="1280" fill="#000" opacity=".35"/>`;
  const boxes = `<g filter="url(#sh)">${[0, 1, 2, 3].map((i) => `<rect x="${60 + i * 8}" y="${1000 - i * 60}" width="600" height="60" rx="6" fill="#e8c08b" ${A.O(7)}/>`).join('')}
    <text x="380" y="958" font-family="Anton" font-size="40" fill="#b5462b" text-anchor="middle">PIZZA</text>
    <path d="M110 1180 q60 -10 120 0" stroke="#c88" stroke-width="6" fill="none" opacity=".6"/></g>`;
  const glowA = t > 0.9 ? 0.9 : 0.2;
  const phone = `<g transform="translate(${360 + vib} 700) rotate(-4)">
    <ellipse cx="0" cy="0" rx="300" ry="380" fill="url(#glow)" opacity="${glowA}"/>
    <rect x="-150" y="-260" width="300" height="520" rx="44" fill="#1b1b1b" ${A.O(9)}/>
    <rect x="-128" y="-226" width="256" height="452" rx="16" fill="${t > 0.9 ? '#1d2b55' : '#0b0b0b'}"/>
    ${t > 0.9 ? `<text x="0" y="-130" font-family="Anton" font-size="72" fill="#fff" text-anchor="middle" opacity=".9">03:47</text>
      <text x="0" y="-90" font-family="Anton" font-size="22" fill="#cfd8ff" text-anchor="middle">MARDI 1 NOVEMBRE</text>` : ''}
    ${A.pop(0, 40, notif, `<g filter="url(#sh)"><rect x="-118" y="-60" width="236" height="150" rx="18" fill="#fff" ${A.O(4)}/>
      <circle cx="-85" cy="-28" r="20" fill="#ef5b93" ${A.O(3)}/><text x="-85" y="-20" font-family="Anton" font-size="22" fill="#fff" text-anchor="middle">I</text>
      <text x="-55" y="-18" font-family="Anton" font-size="24" fill="${A.K}">INÈS 🎉</text>
      <text x="-100" y="20" font-family="Anton" font-size="19" fill="#333">Les 10 ans du lycée,</text>
      <text x="-100" y="46" font-family="Anton" font-size="19" fill="#333">c'est dans 30 jours !</text>
      <text x="-100" y="74" font-family="Anton" font-size="20" fill="${A.C.red}">Nathan vient ❤</text></g>`)}
    <rect x="-40" y="-248" width="80" height="14" rx="7" fill="#000"/>
  </g>
  ${vib ? `<path d="M170 560 q20 20 0 40 M190 545 q30 35 0 70 M550 560 q-20 20 0 40 M530 545 q-30 35 0 70" fill="none" stroke="#fff" stroke-width="6" stroke-linecap="round" opacity=".8"/>` : ''}`;
  const scene = A.camera(bg + boxes + phone, 360, 700, z);
  const titre = t < 2.2 ? `<g opacity="${clamp((2.2 - t) / 0.3).toFixed(2)}">${A.pop(360, 330, popS(t, 0.0, 0.4), A.titre0(0, [['LANA A ', '#fff'], ['30 JOURS', A.C.yellow]], 92))}</g>` : '';
  return scene + titre + A.hud(30, 0) + A.sousTitres(t, sc.words);
};

/* 2. La couette : on ne voit que le chignon */
R.couette = (t, sc) => {
  const z = tw(t, 0, sc.dur, 1.18, 1.05);
  const wig = Math.sin(t * 3) * 6;
  const peek = tw(t, 1.4, 1.9, 0, 1, easeBack);
  const lump = `<g filter="url(#sh)">
    <rect x="70" y="860" width="580" height="200" rx="20" fill="#6d55a8" ${A.O(8)}/>
    <rect x="70" y="1040" width="30" height="80" fill="#4b3a7a" ${A.O(6)}/><rect x="620" y="1040" width="30" height="80" fill="#4b3a7a" ${A.O(6)}/>
    <rect x="90" y="805" width="150" height="80" rx="30" fill="#efe9ff" ${A.O(6)}/>
    <g transform="translate(0 ${-peek * 55})">
     <circle cx="170" cy="830" r="54" fill="${A.C.hair}" ${A.O(6)}/>
     <path d="M140 810 q30 -30 60 -5 M135 840 q30 20 70 -15" fill="none" stroke="${A.C.hairD}" stroke-width="5"/>
     <rect x="190" y="745" width="14" height="90" rx="3" fill="#ffd23f" ${A.O(4)} transform="rotate(30 197 790)"/>
     <path d="M140 790 l-30 -24 M200 790 l26 -30" stroke="${A.C.hair}" stroke-width="8" stroke-linecap="round"/>
    </g>
    <path d="M80 ${905 + wig} q90 -95 220 -60 q140 -60 230 10 q100 20 120 90 v115 h-570z" fill="#b9a5ea" ${A.O(8)}/>
    <path d="M150 ${930 + wig} q80 -40 160 -10 M380 ${910 - wig} q90 -30 170 20" fill="none" stroke="#8f78cf" stroke-width="7"/>
    <ellipse cx="350" cy="${880 + wig}" rx="60" ry="30" fill="#7fd0ff" opacity="${(0.3 + 0.2 * Math.sin(t * 7)).toFixed(2)}"/>
  </g>`;
  const room = A.chambre(t, { lit: 'lump', linge: false, nuggets: false }) + lump + A.odeurs(t, [[620, 820], [110, 790], [430, 760]]) + A.linge(0.8, 40, 60);
  const dark = `<rect width="720" height="1280" fill="#000" opacity=".25"/>`;
  const shutter = wt(sc, 'volets');
  const arrow = A.pop(560, 600, popS(t, shutter, 0.35), A.etiquette('FERMÉS DEPUIS 2022', 330, A.C.red, 30), -4);
  const label = A.pop(360, 1150, popS(t, wt(sc, 'Lana'), 0.35), A.etiquette('LANA · 25 ANS', 330));
  return entree(t, A.camera(room + dark, 360, 820, z) + arrow + label + `<rect width="720" height="1280" fill="url(#vig)"/>`) + A.hud(30, 0) + A.sousTitres(t, sc.words, 1010);
};

/* 3. Présentation : Lana debout */
R.presentation = (t, sc) => {
  const z = tw(t, 0, sc.dur, 1.0, 1.1);
  const tLit = wt(sc, 'lit'), tSand = wt(sc, 'Sandrine'), tPensent = wt(sc, 'pensent');
  const P = {
    t, blink: blinkAt(t, 1), lid: 0.42, look: [0, 4], headRot: Math.sin(t * 0.9) * 2,
    mouth: 'plat', armL: POSES.bas, armR: POSES.bas,
  };
  if (t > tLit - 0.4 && t < tLit + 0.7) { P.mouth = 'o'; P.lid = 0.7; P.headRot = -6; } // bâillement
  if (t > tPensent) { P.look = [-6, 2]; P.browLift = -4; }
  if (t > tSand) {
    const k = easeBack((t - tSand) / 0.35);
    P.armL = [A.lerp(78, 22, clamp(k)), A.lerp(92, -38, clamp(k))];
    P.armR = [A.lerp(78, 22, clamp(k)), A.lerp(92, -38, clamp(k))];
    P.mouth = 'tordu'; P.browLift = -12; P.lid = 0.25; P.look = [4, 0]; P.headRot = 5;
    P.sticker = popS(t, tSand + 0.05, 0.4);
  }
  const scene = A.chambre(t) + A.odeurs(t) + A.lana(P) + `<rect width="720" height="1280" fill="url(#vig)"/>`;
  const lit = A.pop(360, 1150, popS(t, wt(sc, 'service'), 0.35), A.etiquette('SERVICE CLIENT · DEPUIS SON LIT', 560, A.C.yellow, 32));
  return entree(t, A.camera(scene, 360, 680, z)) + (t < tSand ? lit : '') + A.hud(30, 0) + A.sousTitres(t, sc.words, 1050);
};

/* 4. Pâtes, le chat */
R.pates = (t, sc) => {
  const tDem = wt(sc, 'demandé'), tLui = wt(sc, 'Lui');
  const z = tw(t, 0, sc.dur, 1.05, 1.18);
  const o = { t, blink: blinkAt(t, 2), lid: 0.5, headRot: Math.sin(t * 0.8) * 3, lookX: 0, meow: 0 };
  if (t > tLui && t < tLui + 0.6) o.meow = Math.sin(((t - tLui) / 0.6) * Math.PI);
  if (t > tDem) { o.lookX = 5; o.headRot = -8; }
  const v = t > tDem ? A.valise(560, 1080 + (1 - clamp((t - tDem) / 0.3)) * -300, easeBack((t - tDem) / 0.35)) : '';
  const nameTag = A.pop(360, 1150, popS(t, tLui + 0.3, 0.35), A.etiquette('PÂTES · 4 ANS · 9 KG', 380));
  const scene = A.chambre(t, { linge: false }) + A.odeurs(t, [[160, 640], [600, 600], [230, 900]]) + A.chat(360, 860, 2.1, o) + v + `<rect width="720" height="1280" fill="url(#vig)"/>`;
  return entree(t, A.camera(scene, 360, 800, z)) + nameTag + A.hud(30, 0) + A.sousTitres(t, sc.words, 380);
};

/* 5. Le message d'Inès : choc */
R.message = (t, sc) => {
  const tN = wt(sc, 'sera'), tDix = wt(sc, 'dix'), tInes = wt(sc, "d'Inès");
  const shocked = t > tN;
  const P = {
    t, blink: shocked ? 0 : blinkAt(t, 3), lid: 0.38, look: [8, 10], phone: true, armR: POSES.phone, armL: POSES.bas,
    mouth: 'plat', headRot: 3,
  };
  if (t > tDix) { P.lid = 0.15; P.browLift = -6; P.mouth = 'o'; }
  if (shocked) {
    P.eyes = 'grand'; P.lid = 0; P.look = [0, 0]; P.mouth = 'cri'; P.browLift = -22; P.sweat = true; P.headRot = -4 + Math.sin(t * 40) * 1.5;
    P.armL = [A.lerp(78, -30, clamp((t - tN) / 0.25)), A.lerp(92, -110, clamp((t - tN) / 0.25))];
  }
  const zBase = tw(t, 0, tN, 1.0, 1.12);
  const z = shocked ? 1.12 + 0.14 * easeOut((t - tN) / 0.25) : zBase;
  const cy = shocked ? 660 : 700;
  const [sx, sy] = A.shake(t, tN, 0.5, 14);
  const scene = A.chambre(t) + A.odeurs(t) + A.lana(P) + `<rect width="720" height="1280" fill="url(#vig)"/>`;
  const ines = A.pop(200, 330, popS(t, tInes, 0.35), A.etiquette('INÈS · EX-MEILLEURE AMIE', 400, '#ef5b93', 30), -5);
  const heart = shocked ? A.pop(560, 330, popS(t, tN + 0.1, 0.45), `<path d="M0 30 C-60 -20 -40 -70 0 -40 C40 -70 60 -20 0 30Z" fill="${A.C.red}" ${A.O(6)} filter="url(#sh)"/>`, 8)
    + A.pop(360, 1140, popS(t, tN + 0.2, 0.4), A.etiquette('NATHAN · LE CRUSH DU LYCÉE', 470, A.C.red, 32)) : '';
  const flashR = shocked && t < tN + 0.15 ? `<rect width="720" height="1280" fill="#fff" opacity=".5"/>` : '';
  return entree(t, A.camera(scene, 360, cy, z, sx, sy)) + (shocked ? '' : ines) + heart + flashR + A.hud(30, 0) + A.sousTitres(t, sc.words, shocked ? 260 : 1050);
};

/* 6. Flashback : Lana au lycée */
R.lycee = (t, sc) => {
  const z = tw(t, 0, sc.dur, 1.0, 1.12);
  const inT = easeOut(t / 0.45);
  const P = { t, teen: true, blink: blinkAt(t, 4), lid: 0.05, mouth: 'sourire', eyes: 'normal', look: [0, 0], armL: POSES.hanche, armR: POSES.salut, headRot: 4 + Math.sin(t * 2) * 2 };
  const kid = (x, col, hair) => `<g transform="translate(${x} 0)"><path d="M-70 900 q0 -80 70 -80 q70 0 70 80 v180 h-140z" fill="${col}" ${A.O(6)}/>
    <circle cx="0" cy="740" r="70" fill="${A.C.skin}" ${A.O(6)}/><path d="M-70 735 q0 -80 70 -80 q70 0 70 80 q-30 -40 -70 -30 q-40 -10 -70 30z" fill="${hair}" ${A.O(5)}/>
    <circle cx="-22" cy="745" r="7" fill="${A.K}"/><circle cx="22" cy="745" r="7" fill="${A.K}"/><path d="M-15 775 q15 10 30 0" fill="none" ${A.O(4)}/></g>`;
  const lockers = [0, 1, 2, 3, 4, 5].map((i) => `<rect x="${i * 120}" y="300" width="116" height="700" fill="#5c8ad6" ${A.O(5)}/><rect x="${i * 120 + 20}" y="340" width="76" height="8" fill="#3d64a8"/><rect x="${i * 120 + 20}" y="360" width="76" height="8" fill="#3d64a8"/><circle cx="${i * 120 + 95}" cy="650" r="6" fill="#ddd"/>`).join('');
  const photo = `<rect width="720" height="1280" fill="#f2e3c4"/>${lockers}<rect x="0" y="1000" width="720" height="280" fill="#c9a36b"/>
     ${kid(95, '#9b59b6', '#2b1a10')}${kid(625, '#27ae60', '#e0b04a')}
     <g transform="translate(360 1180) scale(.82) translate(-360 -1230)">${A.lana(P)}</g>
     ${A.etoiles(t, [[240, 470, 1], [500, 430, 1.2], [470, 760, 0.8], [230, 820, 0.9], [560, 600, 0.7]])}`;
  const polaroid = `<g transform="translate(360 660) rotate(${A.lerp(-14, -3, inT).toFixed(2)}) scale(${A.lerp(0.6, 0.86, inT).toFixed(3)}) translate(-360 -640)" filter="url(#sh)">
     <rect x="-20" y="-20" width="760" height="1420" fill="#fbf8f0" ${A.O(6)}/>
     <svg x="0" y="0" width="720" height="1280" viewBox="0 0 720 1280">${photo}<rect width="720" height="1280" fill="url(#sepia)" opacity=".28"/></svg>
     <text x="360" y="1360" font-family="Anton" font-size="62" fill="#333" text-anchor="middle">LYCÉE · 2016 ✨</text></g>`;
  const bg = `<rect width="720" height="1280" fill="#2a1b45"/>${A.etoiles(t * 0.6, [[80, 300, 1], [650, 260, 1.3], [90, 1050, 0.8], [640, 1100, 1]])}`;
  const tag = A.pop(360, 220, popS(t, 0.2, 0.4), A.etiquette('IL Y A 10 ANS', 300, A.C.yellow));
  return A.camera(bg + polaroid, 360, 660, z) + A.sousTitres(t, sc.words, 225);
};

/* 7. Le jean qui sert de rideau */
R.jean = (t, sc) => {
  const z = tw(t, 0, 0.6, 1.0, 1.75, easeOut);
  const label = A.pop(360, 1080, popS(t, wt(sc, 'jean'), 0.35), A.etiquette('SON SEUL JEAN 👖', 360, A.C.blue));
  const scene = A.chambre(t, { rideau: 'jean' }) + A.odeurs(t, [[480, 600], [640, 620]]);
  return A.camera(scene, 545, 420, z) + `<rect width="720" height="1280" fill="url(#vig)"/>` + label + A.hud(30, 0) + A.sousTitres(t, sc.words, 920);
};

/* 8. Elle se lève... et glisse */
R.chute = (t, sc) => {
  const tDec = wt(sc, 'décidée'), tChanger = wt(sc, 'changer');
  const segB = sc.voices[1].start;
  const tSlip = sc.voices[0].start + 3.2 + 0.2;
  const tLand = tSlip + 0.5;
  let inner;
  if (t < tLand) {
    const P = { t, blink: blinkAt(t, 5), lid: 0.2, look: [0, 0], mouth: 'plat', armL: POSES.bas, armR: POSES.bas, headRot: 0 };
    if (t > tDec) { P.browAng = 14; P.mouth = 'dents'; P.lid = 0.25; const k = clamp((t - tDec) / 0.25); P.armR = [A.lerp(78, -48, k), A.lerp(92, -84, k)]; P.armRopt = { fist: true }; }
    if (t > tChanger + 0.2) { P.armR = POSES.haut; }
    let x = 0, rot = 0, y = 0;
    if (t > tChanger + 0.15) x = tw(t, tChanger + 0.15, tSlip, 0, 70);
    if (t > tSlip) {
      const k = clamp((t - tSlip) / 0.5);
      rot = 95 * easeOut(k) * 0.9; x = 70 + 140 * k; y = -60 * Math.sin(k * Math.PI);
      P.eyes = 'grand'; P.mouth = 'cri'; P.lid = 0; P.browLift = -20; P.armL = POSES.haut; P.armR = POSES.salut;
    }
    P.x = x; P.y = y; P.rot = rot;
    const nug = t > tSlip ? A.nuggets(330 + (t - tSlip) * 300, 1235 - Math.sin(clamp((t - tSlip) / 0.7) * Math.PI) * 400, (t - tSlip) * 720, 1.2) : A.nuggets(330, 1235, -8);
    inner = A.chambre(t, { nuggets: false }) + A.odeurs(t) + A.lana(P) + nug;
  } else {
    const k = t - tLand;
    const sway = Math.sin(k * 5) * 6 * Math.exp(-k * 0.8);
    const legs = `<g transform="rotate(${sway.toFixed(2)} 520 1080)">
      ${[[470, -18], [570, 16]].map(([x, r]) => `<g transform="rotate(${r} ${x} 1060)"><rect x="${x - 40}" y="880" width="80" height="190" rx="20" fill="${A.C.pink}" ${A.O(7)}/>
        <ellipse cx="${x}" cy="880" rx="62" ry="32" fill="#fff" ${A.O(7)}/><path d="M${x - 8} 852 l10 -32 l10 32z" fill="#ffd23f" ${A.O(4)}/><circle cx="${x - 18}" cy="874" r="5" fill="${A.K}"/><circle cx="${x + 18}" cy="874" r="5" fill="${A.K}"/></g>`).join('')}
    </g>`;
    const nugFall = A.nuggets(260, Math.min(1235, 600 + k * 1600), k * 400, 1.2);
    inner = A.chambre(t, { linge: false, nuggets: false }) + A.odeurs(t) + legs + A.linge(1.8, -90, 40) +
      A.etoiles(t, [[520 + Math.cos(t * 5) * 90, 900 + Math.sin(t * 5) * 25, 0.9], [520 + Math.cos(t * 5 + 2.1) * 90, 900 + Math.sin(t * 5 + 2.1) * 25, 0.9], [520 + Math.cos(t * 5 + 4.2) * 90, 900 + Math.sin(t * 5 + 4.2) * 25, 0.9]]) + nugFall;
  }
  const [sx, sy] = A.shake(t, tLand, 0.45, 20);
  const z = t < tLand ? tw(t, 0, tSlip, 1.0, 1.08) : 1.15;
  const cy = t < tLand ? 700 : 720;
  const boom = A.pop(500, 640, t > tLand && t < tLand + 1.0 ? popS(t, tLand, 0.25) : 0, A.titre0(0, [['PAF !', A.C.yellow]], 110), -8);
  const lbl = A.pop(360, 1160, popS(t, segB + 1.2, 0.35), A.etiquette('BOÎTE DE NUGGETS : 1 · LANA : 0', 540, A.C.red, 32));
  return A.camera(`<rect width="720" height="1280" fill="#2a1b45"/>` + inner + `<rect width="720" height="1280" fill="url(#vig)"/>`, 360, cy, z, sx, sy) + boom + lbl + A.hud(30, 0) + A.sousTitres(t, sc.words, t < tLand ? 1050 : 430);
};

/* 9. Le miroir de la salle de bain */
R.miroir = (t, sc) => {
  const tTrente = wt(sc, 'trente'), tToi = wt(sc, 'toi'), tChoisit = wt(sc, 'choisit');
  const P = { t, blink: blinkAt(t, 6), lid: 0.35, look: [0, 0], mouth: 'tordu', armL: POSES.bas, armR: POSES.bas, headRot: Math.sin(t) * 2, browAng: -8 };
  if (t > 0.3 && t < tTrente) { P.headRot = -6; P.look = [-6, 0]; P.mouth = 'soupir'; }
  if (t > tChoisit - 0.2) { P.browAng = 0; P.browLift = -10; P.lid = 0.15; P.mouth = 'plat'; }
  if (t > tToi - 0.1) { P.armR = POSES.pointe; P.armRopt = { point: true }; P.mouth = 'sourire'; P.eyes = 'normal'; P.lid = 0.1; P.browLift = -14; }
  const zT = t > tToi ? 1.08 + 0.12 * easeOut((t - tToi) / 0.3) : tw(t, 0, tToi, 1.0, 1.08);
  const scene = A.salleDeBain(t) + A.lana(P) + `<rect width="720" height="1280" fill="url(#vig)"/>`;
  const frame = `<rect x="18" y="18" width="684" height="1244" rx="40" fill="none" stroke="#e9e3d6" stroke-width="36"/><rect x="0" y="0" width="720" height="1280" rx="50" fill="none" stroke="${A.K}" stroke-width="8"/>
    <path d="M60 80 l80 -40 M70 130 l130 -70" stroke="#fff" stroke-width="10" stroke-linecap="round" opacity=".35"/>`;
  const j30 = A.pop(360, 330, popS(t, tTrente, 0.4), A.titre0(0, [['J-30', A.C.red]], 150), -4);
  const toi = A.pop(360, 1150, popS(t, tToi, 0.35), A.etiquette('👉 C\'EST TOI QUI CHOISIS', 480, A.C.yellow, 36));
  return entree(t, A.camera(scene, 360, 700, zT)) + postitsOver(t) + frame + (t < tToi ? j30 : '') + toi + A.hud(30, 0, 1) + A.sousTitres(t, sc.words, t > tToi ? 330 : 1050);
};
const postitsOver = (t) => A.postits(t);

/* 10. Le vote : APPART ou SOURCILS */
R.vote = (t, sc) => {
  const tA = wt(sc, 'appart'), tS = wt(sc, 'sourcils');
  const hlA = t > tA && t < tS ? 1 : 0, hlS = t > tS ? 1 : 0;
  const left = `<g clip-path="url(#cLeft)">${A.camera(A.chambre(t) + A.odeurs(t), 330, 900, 1.25 + 0.08 * hlA)}<rect width="720" height="1280" fill="#000" opacity="${hlS ? 0.45 : 0}"/></g>`;
  const P = { t, blink: blinkAt(t, 7), lid: 0.4, look: [0, -10], mouth: 'tordu', browLift: Math.sin(t * 6) * 4 * (hlS ? 1 : 0) };
  const right = `<g clip-path="url(#cRight)"><rect x="364" width="356" height="1280" fill="#3c2766"/>
     ${A.camera(A.lana(P), 360, 540, 2.3 + 0.15 * hlS, 180, 0)}<rect width="720" height="1280" fill="#000" opacity="${hlA ? 0.45 : 0}"/></g>`;
  const div = `<rect x="352" y="0" width="16" height="1280" fill="${A.K}"/>
    ${A.pop(360, 640, popS(t, 0.2, 0.4), `<circle r="62" fill="${A.C.yellow}" ${A.O(8)}/><text y="22" font-family="Anton" font-size="62" fill="${A.K}" text-anchor="middle">OU</text>`)}`;
  const la = A.pop(180, 1050, popS(t, 0.25, 0.4) * (1 + 0.12 * hlA), A.etiquette('APPART', 260, A.C.yellow, 48));
  const ls = A.pop(540, 1050, popS(t, 0.4, 0.4) * (1 + 0.12 * hlS), A.etiquette('SOURCILS', 280, '#ef5b93', 48));
  const q = A.pop(360, 300, popS(t, 0.1, 0.4), A.titre0(0, [['PAR QUOI', '#fff']], 84) + `<g transform="translate(0 95)">${A.titre0(0, [['ELLE COMMENCE ?', A.C.yellow]], 84)}</g>`);
  return left + right + div + la + ls + q + `<rect width="720" height="1280" fill="url(#vig)" opacity=".6"/>`;
};

/* 11. Appel au vote final */
R.fin = (t, sc) => {
  const tMot = wt(sc, 'mot'), tToujours = wt(sc, 'toujours', 0, 'e');
  const wave = Math.sin(t * 7) * 18;
  const P = { t, blink: blinkAt(t, 8), lid: 0.2, look: [0, 0], mouth: 'sourire', eyes: 'normal', armL: POSES.bas, armR: [-30 + wave * 0.3, -100 + wave], headRot: Math.sin(t * 1.5) * 3, browLift: -6, s: 0.9, y: 30 };
  const o = { t, blink: blinkAt(t, 9), lid: 0.5, headRot: -6 + Math.sin(t) * 3 };
  const scene = A.chambre(t) + A.odeurs(t) + A.lana(P) + A.chat(205, 735, 0.62, o) + `<rect width="720" height="1280" fill="url(#vig)"/>`;
  const z = tw(t, 0, sc.dur, 1.0, 1.06);
  const bounce = Math.abs(Math.sin(t * 5)) * 18;
  const cta = A.pop(360, 1040, popS(t, tMot - 0.3, 0.4), A.etiquette('COMMENTE UN MOT 👇', 470, A.C.yellow, 44));
  const chips = A.pop(205, 1150, popS(t, tMot + 0.1, 0.35), A.etiquette('APPART', 240, A.C.yellow, 44)) + A.pop(515, 1150, popS(t, tMot + 0.25, 0.35), A.etiquette('SOURCILS', 260, '#ef5b93', 44));
  const fleche = t > tMot ? `<g transform="translate(360 ${1225 + bounce})"><path d="M-20 -20 h40 v20 h22 l-42 36 l-42 -36 h22z" fill="${A.C.yellow}" ${A.O(5)}/></g>` : '';
  const end = A.pop(360, 300, popS(t, tToujours + 0.4, 0.45), A.titre0(0, [['JOUR 2', A.C.yellow]], 96) + `<g transform="translate(0 80)">${A.titre0(0, [['TRÈS BIENTÔT ⏰', '#fff']], 60)}</g>`);
  return entree(t, A.camera(scene, 360, 660, z)) + cta + chips + fleche + end + A.hud(30, 0) + A.sousTitres(t, sc.words, 300);
};

function frameAt(T) {
  let sc = TL.scenes[TL.scenes.length - 1];
  for (const s of TL.scenes) if (T >= s.start && T < s.start + s.dur) { sc = s; break; }
  const t = T - sc.start;
  return A.DEFS + R[sc.id](t, sc);
}

module.exports = { TL, frameAt, wt, S };
