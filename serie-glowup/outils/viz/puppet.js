// Personnages en CORPS ENTIER, style « pantin » vectoriel (grosse tête, membres articulés). viewBox 0 0 600 1100
const { toonPerson, C } = require('./toon2');
const K = '#1d1a24';
const S = (w = 6) => `stroke="${K}" stroke-width="${w}" stroke-linejoin="round" stroke-linecap="round"`;

// tenues corps entier
const OUTFIT = {
  YANIS_J1: { top: '#a7a9ad', short: true, stains: true, belly: true, pants: '#4a5a7a', shoes: '#e8e8e8', stink: true },
  YANIS: { top: '#8d9096', pants: '#2f3a52', shoes: '#f2f2f2' },
  SARAH: { top: '#ead8bc', pants: '#7aa3d6', shoes: '#f2f2f2', slim: true },
  KENZO: { top: '#151515', pants: '#222', shoes: '#f2f2f2', wide: true, text: 'COACH' },
  SOFIANE: { top: '#151515', pants: '#151515', shoes: '#f2f2f2', stripes: true },
  NADIA: { top: '#dcc6a3', pants: '#7a63a0', shoes: '#5a4a3a', dress: true },
  LINA: { top: '#ffffff', pants: '#3a4a6a', shoes: '#f2f2f2', apron: true, slim: true },
  BILAL: { top: '#f4f4f4', pants: '#2a2a2a', shoes: '#141414' },
  MOUSSA: { top: '#1b1b1b', pants: '#222', shoes: '#141414' },
};

function limb(x1, y1, a1, l1, a2, l2, color, w = 46) {
  const r = d => d * Math.PI / 180;
  const x2 = x1 + Math.sin(r(a1)) * l1, y2 = y1 + Math.cos(r(a1)) * l1;
  const x3 = x2 + Math.sin(r(a2)) * l2, y3 = y2 + Math.cos(r(a2)) * l2;
  const path = `M${x1} ${y1} L${x2.toFixed(1)} ${y2.toFixed(1)} L${x3.toFixed(1)} ${y3.toFixed(1)}`;
  return { svg: `<path d="${path}" fill="none" stroke="${K}" stroke-width="${w + 10}" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="${path}" fill="none" stroke="${color}" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round"/>
    <circle cx="${x2.toFixed(1)}" cy="${y2.toFixed(1)}" r="${w / 2 - 6}" fill="none" stroke="${K}" stroke-width="3" opacity=".35"/>`, x: x3, y: y3 };
}

// poses : angles (degrés, 0 = vers le bas) [bras gauche haut, bas], [bras droit haut, bas]
const POSES = {
  idle: [[42, 18], [-42, -18]],
  panic: [[150, 170], [-150, -170]],
  phone: [[42, 18], [-70, -175]],
  fist: [[42, 18], [-160, -178]],
  tired: [[30, 6], [-30, -6]],
  flex: [[95, 175], [-95, -175]],
  point: [[42, 18], [-95, -95]],
};

function puppet(pid, expr = 'neutre', talk = false, pose = 'idle') {
  const c = C[pid] || C.YANIS, o = OUTFIT[pid] || OUTFIT.YANIS;
  const skin = c.skin;
  const wide = o.wide ? 40 : o.slim ? -25 : 0, fat = o.belly ? 40 : 0;
  const [L, R] = POSES[pose] || POSES.idle;
  // jambes
  const legW = o.belly ? 62 : 54;
  const legs = `
    <path d="M${225 - wide / 3} 760 L${215 - wide / 3} 1010" ${S(legW + 10)}/><path d="M${225 - wide / 3} 760 L${215 - wide / 3} 1010" stroke="${o.pants}" stroke-width="${legW}" stroke-linecap="round"/>
    <path d="M${375 + wide / 3} 760 L${385 + wide / 3} 1010" ${S(legW + 10)}/><path d="M${375 + wide / 3} 760 L${385 + wide / 3} 1010" stroke="${o.pants}" stroke-width="${legW}" stroke-linecap="round"/>
    <ellipse cx="${200 - wide / 3}" cy="1040" rx="62" ry="30" fill="${o.shoes}" ${S()}/><ellipse cx="${400 + wide / 3}" cy="1040" rx="62" ry="30" fill="${o.shoes}" ${S()}/>
    <path d="M${150 - wide / 3} 1050 L${250 - wide / 3} 1050 M${350 + wide / 3} 1050 L${450 + wide / 3} 1050" stroke="#c9c9c9" stroke-width="6"/>`;
  // bras
  const la = limb(175 - wide / 2 - fat / 3, 380, -L[0], 150, -L[1], 140, skin);
  const ra = limb(425 + wide / 2 + fat / 3, 380, -R[0], 150, -R[1], 140, skin);
  const hand = (p) => `<circle cx="${p.x.toFixed(1)}" cy="${p.y.toFixed(1)}" r="30" fill="${skin}" ${S()}/>`;
  const phone = pose === 'phone' ? `<rect x="${(ra.x - 32).toFixed(1)}" y="${(ra.y - 70).toFixed(1)}" width="64" height="110" rx="12" fill="#222" ${S(5)}/><rect x="${(ra.x - 24).toFixed(1)}" y="${(ra.y - 60).toFixed(1)}" width="48" height="84" rx="6" fill="#7fd0ff"/>` : '';
  // torse
  const tw = 270 + wide + fat, top = 330, bottom = o.short ? 590 : 790;
  const torso = o.dress
    ? `<path d="M${300 - tw / 2} ${top + 40} Q300 ${top - 10} ${300 + tw / 2} ${top + 40} L${300 + tw / 2 + 50} 860 L${300 - tw / 2 - 50} 860 Z" fill="${o.top}" ${S()}/>`
    : `<path d="M${300 - tw / 2} ${top + 50} Q300 ${top - 10} ${300 + tw / 2} ${top + 50} L${300 + tw / 2 + 6} ${bottom} Q300 ${bottom + 20} ${300 - tw / 2 - 6} ${bottom} Z" fill="${o.top}" ${S()}/>
       <path d="M${300 - tw / 2} ${top + 50} L${300 - tw / 2 - 40} ${top + 130} L${300 - tw / 2 + 10} ${top + 160} Z M${300 + tw / 2} ${top + 50} L${300 + tw / 2 + 40} ${top + 130} L${300 + tw / 2 - 10} ${top + 160} Z" fill="${o.top}" ${S()}/>`;
  const belly = o.belly ? `<ellipse cx="300" cy="680" rx="${150 + fat}" ry="125" fill="${skin}" ${S()}/>
    <path d="M292 690 q8 10 0 18" fill="none" ${S(5)}/>${[[250, 640], [270, 660], [330, 650], [350, 672], [300, 620], [240, 700], [360, 710]].map(([x, y]) => `<path d="M${x} ${y} l4 -14" ${S(3)}/>`).join('')}
    <path d="M${300 - tw / 2 - 6} ${bottom} Q300 ${bottom + 30} ${300 + tw / 2 + 6} ${bottom}" fill="none" ${S()}/>` : '';
  const pantsTop = o.belly ? `<path d="M170 760 Q300 800 430 760 L430 790 Q300 830 170 790 Z" fill="${o.pants}" ${S()}/>` : '';
  const stains = o.stains ? `<ellipse cx="250" cy="470" rx="34" ry="22" fill="#c9883a" opacity=".75"/><ellipse cx="360" cy="520" rx="26" ry="18" fill="#9a5a3a" opacity=".7"/><circle cx="330" cy="430" r="14" fill="#c9883a" opacity=".7"/>
    <ellipse cx="${300 - tw / 2 + 30}" cy="${top + 120}" rx="28" ry="36" fill="#7d7f84" opacity=".8"/><ellipse cx="${300 + tw / 2 - 30}" cy="${top + 120}" rx="28" ry="36" fill="#7d7f84" opacity=".8"/>` : '';
  const stink = o.stink ? [[90, 470], [500, 450], [70, 640], [520, 640]].map(([x, y]) => `<path d="M${x} ${y} q-18 -26 0 -52 q18 -26 0 -52 q-18 -26 0 -52" fill="none" stroke="#7bc96f" stroke-width="7" stroke-linecap="round" opacity=".85"/>`).join('') : '';
  const extra = (o.text ? `<text x="300" y="${top + 150}" font-family="Anton" font-size="56" text-anchor="middle" fill="#fff">${o.text}</text>` : '')
    + (o.stripes ? `<path d="M${300 - tw / 2 - 30} ${top + 110} L${300 - tw / 2 + 20} ${top + 60} M${300 + tw / 2 + 30} ${top + 110} L${300 + tw / 2 - 20} ${top + 60}" stroke="#fff" stroke-width="10"/>` : '')
    + (o.apron ? `<path d="M210 ${top + 120} L390 ${top + 120} L400 ${bottom} L200 ${bottom} Z" fill="#dcc29a" ${S(5)}/>` : '');
  const neck = `<path d="M262 300 L262 350 Q300 368 338 350 L338 300 Z" fill="${skin}" ${S()}/>`;
  // tête : on réutilise le visage BD (clip sur la tête), réduite et posée sur le corps
  const head = `<defs><clipPath id="hc${pid}${expr}${talk ? 1 : 0}"><ellipse cx="300" cy="280" rx="215" ry="262"/></clipPath></defs>
    <g transform="translate(115,-40) scale(0.62)"><g clip-path="url(#hc${pid}${expr}${talk ? 1 : 0})">${toonPerson(pid, expr, talk)}</g></g>`;
  return `<g>${legs}${pantsTop}${torso}${belly}${stains}${extra}${la.svg}${ra.svg}${neck}${hand(la)}${hand(ra)}${phone}${stink}${head}</g>`;
}

// Fond à rayons (style « sunburst ») + particules
function sunburst(c1 = '#ff4fa3', c2 = '#ff77bb') {
  const rays = Array.from({ length: 24 }, (_, i) => {
    const a = (i * 15) * Math.PI / 180, b = (i * 15 + 7.5) * Math.PI / 180, R = 2400;
    return `<path d="M540 1000 L${(540 + Math.cos(a) * R).toFixed(0)} ${(1000 + Math.sin(a) * R).toFixed(0)} L${(540 + Math.cos(b) * R).toFixed(0)} ${(1000 + Math.sin(b) * R).toFixed(0)} Z" fill="${c2}"/>`;
  }).join('');
  const dots = Array.from({ length: 26 }, (_, i) => `<circle cx="${(i * 197) % 1080}" cy="${(i * 331) % 1920}" r="${4 + (i % 4) * 2}" fill="${['#fff', '#ffd54a', '#ff9ec7'][i % 3]}" opacity=".8"/>`).join('');
  return `<rect width="1080" height="1920" fill="${c1}"/>${rays}${dots}<radialGradient id="vg" cx=".5" cy=".5" r=".75"><stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".35"/></radialGradient><rect width="1080" height="1920" fill="url(#vg)"/>`;
}
const SCENE_COLORS = {
  chambre: ['#7a4fd6', '#9067e8'], chambreNuit: ['#3b2a7a', '#4a3a95'], salleMuscu: ['#e04a3a', '#f0644f'], cuisine: ['#f08a2a', '#f7a24a'],
  parc: ['#3aa65a', '#52c172'], boulangerie: ['#e3a43a', '#efbb5a'], barbier: ['#2a8fd6', '#47a8ee'], salleDeBain: ['#2fb5c9', '#4fcbdc'],
  magasin: ['#ff4fa3', '#ff77bb'], mariage: ['#d4a72c', '#e8c24a'], garage: ['#5a6b80', '#71839a'], rose: ['#ff4fa3', '#ff77bb'],
};
module.exports = { puppet, sunburst, SCENE_COLORS, OUTFIT };
