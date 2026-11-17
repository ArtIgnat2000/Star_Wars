# -*- coding: utf-8 -*-
"""Титульный фон: кинематографичный космос + векторный логотип."""
import json, os, sys
from PIL import Image, ImageEnhance
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backdrops as B
from rig import Svg, f, circle, ellipse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "assets", "raw")
FILM = os.path.join(ROOT, "assets", "film")


def logo_svg():
    s = Svg(480, 360)
    t = "STAR WARS"
    size = B.fit(t, 400, 1.5)
    s.add(f'<g opacity="0.92">')
    s.add(B.text(t, (480 - B.text_width(t, size, 1.5)) / 2, 84, size, "#ffe14d", "#2b1a05",
                 ow=0.34, gap=1.5))
    s.add("</g>")
    t2 = "NABOO DUEL"
    s2 = B.fit(t2, 240, 1.7)
    s.add(B.text(t2, (480 - B.text_width(t2, s2, 1.7)) / 2, 176, s2, "#eaf1ff", "#0b1426",
                 ow=0.5, gap=1.7))
    return str(s)


def main():
    im = Image.open(os.path.join(RAW, "bd-space.png")).convert("RGB")
    w, h = im.size
    nw = int(h * 4 / 3)
    im = im.crop(((w - nw) // 2, 0, (w + nw) // 2, h)).resize((480, 360), Image.LANCZOS)
    im = ImageEnhance.Brightness(im).enhance(0.72)
    out_svg = "/tmp/title-logo.svg"
    open(out_svg, "w", encoding="utf-8").write(logo_svg())
    os.system(f"SCALE=2 node '{ROOT}/tools/render.js' {out_svg} >/dev/null")
    logo = Image.open("/tmp/title-logo.png").convert("RGBA").resize((480, 360), Image.LANCZOS)
    im = im.convert("RGBA")
    im.alpha_composite(logo)
    os.makedirs(os.path.join(FILM, "backdrops"), exist_ok=True)
    im.convert("RGB").save(os.path.join(FILM, "backdrops", "title.png"))
    # прописываем фон в манифест
    mpath = os.path.join(FILM, "manifest.json")
    man = json.load(open(mpath, encoding="utf-8"))
    man["backdrops"] = [b for b in man["backdrops"] if b["slug"] != "title"]
    man["backdrops"].insert(0, {"slug": "title", "name": "Титул",
                                "file": "backdrops/title.png"})
    json.dump(man, open(mpath, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("готово: assets/film/backdrops/title.png")


if __name__ == "__main__":
    main()
