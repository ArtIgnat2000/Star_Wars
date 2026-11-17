# -*- coding: utf-8 -*-
"""«Скриншоты» лёгкой версии (assets/lite) → preview/duel-lite-*.png.

Позиции считаются так же, как в Scratch: центр вращения костюма — стопы,
поэтому персонаж стоит на нужной линии пола при любом размере холста.
"""
import json
import os

from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREV = os.path.join(ROOT, "preview")
LITE = os.path.join(ROOT, "assets", "lite")
MAN = json.load(open(os.path.join(LITE, "manifest.json"), encoding="utf-8"))
SP = {s["slug"]: s for s in MAN["sprites"]}
BD = {b["slug"]: b for b in MAN["backdrops"]}
PATH = {b["slug"]: b["file"] for b in MAN["backdrops"]}


def costume(slug, name):
    s = SP[slug]
    for c in s["costumes"]:
        if c["name"] == name:
            return c
    raise KeyError((slug, name))


def place(canvas, slug, name, x, y, pct, mirror=False):
    """x, y — положение стоп в координатах сцены Scratch (−240..240, −180..180)."""
    c = costume(slug, name)
    im = Image.open(os.path.join(ROOT, c["file"])).convert("RGBA")
    if mirror:
        im = ImageOps.mirror(im)
    k = pct / 100.0
    im = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)
    cx = (c["w"] - c["cx"] if mirror else c["cx"]) * k
    cy = c["cy"] * k
    canvas.alpha_composite(im, (int(240 + x - cx), int(180 - y - cy)))


def bg(slug):
    return Image.open(os.path.join(ROOT, PATH[slug])).convert("RGBA").resize((480, 360))


def title():
    c = bg("choice")
    place(c, "quigon", "стойка", -110, -68, 31)
    place(c, "obiwan", "стойка", 110, -68, 31)
    place(c, "arrow", "стрелка", -110, 88, 60)
    return c


def duel():
    c = bg("duel")
    place(c, "obiwan", "атака", -110, -115, 37)
    place(c, "maul", "атака", 55, -115, 37, mirror=True)
    place(c, "ring", "2", -20, -30, 40)
    flash = costume("flash", "2")
    im = Image.open(os.path.join(ROOT, flash["file"])).convert("RGBA")
    im = im.resize((int(im.width * 0.5), int(im.height * 0.5)), Image.LANCZOS)
    c.alpha_composite(im, (int(240 - 20 - im.width / 2), int(180 + 35 - im.height / 2)))
    return c


def walk():
    """Герой идёт (кадр «шаг-1»), Мол подходит к нему."""
    c = bg("duel")
    place(c, "quigon", "шаг-1", -130, -115, 37)
    place(c, "maul", "шаг-2", 110, -115, 37, mirror=True)
    return c


def block():
    """Герой закрылся, Мол рубит — клинки встретились, летит кольцо."""
    c = bg("duel")
    place(c, "obiwan", "блок", -110, -115, 37)
    place(c, "maul", "атака", 55, -115, 37, mirror=True)
    place(c, "ring", "1", -25, -30, 45)
    return c


def victory():
    """Победа: герой поднял меч, Мол растворяется."""
    c = bg("win")
    place(c, "obiwan", "победа", -110, -115, 37)
    m = costume("maul", "ранен")
    im = Image.open(os.path.join(ROOT, m["file"])).convert("RGBA")
    im = ImageOps.mirror(im)
    k = 0.37
    im = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
    im.putalpha(im.getchannel("A").point(lambda v: int(v * 0.25)))
    c.alpha_composite(im, (int(240 + 55 - im.width / 2), int(180 + 115 - im.height + 4)))
    return c


if __name__ == "__main__":
    scenes = [("duel-lite-1.png", title(), "титул"),
              ("duel-lite-2.png", duel(), "удар"),
              ("duel-lite-3.png", walk(), "ходьба"),
              ("duel-lite-4.png", block(), "блок"),
              ("duel-lite-5.png", victory(), "победа")]
    ims = []
    for fname, im, _ in scenes:
        rgb = im.convert("RGB")
        rgb.save(os.path.join(PREV, fname))
        ims.append(rgb)
    sheet = Image.new("RGB", (480, 10 + 370 * len(ims)), (10, 10, 16))
    for i, im in enumerate(ims):
        sheet.paste(im, (0, i * 370))
    sheet.save(os.path.join(PREV, "duel-lite.png"))
    print("готово:", ", ".join(os.path.join("preview", f) for f, _, _ in scenes),
          "+ duel-lite.png")
