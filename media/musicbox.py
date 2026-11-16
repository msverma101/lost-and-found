#!/usr/bin/env python3
"""Original music-box waltz for LOST & FOUND (composed for this film, no samples).
Writes audio/theme.wav (two passes, gentle), audio/theme_winddown.wav (slows and stops),
audio/theme_end.wav (one pass + final chord)."""
import os, wave
import numpy as np

SR = 44100
OUT = os.path.dirname(os.path.abspath(__file__))
NOTE = {n: i for i, n in enumerate("C C# D D# E F F# G G# A A# B".split())}


def freq(name):
    pitch, octave = name[:-1], int(name[-1])
    return 440.0 * 2 ** ((NOTE[pitch] + 12 * (octave - 4) - 9) / 12)


def tine(f, dur=2.6, vel=1.0):
    t = np.arange(int(SR * dur)) / SR
    # tuned steel tine: fundamental, octave and a slightly inharmonic high partial, each decaying faster
    s = (np.sin(2 * np.pi * f * t) * np.exp(-t * 1.6)
         + 0.35 * np.sin(2 * np.pi * f * 2.0 * t) * np.exp(-t * 3.5)
         + 0.12 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 9.0))
    attack = np.minimum(1, t / 0.002)
    return vel * s * attack


# melody (3/4 waltz, one note per beat, "-" = hold) and bass on beat 1 of each bar
MEL = ("E5 A5 C6 | B5 A5 E5 | F5 A5 D6 | C6 B5 - | E5 G5 B5 | A5 G5 E5 | D5 F5 A5 | G#5 - - | "
       "E5 A5 C6 | B5 A5 E5 | F5 A5 D6 | C6 B5 A5 | G5 E5 C6 | B5 D5 G#5 | A5 - - | - - -")
BASS = "A3 E3 D3 E3 C3 C3 D3 E3 A3 E3 D3 F3 C3 E3 A2 -".split()


def render(passes=1, bpm=72, slow_to=None, final_chord=False, vel=0.8):
    bars = [b.split() for b in MEL.split("|")]
    events, beat = [], 0
    for _ in range(passes):
        for bi, bar in enumerate(bars):
            if BASS[bi] != "-":
                events.append((beat, BASS[bi], 0.5))
            for k, n in enumerate(bar):
                if n != "-":
                    events.append((beat + k, n, 1.0))
            beat += 3
    total_beats = beat
    # beat -> seconds, optionally slowing (a winding-down spring)
    def when(b):
        if slow_to is None:
            return b * 60 / bpm
        # tempo falls linearly from bpm to slow_to across the piece
        bs = np.linspace(0, b, 200)
        tempo = bpm + (slow_to - bpm) * bs / total_beats
        return np.trapezoid(60 / tempo, bs) if hasattr(np, "trapezoid") else np.trapz(60 / tempo, bs)
    if final_chord:
        events += [(total_beats, n, 0.7) for n in ("A3", "E4", "A4", "C5", "E5")]
    length = when(total_beats + (4 if final_chord else 0)) + 3
    buf = np.zeros(int(SR * length))
    rng = np.random.default_rng(1)
    for b, n, v in events:
        start = int(SR * (when(b) + rng.normal(0, 0.006)))  # slight mechanical unevenness
        x = tine(freq(n), vel=v * vel * rng.uniform(0.9, 1.05))
        buf[start:start + len(x)] += x[: len(buf) - start]
    # small-room reverb: a few feedback delays
    wet = buf.copy()
    for d, g in ((0.031, 0.35), (0.047, 0.3), (0.071, 0.25), (0.113, 0.2), (0.173, 0.15)):
        k = int(SR * d)
        for _ in range(3):
            wet[k:] += g * wet[:-k] * 0.5
    out = 0.75 * buf + 0.25 * wet / 3
    # faint mechanism hiss and fade out
    out += rng.normal(0, 0.0015, len(out))
    fade = int(SR * 2.5)
    out[-fade:] *= np.linspace(1, 0, fade)
    return out / np.max(np.abs(out)) * 0.8


def save(name, x):
    st = np.stack([x, np.roll(x, 90) * 0.97], axis=1)  # slight stereo width
    data = (st * 32767).astype("<i2").tobytes()
    with wave.open(os.path.join(OUT, name), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(data)
    print(name, f"{len(x) / SR:.1f}s")


save("theme.wav", render(passes=2, bpm=72))
save("theme_winddown.wav", render(passes=1, bpm=66, slow_to=26))
save("theme_end.wav", render(passes=1, bpm=64, final_chord=True))
