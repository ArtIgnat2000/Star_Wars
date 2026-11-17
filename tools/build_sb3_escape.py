# -*- coding: utf-8 -*-
"""Новая игра: «Побег со „Звезды Смерти“» — бег с прыжком, не больше 120 блоков.

Запуск: python3 tools/build_sb3_escape.py
Результат: star_wars_escape.sb3

Правила:
  ПРОБЕЛ (или ↑) — прыжок: взлёт, падение, приземление;
  300 м    — ангар с «Соколом», побег удался,
  3 удара  — «Поймали».

Скриптов шесть: три на сцене, бег Люка, «фабрика» препятствий с ящиком-клоном
и «фабрика» энергоячеек с ячейкой-клоном.
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
ESC = os.path.join(ROOT, "assets", "escape")
SND = os.path.join(ROOT, "assets", "sounds")
OUT = os.path.join(ROOT, "star_wars_escape.sb3")

# --------------------------------------------------------------- переменные --
DISTANCE_TO_WIN = 300     # метров до ангара
LIVES = 3                 # сколько ударов выдержит Люк
MAX_LIVES = 5             # больше ячейки не дают

VARS = {"метры": "v-dist", "жизни": "v-lives", "игра": "v-run", "прыжок": "v-jump"}
ALL_VARS = {vid: [name, 0] for name, vid in VARS.items()}
ALL_VARS[VARS["жизни"]][1] = LIVES
ALL_VARS[VARS["игра"]][1] = 1

BC = {"играть": "b-play", "конец": "b-over"}
ALL_BC = {bid: name for name, bid in BC.items()}

sb3lib.VARS, sb3lib.BC = VARS, BC
sb3lib.ALL_VARS, sb3lib.ALL_BC = ALL_VARS, ALL_BC

MAN = json.load(open(os.path.join(ESC, "manifest.json"), encoding="utf-8"))
SP = {s["slug"]: s for s in MAN["sprites"]}
BD = {b["slug"]: b for b in MAN["backdrops"]}

# ------------------------------------------------------------------- числа ---
FLOOR = -160              # линия пола (ноги)
LUKE_H = 129              # рост Люка на экране (костюм 300 px → 43 %)
LUKE_SIZE = 43
LUKE_X = -150
HERO_Y = FLOOR + LUKE_H // 2      # центр спрайта, когда Люк стоит  (−95)
X_MIN, X_MAX = -200, -80          # где Люк может быть по коридору
JUMP_V = 17               # сила прыжка
GRAVITY = -1.2            # на сколько падает скорость за кадр
HIT_DIST = 72             # ближе этого — столкновение
HIT_Y = -55               # ...и если Люк ещё низко (не перепрыгнул)
OBST_X1, OBST_X2 = 275, -290
OBST_Y = FLOOR + 35       # ящик и дроид одной высоты — стоят на полу
OBST_SPEED = 7
OBST_EVERY = 1.4        # пауза между препятствиями: между ними есть где приземлиться
CELL_Y = 40               # ячейка висит высоко: достать только прыжком
CELL_X1, CELL_X2 = 275, -290
CELL_SPEED = 5
CELL_EVERY = 3.0
SCREEN_WAIT = 2.2


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
st = Target("Stage", is_stage=True, prefix="st")
for slug in ("corridor", "win", "lose"):
    b = BD[slug]
    data = open(os.path.join(ROOT, b["file"]), "rb").read()
    md5 = hashlib.md5(data).hexdigest()
    st.costumes.append({"assetId": md5, "name": b["name"], "bitmapResolution": 1,
                        "md5ext": md5 + ".png", "dataFormat": "png",
                        "rotationCenterX": 240, "rotationCenterY": 180, "_data": data})
st.add_sound("победа", "победа.wav")
st.add_sound("поражение", "поражение.wav")

st.script(40, 40, when_flag(), bcast("играть"))

st.script(40, 160,
          when_recv("играть"),
          setvar("метры", num(0)),
          setvar("жизни", num(LIVES)),
          setvar("игра", num(1)),
          backdrop("Коридор"))

# 300 метров — ангар, кончились жизни — «Поймали». Экран сменяется сам.
st.script(40, 320,
          when_recv("конец"),
          setvar("игра", num(0)),
          if_else(lt(V("жизни"), num(1)),
                  [backdrop("Поймали"), play("поражение")],
                  [backdrop("Ангар"), play("победа")]),
          wait(SCREEN_WAIT),
          # игра = 1 ставим до сигнала, иначе Люк и «фабрики»
          # успевают увидеть «игра = 0» и сразу завершают скрипты
          setvar("игра", num(1)),
          bcast("играть"))
targets.append(st)

# =================================================================== ЛЮК ====
luke = Target("Люк", prefix="lk")
costumes(luke, "luke")
luke.x, luke.y, luke.size = LUKE_X, HERO_Y, LUKE_SIZE
luke.script(40, 40,
            when_recv("играть"),
            gotoxy(num(LUKE_X), num(HERO_Y)),
            repeat_until(eq(V("игра"), num(0)),
                         # прыжок — только с пола; ПРОБЕЛ или ↑
                         if_(AND(OR(keyp("space"), keyp("up arrow")),
                                 eq(ypos(), num(HERO_Y))),
                             setvar("прыжок", num(JUMP_V))),
                         # физика: скорость падает каждый кадр, на полу
                         # «ждать» ниже не даёт улететь — y возвращает приземление
                         changevar("прыжок", num(GRAVITY)),
                         chy(V("прыжок")),
                         # приземление
                         if_(lt(ypos(), num(HERO_Y)),
                             sety(num(HERO_Y)),
                             setvar("прыжок", num(0))),
                         next_costume(),          # две позы бега — анимация
                         changevar("метры", num(1)),
                         if_(gt(V("метры"), num(DISTANCE_TO_WIN - 1)),
                             bcast("конец")),
                         # без «ждать» петля без движения крутится
                         # быстрее кадра, и метры набегают мгновенно
                         wait(0.01)))
targets.append(luke)

# ============================================================ ПРЕПЯТСТВИЕ ===
ob = Target("Препятствие", prefix="ob")
costumes(ob, "obstacle")
ob.add_sound("удар", "лазер.wav")
ob.visible = False

ob.script(40, 40,
          when_recv("играть"),
          repeat_until(eq(V("игра"), num(0)),
                       wait(OBST_EVERY),
                       # клон получает текущий костюм оригинала:
                       # ящик и дроид приходят по очереди
                       next_costume(),
                       clone("Препятствие")))

# ящик и дроид — один спрайт: столкновение считаем по расстоянию,
# поэтому ширина картинки на честность игры не влияет
ob.script(40, 220,
          when_clone(),
          gotoxy(num(OBST_X1), num(OBST_Y)),
          show(),
          repeat_until(OR(lt(xpos(), num(OBST_X2)),
                          AND(lt(dist("Люк"), num(HIT_DIST)),
                              lt(prop_of("y position", "Люк"), num(HIT_Y)))),
                       chx(num(-OBST_SPEED))),
          if_(lt(dist("Люк"), num(HIT_DIST)),
              play("удар"),
              changevar("жизни", num(-1)),
              if_(lt(V("жизни"), num(1)),
                  bcast("конец"))),
          del_clone())
targets.append(ob)

# ============================================================== ЭНЕРГОЯЧЕЙКА =
cell = Target("Ячейка", prefix="cl")
costumes(cell, "cell")
cell.add_sound("блип", "блип.wav")
cell.visible = False

cell.script(40, 40,
            when_recv("играть"),
            repeat_until(eq(V("игра"), num(0)),
                         wait(CELL_EVERY),
                         clone("Ячейка")))

cell.script(40, 220,
            when_clone(),
            gotoxy(num(CELL_X1), num(CELL_Y)),
            show(),
            repeat_until(OR(lt(xpos(), num(CELL_X2)), touching("Люк")),
                         chx(num(-CELL_SPEED))),
            if_(touching("Люк"),
                play("блип"),
                changevar("жизни", num(1))),
            del_clone())
targets.append(cell)

# ============================================================= мониторы =====
MON = []
for name, xv, yv in (("метры", -200, 160), ("жизни", 120, 160)):
    MON.append({"id": VARS[name], "mode": "default", "opcode": "data_variable",
                "params": {"VARIABLE": name}, "spriteName": None,
                "value": ALL_VARS[VARS[name]][1], "width": 0, "height": 0,
                "x": xv, "y": yv, "visible": True, "sliderMin": 0,
                "sliderMax": 100, "isDiscrete": True})

project = {"targets": [t.to_json() for t in targets], "monitors": MON,
           "extensions": [], "meta": {"semver": "3.0.0", "vm": "0.2.0",
                                      "agent": "Star Wars escape"}}

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
assert len(blocks) <= 120, f"блоков {len(blocks)} — больше 120!"
