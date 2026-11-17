import sys, cairo, math
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chars import *

W, H = 1920, 1080
surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(surf)
g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgba(0, *hexc("#fff4d6")); g.add_color_stop_rgba(1, *hexc("#ffd59a")); c.set_source(g); c.paint()
c.save(); c.translate(960, 1300)
for i in range(24):
    c.move_to(0, 0); c.arc(0, 0, 2200, i * PI / 12, i * PI / 12 + PI / 24); c.close_path(); setc(c, (1, 1, 1, 0.18)); c.fill()
c.restore()

def label(text, x, y, size, col="#5a2a00", face="Baloo 2"):
    draw_text(c, text, x, y - size * 0.3, size, col, "#ffffff", max(2, size // 9), "hi" if face == "Baloo 2" else "en")

label("टिंकू की महाभारत", 960, 78, 64, "#c2410c")
label("Tinku's Mahabharat  ·  character sheet", 960, 126, 30, "#7c2d12", "Fredoka")

# host
rrect(c, 30, 160, 330, 890, 30); setc(c, (1, 1, 1, 0.55)); c.fill()
tinku(c, 195, 930, 0.3, 1.25, (0.3, 2.3), 0.0, 0.3)
label("टिंकू", 195, 1000, 46, "#c2410c"); label("Tinku (host)", 195, 1036, 26, "#7c2d12", "Fredoka")

keys = ["shantanu", "ganga", "bheeshm", "krishna", "draupadi", "karn", "shakuni",
        "yudhishthir", "bheem", "arjun", "nakul", "sahadev", "duryodhan", "abhimanyu"]
x0, slot = 490, 208
for i, k in enumerate(keys):
    row, col = divmod(i, 7)
    x = x0 + col * slot
    yb = 572 if row == 0 else 1022
    hero(c, k, x, yb - 42, 0.4, 0.56, (0.25, 0.35 if CAST[k].get("item", "none") != "none" else 0.25), 0.0, 0.0)
    label(CAST[k]["hi"], x, yb + 2, 30, "#c2410c")
    label(CAST[k]["en"], x, yb + 30, 20, "#7c2d12", "Fredoka")
surf.write_to_png(sys.argv[1] if len(sys.argv) > 1 else "character_sheet.png")
