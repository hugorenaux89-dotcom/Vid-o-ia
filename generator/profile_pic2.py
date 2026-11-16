#!/usr/bin/env python3
"""Photo de profil n°2 (1080x1080) : le personnage qui pousse son rocher — "YOU VS YOU"."""
import os
import sys

import cairo

sys.path.insert(0, os.path.dirname(__file__))
import ego_video as E  # noqa: E402

S = 1080


def main(out="output/photo_profil_2.png"):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, S, S)
    ctx = cairo.Context(surf)
    E.rgb(ctx, (0.03, 0.03, 0.035))
    ctx.paint()
    E.glow(ctx, 600, 470, 520, E.RED, 0.45)

    # la scene du rocher (coordonnees de la video 1080x1920) recadree dans le carre
    ctx.save()
    ctx.translate(S / 2, S / 2 + 90)
    ctx.scale(0.9, 0.9)
    ctx.translate(-380, -1210)
    E.you_vs_you_image(ctx, 0.9, 10, fig_col=E.RED)
    ctx.restore()

    E.text(ctx, "YOU VS YOU", S / 2, 215, 100, family=E.SERIF, color=(1, 1, 1))

    g = cairo.RadialGradient(S / 2, S / 2, S * 0.32, S / 2, S / 2, S * 0.72)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0, 0, 0, 0.75)
    ctx.set_source(g)
    ctx.paint()
    E.grain(ctx, 3, 0.05)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    surf.write_to_png(out)
    print(out)


if __name__ == "__main__":
    main(*sys.argv[1:])
