import datetime
from unittest import TestCase

from Classes.config import PlatformDataCollection
from Classes.publication import TextPublication
from Classes.schedule import Schedule


class ScheduleTests(TestCase):
    def test_next_publish_returns_earliest_upload_time(self):
        a = TextPublication("a", PlatformDataCollection(), upload_time=datetime.datetime(2026, 6, 20, 10, 0))
        b = TextPublication("b", PlatformDataCollection(), upload_time=datetime.datetime(2026, 6, 19, 10, 0))
        c = TextPublication("c", PlatformDataCollection(), upload_time=None)
        schedule = Schedule([a, b, c])

        result = schedule.next_publish()

        self.assertIs(b, result)

    def test_get_due_returns_only_items_due_at_or_before_start(self):
        start = datetime.datetime(2026, 6, 19, 12, 0)
        due = TextPublication("due", PlatformDataCollection(), upload_time=datetime.datetime(2026, 6, 19, 12, 0))
        future = TextPublication("future", PlatformDataCollection(), upload_time=datetime.datetime(2026, 6, 19, 13, 0))
        no_time = TextPublication("none", PlatformDataCollection(), upload_time=None)
        schedule = Schedule([due, future, no_time])

        result = schedule.get_due(start)

        self.assertEqual([due], result)
