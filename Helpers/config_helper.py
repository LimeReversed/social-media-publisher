from Classes.config import *
from Helpers.file_helper import load_json

def load_config(file_path: str) -> Config:
    config_data = load_json(file_path)

    if config_data is None:
        raise FileNotFoundError(f"Config file not found: {file_path}")

    return Config.from_dict(file_path, config_data)

def load_config_list(file_paths: list[str]) -> list[Config]:
    configs = []

    for path in file_paths:
        config = load_config(path)
        configs.append(config)

    return configs

