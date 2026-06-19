from abc import ABC, abstractmethod
from youtube_upload_video import post_youtube_video
from bluesky_post import post_bluesky_with_youtube_video, post_bluesky


# https://medium.com/@johnie5/using-python-to-gather-files-and-file-data-within-a-directory-323ce78346c2
  
class Publisher(ABC):
    def __init__(self, description: str):
        self.description: str = description

    @abstractmethod
    def publish(self):
        ...

class YoutubePublisher(Publisher):
    def __init__(self, description: str, title: str, video_path: str, category: str = "22", tags: str = "", privacy_status: str = "public"):
        super().__init__(description)
        self.video_path: str = video_path
        self.title: str = title
        self.category: str = category
        self.tags: str = tags
        self.privacy_status: str = privacy_status
        self.type: str = "YouTube"
        self.video_id: str = ""

    def publish(self):
        self.video_id = post_youtube_video(
            video_path=self.video_path,
            title=self.title,
            description=self.description,
            category=self.category,
            keywords=self.tags,
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