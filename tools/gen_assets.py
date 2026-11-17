# -*- coding: utf-8 -*-
"""
Генератор всех SVG-ассетов набора «Star Wars: Дуэль на Набу» для Scratch 3.0.
Запуск:  python3 tools/gen_assets.py
Результат: assets/backdrops/*.svg, assets/sprites/<спрайт>/*.svg, assets/manifest.json
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rig import QUIGON, OBIWAN, MAUL, character_svg, W as CW, H as CH
import vehicles as V
import backdrops as B

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")

# ------------------------------------------------------------------ позы -----
STANCE = dict(lean=2, legF=(10, 4), legB=(-10, -6), armB=(14, 16), armF=(40, 30), saber=52)
WALK = [
    dict(lean=3, bob=-1, legF=(26, 10), legB=(-22, -34), armB=(-4, 12), armF=(33, 32), saber=58),
    dict(lean=2, bob=1, legF=(14, 2), legB=(-8, -16), armB=(8, 16), armF=(38, 30), saber=54),
    dict(lean=2, bob=-1, legF=(-18, -26), legB=(22, 12), armB=(18, 14), armF=(44, 28), saber=50),
    dict(lean=2, bob=1, legF=(0, -8), legB=(8, 0), armB=(12, 16), armF=(40, 30), saber=52),
]
JUMP = dict(lean=6, bob=-8, legF=(38, 58), legB=(-6, -34), armB=(-18, -8), armF=(58, 12), saber=44)
WINDUP = dict(lean=-3, legF=(16, 6), legB=(-16, -12), armB=(-12, 10), armF=(70, -18),
              saber=206, head=-4)
STRIKE = dict(lean=8, legF=(24, 8), legB=(-22, -16), armB=(20, 10), armF=(84, 6), saber=72, head=4)
BLOCK = dict(lean=0, legF=(12, 6), legB=(-12, -10), armB=(0, 20), armF=(56, 40), saber=172)
HIT = dict(lean=-10, bob=2, legF=(-14, -20), legB=(18, 10), armB=(-24, -14), armF=(20, 40),
           saber=140, head=-12)

MAUL_VARIANTS = dict(STANCE=dict(STANCE, saber=104, legF=(14, 8), legB=(-14, -10),
                                 armF=(50, 24), lean=3, head=-2),
                     WINDUP=dict(WINDUP, saber=300, armF=(56, -6), lean=-4),
                     STRIKE=dict(STRIKE, saber=58, armF=(78, 4)),
                     BLOCK=dict(BLOCK, saber=138),
                     HIT=dict(HIT, saber=250))


def char_costumes(cfg, maul=False):
    v = MAUL_VARIANTS if maul else {}
    st = v.get("STANCE", STANCE)
    out = [("стойка", character_svg(cfg, st))]
    for i, p in enumerate(WALK, 1):
        out.append((f"шаг-{i}", character_svg(cfg, p)))
    out.append(("прыжок", character_svg(cfg, JUMP)))
    out.append(("удар-1", character_svg(cfg, v.get("WINDUP", WINDUP))))
    out.append(("удар-2", character_svg(cfg, v.get("STRIKE", STRIKE))))
    out.append(("блок", character_svg(cfg, v.get("BLOCK", BLOCK))))
    out.append(("ранен", character_svg(cfg, v.get("HIT", HIT))))
    return out


# --------------------------------------------------------------- манифест ----
MANIFEST = {"backdrops": [], "sprites": []}


def write_sprite(slug, name, costumes, w, h, folder=None):
    d = os.path.join(ASSETS, "sprites", folder or slug)
    os.makedirs(d, exist_ok=True)
    items = []
    for i, (cname, svg) in enumerate(costumes):
        fn = f"{i+1:02d}-{slug}-{i+1}.svg"
        with open(os.path.join(d, fn), "w", encoding="utf-8") as fh:
            fh.write(svg)
        items.append({"name": cname, "file": f"sprites/{folder or slug}/{fn}", "w": w, "h": h})
    MANIFEST["sprites"].append({"slug": slug, "name": name, "size": [w, h], "costumes": items})
    return items


def write_backdrop(slug, name, svg):
    d = os.path.join(ASSETS, "backdrops")
    os.makedirs(d, exist_ok=True)
    fn = f"{slug}.svg"
    with open(os.path.join(d, fn), "w", encoding="utf-8") as fh:
        fh.write(svg)
    MANIFEST["backdrops"].append({"slug": slug, "name": name, "file": f"backdrops/{fn}",
                                  "w": B.W, "h": B.H})


def main():
    # ---------------- фоны ----------------
    write_backdrop("01-title", "Титул", B.title())
    write_backdrop("02-space", "Космос", B.space())
    write_backdrop("03-naboo", "Посадка на Набу", B.naboo())
    write_backdrop("04-generator", "Генераторная", B.generator())
    write_backdrop("05-victory", "Победа", B.victory())

    # ---------------- персонажи ----------------
    write_sprite("quigon", "Квай-Гон", char_costumes(QUIGON), CW, CH)
    write_sprite("obiwan", "Оби-Ван", char_costumes(OBIWAN), CW, CH)
    write_sprite("maul", "Дарт Мол", char_costumes(MAUL, maul=True), CW, CH)

    # ---------------- техника и эффекты ----------------
    write_sprite("naboo-fighter", "Истребитель", [
        ("двигатель-1", V.naboo_fighter(0.72)),
        ("двигатель-2", V.naboo_fighter(1.0)),
        ("двигатель-3", V.naboo_fighter(1.28)),
    ], 140, 200)
    write_sprite("droid-fighter", "Дроид-истребитель", [
        ("крылья-открыты", V.droid_fighter(True)),
        ("крылья-сложены", V.droid_fighter(False)),
    ], 130, 130)
    write_sprite("laser", "Лазер", [
        ("синий", V.laser("#66d9ff", "#ffffff", 46, 9)),
    ], 26, 56)
    write_sprite("enemy-laser", "Лазер врага", [
        ("красный", V.laser("#ff5a3d", "#ffe8d0", 40, 9)),
    ], 26, 50)
    write_sprite("explosion", "Взрыв", [
        (f"кадр-{i+1}", V.explosion(i)) for i in range(4)
    ], 110, 110)
    write_sprite("sparks", "Искры", [
        (f"кадр-{i+1}", V.clash_sparks(i)) for i in range(2)
    ], 90, 90)
    write_sprite("plasma-gate", "Плазма-врата", [
        ("закрыто", V.plasma_gate(False)),
        ("открыто", V.plasma_gate(True)),
    ], 200, 360)
    write_sprite("dot", "Режиссёр", [("точка", V.dot())], 10, 10)

    with open(os.path.join(ASSETS, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(MANIFEST, fh, ensure_ascii=False, indent=1)
    n = sum(len(s["costumes"]) for s in MANIFEST["sprites"])
    print(f"готово: {len(MANIFEST['backdrops'])} фонов, {len(MANIFEST['sprites'])} спрайтов, "
          f"{n} костюмов")


if __name__ == "__main__":
    main()
