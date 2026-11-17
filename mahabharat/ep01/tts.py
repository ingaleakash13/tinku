import json, os, re, numpy as np, soundfile as sf, pyworld as pw
from kokoro_onnx import Kokoro
from script import LINES, VOICES

SR = 24000
os.makedirs("audio/lines", exist_ok=True)
k = Kokoro("tts/kokoro-v1.0.onnx", "tts/voices-v1.0.bin")

def trim(x, thr=0.01):
    idx = np.where(np.abs(x) > thr)[0]
    if len(idx) == 0: return x
    return x[max(0, idx[0] - int(0.03 * SR)): min(len(x), idx[-1] + int(0.08 * SR))]

def reshape(x, f0k, fk):
    """Change pitch and voice character (formants) without changing speed."""
    if f0k == 1.0 and fk == 1.0: return x
    xd = x.astype(np.float64)
    f0, tm = pw.harvest(xd, SR, f0_floor=60, f0_ceil=700, frame_period=5.0)
    sp = pw.cheaptrick(xd, f0, tm, SR); ap = pw.d4c(xd, f0, tm, SR)
    nb = sp.shape[1]; src = np.clip(np.arange(nb) / fk, 0, nb - 1)
    sp2 = np.stack([np.interp(src, np.arange(nb), row) for row in sp])
    y = pw.synthesize(f0 * f0k, sp2, ap, SR, frame_period=5.0)
    return y.astype(np.float32)

rng = np.random.default_rng(3)
_ir = rng.standard_normal(int(0.22 * SR)) * np.exp(-np.arange(int(0.22 * SR)) / (0.05 * SR)); _ir /= np.abs(_ir).sum()
def room(x, wet=0.10):
    r = np.convolve(x, _ir)[: len(x) + int(0.15 * SR)]
    y = np.pad(x, (0, len(r) - len(x))); return (y * (1 - wet) + r * wet * 6).astype(np.float32)

def tighten(x, max_gap=0.14, thr=0.012):
    """Shorten any silence inside a line to a natural breath so speech flows without stops."""
    hop = int(0.01 * SR); e = np.array([np.abs(x[i:i + hop]).max() for i in range(0, len(x) - hop, hop)])
    out = []; i = 0; n = len(e)
    while i < n:
        if e[i] < thr:
            j = i
            while j < n and e[j] < thr: j += 1
            keep = min(j - i, int(max_gap / 0.01))
            a = i * hop; out.append(x[a:a + keep * hop]); i = j
        else:
            out.append(x[i * hop:(i + 1) * hop]); i += 1
    out.append(x[n * hop:])
    return np.concatenate(out)

def speak(text, voice, speed):
    s, sr = k.create(text, voice=voice, speed=speed, lang="hi")   # whole line in one breath
    return tighten(trim(s))

t = 0.0; timeline = []
for i, (scene, spk, hi, en, pause, cue) in enumerate(LINES):
    voice, speed, f0k, fk = VOICES[spk]
    x = room(reshape(speak(hi, voice, speed), f0k, fk))
    x = x / (np.abs(x).max() + 1e-9) * 0.9
    fn = f"audio/lines/{i:02d}.wav"; sf.write(fn, x, SR)
    t += pause; d = len(x) / SR
    timeline.append(dict(i=i, scene=scene, speaker=spk, text=hi, en=en, cue=cue, start=round(t, 3), end=round(t + d, 3), file=fn))
    t += d
    print(f"{i:02d} {spk:9s} {t-d:6.2f}-{t:6.2f} {en}")
json.dump(dict(lines=timeline, speech_end=t), open("timeline.json", "w"), indent=1, ensure_ascii=False)
print("speech ends", round(t, 2))
