# -*- coding: utf-8 -*-
"""Фоны 480x360 для Scratch 3.0 (вектор)."""
import math
import random
from rig import Svg, f, line, poly, ellipse, circle, path, shade, mix

W, H = 480, 360

# --- мини-шрифт (латиница, «плакатный» стиль) --------------------------------
LETTERS = {
    "S": [[(4, .8), (3, 0), (1, 0), (0, .9), (0, 2.1), (1, 3), (3, 3), (4, 3.9), (4, 5.1),
           (3, 6), (1, 6), (0, 5.2)]],
    "T": [[(0, 0), (4, 0)], [(2, 0), (2, 6)]],
    "A": [[(0, 6), (2, 0), (4, 6)], [(1, 3.7), (3, 3.7)]],
    "R": [[(0, 6), (0, 0), (3, 0), (4, .9), (4, 2.1), (3, 3), (0, 3)], [(2.2, 3), (4, 6)]],
    "W": [[(0, 0), (1, 6), (2, 2), (3, 6), (4, 0)]],
    "N": [[(0, 6), (0, 0), (4, 6), (4, 0)]],
    "B": [[(0, 6), (0, 0), (3, 0), (4, .9), (4, 2.1), (3, 3), (0, 3)],
          [(3, 3), (4, 3.9), (4, 5.1), (3, 6), (0, 6)]],
    "O": [[(1, 0), (3, 0), (4, .9), (4, 5.1), (3, 6), (1, 6), (0, 5.1), (0, .9), (1, 0)]],
    "D": [[(0, 0), (0, 6)], [(0, 0), (2.4, 0), (4, 1.8), (4, 4.2), (2.4, 6), (0, 6)]],
    "U": [[(0, 0), (0, 5.1), (1, 6), (3, 6), (4, 5.1), (4, 0)]],
    "E": [[(4, 0), (0, 0), (0, 6), (4, 6)], [(0, 3), (3, 3)]],
    "H": [[(0, 0), (0, 6)], [(4, 0), (4, 6)], [(0, 3), (4, 3)]],
    "I": [[(2, 0), (2, 6)]],
    "Y": [[(0, 0), (2, 3), (4, 0)], [(2, 3), (2, 6)]],
    "P": [[(0, 6), (0, 0), (3, 0), (4, .9), (4, 2.4), (3, 3.3), (0, 3.3)]],
    "L": [[(0, 0), (0, 6), (4, 6)]],
    "C": [[(4, 1), (3, 0), (1, 0), (0, 1.2), (0, 4.8), (1, 6), (3, 6), (4, 5)]],
    "M": [[(0, 6), (0, 0), (2, 3.4), (4, 0), (4, 6)]],
    "-": [[(0.6, 3), (3.4, 3)]],
    " ": [],
}


def text(txt, x, y, size, color, outline=None, ow=0.55, gap=1.9, sw=1.05):
    """Рисует надпись «плакатными» штрихами. (x,y) — левый верхний угол."""
    unit = size / 6.0
    out = []
    cx = x
    for ch in txt.upper():
        strokes = LETTERS.get(ch, [])
        for st in strokes:
            pts = [(cx + px * unit, y + py * unit) for px, py in st]
            d = " ".join(f"{f(px)},{f(py)}" for px, py in pts)
            if outline:
                out.append(f'<polyline points="{d}" fill="none" stroke="{outline}" '
                           f'stroke-width="{f(sw*unit + ow*unit*2)}" stroke-linecap="round" '
                           f'stroke-linejoin="round"/>')
            out.append(f'<polyline points="{d}" fill="none" stroke="{color}" '
                       f'stroke-width="{f(sw*unit)}" stroke-linecap="round" '
                       f'stroke-linejoin="round"/>')
        cx += (4 + gap) * unit
    return "".join(out)


def text_width(txt, size, gap=1.9):
    return len(txt) * (4 + gap) * size / 6.0


def fit(txt, width, gap=1.9):
    """Подбирает кегль так, чтобы надпись влезла в width."""
    return width * 6.0 / (len(txt) * (4 + gap))


# ------------------------------------------------------------------ звёзды ---
def stars(svg, n, seed, ymax=H, size=(0.6, 2.0), color="#ffffff", op=(0.25, 1.0)):
    rnd = random.Random(seed)
    for _ in range(n):
        x, y = rnd.uniform(0, W), rnd.uniform(0, ymax)
        r = rnd.uniform(*size)
        svg.add(circle((x, y), r, color, rnd.uniform(*op)))


_NEB = [0]


def nebula(svg, cx, cy, rx, ry, color, op=0.20, gid=None):
    """Мягкое облако газа — радиальный градиент (Scratch поддерживает)."""
    _NEB[0] += 1
    gid = gid or f"neb{_NEB[0]}"
    svg.add(f'<defs><radialGradient id="{gid}" cx="0.5" cy="0.5" r="0.5">'
            f'<stop offset="0" stop-color="{color}" stop-opacity="{f(op)}"/>'
            f'<stop offset="0.55" stop-color="{color}" stop-opacity="{f(op*0.45)}"/>'
            f'<stop offset="1" stop-color="{color}" stop-opacity="0"/>'
            f'</radialGradient></defs>')
    svg.add(f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(rx)}" ry="{f(ry)}" fill="url(#{gid})"/>')


# ------------------------------------------------------------------- фоны ----
def title():
    s = Svg(W, H)
    s.add('<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">'
          '<stop offset="0" stop-color="#050a1c"/><stop offset="0.55" stop-color="#0a1430"/>'
          '<stop offset="1" stop-color="#132a4a"/></linearGradient></defs>')
    s.add(f'<rect width="{W}" height="{H}" fill="url(#g)"/>')
    nebula(s, 90, 90, 130, 70, "#3b6fd6", 0.20)
    nebula(s, 400, 60, 150, 80, "#8a3bd6", 0.16)
    stars(s, 150, 3)
    # планета Набу внизу
    s.add(circle((240, 470), 190, "#1e6a8a", 1))
    s.add(circle((240, 470), 178, "#2c8ba8", 0.75))
    s.add(ellipse((190, 400), 70, 26, "#5fc9a0", 0.5))
    s.add(ellipse((300, 420), 60, 22, "#5fc9a0", 0.35))
    s.add(f'<defs><radialGradient id="atm2" cx="0.5" cy="0.55" r="0.5">'
          f'<stop offset="0.7" stop-color="#7fe6ff" stop-opacity="0"/>'
          f'<stop offset="0.88" stop-color="#7fe6ff" stop-opacity="0.28"/>'
          f'<stop offset="1" stop-color="#7fe6ff" stop-opacity="0"/></radialGradient></defs>')
    s.add(f'<circle cx="240" cy="470" r="196" fill="url(#atm2)"/>')
    # скрещённые световые мечи
    s.add(line((150, 300), (330, 60), 26, "#2a8fdd", 0.14))
    s.add(line((150, 300), (330, 60), 9, "#5fb8ff", 0.35))
    s.add(line((330, 300), (150, 60), 26, "#e01812", 0.14))
    s.add(line((330, 300), (150, 60), 9, "#ff3f33", 0.35))
    # заголовок
    t = "STAR WARS"
    size = fit(t, 392)
    s.add(text(t, (W - text_width(t, size)) / 2, 92, size, "#ffe14d", "#2b1a05", ow=0.34,
               gap=1.5))
    t0 = "EPISODE I"
    size0 = 13
    s.add(text(t0, (W - text_width(t0, size0, 2.6)) / 2, 160, size0, "#9fb2d8", "#0b1426",
               ow=0.5, gap=2.6))
    t2 = "NABOO DUEL"
    size2 = fit(t2, 250, 1.6)
    s.add(text(t2, (W - text_width(t2, size2, 1.6)) / 2, 184, size2, "#dfe9ff", "#0b1426",
               ow=0.45, gap=1.6))
    return str(s)


def space():
    s = Svg(W, H)
    s.add('<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">'
          '<stop offset="0" stop-color="#03050f"/><stop offset="0.6" stop-color="#071230"/>'
          '<stop offset="1" stop-color="#0d2246"/></linearGradient></defs>')
    s.add(f'<rect width="{W}" height="{H}" fill="url(#g)"/>')
    nebula(s, 120, 70, 170, 90, "#3a63c8", 0.18)
    nebula(s, 380, 120, 140, 80, "#7a3ec0", 0.14)
    stars(s, 220, 11, ymax=300, size=(0.5, 1.8))
    stars(s, 40, 12, ymax=300, size=(1.6, 2.8), op=(0.5, 1.0))
    # большая планета Набу снизу
    s.add(circle((240, 520), 260, "#1c5f80", 1))
    s.add(circle((240, 520), 250, "#25809e", 0.8))
    s.add(ellipse((150, 400), 90, 24, "#63cba2", 0.55))
    s.add(ellipse((320, 420), 80, 22, "#63cba2", 0.42))
    s.add(f'<defs><radialGradient id="atm" cx="0.5" cy="0.62" r="0.55">'
          f'<stop offset="0.55" stop-color="#67e0ff" stop-opacity="0"/>'
          f'<stop offset="0.78" stop-color="#7fe6ff" stop-opacity="0.30"/>'
          f'<stop offset="1" stop-color="#7fe6ff" stop-opacity="0"/>'
          f'</radialGradient></defs>')
    s.add(f'<ellipse cx="240" cy="520" rx="300" ry="300" fill="url(#atm)"/>')
    s.add(ellipse((200, 336), 150, 18, "#bff0ff", 0.18))
    s.add(ellipse((330, 350), 110, 13, "#bff0ff", 0.14))
    # далёкие корабли-силуэты
    s.add(ellipse((70, 300), 26, 5, "#0a1526", 0.7))
    s.add(ellipse((420, 330), 18, 4, "#0a1526", 0.6))
    return str(s)


def naboo():
    s = Svg(W, H)
    s.add('<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
          '<stop offset="0" stop-color="#7fc4f2"/><stop offset="0.6" stop-color="#c8e6f7"/>'
          '<stop offset="1" stop-color="#f2e6c8"/></linearGradient>'
          '<linearGradient id="hill" x1="0" y1="0" x2="0" y2="1">'
          '<stop offset="0" stop-color="#5fae72"/><stop offset="1" stop-color="#2f7a4d"/>'
          '</linearGradient></defs>')
    s.add(f'<rect width="{W}" height="{H}" fill="url(#sky)"/>')
    # облака
    for (cx, cy, r) in ((80, 70, 34), (120, 60, 24), (380, 96, 30), (420, 86, 22)):
        s.add(ellipse((cx, cy), r * 1.4, r * 0.6, "#ffffff", 0.75))
    # дальние холмы
    s.add(path(f"M 0 {250} C 90 {200} 170 {230} 260 {212} C 350 {194} 420 {224} 480 {206} "
               f"L 480 {360} L 0 {360} Z", "#8fcfa0", 0.9))
    # дворец Тид: башни-цилиндры с куполами
    def tower(cx, top, w, r, shade_col):
        s.add(f'<rect x="{f(cx-w/2)}" y="{f(top)}" width="{f(w)}" height="{f(258-top)}" '
              f'fill="#efe8d6"/>')
        s.add(f'<rect x="{f(cx+w/2-w*0.36)}" y="{f(top)}" width="{f(w*0.36)}" '
              f'height="{f(258-top)}" fill="{shade_col}" opacity="0.9"/>')
        s.add(path(f"M {f(cx-r-2)} {f(top)} A {f(r+2)} {f(r+2)} 0 0 1 {f(cx+r+2)} {f(top)} Z",
                   "#faf5e8", 1, "#d9d0b8", 1.4))
        s.add(path(f"M {f(cx+r*0.2)} {f(top-r*0.92)} A {f(r)} {f(r)} 0 0 1 {f(cx+r+1)} {f(top)} "
                   f"L {f(cx+r*0.2)} {f(top)} Z", shade_col, 0.55))
        s.add(line((cx, top - r - 2), (cx, top - r - 16), 2.2, "#d8d2bd"))
        for wy in range(int(top + 12), 250, 26):
            s.add(f'<rect x="{f(cx-4)}" y="{wy}" width="8" height="11" rx="3" '
                  f'fill="#8d9bb0" opacity="0.65"/>')

    s.add(f'<rect x="196" y="240" width="150" height="24" fill="#e6ddc8"/>')
    tower(238, 214, 28, 13, "#cfc6b1")
    tower(272, 200, 38, 20, "#cfc6b1")
    tower(310, 216, 26, 12, "#cfc6b1")
    tower(200, 232, 18, 8, "#d7cebb")
    tower(340, 228, 18, 8, "#d7cebb")
    # главный холм с травой
    s.add(path(f"M 0 {286} C 110 {250} 210 {286} 320 {276} C 390 {270} 440 {282} 480 {272} "
               f"L 480 {360} L 0 {360} Z", "url(#hill)", 1))
    s.add(path(f"M 0 {318} C 120 {300} 230 {330} 340 {312} C 400 {304} 450 {316} 480 {308} "
               f"L 480 {360} L 0 {360} Z", "#276b43", 1))
    # деревья-силуэты
    for tx, ty in ((46, 322), (76, 330), (432, 320), (462, 332)):
        s.add(f'<rect x="{f(tx-3)}" y="{f(ty)}" width="6" height="34" fill="#1a4a30"/>')
        s.add(ellipse((tx, ty - 6), 17, 24, "#1f5a39"))
        s.add(ellipse((tx - 9, ty + 4), 11, 15, "#1d5436"))
        s.add(ellipse((tx + 10, ty + 2), 10, 13, "#24643f"))
    return str(s)


def generator():
    s = Svg(W, H)
    s.add('<defs><linearGradient id="wall" x1="0" y1="0" x2="0" y2="1">'
          '<stop offset="0" stop-color="#221a20"/><stop offset="0.7" stop-color="#3a2a2e"/>'
          '<stop offset="1" stop-color="#211a1e"/></linearGradient>'
          '<radialGradient id="core" cx="0.5" cy="0.5" r="0.5">'
          '<stop offset="0" stop-color="#ffd6a0"/><stop offset="0.35" stop-color="#ff6a2a"/>'
          '<stop offset="1" stop-color="#5a1a10" stop-opacity="0"/></radialGradient></defs>')
    s.add(f'<rect width="{W}" height="{H}" fill="url(#wall)"/>')
    # панели стен
    for x in range(-20, W, 60):
        s.add(poly([(x, 0), (x + 46, 0), (x + 54, 300), (x - 2, 300)], "#2b2026", 0.55))
        s.add(line((x + 46, 0), (x + 54, 300), 2, "#151015", 0.7))
    # трубы
    for y in (26, 44):
        s.add(f'<rect x="0" y="{y}" width="{W}" height="7" fill="#3d2f33" opacity="0.9"/>')
        s.add(f'<rect x="0" y="{y+7}" width="{W}" height="3" fill="#120e12" opacity="0.7"/>')
    for x in range(30, W, 120):
        s.add(f'<rect x="{x}" y="20" width="10" height="34" fill="#4a3a3d"/>')
    # энергетическое ядро
    s.add(circle((240, 150), 150, "url(#core)", 0.55))
    s.add(circle((240, 150), 44, "#ff7a35", 0.62))
    s.add(circle((240, 150), 30, "#ffd0a0", 0.8))
    s.add(circle((240, 150), 60, "#ff5a20", 0.14))
    # кольца реактора
    for r in (70, 92, 116):
        s.add(f'<circle cx="240" cy="150" r="{r}" fill="none" stroke="#4a3238" '
              f'stroke-width="6" opacity="0.8"/>')
        s.add(f'<circle cx="240" cy="150" r="{r}" fill="none" stroke="#ff8a4a" '
              f'stroke-width="1.6" opacity="0.35"/>')
    # пол-платформа
    s.add(f'<rect x="0" y="300" width="{W}" height="60" fill="#191317"/>')
    s.add(f'<rect x="0" y="300" width="{W}" height="7" fill="#4a3a3d"/>')
    for x in range(0, W, 40):
        s.add(line((x, 307), (x - 14, 360), 2, "#0f0b0e", 0.8))
    s.add(ellipse((240, 330), 220, 26, "#ff7a35", 0.10))
    # тросы
    for x in (60, 420):
        s.add(path(f"M {x} 0 C {x+16} 90 {x-14} 150 {x+6} 220", "none", 1, "#141014", 3))
    return str(s)


def victory():
    s = Svg(W, H)
    s.add('<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
          '<stop offset="0" stop-color="#1b2a5e"/><stop offset="0.4" stop-color="#8a4a7a"/>'
          '<stop offset="0.72" stop-color="#f08a52"/><stop offset="1" stop-color="#ffd08a"/>'
          '</linearGradient></defs>')
    s.add(f'<rect width="{W}" height="{H}" fill="url(#sky)"/>')
    stars(s, 44, 21, ymax=72, size=(0.6, 1.6), op=(0.15, 0.5))
    s.add(circle((360, 250), 60, "#ffe6a8", 0.95))
    s.add(circle((360, 250), 84, "#ffe6a8", 0.18))
    # силуэт Тид
    s.add(path(f"M 0 300 C 60 290 90 296 130 288 L 130 360 L 0 360 Z", "#3a2145", 1))
    s.add(path(f"M 350 300 C 400 292 440 298 480 292 L 480 360 L 350 360 Z", "#3a2145", 1))
    for (cx, r) in ((90, 26), (150, 34), (330, 30), (410, 22)):
        s.add(f'<rect x="{f(cx-r)}" y="300" width="{f(2*r)}" height="60" fill="#40264c"/>')
        s.add(path(f"M {f(cx-r-3)} 300 A {f(r+3)} {f(r+3)} 0 0 1 {f(cx+r+3)} 300 Z",
                   "#4a2c58", 1))
    s.add(ellipse((240, 360), 300, 46, "#2a1730", 1))
    # блики на воде
    for i, y in enumerate(range(330, 358, 6)):
        s.add(ellipse((240 + (i % 2) * 10 - 5, y), 150 - i * 26, 2.4, "#ffcf95",
                      0.22 - i * 0.04))
    t = "THE END"
    size = fit(t, 300)
    s.add(text(t, (W - text_width(t, size)) / 2, 70, size, "#ffe9a8", "#3a1a08", ow=0.4,
               gap=1.7))
    return str(s)
