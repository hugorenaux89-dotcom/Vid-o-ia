// Décors « sunburst » (1188x2112) + personnages corps entier (1200x2200) + bustes pour la story
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const { puppet, sunburst, SCENE_COLORS } = require('./puppet');
const { toonPerson } = require('./toon2');
const [,, listFile, outDir] = process.argv;
const req = JSON.parse(fs.readFileSync(listFile));
const css = `<style>@font-face{font-family:Anton;src:url(file:///root/.fonts/Anton-Regular.ttf)}body{margin:0;background:transparent}</style>`;
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1188, height: 2112 } });
  for (const s of req.scenes) {
    const f = path.join(outDir, `bg_${s}.png`); if (fs.existsSync(f)) continue;
    const [c1, c2] = SCENE_COLORS[s] || SCENE_COLORS.rose;
    await p.setViewportSize({ width: 1188, height: 2112 });
    await p.setContent(css + `<svg id="s" xmlns="http://www.w3.org/2000/svg" width="1188" height="2112" viewBox="0 0 1080 1920">${sunburst(c1, c2)}</svg>`);
    await p.locator('#s').screenshot({ path: f });
  }
  await p.setViewportSize({ width: 1200, height: 2200 });
  for (const [id, expr, pose, talk] of req.persons) {
    const f = path.join(outDir, `p_${id}_${expr}_${pose}_${talk}.png`); if (fs.existsSync(f)) continue;
    await p.setContent(css + `<svg id="s" xmlns="http://www.w3.org/2000/svg" width="1200" height="2200" viewBox="0 0 600 1100">${puppet(id, expr, !!talk, pose)}</svg>`);
    await p.evaluate(() => document.fonts.ready);
    await p.locator('#s').screenshot({ path: f, omitBackground: true });
  }
  await p.setViewportSize({ width: 1200, height: 1440 });
  for (const [id, expr] of req.busts || []) {
    const f = path.join(outDir, `t_${id}_${expr}_0.png`); if (fs.existsSync(f)) continue;
    await p.setContent(css + `<svg id="s" xmlns="http://www.w3.org/2000/svg" width="1200" height="1440" viewBox="0 0 600 720">${toonPerson(id, expr, false)}</svg>`);
    await p.locator('#s').screenshot({ path: f, omitBackground: true });
  }
  await b.close();
})();
