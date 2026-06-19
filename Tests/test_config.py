from unittest import TestCase, result
from Classes.config import *
from Helpers.config_helper import *
import os
from pprint import pformat
from dataclasses import asdict
class ConfigTests(TestCase):

    def test_platform_data_merge__should_concat_description_and_dedupe_tags(self):
        global_youtube = YoutubeData(description="global description", tags=["tag1", "tag2"], category=22)
        local_youtube = YoutubeData(description="local description", tags=["tag2", "tag3"], category=0)
        merged_youtube = global_youtube.merge(local_youtube)

        self.assertEqual("global description\n\nlocal description", merged_youtube.description)
        self.assertEqual(["tag1", "tag2", "tag3"], merged_youtube.tags)
        self.assertEqual(22, merged_youtube.category)

        global_bluesky = BlueskyData(text="global post", tags=["a", "b"])
        local_bluesky = BlueskyData(text="local post", tags=["b", "c"])
        merged_bluesky = global_bluesky.merge(local_bluesky)

        self.assertEqual("global post\n\nlocal post", merged_bluesky.text)
        self.assertEqual(["a", "b", "c"], merged_bluesky.tags)

    def test_load_config__should_load_config_from_file(self):
        platform_data = dict[Platforms, PlatformData]()
        platform_data[Platforms.YOUTUBE] = YoutubeData(description="Youtube description", tags=["tag1"], category=22)
        platform_data[Platforms.BLUESKY] = BlueskyData(text="Bluesky description", tags=["tag2"])

        map_item = FolderItem("./test_videos", platform_data)
        global_platform_data = dict[Platforms, PlatformData]()
        global_platform_data[Platforms.YOUTUBE] = YoutubeData(description="", tags=[], category=0)
        global_platform_data[Platforms.BLUESKY] = BlueskyData(text="", tags=[])
        upload_times = [UploadTime(day=3, hour=13, minute=0), UploadTime(day=5, hour=11, minute=0)]
        start_time = datetime.datetime(2026, 6, 1)
        config_file_path = os.path.abspath("./Tests/mocks/config_mock_1.schedule.json")

        expected = Config(config_file_path, upload_times, start_time, [map_item], global_platform_data)
        result = load_config(config_file_path)
        # print("EXPECTED:\n" + pformat(asdict(expected), sort_dicts=False, width=100))
        # print("RESULT:\n" + pformat(asdict(result), sort_dicts=False, width=100))
        self.assertEqual(expected, result)