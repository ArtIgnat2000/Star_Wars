# -*- coding: utf-8 -*-
"""Новая простая игра: «Сбей дроидов» — не больше 100 блоков.

Запуск: python3 tools/build_sb3_arcade.py
Результат: star_wars_arcade.sb3

Правила:
  ← →    — вести корабль,
  ПРОБЕЛ — выстрел,
  сбить 8 дроидов — победа,
  пропустить 5 дроидов — поражение.

Всё держится на клонах и четырёх переменных: очки, жизни, игра, лазер.
Скриптов всего пять — по одному на «роль», их видно в редакторе целиком.
"""
import hashlib
import json
import os
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sb3lib
from sb3lib import *      # noqa: F401,F403

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCADE = os.path.join(ROOT, "assets", "arcade")
OUT = os.path.join(ROOT, "star_wars_arcade.sb3")

# --------------------------------------------------------------- переменные --
SCORE_TO_WIN = 8         # сколько дроидов сбить
LIVES = 5                # сколько можно пропустить

VARS = {"очки": "v-score", "жизни": "v-lives", "игра": "v-run", "лазер": "v-laser"}
ALL_VARS = {vid: [name, 0] for name, vid in VARS.items()}
ALL_VARS[VARS["жизни"]][1] = LIVES
ALL_VARS[VARS["игра"]][1] = 1

BC = {"играть": "b-play", "конец": "b-over"}
ALL_BC = {bid: name for name, bid in BC.items()}

sb3lib.VARS, sb3lib.BC = VARS, BC
sb3lib.ALL_VARS, sb3lib.ALL_BC = ALL_VARS, ALL_BC

MAN = json.load(open(os.path.join(ARCADE, "manifest.json"), encoding="utf-8"))
SP = {s["slug"]: s for s in MAN["sprites"]}
BD = {b["slug"]: b for b in MAN["backdrops"]}

SHIP_Y, SHIP_SIZE = -118, 40
DROID_Y1, DROID_Y2 = 185, -140
DROID_SPEED = 2.5        # пикселей за кадр вниз
STEP = 8                 # пикселей за кадр при ← →
SCREEN_WAIT = 2.2        # сколько висит экран финала, потом бой начинается сам


def bounce():
    """«если на краю, оттолкнуться» — не даёт кораблю улететь за экран.

    Стиль вращения «влево-вправо»: отскок только отражает корабль,
    а он симметричный, поэтому этого не видно.
    """
    return n("motion_ifonedgebounce")


def goto_sprite(name):
    """«перейти в [спрайт]» — лазер рождается там, где стоит корабль."""
    return n("motion_goto", {"TO": menu("motion_goto_menu", TO=[name, None])})


def add_png(t, rel, name, w, h, cx, cy):
    data = open(os.path.join(ROOT, rel), "rb").read()
    md5 = hashlib.md5(data).hexdigest()
    t.costumes.append({"assetId": md5, "name": name, "bitmapResolution": 1,
                       "md5ext": md5 + ".png", "dataFormat": "png",
                       "rotationCenterX": cx, "rotationCenterY": cy, "_data": data})


def costumes(t, slug):
    for c in SP[slug]["costumes"]:
        add_png(t, c["file"], c["name"], c["w"], c["h"], c["cx"], c["cy"])


targets = []

# ================================================================= СЦЕНА ====
# Три коротких скрипта: старт, подготовка кону и экран финала.
st = Target("Stage", is_stage=True, prefix="st")   # имя сцены в .sb3 всегда Stage
for slug in ("space", "win", "lose"):
    b = BD[slug]
    data = open(os.path.join(ROOT, b["file"]), "rb").read()
    md5 = hashlib.md5(data).hexdigest()
    st.costumes.append({"assetId": md5, "name": b["name"], "bitmapResolution": 1,
                        "md5ext": md5 + ".png", "dataFormat": "png",
                        "rotationCenterX": 240, "rotationCenterY": 180, "_data": data})
st.add_sound("победа", "победа.wav")
st.add_sound("поражение", "поражение.wav")

st.script(40, 40,
          when_flag(),
          bcast("играть"))

st.script(40, 160,
          when_recv("играть"),
          setvar("очки", num(0)),
          setvar("жизни", num(LIVES)),
          setvar("игра", num(1)),
          backdrop("Космос"))

# Жизни кончились → «Поражение», дроиды сбиты → «Победа».
st.script(40, 320,
          when_recv("конец"),
          setvar("игра", num(0)),
          if_else(lt(V("жизни"), num(1)),
                  [backdrop("Поражение"), play("поражение")],
                  [backdrop("Победа"), play("победа")]),
          wait(SCREEN_WAIT),
          # игра = 1 ставим ДО сигнала: иначе корабль и дроиды успевают
          # увидеть «игра = 0» и сразу завершают свои скрипты
          setvar("игра", num(1)),
          bcast("играть"))
targets.append(st)

# ================================================================ КОРАБЛЬ ===
# Один скрипт: полёт, выстрел и огонёк двигателя.
sh = Target("Корабль", prefix="sh")
costumes(sh, "korabl")
sh.add_sound("лазер", "лазер.wav")
sh.x, sh.y, sh.size = 0, SHIP_Y, SHIP_SIZE
sh.rotation_style = "left-right"
sh.script(40, 40,
          when_recv("играть"),
          repeat_until(eq(V("игра"), num(0)),
                       if_(keyp("left arrow"), chx(num(-STEP))),
                       if_(keyp("right arrow"), chx(num(STEP))),
                       # новый выстрел — только когда предыдущий улетел
                       if_(AND(keyp("space"), eq(V("лазер"), num(0))),
                           clone("Лазер"),
                           play("лазер")),
                       bounce()))
targets.append(sh)

# ================================================================== ЛАЗЕР ===
# Клон летит вверх, пока не выйдет за край или не заденет дроида.
lz = Target("Лазер", prefix="lz")
costumes(lz, "laser")
lz.visible = False
lz.script(40, 40,
          when_clone(),
          setvar("лазер", num(1)),
          goto_sprite("Корабль"),
          show(),
          repeat_until(gt(ypos(), num(175)), chy(num(14))),
          setvar("лазер", num(0)),
          del_clone())
targets.append(lz)

# ================================================================== ДРОИД ===
# Оригинал спрятан; клоны падают сверху, взрываются от лазера или прорываются.
dr = Target("Дроид", prefix="dr")
costumes(dr, "droid")
dr.add_sound("взрыв", "взрыв.wav")
dr.visible = False
dr.size = 40

dr.script(40, 40,
          when_recv("играть"),
          repeat_until(eq(V("игра"), num(0)),
                       wait(1.1),
                       clone("Дроид")))

dr.script(40, 220,
          when_clone(),
          gotoxy(rnd(num(-190), num(190)), num(DROID_Y1)),
          show(),
          repeat_until(OR(eq(V("игра"), num(0)),
                          OR(lt(ypos(), num(DROID_Y2)), touching("Лазер"))),
                       chy(num(-DROID_SPEED))),
          if_else(touching("Лазер"),
                  [next_costume(),
                   play("взрыв"),
                   wait(0.12),
                   changevar("очки", num(1)),
                   if_(gt(V("очки"), num(SCORE_TO_WIN - 1)),
                       bcast("конец"))],
                  # прорвался вниз — минус жизнь
                  [if_(lt(ypos(), num(DROID_Y2)),
                       changevar("жизни", num(-1)),
                       if_(lt(V("жизни"), num(1)),
                           bcast("конец")))]),
          del_clone())
targets.append(dr)

# ============================================================= мониторы =====
MON = []
for name, x, y in (("очки", -200, 160), ("жизни", 120, 160)):
    MON.append({"id": VARS[name], "mode": "default", "opcode": "data_variable",
                "params": {"VARIABLE": name}, "spriteName": None,
                "value": ALL_VARS[VARS[name]][1], "width": 0, "height": 0,
                "x": x, "y": y, "visible": True, "sliderMin": 0, "sliderMax": 100,
                "isDiscrete": True})

project = {"targets": [t.to_json() for t in targets], "monitors": MON,
           "extensions": [], "meta": {"semver": "3.0.0", "vm": "0.2.0",
                                      "agent": "Star Wars arcade"}}

assets = {}
for t in targets:
    for c in t.costumes + t.sounds:
        assets[c["md5ext"]] = c["_data"]

with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("project.json", json.dumps(project, ensure_ascii=False))
    for fname, data in assets.items():
        z.writestr(fname, data)

blocks = [b for t in targets for b in t.blocks.values()]
real = [b for b in blocks if not b.get("shadow")]
print(f"собрано: {OUT}")
print(f"  спрайтов: {len(targets) - 1}, блоков: {len(real)} в редакторе "
      f"({len(blocks)} вместе с меню), ассетов: {len(assets)}, "
      f"размер: {os.path.getsize(OUT) // 1024} КБ")
assert len(blocks) <= 100, f"блоков {len(blocks)} — больше 100!"
