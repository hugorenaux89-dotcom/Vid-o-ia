// Personnage corps entier « plus réaliste » : proportions naturelles, volumes ombrés, mains avec doigts. viewBox 0 0 600 1300
const { toonPerson, C } = require('./toon2');
const K = '#1f1a17';

function shade(hex, f) {
  const n = parseInt(hex.slice(1), 16);
  const ch = s => Math.max(0, Math.min(255, Math.round(((n >> s) & 255) * (1 + f))));
  return '#' + [16, 8, 0].map(s => ch(s).toString(16).padStart(2, '0')).join('');
}

const OUTFIT = {
  YANIS_J1: { top: '#9ea2a8', short: true, stains: true, belly: true, pants: '#4b5878', shoes: '#ececec', stink: true },
  YANIS_A: { top: '#9ea2a8', short: true, stains: true, belly: true, pants: '#4b5878', shoes: '#ececec', stink: true },
  YANIS: { top: '#8d9096', pants: '#2f3a52', shoes: '#f2f2f2' },
  NADIA: { top: '#dcc6a3', pants: '#7a63a0', shoes: '#5a4a3a', dress: true },
  SOFIANE: { top: '#1b1b1b', pants: '#1b1b1b', shoes: '#f2f2f2', stripes: true },
  SARAH: { top: '#ead8bc', pants: '#7aa3d6', shoes: '#f2f2f2', slim: true },
  KENZO: { top: '#151515', pants: '#222', shoes: '#f2f2f2', wide: true, text: 'COACH' },
  LINA: { top: '#ffffff', pants: '#3a4a6a', shoes: '#f2f2f2', slim: true, apron: true },
};

// membre « cylindrique » : contour + couleur + ombre + reflet
function tube(pts, w, color) {
  const d = 'M' + pts.map(p => p.map(v => v.toFixed(1)).join(' ')).join(' L');
  return `<path d="${d}" fill="none" stroke="${K}" stroke-width="${w + 8}" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="${d}" fill="none" stroke="${color}" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="${d}" fill="none" stroke="${shade(color, -0.22)}" stroke-width="${w * 0.42}" stroke-linecap="round" stroke-linejoin="round" transform="translate(${w * 0.22},2)" opacity=".75"/>
    <path d="${d}" fill="none" stroke="${shade(color, 0.25)}" stroke-width="${w * 0.18}" stroke-linecap="round" stroke-linejoin="round" transform="translate(${-w * 0.25},0)" opacity=".7"/>`;
}

function sleeveTube(pts, w, color) {
  const d = 'M' + pts.map(p => p.map(v => v.toFixed(1)).join(' ')).join(' L');
  return `<path d="${d}" fill="none" stroke="${K}" stroke-width="${w + 8}" stroke-linecap="round"/><path d="${d}" fill="none" stroke="${color}" stroke-width="${w}" stroke-linecap="round"/>`;
}
function arm(x, y, a1, a2, skin, sleeve, sleeveLen) {
  const r = d => d * Math.PI / 180;
  const L1 = 175, L2 = 160;
  const e = [x + Math.sin(r(a1)) * L1, y + Math.cos(r(a1)) * L1];
  const h = [e[0] + Math.sin(r(a2)) * L2, e[1] + Math.cos(r(a2)) * L2];
  const s = [x + Math.sin(r(a1)) * sleeveLen, y + Math.cos(r(a1)) * sleeveLen];
  return { svg: tube([[x, y], e, h], 46, skin) + (sleeve ? sleeveTube([[x, y], s], 66, sleeve) : ''), hand: h, ang: a2 };
}

function hand(p, ang, skin) {
  const [x, y] = p;
  const fingers = [-14, -5, 4, 13].map((dx, i) => `<rect x="${(x + dx - 5).toFixed(1)}" y="${(y + 14).toFixed(1)}" width="11" height="${22 + (i === 1 || i === 2 ? 4 : 0)}" rx="5.5" fill="${skin}" stroke="${K}" stroke-width="3.5"/>`).join('');
  return `<g transform="rotate(${(-ang).toFixed(1)} ${x.toFixed(1)} ${y.toFixed(1)})">${fingers}
    <ellipse cx="${x.toFixed(1)}" cy="${(y + 8).toFixed(1)}" rx="24" ry="22" fill="${skin}" stroke="${K}" stroke-width="4"/>
    <ellipse cx="${(x - 22).toFixed(1)}" cy="${(y + 4).toFixed(1)}" rx="8" ry="14" fill="${skin}" stroke="${K}" stroke-width="3.5" transform="rotate(25 ${(x - 22).toFixed(1)} ${(y + 4).toFixed(1)})"/>
    <ellipse cx="${(x + 6).toFixed(1)}" cy="${(y + 6).toFixed(1)}" rx="12" ry="9" fill="${shade(skin, 0.18)}" opacity=".6"/></g>`;
}

const POSES = { idle: [[18, 6], [-18, -6]], panic: [[150, 172], [-150, -172]], phone: [[18, 6], [-35, -168]],
  fist: [[18, 6], [-165, -178]], tired: [[8, 2], [-8, -2]], flex: [[95, 178], [-95, -178]], point: [[18, 6], [-90, -90]] };

let gid = 0;
function body(pid, expr = 'neutre', talk = false, pose = 'idle') {
  const c = C[pid] || C.YANIS, o = OUTFIT[pid] || OUTFIT.YANIS, skin = c.skin, id = ++gid;
  const fat = o.belly ? 46 : 0, wide = o.wide ? 34 : o.slim ? -26 : 0;
  const [L, R] = POSES[pose] || POSES.idle;
  const sx = 300, sh = 470;                       // épaules
  const shoulderW = 150 + wide + fat * 0.6;
  // --- jambes
  const hipY = 860, kneeY = 1050, ankY = 1215;
  const lx = sx - 62 - fat * 0.3 - wide * 0.2, rx = sx + 62 + fat * 0.3 + wide * 0.2;
  const legs = tube([[lx, hipY], [lx - 6, kneeY], [lx - 10, ankY]], 92 + fat * 0.5, o.pants) + tube([[rx, hipY], [rx + 6, kneeY], [rx + 10, ankY]], 92 + fat * 0.5, o.pants)
    + `<path d="M${lx - 30} ${kneeY} q20 10 40 0 M${rx - 10} ${kneeY} q20 10 40 0" fill="none" stroke="${shade(o.pants, -0.3)}" stroke-width="4"/>`;
  const shoe = x => `<path d="M${x - 60} 1262 Q${x - 62} 1214 ${x - 22} 1210 L${x + 30} 1212 Q${x + 78} 1222 ${x + 80} 1262 Z" fill="${o.shoes}" stroke="${K}" stroke-width="5"/>
    <rect x="${x - 64}" y="1254" width="148" height="16" rx="8" fill="${shade(o.shoes, -0.25)}" stroke="${K}" stroke-width="4"/>
    <path d="M${x - 14} 1222 l18 0 M${x - 10} 1232 l18 0" stroke="${K}" stroke-width="3"/>`;
  const shoes = shoe(lx - 14) + shoe(rx + 14);
  // --- torse
  const top = sh - 30, bot = o.short ? 700 : 880;
  const tw = shoulderW;
  const torsoPath = `M${sx - tw} ${top + 40} Q${sx - tw + 10} ${top} ${sx - 60} ${top - 6} Q${sx} ${top + 22} ${sx + 60} ${top - 6} Q${sx + tw - 10} ${top} ${sx + tw} ${top + 40} L${sx + tw - 8 + fat * 0.4} ${bot} Q${sx} ${bot + 24} ${sx - tw + 8 - fat * 0.4} ${bot} Z`;
  const torso = o.dress ? `<path d="M${sx - tw} ${top + 40} Q${sx} ${top - 20} ${sx + tw} ${top + 40} L${sx + tw + 60} 1010 L${sx - tw - 60} 1010 Z" fill="${o.top}" stroke="${K}" stroke-width="6"/>`
    : `<defs><linearGradient id="tg${id}" x1="0" x2="1" y1="0" y2="0"><stop offset="0" stop-color="${shade(o.top, 0.12)}"/><stop offset=".55" stop-color="${o.top}"/><stop offset="1" stop-color="${shade(o.top, -0.25)}"/></linearGradient></defs>
       <path d="${torsoPath}" fill="url(#tg${id})" stroke="${K}" stroke-width="6" stroke-linejoin="round"/>
       <path d="M${sx - 40} ${top + 120} q30 40 10 90 M${sx + 50} ${top + 150} q-20 50 4 100 M${sx - tw + 40} ${top + 200} q20 30 10 70" fill="none" stroke="${shade(o.top, -0.28)}" stroke-width="4" opacity=".7"/>`;
  // ventre SOUS le tee-shirt : tissu tendu, ombré, avec plis et ourlet
  const belly = o.belly ? `<defs><radialGradient id="bg${id}" cx=".36" cy=".3" r=".8"><stop offset="0" stop-color="${shade(o.top, 0.14)}"/><stop offset=".6" stop-color="${o.top}"/><stop offset="1" stop-color="${shade(o.top, -0.3)}"/></radialGradient></defs>
    <path d="M${sx - tw + 4} ${bot - 120} Q${sx - tw - fat * 0.9} ${bot + 70} ${sx - tw + 30} ${bot + 175} Q${sx} ${bot + 215} ${sx + tw - 30} ${bot + 175} Q${sx + tw + fat * 0.9} ${bot + 70} ${sx + tw - 4} ${bot - 120} Z" fill="url(#bg${id})"/>
    <path d="M${sx - tw + 4} ${bot - 120} Q${sx - tw - fat * 0.9} ${bot + 70} ${sx - tw + 30} ${bot + 175} Q${sx} ${bot + 215} ${sx + tw - 30} ${bot + 175} Q${sx + tw + fat * 0.9} ${bot + 70} ${sx + tw - 4} ${bot - 120}" fill="none" stroke="${K}" stroke-width="6" stroke-linejoin="round"/>
    <path d="M${sx - tw + 40} ${bot + 160} Q${sx} ${bot + 196} ${sx + tw - 40} ${bot + 160}" fill="none" stroke="${shade(o.top, -0.35)}" stroke-width="5"/>
    <path d="M${sx - 70} ${bot + 20} q40 30 90 18 M${sx - 90} ${bot + 80} q60 30 140 10 M${sx + 40} ${bot - 40} q30 20 60 10 M${sx - tw + 30} ${bot + 40} q20 30 18 70 M${sx + tw - 30} ${bot + 40} q-20 30 -18 70" fill="none" stroke="${shade(o.top, -0.3)}" stroke-width="4" stroke-linecap="round" opacity=".8"/>
    <ellipse cx="${sx + 60}" cy="${bot + 60}" rx="34" ry="22" fill="#b9813f" opacity=".7"/><ellipse cx="${sx - 50}" cy="${bot + 120}" rx="22" ry="15" fill="#8f5a3a" opacity=".6"/><circle cx="${sx + 10}" cy="${bot + 150}" r="10" fill="#b9813f" opacity=".7"/>
    <ellipse cx="${sx - 40}" cy="${bot - 10}" rx="${tw * 0.4}" ry="60" fill="#fff" opacity=".08"/>` : '';
  const waist = `<path d="M${sx - tw + 6} ${hipY - 40} Q${sx} ${hipY - 10} ${sx + tw - 6} ${hipY - 40} L${sx + tw - 2} ${hipY + 10} Q${sx} ${hipY + 40} ${sx - tw + 2} ${hipY + 10} Z" fill="${o.pants}" stroke="${K}" stroke-width="6"/>
    <path d="M${sx - 14} ${hipY - 18} l-8 46 M${sx + 14} ${hipY - 18} l8 46" stroke="#e8e8e8" stroke-width="5"/>`;
  const stains = o.stains ? `<ellipse cx="${sx - 50}" cy="${top + 110}" rx="36" ry="24" fill="#b9813f" opacity=".7"/><ellipse cx="${sx + 70}" cy="${top + 170}" rx="26" ry="18" fill="#8f5a3a" opacity=".65"/><circle cx="${sx + 30}" cy="${top + 70}" r="14" fill="#b9813f" opacity=".7"/>
    <ellipse cx="${sx - tw + 38}" cy="${top + 120}" rx="30" ry="40" fill="${shade(o.top, -0.3)}" opacity=".75"/><ellipse cx="${sx + tw - 38}" cy="${top + 120}" rx="30" ry="40" fill="${shade(o.top, -0.3)}" opacity=".75"/>` : '';
  const extra = (o.text ? `<text x="${sx}" y="${top + 160}" font-family="Anton" font-size="58" text-anchor="middle" fill="#fff">${o.text}</text>` : '')
    + (o.stripes ? `<path d="M${sx - tw - 26} ${top + 130} L${sx - tw + 30} ${top + 50} M${sx + tw + 26} ${top + 130} L${sx + tw - 30} ${top + 50}" stroke="#fff" stroke-width="10"/>` : '')
    + (o.apron ? `<path d="M${sx - 100} ${top + 140} L${sx + 100} ${top + 140} L${sx + 110} ${bot} L${sx - 110} ${bot} Z" fill="#dcc29a" stroke="${K}" stroke-width="5"/>` : '');
  const neck = `<path d="M${sx - 40} 380 L${sx - 40} ${top + 10} Q${sx} ${top + 34} ${sx + 40} ${top + 10} L${sx + 40} 380 Z" fill="${shade(skin, -0.12)}" stroke="${K}" stroke-width="6"/>`;
  // --- bras (devant le corps)
  const la = arm(sx - tw + 18, top + 52, -L[0], -L[1], skin, o.dress ? null : o.top, o.short ? 52 : 160);
  const ra = arm(sx + tw - 18, top + 52, -R[0], -R[1], skin, o.dress ? null : o.top, o.short ? 52 : 160);
  const phone = pose === 'phone' ? `<rect x="${(ra.hand[0] - 30).toFixed(1)}" y="${(ra.hand[1] - 78).toFixed(1)}" width="60" height="108" rx="12" fill="#1c1c1c" stroke="${K}" stroke-width="5"/><rect x="${(ra.hand[0] - 23).toFixed(1)}" y="${(ra.hand[1] - 70).toFixed(1)}" width="46" height="86" rx="6" fill="#8fd4ff"/>` : '';
  const stink = o.stink ? [[70, 520], [520, 500], [60, 700], [530, 700]].map(([x, y]) => `<path d="M${x} ${y} q-16 -24 0 -48 q16 -24 0 -48 q-16 -24 0 -48" fill="none" stroke="#7bc96f" stroke-width="7" stroke-linecap="round" opacity=".8"/>`).join('') : '';
  // --- tête (visage BD + ombrage)
  const big = (c.w || 1) > 1.25, hs = big ? 0.74 : 0.6, hx = sx - 300 * hs, hy = big ? 70 : 108;
  const head = `<defs><clipPath id="hc${id}"><ellipse cx="300" cy="300" rx="285" ry="290"/></clipPath>
      <linearGradient id="fs${id}" x1="0" x2="1"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#3a1d0a" stop-opacity=".22"/></linearGradient></defs>
    <g transform="translate(${hx},${hy - 20}) scale(${hs})"><g clip-path="url(#hc${id})">${toonPerson(pid, expr, talk)}
      <ellipse cx="300" cy="300" rx="285" ry="290" fill="url(#fs${id})"/></g></g>`;
  const floorShadow = `<ellipse cx="${sx}" cy="1268" rx="${200 + fat}" ry="26" fill="#000" opacity=".25"/>`;
  return `<g>${floorShadow}${legs}${shoes}${waist}${torso}${belly}${stains}${extra}${neck}${head}${la.svg}${ra.svg}${hand(la.hand, la.ang, skin)}${hand(ra.hand, ra.ang, skin)}${phone}${stink}</g>`;
}

module.exports = { body, OUTFIT };
