from datetime import datetime
from Classes.publication import Publication, VideoPublication

class Schedule:
    def __init__(self, publication_list: list[Publication]):
        self.publication_list: list[Publication] = publication_list

    def next_publish(self) -> Publication:
        # Using datetime.max because uploade_time can be None and therefore lambda is refusing it unless I set a fallback. 
        return min(self.publication_list, key=lambda pub: pub.upload_time or datetime.max)
    
    def get_due(self, start_time: datetime) -> list[Publication]:
        due_publications = []
        for publication in self.publication_list:
            if publication.upload_time and publication.upload_time <= start_time:
                due_publications.append(publication)
        return due_publications