# Lana 30 jours — Épisode 1, version 5 (1 min 46)

Même histoire que la v4, avec une **voix off entièrement refaite**, toujours sans ElevenLabs :

- Moteur : **Chatterbox multilingue** (Resemble AI, licence MIT, utilisable commercialement), tourne en local.
- Voix de référence : extraits de livres audio **LibriVox (domaine public)** — narrateur grave et expressif, deux lectrices pour Lana et Inès.
- Interprétation réglée réplique par réplique (pince-sans-rire, mielleuse pour Inès, cri, émotion au souvenir du bal).
- Chaque réplique générée plusieurs fois ; la meilleure prise est choisie automatiquement par transcription (Whisper local).
- Traitement « voix radio » (coupe-bas, présence, compression), débit accéléré sans changer la hauteur, respirations resserrées.
- Bruitages : 10, uniquement ceux qui racontent quelque chose, jamais par-dessus un mot. Volume -14 LUFS.
- Vidéo : coup de zoom quand Lana parle, glissé rapide entre les plans, Lana se fige sur « Attends… » puis explose sur « Quoi ?! Nathan ?! ».

Changements de texte : « Hors de question. » → « Non. Hors de question. » ; « Quoi ?! Nathan ?! » → « Attends… Quoi ?! Nathan ?! ».

## Refaire
```
<venv>/python outils/voix_chatterbox.py episodes/ep01-v5/voix-off.json build/ep01-v5/brut
python3 outils/voix_post.py episodes/ep01-v5/voix-off.json build/ep01-v5/brut build/ep01-v5/voix
export VOIX_DIR=build/ep01-v5/voix OUT_DIR=build/ep01-v5
node outils/mix-ep2d.js
DSF=1.5 node outils/render.js ./ep2d.js video build/ep01-v5/video.mp4 30 4
```
