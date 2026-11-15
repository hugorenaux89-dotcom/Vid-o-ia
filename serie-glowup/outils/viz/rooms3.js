// Décors supplémentaires pour les épisodes 4 à 30
const { ROOMS2, calendar, shell, glow, lg } = require('./rooms2');
const K = '#1f1a17';
const O = (w = 5) => `stroke="${K}" stroke-width="${w}" stroke-linejoin="round" stroke-linecap="round"`;
const T = (x, y, s, txt, fill = '#fff', anchor = 'middle') => `<text x="${x}" y="${y}" font-family="Lilita One" font-size="${s}" text-anchor="${anchor}" fill="${fill}">${txt}</text>`;
const chairBig = (x, y, col) => `<g transform="translate(${x},${y})"><rect x="-150" y="-420" width="300" height="300" rx="50" fill="${col}" ${O(7)}/><rect x="-170" y="-140" width="340" height="80" rx="30" fill="${col}" ${O(7)}/><rect x="-200" y="-200" width="50" height="40" rx="12" fill="#333" ${O(4)}/><rect x="150" y="-200" width="50" height="40" rx="12" fill="#333" ${O(4)}/><rect x="-14" y="-60" width="28" height="120" fill="#888" ${O(4)}/><ellipse cx="0" cy="66" rx="140" ry="22" fill="#666" ${O(5)}/></g>`;
Object.assign(ROOMS2, {
  chambreJour: (o = {}) => ROOMS2.chambreNuit(o).replace('fill="#0b1433"', 'fill="#9fd4ff"').replace(/<rect width="1080" height="1920" fill="#040818" opacity=".16"\/>/, '<rect width="1080" height="1920" fill="#fff6d0" opacity=".12"/>'),
  barbier: () => `${shell(['#2b2b2b', '#1c1c1c'], '#151515', '#e8e8e8', '#9a9a9a', false)}
    ${[...Array(10)].map((_, i) => [...Array(7)].map((_, j) => `<rect x="${(i * 120 + (j % 2) * 60) - 60}" y="${1250 + j * 100}" width="60" height="100" fill="${(i + j) % 2 ? '#222' : '#eee'}" opacity=".9"/>`).join('')).join('')}
    <rect x="160" y="200" width="760" height="560" rx="20" fill="#bfe4ff" stroke="#c9a23a" stroke-width="16"/><path d="M220 260 L320 200 M240 360 L460 210" stroke="#fff" stroke-width="14" opacity=".5"/>
    ${T(540, 160, 90, 'CHEZ MOUSSA', '#e2b73a')}
    <rect x="140" y="780" width="800" height="40" fill="#6e4528" ${O(5)}/>${[0, 1, 2, 3, 4].map(i => `<rect x="${200 + i * 140}" y="${700 + (i % 2) * 10}" width="50" height="${80 - (i % 2) * 10}" rx="10" fill="${['#3ec5ff', '#e5483f', '#ffd23a', '#5bbf4a', '#fff'][i]}" ${O(4)}/>`).join('')}
    <g transform="translate(70,300)"><rect x="-26" y="0" width="52" height="420" rx="26" fill="#fff" ${O(5)}/>${[0, 1, 2, 3, 4, 5].map(i => `<path d="M-26 ${40 + i * 64} L26 ${10 + i * 64}" stroke="#e5483f" stroke-width="18"/><path d="M-26 ${70 + i * 64} L26 ${40 + i * 64}" stroke="#2f6fd6" stroke-width="12"/>`).join('')}</g>
    <defs>${glow('gbb', 540, 400, 900, '#ffe9b0', 0.3)}</defs><rect width="1080" height="1920" fill="url(#gbb)"/>`,
  opticien: () => `${shell(['#f5f5f0', '#e3e3da'], '#d6d6cc', '#d9d0c0', '#b0a690', true)}
    ${T(540, 190, 92, 'OPTIQUE', '#2f6fd6')}
    ${[0, 1, 2].map(r => `<rect x="160" y="${260 + r * 190}" width="760" height="20" fill="#bba889" ${O(4)}/>` + [0, 1, 2, 3, 4].map(i => `<g transform="translate(${230 + i * 150},${250 + r * 190})"><rect x="-56" y="-46" width="50" height="36" rx="10" fill="none" stroke="${['#222', '#9a1d2a', '#2f6fd6', '#6e4528', '#222'][(i + r) % 5]}" stroke-width="7"/><rect x="6" y="-46" width="50" height="36" rx="10" fill="none" stroke="${['#222', '#9a1d2a', '#2f6fd6', '#6e4528', '#222'][(i + r) % 5]}" stroke-width="7"/></g>`).join('')).join('')}
    <g transform="translate(860,900)"><rect x="-90" y="-140" width="180" height="300" fill="#fff" ${O(5)}/>${['E', 'F P', 'T O Z', 'L P E D'].map((l, i) => T(0, -80 + i * 64, 60 - i * 10, l, '#111')).join('')}</g>
    <defs>${glow('go', 540, 300, 900, '#ffffff', 0.35)}</defs><rect width="1080" height="1920" fill="url(#go)"/>`,
  dentiste: () => `${shell(['#e4f6f8', '#c8ecef'], '#b8e0e4', '#eef4f5', '#c2d0d3', false)}
    ${T(540, 190, 80, 'CABINET DENTAIRE', '#2a8a9a')}
    <g transform="translate(860,520)"><path d="M-80 -120 Q-100 -200 -40 -200 Q0 -180 40 -200 Q100 -200 80 -120 Q70 0 40 60 Q20 0 0 0 Q-20 0 -40 60 Q-70 0 -80 -120 Z" fill="#fff" ${O(6)}/><path d="M-40 -110 q20 30 60 0" fill="none" ${O(5)}/><circle cx="-26" cy="-140" r="8" fill="#111"/><circle cx="26" cy="-140" r="8" fill="#111"/></g>
    <g transform="translate(300,340)"><path d="M0 0 L0 200 M-60 0 L60 0" ${O(8)}/><ellipse cx="0" cy="230" rx="110" ry="50" fill="#fffbe0" ${O(6)}/><ellipse cx="0" cy="230" rx="80" ry="34" fill="#fff" opacity=".9"/></g>
    <rect x="150" y="1000" width="300" height="200" rx="16" fill="#fff" ${O(5)}/><rect x="170" y="1020" width="260" height="20" fill="#2a8a9a"/>
    <defs>${glow('gd', 300, 570, 600, '#fffbe0', 0.5)}</defs><rect width="1080" height="1920" fill="url(#gd)"/>`,
  medecin: () => `${shell(['#eef8f4', '#d4efe6'], '#c4e4da', '#f2f2f2', '#c8cccc', false)}
    ${[...Array(9)].map((_, i) => `<path d="M${120 + i * 105} 1250 L${-300 + i * 210} 1920" stroke="#d8dddd" stroke-width="4"/>`).join('')}
    ${T(540, 190, 84, 'DOCTEUR ROUSSEAU', '#2a8a6a')}
    <rect x="170" y="300" width="300" height="400" fill="#fff" ${O(6)}/>${T(320, 360, 40, 'CHEVEUX', '#2a8a6a')}<circle cx="320" cy="500" r="100" fill="#f3d2b0" ${O(5)}/>${[...Array(7)].map((_, i) => `<path d="M${250 + i * 24} 430 q6 -50 12 -70" fill="none" stroke="#1c1511" stroke-width="7"/>`).join('')}
    <rect x="610" y="300" width="300" height="300" fill="#9fd4ff" ${O(8)}/><path d="M760 300 L760 600 M610 450 L910 450" ${O(7)}/>
    <rect x="560" y="1000" width="420" height="80" rx="20" fill="#bfe4d8" ${O(6)}/><rect x="560" y="990" width="420" height="30" rx="12" fill="#fff" ${O(4)}/><rect x="600" y="1080" width="24" height="170" fill="#888"/><rect x="920" y="1080" width="24" height="170" fill="#888"/>
    <defs>${glow('gm3', 540, 300, 900, '#ffffff', 0.4)}</defs><rect width="1080" height="1920" fill="url(#gm3)"/>`,
  magasin: () => `${shell(['#f4ece2', '#e6d8c6'], '#d8c6b0', '#c9b49a', '#9a8468', true)}
    ${T(540, 190, 92, 'BOUTIQUE', '#141414')}
    ${[0, 1].map(r => `<path d="M140 ${300 + r * 380} L940 ${300 + r * 380}" ${O(10)}/>` + [...Array(9)].map((_, i) => `<g transform="translate(${190 + i * 88},${300 + r * 380})"><path d="M0 0 l0 20" ${O(4)}/><path d="M-36 30 L-14 20 L14 20 L36 30 L30 60 L22 56 L22 230 L-22 230 L-22 56 L-30 60 Z" fill="${['#22325a', '#f4f4f4', '#1d1d22', '#d8c3a0', '#9a1d2a', '#23345e', '#5bbf4a', '#f4f4f4', '#3e4a66'][(i + r * 3) % 9]}" ${O(4)}/></g>`).join('')).join('')}
    <rect x="780" y="1000" width="200" height="250" fill="#6e4528" ${O(5)}/><rect x="760" y="980" width="240" height="30" fill="#8a5a36" ${O(5)}/>
    <g transform="translate(250,1240)"><rect x="-70" y="-560" width="140" height="560" rx="70" fill="#bfe4ff" stroke="#c9a23a" stroke-width="10"/></g>
    <defs>${glow('gs2', 540, 300, 900, '#fff4d0', 0.4)}</defs><rect width="1080" height="1920" fill="url(#gs2)"/>`,
  studioDanse: () => `${shell(['#3a1d5e', '#251240'], '#1d0e33', '#c9a06a', '#8a6638', true)}
    <rect x="140" y="220" width="800" height="760" fill="#bfe4ff" opacity=".35" ${O(5)}/>${[0, 1, 2, 3].map(i => `<path d="M${140 + i * 200} 220 L${140 + i * 200} 980" stroke="#fff" stroke-opacity=".3" stroke-width="4"/>`).join('')}
    <rect x="140" y="900" width="800" height="16" fill="#c9a23a"/>${T(540, 170, 90, 'DANSE STUDIO', '#ff6bd8')}
    ${[...Array(12)].map((_, i) => `<circle cx="${100 + i * 80}" cy="${60 + (i % 3) * 20}" r="12" fill="${['#ff6bd8', '#4fe1ff', '#ffe14f'][i % 3]}"/>`).join('')}
    <defs>${glow('gds', 540, 900, 900, '#ff6bd8', 0.35)}</defs><rect width="1080" height="1920" fill="url(#gds)"/>`,
  garage: () => `${shell(['#5a6470', '#454d57'], '#3a414a', '#6a6a6a', '#3a3a3a', false)}
    ${T(540, 190, 90, 'GARAGE AUTO', '#ffd23a')}
    <rect x="160" y="260" width="760" height="300" fill="#2f353d" ${O(5)}/>${[...Array(12)].map((_, i) => `<path d="M${200 + i * 60} 300 l0 ${80 + (i % 3) * 40}" stroke="#9aa4ae" stroke-width="10" stroke-linecap="round"/>`).join('')}
    <g transform="translate(540,1180)"><path d="M-380 0 Q-370 -120 -250 -140 L-150 -230 L150 -230 L260 -140 Q380 -120 380 0 Z" fill="#e5483f" ${O(7)}/><path d="M-130 -210 L-60 -150 L60 -150 L130 -210 Z" fill="#9fd4ff" ${O(5)}/><circle cx="-230" cy="10" r="70" fill="#222" ${O(6)}/><circle cx="230" cy="10" r="70" fill="#222" ${O(6)}/><circle cx="-230" cy="10" r="26" fill="#aaa"/><circle cx="230" cy="10" r="26" fill="#aaa"/></g>
    <ellipse cx="300" cy="1500" rx="160" ry="30" fill="#111" opacity=".5"/>
    <defs>${glow('gg', 540, 200, 900, '#fff', 0.25)}</defs><rect width="1080" height="1920" fill="url(#gg)"/>`,
  mariage: () => `<defs>${lg('wm', '#fff2e0', '#f2d9b8')}${lg('wf', '#d8b98a', '#a8865a')}</defs><rect width="1080" height="1920" fill="url(#wm)"/>
    ${[...Array(9)].map((_, i) => `<rect x="${i * 130 - 20}" y="0" width="60" height="1250" fill="#fff" opacity=".35"/>`).join('')}
    <path d="M0 140 Q270 260 540 140 Q810 260 1080 140" fill="none" stroke="#fff" stroke-width="18"/>${[...Array(16)].map((_, i) => `<circle cx="${30 + i * 68}" cy="${170 + 50 * Math.sin(i / 15 * Math.PI * 2)}" r="12" fill="#ffe9a0"/>`).join('')}
    <path d="M300 1250 L300 520 Q540 300 780 520 L780 1250" fill="none" stroke="#fff" stroke-width="30"/>${[...Array(10)].map((_, i) => `<circle cx="${300 + 480 * (i / 9)}" cy="${520 - 200 * Math.sin(i / 9 * Math.PI)}" r="34" fill="${i % 2 ? '#ff9ec2' : '#fff'}" ${O(4)}/>`).join('')}
    ${T(540, 470, 64, 'BILAL &amp; YASMINE', '#c9a23a')}
    <rect x="0" y="1250" width="1080" height="670" fill="url(#wf)"/>
    ${[160, 920].map(x => `<g transform="translate(${x},1200)"><ellipse cx="0" cy="0" rx="140" ry="30" fill="#fff" ${O(5)}/><rect x="-10" y="0" width="20" height="120" fill="#ddd"/><path d="M-20 -10 L0 -110 L20 -10 Z" fill="#fff" ${O(4)}/><circle cx="0" cy="-120" r="10" fill="#ffd23a"/></g>`).join('')}
    <path d="M440 1250 L640 1250 L760 1920 L320 1920 Z" fill="#c0392b" opacity=".85"/>
    <defs>${glow('gw2', 540, 600, 1000, '#fff3c0', 0.4)}</defs><rect width="1080" height="1920" fill="url(#gw2)"/>`,
});
module.exports = { ROOMS2 };
