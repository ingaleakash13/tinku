# Tinku & Friends — story: नानी के गाँव में छत पर छम-छम! / The Jingle on Nani's Roof   (Hindi dialogue, English captions · spooky-funny)
# Original story (trend: "90s नानी का गाँव — आधी रात छत पर कौन?" midnight mysteries). LINES = (scene, speaker, hindi, english, pause, cue)
# scenes: evening (Nani's village courtyard) · night (room under the roof) · stairs (horned shadow) · roof (reveal) · morning
# "chameli" = Nani's goat, bleats only (synthesised in tts.py)

STORY_HI = "नानी के गाँव में छत पर छम-छम!"
STORY_EN = "The Jingle on Nani's Roof"
LANG = "hi"
NEXT_EN = "Sabzi Race"
NEXT = f"Next: {NEXT_EN}!"

LINES = [
    ("evening", "pinky",   "नानी! देखो, आपकी दी हुई नई पायल! छम-छम-छम!", "Nani! Look, the new anklets you gave me! Chham-chham-chham!", 0.9, "payal"),
    ("evening", "nani",    "बड़ी प्यारी लग रही है, मेरी गुड़िया!", "They look lovely, my little doll!", 0.5, "lovely"),
    ("evening", "tinku",   "नानी के गाँव में तो आसमान तारों से भरा है!", "In Nani's village the sky is full of stars!", 0.6, "stars"),
    ("evening", "nani",    "चलो बच्चो, अब सो जाओ। और पायल खिड़की पर रख दो, पिंकी।", "Come on kids, time to sleep. And keep the anklets on the window, Pinky.", 0.5, "sleep"),
    ("evening", "pinky",   "ठीक है नानी। गुड नाइट!", "Okay Nani. Good night!", 0.4, "goodnight"),
    ("night",   "pinky",   "टिंकू! उठो! छत पर कोई चल रहा है!", "Tinku! Wake up! Someone's walking on the roof!", 3.6, "wake"),
    ("night",   "tinku",   "आधी रात को? छत पर कौन होगा?", "At midnight? Who'd be on the roof?", 0.5, "who"),
    ("night",   "pinky",   "और ये… ये तो मेरी पायल की आवाज़ है!", "And that's... that's the sound of MY anklets!", 1.0, "sound"),
    ("night",   "tinku",   "खिड़की देखो… तुम्हारी पायल गायब है!", "Look at the window... your anklets are gone!", 0.5, "gone"),
    ("night",   "pinky",   "भूत ने मेरी पायल पहन ली!", "A ghost is wearing my anklets!", 0.4, "ghostpayal"),
    ("night",   "tinku",   "डरो मत। टॉर्च लो, धीरे-धीरे ऊपर चलते हैं।", "Don't be scared. Take the torch, let's go up slowly.", 0.5, "upstairs"),
    ("stairs",  "pinky",   "श्श्श! दीवार पर देखो… परछाई!", "Shhh! Look at the wall... a shadow!", 1.8, "shadow"),
    ("stairs",  "tinku",   "इसके तो… सींग हैं!", "It has... HORNS!", 0.6, "horns"),
    ("stairs",  "chameli", "", "Meh-eh-eh!", 0.3, "bleat1"),
    ("stairs",  "pinky",   "और ये चर-चर किसकी आवाज़ है? कोई कुछ चबा रहा है!", "And what's that crunch-crunch? Something's chewing!", 0.8, "chew"),
    ("stairs",  "tinku",   "रुको… यहाँ सूखी घास गिरी है। और खुरों के निशान!", "Wait... there's dry hay here. And hoof prints!", 0.6, "hay"),
    ("stairs",  "pinky",   "खुर? भूतों के खुर होते हैं क्या?", "Hooves? Do ghosts have hooves?", 0.4, "hooves"),
    ("roof",    "tinku",   "एक… दो… तीन… टॉर्च ऑन!", "One... two... three... torch ON!", 1.4, "torch"),
    ("roof",    "pinky",   "अरे! ये तो नानी की बकरी चमेली है!", "Hey! It's Nani's goat, Chameli!", 1.2, "chameli"),
    ("roof",    "tinku",   "और उसके पैरों में… तुम्हारी पायल फँसी है! हा हा!", "And on her legs... your anklets are stuck! Ha ha!", 0.5, "stuck"),
    ("roof",    "chameli", "", "Meh-meh!", 0.4, "bleat2"),
    ("roof",    "pinky",   "चमेली नाच रही है! छम-छम-छम!", "Chameli is dancing! Chham-chham-chham!", 1.4, "dance"),
    ("roof",    "nani",    "अरे! इतनी रात को इतना शोर? चमेली! तू यहाँ कैसे?", "Hey! All this noise at night? Chameli! How did you get up here?", 1.2, "nanicomes"),
    ("roof",    "tinku",   "नानी, ये खिड़की से पायल लेकर भाग आई थी!", "Nani, she grabbed the anklets from the window and ran up here!", 0.5, "explain"),
    ("roof",    "nani",    "हा हा! चमेली को भी सजना पसंद है!", "Ha ha! Chameli likes dressing up too!", 0.5, "dressup"),
    ("morning", "pinky",   "पायल तो वापस मिल गई… पर चमेली उदास हो गई।", "I got my anklets back... but now Chameli is sad.", 2.0, "sad"),
    ("morning", "nani",    "तो चमेली के लिए एक छोटी घंटी बाँध देते हैं!", "Then let's tie a little bell on Chameli!", 0.5, "bell"),
    ("morning", "chameli", "", "Meh-meh!", 1.2, "bleat3"),
    ("morning", "tinku",   "अगली बार देखना — गोलू और सब्ज़ियों की ज़बरदस्त दौड़!", "Next time: Golu's crazy race with the vegetables!", 1.0, "next"),
    ("morning", "pinky",   "बाय-बाय दोस्तों!", "Bye-bye, friends!", 0.5, "bye1"),
    ("morning", "tinku",   "बाय-बाय!", "Bye-bye!", 0.3, "bye2"),
]

NAMES = {"tinku": ("टिंकू", "#f08a00"), "pinky": ("पिंकी", "#e8327f"), "nani": ("नानी", "#8a3a8a"), "chameli": ("चमेली", "#7a6a4a")}
