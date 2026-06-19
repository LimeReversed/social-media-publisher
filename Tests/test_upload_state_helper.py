import os
import tempfile
from unittest import TestCase

from Helpers.upload_state_helper import (
    get_upload_state_path,
    load_upload_state,
    mark_folder_completed,
    mark_uploaded,
    normalize_folder_key,
)


class UploadStateHelperTests(TestCase):
    def test_get_upload_state_path_replaces_schedule_suffix(self):
        config_path = os.path.join("C:/tmp", "name.schedule.json")

        result = get_upload_state_path(config_path)

        self.assertTrue(result.endswith("name.uploaded.json"))

    def test_mark_uploaded_persists_unique_sorted_ids(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "config.schedule.json")
            folder_path = os.path.join(temp_dir, "videos")

            mark_uploaded(config_path, folder_path, "b")
            mark_uploaded(config_path, folder_path, "a")
            mark_uploaded(config_path, folder_path, "a")

            state = load_upload_state(config_path)
            folder_key = normalize_folder_key(folder_path)
            self.assertEqual(["a", "b"], state["folders"][folder_key]["uploaded_ids"])
            self.assertEqual("active", state["folders"][folder_key]["status"])

    def test_mark_folder_completed_sets_status_and_clears_ids(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "config.schedule.json")
            folder_path = os.path.join(temp_dir, "videos")

            mark_uploaded(config_path, folder_path, "x")
            mark_folder_completed(config_path, folder_path)

            state = load_upload_state(config_path)
            folder_key = normalize_folder_key(folder_path)
            self.assertEqual("completed", state["folders"][folder_key]["status"])
            self.assertEqual([], state["folders"][folder_key]["uploaded_ids"])
