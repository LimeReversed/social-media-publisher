import os
from datetime import datetime
from typing import Any

from Helpers.file_helper import load_json, save_json


def get_upload_state_path(config_file_path: str) -> str:
    if config_file_path.endswith(".schedule.json"):
        return config_file_path[:-len(".schedule.json")] + ".uploaded.json"
    return config_file_path + ".uploaded.json"


def load_upload_state(config_file_path: str) -> dict[str, Any]:
    state_path = get_upload_state_path(config_file_path)

    if not os.path.exists(state_path):
        return {"folders": {}}

    state = load_json(state_path)
    if not isinstance(state, dict):
        return {"folders": {}}

    state.setdefault("folders", {})
    return state


def save_upload_state(config_file_path: str, state: dict[str, Any]) -> None:
    save_json(state, get_upload_state_path(config_file_path))


def normalize_folder_key(folder_path: str) -> str:
    return os.path.normcase(os.path.abspath(folder_path))


def _ensure_folder_state(state: dict[str, Any], folder_path: str) -> dict[str, Any]:
    folders = state.setdefault("folders", {})
    folder_key = normalize_folder_key(folder_path)
    folder_state = folders.get(folder_key)

    if not isinstance(folder_state, dict):
        folder_state = {"uploaded_items": {}}
        folders[folder_key] = folder_state

    # Migrate legacy list-based format to map-based metadata format.
    if "uploaded_items" not in folder_state:
        legacy_ids = folder_state.get("uploaded_ids", [])
        uploaded_items: dict[str, dict[str, Any]] = {}
        if isinstance(legacy_ids, list):
            for video_id in legacy_ids:
                if isinstance(video_id, str):
                    uploaded_items[video_id] = {"name": "", "uploaded_at": None}
        folder_state["uploaded_items"] = uploaded_items

    if not isinstance(folder_state.get("uploaded_items"), dict):
        folder_state["uploaded_items"] = {}

    return folder_state


def get_uploaded_ids(state: dict[str, Any], folder_path: str) -> set[str]:
    folder_state = _ensure_folder_state(state, folder_path)
    uploaded_items = folder_state.get("uploaded_items", {})
    if not isinstance(uploaded_items, dict):
        return set()
    return set(uploaded_items.keys())


def mark_uploaded(config_file_path: str, folder_path: str, video_id: str, name: str) -> None:
    state = load_upload_state(config_file_path)
    folder_state = _ensure_folder_state(state, folder_path)
    uploaded_items = folder_state.setdefault("uploaded_items", {})
    uploaded_items[video_id] = {
        "name": name,
        "uploaded_at": datetime.now().isoformat(),
    }
    save_upload_state(config_file_path, state)