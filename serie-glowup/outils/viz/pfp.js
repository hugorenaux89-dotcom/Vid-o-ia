const { chromium } = require('playwright');
const { toonPerson } = require('./toon2');
const css = `<style>@font-face{font-family:'Lilita One';src:url(file:///root/.fonts/LilitaOne-Regular.ttf)}body{margin:0}</style>`;
const rays = [...Array(18)].map((_, i) => { const a = i * 20 * Math.PI / 180, b = (i * 20 + 10) * Math.PI / 180; return `<path d="M540 520 L${540 + 1200 * Math.cos(a)} ${520 + 1200 * Math.sin(a)} L${540 + 1200 * Math.cos(b)} ${520 + 1200 * Math.sin(b)} Z" fill="#fff" opacity=".07"/>`; }).join('');
const svg = (expr) => `<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1080" viewBox="0 0 1080 1080">
<defs><radialGradient id="g" cx=".5" cy=".45" r=".7"><stop offset="0" stop-color="#7b4cff"/><stop offset="1" stop-color="#1d1846"/></radialGradient></defs>
<rect width="1080" height="1080" fill="url(#g)"/>${rays}
<circle cx="540" cy="500" r="330" fill="#ffd23a" opacity=".25"/>
<g transform="translate(130,60) scale(1.37)">${toonPerson('YANIS_A', expr, false)}</g>
<g transform="translate(540,915) rotate(-4)"><rect x="-250" y="-70" width="500" height="130" rx="34" fill="#141418" stroke="#ffd23a" stroke-width="10"/>
<text x="0" y="28" font-family="Lilita One" font-size="92" text-anchor="middle" fill="#ffd23a" stroke="#000" stroke-width="3">30 <tspan fill="#fff">JOURS</tspan></text></g></svg>`;
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1080 } });
  for (const e of ['choque', 'sourire']) {
    await p.setContent(css + svg(e)); await p.evaluate(() => document.fonts.ready);
    await p.screenshot({ path: `${process.argv[2]}/pfp_${e}.png` });
  }
  await b.close();
})();
