# Tinku ki Mahabharat — Episode 1: राजा शांतनु और गंगा (King Shantanu and Ganga)
# Original retelling written from the traditional epic.
# (scene, speaker, hindi, english_caption, pause_before, cue)

EP_NUM = 1
EP_TITLE_HI = "राजा शांतनु और गंगा"
EP_TITLE_EN = "King Shantanu and Ganga"

LINES = [
    ("title", "tinku", "नमस्ते दोस्तों! टिंकू की महाभारत में आपका स्वागत है!", "Hello friends! Welcome to Tinku's Mahabharat!", 1.6, "title"),

    ("room", "tinku", "मैं हूँ टिंकू! और आज से हम सुनेंगे, दुनिया की सबसे बड़ी कहानी. महाभारत!", "I'm Tinku! And from today, we'll hear the biggest story in the world: the Mahabharat!", 1.6, "room_wave"),
    ("room", "tinku", "इसमें राजा हैं, रानियाँ हैं, वीर योद्धा हैं, और बहुत सारी अच्छी सीख भी!", "It has kings, queens, brave warriors, and lots of good lessons too!", 0.5, "icons"),
    ("room", "tinku", "तो चलिए, कहानी की किताब खोलते हैं!", "So come on, let's open the storybook!", 0.5, "book_open"),

    ("palace", "tinku", "बहुत समय पहले, हस्तिनापुर नाम का एक सुंदर नगर था.", "Long, long ago, there was a beautiful city called Hastinapur.", 2.0, "palace"),
    ("palace", "tinku", "वहाँ के राजा थे, राजा शांतनु. वो बहुत दयालु और न्यायप्रिय थे.", "Its king was King Shantanu. He was very kind and fair.", 0.5, "shantanu_in"),
    ("palace", "shantanu", "मेरी प्रजा खुश रहे, यही मेरा सबसे बड़ा सुख है.", "My people's happiness is my greatest joy.", 0.4, "shantanu_talk"),

    ("river", "tinku", "एक दिन, राजा शांतनु गंगा नदी के किनारे घूमने गए.", "One day, King Shantanu went for a walk by the river Ganga.", 1.4, "to_river"),
    ("river", "tinku", "तभी, पानी में से एक तेज़ रोशनी निकली!", "Suddenly, a bright light rose from the water!", 0.5, "glow"),
    ("river", "tinku", "और नदी से बाहर आईं, एक बहुत सुंदर देवी.", "And out of the river came a very beautiful goddess.", 0.4, "ganga_rise"),
    ("river", "shantanu", "आप कौन हैं, देवी? मैंने ऐसा तेज कभी नहीं देखा.", "Who are you, goddess? I have never seen such radiance.", 0.8, "sh_ask"),
    ("river", "ganga", "मैं गंगा हूँ, राजन. इसी नदी की देवी.", "I am Ganga, O king. The goddess of this very river.", 0.4, "ga_intro"),
    ("river", "shantanu", "क्या आप हस्तिनापुर की महारानी बनेंगी?", "Will you become the queen of Hastinapur?", 0.5, "propose"),
    ("river", "ganga", "बनूँगी. पर मेरी एक शर्त है.", "I will. But I have one condition.", 0.5, "condition"),
    ("river", "ganga", "मैं जो भी करूँ, आप मुझसे कभी कोई प्रश्न नहीं पूछेंगे, और मुझे कभी नहीं रोकेंगे.", "Whatever I do, you will never question me, and never stop me.", 0.3, "condition2"),
    ("river", "ganga", "जिस दिन आपने मुझे रोका, उसी दिन मैं चली जाऊँगी.", "The day you stop me, that very day I will leave.", 0.3, "condition3"),
    ("river", "shantanu", "मैं वचन देता हूँ, देवी. मैं आपको कभी नहीं रोकूँगा.", "I give you my word, goddess. I will never stop you.", 0.5, "promise"),

    ("wedding", "tinku", "और फिर, बड़ी धूमधाम से, राजा शांतनु और गंगा का विवाह हुआ!", "And then, with a grand celebration, King Shantanu and Ganga were married!", 1.4, "wedding"),
    ("wedding", "tinku", "कुछ समय बाद, उनके घर एक नन्हा बालक आया.", "Some time later, a little baby boy was born to them.", 1.2, "baby1"),

    ("stars", "tinku", "पर गंगा, उस बालक को लेकर नदी के पास गईं.", "But Ganga took the baby to the river.", 1.2, "river_baby"),
    ("stars", "tinku", "और वो बालक, एक चमकते तारे की तरह, आसमान में चला गया!", "And the baby rose into the sky, like a shining star!", 0.4, "star1"),
    ("stars", "tinku", "राजा शांतनु हैरान थे. पर उन्होंने वचन दिया था, इसलिए वो चुप रहे.", "King Shantanu was shocked. But he had given his word, so he stayed silent.", 0.6, "sad"),
    ("stars", "tinku", "ऐसा एक बार नहीं, सात बार हुआ. एक, दो, तीन, चार, पाँच, छह, सात!", "This happened not once, but seven times. One, two, three, four, five, six, seven!", 0.6, "seven"),
    ("stars", "tinku", "दोस्तों, क्या आप जानते हैं, वो बालक कौन थे?", "Friends, do you know who those babies were?", 1.0, "ask"),
    ("stars", "tinku", "वो वसु थे, स्वर्ग के देवता! एक श्राप की वजह से, उन्हें धरती पर जन्म लेना पड़ा था.", "They were the Vasus, gods of heaven! Because of a curse, they had to be born on earth.", 1.0, "vasus"),
    ("stars", "tinku", "माँ गंगा, उन्हें श्राप से मुक्त करके, वापस स्वर्ग भेज रही थीं.", "Mother Ganga was freeing them from the curse and sending them back to heaven.", 0.4, "free"),

    ("eighth", "tinku", "फिर आया आठवाँ बालक. और गंगा, फिर से नदी की ओर चलीं.", "Then came the eighth baby. And Ganga walked towards the river once again.", 1.4, "baby8"),
    ("eighth", "shantanu", "रुको, गंगा! इस बार मैं चुप नहीं रहूँगा! यह बालक मुझे दे दो!", "Stop, Ganga! This time I won't stay silent! Give this child to me!", 0.4, "stop"),
    ("eighth", "ganga", "राजन, आपने अपना वचन तोड़ दिया.", "O king, you have broken your promise.", 0.8, "broken"),
    ("eighth", "ganga", "यह आठवाँ वसु है. इसे धरती पर, लंबा जीवन जीना है.", "This is the eighth Vasu. He must live a long life on earth.", 0.4, "eighth_vasu"),
    ("eighth", "ganga", "अब मुझे जाना होगा. पर मैं इसे बड़ा करके, आपको वापस लौटाऊँगी.", "Now I must go. But I will raise him, and bring him back to you.", 0.4, "must_go"),
    ("eighth", "shantanu", "गंगा... मेरा पुत्र... मैं इंतज़ार करूँगा.", "Ganga... my son... I will wait.", 0.6, "wait"),
    ("eighth", "tinku", "और माँ गंगा, नन्हे बालक के साथ, नदी में समा गईं.", "And Mother Ganga, with the little baby, vanished into the river.", 0.6, "ganga_leave"),

    ("room2", "tinku", "अगली बार देखिए, वो नन्हा बालक बड़ा होकर क्या बना! एक महान योद्धा!", "Next time, see what that little baby grew up to be! A great warrior!", 2.2, "next"),
    ("room2", "tinku", "तब तक के लिए, नमस्ते दोस्तों! फिर मिलेंगे!", "Until then, goodbye friends! See you again!", 0.8, "bye"),
]

VOICES = {
    # kokoro voice, speed, pitch (F0) factor, formant factor  — reshaped with WORLD, speed unchanged
    "tinku": ("hf_beta", 1.0, 1.65, 1.15),     # cute young boy
    "shantanu": ("hm_omega", 0.9, 0.9, 0.96),  # deeper, regal
    "ganga": ("hf_alpha", 0.95, 1.0, 1.0),      # natural, gentle
}
NAMES = {"tinku": ("टिंकू", "#f08a00"), "shantanu": ("राजा शांतनु", "#1d8a8a"), "ganga": ("माँ गंगा", "#2f8fd8")}
