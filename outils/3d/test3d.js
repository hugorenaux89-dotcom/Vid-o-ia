const { lancer, ouvrir, image } = require('./moteur');
(async () => {
  const b = await lancer();
  const t0 = Date.now();
  const p = await ouvrir(b, JSON.parse(process.argv[3] || '{}'), +(process.env.DSF || 1));
  console.log('init', Date.now() - t0, 'ms');
  const t1 = Date.now();
  await image(p, 0, '');
  await p.screenshot({ path: process.argv[2] });
  console.log('image', Date.now() - t1, 'ms');
  await b.close();
})();
