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

T_START = S("start") + 0.6                # START pressed: the screen starts to glow
T_PULL = S("pull") - 0.5                  # portal opens, everyone gets pulled in
T_CITY = scene_start("city") - 2.0        # flash-wipe into the game world
T_KART = scene_start("kart") - 1.2        # wipe into the go-kart chase
T_JUMP = S("jump") + 0.05
T_CAUGHT = S("caught") - 1.1              # kart catches the ice-cream cart
T_ARCADE = scene_start("arcade") - 1.4
T_CLAW1 = S("steer") + 1.6                # first claw try (grabs the teddy)
T_CLAW2 = S("again") + 0.3                # second try (grabs Moti)
T_SHADOW = S("shadow") - 1.2              # giant boss shadow crosses the sky
T_SAVE = S("save") + 0.6                  # SAVING… bar, then the portal pulls them home
T_BACK = scene_start("back") - 2.0
T_OUTRO = E("bye2") + 0.8
