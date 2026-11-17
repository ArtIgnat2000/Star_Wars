# -*- coding: utf-8 -*-
"""
Векторный «риг» персонажей для набора спрайтов Star Wars (Scratch 3.0).
Все костюмы рисуются кодом, поэтому анимация согласована по пропорциям.

Система координат SVG: x вправо, y вниз. Персонаж нарисован в профиль,
лицом вправо. Ноги стоят на земле около y = 222.
"""
import math

OUT = "#241d18"          # общий контур
OUT_SOFT = "#3a2e26"


def f(v):
    return ("%g" % round(float(v), 2))


# ---------------------------------------------------------------- утилиты ----
def hex2rgb(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def rgb2hex(rgb):
    return "#" + "".join("%02x" % max(0, min(255, int(round(v)))) for v in rgb)


def shade(c, k):
    """k<0 — темнее, k>0 — светлее."""
    r, g, b = hex2rgb(c)
    if k >= 0:
        return rgb2hex((r + (255 - r) * k, g + (255 - g) * k, b + (255 - b) * k))
    return rgb2hex((r * (1 + k), g * (1 + k), b * (1 + k)))


def mix(c1, c2, t):
    a, b = hex2rgb(c1), hex2rgb(c2)
    return rgb2hex(tuple(a[i] + (b[i] - a[i]) * t for i in range(3)))


def seg(p, ang, ln):
    """Точка на расстоянии ln от p под углом ang (0° = вниз, + = вперёд/вправо)."""
    r = math.radians(ang)
    return (p[0] + ln * math.sin(r), p[1] + ln * math.cos(r))


class Svg:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.parts = []

    def add(self, s):
        self.parts.append(s)
        return self

    def __str__(self):
        body = "\n".join(self.parts)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{f(self.w)}" '
                f'height="{f(self.h)}" viewBox="0 0 {f(self.w)} {f(self.h)}">\n'
                f'{body}\n</svg>\n')

    def save(self, path):
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(str(self))


def line(p, q, w, color, opacity=1, cap="round"):
    return (f'<line x1="{f(p[0])}" y1="{f(p[1])}" x2="{f(q[0])}" y2="{f(q[1])}" '
            f'stroke="{color}" stroke-width="{f(w)}" stroke-linecap="{cap}" '
            f'opacity="{f(opacity)}"/>')


def poly(points, fill, opacity=1, stroke=None, sw=0, closed=True):
    d = " ".join(f"{f(p[0])},{f(p[1])}" for p in points)
    tag = "polygon" if closed else "polyline"
    s = f'stroke="{stroke}" stroke-width="{f(sw)}" stroke-linejoin="round" ' if stroke else ""
    return f'<{tag} points="{d}" fill="{fill}" opacity="{f(opacity)}" {s}/>'


def ellipse(c, rx, ry, fill, opacity=1, stroke=None, sw=0, rot=0):
    s = f'stroke="{stroke}" stroke-width="{f(sw)}" ' if stroke else ""
    tr = f' transform="rotate({f(rot)},{f(c[0])},{f(c[1])})"' if rot else ""
    return (f'<ellipse cx="{f(c[0])}" cy="{f(c[1])}" rx="{f(rx)}" ry="{f(ry)}" '
            f'fill="{fill}" opacity="{f(opacity)}" {s}{tr}/>')


def circle(c, r, fill, opacity=1, stroke=None, sw=0):
    s = f'stroke="{stroke}" stroke-width="{f(sw)}" ' if stroke else ""
    return (f'<circle cx="{f(c[0])}" cy="{f(c[1])}" r="{f(r)}" fill="{fill}" '
            f'opacity="{f(opacity)}" {s}/>')


def path(d, fill, opacity=1, stroke=None, sw=0):
    s = f'stroke="{stroke}" stroke-width="{f(sw)}" stroke-linejoin="round" stroke-linecap="round" ' if stroke else ""
    return f'<path d="{d}" fill="{fill}" opacity="{f(opacity)}" {s}/>'


def limb(a, b, w, color, outline=OUT, ow=4.4, shadow=None):
    """Конечность: тёмный контур + цветная «капсула» + тень по нижней стороне."""
    out = line(a, b, w + ow, outline)
    out += line(a, b, w, color)
    if shadow:
        off = (b[0] - a[0], b[1] - a[1])
        ln = math.hypot(*off) or 1
        nx, ny = -off[1] / ln, off[0] / ln
        s = 1 if color and True else 1
        p = (a[0] + nx * w * 0.22 * s, a[1] + ny * w * 0.22 * s)
        q = (b[0] + nx * w * 0.22 * s, b[1] + ny * w * 0.22 * s)
        out += line(p, q, w * 0.42, shadow)
    return out


# ------------------------------------------------------------------ мечи -----
def _blade(out, p0, p1, cfg, glow=True):
    if glow:
        out.append(line(p0, p1, 22, cfg["glow"], 0.16))
        out.append(line(p0, p1, 13, cfg["glow"], 0.30))
    out.append(line(p0, p1, 7.2, cfg["blade"], 0.95))
    out.append(line(p0, p1, 3.0, cfg["core"], 0.95))


def saber_back(hand, angle, cfg, blade_len=88, spin=0.0):
    """Задняя половина двуклинкового меча — рисуется ЗА телом."""
    if not cfg["double"]:
        return ""
    out = []
    a = angle + spin
    _blade(out, seg(hand, a + 180, blade_len * 0.52), seg(hand, a + 180, 13), cfg)
    return "".join(out)


def saber_front(hand, angle, cfg, blade_len=88, spin=0.0):
    """Рукоять, кисть и передний клинок — поверх тела."""
    out = []
    a = angle + spin
    hilt = cfg["hilt"]
    if cfg["double"]:
        out.append(line(seg(hand, a + 180, 13), seg(hand, a, 13), 9.5, OUT))
        out.append(line(seg(hand, a + 180, 12), seg(hand, a, 12), 7.4, hilt))
        out.append(line(seg(hand, a + 180, 3), seg(hand, a, 3), 2.2, shade(hilt, -0.45)))
        _blade(out, seg(hand, a, 13), seg(hand, a, blade_len), cfg)
    else:
        out.append(line(seg(hand, a + 180, 16), seg(hand, a, 14), 9.5, OUT))
        out.append(line(seg(hand, a + 180, 15), seg(hand, a, 13), 7.2, hilt))
        out.append(line(seg(hand, a + 180, 4), seg(hand, a, 4), 2.4, shade(hilt, -0.45)))
        _blade(out, seg(hand, a, 13), seg(hand, a, blade_len), cfg)
    out.append(circle(hand, 5.6, cfg["skin"], 1, OUT, 2.6))
    out.append(circle((hand[0] + 4.4, hand[1] - 3.2), 3.4, cfg["skin_l"], 0.55))
    return "".join(out)


# -------------------------------------------------------------- персонажи ----
QUIGON = dict(
    key="quigon", name="Квай-Гон",
    skin="#eec096", skin_d="#d5a077", skin_l="#f7d3ac",
    hair="#5d3c22", hair_d="#482c17",
    tunic="#d2c09a", tunic_d="#b6a47f",
    robe="#5f472f", robe_d="#4a3724",
    pants="#8d7752", belt="#40301f", boots="#4b3927",
    blade="#62f07f", core="#f2fff3", glow="#25c454",
    hilt="#9aa2a9", double=False, height=1.0, hair_style="quigon",
)
OBIWAN = dict(
    key="obiwan", name="Оби-Ван",
    skin="#f0c49c", skin_d="#d8a87f", skin_l="#f9d8b4",
    hair="#a97a45", hair_d="#8a6033",
    tunic="#e2d7b9", tunic_d="#c6b998",
    robe="#93714a", robe_d="#775a39",
    pants="#cbbd9c", belt="#5c432c", boots="#5f4730",
    blade="#5fb8ff", core="#f0f9ff", glow="#2a8fdd",
    hilt="#a7aeb5", double=False, height=0.96, hair_style="obiwan",
)
MAUL = dict(
    key="maul", name="Дарт Мол",
    skin="#cf2b2b", skin_d="#a92123", skin_l="#e2453f",
    hair=None, hair_d=None, ink="#1b1517",
    tunic="#332a3d", tunic_d="#241d2c",
    robe="#2a2133", robe_d="#1a1420",
    pants="#1e1b25", belt="#0f0c12", boots="#120f16",
    blade="#ff3f33", core="#fff0ec", glow="#e01812",
    hilt="#7d848c", double=True, height=1.06, hair_style="maul",
)

HIP = (150.0, 142.0)
TORSO_LEN = 58.0
THIGH, SHIN = 44.0, 42.0
UPPER, FORE = 30.0, 27.0

W, H = 300, 230          # холст костюма (тело по центру, справа место для клинка)


def face_path(cx, cy, s=1.0):
    """Силуэт лица в профиль (лицом вправо)."""
    x = lambda v: cx + v * s
    y = lambda v: cy + v * s
    return (f"M {f(x(-16))} {f(y(-6))} "
            f"C {f(x(-15))} {f(y(-20))} {f(x(-4))} {f(y(-25))} {f(x(6))} {f(y(-20))} "
            f"C {f(x(12))} {f(y(-17))} {f(x(13))} {f(y(-11))} {f(x(14))} {f(y(-6))} "
            f"L {f(x(15.5))} {f(y(-2))} "
            f"L {f(x(21))} {f(y(5))} "
            f"L {f(x(15.5))} {f(y(7))} "
            f"L {f(x(16.5))} {f(y(10))} "
            f"L {f(x(14))} {f(y(12))} "
            f"C {f(x(14))} {f(y(18))} {f(x(10))} {f(y(22))} {f(x(5))} {f(y(22))} "
            f"C {f(x(-3))} {f(y(22))} {f(x(-10))} {f(y(17))} {f(x(-14))} {f(y(9))} "
            f"C {f(x(-16))} {f(y(4))} {f(x(-16.5))} {f(y(-1))} {f(x(-16))} {f(y(-6))} Z")


def _head(cfg, c, tilt):
    """Голова в профиль: волосы-силуэт, лицо, борода, глаз."""
    cx, cy = c
    skin, skd = cfg["skin"], cfg["skin_d"]
    style = cfg["hair_style"]
    g = [f'<g transform="rotate({f(tilt)},{f(cx-8)},{f(cy+20)})">']

    # ---------- волосы позади головы ----------
    if style == "quigon":
        hair, hd = cfg["hair"], cfg["hair_d"]
        g.append(path(
            f"M {f(cx+10)} {f(cy-14)} "
            f"C {f(cx+2)} {f(cy-30)} {f(cx-16)} {f(cy-30)} {f(cx-20)} {f(cy-12)} "
            f"C {f(cx-25)} {f(cy+6)} {f(cx-23)} {f(cy+26)} {f(cx-16)} {f(cy+34)} "
            f"L {f(cx-4)} {f(cy+28)} "
            f"C {f(cx-9)} {f(cy+12)} {f(cx-8)} {f(cy-2)} {f(cx+4)} {f(cy-8)} Z",
            hd, 1, OUT, 3.0))
        # хвост волос за спиной
        g.append(path(
            f"M {f(cx-16)} {f(cy+22)} C {f(cx-26)} {f(cy+40)} {f(cx-24)} {f(cy+58)} "
            f"{f(cx-14)} {f(cy+66)} C {f(cx-10)} {f(cy+50)} {f(cx-10)} {f(cy+34)} "
            f"{f(cx-8)} {f(cy+24)} Z", hair, 1, OUT, 2.6))
    elif style == "obiwan":
        hair, hd = cfg["hair"], cfg["hair_d"]
        g.append(path(
            f"M {f(cx+10)} {f(cy-14)} "
            f"C {f(cx+3)} {f(cy-28)} {f(cx-14)} {f(cy-28)} {f(cx-18)} {f(cy-11)} "
            f"C {f(cx-22)} {f(cy+4)} {f(cx-21)} {f(cy+16)} {f(cx-15)} {f(cy+22)} "
            f"L {f(cx-5)} {f(cy+18)} "
            f"C {f(cx-9)} {f(cy+6)} {f(cx-8)} {f(cy-4)} {f(cx+4)} {f(cy-9)} Z",
            hd, 1, OUT, 3.0))
        g.append(line((cx - 12, cy + 12), (cx - 16, cy + 32), 4.6, hair, 1))
        g.append(circle((cx - 16, cy + 33), 2.6, hd))
    else:  # Дарт Мол: череп без волос
        g.append(ellipse((cx - 1, cy - 1), 17.5, 21, cfg["skin_d"]))

    # ---------- лицо ----------
    g.append(path(face_path(cx, cy), skin, 1, OUT, 3.4))

    # ---------- ухо ----------
    if style != "maul":
        g.append(ellipse((cx - 10, cy + 4), 3.2, 5.0, skd, 1, OUT, 2.0))
        g.append(path(f"M {f(cx-11)} {f(cy+3)} C {f(cx-8)} {f(cy+2)} {f(cx-8)} {f(cy+6)} "
                      f"{f(cx-10.5)} {f(cy+6)}", skd, 1, OUT_SOFT, 1.0))

    if style == "maul":
        ink = cfg["ink"]
        # рога по черепу
        for hx, hy, hh in ((cx - 12, cy - 16, 8), (cx - 2, cy - 20, 10), (cx + 7, cy - 18, 8),
                           (cx + 13, cy - 11, 6), (cx - 16, cy - 3, 5), (cx - 10, cy + 13, 4)):
            g.append(path(f"M {f(hx-3.6)} {f(hy+2)} L {f(hx)} {f(hy-hh)} L {f(hx+3.6)} {f(hy+2)} Z",
                          ink))
        # полоса через макушку
        g.append(f'<path d="M {f(cx+12)} {f(cy-9)} C {f(cx+5)} {f(cy-20)} {f(cx-7)} {f(cy-20)} '
                 f'{f(cx-14)} {f(cy-7)}" fill="none" stroke="{ink}" stroke-width="5" '
                 f'stroke-linecap="round"/>')
        # «очки» вокруг глаз
        g.append(path(f"M {f(cx-7)} {f(cy-9)} L {f(cx+15)} {f(cy-8)} L {f(cx+15)} {f(cy+1)} "
                      f"L {f(cx-3)} {f(cy+1)} Z", ink))
        # полоса по носу
        g.append(line((cx + 14, cy - 6), (cx + 18.5, cy + 5), 4.2, ink))
        # скулы
        g.append(line((cx - 2, cy + 4), (cx + 6, cy + 11), 3.2, ink))
        g.append(line((cx - 9, cy + 7), (cx - 3, cy + 13), 2.6, ink))
        # бородка
        g.append(path(f"M {f(cx+2)} {f(cy+12)} C {f(cx+3)} {f(cy+21)} {f(cx+10)} {f(cy+23)} "
                      f"{f(cx+14)} {f(cy+18)} C {f(cx+11)} {f(cy+16)} {f(cx+8)} {f(cy+14)} "
                      f"{f(cx+7)} {f(cy+11)} Z", ink))
        # глаза
        g.append(ellipse((cx + 8, cy - 4), 4.4, 3.3, "#ffd23f", 1, "#f7ecc0", 1.5))
        g.append(circle((cx + 9.6, cy - 4), 1.5, "#2a1c06"))
        g.append(line((cx + 10, cy + 13), (cx + 15, cy + 12), 1.8, "#7a1418"))
    else:
        # глаз
        g.append(ellipse((cx + 8, cy - 3), 3.9, 3.3, "#ffffff", 1, OUT_SOFT, 1.6))
        g.append(circle((cx + 9.4, cy - 2.8), 1.7, "#33261c"))
        g.append(line((cx + 2, cy - 9.5), (cx + 13, cy - 10), 2.8, cfg["hair_d"]))
        g.append(line((cx + 13, cy + 11.5), (cx + 16, cy + 11), 1.5, "#8d5a4a"))
        # борода
        beard = cfg["hair"]
        bd = cfg["hair_d"]
        if style == "quigon":
            g.append(path(
                f"M {f(cx+1)} {f(cy+4)} C {f(cx-2)} {f(cy+19)} {f(cx+8)} {f(cy+26)} "
                f"{f(cx+15)} {f(cy+20)} C {f(cx+18)} {f(cy+16)} {f(cx+17)} {f(cy+12)} "
                f"{f(cx+14)} {f(cy+11)} C {f(cx+12)} {f(cy+16)} {f(cx+7)} {f(cy+16)} "
                f"{f(cx+5)} {f(cy+9)} Z", beard, 1, OUT, 2.2))
            g.append(path(f"M {f(cx+7)} {f(cy+7)} C {f(cx+12)} {f(cy+5)} {f(cx+16)} {f(cy+7)} "
                          f"{f(cx+16)} {f(cy+9)} C {f(cx+12)} {f(cy+8)} {f(cx+9)} {f(cy+9)} "
                          f"{f(cx+7)} {f(cy+11)} Z", bd))
        else:
            g.append(path(
                f"M {f(cx+4)} {f(cy+8)} C {f(cx+2)} {f(cy+20)} {f(cx+9)} {f(cy+24)} "
                f"{f(cx+14)} {f(cy+19)} C {f(cx+16)} {f(cy+15)} {f(cx+15)} {f(cy+12)} "
                f"{f(cx+13)} {f(cy+11)} C {f(cx+11)} {f(cy+15)} {f(cx+8)} {f(cy+14)} "
                f"{f(cx+7)} {f(cy+8)} Z", beard, 1, OUT, 2.0))
            g.append(path(f"M {f(cx+8)} {f(cy+6)} C {f(cx+12)} {f(cy+5)} {f(cx+15)} {f(cy+6)} "
                          f"{f(cx+15)} {f(cy+8)} C {f(cx+12)} {f(cy+7)} {f(cx+10)} {f(cy+8)} "
                          f"{f(cx+8)} {f(cy+9)} Z", bd))
        # бровь-складка
        g.append(line((cx + 14, cy - 6), (cx + 17, cy - 3), 1.3, cfg["skin_d"]))

    # ---------- чёлка поверх лица ----------
    if style == "quigon":
        g.append(path(
            f"M {f(cx+13)} {f(cy-8)} C {f(cx+8)} {f(cy-20)} {f(cx-6)} {f(cy-23)} "
            f"{f(cx-15)} {f(cy-11)} L {f(cx-16)} {f(cy-2)} L {f(cx-13)} {f(cy-5)} "
            f"C {f(cx-6)} {f(cy-12)} {f(cx+4)} {f(cy-14)} {f(cx+11)} {f(cy-9)} Z",
            cfg["hair"], 1, OUT, 2.6))
        g.append(path(f"M {f(cx-13)} {f(cy-6)} C {f(cx-8)} {f(cy-18)} {f(cx+4)} {f(cy-20)} "
                      f"{f(cx+9)} {f(cy-12)} C {f(cx+2)} {f(cy-16)} {f(cx-7)} {f(cy-14)} "
                      f"{f(cx-13)} {f(cy-6)} Z", cfg["hair_d"], 0.85))
    elif style == "obiwan":
        g.append(path(
            f"M {f(cx+12)} {f(cy-8)} C {f(cx+7)} {f(cy-19)} {f(cx-5)} {f(cy-22)} "
            f"{f(cx-13)} {f(cy-11)} L {f(cx-14)} {f(cy-3)} L {f(cx-11)} {f(cy-6)} "
            f"C {f(cx-5)} {f(cy-12)} {f(cx+3)} {f(cy-13)} {f(cx+10)} {f(cy-9)} Z",
            cfg["hair"], 1, OUT, 2.6))
        g.append(path(f"M {f(cx-11)} {f(cy-7)} C {f(cx-6)} {f(cy-17)} {f(cx+3)} {f(cy-18)} "
                      f"{f(cx+8)} {f(cy-11)} C {f(cx+2)} {f(cy-15)} {f(cx-5)} {f(cy-13)} "
                      f"{f(cx-11)} {f(cy-7)} Z", cfg["hair_d"], 0.8))
    g.append("</g>")
    return "".join(g)


def character_svg(cfg, pose):
    """Собирает костюм персонажа по позе."""
    svg = Svg(W, H)
    bob = pose.get("bob", 0)
    lean = pose.get("lean", 0)
    hip = (HIP[0] + pose.get("dx", 0), HIP[1] + bob)

    skd = shade(cfg["skin"], -0.16)
    tunic_d = cfg["tunic_d"]
    robe, robe_d = cfg["robe"], cfg["robe_d"]

    # --- таз ---
    svg.add(ellipse((hip[0], hip[1] + 2), 16, 13, cfg["pants"], 1, OUT, 3))

    # --- задний клинок двуклинкового меча (за телом) ---
    _af = pose.get("armF", (26, 18))
    _sF = (hip[0] + 4, hip[1] - TORSO_LEN + 2)
    _hF = seg(seg(_sF, _af[0], UPPER), _af[0] + _af[1], FORE)
    svg.add(saber_back(_hF, pose.get("saber", 20), cfg,
                       blade_len=pose.get("blade", 88), spin=pose.get("spin", 0)))

    # --- дальняя рука ---
    ab = pose.get("armB", (10, 6))
    sB = (hip[0] - 2, hip[1] - TORSO_LEN + 2)
    eB = seg(sB, ab[0], UPPER)
    hB = seg(eB, ab[0] + ab[1], FORE)
    svg.add(limb(sB, eB, 11, tunic_d, shadow=shade(tunic_d, -0.18)))
    svg.add(limb(eB, hB, 9.4, tunic_d, shadow=shade(tunic_d, -0.18)))
    svg.add(circle(hB, 5.2, skd, 1, OUT, 2.4))

    # --- дальняя нога ---
    lb = pose.get("legB", (-8, -10))
    kB = seg(hip, lb[0], THIGH)
    aB = seg(kB, lb[0] + lb[1], SHIN)
    svg.add(limb(hip, kB, 16, shade(cfg["pants"], -0.18), shadow=shade(cfg["pants"], -0.3)))
    svg.add(limb(kB, aB, 13, shade(cfg["pants"], -0.14), shadow=shade(cfg["pants"], -0.3)))
    svg.add(boot(aB, lb[0] + lb[1], cfg, dark=True))

    # --- корпус ---
    torso = []
    sx, sy = hip[0], hip[1] - TORSO_LEN
    # плащ, уходящий назад
    torso.append(path(
        f"M {f(sx+6)} {f(sy-2)} "
        f"C {f(sx-16)} {f(sy+2)} {f(sx-28)} {f(sy+30)} {f(sx-27)} {f(hip[1]+34)} "
        f"L {f(sx-8)} {f(hip[1]+28)} "
        f"C {f(sx-12)} {f(sy+34)} {f(sx-4)} {f(sy+12)} {f(sx+10)} {f(sy+4)} Z",
        robe_d, 1, OUT, 3.0))
    # туника (светлая) — основной силуэт
    torso.append(path(
        f"M {f(sx-16)} {f(sy+1)} "
        f"C {f(sx-19)} {f(sy+22)} {f(sx-18)} {f(sy+40)} {f(sx-17)} {f(hip[1]-4)} "
        f"L {f(hip[0]-16)} {f(hip[1]+6)} L {f(hip[0]+16)} {f(hip[1]+6)} "
        f"L {f(sx+17)} {f(hip[1]-4)} "
        f"C {f(sx+19)} {f(sy+40)} {f(sx+20)} {f(sy+22)} {f(sx+17)} {f(sy+1)} "
        f"C {f(sx+8)} {f(sy-5)} {f(sx-7)} {f(sy-5)} {f(sx-16)} {f(sy+1)} Z",
        cfg["tunic"], 1, OUT, 3.4))
    # тень на спине туники
    torso.append(path(
        f"M {f(sx-16)} {f(sy+2)} C {f(sx-19)} {f(sy+24)} {f(sx-18)} {f(sy+40)} {f(sx-17)} {f(hip[1]-4)} "
        f"L {f(hip[0]-7)} {f(hip[1]+4)} L {f(hip[0]-15)} {f(sy+6)} Z", tunic_d, 0.8))
    # косой запах туники
    torso.append(path(f"M {f(sx+15)} {f(sy+3)} L {f(sx+6)} {f(hip[1]-18)} L {f(sx-1)} {f(hip[1]-18)} "
                      f"L {f(sx+7)} {f(sy+6)} Z", shade(cfg["tunic"], 0.22), 0.75))
    # пояс
    torso.append(poly([(sx - 17, hip[1] - 17), (sx + 17, hip[1] - 17),
                       (sx + 16, hip[1] - 4), (sx - 16, hip[1] - 4)],
                      cfg["belt"], 1, OUT, 2.6))
    torso.append(poly([(sx - 4, hip[1] - 16), (sx + 5, hip[1] - 16),
                       (sx + 5, hip[1] - 5), (sx - 4, hip[1] - 5)],
                      shade(cfg["belt"], 0.2), 1, None, 0))
    # передняя пола плаща
    torso.append(path(
        f"M {f(sx+13)} {f(sy+2)} C {f(sx+20)} {f(sy+18)} {f(sx+21)} {f(hip[1]+6)} "
        f"{f(sx+18)} {f(hip[1]+26)} L {f(sx+5)} {f(hip[1]+28)} "
        f"C {f(sx+10)} {f(hip[1]+8)} {f(sx+8)} {f(sy+16)} {f(sx+4)} {f(sy+5)} Z",
        robe, 1, OUT, 2.8))
    torso.append(path(
        f"M {f(sx+13)} {f(sy+3)} C {f(sx+19)} {f(sy+18)} {f(sx+20)} {f(hip[1]+6)} "
        f"{f(sx+17)} {f(hip[1]+24)} L {f(sx+11)} {f(hip[1]+25)} "
        f"C {f(sx+14)} {f(hip[1]+6)} {f(sx+13)} {f(sy+18)} {f(sx+7)} {f(sy+6)} Z",
        shade(robe, 0.12), 0.8))
    # ворот
    torso.append(path(f"M {f(sx-8)} {f(sy-2)} C {f(sx-1)} {f(sy+7)} {f(sx+7)} {f(sy+7)} "
                      f"{f(sx+12)} {f(sy-1)} C {f(sx+4)} {f(sy+2)} {f(sx-2)} {f(sy+1)} "
                      f"{f(sx-8)} {f(sy-2)} Z", shade(cfg["tunic"], -0.08)))
    if cfg["key"] == "maul":
        # открытая грудь с татуировками
        torso.append(path(f"M {f(sx+3)} {f(sy+3)} C {f(sx+15)} {f(sy+13)} {f(sx+16)} {f(sy+30)} "
                          f"{f(sx+10)} {f(hip[1]-20)} L {f(sx+1)} {f(hip[1]-20)} Z",
                          cfg["skin"], 1, OUT, 2.4))
        torso.append(line((sx + 6, sy + 9), (sx + 11, sy + 26), 2.6, cfg["ink"]))
        torso.append(line((sx + 11, sy + 7), (sx + 13, sy + 18), 2.2, cfg["ink"]))
        torso.append(line((sx + 4, sy + 14), (sx + 9, sy + 15), 1.8, cfg["ink"]))
    svg.add(f'<g transform="rotate({f(lean)},{f(hip[0])},{f(hip[1])})">{"".join(torso)}</g>')

    # --- ближняя нога ---
    lf = pose.get("legF", (8, 6))
    kF = seg(hip, lf[0], THIGH)
    aF = seg(kF, lf[0] + lf[1], SHIN)
    svg.add(limb(hip, kF, 17, cfg["pants"], shadow=shade(cfg["pants"], -0.22)))
    svg.add(limb(kF, aF, 14, cfg["pants"], shadow=shade(cfg["pants"], -0.22)))
    svg.add(boot(aF, lf[0] + lf[1], cfg))

    # --- голова ---
    neck = (hip[0] + 3, hip[1] - TORSO_LEN - 6)
    head_c = (neck[0] + 3, neck[1] - 16)
    svg.add(f'<g transform="rotate({f(lean)},{f(hip[0])},{f(hip[1])})">')
    svg.add(limb((neck[0] - 2, neck[1] + 6), (neck[0] + 1, neck[1] - 2), 11, skd, ow=3.4))
    svg.add(_head(cfg, head_c, pose.get("head", 0)))
    svg.add("</g>")

    # --- ближняя рука + меч ---
    af = pose.get("armF", (26, 18))
    sF = (hip[0] + 4, hip[1] - TORSO_LEN + 2)
    eF = seg(sF, af[0], UPPER)
    hF = seg(eF, af[0] + af[1], FORE)
    sleeve = cfg["tunic"]
    svg.add(limb(sF, eF, 12, shade(sleeve, 0.06) if cfg["key"] == "maul" else sleeve,
                 shadow=shade(sleeve, -0.14)))
    if cfg["key"] == "maul":
        # голая рука с татуировками
        svg.add(limb(eF, hF, 9.6, cfg["skin"], shadow=cfg["ink"]))
        svg.add(line(seg(eF, af[0] + af[1], 8), seg(eF, af[0] + af[1], 20), 2.2, cfg["ink"], 0.9))
    else:
        svg.add(limb(eF, hF, 10, sleeve, shadow=shade(sleeve, -0.14)))
        svg.add(line(seg(eF, af[0] + af[1], 14), hF, 11, shade(cfg["boots"], 0.05), 0.0))
    svg.add(saber_front(hF, pose.get("saber", 20), cfg,
                        blade_len=pose.get("blade", 88), spin=pose.get("spin", 0)))
    return str(svg)


def boot(ankle, shin_ang, cfg, dark=False):
    """Сапог: голенище по направлению голени + стопа носком вперёд."""
    c = shade(cfg["boots"], -0.22) if dark else cfg["boots"]
    fx, fy = ankle
    out = line(seg(ankle, shin_ang, -15), ankle, 19, OUT)
    out += line(seg(ankle, shin_ang, -14), ankle, 15.4, c)
    foot = (f"M {f(fx-9)} {f(fy-4)} L {f(fx+11)} {f(fy-5)} "
            f"C {f(fx+17)} {f(fy-4)} {f(fx+18)} {f(fy+4)} {f(fx+11)} {f(fy+5)} "
            f"L {f(fx-8)} {f(fy+6)} C {f(fx-12)} {f(fy+5)} {f(fx-12)} {f(fy-2)} "
            f"{f(fx-9)} {f(fy-4)} Z")
    out += path(foot, c, 1, OUT, 3.0)
    out += path(f"M {f(fx-7)} {f(fy-2)} L {f(fx+12)} {f(fy-2)}", c, 0, shade(c, 0.18), 2.0)
    return out
