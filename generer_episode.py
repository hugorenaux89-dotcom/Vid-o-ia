"""Génère une vidéo TikTok quiz (1080x1920, 30 i/s) avec voix off, à partir d'un fichier JSON d'épisode.

Usage : python3 generer_episode.py episodes/episode1.json sortie/episode1.mp4

Produit deux fichiers :
  - sortie/episode1.mp4               : voix off + musique + effets sonores
  - sortie/episode1_sans_musique.mp4  : voix off + effets (pour ajouter un son tendance dans TikTok)

Voix : voix neuronale française native Microsoft « Henri » (paquet `edge-tts`, gratuit).
Fond : fond animé commun à tous les épisodes (fonction `fond`).
"""
import asyncio
import hashlib
import json
import math
import os
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS, SR = 1080, 1920, 30, 44100
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
VOIX = "fr-FR-HenriNeural"  # voix française native (pas « Multilingual », qui a un accent anglais)
# Traitement studio de la voix : coupe les graves parasites, présence, compression, léger écho de pièce
FILTRE_VOIX = ("highpass=f=90,equalizer=f=200:t=q:w=1:g=2,equalizer=f=3500:t=q:w=1.5:g=3,"
               "acompressor=threshold=-20dB:ratio=3.5:attack=5:release=120:makeup=3,"
               "aecho=0.8:0.5:35:0.12")
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache_voix")

BG_TOP, BG_BOT = (12, 16, 48), (40, 10, 70)
JAUNE, BLANC, VERT, GRIS = (255, 214, 0), (255, 255, 255), (34, 197, 94), (70, 74, 100)
CASE = (30, 36, 90)

_fonts, _emojis = {}, {}


def font(size):
    if size not in _fonts:
        _fonts[size] = ImageFont.truetype(BOLD, size)
    return _fonts[size]


def emoji_img(e, size):
    key = (e, size)
    if key not in _emojis:
        f = ImageFont.truetype(EMOJI, 109)
        im = Image.new("RGBA", (160, 160))
        ImageDraw.Draw(im).text((10, 10), e, font=f, embedded_color=True)
        im = im.crop(im.getbbox())
        r = size / max(im.size)
        _emojis[key] = im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)
    return _emojis[key]


def coller_emoji(img, e, cx, cy, size):
    if size < 4:
        return
    em = emoji_img(e, int(size))
    img.paste(em, (int(cx - em.width / 2), int(cy - em.height / 2)), em)


# ---------- fond animé (identique pour tous les épisodes) ----------
# Rayons lumineux façon plateau de jeu télé qui tournent lentement, halo central,
# particules qui montent, vignette, et une carte translucide derrière le contenu.

_FW, _FH = W // 2, H // 2  # calcul en demi-résolution puis agrandi (dégradés doux)
_yy, _xx = np.mgrid[0:_FH, 0:_FW].astype(np.float32)
_CX, _CY = _FW / 2, 470 / 2
_ANG = np.arctan2(_yy - _CY, _xx - _CX)
_R = np.hypot(_xx - _CX, (_yy - _CY) * 0.9)
_GRAD = (_yy / _FH)[..., None]
_BASE = (np.array([14, 8, 52], np.float32) * (1 - _GRAD) + np.array([48, 6, 72], np.float32) * _GRAD)
_HALO = np.exp(-(_R / 260) ** 2)[..., None] * np.array([110, 60, 230], np.float32)
_RAYON_ATT = (0.55 * np.exp(-_R / 700))[..., None]
_VIGNETTE = (1 - 0.55 * np.clip(np.hypot((_xx - _FW / 2) / _FW, (_yy - _FH / 2) / _FH) * 1.6, 0, 1) ** 2)[..., None]


def _carte_masque():
    m = Image.new("L", (_FW, _FH), 0)
    ImageDraw.Draw(m).rounded_rectangle([25, 105, _FW - 25, 760], 30, fill=150)
    return (np.asarray(m, np.float32) / 255)[..., None]


_CARTE = _carte_masque()
_rng = np.random.default_rng(7)
_PARTICULES = [(_rng.uniform(0, W), _rng.uniform(0, H), _rng.uniform(25, 70), _rng.uniform(2, 6),
                _rng.uniform(0, 6.28)) for _ in range(45)]


def fond(t):
    """Fond animé au temps t (secondes, temps global de la vidéo)."""
    rayons = 0.5 + 0.5 * np.cos(12 * _ANG + t * 0.35)
    rayons = (rayons ** 6)[..., None] * _RAYON_ATT
    arr = _BASE + _HALO * (0.85 + 0.15 * math.sin(t * 2.2)) + rayons * np.array([170, 120, 255], np.float32)
    arr *= _VIGNETTE
    arr = arr * (1 - _CARTE) + np.array([10, 8, 30], np.float32) * _CARTE
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
    d = ImageDraw.Draw(img)
    for x, y0, v, r, ph in _PARTICULES:
        y = (y0 - v * t) % H
        xx = x + 15 * math.sin(t * 0.8 + ph)
        b = 0.5 + 0.5 * math.sin(t * 2 + ph)
        c = (int(120 + 90 * b), int(100 + 70 * b), 255)
        d.ellipse([xx - r, y - r, xx + r, y + r], fill=c)
    d.rounded_rectangle([50, 210, W - 50, 1520], 60, outline=(120, 90, 255), width=3)
    return img


T = 0.0  # temps global courant


def wrap(text, size, maxw):
    f = font(size)
    lines, cur = [], ""
    for mot in text.split():
        test = (cur + " " + mot).strip()
        if f.getlength(test) <= maxw:
            cur = test
        else:
            lines.append(cur)
            cur = mot
    if cur:
        lines.append(cur)
    return lines


def texte_centre(d, text, y, size, color, maxw=900, interligne=1.2, dx=0):
    lines = wrap(text, size, maxw)
    for i, l in enumerate(lines):
        lw = font(size).getlength(l)
        d.text(((W - lw) / 2 + dx, y + i * size * interligne), l, font=font(size), fill=tuple(color),
               stroke_width=max(2, size // 18), stroke_fill=(0, 0, 0))
    return y + len(lines) * size * interligne


def pop(t, duree=0.3):
    """Effet « pop » : 0 -> 1.15 -> 1."""
    if t >= duree:
        return 1.0
    x = t / duree
    return 1.15 * math.sin(x * math.pi / 2) if x < 0.8 else 1.15 - 0.15 * (x - 0.8) / 0.2


# ---------- voix ----------

# Émotions : réglages (débit, hauteur, volume) appliqués phrase par phrase
TONS = {
    "neutre":     ("+15%", "+0Hz", "+0%"),
    "curieux":    ("+12%", "+3Hz", "+0%"),
    "intrigant":  ("+5%", "-2Hz", "+0%"),
    "mysterieux": ("-2%", "-5Hz", "-5%"),
    "suspense":   ("-8%", "-7Hz", "-8%"),
    "energique":  ("+22%", "+6Hz", "+10%"),
    "malicieux":  ("+16%", "+5Hz", "+5%"),
    "emerveille": ("+8%", "+7Hz", "+5%"),
    "triomphant": ("+16%", "+9Hz", "+15%"),
    "chaleureux": ("+10%", "+2Hz", "+0%"),
}


def voix(texte, ton="neutre"):
    """Renvoie la voix off en numpy float (mono, 44,1 kHz), avec cache."""
    os.makedirs(CACHE, exist_ok=True)
    debit, hauteur, volume = TONS.get(ton, TONS["neutre"])
    h = hashlib.md5(f"{VOIX}|{debit}|{hauteur}|{volume}|{texte}".encode()).hexdigest()
    mp3 = os.path.join(CACHE, h + ".mp3")
    if not os.path.exists(mp3):
        import certifi
        certifi.where = lambda: os.environ.get("SSL_CERT_FILE", "/root/.ccr/ca-bundle.crt") \
            if os.path.exists("/root/.ccr/ca-bundle.crt") else certifi.__file__.replace("__init__.py", "cacert.pem")
        import edge_tts
        asyncio.run(edge_tts.Communicate(texte, VOIX, rate=debit, pitch=hauteur, volume=volume).save(mp3))
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", mp3, "-af", FILTRE_VOIX, "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32767


# ---------- écrans ----------

def ecran_texte(ep, ecran, t, secousse=False):
    img = fond(T)
    d = ImageDraw.Draw(img)
    texte_centre(d, ep["titre"], 170, 38, JAUNE)
    dx = 0
    if secousse and t < 0.6:
        dx = 18 * math.sin(t * 60) * (1 - t / 0.6)
    zoom = 1 + 0.3 * max(0, 1 - t / 0.35) if secousse else 1
    pulse = (1 + 0.03 * math.sin(t * 2 * math.pi * 1.5)) * zoom
    y = 330
    if ecran.get("emoji"):
        coller_emoji(img, ecran["emoji"], W / 2 + dx, 470, 250 * pop(t))
        y = 640
    for text, size, color in ecran["lignes"]:
        y = texte_centre(d, text, y, int(size * pulse), color, dx=dx) + 12
    return img


def ecran_question(ep, i, q, t, A, C):
    img = fond(T)
    d = ImageDraw.Draw(img)
    texte_centre(d, ep["titre"], 170, 38, JAUNE)
    n = len(ep["questions"])
    texte_centre(d, f"QUESTION {i + 1}/{n}", 235, 44, BLANC)
    seg_w, gap = 76, 10
    x0 = (W - (n * seg_w + (n - 1) * gap)) / 2
    for k in range(n):
        d.rounded_rectangle([x0 + k * (seg_w + gap), 300, x0 + k * (seg_w + gap) + seg_w, 314], 6,
                            fill=JAUNE if k <= i else GRIS)

    revele = t >= A + C
    apparition = min(1, t / 0.35)

    # emoji (gauche) + chrono (droite)
    coller_emoji(img, q["emoji"], 330, 455, 190 * pop(t))
    cx, cy, r = 750, 455, 88
    if not revele:
        restant = min(C, A + C - t)
        frac = restant / C
        urgent = restant < 1.5 and t >= A
        couleur = (239, 68, 68) if urgent else JAUNE
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=CASE, outline=GRIS, width=12)
        d.arc([cx - r, cy - r, cx + r, cy + r], -90, -90 + 360 * frac, fill=couleur, width=12)
        num = str(max(1, math.ceil(restant)))
        s = 84 if not urgent else int(84 * (1 + 0.12 * abs(math.sin(t * math.pi * 2))))
        nw = font(s).getlength(num)
        d.text((cx - nw / 2, cy - s * 0.6), num, font=font(s), fill=couleur)
    else:
        sc = pop(t - A - C)
        rr = r * sc
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=VERT)
        if sc > 0.5:
            fs = int(90 * sc)
            d.text((cx - font(fs).getlength("✓") / 2, cy - fs * 0.62), "✓", font=font(fs), fill=BLANC)

    taille = 62
    while len(wrap(q["question"], taille, 940)) > 3 and taille > 44:
        taille -= 2  # question longue : on réduit pour tenir en 3 lignes
    texte_centre(d, q["question"], 590, taille, BLANC, maxw=940)

    lettres = "ABCD"
    y0, h, g = 840, 112, 20
    for k, choix in enumerate(q["choix"]):
        dx = (1 - apparition) * (W if k % 2 else -W) * (1 + k * 0.2)
        y = y0 + k * (h + g)
        bonne = k == q["reponse"]
        fill, txt = CASE, BLANC
        if revele:
            fill, txt = (VERT, BLANC) if bonne else ((40, 42, 60), (130, 130, 150))
        grow = 10 * pop(t - A - C) if revele and bonne else 0
        d.rounded_rectangle([90 + dx - grow, y - grow / 2, 990 + dx + grow, y + h + grow / 2], 28, fill=fill,
                            outline=JAUNE if not revele else fill, width=4)
        d.ellipse([110 + dx, y + 16, 190 + dx, y + 96], fill=JAUNE if not revele or bonne else GRIS)
        lw = font(46).getlength(lettres[k])
        d.text((150 + dx - lw / 2, y + 29), lettres[k], font=font(46), fill=(20, 20, 40))
        size = 50 if font(50).getlength(choix) < 740 else 40
        d.text((215 + dx, y + (h - size) / 2 - 6), choix, font=font(size), fill=txt)

    if revele and q.get("bonus"):
        texte_centre(d, q["bonus"], 1375, 46, JAUNE, maxw=900)
    elif not revele and i == 0:
        texte_centre(d, "Mets ta lettre en commentaire !", 1385, 40, (200, 200, 220))
    return img


# ---------- timeline ----------

def construire(ep):
    """Liste de segments : (durée, rendu(t), [(son, instant)], [(voix, instant)])."""
    segs = []

    def ecran(e, secousse=False, son="whoosh"):
        v = voix(e["voix"], e.get("ton", "neutre"))
        dur = max(e.get("min", 2.0), len(v) / SR + 0.45)
        segs.append((dur, lambda t: ecran_texte(ep, e, t, secousse), [(son, 0)], [(v, 0.1)]))

    ecran(ep["hook"], secousse=True, son="boom")
    ecran(ep["regles"])
    for i, q in enumerate(ep["questions"]):
        C = q.get("compte", 3)
        vq = voix(q.get("voix", q["question"]), q.get("ton_question", "curieux"))
        vr = voix(q["voix_reponse"], q.get("ton_reponse", "triomphant"))
        A = max(1.5, len(vq) / SR + 0.25)
        R = max(2.8, len(vr) / SR + 0.5)
        ev = [("whoosh", 0)] + [("tick", A + s) for s in range(C)] + [("ding", A + C)]
        rendu = (lambda i, q, A, C: lambda t: ecran_question(ep, i, q, t, A, C))(i, q, A, C)
        segs.append((A + C + R, rendu, ev, [(vq, 0.12), (vr, A + C + 0.15)]))
        rel = ep.get("relances", {}).get(str(i + 1))
        if rel:
            ecran(rel, son="suspense")
    ecran(ep["fin"], son="ding")
    return segs


# ---------- audio ----------

def mixer(segs):
    total = sum(s[0] for s in segs)
    n = int(total * SR) + SR
    musique, effets, parole = np.zeros(n), np.zeros(n), np.zeros(n)
    tt = np.arange(n) / SR

    notes = [55, 55, 65.4, 49]
    for b in range(int(total / 0.5) + 1):
        f, s0 = notes[(b // 8) % 4], int(b * 0.5 * SR)
        x = np.arange(min(int(0.45 * SR), n - s0)) / SR
        musique[s0:s0 + len(x)] += 0.18 * np.exp(-x * 7) * np.sin(2 * np.pi * f * 2 * x)
        if b % 2:
            hx = np.arange(min(int(0.05 * SR), n - s0)) / SR
            musique[s0:s0 + len(hx)] += 0.03 * np.random.randn(len(hx)) * np.exp(-hx * 80)
    musique += 0.025 * np.sin(2 * np.pi * 220 * tt) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.25 * tt))

    def add(buf, t0, sig):
        s0 = int(t0 * SR)
        e = min(n, s0 + len(sig))
        if s0 < n:
            buf[s0:e] += sig[:e - s0]

    def x_(d):
        return np.arange(int(d * SR)) / SR

    sons = {
        "tick": lambda: 0.35 * np.sin(2 * np.pi * 1500 * x_(0.08)) * np.exp(-x_(0.08) * 60),
        "ding": lambda: 0.3 * (np.sin(2 * np.pi * 880 * x_(0.9)) + 0.6 * np.sin(2 * np.pi * 1320 * x_(0.9)))
        * np.exp(-x_(0.9) * 4),
        "whoosh": lambda: 0.5 * np.convolve(np.random.randn(len(x_(0.35))), np.ones(30) / 30, "same")
        * np.sin(np.pi * x_(0.35) / 0.35),
        "suspense": lambda: 0.15 * np.sin(2 * np.pi * np.cumsum(100 + 60 * x_(2.5)) / SR) * np.minimum(1, x_(2.5) * 2),
        "boom": lambda: 0.7 * np.sin(2 * np.pi * (60 + 80 * np.exp(-x_(0.6) * 12)) * x_(0.6)) * np.exp(-x_(0.6) * 5),
    }
    t0 = 0
    for dur, _, evs, vxs in segs:
        for nom, dt in evs:
            add(effets, t0 + dt, sons[nom]())
        for v, dt in vxs:
            add(parole, t0 + dt, v)
        t0 += dur

    # baisse la musique quand la voix parle
    env = np.convolve(np.abs(parole), np.ones(SR // 10) / (SR // 10), "same")
    duck = np.where(env > 0.01, 0.35, 1.0)
    duck = np.convolve(duck, np.ones(SR // 8) / (SR // 8), "same")

    def finir(sig):
        sig = sig[:int(total * SR)]
        fade = int(1.2 * SR)
        sig[-fade:] *= np.linspace(1, 0, fade)
        return (sig / max(1e-9, np.abs(sig).max()) * 0.9 * 32767).astype(np.int16)

    avec = finir(1.4 * parole + 0.8 * effets + 0.9 * musique * duck)
    sans = finir(1.4 * parole + 0.8 * effets)
    return avec, sans, total


def ecrire_wav(chemin, audio):
    with wave.open(chemin, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(audio.tobytes())


def main(src, dst):
    global T
    ep = json.load(open(src, encoding="utf-8"))
    segs = construire(ep)
    avec, sans, total = mixer(segs)
    base = dst.rsplit(".", 1)[0]
    ecrire_wav(base + "_a.wav", avec)
    ecrire_wav(base + "_b.wav", sans)

    ff = subprocess.Popen([
        "ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", base + "_a.wav",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", dst,
    ], stdin=subprocess.PIPE)
    t_global = 0.0
    for dur, rendu, _, _ in segs:
        for f in range(int(round(dur * FPS))):
            T = t_global + f / FPS
            ff.stdin.write(rendu(f / FPS).tobytes())
        t_global += int(round(dur * FPS)) / FPS
    ff.stdin.close()
    ff.wait()
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", dst, "-i", base + "_b.wav", "-map", "0:v",
                    "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
                    "-movflags", "+faststart", base + "_sans_musique.mp4"], check=True)
    os.remove(base + "_a.wav")
    os.remove(base + "_b.wav")
    print(f"OK : {dst} et {base}_sans_musique.mp4 ({total:.1f} s)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
