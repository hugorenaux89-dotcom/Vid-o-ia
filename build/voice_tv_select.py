"""Choisit la meilleure prise de chaque réplique (transcription la plus fidèle, puis la plus courte),
puis mastering léger « voix télé » : on garde le naturel (pas de déformation de hauteur).
Sortie : assets/voice_tv/<ligne>.wav
"""
import difflib, glob, json, os, re, subprocess, sys, unicodedata
import numpy as np, soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "assets", "voice_tv", "raw")
OUT = os.path.join(ROOT, "assets", "voice_tv")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# lecture des répliques sans importer chatterbox
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "voice_tv.py")).read()
LINES = eval(src[src.index("LINES = {") + 8: src.index("}\nSTYLE") + 1])

TRIM = ("silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.02,areverse,"
        "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.06,areverse")
# voix de présentateur : coupe-bas, un peu de corps, présence, compression douce, pas de déformation
MASTER = ("highpass=f=70,equalizer=f=120:t=q:w=1:g=2,equalizer=f=300:t=q:w=1.2:g=-1.5,"
          "equalizer=f=3000:t=q:w=1.5:g=3,equalizer=f=10000:t=q:w=1:g=1.5,"
          "acompressor=threshold=-18dB:ratio=3:attack=5:release=80:makeup=3dB,deesser=i=0.3")
TEMPO = float(os.environ.get("TV_TEMPO", "1.08"))  # débit d'animateur, sans changer la hauteur


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.replace("10", "dix")
    return re.sub(r"[^a-z ]", " ", s).split()


def stt(path):
    r = subprocess.run(["curl", "-s", "-m", "60", "-F", "model_id=scribe_v1", "-F", "language_code=fr",
                        "-F", "tag_audio_events=false", "-F", f"file=@{path}",
                        "https://api.elevenlabs.io/v1/speech-to-text"], capture_output=True, text=True).stdout
    try:
        return json.loads(r).get("text") or ""
    except Exception:
        return ""


def ffmpeg(i, o, af):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", i, "-af", af, "-ar", "44100", "-ac", "1", o], check=True)


def whisperize(path_in, path_out):
    import pyworld as pw
    x, fs = sf.read(path_in)
    x = x.astype(np.float64)
    f0, t = pw.harvest(x, fs, f0_floor=60, f0_ceil=400, frame_period=5.0)
    sp = pw.cheaptrick(x, f0, t, fs)
    ap = np.ones_like(pw.d4c(x, f0, t, fs))
    y = pw.synthesize(np.zeros_like(f0), sp, ap, fs, frame_period=5.0)
    sf.write(path_out, y / (np.abs(y).max() + 1e-9) * 0.9, fs)


def main():
    report = []
    for name, (text, style) in LINES.items():
        takes = sorted(glob.glob(os.path.join(RAW, f"{name}_*.wav")))
        best = None
        for p in takes:
            tmp = p.replace(".wav", "_t.wav")
            ffmpeg(p, tmp, TRIM)
            heard = stt(tmp)
            score = difflib.SequenceMatcher(None, norm(text), norm(heard)).ratio()
            d = len(sf.read(tmp)[0]) / 44100
            key = (round(score, 2), -d)
            if best is None or key > best[0]:
                best = (key, tmp, heard, d)
        if best is None:
            print("MANQUE", name); continue
        (score, _), tmp, heard, d = best
        out = os.path.join(OUT, name + ".wav")
        if style == "whisper":
            w = tmp.replace("_t.wav", "_w.wav")
            whisperize(tmp, w)
            ffmpeg(w, out, f"atempo={TEMPO},{MASTER},highpass=f=200,aecho=0.8:0.6:60:0.25,loudnorm=I=-17:TP=-2")
        else:
            ffmpeg(tmp, out, f"atempo={TEMPO},{MASTER},loudnorm=I=-14:TP=-1.5")
        d2 = len(sf.read(out)[0]) / 44100
        flag = "" if score >= 0.85 else "   <-- À REVOIR"
        print(f"{name:<22} {d2:4.2f}s  fidélité {score:.2f}  « {heard} »{flag}")
        report.append(dict(name=name, score=score, heard=heard, dur=d2))
    json.dump(report, open(os.path.join(OUT, "selection.json"), "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
