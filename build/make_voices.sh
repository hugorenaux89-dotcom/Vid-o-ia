#!/bin/bash
# Génère + sélectionne la voix d'un quiz : ./make_voices.sh quizzes/<slug>
set -e
Q=$(realpath "$1")
PY_KY=${PY_KY:-/tmp/claude-0/-home-user-Vid-o-ia/85f0123f-a490-5d08-971d-cbf19527dc3d/scratchpad/kyu/bin/python}
cd "$(dirname "$0")"
QUIZ=$Q/quiz.json TAKES=${TAKES:-2} $PY_KY voice_kyutai.py unmute-prod-website/fabieng-enhanced-v2.wav $Q/voice/raw 2>&1 | grep --line-buffered -E "^[0-9q]|Error|Traceback" || true
QUIZ=$Q/quiz.json SEL_RAW=$Q/voice/raw SEL_OUT=$Q/voice TV_TEMPO=1.1 python3 voice_tv_select.py
