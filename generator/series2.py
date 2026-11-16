#!/usr/bin/env python3
"""
Serie 2 — style "cinematique" : bonhommes blancs en volume (sans visage), lumieres de projecteurs,
pluie, brouillard, ambiance gris-bleu, petites phrases en haut de l'ecran.
Histoires originales : la tempete, les mots devenus marches, les deux bougies, le pont, les chaines.
Chaque video contient la photo motivation du rocher.

    python3 generator/series2.py --video all
    python3 generator/series2.py --video 2 --preview
"""
import argparse
import math
import os
import random
import subprocess
import sys

import cairo
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ego_video as E  # noqa: E402
import series as S1  # noqa: E402
from ego_video import (W, H, FPS, MONO, SERIF, WHITE, RED, P, pmix, text, glow, ik, clamp, lerp,  # noqa: E402
                       ease, ease_out, ease_in, back_out, mix, rgb, d, camera)

SND = S1.SND
FIG = (0.95, 0.95, 0.97)
FIG_DIM = (0.62, 0.64, 0.68)
OUTL = (0.13, 0.14, 0.17)
WARM = (1.0, 0.86, 0.6)
T_SPLIT, T_END = 15.0, 24.0

STAND = S1.STAND
SIT = S1.SIT
CHEER = E.CHEER
CARRY = P(la1=-165, la2=-178, ra1=165, ra2=178, ll1=-8, ll2=-5, rl1=8, rl2=5)
BEND = P(t=128, la1=35, la2=15, ra1=28, ra2=10, ll1=-12, ll2=-6, rl1=18, rl2=4)
KNEEL = P(t=165, la1=150, la2=200, ra1=140, ra2=190, ll1=95, ll2=0, rl1=-20, rl2=-95)
OPEN = P(la1=-125, la2=-120, ra1=125, ra2=120, ll1=-12, ll2=-6, rl1=12, rl2=6)


# ============================================================================ personnage "volume"
def joints2(p, s, arm=1.0, bend=0.0):
    j = E.joints(p, s, arm)
    nx, ny = j["neck"]
    dx, dy = d(p["t"] + bend)
    j["head"] = (nx + dx * 44 * s, ny + dy * 44 * s)
    return j


def stick2(ctx, x, y, p, s=1.0, tint=FIG, alpha=1.0, shadow=None, bend=0.0, arm=1.0, facing=1):
    j = joints2(p, s, arm, bend)
    lw, ow, hr = 25 * s, 3.5 * s, 38 * s
    if shadow is not None:
        fx = x + facing * (j["lf"][0] + j["rf"][0]) / 2
        g = cairo.RadialGradient(fx, shadow, 0, fx, shadow, 90 * s)
        g.add_color_stop_rgba(0, 0, 0, 0, 0.6 * alpha)
        g.add_color_stop_rgba(1, 0, 0, 0, 0)
        ctx.save()
        ctx.translate(fx, shadow)
        ctx.scale(1, 0.15)
        ctx.translate(-fx, -shadow)
        ctx.set_source(g)
        ctx.arc(fx, shadow, 90 * s, 0, 2 * math.pi)
        ctx.fill()
        ctx.restore()
    back = [["sh", "le", "lh"], ["hip", "lk", "lf"]]
    front = [["hip", "neck"], ["sh", "re", "rh"], ["hip", "rk", "rf"]]
    ys = [v[1] for v in j.values()]
    y0, y1 = min(ys) - hr, max(ys) + lw

    def grad(k):
        g = cairo.LinearGradient(-50 * s, y0, 50 * s, y1)
        g.add_color_stop_rgba(0, tint[0] * k, tint[1] * k, tint[2] * k, alpha)
        g.add_color_stop_rgba(1, tint[0] * k * 0.6, tint[1] * k * 0.6, tint[2] * k * 0.64, alpha)
        return g

    def chains(chs, src, w, dx=0.0, dy=0.0):
        if isinstance(src, tuple):
            ctx.set_source_rgba(*src)
        else:
            ctx.set_source(src)
        ctx.set_line_width(w)
        for ch in chs:
            ctx.move_to(j[ch[0]][0] + dx, j[ch[0]][1] + dy)
            for k in ch[1:]:
                ctx.line_to(j[k][0] + dx, j[k][1] + dy)
            ctx.stroke()

    ctx.save()
    ctx.translate(x, y)
    ctx.scale(facing, 1)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    out = (OUTL[0], OUTL[1], OUTL[2], 0.9 * alpha)
    chains(back, out, lw + 2 * ow)
    chains(back, grad(0.7), lw)
    chains(front, out, lw + 2 * ow)
    hx, hy = j["head"]
    ctx.set_source_rgba(*out)
    ctx.arc(hx, hy, hr + ow, 0, 2 * math.pi)
    ctx.fill()
    chains(front, grad(1.0), lw)
    g = cairo.RadialGradient(hx - hr * 0.35, hy - hr * 0.4, 0, hx - hr * 0.1, hy - hr * 0.1, hr * 1.25)
    g.add_color_stop_rgba(0, min(1, tint[0] * 1.05), min(1, tint[1] * 1.05), min(1, tint[2] * 1.05), alpha)
    g.add_color_stop_rgba(1, tint[0] * 0.6, tint[1] * 0.6, tint[2] * 0.65, alpha)
    ctx.set_source(g)
    ctx.arc(hx, hy, hr, 0, 2 * math.pi)
    ctx.fill()
    chains(front, (1, 1, 1, 0.22 * alpha), lw * 0.28, -lw * 0.17, -lw * 0.17)
    ctx.restore()
    return {k: (x + facing * v[0], y + v[1]) for k, v in j.items()}


def hip_on(p, s, gy, bend=0.0):
    j = joints2(p, s, 1.0, bend)
    low = max(j["lf"][1], j["rf"][1], j["lh"][1], j["rh"][1], j["head"][1] + 38 * s)
    return gy - low - 12 * s


def placed2(ctx, x, gy, p, s, tint=FIG, facing=1, alpha=1.0, shadow=True):
    hy = hip_on(p, s, gy)
    return stick2(ctx, x, hy, p, s, tint, alpha, gy if shadow else None, facing=facing)


def walker2(ctx, hipx, ground, smooth, dist, s, tint=FIG, lean=172, stride=26, lift=16, arm=34, alpha=1.0,
            hip_h=104, facing=1, shadow=True, run=False, arms=None):
    L = stride * s
    ph = dist / (4 * L) * 2 * math.pi
    hipy = smooth(hipx) - hip_h * s + 4 * s * math.cos(2 * ph)
    pose = {"t": lean}
    for side, off in (("l", 0.0), ("r", math.pi)):
        u = ((ph + off) / (2 * math.pi)) % 1
        if u < 0.5:
            fl, lf = L - 4 * L * u, 0.0
        else:
            fl = -L + 4 * L * (u - 0.5)
            lf = math.sin(math.pi * (u - 0.5) * 2) * lift * s
        fy = ground(hipx + facing * fl) - lf - 12 * s
        a1, a2 = ik(0, hipy, fl, fy, 58 * s, 58 * s, (1, 0))
        pose[side + "l1"], pose[side + "l2"] = a1, a2
    c = math.cos(ph)
    bend = 80 if run else 30
    pose["la1"], pose["la2"] = -arm * c, -arm * c + bend
    pose["ra1"], pose["ra2"] = arm * c, arm * c + bend
    if arms:
        pose.update(arms)
    return stick2(ctx, hipx, hipy, pose, s, tint, alpha, ground(hipx) if shadow else None, facing=facing), hipy


def tagname(ctx, j, name, s=1.0, col=(0.78, 0.8, 0.85), alpha=1.0):
    hx, hy = j["head"]
    text(ctx, name, hx, hy - 38 * s - 22, 19, color=col, spacing=4, alpha=alpha)


# ============================================================================ ambiance
def sky(ctx, top=(0.12, 0.14, 0.19), bot=(0.03, 0.035, 0.05)):
    ctx.save()
    ctx.identity_matrix()
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, *top)
    g.add_color_stop_rgb(1, *bot)
    ctx.set_source(g)
    ctx.paint()
    ctx.restore()


def spot(ctx, x, ytop, ybot, wtop, wbot, a=0.22, col=(0.85, 0.9, 1.0)):
    g = cairo.LinearGradient(0, ytop, 0, ybot)
    g.add_color_stop_rgba(0, col[0], col[1], col[2], a)
    g.add_color_stop_rgba(1, col[0], col[1], col[2], a * 0.15)
    ctx.set_source(g)
    ctx.move_to(x - wtop / 2, ytop)
    ctx.line_to(x + wtop / 2, ytop)
    ctx.line_to(x + wbot / 2, ybot)
    ctx.line_to(x - wbot / 2, ybot)
    ctx.close_path()
    ctx.fill()
    ctx.save()
    ctx.translate(x, ybot)
    ctx.scale(1, 0.16)
    g = cairo.RadialGradient(0, 0, 0, 0, 0, wbot * 0.6)
    g.add_color_stop_rgba(0, col[0], col[1], col[2], a * 1.6)
    g.add_color_stop_rgba(1, col[0], col[1], col[2], 0)
    ctx.set_source(g)
    ctx.arc(0, 0, wbot * 0.6, 0, 6.28)
    ctx.fill()
    ctx.restore()


def rain(ctx, T, amount, wind=0.3, seed=1):
    if amount <= 0:
        return
    ctx.save()
    ctx.identity_matrix()
    r = random.Random(seed)
    n = int(320 * amount)
    ctx.set_line_width(2)
    for _ in range(n):
        x0, y0 = r.uniform(-300, W + 300), r.uniform(0, H)
        v = r.uniform(1800, 2600)
        ln = r.uniform(30, 70)
        y = (y0 + v * T) % (H + 200) - 100
        x = x0 - wind * (y - y0) * 0.0 + wind * y
        x = (x % (W + 400)) - 200
        ctx.set_source_rgba(0.75, 0.8, 0.9, r.uniform(0.12, 0.35))
        ctx.move_to(x, y)
        ctx.line_to(x - wind * ln, y + ln)
        ctx.stroke()
    ctx.restore()


def fog(ctx, a=0.25, y=1350):
    ctx.save()
    ctx.identity_matrix()
    g = cairo.LinearGradient(0, y - 400, 0, H)
    g.add_color_stop_rgba(0, 0.6, 0.65, 0.75, 0)
    g.add_color_stop_rgba(0.6, 0.6, 0.65, 0.75, a)
    g.add_color_stop_rgba(1, 0.5, 0.55, 0.65, a * 0.6)
    ctx.set_source(g)
    ctx.paint()
    ctx.restore()


def grade(ctx, frame, tint=(0.15, 0.22, 0.4), a=0.06):
    ctx.save()
    ctx.identity_matrix()
    ctx.set_source_rgba(tint[0], tint[1], tint[2], a)
    ctx.paint()
    E.vignette(ctx, 0.8)
    E.grain(ctx, frame, 0.05)
    ctx.restore()


def top_caption(ctx, caps, T):
    ctx.save()
    ctx.identity_matrix()
    for a, b, s_ in caps:
        if not a <= T <= b:
            continue
        n = int(clamp((T - a) / (0.035 * len(s_) + 0.01)) * len(s_))
        al = clamp((b - T) / 0.3)
        size = S1.fit_size(ctx, s_, 30, 980, spacing=6)
        text(ctx, s_[:n], W / 2, 190, size, color=(0.88, 0.9, 0.94), alpha=al, spacing=6)
    ctx.restore()


def flash(ctx, a):
    if a <= 0:
        return
    ctx.save()
    ctx.identity_matrix()
    ctx.set_source_rgba(0.9, 0.93, 1, a)
    ctx.paint()
    ctx.restore()


# ============================================================================ 1. LA TEMPETE
ST_GY = 1380
LIGHTHOUSE_X = 2420


def storm_of(T):
    return ease((T - 3.6) / 0.8) * (1 - 0.85 * ease((T - 19) / 3))


def x_disc(T):
    return -320 + 140 * min(T, 4) + 95 * max(0, min(T, 15) - 4) + 105 * max(0, T - 15)


def world_storm(ctx, T, frame):
    xd = min(x_disc(T), LIGHTHOUSE_X - 90)
    st = storm_of(T)
    e = ease((T - 19.5) / 2.5)
    camera(ctx, xd + lerp(60, 160, e), ST_GY - lerp(230, 420, e), lerp(1.55, 0.95, e))
    sky(ctx, mix((0.13, 0.15, 0.2), (0.07, 0.08, 0.1), st), (0.02, 0.025, 0.035))
    # nuages
    r = random.Random(2)
    for _ in range(14):
        cx = r.uniform(-1000, 3600)
        cy = r.uniform(250, 650)
        rr = r.uniform(160, 320)
        ctx.set_source_rgba(0.05, 0.06, 0.08, 0.5 + 0.4 * st)
        ctx.save()
        ctx.translate(cx + T * 20, cy)
        ctx.scale(1.8, 0.6)
        ctx.arc(0, 0, rr, 0, 6.28)
        ctx.restore()
        ctx.fill()
    # eclair
    bolt = None
    for tb in (4.0, 9.3, 13.1):
        if tb <= T < tb + 0.22:
            bolt = tb
    if bolt:
        rb = random.Random(int(bolt * 10))
        x = xd + rb.uniform(-200, 500)
        y = 120
        ctx.set_source_rgba(0.9, 0.95, 1, 0.9)
        ctx.set_line_width(5)
        ctx.move_to(x, y)
        while y < 900:
            x += rb.uniform(-60, 60)
            y += rb.uniform(50, 110)
            ctx.line_to(x, y)
        ctx.stroke()
    # phare
    lx = LIGHTHOUSE_X
    lamp = (lx, ST_GY - 760)
    ang = T * 1.4
    for k in (0, math.pi):
        a_ = ang + k
        dxb, dyb = math.cos(a_), math.sin(a_) * 0.25
        g = cairo.LinearGradient(lamp[0], lamp[1], lamp[0] + dxb * 1400, lamp[1] + dyb * 1400)
        g.add_color_stop_rgba(0, WARM[0], WARM[1], WARM[2], 0.35)
        g.add_color_stop_rgba(1, WARM[0], WARM[1], WARM[2], 0)
        ctx.set_source(g)
        ctx.move_to(*lamp)
        ctx.line_to(lamp[0] + dxb * 1400 - dyb * 200, lamp[1] + dyb * 1400 - 140)
        ctx.line_to(lamp[0] + dxb * 1400 + dyb * 200, lamp[1] + dyb * 1400 + 140)
        ctx.close_path()
        ctx.fill()
    glow(ctx, lamp[0], lamp[1], 260, WARM, 0.55)
    rgb(ctx, (0.55, 0.57, 0.62))
    ctx.move_to(lx - 90, ST_GY)
    ctx.line_to(lx - 50, lamp[1] + 40)
    ctx.line_to(lx + 50, lamp[1] + 40)
    ctx.line_to(lx + 90, ST_GY)
    ctx.close_path()
    ctx.fill()
    rgb(ctx, (0.3, 0.32, 0.36))
    for k in range(3):
        ctx.rectangle(lx - 80 + k * 6, ST_GY - 200 - k * 200, 160 - k * 12, 40)
    ctx.fill()
    rgb(ctx, WARM)
    ctx.rectangle(lx - 40, lamp[1] - 30, 80, 60)
    ctx.fill()
    if T > 21:
        spot(ctx, lx - 200, lamp[1], ST_GY, 60, 420, 0.35 * ease((T - 21) / 1.5), WARM)
    # route + rambarde
    rgb(ctx, (0.08, 0.085, 0.1))
    ctx.rectangle(-2000, ST_GY, 6000, 900)
    ctx.fill()
    rgb(ctx, (0.35, 0.37, 0.42))
    ctx.set_line_width(4)
    ctx.move_to(-2000, ST_GY)
    ctx.line_to(4000, ST_GY)
    ctx.stroke()
    ctx.set_line_width(6)
    ctx.move_to(-2000, ST_GY - 130)
    ctx.line_to(LIGHTHOUSE_X - 120, ST_GY - 130)
    ctx.stroke()
    x = -2000
    while x < LIGHTHOUSE_X - 120:
        ctx.move_to(x, ST_GY)
        ctx.line_to(x, ST_GY - 130)
        ctx.stroke()
        x += 170
    flat = (lambda _x: ST_GY)
    s = 0.92
    # MOTIVATION : fait demi-tour
    if T < 5:
        xm = -20 + 140 * T
        j, _ = walker2(ctx, xm, flat, flat, 140 * T, s, FIG_DIM)
    else:
        xm = -40 + 700 - 160 * (T - 5)
        j, _ = walker2(ctx, xm, flat, flat, 160 * (T - 5), s, FIG_DIM, facing=-1, lean=176)
    tagname(ctx, j, "MOTIVATION", s, alpha=clamp((12 - T) / 1))
    # EGO : s'arrete et s'effondre
    if T < 8:
        xe = -170 + 140 * min(T, 4) + 95 * max(0, T - 4)
        j, _ = walker2(ctx, xe, flat, flat, xe + 140, s, (0.78, 0.6, 0.6), lean=lerp(172, 150, st))
    else:
        xe = -170 + 560 + 380
        j = placed2(ctx, xe, ST_GY, pmix(SIT, KNEEL, 0.0), s, (0.78, 0.6, 0.6))
    tagname(ctx, j, "EGO", s, col=(0.9, 0.5, 0.5))
    # DISCIPLINE
    if x_disc(T) < LIGHTHOUSE_X - 90:
        j, _ = walker2(ctx, xd, flat, flat, x_disc(T) + 320, s, FIG, lean=lerp(172, 150, st),
                       arm=lerp(34, 18, st))
    else:
        j = placed2(ctx, xd, ST_GY, pmix(STAND, OPEN, ease((T - 21.9) / 0.8)), s, mix(FIG, WARM, 0.25))
    tagname(ctx, j, "DISCIPLINE", s)
    rain(ctx, T, 0.25 + 0.75 * st, wind=0.15 + 0.5 * st, seed=3)
    fog(ctx, 0.12 + 0.12 * st)
    if bolt:
        flash(ctx, 0.35 * (1 - (T - bolt) / 0.22))
    grade(ctx, frame)


# ============================================================================ 2. LES MOTS -> MARCHES
PF, PTOP, PW0, PW1 = 1500, 900, 150, 1010
WORDS = ["LAZY", "LOSER", "NEVER", "GIVE UP", "TOO LATE", "NOBODY"]
BW, BH = 170, 100
STEP_C = [560 + i * 82 for i in range(6)]
PILE = [(260, 0.12), (420, -0.2), (330, 0.05), (480, 0.25), (220, -0.08), (380, 0.18)]
THROW_T = [3.0 + k * 1.1 for k in range(6)]
BUILD_T = [10.0 + k * 1.75 for k in range(6)]


def step_top(i):
    return PF - (i + 1) * BH


def placed_steps(T):
    return sum(1 for b in BUILD_T if T >= b + 1.75)


def stair_ground(n):
    def g(x):
        y = PF
        for i in range(n):
            if STEP_C[i] - BW / 2 <= x <= STEP_C[i] + BW / 2:
                y = min(y, step_top(i))
        if x > PW1 - 5 and n >= 6:
            y = PTOP
        return y
    return g


def stair_smooth(n):
    g = stair_ground(n)
    return lambda x: (g(x - 30) + g(x) + g(x + 30)) / 3


def word_block(ctx, x, y, word, rot=0.0, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    g = cairo.LinearGradient(0, -BH / 2, 0, BH / 2)
    g.add_color_stop_rgba(0, 0.5, 0.52, 0.56, a)
    g.add_color_stop_rgba(1, 0.26, 0.27, 0.3, a)
    ctx.set_source(g)
    S1.rrect(ctx, -BW / 2, -BH / 2, BW, BH, 8)
    ctx.fill_preserve()
    ctx.set_source_rgba(0.1, 0.1, 0.12, a)
    ctx.set_line_width(4)
    ctx.stroke()
    size = S1.fit_size(ctx, word, 30, BW - 24, spacing=2)
    text(ctx, word, 0, 11, size, color=(0.08, 0.08, 0.1), alpha=a, spacing=2)
    ctx.restore()


def world_words(ctx, T, frame):
    hit = 0.0
    for tk in THROW_T:
        if tk + 0.6 <= T < tk + 0.9:
            hit = 1 - (T - tk - 0.6) / 0.3
    cy = 1250 if T < 20.5 else lerp(1250, 1080, ease((T - 20.5) / 2))
    camera(ctx, 580, cy, 1.2, shake=12 * hit, frame=frame)
    sky(ctx)
    spot(ctx, 560, -200, PF, 120, 760, 0.18)
    # parois du trou
    rgb(ctx, (0.07, 0.075, 0.09))
    ctx.rectangle(-800, PTOP, PW0 + 800, 1600)
    ctx.rectangle(PW1, PTOP, 1200, 1600)
    ctx.fill()
    rgb(ctx, (0.05, 0.055, 0.065))
    ctx.rectangle(PW0, PF, PW1 - PW0, 800)
    ctx.fill()
    rgb(ctx, (0.3, 0.32, 0.37))
    ctx.set_line_width(4)
    ctx.move_to(-800, PTOP)
    ctx.line_to(PW0, PTOP)
    ctx.line_to(PW0, PF)
    ctx.line_to(PW1, PF)
    ctx.line_to(PW1, PTOP)
    ctx.line_to(W + 800, PTOP)
    ctx.stroke()
    # foule en haut
    r = random.Random(8)
    leave = ease((T - 20.5) / 2.5)
    for k in range(9):
        side = -1 if k < 5 else 1
        x = (PW0 - 40 - (k % 5) * 75) if side < 0 else (PW1 + 40 + (k - 5) * 75 + 200 * leave)
        pose = pmix(S1.CHEER if False else E.POINT, E.LAUGH, 0.5 + 0.5 * math.sin(T * 6 + k))
        stick2(ctx, x, S1.ground_hip_y(pose, 0.75, PTOP), pose, 0.75, (0.3, 0.32, 0.36), 0.9, facing=-side)
    # marches / blocs
    n_placed = placed_steps(T)
    for i in range(n_placed):
        rgb(ctx, (0.12, 0.125, 0.14))
        ctx.rectangle(STEP_C[i] - BW / 2 + 6, step_top(i) + BH / 2, BW - 12, PF - step_top(i) - BH / 2)
        ctx.fill()
    for i in range(n_placed):
        word_block(ctx, STEP_C[i], step_top(i) + BH / 2, WORDS[i])
    s = 0.85
    carrying = None
    for k, tk in enumerate(THROW_T):
        bt = BUILD_T[k]
        if T < tk:
            continue
        px, prot = PILE[k]
        py = PF - BH / 2
        if T < tk + 0.6:
            u = (T - tk) / 0.6
            sx = PW0 - 60 if k % 2 == 0 else PW1 + 60
            x = lerp(sx, px, u)
            y = lerp(PTOP - 160, py, u * u) - 200 * math.sin(math.pi * u) * 0.4
            word_block(ctx, x, y, WORDS[k], prot + (1 - u) * 6)
        elif T < bt + 0.55:
            word_block(ctx, px, py, WORDS[k], prot)
        elif T < bt + 1.75:
            carrying = k
        if tk + 0.6 <= T < tk + 1.2:
            S1.particles(ctx, px, PF - 5, (T - tk - 0.6) / 0.6, k * 13, n=18, spread=300, up=300,
                         col=(0.6, 0.62, 0.66), size=(4, 10))
    # YOU
    if T < 3:
        j = placed2(ctx, 420, PF, SIT, s)
    elif T < 10:
        near = max([clamp(1 - abs(T - tk - 0.6) / 0.5) for tk in THROW_T] + [0])
        cover = P(t=172, la1=-150, la2=-60, ra1=150, ra2=60, ll1=-10, ll2=-5, rl1=10, rl2=5)
        j = placed2(ctx, 640, PF, pmix(STAND, cover, near), s)
    elif T < BUILD_T[-1] + 1.75:
        k = min(5, int((T - 10.0) / 1.75))
        u = (T - BUILD_T[k]) / 1.75
        px = PILE[k][0]
        tx = STEP_C[k - 1] if k > 0 else STEP_C[0] - 120
        n = k
        g, sm = stair_ground(n), stair_smooth(n)
        if u < 0.3:
            x = lerp(tx, px, ease(u / 0.3))
            j, hy = walker2(ctx, x, g, sm, T * 300, s, facing=-1 if px < tx else 1)
        elif u < 0.4:
            x = px
            j = placed2(ctx, x, PF, BEND, s)
        elif u < 0.85:
            x = lerp(px, tx, ease((u - 0.4) / 0.45))
            j, hy = walker2(ctx, x, g, sm, T * 300, s, arms=dict(la1=-165, la2=-178, ra1=165, ra2=178))
            word_block(ctx, x + 10, j["head"][1] - 95, WORDS[k], 0.0)
        else:
            x = tx
            kk = ease((u - 0.85) / 0.15)
            j = placed2(ctx, x, g(x), CARRY, s)
            bx = lerp(x + 10, STEP_C[k], kk)
            by = lerp(j["head"][1] - 95, step_top(k) + BH / 2, kk)
            word_block(ctx, bx, by, WORDS[k], 0.0)
    else:
        u = clamp((T - (BUILD_T[-1] + 1.75)) / 2.3)
        g, sm = stair_ground(6), stair_smooth(6)
        x = lerp(STEP_C[5] - 40, PW1 + 140, ease(u))
        if u < 1:
            j, hy = walker2(ctx, x, g, sm, x * 1.0, s)
        else:
            spot(ctx, x, -300, PTOP, 80, 360, 0.3, WARM)
            j = placed2(ctx, x, PTOP, pmix(STAND, OPEN, ease((T - 22.9) / 0.8)), s, mix(FIG, WARM, 0.2))
    tagname(ctx, j, "YOU", s)
    fog(ctx, 0.1)
    grade(ctx, frame)


# ============================================================================ 3. LES DEUX BOUGIES
DESK_Y, FLOOR3 = 1250, 1500


def flame(ctx, x, y, h, w, T, seed, a=1.0):
    if h <= 1:
        return
    fl = 1 + 0.12 * math.sin(T * 23 + seed) + 0.08 * math.sin(T * 37 + seed * 2)
    h *= fl
    g = cairo.RadialGradient(x, y - h * 0.3, 0, x, y - h * 0.4, h)
    g.add_color_stop_rgba(0, 1, 0.98, 0.9, a)
    g.add_color_stop_rgba(0.5, 1, 0.8, 0.4, a)
    g.add_color_stop_rgba(1, 1, 0.5, 0.15, 0)
    ctx.set_source(g)
    sway = 6 * math.sin(T * 7 + seed)
    ctx.move_to(x + sway, y - h)
    ctx.curve_to(x + w, y - h * 0.45, x + w * 0.8, y, x, y)
    ctx.curve_to(x - w * 0.8, y, x - w, y - h * 0.45, x + sway, y - h)
    ctx.fill()


def world_candles(ctx, T, frame):
    camera(ctx, 590, 1010, 1.28 + 0.08 * ease(T / T_END))
    hours = 22 + T / T_END * 8.5
    dawn = ease((T - 18.5) / 4)
    sky(ctx, (0.08, 0.085, 0.1), (0.03, 0.03, 0.035))
    # fenetre
    g = cairo.LinearGradient(0, 380, 0, 820)
    g.add_color_stop_rgb(0, 0.04 + 0.4 * dawn, 0.05 + 0.3 * dawn, 0.1 + 0.25 * dawn)
    g.add_color_stop_rgb(1, 0.06 + 0.7 * dawn, 0.06 + 0.45 * dawn, 0.1 + 0.2 * dawn)
    ctx.set_source(g)
    ctx.rectangle(600, 380, 320, 440)
    ctx.fill()
    S1.stars(ctx, (1 - dawn) * 0.8, 800, seed=31)
    rgb(ctx, (0.18, 0.18, 0.2))
    ctx.set_line_width(14)
    ctx.rectangle(600, 380, 320, 440)
    ctx.move_to(760, 380)
    ctx.line_to(760, 820)
    ctx.move_to(600, 600)
    ctx.line_to(920, 600)
    ctx.stroke()
    if dawn > 0:
        ctx.set_source_rgba(1, 0.85, 0.6, 0.18 * dawn)
        ctx.move_to(600, 380)
        ctx.line_to(920, 380)
        ctx.line_to(700, FLOOR3)
        ctx.line_to(80, FLOOR3)
        ctx.close_path()
        ctx.fill()
    # horloge
    cxk, cyk = 260, 520
    rgb(ctx, (0.75, 0.75, 0.78))
    ctx.arc(cxk, cyk, 70, 0, 6.28)
    ctx.fill()
    rgb(ctx, (0.1, 0.1, 0.12))
    ctx.set_line_width(5)
    ctx.arc(cxk, cyk, 70, 0, 6.28)
    ctx.stroke()
    hh = hours % 12
    mm = (hours * 60) % 60
    for ang, ln, wdt in ((hh / 12 * 6.283, 38, 7), (mm / 60 * 6.283, 56, 4)):
        ctx.set_line_width(wdt)
        ctx.move_to(cxk, cyk)
        ctx.line_to(cxk + ln * math.sin(ang), cyk - ln * math.cos(ang))
        ctx.stroke()
    # bureau + chaise
    rgb(ctx, (0.2, 0.19, 0.18))
    ctx.rectangle(380, DESK_Y, 620, 26)
    ctx.rectangle(400, DESK_Y, 22, FLOOR3 - DESK_Y)
    ctx.rectangle(960, DESK_Y, 22, FLOOR3 - DESK_Y)
    ctx.rectangle(190, 1330, 170, 20)
    ctx.rectangle(200, 1350, 16, FLOOR3 - 1350)
    ctx.rectangle(336, 1350, 16, FLOOR3 - 1350)
    ctx.rectangle(190, 1120, 18, 220)
    ctx.fill()
    rgb(ctx, (0.25, 0.25, 0.27))
    ctx.move_to(-200, FLOOR3)
    ctx.line_to(W + 200, FLOOR3)
    ctx.set_line_width(4)
    ctx.stroke()
    # pile de feuilles
    pages = int(4 + T * 3.2)
    for k in range(pages):
        ctx.set_source_rgba(0.85, 0.85, 0.82, 1)
        ctx.rectangle(470 + (k % 3) * 1.5, DESK_Y - 4 - k * 4, 110, 4)
        ctx.fill()
    # bougies
    hm = max(0.0, 240 * (1 - T / 9.0))
    hd = 200 - 140 * T / T_END
    for cx_, hgt, wid, lab, big in ((720, hm, 46, "MOTIVATION", True), (880, hd, 30, "DISCIPLINE", False)):
        if hgt > 0:
            g = cairo.LinearGradient(cx_ - wid / 2, 0, cx_ + wid / 2, 0)
            g.add_color_stop_rgb(0, 0.95, 0.93, 0.88)
            g.add_color_stop_rgb(1, 0.6, 0.58, 0.55)
            ctx.set_source(g)
            ctx.rectangle(cx_ - wid / 2, DESK_Y - hgt, wid, hgt)
            ctx.fill()
        else:
            ctx.set_source_rgba(0.8, 0.78, 0.74, 1)
            ctx.save()
            ctx.translate(cx_, DESK_Y)
            ctx.scale(1, 0.25)
            ctx.arc(0, 0, 40, math.pi, 2 * math.pi)
            ctx.restore()
            ctx.fill()
        text(ctx, lab, cx_, DESK_Y + 60, 18, color=(0.75, 0.78, 0.84), spacing=3)
    # personnage
    s = 0.95
    if T < 21.5:
        speed = 9 if T < 9 else 4
        w_ = math.sin(T * speed)
        pose = P(t=168, la1=70, la2=95, ra1=55 + 12 * w_, ra2=88 + 10 * w_, ll1=88, ll2=0, rl1=84, rl2=-2)
        j = stick2(ctx, 300, 1330 - 14, pose, s, FIG)
    else:
        k = ease((T - 21.5) / 0.8)
        j = placed2(ctx, lerp(300, 420, k), FLOOR3, pmix(STAND, OPEN, ease((T - 22.3) / 0.8)), s,
                    mix(FIG, WARM, 0.25 * dawn))
    tagname(ctx, j, "YOU", s)
    # obscurite avec trous de lumiere
    light_m = 1.0 if hm > 0 else 0.0
    ctx.push_group()
    ctx.set_source_rgba(0.0, 0.0, 0.02, 0.86 * (1 - 0.75 * dawn))
    ctx.paint()
    ctx.set_operator(cairo.OPERATOR_DEST_OUT)
    for cx_, cy_, rad, a in ((720, DESK_Y - hm - 30, 900, 0.95 * light_m), (880, DESK_Y - hd - 20, 430, 0.85)):
        if a <= 0:
            continue
        g = cairo.RadialGradient(cx_, cy_, 0, cx_, cy_, rad)
        g.add_color_stop_rgba(0, 0, 0, 0, a)
        g.add_color_stop_rgba(1, 0, 0, 0, 0)
        ctx.set_source(g)
        ctx.paint()
    ctx.set_operator(cairo.OPERATOR_OVER)
    ctx.pop_group_to_source()
    ctx.paint()
    glow(ctx, 720, DESK_Y - hm - 30, 380, (1, 0.7, 0.35), 0.3 * light_m)
    glow(ctx, 880, DESK_Y - hd - 20, 200, (1, 0.7, 0.35), 0.28)
    flame(ctx, 720, DESK_Y - hm, 95 if hm > 0 else 0, 30, T, 1)
    flame(ctx, 880, DESK_Y - hd, 40, 13, T, 2)
    if 9 <= T < 12:
        k = (T - 9) / 3
        for q in range(5):
            yy = DESK_Y - 30 - k * 300 - q * 40
            ctx.set_source_rgba(0.7, 0.7, 0.72, 0.3 * (1 - k))
            ctx.arc(720 + 25 * math.sin(yy * 0.03 + T), yy, 12 + q * 4, 0, 6.28)
            ctx.fill()
    grade(ctx, frame, tint=(0.3, 0.2, 0.1), a=0.04)


# ============================================================================ 4. LE PONT
BR_Y, BR_L, BR_R, PL = 1250, 240, 1360, 70


def planks_you(T):
    return int(clamp((T - 3.5) / 1.0, 0, 16))


def world_bridge(ctx, T, frame):
    n = planks_you(T)
    xe_you = BR_L + n * PL
    if T < 19.6:
        xy = max(150, xe_you - 50)
    else:
        xy = lerp(xe_you - 50, BR_R + 180, ease((T - 19.6) / 1.9))
    cx = clamp(xy + 120, 540, 1200)
    cx = xy + 60
    z = 1.5
    cyc = BR_Y - 200
    if T > 21.8:
        e = ease((T - 21.8) / 2)
        cx, z, cyc = lerp(cx, 800, e), lerp(1.5, 0.62, e), lerp(BR_Y - 200, 1180, e)
    camera(ctx, cx, cyc, z)
    sky(ctx, (0.1, 0.11, 0.15), (0.02, 0.02, 0.03))
    glow(ctx, BR_R + 350, BR_Y - 300, 700, WARM, 0.35)
    # gouffre
    g = cairo.LinearGradient(0, BR_Y, 0, BR_Y + 1500)
    g.add_color_stop_rgb(0, 0.05, 0.055, 0.07)
    g.add_color_stop_rgb(1, 0.0, 0.0, 0.0)
    ctx.set_source(g)
    ctx.rectangle(BR_L, BR_Y, BR_R - BR_L, 2000)
    ctx.fill()
    for k in range(3):
        ctx.set_source_rgba(0.6, 0.65, 0.75, 0.05)
        ctx.rectangle(BR_L, BR_Y + 500 + k * 220, BR_R - BR_L, 140)
        ctx.fill()
    # falaises
    for x0, x1 in ((-2000, BR_L), (BR_R, 3500)):
        g = cairo.LinearGradient(0, BR_Y, 0, BR_Y + 1500)
        g.add_color_stop_rgb(0, 0.16, 0.17, 0.2)
        g.add_color_stop_rgb(1, 0.03, 0.03, 0.04)
        ctx.set_source(g)
        ctx.move_to(x0, BR_Y)
        ctx.line_to(x1, BR_Y)
        ctx.line_to(x1 + (-60 if x1 == BR_L else 0), BR_Y + 1500)
        ctx.line_to(x0, BR_Y + 1500)
        ctx.close_path()
        ctx.fill()
    S1.flag(ctx, BR_R + 330, BR_Y, T, h=240, col=WARM)
    text(ctx, "THE OTHER SIDE", BR_R + 330, BR_Y + 70, 22, color=(0.8, 0.8, 0.8), spacing=5)
    # pont abandonne de MOTIVATION (plus haut, en arriere-plan)
    nm = int(clamp((T - 4.5) / 0.55, 0, 5))
    for k in range(nm):
        rgb(ctx, (0.26, 0.24, 0.22))
        ctx.rectangle(BR_L + k * PL + 3, BR_Y - 70, PL - 6, 14)
        ctx.fill()
    # pont de YOU
    for k in range(n):
        g = cairo.LinearGradient(0, BR_Y - 8, 0, BR_Y + 12)
        g.add_color_stop_rgb(0, 0.55, 0.47, 0.38)
        g.add_color_stop_rgb(1, 0.3, 0.25, 0.2)
        ctx.set_source(g)
        ctx.rectangle(BR_L + k * PL + 2, BR_Y - 6, PL - 4, 18)
        ctx.fill()
    if n:
        ctx.set_source_rgba(0.7, 0.65, 0.55, 0.8)
        ctx.set_line_width(3)
        ctx.move_to(BR_L, BR_Y - 90)
        ctx.line_to(BR_L + n * PL, BR_Y - 90)
        ctx.stroke()
        for k in range(n + 1):
            ctx.move_to(BR_L + k * PL, BR_Y - 90)
            ctx.line_to(BR_L + k * PL, BR_Y)
            ctx.stroke()
    s = 0.88
    flat = (lambda _x: BR_Y)
    # EGO saute
    if T < 3.2:
        xe = -200 + 130 * T
        j, _ = walker2(ctx, xe, flat, flat, xe * 1.6, s, (0.8, 0.6, 0.6), lean=160, run=True, arm=50)
        tagname(ctx, j, "EGO", s, col=(0.9, 0.5, 0.5))
    elif T < 4.8:
        u = (T - 3.2) / 1.6
        x = -200 + 130 * 3.2 + 260 * u
        y = BR_Y - 120 - 160 * math.sin(math.pi * min(u * 1.6, 1)) + (900 * max(0, u - 0.45) ** 2) * 4
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(u * 3)
        stick2(ctx, 0, 0, pmix(E.run_pose(0), E.LYING, u), s * (1 - 0.4 * u), (0.8, 0.6, 0.6), 1 - u * 0.6)
        ctx.restore()
    # MOTIVATION construit 5 planches puis repart
    if T < 7.5:
        j = placed2(ctx, BR_L - 40 + nm * PL * 0.5, BR_Y - 64, BEND if (T * 3) % 1 < 0.5 else STAND, s * 0.85,
                    FIG_DIM)
        tagname(ctx, j, "MOTIVATION", s * 0.85)
    elif T < 11:
        xm = BR_L - 40 + 5 * PL * 0.5 - 150 * (T - 7.5)
        j, _ = walker2(ctx, xm, lambda _x: BR_Y - 64, lambda _x: BR_Y - 64, 150 * (T - 7.5), s * 0.85, FIG_DIM,
                       facing=-1)
        tagname(ctx, j, "MOTIVATION", s * 0.85, alpha=clamp(11 - T))
    # YOU
    if T < 19.6:
        cyc = (T - 3.5) % 1.0
        if T < 3.5:
            j = placed2(ctx, xy, BR_Y, STAND, s)
        elif cyc < 0.45:
            j = placed2(ctx, xy, BR_Y, BEND, s)
        else:
            j, _ = walker2(ctx, xy, flat, flat, T * 120, s)
    elif T < 21.5:
        j, _ = walker2(ctx, xy, flat, flat, xy, s)
    else:
        spot(ctx, xy, -300, BR_Y, 80, 360, 0.3, WARM)
        j = placed2(ctx, xy, BR_Y, pmix(STAND, OPEN, ease((T - 21.5) / 0.8)), s, mix(FIG, WARM, 0.25))
    tagname(ctx, j, "YOU", s)
    fog(ctx, 0.12, 1500)
    grade(ctx, frame)


# ============================================================================ 5. LES CHAINES
CH_FLOOR = 1450
BREAKS = [6.5, 10.5, 17.6]
ANCH = [("COMFORT", 150, CH_FLOOR - 60), ("YOUR PHONE", 60, CH_FLOOR - 240), ("EXCUSES", 260, CH_FLOOR - 50)]


def chain(ctx, ax, ay, bx, by, a=1.0, sag=0.0):
    ln = math.hypot(bx - ax, by - ay)
    n = max(2, int(ln / 24))
    ang = math.atan2(by - ay, bx - ax)
    for i in range(n):
        u = i / (n - 1)
        x = lerp(ax, bx, u)
        y = lerp(ay, by, u) + sag * 4 * u * (1 - u)
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(ang)
        ctx.scale(1, 0.55 if i % 2 == 0 else 0.2)
        ctx.set_source_rgba(0.68, 0.7, 0.75, a)
        ctx.set_line_width(5 if i % 2 == 0 else 9)
        ctx.arc(0, 0, 15, 0, 6.28)
        ctx.stroke()
        ctx.restore()


def world_chains(ctx, T, frame):
    broken = sum(1 for b in BREAKS if T >= b)
    hit = max([clamp(1 - (T - b) / 0.35) for b in BREAKS if T >= b] + [0])
    if T < 18:
        xy = 470 + 40 * broken + 6 * math.sin(T * 3)
    else:
        xy = 470 + 120 + 380 * (T - 18) + 30 * (T - 18) ** 2
    cx = max(330, xy - 150)
    camera(ctx, cx, CH_FLOOR - 270, 1.4 + 0.05 * hit, shake=16 * hit, frame=frame)
    sky(ctx, (0.1, 0.11, 0.14), (0.02, 0.02, 0.03))
    glow(ctx, 2600, 1100, 1300, WARM, 0.25 + 0.35 * ease((T - 18) / 3))
    rgb(ctx, (0.08, 0.085, 0.1))
    ctx.rectangle(-1000, CH_FLOOR, 6000, 800)
    ctx.fill()
    rgb(ctx, (0.3, 0.32, 0.37))
    ctx.set_line_width(4)
    ctx.move_to(-1000, CH_FLOOR)
    ctx.line_to(5000, CH_FLOOR)
    ctx.stroke()
    spot(ctx, 300, -300, CH_FLOOR, 100, 700, 0.15)
    # ancres
    rgb(ctx, (0.25, 0.25, 0.3))
    S1.rrect(ctx, 20, CH_FLOOR - 150, 290, 110, 20)
    ctx.fill()
    S1.rrect(ctx, 20, CH_FLOOR - 230, 60, 190, 20)
    ctx.fill()
    S1.rrect(ctx, 250, CH_FLOOR - 230, 60, 190, 20)
    ctx.fill()
    rgb(ctx, (0.12, 0.12, 0.14))
    S1.rrect(ctx, 0, CH_FLOOR - 470, 120, 230, 18)
    ctx.fill()
    glow(ctx, 60, CH_FLOOR - 355, 160, (0.5, 0.7, 1), 0.35)
    ctx.set_source_rgba(0.45, 0.65, 0.95, 0.9)
    S1.rrect(ctx, 10, CH_FLOOR - 455, 100, 195, 10)
    ctx.fill()
    g = cairo.RadialGradient(250, CH_FLOOR - 90, 5, 270, CH_FLOOR - 70, 80)
    g.add_color_stop_rgb(0, 0.5, 0.52, 0.56)
    g.add_color_stop_rgb(1, 0.1, 0.1, 0.12)
    ctx.set_source(g)
    ctx.arc(270, CH_FLOOR - 70, 70, 0, 6.28)
    ctx.fill()
    for lab, ax, ay in ANCH:
        text(ctx, lab, ax + 60, ay - (90 if lab == "YOUR PHONE" else 120), 18, color=(0.78, 0.8, 0.86), spacing=3)
    # personnage
    s = 0.95
    flat = (lambda _x: CH_FLOOR)
    if T < 2.2:
        j = placed2(ctx, xy, CH_FLOOR, STAND, s)
    elif T < 18:
        j, hy = walker2(ctx, xy, flat, flat, T * 90, s, lean=142, arm=10, stride=18,
                        arms=dict(la1=-60, la2=-20, ra1=-50, ra2=-15))
    elif T < 22.5:
        j, hy = walker2(ctx, xy, flat, flat, xy, s, lean=160, run=True, arm=50)
    else:
        j = placed2(ctx, xy, CH_FLOOR, pmix(STAND, OPEN, ease((T - 22.5) / 0.8)), s, mix(FIG, WARM, 0.3))
    tagname(ctx, j, "YOU", s)
    hipx, hipy = j["hip"]
    for i, (lab, ax, ay) in enumerate(ANCH):
        if T < BREAKS[i]:
            chain(ctx, ax + 60, ay, hipx - 10, hipy + 10 + i * 12, sag=10 if T < 2.2 else 0)
        elif T < BREAKS[i] + 1.2:
            k = (T - BREAKS[i]) / 1.2
            mx = lerp(ax + 60, hipx, 0.5)
            chain(ctx, ax + 60, ay, mx - 60 * k, lerp(ay, CH_FLOOR - 8, ease(k)), a=1 - 0.3 * k)
            S1.particles(ctx, mx, (ay + hipy) / 2, k, i * 31, n=26, spread=420, up=420, col=(1, 0.85, 0.5),
                         size=(2, 5))
        else:
            mx = lerp(ax + 60, 470, 0.5)
            chain(ctx, ax + 60, ay, mx - 60, CH_FLOOR - 8, a=0.7)
    fog(ctx, 0.1)
    flash(ctx, 0.35 * hit)
    grade(ctx, frame)


# ============================================================================ scenes communes
def scene_quote2(ctx, t, frame, v):
    ctx.save()
    v["world"](ctx, T_END, frame)
    ctx.restore()
    ctx.save()
    ctx.identity_matrix()
    ctx.set_source_rgba(0, 0, 0.01, 0.66)
    ctx.paint()
    l1, l2 = v["quote"]
    n = int(clamp(t / 0.9) * len(l1))
    s1 = S1.fit_size(ctx, l1, 50, 960, spacing=8)
    text(ctx, l1[:n], W / 2, 900, s1, color=(0.85, 0.87, 0.92), spacing=8)
    if t > 1.1:
        k = clamp((t - 1.1) / 0.25)
        sc = lerp(1.6, 1.0, ease_out(k))
        r = random.Random(frame)
        sh = (1 - k) * 20
        s2 = S1.fit_size(ctx, l2, 104, 980, spacing=8)
        glow(ctx, W / 2, 1010, 420, (0.8, 0.85, 1), 0.18 * k)
        ctx.translate(W / 2 + r.uniform(-sh, sh), 1050 + r.uniform(-sh, sh))
        ctx.scale(sc, sc)
        text(ctx, l2, 0, 0, s2, color=WHITE, alpha=k, spacing=8)
    ctx.restore()
    ctx.save()
    ctx.identity_matrix()
    E.vignette(ctx, 0.7)
    if t > v["dur_quote"] - 0.6:
        ctx.set_source_rgba(0, 0, 0, clamp((t - v["dur_quote"] + 0.6) / 0.6))
        ctx.paint()
    ctx.restore()


VIDEOS = [
    dict(key="01_la_tempete", world=world_storm,
         captions=[(0.3, 3.6, "EVERYONE STARTS WHEN THE SKY IS CLEAR."), (4.0, 6.6, "THEN THE STORM COMES."),
                   (6.8, 9.6, "MOTIVATION TURNS BACK."), (9.8, 12.4, "EGO SAYS IT'S UNFAIR."),
                   (12.6, 15, "DISCIPLINE KEEPS WALKING."), (15.4, 18.6, "THE RAIN DOESN'T STOP."),
                   (18.8, 21.6, "YOU JUST GET STRONGER."), (21.9, 24, "THE STORM ENDS. YOU DON'T.")],
         rock=(["KEEP", "WALKING"], "KEEP WALKING"), quote=("THE STORM DOESN'T CARE.", "KEEP WALKING.")),
    dict(key="02_les_mots", world=world_words,
         captions=[(0.3, 3.0, "YOU FELL. EVERYONE WATCHED."), (3.2, 6.2, "THEN THEY STARTED THROWING WORDS."),
                   (6.4, 9.6, "HEAVY ONES."), (10.0, 13.0, "SO YOU PICKED THEM UP."),
                   (13.2, 15, "ONE BY ONE."), (15.3, 18.3, "EVERY INSULT BECAME A STEP."),
                   (18.5, 21.2, "EVERY DOUBT, A LITTLE HIGHER."), (21.5, 24, "THANK THEM.")],
         rock=(["IT'S", "YOU", "VS", "YOU"], "IT'S YOU VS YOU"), quote=("THEY THREW STONES.", "YOU BUILT STAIRS.")),
    dict(key="03_les_bougies", world=world_candles,
         captions=[(0.3, 3.4, "EVERY NIGHT YOU LIGHT TWO CANDLES."), (3.6, 6.6, "ONE BURNS BRIGHT."),
                   (6.8, 9.0, "YOU FEEL UNSTOPPABLE."), (9.2, 12.2, "THEN IT DIES. FAST."),
                   (12.4, 15, "THE OTHER ONE IS SMALL."), (15.3, 18.5, "BUT IT NEVER GOES OUT."),
                   (18.8, 21.6, "NOT AT 3 AM. NOT AT 5 AM."), (21.9, 24, "MORNING ALWAYS COMES.")],
         rock=(["NEVER", "GO", "OUT"], "NEVER GO OUT"),
         quote=("MOTIVATION BURNS BRIGHT.", "DISCIPLINE BURNS LONG.")),
    dict(key="04_le_pont", world=world_bridge,
         captions=[(0.3, 3.0, "THE OTHER SIDE LOOKED IMPOSSIBLE."), (3.2, 5.4, "EGO TRIED TO JUMP."),
                   (5.6, 8.6, "MOTIVATION STARTED A BRIDGE..."), (8.8, 11.2, "...AND LEFT IT."),
                   (11.4, 15, "YOU LAID ONE PLANK A DAY."), (15.3, 18.4, "NOBODY CLAPS FOR ONE PLANK."),
                   (18.6, 21.4, "BUT PLANKS BECOME BRIDGES."), (21.7, 24, "AND BRIDGES TAKE YOU ACROSS.")],
         rock=(["ONE", "PLANK", "A DAY"], "ONE PLANK A DAY"), quote=("DON'T JUMP.", "BUILD.")),
    dict(key="05_les_chaines", world=world_chains,
         captions=[(0.3, 3.0, "YOU'RE NOT LAZY."), (3.2, 6.3, "YOU'RE CHAINED."), (6.5, 8.6, "TO COMFORT."),
                   (8.8, 10.4, "TO YOUR PHONE."), (10.6, 13.2, "TO EVERY EXCUSE."),
                   (13.4, 15, "SO EVERY DAY, YOU PULL."), (15.3, 17.4, "A LITTLE HARDER."),
                   (17.6, 20, "UNTIL ONE DAY..."), (20.2, 24, "NOTHING HOLDS YOU.")],
         rock=(["BREAK", "FREE"], "BREAK FREE"), quote=("YOU'RE NOT STUCK.", "BREAK THE CHAIN.")),
]

DUR = dict(p1=T_SPLIT, rock=3.6, p2=T_END - T_SPLIT, quote=3.4)


def build_scenes(v):
    v["dur_quote"] = DUR["quote"]

    def part(t0):
        def fn(ctx, t, frame):
            T = t0 + t
            ctx.save()
            v["world"](ctx, T, frame)
            ctx.restore()
            top_caption(ctx, v["captions"], T)
        return fn

    return [("p1", DUR["p1"], part(0.0)),
            ("rock", DUR["rock"], lambda c, t, f: S1.scene_rock(c, t, f, v)),
            ("p2", DUR["p2"], part(T_SPLIT)),
            ("quote", DUR["quote"], lambda c, t, f: scene_quote2(c, t, f, v))]


def build_music(speed, out):
    total = sum(DUR.values())
    bounds = [(0, 9.0), (9.0, DUR["p1"] + DUR["rock"]), (DUR["p1"] + DUR["rock"], total)]
    files = ["piano_intro.mp3", "m3_climax.mp3", "m4_drop.mp3"]
    inputs, filt, labels = [], [], []
    for i, (f, (a, b)) in enumerate(zip(files, bounds)):
        inputs += ["-stream_loop", "-1", "-i", os.path.join(SND, f)]
        start, ln = a / speed, (b - a) / speed
        last = i == len(files) - 1
        filt.append(f"[{i}:a]atrim=0:{ln + 0.45:.3f},afade=t=in:d={0.05 if i == 0 else 0.4},"
                    f"afade=t=out:st={max(0.1, ln - (1.6 if last else 0.05)):.3f}:d={1.6 if last else 0.5},"
                    f"adelay={int(start * 1000)}|{int(start * 1000)}[m{i}]")
        labels.append(f"[m{i}]")
    filt.append("".join(labels) + f"amix=inputs={len(files)}:normalize=0,atrim=0:{total / speed:.3f},"
                "loudnorm=I=-14:TP=-1.5[out]")
    subprocess.check_call(["ffmpeg", "-y", "-v", "error"] + inputs + ["-filter_complex", ";".join(filt),
                          "-map", "[out]", "-ar", "44100", "-c:a", "aac", "-b:a", "192k", out])


def render_video(idx, speed=1.0, mb=3, outdir="output/serie2", preview=False):
    v = VIDEOS[idx]
    scenes = build_scenes(v)
    total = sum(s_[1] for s_ in scenes)
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surface)
    os.makedirs(outdir, exist_ok=True)
    if preview:
        from PIL import Image
        times = [0.15 + i * (total - 0.3) / 19 for i in range(20)]
        sheet = Image.new("RGB", (216 * 10, 384 * 2))
        for i, tt in enumerate(times):
            S1.render_frame(ctx, scenes, tt, int(tt * FPS))
            surface.flush()
            arr = np.ndarray((H, W, 4), np.uint8, surface.get_data())
            sheet.paste(Image.fromarray(arr[..., [2, 1, 0]].copy()).resize((216, 384)),
                        ((i % 10) * 216, (i // 10) * 384))
        out = os.path.join(outdir, f"{v['key']}_preview.png")
        sheet.save(out)
        return out
    suffix = "" if speed == 1 else f"_x{speed:g}"
    out = os.path.join(outdir, f"{v['key']}{suffix}.mp4")
    music = os.path.join(outdir, f".{v['key']}{suffix}.m4a")
    build_music(speed, music)
    n_frames = int(total * FPS / speed)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-i", music, "-map", "0:v", "-map", "1:a", "-c:a", "copy", "-shortest",
           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
           out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(n_frames):
        gt = f / FPS * speed
        acc = None
        for k in range(mb):
            S1.render_frame(ctx, scenes, gt + ((k / mb - 0.5) * 0.7 / FPS * speed if mb > 1 else 0), f)
            surface.flush()
            a = np.ndarray((H, W, 4), np.uint8, surface.get_data())
            if mb == 1:
                acc = a
                break
            acc = a.astype(np.uint16) if acc is None else acc + a
        proc.stdin.write((acc if mb == 1 else (acc // mb).astype(np.uint8)).tobytes())
    proc.stdin.close()
    proc.wait()
    os.remove(music)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", default="all")
    ap.add_argument("--speed", type=float, default=1.0)
    ap.add_argument("--mb", type=int, default=3)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--outdir", default="output/serie2")
    args = ap.parse_args()
    ids = list(range(len(VIDEOS))) if args.video == "all" else [int(x) - 1 for x in args.video.split(",")]
    if len(ids) == 1 or args.jobs == 1:
        for i in ids:
            print(render_video(i, args.speed, args.mb, args.outdir, args.preview), flush=True)
        return
    from multiprocessing import Pool
    with Pool(args.jobs) as pool:
        for out in pool.starmap(render_video, [(i, args.speed, args.mb, args.outdir, args.preview) for i in ids]):
            print(out, flush=True)


if __name__ == "__main__":
    main()
