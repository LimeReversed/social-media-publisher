from Classes.upload_times import UploadTimes
from Classes.config import Config
from Helpers.file_helper import *
from Classes.publication import Publication, VideoPublication
from Classes.video import Video
from Classes.schedule import Schedule

#FIX I'm not actually using the global meta data here. 
def constuct_schedule_from_config_list(config_list: list[Config]) -> Schedule:
        publish_list: list[Publication] = []
        
        for config in config_list:
            upload_times = UploadTimes(config.upload_times, config.start_time)

            for map_item in config.maps:
                map_path = map_item.map
                video_paths = get_files(map_path, file_types=[".mp4", ".mov", ".avi", ".mkv"])
                
                # Initialze Video
                for video_path in video_paths:
                    video = Video(video_path)

                    # Initialize Publication with video and add to publish_list
                    if not video.video_id in config.uploaded:
                        publication = VideoPublication(video=video, platform_data=map_item.meta_data)
                        publish_list.append(publication)

            populated_publish_list = populate_upload_times(publish_list, upload_times)
            publish_list += populated_publish_list

        return Schedule(publish_list)

def populate_upload_times(publication_list: list[Publication] , upload_times: UploadTimes) -> list[Publication]:
    result = publication_list.copy()

    for publication in result:
        publication.upload_time = upload_times.pop()
    
    return result