"""Mood music + SFX: cosy ukulele (foggy walk) -> spooky drone, pizzicato, wind, heartbeat (giant shadow) -> happy ukulele (reveal/home)."""
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
ukulele(play, 0.0, T_GHOST + 1.0, MAJ, ROOT, bpm=108)          # cosy winter walk
ukulele(play, T_REVEAL + 0.8, DURATION, MAJ, ROOT, bpm=122)     # happy after the reveal

# spooky bed: low detuned drone, slow minor pizzicato, cold wind, heartbeat while hiding
ts = np.arange(int((T_REVEAL - T_GHOST + 1.5) * SR)) / SR
drone = sum(np.sin(2 * np.pi * f * ts + rng.uniform(0, 6)) for f in (55.0, 55.4, 82.4, 82.0)) / 4
drone = lp(drone * (0.6 + 0.4 * np.sin(2 * np.pi * 0.15 * ts)), 400)
add(spook, drone, T_GHOST - 0.5, 0.5)
B2 = 60 / 72; t = T_GHOST + 0.5
for k in range(200):
    if t > T_REVEAL - 0.3: break
    m = [57, 60, 64, 63, 57, 60, 65, 64][k % 8]
    add(spook, pluck(m, 1.0, 0.18), t, 0.22); t += B2
hb = np.sin(2 * np.pi * 55 * np.arange(int(0.18 * SR)) / SR) * env(int(0.18 * SR), 0.004, 0.06)
t = T_HIDE
while t < S("torch"):
    add(spook, hb, t, 0.6); add(spook, hb, t + 0.22, 0.4); t += 0.95
# winter wind under the whole story (louder in the fog)
wl = lp(noise(DURATION), 700); tt_ = np.arange(len(wl)) / SR
wl *= 0.35 + 0.65 * np.abs(np.sin(2 * np.pi * 0.07 * tt_)); wl *= np.where((tt_ > T_GHOST) & (tt_ < T_REVEAL), 1.0, 0.45)
add(sfx, wl, 0.0, 0.12)

# SFX
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
def step(t): add(sfx, lp(noise(0.08), 600) * env(int(0.08 * SR), 0.002, 0.03), t, 0.35)
def poof(t):
    n = int(0.9 * SR); tt = np.arange(n) / SR; add(sfx, lp(noise(0.9), 2500) * np.exp(-tt / 0.25) * np.minimum(1, tt / 0.02), t, 0.5)
def shake_rattle(t, d=1.2):
    for k in range(int(d * 16)): add(sfx, band(noise(0.04), 2500, 7000) * env(int(0.04 * SR), 0.002, 0.015), t + k / 16, 0.16)

for k in range(16): step(0.2 + k * 0.38)
sting(S("ghost") - 0.25)
click(S("torch") + 0.55)
whoosh(T_REVEAL + 0.35); boing(S("kitten") - 0.1); shimmer(T_REVEAL + 0.9)
for k in range(10): step(T_HOME + k * 0.32)
shake_rattle(T_SHAKE, 1.0); poof(T_SHAKE + 0.4); boing(S("snowy"), 0.35)
shimmer(T_OUTRO + 0.2); boing(S("bye2"))

speech = np.zeros(N, bool)
for l in LINES:
    x, sr = sf.read(l["file"]); x = resample_poly(x, SR, sr); add(voice, x, l["start"])
    speech[int(l["start"] * SR):int(l["end"] * SR)] = True

k_ = int(0.12 * SR)
duck = np.convolve(np.where(speech, 0.32, 1.0), np.ones(k_) / k_, "same")
xf = np.ones(N); tt = np.arange(N) / SR
pl = np.clip(1 - (tt - T_GHOST) / 1.2, 0, 1) + np.clip((tt - T_REVEAL - 0.6) / 1.0, 0, 1)
fade = np.ones(N); fl = int(2.5 * SR); fade[-fl:] = np.linspace(1, 0, fl)
mix = voice + (play * 0.55 * np.clip(pl, 0, 1) + spook * 0.7) * duck * fade + sfx * 0.8
mix = np.tanh(mix * 1.1) * 0.9
sf.write("audio/mix.wav", np.stack([mix, mix], 1), SR, subtype="PCM_16"); print("ok", DURATION)
