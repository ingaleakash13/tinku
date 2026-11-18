"""Full band backing for the song: drums, bass, ukulele strums, piano doubling the tune, bells, SFX, vocals."""
import json, numpy as np, soundfile as sf
from scipy.signal import resample_poly, butter, sosfilt
from script import SECTIONS, LINES, B, BAR, T, SONG_END, CHORUS, COLORS

SR = 48000; DURATION = SONG_END + 0.5; N = int(DURATION * SR)
rng = np.random.default_rng(7)
drums = np.zeros(N); bass = np.zeros(N); uke = np.zeros(N); keys = np.zeros(N); sfx = np.zeros(N)

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
def pluck(m, dur=1.0):
    if m in _ks: return _ks[m]
    f = hz(m); p = int(SR / f); n = int(dur * SR); buf = rng.uniform(-1, 1, p); out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % p]; buf[i % p] = 0.996 * 0.5 * (buf[i % p] + buf[(i + 1) % p])
    out *= np.exp(-np.arange(n) / SR / 0.45); _ks[m] = out; return out
def glock(f, dur=1.0, d=0.45):
    t = np.arange(int(dur * SR)) / SR
    return (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / 0.08)) * env(len(t), 0.002, d)
def piano(m, dur):
    f = hz(m); t = np.arange(int((dur + 0.3) * SR)) / SR
    x = sum(a * np.sin(2 * np.pi * f * h * t) * np.exp(-t * (1.6 + h * 0.9)) for h, a in ((1, 1), (2, 0.45), (3, 0.22), (4, 0.12)))
    e = np.minimum(1, t / 0.004) * np.where(t < dur, 1.0, np.exp(-(t - dur) / 0.08)); return x * e
def sweep(f0, f1, dur, vib=0.0, d=None, shape=1.0):
    n = int(dur * SR); t = np.arange(n) / SR; f = f0 + (f1 - f0) * (t / dur) ** shape
    if vib: f = f * (1 + 0.06 * np.sin(2 * np.pi * vib * t))
    e = np.minimum(1, t / 0.01) * (np.exp(-t / d) if d else np.minimum(1, (dur - t) / 0.05))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * e

KICK = (lambda t: np.sin(2 * np.pi * np.cumsum(50 + 110 * np.exp(-t / 0.03)) / SR) * np.exp(-t / 0.18))(np.arange(int(0.4 * SR)) / SR)
SNARE = band(noise(0.25), 1200, 7000) * env(int(0.25 * SR), 0.001, 0.07) + 0.5 * np.sin(2 * np.pi * 190 * np.arange(int(0.25 * SR)) / SR) * env(int(0.25 * SR), 0.001, 0.05)
CLAP = sum(np.pad(band(noise(0.12), 900, 4000) * env(int(0.12 * SR), 0.001, 0.03), (int(k * 0.011 * SR), int((2 - k) * 0.011 * SR))) for k in range(3))
HAT = band(noise(0.06), 6000, 14000) * env(int(0.06 * SR), 0.001, 0.018)
OHAT = band(noise(0.3), 5000, 13000) * env(int(0.3 * SR), 0.001, 0.12)
CRASH = band(noise(1.6), 3000, 14000) * env(int(1.6 * SR), 0.001, 0.6)
def tom(f): t = np.arange(int(0.3 * SR)) / SR; return np.sin(2 * np.pi * np.cumsum(f * (1 + 0.6 * np.exp(-t / 0.03))) / SR) * np.exp(-t / 0.12)

CH = {"C": [60, 64, 67], "G": [59, 62, 67], "Am": [57, 60, 64], "F": [57, 60, 65], "Dm": [57, 62, 65], "Em": [59, 64, 67]}
ROOT = {"C": 36, "G": 43, "Am": 45, "F": 41, "Dm": 38, "Em": 40}

for sb, nb, kind, scene, chords, info in SECTIONS:
    for b in range(nb):
        tb = T((sb + b) * BAR); parts = chords[b % len(chords)].split()
        last = b == nb - 1
        for half in range(4):                                  # per beat
            ch = parts[0] if len(parts) == 1 or half < 2 else parts[1]
            tt = tb + half * B
            # ukulele strum: D . D U . U D U
            if kind != "card" or b == 0:
                for s, g in ((0, 1.0), (0.5, 0.55)) if half % 2 == 0 else ((0, 0.7), (0.5, 0.6)):
                    notes = CH[ch] + [CH[ch][0] + 12]
                    if s: notes = notes[::-1]
                    for j, m in enumerate(notes): add(uke, pluck(m + 12), tt + s * B + j * 0.011, 0.13 * g)
            # bass: root on beat, octave on the "and" in chorus
            if kind in ("chorus", "verse", "outro") or (kind == "intro" and b >= 2):
                bm = ROOT[ch]; f = hz(bm); bt = np.arange(int(B * 0.9 * SR)) / SR
                tone = np.sin(2 * np.pi * f * bt) + 0.3 * np.sin(4 * np.pi * f * bt)
                add(bass, tone * env(len(bt), 0.008, 0.35), tt, 0.5)
                if kind == "chorus" and half % 2 == 1: add(bass, np.sin(2 * np.pi * 2 * f * bt[: len(bt) // 2]) * env(len(bt) // 2, 0.005, 0.12), tt + 0.5 * B, 0.25)
            # drums
            if kind == "card" and b > 0: continue
            if kind == "intro" and b < 2:
                if half in (1, 3): add(drums, CLAP, tt, 0.35)
                continue
            if half in (0, 2): add(drums, KICK, tt, 0.9)
            if kind == "chorus" and half == 1: add(drums, KICK, tt + 0.5 * B, 0.6)
            if half in (1, 3): add(drums, SNARE, tt, 0.4); add(drums, CLAP, tt, 0.3 if kind == "chorus" else 0.18)
            for e8 in range(2): add(drums, HAT, tt + e8 * B / 2, 0.16 if e8 else 0.11)
            if kind == "chorus" and half == 3: add(drums, OHAT, tt + 0.5 * B, 0.12)
        if b == 0 and kind in ("chorus", "verse", "outro"): add(drums, CRASH, tb, 0.22)
        if last and kind in ("intro", "chorus", "verse"):      # tom fill into the next section
            for k, f in enumerate((220, 196, 165, 140)): add(drums, tom(f), tb + 3 * B + k * B / 4, 0.4)

# piano doubles the sung tune (and plays the chorus hook in the intro)
for l in LINES:
    beat = l["beat"]
    for w, notes in l["notes"]:
        for m, d in notes:
            if m: add(keys, piano(m, d * B * 0.9), T(beat), 0.16 if l["spk"] == "all" else 0.12)
            beat += d
for i, notes in enumerate(CHORUS[:2]):
    beat = (0 + 2 * i) * BAR
    for w, nn in notes:
        for m, d in nn:
            if m: add(keys, glock(hz(m + 12), d * B + 0.6, 0.4), T(beat), 0.32)
            beat += d

# SFX: shimmer + pop on every colour word, Moti barks in each verse's fill bar, fun extras
def pop(t, f, g=0.3): add(sfx, sweep(1200, 380, 0.08, d=0.04), t, g); add(sfx, glock(f, 1.0, 0.5), t + 0.02, 0.2)
def shimmer(t, notes=(84, 88, 91, 96), step=0.05, g=0.14):
    for i, m in enumerate(notes): add(sfx, glock(hz(m), 1.3, 0.6), t + i * step, g)
def bark(t, g=0.5):
    tt = np.arange(int(0.22 * SR)) / SR; f = 520 * np.exp(-tt / 0.12) + 300; ph = 2 * np.pi * np.cumsum(f) / SR
    x = (np.sign(np.sin(ph)) * 0.3 + np.sin(ph) * 0.7 + 0.25 * rng.uniform(-1, 1, len(tt))) * np.minimum(1, tt / 0.01) * np.exp(-tt / 0.07)
    add(sfx, lp(x, 3000), t, g)
def quack(t): x = sweep(700, 500, 0.16, vib=30, d=0.08); add(sfx, np.sign(x) * 0.4 + x * 0.6, t, 0.18)
def honk(t):
    for f in (660, 880): add(sfx, sweep(f, f, 0.14, d=0.1), t, 0.1)
for sb, nb, kind, scene, chords, info in SECTIONS:
    if kind == "verse":
        for k in range(3): bark(T((sb + 5) * BAR + k) + 0.02)
        shimmer(T(sb * BAR))
for l in LINES:
    if l["cue"].endswith("_echo"):
        for k in range(3): pop(T(l["beat"] + k), hz(84 + [0, 4, 7][k]))
    if l["cue"].startswith("ch"):
        shimmer(T(l["beat"]), (79, 84, 88, 91), 0.04, 0.08)
    if l["cue"] == "red_b": honk(T(l["beat"] + 2.5)); honk(T(l["beat"] + 3.0))
    if l["cue"] == "yellow_b":
        for k in range(4): quack(T(l["beat"] + 3.0 + 0.5 * k) + 0.15)
shimmer(0.1, (72, 76, 79, 84, 88, 91, 96), 0.06, 0.2)

# vocals
vox = np.zeros(N)
for s in ("tinku", "pinky", "golu"):
    x, sr = sf.read(f"audio/lines/vox_{s}.wav"); x = resample_poly(x, SR, sr)[:N]; vox[:len(x)] += x
music = drums * 0.8 + bass * 0.75 + uke * 0.75 + keys * 0.9
fade = np.ones(N); fl = int(2.0 * SR); fade[-fl:] = np.linspace(1, 0, fl)
mix = (vox * 1.0 + music * 0.6 + sfx * 0.8) * fade
mix = np.tanh(mix * 1.2) * 0.9
sf.write("audio/mix.wav", np.stack([mix, mix * 0.98 + 0.02 * np.roll(mix, 300)], 1), SR, subtype="PCM_16")
print("ok", round(DURATION, 2), "peak", np.abs(mix).max().round(3))
