from Helpers.file_helper import UploadTime
from unittest import TestCase
from Helpers.datetime_helper import next_upload_datetime
import datetime

class TimeTests(TestCase):

    def test_next_upload_datetime_should_return_correct_dates(self):
        now = datetime.datetime(2026, 6, 6, 10, 0)  # Saturday
        upload_time = UploadTime(day=0, hour=11, minute=0)  # Monday at 11:00
        expected = datetime.datetime(2026, 6, 8, 11, 0)  # Next Monday
        result = next_upload_datetime(upload_time, now)
        self.assertEqual(expected, result)