"""Story: The Giant Ghost in the Fog. Starts straight in the story (no title card, no brand text)."""
import sys, os, math, random, numpy as np, soundfile as sf, cairo
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "mahabharat", "lib"))
from chars import *
from scenery import sky, lin
from cues import *
from script import NAMES, NEXT

W, H, FPS = 1280, 720, 30
GY = 612
LAMP = (1150, 238)          # streetlight bulb
KIT = (1000, 470)           # Barfi sits on the boundary wall
SHAD = (735, 520)           # foot of the giant shadow on the fog

def prog(t, a, b): return clamp((t - a) / (b - a)) if b > a else float(t >= a)
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def back(x, s=1.7):
    x = clamp(x); x -= 1; return x * x * ((s + 1) * x + s) + 1
def lerp(a, b, x): return a + (b - a) * x
def active(t, cue, pre=0.0, post=0.0): return has(cue) and S(cue) - pre <= t <= E(cue) + post
def blink(t, off): return ((t + off) % 3.6) < 0.12

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
def talk(spk, t, seed=0.0):
    m = mo(spk, t); br = 0.03 * math.sin(t * 1.6 + seed)
    if not speaking(spk, t): return ((0.14 + br, 0.25), (0.14 - br, 0.25))
    return ((0.25 + 0.12 * math.sin(t * 0.9 + seed) + 0.1 * m, 0.5 + 0.4 * m), (0.55 + 0.25 * math.sin(t * 1.2 + seed) + 0.25 * m, 1.2 + 0.35 * math.sin(t * 1.8 + seed) + 0.3 * m))
SCARED = ((0.7, -1.9), (0.7, -1.9))
CARRY = ((0.9, 1.9), (0.9, 1.9))          # both hands in front holding the jalebi box
HIPS = ((0.45, -1.1), (0.45, -1.1))

# ---------------------------------------------------------------- background: foggy winter lane at dusk
def house(c, x, y, w, h, col, roof, t, seed):
    r = random.Random(seed)
    rrect(c, x, y, w, h, 4); fs(c, col, dark(col, 0.7), 2.5)
    poly(c, [(x - 14, y + 4), (x + w / 2, y - h * 0.32), (x + w + 14, y + 4)]); fs(c, roof, dark(roof, 0.7), 2.5)
    for i in range(2):
        for j in range(2):
            wx = x + 18 + i * (w - 70); wy = y + 18 + j * (h * 0.42)
            lit = r.random() < 0.75
            rrect(c, wx, wy, 34, 34, 4); fs(c, "#ffd97a" if lit else "#3a4566", dark(col, 0.55), 2)
            if lit:
                rg = cairo.RadialGradient(wx + 17, wy + 17, 4, wx + 17, wy + 17, 50); rg.add_color_stop_rgba(0, 1, 0.85, 0.45, 0.35); rg.add_color_stop_rgba(1, 1, 0.85, 0.45, 0)
                c.set_source(rg); c.arc(wx + 17, wy + 17, 50, 0, 2 * PI); c.fill()
            c.move_to(wx + 17, wy); c.line_to(wx + 17, wy + 34); c.move_to(wx, wy + 17); c.line_to(wx + 34, wy + 17); setc(c, dark(col, 0.55)); c.set_line_width(2); c.stroke()

def streetlight(c, t, on=1.0):
    x, y = LAMP
    rrect(c, x + 34, y - 6, 14, 382, 5); fs(c, "#3a3f5a", "#1a1f2a", 2)
    c.move_to(x + 41, y + 4); c.curve_to(x + 41, y - 26, x + 20, y - 30, x, y - 18); setc(c, "#3a3f5a"); c.set_line_width(9); c.stroke()
    rrect(c, x - 22, y - 14, 44, 18, 7); fs(c, "#ffe9a0", "#3a3f5a", 3)
    rg = cairo.RadialGradient(x, y, 10, x, y, 330); rg.add_color_stop_rgba(0, 1, 0.92, 0.6, 0.55 * on); rg.add_color_stop_rgba(1, 1, 0.92, 0.6, 0)
    c.set_source(rg); c.arc(x, y, 330, 0, 2 * PI); c.fill()

def wall(c, x0, x1, top, bot, col="#c46a4a"):
    rrect(c, x0, top, x1 - x0, bot - top, 4); fs(c, col, dark(col, 0.6), 3)
    for row in range(int((bot - top) / 22)):
        y = top + 22 * (row + 1); c.move_to(x0, y); c.line_to(x1, y)
        off = 0 if row % 2 else 30
        for bx in range(int(x0) + off, int(x1), 60): c.move_to(bx, y - 22); c.line_to(bx, y)
    setc(c, (0.35, 0.12, 0.08, 0.45)); c.set_line_width(2); c.stroke()
    rrect(c, x0 - 6, top - 12, x1 - x0 + 12, 16, 4); fs(c, "#e0d6c8", "#8a7a6a", 2)

def fog(c, t, k=1.0, seed=3, ymin=260, ymax=640, n=16):
    r = random.Random(seed)
    for i in range(n):
        y = r.uniform(ymin, ymax); sp = r.uniform(6, 18); w = r.uniform(260, 520)
        x = (r.uniform(0, 1600) + t * sp) % 1800 - 260
        g = cairo.RadialGradient(x, y, 10, x, y, w * 0.55)
        a = k * r.uniform(0.18, 0.32)
        g.add_color_stop_rgba(0, 0.9, 0.92, 0.97, a); g.add_color_stop_rgba(1, 0.9, 0.92, 0.97, 0)
        c.save(); c.translate(x, y); c.scale(1, 0.35); c.translate(-x, -y); c.set_source(g); c.arc(x, y, w * 0.55, 0, 2 * PI); c.fill(); c.restore()

def lane_bg(c, t, dark_k=0.0):
    sky(c, [(0, lerp_hex("#4a5f8f", "#1e2846", dark_k)), (0.7, lerp_hex("#9aaac8", "#4a5578", dark_k)), (1, lerp_hex("#c8d2e4", "#6a7596", dark_k))], 470)
    # far rooftops
    r = random.Random(9)
    x = -20
    while x < W:
        w = r.uniform(90, 160); h = r.uniform(70, 150)
        rrect(c, x, 470 - h, w, h + 10, 3); setc(c, (0.42, 0.47, 0.6, 1)); c.fill(); x += w - 6
    fog(c, t, 0.7, seed=11, ymin=300, ymax=460, n=10)
    house(c, 40, 300, 200, 190, "#f2c97a", "#c0503a", t, 1)
    house(c, 300, 285, 220, 205, "#9fd0c8", "#5a6fb0", t, 2)
    house(c, 580, 300, 200, 190, "#f0a6b8", "#8a4a7a", t, 3)
    # road + footpath
    c.rectangle(0, 488, W, 40); setc(c, "#b9b2a6"); c.fill()
    c.move_to(0, 528); c.line_to(W, 528); setc(c, "#8a8378"); c.set_line_width(3); c.stroke()
    lin(c, 0, 528, 0, 720, [(0, "#6f7484"), (1, "#4e5262")]); c.rectangle(0, 528, W, 192); c.fill()
    for k in range(7): rrect(c, k * 200 + 40, 640, 110, 10, 4); setc(c, (1, 1, 1, 0.55)); c.fill()
    wall(c, 820, 1290, KIT[1], 612)
    streetlight(c, t)
    # bare winter tree behind the wall
    c.save(); c.translate(1230, 470)
    for ang, ln in ((-1.75, 210), (-1.3, 150), (-2.2, 140)):
        c.move_to(0, 0); c.line_to(ln * math.cos(ang), ln * math.sin(ang)); setc(c, "#4a3a32"); c.set_line_width(14 if ln > 200 else 8); c.stroke()
    c.restore()
    if dark_k > 0: c.rectangle(0, 0, W, H); setc(c, (0.05, 0.07, 0.2, 0.45 * dark_k)); c.fill(); streetlight(c, t, dark_k)

def lerp_hex(a, b, k):
    ca, cb = hexc(a), hexc(b); return "#%02x%02x%02x" % tuple(int(255 * lerp(ca[i], cb[i], k)) for i in range(3))

# ---------------------------------------------------------------- Barfi (white kitten) + the giant shadow
def barfi(c, x, y, s, t, look=0.0, closed=False, glow=0.0, shake=0.0, alpha=1.0, flour=1.0):
    c.save(); c.translate(x + shake * 6 * math.sin(t * 50), y); c.scale(s, s)
    c.push_group()
    fur = "#fbfbff"
    ell(c, 0, 2, 40, 7); setc(c, (0, 0, 0, 0.15)); c.fill()
    c.save(); c.translate(30, -22); c.rotate(-0.6 + 0.35 * math.sin(t * 3)); ell(c, 0, -26, 8, 28); fs(c, fur, "#9aa4c4", 2.5); c.restore()   # tail
    ell(c, 0, -30, 34, 32); fs(c, fur, "#9aa4c4", 2.5)                      # body
    for px in (-16, 12): ell(c, px, -4, 11, 7); fs(c, fur, "#9aa4c4", 2)   # paws
    c.save(); c.translate(0, -74)
    for sgn in (-1, 1):
        poly(c, [(sgn * 30, -10), (sgn * 26, -46), (sgn * 6, -26)]); fs(c, fur, "#9aa4c4", 2.5)
        poly(c, [(sgn * 25, -14), (sgn * 23, -36), (sgn * 11, -24)]); setc(c, "#ffb3c6"); c.fill()
    ell(c, 0, 0, 34, 30); fs(c, fur, "#9aa4c4", 2.5)
    for ex in (-13, 13):
        if glow > 0:
            rg = cairo.RadialGradient(ex, -4, 2, ex, -4, 26); rg.add_color_stop_rgba(0, 0.85, 1, 0.4, 0.8 * glow); rg.add_color_stop_rgba(1, 0.85, 1, 0.4, 0)
            c.set_source(rg); c.arc(ex, -4, 26, 0, 2 * PI); c.fill()
        if closed: c.move_to(ex - 7, -4); c.curve_to(ex - 3, 0, ex + 3, 0, ex + 7, -4); setc(c, "#3a3a4a"); c.set_line_width(2.5); c.stroke()
        else:
            ell(c, ex, -4, 8, 10); fs(c, "#c8f060" if glow > 0.3 else "#8fd0ff", "#3a3a4a", 2)
            ell(c, ex + look * 3, -4, 2.8, 8); setc(c, "#1a1a2a"); c.fill(); ell(c, ex - 2, -8, 2, 2); setc(c, (1, 1, 1, 0.9)); c.fill()
    poly(c, [(-4, 6), (4, 6), (0, 11)]); setc(c, "#ff8fae"); c.fill()
    c.move_to(0, 11); c.line_to(0, 15); c.arc(-4, 15, 4, 0.1 * PI, 0.9 * PI); c.move_to(8, 15); c.arc(4, 15, 4, 0.1 * PI, 0.9 * PI)
    setc(c, "#5a5a6a"); c.set_line_width(2); c.stroke()
    for sgn in (-1, 1):
        for k in (-1, 0, 1): c.move_to(sgn * 14, 10 + k * 4); c.line_to(sgn * 40, 6 + k * 8)
    setc(c, (0.4, 0.4, 0.5, 0.8)); c.set_line_width(1.5); c.stroke()
    c.restore()
    if flour > 0:   # flour dust puffs around her
        r = random.Random(2)
        for i in range(14):
            a = r.uniform(0, 2 * PI); d = r.uniform(30, 60) + 8 * math.sin(t * 3 + i)
            ell(c, d * math.cos(a), -45 + d * math.sin(a) * 0.8, 3, 3); setc(c, (1, 1, 1, 0.7 * flour)); c.fill()
    c.pop_group_to_source(); c.paint_with_alpha(alpha); c.restore()

def giant_shadow(c, t, k):
    """Barfi's shadow thrown on the fog by the streetlight: a huge, wobbly, blurry cat shape with two glowing eyes."""
    if k <= 0.01: return
    x, y = SHAD; s = 3.9 * (0.6 + 0.4 * k)
    rg = cairo.RadialGradient(x, y - 200, 40, x, y - 200, 380)   # lamp-lit fog screen behind the shadow
    rg.add_color_stop_rgba(0, 0.95, 0.93, 0.85, 0.62 * k); rg.add_color_stop_rgba(0.7, 0.92, 0.92, 0.9, 0.3 * k); rg.add_color_stop_rgba(1, 0.9, 0.92, 0.97, 0)
    c.save(); c.translate(x, y - 200); c.scale(1.1, 0.95); c.translate(-x, -(y - 200)); c.set_source(rg); c.arc(x, y - 200, 380, 0, 2 * PI); c.fill(); c.restore()
    wob = 0.04 * math.sin(t * 1.7)
    c.save(); c.translate(x, y); c.rotate(wob); c.scale(s, s * (1 + 0.03 * math.sin(t * 2.3)))
    for blur, a in ((14, 0.12), (8, 0.18), (3, 0.3), (0, 0.42)):
        c.save(); c.scale(1 + blur / 60, 1 + blur / 60)
        c.move_to(-34, 0); c.curve_to(-40, -40, -36, -64, -26, -78)
        c.line_to(-28, -118); c.line_to(-8, -100); c.curve_to(-3, -102, 3, -102, 8, -100); c.line_to(28, -118); c.line_to(26, -78)
        c.curve_to(36, -64, 40, -40, 34, 0); c.close_path()
        setc(c, (0.1, 0.11, 0.22, a * 1.25 * k)); c.fill()
        c.restore()
    c.save(); c.translate(36, -20); c.rotate(-0.5 + 0.3 * math.sin(t * 3)); ell(c, 0, -26, 9, 30); setc(c, (0.12, 0.14, 0.26, 0.4 * k)); c.fill(); c.restore()
    c.restore()
    bl = ((t + 0.4) % 3.1) < 0.15
    for ex in (-14, 14):   # glowing eyes
        ex_, ey = x + ex * s, y - 78 * s
        rg = cairo.RadialGradient(ex_, ey, 4, ex_, ey, 60); rg.add_color_stop_rgba(0, 0.85, 1, 0.4, 0.75 * k); rg.add_color_stop_rgba(1, 0.85, 1, 0.4, 0)
        c.set_source(rg); c.arc(ex_, ey, 60, 0, 2 * PI); c.fill()
        if not bl: ell(c, ex_, ey, 15, 20); setc(c, (0.9, 1, 0.55, 0.95 * k)); c.fill(); ell(c, ex_, ey, 4, 16); setc(c, (0.1, 0.15, 0.05, 0.9 * k)); c.fill()

def light_ray(c, t, k):
    """faint beam from the lamp past the kitten into the fog (the clue)."""
    if k <= 0: return
    lx, ly = LAMP
    c.move_to(lx, ly); c.line_to(SHAD[0] - 260, 160); c.line_to(SHAD[0] - 220, 560); c.close_path()
    g = cairo.LinearGradient(lx, ly, SHAD[0], 380); g.add_color_stop_rgba(0, 1, 0.95, 0.7, 0.28 * k); g.add_color_stop_rgba(1, 1, 0.95, 0.7, 0.0)
    c.set_source(g); c.fill()

def torch_beam(c, x0, y0, x1, y1, a):
    ang = math.atan2(y1 - y0, x1 - x0); L = math.hypot(x1 - x0, y1 - y0) + 80
    c.save(); c.translate(x0, y0); c.rotate(ang)
    g = cairo.LinearGradient(0, 0, L, 0); g.add_color_stop_rgba(0, 1, 0.97, 0.7, 0.55 * a); g.add_color_stop_rgba(1, 1, 0.97, 0.7, 0.08 * a)
    c.move_to(0, -8); c.line_to(L, -110); c.line_to(L, 110); c.line_to(0, 8); c.close_path(); c.set_source(g); c.fill()
    c.restore()
    rg = cairo.RadialGradient(x1, y1, 10, x1, y1, 140); rg.add_color_stop_rgba(0, 1, 0.97, 0.75, 0.4 * a); rg.add_color_stop_rgba(1, 1, 0.97, 0.75, 0)
    c.set_source(rg); c.arc(x1, y1, 140, 0, 2 * PI); c.fill()

def jalebi_box(c, x, y, s=1.0, open_=0.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, -34, -22, 68, 40, 6); fs(c, "#ff9f1a", "#b5600a", 3)
    rrect(c, -34, -26, 68, 10, 4); fs(c, "#ffc04d", "#b5600a", 2)
    for k in range(3):   # steam
        q = (t_glob[0] * 0.8 + k * 0.33) % 1
        c.move_to(-14 + k * 14, -30 - 30 * q); c.curve_to(-20 + k * 14, -40 - 30 * q, -8 + k * 14, -46 - 30 * q, -14 + k * 14, -56 - 30 * q)
        setc(c, (1, 1, 1, 0.6 * (1 - q))); c.set_line_width(3); c.stroke()
    draw_text(c, "जलेबी", 0, 0, 20, "#ffffff", "#b5600a", 3, lang="hi")
    c.restore()
t_glob = [0.0]

# ---------------------------------------------------------------- kids
def kid(name, c, x, y, t, arms, look=0.0, hop=0.0, s=0.88, lean=0.0):
    fn = {"tinku": tinku, "golu": golu}[name]
    fn(c, x, y, t, s, arms, mo(name, t), look, blink(t, {"tinku": 0.3, "golu": 2.2}[name]), hop, lean)

def moti_r(c, x, y, t, s=0.78, look=0.3, hop=0.0, wag=2.0, white=0.0):
    """Moti facing right (towards the fog); optional flour-white coat."""
    c.save(); c.translate(x, 0); c.scale(-1, 1); c.translate(-x, 0)
    c.push_group(); moti(c, x, y, t, s, mo("moti", t), look, blink(t, 0.9), hop, wag)
    if white > 0:
        c.set_operator(cairo.OPERATOR_ATOP); c.rectangle(x - 140, y - 240, 280, 260); setc(c, (1, 1, 1, 0.72 * white)); c.fill(); c.set_operator(cairo.OPERATOR_OVER)
    c.pop_group_to_source(); c.paint(); c.restore()

def golu_box(c, x, y, t, hop=0.0, s=0.88, scared=False):
    jalebi_box(c, x + 2, y - 122 * s / 0.88 - hop + (40 if scared else 0), 0.95)

def scene_lane(c, t, ghost_k=0.0):
    lane_bg(c, t, dark_k=ghost_k)
    barfi(c, KIT[0], KIT[1] - 12, 0.7, t, -0.6, False, glow=ghost_k, alpha=0.35 + 0.0 * ghost_k)
    fog(c, t, 1.0 + 0.8 * ghost_k, seed=5, ymin=380, ymax=620, n=12)
    light_ray(c, t, ghost_k)
    giant_shadow(c, t, ghost_k)
    walk = 1 - ease(prog(t, 0.0, 6.0)) if ghost_k == 0 else 0.0
    xs = {"tinku": 230 - 120 * walk, "golu": 400 - 120 * walk}
    walking = 0.02 < walk < 0.98
    for i, n in enumerate(("tinku", "golu")):
        a = talk(n, t, i); look = 0.2; hop = abs(math.sin(t * 8 + i)) * 8 if walking else 0.0
        scared = ghost_k > 0.3 and t >= S("huge") - 0.4
        if n == "golu":
            a = CARRY
            if active(t, "cold", 0, 0.5): a = ((1.6, -2.4), (1.6, -2.4))
            if scared: a = SCARED; hop = abs(math.sin(t * 14)) * 6
        if n == "tinku" and active(t, "dadi", 0, 0.3): a = (a[0], (1.5, 0.1))
        if n == "tinku" and scared: a = ((0.5, -0.4), (1.4, 0.1)); look = 0.6
        kid(n, c, xs[n], GY, t, a, look, hop)
        if n == "golu" and not (scared or active(t, "cold", 0, 0.5)): golu_box(c, xs[n], GY, t, hop)
    mh = abs(math.sin(t * 9)) * 16 if (active(t, "bark1", 0.1, 0.4) or active(t, "bark2", 0.1, 0.4)) else (abs(math.sin(t * 8)) * 8 if walking else 0)
    moti_r(c, 590 - 120 * walk, GY, t, hop=mh, wag=2.5 if ghost_k == 0 else 0.4)

def scene_hide(c, t):
    lane_bg(c, t, 1.0)
    barfi(c, KIT[0], KIT[1] - 12, 0.7, t, -0.6, False, glow=1.0, alpha=0.35)
    fog(c, t, 1.8, seed=5, ymin=380, ymax=620, n=12)
    clue = active(t, "blurry", 0, 0.6) or active(t, "shadow", 0, 1.5)
    light_ray(c, t, 1.0 + (0.8 if clue else 0))
    giant_shadow(c, t, 1.0)
    if active(t, "shadow", 0, 1.5):   # dotted line: lamp -> kitten -> shadow
        c.save(); c.set_dash([10, 10]); c.move_to(*LAMP); c.line_to(KIT[0], KIT[1] - 50); c.line_to(SHAD[0], SHAD[1] - 330)
        setc(c, (1, 0.9, 0.3, 0.9)); c.set_line_width(4); c.stroke(); c.restore()
        c.arc(KIT[0], KIT[1] - 50, 30 + 4 * math.sin(t * 8), 0, 2 * PI); setc(c, (1, 0.9, 0.3, 0.9)); c.set_line_width(4); c.stroke()
    duck = ease(prog(t, T_HIDE, T_HIDE + 0.5))
    xs = {"tinku": 260, "golu": 420}
    for i, n in enumerate(("tinku", "golu")):
        a = talk(n, t, i); look = 0.6
        if n == "golu": a = SCARED
        if n == "tinku" and t >= S("torch") - 0.2: a = (a[0], (1.45, 0.15))
        kid(n, c, xs[n], GY + 75 * duck, t, a, look, 0)
    moti_r(c, 590, GY + 60 * duck, t, hop=abs(math.sin(t * 9)) * 6 if active(t, "eatjal", 0, 0.5) else 0, wag=0.3)
    wall(c, 120, 700, GY - 120, H + 10, "#b8704e")   # front wall the kids hide behind
    golu_box_x = 420
    if t >= S("torch") + 0.6:
        torch_beam(c, 300, GY - 140, KIT[0], KIT[1] - 50, ease(prog(t, S("torch") + 0.6, S("torch") + 0.9)))

def scene_reveal(c, t):
    lane_bg(c, t, 0.75)
    fog(c, t, 1.0, seed=5, ymin=380, ymax=620, n=12)
    sk = 1 - ease(prog(t, T_REVEAL + 0.3, T_REVEAL + 1.5))
    giant_shadow(c, t, sk)
    rg = cairo.RadialGradient(KIT[0], KIT[1] - 40, 20, KIT[0], KIT[1] - 40, 320); rg.add_color_stop_rgba(0, 1, 0.97, 0.75, 0.4); rg.add_color_stop_rgba(1, 1, 0.97, 0.75, 0)
    c.set_source(rg); c.paint()
    torch_beam(c, 320, GY - 150, KIT[0], KIT[1] - 50, 1.0)
    pop = back(prog(t, T_REVEAL + 0.4, T_REVEAL + 1.0))
    glowing = active(t, "learn2", 0, 0.5)
    barfi(c, KIT[0], KIT[1] - 12, 0.7 + 0.7 * pop, t, -0.8, blink(t, 0.5), glow=1.0 if glowing else 0.25, shake=1.0 if active(t, "meow3", 0, 0.3) else 0)
    if active(t, "learn", 0, 0.5):   # small-near-light -> big shadow diagram
        bx, by = 760, 150
        rrect(c, bx - 210, by - 70, 420, 160, 20); fs(c, (1, 1, 1, 0.92), hexc("#2f7bff"), 4)
        ell(c, bx - 120, by, 14, 14); fs(c, "#ffe066", "#c99a00", 2)                  # light
        ell(c, bx - 60, by + 10, 10, 14); fs(c, "#ffffff", "#7a8ab8", 2)               # small cat
        c.move_to(bx - 120, by); c.line_to(bx + 140, by - 60); c.move_to(bx - 120, by); c.line_to(bx + 140, by + 70)
        setc(c, (1, 0.8, 0.2, 0.8)); c.set_line_width(2); c.stroke()
        ell(c, bx + 120, by + 5, 26, 52); setc(c, (0.12, 0.14, 0.26, 0.75)); c.fill()       # big shadow
        draw_text(c, "small + near the light = BIG shadow", bx, by + 64, 24, "#2b2d42", None, 0, lang="en")
    xs = {"tinku": 280, "golu": 450}
    for i, n in enumerate(("tinku", "golu")):
        a = talk(n, t, i); hop = 0.0; look = 0.6
        if n == "tinku": a = (a[0], (1.45, 0.15))
        if n == "golu" and active(t, "kitten", 0, 0.6): a = ((0.6, -1.4), (0.6, -1.4)); hop = abs(math.sin(t * 10)) * 10
        kid(n, c, xs[n], GY, t, a, look, hop)
        if n == "golu" and not active(t, "kitten", 0, 0.6): golu_box(c, xs[n], GY, t, hop)
    moti_r(c, 620, GY, t, hop=abs(math.sin(t * 8)) * 10 if t > T_REVEAL + 1.2 else 0, wag=3.0 if t > T_REVEAL + 1.2 else 0.5)

def gate(c):
    for px in (1000, 1250):
        rrect(c, px - 22, 330, 44, 290, 6); fs(c, "#e8d8c0", "#8a7a6a", 3); rrect(c, px - 30, 320, 60, 22, 6); fs(c, "#f4ead8", "#8a7a6a", 3)
    for k in range(9):
        x = 1030 + k * 24; c.move_to(x, 380); c.line_to(x, 612)
    setc(c, "#3a4a6a"); c.set_line_width(5); c.stroke()
    c.move_to(1022, 390); c.line_to(1228, 390); c.move_to(1022, 560); c.line_to(1228, 560); setc(c, "#3a4a6a"); c.set_line_width(6); c.stroke()
    rrect(c, 1045, 296, 160, 34, 8); fs(c, "#fff3d6", "#8a4a2a", 3); draw_text(c, "दादी का घर", 1125, 313, 22, "#8a4a2a", None, 0, lang="hi")

def scene_home(c, t):
    lane_bg(c, t, 0.6); gate(c)
    fog(c, t, 0.9, seed=8, ymin=420, ymax=620, n=8)
    walk = ease(prog(t, T_HOME, T_HOME + 3.0))
    xs = {"tinku": lerp(160, 360, walk), "golu": lerp(320, 520, walk)}
    walking = 0 < walk < 1
    # Barfi trots ahead to Moti, then shakes the flour off
    bx = lerp(520, 720, walk); sh = active(t, "shake", 1.6, 0.0) or (T_SHAKE <= t <= S("shake"))
    mwhite = ease(prog(t, T_SHAKE + 0.3, T_SHAKE + 1.1))
    for i, n in enumerate(("tinku", "golu")):
        a = talk(n, t, i); hop = abs(math.sin(t * 8 + i)) * 8 if walking else 0.0; look = 0.4
        if active(t, "snowy", 0, 1.2): a = ((0.6, -1.4), (0.6, -1.4)); hop = abs(math.sin(t * 10 + i)) * 10
        if active(t, "bye1", 0, 3) or active(t, "bye2", 0, 3): a = (a[0], (2.1, 0.5 + 0.5 * math.sin(t * 11 + i))); hop = abs(math.sin(t * 5 + i)) * 10; look = 0
        if n == "golu" and active(t, "eatit", 0, 0.6): a = ((1.2, 1.2), (1.2, 1.2))
        if n == "tinku" and active(t, "golu", 0, 0.8): a = HIPS
        kid(n, c, xs[n], GY, t, a, look, hop)
        if n == "golu" and not (active(t, "snowy", 0, 1.2) or active(t, "bye1", 0, 3) or active(t, "bye2", 0, 3)):
            golu_box(c, xs[n], GY, t, hop)
    moti_r(c, lerp(640, 840, walk), GY, t, hop=abs(math.sin(t * 8)) * (14 if walking else 6), wag=2.5, white=mwhite)
    barfi(c, bx + 260, GY, 0.85, t, 0.4, blink(t, 0.5), glow=0, shake=1.0 if sh else 0, flour=1 - mwhite)
    if T_SHAKE <= t <= T_SHAKE + 1.6:   # flour cloud
        q = prog(t, T_SHAKE, T_SHAKE + 1.6); r = random.Random(7)
        for i in range(40):
            a = r.uniform(-0.3, PI + 0.3); d = 30 + 160 * q * r.uniform(0.5, 1.2)
            ell(c, bx + 260 + d * math.cos(a) * 1.4, GY - 60 - d * math.sin(a) * 0.8, 10 + 14 * q, 10 + 14 * q); setc(c, (1, 1, 1, 0.75 * (1 - q))); c.fill()

def outro_card(c, t):
    lt = t - T_OUTRO
    gr = cairo.RadialGradient(640, 380, 40, 640, 380, 900); gr.add_color_stop_rgba(0, *hexc("#e9f1ff")); gr.add_color_stop_rgba(1, *hexc("#9fb6ff")); c.set_source(gr); c.paint()
    r = random.Random(5)
    for k in range(70):   # gentle snow-like flour flakes
        x0 = r.uniform(0, W); sp = r.uniform(40, 110); ph = r.uniform(0, 800)
        y = (ph + lt * sp) % 800 - 40; x = x0 + 20 * math.sin(lt * 2 + k)
        ell(c, x, y, 5, 5); setc(c, (1, 1, 1, 0.9)); c.fill()
    p = back(prog(lt, 0.1, 0.6))
    if p > 0.02: c.save(); c.translate(640, 140); c.scale(p, p); draw_text(c, "Bye-bye!", 0, 0, 130, "#2f5bd8", "#ffffff", 12, lang="en"); c.restore()
    p2 = back(prog(lt, 0.5, 1.0))
    if p2 > 0.02:
        c.save(); c.translate(640, 262); c.scale(p2, p2); draw_text(c, "See you next time!", 0, 0, 46, "#1f2a5a", "#ffffff", 5, lang="en")
        draw_text(c, NEXT, 0, 58, 36, "#e8327f", "#ffffff", 4, lang="en"); c.restore()
    tinku(c, 430, 680, t, 0.8, ((0.15, 0.3), (2.1, 0.5 + 0.5 * math.sin(t * 10))), 0, 0, blink(t, 0), abs(math.sin(t * 5)) * 12)
    golu(c, 620, 680, t, 0.8, ((0.15, 0.3), (2.1, 0.5 + 0.5 * math.sin(t * 10 + 1))), 0, 0, blink(t, 1), abs(math.sin(t * 5 + 1)) * 12)
    moti(c, 830, 680, t, 0.8, 0, -0.3, False, abs(math.sin(t * 6)) * 12, 2.5)
    barfi(c, 990, 680, 0.9, t, 0, blink(t, 2), 0, flour=0)

def captions(c, t):
    cur = None
    for i, l in enumerate(LINES):
        nxt = LINES[i + 1]["start"] if i + 1 < len(LINES) else 1e9
        if l["start"] - 0.12 <= t <= min(l["end"] + 0.6, nxt - 0.12): cur = l
    if not cur or t >= T_OUTRO: return
    a = clamp((t - cur["start"] + 0.12) / 0.15)
    name, col = NAMES[cur["speaker"]]
    c.select_font_face("Fredoka", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); c.set_font_size(34)
    txt = cur["en"]; tw = c.text_extents(txt).x_advance
    if tw > 1180:
        c.set_font_size(34 * 1180 / tw); tw = c.text_extents(txt).x_advance
    fsz = c.get_font_matrix().xx
    bw = tw + 56; bh = 58; bx, by = 640 - bw / 2, 706 - bh
    c.push_group()
    rrect(c, bx + 3, by + 5, bw, bh, 22); setc(c, (0.1, 0.05, 0.2, 0.25)); c.fill()
    rrect(c, bx, by, bw, bh, 22); fs(c, (1, 1, 1, 0.95), hexc(col), 5)
    nw = text_surface(name, 24, "#ffffff", None, 0, "hi").get_width()
    rrect(c, bx + 18, by - 24, nw + 24, 40, 20); fs(c, col, (1, 1, 1, 1), 3)
    draw_text(c, name, bx + 30, by - 4, 24, "#ffffff", None, 0, lang="hi", anchor="l")
    c.select_font_face("Fredoka", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); c.set_font_size(fsz)
    c.move_to(640 - tw / 2, by + 41); setc(c, "#2b2d42"); c.show_text(txt)
    c.pop_group_to_source(); c.paint_with_alpha(a)

def scene_ghost(c, t): scene_lane(c, t, ghost_k=ease(prog(t, T_GHOST, T_GHOST + 2.2)))

SCENES = [(0.0, scene_lane), (T_GHOST, scene_ghost), (T_HIDE, scene_hide), (T_REVEAL, scene_reveal), (T_HOME, scene_home), (T_OUTRO, lambda c, t: outro_card(c, t))]
WIPE = {T_HOME, T_OUTRO}

def frame(t, surf=None, with_captions=True):
    t_glob[0] = t
    surf = surf or cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(surf)
    idx = max(i for i, (t0, _) in enumerate(SCENES) if t >= t0)
    t0, fn = SCENES[idx]
    z = 1.0 + 0.04 * ease(prog(t, t0, t0 + 12)) if fn is not SCENES[-1][1] else 1.0
    if active(t, "ghost", 0.2, 0.6): z += 0.06 * ease(prog(t, S("ghost") - 0.2, S("ghost") + 0.3))
    sh = 9 * math.exp(-max(0, t - S("ghost") + 0.2) * 4) if S("ghost") - 0.2 <= t <= S("ghost") + 1.2 else 0
    c.save(); c.translate(640 + sh * math.sin(t * 60), 420 + sh * math.cos(t * 47)); c.scale(z, z); c.translate(-640, -420)
    p = ease(prog(t, t0, t0 + 0.8)) if t0 in WIPE and idx > 0 else 1.0
    if p < 1:
        SCENES[idx - 1][1](c, t); c.save(); c.arc(640, 360, 780 * p, 0, 2 * PI); c.clip(); fn(c, t); c.restore()
        c.arc(640, 360, 780 * p, 0, 2 * PI); setc(c, "#ffd23f"); c.set_line_width(12); c.stroke()
    else:
        fn(c, t)
    if T_HIDE <= t < T_HIDE + 0.25 or T_REVEAL <= t < T_REVEAL + 0.25:
        c.rectangle(0, 0, W, H); setc(c, (1, 1, 1, 0.5 * (1 - (t - (T_HIDE if t < T_REVEAL else T_REVEAL)) / 0.25))); c.fill()
    c.restore()
    if with_captions: captions(c, t)
    f = clamp((DURATION - t) / 1.5)   # no fade-in: the first frame is never black
    if f < 1: c.rectangle(0, 0, W, H); setc(c, (0, 0, 0, 1 - f)); c.fill()
    return surf

if __name__ == "__main__":
    os.makedirs("stills", exist_ok=True)
    for ts in sys.argv[1:]: frame(float(ts)).write_to_png(f"stills/f_{float(ts):06.2f}.png")
