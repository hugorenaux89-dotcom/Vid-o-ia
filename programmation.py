"""Prépare les données de programmation Metricool (TikTok + YouTube Shorts) d'un épisode,
à la suite des 100 premiers épisodes (déjà programmés : 3 par jour à 8h, 13h et 18h,
le n°100 le 28/12/2026 à 18h).

Usage : python3 programmation.py 101   -> affiche le JSON des deux publications
"""
import datetime
import json
import re
import sys

BRANCHE = "claude/friendly-gauss-wbccao"
DEPOT = "hugorenaux89-dotcom/Vid-o-ia"
HEURES = ["08:00:00", "13:00:00", "18:00:00"]
DEBUT = datetime.date(2026, 12, 29)  # jour de l'épisode 101


def date(n):
    k = n - 101
    return f"{DEBUT + datetime.timedelta(days=k // 3)}T{HEURES[k % 3]}"


def legende(n):
    t = open(f"episodes/episode{n}_publication.txt", encoding="utf-8").read()
    lignes = t.split("DESCRIPTION :\n", 1)[1].strip().split("\n")
    return lignes[0], lignes[1]


def posts(n):
    l1, l2 = legende(n)
    url = f"https://raw.githubusercontent.com/{DEPOT}/{BRANCHE}/sortie/episode{n}.mp4"
    d = date(n)
    base = {"autoPublish": True, "descendants": [], "draft": False, "firstCommentText": "",
            "hasNotReadNotes": False, "media": [url], "mediaAltText": [], "shortener": False,
            "smartLinkData": {"ids": []}, "publicationDate": {"dateTime": d, "timezone": "Europe/Paris"}}
    tiktok = dict(base, providers=[{"network": "tiktok"}],
                  text=f"{l1}\n{l2}\n\n#quiz #culturegenerale #quizfr #testtonniveau #question #apprendre #savaistu #fyp #pourtoi #defi #episode{n}",
                  tiktokData={"privacyOption": "PUBLIC_TO_EVERYONE", "title": f"Quiz culture G • épisode {n}",
                              "isAigc": True, "disableComment": False, "disableDuet": False, "disableStitch": False,
                              "autoAddMusic": False})
    youtube = dict(base, providers=[{"network": "youtube"}],
                   text=f"{l1}\n{l2}\n\n#quiz #culturegenerale #quizfr #shorts",
                   youtubeData={"title": f"Quiz culture G • épisode {n} 😱 #shorts", "type": "short",
                                "privacy": "public", "tags": ["quiz", "culture générale", "quiz fr", "test"],
                                "category": "EDUCATION", "madeForKids": False, "isAiGeneratedContent": True})
    return {"date": d + "+01:00", "tiktok": tiktok, "youtube": youtube}


if __name__ == "__main__":
    print(json.dumps(posts(int(sys.argv[1])), ensure_ascii=False))
