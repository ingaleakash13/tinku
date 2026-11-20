import os, sys, subprocess, cairo
from draw import frame, W, H, FPS, DURATION

f0, f1, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
tmp = out.replace(".mp4", ".part.mp4")
p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                      "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
for f in range(f0, f1):
    frame(f / FPS, surf)
    surf.flush()
    p.stdin.write(bytes(surf.get_data()))
p.stdin.close()
if p.wait() == 0:
    os.rename(tmp, out)
