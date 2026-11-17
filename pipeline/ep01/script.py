# "Mia & Benny: The Rainbow Garden" — original episode script.
# Each entry: (scene, speaker, text, pause_before_seconds, cue)
# cue = name of an on-screen action that starts when the line starts.

LINES = [
    # 1. Title card
    ("title", "narrator", "Mia and Benny! The Rainbow Garden!", 1.5, "title"),

    # 2. Meet the friends
    ("yard", "narrator", "Good morning, friends! This is Mia.", 2.6, "mia_wave"),
    ("yard", "mia", "Hi, everyone!", 0.3, "mia_jump"),
    ("yard", "narrator", "And this is Mia's best friend, Benny the Bunny!", 0.5, "benny_in"),
    ("yard", "benny", "Hop, hop, hello!", 0.2, "benny_hop"),
    ("yard", "mia", "Benny, let's grow a garden today!", 0.5, "mia_point"),
    ("yard", "benny", "Yay! A garden! What do we need?", 0.3, "benny_hop"),
    ("yard", "mia", "We need a shovel, some seeds, water, and lots of sunshine!", 0.4, "mia_point"),
    ("yard", "benny", "I can help! Let's go!", 0.3, "walk"),

    # 3. Dig and plant
    ("plant", "narrator", "First, Mia digs five little holes in the soil. Dig, dig, dig!", 0.7, "dig"),
    ("plant", "narrator", "Benny helps too. Bunnies are super diggers!", 0.4, "bdig"),
    ("plant", "benny", "Dig, dig, dig, dig, dig!", 0.2, "bdig2"),
    ("plant", "mia", "Now we need seeds. Let's count them!", 0.4, "seedbag"),
    ("plant", "mia", "One!", 0.3, "seed1"),
    ("plant", "mia", "Two!", 0.35, "seed2"),
    ("plant", "mia", "Three!", 0.35, "seed3"),
    ("plant", "mia", "Four!", 0.35, "seed4"),
    ("plant", "mia", "Five!", 0.35, "seed5"),
    ("plant", "benny", "Five little seeds, all tucked into bed!", 0.5, "cover"),

    # 4. Water and sun
    ("grow", "narrator", "Seeds need water to grow. Benny brings the watering can.", 0.7, "can_in"),
    ("grow", "benny", "Splish, splash! Drink up, little seeds!", 0.2, "water"),
    ("grow", "narrator", "And seeds need warm sunshine, too!", 0.5, "sun_shine"),
    ("grow", "mia", "Sun up high, rain comes down, little seeds, grow up from the ground!", 0.5, "chant1"),
    ("grow", "benny", "Sun up high, rain comes down, little seeds, grow up from the ground!", 0.3, "chant2"),
    ("grow", "benny", "Are they growing yet?", 0.8, "peek"),
    ("grow", "narrator", "Not yet, Benny. Growing takes time. Let's wait, and wait.", 0.4, "wait"),
    ("grow", "mia", "Let's do a growing dance while we wait!", 0.6, "dance_start"),
    ("grow", "mia", "Stretch up tall, like a flower!", 0.6, "stretch"),
    ("grow", "benny", "Wiggle, wiggle, like a worm!", 0.6, "wiggle"),
    ("grow", "mia", "And hop, hop, hop, like a bunny!", 0.6, "hophop"),
    ("grow", "narrator", "Look! Something is popping up!", 2.6, "sprout"),

    # 5. The rainbow
    ("bloom", "mia", "A red flower!", 0.4, "f0"),
    ("bloom", "benny", "An orange flower!", 0.4, "f1"),
    ("bloom", "mia", "A yellow flower!", 0.4, "f2"),
    ("bloom", "benny", "A blue flower!", 0.4, "f3"),
    ("bloom", "mia", "A purple flower!", 0.4, "f4"),
    ("bloom", "narrator", "And all the stems and leaves are green! Red, orange, yellow, green, blue, and purple. It's a rainbow garden!", 0.6, "rainbow"),
    ("bloom", "mia", "Let's sing the rainbow song!", 0.8, "mia_jump"),
    ("bloom", "mia", "Red and orange, yellow too! Green and blue, and purple, woo!", 0.4, "sing"),

    # 6. Butterfly + goodbye
    ("end", "benny", "Look, Mia! A butterfly came to visit!", 0.6, "butterfly"),
    ("end", "mia", "Our garden makes everyone happy!", 0.3, "mia_jump"),
    ("end", "narrator", "Which color flower is your favorite? Point to it!", 0.5, "ask"),
    ("end", "mia", "Thank you for helping, Benny!", 1.6, "hug"),
    ("end", "narrator", "Mia and Benny share a big, happy hug.", 0.3, "hug2"),
    ("end", "benny", "Best friends grow the best gardens!", 0.3, "benny_hop"),

    # 7. Outro
    ("outro", "narrator", "Bye-bye, friends! See you next time!", 2.2, "outro"),
    ("outro", "mia", "Bye-bye!", 0.2, "byebye"),
]

VOICES = {
    # kokoro voice, kokoro speed, pitch factor (resample)
    "narrator": ("af_heart", 0.92, 1.0),
    "mia": ("af_sky", 0.88, 1.13),
    "benny": ("am_puck", 0.86, 1.16),
}
