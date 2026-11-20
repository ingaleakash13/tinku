# Story: GTA = ग्रैंड टिंकू एडवेंचर / Grand Tinku Adventure   (Hindi dialogue, English captions · funny video-game adventure)
# Original story (trend weekend, video-game theme; nothing from any real game). LINES = (scene, speaker, hindi, english_caption, pause, cue)
# scenes: room (Tinku's room, TV + console) · city (cartoon beach-city game world, HUD) · kart (go-kart chase) · arcade (claw machine) · back (room)

STORY_HI = "ग्रैंड टिंकू एडवेंचर"
STORY_EN = "Grand Tinku Adventure"
LANG = "hi"
NEXT_EN = "Golu vs the Final Boss"
NEXT = f"Next: {NEXT_EN}!"

LINES = [
    ("room",   "golu",  "टिंकू भैया! ये नया वीडियो गेम कब खेलेंगे?", "Tinku bhaiya! When do we play the new video game?", 0.8, "newgame"),
    ("room",   "tinku", "अभी! होमवर्क ख़त्म, अब गेम टाइम!", "Right now! Homework's done, it's game time!", 0.5, "gametime"),
    ("room",   "golu",  "इस गेम का नाम क्या है?", "What's this game called?", 0.4, "name"),
    ("room",   "tinku", "जी टी ए… ग्रैंड टिंकू एडवेंचर!", "G.T.A.… Grand Tinku Adventure!", 0.4, "gta"),
    ("room",   "moti",  "", "Woof! Woof!", 0.4, "bark1"),
    ("room",   "golu",  "स्टार्ट दबाओ! जल्दी, स्टार्ट!", "Press start! Quick, START!", 0.4, "start"),
    ("room",   "golu",  "अरे! टीवी हमें अंदर खींच रहा है!", "Whoa! The TV is pulling us in!", 1.3, "pull"),
    ("room",   "tinku", "कसकर पकड़ो, गोलू!", "Hold on tight, Golu!", 0.2, "hold"),
    ("city",   "golu",  "वाह! हम सच में गेम के अंदर आ गए!", "Wow! We're really inside the game!", 2.8, "inside"),
    ("city",   "tinku", "ऊपर देखो — दिल, सिक्के, और छोटा सा नक्शा!", "Look up there: hearts, coins and a little map!", 0.5, "hud"),
    ("city",   "golu",  "समुद्र! ताड़ के पेड़! और गुलाबी आसमान!", "The sea! Palm trees! And a pink sky!", 0.5, "sea"),
    ("city",   "golu",  "और वो देखो, पिज़्ज़ा की दुकान! गेम में भी भूख लगती है!", "And look, a pizza shop! I get hungry even inside a game!", 0.4, "pizza"),
    ("city",   "tinku", "मिशन नंबर एक आ गया!", "Here comes Mission One!", 0.8, "mission1"),
    ("city",   "golu",  "आइसक्रीम वाली गाड़ी अपने आप भाग रही है!", "The ice-cream cart is rolling away by itself!", 0.5, "cart"),
    ("city",   "tinku", "चलो, हमारी गो-कार्ट में बैठो!", "Quick, hop into our go-kart!", 0.5, "kart"),
    ("kart",   "golu",  "तेज़! और तेज़, भैया!", "Faster! Faster, bhaiya!", 2.4, "faster"),
    ("kart",   "tinku", "सिक्के उठाते चलो! टिंग! टिंग!", "Grab the coins on the way! Ting! Ting!", 0.5, "coins"),
    ("kart",   "golu",  "पचास सिक्के! साठ! सत्तर!", "Fifty coins! Sixty! Seventy!", 0.3, "count"),
    ("kart",   "golu",  "सामने केले का छिलका!", "Banana peel ahead!", 0.7, "banana"),
    ("kart",   "tinku", "जंप!", "JUMP!", 0.2, "jump"),
    ("kart",   "golu",  "हम उड़ रहे हैं!", "We're flying!", 0.5, "flying"),
    ("kart",   "golu",  "पकड़ ली! आइसक्रीम गाड़ी रुक गई!", "Got it! The ice-cream cart stopped!", 2.2, "caught"),
    ("kart",   "tinku", "मिशन पास! सौ सिक्के!", "Mission passed! A hundred coins!", 0.5, "passed1"),
    ("arcade", "moti",  "", "Woof! Woof! Woof!", 1.8, "bark2"),
    ("arcade", "golu",  "ये आवाज़… ये तो मोती है!", "That bark... it's Moti!", 0.4, "motivoice"),
    ("arcade", "tinku", "अरे! मोती खिलौनों वाली क्रेन मशीन में फँस गया!", "Oh no! Moti is stuck in the toy claw machine!", 0.5, "stuck"),
    ("arcade", "golu",  "मिशन नंबर दो — मोती को बचाओ!", "Mission Two: rescue Moti!", 0.5, "mission2"),
    ("arcade", "tinku", "मैं क्रेन चलाता हूँ। थोड़ा बाएँ… थोड़ा नीचे…", "I'll work the claw. A bit left... a bit down...", 0.6, "steer"),
    ("arcade", "golu",  "मोती, हिलना मत! बिल्कुल हिलना मत!", "Moti, don't move! Don't move at all!", 0.4, "dontmove"),
    ("arcade", "golu",  "ओहो! क्रेन ने तो टेडी बियर पकड़ लिया!", "Oh no! The claw grabbed a teddy bear!", 1.4, "teddy"),
    ("arcade", "tinku", "हा हा! टेडी भी अच्छा है, पर हमें मोती चाहिए!", "Ha ha! Teddy is nice, but we need Moti!", 0.5, "needmoti"),
    ("arcade", "tinku", "एक बार और! इस बार ध्यान से…", "One more try! Carefully this time...", 0.5, "again"),
    ("arcade", "golu",  "पकड़ लिया! मोती बाहर आ गया!", "Got him! Moti is out!", 2.4, "gotmoti"),
    ("arcade", "moti",  "", "Woof! Woof!", 0.3, "bark3"),
    ("arcade", "tinku", "मिशन पास! लेवल अप!", "Mission passed! LEVEL UP!", 0.5, "levelup"),
    ("arcade", "golu",  "मोती, अब तुम भी हमारी टीम में हो!", "Moti, now you're on our team too!", 0.4, "team"),
    ("arcade", "golu",  "भैया… आसमान में इतनी बड़ी परछाईं किसकी है?", "Bhaiya... whose giant shadow is that in the sky?", 1.6, "shadow"),
    ("arcade", "tinku", "लिखा है… बॉस आ रहा है!", "It says... the BOSS is coming!", 0.6, "boss"),
    ("arcade", "tinku", "घड़ी देखो — खाने का टाइम! गेम सेव करो!", "Look at the clock: dinner time! Save the game!", 0.8, "save"),
    ("back",   "golu",  "धप्प! हम वापस कमरे में आ गए!", "Thud! We're back in the room!", 2.2, "back"),
    ("back",   "golu",  "पर उस बॉस का क्या होगा?", "But what about that boss?", 0.5, "whatboss"),
    ("back",   "tinku", "बॉस इंतज़ार कर लेगा। पहले खाना!", "The boss can wait. Dinner first!", 0.5, "dinner"),
    ("back",   "tinku", "अगली बार देखना — गोलू और गेम का आख़िरी बॉस!", "Next time: Golu vs the Final Boss!", 0.7, "next"),
    ("back",   "golu",  "बाय-बाय दोस्तों!", "Bye-bye, friends!", 0.5, "bye1"),
    ("back",   "moti",  "", "Woof!", 0.3, "bye2"),
]

NAMES = {"tinku": ("टिंकू", "#f08a00"), "golu": ("गोलू", "#2fa84a"), "moti": ("मोती", "#a8673a")}
