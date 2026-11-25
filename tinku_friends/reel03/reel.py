"""Reel 03: "Mummy's 5 minutes" — Tinku plays himself AND Mummy (dupatta, bindi, rolling pin) in a relatable home sketch.
1080x1920, ~29 s. No hook overlay, no sound-words, no brand text. Big captions at the top (Instagram UI covers the bottom)."""
import sys, os, math, json, subprocess, numpy as np, soundfile as sf, cairo
from scipy.signal import resample_poly, butter, sosfilt
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "mahabharat", "lib"))
from chars import *
from script import NAMES

W, H, FPS = 1080, 1920, 30
TL = json.load(open("timeline.json")); LINES = TL["lines"]
def L(cue): return next(l for l in LINES if l["cue"] == cue)
def S(cue): return L(cue)["start"]
def E(cue): return L(cue)["end"]
DURATION = round(E("p2") + 2.6, 2)
GY = 1520; SC = 2.3
T_M1 = S("no") - 0.2          # whip: Tinku -> Mummy
T_RING = E("no") + 0.05       # phone rings
T_SKIP = E("call") + 0.35     # whip: time-skip, Tinku waiting at the study table
T_M2 = S("bye") - 0.3         # whip: Mummy still on the phone (night)
T_TK = S("p1") - 0.35         # whip: Tinku deadpan to camera
WHIPS = (T_M1, T_SKIP, T_M2, T_TK)

def prog(t, a, b): return clamp((t - a) / (b - a)) if b > a else float(t >= a)
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def lerp(a, b, x): return a + (b - a) * x
def blink(t, off): return ((t + off) % 3.6) < 0.12

NF = int(DURATION * FPS) + 2
MOUTH = {k: np.zeros(NF) for k in NAMES}
for l in LINES:
    x, sr = sf.read(l["file"]); hp = sr // FPS
    r = np.array([np.sqrt((x[i:i + hp] ** 2).mean()) for i in range(0, len(x) - hp, hp)])
    r = np.clip(r / (np.percentile(r, 90) + 1e-6), 0, 1.2)
    f0 = int(l["start"] * FPS); MOUTH[l["speaker"]][f0:f0 + len(r)] = r[:NF - f0]
def mo(spk, t):
    i = int(t * FPS); return float(MOUTH[spk][i]) if 0 <= i < NF else 0.0
def speaking(spk, t): return any(l["speaker"] == spk and l["start"] - 0.1 <= t <= l["end"] + 0.1 for l in LINES)
def talk(spk, t, seed=0.0):
    m = mo(spk, t); br = 0.03 * math.sin(t * 1.6 + seed)
    if not speaking(spk, t): return ((0.14 + br, 0.25), (0.14 - br, 0.25))
    return ((0.25 + 0.12 * math.sin(t * 0.9 + seed) + 0.1 * m, 0.5 + 0.4 * m), (0.55 + 0.25 * math.sin(t * 1.2 + seed) + 0.25 * m, 1.2 + 0.35 * math.sin(t * 1.8 + seed) + 0.3 * m))
HIP = (0.45, -1.1)

def night_k(t): return ease(prog(t, T_SKIP + 0.6, T_M2 - 0.6))

# ---------------------------------------------------------------- living room
def room(c, t):
    nk = night_k(t)
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgba(0, *(lerp(a, b, nk) for a, b in zip(hexc("#ffe9c7"), hexc("#7a6a9a"))))
    g.add_color_stop_rgba(1, *(lerp(a, b, nk) for a, b in zip(hexc("#ffd6a0"), hexc("#5a4a7a")))); c.set_source(g); c.paint()
    for k in range(12):   # wallpaper stripes
        c.rectangle(k * 96 + 30, 0, 36, GY - 180); setc(c, (1, 1, 1, 0.12 - 0.06 * nk)); c.fill()
    # window with sky: day -> sunset -> night
    wx, wy, ww, wh = 70, 560, 300, 340
    rrect(c, wx - 16, wy - 16, ww + 32, wh + 32, 10); fs(c, "#a86a32", "#5a3414", 4)
    sky = cairo.LinearGradient(0, wy, 0, wy + wh)
    top = [lerp(a, b, nk) for a, b in zip(hexc("#6ec6ff"), hexc("#0f1640"))]; bot = [lerp(a, b, nk) for a, b in zip(hexc("#cdeeff"), hexc("#3a2a6a"))]
    if 0.2 < nk < 0.8: bot = [lerp(a, b, math.sin(PI * (nk - 0.2) / 0.6)) for a, b in zip(bot, hexc("#ff9a4a"))]
    sky.add_color_stop_rgba(0, *top); sky.add_color_stop_rgba(1, *bot)
    c.rectangle(wx, wy, ww, wh); c.set_source(sky); c.fill()
    c.save(); c.rectangle(wx, wy, ww, wh); c.clip()
    sy = lerp(wy + 90, wy + wh + 60, clamp(nk * 1.6)); ell(c, wx + 200, sy, 40, 40); setc(c, "#ffd23f"); c.fill()   # sun sets
    my = lerp(wy + wh + 60, wy + 90, clamp(nk * 1.6 - 0.6)); ell(c, wx + 90, my, 34, 34); setc(c, "#fff6d0"); c.fill()  # moon rises
    ell(c, wx + 104, my - 8, 30, 30); setc(c, top); c.fill()
    for k in range(9):
        a = clamp(nk * 2 - 1) * (0.6 + 0.4 * math.sin(t * 3 + k))
        ell(c, wx + 30 + (k * 67) % 260, wy + 30 + (k * 41) % 180, 3, 3); setc(c, (1, 1, 1, a)); c.fill()
    c.restore()
    c.move_to(wx + ww / 2, wy); c.line_to(wx + ww / 2, wy + wh); c.move_to(wx, wy + wh / 2); c.line_to(wx + ww, wy + wh / 2)
    setc(c, "#a86a32"); c.set_line_width(12); c.stroke()
    # wall clock (hands spin during the time-skip)
    cx, cy = 880, 680; spin = ease(prog(t, T_SKIP + 0.3, T_M2 - 0.3)) * 2 * 2 * PI
    ell(c, cx, cy, 108, 108); fs(c, "#ffffff", "#c0283a", 10)
    for k in range(12):
        a = k * PI / 6; c.move_to(cx + 82 * math.sin(a), cy - 82 * math.cos(a)); c.line_to(cx + 94 * math.sin(a), cy - 94 * math.cos(a))
    setc(c, "#2b2d42"); c.set_line_width(5); c.stroke()
    ha = PI * 0.33 + spin / 12; ma = 0.0 + spin
    c.move_to(cx, cy); c.line_to(cx + 46 * math.sin(ha), cy - 46 * math.cos(ha)); setc(c, "#2b2d42"); c.set_line_width(9); c.stroke()
    c.move_to(cx, cy); c.line_to(cx + 72 * math.sin(ma), cy - 72 * math.cos(ma)); c.set_line_width(6); c.stroke()
    ell(c, cx, cy, 9, 9); setc(c, "#c0283a"); c.fill()
    # sofa (left) + lamp (right) + floor
    c.rectangle(0, GY - 160, W, 200); setc(c, (0.6, 0.4, 0.25, 1)); c.fill()   # skirting shadow
    c.rectangle(0, GY - 20, W, H - GY + 20); fs(c, lerp_hex("#c8875a", "#6a4a5a", nk));
    for k in range(7): c.move_to(0, GY + 20 + k * 64); c.line_to(W, GY + 20 + k * 64)
    setc(c, (0.35, 0.2, 0.1, 0.35)); c.set_line_width(3); c.stroke()
    rrect(c, -60, GY - 330, 300, 150, 40); fs(c, "#2f9e8f", "#1a6a5f", 5); rrect(c, -60, GY - 200, 340, 190, 30); fs(c, "#38b3a2", "#1a6a5f", 5)
    rrect(c, 230, GY - 250, 70, 240, 30); fs(c, "#2f9e8f", "#1a6a5f", 5)
    c.move_to(960, GY - 10); c.line_to(960, GY - 520); setc(c, "#5a3414"); c.set_line_width(10); c.stroke()
    poly(c, [(900, GY - 520), (1020, GY - 520), (990, GY - 640), (930, GY - 640)]); fs(c, "#ffcf6e", "#c98f00", 4)
    ell(c, 960, GY - 6, 60, 14); fs(c, "#5a3414")
    if nk > 0.4:
        rg = cairo.RadialGradient(960, GY - 560, 10, 960, GY - 560, 320); rg.add_color_stop_rgba(0, 1, 0.9, 0.5, 0.45 * nk); rg.add_color_stop_rgba(1, 1, 0.9, 0.5, 0)
        c.set_source(rg); c.paint()

def lerp_hex(a, b, k): return tuple(lerp(x, y, k) for x, y in zip(hexc(a), hexc(b)))

# ---------------------------------------------------------------- props
def phone(c, x, y, rot=0.0, s=1.0, ring=0.0):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    rrect(c, -30, -58, 60, 116, 12); fs(c, "#d6336c", "#7a1438", 3); rrect(c, -23, -46, 46, 88, 6); fs(c, "#5ac8ff")
    c.restore()
    if ring > 0:
        for k in range(3):
            r = 60 + k * 28 + 14 * math.sin(ring * 20); c.arc(x, y, r, -0.9, -0.2); c.arc_negative(x, y, r, PI + 0.9, PI + 0.2)
            c.new_sub_path()
            setc(c, (0.84, 0.2, 0.42, 0.8)); c.set_line_width(7); c.stroke()

def belan(c, x, y, rot):
    c.save(); c.translate(x, y); c.rotate(rot)
    rrect(c, -16, -120, 32, 240, 16); fs(c, "#e0a868", "#8a5228", 4)
    for sg in (-1, 1): rrect(c, -9, sg * 120 - (40 if sg < 0 else 0), 18, 40, 8); fs(c, "#c98a4e", "#8a5228", 3)
    c.restore()

def dupatta(c, x, y, s, hop, lean=0.0, angry=0.0):
    """Mummy disguise over Tinku: pink dupatta over the hair, bindi, jhumkas."""
    c.save(); c.translate(x, y - hop); c.scale(s, s); c.rotate(lean); c.translate(0, -275)
    c.move_to(-96, 40); c.curve_to(-118, -60, -80, -122, 0, -124); c.curve_to(80, -122, 118, -60, 96, 40)
    c.curve_to(110, 120, 120, 190, 92, 240); c.line_to(58, 240); c.curve_to(70, 170, 70, 100, 80, 30)
    c.curve_to(86, -40, 50, -96, 0, -98); c.curve_to(-50, -96, -86, -40, -80, 30)
    c.curve_to(-70, 100, -70, 170, -58, 240); c.line_to(-92, 240); c.curve_to(-120, 190, -110, 120, -96, 40); c.close_path()
    g = cairo.LinearGradient(0, -124, 0, 240); g.add_color_stop_rgba(0, *hexc("#ff6fa8")); g.add_color_stop_rgba(1, *hexc("#d6336c"))
    c.set_source(g); c.fill_preserve(); setc(c, "#8a1440"); c.set_line_width(3.5); c.stroke()
    c.move_to(-80, 30); c.curve_to(-86, -40, -50, -96, 0, -98); c.curve_to(50, -96, 86, -40, 80, 30)
    setc(c, "#ffd23f"); c.set_line_width(7); c.set_dash([10, 7]); c.stroke(); c.set_dash([])
    for k in range(5): ell(c, -30 + k * 15 + 0, -108 + abs(k - 2) * 3, 4, 4); setc(c, (1, 0.85, 0.3, 0.9)); c.fill()
    ell(c, 0, -46, 8, 8); fs(c, "#d81b1b", "#8a0000", 1.5)                                                    # bindi
    for sg in (-1, 1):                                                                                     # jhumkas
        c.move_to(sg * 82, 22); c.line_to(sg * 82, 34); setc(c, "#c98f00"); c.set_line_width(3); c.stroke()
        c.arc(sg * 82, 44, 11, PI, 2 * PI); c.close_path(); fs(c, "#ffd23f", "#c98f00", 2)
    if angry > 0:   # cross eyebrows
        for sg in (-1, 1):
            c.move_to(sg * 58, -50 - 6 * angry); c.line_to(sg * 12, -34 + 4 * angry)
        setc(c, "#3a2414"); c.set_line_width(9); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()
    c.restore()

def cobweb(c, hx, hy, k, t):
    """A cobweb from the top of Tinku's head up to the lamp — he has been waiting that long."""
    if k <= 0: return
    ax, ay = 940, GY - 640
    n = int(1 + 5 * k)
    for i in range(n):
        f = (i + 1) / 6
        c.move_to(hx - 20 + i * 8, hy - 10); c.curve_to(lerp(hx, ax, 0.3), lerp(hy, ay, 0.3) + 40 * f, lerp(hx, ax, 0.7), lerp(hy, ay, 0.7) + 30 * f, ax - 20 + i * 6, ay + 4)
    setc(c, (1, 1, 1, 0.75 * k)); c.set_line_width(2.5); c.stroke()
    cx_, cy_ = lerp(hx, ax, 0.55), lerp(hy, ay, 0.55)                     # little web disc + spider
    for r in (24, 44, 64):
        c.arc(cx_, cy_, r * k, 0, 2 * PI); setc(c, (1, 1, 1, 0.55 * k)); c.set_line_width(2); c.stroke()
    for a in range(8):
        c.move_to(cx_, cy_); c.line_to(cx_ + 70 * k * math.cos(a * PI / 4), cy_ + 70 * k * math.sin(a * PI / 4))
    c.stroke()
    sx, sy = cx_ + 10, cy_ + 20 + 30 * math.sin(t * 2)
    c.move_to(cx_ + 10, cy_); c.line_to(sx, sy); c.stroke()
    ell(c, sx, sy, 12 * k, 10 * k); setc(c, "#2b2d42"); c.fill()
    for sg in (-1, 1):
        for j in range(3): c.move_to(sx, sy); c.line_to(sx + sg * 20 * k, sy - 8 + j * 8)
    c.set_line_width(2.5); c.stroke()

def study_table(c, t):
    rrect(c, 160, GY - 400, 760, 40, 10); fs(c, "#b8763e", "#5a3414", 4)
    rrect(c, 180, GY - 362, 720, 362, 6); fs(c, "#a86a32", "#5a3414", 4)
    rrect(c, 230, GY - 320, 280, 120, 8); fs(c, "#c8864e", "#5a3414", 3); ell(c, 370, GY - 260, 14, 8); setc(c, "#5a3414"); c.fill()
    for k, (col, w) in enumerate((("#2f7bff", 170), ("#ff4f5f", 150), ("#2fbf4a", 180), ("#ffd23f", 140))):   # stack of books
        rrect(c, 700 - w / 2 + (k % 2) * 10, GY - 440 - k * 34, w, 32, 5); fs(c, col, dark(col, 0.6), 3)
    poly(c, [(250, GY - 402), (430, GY - 402), (440, GY - 420), (240, GY - 420)]); fs(c, "#ffffff", "#9aa0b0", 3)  # open notebook

def whip(c, t):
    for T in WHIPS:
        k = 1 - abs(t - T) / 0.18
        if k > 0:
            c.rectangle(0, 0, W, H); setc(c, (1, 1, 1, 0.55 * k)); c.fill()
            for i in range(26):
                y = (i * 77 + 31) % H; ln = 300 + (i * 131) % 500; x = ((i * 397) % W) - ln / 2
                rrect(c, x, y, ln, 10 + i % 3 * 6, 6); setc(c, (1, 1, 1, 0.8 * k)); c.fill()

def skip_card(c, t):
    a = ease(prog(t, T_SKIP + 0.2, T_SKIP + 0.5)) * (1 - ease(prog(t, T_M2 - 0.5, T_M2 - 0.25)))
    if a <= 0: return
    bob = 8 * math.sin(t * 3)
    c.push_group()
    rrect(c, 150, 300 + bob, 780, 210, 50); fs(c, "#2b2d42", "#ffd23f", 10)
    draw_text(c, "2 घंटे बाद…", 540, 370 + bob, 80, "#ffd23f", None, 0, lang="hi")
    draw_text(c, "2 hours later...", 540, 460 + bob, 56, "#ffffff", None, 0, lang="en")
    c.pop_group_to_source(); c.paint_with_alpha(a)

def captions(c, t):
    if T_SKIP + 0.1 < t < T_M2 - 0.1: return
    cur = None
    for i, l in enumerate(LINES):
        nxt = LINES[i + 1]["start"] if i + 1 < len(LINES) else 1e9
        if l["start"] - 0.12 <= t <= min(l["end"] + 0.6, nxt - 0.12): cur = l
    if not cur: return
    a = clamp((t - cur["start"] + 0.12) / 0.15)
    name, col = NAMES[cur["speaker"]]
    c.select_font_face("Fredoka", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); c.set_font_size(62)
    words = cur["en"].split(); lines, curl = [], ""
    for w in words:
        cand = (curl + " " + w).strip()
        if c.text_extents(cand).x_advance <= 900 or not curl: curl = cand
        else: lines.append(curl); curl = w
    lines.append(curl)
    lh = 78; bh = 50 + lh * len(lines); bx, bw, by = 60, 960, 290
    c.push_group()
    rrect(c, bx + 5, by + 8, bw, bh, 40); setc(c, (0.1, 0.05, 0.2, 0.25)); c.fill()
    rrect(c, bx, by, bw, bh, 40); fs(c, (1, 1, 1, 0.97), hexc(col), 9)
    nw = text_surface(name, 40, "#ffffff", None, 0, "hi").get_width()
    rrect(c, bx + 40, by - 38, nw + 44, 66, 33); fs(c, col, (1, 1, 1, 1), 5)
    draw_text(c, name, bx + 62, by - 5, 40, "#ffffff", None, 0, lang="hi", anchor="l")
    c.select_font_face("Fredoka", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); c.set_font_size(62)
    for i, ln in enumerate(lines):
        c.move_to(W / 2 - c.text_extents(ln).x_advance / 2, by + 25 + lh * 0.75 + i * lh); setc(c, "#2b2d42"); c.show_text(ln)
    c.pop_group_to_source(); c.paint_with_alpha(a)

# ---------------------------------------------------------------- shots
def shot(t):
    if t < T_M1: return "ask"
    if t < T_SKIP: return "mummy"
    if t < T_M2: return "wait"
    if t < T_TK: return "mummy2"
    return "deadpan"

def frame(t, surf):
    c = cairo.Context(surf); sh = shot(t)
    # camera
    z, fx, fy = 1.0, 540, 1000
    if sh == "ask": z = 1.0 + 0.05 * ease(prog(t, 0, T_M1))
    if sh == "mummy" and t > T_RING: z = 1.0 + 0.08 * ease(prog(t, S("call"), S("call") + 0.6)); fx, fy = 540, 900
    if sh == "mummy" and t < T_RING: z = 1.12 + 0.03 * math.sin(t * 20) * prog(t, S("no"), S("no") + 0.3) * (1 - prog(t, E("no") - 0.2, E("no")))   # angry shake
    if sh == "wait": z = 1.0 + 0.06 * ease(prog(t, T_SKIP, T_M2))
    if sh == "mummy2": z = 1.08
    if sh == "deadpan":
        z = lerp(1.15, 1.45, ease(prog(t, T_TK, S("p2") - 0.3))); fy = 860
        z += 0.25 * ease(prog(t, S("p2") + 1.0, S("p2") + 1.25))   # punch-in on "TWO HOURS"
    c.save(); c.translate(540, 1000); c.scale(z, z); c.translate(-fx, -fy)
    room(c, t)
    x = 540; hop = 0.0; lean = 0.0; look = 0.0
    if sh == "ask":
        a = ((0.35, -2.3), (0.35, -2.3))   # hands pressed together, pleading
        hop = abs(math.sin(t * 5)) * 10
        hands = tinku(c, x, GY, t, SC, a, mo("tinku", t), 0.0, blink(t, 0.2), hop, 0.03 * math.sin(t * 5))
        rrect(c, 720, GY - 140, 130, 130, 18); fs(c, "#ff4f5f", "#a01a2a", 4)    # toy block + ball beside him
        ell(c, 210, GY - 50, 50, 50); fs(c, "#2f7bff", "#1a3f8a", 4); c.move_to(165, GY - 60); c.curve_to(200, GY - 30, 230, GY - 30, 258, GY - 60); setc(c, "#ffffff"); c.set_line_width(5); c.stroke()
    elif sh in ("mummy", "mummy2"):
        on_phone = sh == "mummy2" or t > T_RING + 0.5
        m = mo("mummy", t)
        if not on_phone:
            ar = talk("mummy", t, 1.0); a = (HIP, (1.3 + 0.5 * m, 0.9 + 0.4 * math.sin(t * 9)))     # wagging the rolling pin
            lean = -0.04
        else:
            a = (HIP if sh == "mummy" else (0.3 + 0.2 * m, 0.6 + 0.3 * m), (2.75, 2.0)); lean = 0.05 * math.sin(t * 1.4) + 0.04
        hands = tinku(c, x, GY, t, SC, a, m, 0.4 if on_phone else 0.0, blink(t, 0.6) or (on_phone and m < 0.05 and int(t * 2) % 5 == 0), 0.0, lean)
        dupatta(c, x, GY, SC, 0.0, lean, 0.0 if on_phone else 1.0)
        hx, hy = hands[1]
        if not on_phone:
            belan(c, hx, hy - 30, 0.5 + 0.4 * math.sin(t * 9))
            if t > T_RING: phone(c, 860, GY - 560, 0, 1.0, t)   # phone ringing on the lamp table
            if t > T_RING: rrect(c, 790, GY - 500, 140, 20, 6); fs(c, "#5a3414")
        else:
            phone(c, hx + 24, hy - 70, 0.25)
            for k in range(3):   # happy chatter sparkles
                ph = (t * 1.4 + k / 3) % 1
                ell(c, 760 + k * 40, 700 - ph * 120, 8 * (1 - ph) + 2, 8 * (1 - ph) + 2); setc(c, (1, 0.4, 0.65, 1 - ph)); c.fill()
    elif sh == "wait":
        droop = ease(prog(t, T_SKIP + 0.8, T_M2 - 0.8))
        c.save(); c.rectangle(0, 0, W, GY - 380); c.clip()
        hands = tinku(c, x, GY, t, SC, ((0.5, -0.4), (0.5, -0.4)), 0.0, -0.3 * (1 - droop), droop > 0.7 or blink(t, 0.1), -70 * droop, 0.08 * droop)
        c.restore()
        study_table(c, t)
        cobweb(c, x + 40, GY + 70 * droop - 275 * SC - 180, ease(prog(t, T_SKIP + 1.0, T_M2 - 0.4)), t)
    else:
        a = ((0.18, 0.2), (0.18, 0.2)) if t < S("p2") + 0.9 else ((0.6, -1.4), (0.6, -1.4))
        hop = abs(math.sin(t * 8)) * 10 if t > S("p2") + 1.0 else 0.0
        tinku(c, x, GY, t, SC, a, mo("tinku", t), 0.0, blink(t, 0.4) or (t > S("p2") + 1.0 and int(t * 4) % 3 == 0), hop, 0.0)
        cobweb(c, x + 40, GY - hop - 275 * SC - 180, 1.0, t)   # the cobweb is still on his head
    c.restore()
    skip_card(c, t)
    captions(c, t)
    whip(c, t)
    f = clamp((DURATION - t) / 0.8)
    if f < 1: c.rectangle(0, 0, W, H); setc(c, (0, 0, 0, 1 - f)); c.fill()
    return surf

# ---------------------------------------------------------------- audio
SR = 48000; N = int(DURATION * SR); rng = np.random.default_rng(5)
def add(buf, x, t, g=1.0):
    i = int(t * SR)
    if 0 <= i < N: x = x[: N - i]; buf[i:i + len(x)] += g * x
def hz(m): return 440.0 * 2 ** ((m - 69) / 12)
def env(n, a=0.005, d=0.3): tt = np.arange(n) / SR; return np.minimum(1, tt / a) * np.exp(-tt / d)
def pluck(m, dur=0.8, decay=0.35):
    f = hz(m); p = int(SR / f); n = int(dur * SR); b = rng.uniform(-1, 1, p); out = np.zeros(n)
    for i in range(n): out[i] = b[i % p]; b[i % p] = 0.996 * 0.5 * (b[i % p] + b[(i + 1) % p])
    return out * np.exp(-np.arange(n) / SR / decay)
def make_audio():
    music = np.zeros(N); sfx = np.zeros(N); voice = np.zeros(N)
    B = 60 / 112; chords = [[60, 64, 67], [57, 60, 64], [53, 57, 60], [55, 59, 62]]; cache = {}
    def tempo_at(tt): return 3.0 if T_SKIP + 0.3 < tt < T_M2 - 0.3 else 1.0   # music races during the time-skip
    tt, bar = 0.0, 0
    while tt < DURATION:
        ch = chords[bar % 4]; sp = tempo_at(tt)
        if not (T_RING - 0.1 < tt < S("call")):
            for s in (0, 1, 1.5, 2.5, 3):
                for j, m_ in enumerate(ch):
                    if m_ not in cache: cache[m_] = pluck(m_)
                    add(music, cache[m_], tt + s * B / sp + j * 0.012, 0.12)
            bt = np.arange(int(B * SR)) / SR; add(music, np.sin(2 * np.pi * hz(ch[0] - 24) * bt) * env(len(bt), 0.01, 0.3), tt, 0.4)
        tt += 4 * B / sp; bar += 1
    for k in range(int((T_M2 - T_SKIP) * 2)):   # fast clock ticking
        n = int(0.03 * SR); add(sfx, sosfilt(butter(2, [2000, 6000], btype="band", fs=SR, output="sos"), rng.uniform(-1, 1, n)) * env(n, 0.001, 0.01), T_SKIP + 0.3 + k * 0.5, 0.5)
    for k in range(2):   # phone ring
        n = int(0.4 * SR); x_ = np.arange(n) / SR
        r = (np.sin(2 * np.pi * 1300 * x_) + np.sin(2 * np.pi * 1700 * x_)) * (np.sin(2 * np.pi * 20 * x_) > 0) * np.minimum(1, (0.4 - x_) / 0.02)
        add(sfx, r, T_RING + k * 0.5, 0.12)
    def whoosh(t):
        n = int(0.35 * SR); x_ = np.arange(n) / SR
        w = sosfilt(butter(2, [600, 4000], btype="band", fs=SR, output="sos"), rng.uniform(-1, 1, n)) * np.sin(np.pi * x_ / 0.35) ** 2
        add(sfx, w, t - 0.17, 0.35)
    for T in WHIPS: whoosh(T)
    def rimshot(t):
        n = int(0.12 * SR); add(sfx, np.sin(2 * np.pi * 180 * np.arange(n) / SR) * env(n, 0.002, 0.05), t, 0.6)
        n = int(0.5 * SR); add(sfx, sosfilt(butter(2, [3000, 12000], btype="band", fs=SR, output="sos"), rng.uniform(-1, 1, n)) * env(n, 0.002, 0.18), t + 0.18, 0.5)
    def laugh(t, d=2.2, g=0.14):
        for k in range(int(d * 9)):
            n = int(0.11 * SR); tt_ = np.arange(n) / SR; f = rng.uniform(380, 620)
            x = (np.sin(2 * np.pi * f * tt_) + 0.5 * np.sin(4 * np.pi * f * tt_)) * np.sin(np.pi * tt_ / 0.11) * rng.uniform(0.4, 1)
            add(sfx, sosfilt(butter(2, [300, 2500], btype="band", fs=SR, output="sos"), x + 0.3 * rng.uniform(-1, 1, n)), t + k / 9 + rng.uniform(0, 0.04), g)
    laugh(E("bye") + 0.1, 1.2, 0.08)          # small chuckle at "the rest tomorrow, in just five minutes"
    rimshot(E("p2") + 0.05); laugh(E("p2") + 0.2, 2.4, 0.16)
    for l in LINES:
        x, sr = sf.read(l["file"]); add(voice, resample_poly(x, SR, sr), l["start"])
    sp = np.zeros(N, bool)
    for l in LINES: sp[int(l["start"] * SR):int(l["end"] * SR)] = True
    k_ = int(0.12 * SR); duck = np.convolve(np.where(sp, 0.35, 1.0), np.ones(k_) / k_, "same")
    fade = np.ones(N); fl = int(1.0 * SR); fade[-fl:] = np.linspace(1, 0, fl)
    mix = np.tanh((voice + music * 0.6 * duck + sfx * 0.8) * fade * 1.1) * 0.9
    os.makedirs("audio", exist_ok=True); sf.write("audio/mix.wav", np.stack([mix, mix], 1), SR, subtype="PCM_16")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        os.makedirs("stills", exist_ok=True)
        for ts in sys.argv[1:]:
            s_ = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); frame(float(ts), s_); s_.write_to_png(f"stills/r_{float(ts):05.2f}.png")
        sys.exit()
    make_audio()
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", "audio/mix.wav",
                          "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "19", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                          "-shortest", "-movflags", "+faststart", "reel.mp4"], stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    for f in range(int(DURATION * FPS)):
        frame(f / FPS, surf); surf.flush(); p.stdin.write(bytes(surf.get_data()))
    p.stdin.close(); p.wait(); print("reel ok", DURATION)
