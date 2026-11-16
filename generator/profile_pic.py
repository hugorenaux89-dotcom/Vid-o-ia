#!/usr/bin/env python3
"""Photo de profil TikTok (1080x1080) dans le style des videos : l'EGO rouge, numero 1."""
import math
import os
import sys

import cairo

sys.path.insert(0, os.path.dirname(__file__))
import ego_video as E  # noqa: E402

S = 1080


def main(out="output/photo_profil.png"):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, S, S)
    ctx = cairo.Context(surf)
    E.rgb(ctx, (0.05, 0.05, 0.055))
    ctx.paint()
    E.glow(ctx, S / 2, 520, 560, E.RED, 0.42)
    E.glow(ctx, S / 2, 520, 300, E.RED, 0.25)

    # bloc "1"
    E.rgb(ctx, (0.2, 0.2, 0.21))
    ctx.rectangle(330, 760, 420, 400)
    ctx.fill()
    E.rgb(ctx, (0.3, 0.3, 0.31))
    ctx.rectangle(330, 760, 420, 12)
    ctx.fill()
    E.text(ctx, "1", S / 2, 960, 170, color=(0.5, 0.5, 0.51))

    # l'EGO, bras levés
    pose = E.P(la1=-128, la2=-142, ra1=128, ra2=142, ll1=-16, ll2=-9, rl1=16, rl2=9)
    s = 1.85
    hy = E.ground_hip_y(pose, s, 760)
    j = E.stick(ctx, S / 2, hy, pose, s, fill=E.RED, shadow=760)
    E.text(ctx, "EGO", S / 2, hy + j["head"][1] - 150, 56, color=(1, 1, 1), spacing=10)

    # confettis
    import random
    r = random.Random(5)
    for _ in range(45):
        x, y = r.uniform(80, 1000), r.uniform(60, 700)
        if math.hypot(x - S / 2, y - 480) < 260:
            continue
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(r.uniform(0, 6.28))
        E.rgb(ctx, r.choice([(0.85, 0.85, 0.85), E.RED, (0.55, 0.55, 0.55)]), 0.8)
        ctx.rectangle(-7, -11, 14, 22)
        ctx.fill()
        ctx.restore()

    g = cairo.RadialGradient(S / 2, S / 2, S * 0.3, S / 2, S / 2, S * 0.72)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0, 0, 0, 0.7)
    ctx.set_source(g)
    ctx.paint()
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    surf.write_to_png(out)
    print(out)


if __name__ == "__main__":
    main(*sys.argv[1:])
