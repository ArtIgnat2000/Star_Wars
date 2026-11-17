# -*- coding: utf-8 -*-
"""
Кинематографичные ассеты: вырезание сгенерированных кадров с хромакея,
выравнивание поз по стопам, кадры пламени двигателя, фоны 480×360.
Результат: assets/film/... + assets/film/manifest.json
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageChops

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "assets", "raw")
FILM = os.path.join(ROOT, "assets", "film")
sys.path.insert(0, os.path.join(ROOT, "tools"))
from cutout import cutout  # noqa: E402


def alpha_bbox(im):
    return im.getbbox()


def feet_anchor(im):
    """Возвращает (x центра стоп, y подошвы) по нижней полосе силуэта."""
    a = im.getchannel("A")
    w, h = im.size
    bbox = a.getbbox()
    if not bbox:
        return w // 2, h
    l, t, r, b = bbox
    band = max(3, int((b - t) * 0.05))
    px = a.crop((0, b - band, w, b)).load()
    xs = []
    for y in range(band):
        for x in range(w):
            if px[x, y] > 40:
                xs.append(x)
    cx = sorted(xs)[len(xs) // 2] if xs else (l + r) // 2
    return cx, b


def build_character(slug, files, fig_h=430):
    """Выравнивает позы по стопам и приводит к одному росту фигуры."""
    cut = []
    for f in files:
        im = cutout(os.path.join(RAW, f), os.path.join("/tmp", f"cut-{f}"), verbose=False)
        fx, fy = feet_anchor(im)
        cut.append((im, fx, fy))
    # единый масштаб: высота силуэта у всех поз одинаковая
    scaled = []
    for im, fx, fy in cut:
        l, t, r, b = im.getbbox()
        k = fig_h / float(b - t)
        im2 = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)
        scaled.append((im2, fx * k, fy * k))
    half = 0
    for im, fx, fy in scaled:
        l, t, r, b = im.getbbox()
        half = max(half, fx - l, r - fx)
    W = int(half * 2) + 24
    H = int(max(im.height for im, _, _ in scaled)) + 16
    out = []
    for im, fx, fy in scaled:
        canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        canvas.alpha_composite(im, (int(round(W / 2 - fx)), int(round(H - 8 - fy))))
        out.append(canvas)
    d = os.path.join(FILM, "sprites", slug)
    os.makedirs(d, exist_ok=True)
    paths = []
    for i, im in enumerate(out):
        p = os.path.join(d, f"{slug}-{i+1}.png")
        im.save(p)
        paths.append(p)
    return paths, out[0].size


def build_ship(slug, raw, out_h, rotate=0):
    im = cutout(os.path.join(RAW, raw), os.path.join("/tmp", f"ship-{slug}.png"), verbose=False)
    if rotate:
        im = im.rotate(rotate, expand=True)
    l, t, r, b = im.getbbox()
    im = im.crop((l, t, r, b))
    k = out_h / im.height
    im = im.resize((int(im.width * k), out_h), Image.LANCZOS)
    d = os.path.join(FILM, "sprites", slug)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, f"{slug}-1.png")
    im.save(p)
    return im, p


def add_flames(ship, count=3):
    """Кадры пламени: аддитивное свечение под соплами."""
    w, h = ship.size
    frames = []
    for i in range(count):
        f = ship.copy()
        glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(glow)
        k = (0.55, 0.8, 1.0)[i]
        for cx in (w * 0.44, w * 0.57):
            cy = h * 0.955
            rw = w * 0.085 * k
            rh = h * 0.075 * k
            d.ellipse([cx - rw, cy - rh, cx + rw, cy + rh], fill=(150, 220, 255, int(200 * k)))
            d.ellipse([cx - rw * 0.55, cy - rh * 0.5, cx + rw * 0.55, cy + rh * 0.5],
                      fill=(255, 255, 255, int(230 * k)))
        glow = glow.filter(ImageFilter.GaussianBlur(radius=max(2, w * 0.012)))
        f.alpha_composite(glow)
        frames.append(f)
    return frames


def backdrop(src_png, dst, crop_ratio=4 / 3, size=(480, 360), darken=1.0, blur=0.0):
    im = Image.open(src_png).convert("RGB")
    w, h = im.size
    target = crop_ratio
    if w / h > target:
        nw = int(h * target)
        im = im.crop(((w - nw) // 2, 0, (w + nw) // 2, h))
    else:
        nh = int(w / target)
        im = im.crop((0, (h - nh) // 2, w, (h + nh) // 2))
    im = im.resize(size, Image.LANCZOS)
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    if darken < 1.0:
        from PIL import ImageEnhance
        im = ImageEnhance.Brightness(im).enhance(darken)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    im.save(dst)
    return dst


def main():
    os.makedirs(FILM, exist_ok=True)
    manifest = {"sprites": [], "backdrops": []}

    # ---------------- персонажи ----------------
    chars = [
        ("quigon", "Квай-Гон", ["quigon-base.png", "quigon-attack.png"],
         ["стойка", "атака"]),
        ("obiwan", "Оби-Ван", ["obiwan-base.png", "obiwan-attack.png"],
         ["стойка", "атака"]),
        ("maul", "Дарт Мол", ["maul-base.png"], ["стойка"]),
    ]
    if os.path.exists(os.path.join(RAW, "maul-attack.png")):
        chars[2] = ("maul", "Дарт Мол", ["maul-base.png", "maul-attack.png"],
                    ["стойка", "атака"])
    for slug, name, files, names in chars:
        paths, size = build_character(slug, files)
        manifest["sprites"].append({
            "slug": slug, "name": name, "w": size[0], "h": size[1],
            "costumes": [{"name": n, "file": os.path.relpath(p, FILM)}
                         for n, p in zip(names, paths)]})

    # ---------------- корабли ----------------
    fighter, _ = build_ship("naboo-fighter", "fighter2.png", 300)
    frames = add_flames(fighter)
    fd = os.path.join(FILM, "sprites", "naboo-fighter")
    fpaths = []
    for i, fr in enumerate(frames):
        p = os.path.join(fd, f"naboo-fighter-{i+1}.png")
        fr.save(p)
        fpaths.append(p)
    manifest["sprites"].append({
        "slug": "naboo-fighter", "name": "Истребитель", "w": fighter.width, "h": fighter.height,
        "costumes": [{"name": f"двигатель-{i+1}", "file": os.path.relpath(p, FILM)}
                     for i, p in enumerate(fpaths)]})

    droid, _ = build_ship("droid-fighter", "droid-base.png", 260, rotate=180)
    manifest["sprites"].append({
        "slug": "droid-fighter", "name": "Дроид-истребитель", "w": droid.width, "h": droid.height,
        "costumes": [{"name": "крылья-открыты",
                      "file": os.path.relpath(os.path.join(fd, "..", "droid-fighter",
                                                           "droid-fighter-1.png"), FILM)}]})

    # ---------------- фоны ----------------
    if os.path.exists(os.path.join(RAW, "bd-space.png")):
        p = backdrop(os.path.join(RAW, "bd-space.png"), os.path.join(FILM, "backdrops", "space.png"))
        manifest["backdrops"].append({"slug": "space", "name": "Космос", "file": os.path.relpath(p, FILM)})

    with open(os.path.join(FILM, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=1)
    for s in manifest["sprites"]:
        print(s["slug"], s["w"], "×", s["h"], "| костюмов:", len(s["costumes"]))
    print("фонов:", len(manifest["backdrops"]))


if __name__ == "__main__":
    main()
