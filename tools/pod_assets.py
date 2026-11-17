# -*- coding: utf-8 -*-
"""Ассеты для игры «Гонки на подах» → assets/pod.

* под и скала вырезаются с хромакея (assets/raw/pod-*.png);
* фон трассы — кинокадр пустыни, обрезанный в 4:3 и уменьшенный до 480×360;
* фоны финала рисуются поверх него же;
* рёв двигателя синтезируется в assets/sounds/рёв-пода.wav.

Запуск: python3 tools/pod_assets.py
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cutout import cutout                      # noqa: E402
from gen_sounds import write_wav              # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "assets", "raw")
OUT = os.path.join(ROOT, "assets", "pod")
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SR = 44100


def sprite(name, rel, w, h, cx=None, cy=None):
    return {"name": name, "file": rel, "w": w, "h": h,
            "cx": w / 2 if cx is None else cx, "cy": h / 2 if cy is None else cy}


def cut(src, dst, target_h=None):
    cutout(os.path.join(RAW, src), dst, target_h=target_h, verbose=False)
    im = Image.open(dst)
    return im.size


# ------------------------------------------------------------------ под -----
def make_pod():
    dst = os.path.join(OUT, "sprites", "pod.png")
    cut("pod-racer.png", dst)
    w, h = Image.open(dst).size
    return sprite("под", os.path.relpath(dst, ROOT), w, h)


def make_rock():
    dst = os.path.join(OUT, "sprites", "rock.png")
    cut("pod-rock.png", dst)
    w, h = Image.open(dst).size
    return sprite("скала", os.path.relpath(dst, ROOT), w, h)


# ------------------------------------------------------------------ фоны ----
def desert():
    im = Image.open(os.path.join(RAW, "pod-desert.png")).convert("RGB")
    w, h = im.size
    nw = int(h * 4 / 3)
    im = im.crop(((w - nw) // 2, 0, (w + nw) // 2, h)).resize((480, 360), Image.LANCZOS)
    return im


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
                        fill=(28, 18, 8, 210))
    d.text((x0, y), text, font=f, fill=(255, 245, 226))
    return im


def top_fade(im, color=(26, 14, 4), height=150, alpha=170):
    fade = Image.new("RGBA", im.size, (0, 0, 0, 0))
    fd = ImageDraw.Draw(fade)
    for y in range(height):
        fd.line((0, y, im.width, y),
                fill=color + (int(alpha * (1 - y / height) ** 1.4),))
    im.alpha_composite(fade)
    return im


def make_backdrops():
    out = []
    base = desert()
    p = os.path.join(OUT, "backdrops", "track.png")
    base.save(p)
    out.append({"slug": "track", "name": "Трасса", "file": os.path.relpath(p, ROOT)})

    win = base.convert("RGBA")
    top_fade(win)
    plate(win, "ФИНИШ!", 40, 58, (255, 226, 96), (58, 34, 4))
    hint(win, "новый заезд начнётся сам", 108)
    p = os.path.join(OUT, "backdrops", "win.png")
    win.convert("RGB").save(p)
    out.append({"slug": "win", "name": "Финиш", "file": os.path.relpath(p, ROOT)})

    lose = base.convert("RGBA")
    veil = Image.new("RGBA", lose.size, (120, 40, 10, 96))
    lose.alpha_composite(veil)
    lose = lose.filter(ImageFilter.GaussianBlur(0.6))
    plate(lose, "АВАРИЯ", 52, 54, (255, 170, 120), (44, 12, 4))
    hint(lose, "и попробуем ещё раз", 126)
    p = os.path.join(OUT, "backdrops", "lose.png")
    lose.convert("RGB").save(p)
    out.append({"slug": "lose", "name": "Авария", "file": os.path.relpath(p, ROOT)})
    return out


# ------------------------------------------------------------------ звук ----
def make_engine():
    """Рёв подов: низкий пилообразный гул + шум ветра, с разгоном."""
    import math
    import random
    dur = 1.6
    n = int(dur * SR)
    rnd = random.Random(11)
    out = []
    ph = 0.0
    lp = 0.0
    for i in range(n):
        t = i / SR
        k = t / dur
        fr = 74 + 26 * k + 5 * math.sin(2 * math.pi * 7 * t)
        ph += 2 * math.pi * fr / SR
        saw = 2 * ((ph / (2 * math.pi)) % 1.0) - 1
        lp = lp * 0.86 + rnd.uniform(-1, 1) * 0.14          # шум двигателя
        v = 0.55 * saw + 0.35 * lp + 0.18 * math.sin(ph * 2)
        env = min(1.0, t * 6) * min(1.0, (dur - t) * 6)
        out.append(v * env * 0.55)
    path, _ = write_wav("рёв-пода.wav", out)
    return os.path.relpath(path, ROOT)


def main():
    os.makedirs(os.path.join(OUT, "sprites"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "backdrops"), exist_ok=True)
    man = {"sprites": [{"slug": "pod", "name": "Под", "costumes": [make_pod()]},
                       {"slug": "rock", "name": "Скала", "costumes": [make_rock()]}],
           "backdrops": make_backdrops()}
    json.dump(man, open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    snd = make_engine()
    print("готово: assets/pod (под, скала, 3 фона) +", snd)
    for s in man["sprites"]:
        for c in s["costumes"]:
            print(f"  {s['name']}: {c['w']}×{c['h']}")


if __name__ == "__main__":
    main()
