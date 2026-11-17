# -*- coding: utf-8 -*-
"""«Скриншоты» уровней из готовых ассетов (кинематографичная версия)."""
import json
import os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREV = os.path.join(ROOT, "preview")
FILM = os.path.join(ROOT, "assets", "film")
VEC = os.path.join(ROOT, "assets")
FM = json.load(open(os.path.join(FILM, "manifest.json"), encoding="utf-8"))
VM = json.load(open(os.path.join(VEC, "manifest.json"), encoding="utf-8"))
FS = {s["slug"]: s for s in FM["sprites"]}
FB = {b["slug"]: b for b in FM["backdrops"]}
VS = {s["slug"]: s for s in VM["sprites"]}
VB = {b["slug"]: b for b in VM["backdrops"]}


def film(slug, idx=0):
    s = FS[slug]
    return Image.open(os.path.join(FILM, s["costumes"][idx]["file"])).convert("RGBA")


def vec(slug, idx=0):
    """Векторные эффекты берём из готовых PNG-рендеров."""
    p = os.path.join(PREV, "png", f"sprite-{slug}-{idx+1:02d}.png")
    if os.path.exists(p):
        return Image.open(p).convert("RGBA")
    s = VS[slug]
    return Image.open(os.path.join(VEC, s["costumes"][idx]["file"])).convert("RGBA")


def place(canvas, img, sx, sy, size_percent):
    w = img.width * size_percent / 100.0
    h = img.height * size_percent / 100.0
    im = img.resize((max(1, int(w)), max(1, int(h))), Image.LANCZOS)
    canvas.alpha_composite(im, (int(240 + sx - im.width / 2), int(180 - sy - im.height / 2)))


def bg_film(slug):
    return Image.open(os.path.join(FILM, FB[slug]["file"])).convert("RGBA").resize((480, 360))


def bg_vec(slug):
    p = os.path.join(PREV, "png", f"backdrop-{slug}.png")
    return Image.open(p).convert("RGBA").resize((480, 360))


def label(img, text):
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    d.rectangle([0, 0, 480, 24], fill=(6, 8, 14, 200))
    d.text((10, 4), text, font=font, fill=(235, 242, 255))
    return img


def level1():
    c = bg_film("space")
    place(c, film("droid-fighter"), 70, 110, 20)
    place(c, film("droid-fighter"), -150, 40, 20)
    place(c, film("droid-fighter"), 180, 150, 20)
    place(c, vec("explosion", 1), -150, 30, 55)
    place(c, vec("enemy-laser", 0), 70, 70, 100)
    place(c, vec("enemy-laser", 0), -150, 5, 100)
    place(c, vec("laser", 0), -20, -30, 100)
    place(c, vec("laser", 0), 24, 20, 100)
    place(c, film("naboo-fighter", 2), 0, -110, 36)
    return label(c, "Уровень 1 · орбита Набу · очки 30 · жизни 3")


def level2():
    c = bg_vec("04-generator")
    place(c, vec("plasma-gate", 0), -205, -60, 60)
    place(c, film("obiwan", 1), 5, -40, 37)
    place(c, vec("sparks", 1), 92, -5, 70)
    place(c, film("maul"), 130, -40, 37)
    return label(c, "Уровень 2 · генераторная · Оби-Ван против Дарта Мола")


if __name__ == "__main__":
    level1().convert("RGB").save(os.path.join(PREV, "gameplay-1.png"))
    level2().convert("RGB").save(os.path.join(PREV, "gameplay-2.png"))
    a = Image.open(os.path.join(PREV, "gameplay-1.png"))
    b = Image.open(os.path.join(PREV, "gameplay-2.png"))
    s = Image.new("RGB", (480, 730), (10, 10, 16))
    s.paste(a, (0, 0))
    s.paste(b, (0, 370))
    s.save(os.path.join(PREV, "gameplay.png"))
    print("готово: preview/gameplay-1.png, gameplay-2.png")
