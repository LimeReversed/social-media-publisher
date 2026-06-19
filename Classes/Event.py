class Event:
    def __init__(self):
        self._listeners = []

    def __iadd__(self, listener) -> 'Event':
        """Register a new listener."""
        self._listeners.append(listener)
        return self

    def __isub__(self, listener) -> 'Event':
        """Unregister an existing listener."""
        if listener in self._listeners:
            self._listeners.remove(listener)
        return self

    def trigger(self, event_data=None):
        """Fire the event, passing event_data to every listener."""
        for listener in self._listeners:
            listener(event_data)