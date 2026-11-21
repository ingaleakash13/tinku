"""Opening HOOK (one COMPLETE 5-8 s scene) + cover thumbnails for Tinku & Friends stories (no brand text anywhere).

The hook is a flash-forward of the most exciting/funny moment of the story, as one COMPLETE little scene (owner, 21 Nov 2026):
T0 = just before the first line/action of the beat starts, DUR = until just after its last line ends (5-8 s; take the
timings from the .en.srt) — never cut mid-sentence or mid-action (push-in zoom, whoosh + boom sting) with a big
curiosity line on screen (a question / cliff-hanger, never a spoiler of the ending, never a lie), then a white flash cuts
into the story itself. Works on the finished mp4s, so nothing needs re-rendering.

usage:
  python3 hook.py full  FULL.mp4 T0 DUR "LINE1" "LINE2" OUT.mp4
        -> OUT = hook (from FULL at T0..T0+DUR, 16:9, covers the burned caption) + the whole FULL video
  python3 hook.py short FULL.mp4 T0 DUR "LINE1" "LINE2" SHORT.mp4 OUT.mp4 [crop_center_x]
        -> OUT = vertical hook + SHORT (its black fade-in skipped, trimmed so the total stays exactly 30 s)
  python3 hook.py cover FULL.mp4 T "LINE1" "LINE2" OUT_BASE [crop_center_x]
        -> OUT_BASE_cover.jpg (1080x1920, Reel/Short cover; text inside the 3:4 grid-safe area)
           and OUT_BASE_thumb.jpg (1280x720, YouTube thumbnail)
env: HOOK_TOP=1 puts the 16:9 hook/thumbnail text at the top (use when the action is low in the frame);
     HOOK_Y0=40 moves the vertical crop down (scenes whose ground sits low). Keep crop_center_x within 450..830.
  python3 hook.py captions SHORT_HOOK.mp4 FULL_HOOK.srt SCRIPT.py SHORT_T0 OUT.mp4 HOOK_DUR
        -> burns big Reel captions (speaker name tag + English line, below the picture) into an already-hooked Short;
           SHORT_T0 = the T0 given to short.py. (New stories: short.py draws these captions itself.)
LINE1 = small yellow teaser line (e.g. "WAIT FOR IT..."), LINE2 = the big hook question. Devanagari works (Baloo 2).
"""
import sys, os, subprocess, tempfile, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONTS = os.path.expanduser("~/.fonts")
FRED, BALOO = f"{FONTS}/Fredoka%5Bwdth,wght%5D.ttf", f"{FONTS}/Baloo2%5Bwght%5D.ttf"
FPS, SR = 30, 48000

def font(txt, size):
    hi = any("ऀ" <= ch <= "ॿ" for ch in txt)
    f = ImageFont.truetype(BALOO if hi else FRED, size)
    try: f.set_variation_by_axes([800] if hi else [700, 100])
    except Exception: pass
    return f

def fit_font(d, txt, size, maxw):
    while size > 20:
        f = font(txt, size)
        if d.textlength(txt, font=f) <= maxw: return f
        size -= 4
    return font(txt, size)

def text_layer(W, H, lines, prog, flash=0.0):
    """lines = [(text, cx, cy, size, fill, maxw, delay)] ; prog = seconds since hook start -> RGBA layer with pop-in text."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for txt, cx, cy, size, fill, maxw, delay in lines:
        if not txt: continue
        k = (prog - delay) / 0.22
        if k <= 0: continue
        k = min(k, 1.0)
        s = 1.0 + 0.45 * (1 - k) ** 2 - 0.08 * np.sin(min(k, 1) * np.pi)        # overshoot pop
        tmp = Image.new("RGBA", (W, int(size * 2.2)), (0, 0, 0, 0)); d = ImageDraw.Draw(tmp)
        f = fit_font(d, txt, size, maxw)
        sw = max(4, size // 9)
        d.text((W / 2 + 5, tmp.height / 2 + 7), txt, font=f, anchor="mm", fill=(40, 10, 70, 150), stroke_width=sw, stroke_fill=(40, 10, 70, 150))
        d.text((W / 2, tmp.height / 2), txt, font=f, anchor="mm", fill=fill, stroke_width=sw, stroke_fill=(43, 18, 82, 255))
        if abs(s - 1) > 0.01:
            tmp = tmp.resize((int(tmp.width * s), int(tmp.height * s)), Image.LANCZOS)
        if k < 1: tmp.putalpha(tmp.getchannel("A").point(lambda a: int(a * min(1, k * 1.6))))
        lay.alpha_composite(tmp, (int(cx - tmp.width / 2), int(cy - tmp.height / 2)))
    if flash > 0:
        lay.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255 * flash))))
    return lay

def grab(src, t0, dur, w=1280, h=720):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t0), "-t", str(dur), "-i", src, "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-r", str(FPS), "-"], capture_output=True, check=True).stdout
    n = len(raw) // (w * h * 3)
    return [Image.frombuffer("RGB", (w, h), raw[i * w * h * 3:(i + 1) * w * h * 3]) for i in range(n)]

def zoom(im, z, cy=0.45):
    W, H = im.size; cw, ch = W / z, H / z; x0 = (W - cw) / 2; y0 = (H - ch) * cy
    return im.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))

TOP = os.environ.get("HOOK_TOP") == "1"   # 16:9 hook text at the TOP (when the action happens low in the frame)

def band(W, H, y0, y1, rgba=(43, 18, 82)):
    """soft dark-purple band (covers burned captions so they never fight the hook text)"""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); a = np.zeros((H, 1), np.float32)
    for y in range(int(y0) - 40, int(y1)):
        if 0 <= y < H: a[y] = 0.97 * min(1, (y - (y0 - 40)) / 40)
    if TOP: a = a[::-1].copy()
    arr = np.zeros((H, W, 4), np.uint8); arr[..., 0], arr[..., 1], arr[..., 2] = rgba; arr[..., 3] = (a * 255).astype(np.uint8)
    return Image.fromarray(arr, "RGBA")

def vertical(im, cx=690, pzoom=1.0):
    """1080x1920: blurred full frame behind, sharp 900x615 crop (captions cut off) scaled to 1080 wide, centred a bit high."""
    SW, SH = 1080, 1920
    bg = im.resize((80, 45)).resize((int(SH * 16 / 9), SH), Image.BICUBIC)
    bg = bg.crop(((bg.width - SW) // 2, 0, (bg.width - SW) // 2 + SW, SH)).filter(ImageFilter.GaussianBlur(14))
    bg = Image.blend(bg, Image.new("RGB", (SW, SH), (20, 8, 40)), 0.5)
    Y0 = float(os.environ.get("HOOK_Y0", 0))   # raise for scenes whose ground sits low (still above the caption box)
    crop = zoom(im, pzoom).crop((cx - 450, Y0, cx + 450, Y0 + 615)).resize((1080, 738), Image.LANCZOS)
    sh = np.linspace(0, 1, SH)[:, None, None]; arr = np.asarray(bg).astype(np.float32)
    arr *= 1 - 0.45 * np.clip((sh - 0.68) / 0.32, 0, 1); bg = Image.fromarray(arr.astype(np.uint8))   # darker bottom
    out = bg.copy(); py = 560; out.paste(crop, (0, py))
    d = ImageDraw.Draw(out); d.rectangle((0, py - 6, SW, py), fill=(255, 255, 255)); d.rectangle((0, py + 738, SW, py + 744), fill=(255, 255, 255))
    return out

def sting(dur, path):
    """whoosh riser into the hook + a soft cartoon boom when the text lands + a shimmer at the cut"""
    n = int(dur * SR); t = np.arange(n) / SR; rng = np.random.default_rng(7); y = np.zeros(n)
    w = rng.standard_normal(n); k = np.exp(-((t - 0.18) / 0.12) ** 2)
    y += np.convolve(w, np.ones(12) / 12, "same") * k * 0.35
    b = (t > 0.22) * np.exp(-(t - 0.22).clip(0) * 9) * np.sin(2 * np.pi * (90 - 40 * (t - 0.22).clip(0)) * t)
    y += b * 0.55
    sh = np.exp(-((t - (dur - 0.12)) / 0.09) ** 2) * sum(np.sin(2 * np.pi * f * t) for f in (1568, 2093, 2637)) / 3
    y += sh * 0.25
    pcm = (np.clip(y, -1, 1) * 32000).astype(np.int16); st = np.repeat(pcm[:, None], 2, 1)
    import wave
    with wave.open(path, "wb") as wv:
        wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(SR); wv.writeframes(st.tobytes())

def encode(frames, W, H, src, t0, dur, out, tmp):
    sp = os.path.join(tmp, "sting.wav"); sting(dur, sp)
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-ss", str(t0), "-t", str(dur), "-i", src, "-i", sp,
                          "-filter_complex", "[1:a]volume=0.9[a1];[a1][2:a]amix=inputs=2:normalize=0:duration=first,aresample=48000[a]",
                          "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p",
                          "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-t", str(dur), out], stdin=subprocess.PIPE)
    for im in frames: p.stdin.write(im.convert("RGB").tobytes())
    p.stdin.close(); assert p.wait() == 0

def concat(a, b, out, b_ss=0.0, b_dur=None, fade_out=False):
    bt = ["-ss", str(b_ss)] + (["-t", str(b_dur)] if b_dur else [])
    vf = f",fade=t=out:st={b_dur - 0.6}:d=0.6" if (fade_out and b_dur) else ""
    af = f",afade=t=out:st={b_dur - 0.8}:d=0.8" if (fade_out and b_dur) else ""
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a, *bt, "-i", b, "-filter_complex",
                    f"[1:v]setpts=PTS-STARTPTS,fps={FPS},format=yuv420p{vf}[v1];[1:a]asetpts=PTS-STARTPTS,aresample=48000{af}[a1];"
                    f"[0:v]fps={FPS},format=yuv420p[v0];[0:a]aresample=48000[a0];[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]",
                    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "19", "-preset", "veryfast", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out], check=True)

def hook_frames(src, t0, dur, l1, l2, mode, cx=690):
    frames = grab(src, t0, dur); out = []
    for i, im in enumerate(frames):
        tt = i / FPS; z = 1.0 + 0.10 * tt / dur
        flash = max(0.0, (tt - (dur - 0.15)) / 0.15)
        if mode == "full":
            fr = zoom(im, z, 0.75 if TOP else 0.45).convert("RGBA"); fr.alpha_composite(band(1280, 720, 560, 720))
            y1, y2 = (52, 120) if TOP else (598, 666)
            fr.alpha_composite(text_layer(1280, 720, [(l1, 640, y1, 44, (255, 214, 10, 255), 1180, 0.05),
                                                      (l2, 640, y2, 66, (255, 255, 255, 255), 1220, 0.35)], tt, flash))
        else:
            fr = vertical(im, cx, z).convert("RGBA")
            fr.alpha_composite(text_layer(1080, 1920, [(l1, 540, 360, 92, (255, 214, 10, 255), 1000, 0.05),
                                                       (l2, 540, 1460, 96, (255, 255, 255, 255), 1010, 0.35)], tt, flash))
        out.append(fr)
    return out

def read_srt(path):
    import re
    subs = []
    for blk in open(path, encoding="utf-8").read().strip().split("\n\n"):
        ls = blk.strip().splitlines()
        if len(ls) < 3: continue
        a, b = [sum(float(x) * m for x, m in zip(re.split("[:,]", ts)[:3], (3600, 60, 1))) + int(ts.split(",")[1]) / 1000
                for ts in ls[1].split(" --> ")]
        subs.append((a, b, " ".join(ls[2:])))
    return subs

def reel_caption(W, sub, name, col, al):
    """white rounded caption box with a coloured name tag, placed just under the picture (above Instagram's bottom UI)"""
    lay = Image.new("RGBA", (W, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    f = font(sub, 60); words = sub.split(); lines = [sub]
    if d.textlength(sub, font=f) > 940:
        best = None
        for i in range(1, len(words)):
            a, b = " ".join(words[:i]), " ".join(words[i:]); w = max(d.textlength(a, font=f), d.textlength(b, font=f))
            if best is None or w < best[0]: best = (w, [a, b])
        lines = best[1]
        while max(d.textlength(x, font=f) for x in lines) > 960 and f.size > 36: f = font(sub, f.size - 4)
    bh = 44 + 76 * len(lines); by = 1400; bx, bw = 45, 990
    d.rounded_rectangle((bx + 5, by + 7, bx + bw + 5, by + bh + 7), 34, fill=(20, 8, 40, 90))
    d.rounded_rectangle((bx, by, bx + bw, by + bh), 34, fill=(255, 255, 255, 245), outline=col, width=8)
    for i, ln in enumerate(lines): d.text((W / 2, by + 60 + i * 76), ln, font=f, anchor="mm", fill=(43, 45, 66))
    if name:
        nf = font(name, 40); nw = d.textlength(name, font=nf)
        d.rounded_rectangle((bx + 30, by - 34, bx + 30 + nw + 40, by + 26), 30, fill=col, outline=(255, 255, 255), width=4)
        d.text((bx + 50, by - 4), name, font=nf, anchor="lm", fill=(255, 255, 255))
    if al < 1: lay.putalpha(lay.getchannel("A").point(lambda a: int(a * al)))
    return lay

def burn_captions(src, srt, script, st0, out, hook=2.8):
    ns = {}; exec(open(script, encoding="utf-8").read(), ns)
    lines, names = ns["LINES"], ns["NAMES"]; subs = read_srt(srt)
    meta = []
    for i, (a, b, txt) in enumerate(subs):
        spk = lines[i][1] if i < len(lines) else None
        nm, col = names.get(spk, ("", "#7a5cc8"))
        c = col.lstrip("#"); meta.append((a, b, txt, nm, tuple(int(c[k:k + 2], 16) for k in (0, 2, 4))))
    W, H = 1080, 1920
    raw = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-i", src, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "19", "-preset", "veryfast", "-pix_fmt", "yuv420p",
                            "-c:a", "copy", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    cache = {}; i = 0; n = W * H * 3
    while True:
        buf = raw.stdout.read(n)
        if len(buf) < n: break
        t = i / FPS; i += 1
        im = Image.frombuffer("RGB", (W, H), buf)
        if t >= hook + 0.1:
            ts = t + st0 + 0.25; cur = None
            for j, m in enumerate(meta):
                nxt = meta[j + 1][0] if j + 1 < len(meta) else 1e9
                if m[0] - 0.1 <= ts <= min(m[1] + 0.4, nxt - 0.1): cur = j
            if cur is not None:
                a, b, txt, nm, col = meta[cur]; al = min(1.0, (ts - a + 0.1) / 0.15, (t - hook - 0.1) / 0.15)
                key = (cur, round(al, 2))
                if key not in cache: cache = {k: v for k, v in cache.items() if k[0] == cur}; cache[key] = reel_caption(W, txt, nm, col, al)
                im = im.convert("RGBA"); im.alpha_composite(cache[key]); im = im.convert("RGB")
        enc.stdin.write(im.tobytes())
    enc.stdin.close(); assert enc.wait() == 0

def split2(txt):
    """long LINE2 for vertical -> two balanced lines (returns list)"""
    if len(txt) <= 20: return [txt]
    w = txt.split(); best = None
    for i in range(1, len(w)):
        a, b = " ".join(w[:i]), " ".join(w[i:]); m = max(len(a), len(b))
        if best is None or m < best[0]: best = (m, [a, b])
    return best[1]

if __name__ == "__main__":
    mode = sys.argv[1]
    with tempfile.TemporaryDirectory() as tmp:
        if mode == "full":
            src, t0, dur, l1, l2, out = sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), sys.argv[5], sys.argv[6], sys.argv[7]
            h = os.path.join(tmp, "hook.mp4"); encode(hook_frames(src, t0, dur, l1, l2, "full"), 1280, 720, src, t0, dur, h, tmp)
            concat(h, src, out)
        elif mode == "short":
            src, t0, dur, l1, l2, short, out = sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8]
            cx = float(sys.argv[9]) if len(sys.argv) > 9 else 690
            frames = grab(src, t0, dur); fr = []
            parts = split2(l2)
            for i, im in enumerate(frames):
                tt = i / FPS; z = 1.0 + 0.10 * tt / dur; flash = max(0.0, (tt - (dur - 0.15)) / 0.15)
                f = vertical(im, cx, z).convert("RGBA")
                lines = [(l1, 540, 330, 92, (255, 214, 10, 255), 1000, 0.05)]
                for j, p in enumerate(parts):
                    lines.append((p, 540, 1470 + j * 120 - (60 if len(parts) > 1 else 0), 100, (255, 255, 255, 255), 1010, 0.35 + 0.12 * j))
                f.alpha_composite(text_layer(1080, 1920, lines, tt, flash)); fr.append(f)
            h = os.path.join(tmp, "hook.mp4"); encode(fr, 1080, 1920, src, t0, dur, h, tmp)
            concat(h, short, out, b_ss=0.25, b_dur=round(30.0 - dur, 3), fade_out=True)
        elif mode == "cover":
            src, t, l1, l2, base = sys.argv[2], float(sys.argv[3]), sys.argv[4], sys.argv[5], sys.argv[6]
            cx = float(sys.argv[7]) if len(sys.argv) > 7 else 690
            im = grab(src, t, 0.05)[0]
            v = vertical(im, cx, 1.04).convert("RGBA"); parts = split2(l2)
            lines = [(l1, 540, 400, 96, (255, 214, 10, 255), 980, 0)]
            for j, p in enumerate(parts):
                lines.append((p, 540, 1460 + j * 124 - (62 if len(parts) > 1 else 0), 108, (255, 255, 255, 255), 1000, 0))
            v.alpha_composite(text_layer(1080, 1920, lines, 5.0)); v.convert("RGB").save(base + "_cover.jpg", quality=92)
            th = zoom(im, 1.06, 0.75 if TOP else 0.45).convert("RGBA"); th.alpha_composite(band(1280, 720, 540, 720))
            y1, y2 = (58, 135) if TOP else (585, 662)
            th.alpha_composite(text_layer(1280, 720, [(l1, 640, y1, 52, (255, 214, 10, 255), 1180, 0), (l2, 640, y2, 76, (255, 255, 255, 255), 1220, 0)], 5.0))
            th.convert("RGB").save(base + "_thumb.jpg", quality=92)
        elif mode == "captions":
            src, srt, script, st0, out = sys.argv[2], sys.argv[3], sys.argv[4], float(sys.argv[5]), sys.argv[6]
            burn_captions(src, srt, script, st0, out, float(sys.argv[7]) if len(sys.argv) > 7 else 2.8)
        print("ok", mode)
