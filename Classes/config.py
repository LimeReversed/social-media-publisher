from dataclasses import dataclass
import datetime
from enum import Enum
from typing import Any
from abc import ABC, abstractmethod

class Platforms(Enum):
    YOUTUBE = "youtube"
    BLUESKY = "bluesky"
    
@dataclass
class PlatformData(ABC):
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PlatformData":
        ...

@dataclass
class YoutubeData(PlatformData):
    description: str
    tags: list[str]
    category: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "YoutubeData":
        return cls(
            description=data.get("description", ""),
            tags=data.get("tags", []),
            category=data.get("category", 0),
        )


@dataclass
class BlueskyData(PlatformData):
    description: str
    tags: list[str]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BlueskyData":
        return cls(
            description=data.get("description", ""),
            tags=data.get("tags", []),
        )


@dataclass
class MapItem:
    map: str
    platform_data: dict[Platforms, PlatformData]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MapItem":
        return cls(
            map=data.get("map", ""),
            platform_data={Platforms(platform): PlatformData.from_dict(data) for platform, data in data.get("platformData", {}).items()},
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

@dataclass
class Config:
    config_file_path: str
    upload_times: list[UploadTime]
    start_time: datetime.datetime
    maps: list[MapItem]
    platform_data: dict[str, PlatformData]

    @classmethod
    def from_dict(cls, file_path: str, data: dict[str, Any]) -> "Config":
        
        start_date_string = data.get("startDate", data.get("startTime", None))
        start_time = datetime.datetime.now() if start_date_string == None else datetime.datetime.fromisoformat(start_date_string) 
        
        return cls(
            config_file_path=file_path,
            upload_times=[UploadTime.from_dict(item) for item in data.get("uploadTimes", [])],
            start_time=start_time,
            maps=[MapItem.from_dict(item) for item in data.get("maps", [])],
            platform_data= PlatformData.from_dict(data.get("metaData", {})),
        )
