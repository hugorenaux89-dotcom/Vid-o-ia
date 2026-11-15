// Lana 30 jours — bibliothèque de dessin animable (SVG 720x1280)
const K = '#151515';
const O = (w = 6) => `stroke="${K}" stroke-width="${w}" stroke-linejoin="round" stroke-linecap="round"`;
const C = {
  skin: '#f4c39c', skinD: '#e3a67c', hair: '#7a4526', hairD: '#56301a', hairL: '#b77447',
  pink: '#f6a9c9', pinkD: '#e283ad', yellow: '#ffd23f', red: '#e23b3b', green: '#5fd35a', blue: '#43c3ff',
};
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const rad = (d) => (d * Math.PI) / 180;
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const lerp = (a, b, t) => a + (b - a) * t;
const easeOut = (t) => 1 - Math.pow(1 - clamp(t), 3);
const easeInOut = (t) => { t = clamp(t); return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };
const easeBack = (t) => { t = clamp(t); const c1 = 1.9, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); };
// valeur qui passe de a à b entre t0 et t1
const tw = (t, t0, t1, a, b, ease = easeInOut) => lerp(a, b, ease((t - t0) / (t1 - t0)));
// clignement naturel : renvoie 0..1
function blinkAt(t, seed = 0) {
  const period = 3.1 + (seed % 3) * 0.7;
  const p = (t + seed * 1.3) % period;
  if (p < 0.14) return Math.sin((p / 0.14) * Math.PI);
  return 0;
}

const DEFS = `
<defs>
 <linearGradient id="wall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a1b45"/><stop offset="1" stop-color="#3c2766"/></linearGradient>
 <radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".55"/></radialGradient>
 <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0f1638"/><stop offset="1" stop-color="#26346b"/></linearGradient>
 <linearGradient id="floor" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3e2c3a"/><stop offset="1" stop-color="#271a24"/></linearGradient>
 <radialGradient id="glow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#9fd8ff" stop-opacity=".6"/><stop offset="1" stop-color="#9fd8ff" stop-opacity="0"/></radialGradient>
 <radialGradient id="glowW" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#fff6c8" stop-opacity=".8"/><stop offset="1" stop-color="#fff6c8" stop-opacity="0"/></radialGradient>
 <radialGradient id="blush" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#ff7d8e" stop-opacity=".55"/><stop offset="1" stop-color="#ff7d8e" stop-opacity="0"/></radialGradient>
 <linearGradient id="tiles" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5fb7b0"/><stop offset="1" stop-color="#3f8f8c"/></linearGradient>
 <linearGradient id="sepia" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f4dcae"/><stop offset="1" stop-color="#e2b77c"/></linearGradient>
 <linearGradient id="denim" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#4f7fc4"/><stop offset="1" stop-color="#355e9e"/></linearGradient>
 <filter id="sh" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="8" stdDeviation="8" flood-color="#000" flood-opacity=".35"/></filter>
 <filter id="silh" x="-20%" y="-20%" width="140%" height="140%"><feFlood flood-color="#1a1030"/><feComposite in2="SourceAlpha" operator="in" result="s"/><feMorphology in="SourceAlpha" operator="dilate" radius="6" result="d"/><feFlood flood-color="#ffd23f"/><feComposite in2="d" operator="in" result="edge"/><feGaussianBlur in="edge" stdDeviation="6" result="glow"/><feMerge><feMergeNode in="glow"/><feMergeNode in="s"/></feMerge></filter>
 <filter id="blur"><feGaussianBlur stdDeviation="7"/></filter>
 <clipPath id="cFace"><ellipse cx="360" cy="560" rx="148" ry="158"/></clipPath>
 <clipPath id="cTop"><path d="M222 790 Q235 735 360 728 Q485 735 498 790 L515 1010 L205 1010 Z"/></clipPath>
 <clipPath id="cEyeL"><ellipse cx="303" cy="570" rx="27" ry="31"/></clipPath>
 <clipPath id="cEyeR"><ellipse cx="418" cy="570" rx="27" ry="31"/></clipPath>
 <clipPath id="cLeft"><rect x="0" y="0" width="356" height="1280"/></clipPath>
 <clipPath id="cRight"><rect x="364" y="0" width="356" height="1280"/></clipPath>
</defs>`;

/* ---------------- DÉCORS ---------------- */
function guirlande(t) {
  return `<path d="M20 215 q170 70 340 10" fill="none" stroke="#222" stroke-width="3"/>` +
    [60, 110, 160, 210, 260, 310].map((x, i) => {
      const y = 215 + Math.sin(((x - 20) / 340) * Math.PI) * 42 + 8;
      const c = ['#ffd23f', '#ff7aa8', '#7fe0ff'][i % 3];
      const a = 0.18 + 0.22 * (0.5 + 0.5 * Math.sin(t * 3 + i * 1.7));
      return `<circle cx="${x}" cy="${y}" r="18" fill="${c}" opacity="${a.toFixed(2)}"/><circle cx="${x}" cy="${y}" r="7" fill="${c}" ${O(3)}/>`;
    }).join('');
}

function fenetre(t, rideau = 'rideau') {
  const stars = [[495, 270], [540, 330], [600, 380], [505, 420], [650, 450], [560, 470]]
    .map(([x, y], i) => `<circle cx="${x}" cy="${y}" r="${(2.2 + 1.3 * (0.5 + 0.5 * Math.sin(t * 2.3 + i * 2))).toFixed(1)}" fill="#fff"/>`).join('');
  let cur;
  if (rideau === 'jean') {
    const sw = Math.sin(t * 1.4) * 2;
    cur = `<g transform="rotate(${sw.toFixed(2)} 520 225)">
      <path d="M455 228 h135 l6 70 l-8 250 h-52 l-12 -190 l-14 190 h-52 l-8 -250z" fill="url(#denim)" ${O(7)}/>
      <path d="M455 262 h141" stroke="#2c4f86" stroke-width="5"/><rect x="510" y="228" width="16" height="34" fill="#355e9e" ${O(4)}/>
      <path d="M470 300 q20 30 45 10 M545 300 q20 30 45 10" fill="none" stroke="#9bbbe6" stroke-width="4"/>
      <path d="M470 330 v190 M576 330 v190" stroke="#9bbbe6" stroke-width="3" stroke-dasharray="8 8"/>
      <circle cx="523" cy="246" r="6" fill="#d9b14a" ${O(3)}/>
      <ellipse cx="480" cy="420" rx="14" ry="10" fill="#2c4f86" opacity=".7"/>
      ${[470, 590].map((x) => `<rect x="${x - 7}" y="215" width="14" height="30" rx="3" fill="#ffd23f" ${O(3)}/>`).join('')}
    </g>`;
  } else {
    cur = `<path d="M450 222 q-10 150 10 330 l55 0 q-25 -170 -10 -330z" fill="#8c3a6a" ${O(6)}/>
      <path d="M470 240 q-6 140 10 300" stroke="#6d2a52" stroke-width="6" fill="none"/>`;
  }
  return `<rect x="455" y="225" width="225" height="300" rx="6" fill="url(#sky)" ${O(7)}/>
    <circle cx="625" cy="290" r="40" fill="url(#glowW)"/><circle cx="625" cy="290" r="28" fill="#fff4c4"/>
    <circle cx="615" cy="282" r="6" fill="#efe1a6"/><circle cx="634" cy="300" r="4" fill="#efe1a6"/>
    ${stars}
    <line x1="567" y1="225" x2="567" y2="525" ${O(6)}/><line x1="455" y1="375" x2="680" y2="375" ${O(6)}/>
    <rect x="440" y="205" width="260" height="18" rx="4" fill="#3a2a2a" ${O(5)}/>
    ${cur}`;
}

function odeurs(t, pts = [[205, 500], [530, 640], [255, 990], [470, 470], [660, 910], [120, 1060]]) {
  return pts.map(([x, y], i) => {
    const ph = t * 1.2 + i * 0.8;
    const dy = -((ph * 22) % 30);
    const o = (0.55 + 0.3 * Math.sin(ph * 2)).toFixed(2);
    const k = 14 + 5 * Math.sin(ph * 3);
    return `<path d="M${x} ${y + dy} q${k} -22 0 -44 q${-k} -22 0 -44 q${k} -22 0 -44" fill="none" stroke="#9be07a" stroke-width="5" stroke-linecap="round" opacity="${o}"/>`;
  }).join('');
}

function chambre(t, o = {}) {
  let st = ''; for (let x = 0; x < 720; x += 60) st += `<rect x="${x}" y="0" width="30" height="1000" fill="#fff" opacity=".035"/>`;
  const flick = (0.85 + 0.15 * Math.sin(t * 9) * Math.sin(t * 2.7)).toFixed(2);
  const lit = o.lit === 'lump' ? '' : `<g filter="url(#sh)">
     <rect x="-30" y="860" width="250" height="175" rx="16" fill="#6d55a8" ${O(7)}/>
     <path d="M-30 885 q70 -45 130 -5 q60 -45 120 5 v40 h-250z" fill="#b9a5ea" ${O(7)}/>
     <path d="M20 880 q30 -20 60 0" fill="none" stroke="#8f78cf" stroke-width="5"/></g>`;
  return `
  <rect width="720" height="1280" fill="url(#wall)"/>${st}
  ${fenetre(t, o.rideau)}
  ${guirlande(t)}
  <g transform="rotate(-5 120 360)" filter="url(#sh)">
   <rect x="35" y="260" width="175" height="225" rx="6" fill="#ef5b93" ${O(6)}/>
   <circle cx="122" cy="345" r="48" fill="#ffd23f" ${O(5)}/><path d="M95 345 l20 -30 l20 30 l20 -30" fill="none" ${O(5)}/>
   <text x="122" y="455" font-family="Anton" font-size="34" fill="#fff" text-anchor="middle">K-DRAMA</text>
  </g>
  <g filter="url(#sh)"><rect x="45" y="545" width="150" height="150" rx="10" fill="#fdfdfd" ${O(6)}/>
   <path d="M45 585 v-30 a10 10 0 0 1 10 -10 h130 a10 10 0 0 1 10 10 v30z" fill="#e23b3b" ${O(5)}/>
   <text x="120" y="577" font-family="Anton" font-size="22" fill="#fff" text-anchor="middle">NOVEMBRE</text>
   ${[0, 1, 2, 3].map((r) => [0, 1, 2, 3, 4].map((c) => `<rect x="${58 + c * 26}" y="${598 + r * 22}" width="18" height="14" rx="2" fill="#d8d8d8"/>`).join('')).join('')}
   <text x="150" y="683" font-family="Anton" font-size="38" fill="#e23b3b" text-anchor="middle">30</text></g>
  <rect x="0" y="1000" width="720" height="280" fill="url(#floor)"/>
  ${[0, 1, 2, 3, 4].map((i) => `<line x1="0" y1="${1040 + i * 55}" x2="720" y2="${1040 + i * 55}" stroke="#1d131b" stroke-width="4" opacity=".6"/>`).join('')}
  ${lit}
  <g filter="url(#sh)">
   <rect x="500" y="770" width="230" height="22" fill="#5b3b2c" ${O(6)}/>
   <rect x="520" y="792" width="18" height="200" fill="#4a2f22" ${O(5)}/>
   <path d="M560 768 l15 -95 h120 l15 95z" fill="#2c2c34" ${O(6)}/>
   <path d="M578 760 l11 -75 h96 l11 75z" fill="#7fd0ff" opacity="${flick}"/>
   <path d="M600 700 h50 M600 715 h70 M600 730 h40" stroke="#fff" stroke-width="5" opacity=".6"/>
   <ellipse cx="635" cy="720" rx="95" ry="65" fill="url(#glow)" opacity="${flick}"/>
   <rect x="520" y="740" width="34" height="30" rx="5" fill="#f1f1f1" ${O(4)}/><path d="M554 748 q14 2 0 16" fill="none" ${O(4)}/>
   <path d="M524 ${736 - ((t * 10) % 6)} q6 -18 0 -30 M540 ${736 - ((t * 10 + 3) % 6)} q6 -18 0 -30" stroke="#ccc" stroke-width="3" fill="none" opacity=".8"/>
  </g>
  <path d="M612 990 l-12 -95 M612 990 l22 -70 M604 930 q-34 -8 -44 12 M622 915 q30 -5 36 20" fill="none" stroke="#86622f" stroke-width="6" stroke-linecap="round"/>
  <path d="M560 943 q-6 8 2 12 M655 935 q6 10 -3 14" fill="#a07b3a" ${O(2)}/>
  <path d="M578 990 h75 l-9 78 h-57z" fill="#c9653c" ${O(6)}/><path d="M584 1005 h63" stroke="#a54d2c" stroke-width="5"/>
  ${o.linge === false ? '' : linge(1)}
  <g filter="url(#sh)">
   ${[0, 1, 2].map((i) => `<rect x="${25 + i * 7}" y="${1170 - i * 30}" width="195" height="30" rx="3" fill="#e8c08b" ${O(5)}/>`).join('')}
   <text x="129" y="1137" font-family="Anton" font-size="20" fill="#b5462b" text-anchor="middle">PIZZA</text>
   <rect x="230" y="1150" width="30" height="50" rx="6" fill="#e23b3b" ${O(4)} transform="rotate(70 245 1175)"/>
  </g>
  ${o.nuggets === false ? '' : nuggets(330, 1235, -8)}`;
}

function linge(s = 1, x = 0, y = 0) {
  return `<g filter="url(#sh)" transform="translate(${x} ${y}) translate(600 1150) scale(${s}) translate(-600 -1150)">
   <path d="M490 1150 q30 -70 100 -55 q55 -45 120 5 q30 50 0 80 h-210 q-30 -5 -10 -30z" fill="#5aa6d6" ${O(6)}/>
   <path d="M540 1118 q34 -30 70 2" fill="none" ${O(4)}/>
   <path d="M600 1100 q40 -40 90 -10 l-10 40 q-40 -20 -70 5z" fill="#f2d24a" ${O(5)}/>
   <path d="M505 1140 q20 -30 50 -20 l-5 25z" fill="#ef5b93" ${O(4)}/>
   <path d="M640 1150 q20 -15 45 0" fill="none" stroke="#3b7fae" stroke-width="5"/>
  </g>`;
}

function nuggets(x, y, r = 0, s = 1) {
  return `<g transform="translate(${x} ${y}) rotate(${r}) scale(${s})" filter="url(#sh)">
   <path d="M-45 -20 h90 l-8 40 h-74z" fill="#e23b3b" ${O(5)}/>
   <path d="M-45 -20 l-10 -26 h110 l-10 26z" fill="#ffd23f" ${O(5)}/>
   <ellipse cx="-15" cy="-30" rx="16" ry="11" fill="#d99a45" ${O(3)}/><ellipse cx="14" cy="-32" rx="15" ry="10" fill="#e3a852" ${O(3)}/>
   <text x="0" y="12" font-family="Anton" font-size="18" fill="#fff" text-anchor="middle">NUGGETS</text>
  </g>`;
}

function salleDeBain(t) {
  let tiles = '';
  for (let y = 0; y < 1000; y += 70) for (let x = (y / 70) % 2 ? -35 : 0; x < 720; x += 70)
    tiles += `<rect x="${x + 3}" y="${y + 3}" width="64" height="64" rx="4" fill="#fff" opacity=".07"/>`;
  return `<rect width="720" height="1280" fill="url(#tiles)"/>${tiles}
   <rect x="0" y="1000" width="720" height="280" fill="#d9cfc2"/>
   ${[0, 1, 2, 3].map((i) => `<line x1="0" y1="${1060 + i * 60}" x2="720" y2="${1060 + i * 60}" stroke="#bfb3a4" stroke-width="4"/>`).join('')}
   <rect x="80" y="160" width="140" height="22" rx="8" fill="#ece9e4" ${O(5)}/>
   <rect x="100" y="110" width="30" height="50" rx="8" fill="#ff8fb7" ${O(4)}/><rect x="145" y="96" width="24" height="64" rx="8" fill="#9be07a" ${O(4)}/>
   <rect x="560" y="140" width="22" height="760" fill="#d7d7d7" ${O(5)}/>
   <path d="M582 150 q50 380 0 760 h140 v-760z" fill="#f6d1e3" ${O(6)}/>
   <path d="M610 170 q30 360 0 720 M650 170 q30 360 0 720" stroke="#e9a9c6" stroke-width="5" fill="none"/>`;
}

function postits(t) {
  const notes = [
    [70, 330, -8, '#ffe066', 'BOIRE\nDE L\'EAU'], [620, 300, 7, '#ff9ec4', 'RAPPELER\nMAMAN'],
    [80, 760, 6, '#9be7ff', 'SORTIR ?'], [630, 720, -6, '#b6f08a', 'PAYER\nLE LOYER'],
  ];
  return notes.map(([x, y, r, c, txt], i) => {
    const rr = r + Math.sin(t * 2 + i) * 1.5;
    const lines = txt.split('\n');
    return `<g transform="translate(${x} ${y}) rotate(${rr.toFixed(2)})" filter="url(#sh)">
      <rect x="-62" y="-62" width="124" height="124" fill="${c}" ${O(4)}/><rect x="-62" y="-62" width="124" height="20" fill="#000" opacity=".08"/>
      ${lines.map((l, j) => `<text x="0" y="${(j - (lines.length - 1) / 2) * 30 + 10}" font-family="Anton" font-size="24" fill="#333" text-anchor="middle">${esc(l)}</text>`).join('')}
    </g>`;
  }).join('');
}

/* ---------------- LANA ---------------- */
const SH_L = [240, 800], SH_R = [480, 800], L1 = 108, L2 = 100;
function arm(side, a1, a2, o = {}) {
  const S = side === 'L' ? SH_L : SH_R;
  const A1 = side === 'L' ? 180 - a1 : a1, A2 = side === 'L' ? 180 - a2 : a2;
  const E = [S[0] + L1 * Math.cos(rad(A1)), S[1] + L1 * Math.sin(rad(A1))];
  const H = [E[0] + L2 * Math.cos(rad(A2)), E[1] + L2 * Math.sin(rad(A2))];
  const sleeve = o.sleeve || C.pink, sleeveD = o.sleeveD || C.pinkD;
  const p = `M${S[0]} ${S[1]} L${E[0].toFixed(1)} ${E[1].toFixed(1)} L${H[0].toFixed(1)} ${H[1].toFixed(1)}`;
  let hand = `<circle cx="${H[0].toFixed(1)}" cy="${H[1].toFixed(1)}" r="29" fill="${C.skin}" ${O(6)}/>`;
  if (o.point) {
    const F = [H[0] + 50 * Math.cos(rad(A2)), H[1] + 50 * Math.sin(rad(A2))];
    hand = `<path d="M${H[0].toFixed(1)} ${H[1].toFixed(1)} L${F[0].toFixed(1)} ${F[1].toFixed(1)}" stroke="${K}" stroke-width="26" stroke-linecap="round"/>
      <path d="M${H[0].toFixed(1)} ${H[1].toFixed(1)} L${F[0].toFixed(1)} ${F[1].toFixed(1)}" stroke="${C.skin}" stroke-width="15" stroke-linecap="round"/>` + hand;
  }
  if (o.fist) hand += `<path d="M${(H[0] - 14).toFixed(1)} ${(H[1] - 6).toFixed(1)} h28 M${(H[0] - 14).toFixed(1)} ${(H[1] + 6).toFixed(1)} h28" stroke="${C.skinD}" stroke-width="4"/>`;
  return `<path d="${p}" fill="none" stroke="${K}" stroke-width="66" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="${p}" fill="none" stroke="${sleeve}" stroke-width="52" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="${p}" fill="none" stroke="${sleeveD}" stroke-width="14" stroke-linecap="round" stroke-linejoin="round" opacity=".6" transform="translate(${side === 'L' ? -12 : 12} 0)"/>
    ${hand}`;
  // eslint-disable-next-line no-unreachable
}
function handPos(side, a1, a2) {
  const S = side === 'L' ? SH_L : SH_R;
  const A1 = side === 'L' ? 180 - a1 : a1, A2 = side === 'L' ? 180 - a2 : a2;
  return [S[0] + L1 * Math.cos(rad(A1)) + L2 * Math.cos(rad(A2)), S[1] + L1 * Math.sin(rad(A1)) + L2 * Math.sin(rad(A2))];
}
const POSES = {
  bas: [78, 92], phone: [58, -98], croise: [110, 180], poing: [100, -80], tete: [-30, -150], cadeau: [100, -40], haut: [-48, -84], hausse: [22, -38], pointe: [96, -62], salut: [-30, -100], hanche: [40, 150],
};

function telephone(x, y, r, s, t, content = 'ines') {
  let screen = '';
  if (content === 'ines') {
    screen = `<rect x="-54" y="-92" width="108" height="150" rx="12" fill="#e9f6ff" stroke="#9cc" stroke-width="2"/>
     <text x="0" y="-62" font-family="Anton" font-size="20" fill="${K}" text-anchor="middle">INÈS 🎉</text>
     <text x="0" y="-30" font-family="Anton" font-size="14" fill="${K}" text-anchor="middle">LES 10 ANS DU LYCÉE</text>
     <text x="0" y="-6" font-family="Anton" font-size="14" fill="${K}" text-anchor="middle">C'EST DANS 30 JOURS</text>
     <text x="0" y="30" font-family="Anton" font-size="16" fill="${C.red}" text-anchor="middle">NATHAN VIENT ❤</text>`;
  }
  return `<g transform="translate(${x} ${y}) rotate(${r}) scale(${s})" filter="url(#sh)">
   <rect x="-75" y="-125" width="150" height="250" rx="22" fill="#1b1b1b" ${O(6)}/>
   <rect x="-62" y="-104" width="124" height="200" rx="8" fill="#fff"/>${screen}
   <circle cx="0" cy="108" r="7" fill="#444"/></g>`;
}

function eye(cx, cy, side, P) {
  const lid = clamp(Math.max(P.lid ?? 0.3, P.blink || 0));
  const [lx, ly] = P.look || [0, 0];
  const big = P.eyes === 'grand';
  const pr = big ? 8 : 11;
  const tilt = (P.lidTilt || 0) * (side === 'L' ? 1 : -1);
  if (P.eyes === 'heureux') {
    return `<path d="M${cx - 24} ${cy + 6} q24 -30 48 0" fill="none" ${O(7)}/>`;
  }
  const lidY = cy - 31 + lid * 66;
  return `<ellipse cx="${cx}" cy="${cy}" rx="27" ry="${big ? 33 : 29}" fill="#fff" ${O(5)}/>
   <g clip-path="url(#cEye${side})">
    ${big ? `<circle cx="${cx + lx}" cy="${cy + ly}" r="${pr}" fill="${K}"/>` :
      `<circle cx="${cx + lx}" cy="${cy + 6 + ly}" r="${pr}" fill="#4a2c1a"/><circle cx="${cx + lx}" cy="${cy + 6 + ly}" r="5.5" fill="${K}"/><circle cx="${cx + lx + 4}" cy="${cy + 2 + ly}" r="2.8" fill="#fff"/>`}
    ${lid > 0.02 ? `<path d="M${cx - 40} ${cy - 50} H${cx + 40} V${(lidY - tilt * 10).toFixed(1)} Q${cx} ${(lidY + 8).toFixed(1)} ${cx - 40} ${(lidY + tilt * 10).toFixed(1)} Z" fill="${P.teen ? C.skin : C.skin}" stroke="${K}" stroke-width="5"/>` : ''}
   </g>
   <ellipse cx="${cx}" cy="${cy}" rx="27" ry="${big ? 33 : 29}" fill="none" ${O(5)}/>`;
}

function bouche(P) {
  const m = P.mouth || 'plat';
  const x = 362, y = 668;
  switch (m) {
    case 'parle': { const k = clamp(P.open || 0); return k < 0.12 ? `<path d="M${x - 26} ${y} q26 -10 52 0" fill="none" ${O(5)}/>` : `<ellipse cx="${x}" cy="${y + 4}" rx="${(16 + k * 10).toFixed(1)}" ry="${(5 + k * 24).toFixed(1)}" fill="#7a1f2b" ${O(5)}/>`; }
    case 'o': return `<ellipse cx="${x}" cy="${y}" rx="13" ry="16" fill="#7a1f2b" ${O(5)}/>`;
    case 'cri': return `<path d="M${x - 26} ${y - 14} q26 -12 52 0 q6 52 -26 54 q-32 -2 -26 -54z" fill="#7a1f2b" ${O(5)}/><path d="M${x - 16} ${y + 24} q16 -12 32 0 q-4 14 -16 14 q-12 0 -16 -14z" fill="#ff8a95"/><path d="M${x - 20} ${y - 12} h40 v8 h-40z" fill="#fff"/>`;
    case 'sourire': return `<path d="M${x - 34} ${y - 6} q34 38 68 0 q-34 10 -68 0z" fill="#7a1f2b" ${O(5)}/><path d="M${x - 26} ${y - 3} q26 8 52 0 v6 q-26 8 -52 0z" fill="#fff"/>`;
    case 'dents': return `<rect x="${x - 30}" y="${y - 12}" width="60" height="24" rx="10" fill="#fff" ${O(5)}/><path d="M${x - 30} ${y} h60 M${x - 10} ${y - 12} v24 M${x + 10} ${y - 12} v24" stroke="${K}" stroke-width="3"/>`;
    case 'tordu': return `<path d="M${x - 30} ${y + 4} q15 -10 30 0 q15 10 30 -6" fill="none" ${O(5)}/>`;
    case 'soupir': return `<ellipse cx="${x + 6}" cy="${y + 2}" rx="18" ry="9" fill="#7a1f2b" ${O(5)}/>`;
    default: return `<path d="M${x - 30} ${y} q30 -16 62 2" fill="none" ${O(5)}/><path d="M${x + 30} ${y} l6 6" ${O(4)}/>`;
  }
}

function sourcils(P) {
  const lift = P.browLift || 0; // négatif = monte
  const ang = P.browAng || 0;   // + = froncés (colère/détermination), - = tristes
  if (P.teen) {
    return `<path d="M272 ${522 + lift} q32 -18 66 -4" fill="none" stroke="${C.hairD}" stroke-width="8" stroke-linecap="round" transform="rotate(${ang} 305 ${520 + lift})"/>
      <path d="M384 ${518 + lift} q34 -14 66 4" fill="none" stroke="${C.hairD}" stroke-width="8" stroke-linecap="round" transform="rotate(${-ang} 418 ${520 + lift})"/>`;
  }
  const hairs = (bx, by, dir) => [0, 1, 2, 3, 4, 5].map((i) => `<path d="M${bx + i * 12} ${by - i * 2 * dir} l${-4 * dir} -15" stroke="#3b2213" stroke-width="4" stroke-linecap="round"/>`).join('');
  return `<g transform="translate(0 ${lift}) rotate(${ang} 305 525)">
     <path d="M262 528 q38 -38 84 -12 l-6 24 q-38 -18 -74 8z" fill="#3b2213" ${O(4)}/>${hairs(270, 522, 1)}</g>
    <g transform="translate(0 ${lift}) rotate(${-ang} 418 520)">
     <path d="M376 516 q46 -26 84 12 l-4 20 q-36 -26 -74 -8z" fill="#3b2213" ${O(4)}/>${hairs(388, 510, -1)}</g>`;
}

function lana(P = {}) {
  const teen = !!P.teen;
  const t = P.t || 0;
  const breathe = 1 + 0.012 * Math.sin(t * 2.2);
  const [aL1, aL2] = P.armL || POSES.bas;
  const [aR1, aR2] = P.armR || POSES.bas;
  const top = teen ? '#f7f7f7' : C.pink, topD = teen ? '#d9d9d9' : C.pinkD;
  const pants = teen ? 'url(#denim)' : C.pink;
  const jacket = teen;

  const legs = `
  <path d="M262 1000 L250 1200 L340 1200 L352 1010 Z" fill="${pants}" ${O(7)}/>
  <path d="M368 1010 L380 1200 L470 1200 L458 1000 Z" fill="${pants}" ${O(7)}/>
  ${teen ? '' : `<path d="M268 1030 l-12 160 h25 l10 -160z M440 1030 l12 160 h18 l-10 -160z" fill="${C.pinkD}" opacity=".8"/>
  ${[[290, 1060], [320, 1130], [275, 1170], [410, 1080], [440, 1150], [400, 1180]].map(([x, y]) => `<path d="M${x} ${y} l5 -10 l5 10 l-5 -3z" fill="#fff" opacity=".9"/>`).join('')}`}
  ${teen
    ? [[295, 1215], [425, 1215]].map(([x, y]) => `<path d="M${x - 60} ${y + 20} q0 -40 40 -40 h40 q40 10 40 40z" fill="#fff" ${O(7)}/><path d="M${x - 60} ${y + 12} h120" stroke="${C.red}" stroke-width="8"/>`).join('')
    : [[295, 1215], [425, 1215]].map(([x, y]) => `<ellipse cx="${x}" cy="${y}" rx="62" ry="32" fill="#fff" ${O(7)}/><ellipse cx="${x}" cy="${y + 12}" rx="55" ry="16" fill="#e9e3f3"/><path d="M${x - 8} ${y - 28} l10 -32 l10 32z" fill="#ffd23f" ${O(4)}/><circle cx="${x - 18}" cy="${y - 6}" r="5" fill="${K}"/><circle cx="${x + 18}" cy="${y - 6}" r="5" fill="${K}"/>`).join('')}`;

  const torso = `
  <path d="M222 790 Q235 735 360 728 Q485 735 498 790 L515 1010 L205 1010 Z" fill="${top}" ${O(7)}/>
  <g clip-path="url(#cTop)"><path d="M440 730 Q500 800 520 1010 L560 1010 L560 720 Z" fill="${topD}" opacity=".75"/>
   <rect x="200" y="990" width="330" height="30" fill="${topD}" opacity=".6"/></g>
  ${teen ? `
   <path d="M330 860 l12 -26 l12 26 l28 2 l-22 18 l8 28 l-26 -16 l-26 16 l8 -28 l-22 -18z" fill="${C.yellow}" ${O(5)}/>
   <path d="M222 790 Q235 735 300 730 L320 1010 L205 1010 Z" fill="url(#denim)" ${O(7)}/>
   <path d="M498 790 Q485 735 420 730 L400 1010 L515 1010 Z" fill="url(#denim)" ${O(7)}/>
   <path d="M300 730 l-30 60 l40 10z M420 730 l30 60 l-40 10z" fill="#355e9e" ${O(5)}/>`
  : `
  <path d="M320 732 q40 28 80 0" fill="#fff" ${O(5)}/>
  <circle cx="360" cy="860" r="52" fill="#fff" ${O(5)}/>
  <path d="M343 812 l17 -48 l17 48z" fill="#ffd23f" ${O(5)}/><path d="M350 795 l20 -6 M354 780 l13 -4" stroke="#e0a800" stroke-width="3"/>
  <path d="M318 830 q-25 20 -8 50 M402 830 q22 18 8 48" fill="none" stroke="#b78be8" stroke-width="10" stroke-linecap="round"/>
  <circle cx="343" cy="855" r="6" fill="${K}"/><circle cx="378" cy="855" r="6" fill="${K}"/>
  <path d="M345 880 q15 12 30 0" fill="none" ${O(4)}/><circle cx="332" cy="872" r="8" fill="url(#blush)"/><circle cx="390" cy="872" r="8" fill="url(#blush)"/>
  <path d="M265 800 q12 -8 22 2 q8 12 -6 16 q-16 2 -16 -18z" fill="#c9783f" opacity=".85"/>
  <path d="M420 950 q16 -10 28 4 q6 16 -12 18 q-20 -2 -16 -22z" fill="#c9783f" opacity=".85"/>
  <circle cx="290" cy="945" r="9" fill="#e23b3b" opacity=".85"/><circle cx="455" cy="805" r="7" fill="#ffd23f"/>
  <text x="360" y="975" font-family="Anton" font-size="56" fill="#43c3ff" stroke="${K}" stroke-width="5" paint-order="stroke" text-anchor="middle">LANA</text>`}
  ${P.sticker ? `<g transform="translate(${P.stickerX || 300} 915) rotate(-10) scale(${P.sticker})" filter="url(#sh)">
     <rect x="-95" y="-38" width="190" height="76" rx="10" fill="#fff" ${O(5)}/><rect x="-95" y="-38" width="190" height="28" rx="10" fill="${C.red}"/>
     <text x="0" y="-17" font-family="Anton" font-size="16" fill="#fff" text-anchor="middle">BONJOUR, JE M'APPELLE</text>
     <text x="0" y="28" font-family="Anton" font-size="34" fill="${K}" text-anchor="middle">SANDRINE</text></g>` : ''}`;

  const sleeveOpt = { sleeve: jacket ? '#4f7fc4' : C.pink, sleeveD: jacket ? '#355e9e' : C.pinkD };
  const armsBehind = '';
  const armsFront = arm('L', aL1, aL2, { ...sleeveOpt, ...(P.armLopt || {}) }) + arm('R', aR1, aR2, { ...sleeveOpt, ...(P.armRopt || {}) });
  const hp = handPos('R', aR1, aR2);
  const phone = P.phone ? telephone(hp[0] + 10, hp[1] - 95, 10, 0.72, t) : '';

  // tête
  const hairColor = C.hair;
  const bun = teen ? '' : `
   <path d="M300 410 l-48 -34 M425 405 l46 -40 M360 352 l4 -44 M330 360 l-26 -40 M400 365 l30 -38" stroke="${hairColor}" stroke-width="9" stroke-linecap="round"/>
   <circle cx="362" cy="400" r="74" fill="${hairColor}" ${O(7)}/>
   <path d="M305 375 q40 -45 95 -10 M310 420 q48 26 100 -24 M335 350 q10 60 60 70 M300 400 q30 -5 50 20" fill="none" stroke="${C.hairD}" stroke-width="5"/>
   <path d="M330 345 q30 -18 60 -5" stroke="${C.hairL}" stroke-width="5" fill="none" opacity=".8"/>
   <rect x="398" y="300" width="17" height="115" rx="3" fill="#ffd23f" ${O(5)} transform="rotate(32 406 357)"/>
   <path d="M432 293 l12 -18" stroke="#e23b3b" stroke-width="9" stroke-linecap="round"/>
   <ellipse cx="362" cy="465" rx="62" ry="16" fill="#43c3ff" ${O(5)}/>`;
  const backHair = teen
    ? `<path d="M200 560 Q200 420 362 418 Q524 420 520 560 L540 820 Q500 850 470 800 L250 800 Q220 850 180 820 Z" fill="${hairColor}" ${O(7)}/>
       <path d="M215 600 q-10 120 0 200 M505 600 q10 120 0 200" stroke="${C.hairL}" stroke-width="6" fill="none" opacity=".7"/>`
    : `<path d="M212 560 Q210 440 362 432 Q514 440 508 560 L516 690 Q490 720 470 690 L250 690 Q230 720 204 690 Z" fill="${hairColor}" ${O(7)}/>`;
  const fringe = teen
    ? `<path d="M215 540 Q230 420 362 418 Q494 420 506 540 Q450 455 380 470 Q300 470 215 540 Z" fill="${hairColor}" ${O(7)}/>
       <path d="M260 465 q60 -35 130 -20" stroke="${C.hairL}" stroke-width="7" fill="none" opacity=".9"/>
       <path d="M300 450 q40 -15 70 -10" stroke="#fff" stroke-width="5" fill="none" opacity=".5"/>`
    : `<path d="M215 520 Q240 425 362 425 Q485 425 506 520 Q470 470 432 492 Q412 455 372 482 Q340 450 305 485 Q262 462 215 520 Z" fill="${hairColor}" ${O(7)}/>
       <path d="M250 470 q40 -25 90 -20 M390 452 q45 0 80 25" stroke="${C.hairL}" stroke-width="5" fill="none" opacity=".75"/>
       <path d="M226 510 q-22 70 -6 140 M496 505 q26 80 6 150" fill="none" stroke="${hairColor}" stroke-width="13" stroke-linecap="round"/>
       <path d="M226 510 q-22 70 -6 140 M496 505 q26 80 6 150" fill="none" stroke="${K}" stroke-width="3" stroke-linecap="round" opacity=".6"/>
       <path d="M440 430 q30 -30 20 -60" fill="none" stroke="${hairColor}" stroke-width="7" stroke-linecap="round"/>`;
  const glasses = teen ? '' : `
   <g transform="rotate(-7 360 570)">
    <circle cx="303" cy="570" r="44" fill="#bfe6ff" fill-opacity=".12" stroke="${K}" stroke-width="9"/>
    <circle cx="418" cy="570" r="44" fill="#bfe6ff" fill-opacity=".12" stroke="${K}" stroke-width="9"/>
    <path d="M280 545 l14 -10 M395 545 l14 -10" stroke="#fff" stroke-width="5" stroke-linecap="round" opacity=".8"/>
    <path d="M347 568 q14 -10 27 0" fill="none" stroke="${K}" stroke-width="9"/>
    <rect x="349" y="556" width="24" height="18" rx="2" fill="#fff" ${O(4)}/><path d="M353 565 h16" stroke="#ccc" stroke-width="3"/>
    <path d="M259 565 l-45 -8 M462 565 l45 -8" stroke="${K}" stroke-width="7"/>
   </g>`;
  const flaws = teen ? `
   <path d="M290 640 l6 -12 l6 12 l-6 -3z M440 470 l6 -12 l6 12" fill="#fff"/>` : `
   <path d="M280 604 q24 14 48 0 M394 604 q24 14 48 0" fill="none" stroke="#b9786b" stroke-width="5" stroke-linecap="round"/>
   <path d="M284 614 q20 8 40 0 M398 614 q20 8 40 0" fill="none" stroke="#c99187" stroke-width="3" stroke-linecap="round"/>
   <circle cx="258" cy="650" r="8" fill="#e8434a" ${O(4)}/><circle cx="256" cy="647" r="2.5" fill="#fff"/>
   <circle cx="450" cy="490" r="7" fill="#e8434a" ${O(4)}/>
   <circle cx="395" cy="690" r="5" fill="#e8434a" ${O(3)}/>`;
  const sweat = P.sweat ? (() => {
    const k = ((t * 0.8) % 1);
    return `<g transform="translate(0 ${(k * 40).toFixed(1)})" opacity="${(1 - k * 0.6).toFixed(2)}"><path d="M478 515 q-14 24 0 34 q14 -10 0 -34z" fill="#8fd7ff" ${O(4)}/><path d="M475 532 q2 6 6 6" stroke="#fff" stroke-width="3" fill="none"/></g>`;
  })() : '';

  const head = `
  <g transform="translate(0 ${(P.headY || 0).toFixed(1)}) rotate(${(P.headRot || 0).toFixed(2)} 360 720)">
   ${bun}
   ${backHair}
   <path d="M328 700 h64 v40 q-32 16 -64 0z" fill="${C.skinD}" ${O(5)}/>
   <ellipse cx="360" cy="560" rx="148" ry="158" fill="${C.skin}" ${O(7)}/>
   <g clip-path="url(#cFace)"><ellipse cx="460" cy="600" rx="90" ry="190" fill="${C.skinD}" opacity=".55"/><ellipse cx="300" cy="460" rx="70" ry="40" fill="#fff" opacity=".18"/></g>
   <ellipse cx="360" cy="560" rx="148" ry="158" fill="none" ${O(7)}/>
   <path d="M214 560 q-30 -10 -28 30 q4 35 34 30z" fill="${C.skin}" ${O(6)}/><path d="M506 560 q30 -10 28 30 q-4 35 -34 30z" fill="${C.skinD}" ${O(6)}/>
   ${teen ? `<circle cx="196" cy="605" r="8" fill="${C.yellow}" ${O(3)}/><circle cx="524" cy="605" r="8" fill="${C.yellow}" ${O(3)}/>` : ''}
   ${fringe}
   ${sourcils(P)}
   ${eye(303, 570, 'L', P)}${eye(418, 570, 'R', P)}
   ${flaws}
   ${glasses}
   <path d="M362 595 q-14 34 6 42 q10 2 14 -4" fill="none" ${O(5)}/>
   <ellipse cx="275" cy="640" rx="34" ry="20" fill="url(#blush)" opacity="${P.blush || 1}"/><ellipse cx="448" cy="640" rx="34" ry="20" fill="url(#blush)" opacity="${P.blush || 1}"/>
   ${bouche(P)}
   ${sweat}
  </g>`;

  const bodyT = `translate(360 1230) scale(1 ${breathe.toFixed(4)}) translate(-360 -1230)`;
  return `<g transform="translate(${P.x || 0} ${P.y || 0}) rotate(${P.rot || 0} 360 1230) translate(360 1230) scale(${P.s || 1}) translate(-360 -1230)">
   <g transform="${bodyT}">${armsBehind}${legs}${torso}${armsFront}${phone}</g>
   <g transform="translate(0 ${((breathe - 1) * -480).toFixed(1)})">${head}</g>
  </g>`;
}

/* ---------------- PÂTES (le chat) ---------------- */
function chat(x, y, sc, o = {}) {
  const t = o.t || 0;
  const tail = Math.sin(t * 2.2) * 14;
  const bl = clamp(Math.max(o.lid ?? 0.45, o.blink || 0));
  const lidY = -45 + bl * 26;
  const meow = o.meow || 0;
  return `<g transform="translate(${x} ${y}) scale(${sc})" filter="url(#sh)">
  <g transform="rotate(${tail.toFixed(1)} 60 80)">
   <path d="M60 80 q90 -10 70 -90" fill="none" stroke="${K}" stroke-width="22" stroke-linecap="round"/>
   <path d="M60 80 q90 -10 70 -90" fill="none" stroke="#ef8a2e" stroke-width="13" stroke-linecap="round"/></g>
  <ellipse cx="0" cy="60" rx="88" ry="72" fill="#ef8a2e" ${O(7)}/>
  <ellipse cx="0" cy="80" rx="45" ry="45" fill="#fbe3c4"/>
  <path d="M-60 40 q12 12 0 26 M60 40 q-12 12 0 26 M-30 0 q0 14 -6 22 M30 0 q0 14 6 22" stroke="#c4651c" stroke-width="6" fill="none"/>
  <g transform="rotate(${(o.headRot || 0).toFixed(1)} 0 30)">
  <circle cx="0" cy="-30" r="64" fill="#ef8a2e" ${O(7)}/>
  <path d="M-58 -58 l6 -60 l44 32z M58 -58 l-6 -60 l-44 32z" fill="#ef8a2e" ${O(7)}/>
  <path d="M-48 -70 l3 -30 l22 16z M48 -70 l-3 -30 l-22 16z" fill="#f7b8c4"/>
  <path d="M-15 -90 l5 22 M0 -94 v24 M15 -90 l-5 22" stroke="#c4651c" stroke-width="6" stroke-linecap="round"/>
  <ellipse cx="-24" cy="-32" rx="15" ry="13" fill="#d6f27a" ${O(4)}/><ellipse cx="24" cy="-32" rx="15" ry="13" fill="#d6f27a" ${O(4)}/>
  <rect x="${-27 + (o.lookX || 0)}" y="-42" width="6" height="20" rx="3" fill="${K}"/><rect x="${21 + (o.lookX || 0)}" y="-42" width="6" height="20" rx="3" fill="${K}"/>
  <path d="M-42 -48 h34 v${(lidY + 48).toFixed(1)} q-18 -4 -34 4z M42 -48 h-34 v${(lidY + 48).toFixed(1)} q18 -4 34 4z" fill="#ef8a2e" ${O(4)}/>
  <ellipse cx="0" cy="-2" rx="30" ry="20" fill="#fbe3c4"/>
  <path d="M-8 -12 l8 8 l8 -8z" fill="#e8708f" ${O(4)}/>
  ${meow > 0.05 ? `<path d="M0 -4 v4 M-14 4 q14 ${(26 * meow).toFixed(1)} 28 0z" fill="#7a1f2b" ${O(4)}/>` : `<path d="M0 -4 v6 M-14 10 q14 -10 28 0" fill="none" ${O(4)}/>`}
  <path d="M-34 -6 h-44 M-34 4 h-40 M34 -6 h44 M34 4 h40" stroke="${K}" stroke-width="3"/>
  </g>
  <ellipse cx="-36" cy="120" rx="26" ry="16" fill="#ef8a2e" ${O(6)}/><ellipse cx="36" cy="120" rx="26" ry="16" fill="#ef8a2e" ${O(6)}/>
  </g>`;
}

function valise(x, y, s) {
  return `<g transform="translate(${x} ${y}) scale(${s})" filter="url(#sh)">
   <rect x="-70" y="-50" width="140" height="100" rx="14" fill="#c0392b" ${O(6)}/>
   <path d="M-25 -50 v-18 h50 v18" fill="none" ${O(6)}/>
   <path d="M-70 -10 h140" stroke="#8e2a1f" stroke-width="5"/>
   <circle cx="-30" cy="20" r="14" fill="#ffd23f" ${O(3)}/><rect x="10" y="10" width="40" height="24" rx="4" fill="#fff" ${O(3)}/>
   <text x="30" y="28" font-family="Anton" font-size="14" fill="${K}" text-anchor="middle">BYE</text>
  </g>`;
}

/* ---------------- HABILLAGE (HUD, titres, sous-titres) ---------------- */
function hud(j = 30, g = 0, o = 1) {
  const box = (x, label, val, col) => `<g filter="url(#sh)"><rect x="${x}" y="105" width="200" height="94" rx="16" fill="#121212" stroke="#333" stroke-width="3"/>
   <text x="${x + 100}" y="138" font-family="Anton" font-size="22" fill="#fff" text-anchor="middle">${label}</text>
   <text x="${x + 100}" y="188" font-family="Anton" font-size="48" fill="${col}" text-anchor="middle">${val}</text></g>`;
  return `<g opacity="${o}">${box(70, 'JOURS RESTANTS', j, '#ffd23f')}${box(450, 'GLOW-UP', g + '%', '#5fd35a')}</g>`;
}

function pop(x, y, s, inner, r = 0) {
  if (s <= 0.001) return '';
  return `<g transform="translate(${x} ${y}) rotate(${r}) scale(${s.toFixed(3)})">${inner}</g>`;
}
const popS = (t, t0, d = 0.35) => (t < t0 ? 0 : easeBack((t - t0) / d));

function titre(y, parts, size = 118, x = 360) {
  return `<text x="${x}" y="${y}" font-family="Anton" font-size="${size}" text-anchor="middle" stroke="${K}" stroke-width="${Math.round(size / 7.5)}" paint-order="stroke" filter="url(#sh)">${parts.map(([tx, c]) => `<tspan fill="${c}">${esc(tx)}</tspan>`).join('')}</text>`;
}
function etiquette(txt, w, col = C.yellow, size = 40) {
  return `<g filter="url(#sh)"><rect x="${-w / 2}" y="-38" width="${w}" height="76" rx="18" fill="#121212" stroke="${col}" stroke-width="4"/>
   <text x="0" y="${size * 0.36}" font-family="Anton" font-size="${size}" fill="#fff" text-anchor="middle">${esc(txt)}</text></g>`;
}
function bandeau(txt, y = 1110, w = 590) {
  return `<g filter="url(#sh)"><rect x="${360 - w / 2}" y="${y}" width="${w}" height="82" rx="18" fill="#121212" stroke="#ffd23f" stroke-width="4"/>
   <text x="360" y="${y + 55}" font-family="Anton" font-size="36" fill="#fff" text-anchor="middle">${esc(txt)}</text></g>`;
}

// Sous-titres mot par mot : groupes de 1 à 3 mots, mot courant en jaune
function groupes(words) {
  const out = []; let g = [];
  words.forEach((w, i) => {
    g.push(w);
    const punct = /[.,!?…:;]$/.test(w.w);
    const long = g.map((x) => x.w).join(' ').length > 15;
    if (punct || g.length >= 3 || long || i === words.length - 1) { out.push(g); g = []; }
  });
  return out;
}
function sousTitres(t, words, y = 1010, emph = null) {
  if (!words || !words.length) return '';
  emph = emph || module.exports.EMPH;
  const gs = groupes(words);
  let cur = null;
  for (let i = 0; i < gs.length; i++) {
    const g = gs[i], next = gs[i + 1];
    const end = next ? next[0].s : g[g.length - 1].e + 0.35;
    if (t >= g[0].s - 0.05 && t < end) { cur = g; break; }
  }
  if (!cur) return '';
  const clean = (w) => w.replace(/[.,!?…:;]+$/, '').toUpperCase();
  const txt = cur.map((w) => clean(w.w));
  const size = txt.join(' ').length > 13 ? 64 : 74;
  const sIn = easeBack((t - cur[0].s + 0.05) / 0.18);
  const spans = cur.map((w, i) => {
    const on = t >= w.s - 0.03;
    const active = on && (i === cur.length - 1 || t < cur[i + 1].s - 0.03);
    const isE = emph && emph.test(w.w);
    const col = isE && on ? '#ff4d5e' : active ? C.yellow : '#fff';
    return `<tspan fill="${col}" ${isE ? `font-size="${Math.round(size * 1.18)}"` : ''} opacity="${on ? 1 : 0.35}">${esc(txt[i])}</tspan>`;
  }).join(' ');
  return `<g transform="translate(360 ${y}) scale(${clamp(sIn, 0, 1.2).toFixed(3)})">
    <text x="0" y="0" font-family="Anton" font-size="${size}" text-anchor="middle" stroke="${K}" stroke-width="14" paint-order="stroke" filter="url(#sh)">${spans}</text></g>`;
}

function etoiles(t, pts) {
  return pts.map(([x, y, s], i) => {
    const k = 0.5 + 0.5 * Math.sin(t * 4 + i * 2.1);
    const sc = (s || 1) * (0.5 + 0.7 * k);
    return `<g transform="translate(${x} ${y}) rotate(${(t * 40 + i * 30) % 360}) scale(${sc.toFixed(2)})"><path d="M0 -22 L6 -6 L22 0 L6 6 L0 22 L-6 6 L-22 0 L-6 -6Z" fill="#fff6b0" ${O(3)}/></g>`;
  }).join('');
}

function camera(inner, cx, cy, z, sx = 0, sy = 0, rot = 0) {
  return `<g transform="translate(${(360 + sx).toFixed(1)} ${(640 + sy).toFixed(1)}) rotate(${rot}) scale(${z.toFixed(4)}) translate(${-cx} ${-cy})">${inner}</g>`;
}
function shake(t, t0, dur = 0.35, amp = 16) {
  if (t < t0 || t > t0 + dur) return [0, 0];
  const k = 1 - (t - t0) / dur;
  return [Math.sin(t * 90) * amp * k, Math.cos(t * 77) * amp * k];
}

module.exports = {
  K, O, C, DEFS, esc, clamp, lerp, tw, easeOut, easeInOut, easeBack, blinkAt, rad,
  chambre, fenetre, odeurs, linge, nuggets, salleDeBain, postits, lana, POSES, handPos, telephone,
  chat, valise, hud, pop, popS, titre, titre0: (y, p, s) => titre(y, p, s, 0), etiquette, bandeau, sousTitres, etoiles, camera, shake,
};
