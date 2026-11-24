"""Reel 01: 'Moti ate my homework' — original 30-second vertical joke (1080x1920), drawn natively for Reels.
No hook overlay, no sound-words, no brand text. Big captions in the upper middle (Instagram UI covers the bottom)."""
import sys, os, math, json, random, subprocess, numpy as np, soundfile as sf, cairo
from scipy.signal import resample_poly, butter, sosfilt
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "mahabharat", "lib"))
from chars import *
from script import NAMES

W, H, FPS = 1080, 1920, 30
TL = json.load(open("timeline.json")); LINES = TL["lines"]
def L(cue): return next(l for l in LINES if l["cue"] == cue)
def S(cue): return L(cue)["start"]
def E(cue): return L(cue)["end"]
T_SNEEZE = E("promise") + 0.6
DURATION = round(T_SNEEZE + 3.6, 2)
GY = 1430

def prog(t, a, b): return clamp((t - a) / (b - a)) if b > a else float(t >= a)
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def lerp(a, b, x): return a + (b - a) * x
def active(t, cue, pre=0.0, post=0.0): return S(cue) - pre <= t <= E(cue) + post
def blink(t, off): return ((t + off) % 3.6) < 0.12

NF = int(DURATION * FPS) + 2
MOUTH = {k: np.zeros(NF) for k in NAMES}
for l in LINES:
    x, sr = sf.read(l["file"]); hp = sr // FPS
    r = np.array([np.sqrt((x[i:i + hp] ** 2).mean()) for i in range(0, len(x) - hp, hp)])
    r = np.clip(r / (np.percentile(r, 90) + 1e-6), 0, 1.2)
    f0 = int(l["start"] * FPS); MOUTH[l["speaker"]][f0:f0 + len(r)] = r[:NF - f0]
def mo(spk, t):
    i = int(t * FPS); return float(MOUTH[spk][i]) if 0 <= i < NF else 0.0
def speaking(spk, t): return any(l["speaker"] == spk and l["start"] - 0.1 <= t <= l["end"] + 0.1 for l in LINES)
def talk(spk, t, seed=0.0):
    m = mo(spk, t); br = 0.03 * math.sin(t * 1.6 + seed)
    if not speaking(spk, t): return ((0.14 + br, 0.25), (0.14 - br, 0.25))
    return ((0.25 + 0.12 * math.sin(t * 0.9 + seed) + 0.1 * m, 0.5 + 0.4 * m), (0.55 + 0.25 * math.sin(t * 1.2 + seed) + 0.25 * m, 1.2 + 0.35 * math.sin(t * 1.8 + seed) + 0.3 * m))
HIPS = ((0.45, -1.1), (0.45, -1.1))

def room(c, t):
    g = cairo.LinearGradient(0, 0, 0, GY); g.add_color_stop_rgba(0, *hexc("#ffe9c7")); g.add_color_stop_rgba(1, *hexc("#ffd6a0")); c.set_source(g); c.rectangle(0, 0, W, H); c.fill()
    for k in range(12): c.rectangle(k * 96, 0, 48, GY); setc(c, (1, 1, 1, 0.12)); c.fill()        # wallpaper stripes
    rrect(c, 90, 560, 330, 300, 14); fs(c, "#8fd3ff", "#8a5a2a", 10)                                # window
    ell(c, 340, 640, 44, 44); setc(c, "#fff3a0"); c.fill()
    for cx_, cy_ in ((190, 700), (260, 690)): ell(c, cx_, cy_, 50, 22); setc(c, (1, 1, 1, 0.9)); c.fill()
    c.move_to(255, 560); c.line_to(255, 860); c.move_to(90, 710); c.line_to(420, 710); setc(c, "#8a5a2a"); c.set_line_width(8); c.stroke()
    rrect(c, 640, 640, 340, 18, 4); fs(c, "#a86a32", "#5a3414", 3)                                   # shelf + books
    for k, col in enumerate(("#ff5b5b", "#2f7bff", "#ffd23f", "#2fbf4a", "#9b3fd6")):
        rrect(c, 660 + k * 52, 540 + (k % 2) * 14, 40, 100 - (k % 2) * 14, 4); fs(c, col, dark(col, 0.7), 2)
    c.rectangle(0, GY, W, H - GY); setc(c, "#c98a5a"); c.fill()                                    # floor
    for k in range(8): c.move_to(0, GY + k * 70); c.line_to(W, GY + k * 70)
    setc(c, (0.45, 0.25, 0.12, 0.25)); c.set_line_width(3); c.stroke()
    ell(c, 560, 1770, 380, 80); setc(c, "#4fb8a8"); c.fill(); ell(c, 560, 1770, 300, 58); setc(c, "#7fd8c8"); c.fill()   # rug

def notebook(c, x, y, s=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, -70, -46, 140, 92, 6); fs(c, "#ffffff", "#7a8ab8", 3); c.move_to(0, -46); c.line_to(0, 46); setc(c, "#7a8ab8"); c.set_line_width(3); c.stroke()
    for k in range(4): c.move_to(-60, -26 + k * 16); c.line_to(-10, -26 + k * 16); c.move_to(10, -26 + k * 16); c.line_to(60, -26 + k * 16)
    setc(c, (0.5, 0.6, 0.9, 0.6)); c.set_line_width(2); c.stroke()
    poly(c, [(40, 46), (70, 16), (70, 46)]); fs(c, "#ffe9c7")                                        # a bite missing!
    c.restore()

def paper_scrap(c, x, y, rot=0.0, s=1.0):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    poly(c, [(-26, -18), (22, -22), (28, 10), (4, 22), (-24, 16)]); fs(c, "#ffffff", "#7a8ab8", 2)
    for k in range(3): c.move_to(-18, -10 + k * 9); c.line_to(16, -12 + k * 9)
    setc(c, (0.5, 0.6, 0.9, 0.7)); c.set_line_width(2); c.stroke(); c.restore()

def captions(c, t):
    cur = None
    for i, l in enumerate(LINES):
        nxt = LINES[i + 1]["start"] if i + 1 < len(LINES) else 1e9
        if l["start"] - 0.12 <= t <= min(l["end"] + 0.6, nxt - 0.12): cur = l
    if not cur: return
    a = clamp((t - cur["start"] + 0.12) / 0.15)
    name, col = NAMES[cur["speaker"]]
    c.select_font_face("Fredoka", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); c.set_font_size(64)
    words = cur["en"].split(); lines, curl = [], ""
    for w in words:
        cand = (curl + " " + w).strip()
        if c.text_extents(cand).x_advance <= 900 or not curl: curl = cand
        else: lines.append(curl); curl = w
    lines.append(curl)
    lh = 80; bh = 50 + lh * len(lines); bx, bw, by = 60, 960, 300
    c.push_group()
    rrect(c, bx + 5, by + 8, bw, bh, 40); setc(c, (0.1, 0.05, 0.2, 0.25)); c.fill()
    rrect(c, bx, by, bw, bh, 40); fs(c, (1, 1, 1, 0.97), hexc(col), 9)
    nw = text_surface(name, 40, "#ffffff", None, 0, "hi").get_width()
    rrect(c, bx + 40, by - 38, nw + 44, 66, 33); fs(c, col, (1, 1, 1, 1), 5)
    draw_text(c, name, bx + 62, by - 5, 40, "#ffffff", None, 0, lang="hi", anchor="l")
    c.select_font_face("Fredoka", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); c.set_font_size(64)
    for i, ln in enumerate(lines):
        c.move_to(W / 2 - c.text_extents(ln).x_advance / 2, by + 25 + lh * 0.75 + i * lh); setc(c, "#2b2d42"); c.show_text(ln)
    c.pop_group_to_source(); c.paint_with_alpha(a)

def frame(t, surf):
    c = cairo.Context(surf)
    # camera: gentle push-in, close-up on sleeping Moti for the punchline
    z, cx, cy = 1.0 + 0.03 * ease(prog(t, 0, DURATION)), 540, 1100
    w = ease(prog(t, S("asleep") - 0.2, S("asleep") + 0.6)) * (1 - ease(prog(t, S("tired") - 0.3, S("tired") + 0.2)))
    w2 = ease(prog(t, T_SNEEZE - 0.3, T_SNEEZE + 0.3)) * (1 - ease(prog(t, T_SNEEZE + 2.0, T_SNEEZE + 2.6)))
    w = max(w, w2)
    z, cx, cy = lerp(z, 1.3, w), lerp(cx, 560, w), lerp(cy, 1500, w)
    cx = min(max(cx, 540 / z), W - 540 / z); cy = min(max(cy, 1100 / z), H - 820 / z)
    c.save(); c.translate(540, 1100); c.scale(z, z); c.translate(-cx, -cy)
    room(c, t)
    rrect(c, 720, 1180, 300, 26, 6); fs(c, "#a86a32", "#5a3414", 3)                               # little study table
    for lx in (740, 990): rrect(c, lx, 1206, 18, 224, 4); fs(c, "#8a5228")
    notebook(c, 870, 1150, 1.0)
    # Pinky (hands on hips, then points at Moti, then facepalm)
    pa = talk("pinky", t, 1)
    if active(t, "q", 0, 0.6) or active(t, "golu", 0, 0.8): pa = HIPS
    if active(t, "asleep", 0, 0.8): pa = (pa[0], (1.0, 0.1))
    if t >= T_SNEEZE + 0.4: pa = (pa[0], (0.6, -2.2))                                            # facepalm
    pinky(c, 290, GY + 60, t, 2.05, pa, mo("pinky", t), 0.4, blink(t, 1.4), abs(math.sin(t * 10)) * 10 if active(t, "golu", 0, 0.4) else 0)
    # Golu (nervous wiggle, then cheeky grin)
    ga = talk("golu", t, 0)
    if active(t, "ate", 0, 0.4): ga = (ga[0], (1.1, 0.2))
    if active(t, "promise", 0, 1.0) or t >= T_SNEEZE: ga = ((0.6, -1.4), (0.6, -1.4))
    golu(c, 800, GY + 60, t, 2.15, ga, mo("golu", t), -0.4, blink(t, 2.2) or t >= T_SNEEZE + 0.6, abs(math.sin(t * 7)) * 8 if speaking("golu", t) else 0, 0.05 * math.sin(t * 6) if speaking("golu", t) else 0)
    # Moti asleep on the rug with a scrap of homework on his nose
    lift = 18 * math.sin(prog(t, S("bark") - 0.1, E("bark") + 0.5) * PI)
    sneeze = prog(t, T_SNEEZE, T_SNEEZE + 0.35)
    moti(c, 610, 1760, t, 1.5, mo("moti", t), 0.0, t < S("bark") - 0.1 or t > E("bark") + 0.5, lift + 20 * math.sin(sneeze * PI), 0.4)
    if sneeze <= 0: paper_scrap(c, 538, 1612 - lift, -0.3, 1.3)
    else:
        q = prog(t, T_SNEEZE, T_SNEEZE + 1.4); paper_scrap(c, lerp(538, 380, q), 1612 - 520 * math.sin(q * PI * 0.9) + 200 * q, q * 8, 1.3 + 0.3 * q)
    c.restore()
    captions(c, t)
    f = clamp((DURATION - t) / 0.8)
    if f < 1: c.rectangle(0, 0, W, H); setc(c, (0, 0, 0, 1 - f)); c.fill()
    return surf

# ---------------------------------------------------------------- audio: light ukulele, sleepy snore, sneeze puff, boing
SR = 48000; N = int(DURATION * SR); rng = np.random.default_rng(5)
def add(buf, x, t, g=1.0):
    i = int(t * SR)
    if 0 <= i < N: x = x[: N - i]; buf[i:i + len(x)] += g * x
def hz(m): return 440.0 * 2 ** ((m - 69) / 12)
def env(n, a=0.005, d=0.3): tt = np.arange(n) / SR; return np.minimum(1, tt / a) * np.exp(-tt / d)
def pluck(m, dur=0.8, decay=0.35):
    f = hz(m); p = int(SR / f); n = int(dur * SR); b = rng.uniform(-1, 1, p); out = np.zeros(n)
    for i in range(n): out[i] = b[i % p]; b[i % p] = 0.996 * 0.5 * (b[i % p] + b[(i + 1) % p])
    return out * np.exp(-np.arange(n) / SR / decay)
def sweep(f0, f1, dur, vib=0.0):
    n = int(dur * SR); tt = np.arange(n) / SR; f = f0 + (f1 - f0) * tt / dur
    if vib: f = f * (1 + 0.06 * np.sin(2 * np.pi * vib * tt))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(1, tt / 0.01) * np.minimum(1, (dur - tt) / 0.05)
def make_audio():
    music = np.zeros(N); sfx = np.zeros(N); voice = np.zeros(N)
    B = 60 / 112; chords = [[60, 64, 67], [57, 60, 64], [53, 57, 60], [55, 59, 62]]; cache = {}
    bar = 0
    while bar * 4 * B < DURATION:
        ch = chords[bar % 4]
        for k, s in enumerate((0, 1, 1.5, 2.5, 3)):
            for j, m in enumerate(ch):
                if m not in cache: cache[m] = pluck(m)
                add(music, cache[m], bar * 4 * B + s * B + j * 0.012, 0.12)
        bt = np.arange(int(B * SR)) / SR; add(music, np.sin(2 * np.pi * hz(ch[0] - 24) * bt) * env(len(bt), 0.01, 0.3), bar * 4 * B, 0.4)
        bar += 1
    for k in range(int(DURATION / 2.2)):   # soft snores while Moti sleeps
        tt = k * 2.2 + 0.4
        if tt < S("bark") - 0.5 or E("bark") + 0.6 < tt < T_SNEEZE - 0.5:
            n = int(0.9 * SR); x = sosfilt(butter(2, 300, fs=SR, output="sos"), rng.uniform(-1, 1, n)) * np.sin(np.pi * np.arange(n) / n) ** 2; add(sfx, x, tt, 0.5)
    add(sfx, sweep(180, 620, 0.3, vib=18), S("ate") + 1.8, 0.25)
    n = int(0.5 * SR); add(sfx, sosfilt(butter(2, [800, 5000], btype="band", fs=SR, output="sos"), rng.uniform(-1, 1, n)) * env(n, 0.005, 0.12), T_SNEEZE, 0.7)   # sneeze puff
    add(sfx, sweep(300, 900, 0.35, vib=20), T_SNEEZE + 0.3, 0.25)
    for l in LINES:
        x, sr = sf.read(l["file"]); add(voice, resample_poly(x, SR, sr), l["start"])
    sp = np.zeros(N, bool)
    for l in LINES: sp[int(l["start"] * SR):int(l["end"] * SR)] = True
    k_ = int(0.12 * SR); duck = np.convolve(np.where(sp, 0.35, 1.0), np.ones(k_) / k_, "same")
    fade = np.ones(N); fl = int(1.0 * SR); fade[-fl:] = np.linspace(1, 0, fl)
    mix = np.tanh((voice + music * 0.6 * duck + sfx * 0.8) * fade * 1.1) * 0.9
    os.makedirs("audio", exist_ok=True); sf.write("audio/mix.wav", np.stack([mix, mix], 1), SR, subtype="PCM_16")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        os.makedirs("stills", exist_ok=True)
        for ts in sys.argv[1:]:
            s_ = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); frame(float(ts), s_); s_.write_to_png(f"stills/r_{float(ts):05.2f}.png")
        sys.exit()
    make_audio()
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", "audio/mix.wav",
                          "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "19", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                          "-shortest", "-movflags", "+faststart", "reel.mp4"], stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    for f in range(int(DURATION * FPS)):
        frame(f / FPS, surf); surf.flush(); p.stdin.write(bytes(surf.get_data()))
    p.stdin.close(); p.wait(); print("reel ok", DURATION)
