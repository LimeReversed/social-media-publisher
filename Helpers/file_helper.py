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

def get_files_by_file_type(directory: str, file_pattern: str) -> list[str]:
    """
    Get file paths by glob pattern.

    Args:
        directory (str): Directory to search for files.
        file_pattern (str): File glob pattern to search for (for example '*.mp4').

    Returns:
        list[str]: List of file paths.
    """
    # Use '**' to search recursively and file patterns to match specific file names.
    files = []

    pattern = os.path.join(directory, '**', file_pattern)
    # glob.glob returns paths in the same form as the pattern you pass in. To ensure we use os.path.abspath on each result.
    files = [os.path.abspath(f) for f in glob.glob(pattern, recursive=True) if os.path.isfile(f)]

    return files

def get_files_by_multiple_file_types(directory: str, file_patterns: list[str]) -> list[str]:
    """
    Get files paths by multiple glob patterns.

    Args:
        directory (str): Directory to search for files.
        file_patterns (list[str]): List of file glob patterns to search for (for example ['*.mp4', '*.mov']).

    Returns:
        list[str]: List of file paths.
    """
    files = []

    for file_pattern in file_patterns:
        files += get_files_by_file_type(directory, file_pattern)
        
    return files



def get_files_from_directories(directories: list[str], file_patterns: list[str]) -> list[str]:
    files = []

    for directory in directories:
        files += get_files_by_multiple_file_types(directory, file_patterns)

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
