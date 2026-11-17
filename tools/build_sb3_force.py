# -*- coding: utf-8 -*-
"""Новая игра: «Дагоба: тренировка Силы» — камни падают, их поднимают Силой.

Запуск: python3 tools/build_sb3_force.py
Результат: star_wars_force.sb3

Правила:
  мышь    — кольцо «Сила» летит за курсором,
  10 камней — истребитель поднят из болота (победа),
  3 утонувших камня — «Не хватило силы».

Управление мышью — впервые в наборе: не надо запоминать клавиши, ребёнок просто
водит курсором. Скриптов шесть: три на сцене, кольцо, «фабрика» камней
и один камень-клон; у Йоды свои две реплики.
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
FORCE = os.path.join(ROOT, "assets", "force")
OUT = os.path.join(ROOT, "star_wars_force.sb3")

# --------------------------------------------------------------- переменные --
WIN_ROCKS = 10            # сколько камней поймать
LIVES = 3                 # сколько камней можно уронить

VARS = {"камни": "v-rocks", "жизни": "v-lives", "игра": "v-run",
        "падение": "v-fall", "пауза": "v-gap"}
ALL_VARS = {vid: [name, 0] for name, vid in VARS.items()}
ALL_VARS[VARS["жизни"]][1] = LIVES
ALL_VARS[VARS["игра"]][1] = 1
ALL_VARS[VARS["падение"]][1] = -3
ALL_VARS[VARS["пауза"]][1] = 1.1

BC = {"играть": "b-play", "конец": "b-over"}
ALL_BC = {bid: name for name, bid in BC.items()}

sb3lib.VARS, sb3lib.BC = VARS, BC
sb3lib.ALL_VARS, sb3lib.ALL_BC = ALL_VARS, ALL_BC

MAN = json.load(open(os.path.join(FORCE, "manifest.json"), encoding="utf-8"))
SP = {s["slug"]: s for s in MAN["sprites"]}
BD = {b["slug"]: b for b in MAN["backdrops"]}

# ------------------------------------------------------------------- числа ---
LUKE_X, LUKE_SIZE = -165, 52          # ноги на y = −150
LUKE_Y = -150 + int(300 * LUKE_SIZE / 200)
YODA_X, YODA_SIZE = 185, 55
YODA_Y = -150 + int(150 * YODA_SIZE / 200)
ROCK_TOP = 190                        # откуда камень падает
ROCK_WATER = -145                     # ниже этого камень утонул
FALL = -3                             # скорость падения (её же ускоряет счёт)
FALL_STEP = -0.06                     # на столько быстрее падают камни за каждый пойманный
ROCK_EVERY = 1.1          # стартовая пауза между камнями (переменная «пауза»)
GAP_STEP = -0.05          # темп растёт с каждым пойманным камнем
ORB_EVERY = 7             # как часто прилетает «свет Силы»
ORB_FALL = -2
SCREEN_WAIT = 2.5


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
for slug in ("swamp", "win", "lose"):
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
          setvar("камни", num(0)),
          setvar("жизни", num(LIVES)),
          setvar("падение", num(FALL)),
          setvar("пауза", num(ROCK_EVERY)),
          setvar("игра", num(1)),
          backdrop("Болото"))

# 10 камней — истребитель поднят, три утонувших — провал. Экран сменяется сам.
st.script(40, 320,
          when_recv("конец"),
          setvar("игра", num(0)),
          if_else(lt(V("жизни"), num(1)),
                  [backdrop("Провал"), play("поражение")],
                  [backdrop("Победа"), play("победа")]),
          wait(SCREEN_WAIT),
          # игра = 1 ставим до сигнала, иначе кольцо и «фабрика»
          # успевают увидеть «игра = 0» и сразу завершают скрипты
          setvar("игра", num(1)),
          bcast("играть"))
targets.append(st)

# =================================================================== ЛЮК ====
luke = Target("Люк", prefix="lk")
costumes(luke, "luke")
luke.x, luke.y, luke.size = LUKE_X, LUKE_Y, LUKE_SIZE
luke.script(40, 40, when_flag(), gotoxy(num(LUKE_X), num(LUKE_Y)))
targets.append(luke)

# =================================================================== ЙОДА ===
yoda = Target("Йода", prefix="yd")
costumes(yoda, "yoda")
yoda.x, yoda.y, yoda.size = YODA_X, YODA_Y, YODA_SIZE
yoda.script(40, 40,
            when_recv("играть"),
            # подсказка на старте и похвала на середине
            say("Камни падают. Подними их Силой!", 2.5),
            wait_until(gt(V("камни"), num(4))),
            say("Хорошо. Сила течёт в тебе.", 2))

yoda.script(40, 320,
            when_recv("играть"),
            wait_until(lt(V("жизни"), num(2))),
            say("Осторожно! Спокойно, как учил я.", 2))

yoda.script(40, 220,
            when_recv("конец"),
            if_else(lt(V("жизни"), num(1)),
                    [say("Не сдавайся. Ещё раз!", 2)],
                    [say("Сила с тобой! Молодец.", 2)]))
targets.append(yoda)

# ================================================================== СИЛА ====
force = Target("Сила", prefix="fr")
costumes(force, "ring")
force.script(40, 40,
             when_recv("играть"),
             goto_front(),
             repeat_until(eq(V("игра"), num(0)),
                          # кольцо летит за курсором (на планшете — за пальцем)
                          goto_mouse(),
                          wait(0.01)))
targets.append(force)

# ================================================================= КАМЕНЬ ===
rock = Target("Камень", prefix="rk")
costumes(rock, "rock")
rock.add_sound("сила", "сила.wav")
rock.add_sound("всплеск", "всплеск.wav")
rock.visible = False

rock.script(40, 40,
            when_recv("играть"),
            repeat_until(eq(V("игра"), num(0)),
                         wait(V("пауза")),
                         clone("Камень")))

rock.script(40, 200,
            when_clone(),
            gotoxy(rnd(num(-215), num(215)), num(ROCK_TOP)),
            setsize(rnd(num(75), num(115))),
            show(),
            # падает, пока не поймали или пока не утонул
            repeat_until(OR(lt(ypos(), num(ROCK_WATER)), touching("Сила")),
                         chy(V("падение"))),
            if_else(touching("Сила"),
                    # поймали: камень уходит вверх, счёт растёт, падать
                    # камни начинают быстрее
                    [play("сила"),
                     repeat(8, chy(num(9))),
                     changevar("камни", num(1)),
                     changevar("падение", num(FALL_STEP)),
                     changevar("пауза", num(GAP_STEP)),
                     if_(gt(V("камни"), num(WIN_ROCKS - 1)),
                         bcast("конец"))],
                    # утонул: минус жизнь
                    [play("всплеск"),
                     changevar("жизни", num(-1)),
                     if_(lt(V("жизни"), num(1)),
                         bcast("конец"))]),
            del_clone())
targets.append(rock)

# =================================================================== СВЕТ ====
orb = Target("Свет", prefix="ob")
costumes(orb, "orb")
orb.add_sound("блип", "блип.wav")
orb.visible = False

orb.script(40, 40,
           when_recv("играть"),
           repeat_until(eq(V("игра"), num(0)),
                        wait(ORB_EVERY),
                        clone("Свет")))

orb.script(40, 200,
           when_clone(),
           gotoxy(rnd(num(-215), num(215)), num(ROCK_TOP)),
           show(),
           # свет плывёт медленнее камня и не тонет «в минус»: не поймал — улетел
           repeat_until(OR(lt(ypos(), num(ROCK_WATER)), touching("Сила")),
                        chy(num(ORB_FALL))),
           if_(touching("Сила"),
               play("блип"),
               changevar("жизни", num(1))),
           del_clone())
targets.append(orb)

# ============================================================= мониторы =====
MON = []
for name, xv, yv in (("камни", -200, 160), ("жизни", 120, 160)):
    MON.append({"id": VARS[name], "mode": "default", "opcode": "data_variable",
                "params": {"VARIABLE": name}, "spriteName": None,
                "value": ALL_VARS[VARS[name]][1], "width": 0, "height": 0,
                "x": xv, "y": yv, "visible": True, "sliderMin": 0,
                "sliderMax": 100, "isDiscrete": True})

project = {"targets": [t.to_json() for t in targets], "monitors": MON,
           "extensions": [], "meta": {"semver": "3.0.0", "vm": "0.2.0",
                                      "agent": "Star Wars force training"}}

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
assert len(blocks) <= 150, f"блоков {len(blocks)} — больше 150!"
