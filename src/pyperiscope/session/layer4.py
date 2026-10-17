"""Session, layer 4: the paper trail.

events.jsonl records every action. On failure, failure.json + screenshots are
written so an agent (or human) can repair the workflow without re-running it:

  failure.json            kind, message, target, step, matches, best, traceback
  failure.png (+.json)    the exact screenshot the decision was made on
  failure-annotated.png   candidates numbered [0], [1]... (= --candidate N)
"""
import json
import time

import cv2

from ..annotate import draw_matches
from .layer3 import Session as Base


class Session(Base):
    def log(self, event, **data):
        if not self.run_dir:
            return
        self.run_dir.mkdir(parents=True, exist_ok=True)
        record = {"t": round(time.time(), 3), "step": self.step, "event": event, **data}
        with open(self.run_dir / "events.jsonl", "a") as out:
            out.write(json.dumps(record, default=str) + "\n")

    def report_failure(self, error, traceback_text=""):
        """Write the failure bundle; returns the report dict."""
        report = {
            "kind": getattr(error, "kind", "exception"),
            "error": type(error).__name__,
            "message": str(error),
            "step": self.step,
            "target": getattr(error, "target", None),
            "matches": [m.to_dict() for m in getattr(error, "matches", [])],
            "best": getattr(error, "best", None),
            "traceback": traceback_text,
        }
        if not self.run_dir:
            return report
        shot = getattr(error, "shot", None) or self.last_shot
        if shot is None and report["kind"] != "stopped":
            try:
                shot = self.capture_fn()
            except Exception:
                shot = None
        if shot is not None:
            shot.save(self.run_dir / "failure.png")
            try:
                size = self.target(report["target"]).size if report["target"] else None
            except FileNotFoundError:
                size = None
            annotated = draw_matches(shot.image, getattr(error, "matches", []), report["best"], size)
            cv2.imwrite(str(self.run_dir / "failure-annotated.png"), annotated)
            report.update(screenshot="failure.png", annotated="failure-annotated.png",
                          screen={"size": list(shot.size), "scale": shot.scale, "origin": list(shot.origin)})
        self.run_dir.mkdir(parents=True, exist_ok=True)
        (self.run_dir / "failure.json").write_text(json.dumps(report, indent=2, default=str) + "\n")
        self.log("failure", kind=report["kind"], message=report["message"])
        return report

    def close(self):
        if self.killswitch:
            self.killswitch.close()
        if getattr(self, "input", None):
            self.input.close()
        self.indicator.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
