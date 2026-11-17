# -*- coding: utf-8 -*-
"""Проверка структуры собранного .sb3 (без запуска Scratch)."""
import json, sys, zipfile

MENUS = {
    "sensing_keyoptions": ("KEY_OPTION",),
    "sensing_touchingobjectmenu": ("TOUCHINGOBJECTMENU",),
    "sensing_distancetomenu": ("DISTANCETO",),
    "looks_costume": ("COSTUME",),
    "looks_backdrops": ("BACKDROP",),
    "control_create_clone_of_menu": ("CLONE_OPTION",),
    "sound_sounds_menu": ("SOUND_MENU",),
    "sensing_of_object_menu": ("OBJECT",),
}

def main(path):
    z = zipfile.ZipFile(path)
    names = set(z.namelist())
    proj = json.loads(z.read("project.json"))
    errs, warns = [], []
    targets = proj["targets"]
    sprite_names = {t["name"] for t in targets}
    stage = [t for t in targets if t["isStage"]][0]
    backdrops = {c["name"] for c in stage["costumes"]}
    variables = {v[0] for t in targets for v in t["variables"].values()}
    broadcasts = set(stage["broadcasts"].values())
    vars_by_name = {v[0] for t in targets for v in t["variables"].values()}

    for t in targets:
        tn = t["name"]
        costumes = {c["name"] for c in t["costumes"]}
        sounds = {s["name"] for s in t["sounds"]}
        for a in t["costumes"] + t["sounds"]:
            if a["md5ext"] not in names:
                errs.append(f"{tn}: нет файла {a['md5ext']}")
        blocks = t["blocks"]
        for bid, b in blocks.items():
            if not isinstance(b, dict):
                errs.append(f"{tn}/{bid}: блок-массив вместо объекта")
                continue
            if b.get("topLevel") and ("x" not in b or "y" not in b):
                warns.append(f"{tn}/{bid}: topLevel без x/y")
            nxt = b.get("next")
            if nxt and nxt not in blocks:
                errs.append(f"{tn}/{bid}: next -> {nxt} не существует")
            if nxt and blocks[nxt].get("parent") != bid:
                errs.append(f"{tn}/{bid}: broken next parent")
            par = b.get("parent")
            if par and par not in blocks:
                errs.append(f"{tn}/{bid}: parent -> {par} не существует")
            for iname, inp in b.get("inputs", {}).items():
                if not isinstance(inp, list) or len(inp) < 2:
                    errs.append(f"{tn}/{bid}: плохой вход {iname}")
                    continue
                for x in inp[1:]:
                    if isinstance(x, str) and x not in blocks:
                        errs.append(f"{tn}/{bid}: вход {iname} -> {x} не существует")
                    if isinstance(x, list) and x and x[0] in (11,):
                        if x[1] not in broadcasts:
                            errs.append(f"{tn}/{bid}: трансляция '{x[1]}' не объявлена")
            op = b["opcode"]
            f = b.get("fields", {})
            if op == "event_whenbroadcastreceived":
                if f["BROADCAST_OPTION"][0] not in broadcasts:
                    errs.append(f"{tn}: when I receive несуществующая трансляция {f['BROADCAST_OPTION']}")
            if op in ("data_setvariableto", "data_changevariableby", "data_variable",
                      "data_showvariable", "data_hidevariable"):
                if f["VARIABLE"][0] not in vars_by_name:
                    errs.append(f"{tn}: переменная {f['VARIABLE']} не объявлена")
            if op == "looks_switchcostumeto":
                pass
            if op == "looks_switchbackdropto":
                pass
            if op == "sensing_touchingobject":
                m = blocks.get(b["inputs"]["TOUCHINGOBJECTMENU"][1])
                v = m["fields"]["TOUCHINGOBJECTMENU"][0]
                if v not in sprite_names and v not in ("_edge_", "_mouse_"):
                    errs.append(f"{tn}: touching '{v}' — нет такого спрайта")
            if op == "control_create_clone_of":
                m = blocks.get(b["inputs"]["CLONE_OPTION"][1])
                v = m["fields"]["CLONE_OPTION"][0]
                if v not in sprite_names and v != "_myself_":
                    errs.append(f"{tn}: clone '{v}' — нет такого спрайта")
            if op == "sensing_distanceto":
                m = blocks.get(b["inputs"]["DISTANCETO"][1])
                v = m["fields"]["DISTANCETO"][0]
                if v not in sprite_names and v != "_mouse_":
                    errs.append(f"{tn}: distance to '{v}' — нет такого спрайта")
            if op == "sensing_of":
                m = blocks.get(b["inputs"]["OBJECT"][1])
                v = m["fields"]["OBJECT"][0]
                if v not in sprite_names and v != "Stage":
                    errs.append(f"{tn}: of '{v}' — нет такого спрайта")
            if op == "sound_play":
                m = blocks.get(b["inputs"]["SOUND_MENU"][1])
                v = m["fields"]["SOUND_MENU"][0]
                if v not in sounds:
                    errs.append(f"{tn}: звук '{v}' не найден в спрайте")
    # costume names used
    for t in targets:
        costumes = {c["name"] for c in t["costumes"]}
        for bid, b in t["blocks"].items():
            if not isinstance(b, dict):
                continue
            if b["opcode"] == "looks_switchcostumeto":
                m = t["blocks"].get(b["inputs"]["COSTUME"][1])
                v = m["fields"]["COSTUME"][0]
                if v not in costumes:
                    errs.append(f"{t['name']}: костюм '{v}' не найден")
            if b["opcode"] == "looks_switchbackdropto":
                m = t["blocks"].get(b["inputs"]["BACKDROP"][1])
                v = m["fields"]["BACKDROP"][0]
                if v not in backdrops:
                    errs.append(f"{t['name']}: фон '{v}' не найден")
    print(f"блоков: {sum(len(t['blocks']) for t in targets)}, ассетов: {len(names)-1}")
    print(f"ошибок: {len(errs)}, предупреждений: {len(warns)}")
    for e in errs[:40]:
        print("  ОШИБКА:", e)
    for w in warns[:10]:
        print("  предупр.:", w)
    return 1 if errs else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "star_wars_duel.sb3"))
