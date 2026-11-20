"""Mood music + SFX: ukulele (room) -> chiptune + sparkle arpeggio (secret level) -> faster chiptune (treasure) -> ukulele (home)."""
import numpy as np, soundfile as sf
from scipy.signal import resample_poly, butter, sosfilt
from cues import *

SR = 48000; N = int(DURATION * SR)
rng = np.random.default_rng(7)
play = np.zeros(N); spook = np.zeros(N); sfx = np.zeros(N); voice = np.zeros(N)

def add(buf, x, t, g=1.0):
    i = int(t * SR)
    if i >= N or i < 0: return
    x = x[: N - i]; buf[i:i + len(x)] += g * x
def hz(m): return 440.0 * 2 ** ((m - 69) / 12)
def env(n, a=0.005, d=0.3):
    t = np.arange(n) / SR; return np.minimum(1, t / a) * np.exp(-t / d)
def noise(d): return rng.uniform(-1, 1, int(d * SR))
def band(x, lo, hi): return sosfilt(butter(2, [lo, hi], btype="band", fs=SR, output="sos"), x)
def lp(x, f): return sosfilt(butter(2, f, btype="low", fs=SR, output="sos"), x)
_ks = {}
def pluck(m, dur=1.0, decay=0.45):
    key = (m, decay)
    if key in _ks: return _ks[key]
    f = hz(m); p = int(SR / f); n = int(dur * SR); buf = rng.uniform(-1, 1, p); out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % p]; buf[i % p] = 0.996 * 0.5 * (buf[i % p] + buf[(i + 1) % p])
    out *= np.exp(-np.arange(n) / SR / decay); _ks[key] = out; return out
def glock(f, dur=1.0, d=0.45):
    t = np.arange(int(dur * SR)) / SR
    return (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / 0.08)) * env(len(t), 0.002, d)
def sweep(f0, f1, dur, vib=0.0, d=None, shape=1.0):
    n = int(dur * SR); t = np.arange(n) / SR; f = f0 + (f1 - f0) * (t / dur) ** shape
    if vib: f = f * (1 + 0.06 * np.sin(2 * np.pi * vib * t))
    e = np.minimum(1, t / 0.01) * (np.exp(-t / d) if d else np.minimum(1, (dur - t) / 0.05))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * e

def ukulele(buf, t0, t1, chords, roots, bpm=118, g=1.0):
    B = 60 / bpm; bar = 0
    while t0 + bar * 4 * B < t1:
        tb = t0 + bar * 4 * B; c_ = bar % len(chords)
        for k, s in enumerate((0, 1, 1.5, 2.5, 3)):
            for j, m in enumerate(chords[c_] if k != 2 else chords[c_][::-1]): add(buf, pluck(m), tb + s * B + j * 0.012, 0.14 * g)
        for s in (0, 2):
            bt = np.arange(int(B * 1.5 * SR)) / SR; add(buf, np.sin(2 * np.pi * hz(roots[c_]) * bt) * env(len(bt), 0.01, 0.3), tb + s * B, 0.45 * g)
        for e8 in range(8): add(buf, band(noise(0.05), 5000, 11000) * env(int(0.05 * SR), 0.002, 0.02), tb + e8 * B / 2, (0.08 if e8 % 2 else 0.045) * g)
        for s in (1, 3): add(buf, band(noise(0.1), 900, 3500) * env(int(0.1 * SR), 0.002, 0.04), tb + s * B, 0.14 * g)
        bar += 1

MAJ = [[60, 64, 67, 72], [60, 65, 69, 72], [59, 62, 67, 71], [60, 64, 67, 72], [57, 60, 64, 69], [57, 60, 65, 69], [59, 62, 67, 71], [60, 64, 67, 72]]
ROOT = [36, 41, 43, 36, 45, 41, 43, 36]
ukulele(play, 0.0, T_PULL + 0.6, MAJ, ROOT)
ukulele(play, T_BACK + 0.4, DURATION, MAJ, ROOT, bpm=124)

# ---- chiptune game music (square lead + triangle bass + noise drums), faster during the kart chase
game = np.zeros(N)
def sq(f, d, duty=0.5, g=1.0):
    n = int(d * SR); tt = np.arange(n) / SR; ph = (f * tt) % 1
    return np.where(ph < duty, 1.0, -1.0) * np.minimum(1, tt / 0.004) * np.exp(-tt / (d * 0.9)) * g
def tri(f, d):
    n = int(d * SR); tt = np.arange(n) / SR; ph = (f * tt) % 1
    return (4 * np.abs(ph - 0.5) - 1) * np.minimum(1, (d - tt) / 0.01)
LEAD = [72, 76, 79, 76, 74, 77, 81, 77, 71, 74, 79, 74, 72, 76, 79, 84]
CH = [(48, [60, 64, 67]), (53, [65, 69, 72]), (55, [67, 71, 74]), (48, [60, 64, 67])]
def chip(t0, t1, bpm, g=1.0):
    B = 60 / bpm; k = 0; t = t0
    while t < t1:
        bar = (k // 16) % 4; root, ch = CH[bar]
        add(game, sq(hz(LEAD[k % 16] + (0 if bar % 2 == 0 else 2)), B / 2 * 0.95, 0.25), t, 0.07 * g)
        if k % 2 == 0: add(game, tri(hz(root - 12 + (7 if (k // 2) % 4 == 2 else 0)), B * 0.9), t, 0.32 * g)
        if k % 4 == 0: add(game, sweep(160, 50, 0.12, d=0.05), t, 0.5 * g)                      # kick
        if k % 4 == 2: add(game, band(noise(0.08), 2000, 9000) * env(int(0.08 * SR), 0.002, 0.03), t, 0.25 * g)  # snare
        add(game, band(noise(0.03), 7000, 12000) * env(int(0.03 * SR), 0.001, 0.01), t, 0.05 * g)
        t += B / 2; k += 1
chip(T_CITY + 0.6, T_TREASURE, 120, 0.85)
chip(T_TREASURE, T_SAVE + 0.4, 140, 1.0)
# sparkly sky pad (soft glock arpeggio) in the secret level
t = T_CITY + 0.6
while t < T_TREASURE:
    for k, m in enumerate((84, 88, 91, 96)): add(sfx, glock(hz(m), 0.8, 0.5), t + k * 0.12, 0.035)
    t += 2.0

# ---- SFX
def boing(t, g=0.3): add(sfx, sweep(180, 620, 0.3, vib=18, shape=0.6), t, g)
def shimmer(t, notes=(72, 76, 79, 84, 88, 91), step=0.07, g=0.2):
    for i, m in enumerate(notes): add(sfx, glock(hz(m), 1.3, 0.6), t + i * step, g)
def whoosh(t, g=0.35, d=0.6):
    n = int(d * SR); x = noise(d); tt = np.arange(n) / SR
    y = sosfilt(butter(2, [600, 3000], btype="band", fs=SR, output="sos"), x) * np.sin(np.pi * tt / d) ** 2; add(sfx, y, t, g)
def ting(t, g=0.16):
    add(sfx, sq(hz(88), 0.07, 0.5, 1.0), t, g); add(sfx, sq(hz(95), 0.18, 0.5, 1.0), t + 0.07, g)
def fanfare(t, g=0.14):
    for i, m in enumerate((72, 76, 79, 84)): add(sfx, sq(hz(m), 0.14, 0.25), t + i * 0.1, g)
    add(sfx, sq(hz(88), 0.6, 0.25), t + 0.4, g); shimmer(t + 0.4, g=0.12)
def oops(t, g=0.16):
    for i, m in enumerate((67, 63, 60)): add(sfx, sq(hz(m), 0.22, 0.5), t + i * 0.2, g)
    add(sfx, sweep(300, 120, 0.5, vib=8), t + 0.6, 0.2)
def bleep(t, m=84, g=0.12): add(sfx, sq(hz(m), 0.09, 0.5), t, g)
def thud(t, g=0.6): add(sfx, sweep(120, 40, 0.25, d=0.1), t, g); add(sfx, lp(noise(0.15), 500) * env(int(0.15 * SR), 0.002, 0.05), t, 0.4)
def whirr(t, d, g=0.07):
    n = int(d * SR); tt = np.arange(n) / SR
    add(sfx, sq(110, d, 0.5) * 0 + np.sign(np.sin(2 * np.pi * (90 + 20 * np.sin(2 * np.pi * 3 * tt)) * tt)) * np.minimum(1, np.minimum(tt, d - tt) / 0.05), t, g)
def riser(t, d, g=0.3):
    n = int(d * SR); tt = np.arange(n) / SR; f = 200 + 1400 * (tt / d) ** 2
    add(sfx, np.sin(2 * np.pi * np.cumsum(f) / SR) * (tt / d) * 0.6 + band(noise(d), 1500, 8000) * (tt / d) ** 2 * 0.6, t, g)
def flap(t):
    for k in range(7): whoosh(t + k * 0.55, 0.22, 0.4)

def buzz(t):
    add(sfx, sq(hz(43), 0.5, 0.5) * 0.7 + sq(hz(44), 0.5, 0.5) * 0.7, t, 0.12)
def pop(t, g=0.35):
    add(sfx, lp(noise(0.4), 1200) * env(int(0.4 * SR), 0.002, 0.12), t, g)
    for k in range(5): add(sfx, band(noise(0.03), 4000, 11000) * env(int(0.03 * SR), 0.001, 0.01), t + 0.1 + k * 0.07 + rng.uniform(0, 0.04), 0.15)

add(sfx, band(noise(0.05), 1500, 6000) * env(int(0.05 * SR), 0.001, 0.02), T_KEYIN + 1.0, 0.5)   # key in
add(sfx, band(noise(0.08), 800, 4000) * env(int(0.08 * SR), 0.001, 0.03), T_KEYIN + 1.9, 0.6)    # click-turn
bleep(T_START + 0.1, 79); bleep(T_START + 0.22, 86); shimmer(T_START + 0.3)
riser(T_PULL, T_CITY - T_PULL, 0.35); whoosh(T_PULL + 0.4, 0.4, 1.2); whoosh(T_CITY - 0.4, 0.5, 0.8)
shimmer(T_CITY + 0.1, (84, 88, 91, 96), 0.06, 0.18)
for k in range(3): thud(T_CITY + 0.8 + k * 0.15, 0.35)
fanfare(T_CITY + 1.6)
boing(T_MOTI, 0.3); buzz(T_MOTI + 0.5); add(sfx, lp(noise(1.2), 160) * np.sin(np.pi * np.arange(int(1.2 * SR)) / SR / 1.2), T_MOTI + 0.6, 0.6)
boing(T_MOTIBACK, 0.25)
for k, h in enumerate(HOPS):
    add(sfx, glock(hz([72, 74, 76, 77, 79, 81, 83][k]), 1.0, 0.5), h, 0.3); add(sfx, sweep(300, 700, 0.15, d=0.08), h - 0.05, 0.1)
shimmer(T_BRIDGE, (72, 76, 79, 84, 88, 91, 96), 0.06, 0.2); fanfare(T_BRIDGE + 0.3, 0.1)
for k in range(18): add(sfx, glock(hz(96 + (k % 3) * 2), 0.3, 0.1), T_CROSS + 0.4 + k * 0.42, 0.05)   # plinky footsteps on the rainbow
boing(S("wobbly") - 0.2, 0.25)
add(sfx, sweep(160, 120, 0.6, vib=12), T_OPEN, 0.18)    # creak
shimmer(T_OPEN + 0.3, (72, 76, 79, 84, 88, 91, 96), 0.07, 0.22); fanfare(T_TROPHY + 0.3)
import random as _r
_rr = _r.Random(11)
for k in range(14):
    tb = T_FIRE + k * 0.55 + _rr.uniform(0, 0.3); _rr.uniform(120, 1160); _rr.uniform(80, 300); _rr.choice(range(9))
    pop(tb, 0.3)
shimmer(T_NOTE, (84, 88, 91), 0.06, 0.12)
fanfare(S("complete") - 0.1); ting(S("complete") + 0.2); ting(S("complete") + 0.4)
riser(T_SAVE, T_BACK - T_SAVE, 0.3); whoosh(T_BACK - 0.3, 0.5, 0.8)
thud(T_BACK + 1.0); thud(T_BACK + 1.25); thud(T_BACK + 1.6, 0.4)
add(sfx, glock(hz(96), 0.6, 0.2), T_BACK + 1.9, 0.25)   # trophy clink on the cabinet
shimmer(T_OUTRO + 0.2); boing(S("bye2"))

speech = np.zeros(N, bool)
for l in LINES:
    x, sr = sf.read(l["file"]); x = resample_poly(x, SR, sr); add(voice, x, l["start"])
    speech[int(l["start"] * SR):int(l["end"] * SR)] = True

k_ = int(0.12 * SR)
duck = np.convolve(np.where(speech, 0.32, 1.0), np.ones(k_) / k_, "same")
tt = np.arange(N) / SR
pl = np.clip(1 - (tt - T_PULL) / 1.0, 0, 1) + np.clip((tt - T_BACK - 0.2) / 1.0, 0, 1)
fade = np.ones(N); fl = int(2.5 * SR); fade[-fl:] = np.linspace(1, 0, fl)
mix = voice + (play * 0.55 * np.clip(pl, 0, 1) + game * 0.9) * duck * fade + sfx * 0.8
mix = np.tanh(mix * 1.1) * 0.9
sf.write("audio/mix.wav", np.stack([mix, mix], 1), SR, subtype="PCM_16"); print("ok", DURATION)
