---
name: longform-animated-talking-head
description: Edits a LANDSCAPE (16:9, YouTube long-form) talking-head clip Kevin records at his desk into a fast-paced animated hyper-edit. 1920x1080, hero layout by default (full-width animation slot, his head in a corner picture-in-picture, fitted flow diagrams) with full-bleed and split layouts as accents, plus a round face-cam over a full-bleed animation or screen recording when the picture is the content. Motion-graphic cards, real logos, Giphy reaction GIFs, YouTube thumbnails he drops in, kinetic phrase captions on an accent line, punch/shake on the slot only. No HeyGen. Use when the user hands over a landscape, long-form or YouTube talking-head video (intro, full episode, tutorial) and asks to edit it. Not for vertical shorts (use split-animated-talking-head, or split-animated-short for Megan/Danny), a calm warm premium edit (gadzhi-edit), a cinematic trailer or cold open (nolan-edit), faceless voiceover B-roll news (fireship-style-edit or fireship-style-short), or learning a new style from a reference video (reverse-engineer).
---

# Long-form animated talking head (landscape 1920x1080)

Built reverse-first on the JEV AI x HyperEdit intro (2026-09-21, Kevin: "ya really good.
solid long form skill start"). Reference cut = **`projects/jev-intro-longform-animated/render.py`**
on top of `templates/longform_engine.py`. Same visual language as the short-form flagship
(Oswald + Luckiest Guy, graphite wash, neon/orange/red + brand accents, real marks, GIFs,
light fx, rare punches) but the canvas, layouts and hook rules are different.

## Critical: locked rules for long-form (Kevin 2026-09-21)

1. **HERO is the default layout** (Kevin 2026-10-27 on the Trial Reels engine edit: "i should
   remain in this edit layout view. its the cleanest"). Full-width slot 1840x950, his head in
   the ringed PIP bottom-right. Diagrams/cards live on the left ~1240px; the column above the PIP
   (x 1290..1840, y < 600) carries the context rail: a "you are here" `ring6`-style loop or
   chapter tag (a `chip`). FULL (face full-bleed + side overlays) only for the hook, one dramatic
   claim, the subscribe beat and the CTA. CIRCLE when footage IS the picture (rule 7).
   SPLIT (slot left + tall head card right) only when Kevin asks for it (it was the 09-21
   favourite for pure talking; superseded for explainer edits).
2. **No mystery cold open.** Short-form gets the dark wash + "?"; long-form does NOT. Frame 0
   is a bright billboard on the ACTUAL topic (brand badges + wordmark + "the biggest update
   yet" chip beside the untouched face). Never darken the hook. No "?" badges later either.
3. **No bottom strip.** Progress bar / label / timecode / chapter name were "truly pointless".
   Accent line at y=1038, captions rest on it, nothing under it.
4. **Head never moves.** No punch_zoom / shake on the head in any layout. Slot layer only.
5. **Captions are phrase groups** (<=4 words, Luckiest Guy 60px, white, 7px black stroke,
   active word in `KEY_COL`, unspoken words dim STEEL), baseline resting on the accent line.
6. **Consistent palette + type across a series.** Pick brand accents once (`PINK` = Jev,
   `VIOLET` = HyperEdit; `CYAN` / `NEON` / `RED` per section) and reuse them every episode.
7. **CIRCLE when the picture is the content** (2026-10-08). A generated animation, a
   screen recording, or one kinetic word uses the round cam, not the tall card and not
   the rectangular PIP. HERO stays the default the moment he is talking to camera
   with no footage to watch.
8. **The payoff hit lands in the pause.** If the punchline word has ≥0.35s of silence
   before it, `pause_onset()` puts the visual at the start of that silence. A hit on
   the word itself gets swallowed by the voice.
9. **No identical picture for ~7s.** A held beat is a picture that is changing
   (typing, a count, a slow push, two renders moving in lockstep with a sweep).
   The same still frame twice is a failed beat. A tiny icon in a corner is a fail:
   the named object is big and centered. Negation is `strike_chip` through the real
   object, not a pill that says "no".
11. **Diagrams use `templates/flow_diagram.py`, never hand-placed boxes** (Kevin 2026-10-27:
    "this diagram looks horrible ... the flow ... and the text not fitting in the boxes ...
    that happened in almost all diagrams"). `flow_card` sizes every box from its text (label
    shrinks 44 -> 28px, sub wraps to 2 lines then ellipsizes), keeps every box inside the panel,
    relaxes overlaps, and routes edges side-to-side with arrowheads and spread ports;
    `loop_card` does the same for loops (nodes on an ellipse, arrowed arcs, numbered badges).
    Author positions on the FULL 0..1 range (0 = flush left/top, 1 = flush right/bottom), at most
    ~3 columns x 3 rows in a 1240x820 panel, subs <= ~22 characters. Do not draw future nodes as
    grey ghosts: a node appears on its spoken word, its edge draws in, then pulses. LOOK at the
    final state of every diagram on a contact sheet: crossing wires or two boxes touching = move
    the `at`, not the font.
12. **Text blocks are `chip()` glass tags** (2026-10-27: the flat grey slab + side bar + grey
    text "design of these text blocks are bad"): dark accent-tinted gradient pill, accent
    hairline, glowing dot, white Oswald. Never hand-roll a grey rectangle with a side bar.
10. **A square animation stays square.** `plate_square()` centers it. Never stretch
    1:1 footage to 16:9. The circle then sits in the black pillar instead of on the picture.

## Layouts (engine constants)

```
HERO   (default, 10-27) see below; content left ~1240px, context rail above the PIP.
SPLIT  (on request) slot 1140x950 at (40,46) LEFT + head card 680x950 at x=1200 RIGHT (1:1 HEAD_CROP from
       meta, r=44, accent ring). Slot-local px: title cy≈70, left cx≈330, right cx≈850, chips y≈700, lane y≈800.
FULL   head full-bleed 1920x1080 + transparent overlay 1920x1080, bottom gradient under the captions.
       Author overlays on the RIGHT (x 1300..1900) or a top wordmark (cy≈84); the face stays clean.
HERO   slot 1840x950 full width + head PIP 520x292 at (1330,690) with ring. Keep hero pieces out of
       the bottom-right 520x292; lanes may run behind the PIP.
CIRCLE picture is 1920x1080 (scene() draws in full-frame pixels) + a 400px face disk at
       (1496, 627), 24px off the right, 53px off the bottom, hairline rim, no accent ring.
       No scanlines, no caption line. Keep full-bleed heroes out of that disk
       (x 1496..1896, y 627..1027). A 1:1 plate leaves the disk in the right pillar.
       Optional `index_chip(layer, "01", "SHAPE")` top-left. Never a bottom timecode.
```

Switch layouts on spoken anchors (every ~4–8 s keeps it action packed). Layout change =
0.24 s zoom-dissolve (outgoing view rendered live at the same t, incoming eases 1.035→1.0 scale);
same-layout section cuts whip. **No shake and no hyperframe flash on any section cut** (Kevin
2026-09-30: "I don't like the video shake transition from a different view"). Shake only fires on
`extra_hits` impact beats.

## Pipeline

1. **Workdir + prep** (clip must exist on disk; landscape 1920x1080 expected, others cover-crop):

```bash
bash ".../longform-animated-talking-head/scripts/setup_workdir.sh" <slug>        # projects/<slug>-longform/
cd projects/<slug>-longform
python3 ".../longform-animated-talking-head/scripts/prep_longform_head.py" --clip "/abs/clip.mov" --whisper
```

   Writes `source/talking_head.mp4` (h264 30fps), `audio/narration.{wav,m4a}`, `audio/words.json`,
   `source/meta.json` (`DUR`, `HEAD_CROP` = 680x950 face-anchored crop for the SPLIT card) and
   `renders/head_sheet.jpg`. **View the sheet**: crown and chin inside the card, face ~42% down;
   override `--crop-x/--crop-top` if he drifts. Fix Whisper mishears in `words.json` first
   ("Jev"/"Jeff", product names) — captions, anchors and number beats all read it.

2. **Read the whole transcript** with timestamps and plan sections at spoken anchors
   (`tabs("word", after)` / `tabs_any([...], after)`). SPLIT by default; one FULL for the hook,
   HERO for the grid moments. **CIRCLE** for a generated animation, a screen recording of the
   actual tool, or a single kinetic word (`bleed_word`). Those holds can run for minutes:
   do not invent a layout change every 4–8s when the picture is already moving. Designed
   animation beats still change about once a second. "Action packed and fast paced" on
   SPLIT/HERO: 6–10 live pieces in the slot, a beat on every named product / number /
   punchline, a GIF on every joke or flex. Payoff visuals use `pause_onset()`, not `tabs()`.

3. **Source assets** (before choreography; scripts live in the short skill, call by path):
   - logos: `split-animated-talking-head/scripts/fetch_brand_asset.py` → `assets/logos/`. Proven
     marks (jev, typesafe, hyperedit, obsidian, github, capcut, premiere, youtube, ffmpeg,
     python, openai, gemini, deepseek) sit in `projects/jev-intro-longform-animated/assets/logos`
     — copy them. Claude family = bundled invader/sphinx. Premiere = Wikimedia SVG →
     `qlmanage -t -s 512`. CapCut = s2 favicon (`tool_badge` skips its white punch).
   - GIFs: `fetch_giphy.py --query ... --list`, pick by title, `--id <id> --slug <slug>`; ≤4 s;
     **memey/funny meme moments only** (Kevin 2026-10-24: "mind blown" type GIFs are corny for long-form).
     Skip "mind blown" / "omg" / "wow" / "shocked" / generic "excited"; search recognizable meme scenes
     tied to the line (stonks, this is fine, money printer go brrr, Leo pointing, Michael Scott, SpongeBob).
     eyeball frame 1. One per beat.
   - thumbnails Kevin drops in → `assets/thumbs/thumb_<i>.png` → `thumb_card(i, w)` (crops the
     YouTube card to the 16:9 image, adds a play badge). Screenshots he pastes live in
     `/var/folders/.../TemporaryItems/NSIRD_screencaptureui_*/` — copy with `find -exec cp`
     (a plain `cp` on those paths fails in the sandbox).
   - figures: `fetch_figure.py` whenever a company / niche with famous faces is spoken.
   Build a contact sheet of everything and view it before authoring.

4. **Author `render.py`** from `templates/render_template.py`: `SECT`, `T_*`, `KEYWORDS`,
   `KEY_COL`, bespoke cards, `scene()`, then `run(SECT, scene, punch_words, extra_hits, ...)`.
   Every workflow / system / pipeline explanation is a `flow_card` (or `loop_card` for a cycle)
   from `flow_diagram.py` (rule 11), placed at slot (640, ~500), w=1240, h=820..900.
   Engine cards: `chip / strike_chip / big_text_card / stamp_card / wordmark / ghost_img /
   ticker / draw_code_rain / sparkle_badge / round_logo / tool_badge + x_mark / terminal_card
   (typed lines) / timeline_card (fake NLE, playhead + agent cursor) / workflow_card (nodes
   light up) / thumb_card / demo_card / whisper_line`; plus `media_marks` (gif_card,
   logo_badge, topic_marks, figure_*, counter/odometer), `hyper_edits` (entrance(k), lanes /
   guarded_conveyor, punch_beats, whip, hyperframe), `light_fx` (light_hit, light_rays,
   bloom_orb, speed_streaks) and `claude_marks` (invader / sphinx).
   Beat `t0` = spoken word (max 0.08 s lead via `r(T)`), except a payoff with a pause
   before it (`pause_onset`). On CIRCLE, `scene()` receives a 1920x1080 layer: paste a
   screen recording full-bleed, `plate_square()` a 1:1 render, or `bleed_word()` one
   claim. Markup on a recording (highlight, number, arrow) lands on the spoken word.
   Cold-open atmosphere with
   `place(..., -0.35, dur=0.01)` so each section's first frame is packed; `exit_at` the
   previous big piece ≤0.06 s before the next hero; rotate `entrance(k)`; punches = ONE hero
   word per section (>=8 s apart); `extra_hits` = the 3–5 biggest claims.

5. **Preview, then render**:

```bash
PREVIEW="0.0,2.2,5.5,12.6,21.5,29.5,44.6,52.2" python3 render.py      # frames/out/f<n>.jpg
bash ".../longform-animated-talking-head/scripts/render_parallel.sh" "Readable Name" 4
# → renders/final.mp4 (1920x1080, the clip's audio, crf 16) + ~/Downloads/Readable Name.mp4
```

   Tile the preview frames (3 columns at 960x540) and LOOK before encoding. A still frame
   repeated, a tiny icon in a corner, a square clip stretched wide, a caption line over a
   full-bleed word, or a hit buried inside a spoken word is a re-render, not a note.
   Also check: pieces under the head card / PIP / circle, empty halves (add a terminal,
   lane or badge), a FULL-layout title over the cap, stamps over GIFs. Kevin reviews
   from ~/Downloads; keep the project for re-renders.

## Learnings

- **2026-10-27 Trial Reels engine (`projects/trial-reels-engine-longform/render.py`).** v1
  diagrams (`dm_diagrams.graph_card`) failed review: fixed-size boxes clipped their own text
  ("TRIAL REE"), nodes hung off the panel edge, edges ran as vertical bus lines behind boxes with
  arrows mid-wire, grey ghost nodes for future steps, and small loop rings overlapped their own
  labels. Rebuilt as `flow_diagram.py` (rules 11 + 12). Same edit: Kevin picked HERO as the
  cleanest view, so every SPLIT section became HERO with content shifted +60px and a right rail
  (loop tracker + chapter tag) above the PIP. Real Claude Motion renders
  (`~/claude-motion-faceless-skills/skills/motion-styles/engine`, `node render.mjs --style X
  --size 1080x1080`) inside Instagram phone mockups were a good "show the tool" beat. Disk-light
  render: `render_segs.sh` (24 segments, 6 parallel, encode + delete per segment, mux the
  ORIGINAL clip audio with -c:a copy).

- **2026-10-08 circle cam (Chase AI, ["Claude Now Does Video"](https://www.youtube.com/watch?v=rscb1DgJtNg)).**
  Watched the first 8 minutes plus later beats (Excalidraw walkthrough, a GitHub skill
  README, the closing square animation). Measured: 1920x1080, 6.6 cuts/min, median shot
  1.0s, and three holds of 174s, 141s and 61s. The fast cuts are the designed animation.
  The holds are a screen recording of the coding agent and the tool itself, with the same
  face disk the whole time. Disk is 400px, center about (1696, 827). The face sits at
  x=0.88, y=0.74, about 18% of the frame tall, and it is on screen 99% of the time.
  No caption track. 43 pauses longer than 0.35s in those 8 minutes (182 wpm), which
  is why `pause_onset()` exists. Square generated clips stay 1:1 in black pillars
  and the disk lives in the right pillar.
  His own on-screen notes, which are now rules 8–10: land the loudest hit in the silence
  before the last line (a hit on the word was "swallowed by the narration"); the same
  picture sitting for 7s is a fail; a tiny corner icon is a fail, the object is big,
  centered, and a negation is a strike through it; pull a contact sheet and look before
  calling it done. Do not copy his take-counter / timecode HUD. SPLIT is still the layout
  when Kevin is talking to camera.

- **2026-09-21 v1 → v2 (JEV intro):** dark hook + "?" = wrong for long-form ("it just needs to
  hook the user into the actual topic"); bottom timeline strip = "truly pointless". Both
  removed; slot/head card grew to 950 tall. Approved: layout switching, phrase captions on
  the line, X-marks over CapCut/Premiere on the spoken word, GitHub fork grid on "hundreds",
  thumbnails on "three video updates", Jev slam + rays, fake timeline, workflow nodes, code
  tree, demo card + "INSANE" stamp. Then: SPLIT named the favourite layout for talking.
- HEVC .mov from Kevin's recorder: transcode to h264 30fps first (cv2 reads sequentially,
  seeks only at a RANGE start). 1572 frames render in ~3 min across 4 chunks.
- Long-form Whisper: `small.en` (base mishears more on a long clip).
- 10-minute clips: ~60–90 sections; ~0.15 s/frame/process → 18k frames ≈ 12 min on 4 chunks.
- **2026-09-25 VIKTOR intro** (`projects/viktor-intro-longform/render.py`): Kevin's raw clip had
  logo SLATES baked in (black frame + product logo, no face) at 35.4–37.9 s and 75.5–78.0 s → the head
  card rendered black. Scan every source for dark runs first (`frame[::8,::8].mean() < 40`) and put those
  spans on `"SOLO"` (any name other than SPLIT, FULL, HERO, or CIRCLE = full-width slot, no head, no PIP); boundaries must
  land on the first real frame. Name-drop reveal + five-fields board went there. Also: `wordmark()`
  clips tall Oswald digits / its `sub` overlaps at big sizes → use a textbbox-sized `big_num()` + a chip;
  Oswald has no ✓ glyph (Menlo does, so terminals are fine); white-bg Wikimedia logos need a white-trim
  crop before `logo_badge(punch=False, fill=WHITE)`.

## Examples

**Example 1: long-form intro hyper-edit**
User says: "Edit this landscape intro I recorded, action packed like the JEV intro." (path to a .mov)
Actions:
1. `bash scripts/setup_workdir.sh <slug>` then `prep_longform_head.py --clip "/abs/clip.mov" --whisper`; view `renders/head_sheet.jpg`, fix mishears in `audio/words.json`.
2. Read the transcript, plan sections on spoken anchors: SPLIT by default, one FULL hook, HERO for grids.
3. Fetch logos, GIFs, figures, thumbnails; LOOK at a contact sheet.
4. Author `render.py` from `templates/render_template.py`, `PREVIEW=...`, then `scripts/render_parallel.sh "Readable Name" 4`.
Result: `renders/final.mp4` (1920x1080, the clip's audio) plus `~/Downloads/Readable Name.mp4`.

**Example 2: full 10-minute episode**
User says: "Hyper-edit my full YouTube episode."
Actions:
1. Same pipeline; plan ~60-90 sections, scan the source for baked-in logo slates first.
2. Render on 4 chunks (~12 min for 18k frames).
Result: a long-form animated edit ready for Kevin's review in ~/Downloads.

## Troubleshooting

Error/Symptom: `prep_longform_head.py` exits with "clip not found".
Cause: the clip path doesn't exist on disk.
Solution: pass an absolute path to an existing file with `--clip`.

Error/Symptom: slow or broken frame reads from Kevin's recorder file.
Cause: HEVC .mov (cv2 reads sequentially, seeks only at a RANGE start).
Solution: prep transcodes to h264 30fps first; always render from `source/talking_head.mp4`.

Error/Symptom: the head card renders black for a few seconds.
Cause: logo slates (black frame + product logo, no face) baked into the raw clip.
Solution: scan for dark runs (`frame[::8,::8].mean() < 40`) and put those spans on `"SOLO"` (full-width slot, no head, no PIP), boundaries on the first real frame.

Error/Symptom: face cut off in the SPLIT card.
Cause: Kevin drifts out of the face-anchored `HEAD_CROP`.
Solution: check `renders/head_sheet.jpg` and override `--crop-x/--crop-top`.

Error/Symptom: big digits clipped or `sub` overlapping in `wordmark()`; a missing check glyph.
Cause: tall Oswald digits at big sizes; Oswald has no check glyph.
Solution: use a textbbox-sized `big_num()` + a chip; use Menlo for check marks (terminals are fine).

Error/Symptom: `cp` of a pasted screenshot fails.
Cause: sandbox blocks a plain `cp` on `/var/folders/.../TemporaryItems/NSIRD_screencaptureui_*/` paths.
Solution: copy with `find ... -exec cp`.

Error/Symptom: a white box around a Wikimedia logo.
Cause: white-background source image.
Solution: white-trim crop before `logo_badge(punch=False, fill=WHITE)`.

