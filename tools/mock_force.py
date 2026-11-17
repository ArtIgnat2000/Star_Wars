# -*- coding: utf-8 -*-
"""«Скриншоты» «Дагобы: тренировки Силы» → preview/force-*.png.

Координаты — как в Scratch (−240..240, −180..180); размер — как «размер спрайта»
в процентах, точка опоры — центр костюма.
"""
import json
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREV = os.path.join(ROOT, "preview")
FORCE = os.path.join(ROOT, "assets", "force")
MAN = json.load(open(os.path.join(FORCE, "manifest.json"), encoding="utf-8"))
SP = {s["slug"]: s for s in MAN["sprites"]}
BD = {b["slug"]: b for b in MAN["backdrops"]}
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# как в игре
LUKE_SIZE, YODA_SIZE = 52, 55


def costume(slug, name=None):
    cs = SP[slug]["costumes"]
    if name is None:
        return cs[0]
    for c in cs:
        if c["name"] == name:
            return c
    raise KeyError((slug, name))


def place(canvas, slug, x, y, size, name=None):
    c = costume(slug, name)
    im = Image.open(os.path.join(ROOT, c["file"])).convert("RGBA")
    k = size / 100.0
    im = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)
    canvas.alpha_composite(im, (int(240 + x - c["cx"] * k), int(180 - y - c["cy"] * k)))


def bg(slug):
    return Image.open(os.path.join(ROOT, BD[slug]["file"])).convert("RGBA").resize((480, 360))


def monitors(canvas, rocks, lives):
    d = ImageDraw.Draw(canvas)
    f = ImageFont.truetype(FONT_B, 15)
    for text, x in ((f"камни {rocks}", 12), (f"жизни {lives}", 372)):
        d.rounded_rectangle((x, 10, x + 96, 38), radius=14, fill=(38, 108, 74, 235),
                            outline=(10, 46, 30, 255))
        d.text((x + 12, 15), text, font=f, fill=(226, 255, 238))


def play():
    c = bg("swamp")
    place(c, "luke", -165, -72, LUKE_SIZE)
    place(c, "yoda", 185, -108, YODA_SIZE)
    place(c, "rock", 130, 120, 90)
    place(c, "rock", -40, 150, 110)
    place(c, "rock", -20, 10, 100)
    place(c, "ring", -20, 10, 100)          # кольцо держит камень
    place(c, "orb", 90, -40, 100)
    monitors(c, 6, 2)
    return c


def win():
    c = bg("win")
    monitors(c, 10, 3)
    return c


def lose():
    c = bg("lose")
    monitors(c, 4, 0)
    return c


if __name__ == "__main__":
    scenes = [("force-1.png", play()), ("force-2.png", win()), ("force-3.png", lose())]
    ims = []
    for fname, im in scenes:
        rgb = im.convert("RGB")
        rgb.save(os.path.join(PREV, fname))
        ims.append(rgb)
    sheet = Image.new("RGB", (480, 10 + 370 * len(ims)), (8, 18, 14))
    for i, im in enumerate(ims):
        sheet.paste(im, (0, i * 370))
    sheet.save(os.path.join(PREV, "force.png"))
    print("готово: preview/force-1..3.png, preview/force.png")
