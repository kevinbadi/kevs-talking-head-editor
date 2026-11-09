import json, subprocess, sys
CLIP = sys.argv[1] if len(sys.argv) > 1 else "raw.mp4"   # the original raw take
keep = [[15.40, 19.70], [20.40, 22.27], [23.99, 26.2], [31.428, 32.76], [37.75, 38.36], [38.56, 42.34],
        [42.54, 54.9], [55.1, 58.42], [58.98, 59.76], [61.76, 65.22], [67.204, 75.3]]
json.dump(keep, open("raw/keep.json", "w"))
parts, ins = [], []
for k, (x, y) in enumerate(keep):
    d = y - x
    parts.append(f"[0:v]trim=start={x}:end={y},setpts=PTS-STARTPTS[v{k}]")
    parts.append(f"[0:a]atrim=start={x}:end={y},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,afade=t=out:st={max(0,d-0.015):.3f}:d=0.015[a{k}]")
    ins.append(f"[v{k}][a{k}]")
open("raw/cut_filter.txt", "w").write(";".join(parts) + ";" + "".join(ins) + f"concat=n={len(keep)}:v=1:a=1[v][a]")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", CLIP, "-filter_complex_script", "raw/cut_filter.txt", "-map", "[v]", "-map", "[a]",
    "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k",
    "-movflags", "+faststart", "raw/cut.mp4"], check=True)
