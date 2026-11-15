# Épisode 1 — « Jour 1 sur 30 » (version finale)

Durée : 1 min 08 · Format 9:16 · Voix off : Brian (ElevenLabs, eleven_multilingual_v2)
Habillage permanent : « JOURS RESTANTS 30 » + « GLOW-UP 0 % », sous-titres mot par mot (mot courant en jaune).

| # | Scène | Voix off | Animation / texte / son |
|---|---|---|---|
| 1 | Téléphone sur les boîtes de pizza | Voici Lana. Et voici le message qui va ruiner son mois. | Titre « LANA A 30 JOURS », vibration, notification d'Inès (« Nathan vient ❤ ») |
| 2 | Lit, seul le chignon dépasse de la couette | Lana a vingt-cinq ans. Ses volets sont fermés depuis la dernière Coupe du monde. | Grillons, couette qui respire, étiquettes « LANA · 25 ANS » et « FERMÉS DEPUIS 2022 » |
| 3 | Lana debout dans sa chambre | Elle bosse au service client… depuis son lit. Les clients pensent qu'elle s'appelle Sandrine. | Bâillement, haussement d'épaules, badge « SANDRINE » qui apparaît |
| 4 | Pâtes, le chat | Lui, c'est Pâtes. Le seul être vivant qui la voit tous les jours. Et il a demandé à déménager. | Miaulement, queue qui bat, valise « BYE » qui tombe |
| 5 | Lana lit le message | Le message vient d'Inès, son ex-meilleure amie. Les dix ans du lycée, c'est dans trente jours. Et Nathan sera là. | Choc : yeux exorbités, cri, cœur, tremblement, « dun dun dun » |
| 6 | Flashback polaroïd « LYCÉE · 2016 » | Il y a dix ans, Lana était la fille la plus stylée du lycée. | Disque rayé, Lana ado rayonnante, étincelles |
| 7 | Zoom sur la fenêtre | Aujourd'hui, son seul jean lui sert de rideau. | Le jean accroché en guise de rideau |
| 8 | Elle se lève et glisse | Alors Lana se lève, décidée à tout changer… / Elle a glissé sur une boîte de nuggets. | Poing levé, glissade, « PAF ! », jambes qui dépassent du linge, étoiles |
| 9 | Miroir de la salle de bain | Il lui reste trente jours. Et ce n'est pas elle qui choisit. C'est toi. | Post-it, « J-30 », Lana pointe la caméra |
| 10 | Écran partagé | Par quoi elle commence ? Son appart… ou ses sourcils ? | « APPART » OU « SOURCILS » |
| 11 | Appel au vote | Commente un seul mot. Le plus voté sera réglé demain. Et chaque changement reste pour toujours. | Lana fait coucou avec Pâtes sur l'épaule, « COMMENTE UN MOT 👇 », « JOUR 2 TRÈS BIENTÔT ⏰ » |

## Légende TikTok
Jour 1 sur 30 😬 Lana a 30 jours avant les 10 ans de son lycée, et c'est TOI qui choisis chaque changement. Commente UN mot : APPART ou SOURCILS. Le plus voté sera réglé au jour 2, et chaque changement reste pour toujours. Abonne-toi pour ne pas rater la transformation. Le jour 30 va être dingue. #30joursdetransformation #transformation #glowup #animation #histoire

## Refaire l'épisode
```
python3 outils/voix.py episodes/ep01/voix-off.json build/ep01/voix
python3 outils/sfx.py episodes/ep01/bruitages.json build/ep01/sfx
node outils/mix-ep01.js
node outils/render.js ./ep01.js video build/ep01/video.mp4 30 4
ffmpeg -i build/ep01/video.mp4 -i build/ep01/audio.m4a -c:v copy -c:a copy -shortest episodes/ep01/lana-jour-01.mp4
```

---

# Version 2 — optimisée TikTok (`lana-jour-01-v2-tiktok.mp4`)

58 s · 1080 × 1920 · 30 i/s · aucune nouvelle génération ElevenLabs (voix et sons existants réutilisés)

| Temps | Plan | Changement |
|---|---|---|
| 0:00 – 0:02 | **Accroche** | Ouverture sur le choc : Lana hurle sur son téléphone (« Et Nathan sera là »), gros plan, tremblement, flash rouge. Texte : « SON CRUSH REVIENT DANS 30 JOURS 😱 ». Puis effet VHS « ⏪ 1 HEURE PLUS TÔT » + disque rayé |
| 0:02 – 0:05 | Téléphone | La notification s'affiche dès 0,3 s (au lieu de 0,9 s) |
| 0:05 – 0:47 | Histoire | Blancs entre les phrases réduits à 0,16 s, voix accélérée de 12 % (même hauteur), marges de début et de fin de plan raccourcies |
| tout du long | Sous-titres | Mots-clés en rouge et plus gros (NATHAN, SANDRINE, DÉMÉNAGER, NUGGETS, TOI, APPART, SOURCILS…) + coup de zoom sur chacun |
| chaque coupe | Transitions | Glissé + zoom d'entrée + whoosh |
| 0:45 – 0:54 | Vote | Plus court, appel au vote conservé |
| 0:54 – 0:58 | **Écran final** | Silhouette mystère « JOUR 30 : MÉCONNAISSABLE ? », « DEMAIN : ON SONNE À SA PORTE 👀 », « 🔔 ABONNE-TOI POUR LA SUITE », « ENVOIE ÇA À TA POTE EN PYJAMA 🦄 » |

Refaire : `python3 outils/resserrer.py build/ep01/voix build/ep01v2/voix 1.12 s5:16:19:s0 s1 s2 s3 s4 s5 s5b s5c s6a s6b s7 s8 s9`
puis `node outils/mix-ep01.js ./ep01v2 ep01v2` et `DSF=1.5 node outils/render.js ./ep01v2.js video build/ep01v2/video.mp4 30 4`.

Légende conseillée :
Son crush revient dans 30 jours… et c'est TOI qui décides de sa transformation 😬 Jour 1/30 : commente APPART ou SOURCILS 👇 Le plus voté sera réglé demain. #30joursdetransformation #glowup #transformation #animation #histoire
