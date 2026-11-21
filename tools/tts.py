#!/usr/bin/env python3
"""Génère la voix off d'un épisode avec ElevenLabs (+ timestamps caractère par caractère).

Usage : python3 tools/tts.py episodes/ep01
Lit   : <episode>/voiceover.txt et <episode>/episode.json (bloc "voice")
Écrit : <episode>/build/voice.mp3 et <episode>/build/alignment.json

La clé API est lue dans ELEVENLABS_API_KEY (ou injectée par un proxy).
"""
import base64
import json
import os
import sys
import urllib.error
import urllib.request

API = "https://api.elevenlabs.io/v1"


def main(ep_dir):
    cfg = json.load(open(os.path.join(ep_dir, "episode.json"), encoding="utf-8"))
    voice = cfg.get("voice", {})
    text = open(os.path.join(ep_dir, "voiceover.txt"), encoding="utf-8").read().strip()
    body = {
        "text": text,
        "model_id": voice.get("model_id", "eleven_multilingual_v2"),
        "language_code": "fr",
        "voice_settings": voice.get("settings", {
            "stability": 0.42, "similarity_boost": 0.8, "style": 0.35,
            "use_speaker_boost": True, "speed": 0.95}),
    }
    url = f"{API}/text-to-speech/{voice.get('voice_id', 'pNInz6obpgDQGcFmaJgB')}/with-timestamps?output_format=mp3_44100_128"
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={
        "xi-api-key": os.environ.get("ELEVENLABS_API_KEY", "proxy-injected"),
        "Content-Type": "application/json"})
    try:
        r = json.load(urllib.request.urlopen(req))
    except urllib.error.HTTPError as e:
        sys.exit(e.read().decode()[:800])
    os.makedirs(os.path.join(ep_dir, "build"), exist_ok=True)
    open(os.path.join(ep_dir, "build", "voice.mp3"), "wb").write(base64.b64decode(r["audio_base64"]))
    json.dump(r["alignment"], open(os.path.join(ep_dir, "build", "alignment.json"), "w"), ensure_ascii=False)
    print("voix :", r["alignment"]["character_end_times_seconds"][-1], "s")


if __name__ == "__main__":
    main(sys.argv[1])
