"""The floating "automation is running" pill (macOS).

Runs as its own process because AppKit needs the main thread. Reads JSON
lines on stdin: {"text": "...", "level": "run" | "warn" | "stop"}; exits on
EOF. The panel ignores the mouse, floats on every Space, and is excluded from
screen capture so it never interferes with matching.

    python -m pyperiscope.safety.overlay
"""
import json
import sys
import threading

import AppKit as A
from PyObjCTools import AppHelper

COLORS = {"run": (0.11, 0.42, 0.93), "warn": (0.93, 0.52, 0.05), "stop": (0.82, 0.14, 0.14)}
WIDTH, HEIGHT, TOP_GAP = 560, 30, 34


def build():
    frame = A.NSScreen.mainScreen().frame()
    rect = A.NSMakeRect((frame.size.width - WIDTH) / 2, frame.size.height - HEIGHT - TOP_GAP, WIDTH, HEIGHT)
    style = A.NSWindowStyleMaskBorderless | A.NSWindowStyleMaskNonactivatingPanel
    panel = A.NSPanel.alloc().initWithContentRect_styleMask_backing_defer_(rect, style, A.NSBackingStoreBuffered, False)
    panel.setLevel_(A.NSStatusWindowLevel)
    panel.setIgnoresMouseEvents_(True)
    panel.setOpaque_(False)
    panel.setHasShadow_(True)
    panel.setBackgroundColor_(A.NSColor.clearColor())
    panel.setSharingType_(A.NSWindowSharingNone)
    panel.setCollectionBehavior_(A.NSWindowCollectionBehaviorCanJoinAllSpaces
                                 | A.NSWindowCollectionBehaviorStationary
                                 | A.NSWindowCollectionBehaviorFullScreenAuxiliary)
    view = panel.contentView()
    view.setWantsLayer_(True)
    view.layer().setCornerRadius_(HEIGHT / 2)
    label = A.NSTextField.labelWithString_("")
    label.setFrame_(A.NSMakeRect(14, 6, WIDTH - 28, HEIGHT - 12))
    label.setAlignment_(A.NSTextAlignmentCenter)
    label.setTextColor_(A.NSColor.whiteColor())
    label.setFont_(A.NSFont.boldSystemFontOfSize_(12))
    label.setLineBreakMode_(A.NSLineBreakByTruncatingMiddle)
    view.addSubview_(label)
    return panel, label


def show(panel, label, message):
    r, g, b = COLORS.get(message.get("level", "run"), COLORS["run"])
    panel.contentView().layer().setBackgroundColor_(A.NSColor.colorWithSRGBRed_green_blue_alpha_(r, g, b, 0.92).CGColor())
    label.setStringValue_(message.get("text", ""))
    panel.orderFrontRegardless()


def read_stdin(panel, label, app):
    for line in sys.stdin:
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            continue
        AppHelper.callAfter(show, panel, label, message)
    AppHelper.callAfter(app.terminate_, None)


def main():
    app = A.NSApplication.sharedApplication()
    app.setActivationPolicy_(A.NSApplicationActivationPolicyAccessory)
    panel, label = build()
    show(panel, label, {"text": "Pyperiscope starting…", "level": "run"})
    threading.Thread(target=read_stdin, args=(panel, label, app), daemon=True).start()
    AppHelper.runEventLoop()


if __name__ == "__main__":
    main()
