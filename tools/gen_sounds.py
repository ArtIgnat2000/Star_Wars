# -*- coding: utf-8 -*-
"""Синтез звуков для игры (WAV 44100 Гц, моно, 16 бит)."""
import math
import os
import random
import struct
import wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "sounds")
SR = 44100


def write_wav(name, samples, sr=SR):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    frames = b"".join(struct.pack("<h", int(max(-1.0, min(1.0, s)) * 32000)) for s in samples)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(frames)
    return path, len(samples)


def sweep(dur, f0, f1, shape="sine", decay=8.0, harm=2, harm_amp=0.25):
    n = int(dur * SR)
    out = []
    ph = 0.0
    for i in range(n):
        t = i / SR
        fr = f0 + (f1 - f0) * (t / dur)
        ph += 2 * math.pi * fr / SR
        if shape == "square":
            v = 1.0 if math.sin(ph) >= 0 else -1.0
        elif shape == "saw":
            v = 2 * ((ph / (2 * math.pi)) % 1.0) - 1
        else:
            v = math.sin(ph)
        v += harm_amp * math.sin(ph * harm)
        env = math.exp(-decay * t) * min(1.0, t * 400)
        out.append(v * env * 0.5)
    return out


def noise_burst(dur, decay=6.0, lp=0.35, tone=None, tone_amp=0.5):
    n = int(dur * SR)
    rnd = random.Random(5)
    out = []
    prev = 0.0
    ph = 0.0
    for i in range(n):
        t = i / SR
        x = rnd.uniform(-1, 1)
        prev = prev + lp * (x - prev)
        v = prev * 3.2
        if tone:
            ph += 2 * math.pi * tone * math.exp(-1.2 * t) / SR
            v += tone_amp * math.sin(ph)
        out.append(v * math.exp(-decay * t))
    return out


def mix(*tracks):
    n = max(len(t) for t in tracks)
    out = [0.0] * n
    for tr in tracks:
        for i, v in enumerate(tr):
            out[i] += v
    return [max(-1.0, min(1.0, v * 0.8)) for v in out]


def clash():
    out = []
    rnd = random.Random(9)
    dur = 0.45
    n = int(dur * SR)
    parts = [(rnd.uniform(700, 3600), rnd.uniform(0.02, 0.08)) for _ in range(7)]
    for i in range(n):
        t = i / SR
        v = 0.0
        for f, d in parts:
            v += math.sin(2 * math.pi * f * t) * math.exp(-d * 40 * t) * 0.16
        v += rnd.uniform(-1, 1) * math.exp(-28 * t) * 0.25
        out.append(v * min(1.0, t * 600))
    return out


def hum(dur=2.0):
    n = int(dur * SR)
    out = []
    for i in range(n):
        t = i / SR
        v = 0.34 * math.sin(2 * math.pi * 96 * t)
        v += 0.22 * math.sin(2 * math.pi * 192 * t + 0.7)
        v += 0.12 * math.sin(2 * math.pi * 288 * t + 1.4)
        v += 0.05 * math.sin(2 * math.pi * 432 * t)
        am = 0.82 + 0.18 * math.sin(2 * math.pi * 6 * t)
        v *= am * 0.6
        v *= min(1.0, i / 900) * min(1.0, (n - i) / 900)
        out.append(v)
    return out


def notes(seq, dur=0.2, shape="triangle"):
    out = []
    for k, fr in enumerate(seq):
        n = int(dur * SR)
        for i in range(n):
            t = i / SR
            ph = 2 * math.pi * fr * t
            if shape == "triangle":
                v = 2 / math.pi * math.asin(math.sin(ph))
            else:
                v = math.sin(ph)
            env = min(1.0, t * 90) * math.exp(-3.2 * t)
            out.append(v * env * 0.55)
    return out


def main():
    made = []
    made.append(("лазер.wav", sweep(0.22, 1500, 220, "square", 11, 2, 0.3)))
    made.append(("лазер-врага.wav", sweep(0.18, 900, 160, "square", 12, 2, 0.25)))
    made.append(("меч-вкл.wav", sweep(0.55, 70, 320, "saw", 1.2, 2, 0.4)))
    made.append(("меч-выкл.wav", sweep(0.5, 320, 70, "saw", 2.4, 2, 0.4)))
    made.append(("удар-меча.wav", clash()))
    made.append(("взрыв.wav", mix(noise_burst(0.8, 5.5, 0.22, 70, 0.7),
                                 noise_burst(0.6, 8.0, 0.5))))
    made.append(("гудение-меча.wav", hum(2.0)))
    made.append(("победа.wav", notes([523, 659, 784, 1047], 0.22)))
    made.append(("поражение.wav", notes([440, 392, 330, 262], 0.26, "sine")))
    total = 0
    for name, samples in made:
        path, n = write_wav(name, samples)
        total += n
        print(f"{name}: {n} сэмплов, {os.path.getsize(path)//1024} КБ")
    print("всего сэмплов:", total)


if __name__ == "__main__":
    main()
