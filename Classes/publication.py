from abc import ABC, abstractmethod
from datetime import datetime
from Classes.config import PlatformDataCollection
from Classes.video import Video
       
class Publication(ABC):
    """Abstract base class for publications. This, and it's subclasses, hold information about the publication, such as what, when and where to publish."""
    def __init__(self, platform_data: PlatformDataCollection, upload_time: datetime | None = None):
        self.upload_time: datetime | None = upload_time
        self.platform_data: PlatformDataCollection = platform_data

    @abstractmethod
    def get_name(self):
        ...

class TextPublication(Publication):
    """TextPublication is a subclass of Publication that represents a text-based publication, such as a post on a social media platform."""
    def __init__(self, text: str, platform_data: PlatformDataCollection, upload_time: datetime | None = None):
        super().__init__(platform_data=platform_data, upload_time=upload_time)
        self.text: str = text

    def get_name(self) -> str:
        return self.text
class VideoPublication(Publication):
    """The publication classes hold information about the publication, such as what, when and where to publish."""
    def __init__(
        self,
        video: Video,
        platform_data: PlatformDataCollection,
        upload_time: datetime | None = None,

        # FIX These are only used for tracking which videos have been published.
        config_file_path: str = "",
        source_folder: str = "",
    ):
        super().__init__(platform_data=platform_data, upload_time=upload_time)
        self.video: Video = video
        self.config_file_path: str = config_file_path
        self.source_folder: str = source_folder

    def get_name(self) -> str:
        return self.video.name