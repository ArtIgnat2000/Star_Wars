# -*- coding: utf-8 -*-
"""Корабли, дроиды, лазеры, взрывы, врата — векторные спрайты (SVG)."""
import math
import random
from rig import Svg, f, line, poly, ellipse, circle, path, shade, mix

CHROME = "#c9d3da"
CHROME_D = "#8f9aa3"
CHROME_L = "#eef4f8"
YELLOW = "#e8b73a"
YELLOW_D = "#c08f1c"
DARK = "#2b3138"
OUT = "#1d2126"


# --------------------------------------------------------- истребитель Набу --
def naboo_fighter(flame=1.0):
    """N-1 Starfighter, вид сверху, нос направлен ВВЕРХ. 140x200."""
    s = Svg(140, 200)
    cx = 70
    # пламя двигателей
    s.add(ellipse((cx, 168), 15 * flame, 16 * flame, "#4fc3f7", 0.45))
    for w, h, op in ((24, 34, 0.35), (16, 26, 0.6), (8, 16, 0.95)):
        s.add(ellipse((cx, 158 + h * 0.45), w * flame * 0.5, h * flame * 0.5,
                      "#8fdcff" if op < 0.9 else "#ffffff", op))
    # задние крылья (скошенные назад)
    for sgn in (1, -1):
        d = (f"M {f(cx+12*sgn)} {104} L {f(cx+52*sgn)} {142} L {f(cx+47*sgn)} {154} "
             f"L {f(cx+9*sgn)} {126} Z")
        s.add(path(d, CHROME, 1, OUT, 3.4))
        s.add(path(f"M {f(cx+16*sgn)} {110} L {f(cx+45*sgn)} {140} L {f(cx+42*sgn)} {146} "
                   f"L {f(cx+14*sgn)} {118} Z", YELLOW, 1, YELLOW_D, 1.2))
    # передние «вилки» — визитная карточка N-1
    for sgn in (1, -1):
        d = (f"M {f(cx+11*sgn)} {96} L {f(cx+17*sgn)} {16} L {f(cx+11*sgn)} {10} "
             f"L {f(cx+5*sgn)} {88} Z")
        s.add(path(d, CHROME_L, 1, OUT, 3.2))
        s.add(path(f"M {f(cx+12.5*sgn)} {90} L {f(cx+15*sgn)} {24} L {f(cx+12*sgn)} {20} "
                   f"L {f(cx+8.5*sgn)} {84} Z", YELLOW, 1, None, 0))
    # корпус
    s.add(path(f"M {cx} {34} C {cx+10} {50} {cx+14} {76} {cx+14} {112} "
               f"C {cx+14} {134} {cx+12} {148} {cx+10} {158} "
               f"L {cx-10} {158} C {cx-12} {148} {cx-14} {134} {cx-14} {112} "
               f"C {cx-14} {76} {cx-10} {50} {cx} {34} Z", CHROME, 1, OUT, 3.6))
    s.add(path(f"M {cx} {36} C {cx+7} {56} {cx+9} {82} {cx+9} {112} "
               f"C {cx+9} {132} {cx+7} {146} {cx+5} {156} L {cx-4} {156} "
               f"C {cx-6} {144} {cx-7} {132} {cx-7} {112} C {cx-7} {82} {cx-6} {56} "
               f"{cx} {36} Z", CHROME_L, 0.9))
    # жёлтые полосы
    s.add(path(f"M {cx-13} {104} L {cx-13} {132} L {cx-8} {132} L {cx-8} {104} Z", YELLOW, 0.95))
    s.add(path(f"M {cx+8} {104} L {cx+8} {132} L {cx+13} {132} L {cx+13} {104} Z", YELLOW, 0.95))
    # кабина
    s.add(ellipse((cx, 76), 10, 18, "#20323f", 1, CHROME_D, 3.2))
    s.add(ellipse((cx - 2.5, 72), 4.4, 8.5, "#7fd0ff", 0.55))
    # астромех R2
    s.add(circle((cx, 106), 8.4, "#dfe6ea", 1, OUT, 2.6))
    s.add(path(f"M {cx-8} {105} C {cx-3} {100} {cx+3} {100} {cx+8} {105} L {cx+8} {107} "
               f"L {cx-8} {107} Z", "#3f7fd6", 1))
    s.add(circle((cx, 106), 3.0, "#2b3a45"))
    # киль
    s.add(path(f"M {cx-3} {132} L {cx+3} {132} L {cx+2} {160} L {cx-2} {160} Z",
               CHROME_D, 1, OUT, 2))
    return str(s)


# ------------------------------------------------------- дроид-истребитель --
def droid_fighter(open_wings=True):
    """Vulture droid, вид сверху, нос направлен ВНИЗ. 130x130."""
    s = Svg(130, 130)
    cx, cy = 65, 62
    spread = 1.0 if open_wings else 0.45
    body = "#4a4f57"
    rust = "#b5622a"
    # 4 крыла в форме X
    for dx, dy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        p1 = (cx + 10 * dx, cy + 7 * dy)
        p2 = (cx + 46 * spread * dx, cy + 40 * spread * dy)
        p3 = (cx + 34 * spread * dx, cy + 46 * spread * dy)
        p4 = (cx + 8 * dx, cy + 17 * dy)
        s.add(poly([p1, p2, p3, p4], "#3a3f46", 1, OUT, 3))
        s.add(poly([(cx + 13 * dx, cy + 11 * dy), (cx + 40 * spread * dx, cy + 37 * spread * dy),
                    (cx + 33 * spread * dx, cy + 41 * spread * dy),
                    (cx + 12 * dx, cy + 15 * dy)], rust, 0.85))
    # корпус
    s.add(path(f"M {cx} {cy+42} C {cx+13} {cy+20} {cx+15} {cy-10} {cx+12} {cy-30} "
               f"L {cx-12} {cy-30} C {cx-15} {cy-10} {cx-13} {cy+20} {cx} {cy+42} Z",
               body, 1, OUT, 3.4))
    s.add(path(f"M {cx} {cy+36} C {cx+7} {cy+14} {cx+8} {cy-12} {cx+6} {cy-26} "
               f"L {cx-6} {cy-26} C {cx-8} {cy-12} {cx-7} {cy+14} {cx} {cy+36} Z",
               "#5c626b", 0.9))
    # красный сенсор
    s.add(ellipse((cx, cy + 26), 7, 5.5, "#ff4a3d", 1, "#2a1010", 2))
    s.add(ellipse((cx, cy + 26), 4.2, 3.2, "#ffd0c0", 0.9))
    # «глаз» сверху
    s.add(circle((cx, cy - 12), 4.6, "#ff6a4a", 1, "#2a1010", 2))
    return str(s)


# ------------------------------------------------------------------ лазеры --
def laser(color="#66d9ff", core="#ffffff", length=46, w=9):
    s = Svg(26, length + 10)
    cx = 13
    s.add(ellipse((cx, 5 + length / 2), w * 1.9, length * 0.58, color, 0.25))
    s.add(ellipse((cx, 5 + length / 2), w * 1.1, length * 0.5, color, 0.6))
    s.add(f'<rect x="{f(cx-w/2)}" y="5" width="{f(w)}" height="{f(length)}" rx="{f(w/2)}" '
          f'fill="{core}"/>')
    s.add(f'<rect x="{f(cx-w/2+1.6)}" y="8" width="{f(w*0.42)}" height="{f(length-6)}" '
          f'rx="{f(w*0.2)}" fill="{color}"/>')
    return str(s)


# ------------------------------------------------------------------ взрыв ---
def explosion(phase=0):
    """phase 0..3 — кадры взрыва. 110x110."""
    rnd = random.Random(1234)
    s = Svg(110, 110)
    c = (55, 55)
    if phase >= 3:
        r = 48
        s.add(circle(c, r, "#5a5a5a", 0.18))
        s.add(circle(c, r * 0.8, "#8a8a8a", 0.12))
        s.add(ellipse(c, 6, 6, "#6b6b6b", 0.35))
        return str(s)
    scale = (0.55, 0.85, 1.0)[phase]
    colors = [("#ffd54a", 0.9), ("#ff8a26", 0.9), ("#e6402a", 0.8)]
    for i, (col, op) in enumerate(colors):
        pts = []
        n = 14
        for k in range(n * 2):
            ang = math.pi * k / n
            rad = (26 + 18 * ((k % 2) == 0)) * scale * (1 - 0.16 * i)
            rad *= 1 + rnd.uniform(-0.12, 0.12)
            pts.append((c[0] + rad * math.cos(ang), c[1] + rad * math.sin(ang)))
        s.add(poly(pts, col, op * (0.6 + 0.15 * (2 - i))))
    s.add(circle(c, 16 * scale, "#fff3c4", 0.95))
    return str(s)


# ------------------------------------------------------------ искры удара ---
def clash_sparks(phase=0):
    s = Svg(90, 90)
    c = (45, 45)
    rnd = random.Random(77 + phase)
    for i in range(9):
        ang = rnd.uniform(0, math.tau)
        ln = rnd.uniform(16, 34) * (1.0 if phase == 0 else 1.25)
        p1 = (c[0] + 6 * math.cos(ang), c[1] + 6 * math.sin(ang))
        p2 = (c[0] + ln * math.cos(ang), c[1] + ln * math.sin(ang))
        s.add(line(p1, p2, 3.4, "#fff6c0", 0.9))
        s.add(circle(p2, 3.0, "#ffd75e", 0.85))
    s.add(circle(c, 12, "#ffffff", 0.7))
    s.add(circle(c, 20, "#ffd75e", 0.28))
    return str(s)


# ------------------------------------------------------------ плазма-врата --
def plasma_gate(open_=False):
    """Вертикальное силовое поле в генераторной. 200x360."""
    s = Svg(200, 360)
    if not open_:
        s.add(f'<rect x="24" y="0" width="152" height="360" fill="#ff4a2a" opacity="0.16"/>')
        s.add(f'<rect x="44" y="0" width="112" height="360" fill="#ff6a35" opacity="0.22"/>')
        s.add(f'<rect x="84" y="0" width="32" height="360" fill="#ffd0a0" opacity="0.35"/>')
        for y in range(4, 360, 12):
            s.add(f'<rect x="26" y="{y}" width="148" height="4" fill="#ffb27a" opacity="0.30"/>')
        s.add(line((30, 0), (30, 360), 3, "#ff8a5a", 0.8, cap="butt"))
        s.add(line((170, 0), (170, 360), 3, "#ff8a5a", 0.8, cap="butt"))
    else:
        s.add(f'<rect x="76" y="0" width="10" height="360" fill="#ff6a35" opacity="0.25"/>')
        s.add(f'<rect x="96" y="0" width="10" height="360" fill="#ff6a35" opacity="0.25"/>')
        s.add(line((30, 0), (30, 360), 3, "#8a4a3a", 0.6, cap="butt"))
        s.add(line((170, 0), (170, 360), 3, "#8a4a3a", 0.6, cap="butt"))
    return str(s)


# --------------------------------------------------------- пустой костюм  ---
def dot():
    s = Svg(10, 10)
    s.add(circle((5, 5), 4.4, "#ffffff", 0.02))
    return str(s)
