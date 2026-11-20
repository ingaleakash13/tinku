"""Story: Golu vs the Final Boss. Starts straight in the story (no title card, no brand text).
Original cartoon video-game world: a beach city at sunset with a game HUD (hearts, coins, mini-map, mission banners)."""
import sys, os, math, random, numpy as np, soundfile as sf, cairo
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "mahabharat", "lib"))
from chars import *
from scenery import room_bg, sky, lin, cloud
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
CHEER = ((2.5, 0.3), (2.5, 0.3))
HOLD = ((0.25, -1.75), (0.25, -1.75))         # hands together in front (controller / steering wheel)
SCARED = ((0.7, -1.9), (0.7, -1.9))
HIPS = ((0.45, -1.1), (0.45, -1.1))

def kid(name, c, x, y, t, arms, look=0.0, hop=0.0, s=0.88, lean=0.0):
    fn = {"tinku": tinku, "pinky": pinky, "golu": golu}[name]
    return fn(c, x, y, t, s, arms, mo(name, t), look, blink(t, {"tinku": 0.3, "pinky": 1.4, "golu": 2.2}[name]), hop, lean)

def puppy(c, x, y, t, s=0.78, hop=0.0, wag=2.0, look=-0.3):
    moti(c, x, y, t, s, mo("moti", t), look, blink(t, 0.9), hop, wag)

def star(c, x, y, r, col="#ffd23f", out="#c98f00"):
    pts = [((r if i % 2 == 0 else r * 0.45) * math.cos(-PI / 2 + i * PI / 5) + x, (r if i % 2 == 0 else r * 0.45) * math.sin(-PI / 2 + i * PI / 5) + y) for i in range(10)]
    poly(c, pts); fs(c, col, out, 2)
def heart(c, x, y, s=1.0, col="#ff4f8b", a=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.move_to(0, 12); c.curve_to(-26, -6, -14, -24, 0, -10); c.curve_to(14, -24, 26, -6, 0, 12); setc(c, (*hexc(col)[:3], a)); c.fill(); c.restore()

# ---------------------------------------------------------------- game values
def coins_at(t): return 490 + (500 if t >= T_HAPPY + 0.8 else 0)
def last_coin_change(t): return T_HAPPY + 0.8 if t >= T_HAPPY + 0.8 else -9

# ---------------------------------------------------------------- the game world
BUILD = [(0, 230, 190, "#ff9fcf", "ICE CREAM", "#ff3b8b"), (250, 180, 150, "#7fe0ff", "SURF", "#0077ff"),
         (450, 260, 230, "#ffe066", "PIZZA", "#ff5b1a"), (740, 200, 170, "#b99bff", "ARCADE", "#ff2fd0"),
         (980, 220, 210, "#8cf0b0", "JUICE", "#00a86b"), (1230, 190, 160, "#ffb38a", "TOYS", "#ff3b3b")]
TILE = 1500

def palm(c, x, y, s, t):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.move_to(-10, 0); c.curve_to(-6, -80, 6, -160, 22, -230); c.line_to(36, -226); c.curve_to(22, -160, 14, -80, 12, 0); c.close_path()
    c.set_source(lin(c, -10, 0, 30, 0, [(0, "#b8743a"), (1, "#7a4a24")])); c.fill()
    for k in range(7): c.move_to(-6 + k * 2.5, -30 - k * 30); c.line_to(14 + k * 2.5, -34 - k * 30)
    setc(c, (0.35, 0.2, 0.08, 0.5)); c.set_line_width(2.5); c.stroke()
    for k, a in enumerate((-2.6, -2.0, -1.3, -0.6, 0.0, 0.6)):
        sw = 0.05 * math.sin(t * 1.5 + k)
        c.save(); c.translate(29, -230); c.rotate(a + sw)
        c.move_to(0, 0); c.curve_to(40, -30, 90, -20, 120, 20); c.curve_to(80, -2, 40, 0, 0, 8); c.close_path(); fs(c, "#2fbf6a", "#1a7a40", 2)
        c.restore()
    for dx in (20, 36): ell(c, dx, -222, 9, 9); fs(c, "#7a4a24")
    c.restore()

def building(c, x, base, w, h, col, sign, ncol, t, k):
    rrect(c, x, base - h, w, h + 10, 6); c.set_source(lin(c, x, 0, x + w, 0, [(0, light(col, 0.15)), (1, dark(col, 0.85))])); c.fill_preserve()
    setc(c, dark(col, 0.6)); c.set_line_width(3); c.stroke()
    rrect(c, x - 8, base - h - 10, w + 16, 16, 5); fs(c, dark(col, 0.75))
    for row in range(int((h - 80) / 46)):
        for col_ in range(int((w - 30) / 44)):
            wx = x + 22 + col_ * 44; wy = base - h + 64 + row * 46
            lit = (k * 7 + row * 3 + col_) % 4 != 0
            rrect(c, wx, wy, 26, 30, 4); setc(c, (1, 0.95, 0.7, 0.95) if lit else (0.35, 0.4, 0.6, 0.8)); c.fill()
    fl = 0.75 + 0.25 * math.sin(t * 7 + k * 2) if (k % 3) else 1.0          # neon sign with a little flicker
    tw = text_surface(sign, 30, "#ffffff", ncol, 4, "en").get_width()
    rrect(c, x + w / 2 - tw / 2 - 12, base - h + 14, tw + 24, 40, 12); fs(c, (0.15, 0.1, 0.3, 0.92), hexc(ncol), 3)
    draw_text(c, sign, x + w / 2, base - h + 35, 30, "#ffffff", ncol, 4, lang="en", alpha=fl)
    rrect(c, x + w / 2 - 22, base - 56, 44, 56, 6); fs(c, "#5a3a8a", "#2a1a4a", 2)    # door

def city_bg(c, t, scroll=0.0):
    sky(c, [(0, "#6b5cff"), (0.45, "#ff7ac8"), (0.8, "#ffb36b"), (1, "#ffe39a")], 470)
    # retro striped sun
    sx, sy = 900 - (scroll * 0.03) % 200, 300
    g = cairo.RadialGradient(sx, sy, 60, sx, sy, 380); g.add_color_stop_rgba(0, 1, 0.9, 0.5, 0.55); g.add_color_stop_rgba(1, 1, 0.6, 0.6, 0); c.set_source(g); c.paint()
    c.save(); c.arc(sx, sy, 120, 0, 2 * PI); c.clip()
    c.set_source(lin(c, 0, sy - 120, 0, sy + 120, [(0, "#fff36b"), (1, "#ff5fa8")])); c.paint()
    for k in range(6):
        yy = sy + 10 + k * 20; c.rectangle(sx - 130, yy, 260, 4 + k * 1.6); setc(c, (1, 0.5, 0.75, 0.9)); c.fill()
    c.restore()
    r = random.Random(3)
    for i in range(4): cloud(c, (r.uniform(0, 1500) - scroll * 0.06 + t * 6) % 1600 - 200, r.uniform(60, 170), r.uniform(0.6, 1.0), 0.85, warm=True)
    # sea
    c.set_source(lin(c, 0, 360, 0, 470, [(0, "#3fd0e8"), (1, "#1a8ad0")])); c.rectangle(0, 360, W, 110); c.fill()
    for k in range(18):
        x = (k * 97 - scroll * 0.15 + 20 * math.sin(t + k)) % 1400 - 60; y = 372 + (k % 5) * 18
        c.move_to(x, y); c.line_to(x + 40, y); setc(c, (1, 1, 1, 0.35 + 0.25 * math.sin(t * 3 + k))); c.set_line_width(3); c.stroke()
    # far skyline
    off = (scroll * 0.2) % 600
    for k in range(4):
        bx = k * 600 - off - 100
        for dx, w_, h_ in ((0, 70, 120), (80, 50, 170), (140, 90, 90), (240, 60, 150), (320, 80, 110), (420, 60, 190), (500, 70, 100)):
            rrect(c, bx + dx, 360 - h_, w_, h_, 4); setc(c, (0.45, 0.3, 0.75, 0.55)); c.fill()
    # mid buildings
    off = (scroll * 0.5) % TILE
    for rep in (0, 1):
        for k, (bx, w_, h_, col, sign, ncol) in enumerate(BUILD):
            x = bx + rep * TILE - off
            if x > W + 20 or x + w_ < -20: continue
            building(c, x, 480, w_, h_, col, sign, ncol, t, k)
    # sidewalk + road
    c.set_source(lin(c, 0, 470, 0, 540, [(0, "#ffd0e0"), (1, "#f4a8c8")])); c.rectangle(0, 470, W, 70); c.fill()
    for k in range(16):
        x = k * 90 - (scroll * 0.9) % 90; c.move_to(x, 470); c.line_to(x - 20, 540)
    setc(c, (0.8, 0.4, 0.6, 0.35)); c.set_line_width(2); c.stroke()
    off = (scroll * 0.9) % 430
    for k in range(5): palm(c, k * 430 - off + 60, 500, 0.9, t)
    c.set_source(lin(c, 0, 540, 0, 720, [(0, "#5a4a8a"), (1, "#3a2f62")])); c.rectangle(0, 540, W, 180); c.fill()
    rrect(c, -10, 536, W + 20, 10, 3); setc(c, "#ffe066"); c.fill()
    off = scroll % 160
    for k in range(10): rrect(c, k * 160 - off, 652, 80, 10, 5); setc(c, (1, 0.95, 0.6, 0.9)); c.fill()

def hearts(c, x, y, n=3):
    for k in range(n):
        c.save(); c.translate(x + k * 46, y); c.scale(1.1, 1.1)
        c.move_to(0, 12); c.curve_to(-26, -6, -14, -24, 0, -10); c.curve_to(14, -24, 26, -6, 0, 12); fs(c, "#ff3b6b", "#ffffff", 3)
        ell(c, -7, -8, 4, 3); setc(c, (1, 1, 1, 0.6)); c.fill(); c.restore()

def coin(c, x, y, t, s=1.0, k=0):
    sq = abs(math.cos(t * 4 + k))
    c.save(); c.translate(x, y); c.scale(s * max(0.2, sq), s)
    ell(c, 0, 0, 18, 18); fs(c, "#ffd23f", "#c98f00", 3); ell(c, 0, 0, 11, 11); setc(c, "#ffe98a"); c.fill()
    star(c, 0, 1, 8, "#ffd23f", "#c98f00"); c.restore()

def minimap(c, x, y, t, dotx=0.0):
    ell(c, x, y, 62, 62); fs(c, (0.16, 0.12, 0.32, 0.85), (1, 1, 1, 1), 4)
    c.save(); ell(c, x, y, 58, 58); c.clip()
    for k in range(-3, 4): c.move_to(x - 70, y + k * 26 + 6); c.line_to(x + 70, y + k * 26 - 10)
    for k in range(-3, 4): c.move_to(x + k * 30, y - 70); c.line_to(x + k * 30 + 14, y + 70)
    setc(c, (1, 1, 1, 0.3)); c.set_line_width(5); c.stroke()
    ell(c, x + 30, y - 30, 22, 14); setc(c, (0.25, 0.75, 0.95, 0.7)); c.fill()
    c.restore()
    px, py = x + dotx, y + 6
    poly(c, [(px, py - 12), (px + 9, py + 8), (px, py + 3), (px - 9, py + 8)]); fs(c, "#ffd23f", "#ffffff", 2)
    if (t * 2) % 1 < 0.6: ell(c, x - 26, y + 20, 6, 6); fs(c, "#ff3b6b", "#ffffff", 2)    # mission marker

HUD_L, HUD_R = 0, 0          # x-shift of the left / right HUD blocks (short.py moves them inside its vertical crop)
def hud(c, t, alpha=1.0, clock=False):
    c.push_group(); c.save(); c.translate(HUD_L, 0)
    rrect(c, 18, 16, 300, 96, 20); setc(c, (0.12, 0.08, 0.28, 0.55)); c.fill()
    hearts(c, 52, 46)
    pop = 1 + 0.35 * math.exp(-(t - last_coin_change(t)) * 8)
    coin(c, 54, 88, t, 0.95)
    c.save(); c.translate(82, 89); c.scale(pop, pop); draw_text(c, f"{coins_at(t)}", 0, 0, 30, "#ffe066", "#3a2a00", 4, lang="en", anchor="l"); c.restore()
    c.restore(); c.save(); c.translate(HUD_R, 0)
    minimap(c, 1192, 86, t, 8 * math.sin(t * 0.7))
    if clock:
        q = back(prog(t, S("save") - 0.2, S("save") + 0.3))
        c.save(); c.translate(1060, 86); c.scale(q, q); rrect(c, -78, -24, 156, 48, 14); fs(c, "#ffffff", "#ff3b6b", 4)
        draw_text(c, "9:00 PM", 0, 1, 28, "#ff3b6b", None, 0, lang="en"); c.restore()
    c.restore(); c.pop_group_to_source(); c.paint_with_alpha(alpha)

def banner(c, t, t0, text, col="#ff2fd0", sub=None, dur=2.6, y=165, size=56):
    lt = t - t0
    if lt < 0 or lt > dur: return
    q = back(prog(lt, 0, 0.35)); out = ease(prog(lt, dur - 0.35, dur))
    if q < 0.03: return
    c.save(); c.translate(640 + 1400 * out, y); c.scale(q, q)
    tw = text_surface(text, size, "#ffffff", None, 0, "en").get_width()
    poly(c, [(-tw / 2 - 60, -46), (tw / 2 + 60, -46), (tw / 2 + 36, 46), (-tw / 2 - 36, 46)]); fs(c, col, "#ffffff", 5)
    draw_text(c, text, 0, -2, size, "#ffffff", dark(col, 0.5), 6, lang="en")
    if sub:
        sw = text_surface(sub, 30, "#ffffff", None, 0, "en").get_width()
        rrect(c, -sw / 2 - 20, 50, sw + 40, 46, 14); fs(c, (1, 1, 1, 0.95), hexc(col), 3)
        draw_text(c, sub, 0, 73, 30, dark(col, 0.45), None, 0, lang="en")
    for k in range(8):   # sparkles
        a = k * PI / 4 + lt * 2; rr = tw / 2 + 90 + 10 * math.sin(lt * 9 + k)
        ell(c, rr * math.cos(a) * 0.9, 40 * math.sin(a), 5, 5); setc(c, (1, 1, 0.6, 0.9 * (1 - out))); c.fill()
    c.restore()

def popup(c, t, t0, text, x, y, col="#ffe066"):
    q = prog(t, t0, t0 + 0.8)
    if 0 < q < 1: draw_text(c, text, x, y - 60 * q, 34, col, "#3a2a00", 5, lang="en", alpha=1 - q * q)

# ---------------------------------------------------------------- room props
TVX, TVY = 830, 335            # screen centre
def portal(c, x, y, R, t, a=1.0):
    cols = ["#ff2fd0", "#6b5cff", "#2fd0ff", "#ffe066"]
    c.save(); c.translate(x, y)
    for k in range(10):
        rr = R * (1 - k / 10)
        c.save(); c.rotate(t * (3 + k * 0.6) * (1 if k % 2 else -1))
        c.arc(0, 0, rr, 0, PI * 1.4); setc(c, (*hexc(cols[k % 4])[:3], 0.85 * a)); c.set_line_width(max(2, R / 14)); c.stroke(); c.restore()
    g = cairo.RadialGradient(0, 0, 0, 0, 0, R * 0.5); g.add_color_stop_rgba(0, 1, 1, 1, a); g.add_color_stop_rgba(1, 1, 1, 1, 0)
    c.set_source(g); c.arc(0, 0, R * 0.5, 0, 2 * PI); c.fill()
    c.restore()

def mini_city(c, x, y, w, h, t):
    c.save(); rrect(c, x, y, w, h, 6); c.clip()
    c.set_source(lin(c, 0, y, 0, y + h, [(0, "#6b5cff"), (0.6, "#ff7ac8"), (1, "#ffb36b")])); c.paint()
    ell(c, x + w * 0.72, y + h * 0.62, 34, 34); setc(c, "#fff36b"); c.fill()
    for k, (dx, bw, bh, col) in enumerate(((0.05, 0.14, 0.4, "#ff9fcf"), (0.22, 0.12, 0.3, "#7fe0ff"), (0.38, 0.16, 0.5, "#ffe066"), (0.6, 0.12, 0.34, "#b99bff"), (0.8, 0.16, 0.44, "#8cf0b0"))):
        rrect(c, x + dx * w, y + h * (0.86 - bh), bw * w, bh * h + 10, 3); fs(c, col, dark(col, 0.6), 1.5)
    c.rectangle(x, y + h * 0.84, w, h * 0.16); setc(c, "#5a4a8a"); c.fill()
    c.restore()

def tv(c, t, glow=0.0):
    rrect(c, 650, 440, 360, 80, 10); c.set_source(lin(c, 0, 440, 0, 520, [(0, "#c98a50"), (1, "#8a5a2b")])); c.fill_preserve(); setc(c, "#5a3414"); c.set_line_width(3); c.stroke()
    for k in range(2): rrect(c, 668 + k * 170, 456, 154, 50, 6); fs(c, "#b97a45", "#5a3414", 2); ell(c, 745 + k * 170, 481, 5, 5); setc(c, "#ffd23f"); c.fill()
    rrect(c, 770, 418, 120, 24, 6); fs(c, "#3a3f5a", "#1a1f2a", 2)                # console
    ell(c, 790, 430, 4, 4); setc(c, (0.3, 1, 0.5, 1) if t > T_START else (1, 0.3, 0.3, 1)); c.fill()
    rrect(c, 815, 404, 30, 16, 4); fs(c, "#3a3f5a")
    rrect(c, 660, 220, 340, 196, 16); fs(c, "#2b2d42", "#11121c", 4)
    sx, sy, sw, sh = 678, 236, 304, 164
    mini_city(c, sx, sy, sw, sh, t)
    rrect(c, sx + 22, sy + 12, sw - 44, 64, 12); fs(c, (0.15, 0.1, 0.3, 0.75), (1, 0.4, 0.8, 1), 2.5)
    draw_text(c, "GRAND TINKU", 830, sy + 32, 26, "#ffe066", "#7a1f5a", 4, lang="en")
    draw_text(c, "ADVENTURE", 830, sy + 60, 22, "#ffffff", "#7a1f5a", 3, lang="en")
    if t < T_START and (t * 1.6) % 1 < 0.65: draw_text(c, "PRESS START", 830, sy + 138, 22, "#ffffff", "#2b2d42", 4, lang="en")
    if glow > 0:
        c.save(); rrect(c, sx, sy, sw, sh, 6); c.clip(); setc(c, (1, 1, 1, 0.5 * glow)); c.paint(); c.restore()
        g = cairo.RadialGradient(TVX, TVY, 40, TVX, TVY, 420); g.add_color_stop_rgba(0, 0.9, 0.6, 1, 0.45 * glow); g.add_color_stop_rgba(1, 0.9, 0.6, 1, 0); c.set_source(g); c.paint()
    rrect(c, 820, 416, 20, 6, 2); setc(c, "#11121c"); c.fill()

def controller(c, hands, t):
    (x0, y0), (x1, y1) = hands; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 + 4
    c.save(); c.translate(cx, cy)
    rrect(c, -40, -14, 80, 30, 14); fs(c, "#3a3f5a", "#11121c", 2.5)
    for dx, col in ((18, "#ff3b6b"), (28, "#2fbf4a")): ell(c, dx, -2 + (dx - 18), 5, 5); setc(c, col); c.fill()
    rrect(c, -28, -4, 16, 6, 2); setc(c, "#c0c4d8"); c.fill(); rrect(c, -23, -9, 6, 16, 2); c.fill()
    c.restore()

# ---------------------------------------------------------------- props for the boss level
def sandcastle(c, x, y, s, t, smash=0.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    sand, sd = "#f2c879", "#c8963f"
    ell(c, 0, 0, 170, 22); setc(c, (0.6, 0.4, 0.1, 0.18)); c.fill()
    rrect(c, -130, -110, 260, 112, 8); c.set_source(lin(c, 0, -110, 0, 0, [(0, light(sand, 0.15)), (1, sand)])); c.fill_preserve(); setc(c, sd); c.set_line_width(3); c.stroke()
    for k in range(6): rrect(c, -130 + k * 46, -128, 30, 22, 3); fs(c, sand, sd, 2.5)
    for tx in (-110, 110):   # towers
        rrect(c, tx - 36, -200, 72, 200, 8); c.set_source(lin(c, tx - 36, 0, tx + 36, 0, [(0, light(sand, 0.2)), (1, dark(sand, 0.9))])); c.fill_preserve(); setc(c, sd); c.stroke()
        for k in range(3): rrect(c, tx - 36 + k * 27, -218, 18, 20, 3); fs(c, sand, sd, 2.5)
        c.move_to(tx, -218); c.line_to(tx, -270); setc(c, "#7a5a3a"); c.set_line_width(3); c.stroke()
        poly(c, [(tx, -270), (tx + 36 + 4 * math.sin(t * 6 + tx), -258), (tx, -246)]); setc(c, "#ff3b6b"); c.fill()
        ell(c, tx, -140, 10, 14); setc(c, dark(sand, 0.6)); c.fill()
    c.move_to(-30, 2); c.line_to(-30, -50); c.arc(0, -50, 30, PI, 2 * PI); c.line_to(30, 2); c.close_path(); setc(c, dark(sand, 0.62)); c.fill()
    for k in range(9):
        ell(c, -120 + k * 30, -30 - (k % 3) * 22, 4, 3); setc(c, (0.6, 0.4, 0.15, 0.4)); c.fill()
    for k, (sx_, sy_) in enumerate(((-150, -6), (140, -4), (60, 4))):   # shells
        c.save(); c.translate(sx_, sy_); ell(c, 0, 0, 12, 9); fs(c, ["#ff9fcf", "#ffffff", "#ffb38a"][k], "#c87a5a", 1.5); c.restore()
    c.restore()
    if smash > 0:   # sand puff
        for k in range(10):
            a = k * 0.6; q = smash
            ell(c, x + (60 + 140 * q) * math.cos(a) * s, y - 120 * s + (40 + 80 * q) * math.sin(a) * s * 0.6, 18 * (1 - q) + 4, 14 * (1 - q) + 3)
            setc(c, (0.95, 0.8, 0.5, 0.8 * (1 - q))); c.fill()

def pigeon_king(c, x, y, t, s=1.0, mood="grumpy", flap=0.0, m=0.0, wing_up=0.0, rumble=0.0):
    """Pigeon King: a giant, round, lavender-grey pigeon with an iridescent neck and a gold crown (front view)."""
    c.save(); c.translate(x, y); c.scale(s, s)
    ell(c, 0, 4, 150, 18); setc(c, (0, 0, 0, 0.15)); c.fill()
    body, bd = "#a2a4d6", "#5e5f98"
    for sgn in (-1, 1):   # wings behind the body
        a = sgn * (0.25 + 0.9 * flap) + (-0.0 if sgn < 0 else -wing_up * 1.6)
        c.save(); c.translate(sgn * 100, -250); c.rotate(a)
        c.move_to(0, 0); c.curve_to(sgn * 90, 30, sgn * 110, 140, sgn * 50, 230); c.curve_to(sgn * 20, 170, -sgn * 10, 90, 0, 0); c.close_path()
        c.set_source(lin(c, 0, 0, 0, 230, [(0, body), (1, "#7d7fb8")])); c.fill_preserve(); setc(c, bd); c.set_line_width(4); c.stroke()
        for k, yy in enumerate((110, 150)):   # the two dark wing bars
            c.move_to(sgn * 18, yy); c.curve_to(sgn * 50, yy + 6, sgn * 80, yy - 4, sgn * 92, yy - 16); setc(c, "#3a3b6a"); c.set_line_width(9); c.stroke()
        for k in range(4):
            c.move_to(sgn * (40 + k * 12), 200 - k * 18); c.line_to(sgn * (54 + k * 12), 222 - k * 18); setc(c, (0.25, 0.25, 0.45, 0.6)); c.set_line_width(3); c.stroke()
        c.restore()
    for fx in (-55, 55):   # feet
        for a in (-0.5, 0, 0.5):
            c.save(); c.translate(fx, -8); c.rotate(a); rrect(c, -6, -2, 12, 30, 6); fs(c, "#ff7a95", "#c8405a", 2); c.restore()
    ell(c, 0, -175, 135, 160); c.set_source(lin(c, -135, 0, 135, 0, [(0, light(body, 0.1)), (1, dark(body, 0.85))])); c.fill_preserve(); setc(c, bd); c.set_line_width(4); c.stroke()
    ell(c, 0, -150, 82, 105); setc(c, (0.92, 0.92, 1, 0.75)); c.fill()
    if rumble > 0:   # tummy rumble wiggles
        for k in range(3):
            c.move_to(-50 + k * 6, -120 - k * 26)
            for j in range(6): c.rel_line_to(16, (-1) ** j * (8 + 4 * math.sin(t * 30 + k)))
            setc(c, (0.35, 0.3, 0.6, rumble)); c.set_line_width(3.5); c.stroke()
    # iridescent neck
    ell(c, 0, -282, 100, 52); c.set_source(lin(c, -100, 0, 100, 0, [(0, "#3fc89a"), (0.5, "#8a4fd8"), (1, "#3fc89a")])); c.fill()
    hy = -350 + 6 * math.sin(t * 2.2)
    ell(c, 0, hy, 88, 82); c.set_source(lin(c, 0, hy - 82, 0, hy + 82, [(0, "#b8bae6"), (1, "#9294cc")])); c.fill_preserve(); setc(c, bd); c.set_line_width(4); c.stroke()
    happy = mood == "happy"
    for sgn in (-1, 1):
        ex, ey = sgn * 36, hy - 8
        if happy:
            c.move_to(ex - 18, ey + 4); c.curve_to(ex - 8, ey - 14, ex + 8, ey - 14, ex + 18, ey + 4); setc(c, "#2b1b40"); c.set_line_width(6); c.stroke()
            ell(c, sgn * 58, hy + 26, 16, 10); setc(c, (1, 0.45, 0.6, 0.55)); c.fill()
        else:
            ell(c, ex, ey, 24, 24); fs(c, "#ff9a2a", "#a85a10", 3); ell(c, ex, ey, 12, 12); setc(c, "#1a1a2e"); c.fill()
            ell(c, ex - 4, ey - 5, 4, 4); setc(c, "#ffffff"); c.fill()
            if mood == "grumpy":
                c.move_to(ex - sgn * 22, ey - 24); c.line_to(ex + sgn * 24, ey - 40); setc(c, "#3a3b6a"); c.set_line_width(8); c.stroke()
    ell(c, 0, hy + 14, 18, 12); setc(c, "#f4f4ff"); c.fill()           # cere
    op = 6 + 16 * m
    poly(c, [(-20, hy + 22), (20, hy + 22), (0, hy + 50)]); fs(c, "#ffb03a", "#a8601a", 2.5)
    if m > 0.1:
        poly(c, [(-14, hy + 34), (14, hy + 34), (0, hy + 34 + op)]); fs(c, "#e8902a", "#a8601a", 2)
    # crown
    cy = hy - 70
    c.move_to(-60, cy + 16); c.line_to(-66, cy - 40); c.line_to(-34, cy - 10); c.line_to(0, cy - 56); c.line_to(34, cy - 10); c.line_to(66, cy - 40); c.line_to(60, cy + 16); c.close_path()
    c.set_source(lin(c, 0, cy - 56, 0, cy + 16, [(0, "#fff08a"), (1, "#e8a800")])); c.fill_preserve(); setc(c, "#a87400"); c.set_line_width(3); c.stroke()
    for jx, col in ((-36, "#ff3b6b"), (0, "#2f7bff"), (36, "#2fbf4a")): ell(c, jx, cy + 2, 8, 8); fs(c, col, "#ffffff", 1.5)
    for jx in (-66, 0, 66): ell(c, jx, cy - 44 - (12 if jx == 0 else 0), 6, 6); fs(c, "#ffffff", "#a87400", 1.5)
    c.restore()

def beak_pos(x, y, s, t): return x, y + s * (-350 + 6 * math.sin(t * 2.2) + 40)

def grain_bag(c, x, y, s=1.0, open_=False):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.move_to(-22, -10); c.curve_to(-30, 20, -24, 40, 0, 42); c.curve_to(24, 40, 30, 20, 22, -10); c.close_path(); fs(c, "#c8955a", "#7a4a24", 2.5)
    c.move_to(-22, -10); c.curve_to(-10, -18, 10, -18, 22, -10); setc(c, "#e8c08a" if open_ else "#7a4a24"); c.set_line_width(4); c.stroke()
    if open_:
        for k in range(5): ell(c, -12 + k * 6, -12, 3, 2.5); setc(c, "#ffe08a"); c.fill()
    else:
        c.move_to(-14, -14); c.curve_to(-4, -26, 4, -26, 14, -14); setc(c, "#ff3b6b"); c.set_line_width(3); c.stroke()
    c.restore()

def feather(c, x, y, a=0.0, s=1.0):
    c.save(); c.translate(x, y); c.rotate(a); c.scale(s, s)
    c.move_to(0, 0); c.curve_to(-18, -30, -14, -70, 0, -96); c.curve_to(14, -70, 18, -30, 0, 0); fs(c, "#ff7ab0", "#c8407a", 2)
    c.move_to(0, 6); c.line_to(0, -90); setc(c, "#ffffff"); c.set_line_width(2); c.stroke()
    c.restore()

def gold_key(c, x, y, t, s=1.0, tag=0.0):
    g = cairo.RadialGradient(x, y, 10, x, y, 150 * s); g.add_color_stop_rgba(0, 1, 0.95, 0.5, 0.55); g.add_color_stop_rgba(1, 1, 0.95, 0.5, 0); c.set_source(g); c.arc(x, y, 150 * s, 0, 2 * PI); c.fill()
    c.save(); c.translate(x, y); c.rotate(0.15 * math.sin(t * 2)); c.scale(s, s)
    ell(c, -50, 0, 34, 34); fs(c, "#ffd23f", "#a87400", 4); ell(c, -50, 0, 14, 14); setc(c, (1, 0.97, 0.8, 1)); c.fill()
    rrect(c, -18, -9, 100, 18, 6); fs(c, "#ffd23f", "#a87400", 3)
    rrect(c, 52, 8, 12, 22, 3); fs(c, "#ffd23f", "#a87400", 2.5); rrect(c, 70, 8, 12, 30, 3); fs(c, "#ffd23f", "#a87400", 2.5)
    for k in range(4):
        a = t * 3 + k * PI / 2; star(c, 20 + 90 * math.cos(a), 50 * math.sin(a), 8, "#fff6b0", "#ffd23f")
    c.restore()
    if tag > 0.02:
        c.save(); c.translate(x, y + 70 * s); c.scale(tag, tag)
        rrect(c, -120, -24, 240, 48, 16); fs(c, "#7b2fd6", "#ffffff", 4)
        draw_text(c, "SECRET LEVEL", 0, 1, 30, "#ffe066", None, 0, lang="en"); c.restore()

def boss_bar(c, t, alpha):
    if alpha <= 0: return
    c.push_group()
    hp = ease(prog(t, T_HAPPY + 0.4, T_HAPPY + 2.2))
    rrect(c, 430, 18, 420, 70, 18); setc(c, (0.12, 0.08, 0.28, 0.75)); c.fill()
    draw_text(c, "PIGEON KING" if hp < 0.5 else "NEW FRIEND!", 640, 38, 24, "#ffe066" if hp < 0.5 else "#ff9fcf", None, 0, lang="en")
    rrect(c, 450, 56, 380, 20, 10); setc(c, (1, 1, 1, 0.2)); c.fill()
    shake = 3 * math.sin(t * 50) if (T_FLAP1 <= t <= T_FLAP1 + 0.6 or T_FLAP2 <= t <= T_FLAP2 + 0.6) else 0
    rrect(c, 450 + shake, 56, 380, 20, 10); setc(c, (0.9, 0.15, 0.2, 1 - hp)); c.fill()
    for k in range(9):   # hearts fill the bar from the left
        q = clamp(hp * 9 - k)
        if q > 0: heart(c, 472 + k * 42, 66, 0.55 * back(q), "#ff4f8b")
    c.pop_group_to_source(); c.paint_with_alpha(alpha)

# ---------------------------------------------------------------- scenes
def sucked(c, t, x, y, fn):
    """Draw a character being pulled into the TV portal."""
    p = ease(prog(t, T_PULL + 0.9, T_CITY - 0.1))
    if p >= 0.98: return
    c.save(); px, py = lerp(x, TVX, p), lerp(y, TVY + 120, p)
    c.translate(px, py - 150); c.rotate(p * 7 + 0.15 * math.sin(t * 20) * (p > 0)); c.scale(1 - 0.85 * p, 1 - 0.85 * p); c.translate(-px, -(py - 150))
    fn(px, py); c.restore()

def scene_room(c, t):
    room_bg(c, t)
    glow = ease(prog(t, T_START, T_START + 0.6)) * (0.6 + 0.4 * math.sin(t * 10))
    tv(c, t, glow)
    if t >= T_PULL:
        R = 40 + 260 * ease(prog(t, T_PULL, T_PULL + 1.2))
        portal(c, TVX, TVY, R, t)
        for k in range(14):
            a = k * 0.45 + t; rr = 520 - ((t * 500 + k * 90) % 480)
            c.move_to(TVX + rr * math.cos(a), TVY + rr * math.sin(a) * 0.7); c.line_to(TVX + (rr - 60) * math.cos(a), TVY + (rr - 60) * math.sin(a) * 0.7)
            setc(c, (1, 1, 1, 0.5)); c.set_line_width(4); c.stroke()
    shake = 3 * math.sin(t * 40) if t >= T_PULL else 0
    pull = ease(prog(t, T_PULL, T_PULL + 0.9))
    def draw_tinku(px, py):
        a = talk("tinku", t, 0)
        if t < T_PULL and not speaking("tinku", t): a = HOLD
        if active(t, "start", 0, 0.3): a = HOLD
        if t >= T_PULL: a = ((2.3, 0.6), (2.6, 0.2))
        hands = kid("tinku", c, px + shake, py, t, a, 0.3 if t < T_PULL else 0.6, 0, 0.88, 0.25 * pull)
        if a == HOLD: controller(c, hands, t)
    def draw_pinky(px, py):
        a = talk("pinky", t, 2); hop = 0
        if active(t, "snacks", 0, 0.3): a = ((0.6, -1.4), (0.6, -1.4)); hop = abs(math.sin(t * 9)) * 8
        if active(t, "pinkyin", 0, 0.2): a = (a[0], (2.6, 0.2)); hop = abs(math.sin(t * 8)) * 10
        if t >= T_PULL: a = SCARED
        kid("pinky", c, px + shake, py, t, a, 0.2, hop, 0.88, 0.28 * pull)
    def draw_golu(px, py):
        a = talk("golu", t, 1); hop = 0
        if active(t, "hurry", 0, 0.3) or active(t, "start", 0, 0.8): hop = abs(math.sin(t * 9)) * 16
        if active(t, "bag", 0, 0.4): a = (a[0], (2.2, 0.4))
        if t >= T_PULL: a = SCARED
        hands = kid("golu", c, px + shake, py, t, a, 0.4, hop, 0.88, 0.3 * pull)
        if t < T_PULL: grain_bag(c, hands[1][0], hands[1][1] + 26, 0.9)
    for x, fn in ((250, draw_tinku), (445, draw_pinky), (625, draw_golu)):
        sucked(c, t, x, GY, fn) if t >= T_PULL else fn(x, GY)

KX = 1010            # Pigeon King position
def scene_arena(c, t):
    city_bg(c, t, 1300)
    c.set_source(lin(c, 0, 520, 0, 720, [(0, "#ffe6a8"), (1, "#f2c070")])); c.rectangle(0, 520, W, 200); c.fill()     # beach sand
    for k in range(14):
        x = (k * 97) % W; y = 560 + (k * 53) % 140; ell(c, x, y, 6, 3); setc(c, (0.8, 0.6, 0.3, 0.35)); c.fill()
    c.move_to(0, 524)
    for k in range(33): c.line_to(k * 40, 524 + 6 * math.sin(t * 2 + k))
    c.line_to(W, 516); c.line_to(0, 516); c.close_path(); setc(c, (1, 1, 1, 0.75)); c.fill()   # foam edge
    for k in range(9):   # bunting
        x0 = 140 + k * 110; c.move_to(x0, 236 + 10 * math.sin(k)); poly(c, [(x0, 236), (x0 + 40, 236), (x0 + 20, 270 + 4 * math.sin(t * 3 + k))])
        setc(c, ["#ff3b6b", "#ffd23f", "#2f7bff", "#2fbf4a"][k % 4]); c.fill()
    # Pigeon King
    rise = ease(prog(t, T_RISE, T_RISE + 1.0))
    happy = t >= T_HAPPY
    mood = "happy" if happy else ("grumpy" if t < S("rumble") else "plain")
    flap = 0.0
    for tf in (T_FLAP1, T_FLAP2):
        if tf <= t <= tf + 1.6: flap = abs(math.sin((t - tf) * 9)) * (1 - prog(t, tf + 1.0, tf + 1.6))
    if happy and t < T_HAPPY + 1.8: flap = 0.4 * abs(math.sin((t - T_HAPPY) * 8))
    ks = 1.0 - 0.18 * ease(prog(t, T_HAPPY + 0.2, T_HAPPY + 1.4))
    wing_up = ease(prog(t, S("highfive") + 0.4, S("highfive") + 0.8)) * (1 - ease(prog(t, E("highfive") + 0.6, E("highfive") + 1.0)))
    rum = 1.0 if active(t, "rumble", 0.6, 0.3) or active(t, "tummy", 0, 0.3) else 0
    if rise > 0:
        bob = 10 * abs(math.sin(t * 6)) if happy else 0
        pigeon_king(c, KX, GY + 20 + (1 - rise) * 380 - bob, t, ks, mood, flap, mo("pigeon", t), wing_up, rum)
    sandcastle(c, KX, GY + 50, 0.85, t)
    # gusts of wind
    for tf in (T_FLAP1, T_FLAP2):
        q = prog(t, tf, tf + 1.4)
        if 0 < q < 1:
            for k in range(7):
                x = KX - 160 - 700 * ((q * 1.6 + k / 7) % 1); y = 330 + k * 36
                c.move_to(x, y); c.curve_to(x - 40, y - 14, x - 80, y + 14, x - 130, y); setc(c, (1, 1, 1, 0.7 * (1 - q))); c.set_line_width(5); c.stroke()
    # small sandcastle Tinku crashes into
    smash = prog(t, T_FLAP1 + 1.3, T_FLAP1 + 2.2)
    stuck = T_FLAP1 + 1.3 <= t < T_TOUT
    # --- Tinku
    tx, ty, trot = 600, GY, 0.0
    a = talk("tinku", t, 0); hop = 0.0; look = 0.4
    walk = prog(t, T_TWALK, T_TWALK + 1.2)
    if T_TWALK <= t < T_FLAP1 + 0.3: tx = lerp(600, 820, ease(walk)); hop = abs(math.sin(t * 10)) * 10 * (walk < 1); a = HIPS if walk >= 1 else a
    if T_FLAP1 + 0.3 <= t < T_FLAP1 + 1.3:
        q = prog(t, T_FLAP1 + 0.3, T_FLAP1 + 1.3); tx = lerp(820, 745, q); ty = GY - 260 * math.sin(PI * q) - 40 * q; trot = -q * 2 * PI - PI * q; a = ((2.4, 0.4), (2.4, 0.4))
    if t >= T_TOUT:
        q = prog(t, T_TOUT, T_TOUT + 0.8); tx = lerp(745, 600, ease(q)); hop = 120 * math.sin(PI * q) if q < 1 else 0
    if active(t, "won", 0, 0.5) or active(t, "secret", 0, 0.3): a = (a[0], (2.4, 0.3))
    if T_PWALK <= t < T_HAPPY and t >= T_TOUT + 0.8 and not speaking("tinku", t): a = ((0.6, -1.4), (0.6, -1.4)) if active(t, "sand", 0, 0) else a
    # --- Pinky
    px_, prot = 410, 0.0
    pa = talk("pinky", t, 2); phop = 0.0; plook = 0.4
    pw = prog(t, T_PWALK, T_PWALK + 1.2)
    if active(t, "sand", 0, 0.4): pa = ((0.6, -1.4), (0.6, -1.4)); phop = abs(math.sin(t * 10)) * 10
    if T_PWALK <= t < T_FLAP2 + 0.3: px_ = lerp(410, 820, ease(pw)); phop = abs(math.sin(t * 10)) * 10 * (pw < 1); pa = (pa[0], (1.9, 0.5))
    if T_FLAP2 + 0.3 <= t < T_FLAP2 + 1.8:
        q = prog(t, T_FLAP2 + 0.3, T_FLAP2 + 1.8); px_ = lerp(820, 410, ease(q)); phop = 90 * math.sin(PI * q); prot = -2 * PI * ease(q); pa = ((2.4, 0.4), (2.4, 0.4))
    if active(t, "hearts", 0, 0.5) or active(t, "key", 0, 0.5): pa = (pa[0], (2.6, 0.1))
    # --- Golu
    gx = 230; ga = talk("golu", t, 1); ghop = 0.0; glook = 0.4
    gw = prog(t, T_GWALK, T_GWALK + 1.6)
    if t >= T_GWALK: gx = lerp(230, 790, ease(gw)); ghop = abs(math.sin(t * 10)) * 10 * (0 < gw < 1)
    if t >= E("save") - 1.0: gx = lerp(790, 640, ease(prog(t, E("save") - 1.0, E("save"))))
    if active(t, "giant", 0, 0.5) or active(t, "grumpy", 0, 0.3): ga = SCARED
    if active(t, "share", 0.2, 1.8): ga = (ga[0], (1.5, 0.3))
    if active(t, "highfive", 0, 1.0): ga = (ga[0], (2.8, 0.1)); ghop = abs(math.sin(t * 8)) * 10
    if active(t, "now", 0, 0.3): ghop = abs(math.sin(t * 9)) * 14
    # draw back-to-front
    if stuck or t < T_FLAP1 + 1.3 and t >= T_FLAP1 + 0.3 and False: pass
    if stuck:   # upside-down Tinku, legs kicking out of the small castle
        c.save(); c.translate(745, GY - 90); c.rotate(PI + 0.12 * math.sin(t * 12)); c.translate(-745, -(GY - 90))
        kid("tinku", c, 745, GY - 90, t, ((0.3, 0.2), (0.3, 0.2)), 0, 0, 0.85); c.restore()
    sandcastle(c, 745, GY + 60, 0.62, t, smash if smash < 1 else 0)
    if stuck and t > T_FLAP1 + 1.4:
        for k in range(5):   # sand bits
            q = ((t * 1.3 + k / 5) % 1); ell(c, 745 - 80 + k * 40, GY - 60 - 40 * q, 5, 4); setc(c, (0.9, 0.75, 0.45, 1 - q)); c.fill()
    hands_p = None
    for name in ("golu", "pinky", "tinku"):
        if name == "tinku" and not stuck:
            c.save(); c.translate(tx, ty - 150); c.rotate(trot); c.translate(-tx, -(ty - 150))
            kid("tinku", c, tx, ty, t, a, look, hop); c.restore()
        if name == "pinky":
            c.save(); c.translate(px_, GY - 150); c.rotate(prot); c.translate(-px_, -(GY - 150))
            hands_p = kid("pinky", c, px_, GY, t, pa, plook, phop); c.restore()
            if T_PWALK - 1.2 <= t < T_FLAP2 + 0.3 or active(t, "tickle", 0, 0):
                feather(c, hands_p[1][0], hands_p[1][1] + 10, 0.4 + 0.5 * math.sin(t * 14) * (t >= T_PWALK + 1.2), 0.9)
        if name == "golu":
            hg = kid("golu", c, gx, GY, t, ga, glook, ghop)
            if t >= T_CITY and t < T_GRAINS + 3.0: grain_bag(c, hg[1][0], hg[1][1] + 26, 0.9, open_=t >= T_GRAINS - 0.3)
            gbag = hg[1]
    # grains flying into the beak
    if T_GRAINS <= t <= T_GRAINS + 2.6:
        bx, by = beak_pos(KX, GY + 20, ks, t)
        for k in range(16):
            q = ((t - T_GRAINS) * 1.4 + k / 16) % 1
            if t - T_GRAINS < k / 16 / 1.4: continue
            x = lerp(gbag[0], bx, q); y = lerp(gbag[1] + 10, by, q) - 110 * math.sin(PI * q)
            ell(c, x, y, 5, 4); fs(c, "#ffe08a", "#a8802a", 1.2)
    if T_HAPPY <= t <= T_HAPPY + 3:
        for k in range(5):
            q = prog(t, T_HAPPY + 0.25 * k, T_HAPPY + 0.25 * k + 1.4)
            if 0 < q < 1: heart(c, KX - 80 + 40 * k, GY - 380 - 120 * q, 1.4, "#ff4f8b", 1 - q)
    if active(t, "highfive", 0, 1.0) and prog(t, S("highfive") + 0.6, S("highfive") + 1.2) > 0:
        q = prog(t, S("highfive") + 0.6, S("highfive") + 1.4)
        if q < 1:
            for k in range(8): a_ = k * PI / 4; star(c, 880 + 70 * q * math.cos(a_), 300 + 70 * q * math.sin(a_), 12 * (1 - q) + 3)
    # golden key
    if t >= T_KEY:
        q = ease(prog(t, T_KEY, T_KEY + 1.6)); bx, by = beak_pos(KX, GY + 20, ks, t)
        kx_, ky_ = lerp(bx, 330, q), lerp(by, 200, q) - 120 * math.sin(PI * q) + 8 * math.sin(t * 2.5)
        if t < T_SAVE + 1.2: gold_key(c, kx_, ky_, t, 0.4 + 0.6 * q, back(prog(t, S("secret") - 0.1, S("secret") + 0.3)))
    banner(c, t, T_CITY + 2.4, "BOSS LEVEL", "#e8202a", "Meet the Pigeon King!", 3.2)
    banner(c, t, T_HAPPY + 0.6, "YOU WIN!", "#2fbf4a", "Boss became your friend! +500", 3.6)
    if t >= T_SAVE:
        q = prog(t, T_SAVE, T_SAVE + 1.8)
        rrect(c, 440, 130, 400, 110, 20); fs(c, (0.12, 0.08, 0.28, 0.9), (1, 1, 1, 1), 4)
        draw_text(c, "SAVING" + "." * (1 + int(t * 4) % 3), 640, 165, 34, "#ffffff", None, 0, lang="en")
        rrect(c, 470, 192, 340, 26, 13); setc(c, (1, 1, 1, 0.25)); c.fill(); rrect(c, 470, 192, max(26, 340 * q), 26, 13); setc(c, "#2fbf4a"); c.fill()
        if q >= 1:
            R = 60 + 900 * ease(prog(t, T_SAVE + 1.8, T_BACK + 0.2)); portal(c, 640, 360, R, t)

def scene_back(c, t):
    room_bg(c, t); tv(c, t, 0.4 * (1 - prog(t, T_BACK, T_BACK + 2.0)))
    for i, (n, x) in enumerate((("tinku", 290), ("pinky", 490), ("golu", 690))):
        t0 = T_BACK + 0.3 + i * 0.25; p = prog(t, t0, t0 + 0.7)
        px = lerp(TVX, x, p); py = lerp(TVY + 60, GY, p) - 160 * math.sin(PI * p)
        a = talk(n, t, i); hop = 0.0; look = 0.0
        if p < 1: a = CHEER
        if n == "tinku" and active(t, "next", 0, 0.5): a = (a[0], (2.4, 0.3))
        if n == "golu" and active(t, "empty", 0, 0.5): a = ((1.2, -1.6), (1.2, -1.6))
        if active(t, "bye1", 0, 4) or active(t, "bye2", 0, 3): a = (a[0], (2.1, 0.5 + 0.5 * math.sin(t * 11 + i))); hop = abs(math.sin(t * 5 + i)) * 10
        if t >= t0:
            c.save(); c.translate(px, py - 150); c.rotate((1 - p) * 4); c.translate(-px, -(py - 150)); kid(n, c, px, py, t, a, look, hop); c.restore()
            if p >= 1 and t < t0 + 2.2:
                for k in range(3):
                    a_ = t * 4 + k * 2.1; star(c, x + 70 * math.cos(a_), GY - 330 + 18 * math.sin(a_), 14)

def outro_card(c, t):
    lt = t - T_OUTRO
    gr = cairo.RadialGradient(640, 380, 40, 640, 380, 900); gr.add_color_stop_rgba(0, *hexc("#fff3c4")); gr.add_color_stop_rgba(1, *hexc("#c9a8ff")); c.set_source(gr); c.paint()
    r = random.Random(5); cols = ["#ff3b3b", "#ff8c1a", "#ffd21a", "#2fbf4a", "#2f8bff", "#9b3fd6"]
    for k in range(50):
        x0 = r.uniform(0, W); sp = r.uniform(60, 130); ph = r.uniform(0, 800)
        y = (ph + lt * sp) % 800 - 40; x = x0 + 20 * math.sin(lt * 2 + k)
        if k % 3 == 0: coin(c, x, y, t, 0.8, k)
        else: c.save(); c.translate(x, y); c.rotate(lt * 2 + k); rrect(c, -6, -3, 12, 6, 2); setc(c, cols[k % 6]); c.fill(); c.restore()
    p = back(prog(lt, 0.1, 0.6))
    if p > 0.02: c.save(); c.translate(640, 140); c.scale(p, p); draw_text(c, "Bye-bye!", 0, 0, 130, "#7b2fd6", "#ffffff", 12, lang="en"); c.restore()
    p2 = back(prog(lt, 0.5, 1.0))
    if p2 > 0.02:
        c.save(); c.translate(640, 262); c.scale(p2, p2); draw_text(c, "See you next time!", 0, 0, 46, "#7c2d12", "#ffffff", 5, lang="en")
        draw_text(c, NEXT, 0, 58, 36, "#e8202a", "#ffffff", 4, lang="en"); c.restore()
    for i, (fn, x) in enumerate(((tinku, 360), (pinky, 560), (golu, 750))):
        fn(c, x, 680, t, 0.8, ((0.15, 0.3), (2.1, 0.5 + 0.5 * math.sin(t * 10 + i))), 0, 0, blink(t, i), abs(math.sin(t * 5 + i)) * 12)
    pigeon_king(c, 960, 680, t, 0.45, "happy", 0.3 * abs(math.sin(t * 6)))

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

SCENES = [(0.0, scene_room), (T_CITY, scene_arena), (T_BACK, scene_back), (T_OUTRO, lambda c, t: outro_card(c, t))]
WIPE = {T_OUTRO}
FLASH = {T_CITY, T_BACK}

def frame(t, surf=None, with_captions=True):
    surf = surf or cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(surf)
    idx = max(i for i, (t0, _) in enumerate(SCENES) if t >= t0)
    t0, fn = SCENES[idx]
    z = 1.0 + 0.04 * ease(prog(t, t0, t0 + 12)) if fn is not SCENES[-1][1] else 1.0
    if T_PULL <= t < T_CITY: z += 0.12 * ease(prog(t, T_PULL, T_CITY))          # camera dives toward the TV
    sh = 0
    for ts_ in (T_RISE + 0.9, T_FLAP1 + 1.3, T_FLAP2):
        if ts_ <= t <= ts_ + 0.6: sh = 8 * (1 - prog(t, ts_, ts_ + 0.6))
    if T_BACK + 0.9 <= t <= T_BACK + 1.4: sh = 8 * (1 - prog(t, T_BACK + 0.9, T_BACK + 1.4))
    cy = 420 if not (T_PULL <= t < T_CITY) else lerp(420, TVY, ease(prog(t, T_PULL, T_CITY)))
    cx = 640 if not (T_PULL <= t < T_CITY) else lerp(640, TVX, ease(prog(t, T_PULL, T_CITY)))
    c.save(); c.translate(cx + sh * math.sin(t * 60), cy + sh * math.cos(t * 47)); c.scale(z, z); c.translate(-cx, -cy)
    p = ease(prog(t, t0, t0 + 0.8)) if t0 in WIPE and idx > 0 else 1.0
    if p < 1:
        SCENES[idx - 1][1](c, t); c.save(); c.arc(640, 360, 780 * p, 0, 2 * PI); c.clip(); fn(c, t); c.restore()
        c.arc(640, 360, 780 * p, 0, 2 * PI); setc(c, "#ffd23f"); c.set_line_width(12); c.stroke()
    else:
        fn(c, t)
    c.restore()
    if T_CITY <= t < T_BACK:
        ha = ease(prog(t, T_CITY + 1.2, T_CITY + 1.8)) * (1 - prog(t, T_BACK - 0.6, T_BACK))
        hud(c, t, ha, clock=t >= S("save") - 0.2)
        boss_bar(c, t, ha * ease(prog(t, T_RISE + 0.6, T_RISE + 1.2)))
    for tf in FLASH:   # white flash through the portal
        if tf - 0.5 <= t < tf + 0.6:
            k = 1 - abs(t - tf) / (0.5 if t < tf else 0.6)
            c.rectangle(0, 0, W, H); setc(c, (1, 1, 1, clamp(k))); c.fill()
    if with_captions: captions(c, t)
    f = clamp(min(t / 0.25, (DURATION - t) / 1.5))
    if f < 1: c.rectangle(0, 0, W, H); setc(c, (0, 0, 0, 1 - f)); c.fill()
    return surf

if __name__ == "__main__":
    os.makedirs("stills", exist_ok=True)
    for ts in sys.argv[1:]: frame(float(ts)).write_to_png(f"stills/f_{float(ts):06.2f}.png")
