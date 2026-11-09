# Learnings log (split-animated-talking-head)

Full dated log of Kevin's corrections and run learnings, moved out of SKILL.md for length. Every rule here is also summarized in SKILL.md (`## Critical` and the pipeline steps); this file keeps the full context, the screenshots/videos each rule came from, and the reference project paths.

- **2026-10-08 picture rules, from Chase AI's ["Claude Now Does Video"](https://www.youtube.com/watch?v=rscb1DgJtNg).**
  Watched the 14 min cut (first 8 min measured, later beats sampled). It is a 16:9
  circle-cam edit, so the band geometry here does not change. What transfers to the
  slot: his own on-screen review said the final hit was swallowed by the narration
  and now lands in the silence before the last line (~0.6s early when a pause
  exists); a "same t, same picture" beat sat still for 7 seconds and had to become
  two moving renders plus a sweep and a slow push; a video icon that was a tiny
  empty mark in the corner had to become big, centered, with a strike through it
  for the negation. Square generated clips in that video are pillarboxed, never
  stretched. Screen recordings of the actual tool (the agent log, Excalidraw, a
  GitHub README) hold for one to three minutes with markup landing on the spoken
  words. Designed animation beats still cut about once a second (median shot 1.0s
  across 54 shots in the first 8 min; the 174s / 141s / 61s outliers are the
  recordings). The round face cam is a long-form layout (`longform-animated-talking-head`
  CIRCLE). Do not replace this skill's 1056x960 band with a circle.

- **Caption glow is a tight halo (Kevin 2026-09-19: "the glow the captions give off is
  way too large"):** `caption_bloom` radius comes from the word height (th*0.55+10),
  alpha 40, never max(tw, th)/2+36. A wide word must not light up half the band edge.
- **Captions on the pink line (Kevin 2026-09-18, JEV video 3 screenshot):** the
  caption used to sit in the gap between the animation slot and the band
  (`CAP_BOTTOM - fs`, descender padding left a visible gap). Kevin wants the
  letters resting ON the line. First fix centered the word on the line and it
  covered the top of the cap (2026-09-19: "the captions need to be above
  talking head"). Locked: `anchor="ls"` at `y = BAND_Y - 5` (baseline on the
  line, glyphs above the head), drawn after the band. Then 2026-09-19 pm: "has
  to sit on top of that line, it's on it a bit" + the DOG screenshot: caption
  face is now Luckiest Guy with a 7px black stroke, baseline at BAND_Y-18 so the
  stroke bottom rests on the line top; no separate shadow (the stroke is the
  contrast). Title cards / chips stay Oswald. Template + both jev render.py updated; keep `caption_bloom` and the
  black shadow so silver reads on the bright room behind the head.

- **Oswald Bold is the overlay face (Kevin 2026-09-15, screenshot of AND
  over a code UI).** Title cards, chips, huge_word, captions, counters, name
  plates, ghosts: `AR` from `templates/fonts.py` → `fonts/Oswald-Bold.ttf`.
  Arial in the slot is a regression. Terminals / code rain / tickers stay
  Menlo (`ML`, `ImageFont.truetype(..., index=0)`). Copy `fonts.py` + the
  ttf with the other templates. Condensed type can run 8–12px larger than
  the old Arial sizes on the same 960-wide card.
- **Variety over repetition; effects for drama only (Kevin 2026-09-12: "on
  the gifs and stuff, i like animations but a variety. punches and stuff
  like that should apply for dramatic effect").** Rules: (a) no two
  consecutive GIFs / cards enter the same way, rotate with
  `hyper_edits.entrance(k)` (up / tilt-left / drop-pop / tilt-right /
  scale-up / slide / drop-tilt / pop-right) or hand-pick; (b) a GIF appears
  once per video unless it is a deliberate callback on the CTA; (c) impact
  effects (punch, shake, light_hit, hyperframe flash, slam) are reserved for
  the ONE dramatic beat of a section (the reveal, the number, the
  punchline), never on every chip and badge; (d) between beats the slot
  moves through entrances, lanes, terminals typing and GIF motion, not
  through camera hits. If a section has two hits inside 4 s, cut one.
- **Punch-ins were on every keyword (Kevin 2026-09-12: "far too many zoom
  punch effects. it makes it annoying to watch").** 30 keywords in a 37 s
  clip = a zoom every second plus speed streaks on each. Locked:
  `punch_beats()` in hyper_edits (one hero word per section, >=8 s apart,
  <=6/min, amt 0.045); KEYWORDS never drive the zoom again. Energy comes
  from entrances, GIFs, cuts and light hits, not from the slot jumping.
- **No black strip above the head (Kevin 2026-09-12, github-research-agent
  screenshot: "it just doesn't look good").** Kevin's recorder frames the
  head with a BLACK region above it and that boundary moves mid-clip
  (705 -> 772 at 30 s), so a face-box crop that starts above it ships a
  black bar at the top of the band for part of the video. `prep_talking_head.py`
  now scans the whole clip (`content_top`, every 0.5 s, max first-lit row),
  clamps `crop_top` under it, shrinks + upscales the crop when the picture
  below is shorter than 982 px, and `verify_band_top` refuses a band with
  black top rows anywhere. Rule: never fix this by lowering `--crop-top`;
  raise it. Eyeball band frames at 3 to 4 timestamps (not one) before
  compositing.
- **Partial edit / source passthrough (Kevin 2026-09-11, "only the first 15
  seconds needs edit, the rest is handled by broll, captions throughout").**
  When the source clip already carries its own split (screen recording over
  the head) after some point, set `CUT_AT` and animate only `SECT` before
  it; from `CUT_AT` write the SOURCE frame verbatim (`cv2` on
  `source/talking_head.mp4`, native 1080x1920) + `draw_caption()` at the
  same `CAP_Y`, plus one `hyperframe` on the cut.
  Reference: `projects/first15-animated/render.py`. Check the source's
  own split line first (brightness-jump scan found y=944) so captions do not
  land on his B-roll's content.
- **2026-09-11 (Kevin, second-brain): "far too much pulsing my friend. i like
  effects but add variety."** Three things were breathing at once: `place()`
  bobbed EVERY element on the same 2.6s sine (the whole slot inhaled
  together), the word-mark cards ran `scale 1.04 yoyo repeat 3`, and the
  CTA card pulsed forever (`1 + 0.05*sin(6t)`). Locked: (a) big pieces
  (>=400px) never idle-move; small pieces drift <=3px with a per-element
  phase + period (3.2 to 5.6s) so nothing syncs; (b) no `yoyo`/`repeat`
  scale pulses, one overshoot settle then still, and each
  card gets a DIFFERENT entrance (whip from left, drop + bounce, letter
  spacing ease); (c) CTA = one slam + one `highlight_sweep`, then still;
  (d) `rim_pulse` only for the first 0.6s after a hit. Energy comes from
  cuts, hits, GIFs and entrances, never from everything wobbling.
- **2026-09-10 (Kevin, agentic-skills): go harder + light the slot.** Sparse
  2–3 card layouts read dead next to china-robots. Lock `templates/light_fx.py`
  on every recut: scanlines, HUD scan, neon floor grid, bloom behind the
  invader, `light_hit` (ring/sparks/flare) on punches and GIF lands, caption
  bloom on keywords. GIFs stay the front layer. Invader > sphinx when both
  exist. Density still china-robots (6–10 live elements).
- **2026-09-10 (Kevin, voice-agents screenshot): the horizontal logo
  conveyor is a staple.** Full-width scroll of icons associated with the
  video (OpenAI / Cursor / Docker / …). Required every cut — `5d` +
  `media_marks.topic_marks` + `guarded_conveyor`. One lane, topic-true
  marks only.
- **2026-09-10 (Kevin, github-research-agent): slot wash was too dark.**
  Lift CHAR to (48,50,58). `textured_bg` adds light patches + a stronger
  accent glow; do not composite `base-8` black sinks. `slot_vignette` at
  `a=22`, not 55. Reference compositor:
  `projects/github-research-agent-animated/render.py`.
- **2026-09-10 (Kevin, china-robots): "INCREDIBLE EDIT THATS THE STANDARD."**
  Density, titles, GIFs, neon/orange/red. Compositor:
  china-robots (render.py no longer on disk; use social-agents / gitnexus as code refs). Do not regress to
  paper/sage/coral or a sparse 2–3 card layout. Use the brighter wash above.
- 2026-09-05 upgrade (Kevin): Giphy GIFs (`scripts/fetch_giphy.py` +
  `gif_card`), notable-figure portraits per niche (`scripts/fetch_figure.py` +
  `figure_row` / `figure_spotlight`), hyper-edit layer (`templates/
  hyper_edits.py`: keyword punch-ins, hyperframe inserts, whip cuts, shake,
  springs, freeze hit). All
  verified on the opensource-100 band. Wikidata name search returned the
  wrong Tom Brown → X avatar now outranks Wikidata; tiny Commons originals
  (<400px) are swapped for the X avatar too. Dashboard `DATABASE_URL` carries
  `uselibpqcompat`, which psycopg2 rejects; `_pg_dsn()` strips it.
- Whip + hyperframe on the same cut reads as a glitch storm. One per cut.
- **Density floor (Kevin 2026-09-08, cold-DM edit): "some parts of the animation
  screen were a little bit empty."** Every section must carry, from its first
  frame: at least 3 pieces on screen at all times (a hero/card, a mark or
  figure, a chip or lane), at least one GIF or one notable-figure per
  section, and something moving (lane, spinning mark, invader, count-up).
  Cold-open atmosphere at t0=0 for every section, never a lone chip. More
  memes, more public figures, more motion: if a beat has only a chip and a
  ghost word, add a figure row, a GIF, or a phone/terminal card.
- Numbers (Kevin 2026-09-05 + 2026-09-15): every spoken number is a
  counter, rendered by the Apple counter (templates/apple_counter.py, 2026-09-29):
  full figures, SF Pro rolling digits, odometer carry. Compact "2B" and the old boxed reels (orange cages, overflowing
  digits, "COUNTING TOKENS") are a fail. Run scripts/number_beats.py;
  auto_counters covers what the choreography misses. Bare version digits
  are skipped on purpose. The odometer is the only big piece while it
  counts — no GIF / invader / hyperframe on top of the digits.
- **Talking head locked (Kevin 2026-09-05, HF-hack intro):** the band punch-in
  and shake made the talking head move; Kevin does not want that. He DOES
  want the shake and impact beats, on the animation slot. Band is composited
  at a fixed (12, BAND_Y); the slot layer gets punch_zoom + shake_offset.
- **Band sits higher (Kevin 2026-09-15, ollama-claude-code recut):** y=960
  flushed the card to the bottom of the 9:16 and clipped the chin/body.
  BAND_Y=936, round all four corners, leave ~24px under the card. If the
  hat/crown is clipped, lower `--crop-top`; if the chin is clipped after
  that, the band position is the first lever, not a tighter crop.
- **One carousel per band (Kevin 2026-09-05, voice-agents hook).** Two
  conveyors on the same y, plus loose icons and the invader parked on top,
  read as four carousels stacked. Rules: one moving stream (conveyor /
  zigzag / orbit / ticker) per section at a time; it owns its y band
  (mark height + 6px) and nothing else is placed in that band; a second
  stream may only start after the first has exited. `hyper_edits.lanes`
  enforces it: call `lanes.reset()` at the top of each frame, draw streams
  through `guarded_conveyor(...)` (an overlapping stream is skipped and
  logged), and check `lanes.free(y0, y1)` before parking a card or the
  invader on a stream. No loose "$" icons as fillers: Kevin dislikes them.
  Fill with product marks, chips, or nothing.
- **Stacking rule (Kevin 2026-09-05, Kairos "unbelievable" beat):** a GIF
  card, a hero text card, the previous section's repo/shot card and the
  lower third all overlapped at once. Max **two big pieces**
  (>400px wide: GIF card, hero, shot/repo card, figure spotlight) live at a
  time; when a GIF or hero enters, `exit_at` the previous big card ≤0.1s
  before its `t0`. While a lower third is live (slot y≥600) nothing else
  is authored below cy≈380 (→ py 590). Left/right halves: GIF on one side,
  hero on the other, never both centered. Chips and marks are the only
  things allowed to overlap a card edge.
- GIFs are 720px frame banks (≤4s); a 12s Giphy loop is 360 PNGs — pick the
  short ones from `--list`.

- Frame 0 must be packed. `place(..., t0=-0.4, dur=0.01)` for cold-open
  atmosphere. `t0=0` + 0.3s ease + the hook flash = a blank first frame on
  scroll-stop (NVIDIA SkillSpector, 2026-09-02). Skip the white flash on hook.
  The packed frame is a **billboard** (Kevin 2026-09-14): one or two giant
  figure circles / a huge number / a huge logo, not three 170px heads plus
  chips. If frame 0 looks like a sticker sheet, it failed.
- **Intro figures + numbers + logos must be huge (Kevin 2026-09-14).**
  Hook `figure_round` 520–620 (or `figure_row` size=480 for two). Body floor
  280 / 320. Hero numbers: the Apple counter (`counter_card` / `odometer_card`, full figures) intro h≥400.
  Standalone intro logos 360–520.
  150–220px portrait circles are a regression.
- **Look + density gold standard is china-robots (Kevin 2026-09-10):**
  china-robots (render.py no longer on disk; use social-agents / gitnexus as code refs). Neon/orange/red accents,
  silver captions, 960px titles, full-slot B-roll, 5–8 memes, title-over-GIF
  stack, 6–10 elements live. **Slot wash is brighter** (Kevin 2026-09-10,
  github-research-agent): CHAR=(48,50,58), GRAPHITE=(36,38,46), lift the
  textured_bg instead of crushing it toward black, keep `slot_vignette` light
  (`a=22`). Near-black CHAR=(14,15,18) reads dead. NVIDIA SkillSpector
  (2026-09-02) is the older density floor — match china-robots energy on
  every video. Computer / hack / code talk still gets terminals, grids,
  conveyors, code rain — not a single text pill.
- Left-edge clipping: dense left stacks (file trees, warn icons, globes)
  were getting cut off on SkillSpector. Keep asset edges inside x=36..1044.
  Do not `place(..., 165, ...)` a 450px card. Clamp in `place()` if unsure.
- Whisper also drops or swaps the **opening word**. Play the first 2s of the
  clip before locking captions. "stop wasting" has been heard as "without wasting".
- Pack lock (opensource-100, 2026-09-03): `AH=770`, `LAYER_Y=90`,
  `PACK_DY=210`. Composite at `(0, 90)`, not `(0, 0)` or `(0, 42)`.
  `LAYER_Y=42` + `AH=840` + heroes at cy≈280 hugs the top and leaves a
  vacant band between the graphics and the captions. The pack must sit
  just above y≈867. Verify a frame: ink in the animation slot should end
  within ~80px of the caption line, not 250px above it.
- Cache card renders by state (`CACHE` dict) — ~1,900 frames in ~5 min.
- Live talking-head band is **1056×960 @ y=936** on **1080×1920**. Never
  704×640 on 720×1280 — that downscales a 1080p clip and Instagram wrecks it
  further (Kevin 2026-09-03). Recrop with lower `--crop-top` rather than stretching.
  Do not sit the band at y=960 (Kevin 2026-09-15: too low, bottom clipped).
- Named products get **real logos / GitHub cards**, not text pills. Fetch before
  authoring beats (`scripts/fetch_brand_asset.py`). Claude / Claude Code /
  Opus / Sonnet / Haiku / Fable / Anthropic always use the bundled invader +
  sphinx (`templates/claude_marks.py`) — never a generic favicon.
- Fill the animation slot **edge to edge** (1080×770 at y=90, 1:1). The
  slot is shorter and lower than the old 840@y=42 so content meets the
  captions. Downscaling an 853 canvas into 540×640 leaves a dead band
  between graphics, captions, and the talking head. Downscaling the whole
  video to 720p is forbidden.
- Beat `t0` = spoken-word start minus section start. Punchline graphics (names,
  numbers) appear **on** the word, never 4–6s early. Max lead ~0.1s.
- Prep transcodes the band to 30fps so cv2 reads 1:1 with render frames
  (phone clips are often 24/60fps, HeyGen was 25).
- Face-detect crop can miss side-on / backlit / hatted heads — `--crop-top` is the
  fix, not stretching. Haar face boxes ignore baseball caps; pad extra.
- Hard-fail if `renders/talking_band45.mp4` is missing or shorter than ~1s
  before composing. Do not fall back to HeyGen.
- Conveyor/orbit/zigzag y + PACK_DY must keep the FULL icon inside the 770px
  layer: `conveyor_marks` (and friends) don't clamp like `place()` does, so a
  conveyor authored at cy=560 (py→770 = the layer edge) renders a row of
  half-sliced icons (embracing-fanaticism, Kevin 2026-09-05: "cutoff and looks
  bad"). Keep stream centers ≤ 770 - icon_size/2 - 10 after py(), or add the
  clamp inside the helper.
- Live product b-roll inside a browser-chrome card in the animation slot is a
  PROVEN beat (embracing-fanaticism app section, Kevin 2026-09-05: "really
  good"). Map abs-time windows to source time, seek per frame, keep the
  window under a name_tag + scoreboard chip.
- Read the whole transcript for niche + vibe BEFORE authoring beats, and plan
  notable-figure portraits / GIFs into the choreography wherever the topic
  supports them ("content creator" talk → creator faces, "basketball app" →
  hoopers) — fetch_figure.py --niche + fetch_giphy.py. Placement doesn't have
  to snap to the exact spoken word; it flows from the plan. Named figures
  (MrBeast, Top G) stay mandatory (Kevin 2026-09-05).
- **Lower-thirds vs the topic lane (stop-the-slop, 2026-09-13):** a
  lower third at slot y≈640 lands on top of a `guarded_conveyor` at
  `490 + PACK_DY`. Gate every
  lane with the LT window (`if lt < t_named - 0.05 or lt >= t_after:`) so the
  lane exits before the lower third slides in. Also: `punch_beats()` is now
  used for real (5 punches on a 61 s clip); Whisper base.en heard "slop" as
  "slot" and "GPT" as "GBT" — fix words.json before number_beats/captions.
  Reference: `projects/stop-the-slop-animated/render.py`.
- **Letterboxed source = black band bottom (2026-09-18, name-is-jef).** Kevin's
  recorder can export the picture as a 608 px strip (rows 656..1263) inside a
  1080x1920 frame. Prep clamps the crop top under the black but keeps
  `crop_h=982`, so the band ships ~320 black rows at the BOTTOM. Check the band
  sheet for black bottom rows too. Fix: measure lit rows, re-run prep without
  `--whisper` (keeps the fixed words.json) with a cover crop at 1056:960:
  `--crop-top 656 --crop-h 608 --crop-x <face_cx-334> --crop-w 669` (Haar face
  cx on the lit strip). Upscale is fine; letterbox is not.
  Reference: `projects/name-is-jef-animated/render.py` (JEV / TypeSafe:
  pink brand accent, founder portraits scraped from typesafe.ai/team, pricing
  table + Pareto chart shots as b-roll, decision_row / action / yes-no / score
  cards, price wind-down + kinetic "one word at a time" + RL lower third).
- **Parallel RANGE chunks desync the band (2026-09-26, viktor-short).** The gitnexus loop reads
  `band_cap.read()` sequentially from frame 0, so `RANGE=261:522` renders the head from 0:00. Before the
  loop: `if todo and not PREVIEW: band_cap.set(cv2.CAP_PROP_POS_FRAMES, todo[0])`. Verified sync by
  diffing band crops vs `talking_band45.mp4` (diff <1 at the right frame). Reference:
  `projects/viktor-short-animated/render.py` (assembled from gitnexus parts + `viktor_scene.py`).
  Also: small.en Whisper with `initial_prompt` of the product names fixed every mishear base.en made
  ("Claude"/"cloud", VIKTOR, "won't"); run it on shorts too, not just long-form.
