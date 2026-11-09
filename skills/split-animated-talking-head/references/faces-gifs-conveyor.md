# Faces, reaction GIFs and the topic conveyor (full steps 5b to 5d)

Full text of pipeline steps 5b, 5c and 5d, moved out of SKILL.md for length. SKILL.md keeps the commands and the locked rules; this file has the niche map, sourcing order, choreography helpers and size floors in detail. Paths written as `.../split-animated-talking-head/` mean this skill folder.

5b. **SOURCE THE FACES** (Kevin 2026-09-05). Whenever the transcript names a
   company, model, or niche that has famous people behind it, put those people
   on screen — viewers who recognize Dario, Sam, Elon, GaryVee, Hormozi lock in
   harder than they do on a logo. Curated niche map lives in
   `scripts/fetch_figure.py` (`--list`): `claude`/`anthropic`/`opus`/… →
   Anthropic founders (Dario + Daniela Amodei, Jack Clark, Jared Kaplan, Chris
   Olah, Tom Brown); `spacex` → Musk, Shotwell, Mueller; `openai`/`chatgpt` →
   Altman, Brockman, Sutskever, Murati…; `marketing` → GaryVee, Hormozi, Godin,
   Neil Patel, Brunson, Kotler, Ogilvy; `business`/`founders`/`money` → Buffett,
   Bezos, Jobs, Musk, Cuban, Hormozi, Naval, Codie, Martell, Thiel; `sales` →
   Cardone, Belfort, Hormozi, Ziglar, Tracy, Robbins; plus `google`, `nvidia`,
   `meta`, `microsoft`, `apple`, `tesla`, `amazon`, `xai`.

```bash
python3 ".../split-animated-talking-head/scripts/fetch_figure.py" --niche claude --top 4
python3 ".../split-animated-talking-head/scripts/fetch_figure.py" --niche openai --niche marketing
python3 ".../split-animated-talking-head/scripts/fetch_figure.py" --name "Jensen Huang" --wiki Jensen_Huang --x nvidia --role "NVIDIA CEO"
# → assets/figures/<slug>.png (800x800 face-cropped) + <slug>.json {name, role, credit}
```

   Sources: Wikipedia/Commons original → current X avatar (unavatar) →
   Wikidata name-match last (it has returned the wrong "Tom Brown"; eyeball
   any `warn` line). **Always view the fetched portraits** (contact sheet)
   before choreographing; swap with `--name/--x --force` if a crop is a
   stranger or a decade old. Choreography (`templates/media_marks.py`):
   `figure_row(layer, slugs, cx, cy, lt, t0, place, names=True)` for a
   founders lineup (2 faces on the intro, 2–3 later, staggered, alternating tilt),
   `figure_spotlight(layer, slug, cx, cy, lt, t0, place)` when ONE person is
   the beat (hero portrait + name plate + role), `figure_card(slug, w=380)` /
   `figure_round(slug, 360, ring=CORAL)` as marks. **Face lands on the spoken
   word** (`word_onset(words, "anthropic")`), never early. Pair the row with
   the brand mark (Claude → invader + sphinx beside the Amodeis). Names in
   plates are first names for rows, full name + role for spotlights.

   **Figure circle size lock (Kevin 2026-09-14: "make them much larger…
   intro screens should be eye catching with big #s, figures, logos"):**
   the 150–220px rounds that kept shipping (phone-farm, anything-to-explain,
   open-source-trap hook) read as thumbnails, not icons. Floor:
   - **Hook / intro / cold-open:** these ARE the billboard. 1 face →
     `figure_spotlight(..., size=560)` or `figure_round(..., 520–620)`.
     2 faces → `figure_row(..., size=480, gap=12)`. Never 3+ tiny heads on
     the first section — pick the two most iconic. Pair with a 960-wide
     title **or** a `odometer_card` / `counter_card(..., h=440)` **or** a 400–520px logo
     badge; the slot should feel huge, not busy. Conveyor marks stay 110–140
     and sit under the giants, they do not replace them.
   - **Body sections:** single circle ≥280; 2–3-up row ≥320. Spotlight ≥480.
   - **Banned:** `figure_round(..., 150)` / `size=170` / `size=190` anywhere.
     If a 3-up row cannot fit at 320, drop to 2 faces and go bigger.
   Max one lineup per section. Intro faces may be the hero for up to 2.5s;
   later sections treat extra faces as supporting marks, still at the floor
   above — never shrunk to make room for a fourth.

5c. **PULL REACTION GIFs** (Giphy API, Kevin 2026-09-05). Punchlines, flexes,
   shocks and "I'm sorry CapCut" jokes get a real reaction GIF, not a text pill.
   `GIPHY_API_KEY` is in `.env`; the dashboard's favorited
   allow-list (`gifs` table) is available via `--favorites`.

```bash
python3 ".../split-animated-talking-head/scripts/fetch_giphy.py" --query "mind blown" --list   # look first
python3 ".../split-animated-talking-head/scripts/fetch_giphy.py" --query "mind blown" --slug mind-blown --pick 1
python3 ".../split-animated-talking-head/scripts/fetch_giphy.py" --favorites --query money --slug money-rain --mark-used
# → assets/gifs/<slug>/f0001.png … @30fps (≤4s, 720px wide) + meta.json
```

   Pick by title from `--list` (Kramer / Jon Stewart "mind blown" over a
   12-second anime loop). **Eyeball frame 1** before using: drop GIFs with
   slurs/subtitles, the wrong person, or a joke that misses the line.
   Play with `gif_card(..., w=400, frame="round")` for pairs under a title.
   Rules (china-robots lock): **one GIF per beat, 5–8 per video**, never the
   hero for >2.5s, never covering a 960px title card. Later-section stack is
   **title at cy≈125, pair of ~400px GIFs at cy≈450** (left/right). Hook
   frame 0 is the figure/number/logo billboard — do not cover it with a GIF
   pair unless the hook *is* B-roll. GIF audio is never mixed in. Rating pg-13.

5d. **TOPIC LOGO CONVEYOR — staple (Kevin 2026-09-10).** Every video gets a
   full-width horizontal scroll of the icons *associated with this edit*
   (the stack, products, companies, tools in the story — not random logos).
   Voice-agents showed OpenAI / Cursor / Docker / Cloudflare / … sliding
   under the faces. China-robots used Unitree / Tesla / NVIDIA / Meta /
   Boston Dynamics on "hardware + AI". That lane is the touch Kevin wants
   every time. Conveyor marks stay 110–140px; they are the stream, not the
   intro hero. On the hook, also `place()` 1–2 **giant** logos (360–520px)
   as billboard pieces next to the big figures / number (Kevin 2026-09-14).

   Fetch 5–8 real marks in step 5 (`fetch_brand_asset.py`). Punch white
   pads. Then one lane, one y-band, via `guarded_conveyor`:

```python
from media_marks import topic_marks
marks = topic_marks(["openai", "cursor", "docker", "cloudflare", "vapi"], size=120)
# y is authored cy; helper adds PACK_DY like china-robots
guarded_conveyor(layer, 400 + PACK_DY, max(0, lt - t0), marks,
                 conveyor_marks, name="topic-lane", speed=180, gap=22)
```

   Rules:
   - **At least one topic lane per video.** Cold-open it on the hook when
     the stack is the point, or enter on the spoken product/category beat.
   - 5–8 marks, ~110–130px, graphite badges (dark slot). Full slot width.
   - **One moving stream at a time** (already locked). The lane owns its
     y-band; no second conveyor / orbit on the same band; `lanes.reset()`
     every frame.
   - Marks must match the video. Do not fill with leftover icons from
     another project. Eyeball each PNG (wrong logo / broken SVG → drop).
   - Do not sit the lane on the caption line. Center ≤ `770 - size/2 - 10`
     after PACK_DY (half-sliced icons are a known fail).
