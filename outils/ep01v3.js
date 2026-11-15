// Épisode 1 — version 2 optimisée TikTok : accroche choc, rythme resserré, mots-clés, fin avec teaser
const path = require('path');
const A = require('./art');
const E1 = require('./ep01');
const { tw, easeOut, easeBack, blinkAt, popS, clamp, POSES } = A;

E1.setVoix(path.join(__dirname, '../build/ep01v2/voix'));
A.EMPH = /^(nathan|sandrine|déménager|ruiner|stylée|jean|rideau|nuggets|toi|appart|sourcils|trente|30)/i;
const R = { ...E1.R };

// Scènes resserrées (temps morts réduits) + accroche + écran final
const SCENES = [
  { id: 'hook', segs: [['s0', 0.0]], tail: 0.55 },
  { id: 'telephone', segs: [['s1', 0.0]], tail: 0.2, notif: 0.25 },
  { id: 'couette', segs: [['s2', 0.1]], tail: 0.2 },
  { id: 'presentation', segs: [['s3', 0.1]], tail: 0.15 },
  { id: 'pates', segs: [['s4', 0.1]], tail: 0.15 },
  { id: 'message', segs: [['s5', 0.1]], tail: 0.4 },
  { id: 'lycee', segs: [['s5b', 0.15]], tail: 0.15 },
  { id: 'jean', segs: [['s5c', 0.1]], tail: 0.15 },
  { id: 'chute', segs: [['s6a', 0.1], ['s6b', 0]], gap: 1.05, tail: 0.1 },
  { id: 'miroir', segs: [['s7', 0.15]], tail: 0.1 },
  { id: 'vote', segs: [['s8', 0.15]], tail: 0.1 },
  { id: 'fin', segs: [['s9', 0.1]], tail: 0.3 },
  { id: 'teaser', segs: [], tail: 3.4 },
];

function construireTimeline() {
  let T = 0; const out = [];
  for (const sc of SCENES) {
    const words = [], voices = []; let local = 0;
    sc.segs.forEach(([id, lead], i) => {
      const v = E1.voix(id);
      local += i === 0 ? lead : sc.gap || 0;
      voices.push({ id, start: local, dur: v.dur });
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
const wt = E1.wt;

/* ACCROCHE : Lana hurle sur son téléphone, puis retour en arrière */
R.hook = (t, sc) => {
  const tRew = sc.voices[0].start + sc.voices[0].dur + 0.05;
  const P = { t, blink: 0, lid: 0, eyes: 'grand', look: [0, 0], phone: true, armR: POSES.phone, mouth: 'cri', browLift: -24, sweat: true,
    headRot: -4 + Math.sin(t * 45) * 2, armL: [-30, -110] };
  const z = 1.62 + 0.18 * easeOut(t / 0.6);
  const [sx, sy] = A.shake(t, 0, 0.9, 18);
  let scene = A.chambre(t) + A.odeurs(t) + A.lana(P) + `<rect width="720" height="1280" fill="url(#vig)"/>`;
  scene = A.camera(scene, 380, 620, z, sx, sy);
  const red = `<rect width="720" height="1280" fill="#ff1f3d" opacity="${(0.3 * Math.abs(Math.sin(t * 9 + 1.2)) * (1 - clamp(t / 1.2))).toFixed(2)}"/>`;
  const hookTxt = A.pop(360, 330, Math.max(0.85, popS(t, -0.1, 0.25)), A.titre0(0, [['IL REVIENT', '#fff']], 104) + `<g transform="translate(0 104)">${A.titre0(0, [['DANS ', '#fff'], ['30 JOURS', A.C.yellow], [' 😱', '#fff']], 86)}</g>`);
  const tag = A.pop(360, 1130, popS(t, 0.6, 0.3), A.etiquette('JOUR 1/30 · TU DÉCIDES 👇', 470, A.C.yellow, 38));
  let rew = '';
  if (t > tRew) {
    const k = clamp((t - tRew) / (sc.dur - tRew));
    let lines = ''; for (let y = (t * 900) % 16; y < 1280; y += 16) lines += `<rect y="${y.toFixed(0)}" width="720" height="3" fill="#000" opacity=".25"/>`;
    rew = `<rect width="720" height="1280" fill="#0b1640" opacity="${(0.25 + 0.45 * k).toFixed(2)}"/>${lines}` +
      A.pop(360, 640, easeBack(k * 3), `<g filter="url(#sh)"><rect x="-280" y="-70" width="560" height="140" rx="22" fill="#121212" stroke="#fff" stroke-width="5"/>
        <text x="0" y="22" font-family="Anton" font-size="62" fill="#fff" text-anchor="middle">⏪ 1 HEURE PLUS TÔT</text></g>`);
  }
  return scene + red + (t < tRew ? hookTxt + tag : '') + A.hud(30, 0) + rew;
};

/* JEAN : on arrive directement zoomé */
R.jean = (t, sc) => {
  const z = tw(t, 0, sc.dur, 1.95, 2.1);
  const label = A.pop(360, 1080, popS(t, wt(sc, 'jean'), 0.35), A.etiquette('SON SEUL JEAN 👖', 360, A.C.blue));
  const scene = A.chambre(t, { rideau: 'jean' }) + A.odeurs(t, [[480, 600], [640, 620]]);
  return E1.entree(t, A.camera(scene, 545, 410, z)) + `<rect width="720" height="1280" fill="url(#vig)"/>` + label + A.hud(30, 0) + A.sousTitres(t, sc.words, 920);
};

/* ÉCRAN FINAL : teaser du jour 2 + abonnement + partage */
R.teaser = (t, sc) => {
  const P = { t, teen: true, blink: 0, lid: 0, mouth: 'sourire', eyes: 'normal', armL: POSES.hanche, armR: POSES.hanche, headRot: 3 };
  const bg = `<rect width="720" height="1280" fill="#170f2b"/>` + A.etoiles(t, [[90, 320, 1], [640, 360, 1.2], [110, 900, 0.8], [620, 960, 1], [360, 230, 0.7]]);
  const glowR = 260 + 20 * Math.sin(t * 3);
  const sil = `<circle cx="360" cy="720" r="${glowR.toFixed(0)}" fill="url(#glowW)" opacity=".35"/>
    <g transform="translate(360 1180) scale(${(0.72 + 0.02 * Math.sin(t * 2)).toFixed(3)}) translate(-360 -1230)" filter="url(#silh)">${A.lana(P)}</g>
    ${A.pop(360, 660, popS(t, 0.35, 0.4), `<text x="0" y="0" font-family="Anton" font-size="230" fill="${A.C.yellow}" text-anchor="middle" stroke="${A.K}" stroke-width="16" paint-order="stroke">?</text>`)}`;
  const l1 = A.pop(360, 250, popS(t, 0.0, 0.35), A.titre0(0, [['JOUR 30 :', A.C.yellow]], 76) + `<g transform="translate(0 86)">${A.titre0(0, [['MÉCONNAISSABLE ?', '#fff']], 76)}</g>`);
  const demain = A.pop(360, 1010, popS(t, 0.9, 0.35), A.etiquette('DEMAIN : ON SONNE À SA PORTE 👀', 580, A.C.red, 34));
  const abo = A.pop(360, 1110, popS(t, 1.5, 0.35) * (1 + 0.05 * Math.sin(t * 8)), A.etiquette('🔔 ABONNE-TOI POUR LA SUITE', 520, A.C.yellow, 36));
  const share = A.pop(360, 1210, popS(t, 2.1, 0.35), A.etiquette('ENVOIE ÇA À TA POTE EN PYJAMA 🦄', 600, '#ef5b93', 30));
  return E1.entree(t, bg + sil) + l1 + demain + abo + share;
};

// Coups de zoom sur les mots-clés + whoosh visuel aux coupes
function frameAt(T) {
  let sc = TL.scenes[TL.scenes.length - 1];
  for (const s of TL.scenes) if (T >= s.start && T < s.start + s.dur) { sc = s; break; }
  const t = T - sc.start;
  let bump = 0;
  for (const w of sc.words) if (A.EMPH.test(w.w) && t > w.s) bump += 0.045 * Math.exp(-(t - w.s) / 0.14);
  let inner = R[sc.id](t, sc);
  if (bump > 0.001) inner = `<g transform="translate(360 640) scale(${(1 + bump).toFixed(4)}) translate(-360 -640)">${inner}</g>`;
  // flou de mouvement à l'entrée de chaque plan (sauf le premier)
  if (sc.start > 0 && t < 0.1) inner = `<g transform="translate(${((1 - t / 0.1) * 40).toFixed(1)} 0)">${inner}</g>`;
  return A.DEFS + `<rect width="720" height="1280" fill="#1b1230"/>` + inner;
}

module.exports = { TL, frameAt, wt, S };
