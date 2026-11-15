"""Voix off 100 % locale : Piper (synthèse) + faster-whisper (minutage mot par mot et contrôle).
Usage : voix_locale.py <voix-off.json> <dossier_sortie>"""
import json, sys, os, wave, re, difflib, subprocess
import numpy as np
from piper import PiperVoice, SynthesisConfig
from faster_whisper import WhisperModel
V = os.path.join(os.path.dirname(__file__), '../build/outils/voices')
VOIX = {  # modèle, locuteur, vitesse (plus petit = plus rapide), variation
  'narrateur': ('fr_FR-tom-medium', None, 0.92, 0.6),
  'lana': ('fr_FR-siwis-medium', None, 0.88, 0.75),
  'ines': ('fr_FR-upmc-medium', 0, 0.95, 0.6),
}
segs, out = json.load(open(sys.argv[1])), sys.argv[2]
os.makedirs(out, exist_ok=True)
models = {}
wm = WhisperModel('small', device='cpu', compute_type='int8')
norm = lambda s: re.sub(r"[^a-z0-9àâäéèêëîïôöùûüç']", '', s.lower())
only = sys.argv[3].split(',') if len(sys.argv) > 3 else None
for s in segs:
    if only and s['id'] not in only: continue
    m, spk, ls, ns = VOIX[s['voix']]
    if m not in models: models[m] = PiperVoice.load(f'{V}/{m}.onnx')
    raw = f"{out}/{s['id']}_raw.wav"
    with wave.open(raw, 'wb') as w:
        models[m].synthesize_wav(s.get('dire', s['text']), w, SynthesisConfig(speaker_id=spk, length_scale=ls, noise_scale=ns))
    # nettoyage : coupe les silences de début/fin, léger traitement voix
    af = 'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,highpass=f=70,acompressor=threshold=-18dB:ratio=3:attack=5:release=80,volume=1.5'
    if s['voix'] == 'lana': af += ',asetrate=22050*1.04,aresample=22050,atempo=0.97'
    wav = f"{out}/{s['id']}.wav"
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', raw, '-af', af, '-ar', '44100', wav], check=True)
    os.remove(raw)
    dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', wav]))
    pcm = np.frombuffer(subprocess.check_output(['ffmpeg', '-loglevel', 'error', '-i', wav, '-f', 's16le', '-ac', '1', '-ar', '16000', '-']), np.int16).astype(np.float32) / 32768
    res, _ = wm.transcribe(pcm, language='fr', word_timestamps=True, beam_size=5)
    ww = [w for seg in res for w in seg.words]
    heard = ' '.join(w.word.strip() for w in ww)
    # aligne les mots du script sur les mots entendus
    sw = s['text'].split()
    a, b = [norm(x) for x in s.get('dire', s['text']).split()], [norm(w.word) for w in ww]
    words = [None] * len(sw)
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b).get_opcodes():
        if tag in ('equal', 'replace'):
            for k in range(i2 - i1):
                j = j1 + min(k * (j2 - j1) // max(1, i2 - i1), j2 - j1 - 1) if j2 > j1 else None
                if j is not None: words[i1 + k] = (ww[j].start, ww[j].end)
    # interpole les mots non trouvés
    for i in range(len(sw)):
        if words[i] is None:
            prev = next((words[k][1] for k in range(i - 1, -1, -1) if words[k]), 0.0)
            nxt = next((words[k][0] for k in range(i + 1, len(sw)) if words[k]), dur)
            words[i] = (prev, prev + (nxt - prev) / 2)
    ratio = difflib.SequenceMatcher(None, ' '.join(a), ' '.join(b)).ratio()
    json.dump({'words': [{'w': w, 's': t[0], 'e': t[1]} for w, t in zip(sw, words)], 'dur': dur, 'voix': s['voix'], 'entendu': heard, 'fidelite': round(ratio, 3)},
              open(f"{out}/{s['id']}.json", 'w'), ensure_ascii=False, indent=1)
    print(f"{s['id']:3} {dur:5.2f}s  fidélité {ratio:.2f}  | {heard}")
