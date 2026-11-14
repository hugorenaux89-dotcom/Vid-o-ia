import asyncio, json, os, ssl, edge_tts, edge_tts.communicate as ec
ec._SSL_CTX=ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
VOICE="fr-FR-RemyMultilingualNeural"
async def one(s):
    c=edge_tts.Communicate(s["text"],VOICE,rate="+6%",boundary="WordBoundary",proxy=os.environ.get("HTTPS_PROXY"))
    words=[]
    with open(f"audio/{s['id']}.mp3","wb") as f:
        async for ch in c.stream():
            if ch["type"]=="audio": f.write(ch["data"])
            elif ch["type"]=="WordBoundary":
                words.append({"t":ch["offset"]/1e7,"d":ch["duration"]/1e7,"w":ch["text"]})
    json.dump(words,open(f"audio/{s['id']}.json","w"),ensure_ascii=False)
async def main():
    for s in json.load(open("script.json")): await one(s)
asyncio.run(main())
