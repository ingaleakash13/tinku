import json

TL = json.load(open("timeline.json"))
LINES = TL["lines"]
DURATION = round(TL["speech_end"] + 6.5, 2)


def L(cue): return next(l for l in LINES if l["cue"] == cue)
def S(cue): return L(cue)["start"]
def E(cue): return L(cue)["end"]


def scene_start(name):
    i = next(k for k, l in enumerate(LINES) if l["scene"] == name)
    prev_end = LINES[i - 1]["end"] if i else 0.0
    return round(prev_end + (LINES[i]["start"] - prev_end) * 0.35, 3) if i else 0.0


SCENES = ["title", "room", "palace", "river", "wedding", "stars", "eighth", "room2"]
BOUNDS = {s: scene_start(s) for s in SCENES}
T_OUTRO = E("bye") + 0.6
ORDER = SCENES + ["outro"]
BOUNDS["outro"] = T_OUTRO


def scene_at(t):
    cur = "title"
    for s in ORDER:
        if t >= BOUNDS[s]: cur = s
    return cur


_l = L("seven"); _d = _l["end"] - _l["start"]
SEVEN_TIMES = [_l["start"] + _d * (0.47 + k * 0.074) for k in range(7)]
STAR1_T = S("star1") + 1.0
