const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
(async()=>{
 const tl=JSON.parse(fs.readFileSync('timeline.json','utf8'));
 const mode=process.argv[2]||'preview';
 const browser=await chromium.launch();
 const mk=async()=>{const p=await browser.newPage({viewport:{width:1080,height:1920}});
   p.on('pageerror',e=>console.error('PAGEERR',e.message));
   await p.goto('file://'+path.resolve('render.html'));await p.evaluate(t=>window.setTL(t),tl);
   await p.evaluate(()=>document.fonts.ready);return p};
 if(mode==='preview'){
   fs.mkdirSync('preview',{recursive:true});const p=await mk();
   for(const s of tl.scenes){const f=Math.floor((s.start+s.dur*0.6)*tl.fps);
     await p.evaluate(f=>window.renderFrame(f),f);await p.evaluate(()=>document.fonts.ready);
     await p.screenshot({path:`preview/${s.id}.jpg`,type:'jpeg',quality:70});}
 } else {
   fs.mkdirSync('frames',{recursive:true});const N=tl.frames,P=4;
   await Promise.all([...Array(P)].map(async(_,w)=>{const p=await mk();
     for(let f=w;f<N;f+=P){await p.evaluate(f=>window.renderFrame(f),f);
       await p.screenshot({path:`frames/f${String(f).padStart(5,'0')}.jpg`,type:'jpeg',quality:90});
       if(f%300===0)console.log(f);}}));
 }
 await browser.close();
})();
