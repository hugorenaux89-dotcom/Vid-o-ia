"""Crée les photos de profil TikTok (1080x1080) dans le style des vidéos quiz.

Usage : python3 profil/creer_photo_profil.py
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

S = 1080
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
JAUNE = (255, 214, 0)
ICI = os.path.dirname(os.path.abspath(__file__))


def fond():
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    c = S / 2
    ang, r = np.arctan2(yy - c, xx - c), np.hypot(xx - c, yy - c)
    base = np.array([20, 10, 60], np.float32) * (1 - yy / S)[..., None] + \
        np.array([55, 8, 85], np.float32) * (yy / S)[..., None]
    halo = np.exp(-(r / 380) ** 2)[..., None] * np.array([130, 70, 255], np.float32)
    rayons = ((0.5 + 0.5 * np.cos(12 * ang + 0.2)) ** 6 * 0.6 * np.exp(-r / 900))[..., None] \
        * np.array([170, 120, 255], np.float32)
    vign = (1 - 0.5 * np.clip(r / (S * 0.7), 0, 1) ** 2)[..., None]
    return Image.fromarray(np.clip((base + halo + rayons) * vign, 0, 255).astype(np.uint8))


def emoji(e, size):
    im = Image.new("RGBA", (160, 160))
    ImageDraw.Draw(im).text((10, 10), e, font=ImageFont.truetype(EMOJI, 109), embedded_color=True)
    im = im.crop(im.getbbox())
    k = size / max(im.size)
    return im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)


def texte(d, t, cy, size, fill, stroke=10):
    f = ImageFont.truetype(BOLD, size)
    l, top, r, b = d.textbbox((0, 0), t, font=f, stroke_width=stroke)
    d.text(((S - (r - l)) / 2 - l, cy - (b - top) / 2 - top), t, font=f, fill=fill,
           stroke_width=stroke, stroke_fill=(15, 5, 40))


def lueur(img, t, cy, size):
    """Halo jaune flou derrière un texte."""
    calque = Image.new("RGBA", (S, S))
    texte(ImageDraw.Draw(calque), t, cy, size, JAUNE + (255,), stroke=24)
    calque = calque.filter(ImageFilter.GaussianBlur(28))
    img.paste(calque, (0, 0), calque)


def particules(d):
    rng = np.random.default_rng(3)
    for _ in range(40):
        x, y, rr = rng.uniform(0, S), rng.uniform(0, S), rng.uniform(2, 6)
        if math.hypot(x - S / 2, y - S / 2) > 330:
            d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(190, 170, 255))


def version_point_interrogation():
    """Logo principal : gros « ? » jaune lumineux + éclair, lisible même en tout petit."""
    img = fond()
    d = ImageDraw.Draw(img)
    particules(d)
    d.ellipse([170, 170, S - 170, S - 170], outline=JAUNE, width=14)
    lueur(img, "?", S / 2 + 10, 560)
    texte(ImageDraw.Draw(img), "?", S / 2 + 10, 560, JAUNE, stroke=16)
    e = emoji("⚡", 230)
    img.paste(e, (int(S / 2 + 150), int(S / 2 - 330)), e)
    return img


def version_cerveau():
    """Variante : cerveau + « QUIZ » en gros."""
    img = fond()
    d = ImageDraw.Draw(img)
    particules(d)
    e = emoji("🧠", 420)
    img.paste(e, (int(S / 2 - e.width / 2), 190), e)
    lueur(img, "QUIZ", 790, 210)
    texte(ImageDraw.Draw(img), "QUIZ", 790, 210, JAUNE, stroke=14)
    return img


def apercu_rond(img, taille=300):
    """Aperçu tel que TikTok l'affiche (rond, petit)."""
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).ellipse([0, 0, S, S], fill=255)
    rond = Image.new("RGB", (S, S), (255, 255, 255))
    rond.paste(img, (0, 0), m)
    return rond.resize((taille, taille), Image.LANCZOS)


if __name__ == "__main__":
    a, b = version_point_interrogation(), version_cerveau()
    a.save(os.path.join(ICI, "photo_profil.png"))
    b.save(os.path.join(ICI, "photo_profil_variante.png"))
    planche = Image.new("RGB", (1000, 400), (255, 255, 255))
    planche.paste(apercu_rond(a), (60, 50))
    planche.paste(apercu_rond(b), (380, 50))
    planche.paste(apercu_rond(a, 100), (720, 150))
    planche.paste(apercu_rond(b, 100), (850, 150))
    planche.save(os.path.join(ICI, "apercu_rond.png"))
    print("OK")
