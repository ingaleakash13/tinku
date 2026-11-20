"""Story: Pinky and the Secret Level. Starts straight in the story (no title card, no brand text).
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
def coins_at(t): return 990 + (1000 if t >= S("complete") + 0.2 else 0)
def last_coin_change(t): return S("complete") + 0.2 if t >= S("complete") + 0.2 else -9

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

# ---------------------------------------------------------------- props for the secret level
RAINBOW = ["#ff3b3b", "#ff8c1a", "#ffd21a", "#2fbf4a", "#2f8bff", "#4b3fc8", "#a04dff"]
TILE_ORDER = [2, 4, 0, 6, 3, 1, 5]          # colour index on each of the 7 tiles (left to right): yellow, blue, red, violet, green, orange, indigo
def tile_x(k): return 60 + k * 68
def tile_of(color): return TILE_ORDER.index(color)

def gold_key(c, x, y, t, s=1.0, glow=True):
    if glow:
        g = cairo.RadialGradient(x, y, 10, x, y, 150 * s); g.add_color_stop_rgba(0, 1, 0.95, 0.5, 0.5); g.add_color_stop_rgba(1, 1, 0.95, 0.5, 0); c.set_source(g); c.arc(x, y, 150 * s, 0, 2 * PI); c.fill()
    c.save(); c.translate(x, y); c.rotate(0.15 * math.sin(t * 2)); c.scale(s, s)
    ell(c, -50, 0, 34, 34); fs(c, "#ffd23f", "#a87400", 4); ell(c, -50, 0, 14, 14); setc(c, (1, 0.97, 0.8, 1)); c.fill()
    rrect(c, -18, -9, 100, 18, 6); fs(c, "#ffd23f", "#a87400", 3)
    rrect(c, 52, 8, 12, 22, 3); fs(c, "#ffd23f", "#a87400", 2.5); rrect(c, 70, 8, 12, 30, 3); fs(c, "#ffd23f", "#a87400", 2.5)
    c.restore()

def sky_bg(c, t):
    c.set_source(lin(c, 0, 0, 0, 720, [(0, "#6fc8ff"), (0.5, "#bfe8ff"), (0.85, "#ffd6f0"), (1, "#ffe9c8")])); c.paint()
    g = cairo.RadialGradient(1100, 110, 30, 1100, 110, 500); g.add_color_stop_rgba(0, 1, 1, 0.85, 0.8); g.add_color_stop_rgba(1, 1, 1, 0.85, 0); c.set_source(g); c.paint()
    ell(c, 1100, 110, 56, 56); setc(c, "#fff6b0"); c.fill()
    c.save(); c.translate(1100, 110); c.rotate(t * 0.05)
    for i in range(12):
        c.save(); c.rotate(i * PI / 6); c.move_to(0, 0); c.line_to(1400, -50); c.line_to(1400, 50); c.close_path(); setc(c, (1, 1, 0.9, 0.06)); c.fill(); c.restore()
    c.restore()
    r = random.Random(8)
    for i in range(5): cloud(c, (r.uniform(0, 1500) + t * r.uniform(4, 9)) % 1600 - 200, r.uniform(40, 220), r.uniform(0.6, 1.1), 0.9)
    for k, (x, y, s) in enumerate(((240, 250, 0.35), (1180, 330, 0.3), (700, 200, 0.22))):   # distant floating islets
        yy = y + 8 * math.sin(t * 0.9 + k)
        poly(c, [(x - 90 * s * 3, yy), (x + 90 * s * 3, yy), (x + 30 * s * 3, yy + 140 * s * 3), (x, yy + 200 * s * 3), (x - 40 * s * 3, yy + 130 * s * 3)])
        c.set_source(lin(c, 0, yy, 0, yy + 200 * s * 3, [(0, "#c89a6a"), (1, "#8a6a8a")])); c.fill()
        ell(c, x, yy, 92 * s * 3, 14 * s * 3); setc(c, "#7fd06a"); c.fill()
    for k in range(4):   # birds
        x = (k * 300 + t * 40) % 1500 - 100; y = 150 + 40 * math.sin(k * 2 + t * 0.5); w = 12 + 4 * math.sin(t * 8 + k)
        c.move_to(x - 14, y - w * 0.4); c.curve_to(x - 6, y - w, x - 2, y - 4, x, y); c.curve_to(x + 2, y - 4, x + 6, y - w, x + 14, y - w * 0.4)
        setc(c, (0.3, 0.3, 0.5, 0.7)); c.set_line_width(2.5); c.stroke()

def island(c, x0, x1, top, t, seed=1):
    r = random.Random(seed); w = x1 - x0
    pts = [(x0, top + 10)]
    for k in range(9):
        fx = x0 + w * (k + 0.5) / 9; pts.append((fx, top + 60 + 110 * math.sin(PI * (k + 0.5) / 9) * r.uniform(0.8, 1.3) + (60 if k % 3 == 1 else 0)))
    pts.append((x1, top + 10))
    poly(c, pts); c.set_source(lin(c, 0, top, 0, top + 240, [(0, "#c8925a"), (0.6, "#9a6a4a"), (1, "#7a5a8a")])); c.fill_preserve(); setc(c, "#6a4a2a"); c.set_line_width(3); c.stroke()
    for k in range(6):
        sx = x0 + w * r.uniform(0.1, 0.9); sy = top + r.uniform(40, 120); ell(c, sx, sy, r.uniform(14, 26), r.uniform(8, 14)); setc(c, (0.45, 0.3, 0.2, 0.35)); c.fill()
    for k in range(4):   # hanging vines
        vx = x0 + w * (0.15 + 0.22 * k); c.move_to(vx, top + 20); c.curve_to(vx + 8 * math.sin(t + k), top + 70, vx - 6, top + 110, vx + 4 * math.sin(t * 1.3 + k), top + 140 + 20 * (k % 2))
        setc(c, "#3f9e3f"); c.set_line_width(4); c.stroke()
    rrect(c, x0 - 6, top - 6, w + 12, 30, 14); c.set_source(lin(c, 0, top - 6, 0, top + 24, [(0, "#8ddc62"), (1, "#4fae44")])); c.fill_preserve(); setc(c, "#3a8a3a"); c.set_line_width(3); c.stroke()
    for k in range(int(w / 40)):
        fx = x0 + 20 + k * 40 + r.uniform(-8, 8); col = r.choice(["#ff5f8f", "#ffb000", "#a04dff", "#ffffff"])
        for a in range(5): ell(c, fx + 4 * math.cos(a * 1.256), top - 2 + 4 * math.sin(a * 1.256), 3.5, 3.5); setc(c, col); c.fill()

def cloud_sea(c, t):
    for row, (y, a) in enumerate(((650, 0.9), (690, 1.0))):
        for k in range(9):
            x = (k * 170 + t * (6 + row * 4)) % 1500 - 120
            for dx, dy, rr in ((0, 0, 50), (40, -16, 56), (90, 0, 46)): ell(c, x + dx, y + dy, rr, rr * 0.7); setc(c, (1, 1, 1, a)); c.fill()

def tiles(c, t, lit_count, moti_on):
    for k in range(7):
        col = RAINBOW[TILE_ORDER[k]]; x = tile_x(k); y = 600
        on = TILE_ORDER[k] < lit_count
        poly(c, [(x - 30, y + 30), (x + 34, y + 30), (x + 28, y), (x - 24, y)]); fs(c, light(col, 0.25) if on else col, dark(col, 0.6), 3)
        if on:
            g = cairo.RadialGradient(x, y + 15, 2, x, y + 15, 60); g.add_color_stop_rgba(0, *hexc(col, 0.6)); g.add_color_stop_rgba(1, *hexc(col, 0)); c.set_source(g); c.arc(x, y + 15, 60, 0, 2 * PI); c.fill()
        if moti_on and TILE_ORDER[k] == 3:
            c.move_to(x - 14, y + 4); c.line_to(x + 14, y + 26); c.move_to(x + 14, y + 4); c.line_to(x - 14, y + 26); setc(c, (1, 1, 1, 0.5 + 0.5 * math.sin(t * 20))); c.set_line_width(6); c.stroke()

BCX, BCY = 730, 700          # rainbow bridge centre
def bridge(c, t, n):
    for k in range(n):
        q = back(prog(t, HOPS[k], HOPS[k] + 0.4))
        if q <= 0.02: continue
        R = 250 - k * 13
        c.save(); c.translate(BCX, BCY); c.scale(1, q)
        c.arc(0, 0, R, PI, 2 * PI); c.arc_negative(0, 0, R - 13, 2 * PI, PI); c.close_path(); setc(c, RAINBOW[k]); c.fill(); c.restore()
    if n == 7:
        c.arc(BCX, BCY, 250, PI, 2 * PI); setc(c, (1, 1, 1, 0.7)); c.set_line_width(3); c.stroke()
        for k in range(6):
            a = PI + PI * ((t * 0.2 + k / 6) % 1); star(c, BCX + 220 * math.cos(a), BCY + 220 * math.sin(a), 7, "#ffffff", "#ffe066")

def on_bridge_y(x):
    d = abs(x - BCX)
    if d < 215: return BCY - math.sqrt(215 ** 2 - d ** 2) + 6
    return GY

def chest(c, x, y, t, open_=0.0):
    c.save(); c.translate(x, y)
    ell(c, 0, 4, 130, 16); setc(c, (0, 0, 0, 0.18)); c.fill()
    if open_ > 0:
        g = cairo.RadialGradient(0, -130, 10, 0, -130, 260); g.add_color_stop_rgba(0, 1, 0.95, 0.5, 0.8 * open_); g.add_color_stop_rgba(1, 1, 0.95, 0.5, 0); c.set_source(g); c.arc(0, -130, 260, 0, 2 * PI); c.fill()
        for k in range(10):
            c.save(); c.translate(0, -120); c.rotate(-PI / 2 + (k - 4.5) * 0.18 + 0.05 * math.sin(t * 3 + k))
            c.move_to(0, -6); c.line_to(260 * open_, -18); c.line_to(260 * open_, 18); c.line_to(0, 6); c.close_path(); setc(c, (1, 0.95, 0.6, 0.35)); c.fill(); c.restore()
    rrect(c, -110, -120, 220, 120, 12); c.set_source(lin(c, 0, -120, 0, 0, [(0, "#c8803a"), (1, "#8a4a1a")])); c.fill_preserve(); setc(c, "#5a2a0a"); c.set_line_width(4); c.stroke()
    for bx in (-80, 80): rrect(c, bx - 10, -120, 20, 120, 4); fs(c, "#ffd23f", "#a87400", 2.5)
    rrect(c, -22, -96, 44, 40, 6); fs(c, "#ffd23f", "#a87400", 2.5); ell(c, 0, -80, 6, 8); setc(c, "#5a2a0a"); c.fill()
    c.save(); c.translate(0, -120); c.scale(1, 1 - 1.8 * open_)       # lid flips up
    c.move_to(-110, 0); c.curve_to(-110, -70, 110, -70, 110, 0); c.close_path(); c.set_source(lin(c, 0, -60, 0, 0, [(0, "#d8904a"), (1, "#9a5a2a")])); c.fill_preserve(); setc(c, "#5a2a0a"); c.set_line_width(4); c.stroke()
    for bx in (-80, 80): c.move_to(bx, 0); c.line_to(bx, -48); setc(c, "#ffd23f"); c.set_line_width(18); c.stroke()
    c.restore(); c.restore()

def trophy(c, x, y, s=1.0, t=0.0, plaque=True):
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, -60, -40, 120, 40, 8); fs(c, "#7a4a24", "#3a2010", 3)
    if plaque:
        rrect(c, -50, -34, 100, 28, 6); fs(c, "#ffe9a0", "#a87400", 2)
        draw_text(c, "BEST TEAM", 0, -20, 17, "#7a4a24", None, 0, lang="en")
    rrect(c, -16, -90, 32, 52, 6); fs(c, "#ffd23f", "#a87400", 3)
    for sgn in (-1, 1):
        c.move_to(sgn * 66, -200); c.curve_to(sgn * 120, -200, sgn * 110, -130, sgn * 50, -130); setc(c, "#a87400"); c.set_line_width(16); c.stroke()
        c.move_to(sgn * 66, -200); c.curve_to(sgn * 120, -200, sgn * 110, -130, sgn * 50, -130); setc(c, "#ffd23f"); c.set_line_width(10); c.stroke()
    c.move_to(-80, -230); c.line_to(80, -230); c.curve_to(80, -140, 40, -96, 0, -92); c.curve_to(-40, -96, -80, -140, -80, -230); c.close_path()
    c.set_source(lin(c, -80, 0, 80, 0, [(0, "#fff08a"), (0.5, "#ffd23f"), (1, "#c98f00")])); c.fill_preserve(); setc(c, "#a87400"); c.set_line_width(4); c.stroke()
    star(c, 0, -170, 26, "#ffffff", "#ffd23f")
    c.move_to(-56, -220); c.curve_to(-58, -170, -40, -130, -20, -112); setc(c, (1, 1, 1, 0.5)); c.set_line_width(6); c.stroke()
    c.restore()

def fireworks(c, t, t0):
    r = random.Random(11)
    for k in range(14):
        tb = t0 + k * 0.55 + r.uniform(0, 0.3); x = r.uniform(120, 1160); y = r.uniform(80, 300); col = r.choice(RAINBOW + ["#ffffff", "#ff9fcf"])
        q = prog(t, tb, tb + 1.3)
        if q <= 0 or q >= 1: continue
        for j in range(24):
            a = j * PI / 12; rr = 150 * ease(q); r0 = max(0, rr - 50)
            c.move_to(x + r0 * math.cos(a), y + r0 * math.sin(a) + 30 * q * q); c.line_to(x + rr * math.cos(a), y + rr * math.sin(a) + 30 * q * q)
            setc(c, (*hexc(col)[:3], 0.8 * (1 - q))); c.set_line_width(5); c.stroke()
            star(c, x + rr * math.cos(a), y + rr * math.sin(a) + 30 * q * q, 9 * (1 - q) + 3, col, "#ffffff")

def note_scroll(c, x, y, q):
    if q <= 0.02: return
    c.save(); c.translate(x, y); c.scale(q, q)
    rrect(c, -170, -46, 340, 92, 10); fs(c, "#fff6dc", "#c8963f", 4)
    for sx in (-176, 176): ell(c, sx, 0, 14, 50); fs(c, "#e8c890", "#c8963f", 3)
    draw_text(c, "Thanks for playing,", 0, -14, 28, "#7a4a24", None, 0, lang="en"); draw_text(c, "friends!", 0, 20, 28, "#e8327f", None, 0, lang="en")
    c.restore()

# ---------------------------------------------------------------- scenes
def sucked(c, t, x, y, fn):
    p = ease(prog(t, T_PULL + 0.9, T_CITY - 0.1))
    if p >= 0.98: return
    c.save(); px, py = lerp(x, TVX, p), lerp(y, TVY + 120, p)
    c.translate(px, py - 150); c.rotate(p * 7 + 0.15 * math.sin(t * 20) * (p > 0)); c.scale(1 - 0.85 * p, 1 - 0.85 * p); c.translate(-px, -(py - 150))
    fn(px, py); c.restore()

def scene_room(c, t):
    room_bg(c, t)
    c.save(); c.move_to(110, 300); c.line_to(300, 300); c.line_to(600, 720); c.line_to(150, 720); c.close_path(); setc(c, (1, 0.95, 0.7, 0.22)); c.fill(); c.restore()   # morning sun
    glow = ease(prog(t, T_START, T_START + 0.6)) * (0.6 + 0.4 * math.sin(t * 10))
    tv(c, t, glow)
    kq = prog(t, T_KEYIN + 1.0, T_KEYIN + 1.6)
    if t >= T_KEYIN + 1.0 and t < T_PULL + 1.0:   # key in the console slot, turning
        c.save(); c.translate(810, 410); c.rotate(-PI / 2 * ease(prog(t, T_KEYIN + 1.4, T_KEYIN + 1.9))); gold_key(c, 0, -30, t, 0.45, glow=False); c.restore()
    if t >= T_PULL:
        R = 40 + 260 * ease(prog(t, T_PULL, T_PULL + 1.2)); portal(c, TVX, TVY, R, t)
        for k in range(14):
            a = k * 0.45 + t; rr = 520 - ((t * 500 + k * 90) % 480)
            c.move_to(TVX + rr * math.cos(a), TVY + rr * math.sin(a) * 0.7); c.line_to(TVX + (rr - 60) * math.cos(a), TVY + (rr - 60) * math.sin(a) * 0.7)
            setc(c, (1, 1, 1, 0.5)); c.set_line_width(4); c.stroke()
    shake = 3 * math.sin(t * 40) if t >= T_PULL else 0
    pull = ease(prog(t, T_PULL, T_PULL + 0.9))
    yawn = active(t, "yawn", 0.1, 0.4)
    def draw_tinku(px, py):
        a = talk("tinku", t, 0); closed = False
        if yawn: a = ((2.7, 0.3), (2.7, 0.3))
        if t >= T_PULL: a = ((2.3, 0.6), (2.6, 0.2))
        tinku(c, px + shake, py, t, 0.88, a, mo("tinku", t), 0.3, yawn or blink(t, 0.3), 0, 0.25 * pull)
    def draw_pinky(px, py):
        a = talk("pinky", t, 2); hop = 0
        if active(t, "wake", 0, 0.3) or active(t, "exactly", 0, 0.3): hop = abs(math.sin(t * 8)) * 12
        if active(t, "pillow", 0, 0.2): a = (a[0], (2.4, 0.3))
        if T_KEYIN <= t < T_KEYIN + 1.6: a = (a[0], (1.6, 0.4))
        if t >= T_PULL: a = SCARED
        hands = kid("pinky", c, px + shake, py, t, a, 0.2 if t < T_KEYIN else 0.6, hop, 0.88, 0.28 * pull)
        if t < T_KEYIN + 1.0: gold_key(c, hands[1][0] + 10, hands[1][1] - 6, t, 0.42)
    def draw_moti(px, py):
        hop = abs(math.sin(t * 7)) * 14 if active(t, "bark1", 0.2, 0.6) or active(t, "okay", 0, 0.5) else 0
        puppy(c, px + shake, py, t, 0.72, hop, 2.5)
    pxk = lerp(470, 640, ease(prog(t, T_KEYIN, T_KEYIN + 0.9)))
    for x, fn in ((1090, draw_moti), (260, draw_tinku), (pxk, draw_pinky)):
        sucked(c, t, x, GY, fn) if t >= T_PULL else fn(x, GY)

def hop_state(t):
    """Pinky's x, y and how many colours are lit."""
    n = sum(1 for h in HOPS if t >= h)
    if n == 0:
        if t >= HOPS[0] - 0.9: q = prog(t, HOPS[0] - 0.9, HOPS[0]); return lerp(395, tile_x(tile_of(0)), ease(q)), 615 - 70 * math.sin(PI * q), 0
        return 395, GY, 0
    cur = tile_x(tile_of(n - 1))
    if n < 7 and t >= HOPS[n] - 0.45:
        q = prog(t, HOPS[n] - 0.45, HOPS[n]); nx = tile_x(tile_of(n)); return lerp(cur, nx, q), 615 - 70 * math.sin(PI * q), n
    if n == 7 and t >= T_BRIDGE:
        q = prog(t, T_BRIDGE, T_BRIDGE + 0.8); return lerp(cur, 395, ease(q)), lerp(615, GY, q) - 50 * math.sin(PI * q), n
    return cur, 615, n

def scene_sky(c, t):
    sky_bg(c, t); cloud_sea(c, t)
    shake = 5 * math.sin(t * 40) if active(t, "shaking", 0.4, 0) or T_MOTI + 0.6 <= t <= T_MOTIBACK else 0
    c.save(); c.translate(shake, 0)
    island(c, -20, 560, 592, t, 3); island(c, 900, 1300, 592, t, 5)
    chest(c, 1110, 612, t)
    px, py, lit = hop_state(t)
    bridge(c, t, lit)
    tiles(c, t, lit, T_MOTI + 0.5 <= t < T_MOTIBACK)
    c.restore()
    # walking over the bridge
    cross = [(n, T_CROSS + d) for n, d in (("pinky", 0.0), ("tinku", 1.4), ("moti", 2.8))]
    def walker(x0, t0):
        q = prog(t, t0, t0 + 7.0); x = lerp(x0, 1000, ease(q)); return x, on_bridge_y(x), 0 < q < 1
    # Moti
    if t < T_CROSS + 2.8:
        mx, my = 505, GY
        if T_MOTI <= t < T_MOTIBACK + 0.6:
            q = prog(t, T_MOTI, T_MOTI + 0.5); q2 = prog(t, T_MOTIBACK, T_MOTIBACK + 0.6)
            gx = tile_x(tile_of(3)); mx = lerp(lerp(505, gx, q), 505, q2); my = lerp(lerp(GY, 625, q), GY, q2) - 70 * math.sin(PI * q) - 60 * math.sin(PI * q2)
        hop = abs(math.sin(t * 7)) * 10 if active(t, "bark3", 0.2, 0.5) else 0
        puppy(c, mx + shake, my, t, 0.62, hop, 2.5)
    else:
        x, y, w = walker(505, T_CROSS + 2.8); puppy(c, x, y, t, 0.62, abs(math.sin(t * 9)) * 8 * w, 2.5)
    # Tinku
    if t < T_CROSS + 1.4:
        a = talk("tinku", t, 0); look = 0.4
        if active(t, "chest", 0, 0.5): a = (a[0], (1.7, 0.2)); look = 0.7
        if active(t, "tiles", 0, 0.5): a = (a[0], (1.0, -0.3)); look = 0.2
        if active(t, "wrong", 0, 0.5) or active(t, "shaking", 0, 0.3): a = SCARED
        if active(t, "bridge", 0, 0.5): a = CHEER
        tinku(c, 120 + shake, GY, t, 0.8, a, mo("tinku", t), look, blink(t, 0.3), 0)
    else:
        x, y, w = walker(120, T_CROSS + 1.4)
        a = talk("tinku", t, 0)
        if active(t, "wobbly", 0, 0.5): a = (a[0], (1.2, 0.2))
        tinku(c, x, y, t, 0.8, a, mo("tinku", t), 0.4, blink(t, 0.3), abs(math.sin(t * 9)) * 8 * w, 0.06 * math.sin(t * 5) * w)
    # Pinky
    if t < T_CROSS:
        a = talk("pinky", t, 2); look = 0.4
        if active(t, "pattern", 0, 0.3): a = (a[0], (2.6, 0.2))
        if HOPS[0] - 0.9 <= t < T_BRIDGE + 0.8: a = CHEER
        if active(t, "cross", 0, 0.3): a = (a[0], (1.7, 0.3))
        hands = pinky(c, px + shake, py, t, 0.8, a, mo("pinky", t), look, blink(t, 1.4), 0)
    else:
        x, y, w = walker(395, T_CROSS)
        a = talk("pinky", t, 2)
        if active(t, "wobbly", 0, 0.3): a = ((1.6, 0.2), (1.6, 0.2))
        pinky(c, x, y, t, 0.8, a, mo("pinky", t), 0.4, blink(t, 1.4), abs(math.sin(t * 9 + 1)) * 8 * w, 0.08 * math.sin(t * 5 + 1) * w)
    for k, h in enumerate(HOPS):   # colour name pops up on every hop
        q = prog(t, h, h + 1.0)
        if 0 < q < 1: draw_text(c, ["RED", "ORANGE", "YELLOW", "GREEN", "BLUE", "INDIGO", "VIOLET"][k], tile_x(tile_of(k)), 470 - 40 * q, 30, RAINBOW[k], "#ffffff", 5, lang="en", alpha=1 - q * q)
    if T_MOTI + 0.5 <= t < T_MOTI + 1.8 and (t * 6) % 1 < 0.7:
        draw_text(c, "WRONG TILE!", tile_x(tile_of(3)), 470, 34, "#e8202a", "#ffffff", 6, lang="en")
    banner(c, t, T_CITY + 1.6, "SECRET LEVEL", "#7b2fd6", "Reach the treasure!", 3.2)
    banner(c, t, T_BRIDGE + 0.3, "RAINBOW BRIDGE!", "#2f8bff", "Red - Orange - Yellow - Green - Blue - Indigo - Violet", 3.4, 150, 50)

def scene_treasure(c, t):
    sky_bg(c, t); fireworks(c, t, T_FIRE); cloud_sea(c, t)
    island(c, 120, 1160, 592, t, 7)
    oq = ease(prog(t, T_OPEN, T_OPEN + 0.6))
    rise = back(prog(t, T_TROPHY, T_TROPHY + 1.0))
    if t < T_SAVE:
        chest(c, 640, 612, t, oq)
        if rise > 0: trophy(c, 640, 510 - 60 * rise + 6 * math.sin(t * 2), 0.55 + 0.45 * rise * 0.6, t)
    note_scroll(c, 640, 150, back(prog(t, T_NOTE, T_NOTE + 0.5)) * (1 - prog(t, E("note") + 1.0, E("note") + 1.4)))
    walk_in = ease(prog(t, T_TREASURE, T_TREASURE + 1.8))
    for i, (n, x0, x) in enumerate((("pinky", -200, 400), ("tinku", -380, 880))):
        xx = lerp(x0, x, walk_in) if n == "pinky" else lerp(1500, x, walk_in)
        a = talk(n, t, i); hop = abs(math.sin(t * 9 + i)) * 8 * (walk_in < 1)
        if n == "pinky" and active(t, "open", 0, 0.6): a = ((1.5, 0.2), (1.5, 0.2))
        if active(t, "trophy", 0, 1.0) or active(t, "complete", 0, 1.2) or active(t, "fireworks", 0, 0.5): a = CHEER; hop = abs(math.sin(t * 8 + i)) * 16
        if n == "tinku" and active(t, "youopen", 0, 0.3): a = (a[0], (1.7, 0.3))
        fn = tinku if n == "tinku" else pinky
        fn(c, xx, GY, t, 0.85, a, mo(n, t), 0.3 if n == "pinky" else -0.3, blink(t, i), hop)
    mx = lerp(1600, 1030, walk_in)
    puppy(c, mx, GY, t, 0.66, abs(math.sin(t * 8)) * (16 if active(t, "bark4", 0.2, 1.0) else 4), 3.0)
    banner(c, t, S("complete") - 0.1, "GAME COMPLETE!", "#2fbf4a", "+1000 coins", 3.4, 200)
    if t >= T_SAVE:
        R = 60 + 900 * ease(prog(t, T_SAVE, T_BACK + 0.2)); portal(c, 640, 360, R, t)

def scene_back(c, t):
    room_bg(c, t); tv(c, t, 0.4 * (1 - prog(t, T_BACK, T_BACK + 2.0)))
    tq = prog(t, T_BACK + 1.2, T_BACK + 1.9)   # the trophy pops out too and lands on the cabinet
    if t >= T_BACK + 1.2: trophy(c, lerp(TVX, 980, tq), lerp(TVY, 440, tq) - 120 * math.sin(PI * tq), 0.42, t)
    for i, (n, x) in enumerate((("tinku", 300), ("pinky", 500))):
        t0 = T_BACK + 0.3 + i * 0.25; p = prog(t, t0, t0 + 0.7)
        px = lerp(TVX, x, p); py = lerp(TVY + 60, GY, p) - 160 * math.sin(PI * p)
        a = talk(n, t, i); hop = 0.0
        if p < 1: a = CHEER
        if n == "pinky" and active(t, "back", 0, 0.3): a = (a[0], (1.9, 0.3))
        if active(t, "bye1", 0, 4) or active(t, "bye2", 0, 3): a = (a[0], (2.1, 0.5 + 0.5 * math.sin(t * 11 + i))); hop = abs(math.sin(t * 5 + i)) * 10
        if t >= t0:
            c.save(); c.translate(px, py - 150); c.rotate((1 - p) * 4); c.translate(-px, -(py - 150))
            (tinku if n == "tinku" else pinky)(c, px, py, t, 0.88, a, mo(n, t), 0, blink(t, i), hop); c.restore()
    t0 = T_BACK + 0.9; p = prog(t, t0, t0 + 0.7)
    if t >= t0: puppy(c, lerp(TVX, 700, p), lerp(TVY + 60, GY, p) - 140 * math.sin(PI * p), t, 0.72, abs(math.sin(t * 7)) * 10 if p >= 1 else 0, 3.0)

def outro_card(c, t):
    lt = t - T_OUTRO
    gr = cairo.RadialGradient(640, 380, 40, 640, 380, 900); gr.add_color_stop_rgba(0, *hexc("#fff3c4")); gr.add_color_stop_rgba(1, *hexc("#a8dcff")); c.set_source(gr); c.paint()
    for k in range(7):
        c.arc(640, 980, 700 - k * 26, PI, 2 * PI); setc(c, (*hexc(RAINBOW[k])[:3], 0.35)); c.set_line_width(26); c.stroke()
    r = random.Random(5)
    for k in range(40):
        x0 = r.uniform(0, W); sp = r.uniform(60, 130); ph = r.uniform(0, 800)
        y = (ph + lt * sp) % 800 - 40; x = x0 + 20 * math.sin(lt * 2 + k)
        if k % 3 == 0: star(c, x, y, 9, "#ffd23f", "#c98f00")
        else: c.save(); c.translate(x, y); c.rotate(lt * 2 + k); rrect(c, -6, -3, 12, 6, 2); setc(c, RAINBOW[k % 7]); c.fill(); c.restore()
    p = back(prog(lt, 0.1, 0.6))
    if p > 0.02: c.save(); c.translate(640, 140); c.scale(p, p); draw_text(c, "Bye-bye!", 0, 0, 130, "#7b2fd6", "#ffffff", 12, lang="en"); c.restore()
    p2 = back(prog(lt, 0.5, 1.0))
    if p2 > 0.02:
        c.save(); c.translate(640, 262); c.scale(p2, p2); draw_text(c, "See you next time!", 0, 0, 46, "#7c2d12", "#ffffff", 5, lang="en")
        draw_text(c, NEXT, 0, 58, 36, "#2f7bff", "#ffffff", 4, lang="en"); c.restore()
    for i, (fn, x) in enumerate(((tinku, 430), (pinky, 640))):
        fn(c, x, 680, t, 0.8, ((0.15, 0.3), (2.1, 0.5 + 0.5 * math.sin(t * 10 + i))), 0, 0, blink(t, i), abs(math.sin(t * 5 + i)) * 12)
    moti(c, 840, 680, t, 0.8, 0, -0.3, False, abs(math.sin(t * 6)) * 12, 2.5)
    trophy(c, 1010, 680, 0.45, t)

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

SCENES = [(0.0, scene_room), (T_CITY, scene_sky), (T_TREASURE, scene_treasure), (T_BACK, scene_back), (T_OUTRO, lambda c, t: outro_card(c, t))]
WIPE = {T_TREASURE, T_OUTRO}
FLASH = {T_CITY, T_BACK}

def frame(t, surf=None, with_captions=True):
    surf = surf or cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(surf)
    idx = max(i for i, (t0, _) in enumerate(SCENES) if t >= t0)
    t0, fn = SCENES[idx]
    z = 1.0 + 0.04 * ease(prog(t, t0, t0 + 12)) if fn is not SCENES[-1][1] else 1.0
    if T_PULL <= t < T_CITY: z += 0.12 * ease(prog(t, T_PULL, T_CITY))          # camera dives toward the TV
    sh = 0
    for ts_ in (T_MOTI + 0.5,):
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
        hud(c, t, ha)
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
