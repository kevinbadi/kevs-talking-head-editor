# Kev's Talking Head Editor

The Claude Code skills I use to edit my talking-head videos, short form and long form. Free and open source.

Hand Claude a raw clip of you talking to camera. It:

1. **Cuts the ums, uhs, false starts and dead air** (`tools/filler_cut.py`: filler-aware Whisper + a silence map, then a clean ffmpeg jump-cut).
2. **Reads your whole transcript** to understand what the video is about.
3. **Pulls GIFs and memes from the Giphy API** that match what you're saying, plus real logos for every product you name.
4. **Syncs everything to your voice**: kinetic captions, animations, text on screen, Apple-style number counters, punch-ins, whips and light hits, all landing on the spoken word.

Everything renders locally in Python (PIL + OpenCV + ffmpeg). No paid video API, no HTML overlay.

| Skill | Output | Layout |
|---|---|---|
| `split-animated-talking-head` | **Short form**, 1080x1920 (Reels / TikTok / Shorts) | Animation slot on top, your head in a rounded band below, captions sitting on the split line |
| `longform-animated-talking-head` | **Long form**, 1920x1080 (YouTube) | SPLIT (animation left, your head card right), FULL and HERO layouts switched per section |

## Install

```bash
git clone https://github.com/kevinbadi/kevs-talking-head-editor
cd kevs-talking-head-editor
./install.sh                  # -> ~/.claude/skills
# or: ./install.sh /path/to/your/project
pip install -r requirements.txt
```

You also need `ffmpeg` on your PATH. Put a free Giphy key in a `.env` in your project folder:

```
GIPHY_API_KEY=your_key_here
```

## Use it

Open Claude Code in your project folder and say:

> Here's my talking head `~/Downloads/take.mp4`. Cut the ums and dead air, then make the split animated short.

or, for YouTube:

> Edit `~/Downloads/take.mov` as a long-form talking-head video.

Claude creates `projects/<slug>-animated/` (or `-longform/`), cuts the take, preps the head crop, sources logos and GIFs, writes a `render.py` for your script, renders the frames and muxes your original audio. The finished file is `renders/final.mp4`.

### The filler cut on its own

```bash
python3 tools/filler_cut.py transcribe --clip /abs/path/take.mp4 --workdir .
#   read raw/words_indexed.txt; [F] = auto-flagged filler. Note any restarts to drop.
python3 tools/filler_cut.py cut --clip /abs/path/take.mp4 --workdir . --cut "36-43,49-52"
#   -> raw/cut.mp4, then re-transcribes it and lists anything filler-like that's left
```

Tip: always look at that re-transcription. Whisper sometimes hides a restart ("is my number one, uh, is my number one") inside one long word on the first pass. If it does, use a hand keep-list like `examples/kevs-talking-head-editor-short/recut.py`.

## Example

`examples/kevs-talking-head-editor-short/render.py` is the render for the short where I introduce this skill (77 s raw take cut to 42 s): Claude hook, #1 style counter, the product name as kinetic type, transcript scan, Giphy API + GIF grid, an editing timeline syncing to the voice, a ticking checklist, a watch-time chart and the comment CTA. Use it as a starting point for your own `render.py`.

## What's inside

```
skills/split-animated-talking-head/    short form: SKILL.md, prep + fetch scripts, compositor templates, references
skills/longform-animated-talking-head/ long form: SKILL.md, prep + setup scripts, layout engine
tools/filler_cut.py                    um / dead-air jump-cut pass
examples/                              a real render.py + the hand keep-list re-cut
```

The `references/learnings.md` log is every correction from months of real edits. It's why the defaults look the way they do.

## License

MIT. Fonts: Oswald and Luckiest Guy (SIL Open Font License / Apache 2.0). Claude and Anthropic marks belong to Anthropic; GIFs belong to their creators via Giphy.
