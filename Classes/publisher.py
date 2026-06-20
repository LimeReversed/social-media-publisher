from abc import ABC, abstractmethod
from Classes.publication import *
from youtube_upload_video import post_youtube_video
from bluesky_post import post_bluesky_with_youtube_video, post_bluesky

# https://medium.com/@johnie5/using-python-to-gather-files-and-file-data-within-a-directory-323ce78346c2
  
class Publisher(ABC):
    def __init__(self):
        ...

    @abstractmethod
    def publish(self):
        ...

class YoutubePublisher(Publisher):
    def __init__(self, publication: VideoPublication):
        super().__init__()
        self.description: str = publication.platform_data.youtube.description if publication.platform_data.youtube else ""
        self.video_path: str = publication.video.path
        self.title: str = publication.video.name
        self.category: str = publication.platform_data.youtube.category if publication.platform_data.youtube else ""
        self.tags: list[str] = publication.platform_data.youtube.tags if publication.platform_data.youtube else []
        self.privacy_status: str = publication.platform_data.youtube.privacy_status if publication.platform_data.youtube else ""
        self.video_id: str = ""

    def publish(self):
        self.video_id = post_youtube_video(
            video_path=self.video_path,
            title=self.title,
            description=self.description,
            category=self.category,
            keywords=",".join(self.tags),
            privacy_status=self.privacy_status
        )

class BlueskyPublisher(Publisher):
    def __init__(self, publication: TextPublication):
        super().__init__()
        self.text: str = publication.text

    def publish(self):
        post_bluesky(text=self.text)

class BlueskyWithVideoPublisher(Publisher):
    def __init__(self, publication: VideoPublication, youtube_video_id: str = ""):
        super().__init__()
        self.youtube_video_id: str = youtube_video_id
        self.text: str = publication.get_name()

    def publish(self):
        post_bluesky_with_youtube_video(
            text=self.text,
            video_id=self.youtube_video_id,
            title="",
            description=""
        )