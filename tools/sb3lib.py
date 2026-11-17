# -*- coding: utf-8 -*-
"""
Сборка готового проекта Scratch 3.0 (финальная версия для 2 уровней).
Запуск: python3 tools/build_sb3.py
Результат: star_wars_duel.sb3 (можно сразу открыть в Scratch 3 онлайн/офлайн).
"""
import hashlib
import json
import os
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
OUT_SB3 = os.path.join(ROOT, "star_wars_duel.sb3")

# --------------------------------------------------------------- глобальные --
VARS = {
    "очки": "v-score", "жизни": "v-lives", "этап": "v-stage", "ход": "v-run",
    "хп_мол": "v-maulhp", "спавн_x": "v-sx", "спавн_y": "v-sy",
    "блок_игрок": "v-pblock", "блок_мол": "v-mblock", "атака": "v-atk",
    "прыжок": "v-jump", "движется": "v-move",
}
ALL_VARS = {vid: [name, 0] for name, vid in VARS.items()}
ALL_VARS[VARS["жизни"]][1] = 3
ALL_VARS[VARS["ход"]][1] = 0
ALL_VARS[VARS["хп_мол"]][1] = 3

BC = {
    "меню": "b-menu", "старт": "b-start", "полетели": "b-fly",
    "уровень 2": "b-lvl2", "бой": "b-fight", "урон": "b-hurt",
    "победа": "b-win", "поражение": "b-lose",
}
ALL_BC = {bid: name for name, bid in BC.items()}


# ------------------------------------------------------------------- блоки ---
def n(op, inputs=None, fields=None):
    return {"op": op, "inputs": inputs or {}, "fields": fields or {}}


def num(v):
    return ("lit", 4, str(v))


def txt(v):
    return ("lit", 10, str(v))


def rep(node):
    return ("rep", node)


def sub(*nodes):
    flat = []
    for nd in nodes:
        flat.extend(nd if isinstance(nd, list) else [nd])
    return ("sub", flat)


def menu(op, **fields):
    return ("menu", op, fields)


def V(name):
    return rep(n("data_variable", fields={"VARIABLE": [name, VARS[name]]}))


def setvar(name, val):
    return n("data_setvariableto", {"VALUE": val}, {"VARIABLE": [name, VARS[name]]})


def changevar(name, val):
    return n("data_changevariableby", {"VALUE": val}, {"VARIABLE": [name, VARS[name]]})


def eq(a, b):
    return rep(n("operator_equals", {"OPERAND1": a, "OPERAND2": b}))


def gt(a, b):
    return rep(n("operator_gt", {"OPERAND1": a, "OPERAND2": b}))


def lt(a, b):
    return rep(n("operator_lt", {"OPERAND1": a, "OPERAND2": b}))


def add(a, b):
    return rep(n("operator_add", {"NUM1": a, "NUM2": b}))


def subn(a, b):
    return rep(n("operator_subtract", {"NUM1": a, "NUM2": b}))


def rnd(a, b):
    return rep(n("operator_random", {"FROM": a, "TO": b}))


def AND(a, b):
    return rep(n("operator_and", {"OPERAND1": a, "OPERAND2": b}))


def OR(a, b):
    return rep(n("operator_or", {"OPERAND1": a, "OPERAND2": b}))


def NOT(a):
    return rep(n("operator_not", {"OPERAND": a}))


def keyp(k):
    return rep(n("sensing_keypressed", {"KEY_OPTION": menu("sensing_keyoptions", KEY_OPTION=[k, None])}))


def touching(name):
    return rep(n("sensing_touchingobject",
                 {"TOUCHINGOBJECTMENU": menu("sensing_touchingobjectmenu", TOUCHINGOBJECTMENU=[name, None])}))


def dist(name):
    return rep(n("sensing_distanceto",
                 {"DISTANCETO": menu("sensing_distancetomenu", DISTANCETO=[name, None])}))


def prop_of(prop, obj):
    return rep(n("sensing_of", {"OBJECT": menu("sensing_of_object_menu", OBJECT=[obj, None])},
                 {"PROPERTY": [prop, None]}))


def xpos():
    return rep(n("motion_xposition"))


def ypos():
    return rep(n("motion_yposition"))


def gotoxy(x, y):
    return n("motion_gotoxy", {"X": x, "Y": y})


def setx(x):
    return n("motion_setx", {"X": x})


def sety(y):
    return n("motion_sety", {"Y": y})


def chx(v):
    return n("motion_changexby", {"DX": v})


def chy(v):
    return n("motion_changeyby", {"DY": v})


def point(d):
    return n("motion_pointindirection", {"DIRECTION": num(d)})


def rotstyle(style):
    return n("motion_setrotationstyle", fields={"STYLE": [style, None]})


def switch_costume(name):
    return n("looks_switchcostumeto",
             {"COSTUME": menu("looks_costume", COSTUME=[name, None])})


def next_costume():
    return n("looks_nextcostume")


def costume_number():
    return rep(n("looks_costumenumbername", fields={"NUMBER_NAME": ["number", None]}))


def say(msg, secs):
    return n("looks_sayforsecs", {"MESSAGE": txt(msg), "SECS": num(secs)})


def say_(msg):
    return n("looks_say", {"MESSAGE": txt(msg)})


def ghost(v):
    return n("looks_seteffectto", {"VALUE": num(v)}, {"EFFECT": ["GHOST", None]})


def setsize(v):
    return n("looks_setsizeto", {"SIZE": num(v)})


def show():
    return n("looks_show")


def hide():
    return n("looks_hide")


def goto_front():
    return n("looks_gotofrontback", fields={"FRONT_BACK": ["front", None]})


def backdrop(name):
    return n("looks_switchbackdropto",
             {"BACKDROP": menu("looks_backdrops", BACKDROP=[name, None])})


def play(snd):
    return n("sound_play", {"SOUND_MENU": menu("sound_sounds_menu", SOUND_MENU=[snd, None])})


def wait(t):
    return n("control_wait", {"DURATION": num(t)})


def forever(*body):
    return n("control_forever", {"SUBSTACK": sub(*body)})


def repeat(times, *body):
    if isinstance(times, (int, float)):
        times = num(times)
    flat = []
    for b in body:
        flat.extend(b if isinstance(b, list) else [b])
    return n("control_repeat", {"TIMES": times, "SUBSTACK": sub(*flat)})


def repeat_until(cond, *body):
    return n("control_repeat_until", {"CONDITION": cond, "SUBSTACK": sub(*body)})


def if_(cond, *body):
    return n("control_if", {"CONDITION": cond, "SUBSTACK": sub(*body)})


def if_else(cond, body1, body2):
    return n("control_if_else", {"CONDITION": cond, "SUBSTACK": sub(*body1),
                                 "SUBSTACK2": sub(*body2)})


def wait_until(cond):
    return n("control_wait_until", {"CONDITION": cond})


def clone(sprite):
    return n("control_create_clone_of",
             {"CLONE_OPTION": menu("control_create_clone_of_menu", CLONE_OPTION=[sprite, None])})


def bcast(name):
    return n("event_broadcast", {"BROADCAST_INPUT": ("bc", name)})


def when_flag():
    return n("event_whenflagclicked")


def when_recv(name):
    return n("event_whenbroadcastreceived", fields={"BROADCAST_OPTION": [name, BC[name]]})


def when_clone():
    return n("control_start_as_clone")


def del_clone():
    return n("control_delete_this_clone")


# --------------------------------------------------------------- target ------
class Target:
    def __init__(self, name, is_stage=False, prefix="t"):
        self.name = name
        self.is_stage = is_stage
        self.prefix = prefix
        self.blocks = {}
        self._n = 0
        self.costumes = []
        self.sounds = []
        self.variables = {} if not is_stage else dict(ALL_VARS)
        self.x = 0
        self.y = 0
        self.size = 100
        self.direction = 90
        self.visible = True
        self.rotation_style = "all around"
        self.current_costume = 0
        self.layer = 1

    # --- эмиссия ---
    def _new(self):
        self._n += 1
        return f"{self.prefix}-{self._n}"

    def _emit_input(self, spec, parent):
        if not isinstance(spec, tuple):
            raise TypeError(f"плохой вход блока: {spec!r}")
        kind = spec[0]
        if kind == "lit":
            return [1, [spec[1], spec[2]]]
        if kind == "bc":
            return [1, [11, spec[1], BC[spec[1]]]]
        if kind == "menu":
            bid = self._new()
            fields = {k: list(v) for k, v in spec[2].items()}
            self.blocks[bid] = {"opcode": spec[1], "next": None, "parent": parent,
                                "inputs": {}, "fields": fields, "shadow": True,
                                "topLevel": False}
            return [1, bid]
        if kind == "rep":
            bid = self._emit_node(spec[1], parent)
            return [2, bid]
        if kind == "sub":
            first = self._emit_stack(spec[1], parent)
            return [2, first] if first else [2, None]
        raise ValueError(kind)

    def _emit_node(self, node, parent):
        bid = self._new()
        blk = {"opcode": node["op"], "next": None, "parent": parent, "inputs": {},
               "fields": {k: list(v) for k, v in node["fields"].items()},
               "shadow": False, "topLevel": False}
        self.blocks[bid] = blk
        for iname, spec in node["inputs"].items():
            blk["inputs"][iname] = self._emit_input(spec, bid)
        # чистим пустые подстеки
        for k in list(blk["inputs"]):
            if blk["inputs"][k] == [2, None]:
                del blk["inputs"][k]
        return bid

    def _emit_stack(self, nodes, parent, x=0, y=0, top=False):
        prev = None
        first = None
        for node in nodes:
            bid = self._emit_node(node, prev if prev is not None else parent)
            if first is None:
                first = bid
                if top:
                    self.blocks[bid]["topLevel"] = True
                    self.blocks[bid]["x"] = x
                    self.blocks[bid]["y"] = y
                    self.blocks[bid]["parent"] = None
            else:
                self.blocks[prev]["next"] = bid
            prev = bid
        return first

    def script(self, x, y, *nodes):
        self._emit_stack(list(nodes), None, x=x, y=y, top=True)

    def add_costume(self, name, path, w, h):
        data = open(os.path.join(ASSETS, path), "rb").read()
        md5 = hashlib.md5(data).hexdigest()
        self.costumes.append({"assetId": md5, "name": name, "bitmapResolution": 1,
                              "md5ext": md5 + ".svg", "dataFormat": "svg",
                              "rotationCenterX": w / 2, "rotationCenterY": h / 2,
                              "_data": data})

    def add_sound(self, name, filename):
        path = os.path.join(ASSETS, "sounds", filename)
        data = open(path, "rb").read()
        md5 = hashlib.md5(data).hexdigest()
        import wave
        with wave.open(path, "rb") as w:
            count = w.getnframes()
        self.sounds.append({"assetId": md5, "name": name, "dataFormat": "wav",
                            "rate": 44100, "sampleCount": count,
                            "md5ext": md5 + ".wav", "_data": data})

    def to_json(self):
        def base(ctype):
            out = []
            for c in ctype:
                c = dict(c)
                c.pop("_data", None)
                out.append(c)
            return out
        d = {
            "isStage": self.is_stage, "name": self.name,
            "variables": self.variables, "lists": {},
            "broadcasts": dict(ALL_BC) if self.is_stage else {},
            "blocks": self.blocks, "comments": {},
            "currentCostume": self.current_costume,
            "costumes": base(self.costumes), "sounds": base(self.sounds),
            "volume": 100, "layerOrder": 0 if self.is_stage else self.layer,
        }
        if self.is_stage:
            d.update({"tempo": 60, "videoTransparency": 50, "videoState": "off",
                      "textToSpeechLanguage": None})
        else:
            d.update({"visible": self.visible, "x": self.x, "y": self.y,
                      "size": self.size, "direction": self.direction,
                      "draggable": False, "rotationStyle": self.rotation_style})
        return d


def sprite_by_slug(manifest, slug):
    for s in manifest["sprites"]:
        if s["slug"] == slug:
            return s
    raise KeyError(slug)
