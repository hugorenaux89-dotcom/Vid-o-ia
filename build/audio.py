"""Bande-son : musique 120 BPM procédurale (intensité par niveau), effets de quiz, voix, ducking."""
import json, os, subprocess
import numpy as np
from timeline import ROOT, VOICE_DIR, build

SR = 44100
rng = np.random.default_rng(7)


def env(n, a=0.002, d=0.1):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / d)


def tone(f, length, d=0.1, wave="sine", a=0.002):
    n = int(length * SR); t = np.arange(n) / SR
    if wave == "sine":
        w = np.sin(2 * np.pi * f * t)
    elif wave == "saw":
        w = 2 * ((f * t) % 1) - 1
    elif wave == "square":
        w = np.sign(np.sin(2 * np.pi * f * t))
    return w * env(n, a, d)


def lowpass(x, alpha):
    y = np.empty_like(x); acc = 0.0
    # filtre RC simple vectorisé par blocs
    from scipy.signal import lfilter
    return lfilter([alpha], [1, alpha - 1], x)


def highpass(x, alpha):
    return x - lowpass(x, alpha)


# ---------- EFFETS ----------
def sfx_whoosh():
    n = int(0.35 * SR); t = np.arange(n) / SR
    noise = rng.standard_normal(n)
    out = np.zeros(n)
    # balayage de filtre : on mélange plusieurs bandes
    for k, a in enumerate(np.linspace(0.02, 0.5, 8)):
        seg = lowpass(noise, a) * np.exp(-((t - 0.04 * k) / 0.06) ** 2)
        out += seg
    return 0.8 * out / np.abs(out).max()


def sfx_pop():
    n = int(0.12 * SR); t = np.arange(n) / SR
    f = 900 * np.exp(-t * 25) + 300
    w = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.001, 0.035)
    return 0.7 * w


def sfx_tick(high=True):
    n = int(0.04 * SR)
    f = 2400 if high else 1800
    w = tone(f, 0.04, 0.008) + 0.5 * highpass(rng.standard_normal(n), 0.3) * env(n, 0.0005, 0.004)
    return 0.45 * w


def sfx_ding():
    out = 0
    for f, g, d in [(1318.5, 1, 0.35), (2637, 0.4, 0.2), (1975.5, 0.5, 0.3), (3951, 0.15, 0.12)]:
        out = out + g * tone(f, 0.7, d, a=0.001)
    return 0.55 * out / 2.05


def sfx_levelup():
    notes = [523.25, 659.25, 783.99, 1046.5, 1318.5]
    out = np.zeros(int(0.6 * SR))
    for i, f in enumerate(notes):
        s = int(i * 0.07 * SR)
        x = tone(f, 0.3, 0.12, "square") * 0.5 + tone(f, 0.3, 0.15)
        out[s:s + len(x)] += x[:len(out) - s]
    return 0.35 * out / np.abs(out).max()


def sfx_impact():
    n = int(0.9 * SR); t = np.arange(n) / SR
    f = 110 * np.exp(-t * 6) + 38
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.35)
    rumble = lowpass(rng.standard_normal(n), 0.03) * env(n, 0.01, 0.4) * 4
    crack = highpass(rng.standard_normal(n), 0.5) * env(n, 0.0005, 0.03)
    out = boom + 0.6 * rumble + 0.5 * crack
    return 0.95 * np.tanh(1.5 * out) / np.tanh(1.5)


def sfx_jingle():
    seq = [(0.0, 783.99), (0.12, 1046.5), (0.24, 1318.5), (0.36, 1567.98), (0.5, 2093.0)]
    out = np.zeros(int(1.1 * SR))
    for s, f in seq:
        x = tone(f, 0.5, 0.18) + 0.3 * tone(f * 2, 0.5, 0.1)
        i = int(s * SR); out[i:i + len(x)] += x[:len(out) - i]
    return 0.4 * out / np.abs(out).max()


# ---------- MUSIQUE ----------
def kick():
    n = int(0.35 * SR); t = np.arange(n) / SR
    f = 150 * np.exp(-t * 30) + 48
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.001, 0.12)


def clap():
    n = int(0.2 * SR)
    x = highpass(rng.standard_normal(n), 0.4)
    e = np.zeros(n)
    for o in [0, 0.008, 0.016]:
        i = int(o * SR); e[i:] += env(n - i, 0.0005, 0.05 if o == 0.016 else 0.006)
    return 0.6 * x * e


def hat(open_=False):
    n = int((0.12 if open_ else 0.04) * SR)
    return 0.25 * highpass(rng.standard_normal(n), 0.7) * env(n, 0.0005, 0.04 if open_ else 0.01)


def music(total, levels_at, cuts):
    """levels_at: liste (t, niveau 0..3). cuts: [(t0,t1)] coupure nette."""
    n = int(total * SR) + SR
    drums = np.zeros(n); bass = np.zeros(n); keys = np.zeros(n); lead = np.zeros(n)
    beat = 0.5
    prog = [(110.0, [220.0, 261.63, 329.63]),   # Am
            (87.31, [174.61, 220.0, 261.63]),   # F
            (130.81, [261.63, 329.63, 392.0]),  # C
            (98.0, [196.0, 246.94, 293.66])]    # G

    def lvl(t):
        L = 0
        for t0, l in levels_at:
            if t >= t0: L = l
        return L

    K, C, H, HO = kick(), clap(), hat(), hat(True)
    sixteenth = beat / 4
    steps = int(total / sixteenth) + 2
    for s in range(steps):
        t = s * sixteenth; i = int(t * SR)
        L = lvl(t)
        bar = int(t // 2.0); pos = s % 16
        root, chord = prog[bar % 4]

        def put(buf, x, g=1.0):
            j = min(len(buf), i + len(x)); buf[i:j] += g * x[:j - i]
        if pos % 4 == 0: put(drums, K, 0.9)
        if pos in (4, 12): put(drums, C, 0.7 if L >= 1 else 0.45)
        if pos % 2 == 0: put(drums, H, 0.8)
        if L >= 2 and pos % 2 == 1: put(drums, H, 0.5)
        if L >= 1 and pos in (2, 6, 10, 14): put(drums, HO, 0.5)
        if L >= 3 and pos in (14, 15): put(drums, K, 0.5)
        # basse : croches décalées
        if pos % 2 == 0 and pos % 4 != 0 or (L >= 2 and pos % 4 == 0):
            f = root * (2 if pos in (6, 14) else 1)
            put(bass, tone(f, 0.22, 0.12, "saw", 0.003), 0.55)
        # accords stabs
        if pos in (0, 3, 6, 10) or (L >= 1 and pos in (12, 14)):
            x = sum(tone(f, 0.25, 0.09, "saw", 0.002) for f in chord) / 3
            put(keys, x, 0.35 + 0.08 * L)
        # lead arpège à partir du difficile
        if L >= 2 and pos % 2 == 0:
            f = chord[(pos // 2) % 3] * 2
            put(lead, tone(f, 0.15, 0.06, "square", 0.002), 0.12 + 0.05 * (L - 2))
    bass = lowpass(bass, 0.12)
    keys = lowpass(keys, 0.25)
    lead = lowpass(lead, 0.35)
    mix = drums + bass + keys + lead
    # ouverture de filtre / gain global par niveau
    t = np.arange(n) / SR
    g = np.ones(n)
    for (t0, l) in levels_at:
        g[t >= t0] = [0.78, 0.86, 0.93, 1.0][l]
    mix *= g
    for a, b in cuts:
        m = (t >= a) & (t < b)
        mix[m] = 0
        # petit roulement de caisse claire pendant la coupure
        roll_n = int((b - a) * SR)
        r = np.zeros(roll_n)
        k = 0
        while k * 0.0625 < (b - a) - 0.05:
            j = int(k * 0.0625 * SR); x = clap() * (0.15 + 0.5 * k * 0.0625 / (b - a))
            r[j:j + len(x)] += x[:roll_n - j]; k += 1
        mix[int(a * SR):int(a * SR) + roll_n] += r * 0.5
    return mix[: int(total * SR)]


def load_voice(name):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(VOICE_DIR, name + ".wav"), "-f", "f32le",
                          "-ac", "1", "-ar", str(SR), "-"], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def main():
    tl = build()
    total = tl["duration"]
    n = int(total * SR)
    qs = tl["questions"]
    lv_index = {"FACILE": 0, "MOYEN": 1, "DIFFICILE": 2, "EXTREME": 3}
    levels_at = [(q["appear"], lv_index[q["level"]]) for q in qs]
    cuts = [tuple(q["suspense"]) for q in qs if q["suspense"]]
    mus = music(total, levels_at, cuts)
    mus = mus / np.abs(mus).max()

    voice = np.zeros(n)
    for st, name in tl["voices"]:
        v = load_voice(name); i = int(st * SR); j = min(n, i + len(v)); voice[i:j] += v[:j - i]

    fx = np.zeros(n)
    bank = {"whoosh": sfx_whoosh(), "pop": sfx_pop(), "ding": sfx_ding(), "levelup": sfx_levelup(),
            "impact": sfx_impact(), "jingle": sfx_jingle(), "cut": np.zeros(10)}
    for st, kind in tl["sfx"]:
        x = bank[kind]; i = int(st * SR); j = min(n, i + len(x)); fx[i:j] += x[:j - i]
    # tic-tac : un « TOC » marqué à chaque chiffre, tic-tac entre, accélère sur le dernier chiffre
    for q in qs:
        a, b = q["cd_start"], q["cd_end"]
        step = (b - a) / 5
        low = q["level"] in ("DIFFICILE", "EXTREME")
        for dgt in range(5):
            t0 = a + dgt * step
            sub = 4 if dgt == 4 else 2
            for s_ in range(sub):
                tt = t0 + s_ * step / sub
                x = sfx_tick(high=(s_ % 2 == 0))
                g = 1.15 if s_ == 0 else 0.7
                if low: x = np.interp(np.arange(int(len(x) * 1.3)) / 1.3, np.arange(len(x)), x)
                i = int(tt * SR); j = min(n, i + len(x)); fx[i:j] += g * x[:j - i]

    # ducking de la musique sous la voix (env. -20 dB par rapport à la voix)
    from scipy.ndimage import maximum_filter1d, uniform_filter1d
    vabs = maximum_filter1d(np.abs(voice), int(0.05 * SR))
    active = uniform_filter1d((vabs > 0.02).astype(float), int(0.12 * SR))
    duck = 1 - 0.55 * np.clip(active * 1.5, 0, 1)
    mix = 0.30 * mus * duck + 1.0 * voice + 0.55 * fx
    # fondu de raccord de boucle très court (pas de fondu au noir audio)
    f = int(0.01 * SR); mix[:f] *= np.linspace(0, 1, f); mix[-f:] *= np.linspace(1, 0, f)
    peak = np.abs(mix).max(); mix = mix / peak * 0.95
    out = os.path.join(ROOT, "build", "mix.wav")
    import wave
    with wave.open(out, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
    # piste seule pour vérification
    print("mix ->", out, f"{total:.2f}s")
    # contrôle des blancs : fenêtres de 0,3 s où ni voix ni effet
    act = maximum_filter1d((np.abs(voice) + np.abs(fx)) > 0.01, int(0.3 * SR))
    gaps = np.where(~act)[0]
    print("échantillons sans voix ni effet (fenêtre 0,3 s):", len(gaps) / SR, "s")


if __name__ == "__main__":
    main()
