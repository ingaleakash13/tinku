# Tinku & Friends — NEW FORMAT story (narrator + full arc): नानी के गाँव में आधी रात का राज़ / The Midnight Secret at Nani's Village
# Owner (24 Nov 2026): no sound-words like छम-छम / टन-टन / धप्प in lines or on screen.
# Hindi narration + dialogue, English captions. Trend: "90s नानी का गाँव — आधी रात छत पर कौन?" midnight mysteries.
# Arc: Pinky WANTS to dance at tomorrow's fair in Nani's new anklets -> anklets vanish at midnight, chham-chham on the roof ->
# horned shadow, kids flee -> sad morning, detective clues -> trap at night -> it's Chameli the goat (her bell broke, she
# missed the jingle) -> chase, slip into hay, anklets fly, caught -> fair: Pinky dances, Chameli gets a new bell and dances too.
# LINES = (scene, speaker, hindi, english_caption, pause_before_seconds, cue)

STORY_HI = "नानी के गाँव में आधी रात का राज़"
STORY_EN = "The Midnight Secret at Nani's Village"
LANG = "hi"
NEXT_EN = "Sabzi Race"
NEXT = f"Next: {NEXT_EN}!"

LINES = [
    ("road",    "narrator", "सर्दियों की छुट्टियाँ शुरू हो गई थीं। टिंकू और पिंकी पहली बार नानी के गाँव जा रहे थे।", "Winter holidays had begun. Tinku and Pinky were going to Nani's village for the very first time.", 0.6, "n_intro"),
    ("road",    "narrator", "चारों तरफ़ हरे-भरे खेत थे, और दूर से नानी का छोटा-सा घर दिख रहा था।", "Green fields everywhere, and far away they could see Nani's little house.", 0.4, "n_fields"),
    ("road",    "pinky",    "टिंकू, देखो! वो रहा नानी का घर! चलो दौड़ लगाते हैं!", "Tinku, look! There's Nani's house! Let's race!", 0.4, "race"),
    ("road",    "tinku",    "रुको पिंकी! मेरा बैग बहुत भारी है!", "Wait, Pinky! My bag is so heavy!", 0.5, "heavy"),
    ("court",   "narrator", "नानी ने दोनों को कसकर गले से लगा लिया। आँगन में नानी की प्यारी बकरी चमेली भी घूम रही थी।", "Nani hugged them both tight. Nani's sweet goat, Chameli, was wandering around the courtyard.", 2.4, "n_hug"),
    ("court",   "nani",     "आ गए मेरे बच्चे! पिंकी, देख तेरे लिए क्या लाई हूँ।", "My children are here! Pinky, look what I got for you.", 0.4, "gift"),
    ("court",   "pinky",    "नई पायल! कितनी सुंदर है, नानी!", "New anklets! They're so beautiful, Nani!", 0.5, "payal"),
    ("court",   "nani",     "कल गाँव में मेला है। तू इन्हें पहनकर स्टेज पर नाचेगी ना?", "Tomorrow there's a fair in the village. You'll wear them and dance on the stage, won't you?", 0.4, "fair"),
    ("court",   "pinky",    "हाँ नानी! मैं इन्हें पहनकर सबसे अच्छा नाचूँगी!", "Yes, Nani! I'll wear them and dance the best!", 0.4, "dance1"),
    ("court",   "chameli",  "", "Meh-meh!", 0.5, "bleat1"),
    ("court",   "narrator", "चमेली पायल के घुँघरुओं की आवाज़ बड़े ध्यान से सुन रही थी।", "Chameli was listening very carefully to the sound of the anklet bells.", 0.4, "n_listen"),
    ("court",   "tinku",    "देखो, चमेली को भी पायल पसंद आ गई!", "Look, Chameli likes the anklets too!", 0.4, "likes"),
    ("court",   "nani",     "उसकी पुरानी घंटी टूट गई है ना, इसलिए आजकल बड़ी चुप-चुप रहती है।", "Her old bell broke, you see. That's why she's been so quiet lately.", 0.4, "bellbroke"),
    ("night",   "narrator", "रात हुई। पिंकी ने पायल खिड़की पर रख दी, और दोनों रज़ाई में घुसकर सो गए।", "Night fell. Pinky put the anklets on the window, and they snuggled under the quilt and fell asleep.", 2.2, "n_night"),
    ("night",   "narrator", "आधी रात को… अचानक छत से एक आवाज़ आई।", "At midnight... suddenly, a sound came from the roof.", 1.0, "n_midnight"),
    ("night",   "pinky",    "टिंकू… टिंकू! उठो! सुनो… छत पर पायल की आवाज़!", "Tinku... Tinku! Wake up! Listen... anklets on the roof!", 2.6, "wake"),
    ("night",   "tinku",    "आधी रात को छत पर कौन होगा?", "Who'd be on the roof at midnight?", 0.5, "who"),
    ("night",   "pinky",    "मेरी पायल! खिड़की पर नहीं है!", "My anklets! They're not on the window!", 0.7, "gone"),
    ("night",   "tinku",    "चलो, टॉर्च लेकर देखते हैं। धीरे-धीरे।", "Come on, let's take the torch and look. Slowly.", 0.5, "torch1"),
    ("stairs",  "narrator", "दोनों दबे पाँव सीढ़ियाँ चढ़ने लगे। हर सीढ़ी पर दिल ज़ोर-ज़ोर से धड़क रहा था।", "They tiptoed up the stairs. With every step, their hearts beat louder.", 1.8, "n_tiptoe"),
    ("stairs",  "pinky",    "श्श्श! दीवार पर देखो…", "Shhh! Look at the wall...", 0.6, "wall"),
    ("stairs",  "narrator", "दीवार पर एक बहुत बड़ी परछाई थी… और उसके सिर पर दो नुकीले सींग!", "On the wall was a huge shadow... with two pointy horns on its head!", 0.5, "n_shadow"),
    ("stairs",  "tinku",    "स… सींग! भागो!", "H-horns! RUN!", 0.4, "run"),
    ("stairs",  "narrator", "दोनों उल्टे पाँव भागे… और सीधे रज़ाई के अंदर!", "They turned and ran... straight back under the quilt!", 0.6, "n_ran"),
    ("morning", "narrator", "सुबह हुई। मुर्गे ने बाँग दी। पर पिंकी बहुत उदास थी।", "Morning came. The rooster crowed. But Pinky was very sad.", 2.6, "n_morning"),
    ("morning", "pinky",    "मेरी पायल चली गई। अब मैं मेले में कैसे नाचूँगी?", "My anklets are gone. How will I dance at the fair now?", 0.5, "sad"),
    ("morning", "tinku",    "उदास मत हो, पिंकी। हम जासूस बनेंगे और पता लगाएँगे!", "Don't be sad, Pinky. We'll be detectives and find out!", 0.5, "detective"),
    ("clues",   "narrator", "दोनों छत पर गए। वहाँ उन्हें कुछ अजीब चीज़ें मिलीं।", "They went up to the roof. There they found some strange things.", 2.0, "n_clues"),
    ("clues",   "tinku",    "देखो, सूखी घास… और ये छोटे-छोटे निशान।", "Look, dry hay... and these tiny marks.", 0.5, "hay"),
    ("clues",   "pinky",    "ये तो भूत के पैर नहीं लगते। ये तो… खुर जैसे हैं!", "These don't look like ghost feet. They look like... hooves!", 0.6, "hooves"),
    ("clues",   "tinku",    "मेरे पास एक प्लान है! आज रात हम भूत को पकड़ेंगे!", "I have a plan! Tonight we'll catch the ghost!", 0.6, "plan"),
    ("trap",    "narrator", "रात को दोनों रज़ाई ओढ़कर छत के कोने में छिप गए। टिंकू ने सीढ़ियों पर घंटियों वाली एक डोरी बाँध दी।", "That night they hid in a corner of the roof under a quilt. Tinku tied a string of little bells across the stairs.", 2.2, "n_trap"),
    ("trap",    "pinky",    "टिंकू, मुझे डर लग रहा है।", "Tinku, I'm scared.", 0.6, "scared"),
    ("trap",    "tinku",    "मैं यहीं हूँ। बस टॉर्च तैयार रखो।", "I'm right here. Just keep the torch ready.", 0.4, "ready"),
    ("trap",    "narrator", "ठीक आधी रात को… फिर से पायल की आवाज़ आई… और फिर डोरी की घंटियाँ बज उठीं!", "Right at midnight... the anklet sound came again... and then the bells on the string rang!", 1.2, "n_bells"),
    ("trap",    "tinku",    "अभी! टॉर्च ऑन!", "NOW! Torch on!", 0.4, "torchon"),
    ("trap",    "pinky",    "अरे! ये तो… चमेली है!", "Hey! It's... Chameli!", 1.0, "itschameli"),
    ("trap",    "tinku",    "और उसके पैरों में तुम्हारी पायल! हा हा हा!", "And your anklets are on her legs! Ha ha ha!", 0.4, "onlegs"),
    ("trap",    "chameli",  "", "Meh-meh!", 0.3, "bleat2"),
    ("chase",   "narrator", "पकड़े जाने के डर से चमेली पूरी छत पर भागने लगी।", "Afraid of being caught, Chameli ran all over the roof.", 0.8, "n_chase"),
    ("chase",   "pinky",    "रुको चमेली! मेरी पायल!", "Stop, Chameli! My anklets!", 0.8, "stop"),
    ("chase",   "narrator", "चमेली फिसली, और सीधे घास के ढेर में जा गिरी! पायल उछलकर हवा में उड़ी…", "Chameli slipped and fell right into the hay pile! The anklets flew up into the air...", 1.4, "n_slip"),
    ("chase",   "tinku",    "पकड़ ली!", "Got them!", 0.6, "caught"),
    ("chase",   "nani",     "अरे-अरे! इतनी रात को ये क्या हो रहा है?", "Hey, hey! What's going on so late at night?", 1.6, "nanicomes"),
    ("chase",   "pinky",    "नानी, छत वाला भूत चमेली निकली! वो रोज़ रात मेरी पायल पहनकर नाचती थी!", "Nani, the roof ghost was Chameli! Every night she wore my anklets and danced!", 0.5, "explain"),
    ("chase",   "nani",     "बेचारी! घंटी टूटने के बाद उसे पायल की आवाज़ अच्छी लगने लगी होगी।", "Poor thing! After her bell broke, she must have loved the sound of the anklets.", 0.5, "poor"),
    ("mela",    "narrator", "अगली शाम गाँव का मेला रंग-बिरंगी रोशनी से जगमगा रहा था।", "The next evening, the village fair sparkled with colourful lights.", 2.4, "n_mela"),
    ("mela",    "narrator", "पिंकी ने पायल पहनकर स्टेज पर सबसे सुंदर नाच दिखाया।", "Pinky wore her anklets and danced the most beautiful dance on stage.", 0.5, "n_dance"),
    ("mela",    "narrator", "और चमेली? नानी ने उसके गले में एक नई चमकदार घंटी बाँध दी थी।", "And Chameli? Nani had tied a shiny new bell around her neck.", 2.0, "n_bell"),
    ("mela",    "chameli",  "", "Meh-meh!", 0.4, "bleat3"),
    ("mela",    "tinku",    "देखो! चमेली भी पिंकी के साथ नाच रही है!", "Look! Chameli is dancing with Pinky too!", 0.5, "dance2"),
    ("mela",    "pinky",    "मेरी पायल और चमेली की घंटी! हम दोनों की जोड़ी सुपरहिट!", "My anklets and Chameli's bell! We're a superhit pair!", 0.6, "superhit"),
    ("mela",    "narrator", "उस रात नानी के गाँव में कोई भूत नहीं था… बस खूब सारी हँसी, और ढेर सारा प्यार।", "That night there was no ghost in Nani's village... just lots of laughter, and lots of love.", 1.4, "n_end"),
    ("mela",    "tinku",    "अगली बार देखना — गोलू और सब्ज़ियों की ज़बरदस्त दौड़!", "Next time: Golu's crazy race with the vegetables!", 1.0, "next"),
    ("mela",    "pinky",    "बाय-बाय दोस्तों!", "Bye-bye, friends!", 0.5, "bye1"),
    ("mela",    "tinku",    "बाय-बाय!", "Bye-bye!", 0.3, "bye2"),
]

NAMES = {"narrator": ("कहानी", "#5a6abf"), "tinku": ("टिंकू", "#f08a00"), "pinky": ("पिंकी", "#e8327f"), "nani": ("नानी", "#8a3a8a"), "chameli": ("चमेली", "#7a6a4a")}
