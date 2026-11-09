---
name: split-animated-talking-head
description: Turn a user-supplied talking-head clip (webcam, phone selfie, or recorded speaker) plus an optional script or source URL into a 1080x1920 split-format vertical short. Custom-generated animations fill the top slot, the provided talking head sits in a taller rounded band across the bottom, kinetic captions sync to the clip's own voice, real product logos/screenshots appear whenever a named tool is spoken, real portraits of the notable figures behind any spoken niche (Claude/Anthropic, SpaceX, OpenAI, marketing, business, sales), Giphy reaction GIFs on punchlines, Apple-style counters on every number, and a hyper-edit layer (keyword punch-ins, hyperframe inserts, whip cuts, shake). No HeyGen. Use when the user provides a talking-head video, webcam recording, selfie clip, or asks for the split animated format using their footage instead of a Megan/Danny/Kevin avatar. Not for avatar-narrated shorts (use split-animated-short) or 16:9 long-form edits (use longform-animated-talking-head).
---

# Split Animated Short: user talking head (taller live band)

## Critical (Kevin locks; full dated context in `references/learnings.md`)

Output and band
- **Final video is 1080x1920. Never 720x1280** (Kevin 2026-09-03). Never scale the talking head below 1056x960. If ffprobe on `renders/final.mp4` is not `1080x1920`, delete it and start over.
- Band is **1056x960 at y=936**, all four corners rounded r=60, 12px side margins, ~24px of canvas under it (Kevin 2026-09-15: y=960 clipped the chin). Never `BAND_H+60`.
- **The talking head never moves** (Kevin 2026-09-05): band composited at a fixed `(12, BAND_Y)`. Punch-ins, shake and flashes go on the animation slot only.
- **No black strip above the head, no letterbox in the band** (Kevin 2026-09-12, 2026-09-18). Check band frames at 3 to 4 timestamps, top AND bottom rows.
- **Never mux `audio/narration.wav`** (16 kHz Whisper scratch; Kevin 2026-09-22 "why is the audio bad?"). Use `narration.m4a` or `-c:a copy` from the original clip. No trending/copyrighted sounds.
- No HeyGen. Never use this skill for Megan/Danny/Kevin avatars (`split-animated-short`).

Layout
- **Pack lock:** `AH=770`, `LAYER_Y=90`, `PACK_DY=210`, `BAND_Y=936`. Animations sit just above the captions, never hugging the top (Kevin 2026-09-03).
- Assets stay inside **x=36..1044**. Stream centers at most `770 - icon_size/2 - 10` after PACK_DY (half-sliced icons are a known fail).
- **Captions sit ON the accent line** (Kevin 2026-09-18/19): Luckiest Guy caps, white fill (KEY_COL on keywords), 7px black stroke, `anchor="ls"` at `y = BAND_Y - 18` so the stroke bottom rests on the line top, drawn after the band. Never over the head, never on the line, never floating. Caption glow is a tight halo (word height, alpha at most 40).
- **Type:** overlay text Oswald Bold (`AR`), captions Luckiest Guy (`CAP`), terminals Menlo (`ML`, `index=0`). Never Arial in the slot.
- **Colors:** lifted graphite wash (CHAR=(48,50,58), `slot_vignette(a=22)`); never near-black (14,15,18), never Megan paper/sage/coral (Kevin 2026-09-10).

Content and choreography
- **Density floor:** 6 to 10 live elements; at least 3 pieces at all times, one GIF or figure per section, something always moving (Kevin 2026-09-08/10).
- **Frame 0 is a packed billboard** (Kevin 2026-09-02/14): one or two giant faces / a huge number / a huge logo. No white flash or hyperframe on the hook. Figure circles of 150 to 220px are banned anywhere.
- **Beat `t0` = the spoken word**, max lead 0.1s. Never preview a product or number before it is said.
- **Named products get real logos/cards, never text pills.** Claude / Claude Code / Opus / Sonnet / Haiku / Fable / Anthropic always use the bundled invader + sphinx, never a favicon (Kevin 2026-09-03).
- **Named figures are mandatory** when the niche supports them (Kevin 2026-09-05).
- **Every spoken number gets an Apple counter** with full figures and live commas, never "2B" as the hero (Kevin 2026-09-05/29). Nothing sits on top of a counting counter.
- **Topic logo conveyor on every cut** (Kevin 2026-09-10); one moving stream per y-band at a time (Kevin 2026-09-05). No loose "$" filler icons.
- **Stacking:** max two big pieces (over 400px) live at once; exit the previous big card at most 0.1s before the next `t0` (Kevin 2026-09-05).
- **No synced pulse** (Kevin 2026-09-11): no bobbing, no yoyo/repeat scale pulses, no pulsing CTA (one slam + one highlight sweep, then still).
- **Variety; impact for drama only** (Kevin 2026-09-12): rotate entrances (`entrance(k)`), one GIF use per video, punch/shake/light_hit/hyperframe/slam only on each section's ONE dramatic beat. **Punch-ins are rare:** `punch_beats()`, one hero word per section, at least 8s apart, at most 6/min, amt 0.045.
- Whip **or** hyperframe on a cut, never both.
- **No HTML overlay layer** (Kevin 2026-10-02 "its actually bad"): everything is drawn in the PIL compositor.
- On-screen text: no em/en dashes, profanity censored on screen (`sh*t`), audio uncensored.
- Publish only on Kevin's go.

Picture rules (2026-10-08, from [Chase AI's Claude video](https://www.youtube.com/watch?v=rscb1DgJtNg); the band stays, these are about the slot):
- **Payoff hit lands in the pause.** If `words.json` has ≥0.35s of silence before the punchline word, that visual's `t0` is the start of the silence, not the word. A hit on the word gets swallowed by the voice. The 0.1s lead still applies when there is no pause.
- **No identical picture for ~7s.** A still card still dies at 2.5s. A screen recording or generated animation may hold for the whole spoken stretch only while the picture itself is changing (typing, scrolling, a slow push, two renders moving together with a sweep). The same frame twice is a failed beat.
- **The named thing is big and centered.** A tiny mark in the corner fails. Negation is a strike through the real logo or card, not a pill that says "no".
- **Square footage stays square.** Fit a 1:1 animation inside the slot and let the graphite wash fill the sides. Never stretch it to 1080 wide.
- **Markup on a recording lands on the spoken word** (highlight, number, arrow). One kinetic word may fill the slot and bleed off the edges, once per video. That word is the graphic.
- **Look at a contact sheet before encode.** A repeated still, a corner icon, or a buried hit is a re-render.

Same flagship format as `split-animated-short`, except the bottom band is the
**clip the user hands you**, not a HeyGen talking-photo. The clip's audio is
the master timeline. Animations are authored per script — zero pixels from any
*reference* reel except its words, if one is given.

Live talking-head footage needs **more band height than the HeyGen 45% lock**
so hats/hair aren't clipped (Kevin 2026-09-01). Band geometry is in `## Critical`.

**PACK LOCK (Kevin 2026-09-03, opensource-100 recut):** animations sit
**just above the captions**, not up against the top of the frame. A top-hugging
pack leaves a vacant band in the middle of the screen. Locked numbers:

```
AH = 770          # animation layer height
LAYER_Y = 90      # composite at (0, 90) → layer covers canvas y=90..860
PACK_DY = 210     # add to every place()/conveyor/orbit/ticker/ghost cy
CAP_Y = 867       # top of the caption zone (pack reference); the word itself is
                  # baseline at BAND_Y-18, anchor="ls", stroke on the line top (Kevin 2026-09-19)
BAND_Y = 936      # talking-head band (Kevin 2026-09-15: 960 was too low / clipped the bottom)
```

Layer ends ~7px above the captions. Pack numbers from
`projects/opensource-100-animated/render.py`. **Never** `LAYER_Y=42` +
`AH=840` with heroes at cy≈180–280 — that was the vacant-middle bug. Never
design at 853 and downscale, and never render the whole video at 720.

**Reference renders** (detail of what each did lives in `references/reference-edits.md`):
- **BEST EDIT YET (Kevin 2026-09-26):** `projects/social-agents-animated/render.py`, the top reference. User b-roll used three ways (banner reveal, zoomed live terminal, single-line repo crops), spoken feature lists as a ticking checklist with one bespoke visual per item, GIFs matched word for word to the line. Reuse its Broll / crop_img / strip_card / broll_view(zoom=) helpers whenever b-roll is supplied.
- **STATUS QUO (Kevin 2026-09-19, "SOOOOO GOOOOD that should be the new status quo"):** `projects/gitnexus-animated/render.py`. Match its energy on every cut.

**LOOK + TYPE LOCK (Kevin 2026-09-10, 2026-09-15, 2026-09-19).** Density /
titles / GIFs follow china-robots (render.py no longer on disk; use
social-agents / gitnexus as code refs). Slot brightness follows
`projects/github-research-agent-animated/render.py` (Kevin: "background
is too dark"): lifted graphite `textured_bg`, `slot_vignette(..., a=22)`.
Override these colors after exec of `animation_assets_and_beats.py`, and copy
`fonts.py` + both ttfs into every workdir:

```
INK=(10,11,14)  SILVER=(198,204,214)  STEEL=(92,98,108)
GRAPHITE=(36,38,46)  CHAR=(48,50,58)
NEON=(57,255,132)  ORANGE=(255,122,24)  RED=(255,48,64)
CORAL=ORANGE  PAPER=GRAPHITE
AR=Oswald Bold    CAP=Luckiest Guy (captions only)    ML=Menlo (terminals only, index=0)
```

Chips and cards: graphite + accent bar, Oswald. Accent bars orange/neon/red
per section. Hero titles **~960px wide**. User B-roll fills ~1000x500, not a
small inset. Full lock text, the conveyor staple and the intro billboard
notes: `references/reference-edits.md`.

Reference compositor + asset library: this skill's `templates/`. Per video,
create `projects/<slug>-animated/` (slug from the clip filename or topic)
and adapt.

Env: `GIPHY_API_KEY` in `.env` (for reaction GIFs). Band prep is local: ffmpeg, OpenCV, Whisper.
Run `tools/filler_cut.py` on the raw take first (ums, uhs, false starts, dead air), then prep from `raw/cut.mp4`.

## Required input

The user **must** provide a talking-head clip. Accept:

- an absolute/relative file path (`~/Desktop/hook.mov`, `source/talking.mp4`)
- a file they dropped into the chat / workspace
- a URL that **is** their talking-head (download with yt-dlp / curl immediately)

Refuse to start until the clip exists on disk. If they also drop a *reference*
reel URL (the thing to recreate visually), that is optional and only supplies
the script — never its pixels.

Vertical 9:16 is ideal. Horizontal/webcam is fine; prep will cover-crop.

## Pipeline

1. **Workdir.** `mkdir -p projects/<slug>-animated/{source,audio,renders,frames}`
   and `cd` there. Copy this skill's `templates/` in (including `apple_counter.py`, `light_fx.py`,
   `fonts.py`, and `fonts/Oswald-Bold.ttf`).

2. **Prep the talking head** (do this first — it is the timeline):

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/prep_talking_head.py" \
  --clip "/ABS/PATH/TO/CLIP" \
  --workdir . \
  --whisper
```

Writes `source/talking_head.mp4` (native resolution, never downscaled),
`audio/narration.wav` + `.m4a`, `renders/talking_band45.mp4` (**1056×960 @
30fps**, rounded later in compose), `source/meta.json` (`DUR`, crop), and
`audio/words.json`.

Inspect band frames at **3 to 4 timestamps** (the recorder re-frames the
head mid-clip). Crop rule for **live** heads: keep the **full hat /
hairline in frame** with a sliver of space above (backward caps sit higher
than Haar's face box). Default `--head-pad` is 0.35. If the crown is clipped,
lower `--crop-top` (and raise `--crop-h` to match the 1056:960 band aspect),
but never below the clip's own black region: prep scans the whole clip for
the first lit row and clamps the crop under it (`content_top`), and refuses
a band with black top rows (`verify_band_top`). A black strip above the
head is a failed prep, not a look. Do not letterbox the band. Do not scale
the band below 1056×960.

3. **Get the script (words to animate).**
   - Default: the talking-head transcript (`audio/words.json`) **is** the script.
   - Extra script given → use it, but **time** beats to the clip's Whisper
     stamps, not to the written script's imagined pacing.
   - Extra URL given (IG/YT/TikTok to *recreate*) → scrape caption / Whisper
     that source for copy only. IG: Apify `apify~instagram-scraper`
     (`directUrls` + `resultsType: "details"`), download `videoUrl` immediately.
     YouTube/TikTok: yt-dlp. Then persona-swap / product-name-fix against the
     caption. The talking-head clip still owns picture + audio.

4. **Guard on-screen text.** Em/en dashes are banned from UGC overlays (AI
   tell). Censor spoken profanity on-screen Nick-thumbnail style (`sh*t`);
   leave the clip's audio uncensored. If the talking head is *not* Kevin and
   the optional source script names Kevin/Kev/Nick/Saraev, strip or swap
   those names in overlay copy.

5. **SOURCE REAL BRAND ART** (do this before choreography). Walk the transcript
   for every named product, tool, model, or company (Claude, Google, GitHub,
   GitNexus, OmniRoute, GPT, Gemini, Llama, …). For each one, fetch a real
   mark into `assets/logos/<slug>.png` and a social/product card into
   `assets/shots/<slug>.png` when it exists:

```bash
python3 ".../split-animated-talking-head/scripts/fetch_brand_asset.py" \
  --name claude
python3 ".../split-animated-talking-head/scripts/fetch_brand_asset.py" \
  --name gitnexus --github abhigyanpatwari/GitNexus
```

   Priority: **Claude family is locked** (Kevin 2026-09-03). Do not fetch a
   favicon for Claude, Claude Code, Opus, Sonnet, Haiku, Fable, or Anthropic.
   Copy the bundled marks and dance them:

```bash
python3 ".../split-animated-talking-head/scripts/fetch_brand_asset.py" --name claude
# writes assets/logos/claude.png (sphinx) plus claude-invader.png + claude-sphinx.png
```

   - **Invader** (`templates/claude_marks.py` → `place_claude_invader`): block
     Space-Invader. Idle dance + walk cycle. **Look:** pass `look_at=(x,y)`
     in layer pixels and the pupils slide toward that point (blinks on their
     own). **Grab:** `grab="right"|"left"|"both"`, `grab_at=(x,y)`,
     `grab_t=0..1` (0 rest, ~0.55 reached, 1 holding/lifted). Pass `hold=`
     an RGBA (use `skill_chip("SKILL.md")`) to stick a card to the hand
     once `grab_t > 0.55`. Morph with `morph=0..1` (starburst scatter).
   - **Sphinx** (`place_claude_sphinx`): official Anthropic starburst badge.
     Use as the spinning mark for Opus / Sonnet / Haiku / Anthropic, and as
     a secondary badge next to the invader.
   Call `place_claude(layer, cx, cy, lt, word="claude", look_at=..., grab="right", grab_at=..., grab_t=...)`.
   Copy `templates/claude_marks.py` and `assets/claude-*.png` into the project.

   For every other named product: official SVG/PNG (Wikimedia / simple-icons /
   site favicon) → GitHub avatar + OpenGraph card → Google s2 favicon. Convert
   SVG with `qlmanage -t` on macOS. **A named product must appear as a logo,
   icon, screenshot, or orbiting mark — never as a text-only pill if a mark
   can be fetched.** Punch near-white backgrounds to alpha; keep dark
   full-bleed logos as round badges.

5b. **SOURCE THE FACES** (Kevin 2026-09-05). Whenever the transcript names a
   company, model, or niche with famous people behind it, put those people on
   screen. Niche map: `scripts/fetch_figure.py --list` (claude/anthropic,
   spacex, openai, marketing, business, sales, google, nvidia, meta, ...).

```bash
python3 ".../split-animated-talking-head/scripts/fetch_figure.py" --niche claude --top 4
python3 ".../split-animated-talking-head/scripts/fetch_figure.py" --name "Jensen Huang" --wiki Jensen_Huang --x nvidia --role "NVIDIA CEO"
# → assets/figures/<slug>.png (800x800 face-cropped) + <slug>.json {name, role, credit}
```

   - **Always view the fetched portraits** (contact sheet) before choreographing;
     swap with `--name/--x --force` if a crop is a stranger or a decade old.
     Eyeball any Wikidata `warn` line (it once returned the wrong "Tom Brown").
   - Helpers in `templates/media_marks.py`: `figure_row` (lineup),
     `figure_spotlight` (one person is the beat), `figure_card` / `figure_round`.
     **Face lands on the spoken word** (`word_onset(words, "anthropic")`).
     Pair with the brand mark (Claude → invader + sphinx beside the Amodeis).
   - **Size lock (Kevin 2026-09-14):** hook 1 face = `figure_spotlight(size=560)`
     or `figure_round` 520 to 620; 2 faces = `figure_row(size=480, gap=12)`; never
     3+ tiny heads on the first section. Body: single circle at least 280, 2 to 3-up
     row at least 320, spotlight at least 480. Banned: 150 / 170 / 190 anywhere.
     Max one lineup per section.

5c. **PULL REACTION GIFs** (Giphy API, Kevin 2026-09-05). Punchlines, flexes,
   shocks get a real reaction GIF, not a text pill. Needs `GIPHY_API_KEY`
   (`.env`); `--favorites` reads the dashboard allow-list (`gifs` table).

```bash
python3 ".../split-animated-talking-head/scripts/fetch_giphy.py" --query "mind blown" --list   # look first
python3 ".../split-animated-talking-head/scripts/fetch_giphy.py" --query "mind blown" --slug mind-blown --pick 1
python3 ".../split-animated-talking-head/scripts/fetch_giphy.py" --favorites --query money --slug money-rain --mark-used
# → assets/gifs/<slug>/f0001.png … @30fps (≤4s, 720px wide) + meta.json
```

   **Eyeball frame 1** (drop slurs/subtitles, wrong person, missed joke). One GIF
   per beat, 5 to 8 per video, never the hero over 2.5s, never covering a 960px
   title. Later-section stack: title at cy≈125, pair of ~400px GIFs at cy≈450.
   Hook frame 0 stays the billboard. GIF audio never mixed in. Rating pg-13.

5d. **TOPIC LOGO CONVEYOR, staple (Kevin 2026-09-10).** Every video gets a
   full-width horizontal scroll of 5 to 8 icons tied to THIS edit (110 to 140px,
   graphite badges), drawn through `guarded_conveyor`. On the hook also place
   1 to 2 **giant** logos (360 to 520px) (Kevin 2026-09-14).

```python
from media_marks import topic_marks
marks = topic_marks(["openai", "cursor", "docker", "cloudflare", "vapi"], size=120)
guarded_conveyor(layer, 400 + PACK_DY, max(0, lt - t0), marks,
                 conveyor_marks, name="topic-lane", speed=180, gap=22)
```

   One moving stream at a time, it owns its y-band, `lanes.reset()` every frame.
   Marks must match the video (eyeball each PNG). Never on the caption line;
   center at most `770 - size/2 - 10` after PACK_DY. Gate the lane off before a
   lower third slides in (see `references/learnings.md`, 2026-09-13).

   Full step text: `references/faces-gifs-conveyor.md`.

6. **AUTHOR THE ANIMATION** (fresh per script): split narration into sections
   at spoken anchors using `audio/words.json` + `source/meta.json` `DUR`.
   **Density + look are locked to the china-robots recut**
   (china-robots (render.py no longer on disk; use social-agents / gitnexus as code refs), Kevin 2026-09-10):
   that is how animated every video in this format should feel. Target
   **6–10 elements on screen at once**, not 2–3 lonely cards.    Prefer
   **motion graphics over copy**: spinning logos, GitHub/product chrome
   (`shot_card`), terminals with ticking lines, skill-file grids, computer
   mockups, scan HUDs, force-directed graphs, brand badges, code
   rain, locks/skulls/bombs when the topic is hacks. Text cards caption a
   graphic, they are not the graphic.
   **Do not default every beat to `orbit_marks`.** The **topic logo conveyor
   is mandatory** (see `5d`). Rotate the *other* motion: zigzag, explode,
   ticker, cascade, loop-arrows, Ken Burns. One orbit per video is plenty.
   Scene content must MATCH what's being said. Set `DUR` from `meta.json`,
   not the template's 62.9s.

   **Cold open (locked, Kevin 2026-09-02):** frame 0 of the *video* must
   already be packed. Scroll-stop on TikTok/Reels shows the first frame.
   Atmosphere (terminal, skill tiles, ghost word, a logo that is legal to
   show) uses `place(..., t0=-0.4, dur=0.01)` so the ease-in has already
   finished. **Never** start the first beat at `t0=0` with `dur=0.3` — that
   leaves frame 0 blank. Skip the white flash on the **hook** section for
   the same reason.

   **Beat `t0` is the spoken word, not the section start.** For every punchline
   (a product name, a number, a claim), look up that word's start in
   `audio/words.json` and set `t0 = word_start - section_start`. Max lead is
   **0.1s**. Never put "300" / "2B" / a named plugin on screen while he is
   still winding up to say it — that spoils the line. Do not preview later
   named products in an earlier section (e.g. don't flash OmniRoute during
   "three core plugins"). Cold-open atmosphere is the exception: generic
   (computer, skills, "installing") can be up before the first named product.

6b. **EVERY SPOKEN NUMBER GETS A COUNTER (Kevin 2026-09-05).** Money, GitHub
   stars, downloads, views, followers, counts, years, percentages, "10 p.m.",
   "3 times a day": if the transcript says a number, a count-up animation
   lands on it. Run the detector while planning beats:

```bash
python3 ".../split-animated-talking-head/scripts/number_beats.py"   # reads audio/words.json
#  26.40s   100  socials  <- "100 socials"
#  48.46s  $20/mo         <- "20 bucks a month"
#  51.02s  $2B            <- "$2 billion"
```

   `number_beats(words)` (in `hyper_edits.py`) understands digits, spelled
   numbers ("twenty five", "a hundred"), scales ("2 billion", "9.3k"), money
   ("$20", "20 bucks"), "%", "3 times", "10 p.m.", "per month" and a trailing
   label word (stars, downloads, views, socials, agents…). It skips bare
   version digits ("Gemma 4", "LTX 2.5"). Fix Whisper mishears in `words`
   first (see the nano-banana / "2 .5" fixes) so the detector sees the real
   number.

   **Apple counter lock (Kevin 2026-09-29: "find and implement a modern apple
   inspired odometer that'll replace the one we currently have, it's bad").**
   Every hero number, big or small, renders through `templates/apple_counter.py`
   (`counter_card` and `odometer_card` in media_marks both delegate to it, so
   old call sites just work). It is modeled on iOS `contentTransition(.numericText())`
   and keynote stat slides:

   Spec summary (full spec in `references/apple-counter.md`): SF Pro Display
   Bold rolling digits on a frosted glass card, odometer carry, no leading
   zeros, full figures with live commas (`2,000,000,000` not `2B`), in-out
   easing for 10k and up, bare 1900 to 2099 treated as a year unless
   `"style": "count"` or a label is passed (Kevin 2026-09-29: "2000" started
   at 1960). Park at 0 up to ~0.2s before the number word, count on it, land
   on the unit word, max lead 0.1s. The counter is the only big piece while
   it counts. Sizes: hero 10k and up `w=1000, h=400`; smaller `w=440-560, h=300-320`.


   Hero counts are authored by hand from `number_beats(words)` (example code in
   `references/apple-counter.md`).

   Smaller numbers (100, 646, 20%, $20) use `counter_card` (same Apple
   counter, sized to the figure). Fallback:
   `auto_counters(layer, BEATS, t, a, place, handled=HANDLED)` once per frame
   after the section choreography (`HANDLED` = the `t` values you animated
   yourself). Counter = a big piece (stacking rule applies): exit the
   previous hero before it lands, never park it on a stream lane.

7. **Pacing (locked):** nothing on screen >2.5s *as the hero*; supporting
   orbiting marks / code rain / ghost words stay through the beat. 0.3s
   directional entrances with ±8° tilt + overshoot pop; exits fly up before
   the next beat; per-section Ken Burns zoom; white flash cut at section
   starts **except the first section**; ghost words parallax-drift; something
   always moving (spinning marks, orbiting logos, ticking checks, terminals,
   a lane). **Motion variety, not pulse (Kevin 2026-09-11):** no element
   scale-pulses or bobs in sync; big pieces are still after they land;
   rotate entrances (slam, whip, drop-bounce, tilt-in, typewriter) so no
   two consecutive beats use the same move. If a stretch of >0.4s would only show a ghost word, add
   another graphic.

7b. **HYPER-EDIT LAYER (locked, Kevin 2026-09-05)**, `templates/hyper_edits.py`.
   The motion graphics are the content; the hyper-edit is the cut. All
   deterministic in `t`, all on the **animation slot only**:
   - Punch + shake per frame: `layer = punch_zoom(layer, punch_scale(t, PUNCH_T, amt=0.045))`,
     `sx, sy = shake_offset(t, HIT_T, amp=14)`, `frame.alpha_composite(layer, (sx, LAYER_Y + sy))`.
     `PUNCH_T = punch_beats(words, PUNCH_WORDS)` (rare, see Critical); never
     `keyword_onsets` for punches. Band stays at `(12, BAND_Y)`.
   - Hyperframes: 1 to 2 frame accent inserts on cuts (`hyperframe(frame, t, CUT_T, FPS, region=(0, LAYER_Y, W, AH))`).
     Never on the hook, never on a counting odometer (Kevin 2026-09-15).
   - Whip cuts between sections (`whip_wipe(..., lt / 0.16, direction=whip_dir(name))`), whip OR hyperframe per cut.
   - Shake on section cuts plus at most 3 to 5 biggest claims, at most 0.26s.
   - Spring entrances (`spring_preset`, `ease_back_out`, `slam_in`), rotated via `entrance(k)`.
   - Freeze hit (`freeze_hit`) max one per video. Text fx: `count_up`, `typewriter`, `highlight_sweep`, `caption_impact`.
   Target: a 60s video feels like ~40 cuts though the band is one take.
   Full parameters: `references/hyper-edit-and-light-fx.md`.

7c. **No HTML overlay layer (Kevin 2026-10-02: "its actually bad").** The HyperFrames
   `hf_layer` overlay (`render_hf_layer.sh`, `hf_layer_frame`) is removed from the skill.
   Everything in the slot is drawn in the PIL compositor: kinetic titles, lower thirds,
   counters (`apple_counter.py`), terminals. Do not bring back an HTML/GSAP overlay.

7d. **LIGHT FX LAYER (locked, Kevin 2026-09-10)**, `templates/light_fx.py`, animation
    slot only. Atmosphere from frame 0 (`scanlines`, `hud_scan`, `neon_grid`,
    `bloom_orb` behind the invader/hero, `slot_vignette`). `light_hit` on the
    section's dramatic beat; `light_rays` only for the CTA / one hero flex;
    `caption_bloom` drawn before the word as a tight halo (a at most 40). Copy
    `light_fx.py` into the workdir. Code sample: `references/hyper-edit-and-light-fx.md`.

8. **Compose** (`templates/split_55_45_compositor.py`, adapted in the workdir):
   - Canvas: **1080 × 1920**. If an old project still has `W, H = 720, 1280`,
     change it before encoding. Coordinates are 1080-space (center **x=540**).
     The template's Megan example still writes 720-era numbers and wraps them
     with `s()` (×1.5). New choreography should use 1080 numbers directly and
     must **not** double-wrap.
   - Animation layer: **1080 × 770**, composited **1:1** at `(0, LAYER_Y)`
     with **LAYER_Y = 90** (canvas 90..860). Apply **PACK_DY = 210** inside
     `place()` (and conveyor / orbit / explode / zigzag / ticker / waveform /
     ghost y) so the pack meets the caption line. Clamp y so assets stay
     inside the 770 slot. After the offset, heroes land around canvas
     y≈500–660; footer chips / receipts kiss y≈850. Cards ~960–990 wide,
     hero numbers ~960×400–520 (`odometer_card` for ≥10k, else `counter_card` h=380–480, intro h≥440),
     intro logos 360–520px, body logos 280–360px, conveyor marks 110–140.
     Author `place(..., cy)` in the old 200–400 hero range and let
     `PACK_DY` drop them — do **not** also author at cy≈500 or they will
     clip the captions. **Side inset:**
     keep every asset fully on-canvas. Left/right edges stay inside
     **x=36..1044** (`SAFE_X`). A ~450px file-tree / terminal parked at
     `cx=165` gets sliced off the left. Side-column pieces: `cx ≥ 270`
     for ~450px cards, `cx ≥ 180` for ~180px icons. Prefer `frm="up"` /
     `"down"` for left-column assets. **Do not** `R(..., 0.78)` shrink, and
     **do not** design at 853 then `resize((540, 640))`.
   - Band: **1056x960 at y=936**, r=60 on all four corners, 12px side margins
     (see Critical). Read `renders/talking_band45.mp4` (already 30fps from
     prep). Hold the last frame if the clip runs short of `DUR`.
   - Kinetic captions **sit on the accent line on top of the band** (Kevin
     2026-09-18: "the text should be sitting on that pink line"; 2026-09-19:
     "the captions need to be above talking head", then "has to sit on top of
     that line, it's on it a bit"): one word, Luckiest Guy, `anchor="ls"`,
     `stroke_width=7`, at `y = BAND_Y - 8 - 7 - 3` (line top is BAND_Y-8) so the
     stroke's bottom edge touches the line top. Pop on word onset; KEYWORDS in
     `KEY_COL` and ~18% bigger; body words white, no separate shadow. Caption
     windows disjoint using Whisper word times.
   - Band file is `renders/talking_band45.mp4` (prep output). Hard-fail if missing.

9. **Encode + deliver:** frames → ffmpeg + the clip's narration audio
   (`audio/narration.m4a`), crf 16. Review a tiled overview + 2–3 full-res
   frames for collisions / crop. Stage a feed item in
   `brand-content/<persona-or-brand>/carousels/` only if publishing. Publish
   only on Kevin's go.

## Encode

```bash
ffmpeg -y -framerate 30 -i frames/out5/f%05d.jpg -i audio/narration.m4a \
  -c:v libx264 -pix_fmt yuv420p -preset medium -crf 16 -c:a aac -b:a 192k \
  -movflags +faststart -shortest renders/final.mp4
ffprobe -v error -select_streams v:0 -show_entries stream=width,height \
  -of csv=p=0:s=x renders/final.mp4
# must print 1080x1920 — anything else is a failed render
```

Use the clip audio, not a TTS stand-in. Do not mix in trending/copyrighted
sounds (YouTube Content ID).

**Never mux `audio/narration.wav`** (Kevin 2026-09-22, minecraft-astra-jev: "why is
the audio bad?"). That file is the 16 kHz mono downmix prep makes for Whisper. Mux
`audio/narration.m4a` (the untouched 44.1 kHz stereo track) or, better, map the audio
straight from the original clip with `-c:a copy`:

```bash
ffmpeg -y -framerate 30 -i frames/out5/f%05d.jpg -i "<original clip>" \
  -map 0:v:0 -map 1:a:0 -c:v libx264 -pix_fmt yuv420p -crf 16 -c:a copy \
  -movflags +faststart -shortest renders/final.mp4
ffprobe -v error -select_streams a:0 -show_entries stream=sample_rate,channels -of csv=p=0 renders/final.mp4
# must print 44100,2 (or the source's rate) — 16000,1 means the Whisper scratch track got muxed
```
## Learnings and bundled references

The full dated learnings log (every Kevin correction with its source video, reference project paths, and fixes) is in `references/learnings.md`. Read it before a new edit. Its rules are summarized in `## Critical` and the pipeline steps above. Other references:
- `references/reference-edits.md`: what the gold-standard renders (social-agents, gitnexus) did.
- `references/faces-gifs-conveyor.md`: full steps 5b to 5d (niche map, sourcing order, size floors).
- `references/apple-counter.md`: full counter spec.
- `references/hyper-edit-and-light-fx.md`: full steps 7b and 7d with code.

Other proven patterns from the log: partial edit / source passthrough when only the first N seconds need animating (`CUT_AT`, ref `projects/first15-animated/render.py`); live product b-roll inside a browser-chrome card (Kevin 2026-09-05 "really good"); cache card renders by state (`CACHE` dict, ~1,900 frames in ~5 min).

## Examples

**Example 1: standard split edit from Kevin's clip**
User says: "Here's my talking head ~/Downloads/gitnexus.mov, make the split animated version"
Actions:
1. `mkdir -p projects/gitnexus-animated/{source,audio,renders,frames}` and copy `templates/` (with `fonts/`, `apple_counter.py`, `light_fx.py`).
2. Run `scripts/prep_talking_head.py --clip ~/Downloads/gitnexus.mov --workdir . --whisper`; check band frames at 3 to 4 timestamps; fix product-name mishears in `audio/words.json`.
3. Fetch marks (`fetch_brand_asset.py`), faces (`fetch_figure.py --niche ...`), GIFs (`fetch_giphy.py --list` then `--pick`), and run `number_beats.py`.
4. Author sections from `references/reference-edits.md` energy, compose at 1080x1920, encode with the clip's real audio, ffprobe for `1080x1920` and `44100,2`.
Result: `renders/final.mp4`, 1080x1920, band 1056x960 at y=936, captions on the accent line. Copy to ~/Downloads with a readable name; publish only on Kevin's go.

**Example 2: clip plus a reel to recreate**
User says: "Use my selfie clip but recreate the visuals from this IG reel: https://www.instagram.com/reel/XXXX"
Actions:
1. Prep the selfie clip first (it owns picture and audio).
2. Scrape the reel with Apify `apify~instagram-scraper` for its caption/words only; never use its pixels.
3. Author beats timed to the selfie clip's Whisper stamps.
Result: Split short with the user's head and voice, visuals authored fresh.

**Example 3: wrong skill**
User says: "Make a split animated short with Megan narrating this script"
Actions:
1. This needs a HeyGen avatar, so load `split-animated-short` instead.
Result: Routed; this skill never calls HeyGen.

## Troubleshooting

**Error:** `band has a black strip at the top at t=[...]s` (from `prep_talking_head.py`)
Cause: The crop starts above the recorder's black region, which can move mid-clip.
Solution: RAISE `--crop-top` (or rerun prep, which clamps under `content_top`). Never lower it.

**Symptom:** Black rows at the BOTTOM of the band
Cause: Letterboxed source (picture is a ~608px strip inside 1080x1920) (2026-09-18).
Solution: Rerun prep without `--whisper` with an explicit cover crop, e.g. `--crop-top 656 --crop-h 608 --crop-x <face_cx-334> --crop-w 669`. Details in `references/learnings.md`.

**Error:** `refusing a downscaled source` / `band is WxH, refusing anything below 1056x960`
Cause: A 1080p clip was scaled down, or the band came out too small.
Solution: Use the original clip at native resolution; never ship 720p.

**Symptom:** Hat/crown clipped, or face crop missed (side-on, backlit, hatted head)
Cause: Haar face boxes ignore baseball caps.
Solution: Adjust `--crop-top` / `--crop-h` (keep the 1056:960 aspect) or raise `--head-pad` (default 0.35). If the chin clips after that, the band position is the first lever.

**Symptom:** Audio sounds bad in the final render
Cause: `audio/narration.wav` (16 kHz mono Whisper scratch) was muxed.
Solution: Mux `narration.m4a` or map the original clip audio with `-c:a copy`; ffprobe must show `44100,2`.

**Symptom:** Talking head out of sync in parallel `RANGE=` chunks
Cause: The render loop reads the band sequentially from frame 0.
Solution: Before the loop, `band_cap.set(cv2.CAP_PROP_POS_FRAMES, todo[0])` (2026-09-26, viktor-short).

**Symptom:** Wrong words in captions ("Clod", "slot" for "slop", "GBT", wrong opening word)
Cause: Whisper mishears product names and the first word.
Solution: Use small.en with an `--whisper-prompt` of product names (prep default), play the first 2s, and fix `words.json` before `number_beats` and captions.

**Symptom:** Half-sliced icons along the bottom of the slot
Cause: Conveyor/orbit helpers do not clamp like `place()`.
Solution: Keep stream centers at most `770 - icon_size/2 - 10` after PACK_DY.

**Symptom:** Lower third collides with the topic lane
Cause: Lower third at slot y≈640 lands on a lane at `490 + PACK_DY`.
Solution: Gate the lane with the lower-third window so it exits first (2026-09-13).

**Error:** `GIPHY_API_KEY not set` / `DATABASE_URL not set, cannot read favorites`
Cause: Missing env in `.env`.
Solution: Add the key. If psycopg2 rejects `DATABASE_URL`, its `uselibpqcompat` param is the cause; `_pg_dsn()` strips it.

**Error:** `could not fetch a mark for <name>` (`fetch_brand_asset.py`)
Cause: No official SVG/PNG, GitHub avatar or favicon found.
Solution: Pass `--github owner/repo`, or source the mark manually; never fall back to a text pill if a mark exists.
