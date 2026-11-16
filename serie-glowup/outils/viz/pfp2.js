const { chromium } = require('playwright');
const { stand, PROPS } = require('./rig'); require('./props2'); const { ensureY } = require('./look');
ensureY('Y1');
const css = `<style>@font-face{font-family:'Lilita One';src:url(file:///root/.fonts/LilitaOne-Regular.ttf)}body{margin:0}</style>`;
const rays = [...Array(18)].map((_, i) => { const a = i * 20 * Math.PI / 180, b = (i * 20 + 10) * Math.PI / 180; return `<path d="M540 470 L${540 + 1300 * Math.cos(a)} ${470 + 1300 * Math.sin(a)} L${540 + 1300 * Math.cos(b)} ${470 + 1300 * Math.sin(b)} Z" fill="#fff" opacity=".07"/>`; }).join('');
const V = {
  choque: { expr: 'choque', la: [125, 150], ra: [125, 152], rp: ['controller', 20, 0, 0], t: 0.3 },
  rage: { expr: 'colere', la: [130, 155], ra: [130, 158], rp: ['controller', -25, 0, 0], t: 0.3 },
};
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1080 } });
  for (const [k, q] of Object.entries(V)) {
    const y = stand('Y1', Object.assign({ jiggle: 0, stink: 0.9 }, q));
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1080" viewBox="0 0 1080 1080">
      <defs><radialGradient id="g" cx=".5" cy=".42" r=".75"><stop offset="0" stop-color="#ff3fa4"/><stop offset=".55" stop-color="#6a2bd8"/><stop offset="1" stop-color="#150b3a"/></radialGradient></defs>
      <rect width="1080" height="1080" fill="url(#g)"/>${rays}
      <circle cx="540" cy="470" r="360" fill="#ffd23a" opacity=".18"/>
      <g transform="translate(${540 - 300 * 1.2},${-20}) scale(1.2)">${y}</g>
      <g transform="translate(540,960) rotate(-4)"><rect x="-300" y="-78" width="600" height="140" rx="38" fill="#141418" stroke="#ffd23a" stroke-width="10"/>
      <text x="0" y="28" font-family="Lilita One" font-size="96" text-anchor="middle" fill="#ffd23a" stroke="#000" stroke-width="3">30 <tspan fill="#fff">JOURS</tspan></text></g></svg>`;
    await p.setContent(css + svg); await p.evaluate(() => document.fonts.ready);
    await p.screenshot({ path: `${process.argv[2]}/pfp2_${k}.png` });
  }
  await b.close();
})();
