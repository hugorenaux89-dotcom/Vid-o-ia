import json, subprocess, numpy as np
FPS=30; PAD=0.35; SR=24000
script=json.load(open("script.json"))
t=0; scenes=[]; parts=[]
for i,s in enumerate(script):
    wav=subprocess.run(["ffmpeg","-v","error","-i",f"audio/{s['id']}.mp3","-f","s16le","-ac","1","-ar",str(SR),"-"],capture_output=True).stdout
    a=np.frombuffer(wav,dtype=np.int16).astype(np.float32)/32768
    lead=0.15 if i else 0.05
    pad=np.zeros(int(SR*lead),np.float32); tail=np.zeros(int(SR*PAD),np.float32)
    seg=np.concatenate([pad,a,tail]); dur=len(seg)/SR
    words=[{"t":round(t+lead+w["t"],3),"e":round(t+lead+w["t"]+w["d"],3),"w":w["w"]} for w in json.load(open(f"audio/{s['id']}.json"))]
    scenes.append({**s,"start":round(t,3),"dur":round(dur,3),"words":words})
    parts.append(seg); t+=dur
voice=np.concatenate(parts)
# small fade tail
voice=np.concatenate([voice,np.zeros(int(SR*0.6),np.float32)])
import wave
with wave.open("audio/voice.wav","wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(voice,-1,1)*32767).astype(np.int16).tobytes())
total=len(voice)/SR; n=int(total*FPS)
hop=SR//FPS; amp=[]
for f in range(n):
    x=voice[f*hop:f*hop+hop]; amp.append(float(np.sqrt(np.mean(x*x))) if len(x) else 0)
amp=np.array(amp); amp=np.clip(amp/np.percentile(amp[amp>0.005],90),0,1)
json.dump({"fps":FPS,"total":total,"frames":n,"scenes":scenes,"amp":[round(float(v),3) for v in amp]},open("timeline.json","w"),ensure_ascii=False)
print(total,n)
