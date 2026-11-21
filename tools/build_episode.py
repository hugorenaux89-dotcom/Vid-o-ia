#!/usr/bin/env python3
"""Monte un épisode TikTok 9:16 complet à partir de :
  - build/voice.mp3 + build/alignment.json  (tools/tts.py)
  - build/mus_intro.mp3, build/mus_epic.mp3   (musique : intro sombre / partie épique)
  - build/sfx_riser.mp3, build/sfx_impact.mp3, build/sfx_whoosh.mp3
  - episode.json (scènes, mots surlignés, moment du drop...)
  - clips/*.mp4 optionnels : si un plan réel existe pour une scène, il remplace le fond généré.

Usage : python3 tools/build_episode.py episodes/ep01 [--preview]
Sortie : <episode>/output/<id>.mp4 (1080x1920, 30 i/s, H.264 + AAC, -14 LUFS)
"""
import json
import math
import os
import re
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS, SR = 1080, 1920, 30, 44100
GOLD = (242, 179, 61)
WHITE = (255, 255, 255)
FONT_BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FONT_BOLD = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
RNG = np.random.default_rng(501)


# ----------------------------------------------------------------------------- audio utils
def load_audio(path, ch=2):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", str(ch), "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, ch).copy()


def save_wav(path, x):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ac", str(x.shape[1]), "-ar", str(SR),
                          "-i", "-", path], stdin=subprocess.PIPE)
    p.communicate(x.astype(np.float32).tobytes())


def rms(x):
    return float(np.sqrt(np.mean(x ** 2) + 1e-12))


def db(v):
    return 10 ** (v / 20)


def place(track, clip, t, gain=1.0):
    i = int(round(t * SR))
    if i < 0:
        clip, i = clip[-i:], 0
    n = min(len(clip), len(track) - i)
    if n > 0:
        track[i:i + n] += clip[:n] * gain


def fade(x, fin=0.0, fout=0.0):
    x = x.copy()
    a, b = int(fin * SR), int(fout * SR)
    if a:
        x[:a] *= np.linspace(0, 1, a)[:, None]
    if b:
        x[-b:] *= np.linspace(1, 0, b)[:, None]
    return x


def loud_start(x, thresh_db=-30, win=0.25):
    """Premier instant où la musique devient vraiment audible."""
    n = int(win * SR)
    for k in range(0, len(x) - n, n // 2):
        if rms(x[k:k + n]) > db(thresh_db):
            return k / SR
    return 0.0


# ----------------------------------------------------------------------------- words & timing
def parse_words(al):
    words, cur, st, en = [], "", 0.0, 0.0
    for c, a, b in zip(al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]):
        if c.isspace():
            if cur:
                words.append({"text": cur, "start": st, "end": en})
            cur = ""
        else:
            if not cur:
                st = a
            cur += c
            en = b
    if cur:
        words.append({"text": cur, "start": st, "end": en})
    return [w for w in words if re.search(r"\w", w["text"])]


def norm(s):
    return re.sub(r"[^\w']", "", s.lower().replace("’", "'"))


def find_phrase(words, phrase, start=0):
    toks = [norm(t) for t in phrase.split()]
    for i in range(start, len(words) - len(toks) + 1):
        if all(norm(words[i + k]["text"]) == toks[k] for k in range(len(toks))):
            return i
    raise ValueError(f"phrase introuvable : {phrase!r}")


def tighten(voice, words, cfg):
    """Raccourcit les silences trop longs pour garder un rythme TikTok."""
    max_gap, dram = cfg.get("max_gap", 0.26), cfg.get("dramatic_gap", 0.55)
    drop = set()
    for ph in cfg.get("remove", []):  # phrases coupées au montage
        i0 = find_phrase(words, ph)
        drop.update(range(i0, i0 + len(ph.split())))
    words[:] = [w for k, w in enumerate(words) if k not in drop]
    dram_idx = set()
    for ph in cfg.get("dramatic_before", []):
        try:
            dram_idx.add(find_phrase(words, ph))
        except ValueError:
            pass
    cuts = []  # (start, end) en secondes, dans l'audio original
    for i in range(1, len(words)):
        gap = words[i]["start"] - words[i - 1]["end"]
        target = dram if i in dram_idx else max_gap
        if gap > target + 0.05:
            cs = words[i - 1]["end"] + max(0.14, target * 0.6)
            ce = cs + (gap - target)
            ce = min(ce, words[i]["start"] - 0.04)
            if ce - cs > 0.03:
                cuts.append((cs, ce))
    # voix : début de l'audio jusqu'au 1er mot -> 0.05 s
    lead = max(0.0, words[0]["start"] - 0.05)
    if lead > 0.03:
        cuts.insert(0, (0.0, lead))
    segs, last = [], 0.0
    xf = int(0.008 * SR)
    for cs, ce in cuts:
        seg = voice[int(last * SR):int(cs * SR)].copy()
        if len(seg) > 2 * xf:
            seg[:xf] *= np.linspace(0, 1, xf)[:, None] if last > 0 else 1
            seg[-xf:] *= np.linspace(1, 0, xf)[:, None]
        segs.append(seg)
        last = ce
    tail = voice[int(last * SR):].copy()
    if len(tail) > xf:
        tail[:xf] *= np.linspace(0, 1, xf)[:, None]
    segs.append(tail)
    out = np.concatenate(segs)

    def remap(t):
        shift = 0.0
        for cs, ce in cuts:
            if t >= ce:
                shift += ce - cs
            elif t > cs:
                shift += t - cs
        return t - shift

    for w in words:
        w["start"], w["end"] = remap(w["start"]), remap(w["end"])
    return out


# ----------------------------------------------------------------------------- subtitles
def display_words(words, dcfg):
    merges = dcfg.get("merge", [])
    rep = dcfg.get("replace", {})
    out, i = [], 0
    while i < len(words):
        done = False
        for m in merges:
            toks, label = m[:-1], m[-1]
            if i + len(toks) <= len(words) and all(norm(words[i + k]["text"]) == norm(toks[k]) for k in range(len(toks))):
                trail = re.sub(r"[\w'\-]", "", words[i + len(toks) - 1]["text"])
                out.append({"text": label + trail, "start": words[i]["start"], "end": words[i + len(toks) - 1]["end"]})
                i += len(toks)
                done = True
                break
        if done:
            continue
        w = dict(words[i])
        core = norm(w["text"])
        if core in rep:
            w["text"] = re.sub(r"[\w']+", rep[core], w["text"], count=1)
        out.append(w)
        i += 1
    return out


STOP = {"où", "à", "de", "le", "la", "les", "que", "qui", "tu", "te", "un", "une", "ne", "et", "quand", "on", "pas", "ça"}


def make_chunks(dwords, max_words=3, max_chars=15):
    chunks, cur = [], []
    for w in dwords:
        if cur and len(cur) >= 2 and norm(cur[-1]["text"]) in STOP and not re.search(r"[.!?…,:]$", cur[-1]["text"]) \
                and len(" ".join(x["text"] for x in cur)) >= max_chars - 4:
            last = cur.pop()
            chunks.append(cur)
            cur = [last]
        cur.append(w)
        txt = " ".join(x["text"] for x in cur)
        end_punct = re.search(r"[.!?…,:]$", w["text"]) or w["text"].endswith("...")
        if len(cur) >= max_words or len(txt) >= max_chars or end_punct:
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    return chunks


def clean(t):
    t = t.replace("...", "").replace("…", "")
    t = re.sub(r"[.,:;«»]", "", t)
    return t.upper().strip()


def fit_font(path, text, max_w, size):
    while size > 40:
        f = ImageFont.truetype(path, size)
        if f.getlength(text) <= max_w:
            return f
        size -= 4
    return ImageFont.truetype(path, size)


def render_chunk(chunk, highlight, lit):
    """Image RGBA d'un groupe de mots ; les `lit` premiers mots sont allumés, les suivants atténués."""
    texts = [clean(w["text"]) for w in chunk]
    hl = [norm(w["text"]) in highlight for w in chunk]
    single = len(chunk) == 1
    base = 150 if (single and hl[0]) else (124 if single else 104)
    full = " ".join(texts)
    font = fit_font(FONT_BLACK, full, 940, base)
    space = font.getlength(" ")
    widths = [font.getlength(t) for t in texts]
    tw = sum(widths) + space * (len(texts) - 1)
    pad = 60
    img_w, img_h = int(tw + pad * 2), int(font.size * 1.5 + pad * 2)
    shadow = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
    txt = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
    ds, dt = ImageDraw.Draw(shadow), ImageDraw.Draw(txt)
    x, y = pad, pad
    for k, t in enumerate(texts):
        on = k < lit
        col = GOLD if hl[k] else WHITE
        alpha = 255 if on else 70
        ds.text((x, y + 8), t, font=font, fill=(0, 0, 0, 200 if on else 60))
        dt.text((x, y), t, font=font, fill=col + (alpha,), stroke_width=7, stroke_fill=(0, 0, 0, alpha))
        x += widths[k] + space
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))
    return Image.alpha_composite(shadow, txt)


# ----------------------------------------------------------------------------- visuals
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
VIGNETTE = np.clip(1.0 - 0.75 * (((XX - W / 2) / (W * 0.75)) ** 2 + ((YY - H / 2) / (H * 0.62)) ** 2), 0.15, 1)[..., None]
GRAIN = [RNG.normal(0, 1, (H // 2, W // 2)).astype(np.float32) for _ in range(6)]
GRAIN = [np.kron(g, np.ones((2, 2), np.float32))[..., None] for g in GRAIN]


def vgrad(stops):
    """Dégradé vertical : liste de (position 0..1, (r,g,b) 0..1)."""
    t = np.arange(H, dtype=np.float32) / H
    out = np.zeros((H, 3), np.float32)
    for (p0, c0), (p1, c1) in zip(stops[:-1], stops[1:]):
        m = (t >= p0) & (t <= p1)
        a = ((t[m] - p0) / max(p1 - p0, 1e-6))[:, None]
        out[m] = np.array(c0) * (1 - a) + np.array(c1) * a
    return np.repeat(out[:, None, :], W, axis=1)


def radial(cx, cy, r, color, power=2.0):
    d = np.sqrt((XX - cx) ** 2 + (YY - cy) ** 2) / r
    return (np.clip(1 - d, 0, 1) ** power)[..., None] * np.array(color, np.float32)


def bokeh_layer(n, colors, rmin, rmax, h=int(H * 1.6)):
    img = Image.new("RGB", (W, h), (0, 0, 0))
    d = ImageDraw.Draw(img)
    for _ in range(n):
        x, y = RNG.uniform(0, W), RNG.uniform(0, h)
        r = RNG.uniform(rmin, rmax)
        c = colors[RNG.integers(len(colors))]
        k = RNG.uniform(0.25, 1.0)
        d.ellipse([x - r, y - r, x + r, y + r], fill=tuple(int(v * k) for v in c))
    return np.asarray(img.filter(ImageFilter.GaussianBlur(rmax * 0.45)), np.float32) / 255


def skyline(lit_ratio=0.12, top=0.72):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x = -20
    while x < W:
        bw = RNG.integers(50, 160)
        bh = RNG.integers(int(H * 0.08), int(H * (1 - top) + H * 0.12))
        y0 = H - bh
        d.rectangle([x, y0, x + bw, H], fill=(6, 7, 11, 255))
        for wy in range(int(y0 + 14), H, 26):
            for wx in range(int(x + 8), int(x + bw - 8), 18):
                if RNG.random() < lit_ratio:
                    d.rectangle([wx, wy, wx + 7, wy + 11], fill=(255, 196, 110, 255))
        x += bw + RNG.integers(2, 12)
    return img


def mountains(color=(8, 6, 8)):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    xs = np.arange(W)
    ys = H * 0.80 - (60 * np.sin(xs / 170 + 1.3) + 35 * np.sin(xs / 61 + 0.4) + 18 * np.sin(xs / 23)
                     + 120 * np.exp(-((xs - W * 0.62) / 260) ** 2))
    ImageDraw.Draw(img).polygon([(0, H)] + list(zip(xs.tolist(), ys.tolist())) + [(W, H)], fill=color + (255,))
    return img


def rays(cx, cy, n=14, strength=0.10, color=(1.0, 0.75, 0.4)):
    ang = np.arctan2(YY - cy, XX - cx)
    v = (0.5 + 0.5 * np.cos(ang * n)) ** 6 * np.clip(1 - np.sqrt((XX - cx) ** 2 + (YY - cy) ** 2) / (H * 0.9), 0, 1)
    return v[..., None] * np.array(color, np.float32) * strength


def ghost_layer(text, color=(255, 255, 255), fill_a=16, stroke_a=60):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if not text:
        return img
    f = fit_font(FONT_BLACK, text, W * 0.92, 420)
    d = ImageDraw.Draw(img)
    tw = f.getlength(text)
    d.text(((W - tw) / 2, H * 0.30), text, font=f, fill=color + (fill_a,), stroke_width=3, stroke_fill=color + (stroke_a,))
    return img.filter(ImageFilter.GaussianBlur(1.2))


def over(base, rgba_img):
    a = np.asarray(rgba_img, np.float32) / 255
    return base * (1 - a[..., 3:]) + a[..., :3] * a[..., 3:]


class Scene:
    def __init__(self, spec, t0, t1, ep_dir):
        self.spec, self.t0, self.t1 = spec, t0, t1
        self.style = spec.get("style", "night")
        self.clip_proc = None
        self.bokeh = None
        self.sun = None
        self.fg = None
        clip = spec.get("clip")
        if clip and os.path.exists(os.path.join(ep_dir, clip)):
            self.clip_proc = subprocess.Popen(
                ["ffmpeg", "-v", "error", "-i", os.path.join(ep_dir, clip), "-vf",
                 f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}",
                 "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
            self.last_clip = np.zeros((H, W, 3), np.float32)
        self.base = self.build_base()

    def build_base(self):
        s, g = self.style, self.spec.get("ghost")
        if s == "night":
            b = vgrad([(0, (0.01, 0.015, 0.03)), (1, (0.04, 0.07, 0.13))])
            self.bokeh = bokeh_layer(40, [(90, 140, 255), (255, 170, 80), (160, 190, 255)], 8, 38) * 0.55
            b = over(b, ghost_layer(g))
        elif s == "doubt":
            b = vgrad([(0, (0.025, 0.025, 0.03)), (1, (0.07, 0.06, 0.065))])
            b += radial(W * 0.5, H * 0.18, H * 0.55, (0.10, 0.10, 0.12), 1.6)
            b = over(b, ghost_layer(g, fill_a=22, stroke_a=80))
        elif s == "void":
            b = vgrad([(0, (0.0, 0.0, 0.0)), (1, (0.025, 0.02, 0.03))])
            b = over(b, ghost_layer(g, color=(200, 40, 40), fill_a=40, stroke_a=120))
        elif s == "mirror":
            b = vgrad([(0, (0.015, 0.015, 0.02)), (1, (0.03, 0.03, 0.04))])
            beam = np.exp(-((XX - W / 2) / 170) ** 2)[..., None] * np.array([0.10, 0.11, 0.14], np.float32)
            b += beam * np.clip(1.2 - YY / H, 0, 1)[..., None]
        elif s == "gym":
            b = vgrad([(0, (0.02, 0.02, 0.02)), (1, (0.05, 0.04, 0.035))])
            cone = np.clip(1 - np.abs(XX - W / 2) / (90 + YY * 0.33), 0, 1) ** 1.5
            b += cone[..., None] * np.array([0.32, 0.28, 0.22], np.float32) * np.clip(1.1 - YY / H, 0, 1)[..., None]
            b += radial(W / 2, -40, 260, (0.9, 0.8, 0.6), 2.5)
            self.bokeh = bokeh_layer(70, [(255, 230, 190)], 2, 6) * 0.5
            b = over(b, ghost_layer(g, fill_a=14, stroke_a=55))
        elif s == "clock":
            b = vgrad([(0, (0.01, 0.015, 0.035)), (1, (0.02, 0.03, 0.06))])
            b = over(b, ghost_layer(g, color=(255, 60, 50), fill_a=55, stroke_a=140))
            b += radial(W / 2, H * 0.40, W * 0.9, (0.18, 0.03, 0.02), 2.2)
        elif s == "counter":
            b = vgrad([(0, (0.03, 0.02, 0.01)), (1, (0.11, 0.06, 0.02))])
            b += radial(W / 2, H * 0.32, W * 0.8, (0.20, 0.12, 0.03), 2)
        elif s in ("sunrise", "sunrise_run", "final"):
            hot = 1.25 if s == "final" else 1.0
            b = vgrad([(0, (0.04, 0.05, 0.13)), (0.45, (0.42, 0.20, 0.17)), (0.72, (0.98 * hot, 0.52, 0.18)),
                       (1, (0.35, 0.12, 0.05))])
            b += rays(W * 0.5, H * 0.76, strength=0.12 * hot)
            self.sun = True
            self.fg = mountains() if s != "final" else skyline(0.05)
        elif s == "rooftop":
            b = vgrad([(0, (0.03, 0.03, 0.09)), (0.55, (0.20, 0.10, 0.20)), (0.80, (0.75, 0.38, 0.20)),
                       (1, (0.3, 0.12, 0.08))])
            self.bokeh = bokeh_layer(25, [(255, 200, 140)], 4, 14) * 0.35
            b = over(b, skyline())
        else:
            b = vgrad([(0, (0.02, 0.02, 0.03)), (1, (0.05, 0.05, 0.07))])
        return np.clip(b, 0, 1).astype(np.float32)

    def frame(self, t):
        lt, dur = t - self.t0, max(self.t1 - self.t0, 0.01)
        p = lt / dur
        if self.clip_proc:
            raw = self.clip_proc.stdout.read(W * H * 3)
            if len(raw) == W * H * 3:
                self.last_clip = np.frombuffer(raw, np.uint8).reshape(H, W, 3).astype(np.float32) / 255
            img = self.last_clip * 0.72
        else:
            img = self.base.copy()
            if self.sun:
                rise = H * (0.83 - 0.09 * p) if self.style != "final" else H * 0.70
                img += radial(W / 2, rise, W * 1.1, (0.55, 0.30, 0.10), 2.2) + radial(W / 2, rise, 130, (1, 0.9, 0.7), 1.2)
            if self.fg is not None:
                img = over(img, self.fg)
            if self.bokeh is not None:
                off = int((self.bokeh.shape[0] - H) * (1 - (t * 0.04) % 1))
                img += self.bokeh[off:off + H]
            if self.style == "doubt":  # néon qui vacille
                img *= 0.9 + 0.1 * (math.sin(t * 37) > -0.85)
        # punch-in à la coupe puis lent zoom
        scale = 1.0 + 0.06 * math.exp(-lt * 9) + 0.045 * p
        if scale > 1.001:
            cw, ch = W / scale, H / scale
            x0, y0 = (W - cw) / 2, (H - ch) / 2
            if self.spec.get("flash") and lt < 0.45:  # tremblement au drop
                k = (0.45 - lt) * 40
                x0 += RNG.uniform(-k, k)
                y0 += RNG.uniform(-k, k)
            pil = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
            pil = pil.resize((W, H), Image.BILINEAR, box=(max(0, x0), max(0, y0), min(W, x0 + cw), min(H, y0 + ch)))
            img = np.asarray(pil, np.float32) / 255
        if self.spec.get("flash") and lt < 0.3:
            img = img + (1 - lt / 0.3) ** 2
        return img


# ----------------------------------------------------------------------------- main
def main(ep_dir, preview=False):
    cfg = json.load(open(os.path.join(ep_dir, "episode.json"), encoding="utf-8"))
    bdir = os.path.join(ep_dir, "build")
    odir = os.path.join(ep_dir, "output")
    os.makedirs(odir, exist_ok=True)

    # ---- voix
    words = parse_words(json.load(open(os.path.join(bdir, "alignment.json"), encoding="utf-8")))
    voice = load_audio(os.path.join(bdir, "voice.mp3"), 1)
    voice = tighten(voice, words, cfg.get("tighten", {}))
    tempo = cfg.get("tighten", {}).get("tempo", 1.0)
    if abs(tempo - 1) > 1e-3:
        save_wav(os.path.join(bdir, "_v.wav"), voice)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(bdir, "_v.wav"), "-af", f"atempo={tempo}",
                        os.path.join(bdir, "_vt.wav")], check=True)
        voice = load_audio(os.path.join(bdir, "_vt.wav"), 1)
        for w in words:
            w["start"] /= tempo
            w["end"] /= tempo
    voice_end = words[-1]["end"]
    total = voice_end + 0.35 + cfg.get("end_card_seconds", 1.6)
    N = int(total * SR)
    print(f"durée voix resserrée : {voice_end:.2f}s — vidéo : {total:.2f}s")

    def at(phrase):
        return words[find_phrase(words, phrase)]["start"]

    t_drop = at(cfg["drop_at"])
    t_sil = at(cfg["silence_at"])
    i_sil = find_phrase(words, cfg["silence_at"])
    t_sil_end = words[i_sil + len(cfg["silence_at"].split()) - 1]["end"]

    # ---- mix audio
    v2 = np.repeat(voice, 2, axis=1)
    v2 *= db(-16) / rms(v2[np.abs(v2[:, 0]) > 0.01])
    vt = np.zeros((N, 2), np.float32)
    place(vt, v2, 0.0)

    mt = np.zeros((N, 2), np.float32)
    intro = load_audio(os.path.join(bdir, "mus_intro.mp3"))
    epic = load_audio(os.path.join(bdir, "mus_epic.mp3"))
    intro *= db(-24) / rms(intro[int(len(intro) * 0.3):])
    epic *= db(-21) / rms(epic[int(len(epic) * 0.3):])
    i_off = max(0.0, loud_start(intro, -40) - 0.2)
    seg = intro[int(i_off * SR):]
    need = int(t_drop * SR)
    while len(seg) < need:  # boucle si l'intro est trop courte
        seg = np.concatenate([seg, intro[int(len(intro) * 0.4):]])
    place(mt, fade(seg[:need], 0.02, 0.35), 0.0)
    e_off = max(0.0, loud_start(epic, -26) - 0.05)
    eseg = epic[int(e_off * SR):]
    elen = int((t_sil - t_drop) * SR)
    while len(eseg) < elen:
        eseg = np.concatenate([eseg, epic[int(len(epic) * 0.35):]])
    place(mt, fade(eseg[:elen + int(0.25 * SR)], 0.0, 0.25), t_drop)
    # fin : retour de la musique après « J'ai commencé »
    tail = epic[int(len(epic) * 0.55):]
    tail = fade(tail[:int((total - t_sil_end) * SR)], 0.05, 1.2)
    place(mt, tail, t_sil_end + 0.15, 0.9)

    # ducking sous la voix
    env = np.abs(vt[:, 0])
    k = int(0.12 * SR)
    env = np.convolve(env, np.ones(k) / k, mode="same")
    env = np.clip(env / (np.percentile(env[env > 1e-4], 90) + 1e-9), 0, 1)
    mt *= (1 - 0.45 * env)[:, None]

    st = np.zeros((N, 2), np.float32)
    riser = load_audio(os.path.join(bdir, "sfx_riser.mp3"))
    impact = load_audio(os.path.join(bdir, "sfx_impact.mp3"))
    whoosh = load_audio(os.path.join(bdir, "sfx_whoosh.mp3"))
    riser *= db(-22) / rms(riser)
    impact *= db(-4) / (np.abs(impact).max() + 1e-9)
    whoosh *= db(-30) / rms(whoosh)
    place(st, fade(riser, 0.3, 0.05), t_drop - len(riser) / SR)
    place(st, impact, t_drop - 0.02)
    place(st, impact, t_sil_end + 0.12, 0.8)

    # ---- scènes
    scenes, idx = [], 0
    for sp in cfg["scenes"]:
        idx = find_phrase(words, sp["at"], idx)
        scenes.append([sp, words[idx]["start"]])
    scenes[0][1] = 0.0
    sc_objs = []
    for k, (sp, t0) in enumerate(scenes):
        t1 = scenes[k + 1][1] if k + 1 < len(scenes) else total
        sc_objs.append((sp, t0, t1))
        if 0 < k and not sp.get("flash"):
            place(st, whoosh, t0 - 0.35)

    mix = vt + mt + st
    save_wav(os.path.join(bdir, "_mix.wav"), mix)
    audio_out = os.path.join(bdir, "mix.m4a")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(bdir, "_mix.wav"), "-af",
                    "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", str(SR), "-c:a", "aac", "-b:a", "256k", audio_out], check=True)

    # ---- sous-titres
    highlight = {norm(h) for h in cfg.get("highlight", [])}
    dw = [w for w in display_words(words, cfg.get("display", {})) if clean(w["text"])]
    chunks = make_chunks(dw)
    sub_events = []
    for k, ch in enumerate(chunks):
        s = ch[0]["start"]
        e = chunks[k + 1][0]["start"] if k + 1 < len(chunks) else ch[-1]["end"] + 0.6
        e = min(e, ch[-1]["end"] + 0.9)
        imgs = [render_chunk(ch, highlight, lit) for lit in range(1, len(ch) + 1)]
        sub_events.append((s, e, ch, imgs))
    sub_events[0] = (0.0,) + sub_events[0][1:]
    write_srt(os.path.join(odir, f"{cfg['id']}.srt"), chunks)

    # ---- rendu vidéo
    font_brand = ImageFont.truetype(FONT_BLACK, 150)
    font_small = ImageFont.truetype(FONT_BOLD, 46)
    font_wm = ImageFont.truetype(FONT_BOLD, 34)
    font_counter = ImageFont.truetype(FONT_BLACK, 210)
    font_counter_lbl = ImageFont.truetype(FONT_BOLD, 54)
    counter_scene = next((s for s in sc_objs if s[0]["style"] == "counter"), None)

    out_path = os.path.join(odir, f"{cfg['id']}{'_preview' if preview else ''}.mp4")
    enc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
         "-i", "-", "-i", audio_out, "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
         "-preset", "veryfast" if preview else "slow", "-crf", "23" if preview else "18", "-maxrate", "12M", "-bufsize", "24M",
         "-pix_fmt", "yuv420p", "-profile:v", "high", "-movflags", "+faststart", "-c:a", "copy", "-shortest", out_path],
        stdin=subprocess.PIPE)
    nframes = int(total * FPS)
    live = {}
    for fi in range(nframes):
        t = fi / FPS
        k = max(i for i, s in enumerate(sc_objs) if s[1] <= t + 1e-6)
        if k not in live:
            live = {k: Scene(*sc_objs[k], ep_dir)}
        img = live[k].frame(t)
        img = img * VIGNETTE + GRAIN[fi % 6] * 0.028
        pil = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).convert("RGBA")

        # compteur JOUR 001 -> 180
        if counter_scene and counter_scene[1] <= t < counter_scene[2] + 1.0:
            c0, c1 = counter_scene[1], counter_scene[2]
            q = min(1.0, (t - c0) / max(c1 - c0 - 0.15, 0.1))
            n = 1 + int(179 * (q ** 1.6))
            alpha = 255 if t < c1 else int(255 * max(0, 1 - (t - c1)))
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(lay)
            txt = f"{n:03d}"
            d.text(((W - font_counter.getlength(txt)) / 2, H * 0.22), txt, font=font_counter, fill=GOLD + (alpha,))
            lbl = "J O U R"
            d.text(((W - font_counter_lbl.getlength(lbl)) / 2, H * 0.18), lbl, font=font_counter_lbl,
                   fill=(255, 255, 255, int(alpha * 0.8)))
            pil = Image.alpha_composite(pil, lay)

        # sous-titres (karaoké : mots allumés au fil de la voix)
        for s, e, ch, imgs in sub_events:
            if s <= t < e:
                lit = max(1, sum(1 for w in ch if w["start"] <= t + 0.03))
                im = imgs[min(lit, len(imgs)) - 1]
                pop = 1 + 0.14 * math.exp(-(t - s) * 16)
                if pop > 1.005:
                    im = im.resize((int(im.width * pop), int(im.height * pop)), Image.BILINEAR)
                pil.alpha_composite(im, (int((W - im.width) / 2), int(H * 0.60 - im.height / 2)))
                break

        d = ImageDraw.Draw(pil)
        # filigrane discret après l'accroche (aucun logo au début)
        if 3.0 < t < voice_end:
            d.text((60, 150), cfg.get("brand", ""), font=font_wm, fill=(255, 255, 255, 90))
        # barre de progression
        d.rectangle([0, 0, int(W * t / total), 7], fill=GOLD + (230,))
        # carton de fin
        if t > voice_end + 0.35:
            a = min(1, (t - voice_end - 0.35) / 0.35)
            lay = Image.new("RGBA", (W, H), (0, 0, 0, int(150 * a)))
            dl = ImageDraw.Draw(lay)
            b = cfg.get("brand", "")
            dl.text(((W - font_brand.getlength(b)) / 2, H * 0.40), b, font=font_brand, fill=GOLD + (int(255 * a),))
            for j, line in enumerate(["L'heure où tout commence.", "Épisode 1 / 30 — Jour 1."]):
                dl.text(((W - font_small.getlength(line)) / 2, H * 0.52 + j * 70), line, font=font_small,
                        fill=(255, 255, 255, int(220 * a)))
            pil = Image.alpha_composite(pil, lay)
        enc.stdin.write(pil.convert("RGB").tobytes())
        if fi % 150 == 0:
            print(f"  image {fi}/{nframes}", flush=True)
    enc.stdin.close()
    enc.wait()
    json.dump({"duration": total, "drop": t_drop, "scenes": [(s[0]["at"], round(s[1], 2), round(s[2], 2)) for s in sc_objs],
               "words": [(w["text"], round(w["start"], 2), round(w["end"], 2)) for w in words]},
              open(os.path.join(odir, f"{cfg['id']}_timeline.json"), "w"), ensure_ascii=False, indent=1)
    print("OK ->", out_path)


def write_srt(path, chunks):
    def ts(x):
        ms = int(round(x * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    with open(path, "w", encoding="utf-8") as f:
        for k, ch in enumerate(chunks):
            e = chunks[k + 1][0]["start"] if k + 1 < len(chunks) else ch[-1]["end"] + 0.6
            f.write(f"{k + 1}\n{ts(ch[0]['start'])} --> {ts(min(e, ch[-1]['end'] + 0.9))}\n"
                    f"{clean(' '.join(w['text'] for w in ch))}\n\n")


if __name__ == "__main__":
    main(sys.argv[1], "--preview" in sys.argv)
