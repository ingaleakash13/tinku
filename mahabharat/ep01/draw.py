import sys, math, random, numpy as np, soundfile as sf, cairo
import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from chars import *
from scenery import room_bg, palace_scene_bg, river_bank_scene, mandap_scene_bg
from cues import *
from script import NAMES, EP_NUM, EP_TITLE_HI, EP_TITLE_EN

W, H, FPS = 1280, 720, 30
GY = 600          # feet line for characters
CS = 0.66         # adult character scale

def prog(t, a, b): return clamp((t - a) / (b - a)) if b > a else float(t >= a)
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def back(x, s=1.7):
    x = clamp(x); x -= 1; return x * x * ((s + 1) * x + s) + 1
def lerp(a, b, x): return a + (b - a) * x
def keyed(t, keys):
    if t <= keys[0][0]: return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t <= t1: return lerp(v0, v1, ease(prog(t, t0, t1)))
    return keys[-1][1]
def active(t, cue, pre=0.0, post=0.0): return S(cue) - pre <= t <= E(cue) + post
def blink(t, off): return ((t + off) % 3.9) < 0.12

# ---------------- lip sync
NF = int(DURATION * FPS) + 2
MOUTH = {k: np.zeros(NF) for k in NAMES}
for l in LINES:
    x, sr = sf.read(l["file"]); hp = sr // FPS
    r = np.array([np.sqrt((x[i:i + hp] ** 2).mean()) for i in range(0, len(x) - hp, hp)])
    r = np.clip(r / (np.percentile(r, 90) + 1e-6), 0, 1.2)
    f0 = int(l["start"] * FPS); MOUTH[l["speaker"]][f0:f0 + len(r)] = r[:NF - f0]
for k in MOUTH: MOUTH[k] = np.convolve(MOUTH[k], [0.25, 0.5, 0.25], "same")
def mo(spk, t):
    i = int(t * FPS); return float(MOUTH[spk][i]) if 0 <= i < NF else 0.0
def speaking(spk, t): return any(l["speaker"] == spk and l["start"] - 0.1 <= t <= l["end"] + 0.1 for l in LINES)

# ---------------- natural talking gestures
def talk(spk, t, seed=0.0, idle=True):
    """(left, right) arm poses as (shoulder, elbow) — gentle idle breathing, expressive while speaking."""
    m = mo(spk, t); sp = speaking(spk, t)
    br = 0.03 * math.sin(t * 1.6 + seed)
    if not sp:
        return ((0.14 + br, 0.22), (0.14 - br, 0.22))
    a = 0.5 + 0.22 * math.sin(t * 1.1 + seed) + 0.25 * m
    b = 1.15 + 0.35 * math.sin(t * 1.7 + seed * 2) + 0.35 * m
    la = 0.22 + 0.12 * math.sin(t * 0.8 + seed) + 0.1 * m
    lb = 0.45 + 0.4 * math.sin(t * 1.3 + seed) * m
    return ((la, lb), (a, b))

# ---------------- backgrounds
def sky(c, top, bot, y1=520):
    g = cairo.LinearGradient(0, 0, 0, y1); g.add_color_stop_rgba(0, *hexc(top)); g.add_color_stop_rgba(1, *hexc(bot)); c.set_source(g); c.paint()

def cloud(c, x, y, s, a=1.0):
    for dx, dy, r in ((0, 0, 34), (36, -16, 42), (76, 0, 34), (38, 10, 36)):
        ell(c, x + dx * s, y + dy * s, r * s, r * s * 0.9); setc(c, (1, 1, 1, a)); c.fill()

def clouds(c, t, a=1.0):
    for i, (x, y, s) in enumerate(((100, 90, 1.0), (520, 60, 0.8), (930, 120, 1.1), (1300, 80, 0.9))):
        cloud(c, (x + t * (5 + i)) % 1500 - 150, y, s, a)

def grass(c, y0=520, c1="#7ad35e", c2="#4fb84a"):
    g = cairo.LinearGradient(0, y0, 0, H); g.add_color_stop_rgba(0, *hexc(c1)); g.add_color_stop_rgba(1, *hexc(c2))
    c.set_source(g); c.rectangle(0, y0, W, H - y0); c.fill()
    r = random.Random(4)
    for _ in range(50):
        ell(c, r.uniform(0, W), r.uniform(y0 + 20, H), 3, 3); setc(c, r.choice(["#ffffff", "#ffe14d", "#ff8fc7"])); c.fill()

def palace_building(c, x, y, s=1.0, col="#f2c78f", dome="#f5b82e"):
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, -260, -170, 520, 170, 6); fs(c, col, dark(col, 0.75), 3)
    for k in range(-3, 4):  # arches
        c.move_to(k * 70 - 22, 0); c.line_to(k * 70 - 22, -70); c.curve_to(k * 70 - 22, -100, k * 70 + 22, -100, k * 70 + 22, -70); c.line_to(k * 70 + 22, 0); c.close_path()
        fs(c, dark(col, 0.62), dark(col, 0.5), 2)
    rrect(c, -280, -186, 560, 22, 6); fs(c, light(col, 0.3), dark(col, 0.75), 3)
    for dx, r, h in ((-180, 46, 60), (0, 80, 100), (180, 46, 60)):
        rrect(c, dx - r * 0.7, -186 - h * 0.6, r * 1.4, h * 0.6, 4); fs(c, col, dark(col, 0.75), 3)
        c.move_to(dx - r, -186 - h * 0.6); c.curve_to(dx - r, -186 - h * 1.6, dx - 6, -186 - h * 1.7, dx, -186 - h * 2.0)
        c.curve_to(dx + 6, -186 - h * 1.7, dx + r, -186 - h * 1.6, dx + r, -186 - h * 0.6); c.close_path(); fs(c, dome, dark(dome, 0.7), 3)
        c.move_to(dx, -186 - h * 2.0); c.line_to(dx, -186 - h * 2.0 - 40); setc(c, "#8a5a2b"); c.set_line_width(3); c.stroke()
        c.move_to(dx, -186 - h * 2.0 - 40); c.line_to(dx + 34, -186 - h * 2.0 - 30); c.line_to(dx, -186 - h * 2.0 - 20); c.close_path(); fs(c, "#ff7a1a", "#c4520a", 2)
    c.restore()

def bg_palace(c, t):
    return palace_scene_bg(c, t)
    sky(c, "#4fb8ff", "#d6f3ff"); clouds(c, t)
    for hx, r in ((150, 300), (700, 360), (1200, 320)):
        ell(c, hx, 560, r, r * 0.45); setc(c, "#a5e07f"); c.fill()
    palace_building(c, 640, 470, 1.0)
    grass(c, 470)
    c.move_to(520, 720); c.line_to(600, 470); c.line_to(680, 470); c.line_to(760, 720); c.close_path(); setc(c, "#e8c690"); c.fill()

def river_poly(c):
    c.move_to(560, 430); c.curve_to(700, 430, 900, 432, 1280, 440); c.line_to(1280, 720); c.line_to(520, 720)
    c.curve_to(560, 640, 520, 520, 560, 430); c.close_path()

def bg_river(c, t, dusk=0.0):
    return river_bank_scene(c, t, dusk)
    top = "#4fb8ff" if dusk < 0.5 else "#2a2f7a"; bot = "#d6f3ff" if dusk < 0.5 else "#ff9f6e"
    sky(c, top, bot, 440)
    if dusk < 0.5: clouds(c, t)
    else:
        ell(c, 1040, 120, 46, 46); setc(c, (1, 0.97, 0.85, 1)); c.fill()
        ell(c, 1058, 108, 40, 40); setc(c, hexc(top)); c.fill()
    for hx, r, col in ((200, 380, "#86c96a" if dusk < .5 else "#4e6e5a"), (900, 420, "#97d977" if dusk < .5 else "#56785e")):
        ell(c, hx, 470, r, r * 0.3); setc(c, col); c.fill()
    grass(c, 440, "#7ad35e" if dusk < .5 else "#4c8f4a", "#4fb84a" if dusk < .5 else "#2f6b3a")
    river_poly(c)
    g = cairo.LinearGradient(0, 430, 0, 720); g.add_color_stop_rgba(0, *hexc("#8fdcff" if dusk < .5 else "#6a7fd6")); g.add_color_stop_rgba(1, *hexc("#2f8fd8" if dusk < .5 else "#2a3f8f"))
    c.set_source(g); c.fill()
    c.save(); river_poly(c); c.clip()
    for row in range(9):
        y = 450 + row * 30
        for k in range(10):
            x = (k * 140 + row * 60 + t * 30 * (1 + row * 0.1)) % 900 + 520
            c.move_to(x, y); c.curve_to(x + 15, y - 6, x + 30, y - 6, x + 45, y); setc(c, (1, 1, 1, 0.35)); c.set_line_width(2.5); c.stroke()
    c.restore()
    for lx, ly in ((640, 690), (1180, 520), (1010, 680)):  # lotus pads
        ell(c, lx, ly, 26, 9); fs(c, "#3fae4a", "#2a7a33", 2)
        for a in (-0.6, 0, 0.6):
            c.save(); c.translate(lx, ly - 4); c.rotate(a); ell(c, 0, -10, 6, 12); fs(c, "#ff9fcf", "#d9407c", 1.5); c.restore()
    for tx in (120, 420):
        rrect(c, tx - 14, 300, 28, 160, 10); fs(c, "#a0643a")
        for dx, dy, r in ((0, 280, 70), (-50, 320, 52), (50, 320, 52)):
            ell(c, tx + dx, dy, r, r * 0.9); fs(c, "#3fbf5a" if dusk < .5 else "#2f7a44", "#2f9a47" if dusk < .5 else "#1f5a33", 3)

def bg_room(c, t):
    return room_bg(c, t)
    g = cairo.LinearGradient(0, 0, 0, 500); g.add_color_stop_rgba(0, *hexc("#bfe6ff")); g.add_color_stop_rgba(1, *hexc("#9fd4f5")); c.set_source(g); c.paint()
    c.rectangle(0, 500, W, 220); g2 = cairo.LinearGradient(0, 500, 0, 720); g2.add_color_stop_rgba(0, *hexc("#e3a86a")); g2.add_color_stop_rgba(1, *hexc("#c4844a")); c.set_source(g2); c.fill()
    for k in range(9): c.move_to(0, 520 + k * 24); c.line_to(W, 520 + k * 24)
    setc(c, (0.6, 0.38, 0.18, 0.35)); c.set_line_width(2); c.stroke()
    rrect(c, 0, 494, W, 12, 2); fs(c, "#ffffff", (0.8, 0.85, 0.9, 1), 2)
    rrect(c, 80, 90, 230, 200, 12); fs(c, "#fff8e6", "#d9a441", 8)  # window
    c.save(); rrect(c, 88, 98, 214, 184, 8); c.clip(); sky(c, "#4fb8ff", "#d6f3ff", 300); cloud(c, 140 + (t * 8) % 200, 150, 0.6); c.restore()
    c.move_to(195, 98); c.line_to(195, 282); c.move_to(88, 190); c.line_to(302, 190); setc(c, "#d9a441"); c.set_line_width(6); c.stroke()
    rrect(c, 380, 120, 150, 110, 8); fs(c, "#fff3c4", "#e07a1f", 6)  # poster: sun & bow
    c.save(); c.translate(455, 215); c.rotate(0.3)
    c.move_to(0, 0); c.curve_to(-3, -30, -2, -60, 0, -80); setc(c, "#2f9a47"); c.set_line_width(3); c.stroke()
    ell(c, 0, -74, 18, 30); fs(c, "#1fa38a", "#0f6b5a", 2); ell(c, 0, -80, 12, 17); setc(c, "#1f6fe0"); c.fill()
    ell(c, 0, -82, 7, 10); setc(c, "#0b1d4f"); c.fill(); ell(c, 0, -84, 3, 4); setc(c, "#ffd23f"); c.fill(); c.restore()
    rrect(c, 960, 180, 220, 320, 8); fs(c, "#c98a4b", "#8a5a2b", 4)  # bookshelf
    for row in range(3):
        y = 200 + row * 100
        rrect(c, 966, y + 80, 208, 10, 2); fs(c, "#8a5a2b")
        r = random.Random(row)
        x = 974
        while x < 1160:
            w = r.uniform(16, 26); h = r.uniform(55, 78)
            rrect(c, x, y + 80 - h, w, h, 3); fs(c, r.choice(["#ff5b5b", "#2f7bff", "#ffd23f", "#3fae4a", "#a04dff", "#ff8c1a"])); x += w + 3
    ell(c, 520, 640, 380, 60); setc(c, "#ff9f6e"); c.fill(); ell(c, 520, 640, 320, 44); setc(c, "#ffc48f"); c.fill()  # rug

def storybook(c, t, x=900, y=590, openp=0.0, closep=0.0):
    p = openp * (1 - closep)
    c.save(); c.translate(x, y)
    rrect(c, -16, -40, 32, 40, 6); fs(c, "#8a5a2b")
    poly(c, [(-120, -40), (120, -40), (90, -60), (-90, -60)]); fs(c, "#a0643a")
    if p > 0.02:
        glow = cairo.RadialGradient(0, -160, 10, 0, -160, 220); glow.add_color_stop_rgba(0, 1, 0.92, 0.5, 0.7 * p); glow.add_color_stop_rgba(1, 1, 0.92, 0.5, 0)
        c.set_source(glow); c.arc(0, -160, 220, 0, 2 * PI); c.fill()
        for sx in (-1, 1):
            c.move_to(0, -66); c.curve_to(sx * 50, -80, sx * 110, -78, sx * 130, -70); c.line_to(sx * 130, -230); c.curve_to(sx * 110, -238, sx * 50, -240, 0, -226); c.close_path()
            fs(c, "#fffaf0", "#c9b48a", 2.5)
            for k in range(6):
                c.move_to(sx * 20, -200 + k * 22); c.line_to(sx * 110, -204 + k * 22); setc(c, (0.6, 0.5, 0.35, 0.4)); c.set_line_width(2); c.stroke()
        cw = math.cos(PI * min(1, p))  # cover flipping to the left
        c.save(); c.scale(cw if abs(cw) > 0.02 else 0.02, 1)
        if cw > 0:
            rrect(c, 0, -236, 134, 172, 8); fs(c, "#c0392b", "#7a1f15", 3)
        c.restore()
    else:
        rrect(c, -100, -236, 200, 172, 10); fs(c, "#c0392b", "#7a1f15", 4)
        rrect(c, -86, -222, 172, 144, 8); setc(c, GOLD); c.set_line_width(3); c.stroke()
        draw_text(c, "महाभारत", 0, -160, 40, "#ffd23f", "#7a1f15", 3)
        ell(c, 0, -110, 12, 12); fs(c, GOLD, GOLD_D, 2)
    c.restore()

def bg_wedding(c, t):
    return mandap_scene_bg(c, t)
    sky(c, "#ffd27a", "#fff1d6", 500)
    palace_building(c, 640, 470, 1.15, "#f7d9a8", "#ffb000")
    c.rectangle(0, 470, W, 250); g = cairo.LinearGradient(0, 470, 0, 720); g.add_color_stop_rgba(0, *hexc("#f3d2a0")); g.add_color_stop_rgba(1, *hexc("#e0b47a")); c.set_source(g); c.fill()
    for k in range(-4, 5):  # rangoli-ish floor dots
        ell(c, 640 + k * 120, 680, 14, 5); setc(c, (1, 0.5, 0.3, 0.5)); c.fill()
    # mandap
    for px in (340, 940):
        rrect(c, px - 12, 230, 24, 380, 8); fs(c, "#d9a441", "#8a5a12", 3)
    c.move_to(310, 240); c.curve_to(500, 160, 780, 160, 970, 240); c.line_to(970, 260); c.curve_to(780, 186, 500, 186, 310, 260); c.close_path(); fs(c, "#e8432f", "#9a1f12", 3)
    for k in range(13):  # marigold strings
        x = 330 + k * 52
        c.move_to(x, 250 - 40 * math.sin(PI * k / 12)); c.line_to(x, 330 - 40 * math.sin(PI * k / 12))
        c.set_dash([0.1, 12]); c.set_line_cap(cairo.LINE_CAP_ROUND); setc(c, "#ff9f1a" if k % 2 else "#ffd23f"); c.set_line_width(11); c.stroke(); c.set_dash([])

def havan(c, t, x=640, y=640):
    rrect(c, x - 50, y - 26, 100, 32, 4); fs(c, "#c0623a", "#7a3a1a", 3)
    for k, (dx, h) in enumerate(((-18, 40), (0, 56), (18, 40))):
        fl = h * (1 + 0.15 * math.sin(t * 14 + k * 2))
        c.move_to(x + dx - 12, y - 26); c.curve_to(x + dx - 14, y - 26 - fl * 0.6, x + dx, y - 26 - fl * 0.8, x + dx, y - 26 - fl)
        c.curve_to(x + dx, y - 26 - fl * 0.8, x + dx + 14, y - 26 - fl * 0.6, x + dx + 12, y - 26); c.close_path(); fs(c, "#ff9f1a", "#e8432f", 2)

def garland(c, x, y):
    for k in range(13):
        a = PI * k / 12
        ell(c, x - 34 * math.cos(a), y + 70 * math.sin(a) * 0.9, 7, 7); setc(c, "#ff8c1a" if k % 2 else "#ffd23f"); c.fill()

def baby(c, x, y, s=1.0, glow=0.0):
    if glow > 0:
        gr = cairo.RadialGradient(x, y, 4, x, y, 70 * s); gr.add_color_stop_rgba(0, 1, 1, 0.8, 0.8 * glow); gr.add_color_stop_rgba(1, 1, 1, 0.8, 0)
        c.set_source(gr); c.arc(x, y, 70 * s, 0, 2 * PI); c.fill()
    c.save(); c.translate(x, y); c.scale(s, s)
    ell(c, 0, 8, 34, 24); fs(c, "#fff3d9", "#d9c39a", 2.5)
    ell(c, -16, -6, 18, 18); fs(c, "#f6d0ae", "#c9966a", 2)
    c.arc(-20, -8, 3, 0.1 * PI, 0.9 * PI); c.arc(-11, -8, 3, 0.1 * PI, 0.9 * PI); setc(c, "#3a2414"); c.set_line_width(1.6); c.stroke()
    ell(c, -16, 0, 2.5, 1.6); setc(c, "#e0567f"); c.fill()
    c.move_to(-6, 14); c.curve_to(10, 4, 24, 10, 30, 18); setc(c, "#ffd23f"); c.set_line_width(3); c.stroke()
    c.restore()

def star(c, x, y, r, a=1.0, face=0.0, tw=0.0):
    gr = cairo.RadialGradient(x, y, 1, x, y, r * 3); gr.add_color_stop_rgba(0, 1, 0.96, 0.7, 0.7 * a); gr.add_color_stop_rgba(1, 1, 0.96, 0.7, 0)
    c.set_source(gr); c.arc(x, y, r * 3, 0, 2 * PI); c.fill()
    c.save(); c.translate(x, y); c.rotate(tw)
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * 0.45; ang = -PI / 2 + i * PI / 5; pts.append((rr * math.cos(ang), rr * math.sin(ang)))
    poly(c, pts); fs(c, hexc("#ffe066", a), hexc("#f5a400", a), 2)
    if face > 0:
        setc(c, (0.4, 0.25, 0.05, a * face)); ell(c, -r * 0.2, -r * 0.05, r * 0.07, r * 0.09); c.fill(); ell(c, r * 0.2, -r * 0.05, r * 0.07, r * 0.09); c.fill()
        c.arc(0, r * 0.08, r * 0.18, 0.15 * PI, 0.85 * PI); c.set_line_width(max(1.5, r * 0.06)); c.stroke()
    c.restore()

STAR_POS = [(250, 110), (420, 70), (590, 120), (760, 60), (930, 110), (1100, 70), (340, 200)]

def heart(c, x, y, s, a=1.0, col="#ff4f8b"):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.move_to(0, 8); c.curve_to(-22, -6, -12, -26, 0, -12); c.curve_to(12, -26, 22, -6, 0, 8); setc(c, hexc(col, a)); c.fill(); c.restore()

def sparkles(c, t, cx, cy, rad, n=14, a=1.0, seed=1):
    r = random.Random(seed)
    for k in range(n):
        ang = r.uniform(0, 2 * PI); d = rad * r.uniform(0.4, 1.0); ph = r.uniform(0, 6)
        al = a * (0.5 + 0.5 * math.sin(t * 5 + ph))
        x = cx + d * math.cos(ang + t * 0.4); y = cy + d * math.sin(ang + t * 0.4)
        c.save(); c.translate(x, y); c.rotate(t + ph)
        poly(c, [(0, -9), (2, -2), (9, 0), (2, 2), (0, 9), (-2, 2), (-9, 0), (-2, -2)]); setc(c, (1, 1, 0.85, al)); c.fill(); c.restore()

# ---------------- scenes
def tinku_room(c, t, closing=False):
    bg_room(c, t)
    op = ease(prog(t, S("book_open") + 0.6, S("book_open") + 1.6))
    cl = ease(prog(t, BOUNDS["room2"] + 0.2, BOUNDS["room2"] + 1.0)) if closing else 0
    storybook(c, t, 930, 590, 1.0 if closing else op, cl)
    arms = list(talk("tinku", t, 0.5)); m = mo("tinku", t); hopy = 0
    if active(t, "room_wave", 0.2, 0.5): arms[1] = (2.1, 0.5 + 0.5 * math.sin(t * 11))
    if active(t, "icons"): arms = [(1.2, 0.9 + 0.2 * math.sin(t * 3)), (1.2, 0.9 + 0.2 * math.sin(t * 3 + 1))]
    if active(t, "book_open", 0, 1.5): arms[1] = (1.35, 0.15)
    if closing and active(t, "next"): arms[1] = (2.0, 0.9)
    if closing and active(t, "bye", 0, 1.0): arms = [(0.15, 0.3), (2.1, 0.5 + 0.5 * math.sin(t * 11))]; hopy = abs(math.sin(t * 6)) * 10
    tx = 470
    tinku(c, tx, 620, t, 1.0, tuple(arms), m, 0.3, blink(t, 0.5), hopy)
    if active(t, "icons", 0, 0.8):
        for i, kind in enumerate(("crown", "queen", "bow", "bulb")):
            p = back(prog(t, S("icons") + 0.5 + i * 0.8, S("icons") + 0.9 + i * 0.8))
            if p <= 0: continue
            x = 250 + i * 150; y = 150 + 8 * math.sin(t * 3 + i)
            c.save(); c.translate(x, y); c.scale(p, p)
            ell(c, 0, 0, 52, 52); fs(c, "#ffffff", "#ffb000", 5)
            if kind == "crown":
                c.translate(0, 18); c.scale(0.55, 0.55); c.translate(0, 60)
                rrect(c, -62, -52, 124, 18, 8); gold(c, 3); c.move_to(-58, -40); c.curve_to(-60, -80, -44, -118, 0, -132); c.curve_to(44, -118, 60, -80, 58, -40); c.close_path(); gold(c, 3)
                ell(c, 0, -96, 13, 16); fs(c, "#d81b3c", "#7a0d1f", 2)
            elif kind == "queen":
                c.translate(0, 28); c.scale(0.7, 0.7); c.translate(0, 40)
                for (bx, tx_, ty) in ((-36, -30, -84), (0, 0, -110), (36, 30, -84)):
                    poly(c, [(bx - 16, -40), (tx_, ty), (bx + 16, -40)]); gold(c, 2)
                rrect(c, -50, -48, 100, 16, 6); gold(c, 2); ell(c, 0, -70, 8, 10); fs(c, "#d81b3c", "#7a0d1f", 2)
            elif kind == "bow":
                c.arc(-20, 0, 38, -0.42 * PI, 0.42 * PI); setc(c, "#8a4b1f"); c.set_line_width(6); c.stroke()
                c.move_to(-20 + 38 * math.cos(-0.42 * PI), 38 * math.sin(-0.42 * PI)); c.line_to(-20 + 38 * math.cos(0.42 * PI), 38 * math.sin(0.42 * PI)); setc(c, "#666666"); c.set_line_width(1.5); c.stroke()
                c.move_to(-26, 0); c.line_to(26, 0); setc(c, "#8a5a2b"); c.set_line_width(3); c.stroke(); poly(c, [(26, -6), (38, 0), (26, 6)]); setc(c, "#8a93a6"); c.fill()
            else:
                ell(c, 0, -6, 22, 24); fs(c, "#ffe066", "#e0a000", 3); rrect(c, -10, 16, 20, 14, 3); fs(c, "#b8c4d6", "#7d8aa0", 2)
                for a_ in range(5):
                    ang = -PI / 2 + (a_ - 2) * 0.5; c.move_to(30 * math.cos(ang), -6 + 30 * math.sin(ang)); c.line_to(40 * math.cos(ang), -6 + 40 * math.sin(ang))
                setc(c, "#ffb000"); c.set_line_width(3); c.stroke()
            c.restore()
    if closing:
        p2 = back(prog(t, S("next") + 0.2, S("next") + 0.8))
        if p2 > 0 and t < S("bye") + 0.5:
            c.save(); c.translate(860, 240); c.scale(p2, p2)
            for k, (dx, dy, r) in enumerate(((-150, 150, 12), (-120, 120, 18))):
                ell(c, dx - 60, dy, r, r); fs(c, "#ffffff", "#9aa5b8", 3)
            ell(c, 0, 0, 200, 140); fs(c, "#ffffff", "#9aa5b8", 4)
            c.save(); ell(c, 0, 0, 196, 136); c.clip()
            c.push_group(); hero(c, "bheeshm", 0, 230, t, 0.48, (0.25, 0.35)); pat = c.pop_group()
            setc(c, "#3a3f5c"); c.mask(pat)
            c.restore()
            draw_text(c, "?", 120, -40, 90, "#ff8c1a", "#ffffff", 6, lang="en")
            draw_text(c, "?", -130, -60, 60, "#2f7bff", "#ffffff", 5, lang="en")
            c.restore()

def palace_scene(c, t):
    bg_palace(c, t)
    a = S("shantanu_in")
    x = keyed(t, [(a, 1450), (a + 2.4, 760)])
    walking = a <= t <= a + 2.4
    m = mo("shantanu", t)
    arms = ((0.25 + 0.3 * math.sin(t * 9), 0.3), (0.25 - 0.3 * math.sin(t * 9), 0.3)) if walking else talk("shantanu", t, 1.0)
    hero(c, "shantanu", x, GY, t, CS * 1.05, arms, m, -0.5, blink(t, 0.7), abs(math.sin(t * 9)) * 8 if walking else 0, face=-1 if walking else 1)

def river_scene(c, t):
    bg_river(c, t)
    x = keyed(t, [(S("to_river"), -150), (S("to_river") + 3.0, 330)])
    walking = S("to_river") <= t <= S("to_river") + 3.0
    m = mo("shantanu", t); arms = list(talk("shantanu", t, 1.0)); kneel = 0; mood = None
    if walking: arms = [(0.25 + 0.3 * math.sin(t * 9), 0.3), (0.25 - 0.3 * math.sin(t * 9), 0.3)]
    if active(t, "propose", 0.2, 0.5): kneel = ease(prog(t, S("propose") - 0.2, S("propose") + 0.4)) * (1 - ease(prog(t, E("propose") + 0.2, E("propose") + 0.6))); arms[1] = (0.9, 0.7)
    if active(t, "promise"): arms = [(0.15, -2.0), (0.45, 1.1 + 0.2 * math.sin(t * 1.5))]
    # glow orb from the water
    g0 = S("glow")
    ga = ease(prog(t, g0 + 0.3, g0 + 1.4))
    rise = ease(prog(t, S("ganga_rise") + 0.2, S("ganga_rise") + 2.2))
    gx = 880
    if ga > 0:
        r = 60 + 120 * ga + 20 * math.sin(t * 4)
        gr = cairo.RadialGradient(gx, 560, 5, gx, 560, r * 2); gr.add_color_stop_rgba(0, 1, 1, 0.9, 0.9 * ga); gr.add_color_stop_rgba(1, 0.6, 0.9, 1, 0)
        c.set_source(gr); c.arc(gx, 560, r * 2, 0, 2 * PI); c.fill()
    hero(c, "shantanu", x, GY, t, CS * 1.05, tuple(arms), m, 0.6, blink(t, 0.7), abs(math.sin(t * 9)) * 8 if walking else 0, kneel=kneel, face=1)
    if rise > 0:
        c.save(); c.rectangle(0, 0, W, 602); c.clip()
        ga_arms = list(talk("ganga", t, 2.0)); gm = mo("ganga", t)
        if active(t, "condition", 0, 0.3) or active(t, "condition2"): ga_arms[1] = (0.7, 1.9)
        if active(t, "ga_intro"): ga_arms[0] = (0.2, -1.9)
        hero(c, "ganga", gx, GY + 420 * (1 - rise), t, CS * 1.05, tuple(ga_arms), gm, -0.6, blink(t, 1.3), face=-1)
        c.restore()
        ell(c, gx, 602, 90 + 20 * math.sin(t * 3), 14); setc(c, (1, 1, 1, 0.45)); c.set_line_width(3); c.stroke()
        sparkles(c, t, gx, 420, 160, 12, 0.8 * rise, 3)
    if active(t, "propose", 0, 0.6):
        for k in range(4):
            dt = t - S("propose") - k * 0.5
            if 0 < dt < 2: heart(c, 520 + k * 50, 380 - dt * 70, 1.2, clamp(1 - dt / 2))
    if active(t, "promise", 0, 1.0):
        p = ease(prog(t, S("promise") + 1.2, S("promise") + 2.2))
        c.arc(600, 330, 60 + 280 * p, 0, 2 * PI); setc(c, (1, 0.85, 0.3, 0.7 * (1 - p))); c.set_line_width(8); c.stroke()
        sparkles(c, t, 600, 330, 200, 10, 1 - p * 0.5, 7)

def wedding_scene(c, t):
    bg_wedding(c, t)
    havan(c, t, 640, 650)
    sx, gx = 520, 770
    sh = hero(c, "shantanu", sx, GY, t, CS, ((0.15, 0.25), (0.3, 1.2)), 0, 0.5, blink(t, 0.7))
    gh = hero(c, "ganga", gx, GY, t, CS, ((0.3, 1.2), (0.15, 0.25)) if t < S("baby1") + 0.3 else ((0.45, 1.6), (0.45, 1.6)), 0, -0.5, blink(t, 1.3), item_on=t < S("baby1") + 0.3)
    gp = ease(prog(t, S("wedding") + 0.8, S("wedding") + 1.6))
    if gp > 0:
        garland(c, sx, GY - 0.6 * 336 + 30 * (1 - gp) - 0); garland(c, gx, GY - 0.6 * 332 + 30 * (1 - gp))
    if t >= S("baby1") + 0.3:  # baby in Ganga's arms
        hx = (gh[0][0] + gh[1][0]) / 2; hy = (gh[0][1] + gh[1][1]) / 2
        p = back(prog(t, S("baby1") + 0.3, S("baby1") + 0.9))
        baby(c, gx - 30, GY - 230, 0.9 * p, 0.5)
        for k in range(3):
            dt = t - S("baby1") - 0.8 - k * 0.6
            if 0 < dt < 2: heart(c, gx - 100 + k * 60, GY - 300 - dt * 60, 1.0, clamp(1 - dt / 2))
    r = random.Random(2)
    for k in range(40):  # petals
        x0 = r.uniform(0, W); sp = r.uniform(50, 110); ph = r.uniform(0, 700)
        y = (ph + (t - BOUNDS["wedding"]) * sp) % 760 - 40; x = x0 + 25 * math.sin(t * 1.5 + k)
        c.save(); c.translate(x, y); c.rotate(t * 2 + k); ell(c, 0, 0, 8, 4.5); setc(c, ["#ff5f8f", "#ff9f1a", "#ffd23f"][k % 3]); c.fill(); c.restore()

def stars_scene(c, t, eighth=False):
    bg_river(c, t, dusk=1.0)
    n_stars = 0
    if not eighth:
        if t >= STAR1_T + 1.4: n_stars = 1
        for k, st in enumerate(SEVEN_TIMES):
            if t >= st: n_stars = max(n_stars, k + 1)
    else:
        n_stars = 7
    face = ease(prog(t, S("vasus") + 0.4, S("vasus") + 1.2)) if not eighth else 1.0
    for k in range(n_stars):
        x, y = STAR_POS[k]
        app = back(prog(t, (SEVEN_TIMES[k] if k else STAR1_T + 1.4) - 0.05, (SEVEN_TIMES[k] if k else STAR1_T + 1.4) + 0.35)) if not eighth else 1
        drift = -12 * ease(prog(t, S("free"), E("free") + 1.0)) if not eighth else -12
        star(c, x, y + drift, 22 * app + 2 * math.sin(t * 3 + k), 1.0, face, 0.1 * math.sin(t + k))
    if not eighth:
        for k, st in enumerate(SEVEN_TIMES):  # counting numbers
            dt = t - st
            if 0 <= dt < 0.7:
                draw_text(c, ["१", "२", "३", "४", "५", "६", "७"][k] + "  " + str(k + 1), 640, 300 - dt * 40, 70, "#ffd23f", "#7a3a00", 6, alpha=clamp(1 - dt / 0.7))
    # characters
    sad = t >= S("sad") - 0.2 if not eighth else False
    if not eighth:
        gx = keyed(t, [(BOUNDS["stars"], 760), (S("river_baby") + 1.6, 900)])
        sx = 300
        sm = None if t < S("sad") - 0.3 else "sad"
        hero(c, "shantanu", sx, GY, t, CS * 1.05, (0.3, 0.3), 0, 0.6, blink(t, 0.7) or sm == "sad" and ((t % 4) < 1.2), mood=sm)
        holding = t < STAR1_T + 0.2 or (S("seven") <= t <= E("seven"))
        hero(c, "ganga", gx, GY, t, CS * 1.05, ((0.45, 1.6), (0.45, 1.6)) if holding else (0.35, 1.6 if STAR1_T <= t <= STAR1_T + 1.5 else 0.35), 0, -0.4, blink(t, 1.3), face=-1, item_on=not holding and not (STAR1_T <= t <= STAR1_T + 1.5))
        if holding: baby(c, gx + 4, GY - 205, 0.85)
        # star rising out of her hands
        p = prog(t, STAR1_T, STAR1_T + 1.5)
        if 0 < p < 1:
            x = lerp(gx + 10, STAR_POS[0][0], ease(p)); y = lerp(GY - 230, STAR_POS[0][1], ease(p)) - 80 * math.sin(PI * p)
            baby(c, x, y, 0.8 * (1 - p) + 0.01, 1.0); star(c, x, y, 10 + 12 * p, p)
        for st in SEVEN_TIMES[1:]:
            p = prog(t, st - 0.5, st)
            if 0 < p < 1:
                star(c, lerp(gx, STAR_POS[SEVEN_TIMES.index(st)][0], ease(p)), lerp(GY - 230, STAR_POS[SEVEN_TIMES.index(st)][1], ease(p)), 8 + 12 * p, 1)
        if active(t, "vasus", 0, 2):
            sparkles(c, t, 680, 120, 480, 24, 0.8, 9)
    else:
        a8 = S("baby8")
        leave = ease(prog(t, S("ganga_leave") + 0.3, S("ganga_leave") + 3.0))
        gx = keyed(t, [(BOUNDS["eighth"], 600), (a8 + 3.4, 870), (S("ganga_leave"), 870), (S("ganga_leave") + 1.0, 920)])
        sx = keyed(t, [(S("stop") - 0.3, -160), (S("stop") + 1.4, 430)])
        run = S("stop") - 0.3 <= t <= S("stop") + 1.4
        sm = "sad" if t >= S("broken") else None
        s_arms = [(0.3 + 0.5 * math.sin(t * 12), 0.6), (1.4, 0.2)] if run else ([(0.3, 0.4), (1.3, 0.3)] if active(t, "stop") else list(talk("shantanu", t, 1.0)))
        if active(t, "wait", 0, 3): s_arms = [(0.15, -2.0), (0.15, -1.6)]
        hero(c, "shantanu", sx, GY, t, CS * 1.05, tuple(s_arms), mo("shantanu", t), 0.6, blink(t, 0.7), abs(math.sin(t * 12)) * 12 if run else 0, mood=sm)
        walking = BOUNDS["eighth"] <= t <= a8 + 3.4
        face = 1 if walking else -1
        c.save()
        if leave > 0: c.rectangle(0, 0, W, 602); c.clip()
        gm = mo("ganga", t)
        hero(c, "ganga", gx, GY + 440 * leave, t, CS * 1.05, ((0.45, 1.6), (0.45, 1.6)), gm, -0.5 if face < 0 else 0.5, blink(t, 1.3), abs(math.sin(t * 7)) * 6 if walking else 0, face=face, mood="sad" if active(t, "must_go") else None, item_on=False)
        baby(c, gx + 4 * face, GY + 440 * leave - 205, 0.85, 0.6 if active(t, "eighth_vasu", 0, 2) else 0)
        c.restore()
        if leave > 0:
            ell(c, gx, 602, 90 + 30 * leave, 14); setc(c, (1, 1, 1, 0.5 * (1 - leave * 0.5))); c.set_line_width(3); c.stroke()
            sparkles(c, t, gx, 450, 150, 16, 1 - leave * 0.6, 5)

def title_card(c, t):
    gr = cairo.RadialGradient(640, 380, 40, 640, 380, 900); gr.add_color_stop_rgba(0, *hexc("#ffe680")); gr.add_color_stop_rgba(1, *hexc("#ff7a1a")); c.set_source(gr); c.paint()
    c.save(); c.translate(640, 380); c.rotate(t * 0.12)
    for i in range(18):
        c.move_to(0, 0); c.arc(0, 0, 1200, i * PI / 9, i * PI / 9 + PI / 18); c.close_path(); setc(c, (1, 1, 1, 0.14)); c.fill()
    for r in (150, 210):
        for k in range(16):
            a = k * PI / 8 + t * 0.2 * (1 if r == 150 else -1)
            c.save(); c.rotate(a); c.translate(r, 0); ell(c, 0, 0, 22, 9); setc(c, (1, 1, 1, 0.25)); c.fill(); c.restore()
    c.restore()
    p = back(prog(t, 0.2, 0.9))
    if p > 0:
        c.save(); c.translate(640, 250); c.scale(p, p)
        draw_text(c, "टिंकू की महाभारत", 0, 0, 120, "#c2410c", "#ffffff", 12)
        c.restore()
    p2 = back(prog(t, 0.9, 1.4))
    if p2 > 0:
        c.save(); c.translate(640, 400); c.scale(p2, p2)
        rrect(c, -330, -48, 660, 96, 48); fs(c, "#d81b60", "#ffffff", 6)
        draw_text(c, f"एपिसोड {EP_NUM}  •  {EP_TITLE_HI}", 0, -6, 46, "#ffffff")
        draw_text(c, f"Episode {EP_NUM} · {EP_TITLE_EN}", 0, 30, 20, "#ffe0ef", lang="en")
        c.restore()
    pt = back(prog(t, 0.6, 1.2))
    tinku(c, 170, 760 - 160 * pt, t, 0.95, (0.3, 2.3 + 0.3 * math.sin(t * 10)), mo("tinku", t), 0.3, blink(t, 0.5))
    ps = back(prog(t, 1.2, 1.8))
    hero(c, "shantanu", 1060, 900 - 230 * ps, t, 0.7, (0.25, 0.25)); hero(c, "ganga", 1200, 900 - 230 * ps, t, 0.7, (0.25, 0.25), face=-1)

def outro_card(c, t):
    lt = t - T_OUTRO
    gr = cairo.RadialGradient(640, 380, 40, 640, 380, 900); gr.add_color_stop_rgba(0, *hexc("#fff3c4")); gr.add_color_stop_rgba(1, *hexc("#ffb000")); c.set_source(gr); c.paint()
    r = random.Random(5)
    for k in range(60):
        x0 = r.uniform(0, W); sp = r.uniform(60, 130); ph = r.uniform(0, 800)
        y = (ph + lt * sp) % 800 - 40; x = x0 + 20 * math.sin(lt * 2 + k)
        c.save(); c.translate(x, y); c.rotate(lt * 2 + k); ell(c, 0, 0, 9, 5); setc(c, ["#ff5f8f", "#ff8c1a", "#ffd23f", "#e8432f"][k % 4]); c.fill(); c.restore()
    p = back(prog(lt, 0.2, 0.8))
    if p > 0:
        c.save(); c.translate(700, 220); c.scale(p, p); draw_text(c, "फिर मिलेंगे!", 0, 0, 130, "#d81b60", "#ffffff", 12); c.restore()
    p2 = back(prog(lt, 0.8, 1.3))
    if p2 > 0:
        c.save(); c.translate(700, 350); c.scale(p2, p2)
        draw_text(c, "See you next time!", 0, 0, 44, "#7c2d12", "#ffffff", 5, lang="en")
        draw_text(c, "अगला एपिसोड: देवव्रत की वापसी", 0, 64, 38, "#2f6fd8", "#ffffff", 4)
        c.restore()
    tinku(c, 220, 680, t, 1.05, (0.3, 2.3 + 0.3 * math.sin(t * 11)), mo("tinku", t), 0.3, blink(t, 0.5), abs(math.sin(t * 6)) * 12)

# ---------------- overlay: Tinku inset during the story, captions
STORY = ("palace", "river", "wedding", "stars", "eighth")

def tinku_inset(c, t):
    if scene_at(t) not in STORY: return
    on = any(l["speaker"] == "tinku" and l["start"] - 0.4 <= t <= l["end"] + 0.4 for l in LINES)
    a = getattr(tinku_inset, "a", 0.0)
    target = 1.0 if on else 0.0
    # smooth alpha from distance to nearest Tinku line edge
    best = 0.0
    for l in LINES:
        if l["speaker"] != "tinku": continue
        best = max(best, clamp(min(t - (l["start"] - 0.5), (l["end"] + 0.5) - t) / 0.3))
    a = best
    if a <= 0: return
    cx, cy, R = 104, 104, 82
    c.save(); c.translate(cx, cy); s = 0.85 + 0.15 * back(a); c.scale(s, s); c.translate(-cx, -cy)
    c.push_group()
    ell(c, cx, cy, R + 6, R + 6); setc(c, "#ff8c1a"); c.fill()
    ell(c, cx, cy, R, R); setc(c, "#bfe6ff"); c.fill()
    c.save(); ell(c, cx, cy, R, R); c.clip()
    tinku(c, cx, cy + 222, t, 0.72, (0.3, 0.3 + 0.4 * mo("tinku", t)), mo("tinku", t), 0.4, blink(t, 0.5))
    c.restore()
    draw_text(c, "टिंकू", cx, cy + R + 4, 26, "#ffffff", "#ff8c1a", 4)
    c.pop_group_to_source(); c.paint_with_alpha(a)
    c.restore()

def captions(c, t):
    cur = None
    for i, l in enumerate(LINES):
        nxt = LINES[i + 1]["start"] if i + 1 < len(LINES) else 1e9
        if l["start"] - 0.12 <= t <= min(l["end"] + 0.6, nxt - 0.12): cur = l
    if not cur or t >= T_OUTRO: return
    a = clamp((t - cur["start"] + 0.12) / 0.15)
    words = cur["en"].split()
    c.select_font_face("Fredoka", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); c.set_font_size(31)
    sp = c.text_extents(" ").x_advance; ws = [c.text_extents(w).x_advance for w in words]
    rows, row, rw = [], [], 0
    for w, wd in zip(words, ws):
        if row and rw + sp + wd > 1060: rows.append((row, rw)); row, rw = [], 0
        rw += (sp if row else 0) + wd; row.append((w, wd))
    rows.append((row, rw))
    lh = 40; bw = max(r[1] for r in rows) + 56; bh = len(rows) * lh + 22
    bx, by = 640 - bw / 2, 708 - bh
    name, col = NAMES[cur["speaker"]]
    c.push_group()
    rrect(c, bx + 3, by + 5, bw, bh, 22); setc(c, (0.1, 0.05, 0.2, 0.25)); c.fill()
    rrect(c, bx, by, bw, bh, 22); fs(c, (1, 1, 1, 0.95), hexc(col), 5)
    tw = text_surface(name, 26, "#ffffff", None, 0, "hi").get_width()
    rrect(c, bx + 18, by - 22, tw + 24, 40, 20); fs(c, col, (1, 1, 1, 1), 3)
    draw_text(c, name, bx + 30, by - 2, 26, "#ffffff", None, 0, anchor="l")
    c.select_font_face("Fredoka", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); c.set_font_size(31)
    for li, (row, rw) in enumerate(rows):
        x = 640 - rw / 2; y = by + 11 + lh * li + 30
        for w, wd in row:
            c.move_to(x, y); setc(c, "#2b2d42"); c.show_text(w); x += wd + sp
    c.pop_group_to_source(); c.paint_with_alpha(a)

def draw_scene(c, name, t):
    if name == "title": title_card(c, t)
    elif name == "room": tinku_room(c, t)
    elif name == "palace": palace_scene(c, t)
    elif name == "river": river_scene(c, t)
    elif name == "wedding": wedding_scene(c, t)
    elif name == "stars": stars_scene(c, t)
    elif name == "eighth": stars_scene(c, t, eighth=True)
    elif name == "room2": tinku_room(c, t, closing=True)
    elif name == "outro": outro_card(c, t)

def frame(t, surf=None):
    surf = surf or cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(surf)
    cur = scene_at(t); i = ORDER.index(cur)
    t0 = BOUNDS[cur]; p = ease(prog(t, t0, t0 + 0.9))
    if i > 0 and p < 1:
        draw_scene(c, ORDER[i - 1], t)
        c.save(); c.arc(640, 360, 760 * p, 0, 2 * PI); c.clip(); draw_scene(c, cur, t); c.restore()
        c.arc(640, 360, 760 * p, 0, 2 * PI); setc(c, "#ffd23f"); c.set_line_width(12); c.stroke()
    else:
        draw_scene(c, cur, t)
    tinku_inset(c, t)
    captions(c, t)
    f = clamp(min(t / 0.4, (DURATION - t) / 1.5))
    if f < 1: c.rectangle(0, 0, W, H); setc(c, (0, 0, 0, 1 - f)); c.fill()
    return surf

if __name__ == "__main__":
    import os; os.makedirs("stills", exist_ok=True)
    for ts in sys.argv[1:]:
        frame(float(ts)).write_to_png(f"stills/f_{float(ts):06.2f}.png")
