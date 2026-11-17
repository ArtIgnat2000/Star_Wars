# -*- coding: utf-8 -*-
"""Постер набора: preview/poster.svg (рендерится в preview/poster.png)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rig import QUIGON, OBIWAN, MAUL, character_svg            # noqa: E402
import rig                                                     # noqa: E402
import backdrops as B                                          # noqa: E402
import vehicles as V                                           # noqa: E402

W, H = 1600, 900

STANCE = dict(lean=2, legF=(10, 4), legB=(-10, -6), armB=(14, 16), armF=(40, 30), saber=52)
BLOCK = dict(lean=0, legF=(12, 6), legB=(-12, -10), armB=(0, 20), armF=(56, 40), saber=172)
MAUL_ST = dict(lean=3, legF=(14, 8), legB=(-14, -10), armB=(18, 14), armF=(50, 24),
               saber=104, head=-2, blade=86)
MAUL_STRIKE = dict(lean=8, legF=(24, 8), legB=(-22, -16), armB=(20, 10), armF=(78, 4),
                   saber=118, head=4)


def body(svg_text):
    return svg_text.split("\n", 1)[1].rsplit("</svg>", 1)[0]


def place(svg_text, x, y_feet, scale, mirror=False):
    s = scale
    if mirror:
        tx = x + 150 * s
        tr = f"translate({tx:.1f},{y_feet - 222 * s:.1f}) scale({-s},{s})"
    else:
        tr = f"translate({x - 150 * s:.1f},{y_feet - 222 * s:.1f}) scale({s})"
    return f'<g transform="{tr}">{body(svg_text)}</g>'


def main():
    s = rig.Svg(W, H)
    # --- космос ---
    s.add('<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
          '<stop offset="0" stop-color="#03040e"/><stop offset="0.55" stop-color="#0a1633"/>'
          '<stop offset="1" stop-color="#14264a"/></linearGradient>'
          '<radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">'
          '<stop offset="0" stop-color="#ffb04a" stop-opacity="0.5"/>'
          '<stop offset="1" stop-color="#ff6a2a" stop-opacity="0"/></radialGradient>'
          '<radialGradient id="atm" cx="0.5" cy="0.5" r="0.5">'
          '<stop offset="0.62" stop-color="#5fd0ff" stop-opacity="0"/>'
          '<stop offset="0.85" stop-color="#5fd0ff" stop-opacity="0.35"/>'
          '<stop offset="1" stop-color="#5fd0ff" stop-opacity="0"/>'
          '</radialGradient></defs>')
    s.add(f'<rect width="{W}" height="{H}" fill="url(#sky)"/>')
    B.stars(s, 260, 5, ymax=700, size=(0.8, 3.2))
    B.nebula(s, 300, 240, 520, 300, "#3b6fd6", 0.20)
    B.nebula(s, 1300, 180, 420, 260, "#8a3bd6", 0.16)
    # планета
    s.add(f'<circle cx="240" cy="1080" r="470" fill="#1f6f92"/>')
    s.add(f'<circle cx="240" cy="1080" r="455" fill="#2b8aa8"/>')
    s.add(f'<ellipse cx="120" cy="760" rx="190" ry="52" fill="#69cfa6" opacity="0.5"/>')
    s.add(f'<ellipse cx="330" cy="820" rx="150" ry="40" fill="#69cfa6" opacity="0.35"/>')
    s.add(f'<circle cx="240" cy="1080" r="500" fill="url(#atm)"/>')
    # световой «взрыв» за фигурами
    s.add(f'<ellipse cx="800" cy="620" rx="520" ry="300" fill="url(#glow)"/>')
    # корабли
    ship = vehicles_body(V.naboo_fighter(1.1))
    s.add(f'<g transform="translate(1330,120) rotate(16) scale(0.98)">{ship}</g>')
    droid = vehicles_body(V.droid_fighter(True))
    s.add(f'<g transform="translate(1470,560) rotate(-14) scale(0.9)">{droid}</g>')
    s.add(f'<g transform="translate(150,430) rotate(-8) scale(0.6)">{droid}</g>')
    # персонажи
    s.add(place(character_svg(QUIGON, dict(STANCE, saber=120)), 430, 812, 1.55))
    s.add(place(character_svg(OBIWAN, dict(BLOCK, lean=4)), 700, 818, 1.7))
    s.add(place(character_svg(MAUL, MAUL_STRIKE), 1160, 818, 1.8, mirror=True))
    # заголовок
    t = "STAR WARS"
    size = B.fit(t, 700, 1.5)
    s.add(B.text(t, (W - B.text_width(t, size, 1.5)) / 2, 96, size, "#ffe14d", "#2b1a05",
                 ow=0.34, gap=1.5))
    s.add(f'<text x="{W/2}" y="290" text-anchor="middle" font-family="DejaVu Sans" '
          f'font-weight="bold" font-size="64" fill="#dfe9ff" stroke="#0b1426" '
          f'stroke-width="6" paint-order="stroke">ДУЭЛЬ НА НАБУ</text>')
    s.add(f'<text x="{W/2}" y="352" text-anchor="middle" font-family="DejaVu Sans" '
          f'font-size="30" fill="#9fb2d8" letter-spacing="4">СПРАЙТЫ И ФОНЫ ДЛЯ SCRATCH 3.0</text>')
    # нижняя плашка
    s.add(f'<rect x="0" y="826" width="{W}" height="74" fill="#050912" opacity="0.55"/>')
    s.add(f'<text x="{W/2}" y="872" text-anchor="middle" font-family="DejaVu Sans" '
          f'font-size="26" fill="#c9d6ee">Квай-Гон · Оби-Ван · Дарт Мол · N-1 · дроид-истребитель · '
          f'фоны Набу</text>')
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "preview", "poster.svg")
    open(out, "w", encoding="utf-8").write(str(s))
    print("готово:", out)


def vehicles_body(svg_text):
    return svg_text.split("\n", 1)[1].rsplit("</svg>", 1)[0]


if __name__ == "__main__":
    main()
