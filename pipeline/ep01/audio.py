import numpy as np, soundfile as sf
from scipy.signal import resample_poly, butter, sosfilt
from cues import *

SR = 48000
N = int(DURATION * SR)
rng = np.random.default_rng(7)
music = np.zeros(N); melody = np.zeros(N); sfx = np.zeros(N); voice = np.zeros(N)


def add(buf, x, t, g=1.0):
    i = int(t * SR)
    if i >= N: return
    x = x[: N - i]
    buf[i:i + len(x)] += g * x


def hz(note):  # midi -> hz
    return 440.0 * 2 ** ((note - 69) / 12)


def env(n, a=0.005, d=0.3):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / d)


_ks = {}
def pluck(note, dur=1.2):
    if note in _ks: return _ks[note]
    f = hz(note); p = int(SR / f); n = int(dur * SR)
    buf = rng.uniform(-1, 1, p); out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = 0.996 * 0.5 * (buf[i % p] + buf[(i + 1) % p])
    out *= np.exp(-np.arange(n) / SR / 0.5)
    _ks[note] = out
    return out


def glock(f, dur=1.0, d=0.45):
    t = np.arange(int(dur * SR)) / SR
    x = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / 0.08) + 0.15 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t / 0.04)
    return x * env(len(t), 0.002, d)


def noise(dur):
    return rng.uniform(-1, 1, int(dur * SR))


def band(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], btype="band", fs=SR, output="sos"), x)


def sweep(f0, f1, dur, vib=0.0, d=None, shape=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    f = f0 + (f1 - f0) * (t / dur) ** shape
    if vib: f = f * (1 + 0.06 * np.sin(2 * np.pi * vib * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    e = np.minimum(1, t / 0.01) * (np.exp(-t / d) if d else np.minimum(1, (dur - t) / 0.05))
    return np.sin(ph) * e


# ---------------- music bed: 112 bpm, C – G – Am – F ----------------
BPM = 112; B = 60 / BPM
CHORDS = [[60, 64, 67, 72], [59, 62, 67, 71], [57, 60, 64, 69], [57, 60, 65, 69]]
ROOTS = [36, 43, 45, 41]
STRUM = [0, 1, 1.5, 2.5, 3]  # island strum, beats in a bar
MEL = [  # (beat, midi, beats long) per 4-bar phrase
    (0, 76, 1), (1, 79, 1), (2, 81, .5), (2.5, 79, .5), (3, 76, 1),
    (4, 74, 1), (5, 79, 1), (6, 71, 2),
    (8, 72, 1), (9, 76, 1), (10, 81, .5), (10.5, 79, .5), (11, 76, 1),
    (12, 77, 1), (13, 76, .5), (13.5, 74, .5), (14, 72, 2),
]
t0 = 0.0
bar = 0
while t0 + bar * 4 * B < DURATION:
    tb = t0 + bar * 4 * B
    c = bar % 4
    for k, s in enumerate(STRUM):
        down = k != 2
        notes = CHORDS[c] if down else CHORDS[c][::-1]
        for j, nn in enumerate(notes):
            add(music, pluck(nn), tb + s * B + j * 0.012, 0.16 if down else 0.11)
    for s in (0, 2):  # bass
        bt = np.arange(int(B * 1.6 * SR)) / SR; f = hz(ROOTS[c])
        add(music, (np.sin(2 * np.pi * f * bt) + 0.3 * np.sin(4 * np.pi * f * bt)) * env(len(bt), 0.01, 0.35), tb + s * B, 0.5)
    for e8 in range(8):  # shaker
        add(music, band(noise(0.06), 5000, 11000) * env(int(0.06 * SR), 0.003, 0.02), tb + e8 * B / 2, 0.10 if e8 % 2 else 0.05)
    for s in (1, 3):  # soft clap
        add(music, band(noise(0.12), 900, 3500) * env(int(0.12 * SR), 0.002, 0.04), tb + s * B, 0.18)
    if bar % 4 == 0:
        for (bt_, nn, ln) in MEL:
            add(melody, glock(hz(nn), ln * B + 0.6, 0.35), tb + bt_ * B, 0.22)
    bar += 1

# ---------------- voices ----------------
speech = np.zeros(N, bool)
for l in LINES:
    x, sr = sf.read(l["file"])
    x = resample_poly(x, SR, sr)
    add(voice, x, l["start"])
    speech[int(l["start"] * SR):int(l["end"] * SR)] = True

# ---------------- sound effects ----------------
def boing(t, g=0.35): add(sfx, sweep(180, 620, 0.32, vib=18, shape=0.6), t, g)
def popf(t, f, g=0.4):
    add(sfx, sweep(1200, 380, 0.08, d=0.04), t, g); add(sfx, glock(f, 1.2, 0.6), t + 0.03, 0.3)
def thunk(t, g=0.6):
    tt = np.arange(int(0.18 * SR)) / SR
    add(sfx, (np.sin(2 * np.pi * 85 * tt) + 0.6 * band(noise(0.18), 150, 900)) * env(len(tt), 0.002, 0.05), t, g)
def swish(t, dur=0.45, g=0.25):
    x = noise(dur); n = len(x); out = np.zeros(n); w = 256
    for i in range(0, n, w):
        p = i / n; c = 800 + 4000 * np.sin(np.pi * p)
        out[i:i + w] = band(x[i:i + w + 512], c * 0.7, c * 1.3)[:len(out[i:i + w])]
    add(sfx, out * np.sin(np.pi * np.arange(n) / n), t, g)
def shimmer(t, notes=(72, 76, 79, 84, 88, 91), step=0.07, g=0.22):
    for i, nn in enumerate(notes): add(sfx, glock(hz(nn), 1.4, 0.7), t + i * step, g)
def water(t0, t1):
    add(sfx, band(noise(t1 - t0), 1500, 6000) * np.sin(np.pi * np.linspace(0, 1, int((t1 - t0) * SR))) ** 0.5, t0, 0.07)
    t = t0
    while t < t1:
        add(sfx, sweep(1400 + rng.uniform(0, 1400), 2600, 0.05, d=0.02), t, 0.12); t += rng.uniform(0.06, 0.16)

shimmer(0.25); popf(1.2, hz(84))
for t in starts("mia_jump"): boing(t + 0.1)
for i in range(3): boing(S("benny_in") + 0.2 + i * 0.5, 0.25)
for t in starts("benny_hop"): boing(t + 0.05, 0.3); boing(t + 0.5, 0.25)
swish(T_PAN0 + 0.3, 1.0, 0.18)
for t in DIG_HITS: thunk(t)
for t in BDIG_HITS: thunk(t, 0.4)
swish(S("seedbag"), 0.35)
for i, t in enumerate(SEED_TIMES): add(sfx, glock(hz([84, 86, 88, 89, 91][i]), 1.0, 0.4), t, 0.35)
swish(S("cover"), 0.6, 0.2)
swish(S("can_in"), 0.5)
water(S("water"), E("water") + 0.6)
shimmer(S("sun_shine") + 0.2, (79, 84, 88, 91, 96), 0.09)
boing(S("peek") + 0.1, 0.2)
for k in range(int((E("wait") - S("wait")) / 0.5)):  # tick-tock
    tt = np.arange(int(0.05 * SR)) / SR
    add(sfx, np.sin(2 * np.pi * (1800 if k % 2 else 1300) * tt) * env(len(tt), 0.001, 0.012), S("wait") + 0.2 + k * 0.5, 0.25)
shimmer(S("dance_start"), (72, 76, 79, 84), 0.08)
add(sfx, sweep(300, 1100, 1.0), S("stretch") + 0.1, 0.12)
add(sfx, sweep(330, 330, 1.2, vib=7), S("wiggle") + 0.05, 0.1)
for t in HOPHOP_TIMES: boing(t, 0.3)
for t in SPROUT_TIMES: add(sfx, sweep(500, 1500, 0.1, d=0.05), t, 0.25)
for i, t in enumerate(FLOWER_TIMES): popf(t, hz([72, 74, 76, 79, 81][i]))
shimmer(RAINBOW_T, (72, 74, 76, 77, 79, 81, 83, 84, 88), 0.06, 0.2)
for k in range(8): add(music, band(noise(0.12), 900, 3500) * env(int(0.12 * SR), 0.002, 0.04), S("sing") + k * B, 0.35)
for i in range(6): add(sfx, glock(hz(96 + (i * 3) % 7), 0.8, 0.3), S("butterfly") + 0.1 + i * 0.22, 0.12)
shimmer(S("hug2") + 0.1, (72, 76, 79), 0.25, 0.2)
shimmer(T_OUTRO + 0.3); boing(S("byebye"), 0.3)

# ---------------- mix ----------------
duck = np.where(speech, 0.32, 1.0)
k = int(0.12 * SR); duck = np.convolve(duck, np.ones(k) / k, "same")
mel_duck = np.convolve(np.where(speech, 0.0, 1.0), np.ones(k) / k, "same")
fade = np.ones(N); fl = int(2.5 * SR); fade[-fl:] = np.linspace(1, 0, fl)
fi = int(0.4 * SR); fade[:fi] *= np.linspace(0, 1, fi)
mix = voice * 1.0 + (music * 0.55 * duck + melody * 0.6 * mel_duck) * fade + sfx * 0.8
mix = np.tanh(mix * 1.1) * 0.89
stereo = np.stack([mix, mix], 1)
sf.write("audio/mix.wav", stereo, SR, subtype="PCM_16")
print("peak", float(np.abs(mix).max()), "dur", N / SR)
