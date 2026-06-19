from Classes.upload_times import UploadTimes
from Classes.config import Config, PlatformDataCollection
from Helpers.file_helper import *
from Helpers.upload_state_helper import get_uploaded_ids, is_folder_completed, load_upload_state
from Classes.publication import Publication, VideoPublication
from Classes.video import Video
from Classes.schedule import Schedule

def merge_platform_data(
    global_data: PlatformDataCollection,
    local_data: PlatformDataCollection,
) -> PlatformDataCollection:
    if global_data.youtube and local_data.youtube:
        youtube = global_data.youtube.merge(local_data.youtube)
    else:
        youtube = local_data.youtube or global_data.youtube

    if global_data.bluesky and local_data.bluesky:
        bluesky = global_data.bluesky.merge(local_data.bluesky)
    else:
        bluesky = local_data.bluesky or global_data.bluesky

    return PlatformDataCollection(youtube=youtube, bluesky=bluesky)

def sort_by_creation_time(publication_list: list[Publication]) -> None:
        publication_list.sort(key=lambda pub: pub.video.creation_time if isinstance(pub, VideoPublication) and pub.video else float('inf'))

def constuct_schedule_from_config_list(config_list: list[Config]) -> Schedule:
        publish_list: list[Publication] = []
        
        for config in config_list:
            upload_state = load_upload_state(config.config_file_path)
            upload_times = UploadTimes(config.upload_times, config.start_time)

            for folder_item in config.folders:
                folder_path = folder_item.folder
                if is_folder_completed(upload_state, folder_path):
                    continue

                uploaded_ids = get_uploaded_ids(upload_state, folder_path)
                video_paths = get_files(folder_path, file_types=[".mp4", ".mov", ".avi", ".mkv"])
                
                # Initialze Video
                for video_path in video_paths:
                    video = Video(video_path)
                    merged_platform_data = merge_platform_data(config.platform_data, folder_item.platform_data)

                    # Initialize Publication with video and add to publish_list
                    if video.video_id not in uploaded_ids:
                        publication = VideoPublication(
                            video=video,
                            platform_data=merged_platform_data,
                            config_file_path=config.config_file_path,
                            source_folder=folder_path,
                        )
                        publish_list.append(publication)

            sort_by_creation_time(publish_list)
            populated_publish_list = populate_upload_times(publish_list, upload_times)
            publish_list = populated_publish_list

        return Schedule(publish_list)

def populate_upload_times(publication_list: list[Publication] , upload_times: UploadTimes) -> list[Publication]:
    result = publication_list.copy()

    for publication in result:
        publication.upload_time = upload_times.pop()
    
    return result