#!/usr/bin/env python3
"""Raw-take cleanup: cut um/uh, false starts and dead air BEFORE prep_talking_head.py.

Every talking-head edit gets this pass first: ums, uhs, false starts and dead air out.


Step 1, transcribe (filler-aware Whisper + silence map, prints an indexed transcript):
    python3 filler_cut.py transcribe --clip /ABS/clip.mov --workdir .
Read raw/words_indexed.txt. [F] = auto-flagged filler. Pick the extra indices to drop
(false starts, restarts, repeated phrases, off-camera asides, pre-roll mumbles).

Step 2, cut (auto fillers + your picks, carve silences, render raw/cut.mp4, re-check):
    python3 filler_cut.py cut --clip /ABS/clip.mov --workdir . --cut "0-5,96-98,137"

Then prep the band from raw/cut.mp4 and mux the final audio from raw/cut.mp4.
"""
import argparse, json, os, re, subprocess, sys

FILLERS = {"um", "umm", "uh", "uhh", "uhm", "erm", "er", "hmm", "mm", "mhm", "ah", "eh"}
PROMPT = ("Um, uh, so, like, um, I mean, uh, you know. "
          "Creator OS, Claude, Claude Code, Anthropic, Opus, Sonnet, GitHub, ChatGPT, OpenAI, Gemini.")
PRE, POST = 0.06, 0.12          # pad around kept word runs
SIL_DB, SIL_MIN = -40, 0.32     # silencedetect: carve any gap longer than this
KEEP_GAP = 0.12                 # breath left behind where a silence was carved


def norm(w):
    return re.sub(r"[^a-z']", "", w.lower())


def sh(cmd):
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def wav16(src, dst):
    sh(["ffmpeg", "-y", "-i", src, "-vn", "-ac", "1", "-ar", "16000", dst])


def transcribe(wav, prompt):
    from faster_whisper import WhisperModel
    m = WhisperModel("small.en", compute_type="int8")
    segs, _ = m.transcribe(wav, word_timestamps=True, vad_filter=False, initial_prompt=prompt)
    return [[w.word.strip(), round(w.start, 3), round(w.end, 3), round(w.probability, 3)]
            for s in segs for w in s.words]


def silences(wav, W):
    """Union of three dead-air detectors. Energy alone fails on a noisy room (2026-11-09 take:
    floor ~-32 dB, -40 dB found nothing), so Silero VAD gaps and Whisper word gaps join in."""
    err = subprocess.run(["ffmpeg", "-i", wav, "-af", f"silencedetect=noise={SIL_DB}dB:d={SIL_MIN}",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    gaps = list(zip(st, en))
    try:
        from faster_whisper.audio import decode_audio
        from faster_whisper.vad import get_speech_timestamps, VadOptions
        sp = get_speech_timestamps(decode_audio(wav, sampling_rate=16000),
                                   VadOptions(threshold=0.5, min_silence_duration_ms=250,
                                              speech_pad_ms=0, min_speech_duration_ms=80))
        sp = [(t["start"] / 16000, t["end"] / 16000) for t in sp]
        if sp:
            gaps += [(0.0, sp[0][0])] + [(sp[i][1], sp[i + 1][0]) for i in range(len(sp) - 1)]
    except Exception as e:
        print(f"VAD skipped: {e}")
    if W:
        gaps += [(0.0, W[0][1])] + [(W[i - 1][2], W[i][1]) for i in range(1, len(W))]
    gaps = sorted((round(s, 3), round(e, 3)) for s, e in gaps if e - s >= SIL_MIN)
    m = []
    for s, e in gaps:
        if m and s <= m[-1][1]: m[-1][1] = max(m[-1][1], e)
        else: m.append([s, e])
    return [tuple(x) for x in m]


def parse_idx(spec):
    out = set()
    for part in filter(None, (p.strip() for p in (spec or "").split(","))):
        if "-" in part:
            a, b = map(int, part.split("-"))
            out.update(range(a, b + 1))
        else:
            out.add(int(part))
    return out


def cmd_transcribe(a):
    raw = os.path.join(a.workdir, "raw")
    os.makedirs(raw, exist_ok=True)
    wav = os.path.join(raw, "raw16k.wav")
    wav16(a.clip, wav)
    W = transcribe(wav, a.prompt)
    json.dump(W, open(os.path.join(raw, "raw_words.json"), "w"))
    sil = silences(wav, W)
    with open(os.path.join(raw, "silences.txt"), "w") as f:
        f.writelines(f"{s} {e}\n" for s, e in sil)
    lines = []
    for i, (w, s, e, p) in enumerate(W):
        flag = "[F]" if norm(w) in FILLERS else "   "
        gap = s - W[i - 1][2] if i else s
        pause = f"  <-- {gap:.2f}s pause" if gap >= 0.6 else ""
        lines.append(f"{i:4d} {flag} {s:7.2f}-{e:6.2f}  {w}{pause}")
    open(os.path.join(raw, "words_indexed.txt"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    nf = sum(1 for w in W if norm(w[0]) in FILLERS)
    print(f"\n{len(W)} words, {nf} auto-flagged fillers, {len(sil)} silences >{SIL_MIN}s. "
          f"Pick false starts / restarts / asides, then run `cut --cut ...`.")


def build_keep(W, cut, sil, min_keep):
    runs, cur = [], None
    for i, (w, s, e, p) in enumerate(W):
        if i in cut:
            if cur: runs.append(cur); cur = None
            continue
        cur = [s, e] if cur is None else [cur[0], e]
    if cur: runs.append(cur)
    out = []
    for x0, y0 in ([max(0, s - PRE), e + POST] for s, e in runs):
        pieces = [[x0, y0]]
        for ss, se in sil:
            cs, ce = ss + KEEP_GAP / 2, se - KEEP_GAP / 2
            if ce - cs <= 0.05:
                continue
            nxt = []
            for x, y in pieces:
                if cs > x and ce < y: nxt += [[x, cs], [ce, y]]
                elif cs <= x < ce < y: nxt.append([ce, y])
                elif x < cs < y <= ce: nxt.append([x, cs])
                elif cs <= x and y <= ce: pass
                else: nxt.append([x, y])
            pieces = nxt
        out += pieces
    out.sort()
    m = []
    for x, y in out:
        if m and x <= m[-1][1] + 0.02: m[-1][1] = max(m[-1][1], y)
        else: m.append([x, y])
    return [[round(x, 3), round(y, 3)] for x, y in m if y - x >= min_keep]


def swallowed(W, cut, keep):
    """Kept words that ended up mostly outside the keep segments (silencedetect ate a soft word)."""
    bad = []
    for i, (w, s, e, p) in enumerate(W):
        if i in cut or e <= s: continue
        cov = sum(max(0, min(e, y) - max(s, x)) for x, y in keep)
        if cov / (e - s) < 0.5: bad.append((i, w, s))
    return bad


def cmd_cut(a):
    raw = os.path.join(a.workdir, "raw")
    W = json.load(open(os.path.join(raw, "raw_words.json")))
    sil = [tuple(map(float, l.split())) for l in open(os.path.join(raw, "silences.txt")) if l.strip()]
    cut = parse_idx(a.cut)
    if not a.no_auto:
        cut |= {i for i, w in enumerate(W) if norm(w[0]) in FILLERS}
    cut -= parse_idx(a.keep)
    keep = build_keep(W, cut, sil, a.min_keep)
    for i, w, s in swallowed(W, cut, keep):
        print(f"WARN kept word #{i} '{w}' @{s:.2f}s is mostly carved out: play it, then pass --keep {i} "
              f"or pull the segment start back by hand in raw/keep.json")
    json.dump(keep, open(os.path.join(raw, "keep.json"), "w"))
    parts, ins = [], []
    for k, (x, y) in enumerate(keep):
        d = y - x
        parts.append(f"[0:v]trim=start={x}:end={y},setpts=PTS-STARTPTS[v{k}]")
        parts.append(f"[0:a]atrim=start={x}:end={y},asetpts=PTS-STARTPTS,"
                     f"afade=t=in:d=0.012,afade=t=out:st={max(0, d - 0.015):.3f}:d=0.015[a{k}]")
        ins.append(f"[v{k}][a{k}]")
    fc = ";".join(parts) + ";" + "".join(ins) + f"concat=n={len(keep)}:v=1:a=1[v][a]"
    fpath = os.path.join(raw, "cut_filter.txt")
    open(fpath, "w").write(fc)
    out = os.path.join(raw, "cut.mp4")
    sh(["ffmpeg", "-y", "-i", a.clip, "-filter_complex_script", fpath, "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", out])
    dur = lambda p: float(sh(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                              "-of", "csv=p=0", p]).stdout)
    print(f"{len(keep)} segments: {dur(a.clip):.1f}s -> {dur(out):.1f}s  ({out})")
    # verify: re-transcribe the cut and list anything filler-like still in it
    cw = os.path.join(raw, "cut16k.wav")
    wav16(out, cw)
    CW = transcribe(cw, a.prompt)
    left = [(w, s) for w, s, e, p in CW if norm(w) in FILLERS]
    gaps = [(CW[i - 1][2], CW[i][1]) for i in range(1, len(CW)) if CW[i][1] - CW[i - 1][2] > 0.6]
    print(" ".join(w for w, *_ in CW))
    print(f"residual fillers: {left or 'none'}")
    print(f"gaps >0.6s left: {[(round(x, 2), round(y, 2)) for x, y in gaps] or 'none'}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("transcribe"); c = sub.add_parser("cut")
    for p in (t, c):
        p.add_argument("--clip", required=True)
        p.add_argument("--workdir", default=".")
        p.add_argument("--prompt", default=PROMPT, help="Whisper initial_prompt (add this video's product names)")
    c.add_argument("--cut", default="", help='extra word indices to drop, e.g. "0-5,96-98"')
    c.add_argument("--keep", default="", help="indices to keep even if auto-flagged")
    c.add_argument("--no-auto", action="store_true", help="do not auto-drop [F] fillers")
    c.add_argument("--min-keep", type=float, default=0.2, help="drop keep slivers shorter than this (s)")
    a = ap.parse_args()
    a.clip = os.path.abspath(os.path.expanduser(a.clip))
    if not os.path.exists(a.clip): sys.exit(f"clip not found: {a.clip}")
    {"transcribe": cmd_transcribe, "cut": cmd_cut}[a.cmd](a)


if __name__ == "__main__":
    main()
