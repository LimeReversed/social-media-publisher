from unittest import TestCase
from Classes.config import *
from Helpers.config_helper import *


class ConfigTests(TestCase):

    def test_load_config__should_load_config_from_file(self):
        platform_data = dict[str, PlatformData]()
        platform_data[Platforms.YOUTUBE.value] = YoutubeData(description="Youtube description", tags=["tag1"], category=22)
        platform_data[Platforms.BLUESKY.value] = BlueskyData(description="Bluesky description", tags=["tag2"])

        map_item = MapItem("./test_videos", platform_data)
        upload_times = [UploadTime(day=3, hour=13, minute=0), UploadTime(day=5, hour=11, minute=0)]
        start_time = datetime.datetime(2026, 6, 1)
        config_file_path = "test_config.json"
        expected = Config(config_file_path, upload_times, start_time, [map_item], platform_data)


        result = load_config(config_file_path)

        self.assertEqual(expected, result)