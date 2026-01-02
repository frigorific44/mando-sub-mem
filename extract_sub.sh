#!/bin/bash
readarray -t SUB_STREAMS < <(ffprobe -v error -select_streams s -show_entries stream_tags=title -of csv=p=0 "$1")
readarray -t SUB_INDICES < <(ffprobe -v error -select_streams s -show_entries stream=index -of csv=p=0 "$1")
printf "\nSubtitle Streams\n\n"
i=1
for stream in "${SUB_STREAMS[@]}"; do
  echo "${i}. $stream"
  ((i++))
done
s=0
printf "Choose:\n"
while [ $s -lt 1 ] || [ $s -ge $i ]; do
  read s
done
((s--))
# title=${SUB_STREAMS[$s]}
# echo "$title"
# echo "$index"
ffmpeg -i "$1" -map "0:s:$s" subtitles.srt
