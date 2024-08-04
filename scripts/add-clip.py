#!/usr/bin/env python3

import os
import sys
import json

for var in ('FINAL_DIR', 'CLIPNAME', 'CLIPDESC', 'CLIPSRC'):
  if not var in os.environ.keys():
    print(f'Environment variable not found: {arg}')
    sys.exit(1)

clipdata = {'clips': {}}
json_clips_path = os.path.join(os.environ.get('FINAL_DIR'), 'clips.json')
if os.path.exists(json_clips_path):
  with open(json_clips_path, 'r') as f:
    clipdata = json.load(f)

clipdata['clips'][os.environ.get('CLIPNAME')] = {'desc': os.environ.get('CLIPDESC'), 'src': os.environ.get('CLIPSRC')}

with open(json_clips_path, 'w') as f:
  json.dump(clipdata, f)
