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

# Tinku & Friends (टिंकू और दोस्त) — kids learning series

Short animated learning videos for babies, Nursery, LKG, UKG and Classes 1–5. Published every **Monday and Wednesday at 5 PM IST** (ep 1: Wed 18 Nov 2026),
Unlisted, made for kids, via Metricool. Code: `tinku_friends/epNN/` (episode 1 = reference). Shared character/scenery code is in
`mahabharat/lib/` (`tinku()`, `pinky()`, `golu()`, `moti()`, `park_bg()`, …). Friends sheet: `tinku_friends/friends_sheet.png`.

## Rules
- **Cast:** Tinku (7, glasses, yellow tee), Pinky (6, pigtails, pink frock), Golu (4, chubby, green dungarees), Moti (puppy, barks only).
  Do not redesign them. New props/backgrounds in the same bright style.
- **No introductions** ("I'm Tinku…"): title card, then straight into the topic. End with a one-line teaser of the next episode,
  "Bye-bye!" and the outro card. No moral/conclusion summary.
- **Length 2:00–3:00** (check after TTS; add repetitions, examples or a sing-along recap to reach 2:00; trim to stay under 3:00).
- **Levels:** follow the topic plan, which mixes little-ones topics (babies–UKG) and Classes 1–5 topics. Each episode's teaser must name the NEXT topic in the plan.
- **Language:** English for English/maths/science/GK topics (English captions); Hindi for Hindi-language topics (Hindi captions
  + English helper words). Voices from `FRIENDS_VOICES` in `mahabharat/lib/voices.py`, recorded in one breath, inner pauses tightened.
- **Teaching style:** big clear visuals that pop exactly when the word is spoken, repetition (a friend echoes the key word),
  colourful numbered/lettered cards, kid-pace speech (speed ≈ 0.85), cheerful ukulele bed, pop/boing/shimmer SFX.
- **Original content only:** write your own rhymes/chants; never reproduce copyrighted songs (traditional public-domain nursery
  rhymes are fine, but prefer originals).

## Topic plan (continue in order; skip any already in episodes/tinku_friends)
1 Let's Count 1 to 10 (done) · 2 Colors of the Rainbow (ep 1's teaser promises this) · 3 Times table of 2 · 4 Parts of a Plant · 5 Shapes Around Us ·
6 Hindi Varnamala: स्वर (अ–अः) · 7 Animals and Their Sounds · 8 Our Solar System · 9 ABC: A to M · 10 Times table of 3 ·
11 ABC: N to Z · 12 The Water Cycle · 13 Fruits We Love · 14 Hindi व्यंजन (क–ञ) · 15 Vegetables · 16 Nouns: Naming Words ·
17 Big and Small (opposites) · 18 Parts of Our Body & Five Senses · 19 Counting 11 to 20 · 20 Times table of 4 · 21 Brush Your Teeth! ·
22 Days of the Week & Months · 23 Vehicles on the Road · 24 Hindi व्यंजन (ट–म) · 25 Wild and Pet Animals · 26 Addition up to 10 ·
27 Good Manners: Please, Sorry, Thank You · 28 Seasons of India · 29 Birds Around Us · 30 Times table of 5 · 31 Fruits & Colors Match ·
32 Hindi मात्राएँ (ा ि ी) · 33 Up and Down, In and Out · 34 Healthy Food · 35 Community Helpers · 36 Subtraction up to 10 ·
37 Bedtime Routine · 38 Our National Symbols · 39 Insects & Bugs · 40 Times table of 10
