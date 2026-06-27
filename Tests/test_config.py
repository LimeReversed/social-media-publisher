from unittest import TestCase
import datetime
import os
from typing import cast
from Classes.config import BlueskyData, Config, FolderItem, MediaItem, PlatformDataCollection, PostItem, SpecificUploadTime, UploadTime, YoutubeData
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

    def test_from_dict__supports_global_platform_data_folders_posts_and_specific_upload_times(self):
        config_data = {
            "startDate": "2026-06-01",
            "uploadTimes": [{"day": 3, "hour": 13, "minute": 0}],
            "globalPlatformData": {
                "all": {"tags": ["common-tag"]},
                "youtube": {
                    "description": "Global youtube description",
                    "tags": ["youtube-tag"],
                    "category": "22",
                    "privacy_status": "public",
                },
                "bluesky": {
                    "text": "Global bluesky text",
                    "tags": ["bluesky-tag"],
                    "media": [{"type": "video_link", "source": "youtube", "sourceType": "result_from_upload"}],
                },
            },
            "folders": [
                {
                    "folder": os.path.abspath("./Tests/TestVideos"),
                    "folderType": "file_path",
                    "platformData": {
                        "all": {"tags": ["folder-common-tag"]},
                        "youtube": {
                            "description": "Folder youtube description",
                            "tags": ["folder-youtube-tag"],
                            "category": "23",
                            "privacy_status": "private",
                        },
                    },
                }
            ],
            "posts": [
                {
                    "platformData": {
                        "all": {"tags": ["post-common-tag"]},
                        "bluesky": {
                            "text": "Post bluesky text",
                            "tags": ["post-bluesky-tag"],
                        },
                    }
                }
            ],
            "specificUploadTimes": [
                {
                    "date": "2026-06-15",
                    "time": "13:00",
                    "platformData": {
                        "all": {"tags": ["specific-common-tag"]},
                        "youtube": {
                            "description": "Specific youtube description",
                            "tags": ["specific-youtube-tag"],
                            "category": "24",
                            "privacy_status": "public",
                        },
                    },
                }
            ],
        }

        config = Config.from_dict("dummy.json", config_data)

        self.assertEqual(1, len(config.folders))
        self.assertEqual(1, len(config.posts))
        self.assertEqual(1, len(config.specific_upload_times))

        youtube_data = config.platform_data.youtube
        bluesky_data = config.platform_data.bluesky

        self.assertIsNotNone(youtube_data)
        self.assertIsNotNone(bluesky_data)
        youtube_data = cast(YoutubeData, youtube_data)
        bluesky_data = cast(BlueskyData, bluesky_data)
        self.assertEqual(["common-tag", "youtube-tag"], youtube_data.tags)
        self.assertEqual(["common-tag", "bluesky-tag"], bluesky_data.tags)
        self.assertIsNotNone(bluesky_data.media)
        media_items = cast(list[MediaItem], bluesky_data.media)
        self.assertEqual(1, len(media_items))
        self.assertEqual("result_from_upload", media_items[0].sourceType)

        folder = config.folders[0]
        self.assertEqual(os.path.abspath("./Tests/TestVideos"), folder.folder)
        folder_youtube = folder.platform_data.youtube
        self.assertIsNotNone(folder_youtube)
        folder_youtube = cast(YoutubeData, folder_youtube)
        self.assertEqual(["youtube-tag", "common-tag", "folder-common-tag", "folder-youtube-tag"], folder_youtube.tags)

        post = config.posts[0]
        self.assertIsInstance(post, PostItem)
        post_bluesky = post.platform_data.bluesky
        self.assertIsNotNone(post_bluesky)
        post_bluesky = cast(BlueskyData, post_bluesky)
        self.assertEqual(["bluesky-tag", "common-tag", "post-common-tag", "post-bluesky-tag"], post_bluesky.tags)

        specific_upload_time = config.specific_upload_times[0]
        self.assertIsInstance(specific_upload_time, SpecificUploadTime)
        self.assertEqual(datetime.date(2026, 6, 15), specific_upload_time.date)
        self.assertEqual(datetime.time(13, 0), specific_upload_time.time)
        specific_youtube = specific_upload_time.platform_data.youtube
        self.assertIsNotNone(specific_youtube)
        specific_youtube = cast(YoutubeData, specific_youtube)
        self.assertEqual("Global youtube description\n\nSpecific youtube description", specific_youtube.description)