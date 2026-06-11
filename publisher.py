from abc import ABC, abstractmethod
from datetime import datetime
import time
from enum import Enum
import hashlib
import os
from Classes.config import MetaData
from youtube_upload_video import post_youtube_video
from bluesky_post import post_bluesky_with_youtube_video, post_bluesky

# UploadDate
# Thumbnail
# VideoId
# Category
# Description
# Title
# Tags
# PrivacyStatus
# VideoPath
# VideoUrl
# Type - Youtube, Bluesky
# https://medium.com/@johnie5/using-python-to-gather-files-and-file-data-within-a-directory-323ce78346c2

class Video:
    def __init__(self, path: str):
        self.path: str = path
        self.name: str = os.path.splitext(os.path.basename(path))[0]
        self.creation_time: float = os.path.getctime(path)
        self.video_id: str = self.hash_video_file(self.path)

    def hash_video_file(self, path: str, chunk_size: int = 1024 * 1024) -> str:
        digest = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(chunk_size):
                digest.update(chunk)
        return digest.hexdigest()
    
class Publisher(ABC):
    def __init__(self, description: str):
        self.description: str = description

    @abstractmethod
    def publish(self):
        ...

class YoutubePublisher(Publisher):
    def __init__(self, description: str, title: str, video_path: str, category: str = "22", keywords: str = "", privacy_status: str = "public"):
        super().__init__(description)
        self.video_path: str = video_path
        self.title: str = title
        self.category: str = category
        self.keywords: str = keywords
        self.privacy_status: str = privacy_status
        self.type: str = "YouTube"
        self.video_id: str = ""

    def publish(self):
        self.video_id = post_youtube_video(
            video_path=self.video_path,
            title=self.title,
            description=self.description,
            category=self.category,
            keywords=self.keywords,
            privacy_status=self.privacy_status
        )

class BlueskyPublisher(Publisher):
    def __init__(self, description: str):
        super().__init__(description)
        self.type: str = "Bluesky"

    def publish(self):
        post_bluesky(text=self.description)

class BlueskyWithVideoPublisher(BlueskyPublisher):
    def __init__(self, description: str, youtube_video_id: str = ""):
        super().__init__(description)
        self.youtube_video_id: str = youtube_video_id

    def publish(self):
        post_bluesky_with_youtube_video(
            text=self.description,
            video_id=self.youtube_video_id,
            title="",
            description=""
        )

class Platsforms(Enum):
    YOUTUBE = "YouTube"
    BLUESKY = "Bluesky"
    
class Publication:
    def __init__(self, video: Video | None = None, meta_data: MetaData | None = None, upload_time: datetime | None = None):
        self.publishers: dict[str, Publisher] = {}
        self.upload_time: datetime | None = upload_time
        self.video: Video | None = video

        youtube_post = YoutubePublisher(
            description=meta_data.youtube.description,
            title=meta_data.youtube.titlePrefix + video.name,
            video_path=video.path,
            category=str(meta_data.youtube.category),
            keywords=",".join(meta_data.youtube.tags)
        )

        bluesky_post = BlueskyWithVideoPublisher(
            # FIX maybe should be the name of the file. 
            description=meta_data.bluesky.description,
            youtube_video_id=youtube_post.video_id
        )

        self.add_publisher(Platsforms.YOUTUBE, youtube_post)
        self.add_publisher(Platsforms.BLUESKY, bluesky_post)


    def add_publisher(self, platform: Platsforms, publisher: Publisher):
        self.publishers[platform.value] = publisher

    def publish_all(self):
        # Important to post YouTube first to get the video ID for the Bluesky post if needed
        if Platsforms.YOUTUBE.value in self.publishers:
            self.publishers[Platsforms.YOUTUBE.value].publish()
            self.publishers[Platsforms.BLUESKY.value].youtube_video_id = self.publishers[Platsforms.YOUTUBE.value].video_id

        time.sleep(300)  # Small delay to ensure YouTube video ID is available for Bluesky post
        # Here we can loop through the rest:
        for platform, publisher in self.publishers.items():
            if platform != Platsforms.YOUTUBE.value:
                publisher.publish()