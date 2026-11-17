import json

TL = json.load(open("timeline.json"))
LINES = TL["lines"]
DURATION = round(TL["speech_end"] + 3.2, 2)


def starts(cue):
    return [l["start"] for l in LINES if l["cue"] == cue]


def line(cue):
    return next(l for l in LINES if l["cue"] == cue)


def S(cue):
    return line(cue)["start"]


def E(cue):
    return line(cue)["end"]


# Scene boundaries (seconds) — shared by picture and sound.
T_TITLE_END = S("mia_wave") - 1.4          # wipe from title into the yard
T_PAN0 = S("walk") - 0.2                   # camera starts panning to the garden
T_PAN1 = S("dig") - 0.1
T_OUTRO = S("outro") - 1.6                 # wipe to the goodbye card

DIG_HITS = []
t = S("dig") + 0.35
while t < E("dig") - 0.1:
    DIG_HITS.append(round(t, 3)); t += 0.8
BDIG_HITS = []
t = S("bdig2") + 0.05
while t < E("bdig2") + 0.2:
    BDIG_HITS.append(round(t, 3)); t += 0.3
SEED_TIMES = [S(f"seed{i}") + 0.15 for i in range(1, 6)]
SPROUT_TIMES = [S("sprout") + 0.3 + i * 0.18 for i in range(5)]
FLOWER_TIMES = [S(f"f{i}") + 0.05 for i in range(5)]
RAINBOW_T = S("rainbow") + 5.0
HOPHOP_TIMES = [S("hophop") + 0.35 + i * 0.5 for i in range(3)]
