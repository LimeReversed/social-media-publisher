import glob
import json
import os
from datetime import date, datetime
from dataclasses import asdict, is_dataclass
from typing import Any


def json_default(value: Any) -> str:
    if isinstance(value, (date, datetime)):
        return value.isoformat()

    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")

def get_files(directory: str, file_types: list[str]=[]) -> list[str]:
    # Use '**' to search recursively and file_types to match specific file types
    pattern = os.path.join(directory, '**', '*')
    files = [f for f in glob.glob(pattern, recursive=True) if os.path.isfile(f)]

    if file_types:
        files = [f for f in files if any(f.endswith(ft) for ft in file_types)]

    return files


def get_files_from_directories(directories: list[str], file_types: list[str]=[]) -> list[str]:
    files = []

    for directory in directories:
        files += get_files(directory, file_types)

    return files

def save_json(data: Any, file_path: str) -> None:
    directory = os.path.dirname(file_path)

    if not os.path.exists(directory):
        os.makedirs(directory)

    if is_dataclass(data) and not isinstance(data, type):
        data = asdict(data)

    if not isinstance(data, str):
        data = json.dumps(data, indent=2, default=json_default)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(data)


def load_json(file_path: str) -> Any:
    directory = os.path.dirname(file_path)

    if directory and not os.path.exists(directory):
        return None

    with open(file_path, 'r', encoding='utf-8') as file:
        return json.loads(file.read())

def get_current_directory():
    return os.path.abspath(os.path.curdir)
