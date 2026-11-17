# -*- coding: utf-8 -*-
"""Постер кинематографичной версии (PIL-композиция из готовых ассетов)."""
import json
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter, ImageEnhance

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILM = os.path.join(ROOT, "assets", "film")
PREV = os.path.join(ROOT, "preview")
RAW = os.path.join(ROOT, "assets", "raw")
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
W, H = 1600, 900

MAN = json.load(open(os.path.join(FILM, "manifest.json"), encoding="utf-8"))
FS = {s["slug"]: s for s in MAN["sprites"]}


def sprite(slug, idx=0):
    return Image.open(os.path.join(FILM, FS[slug]["costumes"][idx]["file"])).convert("RGBA")


def fit_h(img, h, mirror=False, angle=0):
    im = ImageOps.mirror(img) if mirror else img
    k = h / im.height
    im = im.resize((int(im.width * k), h), Image.LANCZOS)
    if angle:
        im = im.rotate(angle, expand=True, resample=Image.BICUBIC)
    return im


def paste_feet(canvas, im, cx, feet_y):
    canvas.alpha_composite(im, (int(cx - im.width / 2), int(feet_y - im.height)))


def main():
    # фон: орбита Набу, кадрируем под 16:9
    bg = Image.open(os.path.join(RAW, "bd-space.png")).convert("RGB")
    w, h = bg.size
    nw = int(h * W / H)
    bg = bg.crop(((w - nw) // 2, 0, (w + nw) // 2, h)).resize((W, H), Image.LANCZOS)
    bg = ImageEnhance.Brightness(bg).enhance(0.9)
    canvas = bg.convert("RGBA")

    # мягкий тёплый свет за фигурами
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dg = ImageDraw.Draw(glow)
    dg.ellipse([W * 0.28, H * 0.42, W * 0.78, H * 0.98], fill=(255, 150, 70, 60))
    glow = glow.filter(ImageFilter.GaussianBlur(140))
    canvas.alpha_composite(glow)

    # корабли
    fighter = fit_h(sprite("naboo-fighter", 2), 230, angle=18)
    canvas.alpha_composite(fighter, (1300, 96))
    droid = fit_h(sprite("droid-fighter"), 130)
    canvas.alpha_composite(droid, (170, 210))

    # персонажи (стоят на одной линии)
    feet = 862
    paste_feet(canvas, fit_h(sprite("quigon", 1), 505), 330, feet - 20)
    paste_feet(canvas, fit_h(sprite("obiwan", 1), 545), 720, feet)
    paste_feet(canvas, fit_h(sprite("maul", 0), 525, mirror=True), 1360, feet - 10)

    # световые мечи подсвечиваем лёгким bloom
    bloom = canvas.filter(ImageFilter.GaussianBlur(12))
    canvas = Image.blend(canvas, bloom, 0.18).convert("RGBA")

    d = ImageDraw.Draw(canvas)
    # заголовок
    f1 = ImageFont.truetype(FONT_B, 132)
    f2 = ImageFont.truetype(FONT_B, 62)
    f3 = ImageFont.truetype(FONT_R, 30)
    title = "STAR WARS"
    tw = d.textlength(title, font=f1)
    d.text(((W - tw) / 2, 60), title, font=f1, fill=(255, 224, 77),
           stroke_width=7, stroke_fill=(28, 18, 4))
    sub = "ДУЭЛЬ НА НАБУ"
    tw2 = d.textlength(sub, font=f2)
    d.text(((W - tw2) / 2, 214), sub, font=f2, fill=(235, 242, 255),
           stroke_width=6, stroke_fill=(10, 16, 30))
    sub2 = "СПРАЙТЫ И ФОНЫ ДЛЯ SCRATCH 3.0"
    tw3 = d.textlength(sub2, font=f3)
    d.text(((W - tw3) / 2, 292), sub2, font=f3, fill=(186, 203, 230),
           stroke_width=4, stroke_fill=(8, 12, 24))

    # нижняя плашка
    d.rectangle([0, 828, W, H], fill=(6, 9, 16, 190))
    f4 = ImageFont.truetype(FONT_R, 27)
    line = "Квай-Гон Джинн · Оби-Ван Кеноби · Дарт Мол · N-1 · дроид-истребитель · Набу"
    tw4 = d.textlength(line, font=f4)
    d.text(((W - tw4) / 2, 850), line, font=f4, fill=(205, 216, 236))

    canvas.convert("RGB").save(os.path.join(PREV, "poster.png"))
    print("готово: preview/poster.png", canvas.size)


if __name__ == "__main__":
    main()
