from config_common import *
from config_input import *


class EncodePresets:

  ffmpeg_x26x_svt = '"$ffmpeg_bin" -y -i "$input_path" -c:v $codec_name -preset $speed -crf $quality -g $gop "$output_path"'

  ffmpeg_vpx_aom = '"$ffmpeg_bin" -y -i "$input_path" -row-mt 1 -tile-rows $tiles_log -tile-columns $tiles_log -b:v 0 -c:v $codec_name -cpu-used $speed -crf $quality -g $gop "$output_path"'

  ffmpeg_vp9ll = '"$ffmpeg_bin" -y -i "$input_path" -c:v libvpx-vp9 -lossless 1 -row-mt 1 -tile-rows 2 -tile-columns 6 -g 15 -cpu-used 4 -an "$output_path" '

  ffmpeg_avs2 = '"$ffmpeg_bin" -y -i "$input_path" -c:v $codec_name -speed_level $speed -qp $quality -g $gop "$output_path"'

  ffmpeg_avs3 = '"$ffmpeg_bin" -y -i "$input_path" -thds_wpp $thread_cnt -thds_frm 8 -c:v $codec_name -speed $speed -rc_type 1 -crf $quality -g $gop "$output_path"'

  ffmpeg_vaapi = '$system_args "$ffmpeg_bin" -y -hwaccel vaapi -hwaccel_device /dev/dri/renderD128 -hwaccel_output_format vaapi -i "$input_path" -c:v $codec_name -vf \'format=nv12,hwupload\' -compression_level:v $comp_level -g $gop -rc_mode 1 -global_quality:v $quality "$output_path"'

  vvenc = 'vvencapp --y4m -i "$input_path" -c yuv420 --intraperiod $gop --internal-bitdepth 8 -t $thread_cnt -q $quality --preset $speed -o "$output_path" '

  # crashes when using more than 8 threads
  # also it returns this weird 205 code even when output file is okay, ignore it
  # xeve_app.c needs to be patched to read 200 rather than 80 bytes of y4m header
  xeve = 'xeve_app -i "$input_path" -q $quality --keyint $gop --profile $profile --preset $speed --threads 8 -o "$output_path" ; if [ $$? -eq 205 ]; then true; fi'


# maybe vaapi should also decode accelerated??
class DecodePresets:

  ffmpeg_generic = '"$ffmpeg_bin_dec" -y $pre_ffargs -i "$output_path" $ffargs -pix_fmt yuv420p "$output_path.y4m"'


profiles =  [

  {
    "name": "original",
    "enabled": True,

    "ffmpeg_bin": "ffmpeg",
    "ffmpeg_bin_dec": "ffmpeg",
    "ffprobe_bin": "ffprobe",

    "commands": {
      "encode": MeasurePerformancePreset(
        EncodePresets.ffmpeg_vp9ll, "encode", True
      ),
      "rds": MiscPresets.reset_decoding_stats,
      "decode": MeasurePerformancePreset(
        DecodePresets.ffmpeg_generic, "decode"
      ),
      "bitrate": MetricsPresets.bitrate,
      "vmaf": MetricsPresets.vmaf,
      "ssimulacra2": MetricsPresets.ssimulacra2,
      "signal_params": MiscPresets.signal_params,
      "rm_output_y4m": MiscPresets.rm_output_y4m,
    },

    "iterators": {
      "speed": [0,],
      "quality": {0: {}},
    },

    "codec_name": "original",
    "codec_version_cmd": "$ffmpeg_bin -version",
    "input_path": "${clipname}.y4m",
    "output_path": "${clipname}_${codec_name}/${clipname}.${codec_name}.webm",

    "color": "#ffffff",

    "cpu_cost": 12,
  },

  {
    "name": "H264 (x264) $speed",
    "enabled": True,

    "ffmpeg_bin": "ffmpeg",
    "ffmpeg_bin_dec": "ffmpeg",
    "ffprobe_bin": "ffprobe",

    "commands": {
      "encode": MeasurePerformancePreset(
        EncodePresets.ffmpeg_x26x_svt, "encode", True
      ),
      "rds": MiscPresets.reset_decoding_stats,
      "decode": MeasurePerformancePreset(
        DecodePresets.ffmpeg_generic, "decode"
      ),
      "bitrate": MetricsPresets.bitrate,
      "vmaf": MetricsPresets.vmaf,
      "ssimulacra2": MetricsPresets.ssimulacra2,
      "signal_params": MiscPresets.signal_params,
      "rm_output_y4m": MiscPresets.rm_output_y4m,
    },

    "iterators": {
      "speed": {
        "veryslow": {"cpu_cost_mult": 1},
        "slow": {"cpu_cost_mult": 1},
        "medium": {"cpu_cost_mult": 0.75},
        "fast": {"cpu_cost_mult": 0.5},
      },
      "quality": seq(22, 40, 2),
      # "quality": seq(22, 26, 2),
    },

    "codec_name": "libx264",
    "codec_version_cmd": "x264 --version; echo; $ffmpeg_bin -version",
    "input_path": "${clipname}.y4m",
    "output_path": "${clipname}_${codec_name}_${speed}/${clipname}.${codec_name}_${speed}_g${gop}_crf${quality}.mp4",

    "color": "#ffffff",

    "cpu_cost": 24,
  },

  {
    "name": "H265 (x265) $speed",
    "enabled": True,

    "ffmpeg_bin": "ffmpeg",
    "ffmpeg_bin_dec": "ffmpeg",
    "ffprobe_bin": "ffprobe",

    "commands": {
      "encode": MeasurePerformancePreset(
        EncodePresets.ffmpeg_x26x_svt, "encode", True
      ),
      "rds": MiscPresets.reset_decoding_stats,
      "decode": MeasurePerformancePreset(
        DecodePresets.ffmpeg_generic, "decode"
      ),
      "bitrate": MetricsPresets.bitrate,
      "vmaf": MetricsPresets.vmaf,
      "signal_params": MiscPresets.signal_params,
      "encode_llproxy_ssimulacra2": RunParallel(
        MiscPresets.encode_llproxy, MetricsPresets.ssimulacra2
      ),
      "rm_output_y4m": MiscPresets.rm_output_y4m,
    },

    "iterators": {
      "speed": ["veryslow", "slow", "medium", "fast"],
      "quality": seq(22, 42, 2),
      #"quality": seq(22, 26, 2),
    },

    "codec_name": "libx265",
    "codec_version_cmd": "x265 --version; echo; $ffmpeg_bin -version",
    "input_path": "${clipname}.y4m",
    "output_path": "${clipname}_${codec_name}_${speed}/${clipname}.${codec_name}_${speed}_g${gop}_crf${quality}.mp4",

    "color": "#ffffff",

    "cpu_cost": 18,
  },

  {
    "name": "H266 (vvenc) $speed",
    "enabled": True,

    "ffmpeg_bin": "ffmpeg_vvc",
    "ffmpeg_bin_dec": "ffmpeg_vvc",
    "ffprobe_bin": "ffprobe",
    "pre_ffargs": "-strict -2",

    "commands": {
      "encode": MeasurePerformancePreset(
        EncodePresets.vvenc, "encode", True
      ),
      "rds": MiscPresets.reset_decoding_stats,
      "decode": MeasurePerformancePreset(
        DecodePresets.ffmpeg_generic, "decode"
      ),
      "bitrate": MetricsPresets.bitrate,
      "vmaf": MetricsPresets.vmaf,
      "signal_params": MiscPresets.signal_params,
      "encode_llproxy_ssimulacra2": RunParallel(
        MiscPresets.encode_llproxy, MetricsPresets.ssimulacra2
      ),
      "rm_output_y4m": MiscPresets.rm_output_y4m,
    },

    "iterators": {
      "speed": {
        "slow": {"cpu_cost_mult": 0.6},
        "medium": {"cpu_cost_mult": 0.6},
        "fast": {"cpu_cost_mult": 1},
      },
      "quality": seq(22, 26, 2, {"cpu_cost_mult": 1.5}) | seq(28, 44, 2),
    },

    "codec_name": "vvenc-h266",
    "codec_version_cmd": "for g in vvenc vvdec; do $${g}app --version; cd ~/Downloads/Sources/$$g; echo -n \"git commit: \"; git rev-parse --short HEAD; done; echo; $ffmpeg_bin -version",
    "input_path": "${clipname}.y4m",
    "output_path": "${clipname}_${codec_name}_${speed}/${clipname}.${codec_name}_${speed}_g${gop}_q${quality}.h266",

    "color": "#ffffff",

    "cpu_cost": 30,
  },

  {
    "name": "EVC (xeve) $profile $speed",
    "enabled": True,

    "ffmpeg_bin": "ffmpeg_evc",
    "ffmpeg_bin_dec": "ffmpeg_evc",
    "ffprobe_bin": "ffprobe_evc",
    "pre_ffargs": "-r $fps",

    "commands": {
      "encode": MeasurePerformancePreset(
        EncodePresets.xeve, "encode", True
      ),
      "rds": MiscPresets.reset_decoding_stats,
      "decode": MeasurePerformancePreset(
        DecodePresets.ffmpeg_generic, "decode"
      ),
      "bitrate": MetricsPresets.bitrate,
      "vmaf": MetricsPresets.vmaf,
      "signal_params": MiscPresets.signal_params,
      "encode_llproxy_ssimulacra2": RunParallel(
        MiscPresets.encode_llproxy, MetricsPresets.ssimulacra2
      ),
      "rm_output_y4m": MiscPresets.rm_output_y4m,
    },

    "iterators": {
      "profile": ["baseline", "main"],
      "speed": {
        "medium": {"cpu_cost_mult": 1},
      },
      "quality": seq(22, 38, 2),
      #"quality": seq(26, 28, 2),
    },

    "codec_name": "xeve-evc",
    "codec_version_cmd": "for g in xeve xevd; do cd ~/Downloads/Sources/$$g; echo -n \"$$g git commit: \"; git rev-parse --short HEAD; done; echo; $ffmpeg_bin -version",
    "input_path": "${clipname}.y4m",
    "output_path": "${clipname}_${codec_name}_${profile}_${speed}/${clipname}.${codec_name}_${profile}_${speed}_g${gop}_q${quality}.evc",

    "color": "#ffffff",

    # TODO: adjust to always be 8 threads regardless of global multiplier
    "cpu_cost": 8,
  },

  {
    "name": 'AVS2 (xavs2e) speed $speed',
    "enabled": False,

    "ffmpeg_bin": "ffmpeg",
    "ffmpeg_bin_dec": "ffmpeg",
    "ffprobe_bin": "ffprobe",
    "pre_ffargs": "-r $fps",

    "commands": {
      "encode": MeasurePerformancePreset(
        EncodePresets.ffmpeg_avs2, "encode", True
      ),
      "rds": MiscPresets.reset_decoding_stats,
      "decode": MeasurePerformancePreset(
        DecodePresets.ffmpeg_generic, "decode"
      ),
      "bitrate": MetricsPresets.bitrate,
      "vmaf": MetricsPresets.vmaf,
      "signal_params": MiscPresets.signal_params,
      "encode_llproxy_ssimulacra2": RunParallel(
        MiscPresets.encode_llproxy, MetricsPresets.ssimulacra2
      ),
      "rm_output_y4m": MiscPresets.rm_output_y4m,
    },

    "iterators": {
      "speed": {
        "3": {"cpu_cost_mult": 0.9},
        "6": {"cpu_cost_mult": 0.8},
        "9": {"cpu_cost_mult": 1.1},
      },
      "quality": seq(24, 32, 4, {"cpu_cost_mult": 1.1}) | seq(36, 44, 4),
    },

    "codec_name": "libxavs2",
    "codec_version_cmd": "pacman -Q | grep avs2; echo; $ffmpeg_bin -version",
    "input_path": "${clipname}.y4m",
    "output_path": "${clipname}_${codec_name}_speed${speed}/${clipname}.${codec_name}_speed${speed}_g${gop}_q${quality}.avs2",

    "color": "#ffffff",

    "cpu_cost": 16,
  },

  {
    "name": 'AVS3 (uavs3e) speed $speed',
    "enabled": True,

    "ffmpeg_bin": "ffmpeg_avs3",
    "ffmpeg_bin_dec": "ffmpeg_avs3",
    "ffprobe_bin": "ffprobe",
    "pre_ffargs": "-r $fps",

    "commands": {
      "encode": MeasurePerformancePreset(
        EncodePresets.ffmpeg_avs3, "encode", True
      ),
      "rds": MiscPresets.reset_decoding_stats,
      "decode": MeasurePerformancePreset(
        DecodePresets.ffmpeg_generic, "decode"
      ),
      "bitrate": MetricsPresets.bitrate,
      "vmaf": MetricsPresets.vmaf,
      "signal_params": MiscPresets.signal_params,
      "encode_llproxy_ssimulacra2": RunParallel(
        MiscPresets.encode_llproxy, MetricsPresets.ssimulacra2
      ),
      "rm_output_y4m": MiscPresets.rm_output_y4m,
    },

    "iterators": {
      "speed": {
        "2": {"cpu_cost_mult": 1},
        "4": {"cpu_cost_mult": 1},
      },
      "quality": seq(26, 30, 2, {"cpu_cost_mult": 1.5}) | seq(32, 48, 2),
      #"quality": seq(22, 24, 2, {"cpu_cost_mult": 1.5}) | seq(32, 36, 2),
    },

    "codec_name": "libuavs3e",
    "codec_version_cmd": "pacman -Q | grep avs3; $ffmpeg_bin -version; echo; $ffmpeg_bin_dec -version",
    "input_path": "${clipname}.y4m",
    "output_path": "${clipname}_${codec_name}_speed${speed}/${clipname}.${codec_name}_speed${speed}_g${gop}_crf${quality}.avs3",

    "color": "#ffffff",

    "cpu_cost": 8,
  },

  {
    "name": 'VP9 (vpx) speed $speed',
    "enabled": True,

    "ffmpeg_bin": "ffmpeg",
    "ffmpeg_bin_dec": "ffmpeg",
    "ffprobe_bin": "ffprobe",

    "commands": {
      "encode": MeasurePerformancePreset(
        EncodePresets.ffmpeg_vpx_aom, "encode", True
      ),
      "rds": MiscPresets.reset_decoding_stats,
      "decode": MeasurePerformancePreset(
        DecodePresets.ffmpeg_generic, "decode"
      ),
      "bitrate": MetricsPresets.bitrate,
      "vmaf": MetricsPresets.vmaf,
      "ssimulacra2": MetricsPresets.ssimulacra2,
      "signal_params": MiscPresets.signal_params,
      "rm_output_y4m": MiscPresets.rm_output_y4m,
    },

    "iterators": {
      "speed": {
        "0": {"cpu_cost_mult": 1},
        "2": {"cpu_cost_mult": 1},
        "4": {"cpu_cost_mult": 0.8},
        "6": {"cpu_cost_mult": 0.5},
      },
      "quality": seq(30, 62, 4),
      #"quality": seq(24, 60, 6),
    },

    "codec_name": "libvpx-vp9",
    "codec_version_cmd": "for g in enc dec; do vpx$${g} --help | grep \"WebM Project VP9\" | sed 's/^[ \t]*//'; done; echo; $ffmpeg_bin -version",
    "tiles_log": 2,
    "input_path": "${clipname}.y4m",
    "output_path": "${clipname}_${codec_name}_speed${speed}/${clipname}.${codec_name}_speed${speed}_g${gop}_crf${quality}.webm",

    "color": "#ffffff",

    "cpu_cost": 12,
  },

  {
    "name": 'AV1 (aom) speed $speed',
    "enabled": True,

    "ffmpeg_bin": "ffmpeg",
    "ffmpeg_bin_dec": "ffmpeg",
    "ffprobe_bin": "ffprobe",

    "commands": {
      "encode": MeasurePerformancePreset(
        EncodePresets.ffmpeg_vpx_aom, "encode", True
      ),
      "rds": MiscPresets.reset_decoding_stats,
      "decode": MeasurePerformancePreset(
        DecodePresets.ffmpeg_generic, "decode"
      ),
      "bitrate": MetricsPresets.bitrate,
      "vmaf": MetricsPresets.vmaf,
      "ssimulacra2": MetricsPresets.ssimulacra2,
      "signal_params": MiscPresets.signal_params,
      "rm_output_y4m": MiscPresets.rm_output_y4m,
    },

    "iterators": {
      "speed": {
        "2": {"cpu_cost_mult": 1.2},
        "4": {"cpu_cost_mult": 0.8},
        "6": {"cpu_cost_mult": 1},
      },
      "quality": seq(24, 60, 4) | {63: {}},
      #"quality": seq(24, 56, 8),
    },

    "codec_name": "libaom-av1",
    "codec_version_cmd": "aomenc --help | grep \"AOMedia Project AV1\" | sed 's/^[ \t]*//'; echo; pacman -Q dav1d; echo; $ffmpeg_bin -version",
    "tiles_log": 3,
    "input_path": "${clipname}.y4m",
    "output_path": "${clipname}_${codec_name}_speed${speed}/${clipname}.${codec_name}_speed${speed}_g${gop}_crf${quality}.webm",

    "color": "#ffffff",

    "cpu_cost": 20,
  },

  {
    "name": 'AV1 (svt) speed $speed',
    "enabled": True,

    "ffmpeg_bin": "ffmpeg",
    "ffmpeg_bin_dec": "ffmpeg",
    "ffprobe_bin": "ffprobe",

    "commands": {
      "encode": MeasurePerformancePreset(
        EncodePresets.ffmpeg_x26x_svt, "encode", True
      ),
      "rds": MiscPresets.reset_decoding_stats,
      "decode": MeasurePerformancePreset(
        DecodePresets.ffmpeg_generic, "decode"
      ),
      "bitrate": MetricsPresets.bitrate,
      "vmaf": MetricsPresets.vmaf,
      "ssimulacra2": MetricsPresets.ssimulacra2,
      "signal_params": MiscPresets.signal_params,
      "rm_output_y4m": MiscPresets.rm_output_y4m,
    },

    "iterators": {
      "speed": {
        "4": {"cpu_cost_mult": 1},
        "7": {"cpu_cost_mult": 1},
        "10": {"cpu_cost_mult": 1},
      },
      "quality": seq(28, 60, 4) | {63: {}},
      # "quality": seq(24, 56, 8),
    },

    "codec_name": "libsvtav1",
    "codec_version_cmd": "SvtAv1EncApp --version; echo; pacman -Q dav1d; echo; $ffmpeg_bin -version",
    "input_path": "${clipname}.y4m",
    "output_path": "${clipname}_${codec_name}_speed${speed}/${clipname}.${codec_name}_speed${speed}_g${gop}_crf${quality}.webm",

    "color": "#ffffff",

    "cpu_cost": 30,
  },

  {
    "name": 'AV1 (Intel A750 vaapi)',
    "enabled": True,

    #"system_args": "LD_LIBRARY_PATH=/home/oloke/bin/cartwheel/lib/ ",
    #"ffmpeg_bin": "/home/oloke/bin/cartwheel/bin/ffmpeg",
    "ffmpeg_bin": "ffmpeg",
    "ffmpeg_bin_dec": "ffmpeg",
    "ffprobe_bin": "ffprobe",

    "commands": {
      "encode": MeasurePerformancePreset(
        EncodePresets.ffmpeg_vaapi, "encode", True
      ),
      "rds": MiscPresets.reset_decoding_stats,
      "decode": MeasurePerformancePreset(
        DecodePresets.ffmpeg_generic, "decode"
      ),
      "bitrate": MetricsPresets.bitrate,
      "vmaf": MetricsPresets.vmaf,
      "ssimulacra2": MetricsPresets.ssimulacra2,
      "signal_params": MiscPresets.signal_params,
      "rm_output_y4m": MiscPresets.rm_output_y4m,
    },

    "iterators": {
      "speed": [0],
      "quality": seq(90, 210, 10),
      # "quality": seq(90, 210, 30),
    },

    "codec_name": "av1_vaapi",
    "codec_version_cmd": "$ffmpeg_bin -version",
    "comp_level": 1,
    "is_gpu": True,
    "input_path": "${clipname}.y4m",
    "output_path": "${clipname}_${codec_name}/${clipname}.${codec_name}_g${gop}_q${quality}.webm",

    "color": "#ffffff",

    "cpu_cost": 2,
  },

  {
    "name": 'VP9 (Intel A750 vaapi)',
    "enabled": True,

    "ffmpeg_bin": "ffmpeg",
    "ffmpeg_bin_dec": "ffmpeg",
    "ffprobe_bin": "ffprobe",

    "commands": {
      "encode": MeasurePerformancePreset(
        EncodePresets.ffmpeg_vaapi, "encode", True
      ),
      "rds": MiscPresets.reset_decoding_stats,
      "decode": MeasurePerformancePreset(
        DecodePresets.ffmpeg_generic, "decode"
      ),
      "bitrate": MetricsPresets.bitrate,
      "vmaf": MetricsPresets.vmaf,
      "ssimulacra2": MetricsPresets.ssimulacra2,
      "signal_params": MiscPresets.signal_params,
      "rm_output_y4m": MiscPresets.rm_output_y4m,
    },

    "iterators": {
      "speed": [0],
      "quality": seq(100, 210, 10),
      #"quality": seq(32, 40, 8),
    },

    "codec_name": "vp9_vaapi",
    "codec_version_cmd": "$ffmpeg_bin -version",
    "comp_level": 0,
    "is_gpu": True,
    "input_path": "${clipname}.y4m",
    "output_path": "${clipname}_${codec_name}/${clipname}.${codec_name}_g${gop}_q${quality}.mp4",

    "color": "#ffffff",

    "cpu_cost": 2,
  },

  {
    "name": 'H264 (Intel A750 vaapi)',
    "enabled": True,

    "ffmpeg_bin": "ffmpeg",
    "ffmpeg_bin_dec": "ffmpeg",
    "ffprobe_bin": "ffprobe",

    "commands": {
      "encode": MeasurePerformancePreset(
        EncodePresets.ffmpeg_vaapi, "encode", True
      ),
      "rds": MiscPresets.reset_decoding_stats,
      "decode": MeasurePerformancePreset(
        DecodePresets.ffmpeg_generic, "decode"
      ),
      "bitrate": MetricsPresets.bitrate,
      "vmaf": MetricsPresets.vmaf,
      "ssimulacra2": MetricsPresets.ssimulacra2,
      "signal_params": MiscPresets.signal_params,
      "rm_output_y4m": MiscPresets.rm_output_y4m,
    },

    "iterators": {
      "speed": [0],
      "quality": seq(26, 44, 2),
      #"quality": seq(32, 40, 8),
    },

    "codec_name": "h264_vaapi",
    "codec_version_cmd": "$ffmpeg_bin -version",
    "comp_level": 0,
    "is_gpu": True,
    "input_path": "${clipname}.y4m",
    "output_path": "${clipname}_${codec_name}/${clipname}.${codec_name}_g${gop}_q${quality}.mp4",

    "color": "#ffffff",

    "cpu_cost": 2,
  },

  {
    "name": 'H265 (Intel A750 vaapi)',
    "enabled": True,

    "ffmpeg_bin": "ffmpeg",
    "ffmpeg_bin_dec": "ffmpeg",
    "ffprobe_bin": "ffprobe",

    "commands": {
      "encode": MeasurePerformancePreset(
        EncodePresets.ffmpeg_vaapi, "encode", True
      ),
      "rds": MiscPresets.reset_decoding_stats,
      "decode": MeasurePerformancePreset(
        DecodePresets.ffmpeg_generic, "decode"
      ),
      "bitrate": MetricsPresets.bitrate,
      "vmaf": MetricsPresets.vmaf,
      "signal_params": MiscPresets.signal_params,
      "encode_llproxy_ssimulacra2": RunParallel(
        MiscPresets.encode_llproxy, MetricsPresets.ssimulacra2
      ),
      "rm_output_y4m": MiscPresets.rm_output_y4m,
    },

    "iterators": {
      "speed": [0],
      "quality": seq(24, 44, 2),
      #"quality": seq(24, 40, 8),
    },

    "codec_name": "hevc_vaapi",
    "codec_version_cmd": "$ffmpeg_bin -version",
    "comp_level": 0,
    "is_gpu": True,
    "input_path": "${clipname}.y4m",
    "output_path": "${clipname}_${codec_name}/${clipname}.${codec_name}_g${gop}_q${quality}.mp4",

    "color": "#ffffff",

    "cpu_cost": 2,
  },

]
