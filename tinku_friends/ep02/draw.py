"""Story: The Park Ghost. Starts straight in the story (no title card, no brand text)."""
import sys, os, math, random, numpy as np, soundfile as sf, cairo
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "mahabharat", "lib"))
from chars import *
from scenery import park_bg, sky, lin
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
SCARED = ((0.7, -1.9), (0.7, -1.9))          # hands up to the face
HIPS = ((0.45, -1.1), (0.45, -1.1))

# ---------------------------------------------------------------- props
def ghost(c, x, y, s, t, peek_paws=1.0, tail=1.0, alpha=1.0):
    c.save(); c.translate(x, y + 8 * math.sin(t * 2.2)); c.scale(s, s)
    c.push_group()
    if tail > 0:   # wagging tail poking out at the back
        c.save(); c.translate(78, -60); c.rotate(-0.4 + 0.5 * math.sin(t * 12)); ell(c, 0, -22, 10, 26); fs(c, "#f3dfbf", dark("#f3dfbf", 0.75)); c.restore()
    for k, px in enumerate((-52, -20, 20, 52)):   # four little paws under the hem
        ell(c, px, -6 + 3 * math.sin(t * 8 + k), 15, 10); fs(c, "#f3dfbf", dark("#f3dfbf", 0.7), 2.5)
    c.move_to(-80, -20); c.curve_to(-92, -120, -60, -210, 0, -212); c.curve_to(60, -210, 92, -120, 80, -20)
    for k in range(6):
        x0 = 80 - k * 160 / 6; x1 = x0 - 160 / 6
        c.curve_to(x0 - 6, -8 + 10 * math.sin(t * 3 + k), x1 + 6, -36 + 10 * math.sin(t * 3 + k), x1, -20)
    c.close_path()
    g = cairo.LinearGradient(0, -212, 0, -10); g.add_color_stop_rgba(0, 1, 1, 1, 1); g.add_color_stop_rgba(1, 0.86, 0.9, 1, 1)
    c.set_source(g); c.fill_preserve(); setc(c, "#8a93b8"); c.set_line_width(3.5); c.stroke()
    for ex in (-28, 28): ell(c, ex, -140, 14, 20); setc(c, "#1a1a2e"); c.fill()
    ell(c, 0, -96, 16, 12); setc(c, "#1a1a2e"); c.fill()
    c.pop_group_to_source(); c.paint_with_alpha(alpha); c.restore()

def bush(c, x, y, s, t, shake=0.0, night=True):
    c.save(); c.translate(x + shake * 4 * math.sin(t * 40), y); c.scale(s, s)
    cols = ("#2f6b4a", "#3d8a5a", "#4fa86a") if night else ("#3f9e3f", "#55b84a", "#6fd04a")
    for dx, dy, r in ((-90, -40, 60), (-30, -80, 75), (50, -70, 70), (100, -30, 55), (0, -30, 80)): ell(c, dx, dy, r, r * 0.8); setc(c, cols[0]); c.fill()
    for dx, dy, r in ((-60, -60, 40), (20, -100, 45), (80, -60, 38)): ell(c, dx, dy, r, r * 0.7); setc(c, cols[1]); c.fill()
    for dx, dy, r in ((-40, -80, 18), (40, -112, 20)): ell(c, dx, dy, r, r * 0.6); setc(c, cols[2]); c.fill()
    c.restore()

def bench(c, x, y, s=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    for lx in (-190, 170): rrect(c, lx, -60, 20, 64, 4); fs(c, "#5a3a22", "#2a1a10", 2)
    for k in range(3): rrect(c, -220, -80 - k * 32, 440, 24, 8); fs(c, "#b8743a", "#5a3414", 3)
    for k in range(3): c.move_to(-200, -68 - k * 32); c.line_to(200, -68 - k * 32); setc(c, (0.4, 0.2, 0.08, 0.35)); c.set_line_width(2); c.stroke()
    c.restore()

def clothesline(c, t, sheet_on=True, sheet_p=1.0):
    for px in (960, 1230):
        rrect(c, px - 6, 300, 12, 230, 4); fs(c, "#7a5a3a", "#3a2a1a", 2)
    c.move_to(960, 312); c.curve_to(1050, 340, 1140, 340, 1230, 312); setc(c, "#d8d8e0"); c.set_line_width(2.5); c.stroke()
    for k, (x0, col) in enumerate(((990, "#ff8fb0"), (1160, "#8fc0ff"))):   # other clothes on the line
        c.save(); c.translate(x0, 330); c.rotate(0.05 * math.sin(t * 2 + k)); rrect(c, -22, 0, 44, 52, 6); fs(c, col, dark(col, 0.7), 2); c.restore()
    if sheet_on and sheet_p > 0:
        c.save(); c.translate(1075, 330); c.scale(1, sheet_p); c.rotate(0.03 * math.sin(t * 2))
        c.move_to(-60, 0); c.line_to(60, 0); c.curve_to(64, 60, 58, 110, 62, 140)
        for k in range(5): c.curve_to(50 - k * 24, 150, 40 - k * 24, 130, 38 - k * 24, 140)
        c.curve_to(-64, 100, -58, 50, -60, 0); c.close_path(); fs(c, "#f4f6ff", "#8a93b8", 2.5)
        c.restore()
        for px in (1030, 1120): rrect(c, px - 3, 322, 6, 16, 2); setc(c, "#ffd23f"); c.fill()

def owl(c, x, y, t, on):
    c.save(); c.translate(x, y); c.scale(1.4, 1.4)
    ell(c, 0, 0, 26, 32); fs(c, "#8a6a4a", "#3a2a1a", 2.5); ell(c, 0, 8, 16, 20); setc(c, "#c9a77a"); c.fill()
    poly(c, [(-22, -24), (-14, -40), (-6, -26)]); setc(c, "#6a4a2a"); c.fill(); poly(c, [(22, -24), (14, -40), (6, -26)]); c.fill()
    bl = ((t + 0.7) % 2.6) < 0.14
    for ex in (-11, 11):
        ell(c, ex, -10, 10, 10); fs(c, "#ffe066" if on else "#d9c070", "#3a2a1a", 2)
        if not bl: ell(c, ex, -10, 4.5, 5.5); setc(c, "#1a1a1a"); c.fill()
        else: c.move_to(ex - 8, -10); c.line_to(ex + 8, -10); setc(c, "#3a2a1a"); c.set_line_width(2.5); c.stroke()
    poly(c, [(-4, -2), (4, -2), (0, 6)]); setc(c, "#ff9f1a"); c.fill()
    c.restore()

def torch_beam(c, x0, y0, x1, y1, a):
    ang = math.atan2(y1 - y0, x1 - x0); L = math.hypot(x1 - x0, y1 - y0) + 120
    c.save(); c.translate(x0, y0); c.rotate(ang)
    g = cairo.LinearGradient(0, 0, L, 0); g.add_color_stop_rgba(0, 1, 0.97, 0.7, 0.55 * a); g.add_color_stop_rgba(1, 1, 0.97, 0.7, 0.05 * a)
    c.move_to(0, -8); c.line_to(L, -150); c.line_to(L, 150); c.line_to(0, 8); c.close_path(); c.set_source(g); c.fill()
    c.restore()
    rg = cairo.RadialGradient(x1, y1, 10, x1, y1, 170); rg.add_color_stop_rgba(0, 1, 0.97, 0.75, 0.35 * a); rg.add_color_stop_rgba(1, 1, 0.97, 0.75, 0)
    c.set_source(rg); c.arc(x1, y1, 170, 0, 2 * PI); c.fill()

# ---------------------------------------------------------------- skies / lighting
def night_overlay(c, t, k=1.0):
    c.rectangle(0, 0, W, H); setc(c, (0.05, 0.06, 0.25, 0.62 * k)); c.fill()
    rg = cairo.RadialGradient(1080, 110, 20, 1080, 110, 260); rg.add_color_stop_rgba(0, 1, 1, 0.9, 0.35 * k); rg.add_color_stop_rgba(1, 1, 1, 0.9, 0)
    c.set_source(rg); c.paint()
    c.push_group(); ell(c, 1080, 110, 44, 44); setc(c, (1, 0.98, 0.85, 1)); c.fill()
    c.set_operator(cairo.OPERATOR_DEST_OUT); ell(c, 1100, 98, 40, 40); setc(c, (0, 0, 0, 1)); c.fill(); c.set_operator(cairo.OPERATOR_OVER)
    c.pop_group_to_source(); c.paint_with_alpha(k)                                  # crescent moon
    r = random.Random(4)
    for i in range(55):
        x, y = r.uniform(0, W), r.uniform(10, 300); tw = 0.5 + 0.5 * math.sin(t * 3 + i)
        c.arc(x, y, r.uniform(1.2, 2.6), 0, 2 * PI); setc(c, (1, 1, 0.85, k * (0.4 + 0.6 * tw))); c.fill()
    for i in range(10):   # fireflies
        x = (i * 137 + t * 25) % 1400 - 60; y = 420 + 60 * math.sin(t * 0.8 + i * 2)
        c.arc(x, y, 3, 0, 2 * PI); setc(c, (1, 1, 0.5, k * (0.5 + 0.5 * math.sin(t * 5 + i)))); c.fill()

def dusk_overlay(c, t):
    g = cairo.LinearGradient(0, 0, 0, 470); g.add_color_stop_rgba(0, 1, 0.55, 0.3, 0.45); g.add_color_stop_rgba(1, 1, 0.75, 0.4, 0.25)
    c.set_source(g); c.rectangle(0, 0, W, 470); c.fill()
    c.rectangle(0, 0, W, H); setc(c, (1, 0.6, 0.3, 0.12)); c.fill()
    if t >= S("star") - 0.2:   # first star pops
        q = back(prog(t, S("star") - 0.2, S("star") + 0.3)); tw = 1 + 0.25 * math.sin(t * 6)
        if q > 0.02:
            c.save(); c.translate(860, 90); c.scale(q * tw, q * tw)
            pts = [((22 if i % 2 == 0 else 9) * math.cos(-PI / 2 + i * PI / 5), (22 if i % 2 == 0 else 9) * math.sin(-PI / 2 + i * PI / 5)) for i in range(10)]
            poly(c, pts); setc(c, "#fff6b0"); c.fill(); c.restore()

# ---------------------------------------------------------------- the kids
def kid(name, c, x, y, t, arms, look=0.0, hop=0.0, s=0.88, lean=0.0):
    fn = {"tinku": tinku, "pinky": pinky, "golu": golu}[name]
    fn(c, x, y, t, s, arms, mo(name, t), look, blink(t, {"tinku": 0.3, "pinky": 1.4, "golu": 2.2}[name]), hop, lean)

def ball_pos(t):
    """Ball thrown between the kids in the dusk scene."""
    legs = [(S("catch") - 0.6, S("catch") + 0.5, 720, 300), (S("gotit") + 0.2, S("gotit") + 1.2, 300, 520), (S("higher") + 0.8, S("higher") + 2.4, 520, 720)]
    for a, b, x0, x1 in legs:
        if a <= t <= b:
            p = (t - a) / (b - a); h = 220 if x1 == 720 else 150
            return lerp(x0, x1, p), 360 - h * math.sin(PI * p)
    return None

def scene_dusk(c, t):
    park_bg(c, t); dusk_overlay(c, t)
    xs = {"tinku": 300, "pinky": 520, "golu": 720}
    for i, n in enumerate(("tinku", "pinky", "golu")):
        a = talk(n, t, i); look = 0.0; hop = 0.0
        if active(t, "star", 0, 3.0) or active(t, "twinkle", 0, 0.5): a = (a[0], (2.4, 0.3)) if n == "pinky" else a; look = -0.2
        if n == "golu" and (active(t, "catch", 0.4, 0.4) or active(t, "higher", 0, 1.5)): a = ((2.3, 0.4), (2.3, 0.4)); hop = abs(math.sin(t * 7)) * 18
        if n == "tinku" and active(t, "gotit", 0.3, 0.3): a = ((2.2, 0.5), (2.2, 0.5))
        kid(n, c, xs[n], GY, t, a, look, hop)
    bp = ball_pos(t)
    if bp: ell(c, bp[0], bp[1], 18, 18); fs(c, "#ff4f5f", "#a8202e", 3); c.arc(bp[0], bp[1], 12, 0.2, 2.2); setc(c, (1, 1, 1, 0.7)); c.set_line_width(3); c.stroke()
    run = ease(prog(t, S("bark1") + 0.3, S("moti_runs") + 1.5))
    mx = lerp(920, 1450, run); mh = abs(math.sin(t * 9)) * 22 if run > 0 else abs(math.sin(t * 5)) * 6
    moti(c, mx, GY, t, 0.78, mo("moti", t), 0.3, blink(t, 0.9), mh, 2.0)
    if run > 0 and mx < 1400: ell(c, mx + 70, GY - 120 - mh, 14, 14); fs(c, "#ff4f5f", "#a8202e", 2)

def night_base(c, t, ghost_x=None, shake=0.0):
    park_bg(c, t); night_overlay(c, t)
    owl(c, 75, 345, t, active(t, "hoo", 1.6, 4.0) or active(t, "owl", 0, 0.5))
    clothesline(c, t, sheet_on=False)
    bush(c, 1040, 610, 1.15, t, shake)

def scene_night(c, t):
    night_base(c, t, shake=1.0 if active(t, "rustle", 0.3, 1.5) else 0.0)
    gp = ease(prog(t, T_GHOST, T_GHOST + 1.4))
    if gp > 0: ghost(c, 1040, 600 - 70 * gp, 0.95, t, alpha=gp)
    bush(c, 1040, 640, 0.7, t, 0)  # front leaves over the ghost's hem
    xs = {"tinku": 360, "pinky": 530, "golu": 690}
    for i, n in enumerate(("tinku", "pinky", "golu")):
        a = talk(n, t, i); look = 0.0; hop = 0.0
        if n == "golu" and (active(t, "dark", 0, 1) or t >= S("ghost")): a = SCARED
        if n == "tinku" and active(t, "brave", 0, 0.5): a = HIPS
        if n == "tinku" and active(t, "call", 0, 0.3): a = ((0.5, -1.8), (0.5, -1.8))
        if n == "pinky" and active(t, "rustle", 0, 1.5): a = (a[0], (1.55, 0.1)); look = 0.6
        if t >= S("ghost") - 0.3: a = SCARED; hop = abs(math.sin(t * 14)) * 6
        if active(t, "hoo", 1.0, 0.8) or active(t, "owl", 0, 0.5): look = -0.5
        kid(n, c, xs[n], GY, t, a, look, hop)

def scene_hide(c, t):
    gx = lerp(1040, 900, ease(prog(t, S("coming") - 0.5, S("coming") + 2.0)))
    night_base(c, t)
    ghost(c, gx, 530, 0.95, t)
    focus_legs = active(t, "legs", 0, 1.0); focus_tail = active(t, "tail", 0, 1.0) or active(t, "ghosttail", 0, 0.5)
    if focus_legs or focus_tail:   # spotlight on the clue
        fx, fy = (gx, 515) if focus_legs else (gx + 74, 460)
        rg = cairo.RadialGradient(fx, fy, 10, fx, fy, 90); rg.add_color_stop_rgba(0, 1, 1, 0.7, 0.45); rg.add_color_stop_rgba(1, 1, 1, 0.7, 0)
        c.set_source(rg); c.arc(fx, fy, 90, 0, 2 * PI); c.fill()
        c.arc(fx, fy, 70 + 6 * math.sin(t * 8), 0, 2 * PI); setc(c, (1, 0.9, 0.3, 0.9)); c.set_line_width(5); c.stroke()
    xs = {"tinku": 380, "pinky": 520, "golu": 650}
    duck = ease(prog(t, T_HIDE, T_HIDE + 0.5))
    for i, n in enumerate(("tinku", "pinky", "golu")):
        a = talk(n, t, i); look = 0.6
        if n == "golu": a = SCARED
        if n == "tinku" and t >= S("torch") - 0.2: a = (a[0], (1.45, 0.15))
        kid(n, c, xs[n], GY + 70 * duck, t, a, look, 0)
    bench(c, 520, GY + 10, 1.0)
    for k in range(7):   # low hedge in front of the bench hides the crouching kids' legs
        x = 290 + k * 78; ell(c, x, GY + 40, 62, 46); setc(c, "#2f6b4a"); c.fill(); ell(c, x - 12, GY + 26, 30, 20); setc(c, "#3d8a5a"); c.fill()
    if t >= S("torch") + 0.6:
        torch_beam(c, 470, GY - 120 + 70 * duck - 60, gx, 450, ease(prog(t, S("torch") + 0.6, S("torch") + 0.9)))

def scene_reveal(c, t):
    park_bg(c, t); night_overlay(c, t, 0.85)
    owl(c, 75, 345, t, False)
    hung = t >= S("hang") + 1.2 and t < T_GOLUGHOST
    clothesline(c, t, sheet_on=hung, sheet_p=ease(prog(t, S("hang") + 1.2, S("hang") + 1.6)))
    bush(c, 1040, 610, 1.15, t)
    # torch light pool
    rg = cairo.RadialGradient(820, 520, 30, 820, 520, 420); rg.add_color_stop_rgba(0, 1, 0.97, 0.75, 0.32); rg.add_color_stop_rgba(1, 1, 0.97, 0.75, 0)
    c.set_source(rg); c.paint()
    off = ease(prog(t, T_REVEAL + 0.4, T_REVEAL + 1.2))
    happy = t > T_REVEAL + 1.0
    moti(c, 900, GY, t, 0.8, mo("moti", t), -0.3, blink(t, 0.9), abs(math.sin(t * 8)) * 20 if happy else 0, 3.0 if happy else 0.5)
    if happy and t < S("hang"): ell(c, 830, GY - 128 - abs(math.sin(t * 8)) * 20, 14, 14); fs(c, "#ff4f5f", "#a8202e", 2)
    if off < 1:   # the sheet whooshes up and away
        ghost(c, 900 + 300 * off, 540 - 420 * off, 0.95 * (1 - 0.3 * off), t, tail=0, alpha=1 - off * 0.6)
    xs = {"tinku": 330, "pinky": 500, "golu": 660}
    for i, n in enumerate(("tinku", "pinky", "golu")):
        a = talk(n, t, i); hop = 0.0
        if active(t, "laugh", 0, 0.6) or active(t, "boo", 0, 1.0): a = ((0.6, -1.4), (0.6, -1.4)); hop = abs(math.sin(t * 10)) * 10
        if n == "golu" and t >= T_GOLUGHOST + 0.4: continue
        kid(n, c, xs[n], GY, t, a, 0.3, hop)
    if t >= T_GOLUGHOST:   # the sheet blows off the line onto Golu
        p = ease(prog(t, T_GOLUGHOST, T_GOLUGHOST + 0.6))
        gx, gy = lerp(1075, 660, p), lerp(420, GY + 6, p)
        wig = 0.12 * math.sin(t * 12) if active(t, "boo", 0, 0.8) else 0
        c.save(); c.translate(gx, gy); c.rotate(wig); c.translate(-gx, -gy)
        if p >= 1:
            for lx in (-16, 16): ell(c, gx + lx, gy - 6, 20, 10); fs(c, "#2f7bff")
        ghost(c, gx, gy - 4, 0.72 + 0.2 * p, t, peek_paws=0, tail=0)
        c.restore()

def streetlight(c, x, t):
    rrect(c, x - 7, 250, 14, 380, 5); fs(c, "#3a3f5a", "#1a1f2a", 2)
    c.move_to(x, 260); c.curve_to(x, 230, x + 30, 220, x + 60, 228); setc(c, "#3a3f5a"); c.set_line_width(10); c.stroke()
    rrect(c, x + 44, 226, 40, 22, 8); fs(c, "#ffe9a0", "#3a3f5a", 3)
    c.move_to(x + 50, 248); c.line_to(x - 140, 640); c.line_to(x + 300, 640); c.line_to(x + 78, 248); c.close_path()
    g = cairo.LinearGradient(0, 248, 0, 640); g.add_color_stop_rgba(0, 1, 0.95, 0.6, 0.42); g.add_color_stop_rgba(1, 1, 0.95, 0.6, 0.08); c.set_source(g); c.fill()

def gate(c):
    for px in (150, 470):
        rrect(c, px - 22, 300, 44, 340, 6); fs(c, "#c9a06a", "#6a4a2a", 3); rrect(c, px - 30, 290, 60, 22, 6); fs(c, "#e0b880", "#6a4a2a", 3)
    c.move_to(150, 330); c.curve_to(250, 270, 370, 270, 470, 330); setc(c, "#6a4a2a"); c.set_line_width(10); c.stroke()
    draw_text(c, "PARK", 310, 290, 34, "#ffe9a0", "#6a4a2a", 5, lang="en")

def scene_home(c, t):
    park_bg(c, t); night_overlay(c, t, 0.85); gate(c); streetlight(c, 860, t)
    walk = ease(prog(t, T_HOME, T_HOME + 3.0))
    xs = {"tinku": lerp(900, 560, walk), "pinky": lerp(1060, 720, walk), "golu": lerp(1200, 860, walk)}
    walking = 0 < walk < 1
    for i, n in enumerate(("tinku", "pinky", "golu")):
        a = talk(n, t, i); hop = abs(math.sin(t * 8 + i)) * 8 if walking else 0.0
        if active(t, "bye1", 0, 3) or active(t, "bye2", 0, 3): a = (a[0], (2.1, 0.5 + 0.5 * math.sin(t * 11 + i))); hop = abs(math.sin(t * 5 + i)) * 10
        if n == "golu" and active(t, "hug", 0, 2.0): a = ((1.5, -1.2), (1.5, -1.2))
        kid(n, c, xs[n], GY, t, a, 0.0, hop)
    mx = lerp(1330, 1010, walk) if not active(t, "hug", 0, 2.0) else 960
    moti(c, mx, GY, t, 0.78, mo("moti", t), -0.3, blink(t, 0.9), abs(math.sin(t * 8)) * (14 if walking else 6), 2.5)
    if active(t, "hug", 0, 2.0):
        for k in range(3):
            q = prog(t, S("hug") + 0.3 * k, S("hug") + 0.3 * k + 1.2)
            if 0 < q < 1: draw_text(c, "♥", 930 + 30 * k, 420 - 80 * q, 40, "#ff4f8b", None, 0, lang="en", alpha=1 - q)

def outro_card(c, t):
    lt = t - T_OUTRO
    gr = cairo.RadialGradient(640, 380, 40, 640, 380, 900); gr.add_color_stop_rgba(0, *hexc("#fff3c4")); gr.add_color_stop_rgba(1, *hexc("#ff9fcf")); c.set_source(gr); c.paint()
    r = random.Random(5); cols = ["#ff3b3b", "#ff8c1a", "#ffd21a", "#2fbf4a", "#2f8bff", "#9b3fd6"]
    for k in range(60):
        x0 = r.uniform(0, W); sp = r.uniform(60, 130); ph = r.uniform(0, 800)
        y = (ph + lt * sp) % 800 - 40; x = x0 + 20 * math.sin(lt * 2 + k)
        c.save(); c.translate(x, y); c.rotate(lt * 2 + k); rrect(c, -6, -3, 12, 6, 2); setc(c, cols[k % 6]); c.fill(); c.restore()
    p = back(prog(lt, 0.1, 0.6))
    if p > 0.02: c.save(); c.translate(640, 140); c.scale(p, p); draw_text(c, "Bye-bye!", 0, 0, 130, "#d81b60", "#ffffff", 12, lang="en"); c.restore()
    p2 = back(prog(lt, 0.5, 1.0))
    if p2 > 0.02:
        c.save(); c.translate(640, 262); c.scale(p2, p2); draw_text(c, "See you next time!", 0, 0, 46, "#7c2d12", "#ffffff", 5, lang="en")
        draw_text(c, NEXT, 0, 58, 36, "#2f7bff", "#ffffff", 4, lang="en"); c.restore()
    for i, (fn, x) in enumerate(((tinku, 360), (pinky, 560), (golu, 750))):
        fn(c, x, 680, t, 0.8, ((0.15, 0.3), (2.1, 0.5 + 0.5 * math.sin(t * 10 + i))), 0, 0, blink(t, i), abs(math.sin(t * 5 + i)) * 12)
    moti(c, 930, 680, t, 0.8, 0, -0.3, False, abs(math.sin(t * 6)) * 12, 2.5)

def badge(c):
    c.save(); c.translate(24, 20)
    rrect(c, 0, 0, 210, 44, 22); fs(c, (1, 1, 1, 0.85), hexc("#ff6b1a"), 3)
    draw_text(c, "Tinku & Friends", 105, 22, 24, "#ff6b1a", None, 0, lang="en"); c.restore()

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
    bw = tw + 56; bh = 58; bx, by = 640 - bw / 2, 706 - bh
    c.push_group()
    rrect(c, bx + 3, by + 5, bw, bh, 22); setc(c, (0.1, 0.05, 0.2, 0.25)); c.fill()
    rrect(c, bx, by, bw, bh, 22); fs(c, (1, 1, 1, 0.95), hexc(col), 5)
    nw = text_surface(name, 24, "#ffffff", None, 0, "hi").get_width()
    rrect(c, bx + 18, by - 24, nw + 24, 40, 20); fs(c, col, (1, 1, 1, 1), 3)
    draw_text(c, name, bx + 30, by - 4, 24, "#ffffff", None, 0, lang="hi", anchor="l")
    c.select_font_face("Fredoka", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); c.set_font_size(34)
    c.move_to(640 - tw / 2, by + 41); setc(c, "#2b2d42"); c.show_text(txt)
    c.pop_group_to_source(); c.paint_with_alpha(a)

SCENES = [(0.0, scene_dusk), (T_NIGHT, scene_night), (T_HIDE, scene_hide), (T_REVEAL, scene_reveal), (T_HOME, scene_home), (T_OUTRO, lambda c, t: outro_card(c, t))]
WIPE = {T_NIGHT, T_HOME, T_OUTRO}

def frame(t, surf=None, with_captions=True):
    surf = surf or cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(surf)
    idx = max(i for i, (t0, _) in enumerate(SCENES) if t >= t0)
    t0, fn = SCENES[idx]
    # camera: slow push-in per scene + a shake on the ghost sting
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
    if T_HIDE <= t < T_HIDE + 0.25 or T_REVEAL <= t < T_REVEAL + 0.25:   # quick flash cut
        c.rectangle(0, 0, W, H); setc(c, (1, 1, 1, 0.5 * (1 - (t - (T_HIDE if t < T_REVEAL else T_REVEAL)) / 0.25))); c.fill()
    c.restore()
    if with_captions: captions(c, t)
    f = clamp(min(t / 0.25, (DURATION - t) / 1.5))
    if f < 1: c.rectangle(0, 0, W, H); setc(c, (0, 0, 0, 1 - f)); c.fill()
    return surf

if __name__ == "__main__":
    os.makedirs("stills", exist_ok=True)
    for ts in sys.argv[1:]: frame(float(ts)).write_to_png(f"stills/f_{float(ts):06.2f}.png")
