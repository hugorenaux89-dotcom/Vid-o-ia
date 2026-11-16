"""Original phonk / montagem soundtrack, synthesized from scratch.

Everything is generated with numpy (no samples, no copyrighted music), so the
beat grid is known exactly and the video can cut frame-perfectly on it.

Outputs:
  build/music.wav     48 kHz stereo master
  build/beatmap.json  sections, beats, kicks, claps, accents (seconds)
"""
import json
import os
import sys

import numpy as np
from scipy import signal

SR = 48000
BPM = 130.0
BEAT = 60.0 / BPM
STEP = BEAT / 4  # 16th note
BAR = BEAT * 4

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")

rng = np.random.default_rng(7)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def t_axis(dur):
    return np.arange(int(dur * SR)) / SR


def env_exp(n, decay):
    return np.exp(-np.arange(n) / SR / decay)


def bp(x, lo, hi, order=2):
    sos = signal.butter(order, [lo, hi], btype="band", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def hp(x, f, order=2):
    sos = signal.butter(order, f, btype="high", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def lp(x, f, order=2):
    sos = signal.butter(order, f, btype="low", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def sweep_lp(x, f0, f1):
    """Time-varying low-pass (filter opening), done in chunks."""
    out = np.zeros_like(x)
    n = len(x)
    chunk = 1024
    zi = None
    for i in range(0, n, chunk):
        frac = i / max(1, n - 1)
        f = f0 * (f1 / f0) ** frac
        sos = signal.butter(2, min(f, SR / 2 - 100), btype="low", fs=SR, output="sos")
        if zi is None:
            zi = signal.sosfilt_zi(sos) * 0
        seg, zi = signal.sosfilt(sos, x[i:i + chunk], zi=zi)
        out[i:i + chunk] = seg
    return out


# ---------------------------------------------------------------- instruments

def kick(drive=2.5):
    d = 0.45
    t = t_axis(d)
    f = 48 + 170 * np.exp(-t / 0.035)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * env_exp(len(t), 0.16)
    click = hp(rng.standard_normal(len(t)), 3000) * env_exp(len(t), 0.004) * 0.5
    return np.tanh(drive * (body + click)) * 0.9


def bass808(note, dur, drive=4.0, glide_from=None):
    t = t_axis(dur)
    f = np.full(len(t), midi(note))
    if glide_from is not None:
        g = np.exp(-t / 0.06)
        f = midi(note) * (midi(glide_from) / midi(note)) ** g
    ph = 2 * np.pi * np.cumsum(f) / SR
    e = np.minimum(1, t / 0.004) * np.exp(-t / (dur * 0.9))
    s = np.sin(ph) + 0.25 * np.sin(2 * ph)
    dist = np.tanh(drive * s) / np.tanh(drive)
    sub = np.sin(ph)
    return (0.55 * dist + 0.6 * sub) * e


def cowbell(note, dur=0.32, bright=1.0):
    """TR-808 style cowbell (two detuned squares, ratio 1.48) pitched to a note."""
    t = t_axis(dur)
    f1 = midi(note)
    f2 = f1 * 1.4815
    sq = signal.square(2 * np.pi * f1 * t) + 0.8 * signal.square(2 * np.pi * f2 * t)
    sq = bp(sq, f1 * 0.9, min(f2 * 3.5 * bright, SR / 2 - 200))
    e = np.exp(-t / 0.018) * 0.6 + np.exp(-t / (dur * 0.45)) * 0.4
    s = sq * e
    return np.tanh(2.2 * s) * 0.5


def clap():
    d = 0.35
    t = t_axis(d)
    n = rng.standard_normal(len(t))
    e = np.zeros(len(t))
    for off in (0.0, 0.009, 0.018, 0.027):
        i = int(off * SR)
        e[i:] += np.exp(-np.arange(len(t) - i) / SR / (0.006 if off < 0.027 else 0.11))
    s = bp(n, 900, 4500) * e
    body = np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.05) * 0.35
    return np.tanh(1.8 * (s + body)) * 0.7


def hat(open_=False):
    d = 0.25 if open_ else 0.05
    t = t_axis(d)
    n = rng.standard_normal(len(t))
    metal = sum(signal.square(2 * np.pi * f * t) for f in (3150, 4160, 5300, 6980, 8100))
    s = hp(0.6 * n + 0.15 * metal, 7000) * env_exp(len(t), 0.07 if open_ else 0.012)
    return s * 0.35


def pad(notes, dur):
    t = t_axis(dur)
    s = np.zeros(len(t))
    for n in notes:
        for det in (-0.12, 0.0, 0.11):
            f = midi(n) * 2 ** (det / 12)
            s += signal.sawtooth(2 * np.pi * f * t + rng.uniform(0, 6))
    s = lp(s, 1400, 2)
    e = np.minimum(1, t / 0.35) * np.minimum(1, (dur - t) / 0.4).clip(0, 1)
    return s * e * 0.06


def riser(dur):
    t = t_axis(dur)
    n = rng.standard_normal(len(t))
    out = np.zeros(len(t))
    chunk = 2048
    for i in range(0, len(t), chunk):
        frac = i / len(t)
        c = 400 * (14000 / 400) ** frac
        out[i:i + chunk] = bp(n[i:i + chunk], c * 0.7, min(c * 1.3, SR / 2 - 500), 1)
    tone_f = 200 * (1600 / 200) ** (t / dur)
    tone = np.sin(2 * np.pi * np.cumsum(tone_f) / SR) * 0.15
    e = (t / dur) ** 2.2
    return (out * 0.5 + tone) * e


ROLL_HITS = []


def snare_roll(dur, start_rate=4, end_rate=32, at=None):
    out = np.zeros(int(dur * SR))
    t = 0.0
    c = clap()
    while t < dur:
        if at is not None:
            ROLL_HITS.append(at + t)
        frac = t / dur
        rate = start_rate * (end_rate / start_rate) ** frac  # hits per beat
        i = int(t * SR)
        seg = c[: len(out) - i] * (0.25 + 0.75 * frac)
        out[i:i + len(seg)] += seg
        t += BEAT / rate
    return out


def sub_drop(dur=2.5):
    t = t_axis(dur)
    f = 70 * (28 / 70) ** (t / dur)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 1.2)
    return np.tanh(2 * s) * 0.9


def reverb(x, seconds=1.8, mix=0.25, pre=0.02):
    n = int(seconds * SR)
    ir = rng.standard_normal(n) * np.exp(-np.arange(n) / SR / (seconds / 5))
    ir = lp(ir, 6000)
    ir[: int(pre * SR)] = 0
    ir /= np.sqrt(np.sum(ir ** 2))
    wet = signal.fftconvolve(x, ir)[: len(x)]
    return x * (1 - mix) + wet * mix * 0.9


# ---------------------------------------------------------------- arrangement

# Sections in bars
SECTIONS = [
    ("intro", 0, 4),
    ("build", 4, 5),
    ("dropA", 5, 13),
    ("break", 13, 15),
    ("dropB", 15, 19),
    ("outro", 19, 21),
]
TOTAL_BARS = 21
LEAD_IN = 0.0  # music starts at t=0

# Key: F minor (F Ab C Db Eb). Chord roots per bar (2-bar cycle x2): Fm Db Eb C
ROOTS = [41, 37, 39, 36]  # F1 Db1 Eb1 C1 (808 octave, shifted +12 below)

# Montagem cowbell riff: tresillo groove, 2 bars = 32 sixteenths.
RIFF = {
    0: 77, 3: 77, 6: 75, 8: 77, 11: 80, 14: 77,
    16: 73, 19: 73, 22: 72, 24: 73, 27: 75, 30: 72,
}
RIFF_B = {  # second half of the 4-bar phrase
    0: 75, 3: 75, 6: 73, 8: 75, 11: 79, 14: 75,
    16: 72, 19: 72, 22: 70, 24: 72, 27: 68, 29: 70, 30: 72,
}

PAD_CHORDS = [[65, 68, 72], [61, 65, 68], [63, 67, 70], [60, 64, 67]]


def bar_t(b):
    return LEAD_IN + b * BAR


def place(buf, x, t, gain=1.0):
    i = int(round(t * SR))
    if i >= len(buf):
        return
    seg = x[: len(buf) - i]
    buf[i:i + len(seg)] += seg * gain


def section_of(bar):
    for name, a, b in SECTIONS:
        if a <= bar < b:
            return name
    return None


def build():
    os.makedirs(BUILD, exist_ok=True)
    total = bar_t(TOTAL_BARS) + 3.0
    n = int(total * SR)
    drums = np.zeros(n)
    bass = np.zeros(n)
    bell = np.zeros(n)
    atmos = np.zeros(n)
    fx = np.zeros(n)
    kick_env = np.zeros(n)  # for sidechain

    beatmap = {"bpm": BPM, "beat": BEAT, "bar": BAR, "sections": [], "beats": [],
               "kicks": [], "claps": [], "accents": [], "downbeats": []}
    for name, a, b in SECTIONS:
        beatmap["sections"].append({"name": name, "start": bar_t(a), "end": bar_t(b)})

    K = kick()
    C = clap()
    H = hat()
    HO = hat(True)

    for bar in range(TOTAL_BARS):
        sec = section_of(bar)
        t0 = bar_t(bar)
        beatmap["downbeats"].append(t0)
        for q in range(4):
            beatmap["beats"].append(t0 + q * BEAT)
        phrase = bar % 4
        riff = RIFF if phrase < 2 else RIFF_B
        riff_off = 0 if phrase % 2 == 0 else 16
        root = ROOTS[phrase]

        # ---- pads (intro / break / outro)
        if sec in ("intro", "build", "break", "outro"):
            g = 1.0 if sec != "outro" else 0.8
            place(atmos, pad(PAD_CHORDS[phrase], BAR + 0.3), t0, g)

        # ---- cowbell riff
        for s in range(16):
            note = riff.get(s + riff_off)
            if note is None:
                continue
            ts = t0 + s * STEP
            if sec == "intro":
                if bar < 2 and s % 8 != 0:
                    continue
                place(bell, cowbell(note, 0.30), ts, 0.55)
            elif sec == "build":
                place(bell, cowbell(note, 0.28), ts, 0.7)
            elif sec in ("dropA", "dropB"):
                place(bell, cowbell(note, 0.30), ts, 1.0)
                if sec == "dropB":
                    place(bell, cowbell(note + 12, 0.22, 1.3), ts, 0.45)
            elif sec == "break":
                place(bell, cowbell(note, 0.45), ts, 0.6)

        # ---- drums + 808
        if sec in ("dropA", "dropB"):
            kick_steps = [0, 6, 10] if sec == "dropA" else [0, 3, 6, 10, 14]
            if bar == SECTIONS[2][2] - 1 or bar == SECTIONS[4][2] - 1:
                kick_steps = [0, 6, 8, 10, 12, 14]  # fill at end of drop
            for s in kick_steps:
                ts = t0 + s * STEP
                place(drums, K, ts, 1.0)
                place(kick_env, np.exp(-np.arange(int(0.2 * SR)) / SR / 0.08), ts)
                beatmap["kicks"].append(ts)
            for s in (4, 12):
                ts = t0 + s * STEP
                place(drums, C, ts, 0.85)
                beatmap["claps"].append(ts)
            # hats: 8ths (dropA) / 16ths (dropB) + rolls on beat 4 every 2 bars
            hat_div = 2 if sec == "dropA" else 1
            for s in range(0, 16, hat_div):
                ts = t0 + s * STEP
                vel = 0.8 if s % 4 == 2 else 0.5
                place(drums, H, ts, vel)
            if bar % 2 == 1:
                for k in range(6):
                    place(drums, H, t0 + 12 * STEP + k * (BEAT / 6), 0.45 + 0.08 * k)
            place(drums, HO, t0 + 14 * STEP, 0.4)
            # 808: root on 1, re-hit on the "and" of 2, glide on 4
            place(bass, bass808(root, BEAT * 1.4, 4.5), t0, 1.0)
            place(bass, bass808(root, BEAT * 0.9, 4.5), t0 + 6 * STEP, 0.9)
            place(bass, bass808(root + 12, BEAT * 1.5, 5.0, glide_from=root),
                  t0 + 10 * STEP, 0.85)
        elif sec == "intro" and bar >= 2:
            place(bass, bass808(root, BAR * 0.9, 2.5), t0, 0.55)
        elif sec == "build":
            place(fx, snare_roll(BAR - BEAT * 0.5, at=t0), t0, 0.5)
            place(fx, riser(BAR), t0, 0.9)
            place(bass, bass808(root, BEAT * 2, 3.0), t0, 0.6)
        elif sec == "break":
            if bar == SECTIONS[3][1]:
                place(bass, bass808(ROOTS[0], BAR * 1.6, 3.5), t0, 0.9)
            if bar == SECTIONS[3][2] - 1:
                place(fx, snare_roll(BAR - BEAT * 0.5, 2, 24, at=t0), t0, 0.45)
                place(fx, riser(BAR), t0, 0.8)
        elif sec == "outro":
            if bar == SECTIONS[5][1]:
                place(drums, K, t0, 1.0)
                place(bass, bass808(ROOTS[0], BAR * 2.2, 4.0), t0, 1.0)
                place(fx, sub_drop(3.0), t0, 0.8)
                beatmap["kicks"].append(t0)

    # big hits at drops
    for name in ("dropA", "dropB"):
        a = [s for s in SECTIONS if s[0] == name][0][1]
        place(fx, sub_drop(2.4), bar_t(a), 0.9)
        beatmap["accents"].append(bar_t(a))
    beatmap["accents"].append(bar_t(SECTIONS[5][1]))

    # gap of silence right before each drop (classic edit "breath")
    for name in ("dropA", "dropB"):
        a = [s for s in SECTIONS if s[0] == name][0][1]
        g0 = int((bar_t(a) - BEAT * 0.5) * SR)
        g1 = int(bar_t(a) * SR) - 64
        for buf in (drums, bass, bell, atmos, fx):
            buf[g0:g1] *= np.linspace(1, 0, g1 - g0) ** 6

    # ---- processing
    sc = 1 - 0.75 * np.clip(kick_env, 0, 1)
    bass *= sc
    atmos *= 1 - 0.5 * np.clip(kick_env, 0, 1)

    # intro cowbell: filter opens over the intro
    ia = int(bar_t(0) * SR)
    ib = int(bar_t(5) * SR)
    bell[ia:ib] = sweep_lp(bell[ia:ib], 700, 9000)
    bell = reverb(bell, 1.6, 0.28)
    atmos = reverb(atmos, 2.5, 0.4)
    fx = reverb(fx, 1.2, 0.2)
    bass = lp(bass, 5000)

    # stereo: bell/hats slightly wide using Haas delay
    def widen(x, ms=9):
        d = int(ms / 1000 * SR)
        r = np.concatenate([np.zeros(d), x[:-d]])
        return np.stack([x, r * 0.96], 1)

    def mono(x):
        return np.stack([x, x], 1)

    mix = (mono(drums) * 0.95 + mono(bass) * 0.95 + widen(bell, 11) * 0.62 +
           widen(atmos, 17) * 1.0 + widen(fx, 7) * 0.8)

    # master: glue saturation + limiter
    mix = mix / np.max(np.abs(mix))
    mix = np.tanh(mix * 1.6) / np.tanh(1.6)
    mix = mix * 0.89  # ~ -1 dBFS peak

    # fade out tail
    tail = int(bar_t(TOTAL_BARS) * SR)
    fade = np.linspace(1, 0, n - tail) ** 2
    mix[tail:] *= fade[:, None]

    import soundfile as sf
    sf.write(os.path.join(BUILD, "music.wav"), mix.astype(np.float32), SR, subtype="PCM_24")
    beatmap["duration"] = total
    beatmap["rolls"] = sorted(ROLL_HITS)
    with open(os.path.join(BUILD, "beatmap.json"), "w") as f:
        json.dump(beatmap, f, indent=1)
    print("music.wav", total, "s;", len(beatmap["kicks"]), "kicks")


if __name__ == "__main__":
    build()
