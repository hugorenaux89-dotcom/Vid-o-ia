const {chromium}=require('playwright');const fs=require('fs');const http=require('http');const path=require('path');
const root=__dirname;
const srv=http.createServer((q,r)=>{const f=path.join(root,decodeURIComponent(q.url.split('?')[0]));fs.readFile(f,(e,d)=>{if(e){r.writeHead(404);r.end();return}
 const ext=path.extname(f);r.writeHead(200,{'Content-Type':{'.js':'text/javascript','.html':'text/html','.ttf':'font/ttf','.json':'application/json'}[ext]||'application/octet-stream'});r.end(d)})}).listen(8123);
(async()=>{
 const tl=JSON.parse(fs.readFileSync('voice.json'));const amp=JSON.parse(fs.readFileSync('amp.json'));
 const N=Math.floor(tl.total*30);const mode=process.argv[2]||'preview';const P=+(process.argv[3]||3);
 const b=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
 const mk=async()=>{const p=await b.newPage({viewport:{width:1080,height:1920}});p.on('pageerror',e=>console.error('PAGEERR',e.message));p.on('console',m=>{if(m.type()==='error')console.error('CONSOLE',m.text())});
  await p.goto('http://localhost:8123/scene.html');await p.waitForFunction(()=>window.ready,null,{timeout:60000});await p.evaluate(([t,a])=>window.setTL(t,a),[tl,amp]);await p.evaluate(()=>document.fonts.ready);return p};
 if(mode==='preview'){fs.mkdirSync('preview',{recursive:true});const p=await mk();
  const which=process.argv[4]?process.argv[4].split(','):null;
  for(const pl of tl.plans){if(which&&!which.includes(pl.id))continue;for(const fr of [.3,.75]){const f=Math.floor((pl.start+pl.dur*fr)*30);const t0=Date.now();
   await p.evaluate(f=>window.renderFrame(f),f);await p.screenshot({path:`preview/${pl.id}_${fr}.jpg`,type:'jpeg',quality:75});if(pl.id==='p01'&&fr===.3)console.log('ms/frame',Date.now()-t0)}}
 } else {fs.mkdirSync('frames',{recursive:true});const t0=Date.now();
  await Promise.all([...Array(P)].map(async(_,w)=>{const p=await mk();for(let f=w;f<N;f+=P){const fn=`frames/f${String(f).padStart(5,'0')}.jpg`;if(fs.existsSync(fn))continue;
   await p.evaluate(f=>window.renderFrame(f),f);await p.screenshot({path:fn,type:'jpeg',quality:90});if(f%300===0)console.log(f,((Date.now()-t0)/1000|0)+'s')}}));}
 await b.close();srv.close();
})();
