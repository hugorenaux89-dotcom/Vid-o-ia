"""Voix française NATIVE et réaliste, gratuite : Kyutai TTS 1.6B en/fr (labo parisien, licence CC-BY 4.0).
Voix de référence : locuteurs français natifs du jeu CML-TTS (kyutai/tts-voices, CC-BY 4.0).

Usage (environnement Python avec `moshi`) :
    python voice_kyutai.py <voix> <dossier_sortie> [lignes...]
    python voice_kyutai.py --test <voix1,voix2,...> "<texte>"
"""
import os, sys, time
import numpy as np
import soundfile as sf
import torch
from moshi.models.loaders import CheckpointInfo
from moshi.models.tts import DEFAULT_DSM_TTS_REPO, TTSModel

HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "voice_tv.py")).read()
LINES = eval(src[src.index("LINES = {") + 8: src.index("}\nSTYLE") + 1])
CFG = float(os.environ.get("KY_CFG", "2.0"))
TEMP = float(os.environ.get("KY_TEMP", "0.6"))

torch.set_num_threads(os.cpu_count() or 4)
_model = None


def model():
    global _model
    if _model is None:
        info = CheckpointInfo.from_hf_repo(DEFAULT_DSM_TTS_REPO)
        _model = TTSModel.from_checkpoint_info(info, n_q=32, temp=TEMP, device=torch.device("cpu"), dtype=torch.float32)
    return _model


def say(text, voice):
    m = model()
    entries = m.prepare_script([text], padding_between=1)
    vp = m.get_voice_path(voice)
    attrs = m.make_condition_attributes([vp], cfg_coef=CFG)
    pcms = []

    def on_frame(frame):
        if (frame != -1).all():
            pcm = m.mimi.decode(frame[:, 1:, :]).cpu().numpy()
            pcms.append(np.clip(pcm[0, 0], -1, 1))

    with m.mimi.streaming(1):
        m.generate([entries], [attrs], on_frame=on_frame)
    return np.concatenate(pcms, axis=-1), m.mimi.sample_rate


def main():
    if sys.argv[1] == "--test":
        voices = sys.argv[2].split(","); text = sys.argv[3]
        out = os.environ.get("KY_OUT", ".")
        for v in voices:
            t0 = time.time(); a, sr = say(text, v)
            name = os.path.basename(v).split("_enhanced")[0]
            sf.write(os.path.join(out, f"ky_{name}.wav"), a, sr)
            print(f"{name} {len(a) / sr:.2f}s audio en {time.time() - t0:.0f}s", flush=True)
        return
    voice, outdir = sys.argv[1], sys.argv[2]
    only = set(sys.argv[3:])
    takes = int(os.environ.get("TAKES", "2"))
    os.makedirs(outdir, exist_ok=True)
    for name, (text, style) in LINES.items():
        if only and name not in only:
            continue
        for k in range(takes):
            path = os.path.join(outdir, f"{name}_{k}.wav")
            if os.path.exists(path) and not only:
                continue
            torch.manual_seed(97 * k + 13)
            t0 = time.time(); a, sr = say(text, voice)
            sf.write(path, a, sr)
            print(f"{name}_{k} {len(a) / sr:.2f}s ({time.time() - t0:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
