#!/usr/bin/env bash

visible=false
vmaf=true
input=""
outext=""

if [ -z "${FFMPEG_BIN}" ]
then
  FFMPEG_BIN=ffmpeg
fi
if [ -z "${FFMPEG_WITH_VMAF_BIN}" ]
then
  FFMPEG_WITH_VMAF_BIN=ffmpeg
fi

if [ -z "${FFPROBE_BIN}" ]
then
  FFPROBE_BIN=ffprobe
fi

if [ -z "${VMAF}" ]
then
  VMAF=true
fi

suffix=""
bin_args=""

temp_props=$(mktemp)

is_reserved_arg() { case $2 in "--s-"*) true;; *) false;; esac; }

for arg in "${@:1}"
do

  if [ "$arg" != "-hidden" ] && [ "$arg" != "-visible" ] && [ "${arg:0:4}" != "--s-" ]
  then
    bin_args="$bin_args $arg"
  fi

  case "$arg" in

    --s-input=*)
      input=$(echo $arg | cut -f2 -d=) ;;
    --s-out-ext=*)
      outext=$(echo $arg | cut -f2 -d=) ;;
    --s-out-dir=*)
      outdir=$(echo $arg | cut -f2 -d=) ;;

  esac

  if [ "$arg" == "-hidden" ]
  then
    visible=false
    continue
  fi

  if [ "$arg" == "-visible" ]
  then
    visible=true
    continue
  fi

  if [ "$visible" = false ]
  then
    continue
  fi

  emit=""
  case "$arg" in

    "-c:v" | "-vcodec")
      emit="codec" ;;
    "-c:a" | "-acodec")
      emit="acodec";;

    "-preset" | "--preset")
      emit="preset" ;;

    "-b:v")       emit="bv" ;;
    "-b:a")       emit="ba" ;;
    "-cpu-used")  emit="cpuused" ;;
    "-speed")     emit="speed" ;;
    "-threads")   emit="threads" ;;
    "-crf")       emit="crf" ;;
    "-g")         emit="gop" ;;
    "-r")         emit="fps" ;;
    "-profile:v") emit="vprofile" ;;
    "-profile:a") emit="aprofile" ;;
    "-q" | "-qp") emit="q" ;;
    "-pix_fmt")   emit="pixfmt" ;;

    "-compression_level:v") emit="clevel" ;;
    "-global_quality:v") emit="q" ;;

    -*) ;;

    *)
      emit="${arg}_"; echo ${arg} >> $temp_props ;;

  esac

  if [ "$emit" != "${arg}_" ] && [ "$emit" != "" ]
  then
    echo -n "${emit}: " >> $temp_props
  fi

  suffix="$suffix$emit"

done

if [ -z "${input}" ]
then
  echo No input file provided.
  rm $temp_props
  exit 1
fi

if [ -z "${outext}" ]
then
  echo No output extension provided.
  rm $temp_props
  exit 1
fi

if [ -z "${outdir}" ]
then
  outdir=$(dirname "$input")
fi
mkdir -p "${outdir}"

output="${outdir}"/$(basename "$input.${suffix::-1}.$outext")

/usr/bin/time -o "$output.stats.yaml" -f "cmd: %C\ntime (s): %e\ncpu: %P\nmem (kB): %M\nexit code: %x" sh -c "$FFMPEG_BIN '$PRE_INPUT_ARGS' -i '$input' $bin_args '$output'"

if [ $? != 0 ]
then
    exit $?
fi

sed -i 's/cpu: \([0-9]\+\)%$/cpu: \1/' "$output.stats.yaml"

if [ "$VMAF" = true ]
then
  $FFMPEG_BIN -i "$output" -pix_fmt yuv420p -f yuv4mpegpipe - | $FFMPEG_WITH_VMAF_BIN -hide_banner -i "$input" -i - -pix_fmt yuv420p -an -lavfi "[0:v]setpts=PTS-STARTPTS[reference];[1:v]setpts=PTS-STARTPTS[distorted];[distorted][reference]libvmaf=feature='name=psnr':log_fmt=json:n_threads=4:log_path=$output.json" -f null -
  echo vmaf: $(cat "$output.json" | jq '.pooled_metrics | .vmaf | .mean') >> "$output.stats.yaml"
  echo "psnr y:" $(cat "$output.json" | jq '.pooled_metrics | .psnr_y | .mean') >> "$output.stats.yaml"
fi

FFMPEG_BIN=$FFMPEG_BIN FFPROBE_BIN=$FFPROBE_BIN ffmpeg-calc-bitrate.sh "${output}" >> "$output.stats.yaml"

cat $temp_props >> "$output.stats.yaml"
rm $temp_props

echo "output:" $(basename "${output}") >> "$output.stats.yaml"

cat "$output.stats.yaml"
