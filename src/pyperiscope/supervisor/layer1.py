"""Supervisor, layer 1: one supervised run = runs/<id>/run.json plus one
attempt-N/ folder per execution of the workflow (each in its own process, so
a crash or a stop never takes the supervisor down)."""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from ..project import Project
from ..workflow import EXIT_FAILED, EXIT_OK, EXIT_SETUP, EXIT_STOPPED, EXIT_USAGE

EXIT_NAMES = {EXIT_OK: "ok", EXIT_FAILED: "failed", EXIT_USAGE: "usage", EXIT_STOPPED: "stopped", EXIT_SETUP: "setup"}


def tool_env():
    """Environment for children: make sure our `pyperiscope` CLI is on PATH."""
    env = dict(os.environ)
    env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env.get("PATH", "")
    return env


class Supervisor:
    def __init__(self, project, workflow, run_id=None, agent=None, model=None, agent_attempts=None, human=True):
        self.project = project if isinstance(project, Project) else Project(project)
        cfg = self.project.config
        self.workflow = self.project.workflows / f"{workflow}.py"
        if not self.workflow.exists():
            raise FileNotFoundError(f"no workflow {self.workflow}")
        self.agent = agent or cfg["agent"]
        self.model = model or cfg["agent_model"]
        self.agent_attempts = cfg["agent_attempts"] if agent_attempts is None else agent_attempts
        self.human = human
        self.id = run_id or Project.new_id(workflow)
        self.dir = self.project.runs / self.id
        self.dir.mkdir(parents=True, exist_ok=True)
        self.state = {"id": self.id, "workflow": workflow, "status": "starting", "agent": self.agent,
                      "model": self.model, "created": time.time(), "attempts": []}
        self.save()

    def save(self, **changes):
        self.state.update(changes, updated=time.time())
        tmp = self.dir / "run.json.tmp"
        tmp.write_text(json.dumps(self.state, indent=2, default=str) + "\n")
        tmp.replace(self.dir / "run.json")

    def launch(self, from_step=None, input=None):
        """Run the workflow once; returns the attempt record."""
        n = len(self.state["attempts"]) + 1
        attempt_dir = self.dir / f"attempt-{n}"
        cmd = [sys.executable, str(self.workflow), "--run-dir", str(attempt_dir)]
        if from_step:
            cmd += ["--from-step", from_step]
        if input:
            cmd += ["--input", input]
        self.save(status="running", step=from_step)
        code = subprocess.run(cmd, cwd=self.project.root, env=tool_env()).returncode
        failure_path = attempt_dir / "failure.json"
        failure = json.loads(failure_path.read_text()) if failure_path.exists() else {}
        record = {"n": n, "dir": self.project.relative(attempt_dir), "from_step": from_step,
                  "exit": code, "result": EXIT_NAMES.get(code, "crashed"),
                  "kind": failure.get("kind"), "step": failure.get("step"),
                  "message": failure.get("message"), "fixed_by": None}
        self.state["attempts"].append(record)
        self.save()
        return record
