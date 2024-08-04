#!/usr/bin/env python

from dataclasses import dataclass
from typing import Optional
import numpy as np
import subprocess
import statistics
import psutil
import time
import json
import sys

@dataclass
class ProcessInfo:
  cpu_percent: float
  mem_rss: int

def get_process_info(pid: int) -> Optional[ProcessInfo]:

  try:
    p = psutil.Process(pid)
  except psutil.NoSuchProcess:
    return None

  cpu_percent = p.cpu_percent(interval=0.1)

  memory_info = p.memory_info()
  mem_rss = memory_info.rss

  out_pi = ProcessInfo(cpu_percent=cpu_percent, mem_rss=mem_rss)

  for c in p.children(recursive=False):

    child_pi = get_process_info(c.pid)

    out_pi.cpu_percent += child_pi.cpu_percent
    out_pi.mem_rss += child_pi.mem_rss

  return out_pi


def measure_stats(command: str, output_json_path: str) -> int:

  records = []

  start_time = time.time()
  process = subprocess.Popen(command, shell=True)

  while process.poll() is None:

    pi = get_process_info(process.pid)
    records.append(
      {
        'time_s': round(time.time() - start_time, 1),
        'cpu_percent': pi.cpu_percent,
        'mem_rss': pi.mem_rss,
      }
    )

  pooled_results = {}
  pooled_results['time_s'] = records[-1]['time_s']
  pooled_results['exit_code'] = process.returncode

  for sname in ('cpu_percent', 'mem_rss'):

    sdata = [x.get(sname) for x in records]
    np_sdata = np.array(sdata)

    pooled_results[sname+'_mean'] = int(sum(sdata) / len(records))
    pooled_results[sname+'_peak'] = max(sdata)

    pooled_results[sname+'_5perc'] = np.percentile(np_sdata, 5)
    pooled_results[sname+'_95perc'] = np.percentile(np_sdata, 95)

  with open(output_json_path, 'w', encoding='utf-8') as f:
    json.dump({'cmd': command, 'records': records, 'pooled_results': pooled_results}, f)

  return process.returncode


output_json_path = sys.argv[1]

args = ' '.join(sys.argv[2:])
retcode = measure_stats(args, output_json_path)

sys.exit(retcode)
