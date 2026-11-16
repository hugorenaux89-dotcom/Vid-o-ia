"""Beat-synced football edit renderer (1080x1920, 60 fps).

Pipeline per frame:
  camera (velocity zoom curve + beat punches + shake) on 2.5D layers (background
  clean-plate / player cut-out) -> radial motion blur -> colour grade (per-section
  LUT + saturation) -> bloom -> light leaks -> text BEHIND the player -> text in
  front -> flash -> chromatic aberration -> vignette -> letterbox -> sharpen -> grain

The timeline (edit/timeline.py) is built from build/beatmap.json produced by
edit/music.py, so every cut, punch and flash lands exactly on the music.

Usage:
  python3 edit/render.py                 # full render -> output/
  python3 edit/render.py --preview 9.3 12.0 26   # write PNG stills at these times
  python3 edit/render.py --from 9 --to 13 --fps 30  # quick partial render
"""
import argparse
import json
import math
import os
import subprocess
import sys
import time
from functools import lru_cache
from multiprocessing import Pool

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import timeline as TL  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
PREP = os.path.join(BUILD, "prep")
FONTS = os.path.join(ROOT, "assets", "fonts")
W, H = 1080, 1920
cv2.setNumThreads(1)


# ------------------------------------------------------------------ easing

def clamp01(x):
    return min(1.0, max(0.0, x))


def ease_out_cubic(x):
    x = clamp01(x)
    return 1 - (1 - x) ** 3


def ease_in_out(x):
    x = clamp01(x)
    return x * x * (3 - 2 * x)


def ease_out_back(x, s=2.2):
    x = clamp01(x) - 1
    return x * x * ((s + 1) * x + s) + 1


def velocity_curve(u, k=2.6):
    """fast -> slow-mo -> fast (the classic 'velocity' edit speed ramp)."""
    u = clamp01(u)
    v = 2 * u - 1
    return 0.5 + 0.5 * math.copysign(abs(v) ** k, v)


def decay(t, h, tau):
    return math.exp(-(t - h) / tau) if t >= h else 0.0


# ------------------------------------------------------------------ assets

@lru_cache(maxsize=40)
def load_src(key):
    d = np.load(os.path.join(PREP, key + ".npz"))
    img = d["img"]
    mask = d["mask"]
    bg = d["bg"]
    bbox = tuple(int(v) for v in d["bbox"])
    return img, mask, bg, bbox


@lru_cache(maxsize=16)
def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


FONT_FILES = {
    "anton": "Anton-Regular.ttf",
    "bebas": "BebasNeue-Regular.ttf",
    "serif": "InstrumentSerif-Italic.ttf",
    "archivo": "ArchivoBlack-Regular.ttf",
}


@lru_cache(maxsize=64)
def text_sprite(text, face, size, style="fill", tracking=0, color=(255, 255, 255),
                stroke=6, shadow=0.55, max_w=1000):
    """Render a text sprite -> premultiplied float32 RGBA (h, w, 4)."""
    f = font(FONT_FILES[face], size)
    # auto-fit width
    def measure(fnt):
        return sum(fnt.getlength(c) for c in text) + tracking * (len(text) - 1)
    while measure(f) > max_w and size > 20:
        size = int(size * 0.94)
        f = font(FONT_FILES[face], size)
    tw = int(measure(f)) + 4
    asc, desc = f.getmetrics()
    th = asc + desc
    pad = int(size * 0.35) + stroke * 2
    Wt, Ht = tw + 2 * pad, th + 2 * pad

    def draw_mask(sw):
        m = Image.new("L", (Wt, Ht), 0)
        d = ImageDraw.Draw(m)
        x = pad
        for c in text:
            d.text((x, pad), c, font=f, fill=255, stroke_width=sw, stroke_fill=255)
            x += f.getlength(c) + tracking
        return np.asarray(m).astype(np.float32) / 255

    fill = draw_mask(0)
    if style == "outline":
        full = draw_mask(stroke)
        a = np.clip(full - fill, 0, 1)
        # keep a hint of the fill so it reads on busy backgrounds
        a = np.clip(a + fill * 0.06, 0, 1)
    else:
        a = fill
    col = np.array(color, np.float32) / 255
    rgba = np.zeros((Ht, Wt, 4), np.float32)
    if shadow > 0:
        sh = cv2.GaussianBlur(a, (0, 0), size * 0.08 + 2) * shadow
        rgba[..., 3] = sh  # black shadow, premultiplied rgb = 0
    rgba[..., :3] = rgba[..., :3] * (1 - a[..., None]) + col * a[..., None]
    rgba[..., 3] = rgba[..., 3] * (1 - a) + a
    return rgba


# ------------------------------------------------------------------ precomputed fields

def _vignette():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    nx = (x - W / 2) / (W / 2)
    ny = (y - H / 2) / (H / 2)
    r = np.sqrt(nx ** 2 * 1.0 + ny ** 2 * 0.75)
    return np.clip(r, 0, 1.6).astype(np.float32)


VIG_R = None
GRAIN = None


def init_worker():
    global VIG_R, GRAIN
    VIG_R = _vignette()
    rng = np.random.default_rng(3)
    GRAIN = []
    for _ in range(10):
        g = rng.standard_normal((H // 3, W // 3)).astype(np.float32)
        g = cv2.resize(g, (W, H), interpolation=cv2.INTER_LINEAR)
        GRAIN.append(g)


# ------------------------------------------------------------------ grading

def make_lut(p):
    x = np.linspace(0, 1, 256, dtype=np.float32)
    luts = []
    for c in range(3):
        y = np.clip(x * p["exposure"], 0, 1)
        k = p["contrast"]
        s = 1 / (1 + np.exp(-k * 4 * (y - 0.5)))
        s0 = 1 / (1 + np.exp(k * 2))
        s1 = 1 / (1 + np.exp(-k * 2))
        y = (s - s0) / (s1 - s0)
        y = y + p["shadow"][c] * (1 - y) ** 3 + p["high"][c] * y ** 3
        y = p["lift"] + y * (1 - p["lift"])
        luts.append(np.clip(y * 255, 0, 255).astype(np.uint8))
    return np.stack(luts, 1)  # 256 x 3


def grade(img_u8, p):
    lut = make_lut(p)
    out = np.empty_like(img_u8)
    for c in range(3):
        out[..., c] = cv2.LUT(img_u8[..., c], lut[:, c])
    f = out.astype(np.float32) * (1 / 255)
    luma = f[..., 0] * 0.299 + f[..., 1] * 0.587 + f[..., 2] * 0.114
    sat = p["sat"]
    if abs(sat - 1) > 1e-3:
        f = luma[..., None] + (f - luma[..., None]) * sat
    return np.clip(f, 0, 1), luma


def bloom(f, luma, amount):
    if amount <= 0:
        return f
    small = cv2.resize(f, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    ls = cv2.resize(luma, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    hl = np.clip((ls - 0.62) / 0.38, 0, 1) ** 2
    b = small * hl[..., None]
    b = cv2.GaussianBlur(b, (0, 0), 10) + cv2.GaussianBlur(b, (0, 0), 28) * 0.7
    b = cv2.resize(b, (W, H), interpolation=cv2.INTER_LINEAR)
    return 1 - (1 - f) * (1 - np.clip(b * amount, 0, 1))


def light_leak(t, amount, seed=0):
    if amount <= 0:
        return None
    w, h = 135, 240
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    acc = np.zeros((h, w, 3), np.float32)
    blobs = [((1.0, 0.42, 0.08), 0.13, 0.9), ((1.0, 0.12, 0.10), 0.09, 1.3),
             ((1.0, 0.78, 0.35), 0.17, 0.6)]
    for i, (col, sp, ph) in enumerate(blobs):
        cx = w * (0.5 + 0.55 * math.sin(t * sp * 2 * math.pi + ph + seed))
        cy = h * (0.5 + 0.45 * math.cos(t * sp * 1.3 * 2 * math.pi + ph * 2 + seed))
        r = w * (0.55 + 0.15 * math.sin(t * 0.7 + i))
        g = np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r * r))
        acc += g[..., None] * np.array(col, np.float32)
    acc = cv2.resize(acc, (W, H), interpolation=cv2.INTER_CUBIC)
    return np.clip(acc * amount, 0, 1)


# ------------------------------------------------------------------ camera

def shake_noise(t, seed):
    return (math.sin(2 * math.pi * 7.3 * t + seed) * 0.5 +
            math.sin(2 * math.pi * 11.7 * t + seed * 2.1) * 0.3 +
            math.sin(2 * math.pi * 17.9 * t + seed * 3.7) * 0.2)


def camera_params(shot, t, env):
    """Return zoom z (relative to cover), focus centre (cx, cy) in src px, rotation deg,
    output offset (ox, oy) px, parallax progress."""
    img, mask, bg, bbox = load_src(shot["src"])
    h, w = img.shape[:2]
    t0, t1 = shot["t0"], shot["t1"]
    u = (t - t0) / max(1e-6, t1 - t0)
    curve = shot.get("curve", "velocity")
    if curve == "velocity":
        p = velocity_curve(u, shot.get("k", 2.6))
    elif curve == "linear":
        p = clamp01(u)
    else:
        p = ease_in_out(u)
    z = shot["z0"] + (shot["z1"] - shot["z0"]) * p

    # stutter zoom (build-ups): one step per roll hit
    if shot.get("stutter"):
        n = sum(1 for h_ in shot["stutter"] if h_ <= t)
        z *= 1 + shot.get("stutter_step", 0.02) * n

    # impact zoom on shot entry ("zoom-out punch")
    if shot.get("entry", 0) > 0:
        z *= 1 + shot["entry"] * decay(t, t0, shot.get("entry_tau", 0.09))
    # beat punches
    for hp in shot.get("punches", []):
        z *= 1 + shot.get("punch_amp", 0.06) * decay(t, hp, 0.11)

    fx, fy = shot.get("focus") or (0.5, 0.35)
    x0, y0, x1, y1 = bbox
    cx = x0 + (x1 - x0) * fx
    cy = y0 + (y1 - y0) * fy
    if shot.get("focus_abs"):
        cx, cy = shot["focus_abs"][0] * w, shot["focus_abs"][1] * h
    pan = shot.get("pan", (0, 0))
    cx += pan[0] * w * (p - 0.5)
    cy += pan[1] * h * (p - 0.5)

    rot = shot.get("r0", 0) + (shot.get("r1", 0) - shot.get("r0", 0)) * p
    amp = env["shake"]
    seed = shot.get("seed", 1.0)
    ox = amp * 34 * shake_noise(t, seed)
    oy = amp * 34 * shake_noise(t + 3.1, seed + 1.7)
    rot += amp * 1.3 * shake_noise(t + 7.7, seed + 0.4)
    # slow handheld drift
    hd = shot.get("handheld", 0.3)
    ox += hd * 6 * math.sin(t * 1.3 + seed)
    oy += hd * 6 * math.sin(t * 1.1 + seed * 2)
    rot += hd * 0.25 * math.sin(t * 0.9 + seed)
    return z, cx, cy, rot, ox, oy, p


def affine(w, h, z, cx, cy, rot, ox, oy):
    cover = max(W / w, H / h)
    S = cover * z
    # keep view inside the source
    hw, hh = W / (2 * S), H / (2 * S)
    cx = min(max(cx, hw), w - hw) if w > 2 * hw else w / 2
    cy = min(max(cy, hh), h - hh) if h > 2 * hh else h / 2
    th = math.radians(rot)
    a, b = S * math.cos(th), S * math.sin(th)
    tx = W / 2 + ox - (a * cx - b * cy)
    ty = H / 2 + oy - (b * cx + a * cy)
    return np.array([[a, -b, tx], [b, a, ty]], np.float32), S


def warp(src, M, interp=cv2.INTER_LINEAR):
    return cv2.warpAffine(src, M, (W, H), flags=interp, borderMode=cv2.BORDER_REFLECT101)


def radial_blur(f, amount, cx=W / 2, cy=H / 2, n=None):
    if amount < 0.002:
        return f
    n = n or int(min(9, 3 + amount * 300))
    acc = f.copy()
    for i in range(1, n):
        s = 1 + amount * i / (n - 1)
        M = np.array([[s, 0, cx - s * cx], [0, s, cy - s * cy]], np.float32)
        acc += cv2.warpAffine(f, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)
    return acc / n


# ------------------------------------------------------------------ text

def text_state(tx, t):
    """Return (scale, dx, dy, alpha) for a text item at time t, or None."""
    ti, to = tx["t_in"], tx["t_out"]
    if t < ti or t >= to:
        return None
    a = 1.0
    s = 1.0
    dx = dy = 0.0
    anim = tx.get("anim", "pop")
    e = t - ti
    if anim == "pop":
        s = 1.35 - 0.35 * ease_out_back(e / 0.2)
        a = clamp01(e / 0.06)
    elif anim == "slide":
        dy = 70 * (1 - ease_out_cubic(e / 0.45))
        a = clamp01(e / 0.25)
    elif anim == "flicker":
        a = 1.0 if e > 0.18 else (1.0 if int(e * 60) % 3 != 1 else 0.15)
    elif anim == "slam":
        s = 2.2 - 1.2 * ease_out_cubic(e / 0.12)
        a = clamp01(e / 0.04)
    elif anim == "fade":
        a = clamp01(e / 0.35)
    # exit
    ex = tx.get("exit", 0.12)
    if to - t < ex:
        a *= clamp01((to - t) / ex)
    # life drift
    s *= 1 + tx.get("drift", 0.05) * clamp01(e / max(0.01, to - ti))
    return s, dx, dy, a * tx.get("opacity", 1.0)


def text_layer(tx, t, shake_xy):
    st = text_state(tx, t)
    if st is None:
        return None
    s, dx, dy, a = st
    if a <= 0.001:
        return None
    spr = text_sprite(tx["text"], tx.get("face", "anton"), tx.get("size", 200),
                      tx.get("style", "fill"), tx.get("tracking", 0),
                      tuple(tx.get("color", (255, 255, 255))), tx.get("stroke", 6),
                      tx.get("shadow", 0.55), tx.get("max_w", 1000))
    sh, sw = spr.shape[:2]
    px, py = tx["pos"]
    px = px * W + dx + shake_xy[0] * tx.get("follow", 0.6)
    py = py * H + dy + shake_xy[1] * tx.get("follow", 0.6)
    M = np.array([[s, 0, px - s * sw / 2], [0, s, py - s * sh / 2]], np.float32)
    lay = cv2.warpAffine(spr, M, (W, H), flags=cv2.INTER_LINEAR,
                         borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    if a < 1:
        lay *= a
    return lay


def over(f, lay):
    return lay[..., :3] + f * (1 - lay[..., 3:4])


# ------------------------------------------------------------------ frame

def render_frame(t):
    T = TL.get()
    shot = T.shot_at(t)
    env = T.env_at(t)
    gp = T.grade_at(t)

    img, mask, bg, bbox = load_src(shot["src"])
    h, w = img.shape[:2]
    z, cx, cy, rot, ox, oy, p = camera_params(shot, t, env)
    M, S = affine(w, h, z, cx, cy, rot, ox, oy)

    # zoom velocity for motion blur
    dt = 1 / 60
    zp = camera_params(shot, max(shot["t0"], t - dt), env)[0]
    zv = abs(math.log(z / zp)) if zp > 0 else 0

    par = shot.get("parallax", 0.0)
    m = warp(mask, M).astype(np.float32) * (1 / 255)

    if shot.get("mode") == "silhouette":
        f = silhouette(m, t, shot)
    else:
        if par > 0:
            k = par * (0.02 + 0.06 * p)
            Mf, _ = affine(w, h, z * (1 + k), cx, cy, rot, ox + par * 22 * p, oy)
            Mb, _ = affine(w, h, z * (1 - k * 0.4), cx, cy, rot, ox - par * 10 * p, oy)
            fg = warp(img, Mf)
            m = warp(mask, Mf).astype(np.float32) * (1 / 255)
            bgw = warp(bg, Mb)
            mm = m[..., None]
            comp = (bgw.astype(np.float32) * (1 - mm) + fg.astype(np.float32) * mm)
            base_u8 = np.clip(comp, 0, 255).astype(np.uint8)
        else:
            base_u8 = warp(img, M)

        # motion blur from camera zoom speed (+ explicit blur requests)
        blur_amt = min(0.12, zv * 1.6) + env.get("blur", 0)
        f, luma = grade(base_u8, gp)
        if blur_amt > 0.002:
            f = radial_blur(f, blur_amt)
            m = radial_blur(m, blur_amt)
            luma = f[..., 0] * 0.299 + f[..., 1] * 0.587 + f[..., 2] * 0.114
        f = bloom(f, luma, gp.get("bloom", 0.25))

    ll = light_leak(t, env.get("leak", 0), shot.get("seed", 0))
    if ll is not None:
        f = 1 - (1 - f) * (1 - ll)

    shake_xy = (ox, oy)
    # texts behind the player
    behind = [x for x in T.texts if x.get("layer") == "behind"]
    front = [x for x in T.texts if x.get("layer") != "behind"]
    if behind:
        base = f
        g = f
        any_ = False
        for tx in behind:
            lay = text_layer(tx, t, shake_xy)
            if lay is not None:
                g = over(g, lay)
                any_ = True
        if any_:
            mm = m[..., None]
            f = g * (1 - mm) + base * mm
    for tx in front:
        lay = text_layer(tx, t, shake_xy)
        if lay is not None:
            f = over(f, lay)

    # flash
    fl = env.get("flash", 0)
    if fl > 0.003:
        fc = np.array(env.get("flash_color", (1, 1, 1)), np.float32)
        f = f + (fc - f) * min(0.92, fl)

    # chromatic aberration (radial)
    ca = env.get("ca", 0)
    if ca > 0.0008:
        out = f.copy()
        for c, s in ((0, 1 + ca), (2, 1 - ca)):
            Mc = np.array([[s, 0, W / 2 - s * W / 2], [0, s, H / 2 - s * H / 2]], np.float32)
            out[..., c] = cv2.warpAffine(f[..., c], Mc, (W, H), flags=cv2.INTER_LINEAR,
                                         borderMode=cv2.BORDER_REFLECT101)
        f = out

    # vignette
    vg = gp.get("vignette", 0.35)
    if vg > 0:
        f = f * (1 - vg * np.clip(VIG_R - 0.35, 0, 1.2)[..., None] ** 1.6)

    # exposure fades (from / to black)
    fb = env.get("black", 0)
    if fb > 0:
        f = f * (1 - fb)

    # sharpen
    sh = gp.get("sharpen", 0.4)
    if sh > 0:
        bl = cv2.GaussianBlur(f, (0, 0), 1.3)
        f = f + (f - bl) * sh

    # letterbox
    lb = int(env.get("letterbox", 0))
    if lb > 0:
        f[:lb] = 0
        f[H - lb:] = 0

    # front-most overlays that must not be letterboxed / graded (credits)
    for tx in T.overlays:
        lay = text_layer(tx, t, (0, 0))
        if lay is not None:
            f = over(f, lay)

    # grain
    ga = gp.get("grain", 0.03)
    if ga > 0:
        g = GRAIN[int(t * 60) % len(GRAIN)]
        lum = np.clip(f.mean(axis=2, keepdims=True), 0, 1)
        f = f + g[..., None] * ga * (0.4 + 0.6 * (1 - np.abs(lum * 2 - 1)))

    return (np.clip(f, 0, 1) * 255 + 0.5).astype(np.uint8)


def silhouette(m, t, shot):
    """Black frame with the player's outline glowing (pre-drop 'breath')."""
    er = cv2.erode(m, np.ones((5, 5), np.uint8))
    edge = np.clip(m - er, 0, 1)
    glow = cv2.GaussianBlur(edge, (0, 0), 6) * 2.5 + cv2.GaussianBlur(edge, (0, 0), 22) * 2.0
    col = np.array(shot.get("rim", (1.0, 0.22, 0.18)), np.float32)
    f = glow[..., None] * col + edge[..., None] * np.array((1, 1, 1), np.float32)
    f += m[..., None] * 0.03
    return np.clip(f, 0, 1)


# ------------------------------------------------------------------ main

def _render_idx(args):
    i, fps = args
    return render_frame(i / fps).tobytes()


def mix_audio(out_wav):
    import soundfile as sf
    T = TL.get()
    music, sr = sf.read(os.path.join(BUILD, "music.wav"), dtype="float32")
    total = len(music)
    mix = music.copy() * 0.92
    for ev in T.sfx:
        path = os.path.join(ROOT, "assets", "sfx", ev["file"])
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "2",
                              "-ar", str(sr), "-"], capture_output=True, check=True).stdout
        x = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
        if ev.get("dur"):
            x = x[: int(ev["dur"] * sr)]
        n = len(x)
        fade_in = int(ev.get("fade_in", 0.005) * sr)
        fade_out = int(ev.get("fade_out", 0.3) * sr)
        env = np.ones(n, np.float32)
        if fade_in:
            env[:fade_in] = np.linspace(0, 1, fade_in)
        if fade_out:
            env[-fade_out:] *= np.linspace(1, 0, fade_out)
        x *= env[:, None] * ev.get("gain", 0.5)
        i = int(ev["t"] * sr)
        j = min(total, i + n)
        if i < total:
            mix[i:j] += x[: j - i]
    # loudness: normalise on the 99.7th percentile so rare SFX peaks are soft-limited
    ref = np.percentile(np.abs(mix), 99.7)
    mix = np.tanh(mix / ref * 1.25) * 0.89  # hard ceiling at 0.89 (~-1 dBFS)
    sf.write(out_wav, mix, sr, subtype="PCM_24")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", nargs="*", type=float)
    ap.add_argument("--from", dest="t_from", type=float, default=0)
    ap.add_argument("--to", dest="t_to", type=float, default=None)
    ap.add_argument("--fps", type=int, default=60)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default=os.path.join(ROOT, "output", "mbappe_edit.mp4"))
    ap.add_argument("--crf", type=int, default=18)
    ap.add_argument("--maxrate", default="14M")
    args = ap.parse_args()

    T = TL.get()
    if args.preview is not None:
        init_worker()
        os.makedirs(os.path.join(BUILD, "preview"), exist_ok=True)
        for t in args.preview:
            t0 = time.time()
            fr = render_frame(t)
            p = os.path.join(BUILD, "preview", "f_%06.2f.jpg" % t)
            Image.fromarray(fr).save(p, quality=92)
            print(p, "%.2fs" % (time.time() - t0))
        return

    t_to = args.t_to if args.t_to is not None else T.duration
    fps = args.fps
    n0, n1 = int(round(args.t_from * fps)), int(round(t_to * fps))
    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    audio = os.path.join(BUILD, "final_audio.wav")
    mix_audio(audio)

    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
           "-ss", f"{args.t_from:.4f}", "-t", f"{(t_to - args.t_from):.4f}", "-i", audio,
           "-map", "0:v", "-map", "1:a",
           "-c:v", "libx264", "-preset", "slow", "-crf", str(args.crf), "-tune", "film",
           "-maxrate", args.maxrate, "-bufsize", str(int(args.maxrate.rstrip("M")) * 2) + "M",
           "-profile:v", "high", "-level", "4.2", "-pix_fmt", "yuv420p",
           "-x264-params", "keyint=%d:min-keyint=%d" % (fps * 2, fps // 2),
           "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
           "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart",
           "-shortest", args.out]
    enc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    with Pool(args.workers, initializer=init_worker) as pool:
        for k, buf in enumerate(pool.imap(_render_idx, ((i, fps) for i in range(n0, n1)), chunksize=4)):
            enc.stdin.write(buf)
            if k % 120 == 0:
                el = time.time() - t0
                print(f"frame {k}/{n1 - n0}  {el:.0f}s  ({(k + 1) / max(el, 1e-3):.1f} fps)", flush=True)
    enc.stdin.close()
    enc.wait()
    print("done", args.out, "%.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
