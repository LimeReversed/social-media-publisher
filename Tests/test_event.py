from unittest import TestCase

from Classes.Event import Event


class EventTests(TestCase):
    def test_trigger_calls_registered_listener_with_payload(self):
        event = Event()
        calls = []

        def listener(payload):
            calls.append(payload)

        event += listener
        event.trigger({"ok": True})

        self.assertEqual([{"ok": True}], calls)

    def test_removed_listener_is_not_called(self):
        event = Event()
        calls = []

        def listener(payload):
            calls.append(payload)

        event += listener
        event -= listener
        event.trigger("data")

        self.assertEqual([], calls)
