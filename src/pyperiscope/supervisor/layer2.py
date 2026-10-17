"""Supervisor, layer 2: hand a failure to a coding agent (Claude Code or
Codex) running headless in the project folder. The agent edits the workflow
and/or fixes targets through the validating `pyperiscope target` commands,
writes what it did to fix-N.md, and exits. It never drives the screen itself;
the supervisor re-runs the workflow afterwards to prove the fix."""
import subprocess

from .layer1 import Supervisor as Base
from .layer1 import tool_env

QRH = {"ambiguous": "Q1 TARGET AMBIGUOUS", "not_found": "Q2 TARGET NOT FOUND", "exception": "Q6 WORKFLOW ERROR",
       "error": "Q6 WORKFLOW ERROR", "validation_failed": "Q6 WORKFLOW ERROR"}
TOOLS = "Bash(pyperiscope target:*),Bash(pyperiscope zoom:*),Bash(pyperiscope screenshot:*),Read,Edit,Write,Glob,Grep"

PROMPT = """You are the agent on a Pyperiscope bot. The workflow `{workflow}` failed in step `{step}`.

Run QRH checklist {checklist} from manual/4-qrh.md, within manual/1-limitations.md.
The memory items apply: no input to the application, do not run the workflow, read the report first.

Failure bundle ({attempt}/):
- failure.json: kind, step, target, message, matches, best, traceback
- failure-annotated.png: the screen at failure, candidates numbered [0], [1], ...
- failure.png: the raw screenshot, used as --shot. You see it downscaled; read exact
  coordinates with `pyperiscope zoom {attempt}/failure.png --box x,y,w,h`.
Also see workflows/{workflow}.py, targets/<name>/, AGENTS.md (API and CLI), and earlier
repair notes in runs/*/fix-*.md.

Change targets only with `pyperiscope target ...` (validated). When the checklist says hand
over, change nothing more. Either way, end by writing your repair note to {notes}: what you
found, what you changed, and how sure you are. The supervisor re-runs from step `{step}`.
"""


class Supervisor(Base):
    def fix_with_agent(self, attempt, n):
        """Run one agent fix for `attempt`; returns the agent's exit code."""
        notes = f"{self.project.relative(self.dir)}/fix-{n}.md"
        checklist = QRH.get(attempt["kind"], "matching the failure kind")
        prompt = PROMPT.format(workflow=self.state["workflow"], attempt=attempt["dir"], checklist=checklist,
                               step=attempt["step"] or "the start", notes=notes)
        images = [f"{attempt['dir']}/failure-annotated.png"]
        cmd = self.agent_command(prompt, images)
        self.save(status="fixing", fixer=self.agent)
        log_path = self.dir / f"fix-{n}.log"
        with open(log_path, "w") as log:
            log.write("$ " + " ".join(cmd[:3]) + " ...\n\n" + prompt + "\n---\n")
            log.flush()
            try:
                return subprocess.run(cmd, cwd=self.project.root, env=tool_env(), stdout=log,
                                      stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                                      timeout=self.project.config["agent_timeout"]).returncode
            except subprocess.TimeoutExpired:
                log.write("\n[pyperiscope] agent timed out\n")
                return -1
            except FileNotFoundError:
                log.write(f"\n[pyperiscope] `{cmd[0]}` is not installed or not on PATH\n")
                return -2

    def agent_command(self, prompt, images):
        if self.agent == "claude":
            cmd = ["claude", "-p", prompt, "--permission-mode", "acceptEdits",
                   "--allowedTools", TOOLS]
            return cmd + (["--model", self.model] if self.model else [])
        if self.agent == "codex":
            cmd = ["codex", "exec", "--full-auto"]
            for image in images:
                cmd += ["--image", image]
            return cmd + (["--model", self.model] if self.model and "claude" not in self.model else []) + [prompt]
        raise ValueError(f"unknown agent {self.agent!r}; use claude, codex or none")
