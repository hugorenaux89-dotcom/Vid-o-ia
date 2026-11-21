"""Construit les fichiers des épisodes 2 à 50 (JSON vidéo + description TikTok) à partir de
episodes/saison1_questions.py, et met à jour la fin de l'épisode 1.

Usage : python3 creer_saison.py
"""
import json
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ICI, "episodes"))
from saison1_questions import E  # noqa: E402
from saison2_questions import E as E2  # noqa: E402

E.update(E2)

J, B, V = [255, 214, 0], [255, 255, 255], [34, 197, 94]

ACCROCHES = [
    ("😱", [["Presque personne", 90, J], ["n'a 10/10", 90, B], ["à ce quiz...", 76, B], ["Et toi ?", 110, J]],
     "Presque personne n'a dix sur dix à ce quiz... Et toi ?"),
    ("🧠", [["Seuls les", 80, B], ["vrais génies", 96, J], ["ont 10/10", 90, B], ["Prouve-le !", 100, J]],
     "Seuls les vrais génies ont dix sur dix. Prouve-le !"),
    ("🔥", [["La dernière", 90, J], ["question va", 80, B], ["te piéger...", 80, B], ["Tu paries ?", 100, J]],
     "La dernière question va te piéger... Tu paries ?"),
    ("🤔", [["Tu te crois", 90, B], ["cultivé ?", 100, J], ["On va", 80, B], ["vérifier !", 100, J]],
     "Tu te crois cultivé ? On va vérifier !"),
    ("⚡", [["10 questions", 96, J], ["de plus en", 80, B], ["plus dures...", 80, B], ["T'es prêt ?", 100, J]],
     "Dix questions, de plus en plus dures... T'es prêt ?"),
    ("😏", [["Si tu fais", 86, B], ["10/10,", 110, J], ["t'es un", 86, B], ["génie !", 110, J]],
     "Si tu fais dix sur dix... t'es un génie."),
]

REGLES = {"emoji": "📝", "lignes": [["Compte tes points", 84, B], ["et écris ton score", 76, J], ["en commentaire !", 76, J]],
          "voix": "Allez, compte tes points. C'est parti !", "ton": "energique"}

RELANCES_5 = [
    ("🔥", [["Mi-temps !", 100, J], ["T'as tout bon ?", 72, B], ["Accroche-toi...", 72, B]],
     "Mi-temps ! T'as tout bon ? Accroche-toi... la suite est plus dure."),
    ("😬", [["5/5 ?", 110, J], ["Pas mal !", 76, B], ["Mais ça se corse...", 68, B]],
     "Cinq sur cinq ? Pas mal ! Mais attention... ça se corse."),
    ("💪", [["Toujours là ?", 96, J], ["La suite est", 72, B], ["plus difficile !", 72, B]],
     "Toujours là ? Bravo. Mais la suite... est plus difficile."),
]

RELANCES_9 = [
    ("😱", [["DERNIÈRE QUESTION", 86, J], ["Presque personne", 75, B], ["ne la trouve...", 75, B]],
     "Bon... dernière question. Et celle-là, presque personne la trouve."),
    ("🎯", [["DERNIÈRE QUESTION", 86, J], ["La plus dure", 75, B], ["de l'épisode...", 75, B]],
     "Dernière question... et c'est la plus dure de l'épisode."),
    ("👀", [["DERNIÈRE QUESTION", 86, J], ["Concentre-toi", 75, B], ["bien...", 75, B]],
     "Attention... dernière question. Concentre-toi bien."),
]

FIN = {
    "emoji": "🏆",
    "lignes": [["TON SCORE ?", 96, J], ["0-4 : débutant", 56, B], ["5-7 : solide", 56, B], ["8-9 : très fort", 56, B],
               ["10 : GÉNIE", 66, V], ["Abonne-toi pour voir", 54, J], ["les prochains épisodes !", 54, J],
               ["3 nouveaux quiz par jour", 50, V]],
    "voix": "Alors, t'as eu combien ? Dis-le en commentaire... et abonne-toi pour voir les prochains épisodes. Y'en a trois nouveaux chaque jour !",
    "ton": "chaleureux", "min": 3.5,
}

LEGENDES = [
    "Épisode {n} 🧠 Presque personne n'a 10/10... et toi ? Ton score en commentaire 👇",
    "Quiz culture G • épisode {n} 🔥 La dernière question est un vrai piège 😱 T'as eu combien ? 👇",
    "Épisode {n} ⚡ 10 questions, de plus en plus dures. Tu tiens jusqu'au bout ? 👇",
    "Tu te crois cultivé ? 🤔 Épisode {n} : prouve-le en commentaire 👇",
    "Épisode {n} 😏 Si tu fais 10/10, t'es un génie. Dis-nous ton score 👇",
]
HASHTAGS = "#quiz #culturegenerale #quizfr #testtonniveau #question #apprendre #savaistu #fyp #pourtoi #defi"


def ton_reponse(voix):
    return "malicieux" if any(m in voix for m in ("Pas ", "pas ", "Et non", "Eh non")) else "triomphant"


def episode(n, questions):
    em, lignes, voix = ACCROCHES[(n - 2) % len(ACCROCHES)]
    r5, r9 = RELANCES_5[n % 3], RELANCES_9[n % 3]
    qs = []
    for k, (emo, q, choix, rep, bonus, vr) in enumerate(questions):
        item = {"emoji": emo, "question": q, "choix": choix, "reponse": rep, "bonus": bonus,
                "voix_reponse": vr, "ton_question": "suspense" if k == 9 else "curieux", "ton_reponse": ton_reponse(vr)}
        if k == 9:
            item["compte"] = 4
        qs.append(item)
    return {
        "titre": f"QUIZ CULTURE GÉ • ÉPISODE {n}",
        "hook": {"emoji": em, "lignes": lignes, "voix": voix, "ton": "mysterieux", "min": 2.5},
        "regles": REGLES,
        "relances": {
            "5": {"emoji": r5[0], "lignes": r5[1], "voix": r5[2], "ton": "malicieux"},
            "9": {"emoji": r9[0], "lignes": r9[1], "voix": r9[2], "ton": "suspense"},
        },
        "questions": qs,
        "fin": FIN,
    }


def publication(n):
    return (f"ÉPISODE {n} – À COPIER AU MOMENT DE PUBLIER\n\n"
            f"DESCRIPTION :\n{LEGENDES[(n - 1) % len(LEGENDES)].format(n=n)}\n"
            f"3 nouveaux quiz chaque jour : abonne-toi pour ne rien rater ⚡\n\n{HASHTAGS} #episode{n}\n")


def verifier():
    vus = {}
    erreurs = []
    for n, qs in sorted(E.items()):
        if len(qs) != 10:
            erreurs.append(f"épisode {n} : {len(qs)} questions")
        for emo, q, choix, rep, bonus, vr in qs:
            if len(choix) != 4 or not 0 <= rep < 4 or len(set(choix)) != 4:
                erreurs.append(f"épisode {n} : choix invalides pour « {q} »")
            if q.lower() in vus:
                erreurs.append(f"doublon : « {q} » (épisodes {vus[q.lower()]} et {n})")
            vus[q.lower()] = n
    return erreurs


if __name__ == "__main__":
    err = verifier()
    if err:
        print("\n".join(err))
        sys.exit(1)
    dossier = os.path.join(ICI, "episodes")
    toutes = []
    for n, qs in sorted(E.items()):
        with open(os.path.join(dossier, f"episode{n}.json"), "w", encoding="utf-8") as f:
            json.dump(episode(n, qs), f, ensure_ascii=False, indent=1)
        pub = publication(n)
        with open(os.path.join(dossier, f"episode{n}_publication.txt"), "w", encoding="utf-8") as f:
            f.write(pub)
        toutes.append(pub)

    # Épisode 1 : même fin « abonne-toi pour voir les prochains épisodes »
    p1 = os.path.join(dossier, "episode1.json")
    ep1 = json.load(open(p1, encoding="utf-8"))
    ep1["fin"] = FIN
    json.dump(ep1, open(p1, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    pub1 = open(os.path.join(dossier, "episode1_publication.txt"), encoding="utf-8").read()

    with open(os.path.join(ICI, "DESCRIPTIONS_TIKTOK.txt"), "w", encoding="utf-8") as f:
        f.write("DESCRIPTIONS DES ÉPISODES (à copier sous chaque vidéo TikTok)\n" + "=" * 60 + "\n\n")
        f.write(pub1 + "\n" + "-" * 60 + "\n\n")
        f.write(("\n" + "-" * 60 + "\n\n").join(toutes))
    import datetime
    debut = datetime.date(2026, 11, 22)
    heures = ["12h30", "18h00", "21h00"]
    jours = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    with open(os.path.join(ICI, "PLANNING_PUBLICATION.txt"), "w", encoding="utf-8") as f:
        f.write("PLANNING : 3 ÉPISODES PAR JOUR (12h30, 18h00, 21h00)\n" + "=" * 52 + "\n")
        for n in range(1, max(E) + 1):
            j = (n - 1) // 3
            d = debut + datetime.timedelta(days=j)
            if (n - 1) % 3 == 0:
                f.write(f"\nJour {j + 1} – {jours[d.weekday()]} {d.day:02d}/{d.month:02d}/{d.year}\n")
            f.write(f"  {heures[(n - 1) % 3]}  →  épisode {n}  (sortie/episode{n}.mp4)\n")
    print(f"OK : {len(E)} épisodes créés + épisode 1 mis à jour + planning")
