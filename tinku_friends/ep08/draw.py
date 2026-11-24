"""Story: The Jingle on Nani's Roof. Starts straight in the story (no title card, no brand text)."""
import sys, os, math, random, numpy as np, soundfile as sf, cairo
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "mahabharat", "lib"))
from chars import *
from chars import _kid_face
from scenery import sky, lin, clouds, birds
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

def roof_bg(c, t, lit=0.0, morning=False, hay=True):
    if morning:
        sky(c, [(0, "#6cc0ff"), (0.7, "#bfe6ff"), (1, "#fff0d0")], 470, sun=(1100, 110, 44, "#fff3b0"), rays=0.6, t=t)
    else:
        g = cairo.LinearGradient(0, 0, 0, 470); g.add_color_stop_rgba(0, *hexc("#121844")); g.add_color_stop_rgba(1, *hexc("#2a3470")); c.set_source(g); c.rectangle(0, 0, W, 470); c.fill()
        stars(c, t, 1.0, ymax=330); moon(c, 1100, 100, 42)
    for i in range(8):
        hx = i * 180 - 60; c.move_to(hx, 470); c.line_to(hx, 400 - (i % 3) * 20); c.line_to(hx + 70, 370 - (i % 3) * 20); c.line_to(hx + 140, 400 - (i % 3) * 20); c.line_to(hx + 140, 470); c.close_path()
        setc(c, "#c98a5a" if morning else "#1a2040"); c.fill()
        if i % 2 and not morning: rrect(c, hx + 50, 420 - (i % 3) * 20, 18, 18, 2); setc(c, (1, 0.85, 0.45, 0.8)); c.fill()
    c.rectangle(0, 470, W, 250); setc(c, "#8a7a8a"); c.fill()                              # roof floor
    for k in range(8): c.move_to(0, 470 + k * 32); c.line_to(W, 470 + k * 32)
    setc(c, (0.3, 0.25, 0.35, 0.3)); c.set_line_width(2); c.stroke()
    rrect(c, 0, 440, W, 34, 4); fs(c, "#b09aa0", "#5a4a5a", 3)                             # parapet
    rrect(c, 60, 300, 130, 150, 10); fs(c, "#3a3a4a", "#1a1a2a", 3); rrect(c, 52, 290, 146, 20, 6); fs(c, "#4a4a5a")   # water tank
    if hay: ell(c, 1110, 600, 120, 40); setc(c, "#d8b860"); c.fill(); ell(c, 1110, 580, 90, 34); setc(c, "#e8cc78"); c.fill()  # hay pile
    for k in range(20 if hay else 0):
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

# ---------------------------------------------------------------- props
def payal_feet(c, x, y, s=0.88):
    """silver anklets drawn at a standing kid's ankles"""
    for lx in (-16, 16):
        px = x + lx * s; py = y - 14 * s
        c.move_to(px - 12 * s, py - 4); c.curve_to(px - 8 * s, py + 6, px + 8 * s, py + 6, px + 12 * s, py - 4); setc(c, "#eef1f8"); c.set_line_width(5); c.stroke()
        for b in (-8, 0, 8): ell(c, px + b * s, py + 5, 3.5, 3.5); fs(c, "#ffffff", "#8a90a0", 1.2)

def payal_prop(c, x, y, s=1.0, rot=0.0):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    for k in range(2):
        c.save(); c.translate(-14 + k * 28, 0); c.arc(0, 0, 16, 0, 2 * PI); setc(c, "#eef1f8"); c.set_line_width(5); c.stroke()
        for a in range(6): ell(c, 16 * math.cos(a * 1.05 + 0.5), 16 * math.sin(a * 1.05 + 0.5) + 4, 3.5, 3.5); fs(c, "#ffffff", "#8a90a0", 1.2)
        c.restore()
    c.restore()

def backpack(c, x, y, s=0.88, col="#2f7bff"):
    rrect(c, x - 52 * s, y - 230 * s, 46 * s, 92 * s, 12); fs(c, col, dark(col, 0.65), 3)
    rrect(c, x - 50 * s, y - 180 * s, 40 * s, 26 * s, 8); fs(c, light(col, 0.3), dark(col, 0.65), 2)

def magnifier(c, hx, hy, ang=-0.6):
    c.save(); c.translate(hx, hy); c.rotate(ang); rrect(c, -4, -6, 40, 12, 5); fs(c, "#7a4a22", "#3a2210", 2)
    c.arc(56, 0, 20, 0, 2 * PI); fs(c, (0.75, 0.9, 1, 0.45), "#4a4a5a", 5); c.restore()

def bubble(c, x, y, t, kind):
    c.save(); c.translate(x, y + 4 * math.sin(t * 3))
    for r, dx, dy in ((8, -40, 70), (12, -24, 44)): ell(c, dx, dy, r, r); fs(c, "#ffffff", "#7a8ab8", 2)
    ell(c, 0, 0, 62, 46); fs(c, "#ffffff", "#7a8ab8", 3)
    if kind == "bell":   # cracked bell
        c.move_to(-18, 16); c.curve_to(-18, -20, 18, -20, 18, 16); c.close_path(); fs(c, "#ffd23f", "#c99a00", 2)
        c.move_to(-2, -14); c.line_to(4, -2); c.line_to(-4, 6); c.line_to(2, 16); setc(c, "#5a3a10"); c.set_line_width(3); c.stroke()
    elif kind == "idea":
        ell(c, 0, -4, 18, 20); fs(c, "#fff27a", "#c9a000", 2); rrect(c, -8, 14, 16, 10, 3); fs(c, "#9aa0b0")
        for a in range(7): c.move_to(28 * math.cos(a * 0.9 - 2.6), 28 * math.sin(a * 0.9 - 2.6) - 4); c.line_to(36 * math.cos(a * 0.9 - 2.6), 36 * math.sin(a * 0.9 - 2.6) - 4)
        setc(c, "#ffb000"); c.set_line_width(3); c.stroke()
    elif kind == "payal":
        payal_prop(c, 0, 0, 0.9)
    c.restore()

def hoofprints(c, pts, a=1.0):
    for px, py in pts:
        for dx in (-6, 6): ell(c, px + dx, py, 5, 8); setc(c, (0.45, 0.38, 0.32, 0.8 * a)); c.fill()

def bell_string(c, t, x0, x1, y, ring=0.0):
    c.move_to(x0, y); c.curve_to(x0 + 60, y + 18, x1 - 60, y + 18, x1, y); setc(c, "#e8d8b0"); c.set_line_width(3); c.stroke()
    for k in range(5):
        bx = lerp(x0, x1, (k + 1) / 6); by = y + 14 + 6 * ring * math.sin(t * 40 + k)
        c.save(); c.translate(bx, by); c.rotate(0.5 * ring * math.sin(t * 30 + k)); c.move_to(-8, 8); c.curve_to(-8, -8, 8, -8, 8, 8); c.close_path(); fs(c, "#ffd23f", "#c99a00", 2); c.restore()

def quilt_lump(c, x, y, t, peek=1.0, shake=0.0, kids=("tinku", "pinky")):
    """kids hiding under a quilt: heads peek out above it"""
    for i, n in enumerate(kids):
        hx = x - 70 + i * 140
        fn = {"tinku": tinku, "pinky": pinky}[n]
        fn(c, hx, y + 210 - 120 * peek, t, 0.7, ((0.14, 0.25), (0.14, 0.25)), mo(n, t), 0.5, blink(t, i), 0)
    sx = 6 * shake * math.sin(t * 40)
    c.move_to(x - 210 + sx, y + 20); c.curve_to(x - 200, y - 60, x - 60, y - 70, x, y - 66); c.curve_to(x + 80, y - 70, x + 200, y - 60, x + 210 + sx, y + 20); c.close_path()
    fs(c, "#e8577a", "#8a2a4a", 3)
    for k in range(5): ell(c, x - 140 + k * 70, y - 20, 12, 12); setc(c, (1, 0.9, 0.4, 0.85)); c.fill()

# ---------------------------------------------------------------- extra backgrounds
def road_bg(c, t, pan=0.0):
    sky(c, [(0, "#5cb8ff"), (0.65, "#a9dcff"), (1, "#f0f8ff")], 430, sun=(1120, 100, 44, "#fff3b0"), rays=0.8, t=t)
    clouds(c, t, 0.95, n=5, ymax=170, seed=3)
    c.save(); c.translate(-pan * 0.3, 0)
    for hx, r, col in ((150, 420, "#a6e07f"), (760, 520, "#95d870"), (1400, 460, "#a6e07f")):
        ell(c, hx, 450, r, r * 0.3); setc(c, col); c.fill()
    hut(c, 980, 330, 170, 100, door=True)
    neem(c, 880, 440, 0.5)
    c.restore()
    c.save(); c.translate(-pan * 0.6, 0)
    c.rectangle(-200, 430, W + 800, 290); setc(c, "#8fd068"); c.fill()
    for row in range(5):   # mustard field stripes
        y = 450 + row * 26
        for k in range(40):
            ell(c, -200 + k * 60 + (row % 2) * 30, y, 22, 8); setc(c, "#ffd23f" if (k + row) % 3 else "#f2b705"); c.fill()
    c.restore()
    c.move_to(0, 600); c.curve_to(400, 580, 800, 610, 1280, 590); c.line_to(1280, 720); c.line_to(0, 720); c.close_path()
    setc(c, (0.86, 0.74, 0.52, 1)); c.fill()
    birds(c, t, 4, 2)

def mela_bg(c, t):
    g = cairo.LinearGradient(0, 0, 0, 500); g.add_color_stop_rgba(0, *hexc("#2a1a5a")); g.add_color_stop_rgba(1, *hexc("#a8487a")); c.set_source(g); c.rectangle(0, 0, W, 500); c.fill()
    stars(c, t, 0.6, n=40, ymax=200)
    # ferris wheel
    cx, cy, R = 200, 280, 170
    for sgn in (-1, 1): c.move_to(cx, cy); c.line_to(cx + sgn * 110, 520); setc(c, "#5a3a7a"); c.set_line_width(10); c.stroke()
    c.arc(cx, cy, R, 0, 2 * PI); setc(c, "#ffd23f"); c.set_line_width(6); c.stroke()
    rot = t * 0.25
    for k in range(10):
        a = rot + k * 2 * PI / 10; px, py = cx + R * math.cos(a), cy + R * math.sin(a)
        c.move_to(cx, cy); c.line_to(px, py); setc(c, (1, 0.85, 0.3, 0.7)); c.set_line_width(2); c.stroke()
        rrect(c, px - 16, py, 32, 24, 6); fs(c, ["#ff4f5f", "#2f7bff", "#2fbf4a", "#ff8c1a", "#9b3fd6"][k % 5], "#3a2a4a", 2)
        ell(c, px, py, 5, 5); setc(c, (1, 1, 0.7, 0.5 + 0.5 * math.sin(t * 6 + k))); c.fill()
    # stalls
    for k, (sx, col) in enumerate(((880, "#ff4f5f"), (1080, "#2f7bff"))):
        rrect(c, sx, 380, 170, 140, 6); fs(c, "#f4e2c4", "#8a6a4a", 3)
        for st in range(6):
            poly(c, [(sx - 10 + st * 32, 380), (sx + 6 + st * 32, 340), (sx + 22 + st * 32, 380)]); fs(c, col if st % 2 else "#ffffff", dark(col, 0.7), 2)
        for j in range(4): ell(c, sx + 30 + j * 36, 440, 12, 12); setc(c, ["#ffd23f", "#ff8fb0", "#8fc0ff", "#9ff08a"][j]); c.fill()
    c.rectangle(0, 500, W, 220); setc(c, "#6a4a5a"); c.fill()
    # stage
    rrect(c, 380, 470, 520, 70, 6); fs(c, "#c0392b", "#6a1a14", 4)
    for k in range(9): rrect(c, 390 + k * 56, 476, 40, 10, 3); setc(c, "#ffd23f"); c.fill()
    # string lights (zig-zag) above
    for row in range(2):
        pts = [(x, 60 + row * 70 + 40 * math.sin(x / 160 * PI)) for x in range(0, W + 40, 40)]
        c.move_to(*pts[0])
        for p in pts[1:]: c.line_to(*p)
        setc(c, (0.2, 0.15, 0.3, 0.8)); c.set_line_width(2); c.stroke()
        for i, (x, y) in enumerate(pts):
            on = 0.5 + 0.5 * math.sin(t * 5 + i * 1.3 + row)
            col = ["#ff4f5f", "#ffd23f", "#2fbf4a", "#2f7bff", "#ff8c1a"][(i + row) % 5]
            rg = cairo.RadialGradient(x, y + 8, 2, x, y + 8, 18); r_, g_, b_, _ = hexc(col); rg.add_color_stop_rgba(0, r_, g_, b_, 0.7 * on); rg.add_color_stop_rgba(1, r_, g_, b_, 0)
            c.set_source(rg); c.arc(x, y + 8, 18, 0, 2 * PI); c.fill()
            ell(c, x, y + 8, 5, 7); setc(c, col); c.fill()

def crowd(c, t):
    r = random.Random(3)
    for k in range(16):
        x = 20 + k * 82 + r.uniform(-10, 10); y = 700 + 6 * math.sin(t * 3 + k)
        ell(c, x, y - 40, 34, 34); setc(c, (0.15, 0.1, 0.2, 0.92)); c.fill(); ell(c, x, y + 20, 50, 40); c.fill()
        if k % 3 == 0:   # clapping hands
            a = abs(math.sin(t * 8 + k)); ell(c, x - 14 + 10 * a, y - 90, 10, 10); setc(c, (0.15, 0.1, 0.2, 0.92)); c.fill(); ell(c, x + 14 - 10 * a, y - 90, 10, 10); c.fill()

# ---------------------------------------------------------------- kids
def kid(name, c, x, y, t, arms, look=0.0, hop=0.0, s=0.88, lean=0.0):
    fn = {"tinku": tinku, "pinky": pinky}[name]
    return fn(c, x, y, t, s, arms, mo(name, t), look, blink(t, {"tinku": 0.3, "pinky": 1.4}[name]), hop, lean)
def walk_hop(t, on, k=8, a=8): return abs(math.sin(t * k)) * a if on else 0.0
SCARED = ((0.7, -1.9), (0.7, -1.9))
TORCH = ((0.14, 0.25), (1.45, 0.15))
HUG = ((1.3, 0.9), (1.3, 0.9))
CHEER = ((0.6, -1.4), (0.6, -1.4))
SAD = ((0.05, 0.6), (0.05, 0.6))

# ---------------------------------------------------------------- scenes
def scene_road(c, t):
    w = prog(t, 0.0, T_COURT)
    road_bg(c, t, pan=300 * w)
    run = ease(prog(t, S("race"), S("race") + 2.5))
    tx = lerp(160, 420, ease(prog(t, 0.3, S("race") + 0.5))) + 120 * ease(prog(t, S("heavy"), T_COURT))
    px = lerp(330, 560, ease(prog(t, 0.0, S("race")))) + 600 * run
    backpack(c, tx, GY)
    a = talk("tinku", t, 0); a = ((0.5, 1.2), a[1]) if not active(t, "heavy", 0, 0.5) else ((0.5, 1.2), (2.2, 0.4))
    kid("tinku", c, tx, GY, t, a, 0.2, walk_hop(t, True, 7, 7), lean=0.08 if active(t, "heavy", 0, 1) else 0)
    pa = talk("pinky", t, 1)
    if active(t, "race", 0, 0.5): pa = (pa[0], (2.3, 0.3))
    if run > 0: pa = ((1.2, 0.8), (1.2, 0.8))
    kid("pinky", c, px, GY, t, pa, 0.3, walk_hop(t, True, 12 if run > 0 else 7, 14 if run > 0 else 7), lean=0.12 * run)
    backpack(c, px + 8, GY, 0.88, "#ff8fb0")

def scene_court(c, t):
    courtyard(c, t, night=0.25 * ease(prog(t, T_COURT, T_NIGHT)))
    arrive = ease(prog(t, T_COURT, T_COURT + 2.0))
    xs = {"tinku": lerp(-120, 380, arrive), "pinky": lerp(-40, 540, arrive)}
    hugging = active(t, "n_hug", -0.5, 0.0) and t < S("n_hug") + 3.5
    for i, n in enumerate(("tinku", "pinky")):
        a = talk(n, t, i); hop = walk_hop(t, arrive < 1, 8, 8); look = 0.3
        if hugging and arrive >= 1: a = HUG
        if n == "pinky" and (active(t, "payal", 0, 0.5) or active(t, "dance1", 0, 0.6)): a = ((1.9, 0.6), (1.9, 0.6)); hop = abs(math.sin(t * 9)) * 16
        if n == "tinku" and active(t, "likes", 0, 0.5): a = (a[0], (1.55, 0.05)); look = 0.7
        kid(n, c, xs[n] + (60 if hugging and arrive >= 1 else 0), GY, t, a, look, hop)
        if n == "pinky" and t >= S("payal") + 0.5: payal_feet(c, xs[n], GY - hop)
    na = talk("nani", t, 3)
    if hugging and arrive >= 1: na = HUG
    hands = nani(c, 760, GY + 20, t, 0.95, na, mo("nani", t), -0.4, blink(t, 2.0))
    if active(t, "gift", 0.0, 0.0) or (S("gift") <= t < S("payal") + 0.4):
        hx, hy = hands[0]; payal_prop(c, hx - 10, hy - 10, 1.0)
    # Chameli wanders, then listens
    listen = active(t, "n_listen", 0.5, 0.5) or active(t, "bleat1", 0.2, 0.4)
    gx = 1040 + (0 if listen else 70 * math.sin(t * 0.4))
    chameli(c, gx, GY + 10, t, 1.0, face=-1, dance=0.0, payal=False, m=mo("chameli", t), closed=blink(t, 0.7))
    if listen:
        for k in range(3):
            q = ((t * 0.8) + k / 3) % 1
            draw_text(c, "छम", lerp(560, gx - 60, q), GY - 60 - 60 * math.sin(q * PI), 26, "#ffffff", "#5a3a7a", 3, lang="hi", alpha=1 - q)
    if active(t, "bellbroke", 0, 0.6): bubble(c, gx + 30, GY - 230, t, "bell")
    if active(t, "dance1", 0, 0.6): notes(c, xs["pinky"], GY - 40, t, S("dance1"))

def scene_night(c, t):
    room(c, t, payal_on=t < S("n_midnight") + 1.0)
    awake = ease(prog(t, S("wake") - 0.4, S("wake") + 0.6))
    xs = {"tinku": 220, "pinky": 400}
    for i, n in enumerate(("tinku", "pinky")):
        up = awake if n == "pinky" else ease(prog(t, S("who") - 0.4, S("who") + 0.4))
        a = talk(n, t, i); look = -0.3
        if n == "pinky" and active(t, "wake", 0, 0.3): a = ((0.5, -0.3), (1.6, 0.3))
        if active(t, "gone", 0, 1.0): a = SCARED if n == "pinky" else (a[0], (1.55, 0.05)); look = 0.7
        if n == "tinku" and t >= S("torch1") - 0.2: a = TORCH
        y = lerp(GY + 150, GY, up)
        hands = kid(n, c, xs[n], y, t, a, look, 0, lean=0.0)
        if n == "tinku" and t >= S("torch1") - 0.2: hx, hy = hands[1]; torch_in_hand(c, hx, hy, -0.2)
    rrect(c, 80, 480, 480, 54, 22); fs(c, "#e8577a", "#8a2a4a", 3)                # quilt over legs / sleeping kids
    for k in range(6): ell(c, 120 + k * 80, 506, 14, 14); setc(c, (1, 0.9, 0.4, 0.8)); c.fill()
    rrect(c, 60, 528, 520, 70, 8); fs(c, "#6a4a32", "#3a2a1a", 3)                     # bed front panel hides legs
    c.rectangle(40, 598, 560, 130); setc(c, "#3a3258"); c.fill()
    for lx in (70, 550): rrect(c, lx, 590, 20, 40, 4); fs(c, "#5a3a22")
    if t < S("wake") - 0.4:
        for k in range(3):   # zzz
            q = ((t * 0.5) + k / 3) % 1
            draw_text(c, "z", 330 + 40 * q, 440 - 80 * q, 24 + 14 * q, "#e8ecff", None, 0, lang="en", alpha=1 - q)
    if T_CHHAM <= t <= S("torch1") + 1:
        for k in range(3):
            q = ((t - T_CHHAM) * 0.8 + k / 3) % 1
            draw_text(c, "छम…", 640 + 220 * math.sin(k * 2.1), 120 - 40 * q, 34, "#e8ecff", "#2a2a5a", 4, lang="hi", alpha=0.85 * (1 - q))
    if active(t, "gone", 0, 1.2):
        c.arc(1000, 382, 70 + 5 * math.sin(t * 8), 0, 2 * PI); setc(c, (1, 0.9, 0.3, 0.9)); c.set_line_width(5); c.stroke()

def scene_stairs(c, t):
    if t >= T_RUN + 1.0:   # back in bed, quilt shaking
        room(c, t, payal_on=False)
        rrect(c, 60, 520, 520, 50, 8); fs(c, "#6a4a32", "#3a2a1a", 3)
        quilt_lump(c, 320, 520, t, peek=0.35 + 0.15 * math.sin(t * 3), shake=1.0)
        return
    stairs_bg(c, t)
    sp = ease(prog(t, T_STAIRS, S("wall")))
    k = ease(prog(t, S("n_shadow") - 0.2, S("n_shadow") + 1.0))
    if k > 0:
        c.save(); c.translate(660 + 18 * math.sin(t * 0.8), 470); c.scale(2.6, 2.6)
        c.push_group(); chameli(c, 0, 0, t, 1.0, face=-1, dance=0.15, silhouette=(0.05, 0.05, 0.14, 1.0))
        c.pop_group_to_source(); c.paint_with_alpha(0.85 * k); c.restore()
    flee = ease(prog(t, T_RUN, T_RUN + 0.9))
    xs = {"tinku": lerp(lerp(150, 400, sp), -200, flee), "pinky": lerp(lerp(40, 260, sp), -260, flee)}
    ys = {"tinku": lerp(lerp(670, 600, sp), 700, flee), "pinky": lerp(lerp(700, 650, sp), 720, flee)}
    for i, n in enumerate(("pinky", "tinku")):
        a = talk(n, t, i); look = 0.5; hop = abs(math.sin(t * 5)) * 4 if sp < 1 else 0
        if n == "tinku": a = TORCH
        if n == "pinky": a = ((0.5, -0.4), (1.2, 0.3))
        if t >= S("n_shadow") + 0.5: a = SCARED if n == "pinky" else ((0.7, -1.9), (1.45, 0.15)); hop = abs(math.sin(t * 14)) * 6
        if flee > 0: a = SCARED; hop = abs(math.sin(t * 16)) * 14; look = -0.6
        hands = kid(n, c, xs[n], ys[n], t, a, look, hop, s=0.8)
        if n == "tinku" and flee < 0.2:
            hx, hy = hands[1]; torch_in_hand(c, hx, hy, -0.35); torch_beam(c, hx + 40, hy - 14, 720, 300, 0.55, 80)

def scene_morning(c, t):
    courtyard(c, t, 0.0, morning=True)
    chameli(c, 1060, GY + 10, t, 1.0, face=-1, payal=False, closed=True)   # Chameli sleeping innocently
    draw_text(c, "z", 1000, GY - 150 - 20 * math.sin(t), 26, "#7a6a9a", None, 0, lang="en")
    xs = {"tinku": 360, "pinky": 560}
    for i, n in enumerate(("tinku", "pinky")):
        a = talk(n, t, i); hop = 0.0; look = 0.3
        if n == "pinky" and t < S("detective") + 1.0: a = SAD; look = -0.2
        if n == "tinku" and active(t, "detective", 0, 1.5): a = (a[0], (1.7, 0.4))
        hands = kid(n, c, xs[n], GY, t, a, look, hop)
        if n == "tinku" and t >= S("detective"): hx, hy = hands[1]; magnifier(c, hx, hy)
        if n == "pinky" and active(t, "sad", 0, 0.8):   # tear
            q = ((t - S("sad")) * 0.7) % 1; ell(c, xs[n] + 26, GY - 250 + 60 * q, 6, 9); setc(c, (0.5, 0.75, 1, 1 - q)); c.fill()
    nani(c, 860, GY + 20, t, 0.95, ((0.2, 0.3), (0.2, 0.3)), 0, -0.4, blink(t, 2.0))

def scene_clues(c, t):
    roof_bg(c, t, morning=True)
    for k in range(14): hx = 640 + k * 9; c.move_to(hx, 640); c.line_to(hx + 14, 632 - (k % 3) * 4); setc(c, "#c9a040"); c.set_line_width(3); c.stroke()
    pts = [(820 + k * 70, 600 - (k % 2) * 16) for k in range(5)]
    hoofprints(c, pts, ease(prog(t, S("hay") - 0.5, S("hay"))))
    if active(t, "hay", 0, 1.0): c.arc(700, 636, 60 + 5 * math.sin(t * 8), 0, 2 * PI); setc(c, (1, 0.9, 0.3, 0.9)); c.set_line_width(5); c.stroke()
    if active(t, "hooves", 0, 1.0): c.arc(890, 596, 70 + 5 * math.sin(t * 8), 0, 2 * PI); setc(c, (1, 0.9, 0.3, 0.9)); c.set_line_width(5); c.stroke()
    walk = ease(prog(t, T_CLUES, T_CLUES + 2.5))
    xs = {"tinku": lerp(-100, 420, walk), "pinky": lerp(-240, 260, walk)}
    for i, n in enumerate(("tinku", "pinky")):
        a = talk(n, t, i); look = 0.5; hop = walk_hop(t, walk < 1)
        if n == "tinku": a = (a[0], (1.2, 0.6))
        if n == "pinky" and active(t, "hooves", 0, 1): a = (a[0], (1.55, 0.1))
        if n == "tinku" and active(t, "plan", 0, 1.2): a = CHEER; hop = abs(math.sin(t * 9)) * 10
        hands = kid(n, c, xs[n], GY, t, a, look, hop, lean=0.15 if (n == "tinku" and active(t, "hay", 0, 1)) else 0)
        if n == "tinku" and not active(t, "plan", 0, 1.2): hx, hy = hands[1]; magnifier(c, hx, hy, 0.4)
    if active(t, "plan", 0, 1.2): bubble(c, xs["tinku"] + 60, GY - 340, t, "idea")

def scene_trap(c, t):
    lit = ease(prog(t, T_TORCH, T_TORCH + 0.3))
    roof_bg(c, t, lit=lit * 0.6)
    rrect(c, 1180, 440, 100, 280, 4); fs(c, "#2a2440", "#1a1a2a", 2)                    # stair opening (right)
    ring = 1.0 if T_BELLS <= t <= T_BELLS + 1.4 else 0.0
    bell_string(c, t, 1170, 1280, 470, ring)
    ent = ease(prog(t, T_BELLS - 2.5, T_BELLS + 0.6))
    gx = lerp(1360, 860, ent)
    if ent > 0:
        if lit < 0.5:   # still dark: just a dark shape with jingling feet
            c.push_group(); chameli(c, gx, GY - 6, t, 1.4, face=-1, dance=0.3, silhouette=(0.08, 0.08, 0.18, 1.0)); c.pop_group_to_source(); c.paint_with_alpha(0.9)
            for lx in (-30, 10): ell(c, gx + lx * 1.4 - 40, GY - 12, 10, 4); setc(c, (0.9, 0.92, 1, 0.8)); c.fill()
        else:
            chameli(c, gx, GY - 6, t, 1.4, face=-1, dance=0.4 if active(t, "bleat2", 0.2, 0.4) else 0.0, payal=True, m=mo("chameli", t), closed=blink(t, 0.7))
    if active(t, "onlegs", 0, 1.0): c.arc(gx - 40, GY - 30, 50 + 4 * math.sin(t * 8), 0, 2 * PI); setc(c, (1, 0.9, 0.3, 0.9)); c.set_line_width(5); c.stroke()
    peek = 1.0 if t >= S("torchon") - 0.3 else (0.45 if (active(t, "scared", 0.2, 0.3) or active(t, "ready", 0.2, 0.3)) else 0.3)
    quilt_lump(c, 430, GY - 50, t, peek=peek, shake=0.6 if T_BELLS <= t <= S("torchon") else 0.0)
    if lit > 0:
        torch_beam(c, 500, GY - 170, gx - 40, GY - 90, lit, 120)
        draw_text(c, "!", 860, GY - 300, 60, "#ffd23f", "#3a2a5a", 5, lang="en", alpha=1.0 if active(t, "itschameli", 0, 1) else 0)

def scene_chase(c, t):
    roof_bg(c, t, lit=0.6)
    slip = prog(t, T_SLIP, T_SLIP + 0.8)
    if t < T_SLIP:   # zig-zag run around the roof
        q = t - T_CHASE; gx = 760 + 330 * math.sin(q * 1.3); face = 1 if math.cos(q * 1.3) > 0 else -1; gy = GY - 6
        chameli(c, gx, gy, t, 1.25, face=face, dance=1.0, payal=True)
        notes(c, gx, gy - 220, t, T_CHASE, 3)
    else:
        gx = lerp(1000, 1110, ease(slip)); gy = lerp(GY - 6, GY - 20, ease(slip))
        c.save(); c.translate(gx, gy); c.rotate(-0.9 * ease(slip)); c.translate(-gx, -gy)
        chameli(c, gx, gy, t, 1.25, face=1, payal=t < T_FLY, closed=True); c.restore()
        ell(c, 1110, 610, 130, 46); setc(c, "#e8cc78"); c.fill()                             # hay in front
        for k in range(16):
            q = prog(t, T_SLIP + 0.6, T_SLIP + 1.8); r = random.Random(k)
            if 0 < q < 1: ell(c, 1110 + r.uniform(-120, 120) * q, 560 - r.uniform(60, 180) * math.sin(q * PI), 8, 3); setc(c, (0.9, 0.78, 0.4, 1 - q)); c.fill()
    fl = prog(t, T_FLY, T_CATCH + 0.3)
    tx = 560 if t >= T_SLIP else lerp(300, 560, prog(t, T_CHASE, T_SLIP))
    if 0 < fl < 1:
        px = lerp(1080, tx + 40, fl); py = 520 - 360 * math.sin(fl * PI) + 60 * fl
        payal_prop(c, px, py, 1.0, t * 8)
    xs = {"tinku": tx, "pinky": tx - 190}
    for i, n in enumerate(("tinku", "pinky")):
        a = talk(n, t, i); look = 0.5; hop = abs(math.sin(t * 12 + i)) * 12 if t < T_SLIP else 0
        if n == "pinky" and active(t, "stop", 0, 1): a = (a[0], (2.0, 0.2))
        if n == "tinku" and T_FLY + 0.3 <= t <= S("caught") + 1.2: a = ((2.4, 0.3), (2.4, 0.3)); hop = 30 * math.sin(prog(t, T_CATCH - 0.4, T_CATCH + 0.4) * PI)
        if t >= S("explain") - 0.3: a = talk(n, t, i); hop = 0
        hands = kid(n, c, xs[n], GY, t, a, look, hop)
        if n == "tinku" and t >= T_CATCH + 0.3:
            hx, hy = hands[1]; payal_prop(c, hx, hy - 10, 0.8)
    if t >= T_NANI:
        nx = lerp(-140, 200 if True else 0, ease(prog(t, T_NANI, T_NANI + 1.8)))
        nani(c, nx, GY + 30, t, 0.95, ((0.3, 0.4), (0.9, 1.3)) if not speaking("nani", t) else talk("nani", t, 3), mo("nani", t), 0.5, blink(t, 2.0), abs(math.sin(t * 7)) * 6 if nx < 190 else 0, lantern=True)
    if t >= T_SLIP + 1.0: draw_text(c, "धप्प!", 1110, 470, 48, "#ffffff", "#8a5a1a", 5, lang="hi", alpha=1 - prog(t, T_SLIP + 1.8, T_SLIP + 2.6))

def scene_mela(c, t):
    mela_bg(c, t)
    dancing = t >= S("n_dance") - 0.3
    belled = t >= T_BELL
    ps = 0.8
    pa = ((1.9 + 0.3 * math.sin(t * 6), 0.6 + 0.4 * math.sin(t * 7)), (1.9 + 0.3 * math.sin(t * 6 + 2), 0.6 + 0.4 * math.sin(t * 7 + 1))) if dancing and not speaking("pinky", t) else talk("pinky", t, 1)
    if active(t, "bye1", 0, 3) or active(t, "bye2", 0, 3): pa = (pa[0], (2.1, 0.5 + 0.5 * math.sin(t * 11)))
    hop = abs(math.sin(t * 6)) * 14 if dancing else 0
    kid("pinky", c, 600, 480, t, pa, 0.0, hop, s=ps, lean=0.1 * math.sin(t * 3) if dancing else 0)
    payal_feet(c, 600, 480 - hop, ps)
    if dancing: notes(c, 470, 330, t, S("n_dance"), 3, "#ffd23f")
    if belled:
        chameli(c, 780, 480, t, 0.85, face=-1, dance=1.0, payal=False, bell=True, m=mo("chameli", t))
    nani(c, 1080, GY + 70, t, 0.9, ((0.6, -1.4), (0.6, -1.4)) if not speaking("nani", t) else talk("nani", t, 3), 0, 0.0, blink(t, 2.0))
    ta = talk("tinku", t, 0)
    if not speaking("tinku", t): ta = ((1.0 + 0.3 * abs(math.sin(t * 8)), 1.2), (1.0 + 0.3 * abs(math.sin(t * 8)), 1.2))
    if active(t, "bye1", 0, 3) or active(t, "bye2", 0, 3): ta = (ta[0], (2.1, 0.5 + 0.5 * math.sin(t * 11 + 1)))
    kid("tinku", c, 260, GY + 60, t, ta, 0.4, abs(math.sin(t * 5)) * 6)
    crowd(c, t)
    if dancing:
        r = random.Random(int(t * 3))
        for k in range(6): ell(c, r.uniform(380, 900), r.uniform(220, 460), 3, 3); setc(c, (1, 0.95, 0.5, 0.9)); c.fill()

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
    chameli(c, 820, 680, t, 1.05, face=-1, dance=0.6, payal=False, bell=True)

def _wrap(c, txt, maxw):
    if c.text_extents(txt).x_advance <= maxw: return [txt]
    words = txt.split(); best = None
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:]); w = max(c.text_extents(a).x_advance, c.text_extents(b).x_advance)
        if best is None or w < best[0]: best = (w, [a, b])
    return best[1]

def captions(c, t):
    cur = None
    for i, l in enumerate(LINES):
        nxt = LINES[i + 1]["start"] if i + 1 < len(LINES) else 1e9
        if l["start"] - 0.12 <= t <= min(l["end"] + 0.6, nxt - 0.12): cur = l
    if not cur or t >= T_OUTRO: return
    a = clamp((t - cur["start"] + 0.12) / 0.15)
    name, col = NAMES[cur["speaker"]]
    c.select_font_face("Fredoka", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); c.set_font_size(32)
    lines = _wrap(c, cur["en"], 1100)
    tw = max(c.text_extents(x).x_advance for x in lines)
    bw = tw + 56; bh = 22 + 40 * len(lines); bx, by = 640 - bw / 2, 708 - bh
    c.push_group()
    rrect(c, bx + 3, by + 5, bw, bh, 22); setc(c, (0.1, 0.05, 0.2, 0.25)); c.fill()
    rrect(c, bx, by, bw, bh, 22); fs(c, (1, 1, 1, 0.95), hexc(col), 5)
    nw = text_surface(name, 24, "#ffffff", None, 0, "hi").get_width()
    rrect(c, bx + 18, by - 24, nw + 24, 40, 20); fs(c, col, (1, 1, 1, 1), 3)
    draw_text(c, name, bx + 30, by - 4, 24, "#ffffff", None, 0, lang="hi", anchor="l")
    c.select_font_face("Fredoka", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); c.set_font_size(32)
    for i, ln in enumerate(lines):
        c.move_to(640 - c.text_extents(ln).x_advance / 2, by + 42 + i * 40); setc(c, "#2b2d42"); c.show_text(ln)
    c.pop_group_to_source(); c.paint_with_alpha(a)

# camera close-ups: (cue_or_time_start, end, x, y, zoom)
def FOCUS():
    return [
        (S("n_listen") - 0.3, E("n_listen") + 0.3, 1000, 470, 1.45),
        (S("gone") - 0.2, E("gone") + 0.6, 960, 360, 1.35),
        (S("n_shadow") - 0.2, E("run"), 640, 330, 1.25),
        (S("sad") - 0.4, E("sad") + 0.3, 560, 430, 1.5),
        (S("hooves") - 0.3, E("hooves") + 0.3, 860, 560, 1.4),
        (S("itschameli") - 0.3, E("onlegs") + 0.4, 840, 480, 1.4),
        (S("caught") - 0.4, E("caught") + 0.4, 560, 420, 1.35),
        (S("n_bell") - 0.2, E("bleat3") + 0.6, 720, 380, 1.3),
    ]
_FOC = None
def cam(t, t0):
    global _FOC
    if _FOC is None: _FOC = FOCUS()
    cx, cy, z = 640, 400, 1.0 + 0.05 * ease(prog(t, t0, t0 + 14))
    for a, b, fx, fy, fz in _FOC:
        w = ease(prog(t, a, a + 0.7)) * (1 - ease(prog(t, b - 0.5, b)))
        if w > 0: cx, cy, z = lerp(cx, fx, w), lerp(cy, fy, w), lerp(z, fz, w)
    cx = min(max(cx, 640 / z), W - 640 / z); cy = min(max(cy, 400 / z), H - 320 / z)   # never show outside the canvas
    return cx, cy, z

SCENES = [(0.0, scene_road), (T_COURT, scene_court), (T_NIGHT, scene_night), (T_STAIRS, scene_stairs), (T_MORNING, scene_morning),
          (T_CLUES, scene_clues), (T_TRAP, scene_trap), (T_CHASE, scene_chase), (T_MELA, scene_mela), (T_OUTRO, lambda c, t: outro_card(c, t))]
WIPE = {T_COURT, T_NIGHT, T_MORNING, T_CLUES, T_TRAP, T_MELA, T_OUTRO}

def frame(t, surf=None, with_captions=True):
    surf = surf or cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(surf)
    idx = max(i for i, (t0, _) in enumerate(SCENES) if t >= t0)
    t0, fn = SCENES[idx]
    cx, cy, z = cam(t, t0) if fn is not SCENES[-1][1] else (640, 400, 1.0)
    sh = 9 * math.exp(-max(0, t - S("n_shadow") - 1.2) * 4) if S("n_shadow") + 1.0 <= t <= S("n_shadow") + 2.4 else 0
    c.save(); c.translate(640 + sh * math.sin(t * 60), 400 + sh * math.cos(t * 47)); c.scale(z, z); c.translate(-cx, -cy)
    p = ease(prog(t, t0, t0 + 0.8)) if t0 in WIPE and idx > 0 else 1.0
    if p < 1:
        SCENES[idx - 1][1](c, t); c.save(); c.arc(cx, cy, 780 * p / z, 0, 2 * PI); c.clip(); fn(c, t); c.restore()
        c.arc(cx, cy, 780 * p / z, 0, 2 * PI); setc(c, "#ffd23f"); c.set_line_width(12 / z); c.stroke()
    else:
        fn(c, t)
    for tf in (T_STAIRS, T_TORCH):
        if tf <= t < tf + 0.25: c.rectangle(-W, -H, 3 * W, 3 * H); setc(c, (1, 1, 1, 0.5 * (1 - (t - tf) / 0.25))); c.fill()
    c.restore()
    if with_captions: captions(c, t)
    f = clamp((DURATION - t) / 1.5)   # no fade-in: the first frame is never black
    if f < 1: c.rectangle(0, 0, W, H); setc(c, (0, 0, 0, 1 - f)); c.fill()
    return surf

if __name__ == "__main__":
    os.makedirs("stills", exist_ok=True)
    for ts in sys.argv[1:]: frame(float(ts)).write_to_png(f"stills/f_{float(ts):06.2f}.png")
