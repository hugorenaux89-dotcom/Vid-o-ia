"""Moteur d'animation minimaliste : figurines lumineuses, blocs, caméra, texte.

Rendu image par image avec PIL + numpy, format vertical 1080x1920.
Le monde est en unités "monde" : sol à y=0, y vers le haut.
"""
import math
import os
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
SS = 2  # supersampling du calque des figurines

FONT_DIRS = ["/usr/share/fonts/truetype/jetbrains-mono", os.path.join(os.path.dirname(__file__), "fonts")]


@lru_cache(maxsize=256)
def font(size, weight="ExtraBold"):
    for d in FONT_DIRS:
        p = os.path.join(d, f"JetBrainsMono-{weight}.ttf")
        if os.path.exists(p):
            return ImageFont.truetype(p, int(size))
    return ImageFont.load_default()


# ---------------------------------------------------------------- utilitaires
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def lerp(a, b, w):
    return a + (b - a) * w


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_in_out(x):
    return smooth(x)


def seg(t, a, b):
    """Progression 0..1 de t entre a et b."""
    if b <= a:
        return 1.0 if t >= b else 0.0
    return clamp((t - a) / (b - a))


def lerp_pt(p, q, w):
    return (lerp(p[0], q[0], w), lerp(p[1], q[1], w))


def hash01(i, salt=0):
    x = math.sin(i * 12.9898 + salt * 78.233) * 43758.5453
    return x - math.floor(x)


# ---------------------------------------------------------------- figurine
TORSO, NECK, HEAD_R = 100, 12, 27
UARM, FARM = 58, 54
THIGH, SHIN = 66, 64
LIMB_W = 15
STAND_HIP = 124


class Pose:
    __slots__ = ("hip", "lean", "tilt", "hands", "feet", "facing")

    def __init__(self, hip, lean=0.0, tilt=0.0, hands=None, feet=None, facing=1):
        self.hip = hip
        self.lean = lean
        self.tilt = tilt
        self.hands = hands
        self.feet = feet
        self.facing = facing

    def shoulder(self):
        a = math.radians(self.lean) * self.facing
        d = TORSO - 8
        return (self.hip[0] + math.sin(a) * d, self.hip[1] + math.cos(a) * d)

    def blend(self, other, w):
        return Pose(
            lerp_pt(self.hip, other.hip, w),
            lerp(self.lean, other.lean, w),
            lerp(self.tilt, other.tilt, w),
            [lerp_pt(a, b, w) for a, b in zip(self.hands, other.hands)],
            [lerp_pt(a, b, w) for a, b in zip(self.feet, other.feet)],
            other.facing if w > 0.5 else self.facing,
        )


def stand_pose(x, ground=0.0, facing=1, breath=0.0, lean=0.0, tilt=0.0):
    hip = (x, ground + STAND_HIP + breath)
    p = Pose(hip, lean, tilt, None, [(x - 16 + facing * 4, ground), (x + 16 + facing * 4, ground)], facing)
    s = p.shoulder()
    p.hands = [(s[0] - 12 + facing * 4, s[1] - 104), (s[0] + 12 + facing * 4, s[1] - 104)]
    return p


def ik(root, target, a, b, bend_sign, facing):
    dx, dy = target[0] - root[0], target[1] - root[1]
    d = math.hypot(dx, dy)
    base = math.atan2(dy, dx)
    if d >= a + b - 0.5:
        ux, uy = math.cos(base), math.sin(base)
        mid = (root[0] + ux * a, root[1] + uy * a)
        end = (root[0] + ux * (a + b), root[1] + uy * (a + b))
        return mid, end
    d = max(d, abs(a - b) + 0.5)
    cosal = clamp((a * a + d * d - b * b) / (2 * a * d), -1, 1)
    al = math.acos(cosal)
    c1 = (root[0] + a * math.cos(base + al), root[1] + a * math.sin(base + al))
    c2 = (root[0] + a * math.cos(base - al), root[1] + a * math.sin(base - al))
    # bend_sign=+1 : articulation vers l'avant (genou), -1 : vers l'arrière (coude)
    k1 = c1[0] * facing * bend_sign
    k2 = c2[0] * facing * bend_sign
    mid = c1 if k1 >= k2 else c2
    return mid, target


def skeleton(p):
    a = math.radians(p.lean) * p.facing
    tdir = (math.sin(a), math.cos(a))
    neck_base = (p.hip[0] + tdir[0] * TORSO, p.hip[1] + tdir[1] * TORSO)
    ha = a + math.radians(p.tilt) * p.facing
    hdir = (math.sin(ha), math.cos(ha))
    head = (neck_base[0] + hdir[0] * (NECK + HEAD_R), neck_base[1] + hdir[1] * (NECK + HEAD_R))
    sh = p.shoulder()
    arms = [ik(sh, h, UARM, FARM, -1, p.facing) for h in p.hands]
    legs = [ik(p.hip, f, THIGH, SHIN, +1, p.facing) for f in p.feet]
    return dict(neck=neck_base, head=head, sh=sh, arms=arms, legs=legs)


# ---------------------------------------------------------------- caméra
class Camera:
    def __init__(self, cx, cy, z):
        self.cx, self.cy, self.z = cx, cy, z

    def to_screen(self, x, y, ss=1):
        return ((W / 2 + (x - self.cx) * self.z) * ss, (H / 2 - (y - self.cy) * self.z) * ss)

    def ground_y(self):
        return self.to_screen(0, 0)[1]


# ---------------------------------------------------------------- dessin
class Canvas:
    """Calque additif (fond noir) dessiné en supersampling."""

    def __init__(self, cam):
        self.cam = cam
        self.img = Image.new("RGB", (W * SS, H * SS), (0, 0, 0))
        self.d = ImageDraw.Draw(self.img)
        self.k = cam.z * SS

    def P(self, pt):
        return self.cam.to_screen(pt[0], pt[1], SS)

    def line(self, a, b, w, col):
        A, B = self.P(a), self.P(b)
        wpx = max(1, int(w * self.k))
        self.d.line([A, B], fill=col, width=wpx)
        r = wpx / 2
        for X, Y in (A, B):
            self.d.ellipse([X - r, Y - r, X + r, Y + r], fill=col)

    def circle(self, c, r, col):
        X, Y = self.P(c)
        R = r * self.k
        self.d.ellipse([X - R, Y - R, X + R, Y + R], fill=col)

    def rect(self, x0, y0, x1, y1, col, radius=3):
        A = self.P((x0, y1))
        B = self.P((x1, y0))
        self.d.rounded_rectangle([A[0], A[1], B[0], B[1]], radius=max(0, radius * self.k), fill=col)

    def rect_outline(self, x0, y0, x1, y1, col, width=2):
        A = self.P((x0, y1))
        B = self.P((x1, y0))
        self.d.rounded_rectangle([A[0], A[1], B[0], B[1]], radius=4 * self.k, outline=col, width=max(1, int(width * self.k)))

    def polygon(self, pts, col):
        self.d.polygon([self.P(p) for p in pts], fill=col)

    def text_world(self, x, y, s, size, col, spacing=0.18):
        f = font(max(6, size * self.k), "Bold")
        X, Y = self.P((x, y))
        tracking = size * self.k * spacing
        widths = [f.getlength(ch) for ch in s]
        total = sum(widths) + tracking * (len(s) - 1)
        cx = X - total / 2
        for ch, wd in zip(s, widths):
            self.d.text((cx, Y), ch, font=f, fill=col, anchor="lm")
            cx += wd + tracking

    def figure(self, p, front=(255, 255, 255), back=(150, 150, 150)):
        sk = skeleton(p)
        bk = back
        # membres arrière
        (e, h) = sk["arms"][0]
        self.line(sk["sh"], e, LIMB_W, bk)
        self.line(e, h, LIMB_W, bk)
        (k, f) = sk["legs"][0]
        self.line(p.hip, k, LIMB_W + 1, bk)
        self.line(k, f, LIMB_W + 1, bk)
        # corps
        self.line(p.hip, sk["neck"], LIMB_W + 3, front)
        self.line(sk["neck"], sk["head"], LIMB_W - 2, front)
        self.circle(sk["head"], HEAD_R, front)
        # membres avant
        (k, f) = sk["legs"][1]
        self.line(p.hip, k, LIMB_W + 1, front)
        self.line(k, f, LIMB_W + 1, front)
        (e, h) = sk["arms"][1]
        self.line(sk["sh"], e, LIMB_W, front)
        self.line(e, h, LIMB_W, front)
        return sk

    def flame(self, head, size, t, seed=0):
        if size <= 0.02:
            return
        bx, by = head[0], head[1] + HEAD_R - 4
        layers = [((255, 60, 25), 1.0), ((255, 130, 30), 0.72), ((255, 215, 120), 0.45), ((255, 250, 225), 0.22)]
        for col, sc in layers:
            hgt = 78 * size * sc * (1 + 0.12 * math.sin(t * 17 + seed) + 0.08 * math.sin(t * 29 + 1.3))
            wid = 22 * size * (0.35 + 0.65 * sc) * (1 + 0.1 * math.sin(t * 13 + 2))
            sway = 10 * size * math.sin(t * 7.3 + seed) + 5 * size * math.sin(t * 15.1)
            n = 16
            left, right = [], []
            for i in range(n + 1):
                v = i / n
                hw = wid * math.sin(math.pi * v**0.6)
                yy = by - 6 * size + v * hgt
                xo = sway * v * v
                left.append((bx - hw + xo, yy))
                right.append((bx + hw + xo, yy))
            self.polygon(left + right[::-1], col)


def text_layer_lines(img, lines, y_center, size, col=(255, 255, 255), line_h=1.3, weight="ExtraBold", reveal=None, alpha=1.0):
    """Texte centré en espace écran sur une image RGB 1x (dessin additif-ish)."""
    d = ImageDraw.Draw(img)
    f = font(size, weight)
    total_chars = sum(len(l) for l in lines)
    shown = total_chars if reveal is None else int(reveal)
    lh = size * line_h
    y0 = y_center - lh * (len(lines) - 1) / 2
    c = tuple(int(v * alpha) for v in col)
    count = 0
    for i, l in enumerate(lines):
        vis = l[: max(0, min(len(l), shown - count))]
        count += len(l)
        if not vis:
            continue
        wfull = f.getlength(l)
        x = W / 2 - wfull / 2
        d.text((x, y0 + i * lh), vis, font=f, fill=c, anchor="lm")


def wrap(text, maxc):
    words = text.split(" ")
    lines, cur = [], ""
    for w_ in words:
        if len(cur) + len(w_) + (1 if cur else 0) <= maxc:
            cur = (cur + " " + w_) if cur else w_
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- fond
def make_background(seed=3):
    rng = np.random.default_rng(seed)
    y = np.linspace(0, 1, H)[:, None]
    x = np.linspace(0, 1, W)[None, :]
    base = 0.035 + 0.06 * np.exp(-((y - 0.25) ** 2) / 0.08)
    beams = np.zeros((H, W))
    n = 9
    for i in range(n):
        cx = (i + 0.5) / n + rng.uniform(-0.03, 0.03)
        wdt = rng.uniform(0.012, 0.03)
        inten = rng.uniform(0.05, 0.13)
        fall = np.clip(1 - y / rng.uniform(0.55, 0.8), 0, 1) ** 1.6
        beams += inten * np.exp(-((x - cx) ** 2) / (2 * wdt**2)) * fall
    vign = 1 - 0.55 * (((x - 0.5) / 0.75) ** 2 + ((y - 0.5) / 0.85) ** 2)
    bg = (base + beams) * np.clip(vign, 0.2, 1)
    return np.repeat(bg[:, :, None], 3, axis=2).astype(np.float32)


def composite(bg, fg_img, cam, extra_glow=None, brightness=1.0, bg_boost=0.0, reflect=True, grain_seed=0, text_img=None):
    fg_small = fg_img.resize((W, H), Image.LANCZOS)
    if text_img is not None:
        fg_small = Image.fromarray(np.maximum(np.asarray(fg_small), np.asarray(text_img)))
    fg = np.asarray(fg_small).astype(np.float32) / 255.0
    q = fg_small.resize((W // 4, H // 4), Image.BILINEAR)
    g1 = q.filter(ImageFilter.GaussianBlur(3)).resize((W, H), Image.BILINEAR)
    g2 = q.filter(ImageFilter.GaussianBlur(14)).resize((W, H), Image.BILINEAR)
    glow = 0.55 * np.asarray(g1).astype(np.float32) / 255.0 + 0.9 * np.asarray(g2).astype(np.float32) / 255.0
    if extra_glow is not None:
        glow += extra_glow
    out = bg * (1 + bg_boost) + glow

    gy = int(round(cam.ground_y()))
    # halo du sol
    yy = np.arange(H, dtype=np.float32)[:, None]
    horizon = 0.10 * np.exp(-((yy - gy) ** 2) / (2 * 30.0**2)) + 0.03 * np.exp(-((yy - gy) ** 2) / (2 * 220.0**2))
    out += horizon[:, :, None]
    if reflect and 0 < gy < H:
        hh = min(gy, H - gy)
        if hh > 4:
            src = fg[gy - hh : gy][::-1]
            fade = np.exp(-np.arange(hh, dtype=np.float32) / 140.0)[:, None, None] * 0.28
            out[gy : gy + hh] += src * fade
            # sol plus sombre sous la ligne
            out[gy:] *= 0.92
    out = np.maximum(out, fg)
    out *= brightness
    rng = np.random.default_rng(grain_seed)
    out += rng.normal(0, 0.012, (H, W, 1)).astype(np.float32)
    out = np.clip(out, 0, 1) ** (1 / 1.05)
    return Image.fromarray((out * 255).astype(np.uint8))
