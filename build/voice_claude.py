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
    "05_Q2_reponse": ("Brésil !", "punch"),
    "06_Q3_question": ("Suivant !", "normal"),
    "07_Q3_reponse": ("Canada ! Bien joué !", "punch"),
    "08_niveau_moyen": ("Niveau moyen !", "punch"),
    "09_Q4_reponse": ("Turquie !", "punch"),
    "10_Q5_question": ("Celui-ci ?", "normal"),
    "11_Q5_reponse": ("Grèce !", "punch"),
    "12_Q6_question": ("Et lui ?", "normal"),
    "13_Q6_reponse": ("Corée du Sud ! Bravo !", "punch"),
    "14_niveau_difficile": ("Ça se complique !", "punch"),
    "15_Q7_reponse": ("Népal ! Aïe !", "punch"),
    "16_Q8_question": ("Attention !", "normal"),
    "17_Q8_reponse": ("Kazak-stane !", "normal"),
    "18_niveau_extreme": ("Niveau extrême !", "punch"),
    "19_suspense": ("La réponse...", "whisper"),
    "20_Q9_reponse": ("Le Bhoutan !", "punch"),
    "21_Q10_question": ("Le dernier !", "normal"),
    "22_Q10_reponse": ("Tchad ! Pas la Roumanie !", "punch"),
    "23_conclusion": ("Alors, t'as combien ? Dis-le en commentaire !", "punch"),
}

# réglages de synthèse par style : length_scale (<1 = plus rapide), variabilité de l'intonation
SYN = {"punch": (0.78, 0.80, 1.0), "normal": (0.82, 0.70, 0.9), "whisper": (1.05, 0.5, 0.6)}

# traitement : timbre (EQ chaleur + présence), compression « radio », hauteur par style
TRIM = ("silenceremove=start_periods=1:start_threshold=-40dB:start_silence=0.02,areverse,"
        "silenceremove=start_periods=1:start_threshold=-42dB:start_silence=0.05,areverse")
COMMON = ("highpass=f=75,equalizer=f=140:t=q:w=1:g=2.5,equalizer=f=350:t=q:w=1.2:g=-2,"
          "equalizer=f=3200:t=q:w=1.4:g=4,equalizer=f=9000:t=q:w=1:g=2,"
          "acompressor=threshold=-20dB:ratio=4:attack=4:release=60:makeup=4dB,"
          "deesser=i=0.4")
PITCH = {"punch": 1.035, "normal": 1.0, "whisper": 0.97}


def fx_chain(style, sr):
    p = PITCH[style]
    pitch = f"asetrate={int(sr * p)},aresample=44100,atempo={1 / p:.4f}"
    if style == "whisper":
        # voix soufflée : on retire le grave, on ajoute un léger écho de « suspense »
        return f"{TRIM},{pitch},highpass=f=300,lowpass=f=7000,{COMMON},aecho=0.8:0.6:60:0.25,volume=-3dB"
    return f"{TRIM},{pitch},{COMMON}"


def main():
    model = sys.argv[1]
    sid = int(sys.argv[2]) if len(sys.argv) > 2 else None
    os.makedirs(RAW, exist_ok=True)
    voice = PiperVoice.load(model)
    sr = voice.config.sample_rate
    for name, (text, style) in LINES.items():
        ls, ns, nw = SYN[style]
        raw = os.path.join(RAW, name + ".wav")
        with wave.open(raw, "wb") as w:
            voice.synthesize_wav(text, w, syn_config=SynthesisConfig(speaker_id=sid, length_scale=ls,
                                                                     noise_scale=ns, noise_w_scale=nw))
        out = os.path.join(OUT, name + ".wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af",
                        fx_chain(style, sr) + ",loudnorm=I=-14:TP=-1.5" + (",volume=-4dB" if style == "whisper" else ""),
                        "-ar", "44100", "-ac", "1", out], check=True)
        d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out],
                           capture_output=True, text=True).stdout.strip()
        print(f"{name:<22} {float(d):.2f}s  [{style}] {text}")


if __name__ == "__main__":
    main()
