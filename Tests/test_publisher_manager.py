import tempfile
import types
import sys
import os
import importlib
from unittest import TestCase
from unittest.mock import patch

from Classes.config import BlueskyData, PlatformDataCollection, YoutubeData
from Classes.publication import TextPublication, VideoPublication
from Classes.schedule import Schedule
from Classes.video import Video


def _import_publisher_manager():
    youtube_stub = types.ModuleType("youtube_upload_video")
    setattr(youtube_stub, "post_youtube_video", lambda **kwargs: "stub-id")

    bluesky_stub = types.ModuleType("bluesky_post")
    setattr(bluesky_stub, "post_bluesky_with_youtube_video", lambda **kwargs: None)
    setattr(bluesky_stub, "post_bluesky", lambda **kwargs: None)

    with patch.dict(sys.modules, {"youtube_upload_video": youtube_stub, "bluesky_post": bluesky_stub}):
        module_name = "Classes.publisher_manager"
        if module_name in sys.modules:
            module = importlib.reload(sys.modules[module_name])
        else:
            module = importlib.import_module(module_name)

    return module


class PublisherManagerTests(TestCase):
    def test_publish_video_invokes_youtube_and_removes_from_schedule(self):
        publisher_manager_module = _import_publisher_manager()
        PublisherManager = publisher_manager_module.PublisherManager
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_video_path = os.path.join(temp_dir, "video.mp4")
            with open(temp_video_path, "wb") as f:
                f.write(b"video-bytes")

            publication = VideoPublication(
                video=Video(temp_video_path),
                platform_data=PlatformDataCollection(
                    youtube=YoutubeData(description="d", tags=["t"], category="22", privacy_status="public"),
                ),
            )
            schedule = Schedule([publication])
            manager = PublisherManager(schedule)
            events = []
            manager.on_published += lambda p: events.append(p)

            youtube_instance = type("StubYoutube", (), {"video_id": "abc", "publish": lambda self: None})()
            with patch.object(publisher_manager_module, "YoutubePublisher", return_value=youtube_instance) as youtube_ctor:
                manager.publish(publication)

            youtube_ctor.assert_called_once_with(publication)
            self.assertEqual([], schedule.publication_list)
            self.assertEqual([publication], events)

    def test_publish_text_bluesky_uses_bluesky_with_video_publisher(self):
        publisher_manager_module = _import_publisher_manager()
        PublisherManager = publisher_manager_module.PublisherManager
        publication = TextPublication(
            text="hello",
            platform_data=PlatformDataCollection(bluesky=BlueskyData(text="hello", tags=[])),
        )
        schedule = Schedule([publication])
        manager = PublisherManager(schedule)

        bluesky_instance = type("StubBluesky", (), {"publish": lambda self: None})()
        with patch.object(publisher_manager_module, "BlueskyWithVideoPublisher", return_value=bluesky_instance) as bluesky_ctor:
            manager.publish(publication)

        bluesky_ctor.assert_called_once_with(publication, "")
        self.assertEqual([], schedule.publication_list)
