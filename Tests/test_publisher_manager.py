import tempfile
import types
import sys
import os
import importlib
from unittest import TestCase
from unittest.mock import patch

from Classes.config import BlueskyData, PlatformDataCollection, YoutubeData
from Classes.publication import TextPublication, VideoPublication
from Classes.schedule import Schedule
from Classes.video import Video


class PublisherManagerTests(TestCase):
    ...
