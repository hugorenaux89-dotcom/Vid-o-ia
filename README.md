# Vid-o-ia

Générateur de vidéos motivation style « stickman » (format TikTok / Reels, 1080x1920, 30 fps).

## EGO vs MOTIVATION / DISCIPLINE / TALENT

`generator/ego_video.py` dessine toute la vidéo image par image (aucun visuel copié) :

1. Podium MOTIVATION / DISCIPLINE / TALENT + foule, l'EGO arrive 4e
2. Gros plans, puis tout le monde se moque de l'EGO (étiquettes LOSER, GIVE UP, 4TH PLACE, NOBODY)
3. DAY 1 – REPS 0 → première traction
4. Time-lapse : calendrier qui défile (jour 1 → 365), tractions / pompes, REPS → 25 000
5. Jour « X » : l'EGO seul, lumière rouge
6. Course : il tombe, bulle de pensée avec la foule qui rit, il devient rouge
7. Photo motivation « obsessed » (définition du dictionnaire) – *obsession beats talent. every time.*
8. Photo motivation « IT'S YOU VS YOU » avec le personnage qui pousse son rocher
9. Course : l'EGO rouge dépasse tout le monde et passe la ligne FINISH
10. PROVE THEM ALL **WRONG.**
11. Podium final : l'EGO est numéro 1

La vidéo est en vitesse normale (x1, ~42 s). L'enregistrement d'origine était en x2.

Style : bonhommes sans visage (membres arrière plus sombres, reflets, ombres au sol), caméra dynamique (zoom à chaque coupe, whip-pan, secousses aux impacts, traînées de vitesse) et flou de mouvement (`--mb 3` par défaut, `--mb 1` pour un rendu plus rapide). Le rocher de « IT'S YOU VS YOU » est généré procéduralement (relief, éclairage, fissures) et le personnage le pousse avec de vraies mains posées dessus (cinématique inverse).

```bash
pip install pycairo numpy pillow        # + ffmpeg
python3 generator/ego_video.py --music assets/musique_ego.m4a                 # x1 -> output/ego_vs_discipline.mp4
python3 generator/ego_video.py --music assets/musique_ego.m4a --speed 2 -o output/ego_vs_discipline_x2.mp4
python3 generator/ego_video.py --preview                                     # planche de captures
```

La musique (`assets/musique_ego.m4a`) a été générée avec ElevenLabs (piano sombre puis beat phonk à partir de la chute).
