const { chromium } = require('playwright');
const { stand } = require('./rig'); const { ensureY } = require('./look');
const days = [1, 3, 7, 11, 12, 13, 14, 18, 20, 24, 28, '28s', 30];
const css = `<style>@font-face{font-family:'Lilita One';src:url(file:///root/.fonts/LilitaOne-Regular.ttf)}body{margin:0;background:#7a8}</style>`;
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 13 * 300, height: 700 } });
  const svg = days.map((d, i) => { ensureY('Y' + d); return `<g transform="translate(${i * 300},20) scale(0.5)">${stand('Y' + d, { expr: 'sourire', t: 0 })}</g><text x="${i * 300 + 150}" y="690" font-size="40" text-anchor="middle">${d}</text>`; }).join('');
  await p.setContent(css + `<svg xmlns="http://www.w3.org/2000/svg" width="${13 * 300}" height="700">${svg}</svg>`);
  await p.screenshot({ path: process.argv[2] }); await b.close(); })();
