const {chromium}=require('playwright');const fs=require('fs');const http=require('http');const path=require('path');
const srv=http.createServer((q,r)=>{fs.readFile(path.join(__dirname,q.url.split('?')[0]),(e,d)=>{r.writeHead(e?404:200,{'Content-Type':q.url.endsWith('.js')?'text/javascript':'text/html'});r.end(d)})}).listen(8124);
(async()=>{const b=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('http://localhost:8124/scene.html');await p.waitForFunction(()=>window.ready);
await p.evaluate(([t,a])=>window.setTL(t,a),[JSON.parse(fs.readFileSync('voice.json')),JSON.parse(fs.readFileSync('amp.json'))]);
for(const f of process.argv.slice(2)){await p.evaluate(f=>window.renderFrame(f),+f);console.log(f,JSON.stringify(await p.evaluate(()=>window.dbg())))}
await b.close();srv.close()})();
