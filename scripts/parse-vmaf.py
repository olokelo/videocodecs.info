#!/usr/bin/env python3
import numpy as np
import json
import statistics
import sys

vmaf_data = json.load(sys.stdin)

mean = vmaf_data['pooled_metrics']['vmaf']['mean']

vmaf_frames = [x['metrics']['vmaf'] for x in vmaf_data['frames']]
stdev = statistics.stdev(vmaf_frames)

np_vmaf_frames = np.array(vmaf_frames)

sys.stdout.write(f"mean: {mean}\n")
sys.stdout.write(f"median: {np.percentile(np_vmaf_frames, 50)}\n")
sys.stdout.write(f"std dev: {stdev}\n")
sys.stdout.write(f"1st percentile: {np.percentile(np_vmaf_frames, 1)}\n")
sys.stdout.write(f"5th percentile: {np.percentile(np_vmaf_frames, 5)}\n")
sys.stdout.write(f"95th percentile: {np.percentile(np_vmaf_frames, 95)}\n")
