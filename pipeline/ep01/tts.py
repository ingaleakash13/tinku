import json, os, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
from script import LINES, VOICES

SR = 24000
os.makedirs("audio/lines", exist_ok=True)
k = Kokoro("tts/kokoro-v1.0.onnx", "tts/voices-v1.0.bin")

def trim(x, thr=0.01):
    idx = np.where(np.abs(x) > thr)[0]
    if len(idx) == 0:
        return x
    a = max(0, idx[0] - int(0.03 * SR)); b = min(len(x), idx[-1] + int(0.08 * SR))
    return x[a:b]

def pitch(x, f):
    if f == 1.0:
        return x
    n = int(len(x) / f)
    return np.interp(np.arange(n) * f, np.arange(len(x)), x).astype(np.float32)

t = 0.0
timeline = []
for i, (scene, spk, text, pause, cue) in enumerate(LINES):
    voice, speed, pf = VOICES[spk]
    samples, sr = k.create(text, voice=voice, speed=speed, lang="en-us")
    assert sr == SR
    x = pitch(trim(samples), pf)
    x = x / (np.abs(x).max() + 1e-9) * 0.9
    fn = f"audio/lines/{i:02d}.wav"
    sf.write(fn, x, SR)
    t += pause
    d = len(x) / SR
    timeline.append(dict(i=i, scene=scene, speaker=spk, text=text, cue=cue, start=round(t, 3), end=round(t + d, 3), file=fn))
    t += d
    print(f"{i:02d} {spk:8s} {t-d:6.2f}-{t:6.2f}  {text}")

json.dump(dict(lines=timeline, speech_end=t), open("timeline.json", "w"), indent=1)
print("speech ends at", round(t, 2))
