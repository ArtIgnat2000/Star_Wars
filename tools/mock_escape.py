# -*- coding: utf-8 -*-
"""«Скриншоты» «Побега со „Звезды Смерти“» → preview/escape-*.png.

Координаты — как в Scratch (−240..240, −180..180); размер — как «размер спрайта»
в процентах, точка опоры — центр костюма.
"""
import json
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREV = os.path.join(ROOT, "preview")
ESC = os.path.join(ROOT, "assets", "escape")
MAN = json.load(open(os.path.join(ESC, "manifest.json"), encoding="utf-8"))
SP = {s["slug"]: s for s in MAN["sprites"]}
BD = {b["slug"]: b for b in MAN["backdrops"]}
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# как в игре: Люк 43 %, ящик и дроид 100 %, пол на y = −160
LUKE_SIZE = 43


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


def monitors(canvas, meters, lives):
    d = ImageDraw.Draw(canvas)
    f = ImageFont.truetype(FONT_B, 15)
    for text, x in ((f"метры {meters}", 12), (f"жизни {lives}", 372)):
        d.rounded_rectangle((x, 10, x + 96, 38), radius=14, fill=(60, 150, 235, 235),
                            outline=(16, 44, 84, 255))
        d.text((x + 12, 15), text, font=f, fill=(240, 250, 255))


def run():
    c = bg("corridor")
    place(c, "cell", 20, 40, 100)
    place(c, "obstacle", 100, -125, 100, "ящик")
    place(c, "obstacle", 190, -125, 100, "дроид")
    place(c, "luke", -150, -96 + 40, LUKE_SIZE, "бег-2")   # Люк в прыжке над ящиком
    monitors(c, 128, 3)
    return c


def win():
    c = bg("win")
    monitors(c, 300, 3)
    return c


def caught():
    c = bg("lose")
    monitors(c, 96, 0)
    return c


if __name__ == "__main__":
    scenes = [("escape-1.png", run()), ("escape-2.png", win()), ("escape-3.png", caught())]
    ims = []
    for fname, im in scenes:
        rgb = im.convert("RGB")
        rgb.save(os.path.join(PREV, fname))
        ims.append(rgb)
    sheet = Image.new("RGB", (480, 10 + 370 * len(ims)), (10, 14, 22))
    for i, im in enumerate(ims):
        sheet.paste(im, (0, i * 370))
    sheet.save(os.path.join(PREV, "escape.png"))
    print("готово: preview/escape-1..3.png, preview/escape.png")
