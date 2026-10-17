"""The input backend contract. One backend per OS; all coordinates are global
screen points (not pixels). Modes:

  isolated  events go straight to the target app's process; the user's real
            cursor and keyboard are untouched, so both can work at once
  shared    events go through the system like a real mouse; the cursor is
            put back afterwards, and actions wait while the user is moving it
  dry       nothing is sent; actions are only recorded (tests, rehearsals)
"""


class InputBackend:
    mode = "base"

    def move(self, x, y):
        raise NotImplementedError

    def click(self, x, y, button="left", count=1):
        raise NotImplementedError

    def drag(self, x0, y0, x1, y1, button="left"):
        raise NotImplementedError

    def scroll(self, x, y, dx=0, dy=0):
        raise NotImplementedError

    def type_text(self, text):
        raise NotImplementedError

    def key(self, combo):
        raise NotImplementedError

    def close(self):
        pass


class RecordingInput(InputBackend):
    """Backend for `input: "dry"` and tests: remembers every call."""
    mode = "dry"

    def __init__(self, *args, **kwargs):
        self.calls = []

    def _record(self, name, *args, **kwargs):
        self.calls.append((name, args, kwargs))

    def move(self, x, y):
        self._record("move", x, y)

    def click(self, x, y, button="left", count=1):
        self._record("click", x, y, button=button, count=count)

    def drag(self, x0, y0, x1, y1, button="left"):
        self._record("drag", x0, y0, x1, y1, button=button)

    def scroll(self, x, y, dx=0, dy=0):
        self._record("scroll", x, y, dx=dx, dy=dy)

    def type_text(self, text):
        self._record("type", text)

    def key(self, combo):
        self._record("key", combo)
