"""The edit itself: shots, texts, effects envelopes, grade and SFX, all derived
from the beat map so every event lands on the music."""
import bisect
import json
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")

# Per-photo framing: focus point in source (normalised 0..1 of full image)
# and optional default zoom bias. Tuned by eye on the contact sheet.
FOCUS = {
    "back10": (0.50, 0.40),
    "closeup": (0.47, 0.38),
    "sprint": (0.50, 0.45),
    "sprint2": (0.56, 0.45),
    "volley": (0.47, 0.45),
    "volley2": (0.47, 0.42),
    "flex": (0.50, 0.42),
    "armswide": (0.50, 0.45),
    "fist": (0.47, 0.35),
    "jump": (0.50, 0.40),
    "keeper": (0.62, 0.50),
    "shot": (0.40, 0.50),
    "dribble": (0.62, 0.48),
    "run": (0.50, 0.40),
    "thumbs": (0.50, 0.35),
    "profile": (0.42, 0.40),
    "kick": (0.55, 0.50),
    "chest": (0.48, 0.38),
    "trophy18": (0.71, 0.45),
    "celeb18": (0.62, 0.40),
    "champs18": (0.58, 0.45),
    "young18": (0.50, 0.40),
    "trophyrain": (0.55, 0.45),
    "madrid": (0.50, 0.40),
    "psgface": (0.50, 0.40),
    "psgthumb": (0.45, 0.35),
    "psgdrib": (0.50, 0.45),
    "psgshot": (0.62, 0.55),
}

# Extra zoom for photos where the player is small in frame
ZOOMBIAS = {"madrid": 1.25}
# Horizontal/vertical drift across a shot (fraction of source size)
PAN = {"volley": (0.2, 0.0), "keeper": (0.1, 0.0)}

GRADES = {
    "intro": dict(exposure=0.86, contrast=1.15, shadow=(-0.03, 0.0, 0.05), high=(0.06, 0.02, -0.04),
                  lift=0.015, sat=0.8, bloom=0.28, vignette=0.6, grain=0.022, sharpen=0.4),
    "build": dict(exposure=0.95, contrast=1.15, shadow=(-0.03, 0.0, 0.05), high=(0.05, 0.02, -0.03),
                  lift=0.02, sat=0.55, bloom=0.3, vignette=0.6, grain=0.024, sharpen=0.4),
    "dropA": dict(exposure=1.03, contrast=1.15, shadow=(-0.04, 0.01, 0.06), high=(0.07, 0.02, -0.05),
                  lift=0.0, sat=1.18, bloom=0.3, vignette=0.4, grain=0.02, sharpen=0.45),
    "break": dict(exposure=0.98, contrast=1.0, shadow=(0.0, -0.01, 0.03), high=(0.08, 0.04, -0.02),
                  lift=0.05, sat=0.42, bloom=0.5, vignette=0.5, grain=0.024, sharpen=0.3),
    "dropB": dict(exposure=1.04, contrast=1.25, shadow=(-0.05, 0.0, 0.07), high=(0.08, 0.02, -0.06),
                  lift=0.0, sat=1.28, bloom=0.32, vignette=0.42, grain=0.02, sharpen=0.5),
    "outro": dict(exposure=1.0, contrast=1.1, shadow=(-0.02, 0.0, 0.04), high=(0.05, 0.03, -0.02),
                  lift=0.04, sat=0.55, bloom=0.4, vignette=0.55, grain=0.024, sharpen=0.35),
}


class Timeline:
    def __init__(self, bm):
        self.bm = bm
        self.BEAT = bm["beat"]
        self.BAR = bm["bar"]
        self.sec = {s["name"]: (s["start"], s["end"]) for s in bm["sections"]}
        self.duration = bm["duration"]
        self.kicks = sorted(bm["kicks"])
        self.claps = sorted(bm["claps"])
        self.rolls = sorted(bm["rolls"])
        self.shots = []
        self.texts = []
        self.overlays = []
        self.hits = []      # (t, shake, flash, ca)
        self.blurs = []     # (t, amount) symmetric transition blur spikes
        self.sfx = []
        self.build()
        self.shots.sort(key=lambda s: s["t0"])
        self._starts = [s["t0"] for s in self.shots]

    # -------------------------------------------------------------- helpers
    def bar(self, b):
        return b * self.BAR

    def kicks_in(self, a, b):
        return [k for k in self.kicks if a - 1e-6 <= k < b - 1e-6]

    def shot(self, src, t0, t1, **kw):
        d = dict(src=src, t0=t0, t1=t1, z0=1.04, z1=1.16, curve="velocity", parallax=0.5,
                 focus_abs=FOCUS.get(src, (0.5, 0.4)), seed=(sum(map(ord, src)) % 997) / 97.0 + t0)
        d.update(kw)
        if src in PAN and "pan" not in kw:
            d["pan"] = PAN[src]
        zb = ZOOMBIAS.get(src, 1.0)
        d["z0"] *= zb
        d["z1"] *= zb
        self.shots.append(d)
        return d

    def text(self, text, t_in, t_out, **kw):
        d = dict(text=text, t_in=t_in, t_out=t_out)
        d.update(kw)
        self.texts.append(d)
        return d

    def hit(self, t, shake=0.0, flash=0.0, ca=0.0):
        self.hits.append((t, shake, flash, ca))

    def sfx_at(self, file, t, **kw):
        d = dict(file=file, t=t)
        d.update(kw)
        self.sfx.append(d)

    # -------------------------------------------------------------- the edit
    def build(self):
        B, BAR = self.BEAT, self.BAR
        i0, i1 = self.sec["intro"]
        b0, b1 = self.sec["build"]
        a0, a1 = self.sec["dropA"]
        k0, k1 = self.sec["break"]
        d0, d1 = self.sec["dropB"]
        o0, o1 = self.sec["outro"]

        # ---------------- INTRO: cinematic, one shot per bar, story in text
        intro = [
            ("back10", dict(z0=1.0, z1=1.10, parallax=0.9)),
            ("trophy18", dict(z0=1.06, z1=1.16, parallax=0.6, r0=-1.0, r1=0.5)),
            ("celeb18", dict(z0=1.14, z1=1.02, parallax=0.6, r0=1.0, r1=-0.5)),
            ("psgface", dict(z0=1.0, z1=1.12, parallax=0.7)),
        ]
        for i, (src, kw) in enumerate(intro):
            t0 = self.bar(i)
            self.shot(src, t0, t0 + BAR, curve="smooth", handheld=0.8, **kw)
            if i > 0:
                self.blurs.append((t0, 0.07))
                self.hit(t0, shake=0.35, flash=0.25, ca=0.004)
                self.sfx_at("whoosh.mp3", t0 - 0.16, gain=0.45, fade_out=0.15)
        self.hit(-0.06, shake=0.6, flash=0.45, ca=0.006)

        # hook
        self.text("MBAPPÉ", -0.35, BAR, face="anton", size=300, pos=(0.5, 0.215),
                  layer="behind", anim="slam", exit=0.06, drift=0.06)
        self.text("KYLIAN", 0.30, BAR, face="bebas", size=92, tracking=34, pos=(0.5, 0.125),
                  anim="slide", exit=0.06)
        # 2018
        t = self.bar(1)
        self.text("2018", t, t + BAR, face="anton", size=430, style="outline", stroke=7,
                  pos=(0.5, 0.25), layer="behind", anim="pop", exit=0.06)
        self.text("19 ans.", t + 0.25, t + BAR, face="serif", size=150, pos=(0.5, 0.70),
                  anim="slide", exit=0.06)
        self.text("CHAMPION DU MONDE", t + 0.5, t + BAR, face="bebas", size=74, tracking=12,
                  pos=(0.5, 0.775), anim="slide", exit=0.06)
        # 2022
        t = self.bar(2)
        self.text("2022", t, t + BAR, face="anton", size=430, style="outline", stroke=7,
                  pos=(0.5, 0.25), layer="behind", anim="pop", exit=0.06)
        self.text("Triplé", t + 0.25, t + BAR, face="serif", size=150, pos=(0.5, 0.70),
                  anim="slide", exit=0.06)
        self.text("EN FINALE DE COUPE DU MONDE", t + 0.5, t + BAR, face="bebas", size=64,
                  tracking=10, pos=(0.5, 0.775), anim="slide", exit=0.06)
        # PSG
        t = self.bar(3)
        self.text("256", t, t + BAR, face="anton", size=470, style="outline", stroke=7,
                  pos=(0.5, 0.25), layer="behind", anim="pop", exit=0.06)
        self.text("buts.", t + 0.25, t + BAR, face="serif", size=150, pos=(0.5, 0.70),
                  anim="slide", exit=0.06)
        self.text("MEILLEUR BUTEUR DE L'HISTOIRE DU PSG", t + 0.5, t + BAR, face="bebas",
                  size=58, tracking=8, pos=(0.5, 0.775), anim="slide", exit=0.06)

        # ---------------- BUILD: stutter zoom on the snare roll, then silhouette breath
        roll = [r for r in self.rolls if b0 <= r < b1]
        gap = b1 - B * 0.5
        vis_roll = []
        for r in roll:  # visual steps no faster than 1 per 2 frames
            if not vis_roll or r - vis_roll[-1] >= 2 / 60:
                vis_roll.append(r)
        self.shot("closeup", b0, gap, curve="linear", z0=1.0, z1=1.05, parallax=0.6,
                  stutter=vis_roll, stutter_step=0.012, handheld=0.4)
        last_z = 1.05 * (1 + 0.012 * len(vis_roll))
        self.shot("closeup", gap, b1, mode="silhouette", curve="linear", z0=last_z,
                  z1=last_z * 1.03, parallax=0.0, handheld=0.0)
        for j, r in enumerate(vis_roll):
            frac = (r - b0) / (b1 - b0)
            self.hit(r, shake=0.15 + 0.6 * frac, flash=0.05 + 0.12 * frac, ca=0.002 + 0.006 * frac)
        self.text("10", b0, gap, face="anton", size=900, style="outline", stroke=9,
                  pos=(0.5, 0.36), layer="behind", anim="fade", drift=0.25, opacity=0.9)

        # ---------------- DROP A
        dropA = {
            5: ["volley"],  # pans from body to the ball (see PAN)
            6: ["sprint", "sprint2", "kick"],
            7: ["psgdrib", "psgface", "psgthumb"],
            8: ["madrid"],
            9: ["dribble", "keeper", "run"],
            10: ["shot"],
            11: ["armswide", "flex", "jump"],
            12: ["fist", "thumbs", "volley2", "chest", "celeb18", "back10"],
        }
        self._drop(dropA, a0, base_flash=0.38)
        # drop A texts
        t = self.bar(8)
        self.text("REAL MADRID", t, t + BAR, face="anton", size=250, pos=(0.5, 0.22),
                  layer="behind", anim="slam", exit=0.05)
        self.text("SOULIER D'OR EUROPÉEN 2025", t + 0.2, t + BAR, face="bebas", size=66,
                  tracking=10, pos=(0.5, 0.80), anim="pop", exit=0.05)

        # ---------------- BREAK
        self.shot("champs18", k0, k0 + BAR, curve="smooth", z0=1.0, z1=1.1, parallax=0.5,
                  handheld=0.8)
        roll2 = [r for r in self.rolls if k0 <= r < k1]
        gap2 = k1 - B * 0.5
        vis2 = []
        for r in roll2:
            if not vis2 or r - vis2[-1] >= 2 / 60:
                vis2.append(r)
        self.shot("chest", k0 + BAR, gap2, curve="linear", z0=1.02, z1=1.08, parallax=0.7,
                  stutter=vis2, stutter_step=0.01, handheld=0.5)
        lz = 1.08 * (1 + 0.01 * len(vis2))
        self.shot("chest", gap2, k1, mode="silhouette", curve="linear", z0=lz, z1=lz * 1.03,
                  parallax=0.0, handheld=0.0, rim=(0.25, 0.45, 1.0))
        self.blurs.append((k0 + BAR, 0.07))
        self.hit(k0, shake=0.4, flash=0.55, ca=0.006)
        self.hit(k0 + BAR, shake=0.3, flash=0.3, ca=0.004)
        for r in vis2:
            frac = (r - k0 - BAR) / BAR
            self.hit(r, shake=0.1 + 0.6 * frac, flash=0.04 + 0.1 * frac, ca=0.002 + 0.005 * frac)
        self.text("MEILLEUR BUTEUR", k0 + 0.1, k0 + BAR, face="anton", size=170,
                  pos=(0.5, 0.20), anim="slide", exit=0.06)
        self.text("DES BLEUS EN COUPE DU MONDE", k0 + 0.35, k0 + BAR, face="bebas", size=70,
                  tracking=10, pos=(0.5, 0.265), anim="slide", exit=0.06)
        self.text("et ce n'est pas fini.", k0 + BAR + 0.1, gap2, face="serif", size=120,
                  pos=(0.5, 0.74), anim="slide", exit=0.05)

        # ---------------- DROP B (faster: 5 cuts per bar)
        dropB = {
            15: ["volley2", "kick", "sprint", "armswide", "shot"],
            16: ["dribble", "keeper", "run", "psgdrib", "flex"],
            17: ["jump", "fist", "back10", "sprint2", "volley"],
            18: ["thumbs", "celeb18", "madrid", "trophy18", "psgthumb", "closeup"],
        }
        self._drop(dropB, d0, base_flash=0.42, amp=1.25)
        words = {15: "VITESSE.", 16: "TECHNIQUE.", 17: "PUISSANCE.", 18: "LÉGENDE."}
        for b, wd in words.items():
            t = self.bar(b)
            self.text(wd, t, t + BAR, face="anton", size=260, style="outline", stroke=7,
                      pos=(0.5, 0.19), layer="behind", anim="slam", exit=0.04)

        # ---------------- OUTRO
        self.shot("profile", o0, self.duration, curve="smooth", z0=1.18, z1=1.0, parallax=0.9,
                  handheld=0.6, entry=0.2)
        self.hit(o0, shake=1.6, flash=0.85, ca=0.014)
        self.text("KYLIAN MBAPPÉ", o0 + 0.05, o1 + 0.5, face="anton", size=200,
                  pos=(0.5, 0.21), layer="behind", anim="slam", exit=0.6)
        self.text("la légende continue.", o0 + 0.6, o1 + 0.5, face="serif", size=110,
                  pos=(0.5, 0.75), anim="slide", exit=0.6)
        cr0 = o1 + 0.7
        self.overlays.append(dict(text="ÉDIT ORIGINAL · MUSIQUE ORIGINALE", t_in=cr0,
                                  t_out=self.duration, face="bebas", size=46, tracking=8,
                                  pos=(0.5, 0.47), anim="fade", opacity=0.85, drift=0.0,
                                  shadow=0.0))
        self.overlays.append(dict(text="Photos : Wikimedia Commons (CC BY / CC BY-SA)",
                                  t_in=cr0 + 0.2, t_out=self.duration, face="serif", size=44,
                                  pos=(0.5, 0.515), anim="fade", opacity=0.7, drift=0.0,
                                  shadow=0.0))

        # ---------------- SFX
        self.sfx_at("whistle.mp3", 0.03, gain=0.5, fade_out=0.4)
        self.sfx_at("ambience.mp3", 0.0, gain=0.45, dur=b1 - 0.25, fade_in=0.05, fade_out=1.2)
        self.sfx_at("whoosh.mp3", k0 + BAR - 0.16, gain=0.4, fade_out=0.15)
        for t in (a0, d0):
            self.sfx_at("impact.mp3", t, gain=0.8, fade_out=1.0)
            self.sfx_at("kick.mp3", t, gain=0.55, fade_out=0.3)
        self.sfx_at("crowd.mp3", a0, gain=0.42, dur=6.0, fade_out=3.0)
        self.sfx_at("crowd.mp3", k0, gain=0.3, dur=3.6, fade_in=0.4, fade_out=1.5)
        self.sfx_at("impact.mp3", o0, gain=0.9, fade_out=2.0)
        self.sfx_at("crowd.mp3", o0, gain=0.5, dur=6.5, fade_out=3.5)
        self.sfx_at("kick.mp3", self.bar(10), gain=0.45, fade_out=0.3)

    def _drop(self, plan, sec_start, base_flash=0.35, amp=1.0):
        BAR = self.BAR
        flip = False
        for b, srcs in plan.items():
            t0 = self.bar(b)
            ks = self.kicks_in(t0, t0 + BAR)
            if len(srcs) == 1:
                cuts = [t0, t0 + BAR]
            else:
                cuts = ks[: len(srcs)] + [t0 + BAR]
                cuts[0] = t0
            for j, src in enumerate(srcs):
                a, e = cuts[j], cuts[j + 1]
                flip = not flip
                z0, z1 = (1.22, 1.06) if flip else (1.04, 1.2)
                r0 = (2.0 if flip else -2.0) * amp
                punches = [k for k in ks if a + 1e-6 < k < e - 1e-6]
                self.shot(src, a, e, curve="velocity", z0=z0, z1=z1, r0=r0, r1=0.0,
                          entry=0.16 * amp, punches=punches, punch_amp=0.06 * amp,
                          parallax=0.6, handheld=0.5)
                strong = abs(a - sec_start) < 1e-3
                self.hit(a, shake=(2.0 if strong else 0.9) * amp,
                         flash=0.9 if strong else base_flash,
                         ca=(0.016 if strong else 0.008) * amp)
                self.blurs.append((a, 0.035 * amp))
                for p in punches:
                    self.hit(p, shake=0.6 * amp, flash=0.12, ca=0.005 * amp)
            for c in self.claps:
                if t0 <= c < t0 + BAR:
                    self.hit(c, shake=0.25 * amp, flash=0.0, ca=0.002)

    # -------------------------------------------------------------- queries
    def shot_at(self, t):
        i = bisect.bisect_right(self._starts, t) - 1
        return self.shots[max(0, i)]

    def section_at(self, t):
        for name, (a, b) in self.sec.items():
            if a <= t < b:
                return name
        return "outro"

    def env_at(self, t):
        shake = flash = ca = 0.0
        for (h, s, f, c) in self.hits:
            if h <= t < h + 1.0:
                e = t - h
                shake += s * math.exp(-e / 0.16)
                flash += f * math.exp(-e / 0.055)
                ca += c * math.exp(-e / 0.10)
        blur = 0.0
        for (h, a) in self.blurs:
            blur += a * math.exp(-abs(t - h) / 0.035)
        sec = self.section_at(t)
        base = {"intro": 0.02, "build": 0.05, "dropA": 0.12, "break": 0.03,
                "dropB": 0.2, "outro": 0.03}[sec]
        shake += base
        # letterbox: cinematic bars in calm sections, snap open on drops
        lb_full = 118
        lb = 0.0
        if sec in ("intro", "build", "break") or (sec == "outro"):
            a = self.sec[sec][0]
            lb = lb_full * min(1.0, (t - a) / 0.5) if sec in ("break", "outro") else lb_full
            if sec == "intro":
                lb = lb_full
        if t >= self.sec["outro"][1]:
            lb = lb_full
        leak = {"intro": 0.14, "build": 0.1, "dropA": 0.0, "break": 0.26,
                "dropB": 0.0, "outro": 0.1}[sec]
        for acc in (self.sec["dropA"][0], self.sec["dropB"][0], self.sec["outro"][0]):
            if acc <= t < acc + 1.0:
                leak += 0.25 * math.exp(-(t - acc) / 0.25)
        black = 0.0
        o1 = self.sec["outro"][1]
        if t > o1 + 0.2:
            black = min(1.0, (t - o1 - 0.2) / 0.6)
        # strobe on the last (fill) bar of each drop
        strobe = 0.0
        for b in (12, 18):
            a = self.bar(b) + self.BAR * 0.5
            if a <= t < self.bar(b + 1) - self.BEAT * 0.5:
                strobe = 0.22 if int(t * 30) % 2 == 0 else -0.08
        return dict(shake=shake, flash=min(flash, 0.95), ca=min(ca, 0.02), blur=min(blur, 0.1),
                    letterbox=lb, leak=leak, black=black, strobe=strobe)

    def grade_at(self, t):
        sec = self.section_at(t)
        g = dict(GRADES[sec])
        if sec == "build":
            a, b = self.sec["build"]
            fr = (t - a) / (b - a)
            g["sat"] = 0.55 - 0.3 * fr
            g["exposure"] = 0.98 - 0.12 * fr
        if sec == "outro" or t >= self.sec["outro"][1]:
            a = self.sec["outro"][0]
            fr = min(1.0, max(0.0, (t - a - 0.4) / 2.5))
            g["sat"] = 0.75 * (1 - fr) + 0.0 * fr
        return g


_T = None


def get():
    global _T
    if _T is None:
        with open(os.path.join(BUILD, "beatmap.json")) as f:
            _T = Timeline(json.load(f))
    return _T
