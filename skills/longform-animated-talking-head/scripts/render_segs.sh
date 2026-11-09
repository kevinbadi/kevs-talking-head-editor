#!/usr/bin/env bash
# Disk-light full render: 24 segments, 6 at a time; each segment renders its frames, encodes, then deletes them.
set -uo pipefail
NAME="${1:?name}"; SEGS=24; PAR=6
N=$(python3 -c "import json;m=json.load(open('source/meta.json'));print(int(float(m['DUR'])*30))")
STEP=$(( (N + SEGS - 1) / SEGS ))
mkdir -p renders/segs frames/logs
seg() {
  i=$1; A=$(( i * STEP )); B=$(( A + STEP )); [ $B -gt $N ] && B=$N
  [ -f renders/segs/s_$(printf %02d $i).mp4 ] && return 0
  D="frames/seg_$i"; mkdir -p "$D"
  RANGE="$A:$B" OUT="$D" python3 render.py > "frames/logs/seg_$i.txt" 2>&1 || { echo "seg $i FAILED"; return 1; }
  ffmpeg -y -loglevel error -framerate 30 -start_number $A -i "$D/f%05d.jpg" -c:v libx264 -pix_fmt yuv420p \
    -preset medium -crf 16 -r 30 "renders/segs/s_$(printf %02d $i).mp4" && find "$D" -name "*.jpg" -delete && rmdir "$D"
  echo "seg $i done ($A-$B)"
}
export -f seg; export STEP N
seq 0 $((SEGS-1)) | xargs -P $PAR -I{} bash -c 'seg {}'
ls renders/segs/s_*.mp4 | sed "s/^/file '/; s/$/'/" | sed "s|file 'renders/segs/|file '|" > renders/segs/list.txt
ffmpeg -y -loglevel error -f concat -safe 0 -i renders/segs/list.txt -i "$HOME/Downloads/the Claude + instagram self improving marketing.mov" -map 0:v -map 1:a:0 \
  -c:v copy -c:a copy -movflags +faststart -shortest renders/final.mp4
ffprobe -v error -show_entries stream=width,height:format=duration -of csv=p=0 renders/final.mp4
cp renders/final.mp4 "$HOME/Downloads/$NAME.mp4" && echo "-> ~/Downloads/$NAME.mp4"
