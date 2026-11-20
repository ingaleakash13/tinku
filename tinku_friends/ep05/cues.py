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

T_KEYIN = S("turn") + 0.2                 # Pinky walks to the console and turns the golden key
T_START = E("turn") - 0.3                 # the screen starts to glow
T_PULL = S("pull") - 0.4                  # portal opens, everyone gets pulled in
T_CITY = scene_start("sky") - 2.0         # flash into the secret level
T_MOTI = S("bark2") - 0.4                 # Moti hops onto the wrong (green) tile
T_MOTIBACK = E("shaking") - 0.4           # ...and hops back
r1, r2 = L("r1"), L("r2")
HOPS = [r1["start"] + (r1["end"] - r1["start"]) * k / 3 for k in range(3)] + [r2["start"] + (r2["end"] - r2["start"]) * k / 4 for k in range(4)]
T_BRIDGE = HOPS[-1] + 0.5                 # bridge complete
T_CROSS = E("cross") - 0.2                # everyone walks over the rainbow bridge
T_TREASURE = scene_start("treasure") - 1.2
T_OPEN = E("open") - 0.2                  # chest lid opens
T_TROPHY = T_OPEN + 0.8                   # trophy rises
T_FIRE = S("fireworks") - 0.3
T_NOTE = S("note") - 0.2
T_SAVE = E("takehome") - 1.0              # portal home
T_BACK = scene_start("back") - 2.0
T_OUTRO = E("bye2") + 0.8
