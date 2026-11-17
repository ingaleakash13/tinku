# Tinku & Friends — Episode 1: Let's Count 1 to 10!  (little ones: babies–UKG, English)
# (scene, speaker, text_spoken, caption, pause_before, cue)

EP_NUM = 1
EP_TITLE = "Let's Count 1 to 10!"
NEXT = "Next time: Colors of the Rainbow!"

W = ["One", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]
def count_to(n): return ", ".join(W[:n]) + "."

ITEMS = [  # (number, speaker, kind, phrase)
    (1, "pinky", "sun", "One big, bright sun!"),
    (2, "golu", "balloon", "Two red balloons!"),
    (3, "tinku", "apple", "Three juicy apples!"),
    (4, "pinky", "star", "Four shiny stars!"),
    (5, "golu", "fish", "Five little fish!"),
    (6, "tinku", "flower", "Six pretty flowers!"),
    (7, "pinky", "butterfly", "Seven happy butterflies!"),
    (8, "golu", "cupcake", "Eight yummy cupcakes!"),
    (9, "tinku", "bubble", "Nine floating bubbles!"),
    (10, "pinky", "finger", "Ten little fingers!"),
]

LINES = [
    ("title", "tinku", "Tinku and Friends! Let's count, one to ten!", "Tinku & Friends! Let's count 1 to 10!", 1.4, "title"),
]
ECHO = {"tinku": "golu", "pinky": "tinku", "golu": "pinky"}
for n, spk, kind, phrase in ITEMS:
    spoken = (count_to(n) + " " if n > 1 else "") + phrase
    caption = (", ".join(str(k) for k in range(1, n + 1)) + "... " if n > 1 else "") + phrase
    LINES.append(("count", spk, spoken, caption, 1.8 if n > 1 else 2.4, f"n{n}"))
    word = W[n - 1].capitalize()
    LINES.append(("count", ECHO[spk], f"{word}!", f"{n}! {word}!", 0.5, f"e{n}"))
LINES += [
    ("count", "tinku", "Wow! Now let's count again, super fast!", "Wow! Now let's count again, super fast!", 1.2, "again"),
    ("count", "golu", "One, two, three, four, five, six, seven, eight, nine, ten!", "1, 2, 3, 4, 5, 6, 7, 8, 9, 10!", 0.4, "fast"),
    ("count", "moti", "", "Woof! Woof! Woof!", 0.3, "moti_cheer"),
    ("park", "tinku", "Next time, we'll learn all the colors of the rainbow!", "Next time, we'll learn all the colors of the rainbow!", 1.0, "next"),
    ("park", "pinky", "Bye-bye, friends!", "Bye-bye, friends!", 0.4, "bye1"),
    ("park", "golu", "Bye-bye!", "Bye-bye!", 0.2, "bye2"),
]

VOICES = {  # kokoro English voice, speed, F0 factor, formant factor  (targets: Tinku ~285 Hz, Pinky ~315, Golu ~340)
    "tinku": ("af_river", 0.86, 1.55, 1.12),   # young boy (~7)
    "pinky": ("af_bella", 0.86, 1.48, 1.12),   # little girl (~6)
    "golu": ("af_heart", 0.84, 1.70, 1.20),    # tiny giggly boy (~4)
}
NAMES = {"tinku": ("Tinku", "#f08a00"), "pinky": ("Pinky", "#e8327f"), "golu": ("Golu", "#2fa84a"), "moti": ("Moti", "#a8673a")}
