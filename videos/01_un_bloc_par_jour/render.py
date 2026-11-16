"""Rendu des images + encodage. Usage : python3 render.py OUT_DIR [--preview t1,t2,...]"""
import json
import os
import subprocess
import sys
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(__file__))
import scene  # noqa: E402

CAMS = None


def work(f):
    path = os.path.join(OUT, f"f{f:05d}.jpg")
    if not os.path.exists(path):
        scene.render_frame(f, CAMS[f]).save(path, quality=93)
    return f


if __name__ == "__main__":
    OUT = sys.argv[1]
    os.makedirs(OUT, exist_ok=True)
    CAMS = scene.camera_track()
    if len(sys.argv) > 2 and sys.argv[2] == "--preview":
        for ts in sys.argv[3].split(","):
            f = int(float(ts) * scene.FPS)
            scene.render_frame(f, CAMS[f]).save(os.path.join(OUT, f"prev_{float(ts):05.1f}.jpg"), quality=90)
        sys.exit(0)
    n = int(scene.DURATION * scene.FPS)
    with Pool(os.cpu_count()) as pool:
        for i, _ in enumerate(pool.imap_unordered(work, range(n), chunksize=8)):
            if i % 300 == 0:
                print(f"{i}/{n}", flush=True)
    with open(os.path.join(OUT, "events.json"), "w") as fh:
        json.dump(scene.audio_events(), fh)
