# -*- coding: utf-8 -*-
"""Ассеты для игры «Дагоба: тренировка Силы» → assets/force.

* Люк, Йода и камни вырезаются с хромакея (assets/raw/force-*.png);
* болото и кадр с поднятым истребителем — кинокадры 4:3 → 480×360;
* кольцо «Сила» рисуется кодом: зелёный ободок со свечением;
* звуки «сила» (камень уходит вверх) и «всплеск» (камень утонул) синтезируются.

Запуск: python3 tools/force_assets.py
"""
import json
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cutout import cutout                      # noqa: E402
from gen_sounds import write_wav              # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "assets", "raw")
OUT = os.path.join(ROOT, "assets", "force")
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SR = 44100

LUKE_H = 300      # на экране 156 px (размер 52 %)
YODA_H = 150
ROCK_H = 70
RING = 110        # диаметр кольца «Сила»


def sprite(name, rel, w, h, cx=None, cy=None):
    return {"name": name, "file": rel, "w": w, "h": h,
            "cx": w / 2 if cx is None else cx, "cy": h / 2 if cy is None else cy}


def cut(src, dst, target_h, name):
    cutout(os.path.join(RAW, src), dst, target_h=target_h, verbose=False)
    w, h = Image.open(dst).size
    return sprite(name, os.path.relpath(dst, ROOT), w, h)


# ------------------------------------------------------------------ спрайты --
def make_sprites():
    d = os.path.join(OUT, "sprites")
    return ([cut("force-luke.png", os.path.join(d, "luke.png"), LUKE_H, "Люк")],
            [cut("force-yoda.png", os.path.join(d, "yoda.png"), YODA_H, "Йода")],
            [cut("force-rock.png", os.path.join(d, "rock.png"), ROCK_H, "камень")])


def make_ring():
    """Кольцо «Сила»: яркий зелёный ободок и мягкое свечение вокруг."""
    w = h = RING
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for i in range(10):
        r = 44 - i * 3
        gd.ellipse((w / 2 - r, h / 2 - r, w / 2 + r, h / 2 + r),
                   outline=(120, 255, 170, 40 + i * 12), width=4)
    glow = glow.filter(ImageFilter.GaussianBlur(5))
    im.alpha_composite(glow)
    d = ImageDraw.Draw(im)
    for i, (r, a, thick) in enumerate(((40, 150, 5), (38, 220, 3))):
        d.ellipse((w / 2 - r, h / 2 - r, w / 2 + r, h / 2 + r),
                  outline=(150, 255, 190, a), width=thick)
    # четыре «искры» по краям — кольцо видно и на светлом, и на тёмном
    for ang in (0, 90, 180, 270):
        x = w / 2 + 40 * math.cos(math.radians(ang))
        y = h / 2 + 40 * math.sin(math.radians(ang))
        d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(230, 255, 240, 235))
    p = os.path.join(OUT, "sprites", "ring.png")
    im.save(p)
    return sprite("Сила", os.path.relpath(p, ROOT), w, h)


def make_orb():
    """«Свет Силы» — бонус: голубая светящаяся сфера."""
    w = h = 64
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((2, 2, w - 2, h - 2), fill=(90, 220, 255, 150))
    glow = glow.filter(ImageFilter.GaussianBlur(7))
    im.alpha_composite(glow)
    d = ImageDraw.Draw(im)
    d.ellipse((16, 16, w - 16, h - 16), fill=(180, 245, 255, 235))
    d.ellipse((22, 20, w - 26, h - 34), fill=(255, 255, 255, 230))
    for ang in (30, 150, 270):
        x = w / 2 + 24 * math.cos(math.radians(ang))
        y = h / 2 + 24 * math.sin(math.radians(ang))
        d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(235, 255, 255, 210))
    p = os.path.join(OUT, "sprites", "orb.png")
    im.save(p)
    return sprite("Свет", os.path.relpath(p, ROOT), w, h)


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
                        fill=(8, 26, 18, 215))
    d.text((x0, y), text, font=f, fill=(225, 255, 238))
    return im


def make_backdrops():
    out = []
    swamp = frame("force-swamp.png")
    p = os.path.join(OUT, "backdrops", "swamp.png")
    swamp.save(p)
    out.append({"slug": "swamp", "name": "Болото", "file": os.path.relpath(p, ROOT)})

    win = frame("force-xwing.png").convert("RGBA")
    win.alpha_composite(Image.new("RGBA", win.size, (4, 30, 24, 70)))
    plate(win, "СИЛА С ТОБОЙ!", 30, 48, (170, 255, 205), (4, 26, 14))
    hint(win, "истребитель поднят из болота", 96)
    p = os.path.join(OUT, "backdrops", "win.png")
    win.convert("RGB").save(p)
    out.append({"slug": "win", "name": "Победа", "file": os.path.relpath(p, ROOT)})

    lose = swamp.convert("RGBA")
    lose.alpha_composite(Image.new("RGBA", lose.size, (10, 20, 30, 120)))
    lose = lose.filter(ImageFilter.GaussianBlur(1.0))
    plate(lose, "НЕ ХВАТИЛО СИЛЫ", 44, 46, (150, 220, 255), (4, 14, 26))
    hint(lose, "соберись и попробуй снова", 112)
    p = os.path.join(OUT, "backdrops", "lose.png")
    lose.convert("RGB").save(p)
    out.append({"slug": "lose", "name": "Провал", "file": os.path.relpath(p, ROOT)})
    return out


# ------------------------------------------------------------------ звуки ---
def make_force():
    """Камень уходит вверх: мягкий восходящий гул."""
    dur = 0.7
    n = int(dur * SR)
    out = []
    ph = 0.0
    for i in range(n):
        t = i / SR
        f = 180 + 520 * (t / dur) ** 0.7
        ph += 2 * math.pi * f / SR
        env = min(1.0, t * 12) * max(0.0, 1.0 - (t / dur) ** 2)
        out.append((math.sin(ph) * 0.5 + math.sin(ph * 2.01) * 0.18) * env * 0.6)
    path, _ = write_wav("сила.wav", out)
    return os.path.relpath(path, ROOT)


def make_splash():
    """Камень утонул: короткий шумовой всплеск."""
    dur = 0.45
    n = int(dur * SR)
    rnd = random.Random(5)
    out = []
    lp = 0.0
    for i in range(n):
        t = i / SR
        lp = lp * 0.7 + rnd.uniform(-1, 1) * 0.3
        bub = math.sin(2 * math.pi * (300 - 180 * t) * t) * 0.25
        env = min(1.0, t * 40) * max(0.0, 1.0 - (t / dur) ** 0.8)
        out.append((lp * 0.7 + bub) * env * 0.7)
    path, _ = write_wav("всплеск.wav", out)
    return os.path.relpath(path, ROOT)


def main():
    os.makedirs(os.path.join(OUT, "sprites"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "backdrops"), exist_ok=True)
    luke, yoda, rock = make_sprites()
    man = {"sprites": [{"slug": "luke", "name": "Люк", "costumes": luke},
                       {"slug": "yoda", "name": "Йода", "costumes": yoda},
                       {"slug": "rock", "name": "Камень", "costumes": rock},
                       {"slug": "ring", "name": "Сила", "costumes": [make_ring()]},
                       {"slug": "orb", "name": "Свет", "costumes": [make_orb()]}],
           "backdrops": make_backdrops()}
    json.dump(man, open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("готово: assets/force +", make_force(), make_splash())
    for s in man["sprites"]:
        for c in s["costumes"]:
            print(f"  {s['name']}: {c['w']}×{c['h']}")


if __name__ == "__main__":
    main()
