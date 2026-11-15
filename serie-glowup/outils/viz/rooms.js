// Décors en perspective avec éclairage (1080 x 1920)
const K = '#1f1a17';
const O = (w = 5) => `stroke="${K}" stroke-width="${w}" stroke-linejoin="round"`;
const grad = (id, a, b, vertical = true) => `<linearGradient id="${id}" x1="0" y1="0" x2="${vertical ? 0 : 1}" y2="${vertical ? 1 : 0}"><stop offset="0" stop-color="${a}"/><stop offset="1" stop-color="${b}"/></linearGradient>`;
const light = (cx, cy, r, color, op) => `<radialGradient id="l${cx}${cy}" cx="${cx / 1080}" cy="${cy / 1920}" r="${r}"><stop offset="0" stop-color="${color}" stop-opacity="${op}"/><stop offset="1" stop-color="${color}" stop-opacity="0"/></radialGradient>`;
// pièce : mur du fond + murs latéraux + sol en perspective
function room(wall, side, floor, floorLines = true) {
  return `<defs>${grad('wall', wall[0], wall[1])}${grad('side', side[0], side[1], false)}${grad('fl', floor[0], floor[1])}</defs>
  <rect width="1080" height="1920" fill="url(#wall)"/>
  <path d="M0 0 L150 120 L150 1250 L0 1500 Z" fill="${side[0]}" opacity=".9"/><path d="M1080 0 L930 120 L930 1250 L1080 1500 Z" fill="${side[1]}" opacity=".9"/>
  <path d="M0 1500 L150 1250 L930 1250 L1080 1500 L1080 1920 L0 1920 Z" fill="url(#fl)"/>
  ${floorLines ? [0, 1, 2, 3, 4, 5, 6].map(i => `<path d="M${150 + i * 130} 1250 L${-200 + i * 247} 1920" stroke="#000" stroke-opacity=".12" stroke-width="3"/>`).join('') + [1330, 1440, 1590, 1780].map(y => `<path d="M0 ${y} L1080 ${y}" stroke="#000" stroke-opacity=".1" stroke-width="3"/>`).join('') : ''}
  <path d="M150 120 L930 120 M150 1250 L930 1250 M150 120 L150 1250 M930 120 L930 1250" stroke="#000" stroke-opacity=".25" stroke-width="4"/>`;
}
const R = {
  chambre: (night = false) => `${room(['#7b6aa8', '#5e4f8a'], ['#5a4a85', '#4e4078'], ['#8a6a4a', '#5e4630'])}
    <rect x="590" y="260" width="300" height="380" fill="${night ? '#16224a' : '#a7d8ff'}" ${O(8)}/>
    ${[0, 1, 2, 3].map(i => `<rect x="${605 + i * 72}" y="${400 + (i % 2) * 60}" width="56" height="${240 - (i % 2) * 60}" fill="${night ? '#2a3768' : '#7d93b8'}"/>` + (night ? `<rect x="${615 + i * 72}" y="${430 + (i % 2) * 60}" width="12" height="14" fill="#ffd66b"/><rect x="${640 + i * 72}" y="${470 + (i % 2) * 60}" width="12" height="14" fill="#ffd66b"/>` : '')).join('')}
    <path d="M740 260 L740 640 M590 450 L890 450" ${O(10)}/><rect x="570" y="640" width="340" height="24" fill="#ddd" ${O()}/>
    <path d="M560 240 Q610 450 580 680 L620 680 Q640 450 600 240 Z M920 240 Q870 450 900 680 L860 680 Q840 450 880 240 Z" fill="#c0392b" ${O(4)}/>
    <rect x="200" y="300" width="250" height="330" fill="#e5483f" ${O()}/><path d="M230 560 q95 -130 190 0" fill="none" stroke="#fff" stroke-width="12"/><text x="325" y="380" font-family="Anton" font-size="62" text-anchor="middle" fill="#fff">GTR</text>
    <rect x="210" y="700" width="140" height="190" fill="#3d8bff" ${O()}/><text x="280" y="815" font-family="Anton" font-size="52" text-anchor="middle" fill="#fff">PSG</text>
    <path d="M170 1080 L520 1080 L560 1300 L150 1340 Z" fill="#2f6fd6" ${O()}/><path d="M170 1080 L520 1080 L520 1040 L170 1040 Z" fill="#f2f2f2" ${O()}/><ellipse cx="250" cy="1050" rx="70" ry="28" fill="#fff" ${O(4)}/>
    <path d="M200 1150 q80 30 160 -6 q60 40 140 10" fill="none" stroke="#1f5ab0" stroke-width="6"/>
    <rect x="700" y="980" width="220" height="24" fill="#8a6a4a" ${O()}/><rect x="715" y="1004" width="16" height="200" fill="#6a4e33"/><rect x="890" y="1004" width="16" height="200" fill="#6a4e33"/>
    <rect x="740" y="860" width="150" height="110" rx="8" fill="#1c1c1c" ${O()}/><rect x="752" y="872" width="126" height="86" fill="${night ? '#4fa3ff' : '#2f5d8a'}"/>
    ${[0, 1, 2].map(i => `<rect x="${750 + i * 42}" y="950" width="26" height="30" rx="4" fill="${['#4caf50', '#f2c230', '#e5483f'][i]}" ${O(3)}/>`).join('')}
    <path d="M140 1360 q40 -20 90 0 q-20 30 -90 0 Z M760 1420 q60 -30 120 4 q-50 30 -120 -4 Z" fill="#c9b8a0" ${O(4)}/>
    ${night ? `<defs>${light(820, 900, 0.4, '#7fc8ff', 0.35)}</defs><rect width="1080" height="1920" fill="#060a1c" opacity=".45"/><rect width="1080" height="1920" fill="url(#l820900)"/>` : `<defs>${light(740, 450, 0.55, '#fff6d0', 0.35)}</defs><rect width="1080" height="1920" fill="url(#l740450)"/>`}`,
  salleMuscu: () => `${room(['#4a505c', '#363b45'], ['#3a3f4a', '#2f343e'], ['#26282e', '#121317'], true)}
    <rect x="150" y="300" width="780" height="520" fill="#9fb4c8" opacity=".3" ${O()}/><path d="M410 300 L410 820 M670 300 L670 820" stroke="#000" stroke-opacity=".3" stroke-width="5"/>
    <text x="540" y="230" font-family="Anton" font-size="120" text-anchor="middle" fill="#ff3b3b" stroke="${K}" stroke-width="5">IRON CITÉ</text>
    ${[0, 1, 2].map(i => `<rect x="${200 + i * 250}" y="80" width="180" height="20" rx="10" fill="#f4fbff"/>`).join('')}
    <rect x="170" y="880" width="740" height="22" fill="#666" ${O()}/>${[0, 1, 2, 3, 4, 5].map(i => `<g transform="translate(${200 + i * 118},840)"><rect x="0" y="0" width="22" height="${40 + i * 3}" rx="5" fill="#222" ${O(3)}/><rect x="22" y="${14 + i}" width="40" height="10" fill="#aaa"/><rect x="62" y="0" width="22" height="${40 + i * 3}" rx="5" fill="#222" ${O(3)}/></g>`).join('')}
    <rect x="700" y="1010" width="260" height="40" rx="10" fill="#c0392b" ${O()}/><rect x="720" y="1050" width="22" height="190" fill="#555"/><rect x="918" y="1050" width="22" height="190" fill="#555"/>
    <path d="M660 960 L1000 960" stroke="#c9c9c9" stroke-width="14"/><circle cx="672" cy="960" r="48" fill="#1c1c1c" ${O()}/><circle cx="988" cy="960" r="48" fill="#1c1c1c" ${O()}/>
    <rect x="170" y="980" width="80" height="260" rx="36" fill="#b03a2e" ${O()}/><path d="M210 940 L210 980" ${O(6)}/>
    <rect x="300" y="1080" width="140" height="160" fill="#2e7d32" ${O()}/><text x="370" y="1180" font-family="Anton" font-size="38" text-anchor="middle" fill="#fff">EAU</text>
    <rect x="0" y="0" width="1080" height="1920" fill="#ff3020" opacity=".05"/>
    <defs>${light(540, 120, 0.6, '#ffffff', 0.25)}</defs><rect width="1080" height="1920" fill="url(#l540120)"/>`,
  cuisine: () => `${room(['#f1c38c', '#e3a868'], ['#d99a5a', '#cf8f50'], ['#c9a27a', '#9a7450'])}
    ${[0, 1, 2, 3, 4].map(i => [0, 1].map(j => `<rect x="${170 + i * 150}" y="${830 + j * 110}" width="140" height="100" fill="#fff4e0" stroke="#d8b890" stroke-width="3"/>`).join('')).join('')}
    <rect x="160" y="1050" width="760" height="200" fill="#a7774a" ${O()}/><rect x="150" y="1030" width="780" height="30" fill="#e8d8c0" ${O()}/>
    <rect x="180" y="240" width="330" height="300" fill="#b9733a" ${O()}/><path d="M345 240 L345 540" ${O()}/><circle cx="330" cy="400" r="9" fill="${K}"/><circle cx="360" cy="400" r="9" fill="${K}"/>
    <rect x="590" y="260" width="300" height="330" fill="#a7d8ff" ${O(8)}/><path d="M740 260 L740 590 M590 425 L890 425" ${O(8)}/>
    <path d="M250 1030 q0 -110 110 -110 q110 0 110 110 Z" fill="#c4502e" ${O()}/><path d="M360 920 l0 -34" ${O(10)}/><path d="M320 880 q20 -40 0 -80 M390 880 q20 -40 0 -80" fill="none" stroke="#fff" stroke-width="8" opacity=".7"/>
    <rect x="650" y="900" width="200" height="130" fill="#f4f4f4" ${O()}/>${[0, 1, 2].map(i => `<rect x="${668 + i * 60}" y="920" width="44" height="60" fill="#ffcf6a" ${O(3)}/>`).join('')}
    <path d="M540 0 L540 120" ${O(5)}/><path d="M470 190 L500 120 L580 120 L610 190 Z" fill="#f2c230" ${O()}/>
    <defs>${light(540, 260, 0.5, '#fff1c0', 0.45)}</defs><rect width="1080" height="1920" fill="url(#l540260)"/>`,
};
R.chambreNuit = () => R.chambre(true);
module.exports = { ROOMS: R };
