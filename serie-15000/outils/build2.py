"""Montage v2 « style BD gros plan » : python3 build2.py SCRIPTS VOIX OUT [épisodes]"""
import re, os, sys, glob, json, hashlib, subprocess, unicodedata, random, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

SCRIPTS, VOIX, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
ONLY = set(int(x) for x in sys.argv[4].split(",")) if len(sys.argv) > 4 else None
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "v2work"); ASSETS = os.path.join(WORK, "assets"); SEG = os.path.join(WORK, "seg")
for d in (WORK, ASSETS, SEG, OUT): os.makedirs(d, exist_ok=True)
FPS, W, H = 30, 1080, 1920
CW = 1380                       # largeur d'affichage du personnage (gros plan)
def F(w, s): return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{w}.otf", s)
def A(s): return ImageFont.truetype("/root/.fonts/Anton-Regular.ttf", s)

def norm(s):
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if unicodedata.category(c) != "Mn").upper().strip()
def clean(t):
    t = t.replace("🅰️", "").replace("🅱️", "")
    return re.sub(r"\s+", " ", "".join(c for c in t if ord(c) < 0x2190 or c in "→€…’«»★")).strip()

TAGS = ["YANIS", "VIDAL", "SOFIANE", "LINA", "NADIA", "GERARD", "BRUNO", "KARIM", "INES", "BERNARD", "MALIK"]
WHO = {"LE POLICIER": "POLICIER", "L'HOMME EN GRIS": "GRIS", "L'ACHETEUR": "ACHETEUR", "UNE VOIX": None, "TOUS": "YANIS"}
COLORS = {"YANIS": "#ffcf4a", "VIDAL": "#ff5a5a", "SOFIANE": "#5ad1ff", "LINA": "#ff8ad8", "NADIA": "#b59cff", "GERARD": "#8fe08a",
          "BRUNO": "#ff9a4a", "KARIM": "#f2f2f2", "INES": "#ff7ab8", "BERNARD": "#e0b07a", "MALIK": "#e8d3a0", "POLICIER": "#8fb8ff", "GRIS": "#cccccc", "ACHETEUR": "#cccccc"}
DEFAULT = {"YANIS": "inquiet", "VIDAL": "mefiant", "SOFIANE": "sourire", "LINA": "neutre", "NADIA": "inquiet", "GERARD": "inquiet", "BRUNO": "determine",
           "KARIM": "calme", "INES": "sourire", "BERNARD": "tendre", "MALIK": "tendre", "POLICIER": "neutre", "GRIS": "calme", "ACHETEUR": "neutre"}
CUES = [("larmes", ("crying", "tears", "red eyes")), ("panique", ("scared", "panick", "out of breath", "panting", "running")),
        ("choque", ("shock", "freez", "pale", "stops dead")), ("colere", ("angry", "anger", "shouting", "slams", "throwing")),
        ("sourire", ("smil", "proud", "joy", "dancing", "laughing", "happy", "excited", "relieved", "amused")),
        ("triste", ("sad", "devastated", "head down", "defeated", "ashamed", "exhausted")), ("tendre", ("tender", "moved", "gentle", "kiss")),
        ("determine", ("determined", "serious", "firmly")), ("mefiant", ("skeptical", "suspicious", "doubtful", "stares", "staring", "cold")),
        ("inquiet", ("worried", "nervous", "hesitat", "tense", "listening")), ("calme", ("calm", "relaxed", "confident", "arrogant"))]

def scene_of(cam, prev):
    c = cam.lower(); night = any(k in c for k in ("night", "dark", "dusk"))
    if "police lights" in c: return "police"
    for tag, sc in (("{BUREAU}", "bureau"), ("{ENTREPOT}", "entrepot"), ("{CAVE}", "cave"), ("{TOIT}", "toit"), ("{PMU}", "pmu"),
                    ("{COMMISSARIAT}", "commissariat"), ("{VOITURE}", "voiture"), ("{PARKING}", "parking"), ("{BOULANGERIE}", "boulangerie")):
        if tag in cam: return sc
    if "{GARAGE}" in cam: return "garageNuit" if night else "garage"
    if "{CUISINE}" in cam: return "cuisineNuit" if night else "cuisine"
    if "{CHAMBRE}" in cam: return "chambreNuit" if night else "chambre"
    if any(k in c for k in ("stairwell", "hall", "front door", "hallway")): return "hall"
    if "a car at night" in c: return "voiture"
    if any(k in c for k in ("street", "sidewalk", "balcony", "outside", "memory")): return "rueJour" if "morning" in c else "rue"
    return prev or "garage"

def cue(pid, cam, emo="normal", text=""):
    if emo == "sad": return "larmes" if pid in ("NADIA",) else "triste"
    if emo == "whisper": return "inquiet"
    if emo == "shout": return "choque" if "?" in text else "colere"
    if emo == "memory": return "tendre"
    t = "{" + pid + "}"
    if t in cam:
        i = cam.find(t); nx = [cam.find("{" + o + "}", i + len(t)) for o in TAGS]; nx = [x for x in nx if x > 0]; win = cam[i:(min(nx) if nx else len(cam))].lower()
        for ex, keys in CUES:
            if any(k in win for k in keys): return ex
    if emo == "excited": return "sourire" if pid in ("SOFIANE", "LINA", "INES", "BERNARD") else "choque"
    return DEFAULT.get(pid, "neutre")

def emotion(direction, text, cam, who):
    d = direction.lower()
    if any(k in d for k in ("téléphone", "appel")): return "phone"
    if "voix off, grave" in d: return "memory"
    if "chuchot" in d: return "whisper"
    if any(k in d for k in ("larmes", "se brise")): return "sad"
    if "!" in text and (re.findall(r"\b[A-ZÉÈÀÇ]{3,}\b", text) or "?!" in text): return "shout"
    if "!" in text: return "excited"
    return "normal"

# ---------------- parsing ----------------
def parse():
    eps = {}
    for f in sorted(glob.glob(os.path.join(SCRIPTS, "ep*.md"))):
        ep = None; n = 0; cur = None
        for line in open(f, encoding="utf-8"):
            m = re.match(r"## Épisode (\d+) · (J-\d+) · « (.+?) »", line)
            if m:
                ep = int(m.group(1)); n = 0; cur = None
                eps[ep] = {"n": ep, "j": m.group(2), "title": m.group(3), "blocks": [], "counter": "0", "alt": {}, "choice": None}
                continue
            if ep is None: continue
            E = eps[ep]; s = line.strip()
            if s.startswith("⏱️"):
                m = re.search(r"`J-\d+ · ([\d ]+) €", s)
                if m: E["counter"] = m.group(1).strip()
                for amt, ab in re.findall(r"\*\(([\d ]+) €[^)]*? si (A|B)", s): E["alt"][ab] = amt.strip()
                continue
            kind = "A" if s.startswith("**🅰️") else "B" if s.startswith("**🅱️") else "R" if s.startswith("**R ·") else "main" if re.match(r"\*\*P\d+", s) else None
            if kind:
                tag = kind if kind in ("A", "B") else re.match(r"\*\*(P\d+|R)", s).group(1)
                cur = {"kind": kind, "tag": tag, "cam": "", "notes": [], "lines": []}; E["blocks"].append(cur); continue
            if cur is None: continue
            if s.startswith("🎥"): cur["cam"] += " " + s
            elif s.startswith("📝"):
                bt = re.findall(r"`([^`]+)`", s)
                if "🅰️" in s and len(bt) >= 2:
                    E["choice"] = (clean(bt[0]), clean(bt[1])); cur["choice"] = True
                elif bt:
                    lab = re.findall(r"\*\(([^)]+)\)\*", s)
                    cur["notes"].append((clean(lab[0]) if lab else "", clean(" / ".join(bt))))
            elif s.startswith("🗣️"):
                m = re.match(r"🗣️ \*\*(.+?)\*\*(.*)", s)
                parts = re.findall(r"«\s*(.+?)\s*»", m.group(2))
                if not parts: continue
                n += 1; who = norm(m.group(1))
                fname = f"{n:02d}_{cur['tag'] if cur['tag'] not in ('A','B') else 'ouverture-'+cur['tag']}_{who.replace(' ','-').replace(chr(39),'')}.mp3"
                cur["lines"].append({"who": who, "label": clean(m.group(1)), "text": clean(" ".join(parts)),
                                     "dir": " ".join(re.findall(r"\*\((.+?)\)\*", m.group(2))), "audio": os.path.join(VOIX, f"ep{ep:02d}", fname)})
    return eps

# ---------------- audio utils ----------------
def dur(p): return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]).decode())
def envelope(p, step=0.1):
    raw = subprocess.check_output(["ffmpeg", "-loglevel", "error", "-i", p, "-f", "s16le", "-ac", "1", "-ar", "8000", "-"])
    a = np.frombuffer(raw, dtype=np.int16).astype(np.float32); k = int(8000 * step)
    rms = np.array([np.sqrt(np.mean(a[i:i + k] ** 2)) for i in range(0, max(len(a) - k, 1), k)] or [0])
    st = (rms > 0.25 * max(rms.max(), 1)).astype(int)
    for i in range(2, len(st)):
        if st[i] and st[i - 1] and st[i - 2]: st[i] = 0
    return st
def run(cmd): subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

# ---------------- texte (calque) ----------------
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
        if len(t) <= 13 or not cur: cur = t
        else: out.append(cur); cur = w_
    if cur: out.append(cur)
    return out

def layer(st, big=None):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    g = Image.new("RGBA", (W, 380)); gd = ImageDraw.Draw(g)
    for i in range(380): gd.line([(0, i), (W, i)], fill=(0, 0, 0, int(140 * (1 - i / 380))))
    im.alpha_composite(g)
    # compteur
    f = F("ExtraBold", 46); t = st["counter"]; tw = d.textlength(t, font=f)
    rr(d, ((W - tw) / 2 - 34, 140, (W + tw) / 2 + 34, 222), 40, (0, 0, 0, 175))
    d.text((W / 2, 181), t, font=f, fill=st.get("ccolor", "white"), anchor="mm")
    y = 250
    if st.get("toplabel"):
        f2 = A(64); t2 = st["toplabel"]; tw2 = d.textlength(t2, font=f2)
        rr(d, ((W - tw2) / 2 - 26, y, (W + tw2) / 2 + 26, y + 92), 20, st.get("tlcolor", "#ffcf4a"), "#141414", 6)
        d.text((W / 2, y + 46), t2, font=f2, fill="#141414", anchor="mm"); y += 120
    for lab, txt in st.get("cards", []):
        ft = F("Bold", 42); lines = wrap(txt, ft, 840, d)[:4]
        h = 34 + (42 if lab else 0) + len(lines) * 54 + 18
        rr(d, (90, y, W - 90, y + h), 28, (255, 255, 255, 245), "#141414", 6)
        yy = y + 24
        if lab: d.text((122, yy), lab.upper(), font=F("Bold", 28), fill=(110, 110, 110)); yy += 42
        for ln in lines: d.text((122, yy), ln, font=ft, fill=(20, 20, 24)); yy += 54
        y += h + 18
    if st.get("phone"):
        rr(d, (240, y, W - 240, y + 120), 60, (20, 22, 30, 235), "#141414", 6)
        d.text((W / 2, y + 60), "📞 " if False else f"APPEL · {st['phone']}", font=A(58), fill="#5ee38a", anchor="mm")
    if st.get("choice"):
        a, b = st["choice"]
        rr(d, (50, 330, W - 50, 1180), 40, (14, 16, 24, 235), "#141414", 8)
        d.text((W / 2, 430), "À TOI DE CHOISIR", font=A(110), fill="#ffcf4a", anchor="mm", stroke_width=6, stroke_fill="#141414")
        yy = 540
        for L, col, txt in (("A", "#ff4d4d", a), ("B", "#3d8bff", b)):
            d.ellipse((90, yy, 210, yy + 120), fill=col, outline="#141414", width=6); d.text((150, yy + 60), L, font=A(80), fill="white", anchor="mm")
            ls = wrap(txt, F("ExtraBold", 50), 700, d)[:3]; ty = yy + 60 - len(ls) * 30
            for ln in ls: d.text((240, ty), ln, font=F("ExtraBold", 50), fill="white"); ty += 60
            yy += 250
        d.text((W / 2, 1100), "VOTE EN COMMENTAIRE ↓", font=A(76), fill="white", anchor="mm")
    if st.get("title"):
        n_, t_ = st["title"]
        d.text((W / 2, 1180), n_, font=A(90), fill="#ffcf4a", anchor="mm", stroke_width=10, stroke_fill="#000")
        fb = A(170)
        while d.textlength(t_.upper(), font=fb) > 1000 and fb.size > 90: fb = A(fb.size - 10)
        d.text((W / 2, 1330), t_.upper(), font=fb, fill="white", anchor="mm", stroke_width=14, stroke_fill="#000")
    if st.get("manque"):
        d.text((W / 2, 1180), "IL MANQUE", font=A(110), fill="white", anchor="mm", stroke_width=12, stroke_fill="#000")
        d.text((W / 2, 1340), st["manque"], font=A(190), fill="#ff4d4d", anchor="mm", stroke_width=14, stroke_fill="#000")
    if st.get("suspense"):
        d.text((W / 2, 1180), "QUE VA FAIRE", font=A(120), fill="white", anchor="mm", stroke_width=12, stroke_fill="#000")
        d.text((W / 2, 1330), "YANIS ?", font=A(190), fill="#ffcf4a", anchor="mm", stroke_width=14, stroke_fill="#000")
    if st.get("result"):
        L, txt = st["result"]; col = "#ff4d4d" if L == "A" else "#3d8bff"
        rr(d, (70, 330, W - 70, 760), 40, (14, 16, 24, 230), "#141414", 8)
        d.text((W / 2, 420), "VOUS AVEZ CHOISI", font=A(90), fill="white", anchor="mm")
        d.ellipse((W / 2 - 75, 480, W / 2 + 75, 630), fill=col, outline="#141414", width=7); d.text((W / 2, 555), L, font=A(100), fill="white", anchor="mm")
        ls = wrap(txt, F("ExtraBold", 46), 860, d)[:2]; ty = 660
        for ln in ls: d.text((W / 2, ty), ln, font=F("ExtraBold", 46), fill="#ffcf4a", anchor="mm"); ty += 56
    if big:
        fb = A(150)
        while d.textlength(big, font=fb) > 1000 and fb.size > 90: fb = A(fb.size - 10)
        d.text((W / 2, 1290), big.upper(), font=fb, fill="white", anchor="mm", stroke_width=13, stroke_fill="#000")
    if st.get("sub"):
        fs = F("Bold", 42); ls = wrap(st["sub"], fs, 900, d)[:3]
        yy = 1420
        lab = st.get("sublabel")
        if lab:
            tw3 = d.textlength(lab, font=A(40)); rr(d, (W / 2 - tw3 / 2 - 18, yy - 58, W / 2 + tw3 / 2 + 18, yy - 6), 14, st.get("subcolor", "#ffcf4a"))
            d.text((W / 2, yy - 32), lab, font=A(40), fill="#141414", anchor="mm")
        for ln in ls:
            tw4 = d.textlength(ln, font=fs); rr(d, (W / 2 - tw4 / 2 - 20, yy, W / 2 + tw4 / 2 + 20, yy + 60), 12, (35, 35, 35, 215))
            d.text((W / 2, yy + 30), ln, font=fs, fill="white", anchor="mm"); yy += 66
    return im

# ---------------- plan ----------------
def plan(E, version, prev_choice):
    counter = E["alt"].get(version, E["counter"]) if version else E["counter"]
    blocks = [b for b in E["blocks"] if b["kind"] in ("main", "R") or b["kind"] == version]
    segs, scene, first = [], None, True
    jn = 31 - int(E['j'][2:]) if E['j'] != "J-0" else 30
    segs.append(dict(kind="silent", dur=2.6, scene=scene_of(blocks[0]["cam"], None), flash=False, cards=[], counter=f"{E['j']} · {counter} € / 15 000 €",
                     ccolor="white", newblock=True, pid="YANIS", expr="inquiet", title=(f"JOUR {jn} SUR 30", E["title"]), sfx="boom", intro=True))
    def ctr(): return f"{E['j']} · {counter} € / 15 000 €"
    for bi, b in enumerate(blocks):
        cam = b["cam"]; scene = scene_of(cam, scene)
        flash = "flashback" in cam.lower() or "{FLASHBACK}" in cam
        tags = sorted([t for t in TAGS if "{" + t + "}" in cam], key=lambda t: cam.find("{" + t + "}")) or ["YANIS"]
        cards, ccolor = [], "white"
        for lab, txt in b["notes"]:
            m = re.search(r"→\s*([\d ]+) €", txt)
            if m:
                old = int(re.sub(r"\D", "", counter) or 0); new = int(re.sub(r"\D", "", m.group(1)))
                ccolor = "#ff4d4d" if new < old else "#5ee38a"; counter = f"{new:,}".replace(",", " ")
            cards.append((lab, txt))
        base = dict(scene=scene, flash=flash, cards=cards, counter=ctr(), ccolor=ccolor, newblock=True)
        if first: base["toplabel"] = f"JOUR {31 - int(E['j'][2:])} SUR 30" if E['j'] != "J-0" else "JOUR 30 SUR 30"
        if b["kind"] in ("A", "B"):
            res = (b["kind"], prev_choice[0 if b["kind"] == "A" else 1]) if prev_choice else None
            segs.append(dict(base, kind="silent", dur=3.0, pid=tags[0], expr=cue(tags[0], cam), result=res, cards=[], sfx="whoosh"))
            if cards:
                segs.append(dict(base, kind="silent", dur=2.0 + sum(len(t) for _, t in cards) / 22, pid=tags[0], expr=cue(tags[0], cam), toplabel=None, newblock=False, sfx="pop"))
            first = False; continue
        if not b["lines"]:
            segs.append(dict(base, kind="silent", dur=min(5.5, 2.2 + sum(len(t) for _, t in cards) / 20), pid=tags[0], expr=cue(tags[0], cam), sfx="pop" if cards else "whoosh"))
            first = False; continue
        for i, l in enumerate(b["lines"]):
            pid = WHO.get(l["who"], l["who"])
            emo = emotion(l["dir"], l["text"], cam, l["who"])
            off = "off" in l["dir"].lower() and "voix off, grave" not in l["dir"].lower()
            st = dict(base, kind="line", audio=l["audio"], sub=l["text"], sublabel=l["label"].upper() if pid else "UNE VOIX",
                      subcolor=COLORS.get(pid or "", "#dddddd"), gap=0.35, emo=emo, sfx=("whoosh" if i == 0 and bi > 0 else None))
            if i > 0: st.update(newblock=False, toplabel=None, ccolor="white")
            if b["kind"] == "R": st.update(toplabel="RÉSUMÉ", tlcolor="#ff4d4d")
            if emo == "phone" and pid not in tags:
                local = [t for t in tags if t != pid][:1] or ["YANIS"]
                st.update(pid=local[0], expr=cue(local[0], cam), talk=False, phone=l["label"].upper())
            elif emo == "memory":
                st.update(pid="MALIK", expr="tendre", talk=True, flash=True)
            elif pid is None:
                st.update(pid=tags[0], expr="panique", talk=False)
            else:
                st.update(pid=pid, expr=cue(pid, cam, emo, l["text"]), talk=not off)
            if emo == "shout" or st["expr"] in ("panique", "colere", "choque"): st["shake"] = True
            segs.append(st)
            others = [t for t in tags if t != st["pid"]]
            if not others and not st.get("phone") and st.get("talk"):
                alt = {"inquiet": "triste", "panique": "choque", "choque": "panique", "colere": "determine", "triste": "inquiet",
                       "sourire": "tendre", "determine": "mefiant", "mefiant": "calme", "calme": "mefiant", "tendre": "sourire",
                       "larmes": "triste", "neutre": "inquiet"}.get(st["expr"], "inquiet")
                segs.append(dict(base, kind="silent", dur=1.5, pid=st["pid"], expr=alt, newblock=True, toplabel=None, ccolor="white",
                                 cards=[], sfx=None, react=True, flash=st["flash"]))
            if others and st["kind"] == "line" and not st.get("phone"):
                segs.append(dict(base, kind="silent", dur=1.6, pid=others[0], expr=cue(others[0], cam), newblock=True, toplabel=None,
                                 ccolor="white", sfx=None, react=True, shake=st.get("shake", False) and False))
        if b.get("choice"):
            rest = 15000 - int(re.sub(r"\D", "", counter) or 0)
            if rest > 0:
                segs.append(dict(base, kind="silent", dur=2.6, pid="YANIS", expr="inquiet", manque=f"{rest:,} €".replace(",", " "), cards=[],
                                 toplabel=None, newblock=True, sfx="boom", fill=True))
            segs.append(dict(base, kind="silent", dur=2.6, pid="YANIS", expr="inquiet", manque=None, suspense=True, cards=[],
                             toplabel=None, newblock=True, sfx="whoosh"))
            segs.append(dict(base, kind="silent", dur=3.6, pid="YANIS", expr="determine", choice=E["choice"], cards=[], toplabel=None, newblock=False, sfx="boom"))
        first = False
    # durée mini 62 s : on allonge les silences puis les respirations
    def total():
        return sum((dur(s["audio"]) + s["gap"]) if s["kind"] == "line" else s["dur"] for s in segs)
    T = total(); need = 64 - T
    if need > 0:
        sil = [s for s in segs if s["kind"] == "silent" and not s.get("choice") and not s.get("intro")]
        for s in sil: s["dur"] += min(3.2, need / max(1, len(sil)))
        T = total(); need = 64 - T
    if need > 0:
        ls = [s for s in segs if s["kind"] == "line"]
        for s in ls: s["gap"] += min(1.6, need / max(1, len(ls)))
        T = total(); need = 64 - T
    if need > 0: segs[-1]["dur"] += min(need, 12.0)
    return segs

# ---------------- rendu ----------------
def sepia(im):
    g = ImageOps.grayscale(im.convert("RGB")); s = ImageOps.colorize(g, "#2a1d10", "#f3e2c0").convert("RGBA")
    if im.mode == "RGBA": s.putalpha(im.getchannel("A"))
    return s

def render_seg(s):
    D = (dur(s["audio"]) + s["gap"]) if s["kind"] == "line" else s["dur"]
    key = hashlib.md5(json.dumps(s, sort_keys=True, default=str).encode()).hexdigest()[:16]
    out = os.path.join(SEG, key + ".mp4")
    if os.path.exists(out): return out, D
    tmp = os.path.join(SEG, key); os.makedirs(tmp, exist_ok=True)
    bg = Image.open(os.path.join(ASSETS, f"bg_{s['scene']}.png")).convert("RGB")
    if s["flash"]: bg = sepia(bg).convert("RGB")
    bgp = os.path.join(tmp, "bg.png"); bg.save(bgp, compress_level=1)
    def char(talk):
        im = Image.open(os.path.join(ASSETS, f"t_{s['pid']}_{s['expr']}_{1 if talk else 0}.png")).convert("RGBA")
        if s["flash"]: im = sepia(im)
        p = os.path.join(tmp, f"c{int(talk)}.png"); im.save(p, compress_level=1); return p
    c0 = char(False)
    clist = os.path.join(tmp, "c.txt")
    if s["kind"] == "line" and s.get("talk"):
        c1 = char(True); env = envelope(s["audio"]); runs = []
        for v in env:
            if runs and runs[-1][0] == v: runs[-1][1] += 0.1
            else: runs.append([v, 0.1])
        rest = D - sum(r[1] for r in runs)
        if rest > 0: runs.append([0, rest])
        open(clist, "w").write("".join(f"file '{c1 if v else c0}'\nduration {t:.3f}\n" for v, t in runs) + f"file '{c0}'\n")
    else:
        open(clist, "w").write(f"file '{c0}'\nduration {D:.3f}\nfile '{c0}'\n")
    # calque texte : gros mots successifs
    tlist = os.path.join(tmp, "t.txt")
    if s["kind"] == "line":
        ch = chunks(s["sub"]); ad = dur(s["audio"]) - 0.12; tot = sum(len(c) + 2 for c in ch)
        body, t0 = "", 0.0
        p0 = os.path.join(tmp, "t_.png"); layer(s).save(p0, compress_level=1)
        body += f"file '{p0}'\nduration 0.120\n"
        for i, c in enumerate(ch):
            p = os.path.join(tmp, f"t{i}.png"); layer(s, c).save(p, compress_level=1)
            dd = ad * (len(c) + 2) / tot; body += f"file '{p}'\nduration {dd:.3f}\n"; t0 += dd
        rest = D - 0.12 - t0
        body += f"file '{p0}'\nduration {max(rest, 0.05):.3f}\nfile '{p0}'\n"
        open(tlist, "w").write(body)
    else:
        p0 = os.path.join(tmp, "t_.png"); layer(s).save(p0, compress_level=1)
        open(tlist, "w").write(f"file '{p0}'\nduration {D:.3f}\nfile '{p0}'\n")
    ph = random.Random(key).uniform(0, 6.28); off = random.Random(key + "x").choice([-50, 0, 50])
    sh = 14 if s.get("shake") else 0
    zoom = f"(1+0.05*t/{D:.3f}+0.13*max(0\\,1-t/0.22))" if s.get("newblock") or s["kind"] == "line" else f"(1+0.04*t/{D:.3f})"
    fc = (f"[0:v]crop=1080:1920:x='54+40*sin(t*0.35+{ph:.2f})':y='96-60*t/{D:.3f}'[b];"
          f"[1:v]fps={FPS},format=rgba,scale=w='trunc({CW}*{zoom}/2)*2':h=-2:eval=frame[c];"
          f"[b][c]overlay=x='(W-w)/2+{off}+{sh}*sin(t*75)*max(0\\,1-t/0.6)':y='H-h+170':eval=frame[bc];"
          f"[2:v]fps={FPS},format=rgba[t];[bc][t]overlay=0:0,format=yuv420p[v]")
    a_in = ["-i", s["audio"]] if s["kind"] == "line" else ["-f", "lavfi", "-t", f"{D:.3f}", "-i", "anullsrc=r=44100:cl=stereo"]
    run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", str(FPS), "-t", f"{D:.3f}", "-i", bgp,
         "-f", "concat", "-safe", "0", "-i", clist, "-f", "concat", "-safe", "0", "-i", tlist, *a_in,
         "-filter_complex", fc + ";[3:a]aresample=44100,aformat=channel_layouts=stereo,apad[a]",
         "-map", "[v]", "-map", "[a]", "-t", f"{D:.3f}", "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-ar", "44100", out])
    shutil.rmtree(tmp, ignore_errors=True)
    return out, D

SFX = {
    "whoosh": "anoisesrc=color=pink:amplitude=0.6:d=0.45,highpass=f=600,lowpass=f=5000,afade=t=in:d=0.18,afade=t=out:st=0.2:d=0.25,volume=0.5",
    "pop": "sine=f=880:d=0.12,afade=t=out:st=0.03:d=0.09,volume=0.5",
    "boom": "sine=f=55:d=1.2,afade=t=out:st=0.1:d=1.1,volume=2.2",
}
def sfx_files():
    out = {}
    for k, f in SFX.items():
        p = os.path.join(WORK, f"sfx_{k}.wav")
        if not os.path.exists(p): run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f, "-ar", "44100", "-ac", "2", p])
        out[k] = p
    return out

def build(E, version, prev_choice, label):
    segs = plan(E, version, prev_choice)
    files, t, events = [], 0.0, []
    for s in segs:
        f, D = render_seg(s); files.append(f)
        if s.get("sfx"): events.append((s["sfx"], t))
        t += D
    lst = os.path.join(WORK, label + ".txt"); open(lst, "w").write("".join(f"file '{f}'\n" for f in files))
    raw = os.path.join(WORK, label + "_raw.mp4")
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", raw])
    sf = sfx_files()
    drone = "0.08*sin(2*PI*55*t)*(0.6+0.4*sin(2*PI*0.2*t))+0.05*sin(2*PI*82.4*t)+0.03*sin(2*PI*110*t)*(0.5+0.5*sin(2*PI*0.13*t))+0.25*sin(2*PI*1700*t)*exp(-70*mod(t,1))"
    ins = ["-i", raw, "-f", "lavfi", "-i", f"aevalsrc='{drone}':s=44100:d={t:.2f}"]
    fc = f"[1:a]lowpass=f=2500,afade=t=in:d=1.5,afade=t=out:st={max(0, t - 2):.2f}:d=2,volume=0.45,aformat=channel_layouts=stereo[m]"
    mix = ["[0:a]", "[m]"]
    for i, (k, at) in enumerate(events):
        ins += ["-i", sf[k]]; ms = int(at * 1000)
        fc += f";[{i + 2}:a]adelay={ms}|{ms}[e{i}]"; mix.append(f"[e{i}]")
    fc += f";{''.join(mix)}amix=inputs={len(mix)}:duration=first:normalize=0,alimiter=limit=0.95[a]"
    out = os.path.join(OUT, label + ".mp4")
    run(["ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex", fc, "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out])
    os.remove(raw)
    return t

if __name__ == "__main__":
    eps = parse()
    todo = []
    for n in sorted(eps):
        if ONLY and n not in ONLY: continue
        E = eps[n]; prev = eps.get(n - 1, {}).get("choice")
        ab = any(b["kind"] in ("A", "B") for b in E["blocks"])
        for v in (("A", "B") if ab else (None,)): todo.append((E, v, prev, f"ep{n:02d}" + (f"-{v}" if v else "")))
    scenes, persons = set(), set()
    for E, v, prev, _ in todo:
        for s in plan(E, v, prev):
            scenes.add(s["scene"]); persons.add((s["pid"], s["expr"], 0)); persons.add((s["pid"], s["expr"], 1))
    req = os.path.join(WORK, "req.json"); json.dump({"scenes": sorted(scenes), "persons": sorted(persons)}, open(req, "w"))
    subprocess.run(["node", os.path.join(HERE, "viz", "assets2.js"), req, ASSETS], check=True)
    rep = []
    for E, v, prev, label in todo:
        T = build(E, v, prev, label); rep.append(f"{label}: {T:.1f}s"); print(rep[-1], flush=True)
    open(os.path.join(OUT, "durees.txt"), "a").write("\n".join(rep) + "\n")
