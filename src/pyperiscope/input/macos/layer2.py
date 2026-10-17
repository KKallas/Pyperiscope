"""macOS input, layer 2: mouse."""
import time

import Quartz as Q

from .layer1 import WINDOW_THAT_CAN_HANDLE, WINDOW_UNDER_POINTER
from .layer1 import QuartzInput as Base

BUTTONS = {
    "left": (Q.kCGEventLeftMouseDown, Q.kCGEventLeftMouseUp, Q.kCGEventLeftMouseDragged, Q.kCGMouseButtonLeft),
    "right": (Q.kCGEventRightMouseDown, Q.kCGEventRightMouseUp, Q.kCGEventRightMouseDragged, Q.kCGMouseButtonRight),
    "middle": (Q.kCGEventOtherMouseDown, Q.kCGEventOtherMouseUp, Q.kCGEventOtherMouseDragged, Q.kCGMouseButtonCenter),
}
STEP_DELAY = 0.012


class QuartzInput(Base):
    def _mouse(self, kind, x, y, button, pid, wid, clicks=1):
        event = Q.CGEventCreateMouseEvent(self.source, kind, (x, y), button)
        Q.CGEventSetIntegerValueField(event, Q.kCGMouseEventClickState, clicks)
        if wid:
            Q.CGEventSetIntegerValueField(event, WINDOW_UNDER_POINTER, wid)
            Q.CGEventSetIntegerValueField(event, WINDOW_THAT_CAN_HANDLE, wid)
        self.post(event, pid)
        time.sleep(STEP_DELAY)

    def move(self, x, y):
        pid, wid = self.route(x, y)
        with self.user_paused():
            self._mouse(Q.kCGEventMouseMoved, x, y, Q.kCGMouseButtonLeft, pid, wid)

    def click(self, x, y, button="left", count=1):
        down, up, _, btn = BUTTONS[button]
        pid, wid = self.route(x, y)
        with self.user_paused():
            self._mouse(Q.kCGEventMouseMoved, x, y, btn, pid, wid)
            for n in range(1, count + 1):
                self._mouse(down, x, y, btn, pid, wid, n)
                self._mouse(up, x, y, btn, pid, wid, n)

    def drag(self, x0, y0, x1, y1, button="left", steps=20):
        down, up, dragged, btn = BUTTONS[button]
        pid, wid = self.route(x0, y0)
        with self.user_paused():
            self._mouse(Q.kCGEventMouseMoved, x0, y0, btn, pid, wid)
            self._mouse(down, x0, y0, btn, pid, wid)
            for i in range(1, steps + 1):
                x, y = x0 + (x1 - x0) * i / steps, y0 + (y1 - y0) * i / steps
                self._mouse(dragged, x, y, btn, pid, wid)
            self._mouse(up, x1, y1, btn, pid, wid)

    def scroll(self, x, y, dx=0, dy=0):
        """dy > 0 scrolls content down (wheel towards you), in lines."""
        pid, wid = self.route(x, y)
        with self.user_paused():
            self._mouse(Q.kCGEventMouseMoved, x, y, Q.kCGMouseButtonLeft, pid, wid)
            event = Q.CGEventCreateScrollWheelEvent(self.source, Q.kCGScrollEventUnitLine, 2, -int(dy), -int(dx))
            Q.CGEventSetLocation(event, (x, y))
            self.post(event, pid)
