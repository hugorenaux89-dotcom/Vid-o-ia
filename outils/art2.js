// Lana 30 jours — dessins 2D supplémentaires (lit, livreur, bal, couloir, nuit)
const A = require('./art');
const { K, O, C, clamp, esc } = A;

// Grand lit vu de face : fond (tête de lit + oreiller) et devant (couette)
function litFond(t) {
  return `<g filter="url(#sh)">
   <rect x="70" y="600" width="580" height="420" rx="30" fill="#5b3b2c" ${O(7)}/>
   <rect x="95" y="625" width="530" height="370" rx="22" fill="#6b4632"/>
   <path d="M120 660 h480" stroke="#7d5640" stroke-width="10" stroke-linecap="round"/>
   <rect x="40" y="960" width="640" height="120" rx="20" fill="#f1eefa" ${O(7)}/>
   <path d="M150 905 q60 -60 140 -30 q50 -40 120 -10 q70 -20 130 30 l-10 70 h-370z" fill="#efe9ff" ${O(6)}/>
  </g>`;
}
function couette(t, y = 990, wig = 0) {
  return `<g filter="url(#sh)">
   <path d="M10 ${y + wig} q100 -50 240 -20 q120 -40 230 0 q120 -30 230 25 v300 h-700z" fill="#9b7fd6" ${O(8)}/>
   <path d="M60 ${y + 60 + wig} q120 -30 240 0 M380 ${y + 50 - wig} q120 -30 250 10" fill="none" stroke="#7d62bd" stroke-width="7"/>
   <path d="M30 ${y + 160} q300 -40 660 0" fill="none" stroke="#b9a5ea" stroke-width="10" opacity=".7"/>
  </g>`;
}
function tableDeNuit(t, o = {}) {
  const lit = o.ecran ? 1 : 0;
  const v = o.vibre ? Math.sin(t * 90) * 4 : 0;
  return `<g filter="url(#sh)">
   <rect x="${o.x ?? 560}" y="${o.y ?? 860}" width="170" height="230" rx="10" fill="#5b3b2c" ${O(6)}/>
   <rect x="${(o.x ?? 560) + 15}" y="${(o.y ?? 860) + 70}" width="140" height="10" fill="#4a2f22"/>
   <g transform="translate(${(o.x ?? 560) + 85 + v} ${(o.y ?? 860) - 6}) rotate(${-8 + v})">
    ${lit ? `<ellipse cx="0" cy="-30" rx="110" ry="90" fill="url(#glow)" opacity=".9"/>` : ''}
    <rect x="-45" y="-14" width="90" height="16" rx="5" fill="#1b1b1b" ${O(4)}/>
    <rect x="-38" y="-12" width="76" height="9" rx="3" fill="${lit ? '#9fdcff' : '#222'}"/>
   </g>
   ${o.vibre ? `<path d="M${(o.x ?? 560) + 10} ${(o.y ?? 860) - 40} q-14 14 0 28 M${(o.x ?? 560) + 160} ${(o.y ?? 860) - 40} q14 14 0 28" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round"/>` : ''}
  </g>`;
}
const nuit = (k = 1) => `<rect width="720" height="1280" fill="#0b1440" opacity="${(0.55 * k).toFixed(2)}"/>`;
const matin = (k = 1) => `<rect width="720" height="1280" fill="#ffb35c" opacity="${(0.13 * k).toFixed(2)}"/>`;

// Livreur de pizza
function livreur(P = {}) {
  const t = P.t || 0;
  const SK = '#c68c5a', SKD = '#a8703f';
  const worry = P.worry || 0;
  const bl = A.clamp(Math.max(0.12, P.blink || 0));
  const eye = (cx) => `<ellipse cx="${cx}" cy="560" rx="24" ry="27" fill="#fff" ${O(5)}/><circle cx="${cx - 6}" cy="566" r="10" fill="#2b1a10"/><circle cx="${cx - 3}" cy="562" r="3" fill="#fff"/>
     <path d="M${cx - 32} ${537 - 4} h64 v${(bl * 54).toFixed(1)} h-64z" fill="${SK}"/>`;
  return `<g transform="translate(${P.x || 0} ${P.y || 0}) translate(360 1230) scale(${P.s || 1}) translate(-360 -1230)">
   <path d="M262 1000 L250 1200 L340 1200 L352 1010 Z" fill="#33334a" ${O(7)}/><path d="M368 1010 L380 1200 L470 1200 L458 1000 Z" fill="#33334a" ${O(7)}/>
   ${[295, 425].map((x) => `<path d="M${x - 60} 1235 q0 -40 40 -40 h40 q40 10 40 40z" fill="#fff" ${O(7)}/>`).join('')}
   <path d="M222 790 Q235 735 360 728 Q485 735 498 790 L515 1010 L205 1010 Z" fill="#e23b3b" ${O(7)}/>
   <rect x="300" y="820" width="120" height="44" rx="8" fill="#fff" ${O(4)}/><text x="360" y="852" font-family="Anton" font-size="28" fill="#e23b3b" text-anchor="middle">PIZZA</text>
   <path d="M232 800 Q170 860 200 930 L300 930 L290 880 Z" fill="#e23b3b" ${O(7)}/><path d="M488 800 Q550 860 520 930 L420 930 L430 880 Z" fill="#e23b3b" ${O(7)}/>
   ${P.boite !== false ? `<g filter="url(#sh)"><rect x="170" y="905" width="380" height="50" rx="6" fill="#e8c08b" ${O(6)}/><text x="360" y="940" font-family="Anton" font-size="26" fill="#b5462b" text-anchor="middle">PIZZA</text></g>
   <circle cx="200" cy="935" r="28" fill="${SK}" ${O(6)}/><circle cx="520" cy="935" r="28" fill="${SK}" ${O(6)}/>` : ''}
   <path d="M330 700 h60 v40 q-30 14 -60 0z" fill="${SKD}" ${O(5)}/>
   <g transform="rotate(${(P.headRot || 0) - worry * 8} 360 720)">
    <ellipse cx="360" cy="570" rx="140" ry="150" fill="${SK}" ${O(7)}/>
    <path d="M216 570 q-30 -10 -28 30 q4 35 34 30z M504 570 q30 -10 28 30 q-4 35 -34 30z" fill="${SK}" ${O(6)}/>
    <path d="M222 520 Q230 410 360 405 Q490 410 498 520 Q430 470 360 475 Q290 470 222 520 Z" fill="#e23b3b" ${O(7)}/>
    <path d="M300 470 Q360 430 470 470 L560 500 Q520 520 470 505 Z" fill="#c22a2a" ${O(6)}/>
    <text x="360" y="465" font-family="Anton" font-size="34" fill="#fff" text-anchor="middle">🍕</text>
    <path d="M${270} ${520 - worry * 14} q30 ${-10 - worry * 10} 60 ${-2 + worry * 8}" fill="none" stroke="#1a1a1a" stroke-width="10" stroke-linecap="round"/>
    <path d="M${390} ${518 + worry * 6} q30 ${-8 - worry * 12} 60 ${4 + worry * 6}" fill="none" stroke="#1a1a1a" stroke-width="10" stroke-linecap="round"/>
    ${eye(305)}${eye(415)}
    <path d="M362 595 q-12 30 6 38" fill="none" ${O(5)}/>
    ${worry > 0.4 ? `<path d="M330 672 q30 -18 60 0" fill="none" ${O(5)}/>` : `<path d="M330 662 q30 16 60 0" fill="none" ${O(5)}/>`}
    <path d="M290 690 q70 30 140 0" fill="none" stroke="#1a1a1a" stroke-width="4" opacity=".5"/>
   </g>
  </g>`;
}

function couloir(t, o = {}) {
  const ouverte = o.ouverte ?? 0;
  let w = ''; for (let x = 0; x < 720; x += 60) w += `<rect x="${x}" y="0" width="30" height="1060" fill="#fff" opacity=".03"/>`;
  return `<rect width="720" height="1280" fill="#3a2a55"/>${w}
   <rect x="0" y="1060" width="720" height="220" fill="#3e2c3a"/>
   <rect x="150" y="330" width="420" height="740" fill="#1d1430" ${O(7)}/>
   ${ouverte ? `<rect x="150" y="330" width="420" height="740" fill="#e9c98a" opacity=".85"/><rect x="150" y="330" width="420" height="740" fill="url(#glowW)" opacity=".5"/>` : ''}
   <g transform="translate(150 330) scale(${(1 - ouverte * 0.85).toFixed(3)} 1)">
    <rect x="0" y="0" width="420" height="740" fill="#7b4a2e" ${O(7)}/>
    <rect x="50" y="60" width="320" height="260" rx="8" fill="#6a3f27" ${O(5)}/><rect x="50" y="400" width="320" height="260" rx="8" fill="#6a3f27" ${O(5)}/>
    <circle cx="370" cy="380" r="18" fill="#d9b14a" ${O(4)}/>
    <circle cx="210" cy="190" r="12" fill="#222" ${O(3)}/>
   </g>
   <rect x="138" y="318" width="444" height="20" fill="#2a1d40" ${O(5)}/>
   ${o.fente ? `<rect x="150" y="1062" width="420" height="10" fill="#fff1b8"/><path d="M150 1072 L120 1280 H600 L570 1072 Z" fill="#fff1b8" opacity=".18"/>` : ''}
   ${o.pieds ? [-1, 1].map((s) => `<ellipse cx="${360 + s * 45 + Math.sin(t * 2) * 12}" cy="1068" rx="38" ry="7" fill="#000"/>`).join('') : ''}
   <rect x="610" y="610" width="40" height="60" rx="8" fill="#ddd" ${O(4)}/><circle cx="630" cy="640" r="10" fill="${o.sonnette ? '#ffd23f' : '#999'}" ${O(3)}/>
   <rect x="250" y="1110" width="220" height="60" rx="10" fill="#e23b3b" ${O(5)}/><text x="360" y="1152" font-family="Anton" font-size="30" fill="#fff" text-anchor="middle">BIENVENUE</text>`;
}

function bal(t, k = 0) {
  const bulbs = [];
  for (const side of [-1, 1]) for (let i = 0; i < 9; i++) {
    const u = i / 8; const x = 360 + side * (40 + u * 340); const y = 160 + u * 150 + Math.sin(u * Math.PI) * 40;
    const c = ['#ffd23f', '#ff7aa8', '#7fe0ff'][i % 3];
    const a = (0.3 + 0.3 * Math.sin(t * 3 + i + side)) * (1 - 0.7 * k);
    bulbs.push(`<circle cx="${x}" cy="${y}" r="22" fill="${c}" opacity="${a.toFixed(2)}"/><circle cx="${x}" cy="${y}" r="8" fill="${c}" ${O(3)}/>`);
  }
  const disco = Array.from({ length: 6 }, (_, i) => `<path d="M${360 - 60 + i * 20} 120 v80" stroke="#9aa6c0" stroke-width="2" opacity=".6"/>`).join('');
  return `<rect width="720" height="1280" fill="#241640"/>
   <rect x="0" y="0" width="720" height="1000" fill="#2f1d55"/>
   ${[0, 1, 2, 3, 4, 5].map((i) => `<rect x="${i * 120}" y="560" width="116" height="440" fill="#3b2768" ${O(4)}/>`).join('')}
   <rect x="110" y="380" width="500" height="110" rx="10" fill="#e84f8a" ${O(6)}/>
   <text x="360" y="455" font-family="Anton" font-size="56" fill="#fff" text-anchor="middle">BAL DE FIN D'ANNÉE 2016</text>
   <path d="M20 160 Q190 300 360 160 Q530 300 700 160" fill="none" stroke="#222" stroke-width="3"/>${bulbs.join('')}
   <g transform="translate(360 150) rotate(${(t * 30) % 360})"><circle r="46" fill="#cfd6e6" ${O(5)}/>${disco}<path d="M-46 0 h92 M0 -46 v92" stroke="#9aa6c0" stroke-width="3"/></g>
   <rect x="0" y="1000" width="720" height="280" fill="#6b4a32"/>
   ${[0, 1, 2, 3].map((i) => `<line x1="0" y1="${1040 + i * 60}" x2="720" y2="${1040 + i * 60}" stroke="#5a3b26" stroke-width="5"/>`).join('')}
   <ellipse cx="360" cy="1180" rx="${200 + 60 * k}" ry="50" fill="#fff6c8" opacity="${(0.15 + 0.25 * k).toFixed(2)}"/>
   <path d="M${300 - 40 * k} 0 L${120 - 60 * k} 1180 H${600 + 60 * k} L${420 + 40 * k} 0Z" fill="#fff6c8" opacity="${(0.06 + 0.12 * k).toFixed(2)}"/>`;
}
const cadeau = (x, y) => `<g transform="translate(${x} ${y})" filter="url(#sh)"><rect x="-55" y="-45" width="110" height="90" rx="6" fill="#e84f8a" ${O(5)}/><rect x="-8" y="-45" width="16" height="90" fill="#ffd23f"/><rect x="-55" y="-8" width="110" height="16" fill="#ffd23f"/><path d="M0 -45 q-30 -40 -40 -10 q20 10 40 10 q20 0 40 -10 q-10 -30 -40 10z" fill="#ffd23f" ${O(4)}/></g>`;

function zzz(t, x, y) {
  return [0, 1, 2].map((i) => { const k = ((t * 0.6 + i / 3) % 1); return `<text x="${x + k * 60}" y="${y - k * 120}" font-family="Anton" font-size="${30 + k * 30}" fill="#fff" opacity="${(1 - k).toFixed(2)}" stroke="${K}" stroke-width="5" paint-order="stroke">Z</text>`; }).join('');
}

module.exports = { litFond, couette, tableDeNuit, nuit, matin, livreur, couloir, bal, cadeau, zzz };
