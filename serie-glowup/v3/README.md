# ✨ « Yanis a 30 jours » — Glow-up v3 (format type Kévin, notre histoire)

> **Yanis a 30 jours avant le mariage de son cousin, où son ex Sarah viendra avec son nouveau copain. Chaque jour, c'est TOI qui choisis ce qui change chez lui. Et chaque changement reste pour toujours.**

## Le format
- **Durée :** entre **1 min 02 et 1 min 17** par vidéo, soit environ 230 à 260 mots de voix off lue en continu, **sans aucun blanc**.
- **Voix off :** elle raconte la vie de Yanis à la troisième personne, sur un ton rapide, drôle et plein d'accroches. **Yanis ne parle jamais.**
- **À l'écran :**
  - en haut, **un gros titre** qui change à chaque plan (lettres blanches, mot clé en rouge) ;
  - au centre, **Yanis en grand**, dans un décor détaillé, avec une animation à chaque plan ;
  - en bas, **un bandeau** : `JOUR 7 · VOUS AVEZ CHOISI CHEVEUX` ;
  - les sous-titres de la voix off, mot à mot, au-dessus du bandeau.
- **Le vote :** chaque épisode se termine par « **Commente UN mot : X ou Y** ». Le mot gagnant est réglé dans l'épisode suivant (c'est nous qui décidons). L'autre revient plus tard.
- **Pas de bips, pas de minuteur, pas de plan figé :** chaque plan dure le temps de sa phrase.

## Format d'un plan
```
**P3 · Titre**
🎥 `prompt de l'image`
🎭 `expression · pose`
🔠 `GROS TITRE EN HAUT`        (le mot entre *étoiles* s'affiche en rouge)
🎙️ **VOIX OFF** : « texte lu »
📝 `carte à l'écran`           (optionnel)
```

## Ce qui change chaque jour (vote du public)
| Jour | Changement | Jour | Changement | Jour | Changement |
|---|---|---|---|---|---|
| 1 | 2 L d'eau | 11 | Dents blanches | 21 | Danse |
| 2 | Odeur (douche + déo) | 12 | Barbe (bouc + moustache) | 22 | Cuisine |
| 3 | Baskets de running | 13 | Coupe (dégradé + boucles) | 23 | Montre de son père |
| 4 | Frigo sain | 14 | Sourcils | 24 | Costume |
| 5 | Lunettes | 15 | Posture | 25 | Discours |
| 6 | Dents (détartrage) | 16 | Ongles | 26 | Chaussures |
| 7 | Cheveux (en 6 secondes) | 17 | Parfum | 27 | Cadeau + 10 km |
| 8 | Boutons (routine) | 18 | Chambre | 28 | La vérité à Kenzo |
| 9 | Sommeil | 19 | Style | 29 | Entrée de star |
| 10 | Peau (plus aucun bouton) | 20 | Confiance (< 100 kg) | 30 | Le mariage |

**Sport :** muscu → repos → course, de 3 km à 10 km/h (jour 3) jusqu'à 10 km à 12 km/h (jour 27). **Poids :** 112 kg → 95 kg.
**Fin de chaque épisode :** « Demain, qu'est-ce qu'on améliore : X… ou Y ? Écris-le en commentaire ! »
**Apparence :** elle évolue automatiquement jour après jour (`outils/viz/look.js`).

## L'apparence de Yanis (raccourcis pour les prompts)
- **{YANIS_A}** (jours 1 à 6) : `full body, 24-year-old very overweight North African young man, big round fat face with a double chin, BALD on top with a shiny scalp and a few thin hairs on the sides, BROKEN black glasses taped in the middle with one cracked lens, dirty yellow teeth, badly shaved patchy beard with razor cuts, almost-joined eyebrows, red pimples, big belly UNDER a too-tight stained grey t-shirt with sweat marks, dirty grey joggers, worn-out sneakers`
- **{YANIS_B}** (jours 7 à 13) : `full body, chubby North African young man, round face, NEW clean black glasses, THICK dark hair grown back (messy, not styled yet), fewer pimples, cleaner teeth, patchy beard, belly under a clean grey t-shirt, new running shoes`
- **{YANIS_C}** (jours 14 à 19) : `full body, slimmer face, sharp skin fade haircut with a textured top, clean short beard, clear skin, white teeth, stylish black glasses, fitted black t-shirt, smaller belly`
- **{YANIS_D}** (jours 20 à 26) : `full body, handsome athletic man, perfect fade, perfect short beard, glowing skin, thin glasses, navy knit polo, beige chino, white sneakers, his late father's vintage watch`
- **{YANIS_E}** (jours 27 à 30) : `full body, very handsome athletic man, sharp jawline, perfect hair and beard, flawless skin, elegant thin glasses, tailored navy suit, polished shoes`

**Nouveau décor :** **{MEDECIN}** : `a bright doctor's office, white and mint walls, an examination table with paper, a poster of a smiling tooth and a hair diagram, a window on a hallway, white tiled floor`

**Style des prompts :** `2D cartoon illustration, thick clean outlines, flat colors with soft shading, character large in the center, detailed background, vertical 9:16, sharp and clean.`

👉 Épisodes : [`episodes-01-03.md`](./episodes-01-03.md) · [`episodes-04-12.md`](./episodes-04-12.md) · [`episodes-13-21.md`](./episodes-13-21.md) · [`episodes-22-30.md`](./episodes-22-30.md)

👉 Descriptions TikTok : [`descriptions.md`](./descriptions.md) (et `videos/epXX-description.txt` à côté de chaque vidéo)
