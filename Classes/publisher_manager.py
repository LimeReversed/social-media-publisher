from Classes.config import Config, YoutubeData, BlueskyData
from Classes.publication import Publication, VideoPublication
from Classes.publisher import YoutubePublisher, BlueskyPublisher, BlueskyWithVideoPublisher
from Classes.schedule import Schedule
from Classes.Event import Event

class PublisherManager:
    """PublisherManager is responsible for managing the publishers and orchestrating the publication process based on the schedule."""
    def __init__(self, schedule: Schedule):
        self.schedule = schedule
        self.on_published = Event()

    def publish(self, publication: Publication):
        if publication.platform_data.youtube is not None and isinstance(publication, VideoPublication):
            youtube_data = publication.platform_data.youtube
            youtube_publisher = YoutubePublisher(youtube_data.description, publication.video.name, publication.video.path, str(youtube_data.category), ",".join(youtube_data.tags))
            youtube_publisher.publish()
        if publication.platform_data.bluesky is not None:
            bluesky_data = publication.platform_data.bluesky
            bluesky_publisher = BlueskyPublisher(bluesky_data.text)
            bluesky_publisher.publish()
        
        self.schedule.publication_list.remove(publication)
        self.on_published.trigger(publication)

    def publish_multiple(self, publications: list[Publication]):
        for publication in publications:
            self.publish(publication)