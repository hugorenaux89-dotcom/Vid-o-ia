// Rend décors (1188x2112) et personnages style BD (1200x1440, transparent)
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const { BG } = require('./toonbg');
const { toonPerson } = require('./toon2');
const [,, listFile, outDir] = process.argv;
const req = JSON.parse(fs.readFileSync(listFile));
const css = `<style>@font-face{font-family:Anton;src:url(file:///root/.fonts/Anton-Regular.ttf)}body{margin:0;background:transparent}</style>`;
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1188, height: 2112 } });
  for (const s of req.scenes) {
    const f = path.join(outDir, `bg_${s}.png`); if (fs.existsSync(f)) continue;
    await p.setViewportSize({ width: 1188, height: 2112 });
    await p.setContent(css + `<svg id="s" xmlns="http://www.w3.org/2000/svg" width="1188" height="2112" viewBox="0 0 1080 1920">${BG[s]()}</svg>`);
    await p.evaluate(() => document.fonts.ready);
    await p.locator('#s').screenshot({ path: f });
  }
  await p.setViewportSize({ width: 1200, height: 1440 });
  for (const [id, expr, talk] of req.persons) {
    const f = path.join(outDir, `t_${id}_${expr}_${talk}.png`); if (fs.existsSync(f)) continue;
    await p.setContent(css + `<svg id="s" xmlns="http://www.w3.org/2000/svg" width="1200" height="1440" viewBox="0 0 600 720">${toonPerson(id, expr, !!talk)}</svg>`);
    await p.evaluate(() => document.fonts.ready);
    await p.locator('#s').screenshot({ path: f, omitBackground: true });
  }
  await b.close();
})();
