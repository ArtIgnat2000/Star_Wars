# -*- coding: utf-8 -*-
"""«Скриншоты» «Гонок на подах» → preview/podrace-*.png.

Координаты — как в Scratch (−240..240, −180..180); размер — как «размер спрайта»
в процентах, точка опоры — центр костюма.
"""
import json
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREV = os.path.join(ROOT, "preview")
POD = os.path.join(ROOT, "assets", "pod")
MAN = json.load(open(os.path.join(POD, "manifest.json"), encoding="utf-8"))
SP = {s["slug"]: s for s in MAN["sprites"]}
BD = {b["slug"]: b for b in MAN["backdrops"]}
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def costume(slug, name):
    for c in SP[slug]["costumes"]:
        if c["name"] == name:
            return c
    raise KeyError((slug, name))


def place(canvas, slug, name, x, y, size, mirror=False):
    c = costume(slug, name)
    im = Image.open(os.path.join(ROOT, c["file"])).convert("RGBA")
    k = size / 100.0
    im = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)
    if mirror:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    px = int(240 + x - c["cx"] * k)
    py = int(180 - y - c["cy"] * k)
    canvas.alpha_composite(im, (px, py))


def bg(slug):
    return Image.open(os.path.join(ROOT, BD[slug]["file"])).convert("RGBA").resize((480, 360))


def monitors(canvas, meters, lives):
    d = ImageDraw.Draw(canvas)
    f = ImageFont.truetype(FONT_B, 15)
    for text, x in ((f"метры {meters}", 12), (f"жизни {lives}", 372)):
        d.rounded_rectangle((x, 10, x + 96, 38), radius=14, fill=(255, 140, 26, 235),
                            outline=(120, 60, 8, 255))
        d.text((x + 12, 15), text, font=f, fill=(30, 14, 0))


def race():
    c = bg("track")
    place(c, "rock", "скала", 170, 70, 17)
    place(c, "rock", "скала", 60, -85, 14, mirror=True)
    place(c, "rock", "скала", -30, 100, 18)
    place(c, "pod", "под", -105, -40, 18)
    monitors(c, 128, 3)
    return c


def finish():
    c = bg("win")
    place(c, "pod", "под", -105, -40, 18)
    monitors(c, 400, 4)
    return c


def crash():
    c = bg("lose")
    place(c, "rock", "скала", 20, -20, 20)
    place(c, "pod", "под", -105, -40, 18)
    monitors(c, 96, 0)
    return c


if __name__ == "__main__":
    scenes = [("podrace-1.png", race()), ("podrace-2.png", finish()),
              ("podrace-3.png", crash())]
    ims = []
    for fname, im in scenes:
        rgb = im.convert("RGB")
        rgb.save(os.path.join(PREV, fname))
        ims.append(rgb)
    sheet = Image.new("RGB", (480, 10 + 370 * len(ims)), (24, 16, 8))
    for i, im in enumerate(ims):
        sheet.paste(im, (0, i * 370))
    sheet.save(os.path.join(PREV, "podrace.png"))
    print("готово: preview/podrace-1..3.png, preview/podrace.png")
