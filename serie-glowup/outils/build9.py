"""Montage « voix off continue » : python3 build6.py SCRIPTS_DIR VOIX_DIR OUT_DIR [épisodes]"""
import re, os, sys, glob, json, hashlib, subprocess, unicodedata, random, shutil
from PIL import Image, ImageDraw, ImageFont

SCRIPTS, VOIX, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
ONLY = set(int(x) for x in sys.argv[4].split(",")) if len(sys.argv) > 4 else None
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "v9work"); ASSETS = os.path.join(WORK, "assets"); SEG = os.path.join(WORK, "seg")
for d in (WORK, ASSETS, SEG, OUT): os.makedirs(d, exist_ok=True)
FPS, W, H = 30, 1080, 1920
def F(w, s): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{w}.otf", s)
def A(s): return ImageFont.truetype("/root/.fonts/Anton-Regular.ttf", s)
def L(s): return ImageFont.truetype("/root/.fonts/LilitaOne-Regular.ttf", s)
def clean(t): return re.sub(r"\s+", " ", "".join(c for c in t.replace("🅰️", "").replace("🅱️", "") if ord(c) < 0x2190 or c in "→€…’«»★")).strip()
def run(cmd): subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
def dur(p): return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]).decode())

OTHERS = ["SARAH", "KENZO", "SOFIANE", "NADIA", "LINA", "MOUSSA", "BILAL", "INES"]
CUE = [("larmes", ("crying", "tears")), ("panique", ("panick", "scared", "screaming", "terror")), ("choque", ("shock", "surprised", "freez", "double-take")),
       ("colere", ("angry",)), ("sourire", ("smil", "proud", "happy", "laughing", "joy", "applauding", "excited", "big smile")),
       ("triste", ("sad", "disappointed", "disgusted", "hurt")), ("tendre", ("moved", "tender")), ("mefiant", ("skeptical", "suspicious")),
       ("determine", ("serious", "determined")), ("inquiet", ("worried", "nervous"))]
SCENES = [("{SALLE_MUSCU}", "salleMuscu"), ("{CUISINE}", "cuisine"), ("{SALLE_DE_BAIN}", "salleDeBain"), ("{PARC}", "parc"), ("{BOULANGERIE}", "boulangerie"),
          ("{BARBIER}", "barbier"), ("{OPTICIEN}", "opticien"), ("{DENTISTE}", "dentiste"), ("{MAGASIN}", "magasin"), ("{GARAGE}", "garage"),
          ("{SALLE_MARIAGE}", "mariage"), ("{STUDIO_DANSE}", "studioDanse"), ("{CHAMBRE}", "chambre")]

def scene_of(cam, prev):
    for tag, sc in SCENES:
        if tag in cam:
            return sc + ("Nuit" if sc == "chambre" and any(k in cam.lower() for k in ("night", "2 a.m", "dark")) else "")
    return prev or "chambre"

def cue(pid, cam):
    t = "{" + pid + "}"
    if t in cam:
        i = cam.find(t); win = cam[i:i + 90].lower()
        for ex, keys in CUE:
            if any(k in win for k in keys): return ex
    return {"SOFIANE": "sourire", "NADIA": "sourire", "LINA": "sourire", "SARAH": "sourire", "KENZO": "sourire", "MOUSSA": "sourire", "BILAL": "sourire", "INES": "sourire"}.get(pid, "neutre")

def parse():
    eps = {}
    for f in sorted(glob.glob(os.path.join(SCRIPTS, "episodes-*.md"))):
        ep = None; n = 0; cur = None
        for line in open(f, encoding="utf-8"):
            s = line.strip()
            m = re.match(r"## Épisode (\d+) · (J-\d+) · « (.+?) »", s)
            if m:
                ep = int(m.group(1)); n = 0; cur = None
                eps[ep] = {"n": ep, "j": m.group(2), "title": m.group(3), "plans": [], "counter": "", "choice": None}; continue
            if ep is None: continue
            E = eps[ep]
            if s.startswith("📈"):
                m = re.search(r"`(\d+) · (\d+)`", s)
                if m: E["hud"] = (int(m.group(1)), int(m.group(2)))
                continue
            if s.startswith("⏱️"):
                m = re.search(r"📊 `([^`]+)`", s); E["counter"] = m.group(1) if m else ""; continue
            m = re.match(r"\*\*(P\d+) ·", s)
            if m:
                cur = {"tag": m.group(1), "cam": "", "expr": "neutre", "pose": "idle", "notes": [], "voice": None, "vote": None, "choice": None, "head": "", "sfx": None, "kind": None, "p": {}, "sfxb": None}
                E["plans"].append(cur); continue
            if cur is None: continue
            if s.startswith("🎥"): cur["cam"] = s
            elif s.startswith("🎬"):
                m = re.search(r"`([^`]+)`", s)
                if m:
                    w_ = m.group(1).split(); cur["kind"] = w_[0]; cur["p"] = dict(x.split("=", 1) for x in w_[1:] if "=" in x)
            elif s.startswith("🔊"):
                m = re.search(r"`(\w+)(?:@(\d+))?`", s); cur["sfx"] = m.group(1) if m else None; cur["sfxb"] = int(m.group(2)) if m and m.group(2) else None
            elif s.startswith("🔠"):
                m = re.search(r"`([^`]+)`", s); cur["head"] = m.group(1) if m else ""
            elif s.startswith("🎭"):
                m = re.search(r"`(\w+) · (\w+)`", s)
                if m: cur["expr"], cur["pose"] = m.group(1), m.group(2)
            elif s.startswith("📝"):
                bt = re.findall(r"`([^`]+)`", s)
                if "🅰️" in s and len(bt) >= 2: cur["choice"] = (clean(bt[0]), clean(bt[1])); E["choice"] = cur["choice"]
                elif bt and "VOUS AVEZ VOT" in s: cur["vote"] = ("A" if "🅰️" in s else "B", clean(bt[0]).split(":", 1)[-1].strip())
                elif bt:
                    lab = re.findall(r"\*\(([^)]+)\)\*", s); cur["notes"].append((clean(lab[0]) if lab else "", clean(" / ".join(bt))))
            elif s.startswith("🎙️"):
                parts = re.findall(r"«\s*(.+?)\s*»", s)
                if parts:
                    n += 1; cur["voice"] = {"text": clean(" ".join(parts)), "audio": os.path.join(VOIX, f"ep{ep:02d}", f"{n:02d}_{cur['tag']}_VOIX-OFF.mp3")}
    return eps

# ------------------------------------------------------------------ texte
def rr(d, b, r, fill, outline=None, width=0): d.rounded_rectangle(b, r, fill=fill, outline=outline, width=width)
def wrap(text, f, maxw, d):
    out, cur = [], ""
    for w_ in text.split():
        t = (cur + " " + w_).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: out.append(cur); cur = w_
    if cur: out.append(cur)
    return out
SMALL = {"LE", "LA", "LES", "UN", "UNE", "DE", "DES", "DU", "À", "AU", "ET", "SON", "SA", "SES", "CE", "IL", "EN", "DANS", "SUR", "POUR", "PAR", "AVEC", "QUI", "QUE", "NE", "MON", "MA", "MES", "PLUS", "SE", "SI", "OU", "MAIS", "C'EST", "L'", "D'", "QU'"}
def headline(d, text, y0=90, im=None, small=False):
    """gros titre : ~jaune~, *rouge*, reste blanc ; police épaisse, gros contour + ombre portée"""
    toks = []
    for m in re.finditer(r"~[^~]+~|\*[^*]+\*|\S+", text):
        w_ = m.group(0); col = "#ffd23a" if w_.startswith("~") else "#ff3b3b" if w_.startswith("*") else "white"
        for sub in w_.strip("*~").split(): toks.append((sub.upper(), col))
    def lay(f):
        lines, cur = [], []
        for t, c in toks:
            trial = " ".join(x for x, _ in cur + [(t, c)])
            if d.textlength(trial, font=f) > 1000 and cur:
                carry = []
                while len(cur) > 1 and cur[-1][0] in SMALL: carry.insert(0, cur.pop())
                lines.append(cur); cur = carry + [(t, c)]
            else: cur.append((t, c))
        if cur: lines.append(cur)
        return lines
    wid = lambda f, ls: max(d.textlength(" ".join(t for t, _ in ln), font=f) for ln in ls)
    f = L(118 if small else 138); lines = lay(f)
    while (len(lines) > (2 if small else 3) or wid(f, lines) > 1030) and f.size > 64: f = L(f.size - 6); lines = lay(f)
    y = y0
    for ln in lines:
        total = d.textlength(" ".join(t for t, _ in ln), font=f); x = (W - total) / 2
        for t, c in ln:
            d.text((x + 7, y + 9), t, font=f, fill="#000", stroke_width=14, stroke_fill="#000")
            d.text((x, y), t, font=f, fill=c, stroke_width=14, stroke_fill="#111")
            x += d.textlength(t + " ", font=f)
        y += int(f.size * 1.02)
    return y

def chunks(text):
    """groupes de 1 à 3 mots qui ont un sens, coupés à la ponctuation, jamais sur un petit mot"""
    words = re.sub(r"[«»]", "", text).split(); out, cur = [], []
    for w_ in words:
        cur.append(w_); s_ = " ".join(cur)
        end = re.search(r"[.!?…:,]$", w_)
        if (end or len(s_) >= 14 or len(cur) == 3) and w_.upper().strip(".,!?…:") not in SMALL:
            out.append(s_); cur = []
    if cur:
        if out and len(" ".join(cur)) < 6: out[-1] += " " + " ".join(cur)
        else: out.append(" ".join(cur))
    return out

def popc(im, layer_img, k, cy):
    """colle layer_img sur im, agrandi d'un facteur k autour de la ligne cy (effet rebond)"""
    if abs(k - 1) < 1e-3: im.alpha_composite(layer_img); return
    sc = layer_img.resize((int(W * k), int(H * k)), Image.LANCZOS)
    ox, oy = int(W / 2 - W / 2 * k), int(cy - cy * k)
    im.alpha_composite(sc.crop((-ox, -oy, -ox + W, -oy + H)))

def hud(d, st):
    """barre du haut façon série TikTok : JOURS RESTANTS · ARGENT · GLOW-UP"""
    pct, eur = st["hud"]; rest = 31 - st.get("day", 1)
    boxes = [(30, 340), (370, 710), (740, 1050)]
    for (x0, x1) in boxes: rr(d, (x0, 28, x1, 178), 26, (14, 14, 18, 235), "#2a2a33", 4)
    d.text((185, 62), "JOURS RESTANTS", font=A(34), fill="#e8e8e8", anchor="mm"); d.text((185, 128), str(rest), font=A(84), fill="#ffd23a", anchor="mm", stroke_width=4, stroke_fill="#111")
    col = "#7dff7a" if eur >= 0 else "#ff4d4d"
    rr(d, (370, 28, 710, 178), 26, (14, 14, 18, 235), col, 5)
    d.text((540, 62), "ARGENT", font=A(34), fill="#e8e8e8", anchor="mm"); d.text((540, 128), f"{'+' if eur >= 0 else '-'}{abs(eur)} €", font=A(80), fill=col, anchor="mm", stroke_width=4, stroke_fill="#111")
    d.text((895, 62), "GLOW-UP", font=A(34), fill="#e8e8e8", anchor="mm"); d.text((895, 124), f"{pct}%", font=A(84), fill="#7dff7a", anchor="mm", stroke_width=4, stroke_fill="#111")
    rr(d, (770, 160, 1020, 170), 5, (60, 60, 70, 255)); rr(d, (770, 160, 770 + max(8, int(250 * pct / 100)), 170), 5, "#3ccf4e")
    return 200

def layer(st, big=None, hk=1.0, ck=1.0):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    y0 = hud(d, st) if st.get("hud") else 90
    hl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); y = headline(ImageDraw.Draw(hl), st.get("head") or "", y0, small=bool(st.get("hud"))) + 14
    # badge sport / glow-up sous le titre
    for lab, txt in st.get("cards", []):
        u = txt.upper().lstrip("😩🏃🏋️✅🏆✨ ")
        if u.startswith("GLOW-UP DU JOUR"): col, fg, u = "#ffcf4a", "#141414", "★ " + u.split(":", 1)[1].strip()
        elif re.match(r"(MUSCU|COURSE|REPOS|3 KM|.*KM EN|10 KM)", u): col, fg = "#3d8bff", "white"
        else: col, fg = (255, 255, 255, 240), "#141414"; u = (lab.upper() + " : " if lab else "") + txt
        f = L(50) if col != (255, 255, 255, 240) else L(40)
        ls = wrap(u.replace("★ ", ""), f, 900, d)[:2]; h = 26 + len(ls) * (56 if col != (255, 255, 255, 240) else 46)
        rr(d, (80, y, W - 80, y + h), 22, col, "#111", 5); ty = y + 13
        for ln in ls: d.text((W / 2, ty + (28 if col != (255, 255, 255, 240) else 23)), ln, font=f, fill=fg, anchor="mm"); ty += 56 if col != (255, 255, 255, 240) else 46
        y += h + 12
    if st.get("story"):
        x0 = 40; cw = 400; y += 10
        rr(d, (x0, y, x0 + cw, y + 560), 40, (20, 20, 24, 255), "#000", 10)
        g = Image.new("RGBA", (cw - 20, 540)); gd = ImageDraw.Draw(g)
        for i in range(540): gd.line([(0, i), (cw - 20, i)], fill=(255, 140 - i // 7, 90 + i // 9, 255))
        im.alpha_composite(g, (x0 + 10, y + 10))
        for k, pid_ in enumerate(st["story"]):
            fimg = Image.open(os.path.join(ASSETS, f"t_{pid_}_sourire_0.png")).convert("RGBA").crop((150, 20, 1050, 1100)).resize((230, 276))
            im.alpha_composite(fimg, (x0 + 10 + k * 150, y + 110))
        d = ImageDraw.Draw(im)
        rr(d, (x0 + 24, y + 28, x0 + 200, y + 70), 20, (255, 255, 255, 230)); d.text((x0 + 112, y + 49), "PHOTO", font=L(32), fill="#e1306c", anchor="mm")
        ty = y + 430
        for ln in wrap(st.get("storytext", ""), L(36), cw - 50, d)[:3]: d.text((x0 + cw / 2, ty), ln, font=L(36), fill="white", anchor="mm", stroke_width=4, stroke_fill="#000"); ty += 42
    for prop in []:
        if prop == "invitation":
            rr(d, (40, 820, 360, 1050), 18, "#f6e7b8", "#b8902f", 8); d.text((200, 875), "MARIAGE", font=A(44), fill="#8a6a1f", anchor="mm")
            d.text((200, 935), "BILAL & YASMINE", font=A(38), fill="#141414", anchor="mm"); d.text((200, 995), "DANS 30 JOURS", font=F("Bold", 28), fill="#8a6a1f", anchor="mm")
        if prop == "chips":
            d.polygon([(800, 860), (1040, 840), (1020, 1080), (830, 1100)], fill="#f2c230", outline="#141414", width=8); d.text((920, 970), "CHIPS", font=A(60), fill="#d9342b", anchor="mm")
        if prop == "water":
            rr(d, (870, 760, 1010, 1160), 40, (140, 200, 255, 230), "#141414", 8); rr(d, (900, 720, 980, 770), 10, "#3d8bff", "#141414", 6)
            d.text((940, 950), "2 L", font=A(64), fill="#141414", anchor="mm"); d.text((940, 1020), "/ JOUR", font=A(34), fill="#141414", anchor="mm")
    if st.get("choice"):
        a, b = st["choice"]
        for k, (word, col) in enumerate(((a, "#ff3b3b"), (b, "#3d8bff"))):
            yy = 980 + k * 230
            f = L(130)
            while d.textlength(word.upper(), font=f) > 760: f = L(f.size - 8)
            tw = d.textlength(word.upper(), font=f)
            rr(d, (W / 2 - tw / 2 - 50, yy, W / 2 + tw / 2 + 50, yy + 170), 30, col, "#111", 8)
            d.text((W / 2, yy + 85), word.upper(), font=f, fill="white", anchor="mm", stroke_width=6, stroke_fill="#111")
        d.text((W / 2, 1200), "OU", font=L(80), fill="white", anchor="mm", stroke_width=8, stroke_fill="#111")
    # sous-titres (mots qui défilent), sans fond gris
    cl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dm = d; d = ImageDraw.Draw(cl); CY = 1590
    if big:
        fb = L(104)
        while d.textlength(big.upper(), font=fb) > 1000 and fb.size > 60: fb = L(fb.size - 8)
        d.text((W / 2 + 5, CY + 7), big.upper(), font=fb, fill="#000", anchor="mm", stroke_width=13, stroke_fill="#000")
        keys = {re.sub(r"[^\wÀ-ÿ']", "", w_).upper() for w_ in re.sub(r"[*~]", " ", st.get("head") or "").split()} - SMALL
        ws = big.upper().split(); x = W / 2 - d.textlength(big.upper(), font=fb) / 2
        for w_ in ws:
            hot = re.sub(r"[^\wÀ-ÿ']", "", w_) in keys or re.search(r"\d", w_)
            d.text((x, CY), w_, font=fb, fill=("#ffd23a" if hot else "white") if st.get("hud") else ("#ff4d4d" if hot else "#ffe14a"), anchor="lm", stroke_width=13, stroke_fill="#111")
            x += d.textlength(w_ + " ", font=fb)
    d = dm
    # bandeau du jour
    band = st.get("band", "")
    if band:
        fb2 = L(60)
        while d.textlength(band.upper(), font=fb2) > W - 200: fb2 = L(fb2.size - 2)
        rr(d, (70, 1712, W - 70, 1832), 34, (16, 16, 22, 240), "#f2c230", 7)
        d.text((W / 2, 1772), band.upper(), font=fb2, fill="white", anchor="mm")
    popc(im, cl, ck, CY); popc(im, hl, hk, 200)
    return im

# ------------------------------------------------------------------ plan
def plans_to_segments(E):
    segs, scene = [], None
    for i, p in enumerate(E["plans"]):
        cam = p["cam"]; scene = scene_of(cam, scene)
        m = re.search(r"\{(YANIS_[A-E])\}", cam); yid = m.group(1) if m else "YANIS_A"
        others = [o for o in OTHERS if "{" + o + "}" in cam and "{" + o + "}'s contact" not in cam]
        others.sort(key=lambda o: cam.find("{" + o + "}"))
        cl = cam.lower(); story = "instagram story" in cl or ("story" in cl and "{SARAH}" in cam and "{KENZO}" in cam and "phone" in cl)
        st = {"counter": E["counter"], "scene": scene, "cards": [], "props": [], "audio": p["voice"]["audio"] if p["voice"] else None,
              "sub": p["voice"]["text"] if p["voice"] else "", "yanis": yid if "{YANIS" in cam else None, "expr": p["expr"], "pose": p["pose"],
              "vote": p["vote"], "choice": p["choice"], "i": i, "head": p["head"], "band": E["counter"], "sfx": p["sfx"], "kind": p["kind"], "p": p["p"], "sfxb": p["sfxb"], "day": E["n"], "hud": E.get("hud")}
        st["props"] = [k for k, w in (("invitation", "invitation"), ("chips", "chips"), ("water", "water bottle")) if w in cl]
        cards = list(p["notes"])
        if story:
            st["story"] = ["SARAH", "KENZO"]; st["storytext"] = next((t for l, t in cards if l.lower() == "story"), ""); st["props"] = []
            cards = [(l, t) for l, t in cards if l.lower() != "story"]; others = []
        st["cards"] = cards
        st["others"] = [(o, cue(o, cam)) for o in others[:1]]
        if st["yanis"] is None and others: st["yanis"] = None
        st["shot"] = "close" if p["expr"] in ("choque", "panique", "colere", "larmes") else ("medium" if i % 2 else "wide")
        segs.append(st)
    return segs

def timing(s):
    j = s["audio"].replace(".mp3", ".json")
    return json.load(open(j)) if os.path.exists(j) else {"starts": [0.1], "sents": [s["sub"]]}

def seg_key(s):
    return hashlib.md5((json.dumps({k: v for k, v in s.items()}, sort_keys=True, default=str) + str(os.path.getsize(s["audio"]) if s.get("audio") and os.path.exists(s["audio"]) else 0) + open(os.path.join(HERE, "viz", "anim.js")).read() + open(os.path.join(HERE, "viz", "rig.js")).read() + open(os.path.join(HERE, "viz", "rooms2.js")).read() + "".join(open(os.path.join(HERE, "viz", f)).read() for f in ("kinds2.js", "look.js", "props2.js", "rooms3.js", "toon2.js"))).encode()).hexdigest()[:16]

def seg_dur(s): return dur(s["audio"]) + (0.06 if not s.get("choice") else 1.4)

def render_seg(s, epn):
    ad = dur(s["audio"]); D = seg_dur(s); key = seg_key(s)
    out = os.path.join(SEG, key + ".mp4")
    if os.path.exists(out): return out, D
    tmp = os.path.join(SEG, key + "_t"); os.makedirs(tmp, exist_ok=True)
    frames = os.path.join(SEG, key + "_f")
    tm = timing(s); st0 = tm["starts"]; sents = tm["sents"]
    # sous-titres calés phrase par phrase
    body = ""; s2 = dict(s, sub=""); p0 = os.path.join(tmp, "t_.png"); layer(s2).save(p0, compress_level=1)
    t0 = 0.0; k = 0
    for i, hk in enumerate((0.55, 0.85, 1.1, 1.04)):
        p = os.path.join(tmp, f"h{i}.png"); layer(s2, None, hk=hk).save(p, compress_level=1); body += f"file '{p}'\nduration {1 / FPS:.4f}\n"; t0 += 1 / FPS
    for i, sent in enumerate(sents):
        a = st0[i]; b = st0[i + 1] - 0.05 if i + 1 < len(st0) else ad - 0.15
        if a > t0: body += f"file '{p0}'\nduration {a - t0:.3f}\n"; t0 = a
        ch = chunks(sent); tot = sum(len(c) + 3 for c in ch)
        for c in ch:
            p = os.path.join(tmp, f"t{k}.png"); pp = os.path.join(tmp, f"u{k}.png"); k += 1
            layer(s2, c).save(p, compress_level=1); layer(s2, c, ck=1.2).save(pp, compress_level=1)
            dd = (b - a) * (len(c) + 3) / tot; body += f"file '{pp}'\nduration {min(dd, 2 / FPS):.4f}\nfile '{p}'\nduration {max(dd - 2 / FPS, 0.01):.3f}\n"; t0 += dd
    body += f"file '{p0}'\nduration {max(D - t0, 0.05):.3f}\nfile '{p0}'\n"
    tl = os.path.join(tmp, "t.txt"); open(tl, "w").write(body)
    run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(frames, "f_%05d.jpg"),
         "-f", "concat", "-safe", "0", "-i", tl, "-i", s["audio"],
         "-filter_complex", "[1:v]fps=30,format=rgba[t];[0:v][t]overlay=0:0,format=yuv420p[v];[2:a]aresample=44100,aformat=channel_layouts=stereo,apad[a]",
         "-map", "[v]", "-map", "[a]", "-t", f"{D:.3f}", "-r", str(FPS), "-c:v", "libx264", "-preset", "medium",
         "-crf", "17", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-ar", "44100", out])
    shutil.rmtree(tmp, ignore_errors=True); shutil.rmtree(frames, ignore_errors=True)
    return out, D

def sfx_time(s):
    b = timing(s)["starts"]; k = s.get("kind")
    if s.get("sfxb") is not None: return (b[s["sfxb"]] if s["sfxb"] < len(b) else b[-1]) + 0.15
    g = lambda i, d=0.35: (b[i] if i < len(b) else b[-1]) + 0.2
    return {"pushup": (b[6] + 0.5) if len(b) > 6 else 3, "throw": 1.9, "armsUp": g(1) + 0.3, "phone": g(1), "score": g(2), "invite": 0.12, "hook": 0.05, "armRaise": 0.05, "sore": g(1), "sofiane": 0.3, "nose": g(1) - 0.2, "runPass": (b[1] if len(b) > 2 else 1.3), "box": g(3) - 0.2, "croissant": g(3) + 0.6}.get(k, 0.35)

SFX = {"thud": "anoisesrc=color=brown:amplitude=0.9:d=0.35,lowpass=f=180,afade=t=out:st=0.05:d=0.3,volume=3",
       "boing": "aevalsrc='0.6*sin(2*PI*(90+60*exp(-6*t))*t)*exp(-3*t)':d=0.7,lowpass=f=600",
       "scratch": "anoisesrc=color=pink:amplitude=0.7:d=0.5,bandpass=f=900:width_type=h:w=600,afade=t=out:st=0.2:d=0.3,volume=0.8",
"whoosh": "anoisesrc=color=pink:amplitude=0.6:d=0.4,highpass=f=700,lowpass=f=5000,afade=t=in:d=0.15,afade=t=out:st=0.18:d=0.22,volume=0.45",
       "boom": "sine=f=55:d=1.2,afade=t=out:st=0.1:d=1.1,volume=2.0", "pop": "sine=f=900:d=0.1,afade=t=out:st=0.03:d=0.07,volume=0.4"}

def build(E):
    segs = plans_to_segments(E); files, t, ev = [], 0.0, []
    for s in segs:
        f, D = render_seg(s, E["n"]); files.append(f)
        ev.append(("boom" if s.get("choice") else "whoosh", t))
        if s.get("sfx") in ("boom", "thud", "boing", "scratch"): ev.append((s["sfx"], t + sfx_time(s)))
        if s.get("kind") == "throw": ev.append(("whoosh", t + 1.1)); ev.append(("thud", t + 1.9))
        t += D
    lst = os.path.join(WORK, f"ep{E['n']:02d}.txt"); open(lst, "w").write("".join(f"file '{f}'\n" for f in files))
    raw = os.path.join(WORK, f"ep{E['n']:02d}_raw.mp4"); run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", raw])
    sfx = {}
    for k, f in SFX.items():
        p = os.path.join(WORK, f"sfx_{k}.wav")
        if not os.path.exists(p): run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f, "-ar", "44100", "-ac", "2", p])
        sfx[k] = p
    beat = "0.55*sin(2*PI*52*t)*exp(-9*mod(t,0.5))+0.05*sin(2*PI*110*t)*(0.5+0.5*sin(2*PI*0.25*t))+0.04*sin(2*PI*164.8*t)*(0.5+0.5*sin(2*PI*0.2*t))"
    mus = os.path.join(WORK, f"musique_{int(t) + 2}.wav")
    if not os.path.exists(mus): run(["python3", os.path.join(HERE, "musique.py"), mus, str(int(t) + 2)])
    ins = ["-i", raw, "-i", mus]
    fc = f"[1:a]atrim=0:{t:.2f},afade=t=in:d=0.6,afade=t=out:st={max(0, t - 2):.2f}:d=2,volume=0.42,aformat=channel_layouts=stereo[m];[0:a]asplit=2[vx][vs];[m][vs]sidechaincompress=threshold=0.015:ratio=8:attack=20:release=300[md]"
    mix = ["[vx]", "[md]"]
    for i, (k, at) in enumerate(ev):
        ins += ["-i", sfx[k]]; ms = int(at * 1000); fc += f";[{i + 2}:a]adelay={ms}|{ms}[e{i}]"; mix.append(f"[e{i}]")
    fc += f";{''.join(mix)}amix=inputs={len(mix)}:duration=first:normalize=0,alimiter=limit=0.95[a]"
    out = os.path.join(OUT, f"ep{E['n']:02d}.mp4")
    run(["ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex", fc, "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out])
    os.remove(raw); return t

if __name__ == "__main__":
    eps = parse(); todo = [eps[n] for n in sorted(eps) if not ONLY or n in ONLY]
    busts, jobs = set(), []
    for E in todo:
        for s in plans_to_segments(E):
            for b in s.get("story", []): busts.add((b, "sourire"))
            key = seg_key(s)
            if os.path.exists(os.path.join(SEG, key + ".mp4")): continue
            jobs.append({"day": 31 - E["n"], "kind": s["kind"], "D": seg_dur(s), "beats": timing(s)["starts"], "expr": s["expr"], "yid": (f"Y{E['n']}" if E["n"] >= 4 or E["n"] == 1 else (s["yanis"] or "YANIS_A")), "p": s.get("p", {}), "out": os.path.join(SEG, key + "_f"), "fps": FPS})
    req = os.path.join(WORK, "req.json"); json.dump({"scenes": [], "persons": [], "busts": sorted(busts)}, open(req, "w"))
    subprocess.run(["node", os.path.join(HERE, "viz", "assets5.js"), req, ASSETS], check=True)
    jf = os.path.join(WORK, "jobs.json"); json.dump(jobs, open(jf, "w"))
    if jobs: subprocess.run(["node", os.path.join(HERE, "viz", "anim.js"), jf], check=True)
    for E in todo: print(f"ep{E['n']:02d}: {build(E):.1f}s", flush=True)
