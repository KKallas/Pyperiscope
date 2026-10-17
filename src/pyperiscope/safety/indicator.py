"""Tell the person at the machine that automation is running.

Indicator drives the overlay process; notify() posts a macOS notification
(used when a run finishes, stops, or needs a human).
"""
import json
import subprocess
import sys


class Indicator:
    def __init__(self, enabled=True):
        self.proc = None
        if enabled and sys.platform == "darwin":
            self.proc = subprocess.Popen([sys.executable, "-m", "pyperiscope.safety.overlay"],
                                         stdin=subprocess.PIPE, text=True,
                                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    @property
    def pid(self):
        return self.proc.pid if self.proc else None

    def show(self, text, level="run"):
        if not self.proc or self.proc.poll() is not None:
            return
        try:
            self.proc.stdin.write(json.dumps({"text": text, "level": level}) + "\n")
            self.proc.stdin.flush()
        except (BrokenPipeError, OSError):
            self.proc = None

    def close(self):
        if not self.proc:
            return
        try:
            self.proc.stdin.close()
            self.proc.wait(timeout=2)
        except (OSError, subprocess.TimeoutExpired):
            self.proc.kill()
        self.proc = None


def notify(title, text):
    """Best-effort desktop notification; never raises."""
    if sys.platform != "darwin":
        return
    script = f"display notification {json.dumps(text, ensure_ascii=False)} with title {json.dumps(title, ensure_ascii=False)}"
    try:
        subprocess.run(["osascript", "-e", script], timeout=5, capture_output=True)
    except (OSError, subprocess.TimeoutExpired):
        pass
