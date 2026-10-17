"""Hold Esc for N seconds (default 3) to stop the automation.

Polls the physical keyboard state (HID level) so it sees the person's Esc no
matter which app is in front, and never sees the Esc keys a workflow sends
in isolated mode. A workflow's own Esc taps in shared mode are too short to
trigger it. Needs the Input Monitoring permission; without it macOS reports
every key as up, so we refuse to start rather than run without brakes.
"""
import _thread
import sys
import threading
import time

from ..errors import PermissionMissing

ESC_KEYCODE = 53
POLL_SECONDS = 0.05


def esc_is_down():
    import Quartz as Q
    return bool(Q.CGEventSourceKeyState(Q.kCGEventSourceStateHIDSystemState, ESC_KEYCODE))


def check_permission(request=True):
    if sys.platform != "darwin":
        raise NotImplementedError("kill switch is macOS-only for now")
    import Quartz as Q
    if Q.CGPreflightListenEventAccess():
        return
    if request:
        Q.CGRequestListenEventAccess()
    raise PermissionMissing("Input Monitoring permission is needed for the Esc kill switch; "
                            "grant it to your terminal/editor and restart it (pyperiscope doctor)")


class KillSwitch:
    def __init__(self, hold=3.0, stop=None, on_progress=None, key_down=esc_is_down):
        self.hold = hold
        self.stop = stop or threading.Event()   # set when the user stops us
        self.on_progress = on_progress          # called with seconds held (0 = released)
        self.key_down = key_down
        self._closed = threading.Event()
        self._thread = None

    def start(self, check=True):
        if check:
            check_permission()
        self._thread = threading.Thread(target=self._watch, name="pyperiscope-killswitch", daemon=True)
        self._thread.start()
        return self

    def _watch(self):
        since, shown = None, 0
        while not self._closed.wait(POLL_SECONDS):
            if not self.key_down():
                if shown and self.on_progress:
                    self.on_progress(0)
                since, shown = None, 0
                continue
            since = since or time.monotonic()
            held = time.monotonic() - since
            if self.on_progress and int(held * 4) != shown:   # update ~4x per second
                shown = int(held * 4)
                self.on_progress(held)
            if held >= self.hold:
                self.trigger()
                return

    def trigger(self):
        """Stop now: flag it for the session and interrupt whatever the main
        thread is doing (a sleep, a long find, user code)."""
        if self.stop.is_set():
            return
        self.stop.set()
        _thread.interrupt_main()

    def close(self):
        self._closed.set()
