"""Reel 02: Tinku solo stand-up — 3 quick clean jokes for kids AND adults (1080x1920), drawn natively for Reels.
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
DURATION = round(E("j3b") + 2.6, 2)
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

def stage(c, t):
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgba(0, *hexc("#2a1a4a")); g.add_color_stop_rgba(1, *hexc("#4a2a6a")); c.set_source(g); c.paint()
    for row in range(26):   # brick wall
        for k in range(8):
            x = k * 150 + (75 if row % 2 else 0) - 40; y = 200 + row * 52
            rrect(c, x, y, 140, 44, 4); setc(c, (0.55, 0.25, 0.3, 0.35)); c.fill()
    for sgn in (-1, 1):     # red curtains
        x0 = 0 if sgn < 0 else W
        c.move_to(x0, 0); c.line_to(x0 - sgn * 230, 0)
        for k in range(6): c.curve_to(x0 - sgn * (200 - k * 8), 300 + k * 260, x0 - sgn * (150 - k * 10), 400 + k * 260, x0 - sgn * (190 - k * 6), 560 + k * 260)
        c.line_to(x0, H); c.close_path(); fs(c, "#c0283a", "#6a1020", 4)
        for k in range(4): c.move_to(x0 - sgn * (40 + k * 45), 0); c.curve_to(x0 - sgn * (30 + k * 45), 700, x0 - sgn * (60 + k * 45), 1300, x0 - sgn * (40 + k * 45), H)
        setc(c, (0.4, 0.05, 0.1, 0.35)); c.set_line_width(6); c.stroke()
    c.move_to(0, 0); c.line_to(W, 0); c.line_to(W, 150); c.curve_to(800, 220, 280, 220, 0, 150); c.close_path(); fs(c, "#a8202e", "#6a1020", 4)
    rg = cairo.RadialGradient(540, 1250, 60, 540, 1250, 560); rg.add_color_stop_rgba(0, 1, 0.95, 0.7, 0.45); rg.add_color_stop_rgba(1, 1, 0.95, 0.7, 0)   # spotlight
    c.set_source(rg); c.paint()
    c.rectangle(0, GY + 20, W, H - GY); setc(c, "#6a3a2a"); c.fill()                                    # stage floor
    for k in range(9): c.move_to(0, GY + 20 + k * 60); c.line_to(W, GY + 20 + k * 60)
    setc(c, (0.3, 0.15, 0.1, 0.4)); c.set_line_width(3); c.stroke()
    ell(c, 540, GY + 60, 300, 50); setc(c, (1, 0.95, 0.7, 0.25)); c.fill()
    c.move_to(860, GY + 30); c.line_to(860, 1080); setc(c, "#2a2a3a"); c.set_line_width(10); c.stroke()    # mic stand
    ell(c, 860, GY + 34, 50, 12); setc(c, "#2a2a3a"); c.fill(); ell(c, 860, 1060, 18, 30); fs(c, "#555566", "#222233", 3)

def phone(c, x, y, rot=0.0, s=1.0):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    rrect(c, -34, -62, 68, 124, 12); fs(c, "#2a2a3a", "#111111", 3); rrect(c, -27, -50, 54, 96, 6); fs(c, "#5ac8ff")
    for k in range(3): rrect(c, -20, -40 + k * 30, 40, 18, 4); setc(c, (1, 1, 1, 0.7)); c.fill()
    c.restore()

def tv(c, x, y, s, t):
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, -150, -110, 300, 210, 18); fs(c, "#3a3a4a", "#1a1a2a", 5)
    rrect(c, -130, -92, 260, 170, 10); setc(c, "#ff8c1a" if int(t * 3) % 2 else "#2f7bff"); c.fill()
    ell(c, -40, -10, 40, 40); setc(c, "#ffd23f"); c.fill(); poly(c, [(20, 40), (80, -40), (120, 40)]); setc(c, "#2fbf4a"); c.fill()
    for sgn in (-1, 1): c.move_to(sgn * 30, -110); c.line_to(sgn * 80, -180); setc(c, "#3a3a4a"); c.set_line_width(5); c.stroke()
    rrect(c, -60, 100, 120, 20, 6); fs(c, "#3a3a4a")
    c.restore()

def laptop(c, x, y, s, t, mode):
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, -180, -230, 360, 230, 16); fs(c, "#d8dce6", "#5a5e6a", 5); rrect(c, -160, -212, 320, 194, 8); setc(c, "#ffffff"); c.fill()
    rrect(c, -140, -150, 280, 50, 25); fs(c, "#ffffff", "#9aa0b0", 3)                                   # generic search box (no logos)
    c.arc(-112, -125, 12, 0, 2 * PI); setc(c, "#9aa0b0"); c.set_line_width(3); c.stroke()
    txt = "why am I so lazy?" if mode == 0 else ("..." if mode == 1 else "Tomorrow.")
    draw_text(c, txt, 10, -125, 28 if mode != 2 else 34, "#2b2d42", None, 0, lang="en")
    if mode == 1:
        for k in range(8):
            a = t * 6 + k * 0.78; ell(c, 30 * math.cos(a), -60 + 30 * math.sin(a), 5, 5); setc(c, (0.3, 0.5, 1, (k + 1) / 8)); c.fill()
    poly(c, [(-200, 0), (200, 0), (230, 30), (-230, 30)]); fs(c, "#b8bcc6", "#5a5e6a", 4)
    c.restore()

def report(c, x, y, rot, flip):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(1 - 2 * flip if flip < 0.5 else 2 * flip - 1, 1)
    rrect(c, -90, -120, 180, 240, 10); fs(c, "#ffffff", "#7a8ab8", 4)
    if flip < 0.5:
        draw_text(c, "REPORT CARD", 0, -90, 26, "#2f5bd8", None, 0, lang="en")
        for k in range(5): c.move_to(-70, -50 + k * 34); c.line_to(70, -50 + k * 34)
        setc(c, (0.6, 0.65, 0.8, 0.8)); c.set_line_width(3); c.stroke()
    else:
        draw_text(c, "MARKS:", 0, -60, 30, "#2b2d42", None, 0, lang="en"); draw_text(c, "?", 0, 20, 90, "#ff4f5f", None, 0, lang="en")
    c.restore()

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
    z = 1.0 + 0.04 * ease(prog(t, 0, DURATION))
    for cue in ("j1b", "j2b", "j3b"):   # punch-in on every punchline
        z += 0.10 * ease(prog(t, E(cue) - 0.8, E(cue) - 0.3)) * (1 - ease(prog(t, E(cue) + 0.6, E(cue) + 1.0)))
    c.save(); c.translate(540, 1150); c.scale(z, z); c.translate(-540, -1150)
    stage(c, t)
    j1 = t < S("j2a") - 0.6; j2 = S("j2a") - 0.6 <= t < S("j3a") - 0.6; j3 = t >= S("j3a") - 0.6
    tvp = ease(prog(t, S("j1b") + 1.2, S("j1b") + 1.6)) if j1 else 0
    if tvp > 0: tv(c, 270, 900, 1.0 * tvp, t)
    if j2:
        mode = 0 if t < S("j2b") - 0.2 else (1 if t < S("j2b") + 1.2 else 2)
        k_ = ease(prog(t, S("j2a") - 0.6, S("j2a") - 0.2))
        if k_ > 0:   # small table under the laptop
            rrect(c, 225 - 200 * k_, 1070, 400 * k_, 24, 6); fs(c, "#a86a32", "#5a3414", 3)
            for lx in (-160, 140): rrect(c, 225 + lx * k_, 1094, 20, (GY - 1074) * k_, 4); fs(c, "#8a5228")
        laptop(c, 225, 1040, k_, t, mode)
    a = talk("tinku", t, 0); look = 0.0; hop = 0.0; lean = 0.0
    punch = any(E(cu) - 0.4 <= t <= E(cu) + 1.0 for cu in ("j1b", "j2b", "j3b"))
    if j1 and t < S("j1b") + 1.0: a = (a[0], (1.6, 0.9))                       # holding the phone
    if j2: look = -0.5; a = (a[0], (1.2, 1.0)) if t < S("j2b") else a
    if j3: a = (a[0], (1.5, 0.9))                                              # holding the report card
    if punch: a = ((0.6, -1.4), (0.6, -1.4)) if not j3 else ((0.6, -1.4), (1.5, 0.9)); hop = abs(math.sin(t * 9)) * 14; lean = 0.06 * math.sin(t * 7)
    hands = tinku(c, 600, GY, t, 2.4, a, mo("tinku", t), look, blink(t, 0.3) or (punch and int(t * 4) % 3 == 0), hop, lean)
    hx, hy = hands[1]
    if j1 and t < S("j1b") + 1.0:
        dropped = prog(t, S("j1b") + 0.3, S("j1b") + 0.9)
        phone(c, lerp(hx + 10, 760, dropped), lerp(hy - 50, GY + 10, dropped), lerp(-0.2, 1.4, dropped))
    elif j1: phone(c, 760, GY + 10, 1.4)
    if j3: report(c, hx + 20, hy - 120, -0.15, ease(prog(t, S("j3b") + 3.8, S("j3b") + 4.4)))
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
    def rimshot(t):
        n = int(0.12 * SR); add(sfx, np.sin(2 * np.pi * 180 * np.arange(n) / SR) * env(n, 0.002, 0.05), t, 0.6)
        n = int(0.5 * SR); add(sfx, sosfilt(butter(2, [3000, 12000], btype="band", fs=SR, output="sos"), rng.uniform(-1, 1, n)) * env(n, 0.002, 0.18), t + 0.18, 0.5)
    def laugh(t, d=1.6):
        for k in range(int(d * 7)):
            n = int(0.11 * SR); tt = np.arange(n) / SR; f = rng.uniform(380, 620)
            x = (np.sin(2 * np.pi * f * tt) + 0.5 * np.sin(4 * np.pi * f * tt)) * np.sin(np.pi * tt / 0.11) * rng.uniform(0.4, 1)
            add(sfx, sosfilt(butter(2, [300, 2500], btype="band", fs=SR, output="sos"), x + 0.3 * rng.uniform(-1, 1, n)), t + k / 7 + rng.uniform(0, 0.04), 0.12)
    for cu in ("j1b", "j2b", "j3b"): rimshot(E(cu) + 0.05); laugh(E(cu) + 0.2)
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
