# Story: Pinky and the Secret Level   (English dialogue · video-game adventure + rainbow colours)
# Original story (trend weekend, video-game theme; nothing from any real game). LINES = (scene, speaker, english_line, english_caption, pause, cue)
# scenes: room (Sunday morning, TV + console) · sky (secret level: floating cloud islands, colour tiles, rainbow bridge) · treasure · back (room)

STORY_HI = "पिंकी और सीक्रेट लेवल"
STORY_EN = "Pinky and the Secret Level"
LANG = "en"
NEXT_EN = "Golu's Giant Sneeze"
NEXT = f"Next: {NEXT_EN}!"

LINES = [
    ("room",     "pinky", "Tinku! Wake up! I kept the golden key safe all night!", "Tinku! Wake up! I kept the golden key safe all night!", 0.8, "wake"),
    ("room",     "tinku", "Yawn... Pinky, it's Sunday morning!", "Yawn... Pinky, it's Sunday morning!", 0.5, "yawn"),
    ("room",     "pinky", "Exactly! No school today. Secret level time!", "Exactly! No school today. Secret level time!", 0.4, "exactly"),
    ("room",     "moti",  "", "Woof! Woof!", 0.4, "bark1"),
    ("room",     "tinku", "Okay, okay! Moti wants to come too.", "Okay, okay! Moti wants to come too.", 0.4, "okay"),
    ("room", "tinku", "Where did you hide the key all night?", "Where did you hide the key all night?", 0.4, "where"),
    ("room", "pinky", "Under my pillow! I checked it ten times!", "Under my pillow! I checked it ten times!", 0.4, "pillow"),
    ("room",     "pinky", "Key goes in the console... and... turn!", "Key goes in the console... and... turn!", 0.5, "turn"),
    ("room",     "tinku", "Here we go again!", "Here we go again!", 1.0, "pull"),
    ("sky",      "pinky", "Wow! We're on an island floating in the clouds!", "Wow! We're on an island floating in the clouds!", 2.6, "wow"),
    ("sky",      "tinku", "And there's a treasure chest on that far island!", "And there's a treasure chest on that far island!", 0.5, "chest"),
    ("sky",      "pinky", "But there's no bridge. How do we get across?", "But there's no bridge. How do we get across?", 0.5, "nobridge"),
    ("sky",      "tinku", "Look, seven coloured tiles on the ground.", "Look, seven coloured tiles on the ground.", 0.6, "tiles"),
    ("sky", "pinky", "Red, yellow, blue, green... they're all mixed up.", "Red, yellow, blue, green... they're all mixed up.", 0.4, "mixed"),
    ("sky",      "moti",  "", "Woof!", 0.5, "bark2"),
    ("sky",      "tinku", "Oops! Moti jumped on green first. Wrong tile!", "Oops! Moti jumped on green first. Wrong tile!", 0.9, "wrong"),
    ("sky", "tinku", "The tiles are shaking! Moti, come back!", "The tiles are shaking! Moti, come back!", 0.3, "shaking"),
    ("sky",      "pinky", "Wait! I know this pattern. It's a rainbow!", "Wait! I know this pattern. It's a rainbow!", 0.6, "pattern"),
    ("sky",      "pinky", "Red... orange... yellow...", "Red... orange... yellow...", 1.0, "r1"),
    ("sky",      "pinky", "Green... blue... indigo... violet!", "Green... blue... indigo... violet!", 0.8, "r2"),
    ("sky",      "tinku", "Look! Every jump builds a piece of the bridge!", "Look! Every jump builds a piece of the bridge!", 0.6, "bridge"),
    ("sky", "tinku", "Pinky, how did you know the order?", "Pinky, how did you know the order?", 0.5, "how"),
    ("sky", "pinky", "Mummy taught me. A rainbow always goes from red to violet!", "Mummy taught me. A rainbow always goes from red to violet!", 0.4, "mummy"),
    ("sky",      "pinky", "A rainbow bridge! Come on, let's cross!", "A rainbow bridge! Come on, let's cross!", 0.8, "cross"),
    ("sky", "pinky", "Ooh, it's a bit wobbly! Hold my hand, Tinku.", "Ooh, it's a bit wobbly! Hold my hand, Tinku.", 1.4, "wobbly"),
    ("sky",      "tinku", "Don't look down, Moti. Just look at the treasure!", "Don't look down, Moti. Just look at the treasure!", 0.8, "dontlook"),
    ("sky",      "moti",  "", "Woof!", 0.4, "bark3"),
    ("treasure", "pinky", "We made it! Tinku, you open it.", "We made it! Tinku, you open it.", 2.2, "madeit"),
    ("treasure", "tinku", "No, Pinky. You solved the puzzle. You open it!", "No, Pinky. You solved the puzzle. You open it!", 0.5, "youopen"),
    ("treasure", "pinky", "Okay! One... two... three!", "Okay! One... two... three!", 0.5, "open"),
    ("treasure", "tinku", "Wow! A golden trophy! It says... BEST TEAM!", "Wow! A golden trophy! It says... BEST TEAM!", 2.2, "trophy"),
    ("treasure", "pinky", "And fireworks! The whole sky is sparkling!", "And fireworks! The whole sky is sparkling!", 0.6, "fireworks"),
    ("treasure", "tinku", "There's a note too: Thanks for playing, friends!", "There's a note too: Thanks for playing, friends!", 0.5, "note"),
    ("treasure", "moti",  "", "Woof! Woof! Woof!", 0.4, "bark4"),
    ("treasure", "tinku", "Game complete! We finished the whole game!", "Game complete! We finished the whole game!", 0.6, "complete"),
    ("treasure", "pinky", "Golu is going to love this trophy!", "Golu is going to love this trophy!", 0.5, "golu"),
    ("treasure", "tinku", "Let's take it home and show him!", "Let's take it home and show him!", 0.6, "takehome"),
    ("back",     "pinky", "Home sweet home! Hey, the trophy came with us!", "Home sweet home! Hey, the trophy came with us!", 2.2, "back"),
    ("back",     "tinku", "Next time: Golu's sneeze is so giant, everything flies away!", "Next time: Golu's sneeze is so giant, everything flies away!", 0.6, "next"),
    ("back",     "pinky", "Bye-bye, friends!", "Bye-bye, friends!", 0.5, "bye1"),
    ("back",     "moti",  "", "Woof!", 0.3, "bye2"),
]

NAMES = {"tinku": ("Tinku", "#f08a00"), "pinky": ("Pinky", "#e8327f"), "moti": ("Moti", "#a8673a")}
