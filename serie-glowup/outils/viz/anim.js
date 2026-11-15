// Rendu image par image des plans animés : node anim.js jobs.json   (job = {kind, D, beats, expr, yid, out, fps, frames?})
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const { stand, plank, lying, PROPS, stinkLines } = require('./rig');
const { ROOMS2 } = require('./rooms2');
const K = '#1f1a17';
const f1 = v => (+v).toFixed(1);
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const ease = x => { x = clamp(x, 0, 1); return x * x * (3 - 2 * x); };
const ramp = (t, a, b) => ease((t - a) / (b - a));
const S = Math.sin;
const place = (svg, x, feet, s) => `<g transform="translate(${f1(x - 300 * s)},${f1(feet - 1270 * s)}) scale(${s})">${svg}</g>`;
const blinkAt = (t, seed = 0) => ((t + seed * 0.7) % 2.9) > 2.76;
const ex = (e, t, seed) => blinkAt(t, seed) ? e + '_blink' : e;
const idleArms = (t, k = 1) => ({ la: [16 + 3 * k * S(t * 2.1), 8 + 6 * k * S(t * 2.1 + 1)], ra: [16 + 3 * k * S(t * 2.1 + 2), 8 + 6 * k * S(t * 2.1 + 3)] });
const breath = t => 6 * S(t * 2.6);

// caméra : point du monde (fx, fy) envoyé à l'écran (540, 1000), zoom z
function camera(t, D, z, fx, fy, shakes = []) {
  let zz = z * (1 + 0.1 * Math.max(0, 1 - t / 0.22)) * (1 + 0.045 * t / D);
  let dx = 0, dy = 0;
  for (const [at, amp] of shakes) { const u = t - at; if (u >= 0 && u < 0.45) { const a = amp * (1 - u / 0.45); dx += a * S(u * 90); dy += a * S(u * 73 + 1); } }
  const vw = 1080 / zz, vh = 1920 / zz;
  const left = clamp(fx - 540 / zz, 0, 1080 - vw) + dx / zz, top = clamp(fy - 1000 / zz, 0, 1920 - vh) + dy / zz;
  return `scale(${zz.toFixed(4)}) translate(${f1(-left)},${f1(-top)})`;
}
const camH = (t, j, z, x, feet, s, sy = 760, sh = []) => camera(t, j.D, z, x, feet - 1010 * s - 760 / z + (sy - 760) * 0 + 1000 / z - (sy - 760) / z, sh);
function flies(t, t0, cx, cy) {
  if (t < t0) return '';
  return [0, 1, 2, 3, 4].map(i => { const u = t - t0, a = -2.6 + i * 0.55, r = 80 + u * 520; const x = cx + Math.cos(a) * r + 20 * S(u * 30 + i), y = cy + Math.sin(a) * r * 0.8 + 15 * S(u * 40 + i);
    return `<g transform="translate(${f1(x)},${f1(y)})"><ellipse cx="0" cy="0" rx="14" ry="10" fill="#222"/><ellipse cx="-8" cy="-12" rx="10" ry="7" fill="#dff" opacity=".8" transform="rotate(${f1(30 * S(u * 60))})"/><ellipse cx="8" cy="-12" rx="10" ry="7" fill="#dff" opacity=".8"/></g>`; }).join('');
}

const KINDS = {
  // accroche : panique, bras qui s'agitent, sautille
  hook: (t, j) => {
    const jump = Math.abs(S(t * 7)) * 26;
    const y = stand(j.yid, { expr: ex('panique', t), t, la: [150 + 20 * S(t * 9), 160 + 25 * S(t * 9 + 1)], ra: [150 + 20 * S(t * 9 + 2), 160 + 25 * S(t * 9 + 3)], lh: 'open', rh: 'open', bob: breath(t), jiggle: 1, tilt: 4 * S(t * 5), ll: [4, 0], rl: [4, 0] });
    return { scene: 'chambreNuit', act: place(y, 540, 1660 - jump, 0.95), cam: camH(t, j, 1.42, 540, 1660, 0.95, 860, [[0, 26]]) };
  },
  // allongé sur le lit, mange des chips
  bedEat: (t, j) => {
    const cyc = (t % 1.6) / 1.6, up = cyc < 0.5 ? ease(cyc * 2) : 1 - ease((cyc - 0.5) * 2);
    const arm = [70 - 95 * up, 110 - 190 * up];
    const crumbs = (t > 0.5) ? [0, 1, 2].map(i => { const u = ((t * 0.8 + i / 3) % 1); return PROPS.chip(380 + i * 40, 1000 + u * 160); }).join('') : '';
    const y = lying(j.yid, { expr: ex(up > 0.6 ? 'sourire' : 'neutre', t), t, arm, rh: 'open', rp: up > 0.4 ? ['chip', 0, 0, 0] : null, crumbs: 1, y: 1150 });
    const bag = PROPS.chips(630, 1060, 18);
    return { scene: 'chambreNuit', act: `<g transform="translate(265,414) scale(0.62)">${y}</g>${bag}${crumbs}`, cam: camera(t, j.D, 1.75, 470, 1060) };
  },
  // reçoit l'invitation : sursaut puis bras qui tremble
  invite: (t, j) => {
    const jump = t < 0.5 ? S(t / 0.5 * Math.PI) * 60 : 0, sh = 3 * S(t * 40);
    const y = stand(j.yid, { expr: ex('choque', t), t, la: [20, 10], ra: [-20 + sh, -150 + sh], rp: ['invite', 8 + sh, 0, 30], lh: 'open', bob: breath(t), jiggle: t < 0.6 ? 1 : 0.2, tilt: -4 });
    return { scene: 'chambreNuit', act: place(y, 700, 1660 - jump, 0.9), cam: camH(t, j, 1.15, 600, 1660, 0.9, 760, [[0.15, 18]]) };
  },
  // regarde son téléphone, choqué, le pouce qui défile
  phone: (t, j) => {
    const y = stand(j.yid, { expr: ex(j.expr || 'choque', t), t, la: [20 + 2 * S(t * 2), 8], ra: [-10, 205 + 4 * S(t * 6)], rp: ['phone', -20, -10, -40], bob: breath(t), jiggle: 0.3, tilt: -6 + 2 * S(t * 1.5) });
    return { scene: 'chambreNuit', act: place(y, 760, 1660, 0.9), cam: camH(t, j, 1.15, 640, 1660, 0.9, 760, (j.beats || []).slice(1, 2).map(b => [b, 16])) };
  },
  // arrive devant le miroir, se regarde, le ventre qui tremble
  mirror: (t, j) => {
    const walk = 1 - ramp(t, 0, 1.2), x = 330 - 200 * walk, step = S(t * 9) * walk;
    const q = { expr: ex(t < 1.4 ? 'neutre' : 'triste', t), t, ...idleArms(t, 0.6), ll: [18 * step, 4], rl: [-18 * step, 4], bob: breath(t) + Math.abs(step) * 8, jiggle: walk > 0.05 ? 1 : 0.5, tilt: 3 };
    if (t > 1.4) { q.la = [10, 4]; q.ra = [10, 4]; }
    const me = stand(j.yid, q), refl = stand(j.yid, Object.assign({}, q, { t: t + 0.01 }));
    const mirror = `<g><rect x="560" y="420" width="420" height="1120" rx="210" fill="#6e4528" stroke="${K}" stroke-width="8"/>
      <defs><clipPath id="mc"><rect x="590" y="450" width="360" height="1060" rx="180"/></clipPath><linearGradient id="mg" x1="0" x2="1"><stop offset="0" stop-color="#bfe4ff"/><stop offset="1" stop-color="#7fa8d6"/></linearGradient></defs>
      <rect x="590" y="450" width="360" height="1060" rx="180" fill="url(#mg)"/>
      <g clip-path="url(#mc)"><g opacity=".9">${place(`<g transform="translate(600,0) scale(-1,1)">${refl}</g>`, 770, 1640, 0.82)}</g>
      <path d="M640 520 L700 470 M660 640 L800 500" stroke="#fff" stroke-width="16" opacity=".35"/></g>
      <rect x="600" y="1540" width="30" height="120" fill="#5a3820" stroke="${K}" stroke-width="5"/><rect x="910" y="1540" width="30" height="120" fill="#5a3820" stroke="${K}" stroke-width="5"/></g>`;
    return { scene: 'miroir', act: mirror + place(me, x, 1690, 0.92), cam: camH(t, j, 1.05, 560, 1690, 0.92, 740) };
  },
  // Kenzo fait les muscles, Yanis mange ses chips
  score: (t, j) => {
    const fl = S(t * 4) > 0, up = ((t % 1.2) / 1.2 < 0.5);
    const k = stand('KENZO', { expr: ex('sourire', t, 1), t, la: fl ? [95, 178] : [20, 8], ra: fl ? [20, 8] : [95, 178], lh: 'fist', rh: 'fist', flex: 1, bob: breath(t) });
    const y = stand(j.yid, { expr: ex(up ? 'triste' : 'neutre', t), t, la: [30, 60], lp: ['chips', -10, 20, -40], ra: up ? [-25, 205] : [-10, 140], rh: 'open', bob: breath(t), jiggle: 0.4 });
    const crumbs = [0, 1, 2, 3].map(i => { const u = ((t * 0.9 + i / 4) % 1); return PROPS.chip(300 + i * 30, 900 + u * 700); }).join('');
    return { scene: 'chambreNuit', act: place(k, 790, 1640, 0.88) + place(y, 330, 1680, 0.88) + crumbs, cam: camH(t, j, 1.08, 560, 1680, 0.88, 740) };
  },
  // jette les chips dans la poubelle puis poing levé
  throw: (t, j) => {
    const tw = (j.beats && j.beats[0] !== undefined ? 0.5 : 0.5), tt = 1.1;
    let ra, rp = null;
    if (t < tt) { const w = ramp(t, tw, tt); ra = [40 + 110 * w, 60 + 120 * w]; rp = ['chips', 20 + 40 * w]; }
    else if (t < tt + 0.3) { const w = ramp(t, tt, tt + 0.3); ra = [150 - 60 * w, 180 - 120 * w]; }
    else { ra = [165, 178]; }
    const fist = t > tt + 0.5;
    const jump = fist ? Math.max(0, S((t - tt - 0.5) * 6)) * 20 : 0;
    const y = stand(j.yid, { expr: ex(t < tt ? 'colere' : 'determine', t), t, la: fist ? [20, 8] : [30, 40], ra, rh: fist ? 'fist' : 'open', rp, bob: breath(t), jiggle: 0.5 });
    let bag = '';
    if (t >= tt) { const u = clamp((t - tt) / 0.8, 0, 1); const x = 640 + (950 - 640) * u, yy = 820 - 500 * S(u * Math.PI) * 0.8 + 600 * u; if (u < 1) bag = PROPS.chips(x, yy, u * 540); }
    return { scene: 'chambreNuit', act: place(y, 480, 1660 - jump, 0.9) + bag, cam: camH(t, j, 1.12, 600, 1660, 0.9, 760, [[tt + 0.8, 22]]) };
  },
  // pointe la caméra
  point: (t, j) => {
    const pump = S(t * 5) * 8;
    const y = stand(j.yid, { expr: ex(j.expr || 'determine', t), t, la: [16, 8], ra: [80 + pump, 95 + pump], rh: 'point', bob: breath(t), jiggle: 0.3, tilt: -3 });
    return { scene: 'chambreNuit', act: place(y, 460, 1660, 0.95), cam: camH(t, j, 1.3 + 0.12 * t / j.D, 520, 1660, 0.95, 800) };
  },
  // pompes synchronisées sur la voix, puis s'écrase
  pushup: (t, j) => {
    const b = j.beats || [], reps = b.slice(1, 6), crashAt = b[6] !== undefined ? b[6] + 0.45 : j.D * 0.8;
    let d = 0.05 + 0.04 * S(t * 30);
    for (const r of reps) { const u = t - r; if (u >= 0 && u < 0.7) d = Math.max(d, S(u / 0.7 * Math.PI) * 0.95); }
    if (t > crashAt) d = 1 + ramp(t, crashAt, crashAt + 0.25) * 0.3;
    const y = plank(j.yid, { d, t, expr: ex(t > crashAt ? 'larmes' : 'panique', t), jiggle: t > crashAt ? 1 : 0.3 });
    const count = reps.filter(r => t > r).length;
    return { scene: 'salleMuscu', act: `<g transform="translate(260,520) scale(0.8)">${y}</g>`, cam: camera(t, j.D, 1.25, 580, 1330, [[crashAt + 0.2, 34]]), count };
  },
  // épuisé au sol, pouce levé tremblant
  lieFloor: (t, j) => {
    const r = ramp(t, 0.6, 2.0);
    const y = lying(j.yid, { expr: ex('triste', t), t, arm: [100 - 100 * r + 3 * S(t * 30) * r, 60 - 60 * r + 3 * S(t * 30) * r], rh: r > 0.5 ? 'thumb' : 'open', y: 1150, breath: 2.2, stink: 0 });
    return { scene: 'salleMuscu', act: `<g transform="translate(280,640) scale(0.72)">${y}</g>`, cam: camera(t, j.D, 1.3, 560, 1360) };
  },
  // écrit « 2 L » sur la bouteille, maman émue
  water: (t, j) => {
    const wr = 6 * S(t * 14);
    const y = stand(j.yid, { expr: ex('determine', t), t, la: [-15, -125], lp: ['bottle', 0, 40, 120], ra: [-20 + wr * 0.4, -115 + wr], rp: ['marker', -30 + wr], bob: breath(t), jiggle: 0.3, tilt: -5 });
    const wipe = (t % 2.4) < 1.0;
    const n = stand('NADIA', { expr: ex('larmes', t, 2), t, la: [20, 8], ra: wipe ? [-20, 200] : [16, 8], bob: breath(t + 1) });
    return { scene: 'cuisine', act: place(n, 820, 1600, 0.86) + place(y, 380, 1680, 0.92), cam: camH(t, j, 1.08, 580, 1680, 0.92, 720) };
  },
  // lève les bras : nuage vert et mouches qui fuient
  armsUp: (t, j) => {
    const b = j.beats || [], up = b[1] !== undefined ? b[1] : j.D * 0.4, r = ramp(t, up, up + 0.4);
    const y = stand(j.yid, { expr: ex(r > 0.5 ? 'sourire' : 'inquiet', t), t, la: [16 + 150 * r, 8 + 165 * r], ra: [16 + 150 * r, 8 + 165 * r], bob: breath(t), jiggle: 0.4, stink: 0.5 + r * 0.5 });
    const cloud = r > 0 ? `<g opacity="${f1(r * 0.85)}">${stinkLines([[280, 900], [800, 900], [220, 1100], [860, 1080], [540, 760]], t * 1.5, 0.9)}</g>` : '';
    return { scene: 'chambreNuit', act: place(y, 540, 1660, 0.92) + cloud + flies(t, up + 0.3, 540, 1000), cam: camH(t, j, 1.2, 540, 1660, 0.92, 760, [[up + 0.3, 14]]) };
  },
  // ---------- épisode 2
  armRaise: (t, j) => {
    const b = j.beats || [], r = ramp(t, 0.15, 0.5), turn = ramp(t, (b[1] || 1.5) + 0.7, (b[1] || 1.5) + 1.2);
    const y = stand(j.yid, { expr: ex(r > 0.5 ? 'choque' : 'neutre', t), t, la: [16, 8], ra: [16 + 150 * r, 8 + 168 * r], bob: breath(t), jiggle: 0.5, stink: 1 });
    const cloud = `<g opacity="${f1(r * 0.9)}">${stinkLines([[560, 900], [620, 800], [680, 1000], [500, 760]], t * 1.6, 0.95)}</g>`;
    const sx = 1 - 1.3 * turn, sp = t * 25;
    const fan = `<g transform="translate(880,1560)"><rect x="-10" y="-420" width="20" height="400" fill="#777" stroke="${K}" stroke-width="4"/><ellipse cx="0" cy="-10" rx="90" ry="22" fill="#666" stroke="${K}" stroke-width="5"/>
      <g transform="translate(0,-470) scale(${f1(Math.abs(sx) < 0.15 ? 0.15 : sx)},1)"><circle r="130" fill="${sx < 0 ? '#888' : '#dfe8ee'}" stroke="${K}" stroke-width="7"/>
      ${sx > 0 ? [0, 1, 2].map(i => `<ellipse cx="0" cy="-60" rx="34" ry="62" fill="#5aa9e6" stroke="${K}" stroke-width="4" transform="rotate(${f1(sp * 57 + i * 120)})"/>`).join('') + `<circle r="22" fill="#2f6fd6" stroke="${K}" stroke-width="4"/>` : `<circle r="60" fill="#666"/>`}
      ${[...Array(8)].map((_, i) => `<path d="M0 0 L${f1(130 * Math.cos(i * 0.785))} ${f1(130 * Math.sin(i * 0.785))}" stroke="${K}" stroke-width="3" opacity=".5"/>`).join('')}</g></g>`;
    return { scene: 'chambreNuit', act: fan + place(y, 430, 1680, 0.95) + cloud, cam: camH(t, j, 1.25, 600, 1680, 0.95, 820, [[0, 24], [(b[1] || 1.5) + 0.8, 14]]) };
  },
  sore: (t, j) => {
    const c = (t % 2.2) / 2.2, w = c < 0.7 ? ease(c / 0.7) : 1 - ease((c - 0.7) / 0.3), tr = 4 * S(t * 45) * w;
    const y = stand(j.yid, { expr: ex(w > 0.5 ? 'panique' : 'triste', t), t, la: [20 + 55 * w + tr, 20 + 70 * w], ra: [20 + 55 * w - tr, 20 + 70 * w], bob: breath(t), jiggle: 0.6, tilt: 5 * S(t * 3) });
    const tee = `<g transform="translate(${f1(540 - 30)},${f1(1080 - 260 * w)})"><path d="M-170 -60 L-90 -110 L90 -110 L170 -60 L130 0 L90 -20 L90 140 L-90 140 L-90 -20 L-130 0 Z" fill="#e5483f" stroke="${K}" stroke-width="6"/></g>`;
    return { scene: 'chambreNuit', act: place(y, 540, 1680, 0.92) + tee, cam: camH(t, j, 1.15, 540, 1680, 0.92, 760) };
  },
  sofiane: (t, j) => {
    const walk = 1 - ramp(t, 0, 1.3), x = 820 + 430 * walk, step = S(t * 10) * walk, blow = (t % 1.5) < 0.4 && walk < 0.1;
    const sof = stand('SOFIANE', { expr: ex(blow ? 'colere' : 'sourire', t, 1), t, la: [20 + 20 * step, 8], ra: blow ? [140, 175] : [-15, -130], rp: blow ? null : ['kebab', 0, 0, 20], ll: [16 * step, 4], rl: [-16 * step, 4], bob: breath(t) + Math.abs(step) * 10, whistle: 1, blow });
    const y = lying(j.yid, { expr: ex('choque', t), t, arm: [70, 110], y: 1150 });
    return { scene: 'chambreNuit', act: `<g transform="translate(265,414) scale(0.62)">${y}</g>` + place(sof, x, 1720, 0.86), cam: camH(t, j, 1.1, 600, 1720, 0.86, 760, [[1.3, 12]]) };
  },
  napkin: (t, j) => {
    const sh = 4 * S(t * 3);
    const sof = stand('SOFIANE', { expr: ex('sourire', t, 1), t, la: [16, 8], lp: ['kebab', 0, 0, 20], ra: [-35, -150 + sh], rp: ['napkin', -6, -160, 40], bob: breath(t), whistle: 1, tilt: 4 });
    const y = stand(j.yid, { expr: ex('mefiant', t), t, la: [-25, -105], ra: [-25, -105], bob: breath(t + 1), jiggle: 0.2, tilt: -5 + 3 * S(t * 2) });
    return { scene: 'chambreNuit', act: place(y, 300, 1700, 0.88) + place(sof, 760, 1700, 0.86), cam: camH(t, j, 1.08, 560, 1700, 0.88, 740) };
  },
  nose: (t, j) => {
    const b = j.beats || [], walk = 1 - ramp(t, 0, 1.1), x = 790 + 400 * walk, step = S(t * 10) * walk, pinch = t > (b[1] || 1.6) - 0.3;
    const n = stand('NADIA', { expr: ex(pinch ? 'colere' : 'neutre', t, 2), t, la: [-15, -70], lp: ['basket', 0, 40, 30], ra: pinch ? [-22, 198] : [16, 8], ll: [14 * step, 3], rl: [-14 * step, 3], bob: breath(t) + Math.abs(step) * 8, tilt: pinch ? -8 : 0 });
    const y = stand(j.yid, { expr: ex(pinch ? 'inquiet' : 'neutre', t), t, la: [150, 200], ra: [16, 8], bob: breath(t), jiggle: 0.3, stink: 1, tilt: 5 });
    const cloud = `<g opacity=".8">${stinkLines([[480, 1000], [560, 880], [420, 820]], t * 1.5, 0.9)}</g>`;
    return { scene: 'chambreNuit', act: place(y, 330, 1700, 0.9) + cloud + place(n, x, 1700, 0.86), cam: camH(t, j, 1.08, 560, 1700, 0.9, 740, [[(b[1] || 1.6), 12]]) };
  },
  shower: (t, j) => {
    const w = S(t * 12);
    const y = stand(j.yid, { expr: ex(S(t * 1.3) > 0 ? 'determine' : 'sourire', t), t, la: [150 + 8 * w, 205 + 12 * w], ra: [-30 + 8 * w, -115 + 22 * w], rp: ['sponge', 20 * w, 0, 10], bob: breath(t), jiggle: 0.8, stink: 0, towel: 1, tilt: 4 * w });
    const bub = [...Array(12)].map((_, i) => { const u = (t * 0.6 + i / 12) % 1, x = 300 + (i * 97) % 480 + 20 * S(t * 3 + i), yy = 1450 - u * 900; return `<circle cx="${f1(x)}" cy="${f1(yy)}" r="${f1(14 + (i % 4) * 8)}" fill="#fff" fill-opacity=".55" stroke="#9fd4ff" stroke-width="4" opacity="${f1(1 - u)}"/>`; }).join('');
    return { scene: 'salleDeBain', act: place(y, 460, 1700, 0.92) + bub, cam: camH(t, j, 1.12, 520, 1700, 0.92, 760) };
  },
  deo: (t, j) => {
    const b = j.beats || [], fl = t > (b[2] || 3.2) - 0.2, side = Math.floor(t / 1.2) % 2;
    let q;
    if (!fl) q = side ? { la: [-55, -95], lp: ['deo', 70, 0, 0], ra: [150, 175] } : { la: [150, 175], ra: [-55, -95], rp: ['deo', -70, 0, 0] };
    else q = { la: [95, 178], ra: [95, 178], lh: 'fist', rh: 'fist' };
    const y = stand(j.yid, Object.assign({ expr: ex(fl ? 'sourire' : 'determine', t), t, bob: breath(t) + (fl ? Math.abs(S(t * 6)) * 12 : 0), jiggle: 0.5, stink: 0, towel: 1 }, q));
    const spray = fl ? '' : [...Array(10)].map((_, i) => { const u = (t * 3 + i / 10) % 1, dx = side ? -1 : 1; return `<circle cx="${f1(540 + dx * (120 + u * 160))}" cy="${f1(1040 - u * 60 + (i % 3 - 1) * 30 * u)}" r="${f1(6 + u * 18)}" fill="#e8f6ff" opacity="${f1(0.8 - u * 0.8)}"/>`; }).join('');
    const spark = fl ? [0, 1, 2, 3].map(i => { const a = t * 2 + i * 1.57; return `<text x="${f1(540 + Math.cos(a) * 330)}" y="${f1(900 + Math.sin(a) * 260)}" font-family="Lilita One" font-size="64" fill="#ffd23a" stroke="${K}" stroke-width="3">✦</text>`; }).join('') : '';
    return { scene: 'salleDeBain', act: place(y, 540, 1700, 0.92) + spray + spark, cam: camH(t, j, 1.15, 540, 1700, 0.92, 760, fl ? [[(b[2] || 3.2) - 0.2, 12]] : []) };
  },
  sniff: (t, j) => {
    const b = j.beats || [], walk = 1 - ramp(t, 0, 1.0), x = 720 + 380 * walk, step = S(t * 10) * walk, ok = t > (b[2] || 2.6) - 0.4;
    const n = stand('NADIA', { expr: ex(ok ? 'sourire' : 'mefiant', t, 2), t, la: [16, 8], ra: ok ? [30, 160] : [16, 8], rh: ok ? 'thumb' : 'open', ll: [14 * step, 3], rl: [-14 * step, 3], bob: breath(t) + Math.abs(step) * 8 + (ok ? 0 : 4 * S(t * 14)), tilt: ok ? 0 : -12, hx: ok ? 0 : -20 });
    const y = stand(j.yid, { expr: ex(ok ? 'sourire' : 'inquiet', t), t, ...idleArms(t), bob: breath(t) + (ok ? Math.abs(S(t * 6)) * 10 : 0), jiggle: 0.3, stink: 0 });
    const spark = ok ? [0, 1, 2].map(i => { const a = t * 2 + i * 2.1; return `<text x="${f1(330 + Math.cos(a) * 260)}" y="${f1(900 + Math.sin(a) * 220)}" font-family="Lilita One" font-size="60" fill="#ffd23a" stroke="${K}" stroke-width="3">✦</text>`; }).join('') : '';
    return { scene: 'chambreNuit', act: place(y, 330, 1700, 0.9) + place(n, x, 1700, 0.86) + spark, cam: camH(t, j, 1.08, 560, 1700, 0.9, 740) };
  },
  sneakers: (t, j) => {
    const y = stand(j.yid, { expr: ex('inquiet', t), t, la: [-20, -150], lp: ['sneaker', -10 + 4 * S(t * 3), 10, 0], ra: [-20, -150], rp: ['sneaker', 10 - 4 * S(t * 3), -10, 0], bob: breath(t), jiggle: 0.3, tilt: 7 * S(t * 2.2) });
    return { scene: 'chambreNuit', act: place(y, 540, 1680, 0.95), cam: camH(t, j, 1.3, 540, 1680, 0.95, 820) };
  },
  // vote : se gratte la tête puis haussement d'épaules
  vote: (t, j) => {
    const s = (t % 2) < 1;
    const y = stand(j.yid, { expr: ex('inquiet', t), t, la: s ? [150, 200] : [40, 20], ra: s ? [40, 20] : [150, 200], bob: breath(t), jiggle: 0.3, tilt: s ? 6 : -6 });
    return { scene: 'chambreNuit', act: place(y, 540, 1700, 0.9), cam: camH(t, j, 1.1, 540, 1700, 0.9, 700) };
  },
};

const css = `<style>@font-face{font-family:'Lilita One';src:url(file:///root/.fonts/LilitaOne-Regular.ttf)}@font-face{font-family:Anton;src:url(file:///root/.fonts/Anton-Regular.ttf)}body{margin:0;background:#000}</style>`;
async function main() {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2]));
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  for (const j of jobs) {
    fs.mkdirSync(j.out, { recursive: true });
    const fps = j.fps || 30, N = j.frames || Math.ceil(j.D * fps);
    const first = KINDS[j.kind](0, j);
    await p.setContent(css + `<svg id="s" xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920"><g id="cam"><g id="bg">${ROOMS2[first.scene]()}</g><g id="act"></g></g></svg>`);
    await p.evaluate(() => document.fonts.ready);
    const times = j.times || [...Array(N).keys()].map(i => i / fps);
    for (let i = 0; i < times.length; i++) {
      const r = KINDS[j.kind](times[i], j);
      await p.evaluate(([a, c]) => { document.getElementById('act').innerHTML = a; document.getElementById('cam').setAttribute('transform', c); }, [r.act, r.cam]);
      await p.screenshot({ path: path.join(j.out, `f_${String(i).padStart(5, '0')}.jpg`), type: 'jpeg', quality: 90 });
    }
  }
  await b.close();
}
if (require.main === module) main();
module.exports = { KINDS };
