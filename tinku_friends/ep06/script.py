# Tinku & Friends — story: कोहरे में बड़ा भूत / The Giant Ghost in the Fog   (Hindi dialogue, English captions · spooky-funny + learning)
# Original story (trend: winter fog-night stories). LINES = (scene, speaker, hindi, english_caption, pause_before_seconds, cue)
# scenes: lane (foggy winter evening, walking home with jalebis) · ghost (giant shadow in the fog) · hide (behind the front wall)
#         · reveal (torch: a tiny flour-covered kitten on the wall) · home (Moti gets floured)
# "barfi" = Dadi's white kitten, meows only (synthesised in tts.py, like Moti's barks)

STORY_HI = "कोहरे में बड़ा भूत"
STORY_EN = "The Giant Ghost in the Fog"
LANG = "hi"
NEXT_EN = "The Jingle on Nani's Roof"
NEXT = f"Next: {NEXT_EN}!"

LINES = [
    ("lane",   "golu",  "टिंकू भैया, कितनी ठंड है! मेरी नाक तो बर्फ़ बन गई!", "Tinku bhaiya, it's so cold! My nose has turned into ice!", 0.9, "cold"),
    ("lane",   "tinku", "और ये कोहरा देखो! सामने कुछ दिख ही नहीं रहा।", "And look at this fog! We can't see anything ahead.", 0.5, "fog"),
    ("lane",   "golu",  "मुझे तो बस ये गरम-गरम जलेबी दिख रही है!", "I can only see these hot, hot jalebis!", 0.5, "jalebi"),
    ("lane",   "tinku", "ये दादी के लिए हैं, गोलू! रास्ते में मत खाना।", "They're for Dadi, Golu! Don't eat them on the way.", 0.5, "dadi"),
    ("lane",   "golu",  "बस एक… छोटी सी…", "Just one... a tiny one...", 0.4, "justone"),
    ("lane",   "moti",  "", "Woof! Woof!", 0.5, "bark1"),
    ("lane",   "tinku", "मोती, क्या हुआ? किस पर भौंक रहे हो?", "Moti, what happened? Who are you barking at?", 0.5, "what"),
    ("ghost",  "barfi", "", "Meeee-ooow...", 1.8, "meow1"),
    ("ghost",  "golu",  "वो… वो क्या है? कोहरे में कुछ बहुत बड़ा…", "Wh-what's that? Something HUGE in the fog...", 0.6, "huge"),
    ("ghost",  "golu",  "भूत! बड़ा सा भूत!", "A ghost! A giant ghost!", 0.3, "ghost"),
    ("ghost",  "tinku", "इसकी तो चमकती हुई आँखें भी हैं!", "It even has glowing eyes!", 0.4, "eyes"),
    ("ghost",  "moti",  "", "Woof! Woof! Woof!", 0.3, "bark2"),
    ("hide",   "golu",  "भैया, ये हमारी जलेबी खाने आया है!", "Bhaiya, it's come to eat our jalebis!", 1.3, "eatjal"),
    ("hide",   "tinku", "श्श्श! दीवार के पीछे छुप जाओ!", "Shhh! Hide behind the wall!", 0.4, "hidecue"),
    ("hide",   "golu",  "भूत इतना बड़ा क्यों है? ये तो पेड़ जितना ऊँचा है!", "Why is the ghost so big? It's as tall as a tree!", 1.0, "big"),
    ("hide",   "tinku", "रुको… जब ये हिलता है, तो धुंधला भी हो जाता है।", "Wait... when it moves, it goes all blurry.", 0.6, "blurry"),
    ("hide",   "tinku", "ये तो कोहरे पर बनी एक परछाई है! स्ट्रीटलाइट के सामने से!", "It's a shadow on the fog! From in front of the streetlight!", 0.5, "shadow"),
    ("hide",   "golu",  "परछाई? भूत की परछाई?", "A shadow? A ghost's shadow?", 0.4, "ghostshadow"),
    ("hide",   "tinku", "चलो, टॉर्च जलाकर देखते हैं कि असली में कौन है।", "Let's switch on the torch and see who it really is.", 0.5, "torch"),
    ("reveal", "golu",  "अरे! ये तो एक छोटी सी बिल्ली है!", "Hey! It's just a tiny kitten!", 2.4, "kitten"),
    ("reveal", "barfi", "", "Meow!", 0.3, "meow2"),
    ("reveal", "tinku", "ये तो दादी की बिल्ली बर्फ़ी है! पूरी आटे में लिपटी हुई!", "It's Dadi's kitten, Barfi! All covered in flour!", 0.5, "barfi"),
    ("reveal", "golu",  "इतनी छोटी बिल्ली… और इतनी बड़ी परछाई?", "Such a tiny kitten... and such a big shadow?", 0.5, "howbig"),
    ("reveal", "tinku", "रोशनी के पास छोटी चीज़ हो, तो उसकी परछाई बहुत बड़ी बनती है!", "When something small is close to a light, its shadow gets really big!", 0.5, "learn"),
    ("reveal", "tinku", "और बिल्ली की आँखें रोशनी में चमकती हैं, इसलिए वो भूत जैसी लगीं!", "And a cat's eyes shine in the light. That's why they looked spooky!", 0.4, "learn2"),
    ("reveal", "golu",  "बर्फ़ी, तुम आटे के डिब्बे में कूदी थी ना?", "Barfi, you jumped into the flour tin, didn't you?", 0.6, "tin"),
    ("reveal", "barfi", "", "Meow! Meow!", 0.3, "meow3"),
    ("reveal", "golu",  "देखो, ये जलेबी की खुशबू के पीछे-पीछे आई थी!", "Look, she followed the smell of the jalebis!", 0.5, "smell"),
    ("home",   "tinku", "चलो बर्फ़ी, तुम्हें दादी के पास ले चलते हैं।", "Come on Barfi, let's take you to Dadi.", 1.6, "take"),
    ("home",   "golu",  "अरे! बर्फ़ी ने सारा आटा मोती पर झाड़ दिया!", "Oh no! Barfi shook all the flour onto Moti!", 1.8, "shake"),
    ("home",   "tinku", "हा हा! अब मोती बर्फ़ वाला कुत्ता बन गया!", "Ha ha! Now Moti is a snowy puppy!", 0.4, "snowy"),
    ("home",   "moti",  "", "Woof!", 0.3, "bark3"),
    ("home",   "golu",  "और भूत वाली जलेबी… मैं खा लूँ?", "And the ghost's jalebi... can I eat it?", 0.6, "eatit"),
    ("home",   "tinku", "गोलू!", "Golu!", 0.3, "golu"),
    ("home",   "tinku", "अगली बार देखना — नानी की छत पर आधी रात को छम-छम कौन करता है!", "Next time: who's jingling on Nani's roof at midnight?!", 1.2, "next"),
    ("home",   "golu",  "बाय-बाय दोस्तों!", "Bye-bye, friends!", 0.5, "bye1"),
    ("home",   "tinku", "बाय-बाय!", "Bye-bye!", 0.3, "bye2"),
]

NAMES = {"tinku": ("टिंकू", "#f08a00"), "golu": ("गोलू", "#2fa84a"), "moti": ("मोती", "#a8673a"), "barfi": ("बर्फ़ी", "#7a8ab8")}
