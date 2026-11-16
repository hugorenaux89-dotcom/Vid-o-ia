"""Synthèse audio simple (numpy) : piano, nappes de cordes, percussions, effets."""
import numpy as np
from scipy.signal import lfilter

SR = 44100


def note_freq(name):
    names = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6, "Gb": 6,
             "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}
    p, o = name[:-1], int(name[-1])
    midi = 12 * (o + 1) + names[p]
    return 440.0 * 2 ** ((midi - 69) / 12)


class Track:
    def __init__(self, duration):
        self.buf = np.zeros((int(duration * SR) + SR * 6, 2), dtype=np.float64)

    def add(self, t, sig, gain=1.0, pan=0.0):
        i = int(t * SR)
        if i < 0:
            sig = sig[-i:]
            i = 0
        if sig.ndim == 1:
            l, r = np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))
            sig = np.stack([sig * l, sig * r], axis=1)
        n = min(len(sig), len(self.buf) - i)
        if n > 0:
            self.buf[i : i + n] += sig[:n] * gain


def lowpass_fast(x, cutoff):
    a = 1 - np.exp(-2 * np.pi * cutoff / SR)
    return lfilter([a], [1, -(1 - a)], x, axis=0)


def piano(freq, dur=3.0, vel=0.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    decay = 1.6 + freq / 400
    for h, amp in enumerate([1.0, 0.5, 0.28, 0.16, 0.1, 0.06, 0.04], start=1):
        f = freq * h * (1 + 0.0004 * h * h)
        if f > 16000:
            break
        out += amp * np.sin(2 * np.pi * f * t) * np.exp(-t * decay * (1 + 0.45 * h))
    att = np.minimum(1, t / 0.004)
    rel = np.minimum(1, (dur - t) / 0.15)
    return out * att * rel * vel * 0.35


def saw(freq, n, detune=0.0, phase=0.0):
    t = np.arange(n) / SR
    f = freq * (1 + detune)
    return 2 * ((t * f + phase) % 1.0) - 1


def pad(freqs, dur, vel=0.3, attack=1.2, release=1.5, cutoff=1200, vibrato=0.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    rng = np.random.default_rng(int(sum(freqs)))
    for f in freqs:
        for d in (-0.006, 0.0, 0.007):
            vib = 1 + vibrato * np.sin(2 * np.pi * 5.2 * t + rng.uniform(0, 6))
            ph = np.cumsum(f * (1 + d) * vib) / SR + rng.uniform()
            out += 2 * (ph % 1.0) - 1
    out /= max(1, len(freqs) * 3)
    out = lowpass_fast(out, cutoff)
    out = lowpass_fast(out, cutoff * 1.5)
    env = np.minimum(1, t / attack) * np.minimum(1, np.maximum(0, (dur - t)) / release)
    return out * env * vel


def kick(vel=1.0, f0=110, f1=42, dur=0.6):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t * 22)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 6) * vel


def tom(vel=1.0, f0=95, dur=0.7):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f0 * (0.7 + 0.3 * np.exp(-t * 15))
    ph = 2 * np.pi * np.cumsum(f) / SR
    rng = np.random.default_rng(1)
    noise = lowpass_fast(rng.normal(0, 1, n), 1500) * np.exp(-t * 30) * 0.5
    return (np.sin(ph) * np.exp(-t * 5) + noise) * vel


def snare(vel=1.0, dur=0.3):
    n = int(dur * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(2)
    nz = rng.normal(0, 1, n)
    nz = nz - lowpass_fast(nz, 900)
    return (0.6 * nz * np.exp(-t * 18) + 0.5 * np.sin(2 * np.pi * 190 * t) * np.exp(-t * 25)) * vel


def thud(vel=1.0):
    n = int(0.25 * SR)
    t = np.arange(n) / SR
    f = 70 + 120 * np.exp(-t * 40)
    ph = 2 * np.pi * np.cumsum(f) / SR
    rng = np.random.default_rng(3)
    click = lowpass_fast(rng.normal(0, 1, n), 2500) * np.exp(-t * 120) * 0.4
    return (np.sin(ph) * np.exp(-t * 18) + click) * vel


def riser(dur, vel=0.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(4)
    nz = rng.normal(0, 1, n)
    x = t / dur
    a = 1 - np.exp(-2 * np.pi * (300 + 7000 * x**2) / SR)
    # filtre à coupure variable approximé par segments
    out = np.zeros(n)
    seg = SR // 20
    zi = np.zeros(1)
    for i in range(0, n, seg):
        aa = a[i]
        y, zi = lfilter([aa], [1, -(1 - aa)], nz[i : i + seg], zi=zi)
        out[i : i + seg] = y
    f = 110 * 2 ** (x * 2)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.3
    return (out * 2 + tone) * x**2 * vel


def reverb(x, seconds=2.6, mix=0.3, seed=7):
    n = int(seconds * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(seed)
    out = np.empty_like(x)
    for ch in range(x.shape[1]):
        ir = rng.normal(0, 1, n) * np.exp(-t * 6.9 / seconds)
        ir = lowpass_fast(ir, 5000)
        ir /= np.sqrt(np.sum(ir**2))
        L = len(x[:, ch]) + n
        nfft = 1 << (L - 1).bit_length()
        wet = np.fft.irfft(np.fft.rfft(x[:, ch], nfft) * np.fft.rfft(ir, nfft), nfft)[: len(x)]
        out[:, ch] = wet
    return x * (1 - mix) + out * mix * 1.6


def load_wav(path):
    import wave

    with wave.open(path) as w:
        n = w.getnframes()
        data = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float64) / 32768
        data = data.reshape(-1, w.getnchannels())
        if data.shape[1] == 1:
            data = np.repeat(data, 2, axis=1)
    return data


def save_wav(path, x):
    import wave

    x = np.clip(x, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())
