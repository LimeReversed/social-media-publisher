from time import time

from Classes.config import Config, YoutubeData, BlueskyData
from Classes.publication import Publication, TextPublication, VideoPublication
from Classes.publisher import YoutubePublisher, BlueskyPublisher, BlueskyWithVideoPublisher
from Classes.schedule import Schedule
from Classes.Event import Event

class PublisherManager:
    """PublisherManager is responsible for managing the publishers and orchestrating the publication process based on the schedule."""
    def __init__(self, schedule: Schedule):
        self.schedule = schedule
        self.on_published = Event()

    def publish(self, publication: Publication):
        youtube_publisher = None
        if publication.platform_data.youtube is not None and isinstance(publication, VideoPublication):
            youtube_publisher = YoutubePublisher(publication)
            youtube_publisher.publish()

        if publication.platform_data.bluesky is not None and isinstance(publication, VideoPublication):
            time.sleep(300)  # Wait for YouTube video to be processed before posting on Bluesky
            video_id = youtube_publisher.video_id if youtube_publisher else ""

            bluesky_publisher = BlueskyWithVideoPublisher(publication, video_id)
            bluesky_publisher.publish()
        
        self.schedule.publication_list.remove(publication)
        self.on_published.trigger(publication)

    def publish_multiple(self, publications: list[Publication]):
        for publication in publications:
            self.publish(publication)