# 🎬 Dossier de production — QUIZ DRAPEAUX #1

**Vidéos finales :** `output/quiz_drapeaux_voix_libre.mp4` (**voix gratuite maison**, 51,75 s, recommandée) et `output/quiz_drapeaux.mp4` (voix ElevenLabs « Charlie ») — 1080 × 1920, 30 i/s, H.264 + AAC 192 kb/s, **52,25 s**, ≈ −15,7 LUFS.

## 1. Paramètres
| Paramètre | Valeur |
|---|---|
| THÈME | Drapeaux du monde |
| FORMAT | standard (10 questions). **Durée réelle : 52,25 s**, au-dessus des ≈ 45 s visés, car les répliques de voix sont plus longues que prévu (voir §14). Reste sous 59 s. |
| NB_QUESTIONS | 10 (3 / 3 / 2 / 2) |
| MÉCANIQUE | n° 1 « Reconnaître l'image », avec un **piège à l'Extrême** (Tchad ≈ Roumanie) |
| PUBLIC | 13-25 ans et adultes curieux, tout public |
| CONTENU_ENFANTS_YOUTUBE | non (valeur par défaut) |
| VOICE_ID | `IKne3meq5aSn9XLyUdCD` (« Charlie », voix prédéfinie ElevenLabs, modèle `eleven_v3`, langue fr) — voir la remarque ci-dessous |

> ⚠️ **Voix :** ton compte ElevenLabs est en offre gratuite. L'API y refuse Voice Design (« paid plan only ») et les voix françaises de la bibliothèque. J'ai donc pris la voix prédéfinie la plus énergique (« Charlie »), avec `language_code: fr`. Toutes les répliques ont été retranscrites automatiquement (Scribe) en français correct, mais **je n'ai pas pu écouter l'accent**. ➜ À FAIRE PAR TOI : écoute-la. Si l'accent ne te convient pas, crée ta voix maison (§10 du prompt) sur une offre payante, puis relance `build/` avec ce nouveau VOICE_ID.

**Pourquoi les drapeaux ?** Thème universel et « commentable » (« trop facile ! », « jamais vu ce drapeau »). Les images sont libres (Wikimedia Commons) et justes à 100 %, ce qui supprime le risque d'une image fausse. Le piège Tchad/Roumanie de la Q10 est connu pour déclencher des débats en commentaires.

## Voix gratuite « maison » (version recommandée)
- **Moteur :** Piper (TTS neuronal libre, tourne en local, gratuit, sans compte, sans limite de caractères). Modèle `fr_FR-tom-medium` : voix masculine, français de France. Elle a été choisie après comparaison automatique de 127 voix françaises (hauteur, expressivité, transcription sans faute).
- **Ma « sculpture » de la voix** (`build/voice_claude.py`, analyse-resynthèse WORLD + mixage), réglée d'après le §10.1 :
  - *Jeune adulte, légèrement grave* : hauteur moyenne ramenée à 118 Hz (questions) et 128 Hz (réponses et réactions).
  - *Chaleureux* : formants abaissés de 4 % (timbre plus plein), +2,5 dB à 140 Hz, −2 dB à 350 Hz.
  - *Expressif et enthousiaste* : mélodie amplifiée ×1,25 sur les questions et ×1,5 sur les réponses (lissée pour éviter les tremblements), avec un élan montant sur les phrases longues.
  - *Articulation précise, son studio* : présence +4 dB à 3,2 kHz, brillance +2 dB à 9 kHz, compression 4:1, de-esser, −14 LUFS.
  - *Débit rapide* : vitesse ×1,28 sur les phrases. Les mots isolés gardent une vitesse normale, sinon ils deviennent incompréhensibles.
  - *Suspense* : « La réponse… » est un vrai chuchotement (aucune vibration des cordes vocales, 100 % souffle) avec un léger écho.
- **Contrôle** : chaque réplique et le mixage final ont été retranscrits automatiquement, avec zéro erreur. Formulations retenues après test : « Le Brésil », « La Grèce », « Le Bhoutane », « Le Tchad », « Kazak-stane », « Aïe aïe aïe ».
- **Réglages fixes à garder** pour toutes les vidéos : même modèle, mêmes paramètres. C'est l'équivalent du VOICE_ID.
- **Phonétique :** Kazakhstan ➜ « Kazak-stane ».
- **Licence :** le modèle `tom` est publié par le projet Piper. ➜ À FAIRE PAR TOI : vérifier sa licence dans la fiche du modèle (huggingface.co/rhasspy/piper-voices) avant un usage monétisé.
- **Régénérer :** `python3 build/voice_claude.py assets/piper/fr_FR-tom-medium.onnx`, puis `VOICE_DIR=assets/voice_claude OUT_NAME=... python3 audio.py && python3 render.py` (depuis `build/`).

## 2-4. Questions, réponses, confiance
| # | Niveau | Drapeau | Réponse (échelle) | Pourquoi ce niveau | Confiance / source |
|---|---|---|---|---|---|
| 1 | 🟢 Facile | Japon | Japon | Le drapeau le plus reconnaissable du monde | SÛR — Wikimedia « Flag of Japan » |
| 2 | 🟢 Facile | Brésil | Brésil | Losange vert-jaune, très connu (football) | SÛR |
| 3 | 🟢 Facile | Canada | Canada | Feuille d'érable iconique : une victoire qui fait plaisir | SÛR |
| 4 | 🟡 Moyen | Turquie | Turquie | Croissant + étoile : on peut hésiter avec la Tunisie | SÛR |
| 5 | 🟡 Moyen | Grèce | Grèce | Bandes bleues et blanches : on peut hésiter avec l'Uruguay | SÛR |
| 6 | 🟡 Moyen | Corée du Sud | Corée du Sud | Connu, mais confondu avec le Japon ou la Corée du Nord | SÛR |
| 7 | 🟠 Difficile | Népal | Népal | Seul drapeau non rectangulaire, mais le pays est peu cité | SÛR |
| 8 | 🟠 Difficile | Kazakhstan | Kazakhstan | Soleil et aigle sur fond bleu ciel : réservé aux passionnés | SÛR |
| 9 | 🔴 Extrême | Bhoutan | Bhoutan | Le dragon est spectaculaire, mais le pays est rarement associé | SÛR |
| 10 | 🔴 Extrême | Tchad | Tchad | Quasi identique à la Roumanie. L'indice « ce n'est PAS la Roumanie » rend la question juste | SÛR — Wikimedia « Flag of Chad » |

## 5. Accroches
1. **« Seuls les vrais fans auront dix sur dix ! »** (utilisée)
2. « Tu tiens jusqu'au niveau extrême ? »
3. « Je parie que tu bloques avant la fin ! »

## 6-7. Script de la voix (fichiers dans `assets/voice/`, versions rognées et accélérées ×1,12 dans `assets/voice/trimmed/`)
`01_accroche` Seuls les vrais fans auront dix sur dix ! · `02_Q1_question` Quel est ce pays ? · `03_Q1_reponse` Japon ! Trop facile ! · `04_Q2_question` Et celui-là ? · `05_Q2_reponse` Brésil ! · `06_Q3_question` Suivant ! · `07_Q3_reponse` Canada ! Bien joué ! · `08_niveau_moyen` Niveau moyen ! · `09_Q4_reponse` Turquie ! · `10_Q5_question` Celui-ci ? · `11_Q5_reponse` Grèce ! · `12_Q6_question` Et lui ? · `13_Q6_reponse` Corée du Sud ! Bravo ! · `14_niveau_difficile` Ça se complique ! · `15_Q7_reponse` Népal ! Aïe ! · `16_Q8_question` Attention… · `17_Q8_reponse` Kazakhstan ! · `18_niveau_extreme` Niveau extrême ! · `19_suspense` [whispers] La réponse… · `20_Q9_reponse` Le Bhoutan ! · `21_Q10_question` Le dernier ! · `22_Q10_reponse` Tchad ! Pas la Roumanie ! · `23_conclusion` Alors, t'as combien ? Dis-le en commentaire !

**Phonétique :** « Bhoutan » était lu « Boutin ». Écrit « Bhoutanne », il a été retranscrit correctement.

## 8-12. Images, écran, son
- **Drapeaux :** Wikimedia Commons (rendus PNG des SVG officiels), cadre arrondi de la couleur du niveau, ombre portée.
- **Fond :** mosaïque floutée de drapeaux qui **ne sont pas** dans le quiz (France, Italie, Espagne…), teintée selon le niveau, en panoramique lent.
- **Mise en page :** celle du §4.4 (bandeau 170-310, échelle x 40-310, image x 330-890, texte de la question y ≈ 1120, compte à rebours y 1255-1365). Rien d'utile dans les zones de sécurité.
- **Polices :** Luckiest Guy (titres) et Baloo 2 ExtraBold (échelle), toutes deux sous licence OFL, utilisables commercialement.
- **Effets sonores :** synthétisés par le script, sans aucun droit à payer : whoosh, pop, tic-tac en doubles croches qui passe en triples croches dans la dernière seconde (plus grave au Difficile et à l'Extrême), ding, level-up, impact grave, roulement de suspense, jingle final.
- **Musique :** composition procédurale à 120 BPM (Am-F-C-G), sans aucun droit à payer. Chaque niveau ajoute des couches (clap, open hat, arpège, kicks). Coupure nette pendant le suspense. Ducking automatique sous la voix.

## 13. Découpage (calculé à partir des vraies durées des voix, voir `build/timeline.py`)
| Q | Niveau | Apparition | Rebours | Révélation | Fin |
|---|---|---|---|---|---|
| 1 | Facile | 0,00 | 0,20 → 4,25 | 4,25 | 6,00 |
| 2 | Facile | 6,00 | 6,20 → 9,25 | 9,25 | 10,25 |
| 3 | Facile | 10,25 | 10,45 → 13,50 | 13,50 | 15,00 |
| 4 | Moyen (bandeau 15,00-15,50) | 15,00 | 15,70 → 18,75 | 18,75 | 19,75 |
| 5 | Moyen | 19,75 | 19,95 → 23,00 | 23,00 | 24,00 |
| 6 | Moyen | 24,00 | 24,20 → 27,25 | 27,25 | 28,75 |
| 7 | Difficile (bandeau) | 28,75 | 29,45 → 32,50 | 32,50 | 33,50 |
| 8 | Difficile | 33,50 | 33,70 → 36,75 | 36,75 | 37,75 |
| 9 | Extrême (bandeau, tremblement, flash rouge) | 37,75 | 38,45 → 41,50 | suspense 41,50-42,50, puis 42,50 | 43,50 |
| 10 | Extrême | 43,50 | 43,70 → 46,75 | suspense 46,75-47,75, puis 47,75 | 49,25 |
| — | Conclusion « TON SCORE ? / 10 » | 49,25 | — | — | 52,25 (boucle) |

## 14. Durée
10 questions de 4,25 à 5,75 s, plus 2 suspenses de 1 s, plus une conclusion de 3 s : **52,25 s**. L'écart avec les 45 s visés vient des réactions vocales (« Trop facile ! » dure 2 s) et de l'accroche (2,4 s au lieu de 1,5 s). Pour gagner environ 5 s : supprime les réactions des Q1, Q3 et Q6, et raccourcis l'accroche en « Dix sur dix ? Prouve-le ! ».

## 15. Test du pouce : les 3 moments à risque
1. **0-2,4 s :** l'accroche dépasse 1,5 s. Pour compenser, le drapeau du Japon, l'échelle et le texte d'accroche sont tous à l'écran dès l'image 0, et le compte à rebours démarre à 0,2 s.
2. **Le passage Facile → Moyen (15 s) :** risque de lassitude. Le bandeau « NIVEAU MOYEN ! », le level-up, le changement de teinte et la musique qui s'étoffe relancent l'attention.
3. **Le suspense de l'Extrême (1 s de musique coupée) :** l'écran s'assombrit, « LA RÉPONSE… » pulse, un roulement monte, puis la révélation arrive avec un flash.

## 16. Conclusion
« Alors, t'as combien ? Dis-le en commentaire ! » + « TON SCORE ? / 10 » + « Abonne-toi pour le prochain quiz ! ». Dans les 0,3 dernières secondes, les réponses de l'échelle s'effacent et le fond repasse au vert, pour que la boucle s'enchaîne sans coupure visible.

## 17. YouTube Shorts
- **Titre :** Quiz Drapeaux : tu tiens jusqu'au niveau extrême ? 🌍
- Variantes : « 10 drapeaux, 4 niveaux : t'as combien ? 🌍 » / « Seuls les vrais fans ont 10/10 (Quiz Drapeaux) »
- **Description :** Dix drapeaux, quatre niveaux, une seule question : t'as combien ? Écris ton score en commentaire ! Drapeaux : Wikimedia Commons (domaine public). Musique et effets originaux.
- **Hashtags :** #quizdrapeaux #drapeaux #quiz #culturegenerale #shorts

## 18. TikTok
- **Légende :** Quiz drapeaux : t'as combien sur 10 ? 🌍 Test culture générale
- **Hashtags :** #quizdrapeaux #quiz #culturegenerale #geographie #pourtoi
- **Couverture :** `output/couverture.png` (première image), texte « QUIZ DRAPEAUX 🌍 Niveau extrême ? »

## 19. Commentaire à épingler
« Le dernier drapeau… vous avez dit Roumanie ? 👀 Score honnête en dessous ! »

## 20. Crédits
Drapeaux : Wikimedia Commons, « Flag of Japan / Brazil / Canada / Turkey / Greece / South Korea / Nepal / Kazakhstan / Bhutan / Chad », domaine public. Polices : Luckiest Guy et Baloo 2 (SIL OFL). Voix : ElevenLabs. Musique et effets : générés par le script `build/audio.py`.

## 21. Export
Déjà fait : 1080 × 1920, 30 i/s, H.264 High CRF 16, AAC 192 kb/s, faststart. Aucun filigrane, aucune séquence de fin CapCut.

## 22. ➜ À FAIRE PAR TOI
- [ ] Regarder la vidéo sur téléphone, avec et sans son, et **écouter la voix** (accent).
- [ ] Vérifier dans les aperçus TikTok et YouTube que les boutons ne cachent rien.
- [ ] Vérifier la licence actuelle de chaque drapeau sur Wikimedia Commons.
- [ ] Publier le MP4 d'origine sur **chaque** plateforme séparément, en haute qualité sur TikTok.
- [ ] Publier et épingler le commentaire, puis répondre aux commentaires pendant la première heure.
- [ ] Noter où les spectateurs décrochent (rétention YouTube, visionnage complet TikTok) et me le dire.
- [ ] Étiquette IA : la voix est synthétique, mais aucune image n'est générée par IA. Vérifie les règles en vigueur sur chaque plateforme.

## 23. Prochaines vidéos
1. **Quiz Drapeaux 2 : les jumeaux** (Indonésie/Monaco, Irlande/Côte d'Ivoire…). C'est la suite directe du piège Tchad/Roumanie.
2. **Quiz Capitales** (drapeau affiché, on demande la capitale).
3. **Quiz Silhouettes de pays** (mécanique ⚡ silhouette).

## Régénérer la vidéo
```
cd build
python3 audio.py     # mix.wav (musique, effets, voix)
python3 render.py    # rendu des images + mux -> output/quiz_drapeaux.mp4
```
Pour changer le quiz : modifie `QUESTIONS` dans `build/timeline.py` (drapeaux dans `assets/flags/`, voix dans `assets/voice/trimmed/`).

## Checklist
✅ Q1 et bandeau à 0,0 s · ⚠️ accroche de 2,4 s (au lieu de 1,5 s) · ✅ un événement au moins toutes les 1,5 s (tic-tac toutes les 0,25 s) · ✅ blancs audio < 0,3 s · ✅ bandeaux de niveau de 0,5 s · ✅ énergie qui monte · ✅ boucle · ✅ score demandé · ✅ commentaire épinglé fourni · ✅ échelle permanente · ✅ 4 niveaux et leurs couleurs · ✅ réponses de 14 caractères max · ✅ rebours ≥ 3 s · ✅ 52,25 s < 59 s · ✅ aucune image IA de personne · ✅ zones de sécurité respectées
