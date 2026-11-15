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
