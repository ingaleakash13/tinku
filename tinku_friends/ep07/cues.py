import json

TL = json.load(open("timeline.json"))
LINES = TL["lines"]
DURATION = round(TL["speech_end"] + 6.0, 2)

def L(cue): return next(l for l in LINES if l["cue"] == cue)
def has(cue): return any(l["cue"] == cue for l in LINES)
def S(cue): return L(cue)["start"]
def E(cue): return L(cue)["end"]

def scene_start(name):
    return min(l["start"] for l in LINES if l["scene"] == name)

T_NIGHT = E("goodnight") + 0.5          # circle wipe into the dark room; chham-chham starts
T_CHHAM = T_NIGHT + 1.0
T_STAIRS = scene_start("stairs") - 1.3   # flash cut: creeping up the stairs
T_ROOF = S("torch") - 0.9                # wipe onto the dark roof
T_TORCH = E("torch") + 0.1               # torch on -> Chameli revealed
T_NANI = S("nanicomes") - 1.0            # Nani comes up with a lantern
T_MORNING = scene_start("morning") - 1.6
T_OUTRO = E("bye2") + 0.8
