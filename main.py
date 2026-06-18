import time
from Classes.publisher import *
from Helpers.file_helper import *
from datetime import datetime
from Helpers.config_helper import load_config_list
from Helpers.schedule_helper import constuct_schedule_from_config_list

print("Initializing...")
config_paths = get_files(f"{get_current_directory()}/Config", ["*.schedule.json", ".video.json"])

config_list: list[Config] = load_config_list(config_paths)
schedule = constuct_schedule_from_config_list(config_list)
uploaded_path = f"{get_current_directory()}/uploaded.json"
uploaded = load_json(uploaded_path)

print("Initialization complete.")
print("Publish schedule:")
schedule.print_schedule()

print("Starting publish loop...")
next_publication = schedule.next_publish()
print(f"Next publish: {next_publication.video.name} at {next_publication.upload_time}")

while True:
    now = datetime.now()
    for publication in schedule.publication_list:
        if publication.upload_time and publication.upload_time <= now:
            print(f"Publishing {publication.video.name}...")
            publication.publish_all()
            schedule.publication_list.remove(publication)
            
            uploaded.append(publication.video.video_id)
            save_json(uploaded, uploaded_path)
            
            next_publication = schedule.next_publish()
            print(f"Next publish: {next_publication.video.name} at {next_publication.upload_time}")
    
    # time.sleep(900)  # Check every 15 minutes
    time.sleep(5)  # Check every 5 seconds    
