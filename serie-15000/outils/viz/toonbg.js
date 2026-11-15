// Décors détaillés style BD (1080 x 1920), contours épais
const K = '#141414';
const O = (w = 7) => `stroke="${K}" stroke-width="${w}" stroke-linejoin="round" stroke-linecap="round"`;
const night = (a = .35) => `<rect width="1080" height="1920" fill="#0a1430" opacity="${a}"/>`;
const floor = (y, c) => `<rect y="${y}" width="1080" height="${1920 - y}" fill="${c}"/><path d="M0 ${y} L1080 ${y}" ${O()}/>`;
const win = (x, y, w, h, sky = '#9fd3ff', city = true) => `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${sky}" ${O()}/>
  ${city ? [0, 1, 2, 3].map(i => `<rect x="${x + 10 + i * w / 4}" y="${y + h * (0.35 + (i % 2) * 0.15)}" width="${w / 5}" height="${h}" fill="#5a6b8a"/>`).join('') + `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="none" ${O()}/>` : ''}
  <path d="M${x + w / 2} ${y} L${x + w / 2} ${y + h} M${x} ${y + h / 2} L${x + w} ${y + h / 2}" ${O(8)}/>`;
const poster = (x, y, w, h, c, t) => `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${c}" ${O()}/>${t ? `<text x="${x + w / 2}" y="${y + h / 2 + 18}" font-family="Anton" font-size="${Math.min(52, w / 5)}" text-anchor="middle" fill="#fff">${t}</text>` : ''}`;
const plant = (x, y) => `<rect x="${x - 40}" y="${y}" width="80" height="90" fill="#c46a3c" ${O()}/><path d="M${x} ${y} q-60 -80 -20 -150 q20 70 20 150 q10 -110 50 -160 q10 100 -50 160" fill="#4caf50" ${O(6)}/>`;
const lamp = (x, y) => `<path d="M${x} 0 L${x} ${y}" ${O(6)}/><path d="M${x - 70} ${y + 70} L${x - 40} ${y} L${x + 40} ${y} L${x + 70} ${y + 70} Z" fill="#f2c230" ${O()}/><ellipse cx="${x}" cy="${y + 180}" rx="230" ry="160" fill="#fff3b0" opacity=".14"/>`;
const tires = (x, y) => [0, 1, 2].map(i => `<ellipse cx="${x}" cy="${y - i * 70}" rx="120" ry="40" fill="#1b1b1b" ${O()}/><ellipse cx="${x}" cy="${y - i * 70}" rx="55" ry="16" fill="#555"/>`).join('');

const BG = {
  garage: () => `<rect width="1080" height="1920" fill="#4d6178"/>${floor(1250, '#3a4049')}
    <ellipse cx="760" cy="1500" rx="210" ry="40" fill="#14171c" opacity=".6"/>
    <rect x="120" y="140" width="840" height="34" rx="17" fill="#e8f6ff" ${O()}/>
    <rect x="70" y="330" width="460" height="330" fill="#9a7b55" ${O()}/>
    ${[0, 1, 2, 3, 4, 5, 6, 7].map(i => [0, 1, 2, 3, 4].map(j => `<circle cx="${105 + i * 56}" cy="${365 + j * 62}" r="6" fill="#5e4a33"/>`).join('')).join('')}
    <path d="M140 380 l40 200" stroke="#c9ced6" stroke-width="22" stroke-linecap="round"/>
    <rect x="230" y="370" width="26" height="170" rx="6" fill="#e5483f" ${O()}/><rect x="220" y="360" width="46" height="40" rx="6" fill="#9aa1ab" ${O()}/>
    <path d="M330 380 q30 -10 40 20 l-20 150 h-20 z" fill="#f2c230" ${O()}/><circle cx="440" cy="430" r="40" fill="none" stroke="#c9ced6" stroke-width="14"/>
    ${poster(620, 320, 300, 200, '#d94b3d', 'GARAGE')}
    <rect x="600" y="600" width="400" height="24" fill="#6b5640" ${O()}/>
    ${[0, 1, 2, 3].map(i => `<rect x="${620 + i * 92}" y="${520 + (i % 2) * 14}" width="62" height="${80 - (i % 2) * 14}" rx="8" fill="${['#3d8bff', '#e5483f', '#f2c230', '#4caf50'][i]}" ${O(5)}/>`).join('')}
    ${tires(160, 1180)}
    <rect x="880" y="700" width="40" height="560" fill="#e0b84a" ${O()}/><rect x="1000" y="700" width="40" height="560" fill="#e0b84a" ${O()}/><rect x="860" y="1050" width="220" height="30" fill="#c9a23c" ${O()}/>`,
  garageNuit: () => BG.garage() + night(.45) + `<rect x="80" y="110" width="920" height="120" fill="#bfe6ff" opacity=".15"/>`,
  bureau: () => `<rect width="1080" height="1920" fill="#5c6f86"/>${floor(1300, '#40464f')}
    ${win(620, 200, 380, 420, '#33415a', false)}<rect x="640" y="220" width="340" height="380" fill="#2a3446" opacity=".6"/>
    <rect x="80" y="700" width="560" height="380" rx="14" fill="#1f2530" ${O()}/>${[0, 1, 2, 3].map(i => `<rect x="${104 + (i % 2) * 262}" y="${724 + Math.floor(i / 2) * 170}" width="246" height="156" fill="#2f5d8a" ${O(5)}/>`).join('')}
    <text x="360" y="1060" font-family="Anton" font-size="40" text-anchor="middle" fill="#ff5a5a">23:11 → 23:34</text>
    <rect x="300" y="1080" width="120" height="80" fill="#2a2f38" ${O()}/>
    ${poster(90, 220, 240, 330, '#f2f2f2', '')}<text x="210" y="300" font-family="Anton" font-size="44" text-anchor="middle" fill="#d94b3d">NOV.</text>${[0, 1, 2, 3].map(r => [0, 1, 2, 3, 4].map(c => `<rect x="${110 + c * 42}" y="${330 + r * 50}" width="30" height="30" fill="#ddd"/>`).join('')).join('')}
    <rect x="760" y="1180" width="260" height="120" fill="#c9a074" ${O()}/>${[0, 1, 2].map(i => `<rect x="${780 + i * 70}" y="${1150 - i * 6}" width="60" height="40" fill="#f4f4f4" ${O(4)}/>`).join('')}` + night(.3),
  chambre: () => `<rect width="1080" height="1920" fill="#6a5a8e"/>${floor(1300, '#5a4a3a')}
    ${win(640, 220, 360, 420)}
    ${poster(80, 220, 300, 420, '#e5483f', 'GTR')}${poster(400, 300, 190, 260, '#3d8bff', 'PSG')}
    <rect x="60" y="1040" width="560" height="200" fill="#3d8bff" ${O()}/><rect x="60" y="980" width="200" height="90" rx="30" fill="#f4f4f4" ${O()}/>
    <rect x="700" y="900" width="320" height="30" fill="#8a6a4a" ${O()}/><rect x="760" y="760" width="200" height="140" rx="10" fill="#1d1d1d" ${O()}/><rect x="776" y="776" width="168" height="108" fill="#2f5d8a"/>
    <rect x="870" y="1000" width="140" height="300" rx="20" fill="#e5483f" ${O()}/>${plant(620, 1210)}`,
  chambreNuit: () => BG.chambre() + night(.55) + `<ellipse cx="860" cy="830" rx="260" ry="200" fill="#9fd3ff" opacity=".12"/>`,
  cuisine: () => `<rect width="1080" height="1920" fill="#e8a65e"/>${floor(1350, '#b07a4a')}
    ${[0, 1, 2, 3, 4, 5, 6].map(i => [0, 1, 2].map(j => `<rect x="${i * 160 + 10}" y="${720 + j * 120}" width="140" height="100" fill="#f4c88e" ${O(4)}/>`).join('')).join('')}
    <rect x="40" y="200" width="420" height="280" fill="#c97a3a" ${O()}/><path d="M250 200 L250 480" ${O()}/><circle cx="235" cy="340" r="10" fill="${K}"/><circle cx="265" cy="340" r="10" fill="${K}"/>
    ${win(580, 180, 420, 360, '#9fd3ff')}
    <rect x="0" y="1080" width="1080" height="50" fill="#8a5a3a" ${O()}/>
    <path d="M150 1080 q0 -120 120 -120 q120 0 120 120 z" fill="#c4502e" ${O()}/><path d="M270 960 l0 -40" ${O(10)}/><path d="M230 900 q20 -40 0 -80 M300 900 q20 -40 0 -80" fill="none" stroke="#fff" stroke-width="8" opacity=".7"/>
    <rect x="760" y="900" width="180" height="180" fill="#f4f4f4" ${O()}/>${[0, 1, 2].map(i => `<rect x="${775 + i * 55}" y="925" width="40" height="55" fill="#ffcf6a" ${O(4)}/>`).join('')}
    ${lamp(540, 60)}`,
  cuisineNuit: () => BG.cuisine() + night(.6),
  boulangerie: () => `<rect width="1080" height="1920" fill="#f4dfb8"/>${floor(1380, '#a8794e')}
    ${[0, 1].map(r => `<rect x="40" y="${260 + r * 260}" width="1000" height="26" fill="#a8794e" ${O()}/>` + [0, 1, 2, 3, 4, 5].map(i => `<ellipse cx="${120 + i * 165}" cy="${230 + r * 260}" rx="64" ry="32" fill="#d9963f" ${O(5)}/><path d="M${90 + i * 165} ${220 + r * 260} l20 18 m20 -20 l20 18" ${O(4)}/>`).join('')).join('')}
    ${[0, 1, 2, 3, 4, 5, 6].map(i => `<path d="M${60 + i * 150} 760 q40 -90 120 -20" fill="none" stroke="#c98a3f" stroke-width="34" stroke-linecap="round"/><path d="M${60 + i * 150} 760 q40 -90 120 -20" fill="none" ${O(5)}/>`).join('')}
    <rect x="0" y="1050" width="1080" height="330" fill="#e9f6ff" opacity=".7" ${O()}/>${[0, 1, 2, 3, 4].map(i => `<path d="M${80 + i * 200} 1180 q40 -60 100 -10 q40 -50 80 10 z" fill="#e8a65e" ${O(5)}/>`).join('')}
    ${poster(380, 820, 320, 140, '#d94b3d', 'BOULANGERIE')}`,
  parking: () => `<rect width="1080" height="1920" fill="#8fd0f5"/><circle cx="880" cy="200" r="90" fill="#ffe06a" ${O()}/>
    ${[[60, 520], [260, 420], [480, 560], [700, 460], [900, 540]].map(([x, h]) => `<rect x="${x}" y="${1200 - h}" width="170" height="${h}" fill="#c9cfd8" ${O()}/>` + [0, 1, 2, 3].map(r => `<rect x="${x + 25}" y="${1200 - h + 30 + r * 90}" width="40" height="50" fill="#6fa8dc" ${O(4)}/><rect x="${x + 105}" y="${1200 - h + 30 + r * 90}" width="40" height="50" fill="#6fa8dc" ${O(4)}/>`).join('')).join('')}
    ${floor(1200, '#6b7079')}${[0, 1, 2, 3].map(i => `<path d="M${120 + i * 260} 1260 L${80 + i * 260} 1600" stroke="#fff" stroke-width="12"/>`).join('')}
    <rect x="60" y="1060" width="300" height="140" rx="50" fill="#ff7ab8" ${O()}/><circle cx="120" cy="1200" r="40" fill="#222" ${O()}/><circle cx="300" cy="1200" r="40" fill="#222" ${O()}/><rect x="110" y="1080" width="180" height="60" rx="16" fill="#bfe6ff" ${O(5)}/>
    <rect x="700" y="1000" width="300" height="190" fill="#c8a06a" ${O()}/><text x="850" y="1080" font-family="Anton" font-size="56" text-anchor="middle" fill="#3a2a1a">YANIS LAVAGE</text><text x="850" y="1160" font-family="Anton" font-size="60" text-anchor="middle" fill="#d94b3d">40€</text>
    <path d="M600 1250 l-30 120 h120 l-30 -120 z" fill="#3d8bff" ${O()}/>`,
  voiture: () => `<rect width="1080" height="1920" fill="#101830"/>
    ${[[120, 300], [420, 220], [760, 340], [980, 260]].map(([x, y]) => `<circle cx="${x}" cy="${y}" r="70" fill="#ffcf6a" opacity=".25"/><circle cx="${x}" cy="${y}" r="16" fill="#ffe7a0"/>`).join('')}
    <path d="M0 140 Q540 60 1080 140 L1080 900 Q540 820 0 900 Z" fill="none" ${O(16)}/>
    <path d="M0 1250 Q540 1080 1080 1250 L1080 1920 L0 1920 Z" fill="#23283a" ${O()}/>
    <circle cx="300" cy="1360" r="150" fill="#1a1e2c" ${O()}/><circle cx="300" cy="1360" r="70" fill="#2a3044" ${O()}/>
    <rect x="620" y="1260" width="300" height="100" rx="20" fill="#0d1018" ${O()}/><rect x="650" y="1290" width="120" height="40" fill="#3be0ff" opacity=".7"/>
    <rect x="460" y="40" width="160" height="60" rx="10" fill="#222" ${O()}/>`,
  rue: () => `<rect width="1080" height="1920" fill="#1a2550"/>${[[0, 700], [200, 900], [420, 600], [640, 1000], [860, 760]].map(([x, h]) => `<rect x="${x}" y="${1350 - h}" width="220" height="${h}" fill="#2b3766" ${O()}/>` + [0, 1, 2, 3, 4, 5].map(r => [0, 1].map(c => (r + c + x) % 3 ? `<rect x="${x + 40 + c * 90}" y="${1350 - h + 40 + r * 110}" width="50" height="60" fill="#ffd66b" ${O(4)}/>` : '').join('')).join('')).join('')}
    ${floor(1350, '#2c2f3a')}<rect x="880" y="700" width="24" height="650" fill="#555" ${O()}/><path d="M870 700 q30 -60 90 -40" fill="none" ${O(10)}/><circle cx="960" cy="680" r="120" fill="#ffd27a" opacity=".2"/><circle cx="960" cy="680" r="24" fill="#ffe7a0" ${O(5)}/>
    <circle cx="900" cy="200" r="70" fill="#f2f0d8" ${O()}/>`,
  rueJour: () => `<rect width="1080" height="1920" fill="#9fd3ff"/>${[[0, 700], [200, 900], [420, 600], [640, 1000], [860, 760]].map(([x, h]) => `<rect x="${x}" y="${1350 - h}" width="220" height="${h}" fill="#d9cdb8" ${O()}/>` + [0, 1, 2, 3, 4, 5].map(r => [0, 1].map(c => `<rect x="${x + 40 + c * 90}" y="${1350 - h + 40 + r * 110}" width="50" height="60" fill="#6fa8dc" ${O(4)}/>`).join('')).join('')).join('')}
    ${floor(1350, '#8a8f98')}<rect x="120" y="1250" width="260" height="150" rx="40" fill="#e5483f" ${O()}/><circle cx="170" cy="1400" r="40" fill="#222" ${O()}/><circle cx="330" cy="1400" r="40" fill="#222" ${O()}/>`,
  hall: () => `<rect width="1080" height="1920" fill="#8a7f6a"/>${floor(1350, '#5a5244')}
    ${[0, 1, 2, 3, 4].map(i => [0, 1, 2].map(j => `<rect x="${80 + i * 190}" y="${300 + j * 150}" width="160" height="120" fill="#b9b19a" ${O(5)}/><rect x="${110 + i * 190}" y="${330 + j * 150}" width="100" height="14" fill="${K}"/>`).join('')).join('')}
    <rect x="60" y="120" width="960" height="30" rx="15" fill="#fff5d6" ${O()}/>${poster(380, 820, 320, 200, '#f2f2f2', 'INTERDIT')}<text x="540" y="990" font-family="Inter" font-weight="800" font-size="26" text-anchor="middle" fill="#333">DE FUMER</text>
    <rect x="760" y="900" width="240" height="450" fill="#6b4e33" ${O()}/><circle cx="790" cy="1130" r="12" fill="#d4af37" ${O(4)}/>` + night(.25),
  pmu: () => `<rect width="1080" height="1920" fill="#1f5a44"/>${floor(1350, '#3a2a20')}
    <rect x="60" y="180" width="520" height="320" rx="10" fill="#0d0d0d" ${O()}/><rect x="80" y="200" width="480" height="280" fill="#2f8f4e"/><path d="M80 420 L560 420" stroke="#fff" stroke-width="6"/>${[0, 1, 2].map(i => `<path d="M${140 + i * 150} 400 l30 -40 l30 40" fill="#8a5a3a" ${O(5)}/>`).join('')}
    <text x="820" y="320" font-family="Anton" font-size="150" text-anchor="middle" fill="#ff3b6b" stroke="${K}" stroke-width="6">PMU</text>
    <rect x="0" y="1050" width="1080" height="80" fill="#c9ced6" ${O()}/><rect x="0" y="1130" width="1080" height="220" fill="#7a4e30" ${O()}/>
    ${[0, 1, 2, 3, 4].map(i => `<rect x="${120 + i * 180}" y="${960 - (i % 2) * 30}" width="40" height="${90 + (i % 2) * 30}" rx="10" fill="${['#4caf50', '#e5483f', '#f2c230', '#3d8bff', '#9b59b6'][i]}" ${O(5)}/>`).join('')}
    <rect x="620" y="560" width="400" height="300" fill="#e8d5b0" ${O()}/><text x="820" y="660" font-family="Anton" font-size="56" text-anchor="middle" fill="#3a2a1a">TABAC</text><text x="820" y="760" font-family="Anton" font-size="44" text-anchor="middle" fill="#d94b3d">LOTO · PMU</text>`,
  cave: () => `<rect width="1080" height="1920" fill="#2a221c"/>${floor(1350, '#1c1612')}
    <path d="M540 0 L540 220" ${O(6)}/><circle cx="540" cy="250" r="40" fill="#ffe7a0" ${O(6)}/><circle cx="540" cy="250" r="420" fill="#ffd27a" opacity=".14"/>
    ${[[60, 900, 260, 200], [120, 700, 200, 200], [760, 860, 280, 240], [820, 640, 200, 220], [380, 1100, 300, 250]].map(([x, y, w, h], i) => `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${['#9a7048', '#8a6440', '#a07a50', '#7a5a3a', '#b08a5a'][i]}" ${O()}/><path d="M${x} ${y + 40} L${x + w} ${y + 40}" ${O(5)}/>`).join('')}
    <text x="530" y="1250" font-family="Anton" font-size="70" text-anchor="middle" fill="#2a1a10">MALIK</text>
    ${[0, 1, 2, 3, 4, 5].map(i => `<path d="M${i * 200} 0 L${i * 200 + 60} 120" stroke="#3a3028" stroke-width="10"/>`).join('')}`,
  commissariat: () => `<rect width="1080" height="1920" fill="#8a9bb0"/>${floor(1350, '#5a6270')}
    <rect x="0" y="0" width="1080" height="160" fill="#25344a" ${O()}/><text x="540" y="115" font-family="Anton" font-size="96" text-anchor="middle" fill="#fff">POLICE</text>
    ${poster(80, 300, 260, 340, '#f2f2f2', '')}<text x="210" y="380" font-family="Anton" font-size="44" text-anchor="middle" fill="#d94b3d">AVIS DE</text><text x="210" y="440" font-family="Anton" font-size="44" text-anchor="middle" fill="#d94b3d">RECHERCHE</text><rect x="150" y="470" width="120" height="140" fill="#bbb" ${O(4)}/>
    <rect x="0" y="1000" width="1080" height="350" fill="#3a4a62" ${O()}/><rect x="600" y="860" width="300" height="140" rx="10" fill="#1d1d1d" ${O()}/><rect x="620" y="880" width="260" height="100" fill="#2f5d8a"/>
    <rect x="800" y="300" width="200" height="200" fill="#f2f2f2" ${O()}/><circle cx="900" cy="400" r="80" fill="#fff" ${O()}/><path d="M900 400 L900 340 M900 400 L940 420" ${O(6)}/>`,
  entrepot: () => `<rect width="1080" height="1920" fill="#0e1016"/>${floor(1350, '#16181e')}
    <path d="M1080 200 L200 900 L520 1250 Z" fill="#fff6c8" opacity=".16"/>
    ${[0, 1, 2].map(i => `<rect x="40" y="${300 + i * 220}" width="380" height="20" fill="#3a3d45" ${O()}/>` + [0, 1, 2].map(j => `<rect x="${60 + j * 120}" y="${220 + i * 220}" width="90" height="80" fill="#4a4e58" ${O(4)}/>`).join('')).join('')}
    <path d="M300 1250 Q420 980 700 1000 Q960 1020 1020 1250 Z" fill="#7a8088" ${O()}/><path d="M360 1120 Q600 1060 980 1140" fill="none" ${O(5)}/>
    ${[0, 1, 2, 3].map(i => `<rect x="${560 + i * 120}" y="120" width="90" height="140" fill="#2a3446" ${O(5)}/>`).join('')}`,
  toit: () => `<rect width="1080" height="1920" fill="#141a3e"/>${Array.from({ length: 50 }, (_, i) => `<circle cx="${(i * 97) % 1080}" cy="${(i * 53) % 700}" r="${2 + (i % 3)}" fill="#fff" opacity=".8"/>`).join('')}
    <circle cx="860" cy="260" r="90" fill="#f2f0d8" ${O()}/>
    ${[[0, 300], [140, 420], [300, 260], [440, 520], [600, 340], [760, 460], [920, 300]].map(([x, h]) => `<rect x="${x}" y="${1150 - h}" width="150" height="${h}" fill="#232c5c" ${O(5)}/>` + [0, 1, 2, 3].map(r => (r + x) % 2 ? `<rect x="${x + 30}" y="${1150 - h + 30 + r * 70}" width="30" height="30" fill="#ffd66b"/><rect x="${x + 90}" y="${1150 - h + 30 + r * 70}" width="30" height="30" fill="#ffd66b"/>` : '').join('')).join('')}
    <path d="M520 1150 L540 800 L560 1150 Z" fill="#3a4480" ${O(5)}/>
    ${floor(1250, '#3a3e4e')}<rect x="0" y="1150" width="1080" height="100" fill="#55596a" ${O()}/>`,
};
BG.police = () => BG.garageNuit() + `<circle cx="80" cy="500" r="520" fill="#2d6bff" opacity=".35"/><circle cx="1000" cy="560" r="480" fill="#ff2d3d" opacity=".3"/>`;
module.exports = { BG };
