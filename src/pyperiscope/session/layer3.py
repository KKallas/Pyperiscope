"""Session, layer 3: acting. The verbs mirror Claude's computer-use actions
(left_click, double_click, type, key "ctrl+s", scroll, mouse_move,
left_click_drag) so models write workflows fluently.

`where` is a target name (found strictly: exactly one match), a Match, or an
(x, y) tuple in screen points. `offset` shifts the click in points.
"""
from ..input import open_app as _open_app
from ..target import Match
from .layer2 import Session as Base

SCROLL = {"down": (0, 1), "up": (0, -1), "right": (1, 0), "left": (-1, 0)}


class Session(Base):
    def point(self, where, offset=(0, 0), timeout=None):
        if isinstance(where, str):
            where = self.find(where, timeout)
        if isinstance(where, Match):
            where = where.point
        return (where[0] + offset[0], where[1] + offset[1])

    def _act(self, action, where, **data):
        self.guard()
        self.log(action, where=where if isinstance(where, (str, type(None))) else str(where), **data)

    def _settle(self):
        self.wait(self.cfg["action_delay"])

    def left_click(self, where, offset=(0, 0), timeout=None, count=1, button="left"):
        x, y = self.point(where, offset, timeout)
        self._act(f"{button}_click", where, at=[round(x, 1), round(y, 1)], count=count)
        self.input.click(x, y, button, count)
        self._settle()
        return (x, y)

    click = left_click

    def double_click(self, where, offset=(0, 0), timeout=None):
        return self.left_click(where, offset, timeout, count=2)

    def triple_click(self, where, offset=(0, 0), timeout=None):
        return self.left_click(where, offset, timeout, count=3)

    def right_click(self, where, offset=(0, 0), timeout=None):
        return self.left_click(where, offset, timeout, button="right")

    def middle_click(self, where, offset=(0, 0), timeout=None):
        return self.left_click(where, offset, timeout, button="middle")

    def mouse_move(self, where, offset=(0, 0), timeout=None):
        x, y = self.point(where, offset, timeout)
        self._act("mouse_move", where, at=[round(x, 1), round(y, 1)])
        self.input.move(x, y)
        self._settle()

    def left_click_drag(self, start, end, timeout=None):
        x0, y0 = self.point(start, timeout=timeout)
        x1, y1 = self.point(end, timeout=timeout)
        self._act("left_click_drag", start, to=[round(x1, 1), round(y1, 1)])
        self.input.drag(x0, y0, x1, y1)
        self._settle()

    def scroll(self, where, direction="down", amount=3, timeout=None):
        x, y = self.point(where, timeout=timeout)
        dx, dy = SCROLL[direction]
        self._act("scroll", where, direction=direction, amount=amount)
        self.input.scroll(x, y, dx * amount, dy * amount)
        self._settle()

    def type(self, text):
        self._act("type", None, chars=len(text))   # text itself is not logged
        self.input.type_text(text)
        self._settle()

    def key(self, combo, repeat=1):
        """xdotool-style combo: "Return", "Tab", "ctrl+a", "cmd+shift+s"."""
        for _ in range(repeat):
            self._act("key", None, combo=combo)
            self.input.key(combo)
            self._settle()

    def open_app(self, name, wait=1.0):
        """Launch or bring forward an app; it becomes the keyboard target."""
        self._act("open_app", None, app=name)
        _open_app(name)
        self.wait(wait)
