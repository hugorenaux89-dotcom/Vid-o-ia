# Épisode 1 — « Dans 6 mois, tu pourrais être méconnaissable. »

**Vidéo finale :** `output/ep01.mp4` (44,9 s · 1080×1920 · 30 i/s · H.264 12 Mb/s · AAC · −14 LUFS)
**Sous-titres :** `output/ep01.srt` (déjà incrustés dans la vidéo, fichier fourni pour CapCut / TikTok)

---

## 1. Titre accrocheur

**Dans 6 mois, tu pourrais être méconnaissable.**
(Texte à l'écran dès la 1re image : « DANS 6 MOIS » ; pas de logo, pas d'intro.)

## 2. Script complet de la voix off

> Dans six mois… tu pourrais être **méconnaissable**.
>
> Tu te dis que tu commenceras **lundi**. Puis lundi devient le mois prochain. Et le mois prochain… devient **jamais**.
>
> Tu n'es pas **paresseux**. Tu as juste **peur** de commencer **petit**.
>
> Une séance ne change **rien**. Un réveil à cinq heures ne change **rien**.
>
> Mais cent quatre-vingts jours… ça change **tout**.
>
> Cent quatre-vingts **matins** où tu te lèves. Cent quatre-vingts fois où tu refuses d'**abandonner**.
>
> Personne ne verra le **travail**. Tout le monde verra le **résultat**.
>
> Alors commence **aujourd'hui**. Pas **parfait**. Juste aujourd'hui.
>
> Et dans six mois, quand on te demandera : « Qu'est-ce qui t'est arrivé ? »… tu répondras simplement : « J'ai **commencé**. »

Voix : ElevenLabs « Adam » (grave, ferme), modèle multilingual v2, stabilité 0,42, style 0,35.
Montage voix : silences resserrés à 0,20 s (0,45 s avant les phrases clés), tempo ×1,06.
(La phrase « Mais écoute bien » présente dans `voiceover.txt` a été coupée au montage pour tenir sous 45 s.)

## 3. Scènes visuelles seconde par seconde

La version livrée utilise des **fonds cinématographiques générés** (dégradés, bokeh, faisceaux, silhouettes,
lever de soleil) pour rester 100 % originale et publiable tout de suite. Chaque scène a en plus un **plan réel
cible** + un **prompt vidéo IA** : dépose le clip dans `clips/` sous le nom indiqué et relance
`python3 tools/build_episode.py episodes/ep01` — il remplace le fond automatiquement.

| Temps | Partie | Voix | Version livrée (fond généré) | Plan réel cible → fichier | Prompt vidéo IA (Kling / Runway / Veo / Sora) |
|---|---|---|---|---|---|
| 0,0–3,6 | **ACCROCHE** | Dans six mois… tu pourrais être méconnaissable. | Nuit bleue, lumières de ville floues, « 6 MOIS » géant en fantôme | Jeune homme qui court seul dans une rue vide à 5 h, lampadaires → `s01_runner_5am.mp4` | *Cinematic vertical shot, young man running alone on an empty city street at 5am, dark blue hour, wet asphalt reflecting streetlights, breath visible, shallow depth of field, slow motion, anamorphic, film grain, 9:16* |
| 3,6–5,9 | IDENTIFICATION | Tu te dis que tu commenceras lundi. | Pièce sombre, néon qui vacille, « LUNDI » | Main qui appuie sur « snooze », chambre sombre → `s02_alarm_snooze.mp4` | *Close-up of a hand pressing snooze on a glowing phone alarm in a dark bedroom, moody, cold light, cinematic, 9:16* |
| 5,9–8,3 | IDENTIFICATION | Puis lundi devient le mois prochain. | Idem, « LE MOIS PROCHAIN » | Pages de calendrier qui tournent / jours barrés → `s03_calendar.mp4` | *Macro shot of calendar pages flipping fast, days crossed out, dim desk lamp, dust in the light, cinematic, 9:16* |
| 8,3–11,2 | IDENTIFICATION | Et le mois prochain… devient jamais. | Noir total, « JAMAIS » rouge sombre | Jeune homme allongé, visage éclairé par son téléphone → `s04_bed_dark.mp4` | *Young man lying in bed at night, face lit only by phone screen, empty expression, very dark, cinematic, slow push-in, 9:16* |
| 11,2–14,7 | IDENTIFICATION | Tu n'es pas paresseux. Tu as juste peur de commencer petit. | Faisceau vertical froid (lumière de miroir) | Reflet dans un miroir de salle de bain, regard qui doute → `s05_mirror.mp4` | *Man looking at his reflection in a bathroom mirror, single cold light above, doubtful eyes, shallow focus, cinematic, 9:16* |
| 14,7–16,6 | **DÉCLIC** | Une séance ne change rien. | Salle sombre, cône de lumière, poussière, « 1 SÉANCE » | Personne seule dans une salle de muscu sous un spot → `s07_gym_alone.mp4` | *Lone athlete training in an empty dark gym under a single overhead spotlight, dust particles, chalk, cinematic slow motion, 9:16* |
| 16,6–19,2 | DÉCLIC | Un réveil à cinq heures ne change rien. | « 05:00 » rouge digital | Réveil qui affiche 05:00 → `s08_alarm_5am.mp4` | *Digital alarm clock showing 05:00 glowing red in a dark room, then a hand turns it off, cinematic, 9:16* |
| 19,2–21,4 | DÉCLIC (montée) | Mais cent quatre-vingts jours… | **Compteur or « JOUR 001 → 180 »** qui accélère + riser | Timelapse jour/nuit qui défile → `s09_timelapse.mp4` | *Fast timelapse of days and nights passing over a city skyline, clouds racing, sun arcs, cinematic, 9:16* |
| **21,4** | **CLIMAX — DROP** | **ça change tout.** | **Flash blanc + tremblement + impact**, lever de soleil derrière les montagnes, rayons | Lever de soleil explosif depuis un sommet → `s10_sunrise_peak.mp4` | *Epic sunrise bursting over mountain ridge, sun rays, lens flare, golden light flooding the frame, drone shot, 9:16* |
| 22,6–25,5 | CLIMAX | Cent quatre-vingts matins où tu te lèves. | Soleil qui monte, silhouettes de montagnes | Coureur en contre-jour au lever du soleil → `s11_runner_sunrise.mp4` | *Silhouette of a runner sprinting toward the rising sun on a ridge path, golden hour, slow motion, epic, 9:16* |
| 25,5–28,4 | CLIMAX | Cent quatre-vingts fois où tu refuses d'abandonner. | Salle, cône de lumière | Dernière répétition, visage qui serre les dents → `s12_last_rep.mp4` | *Close-up of an exhausted athlete pushing through the last rep, sweat, gritted teeth, dramatic side light, slow motion, 9:16* |
| 28,4–30,5 | CLIMAX | Personne ne verra le travail. | Nuit bleue, lumières floues | Entrepreneur seul tard le soir devant son écran → `s13_entrepreneur_night.mp4` | *Young entrepreneur working late alone at a desk, laptop light on his face, city lights behind the window, cinematic, 9:16* |
| 30,5–32,7 | CLIMAX | Tout le monde verra le résultat. | Lever de soleil plein | Transformation : silhouette avant/après, même cadrage → `s14_transformation.mp4` | *Same man, same framing, morphing from tired and slouched to confident and fit, golden light, cinematic match cut, 9:16* |
| 32,7–36,9 | **CONCLUSION** | Alors commence aujourd'hui. Pas parfait. Juste aujourd'hui. | Toit-terrasse, skyline, ciel violet → orange | Personne qui regarde la ville depuis un toit à l'aube → `s15_rooftop_city.mp4` | *Man standing on a rooftop at dawn looking over a big city, back to camera, wind, purple-orange sky, cinematic wide shot, 9:16* |
| 36,9–38,3 | CONCLUSION | Et dans six mois, | Toit-terrasse | Reflet dans le même miroir qu'en 11 s, mais regard assuré → `s16_mirror_after.mp4` | *Same bathroom mirror, same man, now confident posture, warm morning light, slight smile, 9:16* |
| 38,3–42,5 | CONCLUSION | quand on te demandera : « Qu'est-ce qui t'est arrivé ? »… tu répondras simplement : | Nuit, « ? » fantôme | Un ami qui le regarde, surpris → `s16b_friend_question.mp4` | *Friend looking surprised and impressed at someone off-screen, street at golden hour, natural, cinematic, 9:16* |
| 42,5–44,9 | **CHUTE + FIN** | « J'ai commencé. » | **Musique coupée** sur la phrase, puis impact final + carton « 5H01 — L'heure où tout commence. Épisode 1 / 30 » | Léger sourire, plan serré, soleil derrière → `s17_final_smile.mp4` | *Close-up of a calm confident young man, slight smile, sunrise behind him, lens flare, cinematic, 9:16* |

## 4. Instructions de montage (appliquées automatiquement)

- **Aucune intro, aucun logo** : texte « DANS 6 MOIS » visible dès l'image 1. Filigrane « 5H01 » seulement après 3 s.
- **Coupe à chaque phrase** (17 plans en 45 s, un toutes les 2–3 s), plus rapides dans le climax.
- **Punch-in** de 6 % à chaque coupe puis **zoom lent** de 4,5 % sur la durée du plan.
- **Whoosh discret** sur chaque coupe ; **riser 4 s → impact + flash blanc + tremblement** au drop (21,4 s).
- **Compteur JOUR 001 → 180** qui accélère pendant « Mais cent quatre-vingts jours… » (le visuel signature de la chaîne).
- **Musique qui s'arrête net** sur « J'ai commencé. » (silence = maximum d'impact), puis impact final.
- **Grain argentique + vignette** sur toute la vidéo ; passage **nuit froide → aube dorée** au drop.
- **Barre de progression or** en haut : incite à rester jusqu'au bout.
- **Phrase finale qui renvoie à l'accroche** (« dans six mois ») → donne envie de revoir en boucle.

## 5. Musique

- **0 → 21,4 s :** ambiance sombre et émotionnelle — piano solo en la mineur sur nappe grave, pulsation type battement de cœur, tension qui monte.
- **21,4 → 42,5 s :** trailer épique hybride — grosses percussions, sub-basses, cordes qui s'envolent, toujours en la mineur.
- **Ducking** automatique : la musique baisse d'environ 5 dB sous la voix.
- Musique et bruitages générés avec ElevenLabs Sound Effects (`build/mus_*.mp3`, `build/sfx_*.mp3`).
  Alternative : un morceau « epic motivational / cinematic trailer » de la bibliothèque sonore commerciale de TikTok, en calant le drop sur « ça change tout ».

## 6. Sous-titres affichés

Style : Inter Display Black, MAJUSCULES, contour noir + ombre, 1 à 3 mots à la fois, **mots allumés au rythme de la voix** (karaoké), mots-clés en **or**, petit « pop » à l'apparition, centrés à 60 % de la hauteur (hors zone d'interface TikTok). Chiffres en chiffres : 6, 180, 5H.

```
DANS 6 MOIS / TU POURRAIS ÊTRE / MÉCONNAISSABLE
TU TE DIS / QUE TU COMMENCERAS / LUNDI
PUIS LUNDI DEVIENT / LE MOIS PROCHAIN / ET LE MOIS / PROCHAIN / DEVIENT JAMAIS
TU N'ES PAS / PARESSEUX / TU AS JUSTE / PEUR DE COMMENCER / PETIT
UNE SÉANCE NE / CHANGE RIEN / UN RÉVEIL / À 5H NE / CHANGE RIEN
MAIS 180 JOURS / ÇA CHANGE TOUT
180 MATINS / OÙ TU TE / LÈVES …
… QU'EST-CE QUI T'EST ARRIVÉ ? / TU RÉPONDRAS SIMPLEMENT / J'AI COMMENCÉ
```
(Découpage exact et horodatage : `output/ep01.srt`.)

## 7. Description TikTok optimisée

```
Dans 6 mois, tu pourrais ne plus te reconnaître. Pas grâce à un miracle : grâce à 180 matins où tu décides de te lever. 🌅
Enregistre cette vidéo et regarde-la demain à 5h01.
Envoie-la à quelqu'un qui commence toujours « lundi ».
Épisode 1/30 : on fait les 180 jours ensemble. Abonne-toi pour le jour 2.
```

## 8. Cinq hashtags

`#motivation` `#discipline` `#developpementpersonnel` `#mindset` `#5h01`

## 9. Trois accroches alternatives à tester (A/B)

1. « Tu dis "lundi" depuis combien de temps ? »
2. « Il y a 180 jours, il était exactement comme toi. »
3. « Personne ne verra le travail. Tout le monde verra le résultat. » (en ouverture, puis on rembobine)

## 10. Conseils de publication

- Publier entre 6 h et 8 h ou entre 19 h et 22 h (heure de Paris) ; épingler un commentaire : « Jour 1. Qui commence aujourd'hui ? 👇 » pour lancer les réponses.
- Couverture : image à 21,5 s (« ÇA CHANGE TOUT » + lever de soleil).
- Tester les 3 accroches à 48 h d'intervalle et garder celle qui a le meilleur taux de visionnage à 3 s.
