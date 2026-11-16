"""Write CREDITS.md (photo attributions required by CC BY / CC BY-SA) from
assets/photos/credits.json, plus a short caption ready to paste under the post."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    with open(os.path.join(ROOT, "assets", "photos", "credits.json")) as f:
        credits = json.load(f)
    lines = [
        "# Crédits",
        "",
        "## Photos (Wikimedia Commons)",
        "",
        "Toutes les photos sont sous licence libre. La vidéo, qui les adapte "
        "(recadrage, étalonnage, effets), est publiée sous **CC BY-SA 4.0**.",
        "",
        "| Plan | Auteur | Licence | Source |",
        "|---|---|---|---|",
    ]
    short = []
    for c in credits:
        author = " ".join(c["author"].split()) or "inconnu"
        lines.append(f"| `{c['key']}` | {author} | {c['license']} | [{c['title'][5:]}]({c['source']}) |")
        short.append(author)
    lines += [
        "",
        "## Musique et sons",
        "",
        "- Musique : composition originale générée par code (`edit/music.py`), aucun sample.",
        "- Effets sonores (sifflet, foule, impact, whoosh, frappe) : générés avec ElevenLabs.",
        "",
        "## Polices",
        "",
        "Anton, Bebas Neue, Instrument Serif : SIL Open Font License (Google Fonts).",
        "",
    ]
    with open(os.path.join(ROOT, "CREDITS.md"), "w") as f:
        f.write("\n".join(lines))

    authors = sorted(set(a for a in short if a))
    caption = (
        "KYLIAN MBAPPÉ 🇫🇷⚡ #mbappe #edit #football #phonk #francefootball #realmadrid\n\n"
        "Photos : Wikimedia Commons — " + ", ".join(authors) +
        " (CC BY / CC BY-SA). Musique originale. Vidéo sous licence CC BY-SA 4.0.\n"
    )
    with open(os.path.join(ROOT, "output", "description.txt"), "w") as f:
        f.write(caption)
    print(caption)


if __name__ == "__main__":
    main()
