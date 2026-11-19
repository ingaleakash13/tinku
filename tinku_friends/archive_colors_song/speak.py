"""Spoken voices (owner: 'keep voice normal, not song'). Each lyric line is SPOKEN naturally by its kid, starting on the
line's beat, over the music. Writes the same outputs as sing.py (audio/lines/vox_<kid>.wav + timeline.json) plus
estimated word times, so draw.py pops things exactly when each word is said."""
import sys, os, json, re, numpy as np, soundfile as sf, pyworld as pw
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "mahabharat", "lib"))
from voices import FRIENDS_VOICES
from kokoro_onnx import Kokoro
from script import LINES, T, B, SONG_END

SR = 24000
k = Kokoro("tts/kokoro-v1.0.onnx", "tts/voices-v1.0.bin")
os.makedirs("audio/lines", exist_ok=True)
TARGET_F0 = {"tinku": 285, "pinky": 310, "golu": 350}

def voice_style(v):
    if "+" not in v and "*" not in v: return v
    out = None
    for part in v.split("+"):
        name, w = part.split("*"); st = k.get_voice_style(name) * float(w)
        out = st if out is None else out + st
    return out.astype(np.float32)

def trim(x, thr=0.01):
    idx = np.where(np.abs(x) > thr)[0]
    return x if len(idx) == 0 else x[max(0, idx[0] - int(0.02 * SR)): idx[-1] + int(0.06 * SR)]

def tighten(x, max_gap=0.12, thr=0.012):
    hop = int(0.01 * SR); e = np.array([np.abs(x[i:i + hop]).max() for i in range(0, len(x) - hop, hop)])
    out = []; i = 0; n = len(e)
    while i < n:
        if e[i] < thr:
            j = i
            while j < n and e[j] < thr: j += 1
            keep = min(j - i, int(max_gap / 0.01)); out.append(x[i * hop:i * hop + keep * hop]); i = j
        else: out.append(x[i * hop:(i + 1) * hop]); i += 1
    out.append(x[n * hop:]); return np.concatenate(out)

def median_f0(x):
    f0, _ = pw.harvest(x.astype(np.float64), SR, f0_floor=60, f0_ceil=700, frame_period=5.0); v = f0[f0 > 0]
    return float(np.median(v)) if len(v) else 200.0

def reshape(x, f0k, fk):
    xd = x.astype(np.float64)
    f0, tm = pw.harvest(xd, SR, f0_floor=60, f0_ceil=700, frame_period=5.0)
    sp = pw.cheaptrick(xd, f0, tm, SR); ap = pw.d4c(xd, f0, tm, SR)
    nb = sp.shape[1]; src = np.clip(np.arange(nb) / fk, 0, nb - 1)
    sp2 = np.stack([np.interp(src, np.arange(nb), row) for row in sp])
    return pw.synthesize(f0 * f0k, sp2, ap, SR, frame_period=5.0).astype(np.float32)

def spoken_text(cap):
    return cap.replace("times table of 2", "times table of two").replace("Bye-bye", "Bye bye")

# per-kid pitch factor so each kid sits on their F0 target (measured on a test phrase)
F0K = {}
for kid in TARGET_F0:
    voice, speed, f0k, fk = FRIENDS_VOICES[f"{kid}_en"]
    x, _ = k.create("Red is the apple, shiny and sweet!", voice=voice_style(voice), speed=speed, lang="en-us")
    F0K[kid] = TARGET_F0[kid] / median_f0(trim(x))

N = int((SONG_END + 2) * SR)
tracks = {s: np.zeros(N, np.float32) for s in TARGET_F0}
timeline = []
for li, l in enumerate(LINES):
    kid = l["singers"][0]
    voice, speed, f0k, fk = FRIENDS_VOICES[f"{kid}_en"]
    txt = spoken_text(l["cap"])
    x, _ = k.create(txt, voice=voice_style(voice), speed=speed, lang="en-us")
    x = reshape(tighten(trim(x)), F0K[kid], 1.0 + (fk - 1.0) * 0.6)
    x = x / (np.abs(x).max() + 1e-9) * 0.85
    slot = T(LINES[li + 1]["beat"]) - T(l["beat"]) if li + 1 < len(LINES) else 4.0
    d = len(x) / SR
    t0 = T(l["beat"]) + 0.05
    i = int(t0 * SR); tracks[kid][i:i + len(x)] += x[:N - i]
    # word times: spread over the voiced part by character position (good enough to pop visuals on the word)
    e = np.convolve(np.abs(x), np.ones(240) / 240, "same"); on = np.where(e > 0.03)[0]
    a, b = (on[0] / SR, on[-1] / SR) if len(on) else (0, d)
    words = []; pos = 0; low = txt.lower()
    for w in re.findall(r"[A-Za-z'\-]+", txt):
        j = low.find(w.lower(), pos); pos = j + len(w)
        words.append((w, round(t0 + a + (b - a) * j / max(1, len(txt)), 3)))
    timeline.append(dict(i=li, cue=l["cue"], spk=kid, cap=l["cap"], start=round(t0, 3), end=round(t0 + d, 3), words=words))
    flag = "  <-- longer than its slot!" if d > slot - 0.1 else ""
    print(f"{li:02d} {kid:6s} {t0:7.2f} dur {d:4.2f}/{slot:4.2f}  {txt}{flag}", flush=True)
for s, x in tracks.items(): sf.write(f"audio/lines/vox_{s}.wav", x, SR)
print("F0 factors", {k_: round(v, 2) for k_, v in F0K.items()})
for s in TARGET_F0:
    x, _ = sf.read(f"audio/lines/vox_{s}.wav"); print(s, "median F0", round(median_f0(x[x != 0][: SR * 20]), 1))
json.dump(dict(lines=timeline, song_end=SONG_END, spoken=True), open("timeline.json", "w"), indent=1)
print("done")
