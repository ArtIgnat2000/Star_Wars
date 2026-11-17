# -*- coding: utf-8 -*-
"""Ассеты лёгкой версии «Дуэль на мечах» (assets/lite).

Костюмы персонажей:
  стойка, атака  — берутся из большой версии (assets/film);
  блок, ранен, победа — вырезаются с хромакея здесь же.

У каждого костюма в манифесте есть точка опоры `cx, cy` — это стопы фигуры.
В проекте она становится центром вращения костюма, поэтому при смене позы
персонаж не прыгает, даже если холсты костюмов разной высоты (например,
«победа» с поднятым мечом выше остальных).

Фоны — светлые, 480×360, с подписями, чтобы ребёнку было понятно без скриптов.
Эффекты (вспышка удара, кольцо блока) рисуются кодом.
"""
import json
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "assets", "raw")
FILM = os.path.join(ROOT, "assets", "film")
LITE = os.path.join(ROOT, "assets", "lite")
sys.path.insert(0, os.path.join(ROOT, "tools"))
from cutout import cutout          # noqa: E402
from film_assets import backdrop, feet_anchor, solid_bbox   # noqa: E402

FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# slug: (имя, костюмы) — ("film", номер кадра) или ("raw", файл)
CHARS = {
    "quigon": ("Квай-Гон", [
        ("стойка", "film", 1), ("атака", "film", 2),
        ("блок", "raw", "quigon-block.png"),
        ("ранен", "raw", "quigon-hurt.png"),
        ("победа", "raw", "quigon-win.png")]),
    "obiwan": ("Оби-Ван", [
        ("стойка", "film", 1), ("атака", "film", 2),
        ("блок", "raw", "obiwan-block.png"),
        ("ранен", "raw", "obiwan-hurt.png"),
        ("победа", "raw", "obiwan-win.png")]),
    "maul": ("Дарт Мол", [
        ("стойка", "film", 1), ("атака", "film", 2),
        ("блок", "raw", "maul-block.png"),
        ("ранен", "raw", "maul-hurt.png")]),
}


def _blade(p):
    """Пиксель светового меча — его нельзя мерить как часть фигуры."""
    r, g, b, a = p
    if a < 90:
        return False
    return ((r >= 185 and g <= 100 and b <= 110) or
            (g >= 180 and r <= 130 and b <= 150) or
            (b >= 185 and r <= 130 and g <= 160))


def person_span(im, thr=12):
    """Верх и низ человека без меча: по этому росту выравниваем позы."""
    w, h = im.size
    px = im.load()
    rows = []
    for y in range(h):
        rows.append(sum(1 for x in range(w) if px[x, y][3] > 110 and not _blade(px[x, y])))
    ys = [y for y, c in enumerate(rows) if c >= thr]
    return (min(ys), max(ys)) if ys else (0, h)


def extend_blade(im, extra=150):
    """Дорисовывает клинок вверх, если на кадре он обрезан верхней кромкой.

    Верхней кромки на таких кадрах касается только световой меч, поэтому
    продолжаем именно его: белая сердцевина + цветное свечение вокруг.
    """
    w, h = im.size
    px = im.load()
    xs, halo = [], []
    for y in range(0, 12):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a <= 110:
                continue
            xs.append(x)
            if max(r, g, b) - min(r, g, b) > 40:
                halo.append((r, g, b))
    if len(xs) < 4:
        return im
    cx = sum(xs) / float(len(xs))
    bw = max(10.0, float(max(xs) - min(xs)))
    col = ((120, 160, 255) if not halo else
           tuple(sum(c[i] for c in halo) // len(halo) for i in range(3)))

    out = Image.new("RGBA", (w, h + extra), (0, 0, 0, 0))
    out.alpha_composite(im, (0, extra))
    glow = Image.new("RGBA", out.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(glow)
    for i in range(extra):
        yy = extra - i
        k = 1.0 - i / float(extra)
        half = max(1.5, bw * 0.55 * (0.3 + 0.7 * k))
        d.line([(cx - half, yy), (cx + half, yy)], fill=col + (int(150 * k),))
    glow = glow.filter(ImageFilter.GaussianBlur(bw * 0.45))
    out.alpha_composite(glow)
    core = Image.new("RGBA", out.size, (0, 0, 0, 0))
    dc = ImageDraw.Draw(core)
    dc.line([(cx, extra + 6), (cx, 4)], fill=(255, 255, 255, 235),
            width=max(2, int(bw * 0.34)))
    out.alpha_composite(core)
    return out


def fit_into(im, pad=6):
    """Обрезает по содержимому и добавляет поля: холст костюма по фигуре."""
    bbox = im.getbbox()
    if bbox:
        im = im.crop(bbox)
    out = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
    out.alpha_composite(im, (pad, pad))
    return out


def make_pose(slug, raw, target_person):
    """Вырезает новую позу и приводит её к росту фигуры в «стойке»."""
    im = cutout(os.path.join(RAW, raw), os.path.join("/tmp", f"lite-{raw}"), verbose=False)
    t1, b1 = person_span(im)
    k = target_person / float(max(1, b1 - t1))
    im = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)
    if "win" in raw:                      # поднятый клинок часто обрезан кромкой кадра
        im = extend_blade(im)
    im = fit_into(im)
    d = os.path.join(LITE, "sprites", slug)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, raw.rsplit('.', 1)[0].replace('-', '_') + '.png')
    im.save(p)
    return p


def costume_entry(name, path, cx, cy, w, h):
    return {"name": name, "file": os.path.relpath(path, ROOT).replace(os.sep, "/"),
            "w": w, "h": h, "cx": round(cx, 2), "cy": round(cy, 2)}


def build_character(slug, name, items):
    film = json.load(open(os.path.join(FILM, "manifest.json"), encoding="utf-8"))
    fsp = {s["slug"]: s for s in film["sprites"]}[slug]
    # рост фигуры в стойке — эталон для остальных поз
    stance = Image.open(os.path.join(FILM, fsp["costumes"][0]["file"])).convert("RGBA")
    t0, b0 = person_span(stance)
    target = b0 - t0

    out = []
    for cname, kind, src in items:
        if kind == "film":
            c = fsp["costumes"][src - 1]
            path = os.path.join(FILM, c["file"])
            im = Image.open(path).convert("RGBA")
        else:
            path = make_pose(slug, src, target)
            im = Image.open(path).convert("RGBA")
        cx, cy = feet_anchor(im)
        w, h = im.size
        out.append(costume_entry(cname, path, cx, cy, w, h))
        print(f"  {slug:7} {cname:7} {w}×{h}  опора ({cx:.0f}, {cy:.0f})")
    return {"slug": slug, "name": name, "w": fsp["w"], "h": fsp["h"], "costumes": out}


# ------------------------------------------------------------------ фоны ----
def plate(dr, cx, cy, s, size, fill=(255, 255, 255), font=FONT_R, pad=(12, 5)):
    f = ImageFont.truetype(font, size)
    box = dr.textbbox((0, 0), s, font=f)
    w, h = box[2] - box[0], box[3] - box[1]
    x0, y0 = cx - w / 2 - pad[0], cy - h / 2 - pad[1]
    x1, y1 = cx + w / 2 + pad[0], cy + h / 2 + pad[1]
    dr.rounded_rectangle([x0, y0, x1, y1], radius=int(h / 2 + pad[1]), fill=(14, 20, 32, 165))
    dr.text((cx, cy), s, font=f, fill=fill, anchor="mm")


def text(dr, xy, s, size, fill, anchor="mm", font=FONT_B, shadow=None):
    f = ImageFont.truetype(font, size)
    if shadow:
        dr.text((xy[0] + 2, xy[1] + 2), s, font=f, fill=shadow, anchor=anchor)
    dr.text(xy, s, font=f, fill=fill, anchor=anchor)


def make_backdrops():
    d = os.path.join(LITE, "backdrops")
    os.makedirs(d, exist_ok=True)
    out = {}

    p = backdrop(os.path.join(RAW, "bd-lite-choice.png"), os.path.join(d, "choice.png"),
                 darken=1.02)
    im = Image.open(p).convert("RGBA")
    veil = Image.new("RGBA", (480, 150), (255, 255, 255, 0))
    vd = ImageDraw.Draw(veil)
    for i in range(150):
        vd.line([(0, i), (480, i)], fill=(18, 26, 40, int(130 * (1 - i / 150.0))))
    im.alpha_composite(veil, (0, 0))
    dr = ImageDraw.Draw(im)
    text(dr, (240, 34), "ДУЭЛЬ НА МЕЧАХ", 34, (255, 236, 150), shadow=(40, 30, 0))
    text(dr, (240, 66), "Кто сразится с Дартом Молом?", 17, (255, 255, 255),
         font=FONT_R, shadow=(20, 20, 20))
    plate(dr, 130, 272, "КВАЙ-ГОН", 15, font=FONT_B)
    plate(dr, 350, 272, "ОБИ-ВАН", 15, font=FONT_B)
    plate(dr, 240, 337, "← → выбрать   ·   ПРОБЕЛ — в бой", 13)
    im.convert("RGB").save(p)
    out["choice"] = p

    p = backdrop(os.path.join(RAW, "bd-lite-duel.png"), os.path.join(d, "duel.png"))
    im = Image.open(p).convert("RGBA")
    dr = ImageDraw.Draw(im)
    plate(dr, 240, 334, "ПРОБЕЛ — удар   ·   ↓ — блок", 13)
    im.convert("RGB").save(p)
    out["duel"] = p

    p = backdrop(os.path.join(RAW, "bd-lite-win.png"), os.path.join(d, "win.png"))
    im = Image.open(p).convert("RGBA")
    dr = ImageDraw.Draw(im)
    text(dr, (240, 40), "ПОБЕДА!", 46, (255, 236, 150), shadow=(40, 30, 0))
    plate(dr, 240, 78, "ПРОБЕЛ — сыграть ещё раз", 13)
    im.convert("RGB").save(p)
    out["win"] = p

    im = Image.open(out["duel"]).convert("RGBA")
    im.alpha_composite(Image.new("RGBA", im.size, (12, 16, 26, 165)))
    dr = ImageDraw.Draw(im)
    text(dr, (240, 150), "ПОРАЖЕНИЕ", 38, (255, 170, 150), shadow=(30, 0, 0))
    plate(dr, 240, 192, "ПРОБЕЛ — попробовать снова", 13)
    p = os.path.join(d, "lose.png")
    im.convert("RGB").save(p)
    out["lose"] = p
    return out


# --------------------------------------------------------------- эффекты ----
def radial(size, color, power=2.0):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    px = im.load()
    c = size / 2.0
    for y in range(size):
        for x in range(size):
            d = math.hypot(x - c, y - c) / c
            if d >= 1:
                continue
            a = int(255 * (1 - d) ** power)
            px[x, y] = (color[0], color[1], color[2], a)
    return im


def make_effects():
    """Вспышка удара (3 кадра) и кольцо блока (2 кадра) — рисуются кодом."""
    S = 160
    d = os.path.join(LITE, "sprites", "flash")
    os.makedirs(d, exist_ok=True)
    files = []
    for i, k in enumerate((0.55, 0.8, 1.0)):
        im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        core = radial(int(S * 0.62 * k), (255, 236, 150), 1.6)
        halo = radial(int(S * k), (255, 168, 80), 2.6)
        im.alpha_composite(halo, ((S - halo.width) // 2, (S - halo.height) // 2))
        im.alpha_composite(core, ((S - core.width) // 2, (S - core.height) // 2))
        # лучи
        dr = ImageDraw.Draw(im)
        for a in range(0, 360, 30):
            r = math.radians(a)
            ln = S * 0.34 * k
            dr.line([(S / 2, S / 2), (S / 2 + math.cos(r) * ln, S / 2 + math.sin(r) * ln)],
                    fill=(255, 245, 210, 150), width=3)
        p = os.path.join(d, f"flash-{i + 1}.png")
        im.save(p)
        files.append(p)

    d2 = os.path.join(LITE, "sprites", "ring")
    os.makedirs(d2, exist_ok=True)
    rfiles = []
    for i, k in enumerate((0.55, 0.85)):
        im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        dr = ImageDraw.Draw(im)
        r = S * 0.34 * k
        for t, (wd, al) in enumerate(((10, 90), (6, 160), (3, 230))):
            dr.ellipse([S / 2 - r + wd, S / 2 - r + wd, S / 2 + r - wd, S / 2 + r - wd],
                       outline=(170, 220, 255, al), width=wd)
        im = im.filter(ImageFilter.GaussianBlur(1.2))
        p = os.path.join(d2, f"ring-{i + 1}.png")
        im.save(p)
        rfiles.append(p)

    def entry(slug, name, paths, names):
        c = [costume_entry(n, p, 80, 80, S, S) for n, p in zip(names, paths)]
        return {"slug": slug, "name": name, "w": S, "h": S, "costumes": c}

    print("  эффекты: вспышка — 3 кадра, кольцо — 2 кадра")
    return [entry("flash", "Вспышка", files, ["1", "2", "3"]),
            entry("ring", "Кольцо", rfiles, ["1", "2"])]


def make_arrow():
    S = 64
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    pts = [(8, 6), (S - 8, 6), (S // 2, S - 8)]
    dr.polygon(pts, fill=(255, 214, 64, 255), outline=(60, 44, 0, 255))
    dr.line(pts + [pts[0]], fill=(60, 44, 0, 255), width=3)
    d = os.path.join(LITE, "sprites", "arrow")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "arrow-1.png")
    im.save(p)
    return {"slug": "arrow", "name": "Стрелка", "w": S, "h": S,
            "costumes": [costume_entry("стрелка", p, S / 2, S / 2, S, S)]}


def main():
    os.makedirs(LITE, exist_ok=True)
    print("костюмы:")
    sprites = [build_character(slug, name, items) for slug, (name, items) in CHARS.items()]
    sprites.append(make_arrow())
    sprites += make_effects()

    print("фоны:")
    bd = make_backdrops()
    titles = {"choice": "Выбор героя", "duel": "Дуэль", "win": "Победа", "lose": "Поражение"}
    backdrops = [{"slug": k, "name": titles[k],
                  "file": os.path.relpath(p, ROOT).replace(os.sep, "/")}
                 for k, p in bd.items()]

    man = {"sprites": sprites, "backdrops": backdrops}
    with open(os.path.join(LITE, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(man, fh, ensure_ascii=False, indent=1)
    print("готово: assets/lite/manifest.json")
    for s in sprites:
        print("  ", s["name"], "-", ", ".join(c["name"] for c in s["costumes"]))
    print("   фонов:", len(backdrops))


if __name__ == "__main__":
    main()
