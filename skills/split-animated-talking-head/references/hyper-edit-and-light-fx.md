# Hyper-edit layer and light FX (full steps 7b and 7d)

Full text of pipeline steps 7b and 7d, moved out of SKILL.md for length. SKILL.md keeps the locked rules; this file has every helper call and parameter. Where this older text says an effect fires "on every keyword punch", the later 2026-09-12 rule wins: impact effects only on each section's ONE dramatic beat, punches via `punch_beats()`.

7b. **HYPER-EDIT LAYER (locked, Kevin 2026-09-05)** — `templates/hyper_edits.py`.
   The motion graphics are the *content*; the hyper-edit is the *cut*. Every
   video gets all of these, deterministic in `t`:
   - **Punch-ins and shake go on the ANIMATION SLOT, never the talking head
     (Kevin 2026-09-05).** Per frame: `layer = punch_zoom(layer,
     punch_scale(t, PUNCH_T, amt=0.045))` then `sx, sy = shake_offset(t,
     HIT_T, amp=14)` and `frame.alpha_composite(layer, (sx, LAYER_Y + sy))`.
     **Punches are RARE (Kevin 2026-09-12: "far too many zoom punch
     effects, annoying to watch").** `PUNCH_T = punch_beats(words,
     PUNCH_WORDS)`: hand-pick ONE hero word per section (the product name,
     the number, the CTA word), >=8 s apart, max 6/min, amt 0.045. Never
     `keyword_onsets(words, KEYWORDS)` for punches; KEYWORDS only colour
     captions. `speed_streaks` rides the same short list. Shake = section
     cuts + at most 3 claims. The band is composited at a fixed
     `(12, BAND_Y)` with no zoom or offset, always.
   - **Hyperframes = 1–2 frame accent inserts on cuts.** `hyperframe(frame, t,
     CUT_T, FPS, region=(0, LAYER_Y, W, AH))` cycles white → ink → invert →
     RGB-split so no two cuts flash the same. Animation slot only; the band
     never flashes. Never on the hook (frame 0 stays packed and clean).
     Never on an odometer while it is counting (Kevin 2026-09-15: the
     constellation overlay sat on top of the digits).
   - **Whip cuts between sections.** Replace the flat white flash with
     `whip_wipe(prev_layer, layer, lt / 0.16, direction=whip_dir(name))` for
     the first 0.16s of a section (outgoing scene pushes out motion-blurred,
     incoming pushes in). Whip **or** hyperframe on a given cut, not both.
   - **Shake on impact.** `HIT_T` = section cuts plus the 3 to 5 biggest
     claims; ≤0.26s, decays; applied to the slot offset (above).
   - **Spring / overshoot entrances.** `spring_preset(t, "snappy"|"bouncy"|
     "heavy")`, `ease_back_out`, `slam_in(img, p)` for hero numbers (1.6× →
     1 with overshoot). Rotate: not every card gets the same pop. Use
     `entrance(k)` for GIFs and cards so consecutive pieces differ, and keep
     `light_hit` / shake / hyperframe for the single dramatic beat of a
     section (Kevin 2026-09-12).
   - **Freeze hit** (`freeze_hit(band, p)`) for a record-scratch beat
     ("so I'm sorry CapCut"): band freezes, zooms 12%, paper tint + ink border
     for ~0.5s, then resumes. Max one per video.
   - **Text fx**: `count_up(300, p, suffix="%")` on stats (expo.out),
     `typewriter(text, p)` in terminals, `highlight_sweep` under the claim,
     `caption_impact(t, onset, key)` scales the caption with a squash bounce.
   Density check: the hyper-edit should make a 60s video feel like it has
   ~40 cuts even though the band is one continuous take.

7d. **LIGHT FX LAYER (locked, Kevin 2026-09-10).** `templates/light_fx.py`.
    The slot should feel lit, not flat cards on a flat wash. Every video
    gets a cheap light pass on the **animation slot only** (never the band):

    ```python
    from light_fx import (
        scanlines, hud_scan, neon_grid, slot_vignette,
        bloom_orb, rim_pulse, light_hit, light_rays, speed_streaks,
        caption_bloom,
    )
    # atmosphere — every frame, under or just over the graphics
    scanlines(layer, t)
    hud_scan(layer, t, accent)
    neon_grid(layer, t, STEEL)
    bloom_orb(layer, invader_x, invader_y, 200, accent, a=70)
    # hits — same t0 as the spoken word / GIF land / title slam
    light_hit(layer, 540, 300, t, t0, ORANGE)   # ring + sparks + flare
    speed_streaks(layer, t, PUNCH_T, NEON)
    slot_vignette(layer)
    # caption glow (draw on the canvas BEFORE the word)
    caption_bloom(frame, x, y, tw, 66, KEY_COL[wd] if key else SILVER)   # tight halo (word height), a<=40
    ```

    Atmosphere (scanlines + HUD scan + floor grid + a bloom behind the
    invader / hero) is on from frame 0. `light_hit` fires on every keyword
    punch, section cut, GIF land, and title slam. `light_rays` is reserved
    for the CTA / one hero flex — not every section. Copy `light_fx.py`
    into the workdir with the other templates.
