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

T_COURT = scene_start("court") - 1.4
T_NIGHT = scene_start("night") - 1.4
T_CHHAM = S("n_midnight") + 2.6           # first chham-chham from the roof
T_STAIRS = scene_start("stairs") - 1.2
T_RUN = E("run") + 0.1                    # kids flee down the stairs
T_MORNING = scene_start("morning") - 1.6
T_CLUES = scene_start("clues") - 1.4
T_TRAP = scene_start("trap") - 1.4
T_BELLS = S("n_bells") + 4.0              # the bell-string rings (inside the narration)
T_TORCH = E("torchon") + 0.1
T_CHASE = S("n_chase")
T_SLIP = S("n_slip") + 0.8
T_FLY = S("n_slip") + 2.0
T_CATCH = S("caught") - 0.2
T_NANI = S("nanicomes") - 1.2
T_MELA = scene_start("mela") - 1.6
T_BELL = S("n_bell") + 1.0
T_OUTRO = E("bye2") + 0.8
