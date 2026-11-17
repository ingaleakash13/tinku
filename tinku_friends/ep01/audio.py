import numpy as np, soundfile as sf
from scipy.signal import resample_poly, butter, sosfilt
from cues import *

SR = 48000; N = int(DURATION * SR)
rng = np.random.default_rng(7)
music = np.zeros(N); melody = np.zeros(N); sfx = np.zeros(N); voice = np.zeros(N)

def add(buf, x, t, g=1.0):
    i = int(t * SR)
    if i >= N: return
    x = x[: N - i]; buf[i:i + len(x)] += g * x
def hz(m): return 440.0 * 2 ** ((m - 69) / 12)
def env(n, a=0.005, d=0.3):
    t = np.arange(n) / SR; return np.minimum(1, t / a) * np.exp(-t / d)
def noise(d): return rng.uniform(-1, 1, int(d * SR))
def band(x, lo, hi): return sosfilt(butter(2, [lo, hi], btype="band", fs=SR, output="sos"), x)
_ks = {}
def pluck(m, dur=1.0):
    if m in _ks: return _ks[m]
    f = hz(m); p = int(SR / f); n = int(dur * SR); buf = rng.uniform(-1, 1, p); out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % p]; buf[i % p] = 0.996 * 0.5 * (buf[i % p] + buf[(i + 1) % p])
    out *= np.exp(-np.arange(n) / SR / 0.45); _ks[m] = out; return out
def glock(f, dur=1.0, d=0.45):
    t = np.arange(int(dur * SR)) / SR
    return (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / 0.08)) * env(len(t), 0.002, d)
def sweep(f0, f1, dur, vib=0.0, d=None, shape=1.0):
    n = int(dur * SR); t = np.arange(n) / SR; f = f0 + (f1 - f0) * (t / dur) ** shape
    if vib: f = f * (1 + 0.06 * np.sin(2 * np.pi * vib * t))
    e = np.minimum(1, t / 0.01) * (np.exp(-t / d) if d else np.minimum(1, (dur - t) / 0.05))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * e

# bouncy ukulele bed, 118 bpm, C F G C / Am F G C
B = 60 / 118
CH = [[60, 64, 67, 72], [60, 65, 69, 72], [59, 62, 67, 71], [60, 64, 67, 72], [57, 60, 64, 69], [57, 60, 65, 69], [59, 62, 67, 71], [60, 64, 67, 72]]
RT = [36, 41, 43, 36, 45, 41, 43, 36]
MEL = [(0, 72, 1), (1, 76, 1), (2, 79, 1), (3, 76, 1), (4, 77, 1), (5, 81, 1), (6, 79, 2), (8, 76, 1), (9, 74, 1), (10, 72, 2)]
bar = 0
while bar * 4 * B < DURATION:
    tb = bar * 4 * B; c_ = bar % 8
    for k, s in enumerate((0, 1, 1.5, 2.5, 3)):
        for j, m in enumerate(CH[c_] if k != 2 else CH[c_][::-1]): add(music, pluck(m), tb + s * B + j * 0.012, 0.15)
    for s in (0, 2):
        bt = np.arange(int(B * 1.5 * SR)) / SR; f = hz(RT[c_]); add(music, np.sin(2 * np.pi * f * bt) * env(len(bt), 0.01, 0.3), tb + s * B, 0.5)
    for e8 in range(8): add(music, band(noise(0.05), 5000, 11000) * env(int(0.05 * SR), 0.002, 0.02), tb + e8 * B / 2, 0.09 if e8 % 2 else 0.05)
    for s in (1, 3): add(music, band(noise(0.1), 900, 3500) * env(int(0.1 * SR), 0.002, 0.04), tb + s * B, 0.16)
    if bar % 4 == 0:
        for bt_, m, ln in MEL: add(melody, glock(hz(m), ln * B + 0.5, 0.35), tb + bt_ * B, 0.2)
    bar += 1

speech = np.zeros(N, bool)
for l in LINES:
    x, sr = sf.read(l["file"]); x = resample_poly(x, SR, sr); add(voice, x, l["start"])
    speech[int(l["start"] * SR):int(l["end"] * SR)] = True

def boing(t, g=0.3): add(sfx, sweep(180, 620, 0.3, vib=18, shape=0.6), t, g)
def pop(t, f, g=0.35): add(sfx, sweep(1200, 380, 0.08, d=0.04), t, g); add(sfx, glock(f, 1.0, 0.5), t + 0.02, 0.25)
def shimmer(t, notes=(72, 76, 79, 84, 88, 91), step=0.07, g=0.2):
    for i, m in enumerate(notes): add(sfx, glock(hz(m), 1.3, 0.6), t + i * step, g)
def cheer(t, g=0.18):
    for k in range(30): add(sfx, band(noise(0.06), 1500, 6000) * env(int(0.06 * SR), 0.001, 0.02), t + rng.uniform(0, 1.2), g)

shimmer(0.3)
shimmer(T_COUNT + 0.2, (72, 79, 84), 0.08)
SCALE = [72, 74, 76, 77, 79, 81, 83, 84, 86, 88]
for n in range(1, 11):
    for k, tp in enumerate(POP[n]): pop(tp, hz(SCALE[k]))
    shimmer(S(f"e{n}") + 0.05, (84, 88, 91), 0.05, 0.12)
for k, tp in enumerate(FAST): pop(tp, hz(SCALE[k]), 0.3)
cheer(S("moti_cheer")); shimmer(S("moti_cheer"), (72, 76, 79, 84, 88, 91, 96), 0.06)
shimmer(S("next") + 0.3, (72, 74, 76, 77, 79, 81, 83, 84), 0.07, 0.16)
shimmer(T_OUTRO + 0.3); boing(S("bye2"))

k_ = int(0.12 * SR)
duck = np.convolve(np.where(speech, 0.3, 1.0), np.ones(k_) / k_, "same")
mduck = np.convolve(np.where(speech, 0.0, 1.0), np.ones(k_) / k_, "same")
fade = np.ones(N); fl = int(2.5 * SR); fade[-fl:] = np.linspace(1, 0, fl)
mix = voice + (music * 0.55 * duck + melody * 0.55 * mduck) * fade + sfx * 0.8
mix = np.tanh(mix * 1.1) * 0.89
sf.write("audio/mix.wav", np.stack([mix, mix], 1), SR, subtype="PCM_16"); print("ok", DURATION)
