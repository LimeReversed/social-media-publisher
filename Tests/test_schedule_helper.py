import datetime
import os
from unittest import TestCase
from Classes.config import BlueskyData, PlatformDataCollection, UploadTime, YoutubeData
from Classes.publication import Publication, TextPublication, VideoPublication
from Classes.schedule import Schedule
from Classes.upload_times import UploadTimes
from Helpers.config_helper import load_config
from Helpers.schedule_helper import constuct_schedule_from_config_list, merge_platform_data, populate_upload_times


class ScheduleHelperTests(TestCase):
    def create_schedule_from_config(self, config_file_path: str) -> Schedule:
        config_file_path = os.path.abspath("./Tests/Mocks/config_mock_1.schedule.json")
        config = load_config(config_file_path)
        return constuct_schedule_from_config_list([config])
    
    def test_merge_platform_data__merges_each_platform_correctly(self):
        #FIX: Double check that this merge logic is correct and matches the expected behavior in the application.
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

    def test_populate_upload_times__sets_upload_time_on_each_publication(self):
        publications: list[Publication] = [
            TextPublication("one", PlatformDataCollection()),
            TextPublication("two", PlatformDataCollection()),
        ]
        upload_times = UploadTimes(
            [UploadTime(day=0, hour=9, minute=0), UploadTime(day=1, hour=9, minute=0)],
            datetime.datetime(2026, 6, 1, 0, 0),
        )

        result = populate_upload_times(publications, upload_times)

        self.assertEqual(2, len(result))
        self.assertEqual(result[0].upload_time, datetime.datetime(2026, 6, 1, 9, 0))
        self.assertEqual(result[1].upload_time, datetime.datetime(2026, 6, 2, 9, 0))

    def test_construct_schedule_from_config_list__schedule_has_items(self):
        schedule = self.create_schedule_from_config("./Tests/Mocks/config_mock_1.schedule.json")
        self.assertEqual(2, len(schedule.publication_list), "Expected schedule to have two publications from the test videos")
    
    def test_construct_schedule_from_config_list__creates_video_publications(self):
        schedule = self.create_schedule_from_config("./Tests/Mocks/config_mock_1.schedule.json")
        
        for publication in schedule.publication_list:
            if not isinstance(publication, VideoPublication):
                self.fail("Expected all publications to be VideoPublications")
                return
    
    def test_construct_schedule_from_config_list__creates_expected_youtube_data(self):
        schedule = self.create_schedule_from_config("./Tests/Mocks/config_mock_1.schedule.json")
        publication = schedule.publication_list[0]

        if not isinstance(publication, VideoPublication):
            self.fail("Expected a VideoPublication")
            return
        
        if publication.platform_data.youtube is None:
            self.fail("Expected publication to have a youtube data")
            return
        
        self.assertEqual(os.path.abspath("./Tests/TestVideos/test_video_1.mp4"), publication.video.path)
        self.assertEqual("Youtube description", publication.platform_data.youtube.description)
        self.assertEqual(["tag1"], publication.platform_data.youtube.tags)
        self.assertEqual("22", publication.platform_data.youtube.category)
        self.assertEqual("public", publication.platform_data.youtube.privacy_status)

    def test_construct_schedule_from_config_list__creates_expected_bluesky_data(self):
            schedule = self.create_schedule_from_config("./Tests/Mocks/config_mock_1.schedule.json")
            publication = schedule.publication_list[0]

            if not isinstance(publication, VideoPublication):
                self.fail("Expected a VideoPublication")
                return
            
            self.assertIsNotNone(publication.platform_data.bluesky)

            if publication.platform_data.bluesky is None:
                self.fail("Expected publication to have a bluesky data")
                return
            
            self.assertEqual("Bluesky description", publication.platform_data.bluesky.text)
            self.assertEqual(["tag2"], publication.platform_data.bluesky.tags)


