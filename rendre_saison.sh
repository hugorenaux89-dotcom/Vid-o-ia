#!/bin/bash
# Rend les épisodes (2 en parallèle) dans un dossier temporaire ignoré par git,
# puis déplace chaque vidéo terminée dans sortie/ et l'enregistre (commit + push).
# Usage : ./rendre_saison.sh            (tous les épisodes)
#         ./rendre_saison.sh 4 7 12     (seulement ces épisodes)
cd "$(dirname "$0")"
mkdir -p sortie/.en_cours
BRANCHE=$(git rev-parse --abbrev-ref HEAD)
export BRANCHE
rendre() {
  n=$1
  if python3 generer_episode.py "episodes/episode$n.json" "sortie/.en_cours/episode$n.mp4" >> sortie/rendu.log 2>&1; then
    mv "sortie/.en_cours/episode$n.mp4" "sortie/episode$n.mp4"
    mv "sortie/.en_cours/episode${n}_sans_musique.mp4" "sortie/episode${n}_sans_musique.mp4"
    (
      flock 9
      git add "sortie/episode$n.mp4" && git commit -q -m "Vidéo de l'épisode $n

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01JNk9t8jXnu2qHuk5bAHa8L" >> sortie/rendu.log 2>&1
      for essai in 1 2 3 4; do git push -q origin "$BRANCHE" >> sortie/rendu.log 2>&1 && break; sleep $((essai * 5)); done
    ) 9> sortie/.en_cours/git.lock
    echo "épisode $n OK" >> sortie/rendu.log
  else
    echo "épisode $n ÉCHEC" >> sortie/rendu.log
  fi
}
export -f rendre
if [ $# -gt 0 ]; then printf "%s\n" "$@"; else seq 1 50; fi | xargs -P 2 -I{} bash -c 'rendre {}'
