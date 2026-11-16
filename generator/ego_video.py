#!/usr/bin/env python3
"""
EGO vs MOTIVATION / DISCIPLINE / TALENT
Generateur de video motivation style "stickman" (format TikTok/Reels 1080x1920).

La video est rendue a vitesse NORMALE (x1) : l'enregistrement d'origine etait en x2,
donc chaque scene dure ici environ le double.

Usage :
    python3 generator/ego_video.py                      # -> output/ego_vs_discipline.mp4
    python3 generator/ego_video.py --music musique.mp3  # avec une musique
    python3 generator/ego_video.py --speed 2            # version acceleree x2
    python3 generator/ego_video.py --preview            # planche de captures (png)

Dependances : pycairo, numpy, ffmpeg.
"""
import argparse
import math
import os
import random
import subprocess
import sys

import cairo
import numpy as np

W, H, FPS = 1080, 1920, 30
MONO = "JetBrains Mono"
SERIF = "Liberation Serif"

BG = (0.07, 0.07, 0.075)
OUT = (0.06, 0.06, 0.065)
GREY = (0.62, 0.62, 0.63)
WHITE = (0.96, 0.96, 0.96)
RED = (0.93, 0.29, 0.29)
DARK = (0.17, 0.17, 0.18)


# ----------------------------------------------------------------------------- utils
def lerp(a, b, t):
    return a + (b - a) * t


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def ease_out(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_in(t):
    t = clamp(t)
    return t ** 3


def back_out(t):
    t = clamp(t)
    c = 1.9
    return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2


def mix(c1, c2, t):
    return tuple(lerp(a, b, t) for a, b in zip(c1, c2))


def d(a):
    r = math.radians(a)
    return math.sin(r), math.cos(r)


def rgb(ctx, c, a=1.0):
    ctx.set_source_rgba(c[0], c[1], c[2], a)


# ----------------------------------------------------------------------------- stickman
KEYS = ["t", "la1", "la2", "ra1", "ra2", "ll1", "ll2", "rl1", "rl2"]


def P(t=180, la1=-15, la2=-10, ra1=15, ra2=10, ll1=-10, ll2=-6, rl1=10, rl2=6):
    return dict(t=t, la1=la1, la2=la2, ra1=ra1, ra2=ra2, ll1=ll1, ll2=ll2, rl1=rl1, rl2=rl2)


def pmix(p, q, k):
    return {key: lerp(p[key], q[key], k) for key in KEYS}


# Les angles sont absolus (0 = vers le bas, 90 = vers la droite, 180 = vers le haut).
STAND = P()
SAD = P(la1=-5, la2=-2, ra1=5, ra2=2, ll1=-6, ll2=-4, rl1=6, rl2=4)
CHEER = P(la1=-140, la2=-165, ra1=140, ra2=165, ll1=-14, ll2=-8, rl1=14, rl2=8)
CHEER2 = P(la1=-125, la2=-150, ra1=150, ra2=175, ll1=-12, ll2=-8, rl1=16, rl2=10)
POINT = P(t=174, la1=-30, la2=50, ra1=98, ra2=94, ll1=-12, ll2=-8, rl1=12, rl2=8)
LAUGH = P(t=168, la1=-25, la2=60, ra1=25, ra2=-60, ll1=-12, ll2=-8, rl1=12, rl2=8)
HANG = P(la1=-160, la2=-166, ra1=160, ra2=166, ll1=-5, ll2=6, rl1=22, rl2=-18)
PULL_TOP = P(la1=-55, la2=-172, ra1=55, ra2=172, ll1=-8, ll2=10, rl1=25, rl2=-22)
PUSH_UP = P(t=116, la1=2, la2=0, ra1=-2, ra2=0, ll1=-64, ll2=-64, rl1=-64, rl2=-64)
PUSH_DOWN = P(t=101, la1=-60, la2=25, ra1=-55, ra2=30, ll1=-79, ll2=-79, rl1=-79, rl2=-79)
LYING = P(t=96, la1=70, la2=100, ra1=35, ra2=95, ll1=-92, ll2=-96, rl1=-87, rl2=-80)
PUSH_ROCK = P(t=132, la1=118, la2=104, ra1=112, ra2=98, ll1=-42, ll2=-28, rl1=18, rl2=-8)


def run_pose(ph, lean=160):
    s = math.sin(ph)
    return P(
        t=lean,
        la1=-55 * s, la2=-55 * s + 85,
        ra1=55 * s, ra2=55 * s + 85,
        ll1=48 * s, ll2=48 * s - 25 - 55 * (1 - s) / 2,
        rl1=-48 * s, rl2=-48 * s - 25 - 55 * (1 + s) / 2,
    )


def joints(p, s=1.0, arm=1.0):
    def seg(o, a, ln):
        x, y = d(a)
        return (o[0] + x * ln * s, o[1] + y * ln * s)

    hip = (0.0, 0.0)
    neck = seg(hip, p["t"], 92)
    sh = seg(hip, p["t"], 80)
    head = seg(hip, p["t"], 92 + 33)
    le = seg(sh, p["la1"], 48 * arm)
    lh = seg(le, p["la2"], 46 * arm)
    re = seg(sh, p["ra1"], 48 * arm)
    rh = seg(re, p["ra2"], 46 * arm)
    lk = seg(hip, p["ll1"], 58)
    lf = seg(lk, p["ll2"], 58)
    rk = seg(hip, p["rl1"], 58)
    rf = seg(rk, p["rl2"], 58)
    return dict(hip=hip, neck=neck, sh=sh, head=head, le=le, lh=lh, re=re, rh=rh,
                lk=lk, lf=lf, rk=rk, rf=rf)


def ground_hip_y(p, s, ground, arm=1.0):
    j = joints(p, s, arm)
    low = max(j["lf"][1], j["rf"][1], j["lh"][1], j["rh"][1], j["head"][1] + 30 * s)
    return ground - low - 6 * s


def stick(ctx, x, y, p, s=1.0, fill=GREY, outline=OUT, face=None, face_dx=0.0,
          alpha=1.0, arm=1.0, lw=17, ow=7):
    j = joints(p, s, arm)
    chains = [
        [j["hip"], j["neck"]],
        [j["sh"], j["le"], j["lh"]],
        [j["sh"], j["re"], j["rh"]],
        [j["hip"], j["lk"], j["lf"]],
        [j["hip"], j["rk"], j["rf"]],
    ]
    ctx.save()
    ctx.translate(x, y)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    hr = 31 * s
    for pas, (col, w) in enumerate(((outline, (lw + 2 * ow) * s), (fill, lw * s))):
        rgb(ctx, col, alpha)
        ctx.set_line_width(w)
        for ch in chains:
            ctx.move_to(*ch[0])
            for pt in ch[1:]:
                ctx.line_to(*pt)
            ctx.stroke()
        r = hr + (ow * s if pas == 0 else 0)
        ctx.arc(j["head"][0], j["head"][1], r, 0, 2 * math.pi)
        ctx.fill()
    if face:
        hx, hy = j["head"]
        hx += face_dx * 9 * s
        rgb(ctx, OUT, alpha)
        for ex in (-10, 10):
            ctx.arc(hx + ex * s, hy - 4 * s, 3.6 * s, 0, 2 * math.pi)
            ctx.fill()
        ctx.set_line_width(3.5 * s)
        if face == "sad":
            ctx.arc(hx, hy + 17 * s, 9 * s, math.pi * 1.15, math.pi * 1.85)
        elif face == "happy":
            ctx.arc(hx, hy + 4 * s, 10 * s, math.pi * 0.15, math.pi * 0.85)
        else:  # determined
            ctx.move_to(hx - 8 * s, hy + 11 * s)
            ctx.line_to(hx + 8 * s, hy + 11 * s)
            ctx.stroke()
            ctx.move_to(hx - 16 * s, hy - 14 * s)
            ctx.line_to(hx - 5 * s, hy - 9 * s)
            ctx.move_to(hx + 16 * s, hy - 14 * s)
            ctx.line_to(hx + 5 * s, hy - 9 * s)
        ctx.stroke()
    ctx.restore()
    return j


def stick_sketch(ctx, x, y, p, s, seed, alpha=0.85):
    """Personnage dessine au crayon (traits tremblants)."""
    rnd = random.Random(seed)
    j = joints(p, s)
    chains = [["hip", "neck"], ["sh", "le", "lh"], ["sh", "re", "rh"],
              ["hip", "lk", "lf"], ["hip", "rk", "rf"]]
    ctx.save()
    ctx.translate(x, y)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for _ in range(7):
        ctx.set_source_rgba(1, 1, 1, alpha * rnd.uniform(0.25, 0.6))
        ctx.set_line_width(rnd.uniform(1.2, 3.2))
        for ch in chains:
            pts = [j[k] for k in ch]
            ctx.move_to(pts[0][0] + rnd.gauss(0, 4), pts[0][1] + rnd.gauss(0, 4))
            for pt in pts[1:]:
                ctx.line_to(pt[0] + rnd.gauss(0, 5), pt[1] + rnd.gauss(0, 5))
            ctx.stroke()
        hx, hy = j["head"]
        ctx.arc(hx + rnd.gauss(0, 3), hy + rnd.gauss(0, 3), 30 * s + rnd.gauss(0, 3), 0, 2 * math.pi)
        ctx.stroke()
    ctx.restore()


# ----------------------------------------------------------------------------- text
def font(ctx, family=MONO, size=40, bold=True, italic=False):
    ctx.select_font_face(family,
                         cairo.FONT_SLANT_ITALIC if italic else cairo.FONT_SLANT_NORMAL,
                         cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)


def text_width(ctx, s, spacing=0):
    if not spacing:
        return ctx.text_extents(s).x_advance
    return sum(ctx.text_extents(ch).x_advance for ch in s) + spacing * (len(s) - 1)


def text(ctx, s, x, y, size=40, family=MONO, bold=True, italic=False, color=WHITE,
         alpha=1.0, align="c", spacing=0):
    font(ctx, family, size, bold, italic)
    w = text_width(ctx, s, spacing)
    if align == "c":
        x -= w / 2
    elif align == "r":
        x -= w
    rgb(ctx, color, alpha)
    if not spacing:
        ctx.move_to(x, y)
        ctx.show_text(s)
    else:
        for ch in s:
            ctx.move_to(x, y)
            ctx.show_text(ch)
            x += ctx.text_extents(ch).x_advance + spacing
    return w


def glow(ctx, x, y, r, color, a=0.45):
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, color[0], color[1], color[2], a)
    g.add_color_stop_rgba(1, color[0], color[1], color[2], 0)
    ctx.set_source(g)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.fill()


def tag(ctx, s, x, y, ang, size=20, alpha=1.0):
    """Etiquette blanche collee sur l'EGO (LOSER, GIVE UP...)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(math.radians(ang))
    font(ctx, MONO, size, True)
    w = text_width(ctx, s, 2)
    ctx.set_source_rgba(0.95, 0.95, 0.95, alpha)
    ctx.rectangle(-w / 2 - 10, -size * 0.95, w + 20, size * 1.45)
    ctx.fill()
    ctx.set_source_rgba(0, 0, 0, alpha)
    ctx.set_line_width(2)
    ctx.rectangle(-w / 2 - 10, -size * 0.95, w + 20, size * 1.45)
    ctx.stroke()
    text(ctx, s, 0, 0, size, color=(0.05, 0.05, 0.05), alpha=alpha, spacing=2)
    ctx.restore()


# ----------------------------------------------------------------------------- decor
def background(ctx, base=BG, spot=None, spot_a=0.0):
    rgb(ctx, base)
    ctx.paint()
    if spot:
        glow(ctx, spot[0], spot[1], spot[2], spot[3] if len(spot) > 3 else (1, 1, 1), spot_a)


def vignette(ctx, strength=0.75):
    g = cairo.RadialGradient(W / 2, H / 2, H * 0.25, W / 2, H / 2, H * 0.75)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0, 0, 0, strength)
    ctx.set_source(g)
    ctx.paint()


_rng = np.random.default_rng(7)
GRAIN = []
for _ in range(6):
    n = _rng.integers(0, 255, size=(H // 2, W // 2), dtype=np.uint8)
    arr = np.empty((H // 2, W // 2, 4), dtype=np.uint8)
    arr[..., 0] = n
    arr[..., 1] = n
    arr[..., 2] = n
    arr[..., 3] = 255
    surf = cairo.ImageSurface.create_for_data(arr, cairo.FORMAT_ARGB32, W // 2, H // 2)
    GRAIN.append((surf, arr))


def grain(ctx, frame, a=0.045):
    surf = GRAIN[frame % len(GRAIN)][0]
    ctx.save()
    ctx.scale(2, 2)
    ctx.set_source_surface(surf, 0, 0)
    ctx.paint_with_alpha(a)
    ctx.restore()


class Confetti:
    def __init__(self, n=140, seed=3):
        r = random.Random(seed)
        self.p = []
        for _ in range(n):
            col = r.choice([(0.85, 0.85, 0.85), (0.6, 0.6, 0.6), RED, (0.95, 0.95, 0.95)])
            self.p.append(dict(x=r.uniform(-50, W + 50), y0=r.uniform(-H, H), v=r.uniform(160, 380),
                               sw=r.uniform(0.6, 2.2), ph=r.uniform(0, 6.28), w=r.uniform(8, 16),
                               h=r.uniform(14, 26), c=col, rot=r.uniform(-4, 4)))

    def draw(self, ctx, t, a=1.0):
        for q in self.p:
            y = (q["y0"] + q["v"] * t) % (H + 200) - 100
            x = q["x"] + 30 * math.sin(q["ph"] + t * q["sw"])
            ctx.save()
            ctx.translate(x, y)
            ctx.rotate(q["ph"] + t * q["rot"])
            rgb(ctx, q["c"], a * 0.9)
            ctx.rectangle(-q["w"] / 2, -q["h"] / 2, q["w"], q["h"] * abs(math.cos(t * 3 + q["ph"])) + 2)
            ctx.fill()
            ctx.restore()


CONFETTI = Confetti()


class Crowd:
    def __init__(self, seed=11):
        r = random.Random(seed)
        self.rows = []
        for i, (y, sc, col) in enumerate([(1290, 1.25, (0.16, 0.16, 0.17)),
                                          (1500, 1.4, (0.13, 0.13, 0.14)),
                                          (1720, 1.55, (0.11, 0.11, 0.12)),
                                          (1950, 1.7, (0.09, 0.09, 0.1))]):
            row = []
            n = 9 - i
            for k in range(n + 1):
                x = (k + r.uniform(-0.3, 0.3) + (0.5 if i % 2 else 0)) * (W / n)
                row.append(dict(x=x, ph=r.uniform(0, 6.28), sp=r.uniform(5, 9),
                                kind=r.choice([CHEER, CHEER2, CHEER, POINT, STAND])))
            self.rows.append((y, sc, col, row))

    def draw(self, ctx, t, mood="cheer", ha=False):
        for y, sc, col, row in self.rows:
            for q in row:
                bounce = abs(math.sin(t * q["sp"] + q["ph"]))
                if mood == "cheer":
                    pose = pmix(q["kind"], CHEER, 0.4 + 0.6 * bounce)
                else:
                    pose = pmix(LAUGH, POINT, bounce)
                stick(ctx, q["x"], y - 18 * bounce, pose, sc, fill=col, outline=(0.04, 0.04, 0.045))


CROWD = Crowd()


def calendar(ctx, x, y, label, flips=None, s=1.0):
    def page(px, py, lab, ang=0.0, a=1.0):
        ctx.save()
        ctx.translate(px, py)
        ctx.rotate(ang)
        ctx.scale(s, s)
        ctx.set_source_rgba(0.85, 0.13, 0.15, a)
        ctx.rectangle(-78, -70, 156, 150)
        ctx.fill()
        ctx.set_source_rgba(0.12, 0.12, 0.12, a)
        ctx.rectangle(-78, -86, 156, 22)
        ctx.fill()
        ctx.set_source_rgba(0.9, 0.9, 0.9, a)
        for ex in (-40, 40):
            ctx.arc(ex, -76, 6, 0, 6.28)
            ctx.fill()
        size = 92 if len(lab) <= 1 else (78 if len(lab) == 2 else 62)
        text(ctx, lab, 0, 30, size, color=(1, 1, 1), alpha=a)
        text(ctx, "DAY", 0, 66, 18, color=(1, 1, 1), alpha=a * 0.85, spacing=3)
        ctx.restore()

    page(x, y, label)
    for f in flips or []:
        k = f[1]
        page(x - 230 * k, y - 40 * k + 120 * k * k, f[0], -1.1 * k, (1 - k) * 0.9)


# ----------------------------------------------------------------------------- camera
def camera(ctx, cx, cy, z, shake=0.0, frame=0):
    if shake:
        r = random.Random(frame)
        cx += r.uniform(-shake, shake)
        cy += r.uniform(-shake, shake)
    ctx.translate(W / 2, H / 2)
    ctx.scale(z, z)
    ctx.translate(-cx, -cy)


# ============================================================================= SCENES
PODIUM = dict(
    disc=dict(x=540, top=800, name="DISCIPLINE", num="1", bx=(425, 655)),
    moti=dict(x=310, top=880, name="MOTIVATION", num="2", bx=(195, 425)),
    tale=dict(x=770, top=920, name="TALENT", num="3", bx=(655, 885)),
)
EGO_X, GROUND = 975, 1080


def draw_podium_world(ctx, t, frame, mock=0.0, tags=0.0, ego_red=0.0, ego_on_top=False):
    background(ctx, BG, (W / 2, 750, 750), 0.08)
    CONFETTI.draw(ctx, t, 0.55 if ego_on_top or mock < 0.5 else 0.35)
    # podium blocks
    for key, c in PODIUM.items():
        x0, x1 = c["bx"]
        rgb(ctx, (0.25, 0.25, 0.26))
        ctx.rectangle(x0, c["top"], x1 - x0, GROUND - c["top"] + 400)
        ctx.fill()
        rgb(ctx, (0.33, 0.33, 0.34))
        ctx.rectangle(x0, c["top"], x1 - x0, 10)
        ctx.fill()
        text(ctx, c["num"], (x0 + x1) / 2, c["top"] + 120, 96, color=(0.55, 0.55, 0.56))

    figures = []
    if not ego_on_top:
        for i, (key, c) in enumerate(PODIUM.items()):
            ph = t * 7 + i * 1.7
            base = pmix(CHEER, CHEER2, 0.5 + 0.5 * math.sin(ph))
            mk = pmix(LAUGH, POINT, 0.5 + 0.5 * math.sin(t * 9 + i))
            pose = pmix(base, mk, ease(mock))
            figures.append((key, c["x"], c["top"], pose, GREY, None, c["name"]))
        ego_pose = pmix(STAND, SAD, ease(mock))
        ego_pose["t"] = 180 - 8 * ease(mock)
        figures.append(("ego", EGO_X, GROUND, ego_pose, mix(WHITE, (0.97, 0.55, 0.55), ego_red),
                        "sad", "EGO"))
    else:
        # fin : l'EGO est numero 1
        order = [("disc", "moti"), ("moti", "disc"), ("tale", "tale")]
        names = {"disc": "DISCIPLINE", "moti": "MOTIVATION", "tale": "TALENT"}
        figures.append(("ego", PODIUM["disc"]["x"], PODIUM["disc"]["top"],
                        pmix(CHEER, CHEER2, 0.5 + 0.5 * math.sin(t * 8)), RED, "happy", "EGO"))
        figures.append(("a", PODIUM["moti"]["x"], PODIUM["moti"]["top"], SAD, GREY, None, "DISCIPLINE"))
        figures.append(("b", PODIUM["tale"]["x"], PODIUM["tale"]["top"], SAD, GREY, None, "TALENT"))
        figures.append(("c", EGO_X, GROUND, SAD, (0.4, 0.4, 0.41), None, "MOTIVATION"))

    ego_hip = None
    for key, x, top, pose, col, face, name in figures:
        s = 1.05 if key != "ego" or ego_on_top else 1.0
        hy = ground_hip_y(pose, s, top)
        if key == "ego" and mock > 0 and not ego_on_top:
            x += math.sin(t * 40) * 2.5 * mock
        j = stick(ctx, x, hy, pose, s, fill=col, face=face, face_dx=-0.3)
        hx, hyy = x + j["head"][0], hy + j["head"][1]
        is_red = key == "ego"
        text(ctx, name, hx, hyy - (95 if is_red and ego_on_top else 52), 22, color=RED if is_red else (0.82, 0.82, 0.83),
             spacing=4)
        if key == "ego":
            ego_hip = (x, hy)

    # HA HA
    if mock > 0.2 and not ego_on_top:
        r = random.Random(int(t * 6))
        for _ in range(4):
            key = r.choice(list(PODIUM))
            c = PODIUM[key]
            text(ctx, "HA", c["x"] + r.uniform(-120, 120), c["top"] + r.uniform(-260, 40),
                 r.uniform(26, 40), color=(0.75, 0.75, 0.75), alpha=0.85)

    # etiquettes qui volent sur l'EGO
    if tags > 0 and ego_hip:
        specs = [("LOSER", "moti", (-8, -95), -18), ("GIVE UP", "tale", (12, -20), 24),
                 ("4TH PLACE", "disc", (-6, 50), -9), ("NOBODY", "moti", (10, -150), 14)]
        for i, (lab, src, off, ang) in enumerate(specs):
            k = clamp(tags * 4 - i)
            if k <= 0:
                continue
            c = PODIUM[src]
            sx, sy = c["x"] + 60, c["top"] - 150
            ex, ey = ego_hip[0] + off[0], ego_hip[1] + off[1]
            e = ease_out(k)
            x = lerp(sx, ex, e)
            y = lerp(sy, ey, e) - 120 * math.sin(math.pi * e)
            tag(ctx, lab, x, y, lerp(ang + 360, ang, e) if k < 1 else ang, 17)

    CROWD.draw(ctx, t, "laugh" if mock > 0.5 else "cheer")


def scene_podium(ctx, t, frame):
    # 0 - 2.5 : plan large / 2.5 - 6 : gros plans / 6 - 9.6 : moqueries
    if t < 2.6:
        z = lerp(1.0, 1.06, t / 2.6)
        camera(ctx, W / 2, H / 2 - 20, z)
        draw_podium_world(ctx, t, frame)
    elif t < 6.1:
        k = t - 2.6
        idx = min(2, int(k / 1.17))
        kk = (k - idx * 1.17) / 1.17
        key = ["disc", "moti", "tale"][idx]
        c = PODIUM[key]
        z = lerp(2.4, 2.75, ease(kk))
        camera(ctx, c["x"] + lerp(-30, 30, kk), c["top"] - 190, z)
        draw_podium_world(ctx, t, frame)
    else:
        k = t - 6.1
        camera(ctx, lerp(W / 2, W / 2 + 60, ease(k / 3.5)), H / 2 - 20, lerp(1.0, 1.12, ease(k / 3.5)),
               shake=4 if k > 2.6 else 0, frame=frame)
        draw_podium_world(ctx, t, frame, mock=clamp(k / 0.6), tags=clamp((k - 0.7) / 2.2),
                          ego_red=clamp((k - 2.2) / 1.0))


def gym_base(ctx, glow_a=0.08, red=False):
    background(ctx, (0.055, 0.055, 0.06))
    glow(ctx, W / 2, 1020, 650, RED if red else (1, 1, 1), glow_a)
    rgb(ctx, (0.3, 0.3, 0.31))
    ctx.set_line_width(4)
    ctx.move_to(0, 1290)
    ctx.line_to(W, 1290)
    ctx.stroke()


BAR_Y = 770


def pullup_bar(ctx):
    rgb(ctx, (0.55, 0.55, 0.56))
    ctx.set_line_width(9)
    for x in (300, 780):
        ctx.move_to(x, BAR_Y)
        ctx.line_to(x, 1290)
        ctx.stroke()
    ctx.set_line_width(10)
    ctx.move_to(280, BAR_Y)
    ctx.line_to(800, BAR_Y)
    ctx.stroke()


def ego_pullup(ctx, u, s=1.15, col=WHITE, shake=0.0, t=0.0):
    pose = pmix(HANG, PULL_TOP, ease(u))
    j = joints(pose, s)
    hip_y = BAR_Y - j["rh"][1] + 4
    x = 540 + math.sin(t * 50) * shake
    j = stick(ctx, x, hip_y, pose, s, fill=col, face="sad" if u < 0.7 else "angry")
    text(ctx, "EGO", x + j["head"][0], hip_y + j["head"][1] - 46, 20, color=RED, spacing=3)
    return x + j["head"][0], hip_y + j["head"][1]


def ego_pushup(ctx, u, s=1.15, col=WHITE):
    pose = pmix(PUSH_UP, PUSH_DOWN, ease(u))
    hy = ground_hip_y(pose, s, 1290, arm=0.9)
    j = stick(ctx, 500, hy, pose, s, fill=col, face="angry", face_dx=0.8, arm=0.9)
    text(ctx, "EGO", 500 + j["head"][0], hy + j["head"][1] - 46, 20, color=RED, spacing=3)


def scene_day_one(ctx, t, frame):
    camera(ctx, W / 2, H / 2 - 150, lerp(1.04, 1.0, ease(t / 3)))
    gym_base(ctx)
    pullup_bar(ctx)
    reps = 1 if t > 2.05 else 0
    calendar(ctx, W / 2, 330, "1")
    text(ctx, f"REPS   {reps}", W / 2, 560, 40, color=(0.92, 0.92, 0.92), spacing=6)
    if t < 1.4:
        u = 0.12 + 0.12 * abs(math.sin(t * 5))
        hx, hy = ego_pullup(ctx, u, shake=2.5, t=t)
    elif t < 2.05:
        u = ease((t - 1.4) / 0.65)
        hx, hy = ego_pullup(ctx, u, shake=1.5, t=t)
    elif t < 2.6:
        hx, hy = ego_pullup(ctx, 1.0)
    else:
        hx, hy = ego_pullup(ctx, 1 - ease((t - 2.6) / 0.6))
    if t > 2.05:
        k = clamp((t - 2.05) / 0.25)
        text(ctx, "1", 790, 700, 90 * back_out(k), color=WHITE, alpha=clamp(1.6 - (t - 2.05)))


TL_LEN = 5.2


def scene_timelapse(ctx, t, frame):
    camera(ctx, W / 2, H / 2 - 150, 1.0)
    gym_base(ctx)
    prog = clamp(t / TL_LEN)
    day = int(1 + 364 * prog ** 1.5)
    reps = int(24990 * prog ** 1.7)
    # pages qui s'envolent
    flips = []
    period = 0.18
    for i in range(3):
        tt = (t - i * period) % period
        k = tt / period
        prev_day = int(1 + 364 * clamp((t - tt - i * period) / TL_LEN) ** 1.5)
        if t > period:
            flips.append((str(max(1, prev_day)), clamp(k + i * 0.33)))
    calendar(ctx, W / 2, 330, str(day), flips)
    text(ctx, f"REPS   {reps:,}", W / 2, 560, 40, color=(0.92, 0.92, 0.92), spacing=6)
    seg = int(t / 1.05) % 2
    if seg == 0:
        pullup_bar(ctx)
        u = 0.5 - 0.5 * math.cos(t * 2 * math.pi * 2.6)
        ego_pullup(ctx, u)
    else:
        u = 0.5 - 0.5 * math.cos(t * 2 * math.pi * 3.0)
        ego_pushup(ctx, u)
    text(ctx, "TIME-LAPSE", W / 2, 1360, 20, color=(0.5, 0.5, 0.5), spacing=5,
         alpha=0.6 + 0.4 * math.sin(t * 6))


def scene_crisis(ctx, t, frame):
    camera(ctx, W / 2, H / 2 - 60, lerp(1.0, 1.12, ease(t / 2.2)))
    pulse = 0.18 + 0.1 * math.sin(t * 5)
    gym_base(ctx, glow_a=pulse, red=True)
    calendar(ctx, W / 2, 330, "X")
    text(ctx, "REPS   25,000", W / 2, 560, 40, color=(0.92, 0.92, 0.92), spacing=6)
    hy = ground_hip_y(SAD, 1.1, 1290)
    j = stick(ctx, 540, hy, SAD, 1.1, fill=WHITE, face="sad")
    text(ctx, "EGO", 540, hy + j["head"][1] - 46, 20, color=RED, spacing=3)
    vignette(ctx, 0.85)


LANES = [930, 1080, 1230, 1380]


def track(ctx, scroll, red=0.0):
    background(ctx, (0.06, 0.06, 0.065))
    glow(ctx, W / 2, 1150, 700, RED, 0.06 + 0.1 * red)
    rgb(ctx, (0.28, 0.28, 0.29))
    ctx.set_line_width(3)
    for y in LANES:
        ctx.move_to(0, y + 60)
        ctx.line_to(W, y + 60)
        ctx.stroke()
    # marques au sol qui defilent
    rgb(ctx, (0.22, 0.22, 0.23))
    ctx.set_line_width(4)
    for y in LANES:
        off = (-scroll) % 260
        x = off - 260
        while x < W:
            ctx.move_to(x, y + 60)
            ctx.line_to(x + 60, y + 60)
            ctx.stroke()
            x += 260


def runner(ctx, x, lane_y, ph, col, s=0.85, face=None, label=None, lab_col=(0.8, 0.8, 0.8), alpha=1.0):
    pose = run_pose(ph)
    hy = lane_y + 60 - 112 * s + 10 * abs(math.cos(ph)) * s - 8 * s
    j = stick(ctx, x, hy, pose, s, fill=col, face=face, face_dx=0.8, alpha=alpha)
    if label:
        text(ctx, label, x + j["head"][0], hy + j["head"][1] - 44 * s, 18, color=lab_col, spacing=3,
             alpha=alpha)


def thought_bubble(ctx, cx, cy, r, col, t, frame):
    ctx.save()
    n = 18
    pts = [(cx + r * math.cos(i / n * 2 * math.pi), cy + r * 0.78 * math.sin(i / n * 2 * math.pi))
           for i in range(n)]
    br = r * 0.27
    rgb(ctx, col)
    for x, y in pts:
        ctx.arc(x, y, br + 5, 0, 2 * math.pi)
        ctx.fill()
    rgb(ctx, (0.08, 0.08, 0.085))
    for x, y in pts:
        ctx.arc(x, y, br - 1, 0, 2 * math.pi)
        ctx.fill()
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(1, 0.78)
    ctx.arc(0, 0, r, 0, 2 * math.pi)
    ctx.restore()
    ctx.fill_preserve()
    ctx.clip()
    r_ = random.Random(5)
    for i in range(14):
        x = cx - r + 40 + (i % 7) * (2 * r - 80) / 6 + r_.uniform(-15, 15)
        y = cy - 60 + (i // 7) * 150
        b = abs(math.sin(t * 9 + i))
        stick(ctx, x, y - 10 * b, pmix(LAUGH, POINT if i % 2 else CHEER, b), 0.55,
              fill=(0.55, 0.55, 0.56), outline=(0.05, 0.05, 0.05))
    rr = random.Random(int(t * 7))
    for _ in range(5):
        text(ctx, "HA", cx + rr.uniform(-r + 40, r - 60), cy + rr.uniform(-r * 0.6, r * 0.6), 26,
             color=(0.85, 0.85, 0.85))
    tag(ctx, "LOSER", cx + 90, cy + 40, -12, 16)
    ctx.restore()
    for i, (dx, dy, rr2) in enumerate([(150, 380, 26), (175, 470, 18), (195, 540, 12)]):
        ctx.new_path()
        ctx.arc(cx + dx - 90, cy + dy, rr2, 0, 6.28)
        rgb(ctx, col)
        ctx.set_line_width(4)
        ctx.stroke()


def scene_race_fall(ctx, t, frame):
    track(ctx, t * 500 * clamp(1.6 - t), red=clamp((t - 2.6)))
    others = [("MOTIVATION", LANES[0], 380, 1.0), ("DISCIPLINE", LANES[1], 420, 1.2),
              ("TALENT", LANES[2], 400, 1.1)]
    for name, ly, x0, sp in others:
        x = x0 + max(0, t - 0.5) ** 1.6 * 420 * sp
        if x < W + 150:
            runner(ctx, x, ly, t * 12 + sp, GREY, label=name)
    red = ease(clamp((t - 2.5) / 1.0))
    col = mix(WHITE, RED, red)
    ex = 300 + min(t, 1.4) * 90
    if t < 1.35:
        runner(ctx, ex, LANES[3], t * 11, col, s=1.0, face="angry", label="EGO", lab_col=RED)
    else:
        k = ease_out((t - 1.35) / 0.35)
        pose = pmix(run_pose(1.35 * 11), LYING, k)
        hy = lerp(LANES[3] + 60 - 112, ground_hip_y(LYING, 1.0, LANES[3] + 60), k)
        stick(ctx, ex + 60 * k, hy, pose, 1.0, fill=col, face="sad", face_dx=0.9)
        text(ctx, "EGO", ex + 60 * k + 120, hy - 60, 20, color=RED, spacing=3)
    if t < 0.9:
        text(ctx, "GO!", W / 2, 560, 130 * back_out(t / 0.25), color=WHITE, alpha=clamp((0.9 - t) * 3))
    if t > 1.9:
        k = ease_out((t - 1.9) / 0.4)
        bcol = mix(WHITE, RED, red)
        ctx.save()
        ctx.translate(400, 720)
        ctx.scale(k, k)
        ctx.translate(-400, -720)
        thought_bubble(ctx, 400, 720, 300, bcol, t, frame)
        ctx.restore()
    if t > 3.3:
        text(ctx, "CAN'T", W / 2 + 40, 1650, 120, family=SERIF, color=(0.9, 0.9, 0.9),
             alpha=0.25 * clamp((t - 3.3) * 4))
        text(ctx, "GIVE UP...", W / 2 + 40, 1780, 120, family=SERIF, color=(0.9, 0.9, 0.9),
             alpha=0.25 * clamp((t - 3.3) * 4))
    vignette(ctx, 0.7)


DEFINITION = [
    "the word the lazy use to describe",
    "the dedicated. an intense, unshakable",
    "focus on one single goal — often",
    "mistaken for madness. the hidden",
    "ingredient behind every success.",
]


def scene_obsessed(ctx, t, frame):
    rgb(ctx, (0.1, 0.1, 0.105))
    ctx.paint()
    if t < 2.4:
        z = lerp(1.0, 1.12, ease(t / 2.4))
        camera(ctx, W / 2, 900, z)
    else:
        k = ease((t - 2.4) / 0.6)
        camera(ctx, lerp(W / 2, 330, k), lerp(900, 640, k), lerp(1.12, 2.3, k))
    x0 = 110
    text(ctx, "obsessed", x0, 620, 156, family=SERIF, bold=False, align="l", color=(0.95, 0.95, 0.95))
    text(ctx, "[əbˈsɛst]  adjective • English", x0, 705, 46, family=SERIF, bold=False, italic=True,
         align="l", color=(0.65, 0.65, 0.65))
    rgb(ctx, (0.4, 0.4, 0.4))
    ctx.set_line_width(2)
    ctx.move_to(x0, 755)
    ctx.line_to(W - 110, 755)
    ctx.stroke()
    for i, line in enumerate(DEFINITION):
        a = clamp((t - 0.25 - i * 0.22) * 3)
        text(ctx, line, x0, 835 + i * 64, 46, family=SERIF, bold=False, align="l",
             color=(0.75, 0.75, 0.75), alpha=a)
    if t > 1.3:
        a = clamp((t - 1.3) * 3)
        rgb(ctx, RED, 0.25 * a)
        ctx.rectangle(x0 - 10, 1150, 870 * ease((t - 1.3) / 0.6), 76)
        ctx.fill()
        text(ctx, "obsession beats talent. every time.", x0, 1205, 50, family=SERIF, bold=False,
             align="l", color=WHITE, alpha=a)
    ctx.identity_matrix()
    vignette(ctx, 0.6)
    grain(ctx, frame, 0.06)


def boulder_sketch(ctx, cx, cy, r, seed):
    rnd = random.Random(seed)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for _ in range(170):
        ox, oy = rnd.gauss(0, r * 0.12), rnd.gauss(0, r * 0.12)
        rx = r * rnd.uniform(0.55, 1.02)
        ry = rx * rnd.uniform(0.75, 1.05)
        a0 = rnd.uniform(0, 6.28)
        span = rnd.uniform(0.6, 3.2)
        ctx.save()
        ctx.translate(cx + ox, cy + oy)
        ctx.rotate(rnd.uniform(0, 3.14))
        ctx.scale(1, ry / rx)
        ctx.new_path()
        ctx.arc(0, 0, rx, a0, a0 + span)
        ctx.restore()
        ctx.set_source_rgba(1, 1, 1, rnd.uniform(0.15, 0.6))
        ctx.set_line_width(rnd.uniform(0.8, 2.6))
        ctx.stroke()


def you_vs_you_image(ctx, t, frame, a=1.0):
    seed = frame // 3
    glow(ctx, 560, 1000, 520, (1, 1, 1), 0.07 * a)
    # pente
    rnd = random.Random(seed + 99)
    for _ in range(6):
        ctx.set_source_rgba(1, 1, 1, 0.3 * a)
        ctx.set_line_width(rnd.uniform(1, 2.5))
        ctx.move_to(60, 1420 + rnd.gauss(0, 6))
        ctx.line_to(1040, 900 + rnd.gauss(0, 6))
        ctx.stroke()
    ctx.push_group()
    boulder_sketch(ctx, 640, 900, 210, seed)
    stick_sketch(ctx, 330, 1150, PUSH_ROCK, 1.45, seed + 7)
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(a)


def scene_you_vs_you(ctx, t, frame):
    rgb(ctx, (0.02, 0.02, 0.025))
    ctx.paint()
    words = ["IT'S", "YOU", "VS", "YOU"]
    if t < 1.3:
        i = min(3, int(t / 0.325))
        k = (t - i * 0.325) / 0.325
        sz = lerp(300, 270, k)
        glow(ctx, W / 2, H / 2, 600, (1, 1, 1), 0.12)
        text(ctx, words[i], W / 2, H / 2 + sz * 0.35, sz, family=SERIF, color=WHITE)
    else:
        k = t - 1.3
        ap = clamp(k * 3)
        z = lerp(1.0, 1.08, ease(k / 2.4))
        ctx.save()
        camera(ctx, W / 2, H / 2, z, shake=2, frame=frame)
        text(ctx, "IT'S YOU VS YOU", W / 2, 520, 96, family=SERIF, color=WHITE, alpha=ap)
        you_vs_you_image(ctx, k, frame, ap)
        ctx.restore()
    # flicker
    if frame % 11 == 0:
        ctx.set_source_rgba(1, 1, 1, 0.05)
        ctx.paint()
    vignette(ctx, 0.8)
    grain(ctx, frame, 0.08)


def scene_race_win(ctx, t, frame):
    track(ctx, t * 900, red=0.7)
    ex = 400
    # lignes de vitesse
    rnd = random.Random(frame)
    for _ in range(14):
        y = LANES[3] - 120 + rnd.uniform(-60, 140)
        x = ex - rnd.uniform(60, 220)
        ln = rnd.uniform(80, 260)
        ctx.set_source_rgba(RED[0], RED[1], RED[2], rnd.uniform(0.15, 0.45))
        ctx.set_line_width(rnd.uniform(2, 5))
        ctx.move_to(x, y)
        ctx.line_to(x - ln, y)
        ctx.stroke()
    others = [("MOTIVATION", LANES[0], 1.0), ("TALENT", LANES[1], 2.0), ("DISCIPLINE", LANES[2], 3.0)]
    for name, ly, tp in others:
        x = ex + (tp - t) * 380
        if -150 < x < W + 150:
            runner(ctx, x, ly, t * 11 + tp, (0.45, 0.45, 0.46), label=name, lab_col=(0.6, 0.6, 0.6))
    # ligne d'arrivee
    fx = ex + (3.7 - t) * 520 + 120
    if fx < W + 200:
        rgb(ctx, (0.7, 0.7, 0.7))
        ctx.set_line_width(5)
        ctx.move_to(fx, 560)
        ctx.line_to(fx, LANES[0])
        ctx.stroke()
        rgb(ctx, (0.8, 0.8, 0.8))
        ctx.rectangle(fx - 85, 520, 170, 54)
        ctx.fill()
        text(ctx, "FINISH", fx, 560, 30, color=(0.08, 0.08, 0.08), spacing=4)
        ctx.set_line_width(9)
        for i in range(14):
            y0 = LANES[0] + 60 + i * 40
            rgb(ctx, (0.85, 0.85, 0.85) if i % 2 == 0 else (0.25, 0.25, 0.25))
            ctx.move_to(fx + i * 6, y0)
            ctx.line_to(fx + (i + 1) * 6, y0 + 40)
            ctx.stroke()
    glow(ctx, ex, LANES[3] - 40, 220, RED, 0.35)
    runner(ctx, ex, LANES[3], t * 16, RED, s=1.0, face="angry", label="EGO", lab_col=RED)
    vignette(ctx, 0.7)


def scene_prove(ctx, t, frame):
    # reprend la ligne d'arrivee, assombrie
    ctx.save()
    scene_race_win(ctx, 3.95 + t * 0.15, frame)
    ctx.restore()
    ctx.set_source_rgba(0, 0, 0, 0.55)
    ctx.paint()
    line1 = "PROVE THEM ALL"
    n = int(clamp(t / 0.9) * len(line1))
    text(ctx, line1[:n], W / 2, 1380, 56, color=(0.92, 0.92, 0.92), spacing=8)
    if t > 1.1:
        k = clamp((t - 1.1) / 0.25)
        sc = lerp(1.7, 1.0, ease_out(k))
        shake = (1 - k) * 12
        r = random.Random(frame)
        glow(ctx, W / 2, 1490, 380, RED, 0.35 * k)
        ctx.save()
        ctx.translate(W / 2 + r.uniform(-shake, shake), 1510 + r.uniform(-shake, shake))
        ctx.scale(sc, sc)
        text(ctx, "WRONG.", 0, 0, 120, color=RED, alpha=k, spacing=10)
        ctx.restore()
    vignette(ctx, 0.6)


def scene_final(ctx, t, frame):
    camera(ctx, W / 2, H / 2 - 40, lerp(1.25, 1.0, ease_out(t / 1.2)))
    draw_podium_world(ctx, t + 20, frame, ego_on_top=True)
    ctx.identity_matrix()
    if t > 2.4:
        ctx.set_source_rgba(0, 0, 0, clamp((t - 2.4) / 0.8))
        ctx.paint()


SCENES = [
    ("podium", 9.6, scene_podium),
    ("day_one", 3.2, scene_day_one),
    ("timelapse", TL_LEN, scene_timelapse),
    ("crisis", 2.3, scene_crisis),
    ("race_fall", 4.2, scene_race_fall),
    ("obsessed", 3.4, scene_obsessed),
    ("you_vs_you", 3.8, scene_you_vs_you),
    ("race_win", 4.2, scene_race_win),
    ("prove", 3.0, scene_prove),
    ("final", 3.2, scene_final),
]


def total_duration():
    return sum(s[1] for s in SCENES)


def render_frame(surface, ctx, gt, frame):
    acc = 0.0
    for name, dur, fn in SCENES:
        if gt < acc + dur or name == SCENES[-1][0]:
            lt = gt - acc
            ctx.identity_matrix()
            ctx.save()
            fn(ctx, lt, frame)
            ctx.restore()
            ctx.identity_matrix()
            # flash de coupe
            if acc > 0 and lt < 2 / FPS:
                ctx.set_source_rgba(1, 1, 1, 0.22)
                ctx.paint()
            return name
        acc += dur


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--output", default="output/ego_vs_discipline.mp4")
    ap.add_argument("--music", help="fichier audio a mettre en fond")
    ap.add_argument("--speed", type=float, default=1.0, help="1 = normal, 2 = x2 comme l'original")
    ap.add_argument("--preview", action="store_true", help="planche de captures au lieu de la video")
    args = ap.parse_args()

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surface)
    dur = total_duration()

    if args.preview:
        from PIL import Image
        times = [i * dur / 30 + 0.3 for i in range(30)]
        thumbs = []
        for i, tt in enumerate(times):
            render_frame(surface, ctx, tt, int(tt * FPS))
            surface.flush()
            arr = np.ndarray((H, W, 4), np.uint8, surface.get_data())
            im = Image.fromarray(arr[..., [2, 1, 0]].copy()).resize((216, 384))
            thumbs.append(im)
        sheet = Image.new("RGB", (216 * 10, 384 * 3))
        for i, im in enumerate(thumbs):
            sheet.paste(im, ((i % 10) * 216, (i // 10) * 384))
        out = os.path.splitext(args.output)[0] + "_preview.png"
        os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
        sheet.save(out)
        print(out)
        return

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    n_frames = int(dur * FPS / args.speed)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]
    if args.music:
        cmd += ["-i", args.music, "-map", "0:v", "-map", "1:a", "-c:a", "aac", "-b:a", "192k",
                "-af", f"afade=t=out:st={max(0, n_frames / FPS - 2):.2f}:d=2", "-shortest"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", args.output]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(n_frames):
        gt = f / FPS * args.speed
        render_frame(surface, ctx, gt, f)
        surface.flush()
        proc.stdin.write(bytes(surface.get_data()))
        if f % 60 == 0:
            print(f"\r{f}/{n_frames}", end="", file=sys.stderr, flush=True)
    proc.stdin.close()
    proc.wait()
    print(f"\n-> {args.output} ({n_frames / FPS:.1f}s)")


if __name__ == "__main__":
    main()
