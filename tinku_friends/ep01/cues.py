import json, re

TL = json.load(open("timeline.json"))
LINES = TL["lines"]
DURATION = round(TL["speech_end"] + 6.0, 2)

def L(cue): return next(l for l in LINES if l["cue"] == cue)
def has(cue): return any(l["cue"] == cue for l in LINES)
def S(cue): return L(cue)["start"]
def E(cue): return L(cue)["end"]

T_TITLE_END = S("n1") - 1.4
T_COUNT = S("n1") - 0.8
T_OUTRO = E("bye2") + 0.8

NUMW = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]

def word_times(cue, words):
    """Approximate time each listed word is spoken, by its character position in the line."""
    l = L(cue); txt = l["text"].lower(); d = l["end"] - l["start"]
    out, pos = [], 0
    for w in words:
        i = txt.find(w, pos)
        if i < 0: i = pos
        out.append(l["start"] + d * (i / max(1, len(txt))) + 0.05); pos = i + len(w)
    return out

POP = {}
for n in range(1, 11):
    POP[n] = [S("n1") + 0.25] if n == 1 else word_times(f"n{n}", NUMW[:n])
FAST = word_times("fast", NUMW)
