"""Montage « voix off continue » : python3 build6.py SCRIPTS_DIR VOIX_DIR OUT_DIR [épisodes]"""
import re, os, sys, glob, json, hashlib, subprocess, unicodedata, random, shutil
from PIL import Image, ImageDraw, ImageFont

SCRIPTS, VOIX, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
ONLY = set(int(x) for x in sys.argv[4].split(",")) if len(sys.argv) > 4 else None
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "v8work"); ASSETS = os.path.join(WORK, "assets"); SEG = os.path.join(WORK, "seg")
for d in (WORK, ASSETS, SEG, OUT): os.makedirs(d, exist_ok=True)
FPS, W, H = 30, 1080, 1920
def F(w, s): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{w}.otf", s)
def A(s): return ImageFont.truetype("/root/.fonts/Anton-Regular.ttf", s)
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
            if s.startswith("⏱️"):
                m = re.search(r"📊 `([^`]+)`", s); E["counter"] = m.group(1) if m else ""; continue
            m = re.match(r"\*\*(P\d+) ·", s)
            if m:
                cur = {"tag": m.group(1), "cam": "", "expr": "neutre", "pose": "idle", "notes": [], "voice": None, "vote": None, "choice": None, "head": "", "sfx": None}
                E["plans"].append(cur); continue
            if cur is None: continue
            if s.startswith("🎥"): cur["cam"] = s
            elif s.startswith("🔊"):
                m = re.search(r"`(\w+)`", s); cur["sfx"] = m.group(1) if m else None
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
def chunks(text):
    words = re.sub(r"[«»]", "", text).split(); out, cur = [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if len(t) <= 12 or not cur: cur = t
        else: out.append(cur); cur = w_
    if cur: out.append(cur)
    return out

def headline(d, text, y0=110):
    """gros titre en haut : blanc, mots entre *étoiles* en rouge"""
    words = re.findall(r"\*[^*]+\*|\S+", text)
    toks = []
    for w_ in words:
        red = w_.startswith("*")
        for sub in w_.strip("*").split(): toks.append((sub.upper(), red))
    f = A(112); lines, cur = [], []
    for t, r in toks:
        trial = " ".join(x for x, _ in cur + [(t, r)])
        if d.textlength(trial, font=f) > 980 and cur: lines.append(cur); cur = [(t, r)]
        else: cur.append((t, r))
    if cur: lines.append(cur)
    while len(lines) > 3 and f.size > 70:
        f = A(f.size - 12); lines, cur = [], []
        for t, r in toks:
            trial = " ".join(x for x, _ in cur + [(t, r)])
            if d.textlength(trial, font=f) > 980 and cur: lines.append(cur); cur = [(t, r)]
            else: cur.append((t, r))
        if cur: lines.append(cur)
    y = y0
    for ln in lines:
        total = d.textlength(" ".join(t for t, _ in ln), font=f); x = (W - total) / 2
        for t, r in ln:
            d.text((x, y), t, font=f, fill="#ff3b3b" if r else "white", stroke_width=10, stroke_fill="#111")
            x += d.textlength(t + " ", font=f)
        y += int(f.size * 1.08)
    return y

def layer(st, big=None):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    y = headline(d, st.get("head") or "", 110) + 10
    # badge sport / glow-up sous le titre
    for lab, txt in st.get("cards", []):
        u = txt.upper().lstrip("😩🏃🏋️✅🏆✨ ")
        if u.startswith("GLOW-UP DU JOUR"): col, fg, u = "#ffcf4a", "#141414", "★ " + u.split(":", 1)[1].strip()
        elif re.match(r"(MUSCU|COURSE|REPOS|3 KM|.*KM EN|10 KM)", u): col, fg = "#3d8bff", "white"
        else: col, fg = (255, 255, 255, 240), "#141414"; u = (lab.upper() + " : " if lab else "") + txt
        f = A(46) if col != (255, 255, 255, 240) else F("Bold", 36)
        ls = wrap(u.replace("★ ", ""), f, 900, d)[:2]; h = 26 + len(ls) * (56 if col != (255, 255, 255, 240) else 46)
        rr(d, (80, y, W - 80, y + h), 22, col, "#111", 5); ty = y + 13
        for ln in ls: d.text((W / 2, ty + (28 if col != (255, 255, 255, 240) else 23)), ln, font=f, fill=fg, anchor="mm"); ty += 56 if col != (255, 255, 255, 240) else 46
        y += h + 12
    if st.get("story"):
        rr(d, (250, y, W - 250, y + 640), 46, (20, 20, 24, 255), "#000", 10)
        g = Image.new("RGBA", (560, 600)); gd = ImageDraw.Draw(g)
        for i in range(600): gd.line([(0, i), (560, i)], fill=(255, 140 - i // 8, 90 + i // 10, 255))
        im.alpha_composite(g, (260, y + 20))
        for k, pid_ in enumerate(st["story"]):
            fimg = Image.open(os.path.join(ASSETS, f"t_{pid_}_sourire_0.png")).convert("RGBA").crop((150, 20, 1050, 1100)).resize((290, 348))
            im.alpha_composite(fimg, (300 + k * 190, y + 130))
        d = ImageDraw.Draw(im)
        rr(d, (280, y + 36, 520, y + 76), 20, (255, 255, 255, 230)); d.text((400, y + 56), "STORY", font=F("Bold", 28), fill="#e1306c", anchor="mm")
        ty = y + 500
        for ln in wrap(st.get("storytext", ""), F("ExtraBold", 36), 480, d)[:3]: d.text((W / 2, ty), ln, font=F("ExtraBold", 36), fill="white", anchor="mm", stroke_width=3, stroke_fill="#000"); ty += 44
    for prop in st.get("props", []):
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
            f = A(120)
            while d.textlength(word.upper(), font=f) > 760: f = A(f.size - 8)
            tw = d.textlength(word.upper(), font=f)
            rr(d, (W / 2 - tw / 2 - 50, yy, W / 2 + tw / 2 + 50, yy + 170), 30, col, "#111", 8)
            d.text((W / 2, yy + 85), word.upper(), font=f, fill="white", anchor="mm", stroke_width=6, stroke_fill="#111")
        d.text((W / 2, 1200), "OU", font=A(70), fill="white", anchor="mm", stroke_width=8, stroke_fill="#111")
    # sous-titres (mots qui défilent), sans fond gris
    if big:
        fb = A(96)
        while d.textlength(big.upper(), font=fb) > 1000 and fb.size > 60: fb = A(fb.size - 8)
        d.text((W / 2, 1600), big.upper(), font=fb, fill="#ffe14a", anchor="mm", stroke_width=10, stroke_fill="#111")
    # bandeau du jour
    band = st.get("band", "")
    if band:
        fb2 = A(48); tw = d.textlength(band.upper(), font=fb2)
        rr(d, (W / 2 - tw / 2 - 40, 1700, W / 2 + tw / 2 + 40, 1790), 26, (18, 18, 22, 235), "#e8b23a", 5)
        d.text((W / 2, 1745), band.upper(), font=fb2, fill="white", anchor="mm")
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
              "vote": p["vote"], "choice": p["choice"], "i": i, "head": p["head"], "band": E["counter"], "sfx": p["sfx"]}
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

def fullbody_key(pid, expr, pose): return f"p_{pid}_{expr}_{pose}_0.png"

def render_seg(s, epn):
    ad = dur(s["audio"]); D = ad + (0.06 if not s.get("choice") else 1.4)
    key = hashlib.md5(json.dumps({k: v for k, v in s.items()}, sort_keys=True, default=str).encode()).hexdigest()[:16]
    out = os.path.join(SEG, key + ".mp4")
    if os.path.exists(out): return out, D
    tmp = os.path.join(SEG, key); os.makedirs(tmp, exist_ok=True)
    bgp = os.path.join(tmp, "bg.png"); Image.open(os.path.join(ASSETS, f"bg_{s['scene']}.png")).convert("RGB").save(bgp, compress_level=1)
    # personnages : Yanis (+ éventuellement un autre)
    two = bool(s["others"]) and s["yanis"]
    def compose(blink):
        canvas = Image.new("RGBA", (1600, 2600), (0, 0, 0, 0))
        def put(fn, cx, scale):
            im = Image.open(os.path.join(ASSETS, fn)).convert("RGBA"); w = int(im.width * scale); h = int(im.height * scale)
            canvas.alpha_composite(im.resize((w, h), Image.LANCZOS), (int(cx - w / 2), 2600 - h))
        bx = "_blink" if blink else ""
        if s["yanis"] and not two: put(fullbody_key(s["yanis"], s["expr"] + bx, s["pose"]), 800, 1.0)
        elif two:
            o, oe = s["others"][0]
            put(fullbody_key(o, oe, "idle"), 1080, 0.86); put(fullbody_key(s["yanis"], s["expr"] + bx, s["pose"]), 560, 0.92)
        elif s["others"]:
            o, oe = s["others"][0]; put(fullbody_key(o, oe + bx, "idle"), 800, 1.0)
        return canvas
    c_open = os.path.join(tmp, "c0.png"); compose(False).save(c_open, compress_level=1)
    c_blink = os.path.join(tmp, "c1.png"); compose(True).save(c_blink, compress_level=1)
    rb = random.Random(str(s.get("i")) + s["sub"][:10]); seq, tt = "", 0.0
    while tt < D:
        o = rb.uniform(1.8, 3.2); seq += f"file '{c_open}'\nduration {min(o, D - tt):.3f}\n"; tt += o
        if tt < D: seq += f"file '{c_blink}'\nduration 0.130\n"; tt += 0.13
    seq += f"file '{c_open}'\n"
    cp = os.path.join(tmp, "c.txt"); open(cp, "w").write(seq)
    # gros plan sur les moments forts, plan large sinon
    shot = s.get("shot", "wide")
    if two or s.get("story") or s.get("choice"): shot = "wide"
    CW, yoff = {"close": (1250, "560-0.05*h"), "medium": (1000, "520-0.05*h"), "wide": (760, "H-h-230")}[shot]
    # texte : mots successifs
    ch = chunks(s["sub"]); tot = sum(len(c) + 2 for c in ch); body = ""
    s = dict(s, sub="")
    p0 = os.path.join(tmp, "t_.png"); layer(s).save(p0, compress_level=1)
    t0 = 0.0
    for i, c in enumerate(ch):
        p = os.path.join(tmp, f"t{i}.png"); layer(s, c).save(p, compress_level=1)
        dd = (ad - 0.1) * (len(c) + 2) / tot; body += f"file '{p}'\nduration {dd:.3f}\n"; t0 += dd
    body += f"file '{p0}'\nduration {max(D - t0, 0.05):.3f}\nfile '{p0}'\n"
    tl = os.path.join(tmp, "t.txt"); open(tl, "w").write(body)
    rnd = random.Random(key); ph = rnd.uniform(0, 6.28); off = rnd.choice([-60, -30, 0, 30, 60])
    sh = 16 if s["expr"] in ("choque", "panique", "colere") else 0
    bounce = "+14*abs(sin(t*8))" if s["expr"] in ("panique",) else ("+6*sin(t*3)" if s["expr"] in ("sourire", "determine") else "")
    zoom = f"(1+0.05*t/{D:.3f}+0.10*max(0\\,1-t/0.25))"
    fc = (f"[0:v]crop=1080:1920:x='54+30*sin(t*0.4+{ph:.2f})':y='96-50*t/{D:.3f}'[b];"
          f"[1:v]fps={FPS},format=rgba,scale=w='trunc({CW}*{zoom}/2)*2':h=-2:eval=frame[c];"
          f"[b][c]overlay=x='(W-w)/2+{off}+{sh}*sin(t*70)*max(0\\,1-t/0.5)':y='{yoff}{bounce}':eval=frame[bc];"
          f"[2:v]fps={FPS},format=rgba[t];[bc][t]overlay=0:0,format=yuv420p[v];[3:a]aresample=44100,aformat=channel_layouts=stereo,apad[a]")
    run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", str(FPS), "-t", f"{D:.3f}", "-i", bgp,
         "-f", "concat", "-safe", "0", "-i", cp, "-f", "concat", "-safe", "0", "-i", tl, "-i", s["audio"],
         "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-t", f"{D:.3f}", "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast",
         "-crf", "21", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-ar", "44100", out])
    shutil.rmtree(tmp, ignore_errors=True)
    return out, D

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
        if s.get("sfx") in ("boom", "thud", "boing", "scratch"): ev.append((s["sfx"], t + 0.35))
        t += D
    lst = os.path.join(WORK, f"ep{E['n']:02d}.txt"); open(lst, "w").write("".join(f"file '{f}'\n" for f in files))
    raw = os.path.join(WORK, f"ep{E['n']:02d}_raw.mp4"); run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", raw])
    sfx = {}
    for k, f in SFX.items():
        p = os.path.join(WORK, f"sfx_{k}.wav")
        if not os.path.exists(p): run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f, "-ar", "44100", "-ac", "2", p])
        sfx[k] = p
    beat = "0.55*sin(2*PI*52*t)*exp(-9*mod(t,0.5))+0.05*sin(2*PI*110*t)*(0.5+0.5*sin(2*PI*0.25*t))+0.04*sin(2*PI*164.8*t)*(0.5+0.5*sin(2*PI*0.2*t))"
    ins = ["-i", raw, "-f", "lavfi", "-i", f"aevalsrc='{beat}':s=44100:d={t:.2f}"]
    fc = f"[1:a]lowpass=f=900,afade=t=in:d=1,afade=t=out:st={max(0, t - 2):.2f}:d=2,volume=0.5,aformat=channel_layouts=stereo[m];[0:a]asplit=2[vx][vs];[m][vs]sidechaincompress=threshold=0.015:ratio=8:attack=20:release=300[md]"
    mix = ["[vx]", "[md]"]
    for i, (k, at) in enumerate(ev):
        ins += ["-i", sfx[k]]; ms = int(at * 1000); fc += f";[{i + 2}:a]adelay={ms}|{ms}[e{i}]"; mix.append(f"[e{i}]")
    fc += f";{''.join(mix)}amix=inputs={len(mix)}:duration=first:normalize=0,alimiter=limit=0.95[a]"
    out = os.path.join(OUT, f"ep{E['n']:02d}.mp4")
    run(["ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex", fc, "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out])
    os.remove(raw); return t

if __name__ == "__main__":
    eps = parse(); todo = [eps[n] for n in sorted(eps) if not ONLY or n in ONLY]
    scenes, persons, busts = set(), set(), set()
    for E in todo:
        for s in plans_to_segments(E):
            scenes.add(s["scene"])
            if s["yanis"]: persons.add((s["yanis"], s["expr"], s["pose"], 0)); persons.add((s["yanis"], s["expr"] + "_blink", s["pose"], 0))
            for o, oe in s["others"]: persons.add((o, oe, "idle", 0)); persons.add((o, oe + "_blink", "idle", 0))
            for b in s.get("story", []): busts.add((b, "sourire"))
    req = os.path.join(WORK, "req.json"); json.dump({"scenes": sorted(scenes), "persons": sorted(persons), "busts": sorted(busts)}, open(req, "w"))
    subprocess.run(["node", os.path.join(HERE, "viz", "assets5.js"), req, ASSETS], check=True)
    for E in todo: print(f"ep{E['n']:02d}: {build(E):.1f}s", flush=True)
