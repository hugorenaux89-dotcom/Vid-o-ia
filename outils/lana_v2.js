// Lana 30 jours — rendu v2 (2D cartoon ombré, proche du rendu de la série de référence)
const K = '#151515';
const O = (w=6) => `stroke="${K}" stroke-width="${w}" stroke-linejoin="round" stroke-linecap="round"`;
const SKIN='#f4c39c', SKIN_D='#e3a67c', HAIR='#7a4526', HAIR_D='#56301a', PINK='#f6a9c9', PINK_D='#e283ad';

const defs = `
<defs>
 <linearGradient id="wall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a1b45"/><stop offset="1" stop-color="#3c2766"/></linearGradient>
 <radialGradient id="vig" cx=".5" cy=".55" r=".75"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".55"/></radialGradient>
 <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0f1638"/><stop offset="1" stop-color="#26346b"/></linearGradient>
 <linearGradient id="floor" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3e2c3a"/><stop offset="1" stop-color="#271a24"/></linearGradient>
 <radialGradient id="glow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#9fd8ff" stop-opacity=".55"/><stop offset="1" stop-color="#9fd8ff" stop-opacity="0"/></radialGradient>
 <radialGradient id="blush" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#ff7d8e" stop-opacity=".5"/><stop offset="1" stop-color="#ff7d8e" stop-opacity="0"/></radialGradient>
 <filter id="sh" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="8" stdDeviation="8" flood-color="#000" flood-opacity=".35"/></filter>
 <clipPath id="cFace"><ellipse cx="360" cy="560" rx="148" ry="158"/></clipPath>
 <clipPath id="cTop"><path d="M222 790 Q235 735 360 728 Q485 735 498 790 L515 1010 L205 1010 Z"/></clipPath>
 <pattern id="stars" width="70" height="70" patternUnits="userSpaceOnUse"><path d="M20 22 l4 -10 l4 10 l-4 -2z" fill="#fff" opacity=".55"/><circle cx="52" cy="50" r="3" fill="#fff" opacity=".45"/></pattern>
</defs>`;

function room() {
  let st=''; for(let x=0;x<720;x+=60) st+=`<rect x="${x}" y="0" width="30" height="1000" fill="#fff" opacity=".035"/>`;
  return `
  <rect width="720" height="1280" fill="url(#wall)"/>${st}
  <!-- fenêtre de nuit + rideau -->
  <rect x="455" y="225" width="225" height="300" rx="6" fill="url(#sky)" ${O(7)}/>
  <circle cx="625" cy="290" r="28" fill="#fff4c4" opacity=".9"/>
  ${[[495,270],[540,330],[600,380],[505,420],[650,450],[560,470]].map(([x,y])=>`<circle cx="${x}" cy="${y}" r="3" fill="#fff"/>`).join('')}
  <line x1="567" y1="225" x2="567" y2="525" ${O(6)}/><line x1="455" y1="375" x2="680" y2="375" ${O(6)}/>
  <rect x="440" y="205" width="260" height="18" rx="4" fill="#3a2a2a" ${O(5)}/>
  <path d="M450 222 q-10 150 10 330 l55 0 q-25 -170 -10 -330z" fill="#8c3a6a" ${O(6)}/>
  <path d="M470 240 q-6 140 10 300" stroke="#6d2a52" stroke-width="6" fill="none"/>
  <!-- guirlande lumineuse -->
  <path d="M20 215 q170 70 340 10" fill="none" stroke="#222" stroke-width="3"/>
  ${[60,110,160,210,260,310].map((x,i)=>{const y=215+Math.sin((x-20)/340*Math.PI)*42;const c=['#ffd23f','#ff7aa8','#7fe0ff'][i%3];return `<circle cx="${x}" cy="${y+8}" r="16" fill="${c}" opacity=".25"/><circle cx="${x}" cy="${y+8}" r="7" fill="${c}" ${O(3)}/>`}).join('')}
  <!-- poster -->
  <g transform="rotate(-5 120 360)" filter="url(#sh)">
   <rect x="35" y="260" width="175" height="225" rx="6" fill="#ef5b93" ${O(6)}/>
   <circle cx="122" cy="345" r="48" fill="#ffd23f" ${O(5)}/><path d="M95 345 l20 -30 l20 30 l20 -30" fill="none" ${O(5)}/>
   <text x="122" y="455" font-family="Anton" font-size="34" fill="#fff" text-anchor="middle">K-DRAMA</text>
  </g>
  <!-- calendrier -->
  <g filter="url(#sh)"><rect x="45" y="545" width="150" height="150" rx="10" fill="#fdfdfd" ${O(6)}/>
  <path d="M45 585 v-30 a10 10 0 0 1 10 -10 h130 a10 10 0 0 1 10 10 v30z" fill="#e23b3b" ${O(5)}/>
  <text x="120" y="577" font-family="Anton" font-size="22" fill="#fff" text-anchor="middle">NOVEMBRE</text>
  ${[0,1,2,3].map(r=>[0,1,2,3,4].map(c=>`<rect x="${58+c*26}" y="${598+r*22}" width="18" height="14" rx="2" fill="#d8d8d8"/>`).join('')).join('')}
  <text x="150" y="683" font-family="Anton" font-size="38" fill="#e23b3b" text-anchor="middle">30</text></g>
  <!-- sol -->
  <rect x="0" y="1000" width="720" height="280" fill="url(#floor)"/>
  ${[0,1,2,3,4].map(i=>`<line x1="0" y1="${1040+i*55}" x2="720" y2="${1040+i*55}" stroke="#1d131b" stroke-width="4" opacity=".6"/>`).join('')}
  <!-- lit -->
  <g filter="url(#sh)">
   <rect x="-30" y="860" width="250" height="175" rx="16" fill="#6d55a8" ${O(7)}/>
   <path d="M-30 885 q70 -45 130 -5 q60 -45 120 5 v40 h-250z" fill="#b9a5ea" ${O(7)}/>
   <path d="M20 880 q30 -20 60 0" fill="none" stroke="#8f78cf" stroke-width="5"/>
  </g>
  <!-- bureau + ordi portable -->
  <g filter="url(#sh)">
   <rect x="500" y="770" width="230" height="22" fill="#5b3b2c" ${O(6)}/>
   <rect x="520" y="792" width="18" height="200" fill="#4a2f22" ${O(5)}/>
   <path d="M560 768 l15 -95 h120 l15 95z" fill="#2c2c34" ${O(6)}/>
   <path d="M578 760 l11 -75 h96 l11 75z" fill="#7fd0ff" opacity=".9"/>
   <ellipse cx="635" cy="720" rx="90" ry="60" fill="url(#glow)"/>
   <rect x="520" y="740" width="34" height="30" rx="5" fill="#f1f1f1" ${O(4)}/><path d="M554 748 q14 2 0 16" fill="none" ${O(4)}/>
   <path d="M524 738 q6 -18 0 -30 M540 738 q6 -18 0 -30" stroke="#ccc" stroke-width="3" fill="none"/>
  </g>
  <!-- plante morte -->
  <path d="M612 990 l-12 -95 M612 990 l22 -70 M604 930 q-34 -8 -44 12 M622 915 q30 -5 36 20" fill="none" stroke="#86622f" stroke-width="6" stroke-linecap="round"/>
  <path d="M578 990 h75 l-9 78 h-57z" fill="#c9653c" ${O(6)}/><path d="M584 1005 h63" stroke="#a54d2c" stroke-width="5"/>
  <!-- tas de linge -->
  <g filter="url(#sh)">
   <path d="M490 1150 q30 -70 100 -55 q55 -45 120 5 q30 50 0 80 h-210 q-30 -5 -10 -30z" fill="#5aa6d6" ${O(6)}/>
   <path d="M540 1118 q34 -30 70 2" fill="none" ${O(4)}/>
   <path d="M600 1100 q40 -40 90 -10 l-10 40 q-40 -20 -70 5z" fill="#f2d24a" ${O(5)}/>
   <path d="M505 1140 q20 -30 50 -20 l-5 25z" fill="#ef5b93" ${O(4)}/>
  </g>
  <!-- boîtes de pizza + canette -->
  <g filter="url(#sh)">
  ${[0,1,2].map(i=>`<rect x="${25+i*7}" y="${1170-i*30}" width="195" height="30" rx="3" fill="#e8c08b" ${O(5)}/>`).join('')}
  <text x="129" y="1137" font-family="Anton" font-size="20" fill="#b5462b" text-anchor="middle">PIZZA</text>
  <rect x="230" y="1150" width="30" height="50" rx="6" fill="#e23b3b" ${O(4)} transform="rotate(70 245 1175)"/>
  </g>`;
}

function odeurs(){
  const w=(x,y,o=.8)=>`<path d="M${x} ${y} q16 -22 0 -44 q-16 -22 0 -44 q16 -22 0 -44" fill="none" stroke="#9be07a" stroke-width="5" stroke-linecap="round" opacity="${o}"/>`;
  return w(205,500)+w(530,640,.7)+w(255,990)+w(470,470,.6)+w(660,910)+w(120,1060,.7);
}

function lana(expr='blase'){
  const legs = `
  <path d="M262 1000 L250 1200 L340 1200 L352 1010 Z" fill="${PINK}" ${O(7)}/>
  <path d="M368 1010 L380 1200 L470 1200 L458 1000 Z" fill="${PINK}" ${O(7)}/>
  <path d="M268 1030 l-12 160 h25 l10 -160z M440 1030 l12 160 h18 l-10 -160z" fill="${PINK_D}" opacity=".8"/>
  ${[[290,1060],[320,1130],[275,1170],[410,1080],[440,1150],[400,1180]].map(([x,y])=>`<path d="M${x} ${y} l5 -10 l5 10 l-5 -3z" fill="#fff" opacity=".9"/>`).join('')}
  <!-- chaussons licorne -->
  ${[[295,1215],[425,1215]].map(([x,y])=>`<ellipse cx="${x}" cy="${y}" rx="62" ry="32" fill="#fff" ${O(7)}/><ellipse cx="${x}" cy="${y+12}" rx="55" ry="16" fill="#e9e3f3"/><path d="M${x-8} ${y-28} l10 -32 l10 32z" fill="#ffd23f" ${O(4)}/><circle cx="${x-18}" cy="${y-6}" r="5" fill="${K}"/><circle cx="${x+18}" cy="${y-6}" r="5" fill="${K}"/>`).join('')}`;
  const top = `
  <!-- bras -->
  <path d="M232 800 Q190 840 180 960 Q178 1000 205 1000 Q228 995 232 950 L250 850 Z" fill="${PINK}" ${O(7)}/>
  <path d="M488 800 Q530 840 540 960 Q542 1000 515 1000 Q492 995 488 950 L470 850 Z" fill="${PINK}" ${O(7)}/>
  <path d="M500 840 q25 60 30 140" stroke="${PINK_D}" stroke-width="14" fill="none" opacity=".8"/>
  <ellipse cx="195" cy="1010" rx="28" ry="30" fill="${SKIN}" ${O(6)}/><ellipse cx="525" cy="1010" rx="28" ry="30" fill="${SKIN}" ${O(6)}/>
  <path d="M185 1030 q8 6 16 0 M515 1030 q8 6 16 0" stroke="${SKIN_D}" stroke-width="4" fill="none"/>
  <!-- haut de pyjama -->
  <path d="M222 790 Q235 735 360 728 Q485 735 498 790 L515 1010 L205 1010 Z" fill="${PINK}" ${O(7)}/>
  <g clip-path="url(#cTop)"><path d="M440 730 Q500 800 520 1010 L560 1010 L560 720 Z" fill="${PINK_D}" opacity=".75"/>
   <rect x="200" y="990" width="330" height="30" fill="${PINK_D}" opacity=".6"/></g>
  <path d="M320 732 q40 28 80 0" fill="#fff" ${O(5)}/>
  <!-- licorne brodée -->
  <circle cx="360" cy="860" r="52" fill="#fff" ${O(5)}/>
  <path d="M343 812 l17 -48 l17 48z" fill="#ffd23f" ${O(5)}/><path d="M350 795 l20 -6 M354 780 l13 -4" stroke="#e0a800" stroke-width="3"/>
  <path d="M318 830 q-25 20 -8 50 M402 830 q22 18 8 48" fill="none" stroke="#b78be8" stroke-width="10" stroke-linecap="round"/>
  <circle cx="343" cy="855" r="6" fill="${K}"/><circle cx="378" cy="855" r="6" fill="${K}"/>
  <path d="M345 880 q15 12 30 0" fill="none" ${O(4)}/><circle cx="332" cy="872" r="8" fill="url(#blush)"/><circle cx="390" cy="872" r="8" fill="url(#blush)"/>
  <!-- taches -->
  <path d="M265 800 q12 -8 22 2 q8 12 -6 16 q-16 2 -16 -18z" fill="#c9783f" opacity=".85"/>
  <path d="M420 950 q16 -10 28 4 q6 16 -12 18 q-20 -2 -16 -22z" fill="#c9783f" opacity=".85"/>
  <circle cx="290" cy="945" r="9" fill="#e23b3b" opacity=".85"/><circle cx="455" cy="805" r="7" fill="#ffd23f"/>
  <text x="360" y="975" font-family="Anton" font-size="56" fill="#43c3ff" stroke="${K}" stroke-width="5" paint-order="stroke" text-anchor="middle">LANA</text>`;
  const eyes = expr==='choc'
   ? `<ellipse cx="303" cy="565" rx="27" ry="31" fill="#fff" ${O(5)}/><ellipse cx="418" cy="565" rx="27" ry="31" fill="#fff" ${O(5)}/>
      <circle cx="303" cy="567" r="9" fill="${K}"/><circle cx="418" cy="567" r="9" fill="${K}"/>`
   : `<ellipse cx="303" cy="570" rx="26" ry="27" fill="#fff" ${O(5)}/><ellipse cx="418" cy="570" rx="26" ry="27" fill="#fff" ${O(5)}/>
      <circle cx="306" cy="578" r="10" fill="#4a2c1a"/><circle cx="306" cy="578" r="5" fill="${K}"/><circle cx="310" cy="574" r="2.5" fill="#fff"/>
      <circle cx="415" cy="578" r="10" fill="#4a2c1a"/><circle cx="415" cy="578" r="5" fill="${K}"/><circle cx="419" cy="574" r="2.5" fill="#fff"/>
      <path d="M276 568 q27 -9 54 0 l0 -26 h-54z" fill="${SKIN}" ${O(5)}/><path d="M391 568 q27 -9 54 0 l0 -26 h-54z" fill="${SKIN}" ${O(5)}/>`;
  const mouth = expr==='choc'
   ? `<path d="M340 655 q22 -14 44 0 q4 40 -22 42 q-26 -2 -22 -42z" fill="#7a1f2b" ${O(5)}/><path d="M346 685 q16 -10 32 0 q-4 10 -16 10 q-12 0 -16 -10z" fill="#ff8a95"/>`
   : `<path d="M332 668 q30 -16 62 2" fill="none" ${O(5)}/><path d="M392 668 l6 6" ${O(4)}/>`;
  return legs + top + `
  <!-- cou -->
  <path d="M328 700 h64 v40 q-32 16 -64 0z" fill="${SKIN_D}" ${O(5)}/>
  <!-- chignon nid d'oiseau -->
  <g>
   <path d="M300 410 l-48 -34 M425 405 l46 -40 M360 352 l4 -44 M330 360 l-26 -40 M400 365 l30 -38" stroke="${HAIR}" stroke-width="9" stroke-linecap="round"/>
   <circle cx="362" cy="400" r="74" fill="${HAIR}" ${O(7)}/>
   <path d="M305 375 q40 -45 95 -10 M310 420 q48 26 100 -24 M335 350 q10 60 60 70 M300 400 q30 -5 50 20" fill="none" stroke="${HAIR_D}" stroke-width="5"/>
   <path d="M330 345 q30 -18 60 -5" stroke="#b77447" stroke-width="5" fill="none" opacity=".8"/>
   <rect x="398" y="300" width="17" height="115" rx="3" fill="#ffd23f" ${O(5)} transform="rotate(32 406 357)"/>
   <path d="M432 293 l12 -18" stroke="#e23b3b" stroke-width="9" stroke-linecap="round" transform="rotate(0)"/>
   <!-- chouchou -->
   <ellipse cx="362" cy="465" rx="62" ry="16" fill="#43c3ff" ${O(5)}/>
  </g>
  <!-- cheveux arrière -->
  <path d="M212 560 Q210 440 362 432 Q514 440 508 560 L516 690 Q490 720 470 690 L250 690 Q230 720 204 690 Z" fill="${HAIR}" ${O(7)}/>
  <!-- visage -->
  <ellipse cx="360" cy="560" rx="148" ry="158" fill="${SKIN}" ${O(7)}/>
  <g clip-path="url(#cFace)">
   <ellipse cx="460" cy="600" rx="90" ry="190" fill="${SKIN_D}" opacity=".55"/>
   <ellipse cx="300" cy="460" rx="70" ry="40" fill="#fff" opacity=".18"/>
  </g>
  <ellipse cx="360" cy="560" rx="148" ry="158" fill="none" ${O(7)}/>
  <!-- oreilles -->
  <path d="M214 560 q-30 -10 -28 30 q4 35 34 30z" fill="${SKIN}" ${O(6)}/><path d="M506 560 q30 -10 28 30 q-4 35 -34 30z" fill="${SKIN_D}" ${O(6)}/>
  <!-- frange en mèches -->
  <path d="M215 520 Q240 425 362 425 Q485 425 506 520 Q470 470 432 492 Q412 455 372 482 Q340 450 305 485 Q262 462 215 520 Z" fill="${HAIR}" ${O(7)}/>
  <path d="M250 470 q40 -25 90 -20 M390 452 q45 0 80 25" stroke="#b77447" stroke-width="5" fill="none" opacity=".75"/>
  <path d="M226 510 q-22 70 -6 140 M496 505 q26 80 6 150" fill="none" stroke="${HAIR}" stroke-width="13" stroke-linecap="round"/>
  <path d="M226 510 q-22 70 -6 140 M496 505 q26 80 6 150" fill="none" stroke="${K}" stroke-width="3" stroke-linecap="round" opacity=".6"/>
  <path d="M440 430 q30 -30 20 -60" fill="none" stroke="${HAIR}" stroke-width="7" stroke-linecap="round"/>
  <!-- sourcils broussailleux -->
  <path d="M262 528 q38 -38 84 -12 l-6 24 q-38 -18 -74 8z" fill="#3b2213" ${O(4)}/>
  <path d="M376 516 q46 -26 84 12 l-4 20 q-36 -26 -74 -8z" fill="#3b2213" ${O(4)}/>
  ${[0,1,2,3,4,5].map(i=>`<path d="M${270+i*12} ${522-i*3} l-4 -14" stroke="#3b2213" stroke-width="4" stroke-linecap="round"/><path d="M${388+i*12} ${510+(i>3?(i-3)*4:-i)} l3 -14" stroke="#3b2213" stroke-width="4" stroke-linecap="round"/>`).join('')}
  ${eyes}
  <!-- cernes -->
  <path d="M280 604 q24 14 48 0 M394 604 q24 14 48 0" fill="none" stroke="#b9786b" stroke-width="5" stroke-linecap="round"/>
  <path d="M284 614 q20 8 40 0 M398 614 q20 8 40 0" fill="none" stroke="#c99187" stroke-width="3" stroke-linecap="round"/>
  <!-- lunettes rondes de travers -->
  <g transform="rotate(-7 360 570)">
   <circle cx="303" cy="570" r="44" fill="#bfe6ff" fill-opacity=".12" stroke="${K}" stroke-width="9"/>
   <circle cx="418" cy="570" r="44" fill="#bfe6ff" fill-opacity=".12" stroke="${K}" stroke-width="9"/>
   <path d="M280 545 l14 -10 M395 545 l14 -10" stroke="#fff" stroke-width="5" stroke-linecap="round" opacity=".8"/>
   <path d="M347 568 q14 -10 27 0" fill="none" stroke="${K}" stroke-width="9"/>
   <rect x="349" y="556" width="24" height="18" rx="2" fill="#fff" ${O(4)}/><path d="M353 565 h16" stroke="#ccc" stroke-width="3"/>
   <path d="M259 565 l-45 -8 M462 565 l45 -8" stroke="${K}" stroke-width="7"/>
  </g>
  <!-- nez, joues, bouche -->
  <path d="M362 595 q-14 34 6 42 q10 2 14 -4" fill="none" ${O(5)}/>
  <ellipse cx="275" cy="640" rx="34" ry="20" fill="url(#blush)"/><ellipse cx="448" cy="640" rx="34" ry="20" fill="url(#blush)"/>
  ${mouth}
  <!-- boutons et taches -->
  <circle cx="258" cy="650" r="8" fill="#e8434a" ${O(4)}/><circle cx="256" cy="647" r="2.5" fill="#fff"/>
  <circle cx="450" cy="490" r="7" fill="#e8434a" ${O(4)}/>
  <circle cx="395" cy="690" r="5" fill="#e8434a" ${O(3)}/>
  <!-- goutte de sueur -->
  <path d="M478 515 q-14 24 0 34 q14 -10 0 -34z" fill="#8fd7ff" ${O(4)}/><path d="M475 532 q2 6 6 6" stroke="#fff" stroke-width="3" fill="none"/>`;
}

function chat(x,y,sc,expr='juge'){
  return `<g transform="translate(${x} ${y}) scale(${sc})" filter="url(#sh)">
  <path d="M60 80 q90 -10 70 -90" fill="none" stroke="${K}" stroke-width="22" stroke-linecap="round"/>
  <path d="M60 80 q90 -10 70 -90" fill="none" stroke="#ef8a2e" stroke-width="13" stroke-linecap="round"/>
  <ellipse cx="0" cy="60" rx="88" ry="72" fill="#ef8a2e" ${O(7)}/>
  <ellipse cx="0" cy="80" rx="45" ry="45" fill="#fbe3c4"/>
  <path d="M-60 40 q12 12 0 26 M60 40 q-12 12 0 26 M-30 0 q0 14 -6 22 M30 0 q0 14 6 22" stroke="#c4651c" stroke-width="6" fill="none"/>
  <circle cx="0" cy="-30" r="64" fill="#ef8a2e" ${O(7)}/>
  <path d="M-58 -58 l6 -60 l44 32z M58 -58 l-6 -60 l-44 32z" fill="#ef8a2e" ${O(7)}/>
  <path d="M-48 -70 l3 -30 l22 16z M48 -70 l-3 -30 l-22 16z" fill="#f7b8c4"/>
  <path d="M-15 -90 l5 22 M0 -94 v24 M15 -90 l-5 22" stroke="#c4651c" stroke-width="6" stroke-linecap="round"/>
  <ellipse cx="-24" cy="-32" rx="15" ry="13" fill="#d6f27a" ${O(4)}/><ellipse cx="24" cy="-32" rx="15" ry="13" fill="#d6f27a" ${O(4)}/>
  <rect x="-27" y="-42" width="6" height="20" rx="3" fill="${K}"/><rect x="21" y="-42" width="6" height="20" rx="3" fill="${K}"/>
  <path d="M-42 -40 q18 -4 34 4 l0 -12 h-34z M42 -40 q-18 -4 -34 4 l0 -12 h34z" fill="#ef8a2e" ${O(4)}/>
  <ellipse cx="0" cy="-2" rx="30" ry="20" fill="#fbe3c4"/>
  <path d="M-8 -12 l8 8 l8 -8z" fill="#e8708f" ${O(4)}/>
  <path d="M0 -4 v6 M-14 10 q14 -10 28 0" fill="none" ${O(4)}/>
  <path d="M-34 -6 h-44 M-34 4 h-40 M34 -6 h44 M34 4 h40" stroke="${K}" stroke-width="3"/>
  <ellipse cx="-36" cy="120" rx="26" ry="16" fill="#ef8a2e" ${O(6)}/><ellipse cx="36" cy="120" rx="26" ry="16" fill="#ef8a2e" ${O(6)}/>
  </g>`;
}

function hud(j=30,g=0){
  const box=(x,label,val,col)=>`<g filter="url(#sh)"><rect x="${x}" y="105" width="200" height="94" rx="16" fill="#121212" stroke="#333" stroke-width="3"/>
   <text x="${x+100}" y="138" font-family="Anton" font-size="22" fill="#fff" text-anchor="middle">${label}</text>
   <text x="${x+100}" y="188" font-family="Anton" font-size="48" fill="${col}" text-anchor="middle">${val}</text></g>`;
  return box(70,'JOURS RESTANTS',j,'#ffd23f')+box(450,'GLOW-UP',g+'%','#5fd35a');
}
const titre=(y,parts,size=118)=>`<text x="360" y="${y}" font-family="Anton" font-size="${size}" text-anchor="middle" stroke="${K}" stroke-width="16" paint-order="stroke" filter="url(#sh)">${parts.map(([t,c])=>`<tspan fill="${c}">${t}</tspan>`).join('')}</text>`;
const bandeau=(t,y=1110)=>`<g filter="url(#sh)"><rect x="65" y="${y}" width="590" height="82" rx="18" fill="#121212" stroke="#ffd23f" stroke-width="4"/>
  <text x="360" y="${y+55}" font-family="Anton" font-size="36" fill="#fff" text-anchor="middle">${t}</text></g>`;
const tel=`<g transform="translate(575 800) rotate(14)" filter="url(#sh)"><rect x="-75" y="-125" width="150" height="250" rx="22" fill="#1b1b1b" ${O(6)}/>
  <rect x="-62" y="-104" width="124" height="200" rx="8" fill="#fff"/>
  <rect x="-54" y="-92" width="108" height="150" rx="12" fill="#e9f6ff" stroke="#9cc" stroke-width="2"/>
  <text x="0" y="-62" font-family="Anton" font-size="20" fill="${K}" text-anchor="middle">INÈS 🎉</text>
  <text x="0" y="-30" font-family="Anton" font-size="14" fill="${K}" text-anchor="middle">LES 10 ANS DU LYCÉE</text>
  <text x="0" y="-6" font-family="Anton" font-size="14" fill="${K}" text-anchor="middle">C'EST DANS 30 JOURS</text>
  <text x="0" y="30" font-family="Anton" font-size="16" fill="#e23b3b" text-anchor="middle">NATHAN VIENT ❤</text></g>`;

const scenes={
 'plan03-lana-chambre':()=>room()+odeurs()+lana('blase')+`<rect width="720" height="1280" fill="url(#vig)"/>`+hud(),
 'plan05-lana-choc':()=>room()+odeurs()+lana('choc')+`<rect width="720" height="1280" fill="url(#vig)"/>`+tel+hud(),
 'plan04-pates':()=>room()+odeurs()+chat(360,820,2.1)+`<rect width="720" height="1280" fill="url(#vig)"/>`+hud(),
 'couverture-ep01':()=>room()+odeurs()+`<g transform="translate(0 110)">${lana('blase')}</g><rect width="720" height="1280" fill="url(#vig)"/>`+
   titre(150,[['30 JOURS','#ffd23f']])+titre(280,[['POUR TOUT','#fff']])+titre(410,[['CHANGER','#e23b3b']])+bandeau('JOUR 1 · À TOI DE CHOISIR'),
};
module.exports={scenes};

if(require.main===module){
  const {chromium}=require('playwright'); const out=process.argv[2];
  (async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:720,height:1280}});
   for(const [n,fn] of Object.entries(scenes)){
    await p.setContent(`<html><head><link href="https://fonts.googleapis.com/css2?family=Anton&display=block" rel="stylesheet"><style>body{margin:0}</style></head><body><svg xmlns="http://www.w3.org/2000/svg" width="720" height="1280" viewBox="0 0 720 1280">${defs}${fn()}</svg></body></html>`,{waitUntil:'networkidle'});
    await p.evaluate(()=>document.fonts.ready); await p.screenshot({path:`${out}/${n}.png`}); console.log('ok',n);}
   await b.close();})();
}
