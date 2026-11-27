"""Rendu image par image 1080x1920 @30 i/s, puis encodage H.264 + mux audio."""
import math, os, subprocess, sys, random
from functools import lru_cache
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
from timeline import ROOT, LEVELS, LEVEL_ORDER, QTEXT, build

W, H = 1080, 1920
A = os.path.join(ROOT, "assets")
F_TITLE = os.path.join(A, "fonts", "LuckiestGuy-Regular.ttf")
F_BODY = os.path.join(A, "fonts", "Baloo2-ExtraBold.ttf")
F_EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
TL = build()
FPS = TL["fps"]
DUR = TL["duration"]
QS = TL["questions"]
NQ = len(QS)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


@lru_cache(None)
def font(path, size):
    return ImageFont.truetype(path, size)


def ease_out_back(x, s=1.9):
    x = min(max(x, 0), 1) - 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


def ease_out(x):
    x = min(max(x, 0), 1)
    return 1 - (1 - x) ** 3


def ease_in_out(x):
    x = min(max(x, 0), 1)
    return 3 * x * x - 2 * x ** 3


@lru_cache(512)
def text_img(text, path, size, fill=WHITE, stroke=9, shadow=True):
    f = font(path, size)
    lines = text.split("\n")
    d0 = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    boxes = [d0.textbbox((0, 0), l, font=f, stroke_width=stroke) for l in lines]
    lh = int(size * 1.08)
    wmax = max(b[2] - b[0] for b in boxes)
    pad = 20
    im = Image.new("RGBA", (wmax + 2 * pad, lh * len(lines) + 2 * pad + 10), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for k, (l, b) in enumerate(zip(lines, boxes)):
        x = pad + (wmax - (b[2] - b[0])) / 2 - b[0]
        y = pad + k * lh - b[1] + (lh - (b[3] - b[1])) / 2
        if shadow:
            d.text((x + 5, y + 7), l, font=f, fill=(0, 0, 0, 150), stroke_width=stroke, stroke_fill=(0, 0, 0, 150))
        d.text((x, y), l, font=f, fill=fill, stroke_width=stroke, stroke_fill=BLACK)
    return im


def fit_text(text, path, size, maxw, **kw):
    while size > 20:
        im = text_img(text, path, size, **kw)
        if im.width - 40 <= maxw:
            return im
        size -= 2
    return text_img(text, path, size, **kw)


def paste_center(base, im, cx, cy, scale=1.0, alpha=1.0):
    if scale <= 0.01 or alpha <= 0.01:
        return
    if abs(scale - 1) > 1e-3:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BILINEAR)
    if alpha < 1:
        im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    base.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))


def mix(c1, c2, k):
    return tuple(int(a + (b - a) * k) for a, b in zip(c1, c2))


# ---------------- ASSETS PRÉ-CALCULÉS ----------------
def make_backgrounds():
    flags = [Image.open(os.path.join(A, "flags_bg", f)).convert("RGB") for f in sorted(os.listdir(os.path.join(A, "flags_bg")))]
    BW, BH = 1300, 2200
    col = Image.new("RGB", (BW, BH), (20, 20, 40))
    random.seed(3)
    y = -60; row = 0
    while y < BH:
        x = -120 + (row % 2) * 150
        while x < BW:
            f = random.choice(flags).resize((300, 200), Image.BILINEAR).rotate(random.uniform(-8, 8), expand=True, fillcolor=(20, 20, 40))
            col.paste(f, (x, y)); x += 310
        y += 215; row += 1
    col = col.filter(ImageFilter.GaussianBlur(14))
    arr = np.asarray(col).astype(np.float32) / 255
    gray = arr.mean(axis=2, keepdims=True)
    arr = 0.35 * arr + 0.65 * gray
    yy, xx = np.mgrid[0:BH, 0:BW]
    vign = 1 - 0.55 * (((xx - BW / 2) / (BW / 1.3)) ** 2 + ((yy - BH / 2) / (BH / 1.4)) ** 2)
    out = {}
    for name, inten in zip(LEVEL_ORDER, [0.35, 0.40, 0.48, 0.58]):
        c = np.array(LEVELS[name]["color"], np.float32) / 255
        tint = arr * 0.45 * (1 - inten) + c * inten * (0.35 + 0.65 * arr)
        if name == "EXTREME":
            acc = np.array(LEVELS[name]["accent"], np.float32) / 255
            tint = tint * (1 - 0.35 * yy[..., None] / BH) + acc * 0.35 * (yy[..., None] / BH) * 0.6
        tint = tint * np.clip(vign, 0.2, 1)[..., None] * 0.85
        out[name] = Image.fromarray((np.clip(tint, 0, 1) * 255).astype(np.uint8)).convert("RGBA")
    return out


def rounded_mask(size, r):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), r, fill=255)
    return m


def make_card(q):
    im = Image.open(os.path.join(A, "flags", q["flag"] + ".png")).convert("RGBA")
    maxw, maxh = 520, 540
    s = min(maxw / im.width, maxh / im.height)
    fw, fh = int(im.width * s), int(im.height * s)
    im = im.resize((fw, fh), Image.LANCZOS)
    # sature / contraste léger pour ressortir sur téléphone
    border = 12; pad = 40
    cw, ch = fw + 2 * border, fh + 2 * border
    card = Image.new("RGBA", (cw + 2 * pad, ch + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("RGBA", card.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((pad + 6, pad + 14, pad + cw + 6, pad + ch + 14), 34, fill=(0, 0, 0, 170))
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    card.alpha_composite(sh)
    frame = Image.new("RGBA", (cw, ch), LEVELS[q["level"]]["color"] + (255,))
    inner = Image.new("RGBA", (fw, fh), (255, 255, 255, 255))
    inner.alpha_composite(im)
    frame.paste(inner, (border, border), rounded_mask((fw, fh), 22))
    card.paste(frame, (pad, pad), rounded_mask((cw, ch), 32))
    return card


def make_title():
    im = Image.new("RGBA", (900, 140), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, 899, 139), 40, fill=(18, 22, 48, 245), outline=WHITE, width=6)
    # bande de couleurs des niveaux (signature de la chaîne)
    seg = 900 / 4
    for k, n in enumerate(LEVEL_ORDER):
        d.rectangle((int(k * seg) + (30 if k == 0 else 0), 118, int((k + 1) * seg) - (30 if k == 3 else 0), 132), fill=LEVELS[n]["color"])
    t = text_img("QUIZ DRAPEAUX", F_TITLE, 86, stroke=7, shadow=False)
    im.alpha_composite(t, (int(470 - t.width / 2), int(66 - t.height / 2)))
    # petit logo de chaîne : globe emoji dans une pastille
    try:
        ef = ImageFont.truetype(F_EMOJI, 109)
        e = Image.new("RGBA", (140, 140), (0, 0, 0, 0))
        ImageDraw.Draw(e).text((6, 6), "🌍", font=ef, embedded_color=True)
        e = e.crop(e.getbbox()).resize((84, 84), Image.LANCZOS)
        im.alpha_composite(e, (28, 24))
    except Exception as ex:
        print("emoji:", ex)
    return im


def make_burst(color):
    S = 900
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = S / 2
    for k in range(16):
        a0 = k * 2 * math.pi / 16; a1 = a0 + math.pi / 26
        d.polygon([(c, c), (c + S * math.cos(a0), c + S * math.sin(a0)), (c + S * math.cos(a1), c + S * math.sin(a1))],
                  fill=color + (110,) if k % 2 else (255, 255, 255, 90))
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).ellipse((0, 0, S, S), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(80))
    im.putalpha(ImageChops.multiply(im.getchannel("A"), m))
    return im


def make_check(color=(0x2E, 0xCC, 0x40)):
    im = Image.new("RGBA", (130, 130), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((5, 5, 125, 125), fill=color, outline=WHITE, width=8)
    d.line([(36, 68), (57, 90), (95, 44)], fill=WHITE, width=16, joint="curve")
    return im


def make_qbadge(color):
    im = Image.new("RGBA", (130, 130), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((5, 5, 125, 125), fill=color, outline=WHITE, width=8)
    t = text_img("?", F_TITLE, 84, stroke=5, shadow=False)
    im.alpha_composite(t, (int(65 - t.width / 2), int(70 - t.height / 2)))
    return im


BGS = make_backgrounds()
CARDS = [make_card(q) for q in QS]
TITLE = make_title()
BURSTS = {n: make_burst(LEVELS[n]["color"]) for n in LEVEL_ORDER}
CHECK = make_check()
QBADGE = {n: make_qbadge(LEVELS[n]["color"]) for n in LEVEL_ORDER}

# ---------------- ÉCHELLE ----------------
LADDER_X0, LADDER_X1, LADDER_Y0, LADDER_Y1 = 40, 310, 345, 1415
rows = []
for n in LEVEL_ORDER:
    rows.append(("label", n))
    for q in QS:
        if q["level"] == n:
            rows.append(("q", q["idx"]))
ROW_H = (LADDER_Y1 - LADDER_Y0) / len(rows)
ROW_Y = {}
for k, r in enumerate(rows):
    ROW_Y[r] = LADDER_Y0 + ROW_H * (k + 0.5)


def ladder_slot(idx):
    return (LADDER_X0 + 175, ROW_Y[("q", idx)])


def current_q(t):
    cur = None
    for q in QS:
        if t >= q["appear"]:
            cur = q
    return cur


def draw_ladder(img, t, cur, loop_fade):
    d = ImageDraw.Draw(img)
    cur_level_i = LEVEL_ORDER.index(cur["level"]) if cur else 0
    in_concl = t >= TL["conclusion"]
    pulse = 0.5 + 0.5 * math.cos(2 * math.pi * (t % 0.5) / 0.5)
    for r in rows:
        y = ROW_Y[r]
        if r[0] == "label":
            n = r[1]; li = LEVEL_ORDER.index(n)
            on = li <= cur_level_i or in_concl
            col = LEVELS[n]["color"]
            h = ROW_H * 0.78
            fill = col + (255,) if on else mix(col, (40, 40, 60), 0.6) + (200,)
            d.rounded_rectangle((LADDER_X0, y - h / 2, LADDER_X1 - 20, y + h / 2), 18, fill=fill, outline=(255, 255, 255, 255 if on else 90), width=4)
            txt = LEVELS[n]["label"].upper()
            ti = fit_text(txt, F_TITLE, 40, LADDER_X1 - LADDER_X0 - 50, stroke=5, shadow=False,
                          fill=WHITE if on else (200, 200, 200))
            paste_center(img, ti, (LADDER_X0 + LADDER_X1 - 20) / 2, y + 3)
        else:
            idx = r[1]; q = QS[idx]
            h = ROW_H * 0.82
            is_cur = cur is not None and cur["idx"] == idx and not in_concl and t < q["end"]
            ans_t = q["reveal"] + 0.7
            answered = t >= ans_t
            box_fill = (15, 18, 40, 205)
            d.rounded_rectangle((LADDER_X0, y - h / 2, LADDER_X1 - 20, y + h / 2), 16, fill=box_fill,
                                outline=(255, 255, 255, 60), width=2)
            if is_cur:
                col = LEVELS[q["level"]]["color"]
                glow = Image.new("RGBA", (LADDER_X1 - LADDER_X0 + 40, int(h) + 40), (0, 0, 0, 0))
                ImageDraw.Draw(glow).rounded_rectangle((14, 14, glow.width - 34, glow.height - 14), 18, outline=col + (255,), width=10)
                glow = glow.filter(ImageFilter.GaussianBlur(7 + 5 * pulse))
                img.alpha_composite(glow, (LADDER_X0 - 14, int(y - h / 2) - 14))
                d.rounded_rectangle((LADDER_X0, y - h / 2, LADDER_X1 - 20, y + h / 2), 16, fill=mix(col, (15, 18, 40), 0.55) + (235,),
                                    outline=WHITE, width=4 + int(2 * pulse))
            num = text_img(f"{idx + 1})", F_TITLE, 40, stroke=5, shadow=False)
            img.alpha_composite(num, (LADDER_X0 + 8 - 14, int(y - num.height / 2 + 3)))
            if answered and loop_fade > 0:
                k = (t - ans_t) / 0.2
                sc = ease_out_back(k) if k < 1 else 1.0
                ai = fit_text(q["short"], F_BODY, 40, LADDER_X1 - LADDER_X0 - 95, stroke=5, shadow=False,
                              fill=LEVELS[q["level"]]["color"] if q["level"] != "EXTREME" else (255, 120, 140))
                paste_center(img, ai, LADDER_X0 + 75 + (LADDER_X1 - LADDER_X0 - 95) / 2 + 2, y + 2, sc, loop_fade)


def draw_countdown(img, t, q):
    """Compte à rebours 5-4-3-2-1 puis 0 : pastille chiffre + barre qui se vide."""
    col = LEVELS[q["level"]]["color"]
    a, b = q["cd_start"], q["cd_end"]
    step = (b - a) / 5
    ZERO = 0.45  # durée d'affichage du « 0 » (la réponse s'affiche en même temps)
    if t < a or t >= b + ZERO:
        return
    d = ImageDraw.Draw(img)
    cx, cy, r = 425, 1310, 88
    bx0, bx1, by0, by1 = 535, 890, 1268, 1352
    red = (230, 20, 50)
    if t < b:
        k = (t - a) / (b - a)
        n = 5 - int((t - a) / step)          # 5,4,3,2,1
        n = max(1, min(5, n))
        ph = ((t - a) % step) / step          # phase dans le chiffre
        last = n == 1
        blink = last and int(t * 10) % 2 == 0
        # barre
        d.rounded_rectangle((bx0, by0, bx1, by1), 42, fill=(10, 12, 30, 230), outline=WHITE, width=6)
        fw = int((bx1 - bx0 - 20) * (1 - k))
        if fw > 26:
            d.rounded_rectangle((bx0 + 10, by0 + 10, bx0 + 10 + fw, by1 - 10), 32,
                                fill=(WHITE if blink else (red if last else col)) + (255,))
        # pastille
        ring = red if last else col
        d.ellipse((cx - r - 8, cy - r - 8, cx + r + 8, cy + r + 8), fill=WHITE + (255,))
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(15, 18, 40, 255))
        # arc de progression du chiffre en cours
        d.arc((cx - r + 6, cy - r + 6, cx + r - 6, cy + r - 6), -90, -90 + 360 * (1 - ph), fill=ring + (255,), width=14)
        sc = 1.45 - 0.45 * ease_out_back(min(1, ph / 0.35))
        ti = text_img(str(n), F_TITLE, 120, stroke=9, fill=(255, 90, 110) if last else WHITE)
        paste_center(img, ti, cx, cy + 8, sc)
    else:
        kz = (t - b) / ZERO
        d.ellipse((cx - r - 8, cy - r - 8, cx + r + 8, cy + r + 8), fill=WHITE + (255,))
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=red + (255,))
        ti = text_img("0", F_TITLE, 130, stroke=9)
        paste_center(img, ti, cx, cy + 8, 1.5 - 0.5 * ease_out_back(min(1, kz / 0.4)), 1 - max(0, kz - 0.75) * 4)
        d.rounded_rectangle((bx0, by0, bx1, by1), 42, fill=(10, 12, 30, int(230 * (1 - kz))), outline=WHITE + (int(255 * (1 - kz)),), width=6)


def draw_level_banner(img, t, q):
    a, b = q["banner_t"]
    k = (t - a) / (b - a)
    col = LEVELS[q["level"]]["color"]
    band = Image.new("RGBA", (1500, 230), (0, 0, 0, 0))
    d = ImageDraw.Draw(band)
    d.rectangle((0, 20, 1500, 210), fill=col + (250,))
    d.rectangle((0, 20, 1500, 34), fill=WHITE + (255,)); d.rectangle((0, 196, 1500, 210), fill=WHITE + (255,))
    ti = fit_text(q["banner"][0], F_TITLE, 120, 1000, stroke=10)
    band.alpha_composite(ti, (int(750 - ti.width / 2), int(118 - ti.height / 2)))
    band = band.rotate(6, expand=True, resample=Image.BICUBIC)
    if k < 0.3:
        x = -1600 + (1600 + 540) * ease_out(k / 0.3)
    elif k < 0.75:
        x = 540
    else:
        x = 540 + 1700 * ((k - 0.75) / 0.25) ** 2
    paste_center(img, band, x, 700)


def frame(fi):
    t = fi / FPS
    cur = current_q(t)
    in_concl = t >= TL["conclusion"]
    # fond, avec fondu de teinte pendant les bandeaux de niveau
    lvl = cur["level"]
    bg = BGS[lvl]
    if cur.get("banner_t") and t < cur["banner_t"][1]:
        prev = QS[cur["idx"] - 1]["level"]
        kk = (t - cur["banner_t"][0]) / 0.5
        bg = Image.blend(BGS[prev], BGS[lvl], ease_in_out(kk))
    if t > DUR - 0.3:
        bg = Image.blend(BGS[lvl], BGS["FACILE"], ease_in_out(1 - (DUR - t) / 0.3))
    ox = int(110 + 90 * math.sin(t * 0.21)); oy = int(140 + 120 * math.cos(t * 0.17))
    img = bg.crop((ox, oy, ox + W, oy + H)).copy()

    # tremblement d'écran à l'entrée de l'extrême
    shake = (0, 0)
    if cur.get("banner_t") and cur["level"] == "EXTREME" and t < cur["banner_t"][1]:
        amp = 16 * (1 - (t - cur["banner_t"][0]) / 0.5)
        shake = (int(amp * math.sin(t * 157)), int(amp * math.cos(t * 131)))

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    loop_fade = 1.0
    if t > DUR - 0.3:
        loop_fade = max(0, (DUR - t) / 0.3)

    layer.alpha_composite(TITLE, (90, 170))
    draw_ladder(layer, t, cur, loop_fade)

    if not in_concl:
        q = cur
        col = LEVELS[q["level"]]["color"]
        A0, R = q["appear"], q["reveal"]
        card = CARDS[q["idx"]]
        cx, cy = 610, 690
        # rayons derrière la carte à la révélation
        if t >= R:
            kr = (t - R) / 0.9
            if kr < 1:
                burst = BURSTS[q["level"]].rotate((t - R) * 60, resample=Image.BILINEAR)
                paste_center(layer, burst, cx, cy, 0.7 + 0.5 * ease_out(kr), 1 - kr ** 2)
        k_in = (t - A0) / 0.2
        if k_in < 1:
            sc = 0.85 + 0.15 * ease_out_back(k_in)
        elif t < R:
            sc = 1.0 + 0.06 * (t - A0 - 0.2) / max(0.1, R - A0 - 0.2)
        else:
            kr = (t - R) / 0.15
            sc = 1.06 + 0.05 * math.sin(min(kr, 1) * math.pi)
        # la carte est contenue dans la zone image 330-890 : on borne l'échelle
        sc_max = min(1.0, 600 / card.width * 1.0) if False else 1.0
        paste_center(layer, card, cx, cy, sc * min(1.0, 640 / card.width))
        # pastille ? puis coche
        bx = cx + min(card.width, 640) / 2 * sc - 70
        by = cy - (card.height * min(1.0, 640 / card.width)) / 2 * sc + 60
        if t < R:
            p = 1 + 0.08 * math.sin(2 * math.pi * t / 0.5)
            paste_center(layer, QBADGE[q["level"]], min(bx, 860), max(by, 360), p * ease_out_back(k_in), 1)
        else:
            kc = (t - R) / 0.2
            paste_center(layer, CHECK, min(bx, 860), max(by, 360), ease_out_back(kc))

        # texte de la question
        qt = q.get("qtext", QTEXT)
        if q["idx"] == 0 and "qtext" not in q:
            qt = "QUEL EST\nCE PAYS ?"
        elif "qtext" not in q:
            qt = "QUEL EST\nCE PAYS ?"
        qi = fit_text(qt, F_TITLE, 78 if "qtext" not in q else 66, 560, stroke=9,
                      fill=WHITE)
        kt = (t - A0) / 0.2
        tsc = 0.8 + 0.3 * ease_out(kt / 0.6) if kt < 0.6 else 1.1 - 0.1 * ease_out((kt - 0.6) / 0.4) if kt < 1 else 1.0
        # contour couleur niveau : halo derrière le texte
        if not (q["suspense"] and q["suspense"][0] <= t < q["suspense"][1]):
            paste_center(layer, qi, 610, 1120, tsc)

        insusp = q["suspense"] and q["suspense"][0] <= t < q["suspense"][1]
        if insusp:
            layer.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, 120)))
            ks = (t - q["suspense"][0])
            ti = text_img("LA RÉPONSE…", F_TITLE, 84, stroke=8, fill=(255, 220, 230))
            paste_center(layer, ti, 610, 1120, 1 + 0.06 * math.sin(ks * 18))
        draw_countdown(layer, t, q)

        # réponse : pop au centre, puis vol vers l'échelle
        if t >= R:
            kr = t - R
            big = fit_text(q["big"], F_TITLE, 118, 600, stroke=11,
                           fill=WHITE if q["level"] != "EXTREME" else (255, 235, 120))
            sx, sy = ladder_slot(q["idx"])
            if kr < 0.45:
                paste_center(layer, big, 610, 960, ease_out_back(kr / 0.2))
            elif kr < 0.7:
                k = ease_in_out((kr - 0.45) / 0.25)
                paste_center(layer, big, 610 + (sx - 610) * k, 960 + (sy - 960) * k, 1 - 0.72 * k, 1 - 0.3 * k)

        # bandeau de niveau par-dessus le début de la question
        if q.get("banner_t") and q["banner_t"][0] <= t < q["banner_t"][1]:
            draw_level_banner(layer, t, q)
            if q["level"] == "EXTREME":
                fl = 1 - (t - q["banner_t"][0]) / 0.5
                layer.alpha_composite(Image.new("RGBA", (W, H), (200, 0, 30, int(120 * fl))))
    else:
        kc = (t - TL["conclusion"]) / 0.25
        panel = Image.new("RGBA", (580, 720), (0, 0, 0, 0))
        d = ImageDraw.Draw(panel)
        d.rounded_rectangle((10, 10, 570, 710), 40, fill=(15, 18, 45, 235), outline=WHITE, width=8)
        t1 = text_img("TON SCORE", F_TITLE, 76, stroke=8)
        panel.alpha_composite(t1, (int(290 - t1.width / 2), 80))
        t2 = text_img(f"? / {NQ}", F_TITLE, 150, stroke=11, fill=(255, 210, 0))
        p2 = 1 + 0.06 * math.sin(2 * math.pi * t / 0.5)
        t2s = t2.resize((int(t2.width * p2), int(t2.height * p2)), Image.BILINEAR)
        panel.alpha_composite(t2s, (int(290 - t2s.width / 2), int(330 - t2s.height / 2)))
        t3 = text_img("DIS-LE EN\nCOMMENTAIRE !", F_TITLE, 52, stroke=6)
        panel.alpha_composite(t3, (int(290 - t3.width / 2), 450))
        paste_center(layer, panel, 610, 800, ease_out_back(kc), loop_fade)
        t4 = fit_text("Abonne-toi pour le prochain quiz !", F_BODY, 44, 560, stroke=5)
        paste_center(layer, t4, 610, 1250, ease_out_back((t - TL["conclusion"] - 0.15) / 0.25), loop_fade)

    # accroche (pendant la question 1)
    if t < 2.45:
        ka = t / 0.2
        acc = fit_text("SEULS LES VRAIS FANS\nAURONT 10/10 !", F_TITLE, 50, 540, stroke=6, fill=(255, 225, 60))
        a_alpha = 1 if t < 2.25 else (2.45 - t) / 0.2
        paste_center(layer, acc, 610, 400, 0.8 + 0.2 * ease_out_back(ka), a_alpha)

    img.alpha_composite(layer, shake)

    # flash blanc 2 images à la révélation
    for q in QS:
        if q["reveal"] <= t < q["reveal"] + 2 / FPS:
            img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, 150)))
    return img.convert("RGB").tobytes()


def main():
    nframes = int(round(DUR * FPS))
    only = sys.argv[1:] if len(sys.argv) > 1 else None
    if only:  # captures de contrôle : python render.py 1.0 4.6 ...
        os.makedirs(os.path.join(ROOT, "build", "frames"), exist_ok=True)
        for s in only:
            fi = int(float(s) * FPS)
            Image.frombytes("RGB", (W, H), frame(fi)).save(os.path.join(ROOT, "build", "frames", f"f_{float(s):05.2f}.png"))
        return
    out_v = os.path.join(ROOT, "build", "video_noaudio.mp4")
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p",
                           "-profile:v", "high", out_v], stdin=subprocess.PIPE)
    with Pool(4) as p:
        for k, b in enumerate(p.imap(frame, range(nframes), chunksize=6)):
            ff.stdin.write(b)
            if k % 150 == 0:
                print(f"{k}/{nframes}", flush=True)
    ff.stdin.close(); ff.wait()
    final = os.path.join(ROOT, "output", os.environ.get("OUT_NAME", "quiz_drapeaux.mp4"))
    os.makedirs(os.path.dirname(final), exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", out_v, "-i", os.path.join(ROOT, "build", "mix.wav"),
                    "-c:v", "copy", "-af", "volume=5.2dB,alimiter=limit=0.84:level=false", "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-shortest", "-movflags", "+faststart", final], check=True)
    print("OK ->", final)


if __name__ == "__main__":
    main()
