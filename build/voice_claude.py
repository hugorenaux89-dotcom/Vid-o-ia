"""Voix « maison » 100 % gratuite et locale : Piper (modèle neuronal libre) + traitement sur mesure.

Objectif (description §10.1 du prompt) : voix masculine française, jeune, très énergique,
timbre clair légèrement grave et chaleureux, débit rapide, suspense chuchoté avant l'extrême.

Usage : python3 voice_claude.py <modele.onnx> [speaker_id]
Sortie : assets/voice_claude/<réplique>.wav (rognées, normalisées)
"""
import os, subprocess, sys, wave
from piper import PiperVoice
from piper.config import SynthesisConfig

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "voice_claude")
RAW = os.path.join(OUT, "raw")

# style : "punch" = énergique (aigu +, rapide), "normal", "whisper" = chuchoté/suspense
LINES = {
    "01_accroche": ("Seuls les vrais fans auront dix sur dix !", "punch"),
    "02_Q1_question": ("Quel est ce pays ?", "normal"),
    "03_Q1_reponse": ("Japon ! Trop facile !", "punch"),
    "04_Q2_question": ("Et celui-là ?", "normal"),
    "05_Q2_reponse": ("Le Brésil !", "punch"),
    "06_Q3_question": ("Suivant !", "normal"),
    "07_Q3_reponse": ("Canada ! Bien joué !", "punch"),
    "08_niveau_moyen": ("Niveau moyen !", "punch"),
    "09_Q4_reponse": ("Turquie !", "punch"),
    "10_Q5_question": ("Celui-ci ?", "normal"),
    "11_Q5_reponse": ("La Grèce !", "punch"),
    "12_Q6_question": ("Et lui ?", "normal"),
    "13_Q6_reponse": ("Corée du Sud ! Bravo !", "punch"),
    "14_niveau_difficile": ("Ça se complique !", "punch"),
    "15_Q7_reponse": ("Népal ! Aïe aïe aïe !", "punch"),
    "16_Q8_question": ("Attention !", "normal"),
    "17_Q8_reponse": ("Kazak-stane !", "normal"),
    "18_niveau_extreme": ("Niveau extrême !", "punch"),
    "19_suspense": ("La réponse...", "whisper"),
    "20_Q9_reponse": ("Le Bhoutane !", "punch"),
    "21_Q10_question": ("Le dernier !", "normal"),
    "22_Q10_reponse": ("Le Tchad ! Pas la Roumanie !", "punch"),
    "23_conclusion": ("Alors, t'as combien ? Dis-le en commentaire !", "punch"),
}

# réglages de synthèse par style : length_scale (<1 = plus rapide), variabilité de l'intonation
SYN = {"punch": (0.78, 0.80, 1.0), "normal": (0.82, 0.70, 0.9), "whisper": (1.05, 0.5, 0.6)}

# traitement : timbre (EQ chaleur + présence), compression « radio », hauteur par style
TRIM = ("silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.02,areverse,"
        "silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.05,areverse")
COMMON = ("highpass=f=75,equalizer=f=140:t=q:w=1:g=2.5,equalizer=f=350:t=q:w=1.2:g=-2,"
          "equalizer=f=3200:t=q:w=1.4:g=4,equalizer=f=9000:t=q:w=1:g=2,"
          "acompressor=threshold=-20dB:ratio=4:attack=4:release=60:makeup=4dB,"
          "deesser=i=0.4")
PITCH = {"punch": 1.0, "normal": 1.0, "whisper": 1.0}

# --- Sculpture de la voix avec WORLD (analyse / resynthèse) -------------------------------
# Hauteur cible (médiane) : homme jeune, « légèrement grave » ; un peu plus haut quand il s'enflamme.
F0_TARGET = {"normal": 118.0, "punch": 128.0}
# Expansion de la mélodie autour de la médiane : 1 = inchangée, >1 = plus expressive.
F0_EXPAND = {"normal": 1.25, "punch": 1.5}
# Déformation de l'enveloppe spectrale : <1 abaisse les formants = timbre plus chaud et plus grave.
FORMANT_WARP = 0.96


def sculpt(raw, style):
    import numpy as np, pyworld as pw, soundfile as sf
    x, fs = sf.read(raw)
    x = x.astype(np.float64)
    f0, t = pw.harvest(x, fs, f0_floor=60, f0_ceil=400, frame_period=5.0)
    sp = pw.cheaptrick(x, f0, t, fs)
    ap = pw.d4c(x, f0, t, fs)
    # timbre : formants abaissés
    n = sp.shape[1]
    src = np.clip(np.arange(n) / FORMANT_WARP, 0, n - 1)
    sp = np.array([np.interp(src, np.arange(n), row) for row in sp])
    if style == "whisper":
        # vrai chuchotement : aucune vibration des cordes vocales, excitation 100 % souffle
        f0 = np.zeros_like(f0)
        ap = np.ones_like(ap)
    else:
        from scipy.signal import medfilt
        v = f0 > 0
        if v.sum() > 5:
            # lissage : on exagère la mélodie, pas les micro-tremblements
            f0[v] = np.exp(medfilt(np.log(f0[v]), 7))
            lf = np.log(f0[v])
            med = np.median(lf)
            lf = np.log(F0_TARGET[style]) + F0_EXPAND[style] * (lf - med)
            if style == "punch" and v.sum() > 120:
                # élan d'animateur : la phrase monte légèrement vers son temps fort final
                ramp = np.linspace(-0.04, 0.10, v.sum())
                lf = lf + ramp
            f0[v] = np.exp(np.clip(lf, np.log(70), np.log(330)))
    y = pw.synthesize(f0, sp, ap, fs, frame_period=5.0)
    y = y / (np.abs(y).max() + 1e-9) * 0.9
    out = raw.replace(".wav", "_world.wav")
    sf.write(out, y, fs)
    return out


def fx_chain(style, sr):
    p = PITCH[style]
    pitch = f"asetrate={int(sr * p)},aresample=44100,atempo={1 / p:.4f}"
    if style == "whisper":
        # voix soufflée : on retire le grave, on ajoute un léger écho de « suspense »
        return f"{TRIM},{pitch},highpass=f=180,{COMMON},aecho=0.8:0.6:60:0.25"
    return f"{TRIM},{pitch},{COMMON}"


def main():
    model = sys.argv[1]
    sid = int(sys.argv[2]) if len(sys.argv) > 2 else None
    os.makedirs(RAW, exist_ok=True)
    voice = PiperVoice.load(model)
    sr = voice.config.sample_rate
    for name, (text, style) in LINES.items():
        ls, ns, nw = SYN[style]
        if len(text.split()) <= 2 and style != "whisper":
            ls = 0.95  # un mot isolé trop rapide devient incompréhensible
        raw = os.path.join(RAW, name + ".wav")
        with wave.open(raw, "wb") as w:
            voice.synthesize_wav(text, w, syn_config=SynthesisConfig(speaker_id=sid, length_scale=ls,
                                                                     noise_scale=ns, noise_w_scale=nw))
        raw = sculpt(raw, style)
        out = os.path.join(OUT, name + ".wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af",
                        fx_chain(style, sr) + ",loudnorm=I=-14:TP=-1.5" + (",volume=-4dB" if style == "whisper" else ""),
                        "-ar", "44100", "-ac", "1", out], check=True)
        d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out],
                           capture_output=True, text=True).stdout.strip()
        print(f"{name:<22} {float(d):.2f}s  [{style}] {text}")


if __name__ == "__main__":
    main()
