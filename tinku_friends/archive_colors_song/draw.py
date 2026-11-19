"""Song video: a new full-screen world for every verse, dancing kids, things that pop exactly on the sung word."""
import sys, os, math, random, json, numpy as np, soundfile as sf, cairo
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "mahabharat", "lib"))
from chars import *
from scenery import sky, clouds, cloud, grass_field, treeline, ridge, birds, lin
from script import *

W, H, FPS = 1280, 720, 30
DURATION = SONG_END + 0.5
GY = 600
RAIN = ["#ff3b3b", "#ff8c1a", "#ffd21a", "#2fbf4a", "#2f8bff", "#4b3cc4", "#9b3fd6"]
COL = {k: h for k, _, h, *_ in COLORS}

def prog(t, a, b): return clamp((t - a) / (b - a)) if b > a else float(t >= a)
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def back(x, s=1.7):
    x = clamp(x); x -= 1; return x * x * ((s + 1) * x + s) + 1
def lerp(a, b, x): return a + (b - a) * x
def blink(t, off): return ((t + off) % 3.6) < 0.12

# ---------------------------------------------------------------- timing helpers
def section_at(t):
    bt = t / B / BAR
    for s in SECTIONS:
        if s[0] <= bt < s[0] + s[1]: return s
    return SECTIONS[-1]
def sec_t(s): return T(s[0] * BAR), T((s[0] + s[1]) * BAR)
LBY = {l["cue"]: l for l in LINES}
_TL = json.load(open("timeline.json")) if os.path.exists("timeline.json") else {}
SPOKEN = bool(_TL.get("spoken"))
_WT = {l["cue"]: l["words"] for l in _TL.get("lines", [])}
def word_time(cue, word, nth=0):
    if SPOKEN:   # spoken voices: use the measured time each word is said
        k = 0
        for w, tw in _WT[cue]:
            if w.lower().startswith(word.lower().strip(",!")) or (word == "Mohtee" and w.lower() == "moti"):
                if k == nth: return tw
                k += 1
        raise KeyError((cue, word))
    l = LBY[cue]; beat = l["beat"]; k = 0
    for w, notes in l["notes"]:
        if w and w.strip(",!").lower().startswith(word.lower()):
            if k == nth: return T(beat)
            k += 1
        beat += sum(d for _, d in notes)
    raise KeyError((cue, word))

# ---------------------------------------------------------------- mouths from each kid's vocal track
NF = int(DURATION * FPS) + 2
MOUTH = {}
for s in ("tinku", "pinky", "golu"):
    x, sr = sf.read(f"audio/lines/vox_{s}.wav"); hp = sr // FPS
    r = np.array([np.sqrt((x[i:i + hp] ** 2).mean()) for i in range(0, len(x) - hp, hp)])
    r = np.clip(r / (np.percentile(r[r > 1e-4], 90) + 1e-6), 0, 1.2) if (r > 1e-4).any() else r
    m = np.zeros(NF); m[:min(NF, len(r))] = r[:NF]; MOUTH[s] = np.convolve(m, [0.25, 0.5, 0.25], "same")
def mo(s, t):
    i = int(t * FPS); return float(MOUTH[s][i]) if s in MOUTH and 0 <= i < NF else 0.0
def singing(s, t): return mo(s, t) > 0.08

# ---------------------------------------------------------------- dance
def dance(name, t, kind, lead=False, seed=0.0):
    """Beat-synced moves -> (arms, hop, lean)."""
    bt = t / B; ph = bt % 1; bi = int(bt); bar = bi // 4
    bounce = math.sin(PI * ph) ** 2
    if kind in ("title", "card"):
        return ((0.2, 0.3), (2.3, 0.5 + 0.5 * math.sin(t * 9 + seed))), 14 * bounce, 0.0
    if kind == "echo":
        return ((2.5, 0.2), (2.5, 0.2)), 40 * math.sin(PI * ph), 0.0
    if kind == "fill":
        clap = ph < 0.25
        return (((0.6, -1.7), (0.6, -1.7)) if clap else ((0.9, -0.9), (0.9, -0.9))), 8 * bounce, 0.0
    if kind == "verse" and lead:
        m = mo(name, t)
        return ((0.35 + 0.15 * math.sin(t * 1.3 + seed) + 0.15 * m, 0.6 + 0.4 * m),
                (1.1 + 0.5 * math.sin(t * 2.1 + seed) + 0.3 * m, 1.0 + 0.4 * math.sin(t * 3.0) + 0.3 * m)), 10 * bounce, 0.06 * math.sin(PI * bt / 2)
    if kind == "verse":   # backing: sway and clap on 2 & 4
        if bi % 2 == 1 and ph < 0.3: return ((0.6, -1.7), (0.6, -1.7)), 6 * bounce, 0.05 * math.sin(PI * bt)
        return ((0.25, 0.3), (0.25, 0.3)), 6 * bounce, 0.07 * math.sin(PI * bt)
    move = bar % 4      # chorus / outro: rotate four moves every bar
    if move == 0:   # pump arms up, alternating
        up = bi % 2
        return ((2.6 if up else 0.9, 0.2 if up else 1.2), (0.9 if up else 2.6, 1.2 if up else 0.2)), 16 * bounce, 0.0
    if move == 1:   # sway with wave
        return ((0.3, 0.3), (2.2, 0.6 + 0.6 * math.sin(t * 10 + seed))), 8 * bounce, 0.1 * math.sin(PI * bt)
    if move == 2:   # clap clap
        clap = (ph < 0.3) or (0.5 <= ph < 0.8)
        return (((0.6, -1.7), (0.6, -1.7)) if clap else ((1.0, -0.8), (1.0, -0.8))), 10 * bounce, 0.0
    return ((2.4, 0.4), (2.4, 0.4)), 26 * math.sin(PI * ph), 0.0   # jump with hands up

def gang(c, t, kind, xs=(190, 360, 520, 665), s=0.82, lead=None, hide_moti=False, gy=GY):
    fns = (("tinku", tinku), ("pinky", pinky), ("golu", golu))
    for i, (name, fn) in enumerate(fns):
        k = kind
        arms, h, lean = dance(name, t, k, lead == name, i * 1.3)
        sc = s * (1.08 if lead == name else 1.0)
        fn(c, xs[i], gy + (14 if lead == name else 0), t, sc, arms, mo(name, t), 0.0, blink(t, i * 1.1), h, lean)
    if not hide_moti:
        ph = (t / B) % 1
        mh = 30 * math.sin(PI * ph) if kind in ("fill", "echo") else 10 * math.sin(PI * ph) ** 2
        barking = kind == "fill" and ph < 0.35
        moti(c, xs[3], gy, t, 0.74, 1.0 if barking else 0.0, 0.3, blink(t, 0.9), mh, 2.5 if kind != "verse" else 1.2)
        if barking: draw_text(c, "Woof!", xs[3] + 70, gy - 190 - 20 * ph, 40, "#a8673a", "#ffffff", 5, lang="en")

# ---------------------------------------------------------------- props
def apple(c, x, y, s):
    c.save(); c.translate(x, y); c.scale(s, s)
    ell(c, -9, 3, 20, 23); fs(c, "#ff3b3b", "#b81e1e", 2.5); ell(c, 9, 3, 20, 23); fs(c, "#ff3b3b", "#b81e1e", 2.5); ell(c, 0, 5, 22, 22); setc(c, "#ff3b3b"); c.fill()
    c.move_to(0, -18); c.line_to(3, -30); setc(c, "#7a4a24"); c.set_line_width(3.5); c.stroke()
    c.save(); c.translate(9, -26); c.rotate(-0.5); ell(c, 8, 0, 10, 5); fs(c, "#3fae4a", "#2a7a33", 1.5); c.restore()
    ell(c, -10, -5, 5, 8); setc(c, (1, 1, 1, 0.5)); c.fill(); c.restore()
def fruit_tree(c, x, y, s, leaf=("#3f9e3f", "#2f7f35", "#5fbf4a")):
    c.save(); c.translate(x, y); c.scale(s, s)
    ell(c, 0, 4, 90, 14); setc(c, (0, 0, 0, 0.15)); c.fill()
    c.move_to(-18, 0); c.curve_to(-14, -60, -20, -110, -40, -150); c.line_to(40, -150); c.curve_to(18, -110, 14, -60, 18, 0); c.close_path()
    c.set_source(lin(c, -20, 0, 20, 0, [(0, "#7a4a24"), (0.5, "#9a6232"), (1, "#5e3618")])); c.fill()
    cl = [(-70, -170, 60), (0, -210, 75), (70, -175, 62), (-35, -130, 55), (40, -130, 55), (0, -160, 60)]
    for dx, dy, r in cl: ell(c, dx + 6, dy + 8, r, r * 0.85); setc(c, leaf[1]); c.fill()
    for dx, dy, r in cl: ell(c, dx, dy, r, r * 0.85); setc(c, leaf[0]); c.fill()
    for dx, dy, r in cl: ell(c, dx - r * .25, dy - r * .3, r * .5, r * .38); setc(c, leaf[2]); c.fill()
    c.restore()
TREE_FRUIT = [(-70, -180), (-20, -230), (40, -215), (85, -170), (-45, -130), (20, -150), (60, -120), (-5, -185)]
def fire_truck(c, x, y, s, t):
    c.save(); c.translate(x, y); c.scale(s, s)
    ell(c, 0, 4, 150, 12); setc(c, (0, 0, 0, 0.2)); c.fill()
    rrect(c, -140, -95, 190, 75, 10); fs(c, "#e8322f", "#9a1a18", 3)
    c.move_to(50, -20); c.line_to(50, -110); c.line_to(105, -110); c.curve_to(130, -110, 140, -70, 140, -50); c.line_to(140, -20); c.close_path(); fs(c, "#ff4040", "#9a1a18", 3)
    rrect(c, 62, -100, 52, 36, 6); fs(c, "#bfe6ff", "#3a6a8a", 2.5)
    for k in range(6): rrect(c, -130 + k * 30, -124, 8, 30, 2); setc(c, "#d9d9d9"); c.fill()
    c.move_to(-135, -110); c.line_to(40, -110); c.move_to(-135, -124); c.line_to(40, -124); setc(c, "#bdbdbd"); c.set_line_width(5); c.stroke()
    rrect(c, -130, -70, 160, 12, 4); setc(c, "#ffd23f"); c.fill()
    on = int(t * 6) % 2
    ell(c, 80, -118, 12, 9); setc(c, "#2f7bff" if on else "#ff3b3b"); c.fill()
    for wx in (-95, 85):
        ell(c, wx, -12, 26, 26); fs(c, "#333333", "#111111", 3); ell(c, wx, -12, 11, 11); setc(c, "#cfcfcf"); c.fill()
        c.save(); c.translate(wx, -12); c.rotate(-t * 8)
        for a in range(4): c.rotate(PI / 2); c.move_to(0, 0); c.line_to(10, 0)
        setc(c, "#888888"); c.set_line_width(2); c.stroke(); c.restore()
    c.restore()
def orange_fruit(c, x, y, s):
    c.save(); c.translate(x, y); c.scale(s, s)
    ell(c, 0, 0, 24, 23); fs(c, "#ff9a1f", "#c86400", 2.5)
    for k in range(6): ell(c, -8 + (k % 3) * 8, -6 + (k // 3) * 10, 1.5, 1.5); setc(c, (0.8, 0.4, 0, 0.5)); c.fill()
    ell(c, 3, -24, 9, 4.5); fs(c, "#3fae4a", "#2a7a33", 1.5); ell(c, -8, -8, 6, 8); setc(c, (1, 1, 1, 0.45)); c.fill(); c.restore()
def pumpkin(c, x, y, s):
    c.save(); c.translate(x, y); c.scale(s, s)
    ell(c, 0, 4, 64, 10); setc(c, (0, 0, 0, 0.18)); c.fill()
    for dx, r in ((-34, 30), (34, 30), (-16, 34), (16, 34), (0, 36)):
        ell(c, dx, -32, r, 32); fs(c, "#ff8c1a", "#b85a00", 2.5)
    rrect(c, -5, -74, 10, 16, 3); setc(c, "#5e7a24"); c.fill()
    c.move_to(4, -70); c.curve_to(20, -84, 30, -70, 22, -62); setc(c, "#4f9a2a"); c.set_line_width(3); c.stroke()
    ell(c, -18, -46, 6, 10); setc(c, (1, 1, 1, 0.35)); c.fill(); c.restore()
def duckling(c, x, y, s, t, k):
    c.save(); c.translate(x, y + 3 * math.sin(t * 4 + k)); c.scale(s, s)
    ell(c, 0, 4, 34, 8); setc(c, (1, 1, 1, 0.5)); c.fill()
    ell(c, 0, -14, 30, 20); fs(c, "#ffd21a", "#d19a00", 2.5)
    c.move_to(18, -22); c.curve_to(26, -26, 34, -20, 30, -12); setc(c, "#ffd21a"); c.fill()
    ell(c, -18, -40, 18, 17); fs(c, "#ffd21a", "#d19a00", 2.5)
    q = 0.3 + 0.7 * abs(math.sin(t * 7 + k))
    poly(c, [(-34, -42), (-50, -40 - 3 * q), (-34, -36)]); setc(c, "#ff8c1a"); c.fill()
    poly(c, [(-34, -38), (-48, -36 + 3 * q), (-34, -35)]); setc(c, "#e06a00"); c.fill()
    ell(c, -24, -45, 3.5, 4); setc(c, "#222222"); c.fill()
    c.move_to(-4, -14); c.curve_to(8, -24, 16, -18, 12, -8); setc(c, "#e6b800"); c.set_line_width(3); c.stroke(); c.restore()
def sunflower(c, x, y, s, t, k):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.move_to(0, 0); c.line_to(0, -90); setc(c, "#3f9e3f"); c.set_line_width(6); c.stroke()
    ell(c, 12, -40, 14, 6); fs(c, "#4cbf4a"); c.translate(0, -100); c.rotate(0.1 * math.sin(t * 2 + k))
    for i in range(12): c.save(); c.rotate(i * PI / 6); ell(c, 0, -26, 8, 16); fs(c, "#ffd21a", "#e0a000", 1.5); c.restore()
    ell(c, 0, 0, 17, 17); fs(c, "#7a4a24", "#5a3214", 2); c.restore()
def frog(c, x, y, s, t, k):
    c.save(); c.translate(x, y); c.scale(s, s)
    ell(c, 0, -18, 30, 20); fs(c, "#3fc24a", "#1f7a2a", 2.5)
    for sx in (-1, 1):
        ell(c, sx * 24, -6, 12, 8); fs(c, "#36ad40", "#1f7a2a", 2)
        ell(c, sx * 14, -38, 11, 11); fs(c, "#3fc24a", "#1f7a2a", 2.5); ell(c, sx * 14, -39, 6, 6); fs(c, "#ffffff"); ell(c, sx * 14, -38, 3, 3); setc(c, "#111111"); c.fill()
    c.arc(0, -20, 12, 0.15 * PI, 0.85 * PI); setc(c, "#1f6a24"); c.set_line_width(2.5); c.stroke()
    ell(c, 0, -10, 16, 8); setc(c, (1, 1, 0.8, 0.5)); c.fill(); c.restore()
def big_leaf(c, x, y, s, ang):
    c.save(); c.translate(x, y); c.rotate(ang); c.scale(s, s)
    c.move_to(0, 0); c.curve_to(30, -20, 40, -60, 0, -90); c.curve_to(-40, -60, -30, -20, 0, 0); fs(c, "#2fbf4a", "#1a7a2a", 2.5)
    c.move_to(0, -4); c.line_to(0, -82); setc(c, "#1a8a30"); c.set_line_width(2); c.stroke(); c.restore()
def fish(c, x, y, s, ang, col):
    c.save(); c.translate(x, y); c.rotate(ang); c.scale(s, s)
    poly(c, [(26, 0), (50, -20), (46, 0), (50, 20)]); fs(c, col, dark(col, 0.7), 2.5)
    ell(c, 0, 0, 32, 20); fs(c, light(col, 0.15), dark(col, 0.7), 2.5)
    ell(c, -16, -5, 6, 6); fs(c, "#ffffff", "#333333", 1.5); ell(c, -17, -5, 3, 3); setc(c, "#222222"); c.fill(); c.restore()
def star5(c, x, y, r, col, a=1.0):
    pts = [((r if i % 2 == 0 else r * 0.45) * math.cos(-PI / 2 + i * PI / 5) + x, (r if i % 2 == 0 else r * 0.45) * math.sin(-PI / 2 + i * PI / 5) + y) for i in range(10)]
    poly(c, pts); setc(c, hexc(col, a) if isinstance(col, str) else col); c.fill()
def butterfly(c, x, y, s, t, k, col="#9b3fd6"):
    c.save(); c.translate(x, y); c.scale(s, s); f = abs(math.sin(t * 9 + k))
    for sgn in (-1, 1):
        c.save(); c.scale(sgn * (0.35 + 0.65 * f), 1)
        ell(c, 22, -12, 24, 20); fs(c, col, dark(col, 0.6), 2.5); ell(c, 18, 14, 15, 13); fs(c, light(col, 0.35), dark(col, 0.6), 2.5)
        ell(c, 24, -12, 7, 7); setc(c, (1, 1, 1, 0.6)); c.fill(); c.restore()
    rrect(c, -4, -22, 8, 42, 4); setc(c, "#3a2050"); c.fill()
    c.move_to(-2, -20); c.line_to(-10, -34); c.move_to(2, -20); c.line_to(10, -34); setc(c, "#3a2050"); c.set_line_width(2); c.stroke(); c.restore()
def plum(c, x, y, s):
    c.save(); c.translate(x, y); c.scale(s, s)
    ell(c, 0, 0, 20, 22); fs(c, "#8a2fc0", "#4e1470", 2.5); c.move_to(0, -20); c.curve_to(-4, -6, -4, 8, 0, 20); setc(c, (0.3, 0.05, 0.4, 0.5)); c.set_line_width(2); c.stroke()
    ell(c, 6, -24, 8, 4); fs(c, "#3fae4a", "#2a7a33", 1.5); ell(c, -8, -8, 5, 8); setc(c, (1, 1, 1, 0.45)); c.fill(); c.restore()
def violet_flower(c, x, y, s, t, k):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.move_to(0, 0); c.line_to(0, -50); setc(c, "#3f9e3f"); c.set_line_width(4); c.stroke()
    c.translate(0, -56); c.rotate(0.15 * math.sin(t * 2 + k))
    for i in range(5): ell(c, 13 * math.cos(i * 1.2566), 13 * math.sin(i * 1.2566), 11, 11); fs(c, ["#9b3fd6", "#b45cf0", "#7a2fb0"][k % 3], "#4e1470", 1.5)
    ell(c, 0, 0, 6, 6); setc(c, "#ffe066"); c.fill(); c.restore()
def popin(t, t0, d=0.35):
    q = back(prog(t, t0, t0 + d)); return q if q > 0.02 else 0.0

# ---------------------------------------------------------------- worlds (one per verse)
def ground(c, y, top, bot, t, seed): grass_field(c, y, top, bot, t=t, seed=seed, flowers=True)

def w_orchard(c, t):
    sky(c, [(0, "#3fa8ff"), (0.7, "#a9dcff"), (1, "#eaf7ff")], 470, sun=(1150, 90, 38, "#fff3b0"), rays=1, t=t); clouds(c, t, n=4, seed=3)
    ridge(c, 400, 30, 5, "#9fdc7a", "#7cc65e", 60, 0.6, 520); ground(c, 450, "#8ddc62", "#4fae44", t, 21)
    c.rectangle(0, 470, W, 40); setc(c, "#c9b28a"); c.fill(); c.rectangle(0, 470, W, 4); setc(c, "#e8dcc0"); c.fill()
    for k in range(10): rrect(c, k * 140 + 20, 488, 70, 6, 3); setc(c, "#ffffff"); c.fill()
    ta = word_time("red_a", "apple")
    for i, (tx, ts) in enumerate(((870, 1.0), (1120, 1.1))):
        fruit_tree(c, tx, 470, ts)
        for j, (fx, fy) in enumerate(TREE_FRUIT):
            q = popin(t, ta + (i * 8 + j) * 0.03)
            if q > 0: apple(c, tx + fx * ts, 470 + fy * ts, 1.0 * q)
    tf = word_time("red_b", "fire"); tz = word_time("red_b", "zoom")
    if t > tf - 0.3:
        x = lerp(1500, 860, ease(prog(t, tf - 0.3, tz))) - max(0, t - tz - 1.4) * 900
        fire_truck(c, x, 505, 0.9, t)
def w_farm(c, t):
    sky(c, [(0, "#ff9a3c"), (0.55, "#ffc27a"), (1, "#ffe3b0")], 470, sun=(980, 330, 60, "#ffd27a"), rays=1, t=t); clouds(c, t, 0.8, warm=True, n=4, seed=8)
    ridge(c, 420, 25, 9, "#e8a25a", "#d48a40", 70, 0.5, 520); ground(c, 450, "#b8d85a", "#7aa83a", t, 31)
    for k in range(14):   # fence
        x = 640 + k * 50; rrect(c, x, 410, 12, 70, 3); fs(c, "#c98a4a", "#7a4a24", 2)
    c.rectangle(640, 425, 660, 10); setc(c, "#b07a3a"); c.fill(); c.rectangle(640, 455, 660, 10); c.fill()
    to = word_time("orange_a", "orange", 0); tp = word_time("orange_b", "pumpkin")
    fruit_tree(c, 1110, 470, 1.15, ("#4caf3f", "#3a8a30", "#6fcf4a"))
    for j, (fx, fy) in enumerate(TREE_FRUIT):
        q = popin(t, to + j * 0.04)
        if q > 0: orange_fruit(c, 1110 + fx * 1.15, 470 + fy * 1.15, q)
    for k, (px, py, s) in enumerate(((820, 560, 1.0), (960, 545, 0.8), (1080, 575, 1.2), (1210, 550, 0.85))):
        q = popin(t, tp + k * 0.09)
        if q > 0: pumpkin(c, px, py, s * q)
def w_pond(c, t):
    ts = word_time("yellow_a", "sunshine"); rise = ease(prog(t, ts - 0.2, ts + 0.6))
    sky(c, [(0, lerp_col("#7cc4ff", "#3fb0ff", rise)), (0.7, "#c8ecff"), (1, "#fffbe0")], 470, sun=(1060, lerp(420, 110, rise), 50 + 14 * rise, "#ffe94d"), rays=2 * rise, t=t)
    clouds(c, t, n=3, seed=12); ground(c, 440, "#9be06a", "#5cb84a", t, 41)
    for k in range(12): sunflower(c, 40 + k * 110 + (k % 2) * 30, 470, 0.8 + 0.1 * (k % 3), t, k)
    ell(c, 1040, 545, 260, 70); c.set_source(lin(c, 0, 475, 0, 615, [(0, "#7fd4ff"), (1, "#3aa0e0")])); c.fill()
    for k in range(5): ell(c, 900 + k * 70, 535 + (k % 2) * 25, 26, 4); setc(c, (1, 1, 1, 0.5 + 0.3 * math.sin(t * 3 + k))); c.fill()
    td = word_time("yellow_b", "duckling")
    for k in range(4):
        q = popin(t, td + k * 0.12)
        if q > 0: duckling(c, 870 + k * 95 + 20 * math.sin(t * 0.8 + k), 545 + (k % 2) * 18, (1.15 if k == 0 else 0.75) * q, t, k)
def lerp_col(a, b, x):
    A, Bc = hexc(a), hexc(b); return "#%02x%02x%02x" % tuple(int(255 * lerp(A[i], Bc[i], x)) for i in range(3))
def w_jungle(c, t):
    sky(c, [(0, "#5fc8ff"), (1, "#d8f5d0")], 470, sun=(200, 90, 34, "#fff6b0"), rays=1, t=t)
    for k, (y, col) in enumerate(((330, "#3e9a4a"), (380, "#2f8a3e"))): ridge(c, y, 40, 11 + k, col, dark(col, 0.85), 30, 1.0, 520)
    treeline(c, 440, 55, "#3fae4a", n=40); ground(c, 450, "#6fd04a", "#2f9a3a", t, 51)
    fruit_tree(c, 1130, 470, 1.4, ("#2f9a3a", "#237a2e", "#4fc04a"))
    tl = word_time("green_b", "leaf")
    for k, (lx, ly, a) in enumerate(((1040, 220, -0.7), (1110, 170, -0.2), (1190, 180, 0.4), (1250, 250, 0.9), (1070, 300, -1.1), (1220, 320, 1.2))):
        q = popin(t, tl + k * 0.06)
        if q > 0: big_leaf(c, lx, ly, 0.8 * q, a + 0.08 * math.sin(t * 2 + k))
    ell(c, 960, 560, 200, 40); c.set_source(lin(c, 0, 520, 0, 600, [(0, "#4fc8b8"), (1, "#2a9a8a")])); c.fill()
    for k, (px, py) in enumerate(((850, 555), (960, 570), (1070, 550))): ell(c, px, py, 44, 12); fs(c, "#3fbf4a", "#1f7a2a", 2)
    tg = word_time("green_a", "grass"); tf = word_time("green_a", "froggies")
    for k in range(18):   # grass shoots pop on "grass"
        q = popin(t, tg + k * 0.02)
        if q > 0:
            x = 30 + k * 72; c.move_to(x - 10, 640); c.curve_to(x - 8, 640 - 40 * q, x - 2, 640 - 60 * q, x + 4, 640 - 72 * q); c.curve_to(x + 2, 640 - 40 * q, x + 6, 640 - 20 * q, x + 10, 640)
            setc(c, "#2fbf4a"); c.fill()
    for k, (px, py) in enumerate(((850, 555), (960, 570), (1070, 550))):
        q = popin(t, tf + k * 0.1)
        if q > 0:
            hp = max(0, math.sin(PI * ((t / B) % 1))) * 40 if t > tf + 0.4 else 0
            frog(c, px, py - hp, 1.0 * q, t, k)
def w_sea(c, t):
    tsk = word_time("blue_a", "sky"); q = ease(prog(t, tsk - 0.1, tsk + 0.5))
    sky(c, [(0, lerp_col("#8fd0ff", "#1f7bff", q)), (1, "#d8f0ff")], 380, sun=(1100, 90, 36, "#fffbd0"), rays=1, t=t)
    clouds(c, t, 0.6 + 0.4 * q, n=5, seed=15); birds(c, t, int(5 * q), 4)
    c.set_source(lin(c, 0, 380, 0, 560, [(0, "#2f8bff"), (1, "#1a5fd0")])); c.rectangle(0, 380, W, 180); c.fill()
    for row in range(5):
        y = 400 + row * 34; c.move_to(0, y)
        for x in range(0, W + 40, 40): c.line_to(x, y + 6 * math.sin(x * 0.03 + t * 2 + row))
        setc(c, (1, 1, 1, 0.25 + 0.05 * row)); c.set_line_width(3); c.stroke()
    c.move_to(0, 545); c.curve_to(400, 520, 800, 560, W, 530); c.line_to(W, H); c.line_to(0, H); c.close_path()
    c.set_source(lin(c, 0, 530, 0, H, [(0, "#ffe7a8"), (1, "#f2c97a")])); c.fill()
    for k in range(12): ell(c, 60 + k * 110, 600 + (k % 3) * 30, 4, 3); setc(c, "#e0b060"); c.fill()
    tfi = word_time("blue_b", "fishes")
    for k in range(5):
        t0 = tfi + k * 0.25
        if t >= t0:
            p = ((t - t0) % 2.2) / 1.1
            if p <= 1:
                x0 = 760 + k * 100; x = x0 + 90 * p; y = 440 - 170 * math.sin(PI * p)
                fish(c, x, y, 0.9, -1.2 + 2.4 * p, ["#2f8bff", "#ff8c1a", "#ffd21a", "#ff5f8f", "#14b3b3"][k])
def w_night(c, t):
    tn = word_time("indigo_a", "night"); q = ease(prog(t, tn - 0.2, tn + 0.6))
    sky(c, [(0, lerp_col("#5a6ad8", "#1a1460", q)), (0.7, lerp_col("#8f8fe8", "#3a2fa0", q)), (1, "#6a5fd0")], 500, sun=(1080, 110, 46, "#fff7cf"), rays=0, t=t)
    r = random.Random(4)
    for k in range(60):
        x, y = r.uniform(0, W), r.uniform(20, 380); tw = 0.6 + 0.4 * math.sin(t * 3 + k)
        qq = popin(t, tn + r.uniform(0, 0.8), 0.3)
        if qq > 0: star5(c, x, y, r.uniform(4, 10) * qq, (1, 1, 0.8, tw))
    ridge(c, 440, 40, 21, "#2a2a8a", "#1f1f6a", 60, 0.7, 560); ground(c, 470, "#2f6a6a", "#1f4a4a", t, 61)
    for k in range(5):
        x = (k * 260 + t * 30) % 1400 - 60; y = 160 + 40 * math.sin(t + k)
        c.arc(x, y, 3, 0, 2 * PI); setc(c, (1, 1, 0.5, 0.6 + 0.4 * math.sin(t * 5 + k))); c.fill()   # fireflies
    tb = word_time("indigo_b", "blanket"); qb = popin(t, tb)
    if qb > 0:
        c.save(); c.translate(1010, 580); c.scale(qb, qb)
        ell(c, 0, 10, 190, 20); setc(c, (0, 0, 0, 0.25)); c.fill()
        c.move_to(-180, -10); c.curve_to(-60, -40, 60, -40, 180, -10); c.line_to(170, 20); c.curve_to(60, 30, -60, 30, -170, 20); c.close_path(); fs(c, "#4b3cc4", "#2a1f80", 3)
        for k in range(5): star5(c, -120 + k * 60, -6, 8, "#ffd23f")
        c.restore()
def w_garden(c, t):
    sky(c, [(0, "#b98aff"), (0.7, "#e6d0ff"), (1, "#fff0fa")], 470, sun=(1120, 100, 36, "#fff3f0"), rays=1, t=t); clouds(c, t, n=4, seed=19)
    ridge(c, 410, 30, 23, "#c3a0f0", "#a888e0", 60, 0.6, 520); ground(c, 450, "#9be06a", "#5cb84a", t, 71)
    for k in range(22): violet_flower(c, 20 + k * 60, 470 + (k % 3) * 8, 0.9, t, k)
    fruit_tree(c, 1110, 480, 1.1, ("#4caf3f", "#3a8a30", "#6fcf4a"))
    tp = word_time("violet_b", "plum")
    for j, (fx, fy) in enumerate(TREE_FRUIT):
        q = popin(t, tp + j * 0.04)
        if q > 0: plum(c, 1110 + fx * 1.1, 480 + fy * 1.1, q)
    tbf = word_time("violet_a", "butterfly")
    for k in range(5):
        q = popin(t, tbf + k * 0.1)
        if q > 0:
            x = 700 + k * 120 + 40 * math.sin(t * 1.3 + k); y = 200 + 60 * math.sin(t * 1.7 + k * 2)
            butterfly(c, x, y, 0.9 * q, t, k, ["#9b3fd6", "#b45cf0", "#7a2fb0", "#c77dff", "#8a2fc0"][k])
WORLDS = {"orchard": w_orchard, "farm": w_farm, "pond": w_pond, "jungle": w_jungle, "sea": w_sea, "night": w_night, "garden": w_garden}

# ---------------------------------------------------------------- rainbow (chorus) world
def rainbow_world(c, t, sec):
    sky(c, [(0, "#3fa8ff"), (0.7, "#b0e0ff"), (1, "#f0fbff")], 500, sun=(1150, 95, 36, "#fff3b0"), rays=1.2, t=t)
    clouds(c, t, n=4, seed=6)
    tag = sec[5]
    if tag:
        times = [word_time(f"{tag}_0", w) for w in ("Red", "orange", "yellow", "green")] + [word_time(f"{tag}_1", w) for w in ("Blue", "indigo", "violet")]
    else:
        times = [-10] * 7
    first = tag == "ch1"
    for i, col in enumerate(RAIN):
        r = 470 - i * 28
        p = ease(prog(t, times[i] - 0.05, times[i] + 0.45)) if first else 1.0
        if p <= 0: continue
        glow = math.exp(-max(0, t - times[i]) * 2.2) if t >= times[i] - 0.05 else 0
        c.new_path(); c.arc(640, 560, r, PI, PI + PI * p)
        setc(c, hexc(col, 0.85)); c.set_line_width(28 + 10 * glow); c.stroke()
        if glow > 0.02:
            c.new_path(); c.arc(640, 560, r, PI, 2 * PI); setc(c, (1, 1, 1, 0.45 * glow)); c.set_line_width(10); c.stroke()
    for cx in (175, 1105): cloud(c, cx - 60, 545, 1.5)
    ridge(c, 520, 18, 2, "#9fdc7a", "#86d06a", 60, 0.5, 600); ground(c, 540, "#8ddc62", "#4fae44", t, 12)
    for i, col in enumerate(RAIN):   # colour bubbles fly up when sung
        if times[i] - 0.05 <= t <= times[i] + 2.4:
            lt = t - times[i]; q = back(prog(lt, 0, 0.3))
            if q < 0.02: continue
            x = 160 + i * 160; y = 215 - lt * 45
            c.save(); c.translate(x, y); c.scale(q, q)
            ell(c, 0, 0, 62, 62); fs(c, col, "#ffffff", 6)
            ell(c, -20, -24, 16, 10); setc(c, (1, 1, 1, 0.5)); c.fill()
            name = ["Red", "Orange", "Yellow", "Green", "Blue", "Indigo", "Violet"][i]
            draw_text(c, name, 0, 2, 30 if len(name) > 5 else 34, "#ffffff", dark(col, 0.6), 4, lang="en")
            c.restore()

# ---------------------------------------------------------------- big colour word card in every verse
def color_card(c, t, key, colsyl, t0):
    q = back(prog(t, t0 - 0.05, t0 + 0.35))
    if q < 0.02: return
    ph = (t / B) % 1; puls = 1 + 0.05 * math.sin(PI * ph) ** 4
    word = "".join(colsyl).upper(); col = COL[key]
    c.save(); c.translate(330, 115); c.scale(q * puls, q * puls)
    c.select_font_face("Fredoka", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); c.set_font_size(96)
    tw = c.text_extents(word).x_advance
    rrect(c, -tw / 2 - 40, -70, tw + 80, 140, 70); fs(c, "#ffffff", col, 9)
    draw_text(c, word, 0, 4, 96, col, dark(col, 0.6), 4, lang="en")
    c.restore()

def echo_words(c, t, key, colsyl, cue):
    l = LBY[cue]; word = "".join(colsyl).upper(); col = COL[key]
    for k in range(3):
        t0 = _WT[cue][k][1] if SPOKEN else T(l["beat"] + k)
        if t < t0 - 0.05: continue
        q = back(prog(t, t0 - 0.05, t0 + 0.25))
        if q < 0.02: continue
        hop = 20 * math.sin(PI * clamp((t - t0) / 0.4))
        c.save(); c.translate(260 + k * 380, 140 - hop); c.scale(q, q); c.rotate((k - 1) * 0.12)
        draw_text(c, word + "!", 0, 0, 74, col, "#ffffff", 9, lang="en"); c.restore()

# ---------------------------------------------------------------- title + outro cards
def title_card(c, t):
    gr = cairo.RadialGradient(640, 380, 40, 640, 380, 900); gr.add_color_stop_rgba(0, *hexc("#fff6a8")); gr.add_color_stop_rgba(1, *hexc("#4fb8ff")); c.set_source(gr); c.paint()
    c.save(); c.translate(640, 380); c.rotate(t * 0.15)
    for i in range(18): c.move_to(0, 0); c.arc(0, 0, 1200, i * PI / 9, i * PI / 9 + PI / 18); c.close_path(); setc(c, (1, 1, 1, 0.18)); c.fill()
    c.restore()
    for i, col in enumerate(RAIN):
        p = ease(prog(t, 0.3 + i * 0.12, 1.0 + i * 0.12))
        if p > 0: c.new_path(); c.arc(640, 720, 640 - i * 30, PI, PI + PI * p); setc(c, hexc(col, 0.8)); c.set_line_width(30); c.stroke()
    ph = (t / B) % 1; puls = 1 + 0.04 * math.sin(PI * ph) ** 4
    p = back(prog(t, 0.2, 0.8))
    if p > 0: c.save(); c.translate(640, 120); c.scale(p * puls, p * puls); draw_text(c, "Tinku & Friends", 0, 0, 100, "#ff6b1a", "#ffffff", 11, lang="en"); c.restore()
    p2 = back(prog(t, 0.9, 1.4))
    if p2 > 0:
        c.save(); c.translate(640, 232); c.scale(p2, p2)
        rrect(c, -330, -42, 660, 84, 42); fs(c, "#9b3fd6", "#ffffff", 6)
        draw_text(c, f"Episode {EP_NUM} · {EP_TITLE}", 0, 0, 40, "#ffffff", lang="en"); c.restore()
    for i, (fn, x, nm) in enumerate(((tinku, 360, "tinku"), (pinky, 560, "pinky"), (golu, 750, "golu"))):
        q = back(prog(t, 1.2 + i * 0.2, 1.7 + i * 0.2)); arms, h, lean = dance(nm, t, "title", seed=i)
        fn(c, x, 940 - 290 * q, t, 0.8, arms, 0, 0, blink(t, i), h)
    q = back(prog(t, 1.8, 2.3)); moti(c, 930, 900 - 250 * q, t, 0.8, 0, -0.3, False, abs(math.sin(PI * (t / B))) * 14, 2.5)

def outro_card(c, t, t0):
    lt = t - t0
    gr = cairo.RadialGradient(640, 380, 40, 640, 380, 900); gr.add_color_stop_rgba(0, *hexc("#fff3c4")); gr.add_color_stop_rgba(1, *hexc("#ff9fcf")); c.set_source(gr); c.paint()
    r = random.Random(5)
    for k in range(60):
        x0 = r.uniform(0, W); sp = r.uniform(60, 130); ph = r.uniform(0, 800)
        y = (ph + lt * sp) % 800 - 40; x = x0 + 20 * math.sin(lt * 2 + k)
        c.save(); c.translate(x, y); c.rotate(lt * 2 + k); rrect(c, -6, -3, 12, 6, 2); setc(c, RAIN[k % 7]); c.fill(); c.restore()
    p = back(prog(lt, 0.1, 0.6))
    if p > 0: c.save(); c.translate(640, 140); c.scale(p, p); draw_text(c, "Bye-bye!", 0, 0, 130, "#d81b60", "#ffffff", 12, lang="en"); c.restore()
    p2 = back(prog(lt, 0.5, 1.0))
    if p2 > 0:
        c.save(); c.translate(640, 262); c.scale(p2, p2); draw_text(c, "See you next time!", 0, 0, 46, "#7c2d12", "#ffffff", 5, lang="en")
        draw_text(c, NEXT, 0, 58, 36, "#2f7bff", "#ffffff", 4, lang="en"); c.restore()
    for i, (fn, x, nm) in enumerate(((tinku, 360, "tinku"), (pinky, 560, "pinky"), (golu, 750, "golu"))):
        arms, h, lean = dance(nm, t, "card", seed=i); fn(c, x, 680, t, 0.8, arms, 0, 0, blink(t, i), h)
    moti(c, 930, 680, t, 0.8, 0, -0.3, False, abs(math.sin(PI * (t / B))) * 14, 2.5)

# ---------------------------------------------------------------- lyrics caption
def note_glyph(c, x, y, col, t):
    c.save(); c.translate(x, y + 2 * math.sin(t * 6)); c.rotate(0.1 * math.sin(t * 4))
    ell(c, -5, 8, 8, 6); setc(c, col); c.fill(); c.rectangle(1, -14, 3.5, 22); c.fill()
    c.move_to(4.5, -14); c.curve_to(14, -10, 14, -2, 10, 2); c.set_line_width(3); c.stroke(); c.restore()
def captions(c, t):
    cur = None
    for i, l in enumerate(LINES):
        a = T(l["beat"]) - 0.25; nxt = T(LINES[i + 1]["beat"]) - 0.25 if i + 1 < len(LINES) else 1e9
        end = T(l["beat"] + sum(sum(d for _, d in n) for _, n in l["notes"])) + 0.3
        if a <= t <= min(end, nxt): cur = l
    if not cur: return
    al = clamp((t - T(cur["beat"]) + 0.25) / 0.15)
    name, col = NAMES[cur["spk"]]
    txt = cur["cap"]
    c.select_font_face("Fredoka", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); c.set_font_size(34)
    tw = c.text_extents(txt).x_advance
    bw = tw + 120; bh = 58; bx, by = 640 - bw / 2, 706 - bh
    c.push_group()
    rrect(c, bx + 3, by + 5, bw, bh, 22); setc(c, (0.1, 0.05, 0.2, 0.25)); c.fill()
    rrect(c, bx, by, bw, bh, 22); fs(c, (1, 1, 1, 0.95), hexc(col), 5)
    nw = text_surface(name, 24, "#ffffff", None, 0, "en").get_width()
    rrect(c, bx + 18, by - 22, nw + 24, 38, 19); fs(c, col, (1, 1, 1, 1), 3)
    draw_text(c, name, bx + 30, by - 3, 24, "#ffffff", None, 0, lang="en", anchor="l")
    c.select_font_face("Fredoka", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); c.set_font_size(34)
    c.move_to(640 - tw / 2, by + 41); setc(c, "#2b2d42"); c.show_text(txt)
    for nx in (bx + 30, bx + bw - 30):
        if not SPOKEN: note_glyph(c, nx, by + 30, col, t)
    c.pop_group_to_source(); c.paint_with_alpha(al)

# ---------------------------------------------------------------- scene for a section
def scene(c, t, sec):
    sb, nb, kind, sc, chords, info = sec
    t0, t1 = sec_t(sec)
    if kind == "intro": title_card(c, t); return
    if kind == "card": outro_card(c, t, t0); return
    # camera: slow push-in per section + a small kick on every downbeat
    ph_bar = ((t / B) % BAR) / BAR
    zoom = 1.0 + 0.05 * ease(prog(t, t0, t1)) + 0.012 * math.exp(-ph_bar * 10)
    c.save(); c.translate(640, 420); c.scale(zoom, zoom); c.translate(-640, -420)
    if kind in ("chorus", "outro"):
        rainbow_world(c, t, sec)
        k = "chorus" if kind == "chorus" else "outro"
        if kind == "outro" and t >= word_time("bye", "Bye"): k = "card"
        gang(c, t, k, xs=(330, 530, 720, 900), s=0.8, gy=GY)
    else:
        key = info; i = [k_[0] for k_ in COLORS].index(key); _, colsyl, _, singer, *_ = COLORS[i]
        WORLDS[sc](c, t)
        bar_in = int((t - t0) / (B * BAR))
        k = "verse" if bar_in < 4 else "echo" if bar_in == 4 else "fill"
        hide = key == "indigo" and word_time("indigo_b", "Mohtee") - 0.2 <= t < T((sb + 5) * BAR)
        gang(c, t, k, lead=singer if k == "verse" else None, hide_moti=hide)
        if hide:
            c.save(); c.translate(1010, 560); moti(c, 0, 0, t, 0.7, 0, 0.0, True, 0, 0.3); c.restore()
            for z in range(3):
                zt = (t * 0.8 + z / 3) % 1
                draw_text(c, "z", 1060 + 30 * zt + z * 6, 400 - 80 * zt, 30 + 14 * zt, "#ffffff", "#4b3cc4", 3, lang="en", alpha=1 - zt)
    c.restore()
    if kind == "verse":
        if k != "echo": color_card(c, t, key, colsyl, T(LBY[f"{key}_a"]["beat"]))
        else: echo_words(c, t, key, colsyl, f"{key}_echo")

def frame(t, surf=None):
    surf = surf or cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(surf)
    sec = section_at(t); t0, _ = sec_t(sec)
    idx = SECTIONS.index(sec)
    p = ease(prog(t, t0 - 0.0, t0 + 0.5))
    if idx > 0 and p < 1:   # colourful circle wipe into each new world
        scene(c, t, SECTIONS[idx - 1])
        col = COL.get(sec[5], "#ffd23f") if sec[2] == "verse" else "#ffd23f"
        c.save(); c.arc(640, 360, 760 * p, 0, 2 * PI); c.clip(); scene(c, t, sec); c.restore()
        c.arc(640, 360, 760 * p, 0, 2 * PI); setc(c, col); c.set_line_width(16); c.stroke()
    else:
        scene(c, t, sec)
    captions(c, t)
    f = clamp(min(t / 0.4, (DURATION - t) / 1.5))
    if f < 1: c.rectangle(0, 0, W, H); setc(c, (0, 0, 0, 1 - f)); c.fill()
    return surf

if __name__ == "__main__":
    os.makedirs("stills", exist_ok=True)
    for ts in sys.argv[1:]: frame(float(ts)).write_to_png(f"stills/f_{float(ts):06.2f}.png")
