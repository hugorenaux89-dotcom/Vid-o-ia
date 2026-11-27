"""Timeline du quiz : calculée à partir des vraies durées des voix (fichiers rognés)."""
import json, math, os, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOICE_DIR = os.path.join(ROOT, "assets", "voice", "trimmed")
FPS = 30
BEAT = 0.5  # 120 BPM

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
         banner=("NIVEAU EXTRÊME !", "18_niveau_extreme"), suspense=True),
    dict(flag="Chad", short="Tchad", big="TCHAD", level="EXTREME", vq="21_Q10_question", vr="22_Q10_reponse",
         suspense=True, qtext="INDICE : CE N'EST\nPAS LA ROUMANIE !"),
]


def dur(name):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                          os.path.join(VOICE_DIR, name + ".wav")], capture_output=True, text=True).stdout
    return float(out)


def up(x, step):
    return math.ceil(x / step - 1e-6) * step


def build():
    voices = []   # (start, name)
    sfx = []      # (start, kind)
    qs = []
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
    say("01_accroche", 0.0)

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
        # Compte à rebours : 3 s minimum, et au moins 0,9 s de réflexion après la fin de la voix
        cd_end = max(cd_start + 3.0, last_voice_end + 0.8)
        cd_end = up(cd_end, 0.25)
        R = cd_end
        susp = None
        if q.get("suspense"):
            susp = (cd_end, cd_end + 1.0)
            sfx.append((cd_end, "cut"))
            # le chuchotement démarre 0,05 s après la coupure
            last_voice_end = min(last_voice_end, cd_end)
            say("19_suspense", cd_end + 0.05)
            R = cd_end + 1.0
        sfx.append((R, "ding"))
        rs, re_ = say(q["vr"], R)
        # la question suivante enchaîne dès que la réponse est inscrite (fin de voix - 0,3 s, grille 1/4 de temps)
        nxt = max(R + 0.8, re_ - 0.3)
        nxt = up(nxt - 1e-9, 0.25)
        qs.append(dict(q, idx=i, appear=A, cd_start=cd_start, cd_end=cd_end, reveal=R, end=nxt,
                       suspense=susp, banner_t=(A, A + 0.5) if banner else None))
        t = nxt

    concl = t
    say("23_conclusion", concl + 0.05)
    end = max(concl + 2.0, last_voice_end + 0.35)
    end = up(end, 0.25)
    sfx.append((end - 1.0, "jingle"))
    return dict(questions=qs, voices=voices, sfx=sfx, conclusion=concl, duration=end, fps=FPS)


if __name__ == "__main__":
    tl = build()
    json.dump(tl, open(os.path.join(ROOT, "build", "timeline.json"), "w"), ensure_ascii=False, indent=1)
    for q in tl["questions"]:
        print(f"Q{q['idx']+1:<2} {q['level']:<9} apparition {q['appear']:5.2f}  rebours {q['cd_start']:5.2f}->{q['cd_end']:5.2f}"
              f"  révélation {q['reveal']:5.2f}  fin {q['end']:5.2f}  ({q['end']-q['appear']:.2f} s)")
    print("conclusion", tl["conclusion"], "durée totale", tl["duration"])
    for v in tl["voices"]:
        print(f"  voix {v[0]:6.2f} {v[1]}  (→ {v[0]+dur(v[1]):.2f})")
