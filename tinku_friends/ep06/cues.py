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

T_GHOST = scene_start("ghost") - 1.6      # fog thickens, the giant shadow rises (no cut: same lane, darker)
T_HIDE = scene_start("hide") - 1.0        # flash cut: kids duck behind the front wall
T_REVEAL = S("kitten") - 1.8              # torch on the wall: a tiny floury kitten
T_HOME = scene_start("home") - 1.4        # circle wipe: walking to Dadi's gate
T_SHAKE = S("shake") - 1.6                # Barfi shakes the flour onto Moti
T_OUTRO = E("bye2") + 0.8
