"""Mood music + SFX for the narrated Nani story: journey ukulele -> spooky night -> sad minor morning -> detective tune -> spooky trap -> chase -> fair."""
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
MIN = [[57, 60, 64, 69], [53, 57, 60, 65], [55, 59, 62, 67], [57, 60, 64, 69]]; MROOT = [45, 41, 43, 45]
ukulele(play, 0.0, T_NIGHT + 1.0, MAJ, ROOT, bpm=104)                 # journey + village evening
ukulele(play, T_MORNING + 0.5, T_CLUES + 0.5, MIN, MROOT, bpm=80, g=0.7)  # sad morning
ukulele(play, T_CLUES + 0.5, T_TRAP + 0.5, MAJ, ROOT, bpm=112, g=0.8)  # detectives
ukulele(play, T_TORCH + 0.3, T_MELA, MAJ, ROOT, bpm=132)              # chase!
ukulele(play, T_MELA, DURATION, MAJ, ROOT, bpm=120, g=1.1)            # fair

def spooky(t0, t1, hb_from=None):
    ts = np.arange(int((t1 - t0 + 1.5) * SR)) / SR
    drone = sum(np.sin(2 * np.pi * f * ts + rng.uniform(0, 6)) for f in (55.0, 55.4, 82.4, 82.0)) / 4
    add(spook, lp(drone * (0.6 + 0.4 * np.sin(2 * np.pi * 0.15 * ts)), 400), t0 - 0.5, 0.5)
    t = t0 + 0.5; k = 0
    while t < t1 - 0.3:
        add(spook, pluck([57, 60, 64, 63, 57, 60, 65, 64][k % 8], 1.0, 0.18), t, 0.2); t += 60 / 72; k += 1
    if hb_from:
        hb = np.sin(2 * np.pi * 55 * np.arange(int(0.18 * SR)) / SR) * env(int(0.18 * SR), 0.004, 0.06); t = hb_from
        while t < t1 - 0.4: add(spook, hb, t, 0.6); add(spook, hb, t + 0.22, 0.4); t += 0.95
spooky(T_NIGHT, T_RUN + 1.5, hb_from=T_STAIRS)
spooky(T_TRAP, T_TORCH, hb_from=S("n_bells"))

def boing(t, g=0.3): add(sfx, sweep(180, 620, 0.3, vib=18, shape=0.6), t, g)
def shimmer(t, notes=(72, 76, 79, 84, 88, 91), step=0.07, g=0.2):
    for i, m in enumerate(notes): add(sfx, glock(hz(m), 1.3, 0.6), t + i * step, g)
def whoosh(t, g=0.35):
    n = int(0.6 * SR); x = noise(0.6); tt = np.arange(n) / SR
    y = sosfilt(butter(2, [600, 3000], btype="band", fs=SR, output="sos"), x) * np.sin(np.pi * tt / 0.6) ** 2; add(sfx, y, t, g)
def sting(t):
    for m in (45, 46, 51, 52, 57):
        n = int(1.4 * SR); tt = np.arange(n) / SR
        add(sfx, np.sign(np.sin(2 * np.pi * hz(m) * tt)) * 0.3 * env(n, 0.003, 0.5), t, 0.16)
    add(sfx, band(noise(0.8), 3000, 12000) * np.linspace(0, 1, int(0.8 * SR)) ** 2, t - 0.8, 0.25)
def click(t): add(sfx, band(noise(0.03), 2000, 8000) * env(int(0.03 * SR), 0.001, 0.008), t, 0.6)
def jingle(t, g=0.18):
    for k in range(4): add(sfx, glock(hz(96 + rng.integers(-2, 3)) * rng.uniform(0.98, 1.02), 0.4, 0.12), t + k * 0.03 + rng.uniform(0, 0.02), g)
def chham_steps(t0, t1, gap=0.55, g=0.18):
    t = t0
    while t < t1: jingle(t, g); t += gap * rng.uniform(0.85, 1.15)
def crickets(t0, t1):
    t = t0
    while t < t1:
        n = int(0.05 * SR); tt = np.arange(n) / SR
        for k in range(3): add(sfx, np.sin(2 * np.pi * 4300 * tt) * env(n, 0.002, 0.012), t + k * 0.06, 0.03)
        t += rng.uniform(0.5, 1.1)
def hoot(t):
    for k, dt in enumerate((0, 0.55)):
        n = int(0.42 * SR); tt = np.arange(n) / SR; f = 380 * (1 + 0.04 * np.sin(2 * np.pi * 6 * tt)) * (1 - 0.08 * tt)
        add(sfx, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / 0.42) ** 1.5, t + dt, 0.3)
def step(t): add(sfx, lp(noise(0.08), 600) * env(int(0.08 * SR), 0.002, 0.03), t, 0.35)
def thud(t): add(sfx, lp(noise(0.4), 300) * env(int(0.4 * SR), 0.003, 0.12), t, 0.9)
def rooster(t):
    tt = t
    for f0, f1, d in ((600, 900, 0.25), (900, 820, 0.2), (820, 1050, 0.5)):
        add(sfx, sweep(f0, f1, d, vib=12) * 0.6 + 0.3 * sweep(f0 * 2, f1 * 2, d, vib=12), tt, 0.18); tt += d
def ding(t): add(sfx, glock(hz(88), 1.2, 0.5), t, 0.3); add(sfx, glock(hz(88), 1.2, 0.5), t + 0.35, 0.25)
def birdsong(t0, t1):
    t = t0
    while t < t1: add(sfx, sweep(2400, 3200, 0.12, d=0.08), t, 0.05); add(sfx, sweep(3000, 2600, 0.1, d=0.06), t + 0.15, 0.04); t += rng.uniform(1.2, 2.5)
def crowd_cheer(t0, t1):
    n = int((t1 - t0) * SR); x = band(noise(t1 - t0), 300, 3000) * 0.5
    add(sfx, x * np.minimum(1, np.arange(n) / SR / 1.0) * np.minimum(1, (n - np.arange(n)) / SR / 1.5), t0, 0.12)

birdsong(0.5, T_COURT); for_steps = [step(0.3 + k * 0.45) for k in range(int(T_COURT / 0.45))]
jingle(S("payal") + 0.3); jingle(S("dance1") + 0.2); jingle(S("dance1") + 0.7); jingle(S("dance1") + 1.2)
crickets(T_NIGHT, T_MORNING); hoot(T_NIGHT + 1.0)
chham_steps(T_CHHAM, S("torch1") + 2.0, 0.6, 0.14)
for k in range(10): step(T_STAIRS + 0.8 + k * 0.7)
sting(S("n_shadow") + 1.0)
for k in range(10): step(T_RUN + k * 0.12)
rooster(T_MORNING + 0.6); birdsong(T_MORNING, T_TRAP)
crickets(T_TRAP, T_MELA); chham_steps(S("n_bells") + 1.0, T_BELLS, 0.55, 0.16)
for k in range(6): jingle(T_BELLS + k * 0.15, 0.3)
click(T_TORCH - 0.05); whoosh(T_TORCH); boing(S("itschameli") - 0.1); shimmer(T_TORCH + 0.5)
chham_steps(T_CHASE, T_SLIP, 0.22, 0.2)
whoosh(T_SLIP, 0.4); thud(T_SLIP + 0.8); whoosh(T_FLY, 0.3); shimmer(T_CATCH, g=0.25)
crowd_cheer(T_MELA, T_OUTRO); chham_steps(S("n_dance"), T_OUTRO - 1, 0.3, 0.16)
ding(T_BELL); ding(S("bleat3") + 0.6); ding(S("superhit") + 0.4)
shimmer(T_OUTRO + 0.2); boing(S("bye2"))

speech = np.zeros(N, bool)
for l in LINES:
    x, sr = sf.read(l["file"]); x = resample_poly(x, SR, sr); add(voice, x, l["start"])
    speech[int(l["start"] * SR):int(l["end"] * SR)] = True

k_ = int(0.12 * SR)
duck = np.convolve(np.where(speech, 0.32, 1.0), np.ones(k_) / k_, "same")
xf = np.ones(N); tt = np.arange(N) / SR
pl = np.ones(N)
fade = np.ones(N); fl = int(2.5 * SR); fade[-fl:] = np.linspace(1, 0, fl)
mix = voice + (play * 0.55 * np.clip(pl, 0, 1) + spook * 0.7) * duck * fade + sfx * 0.8
mix = np.tanh(mix * 1.1) * 0.9
sf.write("audio/mix.wav", np.stack([mix, mix], 1), SR, subtype="PCM_16"); print("ok", DURATION)
