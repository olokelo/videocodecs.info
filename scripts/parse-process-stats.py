#!/usr/bin/env python3
import json
import sys

data = json.load(sys.stdin)
pooled_results = data['pooled_results']

print('cmd:', data['cmd'])
print('time (s):', pooled_results['time_s'])
print('exit code:', pooled_results['exit_code'])

print('cpu mean (%):', pooled_results['cpu_percent_mean'])
print('cpu peak (%):', pooled_results['cpu_percent_peak'])
print('ram mean (B):', pooled_results['mem_rss_mean'])
print('ram peak (B):', pooled_results['mem_rss_peak'])

# if is temp
if pooled_results.get('cpu_percent_5perc') is not None:
  print('cpu 5th percentile:', pooled_results['cpu_percent_5perc'])
  print('cpu 95th percentile:', pooled_results['cpu_percent_95perc'])
  print('ram 5th percentile:', pooled_results['mem_rss_5perc'])
  print('ram 95th percentile:', pooled_results['mem_rss_95perc'])
