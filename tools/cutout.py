# -*- coding: utf-8 -*-
"""Вырезание сгенерированных картинок с хромакея (плоский пурпурный фон) в PNG с альфой."""
import os
import sys
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def cutout(src, dst, tol=78, pad=8, target_h=None, despill=0.9, feather=0.8, verbose=True):
    im = Image.open(src).convert("RGBA")
    w, h = im.size
    # 1) заливка фона от углов
    for seed in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
        try:
            ImageDraw.floodfill(im, seed, (0, 0, 0, 0), thresh=tol)
        except Exception:
            pass

    px = im.load()
    # 2) деспилл пурпурного по краям + чистка альфы
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            m = min(r, b) - g
            if m > 0:
                k = m * despill
                r = int(max(0, r - k))
                b = int(max(0, b - k))
                px[x, y] = (r, g, b, a)

    # 3) мягкая кромка по альфе
    alpha = im.getchannel("A")
    if feather:
        alpha = alpha.filter(ImageFilter.GaussianBlur(feather))
        im.putalpha(alpha)

    # 4) обрезка по содержимому
    bbox = im.getbbox()
    if bbox:
        l, t, r_, b_ = bbox
        l = max(0, l - pad)
        t = max(0, t - pad)
        r_ = min(w, r_ + pad)
        b_ = min(h, b_ + pad)
        im = im.crop((l, t, r_, b_))

    if target_h and im.height > 0:
        k = target_h / im.height
        im = im.resize((max(1, int(im.width * k)), target_h), Image.LANCZOS)

    os.makedirs(os.path.dirname(dst), exist_ok=True)
    im.save(dst)
    if verbose:
        print(f"{os.path.basename(dst)}: {im.size[0]}×{im.size[1]}, "
              f"{im.width*im.height/1024:.0f} КБ пикселей")
    return im


def preview_on_dark(src, dst, bg=(22, 26, 36), scale=1.0):
    im = Image.open(src).convert("RGBA")
    if scale != 1.0:
        im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
    canvas = Image.new("RGBA", (im.width + 40, im.height + 40), bg + (255,))
    canvas.alpha_composite(im, (20, 20))
    canvas.save(dst)


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    th = int(sys.argv[3]) if len(sys.argv) > 3 else None
    cutout(src, dst, target_h=th)
    preview_on_dark(dst, "/tmp/cut_preview.png")
