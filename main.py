import time
from Classes.upload_times import UploadTimes
from publisher import *
from Helpers.file_helper import *
from datetime import datetime

def print_next_publish(publish_list: list[Publication]):
    scheduled_publications = [publication for publication in publish_list if publication.upload_time is not None]

    if not scheduled_publications:
        return

    # FIX - A smoother version than a method inside a method
    def get_upload_time(publication: Publication) -> datetime:
        if publication.upload_time is None:
            return datetime.max

        return publication.upload_time

    next_publication = min(scheduled_publications, key=get_upload_time)
    print(f"Next publish: {next_publication.video.name} at {next_publication.upload_time}")

print("Initializing...")
publish_list: list[Publication] = []

config: Config = load_config(f"{get_current_directory()}/config.json")
upload_times = UploadTimes(config.uploadTimes, config.startTime)

for map_item in config.maps:
    map_path = map_item.map
    video_paths = get_files(map_path, file_types=[".mp4", ".mov", ".avi", ".mkv"])
    for video_path in video_paths:
        video = Video(video_path)

        if not video.video_id in config.uploaded:
            publication = Publication(video=video, meta_data=map_item.metaData)
            publish_list.append(publication)

publish_list.sort(key=lambda pub: pub.video.creation_time if pub.video else float('inf'))

for publication in publish_list:
    publication.upload_time = upload_times.pop()

print("Initialization complete.")
print("Publish schedule:")
for publication in publish_list:
    print(f"{publication.video.name} at {publication.upload_time}")
print("Starting publish loop...")
print_next_publish(publish_list)

while True:
    now = datetime.now()
    for publication in publish_list:
        if publication.upload_time and publication.upload_time <= now:
            print(f"Publishing {publication.video.name}...")
            publication.publish_all()
            publish_list.remove(publication)
            config.uploaded.append(publication.video.video_id)
            save_json(config, f"{get_current_directory()}/config.json")
            print_next_publish(publish_list)
    
    # time.sleep(900)  # Check every 15 minutes
    time.sleep(5)  # Check every 5 seconds    
