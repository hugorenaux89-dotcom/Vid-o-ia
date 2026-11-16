// Plans génériques paramétrés (épisodes 4 à 30). 🎬 `kind cle=valeur ...` → j.p
const { ensureY } = require('./look');
function install(X) {
  const { KINDS, camera, camH, place, ex, breath, idleArms, flies, park, jog, ramp, ease, clamp, S, f1, K, stand, plank, lying, PROPS, stinkLines } = X;
  const P = j => j.p || {};
  const B = (j, i, d) => { const b = j.beats || []; return b[i] !== undefined ? b[i] : d; };
  const Y = j => { const id = P(j).stage ? 'Y' + P(j).stage : j.yid; ensureY(id); return id; };

  // ---------- gestes : (t, j, side) -> morceau de pose
  // accent : petite impulsion au début de chaque phrase de la voix off
  const acc = (t, j) => Math.max(0, ...((j && j.beats) || []).map(b => { const u = t - b; return u < 0 ? 0 : u < 0.25 ? u / 0.25 : Math.max(0, 1 - (u - 0.25) / 0.9); }));
  const G = {
    idle: t => idleArms(t),
    talk: (t, j) => { const a = acc(t, j); return { la: [16 + 6 * a, 10 + 20 * a], ra: [22 + 30 * a, 30 + 85 * a], tilt: 3 * a }; },
    wave: t => ({ la: [16, 8], ra: [150, 160 + 25 * S(t * 9)] }),
    point: (t, j) => { const a = acc(t, j); return { la: [16, 8], ra: [76 + 8 * a, 92 + 6 * a], rh: 'point' }; },
    fist: t => ({ la: [16, 8], ra: [165, 178], rh: 'fist', bob: -Math.max(0, S(t * 5)) * 14 }),
    flex: t => ({ la: [95, 178], ra: [95, 178], lh: 'fist', rh: 'fist', bob: Math.abs(S(t * 4)) * -8 }),
    jump: t => ({ la: [155 + 10 * S(t * 8), 170], ra: [155 + 10 * S(t * 8 + 1), 170], bob: -Math.abs(S(t * 6)) * 60, jiggle: 1 }),
    panic: t => ({ la: [150 + 20 * S(t * 9), 160 + 25 * S(t * 9 + 1)], ra: [150 + 20 * S(t * 9 + 2), 160 + 25 * S(t * 9 + 3)], bob: -Math.abs(S(t * 7)) * 24, jiggle: 1 }),
    facepalm: t => ({ la: [16, 8], ra: [-20, 205], tilt: 8 }),
    think: t => ({ la: [-25, -110], ra: [-15, 200], rh: 'point', tilt: 4 }),
    shrug: (t, j) => { const u = acc(t, j); return { la: [40 + 30 * u, 110], ra: [40 + 30 * u, 110], tilt: 5 * u }; },
    eat: t => { const c = (t % 1.4) / 1.4, u = c < 0.5 ? ease(c * 2) : 1 - ease((c - 0.5) * 2); return { la: [16, 8], ra: [-10 - 15 * u, 120 + 85 * u] }; },
    drink: t => { const u = 0.5 + 0.5 * S(t * 2); return { la: [16, 8], ra: [-15, 160 + 45 * u], rpRot: -20 - 60 * u }; },
    phone: t => ({ la: [20, 8], ra: [-10, 205 + 4 * S(t * 6)], rpDefault: 'phone', tilt: -6 }),
    holdUp: t => ({ la: [150, 175], ra: [150, 175], bob: -Math.abs(S(t * 5)) * 16 }),
    show: t => ({ la: [16, 8], ra: [-25, -150 + 5 * S(t * 3)] }),
    showBoth: t => ({ la: [-20, -145], ra: [-20, -145] }),
    dance: t => { const s = S(t * 5); return { la: [90 + 50 * s, 150 + 30 * s], ra: [90 - 50 * s, 150 - 30 * s], ll: [12 * s, 0], rl: [-12 * s, 0], lift: [Math.max(0, s) * 0.4, Math.max(0, -s) * 0.4], bob: -Math.abs(s) * 26, tilt: 8 * s, jiggle: 1 }; },
    cry: t => ({ la: [-20, 200], ra: [-20, 200], tilt: 6 * S(t * 8) }),
    scratch: t => ({ la: [16, 8], ra: [150, 205 + 10 * S(t * 12)], tilt: 6 }),
    clap: t => { const u = Math.abs(S(t * 7)); return { la: [40, 150 + 40 * u], ra: [40, 150 + 40 * u], bob: -u * 6 }; },
    thumbs: t => ({ la: [16, 8], ra: [30, 160], rh: 'thumb', bob: -Math.abs(S(t * 4)) * 8 }),
    thumbs2: t => ({ la: [30, 160], ra: [30, 160], lh: 'thumb', rh: 'thumb', bob: -Math.abs(S(t * 4)) * 10 }),
    bow: t => ({ la: [10, 4], ra: [-20, -110], bob: 20 + 10 * S(t * 2), tilt: 0 }),
    spray: t => ({ la: [16, 8], ra: [-30, 175 + 10 * S(t * 10)] }),
    brush: t => ({ la: [16, 8], ra: [-20 + 4 * S(t * 18), 205 + 8 * S(t * 18)], rpDefault: 'toothbrush' }),
    cream: t => ({ la: [-20 + 4 * S(t * 6), 205 + 8 * S(t * 6)], ra: [-20 + 4 * S(t * 6 + 2), 205 + 8 * S(t * 6 + 2)] }),
    comb: t => ({ la: [16, 8], ra: [150, 200 + 15 * S(t * 6)], rpDefault: 'comb' }),
    armsCross: t => ({ la: [-25, -105], ra: [-25, -105], tilt: 0 }),
    hips: t => ({ la: [40, -40], ra: [40, -40], tilt: 0 }),
    sad: t => ({ la: [6, 2], ra: [6, 2], bob: 10, tilt: 8 }),
    walk: t => { const s = S(t * 8); return { ll: [16 * s, 4], rl: [-16 * s, 4], la: [16 - 14 * s, 8], ra: [16 + 14 * s, 8], bob: -Math.abs(s) * 10 }; },
    curl: t => { const u = 0.5 + 0.5 * S(t * 3.6); return { la: [12, 20 + 150 * u], ra: [12, 20 + 150 * (1 - u)], lp: ['dumbbell', 90], rp: ['dumbbell', 90], lh: 'fist', rh: 'fist', jiggle: 0.5 }; },
    squat: t => { const u = 0.5 + 0.5 * S(t * 3); return { la: [80, 90], ra: [80, 90], lift: [0.6 * u, 0.6 * u], ll: [10 * u, 0], rl: [10 * u, 0], bob: 90 * u, jiggle: 1 }; },
    stretch: t => ({ la: [165 + 8 * S(t * 2), 178], ra: [165 + 8 * S(t * 2), 178], tilt: 12 * S(t * 1.6) }),
    yawn: t => ({ la: [150, 175], ra: [16, 8], tilt: -6 }),
    no: t => ({ la: [-30, -170 + 10 * S(t * 6)], ra: [-30, -170 + 10 * S(t * 6)], tilt: 10 * S(t * 7) }),
    kneel: t => ({ la: [16, 8], ra: [-20, -150], lift: [0.9, 0.2], bob: 120 }),
    hug: t => ({ la: [-40, -100], ra: [-40, -100] }),
    tie: t => ({ la: [-20, 200 + 4 * S(t * 8)], ra: [-20, 200 - 4 * S(t * 8)], tilt: -4 }),
    look: t => ({ ...idleArms(t), tilt: -6 }),
  };
  function pose(gest, t, j, extra = {}) {
    const g = (G[gest] || G.idle)(t, j);
    const q = Object.assign({ bob: breath(t), jiggle: 0 }, g);
    if (g.bob !== undefined) q.bob = g.bob + breath(t) * 0.5;
    const pr = extra.prop || g.rpDefault;
    if (pr && !q.rp) q.rp = [pr, g.rpRot || 0, 0, 0];
    if (extra.lprop) q.lp = [extra.lprop, 0, 0, 0];
    delete q.rpDefault; delete q.rpRot;
    return q;
  }
  // ---------- effets
  function fx(list, t, cx = 540, cy = 900) {
    let s = '';
    for (const f of (list || '').split(',').filter(Boolean)) {
      if (f === 'sparkle') s += [0, 1, 2, 3, 4].map(i => { const a = t * 2.2 + i * 1.26; return `<text x="${f1(cx + Math.cos(a) * 330)}" y="${f1(cy + Math.sin(a) * 280)}" font-family="Lilita One" font-size="${56 + 14 * S(t * 6 + i)}" fill="#ffd23a" stroke="${K}" stroke-width="3">✦</text>`; }).join('');
      if (f === 'hearts') s += [0, 1, 2, 3].map(i => { const u = (t * 0.6 + i / 4) % 1; return `<text x="${f1(cx - 260 + i * 170 + 20 * S(t * 3 + i))}" y="${f1(cy + 300 - u * 600)}" font-size="70" fill="#ff4d7d" opacity="${f1(1 - u)}" font-family="Lilita One">♥</text>`; }).join('');
      if (f === 'zzz') s += [0, 1, 2].map(i => { const u = (t * 0.5 + i / 3) % 1; return `<text x="${f1(cx + 120 + u * 160)}" y="${f1(cy - 100 - u * 300)}" font-family="Lilita One" font-size="${50 + u * 50}" fill="#fff" stroke="${K}" stroke-width="3" opacity="${f1(1 - u)}">Z</text>`; }).join('');
      if (f === 'sweat') s += [0, 1, 2].map(i => { const u = (t * 1.4 + i / 3) % 1; return `<path d="M${f1(cx - 200 + i * 200)} ${f1(cy - 200 + u * 400)} q-14 26 0 34 q14 -8 0 -34 Z" fill="#9fdcff" stroke="${K}" stroke-width="3" opacity="${f1(1 - u)}"/>`; }).join('');
      if (f === 'stink') s += `<g opacity=".85">${stinkLines([[cx - 220, cy + 100], [cx + 220, cy + 80], [cx, cy - 40]], t * 1.5, 0.9)}</g>`;
      if (f === 'notes') s += [0, 1, 2].map(i => { const u = (t * 0.7 + i / 3) % 1; return `<text x="${f1(cx - 300 + i * 300 + 30 * S(t * 4 + i))}" y="${f1(cy + 100 - u * 500)}" font-size="70" fill="#4fe1ff" stroke="${K}" stroke-width="3" opacity="${f1(1 - u)}" font-family="Lilita One">♪</text>`; }).join('');
      if (f === 'confetti') s += [...Array(26)].map((_, i) => { const u = (t * 0.5 + i / 26) % 1; return `<rect x="${f1((i * 83) % 1080 + 30 * S(t * 3 + i))}" y="${f1(-50 + u * 1900)}" width="18" height="30" fill="${['#ff4d7d', '#ffd23a', '#4fe1ff', '#5bbf4a', '#fff'][i % 5]}" transform="rotate(${f1(t * 200 + i * 40)} ${f1((i * 83) % 1080)} ${f1(-50 + u * 1900)})"/>`; }).join('');
      if (f === 'glow') s += `<circle cx="${cx}" cy="${cy}" r="${f1(420 + 30 * S(t * 3))}" fill="#fff6b0" opacity=".18"/>`;
      if (f === 'flash') s += t < 0.25 ? `<rect width="1080" height="1920" fill="#fff" opacity="${f1(1 - t / 0.25)}"/>` : '';
      if (f === 'flies') s += flies(t, 0.2, cx, cy);
      if (f === 'tears') s += [0, 1].map(i => { const u = (t * 1.2 + i / 2) % 1; return `<path d="M${f1(cx - 80 + i * 160)} ${f1(cy - 330 + u * 300)} q-12 24 0 32 q12 -8 0 -32 Z" fill="#7cc8ff" stroke="${K}" stroke-width="3" opacity="${f1(1 - u)}"/>`; }).join('');
      if (f === 'steam') s += [0, 1, 2].map(i => { const u = (t * 0.8 + i / 3) % 1; return `<path d="M${f1(cx - 150 + i * 150)} ${f1(cy - 340 - u * 200)} q-20 -30 0 -60 q20 -30 0 -60" fill="none" stroke="#fff" stroke-width="10" stroke-linecap="round" opacity="${f1(0.7 - u * 0.7)}"/>`; }).join('');
    }
    return s;
  }
  const SHOT = { close: [1.4, 860], med: [1.15, 770], wide: [1.02, 700] };
  const SC = j => P(j).scene || 'chambreJour';

  // ---------- un seul personnage
  KINDS.solo = (t, j) => {
    const p = P(j), id = Y(j), [z, sy] = SHOT[p.shot || 'med'];
    const gest = (t > +(p.at2 || 999) && p.gest2) ? p.gest2 : p.gest;
    const q = pose(gest || 'idle', t, j, p);
    q.expr = ex((t > +(p.at2 || 999) && p.expr2) ? p.expr2 : j.expr, t); q.t = t;
    const x = +(p.x || 540), feet = 1690;
    const y = stand(id, q);
    return { scene: SC(j), act: place(y, x, feet, 0.92) + fx(p.fx, t, x, 920), cam: camH(t, j, z, x, feet, 0.92, sy, p.shake ? [[0.05, 22]] : []) };
  };
  // ---------- deux personnages
  KINDS.duo = (t, j) => {
    const p = P(j), id = Y(j), [z, sy] = SHOT[p.shot || 'wide'];
    const left = p.side === 'right' ? 760 : 320, right = p.side === 'right' ? 320 : 760;
    const walk = p.enter ? 1 - ramp(t, 0, 1.2) : 0, step = S(t * 9) * walk;
    const gest = (t > +(p.at2 || 999) && p.gest2) ? p.gest2 : p.gest;
    const ogest = (t > +(p.oat2 || p.at2 || 999) && p.ogest2) ? p.ogest2 : p.ogest;
    const qy = pose(gest || 'idle', t, j, { prop: p.prop, lprop: p.lprop }); qy.expr = ex((t > +(p.at2 || 999) && p.expr2) ? p.expr2 : j.expr, t); qy.t = t;
    const qo = pose(ogest || 'talk', t + 0.7, j, { prop: p.oprop, lprop: p.olprop }); qo.expr = ex((t > +(p.oat2 || p.at2 || 999) && p.oexpr2) ? p.oexpr2 : (p.oexpr || 'sourire'), t, 1); qo.t = t;
    if (walk > 0.02) { qo.ll = [16 * step, 4]; qo.rl = [-16 * step, 4]; qo.bob = (qo.bob || 0) + Math.abs(step) * 10; }
    if (p.other === 'SOFIANE') qo.whistle = p.whistle ? 1 : 0;
    const ox = right + (right > 540 ? 1 : -1) * 450 * walk;
    const other = place(stand(p.other || 'SOFIANE', qo), ox, 1700, 0.88), me = place(stand(id, qy), left, 1700, 0.9);
    return { scene: SC(j), act: (p.front === 'other' ? me + other : other + me) + fx(p.fx, t, 540, 940), cam: camH(t, j, z, 540, 1700, 0.9, sy - 30, p.shake ? [[0.05, 18]] : []) };
  };
  // ---------- trois personnages (Yanis au centre)
  KINDS.trio = (t, j) => {
    const p = P(j), id = Y(j);
    const qa = pose(p.agest || 'idle', t + 0.4, j, { prop: p.aprop }); qa.expr = ex(p.aexpr || 'sourire', t, 1); qa.t = t;
    const qb = pose(p.bgest || 'idle', t + 0.9, j, { prop: p.bprop }); qb.expr = ex(p.bexpr || 'sourire', t, 2); qb.t = t;
    const gest = (t > +(p.at2 || 999) && p.gest2) ? p.gest2 : p.gest;
    const qy = pose(gest || 'idle', t, j, { prop: p.prop }); qy.expr = ex((t > +(p.at2 || 999) && p.expr2) ? p.expr2 : j.expr, t); qy.t = t;
    return { scene: SC(j), act: place(stand(p.a || 'NADIA', qa), 220, 1640, 0.78) + place(stand(p.b || 'SOFIANE', qb), 860, 1640, 0.78) + place(stand(id, qy), 540, 1720, 0.9) + fx(p.fx, t, 540, 940), cam: camH(t, j, 1.0, 540, 1720, 0.9, 700) };
  };
  // ---------- assis dans un fauteuil (barbier, dentiste, médecin, opticien)
  KINDS.chair = (t, j) => {
    const p = P(j), id = Y(j), s = 0.9, feet = 1720, hip = feet - (1270 - 860) * s + 110 * s;
    const w = S(t * 7);
    const qy = { expr: ex((t > +(p.at2 || 999) && p.expr2) ? p.expr2 : j.expr, t), t, lift: [0.9, 0.9], ll: [14, -6], rl: [14, -6], la: [40, 30], ra: [40, 30], bob: breath(t) * 0.5, jiggle: 0.2, tilt: 3 * S(t * 1.3) };
    if (p.gest === 'thumbs' && t > +(p.at2 || 0)) { qy.ra = [30, 160]; qy.rh = 'thumb'; }
    if (p.gest === 'mirror' && t > +(p.at2 || 0)) { qy.ra = [-25, -150]; qy.rp = ['glassesNew', 0]; }
    const yan = place(stand(id, qy), 430, feet + 110 * s, s);
    const qp = { expr: ex(p.oexpr || 'sourire', t, 1), t, la: [16, 8], ra: [-40 + 6 * w, -120 + 14 * w], rp: [p.tool || 'clippers', -60 + 20 * w], bob: breath(t + 1), tilt: -6 };
    const pro = place(stand(p.pro || 'MOUSSA', qp), 820, 1700, 0.86);
    const col = { barbier: '#9a1d2a', dentiste: '#2a8a9a', medecin: '#2a8a6a', opticien: '#2f6fd6' }[SC(j)] || '#555';
    const chair = `<g transform="translate(430,${f1(hip + 40)})"><rect x="-150" y="-430" width="300" height="300" rx="50" fill="${col}" stroke="${K}" stroke-width="7"/><rect x="-14" y="40" width="28" height="${f1(feet - hip - 70)}" fill="#888" stroke="${K}" stroke-width="4"/><ellipse cx="0" cy="${f1(feet - hip - 30)}" rx="140" ry="22" fill="#666" stroke="${K}" stroke-width="5"/></g>`;
    const seat = `<rect x="260" y="${f1(hip - 12)}" width="340" height="70" rx="28" fill="${col}" stroke="${K}" stroke-width="7"/><rect x="230" y="${f1(hip - 70)}" width="50" height="40" rx="12" fill="#333" stroke="${K}" stroke-width="4"/><rect x="580" y="${f1(hip - 70)}" width="50" height="40" rx="12" fill="#333" stroke="${K}" stroke-width="4"/>`;
    const cape = p.cape ? `<path d="M${f1(430 - 210)} ${f1(hip - 330)} L${f1(430 + 210)} ${f1(hip - 330)} L${f1(430 + 250)} ${f1(hip + 20)} L${f1(430 - 250)} ${f1(hip + 20)} Z" fill="#f4f4f4" stroke="${K}" stroke-width="6" opacity=".95"/>` : '';
    const hairs = p.hairs ? [...Array(6)].map((_, i) => { const u = (t * 0.9 + i / 6) % 1; return `<path d="M${f1(400 + i * 22)} ${f1(hip - 560 + u * 500)} q8 10 0 20" fill="none" stroke="#1c1511" stroke-width="5" opacity="${f1(1 - u)}"/>`; }).join('') : '';
    return { scene: SC(j), act: chair + yan + seat + cape + pro + hairs + fx(p.fx, t, 430, 900), cam: camH(t, j, 1.1, 560, feet + 110 * s, s, 800) };
  };
  // ---------- salle de sport : exercices (avec Kenzo qui coache)
  KINDS.gym = (t, j) => {
    const p = P(j), id = Y(j), ex2 = p.ex || 'curl';
    if (ex2 === 'pushup') {
      const reps = (j.beats || []).slice(1, 6), dd = Math.max(0.05, ...reps.map(r => { const u = t - r; return u >= 0 && u < 0.7 ? S(u / 0.7 * Math.PI) * 0.95 : 0.05; }));
      const y = plank(id, { d: p.auto ? 0.5 + 0.45 * S(t * 4) : dd, t, expr: ex(j.expr || 'determine', t), jiggle: 0.3 });
      const k = p.with ? place(stand(p.with, Object.assign(pose(p.ogest || 'clap', t, j), { expr: ex('sourire', t, 1), t })), 880, 1640, 0.82) : '';
      return { scene: 'salleMuscu', act: k + `<g transform="translate(140,560) scale(0.74)">${y}</g>` + fx(p.fx, t, 500, 1200), cam: camera(t, j.D, 1.12, 560, 1250) };
    }
    const q = pose(ex2, t, j); q.expr = ex(j.expr || 'determine', t); q.t = t;
    const me = place(stand(id, q), p.with ? 360 : 540, 1700, 0.9);
    const k = p.with ? place(stand(p.with, Object.assign(pose(p.ogest || 'clap', t + 0.5, j), { expr: ex(p.oexpr || 'sourire', t, 1), t })), 790, 1680, 0.86) : '';
    const cnt = p.count ? `<text x="${p.with ? 160 : 860}" y="900" font-family="Lilita One" font-size="150" fill="#ffd23a" stroke="${K}" stroke-width="8" text-anchor="middle">${Math.min(+p.count, 1 + Math.floor(t / (j.D / +p.count)))}</text>` : '';
    return { scene: 'salleMuscu', act: k + me + cnt + fx(p.fx || 'sweat', t, 540, 950), cam: camH(t, j, 1.06, 560, 1700, 0.9, 740) };
  };
  // ---------- course (avec un partenaire éventuel)
  KINDS.jog = (t, j) => {
    const p = P(j), id = Y(j), sp = +(p.speed || 260);
    const y = stand(id, Object.assign(jog(t, p.fast ? 2.8 : 2.2), { expr: ex(j.expr || 'determine', t), t, tilt: 3 * S(t * 4) }));
    const w = p.with ? stand(p.with, Object.assign(jog(t + 0.2, p.fast ? 2.8 : 2.2), { expr: ex(p.oexpr || 'sourire', t, 1), t })) : '';
    return { scene: 'parc', act: park(t * sp, p.duck ? 0 : null) + (w ? place(w, 760, 1640, 0.86) : '') + place(y, w ? 340 : 520, 1660, 0.9) + fx(p.fx, t, 540, 900), cam: camH(t, j, 1.08, 540, 1660, 0.9, 760) };
  };
  // ---------- au lit
  KINDS.bed = (t, j) => {
    const p = P(j), id = Y(j), mode = p.mode || 'sleep';
    const arm = mode === 'phone' ? [-25, -60 + 6 * S(t * 3)] : mode === 'wake' ? [10 + 60 * ramp(t, 0.5, 1.2), 30 + 140 * ramp(t, 0.5, 1.2)] : [100, 60];
    const y = lying(id, { expr: ex(j.expr || (mode === 'sleep' ? 'calme' : 'neutre'), t), t, arm, rp: mode === 'phone' ? ['phone', 180, 0, 0] : null, y: 1150, stink: 0 });
    const blanket = `<path d="M${f1(265 + 420 * 0.62)} 1030 Q700 990 860 1030 L870 1150 L${f1(265 + 380 * 0.62)} 1150 Z" fill="#3d6fd6" stroke="${K}" stroke-width="6"/>`;
    return { scene: p.scene || 'chambreNuit', act: `<g transform="translate(265,414) scale(0.62)">${y}</g>` + (mode === 'sleep' ? blanket : '') + fx(p.fx || (mode === 'sleep' ? 'zzz' : ''), t, 330, 950), cam: camera(t, j.D, 1.6, 470, 1040) };
  };
  // ---------- balance : le poids descend
  KINDS.weigh = (t, j) => {
    const p = P(j), id = Y(j), a = +(p.from || 110), b = +(p.to || 108), u = ramp(t, 0.6, Math.min(j.D - 0.6, 2.6));
    const v = (a + (b - a) * u).toFixed(1).replace('.', ',');
    const q = u >= 1 ? G.jump(t) : { la: [30, 40], ra: [30, 40], tilt: 10 };
    const y = stand(id, Object.assign({ bob: breath(t), jiggle: 0.6 }, q, { expr: ex(u >= 1 ? 'sourire' : 'inquiet', t), t }));
    const scale = `<g transform="translate(540,1700)"><rect x="-230" y="-40" width="460" height="70" rx="24" fill="#f4f4f4" stroke="${K}" stroke-width="7"/><rect x="-90" y="-30" width="180" height="46" rx="8" fill="#111"/><text x="0" y="6" font-family="Lilita One" font-size="40" text-anchor="middle" fill="#7dff7a">${v} KG</text></g>`;
    const big = `<text x="540" y="1420" font-family="Lilita One" font-size="${f1(130 + (u >= 1 ? 16 * Math.abs(S(t * 6)) : 0))}" text-anchor="middle" fill="${u >= 1 ? '#7dff7a' : '#fff'}" stroke="${K}" stroke-width="10">${v} KG</text>`;
    return { scene: 'salleDeBain', act: scale + place(y, 540, 1680, 0.9) + big + (u >= 1 ? fx('sparkle', t, 540, 900) : ''), cam: camH(t, j, 1.05, 540, 1680, 0.9, 720) };
  };
  // ---------- avant / après (écran partagé)
  KINDS.beforeAfter = (t, j) => {
    const p = P(j), a = 'Y' + (p.a || 1), b = Y(j); ensureY(a); ensureY(b);
    const ya = stand(a, Object.assign(G.sad(t), { expr: ex('triste', t), t, jiggle: 0.4 })), yb = stand(b, Object.assign(G.flex(t), { expr: ex('sourire', t, 1), t }));
    const r = ramp(t, 0.3, 1.0);
    return { scene: SC(j), act: `<defs><clipPath id="ca"><rect x="0" y="0" width="540" height="1920"/></clipPath><clipPath id="cb"><rect x="540" y="0" width="540" height="1920"/></clipPath></defs>
      <rect x="0" y="0" width="540" height="1920" fill="#000" opacity=".25"/><g clip-path="url(#ca)">${place(ya, 270, 1720, 0.72)}</g><g clip-path="url(#cb)">${place(yb, 270 + 540 * 1, 1720, 0.72)}</g>
      <rect x="532" y="0" width="16" height="1920" fill="#fff"/><text x="270" y="1820" font-family="Lilita One" font-size="80" text-anchor="middle" fill="#fff" stroke="${K}" stroke-width="8">JOUR ${p.a || 1}</text><text x="810" y="1820" font-family="Lilita One" font-size="80" text-anchor="middle" fill="#7dff7a" stroke="${K}" stroke-width="8" opacity="${f1(r)}">JOUR ${b.slice(1)}</text>` + (r > 0.9 ? fx('sparkle', t, 810, 1100) : ''),
      cam: camera(t, j.D, 1.0, 540, 1000) };
  };
  // ---------- transformation magique (flash, étincelles, changement de stade)
  KINDS.magic = (t, j) => {
    const p = P(j), at = B(j, +(p.beat || 1), j.D * 0.45), before = 'Y' + (p.from || 6), after = Y(j), done = t > at; ensureY(before); ensureY(after);
    const q = done ? G.jump(t) : G.look(t);
    const y = stand(done ? after : before, Object.assign({ bob: breath(t), jiggle: 0.4 }, q, { expr: ex(done ? 'sourire' : 'choque', t), t }));
    const k = clamp((t - (at - 2)) / 2, 0, 1);
    const swirl = !done ? [...Array(10)].map((_, i) => { const a = t * 6 + i * 0.63, r = 300 - 120 * k; return `<text x="${f1(540 + Math.cos(a) * r)}" y="${f1(820 + Math.sin(a) * r * 0.7)}" font-family="Lilita One" font-size="${f1(30 + 40 * k)}" fill="#ffd23a" stroke="${K}" stroke-width="2" opacity="${f1(0.2 + 0.8 * k)}">✦</text>`; }).join('') : '';
    const flash = Math.abs(t - at) < 0.25 ? `<rect width="1080" height="1920" fill="#fff" opacity="${f1(1 - Math.abs(t - at) / 0.25)}"/>` : '';
    const cnt = !done && p.count ? `<text x="880" y="760" font-family="Lilita One" font-size="160" text-anchor="middle" fill="#fff" stroke="${K}" stroke-width="10">${Math.max(1, Math.ceil((at - t) / (at / +p.count)))}</text>` : '';
    const doc = p.pro ? place(stand(p.pro, Object.assign(pose(done ? 'clap' : 'show', t, j, { prop: done ? null : 'potion' }), { expr: ex(done ? 'choque' : 'sourire', t, 1), t })), 860, 1680, 0.84) : '';
    return { scene: SC(j), act: doc + place(y, p.pro ? 380 : 540, 1700, 0.92) + swirl + cnt + (done ? fx('sparkle,confetti', t, 540, 900) : '') + flash, cam: camH(t, j, 1.15, 540, 1700, 0.92, 790, [[at, 26]]) };
  };
  // ---------- frigo rempli (sain) ou vidé
  KINDS.fridge2 = (t, j) => {
    const p = P(j), id = Y(j), healthy = p.fill === 'healthy';
    const r = KINDS.fridge(t, Object.assign({}, j, { yid: id }));
    let act = r.act;
    if (healthy) act = act.replace(/PIZZA/g, 'LÉGUMES').replace(/#e5483f/g, '#5bbf4a').replace(/CHIPS/g, 'FRUITS');
    if (p.toss) { const n = Math.floor(t / 0.7); const u = (t % 0.7) / 0.7; act += PROPS.trashbag(170, 1700, 0) + (t > 0.8 ? PROPS.can(640 - 420 * u, 1000 - 300 * S(u * Math.PI) + 600 * u, u * 400) : ''); }
    return Object.assign(r, { act });
  };
  // ---------- mariage : elle saute dans ses bras / il refuse / entrée
  KINDS.hugJump = (t, j) => {
    const p = P(j), id = Y(j), at = B(j, +(p.beat || 1), 1.5), u = ramp(t, at - 0.6, at);
    const sx = 980 - 560 * u, sy = 1700 - 200 * S(u * Math.PI);
    const sarah = stand('SARAH', Object.assign(u < 1 ? G.jump(t) : G.hug(t), { expr: ex('sourire', t, 2), t }));
    const yq = t > at + 0.3 && p.refuse ? G.no(t) : G.hug(t);
    const me = stand(id, Object.assign({ bob: breath(t), jiggle: 0.1 }, yq, { expr: ex(t > at + 0.3 ? (p.refuse ? 'determine' : 'choque') : 'choque', t), t }));
    const kz = p.kenzo ? place(stand('KENZO', Object.assign(G.sad(t), { expr: ex('choque', t, 1), t })), 900, 1600, 0.78) : '';
    const off = p.refuse && t > at + 0.6 ? 160 * ramp(t, at + 0.6, at + 1.2) : 0;
    return { scene: 'mariage', act: kz + place(me, 400, 1720, 0.9) + place(sarah, sx + off, sy, 0.84) + fx(p.fx || 'hearts', t, 540, 900), cam: camH(t, j, 1.08, 560, 1720, 0.9, 760, [[at, 18]]) };
  };
  KINDS.entrance = (t, j) => {
    const p = P(j), id = Y(j), u = ramp(t, 0, 2.2), step = S(t * 7) * (1 - u);
    const me = stand(id, Object.assign(G.walk(t * (1 - u)), { expr: ex(j.expr || 'calme', t), t, ...(u >= 1 ? G.idle(t) : {}) }));
    const s = 0.6 + 0.32 * u;
    const guests = ['NADIA', 'BILAL', 'SOFIANE'].map((g, i) => place(stand(g, Object.assign(G.clap(t + i), { expr: ex(i === 2 ? 'choque' : 'sourire', t, i + 1), t })), [120, 960, 140][i], [1600, 1600, 1900][i], 0.7)).join('');
    return { scene: 'mariage', act: place(me, 540, 1350 + 380 * u, s) + guests + fx('glow,sparkle', t, 540, 1000), cam: camera(t, j.D, 1.0, 540, 1000) };
  };
  // ---------- gamer : assis sur sa chaise, manette, écran qui clignote
  KINDS.gamer = (t, j) => {
    const p = P(j), id = Y(j), mode = p.mode || 'play', s = 0.92, feet = 1720, hip = feet - (1270 - 860) * s + 110 * s;
    const jit = 3 * S(t * 30), rage = mode === 'rage', over = mode === 'over' && t > +(p.at || 1.2);
    let q = { expr: ex(j.expr || 'determine', t), t, lift: [0.9, 0.9], ll: [14, -6], rl: [14, -6], la: [-22 + jit, -115], ra: [-22 - jit, -115], rp: ['controller', 0, -60, -10], bob: breath(t) * 0.6, jiggle: 0.5, tilt: 4 * S(t * 2) };
    if (rage) q = Object.assign(q, { la: [150 + 20 * S(t * 11), 170], ra: [150 + 20 * S(t * 11 + 1), 170], rp: ['controller', t * 400 % 360, 0, 0], bob: -Math.abs(S(t * 9)) * 30, jiggle: 1, tilt: 8 * S(t * 9) });
    if (over) q = Object.assign(q, { la: [20, 10], ra: [20, 10], rp: null, tilt: -6 });
    if (mode === 'phone') q = Object.assign(q, { la: [-22, -115], ra: [-10, 205], rp: ['phone', -20, 0, -40] });
    const me = place(stand(id, q), 430, feet + 110 * s, s);
    const chair = `<g transform="translate(430,${f1(hip)})"><rect x="-190" y="-560" width="380" height="560" rx="70" fill="#141418" stroke="${K}" stroke-width="7"/><rect x="-90" y="-530" width="180" height="480" rx="40" fill="#e5483f"/><rect x="-230" y="-20" width="460" height="70" rx="26" fill="#141418" stroke="${K}" stroke-width="7"/></g>`;
    const flick = 0.5 + 0.5 * S(t * 13) * S(t * 7.3);
    const scr = over ? `<rect x="742" y="842" width="276" height="176" fill="#200"/><text x="880" y="955" font-family="Lilita One" font-size="54" text-anchor="middle" fill="#ff3b3b">PERDU</text>`
      : `<rect x="742" y="842" width="276" height="176" fill="${['#3ec5ff', '#ff4fd8', '#ffe14f', '#5bbf4a'][Math.floor(t * 3) % 4]}" opacity=".9"/><path d="M760 990 l40 -60 l30 40 l50 -80 l60 100 Z" fill="#222" opacity=".5"/><circle cx="${f1(800 + 160 * ((t * 0.7) % 1))}" cy="900" r="16" fill="#fff"/>`;
    const desk = `<g><rect x="720" y="820" width="320" height="220" rx="12" fill="#111" stroke="${K}" stroke-width="7"/>${scr}<rect x="860" y="1040" width="40" height="80" fill="#222"/><rect x="660" y="1110" width="440" height="34" fill="#2b2b33" stroke="${K}" stroke-width="6"/>
      ${[0, 1, 2, 3, 4, 5].map(i => PROPS.can(700 + (i % 3) * 52 + (i > 2 ? 26 : 0), 1106 - (i > 2 ? 84 : 0), 0)).join('')}</g>`;
    const glow = `<ellipse cx="860" cy="930" rx="300" ry="260" fill="${['#3ec5ff', '#ff4fd8', '#ffe14f', '#5bbf4a'][Math.floor(t * 3) % 4]}" opacity="${f1(over ? 0.1 : 0.08 + 0.06 * flick)}"/>`;
    const mom = p.other ? place(stand(p.other, Object.assign(pose(p.ogest || 'point', t + 0.4, j), { expr: ex(p.oexpr || 'colere', t, 1), t })), 140, 1640, 0.8) : '';
    const fall = mode === 'over' && t > +(p.at || 1.2) && t < +(p.at || 1.2) + 0.6 ? PROPS.controller(560, 1150 + 500 * ramp(t, +(p.at || 1.2), +(p.at || 1.2) + 0.5), t * 300) : '';
    return { scene: SC(j) === 'chambreJour' ? 'chambreNuit' : SC(j), act: mom + chair + me + desk + glow + fall + fx(p.fx, t, 430, 900), cam: camH(t, j, +(p.z || 1.12), 560, feet + 110 * s, s, 800, rage || p.shake ? [[0.05, 24]] : (over ? [[+(p.at || 1.2), 20]] : [])) };
  };

}
module.exports = { install };
