"""Vidéo 01 — « UN BLOC PAR JOUR »

Deux figurines, MOTIVATION et DISCIPLINE, veulent construire la même tour.
La motivation démarre en feu, puis s'éteint sous la pluie.
La discipline pose un bloc par jour… jusqu'au jour 365.
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from engine.core import (  # noqa: E402
    HEAD_R, H, STAND_HIP, W, Camera, Canvas, Pose, clamp, composite, ease_out, font, hash01, lerp,
    lerp_pt, make_background, seg, skeleton, smooth, stand_pose, text_layer_lines, wrap,
)

FPS = 30
DURATION = 74.0

BW, BH, BP = 96, 26, 30  # largeur, hauteur, pas vertical des blocs

M_X, M_PILE, M_FACE = -180.0, -295.0, -1
D_X, D_TOWER, D_FACE = 120.0, 235.0, 1

# ------------------------------------------------------------------ planning
M_EVENTS = []
t = 10.3
for p in [0.45] * 8 + [0.85, 1.3, 1.9]:
    M_EVENTS.append((t, p))
    t += p

D_GROUND = [(10.3 + i * 1.4, 1.4) for i in range(9)]
CLIMB = (23.2, 24.8)

D_TOP = []
t = 25.0
while t < 45.0:
    p = lerp(1.3, 0.5, smooth((t - 31) / 14))
    D_TOP.append((t, p, "n"))
    t += p
t = 45.0
while t < 47.9:
    D_TOP.append((t, 0.62, "n"))
    t += 0.62
D_TOP.append((48.0, 5.0, "hard"))
D_TOP.append((53.15, 1.0, "n"))
D_TOP.append((54.2, 1.0, "n"))
t = 55.3
while t < 59.4:
    p = lerp(0.4, 0.2, smooth((t - 55.3) / 2.5))
    D_TOP.append((t, p, "n"))
    t += p

N_GROUND = len(D_GROUND)
N_TOTAL = N_GROUND + len(D_TOP)

CAPTIONS = [
    (0.6, 3.6, "Deux personnes."),
    (3.8, 6.9, "Le même rêve."),
    (7.1, 10.0, "Deux façons d'y arriver."),
    (10.3, 14.2, "Au début, tout le monde est motivé."),
    (14.4, 18.6, "Mais la motivation est une émotion."),
    (18.8, 22.6, "Et les émotions passent."),
    (22.8, 26.8, "Il pleut. La fatigue arrive. Elle s'arrête."),
    (27.0, 30.8, "La motivation attend d'avoir envie."),
    (31.0, 34.8, "La discipline n'attend rien."),
    (35.0, 39.4, "Elle pose un bloc. Puis un autre."),
    (39.6, 43.8, "Sans spectateurs. Sans applaudissements."),
    (44.0, 47.8, "Même les jours où rien ne bouge."),
    (48.0, 51.6, "Surtout quand c'est dur."),
    (51.8, 55.4, "Les jours difficiles comptent double."),
    (55.6, 59.8, "Et un jour…"),
    (60.2, 63.6, "Tout le monde parle de chance."),
    (63.8, 67.3, "Ce n'était qu'un bloc par jour."),
]


def placed_count(events, t, place_at=0.55):
    return sum(1 for e in events if t >= e[0] + place_at * e[1])


def active_event(events, t):
    for i, e in enumerate(events):
        if e[0] <= t < e[0] + e[1]:
            return i, (t - e[0]) / e[1]
    return None, None


# ------------------------------------------------------------------ poses
def place_cycle(x0, facing, pile_x, top_y, u, breath):
    """Porter un bloc puis le poser en haut de la pile. Renvoie (pose, centre du bloc tenu ou None)."""
    stand = stand_pose(x0, 0, facing, breath)
    sh = stand.shoulder()
    carry_h = [(x0 + facing * 44, 175), (x0 + facing * 52, 180)]
    carry = Pose(stand.hip, 6, 8, carry_h, stand.feet, facing)
    tgt_y = top_y + BH / 2
    crouch = clamp((sh[1] - 50) - tgt_y, 0, 75)
    hip_r = (x0 + facing * 22, STAND_HIP - crouch)
    lean = 12 + crouch * 0.4
    reach_h = [(pile_x - facing * 52, tgt_y), (pile_x - facing * 44, tgt_y + 4)]
    reach = Pose(hip_r, lean, 14, reach_h, stand.feet, facing)
    if u < 0.2:
        p, hold = carry, True
    elif u < 0.55:
        p, hold = carry.blend(reach, smooth((u - 0.2) / 0.35)), True
    elif u < 0.85:
        p, hold = reach.blend(stand, smooth((u - 0.55) / 0.3)), False
    else:
        p, hold = stand.blend(carry, smooth((u - 0.85) / 0.15)), False
    block = None
    if hold:
        hx = (p.hands[0][0] + p.hands[1][0]) / 2 + facing * (BW / 2 - 6)
        hy = (p.hands[0][1] + p.hands[1][1]) / 2
        block = (hx, hy - BH / 2)
    return p, block


def sit_pose(x0, facing, breath, look_up=0.0):
    hip = (x0, 20 + breath * 0.5)
    feet = [(x0 + facing * 74, 0), (x0 + facing * 84, 0)]
    tilt = lerp(38, -42, look_up)
    lean = lerp(32, 8, look_up)
    p = Pose(hip, lean, tilt, [hip, hip], feet, facing)
    sk = skeleton(p)
    head = sk["head"]
    hands_head = [(head[0] + facing * 18, head[1] - 22), (head[0] + facing * 26, head[1] - 16)]
    hands_knee = [(x0 + facing * 70, 62), (x0 + facing * 78, 66)]
    p.hands = [lerp_pt(a, b, look_up) for a, b in zip(hands_head, hands_knee)]
    return p


def top_cycle(x0, facing, base_h, u, kind, t):
    """Sur la tour : attraper un bloc à côté, sauter, le glisser dessous.
    Renvoie (pose, bloc_en_mouvement(x,y) ou None, hauteur des pieds)."""
    tx = x0
    side_x = tx + facing * 112
    if kind == "hard":
        # 0-0.15 apparition + accroupi ; 0.15-0.62 lutte ; 0.62-0.88 effort lent ; 0.88-1 relève
        shake = math.sin(t * 38) * 3.5 * (seg(u, 0.15, 0.2) - seg(u, 0.6, 0.65))
        if u < 0.62:
            k = smooth(u / 0.15)
            hip = (tx + facing * 18 + shake, base_h + lerp(STAND_HIP, 62, k))
            hands = [(side_x - facing * 50 + shake, base_h + 14), (side_x - facing * 44 + shake, base_h + 18)]
            st = stand_pose(tx, base_h, facing)
            p = Pose(hip, lerp(0, 48, k), 20, [lerp_pt(a, b, k) for a, b in zip(st.hands, hands)], st.feet, facing)
            return p, (side_x + shake * 0.6, base_h), base_h
        v = smooth(seg(u, 0.62, 0.88))
        feet_y = base_h + BP * v + 18 * math.sin(math.pi * v)
        bx = lerp(side_x, tx, v)
        hip = (tx + facing * lerp(18, 6, v), feet_y + lerp(62, 100, v))
        p = Pose(hip, lerp(48, 18, v), 18, [(bx - facing * 50, base_h + 14), (bx - facing * 44, base_h + 18)],
                 [(tx - 14, feet_y), (tx + 18, feet_y)], facing)
        if u < 0.88:
            return p, (bx, base_h), feet_y
        w = smooth(seg(u, 0.88, 1.0))
        st = stand_pose(tx, base_h + BP, facing, 4 * math.sin(t * 5), lean=6, tilt=10)
        return p.blend(st, w), None, base_h + BP

    stand = stand_pose(tx, base_h, facing)
    crouch = Pose((tx + facing * 14, base_h + 82), 38, 16,
                  [(side_x - facing * 50, base_h + 14), (side_x - facing * 44, base_h + 18)],
                  stand.feet, facing)
    if u < 0.35:
        k = smooth(u / 0.35)
        return stand.blend(crouch, k), (side_x, base_h), base_h
    if u < 0.62:
        v = smooth((u - 0.35) / 0.27)
        feet_y = base_h + BP * v + 26 * math.sin(math.pi * v)
        bx = lerp(side_x, tx, v)
        hip = (tx + facing * lerp(14, 4, v), feet_y + lerp(82, 96, v) + 10 * math.sin(math.pi * v))
        p = Pose(hip, lerp(38, 20, v), 12, [(bx - facing * 50, base_h + 14), (bx - facing * 44, base_h + 18)],
                 [(tx - 14, feet_y), (tx + 18, feet_y - 10 * math.sin(math.pi * v))], facing)
        return p, (bx, base_h), feet_y
    w = smooth((u - 0.62) / 0.38)
    land = Pose((tx + facing * 6, base_h + BP + 96), 20, 12,
                [(tx + facing * 40, base_h + BP + 110), (tx + facing * 48, base_h + BP + 114)],
                [(tx - 14, base_h + BP), (tx + 18, base_h + BP)], facing)
    return land.blend(stand_pose(tx, base_h + BP, facing), w), None, base_h + BP


# ------------------------------------------------------------------ état global
def day_at(t):
    if t < 10.3:
        return 0
    if t < 25.0:
        return max(1, placed_count(D_GROUND, t) + 1)
    d0 = N_GROUND + 1
    x = clamp((t - 25.0) / (59.6 - 25.0))
    return int(d0 + (365 - d0) * x**2.1)


def discipline_state(t):
    """Renvoie (pose, bloc_tenu_ou_mobile, hauteur_tour_affichée)."""
    breath = 2.5 * math.sin(t * 2.2 + 1)
    if t < CLIMB[0]:
        i, u = active_event(D_GROUND, t)
        n = placed_count(D_GROUND, t)
        if i is None:
            if t < D_GROUND[0][0] - 0.3:
                return stand_pose(D_X, 0, D_FACE, breath), None, n
            return stand_pose(D_X, 0, D_FACE, breath), None, n
        top = n * BP if u < 0.55 else (n - 1) * BP
        p, blk = place_cycle(D_X, D_FACE, D_TOWER, top, u, breath)
        return p, blk, n
    if t < 25.0:
        n = N_GROUND
        top = n * BP
        u = seg(t, CLIMB[0], CLIMB[1])
        st0 = stand_pose(D_X, 0, D_FACE, breath)
        crouch0 = Pose((D_X + 10, 70), 30, 10, [(D_X + 40, 50), (D_X + 50, 54)], st0.feet, D_FACE)
        if u < 0.25:
            return st0.blend(crouch0, smooth(u / 0.25)), None, n
        if u < 0.7:
            v = (u - 0.25) / 0.45
            x = lerp(D_X, D_TOWER, smooth(v))
            base = lerp(0, top, smooth(v))
            y = base + 110 + 120 * math.sin(math.pi * v)
            p = Pose((x, y), lerp(25, 10, v), 0,
                     [(x + 40, y + 190 - 120 * v), (x + 50, y + 200 - 120 * v)],
                     [(x - 20, y - 70), (x + 26, y - 60)], D_FACE)
            return p, None, n
        w = smooth((u - 0.7) / 0.3)
        land = Pose((D_TOWER + 8, top + 72), 30, 12, [(D_TOWER + 44, top + 70), (D_TOWER + 54, top + 74)],
                    [(D_TOWER - 14, top), (D_TOWER + 18, top)], D_FACE)
        if u >= 1:
            return stand_pose(D_TOWER, top, D_FACE, breath), None, n
        return land.blend(stand_pose(D_TOWER, top, D_FACE, breath), w), None, n
    # sur la tour
    n_top_done = 0
    for (s, p, kind) in D_TOP:
        pa = 0.88 if kind == "hard" else 0.62
        if t >= s + p:
            n_top_done += 1
    i, u = active_event([(s, p) for (s, p, k) in D_TOP], t)
    if i is None:
        n = N_GROUND + n_top_done
        top = n * BP
        if t >= 59.6:
            st = stand_pose(D_TOWER, top, D_FACE, breath, lean=-3, tilt=-6)
            f = smooth(seg(t, 62.0, 63.0))
            sh = st.shoulder()
            st.hands[1] = lerp_pt(st.hands[1], (sh[0] + 14, sh[1] + 102), f)
            return st, None, n
        return stand_pose(D_TOWER, top, D_FACE, breath), None, n
    s, p_, kind = D_TOP[i]
    n_before = N_GROUND + i
    base = n_before * BP
    pose, blk, feet_y = top_cycle(D_TOWER, D_FACE, base, u, kind, t)
    placed = (u >= (0.88 if kind == "hard" else 0.62))
    return pose, blk, n_before + (1 if placed else 0)


def motivation_state(t):
    breath = 2.5 * math.sin(t * 2.6)
    n = placed_count(M_EVENTS, t)
    end_build = M_EVENTS[-1][0] + M_EVENTS[-1][1]
    if t < end_build:
        i, u = active_event(M_EVENTS, t)
        if i is None:
            # avant de commencer : petit sautillement d'excitation après l'allumage
            hop = 0
            if 5.0 < t < 10.3:
                hop = 4 * abs(math.sin(t * 4.5))
            return stand_pose(M_X, 0, M_FACE, breath + hop, lean=-2), None, n
        top = n * BP if u < 0.55 else (n - 1) * BP
        p, blk = place_cycle(M_X, M_FACE, M_PILE, top, u, breath)
        return p, blk, n
    # fatigue
    tired = smooth(seg(t, end_build, end_build + 2.5))
    st = stand_pose(M_X, 0, M_FACE, breath * 0.6 - 6 * tired, lean=14 * tired, tilt=22 * tired)
    if t < 24.0:
        return st, None, n
    look = smooth(seg(t, 60.8, 62.6))
    sit = sit_pose(M_X - 10, -M_FACE, breath * 0.6, look)
    w = smooth(seg(t, 24.0, 25.6))
    if w < 1:
        mid = Pose((M_X - 4, 70), 26, 25, [(M_X + 40, 60), (M_X + 48, 64)], [(M_X + 40, 0), (M_X + 52, 0)], -M_FACE)
        if w < 0.5:
            return st.blend(mid, smooth(w * 2)), None, n
        return mid.blend(sit, smooth(w * 2 - 1)), None, n
    return sit, None, n


def flame_size(t):
    if t < 5.0:
        return 0.0
    s = ease_out(seg(t, 5.0, 5.6)) * (1 + 0.5 * math.exp(-(t - 5.0) * 4))
    s *= lerp(1.0, 1.25, seg(t, 10.0, 11.0))
    s *= lerp(1.0, 0.35, smooth(seg(t, 14.5, 21.5)))
    s *= 1 - smooth(seg(t, 22.9, 23.5))
    return s


def rain_amount(t):
    return smooth(seg(t, 22.3, 24.0)) * (1 - smooth(seg(t, 54.5, 58.5)))


def lightning(t):
    v = 0.0
    for t0 in (35.05, 41.4, 48.1):
        dt = t - t0
        if 0 <= dt < 0.5:
            v = max(v, math.exp(-dt * 9) * (1 + 0.6 * (math.sin(dt * 80) > 0)))
    return v


# ------------------------------------------------------------------ caméra
def camera_track():
    n = int(DURATION * FPS)
    cams = []
    hs = 0.0
    for f in range(n):
        t = f / FPS
        _, _, cnt = discipline_state(t)
        target_h = cnt * BP if t >= CLIMB[0] else 0
        k = 1 - math.exp(-1.0 / FPS * 2.2)
        hs = hs + (target_h - hs) * k
        yt = hs + 330
        yb = -60
        z = min(1.35, 860.0 / (yt - yb))
        if t < 10:
            z = lerp(1.62, 1.35, smooth(t / 10))
        cy = yb + 440 / z
        cx = -25 + (1.35 - z) * 60
        # gros plan pendant l'effort
        wclose = smooth(seg(t, 46.8, 48.4)) * (1 - smooth(seg(t, 53.4, 55.4)))
        if wclose > 0:
            z2, cx2, cy2 = 1.75, D_TOWER + 40, hs + 170
            z = math.exp(lerp(math.log(z), math.log(z2), wclose))
            cx = lerp(cx, cx2, wclose)
            cy = lerp(cy, cy2, wclose)
        # lent zoom final
        if t > 63.4:
            w = smooth(seg(t, 63.4, 68.5))
            z *= 1 + 0.9 * w
            cx = lerp(cx, D_TOWER, w)
            cy = lerp(cy, hs + 60, w)
        cams.append((cx, cy, z))
    return cams


# ------------------------------------------------------------------ rendu
BG = None


def draw_blocks(cv, x, count, base_col, flash_times, t, dim=1.0):
    for i in range(count):
        y0 = i * BP
        c = int(base_col * dim)
        ft = flash_times[i] if i < len(flash_times) else -99
        fl = math.exp(-(t - ft) * 5) if t >= ft else 0
        c = int(min(255, c + 60 * fl))
        cv.rect(x - BW / 2, y0, x + BW / 2, y0 + BH, (c, c, c), radius=3)
        hl = int(min(255, c + 25))
        cv.rect(x - BW / 2 + 4, y0 + BH - 5, x + BW / 2 - 4, y0 + BH - 3, (hl, hl, hl), radius=1)
        if fl > 0.05:
            g = int(200 * fl)
            cv.rect_outline(x - BW / 2 - 6, y0 - 6, x + BW / 2 + 6, y0 + BH + 6, (g, g, g), width=3)


def flash_list_m():
    return [s + 0.55 * p for (s, p) in M_EVENTS]


def flash_list_d():
    out = [s + 0.55 * p for (s, p) in D_GROUND]
    for (s, p, k) in D_TOP:
        out.append(s + (0.88 if k == "hard" else 0.62) * p)
    return out


FL_M = flash_list_m()
FL_D = flash_list_d()


def render_frame(f, cam_t):
    global BG
    if BG is None:
        BG = make_background()
    t = f / FPS
    cam = Camera(*cam_t)
    cv = Canvas(cam)

    # poussière dans la lumière (écran)
    for i in range(70):
        sx = (hash01(i, 1) * W + 12 * math.sin(t * 0.3 + i)) * 2
        sy = ((hash01(i, 2) * H - t * (8 + 14 * hash01(i, 3))) % H) * 2
        r = 1.5 + 2.5 * hash01(i, 4)
        c = int(40 + 50 * hash01(i, 5))
        cv.d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(c, c, c))

    # labels au sol
    intro = smooth(seg(t, 1.0, 2.2))
    li = int(185 * intro)
    if li > 0:
        cv.text_world(M_X - 30, -34, "MOTIVATION", 17, (li, int(li * lerp(1, 0.75, seg(t, 5, 6))), int(li * lerp(1, 0.65, seg(t, 5, 6)))))
        cv.text_world(D_X + 50, -34, "DISCIPLINE", 17, (li, li, li))

    # pile de la motivation : s'éteint avec la pluie
    m_pose, m_blk, m_n = motivation_state(t)
    dim = lerp(1.0, 0.5, smooth(seg(t, 22, 34)))
    draw_blocks(cv, M_PILE, m_n, 232, FL_M, t, dim)

    d_pose, d_blk, d_n = discipline_state(t)
    draw_blocks(cv, D_TOWER, d_n, 240, FL_D, t)

    # blocs tenus / en mouvement (apparition lumineuse)
    for blk, events in ((m_blk, M_EVENTS), (d_blk, None)):
        if blk is None:
            continue
        x, y = blk
        cv.rect(x - BW / 2, y, x + BW / 2, y + BH, (245, 245, 245), radius=3)

    # figurines
    fade_in = smooth(seg(t, 0.2, 1.4))
    fc = int(255 * fade_in)
    bc = int(150 * fade_in)
    m_front = (fc, fc, fc)
    m_dim = lerp(1.0, 0.72, smooth(seg(t, 20, 26)))
    m_front = tuple(int(v * m_dim) for v in m_front)
    m_sk = cv.figure(m_pose, m_front, (int(bc * m_dim),) * 3)
    cv.figure(d_pose, (fc, fc, fc), (bc, bc, bc))

    # flamme + fumée
    fs = flame_size(t)
    cv.flame(m_sk["head"], fs, t, 0.7)
    if t > 22.9:
        for i in range(14):
            age = ((t - 22.9) * 0.6 + i / 14) % 1.0
            if t - 22.9 < age / 0.6:
                continue
            strength = math.exp(-(t - 23.2) / 6)
            hx, hy = m_sk["head"]
            px = hx + 18 * math.sin(age * 6 + i) + 30 * age
            py = hy + HEAD_R + age * 160
            r = 6 + 22 * age
            c = int(70 * (1 - age) * strength)
            if c > 2:
                cv.circle((px, py), r, (c, c, c))

    # pluie (écran)
    ra = rain_amount(t)
    if ra > 0.01:
        nr = int(170 * ra)
        for i in range(nr):
            sp = 2200 + 900 * hash01(i, 7)
            x0 = hash01(i, 8) * (W + 300) - 150
            y0 = (hash01(i, 9) * (H + 400) + t * sp) % (H + 400) - 200
            ln = 40 + 50 * hash01(i, 10)
            c = int((45 + 60 * hash01(i, 11)) * ra)
            cv.d.line([(x0 * 2, y0 * 2), ((x0 - ln * 0.18) * 2, (y0 + ln) * 2)], fill=(c, c, c), width=2)

    # texte (écran, 1x)
    timg = Image.new("RGB", (W, H), (0, 0, 0))
    for (a, b, txt) in CAPTIONS:
        if a <= t < b:
            lines = wrap(txt, 22)
            rev = (t - a) * 34
            alpha = smooth(seg(t, a, a + 0.15)) * (1 - smooth(seg(t, b - 0.35, b)))
            text_layer_lines(timg, lines, 395, 58, reveal=rev, alpha=alpha)
    d = day_at(t)
    if 10.3 <= t < 67.5:
        a = smooth(seg(t, 10.3, 10.8)) * (1 - smooth(seg(t, 67.0, 67.5)))
        big = 1 + 0.6 * math.exp(-max(0, t - 59.6) * 1.6) * (t >= 59.6)
        s = f"JOUR {d:03d}"
        text_layer_lines(timg, [s], 225, int(36 * big), col=(200, 200, 200), weight="Bold", alpha=a)
        dd = ImageDraw.Draw(timg)
        c = int(120 * a)
        dd.line([(W / 2 - 230, 225), (W / 2 - 140 * big, 225)], fill=(c, c, c), width=2)
        dd.line([(W / 2 + 140 * big, 225), (W / 2 + 230, 225)], fill=(c, c, c), width=2)
    # carte titre finale
    if t >= 67.6:
        a = smooth(seg(t, 67.6, 68.3))
        text_layer_lines(timg, ["UN BLOC", "PAR JOUR."], 860, 128, alpha=a, line_h=1.1)
        a2 = smooth(seg(t, 69.2, 69.9))
        text_layer_lines(timg, ["Pose le tien aujourd'hui."], 1060, 40, col=(190, 190, 190), weight="Medium", alpha=a2)

    # projecteur final sur la discipline
    extra = None
    beam = smooth(seg(t, 59.4, 61.0)) * (1 - 0.6 * smooth(seg(t, 67.6, 68.6)))
    if beam > 0.01:
        sk = skeleton(d_pose)
        hx, hy = cam.to_screen(*sk["head"])
        fx, fy = cam.to_screen(d_pose.hip[0], d_pose.feet[0][1])
        q = Image.new("L", (W // 4, H // 4), 0)
        dq = ImageDraw.Draw(q)
        dq.polygon([((hx - 30) / 4, 0), ((hx + 30) / 4, 0), ((fx + 110) / 4, fy / 4), ((fx - 110) / 4, fy / 4)], fill=255)
        q = q.filter(ImageFilter.GaussianBlur(10)).resize((W, H), Image.BILINEAR)
        extra = (np.asarray(q).astype(np.float32) / 255.0 * 0.32 * beam)[:, :, None]

    bright = smooth(seg(t, 0.0, 1.0)) * (1 - smooth(seg(t, 73.0, 74.0)))
    if t >= 67.6:
        pass
    bg_boost = 0.7 * lightning(t) + 0.5 * beam
    # assombrir la scène derrière la carte titre
    fg_img = cv.img
    if t >= 67.4:
        k = 1 - 0.75 * smooth(seg(t, 67.4, 68.4))
        fg_img = Image.eval(fg_img, lambda v: int(v * k))
        if extra is not None:
            extra = extra * k
    out = composite(BG, fg_img, cam, extra_glow=extra, brightness=bright, bg_boost=bg_boost,
                    grain_seed=f, text_img=timg)
    return out


def audio_events():
    ev = []
    for (s, p) in M_EVENTS:
        ev.append({"t": s + 0.55 * p, "type": "thud", "gain": 0.8})
    for (s, p) in D_GROUND:
        ev.append({"t": s + 0.55 * p, "type": "thud", "gain": 1.0})
    for (s, p, k) in D_TOP:
        tt = s + (0.88 if k == "hard" else 0.62) * p
        ev.append({"t": tt, "type": "thud_big" if k == "hard" else "thud", "gain": 1.2 if k == "hard" else (0.9 if p > 0.2 else 0.35)})
    ev.append({"t": 5.0, "type": "ignite"})
    ev.append({"t": 22.9, "type": "extinguish"})
    ev.append({"t": CLIMB[0] + 0.6 * (CLIMB[1] - CLIMB[0]), "type": "thud_big", "gain": 0.8})
    for t0 in (35.05, 41.4, 48.1):
        ev.append({"t": t0, "type": "thunder"})
    ev.append({"t": 59.6, "type": "impact"})
    ev.append({"t": 67.6, "type": "impact"})
    return ev
