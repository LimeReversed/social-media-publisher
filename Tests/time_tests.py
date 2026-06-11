from unittest import TestCase
import datetime

from Classes.config import UploadTime
from Classes.upload_times import next_upload_datetime


class TimeTests(TestCase):

    def test_next_upload_datetime_should_return_correct_dates(self):
        now = datetime.datetime(2026, 6, 6, 10, 0)  # Saturday
        upload_time = UploadTime(day=0, hour=11, minute=0)  # Monday at 11:00
        expected = datetime.datetime(2026, 6, 8, 11, 0)  # Next Monday

        result = next_upload_datetime(upload_time, now)

        self.assertEqual(expected, result)

    def test_next_upload_datetime_should_keep_today_when_release_is_still_ahead(self):
        now = datetime.datetime(2026, 6, 8, 10, 0)  # Monday before release
        upload_time = UploadTime(day=0, hour=11, minute=0)  # Monday at 11:00
        expected = datetime.datetime(2026, 6, 8, 11, 0)

        result = next_upload_datetime(upload_time, now)

        self.assertEqual(expected, result)