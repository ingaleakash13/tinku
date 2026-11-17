import numpy as np, soundfile as sf
from scipy.signal import resample_poly, butter, sosfilt
from cues import *

SR = 48000
N = int(DURATION * SR)
rng = np.random.default_rng(11)
drone = np.zeros(N); tabla = np.zeros(N); flute = np.zeros(N); sfx = np.zeros(N); voice = np.zeros(N)


def add(buf, x, t, g=1.0):
    i = int(t * SR)
    if i >= N or i + len(x) <= 0: return
    if i < 0: x = x[-i:]; i = 0
    x = x[: N - i]; buf[i:i + len(x)] += g * x

def tt(d): return np.arange(int(d * SR)) / SR
def env(n, a=0.005, d=0.3):
    t = np.arange(n) / SR; return np.minimum(1, t / a) * np.exp(-t / d)
def noise(d): return rng.uniform(-1, 1, int(d * SR))
def band(x, lo, hi): return sosfilt(butter(2, [lo, hi], btype="band", fs=SR, output="sos"), x)
def hz(m): return 440 * 2 ** ((m - 69) / 12)

SA = 50  # D3 (midi 50)

# ---------------- tanpura drone: Pa Sa Sa Sa(low), with buzzy harmonics
def tanpura_pluck(f, d=3.2):
    t = tt(d); x = np.zeros_like(t)
    for h in range(1, 14):
        x += (1 / h ** 0.9) * np.sin(2 * np.pi * f * h * t + h) * np.exp(-t / (2.4 / (1 + h * 0.08)))
    return x * np.minimum(1, t / 0.01) * 0.12
cyc = 3.0; t0 = 0.0
while t0 < DURATION:
    for k, m in enumerate((SA + 7 - 12, SA, SA, SA - 12)):
        add(drone, tanpura_pluck(hz(m)), t0 + k * cyc / 4)
    t0 += cyc

# ---------------- bansuri melody (Yaman-flavoured), played in the gaps
SCALE = [0, 2, 4, 6, 7, 9, 11, 12, 14, 16]
PHRASES = [[(4, 1), (6, 0.5), (7, 0.5), (9, 1.5), (7, 0.5), (6, 1), (4, 2)],
           [(2, 0.5), (4, 0.5), (6, 1), (4, 0.5), (2, 0.5), (0, 3)],
           [(7, 1), (9, 1), (11, 0.5), (12, 0.5), (11, 1), (9, 2)],
           [(9, 0.5), (7, 0.5), (6, 1), (4, 1), (2, 1), (0, 2)]]
BEAT = 60 / 84

def bansuri(f, d):
    t = tt(d + 0.25)
    vib = 1 + 0.008 * np.sin(2 * np.pi * 5.2 * t) * np.minimum(1, t / 0.4)
    ph = 2 * np.pi * np.cumsum(f * vib) / SR
    x = np.sin(ph) + 0.18 * np.sin(2 * ph) + 0.05 * np.sin(3 * ph)
    breath = band(noise(d + 0.25), 1500, 5000) * 0.05
    e = np.minimum(1, t / 0.08) * np.minimum(1, np.maximum(0, (d + 0.25 - t)) / 0.2)
    return (x + breath) * e

t0 = 0.5; pi_ = 0
while t0 < DURATION:
    for (deg, ln) in PHRASES[pi_ % 4]:
        add(flute, bansuri(hz(SA + 12 + deg), ln * BEAT), t0, 0.22)
        t0 += ln * BEAT
    t0 += 2 * BEAT; pi_ += 1

# ---------------- tabla (keherwa) — festive scenes only
def dayan(f=520, d=0.18):
    t = tt(d); return (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.02 * t)) * env(len(t), 0.001, 0.06)
def bayan(d=0.45):
    t = tt(d); f = 95 + 60 * np.exp(-t / 0.05)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.002, 0.18)
def tik(): return band(noise(0.04), 2500, 8000) * env(int(0.04 * SR), 0.001, 0.012)
BOL = ["dha", "ge", "na", "ti", "na", "ka", "dhi", "na"]
def bol(b):
    if b == "dha": return np.pad(dayan(), (0, int(0.27 * SR))) + bayan()
    if b == "dhi": return np.pad(dayan(600), (0, int(0.27 * SR))) + 0.8 * bayan()
    if b == "ge": return bayan()
    if b == "na": return dayan(540)
    return np.pad(tik(), (0, 100))
festive = [(BOUNDS["title"], BOUNDS["palace"]), (BOUNDS["wedding"], BOUNDS["stars"] - 0.5), (BOUNDS["room2"], DURATION)]
t0 = 0.0; k = 0
while t0 < DURATION:
    if any(a <= t0 < b for a, b in festive):
        add(tabla, bol(BOL[k % 8]), t0, 0.5 if BOL[k % 8] in ("dha", "dhi", "ge") else 0.35)
    t0 += BEAT / 2; k += 1

# ---------------- voices
speech = np.zeros(N, bool)
for l in LINES:
    x, sr = sf.read(l["file"]); x = resample_poly(x, SR, sr)
    add(voice, x, l["start"]); speech[int(l["start"] * SR):int(l["end"] * SR)] = True

# ---------------- sound effects
def glock(f, d=1.2, dec=0.6):
    t = tt(d); return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / 0.1)) * env(len(t), 0.002, dec)
def shimmer(t, notes=(74, 78, 81, 86, 90, 93), step=0.07, g=0.2):
    for i, m in enumerate(notes): add(sfx, glock(hz(m)), t + i * step, g)
def gong(t, g=0.5):
    x = tt(4.0); y = sum(a * np.sin(2 * np.pi * f * x) * np.exp(-x / d) for f, a, d in ((98, 1, 2.5), (147.3, 0.6, 1.8), (231, 0.4, 1.2), (342, 0.25, 0.8)))
    add(sfx, y * np.minimum(1, x / 0.004), t, g)
def splash(t, d=0.8, g=0.35):
    x = band(noise(d), 600, 5000) * env(int(d * SR), 0.01, d / 3); add(sfx, x, t, g)
def bells(t, d=1.5, g=0.12):
    tt_ = t
    while tt_ < t + d:
        add(sfx, band(noise(0.08), 5000, 11000) * env(int(0.08 * SR), 0.001, 0.03), tt_, g); tt_ += rng.uniform(0.05, 0.12)
def rise(t, g=0.18):
    for i in range(10): add(sfx, glock(hz(74 + i * 2), 0.8, 0.4), t + i * 0.08, g)
def boom(t, g=0.6):
    x = tt(0.8); f = 70 + 40 * np.exp(-x / 0.05); add(sfx, np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(x), 0.002, 0.25), t, g)

gong(0.2); shimmer(1.0)
shimmer(S("icons") + 0.3, (79, 83, 86), 0.5, 0.15)
shimmer(S("book_open") + 1.0, (74, 79, 83, 86, 91), 0.06); splash(BOUNDS["palace"] - 0.3, 0.6, 0.08)
gong(BOUNDS["palace"] + 0.1, 0.25)
splash(BOUNDS["river"] + 0.2, 1.5, 0.08)
shimmer(S("glow") + 0.3); splash(S("ganga_rise"), 1.2, 0.3); shimmer(S("ganga_rise") + 0.4, (81, 86, 90, 93, 98), 0.09)
shimmer(S("promise") + 2.0, (74, 78, 81, 86), 0.12, 0.18)
bells(BOUNDS["wedding"] + 0.2, 2.5); shimmer(S("wedding") + 0.5)
shimmer(S("baby1") + 0.8, (86, 90, 93), 0.15, 0.15)
splash(S("river_baby") + 1.5, 0.8, 0.12); rise(STAR1_T)
for i, st in enumerate(SEVEN_TIMES): add(sfx, glock(hz(86 + [0, 2, 4, 5, 7, 9, 11][i]), 1.0, 0.5), st, 0.25)
shimmer(S("vasus") + 0.3, (74, 78, 81, 86, 90, 93, 98), 0.1, 0.18)
rise(S("free") + 1.0, 0.12)
boom(S("stop") + 0.05); splash(S("stop") + 0.3, 0.6, 0.2)
splash(S("ganga_leave") + 0.5, 2.5, 0.35); shimmer(S("ganga_leave") + 1.0, (98, 93, 90, 86, 81, 78, 74), 0.12, 0.18)
shimmer(BOUNDS["room2"] + 0.2, (74, 79, 83), 0.1, 0.15)
shimmer(T_OUTRO + 0.3); gong(T_OUTRO + 0.2, 0.25)

# ---------------- mix
k_ = int(0.15 * SR)
duck = np.convolve(np.where(speech, 0.3, 1.0), np.ones(k_) / k_, "same")
fl_duck = np.convolve(np.where(speech, 0.0, 1.0), np.ones(k_ * 3) / (k_ * 3), "same")
sad = np.ones(N)  # softer music during the sad part
a, b = int(BOUNDS["stars"] * SR), int(BOUNDS["room2"] * SR); sad[a:b] = 0.7
fade = np.ones(N); fl = int(3 * SR); fade[-fl:] = np.linspace(1, 0, fl); fade[:int(0.3 * SR)] = np.linspace(0, 1, int(0.3 * SR))
music = (drone * 0.9 + tabla * 0.8) * duck * sad + flute * fl_duck * 0.9 * sad
mix = voice * 1.0 + music * fade * 0.8 + sfx * 0.8
mix = np.tanh(mix * 1.1) * 0.89
sf.write("audio/mix.wav", np.stack([mix, mix], 1), SR, subtype="PCM_16")
print("ok", DURATION, float(np.abs(mix).max()))
