#!/usr/bin/env python3
"""Lyrics edit generator: vertical 9:16 video, dark night visuals, neon word-by-word text.

Usage:
  python3 lyrics_edit.py paroles.txt -o sortie.mp4 [--clips dossier_clips] [--pseudo @moncompte]

Lyrics file format (one entry per line, time in seconds or mm:ss.xx):
  0.0    PREMIER
  0.6    MOT
  1:02.5 *BLANC        <- a leading * shows the word in white instead of pink
  # comment lines and blank lines are ignored
  END 72.0             <- total duration of the lyrics part (end card is added after)

The video is exported WITHOUT audio: add the sound in TikTok and start it at the
same point of the song you used to time the file.
"""
import argparse, glob, math, os, random, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
PINK = (255, 31, 209)
WHITE = (245, 245, 250)
FONT = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
FONT_REG = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"


# ---------------------------------------------------------------- lyrics file
def parse_time(s):
    if ":" in s:
        m, sec = s.split(":")
        return int(m) * 60 + float(sec)
    return float(s)


def load_lyrics(path):
    entries, end = [], None
    for raw in open(path, encoding="utf-8"):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        t, _, text = line.partition(" ")
        if t.upper() == "END":
            end = parse_time(text.strip())
            continue
        text = text.strip()
        white = text.startswith("*")
        entries.append((parse_time(t), text.lstrip("*").strip().upper(), white))
    entries.sort(key=lambda e: e[0])
    if end is None:
        end = entries[-1][0] + 2.0
    return entries, end


# ------------------------------------------------------------ text rendering
_text_cache = {}


def text_layer(text, white):
    """RGBA image of the word with a neon glow (cached)."""
    key = (text, white)
    if key in _text_cache:
        return _text_cache[key]
    size = 104
    font = ImageFont.truetype(FONT, size)
    while font.getlength(text) > W * 0.84 and size > 40:
        size -= 4
        font = ImageFont.truetype(FONT, size)
    color = WHITE if white else PINK
    tw = int(font.getlength(text)) + 160
    th = size + 160
    base = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    d = ImageDraw.Draw(base)
    pos = (80, 80 - size * 0.1)
    d.text(pos, text, font=font, fill=color + (255,))
    glow = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    ImageDraw.Draw(glow).text(pos, text, font=font, fill=color + (255,))
    wide = glow.filter(ImageFilter.GaussianBlur(26))
    tight = glow.filter(ImageFilter.GaussianBlur(8))
    out = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    for layer, k in ((wide, 0.9), (tight, 0.8)):
        a = np.asarray(layer).copy()
        a[..., 3] = (a[..., 3] * k).astype(np.uint8)
        out = Image.alpha_composite(out, Image.fromarray(a))
    # thin dark outline for readability on bright frames
    shadow = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).text((pos[0] + 3, pos[1] + 4), text, font=font, fill=(0, 0, 0, 160))
    out = Image.alpha_composite(out, shadow)
    out = Image.alpha_composite(out, base)
    _text_cache[key] = out
    return out


def paste_word(frame, text, white, age):
    """Pop-in animation: scale 1.35 -> 1.0 and fade in over 0.15 s."""
    layer = text_layer(text, white)
    p = min(1.0, age / 0.15)
    ease = 1 - (1 - p) ** 3
    scale = 1.35 - 0.35 * ease
    if scale != 1.0:
        layer = layer.resize((max(1, int(layer.width * scale)), max(1, int(layer.height * scale))), Image.BILINEAR)
    if p < 1:
        a = np.asarray(layer).copy()
        a[..., 3] = (a[..., 3] * ease).astype(np.uint8)
        layer = Image.fromarray(a)
    cx, cy = W // 2, int(H * 0.47)
    frame.alpha_composite(layer, (cx - layer.width // 2, cy - layer.height // 2))


# ---------------------------------------------------- procedural backgrounds
def sky(w, h, top, bottom, rng):
    t = np.linspace(0, 1, h)[:, None, None]
    g = np.array(top)[None, None] * (1 - t) + np.array(bottom)[None, None] * t
    img = np.repeat(g, w, axis=1)
    stars = rng.random((h, w)) > 0.9993
    img[stars & (np.arange(h)[:, None] < h * 0.5)] = 200
    return img


def building(d, x, y, bw, bh, rng, lit=0.35, color=(6, 6, 12)):
    d.rectangle([x, y, x + bw, H * 2], fill=color)
    win = (255, 190, 120)
    for wy in range(int(y) + 14, int(y + bh), 22):
        for wx in range(int(x) + 10, int(x + bw) - 10, 18):
            if rng.random() < lit:
                k = rng.uniform(0.35, 1.0)
                c = tuple(int(v * k) for v in (win if rng.random() < 0.8 else (170, 200, 255)))
                d.rectangle([wx, wy, wx + 8, wy + 11], fill=c)


def palm(d, x, ground, height, rng):
    pts = [(x + math.sin(i / 10) * 18, ground - i * height / 40) for i in range(41)]
    d.line(pts, fill=(3, 3, 6), width=16)
    tx, ty = pts[-1]
    for k in range(9):
        ang = -math.pi / 2 + (k - 4) * 0.42 + rng.uniform(-0.1, 0.1)
        length = rng.uniform(150, 230)
        leaf = [(tx + math.cos(ang + s * 0.004 * (1 if ang > -math.pi / 2 else -1)) * length * s / 30,
                 ty + math.sin(ang) * length * s / 30 + (s / 30) ** 2 * 120) for s in range(31)]
        d.line(leaf, fill=(3, 3, 6), width=12)


def scene_skyline(seed):
    rng = np.random.default_rng(seed)
    w, h = int(W * 1.2), int(H * 1.2)
    img = Image.fromarray(sky(w, h, (8, 8, 22), (95, 35, 55), rng).astype(np.uint8))
    d = ImageDraw.Draw(img)
    x = -40
    while x < w:
        bw = int(rng.uniform(110, 230))
        bh = rng.uniform(h * 0.25, h * 0.6)
        building(d, x, h - bh, bw, bh, rng, lit=0.25)
        x += bw + int(rng.uniform(-20, 30))
    palm(d, int(w * 0.12), h, h * 0.55, rng)
    return img


def scene_tower(seed):
    rng = np.random.default_rng(seed)
    w, h = int(W * 1.2), int(H * 1.2)
    img = Image.fromarray(sky(w, h, (4, 4, 12), (30, 18, 40), rng).astype(np.uint8))
    d = ImageDraw.Draw(img)
    cx = w // 2 + 60
    # tiered supertall tower
    widths = [360, 300, 240, 180, 130, 90, 50, 20]
    y = h
    for i, bw in enumerate(widths):
        seg = h * 0.11
        building(d, cx - bw // 2, y - seg, bw, seg, rng, lit=0.18, color=(10, 10, 18))
        y -= seg
    d.line([(cx, y), (cx, y - 160)], fill=(20, 20, 30), width=8)
    for side in (-1, 1):
        palm(d, cx + side * 420, h, h * 0.42, rng)
    return img


def scene_fountain(seed):
    rng = np.random.default_rng(seed)
    w, h = int(W * 1.2), int(H * 1.2)
    img = Image.fromarray(sky(w, h, (3, 3, 10), (20, 10, 20), rng).astype(np.uint8))
    d = ImageDraw.Draw(img)
    x = 0
    while x < w:
        bw = int(rng.uniform(80, 160))
        bh = rng.uniform(h * 0.15, h * 0.35)
        building(d, x, h * 0.62 - bh, bw, bh, rng, lit=0.2)
        x += bw + 10
    jets = Image.new("RGB", (w, h), 0)
    jd = ImageDraw.Draw(jets)
    for i in range(14):
        jx = w * (0.05 + 0.9 * i / 13)
        top = h * rng.uniform(0.15, 0.35)
        jd.polygon([(jx - 10, h * 0.66), (jx + 10, h * 0.66), (jx + 30, top), (jx - 30, top)], fill=(230, 110, 70))
    jets = jets.filter(ImageFilter.GaussianBlur(24))
    img = Image.fromarray(np.clip(np.asarray(img, dtype=np.int16) + np.asarray(jets, dtype=np.int16) * 0.8, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    d.rectangle([0, h * 0.66, w, h], fill=(4, 4, 8))
    for _ in range(40):  # crowd silhouettes
        px = rng.uniform(0, w)
        ph = rng.uniform(70, 110)
        d.ellipse([px - 14, h * 0.7 - ph - 26, px + 14, h * 0.7 - ph + 2], fill=(1, 1, 2))
        d.rectangle([px - 20, h * 0.7 - ph, px + 20, h * 0.75], fill=(1, 1, 2))
    return img


def scene_bokeh(seed):
    """Out-of-focus city lights, like seen through a car window."""
    rng = np.random.default_rng(seed)
    w, h = int(W * 1.2), int(H * 1.2)
    img = Image.fromarray(sky(w, h, (6, 4, 14), (14, 6, 18), rng).astype(np.uint8))
    lights = Image.new("RGB", (w, h), 0)
    ld = ImageDraw.Draw(lights)
    palette = [(255, 60, 170), (255, 170, 90), (120, 160, 255), (255, 230, 200)]
    for _ in range(70):
        r = rng.uniform(20, 70)
        x, y = rng.uniform(0, w), rng.uniform(h * 0.2, h * 0.9)
        c = palette[rng.integers(len(palette))]
        k = rng.uniform(0.25, 0.7)
        ld.ellipse([x - r, y - r, x + r, y + r], fill=tuple(int(v * k) for v in c))
    lights = lights.filter(ImageFilter.GaussianBlur(10))
    arr = np.asarray(img, dtype=np.int16) + np.asarray(lights, dtype=np.int16)
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    # car window frame
    d.polygon([(0, 0), (w, 0), (w, h * 0.12), (0, h * 0.2)], fill=(2, 2, 4))
    d.polygon([(0, h * 0.85), (w, h * 0.78), (w, h), (0, h)], fill=(2, 2, 4))
    return img


def scene_rain(seed):
    rng = np.random.default_rng(seed)
    img = scene_skyline(seed + 100)
    streaks = Image.new("L", img.size, 0)
    sd = ImageDraw.Draw(streaks)
    for _ in range(900):
        x, y = rng.uniform(0, img.width), rng.uniform(0, img.height)
        sd.line([(x, y), (x - 6, y + rng.uniform(30, 70))], fill=int(rng.uniform(40, 110)), width=2)
    arr = np.asarray(img, dtype=np.int16) + np.asarray(streaks, dtype=np.int16)[..., None] // 2
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


SCENES = [scene_skyline, scene_bokeh, scene_tower, scene_fountain, scene_rain]


class ProceduralBackground:
    """Ken Burns moves over generated night scenes, cut every `shot` seconds."""

    def __init__(self, total, shot=4.0, seed=7):
        self.shot = shot
        self.cache = {}
        self.seed = seed

    def scene(self, idx):
        if idx not in self.cache:
            self.cache.clear()
            fn = SCENES[idx % len(SCENES)]
            self.cache[idx] = fn(self.seed + idx * 13)
        return self.cache[idx]

    def frame(self, t):
        idx = int(t // self.shot)
        local = (t % self.shot) / self.shot
        img = self.scene(idx)
        rnd = random.Random(idx)
        zoom = 1.0 + 0.08 * (local if rnd.random() < 0.5 else 1 - local)
        cw, ch = int(W * 1.2 / (zoom * 1.0)), int(H * 1.2 / zoom)
        cw, ch = min(cw, img.width), min(ch, img.height)
        dx = (img.width - cw) * (0.5 + 0.35 * (local - 0.5) * (1 if idx % 2 else -1))
        dy = (img.height - ch) * 0.5
        crop = img.crop((int(dx), int(dy), int(dx) + cw, int(dy) + ch)).resize((W, H), Image.BILINEAR)
        return crop


class ClipBackground:
    """Reads user clips (any format) through ffmpeg, scaled/cropped to 9:16, looped."""

    def __init__(self, folder, total, shot=4.0):
        files = sorted(f for f in glob.glob(os.path.join(folder, "*"))
                       if f.lower().endswith((".mp4", ".mov", ".mkv", ".webm", ".m4v")))
        if not files:
            sys.exit(f"Aucun clip vidéo trouvé dans {folder}")
        self.files, self.shot = files, shot
        self.proc, self.cur = None, -1

    def _open(self, idx):
        if self.proc:
            self.proc.kill()
        f = self.files[idx % len(self.files)]
        vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}"
        self.proc = subprocess.Popen(["ffmpeg", "-v", "error", "-stream_loop", "-1", "-i", f, "-vf", vf,
                                      "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
        self.cur = idx

    def frame(self, t):
        idx = int(t // self.shot)
        if idx != self.cur:
            self._open(idx)
        raw = self.proc.stdout.read(W * H * 3)
        return Image.frombytes("RGB", (W, H), raw)


# ------------------------------------------------------------- grading/fx
def make_vignette():
    y, x = np.ogrid[:H, :W]
    r = np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2)
    return np.clip(1.05 - 0.55 * r ** 2, 0.25, 1.0)[..., None].astype(np.float32)


def grade(img, vignette, grain, t, shot):
    a = np.asarray(img, dtype=np.float32)
    a = a * 0.62 * vignette                       # dark moody look
    a[..., 2] *= 1.06                              # slight cool/magenta tint
    a[..., 0] *= 1.03
    a += grain[int(t * FPS) % len(grain)]
    local = t % shot                               # quick dip to black on cuts
    edge = min(local, shot - local)
    if edge < 0.12:
        a *= 0.4 + 0.6 * (edge / 0.12)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")


def watermark(frame, pseudo, t):
    font = ImageFont.truetype(FONT, 30)
    d = ImageDraw.Draw(frame)
    pos = (40, int(H * 0.42)) if int(t // 8) % 2 == 0 else (W - 40 - int(font.getlength(pseudo)), int(H * 0.72))
    d.text((pos[0] + 2, pos[1] + 2), pseudo, font=font, fill=(0, 0, 0, 140))
    d.text(pos, pseudo, font=font, fill=(255, 255, 255, 200))


def end_card(t, pseudo, length):
    """Neutral end card: glitchy search bar that types the account name."""
    img = Image.new("RGBA", (W, H), (14, 16, 26, 255))
    d = ImageDraw.Draw(img)
    bx0, by0, bx1, by1 = 180, 1000, 900, 1100
    for off, col in ((-8, (0, 242, 234)), (8, (255, 0, 80))):
        d.rounded_rectangle([bx0 + off, by0, bx1 + off, by1], 18, fill=col)
    d.rounded_rectangle([bx0, by0, bx1, by1], 18, fill=(255, 255, 255))
    d.rounded_rectangle([bx0 + 14, by0 + 14, bx1 - 14, by1 - 14], 12, fill=(14, 16, 26))
    n = int(len(pseudo) * min(1.0, max(0.0, (t - 0.4) / (length * 0.5))))
    font = ImageFont.truetype(FONT_REG, 46)
    shown = pseudo[:n] + ("|" if int(t * 3) % 2 == 0 else "")
    d.text((bx0 + 50, by0 + 24), shown, font=font, fill=(240, 240, 245))
    big = ImageFont.truetype(FONT, 64)
    title = "ABONNE-TOI"
    d.text(((W - big.getlength(title)) / 2, 840), title, font=big, fill=PINK + (255,))
    return img


# ------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("lyrics")
    ap.add_argument("-o", "--output", default="lyrics_edit.mp4")
    ap.add_argument("--clips", help="dossier de clips vidéo (sinon décors générés)")
    ap.add_argument("--pseudo", default="@moncompte")
    ap.add_argument("--shot", type=float, default=4.0, help="durée d'un plan en secondes")
    ap.add_argument("--endcard", type=float, default=3.0)
    ap.add_argument("--preview", type=float, help="ne rendre que les N premières secondes")
    args = ap.parse_args()

    entries, end = load_lyrics(args.lyrics)
    total = end + args.endcard
    if args.preview:
        total = min(total, args.preview)
    bg = ClipBackground(args.clips, end, args.shot) if args.clips else ProceduralBackground(end, args.shot)
    vignette = make_vignette()
    grain = [np.random.default_rng(i).normal(0, 4, (H, W, 1)).astype(np.float32) for i in range(8)]

    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264",
                            "-preset", "medium", "-crf", "21", "-maxrate", "8M", "-bufsize", "16M", "-pix_fmt", "yuv420p",
                            "-movflags", "+faststart", args.output], stdin=subprocess.PIPE)
    nframes = int(total * FPS)
    for i in range(nframes):
        t = i / FPS
        if t < end:
            frame = grade(bg.frame(t), vignette, grain, t, args.shot)
            cur = [e for e in entries if e[0] <= t]
            if cur:
                start, text, white = cur[-1]
                nxt = next((e[0] for e in entries if e[0] > start), end)
                if t < nxt:
                    paste_word(frame, text, white, t - start)
            watermark(frame, args.pseudo, t)
        else:
            frame = end_card(t - end, args.pseudo, args.endcard)
        enc.stdin.write(frame.convert("RGB").tobytes())
        if i % (FPS * 5) == 0:
            print(f"  {t:5.1f}s / {total:.1f}s", flush=True)
    enc.stdin.close()
    enc.wait()
    print("OK ->", args.output)


if __name__ == "__main__":
    main()
