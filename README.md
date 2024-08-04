# videocodecs.info benchmark

This repo contains the source code for benchmarks and frontend of the [videocodecs.info](https://videocodecs.info) website.
Under `vivict/` directory, there's a custom version of [vivict](https://github.com/vivictorg/vivict) created by Gustav Grusell.
Library used to draw graphs is [highcharts.js](https://www.highcharts.com/).

> This codebase is a subject to change. Right now that's just a couple of scripts glued together. The project should use better benchmark runner in the future. Preferably with Ansible so that the user doesn't need to install everything manually.

# Install requirements

amd64 Linux Host (preferably Arch)

Dependencies:
- python
- python-psutil
- python-numpy
- python-dataclasses-json
- ffmpeg
- vmaf
- ssimulacra2_rs
- npm
- docker
- any other program specified in benchmark config (vvenc, uavs3e, ...)

# How to use

## Modify benchmark config

Benchmark configuration is imported in the `run_benchmark.py` file. By default it's set to `benchmark_config_fhd.py`.
You might also want to review `config_common.py`.

## Set input parameters

Modify the `config_input.py`.
Here's an example of how it should look like
```python
input_clip = {
  'clipname': 'matrix',
  'title': 'Matrix',
  'desc': 'some scenes from Matrix movie trailer',
  'src': 'https://archive.org/download/the-matrix-resurrections-official-trailer-prores/rev-1-dom_trailer_1_online_txtd_mtrx4_ProResMaster_no_slate_prores.mov',
  'gop': 128,
  'fps': 23.98,
  'frames': 360,
  'width': 1920,
  'height': 1080,
}

work_dir = '/tmp'  # directory where the input .y4m file should be
final_dir = '/mnt/codec_benchmarks'  # directory for processed clips
cpu_cost_global_mult = 1.0  # adjust for more/less CPU demanding encodes
```

## Run benchmark

Place input `.y4m` file in the `work_dir`.

Run normally
```shell
$ python run_benchmark.py
```

Only produce stats (vmaf, ssimulacra2, frame bitrate, ...)
this assumes all clips are already encoded
```shell
$ python run_benchmark.py --skip-encoding
```

Only process collections which aren't present in `final_dir`
```shell
$ python run_benchmark.py --update
```


## Build Vivict

```shell
$ cd vivict/
$ npm install
$ npm run build
$ cd ..
```

## Start the frontend

```shell
$ docker build -t vci-nginx-standalone .
$ docker run -p 80:80 -v /mnt/codec_benchmarks:/www/data:ro vci-nginx-standalone
```

It should be now accessible under `http://localhost`
