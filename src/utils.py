import json

from argparse import ArgumentParser


def read_config(config_filepath):
    with open(f'resource/config/{config_filepath}') as f:
        config_dict = json.load(f)

    parser = ArgumentParser()
    for k, v in config_dict.items():
        parser.add_argument(f'--{k}', type=eval(v['type']), default=v['default'])

    config, _ = parser.parse_known_args()
    return config
