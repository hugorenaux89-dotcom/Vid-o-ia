"""Signale les questions qui ressemblent trop à une question déjà utilisée
(même bonne réponse + au moins 2 mots importants en commun, ou même question)."""
import json, re, sys, unicodedata, glob

VIDES = set("""le la les l un une des de du d à a au aux en et est sont quel quelle quels quelles
qui que quoi qu comment combien où ou dans sur par pour avec ce cet cette ces il elle on se s
y t ton ta tes son sa ses leur plus moins très tout tous ne pas n environ""".split())

def mots(t):
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return {m for m in re.findall(r"[a-z0-9]+", t) if m not in VIDES and (len(m) > 2 or m.isdigit())}

def charge():
    qs = []
    for p in sorted(glob.glob("episodes/episode*.json"), key=lambda x: int(re.findall(r"\d+", x)[0])):
        n = int(re.findall(r"\d+", p)[0])
        for q in json.load(open(p, encoding="utf-8"))["questions"]:
            qs.append((n, q["question"], q["choix"][q["reponse"]]))
    return qs

def verifier(premier):
    qs = charge()
    anciens = [q for q in qs if q[0] < premier]
    pb = []
    for n, q, r in [q for q in qs if q[0] >= premier]:
        mq, mr = mots(q), mots(r)
        for n2, q2, r2 in anciens + [x for x in qs if premier <= x[0] < n]:
            commun = mq & mots(q2)
            if q.lower() == q2.lower() or (mr and mr == mots(r2) and len(commun) >= 2):
                pb.append(f"ép.{n} « {q} » ({r})  ~  ép.{n2} « {q2} » ({r2})")
    return pb

if __name__ == "__main__":
    pb = verifier(int(sys.argv[1]) if len(sys.argv) > 1 else 101)
    print("\n".join(pb) if pb else "aucun doublon détecté")
    print(len(pb), "alerte(s)")
