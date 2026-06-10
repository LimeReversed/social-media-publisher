import glob
import json
import os
from Classes.config import Config

def get_files(directory, file_types=None):
    # Use '**' to search recursively and file_types to match specific file types
    pattern = os.path.join(directory, '**', '*')
    files = [f for f in glob.glob(pattern, recursive=True) if os.path.isfile(f)]

    if file_types:
        files = [f for f in files if any(f.endswith(ft) for ft in file_types)]

    return files


def get_files_from_directories(directories, file_types=None):
    files = []

    for directory in directories:
        files += get_files(directory, file_types)

    return files

def save_json(data, file_path):
    directory = os.path.dirname(file_path)

    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(data)


def load_json(file_path):
    directory = os.path.dirname(file_path)

    if directory and not os.path.exists(directory):
        return None

    with open(file_path, 'r', encoding='utf-8') as file:
        return json.loads(file.read())


def load_config(file_path: str) -> Config:
    config_data = load_json(file_path)

    if config_data is None:
        raise FileNotFoundError(f"Config file not found: {file_path}")

    return Config.from_dict(config_data)


def get_current_directory():
    return os.path.abspath(os.path.curdir)
