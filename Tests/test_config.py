from unittest import TestCase
import datetime
import os
from Classes.config import BlueskyData, Config, FolderItem, PlatformDataCollection, UploadTime, YoutubeData
from Helpers.config_helper import load_config

class ConfigTests(TestCase):

    def create_expected_config(self, config_file_path: str) -> Config:
        platform_data = PlatformDataCollection(
            youtube=YoutubeData(description="Youtube description", tags=["tag1"], category="22", privacy_status="public"),
            bluesky=BlueskyData(text="Bluesky description", tags=["tag2"]),
        )

        folder_item = FolderItem(os.path.abspath("./Tests/TestVideos"), platform_data)
        global_platform_data = PlatformDataCollection(
            youtube=YoutubeData(description="", tags=[], category="", privacy_status="public"),
            bluesky=BlueskyData(text="", tags=[]),
        )
        upload_times = [UploadTime(day=3, hour=13, minute=0), UploadTime(day=5, hour=11, minute=0)]
        start_time = datetime.datetime(2026, 6, 1)

        return Config(config_file_path, upload_times, start_time, [folder_item], global_platform_data)
    
    def test_platform_data_merge__concats_description_and_dedupes_tags(self):
        global_youtube = YoutubeData(description="global description", tags=["tag1", "tag2"], category="22", privacy_status="public")
        local_youtube = YoutubeData(description="local description", tags=["tag2", "tag3"], category="", privacy_status="")
        merged_youtube = global_youtube.merge(local_youtube)

        self.assertEqual("global description\n\nlocal description", merged_youtube.description)
        self.assertEqual(["tag1", "tag2", "tag3"], merged_youtube.tags)
        self.assertEqual("22", merged_youtube.category)
        self.assertEqual("public", merged_youtube.privacy_status)

        global_bluesky = BlueskyData(text="global post", tags=["a", "b"])
        local_bluesky = BlueskyData(text="local post", tags=["b", "c"])
        merged_bluesky = global_bluesky.merge(local_bluesky)

        self.assertEqual("global post\n\nlocal post", merged_bluesky.text)
        self.assertEqual(["a", "b", "c"], merged_bluesky.tags)

    def test_load_config__loads_config_from_file(self):
        config_file_path = os.path.abspath("./Tests/Mocks/config_mock_1.schedule.json")

        expected = self.create_expected_config(config_file_path)
        result = load_config(config_file_path)
        self.assertEqual(expected, result)