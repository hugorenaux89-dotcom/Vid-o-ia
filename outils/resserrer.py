"""Resserre une voix : coupe les blancs entre mots (> MAXGAP) et accélère (atempo).
Usage : resserrer.py <dir_source> <dir_sortie> <tempo> id[:mot_debut:mot_fin:nom] ..."""
import json, sys, subprocess
src, out, tempo = sys.argv[1], sys.argv[2], float(sys.argv[3])
MAXGAP, PAD = 0.16, 0.06
for spec in sys.argv[4:]:
    parts = spec.split(':')
    sid = parts[0]; name = parts[3] if len(parts) > 3 else sid
    d = json.load(open(f"{src}/{sid}.json")); words = d['words']
    if len(parts) > 1:
        a = int(parts[1]); b = int(parts[2]); words = words[a:b + 1]
    # segments à garder
    segs = []
    for i, w in enumerate(words):
        s = max(0, w['s'] - PAD) if i == 0 else w['s']
        e = w['e'] + (PAD if i == len(words) - 1 else 0)
        if segs and s - segs[-1][1] <= MAXGAP: segs[-1][1] = e
        else:
            if segs: s = s - min(0.04, s - segs[-1][1])
            segs.append([s, e])
    # nouvelles positions des mots
    new, t, j = [], 0.0, 0
    for (s, e) in segs:
        while j < len(words) and words[j]['s'] < e:
            w = words[j]; new.append({'w': w['w'], 's': (t + w['s'] - s) / tempo, 'e': (t + min(w['e'], e) - s) / tempo}); j += 1
        t += (e - s) + (0.12 if (s, e) != tuple(segs[-1]) else 0)
    filt = ''.join(f"[0:a]atrim={s:.3f}:{e:.3f},asetpts=PTS-STARTPTS[p{i}];" for i, (s, e) in enumerate(segs))
    gap = "anullsrc=r=44100:cl=mono,atrim=0:0.12[g];" ; 
    seq = []
    for i in range(len(segs)):
        seq.append(f"[p{i}]")
        if i < len(segs) - 1: seq.append(f"[g{i}]")
    gaps = ''.join(f"anullsrc=r=44100:cl=mono,atrim=0:0.12,asetpts=PTS-STARTPTS[g{i}];" for i in range(len(segs) - 1))
    filt = filt + gaps + ''.join(seq) + f"concat=n={len(seq)}:v=0:a=1,atempo={tempo}[o]"
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', f"{src}/{sid}.mp3", '-filter_complex', filt, '-map', '[o]', '-ar', '44100', '-ac', '1', '-c:a', 'libmp3lame', '-q:a', '2', f"{out}/{name}.mp3"], check=True)
    dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f"{out}/{name}.mp3"]))
    json.dump({'words': new, 'dur': dur}, open(f"{out}/{name}.json", 'w'), ensure_ascii=False, indent=1)
    print(name, f"{d['dur']:.2f}s -> {dur:.2f}s")
