"""Richer painted-style 2D scenery for Tinku ki Mahabharat (cairo)."""
import math, random, cairo
from chars import hexc, dark, light, setc, ell, rrect, fs, poly, clamp, PI, GOLD, GOLD_D

W, H = 1280, 720

def lin(c, x0, y0, x1, y1, stops):
    g = cairo.LinearGradient(x0, y0, x1, y1)
    for o, col in stops: g.add_color_stop_rgba(o, *(hexc(col) if isinstance(col, str) else col))
    return g

def sky(c, stops, y1=520, sun=None, rays=0.0, t=0.0):
    c.set_source(lin(c, 0, 0, 0, y1, stops)); c.paint()
    if sun:
        sx, sy, sr, scol = sun
        g = cairo.RadialGradient(sx, sy, sr * 0.3, sx, sy, sr * 6)
        g.add_color_stop_rgba(0, *hexc(scol, 0.9)); g.add_color_stop_rgba(0.25, *hexc(scol, 0.35)); g.add_color_stop_rgba(1, *hexc(scol, 0))
        c.set_source(g); c.paint()
        ell(c, sx, sy, sr, sr); setc(c, light(scol, 0.6)); c.fill()
        if rays > 0:
            c.save(); c.translate(sx, sy); c.rotate(t * 0.03)
            for i in range(14):
                c.save(); c.rotate(i * PI / 7)
                c.move_to(0, 0); c.line_to(1400, -60); c.line_to(1400, 60); c.close_path()
                setc(c, (1, 1, 0.9, 0.05 * rays)); c.fill(); c.restore()
            c.restore()

def cloud(c, x, y, s, a=1.0, warm=False):
    base = (1, 0.93, 0.88) if warm else (1, 1, 1)
    for dx, dy, r in ((0, 6, 30), (34, -14, 40), (74, -4, 34), (104, 8, 26), (50, 10, 34)):
        ell(c, x + dx * s, y + dy * s + 6, r * s, r * s * 0.85); setc(c, (0.75, 0.82, 0.92, 0.35 * a)); c.fill()
    for dx, dy, r in ((0, 0, 30), (34, -20, 40), (74, -10, 34), (104, 2, 26), (50, 4, 34)):
        ell(c, x + dx * s, y + dy * s, r * s, r * s * 0.85); setc(c, (*base, a)); c.fill()
    for dx, dy, r in ((30, -30, 22), (66, -20, 16)):
        ell(c, x + dx * s, y + dy * s, r * s, r * s * 0.7); setc(c, (1, 1, 1, 0.6 * a)); c.fill()

def clouds(c, t, a=1.0, warm=False, n=5, ymax=170, seed=2):
    r = random.Random(seed)
    for i in range(n):
        x0 = r.uniform(0, 1500); y = r.uniform(50, ymax); s = r.uniform(0.6, 1.2); sp = r.uniform(3, 8)
        cloud(c, (x0 + t * sp) % 1600 - 200, y, s, a, warm)

def ridge(c, y, amp, seed, col_top, col_bot, step=40, rough=0.5, ybot=720):
    r = random.Random(seed)
    pts = []; x = -50; yy = y
    while x <= W + 60:
        yy = y + amp * (math.sin(x * 0.004 + seed) * 0.6 + r.uniform(-rough, rough) * 0.5)
        pts.append((x, yy)); x += step
    c.move_to(-50, ybot)
    for p in pts: c.line_to(*p)
    c.line_to(W + 60, ybot); c.close_path()
    c.set_source(lin(c, 0, y - amp, 0, ybot, [(0, col_top), (1, col_bot)])); c.fill()
    return pts

def mountains(c, dusk=0.0):
    if dusk < 0.5:
        ridge(c, 330, 70, 3, "#9db8e0", "#c9daf0", 60, 0.9, 520)
        pts = ridge(c, 360, 50, 7, "#8fb0d8", "#bcd2ec", 45, 0.8, 520)
        for x, y in pts[2::5]:  # snow caps
            poly(c, [(x - 22, y + 18), (x, y - 2), (x + 22, y + 18), (x + 8, y + 12), (x - 6, y + 16)]); setc(c, (1, 1, 1, 0.7)); c.fill()
        ridge(c, 410, 30, 11, "#7fb98a", "#a6d49a", 30, 0.6, 520)
    else:
        ridge(c, 330, 70, 3, "#5a5a9a", "#7a6a9e", 60, 0.9, 520)
        ridge(c, 360, 50, 7, "#4a4f8a", "#6c5f92", 45, 0.8, 520)
        ridge(c, 410, 30, 11, "#3a5a5a", "#4f6f62", 30, 0.6, 520)

def treeline(c, y, seed, col, dark_k=0.8, n=40):
    r = random.Random(seed)
    for i in range(n):
        x = i * (W / n) + r.uniform(-10, 10); h = r.uniform(20, 46)
        ell(c, x, y - h * 0.5, h * 0.55, h * 0.6); setc(c, col); c.fill()
    c.rectangle(0, y - 8, W, 30); setc(c, col); c.fill()

def grass_field(c, y0, top="#86d65e", bot="#3f9e3f", t=0.0, seed=4, flowers=True, dusk=0.0):
    if dusk > 0.5: top, bot = "#4c8f4a", "#2a5f34"
    c.set_source(lin(c, 0, y0, 0, H, [(0, top), (1, bot)])); c.rectangle(0, y0, W, H - y0); c.fill()
    r = random.Random(seed)
    for _ in range(140):  # grass tufts
        x = r.uniform(0, W); y = r.uniform(y0 + 10, H); s = 0.5 + (y - y0) / (H - y0)
        col = dark(top if r.random() < 0.5 else bot, 0.82)
        for k in (-1, 0, 1):
            sway = 2 * math.sin(t * 1.5 + x * 0.05)
            c.move_to(x + k * 3 * s, y); c.curve_to(x + k * 4 * s, y - 6 * s, x + k * 6 * s + sway, y - 10 * s, x + k * 8 * s + sway, y - 14 * s)
        setc(c, col); c.set_line_width(1.6 * s); c.stroke()
    if flowers:
        for _ in range(45):
            x = r.uniform(0, W); y = r.uniform(y0 + 15, H); s = 0.6 + (y - y0) / (H - y0) * 0.8
            col = r.choice(["#ffffff", "#ffe14d", "#ff8fc7", "#ff7a3d", "#c39bff"])
            for a in range(5):
                ell(c, x + 3.2 * s * math.cos(a * 1.256), y + 3.2 * s * math.sin(a * 1.256), 2.4 * s, 2.4 * s); setc(c, col); c.fill()
            ell(c, x, y, 1.6 * s, 1.6 * s); setc(c, "#ffb000"); c.fill()

def banyan(c, x, y, s=1.0, dusk=0.0, t=0.0):
    leaf = ("#3f9e3f", "#2f7f35", "#5fbf4a") if dusk < 0.5 else ("#2f6b3a", "#1f4f2a", "#3f7f45")
    c.save(); c.translate(x, y); c.scale(s, s)
    ell(c, 0, 4, 110, 18); setc(c, (0, 0, 0, 0.18)); c.fill()
    c.move_to(-26, 0); c.curve_to(-20, -80, -30, -150, -60, -210); c.line_to(-40, -214); c.curve_to(-6, -160, 0, -120, 4, -150)
    c.curve_to(10, -190, 40, -210, 60, -230); c.line_to(72, -220); c.curve_to(40, -190, 22, -120, 26, 0); c.close_path()
    c.set_source(lin(c, -30, 0, 30, 0, [(0, "#7a4a24"), (0.5, "#9a6232"), (1, "#5e3618")])); c.fill()
    for k in range(-2, 3):  # aerial roots
        c.move_to(k * 30, -170); c.curve_to(k * 32, -110, k * 28, -60, k * 30 + 2, -20); setc(c, (0.45, 0.28, 0.12, 0.6)); c.set_line_width(2); c.stroke()
    cl = [(-90, -230, 70), (-20, -280, 85), (60, -250, 80), (110, -200, 60), (-120, -180, 55), (0, -200, 70), (40, -310, 55), (-60, -300, 55)]
    for dx, dy, r in cl: ell(c, dx + 8, dy + 10, r, r * 0.8); setc(c, leaf[1]); c.fill()
    for dx, dy, r in cl: ell(c, dx, dy, r, r * 0.8); setc(c, leaf[0]); c.fill()
    for dx, dy, r in cl: ell(c, dx - r * 0.25, dy - r * 0.3, r * 0.55, r * 0.4); setc(c, leaf[2]); c.fill()
    c.restore()

def bird(c, x, y, s, t):
    f = math.sin(t * 10) * 0.6
    c.move_to(x - 12 * s, y - 5 * s * f); c.curve_to(x - 6 * s, y - 6 * s * f - 2 * s, x - 2 * s, y - 2, x, y)
    c.curve_to(x + 2 * s, y - 2, x + 6 * s, y - 6 * s * f - 2 * s, x + 12 * s, y - 5 * s * f)
    setc(c, (0.2, 0.2, 0.3, 0.8)); c.set_line_width(2.2); c.stroke()

def birds(c, t, n=5, seed=1):
    r = random.Random(seed)
    for i in range(n):
        x0 = r.uniform(0, 1400); y = r.uniform(80, 220); sp = r.uniform(25, 45)
        bird(c, (x0 + t * sp) % 1500 - 100, y + 6 * math.sin(t + i), r.uniform(0.8, 1.2), t + i)

def flag(c, x, y, t, col="#ff7a1a", s=1.0):
    c.move_to(x, y); c.line_to(x, y - 46 * s); setc(c, "#6b4a2a"); c.set_line_width(2.5); c.stroke()
    c.move_to(x, y - 46 * s)
    for k in range(9):
        c.line_to(x + k * 4.5 * s, y - 46 * s + 4 * s * math.sin(t * 6 + k * 0.7))
    for k in range(8, -1, -1):
        c.line_to(x + k * 4.5 * s, y - 26 * s + 4 * s * math.sin(t * 6 + k * 0.7))
    c.close_path(); fs(c, col, dark(col, 0.7), 1.5)

def chhatri(c, x, y, s, t, stone="#f0c48a", dome="#f5b82e"):
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, -40, -8, 80, 12, 3); fs(c, light(stone, 0.2), dark(stone, 0.7), 2)
    for px in (-30, -10, 10, 30):
        rrect(c, px - 3, -58, 6, 50, 2); fs(c, stone, dark(stone, 0.7), 1.5)
    rrect(c, -46, -66, 92, 10, 4); fs(c, light(stone, 0.2), dark(stone, 0.7), 2)
    c.move_to(-36, -66); c.curve_to(-36, -110, -6, -116, 0, -130); c.curve_to(6, -116, 36, -110, 36, -66); c.close_path()
    c.set_source(lin(c, -36, 0, 36, 0, [(0, light(dome, 0.35)), (0.5, dome), (1, dark(dome, 0.75))])); c.fill_preserve(); setc(c, dark(dome, 0.65)); c.set_line_width(2); c.stroke()
    c.move_to(0, -130); c.line_to(0, -142); setc(c, GOLD_D); c.set_line_width(3); c.stroke(); ell(c, 0, -144, 4, 4); fs(c, GOLD, GOLD_D, 1.5)
    c.restore()

def palace(c, x, y, s, t, stone="#f2c78f", dome="#f5b82e"):
    """Multi-tier Indian palace, base centre at (x, y)."""
    sh = dark(stone, 0.8); hi = light(stone, 0.25)
    c.save(); c.translate(x, y); c.scale(s, s)
    ell(c, 0, 6, 420, 26); setc(c, (0, 0, 0, 0.15)); c.fill()
    for k in range(4):  # steps
        rrect(c, -150 + k * 12, -k * 10, 300 - k * 24, 12, 2); fs(c, light(stone, 0.3 - k * 0.05), sh, 1.5)
    # wings
    for side in (-1, 1):
        c.save(); c.scale(side, 1)
        rrect(c, 160, -230, 220, 230, 4); c.set_source(lin(c, 160, 0, 380, 0, [(0, stone), (1, sh)])); c.fill_preserve(); setc(c, dark(stone, 0.6)); c.set_line_width(2.5); c.stroke()
        for row in range(2):
            for k in range(4):
                ax = 180 + k * 50; ay = -30 - row * 100
                c.move_to(ax, ay); c.line_to(ax, ay - 50); c.curve_to(ax, ay - 70, ax + 30, ay - 70, ax + 30, ay - 50); c.line_to(ax + 30, ay); c.close_path()
                c.set_source(lin(c, 0, ay - 70, 0, ay, [(0, "#5a3a2a"), (1, "#3a2418")])); c.fill_preserve(); setc(c, hi); c.set_line_width(2); c.stroke()
                rrect(c, ax - 4, ay - 2, 38, 6, 2); fs(c, hi, sh, 1)
        rrect(c, 150, -248, 240, 22, 4); fs(c, hi, dark(stone, 0.6), 2)
        for k in range(12): rrect(c, 156 + k * 19.5, -262, 12, 14, 3); fs(c, stone, sh, 1)
        chhatri(c, 270, -248, 0.9, t, stone, dome)
        rrect(c, 368, -300, 30, 300, 6); fs(c, stone, dark(stone, 0.6), 2)
        c.move_to(368, -300); c.curve_to(368, -340, 383, -350, 383, -362); c.curve_to(383, -350, 398, -340, 398, -300); c.close_path(); fs(c, dome, dark(dome, 0.65), 2)
        c.restore()
    # centre block
    rrect(c, -160, -330, 320, 330, 4); c.set_source(lin(c, -160, 0, 160, 0, [(0, hi), (0.6, stone), (1, sh)])); c.fill_preserve(); setc(c, dark(stone, 0.6)); c.set_line_width(2.5); c.stroke()
    c.move_to(-60, 0); c.line_to(-60, -150); c.curve_to(-60, -230, 60, -230, 60, -150); c.line_to(60, 0); c.close_path()  # grand gate
    fs(c, dark(stone, 0.75), dark(stone, 0.55), 3)
    c.move_to(-44, 0); c.line_to(-44, -145); c.curve_to(-44, -205, 44, -205, 44, -145); c.line_to(44, 0); c.close_path()
    c.set_source(lin(c, 0, -205, 0, 0, [(0, "#7a2a1a"), (1, "#4a160d")])); c.fill()
    for k in range(-1, 2): rrect(c, k * 26 - 2, -140, 4, 140, 2); setc(c, (0.9, 0.7, 0.3, 0.6)); c.fill()
    for side in (-1, 1):  # jharokhas
        jx = side * 110
        rrect(c, jx - 28, -250, 56, 70, 6); fs(c, hi, sh, 2)
        c.move_to(jx - 20, -186); c.line_to(jx - 20, -230); c.curve_to(jx - 20, -248, jx + 20, -248, jx + 20, -230); c.line_to(jx + 20, -186); c.close_path(); fs(c, "#4a2a1a", None, 1)
        c.move_to(jx - 34, -180); c.curve_to(jx - 30, -166, jx + 30, -166, jx + 34, -180); c.close_path(); fs(c, stone, sh, 2)
        c.move_to(jx - 32, -250); c.curve_to(jx - 32, -280, jx + 32, -280, jx + 32, -250); c.close_path(); fs(c, dome, dark(dome, 0.65), 2)
    rrect(c, -176, -350, 352, 24, 4); fs(c, hi, dark(stone, 0.6), 2)
    for k in range(18): rrect(c, -170 + k * 19.5, -364, 12, 14, 3); fs(c, stone, sh, 1)
    # main dome
    rrect(c, -90, -420, 180, 70, 4); fs(c, stone, dark(stone, 0.6), 2)
    for k in range(5): c.move_to(-70 + k * 35, -360); c.line_to(-70 + k * 35, -400); c.curve_to(-70 + k * 35, -412, -56 + k * 35, -412, -56 + k * 35, -400); c.line_to(-56 + k * 35, -360); c.close_path(); fs(c, "#5a3a2a", None, 1)
    c.move_to(-110, -420); c.curve_to(-120, -520, -30, -560, 0, -600); c.curve_to(30, -560, 120, -520, 110, -420); c.close_path()
    c.set_source(lin(c, -110, 0, 110, 0, [(0, light(dome, 0.4)), (0.45, dome), (1, dark(dome, 0.7))])); c.fill_preserve(); setc(c, dark(dome, 0.6)); c.set_line_width(3); c.stroke()
    for k in range(-2, 3):
        c.move_to(k * 8, -598); c.curve_to(k * 30, -540, k * 44, -480, k * 46, -420); setc(c, (0.6, 0.38, 0.05, 0.35)); c.set_line_width(2); c.stroke()
    c.move_to(0, -600); c.line_to(0, -630); setc(c, GOLD_D); c.set_line_width(4); c.stroke()
    for k in range(3): ell(c, 0, -606 - k * 9, 6 - k, 4); fs(c, GOLD, GOLD_D, 1)
    flag(c, 0, -632, t, "#ff7a1a", 1.2)
    for sx_ in (-130, 130): chhatri(c, sx_, -350, 0.8, t, stone, dome)
    c.restore()

def river_bank_scene(c, t, dusk=0.0):
    if dusk < 0.5:
        sky(c, [(0, "#3d9ff0"), (0.6, "#9fd5ff"), (1, "#e9f6ff")], 440, sun=(1080, 120, 40, "#fff3b0"), rays=1.0, t=t)
        clouds(c, t, 0.95, n=5, ymax=180)
    else:
        sky(c, [(0, "#1b1f5c"), (0.55, "#6b4a8f"), (0.85, "#ff8a6b"), (1, "#ffc28a")], 440)
        ell(c, 1050, 110, 36, 36); setc(c, (1, 0.97, 0.85, 1)); c.fill()
        ell(c, 1066, 100, 32, 32); setc(c, hexc("#262a6a")); c.fill()
    mountains(c, dusk)
    treeline(c, 440, 21, "#5aa84e" if dusk < 0.5 else "#2f5a3a", n=60)
    # river, widening toward viewer on the right
    def rp():
        c.move_to(500, 438); c.curve_to(760, 432, 1000, 436, 1290, 438); c.line_to(1290, 730); c.line_to(560, 730)
        c.curve_to(520, 640, 470, 520, 500, 438); c.close_path()
    # bank (sand) under the river edge
    grass_field(c, 438, t=t, dusk=dusk)
    c.move_to(470, 438); c.curve_to(440, 520, 500, 640, 530, 730); c.line_to(600, 730); c.curve_to(560, 640, 510, 520, 520, 438); c.close_path()
    setc(c, "#e8cf9a" if dusk < 0.5 else "#9a8a6a"); c.fill()
    rp()
    if dusk < 0.5: c.set_source(lin(c, 0, 438, 0, 730, [(0, "#b8e6ff"), (0.15, "#7cc8f2"), (1, "#1f78c8")]))
    else: c.set_source(lin(c, 0, 438, 0, 730, [(0, "#ffb08a"), (0.15, "#8a6ab0"), (1, "#22336f")]))
    c.fill()
    c.save(); rp(); c.clip()
    r = random.Random(5)
    for k in range(60):  # shimmer streaks
        y = r.uniform(445, 720); x0 = r.uniform(480, 1300); ln = r.uniform(20, 70) * (0.5 + (y - 438) / 300)
        x = (x0 + t * 18 * (0.5 + (y - 438) / 300)) % 860 + 480
        a = 0.25 + 0.25 * math.sin(t * 2 + k)
        c.move_to(x, y); c.line_to(x + ln, y); setc(c, (1, 1, 1, a)); c.set_line_width(1.5 + (y - 438) / 150); c.stroke()
    if dusk < 0.5:  # sun glitter path
        for k in range(30):
            y = 450 + k * 9; w_ = 6 + k * 1.5; x = 1080 + 20 * math.sin(t * 2 + k)
            ell(c, x, y, w_, 1.5); setc(c, (1, 1, 0.85, 0.5 * (1 - k / 30))); c.fill()
    else:
        for k in range(20):
            y = 450 + k * 10; x = 1050 + 10 * math.sin(t * 2 + k)
            ell(c, x, y, 4 + k, 1.4); setc(c, (1, 0.95, 0.8, 0.45 * (1 - k / 20))); c.fill()
    c.restore()
    # ghat steps at the left bank
    for k in range(6):
        y = 560 + k * 26
        poly(c, [(420 - k * 30, y), (560 + k * 12, y), (568 + k * 12, y + 26), (410 - k * 30, y + 26)])
        fs(c, "#d9c1a0" if dusk < 0.5 else "#8a7a66", "#a88f6c" if dusk < 0.5 else "#5a4f40", 2)
    for lx, ly in ((700, 690), (1180, 540), (1000, 650), (860, 600)):  # lotus pads
        ell(c, lx, ly, 26, 8); fs(c, "#3fae4a", "#2a7a33", 2)
        for a in (-0.6, 0, 0.6):
            c.save(); c.translate(lx, ly - 4); c.rotate(a); ell(c, 0, -10, 6, 12); fs(c, "#ff9fcf", "#d9407c", 1.5); c.restore()
    for rx in range(520, 600, 9):  # reeds
        h = 40 + (rx * 37) % 30
        c.move_to(rx, 450); c.curve_to(rx + 2, 430, rx + 4 + 3 * math.sin(t + rx), 420, rx + 6 + 4 * math.sin(t + rx), 450 - h); setc(c, "#4f8f3f" if dusk < .5 else "#2f5a33"); c.set_line_width(2.5); c.stroke()
    banyan(c, 140, 470, 0.95, dusk, t)
    if dusk < 0.5: birds(c, t, 5)
    else:
        r = random.Random(8)
        for k in range(26):  # fireflies
            x = r.uniform(0, 640) + 20 * math.sin(t * 0.7 + k); y = r.uniform(380, 700) + 15 * math.cos(t * 0.9 + k)
            a = 0.5 + 0.5 * math.sin(t * 3 + k * 1.7)
            g = cairo.RadialGradient(x, y, 0, x, y, 9); g.add_color_stop_rgba(0, 1, 1, 0.6, a); g.add_color_stop_rgba(1, 1, 1, 0.6, 0)
            c.set_source(g); c.arc(x, y, 9, 0, 2 * PI); c.fill()

def palace_scene_bg(c, t):
    sky(c, [(0, "#3d9ff0"), (0.6, "#9fd5ff"), (1, "#eaf7ff")], 470, sun=(180, 110, 38, "#fff3b0"), rays=0.8, t=t)
    clouds(c, t, 0.95, n=5)
    mountains(c, 0)
    treeline(c, 470, 33, "#5aa84e", n=60)
    palace(c, 640, 470, 0.66, t)
    grass_field(c, 470, t=t, seed=9)
    # sandstone path with border + fountains + hedges
    c.move_to(480, 720); c.curve_to(560, 560, 600, 490, 600, 470); c.line_to(680, 470); c.curve_to(680, 490, 720, 560, 800, 720); c.close_path()
    c.set_source(lin(c, 0, 470, 0, 720, [(0, "#efd3a2"), (1, "#d9b47a")])); c.fill()
    for k in range(10):
        y = 480 + k * 25; w_ = 40 + k * 16
        c.move_to(640 - w_, y); c.line_to(640 + w_, y); setc(c, (0.7, 0.55, 0.3, 0.25)); c.set_line_width(1.5); c.stroke()
    for side in (-1, 1):
        for k in range(4):
            hx = 640 + side * (110 + k * 60); hy = 500 + k * 40
            ell(c, hx, hy, 28 + k * 6, 14 + k * 3); fs(c, "#3f9e3f", "#2f7f35", 2)
            ell(c, hx - 6, hy - 5, 14 + k * 3, 6 + k); setc(c, "#5fbf4a"); c.fill()
    banyan(c, 90, 520, 0.8, 0, t); banyan(c, 1200, 530, 0.85, 0, t)
    birds(c, t, 4, 3)

def room_bg(c, t):
    c.set_source(lin(c, 0, 0, 0, 500, [(0, "#cfeaff"), (1, "#a8d8f5")])); c.paint()
    for row in range(10):  # wallpaper motif
        for k in range(14):
            x = k * 96 + (row % 2) * 48; y = 30 + row * 50
            for a in range(4):
                ell(c, x + 6 * math.cos(a * PI / 2), y + 6 * math.sin(a * PI / 2), 4, 4); setc(c, (1, 1, 1, 0.35)); c.fill()
    c.set_source(lin(c, 0, 500, 0, 720, [(0, "#e6ad70"), (1, "#c07f45")])); c.rectangle(0, 500, W, 220); c.fill()
    for k in range(9): c.move_to(0, 520 + k * 24); c.line_to(W, 520 + k * 24)
    setc(c, (0.6, 0.38, 0.18, 0.3)); c.set_line_width(2); c.stroke()
    for k in range(14): c.move_to(k * 110 + (k % 2) * 40, 520); c.line_to(k * 110 + (k % 2) * 40 - 30, 720)
    setc(c, (0.6, 0.38, 0.18, 0.15)); c.set_line_width(1.5); c.stroke()
    rrect(c, 0, 494, W, 12, 2); fs(c, "#ffffff", (0.8, 0.85, 0.9, 1), 2)
    # window with curtains and light beam
    c.save(); c.move_to(110, 300); c.line_to(300, 300); c.line_to(560, 720); c.line_to(150, 720); c.close_path(); setc(c, (1, 0.98, 0.85, 0.18)); c.fill(); c.restore()
    rrect(c, 80, 80, 240, 220, 12); fs(c, "#fff8e6", "#d9a441", 8)
    c.save(); rrect(c, 88, 88, 224, 204, 8); c.clip()
    sky(c, [(0, "#4fb0ff"), (1, "#d6f3ff")], 300); cloud(c, 120 + (t * 8) % 220, 140, 0.55); ridge(c, 250, 12, 3, "#7fb98a", "#5f9f6a", 20, 0.5, 300)
    c.restore()
    c.move_to(200, 88); c.line_to(200, 292); c.move_to(88, 190); c.line_to(312, 190); setc(c, "#d9a441"); c.set_line_width(6); c.stroke()
    for side, x in ((-1, 70), (1, 330)):
        c.move_to(x - 22, 64); c.curve_to(x - 10 * side, 160, x + 14 * side, 260, x - 4 * side, 330); c.line_to(x + 24 * side if side > 0 else x - 24, 330)
        c.curve_to(x + 30 * side, 240, x + 20 * side, 140, x + 22, 64); c.close_path(); fs(c, "#ff7a8f", "#d94a62", 2)
    rrect(c, 40, 56, 330, 14, 7); fs(c, "#b97a45", "#7a4a24", 2)
    # framed peacock feather picture
    rrect(c, 400, 110, 140, 120, 8); fs(c, "#fff3c4", "#e07a1f", 6)
    c.save(); c.translate(470, 215); c.rotate(0.3)
    c.move_to(0, 0); c.curve_to(-3, -30, -2, -60, 0, -80); setc(c, "#2f9a47"); c.set_line_width(3); c.stroke()
    ell(c, 0, -74, 18, 30); fs(c, "#1fa38a", "#0f6b5a", 2); ell(c, 0, -80, 12, 17); setc(c, "#1f6fe0"); c.fill()
    ell(c, 0, -82, 7, 10); setc(c, "#0b1d4f"); c.fill(); ell(c, 0, -84, 3, 4); setc(c, "#ffd23f"); c.fill(); c.restore()
    # bookshelf with shading
    rrect(c, 960, 170, 230, 330, 8); c.set_source(lin(c, 960, 0, 1190, 0, [(0, "#d39a5b"), (1, "#a8703e")])); c.fill_preserve(); setc(c, "#7a4a24"); c.set_line_width(4); c.stroke()
    for row in range(3):
        y = 190 + row * 100
        r = random.Random(row); x = 974
        while x < 1170:
            w_ = r.uniform(16, 26); h_ = r.uniform(55, 80)
            col = r.choice(["#ff5b5b", "#2f7bff", "#ffd23f", "#3fae4a", "#a04dff", "#ff8c1a"])
            rrect(c, x, y + 84 - h_, w_, h_, 3); c.set_source(lin(c, x, 0, x + w_, 0, [(0, light(col, 0.2)), (1, dark(col, 0.8))])); c.fill()
            rrect(c, x + 3, y + 84 - h_ + 8, w_ - 6, 3, 1); setc(c, (1, 1, 1, 0.5)); c.fill(); x += w_ + 3
        rrect(c, 966, y + 84, 218, 10, 2); fs(c, "#8a5a2b")
    # plant
    rrect(c, 1206, 430, 50, 70, 8); fs(c, "#e8603f", "#a8402a", 2)
    for a in (-0.8, -0.4, 0, 0.4, 0.8):
        c.save(); c.translate(1231, 432); c.rotate(a + 0.05 * math.sin(t + a)); ell(c, 0, -40, 12, 36); fs(c, "#3fae4a", "#2a7a33", 2); c.restore()
    # rug with pattern
    ell(c, 520, 640, 390, 64); setc(c, (0, 0, 0, 0.08)); c.fill()
    ell(c, 520, 636, 380, 60); setc(c, "#ff8a5c"); c.fill(); ell(c, 520, 636, 330, 46); setc(c, "#ffc48f"); c.fill()
    ell(c, 520, 636, 260, 34); setc(c, "#ff8a5c"); c.set_line_width(4); c.stroke()
    for k in range(16):
        a = k * PI / 8; ell(c, 520 + 300 * math.cos(a), 636 + 40 * math.sin(a), 8, 4); setc(c, "#ffe066"); c.fill()

def mandap_scene_bg(c, t):
    c.set_source(lin(c, 0, 0, 0, 480, [(0, "#ffb84f"), (0.6, "#ffd98a"), (1, "#fff1d6")])); c.paint()
    palace(c, 640, 480, 0.62, t, "#f7d9a8", "#ffb000")
    c.set_source(lin(c, 0, 470, 0, 720, [(0, "#f6d6a6"), (1, "#e2b47a")])); c.rectangle(0, 470, W, 250); c.fill()
    # rangoli
    cx, cy = 640, 680
    for k, col in enumerate(("#ff3b6b", "#ffb000", "#3fae4a", "#2f7bff")):
        for a in range(12):
            ang = a * PI / 6 + k * 0.13
            ell(c, cx + (60 + k * 30) * math.cos(ang) * 2.2, cy + (60 + k * 30) * math.sin(ang) * 0.25, 10, 4); setc(c, hexc(col, 0.7)); c.fill()
    # pillars with banana leaves
    for px in (300, 980):
        rrect(c, px - 16, 220, 32, 400, 8); c.set_source(lin(c, px - 16, 0, px + 16, 0, [(0, "#ffe08a"), (0.5, "#e8b84a"), (1, "#b98a2a")])); c.fill()
        for k in range(6): rrect(c, px - 18, 240 + k * 64, 36, 8, 3); fs(c, "#d81b3c", "#7a0d1f", 1)
        for side in (-1, 1):
            c.save(); c.translate(px, 600); c.rotate(side * 0.25)
            c.move_to(0, 0); c.curve_to(side * 40, -120, side * 30, -260, side * 6, -330); c.curve_to(side * 10, -200, side * 12, -100, 0, 0); c.close_path()
            fs(c, "#4fbf4a", "#2f8f35", 2); c.restore()
    # canopy
    c.move_to(270, 230); c.curve_to(480, 140, 800, 140, 1010, 230); c.line_to(1010, 256); c.curve_to(800, 170, 480, 170, 270, 256); c.close_path()
    c.set_source(lin(c, 0, 140, 0, 256, [(0, "#ff5a3c"), (1, "#c8281a")])); c.fill_preserve(); setc(c, "#8a1a10"); c.set_line_width(3); c.stroke()
    for k in range(15):
        x = 290 + k * 50; yt = 246 - 46 * math.sin(PI * k / 14)
        c.move_to(x, yt); c.line_to(x, yt + 80 + 6 * math.sin(t * 2 + k))
        c.set_dash([0.1, 12]); c.set_line_cap(cairo.LINE_CAP_ROUND); setc(c, "#ff9f1a" if k % 2 else "#ffd23f"); c.set_line_width(11); c.stroke(); c.set_dash([])
    # hanging lamps (diyas) glowing
    for x in (420, 640, 860):
        yb = 300 + 6 * math.sin(t * 1.5 + x)
        c.move_to(x, 180); c.line_to(x, yb); setc(c, "#8a5a12"); c.set_line_width(2); c.stroke()
        g = cairo.RadialGradient(x, yb + 14, 2, x, yb + 14, 50); g.add_color_stop_rgba(0, 1, 0.85, 0.4, 0.8); g.add_color_stop_rgba(1, 1, 0.85, 0.4, 0)
        c.set_source(g); c.arc(x, yb + 14, 50, 0, 2 * PI); c.fill()
        c.arc(x, yb + 14, 14, 0, PI); fs(c, GOLD, GOLD_D, 2)
        c.move_to(x - 4, yb + 14); c.curve_to(x - 5, yb + 4, x, yb, x, yb - 4 + 2 * math.sin(t * 9)); c.curve_to(x, yb, x + 5, yb + 4, x + 4, yb + 14); c.close_path(); setc(c, "#ffcf3f"); c.fill()


def park_bg(c, t):
    """Sunny park / playground for Tinku & Friends."""
    sky(c, [(0, "#4ab2ff"), (0.65, "#a9dcff"), (1, "#eaf7ff")], 470, sun=(1130, 100, 42, "#fff3b0"), rays=1.0, t=t)
    clouds(c, t, 0.95, n=5, ymax=170, seed=6)
    for hx, r, col in ((150, 420, "#a6e07f"), (760, 520, "#95d870"), (1300, 420, "#a6e07f")):
        ell(c, hx, 500, r, r * 0.32); setc(c, col); c.fill()
    treeline(c, 470, 41, "#6cbf55", n=50)
    grass_field(c, 468, "#8ddc62", "#4fae44", t=t, seed=12)
    # path
    c.move_to(0, 640); c.curve_to(300, 600, 700, 690, 1280, 620); c.line_to(1280, 680); c.curve_to(700, 740, 300, 650, 0, 700); c.close_path()
    setc(c, (0.93, 0.83, 0.62, 0.9)); c.fill()
    # swing set (back left)
    c.save(); c.translate(150, 470)
    for x0, x1 in ((-80, -60), (80, 60)):
        c.move_to(x0, 0); c.line_to(x1 * 0.2, -150); setc(c, "#e8432f"); c.set_line_width(8); c.stroke()
    c.move_to(-70, -150); c.line_to(70, -150); setc(c, "#e8432f"); c.set_line_width(10); c.stroke()
    for k, sx in enumerate((-35, 35)):
        a = 0.25 * math.sin(t * 2 + k * 1.5)
        ex = sx + 90 * math.sin(a); ey = -150 + 90 * math.cos(a)
        c.move_to(sx - 12, -150); c.line_to(ex - 12, ey); c.move_to(sx + 12, -150); c.line_to(ex + 12, ey); setc(c, "#6b6b6b"); c.set_line_width(2); c.stroke()
        rrect(c, ex - 18, ey - 4, 36, 8, 3); fs(c, "#ffd23f", "#c99a00", 2)
    c.restore()
    # slide (back right)
    c.save(); c.translate(1150, 470)
    c.move_to(-30, 0); c.line_to(-30, -120); c.move_to(0, 0); c.line_to(0, -120); setc(c, "#2f7bff"); c.set_line_width(6); c.stroke()
    for k in range(5): c.move_to(-30, -20 - k * 22); c.line_to(0, -20 - k * 22)
    setc(c, "#2f7bff"); c.set_line_width(4); c.stroke()
    c.move_to(0, -120); c.curve_to(40, -110, 80, -30, 130, 0); c.line_to(140, -6); c.curve_to(90, -36, 50, -116, 0, -130); c.close_path(); fs(c, "#ffd23f", "#c99a00", 2)
    rrect(c, -38, -134, 46, 14, 4); fs(c, "#ff5b5b", "#a8302a", 2)
    c.restore()
    banyan(c, 60, 520, 0.7, 0, t)
    for fx, col in ((420, "#ff5f8f"), (980, "#ffb000"), (1230, "#a04dff")):
        for k in range(5):
            x = fx + k * 18; y = 486 + (k % 2) * 6
            c.move_to(x, y + 20); c.line_to(x, y); setc(c, "#3f9e3f"); c.set_line_width(2); c.stroke()
            for a in range(5): ell(c, x + 5 * math.cos(a * 1.256), y + 5 * math.sin(a * 1.256), 4, 4); setc(c, col); c.fill()
            ell(c, x, y, 2.5, 2.5); setc(c, "#ffe066"); c.fill()
    birds(c, t, 3, 7)
