"""Pre-process source photos into render-ready layers.

For every photo in assets/photos:
  - resize to a working resolution
  - cut out the player(s) with a human-segmentation net (rembg / U2Net)
  - refine the matte with a guided filter so hair/edges stay clean
  - build a "clean plate" background (player removed + inpainted) for 2.5D parallax

Output per photo in build/prep/<key>.npz : img (uint8 HxWx3, RGB), mask (uint8 HxW),
bg (uint8 HxWx3), bbox (x0,y0,x1,y1 of the subject).
"""
import glob
import os
import sys

import cv2
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets", "photos")
OUT = os.path.join(ROOT, "build", "prep")

LONG_SIDE = 2600


def guided_filter(I, p, r, eps):
    """He et al. guided filter. I: guide (float32 gray 0..1), p: input (float32)."""
    ksize = (2 * r + 1, 2 * r + 1)
    mean_I = cv2.boxFilter(I, -1, ksize)
    mean_p = cv2.boxFilter(p, -1, ksize)
    corr_Ip = cv2.boxFilter(I * p, -1, ksize)
    corr_II = cv2.boxFilter(I * I, -1, ksize)
    var_I = corr_II - mean_I * mean_I
    cov_Ip = corr_Ip - mean_I * mean_p
    a = cov_Ip / (var_I + eps)
    b = mean_p - a * mean_I
    mean_a = cv2.boxFilter(a, -1, ksize)
    mean_b = cv2.boxFilter(b, -1, ksize)
    return mean_a * I + mean_b


def main(keys=None):
    from rembg import new_session, remove

    os.makedirs(OUT, exist_ok=True)
    session = new_session("u2net_human_seg")
    files = sorted(f for f in glob.glob(os.path.join(SRC, "*"))
                   if f.lower().endswith((".jpg", ".jpeg", ".png")))
    for f in files:
        key = os.path.splitext(os.path.basename(f))[0]
        if keys and key not in keys:
            continue
        dst = os.path.join(OUT, key + ".npz")
        if os.path.exists(dst) and not keys:
            continue
        im = Image.open(f)
        im = im.convert("RGB")
        w, h = im.size
        s = min(1.0, LONG_SIDE / max(w, h))
        if s < 1:
            im = im.resize((int(w * s), int(h * s)), Image.LANCZOS)
        img = np.asarray(im).copy()
        H, W = img.shape[:2]

        # segmentation at ~1280 px for speed, matte refined at full res
        s2 = min(1.0, 1280 / max(W, H))
        small = cv2.resize(img, (int(W * s2), int(H * s2)), interpolation=cv2.INTER_AREA)
        m = np.asarray(remove(Image.fromarray(small), session=session, only_mask=True))
        m = cv2.resize(m, (W, H), interpolation=cv2.INTER_CUBIC).astype(np.float32) / 255
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).astype(np.float32) / 255
        r = max(4, int(max(W, H) / 400))
        m = guided_filter(gray, m, r, 1e-3)
        m = np.clip((m - 0.08) / 0.84, 0, 1)
        mask = (m * 255).astype(np.uint8)

        # subject bbox
        ys, xs = np.where(mask > 128)
        if len(xs) == 0:
            bbox = (0, 0, W, H)
        else:
            bbox = (int(np.percentile(xs, 1)), int(np.percentile(ys, 1)),
                    int(np.percentile(xs, 99)), int(np.percentile(ys, 99)))

        # clean plate: inpaint the player out at low res, upsample, blend in
        s3 = 640 / max(W, H)
        sm_img = cv2.resize(img, (int(W * s3), int(H * s3)), interpolation=cv2.INTER_AREA)
        sm_mask = cv2.resize(mask, (int(W * s3), int(H * s3)), interpolation=cv2.INTER_AREA)
        sm_mask = cv2.dilate((sm_mask > 20).astype(np.uint8) * 255, np.ones((9, 9), np.uint8))
        inp = cv2.inpaint(cv2.cvtColor(sm_img, cv2.COLOR_RGB2BGR), sm_mask, 7, cv2.INPAINT_TELEA)
        inp = cv2.cvtColor(inp, cv2.COLOR_BGR2RGB)
        inp = cv2.GaussianBlur(inp, (0, 0), 2)
        inp = cv2.resize(inp, (W, H), interpolation=cv2.INTER_CUBIC)
        dm = cv2.dilate(mask, np.ones((max(3, r * 4) | 1,) * 2, np.uint8)).astype(np.float32) / 255
        dm = cv2.GaussianBlur(dm, (0, 0), r * 2)[..., None]
        bg = (img * (1 - dm) + inp * dm).astype(np.uint8)

        np.savez(dst, img=img, mask=mask, bg=bg, bbox=np.array(bbox))
        print(key, W, H, "bbox", bbox, flush=True)


if __name__ == "__main__":
    main(sys.argv[1:] or None)
