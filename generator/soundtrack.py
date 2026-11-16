#!/usr/bin/env python3
"""
Bande-son calee sur les passages de la video : 4 musiques (une par partie de l'histoire)
+ voix off motivante en anglais. Fonctionne pour n'importe quelle vitesse (--speed).

    python3 generator/soundtrack.py --speed 1.5 -o assets/bande_son_x1.5.m4a
"""
import argparse
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
SND = os.path.join(HERE, "..", "assets", "sons")

# (fichier, debut, fin) en secondes sur la timeline x1 — memes coupes que ego_video.SCENES
MUSIC = [
    ("m1_tension.mp3", 0.0, 9.6),     # podium + moqueries
    ("m2_training.mp3", 9.6, 20.3),   # day 1, time-lapse, jour X
    ("m3_climax.mp3", 20.3, 31.7),    # chute, obsessed, you vs you
    ("m4_drop.mp3", 31.7, 42.1),      # course gagnee, prove them wrong, podium final
]

# (fichier, instant x1, texte)
VOICE = [
    ("v01.mp3", 0.4, "They said I'd never make it."),
    ("v02.mp3", 6.4, "They laughed at me."),
    ("v03.mp3", 9.9, "Day one. Zero."),
    ("v04.mp3", 12.9, "So I showed up. Every. Single. Day."),
    ("v05.mp3", 17.9, "Some days... I wanted to quit."),
    ("v06.mp3", 20.6, "I fell... and they laughed again."),
    ("v07.mp3", 24.6, "They call it obsession."),
    ("v08.mp3", 26.3, "Obsession beats talent."),
    ("v09.mp3", 28.1, "It was never them. It's you... versus you."),
    ("v10.mp3", 35.6, "Now... prove them all wrong."),
]
TOTAL = 42.1


def duration(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                   "-of", "csv=p=0", path])
    return float(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--speed", type=float, default=1.0)
    ap.add_argument("-o", "--output", default="assets/bande_son.m4a")
    args = ap.parse_args()
    sp = args.speed
    tempo = 1.0 if sp <= 1 else min(1.15, sp)  # voix un peu plus rapide en version acceleree

    inputs, filters, labels = [], [], []
    for i, (f, a, b) in enumerate(MUSIC):
        inputs += ["-i", os.path.join(SND, f)]
        start, ln = a / sp, (b - a) / sp
        last = i == len(MUSIC) - 1
        filters.append(
            f"[{i}:a]atrim=0:{ln + 0.45:.3f},afade=t=in:d={0.05 if i == 0 else 0.35},"
            f"afade=t=out:st={ln - (1.5 if last else 0.05):.3f}:d={1.5 if last else 0.5},"
            f"adelay={int(start * 1000)}|{int(start * 1000)}[m{i}]")
        labels.append(f"[m{i}]")
    n = len(MUSIC)
    filters.append("".join(labels) + f"amix=inputs={n}:normalize=0,volume=0.9[music]")

    vlabels = []
    prev_end = 0.0
    for k, (f, t, _) in enumerate(VOICE):
        path = os.path.join(SND, f)
        inputs += ["-i", path]
        d = duration(path) / tempo
        start = max(t / sp, prev_end + 0.12)
        prev_end = start + d
        idx = n + k
        filters.append(f"[{idx}:a]atempo={tempo},adelay={int(start * 1000)}|{int(start * 1000)}[v{k}]")
        vlabels.append(f"[v{k}]")
    filters.append("".join(vlabels) + f"amix=inputs={len(VOICE)}:normalize=0,"
                   "equalizer=f=120:t=q:w=1:g=3,aecho=0.8:0.5:60:0.18,volume=1.6,asplit=2[voice][side]")
    filters.append("[music][side]sidechaincompress=threshold=0.04:ratio=6:attack=15:release=350[duck]")
    filters.append(f"[duck][voice]amix=inputs=2:normalize=0,atrim=0:{TOTAL / sp:.3f},"
                   "loudnorm=I=-14:TP=-1.5[out]")
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    cmd = ["ffmpeg", "-y", "-v", "error"] + inputs + ["-filter_complex", ";".join(filters),
                                                      "-map", "[out]", "-ar", "44100", "-c:a", "aac",
                                                      "-b:a", "192k", args.output]
    subprocess.check_call(cmd)
    print(f"-> {args.output} ({TOTAL / sp:.1f}s)")


if __name__ == "__main__":
    main()
