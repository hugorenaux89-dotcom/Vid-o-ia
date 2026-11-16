"""Musique de fond générée (boucle légère, 100 BPM, La mineur - Fa - Do - Sol) : python3 musique.py sortie.wav secondes"""
import sys, numpy as np, wave
SR = 44100; out = sys.argv[1]; dur = float(sys.argv[2]) if len(sys.argv) > 2 else 120
bpm = 100; beat = 60 / bpm; n = int(SR * dur); t = np.arange(n) / SR; mix = np.zeros(n)
rng = np.random.default_rng(3)
def env(tt, a, d): return np.where(tt < a, tt / a, np.exp(-(tt - a) / d))
def add(at, sig):
    i = int(at * SR); j = min(n, i + len(sig))
    if i < n: mix[i:j] += sig[: j - i]
def lp(x, k):  # passe-bas simple
    y = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x): acc += k * (v - acc); y[i] = acc
    return y
# instruments
tk = np.arange(int(0.35 * SR)) / SR
kick = np.sin(2 * np.pi * (48 + 90 * np.exp(-tk * 30)) * tk) * np.exp(-tk * 9)
ts = np.arange(int(0.22 * SR)) / SR
snare = lp(rng.standard_normal(len(ts)), 0.35) * np.exp(-ts * 22) * 0.55 + np.sin(2 * np.pi * 190 * ts) * np.exp(-ts * 30) * 0.25
th = np.arange(int(0.05 * SR)) / SR
hat = (rng.standard_normal(len(th)) - lp(rng.standard_normal(len(th)), 0.5)) * np.exp(-th * 90) * 0.07
notes = {'A2': 110.0, 'F2': 87.31, 'C3': 130.81, 'G2': 98.0}
chords = [('A2', [220.0, 261.63, 329.63]), ('F2', [174.61, 220.0, 261.63]), ('C3', [196.0, 261.63, 329.63]), ('G2', [196.0, 246.94, 293.66])]
bar = 4 * beat; nb = int(dur / bar) + 1
for b in range(nb):
    root, ch = chords[b % 4]; t0 = b * bar
    for k in range(4):
        add(t0 + k * beat, kick * (0.9 if k in (0, 2) else 0.55))
        if k in (1, 3): add(t0 + k * beat, snare)
        for h in range(2): add(t0 + k * beat + h * beat / 2, hat * (1 if h else 0.6))
    # basse (croches syncopées)
    for k, off in enumerate([0, 0.75, 1.5, 2, 2.75, 3.5]):
        tb = np.arange(int(beat * 0.6 * SR)) / SR
        f = notes[root] * (2 if k == 4 else 1)
        add(t0 + off * beat, (np.sign(np.sin(2 * np.pi * f * tb)) * 0.25 + np.sin(2 * np.pi * f * tb)) * env(tb, 0.005, 0.18) * 0.32)
    # accords pincés (doux)
    for k in (0.5, 1.5, 2.5, 3.0, 3.5):
        tc = np.arange(int(beat * 0.9 * SR)) / SR
        s = sum(np.sin(2 * np.pi * f * tc) + 0.3 * np.sin(4 * np.pi * f * tc) for f in ch) / 3
        add(t0 + k * beat, s * env(tc, 0.004, 0.22) * 0.16)
mix = lp(mix, 0.55)
mix *= 0.85 / max(1e-6, np.abs(mix).max())
fade = int(SR * 1.0); mix[:fade] *= np.linspace(0, 1, fade); mix[-fade:] *= np.linspace(1, 0, fade)
pcm = (np.clip(mix, -1, 1) * 32000).astype(np.int16)
with wave.open(out, 'w') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
