"""Story: Grand Tinku Adventure. Starts straight in the story (no title card, no brand text).
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

def kid(name, c, x, y, t, arms, look=0.0, hop=0.0, s=0.88, lean=0.0):
    fn = {"tinku": tinku, "golu": golu}[name]
    return fn(c, x, y, t, s, arms, mo(name, t), look, blink(t, {"tinku": 0.3, "golu": 2.2}[name]), hop, lean)

def puppy(c, x, y, t, s=0.78, hop=0.0, wag=2.0, look=-0.3):
    moti(c, x, y, t, s, mo("moti", t), look, blink(t, 0.9), hop, wag)

def star(c, x, y, r, col="#ffd23f", out="#c98f00"):
    pts = [((r if i % 2 == 0 else r * 0.45) * math.cos(-PI / 2 + i * PI / 5) + x, (r if i % 2 == 0 else r * 0.45) * math.sin(-PI / 2 + i * PI / 5) + y) for i in range(10)]
    poly(c, pts); fs(c, col, out, 2)
def heart(c, x, y, s=1.0, col="#ff4f8b", a=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.move_to(0, 12); c.curve_to(-26, -6, -14, -24, 0, -10); c.curve_to(14, -24, 26, -6, 0, 12); setc(c, (*hexc(col)[:3], a)); c.fill(); c.restore()

# ---------------------------------------------------------------- game values
COIN_T = [S("coins") - 0.9 + 0.32 * k for k in range(14)]     # coins picked up during the chase
def coins_at(t):
    n = 10 * sum(1 for tc in COIN_T if t >= tc)
    if t >= S("passed1") + 0.2: n += 100
    if t >= S("levelup") + 0.2: n += 250
    return n
def last_coin_change(t):
    ev = [tc for tc in COIN_T if tc <= t] + [x for x in (S("passed1") + 0.2, S("levelup") + 0.2) if x <= t]
    return max(ev) if ev else -9

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
        draw_text(c, "8:00 PM", 0, 1, 28, "#ff3b6b", None, 0, lang="en"); c.restore()
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
        for k in range(14):   # wind streaks into the screen
            a = k * 0.45 + t; rr = 520 - ((t * 500 + k * 90) % 480)
            c.move_to(TVX + rr * math.cos(a), TVY + rr * math.sin(a) * 0.7); c.line_to(TVX + (rr - 60) * math.cos(a), TVY + (rr - 60) * math.sin(a) * 0.7)
            setc(c, (1, 1, 1, 0.5)); c.set_line_width(4); c.stroke()
    shake = 3 * math.sin(t * 40) if t >= T_PULL else 0
    pull = ease(prog(t, T_PULL, T_PULL + 0.9))
    def draw_moti(px, py):
        hop = abs(math.sin(t * 7)) * 14 if active(t, "bark1", 0.2, 0.6) or active(t, "gta", 0, 0.5) else 0
        puppy(c, px + shake, py, t, 0.72, hop, 2.5)
    def draw_tinku(px, py):
        a = talk("tinku", t, 0)
        if t < T_PULL and not active(t, "gta", 0, 0.3): a = HOLD
        if active(t, "gta", 0, 0.5): a = (HOLD[0], (2.3, 0.4))
        if t >= T_PULL: a = ((2.3, 0.6), (2.6, 0.2))
        hands = kid("tinku", c, px + shake, py, t, a, 0.3 if t < T_PULL else 0.6, 0, 0.88, 0.25 * pull)
        if a == HOLD or a[0] == HOLD[0]: controller(c, hands, t)
    def draw_golu(px, py):
        a = talk("golu", t, 1); hop = 0
        if active(t, "start", 0, 0.6) or active(t, "newgame", 0, 0.3): hop = abs(math.sin(t * 9)) * 16; a = CHEER if active(t, "start", 0, 0.6) else a
        if t >= T_PULL: a = SCARED
        kid("golu", c, px + shake, py, t, a, 0.4, hop, 0.88, 0.3 * pull)
    sucked(c, t, 1090, GY, draw_moti) if t >= T_PULL else draw_moti(1090, GY)
    sucked(c, t, 360, GY, draw_tinku) if t >= T_PULL else draw_tinku(360, GY)
    sucked(c, t, 540, GY, draw_golu) if t >= T_PULL else draw_golu(540, GY)

def scene_city(c, t):
    city_bg(c, t, 0)
    land = prog(t, T_CITY + 0.2, T_CITY + 1.0)
    for i, (n, x) in enumerate((("tinku", 400), ("golu", 600))):
        a = talk(n, t, i); hop = 0.0; look = 0.0
        drop = (1 - back(prog(t, T_CITY + 0.2 + i * 0.15, T_CITY + 0.9 + i * 0.15))) * 600
        if active(t, "inside", 0, 0.8) or active(t, "sea", 0, 0.3): a = CHEER; hop = abs(math.sin(t * 8 + i)) * 16
        if n == "tinku" and active(t, "hud", 0, 0.5): a = (a[0], (2.6, 0.1)); look = -0.4
        if n == "golu" and active(t, "pizza", 0, 0.3): a = (a[0], (1.6, 0.0)); look = -0.5
        if active(t, "cart", 0, 2.0) : look = 0.6
        if n == "tinku" and active(t, "kart", 0, 0.6): a = (a[0], (1.7, 0.3))
        kid(n, c, x, GY, t, a, look, hop + drop)
    # the ice-cream cart rolls past (mission 1 starts)
    if t >= S("cart") - 0.8:
        icecream_cart(c, lerp(1500, 1050, ease(prog(t, S("cart") - 0.8, S("cart") + 0.6))) + 30 * max(0, t - S("cart") - 0.6), GY + 30, t)
    if t >= S("kart") + 0.2:      # go-kart rolls in
        go_kart(c, lerp(-300, 180, ease(prog(t, S("kart") + 0.2, S("kart") + 1.4))), GY + 60, t, empty=True)
    banner(c, t, S("mission1") - 0.1, "MISSION 1", "#ff2fd0", "Stop the runaway ice-cream cart!", 3.6)

def icecream_cart(c, x, y, t, roll=True):
    c.save(); c.translate(x, y)
    for wx in (-70, 70):
        ell(c, wx, -14, 26, 26); fs(c, "#3a3f5a", "#11121c", 3); ell(c, wx, -14, 10, 10); setc(c, "#c0c4d8"); c.fill()
        for k in range(4):
            a = k * PI / 4 + (t * 8 if roll else 0); c.move_to(wx + 10 * math.cos(a), -14 + 10 * math.sin(a)); c.line_to(wx + 24 * math.cos(a), -14 + 24 * math.sin(a))
        setc(c, "#c0c4d8"); c.set_line_width(2); c.stroke()
    rrect(c, -110, -150, 220, 120, 16); c.set_source(lin(c, 0, -150, 0, -30, [(0, "#ffffff"), (1, "#d6f0ff")])); c.fill_preserve(); setc(c, "#4a8ad0"); c.set_line_width(3); c.stroke()
    for k in range(5): rrect(c, -110 + k * 44, -60, 22, 30, 0); setc(c, "#ff9fcf"); c.fill()
    # painted cone
    poly(c, [(-20, -70), (20, -70), (0, -30)]); fs(c, "#e8a050", "#a8602a", 2)
    for dx, col in ((-12, "#ff9fcf"), (12, "#8cf0b0"), (0, "#fff36b")): ell(c, dx, -84 - (10 if dx == 0 else 0), 16, 14); fs(c, col, dark(col, 0.7), 2)
    draw_text(c, "ICE CREAM", 0, -130, 24, "#ff3b8b", "#ffffff", 4, lang="en")
    c.move_to(0, -150); c.line_to(0, -240); setc(c, "#8a8fa8"); c.set_line_width(5); c.stroke()     # umbrella
    for k in range(6):
        a0 = PI + k * PI / 6; a1 = a0 + PI / 6
        c.move_to(0, -240); c.arc(0, -240, 120, a0, a1); c.close_path(); setc(c, "#ff5b7a" if k % 2 else "#ffffff"); c.fill()
    c.arc(0, -240, 120, PI, 2 * PI); setc(c, "#c0304a"); c.set_line_width(2.5); c.stroke()
    c.restore()

def go_kart(c, x, y, t, bounce=0.0, empty=False, riders=None):
    c.save(); c.translate(x, y - bounce)
    if riders: riders()
    for wx in (-130, 130):
        ell(c, wx, -30, 40, 40); fs(c, "#2b2d42", "#11121c", 3); ell(c, wx, -30, 18, 18); setc(c, "#ffd23f"); c.fill()
        for k in range(3):
            a = k * PI / 3 - t * 14; c.move_to(wx + 18 * math.cos(a), -30 + 18 * math.sin(a)); c.line_to(wx + 34 * math.cos(a), -30 + 34 * math.sin(a))
        setc(c, (1, 1, 1, 0.5)); c.set_line_width(3); c.stroke()
    c.move_to(-200, -60); c.curve_to(-210, -120, -170, -140, -120, -140); c.line_to(150, -140); c.curve_to(200, -140, 230, -110, 236, -70)
    c.curve_to(240, -46, 210, -40, 180, -40); c.line_to(-180, -40); c.curve_to(-200, -40, -200, -50, -200, -60); c.close_path()
    c.set_source(lin(c, 0, -140, 0, -40, [(0, "#ff5b4a"), (1, "#c8201a")])); c.fill_preserve(); setc(c, "#7a100a"); c.set_line_width(4); c.stroke()
    c.move_to(-170, -120); c.line_to(180, -120); setc(c, (1, 1, 1, 0.35)); c.set_line_width(6); c.stroke()
    ell(c, 0, -90, 34, 26); fs(c, "#ffffff", "#7a100a", 3); draw_text(c, "1", 0, -90, 34, "#c8201a", None, 0, lang="en")
    rrect(c, -230, -96, 24, 30, 6); fs(c, "#8a8fa8", "#3a3f5a", 2)   # exhaust
    c.restore()
    if not empty and bounce == 0:
        for k in range(3):   # exhaust puffs
            q = ((t * 2.5 + k / 3) % 1)
            ell(c, x - 240 - 90 * q, y - 82 - 20 * q, 14 + 22 * q, 12 + 18 * q); setc(c, (1, 1, 1, 0.55 * (1 - q))); c.fill()

def banana(c, x, y):
    c.save(); c.translate(x, y)
    for a in (-0.9, 0, 0.9):
        c.save(); c.rotate(a); c.move_to(-6, 0); c.curve_to(-14, -20, -10, -40, 0, -46); c.curve_to(10, -40, 14, -20, 6, 0); c.close_path(); fs(c, "#ffe066", "#a88a00", 2.5); c.restore()
    ell(c, 0, -4, 10, 6); fs(c, "#a88a00"); c.restore()

SPEED = 560
_scr = {}
def kart_scroll(t):
    """Distance the world has scrolled since the chase began (speed eases in, eases to a stop when caught)."""
    f = int((t - T_KART) * FPS)
    if f <= 0: return 0.0
    if f in _scr: return _scr[f]
    s = 0.0
    for i in range(f):
        tt = T_KART + i / FPS
        v = SPEED * ease(prog(tt, T_KART, T_KART + 1.0)) * (1 - ease(prog(tt, T_CAUGHT + 0.2, T_CAUGHT + 1.2)))
        s += v / FPS
    _scr[f] = s; return s
def speed_at(t): return SPEED * ease(prog(t, T_KART, T_KART + 1.0)) * (1 - ease(prog(t, T_CAUGHT + 0.2, T_CAUGHT + 1.2)))

def scene_kart(c, t):
    sc = kart_scroll(t); v = speed_at(t)
    city_bg(c, t, sc)
    for k in range(9):   # speed lines
        if v < 200: break
        y = 130 + k * 47; x = (k * 377 - t * 1600) % 1600 - 160
        c.move_to(x, y); c.line_to(x + 140, y); setc(c, (1, 1, 1, 0.35)); c.set_line_width(4); c.stroke()
    kx = lerp(380, 600, ease(prog(t, T_CAUGHT, T_CAUGHT + 1.2)))
    jb = 150 * math.sin(PI * prog(t, T_JUMP, T_JUMP + 0.85)) if T_JUMP <= t <= T_JUMP + 0.85 else 0
    rumble = 3 * abs(math.sin(t * 30)) if v > 100 else 0
    cx = lerp(1020, 1010, 0) + 25 * math.sin(t * 2.2) * (v > 100)
    icecream_cart(c, cx, GY + 4, t, roll=v > 20)
    # banana peel on the road
    bt = T_JUMP + 0.42
    bx = kx + (bt - t) * SPEED
    if -60 < bx < W + 60: banana(c, bx, GY - 4)
    # coins on the road
    for k, tc in enumerate(COIN_T):
        if t < tc:
            x = kx + 180 + (tc - t) * SPEED
            if x < W + 40: coin(c, x, GY - 70 - 40 * abs(math.sin(k)), t, 1.1, k)
        popup(c, t, tc, "+10", kx + 230, GY - 200)
    def riders():
        for n, rx, ry in (("golu", -70, -86), ("tinku", 80, -104)):
            a = talk(n, t, 0 if n == "tinku" else 1); hop = 3 * math.sin(t * 22 + rx)
            if n == "tinku": a = HOLD if not active(t, "passed1", 0, 1) else CHEER
            if n == "golu" and (active(t, "faster", 0, 0.5) or active(t, "count", 0, 0.5) or active(t, "flying", 0, 0.4) or active(t, "caught", 0, 1)): a = CHEER
            if n == "golu" and active(t, "banana", 0, 0.4): a = ((1.6, 0.0), a[1])
            kid(n, c, rx, ry, t, a, 0.4, hop, 0.76)
        rrect(c, 120, -170, 12, 50, 4); fs(c, "#3a3f5a")                  # steering column
        ell(c, 126, -172, 30, 10); setc(c, "#2b2d42"); c.set_line_width(7); c.stroke()
    go_kart(c, kx, GY - 4, t, jb + rumble, riders=riders)
    if T_JUMP <= t <= T_JUMP + 1.0:
        for k in range(5):
            q = prog(t, T_JUMP + k * 0.05, T_JUMP + 0.8); ell(c, kx - 60 - 120 * q + k * 20, GY - 14, 24 * (1 - q) + 4, 10 * (1 - q) + 2); setc(c, (1, 1, 1, 0.5 * (1 - q))); c.fill()
    banner(c, t, S("passed1") - 0.1, "MISSION PASSED!", "#2fbf4a", "+100 coins", 3.2)

# ---------------------------------------------------------------- arcade / claw machine
MX, MY0, MY1 = 860, 170, 560      # claw machine centre x, glass top, glass bottom
def claw_state(t):
    """(x, rope_len, closed, holding) of the claw."""
    home_x, top = MX, 40
    def leg(t0, target_x, grab):
        k = [(t0, home_x, top, 0), (t0 + 1.2, target_x, top, 0), (t0 + 2.2, target_x, 250, 0), (t0 + 2.6, target_x, 250, 1), (t0 + 3.6, target_x, top, 1), (t0 + 4.8, MX + 110, top, 1), (t0 + 5.2, MX + 110, top, 0)]
        return k
    keys = leg(T_CLAW1, MX - 70, "teddy") + leg(T_CLAW2, MX + 10, "moti")
    x, ln, cl = home_x, top, 0
    for (a, xa, la, ca), (b, xb, lb, cb) in zip(keys, keys[1:]):
        if a <= t <= b and b > a:
            p = ease(prog(t, a, b)); x = lerp(xa, xb, p); ln = lerp(la, lb, p); cl = ca if t < b else cb; break
        if t > b: x, ln, cl = xb, lb, cb
    hold = None
    if T_CLAW1 + 2.6 <= t < T_CLAW1 + 5.2: hold = "teddy"
    if T_CLAW2 + 2.6 <= t < T_CLAW2 + 5.2: hold = "moti"
    return x, ln, cl, hold

def teddy(c, x, y, s=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    for ex in (-22, 22): ell(c, ex, -78, 12, 12); fs(c, "#b8743a", "#6a3a14", 2)
    ell(c, 0, -20, 30, 32); fs(c, "#c98a4a", "#6a3a14", 2.5); ell(c, 0, -14, 16, 18); setc(c, "#f0c890"); c.fill()
    ell(c, 0, -60, 28, 26); fs(c, "#c98a4a", "#6a3a14", 2.5)
    for ex in (-10, 10): ell(c, ex, -64, 4, 4); setc(c, "#2b1b14"); c.fill()
    ell(c, 0, -54, 8, 6); setc(c, "#f0c890"); c.fill(); ell(c, 0, -56, 3.5, 3); setc(c, "#2b1b14"); c.fill()
    poly(c, [(-12, -36), (0, -30), (12, -36), (0, -42)]); setc(c, "#ff3b6b"); c.fill()
    c.restore()

def toys_pile(c, t, moti_in):
    r = random.Random(9)
    cols = ["#ff3b6b", "#2f7bff", "#ffd23f", "#2fbf4a", "#a04dff", "#ff8c1a"]
    for k in range(26):
        x = MX - 130 + r.uniform(0, 260); y = MY1 - 20 - r.uniform(0, 70) * (1 - abs(x - MX) / 200)
        ell(c, x, y, 22, 22); fs(c, cols[k % 6], dark(cols[k % 6], 0.65), 2); ell(c, x - 7, y - 7, 6, 5); setc(c, (1, 1, 1, 0.5)); c.fill()
    for k, (dx, dy) in enumerate(((-110, -60), (100, -70))):     # rubber ducks
        x, y = MX + dx, MY1 + dy
        ell(c, x, y, 24, 18); fs(c, "#ffe066", "#a88a00", 2); ell(c, x + 12 * (1 if k else -1), y - 20, 13, 13); fs(c, "#ffe066", "#a88a00", 2)
        poly(c, [(x + 22 * (1 if k else -1), y - 22), (x + 34 * (1 if k else -1), y - 18), (x + 22 * (1 if k else -1), y - 14)]); setc(c, "#ff8c1a"); c.fill()

def claw_machine(c, t):
    x0, x1 = MX - 170, MX + 170
    rrect(c, x0 - 20, MY0 - 70, 380, 70, 18); c.set_source(lin(c, 0, MY0 - 70, 0, MY0, [(0, "#ff5fd0"), (1, "#b02fa0")])); c.fill_preserve(); setc(c, "#5a1050"); c.set_line_width(4); c.stroke()
    draw_text(c, "PRIZE CLAW", MX, MY0 - 36, 36, "#ffe066", "#5a1050", 5, lang="en")
    for k in range(12):   # chasing bulbs
        on = (int(t * 8) + k) % 3 == 0; ell(c, x0 - 4 + k * 32, MY0 - 6, 6, 6); setc(c, "#fff36b" if on else "#a8608a"); c.fill()
    rrect(c, x0 - 20, MY1, 380, 150, 12); c.set_source(lin(c, 0, MY1, 0, MY1 + 150, [(0, "#7b5cff"), (1, "#4a2fb0")])); c.fill_preserve(); setc(c, "#2a1a6a"); c.set_line_width(4); c.stroke()
    rrect(c, MX + 80, MY1 + 40, 80, 70, 8); fs(c, "#1a1040", "#ffe066", 3)              # prize chute flap
    draw_text(c, "PUSH", MX + 120, MY1 + 75, 18, "#ffe066", None, 0, lang="en")
    rrect(c, MX - 150, MY1 + 30, 150, 60, 10); fs(c, "#3a2a8a", "#ffe066", 2)            # control deck
    ell(c, MX - 40, MY1 + 60, 18, 18); fs(c, "#ff3b6b", "#7a1020", 3)
    # glass box contents
    c.save(); c.rectangle(x0, MY0, 340, MY1 - MY0); c.clip()
    c.set_source(lin(c, 0, MY0, 0, MY1, [(0, "#3a2a7a"), (1, "#6a4ab0")])); c.paint()
    toys_pile(c, t, True)
    cx, ln, cl, hold = claw_state(t)
    if t < T_CLAW1 + 2.6: teddy(c, MX - 70, MY1 - 40, 0.9)
    if t < T_CLAW2 + 2.6 and t >= T_ARCADE - 1:
        puppy(c, MX + 40, MY1 - 30, t, 0.5, abs(math.sin(t * 6)) * 6 if active(t, "bark2", 0, 0.6) else 0, 1.5, -0.5)
    c.move_to(MX - 170, MY0 + 30); c.line_to(MX + 170, MY0 + 30); setc(c, "#c0c4d8"); c.set_line_width(8); c.stroke()
    rrect(c, cx - 26, MY0 + 18, 52, 26, 6); fs(c, "#8a8fa8", "#3a3f5a", 2)
    tipy = MY0 + 30 + ln
    c.move_to(cx, MY0 + 40); c.line_to(cx, tipy); setc(c, "#d0d4e8"); c.set_line_width(4); c.stroke()
    if hold == "teddy": teddy(c, cx, tipy + 104, 0.9)
    if hold == "moti": puppy(c, cx + 50, tipy + 110, t, 0.5, 0, 3.0, 0.2)
    ell(c, cx, tipy, 18, 14); fs(c, "#c0c4d8", "#5a5f7a", 2.5)
    op = 0.25 if cl else 0.75
    for sgn in (-1, 1):
        c.save(); c.translate(cx + sgn * 10, tipy + 6); c.rotate(-sgn * op)
        c.move_to(0, 0); c.curve_to(sgn * 16, 30, sgn * 10, 56, -sgn * 6, 66); setc(c, "#c0c4d8"); c.set_line_width(7); c.stroke(); c.restore()
    c.restore()
    c.rectangle(x0, MY0, 340, MY1 - MY0); setc(c, (0.8, 0.9, 1, 0.12)); c.fill_preserve(); setc(c, "#ff5fd0"); c.set_line_width(10); c.stroke()
    c.move_to(x0 + 40, MY0 + 20); c.line_to(x0 + 120, MY0 + 20 + 200); setc(c, (1, 1, 1, 0.25)); c.set_line_width(14); c.stroke()

def pigeon_shape(c, flap, col):
    """Side-view pigeon silhouette flying right (used for the boss shadow)."""
    setc(c, col)
    c.move_to(-150, -10); c.line_to(-210, -40); c.line_to(-200, 0); c.line_to(-210, 40); c.line_to(-150, 14); c.close_path(); c.fill()   # tail fan
    ell(c, -20, 0, 140, 52); c.fill()                       # body
    ell(c, 120, -34, 50, 44); c.fill()                      # head
    poly(c, [(160, -40), (204, -26), (160, -18)]); c.fill() # beak
    for sgn, k in ((-1, 1.0), (1, 0.75)):                   # far + near wing
        tip_y = -40 - 190 * flap * k if sgn < 0 else -20 + 150 * flap * k
        c.move_to(-60, -20); c.curve_to(-40, tip_y * 0.6, -10, tip_y, 40, tip_y); c.curve_to(60, tip_y * 0.7, 70, -30, 60, -20); c.close_path(); c.fill()
        for f in range(4):
            fx = -30 + f * 22; c.move_to(fx, tip_y * 0.8); c.line_to(fx - 12, tip_y * 0.8 - 30 * (1 if tip_y < 0 else -1)); c.line_to(fx + 10, tip_y * 0.75); c.close_path(); c.fill()

def boss_shadow(c, t):
    p = prog(t, T_SHADOW, T_SHADOW + 5.0)
    if p <= 0 or p >= 1: return
    x = lerp(-500, 1800, p); y = 150 + 30 * math.sin(p * 6)
    flap = 0.5 + 0.5 * math.sin(t * 6)
    c.save(); c.translate(x, y); c.scale(1.5, 1.5)
    pigeon_shape(c, flap, (0.2, 0.1, 0.35, 0.75))
    ell(c, 132, -42, 8, 8); setc(c, (1, 0.85, 0.2, 0.95)); c.fill()      # glowing eye
    c.restore()

def scene_arcade(c, t):
    city_bg(c, t, 2600)
    c.set_source(lin(c, 0, 540, 0, 720, [(0, "#d89a5a"), (1, "#a86a3a")])); c.rectangle(0, 540, W, 180); c.fill()     # boardwalk planks
    for k in range(9): c.move_to(0, 548 + k * 20); c.line_to(W, 548 + k * 20)
    setc(c, (0.45, 0.25, 0.1, 0.35)); c.set_line_width(2); c.stroke()
    dark_k = ease(prog(t, T_SHADOW, T_SHADOW + 1.0)) * (1 - ease(prog(t, T_SHADOW + 4.5, T_SHADOW + 5.5)))
    boss_shadow(c, t)
    claw_machine(c, t)
    out = prog(t, T_CLAW2 + 5.2, T_CLAW2 + 6.0)
    for i, (n, x) in enumerate((("golu", 330), ("tinku", 560))):
        a = talk(n, t, i); hop = 0.0; look = 0.5
        if n == "tinku" and (T_CLAW1 - 0.4 <= t <= T_CLAW1 + 5.4 or T_CLAW2 - 0.4 <= t <= T_CLAW2 + 5.4):
            a = (a[0], (0.9, -0.6)); look = 0.7
        if n == "golu" and active(t, "dontmove", 0, 0.5): a = ((1.4, 0.4), (1.4, 0.4))
        if active(t, "teddy", 0, 0.3) and n == "golu": a = SCARED
        if active(t, "gotmoti", 0, 1.2) or active(t, "levelup", 0, 1.2): a = CHEER; hop = abs(math.sin(t * 9 + i)) * 18
        if t >= T_SHADOW + 0.4 and t < S("save"): a = SCARED; look = -0.4; hop = abs(math.sin(t * 14)) * 4
        kid(n, c, x, GY + 20, t, a, look, hop)
    if t >= T_CLAW2 + 5.2:   # Moti hops out of the prize chute
        mx = lerp(MX + 120, 445, ease(out)); my = lerp(GY - 10, GY + 60, ease(out)) - 160 * math.sin(PI * out) * (out < 1)
        puppy(c, mx, my, t, 0.72, abs(math.sin(t * 8)) * 14 if out >= 1 else 0, 3.0)
        if active(t, "team", 0, 1.5):
            for k in range(3):
                q = prog(t, S("team") + 0.3 * k, S("team") + 0.3 * k + 1.2)
                if 0 < q < 1: heart(c, 410 + 34 * k, 470 - 80 * q, 1.2, "#ff4f8b", 1 - q)
    if dark_k > 0: c.rectangle(0, 0, W, H); setc(c, (0.1, 0.0, 0.25, 0.35 * dark_k)); c.fill()
    banner(c, t, S("mission2") - 0.1, "MISSION 2", "#ff2fd0", "Rescue Moti!", 3.0)
    banner(c, t, S("teddy") - 0.2, "OOPS!", "#ff8c1a", "Try again", 1.8, 160, 50)
    banner(c, t, S("levelup") - 0.1, "LEVEL UP!", "#2fbf4a", "+250 coins", 2.6)
    if active(t, "boss", 0.2, 1.4) and (t * 4) % 1 < 0.7:
        banner(c, t, S("boss") - 0.2, "WARNING: BOSS INCOMING!", "#e8202a", None, E("boss") - S("boss") + 1.6, 300, 48)
    if t >= T_SAVE:   # SAVING... bar
        q = prog(t, T_SAVE, T_SAVE + 1.8)
        rrect(c, 440, 130, 400, 110, 20); fs(c, (0.12, 0.08, 0.28, 0.9), (1, 1, 1, 1), 4)
        draw_text(c, "SAVING" + "." * (1 + int(t * 4) % 3), 640, 165, 34, "#ffffff", None, 0, lang="en")
        rrect(c, 470, 192, 340, 26, 13); setc(c, (1, 1, 1, 0.25)); c.fill(); rrect(c, 470, 192, max(26, 340 * q), 26, 13); setc(c, "#2fbf4a"); c.fill()
        if q >= 1:
            R = 60 + 900 * ease(prog(t, T_SAVE + 1.8, T_BACK + 0.2)); portal(c, 640, 360, R, t)

def scene_back(c, t):
    room_bg(c, t); tv(c, t, 0.4 * (1 - prog(t, T_BACK, T_BACK + 2.0)))
    for i, (n, x) in enumerate((("tinku", 400), ("golu", 580))):
        t0 = T_BACK + 0.3 + i * 0.25; p = prog(t, t0, t0 + 0.7)
        px = lerp(TVX, x, p); py = lerp(TVY + 60, GY, p) - 160 * math.sin(PI * p)
        a = talk(n, t, i); hop = 0.0; look = 0.0
        if p < 1: a = CHEER
        if active(t, "back", 0, 0.4): look = 0.3
        if n == "tinku" and active(t, "next", 0, 0.5): a = (a[0], (2.4, 0.3))
        if active(t, "bye1", 0, 4) or active(t, "bye2", 0, 3): a = (a[0], (2.1, 0.5 + 0.5 * math.sin(t * 11 + i))); hop = abs(math.sin(t * 5 + i)) * 10
        if t >= t0:
            c.save(); c.translate(px, py); c.rotate((1 - p) * 4); c.translate(-px, -py); kid(n, c, px, py, t, a, look, hop); c.restore()
            if p >= 1 and t < t0 + 2.2:   # dizzy stars
                for k in range(3):
                    a_ = t * 4 + k * 2.1; star(c, x + 70 * math.cos(a_), GY - 330 + 18 * math.sin(a_), 14)
    t0 = T_BACK + 0.9; p = prog(t, t0, t0 + 0.7)
    if t >= t0:
        puppy(c, lerp(TVX, 1000, p), lerp(TVY + 60, GY, p) - 140 * math.sin(PI * p), t, 0.72, abs(math.sin(t * 7)) * 10 if p >= 1 else 0, 3.0)

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
    for i, (fn, x) in enumerate(((tinku, 470), (golu, 670))):
        fn(c, x, 680, t, 0.8, ((0.15, 0.3), (2.1, 0.5 + 0.5 * math.sin(t * 10 + i))), 0, 0, blink(t, i), abs(math.sin(t * 5 + i)) * 12)
    moti(c, 870, 680, t, 0.8, 0, -0.3, False, abs(math.sin(t * 6)) * 12, 2.5)

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

SCENES = [(0.0, scene_room), (T_CITY, scene_city), (T_KART, scene_kart), (T_ARCADE, scene_arcade), (T_BACK, scene_back), (T_OUTRO, lambda c, t: outro_card(c, t))]
WIPE = {T_KART, T_ARCADE, T_OUTRO}
FLASH = {T_CITY, T_BACK}

def frame(t, surf=None, with_captions=True):
    surf = surf or cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(surf)
    idx = max(i for i, (t0, _) in enumerate(SCENES) if t >= t0)
    t0, fn = SCENES[idx]
    z = 1.0 + 0.04 * ease(prog(t, t0, t0 + 12)) if fn is not SCENES[-1][1] else 1.0
    if T_PULL <= t < T_CITY: z += 0.12 * ease(prog(t, T_PULL, T_CITY))          # camera dives toward the TV
    sh = 0
    if T_JUMP + 0.8 <= t <= T_JUMP + 1.3: sh = 7 * (1 - prog(t, T_JUMP + 0.8, T_JUMP + 1.3))
    if T_SHADOW + 0.6 <= t <= T_SHADOW + 1.6: sh = 8 * (1 - prog(t, T_SHADOW + 0.6, T_SHADOW + 1.6))
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
        hud(c, t, ease(prog(t, T_CITY + 1.2, T_CITY + 1.8)) * (1 - prog(t, T_BACK - 0.6, T_BACK)), clock=t >= S("save") - 0.2)
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
