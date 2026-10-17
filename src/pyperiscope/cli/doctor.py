"""Readiness checks: macOS privacy permissions and agent CLIs.

Permissions belong to the app that launches Python (Terminal, iTerm, VS Code,
Claude desktop...). Grant them in System Settings -> Privacy & Security and
restart that app.
"""
import shutil
import sys


def checks():
    out = []
    if sys.platform != "darwin":
        return [("macOS", False, "only macOS is supported in this version")]
    import HIServices
    import Quartz as Q
    out.append(("Screen Recording (see the screen)", bool(Q.CGPreflightScreenCaptureAccess()),
                "System Settings → Privacy & Security → Screen Recording: enable your terminal/editor"))
    out.append(("Accessibility (send clicks and keys)", bool(Q.CGPreflightPostEventAccess() or HIServices.AXIsProcessTrusted()),
                "System Settings → Privacy & Security → Accessibility: enable your terminal/editor"))
    out.append(("Input Monitoring (Esc kill switch)", bool(Q.CGPreflightListenEventAccess()),
                "System Settings → Privacy & Security → Input Monitoring: enable your terminal/editor"))
    if not out[0][1]:
        Q.CGRequestScreenCaptureAccess()
    if not out[2][1]:
        Q.CGRequestListenEventAccess()
    for agent in ("claude", "codex"):
        out.append((f"optional: {agent} CLI on PATH", bool(shutil.which(agent)),
                    f"install {agent} to use it as the fixing agent (agent setting in pyperiscope.json)"))
    return out
