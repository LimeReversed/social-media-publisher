from datetime import datetime
from Classes.publication import Publication


class Schedule:
    def __init__(self, publication_list: list[Publication]):
        # Merge all publication data into one list. Remove upload_times as a member of the class since it's only to initialize publication data, which contains the upload time. 
        # So I just need construct_from_config to take a list of Config.
        # Just keep in mind that it will take a batch of publications at a time and only that should be paired with the upload times.
        # The next list[Publication] will have another set of Upload times. THen we can merge the result into publication_list. 

        self.publication_list: list[Publication] = publication_list
        self._sort_by_creation_time()

    def _sort_by_creation_time(self) -> None:
        # Is this needed? Yes Because it decides which one gets the first thursday. 
        # Populate with upload date first?
        # Get video list and sort?
        self.publication_list.sort(key=lambda pub: pub.video.creation_time if pub.video else float('inf'))

    def next_publish(self) -> Publication:
        # Using datetime.max because uploade_time can be None and therefore lambda is refusing it unless I set a fallback. 
        return min(self.publication_list, key=lambda pub: pub.upload_time or datetime.max)

    def get_video_schedule(self):
        # They do assume videos don't they... should I lean into that or Not. 
        # Maybe a funtion that calls title of post if video doesn't exist. 
        # Have VideoPublication that inherits from Publication. 
        video_schedule = []

        for publication in self.publication_list:
            video_schedule += f"{publication.video.name} at {publication.upload_time}"

        return video_schedule