"""Post-traitement des voix (silences, tempo, égalisation radio) + minutage mot par mot (Whisper).
Usage : voix_post.py <voix-off.json> <dossier_brut> <dossier_sortie> [ids]"""
import json, sys, os, re, difflib, subprocess
import numpy as np
from faster_whisper import WhisperModel
TEMPO = {'narrateur': 1.2, 'lana': 1.1, 'ines': 1.12}
FX = {  # chaîne « voix radio » : coupe-bas, présence, compression, brillance
  'narrateur': 'highpass=f=75,equalizer=f=180:t=q:w=1:g=2,equalizer=f=3200:t=q:w=1.2:g=3,acompressor=threshold=-20dB:ratio=3.5:attack=5:release=90:makeup=2',
  'lana': 'highpass=f=110,equalizer=f=2800:t=q:w=1.2:g=3,acompressor=threshold=-20dB:ratio=3:attack=4:release=80:makeup=2',
  'ines': 'highpass=f=120,equalizer=f=3500:t=q:w=1.2:g=3,acompressor=threshold=-20dB:ratio=3:attack=4:release=80:makeup=2',
}
segs, src, out = json.load(open(sys.argv[1])), sys.argv[2], sys.argv[3]
only = sys.argv[4].split(',') if len(sys.argv) > 4 else None
os.makedirs(out, exist_ok=True)
wm = WhisperModel('small', device='cpu', compute_type='int8')
norm = lambda s: re.sub(r"[^a-z0-9àâäéèêëîïôöùûüç']", '', s.lower())
for s in segs:
    if only and s['id'] not in only: continue
    v = s['voix']; wav = f"{out}/{s['id']}.wav"
    trim = 'adelay=200,silenceremove=start_periods=1:start_threshold=-55dB:start_silence=0.08,areverse,silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.08,areverse'
    # raccourcit les blancs internes trop longs (> 0,35 s)
    gaps = 'silenceremove=stop_periods=-1:stop_duration=0.35:stop_threshold=-42dB:stop_silence=0.15'
    af = f"{trim},{gaps},atempo={TEMPO[v]},{FX[v]},loudnorm=I=-16:TP=-1.5:LRA=9"
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', f"{src}/{s['id']}_cb.wav", '-af', af, '-ar', '44100', '-ac', '1', wav], check=True)
    dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', wav]))
    pcm = np.frombuffer(subprocess.check_output(['ffmpeg', '-loglevel', 'error', '-i', wav, '-f', 's16le', '-ac', '1', '-ar', '16000', '-']), np.int16).astype(np.float32) / 32768
    res, _ = wm.transcribe(pcm, language='fr', word_timestamps=True, beam_size=5)
    ww = [w for seg in res for w in seg.words]
    heard = ' '.join(w.word.strip() for w in ww)
    sw = s['text'].split()
    a, b = [norm(x) for x in s.get('dire', s['text']).split()], [norm(w.word) for w in ww]
    words = [None] * len(sw)
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b).get_opcodes():
        if tag in ('equal', 'replace') and j2 > j1:
            for k in range(i2 - i1):
                j = j1 + min(k * (j2 - j1) // max(1, i2 - i1), j2 - j1 - 1)
                words[i1 + k] = (ww[j].start, ww[j].end)
    for i in range(len(sw)):
        if words[i] is None:
            prev = next((words[k][1] for k in range(i - 1, -1, -1) if words[k]), 0.0)
            nxt = next((words[k][0] for k in range(i + 1, len(sw)) if words[k]), dur)
            words[i] = (prev, prev + (nxt - prev) / 2)
    ratio = difflib.SequenceMatcher(None, ' '.join(a), ' '.join(b)).ratio()
    json.dump({'words': [{'w': w, 's': t[0], 'e': t[1]} for w, t in zip(sw, words)], 'dur': dur, 'voix': v, 'entendu': heard, 'fidelite': round(ratio, 3)},
              open(f"{out}/{s['id']}.json", 'w'), ensure_ascii=False, indent=1)
    print(f"{s['id']:3} {dur:5.2f}s fidélité {ratio:.2f} | {heard}", flush=True)
