# -*- coding: utf-8 -*-
"""Лёгкая версия игры: только дуэль на световых мечах.

Запуск: python3 tools/build_sb3_lite.py
Результат: star_wars_duel_lite.sb3

Правила, которые видит ребёнок:
  1. На титуле выбираешь героя: Квай-Гон или Оби-Ван (← →, ПРОБЕЛ).
  2. ПРОБЕЛ — удар мечом (герой встаёт в позу «атака»).
  3. ↓ — блок (герой встаёт в позу «блок»), удар Мола не отнимает жизнь.
  4. У каждого 3 жизни. Кто первый теряет все — проиграл.

Скрипты нарочно короткие: одна петля «повторять пока игра = 1» на персонажа,
никаких списков, клонов и вложенных условий.
"""
import json
import os
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sb3lib
from sb3lib import *      # noqa: F401,F403

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
LITE = os.path.join(ASSETS, "lite")
OUT = os.path.join(ROOT, "star_wars_duel_lite.sb3")

# --------------------------------------------------------------- переменные --
VARS = {
    "выбор": "v-choice",        # 1 — Квай-Гон, 2 — Оби-Ван
    "хп_героя": "v-hp-hero",
    "хп_мола": "v-hp-maul",
    "блок": "v-block",          # 1, пока герой держит ↓
    "мол_бьёт": "v-maulatk",    # 1, пока Мол замахивается
    "игра": "v-run",            # 1, пока идёт бой
}
ALL_VARS = {vid: [name, 0] for name, vid in VARS.items()}
ALL_VARS[VARS["выбор"]][1] = 1
ALL_VARS[VARS["хп_героя"]][1] = 3
ALL_VARS[VARS["хп_мола"]][1] = 3

BC = {"выбор": "b-choice", "бой": "b-fight", "победа": "b-win",
      "поражение": "b-lose", "искры": "b-sparks"}
ALL_BC = {bid: name for name, bid in BC.items()}

# подменяем таблицы в библиотеке — дальше все помощники работают с lite-именами
sb3lib.VARS, sb3lib.BC = VARS, BC
sb3lib.ALL_VARS, sb3lib.ALL_BC = ALL_VARS, ALL_BC

MAN = json.load(open(os.path.join(LITE, "manifest.json"), encoding="utf-8"))
SP = {s["slug"]: s for s in MAN["sprites"]}
BD = {b["slug"]: b for b in MAN["backdrops"]}
VEC = {s["slug"]: s for s in
       json.load(open(os.path.join(ASSETS, "manifest.json"), encoding="utf-8"))["sprites"]}

HERO_X, MAUL_X, CHAR_Y = -110, 130, -40
TITLE_Y = -10          # на титуле герои стоят чуть выше, под подписями
DUEL_SIZE, TITLE_SIZE = 37, 31
import hashlib


def add_png(t, rel, name, w, h):
    data = open(os.path.join(ROOT, rel), "rb").read()
    md5 = hashlib.md5(data).hexdigest()
    t.costumes.append({"assetId": md5, "name": name, "bitmapResolution": 1,
                       "md5ext": md5 + ".png", "dataFormat": "png",
                       "rotationCenterX": w / 2, "rotationCenterY": h / 2,
                       "_data": data})


def lite_cosutumes(t, slug):
    s = SP[slug]
    for c in s["costumes"]:
        add_png(t, c["file"], c["name"], s["w"], s["h"])


targets = []

# ================================================================= СЦЕНА ====
st = Target("Stage", is_stage=True, prefix="st")
for slug in ("choice", "duel", "win", "lose"):
    b = BD[slug]
    data = open(os.path.join(ROOT, b["file"]), "rb").read()
    md5 = hashlib.md5(data).hexdigest()
    st.costumes.append({"assetId": md5, "name": b["name"], "bitmapResolution": 1,
                        "md5ext": md5 + ".png", "dataFormat": "png",
                        "rotationCenterX": 240, "rotationCenterY": 180, "_data": data})

st.add_sound("победа", "победа.wav")
st.add_sound("поражение", "поражение.wav")

HIDE_HP = [n("data_hidevariable", fields={"VARIABLE": ["хп_героя", VARS["хп_героя"]]}),
           n("data_hidevariable", fields={"VARIABLE": ["хп_мола", VARS["хп_мола"]]})]
SHOW_HP = [n("data_showvariable", fields={"VARIABLE": ["хп_героя", VARS["хп_героя"]]}),
           n("data_showvariable", fields={"VARIABLE": ["хп_мола", VARS["хп_мола"]]})]

st.script(40, 40,
          when_flag(),
          setvar("игра", num(0)),
          setvar("выбор", num(1)),
          backdrop("Выбор героя"),
          bcast("выбор"))

# выбор героя: ← → и старт по ПРОБЕЛу
st.script(40, 220,
          when_recv("выбор"),
          setvar("хп_героя", num(3)),
          setvar("хп_мола", num(3)),
          setvar("игра", num(0)),
          backdrop("Выбор героя"),
          *HIDE_HP,
          wait_until(NOT(keyp("space"))),   # не начинаем бой с зажатой клавиши
          repeat_until(eq(V("игра"), num(1)),
                       if_(keyp("left arrow"), setvar("выбор", num(1))),
                       if_(keyp("right arrow"), setvar("выбор", num(2))),
                       if_(keyp("space"),
                           setvar("игра", num(1)),
                           backdrop("Дуэль"),
                           bcast("бой")),
                       wait(0.03)))

# конец боя
st.script(40, 520,
          when_recv("победа"),
          wait(0.8),
          backdrop("Победа"),
          play("победа"),
          wait(1.5),
          wait_until(NOT(keyp("space"))),
          wait_until(keyp("space")),
          wait(0.3),
          bcast("выбор"))

st.script(40, 760,
          when_recv("поражение"),
          wait(0.4),
          backdrop("Поражение"),
          play("поражение"),
          wait(1.2),
          wait_until(NOT(keyp("space"))),
          wait_until(keyp("space")),
          wait(0.3),
          bcast("выбор"))

st.script(40, 1000, when_recv("бой"), *SHOW_HP)
targets.append(st)

# ================================================================ ГЕРОИ =====
# один и тот же короткий набор скриптов для Квай-Гона (1) и Оби-Вана (2)
for slug, name, prefix, number, title_x, sound in (
        ("quigon", "Квай-Гон", "qg", 1, -110, "меч-вкл"),
        ("obiwan", "Оби-Ван", "ob", 2, 110, "меч-вкл")):
    t = Target(name, prefix=prefix)
    lite_cosutumes(t, slug)
    t.add_sound("меч-вкл", "меч-вкл.wav")
    t.add_sound("удар-меча", "удар-меча.wav")
    t.visible = False
    t.script(40, 40, when_flag(), hide())

    # титул: оба героя стоят на своих местах, стрелка показывает выбранного
    t.script(40, 160,
             when_recv("выбор"),
             gotoxy(num(title_x), num(TITLE_Y)),
             setsize(TITLE_SIZE),
             switch_costume("стойка"),
             show())

    # сам бой
    t.script(40, 320,
             when_recv("бой"),
             if_(eq(V("выбор"), num(number)),
                 gotoxy(num(HERO_X), num(CHAR_Y)),
                 setsize(DUEL_SIZE),
                 switch_costume("стойка"),
                 play("меч-вкл"),
                 repeat_until(eq(V("игра"), num(0)),
                              if_(keyp("down arrow"),
                                  setvar("блок", num(1)),
                                  switch_costume("блок")),
                              if_(AND(keyp("space"), eq(V("блок"), num(0))),
                                  switch_costume("атака"),
                                  wait(0.10),
                                  play("удар-меча"),
                                  bcast("искры"),
                                  changevar("хп_мола", num(-1)),
                                  wait(0.30)),
                              if_(AND(NOT(keyp("down arrow")), NOT(keyp("space"))),
                                  setvar("блок", num(0)),
                                  switch_costume("стойка")),
                              wait(0.03))))

    # финал
    t.script(40, 760,
             when_recv("победа"),
             if_(eq(V("выбор"), num(number)),
                 switch_costume("стойка"),
                 setvar("блок", num(0)),
                 say("Мы победили!", 2.5)))

    t.script(40, 920,
             when_recv("поражение"),
             if_(eq(V("выбор"), num(number)),
                 switch_costume("стойка"),
                 setvar("блок", num(0)),
                 say("Он слишком силён…", 2.5)))
    targets.append(t)

# ============================================================ ДАРТ МОЛ ======
ml = Target("Дарт Мол", prefix="ml")
lite_cosutumes(ml, "maul")
ml.add_sound("гудение-меча", "гудение-меча.wav")
ml.add_sound("удар-меча", "удар-меча.wav")
ml.visible = False
ml.script(40, 40, when_flag(), hide())
ml.script(40, 160, when_recv("выбор"), hide())

ml.script(40, 300,
          when_recv("бой"),
          gotoxy(num(MAUL_X), num(CHAR_Y)),
          setsize(DUEL_SIZE),
          switch_costume("стойка"),
          show(),
          play("гудение-меча"),
          repeat_until(eq(V("игра"), num(0)),
                       # закрылся, потом замахнулся — удар
                       switch_costume("блок"),
                       wait(0.9),
                       switch_costume("атака"),
                       setvar("мол_бьёт", num(1)),
                       wait(0.25),
                       bcast("искры"),
                       play("удар-меча"),
                       if_(eq(V("блок"), num(0)), changevar("хп_героя", num(-1))),
                       wait(0.25),
                       switch_costume("стойка"),
                       setvar("мол_бьёт", num(0)),
                       wait(0.5),
                       # проверяем, не кончился ли бой
                       if_(lt(V("хп_героя"), num(1)),
                           setvar("игра", num(0)),
                           bcast("поражение")),
                       if_(lt(V("хп_мола"), num(1)),
                           setvar("игра", num(0)),
                           bcast("победа"))))

ml.script(40, 900,
          when_recv("победа"),
          wait(0.5),
          switch_costume("стойка"),
          repeat(10, ghost(num(10))),
          hide())

ml.script(40, 1080,
          when_recv("поражение"),
          switch_costume("стойка"),
          say("Ха-ха-ха!", 2.5))
targets.append(ml)

# ============================================================== СТРЕЛКА =====
ar = Target("Стрелка", prefix="ar")
lite_cosutumes(ar, "arrow")
ar.visible = False
ar.script(40, 40, when_flag(), hide())
ar.script(40, 160,
          when_recv("выбор"),
          gotoxy(num(-110), num(88)),
          show(),
          repeat_until(eq(V("игра"), num(1)),
                       if_else(eq(V("выбор"), num(1)),
                               [gotoxy(num(-110), num(88))],
                               [gotoxy(num(110), num(88))]),
                       wait(0.05)),
          hide())
targets.append(ar)

# =============================================================== ИСКРЫ =====
sp = Target("Искры", prefix="sp")
for c in VEC["sparks"]["costumes"]:
    sp.add_costume(c["name"], c["file"], c["w"], c["h"])
sp.add_sound("гудение-меча", "гудение-меча.wav")
sp.visible = False
sp.script(40, 40, when_flag(), hide())
sp.script(40, 160,
          when_recv("искры"),
          gotoxy(num(10), num(-10)),
          setsize(45),
          switch_costume("кадр-1"),
          goto_front(),
          show(),
          wait(0.05),
          switch_costume("кадр-2"),
          wait(0.07),
          hide())
targets.append(sp)

# ============================================================= мониторы =====
MON = []
for name, x, y, vis in (("хп_героя", -150, 150, False), ("хп_мола", 40, 150, False)):
    MON.append({"id": VARS[name], "mode": "default", "opcode": "data_variable",
                "params": {"VARIABLE": name}, "spriteName": None, "value": 3,
                "width": 0, "height": 0, "x": x, "y": y, "visible": vis,
                "sliderMin": 0, "sliderMax": 100, "isDiscrete": True})

project = {"targets": [t.to_json() for t in targets], "monitors": MON,
           "extensions": [], "meta": {"semver": "3.0.0", "vm": "0.2.0",
                                      "agent": "Star Wars duel (lite)"}}

assets = {}
for t in targets:
    for c in t.costumes + t.sounds:
        assets[c["md5ext"]] = c["_data"]

with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("project.json", json.dumps(project, ensure_ascii=False))
    for fname, data in assets.items():
        z.writestr(fname, data)

nb = sum(len(t.blocks) for t in targets)
print(f"собрано: {OUT}")
print(f"  спрайтов: {len(targets) - 1}, блоков: {nb}, ассетов: {len(assets)}, "
      f"размер: {os.path.getsize(OUT) // 1024} КБ")
