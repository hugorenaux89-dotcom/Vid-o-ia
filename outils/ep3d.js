// Épisode 1 (3D) — timeline, enveloppes de voix (lip-sync) et habillage 2D par-dessus la 3D
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');
const A = require('./art');
const { easeOut, easeBack, popS, clamp } = A;

const VX = path.join(__dirname, '../build/ep01-3d/voix');
const voix = (id) => JSON.parse(fs.readFileSync(`${VX}/${id}.json`, 'utf8'));

// plans : segments [voix, attente avant], durée de fin
const PLANS = [
  { id: 'hook', segs: [['a1', 0.0], ['a2', 0.15]], tail: 1.3 },
  { id: 'record', segs: [['b1', 0.15]], tail: 0.2 },
  { id: 'livreur', segs: [['c1', 0.1]], tail: 0.35 },
  { id: 'pates', segs: [['d1', 0.1]], tail: 0.35 },
  { id: 'nuit', segs: [['e1', 0.25]], tail: 0.6 },
  { id: 'message', segs: [['e2', 0.15], ['e3', 0.3]], tail: 0.2 },
  { id: 'refus', segs: [['f1', 0.1], ['f2', 0.55], ['f3', 0.45]], tail: 0.25 },
  { id: 'cri', segs: [['f4', 0.05]], tail: 0.9 },
  { id: 'bal', segs: [['g1', 0.5], ['g2', 0.55]], tail: 0.7 },
  { id: 'decision', segs: [['h1', 0.35]], tail: 0.25 },
  { id: 'chute', segs: [['h2', 0.1], ['h3', 1.25]], tail: 0.6 },
  { id: 'miroir', segs: [['i1', 0.2], ['i2', 0.25]], tail: 0.35 },
  { id: 'vote', segs: [['j1', 0.15]], tail: 0.5 },
  { id: 'cta', segs: [['k1', 0.1]], tail: 0.25 },
  { id: 'porte', segs: [['l1', 0.4]], tail: 3.6 },
];

function enveloppe(id) {
  const raw = execFileSync('ffmpeg', ['-loglevel', 'error', '-i', `${VX}/${id}.wav`, '-f', 's16le', '-ac', '1', '-ar', '12000', '-']);
  const n = Math.floor(raw.length / 2), step = 400; // 30 i/s
  const out = [];
  for (let i = 0; i < n; i += step) {
    let s = 0; for (let k = i; k < Math.min(n, i + step); k++) { const v = raw.readInt16LE(k * 2) / 32768; s += v * v; }
    out.push(Math.sqrt(s / step));
  }
  const mx = Math.max(...out, 1e-3);
  return out.map((v) => +(Math.min(1, v / mx * 1.3)).toFixed(3));
}

function construire() {
  let T = 0; const plans = [];
  for (const p of PLANS) {
    const words = [], voices = []; let local = 0;
    p.segs.forEach(([id, lead]) => {
      const v = voix(id);
      local += lead;
      voices.push({ id, start: local, dur: v.dur, voix: v.voix });
      v.words.forEach((w) => words.push({ w: w.w, s: w.s + local, e: w.e + local, seg: id, voix: v.voix }));
      local += v.dur;
    });
    const dur = local + p.tail;
    plans.push({ ...p, start: T, dur, words, voices });
    T += dur;
  }
  return { plans, total: T };
}
const TL = construire();
const P = Object.fromEntries(TL.plans.map((p) => [p.id, p]));
const env = {};
for (const p of TL.plans) for (const v of p.voices) env[v.id] = enveloppe(v.id);

function wt(p, txt, n = 0, which = 's') {
  const m = p.words.filter((w) => w.w.toLowerCase().includes(txt.toLowerCase()));
  if (!m[n]) throw new Error(`mot introuvable « ${txt} » dans ${p.id}`);
  return m[n][which];
}
const vstart = (p, id) => p.voices.find((v) => v.id === id).start;
const vend = (p, id) => { const v = p.voices.find((x) => x.id === id); return v.start + v.dur; };

// mots-clés mis en valeur + couleur selon qui parle
A.EMPH = /^(nathan|lana|onze|11|pizza|pâtes|croquettes|inès|bal|jamais|nuggets|toi|appart|sourcils|trente|méconnaissable|toujours|demain|porte)/i;
const COUL = { narrateur: '#ffd23f', lana: '#ff8fc8', ines: '#7fe0ff' };
function sousTitres(t, p, y) {
  const w = p.words.filter((x) => t >= x.s - 0.6 && t <= x.e + 1.2);
  if (!w.length) return '';
  const seg = p.words.filter((x) => x.seg === w[0].seg);
  const svg = A.sousTitres(t, seg, y);
  if (!svg) return '';
  return svg.replace(new RegExp(A.C.yellow, 'g'), COUL[w[0].voix] || A.C.yellow);
}

/* ---------- habillages 2D par plan ---------- */
const bulle = (x, y, s, nom, txt, col = '#7fe0ff') => {
  const lines = txt.split('\n');
  const w = 560, h = 70 + lines.length * 46;
  return A.pop(x, y, s, `<g filter="url(#sh)"><rect x="${-w / 2}" y="${-h / 2}" width="${w}" height="${h}" rx="30" fill="#fff" stroke="${A.K}" stroke-width="5"/>
    <path d="M${-w / 2 + 40} ${h / 2 - 4} l-26 34 l60 -34z" fill="#fff" stroke="${A.K}" stroke-width="5" stroke-linejoin="round"/>
    <rect x="${-w / 2 + 34}" y="${h / 2 - 8}" width="52" height="12" fill="#fff"/>
    <circle cx="${-w / 2 + 44}" cy="${-h / 2 + 40}" r="22" fill="${col}" stroke="${A.K}" stroke-width="4"/>
    <text x="${-w / 2 + 44}" y="${-h / 2 + 49}" font-family="Anton" font-size="24" fill="${A.K}" text-anchor="middle">${A.esc(nom[0])}</text>
    <text x="${-w / 2 + 78}" y="${-h / 2 + 50}" font-family="Anton" font-size="28" fill="${A.K}">${A.esc(nom)}</text>
    ${lines.map((l, i) => `<text x="${-w / 2 + 30}" y="${-h / 2 + 100 + i * 46}" font-family="Anton" font-size="36" fill="#333">${A.esc(l)}</text>`).join('')}</g>`);
};
const fleche = (x1, y1, x2, y2, txt, s, col = '#fff') => s <= 0 ? '' : `<g opacity="${clamp(s).toFixed(2)}">
  <path d="M${x1} ${y1} Q${(x1 + x2) / 2 + 30} ${(y1 + y2) / 2 - 40} ${x2} ${y2}" fill="none" stroke="${A.K}" stroke-width="12" stroke-linecap="round"/>
  <path d="M${x1} ${y1} Q${(x1 + x2) / 2 + 30} ${(y1 + y2) / 2 - 40} ${x2} ${y2}" fill="none" stroke="${col}" stroke-width="6" stroke-linecap="round"/>
  <circle cx="${x2}" cy="${y2}" r="9" fill="${col}" stroke="${A.K}" stroke-width="4"/></g>` + A.pop(x1, y1 - 30, s, A.etiquette(txt, txt.length * 19 + 50, col, 30));

const O = {};
O.hook = (t, p) => {
  const tA2 = vstart(p, 'a2'), tCa = wt(p, 'ça'), end = vend(p, 'a2');
  let s = '';
  if (t > 0.9 && t < tA2) s += A.pop(470, 640, popS(t, 0.9, 0.35), `<g transform="rotate(6)" filter="url(#sh)"><rect x="-130" y="-160" width="260" height="320" fill="#fbf8f0" stroke="${A.K}" stroke-width="5"/>
      <rect x="-110" y="-140" width="220" height="220" fill="#7fb3e6"/><path d="M-60 80 v-50 q60 -40 120 0 v50z" fill="#2d5fa8"/><circle cy="-30" r="52" fill="#f0c49a"/><path d="M-54 -40 q54 -70 108 0 q-20 -30 -54 -30 q-34 0 -54 30z" fill="#2b1a10"/>
      <circle cx="-18" cy="-30" r="6" fill="#111"/><circle cx="18" cy="-30" r="6" fill="#111"/><path d="M-16 -6 q16 14 32 0" fill="none" stroke="#111" stroke-width="4"/>
      <text y="125" font-family="Anton" font-size="34" fill="#333" text-anchor="middle">NATHAN · 2016 ❤</text></g>`);
  if (t < tA2) s += A.pop(360, 300, Math.max(0.9, popS(t, -0.1, 0.3)), A.titre0(0, [['SON CRUSH', '#fff']], 96) + `<g transform="translate(0 100)">${A.titre0(0, [['REVIENT DANS ', '#fff'], ['30 JOURS', A.C.yellow]], 72)}</g>`);
  if (t > tCa) {
    const k = t - tCa;
    s += `<rect width="720" height="1280" fill="#fff" opacity="${(0.6 * (1 - clamp(k / 0.15))).toFixed(2)}"/>`;
    s += A.pop(360, 250, popS(t, tCa, 0.25), A.titre0(0, [['ÇA. 👇', '#ff4d5e']], 140), -4);
    s += fleche(150, 470, 300, 560, 'CHIGNON NID D\'OISEAU', popS(t, tCa + 0.35, 0.3), A.C.yellow);
    s += fleche(570, 560, 445, 690, 'SOURCILS SAUVAGES', popS(t, tCa + 0.6, 0.3), '#ff8fc8');
    s += fleche(560, 960, 420, 900, 'PYJAMA DEPUIS 2023', popS(t, tCa + 0.85, 0.3), '#7fe0ff');
  }
  return s + A.hud(30, 0) + (t < end + 0.2 ? sousTitres(t, p, 1150) : '');
};
O.record = (t, p) => A.pop(360, 330, popS(t, wt(p, 'onze'), 0.35), A.etiquette('🏠 11 JOURS SANS SORTIR', 470, A.C.red, 40)) + A.hud(30, 0) + sousTitres(t, p, 1120);
O.livreur = (t, p) => A.pop(470, 330, popS(t, wt(p, 'demandé'), 0.3), `<g filter="url(#sh)"><rect x="-150" y="-50" width="300" height="100" rx="40" fill="#fff" stroke="${A.K}" stroke-width="5"/><path d="M-40 46 l-30 40 l60 -40z" fill="#fff" stroke="${A.K}" stroke-width="5"/><rect x="-60" y="40" width="70" height="12" fill="#fff"/><text y="16" font-family="Anton" font-size="40" fill="${A.K}" text-anchor="middle">…ça va ? 😟</text></g>`)
  + A.pop(360, 1010, popS(t, wt(p, 'contact'), 0.3), A.etiquette('SEUL CONTACT HUMAIN', 380, A.C.yellow, 34)) + A.hud(30, 0) + sousTitres(t, p, 1140);
O.pates = (t, p) => A.pop(360, 1010, popS(t, wt(p, 'Pâtes'), 0.3), A.etiquette('PÂTES · 9 KG DE MÉPRIS', 420, '#ef8a2e', 34)) + A.hud(30, 0) + sousTitres(t, p, 1140);
O.nuit = (t, p) => A.pop(360, 330, popS(t, wt(p, 'trois'), 0.3), `<g filter="url(#sh)"><rect x="-150" y="-60" width="300" height="120" rx="20" fill="#111" stroke="#ff4d5e" stroke-width="5"/><text y="34" font-family="Anton" font-size="92" fill="#ff4d5e" text-anchor="middle">03:47</text></g>`) + A.hud(30, 0) + sousTitres(t, p, 1140);
O.message = (t, p) => {
  const t2 = vstart(p, 'e2'), t3 = vstart(p, 'e3');
  let s = bulle(360, 330, popS(t, t2 - 0.1, 0.3), 'INÈS 💅', 'Coucou ma belle !! Soirée des 10\nans du lycée dans 30 jours 🎉\nTu viens ?');
  if (t > t3) s = A.pop(360, 330, popS(t, t3, 0.3), `<g filter="url(#sh)"><rect x="-250" y="-90" width="500" height="180" rx="24" fill="#121212" stroke="#ef5b93" stroke-width="5"/>
    <circle cx="-170" cy="0" r="56" fill="#ffd9a0" stroke="#fff" stroke-width="5"/><text x="-170" y="22" font-family="Anton" font-size="60" text-anchor="middle">💅</text>
    <text x="-90" y="-28" font-family="Anton" font-size="44" fill="#fff">INÈS</text>
    <text x="-90" y="16" font-family="Anton" font-size="26" fill="#ef5b93">EX-MEILLEURE AMIE</text>
    <text x="-90" y="54" font-family="Anton" font-size="26" fill="#aaa">💔 DEPUIS LE BAL 2016</text></g>`);
  return s + A.hud(30, 0) + sousTitres(t, p, 1140);
};
O.refus = (t, p) => {
  const t3 = vstart(p, 'f3'); let s = '';
  if (t > vstart(p, 'f2') - 0.2) s += A.pop(360, 1000, popS(t, vstart(p, 'f2') - 0.2, 0.3), A.etiquette('📳 2E MESSAGE', 300, A.C.red, 36));
  if (t > t3 - 0.1) s += bulle(360, 330, popS(t, t3 - 0.1, 0.3), 'INÈS 💅', 'Au fait… Nathan m\'a demandé\nsi tu venais 😏');
  return s + A.hud(30, 0) + sousTitres(t, p, 1140);
};
O.cri = (t, p) => {
  const k = t;
  return `<rect width="720" height="1280" fill="#ff1f3d" opacity="${(0.3 * Math.abs(Math.sin(k * 10)) * (1 - clamp(k / 1.4))).toFixed(2)}"/>` +
    A.pop(360, 300, popS(t, 0.05, 0.25), A.titre0(0, [['NATHAN ?!', '#ff4d5e']], 150), -5) + A.hud(30, 0) + sousTitres(t, p, 1140);
};
O.bal = (t, p) => {
  const tJ = vstart(p, 'g2');
  const dim = clamp((t - tJ) / 1.5) * 0.35;
  let s = `<rect width="720" height="1280" fill="#2a1a00" opacity=".18"/><rect width="720" height="1280" fill="#000" opacity="${dim.toFixed(2)}"/>`;
  s += A.pop(360, 200, popS(t, 0.1, 0.4), A.etiquette('⏪ LE BAL · 2016', 340, '#ef5b93', 38));
  if (t > tJ) s += A.pop(360, 330, popS(t, tJ, 0.4), `<g filter="url(#sh)"><rect x="-120" y="-50" width="240" height="100" rx="18" fill="#111" stroke="#fff" stroke-width="4"/><text y="30" font-family="Anton" font-size="70" fill="#fff" text-anchor="middle">23:59</text></g>`);
  return s + sousTitres(t, p, 1140);
};
O.decision = (t, p) => A.pop(360, 320, popS(t, wt(p, 'Trente'), 0.3), A.titre0(0, [['J-30', A.C.red]], 160), -4) + A.hud(30, 0) + sousTitres(t, p, 1150);
O.chute = (t, p) => {
  const tSlip = vend(p, 'h2') + 0.05, tLand = tSlip + 0.55; let s = '';
  if (t < tSlip) s += A.pop(360, 300, popS(t, 0.2, 0.3), A.etiquette('✨ AU RALENTI ✨', 340, '#fff', 40));
  if (t > tLand && t < tLand + 1.1) s += A.pop(500, 560, popS(t, tLand, 0.2), A.titre0(0, [['PAF !', A.C.yellow]], 130), -8);
  if (t > vstart(p, 'h3') + 0.9) s += A.pop(360, 1000, popS(t, vstart(p, 'h3') + 0.9, 0.3), A.etiquette('NUGGETS 1 · LANA 0', 380, A.C.red, 36));
  return s + A.hud(30, 0) + sousTitres(t, p, 1140);
};
O.miroir = (t, p) => {
  const tToi = wt(p, 'toi'), tTj = wt(p, 'toujours');
  const frame = `<rect x="16" y="16" width="688" height="1248" rx="44" fill="none" stroke="#e9e3d6" stroke-width="32"/><rect x="0" y="0" width="720" height="1280" rx="50" fill="none" stroke="${A.K}" stroke-width="8"/>
    <path d="M60 90 l90 -46 M70 140 l140 -76" stroke="#fff" stroke-width="10" stroke-linecap="round" opacity=".35"/>`;
  let s = A.postits(t) + frame;
  s += A.pop(360, 1000, popS(t, tToi, 0.3), A.etiquette('👉 C\'EST TOI QUI CHOISIS', 470, A.C.yellow, 36));
  if (t > tTj) s += A.pop(360, 640, popS(t, tTj, 0.25), `<g transform="rotate(-12)" filter="url(#sh)"><rect x="-230" y="-70" width="460" height="140" rx="14" fill="none" stroke="#ff2d55" stroke-width="12"/><text y="34" font-family="Anton" font-size="96" fill="#ff2d55" text-anchor="middle">DÉFINITIF</text></g>`);
  return s + A.hud(30, 0) + sousTitres(t, p, 330);
};
O.vote = (t, p) => {
  const tA = wt(p, 'appart'), tS = wt(p, 'sourcils'), tC = wt(p, 'postal');
  let s = `<rect x="0" y="632" width="720" height="16" fill="${A.K}"/>`;
  s += A.pop(360, 640, popS(t, 0.1, 0.3), `<circle r="60" fill="${A.C.yellow}" stroke="${A.K}" stroke-width="8"/><text y="22" font-family="Anton" font-size="60" fill="${A.K}" text-anchor="middle">OU</text>`);
  s += A.pop(150, 560, popS(t, tA, 0.3) * (t > tA && t < tS ? 1.12 : 1), A.etiquette('APPART', 230, A.C.yellow, 48));
  s += A.pop(570, 1200, popS(t, tS, 0.3) * (t > tS ? 1.12 : 1), A.etiquette('SOURCILS', 260, '#ef5b93', 48));
  if (t > tC) s += A.pop(470, 760, popS(t, tC, 0.3), A.etiquette('📮 CODE POSTAL : 75 SOURCILS', 470, '#fff', 28), 4);
  if (t < tA) s += A.pop(360, 200, popS(t, 0, 0.3), A.titre0(0, [['PREMIER CHOIX', '#fff']], 72));
  return s + sousTitres(t, p, t < tS ? 1100 : 470);
};
O.cta = (t, p) => {
  const tM = wt(p, 'mot'); const b = Math.abs(Math.sin(t * 5)) * 16;
  return A.pop(360, 1000, popS(t, tM - 0.2, 0.3), A.etiquette('ÉCRIS UN MOT 👇', 400, A.C.yellow, 44)) +
    A.pop(205, 1110, popS(t, tM, 0.3), A.etiquette('APPART', 240, A.C.yellow, 44)) + A.pop(515, 1110, popS(t, tM + 0.15, 0.3), A.etiquette('SOURCILS', 260, '#ef5b93', 44)) +
    (t > tM ? `<g transform="translate(360 ${1200 + b})"><path d="M-20 -20 h40 v20 h22 l-42 36 l-42 -36 h22z" fill="${A.C.yellow}" stroke="${A.K}" stroke-width="5"/></g>` : '') +
    A.hud(30, 0) + sousTitres(t, p, 330);
};
O.porte = (t, p) => {
  const tS = wt(p, 'sonne'), tEnd = vend(p, 'l1') + 0.7;
  let s = '';
  if (t > tS) s += A.pop(360, 300, popS(t, tS, 0.25), A.titre0(0, [['DING DONG 🔔', A.C.yellow]], 100), -3);
  if (t > tEnd) {
    const k = clamp((t - tEnd) / 0.4);
    s = `<rect width="720" height="1280" fill="#120b22" opacity="${(0.82 * k).toFixed(2)}"/>`;
    s += A.pop(360, 260, popS(t, tEnd, 0.35), A.titre0(0, [['JOUR 2', A.C.yellow]], 120) + `<g transform="translate(0 100)">${A.titre0(0, [['QUI EST DERRIÈRE', '#fff']], 64)}</g><g transform="translate(0 180)">${A.titre0(0, [['LA PORTE ? 👀', '#fff']], 64)}</g>`);
    s += A.pop(360, 760, popS(t, tEnd + 0.5, 0.35) * (1 + 0.04 * Math.sin(t * 8)), A.etiquette('🔔 ABONNE-TOI POUR LA SUITE', 540, A.C.yellow, 38));
    s += A.pop(360, 870, popS(t, tEnd + 0.9, 0.35), A.etiquette('💬 VOTE : APPART OU SOURCILS', 560, '#ef5b93', 34));
    s += A.pop(360, 980, popS(t, tEnd + 1.3, 0.35), A.etiquette('📤 ENVOIE ÇA À TA POTE EN PYJAMA', 600, '#7fe0ff', 30));
    return s;
  }
  return s + A.hud(30, 0) + sousTitres(t, p, 1140);
};

function plan(T) {
  let p = TL.plans[TL.plans.length - 1];
  for (const x of TL.plans) if (T >= x.start && T < x.start + x.dur) { p = x; break; }
  return p;
}
function habillage(T, Over = O) {
  const p = plan(T); const t = T - p.start;
  let bump = 0;
  for (const w of p.words) if (A.EMPH.test(w.w) && t > w.s) bump += 0.03 * Math.exp(-(t - w.s) / 0.14);
  const flash = t < 0.08 && p.start > 0 ? `<rect width="720" height="1280" fill="#fff" opacity="${(0.25 * (1 - t / 0.08)).toFixed(2)}"/>` : '';
  const inner = Over[p.id](t, p);
  return `<g transform="translate(360 640) scale(${(1 + bump).toFixed(4)}) translate(-360 -640)">${inner}</g>${flash}`;
}
const overlay = (T) => `<svg xmlns="http://www.w3.org/2000/svg" width="720" height="1280" viewBox="0 0 720 1280">${A.DEFS}${habillage(T)}</svg>`;
const init = () => ({ plans: TL.plans.map(({ id, start, dur, words, voices }) => ({ id, start, dur, words, voices })), total: TL.total, env });

module.exports = { TL, P, overlay, habillage, init, wt, vstart, vend, plan, O, sousTitres, bulle, fleche };
