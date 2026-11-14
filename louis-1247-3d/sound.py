import json, numpy as np, wave
SR=44100; V=json.load(open("voice.json")); TOT=V["total"]; N=int(TOT*SR)
P={p["id"]:p for p in V["plans"]}
rng=np.random.default_rng(7)
def wt(pid,w):
    for x in P[pid]["words"]:
        if x["w"].lower().startswith(w.lower()): return x["t"]
    return P[pid]["start"]
def env(n,a=.005,r=.1):
    e=np.ones(n);ia=int(a*SR);ir=int(r*SR);e[:ia]=np.linspace(0,1,ia);e[-ir:]*=np.linspace(1,0,ir);return e
def add(buf,t,sig,g=1.0):
    i=int(t*SR);j=min(len(buf),i+len(sig));
    if i<len(buf): buf[i:j]+=sig[:j-i]*g
# ---------- music: Karplus-Strong lute + drone + frame drum ----------
def pluck(f,dur,bright=.5):
    n=int(dur*SR);p=int(SR/f);buf=rng.uniform(-1,1,p);out=np.zeros(n)
    for i in range(n):
        out[i]=buf[i%p]; buf[i%p]=.5*(buf[i%p]+buf[(i+1)%p])*.996
    return out*env(n,.002,.05)
cache={}
def pl(f,d):
    k=(round(f,2),d)
    if k not in cache: cache[k]=pluck(f,d)
    return cache[k]
bpm=116;beat=60/bpm
D=146.83;scale=[0,2,3,5,7,9,10,12,14,15,17,19,21,22,24]  # D dorian
fq=lambda deg:D*2**(scale[deg]/12)
mel=[7,9,10,9,7,5,7,4, 7,9,10,12,10,9,7,7, 5,7,9,7,5,4,2,4, 7,5,4,2,0,2,4,0]
music=np.zeros(N)
t=0;i=0
while t<TOT:
    deg=mel[i%len(mel)]
    add(music,t,pl(fq(deg)*2,beat*1.5),.35)
    if i%2==0: add(music,t,pl(fq([0,0,3,4][(i//8)%4]),beat*2.2),.3)
    # frame drum
    if i%4 in (0,3):
        n=int(.25*SR);tt=np.arange(n)/SR;dr=np.sin(2*np.pi*(90*np.exp(-tt*8)+50)*tt)*np.exp(-tt*14);add(music,t,dr,.55)
    if i%4==2:
        n=int(.08*SR);add(music,t,rng.normal(0,1,n)*np.exp(-np.arange(n)/SR*60),.12)
    t+=beat/2;i+=1
# drone
tt=np.arange(N)/SR;drone=(np.sin(2*np.pi*D/2*tt)+.5*np.sin(2*np.pi*D*3/4*tt))*.06*(1+.2*np.sin(tt*.7))
music+=drone
# silence music during quiz pause + duck under voice
gain=np.ones(N)
q0=P["p06"]["start"]+P["p06"]["dur"]-1.75;q1=P["p06"]["start"]+P["p06"]["dur"]
gain[int(q0*SR):int(q1*SR)]=0.0
w=wave.open("audio/voice.wav");vo=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
vo=np.pad(vo,(0,max(0,N-len(vo))))[:N]
envv=np.convolve(np.abs(vo),np.ones(2205)/2205,'same');duck=1-.55*np.clip(envv/.05,0,1)
music*=gain*duck
music=music/np.max(np.abs(music))*.22
# ---------- sfx ----------
sfx=np.zeros(N)
def whoosh(d=.35):
    n=int(d*SR);x=rng.normal(0,1,n);y=np.zeros(n);a=0
    for i in range(n):
        c=.02+.4*(i/n);a=a+c*(x[i]-a);y[i]=a
    return y*np.sin(np.linspace(0,np.pi,n))*1.2
def tone(f,d,dec=6,typ='sin'):
    n=int(d*SR);t=np.arange(n)/SR;s=np.sin(2*np.pi*f*t) if typ=='sin' else np.sign(np.sin(2*np.pi*f*t))*.4
    return s*np.exp(-t*dec)*env(n,.002,.02)
def sweep(f0,f1,d,dec=3):
    n=int(d*SR);t=np.arange(n)/SR;f=np.linspace(f0,f1,n);return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*dec)*env(n,.005,.03)
def oink():
    n=int(.35*SR);t=np.arange(n)/SR;f=260-140*t/0.35+30*np.sin(t*60);ph=np.cumsum(f)/SR
    s=np.sign(np.sin(2*np.pi*ph))*.5+rng.normal(0,.15,n);s=np.convolve(s,np.ones(12)/12,'same')
    return s*np.sin(np.linspace(0,np.pi,n))**.5
WH=whoosh()
for p in V["plans"][1:]: add(sfx,p["start"]-.12,WH,.35)
add(sfx,.15,oink(),.6);add(sfx,.6,oink(),.5)
# rewind
add(sfx,P["p02"]["start"],np.concatenate([sweep(1800,300,.4,1) for _ in range(3)]),.25)
# objet caché sparkle
for k in range(4): add(sfx,P["p04"]["start"]+P["p04"]["sent"][1]["t"]-P["p04"]["start"]+.1+k*.07,tone(1600+k*400,.25,12),.25)
# quiz: pop + ticks + ding
add(sfx,P["p06"]["sent"][1]["t"]+.2,tone(880,.15,20),.4)
for k in range(3): add(sfx,q0+k*.55,tone(1200,.08,30,'sq'),.5)
add(sfx,P["p07"]["start"],tone(1318,.6,5)+tone(1760,.6,5),.4)
add(sfx,wt("p07","mythe"),tone(220,.3,8,'sq'),.35)
# nutella buzzer
add(sfx,P["p08"]["sent"][1]["t"],tone(150,.35,4,'sq'),.35)
# ox moo-ish
add(sfx,P["p09"]["sent"][1]["t"]+.3,sweep(140,110,.8,1.5)*.8,.4)
# rumble + gallop
n=int(2.0*SR);rb=np.convolve(rng.normal(0,1,n),np.ones(400)/400,'same')*np.linspace(0,1,n)*4;add(sfx,P["p11"]["start"],rb,.5)
for k in range(int(P["p12"]["sent"][1]["t"]-P["p12"]["start"])*4+4):
    for o in (0,.09): add(sfx,P["p12"]["start"]+k*.25+o,tone(320,.06,40)+rng.normal(0,.2,int(.06*SR))*np.exp(-np.arange(int(.06*SR))/SR*60),.35)
add(sfx,wt("p12","corvée"),tone(220,.3,8,'sq'),.3)
# boing on bow
add(sfx,P["p13"]["start"]+.3,sweep(200,600,.4,4)*np.sin(np.linspace(0,30,int(.4*SR))),.35)
# choice pops
for k in range(3): add(sfx,P["p14"]["start"]+k*P["p14"]["dur"]/3*1.05,tone(700+k*200,.12,20),.35)
# aïe
add(sfx,P["p15"]["start"]+.3,sweep(900,400,.25,6),.3)
# honey + saignée sting + run
add(sfx,wt("p17","miel"),tone(1318,.5,5),.3)
add(sfx,wt("p18","saignée"),sweep(400,90,.7,2,)*1.0,.35)
for k in range(10): add(sfx,P["p18"]["sent"][1]["t"]+.2+k*.12,tone(180,.05,50),.4)
# oink snuggle
add(sfx,P["p20"]["start"]+.6,oink(),.5)
# end ding
add(sfx,P["p22"]["sent"][2]["t"],tone(988,.5,5)+tone(1318,.5,5),.3)
mix=vo*1.0+music+sfx*.9
mix=mix/np.max(np.abs(mix))*.95
with wave.open("audio/mix.wav","wb") as w:
    w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((mix*32767).astype(np.int16).tobytes())
print("ok",TOT)
