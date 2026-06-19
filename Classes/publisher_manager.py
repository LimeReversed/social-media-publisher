from Classes.config import Config, Platforms
from Classes.publication import Publication
from Classes.publisher import Publisher
from Classes.schedule import Schedule
from Classes.Event import Event

class PublisherManager:
    """PublisherManager is responsible for managing the publishers and orchestrating the publication process based on the schedule."""
    def __init__(self, schedule: Schedule):
        # Hmm jag vet inte vilka argumment som Publisher ska ta förrän jag har en publication. Så kan jag initiera här?
        # Ska klasserna kanske inte ha parametrar, utan de gå in i metoderna?
        self.publishers: dict[Platforms, Publisher] = {}
        self.schedule = schedule
        self.on_published = Event()

    def publish(self, publication: Publication):
        for platform, data in publication.platform_data.items():
            ## Hade kunnat köra self.publishers[platform].publish(publication, data) om jag hade initierat publishers.
            if platform == Platforms.YOUTUBE:
                self.publish_to_youtube(publication, data)
            elif platform == Platforms.BLUESKY:
                self.publish_to_bluesky(publication, data)
        
        self.schedule.publication_list.remove(publication)
        self.on_published.trigger(publication)

    def publish_multiple(self, publications: list[Publication]):
        for publication in publications:
            self.publish(publication)