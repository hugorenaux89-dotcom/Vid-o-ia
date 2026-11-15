// Personnage articulé (bras, jambes, tête, ventre) pour l'animation image par image. Repère 600 x 1300, pieds vers y=1265.
const { toonPerson, C } = require('./toon2');
const K = '#1f1a17';
const f1 = v => (+v).toFixed(1);
function shade(hex, f) {
  const n = parseInt(hex.slice(1), 16);
  const ch = s => Math.max(0, Math.min(255, Math.round(((n >> s) & 255) * (1 + f))));
  return '#' + [16, 8, 0].map(s => ch(s).toString(16).padStart(2, '0')).join('');
}
const OUTFIT = {
  YANIS_A: { top: '#9ea2a8', short: true, stains: true, belly: true, pants: '#4b5878', shoes: '#ececec', stink: true },
  YANIS: { top: '#8d9096', pants: '#2f3a52', shoes: '#f2f2f2' },
  NADIA: { top: '#dcc6a3', pants: '#7a63a0', shoes: '#5a4a3a', dress: true },
  SOFIANE: { top: '#1b1b1b', pants: '#1b1b1b', shoes: '#f2f2f2', stripes: true },
  SARAH: { top: '#ead8bc', pants: '#7aa3d6', shoes: '#f2f2f2', slim: true },
  KENZO: { top: '#151515', pants: '#222', shoes: '#f2f2f2', wide: true, text: 'COACH', muscle: true },
};
const rad = d => d * Math.PI / 180;
const P = (o, a, L) => [o[0] + Math.sin(rad(a)) * L, o[1] + Math.cos(rad(a)) * L];
const path = pts => 'M' + pts.map(p => p.map(f1).join(' ')).join(' L');

function tube(pts, w, color) {
  const d = path(pts);
  return `<path d="${d}" fill="none" stroke="${K}" stroke-width="${w + 9}" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="${d}" fill="none" stroke="${color}" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="${d}" fill="none" stroke="${shade(color, -0.22)}" stroke-width="${f1(w * 0.4)}" stroke-linecap="round" stroke-linejoin="round" transform="translate(${f1(w * 0.22)},2)" opacity=".7"/>
    <path d="${d}" fill="none" stroke="${shade(color, 0.28)}" stroke-width="${f1(w * 0.16)}" stroke-linecap="round" stroke-linejoin="round" transform="translate(${f1(-w * 0.24)},0)" opacity=".7"/>`;
}
function hand(p, ang, skin, kind = 'open') {
  const [x, y] = p.map(f1);
  if (kind === 'fist') return `<g transform="rotate(${f1(-ang)} ${x} ${y})"><circle cx="${x}" cy="${+y + 10}" r="27" fill="${skin}" stroke="${K}" stroke-width="4.5"/>
    <path d="M${x - 18} ${+y + 4} q9 -8 18 0 q9 -8 18 0" fill="none" stroke="${K}" stroke-width="3.5"/></g>`;
  if (kind === 'thumb') return `<g><circle cx="${x}" cy="${+y + 10}" r="26" fill="${skin}" stroke="${K}" stroke-width="4.5"/>
    <rect x="${+x - 9}" y="${+y - 34}" width="18" height="40" rx="9" fill="${skin}" stroke="${K}" stroke-width="4"/></g>`;
  if (kind === 'point') return `<g transform="rotate(${f1(-ang)} ${x} ${y})"><circle cx="${x}" cy="${+y + 8}" r="25" fill="${skin}" stroke="${K}" stroke-width="4.5"/>
    <rect x="${+x - 7}" y="${+y + 14}" width="15" height="48" rx="7.5" fill="${skin}" stroke="${K}" stroke-width="4"/></g>`;
  const fingers = [-14, -5, 4, 13].map((dx, i) => `<rect x="${f1(+x + dx - 5)}" y="${f1(+y + 14)}" width="11" height="${22 + (i === 1 || i === 2 ? 4 : 0)}" rx="5.5" fill="${skin}" stroke="${K}" stroke-width="3.5"/>`).join('');
  return `<g transform="rotate(${f1(-ang)} ${x} ${y})">${fingers}<ellipse cx="${x}" cy="${f1(+y + 8)}" rx="24" ry="22" fill="${skin}" stroke="${K}" stroke-width="4"/>
    <ellipse cx="${f1(x - 22)}" cy="${f1(+y + 4)}" rx="8" ry="14" fill="${skin}" stroke="${K}" stroke-width="3.5" transform="rotate(25 ${f1(x - 22)} ${f1(+y + 4)})"/></g>`;
}
// accessoires tenus en main
const PROPS = {
  shoebox: (x, y, r = 0) => `<g transform="translate(${f1(x)},${f1(y)}) rotate(${f1(r)})"><path d="M-150 -40 L150 -40 L140 60 L-140 60 Z" fill="#ff7a1a" stroke="${K}" stroke-width="6"/><path d="M-150 -40 L-120 -110 L170 -110 L150 -40 Z" fill="#ff9a4a" stroke="${K}" stroke-width="6"/>
    <path d="M-120 -40 Q-118 -90 -70 -94 L-10 -104 Q10 -80 40 -76 Q80 -66 80 -40 Z" fill="#fff" stroke="${K}" stroke-width="5"/><path d="M-60 -70 L20 -84" stroke="#3ec5ff" stroke-width="10"/>
    <path d="M10 -40 Q12 -86 56 -90 L110 -100 Q126 -76 150 -72 Q170 -62 168 -40 Z" fill="#fff" stroke="${K}" stroke-width="5"/><path d="M60 -66 L130 -80" stroke="#3ec5ff" stroke-width="10"/>
    <text x="0" y="30" font-family="Lilita One" font-size="40" text-anchor="middle" fill="#fff">RUNNING</text></g>`,
  watch: (x, y, r = 0) => `<g transform="translate(${f1(x)},${f1(y)}) rotate(${f1(r)})"><rect x="-70" y="-60" width="140" height="100" rx="20" fill="#111" stroke="${K}" stroke-width="6"/><rect x="-58" y="-48" width="116" height="76" rx="10" fill="#9ff59a"/>
    <text x="0" y="5" font-family="Lilita One" font-size="44" text-anchor="middle" fill="#0b3d10">18:00</text><text x="0" y="24" font-family="Lilita One" font-size="18" text-anchor="middle" fill="#0b3d10">3,0 KM</text></g>`,
  croissant: (x, y, r = 0) => `<g transform="translate(${f1(x)},${f1(y)}) rotate(${f1(r)})"><path d="M-70 10 Q-60 -50 0 -54 Q60 -50 70 10 Q40 -6 30 20 Q0 -10 -30 20 Q-40 -6 -70 10 Z" fill="#e8a33a" stroke="${K}" stroke-width="5"/><path d="M-30 -40 L-20 10 M0 -50 L0 0 M30 -40 L20 10" stroke="#b8721a" stroke-width="5"/></g>`,
  kebab: (x, y, r = 0) => `<g transform="translate(${f1(x)},${f1(y)}) rotate(${f1(r)})"><path d="M-40 -150 L40 -150 L28 10 L-28 10 Z" fill="#f4e3c1" stroke="${K}" stroke-width="5"/><path d="M-36 -150 Q0 -190 36 -150 Z" fill="#c9824a" stroke="${K}" stroke-width="5"/>
    <path d="M-30 -150 q10 -16 20 0 q10 -16 20 0 q10 -16 20 0" fill="#5bbf4a" stroke="${K}" stroke-width="3"/><circle cx="-12" cy="-160" r="8" fill="#e5483f"/><path d="M-34 -60 L34 -60" stroke="#c8b48a" stroke-width="4"/></g>`,
  napkin: (x, y, r = 0) => `<g transform="translate(${f1(x)},${f1(y)}) rotate(${f1(r)})"><path d="M-150 -250 L150 -260 L160 20 L-145 30 Z" fill="#fbf7ec" stroke="${K}" stroke-width="6"/>
    <text x="0" y="-195" font-family="Lilita One" font-size="38" text-anchor="middle" fill="#2a54c8">PROGRAMME</text>
    <text x="-120" y="-140" font-family="Lilita One" font-size="30" fill="#141414">LUNDI : MUSCU</text><text x="-120" y="-100" font-family="Lilita One" font-size="30" fill="#141414">MARDI : REPOS</text><text x="-120" y="-60" font-family="Lilita One" font-size="30" fill="#141414">MERCREDI : COURSE</text>
    <ellipse cx="70" cy="-20" rx="60" ry="34" fill="#e8892f" opacity=".75"/><ellipse cx="40" cy="-10" rx="24" ry="14" fill="#c9601a" opacity=".6"/></g>`,
  basket: (x, y, r = 0) => `<g transform="translate(${f1(x)},${f1(y)}) rotate(${f1(r)})"><path d="M-130 -110 L130 -110 L110 40 L-110 40 Z" fill="#d9b06a" stroke="${K}" stroke-width="6"/>
    <path d="M-120 -70 L120 -70 M-115 -30 L115 -30 M-112 10 L112 10" stroke="#b08840" stroke-width="5"/><path d="M-110 -110 q40 -60 90 -20 q40 -50 90 -10 q30 -20 50 30 Z" fill="#7fb3ff" stroke="${K}" stroke-width="5"/><path d="M-40 -130 q30 -30 70 0" fill="#ff9ec2" stroke="${K}" stroke-width="4"/></g>`,
  deo: (x, y, r = 0) => `<g transform="translate(${f1(x)},${f1(y)}) rotate(${f1(r)})"><rect x="-24" y="-130" width="48" height="140" rx="12" fill="#2f6fd6" stroke="${K}" stroke-width="5"/><rect x="-18" y="-152" width="36" height="26" rx="6" fill="#ddd" stroke="${K}" stroke-width="4"/><rect x="-24" y="-80" width="48" height="30" fill="#fff"/><text x="0" y="-58" font-family="Lilita One" font-size="20" text-anchor="middle" fill="#2f6fd6">DÉO</text></g>`,
  sneaker: (x, y, r = 0) => `<g transform="translate(${f1(x)},${f1(y)}) rotate(${f1(r)})"><path d="M-90 20 Q-92 -40 -40 -46 L20 -60 Q40 -30 70 -24 Q100 -14 100 20 Z" fill="#d8d0c0" stroke="${K}" stroke-width="5"/><rect x="-96" y="12" width="200" height="18" rx="8" fill="#8a8070" stroke="${K}" stroke-width="4"/>
    <ellipse cx="-30" cy="-6" rx="18" ry="12" fill="#2a2a2a"/><ellipse cx="50" cy="0" rx="12" ry="9" fill="#2a2a2a"/><path d="M-10 -40 l10 14 l10 -14" fill="none" stroke="${K}" stroke-width="4"/><path d="M60 -40 q8 -20 0 -34 M80 -30 q8 -20 0 -34" fill="none" stroke="#7bc96f" stroke-width="5"/></g>`,
  sponge: (x, y, r = 0) => `<g transform="translate(${f1(x)},${f1(y)}) rotate(${f1(r)})"><rect x="-44" y="-30" width="88" height="56" rx="14" fill="#ffd23a" stroke="${K}" stroke-width="5"/><rect x="-44" y="-30" width="88" height="20" rx="8" fill="#5bbf4a" stroke="${K}" stroke-width="4"/><circle cx="-14" cy="10" r="5" fill="#d9a520"/><circle cx="14" cy="4" r="4" fill="#d9a520"/></g>`,
  chips: (x, y, r = 0) => `<g transform="translate(${f1(x)},${f1(y)}) rotate(${f1(r)})"><path d="M-55 -95 L55 -100 L62 30 L-60 34 Z" fill="#f2c230" stroke="${K}" stroke-width="6"/>
    <path d="M-55 -95 l12 -10 l12 10 l12 -10 l12 10 l12 -10 l12 10 l12 -10 l12 10 l11 -10" fill="none" stroke="${K}" stroke-width="5"/>
    <text x="2" y="-20" font-family="Lilita One" font-size="40" text-anchor="middle" fill="#d9342b" stroke="${K}" stroke-width="1.5">CHIPS</text><ellipse cx="0" cy="12" rx="26" ry="12" fill="#ffe08a" stroke="${K}" stroke-width="3"/></g>`,
  chip: (x, y) => `<ellipse cx="${f1(x)}" cy="${f1(y)}" rx="20" ry="13" fill="#ffd25a" stroke="${K}" stroke-width="4" transform="rotate(-20 ${f1(x)} ${f1(y)})"/>`,
  phone: (x, y, r = 0) => `<g transform="translate(${f1(x)},${f1(y)}) rotate(${f1(r)})"><rect x="-34" y="-110" width="68" height="124" rx="13" fill="#1c1c1c" stroke="${K}" stroke-width="5"/><rect x="-27" y="-100" width="54" height="98" rx="6" fill="#ff7aa8"/><circle cx="-8" cy="-60" r="11" fill="#fff" opacity=".9"/><circle cx="10" cy="-60" r="11" fill="#ffe08a" opacity=".9"/></g>`,
  invite: (x, y, r = 0) => `<g transform="translate(${f1(x)},${f1(y)}) rotate(${f1(r)})"><rect x="-95" y="-150" width="190" height="140" rx="10" fill="#f6e7b8" stroke="#b8902f" stroke-width="7"/>
    <text x="0" y="-102" font-family="Lilita One" font-size="34" text-anchor="middle" fill="#8a6a1f">MARIAGE</text><text x="0" y="-64" font-family="Lilita One" font-size="24" text-anchor="middle" fill="#141414">BILAL &amp; YASMINE</text>
    <path d="M-20 -38 q20 -14 40 0" fill="none" stroke="#c9a23a" stroke-width="4"/><circle cx="-8" cy="-32" r="9" fill="none" stroke="#c9a23a" stroke-width="4"/><circle cx="8" cy="-32" r="9" fill="none" stroke="#c9a23a" stroke-width="4"/></g>`,
  bottle: (x, y, r = 0) => `<g transform="translate(${f1(x)},${f1(y)}) rotate(${f1(r)})"><rect x="-58" y="-270" width="116" height="300" rx="40" fill="#9fd4ff" fill-opacity=".9" stroke="${K}" stroke-width="7"/><rect x="-28" y="-310" width="56" height="44" rx="8" fill="#3d8bff" stroke="${K}" stroke-width="6"/>
    <rect x="-40" y="-230" width="18" height="200" rx="9" fill="#fff" opacity=".45"/><text x="4" y="-100" font-family="Lilita One" font-size="64" text-anchor="middle" fill="#141414">2 L</text></g>`,
  marker: (x, y, r = 0) => `<g transform="translate(${f1(x)},${f1(y)}) rotate(${f1(r)})"><rect x="-9" y="-70" width="18" height="70" rx="5" fill="#222" stroke="${K}" stroke-width="3"/><rect x="-6" y="-84" width="12" height="16" fill="#e33"/></g>`,
  dumbbell: (x, y, r = 0) => `<g transform="translate(${f1(x)},${f1(y)}) rotate(${f1(r)})"><rect x="-60" y="-8" width="120" height="16" fill="#bbb" stroke="${K}" stroke-width="4"/><rect x="-80" y="-30" width="30" height="60" rx="6" fill="#222" stroke="${K}" stroke-width="4"/><rect x="50" y="-30" width="30" height="60" rx="6" fill="#222" stroke="${K}" stroke-width="4"/></g>`,
};

function head(pid, expr, cx, top, scale, tilt, id) {
  const hx = cx - 300 * scale;
  return `<defs><clipPath id="hc${id}"><ellipse cx="300" cy="300" rx="285" ry="290"/></clipPath>
      <linearGradient id="fs${id}" x1="0" x2="1"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#3a1d0a" stop-opacity=".22"/></linearGradient></defs>
    <g transform="rotate(${f1(tilt)} ${f1(cx)} ${f1(top + 470 * scale)}) translate(${f1(hx)},${f1(top)}) scale(${scale})"><g clip-path="url(#hc${id})">${toonPerson(pid, expr, false)}
      <ellipse cx="300" cy="300" rx="285" ry="290" fill="url(#fs${id})"/></g></g>`;
}
function stinkLines(pts, t, op = 0.85) {
  return pts.map(([x, y], i) => { const w = 14 * Math.sin(t * 5 + i); return `<path d="M${x} ${y} q${f1(-16 + w)} -24 0 -48 q${f1(16 + w)} -24 0 -48 q${f1(-16 + w)} -24 0 -48" fill="none" stroke="#7bc96f" stroke-width="8" stroke-linecap="round" opacity="${op}"/>`; }).join('');
}

let gid = 0;
/* pose : { expr, la:[épaule,coude], ra:[...], ll:[hanche,genou], rl:[...], bob, tilt, lh, rh (forme de main), lp, rp ([prop, rot]), jiggle, t, stink } ; angles en degrés, 0 = vers le bas, positif = vers l'extérieur */
function stand(pid, q) {
  const c = C[pid] || C.YANIS, o = OUTFIT[pid] || OUTFIT.YANIS, skin = c.skin, id = ++gid, t = q.t || 0;
  const fat = o.belly ? 50 : 0, wide = o.wide ? 34 : o.slim ? -26 : 0;
  const sx = 300, bob = q.bob || 0;
  const tw = 150 + wide + fat * 0.6;
  const hipY = 860 + bob * 0.4, lx = sx - 62 - fat * 0.3 - wide * 0.2, rx = sx + 62 + fat * 0.3 + wide * 0.2;
  const legW = 92 + fat * 0.5;
  const leg = (x, side, [h, k] = [0, 0], lift = 0) => {
    const a = side * h, kn = P([x, hipY], a, 190 * (1 - 0.6 * lift)), an = P(kn, side * k, 170 * (1 - 0.15 * lift));
    return { svg: tube([[x, hipY], kn, an], legW, o.pants), an, ang: side * k };
  };
  const L = leg(lx, -1, q.ll, (q.lift || [0, 0])[0]), R = leg(rx, 1, q.rl, (q.lift || [0, 0])[1]);
  const shoe = (p, side) => { const [x, y] = p; return `<g transform="translate(${f1(x + side * 12)},${f1(y + 32)})"><path d="M-62 26 Q-64 -24 -22 -28 L30 -26 Q78 -16 80 26 Z" fill="${o.shoes}" stroke="${K}" stroke-width="5" transform="scale(${side},1)"/>
    <rect x="-66" y="18" width="150" height="16" rx="8" fill="${shade(o.shoes, -0.25)}" stroke="${K}" stroke-width="4" transform="scale(${side},1)"/></g>`; };
  const legs = L.svg + R.svg + shoe(L.an, -1) + shoe(R.an, 1);
  // haut du corps (décalé par la respiration)
  const top = 440 + bob, bot = (o.short ? 700 : 880) + bob * 0.7;
  const torsoPath = `M${sx - tw} ${top + 40} Q${sx - tw + 10} ${top} ${sx - 60} ${top - 6} Q${sx} ${top + 22} ${sx + 60} ${top - 6} Q${sx + tw - 10} ${top} ${sx + tw} ${top + 40} L${sx + tw - 8 + fat * 0.4} ${bot} Q${sx} ${bot + 24} ${sx - tw + 8 - fat * 0.4} ${bot} Z`;
  const torso = o.dress ? `<path d="M${sx - tw} ${top + 40} Q${sx} ${top - 20} ${sx + tw} ${top + 40} L${sx + tw + 60} 1010 L${sx - tw - 60} 1010 Z" fill="${o.top}" stroke="${K}" stroke-width="6"/>`
    : `<defs><linearGradient id="tg${id}" x1="0" x2="1"><stop offset="0" stop-color="${shade(o.top, 0.12)}"/><stop offset=".55" stop-color="${o.top}"/><stop offset="1" stop-color="${shade(o.top, -0.25)}"/></linearGradient></defs>
       <path d="${torsoPath}" fill="url(#tg${id})" stroke="${K}" stroke-width="6" stroke-linejoin="round"/>
       <path d="M${sx - 40} ${top + 120} q30 40 10 90 M${sx + 50} ${top + 150} q-20 50 4 100" fill="none" stroke="${shade(o.top, -0.28)}" stroke-width="4" opacity=".7"/>`;
  const jig = (q.jiggle || 0) * Math.sin(t * 22);
  const bw = fat * 0.9 + jig * 6, bb = bot + jig * 3;
  const belly = o.belly ? `<defs><radialGradient id="bg${id}" cx=".36" cy=".3" r=".8"><stop offset="0" stop-color="${shade(o.top, 0.14)}"/><stop offset=".6" stop-color="${o.top}"/><stop offset="1" stop-color="${shade(o.top, -0.3)}"/></radialGradient></defs>
    <path d="M${sx - tw + 4} ${bb - 120} Q${f1(sx - tw - bw)} ${bb + 70} ${sx - tw + 30} ${bb + 175} Q${sx} ${bb + 215} ${sx + tw - 30} ${bb + 175} Q${f1(sx + tw + bw)} ${bb + 70} ${sx + tw - 4} ${bb - 120} Z" fill="url(#bg${id})"/>
    <path d="M${sx - tw + 4} ${bb - 120} Q${f1(sx - tw - bw)} ${bb + 70} ${sx - tw + 30} ${bb + 175} Q${sx} ${bb + 215} ${sx + tw - 30} ${bb + 175} Q${f1(sx + tw + bw)} ${bb + 70} ${sx + tw - 4} ${bb - 120}" fill="none" stroke="${K}" stroke-width="6" stroke-linejoin="round"/>
    <path d="M${sx - tw + 40} ${bb + 160} Q${sx} ${bb + 196} ${sx + tw - 40} ${bb + 160}" fill="none" stroke="${shade(o.top, -0.35)}" stroke-width="5"/>
    <path d="M${sx - 70} ${bb + 20} q40 30 90 18 M${sx - 90} ${bb + 80} q60 30 140 10 M${sx + 40} ${bb - 40} q30 20 60 10" fill="none" stroke="${shade(o.top, -0.3)}" stroke-width="4" stroke-linecap="round" opacity=".8"/>
    <ellipse cx="${sx + 60}" cy="${bb + 60}" rx="34" ry="22" fill="#b9813f" opacity=".7"/><ellipse cx="${sx - 50}" cy="${bb + 120}" rx="22" ry="15" fill="#8f5a3a" opacity=".6"/>
    <ellipse cx="${sx - 40}" cy="${bb - 10}" rx="${f1(tw * 0.4)}" ry="60" fill="#fff" opacity=".1"/>` : '';
  const waist = `<path d="M${sx - tw + 6} ${hipY - 40} Q${sx} ${hipY - 10} ${sx + tw - 6} ${hipY - 40} L${sx + tw - 2} ${hipY + 10} Q${sx} ${hipY + 40} ${sx - tw + 2} ${hipY + 10} Z" fill="${o.pants}" stroke="${K}" stroke-width="6"/>`;
  const sweatMarks = o.stains ? `<ellipse cx="${sx - 50}" cy="${top + 110}" rx="36" ry="24" fill="#b9813f" opacity=".7"/><ellipse cx="${sx + 70}" cy="${top + 170}" rx="26" ry="18" fill="#8f5a3a" opacity=".65"/>
    <ellipse cx="${sx - tw + 38}" cy="${top + 120}" rx="30" ry="40" fill="${shade(o.top, -0.3)}" opacity=".75"/><ellipse cx="${sx + tw - 38}" cy="${top + 120}" rx="30" ry="40" fill="${shade(o.top, -0.3)}" opacity=".75"/>` : '';
  const extra = (o.text ? `<text x="${sx}" y="${top + 170}" font-family="Lilita One" font-size="60" text-anchor="middle" fill="#fff">${o.text}</text>` : '')
    + (o.muscle ? `<path d="M${sx - 70} ${top + 250} q70 30 140 0 M${sx - 60} ${top + 320} q60 24 120 0 M${sx} ${top + 220} l0 160" fill="none" stroke="#333" stroke-width="5"/>` : '')
    + (o.stripes ? `<path d="M${sx - tw - 26} ${top + 130} L${sx - tw + 30} ${top + 50} M${sx + tw + 26} ${top + 130} L${sx + tw - 30} ${top + 50}" stroke="#fff" stroke-width="10"/>` : '');
  const neck = `<path d="M${sx - 40} ${300 + bob} L${sx - 40} ${top + 10} Q${sx} ${top + 34} ${sx + 40} ${top + 10} L${sx + 40} ${300 + bob} Z" fill="${shade(skin, -0.12)}" stroke="${K}" stroke-width="6"/>`;
  // bras
  const armW = 48 + (o.muscle ? 14 : 0) + fat * 0.12;
  const arm = (side, [a1, a2] = [16, 6], hk, pr) => {
    const s0 = [sx + side * (tw - 18), top + 52], e = P(s0, side * a1, 175), h = P(e, side * a2, 160);
    const sl = o.dress ? '' : (() => { const s = P(s0, side * a1, o.short ? 58 : 165); return `<path d="${path([s0, s])}" fill="none" stroke="${K}" stroke-width="${armW + 30}" stroke-linecap="round"/><path d="${path([s0, s])}" fill="none" stroke="${o.top}" stroke-width="${armW + 21}" stroke-linecap="round"/>`; })();
    const bic = o.muscle ? (() => { const m = P(s0, side * a1, 100), ang = -Math.atan2(e[0] - s0[0], e[1] - s0[1]) * 180 / Math.PI; return `<ellipse cx="${f1(m[0])}" cy="${f1(m[1])}" rx="${f1(30 + (q.flex || 0) * 10)}" ry="58" fill="${skin}" stroke="${K}" stroke-width="4" transform="rotate(${f1(ang)} ${f1(m[0])} ${f1(m[1])}) translate(${-side * 14},0)"/>`; })() : '';
    const prop = pr ? PROPS[pr[0]](h[0] + (pr[2] || 0), h[1] + 20 + (pr[3] || 0), pr[1] || 0) : '';
    const front = pr && pr[4] === 'behind';
    return { svg: tube([s0, e, h], armW, skin) + sl + bic, hand: hand(h, side * a2, skin, hk), prop, front, h };
  };
  const la = arm(-1, q.la, q.lh, q.lp), ra = arm(1, q.ra, q.rh, q.rp);
  const big = (c.w || 1) > 1.25, hs = q.hs || (big ? 0.84 : 0.66), htop = (big ? 20 : 92) + bob - (big ? 0 : 0);
  const hd = head(pid, q.expr || 'neutre', sx + (q.hx || 0), htop - 30 * (hs - 0.74) * 4, hs, q.tilt || 0, id);
  const acc = (q.whistle ? `<path d="M${sx - 60} ${top + 4} Q${sx} ${top + 150} ${sx + 60} ${top + 4}" fill="none" stroke="#e5483f" stroke-width="7"/><g transform="translate(${sx + 6},${top + 140}) rotate(${f1(q.blow ? -25 : 0)})"><rect x="-26" y="-14" width="52" height="30" rx="12" fill="#cfd4da" stroke="${K}" stroke-width="5"/><circle cx="14" cy="2" r="7" fill="#555"/></g>` : '')
    + (q.towel ? `<path d="M${sx - tw - 10} ${top + 30} Q${sx - tw + 60} ${top - 30} ${sx - 30} ${top + 10} L${sx - 50} ${top + 300} L${sx - tw - 20} ${top + 280} Z" fill="#ff8fb3" stroke="${K}" stroke-width="6"/><path d="M${sx - tw} ${top + 240} L${sx - 60} ${top + 250}" stroke="#fff" stroke-width="10"/>` : '');
  const stink = (o.stink && q.stink !== 0) ? stinkLines([[40, 600], [560, 580], [30, 820], [570, 800]], t, q.stink || 0.85) : '';
  const shadow = `<ellipse cx="${sx}" cy="1298" rx="${230 + fat}" ry="28" fill="#000" opacity=".28"/>`;
  return `<g>${shadow}${legs}${waist}${torso}${belly}${sweatMarks}${extra}${neck}${hd}${acc}${la.svg}${ra.svg}${la.hand}${ra.hand}${la.prop}${ra.prop}${stink}</g>`;
}

// pompes vues de profil (tête de face). d = 0 bras tendus, 1 en bas, >1.2 écrasé
function plank(pid, q) {
  const c = C[pid], o = OUTFIT[pid] || OUTFIT.YANIS, skin = c.skin, id = ++gid, t = q.t || 0;
  const d = q.d || 0, crash = Math.max(0, Math.min(1, (d - 1) * 5));
  const fy = 1270, feet = [1000, fy - 40];
  const sh = [330, fy - 330 + d * 130 + crash * 90];
  const hip = [700, fy - 250 + d * 90 + crash * 70];
  const legs = tube([hip, [850, (hip[1] + feet[1]) / 2 + 10], feet], 100, o.pants);
  const shoe = `<g transform="translate(${feet[0] + 30},${feet[1] + 8}) rotate(-80)"><path d="M-62 26 Q-64 -24 -22 -28 L30 -26 Q78 -16 80 26 Z" fill="${o.shoes}" stroke="${K}" stroke-width="5"/></g>`;
  const mid = [(sh[0] + hip[0]) / 2, (sh[1] + hip[1]) / 2];
  const sag = 210 + d * 30 + crash * 40 + (q.jiggle || 0) * 6 * Math.sin(t * 22);
  const bodyD = `M${f1(sh[0] - 40)} ${f1(sh[1] - 110)} Q${f1(mid[0])} ${f1(mid[1] - 150)} ${f1(hip[0] + 50)} ${f1(hip[1] - 80)} L${f1(hip[0] + 40)} ${f1(hip[1] + 60)} Q${f1(mid[0] + 40)} ${f1(Math.min(fy, mid[1] + sag))} ${f1(sh[0] - 20)} ${f1(sh[1] + 90)} Z`;
  const torso = `<defs><linearGradient id="pg${id}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${shade(o.top, 0.12)}"/><stop offset=".6" stop-color="${o.top}"/><stop offset="1" stop-color="${shade(o.top, -0.3)}"/></linearGradient></defs>
    <path d="${bodyD}" fill="url(#pg${id})" stroke="${K}" stroke-width="7" stroke-linejoin="round"/>
    <ellipse cx="${f1(mid[0] + 40)}" cy="${f1(mid[1] + 40)}" rx="40" ry="26" fill="#b9813f" opacity=".6"/><path d="M${f1(mid[0] - 60)} ${f1(mid[1] + 70)} q60 30 140 0" fill="none" stroke="${shade(o.top, -0.3)}" stroke-width="5"/>`;
  // bras : coude qui plie vers l'extérieur
  const handY = fy - 12, bend = d * 70 + crash * 60;
  const arm = (dx, back) => { const s = [sh[0] + dx, sh[1] + 30], hnd = [sh[0] + dx - 20 - crash * 60, handY], e = [(s[0] + hnd[0]) / 2 - bend * (back ? 0.6 : 1), (s[1] + hnd[1]) / 2];
    return tube([s, e, hnd], 50, skin) + `<path d="${path([s, P(s, Math.atan2(e[0] - s[0], e[1] - s[1]) * 180 / Math.PI, 50)])}" stroke="${K}" stroke-width="80" stroke-linecap="round"/><path d="${path([s, P(s, Math.atan2(e[0] - s[0], e[1] - s[1]) * 180 / Math.PI, 50)])}" stroke="${o.top}" stroke-width="70" stroke-linecap="round"/>`
      + `<ellipse cx="${f1(hnd[0] - 10)}" cy="${f1(hnd[1])}" rx="34" ry="16" fill="${skin}" stroke="${K}" stroke-width="4"/>`; };
  const hs = 0.8, htop = sh[1] - 470 * hs + 40 + crash * 150;
  const hd = head(pid, q.expr || 'panique', sh[0] - 150, htop, hs, -8 + crash * -12 + Math.sin(t * 3) * 2, id);
  const sweat = [0, 1, 2].map(i => { const ph = (t * 1.6 + i / 3) % 1; return `<path d="M${f1(sh[0] - 280 + i * 90)} ${f1(htop + 200 + ph * 260)} q-14 26 0 34 q14 -8 0 -34 Z" fill="#9fdcff" stroke="${K}" stroke-width="3" opacity="${f1(1 - ph)}"/>`; }).join('');
  const shadow = `<ellipse cx="640" cy="${fy + 12}" rx="440" ry="30" fill="#000" opacity=".3"/>`;
  const stars = crash > 0.5 ? [0, 1, 2].map(i => { const a = t * 4 + i * 2.1; return `<text x="${f1(sh[0] - 160 + Math.cos(a) * 130)}" y="${f1(htop + 40 + Math.sin(a) * 30)}" font-size="54" font-family="Lilita One" fill="#ffd23a" stroke="${K}" stroke-width="3">★</text>`; }).join('') : '';
  return `<g>${shadow}${arm(30, true)}${legs}${shoe}${torso}${hd}${arm(-10, false)}${sweat}${stars}</g>`;
}

// allongé sur le dos (lit ou sol), tête à gauche. q.arm = [épaule, coude] du bras libre ; q.rp = accessoire
function lying(pid, q) {
  const c = C[pid], o = OUTFIT[pid] || OUTFIT.YANIS, skin = c.skin, id = ++gid, t = q.t || 0;
  const by = q.y || 1150, br = (q.breath || 1) * Math.sin(t * 2.4) * 8;
  const legs = tube([[650, by + 10], [850, by - 40], [1010, by + 10]], 100, o.pants) + tube([[640, by + 30], [860, by + 10], [1020, by + 40]], 100, shade(o.pants, -0.1));
  const shoes = [[1040, by - 30], [1050, by + 20]].map(([x, y]) => `<g transform="translate(${x},${y}) rotate(-90)"><path d="M-50 26 Q-52 -24 -18 -28 L26 -26 Q66 -16 68 26 Z" fill="${o.shoes}" stroke="${K}" stroke-width="5"/></g>`).join('');
  const bel = `<defs><radialGradient id="lb${id}" cx=".4" cy=".3" r=".8"><stop offset="0" stop-color="${shade(o.top, 0.15)}"/><stop offset=".6" stop-color="${o.top}"/><stop offset="1" stop-color="${shade(o.top, -0.3)}"/></radialGradient></defs>
    <path d="M260 ${by + 70} Q250 ${by - 120} 360 ${f1(by - 170 - br)} Q520 ${f1(by - 320 - br * 1.6)} 660 ${f1(by - 120 - br)} Q700 ${by - 20} 690 ${by + 70} Z" fill="url(#lb${id})" stroke="${K}" stroke-width="7" stroke-linejoin="round"/>
    <ellipse cx="500" cy="${f1(by - 160 - br)}" rx="38" ry="24" fill="#b9813f" opacity=".7"/><ellipse cx="420" cy="${f1(by - 60)}" rx="24" ry="16" fill="#8f5a3a" opacity=".6"/>
    <ellipse cx="460" cy="${f1(by - 230 - br)}" rx="70" ry="30" fill="#fff" opacity=".12"/>`;
  const sh = [300, by - 80];
  const arm2 = q.arm || [100, 60];
  const e = P(sh, -arm2[0] + 180, 170), h = P(e, -arm2[1] + 180, 150);
  const freeArm = tube([sh, e, h], 50, skin) + hand(h, -arm2[1] + 180, skin, q.rh || 'open');
  const prop = q.rp ? PROPS[q.rp[0]](h[0] + (q.rp[2] || 0), h[1] + (q.rp[3] || 0), q.rp[1] || 0) : '';
  const lowArm = tube([[320, by - 10], [470, by + 30], [600, by + 10]], 50, skin) + hand([600, by + 10], 90, skin);
  const hd = head(pid, q.expr || 'neutre', 170, by - 330, 0.72, -70 + (q.tilt || 0), id);
  const crumbs = (q.crumbs ? [[420, -250], [520, -300], [580, -200], [470, -190], [360, -180]] : []).map(([x, y]) => `<ellipse cx="${x}" cy="${f1(by + y - br)}" rx="12" ry="8" fill="#ffd25a" stroke="${K}" stroke-width="3"/>`).join('');
  const stink = o.stink && q.stink !== 0 ? stinkLines([[420, by - 330], [600, by - 260]], t, 0.7) : '';
  return `<g>${legs}${shoes}${lowArm}${bel}${crumbs}${hd}${prop && q.propBehind ? prop : ''}${freeArm}${prop && !q.propBehind ? prop : ''}${stink}</g>`;
}

module.exports = { stand, plank, lying, PROPS, OUTFIT, shade, stinkLines };
