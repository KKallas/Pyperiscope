"""A workflow is a plain Python file in workflows/ with ordered steps:

    from pyperiscope import Workflow
    wf = Workflow(__file__, app="TextEdit")

    @wf.step
    def open_document(s):
        s.open_app("TextEdit")
        s.left_click("textedit.new_document")

    if __name__ == "__main__":
        wf.main()

Steps are the unit of resume: after a fix, the run restarts at the step that
failed. Make each step start from a screen state it can recognise.
Run it plainly (python workflows/x.py) or under the escalation ladder
(pyperiscope run x), which re-runs it after agent or human fixes.
"""
import argparse
import json
import sys
import traceback
from pathlib import Path

from .errors import PermissionMissing, StoppedByUser
from .project import Project
from .session import Session

EXIT_OK, EXIT_FAILED, EXIT_USAGE, EXIT_STOPPED, EXIT_SETUP = 0, 1, 2, 3, 4


class Workflow:
    def __init__(self, file, app=None, input=None):
        self.file = Path(file).resolve()
        self.name = self.file.stem
        self.project = Project(Project.discover(self.file.parent))
        self.app, self.input = app, input
        self.steps = []

    def step(self, fn):
        self.steps.append(fn)
        return fn

    def step_names(self):
        return [fn.__name__ for fn in self.steps]

    def run(self, from_step=None, run_dir=None, input=None, safety=True, **session_kw):
        names = self.step_names()
        if from_step and from_step not in names:
            print(f"unknown step {from_step!r}; steps: {names}", file=sys.stderr)
            return EXIT_USAGE
        run_dir = Path(run_dir) if run_dir else self.project.runs / Project.new_id(self.name)
        try:
            session = Session(self.project, run_dir, input or self.input, self.app, safety,
                              name=self.name, **session_kw)
        except (PermissionMissing, RuntimeError, NotImplementedError) as error:
            return self._setup_failed(run_dir, error)
        try:
            session.log("workflow_start", workflow=self.name, from_step=from_step)
            for fn in self.steps[names.index(from_step) if from_step else 0:]:
                session.step = fn.__name__
                session.status("running")
                session.log("step_start")
                fn(session)
                session.log("step_done")
            session.step = None
            session.log("workflow_done")
            return EXIT_OK
        except (StoppedByUser, KeyboardInterrupt) as error:
            session.report_failure(StoppedByUser(str(error) or "stopped by user"))
            return EXIT_STOPPED
        except Exception as error:
            report = session.report_failure(error, traceback.format_exc())
            print(f"FAILED in step {report['step']}: [{report['kind']}] {report['message']}", file=sys.stderr)
            print(f"report: {run_dir / 'failure.json'}", file=sys.stderr)
            return EXIT_FAILED
        finally:
            session.close()

    def _setup_failed(self, run_dir, error):
        """The machine is not ready (permissions, app not running): not
        something an agent can fix in the workflow, so say so plainly."""
        run_dir.mkdir(parents=True, exist_ok=True)
        report = {"kind": getattr(error, "kind", "setup"), "error": type(error).__name__,
                  "message": str(error), "step": None, "target": None, "matches": []}
        (run_dir / "failure.json").write_text(json.dumps(report, indent=2) + "\n")
        print(f"SETUP PROBLEM: {error}", file=sys.stderr)
        return EXIT_SETUP

    def main(self, argv=None):
        parser = argparse.ArgumentParser(prog=self.name, description=f"Run workflow {self.name}")
        parser.add_argument("--from-step", help=f"resume at a step: {', '.join(self.step_names())}")
        parser.add_argument("--run-dir", help="where events and failure reports go")
        parser.add_argument("--input", choices=["isolated", "shared", "dry"])
        parser.add_argument("--list-steps", action="store_true")
        args = parser.parse_args(argv)
        if args.list_steps:
            print("\n".join(self.step_names()))
            sys.exit(EXIT_OK)
        sys.exit(self.run(args.from_step, args.run_dir, args.input))
