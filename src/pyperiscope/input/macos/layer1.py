"""macOS input, layer 1: where events go.

isolated: CGEventPostToPid delivers the event to one process. The window
number under the point is stamped into the event so the app routes it to the
right window. The system cursor never moves and the user's keyboard state is
not mixed in (private event source), so a person can keep working.

shared: CGEventPost at the HID level, like real hardware. Before acting we
wait until the user's mouse has been still briefly, and the cursor is
returned to where it was afterwards.

Every event carries TAG in its user-data field so the kill switch can tell
our keystrokes from the person's.
"""
import os
import time
from contextlib import contextmanager

import Quartz as Q

from ...errors import PermissionMissing
from ..base import InputBackend
from .apps import open_app, running_app  # noqa: F401  (re-exported)

TAG = 0x50455249  # "PERI"
WINDOW_UNDER_POINTER = 91         # kCGMouseEventWindowUnderMousePointer
WINDOW_THAT_CAN_HANDLE = 92       # ...ThatCanHandleThisEvent
USER_IDLE_SECONDS = 0.3


def window_at(x, y, skip_pids=(), only_pid=None):
    """(pid, window number) of the front-most on-screen window containing x, y."""
    options = Q.kCGWindowListOptionOnScreenOnly | Q.kCGWindowListExcludeDesktopElements
    for info in Q.CGWindowListCopyWindowInfo(options, Q.kCGNullWindowID) or []:
        pid = info["kCGWindowOwnerPID"]
        if pid in skip_pids or (only_pid and pid != only_pid) or info.get("kCGWindowAlpha", 1) == 0:
            continue
        b = info["kCGWindowBounds"]
        if b["X"] <= x < b["X"] + b["Width"] and b["Y"] <= y < b["Y"] + b["Height"]:
            return pid, info["kCGWindowNumber"]
    return (only_pid, 0) if only_pid else (None, 0)


class QuartzInput(InputBackend):
    def __init__(self, mode="isolated", app=None, skip_pids=(), stop=None):
        if not Q.CGPreflightPostEventAccess():
            Q.CGRequestPostEventAccess()
            raise PermissionMissing("Accessibility permission is needed to send input; "
                                    "grant it to your terminal/editor and restart it (pyperiscope doctor)")
        self.mode, self.app, self.stop = mode, app, stop
        self.skip_pids = {os.getpid(), *[p for p in skip_pids if p]}
        self.source = Q.CGEventSourceCreate(Q.kCGEventSourceStatePrivate)
        self.pid = None
        if app:
            found = running_app(app)
            if not found:
                raise RuntimeError(f"app {app!r} is not running; start it first (Session.open_app)")
            self.pid = found.processIdentifier()
        self.last_pid = self.pid  # keyboard goes to the app we last clicked

    def route(self, x, y):
        """Pick the process + window for a pointer event at x, y."""
        pid, wid = window_at(x, y, self.skip_pids, self.pid)
        self.last_pid = pid or self.last_pid
        return self.last_pid, wid

    def post(self, event, pid=None):
        Q.CGEventSetIntegerValueField(event, Q.kCGEventSourceUserData, TAG)
        if self.mode == "shared":
            Q.CGEventPost(Q.kCGHIDEventTap, event)
            return
        pid = pid or self.last_pid
        if not pid:
            raise RuntimeError("isolated input has no target app yet: click something first or set app=")
        Q.CGEventPostToPid(pid, event)

    @contextmanager
    def user_paused(self):
        """shared mode: wait for the user's mouse to rest, act, put the cursor back."""
        if self.mode != "shared":
            yield
            return
        hid = Q.kCGEventSourceStateHIDSystemState
        while Q.CGEventSourceSecondsSinceLastEventType(hid, Q.kCGAnyInputEventType) < USER_IDLE_SECONDS:
            if self.stop and self.stop.wait(0.05):
                break
        home = Q.CGEventGetLocation(Q.CGEventCreate(None))
        try:
            yield
        finally:
            time.sleep(0.02)
            Q.CGWarpMouseCursorPosition(home)
            Q.CGAssociateMouseAndMouseCursorPosition(True)
