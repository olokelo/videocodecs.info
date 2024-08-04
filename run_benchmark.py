import subprocess
import threading
import itertools
import shutil
import psutil
import string
import yaml
import time
import copy
import sys
import os

from typing import Dict, Any
from pprint import pprint

import benchmark_config_fhd as benchmark_config


SKIP_ENCODING = '--skip-encoding' in sys.argv
UPDATE = '--update' in sys.argv


def run_command(cmd: str, capture_output=False) -> subprocess.CompletedProcess:

  # add scripts directory to path
  cur_env = os.environ.copy()
  cur_env["PATH"] = f"{os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts')}:{cur_env['PATH']}"

  r = subprocess.run(cmd, cwd=benchmark_config.work_dir, capture_output=capture_output, shell=True, env=cur_env)
  return r


def apply_env(value: str, env: Dict[str, Any]) -> str:

  templ = string.Template(value)
  idents = templ.get_identifiers()

  # initialize missing keys with empty values
  for ident in idents:
    if env.get(ident) is None:
      env[ident] = ''

  return templ.substitute(env)


def get_final_profile_dir(profile_work_dir: str) -> str:

  final_dir = benchmark_config.final_dir
  clipname = benchmark_config.input_clip.get('clipname')

  final_clip_dir = os.path.join(final_dir, clipname)
  return os.path.join(final_clip_dir, os.path.basename(profile_work_dir))


# write info about input clip
def write_input_stats() -> None:

  final_profile_dir = get_final_profile_dir('')
  os.makedirs(final_profile_dir, exist_ok=True)

  with open(os.path.join(final_profile_dir, 'input.yaml'), 'w') as fo:
    for k, v in benchmark_config.input_clip.items():
      fo.write(f'{k}: {v}\n')

write_input_stats()


i = 0
encoding_queue = []  # pooling queue from which encoding tasks are chosen and run simultaniously
final_queue = []  # sequential tasks which are being run after all of the encoding is done
for _profile in benchmark_config.profiles:

  if not _profile.get('enabled'):
    continue

  iterators = _profile.get('iterators')

  for cur_values in itertools.product(*iterators.values()):

    profile = copy.deepcopy(_profile)

    # that is some pure magic, don't touch
    for cur_key, cur_value in zip(iterators.keys(), cur_values):
      profile[cur_key] = cur_value

    profile.update(benchmark_config.input_clip)
    profile.update({'final_dir': benchmark_config.final_dir, 'work_dir': benchmark_config.work_dir})
    profile.update({
      'thread_cnt': psutil.cpu_count()
    })
    #profile.update({'quality': quality, 'speed': speed})
    profile['id'] = i
    #print(quality, speed)

    profile['cpu_cost'] *= benchmark_config.cpu_cost_global_mult

    # iterators can be expressed in either a list or dictionary
    # the dictionary can hold additional parameters for the specific iterator value
    for itkey in iterators.keys():
      if type(iterators.get(itkey)) == dict:
        cur_cpu_cost_mult = iterators.get(itkey).get(profile.get(itkey)).get('cpu_cost_mult')
        if cur_cpu_cost_mult:
          profile['cpu_cost'] *= cur_cpu_cost_mult

    # template all values of type string in current profile
    for k in profile.keys():
      if type(profile[k]) != str:
        continue
      profile[k] = apply_env(profile[k], profile)

    profile_work_dir = os.path.join(benchmark_config.work_dir, os.path.dirname(profile.get('output_path')))

    if UPDATE and os.path.exists(get_final_profile_dir(profile_work_dir)):
      continue

    os.makedirs(profile_work_dir, exist_ok=True)

    for cmd_step, cmd in profile.get('commands').items():

      cmd = apply_env(cmd, profile)
      profile['commands'][cmd_step] = cmd

      cur_task = {'cmd': cmd, 'profile': profile, 'profile_work_dir': profile_work_dir}
      if cmd_step == 'encode':
        encoding_queue.append(cur_task)
      else:
        cur_task['done'] = False
        final_queue.append(cur_task)

    with open(os.path.join(profile_work_dir, 'codec_version.txt'), 'wb') as f:
      f.write(run_command(profile.get('codec_version_cmd'), capture_output=True).stdout)

    with open(os.path.join(profile_work_dir, 'collection.yaml'), 'w', encoding='utf-8') as f:
      collection_data = {'group': profile.get('name'), 'color': profile.get('color')}
      yaml.dump(collection_data, f, default_flow_style=False)

    i += 1


if SKIP_ENCODING:
  encoding_queue = []

running_tasks = []


def remove_profile_from_queue(profile_id: int) -> None:

  global final_queue

  # yes, very efficient
  final_queue = [x for x in final_queue if x.get('profile').get('id') != profile_id]


# TODO: test the check for non zero exit code
def run_encode_task(task: Dict[str, Any]) -> None:

  global running_tasks

  running_tasks.append(task)

  r = run_command(task.get('cmd'))
  # if encoding command failed, do not run probing/metrics commands on the corrupted file
  if r.returncode != 0:
    remove_profile_from_queue(task.get('profile').get('id'))

  running_tasks.remove(task)


def find_task(free_cpu: float):

  global encoding_queue, running_tasks

  sorted_queue = sorted(encoding_queue, key=lambda x:x['profile']['cpu_cost'])[::-1]
  #for q in sorted_queue:
  #  print(q.get("cmd"))
  #exit()

  for item in sorted_queue:
    if item.get('profile').get('cpu_cost') < (free_cpu - (0.1*psutil.cpu_count())):
      # only one gpu task can be running at once
      if any([x.get('profile').get('is_gpu') for x in running_tasks]) and item.get('profile').get('is_gpu'):
        continue
      return item
    elif len(running_tasks) == 0:
      print("returning item with cpu_cost higher than free cpu because no tasks are running")
      return item

  return None


i = 0
while not (len(encoding_queue) == 0 and threading.active_count() == 1):

  time.sleep(2)

  free_cpu = psutil.cpu_count() - sum([x.get('profile').get('cpu_cost') for x in running_tasks])

  task = find_task(free_cpu)
  if task is None:
    continue
  print(task.get('cmd'))

  if task is not None:
    t = threading.Thread(target=run_encode_task, args=(task,))
    t.daemon = True
    t.start()
    encoding_queue.remove(task)

  i += 1


#for cmd in encoding_queue:
#  r = run_command(cmd)
#  print(r.stdout, r.stderr)
#  assert r.returncode == 0

# dead code
def aggregate_stats(input_dir_path: str, output_stats_path: str) -> None:

  fo = open(output_stats_path, 'a', encoding='utf-8')

  collection_fname = os.path.join(input_dir_path, 'collection.yaml')
  with open(collection_fname, 'r', encoding='utf-8') as f:
    collection_data = yaml.load(f, Loader=yaml.Loader)

  fo.write(collection_data.get('group') + ':\n')

  for fname in os.listdir(input_dir_path):

    if not fname.endswith('.stats.yaml'):
      continue

    with open(os.path.join(input_dir_path, fname), 'r', encoding='utf-8') as f:

      # test if the input yaml is valid and if not, do not add it to aggregated file
      try:
        yaml.load(f, Loader=yaml.Loader)
      except yaml.YAMLError:
        print('Ignoring invalid yaml.')
        continue

      f.seek(0)

      for line in f.readlines():
        fo.write('  ' + line)

    fo.write('\n')
  fo.close()


def move_final(profile_work_dir: str) -> None:

  global benchmark_config

  final_profile_dir = get_final_profile_dir(profile_work_dir)
  os.makedirs(final_profile_dir, exist_ok=True)

  # aggregate_stats(profile_work_dir, os.path.join(final_clip_dir, 'stats.yaml'))

  shutil.copytree(profile_work_dir, final_profile_dir, dirs_exist_ok=True)
  shutil.rmtree(profile_work_dir)


def is_dir_done(profile_work_dir: str) -> bool:

  global final_queue

  return all([x.get('done') for x in final_queue if x.get('profile_work_dir') == profile_work_dir])


for task in final_queue:

  cmd = task.get('cmd')
  r = run_command(cmd)
  print(cmd)
  # assert r.returncode == 0

  task['done'] = True

  if is_dir_done(task.get('profile_work_dir')):
    print('You can now move all tasks with this profile_work_dir to safe directory.')
    move_final(task.get('profile_work_dir'))


for cmd in benchmark_config.after_final_cmds:

  cmd = apply_env(cmd, {'final_dir': benchmark_config.final_dir, 'work_dir': benchmark_config.work_dir} | {**benchmark_config.input_clip})

  r = run_command(cmd)
  print(cmd)
