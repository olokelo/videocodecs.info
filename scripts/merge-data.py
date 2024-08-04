#!/usr/bin/env python3

import os
import sys
import yaml
import json

class RoundingFloat(float):
    __repr__ = staticmethod(lambda x: format(x, '.1f'))

json.encoder.c_make_encoder = None
if hasattr(json.encoder, 'FLOAT_REPR'):
    # Python 2
    json.encoder.FLOAT_REPR = RoundingFloat.__repr__
else:
    # Python 3
    json.encoder.float = RoundingFloat

def fetch_yaml(fpath):
    with open(fpath) as f:
        try:
            return yaml.load(f, Loader=yaml.FullLoader)
        except yaml.scanner.ScannerError as e:
            return None


if __name__ == '__main__':

    if len(sys.argv) <= 2:
        print("Usage: merge_data.py out.json main_dir/")
        sys.exit(1)

    output_data = {}

    output_json_path = sys.argv[1]
    main_dir = sys.argv[2]

    input_metadata_path = os.path.join(main_dir, "input.yaml")
    output_data['input metadata'] = fetch_yaml(input_metadata_path)

    search_dirs = [
        x for x in os.listdir(main_dir) if os.path.isdir(os.path.join(main_dir, x))
    ]
    for cur_dir in search_dirs:

        cur_dir = os.path.join(main_dir, cur_dir)

        print(cur_dir)

        collection_file_path = os.path.join(cur_dir, 'collection.yaml')
        if not os.path.exists(collection_file_path):
            print(f'Directory {cur_dir} does not exist or has no collection.yaml file in it. Skipping...')
            continue

        print(collection_file_path)
        coll_props = fetch_yaml(collection_file_path)
        assert 'color' in coll_props and 'group' in coll_props
        print(coll_props)

        output_data[coll_props['group']] = {
            'color': coll_props['color']
        }

        points = []
        for point_file_path in os.listdir(cur_dir):

            if not point_file_path.endswith(".stats.yaml"):
                continue

            point_data = fetch_yaml(os.path.join(cur_dir, point_file_path))
            if point_data is None:
                continue

            points.append(point_data)

        output_data[coll_props['group']]['points'] = points

    #output_data = dict(sorted(list(output_data.items())))

    with open(output_json_path, 'w') as f:
        json.dump(output_data, f)
