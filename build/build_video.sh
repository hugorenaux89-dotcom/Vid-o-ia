#!/bin/bash
# Monte la vidéo d'un quiz (voix déjà générée) : ./build_video.sh quizzes/<slug>
set -e
Q=$(realpath "$1"); SLUG=$(basename $Q)
cd "$(dirname "$0")"
export QUIZ=$Q/quiz.json VOICE_DIR=$Q/voice CD_STEP=${CD_STEP:-0.87} OUT_NAME=$SLUG.mp4
python3 timeline.py | grep -E "durée"
python3 audio.py > /dev/null
python3 render.py 2>&1 | grep -E "OK|Error|Trace"
ffmpeg -v error -y -i video_noaudio.mp4 -i mix.wav -af "volume=8dB,alimiter=limit=0.84:level=false" -c:v copy -c:a aac -b:a 192k -ar 44100 -shortest -movflags +faststart ../output/$SLUG.mp4
ffmpeg -v error -y -ss 0.5 -i ../output/$SLUG.mp4 -frames:v 1 ../output/$SLUG.jpg
ffprobe -v error -show_entries format=duration -of csv=p=0 ../output/$SLUG.mp4
