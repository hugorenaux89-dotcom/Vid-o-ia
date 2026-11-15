// Pilote Playwright du rendu 3D : sert les fichiers locaux, expose page.frame(T, overlaySvg)
const path = require('path');
const fs = require('fs');
const { chromium } = require('playwright');
const ROOT = path.join(__dirname, '..');
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json' };
async function ouvrir(b, init, dsf = 1) {
  const p = await b.newPage({ viewport: { width: 720, height: 1280 }, deviceScaleFactor: dsf });
  p.on('pageerror', (e) => console.error('PAGE ERROR', e.message));
  p.on('console', (m) => { if (m.type() === 'error' || m.type() === 'warning') console.error('console:', m.text()); });
  await p.route('http://lana.local/**', (r) => {
    const f = path.join(ROOT, new URL(r.request().url()).pathname);
    if (!fs.existsSync(f)) return r.fulfill({ status: 404, body: '' });
    r.fulfill({ status: 200, body: fs.readFileSync(f), contentType: TYPES[path.extname(f)] || 'application/octet-stream' });
  });
  await p.goto('http://lana.local/3d/index.html');
  await p.waitForFunction(() => window.pret === true, null, { timeout: 120000 });
  await p.evaluate(async (i) => { await document.fonts.load('40px Anton'); await window.init(i); }, init);
  return p;
}
const lancer = () => chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
async function image(p, T, svg) {
  await p.evaluate(([t, s]) => window.frame(t, s), [T, svg]);
}
module.exports = { ouvrir, lancer, image };
