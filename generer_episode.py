"""Génère une vidéo TikTok quiz (1080x1920, 30 i/s) à partir d'un fichier JSON d'épisode.

Usage : python3 generer_episode.py episodes/episode1.json sortie/episode1.mp4
"""
import json
import math
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS, SR = 1080, 1920, 30, 44100
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# Couleurs
BG_TOP, BG_BOT = (12, 16, 48), (40, 10, 70)
JAUNE, BLANC, VERT, GRIS = (255, 214, 0), (255, 255, 255), (34, 197, 94), (70, 74, 100)
CASE = (30, 36, 90)

_fonts = {}


def font(size):
    if size not in _fonts:
        _fonts[size] = ImageFont.truetype(BOLD, size)
    return _fonts[size]


def fond():
    grad = np.linspace(0, 1, H)[:, None]
    top, bot = np.array(BG_TOP), np.array(BG_BOT)
    col = (top * (1 - grad) + bot * grad).astype(np.uint8)
    arr = np.repeat(col[:, None, :], W, axis=1)
    return Image.fromarray(arr.reshape(H, W, 3))


FOND = None


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


def texte_centre(d, text, y, size, color, maxw=900, interligne=1.2):
    lines = wrap(text, size, maxw)
    for i, l in enumerate(lines):
        lw = font(size).getlength(l)
        d.text(((W - lw) / 2, y + i * size * interligne), l, font=font(size), fill=color,
               stroke_width=max(2, size // 18), stroke_fill=(0, 0, 0))
    return y + len(lines) * size * interligne


def entete(d, titre):
    texte_centre(d, titre, 170, 38, JAUNE)


# ---------- écrans ----------

def ecran_texte(ep, lignes, t, duree):
    img = FOND.copy()
    d = ImageDraw.Draw(img)
    entete(d, ep["titre"])
    pulse = 1 + 0.04 * math.sin(t * 2 * math.pi * 1.5)
    total = sum(s * 1.25 for _, s, _ in lignes)
    y = (H - total) / 2 - 150
    for text, size, color in lignes:
        s = int(size * pulse); color = tuple(color)
        y = texte_centre(d, text, y, s, color) + 10
    return img


def ecran_question(ep, i, q, t, compte):
    """t = temps écoulé dans le segment de la question."""
    img = FOND.copy()
    d = ImageDraw.Draw(img)
    entete(d, ep["titre"])
    n = len(ep["questions"])

    # progression
    texte_centre(d, f"QUESTION {i + 1}/{n}", 240, 44, BLANC)
    seg_w, gap, x0 = 76, 10, (W - (n * 76 + (n - 1) * 10)) / 2
    for k in range(n):
        c = JAUNE if k <= i else GRIS
        d.rounded_rectangle([x0 + k * (seg_w + gap), 310, x0 + k * (seg_w + gap) + seg_w, 324], 6, fill=c)

    apparition = min(1, t / 0.35)
    revele = t >= 1 + compte

    # question
    texte_centre(d, q["question"], 380, 64, BLANC, maxw=920)

    # compte à rebours
    cx, cy, r = W / 2, 690, 80
    if not revele:
        restant = max(0, 1 + compte - t)
        frac = min(1, restant / compte)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=CASE, outline=GRIS, width=12)
        if frac > 0:
            d.arc([cx - r, cy - r, cx + r, cy + r], -90, -90 + 360 * frac, fill=JAUNE, width=12)
        num = str(min(compte, math.ceil(restant))) if t >= 1 else str(compte)
        nw = font(80).getlength(num)
        d.text((cx - nw / 2, cy - 48), num, font=font(80), fill=JAUNE)
    else:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=VERT)
        d.text((cx - font(90).getlength("✓") / 2, cy - 55), "✓", font=font(90), fill=BLANC)

    # réponses
    lettres = "ABCD"
    y0, h, g = 810, 118, 24
    for k, choix in enumerate(q["choix"]):
        dx = (1 - apparition) * (W if k % 2 else -W) * (1 + k * 0.2)
        y = y0 + k * (h + g)
        bonne = k == q["reponse"]
        fill, txt = CASE, BLANC
        if revele:
            fill, txt = (VERT, BLANC) if bonne else ((40, 42, 60), (130, 130, 150))
        d.rounded_rectangle([90 + dx, y, 990 + dx, y + h], 28, fill=fill,
                            outline=JAUNE if not revele else fill, width=4)
        d.ellipse([110 + dx, y + 19, 190 + dx, y + 99], fill=JAUNE if not revele or bonne else GRIS)
        lw = font(46).getlength(lettres[k])
        d.text((150 + dx - lw / 2, y + 32), lettres[k], font=font(46), fill=(20, 20, 40))
        size = 52 if font(52).getlength(choix) < 740 else 42
        d.text((215 + dx, y + (h - size) / 2 - 6), choix, font=font(size), fill=txt)

    if revele and q.get("bonus"):
        texte_centre(d, q["bonus"], 1395, 40, JAUNE, maxw=880)
    return img


# ---------- timeline ----------

def construire(ep):
    segs = []  # (duree, fonction(t), evenements audio)
    segs.append((3.0, lambda t: ecran_texte(ep, ep["hook"], t, 3), [("whoosh", 0)]))
    segs.append((3.0, lambda t: ecran_texte(ep, ep["regles"], t, 3), [("whoosh", 0)]))
    for i, q in enumerate(ep["questions"]):
        compte = q.get("compte", 4)
        dur = 1 + compte + 2.2
        ev = [("whoosh", 0)] + [("tick", 1 + s) for s in range(compte)] + [("ding", 1 + compte)]
        segs.append((dur, (lambda i, q, c: lambda t: ecran_question(ep, i, q, t, c))(i, q, compte), ev))
        rel = ep.get("relances", {}).get(str(i + 1))
        if rel:
            segs.append((3.0, (lambda r: lambda t: ecran_texte(ep, r, t, 3))(rel), [("suspense", 0)]))
    segs.append((7.0, lambda t: ecran_texte(ep, ep["fin"], t, 7), [("ding", 0)]))
    return segs


# ---------- audio ----------

def synth(segs):
    total = sum(s[0] for s in segs)
    n = int(total * SR)
    out = np.zeros(n)
    tt = np.arange(n) / SR

    # musique de fond : basse pulsée + nappe, 120 BPM
    notes = [55, 55, 65.4, 49]  # La, La, Do, Sol (graves)
    beat = 0.5
    for b in range(int(total / beat)):
        f = notes[(b // 8) % 4]
        s0 = int(b * beat * SR)
        L = int(0.45 * SR)
        x = np.arange(min(L, n - s0)) / SR
        env = np.exp(-x * 7)
        out[s0:s0 + len(x)] += 0.18 * env * np.sin(2 * np.pi * f * 2 * x)
        if b % 2 == 1:  # charleston
            hl = int(0.05 * SR)
            hx = np.arange(min(hl, n - s0)) / SR
            out[s0:s0 + len(hx)] += 0.03 * np.random.randn(len(hx)) * np.exp(-hx * 80)
    out += 0.025 * np.sin(2 * np.pi * 220 * tt) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.25 * tt))

    def add(t0, sig):
        s0 = int(t0 * SR)
        e = min(n, s0 + len(sig))
        if s0 < n:
            out[s0:e] += sig[:e - s0]

    def tick():
        x = np.arange(int(0.08 * SR)) / SR
        return 0.35 * np.sin(2 * np.pi * 1500 * x) * np.exp(-x * 60)

    def ding():
        x = np.arange(int(0.9 * SR)) / SR
        return 0.3 * (np.sin(2 * np.pi * 880 * x) + 0.6 * np.sin(2 * np.pi * 1320 * x)) * np.exp(-x * 4)

    def whoosh():
        x = np.arange(int(0.35 * SR)) / SR
        bruit = np.convolve(np.random.randn(len(x)), np.ones(30) / 30, "same")
        return 0.6 * bruit * np.sin(np.pi * x / x[-1])

    def suspense():
        x = np.arange(int(2.5 * SR)) / SR
        f = 100 + 60 * x
        return 0.15 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(1, x * 2)

    sons = {"tick": tick, "ding": ding, "whoosh": whoosh, "suspense": suspense}
    t0 = 0
    for dur, _, evs in segs:
        for nom, dt in evs:
            add(t0 + dt, sons[nom]())
        t0 += dur
    fade = int(1.5 * SR)
    out[-fade:] *= np.linspace(1, 0, fade)
    out = out / max(1e-9, np.abs(out).max()) * 0.85
    return (out * 32767).astype(np.int16), total


def main(src, dst):
    global FOND
    FOND = fond()
    ep = json.load(open(src, encoding="utf-8"))
    segs = construire(ep)
    audio, total = synth(segs)
    wav = dst.rsplit(".", 1)[0] + ".wav"
    with wave.open(wav, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(audio.tobytes())

    ff = subprocess.Popen([
        "ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav,
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", dst,
    ], stdin=subprocess.PIPE)
    for dur, render, _ in segs:
        for f in range(int(round(dur * FPS))):
            ff.stdin.write(render(f / FPS).tobytes())
    ff.stdin.close()
    ff.wait()
    print(f"OK : {dst} ({total:.1f} s)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
