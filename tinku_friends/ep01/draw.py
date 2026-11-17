import sys, os, math, random, numpy as np, soundfile as sf, cairo
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "mahabharat", "lib"))
from chars import *
from scenery import park_bg
from cues import *
from script import NAMES, ITEMS, EP_NUM, EP_TITLE, NEXT

W, H, FPS = 1280, 720, 30
GY = 612

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
def active(t, cue, pre=0.0, post=0.0): return has(cue) and S(cue) - pre <= t <= E(cue) + post
def blink(t, off): return ((t + off) % 3.6) < 0.12
def hop(t, t0, h=40, d=0.45): return h * math.sin(PI * (t - t0) / d) if t0 <= t <= t0 + d else 0.0

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

# ---------------- counting icons
def icon(c, kind, x, y, s, t, k=0):
    c.save(); c.translate(x, y + 4 * math.sin(t * 3 + k)); c.scale(s, s)
    if kind == "sun":
        c.save(); c.rotate(t * 0.4)
        for i in range(12): c.save(); c.rotate(i * PI / 6); poly(c, [(-9, -46), (0, -66), (9, -46)]); setc(c, "#ffc21a"); c.fill(); c.restore()
        c.restore(); ell(c, 0, 0, 44, 44); fs(c, "#ffdc2e", "#ffb000", 4)
        c.set_line_width(4); setc(c, "#a35b00"); c.set_line_cap(cairo.LINE_CAP_ROUND)
        for ex in (-15, 15): c.arc(ex, -4, 7, 1.15 * PI, 1.85 * PI); c.stroke()
        c.arc(0, 8, 15, 0.15 * PI, 0.85 * PI); c.stroke()
    elif kind == "balloon":
        c.move_to(0, 40); c.curve_to(8, 60, -8, 70, 4, 90); setc(c, "#777777"); c.set_line_width(2); c.stroke()
        ell(c, 0, 0, 32, 40); fs(c, "#ff3b4b", "#b8202e", 3); poly(c, [(-6, 42), (0, 36), (6, 42)]); setc(c, "#b8202e"); c.fill()
        ell(c, -11, -14, 7, 12); setc(c, (1, 1, 1, 0.55)); c.fill()
    elif kind == "apple":
        ell(c, -12, 4, 26, 30); fs(c, "#ff3b3b", "#b81e1e", 3); ell(c, 12, 4, 26, 30); fs(c, "#ff3b3b", "#b81e1e", 3)
        ell(c, 0, 6, 30, 30); setc(c, "#ff3b3b"); c.fill()
        c.move_to(0, -24); c.curve_to(2, -34, 4, -40, 6, -44); setc(c, "#7a4a24"); c.set_line_width(4); c.stroke()
        c.save(); c.translate(10, -36); c.rotate(-0.5); ell(c, 10, 0, 13, 6); fs(c, "#3fae4a", "#2a7a33", 2); c.restore()
        ell(c, -14, -6, 6, 10); setc(c, (1, 1, 1, 0.5)); c.fill()
    elif kind == "star":
        pts = [((42 if i % 2 == 0 else 18) * math.cos(-PI / 2 + i * PI / 5), (42 if i % 2 == 0 else 18) * math.sin(-PI / 2 + i * PI / 5)) for i in range(10)]
        poly(c, pts); fs(c, "#ffe066", "#f5a400", 3)
        setc(c, "#a35b00"); ell(c, -8, -2, 3, 4); c.fill(); ell(c, 8, -2, 3, 4); c.fill(); c.arc(0, 4, 6, 0.15 * PI, 0.85 * PI); c.set_line_width(2.5); c.stroke()
    elif kind == "fish":
        c.rotate(0.08 * math.sin(t * 4 + k))
        poly(c, [(26, 0), (52, -22), (48, 0), (52, 22)]); fs(c, "#ff8c1a", "#c25e00", 3)
        ell(c, 0, 0, 34, 22); fs(c, "#ffa53b", "#c25e00", 3)
        for sx in (-6, 6): c.arc(sx, 0, 10, -0.4 * PI, 0.4 * PI); setc(c, (1, 1, 1, 0.5)); c.set_line_width(2); c.stroke()
        ell(c, -18, -5, 6, 6); fs(c, "#ffffff", "#333333", 1.5); ell(c, -19, -5, 3, 3); setc(c, "#222222"); c.fill()
    elif kind == "flower":
        c.move_to(0, 10); c.line_to(0, 60); setc(c, "#3fae4a"); c.set_line_width(5); c.stroke()
        c.save(); c.translate(6, 42); c.rotate(-0.6); ell(c, 10, 0, 12, 6); fs(c, "#4cd964", "#2a7a33", 2); c.restore()
        col = ["#ff5f8f", "#a04dff", "#ff8c1a", "#2f7bff", "#ff3b3b", "#ffd23f"][k % 6]
        for i in range(6): ell(c, 20 * math.cos(i * PI / 3), 20 * math.sin(i * PI / 3), 14, 14); fs(c, col, dark(col, 0.7), 2)
        ell(c, 0, 0, 12, 12); fs(c, "#ffe066", "#e0a000", 2)
    elif kind == "butterfly":
        f = abs(math.sin(t * 9 + k))
        for sgn in (-1, 1):
            c.save(); c.scale(sgn * (0.4 + 0.6 * f), 1)
            ell(c, 22, -12, 24, 20); fs(c, ["#ff7ab0", "#2f7bff", "#ffb000", "#a04dff"][k % 4], "#5b3a7a", 2.5)
            ell(c, 18, 14, 15, 13); fs(c, "#ffd23f", "#5b3a7a", 2.5); c.restore()
        rrect(c, -4, -22, 8, 42, 4); setc(c, "#5b3a7a"); c.fill()
    elif kind == "cupcake":
        poly(c, [(-28, 0), (28, 0), (20, 38), (-20, 38)]); fs(c, "#ff8fc7", "#d9407c", 3)
        for i in range(-2, 3): c.move_to(i * 10, 2); c.line_to(i * 8, 36)
        setc(c, "#d9407c"); c.set_line_width(2); c.stroke()
        for dx, dy, r in ((-18, -4, 16), (18, -4, 16), (0, -14, 20), (0, -30, 13)): ell(c, dx, dy, r, r * 0.8); fs(c, "#fff3f8", "#e8b8cc", 2)
        ell(c, 0, -44, 8, 8); fs(c, "#e8322f", "#a01a18", 2)
        for i in range(6): ell(c, -16 + i * 7, -10 + (i % 2) * 8, 2.5, 1.4); setc(c, ["#2f7bff", "#3fae4a", "#ffb000"][i % 3]); c.fill()
    elif kind == "bubble":
        g = cairo.RadialGradient(-10, -10, 2, 0, 0, 38); g.add_color_stop_rgba(0, 1, 1, 1, 0.5); g.add_color_stop_rgba(0.8, 0.6, 0.85, 1, 0.25); g.add_color_stop_rgba(1, 0.5, 0.6, 1, 0.6)
        c.set_source(g); c.arc(0, 0, 36, 0, 2 * PI); c.fill(); c.arc(0, 0, 36, 0, 2 * PI); setc(c, (0.5, 0.7, 1, 0.8)); c.set_line_width(2.5); c.stroke()
        ell(c, -14, -14, 9, 5); setc(c, (1, 1, 1, 0.85)); c.fill()
    c.restore()

def hand(c, x, y, s, fingers_up, mirror=1):
    c.save(); c.translate(x, y); c.scale(s * mirror, s)
    rrect(c, -40, -20, 80, 70, 26); fs(c, "#f3c39f", "#b98a64", 3)
    for i in range(5):
        up = i < fingers_up
        fx = -32 + i * 16 if i < 4 else 46; ang = 0 if i < 4 else 0.9
        L = (60 if i in (1, 2) else 52 if i in (0, 3) else 40) if up else 18
        c.save(); c.translate(fx if i < 4 else 34, -16 if i < 4 else 10); c.rotate(ang)
        rrect(c, -8, -L, 16, L + 8, 8); fs(c, "#f3c39f", "#b98a64", 3)
        if up: ell(c, 0, -L + 7, 5, 4); setc(c, (1, 0.9, 0.9, 0.8)); c.fill()
        c.restore()
    c.restore()

def item_layout(n):
    cols = n if n <= 3 else (2 if n == 4 else 3 if n <= 6 else 4 if n <= 8 else 5)
    rows = (n + cols - 1) // cols
    pos = []
    for i in range(n):
        r_, c_ = divmod(i, cols)
        in_row = min(cols, n - r_ * cols)
        x = 1025 + (c_ - (in_row - 1) / 2) * (min(130, 340 / cols) if cols > 1 else 0)
        y = 290 + (r_ - (rows - 1) / 2) * 140
        pos.append((x, y))
    return pos

NUM_COL = ["#ff3b3b", "#ff8c1a", "#ffb000", "#3fae4a", "#14a3a3", "#2f7bff", "#7a3fbf", "#d81b60", "#e8432f", "#2f9a47"]

def board(c, t):
    p = back(prog(t, T_COUNT, T_COUNT + 0.6)) * (1 - ease(prog(t, S("next") - 0.2, S("next") + 0.4)))
    if p <= 0: return
    c.save(); c.translate(950, 290); c.scale(p, p); c.translate(-950, -290)
    rrect(c, 668, 66, 572, 452, 34); setc(c, (0, 0, 0, 0.12)); c.fill()
    rrect(c, 660, 56, 572, 452, 34); fs(c, "#fffdf5", "#ffb000", 8)
    cur = 0
    for n in range(1, 11):
        if t >= S(f"n{n}") - 0.3: cur = n
    if t >= S("again") - 0.3:
        for k, tp in enumerate(FAST):
            q = back(prog(t, tp, tp + 0.3))
            if q <= 0: continue
            r_, c_ = divmod(k, 5)
            c.save(); c.translate(760 + c_ * 100, 200 + r_ * 170); c.scale(q, q)
            ell(c, 0, 0, 44, 44); fs(c, NUM_COL[k], dark(NUM_COL[k], 0.7), 4)
            draw_text(c, str(k + 1), 0, 2, 52, "#ffffff", None, 0, lang="en"); c.restore()
        draw_text(c, "Count with us!", 946, 470, 34, "#7c2d12", lang="en")
    elif cur:
        n = cur; num_col = NUM_COL[n - 1]
        q = back(prog(t, S(f"n{n}") - 0.3, S(f"n{n}") + 0.2))
        c.save(); c.translate(760, 210); c.scale(q, q)
        draw_text(c, str(n), 0, 0, 170, num_col, "#ffffff", 10, lang="en")
        c.restore()
        draw_text(c, NUMW[n - 1].capitalize(), 760, 350, 46, dark(num_col, 0.85), lang="en")
        kind = ITEMS[n - 1][2]
        if kind == "finger":
            k_up = sum(1 for tp in POP[n] if t >= tp)
            hand(c, 960, 330, 1.2, min(5, k_up), -1); hand(c, 1130, 330, 1.2, max(0, k_up - 5), 1)
        else:
            sz = 1.15 if n <= 3 else 1.0 if n <= 6 else 0.86
            for k, (x, y) in enumerate(item_layout(n)):
                tp = POP[n][k] if k < len(POP[n]) else POP[n][-1]
                qq = back(prog(t, tp, tp + 0.35))
                if qq > 0: icon(c, kind, x, y, sz * qq, t, k)
                if 0 <= t - tp < 0.8 and n > 1:
                    draw_text(c, str(k + 1), x + 34 * sz, y - 44 * sz, 30, NUM_COL[k], "#ffffff", 4, lang="en", alpha=clamp(1 - (t - tp) / 0.8))
        if active(t, f"e{n}", 0.1, 0.4):
            pulse = 1 + 0.15 * math.sin(PI * prog(t, S(f"e{n}"), E(f"e{n}")))
            c.arc(760, 210, 92 * pulse, 0, 2 * PI); setc(c, hexc(num_col, 0.35)); c.set_line_width(10); c.stroke()
    c.restore()

def gang(c, t):
    spread = ease(prog(t, T_COUNT - 0.2, T_COUNT + 1.0)) * (1 - ease(prog(t, S("next") - 0.4, S("next") + 0.8)))
    xs = {"tinku": lerp(330, 130, spread), "pinky": lerp(560, 300, spread), "golu": lerp(780, 465, spread), "moti": lerp(990, 585, spread)}
    fast = active(t, "fast", 0, 0.5) or active(t, "moti_cheer", 0, 0.5)
    def pose(spk, seed):
        a = list(talk(spk, t, seed)); h = 0
        if fast: a = [(2.2, 0.6), (2.2, 0.6)]; h = abs(math.sin(t * 7 + seed)) * 26
        if active(t, "n10", 0, 1.5) or active(t, "e10", 0, 0.5): a = [(2.0, 0.3), (2.0, 0.3)]
        if active(t, "bye1", 0, 3) or active(t, "bye2", 0, 3): a[1] = (2.1, 0.5 + 0.5 * math.sin(t * 11 + seed)); h = abs(math.sin(t * 5 + seed)) * 10
        for n in range(1, 11):
            if active(t, f"e{n}", 0, 0.2) and ITEMS[n - 1][1] != spk: a = [a[0], (1.7, 1.0)]
        return tuple(a), h
    look_board = 0.6 if spread > 0.5 else 0.0
    a, h = pose("tinku", 0.3); tinku(c, xs["tinku"], GY, t, 0.88, a, mo("tinku", t), look_board, blink(t, 0.3), h)
    a, h = pose("pinky", 1.1); pinky(c, xs["pinky"], GY, t, 0.88, a, mo("pinky", t), look_board, blink(t, 1.4), h)
    a, h = pose("golu", 2.2); golu(c, xs["golu"], GY, t, 0.88, a, mo("golu", t), look_board, blink(t, 2.2), h)
    mh = (abs(math.sin(t * 8)) * 20 if active(t, "moti_cheer", 0, 0.6) else 0)
    moti(c, xs["moti"], GY, t, 0.78, mo("moti", t), 0.3, blink(t, 0.9), mh, 1.0 + 1.5 * speaking("moti", t))

def park(c, t):
    park_bg(c, t)
    if active(t, "next", 0, 1.5):
        p = ease(prog(t, S("next") + 0.2, S("next") + 1.4))
        c.save(); c.move_to(640, 470); c.arc(640, 470, 700, PI, PI + PI * p); c.close_path(); c.clip()
        for i, col in enumerate(["#ff3b3b", "#ff8c1a", "#ffd60a", "#4cd964", "#2f7bff", "#7a3fbf"]):
            c.arc(640, 470, 400 - i * 24, PI, 2 * PI); setc(c, hexc(col, 0.8)); c.set_line_width(24); c.stroke()
        c.restore()
    board(c, t)
    gang(c, t)
    if active(t, "moti_cheer", 0, 1.2):
        r = random.Random(3)
        for k in range(50):
            x0 = r.uniform(0, W); dt = t - S("moti_cheer"); y = -20 + dt * r.uniform(200, 380); x = x0 + 20 * math.sin(dt * 3 + k)
            c.save(); c.translate(x, y); c.rotate(dt * 4 + k); rrect(c, -6, -3, 12, 6, 2); setc(c, NUM_COL[k % 10]); c.fill(); c.restore()

def title_card(c, t):
    gr = cairo.RadialGradient(640, 380, 40, 640, 380, 900); gr.add_color_stop_rgba(0, *hexc("#fff6a8")); gr.add_color_stop_rgba(1, *hexc("#4fb8ff")); c.set_source(gr); c.paint()
    c.save(); c.translate(640, 380); c.rotate(t * 0.12)
    for i in range(18): c.move_to(0, 0); c.arc(0, 0, 1200, i * PI / 9, i * PI / 9 + PI / 18); c.close_path(); setc(c, (1, 1, 1, 0.18)); c.fill()
    c.restore()
    p = back(prog(t, 0.2, 0.8))
    if p > 0:
        c.save(); c.translate(640, 150); c.scale(p, p); draw_text(c, "Tinku & Friends", 0, 0, 104, "#ff6b1a", "#ffffff", 11, lang="en"); c.restore()
    p2 = back(prog(t, 0.8, 1.3))
    if p2 > 0:
        c.save(); c.translate(640, 270); c.scale(p2, p2)
        rrect(c, -300, -40, 600, 80, 40); fs(c, "#2f7bff", "#ffffff", 6)
        draw_text(c, f"Episode {EP_NUM} · {EP_TITLE}", 0, 0, 38, "#ffffff", lang="en"); c.restore()
    for i, (fn, x) in enumerate(((tinku, 330), (pinky, 540), (golu, 740))):
        q = back(prog(t, 1.0 + i * 0.2, 1.5 + i * 0.2))
        fn(c, x, 900 - 280 * q, t, 0.8, ((0.15, 0.3), (2.1, 0.5 + 0.5 * math.sin(t * 10 + i))), mo("tinku", t) if fn is tinku else 0, 0, blink(t, i))
    q = back(prog(t, 1.6, 2.1)); moti(c, 940, 860 - 240 * q, t, 0.8, 0, -0.3, False, abs(math.sin(t * 6)) * 12, 2.0)

def outro_card(c, t):
    lt = t - T_OUTRO
    gr = cairo.RadialGradient(640, 380, 40, 640, 380, 900); gr.add_color_stop_rgba(0, *hexc("#fff3c4")); gr.add_color_stop_rgba(1, *hexc("#ff9fcf")); c.set_source(gr); c.paint()
    r = random.Random(5)
    for k in range(60):
        x0 = r.uniform(0, W); sp = r.uniform(60, 130); ph = r.uniform(0, 800)
        y = (ph + lt * sp) % 800 - 40; x = x0 + 20 * math.sin(lt * 2 + k)
        c.save(); c.translate(x, y); c.rotate(lt * 2 + k); rrect(c, -6, -3, 12, 6, 2); setc(c, NUM_COL[k % 10]); c.fill(); c.restore()
    p = back(prog(lt, 0.2, 0.8))
    if p > 0: c.save(); c.translate(640, 150); c.scale(p, p); draw_text(c, "Bye-bye!", 0, 0, 130, "#d81b60", "#ffffff", 12, lang="en"); c.restore()
    p2 = back(prog(lt, 0.8, 1.3))
    if p2 > 0:
        c.save(); c.translate(640, 270); c.scale(p2, p2); draw_text(c, "See you next time!", 0, 0, 46, "#7c2d12", "#ffffff", 5, lang="en")
        draw_text(c, NEXT, 0, 56, 34, "#2f7bff", "#ffffff", 4, lang="en"); c.restore()
    for i, (fn, x) in enumerate(((tinku, 330), (pinky, 540), (golu, 740))):
        fn(c, x, 680, t, 0.8, ((0.15, 0.3), (2.1, 0.5 + 0.5 * math.sin(t * 10 + i))), 0, 0, blink(t, i), abs(math.sin(t * 5 + i)) * 12)
    moti(c, 940, 680, t, 0.8, 0, -0.3, False, abs(math.sin(t * 6)) * 12, 2.0)

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
    nw = text_surface(name, 24, "#ffffff", None, 0, "en").get_width()
    rrect(c, bx + 18, by - 22, nw + 24, 38, 19); fs(c, col, (1, 1, 1, 1), 3)
    draw_text(c, name, bx + 30, by - 3, 24, "#ffffff", None, 0, lang="en", anchor="l")
    c.select_font_face("Fredoka", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); c.set_font_size(34)
    c.move_to(640 - tw / 2, by + 41); setc(c, "#2b2d42"); c.show_text(txt)
    c.pop_group_to_source(); c.paint_with_alpha(a)

def frame(t, surf=None):
    surf = surf or cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(surf)
    def iris(t0, A, B):
        p = ease(prog(t, t0, t0 + 0.8))
        if p <= 0: A(c, t); return
        if p >= 1: B(c, t); return
        A(c, t); c.save(); c.arc(640, 360, 760 * p, 0, 2 * PI); c.clip(); B(c, t); c.restore()
        c.arc(640, 360, 760 * p, 0, 2 * PI); setc(c, "#ffd23f"); c.set_line_width(12); c.stroke()
    if t < T_TITLE_END + 1: iris(T_TITLE_END, title_card, park)
    else: iris(T_OUTRO, park, outro_card)
    captions(c, t)
    f = clamp(min(t / 0.4, (DURATION - t) / 1.5))
    if f < 1: c.rectangle(0, 0, W, H); setc(c, (0, 0, 0, 1 - f)); c.fill()
    return surf

if __name__ == "__main__":
    os.makedirs("stills", exist_ok=True)
    for ts in sys.argv[1:]: frame(float(ts)).write_to_png(f"stills/f_{float(ts):06.2f}.png")
