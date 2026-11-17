# -*- coding: utf-8 -*-
"""Ассеты для игры «Побег со „Звезды Смерти“» → assets/escape.

* Люк (два кадра бега), ящик и дроид вырезаются с хромакея
  (assets/raw/escape-*.png) и приводятся к одному росту;
* коридор и ангар с «Соколом» — кинокадры, обрезанные в 4:3 до 480×360;
* экран «ПОЙМАЛИ» рисуется из того же коридора (красная подсветка + подпись);
* энергоячейка (бонус +1 жизнь) рисуется кодом — она абстрактная, картинка
  из генератора ей не нужна.

Запуск: python3 tools/escape_assets.py
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cutout import cutout                      # noqa: E402
from gen_sounds import write_wav               # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "assets", "raw")
OUT = os.path.join(ROOT, "assets", "escape")
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

LUKE_H = 300      # рост Люка в пикселях костюма (на экране — 120)
OBST_H = 70       # ящик и дроид одной высоты: стоят на полу без подгонки
CELL_H = 96       # энергоячейка


def sprite(name, rel, w, h, cx=None, cy=None):
    return {"name": name, "file": rel, "w": w, "h": h,
            "cx": w / 2 if cx is None else cx, "cy": h / 2 if cy is None else cy}


def cut(src, dst, target_h):
    cutout(os.path.join(RAW, src), dst, target_h=target_h, verbose=False)
    w, h = Image.open(dst).size
    return sprite(os.path.splitext(os.path.basename(dst))[0], os.path.relpath(dst, ROOT), w, h)


# ------------------------------------------------------------------ спрайты --
def make_luke():
    d = os.path.join(OUT, "sprites")
    a = cut("escape-luke.png", os.path.join(d, "luke-run1.png"), LUKE_H)
    b = cut("escape-luke2.png", os.path.join(d, "luke-run2.png"), LUKE_H)
    a["name"], b["name"] = "бег-1", "бег-2"
    return [a, b]


def make_obstacles():
    d = os.path.join(OUT, "sprites")
    a = cut("escape-crate.png", os.path.join(d, "crate.png"), OBST_H)
    b = cut("escape-droid.png", os.path.join(d, "droid.png"), OBST_H)
    a["name"], b["name"] = "ящик", "дроид"
    return [a, b]


def make_cell():
    """Энергоячейка: синий светящийся цилиндр с обоймой — бонус за прыжок."""
    w, h = 54, CELL_H
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for i, r in enumerate(range(26, 8, -3)):
        a = int(16 + i * 7)
        gd.rounded_rectangle((w / 2 - 11 - r / 2, h / 2 - r, w / 2 + 11 + r / 2, h / 2 + r),
                             radius=r, fill=(80, 190, 255, a))
    glow = glow.filter(ImageFilter.GaussianBlur(4))
    im.alpha_composite(glow)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((12, 14, w - 12, h - 14), radius=12, fill=(24, 96, 150, 255),
                        outline=(150, 230, 255, 255), width=2)
    d.rounded_rectangle((17, 24, w - 17, h - 24), radius=8, fill=(120, 225, 255, 235))
    d.rounded_rectangle((21, 30, w - 21, h - 46), radius=6, fill=(230, 250, 255, 220))
    # обоймы сверху и снизу
    for yy in (8, h - 18):
        d.rounded_rectangle((14, yy, w - 14, yy + 10), radius=4, fill=(60, 72, 84, 255),
                            outline=(150, 165, 180, 255))
    p = os.path.join(OUT, "sprites", "cell.png")
    im.save(p)
    return sprite("ячейка", os.path.relpath(p, ROOT), w, h)


# ------------------------------------------------------------------ фоны ----
def frame(rel):
    im = Image.open(os.path.join(RAW, rel)).convert("RGB")
    w, h = im.size
    nw = int(h * 4 / 3)
    return im.crop(((w - nw) // 2, 0, (w + nw) // 2, h)).resize((480, 360), Image.LANCZOS)


def plate(im, text, y, size, fill, stroke):
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT_B, size)
    tw = d.textlength(text, font=f)
    d.text(((im.width - tw) / 2, y), text, font=f, fill=fill,
           stroke_width=max(2, size // 18), stroke_fill=stroke)
    return im


def hint(im, text, y):
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT_R, 17)
    tw = d.textlength(text, font=f)
    x0 = (im.width - tw) / 2
    d.rounded_rectangle((x0 - 14, y - 6, x0 + tw + 14, y + 26), radius=14,
                        fill=(12, 16, 24, 210))
    d.text((x0, y), text, font=f, fill=(226, 240, 255))
    return im


def make_backdrops():
    out = []
    p = os.path.join(OUT, "backdrops", "corridor.png")
    frame("escape-corridor.png").save(p)
    out.append({"slug": "corridor", "name": "Коридор", "file": os.path.relpath(p, ROOT)})

    win = frame("escape-hangar.png").convert("RGBA")
    win = Image.blend(win, Image.new("RGBA", win.size, (10, 30, 60, 255)), 0.06)
    plate(win, "ПОБЕГ УДАЛСЯ!", 34, 50, (140, 240, 255), (4, 20, 40))
    hint(win, "«Сокол» уходит с базы", 100)
    p = os.path.join(OUT, "backdrops", "win.png")
    win.convert("RGB").save(p)
    out.append({"slug": "win", "name": "Ангар", "file": os.path.relpath(p, ROOT)})

    lose = frame("escape-corridor.png").convert("RGBA")
    lose.alpha_composite(Image.new("RGBA", lose.size, (170, 20, 20, 110)))
    lose = lose.filter(ImageFilter.GaussianBlur(0.8))
    plate(lose, "ПОЙМАЛИ", 46, 58, (255, 170, 150), (40, 4, 4))
    hint(lose, "попробуй убежать ещё раз", 124)
    p = os.path.join(OUT, "backdrops", "lose.png")
    lose.convert("RGB").save(p)
    out.append({"slug": "lose", "name": "Поймали", "file": os.path.relpath(p, ROOT)})
    return out


# ------------------------------------------------------------------ звук ----
def make_chime():
    """Короткий «блип» — взял энергоячейку."""
    import math
    dur = 0.28
    n = int(dur * 44100)
    out = []
    ph1 = ph2 = 0.0
    for i in range(n):
        t = i / 44100
        f = 880 if t < 0.09 else 1320
        ph1 += 2 * math.pi * f / 44100
        ph2 += 2 * math.pi * (f * 2) / 44100
        env = min(1.0, t * 60) * max(0.0, 1.0 - (t / dur) ** 1.6)
        out.append((math.sin(ph1) * 0.6 + math.sin(ph2) * 0.25) * env * 0.7)
    path, _ = write_wav("блип.wav", out)
    return os.path.relpath(path, ROOT)


def main():
    os.makedirs(os.path.join(OUT, "sprites"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "backdrops"), exist_ok=True)
    man = {"sprites": [{"slug": "luke", "name": "Люк", "costumes": make_luke()},
                       {"slug": "obstacle", "name": "Препятствие", "costumes": make_obstacles()},
                       {"slug": "cell", "name": "Ячейка", "costumes": [make_cell()]}],
           "backdrops": make_backdrops()}
    json.dump(man, open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    snd = make_chime()
    print("готово: assets/escape +", snd)
    for s in man["sprites"]:
        for c in s["costumes"]:
            print(f"  {s['name']} / {c['name']}: {c['w']}×{c['h']}")


if __name__ == "__main__":
    main()
