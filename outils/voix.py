"""Génère la voix off d'un épisode (ElevenLabs, avec minutage mot par mot)."""
import json, sys, base64, urllib.request, os
VOICE = "nPczCjzI2devNBz1zQrb"  # Brian
src, out = sys.argv[1], sys.argv[2]
segs = json.load(open(src))
os.makedirs(out, exist_ok=True)
texts = [s["text"] for s in segs]
for i, s in enumerate(segs):
    path = f"{out}/{s['id']}.json"
    if os.path.exists(path):
        continue
    body = {"text": s["text"], "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.42, "similarity_boost": 0.8, "style": 0.35, "use_speaker_boost": True},
            "previous_text": " ".join(texts[max(0, i-2):i]), "next_text": " ".join(texts[i+1:i+2])}
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps?output_format=mp3_44100_128",
        data=json.dumps(body).encode(), headers={"xi-api-key": "dummy", "Content-Type": "application/json"})
    d = json.load(urllib.request.urlopen(req))
    open(f"{out}/{s['id']}.mp3", "wb").write(base64.b64decode(d["audio_base64"]))
    al = d["alignment"]
    words, cur, start = [], "", None
    for ch, a, b in zip(al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]):
        if ch.isspace():
            if cur: words.append({"w": cur, "s": start, "e": end}); cur = ""
            continue
        if not cur: start = a
        cur += ch; end = b
    if cur: words.append({"w": cur, "s": start, "e": end})
    json.dump({"words": words, "dur": al["character_end_times_seconds"][-1]}, open(path, "w"), ensure_ascii=False, indent=1)
    print(s["id"], round(al["character_end_times_seconds"][-1], 2), "s")
