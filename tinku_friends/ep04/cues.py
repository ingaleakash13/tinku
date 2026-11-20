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

T_START = E("start") - 0.4                # START pressed: the screen starts to glow
T_PULL = S("pull") - 0.4                  # portal opens, everyone gets pulled in
T_CITY = scene_start("arena") - 2.0       # flash into the boss level
T_RISE = S("coo1") - 0.9                  # Pigeon King rises from behind the big sandcastle
T_TWALK = E("grab") - 0.4                 # Tinku marches toward the boss
T_FLAP1 = S("coo2")                       # wing gust #1 (Tinku flies into the small sandcastle)
T_TOUT = E("ptooh") - 0.3                 # Tinku pops out of the sand
T_PWALK = E("tickle") - 0.6               # Pinky walks over with a feather
T_FLAP2 = S("coo3")                       # giggle + wing gust #2 (Pinky slides back)
T_GWALK = S("hungry") - 0.2               # Golu walks up with his grain bag
T_GRAINS = E("share") - 0.6               # grains fly into the king's beak
T_HAPPY = S("coo4")                       # boss turns friendly, bar fills with hearts
T_KEY = S("key") - 1.2                    # golden key floats over
T_SAVE = S("save") + 0.6
T_BACK = scene_start("back") - 2.0
T_OUTRO = E("bye2") + 0.8
