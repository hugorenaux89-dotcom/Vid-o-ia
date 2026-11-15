"""Voix off locale expressive : Chatterbox multilingue (MIT), voix de référence LibriVox (domaine public).
Usage : <venv>/python voix_chatterbox.py <voix-off.json> <dossier> [ids,séparés,par,virgules]"""
import json, sys, os, time, torch, torchaudio
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
REF = os.path.join(os.path.dirname(__file__), '../build/outils/refs')
# (référence, exagération, cfg) : exagération haute = plus expressif ; cfg bas = débit plus vif
VOIX = {
    'narrateur': ('narrateur.wav', 0.6, 0.45),
    'lana': ('lana.wav', 0.75, 0.4),
    'ines': ('ines.wav', 0.7, 0.4),
}
segs, out = json.load(open(sys.argv[1])), sys.argv[2]
only = sys.argv[3].split(',') if len(sys.argv) > 3 else None
os.makedirs(out, exist_ok=True)
SEEDS = [int(x) for x in os.environ.get('SEEDS', '7').split(',')]
tts = ChatterboxMultilingualTTS.from_pretrained(device='cpu')
for s in segs:
    if only and s['id'] not in only: continue
    ref, ex, cfg = VOIX[s['voix']]
    ex = s.get('ex', ex); cfg = s.get('cfg', cfg)
    for seed in SEEDS:
        torch.manual_seed(seed)
        t0 = time.time()
        wav = tts.generate(s.get('dire', s['text']), language_id='fr', audio_prompt_path=f'{REF}/{ref}', exaggeration=ex, cfg_weight=cfg)
        suf = '' if len(SEEDS) == 1 else f'_s{seed}'
        torchaudio.save(f"{out}/{s['id']}_cb{suf}.wav", wav, tts.sr)
        print(s['id'], seed, f"{wav.shape[-1] / tts.sr:.2f}s audio en {time.time() - t0:.0f}s", flush=True)
