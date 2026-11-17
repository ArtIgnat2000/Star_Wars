# -*- coding: utf-8 -*-
"""Собирает «скриншоты» уровней из готовых PNG-костюмов (проверка пропорций)."""
import json
import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREV = os.path.join(ROOT, "preview")
MAN = json.load(open(os.path.join(ROOT, "assets", "manifest.json"), encoding="utf-8"))
SPR = {s["slug"]: s for s in MAN["sprites"]}
BD = {b["slug"]: b for b in MAN["backdrops"]}


def costume_png(slug, index):
    return Image.open(os.path.join(PREV, "png", f"sprite-{slug}-{index+1:02d}.png")).convert("RGBA")


def place(canvas, img, sx, sy, size_percent):
    """sx, sy — координаты Scratch (центр спрайта), size_percent — размер в %."""
    w = img.width * size_percent / 100.0 / 2.0   # PNG отрендерен в 2x
    h = img.height * size_percent / 100.0 / 2.0
    im = img.resize((max(1, int(w)), max(1, int(h))), Image.LANCZOS)
    px = int(240 + sx - im.width / 2)
    py = int(180 - sy - im.height / 2)
    canvas.alpha_composite(im, (px, py))


def backdrop(slug):
    im = Image.open(os.path.join(PREV, "png", f"backdrop-{slug}.png")).convert("RGB")
    return im.resize((480, 360), Image.LANCZOS).convert("RGBA")


def label(img, text):
    from PIL import ImageDraw, ImageFont
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
    d.rectangle([0, 0, 480, 26], fill=(8, 10, 18, 190))
    d.text((10, 5), text, font=font, fill=(240, 245, 255))
    return img


def level1():
    c = backdrop("02-space")
    place(c, costume_png("droid-fighter", 0), 60, 110, 42)
    place(c, costume_png("droid-fighter", 0), -140, 40, 42)
    place(c, costume_png("droid-fighter", 1), 175, 150, 42)
    place(c, costume_png("explosion", 1), -140, 25, 58)
    place(c, costume_png("enemy-laser", 0), 60, 70, 100)
    place(c, costume_png("enemy-laser", 0), -140, 10, 100)
    place(c, costume_png("laser", 0), -18, -30, 100)
    place(c, costume_png("laser", 0), 26, 20, 100)
    place(c, costume_png("naboo-fighter", 1), 0, -110, 55)
    return label(c, "Уровень 1 · космос над Набу · очки 30 · жизни 3")


def level2():
    c = backdrop("04-generator")
    place(c, costume_png("plasma-gate", 0), -205, -60, 60)
    place(c, costume_png("obiwan", 7), 10, -45, 70)     # удар-1
    place(c, costume_png("sparks", 1), 95, -10, 70)
    place(c, costume_png("maul", 8), 130, -45, 70)      # блок
    return label(c, "Уровень 2 · генераторная · Оби-Ван против Дарта Мола")


if __name__ == "__main__":
    level1().convert("RGB").save(os.path.join(PREV, "gameplay-1.png"))
    level2().convert("RGB").save(os.path.join(PREV, "gameplay-2.png"))
    print("готово: preview/gameplay-1.png, preview/gameplay-2.png")
