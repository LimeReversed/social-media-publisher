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
    @abstractmethod
    def from_dict(cls, data: dict[str, Any]) -> "PlatformData":
        ...

    @abstractmethod
    def merge(self, local: "PlatformData") -> "PlatformData":
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

    def merge(self, other: "YoutubeData") -> "YoutubeData":
        if not isinstance(other, YoutubeData):
            raise TypeError("YoutubeData can only merge with YoutubeData")

        return YoutubeData(
            description=merge_text(self.description, other.description),
            tags=merge_tags(self.tags, other.tags),
            category=other.category if other.category else self.category,
        )


@dataclass
class BlueskyData(PlatformData):
    text: str
    tags: list[str]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BlueskyData":
        return cls(
            text=data.get("text", ""),
            tags=data.get("tags", []),
        )

    def merge(self, other: "BlueskyData") -> "BlueskyData":
        if not isinstance(other, BlueskyData):
            raise TypeError("BlueskyData can only merge with BlueskyData")

        return BlueskyData(
            text=merge_text(self.text, other.text),
            tags=merge_tags(self.tags, other.tags),
        )


def merge_text(global_text: str, local_text: str) -> str:
    parts = [text for text in [global_text.strip(), local_text.strip()] if text]
    return "\n\n".join(parts)


def merge_tags(global_tags: list[str], local_tags: list[str]) -> list[str]:
    seen: set[str] = set()
    merged: list[str] = []

    for tag in [*global_tags, *local_tags]:
        if tag not in seen:
            seen.add(tag)
            merged.append(tag)

    return merged


class PlatformDataFactory:
    _platform_class_map: dict[Platforms, type[PlatformData]] = {
        Platforms.YOUTUBE: YoutubeData,
        Platforms.BLUESKY: BlueskyData,
    }

    @classmethod
    def create(cls, platform: Platforms, data: dict[str, Any]) -> PlatformData:
        platform_cls = cls._platform_class_map.get(platform)
        if platform_cls is None:
            raise ValueError(f"No PlatformData parser found for platform: {platform.value}")
        return platform_cls.from_dict(data)


def parse_platform_data_dict(raw_data: dict[str, Any]) -> dict[Platforms, PlatformData]:
    parsed: dict[Platforms, PlatformData] = {}
    for platform_key, payload in raw_data.items():
        platform = Platforms(platform_key)
        parsed[platform] = PlatformDataFactory.create(platform, payload)
    return parsed


@dataclass
class FolderItem:
    map: str
    platform_data: dict[Platforms, PlatformData]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FolderItem":
        map_platform_data = data.get("platformData", data.get("metaData", {}))
        return cls(
            map=data.get("map", ""),
            platform_data=parse_platform_data_dict(map_platform_data),
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
    folders: list[FolderItem]
    platform_data: dict[Platforms, PlatformData]

    @classmethod
    def from_dict(cls, file_path: str, data: dict[str, Any]) -> "Config":
        
        start_date_string = data.get("startDate", data.get("startTime", None))
        start_time = datetime.datetime.now() if start_date_string == None else datetime.datetime.fromisoformat(start_date_string) 
        
        return cls(
            config_file_path=file_path,
            upload_times=[UploadTime.from_dict(item) for item in data.get("uploadTimes", [])],
            start_time=start_time,
            folders=[FolderItem.from_dict(item) for item in data.get("folders", [])],
            platform_data=parse_platform_data_dict(data.get("platformData", {})),
        )
