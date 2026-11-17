# -*- coding: utf-8 -*-
"""«Скриншоты» уровней из готовых ассетов (кинематографичная версия)."""
import json
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance

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


def place_vec(canvas, slug, idx, sx, sy, pct=100):
    """Векторный спрайт в масштабе сцены Scratch: 100 % = размер костюма в шагах."""
    c = VS[slug]["costumes"][idx]
    img = vec(slug, idx)
    im = img.resize((max(1, int(c["w"] * pct / 100.0)),
                     max(1, int(c["h"] * pct / 100.0))), Image.LANCZOS)
    canvas.alpha_composite(im, (int(240 + sx - im.width / 2), int(180 - sy - im.height / 2)))


def bg_film(slug):
    return Image.open(os.path.join(FILM, FB[slug]["file"])).convert("RGBA").resize((480, 360))


def bg_vec(slug):
    p = os.path.join(PREV, "png", f"backdrop-{slug}.png")
    return Image.open(p).convert("RGBA").resize((480, 360))


def flash(canvas, sx, sy, r=26):
    """Вспышка в точке столкновения клинков (вместо векторных искр)."""
    cx, cy = 240 + sx, 180 - sy
    glow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(glow)
    for i in range(r, 0, -1):
        k = i / float(r)
        a = int(150 * (1 - k) ** 2)
        col = (255, 250, int(200 + 55 * k), a)
        d.ellipse([cx - i, cy - i * 0.8, cx + i, cy + i * 0.8], fill=col)
    glow = glow.filter(ImageFilter.GaussianBlur(r * 0.18))
    canvas.alpha_composite(glow)


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
    place(c, film("explosion", 3), -150, 45, 42)
    place_vec(c, "enemy-laser", 0, 66, 75)
    place_vec(c, "enemy-laser", 0, -146, 8)
    place_vec(c, "laser", 0, -14, -46)
    place_vec(c, "laser", 0, 30, 16)
    place(c, film("naboo-fighter", 2), 0, -110, 36)
    return label(c, "Уровень 1 · орбита Набу · очки 30 · жизни 3")


def level2():
    c = bg_film("generator")
    place(c, film("obiwan", 1), 5, -40, 37)
    flash(c, 145, 10, 30)
    place(c, film("maul", 1), 130, -40, 37)
    return label(c, "Уровень 2 · генераторная · Оби-Ван против Мола")


def landing():
    c = bg_film("naboo")
    return label(c, "Интерлюдия · посадка на Набу · терраса дворца Тид")


if __name__ == "__main__":
    level1().convert("RGB").save(os.path.join(PREV, "gameplay-1.png"))
    level2().convert("RGB").save(os.path.join(PREV, "gameplay-2.png"))
    landing().convert("RGB").save(os.path.join(PREV, "gameplay-3.png"))
    a = Image.open(os.path.join(PREV, "gameplay-1.png"))
    b = Image.open(os.path.join(PREV, "gameplay-2.png"))
    s = Image.new("RGB", (480, 730), (10, 10, 16))
    s.paste(a, (0, 0))
    s.paste(b, (0, 370))
    s.save(os.path.join(PREV, "gameplay.png"))
    print("готово: preview/gameplay-1.png, gameplay-2.png, gameplay-3.png")
