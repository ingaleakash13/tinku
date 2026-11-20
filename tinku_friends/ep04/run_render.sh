#!/usr/bin/env bash
# Render in chunks (parallel), concat, mux audio.
set -e
NF=$(python3 -c "from draw import DURATION,FPS; print(int(DURATION*FPS))")
J=${J:-4}; CH=10; mkdir -p parts
step=$(( (NF + CH - 1) / CH ))
for i in $(seq 0 $((CH-1))); do
  a=$((i*step)); b=$(( (i+1)*step < NF ? (i+1)*step : NF ))
  [ -f parts/p$i.mp4 ] || echo "$a $b parts/p$i.mp4"
done | xargs -P $J -L 1 sh -c 'python3 render.py $0 $1 $2'
: > parts/list.txt; for i in $(seq 0 $((CH-1))); do echo "file 'p$i.mp4'" >> parts/list.txt; done
ffmpeg -v error -y -f concat -safe 0 -i parts/list.txt -c copy video.mp4
ffmpeg -v error -y -i video.mp4 -i audio/mix.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart final.mp4
echo done
