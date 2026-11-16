# Vid-o-ia — Édit Kylian Mbappé

Édit vertical **1080×1920, 60 fps**, ~42 s, monté au battement près sur une musique phonk/montagem **originale**.

➡️ Vidéo finale : [`output/mbappe_edit.mp4`](output/mbappe_edit.mp4) · texte de description prêt à coller : [`output/description.txt`](output/description.txt)

## Ce qu'il y a dedans

Inspiré des codes des édits foot les plus vus (TikTok / Reels / Shorts) :

- **Hook immédiat** : coup de sifflet + « MBAPPÉ » géant placé *derrière* le joueur (détourage IA).
- **Intro ciné** : bandes noires, étalonnage sombre, histoire en 4 temps (2018 · 2022 · PSG · Real).
- **Montée** : zoom saccadé calé sur chaque coup du roulement de caisse claire, puis silhouette lumineuse dans le silence avant le drop.
- **Drops** : cut sur chaque kick, « velocity » (rapide → ralenti → rapide), punch-zoom, shake, flash, aberration chromatique, flou de mouvement radial, parallaxe 2.5D (joueur détaché du fond), bloom, grain.
- **Fin** : impact + foule, passage en noir et blanc, « la légende continue. ».

## Pipeline (tout est en code, reproductible)

```bash
pip install opencv-python-headless numpy scipy soundfile pillow "rembg[cpu]"
python3 edit/fetch_photos.py   # photos libres de droits (Wikimedia Commons) + crédits
python3 edit/music.py          # compose la musique (numpy) + beatmap.json
python3 edit/prep.py           # détourage joueur + fond reconstruit (parallaxe)
python3 edit/render.py         # rendu final -> output/mbappe_edit.mp4
python3 edit/credits.py        # CREDITS.md + output/description.txt
```

- `edit/timeline.py` : le montage (plans, textes, effets, étalonnage, SFX) — c'est ici qu'on change l'ordre des plans ou les textes.
- `edit/render.py --preview 9.3 12 26` : images fixes pour vérifier un moment précis.

## Droits

- Photos : Wikimedia Commons, CC BY / CC BY-SA — auteurs listés dans [`CREDITS.md`](CREDITS.md). La vidéo est donc publiée en **CC BY-SA 4.0** : garder la mention des crédits dans la description.
- Musique : composée par le script, aucun sample → pas de claim Content ID.
- Effets sonores : générés avec ElevenLabs.
