#!/bin/bash
# Rend tous les épisodes (2 en parallèle). Usage : ./rendre_saison.sh [premier] [dernier]
cd "$(dirname "$0")"
seq "${1:-1}" "${2:-50}" | xargs -P 2 -I{} sh -c \
  'python3 generer_episode.py episodes/episode{}.json sortie/episode{}.mp4 >> sortie/rendu.log 2>&1 && echo "épisode {} OK" >> sortie/rendu.log || echo "épisode {} ÉCHEC" >> sortie/rendu.log'
