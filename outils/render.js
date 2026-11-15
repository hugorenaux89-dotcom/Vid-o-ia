// Rendu : node outils/render.js <episode> stills <out_dir> t1 t2 ...
//         node outils/render.js <episode> video <out.mp4> [fps] [workers]
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');
const { chromium } = require('playwright');
const ep = require(path.resolve(__dirname, process.argv[2]));
const mode = process.argv[3];
const HTML = `<html><head><link href="https://fonts.googleapis.com/css2?family=Anton&display=block" rel="stylesheet">
<style>body{margin:0;background:#000}</style></head><body><div id="c"></div>
<div style="font-family:Anton;position:absolute;opacity:0">ABC</div></body></html>`;

async function page(b) {
  const p = await b.newPage({ viewport: { width: 720, height: 1280 } });
  await p.setContent(HTML, { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  return p;
}
const draw = (p, svg) => p.evaluate((s) => { document.getElementById('c').innerHTML = s; },
  `<svg xmlns="http://www.w3.org/2000/svg" width="720" height="1280" viewBox="0 0 720 1280">${svg}</svg>`);

(async () => {
  const b = await chromium.launch();
  if (mode === 'stills') {
    const out = process.argv[4]; fs.mkdirSync(out, { recursive: true });
    const p = await page(b);
    for (const ts of process.argv.slice(5)) {
      await draw(p, ep.frameAt(parseFloat(ts)));
      await p.screenshot({ path: `${out}/t${ts}.png` });
    }
  } else {
    const out = process.argv[4], fps = +(process.argv[5] || 30), W = +(process.argv[6] || 4);
    const N = Math.ceil(ep.TL.total * fps);
    const chunk = Math.ceil(N / W);
    const parts = [];
    await Promise.all([...Array(W).keys()].map(async (w) => {
      const p = await page(b);
      const part = `${out}.part${w}.mp4`; parts[w] = part;
      const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', part]);
      for (let i = w * chunk; i < Math.min(N, (w + 1) * chunk); i++) {
        await draw(p, ep.frameAt(i / fps));
        const buf = await p.screenshot({ type: 'jpeg', quality: 95 });
        if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
        if (w === 0 && i % 100 === 0) console.log(`frame ${i}/${chunk}`);
      }
      ff.stdin.end();
      await new Promise((r) => ff.on('close', r));
    }));
    fs.writeFileSync(`${out}.list`, parts.map((p) => `file '${path.resolve(p)}'`).join('\n'));
    await new Promise((r) => spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', `${out}.list`, '-c', 'copy', out]).on('close', r));
    parts.forEach((p) => fs.unlinkSync(p)); fs.unlinkSync(`${out}.list`);
    console.log('vidéo', out, N, 'images');
  }
  await b.close();
})();
