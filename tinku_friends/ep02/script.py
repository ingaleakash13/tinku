# Tinku & Friends — story: पार्क का भूत / The Park Ghost   (Hindi dialogue, English captions · spooky-funny)
# Original story. LINES = (scene, speaker, hindi, english_caption, pause_before_seconds, cue)
# scenes: dusk (park at sunset) · night (dark park, moon, fireflies) · reveal (torch-lit, Moti under the sheet) · home (park gate, streetlight)

STORY_HI = "पार्क का भूत"
STORY_EN = "The Park Ghost"
LANG = "hi"
NEXT_EN = "Golu's Giant Sneeze"
NEXT = f"Next: {NEXT_EN}!"

LINES = [
    ("dusk",   "golu",  "पकड़ो! पकड़ो गेंद!", "Catch! Catch the ball!", 0.9, "catch"),
    ("dusk",   "tinku", "पकड़ ली! अब मेरी बारी!", "Got it! My turn now!", 0.5, "gotit"),
    ("dusk",   "golu",  "ऊँचा फेंको, तिंकू भैया! और ऊँचा!", "Throw it high, Tinku bhaiya! Higher!", 0.5, "higher"),
    ("dusk",   "pinky", "देखो! आसमान में पहला तारा निकल आया!", "Look! The first star is out in the sky!", 1.2, "star"),
    ("dusk",   "golu",  "वो तारा मुझे देखकर टिमटिमा रहा है!", "That star is twinkling at me!", 0.4, "twinkle"),
    ("dusk",   "pinky", "सूरज डूब रहा है। जल्दी अँधेरा हो जाएगा।", "The sun is setting. It'll be dark soon.", 0.6, "sunset"),
    ("dusk",   "tinku", "बस पाँच मिनट और खेलते हैं!", "Just five more minutes!", 0.4, "five"),
    ("dusk",   "moti",  "", "Woof! Woof!", 0.5, "bark1"),
    ("dusk",   "pinky", "मोती! गेंद लेकर कहाँ भाग रहे हो?", "Moti! Where are you running with the ball?", 0.5, "moti_runs"),
    ("night",  "tinku", "मोती! मोती! कहाँ हो?", "Moti! Moti! Where are you?", 2.2, "call"),
    ("night",  "golu",  "तिंकू भैया… अब तो बहुत अँधेरा हो गया। मुझे डर लग रहा है।", "Tinku bhaiya... it's so dark now. I'm scared.", 0.8, "dark"),
    ("night",  "tinku", "डरो मत, गोलू। मैं हूँ ना!", "Don't be scared, Golu. I'm right here!", 0.5, "brave"),
    ("night",  "golu",  "वो… वो कौन बोला? हू-हू?", "Wh-who said that? Hoo-hoo?", 1.8, "hoo"),
    ("night",  "tinku", "वो तो उल्लू है! उल्लू रात में जागता है और दिन में सोता है।", "That's an owl! Owls stay awake at night and sleep in the day.", 0.5, "owl"),
    ("night",  "pinky", "श्श्श! उस झाड़ी में कुछ हिला!", "Shhh! Something moved in that bush!", 1.2, "rustle"),
    ("night",  "pinky", "भू… भू… भूत!", "G-g-ghost!", 2.6, "ghost"),
    ("night",  "golu",  "बचाओ! भूत!", "Help! A ghost!", 0.2, "help"),
    ("hide",   "golu",  "भैया, भूत हमें खा जाएगा!", "Bhaiya, the ghost will eat us!", 1.4, "eat"),
    ("hide",   "pinky", "वो हमारी तरफ़ ही आ रहा है!", "It's coming this way!", 0.5, "coming"),
    ("hide",   "tinku", "रुको… इस भूत के तो चार पैर हैं!", "Wait... this ghost has four legs!", 1.2, "legs"),
    ("hide",   "pinky", "और… इसकी पूँछ भी हिल रही है!", "And... its tail is wagging!", 0.5, "tail"),
    ("hide",   "golu",  "भूत की पूँछ? भूतों की पूँछ होती है क्या?", "A ghost with a tail? Do ghosts have tails?", 0.4, "ghosttail"),
    ("hide",   "tinku", "चलो, टॉर्च जलाकर देखते हैं।", "Come on, let's look with the torch.", 0.6, "torch"),
    ("reveal", "golu",  "अरे! ये तो मोती है!", "Hey! It's Moti!", 2.4, "itsmoti"),
    ("reveal", "moti",  "", "Woof! Woof! Woof!", 0.3, "bark2"),
    ("reveal", "pinky", "शर्मा आंटी की चादर हवा में उड़कर मोती पर गिर गई थी!", "Sharma aunty's bedsheet blew off and fell on Moti!", 0.6, "sheet"),
    ("reveal", "golu",  "हा हा हा! मोती भूत! मोती भूत!", "Ha ha ha! Moti the ghost! Moti the ghost!", 0.4, "laugh"),
    ("reveal", "tinku", "बेचारा मोती! चादर में फँसकर खुद भी डर गया था।", "Poor Moti! He got stuck in the sheet and got scared too.", 0.6, "poor"),
    ("reveal", "tinku", "चलो, चादर वापस रस्सी पर टाँग देते हैं।", "Let's hang the sheet back on the line.", 0.7, "hang"),
    ("reveal", "golu",  "मैं टाँगूँगा! मैं! मैं!", "I'll hang it! Me! Me!", 0.4, "mehang"),
    ("reveal", "pinky", "अरे गोलू! अब तुम भूत बन गए!", "Oh Golu! Now YOU are the ghost!", 2.0, "golughost"),
    ("reveal", "golu",  "बू! मैं गोलू भूत हूँ!", "Boo! I'm Golu the ghost!", 0.4, "boo"),
    ("home",   "pinky", "चलो, अब सीधे घर! मम्मी इंतज़ार कर रही होंगी।", "Now straight home! Mummy must be waiting.", 2.0, "home"),
    ("home",   "golu",  "पर पहले… मोती को एक बड़ी सी झप्पी!", "But first... a big hug for Moti!", 0.5, "hug"),
    ("home",   "moti",  "", "Woof!", 0.4, "bark3"),
    ("home",   "tinku", "अगली बार देखना — गोलू की इतनी बड़ी छींक, कि सब कुछ उड़ जाएगा!", "Next time: Golu's sneeze so giant, everything flies away!", 1.2, "next"),
    ("home",   "pinky", "बाय-बाय दोस्तों!", "Bye-bye, friends!", 0.5, "bye1"),
    ("home",   "golu",  "बाय-बाय!", "Bye-bye!", 0.3, "bye2"),
]

NAMES = {"tinku": ("टिंकू", "#f08a00"), "pinky": ("पिंकी", "#e8327f"), "golu": ("गोलू", "#2fa84a"), "moti": ("मोती", "#a8673a")}
