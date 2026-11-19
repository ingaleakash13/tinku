"""30-second vertical Short / Instagram Reel cut from the story (1080x1920): blurred background, sharp re-framed
panel, NO captions and no brand text. usage: python3 short.py T_START T_END out.mp4 [crop_center_x]"""
import sys, math, subprocess, cairo
from draw import *

SW, SH = 1080, 1920
T0, T1, OUT = float(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
CX = float(sys.argv[4]) if len(sys.argv) > 4 else 690
CW = 900; SC = SW / CW; PH = int(720 * SC); PY = (SH - PH) // 2   # no on-screen captions in Shorts/Reels (owner's rule)

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
        nxt = LINES[i + 1]["start"] if i + 1 < len(LINES) else 1e9
        if l["start"] - 0.12 <= t <= min(l["end"] + 0.6, nxt - 0.12): cur = l
    if not cur: return
    al = clamp((t - cur["start"] + 0.12) / 0.15)
    name, col = NAMES[cur["speaker"]]
    lines = wrap(c, cur["en"], 58, 940)
    bh = 40 + 74 * len(lines); by = 1520; bx, bw = 50, 980
    c.push_group()
    rrect(c, bx + 4, by + 6, bw, bh, 34); setc(c, (0.1, 0.05, 0.2, 0.3)); c.fill()
    rrect(c, bx, by, bw, bh, 34); fs(c, (1, 1, 1, 0.96), hexc(col), 7)
    nw = text_surface(name, 36, "#ffffff", None, 0, "hi").get_width()
    rrect(c, bx + 30, by - 32, nw + 36, 58, 29); fs(c, col, (1, 1, 1, 1), 4)
    draw_text(c, name, bx + 48, by - 3, 36, "#ffffff", None, 0, lang="hi", anchor="l")
    for i, ln in enumerate(lines): draw_text(c, ln, SW / 2, by + 56 + i * 74, 58, "#2b2d42", None, 0, lang="en")
    c.pop_group_to_source(); c.paint_with_alpha(al)

src = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
small = cairo.ImageSurface(cairo.FORMAT_ARGB32, W // 16, H // 16)
out = cairo.ImageSurface(cairo.FORMAT_ARGB32, SW, SH)
p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{SW}x{SH}", "-r", "30", "-i", "-",
                      "-ss", str(T0), "-i", "audio/mix.wav", "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "19", "-preset", "veryfast",
                      "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-af", f"afade=t=in:d=0.2,afade=t=out:st={T1 - T0 - 1.0}:d=1.0",
                      "-shortest", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
for f in range(int((T1 - T0) * 30)):
    t = T0 + f / 30
    sc = cairo.Context(src); sc.set_operator(cairo.OPERATOR_CLEAR); sc.paint(); sc.set_operator(cairo.OPERATOR_OVER)
    frame(t, src, with_captions=False)
    s2 = cairo.Context(small); s2.scale(1 / 16, 1 / 16); s2.set_source_surface(src, 0, 0); s2.paint()
    c = cairo.Context(out)
    c.save(); k = SH / H * 16; c.translate(SW / 2 - (W / 16) * k / 2, 0); c.scale(k, k)
    c.set_source_surface(small, 0, 0); c.get_source().set_filter(cairo.FILTER_BILINEAR); c.paint(); c.restore()
    c.rectangle(0, 0, SW, SH); setc(c, (0, 0, 0.1, 0.15)); c.fill()
    c.save(); c.rectangle(0, PY, SW, PH); c.clip(); c.translate(0, PY); c.scale(SC, SC); c.translate(-(CX - CW / 2), 0)
    c.set_source_surface(src, 0, 0); c.paint(); c.restore()
    c.rectangle(0, PY, SW, 6); setc(c, (1, 1, 1, 0.9)); c.fill(); c.rectangle(0, PY + PH - 6, SW, 6); c.fill()
    fa = clamp(min((t - T0) / 0.2, (T1 - t) / 0.6))
    if fa < 1: c.rectangle(0, 0, SW, SH); setc(c, (0, 0, 0, 1 - fa)); c.fill()
    out.flush(); p.stdin.write(bytes(out.get_data()))
p.stdin.close(); p.wait(); print("short ok", OUT)
