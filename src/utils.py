import yaml
from typing import Dict


def open_config(config_path:str="config.yaml") -> Dict:
    with open(config_path) as config_file:
        config_data = yaml.load(config_file, Loader=yaml.FullLoader)
    return config_data
