from abc import ABC, abstractmethod
from datetime import datetime
from Classes.config import PlatformData, Platforms
from Classes.video import Video
       
class Publication(ABC):
    """Abstract base class for publications. This, and it's subclasses, hold information about the publication, such as what, when and where to publish."""
    def __init__(self, platform_data: dict[Platforms, PlatformData], upload_time: datetime | None = None):
        self.upload_time: datetime | None = upload_time
        self.platform_data: dict[Platforms, PlatformData] = platform_data

    @abstractmethod
    def get_title(self):
        ...

class VideoPublication(Publication):
    """The publication classes hold information about the publication, such as what, when and where to publish."""
    def __init__(self, video: Video, platform_data: dict[Platforms, PlatformData], upload_time: datetime | None = None):
        self.upload_time: datetime | None = upload_time
        self.video: Video = video
        self.platform_data: dict[Platforms, PlatformData] = platform_data

    def get_title(self) -> str:
        return self.video.name