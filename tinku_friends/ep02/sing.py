"""Singing voice for Tinku & Friends song episodes.
Each word is spoken by Kokoro, then WORLD (pyworld) re-times every syllable onto its note and replaces the pitch
with the melody (glide + vibrato), and shifts formants for a child's voice. Choruses layer the three kids."""
import sys, os, json, numpy as np, soundfile as sf, pyworld as pw
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "mahabharat", "lib"))
from voices import FRIENDS_VOICES
from kokoro_onnx import Kokoro
from script import LINES, B, T, SONG_END

SR = 24000; FP = 5.0; HOP = FP / 1000
k = Kokoro("tts/kokoro-v1.0.onnx", "tts/voices-v1.0.bin")
os.makedirs("audio/lines", exist_ok=True)
rng = np.random.default_rng(11)

def hz(m): return 440.0 * 2 ** ((m - 69) / 12)

_cache = {}
def voice_style(v):
    """'af_heart' or a blend like 'af_heart*0.6+am_puck*0.4' (mixed Kokoro style vectors)."""
    if "+" not in v and "*" not in v: return v
    out = None
    for part in v.split("+"):
        name, w = part.split("*"); st = k.get_voice_style(name) * float(w)
        out = st if out is None else out + st
    return out.astype(np.float32)
def analyse(word, voice, speed):
    key = (word, voice)
    if key in _cache: return _cache[key]
    txt = word.strip(",!").replace("-", "")
    x, _ = k.create(txt + ".", voice=voice_style(voice), speed=speed, lang="en-us")
    idx = np.where(np.abs(x) > 0.01)[0]
    x = x[max(0, idx[0] - int(0.02 * SR)): idx[-1] + int(0.04 * SR)].astype(np.float64)
    f0, tm = pw.harvest(x, SR, f0_floor=80, f0_ceil=700, frame_period=FP)
    sp = pw.cheaptrick(x, f0, tm, SR); ap = pw.d4c(x, f0, tm, SR)
    _cache[key] = (f0, sp, ap); return _cache[key]

def stretch_idx(n_in, voiced, n_out):
    """Frame map: unvoiced (consonant) frames keep speed when possible, voiced frames absorb the stretch."""
    nv = voiced.sum(); nu = n_in - nv
    if n_out <= n_in or nv == 0:
        return np.linspace(0, n_in - 1, max(1, n_out))
    rv = (n_out - nu) / nv
    w = np.where(voiced, rv, 1.0); cum = np.concatenate([[0], np.cumsum(w)])
    return np.interp(np.arange(n_out) + 0.5, cum, np.arange(n_in + 1)) - 0.5

def sing_word(word, notes, t_beat, voice, speed, fk, prev_m, legato=False):
    """Returns (start_time, audio) — voicing of syllable 1 lands on t_beat."""
    f0, sp, ap = analyse(word, voice, speed)
    voiced = f0 > 0; n = len(f0)
    # harvest flickers to 'unvoiced' inside vowels -> the voice drops to a whisper mid-note. Close short gaps.
    i = 0
    while i < n:
        if not voiced[i]:
            j = i
            while j < n and not voiced[j]: j += 1
            if i > 0 and j < n and (j - i) <= 6: voiced[i:j] = True
            i = j
        else: i += 1
    vi = np.where(voiced)[0]
    if len(vi) == 0: vi = np.array([0, n - 1])
    v0, v1 = vi[0], vi[-1] + 1
    ns = len(notes)
    # syllable boundaries inside the voiced span: prefer unvoiced gaps, else equal split
    gaps = [i for i in range(v0 + 1, v1) if not voiced[i] and voiced[i - 1]]
    bounds = [v0]
    for s in range(1, ns):
        target = v0 + (v1 - v0) * s / ns
        cand = [g for g in gaps if abs(g - target) < (v1 - v0) / ns * 0.5]
        bounds.append(min(cand, key=lambda g: abs(g - target)) if cand else int(round(target)))
    bounds.append(n)               # last syllable keeps the word's tail consonant
    pre = v0                       # leading consonant frames go before the beat
    out_f0, out_sp, out_ap = [f0[:pre] * 0], [sp[:pre]], [ap[:pre]]
    for s, (m, beats) in enumerate(notes):
        a, b = bounds[s], bounds[s + 1]
        last = s == ns - 1
        dur = beats * B - (0.015 if (last and legato) else (beats * B * 0.08 + 0.02) if last else 0.0)
        n_out = max(4, int(dur / HOP))
        tail = 0
        if s == ns - 1:   # keep unvoiced word ending (t, s, k…) at natural length after the note
            j = b
            while j > a and not voiced[j - 1]: j -= 1
            tail = b - j; b = j
            n_out = max(4, n_out - tail)
        idx = stretch_idx(b - a, voiced[a:b], n_out) + a
        idx = np.clip(idx, a, b - 1); i0 = np.floor(idx).astype(int); i1 = np.minimum(i0 + 1, b - 1); fr = (idx - i0)[:, None]
        ii = np.clip(np.round(idx).astype(int), a, b - 1)
        SPi = np.exp(np.log(sp[i0] + 1e-12) * (1 - fr) + np.log(sp[i1] + 1e-12) * fr); APi = ap[i0] * (1 - fr) + ap[i1] * fr
        tt = np.arange(n_out) * HOP
        target = hz(m)
        start_f = hz(prev_m) if prev_m else target * 0.94
        glide = np.exp(-tt / 0.045)
        fq = target * (start_f / target) ** glide
        vib = 1 + 0.011 * np.sin(2 * np.pi * 5.6 * tt + rng.uniform(0, 6)) * np.clip((tt - 0.22) / 0.25, 0, 1)
        fq = fq * vib * (1 + 0.004 * rng.standard_normal())
        vo = voiced[ii]
        out_f0.append(np.where(vo, fq, 0.0)); out_sp.append(SPi); out_ap.append(APi)
        if tail:
            out_f0.append(f0[b:b + tail] * 0); out_sp.append(sp[b:b + tail]); out_ap.append(ap[b:b + tail])
        prev_m = m
    F0 = np.concatenate(out_f0); SP = np.concatenate(out_sp); AP = np.concatenate(out_ap)
    vmask = F0 > 0     # keep vowels firm and clear: limit breathiness in voiced frames
    lim = np.ones(AP.shape[1]); lim[: int(AP.shape[1] * 4000 / (SR / 2))] = 0.35
    AP[vmask] = np.minimum(AP[vmask], lim); AP = np.ascontiguousarray(AP)
    nb = SP.shape[1]; src = np.clip(np.arange(nb) / fk, 0, nb - 1)
    SP = np.ascontiguousarray(np.stack([np.interp(src, np.arange(nb), row) for row in SP]))
    y = pw.synthesize(F0, SP, AP, SR, frame_period=FP)
    e = np.ones(len(y)); r = int(0.012 * SR); e[:r] = np.linspace(0, 1, r); e[-r:] = np.linspace(1, 0, r)
    return T(t_beat) - pre * HOP, (y * e).astype(np.float32), prev_m

def sing_line(l, singer):
    voice, speed, f0k, fk = FRIENDS_VOICES[f"{singer}_en"]
    fk = 1.0 + (fk - 1.0) * 0.5
    beat = l["beat"]; prev = None; parts = []
    items = l["notes"]
    for wi, (w, notes) in enumerate(items):
        if w is None: beat += sum(d for _, d in notes); prev = None; continue
        nxt_word = wi + 1 < len(items) and items[wi + 1][0] is not None
        t0, y, prev = sing_word(w, notes, beat, voice, 1.0, fk, prev, legato=nxt_word)
        parts.append((t0, y)); beat += sum(d for _, d in notes)
    return parts

N = int((SONG_END + 2) * SR)
tracks = {s: np.zeros(N, np.float32) for s in ("tinku", "pinky", "golu")}
_ir = rng.standard_normal(int(0.3 * SR)) * np.exp(-np.arange(int(0.3 * SR)) / (0.07 * SR)); _ir /= np.abs(_ir).sum()
timeline = []
for li, l in enumerate(LINES):
    group = len(l["singers"]) > 1
    t_first, t_last = 1e9, 0
    for gi, s in enumerate(l["singers"]):
        for t0, y in sing_line(l, s):
            if group: t0 += [0.0, 0.028, 0.041][gi]
            y = y / (np.abs(y).max() + 1e-9) * ([0.8, 0.32, 0.28][gi] if group else 0.85)
            i = int(t0 * SR); tracks[s][i:i + len(y)] += y[:N - i]
            t_first = min(t_first, t0); t_last = max(t_last, t0 + len(y) / SR)
    timeline.append(dict(i=li, cue=l["cue"], spk=l["spk"], singers=l["singers"], cap=l["cap"], start=round(t_first, 3), end=round(t_last, 3),
                         words=[(w, T(l["beat"] + sum(sum(d for _, d in nn) for _, nn in l["notes"][:j]))) for j, (w, _) in enumerate(l["notes"]) if w]))
    print(f"{li:02d} {l['cue']:12s} {t_first:7.2f}-{t_last:7.2f} {l['cap']}", flush=True)
for s, x in tracks.items():
    wet = np.convolve(x, _ir)[:N]
    sf.write(f"audio/lines/vox_{s}.wav", (x * 0.92 + wet * 1.2).astype(np.float32), SR)
json.dump(dict(lines=timeline, song_end=SONG_END), open("timeline.json", "w"), indent=1)
print("done")
