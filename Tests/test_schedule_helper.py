import datetime
from unittest import TestCase

from Classes.config import BlueskyData, PlatformDataCollection, UploadTime, YoutubeData
from Classes.publication import Publication, TextPublication
from Classes.upload_times import UploadTimes
from Helpers.schedule_helper import merge_platform_data, populate_upload_times


class ScheduleHelperTests(TestCase):
    def test_merge_platform_data_merges_each_platform_correctly(self):
        global_data = PlatformDataCollection(
            youtube=YoutubeData(description="global", tags=["a", "b"], category="22", privacy_status="public"),
            bluesky=BlueskyData(text="hello", tags=["x"]),
        )
        local_data = PlatformDataCollection(
            youtube=YoutubeData(description="local", tags=["b", "c"], category="", privacy_status=""),
            bluesky=BlueskyData(text="world", tags=["x", "y"]),
        )

        merged = merge_platform_data(global_data, local_data)

        youtube = merged.youtube
        if youtube is None:
            self.fail("Expected merged youtube data")

        bluesky = merged.bluesky
        if bluesky is None:
            self.fail("Expected merged bluesky data")

        self.assertEqual("global\n\nlocal", youtube.description)
        self.assertEqual(["a", "b", "c"], youtube.tags)
        self.assertEqual("22", youtube.category)
        self.assertEqual("public", youtube.privacy_status)
        self.assertEqual("hello\n\nworld", bluesky.text)
        self.assertEqual(["x", "y"], bluesky.tags)

    def test_populate_upload_times_sets_upload_time_on_each_publication(self):
        publications: list[Publication] = [
            TextPublication("one", PlatformDataCollection()),
            TextPublication("two", PlatformDataCollection()),
        ]
        upload_times = UploadTimes(
            [UploadTime(day=0, hour=9, minute=0), UploadTime(day=1, hour=9, minute=0)],
            datetime.datetime(2026, 6, 19, 8, 0),
        )

        result = populate_upload_times(publications, upload_times)

        self.assertEqual(2, len(result))
        self.assertIsNotNone(result[0].upload_time)
        self.assertIsNotNone(result[1].upload_time)
