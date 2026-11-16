// Tous les personnages en style « BD gros plan » (contours épais, à plat). viewBox personnage : 0 0 600 720
const K = '#141414';
const E = {
  neutre:    { brow: [262, 258], eyes: 'open', mouth: 'neutral' },
  panique:   { brow: [252, 236], eyes: 'wide', mouth: 'scream', sweat: 3 },
  choque:    { brow: [240, 234], eyes: 'wide', mouth: 'o', sweat: 1 },
  colere:    { brow: [250, 284], eyes: 'squeeze', mouth: 'shout', vein: true },
  triste:    { brow: [270, 246], eyes: 'sad', mouth: 'sad' },
  larmes:    { brow: [272, 244], eyes: 'cry', mouth: 'cry', tears: true },
  sourire:   { brow: [256, 252], eyes: 'happy', mouth: 'grin' },
  determine: { brow: [258, 276], eyes: 'half', mouth: 'tight' },
  mefiant:   { brow: [252, 262], brow2: [272, 280], eyes: 'sus', mouth: 'smirk' },
  tendre:    { brow: [260, 252], eyes: 'soft', mouth: 'soft', blush: true },
  inquiet:   { brow: [264, 244], eyes: 'open', mouth: 'wavy', sweat: 1 },
  calme:     { brow: [262, 260], eyes: 'half', mouth: 'smirk' },
};

const C = {
  YANIS:   { skin: '#c98e62', hair: 'fade', hc: '#1c1511', beard: 'stubble', outfit: 'hoodie', chain: 'silver', w: 1.12 },
  VIDAL:   { skin: '#ecc19c', hair: 'slick', hc: '#b9b9b9', beard: 'none', outfit: 'suit', age: true, w: 1.04, brow: '#8a8a8a' },
  SOFIANE: { skin: '#d29a6a', hair: 'cap', hc: '#151515', beard: 'none', outfit: 'tracksuit', earring: true, w: 1.0 },
  LINA:    { skin: '#a8693f', hair: 'bun', hc: '#24170f', beard: 'none', outfit: 'apron', glasses: 'round', fem: true, w: 0.98 },
  NADIA:   { skin: '#c08a60', hair: 'scarf', hc: '#e3cfae', beard: 'none', outfit: 'cardigan', fem: true, age: true, w: 1.06 },
  GERARD:  { skin: '#f1c09b', hair: 'balding', hc: '#c8c8c8', beard: 'moustache', outfit: 'overallsG', glasses: 'forehead', age: true, w: 1.2, brow: '#9a9a9a' },
  BRUNO:   { skin: '#e0a882', hair: 'shaved', hc: '#141414', beard: 'full', outfit: 'bomber', w: 1.22 },
  KARIM:   { skin: '#c38c60', hair: 'short', hc: '#120d0a', beard: 'trimmed', outfit: 'whiteTrack', chain: 'gold', w: 1.08 },
  INES:    { skin: '#f6d0b2', hair: 'long', hc: '#f0d48a', beard: 'none', outfit: 'pinkTrack', glasses: 'sunHead', fem: true, w: 0.98 },
  BERNARD: { skin: '#f3c9a8', hair: 'flatcap', hc: '#f4f4f4', beard: 'none', outfit: 'corduroy', age: true, w: 1.05, brow: '#d0d0d0' },
  MALIK:   { skin: '#c48a5e', hair: 'fade', hc: '#4a4440', beard: 'stubble', outfit: 'overallsM', age: true, w: 1.12 },
  POLICIER:{ skin: '#e8b994', hair: 'police', hc: '#3a2a20', beard: 'none', outfit: 'police', w: 1.08 },
  GRIS:    { skin: '#efc6a6', hair: 'balding', hc: '#6a5a50', beard: 'none', outfit: 'greysuit', glasses: 'round', age: true, w: 1.05 },
  YANIS_J1:{ skin: '#c98e62', hair: 'messy', hc: '#1c1511', beard: 'patchy', outfit: 'hoodieDirty', chain: 'silver', w: 1.26, pimples: true, unibrow: true, chin: true },
  YANIS_A: { skin: '#c98e62', hair: 'bald', hc: '#1c1511', beard: 'cuts', outfit: 'hoodieDirty', w: 1.42, pimples: true, unibrow: true, chin: true, glasses: 'broken', teeth: 'dirty', jowls: true },
  YANIS_B: { skin: '#c98e62', hair: 'thick', hc: '#1c1511', beard: 'patchy', outfit: 'hoodie', w: 1.3, chin: true, glasses: 'rect', teeth: 'ok', pimplesLight: true },
  YANIS_C: { skin: '#c98e62', hair: 'fade', hc: '#1c1511', beard: 'trimmed', outfit: 'hoodie', w: 1.14, glasses: 'rect' },
  YANIS_D: { skin: '#c98e62', hair: 'fade', hc: '#1c1511', beard: 'trimmed', outfit: 'hoodie', w: 1.06, glasses: 'thin' },
  YANIS_E: { skin: '#c98e62', hair: 'fade', hc: '#1c1511', beard: 'trimmed', outfit: 'hoodie', w: 1.04, glasses: 'thin' },
  SARAH:   { skin: '#ebb68d', hair: 'long', hc: '#3a2216', beard: 'none', outfit: 'cropBeige', fem: true, hoops: true, w: 0.97 },
  KENZO:   { skin: '#e2a77a', hair: 'short', hc: '#ecd27c', beard: 'none', outfit: 'coach', chain: 'gold', w: 1.14, brow: '#b8963f' },
  BILAL:   { skin: '#c7905f', hair: 'short', hc: '#141010', beard: 'trimmed', outfit: 'whiteShirt', w: 1.08 },
  MOUSSA:  { skin: '#6b4329', hair: 'shaved', hc: '#0d0a08', beard: 'trimmed', outfit: 'barber', w: 1.1 },
  ACHETEUR:{ skin: '#ddA27c', hair: 'capFront', hc: '#222', beard: 'trimmed', outfit: 'bomber', glasses: 'sun', w: 1.1 },
};

function shade(hex, f) {
  const n = parseInt(hex.slice(1), 16);
  const ch = s => Math.max(0, Math.min(255, Math.round(((n >> s) & 255) * (1 + f))));
  return '#' + [16, 8, 0].map(s => ch(s).toString(16).padStart(2, '0')).join('');
}
const S = (w = 8) => `stroke="${K}" stroke-width="${w}" stroke-linejoin="round" stroke-linecap="round"`;

function brows(e, col, fem) {
  const [a, b] = e.brow, [c, d] = e.brow2 || e.brow, t = fem ? 12 : 18;
  return `<path d="M196 ${a} L282 ${b} L284 ${b + t + 2} L198 ${a + t} Z" fill="${col}" ${S(4)}/>
          <path d="M318 ${d} L404 ${c} L402 ${c + t} L316 ${d + t + 2} Z" fill="${col}" ${S(4)}/>`;
}

function eye(cx, kind, right, skin, fem) {
  const cy = 305;
  const iris = (r = 13, dy = 0) => `<circle cx="${cx}" cy="${cy + dy}" r="${r}" fill="#3b2314"/><circle cx="${cx}" cy="${cy + dy}" r="${r * 0.5}" fill="#0c0805"/><circle cx="${cx + 4}" cy="${cy + dy - 5}" r="4" fill="#fff"/>`;
  const white = (rx, ry) => `<ellipse cx="${cx}" cy="${cy}" rx="${rx}" ry="${ry}" fill="#fff" ${S(6)}/>`;
  const lash = fem ? `<path d="M${cx - 32} ${cy - 18} Q${cx} ${cy - 40} ${cx + 34} ${cy - 22}" fill="none" ${S(7)}/>` : '';
  const lid = (y2) => `<path d="M${cx - 33} ${cy - 2} L${cx + 33} ${y2} L${cx + 33} ${cy - 32} L${cx - 33} ${cy - 32} Z" fill="${skin}"/><path d="M${cx - 31} ${cy - 2} L${cx + 31} ${y2}" ${S(7)}/>`;
  switch (kind) {
    case 'shut': return `<path d="M${cx - 28} ${cy + 2} Q${cx} ${cy + 12} ${cx + 28} ${cy + 2}" fill="none" ${S(7)}/>`;
    case 'wide': return white(34, 34) + `<circle cx="${cx}" cy="${cy}" r="8" fill="#0c0805"/>`;
    case 'squeeze': return `<path d="${right ? `M${cx + 30} ${cy - 16} L${cx - 2} ${cy} L${cx + 30} ${cy + 16}` : `M${cx - 30} ${cy - 16} L${cx + 2} ${cy} L${cx - 30} ${cy + 16}`}" fill="none" ${S(8)}/>`;
    case 'happy': return `<path d="M${cx - 28} ${cy + 8} Q${cx} ${cy - 22} ${cx + 28} ${cy + 8}" fill="none" ${S(8)}/>`;
    case 'cry': return `<path d="M${cx - 28} ${cy - 4} Q${cx} ${cy + 18} ${cx + 28} ${cy - 4}" fill="none" ${S(8)}/>`;
    case 'half': return white(30, 22) + iris(12, 3) + lid(cy - 2) + lash;
    case 'sus': return right ? white(30, 22) + iris(12, 3) + lid(cy + 4) : white(30, 24) + iris(12, 2) + lash;
    case 'sad': return white(28, 24) + iris(12, 6) + `<path d="M${cx - 30} ${cy - 10} Q${cx} ${cy - 22} ${cx + 30} ${cy - 14}" fill="none" ${S(6)}/>`;
    case 'soft': return white(28, 20) + iris(11, 2) + `<path d="M${cx - 30} ${cy - 6} Q${cx} ${cy - 20} ${cx + 30} ${cy - 6}" fill="none" ${S(6)}/>`;
  }
  return white(30, 26) + iris() + lash;
}

function mouth(kind, talk, fem) {
  const dark = '#5a1515', tongue = '#e86a6a', T = S(7), lip = fem ? `fill="none" stroke="#a33a3a" stroke-width="8" stroke-linecap="round"` : `fill="none" ${T}`;
  if (talk && !['scream', 'shout', 'o', 'cry'].includes(kind)) kind = kind === 'grin' ? 'grinOpen' : 'talk';
  switch (kind) {
    case 'scream': return `<path d="M240 425 Q300 405 360 425 Q362 520 300 528 Q238 520 240 425 Z" fill="${dark}" ${T}/><path d="M252 430 Q300 418 348 430 L346 446 Q300 436 254 446 Z" fill="#fff"/><path d="M262 505 Q300 470 338 505 Q300 525 262 505 Z" fill="${tongue}"/>`;
    case 'shout': return `<path d="M235 420 Q300 400 365 420 Q350 505 300 512 Q250 505 235 420 Z" fill="${dark}" ${T}/><path d="M246 424 Q300 410 354 424 L351 440 Q300 428 249 440 Z" fill="#fff"/><path d="M262 488 Q300 455 340 488 Q300 508 262 488 Z" fill="${tongue}"/>`;
    case 'o': return `<ellipse cx="300" cy="455" rx="30" ry="40" fill="${dark}" ${T}/><path d="M282 478 Q300 464 318 478 Q300 492 282 478 Z" fill="${tongue}"/>`;
    case 'grin': return `<path d="M240 425 Q300 495 360 425 Q300 445 240 425 Z" fill="#fff" ${T}/><path d="M250 432 L350 432" stroke="${K}" stroke-width="4"/>`;
    case 'grinOpen': return `<path d="M240 422 Q300 510 360 422 Q300 440 240 422 Z" fill="${dark}" ${T}/><path d="M246 426 Q300 442 354 426 L350 440 Q300 452 250 440 Z" fill="#fff"/><path d="M275 478 Q300 462 325 478 Q300 492 275 478 Z" fill="${tongue}"/>`;
    case 'talk': return `<path d="M262 430 Q300 420 338 430 Q332 474 300 478 Q268 474 262 430 Z" fill="${dark}" ${T}/><path d="M270 433 Q300 426 330 433 L328 442 Q300 436 272 442 Z" fill="#fff"/>`;
    case 'sad': return `<path d="M262 456 Q300 426 338 456" ${lip}/>`;
    case 'cry': return `<path d="M252 455 Q300 410 348 455 Q300 470 252 455 Z" fill="${dark}" ${T}/><path d="M262 450 Q300 422 338 450" fill="none" stroke="#fff" stroke-width="6"/>`;
    case 'tight': return `<path d="M266 440 L334 438" ${lip}/>`;
    case 'smirk': return `<path d="M266 446 Q300 450 340 428" ${lip}/>`;
    case 'soft': return `<path d="M270 436 Q300 456 330 436" ${lip}/>`;
    case 'wavy': return `<path d="M262 448 Q278 432 294 446 Q310 460 326 444 Q332 440 338 444" ${lip}/>`;
  }
  return `<path d="M266 442 Q300 450 334 440" ${lip}/>`;
}

const defs = (id) => `<defs>
  <pattern id="stub${id}" width="14" height="14" patternUnits="userSpaceOnUse"><circle cx="3" cy="4" r="2.2" fill="#3a2a20" opacity=".55"/><circle cx="10" cy="10" r="2" fill="#3a2a20" opacity=".5"/></pattern>
  <pattern id="fade${id}" width="10" height="10" patternUnits="userSpaceOnUse"><circle cx="3" cy="3" r="2.4" fill="#2a211b" opacity=".75"/><circle cx="8" cy="8" r="2.2" fill="#2a211b" opacity=".6"/></pattern>
  <pattern id="dots${id}" width="26" height="26" patternUnits="userSpaceOnUse"><circle cx="8" cy="8" r="4" fill="#b8956a"/><circle cx="21" cy="20" r="3" fill="#b8956a"/></pattern>
</defs>`;

function body(c) {
  const sh = (fill, wide = 0) => `<path d="M${40 - wide} 720 C${50 - wide} 610 140 560 300 556 C460 560 ${550 + wide} 610 ${560 + wide} 720 Z" fill="${fill}" ${S()}/>`;
  const V = (fill, depth = 680) => `<path d="M250 570 L300 ${depth} L350 570 Z" fill="${fill}" ${S(6)}/>`;
  const tag = (t, col) => `<rect x="380" y="630" width="110" height="38" rx="6" fill="#fff" ${S(5)}/><text x="435" y="658" font-family="Anton" font-size="26" text-anchor="middle" fill="${col}">${t}</text>`;
  switch (c.outfit) {
    case 'hoodie': return sh('#8d9096') + `<path d="M150 600 C190 548 410 548 450 600 C400 585 200 585 150 600 Z" fill="#74777d" ${S()}/>
      <path d="M262 590 L254 680 M338 590 L346 680" stroke="#f2f2f2" stroke-width="9" stroke-linecap="round"/><circle cx="254" cy="686" r="8" fill="#f2f2f2" ${S(4)}/><circle cx="346" cy="686" r="8" fill="#f2f2f2" ${S(4)}/>
      <ellipse cx="130" cy="665" rx="22" ry="13" fill="#4a3424" opacity=".45"/><ellipse cx="470" cy="690" rx="16" ry="10" fill="#4a3424" opacity=".4"/>`;
    case 'suit': return sh('#22325a') + V('#fff') + `<path d="M250 570 L282 640 L262 720 M350 570 L318 640 L338 720" fill="none" ${S(6)}/><path d="M250 570 L300 680 L350 570" fill="none" ${S(6)}/>
      <path d="M140 660 l30 -6" stroke="#f2c230" stroke-width="8"/>`;
    case 'greysuit': return sh('#73777e') + V('#f4f4f4') + `<path d="M292 590 L308 590 L312 670 L300 690 L288 670 Z" fill="#9a1d2a" ${S(4)}/>`;
    case 'tracksuit': return sh('#161616') + `<path d="M90 660 L170 585 M510 660 L430 585" stroke="#f4f4f4" stroke-width="12"/><path d="M100 680 L180 605 M500 680 L420 605" stroke="#f4f4f4" stroke-width="12"/>
      <path d="M300 590 L300 720" stroke="#9a9a9a" stroke-width="6"/><path d="M250 575 Q300 600 350 575" fill="none" stroke="#333" stroke-width="16"/>`;
    case 'whiteTrack': return sh('#f2f2f2') + `<path d="M300 590 L300 720" stroke="#aaa" stroke-width="6"/><path d="M90 660 L170 585 M510 660 L430 585" stroke="#1a1a1a" stroke-width="10"/>`;
    case 'pinkTrack': return sh('#f58fbd') + `<path d="M300 590 L300 720" stroke="#d9649a" stroke-width="6"/><path d="M250 575 Q300 602 350 575" fill="none" stroke="#e477a8" stroke-width="16"/>`;
    case 'apron': return sh('#ffffff') + `<path d="M200 640 L400 640 L414 720 L186 720 Z" fill="#dcc29a" ${S(6)}/><path d="M220 640 L246 580 M380 640 L354 580" stroke="#c4a679" stroke-width="10"/>`;
    case 'cardigan': return sh('#dcc6a3') + `<path d="M252 572 L300 680 L348 572 Z" fill="#7a63a0" ${S(6)}/><circle cx="312" cy="700" r="7" fill="#8a7650" ${S(3)}/>`;
    case 'overallsG': return sh('#3e66aa') + `<path d="M256 572 L300 650 L344 572 Z" fill="#dedede" ${S(6)}/><path d="M220 575 L300 660 M380 575 L300 660" stroke="#2f4f86" stroke-width="14"/>` + tag('GÉRARD', '#2f5fa8');
    case 'overallsM': return sh('#2f5fa8') + `<path d="M256 572 L300 650 L344 572 Z" fill="#f2f2f2" ${S(6)}/><path d="M220 575 L300 660 M380 575 L300 660" stroke="#244b86" stroke-width="14"/>` + tag('MALIK', '#2f5fa8');
    case 'bomber': return sh('#1b1c20', 40) + `<path d="M240 572 Q300 600 360 572 L360 594 Q300 620 240 594 Z" fill="#2c2e33" ${S(5)}/><path d="M300 605 L300 720" stroke="#3a3c42" stroke-width="6"/>`;
    case 'police': return sh('#1f2d4a') + V('#a9c2e6', 650) + `<rect x="390" y="620" width="46" height="56" rx="8" fill="#d4af37" ${S(5)}/><rect x="90" y="590" width="90" height="18" fill="#2f3f5f" ${S(4)}/><rect x="420" y="590" width="90" height="18" fill="#2f3f5f" ${S(4)}/>`;
    case 'corduroy': return sh('#7d5434') + V('#ece4d0') + [130, 160, 190, 410, 440, 470].map(x => `<path d="M${x} 620 L${x - 14} 720" stroke="#664427" stroke-width="5"/>`).join('');
    case 'jacket': return sh('#18191c') + V('#ececec', 720);
    case 'hoodieDirty': return sh('#8d9096') + `<path d="M150 600 C190 548 410 548 450 600 C400 585 200 585 150 600 Z" fill="#74777d" ${S()}/>
      <path d="M262 590 L254 680 M338 590 L346 680" stroke="#e6e6e6" stroke-width="9" stroke-linecap="round"/>
      <ellipse cx="120" cy="665" rx="26" ry="15" fill="#4a3424" opacity=".5"/><ellipse cx="470" cy="690" rx="20" ry="12" fill="#4a3424" opacity=".45"/>
      <ellipse cx="300" cy="700" rx="14" ry="9" fill="#c98a3a" opacity=".55"/><ellipse cx="80" cy="700" rx="30" ry="24" fill="#5f6268" opacity=".7"/><ellipse cx="520" cy="700" rx="30" ry="24" fill="#5f6268" opacity=".7"/>
      ${[[200, 640], [380, 660], [340, 700], [230, 700]].map(([x, y]) => `<circle cx="${x}" cy="${y}" r="5" fill="#e0b050"/>`).join('')}`;
    case 'cropBeige': return sh('#ead8bc') + `<path d="M230 566 Q300 610 370 566" fill="none" stroke="#c9b08c" stroke-width="10"/>`;
    case 'coach': return sh('#151515', 30) + `<text x="300" y="690" font-family="Anton" font-size="62" text-anchor="middle" fill="#fff">COACH</text>`;
    case 'whiteShirt': return sh('#f4f4f4') + `<path d="M256 572 L300 640 L344 572" fill="none" ${S(6)}/><circle cx="300" cy="670" r="5" fill="#bbb"/><circle cx="300" cy="705" r="5" fill="#bbb"/>`;
    case 'barber': return sh('#1b1b1b') + `<path d="M210 600 L390 600 L410 720 L190 720 Z" fill="#2a2a2a" ${S(5)}/><text x="300" y="680" font-family="Anton" font-size="34" text-anchor="middle" fill="#d4af37">CHEZ MOUSSA</text>`;
  }
  return sh('#777');
}

function hairBack(c) {
  if (c.hair === 'long') return `<path d="M160 260 C140 120 220 54 302 54 C384 54 462 120 440 260 L470 640 L130 640 Z" fill="${c.hc}" ${S()}/>`;
  if (c.hair === 'scarf') return `<path d="M140 290 C130 120 210 52 300 52 C390 52 470 120 460 290 C468 420 430 520 470 600 L130 600 C170 520 132 420 140 290 Z" fill="${c.hc}" ${S()}/>
     ${[[180, 140], [420, 150], [160, 330], [440, 350], [300, 580], [210, 560], [390, 565]].map(([x, y]) => `<circle cx="${x}" cy="${y}" r="10" fill="#b8956a"/>`).join('')}`;
  if (c.hair === 'bun') return `<circle cx="300" cy="60" r="62" fill="${c.hc}" ${S()}/>` + [[262, 40], [306, 22], [344, 50], [272, 84], [330, 88]].map(([x, y]) => `<circle cx="${x}" cy="${y}" r="24" fill="${c.hc}" ${S(5)}/>`).join('');
  return '';
}

function hairFront(c, id) {
  const H = c.hc, SS = S();
  switch (c.hair) {
    case 'curly': return `<path d="M180 250 C182 210 186 190 196 176 L206 240 Z M420 250 C418 210 414 190 404 176 L394 240 Z" fill="url(#fade${id})"/>
      <path d="M182 210 C176 150 230 92 302 92 C374 92 428 150 418 210 C404 186 380 172 300 170 C220 172 196 186 182 210 Z" fill="${H}" ${SS}/>
      ${[[206, 150, 30], [244, 120, 34], [286, 104, 36], [330, 106, 35], [370, 124, 33], [400, 156, 28], [226, 178, 24], [266, 150, 30], [310, 140, 31], [352, 156, 28], [384, 184, 22], [300, 80, 26], [258, 84, 22], [344, 86, 22]].map(([x, y, r]) => `<circle cx="${x}" cy="${y}" r="${r}" fill="${H}" ${S(5)}/>`).join('')}
      ${[[206, 150, 30], [244, 120, 34], [286, 104, 36], [330, 106, 35], [370, 124, 33], [400, 156, 28], [266, 150, 30], [310, 140, 31], [352, 156, 28], [300, 80, 26]].map(([x, y, r]) => `<path d="M${x - r * 0.5} ${y - r * 0.2} q${r * 0.35} ${-r * 0.45} ${r * 0.8} ${-r * 0.1}" fill="none" stroke="${shade(H, 1.6)}" stroke-width="4" stroke-linecap="round"/>`).join('')}`;
    case 'fade': return `<path d="M180 250 C182 210 186 190 196 176 L206 240 Z M420 250 C418 210 414 190 404 176 L394 240 Z" fill="url(#fade${id})"/>
      <path d="M176 238 C160 130 222 60 302 60 C384 60 446 130 424 238 C418 200 404 176 390 164 C350 140 250 140 210 164 C196 176 182 200 176 238 Z" fill="${H}" ${SS}/>
      <path d="M220 110 Q236 98 250 108 M262 92 Q280 82 296 92 M310 90 Q330 82 344 94 M356 104 Q372 98 384 112" fill="none" stroke="${shade(H, 1.2)}" stroke-width="5" stroke-linecap="round"/>`;
    case 'bald': return `<path d="M176 290 C168 250 172 214 186 196 L200 214 L196 300 Z M424 290 C432 250 428 214 414 196 L400 214 L404 300 Z" fill="${H}" ${S(5)}/>
      <ellipse cx="262" cy="150" rx="46" ry="20" fill="#fff" opacity=".35" transform="rotate(-18 262 150)"/><ellipse cx="236" cy="176" rx="12" ry="6" fill="#fff" opacity=".3"/>
      <path d="M286 96 q4 -16 0 -26 M306 94 q6 -14 2 -24 M326 100 q8 -12 6 -22" fill="none" stroke="${H}" stroke-width="3" stroke-linecap="round"/>`;
    case 'thick': return `<path d="M170 250 C150 120 220 46 302 46 C388 46 456 120 430 250 C426 206 410 176 392 162 C356 140 246 140 210 162 C192 176 176 206 170 250 Z" fill="${H}" ${SS}/>
      <path d="M200 120 q30 -40 60 -10 q30 -40 60 -6 q30 -36 70 6 q-20 -60 -90 -68 q-70 6 -100 78 Z" fill="${H}" ${S(6)}/>
      <path d="M230 96 Q250 80 272 92 M300 76 Q324 66 344 82" fill="none" stroke="#4a3a30" stroke-width="5" stroke-linecap="round"/>`;
    case 'bowl': return `<path d="M168 262 C150 120 220 56 302 56 C386 56 452 120 432 262 L414 250 L400 214 L380 232 L356 204 L330 226 L304 200 L280 228 L254 204 L232 232 L210 210 L190 248 Z" fill="${H}" ${SS}/>
      <path d="M220 96 Q250 140 236 196 M290 80 Q300 140 286 196 M360 92 Q350 140 366 196" fill="none" stroke="#4a3a30" stroke-width="5" stroke-linecap="round"/>
      <path d="M250 70 q20 -8 40 0" fill="none" stroke="#6a5a4a" stroke-width="6" opacity=".6"/>`;
    case 'messy': return `<path d="M176 240 C150 130 214 52 302 52 C392 52 452 130 424 240 C418 196 404 172 388 160 C350 136 250 136 212 160 C196 172 182 196 176 240 Z" fill="${H}" ${SS}/>
      <path d="M210 92 l-28 -34 l44 18 M262 64 l-6 -42 l26 34 M330 62 l18 -40 l4 44 M384 92 l40 -24 l-22 40 M300 58 l10 -30 l12 30" fill="${H}" ${S(6)}/>
      <path d="M220 120 Q240 104 262 118 M300 100 Q322 90 340 106" fill="none" stroke="#3a2c22" stroke-width="5"/>`;
    case 'short': return `<path d="M176 236 C164 132 224 70 302 70 C382 70 442 132 424 236 C414 196 396 174 380 166 C340 150 260 150 222 166 C204 174 186 196 176 236 Z" fill="${H}" ${SS}/>`;
    case 'slick': return `<path d="M176 225 C164 120 226 64 302 64 C380 64 442 120 424 225 C416 180 398 158 380 150 C340 136 262 136 222 150 C204 158 184 180 176 225 Z" fill="${H}" ${SS}/>
      <path d="M220 120 Q300 86 384 122 M206 150 Q300 112 398 152" fill="none" stroke="#8d8d8d" stroke-width="6"/>`;
    case 'bun': return `<path d="M176 250 C156 136 222 70 300 70 C380 70 446 136 424 250 C412 196 380 160 300 152 C222 160 190 196 176 250 Z" fill="${H}" ${SS}/>
      <circle cx="176" cy="270" r="18" fill="${H}" ${S(5)}/><circle cx="424" cy="270" r="18" fill="${H}" ${S(5)}/>`;
    case 'cap': return `<path d="M170 220 C160 110 226 56 302 56 C380 56 446 110 430 220 C380 186 222 186 170 220 Z" fill="#151515" ${SS}/>
      <path d="M248 196 Q300 168 352 196 L352 214 Q300 190 248 214 Z" fill="#2c2c2c" ${S(5)}/><path d="M282 206 Q300 192 318 206" fill="none" stroke="#666" stroke-width="5"/>`;
    case 'capFront': return `<path d="M170 220 C160 110 226 56 302 56 C380 56 446 110 430 220 Z" fill="#222" ${SS}/><path d="M150 214 Q300 176 450 214 L450 236 Q300 202 150 236 Z" fill="#111" ${S(6)}/>`;
    case 'scarf': return `<path d="M190 214 C196 130 250 104 300 104 C352 104 406 130 410 214 C374 170 226 170 190 214 Z" fill="${H}" ${SS}/>`;
    case 'balding': return `<path d="M178 268 C172 220 178 196 192 182 L198 262 Z M422 268 C428 220 422 196 408 182 L402 262 Z" fill="${H}" ${S(5)}/>
      <path d="M240 120 Q300 104 360 120" fill="none" stroke="${H}" stroke-width="4"/>`;
    case 'shaved': return `<path d="M186 220 C186 136 236 96 300 96 C364 96 414 136 414 220" fill="#000" opacity=".1"/>`;
    case 'long': return `<path d="M170 250 C156 124 226 64 304 66 C384 70 446 130 430 250 C410 180 362 150 300 146 C252 160 200 190 170 250 Z" fill="${H}" ${SS}/>`;
    case 'flatcap': return `<path d="M178 272 C172 226 180 200 194 186 L200 266 Z M422 272 C428 226 420 200 406 186 L400 266 Z" fill="${H}" ${S(5)}/>
      <path d="M166 190 C170 110 236 74 306 76 C380 80 438 112 436 168 L458 196 Q300 160 146 196 Z" fill="#6e4b2f" ${SS}/>`;
    case 'police': return `<path d="M178 240 C168 160 226 120 302 120 C380 120 436 160 422 240 C410 206 380 192 300 190 C220 192 190 206 178 240 Z" fill="${H}" ${SS}/>
      <path d="M180 180 C180 100 240 64 300 64 C362 64 420 100 420 180 Z" fill="#1f2d4a" ${SS}/><path d="M160 176 L440 176 L428 206 Q300 188 172 206 Z" fill="#0f1626" ${S(6)}/><circle cx="300" cy="120" r="18" fill="#d4af37" ${S(4)}/>`;
  }
  return '';
}

function beard(c, id) {
  switch (c.beard) {
    case 'stubble': return `<path d="M186 360 C198 470 250 508 300 510 C350 508 402 470 414 360 C404 440 362 484 300 486 C238 484 196 440 186 360 Z" fill="url(#stub${id})"/><path d="M256 412 Q300 396 344 412 Q300 404 256 412 Z" fill="url(#stub${id})"/>`;
    case 'patchy': return `<path d="M200 420 C214 470 250 500 290 506 L280 470 C250 460 222 444 200 420 Z M400 420 C386 470 350 500 312 506 L322 470 C352 460 380 444 400 420 Z" fill="url(#stub${id})"/><path d="M270 412 Q285 402 296 410 Z" fill="url(#stub${id})"/>`;
    case 'cuts': return `<path d="M188 380 C204 470 250 508 296 512 L286 470 C250 462 214 440 188 380 Z M412 380 C396 470 350 508 306 512 L318 476 C352 462 390 438 412 380 Z" fill="url(#stub${id})"/>
      <path d="M262 470 Q280 480 300 476" fill="url(#stub${id})"/><circle cx="350" cy="452" r="5" fill="url(#stub${id})"/>
      <path d="M232 436 l14 6 M368 470 l12 -8 M300 498 l10 4" stroke="#d23a2a" stroke-width="4" stroke-linecap="round"/>`;
    case 'full': return `<path d="M180 340 C186 470 244 524 300 526 C356 524 414 470 420 340 C404 430 370 470 300 470 C230 470 196 430 180 340 Z" fill="${c.hc}" ${S(6)}/><path d="M250 410 Q300 386 350 410 Q300 420 250 410 Z" fill="${c.hc}" ${S(5)}/>`;
    case 'goatee': return `<path d="M244 420 Q270 398 300 410 Q330 398 356 420 Q352 432 336 426 Q318 418 300 424 Q282 418 264 426 Q248 432 244 420 Z" fill="${c.hc}" ${S(4)}/>
      <path d="M266 462 Q300 452 334 462 Q340 500 300 520 Q260 500 266 462 Z" fill="${c.hc}" ${S(4)}/><path d="M282 478 Q300 486 318 478" fill="none" stroke="${shade(c.hc, 1.6)}" stroke-width="3" stroke-linecap="round" opacity=".7"/>`;
    case 'trimmed': return `<path d="M184 356 C194 470 248 512 300 514 C352 512 406 470 416 356 C402 446 362 484 300 486 C238 484 198 446 184 356 Z" fill="${c.hc}" opacity=".85" ${S(5)}/><path d="M256 410 Q300 394 344 410 Q300 414 256 410 Z" fill="${c.hc}"/>`;
    case 'moustache': return `<path d="M246 418 Q272 388 300 406 Q328 388 354 418 Q328 426 300 414 Q272 426 246 418 Z" fill="#c9c9c9" ${S(5)}/>`;
  }
  return '';
}

function glasses(c) {
  switch (c.glasses) {
    case 'round': return `<circle cx="245" cy="305" r="44" fill="none" ${S(7)}/><circle cx="355" cy="305" r="44" fill="none" ${S(7)}/><path d="M289 300 L311 300" ${S(7)}/>`;
    case 'broken': return `<g transform="rotate(-4 300 305)"><rect x="196" y="270" width="98" height="72" rx="14" fill="#cfe6ff" fill-opacity=".25" ${S(9)}/><rect x="306" y="270" width="98" height="72" rx="14" fill="#cfe6ff" fill-opacity=".25" ${S(9)}/>
      <path d="M332 278 L356 312 L344 336 M356 312 L392 300" stroke="#ffffff" stroke-width="4" fill="none"/><path d="M332 278 L356 312 L344 336 M356 312 L392 300" stroke="#141414" stroke-width="1.5" fill="none"/>
      <rect x="284" y="288" width="32" height="28" rx="4" fill="#f4f4f4" ${S(4)}/><path d="M288 296 l24 0 M288 306 l24 0" stroke="#bbb" stroke-width="2"/>
      <path d="M196 290 L160 280 M404 290 L440 284" ${S(8)}/></g>`;
    case 'rect': return `<rect x="196" y="274" width="98" height="64" rx="10" fill="#cfe6ff" fill-opacity=".18" ${S(8)}/><rect x="306" y="274" width="98" height="64" rx="10" fill="#cfe6ff" fill-opacity=".18" ${S(8)}/><path d="M294 300 L306 300" ${S(7)}/><path d="M196 292 L160 284 M404 292 L440 284" ${S(7)}/>`;
    case 'thin': return `<rect x="200" y="280" width="92" height="56" rx="20" fill="#cfe6ff" fill-opacity=".12" stroke="#2a2a2a" stroke-width="4"/><rect x="308" y="280" width="92" height="56" rx="20" fill="#cfe6ff" fill-opacity=".12" stroke="#2a2a2a" stroke-width="4"/><path d="M292 300 L308 300 M200 296 L164 288 M400 296 L436 288" stroke="#2a2a2a" stroke-width="4"/>`;
    case 'forehead': return `<g transform="translate(0,-130)"><circle cx="248" cy="305" r="36" fill="#cfe6ff" opacity=".7" ${S(6)}/><circle cx="352" cy="305" r="36" fill="#cfe6ff" opacity=".7" ${S(6)}/><path d="M284 300 L316 300" ${S(6)}/></g>`;
    case 'sunHead': return `<g transform="translate(0,-170)"><ellipse cx="245" cy="305" rx="48" ry="30" fill="#151515" ${S(6)}/><ellipse cx="355" cy="305" rx="48" ry="30" fill="#151515" ${S(6)}/><path d="M293 300 L307 300" ${S(6)}/></g>`;
    case 'sun': return `<ellipse cx="245" cy="305" rx="48" ry="30" fill="#151515" ${S(6)}/><ellipse cx="355" cy="305" rx="48" ry="30" fill="#151515" ${S(6)}/><path d="M293 300 L307 300" ${S(6)}/>`;
  }
  return '';
}

let uid = 0;
function toonPerson(pid, expr = 'neutre', talk = false, noBody = false) {
  const blink = String(expr).endsWith('_blink'); const baseExpr = String(expr).replace('_blink', '');
  const c = C[pid], id = ++uid;
  const e0 = E[baseExpr] || E.neutre;
  const e = blink && !['squeeze', 'happy', 'cry'].includes(e0.eyes) ? Object.assign({}, e0, { eyes: 'shut' }) : e0;
  const skinS = shade(c.skin, -0.13);
  const browCol = c.brow || (c.fem ? '#2a1a12' : c.hc === '#f0d48a' ? '#a0784a' : '#1c1511');
  const hideEyes = c.glasses === 'sun';
  const sweat = Array.from({ length: e.sweat || 0 }, (_, i) => {
    const [x, y] = [[452, 200], [140, 250], [470, 300]][i];
    return `<path d="M${x} ${y} Q${x - 18} ${y + 34} ${x} ${y + 44} Q${x + 18} ${y + 34} ${x} ${y} Z" fill="#9fdcff" ${S(5)}/>`;
  }).join('');
  return `${defs(id)}<g>
    ${hairBack(c)}
    ${noBody ? '' : `<g transform="translate(0,-50)">${body(c)}
      <path d="M240 480 L240 580 Q300 606 360 580 L360 480 Z" fill="${skinS}" ${S()}/>
      ${c.chain === 'silver' ? '<path d="M232 568 Q300 620 368 568" fill="none" stroke="#d6d9de" stroke-width="7"/>' : ''}
      ${c.chain === 'gold' ? '<path d="M226 566 Q300 632 374 566" fill="none" stroke="#e2b73a" stroke-width="14"/><path d="M226 566 Q300 632 374 566" fill="none" stroke="#141414" stroke-width="3"/>' : ''}
    </g>`}
    <g transform="translate(300,300) scale(${c.w},1.02) translate(-300,-300)">
      ${c.hair !== 'scarf' ? `<path d="M178 260 C140 250 130 300 142 330 C152 360 176 368 186 356 Z" fill="${c.skin}" ${S()}/><path d="M422 260 C460 250 470 300 458 330 C448 360 424 368 414 356 Z" fill="${c.skin}" ${S()}/>
      <path d="M165 290 Q156 312 170 334 M435 290 Q444 312 430 334" fill="none" ${S(5)}/>` : ''}
      ${c.earring ? `<circle cx="150" cy="352" r="9" fill="#e2b73a" ${S(4)}/>` : ''}
      <path d="M178 230 C178 130 236 92 300 92 C364 92 422 130 422 230 L424 330 C424 448 372 512 300 516 C228 512 176 448 176 330 Z" fill="${c.skin}" ${S()}/>
      <path d="M196 400 C214 470 252 500 300 503 C348 500 386 470 404 400 C392 452 352 478 300 480 C248 478 208 452 196 400 Z" fill="${skinS}" opacity=".5"/>
      ${c.age ? `<path d="M232 170 Q300 156 368 170 M240 196 Q300 184 360 196" fill="none" stroke="${skinS}" stroke-width="6" stroke-linecap="round"/><path d="M252 380 Q238 412 250 440 M348 380 Q362 412 350 440" fill="none" stroke="${skinS}" stroke-width="6" stroke-linecap="round"/>` : ''}
      ${beard(c, id)}
      ${hairFront(c, id)}
      ${brows(e, browCol, c.fem)}
      ${hideEyes ? '' : eye(245, e.eyes, false, c.skin, c.fem) + eye(355, e.eyes, true, c.skin, c.fem)}
      ${glasses(c)}
      <path d="M302 300 C292 338 280 358 288 372 C298 386 322 384 330 370" fill="none" ${S(6)}/><path d="M292 368 Q298 362 304 368" fill="none" ${S(4)}/>
      ${c.jowls ? `<path d="M186 360 C176 430 206 480 246 492 C214 470 196 430 196 380 Z M414 360 C424 430 394 480 354 492 C386 470 404 430 404 380 Z" fill="${shade(c.skin, -0.1)}" opacity=".55"/><path d="M226 534 Q300 568 374 534" fill="none" stroke="#141414" stroke-width="5" stroke-linecap="round" opacity=".55"/>` : ''}
      ${c.teeth === 'dirty' ? mouth(e.mouth, talk, c.fem).replace(/fill="#fff"/g, 'fill="#d9bf55"') + '<circle cx="286" cy="436" r="4" fill="#8a5a2a"/><circle cx="318" cy="438" r="3.5" fill="#8a5a2a"/>' : mouth(e.mouth, talk, c.fem)}
      ${c.beard === 'moustache' ? beard(c, id) : ''}
      ${e.blush || c.fem ? `<ellipse cx="216" cy="384" rx="24" ry="12" fill="#ff7a7a" opacity="${e.blush ? .5 : .25}"/><ellipse cx="384" cy="384" rx="24" ry="12" fill="#ff7a7a" opacity="${e.blush ? .5 : .25}"/>` : ''}
      ${c.pimplesLight ? [[230, 214], [372, 392]].map(([x, y]) => `<circle cx="${x}" cy="${y}" r="7" fill="#e2524a" opacity=".7"/>`).join('') : ''}
      ${c.ugly ? [[200, 230], [400, 240], [260, 180], [340, 170], [215, 430], [385, 440], [300, 470], [250, 395], [350, 400], [190, 330], [410, 330], [320, 205], [280, 500], [330, 490]].map(([x, y], i) => `<circle cx="${x}" cy="${y}" r="${8 + (i % 3) * 3}" fill="${i % 4 ? '#e2524a' : '#f0d36a'}" ${S(3)}/><circle cx="${x - 2}" cy="${y - 3}" r="3" fill="#fff3d0"/>`).join('') + `<path d="M212 342 Q245 372 280 342 M320 342 Q355 372 388 342" fill="none" stroke="#6a3b6a" stroke-width="9" stroke-linecap="round" opacity=".55"/><path d="M216 356 Q245 384 276 356 M324 356 Q355 384 384 356" fill="none" stroke="#6a3b6a" stroke-width="6" stroke-linecap="round" opacity=".35"/><ellipse cx="300" cy="140" rx="60" ry="18" fill="#fff" opacity=".35"/><ellipse cx="300" cy="350" rx="14" ry="8" fill="#fff" opacity=".45"/><ellipse cx="225" cy="250" rx="18" ry="9" fill="#fff" opacity=".3"/>` : ''}
      ${c.headset ? `<path d="M150 300 C140 120 230 40 300 40 C370 40 460 120 450 300" fill="none" stroke="#141414" stroke-width="30"/><path d="M150 300 C140 120 230 40 300 40 C370 40 460 120 450 300" fill="none" stroke="#e5483f" stroke-width="12"/><rect x="118" y="250" width="56" height="110" rx="24" fill="#141414" ${S(6)}/><rect x="426" y="250" width="56" height="110" rx="24" fill="#141414" ${S(6)}/><rect x="128" y="270" width="18" height="70" rx="8" fill="#e5483f"/><rect x="454" y="270" width="18" height="70" rx="8" fill="#e5483f"/><path d="M150 350 Q170 450 250 455" fill="none" stroke="#141414" stroke-width="10" stroke-linecap="round"/><circle cx="256" cy="455" r="14" fill="#141414"/>` : ''}
      ${c.pimples ? [[230, 200], [372, 214], [300, 230], [210, 392], [392, 380], [372, 410], [236, 238]].map(([x, y]) => `<circle cx="${x}" cy="${y}" r="9" fill="#e2524a" ${S(3)}/><circle cx="${x - 2}" cy="${y - 2}" r="3" fill="#ffd0c0"/>`).join('') : ''}
      ${c.unibrow ? `<path d="M276 ${(e.brow[1]) + 4} Q300 ${(e.brow[1]) - 4} 324 ${(e.brow2 || e.brow)[1] + 4}" stroke="${browCol}" stroke-width="12" fill="none" stroke-linecap="round"/>` : ''}
      ${c.chin ? '<path d="M240 512 Q300 548 360 512" fill="none" stroke="#141414" stroke-width="6" stroke-linecap="round" opacity=".7"/>' : ''}
      ${c.hoops ? `<circle cx="168" cy="372" r="26" fill="none" stroke="#e2b73a" stroke-width="8"/><circle cx="432" cy="372" r="26" fill="none" stroke="#e2b73a" stroke-width="8"/>` : ''}
      ${e.tears ? `<path d="M226 318 Q214 380 222 470 L242 470 Q236 380 242 318 Z M374 318 Q386 380 378 470 L358 470 Q364 380 358 318 Z" fill="#7cc8ff" ${S(4)}/>` : ''}
      ${e.vein ? `<path d="M392 150 l14 -14 m-4 18 l14 -14 m-28 4 l-14 -14 m18 18 l-14 -14" stroke="#e33" stroke-width="7" stroke-linecap="round"/>` : ''}
      ${sweat}
    </g></g>`;
}

module.exports = { toonPerson, C, E };
