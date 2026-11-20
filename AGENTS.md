# टिंकू की महाभारत (Tinku's Mahabharat) — episode pipeline

A 45-episode animated kids series, one episode every Friday at 5 PM IST, published Unlisted on YouTube via Metricool.
(The older Mia & Benny pipeline in `pipeline/` is retired.)

## Non-negotiable rules
- **Source:** write every episode fresh from the traditional epic (Vyasa's Mahabharata and its public retellings), in our own words.
  Never use or adapt the script, dialogue or scene order of any TV show or film (e.g. the 2013 Star Plus "Mahabharat"),
  and never copy actors' likenesses or a show's costume designs.
- **Language:** all dialogue in Hindi; on-screen captions in English (with the speaker's name tag in Hindi).
- **Host:** Tinku (a cute boy with glasses, fluffy brown hair, yellow T-shirt, jeans) opens in his room, opens the storybook,
  narrates the story scenes (shown as a small talking circle top-left while he narrates), and returns at the end.
- **Ending:** NO conclusion / "what did we learn" / moral summary. End with Tinku teasing what happens next episode, then
  "तब तक के लिए, नमस्ते दोस्तों! फिर मिलेंगे!" and the outro card ("फिर मिलेंगे!" / "See you next time!" / next-episode title).
- **Characters** speak their own lines in the story. Every character has their own distinct voice from `mahabharat/lib/voices.py`
  (VOICE_CAST). Add new characters to VOICE_CAST with a voice distinct from others in the same scene.
- **Look:** approved designs are in `mahabharat/lib/chars.py` (`tinku()`, `hero(key, …)`; sheet: `mahabharat/character_sheet.png`).
  Do not redesign approved characters. New characters: add a CAST entry in the same style (bright 2D cartoon, men with short
  neat neck-length hair, women graceful with almond eyes, jewelry; queens wear a queen crown). Bhishma uses the one `bheeshm` design throughout.
- **Kid-friendly:** gentle handling of sad or violent moments (e.g. the Vasus rise as stars; battles shown as courage, never gore).
- **Motion:** arms are two-part with elbows: pass poses as `((shoulder, elbow), (shoulder, elbow))`; use `talk(spk, t)` for natural
  speaking gestures; walking bob, blinking, lip-sync from voice loudness.
- **Scenes:** use the rich backgrounds in `mahabharat/lib/scenery.py` (`palace_scene_bg`, `river_bank_scene(dusk)`, `mandap_scene_bg`,
  `room_bg`, `palace()`, `banyan()`, `mountains()`, `grass_field()`, …). Add new backgrounds there in the same detailed style
  (gradients, layered depth, lighting, small animated life such as birds, flags, water shimmer, fireflies).
- **Length:** whatever the story part needs, usually 2:30–5:00.

## How to make episode N
1. `WORK=/home/claude/work bash pipeline/setup.sh` (fonts, cairo, Kokoro Hindi voices, pyworld, ffmpeg).
2. Copy the latest `mahabharat/epNN/` to `mahabharat/epMM/` (MM = next number, two digits); symlink `tts -> /home/claude/work/tts`.
3. Write `script.py`: EP_NUM, EP_TITLE_HI, EP_TITLE_EN, LINES = (scene, speaker, hindi, english, pause, cue), NAMES (Hindi name, colour).
   Use VOICE_CAST from lib/voices.py in `tts.py` (import it) instead of a local VOICES dict.
4. `python3 tts.py` → audio lines + timeline.json. Check: no silence > 0.35 s inside a line; Tinku's median F0 ≈ 280–300 Hz.
5. Update `cues.py` scene list, `audio.py` (tanpura drone + bansuri in pauses + tabla only in festive scenes + scene SFX), and
   `draw.py` scene functions and staging for the new story.
6. Render stills at the busiest moments (`python3 draw.py t1 t2 …`), LOOK at them, fix overlaps/props/text before the full render.
7. Full render: `render.py` in ~10 chunks, 2 in parallel; concat with `-c copy`; mux `audio/mix.wav` (AAC 192k, faststart).
   Sample 8 frames from the final mp4 and check them.
8. Save `episodes/mahabharat/epMM_<slug>.mp4` + `.en.srt`, commit with the code, push to main.
9. Publish with Metricool (blogId 8170191, Asia/Calcutta) on Friday at 17:00 (or ~10 minutes from now if 17:00 has passed):
   youtube, privacy "unlisted", madeForKids true, isAiGeneratedContent true, category "EDUCATION",
   title "टिंकू की महाभारत | एपिसोड N: <Hindi title> | <English title> 🏹", Hindi+English description, 10 tags, hashtags
   (#TinkuKiMahabharat #Mahabharat #KidsStories #HindiKahani #MahabharatForKids …). Media = raw.githubusercontent.com link.
   ALSO post the same full episode to Instagram at the same time as a SEPARATE post: provider instagram, instagramData
   {type "REEL", showReelOnFeed true, isAiGenerated true}, same media; caption = curiosity hook line (1–2 emojis), Hindi+English
   keyword lines with the episode title, "📖 A new episode every Friday at 5 PM!", next episode title, CTA
   "Follow @iamtinku13 for the next episode 💛 | Share with a friend 👫 | Comment your favourite part 👇", 6–8 hashtags
   (#TinkuKiMahabharat #Mahabharat #MahabharatForKids #HindiKahani #KidsStories #IndianMythology #KidsCartoon #Reels).

## 45-episode plan (from the epic)
1 राजा शांतनु और गंगा (done) · 2 देवव्रत की वापसी · 3 भीष्म प्रतिज्ञा · 4 सत्यवती के पुत्र · 5 अंबा, अंबिका, अंबालिका ·
6 धृतराष्ट्र, पांडु और विदुर का जन्म · 7 गांधारी और कुंती · 8 पांडु बने राजा · 9 पांडवों का जन्म · 10 पांडु की विदाई ·
11 हस्तिनापुर वापसी · 12 भीम और दुर्योधन · 13 गुरु द्रोण · 14 अर्जुन और चिड़िया की आँख · 15 एकलव्य की गुरुभक्ति ·
16 रंगभूमि और कर्ण · 17 लाक्षागृह · 18 जंगल में बचाव · 19 भीम और हिडिंबा · 20 द्रौपदी स्वयंवर · 21 पाँच भाई, एक वचन ·
22 इंद्रप्रस्थ का निर्माण · 23 कृष्ण और अर्जुन की मित्रता · 24 राजसूय यज्ञ · 25 दुर्योधन की जलन · 26 शकुनि की चाल ·
27 द्यूत क्रीड़ा · 28 कृष्ण ने की द्रौपदी की रक्षा · 29 बारह वर्ष का वनवास · 30 यक्ष के प्रश्न · 31 अज्ञातवास ·
32 बृहन्नला बने अर्जुन · 33 शांतिदूत कृष्ण · 34 कर्ण को सच का पता · 35 कुंती और कर्ण · 36 कौन किसके साथ ·
37 गीता का उपदेश (भाग 1) · 38 गीता: कर्म करो (भाग 2) · 39 बाणों की शय्या पर भीष्म · 40 वीर अभिमन्यु · 41 दानवीर कर्ण ·
42 कर्ण और अर्जुन · 43 भीम और दुर्योधन · 44 फिर से शांति · 45 महाभारत की कहानी पूरी हुई

---

# Tinku & Friends (टिंकू और दोस्त) — kids STORIES

Standalone animated stories for kids (babies–Class 5): scary-but-safe, funny, learning, friendship, feelings, adventure,
mystery, festivals. EVERY video is a NEW, complete story — no "Episode N" anywhere (not on screen, not in titles).
Published every **Wednesday 17:00, Friday 18:00, Saturday 17:00 and Sunday 09:00 IST** via Metricool (blogId 8170191, Asia/Calcutta)
(Friday is 18:00 so it doesn't clash with Tinku ki Mahabharat at 17:00):
  1. the full story video → YouTube (type "video", PUBLIC, madeForKids, isAiGeneratedContent, category EDUCATION or FILM_ANIMATION);
  2. a 30-second vertical cut → ONE post with providers youtube (type "short") + instagram (type "REEL", isAiGenerated true).
Code: `tinku_friends/epNN/` (NN = running number for folders/files only; ep02 = reference story pipeline). Shared character/scenery
code is in `mahabharat/lib/` (`tinku()`, `pinky()`, `golu()`, `moti()`, `park_bg()`, …). Friends sheet: `tinku_friends/friends_sheet.png`.
(Earlier experiments: `tinku_friends/archive_colors_song/` = sung song version, `tinku_friends/3d_test/` = 3D test — owner chose
normal 2D characters and normal speaking voices; do not use singing, 3D or Kling.)

## Rules
- **Cast:** Tinku (7, glasses, yellow tee), Pinky (6, pigtails, pink frock), Golu (4, chubby, green dungarees), Moti (puppy, barks only).
  Do not redesign them (2D, normal). NOT every video needs every character: use only who the story needs — a solo moment,
  two friends, Moti alone, or one kid telling a funny joke/riddle to the camera are all fine. Vary it. New props/backgrounds/side characters in the same bright 2D style.
- **Start immediately:** NO title card, NO episode name, NO introductions at the start — the first frame is already the story.
- **No brand text in the video:** never show or say "Tinku & Friends" anywhere in the video or the Short/Reel (no badge, no title,
  no outro brand). Character names in captions are fine. End with a one-line teaser naming the NEXT story in the plan, "Bye-bye!" and the
  outro card ("Bye-bye!" / "See you next time!" / "Next: <next story title>"). No moral/conclusion summary.
- **Voices:** normal SPEAKING voices (never singing), one character per line, from `FRIENDS_VOICES` in `mahabharat/lib/voices.py`;
  recorded in one breath, inner pauses tightened; auto-match F0 targets (Tinku ~285 Hz, Pinky ~310, Golu ~350).
- **Language:** mixed by story — the plan marks each story (H) Hindi dialogue + English captions, or (E) English.
- **Kid-safe scary:** spooky = shadows, sounds, a "ghost" that turns out to be something funny; never gore, never real danger left unresolved.
- **Look & motion:** dancing/bouncing is fine in happy moments; talk gestures, blinking, lip-sync from voice loudness; camera moves
  (push-in, small shake on scary stings), circle-wipe between scenes, mood music (playful ukulele, spooky drone + pizzicato,
  comic boing reveal), SFX.
- **Length:** full story 2:00–3:00 (a quick joke/riddle video may be 0:45–1:30); Short/Reel exactly ≤30 s (`short.py T0 T1 out.mp4`, 1080×1920, NO on-screen captions — the full video keeps its captions).
- **Original content only:** our own stories and dialogue; never adapt TV shows/films/books.
- **Calendar events (owner's rule):** every publish day, first check this calendar. If an event falls ON the publish day or
  BEFORE the next publish day (i.e. it would otherwise be missed), make an ORIGINAL kid-friendly story themed on that event
  (add it to the plan as "(event)"). If several events qualify, pick the bigger one. If there is NO event, make the next story
  from the plan (or a fresh random original story — any genre — when the plan runs out). Re-check lunar-festival dates
  (marked ~) with a quick web search before using them; they can shift by a day.
  Kid-friendly framing: Valentine's Week / Valentine's Day = love for friends, family and pets (cards, kindness, sharing — no
  romance); Halloween = costume party and pumpkins, scary-but-funny; Men's/Women's/Mother's/Father's Day = celebrating dads,
  moms, grandparents, helpers; national days = pride, flag, parade, songs (no politics).

  | Date | Event | | Date | Event |
  |---|---|---|---|---|
  | 25 Dec | Christmas | | 1 Jan | New Year |
  | 13 Jan | Lohri | | 14/15 Jan (2027: Fri 15) | Makar Sankranti / Pongal / kite day |
  | 26 Jan | Republic Day (India) | | ~11 Feb 2027 | Vasant Panchami |
  | 7–14 Feb | Valentine's Week (Rose 7, Chocolate 9, Teddy 10, Promise 11, Hug 12) | | 14 Feb | Valentine's Day |
  | ~6 Mar 2027 | Maha Shivratri | | 8 Mar | International Women's Day |
  | ~9 Mar 2027 | Eid al-Fitr | | ~22 Mar 2027 (Holika Dahan 21) | Holi |
  | ~28 Mar 2027 | Easter | | 1 Apr | April Fools' Day |
  | ~7 Apr 2027 | Gudi Padwa / Ugadi | | 14 Apr | Baisakhi / Ambedkar Jayanti |
  | ~15 Apr 2027 | Ram Navami | | 22 Apr | Earth Day |
  | 2nd Sun May (2027: 9 May) | Mother's Day | | ~17 May 2027 | Eid al-Adha |
  | ~20 May 2027 | Buddha Purnima | | 5 Jun | World Environment Day |
  | 3rd Sun Jun (2027: 20 Jun) | Father's Day | | 21 Jun | International Yoga Day |
  | 1st Sun Aug (2027: 1 Aug) | Friendship Day | | 15 Aug | Independence Day (India) |
  | ~17 Aug 2027 | Raksha Bandhan | | ~25 Aug 2027 | Janmashtami |
  | 5 Sep | Teachers' Day | | ~4 Sep 2027 | Ganesh Chaturthi |
  | ~12 Sep 2027 | Onam | | ~30 Sep 2027 | Navratri begins |
  | 2 Oct | Gandhi Jayanti | | ~9 Oct 2027 | Dussehra |
  | 31 Oct | Halloween | | ~29 Oct 2027 (Dhanteras 27, Bhai Dooj 31) | Diwali |
  | ~4 Nov 2027 | Chhath | | 14 Nov | Children's Day |
  | ~13 Nov 2027 | Guru Nanak Jayanti | | 19 Nov | International Men's Day |

## SEO for titles, captions & hashtags (YouTube + Instagram) — owner wants maximum views
- **Keyword first.** Titles start with what parents/kids search for, in the story's language AND Hinglish/English:
  e.g. "Bhoot Wali Kahani 👻 पार्क का भूत | Funny Ghost Story for Kids in Hindi". Do NOT add "| Tinku & Friends" to titles
  (use the space for search words). Keep YouTube titles ≤ 70 chars where
  possible (put the most important words in the first 40), one or two emojis, no clickbait lies.
- **Hook = curiosity, no spoilers.** Shorts/Reels titles and the first caption line are a question or cliff-hanger
  ("A GHOST in the park?! 👻 Wait… why does it have a TAIL? 🐶").
- **YouTube description:** line 1–2 = hook + main keywords (these show in search); then a 2–3 line story summary with natural
  keywords (Hindi kahani, cartoon for kids, moral-free funny story, bedtime story, hindi cartoon, kids story in hindi/english,
  festival name for event stories); who it's for (age/classes); schedule line; next story; then 3 hashtags that appear above
  the title (#TinkuAndFriends + 2 topic tags) followed by 5–8 more (≤ 15 total — YouTube ignores all hashtags if there are more).
  Made-for-kids videos have comments off, so the call to action is "Share with a friend who loves stories! 🔔 Subscribe".
- **YouTube tags (10–15):** mix exact phrases in Hindi script, Hinglish and English (e.g. "bhoot wali kahani", "hindi kahani",
  "cartoon kahani", "kids story in hindi", "funny ghost story", "tinku and friends", "moral stories" is NOT used), plus the event
  name and year for festival stories (e.g. "diwali story for kids 2027").
- **Instagram Reel caption:** line 1 hook (with 1–2 emojis), line 2–3 keyword-rich description (Instagram search reads captions),
  CTA "Follow @iamtinku13 for new stories every Wed, Fri, Sat & Sun 💛 | Share with a friend 👫 | Comment your favourite part 👇",
  then 5–8 hashtags: 2 brand (#TinkuAndFriends #TinkuKiKahani), 3 niche (#HindiKahani #KidsStories #BhootKiKahani…),
  1–2 broad (#KidsCartoon #Reels), event hashtag for festival stories (#Diwali2027…). No banned/irrelevant tags.
- **Captions + hashtags are written fresh for EVERY video** at upload time (full video and Short/Reel each get their own).
- **Shorts:** title includes "#Shorts"; first 2 seconds of the Short must already show the hook (the cut starts mid-action).
- **Every post:** YouTube privacy PUBLIC (unlisted never shows in search/feeds), madeForKids true, isAiGeneratedContent/isAiGenerated true (honest labelling protects reach), category
  FILM_ANIMATION; publish at the scheduled slot (peak times: evenings, Sunday morning).

## Story plan (continue in order; skip any already in episodes/tinku_friends; add more original stories when it runs out)
1 Let's Count 1 to 10 (done, old learning format) · 2 पार्क का भूत / The Park Ghost (H, spooky-funny) · 3 Golu's Giant Sneeze (E, funny) ·
4 मोती खो गया / Moti Is Lost (H, friendship) · 5 Why Does the Moon Follow Us? (E, learning) · 6 आधी रात का राक्षस / The Midnight Fridge Monster (H, spooky-funny) ·
7 Pinky's Kite Contest (E, friendship) · 8 बारिश में बिल्ली / The Kitten in the Rain (H, kindness) · 9 Tinku's Fizzy Volcano (E, learning-funny) ·
10 फुसफुसाता पेड़ / The Whispering Tree (H, mystery) · 11 Golu Is Scared of the Dark (E, feelings) · 12 आम चोर / The Mango Thief (H, funny mystery) ·
13 The Robot Who Couldn't Dance (E, funny) · 14 दिवाली की लाइटें / The Diwali Lights Mix-up (H, festival) · 15 The Treasure Map (E, adventure) ·
16 मेरा लड्डू किसने खाया? / Who Ate My Ladoo? (H, funny) · 17 The Shy New Friend (E, friendship) · 18 दादाजी की जादुई टॉर्च / Grandpa's Magic Torch (H, spooky-learning) ·
19 The Seed That Grew Overnight (E, learning) · 20 मोती और मधुमक्खी / Moti and the Bee (H, funny) · 21 The Haunted School Bus (E, spooky-funny)
