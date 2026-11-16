#!/usr/bin/env python3
"""
Serie de 10 videos motivation "stickman" : MOTIVATION / TALENT / DISCIPLINE.

Chaque video : intro (titre) -> 1re partie du defi -> carte definition du dictionnaire
-> photo motivation du rocher (comme la 1re video) -> 2e partie (la discipline gagne)
-> phrase finale.  La motivation demarre fort puis ralentit et abandonne, le talent
s'arrete, la discipline garde le meme rythme jusqu'au bout.

    python3 generator/series.py --video all            # les 10 videos (x1.5)
    python3 generator/series.py --video 3 --speed 1    # une seule, vitesse normale
    python3 generator/series.py --video all --preview  # planches de captures
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
from ego_video import (W, H, FPS, MONO, SERIF, WHITE, RED, P, pmix, stick, text, glow, tag,  # noqa: E402,F401
                       vignette, grain, ik, clamp, lerp, ease, ease_out, ease_in, back_out, mix, rgb,
                       d, camera, calendar, ground_hip_y, joints)

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SND = os.path.join(ROOT, "assets", "sons")

MOTI_C = (0.66, 0.66, 0.67)
TALE_C = (0.5, 0.5, 0.52)
DISC_C = WHITE
BG = (0.07, 0.07, 0.075)

T_SPLIT = 15.0   # fin de la 1re partie (temps du "monde")
T_END = 26.0     # fin de la 2e partie

SIT = P(t=163, la1=55, la2=105, ra1=45, ra2=95, ll1=125, ll2=25, rl1=118, rl2=18)
SLEEP = P(t=90, la1=-80, la2=-86, ra1=-84, ra2=-80, ll1=-90, ll2=-92, rl1=-88, rl2=-88)
STAND = P(la1=-10, la2=-6, ra1=10, ra2=6, ll1=-8, ll2=-5, rl1=8, rl2=5)
CHEER = E.CHEER


# ============================================================================ helpers
def rrect(ctx, x, y, w, h, r):
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path()


def fit_size(ctx, s, size, maxw, family=MONO, bold=True, spacing=0):
    E.font(ctx, family, size, bold)
    w = E.text_width(ctx, s, spacing)
    return size if w <= maxw else size * maxw / w


def bubble(ctx, x, y, s, a=1.0, size=24):
    if a <= 0:
        return
    E.font(ctx, MONO, size, True)
    w = E.text_width(ctx, s, 1) + 36
    h = size * 1.85
    bx, by = x - w / 2, y - h - 18
    ctx.set_source_rgba(0.95, 0.95, 0.95, a)
    rrect(ctx, bx, by, w, h, 14)
    ctx.fill()
    ctx.move_to(x - 12, by + h - 1)
    ctx.line_to(x, y)
    ctx.line_to(x + 12, by + h - 1)
    ctx.close_path()
    ctx.fill()
    text(ctx, s, x, by + h * 0.68, size, color=(0.06, 0.06, 0.06), alpha=a, spacing=1)


def fade_win(T, t0, t1, f=0.25):
    if T < t0 or T > t1:
        return 0.0
    return clamp(min((T - t0) / f, (t1 - T) / f))


def zzz(ctx, x, y, T, a=1.0):
    for i in range(3):
        k = (T * 0.7 + i / 3) % 1
        text(ctx, "z", x + 30 * k + i * 6, y - 90 * k, 22 + 16 * k, color=(0.85, 0.85, 0.85),
             alpha=a * (1 - k))


def name_tag(ctx, j, x, y, name, col=(0.82, 0.82, 0.83), s=1.0, size=19, alpha=1.0):
    hx, hy = x + j["head"][0], y + j["head"][1]
    text(ctx, name, hx, hy - 48 * s, size, color=col, spacing=3, alpha=alpha)


def hud(ctx, day=None, label=None, value=None, y=210, s=0.85, alpha=1.0):
    ctx.save()
    ctx.identity_matrix()
    if day is not None:
        calendar(ctx, W / 2, y, str(day), s=s)
    if label:
        text(ctx, f"{label}   {value}", W / 2, y + 190 * s + 20, 38, color=(0.93, 0.93, 0.93), spacing=6,
             alpha=alpha)
    ctx.restore()


def walker(ctx, hipx, ground, smooth, dist, s, col, lean=172, stride=26, lift=16, arm=34, alpha=1.0,
           hip_h=104, shadow=True, run=False):
    """Bonhomme qui marche/court : pieds poses au sol (IK) sur n'importe quel terrain."""
    L = stride * s
    ph = dist / (4 * L) * 2 * math.pi
    hipy = smooth(hipx) - hip_h * s + 4 * s * math.cos(2 * ph)
    pose = {"t": lean}
    for side, off in (("l", 0.0), ("r", math.pi)):
        u = ((ph + off) / (2 * math.pi)) % 1
        if u < 0.5:
            fx = hipx + L - 4 * L * u
            lf = 0.0
        else:
            fx = hipx - L + 4 * L * (u - 0.5)
            lf = math.sin(math.pi * (u - 0.5) * 2) * lift * s
        fy = ground(fx) - lf - 5 * s
        a1, a2 = ik(hipx, hipy, fx, fy, 58 * s, 58 * s, (1, 0))
        pose[side + "l1"], pose[side + "l2"] = a1, a2
    c = math.cos(ph)
    bend = 80 if run else 35
    pose["la1"], pose["la2"] = -arm * c, -arm * c + bend
    pose["ra1"], pose["ra2"] = arm * c, arm * c + bend
    j = stick(ctx, hipx, hipy, pose, s, fill=col, alpha=alpha, shadow=ground(hipx) if shadow else None)
    return j, hipy


def placed(ctx, x, ground_y, pose, s, col, alpha=1.0, shadow=True):
    hy = ground_hip_y(pose, s, ground_y)
    j = stick(ctx, x, hy, pose, s, fill=col, alpha=alpha, shadow=ground_y if shadow else None)
    return j, hy


def flag(ctx, x, y, T, h=220, col=RED):
    rgb(ctx, (0.75, 0.75, 0.76))
    ctx.set_line_width(7)
    ctx.move_to(x, y)
    ctx.line_to(x, y - h)
    ctx.stroke()
    rgb(ctx, col)
    ctx.move_to(x, y - h)
    for i in range(9):
        k = i / 8
        ctx.line_to(x + 120 * k, y - h + 8 * math.sin(T * 6 + k * 5) + 30 * k)
    for i in range(9):
        k = 1 - i / 8
        ctx.line_to(x + 120 * k, y - h + 75 + 8 * math.sin(T * 6 + k * 5) - 30 * k)
    ctx.close_path()
    ctx.fill()


def stars(ctx, a=1.0, y1=900, seed=9):
    r = random.Random(seed)
    for _ in range(70):
        x, y = r.uniform(-300, W + 300), r.uniform(-600, y1)
        ctx.set_source_rgba(1, 1, 1, a * r.uniform(0.15, 0.6))
        ctx.arc(x, y, r.uniform(1, 2.6), 0, 6.28)
        ctx.fill()


def particles(ctx, x, y, age, seed, n=14, spread=260, up=380, col=(0.75, 0.75, 0.75), size=(3, 7), g=1400):
    if not 0 <= age <= 1:
        return
    r = random.Random(seed)
    tt = age * 0.7
    for _ in range(n):
        vx = r.uniform(-spread, spread)
        vy = -r.uniform(up * 0.4, up)
        px, py = x + vx * tt, y + vy * tt + 0.5 * g * tt * tt
        ctx.set_source_rgba(col[0], col[1], col[2], 1 - age)
        ctx.arc(px, py, r.uniform(*size), 0, 6.28)
        ctx.fill()


def gem(ctx, x, y, r, rot=0.0, a=1.0, sparkle=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    glow(ctx, 0, 0, r * (2.2 + 2 * sparkle), (0.55, 0.85, 1.0), (0.25 + 0.4 * sparkle) * a)
    pts = [(-r, -0.25 * r), (-0.55 * r, -0.7 * r), (0.55 * r, -0.7 * r), (r, -0.25 * r), (0, r)]
    ctx.move_to(*pts[0])
    for p_ in pts[1:]:
        ctx.line_to(*p_)
    ctx.close_path()
    g = cairo.LinearGradient(-r, -r, r, r)
    g.add_color_stop_rgba(0, 0.85, 0.97, 1, a)
    g.add_color_stop_rgba(0.5, 0.45, 0.78, 0.98, a)
    g.add_color_stop_rgba(1, 0.2, 0.5, 0.85, a)
    ctx.set_source(g)
    ctx.fill_preserve()
    ctx.set_source_rgba(1, 1, 1, 0.8 * a)
    ctx.set_line_width(2)
    ctx.stroke()
    ctx.move_to(-r, -0.25 * r)
    ctx.line_to(r, -0.25 * r)
    ctx.move_to(-0.3 * r, -0.25 * r)
    ctx.line_to(0, r)
    ctx.line_to(0.3 * r, -0.25 * r)
    ctx.stroke()
    if sparkle > 0:
        ctx.set_source_rgba(1, 1, 1, sparkle * a)
        for ang in (0, math.pi / 2):
            ctx.save()
            ctx.rotate(ang + rot * 3)
            ctx.move_to(-r * 1.6, 0)
            ctx.line_to(0, -4)
            ctx.line_to(r * 1.6, 0)
            ctx.line_to(0, 4)
            ctx.close_path()
            ctx.fill()
            ctx.restore()
    ctx.restore()


def finish_line(ctx, fx, top, bottom):
    rgb(ctx, (0.7, 0.7, 0.7))
    ctx.set_line_width(5)
    ctx.move_to(fx, top - 400)
    ctx.line_to(fx, top)
    ctx.stroke()
    rgb(ctx, (0.85, 0.85, 0.85))
    ctx.rectangle(fx - 85, top - 440, 170, 54)
    ctx.fill()
    text(ctx, "FINISH", fx, top - 400, 30, color=(0.08, 0.08, 0.08), spacing=4)
    ctx.set_line_width(9)
    n = int((bottom - top) / 40)
    for i in range(n):
        rgb(ctx, (0.85, 0.85, 0.85) if i % 2 == 0 else (0.25, 0.25, 0.25))
        ctx.move_to(fx + i * 6, top + i * 40)
        ctx.line_to(fx + (i + 1) * 6, top + (i + 1) * 40)
        ctx.stroke()


# ============================================================================ 1. ESCALIERS
ST_W, ST_H, ST_X0, ST_Y0, ST_TOP = 60, 34, -300, 1650, 36
ST_LANES = [(-440, MOTI_C, "MOTIVATION", 0.075), (-220, TALE_C, "TALENT", 0.095), (0, DISC_C, "DISCIPLINE", 0.12)]


def st_ground(dy):
    def g(x):
        k = max(0, min(ST_TOP, math.floor((x - ST_X0) / ST_W)))
        return ST_Y0 + dy - k * ST_H
    return g


def st_smooth(dy):
    def g(x):
        k = clamp((x - ST_X0) / ST_W - 0.5, 0, ST_TOP)
        return ST_Y0 + dy - k * ST_H
    return g


def st_pos(i, T):
    if i == 0:
        return 4.2 * 2.4 * (1 - math.exp(-T / 2.4)), T < 6.6
    if i == 1:
        return 2.3 * min(T, 5.5), T < 5.5
    p = min(1.56 * T, ST_TOP + 0.6)
    return p, p < ST_TOP + 0.6


def world_stairs(ctx, T, frame):
    s = 0.85
    xs = [ST_X0 + (st_pos(i, T)[0] + 0.5) * ST_W for i in range(3)]
    dx = xs[2]
    dy_ = st_smooth(0)(dx) - 230
    k = ease((T - 4) / 4)
    fx = lerp(sum(xs) / 3 + 120, dx + 120, k)
    fy = lerp(st_smooth(0)(sum(xs) / 3) - 420, dy_ - 120, k)
    z = 1.05
    if T > 23.5:
        e = ease((T - 23.5) / 2.2)
        fx = lerp(fx, ST_X0 + ST_TOP * ST_W / 2 + 160, e)
        fy = lerp(fy, ST_Y0 - ST_TOP * ST_H / 2 - 330, e)
        z = lerp(1.05, 0.45, e)
    camera(ctx, fx, fy, z)
    rgb(ctx, BG)
    ctx.paint()
    glow(ctx, fx, fy - 300, 1100, (1, 1, 1), 0.06)
    top_x = ST_X0 + (ST_TOP + 1) * ST_W
    if T > 21:
        glow(ctx, top_x + 200, ST_Y0 - ST_TOP * ST_H - 200, 700, RED, 0.3 * ease((T - 21) / 3))
    for i, (dy, col, name, shade) in enumerate(ST_LANES):
        y0 = ST_Y0 + dy
        ctx.move_to(ST_X0 - 900, y0 + 4000)
        ctx.line_to(ST_X0 - 900, y0)
        for kk in range(ST_TOP):
            ctx.line_to(ST_X0 + (kk + 1) * ST_W, y0 - kk * ST_H)
            ctx.line_to(ST_X0 + (kk + 1) * ST_W, y0 - (kk + 1) * ST_H)
        ctx.line_to(ST_X0 + ST_TOP * ST_W + 3000, y0 - ST_TOP * ST_H)
        ctx.line_to(ST_X0 + ST_TOP * ST_W + 3000, y0 + 4000)
        ctx.close_path()
        rgb(ctx, (shade, shade, shade + 0.01))
        ctx.fill_preserve()
        rgb(ctx, (shade + 0.22, shade + 0.22, shade + 0.23))
        ctx.set_line_width(3)
        ctx.stroke()
        if i == 2:
            flag(ctx, top_x + 260, y0 - ST_TOP * ST_H, T)
            text(ctx, "THE TOP", top_x + 260, y0 - ST_TOP * ST_H + 70, 34, color=(0.5, 0.5, 0.5), spacing=6)
        p, moving = st_pos(i, T)
        x = ST_X0 + (p + 0.5) * ST_W
        g, sm = st_ground(dy), st_smooth(dy)
        if moving:
            fast = i == 0 and T < 4
            j, hy = walker(ctx, x, g, sm, p * ST_W, s, col, lean=160 if fast else 172, hip_h=96,
                           run=fast, arm=50 if fast else 32)
        elif i == 2:
            pose = pmix(STAND, CHEER, ease((T - 23.4) / 0.4))
            glow(ctx, x, g(x) - 150, 260, RED, 0.35)
            j, hy = placed(ctx, x, g(x), pose, s, mix(WHITE, RED, ease((T - 23.4) / 1.0)))
        else:
            j, hy = placed(ctx, x, g(x), SIT, s, col)
        name_tag(ctx, j, x, hy, name, RED if i == 2 and T > 23.4 else (0.82, 0.82, 0.83))
        hx, hh = x + j["head"][0], hy + j["head"][1]
        if i == 0:
            bubble(ctx, hx, hh - 70, "I'LL CONTINUE TOMORROW...", fade_win(T, 7.0, 10.5))
            bubble(ctx, hx, hh - 70, "TOO TIRED...", fade_win(T, 15.5, 19))
        if i == 1:
            bubble(ctx, hx, hh - 70, "I'M GOOD ENOUGH.", fade_win(T, 5.8, 9.0))
            if T > 9.3:
                zzz(ctx, hx + 30, hh - 30, T)
    hud(ctx, min(365, 1 + int(T * 14.5)), "STEPS", f"{int(st_pos(2, T)[0] * 280):,}")


# ============================================================================ 2. TROU / DIAMANTS
DG_SY, DG_DY, DG_X, DG_HW = 700, 2200, [210, 540, 870], 82
DIG_DOWN = P(t=140, la1=55, la2=28, ra1=45, ra2=18, ll1=-15, ll2=-25, rl1=25, rl2=0)
DIG_UP = P(t=178, la1=-150, la2=-118, ra1=-140, ra2=-108, ll1=-10, ll2=-5, rl1=12, rl2=5)


def dig_state(i, T):
    if i == 0:
        return 520 * (1 - math.exp(-T / 2.0)), T < 6.2, 3.3
    if i == 1:
        return min(118 * T, 1462), 118 * T < 1462, 2.4
    target = DG_DY - DG_SY + 6
    return min(68 * T, target), 68 * T < target, 1.9


def digger(ctx, x, yb, T, f, s, col, active):
    c = f * T
    u = 0.5 - 0.5 * math.cos(2 * math.pi * c) if active else 0.0
    pose = pmix(DIG_DOWN, DIG_UP, u)
    j, hy = placed(ctx, x, yb, pose, s, col, shadow=False)
    hx_, hy_ = x + j["rh"][0], hy + j["rh"][1]
    ang = lerp(18, -140, u)
    sx, sy = d(ang)
    ln = 105 * s
    ex, ey = hx_ + sx * ln, hy_ + sy * ln
    rgb(ctx, (0.55, 0.45, 0.35))
    ctx.set_line_width(7 * s)
    ctx.move_to(hx_ - sx * 25 * s, hy_ - sy * 25 * s)
    ctx.line_to(ex, ey)
    ctx.stroke()
    ctx.save()
    ctx.translate(ex, ey)
    ctx.rotate(-math.radians(ang))
    rgb(ctx, (0.7, 0.7, 0.72))
    rrect(ctx, -16 * s, 0, 32 * s, 40 * s, 6 * s)
    ctx.fill()
    ctx.restore()
    if active:
        fr = c % 1
        if fr > 0.5:
            particles(ctx, ex, ey, (fr - 0.5) * 2, int(c) * 7 + int(x), n=10, spread=160, up=900,
                      col=(0.42, 0.35, 0.28), size=(4, 9))
    return j, hy


def world_dig(ctx, T, frame):
    s = 0.8
    dd = dig_state(2, T)[0]
    cy = max(1000, DG_SY + dd - 80)
    z = 1.0
    if T > 22.3:
        e = ease((T - 22.3) / 2.0)
        cy = lerp(cy, (DG_SY + DG_DY) / 2 + 180, e)
        z = lerp(1.0, 0.6, e)
    camera(ctx, W / 2, cy, z)
    rgb(ctx, BG)
    ctx.paint()
    stars(ctx, 0.6, DG_SY - 100)
    # terre
    g = cairo.LinearGradient(0, DG_SY, 0, DG_SY + 2600)
    g.add_color_stop_rgb(0, 0.2, 0.17, 0.14)
    g.add_color_stop_rgb(1, 0.08, 0.07, 0.06)
    ctx.set_source(g)
    ctx.rectangle(-1500, DG_SY, W + 3000, 4000)
    ctx.fill()
    r = random.Random(3)
    for k in range(18):
        y = DG_SY + 120 + k * 135
        ctx.set_source_rgba(0, 0, 0, 0.25)
        ctx.set_line_width(3)
        ctx.move_to(-1500, y)
        for x in range(-1500, W + 1600, 80):
            ctx.line_to(x, y + 10 * math.sin(x * 0.01 + k))
        ctx.stroke()
    for _ in range(260):
        ctx.set_source_rgba(0.5, 0.45, 0.4, r.uniform(0.08, 0.25))
        ctx.save()
        ctx.translate(r.uniform(-1500, W + 1500), r.uniform(DG_SY + 30, DG_SY + 3000))
        ctx.scale(1, 0.6)
        ctx.arc(0, 0, r.uniform(4, 16), 0, 6.28)
        ctx.restore()
        ctx.fill()
    # diamants
    found = T > 22.1
    rg = random.Random(12)
    for hx in DG_X + [-400, 1500, 2000, -900]:
        for _ in range(6):
            gx = hx + rg.uniform(-95, 95)
            gy = DG_DY + rg.uniform(20, 190)
            sp = (0.5 + 0.5 * math.sin(T * 5 + gx)) if (found and hx == DG_X[2]) else 0.0
            gem(ctx, gx, gy, rg.uniform(15, 26), rg.uniform(-0.4, 0.4), 1.0, sp)
    if found:
        glow(ctx, DG_X[2], DG_DY + 80, 420, (0.55, 0.85, 1), 0.35 * ease((T - 22.1) / 0.6))
    # trous + creuseurs
    names = ["MOTIVATION", "TALENT", "DISCIPLINE"]
    cols = [MOTI_C, TALE_C, DISC_C]
    for i, x in enumerate(DG_X):
        depth, active, f = dig_state(i, T)
        rgb(ctx, (0.035, 0.035, 0.04))
        ctx.rectangle(x - DG_HW, DG_SY, 2 * DG_HW, depth)
        ctx.fill()
        rgb(ctx, (0.3, 0.26, 0.22))
        ctx.set_line_width(3)
        ctx.move_to(x - DG_HW, DG_SY)
        ctx.line_to(x - DG_HW, DG_SY + depth)
        ctx.line_to(x + DG_HW, DG_SY + depth)
        ctx.line_to(x + DG_HW, DG_SY)
        ctx.stroke()
        # tas de terre
        hgt = min(120, depth * 0.08)
        rgb(ctx, (0.24, 0.2, 0.16))
        ctx.move_to(x + DG_HW + 4, DG_SY)
        ctx.curve_to(x + DG_HW + 20, DG_SY - hgt, x + DG_HW + 60, DG_SY - hgt, x + DG_HW + 70 + hgt * 0.3, DG_SY)
        ctx.close_path()
        ctx.fill()
        yb = DG_SY + depth
        if i == 2 and found:
            pose = pmix(STAND, CHEER, ease((T - 22.2) / 0.4))
            j, hy = placed(ctx, x, yb, pose, s, mix(WHITE, RED, ease((T - 22.2) / 1.0)), shadow=False)
        elif active or i == 2:
            j, hy = digger(ctx, x - 20, yb, T, f, s, cols[i], active)
        else:
            j, hy = placed(ctx, x - 10, yb, SIT, s, cols[i], shadow=False)
        name_tag(ctx, j, x if i != 0 or active else x - 10, hy, names[i],
                 RED if i == 2 and found else (0.82, 0.82, 0.83), s)
        hx, hh = x + j["head"][0], hy + j["head"][1]
        if i == 0:
            bubble(ctx, hx, hh - 60, "TOO HARD.", fade_win(T, 6.4, 10))
        if i == 1:
            bubble(ctx, hx, hh - 60, "NOTHING HERE...", fade_win(T, 12.7, 16))
    rgb(ctx, (0.35, 0.3, 0.25))
    ctx.set_line_width(4)
    ctx.move_to(-1500, DG_SY)
    ctx.line_to(W + 1500, DG_SY)
    ctx.stroke()
    if T > 22.8:
        x = DG_X[1]
        a = ease((T - 22.8) / 0.5)
        ctx.set_source_rgba(1, 1, 1, 0.8 * a)
        ctx.set_line_width(4)
        ctx.set_dash([12, 10])
        ctx.move_to(x + DG_HW + 30, DG_SY + 1462)
        ctx.line_to(x + DG_HW + 30, DG_DY + 20)
        ctx.stroke()
        ctx.set_dash([])
        text(ctx, "1 M", x + DG_HW + 110, DG_SY + 1490, 40, color=WHITE, alpha=a)
    hud(ctx, min(365, 1 + int(T * 14.5)), "DEPTH", f"{int(dd / 15)} M")


# ============================================================================ 3. TRACTIONS
PU_BAR, PU_FLOOR, PU_X = 820, 1330, [290, 790]


def pull_fig(ctx, cx, u, s, col, shake=0.0, T=0.0):
    pose = pmix(E.HANG, E.PULL_TOP, ease(u))
    j = joints(pose, s)
    hy = PU_BAR - (j["rh"][1] + j["lh"][1]) / 2 + 4
    x = cx + math.sin(T * 50) * shake
    j = stick(ctx, x, hy, pose, s, fill=col, shadow=PU_FLOOR)
    return j, hy, x


def world_pullups(ctx, T, frame):
    s = 0.95
    camera(ctx, W / 2, 1000, 1.0 + 0.04 * math.sin(T * 0.5))
    rgb(ctx, (0.055, 0.055, 0.06))
    ctx.paint()
    glow(ctx, PU_X[1], 950, 600, RED if T > 18 else (1, 1, 1), 0.1 + (0.18 if T > 18 else 0))
    rgb(ctx, (0.3, 0.3, 0.31))
    ctx.set_line_width(4)
    ctx.move_to(-300, PU_FLOOR)
    ctx.line_to(W + 300, PU_FLOOR)
    ctx.stroke()
    for cx in PU_X:
        rgb(ctx, (0.55, 0.55, 0.56))
        ctx.set_line_width(9)
        for x in (cx - 175, cx + 175):
            ctx.move_to(x, PU_BAR)
            ctx.line_to(x, PU_FLOOR)
            ctx.stroke()
        ctx.set_line_width(10)
        ctx.move_to(cx - 195, PU_BAR)
        ctx.line_to(cx + 195, PU_BAR)
        ctx.stroke()
    # MOTIVATION
    cx = PU_X[0]
    reps_m = min(10, int(2.4 * min(T, 4) + 0.5))
    if T < 4:
        j, hy, x = pull_fig(ctx, cx, 0.5 - 0.5 * math.cos(2 * math.pi * 2.4 * T), s, MOTI_C)
    elif T < 6.5:
        x = cx
        j, hy = placed(ctx, cx, PU_FLOOR, SLEEP if T > 4.4 else E.LYING, s, MOTI_C)
    elif 18 <= T < 20.5:
        j, hy, x = pull_fig(ctx, cx, 0.05 + 0.05 * abs(math.sin(T * 9)), s, MOTI_C, shake=3, T=T)
    else:
        x = cx
        j, hy = placed(ctx, cx, PU_FLOOR, SIT, s, MOTI_C)
        if T < 18 or T > 20.5:
            hx_, hy_ = x + j["rh"][0], hy + j["rh"][1]
            rgb(ctx, (0.15, 0.15, 0.16))
            rrect(ctx, hx_ - 4, hy_ - 34, 22, 36, 4)
            ctx.fill()
            ctx.set_source_rgba(0.6, 0.8, 1, 0.6)
            ctx.rectangle(hx_ - 1, hy_ - 31, 16, 28)
            ctx.fill()
    name_tag(ctx, j, x, hy, "MOTIVATION", s=s)
    hx, hh = x + j["head"][0], hy + j["head"][1]
    bubble(ctx, hx, hh - 60, "SO SORE...", fade_win(T, 4.5, 6.6))
    if 6.6 < T < 17.8:
        msgs = ["TOMORROW...", "NEXT WEEK.", "ON MONDAY.", "NEW YEAR..."]
        k = int((T - 6.6) / 2.8)
        bubble(ctx, hx, hh - 60, msgs[k % 4], fade_win((T - 6.6) % 2.8, 0.1, 2.6))
    bubble(ctx, hx, hh - 60, "WHY IS IT SO HARD?", fade_win(T, 18.3, 21.5))
    # DISCIPLINE
    cx = PU_X[1]
    if T < 4:
        u = 0.5 - 0.5 * math.cos(2 * math.pi * 0.75 * T)
        total = int(0.75 * T + 0.5)
    elif T < 5:
        u, total = 0.0, 3
    elif T < T_SPLIT:
        u = 0.5 - 0.5 * math.cos(2 * math.pi * 1.8 * T)
        day = 1 + int((T - 5) / 10 * 364)
        total = 3 + (day - 1) * 30
    else:
        u = 0.5 - 0.5 * math.cos(2 * math.pi * 2.6 * T)
        total = 10923 + int((T - T_SPLIT) * 2.6)
    col = mix(WHITE, RED, ease((T - 18) / 2))
    if 4 <= T < 5:
        x = cx
        j, hy = placed(ctx, cx, PU_FLOOR, STAND, s, col)
    elif T > 23.5:
        x = cx
        glow(ctx, cx, PU_FLOOR - 160, 280, RED, 0.4)
        j, hy = placed(ctx, cx, PU_FLOOR, pmix(STAND, CHEER, ease((T - 23.5) / 0.4)), s, col)
    else:
        j, hy, x = pull_fig(ctx, cx, u, s, col)
    name_tag(ctx, j, x, hy, "DISCIPLINE", RED if T > 18 else (0.82, 0.82, 0.83), s)
    day = 1 if T < 5 else min(365, 1 + int((T - 5) / 10 * 364))
    ctx.save()
    ctx.identity_matrix()
    text(ctx, "REPS", 290, 560, 22, color=(0.6, 0.6, 0.6), spacing=4)
    text(ctx, f"{reps_m}", 290, 630, 64, color=MOTI_C)
    text(ctx, "REPS", 790, 560, 22, color=(0.6, 0.6, 0.6), spacing=4)
    text(ctx, f"{total:,}", 790, 630, 64, color=RED if T > 18 else WHITE)
    ctx.restore()
    hud(ctx, day, y=230, s=0.8)


# ============================================================================ 4. MARATHON
MR_FIN = 300 * 23.0


def mr_state(i, T):
    if i == 0:
        dist = 950 * 2.2 * (1 - math.exp(-min(T, 7.5) / 2.2))
        v = 950 * math.exp(-T / 2.2) if T < 7.5 else 0.0
        return dist, v
    if i == 1:
        if T < 5:
            return 420 * T, 420
        k = clamp((T - 5) / 1.5)
        return 2100 + 420 * 1.5 * (k - k * k / 2), 420 * (1 - k)
    return min(300 * T, MR_FIN + 160), (300 if 300 * T < MR_FIN + 160 else 0)


def world_marathon(ctx, T, frame):
    dd = mr_state(2, T)[0]
    E.track(ctx, dd * 0.75, red=0.6 if T > 20 else 0.0)
    # ciel de nuit qui s'eclaircit
    night = 1 - ease((T - 14) / 8)
    stars(ctx, night, 700, seed=4)
    ctx.set_source_rgba(0.9, 0.9, 0.9, 0.7 * night + 0.1)
    ctx.arc(840, 300 + 40 * (1 - night), 46, 0, 6.28)
    ctx.fill()
    if T > 14:
        glow(ctx, W / 2, 850, 900, RED, 0.25 * (1 - night))
    lanes = [E.LANES[1], E.LANES[2], E.LANES[3]]
    names = ["MOTIVATION", "TALENT", "DISCIPLINE"]
    cols = [MOTI_C, TALE_C, DISC_C]
    scales = [0.82, 0.88, 1.0]
    for i in range(3):
        dist, v = mr_state(i, T)
        x = 400 + (dist - dd) * 0.75
        ly = lanes[i]
        gy = ly + 60
        s = scales[i]
        if not -200 < x < W + 200:
            continue
        if i == 2 and T > 23.2:
            col = mix(WHITE, RED, ease((T - 23.2) / 0.8))
            glow(ctx, x, gy - 150, 260, RED, 0.35)
            j, hy = placed(ctx, x, gy, pmix(STAND, CHEER, ease((T - 23.2) / 0.4)), s, col)
            name_tag(ctx, j, x, hy, names[i], RED, s)
            continue
        if v > 200:
            E.runner(ctx, x, ly, dist / 95, cols[i], s=s, label=names[i], lab_col=(0.82, 0.82, 0.83),
                     trail=2 if i == 2 else 0)
            hy = gy - 112 * s
            j = joints(run_pose(dist / 95), s)
        elif v > 5:
            flat = (lambda _x, _g=gy: _g)
            j, hy = walker(ctx, x, flat, flat, dist * 0.75, s, cols[i])
            name_tag(ctx, j, x, hy, names[i], s=s)
        else:
            pose = SIT if i == 0 else SLEEP
            j, hy = placed(ctx, x, gy, pose, s, cols[i])
            name_tag(ctx, j, x, hy, names[i], s=s)
            if i == 1:
                zzz(ctx, x + j["head"][0] + 20, hy + j["head"][1] - 30, T)
        hx, hh = x + j["head"][0], hy + j["head"][1]
        if i == 0:
            bubble(ctx, hx, hh - 60, "I'M DONE.", fade_win(T, 7.7, 11))
    fx = 400 + (MR_FIN - dd) * 0.75
    if fx < W + 300:
        finish_line(ctx, fx, E.LANES[0] + 60, E.LANES[3] + 60)
    if 22.9 < T < 23.3:
        ctx.save()
        ctx.identity_matrix()
        ctx.set_source_rgba(1, 1, 1, 0.5 * (1 - (T - 22.9) / 0.4))
        ctx.paint()
        ctx.restore()
    vignette(ctx, 0.5)
    hud(ctx, None, "KM", f"{min(42.2, dd / MR_FIN * 42.2):.1f}", y=200)


run_pose = E.run_pose


# ============================================================================ 5. ROCHER
BD_Y = [800, 1330, 1860]
ROCK_SMALL = None


def slope_pt(A, B, prog):
    ux, uy = B[0] - A[0], B[1] - A[1]
    ln = math.hypot(ux, uy)
    ux, uy = ux / ln, uy / ln
    nx, ny = uy, -ux
    if ny > 0:
        nx, ny = -nx, -ny
    return (A[0] + ux * prog, A[1] + uy * prog), (ux, uy), (nx, ny)


def rock_at(ctx, cx, cy, R, rot):
    surf, _, S = E.ROCK
    sc = R / E.ROCK_R
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(rot)
    ctx.scale(sc, sc)
    ctx.set_source_surface(surf, -S / 2, -S / 2)
    ctx.paint()
    ctx.restore()


def pusher(ctx, A, B, prog, t, s, R, col, state="push", push_amp=1.0):
    def sy(x):
        return A[1] + (B[1] - A[1]) * (x - A[0]) / (B[0] - A[0])
    (gx, gy), (ux, uy), (nx, ny) = slope_pt(A, B, prog)
    cx, cy = gx + nx * (R - 3), gy + ny * (R - 3)
    push = (0.5 - 0.5 * math.cos(t * 2 * math.pi * 0.9)) * push_amp
    rock_at(ctx, cx, cy, R, prog / R)
    if state == "push":
        hand_pts = []
        for beta in (10, -3):
            b_ = math.radians(beta)
            vx = -math.cos(b_) * ux + math.sin(b_) * nx
            vy = -math.cos(b_) * uy + math.sin(b_) * ny
            hand_pts.append((cx + vx * R * 0.96, cy + vy * R * 0.96))
        hmx = (hand_pts[0][0] + hand_pts[1][0]) / 2
        hmy = (hand_pts[0][1] + hand_pts[1][1]) / 2
        lean = math.radians(15 + 5 * push)
        ldx, ldy = math.cos(lean) * ux + math.sin(lean) * nx, math.cos(lean) * uy + math.sin(lean) * ny
        dd_ = (182 - 14 * push) * s
        hipx, hipy = hmx - ldx * dd_, hmy - ldy * dd_
        t_ang = math.degrees(math.atan2(hmx - hipx, hmy - hipy)) - 2
        pose = {"t": t_ang}
        tdx, tdy = d(t_ang)
        shx, shy = hipx + tdx * 80 * s, hipy + tdy * 80 * s
        for side, hp in (("l", hand_pts[0]), ("r", hand_pts[1])):
            a1, a2 = ik(shx, shy, hp[0], hp[1], 48 * s, 46 * s, (0, 1))
            pose[side + "a1"], pose[side + "a2"] = a1, a2
        ph = t * 2 * math.pi * 0.45 * (1 if push_amp > 0 else 0)
        for side, off in (("l", 0.0), ("r", math.pi)):
            cyc = math.sin(ph + off)
            along = -40 * s + 48 * s * cyc
            lift = max(0.0, math.cos(ph + off)) * 14 * s * push_amp
            fx = hipx + along * ux
            fy = sy(fx) - 4 - lift
            a1, a2 = ik(hipx, hipy, fx, fy, 58 * s, 58 * s, (ux + nx, uy + ny))
            pose[side + "l1"], pose[side + "l2"] = a1, a2
        j = stick(ctx, hipx, hipy, pose, s, fill=col, neck=-48)
        return j, hipx, hipy
    return None, cx, cy


def world_boulder(ctx, T, frame):
    camera(ctx, W / 2, H / 2 + 20, 1.0)
    rgb(ctx, BG)
    ctx.paint()
    if T > 20:
        glow(ctx, 1000, BD_Y[2] - 600, 600, RED, 0.3 * ease((T - 20) / 2))
    names = ["MOTIVATION", "TALENT", "DISCIPLINE"]
    cols = [MOTI_C, TALE_C, DISC_C]
    R, s = 112, 0.78
    for i, yb in enumerate(BD_Y):
        A, B = (30, yb), (1290, yb - 470)
        ctx.move_to(A[0] - 200, A[1] + 75)
        ctx.line_to(B[0] + 200, B[1] - 75)
        ctx.line_to(B[0] + 200, yb + 900)
        ctx.line_to(A[0] - 200, yb + 900)
        ctx.close_path()
        shade = 0.12 + 0.03 * i
        g = cairo.LinearGradient(0, yb - 470, 0, yb + 500)
        g.add_color_stop_rgb(0, shade + 0.05, shade + 0.05, shade + 0.06)
        g.add_color_stop_rgb(1, 0.03, 0.03, 0.035)
        ctx.set_source(g)
        ctx.fill()
        ctx.set_source_rgba(1, 1, 1, 0.3)
        ctx.set_line_width(2.5)
        ctx.move_to(A[0] - 200, A[1] + 75)
        ctx.line_to(B[0] + 200, B[1] - 75)
        ctx.stroke()
        summit = 990
        if i == 2:
            (fxp, fyp), _, _ = slope_pt(A, B, summit + 60)
            flag(ctx, fxp, fyp, T, h=170)
        if i == 0:
            if T < 5.5:
                prog, state = 200 + 480 * (1 - math.exp(-T / 2)), "push"
            elif T < 7:
                prog, state = lerp(200 + 480 * (1 - math.exp(-2.75)), 300, ease_in((T - 5.5) / 1.5)), "roll"
            else:
                prog, state = 300, "down"
        elif i == 1:
            prog, state = (200 + 70 * min(T, 7)), ("push" if T < 7 else "sit")
        else:
            prog = min(150 + 40 * T, summit)
            state = "push" if prog < summit else "top"
        j, px, py = pusher(ctx, A, B, prog, T, s, R, cols[i] if not (i == 2 and T > 21) else
                           mix(WHITE, RED, ease((T - 21) / 1.5)), "push" if state == "push" else "none")
        if state == "push":
            name_tag(ctx, j, px, py, names[i], s=s)
            hx, hh = px + j["head"][0], py + j["head"][1]
        else:
            if state == "sit":
                (gx, gy), (ux, uy), _ = slope_pt(A, B, prog - R - 60)
                pose, col = SIT, cols[i]
            elif state in ("roll", "down"):
                (gx, gy), _, _ = slope_pt(A, B, 140)
                gy = A[1] + (B[1] - A[1]) * (gx - A[0]) / (B[0] - A[0])
                pose, col = (E.LYING if state == "roll" else SIT), cols[i]
            else:
                (gx, gy), _, _ = slope_pt(A, B, prog - R - 70)
                pose = pmix(STAND, CHEER, ease((T - 21.3) / 0.4))
                col = mix(WHITE, RED, ease((T - 21) / 1.5))
                glow(ctx, gx, gy - 100, 200, RED, 0.35)
            j, hy = placed(ctx, gx, gy, pose, s, col)
            name_tag(ctx, j, gx, hy, names[i], RED if state == "top" else (0.82, 0.82, 0.83), s)
            hx, hh = gx + j["head"][0], hy + j["head"][1]
            if state == "sit" and T > 10.5:
                zzz(ctx, hx + 20, hh - 20, T)
        if i == 0:
            bubble(ctx, hx, hh - 50, "IMPOSSIBLE.", fade_win(T, 7.2, 10.5))
        if i == 1:
            bubble(ctx, hx, hh - 50, "I NEED A BREAK.", fade_win(T, 7.2, 10.3))
    hud(ctx, min(365, 1 + int(T * 14.5)), y=170, s=0.7)


# ============================================================================ 6. BRIQUES
BK_GY, BK_X, BK_W, BK_H = 1580, [200, 540, 880], 66, 30


def bk_rows(i, T):
    if i == 0:
        return 11 * (1 - math.exp(-min(T, 5.2) / 1.6))
    if i == 1:
        return min(2.2 * T, 13.0)
    return min(1.85 * T, 46.0)


def brick(ctx, x, y, w, h, col, rot=0.0):
    ctx.save()
    ctx.translate(x + w / 2, y + h / 2)
    ctx.rotate(rot)
    rgb(ctx, col)
    ctx.rectangle(-w / 2 + 1.5, -h / 2 + 1.5, w - 3, h - 3)
    ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.08)
    ctx.rectangle(-w / 2 + 1.5, -h / 2 + 1.5, w - 3, 5)
    ctx.fill()
    ctx.restore()


def wall(ctx, cx, rows, col, crooked=0.0, collapse=-1.0, seed=0):
    r = random.Random(seed)
    for row in range(int(rows)):
        y = BK_GY - (row + 1) * BK_H
        pieces = [(cx - BK_W, BK_W), (cx, BK_W)] if row % 2 == 0 else \
            [(cx - BK_W, BK_W / 2), (cx - BK_W / 2, BK_W), (cx + BK_W / 2, BK_W / 2)]
        for (bx, bw) in pieces:
            dx = r.uniform(-1, 1) * crooked * row * 2.4
            rot = r.uniform(-1, 1) * crooked * 0.03 * row
            vx, spin = r.uniform(-260, 260), r.uniform(-6, 6)
            if collapse >= 0:
                tt = max(0.0, collapse - (rows - row) * 0.03)
                fall_y = min(BK_GY - BK_H - r.uniform(0, 70), y + 0.5 * 2600 * tt * tt)
                landed = fall_y < y + 0.5 * 2600 * tt * tt
                brick(ctx, bx + dx + vx * min(tt, 0.5), fall_y, bw, BK_H, col,
                      rot + (spin * min(tt, 0.5) if True else 0) * (0.4 if landed else 1))
            else:
                brick(ctx, bx + dx, y, bw, BK_H, col, rot)


def builder(ctx, x, top_y, T, f, s, col, active):
    u = 0.5 - 0.5 * math.cos(2 * math.pi * f * T) if active else 0.0
    bend = P(t=128, la1=35, la2=15, ra1=28, ra2=10, ll1=-12, ll2=-6, rl1=18, rl2=4)
    pose = pmix(STAND, bend, u)
    j, hy = placed(ctx, x, top_y, pose, s, col, shadow=False)
    if active:
        hx_, hy_ = x + j["rh"][0], hy + j["rh"][1]
        brick(ctx, hx_ - 20, hy_ - 8, 40, 18, (0.42, 0.42, 0.43))
    return j, hy


def world_bricks(ctx, T, frame):
    camera(ctx, W / 2, 900, 0.95)
    rgb(ctx, BG)
    ctx.paint()
    ca = ease((T - 12) / 6)
    for k in range(6):
        cx = (k * 260 + T * 25) % 1500 - 200
        ctx.set_source_rgba(0.8, 0.8, 0.8, 0.07 * ca)
        ctx.save()
        ctx.translate(cx, 220 + (k % 3) * 70)
        ctx.scale(1, 0.35)
        ctx.arc(0, 0, 160, 0, 6.28)
        ctx.restore()
        ctx.fill()
    if T > 21:
        glow(ctx, BK_X[2], 250, 500, RED, 0.3 * ease((T - 21) / 2))
    rgb(ctx, (0.3, 0.3, 0.31))
    ctx.set_line_width(4)
    ctx.move_to(-300, BK_GY)
    ctx.line_to(W + 300, BK_GY)
    ctx.stroke()
    names = ["MOTIVATION", "TALENT", "DISCIPLINE"]
    cols = [MOTI_C, TALE_C, DISC_C]
    s = 0.72
    for i, cx in enumerate(BK_X):
        rows = bk_rows(i, T)
        if i == 0:
            collapse = (T - 5.2) if T > 5.2 else -1.0
            wall(ctx, cx, rows, (0.32, 0.32, 0.33), crooked=1.0, collapse=collapse, seed=4)
            if T < 5.2:
                j, hy = builder(ctx, cx, BK_GY - int(rows) * BK_H, T, 3.2, s, cols[0], True)
                x = cx
            else:
                x = cx + 150
                fall = ease_in(clamp((T - 5.2) / 0.5))
                if T < 7:
                    top = lerp(BK_GY - 11 * BK_H, BK_GY, fall)
                    j, hy = placed(ctx, x, top, E.LYING, s, cols[0])
                else:
                    j, hy = placed(ctx, x, BK_GY, SIT, s, cols[0])
        elif i == 1:
            wall(ctx, cx, rows, (0.36, 0.36, 0.37), seed=5)
            top = BK_GY - int(rows) * BK_H
            x = cx
            if 2.2 * T < 13:
                j, hy = builder(ctx, cx, top, T, 2.2, s, cols[1], True)
            else:
                j, hy = placed(ctx, cx, top, SIT, s, cols[1], shadow=False)
                if T > 9.6:
                    zzz(ctx, cx + j["head"][0] + 20, hy + j["head"][1] - 20, T)
        else:
            wall(ctx, cx, rows, (0.44, 0.44, 0.45), seed=6)
            top = BK_GY - int(rows) * BK_H
            x = cx
            col = mix(WHITE, RED, ease((T - 24.9) / 0.8))
            if rows < 46:
                j, hy = builder(ctx, cx, top, T, 1.85, s, col, True)
            else:
                j, hy = placed(ctx, cx, top, pmix(STAND, CHEER, ease((T - 24.9) / 0.4)), s, col, shadow=False)
        name_tag(ctx, j, x, hy, names[i], RED if i == 2 and T > 24.9 else (0.82, 0.82, 0.83), s)
        hx, hh = x + j["head"][0], hy + j["head"][1]
        if i == 0:
            bubble(ctx, hx, hh - 60, "WHAT'S THE POINT?", fade_win(T, 7.2, 11))
        if i == 1:
            bubble(ctx, hx, hh - 60, "GOOD ENOUGH.", fade_win(T, 6.2, 9.4))
    hud(ctx, min(365, 1 + int(T * 14.5)), "BRICKS", f"{int(bk_rows(2, T) * 2):,}", y=160, s=0.7)


# ============================================================================ 7. ARBRE
TR_GY, TR_X, TR_HW = 1480, [380, 900], 62
AXE_UP = P(t=188, la1=-165, la2=-195, ra1=-155, ra2=-185, ll1=-15, ll2=-8, rl1=18, rl2=8)
AXE_HIT = P(t=160, la1=75, la2=92, ra1=82, ra2=96, ll1=-15, ll2=-8, rl1=18, rl2=8)
TR_NOTCH = TR_GY - 190


def tree(ctx, tx, frac, fall_ang, seed):
    ny = TR_NOTCH
    dep = frac * 2 * TR_HW * 0.92
    hh = 22 + 26 * frac
    bark = (0.27, 0.24, 0.21)
    # souche
    rgb(ctx, bark)
    ctx.move_to(tx - TR_HW, TR_GY)
    ctx.line_to(tx - TR_HW, ny + hh)
    ctx.line_to(tx - TR_HW + dep, ny)
    ctx.line_to(tx + TR_HW, ny)
    ctx.line_to(tx + TR_HW, TR_GY)
    ctx.close_path()
    ctx.fill()
    # partie haute (tourne autour du pivot)
    ctx.save()
    ctx.translate(tx + TR_HW, ny)
    ctx.rotate(fall_ang)
    ctx.translate(-(tx + TR_HW), -ny)
    rgb(ctx, bark)
    ctx.move_to(tx - TR_HW, ny - hh)
    ctx.line_to(tx - TR_HW + dep, ny)
    ctx.line_to(tx + TR_HW, ny)
    ctx.line_to(tx + TR_HW - 10, 250)
    ctx.line_to(tx - TR_HW + 10, 250)
    ctx.close_path()
    ctx.fill()
    r = random.Random(seed)
    ctx.set_source_rgba(0, 0, 0, 0.3)
    ctx.set_line_width(3)
    for _ in range(14):
        x = tx + r.uniform(-TR_HW + 12, TR_HW - 12)
        y0 = r.uniform(300, ny - 80)
        ctx.move_to(x, y0)
        ctx.line_to(x + r.uniform(-4, 4), y0 + r.uniform(60, 160))
        ctx.stroke()
    for k in range(9):
        a = k / 9 * 2 * math.pi
        cx_, cy_ = tx + 150 * math.cos(a) * 1.1, 260 + 110 * math.sin(a)
        g = cairo.RadialGradient(cx_ - 30, cy_ - 40, 10, cx_, cy_, 170)
        g.add_color_stop_rgb(0, 0.3, 0.32, 0.3)
        g.add_color_stop_rgb(1, 0.13, 0.14, 0.13)
        ctx.set_source(g)
        ctx.arc(cx_, cy_, 150, 0, 6.28)
        ctx.fill()
    ctx.restore()
    # bois clair dans l'entaille
    if frac > 0:
        ctx.set_source_rgba(0.75, 0.65, 0.5, 0.9)
        ctx.set_line_width(4)
        ctx.move_to(tx - TR_HW, ny + hh)
        ctx.line_to(tx - TR_HW + dep, ny)
        ctx.stroke()
        if fall_ang == 0:
            ctx.move_to(tx - TR_HW, ny - hh)
            ctx.line_to(tx - TR_HW + dep, ny)
            ctx.stroke()


def chopper(ctx, x, T, f, s, col, active, chips_x, seed):
    c = f * T
    fr = c % 1
    if not active:
        u = 0.0
    elif fr < 0.55:
        u = ease(fr / 0.55)
    elif fr < 0.7:
        u = 1 - ease_in((fr - 0.55) / 0.15)
    else:
        u = 0.0
    pose = pmix(AXE_HIT, AXE_UP, u)
    j, hy = placed(ctx, x, TR_GY, pose, s, col)
    hx_, hy_ = x + j["rh"][0], hy + j["rh"][1]
    ang = lerp(95, 200, u)
    sx, sy = d(ang)
    ln = 120 * s
    ex, ey = hx_ + sx * ln, hy_ + sy * ln
    rgb(ctx, (0.55, 0.45, 0.35))
    ctx.set_line_width(8 * s)
    ctx.move_to(hx_ - sx * 18 * s, hy_ - sy * 18 * s)
    ctx.line_to(ex, ey)
    ctx.stroke()
    ctx.save()
    ctx.translate(ex, ey)
    ctx.rotate(-math.radians(ang) + math.pi / 2)
    rgb(ctx, (0.78, 0.78, 0.8))
    ctx.move_to(0, -6)
    ctx.line_to(34 * s, -22 * s)
    ctx.line_to(34 * s, 22 * s)
    ctx.line_to(0, 6)
    ctx.close_path()
    ctx.fill()
    ctx.restore()
    if active and fr >= 0.7:
        particles(ctx, chips_x, TR_NOTCH, (fr - 0.7) / 0.3, int(c) + seed, n=9, spread=260, up=420,
                  col=(0.8, 0.7, 0.55), size=(3, 7))
    return j, hy


def world_tree(ctx, T, frame):
    fall_t = 21.6
    impact = clamp(1 - (T - fall_t - 1.2) / 0.4) if T > fall_t + 1.2 else 0.0
    z = 0.9 if T < fall_t else lerp(0.9, 0.62, ease((T - fall_t) / 1.6))
    camera(ctx, lerp(W / 2, 760, ease((T - fall_t) / 1.6)), lerp(940, 1150, ease((T - fall_t) / 1.6)), z,
           shake=20 * impact, frame=frame)
    rgb(ctx, BG)
    ctx.paint()
    glow(ctx, W / 2, 600, 900, (1, 1, 1), 0.05)
    rgb(ctx, (0.3, 0.3, 0.31))
    ctx.set_line_width(4)
    ctx.move_to(-900, TR_GY)
    ctx.line_to(W + 1500, TR_GY)
    ctx.stroke()
    s = 0.95
    # MOTIVATION
    hits_m = min(10, int(2.3 * min(T, 4.6) + 0.3))
    tree(ctx, TR_X[0], hits_m * 0.028, 0.0, 1)
    if T < 4.6:
        j, hy = chopper(ctx, TR_X[0] - TR_HW - 175 * s, T, 2.3, s, MOTI_C, True, TR_X[0] - TR_HW, 3)
        x = TR_X[0] - TR_HW - 175 * s
    else:
        x = TR_X[0] - TR_HW - 150 * s
        j, hy = placed(ctx, x, TR_GY, SIT, s, MOTI_C)
    name_tag(ctx, j, x, hy, "MOTIVATION", s=s)
    hx, hh = x + j["head"][0], hy + j["head"][1]
    bubble(ctx, hx + 40, hh - 60, "THIS TREE IS TOO BIG.", fade_win(T, 5.0, 8.6))
    bubble(ctx, hx + 40, hh - 60, "I'LL JUST BUY WOOD.", fade_win(T, 16, 19.5))
    # DISCIPLINE
    hits_d = min(26, int(1.2 * T + 0.3))
    fall = (math.pi / 2) * ease_in(clamp((T - fall_t) / 1.2))
    tree(ctx, TR_X[1], hits_d / 26, fall, 2)
    col = mix(WHITE, RED, ease((T - fall_t - 1.2) / 0.8))
    x = TR_X[1] - TR_HW - 175 * s
    if T < fall_t:
        j, hy = chopper(ctx, x, T, 1.2, s, col, True, TR_X[1] - TR_HW + hits_d / 26 * 110, 9)
    else:
        if T > fall_t + 1.2:
            glow(ctx, x, TR_GY - 150, 260, RED, 0.35)
            particles(ctx, TR_X[1] + 600, TR_GY - 20, (T - fall_t - 1.2) / 1.2, 5, n=40, spread=700, up=500,
                      col=(0.6, 0.6, 0.6), size=(6, 16), g=900)
        j, hy = placed(ctx, x, TR_GY, pmix(STAND, CHEER, ease((T - fall_t - 1.2) / 0.4)), s, col)
    name_tag(ctx, j, x, hy, "DISCIPLINE", RED if T > fall_t + 1.2 else (0.82, 0.82, 0.83), s)
    if T > fall_t + 1.2:
        k = ease_out((T - fall_t - 1.2) / 0.4)
        text(ctx, "TIMBER!", 900, 800, 150 * k, color=WHITE, alpha=clamp(3 - (T - fall_t - 1.2)))
    hud(ctx, max(1, hits_d), "HITS", f"{hits_d}", y=190, s=0.75)


# ============================================================================ 8. POIDS
WT_FLOOR, WT_X = 1380, [330, 790]


def lifter(ctx, bar_x, v, kg, s, col, shake=0.0, T=0.0):
    bar_bottom = WT_FLOOR - 50 * s
    bar_top = WT_FLOOR - 113 * s
    vy = ease(v)
    bx = bar_x + (math.sin(T * 47) * shake if shake else 0)
    by = lerp(bar_bottom, bar_top, vy)
    t_ang = lerp(140, 180, vy)
    shx, shy = bx, by - 75 * s
    tx_, ty_ = d(t_ang)
    hipx, hipy = shx - tx_ * 80 * s, shy - ty_ * 80 * s
    pose = {"t": t_ang, "la1": -4, "la2": -2, "ra1": 4, "ra2": 2}
    for side, fx in (("l", bar_x - 34 * s), ("r", bar_x - 12 * s)):
        a1, a2 = ik(hipx, hipy, fx, WT_FLOOR - 6 * s, 58 * s, 58 * s, (1, 0))
        pose[side + "l1"], pose[side + "l2"] = a1, a2
    n = max(0, int((kg - 20) / 20))
    for i in range(n, 0, -1):
        ctx.save()
        ctx.translate(bx + 14 + i * 9 * s, by)
        ctx.scale(0.3, 1)
        rgb(ctx, (0.2 + 0.02 * (i % 2), 0.2, 0.21))
        ctx.arc(0, 0, 50 * s, 0, 6.28)
        ctx.fill_preserve()
        rgb(ctx, (0.45, 0.45, 0.46))
        ctx.set_line_width(5)
        ctx.stroke()
        ctx.restore()
    j = stick(ctx, hipx, hipy, pose, s, fill=col, arm=0.8, shadow=WT_FLOOR)
    rgb(ctx, (0.75, 0.75, 0.77))
    ctx.arc(bx, by, 9 * s, 0, 6.28)
    ctx.fill()
    text(ctx, f"{kg} KG", bar_x + 30, WT_FLOOR + 80, 40, color=(0.75, 0.75, 0.75), spacing=3)
    return j, hipx, hipy


def world_weights(ctx, T, frame):
    s = 1.05
    lift_t = 19.0
    z = 1.0 + (0.12 * ease((T - lift_t) / 2.5) if T > lift_t else 0)
    camera(ctx, lerp(W / 2, WT_X[1] - 40, ease((T - lift_t) / 2)), 1080, z,
           shake=(5 * (1 - ease((T - lift_t) / 2.5)) if lift_t < T < lift_t + 2.5 else 0), frame=frame)
    rgb(ctx, (0.055, 0.055, 0.06))
    ctx.paint()
    glow(ctx, WT_X[1], 1100, 600, RED if T > lift_t else (1, 1, 1), 0.1 + (0.2 if T > lift_t + 2.5 else 0))
    rgb(ctx, (0.3, 0.3, 0.31))
    ctx.set_line_width(4)
    ctx.move_to(-300, WT_FLOOR)
    ctx.line_to(W + 300, WT_FLOOR)
    ctx.stroke()
    # MOTIVATION : 200 kg des le 1er jour
    if T < 4.2:
        j, x, hy = lifter(ctx, WT_X[0], 0.03 + 0.02 * abs(math.sin(T * 8)), 200, s, MOTI_C, shake=3.5, T=T)
    else:
        n = 9
        for i in range(n, 0, -1):
            ctx.save()
            ctx.translate(WT_X[0] + 14 + i * 9 * s, WT_FLOOR - 50 * s)
            ctx.scale(0.3, 1)
            rgb(ctx, (0.2, 0.2, 0.21))
            ctx.arc(0, 0, 50 * s, 0, 6.28)
            ctx.fill()
            ctx.restore()
        text(ctx, "200 KG", WT_X[0] + 30, WT_FLOOR + 80, 40, color=(0.75, 0.75, 0.75), spacing=3)
        x = WT_X[0] - 130
        j, hy = placed(ctx, x, WT_FLOOR, SIT, s, MOTI_C)
    name_tag(ctx, j, x, hy, "MOTIVATION", s=s)
    hx, hh = x + j["head"][0], hy + j["head"][1]
    bubble(ctx, hx, hh - 60, "COME ON!!", fade_win(T, 2.0, 4.1))
    bubble(ctx, hx + 60, hh - 60, "MY BACK...", fade_win(T, 4.4, 7.8))
    bubble(ctx, hx + 60, hh - 60, "MUST BE GENETICS.", fade_win(T, 9.5, 13))
    bubble(ctx, hx + 60, hh - 60, "MAYBE NEXT YEAR.", fade_win(T, 16, 19))
    # DISCIPLINE
    if T < T_SPLIT:
        kg = min(180, 20 + 10 * int(T / 0.85))
        v = 0.5 - 0.5 * math.cos(2 * math.pi * 1.1 * T)
        shake = 0
    elif T < lift_t:
        kg, v, shake = 200, 0.0, 0
    else:
        kg = 200
        v = ease((T - lift_t) / 2.5)
        shake = 4 * (1 - v)
    col = mix(WHITE, RED, ease((T - lift_t - 2.5) / 0.8))
    j, x, hy = lifter(ctx, WT_X[1], v, kg, s, col, shake=shake, T=T)
    name_tag(ctx, j, x, hy, "DISCIPLINE", RED if T > lift_t + 2.5 else (0.82, 0.82, 0.83), s)
    if lift_t + 2.4 < T < lift_t + 2.7:
        ctx.save()
        ctx.identity_matrix()
        ctx.set_source_rgba(1, 1, 1, 0.5)
        ctx.paint()
        ctx.restore()
    day = min(365, 1 + int(T / T_SPLIT * 364)) if T < T_SPLIT else 365
    hud(ctx, day, "DISCIPLINE", f"{kg} KG", y=200, s=0.8)


# ============================================================================ 9. 5 H DU MATIN
def bedroom(ctx, T, who, minutes, ring):
    floor = 840
    win_a = clamp((minutes - 120) / 200)
    ctx.set_source_rgba(0.12 + 0.3 * win_a, 0.12 + 0.3 * win_a, 0.14 + 0.3 * win_a, 1)
    ctx.rectangle(110, 180, 230, 280)
    ctx.fill()
    rgb(ctx, (0.32, 0.32, 0.33))
    ctx.set_line_width(8)
    ctx.rectangle(110, 180, 230, 280)
    ctx.move_to(225, 180)
    ctx.line_to(225, 460)
    ctx.move_to(110, 320)
    ctx.line_to(340, 320)
    ctx.stroke()
    if win_a < 0.5:
        ctx.set_source_rgba(1, 1, 1, 0.6 * (1 - 2 * win_a))
        ctx.arc(290, 230, 20, 0, 6.28)
        ctx.fill()
    rgb(ctx, (0.25, 0.25, 0.26))
    ctx.move_to(0, floor)
    ctx.line_to(W, floor)
    ctx.set_line_width(4)
    ctx.stroke()
    rgb(ctx, (0.2, 0.2, 0.22))
    ctx.rectangle(230, 730, 520, 50)
    ctx.fill()
    ctx.rectangle(240, 780, 22, floor - 780)
    ctx.rectangle(718, 780, 22, floor - 780)
    ctx.rectangle(720, 640, 30, 100)
    ctx.fill()
    rgb(ctx, (0.85, 0.85, 0.86))
    rrect(ctx, 630, 700, 100, 34, 14)
    ctx.fill()
    # table de nuit + reveil
    rgb(ctx, (0.18, 0.18, 0.19))
    ctx.rectangle(800, 720, 150, floor - 720)
    ctx.fill()
    sh = (random.Random(int(T * 30)).uniform(-6, 6) if ring else 0)
    rgb(ctx, (0.1, 0.1, 0.1))
    rrect(ctx, 815 + sh, 650, 120, 70, 10)
    ctx.fill()
    hh_, mm_ = divmod(5 * 60 + int(minutes), 60)
    text(ctx, f"{hh_ % 24}:{mm_:02d}", 875 + sh, 698, 38, color=RED)
    if ring:
        ctx.set_source_rgba(1, 1, 1, 0.7)
        ctx.set_line_width(4)
        for k in range(3):
            rr = 50 + 22 * k + 10 * ((T * 4) % 1)
            ctx.arc(875, 685, rr, -2.4, -0.7)
            ctx.stroke()


def world_5am(ctx, T, frame):
    rgb(ctx, (0.04, 0.04, 0.045))
    ctx.paint()
    # --- panneau haut : MOTIVATION reste au lit
    ctx.save()
    ctx.rectangle(0, 0, W, 958)
    ctx.clip()
    ctx.translate(0, 40)
    rgb(ctx, (0.07, 0.07, 0.075))
    ctx.paint()
    minutes = T * 13 if T < T_SPLIT else 15 * 13 + (T - T_SPLIT) * 25
    ring = (T % 2.2) < 0.7 and minutes < 330
    bedroom(ctx, T, 0, minutes, ring)
    pose = dict(SLEEP)
    if ring:
        k = ease(((T % 2.2)) / 0.5)
        pose["ra1"], pose["ra2"] = lerp(-84, 140, k), lerp(-80, 120, k)
    j, hy = placed(ctx, 460, 732, pose, 1.0, MOTI_C, shadow=False)
    rgb(ctx, (0.4, 0.4, 0.42))
    rrect(ctx, 250, 700, 340, 56, 22)
    ctx.fill()
    text(ctx, "MOTIVATION", 90, 110, 24, color=(0.8, 0.8, 0.8), align="l", spacing=4)
    hx, hh = 460 + j["head"][0], hy + j["head"][1]
    if (T % 2.2) > 0.75:
        bubble(ctx, hx, hh - 50, "5 MORE MINUTES...", fade_win(T % 2.2, 0.8, 2.15) * (1 if T < 18 else 0))
    if not ring:
        zzz(ctx, hx + 30, hh - 30, T)
    bubble(ctx, hx, hh - 50, "WHY AM I ALWAYS TIRED?", fade_win(T, 19.5, 24.5))
    ctx.restore()
    # --- panneau bas : DISCIPLINE se leve et va courir
    ctx.save()
    ctx.rectangle(0, 962, W, 958)
    ctx.clip()
    ctx.translate(0, 980)
    if T < 3.4:
        rgb(ctx, (0.07, 0.07, 0.075))
        ctx.paint()
        bedroom(ctx, T, 1, 0, T < 0.7)
        if T < 0.7:
            j, hy = placed(ctx, 460, 732, SLEEP, 1.0, DISC_C, shadow=False)
            x = 460
        elif T < 1.6:
            k = ease((T - 0.7) / 0.9)
            sit_edge = P(t=178, la1=-10, la2=10, ra1=10, ra2=20, ll1=62, ll2=0, rl1=56, rl2=-4)
            x = lerp(460, 300, k)
            hy = lerp(ground_hip_y(SLEEP, 1.0, 732), 840 - 92, k)
            j = stick(ctx, x, hy, pmix(SLEEP, sit_edge, k), 1.0, fill=DISC_C)
        else:
            k = ease((T - 1.6) / 0.6)
            x = lerp(300, 180, k)
            j, hy = placed(ctx, x, 840, STAND, 1.0, DISC_C)
        name_tag(ctx, j, x, hy, "DISCIPLINE")
        bubble(ctx, x + j["head"][0], hy + j["head"][1] - 60, "5:00. LET'S GO.", fade_win(T, 1.9, 3.35))
    else:
        tt = T - 3.4
        dawn = ease((T - 8) / 14)
        g = cairo.LinearGradient(0, 0, 0, 800)
        g.add_color_stop_rgb(0, 0.04, 0.04, 0.05)
        g.add_color_stop_rgb(1, 0.06 + 0.35 * dawn, 0.05 + 0.1 * dawn, 0.06 + 0.08 * dawn)
        ctx.set_source(g)
        ctx.paint()
        stars(ctx, 1 - dawn, 600, seed=21)
        if dawn > 0:
            glow(ctx, 760, 780, 420, RED, 0.5 * dawn)
            ctx.set_source_rgba(0.95, 0.35, 0.3, dawn)
            ctx.arc(760, 800 - 120 * dawn, 90, math.pi, 2 * math.pi)
            ctx.fill()
        rgb(ctx, (0.05, 0.05, 0.055))
        ctx.rectangle(0, 800, W, 300)
        ctx.fill()
        rgb(ctx, (0.3, 0.3, 0.31))
        ctx.set_line_width(4)
        ctx.move_to(0, 800)
        ctx.line_to(W, 800)
        ctx.stroke()
        speed = 330 if T < T_SPLIT else 460
        dist = tt * speed
        for k in range(6):
            lx = (k * 360 - dist * 0.9) % 2160 - 300
            rgb(ctx, (0.35, 0.35, 0.36))
            ctx.set_line_width(7)
            ctx.move_to(lx, 800)
            ctx.line_to(lx, 470)
            ctx.line_to(lx + 60, 470)
            ctx.stroke()
            glow(ctx, lx + 60, 485, 160, (1, 0.9, 0.7), 0.18 * (1 - dawn))
        if T < 23:
            E.runner(ctx, 420, 740, dist / 95, DISC_C if T < 18 else mix(WHITE, RED, ease((T - 18) / 2)),
                     s=1.0, label="DISCIPLINE", trail=2 if T > T_SPLIT else 0)
        else:
            col = RED
            glow(ctx, 420, 650, 260, RED, 0.35)
            j, hy = placed(ctx, 420, 800, pmix(STAND, CHEER, ease((T - 23) / 0.4)), 1.0, col)
            name_tag(ctx, j, 420, hy, "DISCIPLINE", RED)
        if tt < 0.1:
            ctx.set_source_rgba(1, 1, 1, 0.4)
            ctx.paint()
    ctx.restore()
    rgb(ctx, (0.6, 0.6, 0.62))
    ctx.rectangle(0, 957, W, 6)
    ctx.fill()
    day = 1 if T < 3.4 else min(365, 1 + int((T - 3.4) * 17))
    ctx.save()
    calendar(ctx, W - 120, 960, str(day), s=0.6)
    ctx.restore()


# ============================================================================ 10. CORDE
RP_GY, RP_X = 1700, [230, 540, 850]
RP_TOP_H = 2500


def rope_climber(ctx, rx, h, ph, s, col, shake=0.0, T=0.0):
    hipy = RP_GY - 108 * s - h
    hipx = rx - 24 * s + (math.sin(T * 45) * shake if shake else 0)
    t_ang = 176
    tdx, tdy = d(t_ang)
    shx, shy = hipx + tdx * 80 * s, hipy + tdy * 80 * s
    pose = {"t": t_ang}
    for side, off, pref in (("l", 0.0, (-1, 0.3)), ("r", math.pi, (-1, 0.5))):
        hy_t = shy - 62 * s + 26 * s * math.sin(ph + off)
        a1, a2 = ik(shx, shy, rx, hy_t, 48 * s, 46 * s, pref)
        pose[side + "a1"], pose[side + "a2"] = a1, a2
    for side, off, dy in (("l", 0.0, 92), ("r", math.pi, 78)):
        fy = hipy + dy * s + 12 * s * math.sin(ph + off)
        a1, a2 = ik(hipx, hipy, rx + 4, fy, 58 * s, 58 * s, (1, 0))
        pose[side + "l1"], pose[side + "l2"] = a1, a2
    j = stick(ctx, hipx, hipy, pose, s, fill=col)
    return j, hipx, hipy


def rp_state(i, T):
    if i == 0:
        if T < 6:
            return 1000 * (1 - math.exp(-T / 2.0)), "climb"
        hmax = 1000 * (1 - math.exp(-3))
        if T < 8:
            return hmax, "hang"
        if T < 9.2:
            return lerp(hmax, 0, ease_in((T - 8) / 1.2)), "slide"
        return 0, "sit"
    if i == 1:
        if T < 6.5:
            return 120 * T, "climb"
        if T < 11:
            return 780, "hang"
        if T < 12.4:
            return lerp(780, 0, ease_in((T - 11) / 1.4)), "slide"
        return 0, "sit"
    h = 108 * T
    if h < RP_TOP_H:
        return h, "climb"
    return RP_TOP_H, "top"


def world_rope(ctx, T, frame):
    s = 1.0
    hd = rp_state(2, T)[0]
    hip_d = RP_GY - 108 * s - hd
    cy = min(960, hip_d - 120)
    z = 1.0
    top_t = RP_TOP_H / 108
    if T > top_t + 0.5:
        e = ease((T - top_t - 0.5) / 2.0)
        cy = lerp(cy, RP_GY - RP_TOP_H / 2 - 250, e)
        z = lerp(1.0, 0.36, e)
    camera(ctx, W / 2, cy, z)
    rgb(ctx, BG)
    ctx.paint()
    g = cairo.LinearGradient(0, RP_GY - RP_TOP_H - 600, 0, RP_GY)
    g.add_color_stop_rgba(0, 0.25, 0.08, 0.08, 0.6)
    g.add_color_stop_rgba(1, 0, 0, 0, 0)
    ctx.set_source(g)
    ctx.rectangle(-2000, RP_GY - RP_TOP_H - 1500, W + 4000, RP_TOP_H + 1500)
    ctx.fill()
    rgb(ctx, (0.3, 0.3, 0.31))
    ctx.set_line_width(4)
    ctx.move_to(-2000, RP_GY)
    ctx.line_to(W + 2000, RP_GY)
    ctx.stroke()
    top_y = RP_GY - 108 * s - RP_TOP_H - 190
    rgb(ctx, (0.45, 0.45, 0.46))
    ctx.rectangle(60, top_y - 30, W - 120, 30)
    ctx.fill()
    for rx in RP_X:
        rgb(ctx, (0.62, 0.58, 0.5))
        ctx.set_line_width(13)
        ctx.move_to(rx, top_y)
        ctx.line_to(rx, RP_GY)
        ctx.stroke()
        ctx.set_source_rgba(0, 0, 0, 0.3)
        ctx.set_line_width(2)
        y = top_y
        while y < RP_GY:
            ctx.move_to(rx - 6, y)
            ctx.line_to(rx + 6, y + 10)
            ctx.stroke()
            y += 16
    # cloche
    ring = clamp(1 - (T - top_t) / 1.5) if T > top_t else 0.0
    bx, by = RP_X[2] + 90, top_y
    ctx.save()
    ctx.translate(bx, by)
    ctx.rotate(0.5 * math.sin(T * 25) * ring)
    rgb(ctx, (0.85, 0.7, 0.3))
    ctx.move_to(-45, 110)
    ctx.curve_to(-45, 20, -30, 10, 0, 10)
    ctx.curve_to(30, 10, 45, 20, 45, 110)
    ctx.close_path()
    ctx.fill()
    ctx.arc(0, 118, 12, 0, 6.28)
    ctx.fill()
    ctx.restore()
    if ring > 0:
        for k in range(3):
            rr = 80 + 300 * (((T - top_t) * 1.2 + k / 3) % 1)
            ctx.set_source_rgba(1, 0.85, 0.4, 0.5 * ring)
            ctx.set_line_width(6)
            ctx.arc(bx, by + 60, rr, 0, 6.28)
            ctx.stroke()
        text(ctx, "DING!", bx - 220, by - 40, 120 * back_out(clamp((T - top_t) / 0.3)), color=WHITE,
             alpha=ring)
    names = ["MOTIVATION", "TALENT", "DISCIPLINE"]
    cols = [MOTI_C, TALE_C, DISC_C]
    for i, rx in enumerate(RP_X):
        h, st = rp_state(i, T)
        col = cols[i] if i < 2 else mix(WHITE, RED, ease((T - top_t) / 0.8))
        if st == "sit":
            j, hy = placed(ctx, rx - 70, RP_GY, SIT, s, col)
            x = rx - 70
        else:
            ph = h / (70 * s) if st == "climb" else 1.0
            j, x, hy = rope_climber(ctx, rx, h, ph, s, col, shake=3 if st == "hang" else 0, T=T)
        name_tag(ctx, j, x, hy, names[i], RED if i == 2 and st == "top" else (0.82, 0.82, 0.83), s)
        hx, hh = x + j["head"][0], hy + j["head"][1]
        if i == 0:
            bubble(ctx, hx, hh - 50, "MY ARMS...", fade_win(T, 6.2, 8.2))
            bubble(ctx, hx + 60, hh - 50, "IT'S TOO HIGH.", fade_win(T, 9.5, 13))
        if i == 1:
            bubble(ctx, hx, hh - 50, "I'LL REST HERE.", fade_win(T, 7, 10.6))
            if st == "sit" and T > 13:
                zzz(ctx, hx + 20, hh - 20, T)
    hud(ctx, min(365, 1 + int(T * 14.5)), "HEIGHT", f"{int(hd / 45)} M", y=190, s=0.75)


# ============================================================================ cartes & intro
def scene_intro(ctx, t, frame, v):
    ctx.save()
    v["world"](ctx, 0.0, frame)
    ctx.restore()
    ctx.save()
    ctx.identity_matrix()
    ctx.set_source_rgba(0, 0, 0, 0.62)
    ctx.paint()
    lines = v["title"]
    n = len(lines)
    hs = [80 if s_ == "VS" else 140 for s_, _ in lines]
    y = 860 - sum(hs) / 2
    ys = []
    for h_ in hs:
        ys.append(y + h_ * 0.75)
        y += h_
    for i, (s_, col) in enumerate(lines):
        k = clamp((t - i * 0.28) / 0.22)
        if k <= 0:
            continue
        size = 40 if s_ == "VS" else fit_size(ctx, s_, 104, 940, spacing=8)
        sc = lerp(1.5, 1.0, ease_out(k))
        ctx.save()
        ctx.translate(W / 2, ys[i])
        ctx.scale(sc, sc)
        text(ctx, s_, 0, 0, size, color=col, alpha=k, spacing=8)
        ctx.restore()
    if t > n * 0.28 + 0.2:
        k = clamp((t - n * 0.28 - 0.2) / 0.3)
        size = fit_size(ctx, v["question"], 56, 960, spacing=4)
        glow(ctx, W / 2, y + 110, 360, RED, 0.3 * k)
        text(ctx, v["question"], W / 2, y + 130, size, color=RED, alpha=k, spacing=4)
    ctx.restore()


def scene_definition(ctx, t, frame, v):
    word, phon, lines, quote = v["definition"]
    rgb(ctx, (0.1, 0.1, 0.105))
    ctx.paint()
    if t < 2.4:
        camera(ctx, W / 2, 900, lerp(1.0, 1.12, ease(t / 2.4)))
    else:
        k = ease((t - 2.4) / 0.6)
        camera(ctx, lerp(W / 2, 360, k), lerp(900, 600, k), lerp(1.12, 2.0, k))
    x0 = 110
    size = fit_size(ctx, word, 150, 860, family=SERIF, bold=False)
    text(ctx, word, x0, 600, size, family=SERIF, bold=False, align="l", color=(0.95, 0.95, 0.95))
    text(ctx, phon, x0, 690, 44, family=SERIF, bold=False, italic=True, align="l", color=(0.65, 0.65, 0.65))
    rgb(ctx, (0.4, 0.4, 0.4))
    ctx.set_line_width(2)
    ctx.move_to(x0, 740)
    ctx.line_to(W - 110, 740)
    ctx.stroke()
    for i, line in enumerate(lines):
        a = clamp((t - 0.25 - i * 0.2) * 3)
        text(ctx, line, x0, 820 + i * 64, 46, family=SERIF, bold=False, align="l",
             color=(0.75, 0.75, 0.75), alpha=a)
    yq = 820 + len(lines) * 64 + 90
    if t > 1.3:
        a = clamp((t - 1.3) * 3)
        qs = fit_size(ctx, quote, 50, 850, family=SERIF, bold=False)
        E.font(ctx, SERIF, qs, False)
        qw = E.text_width(ctx, quote)
        rgb(ctx, RED, 0.25 * a)
        ctx.rectangle(x0 - 10, yq - qs * 1.05, (qw + 20) * ease((t - 1.3) / 0.6), qs * 1.5)
        ctx.fill()
        text(ctx, quote, x0, yq, qs, family=SERIF, bold=False, align="l", color=WHITE, alpha=a)
    ctx.identity_matrix()
    vignette(ctx, 0.6)
    grain(ctx, frame, 0.06)


def scene_rock(ctx, t, frame, v):
    words, line = v["rock"]
    rgb(ctx, (0.02, 0.02, 0.025))
    ctx.paint()
    step = 1.3 / len(words)
    if t < 1.3:
        i = min(len(words) - 1, int(t / step))
        k = (t - i * step) / step
        base = fit_size(ctx, words[i], 300, 980, family=SERIF)
        sz = base * lerp(1.45, 1.0, ease_out(k / 0.35)) * lerp(1.0, 0.93, k)
        r = random.Random(frame)
        sh = 18 * clamp(1 - k / 0.3)
        glow(ctx, W / 2, H / 2, 600, (1, 1, 1), 0.12 + 0.15 * clamp(1 - k / 0.3))
        text(ctx, words[i], W / 2 + r.uniform(-sh, sh), H / 2 + sz * 0.35 + r.uniform(-sh, sh), sz,
             family=SERIF, color=WHITE)
    else:
        k = t - 1.3
        ap = clamp(k * 3)
        z = lerp(1.06, 1.18, ease(k / 2.4))
        ctx.save()
        camera(ctx, W / 2 - 30, H / 2 + 60, z, shake=2, frame=frame)
        size = fit_size(ctx, line, 92, 900, family=SERIF)
        text(ctx, line, W / 2 - 30, 640, size, family=SERIF, color=WHITE, alpha=ap)
        E.you_vs_you_image(ctx, k, frame, ap)
        ctx.restore()
    if frame % 11 == 0:
        ctx.set_source_rgba(1, 1, 1, 0.05)
        ctx.paint()
    vignette(ctx, 0.8)
    grain(ctx, frame, 0.08)


def scene_quote(ctx, t, frame, v):
    ctx.save()
    v["world"](ctx, T_END, frame)
    ctx.restore()
    ctx.save()
    ctx.identity_matrix()
    ctx.set_source_rgba(0, 0, 0, 0.62)
    ctx.paint()
    l1, l2 = v["quote"]
    n = int(clamp(t / 0.9) * len(l1))
    s1 = fit_size(ctx, l1, 60, 960, spacing=8)
    text(ctx, l1[:n], W / 2, 900, s1, color=(0.93, 0.93, 0.93), spacing=8)
    if t > 1.1:
        k = clamp((t - 1.1) / 0.25)
        sc = lerp(1.7, 1.0, ease_out(k))
        shake = (1 - k) * 26
        r = random.Random(frame)
        s2 = fit_size(ctx, l2, 116, 980, spacing=8)
        glow(ctx, W / 2, 1010, 420, RED, 0.35 * k)
        ctx.translate(W / 2 + r.uniform(-shake, shake), 1050 + r.uniform(-shake, shake))
        ctx.scale(sc, sc)
        text(ctx, l2, 0, 0, s2, color=RED, alpha=k, spacing=8)
    ctx.restore()
    ctx.save()
    ctx.identity_matrix()
    vignette(ctx, 0.6)
    if t > v["dur_quote"] - 0.6:
        ctx.set_source_rgba(0, 0, 0, clamp((t - v["dur_quote"] + 0.6) / 0.6))
        ctx.paint()
    ctx.restore()


def caption(ctx, s_, a, y):
    if a <= 0:
        return
    size = fit_size(ctx, s_, 36, 940, spacing=2)
    E.font(ctx, MONO, size, True)
    w = E.text_width(ctx, s_, 2) + 56
    ctx.set_source_rgba(0, 0, 0, 0.6 * a)
    rrect(ctx, W / 2 - w / 2, y - size * 1.45, w, size * 2.05, 18)
    ctx.fill()
    text(ctx, s_, W / 2, y, size, color=WHITE, alpha=a, spacing=2)


# ============================================================================ les 10 videos
G = (0.62, 0.62, 0.63)
TITLE3 = [("MOTIVATION", G), ("VS", RED), ("TALENT", G), ("VS", RED), ("DISCIPLINE", WHITE)]
TITLE2 = [("MOTIVATION", G), ("VS", RED), ("DISCIPLINE", WHITE)]

VIDEOS = [
    dict(key="01_escaliers", world=world_stairs, title=TITLE3, question="WHO REACHES THE TOP?",
         captions=[(0.6, 4.4, "DAY 1. EVERYONE STARTS CLIMBING."), (4.7, 8.2, "MOTIVATION STARTS FAST..."),
                   (8.5, 12.0, "...BUT IT NEVER LASTS."), (12.2, 14.9, "TALENT STOPS: \"GOOD ENOUGH.\""),
                   (15.6, 19.6, "DISCIPLINE KEEPS THE SAME PACE."), (19.9, 23.2, "EVERY. SINGLE. DAY."),
                   (23.6, 26, "THE TOP.")],
         definition=("discipline", "[ˈdɪsəplɪn]  noun • English",
                     ["doing what needs to be done,", "even when you don't feel like it.",
                      "the bridge between goals and", "results — still going long",
                      "after motivation is gone."], "motivation fades. discipline stays."),
         rock=(["IT'S", "YOU", "VS", "YOU"], "IT'S YOU VS YOU"),
         quote=("MOTIVATION FADES.", "DISCIPLINE STAYS."), music="A"),
    dict(key="02_diamants", world=world_dig, title=TITLE3, question="WHO FINDS THE DIAMONDS?",
         captions=[(0.6, 4.4, "DAY 1. EVERYONE STARTS DIGGING."), (4.6, 7.4, "MOTIVATION DIGS FAST..."),
                   (7.6, 11.6, "...THEN GIVES UP."), (12.6, 14.9, "TALENT STOPS TOO."),
                   (15.6, 19.5, "DISCIPLINE KEEPS DIGGING."), (19.8, 22.2, "ONE SHOVEL AT A TIME."),
                   (23.0, 26, "HE QUIT 1 METER BEFORE.")],
         definition=("persistence", "[pərˈsɪstəns]  noun • English",
                     ["continuing firmly in a course", "of action despite difficulty",
                      "or failure. refusing to stop —", "especially when the reward",
                      "is closer than it seems."], "most people quit right before it pays."),
         rock=(["KEEP", "DIGGING"], "KEEP DIGGING"),
         quote=("DON'T STOP", "BEFORE THE DIAMONDS."), music="B"),
    dict(key="03_tractions", world=world_pullups, title=TITLE2, question="WHO GETS STRONGER?",
         captions=[(0.4, 3.9, "DAY 1."), (4.2, 7.6, "MOTIVATION: 10 REPS. THEN NOTHING."),
                   (7.9, 11.8, "DISCIPLINE: 30 REPS. EVERY DAY."), (12.0, 14.9, "FOR 365 DAYS."),
                   (15.6, 18.0, "SMALL REPS ADD UP."), (21.6, 26, "10,000+ REPS LATER.")],
         definition=("consistency", "[kənˈsɪstənsi]  noun • English",
                     ["showing up again and again,", "even when nobody is watching.",
                      "small actions repeated daily —", "the quiet force behind every",
                      "great result."], "consistency beats intensity."),
         rock=(["ONE", "MORE", "REP"], "ONE MORE REP"),
         quote=("SMALL REPS.", "EVERY DAY."), music="A"),
    dict(key="04_marathon", world=world_marathon, title=TITLE3, question="WHO FINISHES THE RACE?",
         captions=[(0.4, 3.6, "THE MARATHON STARTS."), (3.9, 7.2, "MOTIVATION SPRINTS AHEAD..."),
                   (7.5, 11.0, "...AND BURNS OUT."), (11.3, 14.9, "DISCIPLINE NEVER CHANGES PACE."),
                   (15.6, 19.5, "KILOMETER AFTER KILOMETER."), (19.8, 22.8, "SAME PACE. NO EXCUSES."),
                   (23.3, 26, "42.2 KM.")],
         definition=("patience", "[ˈpeɪʃəns]  noun • English",
                     ["the ability to keep going", "without rushing the result.",
                      "trusting the process when", "progress feels slow — and",
                      "never changing your pace."], "slow progress is still progress."),
         rock=(["KEEP", "GOING"], "KEEP GOING"),
         quote=("IT'S NOT A SPRINT.", "IT'S A MARATHON."), music="B"),
    dict(key="05_rocher", world=world_boulder, title=TITLE3, question="WHO REACHES THE SUMMIT?",
         captions=[(0.5, 4.4, "EVERYONE HAS A ROCK TO PUSH."), (5.5, 8.6, "MOTIVATION LETS GO..."),
                   (8.8, 12.0, "TALENT TAKES A BREAK..."), (12.2, 14.9, "DISCIPLINE KEEPS PUSHING."),
                   (15.6, 19.5, "EVEN WHEN IT'S HEAVY."), (19.8, 21.2, "STEP BY STEP."),
                   (21.6, 26, "THE SUMMIT.")],
         definition=("resilience", "[rɪˈzɪliəns]  noun • English",
                     ["the strength to keep pushing", "under pressure. to fall, get",
                      "up, and push again — until", "the weight that crushed you",
                      "becomes the weight you carry."], "heavy is the path. push anyway."),
         rock=(["IT'S", "YOU", "VS", "YOU"], "IT'S YOU VS YOU"),
         caption_y=400, quote=("PUSH.", "EVEN WHEN IT'S HEAVY."), music="A"),
    dict(key="06_briques", world=world_bricks, title=TITLE3, question="WHO BUILDS THE TALLEST?",
         captions=[(0.5, 4.0, "EVERYONE STARTS BUILDING."), (4.2, 7.0, "MOTIVATION BUILDS FAST..."),
                   (7.2, 10.5, "...ON NOTHING SOLID."), (10.8, 14.9, "TALENT SETTLES: \"GOOD ENOUGH.\""),
                   (15.6, 19.8, "DISCIPLINE: ONE BRICK A DAY."), (20.2, 24.6, "NO SHORTCUTS."),
                   (25.0, 26, "LOOK AT IT NOW.")],
         definition=("commitment", "[kəˈmɪtmənt]  noun • English",
                     ["a promise you keep to yourself", "every single day. one brick",
                      "at a time, long after the", "excitement of starting has",
                      "disappeared."], "one brick a day builds a tower."),
         rock=(["BUILD.", "EVERY.", "DAY."], "BUILD. EVERY. DAY."),
         quote=("ONE BRICK", "A DAY."), music="B"),
    dict(key="07_arbre", world=world_tree, title=TITLE2, question="WHO CUTS THE TREE?",
         captions=[(0.4, 3.6, "A TREE THAT LOOKS IMPOSSIBLE."), (3.8, 6.8, "MOTIVATION SWINGS HARD..."),
                   (7.0, 10.6, "...AND QUITS AFTER 10 HITS."), (10.9, 14.9, "DISCIPLINE: ONE HIT A DAY."),
                   (15.6, 19.0, "NO MATTER HOW SMALL."), (19.3, 21.5, "HIT. AFTER. HIT."),
                   (22.9, 26, "TIMBER.")],
         definition=("determination", "[dɪˌtɜːmɪˈneɪʃən]  noun • English",
                     ["firmness of purpose. striking", "the same spot again and again,",
                      "until the impossible", "finally gives way."], "every hit counts. even small ones."),
         rock=(["KEEP", "SWINGING"], "KEEP SWINGING"),
         quote=("ONE HIT", "AT A TIME."), music="A"),
    dict(key="08_poids", world=world_weights, title=TITLE2, question="WHO LIFTS 200 KG?",
         captions=[(0.4, 3.8, "DAY 1. SAME BAR."), (4.0, 7.6, "MOTIVATION: 200 KG ON DAY ONE."),
                   (7.8, 11.0, "INJURED. QUIT."), (11.2, 14.9, "DISCIPLINE: +10 KG AT A TIME."),
                   (15.6, 18.8, "ONE YEAR LATER..."), (21.6, 26, "200 KG. NO EGO. JUST WORK.")],
         definition=("progress", "[ˈprəʊɡrɛs]  noun • English",
                     ["forward movement toward a goal,", "built step by step. not in one",
                      "heroic day — but in hundreds", "of small, boring, honest ones."],
                     "start light. never stop."),
         rock=(["NO", "EGO.", "JUST", "WORK."], "NO EGO. JUST WORK."),
         quote=("START LIGHT.", "NEVER STOP."), music="B"),
    dict(key="09_5h_du_matin", world=world_5am, title=TITLE2, question="WHO GETS UP AT 5 AM?",
         captions=[(0.3, 3.2, "5:00 AM."), (3.5, 7.2, "MOTIVATION: 5 MORE MINUTES."),
                   (7.5, 11.2, "DISCIPLINE: ALREADY OUTSIDE."), (11.5, 14.9, "EVERY. SINGLE. MORNING."),
                   (15.6, 19.3, "WHILE THEY SLEEP..."), (19.6, 22.8, "...YOU GET BETTER."),
                   (23.2, 26, "365 SUNRISES.")],
         caption_y=1240,
         definition=("sacrifice", "[ˈsækrɪfaɪs]  noun • English",
                     ["giving up what you want now", "for what you want most.",
                      "a warm bed for a cold road.", "comfort for growth."], "while they sleep, you build."),
         rock=(["NO", "DAYS", "OFF"], "NO DAYS OFF"),
         quote=("WHILE THEY SLEEP,", "YOU WORK."), music="A"),
    dict(key="10_corde", world=world_rope, title=TITLE3, question="WHO RINGS THE BELL?",
         captions=[(0.5, 3.6, "A ROPE. A BELL AT THE TOP."), (3.9, 6.6, "MOTIVATION CLIMBS FAST..."),
                   (6.8, 10.0, "...THEN SLIDES BACK DOWN."), (10.3, 14.9, "TALENT RESTS. THEN FALLS."),
                   (15.6, 19.6, "DISCIPLINE: ONE HAND, THEN THE OTHER."), (19.9, 22.8, "DON'T LOOK DOWN."),
                   (23.4, 26, "DING.")],
         definition=("grit", "[ɡrɪt]  noun • English",
                     ["courage and resolve. the", "strength to keep climbing when",
                      "your arms are burning and", "everyone below says stop."],
                     "don't look down. keep climbing."),
         rock=(["DON'T", "QUIT"], "DON'T QUIT"),
         quote=("DON'T LOOK DOWN.", "KEEP CLIMBING."), music="B"),
]

DUR = dict(intro=3.0, p1=T_SPLIT, definition=3.6, rock=3.8, p2=T_END - T_SPLIT, quote=3.6)


def build_scenes(v):
    v["dur_quote"] = DUR["quote"]
    cy = v.get("caption_y", 1560)

    def world_part(t0):
        def fn(ctx, t, frame):
            T = t0 + t
            ctx.save()
            v["world"](ctx, T, frame)
            ctx.restore()
            ctx.save()
            ctx.identity_matrix()
            for (a, b, s_) in v["captions"]:
                caption(ctx, s_, fade_win(T, a, b, 0.2), cy)
            ctx.restore()
        return fn

    return [
        ("intro", DUR["intro"], lambda c, t, f: scene_intro(c, t, f, v)),
        ("p1", DUR["p1"], world_part(0.0)),
        ("definition", DUR["definition"], lambda c, t, f: scene_definition(c, t, f, v)),
        ("rock", DUR["rock"], lambda c, t, f: scene_rock(c, t, f, v)),
        ("p2", DUR["p2"], world_part(T_SPLIT)),
        ("quote", DUR["quote"], lambda c, t, f: scene_quote(c, t, f, v)),
    ]


def render_frame(ctx, scenes, gt, frame):
    acc = 0.0
    for i, (name, dur, fn) in enumerate(scenes):
        if gt < acc + dur or i == len(scenes) - 1:
            lt = gt - acc
            ctx.identity_matrix()
            cut = acc > 0 and name not in ("p2",) or name == "p2"
            punch = 1.0 + (0.09 * (1 - ease_out(lt / 0.35)) if acc > 0 else 0.0)
            dx = 5 * math.sin(gt * 1.3) + 3 * math.sin(gt * 3.1)
            dy = 5 * math.sin(gt * 1.7 + 1) + 3 * math.sin(gt * 2.3)
            ctx.translate(W / 2 + dx, H / 2 + dy)
            ctx.rotate(0.006 * math.sin(gt * 0.9) - (0.02 * (1 - ease_out(lt / 0.3)) if acc > 0 else 0))
            ctx.scale(punch * 1.02, punch * 1.02)
            ctx.translate(-W / 2, -H / 2)
            ctx.save()
            fn(ctx, lt, frame)
            ctx.restore()
            ctx.identity_matrix()
            if cut and acc > 0 and lt < 2.5 / FPS:
                ctx.set_source_rgba(1, 1, 1, 0.3)
                ctx.paint()
            return
        acc += dur


# ============================================================================ musique
MUSIC_SETS = {
    "A": ["m1_tension.mp3", "m2_training.mp3", "m3_climax.mp3", "m4_drop.mp3"],
    "B": ["piano_intro.mp3", "m2_training.mp3", "m3_climax.mp3", "phonk_beat.mp3"],
}


def build_music(v, speed, out):
    d_ = DUR
    t1 = d_["intro"] + d_["p1"] * 0.5
    t2 = d_["intro"] + d_["p1"]
    t3 = t2 + d_["definition"] + d_["rock"]
    total = sum(d_.values())
    bounds = [(0, t1), (t1, t2), (t2, t3), (t3, total)]
    files = MUSIC_SETS[v["music"]]
    inputs, filt, labels = [], [], []
    for i, (f, (a, b)) in enumerate(zip(files, bounds)):
        inputs += ["-stream_loop", "-1", "-i", os.path.join(SND, f)]
        start, ln = a / speed, (b - a) / speed
        last = i == 3
        filt.append(f"[{i}:a]atrim=0:{ln + 0.45:.3f},afade=t=in:d={0.05 if i == 0 else 0.3},"
                    f"afade=t=out:st={max(0.1, ln - (1.6 if last else 0.05)):.3f}:d={1.6 if last else 0.5},"
                    f"adelay={int(start * 1000)}|{int(start * 1000)}[m{i}]")
        labels.append(f"[m{i}]")
    filt.append("".join(labels) + f"amix=inputs=4:normalize=0,atrim=0:{total / speed:.3f},"
                "loudnorm=I=-14:TP=-1.5[out]")
    subprocess.check_call(["ffmpeg", "-y", "-v", "error"] + inputs +
                          ["-filter_complex", ";".join(filt), "-map", "[out]", "-ar", "44100",
                           "-c:a", "aac", "-b:a", "192k", out])


# ============================================================================ rendu
def render_video(idx, speed=1.5, mb=3, outdir="output/serie", preview=False):
    v = VIDEOS[idx]
    scenes = build_scenes(v)
    total = sum(s[1] for s in scenes)
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surface)
    os.makedirs(outdir, exist_ok=True)
    if preview:
        from PIL import Image
        times = [0.15 + i * (total - 0.3) / 19 for i in range(20)]
        sheet = Image.new("RGB", (216 * 10, 384 * 2))
        for i, tt in enumerate(times):
            render_frame(ctx, scenes, tt, int(tt * FPS))
            surface.flush()
            arr = np.ndarray((H, W, 4), np.uint8, surface.get_data())
            im = Image.fromarray(arr[..., [2, 1, 0]].copy()).resize((216, 384))
            sheet.paste(im, ((i % 10) * 216, (i // 10) * 384))
        out = os.path.join(outdir, f"{v['key']}_preview.png")
        sheet.save(out)
        return out
    suffix = "" if speed == 1 else f"_x{speed:g}"
    out = os.path.join(outdir, f"{v['key']}{suffix}.mp4")
    music = os.path.join(outdir, f".{v['key']}{suffix}.m4a")
    build_music(v, speed, music)
    n_frames = int(total * FPS / speed)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-i", music, "-map", "0:v", "-map", "1:a", "-c:a", "copy", "-shortest",
           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
           "-movflags", "+faststart", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(n_frames):
        gt = f / FPS * speed
        acc = None
        for k in range(mb):
            render_frame(ctx, scenes, gt + ((k / mb - 0.5) * 0.7 / FPS * speed if mb > 1 else 0), f)
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
    ap.add_argument("--video", default="all", help="1-10 ou all")
    ap.add_argument("--speed", type=float, default=1.5)
    ap.add_argument("--mb", type=int, default=3)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--outdir", default="output/serie")
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
