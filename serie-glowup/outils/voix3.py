"""Voix v2 : émotions par réplique, phrase par phrase, pauses naturelles, traitement micro."""
import re, sys, os, asyncio, glob, unicodedata, random, shutil, tempfile, certifi
certifi.where = lambda: "/root/.ccr/ca-bundle.crt"
import edge_tts

SRC, OUT = sys.argv[1], sys.argv[2]
ONLY = set(int(x) for x in sys.argv[3].split(",")) if len(sys.argv) > 3 else None
TMP = tempfile.mkdtemp()
random.seed(7)

# personnage: (voix, vitesse %, hauteur Hz)
V = {
 "YANIS": ("fr-FR-RemyMultilingualNeural", 6, 0),
 "VIDAL": ("fr-FR-HenriNeural", -10, -5),
 "SOFIANE": ("fr-FR-HenriNeural", 16, 9),
 "GERARD": ("fr-BE-GerardNeural", -4, -4),
 "BRUNO": ("fr-CH-FabriceNeural", -12, -12),
 "KARIM": ("fr-FR-RemyMultilingualNeural", -4, -9),
 "BERNARD": ("fr-BE-GerardNeural", -18, 2),
 "MALIK": ("fr-FR-RemyMultilingualNeural", -12, -11),
 "LINA": ("fr-FR-DeniseNeural", 10, 0),
 "NADIA": ("fr-FR-VivienneMultilingualNeural", -4, -2),
 "INES": ("fr-FR-DeniseNeural", 16, 12),
 "LE POLICIER": ("fr-CH-FabriceNeural", -4, 0),
 "L'ACHETEUR": ("fr-CH-FabriceNeural", -8, -6),
 "L'HOMME EN GRIS": ("fr-FR-HenriNeural", -4, 4),
 "UNE VOIX": ("fr-CH-FabriceNeural", 4, -8),
 "TOUS": ("fr-FR-RemyMultilingualNeural", 0, 0),
 "VOIX OFF": ("fr-FR-RemyMultilingualNeural", 6, -2),
}
# émotion: (vitesse, hauteur, volume %, cible loudness, filtre)
EMO = {
 "normal":  (0, 0, 0, -16, "room"),
 "whisper": (-8, -3, -30, -24, "whisper"),
 "shout":   (12, 7, 25, -13, "room"),
 "excited": (7, 3, 10, -15, "room"),
 "sad":     (-13, -4, -15, -20, "room"),
 "slow":    (-10, -2, 0, -17, "room"),
 "fast":    (10, 1, 0, -16, "room"),
 "phone":   (0, 0, 0, -17, "phone"),
 "memory":  (-6, -2, -5, -18, "memory"),
}
CHAIN = {
 "room":    "highpass=f=75,lowpass=f=11500,equalizer=f=220:t=q:w=1:g=1.5,equalizer=f=3200:t=q:w=1.2:g=2,acompressor=threshold=-20dB:ratio=3:attack=4:release=80:makeup=2,aecho=0.85:0.4:14|27:0.07|0.04",
 "whisper": "highpass=f=180,lowpass=f=9000,equalizer=f=5000:t=q:w=1:g=3,acompressor=threshold=-24dB:ratio=2.5:attack=4:release=80,aecho=0.85:0.3:12:0.05",
 "phone":   "highpass=f=320,lowpass=f=3300,equalizer=f=1500:t=q:w=1:g=4,acompressor=threshold=-22dB:ratio=5:attack=2:release=50,acrusher=bits=12:mix=0.15",
 "memory":  "highpass=f=90,lowpass=f=8000,acompressor=threshold=-20dB:ratio=3:attack=5:release=90,aecho=0.8:0.7:60|110:0.25|0.15",
}

def norm(s):
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if unicodedata.category(c) != "Mn").upper().strip()

CAM = [("phone", ("on speaker", "video call", "on the phone", "answering")),
       ("whisper", ("whisper",)),
       ("shout", ("shouting", "screaming", "slams", "pushing")),
       ("sad", ("crying", "tears", "red eyes", "breaking down", "devastated")),
       ("fast", ("panicking", "out of breath", "panting", "panicked", "running")),
       ("slow", ("calm", "slowly", "serious", "very calm"))]

def emotion(direction, text, header, cam="", who=""):
    if who.startswith("VOIX"): return "excited" if "!" in text else "normal"
    d = direction.lower() + " " + header.lower()
    if not direction and who and ("{" + who + "}") in cam:
        c = cam.lower()
        for emo, keys in CAM:
            if any(k in c for k in keys):
                if emo == "phone" and who == "YANIS" and "{YANIS}'s phone" in cam: continue
                return emo
    if any(k in d for k in ("téléphone", "appel vidéo", "dans le micro")): return "phone"
    if "voix off, grave" in d: return "memory"
    if any(k in d for k in ("chuchot", "entre ses dents", "voix basse")): return "whisper"
    if any(k in d for k in ("larmes", "se brise", "ému", "doucement")): return "sad"
    if any(k in d for k in ("glacial", "lent", "long silence", "un temps", "soudain calme")): return "slow"
    if any(k in d for k in ("rapide", "essoufflé", "panique")): return "fast"
    caps = re.findall(r"\b[A-ZÉÈÀÇ]{3,}\b", text)
    if "!" in text and (caps or "?!" in text or "!!" in text): return "shout"
    if "!" in text: return "excited"
    return "normal"

jobs = []
for f in sorted(glob.glob(os.path.join(SRC, "ep*.md"))):
    ep = None; sec = "main"; plan = "x"; n = 0; header = ""; cam = ""
    for line in open(f, encoding="utf-8"):
        m = re.match(r"## Épisode (\d+)", line)
        if m: ep = int(m.group(1)); sec = "main"; n = 0; continue
        if ep is None: continue
        if line.startswith("## "): ep = None; continue
        if "**🅰️" in line: sec = "A"; header = line
        elif "**🅱️" in line: sec = "B"; header = line
        elif line.startswith("### Suite"): sec = "main"
        m = re.match(r"\*\*(P\d+|R)\b", line)
        if m: plan = m.group(1); sec = "main"; header = line
        if line.startswith("🎥"): cam = line
        m = re.match(r"(?:🗣️|🎙️) \*\*(.+?)\*\*(.*)", line.strip())
        if not m: continue
        who = norm(m.group(1)); rest = m.group(2)
        parts = re.findall(r"«\s*(.+?)\s*»", rest)
        if not parts: continue
        direction = " ".join(re.findall(r"\*\((.+?)\)\*", rest))
        text = " ".join(parts)
        n += 1
        tag = sec if sec in ("A", "B") else plan
        name = f"{n:02d}_{'ouverture-'+tag if tag in ('A','B') else tag}_{who.replace(' ','-').replace(chr(39),'')}.mp3"
        if ONLY is None or ep in ONLY:
            jobs.append((ep, name, who, text, emotion(direction, text, header if who == "MALIK" else "", cam, who.replace("È","E"))))

def sentences(text):
    text = text.replace("...", "…")
    out = [s.strip() for s in re.split(r"(?<=[.!?…])\s+", text) if re.search(r"\w", s)]
    return out

def gap_after(s):
    if s.endswith("…"): return random.randint(380, 520)
    if s.endswith("?"): return random.randint(200, 300)
    if s.endswith("!"): return random.randint(150, 240)
    return random.randint(220, 340)

async def sh(*args):
    p = await asyncio.create_subprocess_exec(*args, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.PIPE)
    _, err = await p.communicate()
    if p.returncode: raise RuntimeError(err.decode()[-400:])

async def tts(text, voice, rate, pitch, vol, path):
    for k in range(5):
        try:
            await edge_tts.Communicate(text, voice, rate=f"{rate:+d}%", pitch=f"{pitch:+d}Hz", volume=f"{vol:+d}%").save(path)
            if os.path.getsize(path) > 0: return
        except Exception:
            pass
        await asyncio.sleep(2 * (k + 1))
    raise RuntimeError("tts failed: " + text)

TRIM = "silenceremove=start_periods=1:start_threshold=-48dB:start_silence=0.03,areverse,silenceremove=start_periods=1:start_threshold=-48dB:start_silence=0.06,areverse"

async def line(ep, name, who, text, emo, sem):
    voice, r0, p0 = V.get(who, V["TOUS"])
    er, ep_, evol, lufs, chain = EMO[emo]
    d = os.path.join(OUT, f"ep{ep:02d}"); os.makedirs(d, exist_ok=True)
    work = os.path.join(TMP, f"{ep}_{name}"); os.makedirs(work, exist_ok=True)
    sents = sentences(text)
    out = os.path.join(d, name)
    if os.path.exists(out) and os.path.getsize(out) > 2000: return
    if not sents:  # réplique muette (« … ») : 1 s de silence d'ambiance
        await sh("ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "anoisesrc=color=brown:amplitude=0.0035:r=44100", "-t", "1", "-ac", "1", "-b:a", "160k", out)
        return
    async with sem:
        wavs = []
        for i, s in enumerate(sents):
            mp = os.path.join(work, f"s{i}.mp3"); wv = os.path.join(work, f"s{i}.wav")
            rate = r0 + er + random.randint(-4, 4)
            # dernière phrase d'une question : légère montée ; phrases courtes un peu plus vives
            pitch = p0 + ep_ + random.randint(-3, 3) + (2 if s.endswith("?") else 0)
            if len(s) < 25: rate += 3
            await tts(s, voice, rate, pitch, evol, mp)
            await sh("ffmpeg", "-y", "-loglevel", "error", "-i", mp, "-af", TRIM, "-ar", "44100", "-ac", "1", wv)
            wavs.append(wv)
            if i < len(sents) - 1:
                g = os.path.join(work, f"g{i}.wav")
                await sh("ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", f"{gap_after(s)/1000:.3f}", g)
                wavs.append(g)
        lst = os.path.join(work, "list.txt")
        open(lst, "w").write("".join(f"file '{w}'\n" for w in wavs))
        joined = os.path.join(work, "joined.wav")
        await sh("ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", joined)
        # pré-silence 120 ms + post 250 ms, chaîne micro, bruit de pièce très léger, normalisation
        out = os.path.join(d, name)
        fc = (f"[0]adelay=120,apad=pad_dur=0.25,{CHAIN[chain]},loudnorm=I={lufs}:TP=-1.5:LRA=9,aresample=44100[v];"
              f"anoisesrc=color=brown:amplitude=0.0035:r=44100,highpass=f=60,lowpass=f=3000[n];"
              f"[v][n]amix=inputs=2:duration=first:weights=1 1:normalize=0[o]")
        await sh("ffmpeg", "-y", "-loglevel", "error", "-i", joined, "-filter_complex", fc, "-map", "[o]", "-ar", "44100", "-ac", "1", "-b:a", "160k", out)
        shutil.rmtree(work, ignore_errors=True)

async def run():
    sem = asyncio.Semaphore(6)
    res = await asyncio.gather(*(line(*j, sem) for j in jobs), return_exceptions=True)
    print('erreurs:', [str(r) for r in res if isinstance(r, Exception)])
    print("répliques:", len(jobs))
    from collections import Counter
    print(Counter(j[4] for j in jobs))

asyncio.run(run())
