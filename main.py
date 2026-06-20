import threading
import time
from datetime import datetime
from Classes.config import Config
from Classes.publication import VideoPublication
from Classes.publisher_manager import PublisherManager
from Helpers.config_helper import load_config_list
from Helpers.file_helper import get_current_directory, get_files_by_multiple_file_types
from Helpers.schedule_helper import constuct_schedule_from_config_list
from Helpers.upload_state_helper import mark_uploaded


class PublisherApp:
    def __init__(self) -> None:
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._command_listener, daemon=True)
        self.config_list: list[Config] = []
        self.publisher_manager: PublisherManager | None = None
        self.refresh_interval = 60
        """The value is in seconds. This determines how often the app checks for due publications."""

    def setup(self) -> None:
        print("Initializing...")
        config_paths = get_files_by_multiple_file_types(
            f"{get_current_directory()}/Config", ["*.schedule.json", "*.video.json"]
        )

        self.config_list = load_config_list(config_paths)
        schedule = constuct_schedule_from_config_list(self.config_list)
        self.publisher_manager = PublisherManager(schedule)
        self._wire_events()

        print("Initialization complete.")
        

    def _wire_events(self) -> None:
        if self.publisher_manager is None:
            return
        self.publisher_manager.on_published += self.on_publication_published

    def _print_schedule(self) -> None:
        if self.publisher_manager is None:
            return
        print("Publish schedule:")
        for publication in self.publisher_manager.schedule.publication_list:
            print(f"- {publication.get_name()} at {publication.upload_time}")

    def _print_next_publish(self) -> None:
        if self.publisher_manager is None:
            return
        if not self.publisher_manager.schedule.publication_list:
            return

        next_publication = self.publisher_manager.schedule.next_publish()
        print(f"Next publish: {next_publication.get_name()} at {next_publication.upload_time}")

    def on_publication_published(self, publication) -> None:
        print(f"Published: {publication.get_name()}")

        if isinstance(publication, VideoPublication):
            mark_uploaded(
                config_file_path=publication.config_file_path,
                folder_path=publication.source_folder,
                video_id=publication.video.video_id,
            )

        self._print_next_publish()

    def _command_listener(self) -> None:
        while not self.stop_event.is_set():
            cmd = input().strip().lower()
            if cmd in ("q", "quit", "exit", "stop"):
                print("Stopping...")
                self.stop_event.set()

    def run(self) -> None:
        self.setup()
        self.thread.start()
        self._print_schedule()
        self._print_next_publish()
        print("Starting publish loop...")

        while not self.stop_event.is_set():
            if self.publisher_manager is None:
                break

            now = datetime.now()
            due = self.publisher_manager.schedule.get_due(now)

            if due:
                self.publisher_manager.publish_multiple(due)

            if self.stop_event.wait(self.refresh_interval):
                break
        
        self.thread.join()
        print("Program ended.")


if __name__ == "__main__":
    app = PublisherApp()
    app.run()
