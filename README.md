# Vid-o-ia

Vidéos courtes de motivation (format vertical 1080×1920, TikTok / Reels / Shorts), générées par code :
figurines blanches lumineuses sur fond sombre, blocs, faisceaux de lumière, texte monospace.

## Vidéos

| # | Titre | Durée | Fichier |
|---|-------|-------|---------|
| 01 | Un bloc par jour (Motivation vs Discipline) | 1 min 14 s | `output/01_un_bloc_par_jour.mp4` |

## Structure

- `engine/core.py` : figurines (squelette + IK), caméra, blocs, flamme, texte, compositing avec halo et reflet au sol.
- `engine/music.py` : synthèse audio (piano, cordes, percussions, montée, réverb).
- `videos/NN_nom/scene.py` : scénario, poses, sous-titres et caméra d'une vidéo.
- `videos/NN_nom/render.py` : rendu des images en parallèle.
- `videos/NN_nom/audio.py` : bande-son synchronisée sur les événements de la scène.

## Refaire une vidéo

```bash
pip install -r requirements.txt
cd videos/01_un_bloc_par_jour
python3 render.py /tmp/frames                       # images + events.json
python3 render.py /tmp/prev --preview 5,30,62        # quelques images d'aperçu
python3 audio.py /tmp/frames/events.json SFX_DIR /tmp/audio.wav
ffmpeg -framerate 30 -i /tmp/frames/f%05d.jpg -i /tmp/audio.wav \
  -c:v libx264 -crf 21 -maxrate 9M -bufsize 18M -pix_fmt yuv420p \
  -af loudnorm=I=-14:TP=-1.5 -c:a aac -b:a 192k -shortest out.mp4
```

`SFX_DIR` contient `rain.wav`, `thunder.wav`, `impact.wav`, `whoosh.wav`, `hiss.wav`
(générés avec l'API d'effets sonores ElevenLabs).
