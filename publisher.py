from abc import ABC, abstractmethod
from datetime import datetime
import time
from enum import Enum
import hashlib
import os
from Classes.config import MetaData
from youtube_upload_video import post_youtube_video
from bluesky_post import post_bluesky_with_youtube_video, post_bluesky
from Classes.upload_times import UploadTimes
from Classes.config import Config
from Helpers.file_helper import *

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
    def __init__(self, video: Video, meta_data: MetaData, upload_time: datetime | None = None):
        self.publishers: dict[str, Publisher] = {}
        self.upload_time: datetime | None = upload_time
        self.video: Video = video
        self.meta_data: MetaData = meta_data

        self.youtube_post = YoutubePublisher(
            description=meta_data.youtube.description,
            title=self.get_title(),
            video_path=video.path,
            category=str(meta_data.youtube.category),
            keywords=",".join(meta_data.youtube.tags)
        )

        self.bluesky_post = BlueskyWithVideoPublisher(
            description=self.get_title()
        )

    def publish_all(self):
        # Important to post YouTube first to get the video ID.
        self.youtube_post.publish()
        self.bluesky_post.youtube_video_id = self.youtube_post.video_id

        time.sleep(300)  # Delay to ensure YouTube video ID is available for the publishers that need it.
        self.bluesky_post.publish()

    def get_title(self) -> str:
        return self.meta_data.youtube.titlePrefix + self.video.name
    

class Publications:
    def __init__(self, publication_list: list[Publication], upload_times: UploadTimes):
        self.publication_list: list[Publication] = publication_list
        self.upload_times: UploadTimes = upload_times
        self.sort_by_creation_time()
        self.populate_upload_times()

    @classmethod
    def constuct_from_config(cls, config: Config) -> "Publications":
        upload_times = UploadTimes(config.uploadTimes, config.startTime)

        publish_list: list[Publication] = []
        for map_item in config.maps:
            map_path = map_item.map
            video_paths = get_files(map_path, file_types=[".mp4", ".mov", ".avi", ".mkv"])
            
            # Initialze Video
            for video_path in video_paths:
                video = Video(video_path)

                # Initialize Publication with video and add to publish_list
                if not video.video_id in config.uploaded:
                    publication = Publication(video=video, meta_data=map_item.metaData)
                    publish_list.append(publication)

        return Publications(publish_list, upload_times)

    def sort_by_creation_time(self) -> None:
        self.publication_list.sort(key=lambda pub: pub.video.creation_time if pub.video else float('inf'))

    def populate_upload_times(self) -> None:
        for publication in self.publication_list:
            publication.upload_time = self.upload_times.pop()

    def print_next_publish(self) -> None:
        # Using datetime.max because uploade_time can be None and therefore lambda is refusing it unless I set a fallback. 
        next_publication = min(self.publication_list, key=lambda pub: pub.upload_time or datetime.max)
        
        print(f"Next publish: {next_publication.video.name} at {next_publication.upload_time}")

    def print_schedule(self):
        for publication in self.publication_list:
            print(f"{publication.video.name} at {publication.upload_time}")