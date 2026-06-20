import os
import tempfile
from unittest import TestCase

from Helpers.upload_state_helper import (
    get_upload_state_path,
    get_uploaded_ids,
    load_upload_state,
    mark_uploaded,
    normalize_folder_key,
)


class UploadStateHelperTests(TestCase):
    def test_get_upload_state_path__replaces_schedule_suffix(self):
        config_path = os.path.join("C:/tmp", "name.schedule.json")

        result = get_upload_state_path(config_path)

        self.assertTrue(result.endswith("name.uploaded.json"))

    def test_mark_uploaded__persists_by_hash_with_name_and_timestamp(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "config.schedule.json")
            folder_path = os.path.join(temp_dir, "videos")

            mark_uploaded(config_path, folder_path, "b", "video-b")
            mark_uploaded(config_path, folder_path, "a", "video-a")
            # Duplicate id should update metadata, not create duplicates.
            mark_uploaded(config_path, folder_path, "a", "video-a-new")

            state = load_upload_state(config_path)
            folder_key = normalize_folder_key(folder_path)
            uploaded_items = state["folders"][folder_key]["uploaded_items"]

            self.assertEqual({"a", "b"}, set(uploaded_items.keys()))
            self.assertEqual("video-a-new", uploaded_items["a"]["name"])
            self.assertIsNotNone(uploaded_items["a"]["uploaded_at"])
            self.assertEqual("video-b", uploaded_items["b"]["name"])
            self.assertIsNotNone(uploaded_items["b"]["uploaded_at"])

    def test_get_uploaded_ids__reads_ids_from_uploaded_items_map(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "config.schedule.json")
            folder_path = os.path.join(temp_dir, "videos")

            mark_uploaded(config_path, folder_path, "x", "video-x")
            state = load_upload_state(config_path)
            uploaded_ids = get_uploaded_ids(state, folder_path)

            self.assertEqual({"x"}, uploaded_ids)
