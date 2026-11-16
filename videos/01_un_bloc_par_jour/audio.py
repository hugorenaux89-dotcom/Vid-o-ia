"""Bande-son de la vidéo 01 : musique synthétisée + effets synchronisés.

Usage : python3 audio.py EVENTS_JSON SFX_DIR OUT_WAV
SFX_DIR contient rain.wav, thunder.wav, impact.wav, whoosh.wav, hiss.wav (générés via ElevenLabs).
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from engine.music import (  # noqa: E402
    SR, Track, kick, load_wav, note_freq as N, pad, piano, reverb, riser, save_wav, snare, thud, tom,
)

DUR = 74.0
BAR = 3.0  # 80 BPM, 4/4
BEAT = BAR / 4

# progression i - VI - III - VII en la mineur
CHORDS = [
    ("A2", ["A3", "C4", "E4"]),
    ("F2", ["F3", "A3", "C4"]),
    ("C3", ["C3", "E3", "G3"]),
    ("G2", ["G3", "B3", "D4"]),
]


def chord_at(bar):
    return CHORDS[bar % 4]


def arp(track, t0, bar, vel, octave_up=False, step=BEAT / 2):
    bass, tones = chord_at(bar)
    fr = [N(x) for x in tones]
    pattern = [fr[0], fr[2], fr[0] * 2, fr[1] * 2, fr[0] * 2 * (2 if octave_up else 1), fr[1] * 2, fr[0] * 2, fr[2]]
    nsteps = int(round(BAR / step))
    for i in range(nsteps):
        f = pattern[i % len(pattern)]
        track.add(t0 + i * step, piano(f, 2.2, vel * (1.0 if i % 4 == 0 else 0.75)), pan=-0.2 + 0.4 * (i % 2))


def main(events_path, sfx_dir, out_path):
    music = Track(DUR)
    nbars = int(DUR / BAR) + 1
    for b in range(nbars):
        t0 = b * BAR
        bass, tones = chord_at(b)
        fb = N(bass)
        ft = [N(x) for x in tones]
        # --- A/B : piano en arpèges (0 - 22 s)
        if t0 < 21:
            v = 0.32 if t0 < 9 else 0.42
            arp(music, t0, b, v)
            music.add(t0, pad(ft, BAR + 1.5, 0.05 if t0 < 9 else 0.08, attack=1.0, cutoff=900), pan=0)
        if 9 <= t0 < 21:
            for k in (0, 2):
                music.add(t0 + k * BEAT, kick(0.45, dur=0.5))
            music.add(t0, piano(fb, 3.0, 0.5))
        # --- C : pluie, cordes sombres, battement de cœur (21 - 35 s)
        if 21 <= t0 < 35:
            music.add(t0, pad([fb, fb * 2] + ft, BAR + 2, 0.11, attack=1.5, cutoff=700, vibrato=0.002))
            for k in range(4):
                music.add(t0 + k * BEAT, piano(ft[k % 3] * 2, 2.0, 0.26))
            for k in (0, 2):
                music.add(t0 + k * BEAT, kick(0.5, 70, 40, 0.4))
                music.add(t0 + k * BEAT + 0.24, kick(0.32, 70, 40, 0.4))
        # --- D : montée (35 - 47 s)
        if 35 <= t0 < 47:
            grow = (t0 - 33) / 14
            music.add(t0, pad([fb, fb * 2] + ft + [ft[0] * 2], BAR + 1.5, 0.12 + 0.1 * grow, attack=0.6, cutoff=900 + 1500 * grow, vibrato=0.003))
            arp(music, t0, b, 0.3 + 0.12 * grow, octave_up=True)
            for k in range(4):
                music.add(t0 + k * BEAT, tom(0.35 + 0.35 * grow, 90 if k % 2 == 0 else 120))
            music.add(t0, kick(0.8))
            music.add(t0 + 2 * BEAT, snare(0.25 + 0.3 * grow))
        # --- E : effort, quasi silence (47 - 55 s)
        if 47 <= t0 < 55:
            music.add(t0, pad([N("A1"), N("A2"), N("E3")], BAR + 1, 0.12, attack=1.0, cutoff=500))
            music.add(t0 + 0.2, kick(0.55, 70, 40, 0.4))
            music.add(t0 + 0.44, kick(0.38, 70, 40, 0.4))
            music.add(t0 + 1.7, kick(0.55, 70, 40, 0.4))
            music.add(t0 + 1.94, kick(0.38, 70, 40, 0.4))
            music.add(t0 + 1.0, piano(N("E5"), 2.5, 0.22), pan=0.3)
            music.add(t0 + 2.5, piano(N("A5") if b % 2 else N("C6"), 2.5, 0.16), pan=-0.3)
        # --- G : apothéose (60 - 69 s)
        if 60 <= t0 < 69:
            music.add(t0, pad([fb / 2, fb, fb * 2] + ft + [f * 2 for f in ft], BAR + 1.2, 0.3, attack=0.15, cutoff=2600, vibrato=0.004))
            arp(music, t0, b, 0.5, octave_up=True, step=BEAT / 4)
            for k in range(4):
                music.add(t0 + k * BEAT, kick(1.0 if k % 2 == 0 else 0.6))
                music.add(t0 + k * BEAT, tom(0.5, 80))
            music.add(t0 + BEAT, snare(0.6))
            music.add(t0 + 3 * BEAT, snare(0.6))
            music.add(t0, piano(fb, 3.0, 0.8))
    # --- F : roulement + montée (55 - 59.6 s)
    t = 55.0
    while t < 59.55:
        x = (t - 55) / 4.6
        music.add(t, tom(0.3 + 0.6 * x, 100 + 40 * x))
        if x > 0.5:
            music.add(t, snare(0.2 + 0.5 * x))
        t += 0.75 * (1 - x) + 0.09 * x
    music.add(55.0, riser(4.6, 0.6))
    # mélodie finale
    mel = [("A5", 60.0), ("C6", 61.125), ("B5", 61.875), ("A5", 63.0), ("G5", 64.125), ("E5", 64.875),
           ("G5", 66.0), ("E5", 67.125), ("D5", 67.875), ("E5", 69.0)]
    for nm, tt in mel:
        music.add(tt, piano(N(nm), 3.0, 0.75), pan=0.1)
        music.add(tt, piano(N(nm) / 2, 3.0, 0.4), pan=-0.1)
    # --- H : résolution (69 - 74 s)
    for i, nm in enumerate(["A2", "E3", "A3", "C4", "E4", "A4"]):
        music.add(69.0 + i * 0.12, piano(N(nm), 5.0, 0.45))
    music.add(69.0, pad([N("A2"), N("A3"), N("C4"), N("E4")], 5.0, 0.12, attack=0.3, release=3.5, cutoff=1500))

    mus = reverb(music.buf, 2.8, 0.32)

    # ------------------------------------------------- effets
    fx = Track(DUR)
    ev = json.load(open(events_path))
    sfx = {k: load_wav(os.path.join(sfx_dir, k + ".wav")) for k in ("rain", "thunder", "impact", "whoosh", "hiss")}
    for e in ev:
        g = e.get("gain", 1.0)
        if e["type"] == "thud":
            fx.add(e["t"], thud(0.5 * g))
        elif e["type"] == "thud_big":
            fx.add(e["t"], thud(0.9 * g))
            fx.add(e["t"], kick(0.4 * g))
        elif e["type"] == "ignite":
            fx.add(e["t"] - 0.15, sfx["whoosh"], 0.8)
        elif e["type"] == "extinguish":
            fx.add(e["t"], sfx["hiss"], 0.7)
        elif e["type"] == "thunder":
            fx.add(e["t"], sfx["thunder"], 0.75)
        elif e["type"] == "impact":
            fx.add(e["t"] - 0.05, sfx["impact"], 0.9)
    # pluie : boucle avec fondu, 22.3 → 58.5
    rain = sfx["rain"]
    t, n0 = 22.3, len(rain)
    rain_tr = Track(DUR)
    while t < 58.5:
        seg = rain.copy()
        fade = int(1.0 * SR)
        ramp = np.linspace(0, 1, fade)[:, None]
        seg[:fade] *= ramp
        seg[-fade:] *= ramp[::-1]
        rain_tr.add(t, seg, 1.0)
        t += n0 / SR - 1.0
    tt = np.arange(len(rain_tr.buf)) / SR
    renv = np.clip((tt - 22.3) / 1.7, 0, 1) * np.clip((58.5 - tt) / 4.0, 0, 1)
    rain_tr.buf *= (renv * 0.45)[:, None]

    mix = mus * 0.85 + fx.buf * 0.9 + rain_tr.buf
    n = int(DUR * SR)
    mix = mix[:n]
    # fondu de fin
    tt = np.arange(n) / SR
    mix *= np.clip((DUR - tt) / 1.5, 0, 1)[:, None]
    mix *= np.clip(tt / 0.3, 0, 1)[:, None]
    mix = np.tanh(mix / np.max(np.abs(mix)) * 1.6) / np.tanh(1.6) * 0.89
    save_wav(out_path, mix)


if __name__ == "__main__":
    main(*sys.argv[1:4])
