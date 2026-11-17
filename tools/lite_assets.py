# -*- coding: utf-8 -*-
"""Ассеты лёгкой версии «Дуэль на мечах» (assets/lite).

Использует готовые костюмы «стойка»/«атака» из assets/film и добавляет
третий костюм — «блок». Поза блока вырезается с хромакея и вписывается
в тот же холст, что и остальные костюмы персонажа: масштаб — по высоте
силуэта, ноги — на ту же линию, что и в стойке.

Фоны — светлые, 480×360, с подписями, чтобы ребёнку было понятно без скриптов.
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "assets", "raw")
FILM = os.path.join(ROOT, "assets", "film")
LITE = os.path.join(ROOT, "assets", "lite")
sys.path.insert(0, os.path.join(ROOT, "tools"))
from cutout import cutout          # noqa: E402
from film_assets import backdrop, feet_anchor, solid_bbox   # noqa: E402

FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
CHAR_H = 430          # высота фигуры, как в основной версии

CHARS = [("quigon", "Квай-Гон", "quigon-block.png"),
         ("obiwan", "Оби-Ван", "obiwan-block.png"),
         ("maul", "Дарт Мол", "maul-block.png")]


def _blade(p):
    """Пиксель светового меча — его нельзя мерить как часть фигуры."""
    r, g, b, a = p
    if a < 90:
        return False
    return ((r >= 185 and g <= 100 and b <= 110) or
            (g >= 180 and r <= 130 and b <= 150) or
            (b >= 185 and r <= 130 and g <= 160))


def person_span(im, thr=12):
    """Верх и низ человека без меча: рост, по которому выравниваем позы."""
    w, h = im.size
    px = im.load()
    rows = []
    for y in range(h):
        rows.append(sum(1 for x in range(w) if px[x, y][3] > 110 and not _blade(px[x, y])))
    ys = [y for y, c in enumerate(rows) if c >= thr]
    return (min(ys), max(ys)) if ys else (0, h)


def add_block_costume(slug, raw):
    """Костюм «блок» на том же холсте, что стойка и атака."""
    stage = Image.open(os.path.join(FILM, "sprites", slug, f"{slug}-1.png")).convert("RGBA")
    W, H = stage.size
    cx0, feet0 = feet_anchor(stage)

    pose = cutout(os.path.join(RAW, raw), os.path.join("/tmp", f"lite-{raw}"), verbose=False)
    # рост человека (без меча) должен совпасть с ростом в стойке
    t0, b0 = person_span(stage)
    t1, b1 = person_span(pose)
    k = (b0 - t0) / float(max(1, b1 - t1))
    pose = pose.resize((max(1, int(pose.width * k)), max(1, int(pose.height * k))), Image.LANCZOS)
    cx, feet = feet_anchor(pose)

    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    canvas.alpha_composite(pose, (int(round(cx0 - cx)), int(round(feet0 - feet))))
    d = os.path.join(LITE, "sprites", slug)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, f"{slug}-block.png")
    canvas.save(p)
    print(f"  {slug}: рост {b0 - t0} → {person_span(canvas)[1] - person_span(canvas)[0]}, "
          f"холст {W}×{H}")
    return p


def text(dr, xy, s, size, fill, anchor="mm", font=FONT_B, shadow=None):
    f = ImageFont.truetype(font, size)
    if shadow:
        dr.text((xy[0] + 2, xy[1] + 2), s, font=f, fill=shadow, anchor=anchor)
    dr.text(xy, s, font=f, fill=fill, anchor=anchor)


def plate(dr, cx, cy, s, size, fill=(255, 255, 255), font=FONT_R, pad=(12, 5)):
    """Текст на полупрозрачной тёмной плашке — читается на любом фоне."""
    f = ImageFont.truetype(font, size)
    box = dr.textbbox((0, 0), s, font=f)
    w, h = box[2] - box[0], box[3] - box[1]
    x0, y0 = cx - w / 2 - pad[0], cy - h / 2 - pad[1]
    x1, y1 = cx + w / 2 + pad[0], cy + h / 2 + pad[1]
    dr.rounded_rectangle([x0, y0, x1, y1], radius=int(h / 2 + pad[1]), fill=(14, 20, 32, 165))
    dr.text((cx, cy), s, font=f, fill=fill, anchor="mm")


def make_backdrops():
    d = os.path.join(LITE, "backdrops")
    os.makedirs(d, exist_ok=True)
    out = {}

    # «Выбор героя» — светлая терраса + подписи
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

    # «Дуэль» — светлый зал
    p = backdrop(os.path.join(RAW, "bd-lite-duel.png"), os.path.join(d, "duel.png"),
                 darken=1.0)
    im = Image.open(p).convert("RGBA")
    dr = ImageDraw.Draw(im)
    plate(dr, 240, 334, "ПРОБЕЛ — удар   ·   ↓ — блок", 13)
    im.convert("RGB").save(p)
    out["duel"] = p

    # «Победа» — солнечный двор
    p = backdrop(os.path.join(RAW, "bd-lite-win.png"), os.path.join(d, "win.png"))
    im = Image.open(p).convert("RGBA")
    dr = ImageDraw.Draw(im)
    text(dr, (240, 40), "ПОБЕДА!", 46, (255, 236, 150), shadow=(40, 30, 0))
    plate(dr, 240, 78, "ПРОБЕЛ — сыграть ещё раз", 13)
    im.convert("RGB").save(p)
    out["win"] = p

    # «Поражение» — затемнённый зал
    im = Image.open(out["duel"]).convert("RGBA")
    dark = Image.new("RGBA", im.size, (12, 16, 26, 165))
    im.alpha_composite(dark)
    dr = ImageDraw.Draw(im)
    text(dr, (240, 150), "ПОРАЖЕНИЕ", 38, (255, 170, 150), shadow=(30, 0, 0))
    plate(dr, 240, 192, "ПРОБЕЛ — попробовать снова", 13)
    p = os.path.join(d, "lose.png")
    im.convert("RGB").save(p)
    out["lose"] = p
    return out


def make_arrow():
    """Стрелка выбора: жёлтый треугольник с тёмной обводкой."""
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
    return p


def main():
    os.makedirs(LITE, exist_ok=True)
    film = json.load(open(os.path.join(FILM, "manifest.json"), encoding="utf-8"))
    fsp = {s["slug"]: s for s in film["sprites"]}

    print("костюмы «блок»:")
    sprites = []
    for slug, name, raw in CHARS:
        block = add_block_costume(slug, raw)
        base = fsp[slug]
        costumes = [{"name": c["name"], "file": "assets/film/" + c["file"]}
                    for c in base["costumes"] if c["name"] in ("стойка", "атака")]
        costumes.append({"name": "блок", "file": "assets/lite/" + os.path.relpath(block, LITE)})
        sprites.append({"slug": slug, "name": name, "w": base["w"], "h": base["h"],
                        "costumes": costumes})

    arrow = make_arrow()
    sprites.append({"slug": "arrow", "name": "Стрелка", "w": 64, "h": 64,
                    "costumes": [{"name": "стрелка",
                                  "file": "assets/lite/" + os.path.relpath(arrow, LITE)}]})

    print("фоны:")
    bd = make_backdrops()
    titles = {"choice": "Выбор героя", "duel": "Дуэль", "win": "Победа", "lose": "Поражение"}
    backdrops = [{"slug": k, "name": titles[k], "file": "assets/lite/" + os.path.relpath(p, LITE)}
                 for k, p in bd.items()]

    man = {"sprites": sprites, "backdrops": backdrops}
    with open(os.path.join(LITE, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(man, fh, ensure_ascii=False, indent=1)
    print("готово: assets/lite/manifest.json")
    for s in sprites:
        print("  ", s["name"], "— костюмы:", ", ".join(c["name"] for c in s["costumes"]))
    print("   фонов:", len(backdrops))


if __name__ == "__main__":
    main()
