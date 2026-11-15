// Générateur d'images Lana 30 jours (SVG -> PNG via Playwright)
const S = 'stroke="#141414" stroke-width="7" stroke-linejoin="round" stroke-linecap="round"';
const s = 'stroke="#141414" stroke-width="5" stroke-linejoin="round" stroke-linecap="round"';
const SKIN = '#f6c9a0';

function chambre() {
  let stripes = '';
  for (let x = 0; x < 720; x += 48) stripes += `<rect x="${x}" y="0" width="24" height="1050" fill="#3b2457"/>`;
  return `
  <rect width="720" height="1280" fill="#2f1c47"/>${stripes}
  <!-- fenêtre volets fermés -->
  <rect x="440" y="230" width="230" height="300" fill="#5a3b2a" ${S}/>
  ${[0,1,2,3,4,5,6,7].map(i=>`<line x1="445" y1="${262+i*34}" x2="665" y2="${262+i*34}" stroke="#3a2418" stroke-width="6"/>`).join('')}
  <line x1="555" y1="230" x2="555" y2="530" ${s}/>
  <!-- poster -->
  <rect x="40" y="250" width="170" height="220" rx="6" fill="#e84f8a" ${S} transform="rotate(-6 125 360)"/>
  <circle cx="125" cy="340" r="45" fill="#ffd23f" ${s} transform="rotate(-6 125 360)"/>
  <text x="125" y="440" font-family="Anton" font-size="34" fill="#fff" text-anchor="middle" transform="rotate(-6 125 360)">K-DRAMA</text>
  <!-- calendrier -->
  <rect x="40" y="560" width="160" height="150" rx="8" fill="#fff" ${S}/>
  <rect x="40" y="560" width="160" height="40" rx="8" fill="#e23b3b" ${s}/>
  <text x="120" y="590" font-family="Anton" font-size="24" fill="#fff" text-anchor="middle">NOVEMBRE</text>
  <text x="150" y="690" font-family="Anton" font-size="46" fill="#e23b3b" text-anchor="middle">30</text>
  <circle cx="150" cy="670" r="34" fill="none" stroke="#e23b3b" stroke-width="5"/>
  <!-- sol -->
  <rect x="0" y="1050" width="720" height="230" fill="#4a3426"/>
  ${[0,1,2,3].map(i=>`<line x1="0" y1="${1100+i*50}" x2="720" y2="${1100+i*50}" stroke="#3a281c" stroke-width="5"/>`).join('')}
  <!-- lit -->
  <rect x="-20" y="900" width="230" height="160" rx="14" fill="#7a5fb0" ${S}/>
  <path d="M-20 900 q60 -50 120 -10 q60 -40 110 10 z" fill="#c9b6ef" ${S}/>
  <!-- plante morte -->
  <path d="M610 960 l-10 -90 M610 960 l20 -70 M603 910 q-30 -10 -40 10 M620 900 q30 -5 35 20" fill="none" stroke="#7b5a2a" stroke-width="6" stroke-linecap="round"/>
  <path d="M575 960 h75 l-10 80 h-55 z" fill="#c4623a" ${S}/>
  <!-- linge -->
  <path d="M470 1100 q40 -60 100 -40 q50 -40 110 10 q30 40 0 70 h-200 q-30 -10 -10 -40z" fill="#5fa8d3" ${S}/>
  <path d="M520 1080 q30 -30 60 0" fill="none" ${s}/>
  <rect x="560" y="1060" width="60" height="30" rx="6" fill="#ffd23f" ${s} transform="rotate(-12 590 1075)"/>
  <!-- boîtes de pizza -->
  ${[0,1,2].map(i=>`<rect x="${30+i*6}" y="${1150-i*28}" width="190" height="28" fill="#e9c28f" ${s}/>`).join('')}
  <text x="128" y="1124" font-family="Anton" font-size="20" fill="#b5462b" text-anchor="middle">PIZZA</text>`;
}

function odeurs() {
  const w = (x,y)=>`<path d="M${x} ${y} q15 -20 0 -40 q-15 -20 0 -40 q15 -20 0 -40" fill="none" stroke="#8fd16a" stroke-width="5" stroke-linecap="round" opacity=".85"/>`;
  return w(150,560)+w(590,640)+w(250,980)+w(520,450)+w(660,880);
}

function lana(expr='blase') {
  // corps / pyjama licorne
  const body = `
  <path d="M215 1280 L235 905 Q250 830 360 825 Q470 830 485 905 L505 1280 Z" fill="#f7a8c8" ${S}/>
  <path d="M215 1000 q-50 40 -40 140 q10 30 40 25 z" fill="#f7a8c8" ${S}/>
  <path d="M505 1000 q50 40 40 140 q-10 30 -40 25 z" fill="#f7a8c8" ${S}/>
  <circle cx="200" cy="1170" r="26" fill="${SKIN}" ${s}/>
  <circle cx="520" cy="1170" r="26" fill="${SKIN}" ${s}/>
  <!-- licorne sur le pyjama -->
  <circle cx="360" cy="1010" r="48" fill="#fff" ${s}/>
  <path d="M345 965 l15 -45 l15 45 z" fill="#ffd23f" ${s}/>
  <circle cx="345" cy="1005" r="6" fill="#141414"/><circle cx="378" cy="1005" r="6" fill="#141414"/>
  <path d="M345 1030 q15 12 30 0" fill="none" ${s}/>
  <!-- taches -->
  <ellipse cx="290" cy="940" rx="16" ry="11" fill="#c9733a" opacity=".8"/>
  <ellipse cx="430" cy="1090" rx="20" ry="13" fill="#c9733a" opacity=".8"/>
  <circle cx="300" cy="1120" r="9" fill="#e23b3b" opacity=".8"/>
  <circle cx="455" cy="960" r="7" fill="#ffd23f"/>
  <!-- texte -->
  <text x="360" y="1210" font-family="Anton" font-size="62" fill="#3ec1ff" stroke="#141414" stroke-width="5" paint-order="stroke" text-anchor="middle">LANA</text>`;
  // tête
  const eyes = expr==='choc'
    ? `<circle cx="305" cy="660" r="26" fill="#fff" ${s}/><circle cx="420" cy="660" r="26" fill="#fff" ${s}/>
       <circle cx="305" cy="662" r="9" fill="#141414"/><circle cx="420" cy="662" r="9" fill="#141414"/>`
    : `<circle cx="305" cy="665" r="24" fill="#fff" ${s}/><circle cx="420" cy="665" r="24" fill="#fff" ${s}/>
       <circle cx="308" cy="672" r="9" fill="#141414"/><circle cx="418" cy="672" r="9" fill="#141414"/>
       <path d="M281 662 q24 -10 48 0 v-18 h-48z" fill="${SKIN}" ${s}/><path d="M396 662 q24 -10 48 0 v-18 h-48z" fill="${SKIN}" ${s}/>`;
  const mouth = expr==='choc'
    ? `<ellipse cx="362" cy="770" rx="22" ry="28" fill="#7a1f2b" ${s}/>`
    : `<path d="M335 772 q28 -14 56 4" fill="none" ${s}/>`;
  return body + `
  <!-- cou -->
  <rect x="330" y="790" width="60" height="50" fill="${SKIN}" ${s}/>
  <!-- chignon nid d'oiseau -->
  <circle cx="360" cy="455" r="70" fill="#6b3f22" ${S}/>
  <path d="M310 430 q30 -40 80 -10 M320 470 q40 20 80 -20 M340 410 q10 50 50 60" fill="none" stroke="#3d2412" stroke-width="5"/>
  <path d="M300 420 l-40 -30 M420 420 l40 -40 M360 385 l5 -40" stroke="#6b3f22" stroke-width="8" stroke-linecap="round"/>
  <!-- crayon planté dans le chignon -->
  <rect x="395" y="360" width="16" height="110" fill="#ffd23f" ${s} transform="rotate(30 403 415)"/>
  <!-- cheveux arrière -->
  <path d="M215 640 Q220 500 360 495 Q500 500 505 640 L510 760 L210 760 Z" fill="#6b3f22" ${S}/>
  <!-- visage -->
  <ellipse cx="360" cy="680" rx="140" ry="150" fill="${SKIN}" ${S}/>
  <!-- mèches -->
  <path d="M225 610 Q270 520 360 530 Q450 520 495 610 Q440 560 400 590 Q370 550 330 585 Q280 560 225 610 Z" fill="#6b3f22" ${S}/>
  <path d="M240 600 q-20 80 -5 130" fill="none" stroke="#6b3f22" stroke-width="10" stroke-linecap="round"/>
  <path d="M485 600 q25 70 10 140" fill="none" stroke="#6b3f22" stroke-width="10" stroke-linecap="round"/>
  <!-- sourcils très épais -->
  <path d="M270 618 q35 -28 75 -8 l-4 18 q-35 -14 -68 6 z" fill="#3d2412" ${s}/>
  <path d="M380 610 q40 -20 75 8 l-4 16 q-33 -18 -68 -6 z" fill="#3d2412" ${s}/>
  ${[0,1,2,3,4].map(i=>`<line x1="${280+i*12}" y1="${612-i*2}" x2="${276+i*12}" y2="${598-i*2}" stroke="#3d2412" stroke-width="4"/>`).join('')}
  ${eyes}
  <!-- cernes -->
  <path d="M285 698 q20 12 42 0 M400 698 q20 12 42 0" fill="none" stroke="#b77a6a" stroke-width="5"/>
  <!-- lunettes de travers -->
  <g transform="rotate(-7 362 665)">
    <circle cx="305" cy="665" r="42" fill="none" stroke="#141414" stroke-width="8"/>
    <circle cx="420" cy="665" r="42" fill="none" stroke="#141414" stroke-width="8"/>
    <line x1="347" y1="665" x2="378" y2="665" stroke="#141414" stroke-width="8"/>
    <rect x="352" y="656" width="22" height="18" fill="#fff" ${s}/>
  </g>
  <!-- nez -->
  <path d="M362 690 q-12 30 4 38" fill="none" ${s}/>
  ${mouth}
  <!-- bouton + goutte -->
  <circle cx="260" cy="735" r="8" fill="#e23b3b" ${s}/><circle cx="455" cy="575" r="6" fill="#e23b3b" ${s}/>
  <path d="M470 610 q-10 18 0 26 q10 -8 0 -26z" fill="#7fd0ff" ${s}/>`;
}

function chat(x=560,y=1000,sc=1) {
  return `<g transform="translate(${x} ${y}) scale(${sc})">
  <ellipse cx="0" cy="60" rx="85" ry="70" fill="#f08a2c" ${S}/>
  <circle cx="0" cy="-30" r="62" fill="#f08a2c" ${S}/>
  <path d="M-55 -60 l5 -55 l40 30 z M55 -60 l-5 -55 l-40 30 z" fill="#f08a2c" ${S}/>
  <path d="M-30 -45 q15 8 25 0 M5 -45 q15 8 25 0" fill="none" stroke="#141414" stroke-width="6"/>
  <circle cx="-18" cy="-35" r="6" fill="#141414"/><circle cx="18" cy="-35" r="6" fill="#141414"/>
  <path d="M-8 -12 l8 8 l8 -8z" fill="#e8708f" ${s}/>
  <path d="M-14 8 q14 -10 28 0" fill="none" ${s}/>
  <path d="M-40 -10 h-40 M-40 0 h-38 M40 -10 h40 M40 0 h38" stroke="#141414" stroke-width="3"/>
  <path d="M-60 20 q10 15 0 30 M60 30 q-10 15 0 30" fill="none" stroke="#c76a1a" stroke-width="6"/>
  </g>`;
}

function hud(jours=30, glow=0) {
  return `
  <rect x="70" y="110" width="200" height="90" rx="14" fill="#141414" stroke="#2c2c2c" stroke-width="4"/>
  <text x="170" y="142" font-family="Anton" font-size="22" fill="#fff" text-anchor="middle">JOURS RESTANTS</text>
  <text x="170" y="190" font-family="Anton" font-size="46" fill="#ffd23f" text-anchor="middle">${jours}</text>
  <rect x="450" y="110" width="200" height="90" rx="14" fill="#141414" stroke="#2c2c2c" stroke-width="4"/>
  <text x="550" y="142" font-family="Anton" font-size="22" fill="#fff" text-anchor="middle">GLOW-UP</text>
  <text x="550" y="190" font-family="Anton" font-size="46" fill="#5fd35a" text-anchor="middle">${glow}%</text>`;
}

const t = (y, parts, size=118) => `<text x="360" y="${y}" font-family="Anton" font-size="${size}" text-anchor="middle" stroke="#141414" stroke-width="16" paint-order="stroke">${parts.map(([txt,c])=>`<tspan fill="${c}">${txt}</tspan>`).join('')}</text>`;
const bandeau = (txt, y=1110) => `<rect x="70" y="${y}" width="580" height="80" rx="18" fill="#141414" stroke="#ffd23f" stroke-width="4"/>
  <text x="360" y="${y+53}" font-family="Anton" font-size="36" fill="#fff" text-anchor="middle">${txt}</text>`;

const scenes = {
  'plan03-lana-chambre': () => chambre() + odeurs() + lana('blase') + hud(30,0),
  'plan05-lana-choc': () => chambre() + odeurs() + lana('choc') + hud(30,0) + `
     <g transform="translate(560 830) rotate(12)"><rect x="-70" y="-120" width="140" height="240" rx="18" fill="#141414" ${S}/>
     <rect x="-58" y="-100" width="116" height="190" rx="6" fill="#fff"/>
     <text x="0" y="-55" font-family="Anton" font-size="20" fill="#141414" text-anchor="middle">INÈS 🎉</text>
     <text x="0" y="-15" font-family="Anton" font-size="17" fill="#141414" text-anchor="middle">LES 10 ANS</text>
     <text x="0" y="10" font-family="Anton" font-size="17" fill="#141414" text-anchor="middle">DU LYCÉE</text>
     <text x="0" y="35" font-family="Anton" font-size="17" fill="#141414" text-anchor="middle">DANS 30 JOURS</text>
     <text x="0" y="68" font-family="Anton" font-size="18" fill="#e23b3b" text-anchor="middle">NATHAN VIENT ❤</text></g>`,
  'plan04-pates': () => chambre() + odeurs() + chat(360,820,2.1) + hud(30,0),
  'couverture-ep01': () => chambre() + odeurs() + `<g transform="translate(0 120)">${lana('blase')}</g>` +
     t(150,[['30 JOURS','#ffd23f']]) + t(280,[['POUR TOUT','#fff']]) + t(410,[['CHANGER','#e23b3b']]) + bandeau('JOUR 1 · À TOI DE CHOISIR'),
};

module.exports = { scenes };

if (require.main === module) {
  const { chromium } = require('playwright');
  const out = process.argv[2];
  (async () => {
    const b = await chromium.launch();
    const p = await b.newPage({ viewport: { width: 720, height: 1280 } });
    for (const [name, fn] of Object.entries(scenes)) {
      const html = `<html><head><link href="https://fonts.googleapis.com/css2?family=Anton&display=block" rel="stylesheet"><style>body{margin:0}</style></head>
      <body><svg xmlns="http://www.w3.org/2000/svg" width="720" height="1280" viewBox="0 0 720 1280">${fn()}</svg></body></html>`;
      await p.setContent(html, { waitUntil: 'networkidle' });
      await p.evaluate(() => document.fonts.ready);
      await p.screenshot({ path: `${out}/${name}.png` });
      console.log('ok', name);
    }
    await b.close();
  })();
}
