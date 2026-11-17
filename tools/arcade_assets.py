# -*- coding: utf-8 -*-
"""Ассеты для аркады «Сбей дроидов» → assets/arcade.

Готовые кинокадры корабля, дроида и взрыва берутся из assets/film,
а здесь рисуются лазерный болт и два финальных фона с подписями.

Запуск: python3 tools/arcade_assets.py
"""
import json
import os
import shutil

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILM = os.path.join(ROOT, "assets", "film")
OUT = os.path.join(ROOT, "assets", "arcade")
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def size_of(rel):
    im = Image.open(os.path.join(ROOT, rel))
    return im.size


def costume(name, rel, w=None, h=None, cx=None, cy=None):
    if w is None:
        w, h = size_of(rel)
    return {"name": name, "file": rel, "w": w, "h": h,
            "cx": w / 2 if cx is None else cx,
            "cy": h / 2 if cy is None else cy}


# ------------------------------------------------------------------ лазер ---
def make_laser():
    """Зелёный болт: белая сердцевина и зелёное свечение вокруг."""
    w, h = 18, 52
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # свечение
    d.rounded_rectangle((1, 2, w - 2, h - 3), radius=7, fill=(60, 255, 120, 90))
    im = im.filter(ImageFilter.GaussianBlur(2.2))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((4, 4, w - 5, h - 5), radius=5, fill=(120, 255, 150, 255))
    d.rounded_rectangle((6, 7, w - 7, h - 8), radius=4, fill=(235, 255, 235, 255))
    path = os.path.join(OUT, "sprites", "laser.png")
    im.save(path)
    return costume("болт", os.path.relpath(path, ROOT), w, h)


# ------------------------------------------------------------------ фоны ----
def plate(im, text, y, size, fill, stroke):
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT_B, size)
    tw = d.textlength(text, font=f)
    d.text(((im.width - tw) / 2, y), text, font=f, fill=fill,
           stroke_width=max(2, size // 18), stroke_fill=stroke)
    return im


def hint(im, text, y=310):
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT_R, 17)
    tw = d.textlength(text, font=f)
    x0 = (im.width - tw) / 2
    d.rounded_rectangle((x0 - 14, y - 6, x0 + tw + 14, y + 26), radius=14,
                        fill=(10, 14, 26, 205))
    d.text((x0, y), text, font=f, fill=(235, 242, 255))
    return im


def make_space():
    src = Image.open(os.path.join(FILM, "backdrops", "space.png")).convert("RGB")
    path = os.path.join(OUT, "backdrops", "space.png")
    src.resize((480, 360), Image.LANCZOS).save(path)
    return {"slug": "space", "name": "Космос", "file": os.path.relpath(path, ROOT)}


def make_win():
    im = Image.open(os.path.join(FILM, "backdrops", "victory.png")).convert("RGB")
    im = im.resize((480, 360), Image.LANCZOS).convert("RGBA")
    # мягкая затемняющая полоса сверху, чтобы подпись читалась
    fade = Image.new("RGBA", im.size, (0, 0, 0, 0))
    fd = ImageDraw.Draw(fade)
    for y in range(150):
        fd.line((0, y, 480, y), fill=(14, 9, 4, int(170 * (1 - y / 150) ** 1.4)))
    im.alpha_composite(fade)
    plate(im, "ПОБЕДА!", 40, 58, (255, 226, 96), (58, 34, 4))
    hint(im, "новый бой начнётся сам", 108)
    path = os.path.join(OUT, "backdrops", "win.png")
    im.convert("RGB").save(path)
    return {"slug": "win", "name": "Победа", "file": os.path.relpath(path, ROOT)}


def make_lose():
    im = Image.open(os.path.join(FILM, "backdrops", "space.png")).convert("RGB")
    im = im.resize((480, 360), Image.LANCZOS).convert("RGBA")
    # красноватая дымка, чтобы экран поражения отличался
    veil = Image.new("RGBA", im.size, (120, 10, 20, 90))
    im.alpha_composite(veil)
    im = im.filter(ImageFilter.GaussianBlur(0.6))
    plate(im, "ПОРАЖЕНИЕ", 52, 52, (255, 120, 110), (40, 4, 8))
    hint(im, "и попробуем ещё раз", 126)
    path = os.path.join(OUT, "backdrops", "lose.png")
    im.convert("RGB").save(path)
    return {"slug": "lose", "name": "Поражение", "file": os.path.relpath(path, ROOT)}


def main():
    os.makedirs(os.path.join(OUT, "sprites"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "backdrops"), exist_ok=True)

    laser = make_laser()
    ship = [costume("двигатель-%d" % i,
                    "assets/film/sprites/naboo-fighter/naboo-fighter-%d.png" % i)
            for i in (1, 2, 3)]
    droid = [costume("дроид", "assets/film/sprites/droid-fighter/droid-fighter-1.png")]
    for i in (1, 2, 3):
        droid.append(costume("взрыв-%d" % i,
                             "assets/film/sprites/explosion/explosion-%d.png" % i))

    backdrops = [make_space(), make_win(), make_lose()]
    man = {"sprites": [{"slug": "korabl", "name": "Корабль", "costumes": ship},
                       {"slug": "droid", "name": "Дроид", "costumes": droid},
                       {"slug": "laser", "name": "Лазер", "costumes": [laser]}],
           "backdrops": backdrops}
    json.dump(man, open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("готово: assets/arcade (лазер, 3 фона, манифест)")


if __name__ == "__main__":
    main()
