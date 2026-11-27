"""Voix « commentateur télé » réaliste et gratuite : Chatterbox Multilingual (licence MIT), en local.

Timbre de référence : notre propre voix libre (Piper « tom » sculptée, assets/voice_ref_tom.wav),
donc aucune voix réelle n'est imitée. Chatterbox apporte une intonation naturelle et expressive.

À lancer avec l'environnement Python qui contient chatterbox-tts :
    python voice_tv.py           -> assets/voice_tv/raw/<ligne>_<prise>.wav
Puis : python3 voice_tv_select.py (choix de la meilleure prise + mastering)
"""
import os, sys, time
import soundfile as sf
import torch
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.path.join(ROOT, "assets", "voice_ref_tom.wav")
OUT = os.path.join(ROOT, "assets", "voice_tv", "raw")

# texte, style. « hype » = animateur très enthousiaste ; « host » = présentation posée mais vive ;
# « whisper » = généré calmement puis transformé en chuchotement.
LINES = {
    "01_accroche": ("Seuls les vrais fans auront dix sur dix !", "hype"),
    "02_Q1_question": ("Quel est ce pays ?", "host"),
    "03_Q1_reponse": ("Le Japon ! Trop facile !", "hype"),
    "04_Q2_question": ("Et celui-là ?", "host"),
    "05_Q2_reponse": ("Le Brésil !", "hype"),
    "06_Q3_question": ("Suivant !", "host"),
    "07_Q3_reponse": ("Le Canada ! Bien joué !", "hype"),
    "08_niveau_moyen": ("Niveau moyen !", "hype"),
    "09_Q4_reponse": ("La Turquie !", "hype"),
    "10_Q5_question": ("Et celui-ci ?", "host"),
    "11_Q5_reponse": ("La Grèce !", "hype"),
    "12_Q6_question": ("Et lui ?", "host"),
    "13_Q6_reponse": ("La Corée du Sud ! Bravo !", "hype"),
    "14_niveau_difficile": ("Ça se complique !", "hype"),
    "15_Q7_reponse": ("Le Népal ! Aïe aïe aïe !", "hype"),
    "16_Q8_question": ("Attention !", "host"),
    "17_Q8_reponse": ("Le Kazakhstan !", "hype"),
    "18_niveau_extreme": ("Niveau extrême !", "hype"),
    "19_suspense": ("La réponse...", "whisper"),
    "20_Q9_reponse": ("Le Bhoutan !", "hype"),
    "21_Q10_question": ("Le dernier !", "host"),
    "22_Q10_reponse": ("Le Tchad ! Pas la Roumanie !", "hype"),
    "23_conclusion": ("Alors, t'as combien ? Dis-le en commentaire !", "hype"),
}
STYLE = {"hype": dict(exaggeration=0.85, cfg_weight=0.35, temperature=0.8),
         "host": dict(exaggeration=0.6, cfg_weight=0.4, temperature=0.75),
         "whisper": dict(exaggeration=0.35, cfg_weight=0.5, temperature=0.7)}
TAKES = int(os.environ.get("TAKES", "2"))


def main():
    torch.set_num_threads(os.cpu_count() or 4)
    os.makedirs(OUT, exist_ok=True)
    m = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
    only = set(sys.argv[1:])
    for name, (text, style) in LINES.items():
        if only and name not in only:
            continue
        for k in range(TAKES):
            path = os.path.join(OUT, f"{name}_{k}.wav")
            if os.path.exists(path) and not only:
                continue
            torch.manual_seed(1000 * k + hash(name) % 997)
            t0 = time.time()
            wav = m.generate(text, language_id="fr", audio_prompt_path=REF, **STYLE[style])
            sf.write(path, wav.squeeze().numpy(), m.sr)
            print(f"{name}_{k} {wav.shape[-1] / m.sr:.2f}s ({time.time() - t0:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
