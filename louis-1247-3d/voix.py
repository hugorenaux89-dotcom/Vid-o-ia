import asyncio, json, os, ssl, re, subprocess, numpy as np, edge_tts, edge_tts.communicate as ec
ec._SSL_CTX=ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
src=open("../louis-1247-v2/voix.py").read()
ns={"os":os}; exec(re.search(r"^V=.*?^\]\n",src,re.S|re.M).group(0),ns)
V,T,P=ns["V"],ns["T"],ns["P"]; PX=os.environ.get("HTTPS_PROXY"); SR=44100
async def tts(text,ton):
    r,p=T[ton]; c=edge_tts.Communicate(text,V,rate=r,pitch=p,proxy=PX,boundary="WordBoundary")
    mp3=b"";words=[]
    async for ch in c.stream():
        if ch["type"]=="audio": mp3+=ch["data"]
        elif ch["type"]=="WordBoundary": words.append([ch["offset"]/1e7,(ch["offset"]+ch["duration"])/1e7,ch["text"]])
    pcm=subprocess.run(["ffmpeg","-v","error","-i","-","-f","f32le","-ac","1","-ar",str(SR),"-"],input=mp3,capture_output=True).stdout
    a=np.frombuffer(pcm,np.float32)
    loud=np.where(np.abs(a)>0.01)[0]
    s0=max(0,loud[0]/SR-0.03); s1=min(len(a)/SR,loud[-1]/SR+0.07)
    words[-1][1]=min(words[-1][1],s1-0.05)
    a=a[int(s0*SR):int(s1*SR)].copy()
    n=int(0.012*SR); a[:n]*=np.linspace(0,1,n); a[-n:]*=np.linspace(1,0,n)
    return a,[[w0-s0,w1-s0,w] for w0,w1,w in words]
async def main():
    out=[];plans=[];t=0
    for pid,lines in P:
        pw=[];p0=t;sent=[]
        for ton,txt,pause in lines:
            a,ws=await tts(txt,ton)
            pw+= [{"t":round(t+w0,3),"e":round(t+w1,3),"w":w} for w0,w1,w in ws]
            sent.append({"t":round(t,3),"e":round(t+len(a)/SR,3),"ton":ton})
            out.append(a); t+=len(a)/SR
            out.append(np.zeros(int(pause*SR),np.float32)); t+=pause
        plans.append({"id":pid,"start":round(p0,3),"dur":round(t-p0,3),"words":pw,"sent":sent})
    a=np.concatenate(out+[np.zeros(int(0.8*SR),np.float32)])
    a=a/np.max(np.abs(a))*0.89
    import wave
    with wave.open("audio/voice.wav","wb") as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((a*32767).astype(np.int16).tobytes())
    json.dump({"total":len(a)/SR,"plans":plans},open("voice.json","w"),ensure_ascii=False)
    print(len(a)/SR)
asyncio.run(main())
