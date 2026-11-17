# -*- coding: utf-8 -*-
"""«Скриншоты» лёгкой версии (assets/lite) → preview/duel-lite-1.png и -2.png."""
import json
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREV = os.path.join(ROOT, "preview")
LITE = os.path.join(ROOT, "assets", "lite")
MAN = json.load(open(os.path.join(LITE, "manifest.json"), encoding="utf-8"))
SP = {s["slug"]: s for s in MAN["sprites"]}
BD = {b["slug"]: b for b in MAN["backdrops"]}


def costume(slug, name):
    s = SP[slug]
    for c in s["costumes"]:
        if c["name"] == name:
            return Image.open(os.path.join(ROOT, c["file"])).convert("RGBA")
    raise KeyError((slug, name))


def place(canvas, img, sx, sy, pct):
    k = pct / 100.0
    im = img.resize((max(1, int(img.width * k)), max(1, int(img.height * k))), Image.LANCZOS)
    canvas.alpha_composite(im, (int(240 + sx - im.width / 2), int(180 - sy - im.height / 2)))


def bg(slug):
    return Image.open(os.path.join(ROOT, BD[slug]["file"])).convert("RGBA").resize((480, 360))


def title():
    c = bg("choice")
    place(c, costume("quigon", "стойка"), -110, -10, 31)
    place(c, costume("obiwan", "стойка"), 110, -10, 31)
    place(c, costume("arrow", "стрелка"), -110, 88, 60)
    return c


def duel():
    c = bg("duel")
    place(c, costume("obiwan", "атака"), -110, -40, 37)
    place(c, costume("maul", "блок"), 130, -40, 37)
    spark = Image.open(os.path.join(ROOT, "preview", "png", "sprite-sparks-02.png")).convert("RGBA")
    place(c, spark, 10, -10, 22)
    return c


if __name__ == "__main__":
    a = title().convert("RGB")
    a.save(os.path.join(PREV, "duel-lite-1.png"))
    b = duel().convert("RGB")
    b.save(os.path.join(PREV, "duel-lite-2.png"))
    s = Image.new("RGB", (480, 730), (10, 10, 16))
    s.paste(a, (0, 0))
    s.paste(b, (0, 370))
    s.save(os.path.join(PREV, "duel-lite.png"))
    print("готово: preview/duel-lite-1.png, duel-lite-2.png, duel-lite.png")
