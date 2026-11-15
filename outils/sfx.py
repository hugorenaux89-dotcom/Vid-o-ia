"""Génère les bruitages d'un épisode (ElevenLabs sound generation)."""
import json, sys, urllib.request, os
lst, out = json.load(open(sys.argv[1])), sys.argv[2]
os.makedirs(out, exist_ok=True)
for name, (prompt, dur) in lst.items():
    p = f"{out}/{name}.mp3"
    if os.path.exists(p): continue
    body = {"text": prompt, "duration_seconds": dur, "prompt_influence": 0.6}
    if name.startswith("musique"): body["loop"] = True
    req = urllib.request.Request("https://api.elevenlabs.io/v1/sound-generation?output_format=mp3_44100_128",
        data=json.dumps(body).encode(), headers={"xi-api-key": "dummy", "Content-Type": "application/json"})
    try:
        open(p, "wb").write(urllib.request.urlopen(req).read()); print("ok", name)
    except urllib.error.HTTPError as e:
        print("ERR", name, e.code, e.read()[:300])
