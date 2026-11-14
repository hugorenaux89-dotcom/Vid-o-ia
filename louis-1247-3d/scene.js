import * as THREE from 'three';
const W=1080,H=1920,PI=Math.PI;
const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
const ease=x=>{x=clamp(x);return x*x*(3-2*x)};
const easeOut=x=>{x=clamp(x);return 1-Math.pow(1-x,3)};
const lerp=(a,b,k)=>a+(b-a)*k;
const L3=(a,b,k)=>a.map((v,i)=>lerp(v,b[i],k));
const rnd=i=>{let x=Math.sin(i*127.1+311.7)*43758.5453;return x-Math.floor(x)};
const pulse=(t,a,b)=>clamp((t-a)/0.25)*(1-clamp((t-b)/0.25)); // 0->1 between a..b

// ---------------- renderer ----------------
const canvas=document.getElementById('c');
const renderer=new THREE.WebGLRenderer({canvas,antialias:true,preserveDrawingBuffer:true});
renderer.setSize(W,H,false);renderer.setPixelRatio(1);
renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;
renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.0;
const scene=new THREE.Scene();
const camera=new THREE.PerspectiveCamera(40,W/H,0.05,300);

// ---------------- helpers ----------------
const MC={};
function mat(c,o={}){const k=c+JSON.stringify(o);if(MC[k])return MC[k];
  const m=o.basic?new THREE.MeshBasicMaterial({color:c,transparent:!!o.op,opacity:o.op??1,blending:o.add?THREE.AdditiveBlending:THREE.NormalBlending,depthWrite:!o.op,side:THREE.DoubleSide})
   :new THREE.MeshStandardMaterial({color:c,roughness:o.r??0.6,metalness:o.m??0,emissive:o.e??0,emissiveIntensity:o.ei??1,transparent:!!o.op,opacity:o.op??1});
  return MC[k]=m}
function mk(geo,m,p=[0,0,0],s=1,r=[0,0,0],parent,shadow=true){const x=new THREE.Mesh(geo,m);x.position.set(...p);
  if(typeof s==='number')x.scale.setScalar(s);else x.scale.set(...s);if(Array.isArray(r))x.rotation.set(...r);x.castShadow=shadow;x.receiveShadow=true;if(parent)parent.add(x);return x}
const grp=(p=[0,0,0],parent)=>{const g=new THREE.Group();g.position.set(...p);if(parent)parent.add(g);return g};
const SPH=new THREE.SphereGeometry(1,32,24),CYL=new THREE.CylinderGeometry(1,1,1,24),BOX=new THREE.BoxGeometry(1,1,1),CONE=new THREE.ConeGeometry(1,1,24);
const CAPC={};const CAP=(r,l)=>CAPC[r+'_'+l]||(CAPC[r+'_'+l]=new THREE.CapsuleGeometry(r,l,8,16));
const RBOX=(()=>{const g=new THREE.CapsuleGeometry(.5,0,6,12);return g})();

// ---------------- sky ----------------
const skyMat=new THREE.ShaderMaterial({side:THREE.BackSide,depthWrite:false,uniforms:{top:{value:new THREE.Color()},bot:{value:new THREE.Color()}},
 vertexShader:`varying vec3 vp;void main(){vp=normalize(position);gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,
 fragmentShader:`uniform vec3 top;uniform vec3 bot;varying vec3 vp;void main(){float k=smoothstep(-0.05,0.6,vp.y);gl_FragColor=vec4(mix(bot,top,k),1.);}`});
const sky=new THREE.Mesh(new THREE.SphereGeometry(150,32,16),skyMat);scene.add(sky);

// ---------------- lights ----------------
const hemi=new THREE.HemisphereLight(0xffffff,0x444444,1);scene.add(hemi);
const sun=new THREE.DirectionalLight(0xffffff,2.5);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);
Object.assign(sun.shadow.camera,{left:-9,right:9,top:9,bottom:-9,near:.5,far:60});sun.shadow.bias=-0.0004;sun.shadow.normalBias=0.02;
scene.add(sun);scene.add(sun.target);
const fireL=new THREE.PointLight(0xff8a30,0,14,1.6);scene.add(fireL);
const candleL=new THREE.PointLight(0xffb060,0,10,1.5);scene.add(candleL);
const fillL=new THREE.PointLight(0xffe0c0,0,12,1.5);scene.add(fillL);
const sunBall=mk(SPH,mat(0xfff2c0,{basic:true}),[0,0,0],3,0,scene,false);
const moon=mk(SPH,mat(0xf4ecc8,{basic:true}),[-20,40,-90],4,0,scene,false);
function preset(n){
  const P={
   hutDay:{top:0x3a2a1c,bot:0x3a2a1c,hs:0xffe6c8,hg:0x4a3424,hi:.7,sc:0xffd9a0,si:2.4,sp:[5,7,4],fire:0,fog:null,exp:1.05},
   hutNight:{top:0x120c18,bot:0x120c18,hs:0x7a80b0,hg:0x2a1a14,hi:.6,sc:0x8090ff,si:.35,sp:[3,8,4],fire:45,fill:4,fog:null,exp:1.1},
   dawn:{top:0x7fb0e0,bot:0xffb07a,hs:0xffd9b0,hg:0x6a5038,hi:.9,sc:0xffb070,si:2.6,sp:[8,4,-6],fire:0,fog:[0xffc896,18,70],exp:1.0,sun:[30,10,-60]},
   day:{top:0x3d8fe0,bot:0xcbe9ff,hs:0xdff0ff,hg:0x8a7040,hi:1.0,sc:0xfff4dc,si:3.0,sp:[6,10,5],fire:0,fog:[0xcbe9ff,25,90],exp:1.0,sun:[30,45,-60]},
   noon:{top:0x3d8fe0,bot:0xcbe9ff,hs:0xdff0ff,hg:0x8a7040,hi:1.0,sc:0xfff8e8,si:3.2,sp:[2,12,3],fire:0,fog:[0xcbe9ff,25,90],exp:1.0,sun:[10,60,-40]},
   pm:{top:0x5a7fd0,bot:0xffb27a,hs:0xffd8b0,hg:0x7a5838,hi:.9,sc:0xffa860,si:2.8,sp:[-8,5,4],fire:0,fog:[0xffc090,20,80],exp:1.0,sun:[-40,14,-60]},
   barber:{top:0x1a120e,bot:0x1a120e,hs:0x8a7060,hg:0x201410,hi:.35,sc:0xffc080,si:.6,sp:[2,6,6],fire:0,candle:22,fog:null,exp:1.15},
   night:{top:0x0a0c2a,bot:0x2a2050,hs:0x5060a0,hg:0x101020,hi:.45,sc:0x9fb0ff,si:.7,sp:[-6,9,4],fire:0,fog:[0x1a1838,20,70],exp:1.2},
  }[n];
  skyMat.uniforms.top.value.set(P.top);skyMat.uniforms.bot.value.set(P.bot);
  hemi.color.set(P.hs);hemi.groundColor.set(P.hg);hemi.intensity=P.hi;
  sun.color.set(P.sc);sun.intensity=P.si;sun.position.set(...P.sp);sun.target.position.set(0,0,0);
  fireL.intensity=P.fire;candleL.intensity=P.candle||0;fillL.intensity=P.fill||0;fillL.position.set(0,3,3);
  scene.fog=P.fog?new THREE.Fog(P.fog[0],P.fog[1],P.fog[2]):null;
  renderer.toneMappingExposure=P.exp;
  sunBall.visible=!!P.sun;if(P.sun)sunBall.position.set(...P.sun);
  moon.visible=n==='night';
  return P;
}

// ---------------- LOUIS ----------------
function makeLouis(){
  const L={};const root=grp([0,0,0],scene);L.root=root;const body=grp([0,0,0],root);L.body=body;
  const skin=mat(0xf6cfae,{r:.5}),red=mat(0xd23f4b,{r:.5}),dred=mat(0x8e1f2a,{r:.6}),white=mat(0xf6f6f8,{r:.6}),pants=mat(0x2f2d3a,{r:.7}),
   shoe=mat(0xf4f4f8,{r:.35}),hair=mat(0xd9b062,{r:.45}),hair2=mat(0xe9c87e,{r:.45}),green=mat(0x4f8a3f,{r:.3}),blk=mat(0x111111,{r:.2}),
   gl=mat(0xffffff,{e:0xffffff,ei:1}),pink=mat(0xf08a90,{r:.6}),mouthM=mat(0x6e1a22,{r:.6}),brow=mat(0x9a6a35,{r:.6}),skinD=mat(0xe8b08e,{r:.5});
  L.legs=[];
  [-1,1].forEach(s=>{const lg=grp([s*.11,.86,0],body);mk(CAP(.085,.6),pants,[0,-.39,0],1,0,lg);mk(SPH,shoe,[0,-.8,.05],[.115,.075,.2],0,lg);L.legs.push(lg)});
  const hips=grp([0,.86,0],body);L.hips=hips;
  mk(CAP(.215,.36),red,[0,.34,0],[1,1,.78],0,hips);
  mk(BOX,white,[0,.36,.15],[.14,.56,.05],0,hips);
  mk(CYL,dred,[0,.06,0],[.22,.07,.175],0,hips);
  [-1,1].forEach(s=>mk(BOX,dred,[s*.085,.6,.15],[.07,.15,.03],[0,0,s*.5],hips));
  mk(CYL,skinD,[0,.66,0],[.07,.12,.07],0,hips);
  const head=grp([0,.68,0],hips);L.head=head;
  mk(SPH,skin,[0,.3,0],[.3,.31,.28],0,head);
  const capG=new THREE.SphereGeometry(1,32,16,0,PI*2,0,1.2);
  mk(capG,hair,[0,.34,-.03],[.318,.33,.305],[-.3,0,0],head);
  mk(SPH,hair2,[.05,.57,.1],[.21,.075,.15],[.35,0,-.35],head);
  mk(SPH,hair,[-.1,.56,.08],[.17,.08,.15],[.25,0,.35],head);
  [-1,1].forEach(s=>mk(SPH,skin,[s*.29,.29,0],[.055,.08,.05],0,head));
  L.eyes=[];L.lids=[];L.irises=[];L.brows=[];
  const lidG=new THREE.SphereGeometry(1,24,12,0,PI*2,0,PI/2);
  [-1,1].forEach(s=>{const eg=grp([s*.11,.33,.215],head);eg.scale.z=.6;
    mk(SPH,white,[0,0,0],.088,0,eg,false);
    const ir=grp([0,0,0],eg);mk(SPH,green,[0,0,.068],[.052,.052,.03],0,ir,false);mk(SPH,blk,[0,0,.088],[.027,.027,.015],0,ir,false);mk(SPH,gl,[.018,.022,.1],.011,0,ir,false);
    const lid=mk(lidG,skin,[0,0,0],.094,[-1.3,0,0],eg,false);
    const bg=grp([s*.11,.455,.255],head);mk(CAP(.019,.09),brow,[0,0,0],1,[0,0,PI/2],bg,false);
    L.eyes.push(eg);L.lids.push(lid);L.irises.push(ir);L.brows.push(bg)});
  mk(SPH,skinD,[0,.245,.285],[.036,.032,.03],0,head,false);
  [-1,1].forEach(s=>mk(SPH,pink,[s*.19,.2,.215],[.06,.035,.03],[0,s*.6,0],head,false));
  const mo=grp([0,.15,.262],head);L.mouth=mo;
  L.mOpen=mk(SPH,mat(0x4a0f16,{r:.8}),[0,0,-.012],[.07,.04,.012],0,mo,false);
  L.mTeeth=mk(BOX,white,[0,.022,-.004],[.07,.016,.01],0,mo,false);
  L.mSmile=mk(new THREE.TorusGeometry(.065,.014,8,24,PI),mouthM,[0,.03,0],1,[0,0,PI],mo,false);
  L.mFlat=mk(CAP(.012,.08),mouthM,[0,0,0],1,[0,0,PI/2],mo,false);
  L.mFrown=mk(new THREE.TorusGeometry(.05,.013,8,24,PI),mouthM,[0,-.03,0],1,[0,0,0],mo,false);
  L.mO=mk(SPH,mouthM,[0,-.01,0],[.035,.05,.02],0,mo,false);
  L.sweat=mk(SPH,mat(0x8fd3ff,{r:.1}),[.27,.48,.12],[.03,.045,.03],0,head,false);
  L.arms=[];
  [-1,1].forEach(s=>{const sh=grp([s*.25,.56,0],hips);mk(CAP(.074,.26),red,[0,-.18,0],1,0,sh);
    const el=grp([0,-.37,0],sh);mk(CAP(.07,.2),red,[0,-.14,0],1,0,el);mk(CYL,dred,[0,-.29,0],[.078,.05,.078],0,el);
    mk(SPH,skin,[0,-.37,0],.078,0,el);const hold=grp([0,-.42,0],el);
    L.arms.push({sh,el,hold})});
  return L;
}
const EXPR={
 happy:{by:0,br:.08,lid:.12,m:'smile',ps:1},
 shock:{by:.05,br:-.05,lid:0,m:'O',ps:.75,es:1.12},
 blank:{by:-.01,br:0,lid:.5,m:'flat',ps:1},
 worried:{by:.02,br:-.35,lid:.15,m:'frown',ps:1},
 tired:{by:-.01,br:-.1,lid:.55,m:'flat',ps:1},
 sleep:{by:-.01,br:0,lid:1,m:'flat',ps:1},
 proud:{by:.03,br:.15,lid:.3,m:'smile',ps:1},
 angry:{by:-.02,br:.35,lid:.25,m:'frown',ps:1},
 sly:{by:.02,br:.2,lid:.35,m:'smile',ps:1},
};
function poseLouis(L,p){
  L.root.visible=p.vis!==false;if(p.vis===false)return;
  L.root.position.set(p.x||0,p.y||0,p.z||0);L.root.rotation.set(0,p.ry||0,0);L.root.scale.setScalar(p.s||1);
  const lie=p.lie||0;L.body.rotation.set(-PI/2*lie,0,0);L.body.position.set(0,.13*lie+(p.jump||0),0);
  const breath=Math.sin((p.t||0)*2.2)*.012;
  L.hips.rotation.set((p.bow||0)+(p.sit||0)*PI/2*lie,p.twist||0,p.lean||0);
  L.hips.position.y=.86+breath*.3;
  const h=p.head||[0,0,0],talk=(p.open||0);
  L.head.rotation.set(h[0]+talk*.06*Math.sin((p.t||0)*9),h[1],h[2]);
  // legs
  const lg=p.legs||[0,0];L.legs[0].rotation.set(lg[0],0,0);L.legs[1].rotation.set(lg[1],0,0);
  // arms [x,z], elbow
  const aL=p.armL||[0,0],aR=p.armR||[0,0];
  L.arms[0].sh.rotation.set(aL[0],0,-.1+aL[1]);L.arms[1].sh.rotation.set(aR[0],0,.1+aR[1]);
  L.arms[0].el.rotation.set(-(p.elL||.15),0,0);L.arms[1].el.rotation.set(-(p.elR||.15),0,0);
  L.arms.forEach(a=>{a.hold.clear()});
  if(p.holdL)L.arms[0].hold.add(p.holdL);if(p.holdR)L.arms[1].hold.add(p.holdR);
  // face
  const E=EXPR[p.expr||'happy'];
  L.brows.forEach((b,i)=>{const s=i?1:-1;b.position.y=.455+E.by+(p.browUp||0);b.rotation.z=-s*E.br});
  const blink=p.blink?1:0;
  L.lids.forEach((l,i)=>{let c=Math.max(E.lid,blink);if(p.wink&&i===1)c=1;l.rotation.x=lerp(-1.35,1.45,c)});
  L.eyes.forEach(e=>{const k=E.es||1;e.scale.set(k,k,.6*k)});
  const lk=p.look||[0,0];L.irises.forEach(r=>{r.position.set(lk[0]*.025,lk[1]*.02,0);r.scale.setScalar(1);r.children[1].scale.set(.027*E.ps,.027*E.ps,.015)});
  const op=clamp(talk*1.2);
  [L.mOpen,L.mTeeth,L.mSmile,L.mFlat,L.mFrown,L.mO].forEach(m=>m.visible=false);
  if(op>.12){L.mOpen.visible=L.mTeeth.visible=true;L.mOpen.scale.set(E.m==='O'?.05:.065,.012+op*.045,.012);}
  else ({smile:L.mSmile,flat:L.mFlat,frown:L.mFrown,O:L.mO})[E.m].visible=true;
  L.sweat.visible=!!p.sweat;if(p.sweat)L.sweat.position.y=.48-((p.t||0)*.15%.12);
}

// ---------------- other characters ----------------
const C={pink:mat(0xf3a0b4,{r:.55}),pinkD:mat(0xe07e97,{r:.55}),blk:mat(0x151010,{r:.2}),wht:mat(0xffffff,{e:0xffffff})};
function makePig(){const g=grp([0,0,0],scene);const b=grp([0,0,0],g);
  mk(SPH,C.pink,[0,.45,0],[.55,.38,.4],0,b);
  const hd=grp([.5,.55,0],b);mk(SPH,C.pink,[0,0,0],.28,0,hd);mk(CYL,C.pinkD,[.27,-.03,0],[.11,.1,.11],[0,0,PI/2],hd);
  [-1,1].forEach(s=>{mk(SPH,C.blk,[.33,-.02,s*.04],.022,0,hd,false);mk(SPH,C.blk,[.18,.1,s*.12],.035,0,hd,false);mk(SPH,C.wht,[.205,.115,s*.12],.01,0,hd,false);
    mk(CONE,C.pinkD,[-.02,.26,s*.13],[.08,.16,.05],[0,0,s*0+.3],hd)});
  [[.3,.2],[.3,-.2],[-.3,.2],[-.3,-.2]].forEach(([x,z])=>mk(CYL,C.pinkD,[x,.14,z],[.07,.28,.07],0,b));
  mk(new THREE.TorusGeometry(.06,.018,8,16),C.pinkD,[-.56,.55,0],1,[0,PI/2,0],b);
  return {g,b,hd}}
function makeOx(){const g=grp([0,0,0],scene);const br=mat(0x8a5631,{r:.7}),bd=mat(0x6b4226,{r:.7}),cr=mat(0xf2e6d6,{r:.5});
  mk(SPH,br,[0,1.0,0],[.95,.55,.5],0,g);mk(SPH,cr,[-.1,1.1,.35],[.3,.2,.2],0,g);
  const legs=[];[[.55,.3],[.55,-.3],[-.55,.3],[-.55,-.3]].forEach(([x,z])=>{const l=grp([x,.75,z],g);mk(CAP(.1,.55),bd,[0,-.35,0],1,0,l);legs.push(l)});
  const hd=grp([1.0,1.15,0],g);mk(SPH,br,[0,0,0],[.33,.3,.3],0,hd);mk(SPH,mat(0xc7967a,{r:.6}),[.25,-.1,0],[.16,.14,.2],0,hd);
  [-1,1].forEach(s=>{mk(CONE,cr,[0,.28,s*.25],[.05,.3,.05],[s*-.9,0,0],hd);mk(SPH,C.blk,[.22,.07,s*.15],.04,0,hd,false);mk(SPH,mat(0x2a1610),[.2,.13,s*.14],[.06,.015,.03],[0,0,s*.3],hd,false)});
  return {g,hd,legs}}
function makeLord(){const g=grp([0,0,0],scene);const wh=mat(0xf2ede4,{r:.5}),whd=mat(0xd9cfbe,{r:.6});
  const horse=grp([0,0,0],g);mk(SPH,wh,[0,1.35,0],[.95,.42,.4],0,horse);
  const nk=grp([.75,1.55,0],horse);mk(CAP(.2,.6),wh,[.15,.3,0],1,[0,0,-.55],nk);mk(SPH,wh,[.45,.7,0],[.36,.18,.18],[0,0,-.3],nk);mk(SPH,C.blk,[.5,.8,.15],.035,0,nk,false);mk(SPH,C.blk,[.5,.8,-.15],.035,0,nk,false);
  mk(BOX,whd,[.1,.6,0],[.5,.1,.1],[0,0,-.6],nk);
  const legs=[];[[.6,.22],[.6,-.22],[-.6,.22],[-.6,-.22]].forEach(([x,z])=>{const l=grp([x,1.1,z],horse);mk(CAP(.08,.85),whd,[0,-.5,0],1,0,l);legs.push(l)});
  mk(CAP(.06,.5),whd,[-1.0,1.25,0],1,[0,0,-.5],horse);
  mk(BOX,mat(0x7a1f2e,{r:.6}),[0,1.72,0],[.8,.1,.85],0,horse);mk(BOX,mat(0xe8b84a,{m:.6,r:.3}),[0,1.66,0],[.82,.04,.87],0,horse);
  const lord=grp([0,1.75,0],horse);const robe=mat(0xa3203a,{r:.5}),gold=mat(0xf2c94c,{m:.7,r:.3}),skin=mat(0xf0c6a2,{r:.5});
  mk(new THREE.CylinderGeometry(.2,.36,.85,24),robe,[0,.42,0],1,0,lord);mk(CYL,gold,[0,.3,0],[.3,.05,.3],0,lord);
  const lh=grp([0,.85,0],lord);mk(SPH,skin,[0,.22,0],.24,0,lh);mk(SPH,mat(0x4a2a1a),[0,.06,.12],[.17,.1,.12],0,lh);
  mk(new THREE.CylinderGeometry(.2,.2,.12,24,1,true),gold,[0,.44,0],1,0,lh);for(let i=0;i<6;i++){const a=i/6*PI*2;mk(CONE,gold,[Math.cos(a)*.2,.55,Math.sin(a)*.2],[.04,.12,.04],0,lh)}
  [-1,1].forEach(s=>{mk(SPH,C.blk,[s*.08,.26,.21],.03,0,lh,false);mk(CAP(.016,.07),mat(0x3a2a1a),[s*.08,.33,.21],1,[0,0,PI/2+s*.4],lh,false)});
  mk(CAP(.012,.08),mat(0x6a2a1a),[0,.15,.235],1,[0,0,PI/2],lh,false);
  [-1,1].forEach(s=>mk(CAP(.07,.4),robe,[s*.27,.55,.08],1,[-.6,0,s*.15],lord));
  return {g,horse,legs,nk}}
function makeGuard(){const g=grp([0,0,0],scene);const ar=mat(0x8a8f99,{m:.6,r:.35}),tun=mat(0x3a4a7a,{r:.6}),skin=mat(0xf0c6a2);
  mk(CAP(.09,.6),mat(0x3a3036),[-.1,.4,0],1,0,g);mk(CAP(.09,.6),mat(0x3a3036),[.1,.4,0],1,0,g);
  mk(CAP(.24,.45),tun,[0,1.15,0],[1,1,.8],0,g);mk(SPH,skin,[0,1.72,0],.22,0,g);mk(CONE,ar,[0,1.98,0],[.25,.35,.25],0,g);
  [-1,1].forEach(s=>mk(SPH,C.blk,[s*.07,1.75,.19],.025,0,g,false));
  const sp=grp([.33,1.1,0],g);mk(CYL,mat(0x6b4729),[0,.4,0],[.025,2.2,.025],0,sp);mk(CONE,ar,[0,1.6,0],[.06,.25,.06],0,sp);
  return {g}}
function makeBarber(){const g=grp([0,0,0],scene);const robe=mat(0x5a4636,{r:.7}),skin=mat(0xf0c6a2,{r:.5}),apr=mat(0xe8e0d0,{r:.7});
  mk(CAP(.1,.6),mat(0x3a2e28),[-.12,.4,0],1,0,g);mk(CAP(.1,.6),mat(0x3a2e28),[.12,.4,0],1,0,g);
  mk(CAP(.32,.55),robe,[0,1.2,0],[1,1,.85],0,g);mk(BOX,apr,[0,1.05,.25],[.42,.7,.04],0,g);
  const hd=grp([0,1.78,0],g);mk(SPH,skin,[0,.05,0],.27,0,hd);mk(new THREE.TorusGeometry(.2,.06,8,24,PI),mat(0x777777),[0,0,-.05],1,[0,0,0],hd);
  [-1,1].forEach(s=>{mk(SPH,mat(0x2e2018),[s*.08,-.06,.24],[.1,.04,.05],[0,0,s*.3],hd,false);mk(SPH,C.blk,[s*.09,.08,.24],.03,0,hd,false);mk(SPH,C.wht,[s*.09+.01,.09,.265],.009,0,hd,false);mk(CAP(.02,.07),mat(0x666666),[s*.09,.16,.24],1,[0,0,PI/2-s*.2],hd,false)});
  mk(SPH,mat(0xe0a888),[0,0,.27],[.05,.04,.04],0,hd,false);
  mk(new THREE.TorusGeometry(.06,.014,8,16,PI),mat(0x7a3a2a),[0,-.13,.24],1,[0,0,PI],hd,false);
  const arm=grp([.33,1.5,0],g);mk(CAP(.08,.5),robe,[0,-.3,0],1,0,arm);mk(SPH,skin,[0,-.62,0],.085,0,arm);const hold=grp([0,-.68,0],arm);
  const arm2=grp([-.33,1.5,0],g);mk(CAP(.08,.5),robe,[0,-.3,0],1,0,arm2);mk(SPH,skin,[0,-.62,0],.085,0,arm2);
  return {g,hd,arm,hold,arm2}}
function makePeasant(tunic,hairC,sc){const g=grp([0,0,0],scene);const b=grp([0,0,0],g);const skin=mat(0xeec4a0);
  mk(CAP(.24,.55),mat(tunic,{r:.8}),[0,.75,0],[1,1,.85],0,b);mk(SPH,skin,[0,1.35,0],.22,0,b);mk(SPH,mat(hairC),[0,1.42,-.04],[.23,.2,.22],0,b);
  [-1,1].forEach(s=>mk(CAP(.012,.04),C.blk,[s*.07,1.36,.2],1,[0,0,PI/2],b,false));
  g.scale.setScalar(sc);return {g,b}}
function makeChicken(){const g=grp([0,0,0],scene);const w=mat(0xf7f3ea,{r:.6});mk(SPH,w,[0,.22,0],[.18,.15,.14],0,g);
  const hd=grp([.15,.38,0],g);mk(SPH,w,[0,0,0],.08,0,hd);mk(SPH,mat(0xd93b3b),[0,.08,0],[.04,.04,.015],0,hd);mk(CONE,mat(0xf2b233),[.09,0,0],[.025,.06,.025],[0,0,-PI/2],hd);
  mk(SPH,C.blk,[.05,.02,.05],.013,0,hd,false);mk(SPH,C.blk,[.05,.02,-.05],.013,0,hd,false);
  mk(CYL,mat(0xf2b233),[0,.05,.04],[.01,.12,.01],0,g);mk(CYL,mat(0xf2b233),[0,.05,-.04],[.01,.12,.01],0,g);return {g,hd}}
function makeGoat(){const g=grp([0,0,0],scene);const w=mat(0xd8d2c4,{r:.8});mk(SPH,w,[0,.5,0],[.45,.28,.26],0,g);mk(SPH,w,[.45,.7,0],[.16,.14,.12],0,g);
  [-1,1].forEach(s=>mk(CONE,mat(0x6a5a4a),[.42,.86,s*.06],[.03,.16,.03],[s*-.3,0,-.4],g));
  [[.25,.12],[.25,-.12],[-.25,.12],[-.25,-.12]].forEach(([x,z])=>mk(CYL,w,[x,.2,z],[.04,.4,.04],0,g));return {g}}

// props
const P={};
function mkProp(build){const g=new THREE.Group();build(g);return g}
P.bucket=()=>mkProp(g=>{const w=mat(0x7b5534,{r:.8});mk(new THREE.CylinderGeometry(.13,.1,.22,20),w,[0,-.14,0],1,0,g);mk(new THREE.TorusGeometry(.13,.01,6,20,PI),mat(0x4a3220),[0,-.03,0],1,0,g)});
P.bucketW=()=>mkProp(g=>{g.add(P.bucket());mk(CYL,mat(0x7fc4ea,{r:.1}),[0,-.05,0],[.12,.01,.12],0,g)});
P.mug=()=>mkProp(g=>{mk(new THREE.CylinderGeometry(.06,.055,.14,16),mat(0x8a5a2b,{r:.7}),[0,-.02,.06],1,0,g);mk(CYL,mat(0xf2d48a),[0,.05,.06],[.055,.01,.055],0,g)});
P.bread=()=>mkProp(g=>{mk(SPH,mat(0x5c3b22,{r:.9}),[0,0,.06],[.12,.07,.09],0,g)});
P.straw=()=>mkProp(g=>{for(let i=0;i<14;i++)mk(CYL,mat(0xd8b45a),[(rnd(i)-.5)*.08,0,.06],[.006,.25,.006],[(rnd(i+3)-.5)*.6,0,(rnd(i+7)-.5)*.6],g,false)});
P.sickle=()=>mkProp(g=>{mk(CYL,mat(0x7b5534),[0,0,.05],[.025,.25,.025],[PI/2,0,0],g);mk(new THREE.TorusGeometry(.14,.015,6,20,PI*1.1),mat(0xb8c0c8,{m:.8,r:.25}),[0,.12,.2],1,[0,PI/2,0],g)});
P.pitchfork=()=>mkProp(g=>{mk(CYL,mat(0x7b5534),[0,.3,.05],[.025,1.6,.025],0,g);for(let i=-1;i<=1;i++)mk(CYL,mat(0x9aa0a8,{m:.7}),[i*.06,1.2,.05],[.01,.25,.01],0,g)});
P.sack=()=>mkProp(g=>{mk(SPH,mat(0xc9b07a,{r:.9}),[0,0,0],[.25,.3,.22],0,g);mk(CYL,mat(0x8a6a3a),[0,.28,0],[.06,.08,.06],0,g)});
P.pliers=()=>mkProp(g=>{[-1,1].forEach(s=>mk(BOX,mat(0x6d6f73,{m:.8,r:.3}),[s*.02,-.12,0],[.02,.3,.02],[0,0,s*.12],g))});
P.honey=()=>mkProp(g=>{mk(new THREE.CylinderGeometry(.08,.07,.16,16),mat(0xd8962b,{r:.25}),[0,-.06,0],1,0,g);mk(CYL,mat(0xb58847),[0,.03,0],[.085,.03,.085],0,g)});
P.bowlBlade=()=>mkProp(g=>{mk(new THREE.SphereGeometry(.1,16,8,0,PI*2,PI/2,PI/2),mat(0x8d6748,{r:.7}),[0,-.02,.08],1,0,g);mk(BOX,mat(0xc8d0d8,{m:.9,r:.2}),[0,.05,-.05],[.02,.2,.04],[0,0,.3],g)});
P.finger=null;

// ---------------- environments ----------------
const ENV={};
function env(name,build){const g=grp([0,0,0],scene);build(g);g.visible=false;ENV[name]=g;return g}
const woodA=mat(0x523727,{r:.85}),woodB=mat(0x4a3122,{r:.85}),dirt=mat(0x5e4630,{r:.95}),strawM=mat(0xd8b45a,{r:.9}),strawD=mat(0xb8923a,{r:.9}),stone=mat(0x8a8a88,{r:.9});
function hutShell(g){
  mk(BOX,dirt,[0,-.05,0],[14,.1,14],0,g);
  for(let i=0;i<24;i++){mk(BOX,i%2?woodA:woodB,[-6+i*.52,2.2,-3.2],[.5,4.4,.15],0,g);}
  for(let i=0;i<14;i++){mk(BOX,i%2?woodA:woodB,[-4.2,2.2,-3+i*.52],[.15,4.4,.5],0,g);mk(BOX,i%2?woodA:woodB,[4.2,2.2,-3+i*.52],[.15,4.4,.5],0,g)}
  mk(BOX,mat(0x3b281c),[0,4.3,-1],[9,.25,.25],0,g);mk(BOX,mat(0x3b281c),[0,4.3,1],[9,.25,.25],0,g);
  // straw bed
  mk(CYL,strawM,[0,.07,0],[1.25,.14,1],0,g);
  for(let i=0;i<70;i++){const a=rnd(i)*PI*2,r=Math.sqrt(rnd(i+9))*1.2;mk(CYL,i%2?strawM:strawD,[Math.cos(a)*r,.15,Math.sin(a)*r*.8],[.01,.35,.01],[PI/2+(rnd(i+3)-.5)*.5,0,rnd(i+4)*PI],g,false)}
  // fire pit
  const fp=grp([2.4,0,-1.6],g);for(let i=0;i<9;i++){const a=i/9*PI*2;mk(SPH,stone,[Math.cos(a)*.45,.08,Math.sin(a)*.45],[.14,.1,.12],0,fp)}
  mk(CYL,mat(0x5a3a22),[0,.1,0],[.05,.6,.05],[0,0,PI/2.3],fp);mk(CYL,mat(0x5a3a22),[0,.1,0],[.05,.6,.05],[PI/2.3,0,0],fp);
  g.userData.flames=[];[[0,.55,0xff7a1a,.18],[.1,.45,0xffa630,.14],[-.1,.42,0xff7a1a,.13],[0,.3,0xffe066,.1]].forEach(([x,h,c,r],i)=>{const f=mk(CONE,mat(c,{e:c,ei:2.5,r:1}),[x,h/2+.1,0],[r,h,r],0,fp,false);f.userData={h,r,i};g.userData.flames.push(f)});
  g.userData.fire=fp;
  // table with bowl & bread
  const tb=grp([-2.4,0,-1.5],g);mk(BOX,mat(0x6b4729),[0,.78,0],[1.6,.08,.8],0,tb);[[-.7,-.3],[.7,-.3],[-.7,.3],[.7,.3]].forEach(([x,z])=>mk(BOX,mat(0x5a3b22),[x,.38,z],[.08,.76,.08],0,tb));
  mk(new THREE.SphereGeometry(.16,16,8,0,PI*2,PI/2,PI/2),mat(0x8d6748),[-.2,.98,0],1,[PI,0,0],tb);mk(CYL,mat(0xb7aa8d),[-.2,.96,0],[.15,.01,.15],0,tb);
  mk(SPH,mat(0x5c3b22,{r:.9}),[.35,.88,.05],[.18,.09,.13],0,tb);g.userData.table=tb;
  // light shafts + slits (day)
  const sh=grp([0,0,0],g);g.userData.shafts=sh;
  [-2.6,-.4,1.6].forEach((x,i)=>{mk(BOX,mat(0xffe2a0,{e:0xffd890,ei:3}),[x,2.4,-3.12],[.04,3.6,.02],0,sh,false);
    const pl=mk(new THREE.PlaneGeometry(.9,7),mat(0xffd27a,{basic:true,op:.09,add:true}),[x+.5,2.3,-1.4],1,[-.9,0,.35],sh,false);});
  for(let i=0;i<40;i++){const d=mk(SPH,mat(0xffe7a8,{basic:true,op:.6,add:true}),[(rnd(i)-.5)*6,rnd(i+1)*3.5,(rnd(i+2)-.5)*3],.012,0,sh,false);d.userData.dust=i}
}
env('hut',hutShell);
const thatch=mat(0xc7a14e,{r:.95}),plaster=mat(0xd8c4a0,{r:.9}),beam=mat(0x5a3b22,{r:.8});
function house(g,x,z,s,ry=0){const h=grp([x,0,z],g);h.rotation.y=ry;h.scale.setScalar(s);mk(BOX,plaster,[0,1,0],[2.4,2,2],0,h);
  mk(new THREE.ConeGeometry(1.95,1.6,4),thatch,[0,2.75,0],[1,1,.85],[0,PI/4,0],h);mk(BOX,beam,[0,.6,1.01],[.5,1.2,.03],0,h);
  [-1,1].forEach(s=>{mk(BOX,beam,[s*1.2,1,1.01],[.08,2,.03],0,h)});mk(BOX,beam,[0,2,1.01],[2.4,.08,.03],0,h);
  const win=mk(BOX,mat(0x2a1a10,{e:0xffa040,ei:0}),[.75,1.2,1.01],[.4,.35,.03],0,h);h.userData.win=win;return h}
const houses=[];
env('village',g=>{mk(BOX,mat(0x6e5236,{r:.95}),[0,-.05,0],[80,.1,80],0,g);mk(BOX,mat(0x7a9a4a,{r:.95}),[0,-.04,-20],[80,.1,30],0,g);
  [[-5,-6,1.2,.3],[0,-9,1.4,0],[5.5,-6.5,1.2,-.4],[-9,-3,1,.8],[9,-2,1.1,-.9],[-3,-16,1.3,0],[7,-14,1.2,-.2]].forEach(a=>houses.push(house(g,...a)));
  for(let i=0;i<10;i++){const x=-14+i*3.2,z=-22+rnd(i)*4;mk(CYL,mat(0x5a3b22),[x,1,z],[.18,2,.18],0,g);mk(SPH,mat(0x4f7a3a,{r:.9}),[x,2.6,z],[1.2,1.3,1.2],0,g)}
  for(let i=0;i<14;i++)mk(CYL,beam,[-7+i*.6,.4,2.8],[.05,.8,.05],0,g);mk(BOX,beam,[-3.1,.6,2.8],[8.4,.06,.04],0,g);
  // well
  const w=grp([-1.6,0,-1.2],g);mk(new THREE.CylinderGeometry(.6,.65,.8,20),stone,[0,.4,0],1,0,w);mk(CYL,mat(0x223040,{r:.1}),[0,.79,0],[.5,.02,.5],0,w);
  [-1,1].forEach(s=>mk(BOX,beam,[s*.55,1.2,0],[.08,1.6,.08],0,w));mk(new THREE.ConeGeometry(.9,.6,4),mat(0x8a3a2a,{r:.8}),[0,2.2,0],[1,1,.7],[0,PI/4,0],w);
  mk(CYL,beam,[0,1.6,0],[.05,1.1,.05],[0,0,PI/2],w);g.userData.well=w;
});
// fields
function wheatField(g,n,area,cx,cz,h,col){
  const stalk=new THREE.InstancedMesh(new THREE.CylinderGeometry(.012,.015,1,5),mat(0xc99a2e,{r:.9}),n);
  const head=new THREE.InstancedMesh(new THREE.SphereGeometry(1,8,6),mat(col,{r:.8}),n);
  stalk.castShadow=head.castShadow=true;stalk.receiveShadow=head.receiveShadow=true;g.add(stalk);g.add(head);
  const pts=[];for(let i=0;i<n;i++){let x,z;do{x=cx+(rnd(i*3)-.5)*area[0];z=cz+(rnd(i*3+1)-.5)*area[1]}while(Math.abs(x)<.7&&Math.abs(z)<.7&&false);pts.push([x,z,h*(.8+rnd(i*3+2)*.4),rnd(i)*6])}
  g.userData.wheat=(g.userData.wheat||[]).concat([{stalk,head,pts}]);
}
function updWheat(g,t){if(!g.userData.wheat)return;const m=new THREE.Matrix4(),q=new THREE.Quaternion(),e=new THREE.Euler(),v=new THREE.Vector3(),s=new THREE.Vector3();
  g.userData.wheat.forEach(({stalk,head,pts})=>{pts.forEach(([x,z,h,ph],i)=>{const sw=Math.sin(t*1.8+ph+x*.4)*.12;e.set(0,0,sw);q.setFromEuler(e);
    v.set(x+Math.sin(sw)*-h/2,h/2*Math.cos(sw),z);s.set(1,h,1);m.compose(v,q,s);stalk.setMatrixAt(i,m);
    v.set(x-Math.sin(sw)*h,h*Math.cos(sw)+.06,z);s.set(.035,.09,.035);m.compose(v,q,s);head.setMatrixAt(i,m)});
    stalk.instanceMatrix.needsUpdate=head.instanceMatrix.needsUpdate=true})}
env('plow',g=>{mk(BOX,mat(0x7a5434,{r:.95}),[0,-.05,0],[80,.1,80],0,g);for(let i=0;i<30;i++)mk(BOX,mat(0x5e3e24,{r:.95}),[0,.02,-20+i*1.1],[60,.08,.35],0,g);
  [[-20,-40,14],[10,-45,18],[35,-38,12]].forEach(([x,z,r])=>mk(SPH,mat(0x7d9a52,{r:.95}),[x,-r*.6,z],r,0,g));
  [[-6,-12],[ -9,-14],[8,-16]].forEach(([x,z])=>house(g,x,z,1));
  const pl=grp([0,0,0],g);mk(BOX,beam,[0,.35,0],[1.2,.06,.06],[0,0,-.3],pl);mk(BOX,mat(0x9aa0a8,{m:.6}),[-.5,.1,0],[.3,.15,.05],0,pl);mk(BOX,beam,[.55,.6,.0],[.06,.5,.4],0,pl);g.userData.plow=pl;});
env('wheat',g=>{mk(BOX,mat(0xc9973a,{r:.95}),[0,-.05,0],[80,.1,80],0,g);
  [[-20,-40,14],[10,-45,18],[35,-38,12]].forEach(([x,z,r])=>mk(SPH,mat(0x9aaa52,{r:.95}),[x,-r*.6,z],r,0,g));
  for(let i=0;i<6;i++){const x=-16+i*7,z=-28-rnd(i)*5;mk(CYL,mat(0x5a3b22),[x,1,z],[.2,2,.2],0,g);mk(SPH,mat(0x5f8a3a,{r:.9}),[x,2.7,z],[1.3,1.4,1.3],0,g)}
  wheatField(g,1500,[18,9.5],0,-5.6,1.0,0xe8bb4c);wheatField(g,500,[14,2.5],0,7.4,1.0,0xf0c55a);
  const cart=grp([-2.2,0,-.6],g);mk(BOX,beam,[0,.6,0],[1.4,.12,.8],0,cart);[-1,1].forEach(s=>mk(new THREE.TorusGeometry(.35,.05,8,20),beam,[0,.35,s*.45],1,0,cart));g.userData.cart=cart;
  g.userData.sacks=[0,1,2].map(i=>{const s=P.sack();s.position.set(-2.6+i*.4,.95,-.6);g.add(s);return s});
});
env('barber',g=>{mk(BOX,mat(0x2e221b,{r:.95}),[0,-.05,0],[14,.1,14],0,g);
  for(let i=0;i<20;i++)mk(BOX,i%2?mat(0x3a2a20):mat(0x33251c),[-5+i*.52,2.2,-2.6],[.5,4.4,.15],0,g);
  for(let i=0;i<12;i++)mk(BOX,i%2?mat(0x3a2a20):mat(0x33251c),[-3.8,2.2,-2.4+i*.52],[.15,4.4,.5],0,g);
  const jc=[0x5a8a5a,0x8a5a3a,0x6a5a8a,0xa08a4a,0x4a6a8a,0x9a6a5a];
  [1.2,1.8,2.4].forEach((y,r)=>{mk(BOX,beam,[0,y,-2.35],[5.5,.06,.4],0,g);for(let j=0;j<9;j++){const x=-2.4+j*.6;if(r===1&&j===6)continue;
    mk(new THREE.CylinderGeometry(.09+rnd(j+r*9)*.04,.1,.2+rnd(j*2+r)*.15,14),mat(jc[(j+r)%6],{r:.35}),[x,y+.15,-2.35],1,0,g)}});
  // the hidden 2026 soda can
  const can=grp([-2.4+6*.6,1.8,-2.32],g);mk(new THREE.CylinderGeometry(.065,.065,.24,20),mat(0xe0141e,{r:.3,m:.3}),[0,.15,0],1,0,can);mk(CYL,mat(0xd0d4d8,{m:.9,r:.25}),[0,.275,0],[.06,.012,.06],0,can);
  mk(new THREE.TorusGeometry(.066,.008,6,20),mat(0xffffff),[0,.15,0],[1,1,1],[PI/2,0,.3],can,false);g.userData.can=can;
  // herbs hanging
  for(let i=0;i<7;i++)mk(CONE,mat(0x6a7a3a,{r:.9}),[-2.5+i*.8,3.2,-1.8],[.12,.4,.12],[PI,0,0],g);
  // chair & table
  mk(BOX,beam,[.4,.45,-.6],[.6,.08,.6],0,g);[[-.25,-.25],[.25,-.25],[-.25,.25],[.25,.25]].forEach(([x,z])=>mk(BOX,beam,[.4+x,.22,-.6+z],[.06,.45,.06],0,g));
  const cd=grp([1.8,0,-1.6],g);mk(BOX,beam,[0,.8,0],[1,.06,.6],0,cd);mk(CYL,mat(0xf2ecd8),[0,.95,0],[.04,.22,.04],0,cd);g.userData.candle=mk(CONE,mat(0xffc060,{e:0xffb040,ei:3}),[0,1.12,0],[.03,.09,.03],0,cd,false);
});
const starsG=(()=>{const n=500,pos=new Float32Array(n*3);for(let i=0;i<n;i++){const a=rnd(i)*PI*2,e=.15+rnd(i+n)*1.2;pos.set([Math.cos(a)*Math.cos(e)*120,Math.sin(e)*120,Math.sin(a)*Math.cos(e)*120],i*3)}
  const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.BufferAttribute(pos,3));return new THREE.Points(geo,new THREE.PointsMaterial({color:0xffffff,size:.7,sizeAttenuation:true,fog:false}))})();
env('night',g=>{mk(BOX,mat(0x1d2030,{r:.95}),[0,-.05,0],[80,.1,80],0,g);g.add(starsG);
  [[-5,-6,1.2,.3],[0,-9,1.4,0],[5.5,-6.5,1.2,-.4],[-9,-3,1,.8],[9,-2,1.1,-.9]].forEach(a=>{const h=house(g,...a);h.userData.win.material=mat(0xffb050,{e:0xffa040,ei:2.5})});
  mk(CYL,mat(0x5a3b22,{r:.9}),[0,.22,0],[.22,1.4,.22],[0,0,PI/2],g);
  for(let i=0;i<8;i++){const x=-14+i*4,z=-20+rnd(i)*3;mk(CYL,mat(0x2a2030),[x,1,z],[.18,2,.18],0,g);mk(SPH,mat(0x1e2a2a,{r:.9}),[x,2.6,z],[1.2,1.3,1.2],0,g)}
});

// ---------------- cast ----------------
const louis=makeLouis(),pig=makePig(),ox=makeOx(),lord=makeLord(),guards=[makeGuard(),makeGuard()],barber=makeBarber(),goat=makeGoat();
const chickens=[makeChicken(),makeChicken()];
const family=[makePeasant(0x7a6a4a,0x5a3a22,1),makePeasant(0x8a5a4a,0x3a2214,1),makePeasant(0x6a7a5a,0x6a4a2a,.65),makePeasant(0x7a6a8a,0x5a3a22,.6)];
const props={bucket:P.bucket(),bucketW:P.bucketW(),mug:P.mug(),bread:P.bread(),straw:P.straw(),sickle:P.sickle(),pitch:P.pitchfork(),sackB:P.sack(),pliers:P.pliers(),honey:P.honey(),bowl:P.bowlBlade()};
const stink=[...Array(8)].map((_,i)=>mk(SPH,mat(0x8bbf3c,{basic:true,op:.6}),[0,0,0],.04,0,scene,false));
const drops=[...Array(14)].map(()=>mk(SPH,mat(0x9fe0ff,{r:.05}),[0,0,0],.025,0,scene,false));
const honeyStream=mk(CYL,mat(0xe8a52a,{r:.2}),[0,0,0],[.015,.4,.015],0,scene,false);
const dust=mk(SPH,mat(0xd9c49a,{basic:true,op:.5}),[0,0,0],1,0,scene,false);
const allActors=[pig.g,ox.g,lord.g,...guards.map(x=>x.g),barber.g,goat.g,...chickens.map(c=>c.g),...family.map(f=>f.g),...stink,...drops,honeyStream,dust];

// ---------------- TIMELINE ----------------
let TL=null,AMP=[];
window.setTL=(tl,amp)=>{TL=tl;AMP=amp};
function sentT(pl,i){return pl.sent[i]?pl.sent[i].t-pl.start:0}
function wordT(pl,w){const x=pl.words.find(x=>x.w.toLowerCase().startsWith(w.toLowerCase()));return x?x.t-pl.start:null}

// camera
let shake=0;
function cam(p,l,fov=38){camera.position.set(...p);camera.lookAt(...l);camera.fov=fov;camera.updateProjectionMatrix()}
function camMove(p0,p1,l0,l1,k,f0=38,f1){cam(L3(p0,p1,k),L3(l0,l1,k),lerp(f0,f1??f0,k))}

// ---------------- PLANS ----------------
// each returns {env, preset, hour, badge?, fx:{...}}
const lieBase={x:0,z:1.0,ry:0,lie:1};
const HEADL=[-.6,.3,0];
const PLANS={
 p01(t,d,pl,o){preset('hutNight');
   const jolt=easeOut((t-.35)/.3);
   o.L={...lieBase,expr:'shock',open:o.open,sit:jolt*.55,armL:[-1.6*jolt,-.4],armR:[-1.6*jolt,.4],elL:.8*jolt,elR:.8*jolt,jump:.04*Math.sin(t*30)*(1-clamp(t-1))};
   pig.g.visible=true;pig.g.position.set(-1.05+.06*Math.sin(t*3),0,-.95);pig.hd.rotation.z=Math.sin(t*14)*.08;
   const k=easeOut(t/.35);camMove([0,6.0,4.6],[.1,2.7,1.6],[-.2,.3,-.3],[-.3,.5,-.6],k,55,40);shake=t<1.4?.03:.008;
   o.pops=[{t:.4,txt:'😱',x:760,y:700}];return 'hut'},
 p02(t,d,pl,o){preset('hutNight');
   const rew=1-clamp(t/1.2);o.rewind=t<1.2;const jolt=easeOut(rew);const look=ease((t-1.3)/.3);
   o.L={...lieBase,expr:t<1.3?'shock':'blank',open:o.open,sit:Math.max(jolt*.55,look*.6),armL:[-1.6*jolt,-.4],armR:[lerp(-1.6*jolt,-2.5,look),.3],elR:lerp(.8*jolt,.4,look),elL:.8*jolt,head:[0,0,0],look:[0,look*.5]};
   pig.g.visible=true;pig.g.position.set(-1.05,0,-.95);
   camMove([.2,2.8,2.6],[.2,2.5,2.2],[-.2,.7,-.3],[-.1,.8,-.2],ease(t/d),40,36);return 'hut'},
 p03(t,d,pl,o){preset('hutDay');const t2=sentT(pl,1);
   if(t<t2){const up=ease((t-.8)/1.4);o.L={...lieBase,expr:t<.6?'sleep':'shock',open:o.open,sit:up,armL:[-.3,-.2],armR:[-.3,.2],look:[0,up*.3]};
     const a=-.5+t*.22;cam([Math.sin(a)*3.2,2.4,.2+Math.cos(a)*3.2],[0,.5,.1],38);}
   else{const tt=t-t2;const pat=Math.sin(tt*14);const show=tt>2.4;
     o.L={...lieBase,sit:1,expr:show?'tired':'worried',open:o.open,armL:show?[-1.3,0]:[-.4+pat*.25,.35],armR:show?[-1.9,-.2]:[-.4-pat*.25,-.35],elL:show?.6:1.2,elR:show?.9:1.2,holdR:show?props.straw:null,head:[show?.15:-.2,0,0]};
     const k=easeOut(tt/.3);camMove([.9,1.7,3.4],[.7,1.6,2.9],[0,1.0,.15],[0,1.05,.15],k,32,30);}
   return 'hut'},
 p04(t,d,pl,o){preset('hutDay');const lean=ease((t-.1)/.6);const pt=sentT(pl,1)+.3;const point=ease((t-pt)/.3);
   o.L={x:0,z:.4+lean*.4,ry:0,expr:t<pt?'sly':'proud',open:o.open,bow:.22*lean,armR:[lerp(0,-1.45,point),-.1],elR:lerp(.15,.05,point),wink:t>d-1.2&&t<d-.5,head:[-.12*lean,0,.08]};
   camMove([0,1.75,4.6],[0,1.72,3.9],[0,1.6,0],[0,1.6,.4],ease(t/d),32,30);o.tag={txt:'🔎 OBJET CACHÉ : TROUVE-LE !',t:pt-.2};return 'hut'},
 p05(t,d,pl,o){preset('dawn');
   o.L={x:.3,z:1.0,ry:-.2,expr:t>1.0?'blank':'worried',open:o.open,armR:[-1.35,-.1],elR:.05,holdR:props.bucket,head:[0,.35,0],armL:[-.2,-.5],elL:1.4};
   stink.forEach((s,i)=>{s.visible=true;const k=((t*.5+i/8)%1);s.position.set(.7+Math.sin(k*8+i)*.08,.9+k*.8,1.6+(i%2)*.05);s.scale.setScalar(.04*(1-k)+.01)});
   chickens[0].g.visible=true;chickens[0].g.position.set(lerp(-2.2,1.8,t/d),0,1.9);chickens[0].hd.rotation.z=-Math.max(0,Math.sin(t*6))*.6;
   const k=easeOut(t/.35);cam([2.8,1.7,5.8],L3([-4,1.5,0],[.4,1.3,1.0],k),32);return 'village'},
 p06(t,d,pl,o){preset('day');const qs=sentT(pl,1);const look=t<qs?0:Math.sin((t-qs)*3.2);const end=t>d-1.7;
   o.L={x:-.2,z:.6,ry:.15,expr:end?'proud':'happy',open:o.open,armL:[-1.1,-.15],elL:.6,armR:[-1.1,.15],elR:.6,holdL:props.mug,holdR:props.bucketW,head:[end?-.08:0,end?0:look*.45,0],look:[end?0:look,0],browUp:end?.03:0};
   camMove([0,1.8,5.4],[0,1.8,4.8],[-.2,1.8,0],[-.2,1.75,0],ease(t/d),34,32);
   o.quiz={t:qs+.2,count:d-1.75};return 'village'},
 p07(t,d,pl,o){preset('day');const t3=sentT(pl,2);
   if(t<t3){const dr=ease(t/.5);o.L={x:-.6,z:.5,ry:.4,expr:'proud',open:o.open,armL:[-2.3*dr,-.2],elL:.6,armR:[-2.3*dr,.2],elR:.6,holdR:props.bucketW,head:[-.45*dr,0,0]};
     drops.forEach((p,i)=>{p.visible=t<2.2;const k=((t*1.3+i/14)%1);p.position.set(-.5+Math.sin(i*2)*.25*k,2.1-k*1.4+Math.sin(k*3)*.2,.8+Math.cos(i)*.2*k)});
     camMove([.5,.5,2.6],[.4,.45,2.3],[-.6,1.7,.4],[-.6,1.8,.4],ease(t/t3),54,52);}
   else{const tt=t-t3;const sh=Math.sin(tt*2)*.2;o.L={x:-.6,z:.5,ry:.2,expr:'happy',open:o.open,armL:[-.2,-.6-sh],elL:1.0,armR:[-1.6,-.1],elR:1.3,holdR:props.mug,head:[0,0,.1]};
     camMove([1.0,1.9,4.4],[.8,1.85,3.9],[-.6,1.75,.4],[-.6,1.7,.4],ease(tt/(d-t3)),32,30);}
   o.badgeAt=wordT(pl,'mythe');return 'village'},
 p08(t,d,pl,o){preset('hutDay');const ov=1.2;
   if(t<ov){o.L={vis:false};cam([-2.4,3.0,-.8],[-2.4,.9,-1.52],40);}
   else{const tt=t-ov;const bite=Math.max(0,Math.sin(tt*3));
     o.L={x:-2.4,z:-2.3,ry:0,expr:'blank',open:o.open,armR:[-1.6-bite*.4,-.2],elR:1.6,holdR:props.bread,armL:[-.6,-.1],elL:.8,head:[.05,0,0]};
     camMove([-2.4,1.9,1.9],[-2.4,1.9,1.5],[-2.4,1.7,-2.0],[-2.4,1.72,-2.0],ease(tt/(d-ov)),30,27);}
   o.nope={t:sentT(pl,1)};return 'hut'},
 p09(t,d,pl,o){preset('dawn');const t2=sentT(pl,1);const pl2=ENV.plow.userData.plow;
   const walk=t*.35;ox.g.visible=true;ox.g.position.set(1.3+walk,0,0);ox.legs.forEach((l,i)=>l.rotation.z=Math.sin(t*5+i*PI)*.3);
   const judge=ease((t-t2-.3)/.4);ox.hd.rotation.y=judge*1.1;
   pl2.position.set(-.1+walk,0,0);
   o.L={x:-.9+walk,z:0,ry:PI/2,expr:t>t2+.8?'blank':'tired',open:o.open,bow:.35,armL:[-1.0,0],armR:[-1.0,0],elL:.3,elR:.3,legs:[Math.sin(t*5)*.4,-Math.sin(t*5)*.4],sweat:true,head:[-.2,t>t2+.8?-1.2:0,0]};
   if(t<1.6){const k=ease(t/1.6);camMove([-6,7,8],[-3,4.5,6],[0,0,0],[.3+walk,.8,0],k,40,38);}
   else camMove([walk+.2,1.7,5.0],[walk+.4,1.6,4.5],[walk+.2,1.2,0],[walk+.4,1.25,0],ease((t-1.6)/(d-1.6)),36,32);
   return 'plow'},
 p10(t,d,pl,o){const cuts=[0,d*.34,d*.67];const c=t<cuts[1]?0:t<cuts[2]?1:2;
   if(c===0){preset('noon');const sw=Math.sin(t*6);o.L={x:t*.4-.6,z:.4,ry:.3,expr:'tired',open:o.open,bow:.35,armR:[-1.0+sw*.6,.2],elR:.3,holdR:props.sickle,armL:[-.6,-.2],elL:.5,sweat:true};
     cam([t*.4+1.4,1.3,3.2],[t*.4-.6,1.1,.4],32);}
   else if(c===1){preset('noon');const tt=t-cuts[1];const st=Math.sin(tt*7);o.L={x:-.2,z:.6,ry:.5,expr:'worried',open:o.open,bow:.45,lean:st*.08,armL:[-2.6,-.3],armR:[-2.6,.3],elL:1.9,elR:1.9,sweat:true,legs:[st*.3,-st*.3]};
     props.sackB.position.set(-.25,2.0,.35);props.sackB.rotation.set(0,0,PI/2);scene.add(props.sackB);props.sackB.visible=true;
     cam([1.4,.45,3.2],[-.2,1.4,.4],42);}
   else{const tt=t-cuts[2];preset('pm');const a=lerp(.8,-.8,tt/(d-cuts[2]));sun.position.set(Math.sin(a)*10,6+Math.cos(a)*4,3);sunBall.position.set(Math.sin(a)*60,20+Math.cos(a)*25,-60);
     o.L={x:0,z:.5,ry:.2,expr:'tired',open:o.open,armR:[-2.4,0],elR:2.0,armL:[-.1,-.2],head:[.1,0,0]};cam([-1.0,2.6,6.5],[0,1.4,0],34);o.timelapse=true;}
   return 'wheat'},
 p11(t,d,pl,o){preset('noon');const tr=ease((t-.4)/.5);
   o.L={x:0,z:.5,ry:0,expr:t>.3?'shock':'blank',open:o.open,head:[0,tr*.7,0],look:[tr,0],armR:[-.3,0],armL:[-.3,0]};
   dust.visible=true;dust.position.set(-8,.6,-10);dust.scale.set(2+t,1+t*.4,1.5);
   cam([0,1.9,2.5],[0,1.86,.5],24+t*3);shake=.006+.01*t;return 'wheat'},
 p12(t,d,pl,o){preset('noon');const t2=sentT(pl,1);
   lord.g.visible=true;guards.forEach(g=>g.g.visible=true);
   if(t<t2+.2){const k=t/(t2+.2);lord.g.position.set(lerp(-6,-2.2,ease(k)),0,lerp(-2,-.8,ease(k)));lord.g.rotation.y=-.3;lord.legs.forEach((l,i)=>l.rotation.z=Math.sin(t*9+i*PI/2)*.5);
     lord.horse.position.y=Math.abs(Math.sin(t*9))*.06;
     guards[0].g.position.set(lord.g.position.x-1.4,0,lord.g.position.z-1.6);guards[1].g.position.set(lord.g.position.x-2.0,0,lord.g.position.z-2.6);
     o.L={x:2.2,z:.5,ry:-1.2,expr:'blank',open:o.open};
     cam([.9,.5,4.4],[lord.g.position.x,2.1,lord.g.position.z],46);}
   else{const tt=t-t2;lord.g.position.set(-2.2,0,-.8);lord.g.rotation.y=-.3;lord.horse.position.y=0;
     const sk=ENV.wheat.userData.sacks;const n=Math.floor(clamp(tt/(d-t2)*4,0,3));
     sk.forEach((s,i)=>{s.position.set(i<n?-.7+i*.3:-2.6+i*.4,i<n?.25:.95,i<n?.9:-.6)});
     guards[0].g.position.set(-1.0,0,.2);guards[0].g.rotation.y=PI*.6;guards[1].g.position.set(-1.8,0,-1.6);guards[1].g.rotation.y=PI*.3;
     o.L={x:.9,z:.9,ry:-.5,expr:'blank',open:o.open};
     camMove([2.6,1.8,5.4],[2.3,1.75,4.8],[-.4,1.3,0],[-.3,1.3,0],ease(tt/(d-t2)),36,33);}
   o.badgeAt=wordT(pl,'corvée');return 'wheat'},
 p13(t,d,pl,o){preset('noon');lord.g.visible=true;const k=ease(t/d);lord.g.position.set(lerp(-2.2,-7,k),0,lerp(-.8,-3,k));lord.g.rotation.y=PI*.85;lord.legs.forEach((l,i)=>l.rotation.z=Math.sin(t*9+i*PI/2)*.5);
   const look=t>d-1.2;const b=ease(t/.4)*(look?0:1);
   o.L={x:.9,z:.6,ry:look?0:-.7,expr:look?'blank':'happy',open:o.open,bow:b*1.0,armL:[-.4*b,-.3],armR:[-1.2*b,.2],elR:1.2*b,head:[look?0:-.2*b,0,0]};
   if(!look)cam([3.4,1.5,4.2],[0,1.1,0],36);else cam([.9,1.95,3.1],[.9,1.85,.6],28);
   o.pops=[{t:.45,txt:'🙇',x:760,y:780}];return 'wheat'},
 p14(t,d,pl,o){preset('noon');const h=d/3;const ph=t<h*1.1?0:t<h*2.1?1:2;
   if(ph===0){const b=ease(t/.3);o.L={x:0,z:.6,ry:0,expr:'happy',open:o.open,bow:.9*b,armR:[-1.0*b,.2],elR:1.2*b,head:[-.2*b,0,0]};}
   else if(ph===1){const r=easeOut((t-h*1.1)/.25);o.L={x:0,z:.6,ry:0,expr:'angry',open:o.open,armR:[-3.0*r,.2],elR:.2,holdR:props.pitch,armL:[-.3,-.6*r],elL:1.2,jump:Math.max(0,Math.sin((t-h*1.1)*10))*.08};}
   else o.L={x:0,z:.6,ry:0,expr:'happy',open:o.open,armL:[-.4,-.9],elL:1.4,armR:[-.4,.9],elR:1.4,head:[0,0,.12]};
   camMove([0,1.9,6.0],[0,1.9,5.4],[0,1.85,0],[0,1.85,0],ease(t/d),36,34);o.choice={ph};return 'wheat'},
 p15(t,d,pl,o){preset('pm');const t2=sentT(pl,1);
   if(t<t2){const k=ease(t/.4);o.L={x:0,z:.5,ry:0,expr:'worried',open:o.open,armR:[-1.5*k,.4],elR:1.5*k,head:[.35*k,.25*k,0],look:[.5,-.6],sweat:true};
     camMove([.6,1.9,3.0],[.5,1.85,2.6],[0,1.6,.5],[0,1.6,.5],ease(t/t2),32,30);o.pops=[{t:.3,txt:'AÏE',x:700,y:700,font:'Lucky'}];}
   else{const tt=t-t2;const k=ease(tt/.5);o.L={x:0,z:.5,ry:0,expr:'worried',open:o.open,armL:[-.5*k,-1.1*k],armR:[-.5*k,1.1*k],elL:.3,elR:.3,head:[-.55*k,0,0],look:[0,1]};
     camMove([0,.8,3.8],[0,.7,3.4],[0,1.7,0],[0,1.8,0],ease(tt/(d-t2)),40,38);}
   return 'wheat'},
 p16(t,d,pl,o){preset('barber');candleL.position.set(1.8,1.4,-1.4);const k=ease(t/(d*.6));
   barber.g.visible=true;barber.g.position.set(1.3,0,-.9);barber.g.rotation.y=-.5;barber.arm.rotation.set(-1.3+Math.sin(t*5)*.1,0,.2);barber.hold.clear();barber.hold.add(props.pliers);
   props.pliers.rotation.z=Math.sin(t*8)*.15;fillL.intensity=6;fillL.position.set(0,2.5,2);
   o.L={x:lerp(-3.2,-.6,k),z:.2,ry:lerp(1.3,.5,ease((t-d*.5)/.5)),expr:'worried',open:o.open,legs:k<1?[Math.sin(t*7)*.4,-Math.sin(t*7)*.4]:[0,0]};
   camMove([-.8,1.8,4.6],[-.6,1.75,3.8],[-.3,1.4,-1.4],[0,1.45,-1.2],ease(t/d),40,36);return 'barber'},
 p17(t,d,pl,o){preset('barber');candleL.position.set(1.8,1.4,-1.4);fillL.intensity=6;fillL.position.set(0,2.5,2);
   barber.g.visible=true;barber.g.position.set(.75,0,-.4);barber.g.rotation.y=-1.0;barber.arm.rotation.set(-1.2,0,.6);barber.hold.clear();barber.hold.add(props.honey);props.honey.rotation.set(0,0,-1.9);
   const nod=t>sentT(pl,1)?Math.sin(t*8)*.12:0;
   o.L={x:-.5,z:.2,ry:.6,expr:t>sentT(pl,1)?'proud':'shock',open:o.open,armR:[-1.2,.5],elR:.3,head:[.2+nod,.3,0],look:[.4,-.5]};
   camMove([-1.9,1.8,2.8],[-1.7,1.75,2.4],[-.2,1.4,0],[-.2,1.45,0],ease(t/d),34,32);
   o.badgeAt=.3;return 'barber'},
 p18(t,d,pl,o){preset('barber');candleL.position.set(1.8,1.4,-1.4);fillL.intensity=6;fillL.position.set(0,2.5,2);const t2=sentT(pl,1);
   barber.g.visible=true;barber.g.position.set(.75,0,-.4);barber.g.rotation.y=-.8;barber.arm.rotation.set(-1.4,0,.3);barber.hold.clear();barber.hold.add(props.bowl);
   if(t<t2){o.L={x:-.6,z:.2,ry:.6,expr:'shock',open:o.open,armL:[-.2,-.4],armR:[-.2,.4]};camMove([-.6,1.85,3.4],[-.6,1.85,2.3],[-.3,1.6,0],[-.5,1.8,.1],ease(t/t2),34,26);}
   else{const tt=t-t2;const run=easeOut(tt/1.2);o.L={x:lerp(-.6,-5,run),z:.4,ry:-PI/2,expr:'shock',open:o.open,legs:[Math.sin(tt*16)*.8,-Math.sin(tt*16)*.8],armL:[Math.sin(tt*16)*1.2,0],armR:[-Math.sin(tt*16)*1.2,0],bow:.25,jump:Math.abs(Math.sin(tt*16))*.08};
     cam([1.0,1.7,4.2],[-1.2,1.3,0],40-tt*6);shake=.025;}
   o.badgeAt=wordT(pl,'saignée');return 'barber'},
 p19(t,d,pl,o){preset('hutNight');
   family.forEach((f,i)=>{f.g.visible=true;f.b.rotation.set(0,0,PI/2);f.b.position.set(0,.25,0);const pos=[[-1.7,-1.4],[1.4,-1.2],[1.9,1.0],[-1.5,1.5]][i];f.g.position.set(pos[0],0,pos[1]);f.g.rotation.y=[.3,-.2,.8,-.6][i]});
   goat.g.visible=true;goat.g.position.set(-2.8,0,.8);goat.g.rotation.y=.8;
   pig.g.visible=true;pig.g.position.set(-2.0,0,.2);
   o.L={...lieBase,expr:'shock',open:o.open,look:[0,1]};
   const a=t*.12;cam([Math.sin(a)*1.2,6.6,Math.cos(a)*1.2+2.2],[-.2,0,.1],40);return 'hut'},
 p20(t,d,pl,o){preset('hutNight');const k=ease(t/.9);
   pig.g.visible=true;pig.g.position.set(lerp(-2.0,-.95,k),0,lerp(.2,.05,k));pig.g.rotation.set(0,lerp(0,PI/2,k),0);
   o.L={...lieBase,expr:'blank',open:o.open,head:[0,-.4,0],look:[0,.6]};
   cam([.3,3.6,2.6],[-.2,.3,-.1],40);o.pops=[{t:.8,txt:'🐷💤',x:420,y:760}];return 'hut'},
 p21(t,d,pl,o){preset('night');const t2=sentT(pl,1);
   const Lp={x:0,z:.25,ry:0,expr:'worried',open:o.open,legs:[-1.4,-1.4],y:-.38,armL:[-.6,-.2],armR:[-.6,.2],elL:.8,elR:.8,head:[-.25,0,0],look:[0,1]};
   o.L=Lp;fillL.intensity=5;fillL.position.set(1,2.2,3);
   if(t<t2)camMove([0,1.1,3.6],[0,2.4,5.0],[0,1.2,0],[0,1.6,0],ease(t/t2),36,40);
   else camMove([4,4,10],[2,4.5,11],[0,1.5,-5],[0,2.2,-5],ease((t-t2)/(d-t2)),44,44);
   o.badgeAt=.4;o.sub={t:t2,txt:'(à cause de la mortalité infantile)'};return 'night'},
 p22(t,d,pl,o){preset('hutNight');
   pig.g.visible=true;pig.g.position.set(-.95,0,.05);pig.g.rotation.set(0,PI/2,0);
   const thumb=ease((t-sentT(pl,2))/.3);const close=t>d-1.2;
   o.L={...lieBase,expr:close?'sleep':'tired',open:o.open,head:[0,-.4,0],look:[0,.6],armR:[-1.4*thumb,0],elR:1.4*thumb};
   camMove([.3,3.6,2.6],[.2,3.0,2.0],[-.2,.3,-.1],[-.2,.35,-.3],ease(t/d),40,38);o.fade=clamp((t-(d-.9))/.8);o.cta=true;return 'hut'},
};
const HOURS={p01:'AN 1247',p02:'4H30',p03:'4H30',p04:'4H40',p05:'4H45',p06:'5H00',p07:'5H05',p08:'5H15',p09:'6H00',p10:'9H00',p11:'12H00',p12:'12H05',p13:'12H10',p14:'12H10',p15:'15H00',p16:'15H30',p17:'15H40',p18:'15H45',p19:'20H00',p20:'21H00',p21:'23H00',p22:'23H30'};
const BADGES={p07:'MYTHE ❌',p12:'LA CORVÉE 😐',p17:'MIEL ✅',p18:'SAIGNÉE 😬',p21:'~30 ANS'};

// ---------------- overlay (SVG) ----------------
const esc=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;');
const G=(c,tr)=>`<g transform="${tr}">${c}</g>`;
function chunks(words){const out=[];let cur=[];words.forEach((w,i)=>{if(cur.length&&(cur.map(x=>x.w).join(' ').length+1+w.w.length>16)){out.push(cur);cur=[]}
  cur.push(w);const nx=words[i+1];const gap=nx?nx.t-w.e:9;if(cur.length>=4||gap>.22||!nx){out.push(cur);cur=[]}});return out}
function pill(x,y,txt,sc=1,fill='#1a1230'){const w=txt.length*34+80;return G(`<rect x="0" y="-50" width="${w}" height="100" rx="50" fill="${fill}" opacity=".9" stroke="#f2c94c" stroke-width="5"/><text x="${w/2}" y="20" text-anchor="middle" font-family="Lucky" font-size="56" fill="#fff">${esc(txt)}</text>`,`translate(${x},${y}) scale(${sc})`)}
function badge(txt,p,y=470,rot=-4){const fs=Math.min(84,760/(txt.length*.62)),bw=txt.length*fs*.62+70;
  return G(`<rect x="${-bw/2}" y="${-fs*.85}" width="${bw}" height="${fs*1.7}" rx="30" fill="#ffd84d" stroke="#000" stroke-width="8"/><text x="0" y="${fs*.33}" text-anchor="middle" font-family="Lucky" font-size="${fs}" fill="#1a1230">${esc(txt)}</text>`,`translate(490,${y}) rotate(${rot}) scale(${p})`)}
function card(x,y,emo,lab,on,p){return G(`<rect x="-170" y="-150" width="340" height="300" rx="40" fill="${on?'#ffd84d':'#fff'}" stroke="#000" stroke-width="8"/><text x="0" y="20" text-anchor="middle" font-size="140">${emo}</text><text x="0" y="120" text-anchor="middle" font-family="Lucky" font-size="54" fill="#1a1230">${lab}</text>`,`translate(${x},${y}) scale(${p*(on?1.08:1)}) rotate(${on?-3:0})`)}
function overlay(T,pl,lt,o){
  let s=`<defs><linearGradient id="vg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity=".45"/><stop offset=".15" stop-color="#000" stop-opacity="0"/><stop offset=".75" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".5"/></linearGradient></defs><rect width="1080" height="1920" fill="url(#vg)"/>`;
  // hour pill with tick
  const hr=HOURS[pl.id],lab=hr==='AN 1247'?'AN 1247':'AN 1247 · '+hr;const pop=1+.25*Math.max(0,1-lt/.25);
  s+=G(`<rect x="0" y="-50" width="${lab.length*34+100}" height="100" rx="50" fill="#1a1230" opacity=".88" stroke="#f2c94c" stroke-width="5"/><circle cx="54" cy="0" r="24" fill="none" stroke="#f2c94c" stroke-width="6"/><path d="M54,-14 v14 l10,8" stroke="#f2c94c" stroke-width="6" fill="none" stroke-linecap="round"/><text x="94" y="20" font-family="Lucky" font-size="56" fill="#fff">${lab}</text>`,`translate(56,250) scale(${pop})`);
  // badge
  if(BADGES[pl.id]&&o.badgeAt!=null){const p=easeOut((lt-o.badgeAt)*4);if(p>0)s+=badge(BADGES[pl.id],p)}
  if(pl.id==='p07'){const p=easeOut((lt-.1)*4);s+=badge('💧 RÉPONSE : L’EAU',p,640,3)}
  if(o.sub&&lt>o.sub.t){s+=G(`<text x="0" y="0" text-anchor="middle" font-family="Baloo" font-weight="800" font-size="48" fill="#fff" stroke="#000" stroke-width="9" paint-order="stroke">${esc(o.sub.txt)}</text>`,`translate(490,600) scale(${easeOut((lt-o.sub.t)*4)})`)}
  if(o.tag&&lt>o.tag.t){const p=easeOut((lt-o.tag.t)*4);const wob=Math.sin(lt*6)*2;s+=badge(o.tag.txt,p,480,wob)}
  if(o.nope&&lt>o.nope.t){const p=easeOut((lt-o.nope.t)*4);s+=G(`<circle r="110" fill="#fff" stroke="#e01e1e" stroke-width="22"/><text x="0" y="22" text-anchor="middle" font-family="Lucky" font-size="54" fill="#5b3a1e">NUTELLA</text><path d="M-78,78 L78,-78" stroke="#e01e1e" stroke-width="22"/>`,`translate(800,560) rotate(-10) scale(${p})`)}
  if(o.quiz&&lt>o.quiz.t){const p=easeOut((lt-o.quiz.t)*4);s+=card(300,620,'🍺','BIÈRE',false,p)+card(780,620,'💧','EAU',false,easeOut((lt-o.quiz.t-.15)*4));
    s+=G(`<text x="0" y="0" text-anchor="middle" font-family="Lucky" font-size="70" fill="#fff" stroke="#000" stroke-width="10" paint-order="stroke">VS</text>`,`translate(540,640) scale(${p})`);
    if(lt>o.quiz.count){const c=3-Math.floor((lt-o.quiz.count)/.55);const f=((lt-o.quiz.count)/.55)%1;if(c>=1)s+=G(`<circle r="130" fill="#e94b4b" stroke="#fff" stroke-width="12"/><text x="0" y="62" text-anchor="middle" font-family="Lucky" font-size="200" fill="#fff">${c}</text>`,`translate(540,1180) scale(${1.4-.4*easeOut(f*3)})`)}}
  if(o.choice){const ph=o.choice.ph;s+=card(300,620,'🙇','COURBETTE',ph===0,1)+card(780,620,'⚔️','RÉVOLTE',ph===1,1);if(ph===2)s+=G(`<text x="0" y="0" text-anchor="middle" font-family="Lucky" font-size="76" fill="#ffd84d" stroke="#000" stroke-width="10" paint-order="stroke">COMMENTE ! 👇</text>`,`translate(540,860) scale(${easeOut((lt%9)*3)})`)}
  (o.pops||[]).forEach(p=>{if(lt>p.t&&lt<p.t+1.6){const k=easeOut((lt-p.t)*5);const f=1-clamp((lt-p.t-1.3)/.3);s+=G(`<text x="0" y="0" text-anchor="middle" ${p.font?`font-family="${p.font}" fill="#fff" stroke="#000" stroke-width="10" paint-order="stroke"`:''} font-size="140" opacity="${f}">${p.txt}</text>`,`translate(${p.x},${p.y-(lt-p.t)*40}) scale(${k}) rotate(${Math.sin(lt*10)*6})`)}});
  if(o.rewind){for(let i=0;i<14;i++){const y=((i*137+lt*2400)%1920);s+=`<rect x="0" y="${y}" width="1080" height="${6+rnd(i)*14}" fill="#fff" opacity="${.15+rnd(i+3)*.25}"/>`}
    s+=`<rect width="1080" height="1920" fill="#3a5aff" opacity=".12"/>`+G(`<text x="0" y="0" font-family="Lucky" font-size="120" fill="#fff" stroke="#000" stroke-width="10" paint-order="stroke">◀◀ REWIND</text>`,`translate(150,760)`)}
  if(o.timelapse)s+=G(`<text x="0" y="0" font-family="Lucky" font-size="64" fill="#fff" stroke="#000" stroke-width="9" paint-order="stroke">⏩ x 100</text>`,`translate(720,380)`);
  if(o.cta&&lt>sentT(pl,0)+.2){const p=easeOut((lt-.3)*3);s+=G(`<rect x="-420" y="-80" width="840" height="160" rx="40" fill="#e94b4b" stroke="#fff" stroke-width="8"/><text x="0" y="22" text-anchor="middle" font-family="Lucky" font-size="62" fill="#fff">T'AURAIS TENU COMBIEN ? 👇</text>`,`translate(510,560) scale(${p})`)}
  // captions
  const cs=chunks(pl.words);const i=cs.findIndex((c,j)=>T>=c[0].t-.05&&(!cs[j+1]||T<cs[j+1][0].t-.05));
  if(i>=0&&T<cs[i][cs[i].length-1].e+.6){const cur=cs[i];const pp=easeOut((T-cur[0].t+.05)/.12);
    const chars=cur.map(w=>w.w).join(' ').length,fs=Math.min(98,880/(chars*.56));
    const ws=cur.map(w=>{const a=T>=w.t-.02&&T<w.e+.06;return `<tspan fill="${a?'#ffd84d':'#fff'}">${esc(w.w.toUpperCase())}</tspan>`}).join(' ');
    s+=G(`<text x="0" y="0" text-anchor="middle" font-family="Baloo" font-weight="800" font-size="${fs}" stroke="#000" stroke-width="${fs/6}" stroke-linejoin="round" paint-order="stroke">${ws}</text>`,`translate(490,1470) scale(${lerp(.75,1,pp)}) rotate(${lerp(-3,0,pp)})`)}
  if(o.flash>0)s+=`<rect width="1080" height="1920" fill="#fff" opacity="${o.flash}"/>`;
  if(o.fade>0)s+=`<rect width="1080" height="1920" fill="#000" opacity="${o.fade}"/>`;
  return s;
}

// ---------------- frame ----------------
const svg=document.getElementById('o');
window.renderFrame=(f)=>{
  const fps=30,T=f/fps;
  const pl=TL.plans.find(p=>T>=p.start&&T<p.start+p.dur)||TL.plans[TL.plans.length-1];
  const lt=T-pl.start,d=pl.dur;
  // reset
  Object.values(ENV).forEach(e=>e.visible=false);allActors.forEach(a=>a.visible=false);props.sackB.visible=false;
  shake=0;fireL.position.set(2.4,.8,-1.6);
  ENV.wheat.userData.sacks.forEach((s,i)=>s.position.set(-2.6+i*.4,.95,-.6));
  pig.g.rotation.set(0,0,0);pig.b.rotation.set(0,0,0);
  const amp=AMP[f]||0;
  const o={open:amp,blink:((T+.7)%3.4)<.12};
  const e=PLANS[pl.id](lt,d,pl,o);ENV[e].visible=true;
  // fire / candle / dust / wheat anim
  ENV.hut.userData.flames.forEach(fl=>{const u=fl.userData;const k=1+Math.sin(T*11+u.i*2)*.15+Math.sin(T*17+u.i)*.08;fl.scale.set(u.r*(1+.1*Math.sin(T*9+u.i)),u.h*k,u.r);fl.position.y=u.h*k/2+.1});
  if(fireL.intensity>0)fireL.intensity*=1+Math.sin(T*13)*.1+Math.sin(T*23)*.06;
  ENV.hut.userData.shafts.visible=e==='hut'&&sun.intensity>1;
  ENV.hut.userData.shafts.children.forEach(c=>{if(c.userData.dust!=null){const i=c.userData.dust;c.position.y=((rnd(i+1)*3.5+T*.08*(.5+rnd(i)))%3.5)+.1}});
  if(e==='wheat')updWheat(ENV.wheat,T);
  ENV.barber.userData.candle.scale.y=.09*(1+Math.sin(T*15)*.15);
  const L={t:T,...(o.L||{}),blink:o.blink&&!(o.L&&o.L.expr==='sleep')};poseLouis(louis,L);
  // camera shake & cut punch
  const punch=Math.max(0,1-lt/.18);camera.fov*=1+.06*punch;camera.updateProjectionMatrix();
  if(shake>0){camera.position.x+=Math.sin(T*47)*shake;camera.position.y+=Math.cos(T*53)*shake;camera.rotation.z+=Math.sin(T*31)*shake*.5}
  renderer.render(scene,camera);
  o.flash=Math.max(0,.55-lt*4)*(pl.id==='p01'?0:1);
  svg.innerHTML=overlay(T,pl,lt,o);
};
window.dbg=()=>({cam:camera.position.toArray(),pig:pig.g.position.toArray(),pigScale:pig.g.scale.toArray(),fov:camera.fov,louis:louis.root.position.toArray(),head:louis.head.getWorldPosition(new THREE.Vector3()).toArray()});
window.ready=true;
