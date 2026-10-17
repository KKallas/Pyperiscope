"""Finding and launching macOS apps by name or bundle id."""
import subprocess

import AppKit


def running_app(name):
    """NSRunningApplication by localized name or bundle id, or None."""
    for app in AppKit.NSWorkspace.sharedWorkspace().runningApplications():
        if name in (app.localizedName(), app.bundleIdentifier()):
            return app
    return None


def open_app(name):
    """Launch (or bring forward) an app by name or bundle id."""
    flag = "-b" if "." in name and " " not in name else "-a"
    subprocess.run(["open", flag, name], check=True)
