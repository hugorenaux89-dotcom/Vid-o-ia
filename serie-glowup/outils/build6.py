"""Montage « voix off continue » : python3 build6.py SCRIPTS_DIR VOIX_DIR OUT_DIR [épisodes]"""
import re, os, sys, glob, json, hashlib, subprocess, unicodedata, random, shutil
from PIL import Image, ImageDraw, ImageFont

SCRIPTS, VOIX, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
ONLY = set(int(x) for x in sys.argv[4].split(",")) if len(sys.argv) > 4 else None
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "v6work"); ASSETS = os.path.join(WORK, "assets"); SEG = os.path.join(WORK, "seg")
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
                cur = {"tag": m.group(1), "cam": "", "expr": "neutre", "pose": "idle", "notes": [], "voice": None, "vote": None, "choice": None}
                E["plans"].append(cur); continue
            if cur is None: continue
            if s.startswith("🎥"): cur["cam"] = s
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

def layer(st, big=None):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    m = re.search(r"J-(\d+)", st["counter"]); days = int(m.group(1)) if m else 0
    m = re.search(r"(\d+)\s*%", st["counter"]); pct = int(m.group(1)) if m else 0
    rr(d, (60, 70, 360, 220), 22, "#1d1a24", "#000", 6)
    d.text((210, 112), "JOURS RESTANTS", font=A(34), fill="white", anchor="mm"); d.text((210, 178), str(days), font=A(72), fill="#ffd54a", anchor="mm")
    rr(d, (420, 70, 1020, 220), 22, "#1d1a24", "#000", 6); d.text((720, 112), "GLOW-UP", font=A(34), fill="white", anchor="mm")
    rr(d, (460, 150, 840, 184), 17, "#3a3640"); rr(d, (460, 150, 460 + max(34, 380 * pct / 100), 184), 17, "#5ee38a")
    d.text((935, 168), f"{pct}%", font=A(64), fill="#5ee38a", anchor="mm")
    y = 260
    if st.get("sign"):
        jn = 31 - days if days else 30
        d.line([(210, 220), (300, 290)], fill="#1d1a24", width=6); d.line([(720, 220), (780, 290)], fill="#1d1a24", width=6)
        board = Image.new("RGBA", (680, 300), (0, 0, 0, 0)); bd = ImageDraw.Draw(board)
        bd.rounded_rectangle((20, 20, 660, 220), 18, fill="#ffd54a", outline="#1d1a24", width=10)
        bd.text((340, 120), f"{days} JOURS !" if days else "JOUR J !", font=A(130), fill="#1d1a24", anchor="mm")
        bd.rounded_rectangle((420, 200, 650, 290), 10, fill="white", outline="#e33333", width=8); bd.text((535, 245), f"JOUR {jn}", font=A(62), fill="#e33333", anchor="mm")
        im.alpha_composite(board.rotate(4, resample=Image.BICUBIC), (200, 262)); d = ImageDraw.Draw(im); y = 590
    if st.get("vote"):
        L, txt = st["vote"]; col = "#ff4d4d" if L == "A" else "#3d8bff"
        rr(d, (70, y, W - 70, y + 200), 30, (14, 16, 24, 235), "#000", 6)
        d.text((W / 2, y + 50), "VOUS AVEZ VOTÉ", font=A(60), fill="white", anchor="mm")
        d.ellipse((110, y + 95, 200, y + 185), fill=col, outline="#000", width=5); d.text((155, y + 140), L, font=A(60), fill="white", anchor="mm")
        d.text((230, y + 140), wrap(txt, F("ExtraBold", 44), 760, d)[0], font=F("ExtraBold", 44), fill="#ffd54a", anchor="lm"); y += 220
    if st.get("story"):
        rr(d, (250, y, W - 250, y + 700), 50, (20, 20, 24, 255), "#000", 10)
        g = Image.new("RGBA", (560, 660)); gd = ImageDraw.Draw(g)
        for i in range(660): gd.line([(0, i), (560, i)], fill=(255, 140 - i // 8, 90 + i // 10, 255))
        im.alpha_composite(g, (260, y + 20))
        for k, pid_ in enumerate(st["story"]):
            fimg = Image.open(os.path.join(ASSETS, f"t_{pid_}_sourire_0.png")).convert("RGBA").crop((150, 20, 1050, 1100)).resize((300, 360))
            im.alpha_composite(fimg, (300 + k * 190, y + 150))
        d = ImageDraw.Draw(im)
        rr(d, (280, y + 40, 520, y + 80), 20, (255, 255, 255, 230)); d.text((400, y + 60), "STORY", font=F("Bold", 28), fill="#e1306c", anchor="mm")
        ty = y + 540
        for ln in wrap(st.get("storytext", ""), F("ExtraBold", 38), 480, d)[:3]: d.text((W / 2, ty), ln, font=F("ExtraBold", 38), fill="white", anchor="mm", stroke_width=3, stroke_fill="#000"); ty += 46
        y += 720
    for lab, txt in st.get("cards", []):
        if txt.startswith("GLOW-UP DU JOUR"):
            t2 = txt.split(":", 1)[1].strip(); ls = wrap(t2.upper(), A(62), 860, d)[:3]; h = 110 + len(ls) * 74
            rr(d, (70, y, W - 70, y + h), 30, "#ffcf4a", "#000", 8); d.text((W / 2, y + 52), "GLOW-UP DU JOUR", font=A(54), fill="#141414", anchor="mm")
            ty = y + 118
            for ln in ls: d.text((W / 2, ty), ln, font=A(62), fill="#141414", anchor="mm"); ty += 74
            y += h + 18; continue
        if re.match(r"(MUSCU|COURSE|REPOS|CHRONO|JOUR 1|3 KM|.*KM EN|10 KM)", txt.upper().lstrip("😩🏃🏋️✅🏆 ")):
            ls = wrap(txt.upper(), A(56), 880, d)[:2]; h = 40 + len(ls) * 68
            rr(d, (70, y, W - 70, y + h), 30, "#3d8bff", "#000", 8); ty = y + 54
            for ln in ls: d.text((W / 2, ty), ln, font=A(56), fill="white", anchor="mm"); ty += 68
            y += h + 18; continue
        fl, ft = F("Bold", 28), F("Bold", 42); ls = wrap(txt, ft, 840, d)[:4]; h = 34 + (42 if lab else 0) + len(ls) * 54 + 18
        rr(d, (90, y, W - 90, y + h), 28, (255, 255, 255, 245), "#000", 6); yy = y + 24
        if lab: d.text((122, yy), lab.upper(), font=fl, fill=(110, 110, 110)); yy += 42
        for ln in ls: d.text((122, yy), ln, font=ft, fill=(20, 20, 24)); yy += 54
        y += h + 18
    for prop in st.get("props", []):
        if prop == "invitation":
            rr(d, (40, 760, 380, 1000), 18, "#f6e7b8", "#b8902f", 8); d.text((210, 820), "MARIAGE", font=A(46), fill="#8a6a1f", anchor="mm")
            d.text((210, 880), "BILAL & YASMINE", font=A(40), fill="#141414", anchor="mm"); d.text((210, 945), "DANS 30 JOURS", font=F("Bold", 30), fill="#8a6a1f", anchor="mm")
        if prop == "chips":
            d.polygon([(780, 800), (1030, 780), (1010, 1040), (810, 1060)], fill="#f2c230", outline="#141414", width=8); d.text((905, 920), "CHIPS", font=A(64), fill="#d9342b", anchor="mm")
        if prop == "water":
            rr(d, (860, 700, 1000, 1110), 40, (140, 200, 255, 230), "#141414", 8); rr(d, (890, 660, 970, 710), 10, "#3d8bff", "#141414", 6)
            d.text((930, 900), "2 L", font=A(64), fill="#141414", anchor="mm"); d.text((930, 970), "/ JOUR", font=A(34), fill="#141414", anchor="mm")
    if st.get("choice"):
        a, b = st["choice"]
        rr(d, (50, 600, W - 50, 1240), 40, (14, 16, 24, 235), "#000", 8)
        d.text((W / 2, 690), "À TOI DE CHOISIR", font=A(100), fill="#ffcf4a", anchor="mm", stroke_width=6, stroke_fill="#000")
        yy = 790
        for L, col, txt in (("A", "#ff4d4d", a), ("B", "#3d8bff", b)):
            d.ellipse((90, yy, 200, yy + 110), fill=col, outline="#000", width=6); d.text((145, yy + 55), L, font=A(76), fill="white", anchor="mm")
            ls = wrap(txt, F("ExtraBold", 46), 720, d)[:2]; ty = yy + 55 - len(ls) * 28
            for ln in ls: d.text((230, ty), ln, font=F("ExtraBold", 46), fill="white"); ty += 56
            yy += 190
        d.text((W / 2, 1180), "VOTE EN COMMENTAIRE ↓", font=A(64), fill="white", anchor="mm")
    if big:
        fb = A(140)
        while d.textlength(big.upper(), font=fb) > 1000 and fb.size > 80: fb = A(fb.size - 10)
        d.text((W / 2, 1330), big.upper(), font=fb, fill="white", anchor="mm", stroke_width=13, stroke_fill="#000")
    if st.get("sub"):
        fs = F("Bold", 40); yy = 1450
        for ln in wrap(st["sub"], fs, 920, d)[:3]:
            tw = d.textlength(ln, font=fs); rr(d, (W / 2 - tw / 2 - 18, yy, W / 2 + tw / 2 + 18, yy + 58), 12, (30, 30, 30, 220))
            d.text((W / 2, yy + 29), ln, font=fs, fill="white", anchor="mm"); yy += 64
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
              "vote": p["vote"], "choice": p["choice"], "i": i}
        st["props"] = [k for k, w in (("invitation", "invitation"), ("chips", "chips"), ("water", "water bottle")) if w in cl]
        cards = list(p["notes"])
        if story:
            st["story"] = ["SARAH", "KENZO"]; st["storytext"] = next((t for l, t in cards if l.lower() == "story"), ""); st["props"] = []
            cards = [(l, t) for l, t in cards if l.lower() != "story"]; others = []
        st["cards"] = cards
        st["others"] = [(o, cue(o, cam)) for o in others[:1]]
        if st["yanis"] is None and others: st["yanis"] = None
        if i == 0: st["sign"] = True
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
    canvas = Image.new("RGBA", (1600, 2600), (0, 0, 0, 0))
    def put(fn, cx, scale):
        im = Image.open(os.path.join(ASSETS, fn)).convert("RGBA"); w = int(im.width * scale); h = int(im.height * scale)
        canvas.alpha_composite(im.resize((w, h), Image.LANCZOS), (int(cx - w / 2), 2600 - h))
    two = bool(s["others"]) and s["yanis"]
    if s["yanis"] and not two: put(fullbody_key(s["yanis"], s["expr"], s["pose"]), 800, 1.0)
    elif two:
        o, oe = s["others"][0]
        put(fullbody_key(o, oe, "idle"), 1080, 0.86); put(fullbody_key(s["yanis"], s["expr"], s["pose"]), 560, 0.92)
    elif s["others"]:
        o, oe = s["others"][0]; put(fullbody_key(o, oe, "idle"), 800, 1.0)
    cp = os.path.join(tmp, "c.png"); canvas.save(cp, compress_level=1)
    # gros plan sur les moments forts, plan large sinon
    close = s["expr"] in ("choque", "panique", "colere", "larmes") and not two and not s.get("story") and not s.get("choice")
    CW = 1250 if close else 780
    yoff = "340-0.05*h" if close else "H-h-30"
    # texte : mots successifs
    ch = chunks(s["sub"]); tot = sum(len(c) + 2 for c in ch); body = ""
    p0 = os.path.join(tmp, "t_.png"); layer(s).save(p0, compress_level=1)
    t0 = 0.0
    for i, c in enumerate(ch):
        p = os.path.join(tmp, f"t{i}.png"); layer(s, c).save(p, compress_level=1)
        dd = (ad - 0.1) * (len(c) + 2) / tot; body += f"file '{p}'\nduration {dd:.3f}\n"; t0 += dd
    body += f"file '{p0}'\nduration {max(D - t0, 0.05):.3f}\nfile '{p0}'\n"
    tl = os.path.join(tmp, "t.txt"); open(tl, "w").write(body)
    rnd = random.Random(key); ph = rnd.uniform(0, 6.28); off = rnd.choice([-60, -30, 0, 30, 60])
    sh = 16 if s["expr"] in ("choque", "panique", "colere") else 0
    zoom = f"(1+0.05*t/{D:.3f}+0.10*max(0\\,1-t/0.25))"
    fc = (f"[0:v]crop=1080:1920:x='54+30*sin(t*0.4+{ph:.2f})':y='96-50*t/{D:.3f}'[b];"
          f"[1:v]format=rgba,scale=w='trunc({CW}*{zoom}/2)*2':h=-2:eval=frame[c];"
          f"[b][c]overlay=x='(W-w)/2+{off}+{sh}*sin(t*70)*max(0\\,1-t/0.5)':y='{yoff}':eval=frame[bc];"
          f"[2:v]fps={FPS},format=rgba[t];[bc][t]overlay=0:0,format=yuv420p[v];[3:a]aresample=44100,aformat=channel_layouts=stereo,apad[a]")
    run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", str(FPS), "-t", f"{D:.3f}", "-i", bgp,
         "-loop", "1", "-framerate", str(FPS), "-t", f"{D:.3f}", "-i", cp, "-f", "concat", "-safe", "0", "-i", tl, "-i", s["audio"],
         "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-t", f"{D:.3f}", "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast",
         "-crf", "21", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-ar", "44100", out])
    shutil.rmtree(tmp, ignore_errors=True)
    return out, D

SFX = {"whoosh": "anoisesrc=color=pink:amplitude=0.6:d=0.4,highpass=f=700,lowpass=f=5000,afade=t=in:d=0.15,afade=t=out:st=0.18:d=0.22,volume=0.45",
       "boom": "sine=f=55:d=1.2,afade=t=out:st=0.1:d=1.1,volume=2.0", "pop": "sine=f=900:d=0.1,afade=t=out:st=0.03:d=0.07,volume=0.4"}

def build(E):
    segs = plans_to_segments(E); files, t, ev = [], 0.0, []
    for s in segs:
        f, D = render_seg(s, E["n"]); files.append(f)
        ev.append(("boom" if s.get("choice") or s.get("sign") else "whoosh", t))
        if s["cards"] or s.get("vote"): ev.append(("pop", t + 0.25))
        t += D
    lst = os.path.join(WORK, f"ep{E['n']:02d}.txt"); open(lst, "w").write("".join(f"file '{f}'\n" for f in files))
    raw = os.path.join(WORK, f"ep{E['n']:02d}_raw.mp4"); run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", raw])
    sfx = {}
    for k, f in SFX.items():
        p = os.path.join(WORK, f"sfx_{k}.wav")
        if not os.path.exists(p): run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f, "-ar", "44100", "-ac", "2", p])
        sfx[k] = p
    beat = "0.06*sin(2*PI*55*t)*(0.6+0.4*sin(2*PI*2*t))+0.04*sin(2*PI*110*t)*(0.5+0.5*sin(2*PI*4*t))+0.22*sin(2*PI*1500*t)*exp(-50*mod(t,0.5))"
    ins = ["-i", raw, "-f", "lavfi", "-i", f"aevalsrc='{beat}':s=44100:d={t:.2f}"]
    fc = f"[1:a]lowpass=f=3000,afade=t=in:d=1,afade=t=out:st={max(0, t - 2):.2f}:d=2,volume=0.5,aformat=channel_layouts=stereo[m];[0:a]asplit=2[vx][vs];[m][vs]sidechaincompress=threshold=0.015:ratio=8:attack=20:release=300[md]"
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
            if s["yanis"]: persons.add((s["yanis"], s["expr"], s["pose"], 0))
            for o, oe in s["others"]: persons.add((o, oe, "idle", 0))
            for b in s.get("story", []): busts.add((b, "sourire"))
    req = os.path.join(WORK, "req.json"); json.dump({"scenes": sorted(scenes), "persons": sorted(persons), "busts": sorted(busts)}, open(req, "w"))
    subprocess.run(["node", os.path.join(HERE, "viz", "assets5.js"), req, ASSETS], check=True)
    for E in todo: print(f"ep{E['n']:02d}: {build(E):.1f}s", flush=True)
