"""Story: The Jingle on Nani's Roof. Starts straight in the story (no title card, no brand text)."""
import sys, os, math, random, numpy as np, soundfile as sf, cairo
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "mahabharat", "lib"))
from chars import *
from chars import _kid_face
from scenery import sky, lin
from cues import *
from script import NAMES, NEXT

W, H, FPS = 1280, 720, 30
GY = 612

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
TORCH = ((0.14, 0.25), (1.45, 0.15))

# ---------------------------------------------------------------- new characters
def nani(c, x, y, t=0.0, s=1.0, arms=(0.25, 0.25), m=0.0, look=0.0, closed=False, hopy=0.0, lantern=False):
    """Nani: kind grandmother — grey bun, round glasses, maroon saree with gold border, cream shawl."""
    skin = "#dba57c"; saree = "#a8324a"; gold = "#f2c14e"
    c.save(); c.translate(x, y)
    ell(c, 0, 2, 62 * s, 11 * s); setc(c, (0, 0, 0, 0.16)); c.fill()
    c.translate(0, -hopy); c.scale(s, s)
    for lx in (-18, 18): ell(c, lx + (4 if lx > 0 else -4), -8, 22, 10); fs(c, "#7a4a2a")   # chappals
    c.move_to(-44, -214); c.curve_to(-52, -150, -64, -80, -70, -12); c.curve_to(-24, -2, 24, -2, 70, -12)
    c.curve_to(64, -80, 52, -150, 44, -214); c.close_path()
    g = cairo.LinearGradient(0, -214, 0, -10); g.add_color_stop_rgba(0, *light(saree, 0.1)); g.add_color_stop_rgba(1, *dark(saree, 0.85))
    c.set_source(g); c.fill_preserve(); setc(c, dark(saree, 0.6)); c.set_line_width(3); c.stroke()
    c.move_to(-68, -22); c.curve_to(-24, -12, 24, -12, 68, -22); setc(c, gold); c.set_line_width(8); c.stroke()
    for k in range(6): ell(c, -46 + k * 18, -60 - (k % 2) * 40, 4, 4); setc(c, (1, 0.85, 0.4, 0.8)); c.fill()
    c.move_to(-44, -214); c.curve_to(-10, -170, 20, -120, 50, -70); c.line_to(62, -84); c.curve_to(36, -140, 8, -190, -16, -220); c.close_path()
    fs(c, "#f3e6cf", "#b8a07a", 2.5)                                                   # shawl/pallu
    hands = []
    for sgn, a in ((-1, arms[0]), (1, arms[1])):
        sx = sgn * 44; ell(c, sx + sgn * 4, -200, 16, 15); fs(c, "#f3e6cf", "#b8a07a", 2.5)
        hands.append(limb(c, sx + sgn * 4, -196, mir(a, sgn), 72, skin, 15))
    c.save(); c.translate(0, -282); c.rotate(math.sin(t * 1.6) * 0.03 + m * 0.03)
    ell(c, 0, -76, 34, 26); fs(c, "#d9d9e0", "#9a9aa8", 2.5)                         # bun
    ell(c, -76, 6, 12, 16); fs(c, skin); ell(c, 76, 6, 12, 16); fs(c, skin)
    for sgn in (-1, 1): ell(c, sgn * 76, 22, 4, 4); fs(c, gold)                       # earrings
    ell(c, 0, 0, 78, 76); fs(c, skin, dark(skin, 0.72))
    c.new_path(); c.arc(0, -4, 81, PI * 1.0, PI * 2.0); c.curve_to(70, -30, 40, -40, 0, -36); c.curve_to(-40, -40, -70, -30, -81, -4); c.close_path()
    fs(c, "#d9d9e0", "#9a9aa8", 2.5)                                                   # grey hair, centre parting
    c.move_to(0, -80); c.line_to(0, -38); setc(c, "#9a9aa8"); c.set_line_width(2.5); c.stroke()
    _kid_face(c, skin, m, look, closed, "#3a2414")
    for ex in (-30, 30): c.arc(ex, 6, 27, 0, 2 * PI); setc(c, "#6a4a3a"); c.set_line_width(4); c.stroke()
    c.move_to(-3, 6); c.line_to(3, 6); c.stroke()
    ell(c, 0, -22, 5, 5); setc(c, "#d81b30"); c.fill()                                # bindi
    c.restore()
    dev = [c.user_to_device(*h) for h in hands]
    c.restore()
    if lantern:
        hx, hy = dev[1]; lantern_prop(c, hx, hy + 30, t)
    return dev

def lantern_prop(c, x, y, t, s=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    rg = cairo.RadialGradient(0, 0, 6, 0, 0, 200); rg.add_color_stop_rgba(0, 1, 0.85, 0.45, 0.55); rg.add_color_stop_rgba(1, 1, 0.85, 0.45, 0)
    c.set_source(rg); c.arc(0, 0, 200, 0, 2 * PI); c.fill()
    c.move_to(0, -40); c.curve_to(-18, -56, 18, -56, 0, -40); setc(c, "#3a3a3a"); c.set_line_width(3); c.stroke()
    rrect(c, -16, -40, 32, 8, 3); fs(c, "#5a5a5a")
    ell(c, 0, -10, 16, 24); fs(c, (1, 0.92, 0.6, 0.85), "#5a5a5a", 3)
    ell(c, 0, -6, 4, 9 + math.sin(t * 13)); setc(c, "#ff8a1a"); c.fill()
    rrect(c, -18, 12, 36, 10, 3); fs(c, "#5a5a5a")
    c.restore()

def chameli(c, x, y, t, s=1.0, face=1, dance=0.0, payal=True, bell=False, m=0.0, closed=False, silhouette=None):
    """Chameli: Nani's white goat with brown patches, little curved horns, a beard — optionally wearing Pinky's anklets."""
    c.save(); c.translate(x, y - dance * abs(math.sin(t * 9)) * 22); c.scale(s * face, s)
    sil = silhouette is not None
    col = (lambda a: silhouette) if sil else (lambda a: a)
    if not sil: ell(c, 0, 4 + dance * abs(math.sin(t * 9)) * 22, 80, 10); setc(c, (0, 0, 0, 0.15)); c.fill()
    for k, (lx, ph) in enumerate(((-48, 0), (-26, PI), (32, PI), (54, 0))):   # legs
        a = 0.35 * dance * math.sin(t * 9 + ph)
        c.save(); c.translate(lx, -52); c.rotate(a)
        rrect(c, -7, 0, 14, 52, 6); fs(c, col("#efe8dc"), None if sil else "#a89a86", 2)
        rrect(c, -8, 44, 16, 10, 3); fs(c, col("#4a3a2a"))
        if payal and lx > 0 and not sil:   # anklets on the front legs
            c.move_to(-12, 32); c.curve_to(-8, 40, 8, 40, 12, 32); setc(c, "#e8ecf4"); c.set_line_width(7); c.stroke()
            for b in (-9, 0, 9): ell(c, b, 41, 5, 5); fs(c, "#ffffff", "#8a90a0", 1.5)
        c.restore()
    ell(c, 0, -78, 76, 40); fs(c, col("#f6f1e8"), None if sil else "#a89a86", 3)        # body
    if not sil: ell(c, -24, -84, 26, 18); setc(c, (0.6, 0.42, 0.25, 0.5)); c.fill()
    c.save(); c.translate(-72, -100); c.rotate(-0.6 + 0.3 * math.sin(t * 6)); ell(c, 0, -10, 8, 14); fs(c, col("#f6f1e8")); c.restore()   # tail
    c.save(); c.translate(70, -112); c.rotate(-0.15 + 0.1 * dance * math.sin(t * 9))  # head
    c.move_to(-8, 16); c.curve_to(-14, 40, 10, 50, 16, 26); fs(c, col("#f6f1e8"))     # neck
    for sgn, dx in ((-1, -10), (1, 8)):   # horns
        c.move_to(dx, -26); c.curve_to(dx - 6, -52, dx - 24, -58, dx - 30, -44); setc(c, col("#8a7a60")); c.set_line_width(8); c.stroke()
    c.save(); c.translate(-18, -8); c.rotate(0.6 + 0.1 * math.sin(t * 3)); ell(c, 0, 14, 9, 20); fs(c, col("#e8d8c0"), None if sil else "#a89a86", 2); c.restore()   # ear
    ell(c, 6, 0, 30, 26); fs(c, col("#f6f1e8"), None if sil else "#a89a86", 2.5)
    ell(c, 30, 12, 18, 14); fs(c, col("#f0e2d4"), None if sil else "#a89a86", 2)       # snout
    c.move_to(22, 26); c.curve_to(22, 44, 30, 50, 34, 40); setc(c, col("#d8ccb8")); c.set_line_width(6); c.stroke()   # beard
    if not sil:
        if closed: c.move_to(2, -4); c.curve_to(6, 0, 12, 0, 16, -4); setc(c, "#3a2a1a"); c.set_line_width(2.5); c.stroke()
        else: ell(c, 9, -4, 7, 8); fs(c, "#ffffff", "#3a2a1a", 1.5); rrect(c, 5, -6, 9, 4, 2); setc(c, "#2a1a10"); c.fill()
        ell(c, 40, 8, 3, 2); setc(c, "#5a3a2a"); c.fill()
        if m > 0.1: ell(c, 36, 20, 5, 3 + 4 * m); fs(c, "#7c1d2c")
        else: c.move_to(30, 20); c.curve_to(34, 24, 40, 24, 44, 20); setc(c, "#5a3a2a"); c.set_line_width(2); c.stroke()
    c.restore()
    if bell and not sil:
        c.move_to(52, -96); c.curve_to(62, -80, 80, -78, 90, -92); setc(c, "#e8322f"); c.set_line_width(6); c.stroke()
        c.save(); c.translate(70, -76 + 2 * math.sin(t * 8)); c.move_to(-10, 8); c.curve_to(-10, -10, 10, -10, 10, 8); c.close_path(); fs(c, "#ffd23f", "#c99a00", 2); ell(c, 0, 9, 3, 3); fs(c, "#c99a00"); c.restore()
    c.restore()

# ---------------------------------------------------------------- backgrounds
def stars(c, t, k=1.0, n=70, seed=4, ymax=330):
    r = random.Random(seed)
    for i in range(n):
        x, y = r.uniform(0, W), r.uniform(10, ymax); tw = 0.5 + 0.5 * math.sin(t * 3 + i)
        c.arc(x, y, r.uniform(1.2, 2.8), 0, 2 * PI); setc(c, (1, 1, 0.85, k * (0.4 + 0.6 * tw))); c.fill()

def moon(c, x, y, r=40, k=1.0):
    rg = cairo.RadialGradient(x, y, r * 0.5, x, y, r * 6); rg.add_color_stop_rgba(0, 1, 1, 0.9, 0.35 * k); rg.add_color_stop_rgba(1, 1, 1, 0.9, 0)
    c.set_source(rg); c.arc(x, y, r * 6, 0, 2 * PI); c.fill()
    ell(c, x, y, r, r); setc(c, (1, 0.98, 0.86, k)); c.fill()
    for dx, dy, rr in ((-12, -8, 8), (10, 10, 6), (6, -14, 4)): ell(c, x + dx, y + dy, rr, rr); setc(c, (0.9, 0.88, 0.75, 0.6 * k)); c.fill()

def hut(c, x, y, w, h, wall="#d9a066", roof="#a8442a", door=True, lit=0.0):
    rrect(c, x, y, w, h, 6); fs(c, wall, dark(wall, 0.7), 3)
    for k in range(int(w / 26)):   # roof tiles
        rx = x - 14 + k * 26; poly(c, [(rx, y + 6), (rx + 13, y - 22), (rx + 30, y + 6)]); fs(c, roof, dark(roof, 0.7), 2)
    rrect(c, x - 16, y - 4, w + 32, 14, 4); fs(c, dark(roof, 0.85))
    if door:
        dx = x + w * 0.4; rrect(c, dx, y + h - 120, 60, 120, 6); fs(c, "#6a3a1a", "#3a1a0a", 3)
    wx = x + w * 0.12; rrect(c, wx, y + 40, 50, 50, 6); fs(c, "#ffd97a" if lit > 0 else "#2a3050", "#4a2a14", 3)
    for i in range(3): c.move_to(wx + 12 + i * 13, y + 40); c.line_to(wx + 12 + i * 13, y + 90)
    setc(c, "#4a2a14"); c.set_line_width(3); c.stroke()

def neem(c, x, y, s=1.0, k=0.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, -16, -170, 32, 170, 10); fs(c, "#6a4a32", "#3a2a1a", 3)
    for dx, dy, r in ((-70, -200, 70), (0, -250, 90), (70, -200, 72), (-30, -170, 60), (40, -160, 60)):
        ell(c, dx, dy, r, r * 0.8); setc(c, lerp_col("#4f9e45", "#1f3a2c", k)); c.fill()
    for dx, dy, r in ((-40, -230, 34), (30, -270, 40), (80, -210, 30)):
        ell(c, dx, dy, r, r * 0.7); setc(c, lerp_col("#6cbf55", "#2a4a36", k)); c.fill()
    c.restore()

def lerp_col(a, b, k):
    ca, cb = hexc(a), hexc(b); return tuple(lerp(ca[i], cb[i], k) for i in range(3)) + (1.0,)

def charpai(c, x, y, s=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    for lx in (-110, 100): rrect(c, lx, -40, 12, 44, 3); fs(c, "#7a4a22", "#3a2210", 2)
    rrect(c, -120, -56, 240, 20, 6); fs(c, "#a86a32", "#5a3414", 3)
    for k in range(12): c.move_to(-112 + k * 20, -54); c.line_to(-102 + k * 20, -38)
    setc(c, "#e8d8a8"); c.set_line_width(2); c.stroke()
    c.restore()

def courtyard(c, t, night=0.0, morning=False):
    if morning: sky(c, [(0, "#7cc8ff"), (0.7, "#ffe0b0"), (1, "#fff0d0")], 470, sun=(1100, 150, 46, "#fff3b0"), rays=0.6, t=t)
    else:
        top = lerp_col("#ff9a5a", "#141a44", night); mid = lerp_col("#ffcf8a", "#2a3268", night)
        g = cairo.LinearGradient(0, 0, 0, 470); g.add_color_stop_rgba(0, *top); g.add_color_stop_rgba(1, *mid); c.set_source(g); c.rectangle(0, 0, W, 470); c.fill()
        stars(c, t, night, ymax=280)
        if night > 0.2: moon(c, 1080, 110, 38, night)
    for i in range(6):   # distant huts
        hx = i * 230 - 40; c.move_to(hx, 470); c.line_to(hx, 420); c.line_to(hx + 60, 390); c.line_to(hx + 120, 420); c.line_to(hx + 120, 470); c.close_path()
        setc(c, lerp_col("#b87a55", "#202848", max(night, 0.1 if morning else 0))); c.fill()
    lin(c, 0, 470, 0, 720, [(0, lerp_hex("#d8b27a", "#4a4a6a", night)), (1, lerp_hex("#b88a52", "#2a2a44", night))]); c.rectangle(0, 470, W, 250); c.fill()
    neem(c, 120, 520, 1.0, night)
    hut(c, 700, 300, 460, 220, lit=1.0 if night > 0.3 else 0.0)
    # outside stairs up to the roof (left side of the hut)
    for k in range(7): rrect(c, 640 - k * 18 + 60, 500 - k * 28, 70, 28, 2); fs(c, "#c98a52", "#6a4a2a", 2)
    rrect(c, 1180, 470, 70, 60, 6); fs(c, "#e0c07a", "#8a6a3a", 2)                      # hay bales
    rrect(c, 1170, 440, 60, 40, 6); fs(c, "#e8cc88", "#8a6a3a", 2)
    charpai(c, 470, 600, 1.0)
    if not morning: lantern_prop(c, 590, 520, t, 0.9)
    if night > 0: c.rectangle(0, 0, W, H); setc(c, (0.04, 0.05, 0.18, 0.35 * night)); c.fill()

def lerp_hex(a, b, k):
    ca, cb = hexc(a), hexc(b); return "#%02x%02x%02x" % tuple(int(255 * lerp(ca[i], cb[i], k)) for i in range(3))

def room(c, t, payal_on=False):
    g0 = cairo.LinearGradient(0, 0, 0, 720); g0.add_color_stop_rgba(0, *hexc("#33407e")); g0.add_color_stop_rgba(1, *hexc("#252c60")); c.set_source(g0); c.rectangle(0, 0, W, H); c.fill()
    c.rectangle(0, 560, W, 160); setc(c, "#3a3258"); c.fill()
    # window with moonlight
    wx, wy = 860, 170
    rrect(c, wx - 12, wy - 12, 244, 224, 8); fs(c, "#5a3a24", "#2a1a10", 3)
    c.rectangle(wx, wy, 220, 200); setc(c, "#20306a"); c.fill(); stars(c, t, 1.0, n=12, seed=9, ymax=0)
    for k in range(8):
        sx = wx + 20 + (k * 53) % 200; sy = wy + 20 + (k * 37) % 160; c.arc(sx, sy, 2, 0, 2 * PI); setc(c, (1, 1, 0.85, 0.8)); c.fill()
    moon(c, wx + 160, wy + 60, 24, 0.9)
    for i in range(4): c.move_to(wx + 44 * (i + 1), wy); c.line_to(wx + 44 * (i + 1), wy + 200)
    setc(c, "#5a3a24"); c.set_line_width(6); c.stroke()
    rrect(c, wx - 30, wy + 196, 280, 22, 4); fs(c, "#7a4a2a", "#3a2210", 3)              # window sill
    if payal_on:
        for k in range(2):
            px = wx + 70 + k * 60; c.move_to(px - 20, wy + 194); c.curve_to(px - 14, wy + 178, px + 14, wy + 178, px + 20, wy + 194)
            setc(c, "#e0e4ee"); c.set_line_width(5); c.stroke()
    c.move_to(wx, wy + 200); c.line_to(wx + 220, wy + 200); c.line_to(wx + 120, 720); c.line_to(wx - 200, 720); c.close_path()
    g = cairo.LinearGradient(0, wy + 200, 0, 720); g.add_color_stop_rgba(0, 0.75, 0.8, 1, 0.22); g.add_color_stop_rgba(1, 0.75, 0.8, 1, 0.04); c.set_source(g); c.fill()
    # bed with quilt
    rrect(c, 60, 520, 520, 50, 8); fs(c, "#6a4a32", "#3a2a1a", 3)
    for lx in (70, 550): rrect(c, lx, 560, 20, 60, 4); fs(c, "#5a3a22")
    rrect(c, 80, 480, 480, 54, 22); fs(c, "#e8577a", "#8a2a4a", 3)
    for k in range(6): ell(c, 120 + k * 80, 506, 14, 14); setc(c, (1, 0.9, 0.4, 0.8)); c.fill()

def stairs_bg(c, t):
    g0 = cairo.LinearGradient(0, 0, 0, 720); g0.add_color_stop_rgba(0, *hexc("#2a3266")); g0.add_color_stop_rgba(1, *hexc("#1a2048")); c.set_source(g0); c.rectangle(0, 0, W, H); c.fill()
    rg = cairo.RadialGradient(640, 280, 40, 640, 280, 420); rg.add_color_stop_rgba(0, 0.78, 0.82, 1, 0.55); rg.add_color_stop_rgba(1, 0.78, 0.82, 1, 0)
    c.set_source(rg); c.paint()   # moonlit patch on the wall where the shadow falls
    for k in range(9):   # steps rising to the right
        x = 80 + k * 130; y = 660 - k * 52
        c.rectangle(x, y, 140, 720 - y); setc(c, lerp_col("#4a3f5a", "#2a2440", k / 9)); c.fill()
        c.move_to(x, y); c.line_to(x + 140, y); setc(c, "#6a5a7a"); c.set_line_width(3); c.stroke()
    # moonlight from a small window at the top
    rrect(c, 1080, 60, 120, 90, 6); fs(c, "#2a3a7a", "#4a3a2a", 4)
    moon(c, 1150, 95, 14, 0.9)
    c.move_to(1080, 150); c.line_to(1200, 150); c.line_to(700, 700); c.line_to(300, 700); c.close_path()
    g = cairo.LinearGradient(1140, 150, 500, 700); g.add_color_stop_rgba(0, 0.75, 0.8, 1, 0.2); g.add_color_stop_rgba(1, 0.75, 0.8, 1, 0.02); c.set_source(g); c.fill()

def roof_bg(c, t, lit=0.0, morning=False):
    g = cairo.LinearGradient(0, 0, 0, 470); g.add_color_stop_rgba(0, *hexc("#121844")); g.add_color_stop_rgba(1, *hexc("#2a3470")); c.set_source(g); c.rectangle(0, 0, W, 470); c.fill()
    stars(c, t, 1.0, ymax=330); moon(c, 1100, 100, 42)
    for i in range(8):
        hx = i * 180 - 60; c.move_to(hx, 470); c.line_to(hx, 400 - (i % 3) * 20); c.line_to(hx + 70, 370 - (i % 3) * 20); c.line_to(hx + 140, 400 - (i % 3) * 20); c.line_to(hx + 140, 470); c.close_path()
        setc(c, "#1a2040"); c.fill()
        if i % 2: rrect(c, hx + 50, 420 - (i % 3) * 20, 18, 18, 2); setc(c, (1, 0.85, 0.45, 0.8)); c.fill()
    c.rectangle(0, 470, W, 250); setc(c, "#8a7a8a"); c.fill()                              # roof floor
    for k in range(8): c.move_to(0, 470 + k * 32); c.line_to(W, 470 + k * 32)
    setc(c, (0.3, 0.25, 0.35, 0.3)); c.set_line_width(2); c.stroke()
    rrect(c, 0, 440, W, 34, 4); fs(c, "#b09aa0", "#5a4a5a", 3)                             # parapet
    rrect(c, 60, 300, 130, 150, 10); fs(c, "#3a3a4a", "#1a1a2a", 3); rrect(c, 52, 290, 146, 20, 6); fs(c, "#4a4a5a")   # water tank
    ell(c, 1110, 600, 120, 40); setc(c, "#d8b860"); c.fill(); ell(c, 1110, 580, 90, 34); setc(c, "#e8cc78"); c.fill()  # hay pile
    for k in range(20):
        a = k * 0.31; c.move_to(1040 + k * 7, 560 + 10 * math.sin(a)); c.line_to(1050 + k * 7, 540 + 12 * math.cos(a)); setc(c, "#c9a040"); c.set_line_width(2); c.stroke()
    c.move_to(240, 330); c.line_to(640, 350); setc(c, "#c8c8d8"); c.set_line_width(2); c.stroke()   # clothesline
    for k, col in enumerate(("#ff8fb0", "#8fc0ff", "#ffe066")):
        x0 = 300 + k * 110; c.save(); c.translate(x0, 336 + k * 4); c.rotate(0.05 * math.sin(t * 2 + k)); rrect(c, -20, 0, 40, 48, 5); fs(c, col, dark(col, 0.7), 2); c.restore()
    c.rectangle(0, 0, W, H); setc(c, (0.04, 0.05, 0.2, 0.42 * (1 - lit))); c.fill()

def torch_beam(c, x0, y0, x1, y1, a, wide=110):
    ang = math.atan2(y1 - y0, x1 - x0); L = math.hypot(x1 - x0, y1 - y0) + 80
    c.save(); c.translate(x0, y0); c.rotate(ang)
    g = cairo.LinearGradient(0, 0, L, 0); g.add_color_stop_rgba(0, 1, 0.97, 0.7, 0.55 * a); g.add_color_stop_rgba(1, 1, 0.97, 0.7, 0.1 * a)
    c.move_to(0, -8); c.line_to(L, -wide); c.line_to(L, wide); c.line_to(0, 8); c.close_path(); c.set_source(g); c.fill()
    c.restore()
    rg = cairo.RadialGradient(x1, y1, 10, x1, y1, 160); rg.add_color_stop_rgba(0, 1, 0.97, 0.75, 0.4 * a); rg.add_color_stop_rgba(1, 1, 0.97, 0.75, 0)
    c.set_source(rg); c.arc(x1, y1, 160, 0, 2 * PI); c.fill()

def torch_in_hand(c, hx, hy, ang=0.0):
    c.save(); c.translate(hx, hy); c.rotate(ang); rrect(c, -6, -10, 44, 20, 6); fs(c, "#e8322f", "#8a1a14", 2); rrect(c, 34, -13, 12, 26, 3); fs(c, "#cfd4e0", "#6a7080", 2); c.restore()

def notes(c, x, y, t, t0, n=3, col="#ffffff"):
    for k in range(n):
        q = ((t - t0) * 0.7 + k / n) % 1
        draw_text(c, "छम", x + 40 * math.sin(q * 6 + k * 2), y - 90 * q, 28, col, "#3a2a5a", 3, lang="hi", alpha=1 - q)

# ---------------------------------------------------------------- scenes
def kid(name, c, x, y, t, arms, look=0.0, hop=0.0, s=0.88):
    fn = {"tinku": tinku, "pinky": pinky}[name]
    return fn(c, x, y, t, s, arms, mo(name, t), look, blink(t, {"tinku": 0.3, "pinky": 1.4}[name]), hop)

def scene_evening(c, t):
    courtyard(c, t, night=0.55 * ease(prog(t, 0, T_NIGHT)))
    xs = {"tinku": 330, "pinky": 520}
    for i, n in enumerate(("tinku", "pinky")):
        a = talk(n, t, i); hop = 0.0; look = 0.3
        if n == "pinky" and active(t, "payal", 0, 0.6): hop = abs(math.sin(t * 9)) * 16; a = ((1.9, 0.6), (1.9, 0.6))
        if n == "tinku" and active(t, "stars", 0, 1.0): a = (a[0], (2.5, 0.2)); look = -0.4
        if active(t, "goodnight", 0, 1.0): a = (a[0], (2.1, 0.5 + 0.5 * math.sin(t * 10 + i)))
        kid(n, c, xs[n], GY, t, a, look, hop)
    if active(t, "payal", 0, 0.6): notes(c, 520, GY - 30, t, S("payal"))
    nani(c, 860, GY + 20, t, 0.95, talk("nani", t, 3), mo("nani", t), -0.4, blink(t, 2.0))

def scene_night(c, t):
    room(c, t, payal_on=False)
    up = ease(prog(t, S("wake") - 0.6, S("wake") + 0.4))
    xs = {"tinku": 250, "pinky": 420}
    for i, n in enumerate(("tinku", "pinky")):
        a = talk(n, t, i); look = -0.3; hop = 0.0
        if n == "pinky" and active(t, "wake", 0, 0.3): a = ((0.5, -0.3), (1.6, 0.3))
        if n == "tinku" and active(t, "gone", 0, 1.0): a = (a[0], (1.55, 0.05)); look = 0.7
        if active(t, "ghostpayal", 0, 0.8): a = SCARED; hop = abs(math.sin(t * 14)) * 5
        if n == "tinku" and t >= S("upstairs") - 0.2: a = TORCH
        y = lerp(GY + 90, GY, up) if n == "tinku" else GY
        kid(n, c, xs[n], y, t, a, look, hop)
    rrect(c, 80, 480 + 0, 480, 54, 22); fs(c, "#e8577a", "#8a2a4a", 3)                 # quilt in front of sleeping Tinku's legs
    for k in range(6): ell(c, 120 + k * 80, 506, 14, 14); setc(c, (1, 0.9, 0.4, 0.8)); c.fill()
    if T_CHHAM <= t <= S("upstairs"):   # chham-chham from above
        for k in range(3):
            q = ((t - T_CHHAM) * 0.8 + k / 3) % 1
            draw_text(c, "छम…", 640 + 220 * math.sin(k * 2.1), 120 - 40 * q, 34, "#e8ecff", "#2a2a5a", 4, lang="hi", alpha=0.85 * (1 - q))
    if active(t, "gone", 0, 1.2):
        c.arc(1000, 382, 70 + 5 * math.sin(t * 8), 0, 2 * PI); setc(c, (1, 0.9, 0.3, 0.9)); c.set_line_width(5); c.stroke()

def scene_stairs(c, t):
    stairs_bg(c, t)
    sp = ease(prog(t, T_STAIRS, T_STAIRS + 1.2))
    # giant horned shadow on the wall (Chameli's silhouette, blown up by the moonlight)
    k = ease(prog(t, S("shadow") - 0.6, S("shadow") + 0.6))
    if k > 0:
        c.save(); c.translate(640 + 18 * math.sin(t * 0.8), 470); c.scale(2.6, 2.6)
        c.push_group(); chameli(c, 0, 0, t, 1.0, face=-1, dance=0.15, silhouette=(0.05, 0.05, 0.14, 1.0))
        c.pop_group_to_source(); c.paint_with_alpha(0.85 * k); c.restore()
    if active(t, "horns", 0.1, 1.0):
        for hx in (420, 470):
            c.arc(hx, 120, 46 + 5 * math.sin(t * 8), 0, 2 * PI); setc(c, (1, 0.9, 0.3, 0.0)); c.stroke()
    # hay + hoof prints clue
    if t >= S("hay") - 0.3:
        q = ease(prog(t, S("hay") - 0.3, S("hay") + 0.3))
        for k2 in range(14):
            hx = 640 + k2 * 9; c.move_to(hx, 556); c.line_to(hx + 14, 548 - (k2 % 3) * 4); setc(c, (0.85, 0.7, 0.3, q)); c.set_line_width(3); c.stroke()
        for k2 in range(4):
            px = 760 + k2 * 70; py = 500 - k2 * 26
            for dx in (-6, 6): ell(c, px + dx, py, 5, 8); setc(c, (0.5, 0.45, 0.4, 0.8 * q)); c.fill()
        if active(t, "hay", 0, 1.0): c.arc(700, 548, 60 + 5 * math.sin(t * 8), 0, 2 * PI); setc(c, (1, 0.9, 0.3, 0.9)); c.set_line_width(5); c.stroke()
    xs = {"tinku": lerp(180, 330, sp), "pinky": lerp(60, 200, sp)}
    ys = {"tinku": lerp(660, 610, sp), "pinky": lerp(700, 660, sp)}
    for i, n in enumerate(("pinky", "tinku")):
        a = talk(n, t, i); look = 0.5; hop = 0.0
        if n == "tinku": a = TORCH
        if n == "pinky": a = ((0.5, -0.4), (1.2, 0.3))
        if active(t, "horns", 0, 0.5) or active(t, "bleat1", 0, 0.6): a = SCARED if n == "pinky" else ((0.7, -1.9), (1.45, 0.15)); hop = abs(math.sin(t * 14)) * 6
        hands = kid(n, c, xs[n], ys[n], t, a, look, hop, s=0.8)
        if n == "tinku":
            hx, hy = hands[1]; torch_in_hand(c, hx, hy, -0.35)
            torch_beam(c, hx + 40, hy - 14, 720, 300, 0.55, 80)

def scene_roof(c, t):
    lit = ease(prog(t, T_TORCH, T_TORCH + 0.3))
    roof_bg(c, t, lit=lit * 0.6)
    dancing = t >= S("dance") - 0.4 and t < T_NANI + 0.6
    cx = 820
    if lit > 0:
        torch_beam(c, 300, GY - 160, cx, GY - 90, lit, 120)
    chameli(c, cx, GY - 6, t, 1.5, face=-1, dance=1.0 if dancing else (0.3 if active(t, "bleat2", 0.1, 0.4) else 0.0), payal=True, m=mo("chameli", t), closed=blink(t, 0.7))
    if dancing: notes(c, cx, GY - 200, t, S("dance") - 0.4, 4)
    if active(t, "stuck", 0, 1.0): c.arc(cx - 40, GY - 30, 48 + 4 * math.sin(t * 8), 0, 2 * PI); setc(c, (1, 0.9, 0.3, 0.9)); c.set_line_width(5); c.stroke()
    xs = {"tinku": 250, "pinky": 430}
    for i, n in enumerate(("tinku", "pinky")):
        a = talk(n, t, i); look = 0.5; hop = 0.0
        if n == "tinku" and t < T_NANI: a = TORCH
        if lit < 0.5: a = SCARED if n == "pinky" else a
        if active(t, "stuck", 0, 0.8) or active(t, "dance", 0, 1.4) or active(t, "dressup", 0, 1.0): a = ((0.6, -1.4), (0.6, -1.4)) if n == "pinky" else a; hop = abs(math.sin(t * 10 + i)) * 10
        hands = kid(n, c, xs[n], GY, t, a, look, hop)
        if n == "tinku" and t < T_NANI: hx, hy = hands[1]; torch_in_hand(c, hx, hy, -0.15)
    if t >= T_NANI:
        nx = lerp(-120, 610, ease(prog(t, T_NANI, T_NANI + 1.6)))
        nani(c, nx, GY + 30, t, 0.95, ((0.3, 0.4), (0.9, 1.3)), mo("nani", t), 0.4, blink(t, 2.0), abs(math.sin(t * 7)) * 6 if nx < 600 else 0, lantern=True)

def scene_morning(c, t):
    courtyard(c, t, 0.0, morning=True)
    xs = {"tinku": 300, "pinky": 470}
    for i, n in enumerate(("tinku", "pinky")):
        a = talk(n, t, i); hop = 0.0; look = 0.3
        if active(t, "bye1", 0, 3) or active(t, "bye2", 0, 3): a = (a[0], (2.1, 0.5 + 0.5 * math.sin(t * 11 + i))); hop = abs(math.sin(t * 5 + i)) * 10; look = 0
        kid(n, c, xs[n], GY, t, a, look, hop)
    belled = t >= S("bell") + 1.0
    chameli(c, 760, GY + 10, t, 1.25, face=-1, dance=0.6 if belled else 0.0, payal=False, bell=belled, closed=blink(t, 0.7) if belled else True, m=mo("chameli", t))
    if belled and active(t, "bleat3", 0.5, 1.5): notes(c, 760, GY - 180, t, S("bleat3"), 3, "#ffd23f")
    nani(c, 980, GY + 20, t, 0.95, talk("nani", t, 3), mo("nani", t), -0.4, blink(t, 2.0))

def outro_card(c, t):
    lt = t - T_OUTRO
    gr = cairo.RadialGradient(640, 380, 40, 640, 380, 900); gr.add_color_stop_rgba(0, *hexc("#fff3c4")); gr.add_color_stop_rgba(1, *hexc("#c9a0ff")); c.set_source(gr); c.paint()
    r = random.Random(5); cols = ["#ff3b3b", "#ff8c1a", "#ffd21a", "#2fbf4a", "#2f8bff", "#9b3fd6"]
    for k in range(60):
        x0 = r.uniform(0, W); sp = r.uniform(60, 130); ph = r.uniform(0, 800)
        y = (ph + lt * sp) % 800 - 40; x = x0 + 20 * math.sin(lt * 2 + k)
        c.save(); c.translate(x, y); c.rotate(lt * 2 + k); rrect(c, -6, -3, 12, 6, 2); setc(c, cols[k % 6]); c.fill(); c.restore()
    p = back(prog(lt, 0.1, 0.6))
    if p > 0.02: c.save(); c.translate(640, 140); c.scale(p, p); draw_text(c, "Bye-bye!", 0, 0, 130, "#8a2a8a", "#ffffff", 12, lang="en"); c.restore()
    p2 = back(prog(lt, 0.5, 1.0))
    if p2 > 0.02:
        c.save(); c.translate(640, 262); c.scale(p2, p2); draw_text(c, "See you next time!", 0, 0, 46, "#7c2d12", "#ffffff", 5, lang="en")
        draw_text(c, NEXT, 0, 58, 36, "#2f7bff", "#ffffff", 4, lang="en"); c.restore()
    tinku(c, 380, 680, t, 0.8, ((0.15, 0.3), (2.1, 0.5 + 0.5 * math.sin(t * 10))), 0, 0, blink(t, 0), abs(math.sin(t * 5)) * 12)
    pinky(c, 560, 680, t, 0.8, ((0.15, 0.3), (2.1, 0.5 + 0.5 * math.sin(t * 10 + 1))), 0, 0, blink(t, 1), abs(math.sin(t * 5 + 1)) * 12)
    chameli(c, 840, 680, t, 1.05, face=-1, dance=0.6, payal=False, bell=True)

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

SCENES = [(0.0, scene_evening), (T_NIGHT, scene_night), (T_STAIRS, scene_stairs), (T_ROOF, scene_roof), (T_MORNING, scene_morning), (T_OUTRO, lambda c, t: outro_card(c, t))]
WIPE = {T_NIGHT, T_ROOF, T_MORNING, T_OUTRO}

def frame(t, surf=None, with_captions=True):
    surf = surf or cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(surf)
    idx = max(i for i, (t0, _) in enumerate(SCENES) if t >= t0)
    t0, fn = SCENES[idx]
    z = 1.0 + 0.04 * ease(prog(t, t0, t0 + 12)) if fn is not SCENES[-1][1] else 1.0
    if active(t, "horns", 0.2, 0.6): z += 0.06 * ease(prog(t, S("horns") - 0.2, S("horns") + 0.3))
    sh = 9 * math.exp(-max(0, t - S("horns") + 0.2) * 4) if S("horns") - 0.2 <= t <= S("horns") + 1.2 else 0
    c.save(); c.translate(640 + sh * math.sin(t * 60), 420 + sh * math.cos(t * 47)); c.scale(z, z); c.translate(-640, -420)
    p = ease(prog(t, t0, t0 + 0.8)) if t0 in WIPE and idx > 0 else 1.0
    if p < 1:
        SCENES[idx - 1][1](c, t); c.save(); c.arc(640, 360, 780 * p, 0, 2 * PI); c.clip(); fn(c, t); c.restore()
        c.arc(640, 360, 780 * p, 0, 2 * PI); setc(c, "#ffd23f"); c.set_line_width(12); c.stroke()
    else:
        fn(c, t)
    if T_STAIRS <= t < T_STAIRS + 0.25 or T_TORCH <= t < T_TORCH + 0.25:
        c.rectangle(0, 0, W, H); setc(c, (1, 1, 1, 0.5 * (1 - (t - (T_STAIRS if t < T_TORCH else T_TORCH)) / 0.25))); c.fill()
    c.restore()
    if with_captions: captions(c, t)
    f = clamp((DURATION - t) / 1.5)   # no fade-in: the first frame is never black
    if f < 1: c.rectangle(0, 0, W, H); setc(c, (0, 0, 0, 1 - f)); c.fill()
    return surf

if __name__ == "__main__":
    os.makedirs("stills", exist_ok=True)
    for ts in sys.argv[1:]: frame(float(ts)).write_to_png(f"stills/f_{float(ts):06.2f}.png")
