# Apple counter spec (Kevin 2026-09-29)

Detailed spec for `templates/apple_counter.py`, moved out of SKILL.md step 6b. `counter_card` and `odometer_card` in `media_marks.py` both delegate to it.

- **SF Pro Display Bold digits** (macOS `/System/Library/Fonts/SFNS.ttf`,
  variable: weight 700, optical size 96) in tabular cells, on a frosted dark
  glass card with a hairline top highlight and a faint accent glow. Label =
  tracked caps in SF Pro Text with an accent dot. No boxes, wells, cages,
  progress bars or orange strips (the old boxed-reel odometer is dead).
- **Rolling digits:** a place that changes slides up a short hop (0.34 of
  the cell) while the old digit fades out and the new one fades in, both
  edge-faded so nothing pokes above or below the line. A place spinning
  faster than about one digit per frame renders as ONE speed-blurred digit
  (true vertical box blur), never a half-and-half crossfade: that flickers
  as doubled digits.
- **Odometer carry:** a place rolls only while every place below it is on 9
  and rolling, so the count never shows the next digit early (no
  "2,992,000,000" on the way to 2 billion).
- **No leading zeros:** a new leading digit and its comma slide + fade in as
  the value reaches them, and the figure re-centers smoothly. Frame 0 of a
  count shows a clean "0", not "0,000,000,000".
- **Full figures with live commas.** `2,000,000,000` not `2B`. Compact
  "2B" / "1.5M" is a chip or caption only, never the hero count.
- **Easing:** ≥10k eases in-out so thousands -> millions -> billions
  visibly tick; smaller figures expo-out and settle. One tiny scale breath
  as it lands, never a pulse.
- **Counts vs years:** a bare 1900-2099 with no label is treated as a year
  (no comma, rolls from value-40). Any counted figure ("2000 person academy",
  "1950 members") passes `"style": "count"` or a label and counts from zero
  with a comma (Kevin 2026-09-29: "2000" started at 1960).
- **Timing.** Park the card at 0 up to ~0.2s before the number word (or
  from the section start as atmosphere). Count **on** the spoken number,
  land on the unit / scale word ("stars", "billion"). Max lead 0.1s.
- **The counter is the only big piece while it counts.** Exit GIFs, the
  invader, the conveyor and hyperframe punches off the card; a light_hit
  ring on the landing word is fine.
- Sizes: hero ≥10k `w=1000, h=400`; smaller heroes `w=440-560, h=300-320`.

## Authoring a hero count by hand

Author the hero beat by hand:

```python
NUM = {b["t"]: b for b in number_beats(words)}
bt = NUM[1.52]   # "two billion"
t0 = trel("two", a)          # spin starts on the number
t_land = trel("billion", a) + 0.15
p = 0.04 if lt < t0 else clamp01((lt - t0) / max(0.12, t_land - t0))
place(layer, odometer_card(bt, p, h=400, label="tokens / day"),
   540, 200, lt, trel("spend", a), dur=0.22, exit_at=t0 + 2.2)
```
