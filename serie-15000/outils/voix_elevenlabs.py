"""Génère les voix de la version courte avec ElevenLabs (même nommage que voix2.py).
Usage : python3 voix_elevenlabs.py ../scripts-courts ../voix-elevenlabs
La clé API est injectée par le proxy de l'environnement cloud (en-tête xi-api-key) : aucune variable à définir.
Ensuite : python3 build2.py ../scripts-courts ../voix-elevenlabs ../videos
⚠️ Non testé tant qu'une clé valide n'est pas disponible.
"""
import re, sys, os, glob, json, time, unicodedata, urllib.request

SRC, OUT = sys.argv[1], sys.argv[2]
API = "https://api.elevenlabs.io/v1"
MODEL = "eleven_multilingual_v2"

def req(path, data=None, method=None):
    r = urllib.request.Request(API + path, data=json.dumps(data).encode() if data is not None else None, method=method,
                               headers={"Content-Type": "application/json", "xi-api-key": "proxy-injected", "Accept": "*/*"})
    with urllib.request.urlopen(r, timeout=120) as f: return f.read()

def norm(s):
    s = unicodedata.normalize("NFD", s); return "".join(c for c in s if unicodedata.category(c) != "Mn").upper().strip()

# Choix des voix : voix de la bibliothèque, langue française, par genre / âge.
WANT = {  # personnage: (genre, âge, réglage style)
    "YANIS": ("male", "young"), "SOFIANE": ("male", "young"), "KARIM": ("male", "young"), "LINA": ("female", "young"),
    "INES": ("female", "young"), "VIDAL": ("male", "middle_aged"), "GERARD": ("male", "old"), "BERNARD": ("male", "old"),
    "BRUNO": ("male", "middle_aged"), "MALIK": ("male", "middle_aged"), "NADIA": ("female", "middle_aged"),
    "LE POLICIER": ("male", "middle_aged"), "L'HOMME EN GRIS": ("male", "middle_aged"), "UNE VOIX": ("male", "middle_aged"), "TOUS": ("male", "young"),
}
def pick_voices():
    cache = os.path.join(OUT, "voix_choisies.json")
    if os.path.exists(cache): return json.load(open(cache))
    pool = json.loads(req("/shared-voices?language=fr&page_size=100&sort=usage_character_count_1y"))["voices"]
    chosen, used = {}, set()
    for who, (g, age) in WANT.items():
        cands = [v for v in pool if v.get("gender") == g and v.get("age") == age and v["voice_id"] not in used] or \
                [v for v in pool if v.get("gender") == g and v["voice_id"] not in used]
        v = cands[0]; used.add(v["voice_id"])
        req(f"/voices/add/{v['public_owner_id']}/{v['voice_id']}", {"new_name": f"{who.title()} (série)"}, "POST")
        chosen[who] = v["voice_id"]
    json.dump(chosen, open(cache, "w"), indent=1)
    return chosen

STYLE = {"whisper": 0.15, "shout": 0.8, "sad": 0.6, "excited": 0.6}
def main():
    os.makedirs(OUT, exist_ok=True)
    voices = pick_voices()
    for f in sorted(glob.glob(os.path.join(SRC, "ep*.md"))):
        ep = None; n = 0; tag = "x"
        for line in open(f, encoding="utf-8"):
            m = re.match(r"## Épisode (\d+)", line)
            if m: ep = int(m.group(1)); n = 0; continue
            m = re.match(r"\*\*(P\d+|R)\b", line)
            if m: tag = m.group(1)
            m = re.match(r"🗣️ \*\*(.+?)\*\*(.*)", line.strip())
            if not (ep and m): continue
            parts = re.findall(r"«\s*(.+?)\s*»", m.group(2))
            if not parts: continue
            n += 1; who = norm(m.group(1)); text = " ".join(parts)
            d = os.path.join(OUT, f"ep{ep:02d}"); os.makedirs(d, exist_ok=True)
            p = os.path.join(d, f"{n:02d}_{tag}_{who.replace(' ', '-').replace(chr(39), '')}.mp3")
            if os.path.exists(p): continue
            direc = m.group(2).lower()
            emo = "whisper" if "chuchot" in direc else "sad" if ("larmes" in direc or "brise" in direc) else \
                  "shout" if ("!" in text and re.search(r"\b[A-ZÉÈ]{3,}\b", text)) else "excited" if "!" in text else "normal"
            body = {"text": text, "model_id": MODEL, "language_code": "fr",
                    "voice_settings": {"stability": 0.35, "similarity_boost": 0.8, "style": STYLE.get(emo, 0.35), "use_speaker_boost": True}}
            audio = req(f"/text-to-speech/{voices.get(who, voices['YANIS'])}?output_format=mp3_44100_128", body, "POST")
            open(p, "wb").write(audio); print(p, flush=True); time.sleep(0.3)

if __name__ == "__main__":
    main()
