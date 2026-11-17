import math, random, numpy as np, soundfile as sf, cairo
from cues import *

W, H, FPS = 1280, 720, 30
PI = math.pi
FONT = "Fredoka"
TITLE_FONT = "Baloo 2"

# ---------------------------------------------------------------- helpers
def hexc(h, a=1.0):
    h = h.lstrip("#"); return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)

def dark(h, k=0.78):
    r, g, b, a = hexc(h); return (r * k, g * k, b * k, a)

def setc(c, col):
    if isinstance(col, str): col = hexc(col)
    c.set_source_rgba(*col)

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def prog(t, a, b): return clamp((t - a) / (b - a)) if b > a else float(t >= a)
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def back(x, s=1.9):
    x = clamp(x); x -= 1; return x * x * ((s + 1) * x + s) + 1
def lerp(a, b, x): return a + (b - a) * x

def hop(t, t0, h=40, d=0.45):
    return h * math.sin(PI * (t - t0) / d) if t0 <= t <= t0 + d else 0.0

def ell(c, x, y, rx, ry):
    c.save(); c.translate(x, y); c.scale(max(rx, 0.01), max(ry, 0.01)); c.arc(0, 0, 1, 0, 2 * PI); c.restore()

def rrect(c, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    c.new_sub_path(); c.arc(x + w - r, y + r, r, -PI / 2, 0); c.arc(x + w - r, y + h - r, r, 0, PI / 2)
    c.arc(x + r, y + h - r, r, PI / 2, PI); c.arc(x + r, y + r, r, PI, 1.5 * PI); c.close_path()

def fs(c, col, outline=None, lw=3.5):
    setc(c, col)
    if outline is None and isinstance(col, str): outline = dark(col)
    if outline:
        c.fill_preserve(); setc(c, outline); c.set_line_width(lw); c.stroke()
    else:
        c.fill()

def keyed(t, keys):
    if t <= keys[0][0]: return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t <= t1: return lerp(v0, v1, ease(prog(t, t0, t1)))
    return keys[-1][1]

def active(t, cue, pre=0.0, post=0.0):
    return any(l["start"] - pre <= t <= l["end"] + post for l in LINES if l["cue"] == cue)

def font(c, size, bold=True, face=FONT):
    c.select_font_face(face, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    c.set_font_size(size)

# ---------------------------------------------------------------- lip sync
NF = int(DURATION * FPS) + 2
MOUTH = {k: np.zeros(NF) for k in ("narrator", "mia", "benny")}
for l in LINES:
    x, sr = sf.read(l["file"]); hop_n = sr // FPS
    rms = np.array([np.sqrt((x[i:i + hop_n] ** 2).mean()) for i in range(0, len(x) - hop_n, hop_n)])
    rms = np.clip(rms / (np.percentile(rms, 90) + 1e-6), 0, 1.2)
    f0 = int(l["start"] * FPS)
    MOUTH[l["speaker"]][f0:f0 + len(rms)] = rms[: NF - f0]
for k in MOUTH:
    MOUTH[k] = np.convolve(MOUTH[k], [0.25, 0.5, 0.25], "same")

def mouth(spk, t):
    i = int(t * FPS); return float(MOUTH[spk][i]) if 0 <= i < NF else 0.0

def blink(t, off):
    return ((t + off) % 3.7) < 0.12

# ---------------------------------------------------------------- world layout
CAMX = 900
GROUND_Y = 560
HOLES = [900 + x for x in (400, 520, 640, 760, 880)]
HOLE_Y = 538
FLOWER_COLS = ["#ff3b3b", "#ff8c1a", "#ffd60a", "#2f7bff", "#a04dff"]
FLOWER_H = [150, 185, 165, 190, 155]
MIA_HOME, BEN_HOME = 900 + 250, 900 + 1030

def camx(t): return lerp(0, CAMX, ease(prog(t, T_PAN0, T_PAN1)))

rnd = random.Random(3)
GRASS_DOTS = [(rnd.uniform(-200, 2400), rnd.uniform(575, 720), rnd.choice(["#ffffff", "#ffe14d", "#ff8fc7"]), rnd.uniform(3, 6)) for _ in range(90)]
CLOUDS = [(80, 90, 1.0), (520, 60, 0.8), (900, 130, 1.1), (1350, 80, 0.9), (1800, 110, 1.0)]

# ---------------------------------------------------------------- characters
SKIN = "#c98b5a"; HAIR = "#3b2416"; DRESS = "#ffd23f"
SPOUT = [(0, 0)]
FUR = "#f6f1ff"; FUR_OL = (0.74, 0.69, 0.86, 1)

def arm(c, sx, sy, ang, length, col, w=17, hand=None, ext=0.8):
    length = length * (1 + ext * clamp((abs(ang) - 1.6) / 1.0))
    ex = sx + math.sin(ang) * length; ey = sy + math.cos(ang) * length
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(sx, sy); c.line_to(ex, ey); setc(c, dark(col, 0.8)); c.set_line_width(w + 5); c.stroke()
    c.move_to(sx, sy); c.line_to(ex, ey); setc(c, col); c.set_line_width(w); c.stroke()
    ell(c, ex, ey, w * 0.72, w * 0.72); fs(c, hand or col)
    return ex, ey

def eyes(c, xs, y, rx, ry, look, closed, pr=None):
    for ex in xs:
        if closed:
            c.set_line_width(4.5); setc(c, "#2b1b10"); c.arc(ex, y, rx * 0.8, 0.15 * PI, 0.85 * PI); c.stroke()
        else:
            ell(c, ex, y, rx, ry); fs(c, "#ffffff", (0.35, 0.25, 0.2, 1), 2.5)
            px = ex + look * rx * 0.35; py = y + ry * 0.15
            ell(c, px, py, pr or rx * 0.68, (pr or rx * 0.68) * 1.08); setc(c, "#2b1b10"); c.fill()
            ell(c, px + 4, py - 5, 4.2, 4.2); setc(c, "#ffffff"); c.fill()
            ell(c, px - 3, py + 4, 2, 2); setc(c, "#ffffff"); c.fill()


def mia(c, x, y, t, s=1.0, arms=(0.25, 0.25), m=0.0, look=1, stretch=1.0, lean=0.0, hold=None, closed=False, hopy=0.0):
    c.save(); c.translate(x, y)
    # shadow
    k = 1 - clamp(hopy / 160)
    ell(c, 0, 2, 62 * s * k, 11 * s * k); setc(c, (0, 0, 0, 0.16 * k)); c.fill()
    c.translate(0, -hopy); c.scale(s, s * stretch); c.rotate(lean)
    # legs + shoes
    for lx in (-22, 22):
        rrect(c, lx - 10, -78, 20, 72, 9); fs(c, SKIN)
        ell(c, lx + (3 if lx > 0 else -3), -8, 24, 13); fs(c, "#ff4f6d")
    # back hair
    ell(c, 0, -268, 92, 90); fs(c, HAIR)
    for px in (-96, 96):
        ell(c, px, -300, 44, 44); fs(c, HAIR)
    # dress
    c.move_to(-44, -196); c.line_to(44, -196)
    c.curve_to(56, -150, 74, -100, 82, -70); c.curve_to(40, -54, -40, -54, -82, -70)
    c.curve_to(-74, -100, -56, -150, -44, -196); c.close_path()
    g = cairo.LinearGradient(0, -196, 0, -60); g.add_color_stop_rgba(0, *hexc("#ffe066")); g.add_color_stop_rgba(1, *hexc("#ffbe1a"))
    c.set_source(g); c.fill_preserve(); setc(c, dark(DRESS, 0.7)); c.set_line_width(3.5); c.stroke()
    # hem stripe + pocket flower
    c.move_to(-79, -80); c.curve_to(-40, -66, 40, -66, 79, -80); setc(c, "#ff5fa2"); c.set_line_width(6); c.stroke()
    for a in range(5):
        ell(c, 30 + 8 * math.cos(a * 2 * PI / 5), -112 + 8 * math.sin(a * 2 * PI / 5), 6, 6); setc(c, "#ff5fa2"); c.fill()
    ell(c, 30, -112, 4.5, 4.5); setc(c, "#ffffff"); c.fill()
    # collar
    for sx in (-1, 1):
        c.move_to(0, -196); c.curve_to(sx * 10, -178, sx * 30, -176, sx * 38, -194); c.close_path(); fs(c, "#ffffff", (0.8, 0.8, 0.85, 1), 2)
    # head
    c.save(); c.translate(0, -262); c.rotate(math.sin(t * 2.1) * 0.03 + m * 0.05)
    ell(c, -81, 6, 13, 17); fs(c, SKIN); ell(c, 81, 6, 13, 17); fs(c, SKIN)
    ell(c, 0, 0, 82, 80); fs(c, SKIN, dark(SKIN, 0.75))
    # hair cap with bangs
    c.new_path(); c.arc(0, -2, 86, PI * 1.02, PI * 1.98)
    c.curve_to(84, -30, 70, -36, 52, -34); c.curve_to(40, -50, 18, -46, 6, -40)
    c.curve_to(-8, -54, -36, -50, -44, -36); c.curve_to(-62, -40, -82, -30, -86, -4); c.close_path(); fs(c, HAIR)
    ell(c, -30, -64, 22, 8); setc(c, (1, 1, 1, 0.13)); c.fill()
    # bows
    for bx in (-70, 70):
        c.save(); c.translate(bx, -52); c.rotate(0.4 if bx < 0 else -0.4)
        for sgn in (-1, 1):
            c.move_to(0, 0); c.line_to(sgn * 24, -14); c.line_to(sgn * 24, 14); c.close_path(); fs(c, "#ff5fa2", dark("#ff5fa2"), 2.5)
        ell(c, 0, 0, 7, 7); fs(c, "#ff8cc0", dark("#ff5fa2"), 2); c.restore()
    # face
    eyes(c, (-30, 30), 6, 17, 21, look, closed)
    for bx in (-30, 30):
        c.move_to(bx - 14, -26); c.curve_to(bx - 6, -33, bx + 6, -33, bx + 14, -27); setc(c, HAIR); c.set_line_width(4); c.stroke()
    ell(c, -52, 34, 14, 9); setc(c, (1, 0.45, 0.5, 0.45)); c.fill()
    ell(c, 52, 34, 14, 9); setc(c, (1, 0.45, 0.5, 0.45)); c.fill()
    c.move_to(-5, 26); c.curve_to(-2, 30, 2, 30, 5, 26); setc(c, dark(SKIN, 0.6)); c.set_line_width(3); c.stroke()
    if m > 0.1:
        oh = 6 + 20 * min(m, 1.1)
        ell(c, 0, 46 + oh * 0.3, 15 + 4 * m, oh * 0.6); fs(c, "#8a1f33", "#5e1222", 2.5)
        ell(c, 0, 46 + oh * 0.55, 9, oh * 0.25); setc(c, "#ff7a8f"); c.fill()
        rrect(c, -10, 46 + oh * 0.3 - oh * 0.6 + 1, 20, 6, 3); setc(c, "#ffffff"); c.fill()
    else:
        c.move_to(-20, 42); c.curve_to(-10, 56, 10, 56, 20, 42); setc(c, "#8a1f33"); c.set_line_width(4.5); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()
    c.restore()
    # arms
    hands = []
    hands.append(arm(c, -40, -184, -arms[0], 78, SKIN))
    hands.append(arm(c, 40, -184, arms[1], 78, SKIN))
    if hold == "bag":
        hx, hy = hands[0]
        rrect(c, hx - 22, hy - 4, 44, 40, 12); fs(c, "#b97a45")
        c.move_to(hx - 16, hy + 2); c.line_to(hx + 16, hy + 2); setc(c, "#7b4a22"); c.set_line_width(3); c.stroke()
        ell(c, hx, hy + 20, 7, 9); setc(c, "#ffd23f"); c.fill()
    dev = [c.user_to_device(*h) for h in hands]
    c.restore()
    return dev


def benny(c, x, y, t, s=1.0, arms=(0.35, 0.35), m=0.0, look=-1, lean=0.0, ear=0.0, hold=None, face=1, closed=False, hopy=0.0, stretch=1.0):
    c.save(); c.translate(x, y)
    k = 1 - clamp(hopy / 160)
    ell(c, 0, 2, 60 * s * k, 11 * s * k); setc(c, (0, 0, 0, 0.16 * k)); c.fill()
    c.translate(0, -hopy); c.scale(s * face, s * stretch); c.rotate(lean)
    # tail
    for a in range(6):
        ell(c, 60 + 9 * math.cos(a), -70 + 9 * math.sin(a), 16, 16); setc(c, "#ffffff"); c.fill()
    # feet
    for fx in (-30, 30):
        ell(c, fx, -10, 34, 15); fs(c, FUR, FUR_OL)
        ell(c, fx, -8, 14, 7); setc(c, "#ffc2d4"); c.fill()
    # body
    ell(c, 0, -82, 62, 72); fs(c, FUR, FUR_OL)
    ell(c, 0, -72, 40, 48); setc(c, "#fffbf4"); c.fill()
    # bow tie
    for sgn in (-1, 1):
        c.move_to(0, -146); c.line_to(sgn * 24, -160); c.line_to(sgn * 24, -132); c.close_path(); fs(c, "#2f80ed", dark("#2f80ed"), 2.5)
    ell(c, 0, -146, 7, 7); fs(c, "#5aa0ff", dark("#2f80ed"), 2)
    # head
    c.save(); c.translate(0, -205); c.rotate(math.sin(t * 2.4 + 1) * 0.04 + m * 0.05)
    for sgn in (-1, 1):
        c.save(); c.translate(sgn * 30, -48); c.rotate(sgn * (0.18 + ear + 0.05 * math.sin(t * 3 + sgn)))
        ell(c, 0, -52, 21, 58); fs(c, FUR, FUR_OL); ell(c, 0, -48, 10, 42); setc(c, "#ffb3c7"); c.fill()
        c.restore()
    ell(c, 0, 0, 78, 66); fs(c, FUR, FUR_OL)
    eyes(c, (-28, 28), -6, 16, 19, look, closed)
    ell(c, -50, 22, 13, 8); setc(c, (1, 0.5, 0.65, 0.45)); c.fill()
    ell(c, 50, 22, 13, 8); setc(c, (1, 0.5, 0.65, 0.45)); c.fill()
    ell(c, 0, 16, 10, 7); fs(c, "#ff7aa2", "#d9567f", 2)
    c.set_line_width(2.2); setc(c, (0.6, 0.55, 0.7, 0.8))
    for sgn in (-1, 1):
        for dy in (-4, 4):
            c.move_to(sgn * 24, 22 + dy); c.line_to(sgn * 52, 18 + dy * 2.2); c.stroke()
    if m > 0.1:
        oh = 6 + 16 * min(m, 1.1)
        ell(c, 0, 30 + oh * 0.45, 13 + 3 * m, oh * 0.5); fs(c, "#8a1f33", "#5e1222", 2)
        rrect(c, -9, 24, 8, 11, 2); fs(c, "#ffffff", (0.7, 0.7, 0.75, 1), 1.5)
        rrect(c, 1, 24, 8, 11, 2); fs(c, "#ffffff", (0.7, 0.7, 0.75, 1), 1.5)
    else:
        c.set_line_cap(cairo.LINE_CAP_ROUND); setc(c, "#8a4a5f"); c.set_line_width(3.5)
        c.move_to(0, 23); c.line_to(0, 29); c.stroke()
        c.arc(-8, 29, 8, 0.1 * PI, 0.9 * PI); c.stroke(); c.arc(8, 29, 8, 0.1 * PI, 0.9 * PI); c.stroke()
        rrect(c, -7, 31, 14, 9, 2); fs(c, "#ffffff", (0.7, 0.7, 0.75, 1), 1.5)
    c.restore()
    # arms
    hands = [arm(c, -46, -120, -min(arms[0], 2.4), 46, FUR, 15, ext=0.9), arm(c, 46, -120, min(arms[1], 2.4), 46, FUR, 15, ext=0.9)]
    if hold == "can":
        hx, hy = hands[0]
        c.save(); c.translate(hx, hy); c.rotate(-0.55 if active(t, "water", 0, 0.3) else -0.1)
        rrect(c, -36, -6, 60, 46, 10); fs(c, "#22c3a6")
        c.move_to(-34, 6); c.line_to(-70, -16); setc(c, "#1a9e86"); c.set_line_width(9); c.stroke()
        ell(c, -72, -17, 9, 6); fs(c, "#1a9e86")
        SPOUT[0] = c.user_to_device(-74, -14)
        c.arc(-6, -6, 22, PI * 1.05, PI * 1.95); setc(c, "#1a9e86"); c.set_line_width(6); c.stroke()
        c.restore()
    dev = [c.user_to_device(*h) for h in hands]
    c.restore()
    return dev

# ---------------------------------------------------------------- scenery
def sky(c):
    g = cairo.LinearGradient(0, 0, 0, 520)
    g.add_color_stop_rgba(0, *hexc("#3fb8ff")); g.add_color_stop_rgba(1, *hexc("#c6f1ff"))
    c.set_source(g); c.paint()

def cloud(c, x, y, s, a=1.0):
    for dx, dy, r in ((0, 0, 38), (40, -18, 46), (84, 0, 38), (42, 12, 40)):
        ell(c, x + dx * s, y + dy * s, r * s, r * s * 0.9); setc(c, (1, 1, 1, a)); c.fill()

def sun(c, t):
    x, y = 1130, 105
    glow = back(prog(t, S("sun_shine"), S("sun_shine") + 0.8)) * (1 - 0.6 * prog(t, S("sun_shine") + 2.5, S("sun_shine") + 4))
    r = 56 * (1 + 0.25 * glow)
    gr = cairo.RadialGradient(x, y, r * 0.5, x, y, r * (2.3 + glow))
    gr.add_color_stop_rgba(0, 1, 0.95, 0.5, 0.6); gr.add_color_stop_rgba(1, 1, 0.95, 0.5, 0)
    c.set_source(gr); c.arc(x, y, r * (2.3 + glow), 0, 2 * PI); c.fill()
    c.save(); c.translate(x, y); c.rotate(t * (0.25 + 1.5 * glow))
    for i in range(12):
        c.save(); c.rotate(i * PI / 6)
        c.move_to(-11, -r - 6); c.line_to(0, -r - 30 - 10 * glow); c.line_to(11, -r - 6); c.close_path(); setc(c, "#ffc21a"); c.fill(); c.restore()
    c.restore()
    ell(c, x, y, r, r); fs(c, "#ffdc2e", "#ffb000", 4)
    c.set_line_width(4); setc(c, "#a35b00"); c.set_line_cap(cairo.LINE_CAP_ROUND)
    for ex in (-18, 18):
        c.arc(x + ex * r / 56, y - 4, 8, 1.15 * PI, 1.85 * PI); c.stroke()
    c.arc(x, y + 10 * r / 56, 18 * r / 56, 0.15 * PI, 0.85 * PI); c.stroke()
    ell(c, x - 32 * r / 56, y + 12, 9, 6); setc(c, (1, 0.5, 0.4, 0.5)); c.fill()
    ell(c, x + 32 * r / 56, y + 12, 9, 6); setc(c, (1, 0.5, 0.4, 0.5)); c.fill()

def rainbow(c, t):
    p = ease(prog(t, RAINBOW_T, RAINBOW_T + 1.4))
    if p <= 0: return
    cx, cy = 640, 560
    c.save(); c.move_to(cx, cy); c.arc(cx, cy, 700, PI, PI + PI * p); c.close_path(); c.clip()
    for i, col in enumerate(["#ff3b3b", "#ff8c1a", "#ffd60a", "#4cd964", "#2f7bff", "#a04dff"]):
        c.arc(cx, cy, 500 - i * 26, PI, 2 * PI); setc(c, hexc(col, 0.85)); c.set_line_width(27); c.stroke()
    c.restore()

def hills(c, cam):
    c.save(); c.translate(-cam * 0.45, 0)
    for hx, r, col in ((200, 380, "#a5ea85"), (800, 440, "#97e277"), (1450, 420, "#a5ea85"), (2000, 400, "#97e277")):
        ell(c, hx, 520 + r * 0.55, r, r * 0.75); setc(c, col); c.fill()
    c.restore()

def ground(c):
    g = cairo.LinearGradient(0, 470, 0, 720)
    g.add_color_stop_rgba(0, *hexc("#73d65c")); g.add_color_stop_rgba(1, *hexc("#45b84a"))
    c.set_source(g); c.rectangle(-400, 478, 3400, 300); c.fill()

def fence(c):
    for i in range(-2, 34):
        x = i * 70
        rrect(c, x, 400, 42, 92, 6); fs(c, "#ffffff", (0.82, 0.84, 0.9, 1), 3)
        c.move_to(x, 410); c.line_to(x + 21, 388); c.line_to(x + 42, 410); fs(c, "#ffffff", (0.82, 0.84, 0.9, 1), 3)
    rrect(c, -150, 425, 2600, 16, 5); fs(c, "#ffffff", (0.82, 0.84, 0.9, 1), 3)
    rrect(c, -150, 462, 2600, 16, 5); fs(c, "#ffffff", (0.82, 0.84, 0.9, 1), 3)

def house(c):
    rrect(c, 40, 260, 300, 240, 10); fs(c, "#ff9fc3", "#e0709c", 4)
    c.move_to(15, 270); c.line_to(190, 130); c.line_to(365, 270); c.close_path(); fs(c, "#ff5b5b", "#cf3a3a", 4)
    rrect(c, 260, 150, 40, 70, 4); fs(c, "#ff5b5b", "#cf3a3a", 4)
    rrect(c, 150, 370, 80, 130, 36); fs(c, "#8e5bd8", "#6a3fb0", 4)
    ell(c, 214, 440, 6, 6); setc(c, "#ffd23f"); c.fill()
    for wx in (70, 250):
        rrect(c, wx, 300, 64, 64, 10); fs(c, "#bfe9ff", "#e0709c", 5)
        c.move_to(wx + 32, 300); c.line_to(wx + 32, 364); c.move_to(wx, 332); c.line_to(wx + 64, 332); setc(c, "#ffffff"); c.set_line_width(4); c.stroke()
    ell(c, 190, 220, 30, 30); fs(c, "#bfe9ff", "#e0709c", 5)

def tree(c, x):
    rrect(c, x - 22, 300, 44, 200, 14); fs(c, "#a0643a")
    for dx, dy, r in ((0, 230, 90), (-70, 280, 70), (70, 280, 70), (-40, 180, 60), (45, 185, 62)):
        ell(c, x + dx, dy, r, r * 0.92); fs(c, "#3fbf5a", "#2f9a47", 4)
    for dx, dy in ((-40, 250), (30, 210), (60, 290), (-60, 300), (0, 170)):
        ell(c, x + dx, dy, 9, 9); setc(c, "#ff4f6d"); c.fill()

def bed_back(c):
    rrect(c, 1215, 512, 650, 56, 26); fs(c, "#8a5030", "#6b3a1f", 3)

def bed_front(c, t):
    wet = prog(t, S("water") + 0.3, E("water") + 0.3) * (1 - 0.5 * prog(t, S("sprout") - 4, S("sprout")))
    rrect(c, 1220, 520, 640, 42, 20)
    g = cairo.LinearGradient(0, 520, 0, 562)
    g.add_color_stop_rgba(0, *(lerp(a, b, wet) for a, b in zip(hexc("#7a4524"), hexc("#4f2a14")))); g.add_color_stop_rgba(1, *hexc("#5e3219"))
    c.set_source(g); c.fill()
    rrect(c, 1205, 548, 670, 62, 14); fs(c, "#d1904f", "#a5652d", 4)
    for i in range(1, 6):
        c.move_to(1205 + i * 112, 552); c.line_to(1205 + i * 112, 606); setc(c, "#a5652d"); c.set_line_width(3); c.stroke()
    for i in range(11):
        ell(c, 1230 + i * 61, 580, 4, 3); setc(c, (0.6, 0.35, 0.15, 0.6)); c.fill()

def plants(c, t):
    for i, hx in enumerate(HOLES):
        dug = t >= DIG_HITS[i] if i < len(DIG_HITS) else t >= DIG_HITS[-1]
        hs = back(prog(t, DIG_HITS[min(i, len(DIG_HITS) - 1)], DIG_HITS[min(i, len(DIG_HITS) - 1)] + 0.3))
        cov = back(prog(t, S("cover") + 0.2 + i * 0.15, S("cover") + 0.5 + i * 0.15))
        if dug and cov < 0.5:
            ell(c, hx, HOLE_Y, 26 * hs, 9 * hs); setc(c, "#3a1d0c"); c.fill()
            if t >= SEED_TIMES[i]:
                ell(c, hx, HOLE_Y - 2, 7, 5); fs(c, "#e3ad6c", "#a4703a", 2)
        if cov > 0:
            c.save(); c.translate(hx, HOLE_Y + 2); c.scale(cov, cov)
            c.arc(0, 0, 24, PI, 2 * PI); c.close_path(); fs(c, "#8a5030", "#5e3219", 2.5); c.restore()
        sp = back(prog(t, SPROUT_TIMES[i], SPROUT_TIMES[i] + 0.4))
        if sp <= 0: continue
        fl = back(prog(t, FLOWER_TIMES[i], FLOWER_TIMES[i] + 0.7), 1.4)
        h = lerp(40 * sp, FLOWER_H[i], clamp(fl))
        sway = math.sin(t * 2.2 + i) * 0.06 * clamp(fl * 2)
        c.save(); c.translate(hx, HOLE_Y - 8)
        c.rotate(sway)
        c.move_to(0, 0); c.curve_to(6, -h * 0.3, -6, -h * 0.7, 0, -h)
        c.set_line_cap(cairo.LINE_CAP_ROUND); setc(c, "#2f9a47"); c.set_line_width(11); c.stroke()
        c.move_to(0, 0); c.curve_to(6, -h * 0.3, -6, -h * 0.7, 0, -h); setc(c, "#4cd964"); c.set_line_width(7); c.stroke()
        for sgn, ly in ((-1, 0.35), (1, 0.55)):
            ls = sp * (1 if fl <= 0 else 1 + 0.3 * fl)
            c.save(); c.translate(0, -h * ly if fl > 0 else -h * 0.8); c.rotate(sgn * 0.9); c.scale(ls, ls)
            ell(c, sgn * 0, -16, 10, 20); fs(c, "#4cd964", "#2f9a47", 2.5); c.restore()
        if fl > 0:
            c.translate(0, -h); c.scale(fl, fl); c.rotate(t * 0.3 * (1 if i % 2 else -1))
            col = FLOWER_COLS[i]
            for p in range(6):
                a = p * PI / 3
                ell(c, 26 * math.cos(a), 26 * math.sin(a), 20, 20); fs(c, col, dark(col, 0.75), 3)
            c.rotate(-t * 0.3 * (1 if i % 2 else -1))
            ell(c, 0, 0, 20, 20); fs(c, "#ff9f1a" if i == 2 else "#ffe066", "#e0a000", 3)
            c.set_line_width(2.5); setc(c, "#6b3a1f")
            ell(c, -7, -3, 2.6, 3.2); c.fill(); ell(c, 7, -3, 2.6, 3.2); c.fill()
            c.arc(0, 2, 7, 0.15 * PI, 0.85 * PI); c.stroke()
        c.restore()

def dirt(c, t, hits, x_of, spread=1.0):
    for j, h in enumerate(hits):
        dt = t - h
        if not (0 <= dt <= 0.75): continue
        r = random.Random(j * 31 + int(h * 10))
        x0, y0 = x_of(j)
        for k in range(10):
            vx = r.uniform(-160, 160) * spread; vy = r.uniform(-420, -230)
            px = x0 + vx * dt; py = y0 + vy * dt + 900 * dt * dt
            if py > 560: continue
            ell(c, px, py, 6 * (1 - dt), 6 * (1 - dt)); setc(c, (0.45, 0.25, 0.1, 1)); c.fill()

def note(c, x, y, col, s=1.0, a=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    ell(c, 0, 0, 11, 8.5); setc(c, hexc(col, a)); c.fill()
    c.rectangle(8, -38, 4.5, 38); c.fill()
    c.move_to(12, -38); c.curve_to(26, -30, 26, -18, 20, -12); c.set_line_width(4.5); c.stroke()
    c.restore()

def heart(c, x, y, s, col="#ff4f8b", a=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.move_to(0, 8); c.curve_to(-22, -6, -12, -26, 0, -12); c.curve_to(12, -26, 22, -6, 0, 8); setc(c, hexc(col, a)); c.fill(); c.restore()

def floaters(c, t, kind, t0, t1, sources, rate=3.0):
    cols = ["#ff3b3b", "#ff8c1a", "#2f7bff", "#a04dff", "#ff4f8b", "#22c3a6"]
    n = int((t1 - t0) * rate)
    for j in range(n):
        b = t0 + j / rate; dt = t - b
        if not (0 <= dt <= 2.0): continue
        sx, sy = sources[j % len(sources)]
        a = clamp(1 - dt / 2.0) * clamp(dt * 5)
        x = sx + math.sin(dt * 4 + j) * 18 + (j % 3 - 1) * 20; y = sy - dt * 110
        if kind == "note": note(c, x, y, cols[j % len(cols)], 0.9, a)
        else: heart(c, x, y, 1.1 + 0.3 * (j % 2), "#ff4f8b" if j % 2 else "#ff7ab0", a)

def butterfly(c, t):
    t0 = S("butterfly") - 0.3
    if t < t0: return
    dt = t - t0
    ent = ease(prog(dt, 0, 2.0))
    lx = 640 + 300 * math.sin(dt * 0.9); ly = 300 + 70 * math.sin(dt * 1.8)
    x = lerp(-60, lx, ent); y = lerp(160, ly, ent) + 10 * math.sin(dt * 9)
    flap = abs(math.sin(dt * 16))
    c.save(); c.translate(x, y); c.rotate(0.2 * math.cos(dt * 0.9))
    for sgn in (-1, 1):
        c.save(); c.scale(sgn * (0.35 + 0.65 * flap), 1)
        ell(c, 22, -14, 24, 20); fs(c, "#ff7ab0", "#d9407c", 2.5)
        ell(c, 18, 14, 16, 14); fs(c, "#ffb13b", "#d98a10", 2.5)
        ell(c, 24, -16, 7, 7); setc(c, "#ffffff"); c.fill()
        c.restore()
    rrect(c, -5, -24, 10, 46, 5); setc(c, "#5b3a7a"); c.fill()
    c.set_line_width(2.5); setc(c, "#5b3a7a")
    c.move_to(-2, -22); c.curve_to(-6, -34, -12, -38, -14, -40); c.stroke()
    c.move_to(2, -22); c.curve_to(6, -34, 12, -38, 14, -40); c.stroke()
    c.restore()

def rain_cloud(c, t):
    a, b = S("chant1") - 0.2, E("chant1") + 0.6
    if not (a <= t <= b): return
    p = prog(t, a, b)
    x = lerp(1180, 1700, p); fade = clamp(min(t - a, b - t) * 3)
    for k in range(26):
        r = random.Random(k)
        ph = ((t * 1.6 + r.random()) % 1)
        dx = r.uniform(-10, 110); y = 250 + ph * 280
        c.move_to(x + dx, y); c.line_to(x + dx - 3, y + 16); setc(c, (0.25, 0.55, 1, 0.8 * fade)); c.set_line_width(4); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()
    cloud(c, x, 230, 1.2, fade)

def water_drops(c, t, bx):
    a, b = S("water"), E("water") + 0.4
    if not (a <= t <= b): return
    sx, sy = c.device_to_user(*SPOUT[0])
    for k in range(18):
        r = random.Random(k)
        ph = ((t * 2.2 + r.random()) % 1)
        x = sx + r.uniform(-14, 14) - ph * 10; y = sy + ph * (HOLE_Y - sy)
        ell(c, x, y, 4.5, 6.5); setc(c, (0.3, 0.6, 1, 0.9)); c.fill()

# ---------------------------------------------------------------- character staging
def mia_state(t):
    keys = [(0, 520), (T_PAN0 + 0.1, 520), (T_PAN1 + 0.2, MIA_HOME), (S("dig") - 0.3, MIA_HOME)]
    for i, h in enumerate(DIG_HITS):
        X = HOLES[i] - 95
        keys += [(h - 0.42, X), (h + 0.12, X)]
    keys += [(E("dig") + 0.2, keys[-1][1]), (E("dig") + 1.1, MIA_HOME), (S("hug") + 0.1, MIA_HOME), (S("hug") + 1.3, 900 + 960)]
    x = keyed(t, keys)
    v = (keyed(t + 0.03, keys) - keyed(t - 0.03, keys)) / 0.06
    walking = abs(v) > 30
    hopy = 0.0
    arms = [0.28 + 0.04 * math.sin(t * 2), 0.28 + 0.04 * math.sin(t * 2 + 1)]
    m = mouth("mia", t); look = 1; stretch = 1.0; lean = 0.0; hold = None; closed = blink(t, 0.3)
    if walking:
        hopy += abs(math.sin(t * 11)) * 9
        arms = [0.35 + 0.35 * math.sin(t * 11), 0.35 - 0.35 * math.sin(t * 11)]
    if m > 0.1:
        arms[1] += 0.25 * m
    for st in starts("mia_wave"):
        if st - 0.2 <= t <= st + 2.3: arms[1] = 2.35 + 0.3 * math.sin(t * 12)
    for st in starts("mia_jump"):
        hopy += hop(t, st + 0.1, 60, 0.5)
        if st <= t <= st + 1.0: arms = [2.35, 2.35]
    if active(t, "mia_point"): arms[1] = 1.55
    if active(t, "dig", 0.3, 0.2):
        hold = "shovel"; arms = [0.9, 1.0]
    if S("seedbag") - 0.2 <= t <= SEED_TIMES[-1] + 0.6:
        hold = "bag"; arms[0] = 0.9
        for st in SEED_TIMES:
            if st - 0.6 <= t <= st: arms[1] = lerp(0.4, 2.2, ease(prog(t, st - 0.6, st - 0.35)))
        look = 1
    if active(t, "chant1") or active(t, "chant2") or active(t, "sing"):
        sw = math.sin(t * 2 * PI / (2 * 60 / 112))
        arms = [1.8 + 0.6 * sw, 1.8 - 0.6 * sw]; lean = 0.06 * sw
    if active(t, "stretch", 0.1, 0.6):
        p = ease(prog(t, S("stretch"), S("stretch") + 0.5))
        arms = [lerp(arms[0], 2.45, p), lerp(arms[1], 2.45, p)]; stretch = 1 + 0.08 * p
    if active(t, "wiggle", 0, 0.4):
        lean = 0.12 * math.sin(t * 16)
    for h in HOPHOP_TIMES:
        hopy += hop(t, h, 50, 0.45)
    if S("hophop") <= t <= HOPHOP_TIMES[-1] + 0.5: arms = [2.3, 2.3]
    if active(t, "sing", 0, 0.3):
        hopy += abs(math.sin(t * PI / (60 / 112))) * 14
    if active(t, "ask", 0, 0.5): arms[1] = 1.3; look = 1
    if S("rainbow") <= t <= S("butterfly"): look = 1
    if t >= S("hug") + 0.9:
        p = ease(prog(t, S("hug") + 0.9, S("hug") + 1.4)); arms = [lerp(arms[0], 0.6, p), lerp(arms[1], 1.9, p)]; lean = 0.08 * p
        if t >= S("hug") + 1.4: closed = (t < S("hug") + 3.5)
    return dict(x=x, hopy=hopy, arms=tuple(arms), m=m, look=look, stretch=stretch, lean=lean, hold=hold, closed=closed)


def ben_state(t):
    keys = [(0, 1420), (S("benny_in"), 1420), (S("benny_in") + 1.5, 800), (T_PAN0 + 0.1, 800), (T_PAN1 + 0.2, BEN_HOME),
            (S("bdig") - 0.1, BEN_HOME), (S("bdig") + 0.8, 1555), (E("bdig2") + 0.3, 1555), (E("bdig2") + 1.0, BEN_HOME),
            (S("water") - 0.4, BEN_HOME), (S("water"), 1820), (E("water") + 0.4, 1340), (E("water") + 0.6, 1340), (S("sun_shine") + 1.4, BEN_HOME), (S("hug") + 0.1, BEN_HOME), (S("hug") + 1.3, 900 + 1125)]
    x = keyed(t, keys)
    v = (keyed(t + 0.03, keys) - keyed(t - 0.03, keys)) / 0.06
    hopy = 0.0; face = 1
    arms = [0.35 + 0.05 * math.sin(t * 2.3), 0.35 + 0.05 * math.sin(t * 2.3 + 1)]
    m = mouth("benny", t); look = -1; lean = 0.0; ear = 0.0; hold = None; closed = blink(t, 1.9); stretch = 1.0
    if abs(v) > 30:
        hopy += abs(math.sin(t * 7)) * 34
        face = -1 if v < 0 else 1
    if m > 0.1: arms[0] += 0.3 * m; ear = 0.06 * m
    for st in starts("benny_hop"):
        hopy += hop(t, st + 0.05, 55, 0.42) + hop(t, st + 0.5, 45, 0.4)
        if st <= t <= st + 1.0: arms = [2.4, 2.4]; ear = -0.15
    if S("bdig") + 0.8 <= t <= E("bdig2") + 0.3:
        arms = [0.9 + 0.7 * math.sin(t * 22), 0.9 + 0.7 * math.sin(t * 22 + PI)]; lean = 0.12
        stretch = 0.96
    if S("can_in") - 0.2 <= t <= E("water") + 0.8:
        hold = "can"; arms[0] = 1.2; face = 1; look = -1
    if active(t, "chant1") or active(t, "chant2") or active(t, "sing"):
        sw = math.sin(t * 2 * PI / (2 * 60 / 112) + PI)
        arms = [1.8 + 0.6 * sw, 1.8 - 0.6 * sw]; lean = 0.06 * sw
    if active(t, "peek", 0, 0.6): lean = -0.22; look = -1
    if active(t, "wiggle", 0, 0.5):
        lean = 0.18 * math.sin(t * 16); arms = [1.2, 1.2]; ear = 0.25 * math.sin(t * 16)
    if active(t, "stretch", 0.1, 0.6):
        arms = [2.9, 2.9]; stretch = 1.08
    for h in HOPHOP_TIMES:
        hopy += hop(t, h + 0.08, 60, 0.42)
    if active(t, "sing", 0, 0.3):
        hopy += abs(math.sin(t * PI / (60 / 112) + 0.5)) * 18
    if t >= S("hug") + 0.9:
        p = ease(prog(t, S("hug") + 0.9, S("hug") + 1.4)); arms = [lerp(arms[0], 1.9, p), lerp(arms[1], 0.6, p)]; lean = -0.08 * p
        if t >= S("hug") + 1.4: closed = (t < S("hug") + 3.5)
    return dict(x=x, hopy=hopy, arms=tuple(arms), m=m, look=look, lean=lean, ear=ear, hold=hold, face=face, closed=closed, stretch=stretch)

# ---------------------------------------------------------------- scenes
def main_scene(c, t):
    cam = camx(t)
    sky(c)
    rainbow(c, t)
    c.save(); c.translate(-cam * 0.25, 0)
    for i, (cx, cy, s) in enumerate(CLOUDS):
        cloud(c, (cx + t * (6 + 2 * i)) % 2200 - 150, cy, s)
    c.restore()
    sun(c, t)
    hills(c, cam)
    c.save(); c.translate(-cam, 0)
    ground(c)
    for gx, gy, col, r in GRASS_DOTS:
        ell(c, gx, gy, r, r); setc(c, col); c.fill()
    fence(c)
    house(c)
    tree(c, 1020)
    bed_back(c)
    ms, bs = mia_state(t), ben_state(t)
    hands = mia(c, ms["x"], GROUND_Y, t, 0.92, ms["arms"], ms["m"], ms["look"], ms["stretch"], ms["lean"], ms["hold"], ms["closed"], ms["hopy"])
    if ms["hold"] == "shovel":
        hx, hy = c.device_to_user(*hands[1])
        down = 0
        for h in DIG_HITS:
            if h - 0.25 <= t <= h + 0.3: down = math.sin(PI * prog(t, h - 0.25, h + 0.3))
        tipx, tipy = hx + 70, HOLE_Y - 30 + 34 * down
        c.move_to(hx, hy); c.line_to(tipx, tipy); setc(c, "#a0643a"); c.set_line_width(9); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()
        c.save(); c.translate(tipx, tipy); c.rotate(math.atan2(tipy - hy, tipx - hx) - PI / 2)
        c.move_to(-16, 0); c.line_to(16, 0); c.line_to(12, 30); c.curve_to(6, 42, -6, 42, -12, 30); c.close_path(); fs(c, "#b8c4d6", "#7d8aa0", 3)
        c.restore()
    benny(c, bs["x"], GROUND_Y, t, 0.95, bs["arms"], bs["m"], bs["look"], bs["lean"], bs["ear"], bs["hold"], bs["face"], bs["closed"], bs["hopy"], bs["stretch"])
    # seeds in flight
    for i, st in enumerate(SEED_TIMES):
        p = prog(t, st - 0.4, st)
        if 0 < p < 1:
            x0, y0 = ms["x"] + 70, 400
            x = lerp(x0, HOLES[i], p); y = lerp(y0, HOLE_Y, p) - 160 * math.sin(PI * p)
            ell(c, x, y, 8, 6); fs(c, "#e3ad6c", "#a4703a", 2)
    bed_front(c, t)
    plants(c, t)
    dirt(c, t, DIG_HITS, lambda j: (HOLES[j], HOLE_Y))
    dirt(c, t, BDIG_HITS, lambda j: (1555 + (40 if j % 2 else -40), HOLE_Y), 1.4)
    water_drops(c, t, bs["x"])
    rain_cloud(c, t)
    c.restore()
    # sparkles on each new flower
    for i, ft in enumerate(FLOWER_TIMES):
        dt = t - ft
        if 0 <= dt <= 0.7:
            fx = HOLES[i] - cam; fy = HOLE_Y - 8 - FLOWER_H[i]
            for k in range(8):
                a = k * PI / 4; r = 30 + 90 * dt
                ell(c, fx + r * math.cos(a), fy + r * math.sin(a), 6 * (1 - dt / 0.7), 6 * (1 - dt / 0.7)); setc(c, hexc(FLOWER_COLS[i]))
                c.fill()
    butterfly(c, t)
    mx, bx = ms["x"] - cam, bs["x"] - cam
    floaters(c, t, "note", S("dance_start"), E("hophop") + 0.5, [(mx, 250), (bx, 280)], 2.5)
    floaters(c, t, "note", S("sing"), E("sing") + 0.3, [(mx, 250), (bx, 280), (640, 300)], 4)
    floaters(c, t, "heart", S("hug") + 1.3, E("benny_hop") if False else LINES[-3]["end"] + 1.5, [((mx + bx) / 2, 260)], 3)


def sunburst(c, t, c1, c2):
    gr = cairo.RadialGradient(640, 380, 50, 640, 380, 900)
    gr.add_color_stop_rgba(0, *hexc(c1)); gr.add_color_stop_rgba(1, *hexc(c2)); c.set_source(gr); c.paint()
    c.save(); c.translate(640, 380); c.rotate(t * 0.15)
    for i in range(16):
        c.move_to(0, 0); c.arc(0, 0, 1200, i * PI / 8, i * PI / 8 + PI / 16); c.close_path(); setc(c, (1, 1, 1, 0.13)); c.fill()
    c.restore()


def big_text(c, text, x, y, size, colors, t, t0=0.0, face=TITLE_FONT, wobble=True):
    font(c, size, True, face)
    widths = [c.text_extents(ch).x_advance for ch in text]
    tw = sum(widths); cx = x - tw / 2
    for i, ch in enumerate(text):
        p = back(prog(t, t0 + i * 0.05, t0 + i * 0.05 + 0.45))
        if p <= 0: cx += widths[i]; continue
        dy = math.sin(t * 4 + i * 0.6) * 6 if wobble else 0
        c.save(); c.translate(cx + widths[i] / 2, y + dy); c.scale(p, p)
        c.move_to(-widths[i] / 2, 0); c.text_path(ch)
        setc(c, (0.2, 0.1, 0.35, 0.35)); c.save(); c.translate(4, 6); c.fill_preserve(); c.restore()
        c.new_path(); c.move_to(-widths[i] / 2, 0); c.text_path(ch)
        setc(c, "#ffffff"); c.set_line_width(size * 0.16); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke_preserve()
        setc(c, colors[i % len(colors)] if ch != " " else "#ffffff"); c.fill()
        c.restore(); cx += widths[i]


def title_card(c, t):
    sunburst(c, t, "#fff27a", "#ff9d2e")
    for i, col in enumerate(["#ff3b3b", "#ff8c1a", "#ffd60a", "#4cd964", "#2f7bff", "#a04dff"]):
        p = ease(prog(t, 0.1, 1.0))
        c.save(); c.move_to(640, 470); c.arc(640, 470, 700, PI, PI + PI * p); c.close_path(); c.clip()
        c.arc(640, 470, 430 - i * 24, PI, 2 * PI); setc(c, hexc(col, 0.9)); c.set_line_width(25); c.stroke(); c.restore()
    for i in range(5):
        ell(c, 100 + i * 270, 560, 240, 120); setc(c, "#6fd36f"); c.fill()
    big_text(c, "Mia & Benny", 640, 300, 150, ["#ff4f8b", "#ff8c1a", "#ffb000", "#ffffff", "#2f9a47", "#2f7bff", "#a04dff", "#ff3b3b", "#ff8c1a", "#2f7bff", "#a04dff"], t, 0.3)
    p = back(prog(t, 1.2, 1.7))
    if p > 0:
        c.save(); c.translate(640, 385); c.scale(p, p)
        rrect(c, -260, -42, 520, 74, 37); fs(c, "#ff5fa2", "#d93a7f", 5)
        font(c, 46, True); ext = c.text_extents("The Rainbow Garden")
        c.move_to(-ext.x_advance / 2, 13); setc(c, "#ffffff"); c.show_text("The Rainbow Garden")
        c.restore()
    pm = back(prog(t, 0.8, 1.3)); pb = back(prog(t, 1.0, 1.5))
    mia(c, 180, 900 - 230 * pm, t, 1.05, (0.3, 2.35 + 0.3 * math.sin(t * 10)), mouth("mia", t), 1, closed=blink(t, 0.3))
    benny(c, 1100, 860 - 230 * pb, t, 1.05, (2.6 + 0.35 * math.sin(t * 10 + 1), 0.3), mouth("benny", t), -1, closed=blink(t, 1.9), hopy=abs(math.sin(t * 5)) * 10)


def outro_card(c, t):
    lt = t - T_OUTRO
    sunburst(c, t, "#bff3ff", "#38b6ff")
    rr = random.Random(5)
    cols = ["#ff3b3b", "#ff8c1a", "#ffd60a", "#4cd964", "#2f7bff", "#a04dff", "#ff4f8b"]
    for k in range(70):
        x0 = rr.uniform(0, W); sp = rr.uniform(60, 140); ph = rr.uniform(0, 800)
        y = (ph + lt * sp) % 820 - 60; x = x0 + 20 * math.sin(lt * 2 + k)
        c.save(); c.translate(x, y); c.rotate(lt * 3 + k); rrect(c, -7, -4, 14, 8, 2); setc(c, cols[k % len(cols)]); c.fill(); c.restore()
    for i in range(5):
        ell(c, 100 + i * 270, 600, 240, 120); setc(c, "#6fd36f"); c.fill()
    big_text(c, "Bye-bye!", 640, 270, 160, ["#ff4f8b", "#ff8c1a", "#ffb000", "#4cd964", "#2f7bff", "#a04dff", "#ff3b3b", "#ff8c1a"], lt, 0.3)
    p = back(prog(lt, 1.0, 1.5))
    if p > 0:
        c.save(); c.translate(640, 365); c.scale(p, p)
        font(c, 56, True); ext = c.text_extents("See you next time!")
        c.move_to(-ext.x_advance / 2, 18); c.text_path("See you next time!")
        setc(c, "#2b4cc2"); c.set_line_width(10); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke_preserve(); setc(c, "#ffffff"); c.fill()
        c.restore()
    wv = math.sin(t * 11) * 0.3
    mia(c, 190, 650, t, 0.95, (2.3 - wv, 2.3 + wv), mouth("mia", t), 1, closed=blink(t, 0.3), hopy=hop(t, S("byebye"), 50, 0.5))
    benny(c, 1095, 650, t, 0.95, (2.6 + wv, 2.6 - wv), mouth("benny", t), -1, closed=blink(t, 1.9), hopy=abs(math.sin(t * 5)) * 16)

# ---------------------------------------------------------------- captions
SPK_COL = {"narrator": "#6a3fd6", "mia": "#e8327f", "benny": "#1f6fe0"}
SPK_NAME = {"narrator": "Narrator", "mia": "Mia", "benny": "Benny"}

def captions(c, t):
    cur = None
    for i, l in enumerate(LINES):
        nxt = LINES[i + 1]["start"] if i + 1 < len(LINES) else 1e9
        if l["start"] - 0.12 <= t <= min(l["end"] + 0.6, nxt - 0.12):
            cur = l
    if not cur: return
    a = clamp((t - cur["start"] + 0.12) / 0.12)
    words = cur["text"].split()
    font(c, 33, True)
    sp = c.text_extents(" ").x_advance
    ws = [c.text_extents(w).x_advance for w in words]
    lines, row, rw = [], [], 0
    for w, wd in zip(words, ws):
        if row and rw + sp + wd > 1120:
            lines.append((row, rw)); row, rw = [], 0
        rw += (sp if row else 0) + wd; row.append((w, wd))
    lines.append((row, rw))
    maxw = max(r[1] for r in lines); lh = 42
    bw, bh = maxw + 60, len(lines) * lh + 26
    bx, by = 640 - bw / 2, 700 - bh
    pop = 0.9 + 0.1 * back(a)
    c.save(); c.translate(640, by + bh / 2); c.scale(pop, pop); c.translate(-640, -(by + bh / 2))
    c.push_group()
    rrect(c, bx + 3, by + 5, bw, bh, 26); setc(c, (0.1, 0.05, 0.25, 0.25)); c.fill()
    rrect(c, bx, by, bw, bh, 26); fs(c, (1, 1, 1, 0.96), hexc(SPK_COL[cur["speaker"]]), 5)
    # name tag
    font(c, 24, True); nm = SPK_NAME[cur["speaker"]]; nw = c.text_extents(nm).x_advance
    rrect(c, bx + 24, by - 22, nw + 32, 38, 19); fs(c, SPK_COL[cur["speaker"]], (1, 1, 1, 1), 4)
    c.move_to(bx + 40, by + 5); setc(c, "#ffffff"); c.show_text(nm)
    # words, highlighted as they are spoken (timed by letter count)
    total = sum(len(w) + 1 for w in words); dur = cur["end"] - cur["start"]
    done = 0; font(c, 33, True)
    for li, (row, rw) in enumerate(lines):
        x = 640 - rw / 2; y = by + 13 + lh * li + 33
        for w, wd in row:
            wt = cur["start"] + dur * done / total
            spoken = t >= wt
            c.move_to(x, y); setc(c, SPK_COL[cur["speaker"]] if spoken else "#2b2d42")
            c.show_text(w); x += wd + sp; done += len(w) + 1
    c.pop_group_to_source(); c.paint_with_alpha(a)
    c.restore()

# ---------------------------------------------------------------- frame
def iris(c, t, t0, draw_a, draw_b, d=0.9):
    p = ease(prog(t, t0, t0 + d))
    if p <= 0: draw_a(c, t); return
    if p >= 1: draw_b(c, t); return
    draw_a(c, t)
    c.save(); c.arc(640, 360, 760 * p, 0, 2 * PI); c.clip(); draw_b(c, t); c.restore()
    c.arc(640, 360, 760 * p, 0, 2 * PI); setc(c, "#ffffff"); c.set_line_width(14); c.stroke()


def frame(t, surf=None):
    surf = surf or cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(surf)
    if t < T_TITLE_END + 1:
        iris(c, t, T_TITLE_END, title_card, main_scene)
    else:
        iris(c, t, T_OUTRO, main_scene, outro_card)
    captions(c, t)
    fade = clamp(min(t / 0.4, (DURATION - t) / 1.2))
    if fade < 1:
        c.rectangle(0, 0, W, H); setc(c, (0, 0, 0, 1 - fade)); c.fill()
    return surf


if __name__ == "__main__":
    import sys
    for ts in sys.argv[1:]:
        frame(float(ts)).write_to_png(f"stills/f_{float(ts):06.2f}.png")
