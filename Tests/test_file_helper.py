from Helpers.file_helper import *
from unittest import TestCase

class TestFileHelper(TestCase):
    def test_get_files__returns_config_files(self):
        # Setup
        test_dir = "Tests/Mocks"
        expected_files = [os.path.abspath("Tests/Mocks/config_mock_1.schedule.json")]
        
        # Exercise
        result = get_files_by_multiple_file_types(test_dir, ["*.schedule.json", "*.video.json"])
        
        # Verify
        self.assertEqual(result, expected_files, f"Expected {expected_files}, but got {result}")

    def test_get_files__returns_video_files(self):
        # Setup
        test_dir = "Tests/TestVideos"
        expected_files = [
            os.path.abspath("Tests/TestVideos/test_video_1.mp4"),
            os.path.abspath("Tests/TestVideos/test_video_2.mp4"),
        ]
        
        # Exercise
        result = get_files_by_multiple_file_types(test_dir, ["*.mp4", "*.mov", "*.avi", "*.mkv"])
        
        # Verify
        self.assertEqual(result, expected_files, f"Expected {expected_files}, but got {result}")