"""Pick the input backend for this OS. macOS first; Windows (PostMessage to
the HWND) and Linux (XTest on a second MPX pointer) are the planned isolated
backends and plug in here with the same InputBackend contract."""
import sys

from .base import InputBackend, RecordingInput

MODES = ("isolated", "shared", "dry")


def make_input(mode="isolated", app=None, skip_pids=(), stop=None):
    if mode not in MODES:
        raise ValueError(f"input mode must be one of {MODES}, not {mode!r}")
    if mode == "dry":
        return RecordingInput()
    if sys.platform == "darwin":
        from .macos import QuartzInput
        return QuartzInput(mode, app, skip_pids, stop)
    raise NotImplementedError(f"no input backend for {sys.platform} yet (macOS only for now)")


def open_app(name):
    if sys.platform == "darwin":
        from .macos import open_app as mac_open
        return mac_open(name)
    raise NotImplementedError(f"open_app is not implemented for {sys.platform} yet")


__all__ = ["make_input", "open_app", "InputBackend", "RecordingInput", "MODES"]
