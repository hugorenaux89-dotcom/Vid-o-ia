"""Transcription PHONÉTIQUE (API) de chaque réplique : vérifie liaisons et prononciation.
À lancer avec un Python qui contient transformers + torch :  python phon_check.py <dossier_wav>"""
import glob, itertools, json, os, sys
import librosa, torch
from huggingface_hub import hf_hub_download
from transformers import Wav2Vec2FeatureExtractor, Wav2Vec2ForCTC

MID = "facebook/wav2vec2-xlsr-53-espeak-cv-ft"
fe = Wav2Vec2FeatureExtractor.from_pretrained(MID)
m = Wav2Vec2ForCTC.from_pretrained(MID).eval()
voc = {v: k for k, v in json.load(open(hf_hub_download(MID, "vocab.json"))).items()}
for f in sorted(glob.glob(os.path.join(sys.argv[1], "[0-9]*.wav"))):
    y, _ = librosa.load(f, sr=16000)
    with torch.no_grad():
        ids = m(fe(y, sampling_rate=16000, return_tensors="pt").input_values).logits.argmax(-1)[0].tolist()
    ph = [voc[k] for k, _ in itertools.groupby(ids) if voc[k] not in ("<pad>", "<s>", "</s>")]
    print(f"{os.path.basename(f)[:-4]:<22} /{' '.join(ph)}/")
