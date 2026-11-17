# Mia & Benny — weekly episode pipeline

Original 2-minute animated kids episodes (ages 2–5). Mia is a cheerful girl (yellow dress, pink bows, hair puffs);
Benny is her lavender-white bunny best friend (blue bow tie). Bright 2D style, clear narration, word-highlighted captions.
Never use characters, songs, names or designs from existing shows (e.g. CoComelon) — everything must be original.

## Layout
- `episodes/` — finished videos (`epNN_<slug>.mp4`) and caption files (`.en.srt`). Raw GitHub links to these are what Metricool publishes from.
- `pipeline/setup.sh` — installs fonts, cairo, the Kokoro voice model, ffmpeg. Run first in a fresh workspace.
- `pipeline/ep01/` — the complete working code for episode 1, the reference for every new episode:
  - `script.py` — LINES: (scene, speaker, text, pause_before, cue) + VOICES (narrator af_heart, mia af_sky pitched ×1.13, benny am_puck pitched ×1.16).
  - `tts.py` — records each line, writes `audio/lines/NN.wav` and `timeline.json`.
  - `cues.py` — scene boundaries and action times derived from the timeline (shared by picture and sound).
  - `audio.py` — 112-bpm ukulele music bed (ducks under speech), sound effects (boing, pop, thunk, swish, shimmer, water…), mix → `audio/mix.wav`.
  - `draw.py` — cairo drawing: `mia()`, `benny()` characters (lip-sync from voice loudness, blinking, poses), scenery (sky, sun with face,
    clouds, hills, fence, house, tree, raised garden bed), title card, outro card, iris transitions, captions with speaker name tag and word highlight.
    The story-specific parts are `mia_state()`, `ben_state()`, `plants()`, `main_scene()` and the props.
  - `render.py` — renders frame ranges to mp4 segments (run several in parallel, then concat + mux audio).

## Making a new episode
Run `WORK=/home/claude/work bash pipeline/setup.sh`, then copy the latest `pipeline/epNN/*.py` into `$WORK` and work there
(the code expects `tts/` in the current directory). When done, also save the new code as `pipeline/epNN/` for the next episode.

Steps:
1. Write a new original story in `script.py`: ~45 lines, about 2 minutes of speech plus pauses, one simple learning goal
   (shapes, opposites, animal sounds, kindness, weather, sizes, sharing, bedtime, numbers 6–10…), a repeated chant, a call-and-response
   question to the viewer, a hug/goodbye and "Bye-bye, friends! See you next time!". Keep the title card and outro card.
2. `python3 tts.py`; check total length is 115–130 s; adjust pauses or lines if not.
3. Rewrite the story-specific animation in `cues.py` / `draw.py` (new props, new backdrop details, new actions) and the sound cues in `audio.py`.
   Reuse characters, scenery, captions, transitions and the music engine unchanged.
4. Render stills at the busiest moments (`python3 draw.py t1 t2 …` → `stills/`), look at them, fix overlaps (arms behind heads, props in wrong
   place, captions covering faces) BEFORE the full render.
5. Full render with `render.py` in 8 parallel-by-2 chunks, concat with `-c copy`, add `audio/mix.wav` (AAC 192k, `-movflags +faststart`).
6. Make the `.en.srt` from `timeline.json`. Sample 6 frames from the final mp4 and check them.
