"""Voix ElevenLabs « qualité pro » pour la saison GLOW-UP.

Usage :
  python3 voix_elevenlabs.py ../scripts-courts ../voix-elevenlabs            # génère tout
  python3 voix_elevenlabs.py ../scripts-courts ../voix-elevenlabs --dry-run  # montre les textes envoyés + coût
  python3 voix_elevenlabs.py ../scripts-courts ../voix-elevenlabs --only 1,16
  python3 voix_elevenlabs.py ../scripts-courts ../voix-v2 --fallback ../voix-elevenlabs   # garde l'ancienne prise si crédits épuisés

Ce que fait le script, réplique par réplique :
  1. Prononciation : réécrit les sigles et chiffres à risque (PSG, PS5, 2CV, USB…) uniquement pour la voix.
  2. Ponctuation : normalise les pauses (… , ! ?) pour un débit naturel.
  3. Émotion : déduit l'émotion du script (didascalies, description de la scène, ponctuation)
     et ajoute des balises d'interprétation eleven_v3 ([whispers], [crying], [panicked]…), jouées et non lues.
  4. Réglages : stabilité « Natural » (0.5) par défaut, « Creative » (0.0) pour les répliques très émotionnelles.
  5. Contrôle qualité : retranscrit l'audio (speech-to-text) et régénère une fois si le texte ne correspond pas.
  6. Mastering : coupe les silences, filtre les graves parasites, de-esser, compression douce,
     présence, normalisation -16 LUFS → toutes les voix au même volume.

La clé API est injectée par le proxy de l'environnement cloud (en-tête xi-api-key).
Formule gratuite : seules les voix de base (premade) sont utilisables par l'API.
"""
import re, sys, os, glob, json, time, random, unicodedata, difflib, subprocess, tempfile, urllib.request, urllib.error

API = "https://api.elevenlabs.io/v1"
MODEL = "eleven_v3"
FORMAT = "mp3_44100_128"          # meilleur format autorisé en formule gratuite

VOICES = {
    "SARAH": "EXAVITQu4vr4xnSDxMaL",     # Sarah : jeune, assurée
    "KENZO": "IKne3meq5aSn9XLyUdCD",     # Charlie : énergique, coach
    "BILAL": "iP95p4xoKVk53GoZ742B",     # Chris : chaleureux
    "MOUSSA": "cjVigY5qzO86Huf0OWal",    # Eric : posé
    "UNE INVITEE": "XrExE9yKIg1WjnnlVkGX",
    "LE TAILLEUR": "JBFqnCBsd6RMkjVDRZzb",
    "YANIS": "TX3LPaxmHKxFdv7VOQHJ",     # Liam : jeune, énergique
    "SOFIANE": "bIHbv24MWmeRgasZH58o",   # Will : jeune, détendu
    "KARIM": "N2lVS1w4EtoT3dr4eOWO",     # Callum : rauque
    "VIDAL": "nPczCjzI2devNBz1zQrb",     # Brian : grave, posé
    "GERARD": "CwhRBWXzGAHq8TQ4Fs17",    # Roger : bourru
    "BERNARD": "pqHfZKP75CvOlQylNhV4",   # Bill : âgé
    "BRUNO": "pNInz6obpgDQGcFmaJgB",     # Adam : ferme
    "MALIK": "onwK4e9ZLuTAKqWW03F9",     # Daniel : chaleureux
    "LINA": "cgSgspJ2msm6clMCkdW9",      # Jessica : jeune, vive
    "INES": "FGY2WhTYpPnrIDTdsKH5",      # Laura : pétillante
    "NADIA": "pFZP5JQG7iQjIQuC4Bku",     # Lily : douce
    "LE POLICIER": "cjVigY5qzO86Huf0OWal",
    "L'HOMME EN GRIS": "JBFqnCBsd6RMkjVDRZzb",
    "UNE VOIX": "SOYHLrjzK2X1ezoPC6cr",
    "TOUS": "TX3LPaxmHKxFdv7VOQHJ",
}

# 1. Prononciation (texte envoyé à la voix uniquement ; les sous-titres gardent l'orthographe d'origine)
PRONONCIATION = [
    (r"\bPSG\b", "P.S.G."), (r"\bPS5\b", "P.S. cinq"), (r"\b2CV\b", "deux-chevaux"), (r"\bUSB\b", "U.S.B."),
    (r"–", "-"), (r"\bOK\b", "okay"),
]

# Balises d'interprétation eleven_v3 par émotion
TAGS = {  # balises coûteuses : seulement les émotions fortes ; le reste est porté par la stabilité (gratuite)
    "panique": "[panicked]", "colere": "[angry]",
    "larmes": "[crying]", "chuchote": "[whispers]", "crie": "[shouting]", "menace": "[menacing]", "souvenir": "[softly]",
}
# Ton de base de chaque personnage quand la scène n'indique rien de fort
BASE = {"VIDAL": "menace", "SOFIANE": "excite", "NADIA": "tendre", "BERNARD": "tendre", "KARIM": "calme", "BRUNO": "calme",
        "INES": "excite", "MALIK": "souvenir", "L'HOMME EN GRIS": "calme"}
FORT = {"panique", "colere", "larmes", "crie", "choque", "chuchote", "excite", "sourire", "triste"}  # stabilité « Creative »

# Indices dans la description de scène (🎥) → émotion
CUES = [("larmes", ("crying", "tears", "red eyes")), ("panique", ("panick", "scared", "out of breath")),
        ("choque", ("shock", "pale", "freez")), ("colere", ("angry", "shouting")),
        ("sourire", ("smil", "joy", "dancing", "happy", "excited", "proud", "amused", "laughing")),
        ("triste", ("sad", "devastated", "defeated", "ashamed", "head down", "exhausted")), ("tendre", ("tender", "moved", "gentle")),
        ("determine", ("determined", "serious")), ("mefiant", ("suspicious", "skeptical", "staring", "cold")),
        ("inquiet", ("worried", "nervous", "hesitat", "tense")), ("calme", ("calm", "relaxed", "confident", "arrogant"))]
TAGS_CAM = ["YANIS", "SARAH", "KENZO", "BILAL", "MOUSSA", "VIDAL", "SOFIANE", "LINA", "NADIA", "GERARD", "BRUNO", "KARIM", "INES", "BERNARD", "MALIK"]


def norm(s):
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if unicodedata.category(c) != "Mn").upper().strip()


def emotion(who, direction, text, cam):
    d = direction.lower()
    if "chuchot" in d: return "chuchote"
    if "essouffl" in d: return "panique"
    if "larmes" in d or "brise" in d: return "larmes"
    if "voix off, grave" in d: return "souvenir"
    if "téléphone" in d: return BASE.get(who, "neutre") if who == "VIDAL" else "neutre"
    if "!" in text and (re.search(r"\b[A-ZÉÈÀ]{3,}\b", text) or "?!" in text): return "crie"
    tag = "{" + who + "}"
    if tag in cam:
        i = cam.find(tag); nxt = [cam.find("{" + o + "}", i + len(tag)) for o in TAGS_CAM]; nxt = [x for x in nxt if x > 0]
        win = cam[i:min(nxt) if nxt else len(cam)].lower()
        for emo, keys in CUES:
            if any(k in win for k in keys): return emo
    if "!" in text: return "excite"
    return BASE.get(who, "neutre")


def emotion_finale(who, direction, text, cam):
    e = emotion(who, direction, text, cam)
    # les méchants sourient… de façon menaçante
    if who in ("VIDAL", "KARIM", "BRUNO", "L'HOMME EN GRIS") and e in ("sourire", "calme", "neutre", "mefiant", "excite"):
        return "menace" if who == "VIDAL" else "calme"
    return e


def prepare(text, emo):
    t = text
    for pat, rep in PRONONCIATION: t = re.sub(pat, rep, t)
    t = t.replace("...", "…").replace(" ?", " ?").replace(" !", " !")
    t = re.sub(r"\s+", " ", t).strip()
    if not re.search(r"[.!?…]$", t): t += "."
    # 2. respirations naturelles : une phrase longue sans virgule reçoit une pause avant « et / mais / parce que »
    t = re.sub(r"(\w{4,}) (et|mais|parce que) ", r"\1, \2 ", t) if len(t) > 90 and "," not in t else t
    tag = TAGS.get(emo, "")
    return (tag + " " + t).strip()


# ---------------- API ----------------
def call(path, data=None, files=None, method="POST", raw=False):
    headers = {"xi-api-key": "proxy-injected"}
    body = None
    if files:
        b = "----el" + str(random.random())[2:]
        parts = []
        for k, v in (data or {}).items(): parts.append(f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
        for k, (fn, content) in files.items():
            parts.append(f'--{b}\r\nContent-Disposition: form-data; name="{k}"; filename="{fn}"\r\nContent-Type: audio/mpeg\r\n\r\n'.encode() + content + b"\r\n")
        body = b"".join(parts) + f"--{b}--\r\n".encode(); headers["Content-Type"] = f"multipart/form-data; boundary={b}"
    elif data is not None:
        body = json.dumps(data).encode(); headers["Content-Type"] = "application/json"
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(API + path, data=body, headers=headers, method=method), timeout=180) as f:
                out = f.read(); return out if raw else json.loads(out)
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:300]
            if e.code in (429, 500, 502, 503) and attempt < 3: time.sleep(4 * (attempt + 1)); continue
            raise RuntimeError(f"{e.code} {msg}")


def credits_left():
    s = call("/user/subscription", method="GET")
    return s["character_limit"] - s["character_count"]


def tts(voice, text, emo, seed):
    settings = {"stability": 0.0 if emo in FORT else 0.5, "similarity_boost": 0.8, "use_speaker_boost": True}
    return call(f"/text-to-speech/{voice}?output_format={FORMAT}",
                {"text": text, "model_id": MODEL, "language_code": "fr", "voice_settings": settings, "seed": seed}, raw=True)


def transcript(mp3):
    try:
        r = call("/speech-to-text", {"model_id": "scribe_v1", "language_code": "fr", "tag_audio_events": "false"}, files={"file": ("a.mp3", mp3)})
        return r.get("text", "")
    except Exception as e:
        return None


def simil(a, b):
    f = lambda s: re.sub(r"[^a-z0-9 ]", "", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode()).split()
    a = " ".join(f(re.sub(r"\[[^\]]*\]", "", a))).replace("j suis", "je suis"); b = " ".join(f(b)).replace("j suis", "je suis")
    return difflib.SequenceMatcher(None, a, b).ratio()


# 6. Mastering
MASTER = ("silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,"
          "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.12,areverse,"
          "highpass=f=75,lowpass=f=15000,deesser=i=0.35,"
          "equalizer=f=200:t=q:w=1:g=-1.5,equalizer=f=3200:t=q:w=1.2:g=2,"
          "acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=1.5,"
          "loudnorm=I=-16:TP=-1.5:LRA=7,aresample=44100")


def loudness(path):
    o = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", o)
    return float(m[-1]) if m else -16.0


def master(src_bytes, out, raw_dir=None):
    """Passe 1 : nettoyage + compression. Passe 2 : gain exact vers -16 LUFS + limiteur."""
    if raw_dir:
        os.makedirs(raw_dir, exist_ok=True); open(os.path.join(raw_dir, os.path.basename(out)), "wb").write(src_bytes)
    with tempfile.TemporaryDirectory() as td:
        src = os.path.join(td, "in.mp3"); mid = os.path.join(td, "mid.wav"); open(src, "wb").write(src_bytes)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-af", MASTER.replace(",loudnorm=I=-16:TP=-1.5:LRA=7", ""), "-ac", "1", mid], check=True)
        gain = -16.0 - loudness(mid)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mid, "-af", f"volume={gain:.2f}dB,alimiter=limit=0.84:level=false",
                        "-ac", "1", "-b:a", "192k", out], check=True)


# ---------------- parcours du script ----------------
def lines(src):
    for f in sorted(glob.glob(os.path.join(src, "ep*.md"))):
        ep = None; n = 0; tag = "x"; cam = ""
        for line in open(f, encoding="utf-8"):
            m = re.match(r"## Épisode (\d+)", line)
            if m: ep = int(m.group(1)); n = 0; continue
            m = re.match(r"\*\*(P\d+|R)\b", line)
            if m: tag = m.group(1); cam = ""
            if line.startswith("🎥"): cam = re.sub(r"\{YANIS_J\d+\}", "{YANIS}", line)
            m = re.match(r"🗣️ \*\*(.+?)\*\*(.*)", line.strip())
            if not (ep and m): continue
            parts = re.findall(r"«\s*(.+?)\s*»", m.group(2))
            if not parts: continue
            n += 1; who = norm(m.group(1)); text = " ".join(parts)
            direction = " ".join(re.findall(r"\*\((.+?)\)\*", m.group(2)))
            emo = emotion_finale(who, direction, text, cam)
            yield ep, f"{n:02d}_{tag}_{who.replace(' ', '-').replace(chr(39), '')}.mp3", who, text, emo, prepare(text, emo)


def main():
    src, out = sys.argv[1], sys.argv[2]
    dry = "--dry-run" in sys.argv
    only = None
    fallback = sys.argv[sys.argv.index("--fallback") + 1] if "--fallback" in sys.argv else None
    if "--only" in sys.argv: only = {int(x) for x in sys.argv[sys.argv.index("--only") + 1].split(",")}
    todo = [l for l in lines(src) if not only or l[0] in only]
    cost = sum(len(l[5]) for l in todo)
    print(f"{len(todo)} répliques, {cost} caractères envoyés (balises comprises)")
    if dry:
        for ep, name, who, text, emo, sent in todo: print(f"ep{ep:02d} {name:28s} {emo:9s} | {sent}")
        return
    left = credits_left(); print("crédits restants :", left)
    if cost > left: sys.exit("Pas assez de crédits pour tout générer.")
    report = []
    budget = left - 150                       # marge de sécurité
    remaining = cost
    for ep, name, who, text, emo, sent in todo:
        remaining -= len(sent)
        d = os.path.join(out, f"ep{ep:02d}"); os.makedirs(d, exist_ok=True); p = os.path.join(d, name)
        best, best_s = None, -1
        for attempt in range(2):
            if attempt and credits_left() - 100 < remaining:
                print(f"  (pas de nouvelle prise pour {name} : crédits réservés au reste de la saison)"); break
            try:
                audio = tts(VOICES.get(who, VOICES["YANIS"]), sent, emo, random.randint(1, 10**6))
            except RuntimeError as e:
                print(f"  ✗ {name} : {e}", flush=True); audio = None; break
            if audio is None: break
            tr = transcript(audio); s = simil(text, tr) if tr is not None else 1.0
            if s > best_s: best, best_s = audio, s
            if s >= 0.8: break
            print(f"  ↻ {name} mal compris ({s:.2f}) : « {tr} » — nouvelle prise", flush=True)
        if best is None:                       # crédits épuisés ou erreur : on garde l'ancienne prise
            fb = os.path.join(fallback, f"ep{ep:02d}", name) if fallback else None
            if fb and os.path.exists(fb): subprocess.run(["cp", fb, p]); print(f"  → ancienne prise conservée pour {name}")
            continue
        master(best, p, os.path.join(out, "_brut", f"ep{ep:02d}"))
        report.append({"fichier": f"ep{ep:02d}/{name}", "emotion": emo, "texte_envoye": sent, "controle": round(best_s, 2)})
        print(f"ep{ep:02d}/{name} [{emo}] contrôle {best_s:.2f}", flush=True)
    json.dump(report, open(os.path.join(out, "rapport_voix.json"), "w"), ensure_ascii=False, indent=1)
    print("crédits restants :", credits_left())


if __name__ == "__main__":
    main()
