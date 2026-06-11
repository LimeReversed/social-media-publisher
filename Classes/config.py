from dataclasses import dataclass
import datetime
from typing import Any

@dataclass
class YouTubeMeta:
    titlePrefix: str
    description: str
    tags: list[str]
    category: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "YouTubeMeta":
        return cls(
            titlePrefix=data.get("titlePrefix", ""),
            description=data.get("description", ""),
            tags=data.get("tags", []),
            category=data.get("category", 0),
        )


@dataclass
class BlueskyMeta:
    description: str
    tags: list[str]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BlueskyMeta":
        return cls(
            description=data.get("description", ""),
            tags=data.get("tags", []),
        )


@dataclass
class MetaData:
    youtube: YouTubeMeta
    bluesky: BlueskyMeta

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MetaData":
        return cls(
            youtube=YouTubeMeta.from_dict(data.get("youtube", {})),
            bluesky=BlueskyMeta.from_dict(data.get("bluesky", {})),
        )


@dataclass
class MapItem:
    map: str
    metaData: MetaData

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MapItem":
        return cls(
            map=data.get("map", ""),
            metaData=MetaData.from_dict(data.get("metaData", {})),
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
    uploadTimes: list[UploadTime]
    startTime: datetime.datetime
    uploaded: list[str]
    maps: list[MapItem]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Config":
        
        start_date_string = data.get("startDate", data.get("startTime", None))
        start_time = datetime.datetime.now() if start_date_string == None else datetime.datetime.fromisoformat(start_date_string) 
        
        return cls(
            uploadTimes=[UploadTime.from_dict(item) for item in data.get("uploadTimes", [])],
            startTime=start_time,
            uploaded=data.get("uploaded", []),
            maps=[MapItem.from_dict(item) for item in data.get("maps", [])],
        )
