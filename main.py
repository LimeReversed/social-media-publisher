import time
from Classes.upload_times import UploadTimes
from publisher import *
from Helpers.file_helper import *
from datetime import datetime

print("Initializing...")
config: Config = load_config(f"{get_current_directory()}/config.json")
publications = Publications.constuct_from_config(config)

print("Initialization complete.")
print("Publish schedule:")
publications.print_schedule()
print("Starting publish loop...")
publications.print_next_publish()

while True:
    now = datetime.now()
    for publication in publications.publication_list:
        if publication.upload_time and publication.upload_time <= now:
            print(f"Publishing {publication.video.name}...")
            publication.publish_all()
            publications.publication_list.remove(publication)
            config.uploaded.append(publication.video.video_id)
            save_json(config, f"{get_current_directory()}/config.json")
            publications.print_next_publish()
    
    # time.sleep(900)  # Check every 15 minutes
    time.sleep(5)  # Check every 5 seconds    
