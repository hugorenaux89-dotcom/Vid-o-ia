// Rendu de l'épisode 3D : node outils/render3d.js stills <dir> t1 t2 ... | video <out.mp4> [workers]
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const { lancer, ouvrir, image } = require('./3d/moteur');
const ep = require('./ep3d');
const DSF = +(process.env.DSF || 1);
(async () => {
  const mode = process.argv[2];
  if (mode === 'stills') {
    const out = process.argv[3]; fs.mkdirSync(out, { recursive: true });
    const b = await lancer(); const p = await ouvrir(b, ep.init(), DSF);
    for (const ts of process.argv.slice(4)) { const T = +ts; await image(p, T, ep.overlay(T)); await p.screenshot({ path: `${out}/t${ts}.png` }); }
    await b.close(); return;
  }
  const out = process.argv[3], W = +(process.argv[4] || 3), fps = 30;
  const N = Math.ceil(ep.TL.total * fps), chunk = Math.ceil(N / W), parts = [];
  const t0 = Date.now();
  await Promise.all([...Array(W).keys()].map(async (w) => {
    const b = await lancer(); const p = await ouvrir(b, ep.init(), DSF);
    const part = `${out}.part${w}.mp4`; parts[w] = part;
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', part]);
    for (let i = w * chunk; i < Math.min(N, (w + 1) * chunk); i++) {
      await image(p, i / fps, ep.overlay(i / fps));
      const buf = await p.screenshot({ type: 'jpeg', quality: 94 });
      if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
      if (w === 0 && (i - w * chunk) % 60 === 0) console.log(`w0 ${i - w * chunk}/${chunk} ${((Date.now() - t0) / 1000).toFixed(0)}s`);
    }
    ff.stdin.end(); await new Promise((r) => ff.on('close', r)); await b.close();
  }));
  fs.writeFileSync(`${out}.list`, parts.map((p) => `file '${path.resolve(p)}'`).join('\n'));
  await new Promise((r) => spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', `${out}.list`, '-c', 'copy', out]).on('close', r));
  parts.forEach((p) => fs.unlinkSync(p)); fs.unlinkSync(`${out}.list`);
  console.log('vidéo', out, N, 'images', ((Date.now() - t0) / 1000).toFixed(0), 's');
})();
