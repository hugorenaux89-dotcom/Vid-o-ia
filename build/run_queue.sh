#!/bin/bash
# File d'attente : voix + montage pour chaque quiz donné en argument (slugs)
cd "$(dirname "$0")"
for slug in "$@"; do
  if [ ! -f ../quizzes/$slug/voice/99_conclusion.wav ]; then ./make_voices.sh ../quizzes/$slug; fi
  ./build_video.sh ../quizzes/$slug && echo "VIDEO_OK $slug" || echo "VIDEO_ECHEC $slug"
done
echo "FILE_TERMINEE"
