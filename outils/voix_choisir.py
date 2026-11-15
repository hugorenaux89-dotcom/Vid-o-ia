"""Choisit, pour chaque réplique, la meilleure prise (fidélité Whisper la plus haute, sans hallucination de longueur).
Usage : voix_choisir.py <voix-off.json> <dossier_candidats> <dossier_voix> ids"""
import json, sys, os, shutil, subprocess, glob
spec, cand, final, ids = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4].split(',')
here = os.path.dirname(__file__)
for i in ids:
    best = None
    for f in sorted(glob.glob(f'{cand}/{i}_cb_s*.wav')):
        seed = f.split('_s')[-1][:-4]
        tmp_in, tmp_out = f'{cand}/tmp_{seed}', f'{cand}/out_{seed}'
        os.makedirs(tmp_in, exist_ok=True)
        shutil.copy(f, f'{tmp_in}/{i}_cb.wav')
        subprocess.run([sys.executable, f'{here}/voix_post.py', spec, tmp_in, tmp_out, i], capture_output=True)
        j = json.load(open(f'{tmp_out}/{i}.json'))
        n = len(j['words']); rate = n / max(j['dur'], 0.3)
        score = j['fidelite'] - (0.3 if rate < 1.2 else 0)   # pénalise les prises trop longues (hallucinations)
        print(f"  {i} graine {seed}: fidélité {j['fidelite']:.2f} débit {rate:.1f} mots/s | {j['entendu']}")
        if not best or score > best[0]: best = (score, tmp_out, f)
    shutil.copy(best[2], os.path.join(os.path.dirname(final), 'brut', f'{i}_cb.wav'))
    shutil.copy(f'{best[1]}/{i}.wav', f'{final}/{i}.wav'); shutil.copy(f'{best[1]}/{i}.json', f'{final}/{i}.json')
    print(f"=> {i} : prise retenue (score {best[0]:.2f})")
