"""Spoken voices for a Tinku & Friends story -> audio/lines/NN.wav + timeline.json.
Each kid's pitch is auto-matched to their F0 target; lines in one breath, inner pauses tightened."""
import sys, os, json, numpy as np, soundfile as sf, pyworld as pw
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "mahabharat", "lib"))
from voices import FRIENDS_VOICES
from kokoro_onnx import Kokoro
from script import LINES, LANG

SR = 24000
k = Kokoro("tts/kokoro-v1.0.onnx", "tts/voices-v1.0.bin")
os.makedirs("audio/lines", exist_ok=True)
TARGET_F0 = {"tinku": 285, "pinky": 310, "golu": 350, "nani": 215}
KLANG = "hi" if LANG == "hi" else "en-us"
rng = np.random.default_rng(3)

def voice_style(v):
    if "+" not in v and "*" not in v: return v
    out = None
    for part in v.split("+"):
        name, w = part.split("*"); st = k.get_voice_style(name) * float(w)
        out = st if out is None else out + st
    return out.astype(np.float32)

def trim(x, thr=0.01):
    idx = np.where(np.abs(x) > thr)[0]
    return x if len(idx) == 0 else x[max(0, idx[0] - int(0.02 * SR)): idx[-1] + int(0.07 * SR)]

def tighten(x, max_gap=0.14, thr=0.012):
    hop = int(0.01 * SR); e = np.array([np.abs(x[i:i + hop]).max() for i in range(0, len(x) - hop, hop)])
    out = []; i = 0; n = len(e)
    while i < n:
        if e[i] < thr:
            j = i
            while j < n and e[j] < thr: j += 1
            keep = min(j - i, int(max_gap / 0.01)); out.append(x[i * hop:i * hop + keep * hop]); i = j
        else: out.append(x[i * hop:(i + 1) * hop]); i += 1
    out.append(x[n * hop:]); return np.concatenate(out)

def f0_of(x):
    f0, _ = pw.harvest(x.astype(np.float64), SR, f0_floor=60, f0_ceil=800, frame_period=5.0); v = f0[f0 > 0]
    return float(np.median(v)) if len(v) else 200.0

def reshape(x, f0k, fk):
    xd = x.astype(np.float64)
    f0, tm = pw.harvest(xd, SR, f0_floor=60, f0_ceil=800, frame_period=5.0)
    sp = pw.cheaptrick(xd, f0, tm, SR); ap = pw.d4c(xd, f0, tm, SR)
    nb = sp.shape[1]; src = np.clip(np.arange(nb) / fk, 0, nb - 1)
    sp2 = np.stack([np.interp(src, np.arange(nb), row) for row in sp])
    return pw.synthesize(f0 * f0k, sp2, ap, SR, frame_period=5.0).astype(np.float32)

def raw(spk, text):
    voice, speed, _, _ = FRIENDS_VOICES[f"{spk}_{'hi' if LANG == 'hi' else 'en'}"]
    x, _ = k.create(text, voice=voice_style(voice), speed=speed, lang=KLANG)
    return tighten(trim(x))

def bark(n):
    out = []
    for _ in range(n):
        tt = np.arange(int(0.22 * SR)) / SR; f = 520 * np.exp(-tt / 0.12) + 300; ph = 2 * np.pi * np.cumsum(f) / SR
        x = (np.sign(np.sin(ph)) * 0.3 + np.sin(ph) * 0.7 + 0.25 * rng.uniform(-1, 1, len(tt))) * np.minimum(1, tt / 0.01) * np.exp(-tt / 0.07)
        out += [x.astype(np.float32), np.zeros(int(0.16 * SR), np.float32)]
    return np.concatenate(out[:-1])

def meow(n, spooky=False):
    out = []
    for _ in range(n):
        d = 1.3 if spooky else 0.5; tt = np.arange(int(d * SR)) / SR
        f = (520 if spooky else 700) + (260 if spooky else 380) * np.sin(np.pi * tt / d) ** 1.5
        if spooky: f = f * (1 + 0.03 * np.sin(2 * np.pi * 5 * tt)) * 0.55
        ph = 2 * np.pi * np.cumsum(f) / SR
        x = sum(np.sin(k * ph) / k ** 1.3 for k in range(1, 7)) * np.sin(np.pi * tt / d) ** 0.6
        if spooky:   # echoey, ghostly
            e = np.zeros(len(x) + int(0.9 * SR)); e[:len(x)] += x
            for k, g in ((0.18, 0.5), (0.36, 0.3), (0.54, 0.18)): i = int(k * SR); e[i:i + len(x)] += g * x
            x = e
        out += [x.astype(np.float32), np.zeros(int(0.12 * SR), np.float32)]
    return np.concatenate(out[:-1])

def bleat(n):
    out = []
    for _ in range(n):
        d = 0.55; tt = np.arange(int(d * SR)) / SR
        f = 330 * (1 + 0.08 * np.sign(np.sin(2 * np.pi * 22 * tt)) * np.minimum(1, tt / 0.1)) * (1 - 0.1 * tt / d)
        ph = 2 * np.pi * np.cumsum(f) / SR
        x = sum(np.sin(k * ph) * (1.0 if k in (2, 3) else 0.5) / k for k in range(1, 9)) * np.sin(np.pi * tt / d) ** 0.5
        x = x + 0.08 * rng.uniform(-1, 1, len(tt)) * np.sin(np.pi * tt / d)
        out += [x.astype(np.float32), np.zeros(int(0.1 * SR), np.float32)]
    return np.concatenate(out[:-1])

# pitch factor per kid, measured on all their lines together
by_spk = {}
for scene, spk, hi, en, pause, cue in LINES:
    if spk not in ("moti", "barfi", "chameli"): by_spk.setdefault(spk, []).append(raw(spk, hi))
F0K = {s: TARGET_F0[s] / f0_of(np.concatenate(v)) for s, v in by_spk.items()}
print("F0 factors", {s: round(v, 2) for s, v in F0K.items()})

t = 0.0; tl = []; done = {s: 0 for s in by_spk}
for i, (scene, spk, hi, en, pause, cue) in enumerate(LINES):
    if spk == "moti": x = bark(en.count("Woof"))
    elif spk == "chameli": x = bleat(max(1, en.count("Meh")))
    elif spk == "barfi": x = meow(max(1, en.lower().count("meow") + en.count("Meeee")) if "Meeee" not in en else 1, spooky="Meeee" in en)
    else:
        _, _, _, fk = FRIENDS_VOICES[f"{spk}_{'hi' if LANG == 'hi' else 'en'}"]
        x = reshape(by_spk[spk][done[spk]], F0K[spk], fk); done[spk] += 1
    x = x / (np.abs(x).max() + 1e-9) * 0.9
    fn = f"audio/lines/{i:02d}.wav"; sf.write(fn, x, SR)
    t += pause; d = len(x) / SR
    tl.append(dict(i=i, scene=scene, speaker=spk, text=hi, en=en, cue=cue, start=round(t, 3), end=round(t + d, 3), file=fn))
    t += d
    print(f"{i:02d} {spk:6s} {t - d:6.2f}-{t:6.2f} {en}", flush=True)
for s in by_spk:
    xs = np.concatenate([sf.read(l["file"])[0] for l in tl if l["speaker"] == s]); print(s, "median F0", round(f0_of(xs), 1))
json.dump(dict(lines=tl, speech_end=t), open("timeline.json", "w"), indent=1, ensure_ascii=False)
print("speech ends", round(t, 2))
