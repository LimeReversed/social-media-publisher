from dataclasses import dataclass
import datetime
from typing import Any
from abc import ABC
from platform_data import PlatformDataCollection

@dataclass
class MediaItem:
    type: str
    source: str
    sourceType: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MediaItem":
        return cls(
            type=data.get("type", ""),
            source=data.get("source", ""),
            sourceType=data.get("sourceType", ""),
        )

@dataclass
class FolderItem:
    folder: str
    platform_data: PlatformDataCollection

    @classmethod
    def from_dict(cls, data: dict[str, Any], global_platform_data: dict[str, Any] | None = None) -> "FolderItem":
        folder_platform_data = data.get("platformData", {})
        return cls(
            folder=data.get("folder", ""),
            platform_data=parse_platform_data_dict(folder_platform_data, global_platform_data),
        )


@dataclass
class PostItem:
    platform_data: PlatformDataCollection

    @classmethod
    def from_dict(cls, data: dict[str, Any], global_platform_data: dict[str, Any] | None = None) -> "PostItem":
        return cls(
            platform_data=parse_platform_data_dict(data.get("platformData", {}), global_platform_data),
        )


@dataclass
class SpecificUploadTime:
    date: datetime.date
    time: datetime.time
    platform_data: PlatformDataCollection

    @classmethod
    def from_dict(cls, data: dict[str, Any], global_platform_data: dict[str, Any] | None = None) -> "SpecificUploadTime":
        return cls(
            date=datetime.date.fromisoformat(data.get("date", "1970-01-01")),
            time=datetime.time.fromisoformat(data.get("time", "00:00")),
            platform_data=parse_platform_data_dict(data.get("platformData", {}), global_platform_data),
        )
    
@dataclass
class UploadTime:
    day: int
    hour: int
    minute: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UploadTime":
        return cls(
            day=data.get("day", 0),
            hour=data.get("hour", 0),
            minute=data.get("minute", 0),
        )

class Config(ABC):
    def __init__(self, config_file_path: str, global_platform_data: PlatformDataCollection):
        self.config_file_path: str = config_file_path
        self.global_platform_data: PlatformDataCollection = global_platform_data
    
    @classmethod
    def from_dict(cls, file_path: str, data: dict[str, Any]) -> "Config":
        ...

class FoldersConfig(Config):
    def __init__(self, config_file_path: str, global_platform_data: PlatformDataCollection, upload_times: list[UploadTime], start_time: datetime.datetime, folders: list[FolderItem]):
        super().__init__(config_file_path, global_platform_data) 
        self.upload_times: list[UploadTime] = upload_times
        self.start_time: datetime.datetime = start_time
        self.folders: list[FolderItem] = folders

    @classmethod
    def from_dict(cls, file_path: str, data: dict[str, Any]) -> "FoldersConfig":
        
        start_date_string = data.get("startDate", data.get("startTime", ""))
        start_time = datetime.datetime.now() if not start_date_string else datetime.datetime.fromisoformat(start_date_string)
        global_platform_data = data.get("globalPlatformData", data.get("platformData", {}))
        
        return cls(
            config_file_path=file_path,
            global_platform_data=parse_platform_data_dict(global_platform_data),
            upload_times=[UploadTime.from_dict(item) for item in data.get("uploadTimes", [])],
            start_time=start_time,
            folders=[FolderItem.from_dict(item, global_platform_data) for item in data.get("folders", [])],
            
        )

class PostsConfig(Config):
    def __init__(self, config_file_path: str, global_platform_data: PlatformDataCollection, upload_times: list[UploadTime], start_time: datetime.datetime, posts: list[PostItem]):
        super().__init__(config_file_path, global_platform_data) 
        self.upload_times: list[UploadTime] = upload_times
        self.start_time: datetime.datetime = start_time
        self.posts: list[PostItem] = posts

    @classmethod
    def from_dict(cls, file_path: str, data: dict[str, Any]) -> "Config":
        start_date_string = data.get("startDate", data.get("startTime", ""))
        start_time = datetime.datetime.now() if not start_date_string else datetime.datetime.fromisoformat(start_date_string)
        global_platform_data = data.get("globalPlatformData", data.get("platformData", {}))
        
        return cls(
            config_file_path=file_path,
            global_platform_data=parse_platform_data_dict(global_platform_data),
            upload_times=[UploadTime.from_dict(item) for item in data.get("uploadTimes", [])],
            start_time=start_time,
            posts=[PostItem.from_dict(item, global_platform_data) for item in data.get("posts", [])],
        )

class SpecificUploadTimesConfig(Config):
    def __init__(self, config_file_path: str, global_platform_data: PlatformDataCollection, posts: list[SpecificUploadTime]):
        super().__init__(config_file_path, global_platform_data) 
        self.posts: list[SpecificUploadTime] = posts

    @classmethod
    def from_dict(cls, file_path: str, data: dict[str, Any]) -> "Config":
        global_platform_data = data.get("globalPlatformData", data.get("platformData", {}))
        
        return cls(
            config_file_path=file_path,
            global_platform_data=parse_platform_data_dict(global_platform_data),
            posts=[SpecificUploadTime.from_dict(item, global_platform_data) for item in data.get("posts", [])],
        )
