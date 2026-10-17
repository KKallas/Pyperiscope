"""Session, layer 1: setup and safety.

A Session owns the input backend, the Esc kill switch and the "running"
overlay. Every later layer calls guard()/wait(), so holding Esc stops the
run at the next action or mid-wait.
"""
import threading
from pathlib import Path

from ..errors import StoppedByUser
from ..input import make_input
from ..safety import Indicator, KillSwitch
from ..screen import capture


class Session:
    def __init__(self, project, run_dir=None, input=None, app=None, safety=True,
                 input_backend=None, capture_fn=None, name="session"):
        self.project, self.cfg, self.name = project, project.config, name
        self.run_dir = Path(run_dir) if run_dir else None
        self.step, self.last_shot, self._targets = None, None, {}
        self.stop = threading.Event()
        self.capture_fn = capture_fn or (lambda: capture(self.cfg["monitor"]))
        mode = input or self.cfg["input"]
        safety = safety and mode != "dry" and input_backend is None   # dry runs send nothing
        self.indicator = Indicator(enabled=safety and self.cfg["overlay"])
        self.killswitch = None
        try:
            if safety:
                self.killswitch = KillSwitch(self.cfg["kill_hold_seconds"], self.stop, self._on_hold).start()
            self.input = input_backend or make_input(mode, app or self.cfg["app"], [self.indicator.pid], self.stop)
        except BaseException:
            self.close()
            raise
        self.status("running")

    def log(self, event, **data):
        """Replaced in layer 4 by the events.jsonl writer."""

    # -- safety ---------------------------------------------------------
    def status(self, text, level="run"):
        hold = self.cfg["kill_hold_seconds"]
        where = f"{self.name} › {self.step}" if self.step else self.name
        self._status = f"● {where} — {text}  ·  hold Esc {hold:g}s to stop"
        self.indicator.show(self._status, level)

    def _on_hold(self, held):
        if self.stop.is_set():
            self.indicator.show("■ Stopped by Esc", "stop")
        elif held <= 0:
            self.indicator.show(self._status, "run")
        else:
            left = max(0.0, self.cfg["kill_hold_seconds"] - held)
            self.indicator.show(f"Stopping in {left:.1f}s — keep holding Esc", "warn")

    def guard(self):
        if self.stop.is_set():
            raise StoppedByUser("stopped: Esc was held")

    def wait(self, seconds):
        """Sleep that ends early (with StoppedByUser) when the user stops us."""
        self.guard()
        if self.stop.wait(seconds):
            self.guard()
