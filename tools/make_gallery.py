# -*- coding: utf-8 -*-
"""Генерирует preview/index.html — галерею всех ассетов."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAN = json.load(open(os.path.join(ROOT, "assets", "manifest.json"), encoding="utf-8"))

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
 padding:8px;text-align:center;width:130px}
.row img{height:150px;width:100%;object-fit:contain;display:block;
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
"""


def esc(t):
    return (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def main():
    parts = [f"<!doctype html><html lang='ru'><head><meta charset='utf-8'>",
             "<meta name='viewport' content='width=device-width, initial-scale=1'>",
             "<title>Star Wars: Дуэль на Набу — ассеты для Scratch 3.0</title>",
             f"<style>{CSS}</style></head><body><div class='wrap'>",
             "<h1>STAR <span>WARS</span>: Дуэль на Набу</h1>",
             "<p class='sub'>Полный набор векторов для Scratch 3.0: 5 фонов, 11 спрайтов, "
             f"{sum(len(s['costumes']) for s in MAN['sprites'])} костюмов, 9 звуков "
             "и готовый проект <code>star_wars_duel.sb3</code>.</p>",
             "<img class='poster' src='poster.png' alt='Постер набора'>",
             "<h2>Как это выглядит в игре</h2><div class='grid'>",
             "<div class='card'><img src='gameplay-1.png' alt='Уровень 1'>"
             "<h3 style='margin-top:10px'>Уровень 1 — погоня</h3></div>",
             "<div class='card'><img src='gameplay-2.png' alt='Уровень 2'>"
             "<h3 style='margin-top:10px'>Уровень 2 — дуэль</h3></div>",
             "</div>"]

    # фоны
    parts.append("<h2>Фоны — 480×360</h2><div class='grid'>")
    for b in MAN["backdrops"]:
        parts.append(f"<div class='card'><img src='png/backdrop-{b['slug']}.png' "
                     f"alt='{esc(b['name'])}'><h3 style='margin-top:10px'>{esc(b['name'])}"
                     f"<span class='tag'>{b['w']}×{b['h']}</span></h3>"
                     f"<div class='sub' style='margin:0;font-size:13px'>"
                     f"assets/{b['file']}</div></div>")
    parts.append("</div>")

    # спрайты
    heroes = {"quigon", "obiwan", "maul"}
    for title, group in (("Персонажи", heroes),
                         ("Техника и эффекты", None)):
        parts.append(f"<h2>{title}</h2>")
        for s in MAN["sprites"]:
            if group is not None and s["slug"] not in group:
                continue
            if group is None and s["slug"] in heroes:
                continue
            if s["slug"] == "dot":
                continue
            parts.append(f"<h3>{esc(s['name'])}<span class='tag'>{s['size'][0]}×{s['size'][1]}"
                         f" · {len(s['costumes'])} костюм(ов)</span></h3>")
            parts.append("<div class='row'>")
            for i, c in enumerate(s["costumes"]):
                parts.append(f"<figure><img src='png/sprite-{s['slug']}-{i+1:02d}.png' "
                             f"alt='{esc(c['name'])}'><figcaption>{esc(c['name'])}</figcaption></figure>")
            parts.append("</div><div style='height:10px'></div>")

    parts.append("""
<h2>Как использовать</h2>
<div class='note'>
<b>Быстрый путь:</b> откройте <code>star_wars_duel.sb3</code> на
<a href='https://scratch.mit.edu/projects/editor/'>scratch.mit.edu</a> (Файл → Загрузить с компьютера)
или в офлайн-редакторе Scratch Desktop. Игра сразу играбельна: уровень 1 — погоня на истребителях,
уровень 2 — дуэль с Дартом Молом.
</div>
<div class='note'>
<b>Своими руками:</b> фоны и костюмы лежат в <code>assets/backdrops</code> и
<code>assets/sprites</code> в формате SVG (родной векторный формат Scratch 3).
В редакторе: «Выбрать фон» → «Загрузить» или перетащить файл в список костюмов спрайта.
Растровые копии — в <code>preview/png</code>. Пошаговая сборка скриптов — в
<code>docs/СБОРКА_В_SCRATCH.md</code>, сюжет и правила — в <code>docs/СЮЖЕТ.md</code>.
</div>

<h2>Управление в готовом проекте</h2>
<table>
<tr><th>Уровень</th><th>Клавиши</th><th>Действие</th></tr>
<tr><td>Титульный экран</td><td>ПРОБЕЛ</td><td>начать игру / начать заново</td></tr>
<tr><td>1 — космос</td><td>← →</td><td>маневрировать истребителем</td></tr>
<tr><td>1 — космос</td><td>ПРОБЕЛ</td><td>огонь по дроидам (+10 очков за дроид)</td></tr>
<tr><td>2 — генераторная</td><td>← → / A D</td><td>бежать</td></tr>
<tr><td>2 — генераторная</td><td>↑ / W</td><td>прыжок</td></tr>
<tr><td>2 — генераторная</td><td>ПРОБЕЛ</td><td>удар световым мечом</td></tr>
<tr><td>2 — генераторная</td><td>↓ / S</td><td>блок (Дарт Мол не наносит урон)</td></tr>
</table>
""")
    parts.append("</div></body></html>")
    out = os.path.join(ROOT, "preview", "index.html")
    open(out, "w", encoding="utf-8").write("".join(parts))
    print("готово:", out)


if __name__ == "__main__":
    main()
