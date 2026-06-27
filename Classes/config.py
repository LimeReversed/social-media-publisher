from dataclasses import dataclass
import datetime
from enum import Enum
from typing import Any
from abc import ABC, abstractmethod


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
    category: str
    privacy_status: str
    media: list[MediaItem] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "YoutubeData":
        media_value = data.get("media")
        category_value = data.get("category", "")
        return cls(
            description=data.get("description", ""),
            tags=data.get("tags", []),
            category=category_value if category_value is not None else "",
            privacy_status=data.get("privacy_status", "public"),
            media=[MediaItem.from_dict(item) for item in media_value] if media_value is not None else None,
        )

    def merge(self, other: "YoutubeData") -> "YoutubeData":
        if not isinstance(other, YoutubeData):
            raise TypeError("YoutubeData can only merge with YoutubeData")

        return YoutubeData(
            description=merge_text(self.description, other.description),
            tags=merge_tags(self.tags, other.tags),
            category=other.category if other.category else self.category,
            privacy_status=other.privacy_status if other.privacy_status else self.privacy_status,
            media=merge_media(self.media, other.media),
        )


@dataclass
class BlueskyData(PlatformData):
    text: str
    tags: list[str]
    media: list[MediaItem] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BlueskyData":
        media_value = data.get("media")
        return cls(
            text=data.get("text", ""),
            tags=data.get("tags", []),
            media=[MediaItem.from_dict(item) for item in media_value] if media_value is not None else None,
        )

    def merge(self, other: "BlueskyData") -> "BlueskyData":
        if not isinstance(other, BlueskyData):
            raise TypeError("BlueskyData can only merge with BlueskyData")

        return BlueskyData(
            text=merge_text(self.text, other.text),
            tags=merge_tags(self.tags, other.tags),
            media=merge_media(self.media, other.media),
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


def merge_media(global_media: list[MediaItem] | None, local_media: list[MediaItem] | None) -> list[MediaItem] | None:
    if global_media is None and local_media is None:
        return None

    merged: list[MediaItem] = []
    seen: set[tuple[str, str, str]] = set()

    for media in [*(global_media or []), *(local_media or [])]:
        key = (media.type, media.source, media.sourceType)
        if key not in seen:
            seen.add(key)
            merged.append(media)

    return merged


def merge_payload_value(base: Any, override: Any) -> Any:
    if isinstance(base, dict) and isinstance(override, dict):
        merged_dict: dict[Any, Any] = dict(base)
        for key, value in override.items():
            if key in merged_dict:
                merged_dict[key] = merge_payload_value(merged_dict[key], value)
            else:
                merged_dict[key] = value
        return merged_dict

    if isinstance(base, list) and isinstance(override, list):
        merged_list: list[Any] = []
        seen: set[str] = set()
        for item in [*base, *override]:
            key = repr(item)
            if key not in seen:
                seen.add(key)
                merged_list.append(item)
        return merged_list

    if isinstance(base, str) and isinstance(override, str):
        return merge_text(base, override)

    return override if override is not None else base


def merge_platform_payload(base_payload: dict[str, Any], override_payload: dict[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for key in set([*base_payload.keys(), *override_payload.keys()]):
        base_value = base_payload.get(key)
        override_value = override_payload.get(key)

        if key == "tags" and isinstance(base_value, list) and isinstance(override_value, list):
            merged[key] = merge_tags(base_value, override_value)
        elif key in {"description", "text"} and isinstance(base_value, str) and isinstance(override_value, str):
            merged[key] = merge_text(base_value, override_value)
        elif key == "category":
            merged[key] = override_value if override_value not in (None, "") else base_value
        elif key == "privacy_status":
            merged[key] = override_value if override_value not in (None, "") else base_value
        elif key == "media":
            merged[key] = merge_payload_value(base_value, override_value)
        else:
            merged[key] = merge_payload_value(base_value, override_value)

    return merged


class PlatformDataFactory:
    _platform_class_folder: dict[Platforms, type[PlatformData]] = {
        Platforms.YOUTUBE: YoutubeData,
        Platforms.BLUESKY: BlueskyData,
    }

    @classmethod
    def create(cls, platform: Platforms, data: dict[str, Any]) -> PlatformData:
        platform_cls = cls._platform_class_folder.get(platform)
        if platform_cls is None:
            raise ValueError(f"No PlatformData parser found for platform: {platform.value}")
        return platform_cls.from_dict(data)


@dataclass
class PlatformDataCollection:
    youtube: YoutubeData | None = None
    bluesky: BlueskyData | None = None


def merge_platform_data_dicts(global_data: dict[str, Any], local_data: dict[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    global_all = global_data.get("all", {}) if isinstance(global_data.get("all"), dict) else {}
    local_all = local_data.get("all", {}) if isinstance(local_data.get("all"), dict) else {}
    common_data = merge_platform_payload(global_all, local_all)

    for key in set([*global_data.keys(), *local_data.keys()]):
        if key == "all":
            continue

        global_payload = global_data.get(key, {}) if isinstance(global_data.get(key), dict) else {}
        local_payload = local_data.get(key, {}) if isinstance(local_data.get(key), dict) else {}
        merged[key] = merge_platform_payload(merge_platform_payload(global_payload, common_data), local_payload)

    return merged


def parse_platform_data_dict(raw_data: dict[str, Any], defaults: dict[str, Any] | None = None) -> PlatformDataCollection:
    collection = PlatformDataCollection()
    if raw_data is None:
        return collection

    merged_data = merge_platform_data_dicts(defaults or {}, raw_data)

    for platform_key, payload in merged_data.items():
        if platform_key == "all":
            continue

        platform = Platforms(platform_key)
        data = PlatformDataFactory.create(platform, payload)
        if platform == Platforms.YOUTUBE:
            if not isinstance(data, YoutubeData):
                raise TypeError("Expected YoutubeData for youtube platform")
            collection.youtube = data
        elif platform == Platforms.BLUESKY:
            if not isinstance(data, BlueskyData):
                raise TypeError("Expected BlueskyData for bluesky platform")
            collection.bluesky = data
    return collection


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
    def __init__(self, config_file_path: str):
        self.config_file_path: str = config_file_path
    


class FoldersConfig(Config):
    def __init__(self, config_file_path: str, upload_times: list[UploadTime], start_time: datetime.datetime, folders: list[FolderItem]):
        super().__init__(config_file_path) 
        self.upload_times: list[UploadTime] = upload_times
        self.start_time: datetime.datetime = start_time
        self.folders: list[FolderItem] = folders

        

@dataclass
class Config2:
    config_file_path: str
    upload_times: list[UploadTime]
    start_time: datetime.datetime
    folders: list[FolderItem]
    posts: list[PostItem]
    specific_upload_times: list[SpecificUploadTime]
    platform_data: PlatformDataCollection

    def __init__(
        self,
        config_file_path: str,
        upload_times: list[UploadTime],
        start_time: datetime.datetime,
        folders: list[FolderItem] | None = None,
        platform_data: PlatformDataCollection | None = None,
        posts: list[PostItem] | None = None,
        specific_upload_times: list[SpecificUploadTime] | None = None,
    ):
        self.config_file_path = config_file_path
        self.upload_times = upload_times
        self.start_time = start_time
        self.folders = folders or []
        self.posts = posts or []
        self.specific_upload_times = specific_upload_times or []
        self.platform_data = platform_data or PlatformDataCollection()

    @classmethod
    def from_dict(cls, file_path: str, data: dict[str, Any]) -> "Config":
        
        start_date_string = data.get("startDate", data.get("startTime", ""))
        start_time = datetime.datetime.now() if not start_date_string else datetime.datetime.fromisoformat(start_date_string)
        global_platform_data = data.get("globalPlatformData", data.get("platformData", {}))
        
        return cls(
            config_file_path=file_path,
            upload_times=[UploadTime.from_dict(item) for item in data.get("uploadTimes", [])],
            start_time=start_time,
            folders=[FolderItem.from_dict(item, global_platform_data) for item in data.get("folders", [])],
            posts=[PostItem.from_dict(item, global_platform_data) for item in data.get("posts", [])],
            specific_upload_times=[SpecificUploadTime.from_dict(item, global_platform_data) for item in data.get("specificUploadTimes", [])],
            platform_data=parse_platform_data_dict(global_platform_data),
        )
