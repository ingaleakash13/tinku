# Story: गोलू और आख़िरी बॉस / Golu vs the Final Boss   (Hindi dialogue, English captions · funny video-game adventure)
# Original story (trend weekend, video-game theme; nothing from any real game). LINES = (scene, speaker, hindi, english_caption, pause, cue)
# scenes: room (Tinku's room, TV + console) · arena (beach boss level, Pigeon King, HUD) · back (room)
# "pigeon" = the Pigeon King, who only coos (synthesised in tts.py, like Moti's barks)

STORY_HI = "गोलू और आख़िरी बॉस"
STORY_EN = "Golu vs the Final Boss"
LANG = "hi"
NEXT_EN = "Pinky and the Secret Level"
NEXT = f"Next: {NEXT_EN}!"

LINES = [
    ("room",  "golu",   "टिंकू भैया! आज बॉस से मिलना है! जल्दी गेम चलाओ!", "Tinku bhaiya! Today we meet the boss! Start the game, quick!", 0.8, "hurry"),
    ("room",  "pinky",  "कौन सा बॉस? मुझे भी खेलना है!", "Which boss? I want to play too!", 0.5, "pinkyin"),
    ("room",  "tinku",  "ठीक है पिंकी, आज हम तीनों चलेंगे! सेव वाला गेम खोलता हूँ।", "Okay Pinky, all three of us go today! I'll load the saved game.", 0.5, "load"),
    ("room",  "golu",   "मैंने अपना दानों वाला थैला भी ले लिया। रास्ते में भूख लगी तो?", "I brought my bag of grains too. What if I get hungry?", 0.5, "bag"),
    ("room",  "pinky",  "हा हा! गोलू हर जगह नाश्ता ले जाता है!", "Ha ha! Golu takes snacks everywhere!", 0.4, "snacks"),
    ("room",  "tinku",  "तैयार? तीन… दो… एक… स्टार्ट!", "Ready? Three... two... one... START!", 0.5, "start"),
    ("room",  "pinky",  "आआह! हम अंदर खिंचे जा रहे हैं!", "Aaah! We're being pulled inside!", 1.1, "pull"),
    ("arena", "pinky",  "वाह! ये तो समुद्र किनारे वाला शहर है!", "Wow! It's a city by the sea!", 2.6, "wow"),
    ("arena", "golu",   "और ऊपर लिखा है — बॉस लेवल!", "And up there it says: BOSS LEVEL!", 0.5, "bosslevel"),
    ("arena", "tinku",  "श्श्श… रेत के महल के पीछे कोई है…", "Shhh... someone is behind the sandcastle...", 0.6, "someone"),
    ("arena", "pigeon", "", "Gutur-goo!", 0.8, "coo1"),
    ("arena", "golu",   "अरे बाप रे! इतना बड़ा कबूतर!", "Oh my! Such a GIANT pigeon!", 0.4, "giant"),
    ("arena", "pinky",  "इसके सिर पर तो ताज है! ये कबूतर राजा है!", "It's wearing a crown! It's the Pigeon King!", 0.5, "crown"),
    ("arena", "golu",   "वो हमें गुस्से से क्यों देख रहा है?", "Why is he looking at us so grumpily?", 0.5, "grumpy"),
    ("arena", "tinku",  "डरो मत! मैं जाकर उसका ताज पकड़ता हूँ!", "Don't worry! I'll go and grab his crown!", 0.6, "grab"),
    ("arena", "pigeon", "", "Gutur-goo! Gutur-goo!", 1.0, "coo2"),
    ("arena", "tinku",  "अरे… अरे… पंखों की हवा से उड़ गया!", "Whoa... whoa... his wings blew me away!", 0.4, "blown"),
    ("arena", "pinky",  "टिंकू रेत के महल में घुस गया! हा हा!", "Tinku crashed into the sandcastle! Ha ha!", 0.8, "sand"),
    ("arena", "tinku",  "थू-थू! मुँह में रेत!", "Ptooh! Sand in my mouth!", 0.5, "ptooh"),
    ("arena", "pinky",  "अब मेरी बारी! मैं इस पंख से गुदगुदी करूँगी!", "My turn! I'll tickle him with this feather!", 0.6, "tickle"),
    ("arena", "pigeon", "", "Gutur-goo! Gutur-goo!", 1.0, "coo3"),
    ("arena", "pinky",  "उफ़! उसने तो मुझे भी उड़ा दिया!", "Oof! He blew me away too!", 0.4, "pinkyblown"),
    ("arena", "golu",   "रुको! ये गुड़-गुड़ की आवाज़ कहाँ से आ रही है?", "Wait! Where is that rumbly-grumbly sound coming from?", 1.0, "rumble"),
    ("arena", "tinku",  "कबूतर राजा का पेट बोल रहा है!", "It's the Pigeon King's tummy!", 0.5, "tummy"),
    ("arena", "golu",   "अच्छा! तुम्हें भूख लगी है ना? इसीलिए गुस्सा हो!", "Ohh! You're hungry, aren't you? That's why you're grumpy!", 0.6, "hungry"),
    ("arena", "golu",   "लो, मेरे थैले से दाने खाओ!", "Here, have some grains from my bag!", 0.6, "share"),
    ("arena", "pigeon", "", "Gutur-goo! Gutur-goo!", 1.4, "coo4"),
    ("arena", "pinky",  "देखो! बॉस की बार दिलों से भर गई!", "Look! The boss bar filled up with hearts!", 0.6, "hearts"),
    ("arena", "tinku",  "गोलू, तुमने तो बिना लड़े बॉस लेवल जीत लिया!", "Golu, you won the boss level without any fight!", 0.5, "won"),
    ("arena", "golu",   "कबूतर राजा अब मेरा दोस्त है! हाई-फ़ाइव!", "The Pigeon King is my friend now! High five!", 0.5, "highfive"),
    ("arena", "pigeon", "", "Gutur-goo!", 0.4, "coo5"),
    ("arena", "pinky",  "अरे! उसने हमें एक सुनहरी चाबी दी!", "Hey! He gave us a golden key!", 1.4, "key"),
    ("arena", "tinku",  "इस पर लिखा है — सीक्रेट लेवल!", "It says: SECRET LEVEL!", 0.5, "secret"),
    ("arena", "golu",   "सीक्रेट लेवल? अभी चलें?", "A secret level? Can we go now?", 0.4, "now"),
    ("arena", "tinku",  "आज के लिए गेम सेव! सोने का टाइम हो गया!", "Save the game for today! It's bedtime!", 0.6, "save"),
    ("back",  "pinky",  "धप्प! हम वापस कमरे में!", "Thud! We're back in the room!", 2.2, "back"),
    ("back",  "golu",   "मेरा थैला खाली हो गया… पर पेट नहीं, दिल भर गया!", "My bag is empty... but my heart is full!", 0.5, "empty"),
    ("back",  "tinku",  "अगली बार देखना — पिंकी और गेम का सीक्रेट लेवल!", "Next time: Pinky and the Secret Level!", 0.7, "next"),
    ("back",  "pinky",  "बाय-बाय दोस्तों!", "Bye-bye, friends!", 0.5, "bye1"),
    ("back",  "golu",   "बाय-बाय!", "Bye-bye!", 0.3, "bye2"),
]

NAMES = {"tinku": ("टिंकू", "#f08a00"), "pinky": ("पिंकी", "#e8327f"), "golu": ("गोलू", "#2fa84a"), "pigeon": ("कबूतर राजा", "#7a5cc8")}
