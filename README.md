# Vid-o-ia
## lyrics_edit.py — vidéos « lyrics edit » 9:16

```
python3 lyrics_edit.py paroles.txt -o video.mp4 --pseudo @moncompte [--clips mes_clips/]
```

- `paroles.txt` : une ligne par mot, `temps MOT` (`*MOT` = mot en blanc), terminer par `END <secondes>`. Voir `paroles_exemple.txt`.
- Sans `--clips`, les décors de ville la nuit sont générés automatiquement.
- La vidéo sort **sans son** : ajoute le morceau dans TikTok en le démarrant au même moment que celui utilisé pour minuter le fichier.
- `--preview 10` pour un aperçu rapide des 10 premières secondes.
