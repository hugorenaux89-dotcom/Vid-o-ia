"""Génère les voix de la version courte avec ElevenLabs (même nommage que voix2.py).
Usage : python3 voix_elevenlabs.py ../scripts-courts ../voix-elevenlabs
La clé API est injectée par le proxy de l'environnement cloud (en-tête xi-api-key) : aucune variable à définir.
Ensuite : python3 build2.py ../scripts-courts ../voix-elevenlabs ../videos
Formule gratuite : voix de base d'ElevenLabs (les voix de la bibliothèque et la création de voix demandent un abonnement payant).
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

# Formule gratuite : seules les voix de base (premade) sont utilisables par l'API.
VOICES = {
    "YANIS": "TX3LPaxmHKxFdv7VOQHJ",     # Liam : jeune, énergique
    "SOFIANE": "bIHbv24MWmeRgasZH58o",   # Will : jeune, détendu
    "KARIM": "N2lVS1w4EtoT3dr4eOWO",     # Callum
    "VIDAL": "nPczCjzI2devNBz1zQrb",     # Brian : grave, posé
    "GERARD": "CwhRBWXzGAHq8TQ4Fs17",    # Roger
    "BERNARD": "pqHfZKP75CvOlQylNhV4",   # Bill : âgé
    "BRUNO": "pNInz6obpgDQGcFmaJgB",     # Adam : ferme
    "MALIK": "onwK4e9ZLuTAKqWW03F9",     # Daniel
    "LINA": "cgSgspJ2msm6clMCkdW9",      # Jessica : jeune, vive
    "INES": "FGY2WhTYpPnrIDTdsKH5",      # Laura : pétillante
    "NADIA": "pFZP5JQG7iQjIQuC4Bku",     # Lily : douce
    "LE POLICIER": "cjVigY5qzO86Huf0OWal",
    "L'HOMME EN GRIS": "JBFqnCBsd6RMkjVDRZzb",
    "UNE VOIX": "SOYHLrjzK2X1ezoPC6cr",
    "TOUS": "TX3LPaxmHKxFdv7VOQHJ",
}
def pick_voices(): return VOICES

STYLE = {"whisper": 0.15, "shout": 0.8, "sad": 0.6, "excited": 0.6}
def main():
    os.makedirs(OUT, exist_ok=True)
    only = set(sys.argv[3].split(",")) if len(sys.argv) > 3 else None
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
            if only and f"{ep}" not in only: continue
            d = os.path.join(OUT, f"ep{ep:02d}"); os.makedirs(d, exist_ok=True)
            p = os.path.join(d, f"{n:02d}_{tag}_{who.replace(' ', '-').replace(chr(39), '')}.mp3")
            if os.path.exists(p): continue
            direc = m.group(2).lower()
            emo = "whisper" if "chuchot" in direc else "sad" if ("larmes" in direc or "brise" in direc) else \
                  "shout" if ("!" in text and re.search(r"\b[A-ZÉÈ]{3,}\b", text)) else "excited" if "!" in text else "normal"
            body = {"text": text, "model_id": MODEL, "voice_settings": {"stability": 0.35, "similarity_boost": 0.8, "style": STYLE.get(emo, 0.35), "use_speaker_boost": True}}
            audio = req(f"/text-to-speech/{voices.get(who, voices['YANIS'])}?output_format=mp3_44100_128", body, "POST")
            open(p, "wb").write(audio); print(p, flush=True); time.sleep(0.3)

if __name__ == "__main__":
    main()
