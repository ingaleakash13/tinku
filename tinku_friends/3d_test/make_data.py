import sys, json, numpy as np, soundfile as sf
sys.path.insert(0, "../ep02")
import os; os.chdir("../ep02")
from script import LINES, NAMES, BPM, B, T, SECTIONS, BAR
FPS = 30
def word_time(cue, word):
    l = [x for x in LINES if x["cue"] == cue][0]; beat = l["beat"]
    for w, n in l["notes"]:
        if w and w.strip(",!").lower().startswith(word.lower()): return T(beat)
        beat += sum(d for _, d in n)
ct = [word_time("ch1_0", w) for w in ("Red", "orange", "yellow", "green")] + [word_time("ch1_1", w) for w in ("Blue", "indigo", "violet")]
mouth = {}
for s in ("tinku", "pinky", "golu"):
    x, sr = sf.read(f"audio/lines/vox_{s}.wav"); hp = sr // FPS
    r = np.array([np.sqrt((x[i:i + hp] ** 2).mean()) for i in range(0, len(x) - hp, hp)])
    r = np.clip(r / (np.percentile(r[r > 1e-4], 90) + 1e-6), 0, 1.2); r = np.convolve(r, [0.25, 0.5, 0.25], "same")
    mouth[s] = [round(float(v), 3) for v in r]
lines = [dict(start=T(l["beat"]), end=T(l["beat"] + sum(sum(d for _, d in n) for _, n in l["notes"])), cap=l["cap"], spk=l["spk"]) for l in LINES]
json.dump(dict(bpm=BPM, fps=FPS, lines=lines, names=NAMES, mouth=mouth, colorTimes=ct, introEnd=T(4 * BAR), t0=float(sys.argv[1]), firstChorus=True),
          open("../3d_test/data.json", "w"))
print("ok", ct[:2])
