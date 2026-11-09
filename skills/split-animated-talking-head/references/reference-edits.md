# Reference edits (what each gold-standard render did)

Moved out of SKILL.md for length. SKILL.md keeps the ranking and the locked numbers/colors; this file keeps the detail of what made each reference land.

**BEST EDIT YET (Kevin 2026-09-26):** `projects/social-agents-animated/render.py`
is now the top reference (it outranks gitnexus). What made it: the user's b-roll used three ways
(banner crop as the reveal on the product name; a live terminal card that starts zoomed on the
command, then pulls back and scrolls with the output; single-line "LIVE FROM THE REPO" crops,
left part of the line only so the text stays readable). Spoken feature lists become a ticking
checklist card with one bespoke visual per item (real reel covers/thumbnails from
brand-content + Downloads, mock inbox / caption / hashtag / SEO-climb cards). GIFs whose burned-in
text matches the spoken line word for word. Stamps only on each section's dramatic beat.
Reuse its Broll / crop_img / strip_card / broll_view(zoom=) helpers whenever b-roll is supplied.

**STATUS QUO (Kevin 2026-09-19, "SOOOOO GOOOOD that should be the new status quo"):**
`projects/gitnexus-animated/render.py` is the current gold reference. Everything
below still applies; what made it land: Luckiest Guy captions resting on the accent
line with a tight glow, the user's own screen recording as the b-roll hook (mystery
"?" over it) and as per-word crop cuts later, a meme beat matched to the spoken line
(Hangover calculation meme on "understand any piece of code") followed by a custom
motion piece on the next word (spinning wireframe `globe_card` on "planet"), terminals
that type the spoken action, a legend card lighting up per component, stamps on the
punch words, a kinetic headline + lower third + counter. Match that energy on every cut.


## Look, type and billboard locks (full text)

**LOOK LOCK (Kevin 2026-09-10, china-robots density + github-research-agent wash):**
gold-standard density / titles / GIFs: china-robots (render.py no longer on disk; use social-agents / gitnexus as code refs).
Slot **brightness** lock: `projects/github-research-agent-animated/render.py`
(Kevin 2026-09-10: "background is too dark" on the near-black CHAR wash).
Copy china-robots energy, but use the lifted graphite `textured_bg` — lift
patches, stronger accent glow, `slot_vignette(..., a=22)`. Do **not** ship
Megan paper/sage/coral, and do **not** use near-black CHAR=(14,15,18) as the
slot wash. Locked colors (override after exec of `animation_assets_and_beats.py`).
**Type lock (Kevin 2026-09-15 + 2026-09-19):** overlay / component text is **Oswald Bold**
(`templates/fonts/Oswald-Bold.ttf`, loaded via `templates/fonts.py` as `AR`).
Title cards, chips, huge_word, counters, name plates, ghosts. **Kinetic captions
are Luckiest Guy** (`templates/fonts/LuckiestGuy-Regular.ttf`, `CAP` in fonts.py):
CapCut-style chunky comic caps, white fill (KEY_COL fill on keywords), 7px black
stroke, no drop shadow (Kevin 2026-09-19 "DOG" screenshot). Copy both ttfs.
Never Arial in the slot. Terminals / code rain / tickers stay **Menlo** (`ML`)
— Menlo.ttc must be opened with `index=0` or glyphs double-print. Oswald is
the condensed display face (the big AND over a UI). Copy `fonts.py` +
`fonts/Oswald-Bold.ttf` into every workdir.

```
INK=(10,11,14)  SILVER=(198,204,214)  STEEL=(92,98,108)
GRAPHITE=(36,38,46)  CHAR=(48,50,58)
NEON=(57,255,132)  ORANGE=(255,122,24)  RED=(255,48,64)
CORAL=ORANGE  PAPER=GRAPHITE
AR=Oswald Bold    CAP=Luckiest Guy (captions only)    ML=Menlo (terminals only)
```

Captions: Luckiest Guy, white fill, `KEY_COL` neon/orange/red on keywords, 7px
black stroke, no shadow (2026-09-19 lock; the older Oswald ~66px silver caption is superseded). Chips: graphite + accent
bar, Oswald. Cards: graphite, Oswald. Slot accent bars like
china-robots (orange/neon/red per section). Hero titles are **~960px wide**.
User B-roll in the slot should fill ~1000×500, not a small inset.

**TOPIC LOGO CONVEYOR (Kevin 2026-09-10 — staple).** The horizontal scroll
of brand icons tied to the video (voice-agents: OpenAI / Cursor / Docker /
Cloudflare / … under the faces) is required on every cut. Not optional
decoration. See `5d` below.

**INTRO BILLBOARD (Kevin 2026-09-14):** the hook / cold-open must read from
across the room. Giant numbers, giant figure circles, giant logos — not a
contact sheet of 150–220px heads under a title. See `5b` size lock. 150px
rounds are banned anywhere.

Do **not** call HeyGen. Do **not** use this skill when the user wants Megan,
Danny, or Kevin generated. That is `split-animated-short`.
