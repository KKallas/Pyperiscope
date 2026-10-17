"""Session, layer 2: seeing. find() is strict: exactly one match or an error
that explains what was seen, because a workflow that clicks "one of several"
is a silent bug."""
import time

from ..errors import AmbiguousTarget, TargetNotFound
from ..target import Target
from .layer1 import Session as Base

POLL_SECONDS = 0.25


class Session(Base):
    def target(self, name):
        if name not in self._targets:
            self._targets[name] = Target.load(self.project.targets, name)
        return self._targets[name]

    def screenshot(self):
        self.guard()
        self.last_shot = self.capture_fn()
        return self.last_shot

    def find_all(self, name):
        """Every match of `name` on a fresh screenshot (may be 0 or many)."""
        return self.target(name).find(self.screenshot())

    def find(self, name, timeout=None):
        """Wait up to `timeout` s until `name` matches exactly once; return it."""
        deadline = time.monotonic() + (self.cfg["timeout"] if timeout is None else timeout)
        while True:
            matches = self.find_all(name)
            if len(matches) == 1:
                return matches[0]
            if time.monotonic() >= deadline:
                break
            self.wait(POLL_SECONDS)
        if matches:
            raise AmbiguousTarget(f"{name}: {len(matches)} matches, expected 1 — add a detail to tell them apart",
                                  target=name, matches=matches, shot=self.last_shot)
        best = self.target(name).best(self.last_shot)
        raise TargetNotFound(f"{name}: not on screen (best score {best and best['score']}, "
                             f"needs {self.target(name).confidence})",
                             target=name, shot=self.last_shot, best=best)

    wait_for = find

    def exists(self, name, timeout=0):
        """True if `name` appears at least once within `timeout` s."""
        deadline = time.monotonic() + timeout
        while not self.find_all(name):
            if time.monotonic() >= deadline:
                return False
            self.wait(POLL_SECONDS)
        return True

    def wait_gone(self, name, timeout=None):
        deadline = time.monotonic() + (self.cfg["timeout"] if timeout is None else timeout)
        while self.find_all(name):
            if time.monotonic() >= deadline:
                raise TargetNotFound(f"{name}: still on screen after {timeout}s", target=name, shot=self.last_shot)
            self.wait(POLL_SECONDS)
