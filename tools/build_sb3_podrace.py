# -*- coding: utf-8 -*-
"""Новая игра: «Гонки на подах» — гонка по пустыне Татуина, не больше 120 блоков.

Запуск: python3 tools/build_sb3_podrace.py
Результат: star_wars_podrace.sb3

Правила:
  ↑ ↓      — под уходит вверх или вниз,
  400 м    — финиш,
  4 аварии — гонка проиграна.

Скриптов шесть: три на сцене, заезд пода, «фабрика» скал и одна скала-клон.
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
POD = os.path.join(ROOT, "assets", "pod")
FILM = os.path.join(ROOT, "assets", "film")
OUT = os.path.join(ROOT, "star_wars_podrace.sb3")

# --------------------------------------------------------------- переменные --
DISTANCE_TO_WIN = 400    # метров до финиша
LIVES = 4                # сколько аварий выдержит под

VARS = {"метры": "v-dist", "жизни": "v-lives", "игра": "v-run"}
ALL_VARS = {vid: [name, 0] for name, vid in VARS.items()}
ALL_VARS[VARS["жизни"]][1] = LIVES
ALL_VARS[VARS["игра"]][1] = 1

BC = {"играть": "b-play", "конец": "b-over"}
ALL_BC = {bid: name for name, bid in BC.items()}

sb3lib.VARS, sb3lib.BC = VARS, BC
sb3lib.ALL_VARS, sb3lib.ALL_BC = ALL_VARS, ALL_BC

MAN = json.load(open(os.path.join(POD, "manifest.json"), encoding="utf-8"))
SP = {s["slug"]: s for s in MAN["sprites"]}
BD = {b["slug"]: b for b in MAN["backdrops"]}

POD_X, POD_Y = -105, -40
POD_SIZE = 18
POD_TOP, POD_BOTTOM = 100, -110     # куда под может уйти по вертикали
STEP = 10                           # пикселей за кадр при ↑ ↓
ROCK_X1, ROCK_X2 = 275, -290        # откуда скала выезжает и где исчезает
ROCK_SPEED = 8
ROCK_EVERY = 0.8                    # пауза между скалами
SCREEN_WAIT = 2.2                   # сколько висит финиш/авария


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
for slug in ("track", "win", "lose"):
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
          backdrop("Трасса"))

# 400 метров — финиш, кончились жизни — авария. Экран сменяется сам.
st.script(40, 320,
          when_recv("конец"),
          setvar("игра", num(0)),
          if_else(lt(V("жизни"), num(1)),
                  [backdrop("Авария"), play("поражение")],
                  [backdrop("Финиш"), play("победа")]),
          wait(SCREEN_WAIT),
          # игра = 1 ставим до сигнала, иначе под и скалы
          # успевают увидеть «игра = 0» и сразу завершают скрипты
          setvar("игра", num(1)),
          bcast("играть"))
targets.append(st)

# ==================================================================== ПОД ===
pod = Target("Под", prefix="pd")
costumes(pod, "pod")
pod.add_sound("рёв-пода", "рёв-пода.wav")
pod.x, pod.y, pod.size = POD_X, POD_Y, POD_SIZE
pod.script(40, 40,
          when_recv("играть"),
          gotoxy(num(POD_X), num(POD_Y)),
          play("рёв-пода"),
          repeat_until(eq(V("игра"), num(0)),
                       if_(keyp("up arrow"), chy(num(STEP))),
                       if_(keyp("down arrow"), chy(num(-STEP))),
                       # не вылетаем из трассы
                       if_(gt(ypos(), num(POD_TOP)), sety(num(POD_TOP))),
                       if_(lt(ypos(), num(POD_BOTTOM)), sety(num(POD_BOTTOM))),
                       changevar("метры", num(1)),
                       if_(gt(V("метры"), num(DISTANCE_TO_WIN - 1)),
                           bcast("конец")),
                       # без «ждать» петля без движения крутится в сто раз
                       # быстрее кадра, и метры набегают мгновенно
                       wait(0.01)))
targets.append(pod)

# ================================================================== СКАЛА ===
rock = Target("Скала", prefix="rk")
costumes(rock, "rock")
# кадры взрыва добавляем как костюмы 2–4: попал — вспышка вместо скалы
for i in (1, 2, 3):
    rel = "assets/film/sprites/explosion/explosion-%d.png" % i
    im_w, im_h = 170, 170
    add_png(rock, rel, "взрыв-%d" % i, im_w, im_h, im_w / 2, im_h / 2)
rock.add_sound("взрыв", "взрыв.wav")
rock.visible = False
rock.rotation_style = "left-right"   # отражённая скала — просто другая скала

rock.script(40, 40,
            when_recv("играть"),
            repeat_until(eq(V("игра"), num(0)),
                         wait(ROCK_EVERY),
                         clone("Скала")))

rock.script(40, 220,
            when_clone(),
            gotoxy(num(ROCK_X1), rnd(num(-115), num(115))),
            setsize(rnd(num(13), num(21))),
            # половина скал — зеркальные, чтобы трасса не выглядела одинаковой
            if_(gt(rnd(num(0), num(1)), num(0.5)), point(num(-90))),
            show(),
            repeat_until(OR(lt(xpos(), num(ROCK_X2)), touching("Под")),
                         chx(num(-ROCK_SPEED))),
            if_(touching("Под"),
                # взрыв крупнее самой скалы — так видно, что была авария
                setsize(num(55)),
                next_costume(),
                play("взрыв"),
                wait(0.12),
                changevar("жизни", num(-1)),
                if_(lt(V("жизни"), num(1)),
                    bcast("конец"))),
            del_clone())
targets.append(rock)

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
                                      "agent": "Star Wars podrace"}}

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
