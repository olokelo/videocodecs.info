from typing import List

def seq(start, end, step, innerdict: dict={}):
  assert start <= end
  return dict([(x, innerdict) for x in range(start, end+step, step)])


def MeasurePerformancePreset(cmd: str, section_name: str, overwrite: bool=False) -> str:

  out_json_path = f"$output_path.{section_name}.process-stats.json"

  first_redirect = '>' if overwrite else '>>'

  # sh needed for returning appropriate exit code of main process at the end
  return f'sh -c \'echo "{section_name}:" {first_redirect} "$output_path.stats.yaml" ; process-stats.py "{out_json_path}" ' + cmd + f'; EXIT_CODE=$$? ; cat "{out_json_path}" | parse-process-stats.py | sed "s/^/  /" >> "$output_path.stats.yaml"; exit $$EXIT_CODE \' '


def RunParallel(*cmds: List[str]) -> str:

  if len(cmds) == 0:
    return ''
  elif len(cmds) == 1:
    return cmds[0]

  out = "parallel ::: "
  for cmd in cmds:
    # escape single quotes that might already be in cmd
    out += "'" + cmd.replace("'", "'\\''") + "' "

  return out


# input_path      -> path to input video
# output_path_y4m -> path to .y4m file of compressed video decoded into y4m format
# all paths are relative to work_dir
# thread_cnt      -> number of all threads available on the system
class MetricsPresets:

  vmaf = 'vmaf --threads $thread_cnt --json -o "$output_path.vmaf.json" -r "$input_path" -d "$output_path.y4m" && echo "vmaf:" >> "$output_path.stats.yaml" && cat "$output_path.vmaf.json" | parse-vmaf.py | sed "s/^/  /" >> "$output_path.stats.yaml" '

  # sleep is so that when running in parallel it won't interfere with lossless proxy path in stats file
  ssimulacra2 = 'sleep 2; echo "ssimulacra2:" >> "$output_path.stats.yaml"; ssimulacra2_rs video -f 16 "$input_path" "$output_path.y4m" | tail -n +2 | tr "[:upper:]" "[:lower:]" | sed "s/^/  /" >> "$output_path.stats.yaml"; rm "$output_path.y4m.lwi"'
  #ssimulacra2 = ''

  bitrate = 'echo "probe:" >> "$output_path.stats.yaml"; FFMPEG_BIN="$ffmpeg_bin" FFPROBE_BIN="$ffprobe_bin" FPS=$fps OUTPUT_BR_PATH="$output_path.frame-bitrate.json" ffmpeg-calc-bitrate.sh $output_path | sed "s/^/  /" >> "$output_path.stats.yaml" '


class MiscPresets:

  signal_params = 'echo "quality: \'$quality\'" >> "$output_path.stats.yaml" ; echo "encoded path: \'$output_path\'" >> "$output_path.stats.yaml"'

  encode_llproxy = 'echo "lossless proxy path: \'$output_path.llproxy.webm\'" >> "$output_path.stats.yaml"; ffmpeg -y -i "$output_path.y4m" -c:v libvpx-vp9 -lossless 1 -row-mt 1 -tile-rows 2 -tile-columns 6 -g 15 -cpu-used 4 -an "$output_path.llproxy.webm" '

  rm_output_y4m = 'rm "$output_path.y4m"'

  # leave only encoding part in stat file
  reset_decoding_stats = 'STAT_FILE="$output_path.stats.yaml" SEARCH_STR="decode:" truncate-from.sh'

  merge_data = 'merge-data.py "$final_dir/$clipname/metafile.json" "$final_dir/$clipname" '

  add_clip = 'FINAL_DIR="$final_dir" CLIPNAME="$clipname" CLIPDESC="$desc" CLIPSRC="$src" add-clip.py'


# commands that are meant to be executed after finished clips were moved to $final_dir
after_final_cmds = [
  MiscPresets.add_clip,
  MiscPresets.merge_data
]
