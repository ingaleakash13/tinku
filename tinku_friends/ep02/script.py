# Tinku & Friends — Episode 2: Colors of the Rainbow  (song episode · little ones: babies–UKG · English)
# Original song (words + tune written for this episode). Every line is SUNG on a melody.
# A sung line = (start_beat, singers, notes, caption, cue, scene)
#   notes = [(word, [(midi, beats), ...]), ...]   one (midi, beats) per syllable; word None = rest

EP_NUM = 2
EP_TITLE = "Colors of the Rainbow"
NEXT_TOPIC = "Times Table of 2"
NEXT = "Next time: Times Table of 2!"
BPM = 110
B = 60 / BPM            # seconds per beat
BAR = 4                 # beats per bar
NAMES = {"tinku": ("Tinku", "#f08a00"), "pinky": ("Pinky", "#e8327f"), "golu": ("Golu", "#2fa84a"),
         "moti": ("Moti", "#a8673a"), "all": ("Everyone", "#7a3fbf")}

# ---------------------------------------------------------------- the colours
COLORS = [  # key, colour word syllables, hex, singer, line A, line B, scene
    ("red",    ["Red"],               "#ff3b3b", "pinky", ["is", "the", ("apple", 2), ("shiny", 2), "and", "sweet,"],
                                                         ["is", "the", "fire", "truck,", "zoom", "down", "the", "street!"], "orchard"),
    ("orange", ["Or", "ange"],        "#ff8c1a", "golu",  ["is", "the", ("orange", 2), ("juicy", 2), "and", "round,"],
                                                         ["is", "the", ("pumpkin", 2), "big", "on", "the", "ground!"], "farm"),
    ("yellow", ["Yel", "low"],        "#ffd21a", "tinku", ["is", "the", ("sunshine", 2), ("golden", 2), "and", "bright,"],
                                                         ["is", "the", ("duckling,", 2), "quack,", "quack,", "quack,", "quack!"], "pond"),
    ("green",  ["Green"],             "#2fbf4a", "pinky", ["is", "the", "grass", "where", "the", ("froggies", 2), "hop,"],
                                                         ["is", "the", "leaf", "on", "the", "tall", "tree", "top!"], "jungle"),
    ("blue",   ["Blue"],              "#2f8bff", "golu",  ["is", "the", "sky,", "so", "big", "and", "so", "wide,"],
                                                         ["is", "the", "sea", "where", "the", ("fishes", 2), "glide!"], "sea"),
    ("indigo", ["In", "di", "go"],    "#4b3cc4", "tinku", ["is", "the", "night", "sky,", ("sleepy", 2), "and", "deep,"],
                                                         ["is", "the", ("blanket", 2), "where", ("Mohtee", 2), "sleeps!"], "night"),
    ("violet", ["Vi", "o", "let"],    "#9b3fd6", "pinky", ["is", "the", ("butterfly,", 3), ("flutter,", 2), "fly!"],
                                                         ["is", "the", "plum,", "so", ("yummy,", 2), "oh", "my!"], "garden"),
]
CAP_WORD = {"Mohtee": "Moti"}

# verse tune (2 bars per line): colour word on beat 1, then 8 syllables
#   bar 1: col(1) is(.5) the(.5) s s s s(.5 each)  | bar 2: and(1) last(2) rest(1)
TUNE_A = [67, 67, 69, 72, 69, 67, 64, 65, 67]
TUNE_B = [67, 67, 69, 72, 69, 67, 64, 62, 60]
RHY = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1.0, 2.0]          # 8 syllables after the colour word

def split(n, total):
    return [total / n] * n

def verse_line(colsyl, words, tune):
    notes = [("".join(colsyl), [(tune[0], d) for d in split(len(colsyl), 1.0)])]
    syl = []
    for w in words:
        if isinstance(w, tuple): syl.append((w[0], w[1]))
        else: syl.append((w, 1))
    k = 0
    for w, n in syl:
        notes.append((w, [(tune[1 + k + j], RHY[k + j]) for j in range(n)])); k += n
    assert k == 8, (colsyl, words, k)
    notes.append((None, [(None, 1.0)]))
    return notes

def caption_of(notes):
    ws = [CAP_WORD.get(w.strip(",!"), w.strip(",!")) + ("," if w.endswith(",") else "!" if w.endswith("!") else "") for w, _ in notes if w]
    s = " ".join(ws); return s[0].upper() + s[1:]

# ---------------------------------------------------------------- chorus (all three sing)
CHORUS = [
    [("Red,", [(64, 1)]), ("orange,", [(67, 1), (67, 1)]), ("yellow,", [(69, 1), (67, 1)]), ("green,", [(64, 2)]), (None, [(None, 1)])],
    [("Blue,", [(62, 1)]), ("indigo,", [(65, .5), (65, .5), (64, 1)]), ("violet!", [(62, 1), (60, .5), (62, 1.5)]), (None, [(None, 1)])],
    [("Seven", [(64, .5), (64, .5)]), ("colors", [(67, .5), (67, .5)]), ("shining", [(72, 1), (71, 1)]), ("bright,", [(69, 2)]), (None, [(None, 2)])],
    [("Rainbow,", [(67, .5), (67, .5)]), ("rainbow,", [(69, .5), (67, .5)]), ("what", [(65, .5)]), ("a", [(64, .5)]), ("sight!", [(60, 3)]), (None, [(None, 1)])],
]
CHORUS_CAP = ["Red, orange, yellow, green,", "Blue, indigo, violet!", "Seven colors shining bright,", "Rainbow, rainbow, what a sight!"]
CHORUS_CHORDS = ["C", "Am", "Dm", "G", "C", "F", "G", "C"]
VERSE_CHORDS = ["C", "G", "Am", "G C", "F", "G"]

# ---------------------------------------------------------------- outro (teaser + bye)
OUTRO = [
    ("tinku", [("Next", [(67, 1)]), ("time", [(67, 1)]), ("we", [(69, .5)]), ("learn", [(72, 1)]), ("times", [(69, 1)]), ("table", [(67, .5), (64, .5)]), ("of", [(65, .5)]), ("two!", [(67, 2)])],
     "Next time we learn times table of 2!", "next"),
    ("all", [("Bye-", [(72, 1)]), ("bye!", [(67, 1)]), ("Bye-", [(69, 1)]), ("bye!", [(64, 1)]), ("See", [(65, .5)]), ("you", [(64, .5)]), ("soon!", [(60, 2)]), (None, [(None, 1)])],
     "Bye-bye! Bye-bye! See you soon!", "bye"),
]
OUTRO_CHORDS = ["C", "F", "C", "G C"]

# ---------------------------------------------------------------- arrangement
INTRO_BARS = 4
SECTIONS = []      # (start_bar, n_bars, kind, scene, chords, info)
LINES = []         # sung lines with absolute beats
bar = INTRO_BARS
SECTIONS.append((0, INTRO_BARS, "intro", "title", ["C", "F", "G", "C"], None))

def add_chorus(tag):
    global bar
    SECTIONS.append((bar, 8, "chorus", "rainbow", CHORUS_CHORDS, tag))
    for i, notes in enumerate(CHORUS):
        LINES.append(dict(beat=(bar + 2 * i) * BAR, singers=["tinku", "pinky", "golu"], notes=notes, cap=CHORUS_CAP[i], cue=f"{tag}_{i}", scene="rainbow", spk="all"))
    bar += 8

ECHO = {"pinky": ["tinku", "golu"], "golu": ["tinku", "pinky"], "tinku": ["pinky", "golu"]}
def add_verse(i):
    global bar
    key, colsyl, hexc_, singer, la, lb, scene = COLORS[i]
    SECTIONS.append((bar, 6, "verse", scene, VERSE_CHORDS, key))
    for j, (words, tune) in enumerate(((la, TUNE_A), (lb, TUNE_B))):
        notes = verse_line(colsyl, words, tune)
        LINES.append(dict(beat=(bar + 2 * j) * BAR, singers=[singer], notes=notes, cap=caption_of(notes), cue=f"{key}_{'ab'[j]}", scene=scene, spk=singer))
    cw = "".join(colsyl)
    echo = []
    for p in (72, 69, 72):
        echo.append((cw + "!", [(p, d) for d in split(len(colsyl), 1.0)]))
    echo.append((None, [(None, 1)]))
    LINES.append(dict(beat=(bar + 4) * BAR, singers=ECHO[singer], notes=echo, cap=f"{cw}! {cw}! {cw}!", cue=f"{key}_echo", scene=scene, spk="all"))
    bar += 6   # bar 6 of the verse = instrumental fill (Moti barks on the beat)

add_chorus("ch1")
for i in range(4): add_verse(i)
add_chorus("ch2")
for i in range(4, 7): add_verse(i)
add_chorus("ch3")
SECTIONS.append((bar, 4, "outro", "rainbow", OUTRO_CHORDS, None))
for i, (spk, notes, cap, cue) in enumerate(OUTRO):
    LINES.append(dict(beat=(bar + 2 * i) * BAR, singers=["tinku", "pinky", "golu"] if spk == "all" else [spk], notes=notes, cap=cap, cue=cue, scene="rainbow", spk=spk))
bar += 4
SECTIONS.append((bar, 2, "card", "outro", ["G", "C"], None))
bar += 2
TOTAL_BARS = bar
SONG_END = TOTAL_BARS * BAR * B

def T(beat): return beat * B

if __name__ == "__main__":
    for l in LINES: print(f"{T(l['beat']):7.2f}  {l['cue']:10s} {l['spk']:6s} {l['cap']}")
    print("song length", round(SONG_END, 1), "s")
