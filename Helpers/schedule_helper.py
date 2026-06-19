from Classes.upload_times import UploadTimes
from Classes.config import Config, PlatformData, Platforms
from Helpers.file_helper import *
from Helpers.upload_state_helper import get_uploaded_ids, is_folder_completed, load_upload_state
from Classes.publication import Publication, VideoPublication
from Classes.video import Video
from Classes.schedule import Schedule

def merge_platform_data(
    global_platform_data: dict[Platforms, PlatformData],
    map_platform_data: dict[Platforms, PlatformData],
) -> dict[Platforms, PlatformData]:
    merged: dict[Platforms, PlatformData] = {}
    platforms = set(global_platform_data.keys()) | set(map_platform_data.keys())

    for platform in platforms:
        global_data = global_platform_data.get(platform)
        local_data = map_platform_data.get(platform)

        if global_data and local_data:
            merged[platform] = global_data.merge(local_data)
        elif local_data:
            merged[platform] = local_data
        elif global_data:
            merged[platform] = global_data

    return merged


def constuct_schedule_from_config_list(config_list: list[Config]) -> Schedule:
        publish_list: list[Publication] = []
        
        for config in config_list:
            upload_state = load_upload_state(config.config_file_path)
            upload_times = UploadTimes(config.upload_times, config.start_time)

            for map_item in config.folders:
                map_path = map_item.map
                if is_folder_completed(upload_state, map_path):
                    continue

                uploaded_ids = get_uploaded_ids(upload_state, map_path)
                video_paths = get_files(map_path, file_types=[".mp4", ".mov", ".avi", ".mkv"])
                
                # Initialze Video
                for video_path in video_paths:
                    video = Video(video_path)
                    merged_platform_data = merge_platform_data(config.platform_data, map_item.platform_data)

                    # Initialize Publication with video and add to publish_list
                    if video.video_id not in uploaded_ids:
                        publication = VideoPublication(
                            video=video,
                            platform_data=merged_platform_data,
                            config_file_path=config.config_file_path,
                            source_folder=map_path,
                        )
                        publish_list.append(publication)

            populated_publish_list = populate_upload_times(publish_list, upload_times)
            publish_list += populated_publish_list

        return Schedule(publish_list)

def populate_upload_times(publication_list: list[Publication] , upload_times: UploadTimes) -> list[Publication]:
    result = publication_list.copy()

    for publication in result:
        publication.upload_time = upload_times.pop()
    
    return result