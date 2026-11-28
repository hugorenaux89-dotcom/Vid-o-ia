"""Timeline du quiz : calculée à partir des vraies durées des voix (fichiers rognés)."""
import json, math, os, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOICE_DIR = os.environ.get("VOICE_DIR") or os.path.join(ROOT, "assets", "voice", "trimmed")
FPS = 30
BEAT = 0.5  # 120 BPM
CTA_AFTER = 2  # index de la question après laquelle on place l'appel (Q3)
CD_STEP = float(os.environ.get("CD_STEP", "0.8"))  # durée d'un chiffre du compte à rebours

LEVELS = {
    "FACILE":    {"color": (0x2E, 0xCC, 0x40), "label": "Facile"},
    "MOYEN":     {"color": (0xFF, 0xC3, 0x00), "label": "Moyen"},
    "DIFFICILE": {"color": (0xFF, 0x6B, 0x00), "label": "Difficile"},
    "EXTREME":   {"color": (0xC0, 0x00, 0x2A), "label": "Extrême", "accent": (0x7B, 0x2C, 0xBF)},
}
LEVEL_ORDER = ["FACILE", "MOYEN", "DIFFICILE", "EXTREME"]

QTEXT = "QUEL EST CE PAYS ?"

QUESTIONS = [
    # flag file, réponse courte (échelle), réponse affichée, niveau, voix question, voix réponse, bandeau, suspense, texte question
    dict(flag="Japan", short="Japon", big="JAPON", level="FACILE", vq="02_Q1_question", vr="03_Q1_reponse"),
    dict(flag="Brazil", short="Brésil", big="BRÉSIL", level="FACILE", vq="04_Q2_question", vr="05_Q2_reponse"),
    dict(flag="Canada", short="Canada", big="CANADA", level="FACILE", vq="06_Q3_question", vr="07_Q3_reponse"),
    dict(flag="Turkey", short="Turquie", big="TURQUIE", level="MOYEN", vq=None, vr="09_Q4_reponse",
         banner=("NIVEAU MOYEN !", "08_niveau_moyen")),
    dict(flag="Greece", short="Grèce", big="GRÈCE", level="MOYEN", vq="10_Q5_question", vr="11_Q5_reponse"),
    dict(flag="South_Korea", short="Corée du Sud", big="CORÉE DU SUD", level="MOYEN", vq="12_Q6_question", vr="13_Q6_reponse"),
    dict(flag="Nepal", short="Népal", big="NÉPAL", level="DIFFICILE", vq=None, vr="15_Q7_reponse",
         banner=("ÇA SE COMPLIQUE !", "14_niveau_difficile")),
    dict(flag="Kazakhstan", short="Kazakhstan", big="KAZAKHSTAN", level="DIFFICILE", vq="16_Q8_question", vr="17_Q8_reponse"),
    dict(flag="Bhutan", short="Bhoutan", big="BHOUTAN", level="EXTREME", vq=None, vr="20_Q9_reponse",
         banner=("NIVEAU EXTRÊME !", "18_niveau_extreme")),
    dict(flag="Chad", short="Tchad", big="TCHAD", level="EXTREME", vq="21_Q10_question", vr="22_Q10_reponse",
         qtext="INDICE : CE N'EST\nPAS LA ROUMANIE !"),
]


# ---------- Quiz générique (fichier quizzes/<slug>/quiz.json) ----------
V_ACCROCHE, V_CTA, V_CONCL = "01_accroche", "07b_cta", "23_conclusion"
META = dict(title="QUIZ DRAPEAUX", logo="🌍", accroche_screen="SEULS LES VRAIS FANS\nAURONT 10/10 !",
            default_qtext="QUEL EST\nCE PAYS ?", bg=dict(type="flags"))
BANNER_TXT = {"MOYEN": ("NIVEAU MOYEN !", "Niveau moyen !"), "DIFFICILE": ("ÇA SE COMPLIQUE !", "Ça se complique !"),
              "EXTREME": ("NIVEAU EXTRÊME !", "Niveau extrême !")}
QUIZ_FILE = os.environ.get("QUIZ")


def voice_lines(quiz):
    """Toutes les répliques à générer pour un quiz : {nom: (texte, style)}."""
    L = {"00_accroche": (quiz["accroche_voice"], "hype")}
    prev = None
    for i, q in enumerate(quiz["questions"]):
        n = f"q{i + 1:02d}"
        if q["level"] != prev and prev is not None:
            L[f"{n}_banner"] = (quiz.get("banners", {}).get(q["level"], BANNER_TXT[q["level"]])[1], "hype")
        prev = q["level"]
        if q.get("voice_q"):
            L[f"{n}_q"] = (q["voice_q"], "host")
        L[f"{n}_r"] = (q["voice_r"], "hype")
        if i == CTA_AFTER:
            L["90_cta"] = (quiz.get("cta_voice", "Abonne-toi et like ! On continue !"), "hype")
    L["99_conclusion"] = (quiz.get("conclusion_voice", "Alors, t'as combien ? Dis-le en commentaire !"), "hype")
    return L


if QUIZ_FILE:
    QUIZ = json.load(open(QUIZ_FILE))
    QUIZ_DIR = os.path.dirname(os.path.abspath(QUIZ_FILE))
    VOICE_DIR = os.environ.get("VOICE_DIR") or os.path.join(QUIZ_DIR, "voice")
    V_ACCROCHE, V_CTA, V_CONCL = "00_accroche", "90_cta", "99_conclusion"
    META = dict(title=QUIZ["title"], logo=QUIZ.get("logo", "❓"), accroche_screen=QUIZ["accroche_screen"],
                default_qtext=QUIZ.get("default_qtext", ""), bg=QUIZ.get("bg", dict(type="emoji", items=[QUIZ.get("logo", "❓")])),
                quiz_dir=QUIZ_DIR)
    QUESTIONS = []
    prev = None
    for i, q in enumerate(QUIZ["questions"]):
        n = f"q{i + 1:02d}"
        d = dict(q, short=q["short"], big=q["big"], level=q["level"], vq=f"{n}_q" if q.get("voice_q") else None, vr=f"{n}_r")
        if q["level"] != prev and prev is not None:
            d["banner"] = (QUIZ.get("banners", {}).get(q["level"], BANNER_TXT[q["level"]])[0], f"{n}_banner")
        prev = q["level"]
        QUESTIONS.append(d)


def dur(name):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                          os.path.join(VOICE_DIR, name + ".wav")], capture_output=True, text=True).stdout
    return float(out)


def up(x, step):
    return math.ceil(x / step - 1e-6) * step


def _build():
    voices = []   # (start, name)
    sfx = []      # (start, kind)
    qs = []
    cta = None
    t = 0.0
    last_voice_end = 0.0

    def say(name, at):
        nonlocal last_voice_end
        start = max(at, last_voice_end + 0.04)
        voices.append((round(start, 3), name))
        last_voice_end = start + dur(name)
        return start, last_voice_end

    sfx.append((0.0, "whoosh"))
    # Accroche dite PENDANT la question 1
    say(V_ACCROCHE, 0.0)

    for i, q in enumerate(QUESTIONS):
        A = t
        sfx.append((A, "pop"))
        banner = q.get("banner")
        cd_start = A + 0.2
        if banner:
            sfx.append((A, "impact" if q["level"] == "EXTREME" else "levelup"))
            say(banner[1], A)
            cd_start += 0.5
        if q["vq"]:
            say(q["vq"], A)
        # Compte à rebours 5-4-3-2-1 puis 0 = révélation immédiate (CD_STEP s par chiffre)
        cd_start = max(cd_start, last_voice_end + 0.8 - 5 * CD_STEP)
        cd_start = up(cd_start, 0.05)
        cd_end = cd_start + 5 * CD_STEP
        R = cd_end
        susp = None
        if q.get("suspense"):
            # suspense DANS le compte à rebours : musique coupée sur le « 1 », chuchotement, puis 0 = réponse
            susp = (cd_end - CD_STEP, cd_end)
            sfx.append((cd_end - CD_STEP, "cut"))
            w = dur("19_suspense")
            say("19_suspense", max(last_voice_end + 0.05, cd_end - w - 0.08))
        sfx.append((R, "ding"))
        rs, re_ = say(q["vr"], R)
        # la question suivante enchaîne dès que la réponse est inscrite (fin de voix - 0,3 s, grille 1/4 de temps)
        nxt = max(R + 0.8, re_ - 0.3)
        nxt = up(nxt - 1e-9, 0.25)
        qs.append(dict(q, idx=i, appear=A, cd_start=cd_start, cd_end=cd_end, reveal=R, end=nxt,
                       suspense=susp, banner_t=(A, A + 0.5) if banner else None))
        t = nxt
        if i == CTA_AFTER and os.path.exists(os.path.join(VOICE_DIR, V_CTA + ".wav")):
            # appel « abonne-toi + like » juste avant la question 4, puis enchaînement immédiat
            sfx.append((t, "pop"))
            cs, ce = say(V_CTA, t + 0.05)
            sfx.append((t + 0.95, "pop")); sfx.append((t + 1.45, "ding"))
            cta = (t, up(ce + 0.05, 0.25))
            t = cta[1]

    concl = t
    say(V_CONCL, concl + 0.05)
    end = max(concl + 2.0, last_voice_end + 0.35)
    end = up(end, 0.25)
    sfx.append((end - 1.0, "jingle"))
    return dict(questions=qs, voices=voices, sfx=sfx, conclusion=concl, duration=end, fps=FPS, cta=cta, meta=META)


MIN_DUR = float(os.environ.get("MIN_DUR", "62"))  # TikTok ne rémunère que les vidéos > 1 min


def build():
    """Construit la timeline ; ralentit le compte à rebours si besoin pour dépasser MIN_DUR."""
    global CD_STEP
    base = CD_STEP
    tl = _build()
    while tl["duration"] < MIN_DUR and CD_STEP < 1.3:
        CD_STEP = round(CD_STEP + 0.01, 3)
        tl = _build()
    tl["cd_step"] = CD_STEP
    CD_STEP = base
    return tl


if __name__ == "__main__":
    tl = build()
    json.dump(tl, open(os.path.join(ROOT, "build", "timeline.json"), "w"), ensure_ascii=False, indent=1)
    for q in tl["questions"]:
        print(f"Q{q['idx']+1:<2} {q['level']:<9} apparition {q['appear']:5.2f}  rebours {q['cd_start']:5.2f}->{q['cd_end']:5.2f}"
              f"  révélation {q['reveal']:5.2f}  fin {q['end']:5.2f}  ({q['end']-q['appear']:.2f} s)")
    print("conclusion", tl["conclusion"], "durée totale", tl["duration"])
    for v in tl["voices"]:
        print(f"  voix {v[0]:6.2f} {v[1]}  (→ {v[0]+dur(v[1]):.2f})")
