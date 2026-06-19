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
        return {"version": 1, "updated_at": None, "folders": {}}

    state = load_json(state_path)
    if not isinstance(state, dict):
        return {"version": 1, "updated_at": None, "folders": {}}

    state.setdefault("version", 1)
    state.setdefault("updated_at", None)
    state.setdefault("folders", {})
    return state


def save_upload_state(config_file_path: str, state: dict[str, Any]) -> None:
    state["updated_at"] = datetime.now().isoformat()
    save_json(state, get_upload_state_path(config_file_path))


def normalize_folder_key(folder_path: str) -> str:
    return os.path.normcase(os.path.abspath(folder_path))


def _ensure_folder_state(state: dict[str, Any], folder_path: str) -> dict[str, Any]:
    folders = state.setdefault("folders", {})
    folder_key = normalize_folder_key(folder_path)
    folder_state = folders.get(folder_key)

    if not isinstance(folder_state, dict):
        folder_state = {"status": "active", "uploaded_ids": []}
        folders[folder_key] = folder_state

    folder_state.setdefault("status", "active")
    folder_state.setdefault("uploaded_ids", [])
    return folder_state


def get_uploaded_ids(state: dict[str, Any], folder_path: str) -> set[str]:
    folder_state = _ensure_folder_state(state, folder_path)
    return set(folder_state.get("uploaded_ids", []))


def is_folder_completed(state: dict[str, Any], folder_path: str) -> bool:
    folder_state = _ensure_folder_state(state, folder_path)
    return folder_state.get("status") == "completed"


def mark_uploaded(config_file_path: str, folder_path: str, video_id: str) -> None:
    state = load_upload_state(config_file_path)
    folder_state = _ensure_folder_state(state, folder_path)
    uploaded_ids = set(folder_state.get("uploaded_ids", []))

    uploaded_ids.add(video_id)
    folder_state["uploaded_ids"] = sorted(uploaded_ids)
    save_upload_state(config_file_path, state)


def mark_folder_completed(config_file_path: str, folder_path: str) -> None:
    state = load_upload_state(config_file_path)
    folder_state = _ensure_folder_state(state, folder_path)
    folder_state["status"] = "completed"
    folder_state["uploaded_ids"] = []
    save_upload_state(config_file_path, state)