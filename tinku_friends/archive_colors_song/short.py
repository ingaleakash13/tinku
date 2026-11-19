"""YouTube Short (9:16, <=30 s) cut from the episode: re-framed tighter on the kids, big title + big lyric captions.
usage: python3 short.py T_START T_END out.mp4"""
import sys, math, subprocess, cairo
import draw
from draw import *

SW, SH = 1080, 1920
T0, T1, OUT = float(sys.argv[1]), float(sys.argv[2]), sys.argv[3]

# tighter kid line-up in verses so the vertical crop holds everyone; captions are drawn by the Short itself
draw.gang.__defaults__ = ((300, 450, 595, 730),) + draw.gang.__defaults__[1:]
draw.captions = lambda c, t: None
def echo_short(c, t, key, colsyl, cue):
    l = LBY[cue]; word = "".join(colsyl).upper(); col = COL[key]
    for k in range(3):
        t0 = draw._WT[cue][k][1] if draw.SPOKEN else T(l["beat"] + k)
        if t < t0 - 0.05: continue
        q = back(prog(t, t0 - 0.05, t0 + 0.25))
        if q < 0.02: continue
        hop = 20 * math.sin(PI * clamp((t - t0) / 0.4))
        c.save(); c.translate(330 + k * 235, 150 - hop); c.scale(q, q); c.rotate((k - 1) * 0.12)
        draw_text(c, word + "!", 0, 0, 58, col, "#ffffff", 8, lang="en"); c.restore()
draw.echo_words = echo_short

def crop_center(t):
    sec = section_at(t); return 565 if sec[2] == "verse" else 612
CW = 760; SC = SW / CW; PH = int(720 * SC); PY = 430   # sharp panel: 1080 x 1023 at y=430

def wrap(c, txt, size, maxw):
    c.select_font_face("Fredoka", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); c.set_font_size(size)
    if c.text_extents(txt).x_advance <= maxw: return [txt]
    words = txt.split(); best = None
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        w = max(c.text_extents(a).x_advance, c.text_extents(b).x_advance)
        if best is None or w < best[0]: best = (w, [a, b])
    return best[1]

def short_caption(c, t):
    cur = None
    for i, l in enumerate(LINES):
        a = T(l["beat"]) - 0.25; nxt = T(LINES[i + 1]["beat"]) - 0.25 if i + 1 < len(LINES) else 1e9
        end = T(l["beat"] + sum(sum(d for _, d in n) for _, n in l["notes"])) + 0.3
        if a <= t <= min(end, nxt): cur = l
    if not cur: return
    al = clamp((t - T(cur["beat"]) + 0.25) / 0.15)
    name, col = NAMES[cur["spk"]]
    lines = wrap(c, cur["cap"], 58, 940)
    bh = 40 + 74 * len(lines); by = 1560; bx, bw = 50, 980
    c.push_group()
    rrect(c, bx + 4, by + 6, bw, bh, 34); setc(c, (0.1, 0.05, 0.2, 0.3)); c.fill()
    rrect(c, bx, by, bw, bh, 34); fs(c, (1, 1, 1, 0.96), hexc(col), 7)
    nw = text_surface(name, 36, "#ffffff", None, 0, "en").get_width()
    rrect(c, bx + 30, by - 30, nw + 36, 54, 27); fs(c, col, (1, 1, 1, 1), 4)
    draw_text(c, name, bx + 48, by - 3, 36, "#ffffff", None, 0, lang="en", anchor="l")
    for i, ln in enumerate(lines): draw_text(c, ln, SW / 2, by + 56 + i * 74, 58, "#2b2d42", None, 0, lang="en")
    c.pop_group_to_source(); c.paint_with_alpha(al)

src = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
small = cairo.ImageSurface(cairo.FORMAT_ARGB32, W // 16, H // 16)
out = cairo.ImageSurface(cairo.FORMAT_ARGB32, SW, SH)
p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{SW}x{SH}", "-r", "30", "-i", "-",
                      "-ss", str(T0), "-i", "audio/mix.wav", "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "19", "-preset", "veryfast",
                      "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-af", f"afade=t=out:st={T1 - T0 - 1.2}:d=1.2", "-shortest", "-movflags", "+faststart", OUT],
                     stdin=subprocess.PIPE)
nf = int((T1 - T0) * 30)
for f in range(nf):
    t = T0 + f / 30
    sc = cairo.Context(src); sc.set_operator(cairo.OPERATOR_CLEAR); sc.paint(); sc.set_operator(cairo.OPERATOR_OVER)
    frame(t, src)
    # blurred full-height background from the same frame
    s2 = cairo.Context(small); s2.scale(1 / 16, 1 / 16); s2.set_source_surface(src, 0, 0); s2.paint()
    c = cairo.Context(out)
    c.save(); k = SH / H * 16; c.translate(SW / 2 - (W / 16) * k / 2, 0); c.scale(k, k)
    c.set_source_surface(small, 0, 0); c.get_source().set_filter(cairo.FILTER_BILINEAR); c.paint(); c.restore()
    c.rectangle(0, 0, SW, SH); setc(c, (1, 1, 1, 0.18)); c.fill()
    # sharp re-framed panel
    cx = crop_center(t)
    c.save(); rrect(c, 0, PY, SW, PH, 0); c.clip(); c.translate(0, PY); c.scale(SC, SC); c.translate(-(cx - CW / 2), 0)
    c.set_source_surface(src, 0, 0); c.paint(); c.restore()
    c.rectangle(0, PY, SW, 6); setc(c, (1, 1, 1, 0.9)); c.fill(); c.rectangle(0, PY + PH - 6, SW, 6); c.fill()
    # title
    ph = (t / B) % 1; puls = 1 + 0.03 * math.sin(PI * ph) ** 4
    c.save(); c.translate(SW / 2, 150); c.scale(puls, puls); draw_text(c, "Tinku & Friends", 0, 0, 96, "#ff6b1a", "#ffffff", 11, lang="en"); c.restore()
    rrect(c, SW / 2 - 330, 230, 660, 92, 46); fs(c, "#9b3fd6", "#ffffff", 6)
    draw_text(c, f"{EP_TITLE} 🌈"[:-2], SW / 2, 276, 48, "#ffffff", lang="en")
    short_caption(c, t)
    fa = clamp(min((t - T0) / 0.3, (T1 - t) / 0.8))
    if fa < 1: c.rectangle(0, 0, SW, SH); setc(c, (0, 0, 0, 1 - fa)); c.fill()
    out.flush(); p.stdin.write(bytes(out.get_data()))
p.stdin.close(); p.wait(); print("short ok", OUT)
