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

T_NIGHT = scene_start("night") - 1.6      # dusk -> night wipe
T_HIDE = scene_start("hide") - 1.0        # kids dive behind the bench
T_REVEAL = S("itsmoti") - 1.8             # torch on, sheet pulled off
T_HOME = scene_start("home") - 1.6
T_OUTRO = E("bye2") + 0.8
T_GHOST = S("ghost") - 1.6                # the "ghost" rises from the bush
T_GOLUGHOST = S("golughost") - 1.4        # sheet falls on Golu
