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
    def get_name(self):
        ...

class VideoPublication(Publication):
    """The publication classes hold information about the publication, such as what, when and where to publish."""
    def __init__(
        self,
        video: Video,
        platform_data: dict[Platforms, PlatformData],
        upload_time: datetime | None = None,
        config_file_path: str = "",
        source_folder: str = "",
    ):
        self.upload_time: datetime | None = upload_time
        self.video: Video = video
        self.platform_data: dict[Platforms, PlatformData] = platform_data
        self.config_file_path: str = config_file_path
        self.source_folder: str = source_folder

    def get_name(self) -> str:
        return self.video.name