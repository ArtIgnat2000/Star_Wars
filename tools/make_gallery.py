# -*- coding: utf-8 -*-
"""Генерирует preview/index.html — галерею ассетов (кинематографичная версия)."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILM = os.path.join(ROOT, "assets", "film")
FM = json.load(open(os.path.join(FILM, "manifest.json"), encoding="utf-8"))
VM = json.load(open(os.path.join(ROOT, "assets", "manifest.json"), encoding="utf-8"))
FS = {s["slug"]: s for s in FM["sprites"]}
VB = {b["slug"]: b for b in VM["backdrops"]}

CSS = """
:root{--bg:#0b0e17;--card:#141a26;--line:#232c3d;--txt:#e7edf7;--dim:#93a3bd;--gold:#ffd75e}
*{box-sizing:border-box}
body{margin:0;background:radial-gradient(1200px 600px at 50% -10%,#1a2440,#0b0e17 70%);
 color:var(--txt);font:16px/1.55 "Segoe UI",Roboto,Helvetica,Arial,sans-serif}
.wrap{max-width:1180px;margin:0 auto;padding:32px 20px 80px}
h1{font-size:34px;margin:0 0 6px;letter-spacing:.5px}
h1 span{color:var(--gold)}
h2{margin:44px 0 14px;font-size:23px;border-bottom:1px solid var(--line);padding-bottom:8px}
h3{margin:0 0 4px;font-size:17px}
.sub{color:var(--dim);margin:0 0 18px}
.poster{width:100%;border-radius:14px;border:1px solid var(--line);display:block}
.grid{display:grid;gap:18px;grid-template-columns:repeat(auto-fill,minmax(300px,1fr))}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px}
.card img{width:100%;display:block;border-radius:8px;background:
 repeating-conic-gradient(#1b2231 0% 25%,#222b3c 0% 50%) 50%/18px 18px}
.row{display:flex;flex-wrap:wrap;gap:10px}
.row figure{margin:0;background:var(--card);border:1px solid var(--line);border-radius:10px;
 padding:8px;text-align:center;width:150px}
.row img{height:210px;width:100%;object-fit:contain;display:block;
 background:repeating-conic-gradient(#1b2231 0% 25%,#222b3c 0% 50%) 50%/14px 14px;border-radius:6px}
.row figcaption{font-size:12px;color:var(--dim);margin-top:6px}
.tag{display:inline-block;font-size:12px;color:var(--dim);border:1px solid var(--line);
 border-radius:999px;padding:2px 9px;margin-left:8px;vertical-align:middle}
.note{background:#101725;border-left:3px solid var(--gold);padding:14px 16px;border-radius:8px;
 color:#cfd9ea;margin:18px 0}
code{background:#0d1420;border:1px solid var(--line);border-radius:5px;padding:1px 6px;font-size:13px}
a{color:#8fc4ff}
table{border-collapse:collapse;width:100%;font-size:15px}
td,th{border-bottom:1px solid var(--line);padding:7px 8px;text-align:left}
th{color:var(--dim);font-weight:600}
.pending{opacity:.62}
.dl{display:flex;flex-wrap:wrap;align-items:center;gap:12px;margin:16px 0 4px}
.btn{display:inline-block;background:var(--gold);color:#1a1405;text-decoration:none;
 font-weight:700;padding:12px 20px;border-radius:10px;border:1px solid #b8933180}
.btn.ghost{background:transparent;color:var(--txt);border:1px solid var(--line);font-weight:600}
.btn:hover{filter:brightness(1.08)}
.hint{color:var(--dim);font-size:14px}
"""


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    p = ["<!doctype html><html lang='ru'><head><meta charset='utf-8'>",
         "<meta name='viewport' content='width=device-width, initial-scale=1'>",
         "<title>Star Wars: Дуэль на Набу — ассеты для Scratch 3.0</title>",
         f"<style>{CSS}</style></head><body><div class='wrap'>",
         "<h1>STAR <span>WARS</span>: Дуэль на Набу</h1>",
         "<p class='sub'>Кинематографичный набор для Scratch 3.0: фотореалистичные персонажи "
         "и корабли, фоны Набу, эффекты и готовый проект <code>star_wars_duel.sb3</code>. "
         "Есть и полностью векторная версия — <code>star_wars_duel_vector.sb3</code>.</p>",
         "<img class='poster' src='poster.png' alt='Постер набора'>",
         "<div class='dl'><a class='btn' href='/star_wars_duel.sb3' download>",
         "Скачать star_wars_duel.sb3 · 3,0 МБ</a>",
         "<a class='btn ghost' href='/star_wars_duel_vector.sb3' download>",
         "Векторная версия · 0,5 МБ</a>",
         "<span class='hint'>Открывается в Scratch 3: Файл → Загрузить с компьютера</span></div>",
         "<h2>Как это выглядит в игре</h2><div class='grid'>",
         "<div class='card'><img src='gameplay-1.png' alt='Уровень 1'>"
         "<h3 style='margin-top:10px'>Уровень 1 — погоня</h3></div>",
         "<div class='card'><img src='gameplay-2.png' alt='Уровень 2'>"
         "<h3 style='margin-top:10px'>Уровень 2 — дуэль</h3></div>",
         "<div class='card'><img src='gameplay-3.png' alt='Посадка на Набу'>"
         "<h3 style='margin-top:10px'>Интерлюдия — посадка на Набу</h3></div>",
         "</div>"]

    # персонажи
    p.append("<h2>Персонажи</h2>")
    for slug in ("quigon", "obiwan", "maul"):
        s = FS[slug]
        p.append(f"<h3>{esc(s['name'])}<span class='tag'>{s['w']}×{s['h']} px · "
                 f"{len(s['costumes'])} костюм(а)</span></h3><div class='row'>")
        for c in s["costumes"]:
            p.append(f"<figure><img src='../assets/film/{c['file']}' alt='{esc(c['name'])}'>"
                     f"<figcaption>{esc(c['name'])}</figcaption></figure>")
        p.append("</div><div style='height:12px'></div>")

    # корабли
    p.append("<h2>Корабли</h2>")
    for slug in ("naboo-fighter", "droid-fighter"):
        s = FS[slug]
        p.append(f"<h3>{esc(s['name'])}<span class='tag'>{s['w']}×{s['h']} px · "
                 f"{len(s['costumes'])} костюм(а)</span></h3><div class='row'>")
        for c in s["costumes"]:
            p.append(f"<figure><img src='../assets/film/{c['file']}' alt='{esc(c['name'])}'>"
                     f"<figcaption>{esc(c['name'])}</figcaption></figure>")
        p.append("</div><div style='height:12px'></div>")

    # фоны
    p.append("<h2>Фоны — 480×360</h2><div class='grid'>")
    for slug, title in (("title", "Титул"), ("space", "Космос"),
                        ("naboo", "Посадка на Набу"), ("generator", "Генераторная"),
                        ("victory", "Победа")):
        b = next(x for x in FM["backdrops"] if x["slug"] == slug)
        p.append(f"<div class='card'><img src='../assets/film/{b['file']}' "
                 f"alt='{esc(title)}'><h3 style='margin-top:10px'>{esc(title)}</h3>"
                 f"<div class='sub' style='margin:0;font-size:13px'>кинематографичный</div></div>")
    p.append("</div>")

    # эффекты
    p.append("<h2>Эффекты</h2><div class='grid'>")
    for slug, title in (("laser", "Лазер"), ("enemy-laser", "Лазер врага"),
                        ("explosion", "Взрыв"), ("sparks", "Искры"),
                        ("plasma-gate", "Плазма-врата")):
        if slug in FS:                      # кинематографичный вариант
            src = [(f"../assets/film/{c['file']}", c["name"]) for c in FS[slug]["costumes"]]
        else:
            vs = next(s for s in VM["sprites"] if s["slug"] == slug)
            src = [(f"png/sprite-{slug}-{i+1:02d}.png", c["name"])
                   for i, c in enumerate(vs["costumes"])]
        imgs = "".join(
            f"<img src='{u}' alt='{esc(n)}' style='height:90px'>" for u, n in src)
        p.append(f"<div class='card'><div style='display:flex;gap:8px;justify-content:center;"
                 f"background:repeating-conic-gradient(#1b2231 0% 25%,#222b3c 0% 50%) 50%/14px 14px;"
                 f"border-radius:8px;padding:8px'>{imgs}</div>"
                 f"<h3 style='margin-top:10px'>{esc(title)}</h3></div>")
    p.append("</div>")

    p.append("""
<h2>Как использовать</h2>
<div class='note'><b>Играть сразу:</b> откройте <code>star_wars_duel.sb3</code> на
<a href='https://scratch.mit.edu/projects/editor/'>scratch.mit.edu</a>
(Файл → Загрузить с компьютера) или в Scratch Desktop. Зелёный флажок, затем ПРОБЕЛ.</div>
<div class='note'><b>Брать картинки:</b> кинематографичные спрайты — в
<code>assets/film/sprites</code> (PNG с прозрачностью), фоны — в
<code>assets/film/backdrops</code>, векторные эффекты — в <code>assets/sprites</code> (SVG).
Старая полностью векторная версия — <code>star_wars_duel_vector.sb3</code> и папка
<code>assets/backdrops</code>.</div>

<h2>Управление</h2>
<table>
<tr><th>Уровень</th><th>Клавиши</th><th>Действие</th></tr>
<tr><td>Титул</td><td>ПРОБЕЛ</td><td>начать игру</td></tr>
<tr><td>1 — космос</td><td>← →</td><td>маневрировать</td></tr>
<tr><td>1 — космос</td><td>ПРОБЕЛ</td><td>огонь (+10 очков за дроида)</td></tr>
<tr><td>2 — генераторная</td><td>← → / A D</td><td>бежать</td></tr>
<tr><td>2 — генераторная</td><td>↑ / W</td><td>прыжок</td></tr>
<tr><td>2 — генераторная</td><td>ПРОБЕЛ</td><td>удар мечом</td></tr>
<tr><td>2 — генераторная</td><td>↓ / S</td><td>блок</td></tr>
</table>
""")
    p.append("</div></body></html>")
    out = os.path.join(ROOT, "preview", "index.html")
    open(out, "w", encoding="utf-8").write("".join(p))
    print("готово:", out)


if __name__ == "__main__":
    main()
