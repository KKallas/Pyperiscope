"""A project is one folder holding everything for a set of automations:

    pyperiscope.json   settings (marks the project root)
    targets/<name>/    target.json + main.png + detail1..4.png
    workflows/*.py     workflow scripts (written by you or an agent)
    screens/           screenshots captured for setup
    runs/<id>/         run.json, attempt-N/ (events.jsonl, failure.json, pngs)
"""
import json
import secrets
import time
from pathlib import Path

MARKER = "pyperiscope.json"

DEFAULTS = {
    "input": "isolated",       # isolated | shared | dry
    "app": None,               # default app (name or bundle id) for isolated input
    "monitor": 1,              # mss monitor index; 1 = main display
    "confidence": 0.9,         # default match threshold for new targets
    "detail_tolerance": 6,     # px a detail may drift from its recorded offset
    "timeout": 5.0,            # default seconds find() waits for a target
    "action_delay": 0.15,      # seconds to settle after each input action
    "kill_hold_seconds": 3.0,  # hold Esc this long to stop
    "overlay": True,           # show the floating "running" indicator
    "agent": "claude",         # claude | codex | none
    "agent_model": "claude-opus-5-5",
    "agent_attempts": 2,       # agent fix attempts before calling a human
    "agent_timeout": 900,      # seconds per agent fix attempt
}


class Project:
    def __init__(self, root=None):
        self.root = Path(root).resolve() if root else self.discover()
        if not (self.root / MARKER).exists():
            raise FileNotFoundError(f"{self.root} is not a project (no {MARKER}); run `pyperiscope init`")
        self.config = {**DEFAULTS, **json.loads((self.root / MARKER).read_text() or "{}")}

    @staticmethod
    def discover(start=None):
        here = Path(start or Path.cwd()).resolve()
        for folder in [here, *here.parents]:
            if (folder / MARKER).exists():
                return folder
        raise FileNotFoundError(f"No {MARKER} in {here} or its parents; run `pyperiscope init`")

    @staticmethod
    def create(root, **settings):
        root = Path(root).resolve()
        root.mkdir(parents=True, exist_ok=True)
        if not (root / MARKER).exists():
            (root / MARKER).write_text(json.dumps(settings, indent=2) + "\n")
        return Project(root)

    def _dir(self, name):
        path = self.root / name
        path.mkdir(exist_ok=True)
        return path

    @property
    def targets(self):
        return self._dir("targets")

    @property
    def workflows(self):
        return self._dir("workflows")

    @property
    def screens(self):
        return self._dir("screens")

    @property
    def runs(self):
        return self._dir("runs")

    def target_names(self):
        return sorted(p.parent.name for p in self.targets.glob("*/target.json"))

    def workflow_names(self):
        return sorted(p.stem for p in self.workflows.glob("*.py") if not p.name.startswith("_"))

    def resolve(self, relative):
        """Path inside the project; refuses anything that escapes the root."""
        path = (self.root / relative).resolve()
        if self.root not in path.parents and path != self.root:
            raise PermissionError(f"{relative} is outside the project")
        return path

    def relative(self, path):
        return Path(path).resolve().relative_to(self.root).as_posix()

    @staticmethod
    def new_id(prefix=""):
        stamp = time.strftime("%Y%m%d-%H%M%S")
        return f"{prefix}{'-' if prefix else ''}{stamp}-{secrets.token_hex(2)}"
