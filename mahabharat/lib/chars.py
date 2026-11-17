"""Cartoon cast for the Tinku Mahabharata series (cairo, feet at (x, y), y up = negative)."""
import math, cairo

PI = math.pi

# ------------------------------------------------------------------ helpers
def hexc(h, a=1.0):
    h = h.lstrip("#"); return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)

def dark(h, k=0.75):
    r, g, b, a = hexc(h) if isinstance(h, str) else h; return (r * k, g * k, b * k, a)

def light(h, k=0.35):
    r, g, b, a = hexc(h) if isinstance(h, str) else h; return (r + (1 - r) * k, g + (1 - g) * k, b + (1 - b) * k, a)

def setc(c, col):
    c.set_source_rgba(*(hexc(col) if isinstance(col, str) else col))

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))

def ell(c, x, y, rx, ry):
    c.save(); c.translate(x, y); c.scale(max(rx, .01), max(ry, .01)); c.arc(0, 0, 1, 0, 2 * PI); c.restore()

def rrect(c, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    c.new_sub_path(); c.arc(x + w - r, y + r, r, -PI / 2, 0); c.arc(x + w - r, y + h - r, r, 0, PI / 2)
    c.arc(x + r, y + h - r, r, PI / 2, PI); c.arc(x + r, y + r, r, PI, 1.5 * PI); c.close_path()

def fs(c, col, outline=None, lw=3.0):
    setc(c, col)
    if outline is None: outline = dark(col, 0.68)
    if outline is False:
        c.fill(); return
    c.fill_preserve(); setc(c, outline); c.set_line_width(lw); c.stroke()

def poly(c, pts):
    c.move_to(*pts[0])
    for p in pts[1:]: c.line_to(*p)
    c.close_path()

GOLD = "#f5b82e"; GOLD_D = "#b97a10"

def gold(c, lw=2.5):
    fs(c, GOLD, GOLD_D, lw)

def mir(a, sgn):
    return (sgn * a[0], sgn * a[1]) if isinstance(a, (tuple, list)) else sgn * a


def limb(c, sx, sy, ang, length, col, w, cuff=None, band=None):
    """Two-part arm with an elbow. ang = shoulder angle (0 = down, + = outward/up) or (shoulder, elbow_bend).
    Positive bend lifts the forearm outward/up, negative folds it inward across the body. Returns hand point."""
    if isinstance(ang, (tuple, list)):
        a1, bend = ang
    else:
        a1 = ang; s_ = 1 if a1 >= 0 else -1
        bend = s_ * (0.25 + 0.15 * clamp((abs(a1) - 1.0) / 1.2))
    L1 = length * 0.52; L2 = length * 0.5
    ex = sx + math.sin(a1) * L1; ey = sy + math.cos(a1) * L1
    a2 = a1 + bend
    hx = ex + math.sin(a2) * L2; hy = ey + math.cos(a2) * L2
    c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
    for lw, cl in ((w + 5, dark(col, 0.7)), (w, col)):
        c.move_to(sx, sy); c.line_to(ex, ey); c.line_to(hx, hy); setc(c, cl); c.set_line_width(lw); c.stroke()
    ell(c, ex, ey, w * 0.5, w * 0.5); setc(c, col); c.fill()
    if band:
        bx, by = sx + math.sin(a1) * L1 * 0.55, sy + math.cos(a1) * L1 * 0.55
        c.save(); c.translate(bx, by); c.rotate(-a1); rrect(c, -w / 2 - 2, -5, w + 4, 10, 4); gold(c, 2); c.restore()
    if cuff:
        bx, by = ex + math.sin(a2) * L2 * 0.78, ey + math.cos(a2) * L2 * 0.78
        c.save(); c.translate(bx, by); c.rotate(-a2); rrect(c, -w / 2 - 2, -6, w + 4, 12, 4); gold(c, 2); c.restore()
    # hand: palm + thumb
    side = 1 if sx >= 0 else -1
    c.save(); c.translate(hx, hy); c.rotate(-a2)
    ell(c, side * w * 0.42, w * 0.05, w * 0.3, w * 0.24); fs(c, col, dark(col, 0.7), 2)  # thumb
    ell(c, 0, w * 0.15, w * 0.6, w * 0.66); fs(c, col, dark(col, 0.7), 2.5)
    c.move_to(-w * 0.35, w * 0.45); c.line_to(-w * 0.3, w * 0.62); c.move_to(0, w * 0.5); c.line_to(0, w * 0.7); c.move_to(w * 0.3, w * 0.45); c.line_to(w * 0.25, w * 0.62)
    setc(c, dark(col, 0.72)); c.set_line_width(1.6); c.stroke()
    c.restore()
    return hx, hy + w * 0.15

def eyes(c, xs, y, rx, ry, look=0.0, closed=False, iris="#3a2414", lid=0.0):
    for ex in xs:
        if closed:
            c.set_line_width(4); setc(c, "#2b1b10"); c.arc(ex, y, rx * 0.8, 0.15 * PI, 0.85 * PI); c.stroke(); continue
        ell(c, ex, y, rx, ry); fs(c, "#ffffff", (0.3, 0.2, 0.15, 1), 2.2)
        px = ex + look * rx * 0.35; py = y + ry * 0.12
        ell(c, px, py, rx * 0.66, rx * 0.7); setc(c, iris); c.fill()
        ell(c, px, py, rx * 0.36, rx * 0.38); setc(c, "#140b06"); c.fill()
        ell(c, px + rx * 0.25, py - rx * 0.3, rx * 0.2, rx * 0.2); setc(c, "#ffffff"); c.fill()
        if lid > 0:  # heavy upper lid (stern / sly look)
            c.save(); ell(c, ex, y, rx + 1, ry + 1); c.clip()
            c.rectangle(ex - rx - 2, y - ry - 2, 2 * rx + 4, (2 * ry + 4) * lid); setc(c, "#c58c62"); c.fill(); c.restore()

def feye(c, xs, y, w, h, look=0.0, closed=False, iris="#3a2414"):
    """Elegant almond-shaped eyes with lined upper lid and winged lashes."""
    for ex in xs:
        sgn = 1 if ex > 0 else -1
        if closed:
            c.move_to(ex - w, y); c.curve_to(ex - w / 2, y + h * 0.6, ex + w / 2, y + h * 0.6, ex + w, y)
            setc(c, "#1a0f0a"); c.set_line_width(3); c.stroke(); continue
        def almond():
            c.move_to(ex - w, y + 2); c.curve_to(ex - w * 0.6, y - h * 1.15, ex + w * 0.6, y - h * 1.15, ex + w, y - 1)
            c.curve_to(ex + w * 0.5, y + h * 0.85, ex - w * 0.5, y + h * 0.85, ex - w, y + 2); c.close_path()
        almond(); setc(c, "#ffffff"); c.fill()
        c.save(); almond(); c.clip()
        px = ex + look * w * 0.3; py = y - h * 0.08
        ell(c, px, py, h * 0.82, h * 0.86); setc(c, iris); c.fill()
        ell(c, px, py, h * 0.45, h * 0.47); setc(c, "#140b06"); c.fill()
        ell(c, px + h * 0.3, py - h * 0.32, h * 0.22, h * 0.22); setc(c, "#ffffff"); c.fill()
        ell(c, px - h * 0.25, py + h * 0.3, h * 0.1, h * 0.1); setc(c, "#ffffff"); c.fill()
        c.restore()
        # upper lid + wing
        c.move_to(ex - w - 1, y + 2); c.curve_to(ex - w * 0.6, y - h * 1.15, ex + w * 0.6, y - h * 1.15, ex + w, y - 1)
        c.line_to(ex + sgn * 0 + (w + 7) * (1 if True else 1) * (1 if ex > 0 else 1) if False else ex + w, y - 1)
        setc(c, "#1a0f0a"); c.set_line_width(3.6); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()
        ox = ex + sgn * w
        c.move_to(ox, y - 1 if sgn > 0 else y + 2); c.line_to(ox + sgn * 7, y - 7); setc(c, "#1a0f0a"); c.set_line_width(3); c.stroke()
        for k in range(2):
            lx = ex + sgn * w * (0.62 - k * 0.3); ly = y - h * (0.78 + k * 0.12)
            c.move_to(lx, ly); c.curve_to(lx + sgn * 2, ly - 4, lx + sgn * 5, ly - 6, lx + sgn * 8, ly - 6)
        setc(c, "#1a0f0a"); c.set_line_width(2.2); c.stroke()
        # soft lower lid
        c.move_to(ex - w + 3, y + 3); c.curve_to(ex - w * 0.4, y + h * 0.8, ex + w * 0.4, y + h * 0.8, ex + w - 2, y + 1)
        setc(c, (0.45, 0.25, 0.18, 0.5)); c.set_line_width(1.4); c.stroke()


def mouth(c, y, m, w=16, beard=False):
    if m > 0.1:
        oh = 4 + 14 * min(m, 1.1)
        ell(c, 0, y + oh * 0.35, w * 0.7 + 3 * m, oh * 0.55); fs(c, "#7c1d2c", "#4f0f1b", 2)
        ell(c, 0, y + oh * 0.6, w * 0.4, oh * 0.22); setc(c, "#ff7a8f"); c.fill()
    else:
        c.move_to(-w, y); c.curve_to(-w / 2, y + 10, w / 2, y + 10, w, y)
        setc(c, "#7c1d2c"); c.set_line_width(3.5); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()

# ------------------------------------------------------------------ Tinku (host)
TK_SKIN = "#f3c39f"; TK_HAIR = "#7a4a26"

def tinku(c, x, y, t=0.0, s=1.0, arms=(0.3, 0.3), m=0.0, look=0.0, closed=False, hopy=0.0, lean=0.0):
    c.save(); c.translate(x, y)
    ell(c, 0, 2, 60 * s, 11 * s); setc(c, (0, 0, 0, 0.16)); c.fill()
    c.translate(0, -hopy); c.scale(s, s); c.rotate(lean)
    # legs: jeans + shoes
    for lx in (-20, 20):
        rrect(c, lx - 14, -96, 28, 88, 10); fs(c, "#4a78c2")
        ell(c, lx + (4 if lx > 0 else -4), -8, 24, 12); fs(c, "#ff6b3d")
        rrect(c, lx - 20, -6, 40, 6, 3); setc(c, (1, 1, 1, 0.85)); c.fill()
    rrect(c, -36, -112, 72, 26, 8); fs(c, "#4a78c2")
    # t-shirt
    c.move_to(-44, -196); c.curve_to(-50, -150, -46, -120, -42, -100); c.line_to(42, -100)
    c.curve_to(46, -120, 50, -150, 44, -196); c.close_path()
    g = cairo.LinearGradient(0, -196, 0, -100); g.add_color_stop_rgba(0, *hexc("#ffd93b")); g.add_color_stop_rgba(1, *hexc("#ffbf1f"))
    c.set_source(g); c.fill_preserve(); setc(c, "#c98f00"); c.set_line_width(3); c.stroke()
    c.arc(0, -196, 14, 0, PI); setc(c, "#e8a900"); c.set_line_width(4); c.stroke()
    # sleeves + arms
    hands = []
    for sgn, a in ((-1, arms[0]), (1, arms[1])):
        sx = sgn * 42
        ell(c, sx + sgn * 6, -184, 18, 16); fs(c, "#ffcf2e", "#c98f00", 3)
        hands.append(limb(c, sx + sgn * 6, -180, mir(a, sgn), 74, TK_SKIN, 17))
    # head
    c.save(); c.translate(0, -275); c.rotate(math.sin(t * 2.0) * 0.03 + m * 0.04)
    ell(c, -84, 8, 14, 18); fs(c, TK_SKIN); ell(c, 84, 8, 14, 18); fs(c, TK_SKIN)
    ell(c, 0, 0, 86, 82); fs(c, TK_SKIN, dark(TK_SKIN, 0.72))
    # fluffy messy hair: outlined silhouette, smooth interior, light fringe
    CL = ((-80, -4, 20), (-74, -38, 28), (-50, -66, 30), (-16, -82, 32), (20, -82, 32), (52, -66, 30), (76, -38, 28), (82, -6, 18))
    for hx, hy, r in CL:
        ell(c, hx, hy, r + 3, r * 0.92 + 3); setc(c, dark(TK_HAIR, 0.62)); c.fill()
    for hx, hy, r in CL:
        ell(c, hx, hy, r, r * 0.92); setc(c, TK_HAIR); c.fill()
    c.new_path(); c.arc(0, -8, 84, PI * 1.0, PI * 2.0); c.close_path(); setc(c, TK_HAIR); c.fill()
    for (fx, fy, a, ln) in ((-50, -48, 0.55, 24), (-22, -54, 0.3, 28), (8, -56, 0.05, 30), (36, -52, -0.25, 26), (60, -40, -0.55, 20)):
        c.save(); c.translate(fx, fy); c.rotate(a)
        c.move_to(-15, -4); c.curve_to(-12, ln * 0.5, -2, ln, 6, ln); c.curve_to(4, ln * 0.55, 12, ln * 0.2, 15, -4); c.close_path(); setc(c, TK_HAIR); c.fill()
        c.move_to(-12, 0); c.curve_to(-9, ln * 0.5, -2, ln * 0.9, 5, ln - 1); setc(c, dark(TK_HAIR, 0.72)); c.set_line_width(2); c.stroke()
        c.restore()
    for (sx, sy, a) in ((-36, -70, -0.5), (6, -86, 0.1), (44, -74, 0.6)):
        c.save(); c.translate(sx, sy); c.rotate(a); c.move_to(-12, 6); c.curve_to(-4, -18, 6, -22, 14, -14); setc(c, dark(TK_HAIR, 0.72)); c.set_line_width(2.5); c.stroke(); c.restore()
    c.move_to(-44, -72); c.curve_to(-20, -88, 12, -90, 38, -80); setc(c, (1, 1, 1, 0.16)); c.set_line_width(7); c.stroke()
    # eyes behind round glasses
    eyes(c, (-33, 33), 8, 19, 22, look, closed, "#6b3d1d")
    for gx in (-33, 33):
        ell(c, gx, 8, 30, 29); setc(c, (1, 1, 1, 0.12)); c.fill_preserve(); setc(c, "#3b3330"); c.set_line_width(6); c.stroke()
    c.move_to(-4, 4); c.curve_to(-2, 0, 2, 0, 4, 4); setc(c, "#3b3330"); c.set_line_width(5); c.stroke()
    c.move_to(-63, 2); c.line_to(-82, -2); c.move_to(63, 2); c.line_to(82, -2); c.stroke()
    for bx in (-33, 33):
        c.move_to(bx - 16, -32); c.curve_to(bx - 6, -40, bx + 6, -40, bx + 16, -33); setc(c, TK_HAIR); c.set_line_width(6); c.stroke()
    ell(c, -56, 40, 14, 9); setc(c, (1, 0.45, 0.45, 0.4)); c.fill(); ell(c, 56, 40, 14, 9); c.fill()
    c.move_to(-6, 30); c.curve_to(-3, 36, 3, 36, 6, 30); setc(c, dark(TK_SKIN, 0.6)); c.set_line_width(3); c.stroke()
    if m > 0.1:
        mouth(c, 46, m, 20)
    else:
        c.move_to(-24, 46); c.curve_to(-12, 66, 12, 66, 24, 46); c.close_path(); fs(c, "#7c1d2c", "#4f0f1b", 2.5)
        rrect(c, -16, 47, 32, 7, 3); setc(c, "#ffffff"); c.fill()
    c.restore()
    dev = [c.user_to_device(*h) for h in hands]
    c.restore()
    return dev

# ------------------------------------------------------------------ epic characters
# Each spec drives one shared body builder.
CAST = {
    "krishna":   dict(hi="श्रीकृष्ण", en="Krishna", skin="#4f8fe0", hair="#1c1530", hair_style="long", crown="krishna", tilak="u",
                      top="bare", necklace=3, shawl="#ffd23f", dhoti="#ffc21a", item="flute", mala=True, smile=1, ear="kundal", iris="#2a1a10"),
    "arjun":     dict(hi="अर्जुन", en="Arjun", skin="#d9a16f", hair="#1e1410", hair_style="long", crown="tall", tilak="line",
                      top="bare", necklace=2, shawl="#d6372f", dhoti="#ffffff", item="bow", ear="kundal"),
    "bheem":     dict(hi="भीम", en="Bheem", skin="#b97c4e", hair="#1e1410", hair_style="long", crown="band", tilak="line", build=1.25,
                      top="bare", necklace=2, shawl="#7a3fbf", dhoti="#ff8c1a", item="mace", ear="kundal", brow=1),
    "yudhishthir": dict(hi="युधिष्ठिर", en="Yudhishthir", skin="#d9a16f", hair="#1e1410", hair_style="long", crown="tall", tilak="line",
                      top="bare", necklace=3, shawl="#ffffff", dhoti="#f5c542", item="spear", ear="kundal", beard="short"),
    "karn":      dict(hi="कर्ण", en="Karn", skin="#cf9566", hair="#1e1410", hair_style="wavy", crown="sun", tilak="sun",
                      top="armor", necklace=1, shawl="#ff8c1a", dhoti="#e04a1f", item="bow", ear="sunkundal"),
    "duryodhan": dict(hi="दुर्योधन", en="Duryodhan", skin="#cf9566", hair="#1e1410", hair_style="long", crown="tall", tilak="line",
                      top="bare", necklace=3, shawl="#2c8f5a", dhoti="#8f1f3a", item="mace", ear="kundal", beard="short", brow=2),
    "draupadi":  dict(hi="द्रौपदी", en="Draupadi", skin="#f4caa6", hair="#120c0a", hair_style="braid", crown="queen", tilak="bindi",
                      top="saree", saree="#ff5fa8", border=GOLD, female=True, ear="jhumka", nose=True, sindoor=True, lips="#d81b60", shadow="#b5651d"),
    "bheeshm":   dict(hi="भीष्म पितामह", en="Bheeshm", skin="#e2b58c", hair="#f2f2f2", hair_style="long", crown="silver", tilak="line",
                      top="robe", robe="#f5f0e1", necklace=1, shawl="#c9c9d6", dhoti="#ffffff", item="bow", beard="long", age=1, ear="kundal"),
    "shakuni":   dict(hi="शकुनि", en="Shakuni", skin="#d9a87c", hair="#3a2a20", hair_style="wavy", crown="turban", tilak="none",
                      top="robe", robe="#4b2a6e", necklace=2, shawl="#1f6f6a", dhoti="#2a1d3a", item="dice", beard="goatee", brow=2, lid=0.35, limp=True),
    "abhimanyu": dict(hi="अभिमन्यु", en="Abhimanyu", skin="#d9a16f", hair="#1e1410", hair_style="wavy", crown="band", tilak="line",
                      top="armor2", necklace=1, shawl="#2f7bff", dhoti="#ffd23f", item="sword", ear="kundal", young=1),
    "nakul":     dict(hi="नकुल", en="Nakul", skin="#e6b98f", hair="#1e1410", hair_style="wavy", crown="band", tilak="line",
                      top="bare", necklace=2, shawl="#14a3a3", dhoti="#9fd8ff", item="sword", ear="kundal", young=1),
    "sahadev":   dict(hi="सहदेव", en="Sahadev", skin="#e6b98f", hair="#1e1410", hair_style="wavy", crown="band", tilak="line",
                      top="bare", necklace=2, shawl="#3fae4a", dhoti="#fff0b3", item="scroll", ear="kundal", young=1),
    "shantanu":  dict(hi="राजा शांतनु", en="King Shantanu", skin="#d9a16f", hair="#2a1d14", hair_style="long", crown="tall", tilak="line",
                      top="bare", necklace=3, shawl="#1d8a8a", dhoti="#f5c542", item="none", ear="kundal", beard="short"),
    "ganga":     dict(hi="माँ गंगा", en="Goddess Ganga", skin="#f8dcc4", hair="#1a1414", hair_style="open", crown="goddess", tilak="bindi",
                      top="saree", saree="#4fb8ec", border="#ffffff", female=True, ear="jhumka", item="lotus", glow="#bff0ff", waves=True, lips="#e0567f", shadow="#4f9fd9"),
}


def _crown(c, kind, t):
    if kind in ("tall", "sun", "silver"):
        col, dk = (GOLD, GOLD_D) if kind != "silver" else ("#dfe3ea", "#8a93a6")
        c.move_to(-58, -40); c.curve_to(-60, -80, -44, -118, 0, -132); c.curve_to(44, -118, 60, -80, 58, -40); c.close_path(); fs(c, col, dk, 3)
        rrect(c, -62, -52, 124, 18, 8); fs(c, col, dk, 3)
        for k in range(-2, 3):
            ell(c, k * 22, -43, 4.5, 4.5); setc(c, "#d81b3c" if k % 2 == 0 else "#2a9d5c"); c.fill()
        ell(c, 0, -96, 13, 16); fs(c, "#d81b3c" if kind != "sun" else "#ff6a00", "#7a0d1f", 2.5)
        c.move_to(0, -132); c.line_to(-8, -150); c.line_to(0, -162); c.line_to(8, -150); c.close_path(); fs(c, col, dk, 2.5)
        for sgn in (-1, 1):
            c.move_to(sgn * 30, -70); c.curve_to(sgn * 34, -90, sgn * 22, -104, sgn * 14, -110); setc(c, dk); c.set_line_width(2.5); c.stroke()
        if kind == "sun":
            c.save(); c.translate(0, -96)
            for i in range(10):
                c.save(); c.rotate(i * PI / 5); poly(c, [(-4, -18), (0, -28), (4, -18)]); setc(c, "#ffe066"); c.fill(); c.restore()
            c.restore()
    elif kind == "krishna":
        rrect(c, -56, -52, 112, 18, 8); gold(c, 3)
        c.move_to(-50, -40); c.curve_to(-52, -80, -30, -100, 0, -104); c.curve_to(30, -100, 52, -80, 50, -40); c.close_path(); gold(c, 3)
        ell(c, 0, -76, 10, 12); fs(c, "#d81b3c", "#7a0d1f", 2)
        # peacock feather
        c.save(); c.translate(22, -96); c.rotate(0.35 + 0.05 * math.sin(t * 2))
        c.move_to(0, 0); c.curve_to(-4, -30, -2, -60, 0, -80); setc(c, "#2f9a47"); c.set_line_width(3); c.stroke()
        ell(c, 0, -74, 18, 30); fs(c, "#1fa38a", "#0f6b5a", 2)
        ell(c, 0, -80, 12, 17); setc(c, "#1f6fe0"); c.fill()
        ell(c, 0, -82, 7, 10); setc(c, "#0b1d4f"); c.fill()
        ell(c, 0, -84, 3, 4); setc(c, "#ffd23f"); c.fill()
        c.restore()
    elif kind == "band":
        rrect(c, -62, -48, 124, 20, 9); gold(c, 3)
        ell(c, 0, -38, 9, 10); fs(c, "#d81b3c", "#7a0d1f", 2)
        poly(c, [(-14, -48), (0, -74), (14, -48)]); gold(c, 2.5)
    elif kind == "tiara":
        c.move_to(-46, -40); c.curve_to(-30, -62, 30, -62, 46, -40); setc(c, GOLD_D); c.set_line_width(7); c.stroke()
        c.move_to(-46, -40); c.curve_to(-30, -62, 30, -62, 46, -40); setc(c, GOLD); c.set_line_width(4); c.stroke()
        for k in (-28, -14, 0, 14, 28):
            ell(c, k, -54 + abs(k) * 0.18, 4.5, 4.5); setc(c, "#d81b3c" if k == 0 else "#ffffff"); c.fill()
        # maang tikka
        c.move_to(0, -54); c.line_to(0, -36); setc(c, GOLD_D); c.set_line_width(2.5); c.stroke()
        ell(c, 0, -32, 6, 7); fs(c, GOLD, GOLD_D, 2)
    elif kind in ("queen", "goddess"):
        c.move_to(-50, -36); c.curve_to(-30, -58, 30, -58, 50, -36); c.line_to(50, -48)
        peaks = [(-44, -58, -36, -84), (-24, -66, -14, -100), (0, -70, 0, -116), (24, -66, 14, -100), (44, -58, 36, -84)]
        c.move_to(-50, -40)
        for (bx, by, tx, ty) in peaks:
            c.line_to(bx - 6, by + 8); c.line_to(tx, ty); c.line_to(bx + 8, by + 6)
        c.line_to(50, -40); c.curve_to(30, -52, -30, -52, -50, -40); c.close_path(); gold(c, 2.5)
        c.move_to(-52, -38); c.curve_to(-30, -56, 30, -56, 52, -38); setc(c, GOLD_D); c.set_line_width(9); c.stroke()
        c.move_to(-52, -38); c.curve_to(-30, -56, 30, -56, 52, -38); setc(c, GOLD); c.set_line_width(6); c.stroke()
        for k in range(-4, 5):
            ell(c, k * 11, -46 - (16 - abs(k) * 2) * 0.35, 3, 3); setc(c, "#ffffff"); c.fill()
        gem = "#d81b3c" if kind == "queen" else "#2fb8e0"
        for (bx, by, tx, ty) in peaks:
            ell(c, tx, ty + 4, 4.5, 4.5); setc(c, "#ffffff"); c.fill()
        ell(c, 0, -76, 10, 13); fs(c, gem, dark(gem, 0.6), 2); ell(c, -3, -80, 3, 4); setc(c, (1, 1, 1, 0.7)); c.fill()
        for sx in (-26, 26):
            ell(c, sx, -66, 5, 6); fs(c, "#2a9d5c" if kind == "queen" else "#ffffff", GOLD_D, 1.5)
        # maang tikka
        c.move_to(0, -50); c.line_to(0, -36); setc(c, GOLD_D); c.set_line_width(2.5); c.stroke()
        ell(c, 0, -31, 6, 7); fs(c, GOLD, GOLD_D, 2); ell(c, 0, -30, 2.5, 3); setc(c, gem); c.fill()
    elif kind == "turban":
        ell(c, 0, -52, 70, 44); fs(c, "#c0392b", "#7a1f15", 3)
        for k in range(3):
            c.move_to(-66, -64 + k * 14); c.curve_to(-20, -84 + k * 14, 30, -50 + k * 14, 66, -66 + k * 14); setc(c, "#e8604f"); c.set_line_width(4); c.stroke()
        ell(c, 8, -74, 12, 12); fs(c, GOLD, GOLD_D, 2)
        c.move_to(8, -84); c.curve_to(14, -110, 30, -116, 36, -108); setc(c, "#ffffff"); c.set_line_width(6); c.stroke()


def hero(c, key, x, y, t=0.0, s=1.0, arms=(0.25, 0.25), m=0.0, look=0.0, closed=False, hopy=0.0, lean=0.0, face=1, item_on=True, mood=None, kneel=0.0):
    p = CAST[key]
    skin = p["skin"]; b = p.get("build", 1.0); fem = p.get("female", False)
    young = p.get("young", 0)
    c.save(); c.translate(x, y)
    ell(c, 0, 2, 64 * s * b, 11 * s); setc(c, (0, 0, 0, 0.16)); c.fill()
    c.translate(0, -hopy + kneel * 70 * s); c.scale(s * face, s); c.rotate(lean)
    sh = 1.0 if not young else 0.92
    c.scale(1, sh)
    glow = p.get("glow")
    if glow:
        gr = cairo.RadialGradient(0, -260, 30, 0, -260, 260); gr.add_color_stop_rgba(0, *hexc(glow, 0.55)); gr.add_color_stop_rgba(1, *hexc(glow, 0))
        c.set_source(gr); c.arc(0, -260, 260, 0, 2 * PI); c.fill()
    hair = p["hair"]; hs = p["hair_style"]
    HS = 1.22  # head scale
    # back hair
    if fem and hs in ("open", "braid"):
        ln = {"open": 260, "braid": 130}[hs]
        c.move_to(-70, -420); c.curve_to(-92, -370, -90, -420 + ln * 0.8, -72, -420 + ln)
        c.line_to(72, -420 + ln); c.curve_to(90, -420 + ln * 0.8, 92, -370, 70, -420); c.close_path(); fs(c, hair)
        if hs == "braid":
            for k in range(6):
                ell(c, 48, -280 + k * 30, 16, 18); fs(c, hair)
            for k in range(7):
                ell(c, 30 + (k % 2) * 6, -300 + k * 26, 5.5, 5.5); fs(c, "#ffffff", (0.78, 0.8, 0.72, 1), 1.2)
            ell(c, 48, -98, 8, 8); setc(c, GOLD); c.fill()
    elif not fem and p.get("beard") == "long":
        c.move_to(-70, -440); c.curve_to(-96, -400, -92, -330, -70, -300); c.line_to(70, -300)
        c.curve_to(92, -330, 96, -400, 70, -440); c.close_path(); fs(c, hair, (0.7, 0.7, 0.75, 1))
    elif not fem:
        # neat neck-length hair with curled ends
        c.move_to(-72, -440); c.curve_to(-90, -410, -88, -372, -74, -352)
        for k in range(5):
            x0 = -74 + k * 29.6
            c.curve_to(x0 + 6, -340, x0 + 22, -340, x0 + 29.6, -352)
        c.curve_to(88, -372, 90, -410, 72, -440); c.close_path(); fs(c, hair)
    if p.get("item") == "bow" and item_on:
        c.save(); c.translate(-40, -300); c.rotate(-0.45)
        for k, dx in enumerate((-10, 0, 10)):
            c.move_to(dx, -40); c.line_to(dx, -120); setc(c, "#8a5a2b"); c.set_line_width(4); c.stroke()
            poly(c, [(dx - 7, -96), (dx, -86), (dx + 7, -96), (dx + 7, -124), (dx, -114), (dx - 7, -124)]); fs(c, ["#ffffff", "#ff7a3d", "#ffffff"][k], "#9a7a6a", 1.5)
        rrect(c, -22, -60, 44, 150, 14); fs(c, "#8a3b12", "#4a1d08", 3)
        rrect(c, -22, -56, 44, 14, 6); gold(c, 2); rrect(c, -22, 60, 44, 12, 6); gold(c, 2)
        c.restore()
    # legs / lower garment
    if fem:
        sr = p["saree"]
        c.move_to(-50, -205); c.curve_to(-62, -120, -70, -50, -76, -6); c.line_to(76, -6); c.curve_to(70, -50, 62, -120, 50, -205); c.close_path()
        g = cairo.LinearGradient(0, -205, 0, -6); g.add_color_stop_rgba(0, *light(sr, 0.18)); g.add_color_stop_rgba(1, *dark(sr, 0.85))
        c.set_source(g); c.fill_preserve(); setc(c, dark(sr, 0.65)); c.set_line_width(3); c.stroke()
        if p.get("waves"):
            for row in range(4):
                yy = -170 + row * 38
                for k in range(-3, 4):
                    c.arc(k * 18 + (row % 2) * 9, yy, 8, PI, 2 * PI); setc(c, (1, 1, 1, 0.55)); c.set_line_width(2); c.stroke()
        else:
            for row in range(4):
                for k in range(-2, 3):
                    ell(c, k * 22 + (row % 2) * 11, -165 + row * 36, 3.2, 3.2); setc(c, p["border"]); c.fill()
        for k in range(-2, 3):
            c.move_to(k * 12, -150); c.line_to(k * 20, -8); setc(c, dark(sr, 0.85)); c.set_line_width(2.5); c.stroke()
        c.move_to(-76, -12); c.line_to(76, -12); setc(c, p["border"]); c.set_line_width(9); c.stroke()
        for fx in (-24, 24):
            ell(c, fx, -2, 20, 9); fs(c, skin)
    else:
        dh = p["dhoti"]
        for lx in (-26 * b, 26 * b):
            rrect(c, lx - 13, -90, 26, 84, 10); fs(c, skin)
            ell(c, lx + (4 if lx > 0 else -4), -6, 22, 10); fs(c, "#8a5a2b")
        c.move_to(-52 * b, -210); c.curve_to(-60 * b, -150, -66 * b, -110, -60 * b, -78); c.curve_to(-30, -70, 30, -70, 60 * b, -78)
        c.curve_to(66 * b, -110, 60 * b, -150, 52 * b, -210); c.close_path(); fs(c, dh)
        c.move_to(-8, -200); c.curve_to(-14, -150, -4, -110, -10, -74); c.move_to(14, -196); c.curve_to(8, -150, 18, -110, 12, -78)
        setc(c, dark(dh, 0.8)); c.set_line_width(2.5); c.stroke()
        c.move_to(-60 * b, -80); c.curve_to(-30, -72, 30, -72, 60 * b, -80); setc(c, GOLD); c.set_line_width(6); c.stroke()
    # torso
    top = p["top"]
    if fem:
        c.move_to(-46, -330); c.curve_to(-52, -280, -50, -240, -48, -200); c.line_to(48, -200); c.curve_to(50, -240, 52, -280, 46, -330); c.close_path(); fs(c, skin)
        c.move_to(-46, -330); c.curve_to(-50, -300, -48, -280, -46, -262); c.line_to(46, -262); c.curve_to(48, -280, 50, -300, 46, -330); c.close_path(); fs(c, dark(p["saree"], 0.8))
        # pallu across chest and over shoulder
        c.move_to(-50, -205); c.line_to(-20, -205); c.line_to(50, -330); c.line_to(54, -300); c.line_to(18, -200); c.close_path()
        c.move_to(-48, -260); c.curve_to(-10, -250, 30, -300, 52, -334); c.line_to(60, -300); c.curve_to(40, -240, 0, -205, -48, -205); c.close_path()
        fs(c, p["saree"])
        c.move_to(-48, -258); c.curve_to(-10, -248, 30, -298, 52, -332); setc(c, p["border"]); c.set_line_width(6); c.stroke()
        rrect(c, -50, -214, 100, 14, 6); gold(c, 2)
        c.move_to(-20, -334); c.curve_to(-16, -318, 16, -318, 20, -334); setc(c, GOLD_D); c.set_line_width(7); c.stroke()
        c.move_to(-20, -334); c.curve_to(-16, -318, 16, -318, 20, -334); setc(c, GOLD); c.set_line_width(4); c.stroke()
        for k in range(5):
            ell(c, -12 + k * 6, -322 + abs(k - 2) * -1.5, 2.6, 3.4); setc(c, "#d81b3c" if k % 2 == 0 else "#2a9d5c"); c.fill()
        c.move_to(-30, -332); c.curve_to(-26, -280, 26, -280, 30, -332); setc(c, GOLD); c.set_line_width(3); c.stroke()
        ell(c, 0, -287, 9, 11); fs(c, GOLD, GOLD_D, 2); ell(c, 0, -287, 4, 5); setc(c, "#d81b3c"); c.fill()
    else:
        w = 62 * b; wb = 46 * b
        c.move_to(-w, -338); c.curve_to(-w - 4, -300, -wb - 4, -250, -wb, -205); c.line_to(wb, -205); c.curve_to(wb + 4, -250, w + 4, -300, w, -338)
        c.curve_to(30, -348, -30, -348, -w, -338); c.close_path()
        if top in ("bare",):
            fs(c, skin)
            c.move_to(-34, -296); c.curve_to(-24, -284, -10, -284, -3, -292); c.move_to(34, -296); c.curve_to(24, -284, 10, -284, 3, -292)
            c.move_to(0, -280); c.line_to(0, -222)
            for yy in (-258, -236):
                c.move_to(-14, yy); c.curve_to(-8, yy + 3, -4, yy + 3, -2, yy); c.move_to(14, yy); c.curve_to(8, yy + 3, 4, yy + 3, 2, yy)
            setc(c, dark(skin, 0.78)); c.set_line_width(2.5); c.stroke()
        elif top == "robe":
            fs(c, p["robe"])
            c.move_to(0, -338); c.line_to(0, -205); setc(c, dark(p["robe"], 0.75)); c.set_line_width(2.5); c.stroke()
            for k in range(4):
                ell(c, 0, -320 + k * 32, 4, 4); setc(c, GOLD); c.fill()
        elif top == "armor":
            g = cairo.RadialGradient(0, -280, 10, 0, -280, 90); g.add_color_stop_rgba(0, *hexc("#fff6b0")); g.add_color_stop_rgba(1, *hexc("#e9a81a"))
            c.set_source(g); c.fill_preserve(); setc(c, GOLD_D); c.set_line_width(3); c.stroke()
            c.save(); c.translate(0, -282)
            for i in range(12):
                c.save(); c.rotate(i * PI / 6 + t * 0.4); poly(c, [(-5, -14), (0, -38), (5, -14)]); setc(c, (1, 1, 1, 0.85)); c.fill(); c.restore()
            ell(c, 0, 0, 14, 14); setc(c, "#ffffff"); c.fill(); c.restore()
        elif top == "armor2":
            fs(c, "#c9a227", GOLD_D, 3)
            for k in range(3):
                c.move_to(-w + 8, -320 + k * 36); c.curve_to(-20, -310 + k * 36, 20, -310 + k * 36, w - 8, -320 + k * 36); setc(c, GOLD_D); c.set_line_width(2.5); c.stroke()
        # necklaces
        for k in range(p.get("necklace", 1)):
            c.move_to(-34 - k * 4, -334); c.curve_to(-26, -300 + k * 16, 26, -300 + k * 16, 34 + k * 4, -334)
            setc(c, GOLD_D); c.set_line_width(6); c.stroke()
            c.move_to(-34 - k * 4, -334); c.curve_to(-26, -300 + k * 16, 26, -300 + k * 16, 34 + k * 4, -334)
            setc(c, GOLD); c.set_line_width(3.5); c.stroke()
        ell(c, 0, -306 + 16 * (p.get("necklace", 1) - 1), 7, 8); fs(c, "#d81b3c", "#7a0d1f", 2)
        if p.get("mala"):
            c.move_to(-36, -330); c.curve_to(-40, -240, 40, -240, 36, -330)
            c.set_dash([0.1, 11]); c.set_line_cap(cairo.LINE_CAP_ROUND); setc(c, "#ff8fc7"); c.set_line_width(9); c.stroke(); c.set_dash([])
        # uttariya (shawl) across body
        sc = p["shawl"]
        c.move_to(-w + 2, -338); c.curve_to(-20, -300, 20, -250, w - 4, -212); c.line_to(w - 2, -236)
        c.curve_to(14, -270, -20, -320, -w + 18, -346); c.close_path(); fs(c, sc)
        c.move_to(-w - 2, -336); c.curve_to(-w - 18, -280, -w - 22, -220, -w - 12, -170); c.line_to(-w + 2, -176)
        c.curve_to(-w - 6, -220, -w - 2, -280, -w + 10, -336); c.close_path(); fs(c, sc)
    # arms
    hands = []
    for sgn, a in ((-1, arms[0]), (1, arms[1])):
        sx = sgn * (58 * b if not fem else 44)
        if fem:
            ell(c, sx, -322, 14, 13); fs(c, dark(p["saree"], 0.8))
        hands.append(limb(c, sx, -322, mir(a, sgn), 118 if not fem else 110, skin, (19 if not fem else 15) * (1.15 if b > 1 else 1),
                          cuff=True, band=not fem))
    # neck + head
    rrect(c, -16, -364, 32, 34, 10); fs(c, skin)
    c.save(); c.translate(0, -418); c.scale(HS, HS); c.rotate(math.sin(t * 1.7) * 0.025 + m * 0.03)
    ear = p.get("ear")
    for sgn in (-1, 1):
        ell(c, sgn * 58, 6, 11, 15); fs(c, skin)
        if ear == "kundal":
            ell(c, sgn * 60, 28, 8, 8); fs(c, GOLD, GOLD_D, 2)
        elif ear == "sunkundal":
            gr = cairo.RadialGradient(sgn * 60, 30, 2, sgn * 60, 30, 20); gr.add_color_stop_rgba(0, 1, 1, 0.8, 1); gr.add_color_stop_rgba(1, 1, 0.8, 0.2, 0)
            c.set_source(gr); c.arc(sgn * 60, 30, 20, 0, 2 * PI); c.fill(); ell(c, sgn * 60, 30, 9, 9); fs(c, "#ffe066", GOLD_D, 2)
        elif ear == "jhumka":
            c.move_to(sgn * 58, 18); c.line_to(sgn * 58, 26); setc(c, GOLD_D); c.set_line_width(2); c.stroke()
            c.arc(sgn * 58, 34, 9, PI, 2 * PI); c.close_path(); gold(c, 2)
    if fem:
        c.move_to(-56, -6); c.curve_to(-56, -56, -28, -64, 0, -64); c.curve_to(28, -64, 56, -56, 56, -6)
        c.curve_to(56, 34, 30, 62, 0, 66); c.curve_to(-30, 62, -56, 34, -56, -6); c.close_path(); fs(c, skin, dark(skin, 0.75), 2.5)
    elif young:
        ell(c, 0, 0, 58, 62); fs(c, skin, dark(skin, 0.72))
    else:
        c.move_to(-58, -6); c.curve_to(-58, -56, -30, -64, 0, -64); c.curve_to(30, -64, 58, -56, 58, -6)
        c.curve_to(58, 30, 46, 56, 0, 64); c.curve_to(-46, 56, -58, 30, -58, -6); c.close_path(); fs(c, skin, dark(skin, 0.72))
    # front hair
    if hs != "none":
        c.new_path(); c.arc(0, -4, 61, PI * 1.02, PI * 1.98)
        if fem:
            c.curve_to(54, -30, 30, -44, 4, -58); c.line_to(-4, -58); c.curve_to(-30, -44, -54, -30, -60, -8)
        else:
            c.curve_to(60, -30, 50, -40, 36, -42); c.curve_to(20, -46, 0, -40, -14, -46); c.curve_to(-30, -52, -50, -40, -60, -8)
        c.close_path(); fs(c, hair)
        for sgn in (-1, 1):  # side locks
            if fem:
                c.move_to(sgn * 54, -20); c.curve_to(sgn * 70, 10, sgn * 66, 40, sgn * 58, 60); c.curve_to(sgn * 52, 40, sgn * 52, 10, sgn * 46, -14)
            else:
                c.move_to(sgn * 56, -26); c.curve_to(sgn * 64, -6, sgn * 62, 8, sgn * 56, 16); c.curve_to(sgn * 52, 4, sgn * 52, -10, sgn * 48, -20)
            c.close_path(); fs(c, hair)
    if fem:
        if p.get("sindoor"):
            c.move_to(0, -62); c.line_to(0, -50); setc(c, "#e0162b"); c.set_line_width(3.5); c.stroke()
    # face
    age = p.get("age", 0)
    brow = p.get("brow", 0)
    if fem:
        feye(c, (-23, 23), 8, 17, 12, look, closed, p.get("iris", "#4a2a14"))
    else:
        eyes(c, (-22, 22), 6, 12, 14, look, closed, p.get("iris", "#3a2414"), p.get("lid", 0))
        for ex in (-22, 22):  # defined upper lid (smart, confident look)
            c.arc(ex, 6, 12.5, 1.12 * PI, 1.9 * PI); setc(c, "#1a0f0a"); c.set_line_width(3.5); c.stroke()
    for sgn in (-1, 1):
        tilt = {0: 0, 1: 3, 2: 7}[brow] if True else 0
        if fem:
            c.move_to(sgn * 40, -8); c.curve_to(sgn * 34, -20, sgn * 22, -22, sgn * 10, -14)
            setc(c, "#2a1a12"); c.set_line_width(3); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()
        else:
            if mood == "sad": tilt = -6
            c.move_to(sgn * 34, -16 + (0 if not brow else -tilt * 0.3)); c.curve_to(sgn * 26, -24, sgn * 16, -22 + tilt, sgn * 10, -16 + tilt)
            setc(c, hair if not age else "#d9d9d9"); c.set_line_width(5); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()
    if age:
        for sgn in (-1, 1):
            c.move_to(sgn * 34, 22); c.curve_to(sgn * 30, 26, sgn * 26, 26, sgn * 22, 24); setc(c, dark(skin, 0.7)); c.set_line_width(2); c.stroke()
    if fem:
        c.move_to(-3, 24); c.curve_to(-4, 29, 4, 29, 3, 24); setc(c, dark(skin, 0.7)); c.set_line_width(2); c.stroke()
    else:
        c.move_to(-4, 20); c.curve_to(-6, 28, 6, 28, 4, 20); setc(c, dark(skin, 0.62)); c.set_line_width(2.5); c.stroke()
    if p.get("nose"):
        c.arc(-5, 29, 4, 0.2 * PI, 1.5 * PI); setc(c, GOLD); c.set_line_width(2); c.stroke(); ell(c, -5, 33, 1.8, 1.8); setc(c, '#ffffff'); c.fill()
    ell(c, -36, 26, 11 if fem else 10, 6.5 if fem else 6); setc(c, (1, 0.42, 0.5, 0.3 if not fem else 0.38)); c.fill(); ell(c, 36, 26, 11 if fem else 10, 6.5 if fem else 6); c.fill()
    beard = p.get("beard")
    if beard == "long":
        bc = hair
        c.move_to(-50, 10); c.curve_to(-58, 70, -30, 130, 0, 150); c.curve_to(30, 130, 58, 70, 50, 10); c.curve_to(36, 44, 20, 50, 0, 50)
        c.curve_to(-20, 50, -36, 44, -50, 10); c.close_path(); fs(c, bc, (0.7, 0.7, 0.75, 1), 2.5)
        for k in (-20, 0, 20):
            c.move_to(k, 60); c.curve_to(k + 4, 90, k - 2, 110, k * 0.5, 135); setc(c, (0.75, 0.75, 0.8, 1)); c.set_line_width(2); c.stroke()
    elif beard == "short":
        c.move_to(-48, 18); c.curve_to(-46, 66, 46, 66, 48, 18); c.curve_to(30, 44, -30, 44, -48, 18); c.close_path(); fs(c, hair)
    elif beard == "goatee":
        c.move_to(-12, 50); c.curve_to(-10, 76, 10, 76, 12, 50); c.close_path(); fs(c, hair)
    if beard in ("long", "short", "goatee"):
        c.move_to(-22, 34); c.curve_to(-10, 26, 10, 26, 22, 34); c.curve_to(10, 32, -10, 32, -22, 34); setc(c, hair); c.set_line_width(6); c.stroke()
    if mood == "sad" and m <= 0.1:
        c.move_to(-12, 46); c.curve_to(-6, 39, 6, 39, 12, 46); setc(c, "#7c1d2c" if not fem else p.get("lips", "#d6336c")); c.set_line_width(3.5); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()
    elif fem and m <= 0.1:
        lc = p.get("lips", "#d6336c")
        c.move_to(-11, 41); c.curve_to(-6, 36, -2, 37, 0, 39); c.curve_to(2, 37, 6, 36, 11, 41)
        c.curve_to(6, 49, -6, 49, -11, 41); c.close_path(); fs(c, lc, dark(lc, 0.72), 1.2)
        c.move_to(-11, 41); c.curve_to(-5, 43.5, 5, 43.5, 11, 41); setc(c, dark(lc, 0.6)); c.set_line_width(1.3); c.stroke()
        ell(c, 3, 45, 3, 1.3); setc(c, (1, 1, 1, 0.5)); c.fill()
    else:
        mouth(c, 40, m, 15 if not fem else 12)
    # tilak / bindi
    tk = p.get("tilak")
    if tk == "line":
        rrect(c, -3, -30, 6, 18, 3); setc(c, "#d8231f"); c.fill()
    elif tk == "u":
        c.move_to(-8, -38); c.curve_to(-8, -18, 8, -18, 8, -38); setc(c, "#fff1c4"); c.set_line_width(4); c.stroke()
        rrect(c, -2.5, -32, 5, 14, 2); setc(c, "#d8231f"); c.fill()
    elif tk == "sun":
        ell(c, 0, -24, 6, 6); setc(c, "#ff8c1a"); c.fill()
        for i in range(8):
            a = i * PI / 4; c.move_to(9 * math.cos(a), -24 + 9 * math.sin(a)); c.line_to(13 * math.cos(a), -24 + 13 * math.sin(a))
        setc(c, "#ff8c1a"); c.set_line_width(2); c.stroke()
    elif tk == "bindi":
        ell(c, 0, -20, 4.5, 4.5); setc(c, "#d8231f"); c.fill()
    _crown(c, p.get("crown"), t)
    c.restore()
    # item in right hand (screen right when face=1)
    item = p.get("item", "none") if item_on else "none"
    hx, hy = hands[1]
    if item == "flute":
        c.save(); c.translate(hx, hy); c.rotate(-0.5)
        rrect(c, -90, -6, 150, 12, 6); fs(c, "#d9a441", "#8a5a12", 2.5)
        for k in range(5): ell(c, -60 + k * 18, 0, 2.6, 2.6); setc(c, "#5a3a0a"); c.fill()
        c.restore()
    elif item == "bow":
        c.save(); c.translate(hx, hy)
        L = 150
        # limbs: D-shaped recurve bow seen from the side, belly facing outward
        for sgn in (-1, 1):
            c.move_to(0, sgn * 10)
            c.curve_to(22, sgn * 50, 30, sgn * 110, 10, sgn * (L - 8))
            c.curve_to(6, sgn * (L - 2), 2, sgn * L, -6, sgn * (L + 6))   # recurved tip
            c.set_line_cap(cairo.LINE_CAP_ROUND)
            setc(c, "#4a2410"); c.set_line_width(11); c.stroke_preserve()
            setc(c, "#9a5a2a"); c.set_line_width(7); c.stroke_preserve()
            setc(c, (1, 0.85, 0.6, 0.5)); c.set_line_width(2); c.stroke()
            ell(c, -6, sgn * (L + 6), 5, 5); gold(c, 1.5)
            for k in (0.35, 0.62):  # gold bands on the limbs
                yy = sgn * L * k; xx = 22 * math.sin(PI * k) + 6
                c.save(); c.translate(xx, yy); rrect(c, -7, -4, 14, 8, 3); gold(c, 1.5); c.restore()
        # bow string (straight, taut)
        c.move_to(-6, -(L + 4)); c.line_to(-6, L + 4); setc(c, (0.97, 0.95, 0.88, 1)); c.set_line_width(2); c.stroke()
        # grip wrap
        rrect(c, -9, -22, 18, 44, 7); fs(c, "#7a1f1f", "#3f0d0d", 2)
        for k in range(4):
            c.move_to(-9, -16 + k * 11); c.line_to(9, -10 + k * 11); setc(c, GOLD); c.set_line_width(2); c.stroke()
        c.restore()
    elif item == "mace":
        c.save(); c.translate(hx, hy); c.rotate(0.25)
        rrect(c, -6, -110, 12, 140, 5); fs(c, "#8a5a2b")
        ell(c, 0, -128, 34, 38); fs(c, GOLD, GOLD_D, 3)
        for k in range(3): c.move_to(-32, -140 + k * 14); c.curve_to(-10, -132 + k * 14, 10, -132 + k * 14, 32, -140 + k * 14)
        setc(c, GOLD_D); c.set_line_width(2.5); c.stroke()
        ell(c, 0, -170, 7, 9); gold(c, 2); c.restore()
    elif item == "spear":
        c.save(); c.translate(hx, hy)
        rrect(c, -4, -260, 8, 330, 4); fs(c, "#8a5a2b")
        poly(c, [(-12, -258), (0, -300), (12, -258)]); fs(c, "#dfe3ea", "#8a93a6", 2.5)
        ell(c, 0, -254, 9, 6); gold(c, 2); c.restore()
    elif item == "sword":
        c.save(); c.translate(hx, hy); c.rotate(0.35)
        poly(c, [(-6, -10), (-6, -150), (0, -168), (6, -150), (6, -10)]); fs(c, "#dfe3ea", "#8a93a6", 2.5)
        rrect(c, -22, -12, 44, 10, 4); gold(c, 2); rrect(c, -5, -2, 10, 26, 4); fs(c, "#8a5a2b"); c.restore()
    elif item == "dice":
        for k, (dx, dy, a) in enumerate(((-10, -14, 0.3), (14, -6, -0.2))):
            c.save(); c.translate(hx + dx, hy + dy); c.rotate(a)
            rrect(c, -12, -12, 24, 24, 5); fs(c, "#fff7e6", "#8a6a3a", 2)
            for px, py in ((-5, -5), (5, 5), (0, 0)) if k == 0 else ((-5, -5), (5, 5)):
                ell(c, px, py, 2.6, 2.6); setc(c, "#c0392b"); c.fill()
            c.restore()
    elif item == "scroll":
        c.save(); c.translate(hx, hy); c.rotate(-0.2)
        rrect(c, -10, -60, 34, 70, 4); fs(c, "#f7e7b8", "#b08a3a", 2)
        for k in range(4): c.move_to(-4, -48 + k * 14); c.line_to(18, -48 + k * 14)
        setc(c, (0.55, 0.35, 0.1, 0.6)); c.set_line_width(2); c.stroke()
        for yy in (-62, 10): rrect(c, -14, yy - 4, 42, 10, 5); fs(c, "#a0522d")
        c.restore()
    elif item == "lotus":
        c.save(); c.translate(hx, hy - 10)
        for i, a in enumerate((-0.9, -0.45, 0, 0.45, 0.9)):
            c.save(); c.rotate(a); ell(c, 0, -22, 10, 24); fs(c, "#ff8fc7" if i % 2 else "#ffb3d9", "#d9407c", 2); c.restore()
        ell(c, 0, -6, 10, 6); setc(c, "#ffd23f"); c.fill(); c.restore()
    dev = [c.user_to_device(*h) for h in hands]
    c.restore()
    return dev


# ------------------------------------------------------------------ shaped text (Hindi needs raqm shaping)
from PIL import Image, ImageDraw, ImageFont
import numpy as _np, os as _os
_FONTS = {"hi": _os.path.expanduser("~/.fonts/Baloo2%5Bwght%5D.ttf"), "en": _os.path.expanduser("~/.fonts/Fredoka%5Bwdth,wght%5D.ttf")}
_cache = {}

def text_surface(text, size, fill="#ffffff", stroke=None, stroke_w=0, lang="hi", weight="ExtraBold"):
    key = (text, size, fill, stroke, stroke_w, lang, weight)
    if key in _cache: return _cache[key]
    f = ImageFont.truetype(_FONTS[lang], size, layout_engine=ImageFont.Layout.RAQM)
    try: f.set_variation_by_name(weight if lang == "hi" else "Bold")
    except Exception: pass
    l, t_, r, b_ = f.getbbox(text, stroke_width=stroke_w)
    im = Image.new("RGBA", (r - l + 8, b_ - t_ + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.text((4 - l, 4 - t_), text, font=f, fill=fill, stroke_width=stroke_w, stroke_fill=stroke)
    a = _np.array(im).astype(_np.float32)
    al = a[..., 3:4] / 255.0
    bgra = _np.concatenate([a[..., 2:3] * al, a[..., 1:2] * al, a[..., 0:1] * al, a[..., 3:4]], axis=2).astype(_np.uint8)
    h, w = bgra.shape[:2]
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    stride = surf.get_stride(); buf = surf.get_data()
    arr = _np.ndarray((h, stride // 4, 4), _np.uint8, buffer=buf); arr[:, :w] = bgra; surf.mark_dirty()
    _cache[key] = surf
    return surf

def draw_text(c, text, x, y, size, fill="#ffffff", stroke=None, stroke_w=0, lang="hi", anchor="c", alpha=1.0):
    sf = text_surface(text, size, fill, stroke, stroke_w, lang)
    w, h = sf.get_width(), sf.get_height()
    ox = {"c": w / 2, "l": 0, "r": w}[anchor]
    c.set_source_surface(sf, x - ox, y - h / 2); c.paint_with_alpha(alpha)
    return w, h
