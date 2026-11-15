// Décors détaillés v2 (1080 x 1920) : sol du fond y=1250, premier plan y=1920
const K = '#1f1a17';
const O = (w = 5) => `stroke="${K}" stroke-width="${w}" stroke-linejoin="round" stroke-linecap="round"`;
const lg = (id, a, b, x2 = 0, y2 = 1) => `<linearGradient id="${id}" x1="0" y1="0" x2="${x2}" y2="${y2}"><stop offset="0" stop-color="${a}"/><stop offset="1" stop-color="${b}"/></linearGradient>`;
const glow = (id, cx, cy, r, col, op) => `<radialGradient id="${id}" gradientUnits="userSpaceOnUse" cx="${cx}" cy="${cy}" r="${r}"><stop offset="0" stop-color="${col}" stop-opacity="${op}"/><stop offset="1" stop-color="${col}" stop-opacity="0"/></radialGradient>`;

function shell(wall, side, floorA, floorB, planks = true) {
  return `<defs>${lg('w2', wall[0], wall[1])}${lg('fl2', floorA, floorB)}</defs>
  <rect width="1080" height="1920" fill="url(#w2)"/>
  <path d="M0 0 L120 90 L120 1250 L0 1420 Z" fill="${side}"/><path d="M1080 0 L960 90 L960 1250 L1080 1420 Z" fill="${side}"/>
  <path d="M0 1420 L120 1250 L960 1250 L1080 1420 L1080 1920 L0 1920 Z" fill="url(#fl2)"/>
  ${planks ? [...Array(12)].map((_, i) => `<path d="M${120 + i * 76} 1250 L${-420 + i * 175} 1920" stroke="#000" stroke-opacity=".16" stroke-width="3"/>`).join('') + [1290, 1350, 1430, 1540, 1690, 1880].map((y, i) => [...Array(6)].map((_, j) => `<path d="M${(j * 220 + i * 90) % 1080} ${y} l0 ${30 + i * 12}" stroke="#000" stroke-opacity=".12" stroke-width="3"/>`).join('') + `<path d="M0 ${y} L1080 ${y}" stroke="#000" stroke-opacity=".1" stroke-width="2"/>`).join('') : ''}
  <path d="M120 1250 L960 1250" stroke="#000" stroke-opacity=".35" stroke-width="5"/><rect x="120" y="1222" width="840" height="28" fill="#000" opacity=".18"/>`;
}

function calendar(x, y, n = 30, label = 'MARIAGE') {
  return `<g transform="translate(${x},${y}) rotate(-3)"><rect x="0" y="0" width="210" height="250" rx="10" fill="#fdfdfd" ${O(6)}/><rect x="0" y="0" width="210" height="66" rx="10" fill="#e5483f" ${O(6)}/>
    <circle cx="50" cy="0" r="9" fill="#666" ${O(3)}/><circle cx="160" cy="0" r="9" fill="#666" ${O(3)}/>
    <text x="105" y="47" font-family="Lilita One" font-size="34" text-anchor="middle" fill="#fff">${label}</text>
    <text x="105" y="186" font-family="Lilita One" font-size="92" text-anchor="middle" fill="#141414">J-${n}</text>
    <text x="105" y="230" font-family="Lilita One" font-size="26" text-anchor="middle" fill="#e5483f">15 DÉCEMBRE</text></g>`;
}

function bed(x, y) {   // lit vu de 3/4, tête de lit à gauche
  return `<g transform="translate(${x},${y})">
    <path d="M0 -330 Q0 -380 50 -380 L110 -380 Q150 -380 150 -330 L150 120 L0 120 Z" fill="#8a5a36" ${O(7)}/>
    <path d="M22 -320 Q22 -350 52 -350 L104 -350 Q128 -350 128 -320 L128 40 L22 40 Z" fill="#a8703f" ${O(4)}/>
    <rect x="10" y="80" width="740" height="70" rx="10" fill="#6e4528" ${O(7)}/>
    <rect x="30" y="150" width="34" height="80" fill="#5a3820" ${O(5)}/><rect x="700" y="150" width="34" height="80" fill="#5a3820" ${O(5)}/>
    <rect x="130" y="-30" width="640" height="120" rx="26" fill="#f4f0e8" ${O(7)}/>
    <path d="M150 50 L760 50" stroke="#d8d0c0" stroke-width="5"/>
    <path d="M150 -120 Q140 -170 200 -176 L330 -170 Q380 -160 370 -110 Q360 -60 300 -60 L190 -64 Q150 -70 150 -120 Z" fill="#fff" ${O(7)}/>
    <path d="M200 -140 q50 20 120 6" fill="none" stroke="#ccc" stroke-width="5"/>
    <path d="M300 -46 Q330 -120 420 -96 Q520 -150 600 -90 Q700 -120 790 -40 L800 110 Q760 130 720 112 Q600 140 470 112 Q380 132 300 100 Z" fill="#3d6fd6" ${O(7)}/>
    <path d="M360 -40 q60 40 150 10 M540 -60 q60 50 160 20 M420 60 q80 -30 180 10" fill="none" stroke="#2a52a8" stroke-width="7" stroke-linecap="round"/>
    <path d="M330 -20 q80 -50 160 -40" fill="none" stroke="#7aa0ff" stroke-width="6" opacity=".6" stroke-linecap="round"/>
  </g>`;
}

function desk(x, y, night) {
  return `<g transform="translate(${x},${y})">
    <rect x="0" y="0" width="300" height="26" fill="#2b2b33" ${O(6)}/><rect x="14" y="26" width="20" height="230" fill="#1c1c22"/><rect x="266" y="26" width="20" height="230" fill="#1c1c22"/>
    <rect x="50" y="-200" width="210" height="140" rx="10" fill="#111" ${O(6)}/><rect x="62" y="-188" width="186" height="114" fill="${night ? '#3ec5ff' : '#2f5d8a'}"/>
    <path d="M62 -110 l40 -30 l30 20 l50 -46 l66 50 L248 -74 L62 -74 Z" fill="#1b6fb0" opacity=".8"/><rect x="140" y="-60" width="30" height="60" fill="#222"/>
    <rect x="70" y="-16" width="170" height="16" rx="5" fill="#333" ${O(3)}/>${[0, 1, 2, 3, 4, 5, 6].map(i => `<rect x="${80 + i * 22}" y="-13" width="14" height="6" fill="${['#ff4fd8', '#4fe1ff', '#ffe14f'][i % 3]}"/>`).join('')}
    ${[0, 1, 2].map(i => `<g transform="translate(${-36 + i * 30},-58) rotate(${[-8, 6, 0][i]})"><rect x="0" y="0" width="26" height="56" rx="6" fill="${['#4caf50', '#e5483f', '#4caf50'][i]}" ${O(4)}/><rect x="0" y="16" width="26" height="12" fill="#111"/></g>`).join('')}
  </g>`;
}

function chair(x, y) {
  return `<g transform="translate(${x},${y})"><rect x="-70" y="-300" width="140" height="300" rx="40" fill="#141418" ${O(6)}/><rect x="-36" y="-280" width="72" height="250" rx="24" fill="#e5483f"/>
    <rect x="-100" y="0" width="200" height="50" rx="20" fill="#141418" ${O(6)}/><rect x="-8" y="50" width="16" height="90" fill="#333"/><path d="M-80 150 L80 150" ${O(10)}/><circle cx="-80" cy="160" r="12" fill="#111"/><circle cx="80" cy="160" r="12" fill="#111"/></g>`;
}

const R = {
  chambreNuit: (o = {}) => `${shell(['#28305e', '#1d2347'], '#1a1f40', '#7b5638', '#4e3420')}
    ${[...Array(15)].map((_, i) => `<rect x="${130 + i * 56}" y="90" width="18" height="1130" fill="#fff" opacity=".035"/>`).join('')}
    <rect x="120" y="90" width="840" height="18" fill="#ff4fd8" opacity=".85"/><rect x="120" y="90" width="840" height="60" fill="#ff4fd8" opacity=".15"/>
    <!-- fenêtre -->
    <rect x="610" y="230" width="300" height="400" fill="#0b1433" ${O(10)}/>
    <circle cx="830" cy="320" r="46" fill="#fff6c8"/><circle cx="812" cy="306" r="46" fill="#0b1433"/>
    ${[[650, 270], [700, 330], [760, 260], [880, 420], [660, 420], [740, 400]].map(([a, b]) => `<circle cx="${a}" cy="${b}" r="4" fill="#fff"/>`).join('')}
    ${[0, 1, 2, 3].map(i => `<rect x="${622 + i * 72}" y="${460 + (i % 2) * 50}" width="60" height="${170 - (i % 2) * 50}" fill="#1e2a55"/><rect x="${632 + i * 72}" y="${490 + (i % 2) * 50}" width="12" height="14" fill="#ffd66b"/><rect x="${652 + i * 72}" y="${530 + (i % 2) * 50}" width="12" height="14" fill="#ffd66b"/>`).join('')}
    <path d="M760 230 L760 630 M610 430 L910 430" ${O(9)}/><rect x="592" y="630" width="336" height="26" fill="#ddd" ${O(5)}/>
    <path d="M580 200 Q630 430 600 690 L650 690 Q668 430 625 200 Z M940 200 Q890 430 920 690 L870 690 Q852 430 895 200 Z" fill="#6b2fa0" ${O(5)}/>
    <rect x="570" y="190" width="380" height="16" rx="8" fill="#333" ${O(4)}/>
    <!-- posters -->
    <g transform="rotate(-2 300 400)"><rect x="170" y="230" width="300" height="220" fill="#1a1a1a" ${O(6)}/><path d="M200 400 Q220 340 290 330 L370 320 Q420 322 440 360 L450 400 Z" fill="#e5483f" ${O(5)}/>
      <circle cx="240" cy="402" r="24" fill="#222" ${O(5)}/><circle cx="410" cy="402" r="24" fill="#222" ${O(5)}/><path d="M300 336 L330 362 L420 360" fill="none" stroke="#9fd4ff" stroke-width="10"/>
      <text x="320" y="290" font-family="Lilita One" font-size="52" text-anchor="middle" fill="#fff">GTR</text></g>
    <rect x="160" y="490" width="160" height="200" fill="#1f3b8c" ${O(6)}/><rect x="226" y="490" width="28" height="200" fill="#e5483f"/><circle cx="240" cy="585" r="46" fill="#1f3b8c" ${O(5)}/><text x="240" y="600" font-family="Lilita One" font-size="42" text-anchor="middle" fill="#fff">PSG</text>
    ${calendar(360, 490, o.day || 30)}
    <!-- étagère -->
    <rect x="160" y="760" width="220" height="16" fill="#6e4528" ${O(4)}/><rect x="180" y="700" width="36" height="60" fill="#ffd23a" ${O(4)}/><rect x="226" y="712" width="30" height="48" fill="#4fe1ff" ${O(4)}/><path d="M290 760 L310 690 L330 760 Z" fill="#e5483f" ${O(4)}/>
    ${desk(650, 1010, true)}${chair(820, 1250)}
    ${bed(70, 1180)}
    <!-- poubelle -->
    <g id="trash" transform="translate(330,170)"><path d="M560 1270 L680 1270 L668 1420 L572 1420 Z" fill="#6c7a89" ${O(6)}/><rect x="550" y="1250" width="140" height="26" rx="8" fill="#56636f" ${O(5)}/><path d="M600 1290 l0 110 M640 1290 l0 110" stroke="#4b5560" stroke-width="5"/></g>
    <!-- bazar au sol -->
    <g transform="translate(110,1620) rotate(-8)"><rect x="0" y="0" width="230" height="40" fill="#e9c27a" ${O(5)}/><rect x="0" y="-26" width="230" height="30" fill="#f2d495" ${O(5)}/><text x="115" y="-2" font-family="Lilita One" font-size="26" text-anchor="middle" fill="#d9342b">PIZZA</text></g>
    <path d="M820 1700 q40 -60 110 -40 q50 -20 90 30 q-10 40 -90 40 q-80 10 -110 -30 Z" fill="#5b6fa8" ${O(5)}/><path d="M860 1690 q40 -30 90 -10" fill="none" stroke="#3e4f80" stroke-width="5"/>
    <path d="M760 1840 q30 -40 70 -10 l20 30 q-50 20 -90 -20 Z" fill="#eee" ${O(4)}/>
    <g transform="translate(420,1820) rotate(20)"><path d="M-30 -40 L30 -42 L34 30 L-32 32 Z" fill="#f2c230" ${O(4)}/></g>
    <ellipse cx="200" cy="1500" rx="0" ry="0"/>
    <!-- lumières -->
    <defs>${glow('gm', 805, 940, 420, '#4fc8ff', 0.4)}${glow('gw', 760, 430, 420, '#9fb8ff', 0.2)}${glow('gv', 540, 1500, 900, '#000', 0)}</defs>
    <rect width="1080" height="1920" fill="#040818" opacity=".16"/><rect width="1080" height="1920" fill="url(#gm)"/><rect width="1080" height="1920" fill="url(#gw)"/>
    <rect width="1080" height="1920" fill="#ff4fd8" opacity=".04"/>`,

  miroir: (o = {}) => `${shell(['#28305e', '#1d2347'], '#1a1f40', '#7b5638', '#4e3420')}
    ${[...Array(15)].map((_, i) => `<rect x="${130 + i * 56}" y="90" width="18" height="1130" fill="#fff" opacity=".035"/>`).join('')}
    <rect x="120" y="90" width="840" height="18" fill="#ff4fd8" opacity=".85"/>
    <rect x="170" y="300" width="160" height="200" fill="#1f3b8c" ${O(6)}/><text x="250" y="420" font-family="Lilita One" font-size="44" text-anchor="middle" fill="#fff">PSG</text>
    ${calendar(170, 560, o.day || 30)}
    <defs>${glow('gm2', 760, 900, 520, '#bfe4ff', 0.25)}</defs>
    <rect width="1080" height="1920" fill="#040818" opacity=".25"/><rect width="1080" height="1920" fill="url(#gm2)"/>`,

  salleDeBain: () => `${shell(['#bfe6ea', '#9fd0d6'], '#8cc2c8', '#e8eef0', '#b8c4c8', false)}
    ${[...Array(14)].map((_, i) => [...Array(19)].map((_, j) => `<rect x="${120 + i * 60}" y="${90 + j * 60}" width="60" height="60" fill="none" stroke="#fff" stroke-opacity=".55" stroke-width="3"/>`).join('')).join('')}
    ${[...Array(9)].map((_, i) => `<path d="M${120 + i * 105} 1250 L${-300 + i * 210} 1920" stroke="#9aa8ad" stroke-width="3"/>`).join('')}${[1330, 1450, 1620, 1840].map(y => `<path d="M0 ${y} L1080 ${y}" stroke="#9aa8ad" stroke-width="3"/>`).join('')}
    <!-- douche -->
    <rect x="620" y="180" width="320" height="1070" fill="#d6f2f6" stroke="${K}" stroke-width="6"/><path d="M780 180 L780 260 L700 260" fill="none" ${O(10)}/><circle cx="700" cy="270" r="30" fill="#bbb" ${O(5)}/>
    <rect x="600" y="160" width="360" height="18" rx="9" fill="#888" ${O(4)}/>
    <path d="M610 178 Q640 600 620 1240 L700 1240 Q720 600 680 178 Z" fill="#ffd23a" ${O(5)}/>${[0, 1, 2, 3].map(i => `<circle cx="${650}" cy="${300 + i * 250}" r="18" fill="#ff8fb3" opacity=".8"/>`).join('')}
    <!-- lavabo + miroir -->
    <rect x="200" y="300" width="300" height="380" rx="30" fill="#e8f7ff" stroke="#8a6a4a" stroke-width="14"/><path d="M240 360 L300 320 M250 440 L380 330" stroke="#fff" stroke-width="12" opacity=".7"/>
    <path d="M180 900 L520 900 Q520 1010 350 1010 Q180 1010 180 900 Z" fill="#fff" ${O(6)}/><rect x="320" y="1000" width="60" height="250" fill="#f2f2f2" ${O(5)}/><path d="M350 900 L350 860 L390 860" fill="none" ${O(8)}/>
    <rect x="190" y="830" width="40" height="70" rx="8" fill="#2f6fd6" ${O(4)}/><rect x="240" y="845" width="34" height="55" rx="8" fill="#2f6fd6" ${O(4)}/><rect x="284" y="840" width="34" height="60" rx="8" fill="#2f6fd6" ${O(4)}/>
    <rect x="440" y="820" width="50" height="80" rx="10" fill="#5bbf4a" ${O(4)}/>
    <rect x="140" y="720" width="22" height="160" fill="#888"/><path d="M140 720 L120 720 L120 880" fill="none" ${O(4)}/><path d="M120 730 L60 730 L60 880 L120 880" fill="#ff8fb3" ${O(5)}/>
    <ellipse cx="300" cy="1560" rx="170" ry="50" fill="#5bbf4a" opacity=".8" ${O(4)}/>
    <defs>${glow('gb', 540, 300, 900, '#ffffff', 0.35)}</defs><rect width="1080" height="1920" fill="url(#gb)"/>`,
  parc: () => `<defs>${lg('sky', '#ffb36b', '#ffe3a8')}${lg('gr', '#7cc35a', '#4f9a3a')}</defs>
    <rect width="1080" height="1920" fill="url(#sky)"/><circle cx="780" cy="560" r="120" fill="#fff3b0"/><circle cx="780" cy="560" r="200" fill="#fff3b0" opacity=".3"/>
    ${[0, 1, 2, 3, 4, 5].map(i => `<rect x="${i * 190 - 20}" y="${720 - (i % 3) * 90}" width="150" height="${400 + (i % 3) * 90}" fill="#c9a0b8" opacity=".55"/>`).join('')}
    <path d="M0 1000 Q270 900 540 980 Q800 1050 1080 940 L1080 1300 L0 1300 Z" fill="#6aa84f"/>
    <rect x="0" y="1100" width="1080" height="820" fill="url(#gr)"/>
    <path d="M0 1420 L1080 1420 L1080 1700 L0 1700 Z" fill="#d9b98a"/><path d="M0 1420 L1080 1420" stroke="#b89868" stroke-width="8"/><path d="M0 1700 L1080 1700" stroke="#b89868" stroke-width="8"/>`,
  rue: () => `<defs>${lg('sky2', '#ffd09a', '#ffefcf')}</defs><rect width="1080" height="1920" fill="url(#sky2)"/>
    <rect x="40" y="200" width="1000" height="1250" fill="#e6c9a8" ${O(7)}/>${[0, 1, 2].map(i => [0, 1, 2, 3].map(j => `<rect x="${110 + i * 320}" y="${260 + j * 230}" width="180" height="160" fill="#9fd4ff" ${O(5)}/><path d="M${200 + i * 320} ${260 + j * 230} L${200 + i * 320} ${420 + j * 230}" ${O(4)}/>`).join('')).join('')}
    <rect x="420" y="1120" width="240" height="330" fill="#6e4528" ${O(7)}/><rect x="400" y="1090" width="280" height="40" fill="#555" ${O(5)}/><circle cx="625" cy="1290" r="10" fill="#ffd23a"/><text x="540" y="1080" font-family="Lilita One" font-size="40" text-anchor="middle" fill="#6e4528">BÂT. B</text>
    <rect x="0" y="1450" width="1080" height="470" fill="#b9b2aa"/>${[...Array(8)].map((_, i) => `<path d="M${i * 150} 1450 L${i * 150 - 120} 1920" stroke="#9a948c" stroke-width="5"/>`).join('')}<path d="M0 1450 L1080 1450" stroke="#7a746c" stroke-width="10"/>
    <defs>${glow('gr2', 540, 300, 1000, '#fff', 0.25)}</defs><rect width="1080" height="1920" fill="url(#gr2)"/>`,
  salleMuscu: () => `${shell(['#4a505c', '#363b45'], '#2f343e', '#2a2c33', '#141519', false)}
    ${[...Array(9)].map((_, i) => `<path d="M${120 + i * 105} 1250 L${-300 + i * 210} 1920" stroke="#fff" stroke-opacity=".05" stroke-width="3"/>`).join('')}
    <rect x="150" y="280" width="780" height="520" fill="#9fb4c8" opacity=".25" ${O(6)}/><path d="M410 280 L410 800 M670 280 L670 800" stroke="#000" stroke-opacity=".3" stroke-width="6"/>
    <text x="540" y="580" font-family="Lilita One" font-size="110" text-anchor="middle" fill="#ff3b3b" stroke="${K}" stroke-width="6" opacity=".85">IRON CITÉ</text>
    ${[0, 1, 2].map(i => `<rect x="${200 + i * 250}" y="70" width="180" height="20" rx="10" fill="#f4fbff"/>`).join('')}
    <rect x="170" y="880" width="740" height="22" fill="#666" ${O()}/>${[0, 1, 2, 3, 4, 5].map(i => `<g transform="translate(${200 + i * 118},836)"><rect x="0" y="0" width="22" height="${44 + i * 3}" rx="5" fill="#222" ${O(3)}/><rect x="22" y="${16 + i}" width="40" height="10" fill="#aaa"/><rect x="62" y="0" width="22" height="${44 + i * 3}" rx="5" fill="#222" ${O(3)}/></g>`).join('')}
    <rect x="720" y="1000" width="240" height="40" rx="10" fill="#c0392b" ${O()}/><rect x="740" y="1040" width="22" height="200" fill="#555"/><rect x="918" y="1040" width="22" height="200" fill="#555"/>
    <path d="M680 950 L1000 950" stroke="#c9c9c9" stroke-width="14"/><circle cx="692" cy="950" r="50" fill="#1c1c1c" ${O()}/><circle cx="988" cy="950" r="50" fill="#1c1c1c" ${O()}/>
    <rect x="150" y="960" width="84" height="280" rx="38" fill="#b03a2e" ${O()}/><path d="M192 900 L192 960" ${O(6)}/>
    <rect x="290" y="1090" width="130" height="150" fill="#2e7d32" ${O()}/><text x="355" y="1180" font-family="Lilita One" font-size="40" text-anchor="middle" fill="#fff">EAU</text>
    <path d="M60 1520 L1020 1520 L1060 1760 L20 1760 Z" fill="#2f6fd6" ${O(6)}/><path d="M80 1540 L1000 1540" stroke="#5a8ff0" stroke-width="5"/>
    <defs>${glow('gs', 540, 150, 900, '#ffffff', 0.25)}</defs><rect width="1080" height="1920" fill="url(#gs)"/>`,

  cuisine: () => `${shell(['#f1c38c', '#e3a868'], '#cf8f50', '#c9a27a', '#9a7450', false)}
    ${[...Array(10)].map((_, i) => `<path d="M${120 + i * 94} 1250 L${-400 + i * 210} 1920" stroke="#000" stroke-opacity=".08" stroke-width="3"/>`).join('')}
    ${[0, 1, 2, 3, 4].map(i => [0, 1].map(j => `<rect x="${150 + i * 156}" y="${820 + j * 110}" width="146" height="100" fill="#fff4e0" stroke="#d8b890" stroke-width="3"/>`).join('')).join('')}
    <rect x="140" y="1050" width="800" height="200" fill="#a7774a" ${O()}/><rect x="130" y="1030" width="820" height="30" fill="#e8d8c0" ${O()}/>${[0, 1, 2, 3].map(i => `<rect x="${160 + i * 196}" y="1080" width="170" height="150" rx="6" fill="#b88555" ${O(4)}/><circle cx="${300 + i * 196}" cy="1150" r="8" fill="${K}"/>`).join('')}
    <rect x="160" y="230" width="340" height="300" fill="#b9733a" ${O()}/><path d="M330 230 L330 530" ${O()}/><circle cx="315" cy="390" r="9" fill="${K}"/><circle cx="345" cy="390" r="9" fill="${K}"/>
    <rect x="590" y="250" width="320" height="330" fill="#a7d8ff" ${O(8)}/><path d="M750 250 L750 580 M590 415 L910 415" ${O(8)}/>
    <path d="M240 1030 q0 -110 110 -110 q110 0 110 110 Z" fill="#c4502e" ${O()}/><path d="M350 920 l0 -34" ${O(10)}/>
    <rect x="650" y="900" width="200" height="130" fill="#f4f4f4" ${O()}/>${[0, 1, 2].map(i => `<rect x="${668 + i * 60}" y="920" width="44" height="60" fill="#ffcf6a" ${O(3)}/>`).join('')}
    <path d="M540 0 L540 110" ${O(5)}/><path d="M470 180 L500 110 L580 110 L610 180 Z" fill="#f2c230" ${O()}/>
    
    <defs>${glow('gk', 540, 220, 900, '#fff1c0', 0.45)}</defs><rect width="1080" height="1920" fill="url(#gk)"/>`,
};
module.exports = { ROOMS2: R, calendar, shell, glow, lg, bed, desk, chair };
