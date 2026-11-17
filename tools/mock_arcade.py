# -*- coding: utf-8 -*-
"""«Скриншоты» аркады «Сбей дроидов» → preview/arcade-*.png.

Координаты — как в Scratch (−240..240, −180..180), точка опоры костюма
совпадает с центром вращения в проекте.
"""
import json
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREV = os.path.join(ROOT, "preview")
ARC = os.path.join(ROOT, "assets", "arcade")
MAN = json.load(open(os.path.join(ARC, "manifest.json"), encoding="utf-8"))
SP = {s["slug"]: s for s in MAN["sprites"]}
BD = {b["slug"]: b for b in MAN["backdrops"]}
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def costume(slug, name):
    for c in SP[slug]["costumes"]:
        if c["name"] == name:
            return c
    raise KeyError((slug, name))


def place(canvas, slug, name, x, y, size, glow=0.0):
    c = costume(slug, name)
    im = Image.open(os.path.join(ROOT, c["file"])).convert("RGBA")
    k = size / 100.0
    im = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)
    if glow:
        im.putalpha(im.getchannel("A").point(lambda v: int(v * glow)))
    px = int(240 + x - c["cx"] * k)
    py = int(180 - y - c["cy"] * k)
    canvas.alpha_composite(im, (px, py))


def bg(slug):
    return Image.open(os.path.join(ROOT, BD[slug]["file"])).convert("RGBA").resize((480, 360))


def monitors(canvas, score, lives):
    d = ImageDraw.Draw(canvas)
    f = ImageFont.truetype(FONT_B, 15)
    for text, x in ((f"очки {score}", 12), (f"жизни {lives}", 372)):
        d.rounded_rectangle((x, 10, x + 96, 38), radius=14, fill=(255, 140, 26, 235),
                            outline=(120, 60, 8, 255))
        d.text((x + 12, 15), text, font=f, fill=(30, 14, 0))


def play():
    c = bg("space")
    place(c, "korabl", "двигатель-1", -60, -118, 40)
    place(c, "droid", "дроид", 110, 95, 40)
    place(c, "droid", "дроид", -150, 30, 40)
    # дроид над кораблём только что сбит: искры вместо дроида
    place(c, "droid", "взрыв-2", -60, 30, 55)
    place(c, "laser", "болт", -60, -35, 100)
    monitors(c, 3, 4)
    return c


def win_screen():
    c = bg("win")
    place(c, "korabl", "двигатель-3", 0, -118, 40)
    monitors(c, 8, 5)
    return c


def lose_screen():
    c = bg("lose")
    place(c, "korabl", "двигатель-2", 40, -118, 40)
    monitors(c, 2, 0)
    return c


if __name__ == "__main__":
    scenes = [("arcade-1.png", play()), ("arcade-2.png", win_screen()),
              ("arcade-3.png", lose_screen())]
    ims = []
    for fname, im in scenes:
        rgb = im.convert("RGB")
        rgb.save(os.path.join(PREV, fname))
        ims.append(rgb)
    sheet = Image.new("RGB", (480, 10 + 370 * len(ims)), (8, 10, 18))
    for i, im in enumerate(ims):
        sheet.paste(im, (0, i * 370))
    sheet.save(os.path.join(PREV, "arcade.png"))
    print("готово: preview/arcade-1..3.png, preview/arcade.png")
