#!/usr/bin/env bash

# https://stackoverflow.com/a/60689553

# Determine the peak bitrate and average bit rate for a video file.
#
# Counts video stream packets directly so can be used when
# video bitrate metadata is incorrect or missing. Very fast.
#
# Usage:
# ./vbit.sh <file> <optional: frames to count> <optional: fps (detected automatically if excluded)>
#
# Examples:
# ./vbit.sh input.mkv
# ./vbit.sh input.mkv  10000

if [ -z "${FFMPEG_BIN}" ]
then
  FFMPEG_BIN=ffmpeg
fi

if [ -z "${FFPROBE_BIN}" ]
then
  FFPROBE_BIN=ffprobe
fi

if [ -z "${OUTPUT_BR_PATH}" ]
then
  OUTPUT_BR_PATH=/dev/null
fi

# defaults to detecting tbr with ffmpeg
: ${FPS:=$($FFMPEG_BIN -strict -2 -i $1 2>&1 | sed -n "s/.*, \(.*\) tbr.*/\1/p")}

echo "fps: $FPS"

printf '{"frames": [' > "${OUTPUT_BR_PATH}"

awk -v FPS="${FPS}" -v OUTPUT_BR_PATH="${OUTPUT_BR_PATH}" '
BEGIN{
    FS="="
}

/size/ {
  br=$2/1000.0*8*FPS
  if (br > max_br)
      max_br=br
  acc_br+=br
  acc_bytes+=br
  i+=1

  printf("{\"frameNum\": %d, \"bitrate (kbps)\": %.1f}, ", i, br) >> OUTPUT_BR_PATH

}

END {
    printf("bitrate (kbps): %.1f\n", acc_br/i)
    printf("peak bitrate (kbps): %.1f\n", max_br)
}
' <($FFPROBE_BIN -strict -2 -select_streams v -show_entries packet=size $1 2>/dev/null)

# remote trailing comma as it would invalidate json
truncate -s-2 "${OUTPUT_BR_PATH}"
printf ']}' >> "${OUTPUT_BR_PATH}"
