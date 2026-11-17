# -*- coding: utf-8 -*-
"""Кинематографичный взрыв: кадр на чёрном фоне -> PNG с альфой (screen-key).

Идея: огонь и искры светятся, поэтому яркость пикселя и есть его «непрозрачность».
alpha = max(r, g, b), цвет делим на alpha — при наложении на тёмный космос
получается тот же кадр, но без чёрного прямоугольника вокруг.
Дальше один кадр разворачивается в 4 фазы вспышки (размер + затухание).
"""
import json
import os
import sys

from PIL import Image, ImageChops, ImageEnhance

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "assets", "raw")
FILM = os.path.join(ROOT, "assets", "film")
SIZE = 170           # итоговый холст костюма, шагов сцены
FRAMES = 4


def screen_key(im, gamma=1.0, floor=8):
    """Чёрный фон -> прозрачность, свечение сохраняется."""
    rgb = im.convert("RGB")
    r, g, b = rgb.split()
    a = ImageChops.lighter(ImageChops.lighter(r, g), b)
    if gamma != 1.0:
        a = a.point(lambda v: int(255 * (v / 255.0) ** gamma))
    a = a.point(lambda v: 0 if v < floor else v)
    # «распремножение»: цвет = исходный / альфа
    lut = [0] + [min(255, int(255 * 255 / max(1, v))) for v in range(1, 256)]
    r = ImageChops.multiply(r, a.point(lut))
    g = ImageChops.multiply(g, a.point(lut))
    b = ImageChops.multiply(b, a.point(lut))
    out = Image.merge("RGBA", (r, g, b, a))
    return out


def square(im, pad=0.04):
    bbox = im.getbbox()
    if bbox:
        im = im.crop(bbox)
    w, h = im.size
    side = int(max(w, h) * (1 + pad))
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.alpha_composite(im, ((side - w) // 2, (side - h) // 2))
    return canvas


def build():
    src = os.path.join(RAW, "fx-explosion.png")
    if not os.path.exists(src):
        print("нет", src)
        return None
    base = square(screen_key(Image.open(src)))
    d = os.path.join(FILM, "sprites", "explosion")
    os.makedirs(d, exist_ok=True)
    files = []
    for i in range(FRAMES):
        k = (0.52, 0.72, 0.88, 1.0)[i]
        sub = base.resize((max(1, int(SIZE * k)), max(1, int(SIZE * k))), Image.LANCZOS)
        if i == FRAMES - 1:                      # последний кадр притухает
            sub = ImageEnhance.Brightness(sub).enhance(0.82)
            alpha = sub.getchannel("A").point(lambda v: int(v * 0.85))
            sub.putalpha(alpha)
        canvas = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        canvas.alpha_composite(sub, ((SIZE - sub.width) // 2, (SIZE - sub.height) // 2))
        p = os.path.join(d, f"explosion-{i + 1}.png")
        canvas.save(p)
        files.append(p)

    man_path = os.path.join(FILM, "manifest.json")
    man = json.load(open(man_path, encoding="utf-8"))
    man["sprites"] = [s for s in man["sprites"] if s["slug"] != "explosion"]
    man["sprites"].append({
        "slug": "explosion", "name": "Взрыв", "w": SIZE, "h": SIZE,
        "costumes": [{"name": f"кадр-{i + 1}", "file": os.path.relpath(p, FILM)}
                     for i, p in enumerate(files)]})
    json.dump(man, open(man_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("готово:", len(files), "кадра,", SIZE, "×", SIZE)
    return files


if __name__ == "__main__":
    build()
