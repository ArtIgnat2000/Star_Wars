# -*- coding: utf-8 -*-
"""Собирает готовый проект Scratch 3.0: star_wars_duel.sb3"""
import json
import os
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sb3lib import *          # noqa: F401,F403
import sb3lib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
OUT = os.path.join(ROOT, "star_wars_duel.sb3")

MANIFEST = json.load(open(os.path.join(ASSETS, "manifest.json"), encoding="utf-8"))
SPR = {s["slug"]: s for s in MANIFEST["sprites"]}
BDP = {b["slug"]: b for b in MANIFEST["backdrops"]}
targets = []


def add_costumes(t, slug):
    for c in SPR[slug]["costumes"]:
        t.add_costume(c["name"], c["file"], c["w"], c["h"])


# ============================================================== СЦЕНА =======
stage = Target("Stage", is_stage=True, prefix="st")
for slug in ("01-title", "02-space", "03-naboo", "04-generator", "05-victory"):
    b = BDP[slug]
    data = open(os.path.join(ASSETS, b["file"]), "rb").read()
    md5 = hashlib.md5(data).hexdigest()
    stage.costumes.append({"assetId": md5, "name": b["name"], "bitmapResolution": 1,
                           "md5ext": md5 + ".svg", "dataFormat": "svg",
                           "rotationCenterX": b["w"] / 2, "rotationCenterY": b["h"] / 2,
                           "_data": data})
stage.add_sound("победа", "победа.wav")
stage.add_sound("поражение", "поражение.wav")

stage.script(40, 40,
             when_flag(),
             backdrop("Титул"),
             setvar("очки", num(0)),
             setvar("жизни", num(3)),
             setvar("этап", num(0)),
             setvar("ход", num(0)),
             setvar("хп_мол", num(3)),
             n("data_hidevariable", fields={"VARIABLE": ["хп_мол", VARS["хп_мол"]]}),
             bcast("меню"))

stage.script(40, 300,
             when_recv("старт"),
             setvar("ход", num(0)),
             setvar("очки", num(0)),
             setvar("жизни", num(3)),
             setvar("хп_мол", num(3)),
             setvar("этап", num(1)),
             n("data_hidevariable", fields={"VARIABLE": ["хп_мол", VARS["хп_мол"]]}),
             backdrop("Космос"),
             wait(0.4),
             setvar("ход", num(1)),
             bcast("полетели"))

stage.script(40, 620,
             when_recv("уровень 2"),
             setvar("ход", num(0)),
             wait(0.5),
             setvar("жизни", num(3)),
             setvar("хп_мол", num(3)),
             setvar("этап", num(2)),
             backdrop("Генераторная"),
             n("data_showvariable", fields={"VARIABLE": ["хп_мол", VARS["хп_мол"]]}),
             wait(0.4),
             setvar("ход", num(1)),
             bcast("бой"))

stage.script(40, 940,
             when_recv("победа"),
             setvar("ход", num(0)),
             play("победа"),
             wait(1.6),
             backdrop("Победа"),
             setvar("этап", num(3)))

stage.script(40, 1120,
             when_recv("поражение"),
             setvar("ход", num(0)),
             play("поражение"),
             wait(2.0),
             backdrop("Титул"),
             setvar("этап", num(3)))
targets.append(stage)

# ============================================================ РЕЖИССЁР ======
d = Target("Режиссёр", prefix="dr")
add_costumes(d, "dot")
d.x, d.y, d.visible, d.size = 0, -30, True, 100
d.script(40, 40,
         when_flag(),
         ghost(100),
         gotoxy(num(0), num(-30)),
         forever(
             if_(keyp("space"),
                 if_else(eq(V("этап"), num(0)),
                         [bcast("старт"), wait(1.6)],
                         [if_(eq(V("этап"), num(3)),
                              bcast("старт"), wait(1.6))])),
         ))

d.script(420, 40, when_recv("меню"),
         say("Звёздные войны: Дуэль на Набу. Нажми ПРОБЕЛ, чтобы начать игру.", 5))
d.script(420, 160, when_recv("полетели"),
         say("Уровень 1 — космос. Стрелки ← → манёвр, ПРОБЕЛ — огонь. Сбей 8 дроидов!", 5))
d.script(420, 280, when_recv("бой"),
         wait(0.6),
         say("Уровень 2 — Дарт Мол! ← → бег, ↑ прыжок, ПРОБЕЛ удар мечом, ↓ блок.", 6))
d.script(420, 420, when_recv("победа"),
         wait(1.8),
         say("Победа! Тёмная сторона отступила. Нажми ПРОБЕЛ, чтобы сыграть снова.", 6))
d.script(420, 560, when_recv("поражение"),
         wait(2.2),
         say("Поражение... Нажми ПРОБЕЛ, чтобы попробовать снова.", 5))
targets.append(d)

# ========================================================== ИСТРЕБИТЕЛЬ =====
ship = Target("Истребитель", prefix="sh")
add_costumes(ship, "naboo-fighter")
ship.add_sound("лазер", "лазер.wav")
ship.add_sound("взрыв", "взрыв.wav")
ship.add_sound("меч-выкл", "меч-выкл.wav")
ship.visible = False
ship.size = 55
ship.y = -110

ship.script(40, 40, when_flag(), hide())
ship.script(40, 120, when_recv("старт"), hide())
ship.script(40, 200, when_recv("уровень 2"), hide())
ship.script(40, 280, when_recv("поражение"), hide())
ship.script(40, 360, when_recv("победа"), hide())

ship.script(40, 440,
            when_recv("полетели"),
            show(),
            setsize(55),
            rotstyle("don't rotate"),
            point(90),
            gotoxy(num(0), num(-110)),
            ghost(0),
            switch_costume("двигатель-1"))

ship.script(420, 40,
            when_recv("полетели"),
            repeat_until(eq(V("ход"), num(0)),
                         if_(keyp("right arrow"), chx(num(9))),
                         if_(keyp("left arrow"), chx(num(-9))),
                         if_(gt(xpos(), num(200)), setx(num(200))),
                         if_(lt(xpos(), num(-200)), setx(num(-200))),
                         next_costume(),
                         wait(0.07)))

ship.script(420, 420,
            when_recv("полетели"),
            repeat_until(eq(V("ход"), num(0)),
                         if_(keyp("space"),
                             clone("Лазер"),
                             play("лазер"),
                             wait(0.25)),
                         wait(0.02)))

ship.script(420, 700,
            when_recv("полетели"),
            wait_until(gt(V("очки"), num(79))),
            bcast("уровень 2"))

ship.script(420, 820,
            when_recv("урон"),
            if_(eq(V("этап"), num(1)),
                changevar("жизни", num(-1)),
                play("взрыв"),
                repeat(3,
                       ghost(65), wait(0.08), ghost(0), wait(0.08)),
                if_(lt(V("жизни"), num(1)),
                    bcast("поражение"), hide())))
targets.append(ship)

# =============================================================== ЛАЗЕР ======
lz = Target("Лазер", prefix="lz")
add_costumes(lz, "laser")
lz.visible = False
lz.script(40, 40, when_flag(), hide())
lz.script(40, 160,
          when_clone(),
          switch_costume("синий"),
          gotoxy(prop_of("x position", "Истребитель"),
                 add(prop_of("y position", "Истребитель"), num(46))),
          show(),
          repeat(26,
                 chy(num(15)),
                 if_(touching("Дроид-истребитель"), del_clone()),
                 if_(gt(ypos(), num(188)), del_clone())),
          del_clone())
targets.append(lz)

# ========================================================= ЛАЗЕР ВРАГА =====
el = Target("Лазер врага", prefix="el")
add_costumes(el, "enemy-laser")
el.add_sound("лазер-врага", "лазер-врага.wav")
el.visible = False
el.script(40, 40, when_flag(), hide())
el.script(40, 160,
          when_clone(),
          switch_costume("красный"),
          gotoxy(V("спавн_x"), V("спавн_y")),
          show(),
          play("лазер-врага"),
          repeat_until(OR(touching("Истребитель"), lt(ypos(), num(-178))),
                       chy(num(-9))),
          if_(touching("Истребитель"), bcast("урон")),
          del_clone())
targets.append(el)

# ==================================================== ДРОИД-ИСТРЕБИТЕЛЬ ====
dr = Target("Дроид-истребитель", prefix="df")
add_costumes(dr, "droid-fighter")
dr.add_sound("взрыв", "взрыв.wav")
dr.visible = False
dr.script(40, 40, when_flag(), hide())
dr.script(40, 160, when_recv("уровень 2"), hide())
dr.script(40, 240, when_recv("старт"), hide())

dr.script(40, 320,
          when_recv("полетели"),
          repeat_until(eq(V("ход"), num(0)),
                       clone("_myself_"),
                       wait(rnd(num(0.55), num(1.15)))))

dr.script(420, 40,
          when_clone(),
          show(),
          setsize(42),
          switch_costume("крылья-открыты"),
          gotoxy(rnd(num(-205), num(205)), num(196)),
          repeat_until(OR(lt(ypos(), num(-196)), eq(V("ход"), num(0))),
                       chy(num(-3.6)),
                       switch_costume("крылья-открыты"),
                       if_(touching("Лазер"),
                           changevar("очки", num(10)),
                           play("взрыв"),
                           setvar("спавн_x", xpos()),
                           setvar("спавн_y", ypos()),
                           clone("Взрыв"),
                           wait(0.03),
                           del_clone()),
                       if_(touching("Истребитель"),
                           bcast("урон"),
                           setvar("спавн_x", xpos()),
                           setvar("спавн_y", ypos()),
                           clone("Взрыв"),
                           del_clone()),
                       if_(gt(rnd(num(1), num(100)), num(98)),
                           setvar("спавн_x", xpos()),
                           setvar("спавн_y", subn(ypos(), num(18))),
                           clone("Лазер врага")),
                       wait(0.04)),
          del_clone())
targets.append(dr)

# =============================================================== ВЗРЫВ ======
ex = Target("Взрыв", prefix="ex")
add_costumes(ex, "explosion")
ex.visible = False
ex.script(40, 40, when_flag(), hide())
ex.script(40, 160,
          when_clone(),
          gotoxy(V("спавн_x"), V("спавн_y")),
          setsize(58),
          switch_costume("кадр-1"),
          goto_front(),
          show(),
          next_costume(), wait(0.06),
          next_costume(), wait(0.07),
          next_costume(), wait(0.09),
          del_clone())
targets.append(ex)

# ========================================================== ПЛАЗМА-ВРАТА ====
pg = Target("Плазма-врата", prefix="pg")
add_costumes(pg, "plasma-gate")
pg.visible = False
pg.x, pg.y, pg.size = -205, -60, 60
pg.script(40, 40, when_flag(), hide())
pg.script(40, 160, when_recv("старт"), hide())
pg.script(40, 240,
          when_recv("бой"),
          show(),
          setsize(60),
          gotoxy(num(-205), num(-60)),
          switch_costume("закрыто"),
          repeat_until(eq(V("ход"), num(0)),
                       switch_costume("закрыто"), wait(1.6),
                       switch_costume("открыто"), wait(0.9)))
targets.append(pg)

# ============================================================= КВАЙ-ГОН =====
qg = Target("Квай-Гон", prefix="qg")
add_costumes(qg, "quigon")
qg.add_sound("меч-вкл", "меч-вкл.wav")
qg.visible = False
qg.x, qg.y, qg.size, qg.rotation_style = -195, -45, 70, "left-right"
qg.script(40, 40, when_flag(), hide())
qg.script(40, 160, when_recv("старт"), hide())
qg.script(40, 240, when_recv("победа"), hide())
qg.script(40, 320, when_recv("поражение"), hide())
qg.script(40, 400,
          when_recv("бой"),
          show(),
          setsize(70),
          rotstyle("left-right"),
          point(90),
          gotoxy(num(-195), num(-45)),
          ghost(0),
          switch_costume("стойка"),
          play("меч-вкл"),
          wait(1.4),
          switch_costume("удар-1"), wait(0.35),
          switch_costume("удар-2"), wait(0.45),
          switch_costume("ранен"),
          wait(1.3),
          repeat(6, n("looks_changeeffectby", {"CHANGE": num(16)},
                      {"EFFECT": ["GHOST", None]}), wait(0.05)),
          hide())
targets.append(qg)

# ============================================================== ОБИ-ВАН ====
ob = Target("Оби-Ван", prefix="ob")
add_costumes(ob, "obiwan")
ob.add_sound("меч-вкл", "меч-вкл.wav")
ob.add_sound("удар-меча", "удар-меча.wav")
ob.visible = False
ob.x, ob.y, ob.size, ob.rotation_style = -90, -45, 70, "left-right"
ob.script(40, 40, when_flag(), hide())
ob.script(40, 160, when_recv("старт"), hide())

ob.script(40, 240,
          when_recv("бой"),
          show(),
          setsize(70),
          rotstyle("left-right"),
          point(90),
          gotoxy(num(-90), num(-45)),
          ghost(0),
          switch_costume("стойка"),
          setvar("блок_игрок", num(0)),
          setvar("атака", num(0)),
          setvar("прыжок", num(0)),
          setvar("движется", num(0)))

# --- движение ---
ob.script(420, 40,
          when_recv("бой"),
          repeat_until(eq(V("ход"), num(0)),
                       setvar("движется", num(0)),
                       if_(OR(keyp("right arrow"), keyp("d")),
                           chx(num(6)), setvar("движется", num(1))),
                       if_(OR(keyp("left arrow"), keyp("a")),
                           chx(num(-6)), setvar("движется", num(1))),
                       if_(gt(xpos(), num(160)), setx(num(160))),
                       if_(lt(xpos(), num(-160)), setx(num(-160))),
                       if_else(gt(xpos(), prop_of("x position", "Дарт Мол")),
                               [point(-90)], [point(90)]),
                       if_(AND(OR(keyp("up arrow"), keyp("w")), eq(V("прыжок"), num(0))),
                           setvar("прыжок", num(1)),
                           switch_costume("прыжок"),
                           repeat(12, chy(num(11)), wait(0.02)),
                           repeat(12, chy(num(-11)), wait(0.02)),
                           setvar("прыжок", num(0)),
                           switch_costume("стойка")),
                       if_else(AND(eq(V("движется"), num(1)),
                                   AND(eq(V("атака"), num(0)),
                                       AND(eq(V("блок_игрок"), num(0)),
                                           eq(V("прыжок"), num(0))))),
                               [next_costume(),
                                if_(gt(costume_number(), num(5)), switch_costume("шаг-1"))],
                               [if_(AND(eq(V("атака"), num(0)),
                                        AND(eq(V("блок_игрок"), num(0)),
                                            eq(V("прыжок"), num(0)))),
                                    switch_costume("стойка"))])))

# --- удар ---
ob.script(900, 40,
          when_recv("бой"),
          repeat_until(eq(V("ход"), num(0)),
                       if_(AND(keyp("space"), eq(V("атака"), num(0))),
                           setvar("атака", num(1)),
                           switch_costume("удар-1"),
                           wait(0.1),
                           switch_costume("удар-2"),
                           play("удар-меча"),
                           if_(lt(dist("Дарт Мол"), num(100)),
                               setvar("спавн_x", prop_of("x position", "Дарт Мол")),
                               setvar("спавн_y", add(prop_of("y position", "Дарт Мол"),
                                                     num(35))),
                               clone("Искры"),
                               if_else(eq(V("блок_мол"), num(1)),
                                       [],
                                       [changevar("хп_мол", num(-1)),
                                        if_(lt(V("хп_мол"), num(1)),
                                            bcast("победа"))])),
                           wait(0.2),
                           switch_costume("стойка"),
                           setvar("атака", num(0)))))

# --- блок ---
ob.script(900, 620,
          when_recv("бой"),
          repeat_until(eq(V("ход"), num(0)),
                       if_else(OR(keyp("down arrow"), keyp("s")),
                               [setvar("блок_игрок", num(1)),
                                if_(eq(V("атака"), num(0)), switch_costume("блок"))],
                               [setvar("блок_игрок", num(0))])))

# --- получил удар ---
ob.script(900, 900,
          when_recv("урон"),
          if_(eq(V("этап"), num(2)),
              switch_costume("ранен"),
              wait(0.32),
              if_(eq(V("атака"), num(0)), switch_costume("стойка"))))

ob.script(420, 900,
          when_recv("победа"),
          repeat(3, chy(num(16)), wait(0.12), chy(num(-16)), wait(0.12)),
          switch_costume("стойка"))

ob.script(1180, 900,
          when_recv("поражение"),
          switch_costume("ранен"),
          wait(1.2),
          repeat(8, n("looks_changeeffectby", {"CHANGE": num(12)},
                      {"EFFECT": ["GHOST", None]}), wait(0.06)),
          hide())
targets.append(ob)

# ============================================================= ДАРТ МОЛ ====
ml = Target("Дарт Мол", prefix="ml")
add_costumes(ml, "maul")
ml.add_sound("удар-меча", "удар-меча.wav")
ml.add_sound("гудение-меча", "гудение-меча.wav")
ml.visible = False
ml.x, ml.y, ml.size, ml.rotation_style = 120, -45, 70, "left-right"
ml.script(40, 40, when_flag(), hide())
ml.script(40, 160, when_recv("старт"), hide())

ml.script(40, 240,
          when_recv("бой"),
          show(),
          setsize(70),
          rotstyle("left-right"),
          point(-90),
          gotoxy(num(120), num(-45)),
          ghost(0),
          switch_costume("стойка"),
          setvar("блок_мол", num(0)))

ml.script(420, 40,
          when_recv("бой"),
          repeat_until(eq(V("ход"), num(0)),
                       if_else(gt(xpos(), prop_of("x position", "Оби-Ван")),
                               [point(-90)], [point(90)]),
                       if_else(gt(dist("Оби-Ван"), num(92)),
                               [if_else(gt(xpos(), prop_of("x position", "Оби-Ван")),
                                        [chx(num(-5))], [chx(num(5))]),
                                next_costume(),
                                if_(gt(costume_number(), num(5)),
                                    switch_costume("шаг-1"))],
                               [if_else(gt(rnd(num(1), num(10)), num(7)),
                                        [setvar("блок_мол", num(1)),
                                         switch_costume("блок"),
                                         wait(0.5),
                                         setvar("блок_мол", num(0)),
                                         switch_costume("стойка")],
                                        [switch_costume("удар-1"),
                                         wait(0.15),
                                         switch_costume("удар-2"),
                                         play("удар-меча"),
                                         if_(AND(eq(V("блок_игрок"), num(0)),
                                                 eq(V("прыжок"), num(0))),
                                             changevar("жизни", num(-1)),
                                             bcast("урон"),
                                             if_(lt(V("жизни"), num(1)),
                                                 bcast("поражение"))),
                                         wait(0.5),
                                         switch_costume("стойка"),
                                         if_else(gt(xpos(), prop_of("x position", "Оби-Ван")),
                                                 [chx(num(24))], [chx(num(-24))])])]),
                       wait(0.06)))

ml.script(900, 40,
          when_recv("победа"),
          switch_costume("ранен"),
          wait(1.3),
          repeat(8, n("looks_changeeffectby", {"CHANGE": num(12)},
                      {"EFFECT": ["GHOST", None]}), wait(0.06)),
          hide())

ml.script(900, 320,
          when_recv("поражение"),
          switch_costume("стойка"),
          wait(2.0),
          hide())
targets.append(ml)

# ================================================================ ИСКРЫ ====
sp = Target("Искры", prefix="sp")
add_costumes(sp, "sparks")
sp.visible = False
sp.script(40, 40, when_flag(), hide())
sp.script(40, 160,
          when_clone(),
          gotoxy(V("спавн_x"), V("спавн_y")),
          setsize(70),
          switch_costume("кадр-1"),
          goto_front(),
          show(),
          wait(0.05),
          switch_costume("кадр-2"),
          wait(0.07),
          del_clone())
targets.append(sp)

# ============================================================ мониторы =====
MON = []
for name, x, y, vis in (("очки", -212, 158, True), ("жизни", -92, 158, True),
                        ("хп_мол", 48, 158, False)):
    MON.append({"id": VARS[name], "mode": "default", "opcode": "data_variable",
                "params": {"VARIABLE": name}, "spriteName": None, "value": 0,
                "width": 0, "height": 0, "x": x, "y": y, "visible": vis,
                "sliderMin": 0, "sliderMax": 100, "isDiscrete": True})

# ============================================================ упаковка =====
project = {"targets": [t.to_json() for t in targets], "monitors": MON,
           "extensions": [], "meta": {"semver": "3.0.0", "vm": "0.2.0",
                                      "agent": "Star Wars asset pack"}}

assets = {}
for t in targets:
    for c in t.costumes + t.sounds:
        assets[c["md5ext"]] = c["_data"]

with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("project.json", json.dumps(project, ensure_ascii=False))
    for name, data in assets.items():
        z.writestr(name, data)

nb = sum(len(t.blocks) for t in targets)
print(f"собрано: {OUT}")
print(f"  спрайтов: {len(targets)-1}, блоков: {nb}, ассетов в архиве: {len(assets)}, "
      f"размер: {os.path.getsize(OUT)//1024} КБ")
